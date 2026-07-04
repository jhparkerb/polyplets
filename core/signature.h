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

#include <cstdint>
#include <cstring>
#include <string>

// Result of feeding a partial animal one transition step.
enum class Outcome { Alive, Dead, Complete };

// Fixed-size signature for the hot square-8 path: H+2 bytes, zero-padded to
// SIGMAX (so H <= 30, matching the MAXN cap). Inline (no heap), trivially
// hashable/comparable -- this is what lets the state store be a flat
// open-addressing map instead of unordered_map<string,...> (no per-state
// allocation, no pointer chasing). Same byte layout as the std::string
// signature above; square-4 keeps using the string form.
//
// POLY_SIGMAX override: a standalone single-TU binary may #define it before
// including this header to raise the cap (cpp/sym/symtm.cpp needs H up to
// maxn=34 for the tall-skinny symmetric strips). Production TUs leave it
// unset and get the exact prior 32.
#ifndef POLY_SIGMAX
#define POLY_SIGMAX 32
#endif
static constexpr int SIGMAX = POLY_SIGMAX;
struct Sig {
  unsigned char b[SIGMAX];
  bool operator==(const Sig& o) const {
    return std::memcmp(b, o.b, SIGMAX) == 0;
  }
};

// Three-way compare of two sig keys over `keyLen` bytes — a drop-in for
// memcmp(a, b, keyLen) (returns <0 / 0 / >0 with the SAME lexicographic byte
// order) but ~1.3-1.5x faster on the hot path: it compares 8 bytes at a time as
// big-endian u64s (one CPU compare per 8 bytes instead of memcmp's per-byte
// setup), falling back to memcmp on the <8-byte tail. Used by the sort
// comparator and both k-way merge heaps — a measured chunk of the map terminal
// sort and ~19% of merge (results/{map-profile,merge-ledger}.md). The big-endian
// load makes the numeric u64 order equal the byte order on any host endianness.
inline int sigCmp(const unsigned char* a, const unsigned char* b, int keyLen) {
  int i = 0;
  for (; i + 8 <= keyLen; i += 8) {
    uint64_t pa, pb;
    std::memcpy(&pa, a + i, 8);
    std::memcpy(&pb, b + i, 8);
    pa = __builtin_bswap64(pa);
    pb = __builtin_bswap64(pb);
    if (pa != pb) return pa < pb ? -1 : 1;
  }
  if (i < keyLen)
    return std::memcmp(a + i, b + i, static_cast<size_t>(keyLen - i));
  return 0;
}

// Canonicalize in place over the first H bytes (relabel components 1,2,... in
// order of first occurrence). Flags at b[H], b[H+1] untouched.
inline void canonicalizeSig(unsigned char* b, int H) {
  unsigned char map[256] = {0};
  unsigned char next = 1;
  for (int i = 0; i < H; ++i) {
    const unsigned char v = b[i];
    if (v == 0) continue;
    if (map[v] == 0) map[v] = next++;
    b[i] = map[v];
  }
}

// R1 symmetry fold. Vertical (top<->bottom) reflection of a boundary signature:
// reverse the H row bytes, swap the two touch flags, recanonicalize the labels.
// An involution; equivalent partial animals map to reflected boundaries.
inline Sig reflectSig(const Sig& s, int H) {
  Sig r;
  std::memcpy(r.b, s.b, SIGMAX);
  for (int i = 0; i < H; ++i) r.b[i] = s.b[H - 1 - i];
  r.b[H] = s.b[H + 1];                    // swap touched-top / touched-bottom
  r.b[H + 1] = s.b[H];
  canonicalizeSig(r.b, H);
  return r;
}

// Fold a signature to its orbit's canonical representative min(s, reflect(s))
// (lexicographic over the fixed SIGMAX bytes). Storing only canonical sigs and
// summing into them is the orbit-sum DP: ~2x fewer live states and ~2x fewer
// source transitions, byte-identical totals (the strip's vertical mirror is a
// symmetry of fixed counting). Validated in experiments/r1_sym_fold_check.py.
inline void foldSig(Sig& s, int H) {
  Sig r = reflectSig(s, H);
  if (std::memcmp(r.b, s.b, SIGMAX) < 0) s = r;
}

// std::string form (square-4 path): same relabeling as canonicalizeSig.
inline std::string canonicalize(std::string sig, int H) {
  canonicalizeSig(reinterpret_cast<unsigned char*>(&sig[0]), H);
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

// Admissible lower bound on the number of ADDITIONAL cells any completion of
// this boundary must place to become a valid fixed animal of height exactly H
// (single component, touching row 0 and row H-1). MUST never over-estimate: a
// state whose (min cells so far + this bound) exceeds maxn is pruned, so an
// over-estimate would silently drop a real animal. (The gate, which checks
// every published term, is the admissibility oracle: an inadmissible bound
// makes a count come out low.)
//
// Future cells attach only to the CURRENT column (king reach is one column
// left) or to later future cells, never to vacated earlier columns -- so the
// frontier's vertical reach is fixed by this column's occupied rows. Three
// disjoint row bands each force future cells; their sum is a lower bound:
//   top reach     rows 0..tr-1 climbed if row 0 never touched        (>= tr)
//   bottom reach  rows br+1..H-1 if row H-1 never touched       (>= H-1-br)
//   separating    an empty band between two occupied rows that NO single
//   bands         component spans must be crossed by a king path -> >= its
//                 width in future cells. A band a component spans (same label
//                 above and below, connected via history) costs nothing, and
//                 an empty row inside one component likewise -- counting only
//                 non-spanned bands keeps the bound admissible under
//                 interleaving (e.g. labels A,B,A down a column).
inline int completionLowerBound(const unsigned char* sig, int H) {
  int tr = -1, br = -1;
  for (int i = 0; i < H; ++i)
    if (sig[i] != 0) {
      if (tr < 0) tr = i;
      br = i;
    }
  if (tr < 0) return 0;  // seed / empty boundary
  const int topReach = sig[H] != 0 ? 0 : tr;
  const int bottomReach = sig[H + 1] != 0 ? 0 : (H - 1 - br);

  // belowMask[k] = set of labels present in rows >= k
  std::uint32_t belowMask[SIGMAX + 1];
  belowMask[H] = 0;
  for (int k = H - 1; k >= 0; --k)
    belowMask[k] = belowMask[k + 1] |
                   (sig[k] ? (1u << static_cast<unsigned char>(sig[k])) : 0u);

  int bandSum = 0;
  std::uint32_t aboveMask = 0;  // labels in rows tr..prevRow
  int prevRow = -1;
  for (int i = tr; i <= br; ++i) {
    if (!sig[i]) continue;
    if (prevRow >= 0 && i - prevRow > 1)               // empty band (prevRow,i)
      if ((aboveMask & belowMask[i]) == 0)             // no component spans it
        bandSum += i - prevRow - 1;
    aboveMask |= 1u << static_cast<unsigned char>(sig[i]);
    prevRow = i;
  }
  return topReach + bottomReach + bandSum;
}
