// Perimeter-defect enumerator: fixed animals graded by site-perimeter defect,
// pruned so the cost tracks the (polynomially many) low-defect animals rather
// than the (exponentially many) animals.  docs/perimeter-defect-plan.md, Task B.
//
//   perimeter_defect {square4|square8} NMAX KMAX  ->  lines "n k c H count"
//
// The extra two coordinates are cheap to carry and answer the two questions the
// bare defect census cannot.  c is the cycle rank e - n + 1 of the adjacency
// graph: k = 2c + t - (deg/2 - 2)(n - 1) with t >= 0 (t = sum over empty adjacent
// cells of (animal-neighbours - 1)), i.e. 2c + t on square4 and 2c + t - 2(n-1) on
// square8; the defect budget caps c at floor(k/2) on square4 and floor(k/3) on
// square8 (results/perimeter-defect-diagonals.md), and splitting
// a defect class by c says whether a quasi-polynomial's parity part is carried by
// the cyclic animals -- a ring has an even cell count, so a family that requires
// a cycle can only live on one parity.  H is the bounding-box height, which turns
// the census into a test of inequalities relating n, H and p.
//
// WHY A PRUNED SEARCH IS EXACT.  The defect k := pmax(n) - p, with
// pmax(n) = (deg/2)(n+1) -- 2n+2 on square4, 4n+4 on square8 -- never decreases
// when a cell is added.  Adding a cell v raises pmax by
// deg/2 and changes p by (-1 + g), where g counts v's neighbours that were not
// already perimeter cells.  A cell v adjacent to the animal shares at least
// s(deg) neighbours with whichever animal cell u it touches -- s = 0 on square4,
// s = 2 on square8 (the diagonal case; the orthogonal case shares 4) -- and u is
// itself one of v's neighbours and is not empty.  So g <= deg - 1 - s, giving
//
//     dk = deg/2 - (-1 + g) = deg/2 + 1 - g >= deg/2 + 1 - (deg - 1 - s).
//
// square4: >= 3 - 3 = 0.   square8: >= 5 - 5 = 0.   Non-negative on both, so k
// is monotone along every growth chain, and a Redelmeier DFS that abandons a
// partial animal the moment k > KMAX misses nothing: every animal it would have
// reached already has defect > KMAX.  The bound is TIGHT on both lattices (the
// straight/diagonal stick extends at dk = 0), so this is the sharpest prune
// available, and it is checked at runtime -- see MONOTONE below.
//
// Both the identity and the monotonicity are cross-checked rather than trusted:
// --verify replays the search unpruned and compares every (n, k) cell against
// build/g2's --siteperim census.
//
// The counted objects and the growth discipline are g2's (cpp/g2_redelmeier.cpp):
// each fixed animal is generated exactly once with its scan-minimal cell at the
// origin.  This is a separate binary rather than a g2 flag because the prune
// changes the search itself, not the bookkeeping, and g2's hot kernel is tuned
// for the unpruned frontier.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "obs.h"

using u64 = std::uint64_t;

struct Offset { int dx, dy; };
static constexpr Offset kSquare4[] = {{0,-1},{-1,0},{1,0},{0,1}};
static constexpr Offset kSquare8[] = {{-1,-1},{0,-1},{1,-1},{-1,0},
                                      {1,0},{-1,1},{0,1},{1,1}};

struct Search {
  int maxn = 0, kmax = 0, deg = 0;
  const Offset* offs = nullptr;
  bool prune = true;               // false => unpruned control run (--verify)

  // Deterministic subtree partition, ported from g2's --split (cpp/g2_redelmeier.cpp).
  // Every shard walks the tree identically down to animal size splitS and
  // increments the same counter at that level, so the shards agree on the
  // numbering without communicating; a shard owns -- counts AND descends into --
  // exactly the subtrees whose number is its own mod splitK. Nodes above splitS
  // are counted by shard 0 alone. The elementwise sum over shards must equal the
  // unsplit run, which is what scripts/perimeter_defect_gate.sh checks.
  int splitS = 0;                  // 0 = no splitting
  u64 splitK = 1, splitIdx = 0, splitCtr = 0;

  int gridW = 0, xOrigin = 0, yOrigin = 0;
  std::vector<char> status;        // 1 = never place here (tried/blocked/border)
  std::vector<char> inAnimal;
  std::vector<int> nbr;            // animal-neighbour count of each cell
  int dj[8] = {0};

  int size = 0;
  int perim = 0;                   // |empty cells with nbr > 0|
  int bonds = 0;                   // adjacent pairs inside the animal
  int maxy = 0;                    // miny is always 0, so height = maxy + 1
  std::vector<int> yOf;
  int cmax = 0, hstride = 0;
  std::vector<u64> counts;         // [((n*(kmax+1) + k)*(cmax+1) + c)*hstride + H]
  u64 nodes = 0;
  int minDefectSeen = 1 << 30;
  bool monotoneViolated = false;

