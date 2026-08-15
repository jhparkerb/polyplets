# The onset ridge: the depth-amplitude family is one constant, and it is 50/81

Thread **Ridgeline**, 2026-08-14. Executes the pickup point recorded in
`results/depth-tower-bivariate-dead-end.md` ("What survives"): the onset
double-scaling limit, derived rather than fitted. Scripts, all pure Python 3 and
seconds each unless noted, run from `experiments/`:
`ridgeline_master.py`, `ridgeline_scaling.py`, `ridgeline_vertex.py`,
`ridgeline_dump_families.py`.

**Verdict on the A_j family: CONFIRMED, and reduced to a derived constant.**
The seven measured rationals are not seven numbers. They are one number — the
velocity `alpha = 50/81` at which the defect's branch point moves when the
cluster is allowed one unit of excess — and that velocity is computed here
exactly, by a finite local enumeration, as `450/729`.

**The one-line answer to "35/8 or 118/27 at j = 5": 35/8.**

## 0. What changed, in four steps

1. **A closed form for the whole depth tower.** With `Y = yz` and `t = 1/z`, the
   proved chain identity collapses to
   `G(Y,t) = Phat + Bhat^2/(t-3-Shat)`, `D_j(k) = [Y^k t^(j-1)] G`, where `t`
   marks cluster **excess**. The binomial double sum (C)/(D) of
   `experiments/severance_w3_depths.py` is this identity read coefficient by
   coefficient. Verified at all 74 exact cells, depths 1–4.
2. **The normalisation trap.** `results/onset-defect-law.md` Sec.2 writes
   `A_j = C_j Gamma(j-1/2)`, `C_j` being the amplitude of the defect itself,
   `D_j(k) ~ C_j 9^k k^(j-3/2)`. In `C_j` the conjectured family is not a family
   of binomials at all: it is `C_(M+1)/C_1 = alpha^M/M!`, a pure exponential.
3. **What that means.** An exponential enhancement per unit chain length is
   exactly a square-root branch point whose *location* moves linearly with the
   excess marker: `1 - 9 Y_c(t) = alpha t + O(t^2)`, exponent fixed at `-1/2`.
4. **So alpha is local, and computable.** It is the first-order shift of the
   zero-momentum eigenvalue of the gap walk's row transfer under one 3-cell row.
   That is a finite count: `alpha = Sigma/729` with `Sigma = 450`.

## 1. The master identity

`docs/proofs/diagonal-law.md` Step 2 gives, over cluster types `c = (s_1..s_l)`,
`s_i >= 2`, with surplus `k_c = sum(s_i-1)`, `l_c` rows and excess
`e_c = k_c - l_c = sum(s_i-2)`:

```
F = E_b (1-S)^-1 E_t + P,   S = 3z + sigma,
E_b = z(1 + sum W^b y^k z^l),  E_t = 1 + sum W^t y^k z^l,
sigma = sum W y^k z^(l+1),     P = sum W^p y^k z^l.
```

Every monomial `y^k z^l = Y^k t^e` under `Y = yz`, `t = 1/z`, so each type enters
only through `(k, e)`. With the excess-graded aggregates of
`severance_w3_depths.families` — `Shat = sum_e t^e Sig_e(Y)`, `Bhat`, `Phat` —
the chain telescopes:

```
G(Y,t) := F = Phat(Y,t) + Bhat(Y,t)^2 / (t - 3 - Shat(Y,t)).            (M)
```

Extraction: `[y^k]F = R_k(z)/(1-3z)^(k+1)`, `R_k = sum_i a_i w^i`, `w = 1-3z`, and
`w = (t-3)/t` gives `F = sum_k Y^k sum_s a_(2k+1-s) t^s (t-3)^(k-s)`, hence

```
D_j(k) = [Y^k t^(j-1)] G,   valid for j-1 <= k.                        (M')
```

(The law part of `R_k`, `i <= k`, only reaches `t`-powers `>= k+1`, so it cannot
contaminate `t^(j-1)`.) `(M')` is identity (D) of `severance_w3_depths.py`
resummed; grading is legitimate because a type of excess `e` has `k >= e+1`, so
`t^e` always arrives with at least `Y^(e+1)`.

`experiments/ridgeline_master.py` — **GREEN**: `(M')` reproduces
`severance_w3_depths.D_series` at every cell of depths 1–4, `k <= 19` (20+19+18+17
= 74 exact rational cells); its `t^0` slice reproduces identity (II) of
`onset-defect-depth1-closed.md` at `k = 1..19`; perturbing one excess-1 pure
weight by `+1` breaks it (RED control fires).

