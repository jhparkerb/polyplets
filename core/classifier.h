// classifier.h — Completion-side classifier templates.
//
// The classifier handles the "closing column" path (cpp/early_tm/sweep8.h): when a
// state's empty-next-column closure is a valid complete animal, it contributes
// to the output. Two classifiers:
//
//   ClassifyTriangle — T(n,H) for each (n, H). a(n) = Σ_H T(n,H).
//   ClassifyHoles    — per (n, H, holes), from euler.h's closedEulerDelta4.
//
// Usage: map_shard<W, Classifier>(src, cfg, output)
// The Classifier must provide a static method:
//   void complete(const Sig&, int H, const RunRecord<W>&, Output&)
// where Output accumulates the result for the whole height-sweep.

#pragma once

#include <cstdint>
#include <cstdio>
#include <cstdlib>
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

// ─── Triangle classifier ────────────────────────────────────────────────

// Mirrors cpp/early_tm/sweep8.h:
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

// ─── Holes output accumulator ───────────────────────────────────────────

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

// ─── Holes classifier ───────────────────────────────────────────────────
//
// The holes count for a completed animal = Euler-characteristic holes. The
// hole delta accumulates per column step via closedEulerDelta4 (euler.h) into
// key byte sig.b[H+2] (core/mapreduce.h, keyLen H+3), which is read here.

struct ClassifyHoles {
  template <class W>
  static void complete(const Sig& sig, int H, const RunRecord<W>& rec,
                       HolesRow<W>& out) {
    // completion predicate: exactly one component, touching both top and bottom
    int comps = 0;
    for (int j = 0; j < H; ++j)
      if (sig.b[j] > comps) comps = sig.b[j];
    if (comps != 1 || !sig.b[H] || !sig.b[H + 1]) return;
    // holes count is in sig.b[H+2] (the extended key byte)
    const int holes = static_cast<int>(sig.b[H + 2]);
    for (int i = 0; i < rec.len; ++i) {
      const int n = static_cast<int>(rec.lo) + i;
      if (n < 1 || n >= static_cast<int>(out.byNHoles.size())) continue;
      if (holes >= static_cast<int>(out.byNHoles[n].size())) {
        // An n-cell animal has fewer than n holes, so this cannot happen;
        // dropping the count would be a silent undercount, so stop instead.
        std::fprintf(stderr, "ClassifyHoles: %d holes at n=%d exceeds the table\n",
                     holes, n);
        std::abort();
      }
      out.byNHoles[n][holes] += rec.counts[i];
    }
  }
};
