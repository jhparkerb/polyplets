// directed_cone_anchor.cpp -- the "Cone anchor" validation hook of
// results/directed-king-animals.md: filter the fixed king-animal (polyplet)
// enumeration down to DIRECTED king animals and check it against Bacher's
// closed form D(t) = (1/4)((1+t)/sqrt(1-6t+t^2) - 1)  [OEIS A047781].
//
// Purpose: an independent CLOSED-FORM anchor for the enumerate+filter pipeline.
// Two engines live here so they can disagree:
//   full-enumeration modes -- Redelmeier untried-set DFS over ALL fixed king
//     animals (canonical translate: bottom row's leftmost cell at the origin),
//     with an O(cells) reachability filter applied to every animal generated.
//     The mode selects the filter; the unfiltered total is emitted alongside it
//     in every run as a free control (it must be A006770).
//   cone5 -- direct growth inside the forward cone only (no filter). Same
//     Redelmeier machinery, restricted step set, so each directed animal is
//     generated exactly once; much higher reach, and a cross-check on the filter.
//
// Cone conventions (results/directed-king-animals.md, results/king-subfamilies.md):
//   dir5  Bacher: forward cone {W, NW, N, NE, E} = (-1,0)(-1,1)(0,1)(1,1)(1,0),
//         source = leftmost-bottommost cell. Expect A047781 1,4,19,96,501,...
//   dir4  half-plane variant {N, NE, E, SE} = (0,1)(1,0)(1,1)(1,-1),
//         source = bottommost cell of the leftmost column. Expect A055834
//         1,4,18,85,413,2044 -- diverges from dir5 at n=3 (18 vs 19). RED control.
//   dir5nb  RED control: dir5's cone but the bottom-row contiguity requirement
//         waived (BFS seeded from EVERY bottom-row cell). Must NOT match A047781.
//   cone5 direct-growth twin of dir5.
//
// Usage:   build/directed_cone_anchor MODE N [THREADS]
//   MODE in {dir5, dir4, dir5nb, cone5};  THREADS default min(hw, 8).
// stdout: "n total filtered" per line (filter modes; `total` is A006770),
//         "n count" per line (cone5). stderr: obs.h start/heartbeat/done.
// Target machine: local laptop, <=8 cores. Cost: ~n_max in the low teens for
//   the filter modes (work ~ A006770(n) ~ 6.7x/term), ~n=16 for cone5
//   (~5.83x/term). RAM is O(n^2) bytes per thread -- nil. No checkpointing:
//   runs are minutes and restart from scratch; kill = plain SIGINT.
// Driver + closed-form cross-check: experiments/directed_cone_anchor.py
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "obs.h"

namespace {

enum class Mode { Dir5, Dir4, Dir5NoBottom, Cone5 };

// Grid with a one-cell margin on every side so BFS neighbour steps never need a
// bounds check: x in [-N, N] (stride W), y in [-1, N]. Only x in [-(N-1), N-1],
// y in [0, N-1] can ever be occupied, so the margin ring reads as empty.
int N = 0, W = 0, GRID = 0;

inline int idx(int x, int y) { return (y + 1) * W + (x + N); }

// Redelmeier's canonical half-plane: y >= 0, and the bottom row only extends
// east of the origin. Pins each fixed animal to one translate.
inline bool allowed(int x, int y) {
  return y >= 0 && y < N && x > -N && x < N && !(y == 0 && x < 0);
}

// 8 king neighbours (growth), and the forward cones (reachability filter).
const int KDX[8] = {-1, 0, 1, -1, 1, -1, 0, 1};
const int KDY[8] = {-1, -1, -1, 0, 0, 1, 1, 1};
const int C5DX[5] = {-1, -1, 0, 1, 1};  // W, NW, N, NE, E
const int C5DY[5] = {0, 1, 1, 1, 0};
const int C4DX[4] = {0, 1, 1, 1};  // N, E, NE, SE
const int C4DY[4] = {1, 0, 1, -1};

struct Ctx {
  Mode mode;
  int depth, K, IDX;
  uint64_t taskCtr = 0;
  std::vector<uint8_t> seen, occ;
  std::vector<int> untried, cells, queue;
  std::vector<uint32_t> stamp;
  uint32_t gen = 0;
  std::vector<uint64_t> cntAll, cntFilt;
  std::atomic<uint64_t>* progress = nullptr;