What `(M)` buys is not brevity. It says what the depth variable *is*: a marker for
cluster excess, i.e. a **perturbation of the row transfer of the all-pairs gap
walk**. Depth is not a new object to be summed; it is a coupling constant.

## 2. The family, in the normalisation that makes it simple

`D_j(k) ~ C_j 9^k k^(j-3/2)`, so `F_j(Y) ~ C_j Gamma(j-1/2)(1-9Y)^(-(j-1/2))`, and
the tower has one scaling variable `tau = t/(1-9Y)`. Read at fixed chain length
`L` (using `sum_L z^L L^(M-1/2) ~ Gamma(M+1/2)(1-z)^(-M-1/2)`, checked term by
term for `M <= 4` in `ridgeline_scaling.py`),

```
G/t ~ C_1 sum_L (9Y)^L L^(-1/2) Acal(tL),   Acal(xi) = sum_M (C_(M+1)/C_1) xi^M,
```

so `Acal` is the excess enhancement of a cluster **per unit chain length**.

Now suppose the dominant singularity is a square-root branch point whose location
moves analytically with `t`, exponent fixed:
`h(t)(1 - 9Y - psi(t))^(-1/2)`, `psi(0) = 0`, `psi'(0) = alpha`. In the scaling
limit only `psi'(0)` survives, so `f(tau) = h(0)(1-alpha tau)^(-1/2)` and, using
`Gamma(M+1/2) = sqrt(pi)(1/2)_M`,

```
C_(M+1) = C_1 alpha^M / M!,    Acal(xi) = exp(alpha xi).                (*)
```

Equivalently: **depth M+1 is the M-th derivative of depth 1**,
`F_(M+1) = (-alpha)^M/M! d^M F_1/dw^M + less singular`, `w = 1-9Y`.

`(*)` with `alpha = 50/81` **is** the conjectured family. `ridgeline_scaling.py`
prints the identity for `j = 1..7`:

| j | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| `R_j^coef = 2^(j-1)/(j-1)!` (the law) | 1 | 2 | 2 | 4/3 | 2/3 | 4/15 | 8/105 |
| `-> R_j^doc = R^coef Gamma(j-1/2)/Gamma(1/2)` | 1 | 1 | 3/2 | 5/2 | **35/8** | 63/8 | 231/16 |
| `binom(2j-2,j-1)/2^(j-1)` (measured, `onset-defect-law.md` Sec.2) | 1 | 1 | 3/2 | 5/2 | 35/8 | 63/8 | 231/16 |

The two rows agree identically. The central binomials were the `Gamma(j-1/2)`
weighting in disguise.

This also disposes of the j = 5 rival on its own terms. `118/27` was produced by
a rational recogniser scanning `A_j`, i.e. the Gamma-weighted quantity. Carried
back to the natural normalisation it is `1888/2835`, not a simple rational, and
it corresponds to `alpha` changing to `0.6171206` at `M = 4` alone.

## 3. alpha = 50/81, derived

`Y_c(t)` is where the cluster's row transfer goes critical, so `alpha` is a local
quantity: `alpha = dlambda/dt` at `(1/9, 0)`, `lambda` the zero-momentum
eigenvalue. Rows of size `s` carry `Y^(s-1) t^(s-2)`, so at `t = 0` only 2-cell
rows survive and the bulk (delocalised) critical mode is two pending components
far apart, each taking one king step: **mass 3 x 3 = 9**, critical at `9Y = 1`.
That is where `1/9` comes from, mechanically.

At first order in `t` exactly one row is a 3-cell row. It costs `Y^2 t` and leaves
an intermediate configuration that the next row — an ordinary 2-cell row, cost
`Y` — must resolve. The two-row excursion gives
`lambda = 9Y + Y^3 t Sigma/lambda`, i.e. `lambda = 9Y + Y^2 t Sigma/9`, so at
`Y = 1/9`

```
1 - 9 Y_c = t Sigma/729,     alpha = Sigma/729,
Sigma = sum over 3-cell rows R over the bulk state of (# 2-cell rows after R).
```

`experiments/ridgeline_vertex.py` computes both counts with
`severance_w3_depths.transitions`, the vetted row-transfer enumeration (a row is
legal iff every pending block of the previous row has a cell adjacent to it) —
nothing is counted by hand. Result:

```
baseline (2-cell rows out of the bulk state)  = 9   at every gap G = 8..14
Sigma                                          = 450 at every G = 10..14
                                                   and at both span caps G+6, G+12
alpha = 450/729                                = 50/81   exactly
```

