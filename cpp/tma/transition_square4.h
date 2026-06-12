// T2 plug-in #1: square-4 (polyomino) kink transition.
//
// Validation instrument only -- square-4 has the richest external truth
// (A001168 known to n=70), so this plug-in proves the generic engine
// (T1/T3/T4) before any novel transition rules exist. Per the plan, all
// lattice-specific knowledge in the TMA lives in files like this one.
//
// Boundary convention during the sweep of cell (col, r), 0 <= r < H:
//   sig[0..r)   cells of the NEW column (col)
//   sig[r..H)   cells of the OLD column (col-1)
// The cell being decided neighbors sig[r] (left, old column) and sig[r-1]
// (above, new column). After the decision sig[r] holds the new cell.

#pragma once

#include <string>

#include "signature.h"

enum class Outcome { Alive, Dead, Complete };

struct StepResult {
  Outcome outcome;
  std::string sig;  // canonical; meaningful only for Alive
};

inline StepResult stepSquare4(const std::string& sig, int H, int r,
                              bool occupy) {
  const char left = sig[r];
  const char top = (r > 0) ? sig[r - 1] : 0;
  std::string out = sig;

  if (occupy) {
    char label;
    if (left == 0 && top == 0) {
      label = static_cast<char>(H + 1);  // fresh; canonicalize() renumbers
    } else if (left != 0 && top != 0 && left != top) {
      // the new cell joins two components: union by relabeling top -> left
      label = left;
      for (int i = 0; i < H; ++i)
        if (out[i] == top) out[i] = left;
    } else {
      label = (left != 0) ? left : top;
    }
    out[r] = label;
    if (r == 0) out[H] = 1;          // touched top
    if (r == H - 1) out[H + 1] = 1;  // touched bottom
    return {Outcome::Alive, canonicalize(std::move(out), H)};
  }

  out[r] = 0;
  if (left != 0 && !labelPresent(out, H, left)) {
    // left's component lost its last boundary contact: the animal is
    // finished if nothing else remains on the boundary, otherwise the
    // state can only evolve into disconnected shapes
    if (boundaryEmpty(out, H))
      return {(out[H] != 0 && out[H + 1] != 0) ? Outcome::Complete
                                               : Outcome::Dead,
              {}};
    return {Outcome::Dead, {}};
  }
  return {Outcome::Alive, canonicalize(std::move(out), H)};
}
