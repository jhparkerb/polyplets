// p3_enum.cc -- Proposer 3's independent fixed king-animal (polyplet)
// enumerator, written from the lattice definition only.
//
// Definition used (my own statement of it, no repo kernel consulted):
//   A fixed polyplet with n cells is a set of n distinct cells of Z^2,
//   connected under KING adjacency -- two cells are adjacent iff their
//   coordinates differ by at most 1 in each axis and they are not equal
//   (8 neighbours) -- counted up to translation only (no rotation or
//   reflection quotient).  Height H = (max row - min row + 1) of the
//   bounding box.
//
// Method: Redelmeier-style recursive enumeration.  Canonical translate:
// the lexicographically smallest cell in (y,x) order sits at the origin,
// so every other cell has y > 0, or y == 0 and x > 0.  Cells reachable
// below/left of the origin are pre-marked forbidden.  Each animal of each
// size 1..N is visited exactly once; height is tracked as max y + 1
// (min y is 0 by canonicalisation).
//
// Output: lines "n H T(n,H)" for n = 1..N, to stdout.
//
// Build:  c++ -O2 -o build/p3_enum experiments/tristruct/p3_enum.cc
// Run:    build/p3_enum        (N = 12 baked; seconds)

#include <cstdio>
#include <cstring>

static const int N = 12;        // max cells
static const int W = 2 * N + 3; // padded width  (x offsets -(N+1)..N+1)
static const int R = N + 3;     // padded rows   (y = -1 .. N+1)

static bool seen[R * W];
static int untried[16 * N * N];
static unsigned long long cnt[N + 1][N + 1]; // cnt[n][H]

static const int NB[8] = {-W - 1, -W, -W + 1, -1, +1, W - 1, W, W + 1};

static void rec(int d, int first, int last, int maxy) {
  for (int i = first; i < last; i++) {
    int c = untried[i];
    int y = c / W - 1;
    int my = y > maxy ? y : maxy;
    cnt[d + 1][my + 1]++;
    if (d + 1 < N) {
      int nl = last;
      int added[8];
      int na = 0;
      for (int k = 0; k < 8; k++) {
        int nb = c + NB[k];
        if (!seen[nb]) {
          seen[nb] = true;
          untried[nl++] = nb;
          added[na++] = nb;
        }
      }
      rec(d + 1, i + 1, nl, my);
      for (int k = 0; k < na; k++)
        seen[added[k]] = false;
    }
  }
}

int main() {
  memset(seen, 0, sizeof seen);
  int x0 = N + 1; // origin column (grid centre)
  // forbid: the y=-1 row, the y=N+1 row, the x borders, and y=0,x<x0
  for (int x = 0; x < W; x++) {
    seen[0 * W + x] = true;
    seen[(R - 1) * W + x] = true;
  }
  for (int y = 0; y < R; y++) {
    seen[y * W + 0] = true;
    seen[y * W + (W - 1)] = true;
  }
  for (int x = 1; x < x0; x++)
    seen[1 * W + x] = true; // y == 0, x < 0 relative to origin
  int origin = 1 * W + x0;
  seen[origin] = true;
  untried[0] = origin;
  rec(0, 0, 1, -1);
  for (int n = 1; n <= N; n++)
    for (int h = 1; h <= n; h++)
      if (cnt[n][h])
        printf("%d %d %llu\n", n, h, cnt[n][h]);
  return 0;
}
