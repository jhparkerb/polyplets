// T4 driver for the column-at-a-time square-8 engine.
//
// Per strip height H: seed the empty boundary, then place columns left to
// right. At each column step every live state branches over all 2^H column
// occupancy masks: mask 0 harvests (Complete -> count, Dead -> drop), a
// nonzero mask extends to a new state (or dies if it strands an old
// component). Leftmost column anchored at 0 (the seed's only animal-starting
// move) and exact-height-H via the touch flags make each fixed polyplet
// counted once, so A(n) = sum over H of byHeight[H][n].
//
// v0: no pruning, serial, plain-map statedb, brute 2^H mask fan-out. The
// fan-out caps practical reach; this engine's job is to PROVE the king-move
// transfer matrix is correct, not to set records.

#pragma once

#include <string>
#include <utility>
#include <vector>

#include "statedb.h"
#include "transition_square8.h"

inline SweepResults sweepSquare8(int maxn) {
  SweepResults res;
  res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
  res.totals.assign(maxn + 1, 0);

  for (int H = 1; H <= maxn; ++H) {
    const std::string startSig(H + 2, 0);
    StateDB db;
    db[startSig] = Counts(maxn + 1, 0);
    db[startSig][0] = 1;

    for (int col = 0; col <= maxn && !db.empty(); ++col) {
      StateDB next;
      for (const auto& [sig, counts] : db) {
        for (unsigned mask = 0; mask < (1u << H); ++mask) {
          ColResult cr = stepColumnSquare8(sig, H, mask);
          if (cr.outcome == Outcome::Dead) continue;
          if (cr.outcome == Outcome::Complete) {
            // mask == 0 only; harvest without shifting size
            for (int n = 1; n <= maxn; ++n) res.byHeight[H][n] += counts[n];
            continue;
          }
          const int cells = __builtin_popcount(mask);
          addCounts(next, cr.sig, counts, cells, maxn);
        }
      }
      db = std::move(next);
    }
  }

  for (int h = 1; h <= maxn; ++h)
    for (int n = 1; n <= maxn; ++n) res.totals[n] += res.byHeight[h][n];
  return res;
}
