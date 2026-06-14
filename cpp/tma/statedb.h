// T3 implementation (1): plain hash map from signature to counts-by-size.
//
// Deliberately the dumbest thing that works -- this is THE
// designed-to-be-replaced component (chunked+compressed sets, then
// out-of-core, are later drop-ins behind the same few operations).

#pragma once

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

using u64 = std::uint64_t;
using Counts = std::vector<u64>;  // index = animal size, 0..maxn
using StateDB = std::unordered_map<std::string, Counts>;

struct SweepResults {
  // byHeight[h][n] = fixed animals with n cells and height exactly h
  std::vector<Counts> byHeight;
  Counts totals;
  // calibration: peak number of distinct boundary signatures held at once
  // (the memory bottleneck), and the boundary height where that peak occurred.
  u64 peakStates = 0;
  int peakHeight = 0;
};

// Accumulate src into db[sig], shifting sizes by `shift` (1 when the
// transition occupied a cell), dropping sizes that exceed maxn.
inline void addCounts(StateDB& db, const std::string& sig, const Counts& src,
                      int shift, int maxn) {
  Counts& dst = db[sig];
  if (dst.empty()) dst.assign(maxn + 1, 0);
  for (int n = 0; n + shift <= maxn; ++n)
    if (src[n]) dst[n + shift] += src[n];
}
