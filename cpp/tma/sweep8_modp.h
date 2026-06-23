// R3: u32 mod-p plain-a(n) sweep. The counts-by-size row is stored as uint32_t
// (HALF the u64 row -> ~1.73x less memory, the row being ~84% of per-state
// footprint). Counts are kept mod p; CRT over 2-3 primes recovers the exact a(n)
// (which fits u64 for n <= ~50). Trades compute (one sweep per prime) for RAM --
// ideal for the memory-bound, time-rich reach regime. Composes with R1 (--fold:
// pass fold=true), so R1xR3 ~ 2 x 1.73 ~ 3.4x less RAM.
//
// Self-contained (its own u32 FlatDB) so the gated exact u64 engine is untouched.
// Correctness is by construction: addition mod p is a ring homomorphism, so the
// whole DP commutes with reduction mod p; the small-scale gate confirms
// CRT(sum_H B_H(n) mod p_i) == exact a(n).
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "signature.h"
#include "statedb.h"             // FlatDB::hashSig, u64
#include "transition_square8.h"  // stepColumnSquare8, forEachViableMask

// u32 open-addressing store, structurally identical to FlatDB but half-width vals.
struct FlatDB32 {
  std::vector<Sig> keys;
  std::vector<std::uint32_t> vals;
  std::vector<std::uint8_t> used;
  size_t cap, cnt, stride;

  explicit FlatDB32(int maxn, size_t initCap = 16)
      : cap(initCap), cnt(0), stride(maxn + 1) {
    keys.resize(cap);
    vals.resize(cap * stride);
    used.assign(cap, 0);
  }
  size_t size() const { return cnt; }
  bool empty() const { return cnt == 0; }
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; }
  // clear() only zeroes the used flags; freeMem() actually RETURNS the backing
  // storage to the allocator (shrink to the 16-slot seed). The blocked store
  // (B, sweep8_modp_blocked.h) calls this on a db partition the instant it is
  // drained, so the live high-water is ~1x (next) rather than db+next.
  void freeMem() {
    keys = std::vector<Sig>(16);
    vals = std::vector<std::uint32_t>(16 * stride);
    used = std::vector<std::uint8_t>(16, 0);
    cap = 16; cnt = 0;
  }

  template <class F>
  void for_each(F&& fn) const {
    for (size_t i = 0; i < cap; ++i)
      if (used[i]) fn(keys[i], &vals[i * stride]);
  }
  void grow() {
    std::vector<Sig> ok = std::move(keys);
    std::vector<std::uint32_t> ov = std::move(vals);
    std::vector<std::uint8_t> ou = std::move(used);
    const size_t oldcap = cap;
    cap *= 2; cnt = 0;
    keys.resize(cap);
    vals.resize(cap * stride);
    used.assign(cap, 0);
    for (size_t i = 0; i < oldcap; ++i)
      if (ou[i])
        std::memcpy(slot(ok[i]), &ov[i * stride], stride * sizeof(std::uint32_t));
  }
  std::uint32_t* slot(const Sig& k) {
    if ((cnt + 1) * 100 >= cap * 85) grow();
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) {
      if (keys[h] == k) return &vals[h * stride];
      h = (h + 1) & (cap - 1);
    }
    used[h] = 1; keys[h] = k; ++cnt;
    std::uint32_t* row = &vals[h * stride];
    std::memset(row, 0, stride * sizeof(std::uint32_t));
    return row;
  }
};

inline int minSizeRow32(const std::uint32_t* c, int maxn) {
  for (int n = 1; n <= maxn; ++n)
    if (c[n]) return n;
  return c[0] ? 0 : -1;
}

// dst[n+shift] = (dst[n+shift] + src[n]) mod p. src,dst < p < 2^31 so the u64
// intermediate never overflows.
inline void addCountsModP32(FlatDB32& db, const Sig& sig, const std::uint32_t* src,
                            int shift, int maxn, std::uint32_t p) {
  std::uint32_t* dst = db.slot(sig);
  for (int n = 0; n + shift <= maxn; ++n)
    if (src[n])
      dst[n + shift] = static_cast<std::uint32_t>(
          (static_cast<std::uint64_t>(dst[n + shift]) + src[n]) % p);
}

// One strip height mod p: B_H(n) mod p for n=0..maxn. fold=true applies the R1
// vertical-mirror fold. peakStates is updated with this height's high-water mark.
inline std::vector<std::uint32_t> sweepSquare8HeightModP(int H, int maxn,
                                                         std::uint32_t p, bool fold,
                                                         u64& peakStates) {
  std::vector<std::uint32_t> row(maxn + 1, 0);
  FlatDB32 db(maxn), next(maxn);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1u % p;
  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > peakStates) peakStates = db.size();
    next.clear();
    db.for_each([&](const Sig& sig, const std::uint32_t* counts) {
      const int ms = minSizeRow32(counts, maxn);
      if (ms < 0) return;
      int comps = 0;
      for (int j = 0; j < H; ++j)
        if (sig.b[j] > comps) comps = sig.b[j];
      if (comps == 1 && sig.b[H] && sig.b[H + 1])
        for (int n = 1; n <= maxn; ++n)
          if (counts[n])
            row[n] = static_cast<std::uint32_t>(
                (static_cast<std::uint64_t>(row[n]) + counts[n]) % p);
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        if (fold) foldSig(out, H);
        addCountsModP32(next, out, counts, cells, maxn, p);
      });
    });
    std::swap(db, next);
  }
  return row;
}
