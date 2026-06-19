// Fixed-height king transfer matrix over Z/pZ, for generating-function recovery.
//
// Counts B_H(n) = fixed polyplets of n cells, bounding-box height exactly H, mod a
// prime p. Same column-transfer boundary state as the exact engines (last-column
// occupancy mask + connectivity partition + top/bottom touch flags), but counts
// are reduced mod p so there is no overflow and arbitrarily many terms can be
// produced -- enough to recover the (rational) generating function's recurrence
// by Berlekamp-Massey mod p, then lift to Z by CRT (see gf/modp_recover.py).
//
// No pruning: a single fixed height has a bounded boundary-state space anyway, so
// pruning would only add the modular "is this count nonzero?" hazard for nothing.
//
// CLI:  gf_modp H N P     -> emits "n  B_H(n) mod P"  for n = 1..N
//
// Cross-checked against the exact engines (build/tma --only-height, gf/fixed_height.py):
// reducing their exact B_H(n) mod P must match this for every n.

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unordered_map>
#include <vector>

using u64 = std::uint64_t;

static int H;
static bool ROOK = false;   // true = rook (cross-column same row only)
static int VREACH = 1;      // vertical adjacency reach: 1 = king, 2 = "reach-2"
                            // (5-row-tall neighborhood, still 1-column memory)