  // Site perimeter maxes out at (deg/2)*(n+1): the stick (straight on square4,
  // diagonal on square8).  Asserted at runtime, never assumed -- a violation
  // would silently negate every defect in the table.
  int pmax(int n) const { return (deg / 2) * (n + 1); }
  int defect() const { return pmax(size) - perim; }

  int cellIndex(int x, int y) const { return (y + yOrigin) * gridW + (x + xOrigin); }

  // Redelmeier's canonical half-plane: the scan-minimal cell sits at the origin,
  // so growth is confined to cells at or after it in (y, x) order.
  static bool allowed(int x, int y) { return y > 0 || (y == 0 && x >= 0); }

  void init() {
    // Animal cells live in x in [-(maxn-1), maxn-1], y in [0, maxn-1]; their
    // neighbours reach one further, and the perimeter counts those, so the grid
    // must hold real (not border) entries for them.  One extra ring beyond that
    // is never touched and exists only so a stray index cannot walk off the end.
    xOrigin = maxn + 2;
    yOrigin = 2;
    gridW = 2 * maxn + 5;
    const int gridH = maxn + 4;
    status.assign(static_cast<size_t>(gridW) * gridH, 0);
    inAnimal.assign(status.size(), 0);
    nbr.assign(status.size(), 0);
    for (int y = -2; y <= maxn + 1; ++y)
      for (int x = -(maxn + 2); x <= maxn + 2; ++x) {
        const bool border = (y <= -2) || (y >= maxn + 1) ||
                            (x <= -(maxn + 1)) || (x >= maxn + 1);
        if (border || !allowed(x, y)) status[cellIndex(x, y)] = 1;
      }
    for (int k = 0; k < deg; ++k) dj[k] = offs[k].dy * gridW + offs[k].dx;
    yOf.assign(status.size(), 0);
    for (int y = -2; y <= maxn + 1; ++y)
      for (int x = -(maxn + 2); x <= maxn + 2; ++x) yOf[cellIndex(x, y)] = y;
    cmax = kmax / 2;               // c <= floor(k/2) on square (k = 2c + t), floor(k/3) on king: a cap on both
    hstride = maxn + 1;
    counts.assign(static_cast<size_t>(maxn + 1) * (kmax + 1) * (cmax + 1) * hstride, 0);
  }

  size_t slot(int n, int k, int c, int H) const {
    return ((static_cast<size_t>(n) * (kmax + 1) + k) * (cmax + 1) + c) * hstride + H;
  }

  // Placing a cell: it stops being a perimeter cell (if it was one), and each of
  // its empty neighbours becomes one if it was not already.
  void place(int j) {
    if (nbr[j] > 0) --perim;
    bonds += nbr[j];               // nbr[j] counts j's neighbours already placed
    inAnimal[j] = 1;
    for (int k = 0; k < deg; ++k) {
      const int j2 = j + dj[k];
      if (!inAnimal[j2] && nbr[j2] == 0) ++perim;
      ++nbr[j2];
    }
    ++size;
  }

  void unplace(int j) {
    --size;
    for (int k = 0; k < deg; ++k) {
      const int j2 = j + dj[k];
      --nbr[j2];
      if (!inAnimal[j2] && nbr[j2] == 0) --perim;
    }
    inAnimal[j] = 0;
    bonds -= nbr[j];
    if (nbr[j] > 0) ++perim;
  }

  // What placing cell j would cost.  j is adjacent to the animal (everything in
  // an untried list is), so its own perimeter slot is reclaimed and g fresh ones
  // open up, giving dk = deg/2 + 1 - g.  Crucially g is non-increasing as the
  // animal grows -- a neighbour can only ever become occupied or become an
  // already-counted perimeter cell -- so dk is non-DEcreasing.  A candidate that
  // is over budget now is therefore over budget for the whole subtree and can be
  // dropped from the untried list rather than re-tested at every node.  Without
  // that the list grows like n*deg and the search visits ~150 dead children per
  // live one (measured: 2.4e8 nodes for king n=20, k<=5).
  int deltaK(int j) const {
    int g = 0;
    for (int t = 0; t < deg; ++t) {
      const int j2 = j + dj[t];
      if (!inAnimal[j2] && nbr[j2] == 0) ++g;
    }
    return deg / 2 + 1 - g;
  }

