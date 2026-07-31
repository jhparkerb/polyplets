// strip_mu_cert.cpp — EXACT (certificate-grade) lower bounds on the strip growth
// constants mu_H, upgrading the floating-point power-iteration values of
// cpp/strip_mu.cpp / cpp/strip_mu_kink.cpp to machine-checkable rationals.
//
// WHAT IS CERTIFIED.  mu_H = 1/x*, where x* is the radius of convergence of the
// height-<=H strip generating function = the x at which the king connectivity
// transfer operator M(x) has spectral radius 1 (rho is continuous and strictly
// increasing in x; see results/strip-growth-lambda-bounds.md).  Hence
//
//     rho(M(x)) >= 1  ==>  x >= x*  ==>  mu_H = 1/x* >= 1/x.
//
// So a rational x = den/num with a machine-checked rho(M(x)) >= 1 certifies
// mu_H >= num/den.  The rho >= 1 half is Collatz-Wielandt: for a nonnegative
// matrix A and ANY v >= 0, v != 0, with A v >= v componentwise, iterating gives
// A^k v >= v (A is monotone), so ||A^k||_inf >= v_i/||v||_inf for any i with
// v_i > 0, and rho(A) = lim ||A^k||^(1/k) >= 1.  No positivity of v and no
// irreducibility of A is needed for THIS direction -- the sharper two-sided
// Collatz-Wielandt formula (Horn & Johnson, Matrix Analysis 2nd ed., §8.1;
// Berman & Plemmons, Nonnegative Matrices in the Mathematical Sciences, Ch. 2)
// does need irreducibility, but we only ever use the lower half.
//
// RESTRICTION IS SAFE.  We only ever hold the operator's action on the finite
// support S of the converged eigenvector.  Mass flowing OUT of S is dropped,
// i.e. we certify the principal submatrix M_S, and rho(M_S) <= rho(M).  A
// PASS on M_S therefore implies a PASS on M.  Fail-closed by construction.
//
// ROUNDING IS ONE-SIDED.  One matvec = one column sweep: seed -> H per-cell
// kink stage transitions (weight x^placed) -> finalize.  With x = p/q the "no
// cell" branch has weight 1 and is copied exactly; the "cell placed" branch
// contributes floor(val*p/q) <= val*x.  Every stage is a nonnegative linear map
// (monotone), so the computed vector is <= the exact M_S(x) v componentwise, and
// a check that passes on the computed vector passes on the exact product.  All
// arithmetic is unsigned __int128 with an explicit 2^126 guard on every multiply
// and add: entries run to ~2^96 and p ~ 2^23, so int64 would overflow silently
// -- the guard makes that a loud FAIL, never a wrong PASS.
//
// The three kink functions below are copied VERBATIM from core/kink.h (the
// single source of truth), exactly as cpp/strip_mu_kink.cpp does, to avoid
// pulling in the run/spill machinery kink.h includes.
//
// Usage:
//   strip_mu_cert <Hmin> <Hmax> [--digits D] [--vbits B] [--log FILE]
//   strip_mu_cert --selftest
//
//   --digits D    denominator 10^D for the certified rational (default 7)
//   --vbits  B    largest integer vector entry is 2^B (default = the cap, 96 at
//                 7 digits; a larger explicit value is refused, not clamped)
//   --attempts N  cap on exact sweeps in the numerator search (default 128)
//   --log    F    append receipts to F (default results/strip_mu_certificates.log)
//
// HEADROOM.  The binding budget is vbits + log2(10^digits) < 126 (the hot product
// is val * 10^digits), plus a few bits because merges let an intermediate exceed
// the initial 2^vbits -- measured at 0.7 bits for H<=11, and 6 are reserved.
// The other budget is precision: the eigenvector's dynamic range grows steeply
// and unevenly with H (measured: 24 bits at H=8, 40 at H=9, 45 at H=10, 52 at
// H=11), and the SMALLEST entries must survive the flooring, which costs O(1)
// ulp (measured, by forcing H=10 to --vbits 55). When they do not, the run
// simply certifies a slightly smaller numerator -- the search below finds the
// largest one that passes and the receipt records it. It never widens a
// tolerance.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unordered_map>
#include <vector>