  explicit Ctx(Mode m) : mode(m) {
    seen.assign(GRID, 0);
    occ.assign(GRID, 0);
    stamp.assign(GRID, 0);
    untried.assign(8 * (size_t)N + 8, 0);
    cells.assign(N + 1, 0);
    queue.assign(N + 1, 0);
    cntAll.assign(N + 1, 0);
    cntFilt.assign(N + 1, 0);
  }
};

// Flood the occupied set forward from the mode's source(s); directed iff every
// cell is reached. O(size) per call, run on every animal the DFS generates.
bool directed(Ctx& g, int size) {
  const int* dx;
  const int* dy;
  int nd;
  int qn = 0;
  const uint32_t mark = ++g.gen;

  if (g.mode == Mode::Dir4) {
    dx = C4DX;
    dy = C4DY;
    nd = 4;
    // Source = leftmost column, bottommost cell of it.
    int best = g.cells[0], bx = 1 << 30, by = 1 << 30;
    for (int i = 0; i < size; i++) {
      const int c = g.cells[i];
      const int y = c / W - 1, x = c % W - N;
      if (x < bx || (x == bx && y < by)) {
        bx = x;
        by = y;
        best = c;
      }
    }
    g.queue[qn++] = best;
    g.stamp[best] = mark;
  } else {
    dx = C5DX;
    dy = C5DY;
    nd = 5;
    if (g.mode == Mode::Dir5NoBottom) {
      // RED control: every bottom-row cell is a source, so a split bottom row
      // no longer disqualifies the animal.
      for (int i = 0; i < size; i++) {
        const int c = g.cells[i];
        if (c / W - 1 == 0) {
          g.queue[qn++] = c;
          g.stamp[c] = mark;
        }
      }
    } else {
      // Dir5: the canonical translate puts the leftmost-bottommost cell at the
      // origin, so the Bacher source is always idx(0,0).
      const int c = idx(0, 0);
      g.queue[qn++] = c;
      g.stamp[c] = mark;
    }
  }

  for (int h = 0; h < qn; h++) {
    const int c = g.queue[h];
    for (int s = 0; s < nd; s++) {
      const int d = c + dy[s] * W + dx[s];
      if (g.occ[d] && g.stamp[d] != mark) {
        g.stamp[d] = mark;
        g.queue[qn++] = d;
      }
    }
  }
  return qn == size;
}

void rec(Ctx& g, int size, int lo, int hi) {
  for (int i = lo; i < hi; i++) {
    const int c = g.untried[i];
    const int ns = size + 1;

    bool owned;
    if (ns < g.depth) {
      owned = (g.IDX == 0);
    } else if (ns == g.depth) {
      owned = (g.taskCtr++ % (uint64_t)g.K) == (uint64_t)g.IDX;
      if (!owned) continue;
      if (g.progress) g.progress->fetch_add(1, std::memory_order_relaxed);
    } else {
      owned = true;
    }

    g.occ[c] = 1;
    g.cells[size] = c;
    if (owned) {
      g.cntAll[ns]++;
      if (g.mode == Mode::Cone5 || directed(g, ns)) g.cntFilt[ns]++;
    }

    if (ns < N) {
      const int x = c % W - N, y = c / W - 1;
      int newHi = hi;
      if (g.mode == Mode::Cone5) {
        // Direct growth: only forward-cone successors become candidates, and a
        // bottom-row cell may not spawn a westward bottom-row cell (that would
        // unseat the origin as leftmost-bottommost). What is left is exactly the
        // reachable-closed sets whose canonical source is the origin.
        for (int s = 0; s < 5; s++) {
          if (y == 0 && C5DY[s] == 0 && C5DX[s] < 0) continue;
          const int nx = x + C5DX[s], ny = y + C5DY[s];
          if (!allowed(nx, ny)) continue;
          const int d = idx(nx, ny);
          if (!g.seen[d]) {
            g.seen[d] = 1;
            g.untried[newHi++] = d;
          }
        }
      } else {
        for (int s = 0; s < 8; s++) {
          const int nx = x + KDX[s], ny = y + KDY[s];
          if (!allowed(nx, ny)) continue;
          const int d = idx(nx, ny);
          if (!g.seen[d]) {
            g.seen[d] = 1;
            g.untried[newHi++] = d;
          }
        }
      }
      rec(g, ns, i + 1, newHi);
      for (int j = hi; j < newHi; j++) g.seen[g.untried[j]] = 0;
    }
    g.occ[c] = 0;
  }
}

void run_shard(Ctx* g) {
  const int root = idx(0, 0);
  g->seen[root] = 1;
  g->untried[0] = root;
  rec(*g, 0, 0, 1);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 3 || argc > 4) {
    std::fprintf(stderr, "usage: %s {dir5|dir4|dir5nb|cone5} N [THREADS]\n",
                 argv[0]);
    return 2;
  }
  const std::string ms = argv[1];
  Mode mode;
  if (ms == "dir5") mode = Mode::Dir5;
  else if (ms == "dir4") mode = Mode::Dir4;
  else if (ms == "dir5nb") mode = Mode::Dir5NoBottom;
  else if (ms == "cone5") mode = Mode::Cone5;
  else { std::fprintf(stderr, "unknown mode %s\n", argv[1]); return 2; }

