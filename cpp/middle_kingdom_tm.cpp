// middle_kingdom_tm.cpp -- column transfer matrix for the column-convex cells
// of the docs/middle-kingdom-plan.md Phase 3 grid, by area.
//
// A column-convex king animal is a sequence of nonempty column intervals
// [b(j), t(j)], j = 1..k, with t(j) = b(j) + h(j) - 1, consecutive columns
// king-adjacent:  b(j+1) <= t(j) + 1  and  b(j) <= t(j+1) + 1, i.e.
//   d := b(j+1) - b(j)  in  [-h(j+1), h(j)]        (h(j) + h(j+1) + 1 choices).
// Counted up to translation, so the profile is determined by the d's.
//
// Phase 3's structural finding (results/middle-kingdom-phase3.md): ON A
// COLUMN-CONVEX ANIMAL every directedness predicate of the grid collapses to a
// condition on the bottom profile b alone, because the cone {W,NW,N,NE,E} (and
// {N,NE,E,SE}) can climb a column but never descend inside it, so a column is
// fully reached iff its BOTTOM cell is reached, and the bottom cell of column
// j+1 is enterable from column j exactly when b(j+1) >= b(j) (5-cone) or
// b(j+1) >= b(j) - 1 (4-cone, which owns the extra SE step). Hence:
//
//   MODE        class                              condition on b
//   cc          column-convex (control, A187077)   none
//   ccmono      + bottoms nondecreasing (A007052)  d >= 0
//   ccdir5      x Bacher 5-cone directed           b valley-unimodal
//   ccdir4      x half-plane 4-cone directed       d >= -1
//   ccctrlb     x control B (bottom row waived)    every local min of b is
//                                                  at the global minimum
//   hv          HV-convex (control, novel series)  b valley-unimodal AND
//                                                  t peak-unimodal
//   hvdir4      HV-convex x 4-cone directed        the above AND d >= -1
//   hvmono      HV-convex x b nondecreasing        d >= 0 AND t peak-unimodal
//   stair       staircase (A225114)                d >= 0 AND d >= h - h'
//                                                  (b AND t nondecreasing)
//   hvdir4asc   hvdir4 minus every animal whose phase path visits (0,1)
//               (results/hv-growth-sandwich.md, the spectrum split): the
//               phase-(0,1) state is deleted from the automaton, so what
//               survives is the part of (dir4, HV-convex) the truncated
//               descending block cannot reach; hvdir4 - hvdir4asc is the rest.
//   hvdir4ascbad RED control for hvdir4asc: deletes phase (1,0) instead of
//               (0,1); must not match hvdir4asc
//   ccdir4bad   RED control: d >= -2               must not match ccdir4
//   ccctrlbbad  RED control: ccctrlb with the plateau rule dropped (ascent out
//               of a local-minimum PLATEAU above the global minimum wrongly
//               allowed); must not match ccctrlb
//
// (dir5 x HV-convex, dir5 x staircase, dir4 x staircase, ctrlB x HV-convex,
// ctrlB x staircase and the whole multi-directed row need no mode here: they
// are proved collapses onto the corresponding unfiltered cell -- HV-convexity
// already forces b valley-unimodal, staircase already forces d >= 0.)
//
// Two engines:
//   PROFILE  state (h, pb, pt) -- column height and the two unimodality
//            phases. O(N^3) transitions after collapsing each d-interval into
//            O(1) constant-sign segments. Reaches n in the hundreds.
//   GROUND   state (h, u, ph) for ccctrlb / ccctrlbbad only -- u = b - (running
//            minimum) has to be carried because "local minimum at the global
//            minimum" is a statement about absolute height, so the d's cannot
//            be aggregated. O(N^5)-ish in time and O(N^3) in state, so it runs
//            out of laptop somewhere past n = 400, not past n = 700.
//
// Usage:  build/middle_kingdom_tm MODE N
// stdout: "n a(n)" per line, n = 1..N (the format prec_guess and
//         experiments/convex_growth.py read).
// stderr: obs.h start/heartbeat/done.
// Target machine: laptop. MEASURED (gympie, 1 core): PROFILE modes n=700 in
//   1.5-2.9 s and <= 65 MB; GROUND n=150 in 5.3 s / 194 MB and n=250 in 66.3 s
//   / 938 MB, which fixes its scaling at O(n^4.95) time, O(n^3.2) memory.
//   No checkpointing: runs are seconds to minutes; kill = plain SIGINT.
// Oracle: tests/gate_middle_kingdom.py against Phase 0's brute-force table.
#include <algorithm>
#include <climits>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#include <gmpxx.h>

#include "obs.h"

