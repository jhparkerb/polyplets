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
#include <vector>
#include <algorithm>
#include <array>

#include "obs.h"  // shared observability/provenance runtime (docs/observability.md)

using u64 = std::uint64_t;

struct Offset { int dx, dy; };

// Offsets ordered by grid-index delta ascending (see kSquare8) so the neighbour
// probes walk memory low-to-high.
static constexpr Offset kSquare4[] = {{0,-1},{-1,0},{1,0},{0,1}};
// Ordered by grid-index delta (dy*gridW+dx) ascending: the 8 status[] probes in
// the neighbour loop then walk memory low-to-high (bottom row, middle row, top
// row), which streams/prefetches better. Order is enumeration-order only; the
// counts are offset-order-independent (gate C confirms split-sum invariance).
static constexpr Offset kSquare8[] = {{-1,-1},{0,-1},{1,-1},{-1,0},
                                      {1,0},{-1,1},{0,1},{1,1}};
static constexpr Offset kTri6[]    = {{0,-1},{1,-1},{-1,0},{1,0},{-1,1},{0,1}};

struct Counter {
  // configuration
  int maxn = 0;
  const Offset* offs = nullptr;
  int deg = 0;
  bool perBox = false;
  int splitS = 0;       // 0 = no splitting
  u64 splitK = 1, splitIdx = 0;

  // grid: x in [-(maxn+1), maxn+1], y in [0, maxn+1], flattened.
  // status[j] != 0 means cell j is unavailable: already in some untried
  // list or placed (the tried-set rule), or outside the allowed region /
  // on the border. Folding all of those into one byte makes the neighbor
  // test a single add + load. A cell's status never changes while it is
  // placed: it was already 1 when it entered an untried list, and the
  // tried-set rule keeps it 1 after unplacement until its adder unwinds.
  // Fixed compile-time grid stride (L3): the neighbour deltas dj[k] = dy*gridW+dx
  // then fold into immediate load offsets instead of being reloaded from the
  // struct and added to j every node (the post-L1 hot spot). A row is 128 bytes
  // = 2 cache lines; the 3-row neighbour stencil stays trivially L1-resident.
  // Holds any maxn with 2*maxn+2 < 128, i.e. maxn <= 62 (binary caps at 40).
  static constexpr int gridW = 128;
  std::vector<char> status;
  std::vector<int> xOf, yOf;          // coordinates of grid index j
  int dj[8] = {0};                    // neighbor deltas in grid-index space

  // Each search level keeps a LOCAL copy of the untried list (fixed-size
  // C-stack buffer, flat memcpy). A fully shared stack is unsound: a child
  // level pops entries it shares with its parent and pushes its own
  // neighbors over those slots, clobbering state the parent still needs.
  static constexpr int kMaxN = 40;                // enforced in main()
  static constexpr int kMaxUntried = kMaxN * 8 + 8;

  // results
  std::vector<u64> bySize;            // [n]
  std::vector<u64> byBox;             // [(n*(maxn+1)+w)*(maxn+1)+h]

  // optional rook/bishop connectivity cross-check (off by default, so the
  // production counting path is byte-for-byte unchanged). For each generated
  // polyplet we test whether it is connected under edge (rook) adjacency and,
  // separately, under corner (bishop) adjacency; both subset counts must equal
  // A001168 (fixed polyominoes) -- rook-connected polyplets ARE polyominoes,
  // and bishop-connected ones are polyominoes in disguise (one colour class:
  // the rook lattice rotated 45 degrees). So rookConn == bishopConn == A001168.
  bool connCheck = false;
  std::vector<u64> rookConn, bishopConn;   // [n]
  std::vector<int> placed;                 // grid indices of placed cells
  std::vector<int> pidx;                   // cell -> index within `placed`
  std::vector<char> inAnimal;              // cell -> currently placed?
  int rookOff[4] = {0}, bishOff[4] = {0};  // neighbour deltas, grid-index space

  // optional (size, edge-perimeter) joint distribution (off by default). Edge
  // perimeter = exposed unit edges = 4*size - (sum of rook adjacencies). Shares
  // the placed/inAnimal machinery above; needs only rookOff.
  bool perimCheck = false;
  std::vector<u64> byPerim;                 // [size*perimStride + perim]
  int perimStride = 0;

