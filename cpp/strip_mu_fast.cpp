// strip_mu_fast.cpp — the indexed-array strip growth-constant engine.
//
// Same mathematics as cpp/strip_mu_kink.cpp (power iteration on the
// cell-at-a-time kink-carry transfer, bisecting x for rho(M(x)) = 1, mu_H =
// 1/x*), with the hash-map hot path replaced by the frozen per-stage sparse
// operators of cpp/strip_stage_ops.h. The kink transition is enumerated ONCE
// per H and reduced to two int32 successor arrays per stage; every subsequent
// matvec is a flat indexed scatter. The old engine stays in the tree, built and
// gated, as the cross-check (make gate-strip-fast).
//
// The kernel is shared with the certificate arithmetic by design: --verify runs
// the exact unsigned-__int128 Collatz-Wielandt check of cpp/strip_mu_cert.cpp
// over the SAME frozen operators, term for term, so a certificate tool adopting
// strip_stage_ops.h changes only which weight policy it hands applyOps.
//
// Usage:
//   strip_mu_fast <Hmin> <Hmax>                 mu_H ladder (default 2..11)
//   strip_mu_fast --ops <Hmin> <Hmax>           table sizes / memory only
//   strip_mu_fast --verify <H> <num> <den>      exact mu_H >= num/den check
//   strip_mu_fast --bench <Hmin> <Hmax> [--iters N]   matvec throughput probe
//   strip_mu_fast --selftest                    RED-first gate

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "strip_stage_ops.h"
#include "obs.h"

using strip::StageOps;
using u128 = unsigned __int128;

static std::string u128str(u128 v) {
  if (v == 0) return "0";
  char buf[64]; int i = 63; buf[i] = '\0';
  while (v) { buf[--i] = char('0' + int(v % 10)); v /= 10; }
  return std::string(buf + i);
}

// ───────────────────────────── float phase ───────────────────────────────────

struct Work {                       // scratch reused across every matvec
  std::vector<double> a, b, next;
};

// Matvec tally, so the H=15/16 wall projection is (matvecs) x (sum|S_r|) x
// (measured ns per stage-state) rather than a curve fit through three points.
static std::uint64_t g_matvecs = 0;

// Power-iterate M(x) in place; returns the dominant eigenvalue estimate.
// Iteration count and stopping rule mirror cpp/strip_mu_kink.cpp exactly, so
// the two engines walk the same bisection and must agree digit for digit.
static double rhoF(const StageOps& O, double x, std::vector<double>& w, Work& s,
                   int maxIt = 4000) {
  const strip::FloatWeight fw(x);
  double r = 0;
  for (int it = 0; it < maxIt; ++it) {
    strip::applyOps(O, w, s.next, fw, s.a, s.b);   // float policy cannot fail
    ++g_matvecs;
    double s2 = 0, s1 = 0;
    for (double v : s.next) s2 += v;
    for (double v : w) s1 += v;
    if (!(s2 > 0)) return 0.0;
    const double rn = s2 / s1, inv = 1.0 / s2;
    for (double& v : s.next) v *= inv;
    w.swap(s.next);
    if (it > 3 && std::fabs(rn - r) < 1e-11 * rn) { r = rn; break; }
    r = rn;
  }
  return r;
}

// Warm-started bisection for x* (rho = 1). Same schedule as strip_mu_kink.
static double solveXstar(const StageOps& O, Work& s, std::vector<double>& warm) {
  std::vector<double> w(O.size[0], 0.0);
  w[0] = 1.0;                                   // index 0 is the empty boundary
  for (int i = 0; i < 8; ++i) {
    strip::applyOps(O, w, s.next, strip::FloatWeight(0.25), s.a, s.b);
    ++g_matvecs;
    double t = 0; for (double v : s.next) t += v;
    if (t > 0) w.swap(s.next);
  }
  double lo = 0.10, hi = 0.5;
  for (int it = 0; it < 55; ++it) {
    const double mid = 0.5 * (lo + hi);
    std::vector<double> wm = w;
    if (rhoF(O, mid, wm, s) < 1.0) lo = mid; else hi = mid;
    if (hi - lo < 1e-13) break;
  }
  warm.swap(w);
  return 0.5 * (lo + hi);
}

