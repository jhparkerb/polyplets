// Euler-characteristic / hole accounting for the column transfer matrix (#28).
//
// Holes are an ADDITIVE count coordinate, not a state coordinate: every 2x2
// window's contribution to the Euler number is a function of one adjacent
// COLUMN PAIR, so the running hole count accumulates across exactly the column
// transitions the sweep already performs. This header isolates that accounting
// so the sign/border logic can be unit-tested against a flood-fill oracle
// (tests/euler_unit.cpp) BEFORE it is threaded through transition_square8.h.
//
// Gray's 2x2-window (bit-quad) Euler formula, foreground connectivity c:
//   4*E_c = Q1 - Q3 + (c==4 ? +2 : -2)*QD
// where over all windows Q1 = #(exactly one cell), Q3 = #(exactly three),
// QD = #(diagonal/checkerboard pair). E_c = comps_c - holes_{dual(c)}.
//
// The polyplet is genuinely 8-connected, so its single component pairs with the
// 4-connected background (Jordan dual; OEIS-A389193 convention). Hence the
// PRIMARY hole count is holes_4bg = 1 - E_8fg, and E_8fg uses the MINUS-2*QD
// branch. (Counterintuitive; verified on the n=4 diamond and n=8 ring in the
// unit test -- the diamond is E_8fg=0/holes_4bg=1 vs E_4fg=4/holes_8bg=0.)
#pragma once

#include <cstdint>

// Foreground connectivity selecting which background hole count we accumulate:
//   FG8 -> holes in the 4-connected background (primary, --holes)
//   FG4 -> holes in the 8-connected background (companion, --holes8)
enum class Conn { FG4, FG8 };

// Contribution of one 2x2 window to 4*E. Bits: a=top-left, b=top-right,
// c=bottom-left, d=bottom-right (each 0/1).
inline int quadWindow(int a, int b, int c, int d, Conn conn) {
  const int cnt = a + b + c + d;
  if (cnt == 1) return +1;            // Q1
  if (cnt == 3) return -1;            // Q3
  if (cnt == 2) {                     // QD only if the pair is diagonal
    const bool diag = (a && d && !b && !c) || (b && c && !a && !d);
    if (diag) return conn == Conn::FG4 ? +2 : -2;
  }
  return 0;                           // cnt 0/4, or an edge (non-diagonal) pair
}

// 4*E summed over the windows BETWEEN two adjacent columns (left=oldCol,
// right=newCol), each a row bitmask (bit r set = row r occupied). Windows have
// top-left row r for r in [-1, H-1]; out-of-range rows are empty (the implicit
// top/bottom exterior border).
inline int quadColumnPair(std::uint32_t oldCol, std::uint32_t newCol, int H,
                          Conn conn) {
  auto bit = [](std::uint32_t m, int r, int H) -> int {
    return (r >= 0 && r < H) ? static_cast<int>((m >> r) & 1u) : 0;
  };
  int sum = 0;
  for (int r = -1; r < H; ++r)
    sum += quadWindow(bit(oldCol, r, H), bit(newCol, r, H),
                      bit(oldCol, r + 1, H), bit(newCol, r + 1, H), conn);
  return sum;
}

// Delta to the CLOSED-image 4*E when the boundary advances oldCol -> newCol.
// "Closed image" = the partial animal with the current boundary column treated
// as rightmost (empty exterior beyond it), so the accumulator equals 4*E of a
// real binary image at every step and 4*E is always divisible by 4.
//
//   A_new = A_old + quad(old,new)            // the now-internal column pair
//                 + quad(new, 0)             // new right-border windows
//                 - quad(old, 0)             // old right-border windows (gone)
//
// holes-so-far = comps - A/4 (comps = the boundary's component count, known to
// the engine). For the closed single-component animal, holes = 1 - A/4.
inline int closedEulerDelta4(std::uint32_t oldCol, std::uint32_t newCol, int H,
                             Conn conn) {
  return quadColumnPair(oldCol, newCol, H, conn) +
         quadColumnPair(newCol, 0u, H, conn) -
         quadColumnPair(oldCol, 0u, H, conn);
}