**The trap.** A 3-cell row may leave *three* pending blocks, and such a
configuration is not dead: a single cell of the next row can be adjacent to two
blocks at once when they are close, so an ordinary 2-cell row still closes it.
Filtering intermediates to two blocks loses 72 of the 450 and gives `14/27` —
84% of the answer. The unfiltered count is what the transfer demands.

Controls (all fire): the two-block filter gives a different `Sigma` (378), so the
count is not insensitive to the vertex definition; deleting a single entry from
the 3-cell row table moves `Sigma` to 438; restoring it returns 450.

**Where the exponent comes from, and why `t` does not move it.** The bulk
dispersion is the gap-walk kernel `K(u) = (1+u+u^2)^2/u^2`, `u` marking the gap.
`ridgeline_vertex.py` prints, symbolically: `K(1) = 9` (hence criticality at
`9Y = 1`), `K'(1) = 0` (`u = 1` is stationary, since `K(u) = K(1/u)`), and
`(log K)''(1) = 4/3`, so the stationary point is **nondegenerate**. A nondegenerate
quadratic minimum of the dispersion is exactly what produces a Gaussian transverse
integral and hence `(1-9Y)^(-1/2)` — the derived `theta_1 = -1/2`. An analytic
perturbation of a nondegenerate minimum remains a nondegenerate minimum, so
switching on `t` moves the *height* of the minimum — that is `alpha` — and its
location, while leaving the exponent alone. That is the argument behind assumption
1 below; it is an argument, not yet a proof, because the passage from the
dispersion to the assembled `G` is not controlled here.

**The excursion never leaves the delocalised sector.** Splitting `Sigma` by the
class of the 2-cell state it lands in: **450 land in P (two pending blocks), 0 in
J**, at every gap `G = 10..13`. This matters, because J is the class carrying the
rank-one long jump whose zero-momentum row sum diverges (the localised
`rho ~ 14.41`), and in the two-dimensional class reduction the local transfer
`[[9,0],[-18,9]]` is a Jordan block at the critical eigenvalue — the one place a
naive first-order perturbation would have been ill-defined. At first order in `t`
the vertex acts wholly inside P, where the transfer is a plain translation-
invariant walk of mass 9 and the flat mode is the honest critical mode.

## 4. Verification

Every number below is printed by the named script.

| quantity | value | source |
|---|---|---|
| `(M')` vs `(C)/(D)`, depths 1–4, `k <= 19` | 74/74 cells exact | `ridgeline_master.py` |
| `(M)` at `t^0` vs identity (II) | `k = 1..19` exact | `ridgeline_master.py` |
| RED: one perturbed excess-1 weight | breaks the identity | `ridgeline_master.py` |
| `C_1` (from `D_1`, `k <= 60`) | `0.0511843184401` | `ridgeline_scaling.py 60 1` |
| vs derived `sqrt6/(27 sqrt pi)` | relative `2.46e-12` | `ridgeline_scaling.py 60 1` |
| `alpha_1` (amplitude form, `k <= 60`) | `0.617283951065`, `7.25e-10` from 50/81 | `ridgeline_scaling.py 60 1` |
| `alpha_1` (derivative form, `k <= 60`) | `0.61728395128067`, `1.07e-09` from 50/81 | `ridgeline_scaling.py 60 1` |
| `alpha_1, alpha_2` (`k <= 29`) | `0.61728401849`, `0.61728123436` | `ridgeline_scaling.py 29 2` |
| their deviations from 50/81 | `1.10e-07`, `-4.40e-06` | `ridgeline_scaling.py 29 2` |
| calibrated estimator bias at `k <= 29` | `2.7e-06`, `5.8e-06` | `ridgeline_scaling.py 29 2` |
| `alpha_3` (`k <= 19`, the only reach for `M = 3`) | `0.61725242246`, `-5.11e-05` from 50/81 | `ridgeline_scaling.py 19 3` |
| calibrated bias at `M = 3`, `k <= 19` | `1.1e-04` | `ridgeline_scaling.py 19 3` |
| `Sigma`, `alpha` derived | `450`, `50/81` exactly | `ridgeline_vertex.py` |
| law vs binomial family, `j = 1..7` | identical | `ridgeline_scaling.py` |

Every `alpha_M` deviation is **within the estimator's own bias**, measured by
running the identical extraction on synthetic towers that obey the law exactly and
carry a `1 + c1/k + c2/k^2` correction of realistic size. So depths 2, 3 and 4 are
consistent with a single `alpha`; depth 2 alone pins it to `1.1e-09` relative,
depth 3 to `4.4e-06`, depth 4 to `5.1e-05`.

