// directed_halfplane.cpp -- count half-plane directed king animals:
// n-cell subsets of Z^2 containing the origin such that every cell is
// reachable from the origin by steps (0,1), (1,0), (1,1), (1,-1) without
// leaving the set. Redelmeier untried-set DFS (each animal generated exactly
// once; every generated set is reachable-closed by construction).
// Claimed identification: this equals OEIS A055834 (results/king-subfamilies.md).
//
// Usage: directed_halfplane N   -> prints a(1)..a(N), one per line.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

static int N, W;                 // W = 2N-1 (y stride)
static std::vector<uint8_t> seen;
static std::vector<int> untried;
static std::vector<uint64_t> cnt;

// x in [0, N), y in [-(N-1), N-1]; all steps have dx >= 0 so x >= 0 always.
static inline int idx(int x, int y) { return x * W + (y + N - 1); }

static const int DX[4] = {0, 1, 1, 1};
static const int DY[4] = {1, 0, 1, -1};

static void rec(int size, int lo, int hi) {
  for (int i = lo; i < hi; i++) {
    int c = untried[i];
    cnt[size + 1]++;
    if (size + 1 < N) {
      int x = c / W, y = c % W - (N - 1);
      int newHi = hi;
      for (int s = 0; s < 4; s++) {
        int nx = x + DX[s], ny = y + DY[s];
        if (nx >= N || ny >= N - 1 + 1 || ny < -(N - 1)) continue;
        int d = idx(nx, ny);
        if (!seen[d]) {
          seen[d] = 1;
          untried[newHi++] = d;
        }
      }
      rec(size + 1, i + 1, newHi);
      for (int j = hi; j < newHi; j++) seen[untried[j]] = 0;
    }
  }
}

int main(int argc, char** argv) {
  if (argc != 2) { std::fprintf(stderr, "usage: %s N\n", argv[0]); return 2; }
  N = std::atoi(argv[1]);
  if (N < 1 || N > 30) { std::fprintf(stderr, "N out of range\n"); return 2; }
  W = 2 * N - 1;
  seen.assign((size_t)N * W, 0);
  // untried never exceeds 4 cells added per occupied cell + 1 root
  untried.assign(4 * (size_t)N + 1, 0);
  cnt.assign(N + 1, 0);
  int root = idx(0, 0);
  seen[root] = 1;
  untried[0] = root;
  rec(0, 0, 1);
  for (int n = 1; n <= N; n++) std::printf("%d %llu\n", n, (unsigned long long)cnt[n]);
  return 0;
}
