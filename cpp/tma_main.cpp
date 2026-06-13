// TMA driver (Layer 2 v0). Square-4 only for now: the validation plug-in.
//
// CLI:  tma square4 MAXN [--per-height]
//   totals: "n count" lines; --per-height: "h n count" lines.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#include "tma/sweep.h"
#include "tma/sweep8.h"

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr, "usage: %s {square4|square8} MAXN [--per-height]\n",
                 argv[0]);
    return 2;
  }
  const std::string lattice = argv[1];
  if (lattice != "square4" && lattice != "square8") {
    std::fprintf(stderr, "lattice must be square4 or square8 (v0 engine)\n");
    return 2;
  }
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > 18) {
    std::fprintf(stderr, "MAXN out of range (1..18 for the v0 engine)\n");
    return 2;
  }
  const bool perHeight = (argc > 3 && std::strcmp(argv[3], "--per-height") == 0);

  SweepResults res =
      (lattice == "square4") ? sweepSquare4(maxn) : sweepSquare8(maxn);

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
