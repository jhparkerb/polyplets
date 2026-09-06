// directed_cone_anchor.cpp -- the "Cone anchor" validation hook of
// results/subclasses.md: filter the fixed king-animal (polyplet)
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
// Cone conventions (results/subclasses.md, results/subclasses.md):
//   dir5  Bacher: forward cone {W, NW, N, NE, E} = (-1,0)(-1,1)(0,1)(1,1)(1,0),
//         source = leftmost-bottommost cell. Expect A047781 1,4,19,96,501,...
//   dir4  half-plane variant {N, NE, E, SE} = (0,1)(1,0)(1,1)(1,-1),
//         source = bottommost cell of the leftmost column. Expect A055834
//         1,4,18,85,413,2044 -- diverges from dir5 at n=3 (18 vs 19). RED control.
//   dir5nb  RED control: dir5's cone but the bottom-row contiguity requirement
//         waived (BFS seeded from EVERY bottom-row cell). Must NOT match A047781.
//         This is "control B"; it is NOT Bacher's multi-directed class -- see
//         mdir below and results/subclasses.md.
//   cone5 direct-growth twin of dir5.
//   mdir  Bacher's MULTI-DIRECTED animals, Definition 2 of arXiv:1301.1365,
//         evaluated directly on every animal generated. Sources are the local
//         minima of the column-bottom profile b(x) (not just the global bottom
//         row); keystones are its local maxima, and each keystone must be
//         reachable from a source on either side. Expect 1,4,20,110,636,3790,...
//         cross-checked against the generating function M = D/(1-B) of the
//         paper's Theorem 8 (experiments/multidirected_king.py).
//   mdirbad  RED control for mdir: Definition 2's keystone condition dropped,
//         leaving only "every cell reachable from some local-minimum source".
//         A strict superset; must NOT reproduce the mdir counts.
//   grid  results/subclasses.md Phase 0: a single Redelmeier pass over
//         ALL fixed king animals (unfiltered growth, like dir5/dir4/dir5nb),
//         tallying all 20 (directedness x convexity) cells at once instead of
//         one filter. Directedness: none, dir5, dir4, ctrlB (= dir5nb's
//         predicate -- a class of its own, incomparable with mdir's, NOT a
//         stand-in for it; results/subclasses.md), mdir (Bacher's
//         Definition 2 -- the fifth row Phase 3 added, since Phase 1c settled
//         that ctrlB could not stand in for it). Convexity: none, column-convex,
//         HV-convex, staircase (column-convex + nondecreasing column bottoms
//         AND tops, left to right).
//   gridbad  RED control for grid's staircase predicate: monotonicity checked
//         on column bottoms only, tops dropped. Must NOT reproduce A225114.
//   gridperim  results/subclasses.md Phase 2a: the SAME
//         Redelmeier pass, reusing reach(Dir4) and convexity() verbatim (no
//         new predicate code), but bucketed by SEMIPERIMETER s = W+H (the
//         bounding box) instead of by area n -- the brute-force validator for
//         cpp/convex_perim_tm.cpp's new dir4 mode. Two populations: HV-convex
//         alone, and HV-convex AND dir4. Coverage caveat: an area-<=N
//         enumeration settles s completely only up to s such that
//         floor(s/2)*ceil(s/2) <= N (an animal of semiperimeter s can have
//         area up to ~s^2/4); larger s in the output are LOWER bounds, not
//         exact counts.
//
// Phase 4a of results/subclasses.md: grid/gridbad's pass
// already generates every fixed king animal of every size <= N, so a per-n
// MIN-REDUCE of the site perimeter rides for free (no new search). Site
// perimeter = the number of distinct EMPTY cells adjacent to the animal.
// Convention pinned from cpp/g2_redelmeier.cpp's `--siteperim` (its own
// header comment): KING (8-)adjacency -- "the percolation perimeter for the
// king/nnSquare lattice", cross-checked there against Mertens 1990 Table IVB.
// That is what the two new trailing columns' first value is (minSPKing).
// The second (minSPRook) is a deliberately WRONG adjacency -- orthogonal
// (rook, 4-)adjacency -- kept as a RED control: a k*k solid block has king
// site-perimeter 4k+4 (Minkowski sum with the 3x3 king ball is a (k+2)x(k+2)
// square, minus the k^2 occupied cells) but rook site-perimeter 4k (one
// exposed cell per border cell per side, corners do not merge as they do
// under king adjacency), so the two columns MUST diverge at every k*k size.
//
// Usage:   build/directed_cone_anchor MODE N [THREADS]
//   MODE in {dir5, dir4, dir5nb, cone5, grid, gridbad, mdir, mdirbad,
//   gridperim}; THREADS default min(hw, 8).
// stdout: "n total filtered" per line (filter modes; `total` is A006770),
//         "n count" per line (cone5),
//         "n c[none,none] c[none,col] c[none,hv] c[none,stair] c[dir5,none] ...
//          c[mdir,stair] minSPKing minSPRook" per line (grid/gridbad: the 20
//          directedness x convexity counts as before, dir-major then
//          conv-minor ([none,dir5,dir4,ctrlB,mdir] x
//          [none,col-convex,HV-convex,staircase]), then the two site-perimeter
//          minima over ALL n-cell king animals -- unrestricted by
//          directedness or convexity, i.e. the population c[none,none] counts),
//         "s hv hvdir4" per line (gridperim: s = W+H, 2..N+1; hv = count of
//          HV-convex animals of that box, hvdir4 = the dir4-filtered subset).
// stderr: obs.h start/heartbeat/done.
// Target machine: local laptop, <=8 cores. Cost: ~n_max in the low teens for
//   the filter modes (work ~ A006770(n) ~ 6.7x/term), ~n=16 for cone5
//   (~5.83x/term). RAM is O(n^2) bytes per thread -- nil. No checkpointing:
//   runs are minutes and restart from scratch; kill = plain SIGINT.
// Driver + closed-form cross-check: experiments/directed_cone_anchor.py
#include <algorithm>
#include <atomic>
#include <chrono>
#include <climits>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

