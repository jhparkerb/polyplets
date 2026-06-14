// Driver for the column-at-a-time square-8 (polyplet) engine.
//
// Per strip height H: seed the empty boundary, then place columns left to
// right. Each live state branches over the viable column masks (nonzero,
// non-stranding, in budget -- forEachViableMask); mask 0 harvests a completed
// animal, a nonzero mask extends to a new state unless the size-budget prune
// (min cells so far + admissible completion bound > maxn) rules it out.
// Leftmost column anchored at 0 by the seed, exact-height-H via the touch
// flags, so each fixed polyplet is counted once and A(n) = sum_H byHeight[H][n].
//
// Strip heights are INDEPENDENT sub-sums, so sweepSquare8Height runs one height
// in isolation -- the unit the driver checkpoints, resumes, and (later)
// parallelizes over.

#pragma once

#include <utility>
#include <vector>

#include "statedb.h"
#include "transition_square8.h"

// Count fixed polyplets of height exactly H (sizes 0..maxn), returned as a
// byHeight row. Updates res.peakStates/peakHeight (the memory high-water mark).
inline Counts sweepSquare8Height(int H, int maxn, SweepResults& res) {
  Counts row(maxn + 1, 0);
  FlatDB db(maxn), next(maxn);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > res.peakStates) {
      res.peakStates = db.size();
      res.peakHeight = H;
    }
    next.clear();
    db.for_each([&](const Sig& sig, const u64* counts) {
      const int ms = minSizeRow(counts, maxn);
      if (ms < 0) return;
      // The boundary is canonical, so the component count is its max label.
      int comps = 0;
      for (int j = 0; j < H; ++j)
        if (sig.b[j] > comps) comps = sig.b[j];
      // An empty next column closes the animal: valid iff a single component
      // that has touched both top and bottom (height exactly H).
      if (comps == 1 && sig.b[H] && sig.b[H + 1])
        for (int n = 1; n <= maxn; ++n) row[n] += counts[n];
      // every other mask worth trying: nonzero, non-stranding, in budget
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        // size-budget prune: this contributor's smallest resulting animal is
        // (ms + cells); if it plus the admissible completion bound already
        // exceeds maxn, no size it carries can finish in budget -> drop.
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        addCounts(next, out, counts, cells, maxn);
      });
    });
    std::swap(db, next);
  }
  return row;
}

inline SweepResults sweepSquare8(int maxn) {
  SweepResults res;
  res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
  res.totals.assign(maxn + 1, 0);

  for (int H = 1; H <= maxn; ++H)
    res.byHeight[H] = sweepSquare8Height(H, maxn, res);

  accumulateTotals(res, maxn);
  return res;
}