// ───────────────────────────── exact phase ───────────────────────────────────
// The load-bearing half of a certificate, run over the frozen operators:
// (M_S(den/num) v)_i >= v_i for EVERY i, in exact integer arithmetic. Same
// arithmetic as cpp/strip_mu_cert.cpp's checkCert — floor-rounded placed branch,
// exact no-cell branch, 2^126 guard on every multiply and add.

struct VerifyOut {
  bool pass = false, overflow = false;
  std::size_t failures = 0, states = 0;
  double minRatio = 0, accBits = 0, rangeBits = 0, floatS = 0, checkS = 0;
  std::int32_t firstBad = -1;
  u128 firstBadLhs = 0, firstBadRhs = 0;
};

// Scale a float eigenvector to positive integers with the largest entry at
// 2^vbits. Entries below 1 quantize to 0; that is SAFE (Collatz-Wielandt needs
// only v >= 0, v != 0) and every state is still checked on the inequality side.
static std::vector<u128> quantize(const std::vector<double>& w, int vbits,
                                  double& wmin, double& wmax) {
  wmax = 0; wmin = 1e308;
  for (double v : w) {
    if (v > wmax) wmax = v;
    if (v > 0 && v < wmin) wmin = v;
  }
  std::vector<u128> q(w.size());
  const double scale = std::ldexp(1.0, vbits) / wmax;
  for (std::size_t i = 0; i < w.size(); ++i) q[i] = (u128)(w[i] * scale);
  return q;
}

static VerifyOut checkRational(const StageOps& O, const std::vector<u128>& v,
                               u128 num, u128 den) {
  VerifyOut R;
  R.states = v.size();
  strip::ExactWeight ew(den, num);              // x = den/num
  std::vector<u128> out, a, b;
  if (!strip::applyOps(O, v, out, ew, a, b)) { R.overflow = true; return R; }
  R.accBits = ew.maxAcc ? std::log2((double)ew.maxAcc) : 0.0;
  double mr = 1e308;
  std::size_t nonzero = 0;
  for (std::size_t i = 0; i < v.size(); ++i) {
    const u128 want = v[i];
    if (want == 0) continue;                    // 0 <= anything
    ++nonzero;
    const u128 got = out[i];
    mr = std::min(mr, (double)got / (double)want);
    if (got < want) {
      if (R.failures == 0) {
        R.firstBad = (std::int32_t)i; R.firstBadLhs = got; R.firstBadRhs = want;
      }
      ++R.failures;
    }
  }
  R.minRatio = (mr > 1e307) ? 0.0 : mr;
  // An all-zero v satisfies "A v >= v" vacuously and would certify everything.
  R.pass = (R.failures == 0 && nonzero > 0);
  return R;
}

// vbits ceiling: the hot product is val*den, and merges let an intermediate
// exceed the initial 2^vbits, so reserve 6 bits. Same rule as strip_mu_cert.
static int vbitsCap(u128 den) {
  int bits = 0; for (u128 d = den; d; d >>= 1) ++bits;
  return 126 - bits - 6;
}

// Converge the float vector at x = den/num, quantize, and check.
static VerifyOut verifyRational(const StageOps& O, u128 num, u128 den, int vbits,
                                Work& s) {
  const auto t0 = std::chrono::steady_clock::now();
  std::vector<double> warm;
  solveXstar(O, s, warm);
  rhoF(O, (double)(long double)den / (double)(long double)num, warm, s);
  double wmin = 0, wmax = 0;
  std::vector<u128> v = quantize(warm, vbits, wmin, wmax);
  const auto t1 = std::chrono::steady_clock::now();
  VerifyOut R = checkRational(O, v, num, den);
  const auto t2 = std::chrono::steady_clock::now();
  R.rangeBits = (wmin > 0 && wmax > 0) ? std::log2(wmax / wmin) : 0.0;
  R.floatS = std::chrono::duration<double>(t1 - t0).count();
  R.checkS = std::chrono::duration<double>(t2 - t1).count();
  return R;
}

