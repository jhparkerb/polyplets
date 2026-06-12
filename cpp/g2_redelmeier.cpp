// G2: Redelmeier fixed-animal counter (implementation-plan.md, Layer 1).
//
// Counts fixed lattice animals without duplicates: each animal is generated
// exactly once, translated so that its scan-minimal cell (smallest (y,x)
// lexicographically) sits at the origin. Growth is restricted to cells that
// compare >= origin in that order; the classic untried/tried discipline does
// the rest. Lattice-generic: the neighbor table is the only per-lattice part.
//
// CLI:  g2 LATTICE MAXN [--per-box] [--split S K IDX]
//   aggregate mode: lines "n count"
//   --per-box:      lines "n w h count"   (w,h = bounding box dims)
//   --split S K IDX: deterministic subtree partition at animal size S into K
//       classes; worker IDX counts its classes' subtrees, worker 0 also
//       counts all nodes of size < S. Summing all workers' outputs
//       elementwise must equal the unsplit run (gate check C).
//
// Counts are unsigned 64-bit; safe through ~9e18, far beyond any run this
// binary will be asked to do (polyplet a(22) ~ 5e16).

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using Cell = std::pair<int, int>;

struct Offset { int dx, dy; };

static const Offset kSquare4[] = {{1,0},{-1,0},{0,1},{0,-1}};
static const Offset kSquare8[] = {{1,0},{-1,0},{0,1},{0,-1},
                                  {1,1},{1,-1},{-1,1},{-1,-1}};
static const Offset kTri6[]    = {{1,0},{-1,0},{0,1},{0,-1},{1,-1},{-1,1}};

struct Counter {
  // configuration
  int maxn = 0;
  const Offset* offs = nullptr;
  int deg = 0;
  bool perBox = false;
  int splitS = 0;       // 0 = no splitting
  u64 splitK = 1, splitIdx = 0;

  // grid: x in [-(maxn+1), maxn+1], y in [0, maxn+1], flattened
  int gridW = 0;
  std::vector<char> occupied, reached;

  // results
  std::vector<u64> bySize;            // [n]
  std::vector<u64> byBox;             // [(n*(maxn+1)+w)*(maxn+1)+h]

  // search state
  int size = 0, minx = 0, maxx = 0, maxy = 0;
  u64 splitCtr = 0;

  int cellIndex(int x, int y) const { return y * gridW + (x + maxn + 1); }

  static bool allowed(int x, int y) { return y > 0 || (y == 0 && x >= 0); }

  void init() {
    gridW = 2 * maxn + 3;
    int cells = gridW * (maxn + 2);
    occupied.assign(cells, 0);
    reached.assign(cells, 0);
    bySize.assign(maxn + 1, 0);
    byBox.assign((maxn + 1) * (maxn + 1) * (maxn + 1), 0);
  }

  void record() {
    bySize[size] += 1;
    if (perBox) {
      int w = maxx - minx + 1;
      int h = maxy + 1;                          // miny is always 0
      byBox[(size * (maxn + 1) + w) * (maxn + 1) + h] += 1;
    }
  }

  void search(const std::vector<Cell>& untriedIn) {
    std::vector<Cell> untried = untriedIn;
    while (!untried.empty()) {
      const int x = untried.back().first;
      const int y = untried.back().second;
      untried.pop_back();

      // place the cell
      occupied[cellIndex(x, y)] = 1;
      const int sminx = minx, smaxx = maxx, smaxy = maxy;
      if (x < minx) minx = x;
      if (x > maxx) maxx = x;
      if (y > maxy) maxy = y;
      ++size;

      // split-mode ownership of this node and its subtree
      bool countIt = true, descend = true;
      if (splitS > 0) {
        if (size < splitS) {
          countIt = (splitIdx == 0);
        } else if (size == splitS) {
          const bool mine = (splitCtr++ % splitK) == splitIdx;
          countIt = mine;
          descend = mine;
        }
      }
      if (countIt) record();

      if (descend && size < maxn) {
        std::vector<Cell> next = untried;
        std::vector<int> newlyReached;
        for (int k = 0; k < deg; ++k) {
          const int nx = x + offs[k].dx, ny = y + offs[k].dy;
          if (!allowed(nx, ny)) continue;
          const int j = cellIndex(nx, ny);
          if (occupied[j] || reached[j]) continue;
          reached[j] = 1;
          newlyReached.push_back(j);
          next.push_back({nx, ny});
        }
        search(next);
        for (int j : newlyReached) reached[j] = 0;
      }

      // unplace; (x,y) stays 'reached' so later iterations and deeper
      // levels of this loop never re-add it -- that is the tried-set rule
      --size;
      occupied[cellIndex(x, y)] = 0;
      minx = sminx; maxx = smaxx; maxy = smaxy;
    }
  }

  void run() {
    init();
    reached[cellIndex(0, 0)] = 1;
    search({{0, 0}});
  }
};

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr,
        "usage: %s {square4|square8|tri6} MAXN [--per-box] [--split S K IDX]\n",
        argv[0]);
    return 2;
  }
  Counter c;
  const std::string lattice = argv[1];
  if (lattice == "square4")      { c.offs = kSquare4; c.deg = 4; }
  else if (lattice == "square8") { c.offs = kSquare8; c.deg = 8; }
  else if (lattice == "tri6")    { c.offs = kTri6;    c.deg = 6; }
  else { std::fprintf(stderr, "unknown lattice: %s\n", lattice.c_str()); return 2; }

  c.maxn = std::atoi(argv[2]);
  if (c.maxn < 1 || c.maxn > 40) {
    std::fprintf(stderr, "MAXN out of range (1..40)\n");
    return 2;
  }
  for (int i = 3; i < argc; ++i) {
    if (std::strcmp(argv[i], "--per-box") == 0) {
      c.perBox = true;
    } else if (std::strcmp(argv[i], "--split") == 0 && i + 3 < argc) {
      c.splitS  = std::atoi(argv[i + 1]);
      c.splitK  = std::strtoull(argv[i + 2], nullptr, 10);
      c.splitIdx = std::strtoull(argv[i + 3], nullptr, 10);
      i += 3;
      if (c.splitS < 1 || c.splitK < 1 || c.splitIdx >= c.splitK) {
        std::fprintf(stderr, "bad --split arguments\n");
        return 2;
      }
    } else {
      std::fprintf(stderr, "unknown argument: %s\n", argv[i]);
      return 2;
    }
  }

  c.run();

  if (c.perBox) {
    for (int n = 1; n <= c.maxn; ++n)
      for (int w = 1; w <= c.maxn; ++w)
        for (int h = 1; h <= c.maxn; ++h) {
          const u64 v = c.byBox[(n * (c.maxn + 1) + w) * (c.maxn + 1) + h];
          if (v) std::printf("%d %d %d %llu\n", n, w, h,
                             static_cast<unsigned long long>(v));
        }
  } else {
    for (int n = 1; n <= c.maxn; ++n)
      std::printf("%d %llu\n", n,
                  static_cast<unsigned long long>(c.bySize[n]));
  }
  return 0;
}
