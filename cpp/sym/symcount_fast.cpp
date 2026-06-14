// Fast symmetric-polyplet counter (C++ port of sym/symcount.py).
//
// Counts connected king-move animals invariant under a chosen symmetry type,
// summed over that type's centre/axis placements, by size 1..MAXN. Method
// matches the validated Python: Redelmeier over the ORBIT GRAPH (nodes =
// orbits of cells under the symmetry group), keeping only subsets whose lifted
// cell set is genuinely king-connected, with a per-type anchor pinning any
// residual translation a mirror axis leaves free. See sym/symcount.py and
// docs-s2-symmetric-enumerator.md.
//
// CLI:  symcount_fast {r90|r180|hmirror|dmirror} MAXN   -> "n count" lines.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <algorithm>
#include <string>
#include <vector>

using u64 = std::uint64_t;

struct Aff {              // (x,y) -> (a*x+b*y+c, d*x+e*y+f)
  int a, b, c, d, e, f;
};
static inline void apply(const Aff& t, int x, int y, int& nx, int& ny) {
  nx = t.a * x + t.b * y + t.c;
  ny = t.d * x + t.e * y + t.f;
}

static const Aff ID = {1, 0, 0, 0, 1, 0};

enum class Anchor { None, Xmin0, Diag };

struct Placement {
  std::vector<Aff> group;
};

struct SymType {
  std::vector<Placement> placements;
  Anchor anchor;
};

static SymType makeType(const std::string& name) {
  if (name == "r90")
    return {{{{ID, {0,-1,0, 1,0,0}, {-1,0,0, 0,-1,0}, {0,1,0, -1,0,0}}},
             {{ID, {0,-1,1, 1,0,0}, {-1,0,1, 0,-1,1}, {0,1,0, -1,0,1}}}},
            Anchor::None};
  if (name == "r180")
    return {{{{ID, {-1,0,0, 0,-1,0}}},
             {{ID, {-1,0,1, 0,-1,0}}},
             {{ID, {-1,0,0, 0,-1,1}}},
             {{ID, {-1,0,1, 0,-1,1}}}},
            Anchor::None};
  if (name == "hmirror")
    return {{{{ID, {1,0,0, 0,-1,0}}},
             {{ID, {1,0,0, 0,-1,1}}}},
            Anchor::Xmin0};
  if (name == "dmirror")
    return {{{{ID, {0,1,0, 1,0,0}}}},
            Anchor::Diag};
  std::fprintf(stderr, "unknown symmetry type: %s\n", name.c_str());
  std::exit(2);
}

struct Counter {
  int maxn;
  Anchor anchor;
  int lo, hi, gridW, gridCells;

  std::vector<std::vector<int>> orbitCells;  // cell indices per orbit
  std::vector<int> weight;                    // orbit size
  std::vector<std::vector<int>> adj;          // orbit adjacency

  // search state
  std::vector<char> present;     // cell idx -> in current lift
  std::vector<int> curCells;     // current lift cell indices
  std::vector<char> reached;     // orbit tried-set
  std::vector<int> stamp;        // BFS visited stamp per cell
  int curStamp = 0;
  std::vector<int> bfsStack;     // reused BFS work buffer (no per-node alloc)
  std::vector<u64> counts;

  int cellIdx(int x, int y) const { return (y - lo) * gridW + (x - lo); }
  int cellX(int idx) const { return idx % gridW + lo; }
  int cellY(int idx) const { return idx / gridW + lo; }
  bool inBox(int x, int y) const { return x >= lo && x <= hi && y >= lo && y <= hi; }

  static const int KDX[8], KDY[8];

  void buildOrbits(const std::vector<Aff>& group) {
    orbitCells.clear();
    std::vector<int> cellOrbit(gridCells, -1);
    std::vector<char> seen(gridCells, 0);
    for (int y = lo; y <= hi; ++y) {
      for (int x = lo; x <= hi; ++x) {
        const int id0 = cellIdx(x, y);
        if (seen[id0]) continue;
        std::vector<int> orb;
        bool ok = true;
        for (const Aff& t : group) {
          int nx, ny;
          apply(t, x, y, nx, ny);
          if (!inBox(nx, ny)) { ok = false; }
          else {
            const int j = cellIdx(nx, ny);
            seen[j] = 1;
            bool dup = false;
            for (int c : orb) if (c == j) { dup = true; break; }
            if (!dup) orb.push_back(j);
          }
        }
        seen[id0] = 1;
        if (ok) {
          const int oi = static_cast<int>(orbitCells.size());
          for (int c : orb) cellOrbit[c] = oi;
          orbitCells.push_back(orb);
        }
      }
    }
    const int V = static_cast<int>(orbitCells.size());
    weight.assign(V, 0);
    for (int i = 0; i < V; ++i) weight[i] = static_cast<int>(orbitCells[i].size());
    // adjacency
    adj.assign(V, {});
    std::vector<std::vector<char>> seenEdge;  // dedup via per-orbit marks
    for (int i = 0; i < V; ++i) {
      std::vector<char> mark(V, 0);
      mark[i] = 1;
      for (int c : orbitCells[i]) {
        const int x = cellX(c), y = cellY(c);
        for (int k = 0; k < 8; ++k) {
          const int nx = x + KDX[k], ny = y + KDY[k];
          if (!inBox(nx, ny)) continue;
          const int j = cellOrbit[cellIdx(nx, ny)];
          if (j >= 0 && !mark[j]) { mark[j] = 1; adj[i].push_back(j); }
        }
      }
    }
  }

