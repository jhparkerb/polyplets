// Clean-room independent verifier for king-graph (8-connected) polyplet counts
// T(n,H) = number of FIXED polyplets of size n whose bounding box has height
// EXACTLY H (any width, any translation counted once; no rotation/reflection
// identification).
//
// INDEPENDENCE STATEMENT (see docs/next-system/designs/13-fast-frontier-verification.md):
//   This file deliberately does NOT #include cpp/tma/transition_square8.h,
//   cpp/tma/signature.h, or any production header. It is a from-scratch second
//   implementation of the same column transfer matrix so that a bug in the
//   production step kernel (stepColumnSquare8) does not correlate with a bug
//   here. Differences from production:
//     - connectivity is resolved by an explicit disjoint-set (union-find) built
//       fresh each step over {new-column rows} U {old component ids}; production
//       uses the same idea but its own path-compression arrays and a byte-array
//       Sig -- no code is shared.
//     - viable-mask generation uses a label-BITMASK coverage prune written here
//       from scratch (production's viableRec uses rowSup/sufSup row bitmasks).
//     - exact 64-bit counting (values through n=24 fit in u64), or optional
//       mod-p; production uses u32 mod-p / sort-merge exact.
//   The king-adjacency rule itself (a new cell in row r touches old-column cells
//   in rows {r-1,r,r+1} and same-column cells r+/-1) is intrinsic to the lattice
//   and is NOT "shared logic" -- any correct implementation must use it.
//
// Algorithm (column transfer matrix, left to right):
//   State = the current (rightmost) occupied column, as a partition of its
//   occupied rows into connected components of the partial animal, plus two
//   flags: touched-top (some cell ever in box row 0) and touched-bottom (row
//   H-1). Encoded as a compact key.
//   Seed = empty column. Step: pick a nonempty mask for the next column; a new
//   cell connects (king) to old cells in rows {r-1,r,r+1} and to a same-column
//   new cell in r+1. DEATH rule: if any old component has no new cell adjacent
//   to it, the mask strands it (disconnects the animal) -> reject. HARVEST: a
//   state with exactly ONE component and both flags set is a complete polyplet;
//   add its size-n counts to T(n,H). Every reachable such state is harvested
//   (each fixed polyplet has a unique column decomposition -> counted once).
//
// Build:  c++ -std=c++20 -O3 -o build/cleanroom_verify experiments/cleanroom/cleanroom_verify.cpp
// Usage:  cleanroom_verify MAXN [HMAX] [--prime P] [--triangle FILE] [--quiet]

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <unordered_map>
#include <map>
#include <chrono>

using u64 = std::uint64_t;
using u128 = unsigned __int128;

// ---- disjoint set (my own; fresh per step) ------------------------------
struct DSU {
  std::vector<int> p;
  void reset(int n) { p.resize(n); for (int i = 0; i < n; ++i) p[i] = i; }
  int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
  void join(int a, int b) { a = find(a); b = find(b); if (a != b) p[a] = b; }
};

// A boundary state key: H bytes of component labels (0 = empty row, else
// component id in restricted-growth form 1,2,3,... top-to-bottom) + top flag +
// bottom flag. Distinct encoding built by our own code path.
using Key = std::string;

// Value: counts by size n (index 0..maxn). Exact u64 or mod-p.
struct Row {
  std::vector<u64> c;
  explicit Row(int maxn) : c(maxn + 1, 0) {}
};

static int H_, MAXN_;
static u64 PRIME_ = 0;  // 0 = exact 64-bit

static inline u64 addmod(u64 a, u64 b) {
  if (!PRIME_) return a + b;  // exact: verified in-range for n<=24
  a += b; if (a >= PRIME_) a -= PRIME_; return a;
}

// Build the canonical key of a boundary column given an occupancy bitmask and a
// component root for each occupied row, plus the two flags. Relabels roots in
// order of first appearance (top row 0 downward) -> restricted growth string.
static Key makeKey(unsigned occ, const std::array<int, 32>& root,
                   bool top, bool bot) {
  Key k(H_ + 2, '\0');
  std::array<int, 64> remap;
  remap.fill(0);
  int next = 1;
  for (int r = 0; r < H_; ++r) {
    if (!((occ >> r) & 1u)) { k[r] = 0; continue; }
    int rt = root[r];
    if (remap[rt] == 0) remap[rt] = next++;
    k[r] = static_cast<char>(remap[rt]);
  }
  k[H_] = top ? 1 : 0;
  k[H_ + 1] = bot ? 1 : 0;
  return k;
}