  // optional (size, #holes) joint distribution (off by default). A hole is a
  // bounded 4-connected component of empty cells: the complement of an
  // 8-connected (king) foreground is taken 4-connected, by planar duality, so
  // that exactly one of foreground/background "wins" at every diagonal pinch.
  // Shares the inAnimal/rookOff machinery; adds a flood-fill scratch buffer.
  // Flood the empty exterior of the bounding box (expanded by one cell) and
  // count the 4-connected components of empty cells it never reaches.
  bool holesCheck = false;
  bool holes8 = false;                      // background flood 8-connected?
  std::vector<u64> byHoles;                 // [size*holeStride + holes]
  int holeStride = 0;
  std::vector<u64> hseen;                   // per-animal visited stamps
  u64 hstamp = 0;
  std::vector<int> floodStk;               // flood-fill work stack

  // optional (size, site-perimeter) joint distribution (off by default). The site
  // perimeter is the number of distinct EMPTY king-(8-)adjacent cells of the animal
  // -- the percolation perimeter for the king/nnSquare lattice. Cross-SOURCE check
  // vs Mertens 1990 Table IVB (published polynomials), unlike our edge-perimeter.
  bool siteperimCheck = false;
  std::vector<u64> bySiteperim;             // [size*spStride + siteperim]
  int spStride = 0;

  // optional max enclosed empty AREA per size (M(n), off by default). Uses the
  // same exterior-flood machinery as countHoles(), but SUMS the enclosed empty
  // cells (total hole area) instead of counting components, and keeps the running
  // max per size. Across --split workers the global M(n) is the elementwise MAX of
  // the per-worker outputs (max combines that way; counts would sum).
  bool maxHoleCheck = false;
  bool maxHole8 = false;                     // background flood 8-connected?
  std::vector<u64> maxAreaBySize;            // [size] -> max enclosed empty area

  // optional STRATIFIED maxhole (--maxhole-strat, implies maxHoleCheck): M_asym(n) = max
  // hole area among ASYMMETRIC (trivial-D4-stabilizer) animals; M_k(n) = max total hole
  // area over animals with EXACTLY k holes. Reuses the flood/placed machinery.
  bool maxHoleStrat = false;
  std::vector<u64> maxAreaAsym;              // [size] -> max hole area, asymmetric only
  std::vector<u64> maxAreaByK;               // [size*kStride + k] -> max total area, k holes
  int kStride = 0;
  std::vector<int> symX, symY, symTX, symTY; // scratch for the D4 symmetry check

  // optional (size, #diagonal-contacts) distribution (--contacts). A diagonal contact is a
  // king-but-not-rook adjacency: a pair of cells at offset (+-1,+-1). Density test (c=3/4?).
  bool contactsCheck = false;
  std::vector<u64> byContacts;
  int contactStride = 0;
  int diagOff[4] = {0};                      // the 4 diagonal neighbour deltas (grid-index)
  bool needsCells = false;                   // any analysis needing inAnimal/placed (set in init)

  static int findp(int* p, int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }

  // Connected components of the current animal under the given 4 offsets.
  int components(const int* off) {
    int parent[kMaxN + 1];
    for (int i = 0; i < size; ++i) parent[i] = i;
    for (int i = 0; i < size; ++i)
      for (int k = 0; k < 4; ++k) {
        const int nb = placed[i] + off[k];
        if (inAnimal[nb]) {
          const int ri = findp(parent, i), rj = findp(parent, pidx[nb]);
          if (ri != rj) parent[ri] = rj;
        }
      }
    int comps = 0;
    for (int i = 0; i < size; ++i) if (findp(parent, i) == i) ++comps;
    return comps;
  }

  // Number of holes: bounded enclosed empty regions. Flood the empty exterior of
  // the bounding box expanded by one cell (so the outside is one connected
  // region), then count the connected components among the empty cells inside the
  // box that the exterior flood never reached. Background connectivity is
  // 4-connected (--holes, the Jordan dual of the 8-connected king foreground:
  // the topologically consistent choice and the same hole definition OEIS uses
  // for polyominoes in A389193) or 8-connected (--holes8, the same adjacency as
  // the foreground); both are computed and compared.
  int countHoles() {
    ++hstamp;
    const int xlo = minx - 1, xhi = maxx + 1;
    const int ylo = -1, yhi = maxy + 1;        // miny is always 0
    const int bgdeg = holes8 ? 8 : 4;
    static const int BX[8] = {1, -1, 0, 0, 1, 1, -1, -1};
    static const int BY[8] = {0, 0, 1, -1, 1, -1, 1, -1};
    floodStk.clear();
    auto push = [&](int x, int y) {
      const int j = cellIndex(x, y);
      if (hseen[j] != hstamp) { hseen[j] = hstamp; floodStk.push_back(j); }
    };
    auto flood = [&]() {
      while (!floodStk.empty()) {
        const int j = floodStk.back(); floodStk.pop_back();
        const int cx = xOf[j], cy = yOf[j];
        for (int k = 0; k < bgdeg; ++k) {
          const int x = cx + BX[k], y = cy + BY[k];
          if (x < xlo || x > xhi || y < ylo || y > yhi) continue;
          const int nb = cellIndex(x, y);
          if (inAnimal[nb] || hseen[nb] == hstamp) continue;
          hseen[nb] = hstamp; floodStk.push_back(nb);
        }
      }
    };
    // seed the exterior flood from the whole border of the expanded box
    for (int x = xlo; x <= xhi; ++x) { push(x, ylo); push(x, yhi); }
    for (int y = ylo; y <= yhi; ++y) { push(xlo, y); push(xhi, y); }
    flood();
    int holes = 0;
    for (int y = 0; y <= maxy; ++y)
      for (int x = minx; x <= maxx; ++x) {
        const int j = cellIndex(x, y);
        if (inAnimal[j] || hseen[j] == hstamp) continue;
        ++holes;                               // a fresh enclosed region
        hseen[j] = hstamp; floodStk.push_back(j);
        flood();
      }
    return holes;
  }

