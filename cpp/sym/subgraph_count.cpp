// E0: weighted connected-subgraph counter (S2 phase 2, Layer "science").
//
// Counts connected node-subsets of a finite graph by total node weight, each
// subset exactly once. This is Redelmeier's algorithm generalized off the
// lattice: instead of a half-plane anchoring the translation, we anchor each
// connected subset by its MINIMUM-index vertex -- the search rooted at r only
// ever adds vertices with index > r, so a subset is generated exactly once,
// in the r = (its min vertex) pass. Node weights (orbit sizes 1/2/4 in the
// symmetric enumerator) just make a step advance total weight by wt[v]
// instead of 1.
//
// Input (stdin):
//   line 1: V
//   line 2: V integer weights
//   line 3: E
//   next E lines: "u v"   (undirected edge, 0-indexed)
// Arg: MAXN. Output: "w count" for 1 <= w <= MAXN with count > 0.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

using u64 = std::uint64_t;

struct Graph {
  int V = 0;
  std::vector<int> wt;
  std::vector<std::vector<int>> adj;
};

static int g_maxn;
static const Graph* g;
static std::vector<u64> g_counts;
static std::vector<char> g_reached;

// S currently has total weight w and has already been recorded; extend it by
// vertices in `untried` (all with index > r), recording each new connected
// subset once. `untried` is taken by value: each level keeps its own list so
// a child cannot disturb a parent's pending vertices.
static void grow(int r, long w, std::vector<int> untried) {
  while (!untried.empty()) {
    const int v = untried.back();
    untried.pop_back();
    const long nw = w + g->wt[v];
    if (nw <= g_maxn) {
      g_counts[nw]++;
      std::vector<int> next = untried;
      std::vector<int> newly;
      for (int u : g->adj[v]) {
        if (u > r && !g_reached[u]) {
          g_reached[u] = 1;
          newly.push_back(u);
          next.push_back(u);
        }
      }
      grow(r, nw, std::move(next));
      for (int u : newly) g_reached[u] = 0;
    }
    // v stays reached for the rest of this level (the tried-set rule): a later
    // sibling must not re-add it. It is cleared by the next r-pass reset.
  }
}

int main(int argc, char** argv) {
  if (argc != 2) {
    std::fprintf(stderr, "usage: %s MAXN  (graph on stdin)\n", argv[0]);
    return 2;
  }
  g_maxn = std::atoi(argv[1]);
  if (g_maxn < 1) { std::fprintf(stderr, "MAXN must be >= 1\n"); return 2; }

  Graph graph;
  if (std::scanf("%d", &graph.V) != 1 || graph.V < 0) return 2;
  graph.wt.resize(graph.V);
  graph.adj.resize(graph.V);
  for (int i = 0; i < graph.V; ++i)
    if (std::scanf("%d", &graph.wt[i]) != 1) return 2;
  int E = 0;
  if (std::scanf("%d", &E) != 1 || E < 0) return 2;
  for (int e = 0; e < E; ++e) {
    int a, b;
    if (std::scanf("%d %d", &a, &b) != 2) return 2;
    if (a < 0 || a >= graph.V || b < 0 || b >= graph.V) return 2;
    graph.adj[a].push_back(b);
    graph.adj[b].push_back(a);
  }

  g = &graph;
  g_counts.assign(g_maxn + 1, 0);
  for (int r = 0; r < graph.V; ++r) {
    g_reached.assign(graph.V, 0);
    g_reached[r] = 1;
    if (graph.wt[r] > g_maxn) continue;
    g_counts[graph.wt[r]]++;
    std::vector<int> untried;
    for (int u : graph.adj[r]) {
      if (u > r && !g_reached[u]) {
        g_reached[u] = 1;
        untried.push_back(u);
      }
    }
    grow(r, graph.wt[r], std::move(untried));
  }

  for (int w = 1; w <= g_maxn; ++w)
    if (g_counts[w])
      std::printf("%d %llu\n", w, static_cast<unsigned long long>(g_counts[w]));
  return 0;
}
