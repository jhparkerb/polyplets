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

// Multithreaded version of one height -- LOCK-FREE two-pass (ported from the modp path,
// sweepSquare8HeightModPMT; a per-output mutex caps this DP at ~2.3x and REGRESSES past
// ~12 threads -- measured exact-vs-modp, runs/exact_mt_scaling). Each column:
//   PASS 1 (expand): thread t drains source shards t,t+T,... and routes every output to
//     its OWN per-thread dest shards loc[t][sh] -- no other thread touches loc[t], no lock.
//   PASS 2 (merge): thread u owns dest shards u,u+T,...; it clears dbS[s] and folds in
//     loc[0..T-1][s]. Each dbS[s] written by one thread, each loc[t][s] read by one -> no
//     lock. dbS is reused as the merge target (becomes the next column), so no swap.
// Counts only ACCUMULATE (commutative+associative), so the result is bit-identical to the
// serial sweepSquare8Height regardless of sharding/threading -- gate case M checks exactly
// that. Memory ~ (1 + 1/nthreads)x serial (dbS plus the thread-local dest slices).
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
  std::vector<FlatDB> dbS;
  dbS.reserve(S);
  for (int s = 0; s < S; ++s) dbS.emplace_back(maxn);
  std::vector<std::vector<FlatDB>> loc(nthreads);  // loc[t][s]: thread t's private dest shards
  for (int t = 0; t < nthreads; ++t) {
    loc[t].reserve(S);
    for (int s = 0; s < S; ++s) loc[t].emplace_back(maxn);
  }
  if (reserveStates) {                 // pre-size each shard to its share of the peak
    const size_t per = reserveStates / static_cast<size_t>(S) + 1;
    for (int s = 0; s < S; ++s) {
      dbS[s].reserve(per);             // dbS holds the whole column; loc[t][s] only t's slice
      for (int t = 0; t < nthreads; ++t) loc[t][s].reserve(per / nthreads + 1);
    }
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
    // PASS 1 (expand): threads pull source shards from a shared atomic cursor (DYNAMIC, not a
    // static t,t+T,... stride). Per-state work varies wildly on tall strips (a signature may
    // expand over very many or very few viable masks), so a static 1/T slice left light-shard
    // threads idle while stragglers ground on -- measured ~34% of dalby idle at T=40. Dynamic
    // grab keeps every thread fed until the last ~T shards. Each thread routes outputs to its
    // OWN dest shards loc[t][*] (no shared writes -> no lock) and harvests comps==1 to
    // localRow[t]; the result is independent of which thread drew a source shard (PASS 2 sums
    // all loc[t] per dest), so it stays byte-identical. Each thread also clears its own dest
    // shards here (was a serial pre-loop over all nthreads*S shards on one core).
    std::atomic<int> nextSrc{0};
    auto expand = [&](int t) {
      Counts& lrow = localRow[t];
      std::vector<FlatDB>& mine = loc[t];
      for (int s = 0; s < S; ++s) mine[s].clear();
      u64 ld = 0;  // source states processed by this thread (progress, flushed every 256)
      int s;
      while ((s = nextSrc.fetch_add(1, std::memory_order_relaxed)) < S) {
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
        proctitle::shardDone();  // process-title: one source shard of this column expanded
      }
      if (prog) g_done.fetch_add(ld & 255u, std::memory_order_relaxed);  // flush remainder
    };
    std::vector<std::thread> th;
    // per-column heartbeat: a monitor pulses (states/s, %, per-column ETA) every progSecs
    // while this column expands; joined at the barrier so it never overlaps the merge.
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
    for (int t = 0; t < nthreads; ++t) th.emplace_back(expand, t);
    for (auto& x : th) x.join();
    th.clear();
    if (prog) { monRun.store(false); mon.join(); }

    // PASS 2 (merge): threads pull dest shards from a shared atomic cursor (DYNAMIC, same
    // reason as expand). For dest shard s: clear dbS[s] and fold in loc[0..T-1][s]. Each
    // dest shard is handled by exactly one thread, so dbS[s] has one writer and loc[*][s]
    // one reader -> no lock. dbS is reused as the merge target, so it holds the next column
    // after this -- no swap.
    std::atomic<int> nextDst{0};
    auto merge = [&](int) {
      int s;
      while ((s = nextDst.fetch_add(1, std::memory_order_relaxed)) < S) {
        dbS[s].clear();
        for (int t = 0; t < nthreads; ++t)
          loc[t][s].for_each([&](const Sig& sig, const u64* c) {
            addCounts(dbS[s], sig, c, 0, maxn);
          });
      }
    };
    for (int u = 0; u < nthreads; ++u) th.emplace_back(merge, u);
    for (auto& x : th) x.join();

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