  // Total enclosed empty AREA for the current animal: same exterior flood as
  // countHoles(), but count every empty cell inside the (expanded) box that the
  // exterior flood never reaches -- i.e. the sum of all hole areas. Background
  // connectivity 4-connected (primary, Jordan dual of the king foreground) or
  // 8-connected (--maxhole8).
  int holeArea() {
    ++hstamp;
    const int xlo = minx - 1, xhi = maxx + 1;
    const int ylo = -1, yhi = maxy + 1;        // miny is always 0
    const int bgdeg = maxHole8 ? 8 : 4;
    static const int BX[8] = {1, -1, 0, 0, 1, 1, -1, -1};
    static const int BY[8] = {0, 0, 1, -1, 1, -1, 1, -1};
    floodStk.clear();
    auto push = [&](int x, int y) {
      const int j = cellIndex(x, y);
      if (hseen[j] != hstamp) { hseen[j] = hstamp; floodStk.push_back(j); }
    };
    for (int x = xlo; x <= xhi; ++x) { push(x, ylo); push(x, yhi); }
    for (int y = ylo; y <= yhi; ++y) { push(xlo, y); push(xhi, y); }
    while (!floodStk.empty()) {
      const int j = floodStk.back(); floodStk.pop_back();
      const int cx = xOf[j], cy = yOf[j];
      for (int k = 0; k < bgdeg; ++k) {
        const int x = cx + BX[k], y = cy + BY[k];
        if (x < xlo || x > xhi || y < ylo || y > yhi) continue;
        const int nb = cellIndex(x, y);
        if (inAnimal[nb] || hseen[nb] == hstamp) continue;
        hseen[nb] = hstamp; floodStk.push_back(nb);
      }
    }
    int area = 0;
    for (int y = 0; y <= maxy; ++y)
      for (int x = minx; x <= maxx; ++x) {
        const int j = cellIndex(x, y);
        if (!inAnimal[j] && hseen[j] != hstamp) ++area;   // enclosed empty cell
      }
    return area;
  }

  // search state
  int size = 0, minx = 0, maxx = 0, maxy = 0;
  u64 splitCtr = 0;

  // Row y=-1 exists in the grid as a blocked border: neighbor lookups are a
  // bare j + dj[k] with no coordinate check, so every cell a delta can reach
  // from a placeable cell must have a real, blocked entry.
  int cellIndex(int x, int y) const { return (y + 1) * gridW + (x + maxn + 1); }

  // Flat index into byBox for an (n-cell, w-wide, h-tall) box. One definition kept
  // in lockstep with the byBox.assign((maxn+1)^3) allocation and every emit site.
  int boxIndex(int n, int w, int h) const { return (n * (maxn + 1) + w) * (maxn + 1) + h; }

  static bool allowed(int x, int y) { return y > 0 || (y == 0 && x >= 0); }

