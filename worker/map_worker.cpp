// map_worker.cpp — thin CLI wrapper for map_shard_file (DESIGN §8, T1.2),
// plus the kink-carry kernel (Design 14 Phase 2.4).
//
// Usage (column kernel, default):
//   map_worker --in PATH[,PATH,...] --H N --maxn N [--fold 0|1]
//              --ram BYTES --spill DIR --out PATH
//              [--counter u64|u128] [--lo HEX] [--hi HEX] [--rev GITREV]
//
// Usage (kink kernel):
//   map_worker --kernel kink --stage seed|<int>|finalize
//              --in PATH[,PATH,...] --H N --maxn N [--fold 0|1]
//              --ram BYTES --spill DIR --out PATH
//              [--counter u64|u128] [--lo HEX] [--hi HEX] [--rev GITREV]
//
// Column kernel: reads POLYRUN source run(s), applies the king-column
// transition with disk spill, writes one sorted POLYRUN output run. Emits
// accounting + triangle contributions to stdout.
//
// Kink kernel: --stage selects which of the column's H+2 steps this
// invocation performs (mirrors sweepHeightKink's per-column stage
// sub-loop, orchestrator/sweep.go):
//   seed      column start: harvest (classify) the previous column's
//             end-of-column records (--in keyed H+2), seed stage 0
//             (--out keyed H+4). In-RAM (kinkSeedStage0) -- no spill.
//   <int> r   one of the H mid-column stage transitions (--in/--out both
//             keyed H+4). File-backed, spills past --ram
//             (map_shard_stage_file) -- the parallel-shard/merge-barrier
//             path Design 14 is actually about.
//   finalize  column end: drop the carry, stranding-check, canonicalize,
//             prune, fold (--in keyed H+4, --out keyed H+2). In-RAM
//             (kinkFinalizeColumn) -- no spill, no classify (harvest
//             already happened at seed).
// seed/finalize are in-RAM per Design 14 Phase 2's scope (a(20)-gate scale
// never needs to spill an intermediate column table; file-backed variants
// are a Phase 3 concern). Both still respect --lo/--hi so a sharded unit
// only processes its own key range, matching the column kernel's contract.
// v1 = triangle only: rejects --holes with --kernel kink (the holes Euler
// accumulator collides with the kink carry byte at the same sig offset,
// see core/kink.h).

#include <cctype>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#include "core/fdlimit.h"
#include "core/kink.h"
#include "core/kink_column.h"
#include "core/libenum.h"
#include "worker/worker_util.h"

// Read+range-filter+merge a set of POLYRUN files into one sorted,
// deduplicated in-RAM Run<W>, keyed at `keyLen`. The kink kernel's seed/
// finalize steps are in-RAM (no spill, see file header); this is their read
// side, mirroring map_shard_file's range-filter logic (core/mapreduce.h)
// without the transition -- just merge-by-key over the input files.
template <class W>
static Run<W> readRangedRunFiles(const std::vector<std::string>& paths, int H,
                                 int keyLen, const std::string& lo_hex,
                                 const std::string& hi_hex) {
  requireKeyLenFits(keyLen, "map_worker");
  uint8_t lo_sig[SIGMAX] = {};
  uint8_t hi_sig[SIGMAX] = {};
  const bool has_lo = parseKeyBound(lo_hex, lo_sig, keyLen, "map_worker", "lo");
  const bool has_hi = parseKeyBound(hi_hex, hi_sig, keyLen, "map_worker", "hi");
  Run<W> run;
  for (const auto& p : paths) {
    RunFileReader<W> r(p, H, keyLen);
    if (!r.ok()) {
      std::fprintf(stderr, "map_worker: cannot read input %s\n", p.c_str());
      std::exit(1);
    }
    if (has_lo) r.seekToKey(lo_sig);
    RunRecord<W> rec;
    while (r.next(rec)) {
      if (has_lo && sigCmp(rec.sig.b, lo_sig, keyLen) < 0) continue;
      if (has_hi && sigCmp(rec.sig.b, hi_sig, keyLen) >= 0) break;
      run.push_back(std::move(rec));
    }
  }
  sortRun(run);
  deduplicateRun(run);
  return run;
}