That is also what closes the `j = 5` gap as far as data can. The departure `118/27`
would demand at `M = 4` is `2.65e-04`. Against the largest deviation actually seen,
that is a factor of **5.2x** at `k <= 19`, **29.8x** at `k <= 25` and **60.1x** at
`k <= 29` — the margin widens as the data lengthens, which is what a law that holds
does and a law that is about to break does not.

The sharp estimator is the derivative form: `D_1` is exact at any `k` through the
gap walk, so dividing `D_(M+1)(k)` by `(alpha^M/M!) 9^-M (k+M)!/k! D_1(k+M)`
removes `9^k`, `k^(M-1/2)` and part of the `1/k` structure before extrapolating.

**Reproducing.** `ridgeline_master.py` and `ridgeline_vertex.py` are seconds.
`ridgeline_scaling.py K EMAX` costs whatever the family pass costs (above); the
`K = 60` excess-1 table is cached by `ridgeline_dump_families.py 60 1` as
`results/severance_w3_families_K60_e1.txt` (14 KB, second header line records that
the Python DP wrote it, not the C++ tool), after which that run is 4 s. Note `severance_w3_depths._load_table` only scans
`K_table < 40`, so the cache is read by `ridgeline_master.load_families`, which
accepts any `K_table`; the cached `K = 60` run reproduces the uncached one
digit for digit, which is the check that the cache is sound.

## 5. Limits ledger

**Derived.**

- The master identity `(M)`/`(M')`, from the proved chain identity by a change of
  variables plus the degree bookkeeping in Sec.1. (Machine-verified, not written
  as a standalone proof.)
- The implication `moving branch point, fixed exponent -1/2  ==>  C_(M+1) =
  C_1 alpha^M/M!  ==>  the binomial family`. Pure calculus; exact.
- `Sigma = 450` and hence `alpha = Sigma/729 = 50/81`, from a finite enumeration
  over the vetted transfer, stable in both the gap and the span cap.
- (Elsewhere, and reproduced here numerically:) `C_1 = sqrt6/(27 sqrt pi)`, rate
  9, `theta_1 = -1/2` — branch data of the quartic `Phi`,
  `onset-defect-depth1-closed.md`.

**Assumed, with the evidence named — this is where the weight sits.**

1. *The exponent stays exactly `-1/2` for small `t > 0`.* Evidence: the
   dispersion `K` has a **nondegenerate** stationary point at `u = 1`
   (`(log K)''(1) = 4/3`, printed symbolically), and analytic perturbations of a
   nondegenerate minimum stay nondegenerate — so the exponent is stable for the
   same reason it is `-1/2` at all. Plus `theta_j = j-3/2` measured at every
   `j <= 7` (`onset-defect-law.md` Sec.1) and derived exactly at `j = 1`. What is
   missing is control of the step from the dispersion to the assembled `G`
   (the `Phat`, `Bhat`, `Shat` combination and its rho-cancellation).
2. *`Y_c(t)` is analytic at `t = 0`.* Evidence: each order in `t` adds finitely
   many excess families (`severance_w3_depths.py` Sec.1), so the vertex expansion
   is order-by-order finite. Convergence is not proved.
3. *The rho-cancellation persists at every order in `t`,* so the `1/9`
   singularity stays dominant in `G`. Evidence: rate 9 measured at every depth
   `j <= 6`. Not derived beyond `j = 1`.
4. *The perturbative bookkeeping behind `alpha = Sigma/729`* — a flat
   zero-momentum projection within the delocalised sector. This was the weakest
   link on first writing, because the class structure is not innocent: at zero
   momentum the J row-sum **diverges** with the span cap (the rank-one long jump
   carrying `rho ~ 14.41`), and the local class transfer `[[9,0],[-18,9]]` is a
   Jordan block at the critical eigenvalue, where a naive first-order perturbation
   is ill-defined. It is now much less weak: the excursion is shown to land in P
   450 times out of 450 and in J never, so the vertex acts wholly inside the
   sector where the transfer is a translation-invariant walk of mass 9 and the
   flat mode is the honest critical mode. What remains unproved is the passage
   from "the zero-momentum mass shifts by `Y^2 t Sigma/9`" to "the bulk-edge
   branch point of `G` moves by `alpha t` with its exponent intact" — that is
   assumption 1 wearing a different hat. Supporting evidence: the resulting
   constant is `50/81` exactly, against a measurement good to `1.1e-09`.

**Verified, not derived.**

- `alpha_M` constant over `M = 1, 2, 3` — within calibrated bias at each `M`, so
  "consistent with", not "measured to be". `M = 1` is sharp (`1.1e-09`), `M = 2`
  useful (`4.4e-06`), `M = 3` weak (`5.1e-05`, against a bias envelope of
  `1.1e-04`, i.e. it constrains almost nothing on its own).
