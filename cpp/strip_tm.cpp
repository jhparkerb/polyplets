// strip_tm.cpp — independent strip transfer-matrix engine for the polyplet
// triangle T(n,H). A SECOND, kink-independent computation path.
//
// Sweeps a height-H strip column by column with a king-connectivity partition
// state, counting king-connected cell sets by area with horizontal translation
// fixed (leftmost occupied column = 0). Produces
//     C_H(n) = sum_{h<=H} (H-h+1) * T(n,h)      (vertical placements counted)
// and recovers the triangle by the exact second difference in H:
//     T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n)   (C_0 = C_{-1} = 0).
//
// Counts are __int128: C_H(n) <= H * a(n), and a(36) ~ 2.5e28, so H<=15 at
// n<=40 stays far under the 1.7e38 int128 ceiling. State is packed 4 bits per
// row (label 0=empty else 1..8) into a uint64, so H<=15.
//
// This shares no enumeration with the kink NW-carry kernel that produced the
// banked triangle; agreement is a genuine cross-check. The Python twin
// (experiments/strip_engine.py) is brute-force-anchored at small n and this
// binary is cross-checked against it on H<=10.
//
// Usage: strip_tm <Hmax> <Nmax> [banked_perheight_dir]
//   prints per-H timing, C_H head values, and (if a banked dir is given)
//   a match count of engine T(n,H) vs the banked triangle.

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <chrono>
#include <fstream>
#include <sstream>

using u64 = uint64_t;
using i128 = __int128;

static std::string i128str(i128 v) {
  if (v == 0) return "0";
  bool neg = v < 0;
  unsigned __int128 u = neg ? (unsigned __int128)(-v) : (unsigned __int128)v;
  std::string s;
  while (u) { s += char('0' + int(u % 10)); u /= 10; }
  if (neg) s += '-';
  std::reverse(s.begin(), s.end());
  return s;
}

static i128 parse_i128(const std::string& s) {
  i128 v = 0;
  size_t i = 0;
  bool neg = false;
  if (i < s.size() && (s[i] == '-' || s[i] == '+')) { neg = s[i] == '-'; ++i; }
  for (; i < s.size(); ++i) {
    if (s[i] < '0' || s[i] > '9') break;
    v = v * 10 + (s[i] - '0');
  }
  return neg ? -v : v;
}

struct Engine {
  int H, N;
  // transition cache: state -> successor states + cell-count added, stored as
  // PARALLEL arrays (u64 + uint8_t = 9 bytes/edge, vs 16 for a padded pair) so
  // the cache stays in RAM at H=16 (~millions of states x ~thousands of edges).
  struct TL { std::vector<u64> next; std::vector<uint8_t> add; };
  std::unordered_map<u64, TL> trans;
  std::unordered_map<u64, char> closable;

  static inline int lab(u64 st, int r) { return int((st >> (4 * r)) & 0xF); }

