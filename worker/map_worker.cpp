// map_worker.cpp — thin CLI wrapper for map_shard_file (DESIGN §8, T1.2).
//
// Usage:
//   map_worker --in PATH[,PATH,...] --H N --maxn N [--fold 0|1]
//              --ram BYTES --spill DIR --out PATH
//              [--counter u64|u128] [--lo HEX] [--hi HEX] [--rev GITREV]
//
// Reads POLYRUN source run(s), applies the king-column transition with disk
// spill, writes one sorted POLYRUN output run.  Emits accounting + triangle
// contributions to stdout.

#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "core/libenum.h"
#include "worker/worker_util.h"

// ─── SIGTERM handling ─────────────────────────────────────────────────────────
// map_shard_file checks this flag after each spill and may abort early in M2+.
// For M1, we just let the current operation complete naturally.
static volatile std::sig_atomic_t g_terminate = 0;
static void on_sigterm(int) { g_terminate = 1; }

int main(int argc, char** argv) {
  std::signal(SIGTERM, on_sigterm);

  // ─── Arg parsing ────────────────────────────────────────────────────────────
  std::string in_str, out_path, spill_dir, lo_hex, hi_hex, rev;
  std::string counter_arg = "u64";
  int H = 0, maxn = 0, fold = 0;
  size_t ram_bytes = 128ULL * 1024 * 1024;  // 128 MB default

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--in"))          in_str      = argv[++i];
    else if (arg("--H"))      H           = std::atoi(argv[++i]);
    else if (arg("--maxn"))   maxn        = std::atoi(argv[++i]);
    else if (arg("--fold"))   fold        = std::atoi(argv[++i]);
    else if (arg("--ram"))    ram_bytes   = static_cast<size_t>(std::strtoull(argv[++i], nullptr, 10));
    else if (arg("--spill"))  spill_dir   = argv[++i];
    else if (arg("--out"))    out_path    = argv[++i];
    else if (arg("--counter"))counter_arg = argv[++i];
    else if (arg("--lo"))     lo_hex      = argv[++i];
    else if (arg("--hi"))     hi_hex      = argv[++i];
    else if (arg("--rev"))    rev         = argv[++i];
    else {
      std::fprintf(stderr, "map_worker: unknown arg: %s\n", argv[i]);
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

  const auto in_paths = splitComma(in_str);

  ShardCfg cfg;
  cfg.H                = H;
  cfg.maxn             = maxn;
  cfg.fold             = fold != 0;
  cfg.ram_budget_bytes = ram_bytes;
  cfg.spill_dir        = spill_dir;

  // ─── Run ────────────────────────────────────────────────────────────────────
  const double t0_wall = wallSeconds();
  const double t0_cpu  = cpuSeconds();

  size_t spill_bytes, out_recs;

  if (counter_arg == "u128") {
    TriangleRow<u128> triangle(H, maxn);
    std::tie(spill_bytes, out_recs) = map_shard_file<u128, ClassifyTriangle>(
        in_paths, cfg, out_path, lo_hex, hi_hex, triangle, rev);
    printTriangleRows(H, maxn, triangle.row);
  } else {
    TriangleRow<u64> triangle(H, maxn);
    std::tie(spill_bytes, out_recs) = map_shard_file<u64, ClassifyTriangle>(
        in_paths, cfg, out_path, lo_hex, hi_hex, triangle, rev);
    printTriangleRows(H, maxn, triangle.row);
  }

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  // Emit accounting line.
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu\n",
              cpu_s, wall_s, rss_mb, out_recs, spill_bytes);

  return g_terminate ? 1 : 0;
}