  bool connectedAndAnchored() {
    const int n = static_cast<int>(curCells.size());
    // anchor
    if (anchor == Anchor::Xmin0) {
      int mn = 1 << 30;
      for (int c : curCells) mn = std::min(mn, cellX(c));
      if (mn != 0) return false;
    } else if (anchor == Anchor::Diag) {
      int mn = 1 << 30;
      for (int c : curCells) mn = std::min(mn, cellX(c) + cellY(c));
      if (mn != 0 && mn != 1) return false;
    }
    // king-connectivity BFS over current lift cells (reused stack buffer)
    ++curStamp;
    bfsStack.clear();
    bfsStack.push_back(curCells[0]);
    stamp[curCells[0]] = curStamp;
    int reachedCnt = 1;
    while (!bfsStack.empty()) {
      const int cur = bfsStack.back(); bfsStack.pop_back();
      const int x = cellX(cur), y = cellY(cur);
      for (int k = 0; k < 8; ++k) {
        const int nx = x + KDX[k], ny = y + KDY[k];
        if (!inBox(nx, ny)) continue;
        const int j = cellIdx(nx, ny);
        if (present[j] && stamp[j] != curStamp) {
          stamp[j] = curStamp; ++reachedCnt; bfsStack.push_back(j);
        }
      }
    }
    return reachedCnt == n;
  }

  void addOrbit(int v) {
    for (int c : orbitCells[v]) { present[c] = 1; curCells.push_back(c); }
  }
  void removeOrbit(int v) {
    for (size_t k = 0; k < orbitCells[v].size(); ++k) {
      present[curCells.back()] = 0; curCells.pop_back();
    }
  }

  void search(int root, std::vector<int> untried, int w) {
    if (connectedAndAnchored()) counts[w] += 1;
    while (!untried.empty()) {
      const int v = untried.back(); untried.pop_back();
      const int nw = w + weight[v];
      if (nw <= maxn) {
        std::vector<int> next = untried;
        std::vector<int> newly;
        for (int u : adj[v]) {
          if (u > root && !reached[u]) {
            reached[u] = 1; newly.push_back(u); next.push_back(u);
          }
        }
        addOrbit(v);
        search(root, std::move(next), nw);
        removeOrbit(v);
        for (int u : newly) reached[u] = 0;
      }
    }
  }

  void runPlacement(const std::vector<Aff>& group) {
    buildOrbits(group);
    const int V = static_cast<int>(orbitCells.size());
    present.assign(gridCells, 0);
    stamp.assign(gridCells, 0);
    reached.assign(V, 0);
    curStamp = 0;
    curCells.clear();
    for (int r = 0; r < V; ++r) {
      if (weight[r] > maxn) continue;
      for (int i = 0; i < V; ++i) reached[i] = 0;
      reached[r] = 1;
      addOrbit(r);
      std::vector<int> untried;
      for (int u : adj[r]) {
        if (u > r && !reached[u]) { reached[u] = 1; untried.push_back(u); }
      }
      search(r, std::move(untried), weight[r]);
      removeOrbit(r);
    }
  }
};

const int Counter::KDX[8] = {1, 1, 1, 0, 0, -1, -1, -1};
const int Counter::KDY[8] = {1, 0, -1, 1, -1, 1, 0, -1};

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr, "usage: %s {r90|r180|hmirror|dmirror} MAXN\n", argv[0]);
    return 2;
  }
  SymType type = makeType(argv[1]);
  const int maxn = std::atoi(argv[2]);
  if (maxn < 1 || maxn > 30) { std::fprintf(stderr, "MAXN out of range\n"); return 2; }

  Counter c;
  c.maxn = maxn;
  c.anchor = type.anchor;
  const int R = maxn + 2;
  c.lo = -(R + 1);
  c.hi = R + 1;
  c.gridW = c.hi - c.lo + 1;
  c.gridCells = c.gridW * c.gridW;
  c.counts.assign(maxn + 1, 0);

  for (const Placement& p : type.placements) c.runPlacement(p.group);

  for (int n = 1; n <= maxn; ++n)
    if (c.counts[n])
      std::printf("%d %llu\n", n, static_cast<unsigned long long>(c.counts[n]));
  return 0;
}