// Enumerate viable next-column masks for an old state. `occOld` = occupied rows;
// `labelOld[r]` = component label (1..) of old row r (0 if empty); `budget` =
// max new cells allowed. Prunes by popcount and by a label-bitmask coverage
// check: every old component must be touched by some chosen cell, else it is
// stranded (the step would reject it anyway; we prune early).
template <class F>
static void forEachMask(unsigned occOld, const std::array<int, 32>& labelOld,
                        int budget, F&& emit) {
  // Which component labels exist, and for each row r which labels it would cover
  // if occupied (labels of old rows in {r-1,r,r+1}).
  std::uint32_t allLabels = 0;
  for (int r = 0; r < H_; ++r)
    if ((occOld >> r) & 1u) allLabels |= (1u << labelOld[r]);
  std::array<std::uint32_t, 32> rowCov{};
  for (int r = 0; r < H_; ++r) {
    std::uint32_t m = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H_ && ((occOld >> rr) & 1u)) m |= (1u << labelOld[rr]);
    rowCov[r] = m;
  }
  std::array<std::uint32_t, 33> suf{};
  suf[H_] = 0;
  for (int r = H_ - 1; r >= 0; --r) suf[r] = suf[r + 1] | rowCov[r];

  // DFS over rows.
  struct Rec {
    static void go(int r, unsigned mask, int bits, std::uint32_t cov,
                   std::uint32_t all, const std::array<std::uint32_t, 32>& rowCov,
                   const std::array<std::uint32_t, 33>& suf, int budget, int H,
                   F& emit) {
      if ((cov | suf[r]) != all) return;  // some component can no longer be covered
      if (r == H) { if (mask) emit(mask); return; }
      go(r + 1, mask, bits, cov, all, rowCov, suf, budget, H, emit);  // leave empty
      if (bits + 1 <= budget)
        go(r + 1, mask | (1u << r), bits + 1, cov | rowCov[r], all, rowCov, suf,
           budget, H, emit);  // occupy row r
    }
  };
  Rec::go(0, 0u, 0, 0u, allLabels, rowCov, suf, budget, H_, emit);
}

// Apply one column step. Returns false if the mask strands an old component.
// On success writes the new key and reports new-cell count via popcount(mask).
static bool step(unsigned occOld, const std::array<int, 32>& labelOld,
                 int nCompOld, bool topOld, bool botOld, unsigned mask,
                 Key& outKey) {
  // Universe: new rows 0..H-1 at index r; old component labels 1..nCompOld at
  // index H + label. (label ids are 1..nComp in the stored key.)
  DSU d;
  const int base = H_;  // old label L -> base + L
  d.reset(H_ + nCompOld + 1);
  for (int r = 0; r < H_; ++r) {
    if (!((mask >> r) & 1u)) continue;
    if (r + 1 < H_ && ((mask >> (r + 1)) & 1u)) d.join(r, r + 1);  // vertical
    for (int rr = r - 1; rr <= r + 1; ++rr) {                      // king to old
      if (rr < 0 || rr >= H_) continue;
      int L = labelOld[rr];
      if (L) d.join(r, base + L);
    }
  }
  // Stranding: every old component must share a union-find root with some new
  // cell. Mark roots that contain a new cell, then check each old component.
  std::array<char, 64 + 32> rootHasNew{};
  rootHasNew.fill(0);
  for (int r = 0; r < H_; ++r)
    if ((mask >> r) & 1u) rootHasNew[d.find(r)] = 1;
  for (int L = 1; L <= nCompOld; ++L)
    if (!rootHasNew[d.find(base + L)]) return false;  // stranded -> dead

  // Build new component roots per occupied new row.
  std::array<int, 32> root{};
  for (int r = 0; r < H_; ++r)
    if ((mask >> r) & 1u) root[r] = d.find(r);
  bool top = topOld || (mask & 1u);
  bool bot = botOld || ((mask >> (H_ - 1)) & 1u);
  outKey = makeKey(mask, root, top, bot);
  return true;
}

// Sweep one strip height H; fill T[n] for this H.
static std::vector<u64> sweepHeight(int H, int maxn) {
  H_ = H; MAXN_ = maxn;
  std::vector<u64> T(maxn + 1, 0);
  // dp over generations (column count). Start: empty column, count 1 at n=0.
  std::unordered_map<Key, Row> cur;
  Key empt(H + 2, '\0');
  { Row r0(maxn); r0.c[0] = 1; cur.emplace(empt, std::move(r0)); }

  for (int gen = 0; gen <= maxn; ++gen) {
    std::unordered_map<Key, Row> nxt;
    nxt.reserve(cur.size() * 2);
    for (auto& [key, row] : cur) {
      // Decode key.
      unsigned occ = 0;
      std::array<int, 32> label{};
      label.fill(0);
      int nComp = 0;
      for (int r = 0; r < H; ++r) {
        int v = (unsigned char)key[r];
        label[r] = v;
        if (v) { occ |= (1u << r); nComp = std::max(nComp, v); }
      }
      bool top = key[H] != 0, bot = key[H + 1] != 0;

      // Harvest: complete polyplet iff single component + both flags.
      if (nComp == 1 && top && bot)
        for (int n = 1; n <= maxn; ++n)
          if (row.c[n]) T[n] = addmod(T[n], row.c[n]);

      // Minimum size already committed in this state (smallest n with count).
      int ms = maxn + 1;
      for (int n = 0; n <= maxn; ++n) if (row.c[n]) { ms = n; break; }
      if (ms > maxn) continue;
      int budget = maxn - ms;
      if (budget <= 0) continue;

      forEachMask(occ, label, budget, [&](unsigned mask) {
        Key ok;
        if (!step(occ, label, nComp, top, bot, mask, ok)) return;
        int cells = __builtin_popcount(mask);
        auto it = nxt.find(ok);
        if (it == nxt.end()) it = nxt.emplace(ok, Row(maxn)).first;
        Row& dst = it->second;
        for (int n = 0; n + cells <= maxn; ++n)
          if (row.c[n]) dst.c[n + cells] = addmod(dst.c[n + cells], row.c[n]);
      });
    }
    cur = std::move(nxt);
    if (cur.empty()) break;
  }
  return T;
}

