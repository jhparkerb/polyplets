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

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>

#include "checkpoint.h"
#include "statedb.h"
#include "transition_square8.h"

// Count fixed polyplets of height exactly H (sizes 0..maxn), returned as a
// byHeight row. Updates res.peakStates/peakHeight (the memory high-water mark).
inline Counts sweepSquare8Height(int H, int maxn, SweepResults& res,
                                 const std::function<void(int, u64)>& onColumn = {},
                                 size_t reserveStates = 0,
                                 const CkptCtl* ckpt = nullptr, bool fold = false) {
  Counts row(maxn + 1, 0);
  FlatDB db(maxn), next(maxn);
  if (reserveStates) { db.reserve(reserveStates); next.reserve(reserveStates); }
  const CkptMeta meta{maxn, H, 0, 0, 0, 1, 0, static_cast<u64>(maxn + 1)};

  int startCol = 0;
  bool resumed = false;
  if (ckpt) {  // resume mid-height from a column-boundary checkpoint, if present
    std::int32_t cn = 0, ph = 0; u64 pk = 0;
    const CkptStatus st = tmaCkptLoad(
        *ckpt, meta,
        [&](const Sig& sig, const u64* r) {
          std::memcpy(db.slot(sig), r, static_cast<size_t>(maxn + 1) * sizeof(u64));
        },
        row.data(), static_cast<u64>(maxn + 1), cn, pk, ph);
    if (st == CkptStatus::Refuse) {
      std::fprintf(stderr, "checkpoint %s/ckpt refused (param mismatch or corrupt)\n",
                   ckpt->dir.c_str());
      std::exit(2);
    }
    if (st == CkptStatus::Loaded) {
      startCol = cn; res.peakStates = pk; res.peakHeight = ph; resumed = true;
      std::fprintf(stderr, "resumed col=%d states=%zu (height %d)\n", startCol,
                   db.size(), H);
    }
  }
  if (!resumed) {  // fresh start: seed the empty boundary (NEVER on resume)
    Sig seed;
    std::memset(seed.b, 0, SIGMAX);
    db.slot(seed)[0] = 1;
  }

  auto lastSave = std::chrono::steady_clock::now();
  for (int col = startCol; col <= maxn && !db.empty(); ++col) {
    if (db.size() > res.peakStates) {
      res.peakStates = db.size();
      res.peakHeight = H;
    }
    if (onColumn) onColumn(col, db.size());  // liveness/ETA hook (no-op if unset)
    if (ckpt && col > 0 && db.size() >= ckpt->minStates && ckptDue(*ckpt, lastSave))
      if (tmaCkptSave(*ckpt, meta, db.size(),
                      [&](auto&& emit) { db.for_each(emit); }, row.data(),
                      static_cast<u64>(maxn + 1), col, res.peakStates,
                      res.peakHeight))
        ckptTestKill(col);
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
        if (fold) foldSig(out, H);  // R1: store the orbit-canonical sig (vertical mirror)
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
                                   SweepResults& res,
                                   const std::function<void(int, u64)>& onColumn = {},
                                   size_t reserveStates = 0,
                                   const CkptCtl* ckpt = nullptr, bool fold = false) {
  Counts row(maxn + 1, 0);
  int S = 64;
  while (S < 128 * nthreads) S <<= 1;  // shards: power of two, >> nthreads
  std::vector<FlatDB> dbS, nextS;
  dbS.reserve(S);
  nextS.reserve(S);
  for (int s = 0; s < S; ++s) { dbS.emplace_back(maxn); nextS.emplace_back(maxn); }
  if (reserveStates) {                 // pre-size each shard to its share of the peak
    const size_t per = reserveStates / static_cast<size_t>(S) + 1;
    for (int s = 0; s < S; ++s) { dbS[s].reserve(per); nextS[s].reserve(per); }
  }
  std::vector<std::mutex> mu(S);
  const CkptMeta meta{maxn, H, 0, 0, 0, nthreads, 0, static_cast<u64>(maxn + 1)};

  int startCol = 0;
  bool resumed = false;
  if (ckpt) {  // resume: re-route each saved entry to its shard via hashSig
    std::int32_t cn = 0, ph = 0; u64 pk = 0;
    const CkptStatus st = tmaCkptLoad(
        *ckpt, meta,
        [&](const Sig& sig, const u64* r) {
          std::memcpy(dbS[FlatDB::hashSig(sig) & (S - 1)].slot(sig), r,
                      static_cast<size_t>(maxn + 1) * sizeof(u64));
        },
        row.data(), static_cast<u64>(maxn + 1), cn, pk, ph);
    if (st == CkptStatus::Refuse) {
      std::fprintf(stderr, "checkpoint %s/ckpt refused (param mismatch or corrupt)\n",
                   ckpt->dir.c_str());
      std::exit(2);
    }
    if (st == CkptStatus::Loaded) {
      startCol = cn; res.peakStates = pk; res.peakHeight = ph; resumed = true;
      std::fprintf(stderr, "resumed col=%d (height %d, %d threads)\n", startCol, H,
                   nthreads);
    }
  }
  if (!resumed) {
    Sig seed;
    std::memset(seed.b, 0, SIGMAX);
    dbS[FlatDB::hashSig(seed) & (S - 1)].slot(seed)[0] = 1;
  }

  auto lastSave = std::chrono::steady_clock::now();
  for (int col = startCol; col <= maxn; ++col) {
    u64 total = 0;
    for (int s = 0; s < S; ++s) total += dbS[s].size();
    if (total == 0) break;
    if (total > res.peakStates) { res.peakStates = total; res.peakHeight = H; }
    if (onColumn) onColumn(col, total);  // liveness/ETA hook (no-op if unset)
    if (ckpt && col > 0 && total >= ckpt->minStates && ckptDue(*ckpt, lastSave))
      if (tmaCkptSave(*ckpt, meta, total,
                      [&](auto&& emit) {
                        for (int s = 0; s < S; ++s) dbS[s].for_each(emit);
                      },
                      row.data(), static_cast<u64>(maxn + 1), col, res.peakStates,
                      res.peakHeight))
        ckptTestKill(col);
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
            if (fold) foldSig(out, H);  // R1: canonicalize before sharding/storing
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
inline Counts heightRow(int H, int maxn, int nthreads, SweepResults& res,
                        const std::function<void(int, u64)>& onColumn = {},
                        size_t reserveStates = 0, const CkptCtl* ckpt = nullptr,
                        bool fold = false) {
  return nthreads > 1
             ? sweepSquare8HeightMT(H, maxn, nthreads, res, onColumn, reserveStates,
                                    ckpt, fold)
             : sweepSquare8Height(H, maxn, res, onColumn, reserveStates, ckpt, fold);
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
