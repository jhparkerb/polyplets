// Symmetric-polyplet transfer-matrix counter (Hall of Mirrors thread).
//
// Counts FIXED polyplets (king-connected animals) invariant under a chosen
// symmetry, far past the explicit orbit-graph Redelmeier (symcount_fast):
// a symmetric animal of size n has only ~n/2 free cells, so the TM frontier
// is a(n/2)-scale — trivially in-RAM at n=34, where explicit enumeration
// (~2.6x/term) would take years.
//
// hmirror mode: the production column sweep with every column mask
// restricted to be VERTICALLY PALINDROMIC within the exact-height-H strip.
// An animal of bbox height H is invariant under the y-mirror about its bbox
// mid-line iff every column is palindromic, so summing exact-height strips
// H=1..maxn counts precisely the hmirror-fixed animals; the two axis
// placements (through a cell row / between rows) arise as odd/even H.
// Everything else — connectivity union-find, stranding, closable harvest,
// completion prune — is the production transition, unchanged. The R1 fold
// is skipped: reflectSig is the identity on every reachable state.
//
// r180 mode: the 180-degree rotation centre of a fixed animal is its bbox
// centre, and the rotation maps column j to column W-1-j row-reversed — so
// the RIGHT half is the rotated image of the left and only the left half is
// swept (budget maxn/2 cells). At every column boundary the state closes by
// self-gluing to its own rotation: even widths glue the boundary column to
// its row-reversal across the seam (glueEven), odd widths insert one
// vertically-palindromic middle column between the halves (glueOdd; W=1 is
// the seed's odd glue). All four rotation-centre classes (cell / edge x2 /
// vertex) arise as the W x H parities. Left states are NOT palindromic and
// need not touch either strip edge (the rotated half can supply top or
// bottom), so the sweep uses the general mask generator with its top-reach
// prune disabled and a glue-aware completion bound (see sweepR180).
//
// H runs to maxn=34, past the production caps (SIGMAX=32 key bytes, u32
// masks): POLY_SIGMAX=40 below raises the sig, and stepColumnSquare8 /
// forEachViableMask are instantiated at uint64_t masks.
//
// CLI:  symtm {hmirror|r180} MAXN [THREADS]   -> "n count" lines.
// Gate: tests/gate_symtm.py (live cross-algorithm diff vs symcount_fast).

#define POLY_SIGMAX 40

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>

#include "core/signature.h"
#include "core/transition.h"
#include "../obs.h"

using u64 = std::uint64_t;

struct SigHash {
  size_t operator()(const Sig& s) const {
    u64 h = 1469598103934665603ull;
    for (int i = 0; i < SIGMAX; ++i) { h ^= s.b[i]; h *= 1099511628211ull; }
    return static_cast<size_t>(h);
  }
};
using DB = std::unordered_map<Sig, std::vector<u64>, SigHash>;

static bool closable(const Sig& s, int H) {
  int c = 0;
  for (int i = 0; i < H; ++i)
    if (s.b[i] > c) c = s.b[i];
  return c == 1 && s.b[H] && s.b[H + 1];
}

