# Slope-s slicings of the height triangle: no law off the diagonal (NEGATIVE)

2026-08-09. Closes the open caveat of `boundary-push-recurrence.md` — "only
*linear* slicings n−H=const were tested against long data runs" — for the
slicings that matter: the lines `n = sH + k` with `s >= 2`, which are the ones
that cut through the middle band where the triangle has neither a fixed-height
GF (banked only to H<=10, `results/fixed_height_gfs.txt`) nor a diagonal closed
form (H >= (n+1)/2 only, by the onset n >= 2k+1 of the diagonal law).

Question asked: are those uncovered cells hiding a P_k-analogue — polynomial
times an exponential, with a base other than 3?

## Method

`experiments/slope_slices.py`, `experiments/slope_onset.py` on the banked triangle
(`results/ns_a40/perheight/`). For each slice, fit the minimal
constant-coefficient linear recurrence in H by exact rational elimination,
requiring (a) at least one equation of slack beyond the unknowns and (b) the
largest-H point held out and predicted exactly. Scan an onset t = 0..7 (drop
the first t points), since the s=1 law itself only holds past n >= 2k+1.

**Positive control.** s=1 reproduces the diagonal law and its onset behaviour
exactly: order 1 (root 3) at k=0; with the pre-onset head dropped, order 2 with
coefficients (6, −9) = (x−3)^2 at k=1, and order 3 = (x−3)^3 at k=2. So the
probe finds a law of this shape when one is there, and sees the onset.

## Result — nothing at s = 2 or s = 3

| slice | points | minimal order (any onset t<=7) | ratio at the last point |
|---|---|---|---|
| n=2H   | 20 | none | 41.445 |
| n=2H+1 | 19 | none | 41.645 |
| n=2H+2 | 19 | none | 41.907 |
| n=3H   | 13 | none | 327.41 |
| n=3H+1 | 13 | none | 331.49 |
| n=3H+2 | 12 | none | 338.39 |

**Excluded:** any `poly(H) * mu^H` with deg poly <= 7 and a single base `mu`,
on all six slices, at every onset up to H=8. (Order r = deg+1 for one repeated
root; the search ran to r=8 subject to the slack rule, so on the shorter s=3
slices the effective ceiling is lower — see limits.)

**Not excluded:** a law with degree >= 8, or one whose onset is past H=8. With
20 points on the widest slice there is no way to settle that from banked data,
and no more terms are coming.

## Why the growth form says the same thing

On n=2H the successive ratio is still climbing at the last point (36.89 at H=3
to 41.445 at H=20, monotone) and the local exponent theta from
`T ~ C mu^H H^theta` drifts from −0.15 at H=6 to −0.38 at H=20.

Drift by itself proves nothing, and it would be easy to fool oneself here: run
the same 3-point local-theta estimator on `s=1 k=2`, which is *known* to be a
quadratic times 3^H, and it drifts as well — 2.56 at H=6 to 2.03 at H=20. The
difference is the shape of the drift. The known case converges to its integer
with increments collapsing (0.20, 0.11, 0.06, … 0.01); the slope-2 case moves
monotonically *away* from 0, and a Richardson step from the tail lands near
theta_inf ≈ −0.5 (the same step applied to the control returns 1.93 against a
true 2.00, so read that as ±0.1). A non-integer exponent is what one expects
from an unresolved subexponential correction, not from a polynomial prefactor.

## The structural reason to expect this

The diagonal law's engine is the separation lemma (`docs/proofs/diagonal-law.md`
Step 1): on the k = n−H background every row has one cell, and a one-cell row is
a cut vertex, so the animal factors into finitely many cluster types per surplus
level. At slope 2 the background row has two cells and is **not** a cut, so
connectivity routes around it and the finite-decomposition argument has nothing
to stand on. That is the same obstruction the perimeter grading hits from a
different direction (`results/perimeter-defect-diagonals.md`: defect does not
bound transverse extent), and it is consistent with T(n,H) not being
2D-holonomic (`boundary-push-recurrence.md`, holonomic2d_probe).

## P-finite recurrences: also nothing (same day)

`experiments/pfinite_slices.py`. Seeks `sum_{i=0..r} p_i(H) T(s(H−i)+k, H−i) = 0`
with `deg p_i <= d`, as an exact rational nullspace. Discipline: the last TWO
points of each slice are held out and must be predicted, and the fit is required
to carry at least 2 more equations than unknowns, so a kernel is evidence rather
than an artifact of underdetermination. Onset scanned t = 0..5.

**Positive control.** s=1 is found at the minimal `(r,d)` with the right onsets:
k=0 → (1,0) from H>=1; k=1 → (2,0) from H>=2; k=2 → (3,0) from H>=3. Constant
coefficients, as the diagonal law says.

**s=2 and s=3: none, at any (r,d) in the tested envelope, at any onset.**

| slice | points | envelope actually reachable under the slack rule |
|---|---|---|
| n=2H | 20 | r=1: d<=5, r=2: d<=3, r=3: d<=2, r=4: d<=1, r=5: d<=0 |
| n=3H | 13 | r=1: d<=3, r=2: d<=1, r=3: d<=0 |

That envelope is set by the data, not by the search: 20 points is what a slope-2
slice has when the triangle stops at n=40, and no more are coming.

## Asymptotic ansatz fitting, with the resolving power measured first

