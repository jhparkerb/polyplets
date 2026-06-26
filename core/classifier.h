// classifier.h — Completion-side classifier templates (DESIGN §3, §10).
//
// The classifier handles the "closing column" path (sweep8.h:95-96): when a
// state's empty-next-column closure is a valid complete animal, it contributes
// to the output. Two classifier tags for v1:
//
//   ClassifyTriangle — O1: T(n,H) for each (n, H). a(n) = Σ_H T(n,H).
//   ClassifyHoles    — O2: per (n, H, holes). Reuses euler.h closedEulerDelta4.
//
// Usage: map_shard<Counter, Classifier>(...)
// The Classifier must provide:
//   void complete(const Sig&, int H, int col, const RunRecord<Word>&, Output&)
// where Output accumulates the result for the whole height-sweep.

#pragma once

#include <cstdint>
#include <vector>
#include "core/signature.h"
#include "core/run.h"
#include "core/euler.h"

// ─── Output accumulator: by-height triangle rows ─────────────────────────────

// T(n,H): accumulated by one height-sweep pass.
// row[n] = T(n, H) for this H.
template <class W>
struct TriangleRow {
  int H;
  std::vector<W> row; // indexed 0..maxn; row[n] = count of n-cell animals of height H

  explicit TriangleRow(int H, int maxn) : H(H), row(maxn + 1, W{0}) {}
};

// ─── Triangle classifier (O1) ────────────────────────────────────────────────

// Mirrors sweep8.h:95-96:
//   if comps == 1 && touch_top && touch_bottom:
//       for n in 1..maxn: row[n] += counts[n]
struct ClassifyTriangle {
  template <class W>
  static void complete(const Sig& sig, int H, const RunRecord<W>& rec,
                       TriangleRow<W>& out) {
    // completion predicate: exactly one component, touching both top and bottom
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (sig.b[j] > comps) comps = sig.b[j];
    if (comps != 1 || !sig.b[H] || !sig.b[H + 1]) return;
    // accumulate: counts[lo .. lo+len) contribute to row[lo .. lo+len)
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n >= 1 && n < static_cast<int>(out.row.size()))
        out.row[n] += rec.counts[i];
    }
  }
};

// ─── Holes output accumulator (O2) ───────────────────────────────────────────

// Per (n, holes) count for one height H.
// Stored as a vector of (n, holes, count) triples (sparse; fills in at completion).
template <class W>
struct HolesRow {
  int H;
  // Sparse: pair (n, holes) -> count. For small n, fully dense is fine.
  // Using a flat vec of (n_max+1) vectors indexed by n, then by holes.
  std::vector<std::vector<W>> byNHoles; // byNHoles[n][holes] = count

  HolesRow(int H, int maxn, int maxholes)
    : H(H), byNHoles(maxn + 1, std::vector<W>(maxholes + 1, W{0})) {}
};

// ─── Holes classifier (O2) ───────────────────────────────────────────────────
//
// The holes count for a completed animal = Euler-characteristic holes.
// In the transfer-matrix approach, the hole delta accumulates per column step
// via closedEulerDelta4 (euler.h). The holes count must be carried in the
// RunRecord value alongside the cell-count-vec — for v1 this is implemented
// as an extended RunRecord or a separate parallel structure.
//
// DESIGN NOTE: For M0 (the in-RAM driver), the holes classifier is scaffolded
// but not fully wired (holes need the Euler delta accumulated per-step, which
// requires threading it through the map loop in mapreduce.h). Full wiring is
// part of M5 / T5.4. The skeleton here ensures the seam compiles cleanly.

struct ClassifyHoles {
  template <class W>
  static void complete(const Sig& sig, int H, const RunRecord<W>& rec,
                       HolesRow<W>& out) {
    // Full implementation: see T5.4. Skeleton placeholder.
    (void)sig; (void)H; (void)rec; (void)out;
  }
};