// ─────────────────────────────── selftest ────────────────────────────────────
// RED-first: the engine must be able to come out WRONG when the frozen tables
// are wrong, or the tables prove nothing.
static int selftest() {
  int bad = 0;
  auto fail = [&](const char* what) { ++bad; std::printf("  FAIL: %s\n", what); };

  // A. mu_2 = 1 + sqrt(2), independent of everything in this program.
  {
    StageOps O = strip::buildStageOps(2);
    Work s; std::vector<double> warm;
    const double mu = 1.0 / solveXstar(O, s, warm);
    const double want = 1.0 + std::sqrt(2.0);
    std::printf("selftest A: mu_2 = %.10f (exact %.10f) -> %s\n", mu, want,
                std::fabs(mu - want) < 1e-9 ? "OK" : "WRONG");
    if (!(std::fabs(mu - want) < 1e-9)) fail("mu_2 != 1+sqrt(2)");
  }

  // B. Boundary state counts are a fixed fingerprint of the enumeration
  // (banked in results/growth-constant.md).
  {
    const std::size_t want[] = {3, 8, 20, 50, 126, 322, 834};
    std::printf("selftest B: states H=2..8 =");
    for (int H = 2; H <= 8; ++H) {
      const std::size_t got = strip::buildStageOps(H).states();
      std::printf(" %zu", got);
      if (got != want[H - 2]) fail("state count differs from the banked ladder");
    }
    std::printf(" -> %s\n", bad ? "WRONG" : "OK");
  }

  // C. Corrupt the frozen transition table; mu MUST move. If it does not, the
  // tables are not what the answer depends on and every other check is theatre.
  // The edges corrupted are the heaviest-carrying one at each of the first
  // three stages under the converged eigenvector — an edge that carries no mass
  // (the empty seed's, for one: nothing ever finalizes back to it) legitimately
  // does not move mu, so picking by mass is what makes "must change" a fair
  // demand rather than a coin flip.
  {
    StageOps O = strip::buildStageOps(6);
    Work s; std::vector<double> warm;
    const double mu = 1.0 / solveXstar(O, s, warm);

    // Push the converged vector through the stages to get per-stage masses.
    const strip::FloatWeight fw(1.0 / mu);
    std::vector<std::vector<double>> mass(O.H + 1);
    mass[0] = warm;
    for (int r = 0; r < O.H; ++r) {
      mass[r + 1].assign(O.size[r + 1], 0.0);
      for (std::size_t i = 0; i < O.size[r]; ++i) {
        const double v = mass[r][i];
        if (v == 0) continue;
        if (O.t0[r][i] >= 0) mass[r + 1][O.t0[r][i]] += v;
        double t; fw.placed(v, t);
        if (O.t1[r][i] >= 0) mass[r + 1][O.t1[r][i]] += t;
      }
    }

    int moved = 0, tried = 0;
    for (int r = 0; r < 3; ++r) {
      std::size_t best = 0; double bm = 0;
      for (std::size_t i = 0; i < O.size[r]; ++i)
        if (O.t1[r][i] >= 0 && mass[r][i] > bm) { bm = mass[r][i]; best = i; }
      if (bm <= 0) continue;
      StageOps C = O;
      C.t1[r][best] = -1;                       // drop one "cell placed" edge
      ++tried;
      Work cs; std::vector<double> cw;
      const double cmu = 1.0 / solveXstar(C, cs, cw);
      if (std::fabs(cmu - mu) > 1e-9) ++moved;
    }
    std::printf("selftest C: %d/%d dropped transitions changed mu_6 -> %s\n",
                moved, tried, (tried == 3 && moved == tried) ? "OK" : "WRONG");
    if (tried != 3 || moved != tried)
      fail("a corrupted transition table gave the same mu");
  }

  // D. Corrupt the finalize map the same way.
  {
    StageOps O = strip::buildStageOps(6);
    Work s; std::vector<double> warm;
    const double mu = 1.0 / solveXstar(O, s, warm);
    StageOps C = O;
    int hit = 0;
    for (std::size_t i = 0; i < C.fin.size(); ++i)
      if (C.fin[i] >= 0) { C.fin[i] = -1; hit = 1; break; }
    Work cs; std::vector<double> cw;
    const double cmu = hit ? 1.0 / solveXstar(C, cs, cw) : mu;
    std::printf("selftest D: dropped one finalize edge -> mu_6 %.7f vs %.7f -> %s\n",
                cmu, mu, (hit && std::fabs(cmu - mu) > 1e-9) ? "OK" : "WRONG");
    if (!(hit && std::fabs(cmu - mu) > 1e-9)) fail("corrupted finalize map gave the same mu");
  }

  // E. The exact kernel must say yes to a true claim and NO to a false one.
  // mu_2 = 2.41421356..., so 24142135/10^7 is a lower bound and 24142136/10^7
  // is not (it exceeds mu_2 in the 8th digit).
  {
    StageOps O = strip::buildStageOps(2);
    Work s;
    VerifyOut t = verifyRational(O, 24142135, 10000000, 96, s);
    VerifyOut f = verifyRational(O, 24142136, 10000000, 96, s);
    std::printf("selftest E: mu_2 >= 2.4142135 -> %s (expect PASS); "
                ">= 2.4142136 -> %s (expect FAIL)\n",
                t.pass ? "PASS" : "FAIL", f.pass ? "PASS" : "FAIL");
    if (!t.pass) fail("exact check rejected a true bound");
    if (f.pass) fail("exact check certified an over-claim");
  }

  // F. The all-zero vector satisfies A v >= v vacuously; it must be refused.
  {
    StageOps O = strip::buildStageOps(4);
    std::vector<u128> z(O.states(), 0);
    VerifyOut R = checkRational(O, z, 99999999, 10000000);
    std::printf("selftest F: all-zero vector -> %s (expect FAIL)\n",
                R.pass ? "PASS" : "FAIL");
    if (R.pass) fail("a vacuous certificate was accepted");
  }

  std::printf("selftest: %s\n", bad == 0 ? "ALL OK" : "FAILURES");
  return bad == 0 ? 0 : 1;
}