`experiments/slope2_ansatz.py`. Protocol fixed before any number was read: fit
on H in [H0, 17], hold out H = 18, 19, 20 and predict them; every model linear
in log space (basis `1, H, ln H, sqrt H, 1/H, 1/H^2`) so there is no optimizer
and no starting-guess luck.

**The control that sets the ceiling.** The identical pipeline on the last 20
terms of a(n) — where 40 terms plus differential approximants give
theta = −1.000(1) (`results/series-analysis-da.md`):

| model | fitted theta | max holdout rel err |
|---|---|---|
| C mu^H H^th | −0.961 | 0.014% |
| … e^{c/H} | −0.992 | 0.000% |
| … nu^sqrt(H) | **−0.898** | 0.001% |
| … e^{c/H + d/H^2} | −0.998 | 0.000% |

Three models predict held-out terms to ~1e-5 relative while disagreeing about
theta by 0.1. **A tiny holdout error is not evidence for an exponent at this
series length.** The confusion matrix agrees structurally: data generated from
the 3- and 4-parameter models is won by the 5-parameter one, because nested
supersets always tie or beat. Free-theta fits on the slope-2 slice are therefore
reported only to be discarded: they spread over theta = +0.15 … −0.63 with
holdout errors all under 0.5%.

**What does discriminate: lock theta, fit only mu.** Calibrated on the same
control, where the minimum sits at the true theta = −1.00 (0.181%) and ±0.25
neighbours cost 1.0–1.4%, so the method resolves an exponent to about ±0.25:

| theta locked | mu (slope-2) | holdout err | | control a(n) err |
|---|---|---|---|---|
| 0.00 | 40.83 | 6.47% | | 4.69% |
| **−0.25** | **41.85** | **1.13%** | | 3.49% |
| −0.50 | 42.89 | 4.51% | | 2.28% |
| −1.00 | 45.05 | 16.77% | | **0.18%** (truth) |
| −1.50 | 47.32 | 30.47% | | 2.71% |

**Second control, on a known polynomial-times-exponential.** Same window, the
`s=1 k=2` slice (truth: quadratic × 3^H): the locked scan minimises at
theta = 2.00 with mu = 3.014. The method finds a P_k-shaped law when one is
present. Note its residual at the truth is 2.3%, comparable to slope-2's best —
so residual *level* carries no information; only the exponent's *location* does.

### Factorials: excluded, with the noise floor measured

Asked directly: should factorial-type terms be in the ansatz set? Unbalanced
Gamma-quotients `Gamma(H+a)/Gamma(H+b)` are excluded by the converging ratio
(they force ratio ~ mu H^{a-b}). Balanced ones (central binomial, Catalan) are
already covered twice — asymptotically they are the mu^H H^theta family, and
exactly they make S(H+1)/S(H) rational in H, which is the order-1 P-finite test
that came back empty.

The Stirling signature was tested directly: fit
`ln S = a + bH + c lnH + d (H lnH)`, where a net factorial power shows as
`d != 0` (d = 1 for H!, 0.5 for its square root).

| slice | d | holdout |
|---|---|---|
| control a(n), truth d = 0 | +0.0011 | 0.002% |
| control s=1 k=2 (quadratic x 3^H), truth d = 0 | **+0.0339** | 0.593% |
| slope-2, H0 = 3 / 5 / 7 | +0.0185 / +0.0215 / +0.0170 | <= 0.23% |

The known-zero control returns a *larger* d than the slope-2 slice does, so the
estimator's floor at this length is ~0.03 and slope-2 sits inside it. Factorial
powers above ~0.05 are excluded; a real one would be 20-50x that.

### Verdict

- `mu ≈ 41.8–42.5`, still drifting up with the fit window (41.76 → 41.90 →
  42.02 as H0 goes 3 → 5 → 7). Compare lambda^2 = 50.55: the slope-2 slice is
  suppressed by ~0.83 per unit height against the unconstrained square.
- `theta` is **not identified**. Locked scan says ≈ −0.25, Richardson on the
  local exponent says ≈ −0.5, and the control says this method is worth ±0.25 at
  this length. The honest statement is theta in roughly [−0.6, −0.2].
- What *is* settled: theta is not a small non-negative integer, so the slice is
  not a low-degree polynomial times an exponential — independently agreeing with
  the exact C-finite and P-finite nulls above. `theta = −3/2` (the
  friendly-walkers prediction) is refuted outright: 19–52% holdout error across
  every onset.

## Limits

- The P-finite envelope above is small. A recurrence of order 3 with cubic
  coefficients, say, is untestable on 20 points and stays formally open.
- s=3 slices have 12-13 points, so the C-finite order ceiling there is ~5, not 8.
- Only k = 0, 1, 2 offsets were run per slope.
- The ansatz section reports no fitted constant to more digits than the control
  supports. mu is quoted to 3 significant figures and theta as an interval; the
  free-parameter fits that looked precise (holdout 1e-5) are demonstrated
  unreliable by the a(n) control and are not used for any claim.
- Untried, and the one lever that would add real information: fit the offsets
  k = 0..5 of the slope-2 family jointly with a shared mu, ~6 x 19 points
  against a few shared parameters.
  **SUPERSEDED 2026-08-09** by `results/slope-growth-saddle.md`: the slope-2 line
  is the onset line, so the diagonal law is nearly exact on it, and a saddle
  point on the grand form gives `mu_2 = 42.39460` with no fitting at all —
  confirmed to 6 parts in a million by extrapolating the banked ratios. The
  "drifting up with the fit window" above was drift toward that value. `theta`
  is still unidentified; nothing else in this note changes.