  N = std::atoi(argv[2]);
  if (N < 1 || N > 26) { std::fprintf(stderr, "N out of range (1..26)\n"); return 2; }
  W = 2 * N + 1;
  GRID = W * (N + 2);

  int threads = argc == 4 ? std::atoi(argv[3])
                          : (int)std::min(8u, std::max(1u, std::thread::hardware_concurrency()));
  if (threads < 1) threads = 1;
  // Shard on the subtree rooted at each animal of size `depth`; every thread
  // replays the (tiny) prefix above that depth, shard 0 alone counts it.
  int depth = 7;
  if (N <= 8) { threads = 1; depth = N + 1; }

  obs::Reporter rep("directed_cone_anchor",
                    0, "mode=" + ms + " n=" + std::to_string(N) +
                           " threads=" + std::to_string(threads) +
                           " depth=" + std::to_string(depth));

  std::atomic<uint64_t> progress{0};
  std::atomic<int> finished{0};
  std::vector<Ctx*> ctxs;
  for (int t = 0; t < threads; t++) {
    Ctx* g = new Ctx(mode);
    g->depth = depth;
    g->K = threads;
    g->IDX = t;
    g->progress = &progress;
    ctxs.push_back(g);
  }
  std::vector<std::thread> pool;
  for (int t = 0; t < threads; t++)
    pool.emplace_back([&, t] { run_shard(ctxs[t]); finished.fetch_add(1); });

  while (finished.load() < threads) {
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    rep.beat((double)progress.load(), "unit=subtrees");
  }
  for (auto& th : pool) th.join();

  std::vector<uint64_t> total(N + 1, 0), filt(N + 1, 0);
  for (Ctx* g : ctxs) {
    for (int n = 1; n <= N; n++) { total[n] += g->cntAll[n]; filt[n] += g->cntFilt[n]; }
    delete g;
  }
  for (int n = 1; n <= N; n++) {
    if (mode == Mode::Cone5)
      std::printf("%d %llu\n", n, (unsigned long long)filt[n]);
    else
      std::printf("%d %llu %llu\n", n, (unsigned long long)total[n],
                  (unsigned long long)filt[n]);
  }
  rep.done("mode=" + ms + " n=" + std::to_string(N) + " a_n=" +
           std::to_string(filt[N]));
  return 0;
}
