// T4: the sweep driver.
//
// For each strip height H (1..maxn): start from the empty boundary, sweep
// columns left to right and cells top to bottom within each column, feeding
// every state through the lattice transition twice (cell empty / occupied).
// Animals complete when their last boundary contact disappears (the
// transition reports Complete); requiring the touched-top and touched-bottom
// flags makes the count "height exactly H", and erasing the never-started
// state after column 0 anchors each animal's leftmost column at 0 -- so
// every fixed animal is counted exactly once, and
// A(n) = sum over H of byHeight[H][n].
//
// v0: no pruning (T5), serial (no T6), plain-map statedb. Correct first.

#pragma once

#include <string>
#include <utility>
#include <vector>

#include "statedb.h"
#include "transition_square4.h"

struct SweepResults {
  // byHeight[h][n] = fixed animals with n cells and height exactly h
  std::vector<Counts> byHeight;
  Counts totals;
};

inline SweepResults sweepSquare4(int maxn) {
  SweepResults res;
  res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
  res.totals.assign(maxn + 1, 0);

  for (int H = 1; H <= maxn; ++H) {
    const std::string startSig(H + 2, 0);
    StateDB db;
    db[startSig] = Counts(maxn + 1, 0);
    db[startSig][0] = 1;

    // width <= n <= maxn; one extra column lets the widest animals complete
    for (int col = 0; col <= maxn; ++col) {
      for (int r = 0; r < H; ++r) {
        StateDB next;
        for (const auto& [sig, counts] : db) {
          for (int occ = 0; occ <= 1; ++occ) {
            StepResult sr = stepSquare4(sig, H, r, occ != 0);
            switch (sr.outcome) {
              case Outcome::Dead:
                break;
              case Outcome::Complete:
                // only an unoccupied step completes, so sizes are unshifted
                for (int n = 1; n <= maxn; ++n)
                  res.byHeight[H][n] += counts[n];
                break;
              case Outcome::Alive:
                addCounts(next, sr.sig, counts, occ, maxn);
                break;
            }
          }
        }
        db = std::move(next);
      }
      if (col == 0) db.erase(startSig);  // anchor: column 0 must be used
    }
  }

  for (int h = 1; h <= maxn; ++h)
    for (int n = 1; n <= maxn; ++n) res.totals[n] += res.byHeight[h][n];
  return res;
}
