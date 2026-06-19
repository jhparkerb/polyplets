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

using u64 = std::uint64_t;

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

  // grid: x in [-(maxn+1), maxn+1], y in [0, maxn+1], flattened.
  // status[j] != 0 means cell j is unavailable: already in some untried
  // list or placed (the tried-set rule), or outside the allowed region /
  // on the border. Folding all of those into one byte makes the neighbor
  // test a single add + load. A cell's status never changes while it is
  // placed: it was already 1 when it entered an untried list, and the
  // tried-set rule keeps it 1 after unplacement until its adder unwinds.
  int gridW = 0;
  std::vector<char> status;
  std::vector<int> xOf, yOf;          // coordinates of grid index j
  int dj[8] = {0};                    // neighbor deltas in grid-index space

  // Each search level keeps a LOCAL copy of the untried list (fixed-size
  // C-stack buffer, flat memcpy). A fully shared stack is unsound: a child
  // level pops entries it shares with its parent and pushes its own
  // neighbors over those slots, clobbering state the parent still needs.
  static constexpr int kMaxN = 40;                // enforced in main()
  static constexpr int kMaxUntried = kMaxN * 8 + 8;
  std::vector<int> reachedUndo;       // cells to unmark on unwind

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

  // optional max enclosed empty AREA per size (M(n), off by default). Uses the
  // same exterior-flood machinery as countHoles(), but SUMS the enclosed empty
  // cells (total hole area) instead of counting components, and keeps the running
  // max per size. Across --split workers the global M(n) is the elementwise MAX of
  // the per-worker outputs (max combines that way; counts would sum).
  bool maxHoleCheck = false;
  bool maxHole8 = false;                     // background flood 8-connected?
  std::vector<u64> maxAreaBySize;            // [size] -> max enclosed empty area

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

  static bool allowed(int x, int y) { return y > 0 || (y == 0 && x >= 0); }

  void init() {
    gridW = 2 * maxn + 3;
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
    reachedUndo.clear();
    reachedUndo.reserve(static_cast<size_t>(maxn) * deg + 8);
    bySize.assign(maxn + 1, 0);
    byBox.assign((maxn + 1) * (maxn + 1) * (maxn + 1), 0);
    if (connCheck || perimCheck || holesCheck || maxHoleCheck) {
      inAnimal.assign(cells, 0);
      placed.clear();
      placed.reserve(maxn + 1);
      rookOff[0] = 1; rookOff[1] = -1; rookOff[2] = gridW; rookOff[3] = -gridW;
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
    if (holesCheck || maxHoleCheck) {
      hseen.assign(cells, 0);
      hstamp = 0;
      floodStk.reserve(static_cast<size_t>(maxn) * 4 + 16);
    }
    if (maxHoleCheck) {
      maxAreaBySize.assign(maxn + 1, 0);
    }
  }

  void record() {
    bySize[size] += 1;
    if (perBox) {
      int w = maxx - minx + 1;
      int h = maxy + 1;                          // miny is always 0
      byBox[(size * (maxn + 1) + w) * (maxn + 1) + h] += 1;
    }
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
    if (holesCheck) {
      byHoles[size * holeStride + countHoles()] += 1;
    }
    if (maxHoleCheck) {
      const u64 a = static_cast<u64>(holeArea());
      if (a > maxAreaBySize[size]) maxAreaBySize[size] = a;
    }
  }

  void search(const int* untriedIn, int numUntried) {
    int untried[kMaxUntried];
    std::memcpy(untried, untriedIn,
                static_cast<size_t>(numUntried) * sizeof(int));
    while (numUntried > 0) {
      const int j = untried[--numUntried];

      // place the cell (status[j] is already 1; see comment at the field)
      const int sminx = minx, smaxx = maxx, smaxy = maxy;
      const int x = xOf[j], y = yOf[j];
      if (x < minx) minx = x;
      if (x > maxx) maxx = x;
      if (y > maxy) maxy = y;
      ++size;
      if (connCheck || perimCheck || holesCheck || maxHoleCheck) {
        inAnimal[j] = 1; placed.push_back(j);
        if (connCheck) pidx[j] = size - 1;
      }

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
        int newCount = numUntried;
        const size_t undoMark = reachedUndo.size();
        for (int k = 0; k < deg; ++k) {
          const int j2 = j + dj[k];
          if (!status[j2]) {
            status[j2] = 1;
            untried[newCount++] = j2;
            reachedUndo.push_back(j2);
          }
        }
        search(untried, newCount);
        while (reachedUndo.size() > undoMark) {
          status[reachedUndo.back()] = 0;
          reachedUndo.pop_back();
        }
      }

      // unplace; (x,y) keeps status 1 so later iterations and deeper
      // levels of this loop never re-add it -- the tried-set rule
      if (connCheck || perimCheck || holesCheck || maxHoleCheck) { inAnimal[placed.back()] = 0; placed.pop_back(); }
      --size;
      minx = sminx; maxx = smaxx; maxy = smaxy;
    }
  }

  void run() {
    init();
    const int origin = cellIndex(0, 0);
    status[origin] = 1;
    search(&origin, 1);
  }
};

int main(int argc, char** argv) {
  if (argc < 3) {
    std::fprintf(stderr,
        "usage: %s {square4|square8|tri6} MAXN [--per-box] [--rook-bishop] "
        "[--perimeter] [--holes|--holes8] [--maxhole|--maxhole8] "
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