  void init() {
    needsCells = connCheck || perimCheck || holesCheck || maxHoleCheck ||
                 siteperimCheck || contactsCheck;  // (maxHoleStrat rides maxHoleCheck)
    const int gridH = maxn + 3;                  // rows y = -1 .. maxn+1
    const int cells = gridW * gridH;
    status.assign(cells, 0);
    xOf.assign(cells, 0);
    yOf.assign(cells, 0);
    for (int y = -1; y <= maxn + 1; ++y)
      for (int x = -(maxn + 1); x <= maxn + 1; ++x) {
        const int j = cellIndex(x, y);
        xOf[j] = x;
        yOf[j] = y;
        const bool border = (y == -1) || (y == maxn + 1) ||
                            (x == -(maxn + 1)) || (x == maxn + 1);
        if (border || !allowed(x, y)) status[j] = 1;
      }
    for (int k = 0; k < deg; ++k) dj[k] = offs[k].dy * gridW + offs[k].dx;
    bySize.assign(maxn + 1, 0);
    byBox.assign((maxn + 1) * (maxn + 1) * (maxn + 1), 0);
    if (needsCells) {
      inAnimal.assign(cells, 0);
      placed.clear();
      placed.reserve(maxn + 1);
      rookOff[0] = 1; rookOff[1] = -1; rookOff[2] = gridW; rookOff[3] = -gridW;
      diagOff[0] = gridW + 1; diagOff[1] = gridW - 1;
      diagOff[2] = -gridW + 1; diagOff[3] = -gridW - 1;
    }
    if (connCheck) {
      rookConn.assign(maxn + 1, 0);
      bishopConn.assign(maxn + 1, 0);
      pidx.assign(cells, 0);
      bishOff[0] = gridW + 1; bishOff[1] = gridW - 1;
      bishOff[2] = -gridW + 1; bishOff[3] = -gridW - 1;
    }
    if (perimCheck) {
      perimStride = 4 * maxn + 1;
      byPerim.assign((maxn + 1) * perimStride, 0);
    }
    if (holesCheck) {
      holeStride = maxn + 1;                    // #holes <= size <= maxn
      byHoles.assign((maxn + 1) * holeStride, 0);
    }
    if (siteperimCheck) {
      spStride = 8 * maxn + 1;                  // site-perimeter < 8*size
      bySiteperim.assign((maxn + 1) * spStride, 0);
    }
    if (holesCheck || maxHoleCheck || siteperimCheck) {
      hseen.assign(cells, 0);
      hstamp = 0;
      floodStk.reserve(static_cast<size_t>(maxn) * 4 + 16);
    }
    if (maxHoleCheck) {
      maxAreaBySize.assign(maxn + 1, 0);
    }
    if (maxHoleStrat) {
      kStride = maxn + 1;
      maxAreaByK.assign(static_cast<size_t>(maxn + 1) * kStride, 0);
      maxAreaAsym.assign(maxn + 1, 0);
    }
    if (contactsCheck) {
      contactStride = 4 * maxn + 1;            // #diagonal contacts <= 2*size <= 2*maxn
      byContacts.assign(static_cast<size_t>(maxn + 1) * contactStride, 0);
    }
  }

  // True iff the animal has trivial D4 stabilizer (no nontrivial rotation/reflection maps
  // it onto itself up to translation) -- i.e. its free orbit has full size 8.
  // TODO(simplify): this D4 transform table + canon duplicate the affine-transform
  // machinery in cpp/sym/symcount_fast.cpp; a shared D4/affine header would unify them.
  bool isAsymmetric() {
    static const int T[8][4] = {           // (x,y) -> (a*x+b*y, c*x+d*y)
        {1, 0, 0, 1}, {0, -1, 1, 0}, {-1, 0, 0, -1}, {0, 1, -1, 0},
        {-1, 0, 0, 1}, {1, 0, 0, -1}, {0, 1, 1, 0}, {0, -1, -1, 0}};
    symX.resize(size); symY.resize(size);
    for (int i = 0; i < size; ++i) { symX[i] = xOf[placed[i]]; symY[i] = yOf[placed[i]]; }
    auto canon = [&](const std::vector<int>& X, const std::vector<int>& Y) {
      int mnx = X[0], mny = Y[0];
      for (int i = 1; i < size; ++i) {
        if (X[i] < mnx) mnx = X[i];
        if (Y[i] < mny) mny = Y[i];
      }
      std::vector<long long> key(size);
      for (int i = 0; i < size; ++i)
        key[i] = static_cast<long long>(X[i] - mnx) * 256 + (Y[i] - mny);
      std::sort(key.begin(), key.end());
      return key;
    };
    const std::vector<long long> orig = canon(symX, symY);
    symTX.resize(size); symTY.resize(size);
    for (int t = 1; t < 8; ++t) {
      for (int i = 0; i < size; ++i) {
        symTX[i] = T[t][0] * symX[i] + T[t][1] * symY[i];
        symTY[i] = T[t][2] * symX[i] + T[t][3] * symY[i];
      }
      if (canon(symTX, symTY) == orig) return false;   // a nontrivial symmetry fixes it
    }
    return true;
  }

