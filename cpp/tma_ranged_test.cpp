// R2 gate + memory harness: plain a(n) via the ranged-row sweep, summed over strip
// heights. Prints "n a(n)" (n=1..N) and peak store stats to stderr.
// USAGE: tma_ranged_test N
// Gate (tests/gate_ranged.py): a(n) == exact build/tma; reports the memory ratio.
#include <cstdio>
#include <cstdlib>
#include <vector>

#include "tma/sweep8_ranged.h"

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: %s N\n", argv[0]); return 2; }
  const int maxn = std::atoi(argv[1]);
  std::vector<u64> tot(maxn + 1, 0);
  u64 peakStates = 0, peakBytes = 0;
  for (int H = 1; H <= maxn; ++H) {
    const std::vector<u64> r = sweepSquare8HeightRanged(H, maxn, peakStates, peakBytes);
    for (int n = 1; n <= maxn; ++n) tot[n] += r[n];
  }
  for (int n = 1; n <= maxn; ++n)
    std::printf("%d %llu\n", n, static_cast<unsigned long long>(tot[n]));
  // exact-store bytes for the same peak: cap(=peak/0.85, pow2) * (Sig + row + used)
  std::fprintf(stderr, "peak_states=%llu peak_ranged_bytes=%llu\n",
               static_cast<unsigned long long>(peakStates),
               static_cast<unsigned long long>(peakBytes));
  return 0;
}
