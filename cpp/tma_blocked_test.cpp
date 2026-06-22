// Phase 3.2 gate + memory harness: plain a(n) via the blocked drain-and-free sweep,
// summed over strip heights. Prints "n a(n)" and peak store stats to stderr.
// USAGE: tma_blocked_test N [S]   (S = #hash partitions, power of two, default 64)
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "tma/sweep8_blocked.h"

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: %s N [S]\n", argv[0]); return 2; }
  const int maxn = std::atoi(argv[1]);
  const int S = (argc > 2) ? std::atoi(argv[2]) : 64;
  std::vector<u64> tot(maxn + 1, 0);
  u64 peakStates = 0, peakBytes = 0;
  for (int H = 1; H <= maxn; ++H) {
    const std::vector<u64> r =
        sweepSquare8HeightBlocked(H, maxn, S, peakStates, peakBytes);
    for (int n = 1; n <= maxn; ++n) tot[n] += r[n];
  }
  for (int n = 1; n <= maxn; ++n)
    std::printf("%d %llu\n", n, static_cast<unsigned long long>(tot[n]));
  std::fprintf(stderr, "peak_states=%llu peak_block_bytes=%llu S=%d\n",
               static_cast<unsigned long long>(peakStates),
               static_cast<unsigned long long>(peakBytes), S);
  return 0;
}
