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

// Load known a(n) from an OEIS b-file ("n value" per line, '#'-comment lines
// skipped, e.g. fixtures/b006770.txt). Returns a vector indexed by n (entry 0
// unused); size 1 (no data) if the file is absent or has no numeric rows.
static std::vector<uint64_t> loadKnown(const char* path) {
  std::vector<uint64_t> known(1, 0); // index 0 unused
  FILE* f = std::fopen(path, "r");
  if (!f) return known;
  char line[256];
  while (std::fgets(line, sizeof line, f)) {
    int n; unsigned long long v;
    if (std::sscanf(line, "%d %llu", &n, &v) == 2 && n >= 0) {
      if (n >= static_cast<int>(known.size())) known.resize(n + 1, 0);
      known[n] = v;
    }
  }
  std::fclose(f);
  return known;
}

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

  ShardCfg cfg{.H=H, .maxn=maxn, .fold=fold};
  TriangleRow<W> triangle(H, maxn);

  for (int col = 0; col <= maxn && !frontier.empty(); ++col) {
    // The whole frontier is one shard (in-RAM, no partitioning yet).
    // map_shard drives completion (classify) side and returns successor run.
    frontier = map_shard<W, ClassifyTriangle>(frontier, cfg, triangle);
  }

  return triangle.row; // indexed [0..maxn]
}

// Sweep every height and sum the rows into the triangle total T[n] = Σ_H T(n,H).
// If allRows is non-null, each height's row is stored there for later output.
static std::vector<uint64_t> accumTriangle(
    int maxn, bool fold, std::vector<std::vector<uint64_t>>* allRows = nullptr) {
  std::vector<uint64_t> total(maxn + 1, 0);
  for (int H = 1; H <= maxn; ++H) {
    auto row = sweepHeight(H, maxn, fold);
    for (int n = 0; n <= maxn; ++n) total[n] += row[n];
    if (allRows) (*allRows)[H] = std::move(row);
  }
  return total;
}

int main(int argc, char** argv) {
  int  maxn      = 14;
  bool fold      = false;
  bool foldCheck = false;
  const char* oracleTma = nullptr; // reserved for future oracle-diff mode
  const char* outFile   = nullptr;

  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--maxn") && i + 1 < argc)
      maxn = std::atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--fold"))
      fold = true;
    else if (!std::strcmp(argv[i], "--fold-check"))
      foldCheck = true;
    else if (!std::strcmp(argv[i], "--oracle-tma") && i + 1 < argc)
      oracleTma = argv[++i];
    else if (!std::strcmp(argv[i], "--out") && i + 1 < argc)
      outFile = argv[++i];
  }
  (void)oracleTma;

  if (foldCheck) {
    // Verify fold == unfold byte-identical for all n <= maxn.
    const auto totalUnfold = accumTriangle(maxn, false);
    const auto totalFold   = accumTriangle(maxn, true);
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

  std::vector<std::vector<uint64_t>> allRows(maxn + 1);
  const auto total = accumTriangle(maxn, fold, &allRows);

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

  // Verify against known a(n) from the pinned b-file fixture.
  const auto known = loadKnown("fixtures/b006770.txt");
  const int nKnown = static_cast<int>(known.size()) - 1;
  if (nKnown < 1) {
    std::fprintf(stderr,
                 "FAIL: no known values loaded from fixtures/b006770.txt "
                 "(run from repo root); nothing to verify against\n");
    return 1;
  }
  bool allOk = true;
  for (int n = 1; n <= std::min(maxn, nKnown); ++n) {
    const bool ok = (total[n] == known[n]);
    std::printf("n=%2d  a(n)=%llu  known=%llu  %s\n",
                n, (unsigned long long)total[n],
                (unsigned long long)known[n], ok ? "OK" : "FAIL");
    if (!ok) allOk = false;
  }
  if (!allOk) return 1;
  std::printf("gate_regression PASS (maxn=%d)\n", maxn);
  return 0;
}
