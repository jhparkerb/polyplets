// fused_stage.cpp — Even Keel D6: the fused mid-column stage worker.
//
// Usage:
//   fused_stage --in PATH[,PATH,...] --H N --maxn N --stage R
//               [--counter u64|u128] [--cores N] [--cuts HEX,HEX,...]
//               --out-prefix PREFIX [--ram BYTES] [--rev GITREV]
//
// Replaces one mid-column kink stage round's {mapPhase + mergePhase} pair
// (orchestrator/sweep.go) with a SINGLE multi-threaded in-RAM pass: read the
// whole stage-input frontier once, apply kinkStageTransition per record
// across `--cores` threads, scatter each emitted successor straight into its
// OUTPUT-key range bucket (no intermediate map-output files to write and
// re-read), barrier, then each range's owner sorts+dedups its own bucket and
// writes it. This is docs/even-keel-fusion-plan.md's DDF1-DDF9: the
// algorithm proven in experiments/full_column_bench.cpp's stageMapReduce
// (74.6 effective cores on a real 16M-record H18 stage, byte-identical to
// the sort-merge path), lifted into a real worker reading/writing the
// production POLYRUN format.
//
// --cuts are ACCEPTED from the orchestrator (DDF4): it already computes
// BalancedCutsMulti over the stage input for the merge phase this replaces,
// so the cut logic stays in one place. numRanges = len(cuts)+1. Every
// emitted record's key falls in exactly one range (cuts are on whole keys),
// so each range's owner sees the FULL window of every key before it
// sorts+dedups -- ms-pruning correctness is unaffected by fusion
// (DDF-correctness, see the plan doc).
//
// DDF2: mid-column stage rounds only (this binary always operates on
// keyLen=kinkKeyLen(H) tables in and out). seed/finalize stay on the
// existing map_worker --kernel kink --stage seed|finalize path.
//
// DDF5: in-RAM, no spill. Fails LOUD (nonzero exit, no output written) if
// the projected working set exceeds --ram, rather than silently OOMing.
//
// DDF8: spawn fresh per stage round -- no --persistent mode (unlike
// map_worker/merge_worker); persistent-worker reuse is later work.

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "core/fdlimit.h"
#include "core/kink.h"
#include "core/run.h"
#include "core/runfile.h"
#include "core/signature.h"
#include "worker/worker_io.h"
#include "worker/worker_util.h"

using Clock = std::chrono::steady_clock;
static double secs(Clock::time_point a, Clock::time_point b) {
  return std::chrono::duration<double>(b - a).count();
}

// Parse a comma-separated list of hex cut keys into Sig values, each keyLen
// bytes wide (zero-padded to SIGMAX). Empty string -> no cuts (one range,
// i.e. no partitioning -- the whole stage output in one file).
static std::vector<Sig> parseCuts(const std::string& s, int keyLen) {
  std::vector<Sig> out;
  size_t start = 0;
  while (start < s.size()) {
    size_t pos = s.find(',', start);
    const std::string tok = (pos == std::string::npos) ? s.substr(start)
                                                        : s.substr(start, pos - start);
    if (!tok.empty()) {
      Sig sig;
      std::memset(sig.b, 0, SIGMAX);
      if (!hexToBytes(tok, sig.b, keyLen)) {
        std::fprintf(stderr, "fused_stage: malformed --cuts hex %s\n", tok.c_str());
        std::exit(1);
      }
      out.push_back(sig);
    }
    if (pos == std::string::npos) break;
    start = pos + 1;
  }
  return out;
}