  void search(std::vector<std::vector<int>>& untriedByDepth, int depth,
              int parentDefect) {
    // Worked in place: the child copies out of this level's list into its own,
    // so the parent's remaining entries survive the recursion untouched.
    std::vector<int>& untried = untriedByDepth[depth];
    while (!untried.empty()) {
      const int j = untried.back();
      untried.pop_back();

      const int savedMaxy = maxy;
      place(j);
      if (yOf[j] > maxy) maxy = yOf[j];
      ++nodes;
      const int k = defect();
      if (k < 0) {
        std::fprintf(stderr,
                     "FATAL: site perimeter %d exceeds pmax(%d) = %d -- the "
                     "assumed maximum-perimeter law is wrong\n",
                     perim, size, pmax(size));
        std::exit(3);
      }
      // MONOTONE: the prune's whole correctness rests on this never firing.
      if (k < parentDefect) monotoneViolated = true;
      if (k < minDefectSeen) minDefectSeen = k;

      const bool live = !prune || k <= kmax;

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

      if (countIt && k <= kmax) {
        const int c = bonds - size + 1;
        if (c < 0 || c > cmax) {
          std::fprintf(stderr, "FATAL: cycle rank %d outside [0, %d] at k=%d -- "
                               "the cycle-rank cap from k = 2c + t - (deg/2-2)(n-1) is wrong\n", c, cmax, k);
          std::exit(3);
        }
        counts[slot(size, k, c, maxy + 1)] += 1;
      }

      if (live && descend && size < maxn) {
        std::vector<int>& child = untriedByDepth[depth + 1];
        child.clear();
        const int budget = kmax - k;
        for (const int j2 : untried)
          if (!prune || deltaK(j2) <= budget) child.push_back(j2);
        int fresh[8];
        int added = 0;
        for (int t = 0; t < deg; ++t) {
          const int j2 = j + dj[t];
          if (!status[j2]) {
            status[j2] = 1;
            fresh[added++] = j2;
            if (!prune || deltaK(j2) <= budget) child.push_back(j2);
          }
        }
        search(untriedByDepth, depth + 1, k);
        // Unmark exactly the cells this level added; the tried-set rule keeps
        // everything else at 1 until its own adder unwinds.
        for (int t = 0; t < added; ++t) status[fresh[t]] = 0;
      }
      unplace(j);
      maxy = savedMaxy;
    }
  }

  void run() {
    init();
    std::vector<std::vector<int>> untriedByDepth(maxn + 2);
    const int origin = cellIndex(0, 0);
    status[origin] = 1;
    untriedByDepth[0].assign(1, origin);
    search(untriedByDepth, 0, 0);
  }
};

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr,
                 "usage: %s {square4|square8} NMAX KMAX [--no-prune]\n"
                 "                [--split S K IDX]\n"
                 "  --split: shard the search at animal size S into K parts,\n"
                 "           emit part IDX. Elementwise sum over IDX = unsplit.\n"
                 "  emits \"n k count\" for the site-perimeter defect "
                 "k = (deg/2)(n+1) - p\n",
                 argv[0]);
    return 2;
  }
  Search s;
  const std::string lattice = argv[1];
  if (lattice == "square4")      { s.offs = kSquare4; s.deg = 4; }
  else if (lattice == "square8") { s.offs = kSquare8; s.deg = 8; }
  else { std::fprintf(stderr, "unknown lattice: %s\n", lattice.c_str()); return 2; }
  s.maxn = std::atoi(argv[2]);
  s.kmax = std::atoi(argv[3]);
  for (int i = 4; i < argc; ++i) {
    if (std::strcmp(argv[i], "--no-prune") == 0) s.prune = false;
    else if (std::strcmp(argv[i], "--split") == 0 && i + 3 < argc) {
      s.splitS = std::atoi(argv[i + 1]);
      s.splitK = std::strtoull(argv[i + 2], nullptr, 10);
      s.splitIdx = std::strtoull(argv[i + 3], nullptr, 10);
      i += 3;
      if (s.splitK == 0 || s.splitIdx >= s.splitK || s.splitS < 1) {
        std::fprintf(stderr, "bad --split S K IDX (need S>=1, 0<=IDX<K)\n");
        return 2;
      }
    }
  }
  if (s.maxn < 1 || s.maxn > 400) { std::fprintf(stderr, "NMAX out of range (1..400)\n"); return 2; }
  if (s.kmax < 0 || s.kmax > 40)  { std::fprintf(stderr, "KMAX out of range (0..40)\n"); return 2; }

  const std::string job = "perimdefect-" + lattice + "-N" + std::to_string(s.maxn) +
                          "-K" + std::to_string(s.kmax);
  obs::Reporter rep(job, 0,
                    "lattice=" + lattice + " kmax=" + std::to_string(s.kmax) +
                    (s.prune ? " prune=on" : " prune=off"));
  s.run();

  if (s.monotoneViolated) {
    // The prune is unsound if this ever fires; refuse to emit a table that would
    // look like a census but be missing animals.
    std::fprintf(stderr, "FATAL: defect decreased on a cell addition -- the "
                         "prune is unsound on this lattice\n");
    rep.done("result=fail");
    return 4;
  }
  rep.done("result=ok", "nodes=" + std::to_string(s.nodes) +
                        " min_defect=" + std::to_string(s.minDefectSeen));

  for (int n = 1; n <= s.maxn; ++n)
    for (int k = 0; k <= s.kmax; ++k)
      for (int c = 0; c <= s.cmax; ++c)
        for (int H = 1; H <= s.maxn; ++H) {
          const u64 v = s.counts[s.slot(n, k, c, H)];
          if (v) std::printf("%d %d %d %d %llu\n", n, k, c, H,
                             static_cast<unsigned long long>(v));
        }
  return 0;
}
