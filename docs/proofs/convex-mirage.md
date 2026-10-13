# Convex polyplets by area are (empirically) non-D-finite

Convexity is the classical tractability lever in polyomino enumeration, but
only by *perimeter*. By *area* (cell count) even convex shapes are q-series,
and the data says non-D-finite, for polyplets and for polyominoes alike.

## The question

Does constraining polyplets carve out a subfamily with a closed form? The
diagonal, hole and diagonal-content cuts dead-ended. Convexity is the cut
with real pedigree: convex polyominoes are solved in closed form by perimeter
(Delest–Viennot, Bousquet-Mélou), so convex polyplets were the natural
candidate.

## Convex polyplet

An **HV-convex** king animal: every row is a single contiguous run of cells
and every column is a single contiguous run, no notches, no gaps.

## Method

A row transfer matrix (`experiments/convex_polyplets.py`): build the animal
row by row; the only state needed is `(left-phase, right-phase, width)`
because HV-convex means the left border is v-shaped (non-increasing then
non-decreasing) and the right border ∧-shaped. Transitions are counted by
multiplicity (valid horizontal offsets), weighted by area. `king=True` lets
consecutive rows corner-touch (polyplets); `king=False` requires column
overlap (polyominoes). Validated against brute-force enumeration for n ≤ 8,
and the polyomino setting reproduces the known convex-polyomino area
sequence.

## The sequences (by area)

Convex polyplets, first terms of 38 computed:
```
1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111, 2677214,
8389720, 26271014, 82230035, 257333334, 805229818, 2519563026, 7883577553, ...
```
Convex polyominoes (the known control), first terms:
```
1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312, 23320, 57279, 138536, 331032, ...
```
Growth ratio of the polyplet sequence → μ ≈ 3.129 (against ~6.77 for all
polyplets): a small, structured family.

## The result: non-D-finite by area

A holdout-validated guesser (fit a P-recurrence `Σ_i p_i(n) a(n−i) = 0` with
deg `p_i` ≤ 5, order ≤ 6, on the first 32 terms, then require it to predict
the remaining 6) finds nothing:

```
== convex polyominoes (KNOWN control), 38 terms: no P-recurrence -> non-D-finite
== convex polyplets (NEW),            38 terms: no P-recurrence -> non-D-finite
```

The control failing is the discriminator: the test would surface a recurrence
if one existed at that order, and the known convex-polyomino area sequence is
itself not D-finite at this complexity. So both convex families, by area, are
empirically non-D-finite. (Empirical, not a proof: 38 terms rule out any
recurrence up to order 6 and degree 5.)

Stronger version (`results/subclasses.md`): both series run to n = 700, and
both are excluded at order ≤ 24, degree ≤ 24, and separately satisfy no
algebraic equation of degree ≤ 24 in either variable. The mod-p rank test that
does it is a rigorous exclusion over Q, not a numerical one, and the four
positive and negative controls that keep it powered are a gate
(`make gate-convex-dfinite`). Also: μ = 3.128943269730886252… (199 trusted
digits), θ = 0 with a purely geometric correction, and no integer polynomial
of degree ≤ 20 with height ≤ 1e8 has μ as a root.

## Placement

- A self-contained result: a new integer sequence, plus the non-D-finite-by-area
  finding. Reproduce with `python3 experiments/convex_polyplets.py 38`.
- Off the a(n) path: pure math, not the record.
- The transfer matrix itself is the efficient way to compute the sequence
  (μ ≈ 3.129 growth); there is just no D-finite coefficient formula by area.
