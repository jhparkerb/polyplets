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
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
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

// Multithreaded strip-height sweep mod p -- LOCK-FREE. The per-output mutex of a naive
// sharded mirror caps scaling at ~2.5x on this DP (measured: 19-30s sys time = futex
// contention, and more shards barely helps -> it is the lock OP, not collisions). So we
// avoid shared writes entirely: each column has two parallel passes with a join between.
//   PASS 1 (expand): thread t drains source shards t,t+T,... and routes every output to
//     its OWN per-thread dest shards loc[t][sh] -- no other thread touches loc[t], so no
//     lock. comps==1 harvest -> per-thread u64 row (raw sum can't overflow at our counts).
//   PASS 2 (merge): thread u owns dest shards u,u+T,... ; it clears db[s] and folds in
//     loc[0..T-1][s] (mod p) -- each db[s] written by exactly one thread, each loc[t][s]
//     read by exactly one thread, so again no lock. db is reused as the merge target, so
//     after pass 2 it holds the next column (no swap). Costs a second insert per state
//     (loc then db) but removes all contention. Correctness is by construction (which
//     states/counts are produced is independent of sharding/threading) and gated
//     byte-identical vs the serial path per (H,p,fold).
inline std::vector<std::uint32_t> sweepSquare8HeightModPMT(int H, int maxn,
                                                           std::uint32_t p, bool fold,
                                                           u64& peakStates,
                                                           int nthreads) {
  std::vector<std::uint32_t> row(maxn + 1, 0);
  int S = 64;
  int shardMult = 16;  // TMA_SHARD_MULT: dest shards per thread (>= for merge balance)
  if (const char* e = std::getenv("TMA_SHARD_MULT")) shardMult = std::atoi(e);
  while (S < shardMult * nthreads) S <<= 1;  // shards: power of two, >> nthreads
  std::vector<FlatDB32> dbS;
  dbS.reserve(S);
  for (int s = 0; s < S; ++s) dbS.emplace_back(maxn);
  std::vector<std::vector<FlatDB32>> loc(nthreads);  // loc[t][s]: thread t's dest shards
  for (int t = 0; t < nthreads; ++t) {
    loc[t].reserve(S);
    for (int s = 0; s < S; ++s) loc[t].emplace_back(maxn);
  }
  { Sig seed; std::memset(seed.b, 0, SIGMAX);
    dbS[FlatDB::hashSig(seed) & (S - 1)].slot(seed)[0] = 1u % p; }

  for (int col = 0; col <= maxn; ++col) {
    u64 total = 0;
    for (int s = 0; s < S; ++s) total += dbS[s].size();
    if (total == 0) break;
    if (total > peakStates) peakStates = total;
    for (int t = 0; t < nthreads; ++t)
      for (int s = 0; s < S; ++s) loc[t][s].clear();

    std::vector<std::vector<u64>> localRow(nthreads, std::vector<u64>(maxn + 1, 0));
    auto expand = [&](int t) {
      std::vector<u64>& lrow = localRow[t];
      std::vector<FlatDB32>& mine = loc[t];
      for (int s = t; s < S; s += nthreads)  // thread t owns source shards t,t+T,...
        dbS[s].for_each([&](const Sig& sig, const std::uint32_t* counts) {
          const int ms = minSizeRow32(counts, maxn);
          if (ms < 0) return;
          int comps = 0;
          for (int j = 0; j < H; ++j)
            if (sig.b[j] > comps) comps = sig.b[j];
          if (comps == 1 && sig.b[H] && sig.b[H + 1])
            for (int n = 1; n <= maxn; ++n)
              if (counts[n]) lrow[n] += counts[n];
          forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
            Sig out;
            if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
            const int cells = __builtin_popcount(mask);
            if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
            if (fold) foldSig(out, H);
            addCountsModP32(mine[FlatDB::hashSig(out) & (S - 1)], out, counts, cells,
                            maxn, p);  // thread-local: no lock
          });
        });
    };
    std::vector<std::thread> th;
    for (int t = 0; t < nthreads; ++t) th.emplace_back(expand, t);
    for (auto& x : th) x.join();
    th.clear();

    // merge each dest shard (one owner thread) into dbS -> next column, no lock, no swap
    auto merge = [&](int u) {
      for (int s = u; s < S; s += nthreads) {
        dbS[s].clear();
        for (int t = 0; t < nthreads; ++t)
          loc[t][s].for_each([&](const Sig& sig, const std::uint32_t* c) {
            addCountsModP32(dbS[s], sig, c, 0, maxn, p);
          });
      }
    };
    for (int u = 0; u < nthreads; ++u) th.emplace_back(merge, u);
    for (auto& x : th) x.join();

    for (int t = 0; t < nthreads; ++t)
      for (int n = 1; n <= maxn; ++n)
        row[n] = static_cast<std::uint32_t>(
            (static_cast<u64>(row[n]) + localRow[t][n]) % p);
  }
  return row;
}

// One strip height mod p: B_H(n) mod p for n=0..maxn. fold=true applies the R1
// vertical-mirror fold. peakStates is updated with this height's high-water mark.
// nthreads>1 selects the sharded multithreaded path (above); nthreads<=1 keeps the
// serial path byte-identical for the gated callers.
inline std::vector<std::uint32_t> sweepSquare8HeightModP(int H, int maxn,
                                                         std::uint32_t p, bool fold,
                                                         u64& peakStates,
                                                         int nthreads = 1) {
  if (nthreads > 1) return sweepSquare8HeightModPMT(H, maxn, p, fold, peakStates, nthreads);
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