// runFused does the whole fused stage round for one counter width W: read,
// map+scatter (Phase 1), reduce+write (Phase 2), emit accounting. Returns
// the process exit code.
template <class W>
static int runFused(const std::vector<std::string>& inPaths, int H, int maxn, int r,
                    int cores, const std::vector<Sig>& cuts, const std::string& outPrefix,
                    const std::string& rev, size_t ramBudget) {
  const int kLen = kinkKeyLen(H);
  const double t0Wall = wallSeconds();
  const double t0Cpu  = cpuSeconds();

  // Read the WHOLE stage-input frontier, but in PARALLEL by key-range slice
  // (one thread per slice, sliced on the same `cuts` the output uses). A
  // single serial readRangedRunFiles (one k-way heap over all input) was the
  // fused worker's real bottleneck: it collapsed the whole worker to ~5
  // effective cores despite the map+reduce compute being fully parallel
  // (measured H16 2026-07-09). readRangedRunFiles combines same-key records
  // WITHIN each slice; cuts are whole-key boundaries so every key lives in
  // exactly one slice -> concatenating the slices in ascending cut order is
  // byte-identical to one whole-input read+combine, just cores-way parallel.
  Run<W> src;
  {
    // nSlices MUST be cuts.size()+1: BalancedCutsMulti can return FEWER than
    // cores-1 cuts on a small/low-cardinality input, and indexing cuts[t-1]
    // for t beyond that would read out of bounds and produce OVERLAPPING
    // slices -> double-counted records (exact-2x seen in the fused test).
    // At frontier scale cuts.size()==cores-1 so this is still cores-way.
    const size_t nCuts = cuts.size();
    const int nSlices = static_cast<int>(nCuts) + 1;
    std::vector<Run<W>> slices(static_cast<size_t>(nSlices));
    std::vector<std::thread> pool;
    pool.reserve(static_cast<size_t>(nSlices));
    for (int t = 0; t < nSlices; ++t) {
      pool.emplace_back([&, t]() {
        const std::string lo = (t == 0) ? std::string()
            : bytesToHex(cuts[static_cast<size_t>(t - 1)].b, kLen);
        const std::string hi = (static_cast<size_t>(t) >= nCuts) ? std::string()
            : bytesToHex(cuts[static_cast<size_t>(t)].b, kLen);
        slices[static_cast<size_t>(t)] = readRangedRunFiles<W>(inPaths, H, kLen, lo, hi);
      });
    }
    for (auto& th : pool) th.join();
    size_t tot = 0;
    for (const auto& s : slices) tot += s.size();
    src.reserve(tot);
    for (auto& s : slices) {
      for (auto& rec : s) src.push_back(std::move(rec));
      Run<W>().swap(s);  // free the slice as we drain it
    }
  }

  // DDF5: fail LOUD if the projected in-RAM working set exceeds the
  // caller's budget rather than silently OOMing. Working set ~= input +
  // emitted (fan-out at most 2x, occupy in {0,1}) + deduped output, all
  // resident in this one process at once (no spill implemented).
  const size_t recBytes = sizeof(RunRecord<W>) + static_cast<size_t>(maxn) * sizeof(W) + 32;
  const size_t estBytes = src.size() * recBytes * 4;
  if (ramBudget > 0 && estBytes > ramBudget) {
    std::fprintf(stderr,
        "fused_stage: stage too large for in-RAM fusion (est %zu bytes > "
        "budget %zu for %zu input records); needs spill (unimplemented)\n",
        estBytes, ramBudget, src.size());
    return 1;
  }

  const int threads = std::max(1, cores);
  const int ranges  = static_cast<int>(cuts.size()) + 1;
  auto bucketOf = [&](const Sig& s) {
    int lo = 0, hi = static_cast<int>(cuts.size());
    while (lo < hi) {
      const int m = (lo + hi) / 2;
      if (sigCmp(s.b, cuts[m].b, kLen) < 0) hi = m; else lo = m + 1;
    }
    return lo;
  };

  // ---- Phase 1: map + scatter, FUSED (DDF1/DDF3) --------------------------
  // Each thread owns a contiguous slice of `src` AND its own ranges-wide row
  // of output buckets (tl[t][*]) -- zero shared mutable state between
  // threads during this phase, ownership-transfer only. Unlike
  // full_column_bench.cpp's stageMapReduce (which stages per-thread map
  // output into a flat buffer, then scatters in a SEPARATE parallel pass --
  // an artifact of that benchmark measuring map and scatter as one region
  // but wanting a mid-region timestamp), this scatters straight from the
  // map: no intermediate "emitted" buffer, no extra pass over the data.
  std::vector<std::vector<Run<W>>> tl(static_cast<size_t>(threads),
                                      std::vector<Run<W>>(static_cast<size_t>(ranges)));
  std::vector<double> busyMap(static_cast<size_t>(threads), 0.0);
  const auto mapStart = Clock::now();
  {
    std::vector<std::thread> pool;
    pool.reserve(static_cast<size_t>(threads));
    const size_t chunk = (src.size() + static_cast<size_t>(threads) - 1) /
                         static_cast<size_t>(threads);
    for (int t = 0; t < threads; ++t) {
      pool.emplace_back([&, t]() {
        const auto a = Clock::now();
        const size_t i0 = static_cast<size_t>(t) * chunk;
        const size_t i1 = std::min(src.size(), i0 + chunk);
        for (size_t i = i0; i < i1; ++i) {
          const RunRecord<W>& rec = src[i];
          const int ms = rec.minSize();
          if (ms < 0) continue;
          kinkStageTransition(rec.sig, H, r, ms, maxn, [&](const Sig& tg, int shift) {
            const int newLo = static_cast<int>(rec.lo) + shift;
            if (newLo > maxn) return;
            const int newLen = std::min<int>(rec.len, maxn - newLo + 1);
            RunRecord<W> s;
            s.sig    = tg;
            s.H      = static_cast<uint8_t>(H);
            s.keyLen = static_cast<uint8_t>(kLen);
            s.lo     = static_cast<uint8_t>(newLo);
            s.len    = static_cast<uint8_t>(newLen);
            s.counts.assign(rec.counts.begin(), rec.counts.begin() + newLen);
            tl[static_cast<size_t>(t)][static_cast<size_t>(bucketOf(s.sig))].push_back(std::move(s));
          });
        }
        busyMap[static_cast<size_t>(t)] += secs(a, Clock::now());
      });
    }
    for (auto& th : pool) th.join();
  }
  const double mapWall = secs(mapStart, Clock::now());

  // ---- Phase 2: reduce (DDF1/DDF3) -----------------------------------------
  // Each range's owner concatenates every thread's contribution to ITS
  // range, sorts+dedups (the same sortRun/deduplicateRun every other worker
  // uses), and writes the range file. buckets[bk] is written by exactly one
  // thread (bk's own owner) -- ownership-transfer only, no locks.
  std::vector<Run<W>> buckets(static_cast<size_t>(ranges));
  std::vector<double> busyReduce(static_cast<size_t>(ranges), 0.0);
  std::vector<size_t> recCount(static_cast<size_t>(ranges), 0);
  const auto reduceStart = Clock::now();
  {
    std::vector<std::thread> pool;
    pool.reserve(static_cast<size_t>(ranges));
    for (int bk = 0; bk < ranges; ++bk) {
      pool.emplace_back([&, bk]() {
        const auto a = Clock::now();
        Run<W>& B = buckets[static_cast<size_t>(bk)];
        size_t tot = 0;
        for (int t = 0; t < threads; ++t) tot += tl[static_cast<size_t>(t)][static_cast<size_t>(bk)].size();
        B.reserve(tot);
        for (int t = 0; t < threads; ++t)
          for (auto& x : tl[static_cast<size_t>(t)][static_cast<size_t>(bk)]) B.push_back(std::move(x));
        sortRun(B);
        deduplicateRun(B);
        // Write this range's file IN the reduce thread (fused reduce+write):
        // the write loop was single-threaded, the other half of the serial
        // I/O that pinned the worker to ~5 cores. Each range file is
        // independent -> writing them concurrently, one per owning thread, is
        // safe and byte-identical.
        if (!B.empty()) {
          const std::string path = outPrefix + "_u" + std::to_string(bk) + ".bin";
          writeRunFile<W>(B, path, H, kLen, rev);
          recCount[static_cast<size_t>(bk)] = B.size();
        }
        busyReduce[static_cast<size_t>(bk)] += secs(a, Clock::now());
      });
    }
    for (auto& th : pool) th.join();
  }
  const double reduceWall = secs(reduceStart, Clock::now());

  size_t totalRecs = 0;
  for (size_t c : recCount) totalRecs += c;

  double sumBusy = 0.0;
  for (double b : busyMap) sumBusy += b;
  for (double b : busyReduce) sumBusy += b;
  const double regionWall = mapWall + reduceWall;
  const double effCores = regionWall > 0 ? sumBusy / regionWall : 0.0;

  const double cpuS  = cpuSeconds()  - t0Cpu;
  const double wallS = wallSeconds() - t0Wall;
  const double rssMb = peakRssMB();

  // event=done matches map_worker/merge_worker's accounting-line contract
  // exactly (cpu_s/wall_s/peak_rss_mb/records/spill_bytes/stop_key), so
  // orchestrator's existing ParseWorkerOutput needs no change. map_eff_cores
  // is an extra, informational field (parseEventDone ignores unknown keys):
  // the orchestrator derives its own map_eff_cores for telemetry from
  // cpu_s/wall_s (DDF6), this is a same-number cross-check written by the
  // worker that produced them.
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f records=%zu "
              "spill_bytes=0 stop_key= map_eff_cores=%.2f\n",
              cpuS, wallS, rssMb, totalRecs, effCores);
  return 0;
}

