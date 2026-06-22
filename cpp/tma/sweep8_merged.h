// C3: merged reach engine = R1 (vertical-mirror fold) x R2 (ranged counts-row) x R3
// (u32 mod-p counts). The three levers are orthogonal -- R1 canonicalizes the Sig KEY,
// R2 stores only each row's nonzero support, R3 changes the count TYPE to u32 mod p --
// so they stack. vs the exact u64 engine: ~2x (fold) x ~2x (ranged) x ~2x (u32) ~ 8x
// less RAM per prime; CRT over ~3 primes recovers the exact a(n). This is the in-RAM
// stack that brings a(24)/a(25) into a 122 GB budget (a(23) already fits with R1xR2).
//
// Built directly on the validated ranged sweep (sweep8_ranged.h): same two-pass ranged
// storage and same `fold` key-canonicalization, with the row arena narrowed to u32 and
// every accumulation reduced mod p. Gate: CRT(merged mod p_i) == exact a(n).
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "signature.h"
#include "statedb.h"             // FlatDB::hashSig, u64
#include "sweep8_ranged.h"       // MinDB (pass-1 sizing map, count-type independent)
#include "transition_square8.h"

// Ranged store with a u32 mod-p arena (R2 x R3). Identical index/sizing logic to RangedDB;
// only the run payload is u32 instead of u64.
struct RangedDBModP {
  std::vector<Sig> keys;
  std::vector<std::uint8_t> used, lo;
  std::vector<u64> roff;
  std::vector<std::uint32_t> arena;     // packed runs, values in [0, p)
  size_t cap, cnt, arenaUsed;
  int maxn;
  explicit RangedDBModP(int mx, size_t c = 16)
      : cap(c), cnt(0), arenaUsed(0), maxn(mx) {
    keys.resize(cap); used.assign(cap, 0); lo.assign(cap, 0); roff.assign(cap, 0);
  }
  size_t size() const { return cnt; }
  bool empty() const { return cnt == 0; }
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; arenaUsed = 0; }
  void ensureIdx(size_t need) {
    size_t want = cap;
    while ((need + 1) * 100 >= want * 85) want <<= 1;
    if (want != cap) {
      cap = want;
      keys.resize(cap); used.assign(cap, 0); lo.resize(cap); roff.resize(cap);
    }
  }
  void prepArena(size_t total) { arena.assign(total, 0); }
  void insert(const Sig& k, std::uint8_t loVal) {
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) { if (keys[h] == k) return; h = (h + 1) & (cap - 1); }
    used[h] = 1; keys[h] = k; lo[h] = loVal; roff[h] = arenaUsed; ++cnt;
    arenaUsed += static_cast<size_t>(maxn - loVal + 1);
  }
  std::uint32_t* find(const Sig& k, int& loOut) {
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) {
      if (keys[h] == k) { loOut = lo[h]; return &arena[roff[h]]; }
      h = (h + 1) & (cap - 1);
    }
    return nullptr;
  }
  template <class F> void for_each(F&& fn) const {
    for (size_t i = 0; i < cap; ++i)
      if (used[i]) fn(keys[i], static_cast<int>(lo[i]), &arena[roff[i]]);
  }
  u64 bytes() const {  // u32 arena -> 4 bytes/entry (vs 8 for the exact ranged store)
    return static_cast<u64>(cap) * (sizeof(Sig) + 2 + 8) + arena.size() * 4;
  }
};

// One strip height: folded + ranged + counts mod p (u32). Returns B_H(n) mod p, n=0..maxn.
// p must be < 2^31 so a single `(a+b)` of two reduced values fits u32 before the mod.
inline std::vector<u64> sweepSquare8HeightMerged(int H, int maxn, std::uint32_t p,
                                                 u64& peakStates, u64& peakBytes,
                                                 bool fold = true) {
  std::vector<u64> row(maxn + 1, 0);    // u64 harvest accumulator, reduced mod p at the end
  RangedDBModP db(maxn), next(maxn);
  MinDB mins;
  { Sig seed; std::memset(seed.b, 0, SIGMAX);
    db.ensureIdx(1); db.prepArena(maxn + 1); db.insert(seed, 0);
    int sl; db.find(seed, sl)[0] = 1; }

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > peakStates) peakStates = db.size();

    db.for_each([&](const Sig& sig, int slo, const std::uint32_t* r) {
      int comps = 0;
      for (int j = 0; j < H; ++j) if (sig.b[j] > comps) comps = sig.b[j];
      if (comps == 1 && sig.b[H] && sig.b[H + 1])
        for (int n = slo; n <= maxn; ++n) row[n] += r[n - slo];
    });

    // PASS 1: size every target's row (count-type independent -- same as exact ranged)
    mins.clear();
    db.for_each([&](const Sig& sig, int slo, const std::uint32_t*) {
      forEachViableMask(sig, H, maxn - slo, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (slo + cells + completionLowerBound(out.b, H) > maxn) return;
        if (fold) foldSig(out, H);
        mins.relax(out, static_cast<std::uint8_t>(slo + cells));
      });
    });

    size_t arenaTotal = 0;
    for (size_t i = 0; i < mins.cap; ++i)
      if (mins.used[i]) arenaTotal += static_cast<size_t>(maxn - mins.lo[i] + 1);
    next.clear();
    next.ensureIdx(mins.cnt);
    next.prepArena(arenaTotal);
    for (size_t i = 0; i < mins.cap; ++i)
      if (mins.used[i]) next.insert(mins.keys[i], mins.lo[i]);

    // PASS 2: accumulate source rows (shifted) into target runs, reduced mod p each add
    db.for_each([&](const Sig& sig, int slo, const std::uint32_t* r) {
      forEachViableMask(sig, H, maxn - slo, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (slo + cells + completionLowerBound(out.b, H) > maxn) return;
        if (fold) foldSig(out, H);
        int tlo; std::uint32_t* dst = next.find(out, tlo);
        for (int n = slo; n + cells <= maxn; ++n)
          if (r[n - slo]) {
            std::uint32_t& e = dst[n + cells - tlo];
            e += r[n - slo];             // both < p < 2^31 -> sum < 2^32, fits u32
            if (e >= p) e -= p;          // conditional subtract: no division in the hot loop
          }
      });
    });

    const u64 b = db.bytes() + next.bytes() +
                  static_cast<u64>(mins.cap) * (sizeof(Sig) + 2);
    if (b > peakBytes) peakBytes = b;
    std::swap(db, next);
  }
  for (int n = 0; n <= maxn; ++n) row[n] %= p;   // Sum_states (mod p) -> B_H(n) mod p
  return row;
}