// Enumerate the vertically-palindromic column masks of a height-H strip
// worth trying against `old`, mirroring forEachViableMask's generator prunes
// pair-wise (a "pair" i is rows {i, H-1-i}, or the centre row alone when H
// is odd, weight 1). fn(mask, cells) — `cells` is the full popcount (pairs
// weigh 2). Both prunes cut strict subsets of what the post-enumeration
// authorities (stepColumnSquare8's stranding check, completionLowerBound)
// reject, so the kept set is byte-identical; they only stop the generator
// descending doomed subtrees (99.3% of step calls at the tall strips):
//   - coverage: every old component must gain an adjacent new cell or the
//     step is Dead; if the pairs not yet decided can no longer cover the
//     still-uncovered components, no completion of this prefix survives.
//   - reach: a partial animal that has not touched the strip top must still
//     climb to row 0 — and, touch flags being always symmetric here, also
//     to row H-1 — so a mask whose topmost pair is i owes >= 2i future
//     cells. The debt is charged when the first pair is set (its row is
//     fixed from then on); the all-empty prefix is cut once even the
//     cheapest first pair overshoots.
//   - bands: an empty row band the new mask leaves between two of its
//     occupied rows must be crossed by future cells UNLESS some component
//     of the stepped state spans it. Merging can only make spanning easier,
//     so a band is charged only when it provably cannot be spanned: the old
//     column is empty across the band's interior (no old cell to chain
//     through) and no single old label has cells reaching both sides
//     (spanMax). Each such band is a term completionLowerBound will also
//     charge, so generator rejects stay a strict subset of post-step
//     rejects. A gap between top-half pairs j<i mirrors to an equal bottom
//     band (old states are palindromic, labels mirror) — charged 2x at the
//     moment pair i is set; the single central band is charged 1x at the
//     leaf.
struct PalinCtx {
  int H, half, maxBudget;
  bool touched;
  std::uint32_t all;
  std::uint32_t pairSup[SIGMAX], sufSup[SIGMAX + 1];
  u64 rowOcc;
  int spanMax[SIGMAX + 1];  // max maxRow over labels with minRow <= a

  // Band interior rows t+1..b-1 (caller guarantees b-t >= 2): true iff NO
  // completion of the stepped state can span it.
  bool unspannable(int t, int b) const {
    const u64 interior = ((1ull << (b - t - 1)) - 1) << (t + 1);
    if (rowOcc & interior) return false;
    return spanMax[t + 1] < b - 1;
  }
};

template <class F>
static void palinRec(const PalinCtx& cx, int i, int budget, std::uint32_t cov,
                     u64 mask, int cells, int lastSet, F& fn) {
  if ((cov | cx.sufSup[i]) != cx.all) return;
  if (!cx.touched && mask == 0 && cells + 2 * i + 1 > budget) return;
  if (i == cx.half) {
    if (!mask) return;
    int central = 0;
    const int width = cx.H - 2 * lastSet - 2;  // between row lastSet & mirror
    if (width > 0 && cx.unspannable(lastSet, cx.H - 1 - lastSet))
      central = width;
    if (cells + central <= budget) fn(mask, cells);
    return;
  }
  palinRec(cx, i + 1, budget, cov, mask, cells, lastSet, fn);  // pair i empty
  const int lo = i, hi = cx.H - 1 - i;
  const int w = lo == hi ? 1 : 2;
  int debt = (!cx.touched && mask == 0) ? 2 * i : 0;
  if (lastSet >= 0 && i > lastSet + 1 && cx.unspannable(lastSet, i))
    debt += 2 * (i - lastSet - 1);  // top band + its mirrored bottom band
  if (cells + w + debt <= budget)
    palinRec(cx, i + 1, budget - debt, cov | cx.pairSup[i],
             mask | (1ull << lo) | (1ull << hi), cells + w, i, fn);
}

template <class F>
static void forEachPalinMask(const Sig& old, int H, int budget, F&& fn) {
  PalinCtx cx;
  cx.H = H;
  cx.half = (H + 1) / 2;
  cx.maxBudget = budget;
  cx.touched = old.b[H] != 0;
  cx.all = 0;
  cx.rowOcc = 0;
  std::uint32_t rowSup[SIGMAX];
  int minRow[SIGMAX], maxRow[SIGMAX], maxLab = 0;
  for (int L = 0; L < SIGMAX; ++L) { minRow[L] = SIGMAX; maxRow[L] = -1; }
  for (int r = 0; r < H; ++r) {
    const unsigned char L = old.b[r];
    if (!L) continue;
    cx.all |= 1u << L;
    cx.rowOcc |= 1ull << r;
    if (L > maxLab) maxLab = L;
    if (r < minRow[L]) minRow[L] = r;
    if (r > maxRow[L]) maxRow[L] = r;
  }
  for (int a = 0; a <= H; ++a) {
    int m = -1;
    for (int L = 1; L <= maxLab; ++L)
      if (minRow[L] <= a && maxRow[L] > m) m = maxRow[L];
    cx.spanMax[a] = m;
  }
  for (int r = 0; r < H; ++r) {
    std::uint32_t s = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && old.b[rr]) s |= 1u << old.b[rr];
    rowSup[r] = s;
  }
  for (int i = 0; i < cx.half; ++i)
    cx.pairSup[i] = rowSup[i] | rowSup[H - 1 - i];
  cx.sufSup[cx.half] = 0;
  for (int i = cx.half - 1; i >= 0; --i)
    cx.sufSup[i] = cx.sufSup[i + 1] | cx.pairSup[i];
  palinRec(cx, 0, budget, 0u, 0ull, 0, -1, fn);
}

