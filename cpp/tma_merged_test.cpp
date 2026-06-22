// C3 gate harness: a(n) mod p via the merged R1xR2xR3 engine (fold x ranged x u32-modp),
// summed over strip heights. Run for several primes; tests/gate_merged.py CRTs the rows
// and checks a(n) == A006770. Also prints the peak ranged-modp store bytes (the RAM win).
// USAGE: tma_merged_test N P
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>

#include "tma/sweep8_merged.h"

int main(int argc, char** argv) {
  if (argc < 3) { std::fprintf(stderr, "usage: %s N P\n", argv[0]); return 2; }
  const int maxn = std::atoi(argv[1]);
  const std::uint32_t p = static_cast<std::uint32_t>(std::strtoul(argv[2], nullptr, 10));

  std::vector<u64> tot(maxn + 1, 0);
  u64 peakStates = 0, peakBytes = 0;
  for (int H = 1; H <= maxn; ++H) {
    const std::vector<u64> r = sweepSquare8HeightMerged(H, maxn, p, peakStates, peakBytes);
    for (int n = 1; n <= maxn; ++n) tot[n] = (tot[n] + r[n]) % p;
  }
  for (int n = 1; n <= maxn; ++n)
    std::printf("%d %llu\n", n, static_cast<unsigned long long>(tot[n]));
  std::fprintf(stderr, "peak_states=%llu peak_bytes=%llu p=%u (merged R1xR2xR3)\n",
               static_cast<unsigned long long>(peakStates),
               static_cast<unsigned long long>(peakBytes), p);
  return 0;
}