// ──────────────────────────────── driver ─────────────────────────────────────

// Throughput probe: a FIXED small number of matvecs at one x, float and exact,
// reported as ns per stage-state. Not a mu_H solve — it exists so the H>=15
// wall projection is measured across the cache cliff (the frozen tables go from
// 7.5 MB at H=12 to a projected 566 MB at H=16, i.e. the indexed scatter stops
// being cache-resident) instead of extrapolated from small-H timings.
static void bench(int H, int iters) {
  const auto tb = std::chrono::steady_clock::now();
  StageOps O = strip::buildStageOps(H);
  const double build = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - tb).count();
  Work s;
  std::vector<double> w(O.size[0], 0.0);
  w[0] = 1.0;
  const strip::FloatWeight fw(0.16);
  for (int i = 0; i < 12; ++i) {                 // spread mass over the support
    strip::applyOps(O, w, s.next, fw, s.a, s.b);
    double t = 0; for (double v : s.next) t += v;
    if (t > 0) { for (double& v : s.next) v /= t; w.swap(s.next); }
  }
  const auto t0 = std::chrono::steady_clock::now();
  for (int i = 0; i < iters; ++i) {
    strip::applyOps(O, w, s.next, fw, s.a, s.b);
    double t = 0; for (double v : s.next) t += v;
    if (t > 0) { for (double& v : s.next) v /= t; w.swap(s.next); }
  }
  const double fl = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - t0).count();

  double wmin, wmax;
  std::vector<u128> v = quantize(w, 96, wmin, wmax);
  std::vector<u128> out, a, b;
  const strip::ExactWeight ew(10000000, 63000000);
  const auto t1 = std::chrono::steady_clock::now();
  const bool ok = strip::applyOps(O, v, out, ew, a, b);
  const double ex = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - t1).count();

  std::printf("H=%d states=%zu stage_total=%zu table_mb=%.1f build_s=%.1f "
              "float_ns_per_stage_state=%.2f exact_ns_per_stage_state=%.2f "
              "float_matvec_s=%.3f exact_sweep_s=%.3f overflow=%d\n",
              H, O.states(), O.stageTotal(), O.tableBytes() / 1048576.0, build,
              1e9 * fl / (double(iters) * O.stageTotal()),
              1e9 * ex / double(O.stageTotal()), fl / iters, ex, ok ? 0 : 1);
  std::fflush(stdout);
}

static void printOps(int Hmin, int Hmax) {
  std::printf(" H |   states |  max stage |  sum|S_r| |  table MB | build\n");
  for (int H = Hmin; H <= Hmax; ++H) {
    const auto t0 = std::chrono::steady_clock::now();
    StageOps O = strip::buildStageOps(H);
    const double s = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count();
    std::printf("%2d | %8zu | %10zu | %9zu | %9.1f | %.1fs\n", H, O.states(),
                O.maxStage(), O.stageTotal(), O.tableBytes() / 1048576.0, s);
    std::fflush(stdout);
  }
}

