// R3 small-scale test harness: plain a(n) via the u32 mod-p sweep, summed over
// strip heights. Prints "n  a(n) mod P" for n=1..N and peak_states to stderr.
// USAGE: tma_modp_test N P [--fold]
// The gate (tests/gate_modp.py) runs this for several primes and CRTs the columns
// back to the exact a(n) from build/tma.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "tma/sweep8_modp.h"

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s N P [--fold]\n", argv[0]);
    return 2;
  }
  const int maxn = std::atoi(argv[1]);
  const std::uint32_t p = static_cast<std::uint32_t>(std::strtoul(argv[2], nullptr, 10));
  const bool fold = (argc > 3 && std::strcmp(argv[3], "--fold") == 0);

  std::vector<std::uint64_t> tot(maxn + 1, 0);
  u64 peak = 0;
  for (int H = 1; H <= maxn; ++H) {
    const std::vector<std::uint32_t> r = sweepSquare8HeightModP(H, maxn, p, fold, peak);
    for (int n = 1; n <= maxn; ++n) tot[n] = (tot[n] + r[n]) % p;
  }
  for (int n = 1; n <= maxn; ++n)
    std::printf("%d %llu\n", n, static_cast<unsigned long long>(tot[n]));
  std::fprintf(stderr, "peak_states=%llu p=%u fold=%d\n",
               static_cast<unsigned long long>(peak), p, fold ? 1 : 0);
  return 0;
}