// --- tiny union-find over <= 2H node ids ---
static int uf_find(int* p, int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
static void uf_union(int* p, int a, int b) { int ra = uf_find(p, a), rb = uf_find(p, b); if (ra != rb) p[ra] = rb; }

// set-bit rows of a mask, low to high
static int rowsOf(int mask, int* rows) {
  int k = 0;
  for (int r = 0; r < H; ++r) if (mask >> r & 1) rows[k++] = r;
  return k;
}

// canonical labels (first-seen 0,1,2,...) for a list of roots; pack 4 bits each
static u64 packCanon(const int* roots, int k) {
  int map[64]; for (int i = 0; i < 64; ++i) map[i] = -1;
  u64 packed = 0; int next = 0;
  for (int i = 0; i < k; ++i) {
    int r = roots[i];
    if (map[r] < 0) map[r] = next++;
    packed |= (u64)(map[r] & 0xF) << (4 * i);
  }
  return packed;
}

// a boundary state: occupancy mask, packed component labels, touch flags
struct State { int mask; u64 lab; bool tT, tB; };
struct Key { int mask; u64 lab; int flags;
  bool operator==(const Key& o) const { return mask == o.mask && lab == o.lab && flags == o.flags; } };
struct KeyHash { size_t operator()(const Key& k) const {
  u64 h = 1469598103934665603ull;
  h = (h ^ (u64)k.mask) * 1099511628211ull;
  h = (h ^ k.lab) * 1099511628211ull;
  h = (h ^ (u64)k.flags) * 1099511628211ull;
  return h; } };

// within-column components of a single mask (vertical adjacency)
static u64 colLabels(int mask) {
  int rows[64]; int k = rowsOf(mask, rows);
  int p[64]; for (int i = 0; i < k; ++i) p[i] = i;
  for (int i = 0; i < k; ++i)                 // within-column vertical adjacency
    for (int j = i + 1; j < k; ++j)
      if (rows[j] - rows[i] <= VREACH) uf_union(p, i, j);
  int roots[64]; for (int i = 0; i < k; ++i) roots[i] = uf_find(p, i);
  return packCanon(roots, k);
}

// transition: prev (mask1, lab1) -> next column mask2.
// writes the canonical next labels to *outLab; returns false if a prev component
// is stranded (no cell adjacent to the new column -> can never reconnect).
static bool step(int mask1, u64 lab1, int mask2, u64* outLab) {
  int r1[64], r2[64];
  int n1 = rowsOf(mask1, r1), n2 = rowsOf(mask2, r2);
  int p[128]; for (int i = 0; i < n1 + n2; ++i) p[i] = i;
  int lab1arr[64];
  for (int i = 0; i < n1; ++i) lab1arr[i] = (int)((lab1 >> (4 * i)) & 0xF);
  for (int i = 0; i < n1; ++i)                 // prev rows sharing a label
    for (int j = i + 1; j < n1; ++j)
      if (lab1arr[i] == lab1arr[j]) uf_union(p, i, j);
  for (int a = 0; a < n2; ++a)                  // new column vertical adjacency
    for (int b = a + 1; b < n2; ++b)
      if (r2[b] - r2[a] <= VREACH) uf_union(p, n1 + a, n1 + b);
  for (int j = 0; j < n2; ++j)                  // cross-column adjacency
    for (int i = 0; i < n1; ++i) {
      const int dr = r1[i] - r2[j];
      const bool adj = ROOK ? (dr == 0)                          // rook: same row
                            : (dr >= -VREACH && dr <= VREACH);   // king / reach-V
      if (adj) uf_union(p, n1 + j, i);
    }
  // every prev component must reach some new-column node
  bool newRoot[128]; for (int i = 0; i < n1 + n2; ++i) newRoot[i] = false;
  for (int j = 0; j < n2; ++j) newRoot[uf_find(p, n1 + j)] = true;
  for (int i = 0; i < n1; ++i) if (!newRoot[uf_find(p, i)]) return false;
  int roots[64]; for (int j = 0; j < n2; ++j) roots[j] = uf_find(p, n1 + j);
  *outLab = packCanon(roots, n2);
  return true;
}

int main(int argc, char** argv) {
  if (argc < 4) { std::fprintf(stderr, "usage: %s H N P [rook]\n", argv[0]); return 2; }
  H = std::atoi(argv[1]);
  const int N = std::atoi(argv[2]);
  const u64 P = std::strtoull(argv[3], nullptr, 10);
  if (argc >= 5) {
    if (std::strcmp(argv[4], "rook") == 0) ROOK = true;
    else VREACH = std::atoi(argv[4]);          // vertical reach (1=king, 2=reach-2)
  }
  if (H < 1 || H > 15) { std::fprintf(stderr, "H out of range (1..15)\n"); return 2; }
  const int full = (1 << H) - 1, top = 1, bot = 1 << (H - 1);

  // --- enumerate states and their transitions (BFS) ---
  std::unordered_map<Key, int, KeyHash> id;
  std::vector<State> states;
  auto intern = [&](int mask, u64 lab, bool tT, bool tB) -> int {
    Key k{mask, lab, (tT ? 2 : 0) | (tB ? 1 : 0)};
    auto it = id.find(k);
    if (it != id.end()) return it->second;
    int s = (int)states.size();
    id.emplace(k, s); states.push_back({mask, lab, tT, tB});
    return s;
  };
  std::vector<int> startIds; std::vector<int> startCells;
  for (int m = 1; m <= full; ++m)
    { startIds.push_back(intern(m, colLabels(m), m & top, m & bot)); startCells.push_back(__builtin_popcount(m)); }

  std::vector<int> efrom, eto, eadd;                     // flat edge list
  for (size_t s = 0; s < states.size(); ++s) {           // states grows during the loop
    const State st = states[s];
    for (int m2 = 1; m2 <= full; ++m2) {
      u64 lab2;
      if (!step(st.mask, st.lab, m2, &lab2)) continue;
      int t = intern(m2, lab2, st.tT || (m2 & top), st.tB || (m2 & bot));
      efrom.push_back((int)s); eto.push_back(t); eadd.push_back(__builtin_popcount(m2));
    }
  }
  const int S = (int)states.size();
  const size_t E = efrom.size();

  // terminal = single component (max label 0) AND both flags
  std::vector<char> terminal(S);
  for (int s = 0; s < S; ++s) {
    int k = __builtin_popcount(states[s].mask), maxlab = 0;
    for (int i = 0; i < k; ++i) maxlab = std::max(maxlab, (int)((states[s].lab >> (4 * i)) & 0xF));
    terminal[s] = (maxlab == 0) && states[s].tT && states[s].tB;
  }

  // --- DP indexed by cell-count: b[n][s] = #partial animals of n cells ending in
  // state s. b[n][t] = [start if t is a single-column state of size n] +
  // sum over edges (s->t, add) of b[n-add][s]. Cost O(N * #edges). Rolling
  // window of the last H+1 cell-count rows (since add <= H).
  const int Wn = H + 1;
  std::vector<u64> buf((size_t)Wn * S, 0);
  auto rowOf = [&](int n) -> u64* { return &buf[(size_t)(n % Wn) * S]; };
  std::vector<u64> res(N + 1, 0);
  for (int n = 1; n <= N; ++n) {
    u64* bn = rowOf(n);
    std::fill(bn, bn + S, 0);                       // reuse the slot from n-Wn
    for (size_t i = 0; i < startIds.size(); ++i)    // single-column base cases
      if (startCells[i] == n) bn[startIds[i]] = (bn[startIds[i]] + 1) % P;
    for (size_t e = 0; e < E; ++e)                  // extend by one column
      if (n - eadd[e] >= 1) {
        u64 v = rowOf(n - eadd[e])[efrom[e]];
        if (v) bn[eto[e]] = (bn[eto[e]] + v) % P;
      }
    u64 acc = 0;
    for (int s = 0; s < S; ++s) if (terminal[s] && bn[s]) acc = (acc + bn[s]) % P;
    res[n] = acc;
  }
  for (int n = 1; n <= N; ++n) std::printf("%d %llu\n", n, (unsigned long long)res[n]);
  return 0;
}
