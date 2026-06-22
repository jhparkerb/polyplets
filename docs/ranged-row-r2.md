# R2 — ranged counts-row: measured, confirmed high-value (~2×, growing with N)

**Idea.** Each per-state counts row is stored full, `[0, maxn]` (`maxn+1` u64s).
But a boundary's row is nonzero only on its support `[minSize, maxn]` (you cannot
have a partial of fewer than `minSize` cells with that boundary). Store only the
support → less RAM. The counts row is ~84% of per-state footprint, so the row is
the lever worth attacking.

**Refute attempt — measure first (`cpp/tma_rangestat.cpp`).** At each height's
peak-state column, measure `rowFactor = Σ full width / Σ support width` and the
true `footprintFactor` (counting the fixed 32-byte Sig + an 8-byte range header
that do **not** shrink):

| H  | N  | peakStates | avg minSize | rowFactor | footprintFactor |
|----|----|-----------:|------------:|----------:|----------------:|
|  8 | 12 |      1 586 |   8.0 / 12  |   2.58    |   1.68          |
| 10 | 14 |     10 473 |   9.7 / 14  |   2.81    |   1.83          |
| 11 | 16 |     28 078 |  10.7 / 16  |   2.70    |   1.85          |
| 12 | 15 |     64 189 |  11.1 / 15  |   3.28    |   2.01          |
| 13 | 15 |    137 528 |  10.8 / 15  |   3.10    |   1.96          |

**The refute failed.** At the peak the average state has already placed
~0.67–0.74·maxn cells, so its row is a mostly-empty low prefix; the support is ~3×
narrower than the full row, giving a **~2× footprint reduction**, and the factor
**grows with N** (the row grows while the 32-byte Sig stays fixed). For the reach
regime (N=21–24) it is ≥2×, and the tall-thin heavy strata — which need many cells
just to span their height — have even higher minSize, so R2 helps them most.

**Composition.** R2 is independent of R1 (fold) and R3 (u32 mod-p):

    R1 × R2 × R3  ≈  2 × 2 × 1.73  ≈  ~7× less RAM,

which would put a(24)/a(25) within dalby's 122 GB.

## Implementation path (the top reach project; deferred — non-trivial store change)

The one subtlety: a target row's support **widens under accumulation** — a later
source with fewer cells lowers `minSize`. So rows cannot simply be sized at first
insert. Clean fix = **two passes per column**:

1. **Pass 1 (size):** enumerate the transitions, recording for each target Sig only
   `minSize_t = min over sources of (minSize_s + cells)`. A lightweight Sig→u8 map.
2. **Allocate** each target's row as `[minSize_t, maxn]` in an arena; the slot stores
   `(lo, offset, len)`.
3. **Pass 2 (accumulate):** re-enumerate the transitions, adding into the pre-sized
   ranged rows (`dst[m − lo] += src[…]`).

Cost: ~2× transition work (the two passes) — offset by R1's ~2× speedup, so net
~1× compute for a ~2× memory win. Peak memory is ranged throughout (never holds a
full-width `next`). Gate: ranged totals == exact, like R1/R3.

Measured and specified here so it can be picked up directly; not yet built.
