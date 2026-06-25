// T3 implementation (1): plain hash map from signature to counts-by-size.
//
// Deliberately the dumbest thing that works -- this is THE
// designed-to-be-replaced component (chunked+compressed sets, then
// out-of-core, are later drop-ins behind the same few operations).

#pragma once

#include <algorithm>
#include <cstdint>
#include <cstring>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "signature.h"

using u64 = std::uint64_t;
using Counts = std::vector<u64>;  // index = animal size, 0..maxn
using StateDB = std::unordered_map<std::string, Counts>;  // square-4 path

struct SweepResults {
  // byHeight[h][n] = fixed animals with n cells and height exactly h
  std::vector<Counts> byHeight;
  Counts totals;
  // calibration: peak number of distinct boundary signatures held at once
  // (the memory bottleneck), and the boundary height where that peak occurred.
  u64 peakStates = 0;
  int peakHeight = 0;
};

// Sum per-height rows into res.totals (shared by the plain and checkpoint
// drivers, which both fill res.byHeight one height at a time).
inline void accumulateTotals(SweepResults& res, int maxn) {
  for (int h = 1; h <= maxn; ++h)
    for (int n = 1; n <= maxn; ++n) res.totals[n] += res.byHeight[h][n];
}

// Accumulate src into db[sig], shifting sizes by `shift` (1 when the
// transition occupied a cell), dropping sizes that exceed maxn.
inline void addCounts(StateDB& db, const std::string& sig, const Counts& src,
                      int shift, int maxn) {
  Counts& dst = db[sig];
  if (dst.empty()) dst.assign(maxn + 1, 0);
  for (int n = 0; n + shift <= maxn; ++n)
    if (src[n]) dst[n + shift] += src[n];
}

// --- Flat open-addressing state store for the hot square-8 path ---
//
// Sig -> counts-by-size, all storage in three flat arrays (linear probing): no
// per-state allocation and no pointer chasing, unlike unordered_map. Counts
// rows live in one contiguous u64 array, `stride` (= maxn+1) apart; the row is
// zeroed on first insert, so clear() only has to reset the `used` flags (values
// are never bulk-zeroed, which would dominate at tens of millions of slots).
// Capacity is a power of two; grows by doubling at load factor 0.85 (linear
// probing with FNV-1a is fine that dense; steady slack ~1.43x -> ~1.18x).
//
// TODO(simplify): this open-addressing store is copied four times -- FlatDB (here),
// FlatDB32 (sweep8_modp.h, u32 vals), and HoleDB/PerimDB (sweep8_holes/perim.h, caller
// stride). They differ only in value type and fixed-vs-passed stride => one template
// OAMap<V>. The copies have already DRIFTED: PerimDB grows at load factor 0.70
// (sweep8_perim.h: cap*7) while everyone else uses 0.85 -- exactly the divergence a
// single template would prevent. Store-first refactor (pure plumbing, for_each-only read
// contract => cannot change byte-output); do it gate-protected, separate from a sweep.
struct FlatDB {
  std::vector<Sig> keys;
  std::vector<u64> vals;
  std::vector<uint8_t> used;
  size_t cap, cnt, stride;

  explicit FlatDB(int maxn, size_t initCap = 16)
      : cap(initCap), cnt(0), stride(maxn + 1) {
    keys.resize(cap);
    vals.resize(cap * stride);
    used.assign(cap, 0);
  }
  size_t size() const { return cnt; }
  bool empty() const { return cnt == 0; }
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; }

  // Pre-size (on a fresh/empty store) to hold ~nStates without growing. grow()
  // moves the old arrays aside and allocates the new 2x arrays before freeing the
  // old, so the doubling rehash momentarily holds both -- typically the RSS
  // high-water. Reserving to a measured/predicted peak skips every grow (no
  // transient, no rehash cost). Safe: over-reserve wastes a little, under-reserve
  // just grows as before. Must be called before any insert (resets to empty).
  void reserve(size_t nStates) {
    size_t want = cap;
    while ((nStates + 1) * 100 >= want * 85) want <<= 1;
    if (want == cap) return;
    cap = want;
    keys.resize(cap);
    vals.resize(cap * stride);
    used.assign(cap, 0);
    cnt = 0;
  }

  // Visit each live entry as (key, counts row) -- the only read-back path, so
  // callers never touch the slot layout (keys/vals/used/stride) directly.
  template <class F>
  void for_each(F&& fn) const {
    for (size_t i = 0; i < cap; ++i)
      if (used[i]) fn(keys[i], &vals[i * stride]);
  }

  static size_t hashSig(const Sig& k) {  // FNV-1a over the fixed bytes, 8 at a time
    std::uint64_t w[SIGMAX / 8];
    std::memcpy(w, k.b, SIGMAX);
    size_t h = 1469598103934665603ull;
    for (size_t i = 0; i < SIGMAX / 8; ++i) { h ^= w[i]; h *= 1099511628211ull; }
    return h;
  }

  void grow() {
    std::vector<Sig> ok = std::move(keys);
    std::vector<u64> ov = std::move(vals);
    std::vector<uint8_t> ou = std::move(used);
    const size_t oldcap = cap;
    cap *= 2; cnt = 0;
    keys.resize(cap);
    vals.resize(cap * stride);
    used.assign(cap, 0);
    for (size_t i = 0; i < oldcap; ++i)
      if (ou[i]) {
        u64* dst = slot(ok[i]);
        std::memcpy(dst, &ov[i * stride], stride * sizeof(u64));
      }
  }

  // Find or insert; returns a pointer to the counts row (zeroed on insert).
  u64* slot(const Sig& k) {
    if ((cnt + 1) * 100 >= cap * 85) grow();
    size_t h = hashSig(k) & (cap - 1);
    while (used[h]) {
      if (keys[h] == k) return &vals[h * stride];
      h = (h + 1) & (cap - 1);
    }
    used[h] = 1;
    keys[h] = k;
    ++cnt;
    u64* row = &vals[h * stride];
    std::memset(row, 0, stride * sizeof(u64));
    return row;
  }
};

// Smallest animal size with a nonzero count in a flat counts row (0..maxn).
inline int minSizeRow(const u64* c, int maxn) {
  for (int n = 1; n <= maxn; ++n)
    if (c[n]) return n;
  return c[0] ? 0 : -1;
}

// Accumulate src row into db[sig], shifting sizes by `shift`, dropping > maxn.
inline void addCounts(FlatDB& db, const Sig& sig, const u64* src, int shift,
                      int maxn) {
  u64* dst = db.slot(sig);
  for (int n = 0; n + shift <= maxn; ++n)
    if (src[n]) dst[n + shift] += src[n];
}