// One exact-height strip: the whole-column serial sweep (the same loop as
// experiments/kink_tm's columnSweep) over palindromic masks, accumulating
// closable-state counts into total[n]. Returns per-strip work counters for
// the heartbeat (stateSum = live states summed over columns; steps/dead =
// stepColumnSquare8 calls and its stranding rejections).
struct StripStats {
  u64 stateSum = 0, steps = 0, dead = 0, kept = 0;
};
static StripStats sweepHmirror(int H, int maxn, std::vector<u64>& total) {
  StripStats st;
  DB db, next;
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db[seed] = std::vector<u64>(maxn + 1, 0);
  db[seed][0] = 1;
  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    st.stateSum += db.size();
    next.clear();
    for (auto& [sig, counts] : db) {
      int ms = -1;
      for (int n = 0; n <= maxn; ++n)
        if (counts[n]) { ms = n; break; }
      if (ms < 0) continue;
      if (closable(sig, H))
        for (int n = 1; n <= maxn; ++n) total[n] += counts[n];
      auto emit = [&](u64 mask, int cells) {
        ++st.steps;
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) {
          ++st.dead;
          return;
        }
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        ++st.kept;
        auto& dst = next[out];
        if (dst.empty()) dst.assign(maxn + 1, 0);
        for (int n = 0; n + cells <= maxn; ++n)
          if (counts[n]) dst[n + cells] += counts[n];
      };
      forEachPalinMask(sig, H, maxn - ms, emit);
    }
    std::swap(db, next);
  }
  return st;
}

// ----------------------------------------------------------------- r180 --

static int maxLabel(const Sig& s, int H) {
  int k = 0;
  for (int i = 0; i < H; ++i)
    if (s.b[i] > k) k = s.b[i];
  return k;
}

// Even-width close W=2c: the right half is the left half rotated, so its
// seam column (col c) is the boundary column (col c-1) row-reversed, and a
// right-half component is the rotated image of a left one — same partition
// on reversed rows, its own label namespace. Union-find over {left labels}
// u {right labels} with the seam king adjacencies; the animal is valid iff
// everything fuses into ONE component and it touches the strip top — which
// by rotation is s.top || s.bot (the right half touches top iff the left
// touched bottom) and equals the bottom-touch condition, so one test covers
// both (exact height H).
static bool glueEven(const Sig& s, int H) {
  if (!(s.b[H] || s.b[H + 1])) return false;
  const int k = maxLabel(s, H);
  if (!k) return false;  // empty boundary (seed): nothing to glue
  int p[2 * SIGMAX];
  for (int i = 0; i < 2 * SIGMAX; ++i) p[i] = i;
  for (int r = 0; r < H; ++r) {
    if (!s.b[r]) continue;
    for (int rr = r - 1; rr <= r + 1; ++rr) {  // right seam rows king-adjacent
      if (rr < 0 || rr >= H) continue;
      const unsigned char R = s.b[H - 1 - rr];  // right col c occupancy at rr
      if (R) s8::unite(p, s.b[r], SIGMAX + R);
    }
  }
  const int root = s8::find(p, 1);
  for (int L = 1; L <= k; ++L)
    if (s8::find(p, L) != root || s8::find(p, SIGMAX + L) != root) return false;
  return true;
}