  // Compute the new packed state for placing column S over boundary `st`.
  // Returns true and sets `out`, or false if a previous component would be
  // buried (permanent disconnection).
  bool step(u64 st, int S, u64& out) {
    int occ[16];
    for (int r = 0; r < H; ++r) occ[r] = lab(st, r);
    // tokens: new cells 0..H-1 ; prev components H + label(1..8)
    int par[32];
    for (int i = 0; i < H + 9; ++i) par[i] = i;
    auto find = [&](int x) {
      while (par[x] != x) { par[x] = par[par[x]]; x = par[x]; }
      return x;
    };
    auto uni = [&](int a, int b) { int ra = find(a), rb = find(b); if (ra != rb) par[ra] = rb; };

    int nprev = 0;
    bool seen[9] = {false};
    for (int r = 0; r < H; ++r)
      if (occ[r] && !seen[occ[r]]) { seen[occ[r]] = true; ++nprev; }

    // vertical unions among new cells
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      if (r + 1 < H && ((S >> (r + 1)) & 1)) uni(r, r + 1);
    }
    // cross-column unions + touched-component tracking
    bool touched[9] = {false};
    int ntouch = 0;
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      for (int dr = -1; dr <= 1; ++dr) {
        int rr = r + dr;
        if (rr < 0 || rr >= H) continue;
        int g = occ[rr];
        if (g) {
          if (!touched[g]) { touched[g] = true; ++ntouch; }
          uni(r, H + g);
        }
      }
    }
    if (ntouch < nprev) return false;  // a component was buried

    // relabel new column by component root, first-seen order from row 0
    int rootlab[32];
    for (int i = 0; i < H + 9; ++i) rootlab[i] = 0;
    int next = 1;
    u64 ns = 0;
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      int root = find(r);
      if (!rootlab[root]) rootlab[root] = next++;
      ns |= (u64)rootlab[root] << (4 * r);
    }
    out = ns;
    return true;
  }

  const TL& transitions(u64 st) {
    auto it = trans.find(st);
    if (it != trans.end()) return it->second;
    TL lst;
    int full = (1 << H) - 1;
    for (int S = 1; S <= full; ++S) {
      int add = __builtin_popcount(S);
      if (add > N - 1) continue;
      u64 ns;
      if (step(st, S, ns)) { lst.next.push_back(ns); lst.add.push_back((uint8_t)add); }
    }
    // closable = exactly one component in st
    int comps = 0; bool seen[9] = {false};
    for (int r = 0; r < H; ++r) { int g = lab(st, r); if (g && !seen[g]) { seen[g] = true; ++comps; } }
    closable[st] = (comps == 1) ? 1 : 0;
    auto res = trans.emplace(st, std::move(lst));
    return res.first->second;
  }

  // Compute C_H(0..N).
  std::vector<i128> run() {
    std::vector<i128> C(N + 1, 0);
    std::unordered_map<u64, std::vector<i128>> dp;
    int full = (1 << H) - 1;
    // start column: nonempty, components = vertical runs of S
    for (int S = 1; S <= full; ++S) {
      int add = __builtin_popcount(S);
      if (add > N) continue;
      u64 ns = 0; int next = 1;
      int r = 0;
      while (r < H) {
        if ((S >> r) & 1) {
          int L = next++;
          while (r < H && ((S >> r) & 1)) { ns |= (u64)L << (4 * r); ++r; }
        } else ++r;
      }
      auto& v = dp[ns];
      if (v.empty()) v.assign(N + 1, 0);
      v[add] += 1;
    }
    while (!dp.empty()) {
      std::unordered_map<u64, std::vector<i128>> ndp;
      for (auto& kv : dp) {
        u64 st = kv.first;
        auto& vec = kv.second;
        int hi = 0;
        for (int n = N; n >= 0; --n) if (vec[n] != 0) { hi = n; break; }
        if (hi == 0 && vec[0] == 0) continue;
        const auto& tl = transitions(st);
        if (closable[st]) for (int n = 0; n <= N; ++n) if (vec[n]) C[n] += vec[n];
        for (size_t e = 0; e < tl.next.size(); ++e) {
          int add = tl.add[e];
          u64 ns = tl.next[e];
          auto& nv = ndp[ns];
          if (nv.empty()) nv.assign(N + 1, 0);
          int lim = std::min(hi, N - add);
          for (int n = 0; n <= lim; ++n) { i128 v = vec[n]; if (v) nv[n + add] += v; }
        }
      }
      dp.swap(ndp);
    }
    return C;
  }
};

