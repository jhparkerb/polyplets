// Phase 4 gate: plain a(n) via the fully OUT-OF-CORE sweep (db/next as disk
// partitions), summed over strip heights. Must equal the exact a(n) = A006770.
// USAGE: tma_ooc_test N [S] [scratchdir]   (S = #partitions, pow2, default 8)
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

#include "tma/sweep8_ooc.h"

namespace fs = std::filesystem;

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: %s N [S] [dir]\n", argv[0]); return 2; }
  const int maxn = std::atoi(argv[1]);
  const int S = (argc > 2) ? std::atoi(argv[2]) : 8;
  const std::string dir = (argc > 3) ? argv[3] : "build/ooc_scratch";
  fs::create_directories(dir);

  std::vector<u64> tot(maxn + 1, 0);
  u64 peakStates = 0;
  for (int H = 1; H <= maxn; ++H) {
    const std::vector<u64> r = sweepSquare8HeightOOC(H, maxn, S, dir, peakStates);
    for (int n = 1; n <= maxn; ++n) tot[n] += r[n];
  }
  for (int n = 1; n <= maxn; ++n)
    std::printf("%d %llu\n", n, static_cast<unsigned long long>(tot[n]));
  std::fprintf(stderr, "peak_states=%llu S=%d (out-of-core, RAM ~ peak/S)\n",
               static_cast<unsigned long long>(peakStates), S);
  return 0;
}