// Odd-width close W=2c+1: one middle column m (col c) sits between the
// boundary column (col c-1) and the right half's first column (col c+1 =
// boundary row-reversed); the rotation maps the middle column to itself
// rows-reversed, so m is vertically palindromic. Columns c-1 and c+1 are
// NOT adjacent — all connectivity flows through m. Union-find over {middle
// cells} u {left labels} u {right labels}; valid iff one component. Touch
// (s.top || s.bot || m bit 0, = the bottom condition by palindromy) is the
// generator's job: forEachMiddleMask forces pair 0 when the left half has
// touched neither edge.
static bool glueOdd(const Sig& s, int H, u64 m) {
  const int k = maxLabel(s, H);
  int p[3 * SIGMAX];  // middle row r -> r; left L -> H+L; right L -> H+SIGMAX+L
  for (int i = 0; i < 3 * SIGMAX; ++i) p[i] = i;
  for (int r = 0; r < H; ++r) {
    if (!((m >> r) & 1)) continue;
    if (r + 1 < H && ((m >> (r + 1)) & 1)) s8::unite(p, r, r + 1);
    for (int rr = r - 1; rr <= r + 1; ++rr) {
      if (rr < 0 || rr >= H) continue;
      if (s.b[rr]) s8::unite(p, r, H + s.b[rr]);
      const unsigned char R = s.b[H - 1 - rr];  // right col c+1 occupancy at rr
      if (R) s8::unite(p, r, H + SIGMAX + R);
    }
  }
  int root = -1;
  for (int r = 0; r < H; ++r)
    if ((m >> r) & 1) {
      if (root < 0) root = s8::find(p, r);
      else if (s8::find(p, r) != root) return false;
    }
  for (int L = 1; L <= k; ++L) {
    if (s8::find(p, H + L) != root) return false;
    if (s8::find(p, H + SIGMAX + L) != root) return false;
  }
  return true;
}

// Row-pair coverage, the r180 tall-strip lever. The finished animal needs
// EVERY bbox row nonempty (an empty row disconnects a king animal), and the
// right half covers row r iff the left covers H-1-r — so the left must
// eventually put a cell in every pair {i, H-1-i}. Which pairs past columns
// covered is not in the boundary sig, so each state carries a cov bitmask
// (bit i = pair i covered), merged by OR when states collide. That merge is
// optimistic, and safely so: coverage is PRUNE-ONLY. The glue union-find is
// a faithful adjacency computation on the final cell set, and an uncovered
// row splits it (cells exist on both sides — touch is required), so the
// glue itself rejects every uncovered animal; optimistic cov merely
// under-charges merged states. Bit 0 is the touch condition (pair 0 = rows
// {0, H-1}), so cov stays consistent with the keyed flags.
static u64 pairCov(u64 mask, int H) {
  const int half = (H + 1) / 2;
  u64 c = 0;
  for (int i = 0; i < half; ++i)
    if (((mask >> i) & 1) | ((mask >> (H - 1 - i)) & 1)) c |= 1ull << i;
  return c;
}

// Future n owed by the uncovered pairs: a covering cell is a future left
// cell (weight 2 with its rotated image) or a middle pair (weight 2; the
// centre row, its own mirror, weighs 1), one distinct row each.
static int uncWeight(u64 unc, int H) {
  int w = 2 * __builtin_popcountll(unc);
  if ((H & 1) && ((unc >> ((H - 1) / 2)) & 1)) --w;
  return w;
}

// Middle-column masks worth glueOdd-ing against `s`: vertically palindromic
// (pair i = rows {i, H-1-i}, centre row weight 1), popcount <= budget, plus
// two generator prunes, both strict subsets of what glueOdd itself rejects:
//   - coverage: every left component needs a king-adjacent middle cell (all
//     connectivity flows through the middle); palindromy makes left
//     coverage imply right coverage, so left labels alone are tracked.
//   - forced pairs: the middle is the animal's LAST column decision — every
//     pair the left never covered must be in the mask (row coverage above),
//     including pair 0 when the left touched neither edge (exact height).
struct MidCtx {
  int H, half;
  u64 forced;
  std::uint32_t all;
  std::uint32_t pairSup[SIGMAX], sufSup[SIGMAX + 1];
};

