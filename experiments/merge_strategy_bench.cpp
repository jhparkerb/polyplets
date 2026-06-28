// merge_strategy_bench.cpp — compare fix options for the merge fan-in.
//
// Models the real merge: N sorted input runs with OVERLAPPING key ranges (the
// map outputs), total T records, merged into M key-ranges (the merge workers).
// Four strategies, measuring heap-pops (work) and wall in the page-cache regime
// (the current merge regime: data resident, so heap CPU dominates):
//
//   A current    : per range, k-way merge all N runs FROM THE START, skipping
//                  records below klo (mergeRunFiles today) -> ~M/2 x T pops.
//   B seek-index : per range, binary-search a sparse per-run index to klo, then
//                  k-way merge only [klo,khi) -> ~T pops, but M separate heaps
//                  and N*M index seeks.
//   C bucketed   : runs pre-split into M buckets at write time (the shuffle);
//                  per range, k-way merge the N bucket-j slices -> ~T pops, no
//                  index, small per-range heaps.
//   D one-pass   : a SINGLE k-way merge of all N runs in one streaming pass,
//                  emitting range boundaries as it goes -> exactly T pops, one
//                  heap, N opens (then a trivial slice).
//
// Usage: merge_strategy_bench [T_RECORDS] [N_RUNS] [M_RANGES] [INDEX_STRIDE]
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <queue>
#include <random>
#include <vector>

using u64 = uint64_t;
using clk = std::chrono::steady_clock;
static double secs(clk::time_point a) { return std::chrono::duration<double>(clk::now() - a).count(); }

struct Cursor { u64 key; int run; size_t idx; bool operator>(const Cursor& o) const { return key > o.key; } };
using Heap = std::priority_queue<Cursor, std::vector<Cursor>, std::greater<Cursor>>;

int main(int argc, char** argv) {
  size_t T = argc > 1 ? strtoull(argv[1], nullptr, 10) : 2'000'000; // total records
  int N    = argc > 2 ? atoi(argv[2]) : 128;   // input runs (map outputs)
  int M    = argc > 3 ? atoi(argv[3]) : 128;   // merge ranges (cores*mult)
  int STR  = argc > 4 ? atoi(argv[4]) : 512;   // sparse-index stride

  // N sorted runs, overlapping: assign each of T sorted keys to a random run.
  std::mt19937_64 rng(7);
  std::vector<u64> all(T);
  for (auto& k : all) k = rng();
  std::sort(all.begin(), all.end());
  std::vector<std::vector<u64>> run(N);          // each stays sorted
  for (u64 k : all) run[rng() % N].push_back(k);

  // M range cuts over the u64 keyspace.
  std::vector<u64> cut(M + 1);
  for (int j = 0; j <= M; j++) cut[j] = j == M ? UINT64_MAX : (u64)((__uint128_t)j * UINT64_MAX / M);

  auto report = [&](const char* name, size_t pops, double t, size_t kept) {
    printf("%-12s pops=%-11zu (%.1fx T)  time=%.3fs  kept=%zu %s\n",
           name, pops, (double)pops / T, t, kept, kept == T ? "" : "  <-- MISMATCH");
  };

  // === A: per range, merge all runs from the start, skip below klo ===
  { size_t pops = 0, kept = 0; auto t = clk::now();
    for (int j = 0; j < M; j++) {
      Heap h; for (int r = 0; r < N; r++) if (!run[r].empty()) h.push({run[r][0], r, 0});
      while (!h.empty()) {
        Cursor c = h.top(); h.pop(); pops++;
        if (c.idx + 1 < run[c.run].size()) h.push({run[c.run][c.idx + 1], c.run, c.idx + 1});
        if (c.key < cut[j]) continue;        // skip prefix
        if (c.key >= cut[j + 1]) break;       // done with this range
        kept++;
      }
    }
    report("A current", pops, secs(t), kept); }

  // --- sparse per-run index: key at every STR-th position ---
  std::vector<std::vector<std::pair<u64, size_t>>> idx(N);
  for (int r = 0; r < N; r++) for (size_t i = 0; i < run[r].size(); i += STR) idx[r].push_back({run[r][i], i});

  // === B: seek each run to klo via its index, then merge only [klo,khi) ===
  { size_t pops = 0, kept = 0; auto t = clk::now();
    for (int j = 0; j < M; j++) {
      Heap h;
      for (int r = 0; r < N; r++) {
        // last index entry with key <= cut[j]
        auto& ix = idx[r]; if (ix.empty()) continue;
        int a = 0, b = (int)ix.size() - 1, s = 0;
        while (a <= b) { int m = (a + b) / 2; if (ix[m].first <= cut[j]) { s = m; a = m + 1; } else b = m - 1; }
        size_t p = ix[s].second;
        if (p < run[r].size()) h.push({run[r][p], r, p});
      }
      while (!h.empty()) {
        Cursor c = h.top(); h.pop(); pops++;
        if (c.idx + 1 < run[c.run].size()) h.push({run[c.run][c.idx + 1], c.run, c.idx + 1});
        if (c.key < cut[j]) continue;        // tiny in-block skip
        if (c.key >= cut[j + 1]) break;
        kept++;
      }
    }
    report("B seek-index", pops, secs(t), kept); }

  // === C: runs pre-bucketed by range; merge the N bucket-j slices per range ===
  // Precompute, per run, the bucket boundary offsets (cost paid once, at "write").
  std::vector<std::vector<size_t>> bnd(N, std::vector<size_t>(M + 1, 0));
  for (int r = 0; r < N; r++) { size_t p = 0; for (int j = 0; j <= M; j++) { while (p < run[r].size() && run[r][p] < cut[j]) p++; bnd[r][j] = p; } }
  { size_t pops = 0, kept = 0; auto t = clk::now();
    for (int j = 0; j < M; j++) {
      Heap h;
      for (int r = 0; r < N; r++) { size_t p = bnd[r][j]; if (p < bnd[r][j + 1]) h.push({run[r][p], r, p}); }
      while (!h.empty()) {
        Cursor c = h.top(); h.pop(); pops++;
        size_t nx = c.idx + 1;
        if (nx < bnd[c.run][j + 1]) h.push({run[c.run][nx], c.run, nx});
        kept++;
      }
    }
    report("C bucketed", pops, secs(t), kept); }

  // === D: one streaming N-way merge, slice into ranges as keys cross cuts ===
  { size_t pops = 0, kept = 0; auto t = clk::now();
    Heap h; for (int r = 0; r < N; r++) if (!run[r].empty()) h.push({run[r][0], r, 0});
    while (!h.empty()) {
      Cursor c = h.top(); h.pop(); pops++;
      if (c.idx + 1 < run[c.run].size()) h.push({run[c.run][c.idx + 1], c.run, c.idx + 1});
      kept++;                                 // every record emitted once, in order
    }
    report("D one-pass", pops, secs(t), kept); }

  printf("(T=%zu records, N=%d runs, M=%d ranges; page-cache regime, heap-bound)\n", T, N, M);
  return 0;
}
