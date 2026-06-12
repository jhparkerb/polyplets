// T1(a): generic partition signature (implementation-plan.md, Layer 2).
//
// A signature is a std::string of H+2 bytes:
//   bytes [0, H)   boundary cell states: 0 = empty, else component label
//   byte  H        touched-top flag (some occupied cell ever in row 0)
//   byte  H+1      touched-bottom flag (row H-1)
//
// Labels form a partition of the occupied boundary cells into connected
// components of the partial animal. This generic representation allows
// CROSSING partitions (labels may interleave arbitrarily), which the
// square-8 (polyplet) transition will need; for square-4 the reachable
// partitions happen to be non-crossing, but nothing here assumes it.
// The compact Motzkin encoding (T1(b)) is a later drop-in optimization.

#pragma once

#include <string>

// Canonical form: relabel components in order of first occurrence (1, 2, ...).
// Flags are untouched. Idempotent.
inline std::string canonicalize(std::string sig, int H) {
  unsigned char map[256] = {0};
  unsigned char next = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char v = static_cast<unsigned char>(sig[i]);
    if (v == 0) continue;
    if (map[v] == 0) map[v] = next++;
    sig[i] = static_cast<char>(map[v]);
  }
  return sig;
}

inline bool boundaryEmpty(const std::string& sig, int H) {
  for (int i = 0; i < H; ++i)
    if (sig[i] != 0) return false;
  return true;
}

inline bool labelPresent(const std::string& sig, int H, char label) {
  for (int i = 0; i < H; ++i)
    if (sig[i] == label) return true;
  return false;
}
