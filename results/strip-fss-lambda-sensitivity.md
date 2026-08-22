# The strip ladder's non-analyticity is lambda's error bar, not a log term

2026-08-22, executing `docs/last-orders.md` C2.3. Desk work on the sixteen
banked `mu_H`; no compute job. Probe:
`experiments/strip_fss_lambda_sensitivity.py`, three RED controls green.

## The answer in one paragraph

`results/strip-growth-lambda-bounds.md` closes idea 6.1 (the central-charge
finite-size fit) on a diagnostic: the surface term `S(H) = H(ln λ − ln µ_H)` is
still falling at H = 17 and its increments shrink ~6.5% per rung where a clean
`1/H²` correction predicts ~11.4%, from which it reads "there is a term between
`1/H` and `1/H²`, most likely logarithmic". **The practical half of that
conclusion stands and is strengthened; the mechanistic half is not supported by
this data.** The diagnostic feeds λ in as a constant, and the surface term is
the one place an error in λ is maximally dangerous — `ln λ → ln λ + δ` adds
`H·δ` to `S(H)`, so every increment picks up a constant `+δ` that does not decay
at all. Solving for the λ that would make the ladder look clean gives
**λ\* = 7.2300**, and λ\*(H) **drifts monotonically down** across the whole
ladder — 7.604 at H = 7 to 7.230 at H = 17, decrements decaying as `H^-2.73` —
extrapolating to **λ\*(∞) = 7.1026**, within 0.008 of the independent
7.1102(1). Directly: with λ held at 7.1102, an ordinary analytic expansion in
`1/H` fits H ≥ 12 to **rms 4.4e-7** with four terms. No log term is needed to
describe the data.

## What the diagnostic actually measures

| λ fed in | dS(17) | ratio | shrink | exponent q |
|---|---|---|---|---|
| 7.1102 (differential approximants) | −0.035053 | 0.934769 | 6.52% | **+0.078** |
| 7.111 (a(n)-ratio fit) | −0.034940 | 0.934572 | 6.54% | +0.082 |
| clean `1/H²` | — | 0.882353 | 11.76% | 1 (by definition) |

The banked numbers reproduce exactly. `q` is the exponent in
`S(H) = S_∞ + c·H^-q`, solved **exactly at finite H** from
`(H^-q − (H−1)^-q)/((H−1)^-q − (H−2)^-q)`. The asymptotic shortcut
`((H−1)/H)^(q+1)` that a first cut of this probe used is wrong by enough to
matter — it reads `q = 1.065` off a ladder that is exactly `1/H²`, and the
first RED control caught it. With the exact solve, `q = +0.078`, not the
+0.113 the shortcut gives.

## Why the two lambda values in the banked note could not have found this

The note tests λ = 7.1102 and λ = 7.111 and finds the reading unchanged. Those
differ by 8e-4. The reading flips at **λ\* = 7.2300** — 150× further out. Two
values inside the error bar cannot probe a sensitivity whose scale is 0.12.

It is not an input-precision artifact either. Over all 27 last-digit
perturbations of `mu_15`, `mu_16`, `mu_17` (the ladder is banked to 7 decimals),
λ\* moves within **[7.229932, 7.230046]** — a spread of 1.1e-4 against an
offset of 0.1198, a ratio of **1050×**.

## The measurement that turns it around: lambda*(H) drifts, and where it lands

λ\*(H) is the λ at which rung H's increment ratio equals the clean prediction.
For **any** expansion whose leading correction is `a/H`, λ\*(H) → λ as H → ∞,
because the higher-order terms that spoil the rung-H ratio all vanish. So the
drift is not evidence of anything; where it lands is.

| H | 7 | 9 | 11 | 13 | 15 | 17 |
|---|---|---|---|---|---|---|
| λ\*(H) | 7.6044 | 7.4502 | 7.3574 | 7.2982 | 7.2582 | 7.2300 |

Monotone, decrements decaying as `H^-2.73`, and summing the tail gives
**λ\*(∞) = 7.1026**, offset **−0.0076** from the independent estimate.

**The extrapolator's own accuracy is measured, not assumed.** Run on two
synthetic ladders built at λ = 7.1102 — one analytic (`a/H + b/H² + c/H³` at
the coefficients fitted to the real ladder), one with a genuine log term
(`a/H + c·ln H/H²`) — it returns 7.1095 and 7.1097. So it recovers a known λ to
7e-4, and lands 7.6e-3 low on the real ladder: ten times its own control
accuracy, which is the honest size of what is left unexplained.

