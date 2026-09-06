// Fast symmetric-polyplet counter (C++ port of scripts/symcount.py).
//
// Counts connected king-move animals invariant under a chosen symmetry type,
// summed over that type's centre/axis placements, by size 1..MAXN. Method
// matches the validated Python: Redelmeier over the ORBIT GRAPH (nodes =
// orbits of cells under the symmetry group), keeping only subsets whose lifted
// cell set is genuinely king-connected, with a per-type anchor pinning any
// residual translation a mirror axis leaves free. See scripts/symcount.py and
// docs-s2-symmetric-enumerator.md.
//
// CLI:  symcount_fast {r90|r180|hmirror|dmirror|c4|d2ax|d2diag|d4} MAXN
//                                                        -> "n count" lines.
//
// The first four are per-ELEMENT fixed-point counts Fix(g) (what Burnside
// needs). The last four are per-SUBGROUP invariant counts I(H) (what the
// orbit-SIZE distribution, hence a(n) mod 4, needs) -- a different object:
// I(D2ax) is fixed by BOTH axis mirrors, whereas hmirror is Fix(h).

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <atomic>
#include <mutex>
#include <string>
#include <thread>
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
  // --- SUBGROUP-invariant types (see scripts/symcount.py). Each subgroup below
  // has a centre, so every placement pins translation and no anchor applies.
  // c4 is r90's group: invariance under r90 is invariance under all of C4.
  if (name == "c4") return makeType("r90");
  if (name == "d2ax") {   // {e, h, v, r180}: mirrors x = E/2, y = F/2
    SymType t{{}, Anchor::None};
    for (int E = 0; E <= 1; ++E)
      for (int F = 0; F <= 1; ++F)
        t.placements.push_back({{ID,
                                 {1,0,0, 0,-1,F},
                                 {-1,0,E, 0,1,0},
                                 {-1,0,E, 0,-1,F}}});
    return t;
  }
  if (name == "d2diag") { // {e, d, ad, r180}: mirrors y = x and x + y = D
    SymType t{{}, Anchor::None};
    for (int D = 0; D <= 1; ++D)
      t.placements.push_back({{ID,
                               {0,1,0, 1,0,0},
                               {0,-1,D, -1,0,D},
                               {-1,0,D, 0,-1,D}}});
    return t;
  }
  if (name == "d4") {     // the full group, centred on a cell (V=0) or vertex
    SymType t{{}, Anchor::None};
    for (int V = 0; V <= 1; ++V)
      t.placements.push_back({{ID,
                               {0,-1,V, 1,0,0},
                               {-1,0,V, 0,-1,V},
                               {0,1,0, -1,0,V},
                               {1,0,0, 0,-1,V},
                               {-1,0,V, 0,1,0},
                               {0,1,0, 1,0,0},
                               {0,-1,V, -1,0,V}}});
    return t;
  }
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
  // Optional (n, height) refinement. The height-preserving subgroup of D4 is
  // exactly D2ax = {e,h,v,r180}, so a height-graded orbit count is meaningful
  // for that type: it gives T(n,H) mod 2 (see experiments/subgroup_mod4.py).
  bool byHeight = false;
  std::vector<u64> hcounts;      // (maxn+1) x (maxn+1), indexed n*(maxn+1)+ht

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
    if (connectedAndAnchored()) {
      counts[w] += 1;
      if (byHeight) {
        int ymin = 1 << 30, ymax = -(1 << 30);
        for (int c : curCells) {
          const int y = cellY(c);
          ymin = std::min(ymin, y);
          ymax = std::max(ymax, y);
        }
        hcounts[w * (maxn + 1) + (ymax - ymin + 1)] += 1;
      }
    }
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

  // Enumerate every animal rooted at orbit r (the min-index orbit it contains,
  // via the u>root guard). Self-contained: resets reached, seeds the untried
  // pool from r's neighbours, sweeps, unwinds. Roots are independent, so this
  // is the unit of parallelism.
  void runRoot(int r) {
    const int V = static_cast<int>(orbitCells.size());
    if (weight[r] > maxn) return;
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

  // Parallel over roots: each thread takes an independent copy of the (cheap,
  // read-only-after-build) orbit graph + its own search buffers, and pulls
  // roots off an atomic counter. Dynamic pull because subtree sizes vary
  // wildly (a centred animal's root is its upper-left orbit; low-index roots
  // reach far more than edge ones). Thread-local counts reduce under a mutex.
  void runPlacementParallel(const std::vector<Aff>& group, int nthreads) {
    buildOrbits(group);
    const int V = static_cast<int>(orbitCells.size());
    present.assign(gridCells, 0);
    stamp.assign(gridCells, 0);
    reached.assign(V, 0);
    curStamp = 0;
    curCells.clear();
    list.clear();
    if (nthreads < 1) nthreads = 1;

    std::atomic<int> nextR{0};
    std::mutex reduceMu;
    auto body = [&]() {
      Counter w = *this;                 // independent buffers + graph copy
      w.counts.assign(maxn + 1, 0);
      if (byHeight) w.hcounts.assign((maxn + 1) * (maxn + 1), 0);
      w.list.reserve(V);
      int r;
      while ((r = nextR.fetch_add(1)) < V) w.runRoot(r);
      std::lock_guard<std::mutex> lk(reduceMu);
      for (int n = 0; n <= maxn; ++n) counts[n] += w.counts[n];
      for (size_t i = 0; i < hcounts.size(); ++i) hcounts[i] += w.hcounts[i];
    };
    std::vector<std::thread> pool;
    pool.reserve(nthreads);
    for (int t = 0; t < nthreads; ++t) pool.emplace_back(body);
    for (auto& th : pool) th.join();
  }
};

