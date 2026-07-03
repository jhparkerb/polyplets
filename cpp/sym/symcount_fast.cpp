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
#include <algorithm>
#include <string>
#include <vector>

#include "../obs.h"  // shared observability/provenance runtime (docs/observability.md)

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
  std::vector<int> list;         // shared untried pool (no per-node alloc): a
                                 // node owns list[start..end); its children
                                 // append new neighbours past end, so each
                                 // child's untried range stays contiguous.
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
    // adjacency (per-orbit mark vector dedups neighbours; V is small and this
    // runs once per placement, not in the search hot path)
    adj.assign(V, {});
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

  // Allocation-free Redelmeier over the shared `list` pool. This node owns the
  // untried range list[start..end); it tries each candidate forward, appending
  // a candidate's newly-reached neighbours past the current end so the child's
  // untried range list[i+1..newEnd) is a single contiguous slice — no per-node
  // vector copy (the old `next = untried` + `newly` was ~3 heap allocs/node).
  // On backtrack the appended tail is unmarked and truncated. Forward vs the
  // old LIFO order changes traversal, not the multiset of animals counted.
  void search(int root, int start, int w) {
    if (connectedAndAnchored()) counts[w] += 1;
    const int end = static_cast<int>(list.size());
    for (int i = start; i < end; ++i) {
      const int v = list[i];
      const int nw = w + weight[v];
      if (nw > maxn) continue;
      for (int u : adj[v]) {
        if (u > root && !reached[u]) { reached[u] = 1; list.push_back(u); }
      }
      addOrbit(v);
      search(root, i + 1, nw);
      removeOrbit(v);
      for (int k = end; k < static_cast<int>(list.size()); ++k) reached[list[k]] = 0;
      list.resize(end);
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
    list.clear();
    list.reserve(V);
    for (int r = 0; r < V; ++r) {
      if (weight[r] > maxn) continue;
      for (int i = 0; i < V; ++i) reached[i] = 0;
      reached[r] = 1;
      addOrbit(r);
      list.clear();
      for (int u : adj[r]) {
        if (u > r && !reached[u]) { reached[u] = 1; list.push_back(u); }
      }
      search(r, 0, weight[r]);
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

  obs::Reporter rep("symcount-" + std::string(argv[1]) + "-N" +
                        std::to_string(maxn),
                    static_cast<double>(type.placements.size()),
                    "type=" + std::string(argv[1]));
  int pi = 0;
  for (const Placement& p : type.placements) {
    c.runPlacement(p.group);
    ++pi;
    rep.beat(pi, "placement=" + std::to_string(pi));
  }

  for (int n = 1; n <= maxn; ++n)
    if (c.counts[n])
      std::printf("%d %llu\n", n, static_cast<unsigned long long>(c.counts[n]));
  rep.done("result=ok");
  return 0;
}
