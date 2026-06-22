// R2: ranged counts-row sweep. Each per-state row is stored only on its nonzero
// support [minSize, maxn] -- a u8 `lo` plus a packed run in a shared arena -- not
// the full [0, maxn]. Measured ~2x less RAM (docs/ranged-row-r2.md), growing with N.
//
// The support WIDENS under accumulation (a later source with fewer cells lowers a
// target's minSize), so rows cannot be sized in one pass. Each column therefore
// runs TWO passes over the (validated) transition:
//   pass 1 (size):  minSize[target] = min over sources of (source.lo + cells)
//   pass 2 (accum): add each source's row, shifted, into the pre-sized target run
// Correct by construction: the omitted [0,minSize) entries are all zero, so the
// counts (hence B_H, hence a(n)) are identical to the exact sweep -- the gate checks
// it. Self-contained; the exact u64 engine in sweep8.h is untouched. Serial (the
// memory win, not throughput, is the point of this gate).
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "signature.h"
#include "statedb.h"             // FlatDB::hashSig, u64
#include "transition_square8.h"

// Pass-1 map: Sig -> minSize (u8). Open addressing; keys+lo grow together.
struct MinDB {
  std::vector<Sig> keys;
  std::vector<std::uint8_t> used, lo;
  size_t cap, cnt;
  explicit MinDB(size_t c = 16) : cap(c), cnt(0) {
    keys.resize(cap); used.assign(cap, 0); lo.assign(cap, 0);
  }
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; }
  void grow() {
    std::vector<Sig> ok = std::move(keys);
    std::vector<std::uint8_t> ou = std::move(used), ol = std::move(lo);
    const size_t oc = cap; cap *= 2; cnt = 0;
    keys.resize(cap); used.assign(cap, 0); lo.assign(cap, 0);
    for (size_t i = 0; i < oc; ++i) if (ou[i]) relax(ok[i], ol[i]);
  }
  // record that `Sig` can be reached with minSize <= v (keep the min)
  void relax(const Sig& k, std::uint8_t v) {
    if ((cnt + 1) * 100 >= cap * 85) grow();
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) {
      if (keys[h] == k) { if (v < lo[h]) lo[h] = v; return; }
      h = (h + 1) & (cap - 1);
    }
    used[h] = 1; keys[h] = k; lo[h] = v; ++cnt;
  }
};

// Ranged store: Sig -> (lo, run of len=maxn-lo+1 in `arena`). Built once per column
// from the pass-1 MinDB (so each row's lo is final -- no widening during accumulate).
struct RangedDB {
  std::vector<Sig> keys;
  std::vector<std::uint8_t> used, lo;
  std::vector<u64> roff;          // arena offset of each slot's run
  std::vector<u64> arena;         // packed runs
  size_t cap, cnt, arenaUsed;
  int maxn;
  explicit RangedDB(int mx, size_t c = 16)
      : cap(c), cnt(0), arenaUsed(0), maxn(mx) {
    keys.resize(cap); used.assign(cap, 0); lo.assign(cap, 0); roff.assign(cap, 0);
  }
  size_t size() const { return cnt; }
  bool empty() const { return cnt == 0; }

