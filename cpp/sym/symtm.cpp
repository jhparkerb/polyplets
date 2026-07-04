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
// H runs to maxn=34, past the production caps (SIGMAX=32 key bytes, u32
// masks): POLY_SIGMAX=40 below raises the sig, and stepColumnSquare8 is
// instantiated at uint64_t masks.
//
// CLI:  symtm hmirror MAXN   -> "n count" lines (nonzero counts only).
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

int main(int argc, char** argv) {
  if (argc < 3 || argc > 4 || std::string(argv[1]) != "hmirror") {
    std::fprintf(stderr, "usage: %s hmirror MAXN [THREADS]\n", argv[0]);
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > SIGMAX - 2) {
    std::fprintf(stderr, "MAXN out of range (1..%d)\n", SIGMAX - 2);
    return 2;
  }
  int nthreads = argc == 4 ? std::atoi(argv[3]) : 1;
  if (nthreads < 1) nthreads = 1;

  obs::Reporter rep("symtm-hmirror-N" + std::to_string(maxn),
                    static_cast<double>(maxn),
                    "type=hmirror threads=" + std::to_string(nthreads));

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
      const StripStats st = sweepHmirror(H, maxn, local);
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
