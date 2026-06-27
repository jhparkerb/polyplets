// merge_worker.cpp — thin CLI wrapper for mergeRunFiles (DESIGN §8, T1.2).
//
// Usage:
//   merge_worker --in PATH[,PATH,...] --H N --out PATH
//                [--counter u64|u128] [--klo HEX] [--khi HEX] [--rev GITREV]
//
// K-way merges a set of sorted POLYRUN files into one output file, optionally
// restricting to the output key range [klo, khi).  Pure function of inputs
// (idempotent, safe to re-run on resume).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "core/libenum.h"
#include "worker/worker_util.h"

int main(int argc, char** argv) {
  std::string in_str, out_path, klo_hex, khi_hex, rev;
  std::string counter_arg = "u64";
  int H = 0;

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--in"))           in_str      = argv[++i];
    else if (arg("--H"))       H           = std::atoi(argv[++i]);
    else if (arg("--out"))     out_path    = argv[++i];
    else if (arg("--counter")) counter_arg = argv[++i];
    else if (arg("--klo"))     klo_hex     = argv[++i];
    else if (arg("--khi"))     khi_hex     = argv[++i];
    else if (arg("--rev"))     rev         = argv[++i];
    else {
      std::fprintf(stderr, "merge_worker: unknown arg: %s\n", argv[i]);
      return 1;
    }
  }

  if (in_str.empty() || H <= 0 || out_path.empty()) {
    std::fprintf(stderr, "merge_worker: required: --in --H --out\n");
    return 1;
  }
  if (counter_arg != "u64" && counter_arg != "u128") {
    std::fprintf(stderr, "merge_worker: --counter must be u64 or u128\n");
    return 1;
  }

  const auto in_paths = splitComma(in_str);

  const double t0_wall = wallSeconds();
  const double t0_cpu  = cpuSeconds();

  size_t body_bytes, out_recs;
  if (counter_arg == "u128") {
    std::tie(body_bytes, out_recs) =
        mergeRunFiles<u128>(in_paths, H, klo_hex, khi_hex, out_path, rev);
  } else {
    std::tie(body_bytes, out_recs) =
        mergeRunFiles<u64>(in_paths, H, klo_hex, khi_hex, out_path, rev);
  }

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu\n",
              cpu_s, wall_s, rss_mb, out_recs, body_bytes);
  return 0;
}
