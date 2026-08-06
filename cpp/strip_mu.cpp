// strip_mu.cpp — strip growth constants mu_H by power iteration.
//
// mu_H = dominant strip growth constant of height-H polyplets = 1/x*, where x*
// is the radius of convergence of C_H(x), i.e. the x at which the connectivity
// transfer matrix M(x) has spectral radius 1. Each mu_H < lambda (rigorously),
// mu_H -> lambda. So the mu_H are a monotone lower-bound ladder for the polyplet
// growth constant, with EXACT-strip values (no count-ratio under-convergence).
//
// Method: enumerate reachable frontier states (BFS under step(), reusing the
// verified strip_tm transfer logic), build the weighted edge list, then for a
// given x apply M(x) by power iteration to get spectral radius rho(x); bisect x
// for rho(x)=1; report mu_H = 1/x*.
//
// Validation: reproduces the mu_H from the fixed-height GF roots to all 7
// decimals it prints (~8 significant digits), which is the resolution of
// that comparison and not a claim about further digits (this engine is double
// precision, converges rho to 1e-11 and x* to 1e-13). The same iteration
// recorded at 10 digits by strip_mu_cert agrees to 9-10. Measured in
// experiments/mu_H_precision_audit.py.
// (H<=11: 2.4142, 3.4437, 4.1823, 4.7178, 5.1153, 5.4178, 5.6534, 5.8405,
//  5.9917, 6.1158).
//
// Usage: strip_mu <Hmin> <Hmax>

#include <cstdint>
#include <cstdio>
#include <cmath>
#include <vector>
#include <unordered_map>
#include <queue>
#include <chrono>

using u64 = uint64_t;

struct Engine {
  int H;
  static inline int lab(u64 st, int r) { return int((st >> (4 * r)) & 0xF); }

  // Place column S over frontier `st`; returns false if a prev component buried.
  bool step(u64 st, int S, u64& out) {
    int occ[16];
    for (int r = 0; r < H; ++r) occ[r] = lab(st, r);
    int par[32];
    for (int i = 0; i < H + 9; ++i) par[i] = i;
    auto find = [&](int x) { while (par[x] != x) { par[x] = par[par[x]]; x = par[x]; } return x; };
    auto uni = [&](int a, int b) { int ra = find(a), rb = find(b); if (ra != rb) par[ra] = rb; };
    int nprev = 0; bool seen[9] = {false};
    for (int r = 0; r < H; ++r) if (occ[r] && !seen[occ[r]]) { seen[occ[r]] = true; ++nprev; }
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      if (r + 1 < H && ((S >> (r + 1)) & 1)) uni(r, r + 1);
    }
    bool touched[9] = {false}; int ntouch = 0;
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      for (int dr = -1; dr <= 1; ++dr) {
        int rr = r + dr; if (rr < 0 || rr >= H) continue;
        int g = occ[rr];
        if (g) { if (!touched[g]) { touched[g] = true; ++ntouch; } uni(r, H + g); }
      }
    }
    if (ntouch < nprev) return false;
    int rootlab[32]; for (int i = 0; i < H + 9; ++i) rootlab[i] = 0;
    int next = 1; u64 ns = 0;
    for (int r = 0; r < H; ++r) {
      if (!((S >> r) & 1)) continue;
      int root = find(r);
      if (!rootlab[root]) rootlab[root] = next++;
      ns |= (u64)rootlab[root] << (4 * r);
    }
    out = ns; return true;
  }

  u64 startState(int S) {  // single column: label vertical runs 1,2,...
    u64 ns = 0; int next = 1, r = 0;
    while (r < H) {
      if ((S >> r) & 1) { int L = next++; while (r < H && ((S >> r) & 1)) { ns |= (u64)L << (4 * r); ++r; } }
      else ++r;
    }
    return ns;
  }
};

