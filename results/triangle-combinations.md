# Alternative slicings and combinations of the height triangle

2026-08-09. Ways of combining T(n,H) that are not slices along a line, run on
the banked n<=40 triangle. `experiments/triangle_combinations.py`,
`alt_sign_runs.py`, `parity_amplitude.py`. Novelty against the literature is
UNCHECKED for everything here; the repo was grepped and none of it is recorded
elsewhere in-tree.

## 1. Log-concavity of the triangle — holds everywhere (POSITIVE)

The row polynomial's coefficients and the columns are both log-concave over the
whole closed triangle:

- **every row** `T(n,.)` is log-concave in H, for n = 3..40;
- **every column** `T(.,H)` is log-concave in n, for H = 1..20.

No exceptions in 820 cells. Note this is a different statement from the
log-concavity of `a(n)` discussed in `results/open-conjectures.md` C2/C3, which
concerns the row sums and is open.

It is **not** explained by real-rootedness: the row polynomials are far from
real-rooted (row 40 has 9 real roots out of 39; max |Im| = 2.01), so the usual
Newton-inequality route does not apply and any proof would need another
mechanism — the same difficulty `open-conjectures.md` records for a(n).

## 2. Row polynomial at special points — no structure

`F_n(y) = sum_H T(n,H) y^H` evaluated at y = -1, 1/3, -1/3, 3, 9, 1/9 (the base
3 being the diagonal law's). Minimal C-finite recurrence in n, order <= 8, last
point held out: **none at any of the six points.** Integrality is the only
pattern: y = -1, 3, 9 give integers, as they must.

## 3. The alternating row sum: a huge cancellation that oscillates

`F_n(-1) = sum_H (-1)^H T(n,H)` is ~6 orders of magnitude below a(n)
(1.16e-6 * a(40)), and its sign oscillates with **growing** run lengths:

    sign runs (n=4..40):  3, 5, 5, 8, 8, 8

Growing runs rule out a fixed complex-conjugate singularity pair, which would
give a constant period. The mechanism that does fit: `F_n(-1) = a(n) E[(-1)^H]`,
whose phase tracks `pi * mean_H(n)`, and `mean_H ~ n^0.687` (measured over
n >= 12) grows sublinearly, so the period grows like `n^(1-nu)`.

- **Partly confirmed:** 3 of the 5 sign flips occur exactly where `mean_H`
  crosses a half-integer.
- **Not a usable exponent estimator:** run lengths give `n^0.465` (=> nu = 0.535)
  against the 0.313 predicted by the directly measured mean. Four quantized
  points cannot resolve it. Recorded as a negative so it is not retried.

**The amplitude is the interesting part.** A Gaussian height distribution of the
measured width (w = 3.42 at n=40) would give a Fourier coefficient at frequency
pi of order exp(-pi^2 w^2/2) ~ 1e-26. The measured value is 1e-6 — twenty orders
larger. Fitting `ln(|F|/a)` on n<=33 and predicting n=34..40:

| form | holdout error (in ln) |
|---|---|
| exp(-alpha w), alpha = 4.04 | 1.33 |
| exp(-beta w^2) | 2.21 |

Neither is clean (the oscillation contaminates the envelope), but the
exponential form is clearly preferred over the Gaussian. **The height
distribution is not Gaussian at the parity scale**, which the collapse in
`results/height-distribution-collapse.md` — a coarse-grained statement — could
not have seen. In growth terms the signed sum behaves like ~5.76^n against
a(n)'s 7.11^n.

## 4. Atom degrees against sqrt(lambda)

`results/triangle-structure.md` conjectures the row-direction algebraic
complexity "is" the frontier size, i.e. ~ lambda^(H/2). Fitting the measured
atom degrees (1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289) over H = 5..10 gives
base **2.592** against `sqrt(lambda) = 2.667`. Consistent, on six noisy points
(per-step ratios wander 2.34..2.71); not a confirmation.

## What was not run

Untested combinations that remain open: joint bounding-box B(n,H,W) structure
(data exists only to n~17), moments/cumulants of the height distribution as
sequences in n, symmetry-class-refined triangles, and any statistic requiring
fresh enumeration (perimeter-refined, component-refined).

## 5. Cross-lattice ratio T_king / T_square (confirmation, not discovery)

`experiments/cross_lattice.py`. The square-lattice bounding-box bank
(`results/bbox_square4_n21.txt`) summed over width gives the square height
triangle; control passes (row sums == A001168 for all n <= 21). Comparing cell
by cell with the king triangle on the same cells:

Down each diagonal `n - H = k`, the ratio's successive ratio converges to
**3.000** (exact at k=0; 2.998 at k=1, 2.980 at k=2, 2.94 at k=3 and rising with
H). That is exactly what `docs/proofs/universal-diagonal-law.md` predicts —
`T(H+k,H) = q_k(H) b^H` with b = 3 on king and b = 1 on square — so this is an
independent numerical confirmation of the universal law across two lattices, on
data neither derivation used. It is not new structure.

Off the diagonals the ratio grows smoothly with no visible structure, consistent
with everything else found in the band.

## 6. The width-height joint: square bounding boxes and a local CLT

Using the king bbox bank `results/bbox_polyplets_n17_exact.txt` (columns are
`H W n count`, not `n H W count` -- misreading them silently produces garbage).
Two controls pass first: transpose symmetry `B(n,H,W) = B(n,W,H)` holds with 0
violations for H,W <= 17, and `sum_W B(n,H,W)` equals the banked height triangle
in every cell for n <= 17 -- two independently banked datasets agreeing.

**Square bounding boxes.** The share of n-cell polyplets whose bounding box is
exactly square declines smoothly: 0.183 (n=8), 0.148 (n=11), 0.126 (n=14),
0.111 (n=17). Local log-log slopes over n >= 9 sit in -0.647..-0.686 and the
fit over n >= 10 gives

    P(square bbox) ~ n^(-0.658)

**A local CLT for H - W.** The natural mechanism is that H and W both scale like
n^nu, so `P(H = W) ~ 1/rms(H-W)`. Measured:

| n | rms(H-W) | share | share x rms |
|---|---|---|---|
| 8 | 2.073 | 0.1827 | 0.379 |
| 11 | 2.579 | 0.1477 | 0.381 |
| 14 | 3.036 | 0.1259 | 0.382 |
| 17 | 3.458 | 0.1109 | 0.384 |

The product is nearly constant and climbing steadily toward
`1/sqrt(2*pi) = 0.3989` — the Gaussian local-limit constant. So `H - W` is
asymptotically normal at the scale of its own width.

Note the contrast with section 3: `H - W` is Gaussian on the coarse scale, while
the height distribution is demonstrably **not** Gaussian at the parity scale.
Both are true; the CLT governs the bulk, parity structure lives at lattice
resolution.

**Standing caveat.** `results/nu-exponent.md` withdrew nu as evidence for
universality and instructed that it not be refreshed or put in the paper. Nothing
here reopens that. The observation is about the relative convergence of two
observables, not about class membership: the square-bbox share at n <= 17 is
already nearer 0.6407 than the mean-height route reaches at n = 40, which makes
it the better-behaved diagnostic if a diagnostic is ever wanted.
