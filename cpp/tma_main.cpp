// TMA driver (Layer 2 v0). Square-4 only for now: the validation plug-in.
//
// CLI:  tma square4 MAXN [--per-height]
//   totals: "n count" lines; --per-height: "h n count" lines.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#include "tma/sweep.h"

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s square4 MAXN [--per-height]\n", argv[0]);
    return 2;
  }
  if (std::string(argv[1]) != "square4") {
    std::fprintf(stderr,
                 "only the square4 validation lattice exists so far\n");
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > 18) {
    std::fprintf(stderr, "MAXN out of range (1..18 for the v0 engine)\n");
    return 2;
  }
  const bool perHeight = (argc > 3 && std::strcmp(argv[3], "--per-height") == 0);

  SweepResults res = sweepSquare4(maxn);

  if (perHeight) {
    for (int h = 1; h <= maxn; ++h)
      for (int n = 1; n <= maxn; ++n)
        if (res.byHeight[h][n])
          std::printf("%d %d %llu\n", h, n,
                      static_cast<unsigned long long>(res.byHeight[h][n]));
  } else {
    for (int n = 1; n <= maxn; ++n)
      std::printf("%d %llu\n", n,
                  static_cast<unsigned long long>(res.totals[n]));
  }
  return 0;
}