const int Counter::KDX[8] = {1, 1, 1, 0, 0, -1, -1, -1};
const int Counter::KDY[8] = {1, 0, -1, 1, -1, 1, 0, -1};

int main(int argc, char** argv) {
  // --byheight may appear anywhere; strip it, then read positionals.
  std::vector<std::string> pos;
  bool byHeight = false;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    if (a == "--byheight") byHeight = true;
    else pos.push_back(a);
  }
  if (pos.size() < 2 || pos.size() > 3) {
    std::fprintf(stderr,
                 "usage: %s {r90|r180|hmirror|dmirror|c4|d2ax|d2diag|d4} "
                 "MAXN [THREADS] [--byheight]\n",
                 argv[0]);
    return 2;
  }
  SymType type = makeType(pos[0]);
  const int maxn = std::atoi(pos[1].c_str());
  if (maxn < 1 || maxn > 40) { std::fprintf(stderr, "MAXN out of range\n"); return 2; }

  int nthreads = pos.size() == 3 ? std::atoi(pos[2].c_str()) : 0;
  if (nthreads <= 0) {
    nthreads = static_cast<int>(std::thread::hardware_concurrency());
    if (nthreads < 1) nthreads = 1;
  }

  Counter c;
  c.maxn = maxn;
  c.anchor = type.anchor;
  const int R = maxn + 2;
  c.lo = -(R + 1);
  c.hi = R + 1;
  c.gridW = c.hi - c.lo + 1;
  c.gridCells = c.gridW * c.gridW;
  c.counts.assign(maxn + 1, 0);
  c.byHeight = byHeight;
  if (byHeight) c.hcounts.assign((maxn + 1) * (maxn + 1), 0);

  obs::Reporter rep("symcount-" + pos[0] + "-N" + std::to_string(maxn),
                    static_cast<double>(type.placements.size()),
                    "type=" + pos[0] + " threads=" + std::to_string(nthreads) +
                        (byHeight ? " byheight=1" : ""));
  int pi = 0;
  for (const Placement& p : type.placements) {
    c.runPlacementParallel(p.group, nthreads);
    ++pi;
    rep.beat(pi, "placement=" + std::to_string(pi));
  }

  // Flat "n count"; with --byheight, "n H count" rows instead (height = the
  // bounding-box height of the whole animal, not of the quotient).
  if (byHeight) {
    for (int n = 1; n <= maxn; ++n)
      for (int h = 1; h <= maxn; ++h)
        if (c.hcounts[n * (maxn + 1) + h])
          std::printf("%d %d %llu\n", n, h,
                      static_cast<unsigned long long>(
                          c.hcounts[n * (maxn + 1) + h]));
  } else {
    for (int n = 1; n <= maxn; ++n)
      if (c.counts[n])
        std::printf("%d %llu\n", n,
                    static_cast<unsigned long long>(c.counts[n]));
  }
  rep.done("result=ok");
  return 0;
}
