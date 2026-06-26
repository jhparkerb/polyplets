// driver0.cpp — AC-0 in-RAM driver for map_shard + mergeRuns (T0.5).
//
// Runs one height-sweep at a time (H=1..maxn) using the in-RAM libenum core;
// accumulates the triangle T(n,H); compares Σ_H T(n,H) to known a(n) values.
//
// Usage:
//   driver0 [--maxn N] [--fold] [--fold-check] [--oracle-tma PATH --out FILE]
//
// Modes:
//   default (--maxn N): print triangle rows + verify Σ_H == known a(n) for n≤N
//   --fold-check: verify fold==unfold byte-identical (gate_fold)
//   --oracle-tma PATH --out FILE: write triangle for comparison with old engine

#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <numeric>
#include <string>
#include <vector>

#include "core/libenum.h"

// Known a(n) for n=1..18 from fixtures/b006770.txt
static const uint64_t KNOWN[] = {
  0, // index 0 unused
  1, 4, 20, 110, 638, 3832, 23592, 147941,
  940982, 6053180, 39299408, 257105146, 1692931066, 11208974860ULL,
  74570549714ULL, 498174818986ULL, 3340366308393ULL, 22471158811164ULL,
};
static const int N_KNOWN = static_cast<int>(sizeof(KNOWN) / sizeof(KNOWN[0])) - 1;

// One height-sweep: returns the triangle row T[n] for height H over n=0..maxn.
static std::vector<uint64_t> sweepHeight(int H, int maxn, bool fold) {
  using W = u64;

  // Seed: one source state (empty boundary, counts[0]=1)
  Run<W> frontier;
  {
    RunRecord<W> seed;
    std::memset(seed.sig.b, 0, SIGMAX);
    seed.H = H; seed.lo = 0; seed.len = 1; seed.counts = {W{1}};
    frontier.push_back(seed);
  }

  ShardCfg cfg{H, maxn, fold};
  TriangleRow<W> triangle(H, maxn);

  for (int col = 0; col <= maxn && !frontier.empty(); ++col) {
    // The whole frontier is one shard (in-RAM, no partitioning yet).
    // map_shard drives completion (classify) side and returns successor run.
    Run<W> next = map_shard<W, ClassifyTriangle>(frontier, cfg, triangle);
    frontier = std::move(next);
  }

  return triangle.row; // indexed [0..maxn]
}

int main(int argc, char** argv) {
  int  maxn     = 14;
  bool fold     = false;
  bool foldCheck = false;
  const char* oracleTma = nullptr;
  const char* outFile   = nullptr;

  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--maxn") && i + 1 < argc)
      maxn = std::atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--fold"))
      fold = true;
    else if (!std::strcmp(argv[i], "--fold-check"))
      foldCheck = true;
    else if (!std::strcmp(argv[i], "--oracle-tma") && i + 1 < argc) {
      oracleTma = argv[++i]; (void)oracleTma; // reserved for future oracle-diff mode
    }
    else if (!std::strcmp(argv[i], "--out") && i + 1 < argc)
      outFile = argv[++i];
  }

  // Accumulate the full triangle: T[n] = Σ_H T(n,H)
  std::vector<uint64_t> total(maxn + 1, 0);
  // triangle rows for output (if requested)
  std::vector<std::vector<uint64_t>> allRows(maxn + 1);

  for (int H = 1; H <= maxn; ++H) {
    auto row = sweepHeight(H, maxn, fold);
    for (int n = 0; n <= maxn; ++n) {
      total[n] += row[n];
      if (H <= maxn) allRows[H] = row;
    }
  }

  if (foldCheck) {
    // Verify fold == unfold for n <= maxn
    std::vector<uint64_t> totalUnfold(maxn + 1, 0);
    for (int H = 1; H <= maxn; ++H) {
      auto row = sweepHeight(H, maxn, false);
      for (int n = 0; n <= maxn; ++n) totalUnfold[n] += row[n];
    }
    std::vector<uint64_t> totalFold(maxn + 1, 0);
    for (int H = 1; H <= maxn; ++H) {
      auto row = sweepHeight(H, maxn, true);
      for (int n = 0; n <= maxn; ++n) totalFold[n] += row[n];
    }
    bool ok = true;
    for (int n = 1; n <= maxn; ++n) {
      if (totalFold[n] != totalUnfold[n]) {
        std::fprintf(stderr, "FAIL fold!=unfold at n=%d: fold=%llu unfold=%llu\n",
                     n, (unsigned long long)totalFold[n],
                     (unsigned long long)totalUnfold[n]);
        ok = false;
      }
    }
    if (!ok) return 1;
    std::puts("gate_fold PASS");
    return 0;
  }

  // Write triangle if output file requested
  if (outFile) {
    FILE* f = std::fopen(outFile, "w");
    if (!f) { std::perror(outFile); return 1; }
    for (int H = 1; H <= maxn; ++H)
      for (int n = H; n <= maxn; ++n)
        if (allRows[H][n])
          std::fprintf(f, "%d %d %llu\n", n, H, (unsigned long long)allRows[H][n]);
    std::fclose(f);
  }

  // Verify against known a(n)
  bool allOk = true;
  for (int n = 1; n <= std::min(maxn, N_KNOWN); ++n) {
    const bool ok = (total[n] == KNOWN[n]);
    std::printf("n=%2d  a(n)=%llu  known=%llu  %s\n",
                n, (unsigned long long)total[n],
                (unsigned long long)KNOWN[n], ok ? "OK" : "FAIL");
    if (!ok) allOk = false;
  }
  if (!allOk) return 1;
  std::printf("gate_regression PASS (maxn=%d)\n", maxn);
  return 0;
}
