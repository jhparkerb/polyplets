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

#include <cstring>
#include <mutex>
#include <thread>
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

// Multithreaded version of one height. Same algorithm, but each column's output
// map is split into S shards (by signature hash) each under its own mutex, and
// the source states are fanned across `nthreads` workers. Routing is by the same
// hashSig, and per-shard counts only ever ACCUMULATE (commutative), so the
// result is bit-identical to sweepSquare8Height regardless of interleaving -- the
// gate checks exactly that. Memory ~ serial (the shards together hold the same
// states); no variable-width tricks, since the target machine has the RAM.
inline Counts sweepSquare8HeightMT(int H, int maxn, int nthreads,
                                   SweepResults& res) {
  Counts row(maxn + 1, 0);
  int S = 64;
  while (S < 128 * nthreads) S <<= 1;  // shards: power of two, >> nthreads
  std::vector<FlatDB> dbS, nextS;
  dbS.reserve(S);
  nextS.reserve(S);
  for (int s = 0; s < S; ++s) { dbS.emplace_back(maxn); nextS.emplace_back(maxn); }
  std::vector<std::mutex> mu(S);

  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  dbS[FlatDB::hashSig(seed) & (S - 1)].slot(seed)[0] = 1;

  for (int col = 0; col <= maxn; ++col) {
    u64 total = 0;
    for (int s = 0; s < S; ++s) total += dbS[s].size();
    if (total == 0) break;
    if (total > res.peakStates) { res.peakStates = total; res.peakHeight = H; }
    for (int s = 0; s < S; ++s) nextS[s].clear();

    std::vector<Counts> localRow(nthreads, Counts(maxn + 1, 0));
    auto worker = [&](int t) {
      Counts& lrow = localRow[t];
      for (int s = t; s < S; s += nthreads)  // thread t owns source shards t,t+T,
        dbS[s].for_each([&](const Sig& sig, const u64* counts) {
          const int ms = minSizeRow(counts, maxn);
          if (ms < 0) return;
          int comps = 0;
          for (int j = 0; j < H; ++j)
            if (sig.b[j] > comps) comps = sig.b[j];
          if (comps == 1 && sig.b[H] && sig.b[H + 1])
            for (int n = 1; n <= maxn; ++n) lrow[n] += counts[n];
          forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
            Sig out;
            if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
            const int cells = __builtin_popcount(mask);
            if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
            const int sh = FlatDB::hashSig(out) & (S - 1);
            std::lock_guard<std::mutex> lk(mu[sh]);
            addCounts(nextS[sh], out, counts, cells, maxn);
          });
        });
    };
    std::vector<std::thread> th;
    for (int t = 0; t < nthreads; ++t) th.emplace_back(worker, t);
    for (auto& x : th) x.join();
    for (int t = 0; t < nthreads; ++t)
      for (int n = 1; n <= maxn; ++n) row[n] += localRow[t][n];
    std::swap(dbS, nextS);
  }
  return row;
}

// One height, serial or multithreaded by `nthreads`.
inline Counts heightRow(int H, int maxn, int nthreads, SweepResults& res) {
  return nthreads > 1 ? sweepSquare8HeightMT(H, maxn, nthreads, res)
                      : sweepSquare8Height(H, maxn, res);
}

inline SweepResults sweepSquare8(int maxn, int nthreads = 1) {
  SweepResults res;
  res.byHeight.assign(maxn + 1, Counts(maxn + 1, 0));
  res.totals.assign(maxn + 1, 0);

  for (int H = 1; H <= maxn; ++H)
    res.byHeight[H] = heightRow(H, maxn, nthreads, res);

  accumulateTotals(res, maxn);
  return res;
}
