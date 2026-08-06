// convex_perim_tm.cpp -- HV-convex king animals (convex polyplets) by
// SEMIPERIMETER, exact-box row transfer matrix, C++/GMP port of
// experiments/convex_perimeter.py's count_by_box/perim_series.
//
// docs/middle-kingdom-plan.md Phase 1b. Unlike the by-area DP (convex_area_tm,
// Phase 1a), the by-box state stores the exact column boundaries (l, r), not
// a phase-relative delta -- future transitions need the absolute box
// coordinates, so distinct rp values can't be merged into one scaled count
// the way Phase 1a's dl values were. What DOES collapse is the O(W)-per-lp
// inner rp loop: for a fixed lp, v is added unchanged to EVERY rp in a
// contiguous range, which is a textbook range-update -- a 1D difference
// array per (lp, npl, tLp, npr, tRp) bucket, marked in O(1) per lp and
// materialized with one O(W) prefix-sum sweep per bucket after all source
// states are processed, instead of one add per (lp, rp) pair. That drops
// per-source-state cost from O(W^2) to O(W) (the lp loop remains explicit,
// unlike Phase 1a where the analogous outer loop -- wp there -- was also
// kept explicit), moving the total DP cost from ~S^6 to ~S^5. Verified
// (Python prototype) against the original nested-loop count_by_box for
// Smax in {12, 20, 30}, exact match, before this port.
//
// docs/middle-kingdom-followups-plan.md Phase 2a adds a dir4-filtered mode.
// results/middle-kingdom-phase3.md's Proposition 2 (proved on the COLUMN-built
// transfer matrix, cpp/middle_kingdom_tm.cpp) says a column-convex king animal
// is half-plane-4-cone directed iff the column-bottom profile b(j) never
// drops by more than one row: b(j+1) >= b(j) - 1. This DP is ROW-built
// instead (bottom row first), so the translation was re-derived from Lemma A
// (of the same proposition) directly against this DP's state, not assumed:
//
//   For a column j left of the animal's bottom row (j < l(1)), b(j) is the
//   first row i (searching bottom to top) with l(i) <= j -- the right
//   boundary never restricts a column that far left, since r(1) >= l(1) > j
//   already. b(j) is a right-continuous inverse of l() restricted to l's
//   *descending* phase (pl=0): a single row where l DROPS by k>=1 covers k
//   new columns at once (b constant across them, diff 0, fine); a row where
//   l does NOT drop (flat, lp==l) "wastes" a row index without covering a
//   new column, and if l drops again on any LATER row while still in the
//   descending phase, the two columns either side of that wasted row have
//   b differing by >=2 -- exactly the forbidden drop. (By the symmetric
//   argument on r's ASCENDING phase, the same wasted-row pattern there only
//   makes b RISE across the gap, which Proposition 2 does not restrict, so
//   the right boundary's own phase needs no extra condition.) Hence: dir4 is
//   "in the left-descending phase (pl=0), lp < l strictly, every row; the
//   first row that fails to strictly decrease locks the phase (lp >= l from
//   then on), exactly as the unrestricted DP already locks on lp > l." One
//   line of code: replace `lp > l` with `lp >= l` in the npl transition.
//   Verified two ways before trusting it: worked by hand against a small
//   family of l-sequences (flat-then-drop always produces a >=2 gap in b;
//   drop-by-k>1 in one step never does), then against
//   `build/directed_cone_anchor gridperim` brute force (tests/gate_mk_dir4_perim.py).
//   dir4bad is the RED control the plan asked for by name ("e.g. non-strict
//   decrease"): the un-strengthened `lp > l` rule, i.e. verbatim the
//   unrestricted-HV transition mislabeled as dir4 -- must NOT reproduce the
//   dir4 brute-force counts (it reproduces the unrestricted HV ones instead).
//
// Usage: build/convex_perim_tm SMAX [king] [mode]
//   king default 1; king=0 is the plain-polyomino control, A005436 (mode is
//   forced to "hv" when king=0 -- dir4 is a king-cone notion).
//   mode in {hv, dir4, dir4bad}, default hv (unrestricted HV-convex, the
//   original behavior -- old two-arg invocations are unchanged).
// stdout: p(2), p(3), ..., p(SMAX) on one comma-separated line (semiperimeter
//   series, matching experiments/convex_perimeter.py's perim_series).
// stderr: obs.h start/heartbeat/done.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#include <gmpxx.h>

