// T2 plug-in #2: square-8 (polyplet) column transition -- THE novel core.
//
// King adjacency (edge OR corner) makes the cell-at-a-time boundary need the
// diagonal NW cell that the sweep has already overwritten. We sidestep that by
// transferring a WHOLE COLUMN at a time: the entire old column is present, so
// all king adjacencies (old rows r-1,r,r+1 to new row r) are available with no
// carry. Connectivity is resolved by union-find over the new column's cells and
// the old column's components, so crossing partitions and k-way merges (a new
// cell can fuse up to its W/NW/SW old neighbours plus N/S new neighbours) are
// handled without special cases.
//
// Operates on the fixed-size Sig (no allocation on the hot path). No published
// signature tables exist for this lattice (it is new), so the gate validates
// against animal COUNTS (A006770) and the G2 oracle.

#pragma once

#include <cstdint>
#include <cstring>

#include "signature.h"

namespace s8 {
inline int find(int* p, int x) {
  while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
  return x;
}
inline void unite(int* p, int a, int b) {
  a = find(p, a); b = find(p, b);
  if (a != b) p[a] = b;
}
}  // namespace s8

// Transfer one column. `old` is the current boundary; `mask` (nonzero) bit r
// set means the new column's row r is occupied. For Alive, the canonical next
// signature is written to `out`; Dead means the mask strands an old component.
// Closing the animal (the old mask==0 case) is handled by the caller, which
// already knows the component count -- so this stays purely the extend step.
inline Outcome stepColumnSquare8(const Sig& old, int H, unsigned mask, Sig& out) {
  // union-find slots: new-column row r -> r ; old label L -> H + L. Indices
  // stay < 2*SIGMAX (H <= 30, labels <= H), so stack arrays -- no per-call heap
  // allocation, which dominated the hot path when these were std::vector.
  int p[2 * SIGMAX];
  for (int i = 0; i < 2 * SIGMAX; ++i) p[i] = i;
  for (int r = 0; r < H; ++r) {
    if (!((mask >> r) & 1u)) continue;
    if (r + 1 < H && ((mask >> (r + 1)) & 1u)) s8::unite(p, r, r + 1);
    for (int rr = r - 1; rr <= r + 1; ++rr) {
      if (rr < 0 || rr >= H) continue;
      const unsigned char L = old.b[rr];
      if (L) s8::unite(p, r, H + L);
    }
  }

  // Any old component with no cell in the new column is stranded -> dead.
  char rootHasNew[2 * SIGMAX] = {0};
  for (int r = 0; r < H; ++r)
    if ((mask >> r) & 1u) rootHasNew[s8::find(p, r)] = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char L = old.b[i];
    if (L && !rootHasNew[s8::find(p, H + L)]) return Outcome::Dead;
  }

  std::memset(out.b, 0, SIGMAX);
  for (int r = 0; r < H; ++r)
    if ((mask >> r) & 1u)
      out.b[r] = static_cast<unsigned char>(s8::find(p, r) + 1);  // +1: 0=empty
  canonicalizeSig(out.b, H);
  out.b[H] = (old.b[H] != 0 || (mask & 1u)) ? 1 : 0;                   // top
  out.b[H + 1] = (old.b[H + 1] != 0 || ((mask >> (H - 1)) & 1u)) ? 1 : 0;  // bot
  return Outcome::Alive;
}

