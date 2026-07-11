// strip_mu8.cpp — strip growth constants mu_H via power iteration on the
// VALIDATED tma square-8 king transition, using the viable-mask enumerator to
// skip the 2^H brute force that caps strip_mu at H~13.
//
// mu_H = 1/x*, x* = radius of convergence of the height-H strip = the x where
// the connectivity transfer matrix M(x) has spectral radius 1. States are the
// king-connectivity boundary signatures (top/bottom flags zeroed -> the "<=H"
// transfer matrix, whose dominant eigenvalue is still mu_H). Transitions:
// stepColumnSquare8 over the stranding-only viable masks (no area/reach prune).
//
// Validation target (must reproduce, from strip_mu / fixed-height GF roots):
//   mu_11=6.1158416  mu_12=6.2191246  mu_13=6.3060713
//
// Usage: strip_mu8 <Hmin> <Hmax>

#include <cstdint>
#include <cstdio>
#include <cmath>
#include <vector>
#include <queue>
#include <unordered_map>
#include <chrono>

#include "tma/signature.h"
#include "tma/transition_square8.h"

struct SigHash {
  size_t operator()(const Sig& s) const {
    size_t h = 1469598103934665603ULL;
    for (int i = 0; i < SIGMAX; ++i) { h ^= s.b[i]; h *= 1099511628211ULL; }
    return h;
  }
};

// stranding-only viable masks (no area/reach prune): call viableRec with a large
// budget and topBase=true so only the component-coverage prune fires.
template <class F>
inline void forEachGrowthMask(const Sig& old, int H, F&& fn) {
  std::uint32_t all = 0, rowSup[SIGMAX], sufSup[SIGMAX + 1];
  for (int i = 0; i < H; ++i) if (old.b[i]) all |= 1u << old.b[i];
  for (int r = 0; r < H; ++r) {
    std::uint32_t s = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && old.b[rr]) s |= 1u << old.b[rr];
    rowSup[r] = s;
  }
  sufSup[H] = 0;
  for (int r = H - 1; r >= 0; --r) sufSup[r] = sufSup[r + 1] | rowSup[r];
  s8::viableRec(0, H, 0u, 0, 0u, all, rowSup, sufSup, /*budget*/ H, /*topBase*/ true, fn);
}

int main(int argc, char** argv) {
  int Hmin = argc > 1 ? std::atoi(argv[1]) : 2;
  int Hmax = argc > 2 ? std::atoi(argv[2]) : 13;

  printf(" H |   states |     edges |   mu_H     | x*        | time\n");
  for (int H = Hmin; H <= Hmax; ++H) {
    if (H > 30) { printf("H<=30\n"); break; }
    auto t0 = std::chrono::steady_clock::now();

    std::unordered_map<Sig, int, SigHash> id;
    std::vector<Sig> states;
    std::queue<int> q;
    auto zeroFlags = [&](Sig& s) { s.b[H] = 0; s.b[H + 1] = 0; };
    auto intern = [&](Sig s) -> int {
      zeroFlags(s);
      auto it = id.find(s);
      if (it != id.end()) return it->second;
      int k = states.size(); id.emplace(s, k); states.push_back(s); q.push(k); return k;
    };

    Sig empty; std::memset(empty.b, 0, SIGMAX);
    int full = (1 << H) - 1;
    for (int S = 1; S <= full; ++S) { Sig out; if (stepColumnSquare8(empty, H, (unsigned)S, out) == Outcome::Alive) intern(out); }

    std::vector<std::vector<std::pair<int,int>>> edges;  // per src: (dst, add)
    while (!q.empty()) {
      int si = q.front(); q.pop();
      Sig st = states[si];
      if ((int)edges.size() <= si) edges.resize(si + 1);
      forEachGrowthMask(st, H, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(st, H, mask, out) != Outcome::Alive) return;
        int di = intern(out);
        edges[si].push_back({di, __builtin_popcount(mask)});
      });
    }
    int nst = states.size();
    edges.resize(nst);
    // CSR
    std::vector<long long> rs(nst + 1, 0);
    long long ne = 0; for (int i = 0; i < nst; ++i) ne += edges[i].size();
    for (int i = 0; i < nst; ++i) rs[i + 1] = rs[i] + (long long)edges[i].size();
    std::vector<int> col(ne); std::vector<uint8_t> add(ne);
    for (int i = 0; i < nst; ++i) { long long p = rs[i];
      for (auto& e : edges[i]) { col[p] = e.first; add[p] = (uint8_t)e.second; ++p; }
      std::vector<std::pair<int,int>>().swap(edges[i]); }

    std::vector<double> w(nst, 1.0), w2(nst, 0.0);
    auto rho = [&](double x) {
      double xp[33]; xp[0] = 1; for (int k = 1; k <= H; ++k) xp[k] = xp[k-1]*x;
      double r = 0;
      for (int it = 0; it < 20000; ++it) {
        for (int j = 0; j < nst; ++j) w2[j] = 0.0;
        for (int i = 0; i < nst; ++i) { double wi = w[i]; if (wi == 0) continue;
          for (long long p = rs[i]; p < rs[i+1]; ++p) w2[col[p]] += xp[add[p]] * wi; }
        double s2 = 0, s1 = 0;
        for (int j = 0; j < nst; ++j) { s2 += w2[j]; s1 += w[j]; }
        double rn = s2 / s1, inv = 1.0 / s2;
        for (int j = 0; j < nst; ++j) w[j] = w2[j] * inv;
        if (it > 3 && std::fabs(rn - r) < 1e-11 * rn) { r = rn; break; }
        r = rn;
      }
      return r;
    };

    double lo = 0.10, hi = 0.5;
    for (int it = 0; it < 60; ++it) {
      double mid = 0.5 * (lo + hi);
      if (rho(mid) < 1.0) lo = mid; else hi = mid;
      if (hi - lo < 1e-13) break;
    }
    double xstar = 0.5 * (lo + hi), mu = 1.0 / xstar;
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("%2d | %8d | %9lld | %.7f | %.7f | %.1fs\n", H, nst, ne, mu, xstar, s);
    fflush(stdout);
  }
  return 0;
}
