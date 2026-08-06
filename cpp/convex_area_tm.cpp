// convex_area_tm.cpp -- HV-convex king animals (convex polyplets) by area,
// row transfer matrix, C++/GMP port of experiments/convex_tm.py.
//
// docs/middle-kingdom-plan.md Phase 1a: the Python DP (already collapsed from
// N^5 to N^4 by folding the per-dl loop into O(1) box-count sub-intervals,
// see the same comment in convex_tm.py) still costs O(N^4) DP steps x O(N)
// bigint digits; Python's per-object overhead puts n=500 at ~30 min, over the
// 10-minute laptop budget. This is a straight translation of the same DP --
// same states, same transitions -- onto GMP mpz_class so the interpreter
// overhead drops out. Verify against experiments/convex_tm.py before trusting
// any term this doesn't share with that script's tested range.
//
// State: (w, pl, pr) -- current bottom width, left-boundary phase (0 = still
// non-increasing, 1 = now non-decreasing), right-boundary phase (0 = still
// non-decreasing, 1 = now non-increasing). dp maps state -> vector of counts
// by total cells n. Each outer iteration adds one more row of width wp on
// top of every current state, per the king-reach + phase-monotonicity rules
// in convex_tm.py's module docstring.
//
// Adjacency is a one-line switch. Writing dl = l' - l for the horizontal shift
// of the new row, king reach (l' <= r+1, r' >= l-1) is dl in [-wp, w]; edge
// adjacency (ordinary polyominoes: consecutive rows must share a column, so
// l' <= r and r' >= l) is the tighter dl in [-wp+1, w-1]. Everything else --
// states, phases, box collapse -- is identical, so king=0 yields HV-convex
// POLYOMINOES by area (A067675), the control the D-finiteness work in
// docs/proofs/convex-mirage.md needs at the same term count as the king series.
//
// Usage: build/convex_area_tm N [king]     (king defaults to 1)
// stdout: term(1), term(2), ..., term(N) on one comma-separated line.
// stderr: obs.h start/heartbeat/done.
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <unordered_map>
#include <vector>

#include <gmpxx.h>

#include "obs.h"

namespace {

using Vec = std::vector<mpz_class>;

inline int Key(int w, int pl, int pr) { return (w << 2) | (pl << 1) | pr; }

struct Range {
  int val, lo, hi;
};

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr, "usage: %s N [king]\n", argv[0]);
    return 1;
  }
  const int N = std::atoi(argv[1]);
  const bool king = (argc < 3) || std::atoi(argv[2]) != 0;
  obs::Reporter rep("convex_area_tm", 0,
                    "N=" + std::to_string(N) + " king=" + std::to_string(king));

  std::unordered_map<int, Vec> dp;
  dp.reserve(4 * (size_t)N);
  Vec total(N + 1);
  for (int w = 1; w <= N; ++w) {
    Vec v(N + 1);
    v[w] = 1;
    dp.emplace(Key(w, 0, 0), std::move(v));
    total[w] += 1;
  }

  uint64_t iter = 0;
  while (!dp.empty()) {
    std::unordered_map<int, Vec> ndp;
    ndp.reserve(dp.size() * 2);
    for (auto& kv : dp) {
      const int k = kv.first, w = k >> 2, pl = (k >> 1) & 1, pr = k & 1;
      Vec& vec = kv.second;
      int nmin = -1;
      for (int i = 0; i <= N; ++i)
        if (vec[i] != 0) { nmin = i; break; }
      if (nmin < 0) continue;

      for (int wp = 1; wp <= N - nmin; ++wp) {
        const int lo = (pl == 0) ? (king ? -wp : 1 - wp) : 0;
        const int hi = (pr == 0) ? (king ? w : w - 1) : w - wp;
        if (lo > hi) continue;
        const int splitL = w - wp;

        Range plr[2];
        int nplr = 0;
        if (pl == 0) {
          plr[nplr++] = {0, lo, std::min(hi, 0)};
          plr[nplr++] = {1, std::max(lo, 1), hi};
        } else {
          plr[nplr++] = {1, lo, hi};
        }
        Range prr[2];
        int nprr = 0;
        if (pr == 0) {
          prr[nprr++] = {0, splitL, hi};
          prr[nprr++] = {1, lo, splitL - 1};
        } else {
          prr[nprr++] = {1, lo, hi};
        }

        const int hiN0 = N - wp;
        for (int i = 0; i < nplr; ++i) {
          if (plr[i].lo > plr[i].hi) continue;
          for (int j = 0; j < nprr; ++j) {
            if (prr[j].lo > prr[j].hi) continue;
            const int a = std::max(plr[i].lo, prr[j].lo);
            const int b = std::min(plr[i].hi, prr[j].hi);
            if (a > b) continue;
            const unsigned long count = (unsigned long)(b - a + 1);
            const int tkey = Key(wp, plr[i].val, prr[j].val);
            auto it = ndp.find(tkey);
            if (it == ndp.end())
              it = ndp.emplace(tkey, Vec(N + 1)).first;
            Vec& tgt = it->second;
            for (int n0 = nmin; n0 <= hiN0; ++n0) {
              if (vec[n0] == 0) continue;
              mpz_ptr dst = tgt[n0 + wp].get_mpz_t();
              mpz_srcptr src = vec[n0].get_mpz_t();
              if (count == 1)
                mpz_add(dst, dst, src);
              else
                mpz_addmul_ui(dst, src, count);
            }
          }
        }
      }
    }
    dp = std::move(ndp);
    for (auto& kv : dp) {
      Vec& vec = kv.second;
      for (int n0 = 0; n0 <= N; ++n0)
        if (vec[n0] != 0) total[n0] += vec[n0];
    }
    ++iter;
    rep.beat((double)iter, "dp_states=" + std::to_string(dp.size()));
  }

  std::string out;
  for (int n = 1; n <= N; ++n) {
    if (n > 1) out += ", ";
    out += total[n].get_str();
  }
  std::fputs(out.c_str(), stdout);
  std::fputc('\n', stdout);
  rep.done("n_max=" + std::to_string(N));
  return 0;
}