#include "argparse.h"
#include "obs.h"

namespace {

enum class Mode { Dir5, Dir4, Dir5NoBottom, Cone5, Grid, GridBadStaircase,
                  MultiDir, MultiDirNoKeystone, GridPerim };

// Grid with a one-cell margin on every side so BFS neighbor steps never need a
// bounds check: x in [-N, N] (stride W), y in [-1, N]. Only x in [-(N-1), N-1],
// y in [0, N-1] can ever be occupied, so the margin ring reads as empty.
int N = 0, W = 0, GRID = 0;

inline int idx(int x, int y) { return (y + 1) * W + (x + N); }

// Redelmeier's canonical half-plane: y >= 0, and the bottom row only extends
// east of the origin. Pins each fixed animal to one translate.
inline bool allowed(int x, int y) {
  return y >= 0 && y < N && x > -N && x < N && !(y == 0 && x < 0);
}

// 8 king neighbors (growth), and the forward cones (reachability filter).
const int KDX[8] = {-1, 0, 1, -1, 1, -1, 0, 1};
const int KDY[8] = {-1, -1, -1, 0, 0, 1, 1, 1};
const int C5DX[5] = {-1, -1, 0, 1, 1};  // W, NW, N, NE, E
const int C5DY[5] = {0, 1, 1, 1, 0};
const int C4DX[4] = {0, 1, 1, 1};  // N, E, NE, SE
const int C4DY[4] = {1, 0, 1, -1};
const int RDX[4] = {0, 0, -1, 1};  // rook (orthogonal) neighbors -- Phase 4a
const int RDY[4] = {-1, 1, 0, 0};  // RED control for site-perimeter adjacency

struct Ctx {
  Mode mode;
  int depth, K, IDX;
  uint64_t taskCtr = 0;
  std::vector<uint8_t> seen, occ;
  std::vector<int> untried, cells, queue;
  std::vector<uint32_t> stamp;
  uint32_t gen = 0;
  std::vector<uint64_t> cntAll, cntFilt;
  // Grid-mode scratch: per-column and per-row run bounds, generation-stamped
  // so each is checked in O(size) rather than reset in O(N) per animal.
  std::vector<int> colMin, colMax, colCount, rowMin, rowMax, rowCount;
  std::vector<uint32_t> colStamp, rowStamp;
  uint32_t colGen = 0, rowGen = 0;
  // cnt[dir][conv][n]: dir in {none, dir5, dir4, ctrlB, mdir}, conv in
  // {none, column-convex, HV-convex, staircase} -- the plan's grid, with the
  // multi-directed row Phase 3 added.
  std::vector<uint64_t> cnt[5][4];
  // Phase 4a: per-n minimum site perimeter over ALL n-cell king animals
  // (unrestricted -- the same population as cnt[0][0]). King is the pinned
  // convention; Rook is the RED control. Sentinel UINT64_MAX means "no
  // animal of this size seen by this shard yet".
  std::vector<uint64_t> minSPKing, minSPRook;
  // Phase 2a (results/subclasses.md): per-semiperimeter
  // (s = W+H, 0..2N+1 to be safe) tallies for gridperim mode.
  std::vector<uint64_t> perimHV, perimHVDir4;
  // mdir scratch: source/keystone marks over the grid, the keystone list, and a
  // second BFS queue (the keystone walks run inside the condition-(1) flood).
  std::vector<uint32_t> srcMark, keyMark;
  uint32_t srcGen = 0, keyGen = 0;
  std::vector<int> keyList, queue2;
  std::atomic<uint64_t>* progress = nullptr;

