// FEASIBILITY PROBE -- NOT PRODUCTION.
//
// Standalone frontier dumper for the MPS/entanglement experiment. Re-derives the
// transfer-matrix frontier for a single strip height H by driving the PRODUCTION
// step kernel (stepColumnSquare8) directly over a serial exact-count sweep, and
// dumps the full {signature -> count} vector at a chosen column to stdout.
//
// This file lives entirely under experiments/ and includes the engine headers
// READ-ONLY. It builds its own u64 FlatDB sweep loop (a copy of the serial
// sweepSquare8HeightModP loop from sweep8_modp.h, minus the mod-p reduction and
// minus fold) so nothing in the production engine is touched or linked.
//
// Amplitude choice: we dump EXACT integer counts (u64), NOT mod p. The SVD probe
// measures singular-value DECAY, which is a real/Euclidean notion destroyed by
// reduction to random residues mod p. Exact counts at these H/maxn fit u64.
//
// Output format (one header line, then one line per frontier state):
//   H <H> col <col> maxn <maxn> states <N>
//   <b0> <b1> ... <b_{H+1}> | <total_count>
// where b0..b_{H-1} are the boundary labels, b_H = touched-top, b_{H+1} =
// touched-bottom, and total_count = sum_n counts[n] (partial polyplets of any
// size <= maxn reaching this boundary).
//
// Usage: dump_frontier <H> <maxn> <col|-1 for peak> [out.txt]

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <vector>

#include "signature.h"
#include "statedb.h"             // FlatDB (u64), minSizeRow
#include "transition_square8.h"  // stepColumnSquare8, forEachViableMask, completionLowerBound

int main(int argc, char** argv) {
  if (argc < 4) {
    std::fprintf(stderr, "usage: %s <H> <maxn> <col|-1=peak> [out.txt]\n", argv[0]);
    return 2;
  }
  const int H = std::atoi(argv[1]);
  const int maxn = std::atoi(argv[2]);
  const int wantCol = std::atoi(argv[3]);
  const char* outPath = (argc >= 5) ? argv[4] : nullptr;

  // Serial exact sweep, dumping at the requested column. We keep the frontier of
  // EVERY column so we can (a) report sizes and (b) dump at the peak if col=-1.
  // Snapshotting each column's FlatDB is cheap at these H.
  FlatDB db(maxn), next(maxn);
  Sig seed;
  std::memset(seed.b, 0, SIGMAX);
  db.slot(seed)[0] = 1;

  std::vector<size_t> sizes;
  // Remember the frontier we want to dump.
  std::vector<Sig> dumpKeys;
  std::vector<u64> dumpTotals;
  int dumpedCol = -1;

  auto snapshot = [&](int col) {
    dumpKeys.clear();
    dumpTotals.clear();
    db.for_each([&](const Sig& sig, const u64* counts) {
      u64 tot = 0;
      for (int n = 0; n <= maxn; ++n) tot += counts[n];
      if (tot == 0) return;
      dumpKeys.push_back(sig);
      dumpTotals.push_back(tot);
    });
    dumpedCol = col;
  };

  size_t peak = 0;
  int peakCol = 0;
  // First pass would be needed to find the true peak before dumping if col=-1.
  // To do it in one pass we snapshot on every column into a lightweight record
  // ONLY when it beats the running peak (col=-1) or equals wantCol.
  for (int col = 0; col <= maxn && !db.empty(); ++col) {
    const size_t sz = db.size();
    sizes.push_back(sz);
    if (sz > peak) { peak = sz; peakCol = col; if (wantCol < 0) snapshot(col); }
    // A specific column request lets us STOP right after capturing it -- the
    // frontier plateaus, so an early plateau column is representative and we
    // skip the expensive wide-budget tail sweep.
    if (col == wantCol) { snapshot(col); break; }

    next.clear();
    db.for_each([&](const Sig& sig, const u64* counts) {
      const int ms = minSizeRow(counts, maxn);
      if (ms < 0) return;
      forEachViableMask(sig, H, maxn - ms, [&](unsigned mask) {
        Sig out;
        if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
        const int cells = __builtin_popcount(mask);
        if (ms + cells + completionLowerBound(out.b, H) > maxn) return;
        addCounts(next, out, counts, cells, maxn);
      });
    });
    std::swap(db, next);
  }

  std::fprintf(stderr, "H=%d maxn=%d  peak states=%zu at col=%d  ncols=%zu\n",
               H, maxn, peak, peakCol, sizes.size());
  std::fprintf(stderr, "frontier sizes by column:");
  for (size_t i = 0; i < sizes.size(); ++i) std::fprintf(stderr, " %zu", sizes[i]);
  std::fprintf(stderr, "\n");

  if (dumpedCol < 0) {
    std::fprintf(stderr, "no frontier captured (col out of range)\n");
    return 1;
  }

  FILE* out = outPath ? std::fopen(outPath, "w") : stdout;
  if (!out) { std::perror("fopen"); return 1; }
  std::fprintf(out, "H %d col %d maxn %d states %zu\n", H, dumpedCol, maxn,
               dumpKeys.size());
  for (size_t i = 0; i < dumpKeys.size(); ++i) {
    for (int j = 0; j < H + 2; ++j)
      std::fprintf(out, "%d ", (int)dumpKeys[i].b[j]);
    std::fprintf(out, "| %llu\n", (unsigned long long)dumpTotals[i]);
  }
  if (out != stdout) std::fclose(out);
  std::fprintf(stderr, "dumped %zu states at col=%d\n", dumpKeys.size(), dumpedCol);
  return 0;
}