int main(int argc, char** argv) {
  std::vector<const char*> pos;
  bool doSelftest = false, doOps = false, doVerify = false, doBench = false;
  int vbits = 0, benchIters = 20;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    if (a == "--selftest") doSelftest = true;
    else if (a == "--ops") doOps = true;
    else if (a == "--verify") doVerify = true;
    else if (a == "--bench") doBench = true;
    else if (a == "--iters" && i + 1 < argc) benchIters = std::atoi(argv[++i]);
    else if (a == "--vbits" && i + 1 < argc) vbits = std::atoi(argv[++i]);
    else if (a.size() && a[0] == '-') {
      std::fprintf(stderr, "unknown option %s\n", a.c_str());
      return 2;                                 // fail closed on a bad flag
    } else pos.push_back(argv[i]);
  }
  if (doSelftest) return selftest();

  if (doVerify) {
    if (pos.size() != 3) {
      std::fprintf(stderr, "usage: strip_mu_fast --verify <H> <num> <den>\n");
      return 2;
    }
    const int H = std::atoi(pos[0]);
    if (H < 2 || H > SIGMAX - 4) { std::fprintf(stderr, "H out of range\n"); return 2; }
    const u128 num = (u128)std::strtoull(pos[1], nullptr, 10);
    const u128 den = (u128)std::strtoull(pos[2], nullptr, 10);
    if (num == 0 || den == 0) { std::fprintf(stderr, "num/den must be positive\n"); return 2; }
    const int cap = vbitsCap(den);
    if (vbits == 0) vbits = cap;
    if (vbits < 8 || vbits > cap) {
      std::fprintf(stderr, "--vbits out of range (8..%d for den=%s)\n", cap,
                   u128str(den).c_str());
      return 2;
    }
    obs::Reporter rep("stripmufast-verify-H" + std::to_string(H));
    const auto t0 = std::chrono::steady_clock::now();
    StageOps O = strip::buildStageOps(H);
    Work s;
    VerifyOut R = verifyRational(O, num, den, vbits, s);
    const double wall = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count();
    std::printf("H=%d claim=%s/%s result=%s states=%zu vlen=%zu vbits=%d "
                "vrange_bits=%.1f acc_bits=%.1f fail=%zu min_ratio=%.9f "
                "overflow=%d matvecs=%llu float_s=%.2f exact_sweep_s=%.2f "
                "wall_s=%.1f\n",
                H, u128str(num).c_str(), u128str(den).c_str(),
                R.pass ? "PASS" : "FAIL", O.states(), R.states, vbits,
                R.rangeBits, R.accBits, R.failures, R.minRatio,
                R.overflow ? 1 : 0, (unsigned long long)g_matvecs, R.floatS,
                R.checkS, wall);
    rep.done(std::string("result=") + (R.pass ? "PASS" : "FAIL"));
    return R.pass ? 0 : 1;
  }

  const int Hmin = pos.size() >= 1 ? std::atoi(pos[0]) : 2;
  const int Hmax = pos.size() >= 2 ? std::atoi(pos[1]) : 11;
  if (Hmin < 2 || Hmax < Hmin || Hmax > SIGMAX - 4) {
    std::fprintf(stderr, "H range out of bounds (2..%d)\n", SIGMAX - 4);
    return 2;
  }
  if (doOps) { printOps(Hmin, Hmax); return 0; }
  if (doBench) {
    if (benchIters < 1) { std::fprintf(stderr, "--iters must be >= 1\n"); return 2; }
    for (int H = Hmin; H <= Hmax; ++H) bench(H, benchIters);
    return 0;
  }

  std::printf(" H |   states |   mu_H     | x*        | time\n");
  for (int H = Hmin; H <= Hmax; ++H) {
    obs::Reporter rep("stripmufast-H" + std::to_string(H));
    const auto t0 = std::chrono::steady_clock::now();
    StageOps O = strip::buildStageOps(H);
    const double build = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count();
    Work s; std::vector<double> warm;
    const double xstar = solveXstar(O, s, warm);
    const double wall = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - t0).count();
    std::printf("%2d | %8zu | %.7f | %.7f | %.1fs\n", H, O.states(),
                1.0 / xstar, xstar, wall);
    std::fflush(stdout);
    rep.done("H=" + std::to_string(H) + " states=" + std::to_string(O.states()),
             "build_s=" + std::to_string(build) +
             " table_mb=" + std::to_string(O.tableBytes() / 1048576.0) +
             " matvecs=" + std::to_string(g_matvecs) +
             " stage_total=" + std::to_string(O.stageTotal()));
    g_matvecs = 0;
  }
  return 0;
}