  // Cold path: the optional (size,*) distributions, run once per counted node only
  // when some analysis mode is active. searchT inlines the hot bySize/byBox writes
  // directly; this stays out-of-line (noinline) so it never bloats the kernel. It
  // runs under the NEEDS instantiation, where placed[]/inAnimal[]/box are maintained.
  __attribute__((noinline)) void recordAnalyses() {
    if (connCheck) {
      if (components(rookOff) == 1) rookConn[size] += 1;
      if (components(bishOff) == 1) bishopConn[size] += 1;
    }
    if (perimCheck) {
      int adjsum = 0;
      for (int i = 0; i < size; ++i)
        for (int k = 0; k < 4; ++k)
          if (inAnimal[placed[i] + rookOff[k]]) ++adjsum;
      const int perim = 4 * size - adjsum;       // exposed unit edges
      byPerim[size * perimStride + perim] += 1;
    }
    if (contactsCheck) {
      int diagsum = 0;
      for (int i = 0; i < size; ++i)
        for (int k = 0; k < 4; ++k)
          if (inAnimal[placed[i] + diagOff[k]]) ++diagsum;
      byContacts[static_cast<size_t>(size) * contactStride + diagsum / 2] += 1;  // pair = 2
    }
    if (holesCheck) {
      byHoles[size * holeStride + countHoles()] += 1;
    }
    if (maxHoleCheck) {
      const u64 a = static_cast<u64>(holeArea());
      if (a > maxAreaBySize[size]) maxAreaBySize[size] = a;
    }
    if (siteperimCheck) {
      ++hstamp;                                  // dedup empty neighbours per animal
      int sp = 0;
      for (int i = 0; i < size; ++i)
        for (int k = 0; k < deg; ++k) {          // deg king-neighbour offsets
          const int nb = placed[i] + dj[k];
          if (!inAnimal[nb] && hseen[nb] != hstamp) { hseen[nb] = hstamp; ++sp; }
        }
      bySiteperim[size * spStride + sp] += 1;
    }
    if (maxHoleStrat) {
      // TODO(simplify): holeArea() then countHoles() flood the same animal twice; a
      // combined flood returning (area, #holes) would halve this path's per-record cost.
      // Deferred -- must keep the holes8 vs maxHole8 background-degree choice consistent.
      const u64 area = static_cast<u64>(holeArea());
      if (area > 0) {                          // hole-free animals contribute nothing here
        const int k = countHoles();            // k >= 1
        const size_t kid = static_cast<size_t>(size) * kStride + k;
        if (area > maxAreaByK[kid]) maxAreaByK[kid] = area;
        // the (expensive) D4 check runs ONLY for an animal that would beat the asym
        // record -- short-circuit on area first, so it fires a handful of times per size.
        if (area > maxAreaAsym[size] && isAsymmetric()) maxAreaAsym[size] = area;
      }
    }
  }

  // The hot recursion. The run-constant modes are template parameters, so each
  // instantiation is a straight-line kernel with the dead machinery compiled out:
  //   DEG    - neighbour count (4/6/8) -> the neighbour loop unrolls, dj[] offsets fold
  //   PERBOX - maintain/emit the (w,h) bounding-box histogram
  //   NEEDS  - any per-cell analysis (holes/perim/... needs the cell actually placed)
  //   SPLIT  - subtree partition for --split workers
  // TRACKBOX folds in the fact that the analyses also read minx/maxx/maxy: in pure
  // aggregate mode (no box, no analysis) the box save/update/restore is skipped
  // entirely. run() dispatches to the right instantiation once.
  // Compile-time neighbour deltas in grid-index space, folded from the constexpr
  // offset table and the fixed stride (L3). Used in the kernel so `j + DJ[k]`
  // becomes an immediate load offset instead of a per-node reload+add of dj[].
  // Value-identical to the member dj[] that init() computes for the analysis path.
  template <int DEG>
  static constexpr std::array<int, DEG> kDJ() {
    std::array<int, DEG> d{};
    const Offset* o = (DEG == 4) ? kSquare4 : (DEG == 6) ? kTri6 : kSquare8;
    for (int k = 0; k < DEG; ++k) d[k] = o[k].dy * gridW + o[k].dx;
    return d;
  }

