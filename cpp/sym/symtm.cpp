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
// dmirror mode: transpose invariance (the diagonal axis always passes
// through cells, so there is one placement class and the bbox is forced
// square SxS, S up to maxn — the main diagonal is an n-cell dmirror-fixed
// animal). Sweep HOOKS k=0,1,... (cells with min(x,y)=k) inside an outer
// loop over the exact bbox S: the hook frontier is one hook in absolute
// coordinates, and king adjacency only ever reaches the next hook. The row
// arm of a symmetric animal is the mirror of its column arm, so masks
// enumerate (corner, column arm) only — but the STATE stores the hook
// UNFOLDED (corner + column arm + row arm labels). That deviates from
// docs/dmirror-design.md's folded selfPaired-bit state, which is
// under-specified: a component can straddle the diagonal without touching
// it, so its mirror can be a SECOND visible column-arm label — the pairing
// is a general involution on labels, not one bit per label. Unfolding makes
// the union-find run on real adjacencies and the pairing bookkeeping
// disappears; symmetry stays enforced by construction (see sweepDmirror).
//
// H (and the dmirror bbox S) runs to maxn=34, past the production caps
// (SIGMAX=32 key bytes, u32 masks): POLY_SIGMAX=70 below fits the unfolded
// dmirror hook (34 + 33 label bytes + flag), and stepColumnSquare8 /
// forEachViableMask are instantiated at uint64_t masks.
//
// CLI:  symtm {hmirror|r180|dmirror} MAXN [THREADS]   -> "n count" lines.
// Gate: tests/gate_symtm.py (live cross-algorithm diff vs symcount_fast).

#define POLY_SIGMAX 70

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <vector>

#include "core/signature.h"
#include "core/transition.h"
#include "../obs.h"

using u64 = std::uint64_t;
using u32 = std::uint32_t;
using u8 = std::uint8_t;

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
// Mirror-pair label support, shared by the palindromic and middle-mask
// generators: pairSup[i] = old labels king-adjacent to row i or its mirror
// (setting pair i covers exactly these), sufSup[i] = union over pairs >= i
// (what the remaining pairs could still cover).
static void pairSupport(const Sig& s, int H, int half, std::uint32_t* pairSup,
                        std::uint32_t* sufSup) {
  std::uint32_t rowSup[SIGMAX];
  for (int r = 0; r < H; ++r) {
    std::uint32_t sup = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && s.b[rr]) sup |= 1u << s.b[rr];
    rowSup[r] = sup;
  }
  for (int i = 0; i < half; ++i) pairSup[i] = rowSup[i] | rowSup[H - 1 - i];
  sufSup[half] = 0;
  for (int i = half - 1; i >= 0; --i) sufSup[i] = sufSup[i + 1] | pairSup[i];
}

