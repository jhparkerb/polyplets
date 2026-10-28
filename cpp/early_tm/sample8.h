// Uniform random sampling of fixed polyplets, square-8 (king) lattice.
//
// A counting DP is also an exact uniform sampler: if you know, for every
// boundary state, the number of ways to COMPLETE it into a valid n-cell
// height-H animal, you can walk the transfer matrix forward choosing each next
// column with probability proportional to the completions it leads to -- and
// the column sequence that falls out is a uniformly random animal. No animal is
// ever enumerated; the cost per sample is one walk, not a traversal of all
// a(n).
//
// This REUSES the exact transition (stepColumnSquare8), viable-mask generator,
// and admissible prune (completionLowerBound) from the counting engine, so a
// sampled animal is provably one of the objects the engine counted. The
// completion counts W(sig, rem) are translation-invariant in the column index
// (the dynamics don't depend on which column we're at), so W is a function of
// (boundary, cells-remaining) only -- that is what makes one finite table serve
// every column.
//
// W(seed, n) recomputes byHeight[H][n] as a side effect (it is the number of
// completions of the empty boundary), giving a built-in cross-check against the
// counting engine.

#pragma once

#include <cstdint>
#include <cstring>
#include <random>
#include <unordered_map>
#include <utility>
#include <vector>

#include "signature.h"
#include "statedb.h"  // FlatDB::hashSig, u64
#include "transition_square8.h"

struct SigHash {
  size_t operator()(const Sig& s) const { return FlatDB::hashSig(s); }
};

// Per-height completion-count table for animals of exactly `n` cells, height H.
// W(sig, rem) = number of ways to extend boundary `sig` into a valid height-H
// animal placing exactly `rem` more cells (valid = single component touching
// both rows 0 and H-1 when the next column is empty). Memoized top-down by rem.
struct Completion {
  int H, n;
  // memo[rem][sig] = W(sig, rem); rem in 1..n. rem==0 is the base case below.
  std::vector<std::unordered_map<Sig, u64, SigHash>> memo;

  Completion(int H_, int n_) : H(H_), n(n_), memo(n_ + 1) {}

  // A boundary that, with no further cells, is a complete valid animal: exactly
  // one component, having touched both the top (row 0) and bottom (row H-1).
  bool validClosure(const Sig& sig) const {
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (sig.b[j] > comps) comps = sig.b[j];
    return comps == 1 && sig.b[H] && sig.b[H + 1];
  }

  u64 W(const Sig& sig, int rem) {
    if (rem == 0) return validClosure(sig) ? 1 : 0;  // close here, exactly n
    auto& m = memo[rem];
    auto it = m.find(sig);
    if (it != m.end()) return it->second;
    u64 total = 0;
    // Same choices the counting sweep would make from this state, with budget
    // `rem`: every viable nonzero column that keeps every component alive and
    // can still finish within budget. (Closing is only legal at rem==0, handled
    // above -- a nonzero column always costs >=1 cell.)
    forEachViableMask(sig, H, rem, [&](unsigned mask) {
      Sig out;
      if (stepColumnSquare8(sig, H, mask, out) != Outcome::Alive) return;
      const int cells = __builtin_popcount(mask);
      if (cells + completionLowerBound(out.b, H) > rem) return;  // can't finish
      total += W(out, rem - cells);
    });
    m.emplace(sig, total);
    return total;
  }
};

// Draw one uniformly random height-H, n-cell fixed polyplet, returned as the
// list of occupied (col, row) cells (col anchored at 0, rows in 0..H-1). At
// each column the next column is chosen with probability proportional to the
// completions it leads to; by construction that yields each animal with equal
// probability 1 / W(seed, n).
inline std::vector<std::pair<int, int>> sampleOne(Completion& C,
                                                  std::mt19937_64& rng) {
  Sig sig;
  std::memset(sig.b, 0, SIGMAX);  // seed: empty boundary
  int rem = C.n;
  std::vector<unsigned> cols;
  while (rem > 0) {
    std::vector<unsigned> masks;
    std::vector<Sig> outs;
    std::vector<int> cells;
    std::vector<u64> w;
    u64 sum = 0;
    forEachViableMask(sig, C.H, rem, [&](unsigned mask) {
      Sig out;
      if (stepColumnSquare8(sig, C.H, mask, out) != Outcome::Alive) return;
      const int c = __builtin_popcount(mask);
      if (c + completionLowerBound(out.b, C.H) > rem) return;
      const u64 ways = C.W(out, rem - c);
      if (ways == 0) return;
      masks.push_back(mask);
      outs.push_back(out);
      cells.push_back(c);
      w.push_back(ways);
      sum += ways;
    });
    // sum == W(sig, rem) > 0 on every reachable step (we only descend into
    // states with positive completion count).
    std::uniform_int_distribution<u64> dist(0, sum - 1);
    u64 r = dist(rng);
    size_t idx = 0;
    while (r >= w[idx]) { r -= w[idx]; ++idx; }
    cols.push_back(masks[idx]);
    sig = outs[idx];
    rem -= cells[idx];
  }
  std::vector<std::pair<int, int>> out;
  for (size_t c = 0; c < cols.size(); ++c)
    for (int row = 0; row < C.H; ++row)
      if ((cols[c] >> row) & 1u) out.emplace_back(static_cast<int>(c), row);
  return out;
}