template <class F>
static void midRec(const MidCtx& cx, int i, int budget, std::uint32_t cov,
                   u64 mask, int cells, F& fn) {
  if ((cov | cx.sufSup[i]) != cx.all) return;
  if (i == cx.half) {
    if (mask) fn(mask, cells);
    return;
  }
  if (!((cx.forced >> i) & 1))
    midRec(cx, i + 1, budget, cov, mask, cells, fn);  // pair i empty
  const int lo = i, hi = cx.H - 1 - i;
  const int w = lo == hi ? 1 : 2;
  if (cells + w <= budget)
    midRec(cx, i + 1, budget, cov | cx.pairSup[i],
           mask | (1ull << lo) | (1ull << hi), cells + w, fn);
}

template <class F>
static void forEachMiddleMask(const Sig& s, int H, int budget, u64 forced,
                              F&& fn) {
  MidCtx cx;
  cx.H = H;
  cx.half = (H + 1) / 2;
  cx.forced = forced;
  cx.all = 0;
  for (int r = 0; r < H; ++r)
    if (s.b[r]) cx.all |= 1u << s.b[r];
  std::uint32_t rowSup[SIGMAX];
  for (int r = 0; r < H; ++r) {
    std::uint32_t sup = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && s.b[rr]) sup |= 1u << s.b[rr];
    rowSup[r] = sup;
  }
  for (int i = 0; i < cx.half; ++i)
    cx.pairSup[i] = rowSup[i] | rowSup[H - 1 - i];
  cx.sufSup[cx.half] = 0;
  for (int i = cx.half - 1; i >= 0; --i)
    cx.sufSup[i] = cx.sufSup[i + 1] | cx.pairSup[i];
  midRec(cx, 0, budget, 0u, 0ull, 0, fn);
}

// One exact-height strip of the r180 count: sweep left halves (counts
// indexed by LEFT cells nl, nl <= maxn/2 since n >= 2*nl), harvesting the
// even and odd closes of every state at every column boundary.
//
// Transpose restriction: r180 is central in D4, so transposing is a
// bijection of the r180-fixed set swapping W and H. Each strip harvests
// only W >= H — weight 2 for W > H (the animal and its distinct transpose),
// weight 1 for W == H (square bboxes transpose within the same strip) — so
// tall-NARROW animals are counted as wide-short ones in cheap low-H strips.
// What makes this pay is the column debt it creates: a strip-H state must
// reach floor(H/2) left columns (W=2c>=H or W=2c+1>=H) of >= 1 cell each
// before any glue, which collapses the tall strips (at H=n every column is
// forced to a single cell) — unrestricted, they carried MORE states than
// the mid strips.
//
// Stranding stays authoritative: a component off the boundary can never be
// rescued by the rotated half either (its cells are >= 2 columns away). The
// completion prune replaces completionLowerBound, whose top/bottom-reach
// and band charges are INADMISSIBLE here (the rotated half can supply
// touch, and can span bands through the seam). What survives: if the left
// half has touched NEITHER edge, the finished animal still needs a king
// chain from the boundary to row 0 or row H-1 — every chain cell costs 2
// toward n (a left cell has a distinct rotated image; a middle cell below
// the centre row has a distinct mirror), so the state owes
// 2*min(topGap, botGap) future n on top of its banked 2*(ms+cells).
struct RVal {
  std::vector<u64> c;  // counts by LEFT cells
  u64 cov = 0;         // covered row pairs (optimistic across merges)
};
using RDB = std::unordered_map<Sig, RVal, SigHash>;