  template <int DEG, bool PERBOX, bool NEEDS, bool SPLIT>
  void searchT(const int* untriedIn, int numUntried) {
    constexpr bool TRACKBOX = PERBOX || NEEDS;
    static constexpr std::array<int, DEG> DJ = kDJ<DEG>();
    int untried[kMaxUntried];
    std::memcpy(untried, untriedIn,
                static_cast<size_t>(numUntried) * sizeof(int));
    // Restrict-qualified raw handles for the hot arrays. status is char*, and char
    // pointers legally alias everything, so without __restrict the compiler must
    // treat every `st[j2]=1` as a possible write to bySize/byBox/xOf/dj and reload
    // them; promising non-aliasing lets those stay in registers across the loop.
    char* __restrict st = status.data();
    u64* __restrict bs = bySize.data();
    [[maybe_unused]] const int* __restrict xo = xOf.data();
    [[maybe_unused]] const int* __restrict yo = yOf.data();
    [[maybe_unused]] u64* __restrict bb = byBox.data();
    while (numUntried > 0) {
      const int j = untried[--numUntried];

      // place the cell (status[j] is already 1; see comment at the field)
      [[maybe_unused]] int sminx = 0, smaxx = 0, smaxy = 0;
      if constexpr (TRACKBOX) {
        sminx = minx; smaxx = maxx; smaxy = maxy;
        const int x = xo[j], y = yo[j];
        if (x < minx) minx = x;
        if (x > maxx) maxx = x;
        if (y > maxy) maxy = y;
      }
      ++size;
      if constexpr (NEEDS) {
        inAnimal[j] = 1; placed.push_back(j);
        if (connCheck) pidx[j] = size - 1;
      }

      // split-mode ownership of this node and its subtree
      bool countIt = true, descend = true;
      if constexpr (SPLIT) {
        if (size < splitS) {
          countIt = (splitIdx == 0);
        } else if (size == splitS) {
          const bool mine = (splitCtr++ % splitK) == splitIdx;
          countIt = mine;
          descend = mine;
        }
      }
      if (countIt) {
        bs[size] += 1;
        if constexpr (PERBOX) {
          const int w = maxx - minx + 1;
          const int h = maxy + 1;                    // miny is always 0
          bb[boxIndex(size, w, h)] += 1;
        }
        if constexpr (NEEDS) recordAnalyses();
      }

      if (descend && size < maxn) {
        // Terminal-parent PURE COUNT: at a size-(maxn-1) node under plain
        // aggregate counting (no per-box coords, no per-cell analysis), every
        // child is a distinct maxn-cell animal and the child count is all we
        // want. The marks/pushes such a node would make are never read (nothing
        // recurses below it; the unmark walk erases them at once), and the DEG
        // probed cells are pairwise distinct, so the child count is just the
        // remaining siblings plus the fresh neighbours = numUntried + (DEG minus
        // the number of already-blocked probed cells). status[] is only ever
        // 0/1, so that is DEG - sum(st over the DEG neighbours): pure loads, no
        // stores, no data branches, no recursion, no unmark. This is 85% of the
        // work at the frontier (a(maxn-1)/Sum a(1..maxn-1)); collapsing it here
        // is the dominant kernel win. The old batch below still handles PERBOX
        // (it needs each child's coordinates) and the split-boundary-at-maxn case.
        bool pureCount = false;
        if constexpr (!PERBOX && !NEEDS) {
          bool canCount = true;
          if constexpr (SPLIT) canCount = (splitS < maxn);
          pureCount = canCount && (size + 1 == maxn);
        }
        if (pureCount) {
          int stale = 0;
          for (int k = 0; k < DEG; ++k) stale += st[j + DJ[k]];
          bs[maxn] += static_cast<u64>(numUntried + DEG - stale);
        } else {
        // Branchless (L2): store each neighbour slot unconditionally, claim it
        // only if the cell was fresh. status[] is 0/1 so `1 - st[j2]` is the
        // claim bit; re-marking an already-1 cell is a no-op, and the unmark walk
        // below touches only claimed slots [numUntried,newCount). The dead store
        // into untried[newCount] for a stale cell needs one slot of slack past the
        // claimed region -- kMaxUntried carries +8.
        static_assert(kMaxUntried >= kMaxN * 8 + 8, "branchless probe slack");
        int newCount = numUntried;
        for (int k = 0; k < DEG; ++k) {
          const int j2 = j + DJ[k];
          const int fresh = 1 - st[j2];
          untried[newCount] = j2;
          newCount += fresh;
          st[j2] = 1;
        }
        // Terminal batch: when the children are the last (size==maxn) level, each of
        // untried[0..newCount) placed as the last cell is a distinct maxn-cell animal.
        // Count them all at once -- no recursion, no per-cell place/unplace. This is
        // the most-visited level, so collapsing it removes the bulk of the child
        // memcpys and terminal bookkeeping. Always sound under !NEEDS (needs the cell
        // placed) except when a --split boundary sits AT the last level: then a
        // terminal cell carries per-cell ownership the batch can't express, so under
        // SPLIT it applies only when the boundary is strictly above maxn.
        bool batched = false;
        if constexpr (!NEEDS) {
          bool canBatch = true;
          if constexpr (SPLIT) canBatch = (splitS < maxn);
          if (canBatch && size + 1 == maxn) {
            bs[maxn] += static_cast<u64>(newCount);
            if constexpr (PERBOX) {
              for (int t = 0; t < newCount; ++t) {
                const int j2 = untried[t];
                const int xx = xo[j2], yy = yo[j2];
                const int w = std::max(xx, maxx) - std::min(xx, minx) + 1;
                const int h = std::max(yy, maxy) + 1;   // miny is always 0
                bb[boxIndex(maxn, w, h)] += 1;
              }
            }
            batched = true;
          }
        }
        if (!batched) searchT<DEG, PERBOX, NEEDS, SPLIT>(untried, newCount);
        // The cells we just marked are exactly untried[numUntried..newCount); the
        // child works on its own memcpy'd copy and never writes through this buffer,
        // so those slots still hold them. Unmark by walking the slots -- no separate
        // reachedUndo stack needed (removing it drops a std::vector push/pop per
        // neighbour from the hot loop).
        for (int t = numUntried; t < newCount; ++t) st[untried[t]] = 0;
        }
      }

      // unplace; (x,y) keeps status 1 so later iterations and deeper
      // levels of this loop never re-add it -- the tried-set rule
      if constexpr (NEEDS) { inAnimal[placed.back()] = 0; placed.pop_back(); }
      --size;
      if constexpr (TRACKBOX) { minx = sminx; maxx = smaxx; maxy = smaxy; }
    }
  }

