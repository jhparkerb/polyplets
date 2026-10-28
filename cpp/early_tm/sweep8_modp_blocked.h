// B x R1 x R3: the blocked / hash-partitioned store composed with the u32 mod-p
// fold sweep. db and next are each S separate FlatDB32 partitions. A column DRAINS
// db partition-by-partition -- freeing each partition's RAM (freeMem) the instant it
// is consumed -- while next accumulates. So the live peak is ~1x (next) instead of
// db+next (~2x), on top of R3's u32 row (~1.73x) and R1's fold (~2x). Net vs the
// exact u64 double-buffer: ~2 (B) x 1.73 (R3) x 2 (R1) ~ 6.9x less RAM (the headline
// ~8x is the optimistic end; the blocked drain recovers slightly under 2x because a
// partition's mid-drain `next` already holds part of the column).
//
// Orthogonal composition: R1/R3 change the Sig key fold / count type / row width;
// B changes WHEN a partition's memory is released. Correctness is by construction --
// the partition a state lands in (hashSig & (S-1)) does not affect which states are
// produced or their counts, and addition mod p is a ring homomorphism. Gate: blocked
// B_H(n) mod p == the non-blocked sweepSquare8HeightModP for all (H, p, fold).
#pragma once

#include <cstdint>
#include <cstring>
#include <vector>

#include "signature.h"
#include "sweep8_modp.h"         // FlatDB32, addCountsModP32, minSizeRow32
#include "transition_square8.h"  // stepColumnSquare8, forEachViableMask, foldSig

// One strip height mod p with the blocked drain-and-free store. S = number of hash
// partitions (power of two). peakStates = live state high-water; peakBytes = live
// store-bytes high-water (the metric B targets). Emits B_H(n) mod p for n=0..maxn.
inline std::vector<std::uint32_t> sweepSquare8HeightModPBlocked(
    int H, int maxn, std::uint32_t p, bool fold, int S, u64& peakStates,
    u64& peakBytes) {
  std::vector<std::uint32_t> row(maxn + 1, 0);
  std::vector<FlatDB32> db, next;
  db.reserve(S); next.reserve(S);
  for (int s = 0; s < S; ++s) { db.emplace_back(maxn); next.emplace_back(maxn); }
  { Sig seed; std::memset(seed.b, 0, SIGMAX);
    db[FlatDB::hashSig(seed) & (S - 1)].slot(seed)[0] = 1u % p; }

  auto storeBytes = [](const std::vector<FlatDB32>& v) {
    u64 b = 0;
    for (const auto& part : v)
      b += static_cast<u64>(part.cap) * (part.stride * sizeof(std::uint32_t) + SIGMAX + 1);
    return b;
  };

  for (int col = 0; col <= maxn; ++col) {
    u64 total = 0;
    for (const auto& part : db) total += part.size();
    if (total == 0) break;
    if (total > peakStates) peakStates = total;

    // harvest completed animals across all db partitions (mod p)
    for (auto& part : db)
      part.for_each([&](const Sig& sig, const std::uint32_t* counts) {
        int comps = 0;
        for (int j = 0; j < H; ++j) if (sig.b[j] > comps) comps = sig.b[j];
        if (comps == 1 && sig.b[H] && sig.b[H + 1])
          for (int n = 1; n <= maxn; ++n)
            if (counts[n])
              row[n] = static_cast<std::uint32_t>(
                  (static_cast<std::uint64_t>(row[n]) + counts[n]) % p);
      });

    for (auto& part : next) part.clear();
    // DRAIN db partition by partition; free each the moment it is consumed
    for (int i = 0; i < S; ++i) {
      db[i].for_each([&](const Sig& sig, const std::uint32_t* counts) {
        const int ms = minSizeRow32(counts, maxn);
        if (ms < 0) return;
        forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
          Sig out;
          if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
          const int cells = __builtin_popcount(mask);
          if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
          if (fold) foldSig(out, H);
          addCountsModP32(next[FlatDB::hashSig(out) & (S - 1)], out, counts, cells,
                          maxn, p);
        });
      });
      db[i].freeMem();  // return this partition's RAM right now
      const u64 b = storeBytes(db) + storeBytes(next);
      if (b > peakBytes) peakBytes = b;
    }
    std::swap(db, next);
  }
  return row;
}
