// Phase 3.2 (frontier-revision-plan): blocked / hash-partitioned store. db and next
// are each S separate FlatDB partitions. A column DRAINS db partition-by-partition --
// freeing each partition's RAM the instant it is consumed (freeMem) -- while next
// accumulates. So the live peak is ~1× (next) instead of db+next (~2×), cutting the
// double-buffer. The hash-partitioned layout is also the out-of-core (Phase 4) seam:
// a drained partition could spill to disk instead of being freed.
//
// Orthogonal to R1/R2/R3 -- those change the Sig key / count type / row storage; this
// changes WHEN a partition's memory is released. Self-contained; the exact engine in
// sweep8.h is untouched. Gate: blocked B_H == exact. Serial (memory is the point).
#pragma once

#include <cstring>
#include <vector>

#include "signature.h"
#include "statedb.h"
#include "transition_square8.h"

// One strip height with the blocked/drain-and-free store; B_H(n) for n=0..maxn.
// S = number of hash partitions (power of two). peakBytes tracks the live store
// high-water during the drain (the metric this optimization targets).
inline std::vector<u64> sweepSquare8HeightBlocked(int H, int maxn, int S,
                                                  u64& peakStates, u64& peakBytes) {
  std::vector<u64> row(maxn + 1, 0);
  std::vector<FlatDB> db, next;
  db.reserve(S); next.reserve(S);
  for (int s = 0; s < S; ++s) { db.emplace_back(maxn); next.emplace_back(maxn); }
  { Sig seed; std::memset(seed.b, 0, SIGMAX);
    db[FlatDB::hashSig(seed) & (S - 1)].slot(seed)[0] = 1; }

  auto storeBytes = [](const std::vector<FlatDB>& v) {
    u64 b = 0;
    for (const auto& p : v)
      b += static_cast<u64>(p.cap) * (p.stride * 8 + SIGMAX + 1);
    return b;
  };

  for (int col = 0; col <= maxn; ++col) {
    u64 total = 0;
    for (const auto& p : db) total += p.size();
    if (total == 0) break;
    if (total > peakStates) peakStates = total;

    // harvest completed animals across all db partitions
    for (auto& part : db)
      part.for_each([&](const Sig& sig, const u64* counts) {
        int comps = 0;
        for (int j = 0; j < H; ++j) if (sig.b[j] > comps) comps = sig.b[j];
        if (comps == 1 && sig.b[H] && sig.b[H + 1])
          for (int n = 1; n <= maxn; ++n) row[n] += counts[n];
      });

    for (auto& p : next) p.clear();
    // DRAIN db partition by partition; free each the moment it is consumed
    for (int i = 0; i < S; ++i) {
      db[i].for_each([&](const Sig& sig, const u64* counts) {
        const int ms = minSizeRow(counts, maxn);
        if (ms < 0) return;
        forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
          Sig out;
          if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
          const int cells = __builtin_popcount(mask);
          if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
          addCounts(next[FlatDB::hashSig(out) & (S - 1)], out, counts, cells, maxn);
        });
      });
      db[i].freeMem();  // <-- Phase 3.2: return this partition's RAM right now
      const u64 b = storeBytes(db) + storeBytes(next);
      if (b > peakBytes) peakBytes = b;
    }
    std::swap(db, next);
  }
  return row;
}