  // Turn the three run-constant modes into template arguments, one bool at a time,
  // so the compiler generates the (DEG x PERBOX x NEEDS x SPLIT) cross-product and no
  // instantiation can be mis-transcribed by hand. Each layer is a single branch that
  // fans out once at launch. Adding a future flag is one more peel level, not a
  // doubling of hand-aligned lines.
  template <int DEG, bool PERBOX, bool NEEDS>
  void dispatchSplit(const int* origin) {
    if (splitS > 0) searchT<DEG, PERBOX, NEEDS, true>(origin, 1);
    else            searchT<DEG, PERBOX, NEEDS, false>(origin, 1);
  }
  template <int DEG, bool PERBOX>
  void dispatchNeeds(const int* origin) {
    if (needsCells) dispatchSplit<DEG, PERBOX, true>(origin);
    else            dispatchSplit<DEG, PERBOX, false>(origin);
  }
  template <int DEG>
  void dispatchFlags(const int* origin) {
    if (perBox) dispatchNeeds<DEG, true>(origin);
    else        dispatchNeeds<DEG, false>(origin);
  }

  void run() {
    init();
    const int origin = cellIndex(0, 0);
    status[origin] = 1;
    if (deg == 4) dispatchFlags<4>(&origin);
    else if (deg == 6) dispatchFlags<6>(&origin);
    else dispatchFlags<8>(&origin);
  }
};

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr,
        "usage: %s {square4|square8|tri6} MAXN [--per-box] [--rook-bishop] "
        "[--perimeter] [--siteperim] [--holes|--holes8] [--maxhole|--maxhole8] "
        "[--split S K IDX]\n",
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
    } else if (std::strcmp(argv[i], "--rook-bishop") == 0) {
      c.connCheck = true;
    } else if (std::strcmp(argv[i], "--perimeter") == 0) {
      c.perimCheck = true;
    } else if (std::strcmp(argv[i], "--holes") == 0) {
      c.holesCheck = true;
    } else if (std::strcmp(argv[i], "--holes8") == 0) {
      c.holesCheck = true; c.holes8 = true;
    } else if (std::strcmp(argv[i], "--maxhole") == 0) {
      c.maxHoleCheck = true;
    } else if (std::strcmp(argv[i], "--maxhole8") == 0) {
      c.maxHoleCheck = true; c.maxHole8 = true;
    } else if (std::strcmp(argv[i], "--siteperim") == 0) {
      c.siteperimCheck = true;
    } else if (std::strcmp(argv[i], "--maxhole-strat") == 0) {
      c.maxHoleCheck = true; c.maxHoleStrat = true;
    } else if (std::strcmp(argv[i], "--contacts") == 0) {
      c.contactsCheck = true;
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

  // The Redelmeier enumeration is one recursive call with no clean per-unit
  // boundary to heartbeat on; the maxhole_split.py driver provides per-worker
  // progress, so here we frame it with start/done (provenance + wall + cost).
  std::string job = "g2-" + lattice + "-N" + std::to_string(c.maxn);
  std::string extra = "lattice=" + lattice;
  if (c.splitK > 1) {
    job += "-s" + std::to_string(c.splitIdx);
    extra += " split=" + std::to_string(c.splitS) + " k=" +
             std::to_string(c.splitK) + " idx=" + std::to_string(c.splitIdx);
  }
  obs::Reporter rep(job, 0, extra);
  c.run();
  rep.done("result=ok");

  if (c.connCheck) {
    // "n  polyplets  rook-connected  bishop-connected"; last two must both
    // equal A001168 (fixed polyominoes) and each other.
    for (int n = 1; n <= c.maxn; ++n)
      std::printf("%d %llu %llu %llu\n", n,
                  static_cast<unsigned long long>(c.bySize[n]),
                  static_cast<unsigned long long>(c.rookConn[n]),
                  static_cast<unsigned long long>(c.bishopConn[n]));
  } else if (c.perimCheck) {
    // "n  perimeter  count"; sum over perimeter of count[n] == bySize[n].
    for (int n = 1; n <= c.maxn; ++n)
      for (int p = 0; p <= 4 * c.maxn; ++p) {
        const u64 v = c.byPerim[n * c.perimStride + p];
        if (v) std::printf("%d %d %llu\n", n, p,
                           static_cast<unsigned long long>(v));
      }
  } else if (c.holesCheck) {
    // "n  holes  count"; sum over holes of count[n] == bySize[n].
    // The holes=0 row is the hole-free (simply-connected) polyplet sequence.
    for (int n = 1; n <= c.maxn; ++n)
      for (int h = 0; h < c.holeStride; ++h) {
        const u64 v = c.byHoles[n * c.holeStride + h];
        if (v) std::printf("%d %d %llu\n", n, h,
                           static_cast<unsigned long long>(v));
      }
  } else if (c.siteperimCheck) {
    // "n  site-perimeter  count"; site-perim = # distinct empty king-neighbours.
    // Sum over sp == bySize[n]. Cross-check vs Mertens 1990 Table IVB (nnSquare).
    for (int n = 1; n <= c.maxn; ++n)
      for (int p = 0; p < c.spStride; ++p) {
        const u64 v = c.bySiteperim[n * c.spStride + p];
        if (v) std::printf("%d %d %llu\n", n, p,
                           static_cast<unsigned long long>(v));
      }
  } else if (c.contactsCheck) {
    // "n  contacts  count"; sum over contacts of count == bySize[n]. Total diagonal contacts
    // and the per-cell density c (= mean #contacts / n -> ?) follow from this distribution.
    for (int n = 1; n <= c.maxn; ++n)
      for (int d = 0; d < c.contactStride; ++d) {
        const u64 v = c.byContacts[static_cast<size_t>(n) * c.contactStride + d];
        if (v) std::printf("%d %d %llu\n", n, d, static_cast<unsigned long long>(v));
      }
  } else if (c.maxHoleStrat) {
    // "n M(n) M_asym(n) M_1(n) M_2(n) ..."  (M_asym = max hole area over asymmetric
    // animals; M_k = max total hole area over animals with exactly k holes).
    std::printf("# n M(n) M_asym(n) M_1(n) M_2(n) ...\n");
    for (int n = 1; n <= c.maxn; ++n) {
      int kmax = 0;
      for (int k = 1; k < c.kStride; ++k)
        if (c.maxAreaByK[static_cast<size_t>(n) * c.kStride + k]) kmax = k;
      std::printf("%d %llu %llu", n,
                  static_cast<unsigned long long>(c.maxAreaBySize[n]),
                  static_cast<unsigned long long>(c.maxAreaAsym[n]));
      for (int k = 1; k <= kmax; ++k)
        std::printf(" %llu", static_cast<unsigned long long>(
                                 c.maxAreaByK[static_cast<size_t>(n) * c.kStride + k]));
      std::printf("\n");
    }
  } else if (c.maxHoleCheck) {
    // "n  M(n)"; M(n) = max enclosed empty area over all n-cell polyplets.
    // Across --split workers, combine by taking the elementwise MAX (not sum).
    for (int n = 1; n <= c.maxn; ++n)
      std::printf("%d %llu\n", n,
                  static_cast<unsigned long long>(c.maxAreaBySize[n]));
  } else if (c.perBox) {
    for (int n = 1; n <= c.maxn; ++n)
      for (int w = 1; w <= c.maxn; ++w)
        for (int h = 1; h <= c.maxn; ++h) {
          const u64 v = c.byBox[c.boxIndex(n, w, h)];
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
