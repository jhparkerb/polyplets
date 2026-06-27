// map_worker.cpp — thin CLI wrapper for map_shard_file (DESIGN §8, T1.2).
//
// Usage:
//   map_worker --in PATH[,PATH,...] --H N --maxn N [--fold 0|1]
//              --ram BYTES --spill DIR --out PATH
//              [--lo HEX] [--hi HEX] [--rev GITREV]
//
// Reads POLYRUN source run(s), applies the king-column transition with disk
// spill, writes one sorted POLYRUN output run.  Emits accounting + triangle
// contributions to stdout.

#include <cassert>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>

#ifdef __APPLE__
#include <sys/resource.h>
#else
#include <sys/resource.h>
#endif

#include "core/libenum.h"

// ─── SIGTERM handling ─────────────────────────────────────────────────────────
// map_shard_file checks this flag after each spill and may abort early in M2+.
// For M1, we just let the current operation complete naturally.
static volatile std::sig_atomic_t g_terminate = 0;
static void on_sigterm(int) { g_terminate = 1; }

// ─── Helpers ──────────────────────────────────────────────────────────────────

static std::vector<std::string> splitComma(const std::string& s) {
  std::vector<std::string> parts;
  size_t start = 0;
  while (true) {
    size_t pos = s.find(',', start);
    if (pos == std::string::npos) {
      parts.push_back(s.substr(start));
      break;
    }
    parts.push_back(s.substr(start, pos - start));
    start = pos + 1;
  }
  return parts;
}

static double wallSeconds() {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) * 1e-9;
}

static double cpuSeconds() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
  return static_cast<double>(ru.ru_utime.tv_sec) +
         static_cast<double>(ru.ru_utime.tv_usec) * 1e-6 +
         static_cast<double>(ru.ru_stime.tv_sec) +
         static_cast<double>(ru.ru_stime.tv_usec) * 1e-6;
}

static double peakRssMB() {
  struct rusage ru;
  getrusage(RUSAGE_SELF, &ru);
#ifdef __APPLE__
  return static_cast<double>(ru.ru_maxrss) / (1024.0 * 1024.0);
#else
  return static_cast<double>(ru.ru_maxrss) / 1024.0;
#endif
}

int main(int argc, char** argv) {
  std::signal(SIGTERM, on_sigterm);

  // ─── Arg parsing ────────────────────────────────────────────────────────────
  std::string in_str, out_path, spill_dir, lo_hex, hi_hex, rev;
  int H = 0, maxn = 0, fold = 0;
  size_t ram_bytes = 128ULL * 1024 * 1024;  // 128 MB default

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--in"))    in_str    = argv[++i];
    else if (arg("--H"))     H         = std::atoi(argv[++i]);
    else if (arg("--maxn"))  maxn      = std::atoi(argv[++i]);
    else if (arg("--fold"))  fold      = std::atoi(argv[++i]);
    else if (arg("--ram"))   ram_bytes = static_cast<size_t>(std::strtoull(argv[++i], nullptr, 10));
    else if (arg("--spill")) spill_dir = argv[++i];
    else if (arg("--out"))   out_path  = argv[++i];
    else if (arg("--lo"))    lo_hex    = argv[++i];
    else if (arg("--hi"))    hi_hex    = argv[++i];
    else if (arg("--rev"))   rev       = argv[++i];
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

  TriangleRow<u64> triangle(H, maxn);
  auto [spill_bytes, out_recs] = map_shard_file<u64, ClassifyTriangle>(
      in_paths, cfg, out_path, lo_hex, hi_hex, triangle, rev);

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  // Emit triangle contributions (non-zero entries).
  for (int n = 1; n <= maxn; ++n) {
    if (triangle.row[n] != u64{0})
      std::printf("tri %d %d %llu\n", H, n, (unsigned long long)triangle.row[n]);
  }

  // Emit accounting line.
  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu\n",
              cpu_s, wall_s, rss_mb, out_recs, spill_bytes);

  return g_terminate ? 1 : 0;
}