struct PalinCtx {
  int H, half;
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
  cx.touched = old.b[H] != 0;
  cx.all = 0;
  cx.rowOcc = 0;
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
  pairSupport(old, H, cx.half, cx.pairSup, cx.sufSup);
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
  pairSupport(s, H, cx.half, cx.pairSup, cx.sufSup);
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
  std::vector<u64> c;  // counts by LEFT cells (dmirror: by full n)
  u64 cov = 0;         // covered row pairs / rows (optimistic across merges)
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
  int H, budget, ms2, maxn, colDebt2;
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
  cx.budget = budget;
  cx.ms2 = ms2;
  cx.maxn = maxn;
  cx.colDebt2 = 2 * (colDebt > 0 ? colDebt : 0);
  cx.pairsAll = (1ull << ((H + 1) / 2)) - 1;
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

// --------------------------------------------------------------- dmirror --
//
// Hook sweep inside an outer loop over the exact bbox S: hook k = cells
// with min(x,y)=k, swept k=0..S-1; the hook frontier is one hook in
// absolute coordinates and king adjacency only ever reaches the next hook.
// (A merged single-sweep variant without the S loop — implicit bbox,
// harvest on connectivity alone — was built and byte-matched too, but
// MEASURED SLOWER at every point (n=20 serial 12.5s vs 7.1s; n=24 10t
// >120s vs 92s): the exact-S touch debt prunes more than strip-merging
// dedups, and strips parallelize for free. Recover it from git history if
// ever needed.)
//
// Sig layout (POLY_SIGMAX=70): b[0] = corner label (cell (k,k)), b[i] =
// column-arm position i (cell (k,k+i)) for i=1..33, b[DM_ROW+i] = row-arm
// position i (cell (k+i,k)); b[DM_TOUCH] = touched-outer flag (some cell
// reached absolute coordinate S-1; by symmetry row S-1 iff column S-1).
// Masks: bit 0 = corner (weight 1, its own mirror), bit p>=1 = the PAIR
// {(k,k+p),(k+p,k)} (weight 2) — the row arm always carries the mirrored
// column mask, which is what enforces the symmetry. Exactness of the SxS
// bbox: hook 0 nonempty (masks are never empty) gives min row = min col =
// 0; DM_TOUCH gives max = S-1; arms are bounded by S-1-k.
//
// Labels are components of the partial animal (hooks < k) restricted to
// the current hook; every component must keep a hook cell or it is
// stranded (future hooks are >= 2 away from hook k-1 in some coordinate) —
// the standard death. A state is closable iff ONE label overall and
// touched: an uncovered bbox row r would put cells on both sides (row 0
// via hook 0, row S-1 via touch) with no king path across, so it forces
// >= 2 boundary labels (or an earlier stranding) and closability is
// faithful without a coverage authority — row coverage rides as a
// prune-only OR-merged bitmask exactly like r180's cov.
static constexpr int DM_ROW = 34;    // row-arm byte offset (b[35..67])
static constexpr int DM_TOUCH = 68;  // touched-outer flag byte

static bool closableDm(const Sig& s) {
  if (!s.b[DM_TOUCH]) return false;
  int mx = 0;
  for (int i = 0; i < DM_TOUCH; ++i)
    if (s.b[i] > mx) mx = s.b[i];
  return mx == 1;  // canonical labels: max label == component count
}

// Step hook k-1 -> hook k of the exact-SxS sweep. New-cell adjacencies to
// the old hook, in arm coordinates (old position i = (k-1, k-1+i)): a new arm
// cell (k, k+j) sees old positions j..j+2 on ITS OWN arm only; the new
// corner (k,k) is the one +-2 stencil — it sees old col 0..2 AND old row
// 1..2 (five cells). Within the new hook the arms chain vertically and
// {corner, col 1, row 1} are mutually adjacent (col 1 = (k,k+1) and row 1
// = (k+1,k) are diagonal neighbours even without the corner). Union-find
// slots: new corner 0, new col j -> j, new row j -> 40+j, old label L ->
// 80+L (components per hook <= ~35, an independent set of two 33-paths + a
// corner, so labels fit both the slot space and a u64 bitmask).
static Outcome dmStep(const Sig& old, int k, int S, u64 mask, Sig& out) {
  const int Anew = S - 1 - k, Aold = S - k;
  int p[160];
  for (int i = 0; i < 160; ++i) p[i] = i;
  auto oldCol = [&](int i) -> int {
    return (i >= 0 && i <= Aold && i <= 33) ? old.b[i] : 0;
  };
  auto oldRow = [&](int i) -> int {
    return (i >= 1 && i <= Aold && i <= 33) ? old.b[DM_ROW + i] : 0;
  };
  if (mask & 1) {
    for (int i = 0; i <= 2; ++i)
      if (const int L = oldCol(i)) s8::unite(p, 0, 80 + L);
    for (int i = 1; i <= 2; ++i)
      if (const int L = oldRow(i)) s8::unite(p, 0, 80 + L);
  }
  for (int j = 1; j <= Anew; ++j) {
    if (!((mask >> j) & 1)) continue;
    for (int i = j; i <= j + 2; ++i) {
      if (const int L = oldCol(i)) s8::unite(p, j, 80 + L);
      if (const int L = oldRow(i)) s8::unite(p, 40 + j, 80 + L);
    }
    if (j > 1 && ((mask >> (j - 1)) & 1)) {
      s8::unite(p, j, j - 1);
      s8::unite(p, 40 + j, 40 + j - 1);
    }
  }
  if (mask & 2) {
    s8::unite(p, 1, 41);  // col 1 <-> row 1 (diagonal neighbours)
    if (mask & 1) s8::unite(p, 0, 1);
  }
  bool rootNew[160] = {false};
  if (mask & 1) rootNew[s8::find(p, 0)] = true;
  for (int j = 1; j <= Anew; ++j)
    if ((mask >> j) & 1) {
      rootNew[s8::find(p, j)] = true;
      rootNew[s8::find(p, 40 + j)] = true;
    }
  for (int i = 0; i <= Aold; ++i) {
    if (const int L = oldCol(i))
      if (!rootNew[s8::find(p, 80 + L)]) return Outcome::Dead;
    if (const int L = oldRow(i))
      if (!rootNew[s8::find(p, 80 + L)]) return Outcome::Dead;
  }
  std::memset(out.b, 0, SIGMAX);
  unsigned char lab[160] = {0};
  unsigned char nextL = 1;
  auto assign = [&](int node) -> unsigned char {
    const int r = s8::find(p, node);
    if (!lab[r]) lab[r] = nextL++;
    return lab[r];
  };
  if (mask & 1) out.b[0] = assign(0);
  for (int j = 1; j <= Anew; ++j)
    if ((mask >> j) & 1) out.b[j] = assign(j);
  for (int j = 1; j <= Anew; ++j)
    if ((mask >> j) & 1) out.b[DM_ROW + j] = assign(40 + j);
  out.b[DM_TOUCH] = (old.b[DM_TOUCH] || ((mask >> Anew) & 1)) ? 1 : 0;
  return Outcome::Alive;
}

// Hook-k masks worth stepping, with the r180 lesson applied: all prunes IN
// the recursion. Positions are decided DESCENDING (Anew..0) so the touch
// debt is fixed at the first set bit. Debts, each admissible and merged by
// max (one future corner-chain to (S-1,S-1) both touches and covers every
// remaining row at 1 cell per hook, so they share their cheapest witness):
//   - touch: an untouched state whose topmost mask position is t owes
//     >= Anew - t future cells (absolute reach grows by <= 1 per hook, on
//     either the arm (+2/step) or the diagonal (+1/step)); while no bit is
//     set, the optimistic top is the current position p.
//   - rows: bbox row r > k+p can no longer be covered by this mask; each
//     uncovered one needs a distinct future cell (a cell covers exactly one
//     row). Rows <= k+p are coverable by the remaining positions and get
//     charged through the mask weight itself. (Any nonempty mask covers row
//     k: the corner directly, an arm bit via its row-arm mirror (k+p,k).)
//   - old-label coverage: strict subset of dmStep's stranding rejection.
struct DmGen {
  int k, Anew, ms, maxn;
  bool touched;
  u64 covRows;     // rows covered before this hook (prune-only, OR-merged)
  u64 allRows;     // bits 0..S-1
  u64 all;         // old labels
  u64 posSup[35];  // old labels king-adjacent to new position p
  u64 preSup[35];  // union of posSup[0..p] (positions still undecided)
};

template <class F>
static void dmRec(const DmGen& cx, int p, u64 mask, int w, u64 labCov,
                  u64 rows, int topSet, F& fn) {
  if ((labCov | (p >= 0 ? cx.preSup[p] : 0)) != cx.all) return;
  int debt = 0;
  if (!cx.touched && topSet != cx.Anew)
    debt = cx.Anew - (topSet >= 0 ? topSet : (p > 0 ? p : 0));
  const int base = cx.k + (p > 0 ? p : 0);
  const u64 unc =
      cx.allRows & ~(cx.covRows | rows) & ~((1ull << (base + 1)) - 1);
  const int dCov = __builtin_popcountll(unc);
  if (dCov > debt) debt = dCov;
  if (cx.ms + w + debt > cx.maxn) return;
  if (p < 0) {
    if (mask) fn(mask, w);
    return;
  }
  dmRec(cx, p - 1, mask, w, labCov, rows, topSet, fn);  // position p empty
  const int wp = p ? 2 : 1;
  if (cx.ms + w + wp <= cx.maxn)
    dmRec(cx, p - 1, mask | (1ull << p), w + wp, labCov | cx.posSup[p],
          rows | (1ull << cx.k) | (1ull << (cx.k + p)),
          topSet >= 0 ? topSet : p, fn);
}

template <class F>
static void forEachDmMask(const Sig& s, int k, int S, int ms, int maxn,
                          u64 covRows, F&& fn) {
  DmGen cx;
  cx.k = k;
  cx.Anew = S - 1 - k;
  cx.ms = ms;
  cx.maxn = maxn;
  cx.touched = s.b[DM_TOUCH] != 0;
  cx.covRows = covRows;
  cx.allRows = (1ull << S) - 1;
  const int Aold = S - k;
  auto lb = [&](int idx) -> u64 {
    const unsigned char L = s.b[idx];
    return L ? (1ull << L) : 0;
  };
  cx.all = 0;
  for (int i = 0; i <= Aold && i <= 33; ++i) cx.all |= lb(i);
  for (int i = 1; i <= Aold && i <= 33; ++i) cx.all |= lb(DM_ROW + i);
  for (int p = 0; p <= cx.Anew; ++p) {
    u64 sup = 0;
    if (p == 0) {
      for (int i = 0; i <= 2 && i <= Aold && i <= 33; ++i) sup |= lb(i);
      for (int i = 1; i <= 2 && i <= Aold && i <= 33; ++i)
        sup |= lb(DM_ROW + i);
    } else {
      for (int i = p; i <= p + 2 && i <= Aold && i <= 33; ++i)
        sup |= lb(i) | lb(DM_ROW + i);
    }
    cx.posSup[p] = sup;
  }
  cx.preSup[0] = cx.posSup[0];
  for (int p = 1; p <= cx.Anew; ++p)
    cx.preSup[p] = cx.preSup[p - 1] | cx.posSup[p];
  dmRec(cx, cx.Anew, 0ull, 0, 0ull, 0ull, -1, fn);
}

// One exact-SxS bbox of the dmirror count: sweep hooks k=0..S-1 (db at k
// holds animals over hooks < k), harvesting closable states at every k and
// once more after the last hook. Counts are indexed by full n (corner 1,
// arm pairs 2) — no transpose doubling: each dmirror-fixed animal is built
// exactly once.
//
// RAM is the binding resource at the fat strips (the n=32 push), so two
// bookkeeping moves shrink the peak, both byte-neutral:
//   - count vectors are OFFSET by the hook floor: a state in db at loop k
//     has ms >= k (hooks 0..k-1 are each nonempty), so c[i] holds n = k+i
//     and the k dead zero entries are never allocated;
//   - source states are ERASED as consumed: once a thread has fully
//     processed a db entry it deletes it, so freed nodes recycle into the
//     next-frontier and the peak is ~max(|db|,|next|), not their sum.
//
// Unlike hmirror/r180, dmirror is threaded INSIDE the strip: the fattest
// strip is ~16% of the whole sweep's cpu, so with strip-level parallelism
// alone it floors the wall (measured on the ayr n=28 run: total cpu on
// target but the tail all single-threaded). The db is sharded by hash;
// per hook, threads pull source states off an atomic cursor and insert
// stepped states into per-shard maps under per-shard mutexes — the totals
// are u64 sums, so scheduling order cannot change any result byte. The
// shard index uses the hash's HIGH bits: unordered_map's bucket choice
// uses the low bits, and reusing them would leave each shard's map with a
// correlated, mostly-empty bucket array on power-of-two implementations.
// Tiny hooks skip the thread spawn (work < 256 states).
// Compact frontier shard (Shrink Ray). The unordered_map<Sig,RVal>
// frontier OOMed dalby at n=32: hash node + full-width heap count vector
// cost ~300B+/state (S=31 measured 79.1GB peak; S=30 died >124GB). Flat
// storage instead:
//   ent - fixed 88-byte entries: cov(u64) off(u32) lo,len(u8) sig(70B) pad
//   idx - open-addressing table (pow2, load <= 1/2) of entry indices,
//         probed with the LOW hash bits (shard selection uses the high 32)
//   cnt - one arena; an entry's counts live at [off, off+len),
//         absolute n = floor + lo + j
// Ranged blocks bank profile_rows' measured 0.56x mean occupied width. lo
// is exact -- every contributor is nonzero at its own lo, by induction
// from the seed: a contribution whose lo element would land past maxn is
// pruned before insert (ms + w + owed > maxn) -- so ms = floor + lo with
// no scan, and the all-zero-entry case cannot form. len is slack-rounded
// (up to a multiple of 4, capped at the floor width) so cross-source
// merges nearly always extend in place; a genuine widening reallocates at
// the arena tip and orphans the old block until the shard is freed.
// Entries are never deleted individually: a consuming thread owns a whole
// source shard, harvests + expands every entry, then frees the shard --
// the same erase-as-consumed RAM shape at 1/(64T) granularity, except the
// memory actually returns (per-node erase never gave malloc pages back).
struct DmShard {
  static constexpr u32 EMPTY = 0xFFFFFFFFu;
  static constexpr int COV = 0, OFF = 8, LO = 12, LEN = 13, SIGOFF = 14,
                       STRIDE = 88;
  std::vector<u8> ent;
  std::vector<u32> idx;
  std::vector<u64> cnt;
  u32 n = 0;