// Left-column masks worth stepping in the r180 sweep: forEachViableMask's
// generator (old-component coverage, cell budget) minus its top-reach prune
// (a left half need not touch top — the rotated half can supply it), plus
// the pair-coverage debt IN-RECURSION: at every node, final n >= 2*(ms +
// bits placed) + uncWeight(pairs still uncovered), because each uncovered
// pair costs a distinct future cell — a later bit of THIS mask included
// (it then moves its 2 from the debt into the banked 2*bits). Charging at
// the node instead of post-step is what stops the descent through doomed
// subtrees. fn(mask, cells).
struct R180Gen {
  int H, half, budget, ms2, maxn, colDebt2;
  u64 pairsAll;
  std::uint32_t all;
  std::uint32_t rowSup[SIGMAX], sufSup[SIGMAX + 1];
};

template <class F>
static void r180Rec(const R180Gen& cx, int r, u64 mask, int bits, u64 pcov,
                    std::uint32_t cov, F& fn) {
  if ((cov | cx.sufSup[r]) != cx.all) return;
  const int uw = uncWeight(cx.pairsAll & ~pcov, cx.H);
  if (cx.ms2 + 2 * bits + (uw > cx.colDebt2 ? uw : cx.colDebt2) > cx.maxn)
    return;
  if (r == cx.H) {
    if (mask) fn(mask, bits);
    return;
  }
  r180Rec(cx, r + 1, mask, bits, pcov, cov, fn);  // row r empty
  if (bits + 1 <= cx.budget) {
    const int pr = r < cx.H - 1 - r ? r : cx.H - 1 - r;
    r180Rec(cx, r + 1, mask | (1ull << r), bits + 1, pcov | (1ull << pr),
            cov | cx.rowSup[r], fn);
  }
}

// colDebt2: with the W>=H restriction (see sweepR180), a state that has
// swept `cols` columns after this mask still owes minCols - cols more
// nonempty columns before any glue is allowed — >= 1 future left cell
// (n-weight 2) each. A future cell can fill a column AND cover a pair, so
// the two debts merge by max, not sum.
template <class F>
static void forEachR180Mask(const Sig& s, int H, int budget, int ms2, int maxn,
                            int colDebt, u64 covBase, F&& fn) {
  R180Gen cx;
  cx.H = H;
  cx.half = (H + 1) / 2;
  cx.budget = budget;
  cx.ms2 = ms2;
  cx.maxn = maxn;
  cx.colDebt2 = 2 * (colDebt > 0 ? colDebt : 0);
  cx.pairsAll = (1ull << cx.half) - 1;
  cx.all = 0;
  for (int r = 0; r < H; ++r)
    if (s.b[r]) cx.all |= 1u << s.b[r];
  for (int r = 0; r < H; ++r) {
    std::uint32_t sup = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && s.b[rr]) sup |= 1u << s.b[rr];
    cx.rowSup[r] = sup;
  }
  cx.sufSup[H] = 0;
  for (int r = H - 1; r >= 0; --r) cx.sufSup[r] = cx.sufSup[r + 1] | cx.rowSup[r];
  r180Rec(cx, 0, 0ull, 0, covBase, 0u, fn);
}