int main(int argc, char** argv) {
  int Hmin = argc > 1 ? std::atoi(argv[1]) : 2;
  int Hmax = argc > 2 ? std::atoi(argv[2]) : 12;

  printf(" H |   states |   mu_H     | x*       | time\n");
  for (int H = Hmin; H <= Hmax; ++H) {
    if (H > 15) { printf("H<=15 (4-bit packing)\n"); break; }
    auto t0 = std::chrono::steady_clock::now();
    Engine e; e.H = H;
    int full = (1 << H) - 1;

    // BFS enumerate states + record weighted edges (src -> dst, add cells)
    std::unordered_map<u64, int> id;
    std::vector<u64> states;
    std::queue<u64> q;
    auto intern = [&](u64 s) -> int {
      auto it = id.find(s);
      if (it != id.end()) return it->second;
      int k = states.size(); id[s] = k; states.push_back(s); q.push(s); return k;
    };
    for (int S = 1; S <= full; ++S) intern(e.startState(S));
    std::vector<std::vector<std::pair<int,int>>> edges;  // per src: (dst, add)
    edges.reserve(1 << 16);
    while (!q.empty()) {
      u64 st = q.front(); q.pop();
      int si = id[st];
      if ((int)edges.size() <= si) edges.resize(si + 1);
      for (int S = 1; S <= full; ++S) {
        u64 ns;
        if (!e.step(st, S, ns)) continue;
        int di = intern(ns);
        edges[si].push_back({di, __builtin_popcount(S)});
      }
    }
    int nst = states.size();
    edges.resize(nst);
    // flatten to CSR by source for cache locality
    std::vector<long long> rs(nst + 1, 0);
    for (int i = 0; i < nst; ++i) rs[i + 1] = rs[i] + (long long)edges[i].size();
    std::vector<int> col(rs[nst]); std::vector<uint8_t> add(rs[nst]);
    for (int i = 0; i < nst; ++i) { long long p = rs[i];
      for (auto& ed : edges[i]) { col[p] = ed.first; add[p] = (uint8_t)ed.second; ++p; }
      std::vector<std::pair<int,int>>().swap(edges[i]); }

    // warm-started power iteration; w persists across rho() calls (eigenvector
    // moves slowly with x), so after the first solve each rho takes few iters.
    std::vector<double> w(nst, 1.0), w2(nst, 0.0);
    auto rho = [&](double x) {
      double xp[17]; xp[0] = 1; for (int k = 1; k <= H; ++k) xp[k] = xp[k-1]*x;
      double r = 0;
      for (int it = 0; it < 20000; ++it) {
        #pragma omp parallel for schedule(static)
        for (int j = 0; j < nst; ++j) w2[j] = 0.0;
        // scatter with per-thread private accumulation avoided: use atomic-free
        // gather is not available (edges are by source), so do serial scatter in
        // chunks — matvec is memory-bound; OpenMP the zero/normalize only.
        for (int i = 0; i < nst; ++i) { double wi = w[i]; if (wi == 0) continue;
          for (long long p = rs[i]; p < rs[i+1]; ++p) w2[col[p]] += xp[add[p]] * wi; }
        double s2 = 0, s1 = 0;
        #pragma omp parallel for reduction(+:s2,s1) schedule(static)
        for (int j = 0; j < nst; ++j) { s2 += w2[j]; s1 += w[j]; }
        double rn = s2 / s1, inv = 1.0 / s2;
        #pragma omp parallel for schedule(static)
        for (int j = 0; j < nst; ++j) w[j] = w2[j] * inv;
        if (it > 3 && std::fabs(rn - r) < 1e-11 * rn) { r = rn; break; }
        r = rn;
      }
      return r;
    };

    // bisect x for rho(x)=1 (rho increasing in x)
    double lo = 0.12, hi = 0.5;
    for (int it = 0; it < 60; ++it) {
      double mid = 0.5 * (lo + hi);
      if (rho(mid) < 1.0) lo = mid; else hi = mid;
      if (hi - lo < 1e-13) break;
    }
    double xstar = 0.5 * (lo + hi), mu = 1.0 / xstar;
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("%2d | %8d | %.7f | %.7f | %.1fs\n", H, nst, mu, xstar, s);
    fflush(stdout);
  }
  return 0;
}