// Enumerate exactly the nonzero column masks worth trying against `old`:
//   - popcount <= budget (cannot overshoot maxn) -- lossless,
//   - no old component left stranded -- exactly the masks stepColumnSquare8
//     would NOT immediately kill as Dead.
// This replaces the brute 0..2^H loop: stranded masks (the vast majority once
// components exist) are never generated. A mask "covers" component L iff it sets
// a row adjacent (r-1,r,r+1) to an L-cell, i.e. iff some new cell touches L,
// i.e. iff L is not stranded; step() still re-checks, so it stays the authority.
// Candidate 05, "two-ended reach prune". Rows are visited in INTERLEAVED order
// (0, H-1, 1, H-2, ...) so that both the strip-top row 0 and the strip-bottom
// row H-1 are decided at depths 0 and 1 -- pinning BOTH ends of the eventual
// animal's vertical span as early as possible. We then carry the existing
// in-generator TOP-reach prune AND a symmetric BOTTOM-reach prune:
//
//   lbTop = min over completions of topReach    (band of rows < tr)
//   lbBot = min over completions of bottomReach  (band of rows > br)
//
// where topReach/bottomReach are the disjoint forced-cell bands from
// completionLowerBound (signature.h). Concretely, with clearedMask = the rows
// already DECIDED-CLEARED (visited, bit not set):
//   lbTop = topBase ? 0 : (lowest row index not in clearedMask)
//   lbBot = botBase ? 0 : (H-1 - highest row index in [0,H-1] not in clearedMask)
// An undecided low/high row keeps the corresponding bound at 0 (a completion
// could still set row 0 / row H-1, zeroing that reach), so the bound is a true
// lower bound over the whole subtree. Since lbTop bounds rows < tr and lbBot
// bounds rows > br are DISJOINT bands, lbTop + lbBot <= topReach + bottomReach
// <= completionLowerBound; pruning on bits + lbTop + lbBot > budget therefore
// removes a STRICT SUBSET of what the post-step check already discards ->
// byte-identical output, only the enumeration order of fn() calls changes.
namespace s8 {
template <class F>
inline void viableRec(int d, int H, unsigned mask, int bits, std::uint32_t cov,
                      std::uint32_t all, std::uint32_t decided, const int* order,
                      const std::uint32_t* rowSup, const std::uint32_t* sufSup,
                      int budget, bool topBase, bool botBase, F& fn) {
  if ((cov | sufSup[d]) != all) return;  // remaining rows can't cover all comps
  // Two-ended reach prune: in-generator slice of the post-step
  // completionLowerBound check, here for BOTH the top and bottom forced bands.
  const std::uint32_t cleared = decided & ~mask;        // rows decided-cleared
  const std::uint32_t notCleared = (~cleared) & ((H < 32) ? ((1u << H) - 1) : ~0u);
  if (notCleared) {  // some row still set-or-settable (else subtree is empty)
    const int lbTop = topBase ? 0 : __builtin_ctz(notCleared);
    const int lbBot = botBase ? 0 : (H - 1 - (31 - __builtin_clz(notCleared)));
    if (bits + lbTop + lbBot > budget) return;
  }
  if (d == H) {
    if (mask) fn(mask);
    return;
  }
  const int r = order[d];
  const std::uint32_t dec = decided | (1u << r);
  viableRec(d + 1, H, mask, bits, cov, all, dec, order, rowSup, sufSup, budget,
            topBase, botBase, fn);                                       // r = 0
  if (bits + 1 <= budget)                                                // r = 1
    viableRec(d + 1, H, mask | (1u << r), bits + 1, cov | rowSup[r], all, dec,
              order, rowSup, sufSup, budget, topBase, botBase, fn);
}
}  // namespace s8

template <class F>
inline void forEachViableMask(const Sig& old, int H, int budget, F&& fn) {
  std::uint32_t all = 0, rowSup[SIGMAX];
  for (int i = 0; i < H; ++i)
    if (old.b[i]) all |= 1u << old.b[i];
  for (int r = 0; r < H; ++r) {
    std::uint32_t s = 0;
    for (int rr = r - 1; rr <= r + 1; ++rr)
      if (rr >= 0 && rr < H && old.b[rr]) s |= 1u << old.b[rr];
    rowSup[r] = s;
  }
  // Interleaved visitation order: 0, H-1, 1, H-2, 2, ... (lo and hi closing in).
  int order[SIGMAX];
  for (int lo = 0, hi = H - 1, d = 0; lo <= hi;) {
    order[d++] = lo++;
    if (lo <= hi) order[d++] = hi--;
  }
  // sufSup[d] = OR of rowSup over rows visited at depth d..H-1 (still remaining).
  std::uint32_t sufSup[SIGMAX + 1];
  sufSup[H] = 0;
  for (int d = H - 1; d >= 0; --d) sufSup[d] = sufSup[d + 1] | rowSup[order[d]];
  s8::viableRec(0, H, 0u, 0, 0u, all, 0u, order, rowSup, sufSup, budget,
                old.b[H] != 0, old.b[H + 1] != 0, fn);
}