static StripStats sweepR180(int H, int maxn, std::vector<u64>& total) {
  StripStats st;
  const int hb = maxn / 2;  // left-cell budget
  const int half = (H + 1) / 2;
  const u64 pairsAll = (1ull << half) - 1;
  RDB db, next;
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db[seed].c.assign(hb + 1, 0);
  db[seed].c[0] = 1;
  for (int col = 0; col <= hb && !db.empty(); ++col) {
    st.stateSum += db.size();
    next.clear();
    for (auto& [sig, val] : db) {
      const std::vector<u64>& counts = val.c;
      int ms = -1;
      for (int n = 0; n <= hb; ++n)
        if (counts[n]) { ms = n; break; }
      if (ms < 0) continue;
      if (2 * col >= H && glueEven(sig, H)) {
        const u64 w = 2 * col > H ? 2 : 1;
        for (int nl = ms; nl <= hb; ++nl)
          if (counts[nl]) total[2 * nl] += w * counts[nl];
      }
      if (2 * col + 1 >= H) {
        const u64 w = 2 * col + 1 > H ? 2 : 1;
        forEachMiddleMask(sig, H, maxn - 2 * ms, pairsAll & ~val.cov,
                          [&](u64 m, int mc) {
                            if (!glueOdd(sig, H, m)) return;
                            for (int nl = ms; nl <= hb && 2 * nl + mc <= maxn;
                                 ++nl)
                              if (counts[nl]) total[2 * nl + mc] += w * counts[nl];
                          });
      }
      auto emit = [&](u64 mask, int cells) {
        ++st.steps;
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) {
          ++st.dead;
          return;
        }
        const u64 cov = val.cov | pairCov(mask, H);
        int owed = uncWeight(pairsAll & ~cov, H);
        if (!out.b[H] && !out.b[H + 1]) {
          int tr = -1, br = -1;
          for (int r = 0; r < H; ++r)
            if (out.b[r]) {
              if (tr < 0) tr = r;
              br = r;
            }
          const int climb2 = 2 * (tr < H - 1 - br ? tr : H - 1 - br);
          if (climb2 > owed) owed = climb2;  // max of admissible bounds
        }
        if (2 * (ms + cells) + owed > maxn) return;
        ++st.kept;
        RVal& dst = next[out];
        if (dst.c.empty()) dst.c.assign(hb + 1, 0);
        dst.cov |= cov;
        for (int n = 0; n + cells <= hb; ++n)
          if (counts[n]) dst.c[n + cells] += counts[n];
      };
      forEachR180Mask(sig, H, hb - ms, 2 * ms, maxn, H / 2 - (col + 1),
                      val.cov, emit);
    }
    std::swap(db, next);
  }
  return st;
}

int main(int argc, char** argv) {
  const std::string type = argc >= 2 ? argv[1] : "";
  if (argc < 3 || argc > 4 || (type != "hmirror" && type != "r180")) {
    std::fprintf(stderr, "usage: %s {hmirror|r180} MAXN [THREADS]\n", argv[0]);
    return 2;
  }
  auto* sweep = type == "hmirror" ? sweepHmirror : sweepR180;
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > SIGMAX - 2) {
    std::fprintf(stderr, "MAXN out of range (1..%d)\n", SIGMAX - 2);
    return 2;
  }
  int nthreads = argc == 4 ? std::atoi(argv[3]) : 1;
  if (nthreads < 1) nthreads = 1;

  obs::Reporter rep("symtm-" + type + "-N" + std::to_string(maxn),
                    static_cast<double>(maxn),
                    "type=" + type + " threads=" + std::to_string(nthreads));

  // Strips are independent; parallelize over H exactly as symcount_fast does
  // over roots: threads pull strip indices off an atomic counter, tallest
  // (most expensive) strips first so the stragglers start earliest, and
  // reduce thread-local totals under a mutex.
  std::vector<u64> total(maxn + 1, 0);
  std::atomic<int> nextIdx{0};
  std::atomic<int> beats{0};
  std::mutex mu;
  auto body = [&]() {
    std::vector<u64> local(maxn + 1, 0);
    int idx;
    while ((idx = nextIdx.fetch_add(1)) < maxn) {
      const int H = maxn - idx;  // descending: big strips first
      const StripStats st = sweep(H, maxn, local);
      std::lock_guard<std::mutex> lk(mu);
      rep.beat(beats.fetch_add(1) + 1,
               "H=" + std::to_string(H) +
                   " states=" + std::to_string(st.stateSum) +
                   " steps=" + std::to_string(st.steps) +
                   " dead=" + std::to_string(st.dead) +
                   " kept=" + std::to_string(st.kept),
               /*force=*/true);  // <=34 lines; per-strip stats are the point
    }
    std::lock_guard<std::mutex> lk(mu);
    for (int n = 0; n <= maxn; ++n) total[n] += local[n];
  };
  std::vector<std::thread> pool;
  pool.reserve(nthreads);
  for (int t = 0; t < nthreads; ++t) pool.emplace_back(body);
  for (auto& th : pool) th.join();

  for (int n = 1; n <= maxn; ++n)
    if (total[n])
      std::printf("%d %llu\n", n, static_cast<unsigned long long>(total[n]));
  rep.done("result=ok");
  return 0;
}