  u8* e(u32 i) { return ent.data() + static_cast<size_t>(i) * STRIDE; }
  const u8* e(u32 i) const {
    return ent.data() + static_cast<size_t>(i) * STRIDE;
  }

  // Vector doubling would overshoot the peak-hook RSS by up to 2x; grow at
  // ~1.25x instead (allocation count stays logarithmic).
  template <class V>
  static void grow(V& v, size_t need) {
    if (v.capacity() < need) v.reserve(need + need / 4 + 64);
  }

  static u64 rawHash(const u8* b) {
    u64 h = 1469598103934665603ull;
    for (int i = 0; i < SIGMAX; ++i) { h ^= b[i]; h *= 1099511628211ull; }
    return h;
  }

  void rehash(u32 cap) {  // cap = new pow2 table size
    idx.assign(cap, EMPTY);
    for (u32 i = 0; i < n; ++i) {
      u32 s = static_cast<u32>(rawHash(e(i) + SIGOFF)) & (cap - 1);
      while (idx[s] != EMPTY) s = (s + 1) & (cap - 1);
      idx[s] = i;
    }
  }

  // Merge one kept transition: counts c[0..m) land at floor-relative
  // indices dlo..dlo+m-1 (all < wcap, the floor's width cap). Caller holds
  // this shard's mutex.
  void add(const Sig& key, u64 h, u64 cov, const u64* c, int m, int dlo,
           int wcap) {
    if (idx.empty()) rehash(1024);
    else if (2ull * (n + 1) > idx.size()) rehash(2 * static_cast<u32>(idx.size()));
    const u32 mask = static_cast<u32>(idx.size()) - 1;
    u32 s = static_cast<u32>(h) & mask;
    while (idx[s] != EMPTY) {
      u8* p = e(idx[s]);
      if (!std::memcmp(p + SIGOFF, key.b, SIGMAX)) {
        u64 ecov;
        std::memcpy(&ecov, p + COV, 8);
        ecov |= cov;
        std::memcpy(p + COV, &ecov, 8);
        u32 off;
        std::memcpy(&off, p + OFF, 4);
        const int elo = p[LO], elen = p[LEN];
        if (dlo >= elo && dlo + m <= elo + elen) {
          u64* dst = cnt.data() + off + (dlo - elo);
          for (int j = 0; j < m; ++j) dst[j] += c[j];
        } else {  // widen: union range, slack-rounded, at the arena tip
          const int nlo = dlo < elo ? dlo : elo;
          const int hi0 = elo + elen, hi1 = dlo + m;
          int nlen = (hi0 > hi1 ? hi0 : hi1) - nlo;
          nlen = (nlen + 3) & ~3;
          if (nlen > wcap - nlo) nlen = wcap - nlo;
          const size_t noff = cnt.size();
          grow(cnt, noff + nlen);
          cnt.resize(noff + nlen, 0);
          std::memcpy(cnt.data() + noff + (elo - nlo), cnt.data() + off,
                      static_cast<size_t>(elen) * 8);
          u64* dst = cnt.data() + noff + (dlo - nlo);
          for (int j = 0; j < m; ++j) dst[j] += c[j];
          const u32 noff32 = static_cast<u32>(noff);
          std::memcpy(p + OFF, &noff32, 4);
          p[LO] = static_cast<u8>(nlo);
          p[LEN] = static_cast<u8>(nlen);
        }
        return;
      }
      s = (s + 1) & mask;
    }
    int alen = (m + 3) & ~3;  // new entry, slack for future merges
    if (alen > wcap - dlo) alen = wcap - dlo;
    const size_t noff = cnt.size();
    if (noff + alen > 0xFFFFFF00ull) {  // u32 arena offsets: loud, not wrong
      std::fprintf(stderr, "DmShard arena overflow\n");
      std::abort();
    }
    grow(cnt, noff + alen);
    cnt.resize(noff + alen, 0);
    std::memcpy(cnt.data() + noff, c, static_cast<size_t>(m) * 8);
    grow(ent, static_cast<size_t>(n + 1) * STRIDE);
    ent.resize(static_cast<size_t>(n + 1) * STRIDE, 0);
    u8* p = e(n);
    std::memcpy(p + COV, &cov, 8);
    const u32 noff32 = static_cast<u32>(noff);
    std::memcpy(p + OFF, &noff32, 4);
    p[LO] = static_cast<u8>(dlo);
    p[LEN] = static_cast<u8>(alen);
    std::memcpy(p + SIGOFF, key.b, SIGMAX);
    idx[s] = n++;
  }
};

static StripStats sweepDmirror(int S, int maxn, int T, std::vector<u64>& total,
                               std::mutex& totMu) {
  StripStats st;
  // Shards >> threads: every kept transition inserts under a shard mutex,
  // so at shards == T the locks serialize the sweep (measured: n=24 @10t
  // took 5 min vs 92s strip-parallel). At 64x oversharding the collision
  // rate is ~T/(64T); the residual cost is the uncontended lock (~10%).
  const int NSH = 64 * T;
  std::vector<DmShard> db(NSH), next(NSH);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  {
    const u64 one = 1;  // floor 0, lo 0: the empty prefix, n = 0
    db[0].add(seed, SigHash{}(seed), 0, &one, 1, 0, maxn + 1);
  }
  std::vector<std::mutex> mus(NSH);
  std::mutex stripMu;
  std::vector<u64> stripTot(maxn + 1, 0);
  for (int k = 0; k <= S; ++k) {
    // db entries at loop k have count floor k: n = k + lo + j.
    u64 live = 0;
    for (const auto& sh : db) live += sh.n;
    if (!live) break;
    st.stateSum += live;
    std::atomic<int> cursor{0};
    std::atomic<u64> steps{0}, dead{0}, kept{0};
    const int wcap = maxn - k;  // dst floor k+1: index j valid iff j < wcap
    auto body = [&]() {
      std::vector<u64> lt(maxn + 1, 0);
      u64 mySteps = 0, myDead = 0, myKept = 0;
      int si;
      while ((si = cursor.fetch_add(1)) < NSH) {
        DmShard& src = db[si];
        for (u32 ei = 0; ei < src.n; ++ei) {
          const u8* p = src.e(ei);
          Sig sig;
          std::memcpy(sig.b, p + DmShard::SIGOFF, SIGMAX);
          u64 cov0;
          std::memcpy(&cov0, p + DmShard::COV, 8);
          u32 off;
          std::memcpy(&off, p + DmShard::OFF, 4);
          const int slo = p[DmShard::LO], slen = p[DmShard::LEN];
          const u64* counts = src.cnt.data() + off;
          const int ms = k + slo;  // lo is exact: counts[0] != 0
          if (closableDm(sig))
            for (int j = 0; j < slen; ++j)
              if (counts[j] && ms + j >= 1) lt[ms + j] += counts[j];
          if (k == S) continue;
          // Rows < k can no longer gain a cell; an uncovered one
          // disconnects every completion (harvest's single-label check is
          // the authority).
          if (~cov0 & ((1ull << k) - 1)) continue;
          auto emit = [&](u64 mask, int w) {
            ++mySteps;
            Sig out;
            if (dmStep(sig, k, S, mask, out) != Outcome::Alive) {
              ++myDead;
              return;
            }
            u64 cov = cov0 | (1ull << k);
            for (int q = 1; q <= S - 1 - k; ++q)
              if ((mask >> q) & 1) cov |= 1ull << (k + q);
            int owed = 0;  // post-step authority for the generator's debts
            if (!out.b[DM_TOUCH]) {
              int top = 0;
              for (int q = S - 1 - k; q >= 0; --q)
                if ((mask >> q) & 1) { top = q; break; }
              owed = S - 1 - k - top;
            }
            const int unc = __builtin_popcountll(((1ull << S) - 1) & ~cov &
                                                 ~((1ull << (k + 1)) - 1));
            if (unc > owed) owed = unc;
            if (ms + w + owed > maxn) return;
            ++myKept;
            // src n = k+slo+j; dst floor k+1: same n+w at index slo+w-1+j.
            const int dlo = slo + w - 1;
            int m = slen;
            if (m > wcap - dlo) m = wcap - dlo;  // >= 1: ms + w <= maxn
            const u64 h = SigHash{}(out);
            const int sh = static_cast<int>((h >> 32) % NSH);
            std::lock_guard<std::mutex> lk(mus[sh]);
            next[sh].add(out, h, cov, counts, m, dlo, wcap);
          };
          forEachDmMask(sig, k, S, ms, maxn, cov0, emit);
        }
        src = DmShard();  // consumed: free the whole shard now
      }
      steps += mySteps;
      dead += myDead;
      kept += myKept;
      std::lock_guard<std::mutex> lk(stripMu);
      for (int n = 0; n <= maxn; ++n) stripTot[n] += lt[n];
    };
    if (T > 1 && live >= 256) {
      std::vector<std::thread> pool;
      pool.reserve(T);
      for (int t = 0; t < T; ++t) pool.emplace_back(body);
      for (auto& th : pool) th.join();
    } else {
      body();
    }
    st.steps += steps.load();
    st.dead += dead.load();
    st.kept += kept.load();
    db.swap(next);
  }
  std::lock_guard<std::mutex> lk(totMu);
  for (int n = 0; n <= maxn; ++n) total[n] += stripTot[n];
  return st;
}

int main(int argc, char** argv) {
  const std::string type = argc >= 2 ? argv[1] : "";
  const bool isDm = type == "dmirror";
  if (argc < 3 || argc > (isDm ? 6 : 4) ||
      (type != "hmirror" && type != "r180" && !isDm)) {
    std::fprintf(stderr,
                 "usage: %s {hmirror|r180} MAXN [THREADS]\n"
                 "       %s dmirror MAXN [THREADS [SMIN SMAX]]\n",
                 argv[0], argv[0]);
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > 34) {  // dmirror layout caps the bbox at 34
    std::fprintf(stderr, "MAXN out of range (1..34)\n");
    return 2;
  }
  int nthreads = argc >= 4 ? std::atoi(argv[3]) : 1;
  if (nthreads < 1) nthreads = 1;
  // dmirror strip range: farm exact-bbox strips across machines; the
  // partial totals of disjoint ranges sum to the full count.
  int smin = 1, smax = maxn;
  if (isDm && argc == 6) {
    smin = std::atoi(argv[4]);
    smax = std::atoi(argv[5]);
    if (smin < 1 || smax > maxn || smin > smax) {
      std::fprintf(stderr, "bad strip range %d..%d (need 1<=SMIN<=SMAX<=MAXN)\n",
                   smin, smax);
      return 2;
    }
  }

  obs::Reporter rep(
      "symtm-" + type + "-N" + std::to_string(maxn),
      static_cast<double>(isDm ? smax - smin + 1 : maxn),
      "type=" + type + " threads=" + std::to_string(nthreads) +
          (isDm ? " strips=" + std::to_string(smin) + ".." +
                      std::to_string(smax)
                : ""));

  if (isDm) {
    // Strips run SEQUENTIALLY, tallest (most expensive) first, each using
    // every thread internally — the fat strips are what floor the wall.
    std::vector<u64> total(maxn + 1, 0);
    std::mutex totMu;
    int beats = 0;
    for (int S = smax; S >= smin; --S) {
      const StripStats st = sweepDmirror(S, maxn, nthreads, total, totMu);
      rep.beat(++beats,
               "S=" + std::to_string(S) +
                   " states=" + std::to_string(st.stateSum) +
                   " steps=" + std::to_string(st.steps) +
                   " dead=" + std::to_string(st.dead) +
                   " kept=" + std::to_string(st.kept),
               /*force=*/true);
    }
    for (int n = 1; n <= maxn; ++n)
      if (total[n])
        std::printf("%d %llu\n", n, static_cast<unsigned long long>(total[n]));
    rep.done("result=ok");
    return 0;
  }

  // Strips are independent; parallelize over H exactly as symcount_fast does
  // over roots: threads pull strip indices off an atomic counter, tallest
  // (most expensive) strips first so the stragglers start earliest, and
  // reduce thread-local totals under a mutex.
  auto* sweep = type == "hmirror" ? sweepHmirror : sweepR180;
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