- The law at `j = 5, 6, 7` is a *prediction*, not a measurement. No exact `D_5`
  beyond `k <= 19` exists, here or anywhere.

**Open.**

- Proofs of 1–4 above. Item 4 is a self-contained piece of work: redo the
  first-order perturbation with the correct left/right critical vectors of the
  (J,P) transfer and confirm `Sigma/729` is what falls out.
- The `O(t^2)` motion `psi''(0)` — computable by the same vertex method one order
  up, and *not* needed for the amplitude family (it cancels in the scaling limit),
  so it is a consistency target rather than a gap.
- Direct data at `j = 5`. Still walled: it needs excess-4 families at `k ~ 30`.
  Measured here on dalby, single core, Python family DP:
  `(K, emax) = (19, 1)` 5.6 s, `(27, 1)` 20 s, `(60, 1)` 395 s;
  `(15, 2)` 73 s, `(19, 2)` 214 s, `(23, 2)` 516 s; `(11, 3)` 290 s.
  Cost grows mildly in `K` and steeply in `emax` — `(11, 3)` already costs more
  than `(23, 2)`. The `emax = 4` wall recorded in
  `depth-tower-bivariate-dead-end.md` stands; nothing here reaches `D_5` past
  `k = 19`.

**Weak points, conceded up front.**

- The whole result rests on the *form* of the singularity (assumptions 1–3), not
  on the constant. If the exponent drifts with `t`, the family changes and `35/8`
  goes with it. What stands against that is an argument (nondegeneracy of the
  dispersion's stationary point survives analytic perturbation) plus `theta_j =
  j-3/2` holding at seven depths — not a proof.
- `alpha = Sigma/729` matching exactly is the load-bearing coincidence-or-not. A
  first pass with a plausible-looking filter gave `14/27` and looked equally
  self-consistent until it was checked against the measurement. The reader should
  treat the enumeration, not the derivation prose, as the claim.
- No amount of this resolves `j = 5` *directly*: every `alpha_M` here has
  `M <= 3`, and `M = 4` is exactly the depth the data cannot reach. The case
  against `118/27` is structural — it is not a value the one-parameter law can
  take — supported by the nine-digit agreement of `alpha_1` with the derived
  `50/81` and by the 60x margin at `k <= 29`. Someone who rejects the law's form
  is not answered by any number in this note.

## 6. What this supersedes

- `depth-tower-bivariate-dead-end.md` "What survives": the double-scaling function
  is not merely "the tractable target", it is derived, and the note's
  `sum_j A_j t^j = (sqrt6/27) t/sqrt(1-50t/81)` is confirmed — it is
  `h(0)(1-alpha tau)^(-1/2)` with `alpha = 50/81`. Its statement that "the only
  path that settles this is a derivation" was right.
- `onset-defect-law.md` Sec.2's scoping ("verified for j <= 4 and extrapolated for
  j >= 5") is repaired at the level of *mechanism*: `j >= 5` is now a prediction of
  a one-parameter law whose parameter is derived, rather than an extrapolation of
  a numerical pattern. The section's rival rationals at `j = 5, 6, 7` were
  artefacts of scanning the Gamma-weighted normalisation.
- `onset-defect-depth1-closed.md` Sec.6's conjecture ("every fixed depth is
  algebraic, on curves sharing the branch point at 1/27, with the measured family
  as branch data") is **not** contradicted, and is refined. Each fixed-depth slice
  `F_j` does keep its singularity at `1/9` — that is `theta_j = j-3/2` with rate 9.
  What moves is the branch point of the *resummed* `G(Y,t)`; the fixed-depth
  slices are its Taylor coefficients in `t`, and the increasing exponent
  `-(j-1/2)` is exactly how a moving branch point looks after `t`-expansion at
  fixed `Y`. The amplitude family is that motion, at velocity `50/81`.
- `depth-tower-bivariate-dead-end.md` left the scaling function's algebraicity
  "genuinely uncertain — `1/2` (algebraic square root) or `1/3` (Airy,
  transcendental)". Here it is a square root, and the `1/2` is not a fit: it is
  the nondegeneracy `(log K)''(1) = 4/3 != 0` of the dispersion's stationary
  point. An Airy-class scaling function needs that stationary point to be
  degenerate, which it demonstrably is not. (This is about the double-scaling
  function of the *amplitude* direction. Whether it also settles the separate
  boundary-layer exponent `p ~ 0.39` of `onset-defect-crossover.md` is not
  established here; the two are not shown to be the same object.)