Note what the same table says about the raw diagnostic:

| ladder | λ\*(17) | offset |
|---|---|---|
| analytic, 3 terms | 7.1211 | +0.011 |
| genuine log term | 7.1647 | +0.055 |
| **banked mu_H** | **7.2300** | **+0.120** |

The real ladder's rung-17 offset is twice the log-term synthetic's. Read
naively that says the ladder is *less* analytic than a log model — but the same
three ladders all extrapolate to within 0.008 of the true λ, which says the
rung-17 offset is dominated by how slowly the correction series converges and
not by its functional form.

## The direct test, which does not go through lambda* at all

Can an ordinary analytic expansion fit the ladder? Fit
`ln µ_H = ln λ − Σ_j c_j/H^j` with λ **held** at 7.1102, windowed to keep low
rungs out of an asymptotic fit:

| window | terms | rms residual | worst | λ if fitted instead of held |
|---|---|---|---|---|
| H≥2 | 3 | 6.4e-3 | 1.3e-2 | 7.4178 |
| H≥8 | 3 | 1.3e-4 | 2.1e-4 | 7.2088 |
| H≥10 | 4 | 2.9e-6 | 4.1e-6 | 7.1556 |
| **H≥12** | **4** | **4.4e-7** | 6.6e-7 | 7.1487 |

The ladder is banked to 1e-7 in `mu`, i.e. ~1.5e-8 in `ln mu`, and that is a
truncation floor rather than a noise bar. So a four-term analytic expansion at
λ = 7.1102 describes H ≥ 12 to within 30× the floor. **Nothing is left over for
a log term to explain.**

The right-hand column is the same fit with λ free, and it is the whole story in
one place: λ comes out 7.15–7.25, drifting down as the window rises and as
terms are added, never reaching 7.1102 at any truncation. That upward bias is
what a slowly-converging asymptotic series does to a fitted leading constant.
It is not evidence that λ is 7.15.

## What changes, and what does not

**Stands, and is strengthened.** No `1/H²` coefficient — hence no central
charge — can be read off this ladder at H ≤ 17. The reason is now quantified:
the correction series has not converged, the fitted λ is still biased +0.04
above the independent value at the best window and order available, and rung 17
alone is off by 0.12. Idea 6.1 stays closed.

**Withdrawn as an inference.** "There is a term between `1/H` and `1/H²`, most
likely logarithmic, that this two-parameter ansatz cannot see." The data is
fully consistent with an ordinary analytic expansion whose higher terms are
still large at H = 17. The banked note already labels its log-ansatz table "a
hint, not a result" on the grounds that three parameters fit to three points
solve exactly; the same hedge belongs on the increment-shrink diagnostic that
motivated it, and it did not carry one.

**Not established.** That there is no log term. Removing the evidence *for* a
correction is not evidence *against* it. A log term with small amplitude fits
this data as well as an analytic series does — the synthetic controls show both
extrapolating to the same place. What is established is that the ladder at
H ≤ 17 cannot tell them apart, and that the diagnostic which claimed to had a
λ-sensitivity 150× larger than the range it was tested over.

## Honest limits

- λ\*(∞) rests on a two-point exponent fit and the integral of a tail. Weak
  extrapolation, reported as one; its own control accuracy is 7e-4 and the
  residual offset is 7.6e-3.
- The H ≥ 12, four-term fit has six data points against four free coefficients.
  Barely overdetermined; residuals that small are partly interpolation.
- Everything here is at λ = 7.1102(1) taken as given from
  `results/series-analysis-da.md`. If that value is wrong by more than ~0.01
  the whole reading moves, and this file inherits that dependency rather than
  removing it.
- Nothing here bears on the certified lower bound. `mu_17 ≥ 6.543` is exact
  rational arithmetic and no fit touches it.

## Reproduce

    python3 experiments/strip_fss_lambda_sensitivity.py

Instant, no compute job, three RED controls that must fire: an exactly-`1/H²`
ladder must read `q = 1` and recover its own λ; a ladder with a genuine log
term must not read `q = 1`; and a λ at or below `max(mu_H)`, where the surface
term changes sign, must be refused rather than silently used.