int main(int argc, char** argv) {
  raiseFdLimitToHard();

  std::string inStr, outPrefix, cutsStr, rev, counterArg = "u64";
  int H = 0, maxn = 0, stage = -1, cores = 1;
  size_t ramBytes = 0;

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--in"))              inStr      = argv[++i];
    else if (arg("--H"))          H          = std::atoi(argv[++i]);
    else if (arg("--maxn"))       maxn       = std::atoi(argv[++i]);
    else if (arg("--stage"))      stage      = std::atoi(argv[++i]);
    else if (arg("--counter"))    counterArg = argv[++i];
    else if (arg("--cores"))      cores      = std::atoi(argv[++i]);
    else if (arg("--cuts"))       cutsStr    = argv[++i];
    else if (arg("--out-prefix")) outPrefix  = argv[++i];
    else if (arg("--ram"))        ramBytes   = static_cast<size_t>(std::strtoull(argv[++i], nullptr, 10));
    else if (arg("--rev"))        rev        = argv[++i];
    else {
      std::fprintf(stderr, "fused_stage: unknown or incomplete arg: %s\n", argv[i]);
      return 1;
    }
  }

  if (inStr.empty() || H <= 0 || maxn <= 0 || stage < 0 || outPrefix.empty()) {
    std::fprintf(stderr,
        "fused_stage: required: --in --H --maxn --stage --out-prefix\n"
        "usage: fused_stage --in PATH[,PATH,...] --H N --maxn N --stage R\n"
        "                    [--counter u64|u128] [--cores N] [--cuts HEX,...]\n"
        "                    --out-prefix PREFIX [--ram BYTES] [--rev REV]\n");
    return 1;
  }
  if (stage >= H) {
    std::fprintf(stderr, "fused_stage: --stage must be in [0, H)\n");
    return 1;
  }
  if (counterArg != "u64" && counterArg != "u128") {
    std::fprintf(stderr, "fused_stage: --counter must be u64 or u128\n");
    return 1;
  }

  const auto inPaths = splitComma(inStr);
  const int kLen = kinkKeyLen(H);
  const auto cuts = parseCuts(cutsStr, kLen);

  if (counterArg == "u128")
    return runFused<u128>(inPaths, H, maxn, stage, cores, cuts, outPrefix, rev, ramBytes);
  return runFused<u64>(inPaths, H, maxn, stage, cores, cuts, outPrefix, rev, ramBytes);
}