  explicit Ctx(Mode m) : mode(m) {
    seen.assign(GRID, 0);
    occ.assign(GRID, 0);
    stamp.assign(GRID, 0);
    untried.assign(8 * (size_t)N + 8, 0);
    cells.assign(N + 1, 0);
    queue.assign(N + 1, 0);
    queue2.assign(N + 1, 0);
    srcMark.assign(GRID, 0);
    keyMark.assign(GRID, 0);
    keyList.reserve(N + 1);
    cntAll.assign(N + 1, 0);
    cntFilt.assign(N + 1, 0);
    colMin.assign(W, 0);
    colMax.assign(W, 0);
    colCount.assign(W, 0);
    colStamp.assign(W, 0);
    rowMin.assign(N, 0);
    rowMax.assign(N, 0);
    rowCount.assign(N, 0);
    rowStamp.assign(N, 0);
    for (int d = 0; d < 5; d++)
      for (int c = 0; c < 4; c++) cnt[d][c].assign(N + 1, 0);
    minSPKing.assign(N + 1, UINT64_MAX);
    minSPRook.assign(N + 1, UINT64_MAX);
    perimHV.assign(2 * N + 2, 0);
    perimHVDir4.assign(2 * N + 2, 0);
  }
};

// Advance a generation stamp. Every marker array here is stamped rather than
// cleared per animal; a deep run burns billions of generations, so wrap has to
// zero the array or a stale mark could pass for the current one.
inline uint32_t bump(uint32_t& gen, std::vector<uint32_t>& marks) {
  if (++gen == 0) {
    std::fill(marks.begin(), marks.end(), 0u);
    gen = 1;
  }
  return gen;
}

// The three cone predicates, factored out of what used to be a mode-dispatched
// directed() so grid mode can evaluate all three on the same animal.
enum class ConeKind { Dir5, Dir4, Dir5NoBottom };

inline ConeKind coneKindOf(Mode m) {
  return m == Mode::Dir4 ? ConeKind::Dir4
       : m == Mode::Dir5NoBottom ? ConeKind::Dir5NoBottom
       : ConeKind::Dir5;
}

// Flood the occupied set forward from the cone's source(s); directed iff every
// cell is reached. O(size) per call, run on every animal the DFS generates.
bool reach(Ctx& g, int size, ConeKind kind) {
  const int* dx;
  const int* dy;
  int nd;
  int qn = 0;
  const uint32_t mark = bump(g.gen, g.stamp);

  if (kind == ConeKind::Dir4) {
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
    if (kind == ConeKind::Dir5NoBottom) {
      // RED control / ctrlB: every bottom-row cell is a source, so a split
      // bottom row no longer disqualifies the animal.
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

// Bacher, arXiv:1301.1365, Definition 2 (multi-directed animals). Let b(x) be
// the ordinate of the bottommost cell in column x, and +inf where the column is
// empty (king-connectivity makes the occupied columns an interval, so the only
// +inf values are the two sentinels past the ends). A SOURCE is the cell
// (x, b(x)) at a strict local minimum of b, a KEYSTONE the cell at a strict
// local maximum; where consecutive columns tie, the leftmost takes the mark.
// Sentinels at +inf make the extrema alternate source, keystone, ..., source.
// The animal is multi-directed iff
//   (1) every cell is forward-reachable (5-cone, inside the animal) from some
//       source -- note "some source", not the global-bottom-row source of dir5;
//   (2) every keystone t is reachable from a source strictly left of it AND
//       from one strictly right of it, along paths that pass through no other
//       keystone at t's own height.
// Directed animals have one source and no keystone, so dir5 subset mdir.
// checkKeystones=false drops (2): mdirbad's RED control.
bool multiDirected(Ctx& g, int size, bool checkKeystones) {
  // --- column bottoms b(x) -------------------------------------------------
  const uint32_t cmark = bump(g.colGen, g.colStamp);
  int xlo = INT_MAX, xhi = INT_MIN;
  for (int i = 0; i < size; i++) {
    const int c = g.cells[i];
    const int cx = c % W, y = c / W - 1;
    if (g.colStamp[cx] != cmark) {
      g.colStamp[cx] = cmark;
      g.colMin[cx] = y;
    } else if (y < g.colMin[cx]) {
      g.colMin[cx] = y;
    }
    if (cx < xlo) xlo = cx;
    if (cx > xhi) xhi = cx;
  }

  // --- sources and keystones, and the seed set for condition (1) ----------
  const uint32_t smark = bump(g.srcGen, g.srcMark);
  const uint32_t kmark = bump(g.keyGen, g.keyMark);
  const uint32_t rmark = bump(g.gen, g.stamp);
  g.keyList.clear();
  int qn = 0;
  for (int cx = xlo; cx <= xhi;) {
    const int v = g.colMin[cx];
    int cj = cx;
    while (cj < xhi && g.colMin[cj + 1] == v) cj++;   // maximal plateau [cx, cj]
    const bool lowerLeft = cx > xlo && g.colMin[cx - 1] < v;
    const bool lowerRight = cj < xhi && g.colMin[cj + 1] < v;
    const int c = cx + (v + 1) * W;                   // = idx(cx - N, v)
    if (!lowerLeft && !lowerRight) {                  // strict local minimum
      g.srcMark[c] = smark;
      g.stamp[c] = rmark;
      g.queue[qn++] = c;
    } else if (lowerLeft && lowerRight) {             // strict local maximum
      g.keyMark[c] = kmark;
      g.keyList.push_back(c);
    }
    cx = cj + 1;
  }

  // --- condition (1): forward flood from all sources at once --------------
  for (int h = 0; h < qn; h++) {
    const int c = g.queue[h];
    for (int s = 0; s < 5; s++) {
      const int d = c + C5DY[s] * W + C5DX[s];
      if (g.occ[d] && g.stamp[d] != rmark) {
        g.stamp[d] = rmark;
        g.queue[qn++] = d;
      }
    }
  }
  if (qn != size) return false;
  if (!checkKeystones) return true;

  // --- condition (2): walk backwards out of each keystone -----------------
  for (size_t ki = 0; ki < g.keyList.size(); ki++) {
    const int t = g.keyList[ki];
    const int tx = t % W, ty = t / W - 1;
    const uint32_t bmark = bump(g.gen, g.stamp);
    g.stamp[t] = bmark;
    g.queue2[0] = t;
    int bn = 1;
    bool left = false, right = false;
    for (int h = 0; h < bn && !(left && right); h++) {
      const int c = g.queue2[h];
      for (int s = 0; s < 5; s++) {
        const int d = c - C5DY[s] * W - C5DX[s];      // reversed cone
        if (!g.occ[d] || g.stamp[d] == bmark) continue;
        if (g.keyMark[d] == kmark && d / W - 1 == ty) continue;  // blocked
        g.stamp[d] = bmark;
        g.queue2[bn++] = d;
        if (g.srcMark[d] == smark) {
          if (d % W < tx) left = true;
          else if (d % W > tx) right = true;
        }
      }
    }
    if (!(left && right)) return false;
  }
  return true;
}

inline bool passes(Ctx& g, int size) {
  if (g.mode == Mode::MultiDir) return multiDirected(g, size, true);
  if (g.mode == Mode::MultiDirNoKeystone) return multiDirected(g, size, false);
  return reach(g, size, coneKindOf(g.mode));
}

struct ConvexResult { bool colConvex, hvConvex, staircase; };

// Column-convex: every occupied column's y-extent is gap-free. HV-convex adds
// the same for rows. Staircase adds nondecreasing column bottoms AND tops,
// left to right (checkTops=false drops the tops half -- gridbad's RED control,
// see the file header). Both column and row bounds are generation-stamped
// (colGen/rowGen) so this is O(size), not O(size + grid width).
ConvexResult convexity(Ctx& g, int size, bool checkTops) {
  const uint32_t cmark = bump(g.colGen, g.colStamp);
  const uint32_t rmark = bump(g.rowGen, g.rowStamp);

  for (int i = 0; i < size; i++) {
    const int c = g.cells[i];
    const int x = c % W - N, y = c / W - 1;
    const int cx = x + N;
    if (g.colStamp[cx] != cmark) {
      g.colStamp[cx] = cmark;
      g.colMin[cx] = g.colMax[cx] = y;
      g.colCount[cx] = 1;
    } else {
      if (y < g.colMin[cx]) g.colMin[cx] = y;
      if (y > g.colMax[cx]) g.colMax[cx] = y;
      g.colCount[cx]++;
    }
    if (g.rowStamp[y] != rmark) {
      g.rowStamp[y] = rmark;
      g.rowMin[y] = g.rowMax[y] = x;
      g.rowCount[y] = 1;
    } else {
      if (x < g.rowMin[y]) g.rowMin[y] = x;
      if (x > g.rowMax[y]) g.rowMax[y] = x;
      g.rowCount[y]++;
    }
  }

  bool colConvex = true, rowConvex = true, monotone = true;
  int lastBottom = INT_MIN, lastTop = INT_MIN;
  for (int cx = 0; cx < W; cx++) {  // cx increasing <=> x increasing
    if (g.colStamp[cx] != cmark) continue;
    if (g.colMax[cx] - g.colMin[cx] + 1 != g.colCount[cx]) colConvex = false;
    if (g.colMin[cx] < lastBottom || (checkTops && g.colMax[cx] < lastTop))
      monotone = false;
    lastBottom = g.colMin[cx];
    lastTop = g.colMax[cx];
  }
  for (int y = 0; y < N; y++) {
    if (g.rowStamp[y] != rmark) continue;
    if (g.rowMax[y] - g.rowMin[y] + 1 != g.rowCount[y]) rowConvex = false;
  }
  return {colConvex, colConvex && rowConvex, colConvex && monotone};
}

// Phase 4a: number of distinct EMPTY cells king- (king=true) or rook-
// (king=false) adjacent to the animal. O(size) per call via the same
// generation-stamp trick as reach()/multiDirected() -- margin is exactly one
// cell wide on every side of the grid (file header), so every neighbor
// offset from an occupied cell is in bounds without a check.
int sitePerim(Ctx& g, int size, bool king) {
  const uint32_t mark = bump(g.gen, g.stamp);
  const int* dx = king ? KDX : RDX;
  const int* dy = king ? KDY : RDY;
  const int nd = king ? 8 : 4;
  int sp = 0;
  for (int i = 0; i < size; i++) {
    const int c = g.cells[i];
    for (int s = 0; s < nd; s++) {
      const int d = c + dy[s] * W + dx[s];
      if (!g.occ[d] && g.stamp[d] != mark) {
        g.stamp[d] = mark;
        sp++;
      }
    }
  }
  return sp;
}

// Phase 0 of results/subclasses.md: tally all 16 (directedness x
// convexity) cells for one animal in a single pass. checkTops=false is
// gridbad's deliberately-wrong staircase predicate (RED control). Phase 4a
// rides the same pass: every animal here is unconditionally counted in the
// (none,none) population, so the site-perimeter min-reduce runs on every one.
void gridTally(Ctx& g, int size, bool checkTops) {
  const bool dirFlags[5] = {
      true,
      reach(g, size, ConeKind::Dir5),
      reach(g, size, ConeKind::Dir4),
      reach(g, size, ConeKind::Dir5NoBottom),
      multiDirected(g, size, true),
  };
  // multiDirected() and convexity() both scribble on colMin/colStamp, so the
  // convexity pass has to come after the directedness ones, not before.
  // TODO: the shared scratch pool costs a redundant O(size) column-bottom scan
  // per animal (measured ~5% of a `grid 11 1` run) and leaves this ordering
  // constraint enforced by comment alone -- reordering these two calls compiles
  // and returns wrong counts. The fix is one profile() pass filling colMin /
  // colMax / colCount that both predicates read, plus private stamp arrays for
  // reach()/sitePerim(). Deliberately NOT done in a cleanup pass: this is the
  // hot loop behind the banked `grid 14 8` table.
  const ConvexResult cv = convexity(g, size, checkTops);
  const bool convFlags[4] = {true, cv.colConvex, cv.hvConvex, cv.staircase};
  for (int d = 0; d < 5; d++) {
    if (!dirFlags[d]) continue;
    for (int c = 0; c < 4; c++)
      if (convFlags[c]) g.cnt[d][c][size]++;
  }
  const uint64_t spK = (uint64_t)sitePerim(g, size, true);
  if (spK < g.minSPKing[size]) g.minSPKing[size] = spK;
  const uint64_t spR = (uint64_t)sitePerim(g, size, false);
  if (spR < g.minSPRook[size]) g.minSPRook[size] = spR;
}

// Phase 2a (results/subclasses.md): the brute-force validator
// for cpp/convex_perim_tm.cpp's dir4 mode. Reuses reach(Dir4) and convexity()
// verbatim -- no new predicate, only a new bucketing key. HV-convex is
// checkTops=true (row AND column contiguity); non-HV-convex animals don't
// have a well-defined semiperimeter-by-box distinct from other shapes of the
// same box, and dir4 is only proved (Proposition 2) on column-convex/HV
// animals, so this mode only tallies the HV-convex population.
void gridPerimTally(Ctx& g, int size) {
  const ConvexResult cv = convexity(g, size, /*checkTops=*/true);
  if (!cv.hvConvex) return;
  int xlo = INT_MAX, xhi = INT_MIN, ylo = INT_MAX, yhi = INT_MIN;
  for (int i = 0; i < size; i++) {
    const int c = g.cells[i];
    const int x = c % W - N, y = c / W - 1;
    if (x < xlo) xlo = x;
    if (x > xhi) xhi = x;
    if (y < ylo) ylo = y;
    if (y > yhi) yhi = y;
  }
  const int s = (xhi - xlo + 1) + (yhi - ylo + 1);
  g.perimHV[s]++;
  // reach() needs convexity()'s stamp/colMin scratch untouched by anything
  // else in between -- it uses its own gen/stamp, disjoint from colGen/
  // colStamp, so calling it after convexity() here is safe (same ordering
  // gridTally already relies on, just the other way round).
  if (reach(g, size, ConeKind::Dir4)) g.perimHVDir4[s]++;
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
      if (g.mode == Mode::Grid || g.mode == Mode::GridBadStaircase) {
        gridTally(g, ns, g.mode == Mode::Grid);
      } else if (g.mode == Mode::GridPerim) {
        gridPerimTally(g, ns);
      } else {
        g.cntAll[ns]++;
        if (g.mode == Mode::Cone5 || passes(g, ns)) g.cntFilt[ns]++;
      }
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
    std::fprintf(stderr,
                 "usage: %s {dir5|dir4|dir5nb|cone5|grid|gridbad|mdir|mdirbad|"
                 "gridperim} N [THREADS]\n",
                 argv[0]);
    return 2;
  }
  const std::string ms = argv[1];
  Mode mode;
  if (ms == "dir5") mode = Mode::Dir5;
  else if (ms == "dir4") mode = Mode::Dir4;
  else if (ms == "dir5nb") mode = Mode::Dir5NoBottom;
  else if (ms == "cone5") mode = Mode::Cone5;
  else if (ms == "grid") mode = Mode::Grid;
  else if (ms == "gridbad") mode = Mode::GridBadStaircase;
  else if (ms == "mdir") mode = Mode::MultiDir;
  else if (ms == "mdirbad") mode = Mode::MultiDirNoKeystone;
  else if (ms == "gridperim") mode = Mode::GridPerim;
  else { std::fprintf(stderr, "unknown mode %s\n", argv[1]); return 2; }

  N = (int)argparse::ArgInt(argv[2], "N", 1, 26);
  W = 2 * N + 1;
  GRID = W * (N + 2);

  int threads = argc == 4
      ? (int)argparse::ArgInt(argv[3], "THREADS", 1, 1024)
      : (int)std::min(8u, std::max(1u, std::thread::hardware_concurrency()));
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

  const bool isGrid = mode == Mode::Grid || mode == Mode::GridBadStaircase;
  const bool isGridPerim = mode == Mode::GridPerim;
  std::vector<uint64_t> total(N + 1, 0), filt(N + 1, 0);
  std::vector<uint64_t> agg[5][4];
  for (int d = 0; d < 5; d++)
    for (int c = 0; c < 4; c++) agg[d][c].assign(N + 1, 0);
  std::vector<uint64_t> minSPK(N + 1, UINT64_MAX), minSPR(N + 1, UINT64_MAX);
  std::vector<uint64_t> perimHV(2 * N + 2, 0), perimHVDir4(2 * N + 2, 0);
  for (Ctx* g : ctxs) {
    for (int n = 1; n <= N; n++) {
      total[n] += g->cntAll[n];
      filt[n] += g->cntFilt[n];
      if (isGrid) {
        for (int d = 0; d < 5; d++)
          for (int c = 0; c < 4; c++) agg[d][c][n] += g->cnt[d][c][n];
        if (g->minSPKing[n] < minSPK[n]) minSPK[n] = g->minSPKing[n];
        if (g->minSPRook[n] < minSPR[n]) minSPR[n] = g->minSPRook[n];
      }
    }
    if (isGridPerim) {
      for (int s = 0; s < (int)perimHV.size(); s++) {
        perimHV[s] += g->perimHV[s];
        perimHVDir4[s] += g->perimHVDir4[s];
      }
    }
    delete g;
  }
  for (int n = 1; n <= N; n++) {
    if (mode == Mode::Cone5) {
      std::printf("%d %llu\n", n, (unsigned long long)filt[n]);
    } else if (isGrid) {
      std::printf("%d", n);
      for (int d = 0; d < 5; d++)
        for (int c = 0; c < 4; c++)
          std::printf(" %llu", (unsigned long long)agg[d][c][n]);
      std::printf(" %llu %llu\n", (unsigned long long)minSPK[n],
                  (unsigned long long)minSPR[n]);
    } else if (!isGridPerim) {
      std::printf("%d %llu %llu\n", n, (unsigned long long)total[n],
                  (unsigned long long)filt[n]);
    }
  }
  if (isGridPerim) {
    for (int s = 2; s <= N + 1; s++)
      std::printf("%d %llu %llu\n", s, (unsigned long long)perimHV[s],
                  (unsigned long long)perimHVDir4[s]);
  }
  const uint64_t doneVal =
      isGridPerim ? perimHVDir4[N + 1] : (isGrid ? agg[0][0][N] : filt[N]);
  rep.done("mode=" + ms + " n=" + std::to_string(N) + " a_n=" +
           std::to_string(doneVal));
  return 0;
}