// ---- reference loading + reporting --------------------------------------
int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr,
      "usage: %s MAXN [HMAX] [--prime P] [--triangle FILE] [--quiet]\n", argv[0]);
    return 2;
  }
  int maxn = std::atoi(argv[1]);
  int hmax = maxn;
  std::string triFile = "results/ns_a24/triangle.txt";
  bool quiet = false;
  for (int i = 2; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--prime" && i + 1 < argc) PRIME_ = std::strtoull(argv[++i], nullptr, 10);
    else if (a == "--triangle" && i + 1 < argc) triFile = argv[++i];
    else if (a == "--quiet") quiet = true;
    else if (a[0] != '-') hmax = std::atoi(argv[i]);
  }
  if (hmax > maxn) hmax = maxn;

  // Load reference triangle (values fit u64 through n=24).
  std::map<std::pair<int,int>, u64> ref;
  if (FILE* f = std::fopen(triFile.c_str(), "r")) {
    char line[256];
    while (std::fgets(line, sizeof line, f)) {
      if (line[0] == '#') continue;
      int n, h; unsigned long long v;
      if (std::sscanf(line, "%d %d %llu", &n, &h, &v) == 3)
        ref[{n, h}] = v;
    }
    std::fclose(f);
  } else if (!quiet) {
    std::fprintf(stderr, "warning: could not open %s (no comparison)\n", triFile.c_str());
  }

  auto t0 = std::chrono::steady_clock::now();
  // T[n][H]
  std::vector<std::vector<u64>> T(maxn + 1, std::vector<u64>(hmax + 1, 0));
  for (int H = 1; H <= hmax; ++H) {
    auto th0 = std::chrono::steady_clock::now();
    std::vector<u64> row = sweepHeight(H, maxn);
    for (int n = 1; n <= maxn; ++n) T[n][H] = row[n];
    if (!quiet) {
      double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - th0).count();
      std::fprintf(stderr, "  H=%d swept in %.2fs\n", H, dt);
    }
  }

  // Compare + report.
  int mism = 0, checked = 0;
  int maxMatchN = 0;
  for (int n = 1; n <= maxn; ++n) {
    bool rowOK = true, rowHasRef = false;
    for (int H = 1; H <= std::min(n, hmax); ++H) {
      u64 got = T[n][H];
      auto it = ref.find({n, H});
      if (it == ref.end()) continue;
      rowHasRef = true;
      ++checked;
      u64 want = PRIME_ ? (it->second % PRIME_) : it->second;
      if (got != want) {
        ++mism; rowOK = false;
        if (mism <= 40)
          std::printf("MISMATCH n=%d H=%d got=%llu want=%llu\n",
                      n, H, (unsigned long long)got, (unsigned long long)want);
      }
    }
    if (rowHasRef && rowOK && hmax >= std::min(n, maxn)) maxMatchN = n;
  }

  // Row sums (a(n)) if we swept all H up to n.
  std::printf("\n# T(n,H) clean-room verifier  (prime=%llu, hmax=%d)\n",
              (unsigned long long)PRIME_, hmax);
  for (int n = 1; n <= maxn; ++n) {
    if (hmax < n) break;  // row incomplete
    u64 s = 0;
    for (int H = 1; H <= n; ++H) s = PRIME_ ? addmod(s, T[n][H]) : s + T[n][H];
    std::printf("a(%d) = %llu\n", n, (unsigned long long)s);
  }

  double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  std::printf("\ncompared %d (n,H) cells vs %s: %d mismatch\n",
              checked, triFile.c_str(), mism);
  std::printf("largest n with full row matching reference: %d\n", maxMatchN);
  std::printf("total time: %.2fs\n", dt);
  return mism ? 1 : 0;
}
