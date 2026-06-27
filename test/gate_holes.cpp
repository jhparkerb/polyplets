// gate_holes.cpp — T5.4 gate: per-(n,H,holes) distribution byte-identical to
// build/tma_holes square8 N --holes --per-height (old engine).
//
// Usage:
//   gate_holes [--maxn N]
//
// Runs the new-system ClassifyHoles sweeps for H=1..maxn, prints results in
// the same "holes H n k count" format that gate_holes.py compares against the
// oracle.  Non-zero exit on mismatch.

#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <tuple>
#include <unistd.h>
#include <sys/stat.h>
#include <vector>

#include "core/libenum.h"
#include "worker/worker_util.h"

// Write seed state for the holes path (keyLen = H+3).
static std::string writeHolesSeed(const std::string& dir, int H, int maxn,
                                  const std::string& rev) {
  const int kLen = H + 3;
  std::string path = dir + "/hseed_h" + std::to_string(H) + ".bin";
  RunFileWriter<u64> w(path, H, maxn, "", "", rev, kLen);
  w.append(seedRecord<u64>(H, kLen));
  w.finalize();
  return path;
}

int main(int argc, char** argv) {
  int maxn = 12;

  for (int i = 1; i < argc; ++i) {
    auto arg = [&](const char* flag) {
      return std::strcmp(argv[i], flag) == 0 && i + 1 < argc;
    };
    if (arg("--maxn")) maxn = std::atoi(argv[++i]);
    else {
      std::fprintf(stderr, "gate_holes: unknown arg: %s\n", argv[i]);
      return 1;
    }
  }

  // Safe upper bound: each hole requires >=4 cells but a polyplet can tile
  // holes densely (e.g. a chain of 2x3 rings). Use maxn as a conservative cap.
  const int maxholes = maxn;

  // Spill dir.
  std::string spill_dir = "/tmp/ns_gate_holes_" +
                          std::to_string(static_cast<long>(getpid()));
  if (mkdir(spill_dir.c_str(), 0777) != 0 && errno != EEXIST) {
    std::perror(("gate_holes: mkdir " + spill_dir).c_str());
    return 1;
  }

  const char* rev = GIT_REV;

  // Accumulate: (H, n, holes) -> count
  std::map<std::tuple<int,int,int>, uint64_t> results;

  for (int H = 1; H <= maxn; ++H) {
    const int kLen = H + 3;

    ShardCfg cfg;
    cfg.H                = H;
    cfg.maxn             = maxn;
    cfg.fold             = false;
    cfg.ram_budget_bytes = 64ULL * 1024 * 1024;
    cfg.spill_dir        = spill_dir;
    cfg.keyLen           = kLen;

    std::string frontier = writeHolesSeed(spill_dir, H, maxn, rev);

    HolesRow<u64> hrow(H, maxn, maxholes);

    for (int col = 0; col <= maxn; ++col) {
      std::string next = spill_dir + "/hh" + std::to_string(H) +
                         "_col" + std::to_string(col + 1) + ".bin";

      auto [sb, recs] = map_shard_file<u64, ClassifyHoles>(
          {frontier}, cfg, next, "", "", hrow, rev);
      (void)sb;

      std::remove(frontier.c_str());
      frontier = next;

      if (recs == 0) {
        std::remove(frontier.c_str());
        break;
      }
    }

    // Collect this height's results.
    for (int n = 1; n <= maxn; ++n) {
      if (n >= static_cast<int>(hrow.byNHoles.size())) continue;
      for (int k = 0; k < static_cast<int>(hrow.byNHoles[n].size()); ++k) {
        if (hrow.byNHoles[n][k] == 0) continue;
        results[{H, n, k}] += hrow.byNHoles[n][k];
      }
    }
  }

  // Cleanup spill dir (best effort).
  ::rmdir(spill_dir.c_str());

  // Print in oracle format: "H n k count"
  for (const auto& [key, cnt] : results) {
    const auto [H, n, k] = key;
    std::printf("%d %d %d %llu\n", H, n, k, (unsigned long long)cnt);
  }

  return 0;
}
