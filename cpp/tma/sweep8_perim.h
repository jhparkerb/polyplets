// Perimeter-resolved square-8 sweep: the (size, edge-perimeter) joint
// distribution by the column transfer matrix. Method-B counterpart to the
// generator's `g2 --perimeter`; cross-checking the two distributions exercises
// the transfer matrix at finer grain than totals (task #18).
//
// ISOLATED from the production counting path: it reuses the validated
// transition (stepColumnSquare8), viable-mask generator, and admissible prune
// (completionLowerBound), but keeps its own state store (a (size,perim) table
// per signature). The counting engine in sweep8.h is not touched.
//
// Edge perimeter is additive per column: adding a column of `cells` cells adds
//   4*cells - 2*(vertical adjacencies within the new column)
//           - 2*(horizontal adjacencies to the occupied cells one column left)
// and diagonal contacts never reduce edge perimeter -- so it folds cleanly into
// the DP as a second index. (Closure adds nothing.) Feasible only at small n
// (the per-state row is (maxn+1)*(perim+1) wide), which is all a cross-check
// needs.

#pragma once

#include <cstring>
#include <utility>
#include <vector>

#include "signature.h"
#include "statedb.h"            // u64, Sig, FlatDB::hashSig
#include "transition_square8.h"

// open-addressing Sig -> u64[stride]; stride chosen by the caller.
struct PerimDB {
  std::vector<Sig> keys;
  std::vector<u64> vals;
  std::vector<uint8_t> used;
  size_t cap, cnt, stride;
  explicit PerimDB(size_t stride_, size_t initCap = 16)
      : cap(initCap), cnt(0), stride(stride_) {
    keys.resize(cap); vals.resize(cap * stride); used.assign(cap, 0);
  }
  bool empty() const { return cnt == 0; }
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; }
  template <class F> void for_each(F&& fn) const {
    for (size_t i = 0; i < cap; ++i) if (used[i]) fn(keys[i], &vals[i * stride]);
  }
  void grow() {
    auto ok = std::move(keys); auto ov = std::move(vals); auto ou = std::move(used);
    const size_t oc = cap; cap *= 2; cnt = 0;
    keys.resize(cap); vals.resize(cap * stride); used.assign(cap, 0);
    for (size_t i = 0; i < oc; ++i)
      if (ou[i]) { u64* d = slot(ok[i]); std::memcpy(d, &ov[i * stride], stride * sizeof(u64)); }
  }
  u64* slot(const Sig& k) {
    if ((cnt + 1) * 10 >= cap * 7) grow();
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) { if (keys[h] == k) return &vals[h * stride]; h = (h + 1) & (cap - 1); }
    used[h] = 1; keys[h] = k; ++cnt;
    u64* row = &vals[h * stride]; std::memset(row, 0, stride * sizeof(u64)); return row;
  }
};

// Accumulate height-H contributions into result[size*Pp + perim], Pp = Pmax+1.
inline void sweepSquare8HeightPerim(int H, int maxn, int Pmax,
                                    std::vector<u64>& result) {
  const int Pp = Pmax + 1;
  const size_t stride = static_cast<size_t>(maxn + 1) * Pp;
  PerimDB db(stride), next(stride);
  Sig seed; std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;  // size 0, perimeter 0

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    next.clear();
    db.for_each([&](const Sig& sig, const u64* row) {
      int ms = -1;
      for (int s = 0; s <= maxn && ms < 0; ++s)
        for (int p = 0; p < Pp; ++p) if (row[s * Pp + p]) { ms = s; break; }
      if (ms < 0) return;
      int comps = 0;
      for (int j = 0; j < H; ++j) if (sig.b[j] > comps) comps = sig.b[j];
      if (comps == 1 && sig.b[H] && sig.b[H + 1])         // closure: harvest as-is
        for (size_t i = 0; i < stride; ++i) if (row[i]) result[i] += row[i];
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        int vert = 0;
        for (int r = 0; r + 1 < H; ++r)
          if (((mask >> r) & 1u) && ((mask >> (r + 1)) & 1u)) ++vert;
        int horiz = 0;
        for (int r = 0; r < H; ++r)
          if (((mask >> r) & 1u) && sig.b[r]) ++horiz;     // edge to column on the left
        const int dper = 4 * cells - 2 * vert - 2 * horiz; // always >= 2
        u64* dst = next.slot(out);
        for (int s = 0; s + cells <= maxn; ++s)
          for (int p = 0; p + dper < Pp; ++p) {
            const u64 v = row[s * Pp + p];
            if (v) dst[(s + cells) * Pp + (p + dper)] += v;
          }
      });
    });
    std::swap(db, next);
  }
}

// Full (size, perimeter) distribution summed over heights, sizes 1..maxn.
inline std::vector<u64> sweepSquare8Perim(int maxn, int Pmax) {
  const int Pp = Pmax + 1;
  std::vector<u64> result(static_cast<size_t>(maxn + 1) * Pp, 0);
  for (int H = 1; H <= maxn; ++H) sweepSquare8HeightPerim(H, maxn, Pmax, result);
  return result;
}
