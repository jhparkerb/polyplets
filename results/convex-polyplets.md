# Convex polyplets — a candidate new exactly-solvable king family

Date: 2026-07-10. Flagged as the one genuinely untapped item from the
countable-subpopulations analysis ([[countable-subpopulations-criterion]]).
This is a **big note**: a research lead, not a result yet. Literature check
in flight; update on return.

## Why this is the interesting one

By the criterion (results/countable-subpopulations-criterion.md), an attribute
gives a *counting shortcut* (closed form, not full enumeration) only if it
collapses the 2D connectivity constraint to 1D. **Convexity does exactly that**:
if every row is a contiguous interval, the animal is a 1D sequence of intervals
whose left/right edges evolve row-to-row under a *local* compatibility rule — a
transfer matrix on the edge-increments, which classically yields algebraic or
rational generating functions. Directedness (Bacher) and convexity are the two
canonical 1D-collapse attributes; directedness is done, convexity is open for
the king lattice.

## The object (and why it's genuinely new)

Convexity notions for king animals:
- **row-convex**: every row's cells form one horizontal interval
- **column-convex**: every column one vertical interval
- **HV-convex**: both
- **convex polyplet** := HV-convex ∧ **king-connected**

The wrinkle that makes it new: the classical "convex polyomino" is HV-convex ∧
**edge-connected**. The king version relaxes to king-connected, so it is a
**strict superset** — a pure diagonal join is now allowed. Minimal witness:
`{(0,0),(1,1)}` is HV-convex and king-connected but not edge-connected, so it is
a convex polyplet that is not a convex polyomino. (Note HV-convexity alone does
not force king-connectivity, so the connectivity clause is doing real work.)

Every classical convex-polyomino count is therefore a strict *lower* slice of
the convex-polyplet count; the excess is precisely the HV-convex shapes held
together by diagonal contacts.

## What we'd get (all side-quest, not a lever on a(n))

Per the criterion, this cannot help count `a(n)` — convex is a thin strict
subset that does not compose back to the total. The value is standalone:

1. **A new exactly-solved king family** — if the area-GF is algebraic/rational,
   it is a clean combinatorial result, plausibly unpublished (Bacher's
   directed-king count sat undone until 2013; the convex-*king* case looks
   similarly untouched — the whole convex-polyomino literature is edge-connected).
2. **A growth constant for convex polyplets** = dominant singularity of the GF.
   It is a valid rigorous lower bound on λ_polyplet (convex ⊂ polyplet), but
   convex is *thin*, so expect the constant to be SMALL — likely weaker than the
   directed 5.828 / multi-directed 6.475 bounds already banked. So its worth is
   the result + validation, NOT a better λ bound. (Gauge pending: the
   convex-polyomino growth constant vs the ~4.06 of all polyominoes tells us how
   thin convex is; the lit check is fetching it.)
3. **A third independent closed-form validation anchor** — filter the engine to
   convex polyplets, check coefficients against the GF; orthogonal to the
   strip-TM, g2, and directed (A047781) cross-checks.

## Classical results to build on / compare (to be confirmed by lit check)

- **Delest–Viennot 1984**: convex polyominoes by perimeter — # with perimeter
  `2n+8` is `(2n+11)4ⁿ − 4(2n+1)C(2n,n)`. Algebraic.
- **Bousquet-Mélou (1996)**: convex polyominoes by area — algebraic area-GF via
  functional equations with a catalytic variable ("wasp-waist" / kernel method).
- **Temperley 1956**: row-/column-convex polyominoes — rational GFs.
- Sub-families with known algebraic area-GFs: **stack, staircase (parallelogram),
  directed-convex, bargraph, Ferrers**. Each a candidate king-analog too.
- Klarner–Rivest, Lin–Chang: convex-polyomino GF.

King versions of ALL of these appear absent from the literature — a whole small
family of possible new results, convex polyplets being the headline.

## How to attack (when/if we pick it up)

1. **Define + brute-count**: HV-convex ∧ king-connected, first ~15 terms via the
   existing brute enumerator with a convexity filter. → OEIS lookup (is the
   sequence already there under some name?).
2. **Interval-profile transfer matrix**: state = `(row's left edge, right edge)`
   or the increments; the king row-to-row rule is "next interval overlaps or
   touches (including *diagonally*) the current one." This relaxation of the
   convex-polyomino overlap rule is the entire novelty — set it up and read off
   the functional equation.
3. **Solve** by kernel/catalytic-variable method (Bousquet-Mélou) → conjecture
   algebraic/rational GF → verify coefficients against the brute terms.
4. If clean: growth constant, OEIS submission, validation hook, short write-up.

## Findings (2026-07-10)

**It is unstudied — a genuine gap.** No enumeration or GF for convex / HV-convex /
row- / column-convex animals on the king lattice exists in the literature (the
whole convex-polyomino corpus — Delest–Viennot, Bousquet-Mélou, Temperley,
Klarner–Rivest, Lin–Chang — is edge-connected only). OEIS API query for the terms
below returned null: **not in OEIS.** (Note: the king directed/multi-directed
paper arXiv:1301.1365 is **Bacher**, not "Bousquet-Mélou & Rechnitzer" — a
lit-agent mis-citation, corrected here.)

**Verified terms (ours).** Independent brute enumeration
(`experiments/convex_polyplets.py`) reproduces A006770 exactly through n=10,
validating the enumerator, and gives fixed convex polyplets by area:

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| convex polyplets | 1 | 4 | 16 | 61 | 221 | 766 | 2566 | 8390 | 26982 | 85834 |

(n=2: all 4 dominoes incl. the diagonal `{(0,0),(1,1)}` — the smallest
convex-polyplet-not-convex-polyomino. Compare fixed convex *polyominoes*
A067675 = 1,2,6,19,59,176,…, strictly smaller from n=3.)

**Growth constant ≈ 3.0–3.1** (ratios 4.0→3.18, decreasing). Anchors: convex
polyominoes by area = **2.30914** (Bender 1974); column-convex = **3.2056**
(Temperley, rational GF, A001169); all polyplets λ ≈ 7.11. So convex polyplets
sit near column-convex, **less than half of λ** — a valid but **useless** lower
bound, nowhere near the banked directed 5.828 / multi-directed 6.475. **The λ-bound
motivation is dead;** the value is purely a standalone sequence + a possible clean
GF + a third validation anchor.

## Verdict & cheapest path

Real, new, verified — but low-leverage (weak bound, side-quest). If picked up, in
increasing cost:
1. **Submit the sequence to OEIS** (near-free; it's genuinely new).
2. **King column-convex GF** — relax the classical column-overlap predicate from
   "share ≥1 row" to "share ≥1 row OR touch corner-to-corner"; Temperley's method
   should carry over and likely still gives a **rational** GF. Cleanest real result.
3. **Full HV-convex king GF** — needs the kernel / q-difference machinery
   (Bousquet-Mélou); q-series by area. Most work.

Decision: park unless we want a small standalone king result before close. Not a
lever on a(n) under any outcome.