// Write an in-RAM Run<W> to a POLYRUN file with its .idx sidecar (so the
// orchestrator's normal SampleKeys-based partitioning works on kink
// seed/finalize outputs exactly as it does on column-kernel outputs).
template <class W>
static size_t writeRunFile(const Run<W>& run, const std::string& out_path,
                           int H, int keyLen, const std::string& rev) {
  RunFileWriter<W> w(out_path, H, 0, "", "", rev, keyLen, /*write_index=*/true,
                     /*compress=*/frontierZstd());
  for (const auto& r : run) w.append(r);
  return w.finalize();
}

// SIGTERM handling (cooperative work-stealing stop, DESIGN 08, T2.3) is
// shared with merge_worker.cpp: see worker_util.h's g_workerTerminate/
// installWorkerSigtermHandler. map_shard_file watches g_workerTerminate,
// stops reading at the next key boundary (the cursor), and finalizes a
// fully valid sorted output over [lo, cursor); the cursor comes back in
// stop_key. This is a clean, successful exit (status 0) — distinct from a
// hard SIGKILL (used by the orchestrator's ctx-cancel for checkpoint/
// shutdown), which is uncatchable and discards the partial column for a
// later --resume.

// runOneRequest does everything a one-shot map_worker invocation always did:
// parse one request's args, do the map/merge-shard work, emit accounting.
// Factored out of main() so --persistent (below) can call it once per line
// read from stdin instead of once per process -- eliminating the fork+exec
// cost paid on every single work unit (thousands of sub-second invocations
// per real run; confirmed the dominant real cost via a real heap-alloc
// profile plus direct observation, not a hunch -- see
// docs/utilization-bottleneck-log.md Bottleneck #5).
// `tokens` is the flag/value list with no program name (argv+1..argc in the
// one-shot path; a tokenized stdin line in persistent mode) -- byte-for-byte
// the same flags, same semantics, same output contract either way.
static int runOneRequest(const std::vector<std::string>& tokens) {
  // ─── Arg parsing ────────────────────────────────────────────────────────────
  std::string in_str, out_path, spill_dir, lo_hex, hi_hex, rev;
  std::string counter_arg = "u64";
  std::string kernel_arg = "column";
  std::string stage_arg;
  int H = 0, maxn = 0, fold = 0, holes = 0;
  size_t ram_bytes = 128ULL * 1024 * 1024;  // 128 MB default

  const int n = static_cast<int>(tokens.size());
  for (int i = 0; i < n; ++i) {
    auto arg = [&](const char* flag) {
      return tokens[i] == flag && i + 1 < n;
    };
    auto flag = [&](const char* name) {
      return tokens[i] == name;
    };
    if (arg("--in"))          in_str      = tokens[++i];
    else if (arg("--H"))      H           = std::atoi(tokens[++i].c_str());
    else if (arg("--maxn"))   maxn        = std::atoi(tokens[++i].c_str());
    else if (arg("--fold"))   fold        = std::atoi(tokens[++i].c_str());
    else if (arg("--ram"))    ram_bytes   = static_cast<size_t>(std::strtoull(tokens[++i].c_str(), nullptr, 10));
    else if (arg("--spill"))  spill_dir   = tokens[++i];
    else if (arg("--out"))    out_path    = tokens[++i];
    else if (arg("--counter"))counter_arg = tokens[++i];
    else if (arg("--lo"))     lo_hex      = tokens[++i];
    else if (arg("--hi"))     hi_hex      = tokens[++i];
    else if (arg("--rev"))    rev         = tokens[++i];
    else if (arg("--kernel")) kernel_arg  = tokens[++i];
    else if (arg("--stage"))  stage_arg   = tokens[++i];
    else if (flag("--holes")) holes       = 1;
    else {
      std::fprintf(stderr, "map_worker: unknown arg: %s\n", tokens[i].c_str());
      return 1;
    }
  }

  if (in_str.empty() || H <= 0 || maxn <= 0 || out_path.empty() || spill_dir.empty()) {
    std::fprintf(stderr,
      "map_worker: required: --in --H --maxn --ram --spill --out\n");
    return 1;
  }
  if (counter_arg != "u64" && counter_arg != "u128") {
    std::fprintf(stderr, "map_worker: --counter must be u64 or u128\n");
    return 1;
  }
  if (kernel_arg != "column" && kernel_arg != "kink") {
    std::fprintf(stderr, "map_worker: --kernel must be column or kink\n");
    return 1;
  }
  const bool kink = (kernel_arg == "kink");
  if (kink && holes) {
    std::fprintf(stderr, "map_worker: --kernel kink does not support --holes "
                         "(v1 is triangle-only; the carry byte and the holes "
                         "Euler accumulator collide at the same sig offset)\n");
    return 1;
  }
  int kink_stage = -1;  // -1 = seed, -2 = finalize, >=0 = mid-column stage r
  if (kink) {
    if (stage_arg.empty()) {
      std::fprintf(stderr, "map_worker: --kernel kink requires --stage\n");
      return 1;
    }
    if (stage_arg == "seed") {
      kink_stage = -1;
    } else if (stage_arg == "finalize") {
      kink_stage = -2;
    } else {
      kink_stage = std::atoi(stage_arg.c_str());
      if (kink_stage < 0 || kink_stage >= H) {
        std::fprintf(stderr,
          "map_worker: --stage must be seed, finalize, or an int in [0, H)\n");
        return 1;
      }
    }
  }

  // REFUSE AT START (V5): the key width this request implies must fit SIGMAX
  // before any file is opened. The kink kernel's H+4 key is the reachable case
  // (H >= 29 at SIGMAX=32); the column kernel's H+2 / holes H+3 are checked by
  // the same call so no path is exempt. Every SIGMAX-sized stack buffer
  // downstream (range filters, seekToKey's probe, deserializeRecord's zero-pad)
  // depends on this.
  requireKeyLenFits(kink ? kinkKeyLen(H) : (holes ? H + 3 : H + 2), "map_worker");

  const auto in_paths = splitComma(in_str);

  // maxholes: conservative upper bound; polyplets can tile holes densely.
  const int maxholes = maxn;

  ShardCfg cfg;
  cfg.H                = H;
  cfg.maxn             = maxn;
  cfg.fold             = fold != 0;
  cfg.ram_budget_bytes = ram_bytes;
  cfg.spill_dir        = spill_dir;
  if (holes) cfg.keyLen = H + 3;

  // ─── Run ────────────────────────────────────────────────────────────────────
  const double t0_wall = wallSeconds();
  const double t0_cpu  = cpuSeconds();

  // Throttled progress emitter: at most one event=progress line every ~2s,
  // EXCEPT the very first call, which fires immediately regardless of
  // elapsed time. The orchestrator streams these to drive the within-column
  // heartbeat AND gates work-stealing eligibility on processed>0
  // (stealEligible, orchestrator/sweep.go) -- with the old unconditional 2s
  // throttle, any unit whose whole runtime was under 2s reported
  // processed=0 for its entire life, making it permanently un-stealable no
  // matter how much of the pool was waiting on it (found investigating why
  // a single-unit-inflight column with idle thief-workers spinning on
  // pickVictim never actually stole anything: picked=false because
  // processed=0 the whole time, elapsed well under 2s). The wall-time-floor
  // fix (Bottleneck #1, commit 208864b) never reached this -- it only
  // patched stealEligible's record-count gate, downstream of this earlier,
  // harder processed==0 early return.
  double last_emit = t0_wall;
  bool emitted_once = false;
  auto on_progress = [&](size_t n) {
    const double now = wallSeconds();
    if (!emitted_once || now - last_emit >= 2.0) {
      emitted_once = true;
      last_emit = now;
      std::printf("event=progress processed=%zu elapsed_s=%.1f\n", n, now - t0_wall);
      std::fflush(stdout);
    }
  };

  size_t spill_bytes, out_recs;
  std::string stop_key;  // set iff SIGTERM stopped us early (work-stealing cursor)

  if (kink) {
    spill_bytes = 0;
    if (kink_stage == -1) {
      // seed: H+2-keyed source -> harvest + H+4-keyed stage-0 table. In-RAM
      // (no spill, see file header); still range-filtered so a sharded unit
      // only harvests/seeds its own key range.
      if (counter_arg == "u128") {
        auto src = readRangedRunFiles<u128>(in_paths, H, H + 2, lo_hex, hi_hex);
        TriangleRow<u128> triangle(H, maxn);
        auto stage0 = kinkSeedStage0<u128, ClassifyTriangle>(src, H, triangle);
        out_recs = writeRunFile<u128>(stage0, out_path, H, kinkKeyLen(H), rev);
        printTriangleRows(H, maxn, triangle.row);
      } else {
        auto src = readRangedRunFiles<u64>(in_paths, H, H + 2, lo_hex, hi_hex);
        TriangleRow<u64> triangle(H, maxn);
        auto stage0 = kinkSeedStage0<u64, ClassifyTriangle>(src, H, triangle);
        out_recs = writeRunFile<u64>(stage0, out_path, H, kinkKeyLen(H), rev);
        printTriangleRows(H, maxn, triangle.row);
      }
    } else if (kink_stage == -2) {
      // finalize: H+4-keyed final stage table -> H+2-keyed next column. In-RAM,
      // no classify (harvest already happened at seed).
      if (counter_arg == "u128") {
        auto src = readRangedRunFiles<u128>(in_paths, H, kinkKeyLen(H), lo_hex, hi_hex);
        auto next = kinkFinalizeColumn<u128>(src, H, maxn, fold != 0);
        out_recs = writeRunFile<u128>(next, out_path, H, H + 2, rev);
      } else {
        auto src = readRangedRunFiles<u64>(in_paths, H, kinkKeyLen(H), lo_hex, hi_hex);
        auto next = kinkFinalizeColumn<u64>(src, H, maxn, fold != 0);
        out_recs = writeRunFile<u64>(next, out_path, H, H + 2, rev);
      }
    } else {
      // mid-column stage r: H+4-keyed table -> H+4-keyed table for stage+1.
      // File-backed, spills past --ram (the parallel-shard/merge-barrier
      // path Design 14 is actually about) -- unlike seed/finalize above.
      KinkStageCfg kcfg{H, maxn, kink_stage, ram_bytes, spill_dir};
      if (counter_arg == "u128") {
        std::tie(spill_bytes, out_recs) = map_shard_stage_file<u128>(
            in_paths, kcfg, out_path, lo_hex, hi_hex, rev, on_progress,
            &g_workerTerminate, &stop_key);
      } else {
        std::tie(spill_bytes, out_recs) = map_shard_stage_file<u64>(
            in_paths, kcfg, out_path, lo_hex, hi_hex, rev, on_progress,
            &g_workerTerminate, &stop_key);
      }
    }
  } else if (holes) {
    if (counter_arg == "u128") {
      HolesRow<u128> hrow(H, maxn, maxholes);
      std::tie(spill_bytes, out_recs) = map_shard_file<u128, ClassifyHoles>(
          in_paths, cfg, out_path, lo_hex, hi_hex, hrow, rev, on_progress,
          &g_workerTerminate, &stop_key);
      printHolesRows(H, maxn, hrow.byNHoles);
    } else {
      HolesRow<u64> hrow(H, maxn, maxholes);
      std::tie(spill_bytes, out_recs) = map_shard_file<u64, ClassifyHoles>(
          in_paths, cfg, out_path, lo_hex, hi_hex, hrow, rev, on_progress,
          &g_workerTerminate, &stop_key);
      printHolesRows(H, maxn, hrow.byNHoles);
    }
  } else if (counter_arg == "u128") {
    TriangleRow<u128> triangle(H, maxn);
    std::tie(spill_bytes, out_recs) = map_shard_file<u128, ClassifyTriangle>(
        in_paths, cfg, out_path, lo_hex, hi_hex, triangle, rev, on_progress,
        &g_workerTerminate, &stop_key);
    printTriangleRows(H, maxn, triangle.row);
  } else {
    TriangleRow<u64> triangle(H, maxn);
    std::tie(spill_bytes, out_recs) = map_shard_file<u64, ClassifyTriangle>(
        in_paths, cfg, out_path, lo_hex, hi_hex, triangle, rev, on_progress,
        &g_workerTerminate, &stop_key);
    printTriangleRows(H, maxn, triangle.row);
  }

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  // Emit accounting line.  stop_key is non-empty iff we stopped early at a
  // work-stealing cursor: the output covers [lo, stop_key) and the orchestrator
  // requeues [stop_key, hi).  Empty stop_key = ran to natural completion.
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu stop_key=%s\n",
              cpu_s, wall_s, rss_mb, out_recs, spill_bytes, stop_key.c_str());

  // A cooperative early stop is a SUCCESS (status 0): the partial output is
  // complete and valid over its range.  Only a real failure returns nonzero.
  return 0;
}

// Whitespace-split a stdin request line into tokens. Paths are orchestrator-
int main(int argc, char** argv) {
  raiseFdLimitToHard();  // the spill/merge path fans out to many open files
  installWorkerSigtermHandler();
  return runWorkerMain(argc, argv, runOneRequest);
}