namespace {

enum class Mode { CC, CCMono, CCDir5, CCDir4, CCDir4Bad, CCCtrlB, CCCtrlBBad,
                  HV, HVDir4, HVMono, Stair, HVDir4Asc, HVDir4AscBad };

struct Spec {
  int dmin;    // floor on d = b(j+1) - b(j), before the -h(j+1) adjacency cap
  bool useB;   // enforce b valley-unimodal (nonincreasing, then nondecreasing)
  bool useT;   // enforce t peak-unimodal (nondecreasing, then nonincreasing)
  bool bmono;  // enforce b nondecreasing outright: d >= 0 at every step
  bool tmono;  // enforce t nondecreasing outright: d >= s = h - h' every step
  int banPhase;  // phase code 2*pb+pt to delete from the automaton, or -1
};

const int kNoFloor = INT_MIN / 4;

Spec specOf(Mode m) {
  switch (m) {
    case Mode::CC:        return {kNoFloor, false, false, false, false, -1};
    case Mode::CCMono:    return {0, false, false, false, false, -1};
    case Mode::CCDir5:    return {kNoFloor, true, false, false, false, -1};
    case Mode::CCDir4:    return {-1, false, false, false, false, -1};
    case Mode::CCDir4Bad: return {-2, false, false, false, false, -1};
    case Mode::HV:        return {kNoFloor, true, true, false, false, -1};
    case Mode::HVDir4:    return {-1, true, true, false, false, -1};
    case Mode::HVMono:    return {kNoFloor, false, true, true, false, -1};
    case Mode::Stair:     return {kNoFloor, false, false, true, true, -1};
    case Mode::HVDir4Asc:    return {-1, true, true, false, false, 1};
    case Mode::HVDir4AscBad: return {-1, true, true, false, false, 2};
    default:              return {kNoFloor, false, false, false, false, -1};
  }
}

// ---------------------------------------------------------------------------
// PROFILE engine. dp[a][h][p], p = 2*pb + pt.
// ---------------------------------------------------------------------------
std::vector<mpz_class> runProfile(Mode mode, int N, obs::Reporter& rep) {
  const Spec sp = specOf(mode);
  const size_t stride = 4;
  const size_t rowlen = (size_t)(N + 1) * stride;
  std::vector<mpz_class> dp((size_t)(N + 1) * rowlen);
  auto at = [&](int a, int h, int p) -> mpz_class& {
    return dp[(size_t)a * rowlen + (size_t)h * stride + p];
  };
  std::vector<mpz_class> total(N + 1);

  for (int h = 1; h <= N; ++h) at(h, h, 0) = 1;  // the one-column animals

  for (int a = 1; a <= N; ++a) {
    for (int h = 1; h <= a; ++h)
      for (int p = 0; p < 4; ++p) total[a] += at(a, h, p);
    if (a == N) break;
    for (int h = 1; h <= a; ++h) {
      for (int p = 0; p < 4; ++p) {
        const mpz_class& v = at(a, h, p);
        if (v == 0) continue;
        const int pb = p >> 1, pt = p & 1;
        for (int hp = 1; hp <= N - a; ++hp) {
          int lo = std::max(-hp, sp.dmin), hi = h;
          if (sp.useB && pb == 1) lo = std::max(lo, 0);   // no more descent
          const int s = h - hp;                           // d > s  <=>  t rises
          if (sp.useT && pt == 1) hi = std::min(hi, s);    // no more rise
          if (sp.bmono) lo = std::max(lo, 0);              // b never descends
          if (sp.tmono) lo = std::max(lo, s);              // t never descends
          if (lo > hi) continue;
          // Cut [lo, hi] into segments on which sign(d) and sign(d - s) are
          // both constant; there are at most five.
          int cut[6] = {lo, 0, 1, s, s + 1, hi + 1};
          std::sort(cut, cut + 6);
          for (int c = 0; c < 5; ++c) {
            const int lseg = std::max(cut[c], lo);
            const int rseg = std::min(cut[c + 1], hi + 1);
            if (lseg >= rseg) continue;
            const unsigned long count = (unsigned long)(rseg - lseg);
            const int d = lseg;  // representative: signs are constant here
            const int npb = sp.useB ? (d > 0 ? 1 : pb) : 0;
            const int npt = sp.useT ? (d < s ? 1 : pt) : 0;
            if (sp.banPhase >= 0 && 2 * npb + npt == sp.banPhase) continue;
            mpz_class& dst = at(a + hp, hp, 2 * npb + npt);
            if (count == 1) dst += v;
            else mpz_addmul_ui(dst.get_mpz_t(), v.get_mpz_t(), count);
          }
        }
      }
    }
    rep.beat((double)a, "unit=area denom=" + std::to_string(N));
  }
  return total;
}

// ---------------------------------------------------------------------------
// GROUND engine (ccctrlb / ccctrlbbad). dp[a][h][u][ph]:
//   u  = b - (minimum of b so far)
//   ph = 0  no ascent yet, so u == 0 and the minimum may still fall
//        1  ascended at least once (so a local minimum AT the global minimum
//           already exists); free to rise or fall, but never below u = 0
//        2  currently below a peak and above the minimum -- rising again here
//           would create a local minimum at u > 0, which is exactly what the
//           predicate forbids. plateauKeeps=false is the RED control: it lets
//           a plateau clear the flag, wrongly accepting a local-minimum
//           plateau above the global minimum.
// The right-hand +inf sentinel makes ph = 2 a *rejecting* final state as well
// as a constrained one: an animal that simply stops while descending ends at a
// local minimum above the global one. So ph = 2 states propagate but are not
// counted. (The left sentinel needs no rule: the first column is at u = 0.)
// ---------------------------------------------------------------------------
std::vector<mpz_class> runGround(int N, bool plateauKeeps, obs::Reporter& rep) {
  const size_t phs = 3, ustr = phs, hstr = (size_t)(N + 1) * ustr;
  const size_t astr = (size_t)(N + 1) * hstr;
  std::vector<mpz_class> dp((size_t)(N + 1) * astr);
  auto at = [&](int a, int h, int u, int ph) -> mpz_class& {
    return dp[(size_t)a * astr + (size_t)h * hstr + (size_t)u * ustr + ph];
  };
  std::vector<mpz_class> total(N + 1);

  for (int h = 1; h <= N; ++h) at(h, h, 0, 0) = 1;

  for (int a = 1; a <= N; ++a) {
    for (int h = 1; h <= a; ++h)
      for (int u = 0; u + h <= a; ++u)
        for (int ph = 0; ph < 2; ++ph) total[a] += at(a, h, u, ph);
    if (a == N) break;
    for (int h = 1; h <= a; ++h) {
      for (int u = 0; u + h <= a; ++u) {
        for (int ph = 0; ph < 3; ++ph) {
          const mpz_class& v = at(a, h, u, ph);  // targets are all at a+hp > a
          if (v == 0) continue;
          for (int hp = 1; hp <= N - a; ++hp) {
            const int lo = -hp, hi = h;
            if (ph == 0) {
              // u == 0. Any descent just moves the running minimum down.
              const int nlo = std::min(0, hi);
              if (nlo >= lo) {
                const unsigned long cnt = (unsigned long)(nlo - lo + 1);
                mpz_class& dst = at(a + hp, hp, 0, 0);
                if (cnt == 1) dst += v;
                else mpz_addmul_ui(dst.get_mpz_t(), v.get_mpz_t(), cnt);
              }
              for (int d = 1; d <= hi; ++d) at(a + hp, hp, d, 1) += v;
              continue;
            }
            const int dlo = std::max(lo, -u);              // never below u = 0
            const int dhi = (ph == 2) ? std::min(hi, 0) : hi;
            for (int d = dlo; d <= dhi; ++d) {
              const int nu = u + d;
              int nph;
              if (d > 0) nph = 1;
              else if (d == 0) nph = (ph == 2 && plateauKeeps) ? 2 : 1;
              else nph = (nu == 0) ? 1 : 2;
              at(a + hp, hp, nu, nph) += v;
            }
          }
        }
      }
    }
    rep.beat((double)a, "unit=area denom=" + std::to_string(N));
  }
  return total;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    std::fprintf(stderr,
                 "usage: %s {cc|ccmono|ccdir5|ccdir4|ccdir4bad|ccctrlb|"
                 "ccctrlbbad|hv|hvdir4|hvmono|stair|hvdir4asc|hvdir4ascbad}"
                 " N\n",
                 argv[0]);
    return 2;
  }
  const std::string ms = argv[1];
  Mode mode;
  if (ms == "cc") mode = Mode::CC;
  else if (ms == "ccmono") mode = Mode::CCMono;
  else if (ms == "ccdir5") mode = Mode::CCDir5;
  else if (ms == "ccdir4") mode = Mode::CCDir4;
  else if (ms == "ccdir4bad") mode = Mode::CCDir4Bad;
  else if (ms == "ccctrlb") mode = Mode::CCCtrlB;
  else if (ms == "ccctrlbbad") mode = Mode::CCCtrlBBad;
  else if (ms == "hv") mode = Mode::HV;
  else if (ms == "hvdir4") mode = Mode::HVDir4;
  else if (ms == "hvmono") mode = Mode::HVMono;
  else if (ms == "stair") mode = Mode::Stair;
  else if (ms == "hvdir4asc") mode = Mode::HVDir4Asc;
  else if (ms == "hvdir4ascbad") mode = Mode::HVDir4AscBad;
  else { std::fprintf(stderr, "unknown mode %s\n", argv[1]); return 2; }

  const int N = std::atoi(argv[2]);
  if (N < 1 || N > 4000) { std::fprintf(stderr, "N out of range (1..4000)\n"); return 2; }

  obs::Reporter rep("middle_kingdom_tm", 0,
                    "mode=" + ms + " n=" + std::to_string(N));
  const bool ground = mode == Mode::CCCtrlB || mode == Mode::CCCtrlBBad;
  std::vector<mpz_class> total =
      ground ? runGround(N, mode == Mode::CCCtrlB, rep) : runProfile(mode, N, rep);

  for (int n = 1; n <= N; ++n)
    std::printf("%d %s\n", n, total[n].get_str().c_str());
  rep.done("mode=" + ms + " n=" + std::to_string(N) +
           " a_n=" + (N <= 0 ? std::string("0") : total[N].get_str()));
  return 0;
}
