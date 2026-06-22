// R2 assessment probe (refute-or-confirm "ranged counts-row"). At the peak column
// of one height-H sweep it measures how much a per-state row would shrink if we
// stored only its nonzero support [minSize, maxn] instead of the full [0, maxn].
//   rowFactor   = sum(full width) / sum(support width)        -- the row-only win
//   footFactor  = sum(full per-state bytes) / sum(ranged bytes), counting the
//                 fixed 32-byte Sig + a small range header that do NOT shrink.
// footFactor >~1.5 => R2 is a real reach lever; ~1.0 => a dud, document & move on.
// Read-only; reuses the validated transition/prune so the measured states are exact.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>

#include "tma/signature.h"
#include "tma/statedb.h"
#include "tma/transition_square8.h"

int main(int argc, char** argv) {
  if (argc < 3) { std::fprintf(stderr, "usage: %s H N\n", argv[0]); return 2; }
  const int H = std::atoi(argv[1]);
  const int maxn = std::atoi(argv[2]);

  FlatDB db(maxn), next(maxn);
  Sig seed; std::memset(seed.b, 0, SIGMAX); db.slot(seed)[0] = 1;

  size_t peakStates = 0;
  double pkFull = 0, pkSupp = 0, pkMinSizeSum = 0;
  int peakCol = -1;

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > peakStates) {            // snapshot the support stats at the peak
      peakStates = db.size();
      double full = 0, supp = 0, msSum = 0;
      db.for_each([&](const Sig&, const u64* c) {
        int ms = minSizeRow(c, maxn);
        if (ms < 0) ms = maxn;
        full += (maxn + 1);
        supp += (maxn - ms + 1);
        msSum += ms;
      });
      pkFull = full; pkSupp = supp; pkMinSizeSum = msSum; peakCol = col;
    }
    next.clear();
    db.for_each([&](const Sig& sig, const u64* counts) {
      const int ms = minSizeRow(counts, maxn);
      if (ms < 0) return;
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        addCounts(next, out, counts, cells, maxn);
      });
    });
    std::swap(db, next);
  }

  const double rowFactor = pkFull / pkSupp;
  // per-state bytes: full = (maxn+1)*8 + Sig(32) + used(1); ranged = support*8 +
  // range header(8: lo+len) + Sig(32) + used(1).
  const double fullBytes = pkFull * 8 + peakStates * (SIGMAX + 1.0);
  const double suppBytes = pkSupp * 8 + peakStates * (SIGMAX + 1.0 + 8.0);
  std::printf("H=%d N=%d peakCol=%d peakStates=%zu avgMinSize=%.1f/%d\n",
              H, maxn, peakCol, peakStates, pkMinSizeSum / peakStates, maxn);
  std::printf("  rowFactor=%.3f  footprintFactor=%.3f (Sig+hdr fixed)\n",
              rowFactor, fullBytes / suppBytes);
  return 0;
}
