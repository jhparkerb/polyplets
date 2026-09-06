# Convex Mirage — convex polyplets by area are (empirically) non-D-finite

A finding from the "is there a tractable subfamily of polyplets?" thread. Short
version: **convexity looks like the tractability lever — it's the classical one —
but only by *perimeter*. By *area* (cell count) even convex shapes are q-series,
and the data says non-D-finite. Hence "Convex Mirage."**

## The question

We probed whether *constraining* polyplets carves out a subfamily with a closed
form (the way ordinary polyominoes are a hard-but-studied subfamily of polyplets).
The diagonal, hole, and diagonal-content cuts all dead-ended (see the B(y) and
T(n,h,c) notes). **Convex** is the cut with real pedigree.

## Convex polyplet

An **HV-convex** king-animal: every row is a single contiguous run of cells AND
every column is a single contiguous run — no notches, no gaps. (General polyplets
allow either.) Convexity is *the* classical tractability lever in polyomino
enumeration — convex polyominoes are solved in closed form by **perimeter**
(Delest–Viennot, Bousquet-Mélou, …). So convex polyplets were the natural
candidate to close.

## Method

A row transfer matrix (`experiments/convex_polyplets.py`): build the animal row by
row; the only state needed is `(left-phase, right-phase, width)` because HV-convex
⇔ the left border is v-shaped (non-increasing then non-decreasing) and the right
border ∧-shaped. Transitions are counted by multiplicity (valid horizontal
offsets), weighted by **area** (cells). `king=True` lets consecutive rows
corner-touch (polyplets); `king=False` requires column overlap (polyominoes).
**Validated** against brute-force enumeration for n≤8, and the edge case
reproduces the known convex-polyomino area sequence.

## The sequences (by area = number of cells)

**Convex polyplets** (NEW), first terms of 38 computed:
```
1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111, 2677214,
8389720, 26271014, 82230035, 257333334, 805229818, 2519563026, 7883577553, ...
```
**Convex polyominoes** (the known control), first terms:
```
1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312, 23320, 57279, 138536, 331032, ...
```
Growth ratio of the polyplet sequence → **μ ≈ 3.129** (vs ~6.77 for all polyplets),
confirming a small, structured family.

## The result: non-D-finite by area

I first over-claimed "convex ⇒ algebraic." The correction: the classical
solvability is by **perimeter**; counting by **area** is a different (harder)
enumeration, and even sub-families of convex polyominoes by area are q-series.

A holdout-validated guesser — fit a P-recurrence `Σ_i p_i(n) a(n-i)=0` (deg `p_i`
≤ 5, order ≤ 6) on the first 32 terms, then **require it to predict the remaining
6** — finds **nothing**:

```
== convex polyominoes (KNOWN control), 38 terms: no P-recurrence -> non-D-finite
== convex polyplets (NEW),            38 terms: no P-recurrence -> non-D-finite
```

The **control failing is the discriminator**: the test is not under-powered (it
*would* surface a recurrence if one existed at that order), and the known
convex-polyomino area sequence is itself not D-finite at this complexity. So both
convex families, **by area**, are empirically **non-D-finite** — a clean negative,
of the same character as B(y). (Empirical, not a proof: 38 terms rule out any
recurrence up to order 6 / degree 5.)

**Strengthened 2026-08-05** (`results/subclasses.md` Phase 2a/2b, written
up in `results/subclasses.md`): both series now run to **n=700**, and both
are excluded at **order ≤ 24, degree ≤ 24** — and, separately, satisfy no
algebraic equation of degree ≤ 24 in either variable. The mod-p rank test that
does it is a rigorous exclusion over Q, not a numerical one, and the four
positive/negative controls that keep it powered are a gate
(`make gate-convex-dfinite`). Same session: μ = 3.128943269730886252…
(199 trusted digits), θ = 0 with a purely geometric correction, and no integer
polynomial of degree ≤ 20 / height ≤ 1e8 has μ as a root. The paragraph above
stands; it is now an order of magnitude stronger in every direction.

## Placement

- A **finishable, self-contained** result (unlike B(y), which is parked): a new
  integer sequence worth an OEIS/Superseeker lookup, plus the non-D-finite-by-area
  finding. Reproduce with `python3 experiments/convex_polyplets.py 38`.
- **Off the a(n)-record path** — pure math, for the paper, not the record.
- The transfer matrix itself *is* the efficient "solution" (μ ≈ 3.129 growth);
  there is just no D-finite coefficient formula by area.
