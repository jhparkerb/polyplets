// redelmeier_polyplet.cpp — Redelmeier enumeration of fixed polyplets
// (king-connected animals), counting by cell count n and bounding-box height H.
//
// A THIRD, fully independent method (explicit backtracking enumeration — not a
// transfer matrix at all) to anchor both the kink kernel and the strip TM. Its
// cost is proportional to the number of objects enumerated, so it reaches only
// modest n; but a single full row n independently pins every T(n,H) for that n,
// including the gap heights H=15..19 (at n=19), validating the exact height-H
// code paths that produce the infeasible n=36 gap cells.
//
// Method (Redelmeier 1981, king-adjacency variant): count each fixed polyplet
// once as the translate whose row-major-minimum cell sits at the origin. Grow
// by an "untried" work-list; each cell enters the list once (REACHED) so it is
// never re-added, giving sibling suppression. minrow = 0 (origin), so
// height = maxrow + 1.
//
// Usage: redelmeier_polyplet <Nmax> [banked_perheight_dir] [ntasks taskid]
//   prints T(n,H) row sums a(n) and, if a banked dir is given, a match count.
//   With ntasks>1, this process counts only the subtrees it owns: every size-
//   SPLIT partial animal is assigned a sequential id (identical order in every
//   process, since all do the same shallow traversal) and owned by id%%ntasks.
//   Sizes < SPLIT are counted by task 0 only. Summing all tasks' T(n,H) columns
//   reproduces the serial run exactly — correct because each recursion node is
//   owned by exactly one task, with no shared state. Emits machine-readable
//   "T n H count" lines to <out.taskid> for summing.

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <sstream>

static int Nmax, W, COL0, ORIGIN;
static std::vector<int8_t> state;   // 0 FREE, 1 OCCUPIED, 2 REACHED
static std::vector<int> untried;
static int top;
static long long Tt[64][64];        // Tt[n][H]
static long long total_enum;        // objects visited (for rate)
static int dxy[8];
static int ntasks = 1, taskid = 0;
static int SPLIT = 8;               // subtree-ownership cut depth (size)
static long long splitctr;          // sequential id of size-SPLIT nodes

enum { FREE = 0, OCCUPIED = 1, REACHED = 2 };

static void grow(int start, int size, int maxrow, bool owned) {
  if (size < SPLIT) {
    if (taskid == 0) { ++Tt[size][maxrow + 1]; ++total_enum; }
  } else if (size == SPLIT) {
    owned = (splitctr++ % ntasks) == taskid;
    if (!owned) return;             // another task owns this whole subtree
    ++Tt[size][maxrow + 1]; ++total_enum;
  } else {
    ++Tt[size][maxrow + 1]; ++total_enum;
  }
  if (size == Nmax) return;
  int k = start;
  while (k < top) {
    int v = untried[k];
    ++k;
    state[v] = OCCUPIED;
    int r = v / W;
    int base = top;
    for (int d = 0; d < 8; ++d) {
      int w = v + dxy[d];
      if (w > ORIGIN && state[w] == FREE) {
        state[w] = REACHED;
        untried[top++] = w;
      }
    }
    grow(k, size + 1, r > maxrow ? r : maxrow, owned);
    while (top > base) { int w = untried[--top]; state[w] = FREE; }
    state[v] = REACHED;  // consumed at this level; ancestor frees it on backtrack
  }
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: redelmeier_polyplet <Nmax> [banked_dir]\n"); return 1; }
  Nmax = std::atoi(argv[1]);
  std::string bankdir = (argc > 2) ? argv[2] : "";
  if (argc > 4) { ntasks = std::atoi(argv[3]); taskid = std::atoi(argv[4]); }
  if (ntasks > 1 && Nmax <= SPLIT) SPLIT = Nmax > 2 ? Nmax - 1 : Nmax;

  // board: rows 0..Nmax+1, cols -(Nmax+1)..(Nmax+1)
  W = 2 * (Nmax + 1) + 1;
  COL0 = Nmax + 1;
  int rows = Nmax + 2;
  state.assign((size_t)rows * W + W, FREE);
  untried.assign((size_t)8 * Nmax + 16, 0);
  ORIGIN = 0 * W + COL0;
  int dr[8] = {-1,-1,-1, 0, 0, 1, 1, 1};
  int dc[8] = {-1, 0, 1,-1, 1,-1, 0, 1};
  for (int d = 0; d < 8; ++d) dxy[d] = dr[d] * W + dc[d];

  auto t0 = std::chrono::steady_clock::now();
  // seed: origin occupied, push its > origin free neighbors
  state[ORIGIN] = OCCUPIED;
  top = 0;
  for (int d = 0; d < 8; ++d) {
    int w = ORIGIN + dxy[d];
    if (w > ORIGIN && state[w] == FREE) { state[w] = REACHED; untried[top++] = w; }
  }
  grow(0, 1, 0, true);
  double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();

  // per-task machine-readable dump for summing across processes
  if (ntasks > 1) {
    std::ostringstream op; op << "results/redelmeier/T_n" << Nmax << ".t" << taskid;
    std::ofstream of(op.str());
    for (int n = 1; n <= Nmax; ++n)
      for (int H = 1; H <= n; ++H)
        if (Tt[n][H]) of << "T " << n << " " << H << " " << Tt[n][H] << "\n";
    std::printf("task %d/%d Nmax=%d done in %.1fs (%.3e obj) -> %s\n",
                taskid, ntasks, Nmax, secs, (double)total_enum, op.str().c_str());
    return 0;
  }

  // row sums
  std::printf("Redelmeier polyplets, Nmax=%d, %.2fs, %.3e objects (%.2e/s)\n",
              Nmax, secs, (double)total_enum, total_enum / secs);
  for (int n = 1; n <= Nmax; ++n) {
    long long a = 0;
    for (int H = 1; H <= n; ++H) a += Tt[n][H];
    std::printf("  a(%2d) = %lld\n", n, a);
  }

  if (!bankdir.empty()) {
    int ok = 0, bad = 0, first_n = -1, first_H = -1;
    long long fg = 0, fe = 0;
    for (int H = 1; H <= Nmax; ++H) {
      std::ostringstream p; p << bankdir << "/h" << H << ".out";
      std::ifstream f(p.str());
      if (!f) continue;
      std::string line;
      while (std::getline(f, line)) {
        std::istringstream is(line);
        long long n; std::string val;
        if (!(is >> n >> val)) continue;
        if (n < 1 || n > Nmax) continue;
        // banked values can exceed int64 at large n; only compare where safe
        if (val.size() > 18) continue;
        long long bv = std::stoll(val);
        if (Tt[n][H] == bv) ++ok;
        else { ++bad; if (first_n < 0) { first_n = (int)n; first_H = H; fg = Tt[n][H]; fe = bv; } }
      }
    }
    std::printf("vs banked triangle: %d match, %d MISMATCH\n", ok, bad);
    if (first_n >= 0)
      std::printf("  first mismatch T(%d,%d): redelmeier=%lld banked=%lld\n", first_n, first_H, fg, fe);
    else
      std::printf("  ALL AGREE (comparable cells, n<=%d)\n", Nmax);
  }
  return 0;
}