  // Reuse across columns (like FlatDB swap+clear) instead of reconstructing -- the
  // per-column reconstruction is allocator churn that inflates real RSS far above the
  // logical store. clear() keeps vector capacity; ensureIdx/prepArena grow only when a
  // column is the new largest, then stay.
  void clear() { std::fill(used.begin(), used.end(), 0); cnt = 0; arenaUsed = 0; }
  void ensureIdx(size_t need) {
    size_t want = cap;
    while ((need + 1) * 100 >= want * 85) want <<= 1;
    if (want != cap) {
      cap = want;
      keys.resize(cap); used.assign(cap, 0); lo.resize(cap); roff.resize(cap);
    }
  }
  void prepArena(size_t total) { arena.assign(total, 0); }  // size + zero the live runs
  // Insert a fresh state; the index must already fit (ensureIdx) and the arena be
  // pre-sized+zeroed (prepArena), so this neither grows nor zeroes -- O(1).
  void insert(const Sig& k, std::uint8_t loVal) {
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) { if (keys[h] == k) return; h = (h + 1) & (cap - 1); }
    used[h] = 1; keys[h] = k; lo[h] = loVal; roff[h] = arenaUsed; ++cnt;
    arenaUsed += static_cast<size_t>(maxn - loVal + 1);
  }
  // Locate an existing state; returns its run pointer and sets loOut. (Accum phase.)
  u64* find(const Sig& k, int& loOut) {
    size_t h = FlatDB::hashSig(k) & (cap - 1);
    while (used[h]) {
      if (keys[h] == k) { loOut = lo[h]; return &arena[roff[h]]; }
      h = (h + 1) & (cap - 1);
    }
    return nullptr;  // pass-1 guarantees every pass-2 target exists
  }
  template <class F> void for_each(F&& fn) const {
    for (size_t i = 0; i < cap; ++i)
      if (used[i]) fn(keys[i], static_cast<int>(lo[i]), &arena[roff[i]]);
  }
  u64 bytes() const {  // live footprint estimate
    return static_cast<u64>(cap) * (sizeof(Sig) + 2 + 8) + arena.size() * 8;
  }
};

// One strip height, ranged storage. Returns B_H(n) for n=0..maxn. peakBytes gets the
// high-water store footprint (db + next + MinDB) for the memory comparison.
inline std::vector<u64> sweepSquare8HeightRanged(int H, int maxn, u64& peakStates,
                                                 u64& peakBytes) {
  std::vector<u64> row(maxn + 1, 0);
  RangedDB db(maxn), next(maxn);
  MinDB mins;
  { Sig seed; std::memset(seed.b, 0, SIGMAX);
    db.ensureIdx(1); db.prepArena(maxn + 1); db.insert(seed, 0);
    int sl; db.find(seed, sl)[0] = 1; }

  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    if (db.size() > peakStates) peakStates = db.size();

    // harvest completed animals out of db
    db.for_each([&](const Sig& sig, int slo, const u64* r) {
      int comps = 0;
      for (int j = 0; j < H; ++j) if (sig.b[j] > comps) comps = sig.b[j];
      if (comps == 1 && sig.b[H] && sig.b[H + 1])
        for (int n = slo; n <= maxn; ++n) row[n] += r[n - slo];
    });

    // PASS 1: size every target's row (min over sources of source.lo + cells)
    mins.clear();
    db.for_each([&](const Sig& sig, int slo, const u64*) {
      forEachViableMask(sig, H, maxn - slo, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (slo + cells + completionLowerBound(out.b, H) > maxn) return;
        mins.relax(out, static_cast<std::uint8_t>(slo + cells));
      });
    });

    // allocate next from the sized targets, pre-reserving BOTH the index (to the
    // known state count) and the arena (to the known total support) so neither the
    // open-addressing array nor the row arena carries doubling-capacity slack -- that
    // slack is what would otherwise erase the ranged win.
    size_t arenaTotal = 0;
    for (size_t i = 0; i < mins.cap; ++i)
      if (mins.used[i]) arenaTotal += static_cast<size_t>(maxn - mins.lo[i] + 1);
    next.clear();
    next.ensureIdx(mins.cnt);
    next.prepArena(arenaTotal);
    for (size_t i = 0; i < mins.cap; ++i)
      if (mins.used[i]) next.insert(mins.keys[i], mins.lo[i]);

    // PASS 2: accumulate source rows (shifted) into the pre-sized target runs
    db.for_each([&](const Sig& sig, int slo, const u64* r) {
      forEachViableMask(sig, H, maxn - slo, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (slo + cells + completionLowerBound(out.b, H) > maxn) return;
        int tlo; u64* dst = next.find(out, tlo);
        for (int n = slo; n + cells <= maxn; ++n)
          if (r[n - slo]) dst[n + cells - tlo] += r[n - slo];
      });
    });

    const u64 b = db.bytes() + next.bytes() +
                  static_cast<u64>(mins.cap) * (sizeof(Sig) + 2);
    if (b > peakBytes) peakBytes = b;
    std::swap(db, next);
  }
  return row;
}