#include "argparse.h"
#include "obs.h"

namespace {

using Vec = std::vector<mpz_class>;

// Per-W state/delta index: (l, r) in [0,W)^2 (l<=r used only), plus 4 binary
// flags (pl, pr, tL, tR) or (npl, tLp, npr, tRp) for delta -- same packing.
inline int StateIdx(int W, int a, int b, int f0, int f1, int f2, int f3) {
  return ((((a * W + b) * 2 + f0) * 2 + f1) * 2 + f2) * 2 + f3;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr, "usage: %s SMAX [king=1] [mode=hv|dir4|dir4bad]\n",
                 argv[0]);
    return 1;
  }
  const int Smax = (int)argparse::ArgInt(argv[1], "SMAX", 1, 100000);
  const bool king = argc < 3 || argparse::ArgFlag(argv[2], "king");
  const std::string modeStr = argc < 4 ? "hv" : argv[3];
  bool strictLeft;  // dir4's one-line difference from unrestricted HV: see
                     // header. dir4bad is the RED control -- same as hv.
  if (modeStr == "hv") strictLeft = false;
  else if (modeStr == "dir4") strictLeft = true;
  else if (modeStr == "dir4bad") strictLeft = false;
  else {
    std::fprintf(stderr, "unknown mode %s (want hv|dir4|dir4bad)\n",
                 modeStr.c_str());
    return 1;
  }
  if (modeStr != "hv" && !king) {
    std::fprintf(stderr, "mode=%s needs king=1 (dir4 is a king-cone notion)\n",
                 modeStr.c_str());
    return 1;
  }
  obs::Reporter rep("convex_perim_tm", Smax - 1,
                     "Smax=" + std::to_string(Smax) +
                         " king=" + std::to_string(king) +
                         " mode=" + modeStr);

  Vec p(Smax + 1);  // p[s] = total count at semiperimeter s

  for (int W = 1; W < Smax; ++W) {
    const int Hmax = Smax - W;
    if (Hmax < 1) break;
    const int NS = W * W * 16;  // dense state/delta array size for this W

    Vec dp(NS);
    for (int l = 0; l < W; ++l)
      for (int r = l; r < W; ++r)
        dp[StateIdx(W, l, r, 0, 0, l == 0 ? 1 : 0, r == W - 1 ? 1 : 0)] += 1;

    auto flush = [&](const Vec& d) {
      mpz_class s = 0;
      for (int l = 0; l < W; ++l)
        for (int r = l; r < W; ++r)
          for (int pl = 0; pl < 2; ++pl)
            for (int pr = 0; pr < 2; ++pr) {
              const mpz_class& v = d[StateIdx(W, l, r, pl, pr, 1, 1)];
              if (v != 0) s += v;
            }
      return s;
    };

    Vec res(Hmax + 1);
    res[1] = flush(dp);
    int H = 1;
    while (H < Hmax) {
      // delta[(lp, npl, tLp, npr, tRp)][rp] as one flat array, W+1 wide per
      // bucket so index rp==W is the "one past end" sentinel for the mark.
      Vec delta((size_t)W * 16 * (W + 1));
      auto dIdx = [&](int lp, int npl, int tLp, int npr, int tRp, int rp) {
        return (size_t)((((lp * 2 + npl) * 2 + tLp) * 2 + npr) * 2 + tRp) *
                   (W + 1) +
               rp;
      };
      auto mark = [&](int lp, int npl, int tLp, int npr, int tRp, int a,
                       int b, const mpz_class& v) {
        if (a > b) return;
        delta[dIdx(lp, npl, tLp, npr, tRp, a)] += v;
        delta[dIdx(lp, npl, tLp, npr, tRp, b + 1)] += -v;
      };

      for (int l = 0; l < W; ++l) {
        for (int r = l; r < W; ++r) {
          for (int pl = 0; pl < 2; ++pl) {
            for (int pr = 0; pr < 2; ++pr) {
              for (int tL = 0; tL < 2; ++tL) {
                for (int tR = 0; tR < 2; ++tR) {
                  const mpz_class& v =
                      dp[StateIdx(W, l, r, pl, pr, tL, tR)];
                  if (v == 0) continue;

                  const int lpLo = pl == 1 ? l : 0;
                  const int lpHi =
                      std::min(W - 1, king ? r + 1 : r);
                  for (int lp = lpLo; lp <= lpHi; ++lp) {
                    const int kingOff = king ? l - 1 : l;
                    const int rpLo = std::max(lp, kingOff);
                    const int rpHi = pr == 1 ? r : W - 1;
                    if (rpLo > rpHi) continue;
                    const int npl =
                        (pl == 1 || (strictLeft ? lp >= l : lp > l)) ? 1 : 0;
                    const int tLp = (tL == 1 || lp == 0) ? 1 : 0;

                    // (npr, a, b) sub-ranges of [rpLo, rpHi]
                    int nr = 0;
                    int npr_[2], ra[2], rb[2];
                    if (pr == 0) {
                      int a = rpLo, b = std::min(rpHi, r - 1);
                      if (a <= b) { npr_[nr] = 1; ra[nr] = a; rb[nr] = b; ++nr; }
                      a = std::max(rpLo, r); b = rpHi;
                      if (a <= b) { npr_[nr] = 0; ra[nr] = a; rb[nr] = b; ++nr; }
                    } else {
                      npr_[nr] = 1; ra[nr] = rpLo; rb[nr] = rpHi; ++nr;
                    }

                    for (int i = 0; i < nr; ++i) {
                      const int npr = npr_[i], a = ra[i], b = rb[i];
                      if (tR == 1) {
                        mark(lp, npl, tLp, npr, 1, a, b, v);
                      } else if (a <= W - 1 && W - 1 <= b) {
                        if (a <= W - 2)
                          mark(lp, npl, tLp, npr, 0, a, W - 2, v);
                        mark(lp, npl, tLp, npr, 1, W - 1, W - 1, v);
                      } else {
                        mark(lp, npl, tLp, npr, 0, a, b, v);
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }

      Vec ndp(NS);
      for (int lp = 0; lp < W; ++lp)
        for (int npl = 0; npl < 2; ++npl)
          for (int tLp = 0; tLp < 2; ++tLp)
            for (int npr = 0; npr < 2; ++npr)
              for (int tRp = 0; tRp < 2; ++tRp) {
                mpz_class run = 0;
                for (int rp = 0; rp < W; ++rp) {
                  run += delta[dIdx(lp, npl, tLp, npr, tRp, rp)];
                  if (run != 0)
                    ndp[StateIdx(W, lp, rp, npl, npr, tLp, tRp)] += run;
                }
              }
      dp = std::move(ndp);
      ++H;
      res[H] = flush(dp);
    }
    for (int H2 = 1; H2 <= Hmax; ++H2) p[W + H2] += res[H2];
    rep.beat(W, "W=" + std::to_string(W));
  }

  std::string out;
  for (int s = 2; s <= Smax; ++s) {
    if (s > 2) out += ", ";
    out += p[s].get_str();
  }
  std::fputs(out.c_str(), stdout);
  std::fputc('\n', stdout);
  rep.done("Smax=" + std::to_string(Smax));
  return 0;
}
