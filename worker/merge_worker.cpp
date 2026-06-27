// merge_worker.cpp — thin CLI wrapper for mergeRunFiles (DESIGN §8, T1.2).
//
// Usage:
//   merge_worker --in PATH[,PATH,...] --H N --out PATH
//                [--klo HEX] [--khi HEX] [--rev GITREV]
//
// K-way merges a set of sorted POLYRUN files into one output file, optionally
// restricting to the output key range [klo, khi).  Pure function of inputs
// (idempotent, safe to re-run on resume).

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>

#include <sys/resource.h>

#include "core/libenum.h"

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
  std::string in_str, out_path, klo_hex, khi_hex, rev;
  int H = 0;

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--in"))    in_str   = argv[++i];
    else if (arg("--H"))    H        = std::atoi(argv[++i]);
    else if (arg("--out"))  out_path = argv[++i];
    else if (arg("--klo"))  klo_hex  = argv[++i];
    else if (arg("--khi"))  khi_hex  = argv[++i];
    else if (arg("--rev"))  rev      = argv[++i];
    else {
      std::fprintf(stderr, "merge_worker: unknown arg: %s\n", argv[i]);
      return 1;
    }
  }

  if (in_str.empty() || H <= 0 || out_path.empty()) {
    std::fprintf(stderr, "merge_worker: required: --in --H --out\n");
    return 1;
  }

  const auto in_paths = splitComma(in_str);

  const double t0_wall = wallSeconds();
  const double t0_cpu  = cpuSeconds();

  size_t body_bytes = mergeRunFiles<u64>(in_paths, H, klo_hex, khi_hex, out_path, rev);

  // Count output records from the produced file.
  RunFileReader<u64> counter(out_path, H);
  size_t out_recs = counter.records();

  const double cpu_s  = cpuSeconds()  - t0_cpu;
  const double wall_s = wallSeconds() - t0_wall;
  const double rss_mb = peakRssMB();

  std::printf("event=done cpu_s=%.3f wall_s=%.3f peak_rss_mb=%.1f "
              "records=%zu spill_bytes=%zu\n",
              cpu_s, wall_s, rss_mb, out_recs, body_bytes);
  return 0;
}