#include "core/signature.h"   // Sig, SIGMAX, canonicalizeSig
#include "core/transition.h"  // namespace s8 (find/unite)
#include "obs.h"              // obs::Reporter, provenance

// ---- copied verbatim from core/kink.h ----
inline void canonMixed(Sig& s, int H) {
  unsigned char map[256] = {0}; unsigned char next = 1;
  for (int i = 0; i < H; ++i) { const unsigned char v = s.b[i];
    if (v == 0) continue; if (map[v] == 0) map[v] = next++; s.b[i] = map[v]; }
  const unsigned char c = s.b[H + 2];
  if (c != 0) { if (map[c] == 0) map[c] = next++; s.b[H + 2] = map[c]; }
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

using u128 = unsigned __int128;

struct SigHash {
  size_t operator()(const Sig& s) const {
    size_t h = 1469598103934665603ULL;
    for (int i = 0; i < SIGMAX; ++i) { h ^= s.b[i]; h *= 1099511628211ULL; }
    return h;
  }
};
using Vec  = std::unordered_map<Sig, double, SigHash>;
using IVec = std::unordered_map<Sig, u128, SigHash>;

static const int BIG = 1 << 29;
// Every accumulator is checked against this before a multiply or an add. 2^126
// leaves a full bit of headroom below the unsigned __int128 range so the guard
// itself cannot wrap.
static const u128 LIMIT = (u128)1 << 126;

static std::string u128str(u128 v) {
  if (v == 0) return "0";
  char buf[64]; int i = 63; buf[i] = '\0';
  while (v) { buf[--i] = char('0' + int(v % 10)); v /= 10; }
  return std::string(buf + i);
}

static std::string sigHex(const Sig& s, int H) {
  static const char* hx = "0123456789abcdef";
  std::string r;
  for (int i = 0; i < H + 4; ++i) { r += hx[s.b[i] >> 4]; r += hx[s.b[i] & 15]; }
  return r;
}

// ───────────────────────── SHA-256 (vector checksum) ─────────────────────────
// Self-contained so the receipt's checksum needs no external library; the
// certificate's validity does not depend on it (it identifies WHICH vector was
// checked, so an independent re-verification can confirm it used the same one).
namespace sha {
struct Ctx {
  uint32_t h[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                   0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
  uint8_t buf[64]; size_t len = 0; uint64_t total = 0;
};
inline uint32_t rr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
inline void block(Ctx& c, const uint8_t* p) {
  static const uint32_t K[64] = {
    0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,
    0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
    0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,
    0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
    0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,
    0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
    0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,0xa2bfe8a1u,0xa81a664bu,
    0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
    0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,
    0x5b9cca4fu,0x682e6ff3u,0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,
    0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};
  uint32_t w[64];
  for (int i = 0; i < 16; ++i)
    w[i] = (uint32_t(p[4*i]) << 24) | (uint32_t(p[4*i+1]) << 16) |
           (uint32_t(p[4*i+2]) << 8) | uint32_t(p[4*i+3]);
  for (int i = 16; i < 64; ++i) {
    uint32_t s0 = rr(w[i-15],7) ^ rr(w[i-15],18) ^ (w[i-15] >> 3);
    uint32_t s1 = rr(w[i-2],17) ^ rr(w[i-2],19) ^ (w[i-2] >> 10);
    w[i] = w[i-16] + s0 + w[i-7] + s1;
  }
  uint32_t a=c.h[0],b=c.h[1],cc=c.h[2],d=c.h[3],e=c.h[4],f=c.h[5],g=c.h[6],hh=c.h[7];
  for (int i = 0; i < 64; ++i) {
    uint32_t S1 = rr(e,6) ^ rr(e,11) ^ rr(e,25);
    uint32_t ch = (e & f) ^ (~e & g);
    uint32_t t1 = hh + S1 + ch + K[i] + w[i];
    uint32_t S0 = rr(a,2) ^ rr(a,13) ^ rr(a,22);
    uint32_t mj = (a & b) ^ (a & cc) ^ (b & cc);
    uint32_t t2 = S0 + mj;
    hh=g; g=f; f=e; e=d+t1; d=cc; cc=b; b=a; a=t1+t2;
  }
  c.h[0]+=a; c.h[1]+=b; c.h[2]+=cc; c.h[3]+=d;
  c.h[4]+=e; c.h[5]+=f; c.h[6]+=g;  c.h[7]+=hh;
}
inline void update(Ctx& c, const void* data, size_t n) {
  const uint8_t* p = (const uint8_t*)data; c.total += n;
  while (n) {
    size_t take = std::min(n, size_t(64) - c.len);
    std::memcpy(c.buf + c.len, p, take);
    c.len += take; p += take; n -= take;
    if (c.len == 64) { block(c, c.buf); c.len = 0; }
  }
}
inline std::string hex(Ctx c) {
  uint64_t bits = c.total * 8;
  uint8_t pad = 0x80; update(c, &pad, 1);
  uint8_t z = 0; while (c.len != 56) update(c, &z, 1);
  uint8_t lenb[8];
  for (int i = 0; i < 8; ++i) lenb[i] = uint8_t(bits >> (56 - 8*i));
  update(c, lenb, 8);
  static const char* hx = "0123456789abcdef";
  std::string r;
  for (int i = 0; i < 8; ++i)
    for (int j = 3; j >= 0; --j) {
      uint8_t byte = uint8_t(c.h[i] >> (8*j));
      r += hx[byte >> 4]; r += hx[byte & 15];
    }
  return r;
}
}  // namespace sha

// Deterministic serialization of the certificate vector: states sorted by their
// raw SIGMAX bytes, each followed by its 16-byte little-endian value.
static std::string vectorChecksum(const IVec& v) {
  std::vector<const std::pair<const Sig, u128>*> ord;
  ord.reserve(v.size());
  for (auto& kv : v) ord.push_back(&kv);
  std::sort(ord.begin(), ord.end(), [](auto* a, auto* b) {
    return std::memcmp(a->first.b, b->first.b, SIGMAX) < 0;
  });
  sha::Ctx c;
  for (auto* kv : ord) {
    sha::update(c, kv->first.b, SIGMAX);
    uint8_t le[16];
    u128 x = kv->second;
    for (int i = 0; i < 16; ++i) { le[i] = uint8_t(x); x >>= 8; }
    sha::update(c, le, 16);
  }
  return sha::hex(c);
}

// ───────────────────────────── Phase 1: float ────────────────────────────────

// M(x) * w : one column sweep. w keyed by boundary Sig (flags zeroed).
// `keep` (optional) restricts the output to a fixed state set — the float
// iteration then converges the eigenpair of the SAME principal submatrix M_S
// the exact phase certifies, so the two phases agree on what is being bounded.
static Vec matvecF(const Vec& w, int H, const double* xp, const Vec* keep) {
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
    if (keep && !keep->count(t)) continue;
    out[t] += kv.second;
  }
  return out;
}

// Power-iterate M(x) in place; returns the dominant eigenvalue estimate.
static double rhoF(double x, Vec& w, int H, const Vec* keep, int maxIt = 4000) {
  double xp[2] = {1.0, x};
  double r = 0;
  for (int it = 0; it < maxIt; ++it) {
    Vec w2 = matvecF(w, H, xp, keep);
    if (w2.empty()) return 0.0;
    double s2 = 0, s1 = 0;
    for (auto& kv : w2) s2 += kv.second;
    for (auto& kv : w) s1 += kv.second;
    double rn = s2 / s1, inv = 1.0 / s2;
    for (auto& kv : w2) kv.second *= inv;
    w.swap(w2);
    if (it > 3 && std::fabs(rn - r) < 1e-13 * rn) { r = rn; break; }
    r = rn;
  }
  return r;
}

// ───────────────────────────── Phase 2: exact ────────────────────────────────

// floor-rounded M_S(p/q) * v, restricted to the keys of v. Returns false (and
// leaves `out` unusable) if any accumulator would exceed LIMIT — fail-closed:
// the caller must treat an overflow as a FAILED certificate, never a pass.
//
// Weights are applied PER TERM: the "no cell placed" branch carries weight 1 and
// is copied exactly (no rounding at all), the "cell placed" branch carries
// x = p/q and contributes floor(val*p/q). Two reasons over the obvious
// "accumulate val*q / val*p, then divide the stage by q":
//   * headroom — the accumulator never holds a factor of q (~2^27 at 7 digits),
//     so the vector can carry ~27 more bits, which is exactly the precision the
//     smallest eigenvector entries need at large H;
//   * half the terms become exact, so the accumulated flooring loss is smaller.
// floor(val*p/q) <= val*p/q and a sum of floors <= the floor of the sum, so the
// result is still <= the exact M_S(p/q) v componentwise. `maxAcc` reports the
// largest value ever held, so a run can show how much of the 2^126 it used.
static bool matvecExact(const IVec& v, int H, u128 p, u128 q, IVec& out,
                        u128& maxAcc) {
  maxAcc = 0;
  IVec D; D.reserve(v.size() * 2);
  for (auto& kv : v) {
    Sig m = kv.first; m.b[H + 2] = 0; m.b[H + 3] = 0;
    u128& a = D[m];
    if (a > LIMIT - kv.second) return false;
    a += kv.second;
    if (a > maxAcc) maxAcc = a;
  }
  for (int r = 0; r < H; ++r) {
    IVec D2; D2.reserve(D.size() * 2);
    bool ok = true;
    for (auto& kv : D) {
      const u128 val = kv.second;
      kinkStageTransition(kv.first, H, r, 0, BIG, [&](const Sig& t, int shift) {
        u128 term;
        if (shift) {
          if (val > LIMIT / p) { ok = false; return; }
          term = (val * p) / q;                  // DOWNWARD: floor(val*x)
        } else {
          term = val;                            // weight 1: exact
        }
        u128& a = D2[t];
        if (a > LIMIT - term) { ok = false; return; }
        a += term;
        if (a > maxAcc) maxAcc = a;
      });
      if (!ok) return false;
    }
    D.swap(D2);
  }
  out.clear(); out.reserve(v.size());
  for (auto& kv : D) {
    const Sig& m = kv.first;
    if (!m.b[H + 3]) continue;
    unsigned char outgoing = m.b[H + 2];
    Sig t = m; t.b[H + 2] = 0; t.b[H + 3] = 0;
    if (outgoing != 0 && !labelInMixedState(t, H, outgoing)) continue;
    canonicalizeSig(t.b, H); t.b[H] = 0; t.b[H + 1] = 0;
    if (!v.count(t)) continue;   // leaving S drops mass: rho(M_S) <= rho(M)
    u128& a = out[t];
    if (a > LIMIT - kv.second) return false;
    a += kv.second;
  }
  return true;
}

struct CheckResult {
  bool pass = false;
  bool overflow = false;
  size_t failures = 0;
  std::string firstBad;     // hex signature of the first offending state
  u128 firstBadLhs = 0, firstBadRhs = 0;
  double minRatio = 0.0;    // min_i (M v)_i / v_i over v_i > 0 (diagnostic only)
  double accBits = 0.0;     // log2 of the largest __int128 value ever held
};

// The certificate check: (M_S(p/q) v)_i >= v_i for EVERY i in S, in exact
// integer arithmetic. Any single failure fails the whole certificate.
static CheckResult checkCert(const IVec& v, int H, u128 p, u128 q) {
  CheckResult R;
  IVec out;
  u128 maxAcc = 0;
  if (!matvecExact(v, H, p, q, out, maxAcc)) { R.overflow = true; return R; }
  R.accBits = maxAcc ? std::log2((double)maxAcc) : 0.0;
  double mr = 1e308;
  size_t nonzero = 0;
  for (auto& kv : v) {
    const u128 want = kv.second;
    if (want == 0) continue;   // 0 <= anything; harmless, contributes nothing
    ++nonzero;
    auto it = out.find(kv.first);
    const u128 got = (it == out.end()) ? (u128)0 : it->second;
    mr = std::min(mr, (double)got / (double)want);
    if (got < want) {
      if (R.failures == 0) {
        R.firstBad = sigHex(kv.first, H);
        R.firstBadLhs = got; R.firstBadRhs = want;
      }
      ++R.failures;
    }
  }
  R.minRatio = (mr > 1e307) ? 0.0 : mr;
  // Collatz-Wielandt needs v != 0. An all-zero v satisfies "A v >= v" vacuously
  // and would otherwise be reported as a PASS — refuse it outright.
  R.pass = (R.failures == 0 && nonzero > 0);
  return R;
}

// Scale the float eigenvector to positive integers with the largest entry at
// 2^vbits. Entries whose double falls below 1 quantize to 0; that is SAFE (the
// Collatz-Wielandt test needs only v >= 0, v != 0) and is never silently
// tolerated on the inequality side — every state is still checked.
static IVec quantize(const Vec& w, int vbits, double& wmin, double& wmax) {
  wmax = 0; wmin = 1e308;
  for (auto& kv : w) {
    if (kv.second > wmax) wmax = kv.second;
    if (kv.second > 0 && kv.second < wmin) wmin = kv.second;
  }
  IVec v; v.reserve(w.size() * 2);
  const double scale = std::ldexp(1.0, vbits) / wmax;
  for (auto& kv : w) v[kv.first] = (u128)(kv.second * scale);
  return v;
}

// ───────────────────────────────── driver ────────────────────────────────────

struct CertOut {
  int H = 0;
  long long num = 0, den = 0;
  size_t states = 0;
  int attempts = 0;
  bool pass = false;
  double muFloat = 0, minRatio = 0, wall = 0, rangeBits = 0, accBits = 0;
  std::string checksum, firstBad;
};

static u128 ipow10(int d) { u128 r = 1; for (int i = 0; i < d; ++i) r *= 10; return r; }

// One H: float power iteration -> rational candidate -> exact check, stepping
// the numerator down until it passes (or the budget runs out).
static CertOut certifyH(int H, int digits, int vbits, int maxAttempts) {
  CertOut C; C.H = H;
  auto t0 = std::chrono::steady_clock::now();
  obs::Reporter rep("stripmucert-H" + std::to_string(H), 0,
                    "H=" + std::to_string(H) + " digits=" + std::to_string(digits) +
                    " vbits=" + std::to_string(vbits));

  Sig empty; std::memset(empty.b, 0, SIGMAX);
  Vec w0; w0[empty] = 1.0;

  // bisect x for rho(M(x)) = 1, warm-starting the eigenvector (same schedule as
  // the validated cpp/strip_mu_kink.cpp, so the float mu_H reproduces the ladder)
  Vec w = w0;
  for (int i = 0; i < 8; ++i) {
    double xp[2] = {1.0, 0.25};
    Vec t = matvecF(w, H, xp, nullptr);
    if (!t.empty()) w.swap(t);
  }
  double lo = 0.10, hi = 0.5;
  for (int it = 0; it < 55; ++it) {
    double mid = 0.5 * (lo + hi);
    Vec wm = w;
    if (rhoF(mid, wm, H, nullptr) < 1.0) lo = mid; else hi = mid;
    if (hi - lo < 1e-13) break;
    rep.beat(it, "phase=bisect");
  }
  const double xstar = 0.5 * (lo + hi);
  C.muFloat = 1.0 / xstar;

  const u128 den = ipow10(digits);
  const u128 num0 = (u128)std::floor(C.muFloat * std::pow(10.0, digits));

  // ONE eigenvector for the whole search. Lowering num moves x by parts in 1e8,
  // far below anything the exact check can see, so re-polishing per candidate
  // would only burn sweeps — and a single fixed v makes the receipt's checksum
  // unambiguous (it is the vector that was actually checked).
  Vec wf = w;
  rhoF((double)(long double)den / (double)(long double)num0, wf, H, nullptr);
  double wmin = 0, wmax = 0;
  IVec v = quantize(wf, vbits, wmin, wmax);
  C.states = v.size();
  C.rangeBits = std::log2(wmax / wmin);

  // The check is MONOTONE in num: smaller num means larger x = den/num, every
  // entry of M(x) is nondecreasing in x, so (M v) only grows. So instead of
  // stepping down one at a time (hundreds of sweeps at large H), bracket by
  // doubling and then bisect — ~2*log2(gap) sweeps.
  int sweeps = 0;
  auto tryNum = [&](u128 n) -> bool {
    ++sweeps; C.attempts = sweeps;
    CheckResult R = checkCert(v, H, den, n);   // x = den/n: stage weight 1 or x
    C.accBits = R.accBits;
    if (!R.pass) { C.firstBad = R.firstBad; }
    C.minRatio = R.minRatio;
    std::fprintf(stderr,
                 "event=attempt job=stripmucert-H%d sweep=%d num=%s den=%s "
                 "states=%zu vrange_bits=%.1f acc_bits=%.1f fail=%zu "
                 "min_ratio=%.9f overflow=%d\n",
                 H, sweeps, u128str(n).c_str(), u128str(den).c_str(), v.size(),
                 C.rangeBits, R.accBits, R.failures, R.minRatio, R.overflow ? 1 : 0);
    std::fflush(stderr);
    rep.beat(sweeps, "phase=certify");   // throttled; the attempt line is per-sweep
    return R.pass;
  };

  C.den = (long long)den; C.num = (long long)num0;
  if (tryNum(num0)) {
    C.pass = true;
  } else {
    // bracket: hi always fails, lo (once found) always passes
    u128 hi = num0, lo = 0; bool bracketed = false;
    for (u128 d = 1; d <= num0 && sweeps < maxAttempts; d *= 2) {
      if (tryNum(num0 - d)) { lo = num0 - d; bracketed = true; break; }
      hi = num0 - d;
    }
    while (bracketed && lo + 1 < hi && sweeps < maxAttempts) {
      const u128 mid = lo + (hi - lo) / 2;
      if (tryNum(mid)) lo = mid; else hi = mid;
    }
    // Re-verify the winning numerator last, so the receipt's min_ratio, acc_bits
    // and PASS all describe the rational actually certified — not some probe.
    if (bracketed) { C.num = (long long)lo; C.pass = tryNum(lo); }
  }
  if (C.pass) C.checksum = vectorChecksum(v);

  C.wall = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  rep.done("H=" + std::to_string(H) + " result=" + (C.pass ? "PASS" : "FAIL") +
           " num=" + std::to_string(C.num) + " den=" + std::to_string(C.den) +
           " states=" + std::to_string(C.states));
  return C;
}

static void appendReceipt(const char* path, const CertOut& C, int digits, int vbits) {
  FILE* f = std::fopen(path, "a");
  if (!f) { std::fprintf(stderr, "event=error msg=\"cannot open receipt %s\"\n", path); return; }
  std::fprintf(f,
      "event=certificate t=%s git=%s built=%s host=%s H=%d result=%s "
      "num=%lld den=%lld mu_lower=%.*f mu_float=%.9f states=%zu digits=%d "
      "vbits=%d vrange_bits=%.1f acc_bits=%.1f attempts=%d min_ratio=%.9f "
      "checksum=sha256:%s wall_s=%.1f\n",
      obs::now_iso().c_str(), GIT_REV, BUILD_TIME, obs::host().c_str(), C.H,
      C.pass ? "PASS" : "FAIL", C.num, C.den, digits, (double)C.num / (double)C.den,
      C.muFloat, C.states, digits, vbits, C.rangeBits, C.accBits, C.attempts,
      C.minRatio, C.checksum.empty() ? "-" : C.checksum.c_str(), C.wall);
  std::fclose(f);
}

// ─────────────────────────────── self-test ───────────────────────────────────
// RED-first: these must be able to FAIL. mu_2 = 1+sqrt(2) = 2.41421356..., so
// 24142/10000 is a true lower bound (must PASS) and 24143/10000 is not (must
// FAIL). Then a deliberately corrupted vector must be rejected with an index.
static int selftest() {
  const int H = 2, vbits = 80;
  int bad = 0;

  // Converge the eigenvector at x = 1/2.4142, just OUTSIDE the true radius
  // 1/(1+sqrt 2), so rho > 1 and the true claim has margin to spare.
  Sig empty; std::memset(empty.b, 0, SIGMAX);
  Vec w; w[empty] = 1.0;
  rhoF(10000.0 / 24142.0, w, H, nullptr);

  double wmin, wmax;
  IVec v = quantize(w, vbits, wmin, wmax);
  std::printf("selftest: H=2 states=%zu vrange_bits=%.1f\n", v.size(), std::log2(wmax / wmin));

  CheckResult a = checkCert(v, H, 10000, 24142);
  std::printf("selftest A: mu_2 >= 24142/10000 -> %s (min_ratio=%.9f, expect PASS)\n",
              a.pass ? "PASS" : "FAIL", a.minRatio);
  if (!a.pass) { ++bad; std::printf("  UNEXPECTED: first bad state %s\n", a.firstBad.c_str()); }

  // 2.4143 > 1+sqrt(2): the checker must reject it at the SAME vector.
  Vec w2 = w; rhoF(10000.0 / 24143.0, w2, H, nullptr);
  IVec v2 = quantize(w2, vbits, wmin, wmax);
  CheckResult b = checkCert(v2, H, 10000, 24143);
  std::printf("selftest B: mu_2 >= 24143/10000 -> %s (min_ratio=%.9f, expect FAIL)\n",
              b.pass ? "PASS" : "FAIL", b.minRatio);
  if (b.pass) { ++bad; std::printf("  UNEXPECTED: an over-claim was certified\n"); }
  else std::printf("  rejected at state %s: lhs=%s < rhs=%s\n", b.firstBad.c_str(),
                   u128str(b.firstBadLhs).c_str(), u128str(b.firstBadRhs).c_str());

  // Corrupt one entry of a PASSING vector: the checker must notice.
  IVec vp = v;
  {
    const Sig* worst = nullptr; u128 best = 0;
    for (auto& kv : vp) if (kv.second > best) { best = kv.second; worst = &kv.first; }
    if (worst) vp[*worst] = best << 30;
  }
  CheckResult c = checkCert(vp, H, 10000, 24142);
  std::printf("selftest C: perturbed vector -> %s (expect FAIL)\n", c.pass ? "PASS" : "FAIL");
  if (c.pass) { ++bad; std::printf("  UNEXPECTED: corruption not detected\n"); }
  else std::printf("  rejected at state %s: lhs=%s < rhs=%s (%zu failing states)\n",
                   c.firstBad.c_str(), u128str(c.firstBadLhs).c_str(),
                   u128str(c.firstBadRhs).c_str(), c.failures);

  // The all-zero vector satisfies "A v >= v" vacuously for ANY claim; if the
  // checker accepted it, every rational would certify. It must refuse.
  IVec vz = v;
  for (auto& kv : vz) kv.second = 0;
  CheckResult d = checkCert(vz, H, 10000, 24142);
  std::printf("selftest D: all-zero vector -> %s (expect FAIL)\n", d.pass ? "PASS" : "FAIL");
  if (d.pass) { ++bad; std::printf("  UNEXPECTED: a vacuous certificate was accepted\n"); }

  std::printf("selftest: %s\n", bad == 0 ? "ALL OK" : "FAILURES");
  return bad == 0 ? 0 : 1;
}

int main(int argc, char** argv) {
  int Hmin = 2, Hmax = 11, digits = 7, vbits = 0, maxAttempts = 128;
  const char* logPath = "results/strip_mu_certificates.log";
  bool doSelftest = false;
  std::vector<const char*> pos;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--selftest") doSelftest = true;
    else if (a == "--digits" && i + 1 < argc) digits = std::atoi(argv[++i]);
    else if (a == "--vbits" && i + 1 < argc) vbits = std::atoi(argv[++i]);
    else if (a == "--attempts" && i + 1 < argc) maxAttempts = std::atoi(argv[++i]);
    else if (a == "--log" && i + 1 < argc) logPath = argv[++i];
    else if (a.size() && a[0] == '-') {
      std::fprintf(stderr, "unknown option %s\n", a.c_str());
      return 2;                                   // fail closed on a bad flag
    } else pos.push_back(argv[i]);
  }
  if (doSelftest) return selftest();
  if (pos.size() >= 1) Hmin = std::atoi(pos[0]);
  if (pos.size() >= 2) Hmax = std::atoi(pos[1]);
  // H >= 2 (H=1 is the trivial single-row strip, mu_1 = 1); H+4 bytes must fit
  // the Sig, and the mixed state uses b[H+3]. Refuse rather than corrupt state.
  if (Hmin < 2 || Hmax < Hmin || Hmax > SIGMAX - 4) {
    std::fprintf(stderr, "H range out of bounds (2..%d)\n", SIGMAX - 4);
    return 2;
  }
  if (digits < 1 || digits > 15) { std::fprintf(stderr, "--digits out of range\n"); return 2; }
  if (maxAttempts < 1) { std::fprintf(stderr, "--attempts must be >= 1\n"); return 2; }
  // The hot product is val * 10^digits, and merges let an intermediate exceed
  // the initial 2^vbits; reserve 6 bits for that. Auto-size, and REFUSE an
  // explicit --vbits above the cap rather than run into the overflow guard.
  const int cap = 126 - int(std::ceil(digits * std::log2(10.0))) - 6;
  if (vbits == 0) vbits = cap;
  if (vbits < 8 || vbits > cap) {
    std::fprintf(stderr, "--vbits out of range (8..%d for --digits %d)\n", cap, digits);
    return 2;
  }

  std::printf(" H |   states |  mu_H (float) | certified mu_H >=      | ratio | sweeps | time\n");
  std::fflush(stdout);
  int rc = 0;
  for (int H = Hmin; H <= Hmax; ++H) {
    CertOut C = certifyH(H, digits, vbits, maxAttempts);
    appendReceipt(logPath, C, digits, vbits);
    if (C.pass) {
      std::printf("%2d | %8zu | %13.7f | %10lld/%-10lld | %.4f | %8d | %.1fs\n",
                  C.H, C.states, C.muFloat, C.num, C.den, C.minRatio, C.attempts, C.wall);
    } else {
      std::printf("%2d | %8zu | %13.7f | FAIL (last %lld/%lld, bad state %s) | - | %8d | %.1fs\n",
                  C.H, C.states, C.muFloat, C.num, C.den, C.firstBad.c_str(), C.attempts, C.wall);
      rc = 1;                                     // fail closed
    }
    std::fflush(stdout);
  }
  return rc;
}