int main(int argc, char** argv) {
  // Single-height mode: compute only C_H(0..N) and write "n value" lines.
  // Lets the three machines split heights and compose by differencing later.
  if (argc >= 5 && std::string(argv[1]) == "single") {
    int H = std::atoi(argv[2]);
    int Nmax = std::atoi(argv[3]);
    std::string out = argv[4];
    if (H > 16) { std::fprintf(stderr, "H<=16 (state packing)\n"); return 1; }
    std::printf("strip_tm single: H=%d Nmax=%d -> %s\n", H, Nmax, out.c_str());
    std::fflush(stdout);
    Engine e; e.H = H; e.N = Nmax;
    auto t0 = std::chrono::steady_clock::now();
    auto C = e.run();
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::printf("  C_%d computed in %.1fs (states cached: %zu)\n", H, s, e.trans.size());
    std::ofstream f(out);
    for (int n = 0; n <= Nmax; ++n) f << n << " " << i128str(C[n]) << "\n";
    std::printf("  wrote C_%d(0..%d); head:", H, Nmax);
    for (int n = H; n <= std::min(H + 3, Nmax); ++n) std::printf(" %s", i128str(C[n]).c_str());
    std::printf("\n");
    return 0;
  }

  if (argc < 3) { std::fprintf(stderr, "usage: strip_tm <Hmax> <Nmax> [banked_dir]\n"
                                       "       strip_tm single <H> <Nmax> <outfile>\n"); return 1; }
  int Hmax = std::atoi(argv[1]);
  int Nmax = std::atoi(argv[2]);
  std::string bankdir = (argc > 3) ? argv[3] : "";
  if (Hmax > 16) { std::fprintf(stderr, "Hmax<=16 (state packing)\n"); return 1; }

  std::printf("strip_tm (C++): Hmax=%d Nmax=%d\n", Hmax, Nmax);
  std::vector<std::vector<i128>> Ccols(Hmax + 1);
  std::vector<i128> zero(Nmax + 1, 0);
  for (int H = 1; H <= Hmax; ++H) {
    Engine e; e.H = H; e.N = Nmax;
    auto t0 = std::chrono::steady_clock::now();
    Ccols[H] = e.run();
    auto t1 = std::chrono::steady_clock::now();
    double s = std::chrono::duration<double>(t1 - t0).count();
    std::printf("  C_%-2d computed in %8.2fs  (states cached: %zu)\n", H, s, e.trans.size());
    std::fflush(stdout);
  }

  // recover T and (optionally) compare to banked triangle
  std::unordered_map<long long, i128> banked;  // key n*100+H
  int bmax = 0;
  if (!bankdir.empty()) {
    for (int H = 1; H <= Hmax; ++H) {
      std::ostringstream p; p << bankdir << "/h" << H << ".out";
      std::ifstream f(p.str());
      if (!f) continue;
      std::string line;
      while (std::getline(f, line)) {
        std::istringstream is(line);
        long long n; std::string val;
        if (is >> n >> val) { banked[n * 100 + H] = parse_i128(val); if (n > bmax) bmax = (int)n; }
      }
    }
  }

  int bank_ok = 0, bank_bad = 0;
  long long fb_n = -1, fb_H = -1; i128 fb_g = 0, fb_e = 0;
  for (int H = 1; H <= Hmax; ++H) {
    const auto& cH = Ccols[H];
    const auto& cH1 = (H - 1 >= 1) ? Ccols[H - 1] : zero;
    const auto& cH2 = (H - 2 >= 1) ? Ccols[H - 2] : zero;
    for (int n = H; n <= Nmax; ++n) {
      i128 t = cH[n] - 2 * cH1[n] + cH2[n];
      auto it = banked.find((long long)n * 100 + H);
      if (it != banked.end()) {
        if (t == it->second) ++bank_ok;
        else { ++bank_bad; if (fb_n < 0) { fb_n = n; fb_H = H; fb_g = t; fb_e = it->second; } }
      }
    }
  }
  if (!bankdir.empty()) {
    std::printf("\nvs banked triangle: %d match, %d MISMATCH\n", bank_ok, bank_bad);
    if (fb_n >= 0)
      std::printf("  first mismatch T(%lld,%lld): engine=%s banked=%s\n",
                  fb_n, fb_H, i128str(fb_g).c_str(), i128str(fb_e).c_str());
    else
      std::printf("  ALL AGREE -> columns H<=%d independently confirmed to n=%d\n", Hmax, bmax);
  }

  std::printf("\nC_H head values (independent), n=H..H+3:\n");
  for (int H = 1; H <= Hmax; ++H) {
    std::printf("  C_%-2d:", H);
    for (int n = H; n <= std::min(H + 3, Nmax); ++n) std::printf(" %s", i128str(Ccols[H][n]).c_str());
    std::printf("\n");
  }
  return 0;
}
