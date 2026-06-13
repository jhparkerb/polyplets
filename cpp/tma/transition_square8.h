// T2 plug-in #2: square-8 (polyplet) column transition -- THE novel core.
//
// King adjacency (edge OR corner) makes the cell-at-a-time boundary need the
// diagonal NW cell that the sweep has already overwritten. We sidestep that
// for the correctness-first engine by transferring a WHOLE COLUMN at a time:
// the entire old column is present, so all king adjacencies (old rows r-1,r,
// r+1 to new row r) are available with no carry. Connectivity is resolved by
// union-find over the new column's cells and the old column's components, so
// crossing partitions and k-way merges (a new cell can fuse up to its W/NW/SW
// old neighbours plus N/S new neighbours) are handled without special cases.
//
// Signature layout reused from signature.h: H label bytes + 2 touch flags.
// No published signature tables exist for this lattice (it is new), so the
// gate validates against animal COUNTS (A006770) and the G2 oracle.

#pragma once

#include <algorithm>
#include <string>
#include <vector>

#include "signature.h"

struct ColResult {
  Outcome outcome;   // Alive: extend with sig; Complete: harvest; Dead: drop
  std::string sig;   // meaningful only for Alive
};

namespace s8 {
inline int find(std::vector<int>& p, int x) {
  while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
  return x;
}
inline void unite(std::vector<int>& p, int a, int b) {
  a = find(p, a); b = find(p, b);
  if (a != b) p[a] = b;
}
}  // namespace s8

// Transfer one column. `old` is the current boundary (H labels + 2 flags);
// `mask` bit r set means the new column's row r is occupied.
inline ColResult stepColumnSquare8(const std::string& old, int H,
                                   unsigned mask) {
  int comps = 0, maxLabel = 0;
  bool present[256] = {false};
  for (int i = 0; i < H; ++i) {
    const unsigned char L = static_cast<unsigned char>(old[i]);
    if (L && !present[L]) {
      present[L] = true;
      ++comps;
      if (L > maxLabel) maxLabel = L;
    }
  }

  // mask == 0 closes the animal: nothing can connect further, so it is a
  // valid fixed animal iff the old boundary is a single component that has
  // touched both the top and bottom of the H-strip (height exactly H).
  if (mask == 0) {
    const bool ok = comps == 1 && old[H] != 0 && old[H + 1] != 0;
    return {ok ? Outcome::Complete : Outcome::Dead, {}};
  }

  // union-find slots: new-column row r -> r ; old label L -> H + L
  std::vector<int> p(H + maxLabel + 1);
  for (int i = 0; i < static_cast<int>(p.size()); ++i) p[i] = i;
  for (int r = 0; r < H; ++r) {
    if (!((mask >> r) & 1u)) continue;
    if (r + 1 < H && ((mask >> (r + 1)) & 1u)) s8::unite(p, r, r + 1);
    for (int rr = r - 1; rr <= r + 1; ++rr) {
      if (rr < 0 || rr >= H) continue;
      const unsigned char L = static_cast<unsigned char>(old[rr]);
      if (L) s8::unite(p, r, H + L);
    }
  }

  // Any old component with no cell in the new column is stranded: it can
  // never reconnect to the growing front, so the animal would end up
  // disconnected -> dead.
  std::vector<char> rootHasNew(p.size(), 0);
  for (int r = 0; r < H; ++r)
    if ((mask >> r) & 1u) rootHasNew[s8::find(p, r)] = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char L = static_cast<unsigned char>(old[i]);
    if (L && !rootHasNew[s8::find(p, H + L)]) return {Outcome::Dead, {}};
  }

  std::string out(H + 2, 0);
  for (int r = 0; r < H; ++r)
    if ((mask >> r) & 1u)
      out[r] = static_cast<char>(s8::find(p, r) + 1);  // +1 keeps 0 = empty
  out = canonicalize(std::move(out), H);
  out[H] = (old[H] != 0 || (mask & 1u)) ? 1 : 0;                  // touched top
  out[H + 1] = (old[H + 1] != 0 || ((mask >> (H - 1)) & 1u)) ? 1  // ...bottom
                                                             : 0;
  return {Outcome::Alive, std::move(out)};
}
