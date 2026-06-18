# Perimeter & per-height cross-checks (task #18)

## Generation-side perimeter (done)

`build/g2 square8 N --perimeter` emits the joint (size, edge-perimeter)
distribution, where edge-perimeter = exposed unit edges = 4·size − (rook
adjacencies). Reuses the placed-cell machinery; default (no-flag) output
unchanged. **Validated:** Σ over perimeter of count[n] == A006770(n) for all
n≤13.

Example (n=8, perimeter → count):
```
12:6  14:134  16:811  18:3880  20:11548  22:23664  24:34001
26:34750  28:24860  30:11562  32:2725
```
Perimeter is always even (4n−2·E). Min ~12 (compact), max = 4n (no rook edges).

### Bonus finding: the perimeter=4n slice == A001168
A polyplet with edge-perimeter exactly 4n has zero rook adjacencies — i.e. it is
held together only by corner contacts (bishop-connected, "polyomino in
disguise"). Counting that slice reproduces **A001168 (fixed polyominoes)** exactly
through n=13. So the perimeter statistic and the rook/bishop cross-check are
linked: the extreme of one is the whole of the other. (Free internal
consistency, no external sequence needed.)

### Novelty
No prior art found for the polyplet edge-perimeter distribution (keyword search;
the definitive test is an OEIS numeric search of a row). Candidate-new — an
exploration item, not a verification one, unless/until matched externally.

## Per-height marginal: Method A vs Method B (done, exercises Method B)

The generation engine's bounding-box-height marginal (`g2 square8 N --per-box`,
summed over width) equals the transfer matrix's byHeight rows
(`tma square8 N --per-height`): **all 78 (n,h) cells through n=12 match.** This is
a finer-grained A-vs-B agreement than the totals, and unlike rook/bishop and the
(deferred) perimeter A-vs-B, it directly exercises **Method B's** height
decomposition — which is the TM's structural core. Zero new engine code.

## Full perimeter A-vs-B (TM perimeter dimension) — DONE

The transfer matrix now carries perimeter as a second DP index in an **isolated**
path (`cpp/tma/sweep8_perim.h`, `tma square8 N --perimeter`) that reuses the
validated transition/prune but keeps its own (size,perimeter) state store — the
production counting code is untouched (regression: default `tma square8 12` still
== A006770). Perimeter is additive per column:
`Δ = 4·cells − 2·(vertical adjacencies) − 2·(edges to the column on the left)`.

**Result:** the transfer matrix and the generator agree on the *entire* (size,
perimeter) distribution — all 106 cells through n=12 (and n≤11 in the gate).
This is the first cross-check where **Method B produces a finer-grained statistic
that Method A independently confirms** (rook/bishop and the symmetry checks only
exercise Method A). Wired into `gate_tma.py` as check G (permanent regression).

