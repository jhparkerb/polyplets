// Hole-resolved square-8 sweep: the (size, #holes) joint distribution by the
// column transfer matrix (#28). Method-B counterpart to the generator's
// `g2 square8 --holes`; removes the per-animal flood, so it reaches the same n
// as the bare count instead of capping at n=14.
//
// ISOLATED from the production counting path, exactly like sweep8_perim.h: it
// reuses the validated transition (stepColumnSquare8), viable-mask generator,
// and admissible prune (completionLowerBound), but keeps its own state store (a
// (size,#holes) table per signature). sweep8.h is not touched.
//
// Holes ride as a second additive index via the Euler characteristic (see
// euler.h): for the partial image (columns placed so far, empty beyond),
//   holes-so-far = comps - E,   E maintained by closedEulerDelta4 per column.
// comps = the boundary's component count (every live component touches the
// frontier -- a stranded one is killed Dead -- so it equals the partial image's
// component count). A transition shifts the hole index by
//   dHoles = (comps_new - comps_old) - closedEulerDelta4(occ_old, mask)/4
// which is >= 0: adding a column left-to-right can only seal a rightward-open
// cavity into a new hole, never remove an already-bounded one. Closure adds
// nothing (the boundary's right-edge windows are already folded in every step),
// so a completed animal is harvested at its current hole index as-is.
//
// PRIMARY convention only (Conn::FG8 -> 4-connected-background holes, the Jordan
// dual / OEIS-A389193 convention = `g2 --holes`). The companion 8-bg count needs
// the animal's 4-adjacency component count, which this 8-adjacency union-find
// does not track; it stays on the flood (capped at n=14) for now.

#pragma once

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <utility>
#include <vector>

#include "euler.h"
#include "signature.h"
#include "statedb.h"            // u64, Sig, FlatDB::hashSig
#include "transition_square8.h"

// open-addressing Sig -> u64[stride]; stride chosen by the caller (mirrors the
// PerimDB store in sweep8_perim.h -- same generic shape, named for this path).
struct HoleDB {
  std::vector<Sig> keys;
  std::vector<u64> vals;
  std::vector<uint8_t> used;
  size_t cap, cnt, stride;
  explicit HoleDB(size_t stride_, size_t initCap = 16)
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

// Component count of a canonical boundary = its max label.
inline int boundaryComps(const Sig& sig, int H) {
  int c = 0;
  for (int j = 0; j < H; ++j) if (sig.b[j] > c) c = sig.b[j];
  return c;
}

// Occupancy bitmask of a boundary signature (bit r set = row r occupied).
inline std::uint32_t boundaryOcc(const Sig& sig, int H) {
  std::uint32_t m = 0;
  for (int r = 0; r < H; ++r) if (sig.b[r]) m |= 1u << r;
  return m;
}

// Accumulate height-H contributions into result[size*Kp + holes], Kp = Kmax+1.
// mod > 0 reduces every count mod `mod` (B_{H,k}(n) mod p, no overflow -> any n,
// for mod-p GF recovery, #5b); mod == 0 is the exact u64 path (unchanged). All
// counts stay < mod < 2^31, so each (a+b) < 2^32 fits u64 before reduction.
// hdrop: when true, contributions whose hole index exceeds Kmax are DROPPED
// rather than aborting. Exact for every slice k <= Kmax, because dHoles >= 0
// (holes only seal, never reopen) -- a partial state already over Kmax can never
// produce a final animal with <= Kmax holes. Lets a small Kmax bound RAM to
// O(D_H * maxn * Kmax) so high maxn (many GF terms) fits in memory. #5b.
inline void sweepSquare8HeightHoles(int H, int maxn, int Kmax, Conn conn,
                                    std::vector<u64>& result, u64 mod = 0,
                                    bool hdrop = false) {
  const int Kp = Kmax + 1;
  const size_t stride = static_cast<size_t>(maxn + 1) * Kp;
  HoleDB db(stride), next(stride);
  Sig seed; std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;  // size 0, holes 0

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    next.clear();
    db.for_each([&](const Sig& sig, const u64* row) {
      int ms = -1;
      for (int s = 0; s <= maxn && ms < 0; ++s)
        for (int h = 0; h < Kp; ++h) if (row[s * Kp + h]) { ms = s; break; }
      if (ms < 0) return;
      const int comps = boundaryComps(sig, H);
      if (comps == 1 && sig.b[H] && sig.b[H + 1])         // closure: harvest as-is
        for (size_t i = 0; i < stride; ++i)
          if (row[i]) result[i] = mod ? (result[i] + row[i]) % mod
                                       : result[i] + row[i];
      const std::uint32_t occ = boundaryOcc(sig, H);
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        const int compsNew = boundaryComps(out, H);
        const int dE4 = closedEulerDelta4(occ, mask, H, conn);  // 4 * dEuler
        if (dE4 & 3) {  // must be a multiple of 4 (A is 4*E of a closed image)
          std::fprintf(stderr, "euler delta not /4: %d\n", dE4); std::abort();
        }
        const int dHoles = (compsNew - comps) - dE4 / 4;
        u64* dst = next.slot(out);
        for (int s = 0; s + cells <= maxn; ++s)
          for (int h = 0; h < Kp; ++h) {
            const u64 v = row[s * Kp + h];
            if (!v) continue;
            const int nh = h + dHoles;
            if (nh >= Kp) {
              if (hdrop) continue;     // drop: exact for all k <= Kmax (#5b)
              std::fprintf(stderr,     // else fail loud, never silently truncate
                  "hole index out of range: %d (Kmax=%d); raise --kmax\n", nh, Kmax);
              std::abort();
            }
            u64& cell = dst[(s + cells) * Kp + nh];
            cell = mod ? (cell + v) % mod : cell + v;
          }
      });
    });
    std::swap(db, next);
  }
}

// Full (size, #holes) distribution summed over heights, sizes 1..maxn.
inline std::vector<u64> sweepSquare8Holes(int maxn, int Kmax, Conn conn) {
  const int Kp = Kmax + 1;
  std::vector<u64> result(static_cast<size_t>(maxn + 1) * Kp, 0);
  for (int H = 1; H <= maxn; ++H)
    sweepSquare8HeightHoles(H, maxn, Kmax, conn, result);
  return result;
}
