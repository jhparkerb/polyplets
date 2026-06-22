// Phase 4 (implementation): out-of-core column sweep. db and next live as S partition
// FILES on disk; only ~one partition is resident at a time, so peak RAM is O(peak/S) and
// reach is bounded by disk, not RAM. Per column: scan each db partition (read → harvest +
// transitions, appending (target,row) contributions to S spill files), then reduce each
// spill file into a RAM FlatDB and write it back as the next partition, then swap by
// rename. Correct by construction (every db state processed once; contributions summed by
// Sig in the reduce, exactly addCounts). Self-contained; the exact engine is untouched.
// Gate: out-of-core a(n) == exact (small N, small S so the disk path actually exercises).
#pragma once

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "signature.h"
#include "statedb.h"
#include "transition_square8.h"

// Write a FlatDB's live (Sig, counts-row) entries as flat binary records.
inline void oocWrite(const std::string& fn, const FlatDB& db) {
  std::FILE* f = std::fopen(fn.c_str(), "wb");
  db.for_each([&](const Sig& sig, const u64* r) {
    std::fwrite(sig.b, 1, SIGMAX, f);
    std::fwrite(r, sizeof(u64), db.stride, f);
  });
  std::fclose(f);
}

// Read (Sig,row) records from a file and ACCUMULATE them into db (summing duplicate
// Sigs) -- this is the reduce step; identical-Sig contributions add via slot().
inline void oocReadReduce(FlatDB& db, const std::string& fn) {
  std::FILE* f = std::fopen(fn.c_str(), "rb");
  if (!f) return;
  Sig sig;
  std::vector<u64> r(db.stride);
  while (std::fread(sig.b, 1, SIGMAX, f) == static_cast<size_t>(SIGMAX)) {
    if (std::fread(r.data(), sizeof(u64), db.stride, f) != db.stride) break;
    u64* dst = db.slot(sig);
    for (size_t n = 0; n < db.stride; ++n) dst[n] += r[n];
  }
  std::fclose(f);
}

// One strip height, fully out-of-core. `dir` is a scratch directory. peakStates is the
// high-water live-state count (the metric the partitioning shrinks the RAM image of).
inline std::vector<u64> sweepSquare8HeightOOC(int H, int maxn, int S,
                                              const std::string& dir, u64& peakStates) {
  const size_t stride = static_cast<size_t>(maxn) + 1;
  std::vector<u64> row(maxn + 1, 0);
  auto dbf = [&](int i) { return dir + "/db_" + std::to_string(i); };
  auto nxf = [&](int j) { return dir + "/nx_" + std::to_string(j); };
  auto spf = [&](int j) { return dir + "/sp_" + std::to_string(j); };

  // seed: the empty boundary into its hash partition; the rest empty
  {
    Sig seed; std::memset(seed.b, 0, SIGMAX);
    const int sj = static_cast<int>(FlatDB::hashSig(seed) & (S - 1));
    for (int i = 0; i < S; ++i) {
      FlatDB d(maxn);
      if (i == sj) d.slot(seed)[0] = 1;
      oocWrite(dbf(i), d);
    }
  }

  for (int col = 0; col <= maxn; ++col) {
    std::vector<std::FILE*> sp(S);
    for (int j = 0; j < S; ++j) sp[j] = std::fopen(spf(j).c_str(), "wb");

    u64 total = 0;
    std::vector<u64> shifted(maxn + 1, 0);
    for (int i = 0; i < S; ++i) {
      FlatDB db(maxn);
      oocReadReduce(db, dbf(i));
      std::remove(dbf(i).c_str());
      total += db.size();
      db.for_each([&](const Sig& sig, const u64* counts) {
        int comps = 0;
        for (int b = 0; b < H; ++b) if (sig.b[b] > comps) comps = sig.b[b];
        if (comps == 1 && sig.b[H] && sig.b[H + 1])     // harvest a completed animal
          for (int n = 1; n <= maxn; ++n) row[n] += counts[n];
        const int ms = minSizeRow(counts, maxn);
        if (ms < 0) return;
        forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
          Sig out;
          if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
          const int cells = __builtin_popcount(mask);
          if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
          std::fill(shifted.begin(), shifted.end(), 0);
          for (int n = 0; n + cells <= maxn; ++n)
            if (counts[n]) shifted[n + cells] = counts[n];
          const int j = static_cast<int>(FlatDB::hashSig(out) & (S - 1));
          std::fwrite(out.b, 1, SIGMAX, sp[j]);
          std::fwrite(shifted.data(), sizeof(u64), stride, sp[j]);
        });
      });
    }
    for (int j = 0; j < S; ++j) std::fclose(sp[j]);
    if (total > peakStates) peakStates = total;
    if (total == 0) { for (int j = 0; j < S; ++j) std::remove(spf(j).c_str()); break; }

    for (int j = 0; j < S; ++j) {                       // reduce spills -> next partitions
      FlatDB nx(maxn);
      oocReadReduce(nx, spf(j));
      std::remove(spf(j).c_str());
      oocWrite(nxf(j), nx);
      std::rename(nxf(j).c_str(), dbf(j).c_str());       // swap by rename
    }
  }
  for (int i = 0; i < S; ++i) std::remove(dbf(i).c_str());
  return row;
}
