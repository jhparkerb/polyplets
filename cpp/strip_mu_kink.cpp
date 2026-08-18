// strip_mu_kink.cpp — strip growth constants mu_H via power iteration on the
// CELL-AT-A-TIME kink-carry transfer, reusing the production kinkStageTransition
// (core/kink.h). One M(x)*w matvec = one column sweep: seed -> H per-cell stage
// transitions (weight x^placed, states MERGE) -> finalize. That is O(H*states)
// with no 2^H and no edge storage, so it reaches H well past strip_mu's ~13.
//
// canonMixed / labelInMixedState / kinkStageTransition are copied VERBATIM from
// core/kink.h (the "single source of truth") to avoid pulling in the heavy
// run/spill machinery kink.h includes. Correctness is gated by reproducing the
// exact mu_H from strip_mu / the fixed-height GF roots (mu_11..13 =
// 6.1158416, 6.2191246, 6.3060713).
//
// Usage: strip_mu_kink <Hmin> <Hmax>

#include <cstdint>
#include <cstdio>
#include <cmath>
#include <cstring>
#include <vector>
#include <unordered_map>
#include <chrono>

#include "core/signature.h"   // Sig, SIGMAX, canonicalizeSig
#include "core/transition.h"  // namespace s8 (find/unite)

// ---- copied verbatim from core/kink.h ----
inline void canonMixed(Sig& s, int H) {
  unsigned char map[256] = {0};
  unsigned char next = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char v = s.b[i];
    if (v == 0) continue;
    if (map[v] == 0) map[v] = next++;
    s.b[i] = map[v];
  }
  const unsigned char c = s.b[H + 2];
  if (c != 0) {
    if (map[c] == 0) map[c] = next++;
    s.b[H + 2] = map[c];
  }
}
inline bool labelInMixedState(const Sig& s, int H, unsigned char L) {
  for (int i = 0; i < H; ++i) if (s.b[i] == L) return true;
  return s.b[H + 2] == L;
}
template <class F>
inline void kinkStageTransition(const Sig& s, int H, int r, int ms, int maxn, F&& emit) {
  int uf[2 * SIGMAX];
  for (int occupy = 0; occupy < 2; ++occupy) {
    if (occupy && ms + 1 > maxn) break;
    Sig t = s; unsigned char newLabel = 0;
    if (occupy) {
      for (int i = 0; i < 2 * SIGMAX; ++i) uf[i] = i;
      auto uadd = [&](unsigned char L) { if (L) { int a = s8::find(uf, 0), b = s8::find(uf, L); if (a != b) uf[a] = b; } };
      if (r > 0) uadd(s.b[r - 1]);
      uadd(s.b[r]); uadd(s.b[H + 2]); if (r + 1 < H) uadd(s.b[r + 1]);
      const int root = s8::find(uf, 0); unsigned char fresh = 200;
      for (int i = 0; i < H; ++i) if (t.b[i] && s8::find(uf, t.b[i]) == root) t.b[i] = fresh;
      if (t.b[H + 2] && s8::find(uf, t.b[H + 2]) == root) t.b[H + 2] = fresh;
      newLabel = fresh;
    }
    const unsigned char outgoing = t.b[H + 2];
    t.b[H + 2] = t.b[r]; t.b[r] = occupy ? newLabel : 0;
    if (occupy) { if (r == 0) t.b[H] = 1; if (r == H - 1) t.b[H + 1] = 1; t.b[H + 3] = 1; }
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    canonMixed(t, H); emit(t, occupy ? 1 : 0);
  }
}
// ---- end copy ----

struct SigHash {
  size_t operator()(const Sig& s) const {
    size_t h = 1469598103934665603ULL;
    for (int i = 0; i < SIGMAX; ++i) { h ^= s.b[i]; h *= 1099511628211ULL; }
    return h;
  }
};
using Vec = std::unordered_map<Sig, double, SigHash>;

static const int BIG = 1 << 29;

// M(x) * w : one column sweep. w keyed by boundary Sig (flags zeroed).
Vec matvec(const Vec& w, int H, const double* xp) {
  Vec D; D.reserve(w.size() * 2);
  for (auto& kv : w) { Sig m = kv.first; m.b[H + 2] = 0; m.b[H + 3] = 0; D[m] += kv.second; }
  for (int r = 0; r < H; ++r) {
    Vec D2; D2.reserve(D.size() * 2);
    for (auto& kv : D) { double wt = kv.second;
      kinkStageTransition(kv.first, H, r, 0, BIG, [&](const Sig& t, int shift) { D2[t] += wt * xp[shift]; });
    }
    D.swap(D2);
  }
  Vec out; out.reserve(D.size());
  for (auto& kv : D) { const Sig& m = kv.first;
    if (!m.b[H + 3]) continue;                       // empty column = completion
    unsigned char outgoing = m.b[H + 2];
    Sig t = m; t.b[H + 2] = 0; t.b[H + 3] = 0;
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    canonicalizeSig(t.b, H); t.b[H] = 0; t.b[H + 1] = 0;   // <=H merge
    out[t] += kv.second;
  }
  return out;
}

int main(int argc, char** argv) {
  int Hmin = argc > 1 ? std::atoi(argv[1]) : 2;
  int Hmax = argc > 2 ? std::atoi(argv[2]) : 13;
  printf(" H |   states |   mu_H     | x*        | time\n");
  for (int H = Hmin; H <= Hmax; ++H) {
    auto t0 = std::chrono::steady_clock::now();
    Sig empty; std::memset(empty.b, 0, SIGMAX);
    Vec w0; w0[empty] = 1.0;

    auto rho = [&](double x, Vec& w) {
      double xp[2] = {1.0, x};
      double r = 0;
      for (int it = 0; it < 4000; ++it) {
        Vec w2 = matvec(w, H, xp);
        double s2 = 0, s1 = 0;
        for (auto& kv : w2) s2 += kv.second;
        for (auto& kv : w) s1 += kv.second;
        double rn = s2 / s1, inv = 1.0 / s2;
        for (auto& kv : w2) kv.second *= inv;
        w.swap(w2);
        if (it > 3 && std::fabs(rn - r) < 1e-11 * rn) { r = rn; break; }
        r = rn;
      }
      return r;
    };

    // bisect x for rho=1, warm-starting w
    Vec w = w0; for (int i = 0; i < 8; ++i) { Vec t = matvec(w, H, (double[]){1.0,0.25}); if (!t.empty()) w.swap(t); }
    double lo = 0.10, hi = 0.5;
    for (int it = 0; it < 55; ++it) {
      double mid = 0.5 * (lo + hi);
      Vec wm = w;
      if (rho(mid, wm) < 1.0) lo = mid; else hi = mid;
      if (hi - lo < 1e-13) break;
    }
    double xstar = 0.5 * (lo + hi), mu = 1.0 / xstar;
    // final state count at x*
    Vec wf = w0; rho(xstar, wf);
    double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("%2d | %8zu | %.7f | %.7f | %.1fs\n", H, wf.size(), mu, xstar, s);
    fflush(stdout);
  }
  return 0;
}
