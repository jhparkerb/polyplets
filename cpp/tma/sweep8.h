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

#include <atomic>
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
#include "proctitle.h"
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
  const CkptMeta meta{maxn,    H, 0, 0, 0, 1, 0, static_cast<u64>(maxn + 1),
                      static_cast<std::uint8_t>(fold ? 1 : 0)};

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

// Multithreaded version of one height -- LOCK-FREE, dynamic-dispatch, BATCHED-merge. Threads
// expand into private scratch (no per-insert lock; a mutex capped this DP at ~2.3x and
// regressed past ~12 threads -- runs/exact_mt_scaling), but the scratch is merged into a
// single next-column map every batch so it can't blow up RAM. Each column, for nBatches
// batches of source shards:
//   PASS 1 (expand): each thread dynamically grabs source shards in the batch (atomic cursor,
//     not a static stride -- static left light-shard threads idle, ~34% of dalby at T=40) and
//     routes outputs to its OWN loc[t][sh] -- no shared write, no lock.
//   PASS 2 (merge): each thread dynamically grabs dest shards and folds this batch's
//     loc[*][s] into the single nextDB[s] (accumulate); one writer per nextDB[s], batches
//     sequential -> no lock. nextDB swaps into dbS at column end.
// Why batched: a single end-of-column merge let loc hold the WHOLE next column duplicated
// ~indeg-times (one partial copy per contributing thread) -> ~30x the column -> OOM on the
// heavy a(21) heights. Batching caps loc to ~1/nBatches of that; peak ~ dbS + nextDB +
// loc_batch ~ 2x the column, INDEPENDENT of thread count (TMA_MERGE_BATCHES, default 16).
// Counts only ACCUMULATE (commutative+associative), so the result is bit-identical to the
// serial sweepSquare8Height regardless of sharding/threading/batching -- gate case M checks it.
inline Counts sweepSquare8HeightMT(int H, int maxn, int nthreads,
                                   SweepResults& res,
                                   const std::function<void(int, u64)>& onColumn = {},
                                   size_t reserveStates = 0,
                                   const CkptCtl* ckpt = nullptr, bool fold = false) {
  Counts row(maxn + 1, 0);
  int S = 64;
  int shardMult = 16;  // TMA_SHARD_MULT: dest shards per thread (>= for merge balance)
  if (const char* e = std::getenv("TMA_SHARD_MULT")) shardMult = std::atoi(e);
  while (S < shardMult * nthreads) S <<= 1;  // shards: power of two, >> nthreads
  // dbS = current column (source); nextDB = the single accumulating next column (NO per-thread
  // duplication). loc[t] = thread t's private expand scratch, flushed into nextDB once per
  // BATCH, so it only ever holds ~1/nBatches of the column's duplicated outputs -- this is what
  // bounds RAM (a single end-of-column merge let loc hold ~indeg x the column => OOM on heavy
  // heights). Peak ~ dbS + nextDB + loc_batch ~ 2x the column, independent of thread count.
  int nBatches = 16;  // TMA_MERGE_BATCHES: more batches -> lower peak loc RAM, same total work
  if (const char* e = std::getenv("TMA_MERGE_BATCHES")) { int v = std::atoi(e); if (v > 0) nBatches = v; }
  if (nBatches > S) nBatches = S;
  std::vector<FlatDB> dbS, nextDB;
  dbS.reserve(S); nextDB.reserve(S);
  for (int s = 0; s < S; ++s) { dbS.emplace_back(maxn); nextDB.emplace_back(maxn); }
  std::vector<std::vector<FlatDB>> loc(nthreads);  // loc[t][s]: thread t's private expand scratch
  for (int t = 0; t < nthreads; ++t) {
    loc[t].reserve(S);
    for (int s = 0; s < S; ++s) loc[t].emplace_back(maxn);
  }
  if (reserveStates) {                 // pre-size dbS/nextDB to the peak; loc stays small (batched)
    const size_t per = reserveStates / static_cast<size_t>(S) + 1;
    for (int s = 0; s < S; ++s) { dbS[s].reserve(per); nextDB[s].reserve(per); }
  }
  const CkptMeta meta{maxn,    H, 0, 0, 0, nthreads, 0, static_cast<u64>(maxn + 1),
                      static_cast<std::uint8_t>(fold ? 1 : 0)};

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
  proctitle::setShardTotal(static_cast<u64>(S));  // within-column progress denominator

  // TMA_PROGRESS=1: log per-column expand throughput (states processed/s, % of the column,
  // per-column ETA) to stderr -> h$H.log, for reading the wall of a multi-day run. Interval
  // TMA_PROGRESS_SECS (default 150s); a fresh monitor runs per column, so fast early columns
  // emit nothing and only the heavy columns pulse. Zero cost when unset.
  const char* progEnv = std::getenv("TMA_PROGRESS");
  const bool prog = progEnv && std::atoi(progEnv) > 0;
  int progSecs = 150;
  if (const char* e = std::getenv("TMA_PROGRESS_SECS")) { int v = std::atoi(e); if (v > 0) progSecs = v; }
  std::atomic<u64> g_done{0};

  for (int col = startCol; col <= maxn; ++col) {
    u64 total = 0;
    for (int s = 0; s < S; ++s) total += dbS[s].size();
    if (total == 0) break;
    if (total > res.peakStates) { res.peakStates = total; res.peakHeight = H; }
    if (onColumn) onColumn(col, total);  // liveness/ETA hook (no-op if unset)
    proctitle::setCol(col);              // process-title: column index
    proctitle::resetShards();            // process-title: within-column bar restarts at 0
    if (ckpt && col > 0 && total >= ckpt->minStates && ckptDue(*ckpt, lastSave))
      if (tmaCkptSave(*ckpt, meta, total,
                      [&](auto&& emit) {
                        for (int s = 0; s < S; ++s) dbS[s].for_each(emit);
                      },
                      row.data(), static_cast<u64>(maxn + 1), col, res.peakStates,
                      res.peakHeight))
        ckptTestKill(col);
    std::vector<Counts> localRow(nthreads, Counts(maxn + 1, 0));
    for (int s = 0; s < S; ++s) nextDB[s].clear();  // the single accumulating next column

    // per-column heartbeat: ONE monitor spans the whole column (all batches); g_done
    // accumulates across batches. Pulses states/s + per-column ETA every progSecs.
    std::vector<std::thread> th;
    std::atomic<bool> monRun{true};
    std::thread mon;
    if (prog) {
      g_done.store(0, std::memory_order_relaxed);
      const u64 src = total;
      const int curCol = col, curH = H, ds = progSecs;
      mon = std::thread([&monRun, &g_done, src, curCol, curH, ds]() {
        using namespace std::chrono;
        auto t0 = steady_clock::now();
        while (monRun.load(std::memory_order_relaxed)) {
          for (int i = 0; i < ds * 10 && monRun.load(std::memory_order_relaxed); ++i)
            std::this_thread::sleep_for(milliseconds(100));
          if (!monRun.load(std::memory_order_relaxed)) break;
          const double el = duration_cast<duration<double>>(steady_clock::now() - t0).count();
          const u64 d = g_done.load(std::memory_order_relaxed);
          std::fprintf(stderr,
                       "PROGRESS H=%d col=%d src=%llu done=%llu (%.2f%%) rate=%.0f/s "
                       "elapsed=%.0fs eta_col=%.0fs\n",
                       curH, curCol, (unsigned long long)src, (unsigned long long)d,
                       src ? 100.0 * d / src : 0.0, el > 0 ? d / el : 0.0, el,
                       d > 0 ? (src - d) * el / d : 0.0);
        }
      });
    }

    // Process the column's source shards in nBatches batches. Per batch: each thread expands
    // its dynamically-grabbed share of the batch's source shards into private loc[t] (no
    // shared writes -> no lock; per-state work varies wildly on tall strips, so dynamic grab
    // beats a static stride -- it kept ~34% of dalby idle at T=40), harvesting comps==1 to
    // localRow[t]; then the lock-free merge folds this batch's loc[*][s] into the single
    // nextDB[s] (accumulate) and the next batch reuses loc. So loc only ever holds ~1/nBatches
    // of the column's per-thread-duplicated outputs -- a single end-of-column merge let loc
    // grow to ~indeg x the column and OOM'd the heavy a(21) heights. Output is independent of
    // which thread/batch drew a source shard (every contribution sums into nextDB), so it
    // stays byte-identical to the serial sweep (gate case M).
    std::atomic<int> nextSrc{0}, nextDst{0};
    for (int b = 0; b < nBatches; ++b) {
      const int lo = static_cast<int>(static_cast<long long>(b) * S / nBatches);
      const int hi = static_cast<int>(static_cast<long long>(b + 1) * S / nBatches);
      nextSrc.store(lo, std::memory_order_relaxed);
      auto expand = [&](int t) {
        Counts& lrow = localRow[t];
        std::vector<FlatDB>& mine = loc[t];
        for (int s = 0; s < S; ++s) mine[s].clear();  // fresh scratch each batch
        u64 ld = 0;
        int s;
        while ((s = nextSrc.fetch_add(1, std::memory_order_relaxed)) < hi) {
          dbS[s].for_each([&](const Sig& sig, const u64* counts) {
            if (prog && (++ld & 255u) == 0) g_done.fetch_add(256, std::memory_order_relaxed);
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
              addCounts(mine[FlatDB::hashSig(out) & (S - 1)], out, counts, cells, maxn);
            });
          });
          proctitle::shardDone();  // process-title: one source shard expanded
        }
        if (prog) g_done.fetch_add(ld & 255u, std::memory_order_relaxed);
      };
      for (int t = 0; t < nthreads; ++t) th.emplace_back(expand, t);
      for (auto& x : th) x.join();
      th.clear();

      nextDst.store(0, std::memory_order_relaxed);
      auto merge = [&](int) {  // fold this batch's loc into the accumulating nextDB
        int s;
        while ((s = nextDst.fetch_add(1, std::memory_order_relaxed)) < S) {
          for (int t = 0; t < nthreads; ++t)
            loc[t][s].for_each([&](const Sig& sig, const u64* c) {
              addCounts(nextDB[s], sig, c, 0, maxn);
            });
        }
      };
      for (int u = 0; u < nthreads; ++u) th.emplace_back(merge, u);
      for (auto& x : th) x.join();
      th.clear();
    }
    if (prog) { monRun.store(false); mon.join(); }
    std::swap(dbS, nextDB);  // nextDB now holds this column's output -> becomes the source

    for (int t = 0; t < nthreads; ++t)
      for (int n = 1; n <= maxn; ++n) row[n] += localRow[t][n];
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
