# The slope-s slice growth constants, from the grand form

2026-08-09. `results/slope-slicings.md` measured the growth of the slice
`n = 2H` by fitting 20 banked counts and could only say `mu ≈ 41.8–42.5, still
drifting up with the fit window`. This note gets the same constant from the
closed-form side, analytically, and the two agree to about 3 parts in 100,000.

## The chain

1. **The grand form is a generating function for the whole `P_k` family**:
   `Σ_k P_k(n) y^k = exp(A(y) + n·B(y))`, `A = Σ a_j y^j`, `B = Σ b_j y^j`
   (`docs/proofs/grand-form.md`). `experiments/grand_form_saddle.py` extracts
   `a_j, b_j` for j = 1..19 exactly, by taking the log of the series built from
   the wired `P_1..P_19` with coefficients kept as polynomials in n.

   *This is a check only in part.* The grand form's content is that every log
   coefficient is **linear in n**, and all 19 come out linear, with `b_1 = 25`,
   `a_1 = −45` as the proof requires. But `scripts/derive_pk_fast.py` constructs
   `P_11..P_19` as `known_k + a_k + b_k·n` from the grand-form recurrence itself,
   so for those k linearity is **imposed by construction** and cannot fail. It is
   a genuine independent test only for k ≤ 8, and partially for k = 9, 10.

2. **The slope-s line lies just below onset, where the law is nearly exact.**
   `n = sH + c` means `k = (s−1)H + c`, so on `n = 2H` we have `k = H` exactly:
   the slope-2 line **is** the onset line, one step below the proved region.
   `results/onset-defect-law.md` measures the relative defect there as
   `~ e^(−1.55 k)`. So the true slice and the (invalid) law have the same
   exponential growth.

3. **Saddle point.** With `k = κH`, `n = (1+κ)H`, `κ = s−1`,
   `P_k(n) = [y^k] exp(A + nB)` gives
   `(1/H) ln T → (1−2κ)ln3 + φ(κ)`, where φ is the stationary value of
   `(1+κ)B(y) − κ ln y`, saddle `y·B'(y) = κ/(1+κ)`. Hence

   ```
   mu_s = 3^(1−2κ) · exp(φ(κ))
   ```

## Results

`y*` sits at 0.022–0.034, well inside the truncation: the last retained term
`b_19 y*^19` is 4.5e−07 at s=2. Truncation stability, `mu_2` as the number of
`b_j` used grows:

| J | 8 | 10 | 12 | 14 | 16 | 19 |
|---|---|---|---|---|---|---|
| mu_2 | 42.394991 | 42.394545 | 42.395421 | 42.394930 | 42.394566 | 42.394597 |

Over all J = 8..19 the spread is 42.393686 to 42.395421, i.e. 4e−05 relative —
**about four and a half digits, not five.** Against the direct measurement
(`experiments/slope2_law_vs_truth.py`), extrapolating the banked ratios
`T(2H,H)/T(2H−2,H−1)` in 1/H by exact elimination:

| route | mu_2 |
|---|---|
| grand-form saddle | 42.39460 |
| ratios, order-2 extrapolation (H=18..20) | 42.39549 |
| ratios, order-3 (H=17..20) | 42.39426 |
| ratios, order-4 (H=16..20) | **42.39455** |

Two independent *estimators* — 19 exact polynomials on one side, 20 raw
enumeration counts on the other — though not independent *data*: both rest on the
same banked enumeration, in different cells. The extrapolation orders themselves
span 42.39426 to 42.39549, so the supportable statement is agreement to about
3 parts in 100,000, not the 6-in-a-million a single pair of endpoints suggests.
The raw last ratio at H=20 is only 41.445, which is why the fit in
`slope-slicings.md` read as "drifting up": it was, toward this.

Higher slopes, where the truncated `B` is under more strain (`b_19 y*^19` reaches
1.1e−03 at s=5) and the measured slices are short:

| s | grand-form | last measured ratio | Richardson | points |
|---|---|---|---|---|
| 2 | 42.3946 | 41.445 (H=20) | 42.278 | 19 |
| 3 | 330.83 | 327.41 (H=13) | 318.45 | 12 |
| 4 | 2434.1 | 2596.0 (H=10) | 2194.7 | 9 |
| 5 | 17609 | 21356 (H=8) | 16447 | 7 |

s=3 is corroborated to about 1%. s=4 and s=5 have too few points for the
Richardson step to mean anything — the measured value brackets the prediction
rather than confirming it, and the truncation error is also growing. Only `mu_2`
is claimed to ~4.5 digits; `mu_3 ≈ 331` to about three; s ≥ 4 is illustrative.

## lambda from the production constants

A ray `n = sH` contributes `mu_s^(n/s)` animals, so `lambda = sup_s mu_s^(1/s)`,
and the supremum is at `s -> infinity` because the typical polyplet bounding box
has `H ~ c*sqrt(n)`. In that limit the saddle condition `y B'(y) = kappa/(1+kappa)`
becomes `y_c B'(y_c) = 1` and the formula collapses to

```
ln lambda = B(y_c) - ln y_c - 2 ln 3
```

**lambda expressed entirely in the production constants of the diagonal closed
forms** — no enumeration counts anywhere in it. `experiments/lambda_from_grand_form.py`:

| s | 2 | 3 | 4 | 6 | 8 | 10 | 20 | 40 |
|---|---|---|---|---|---|---|---|---|
| `mu_s^(1/s)` | 6.5111 | 6.9162 | 7.0240 | 7.0854 | 7.1028 | 7.1099 | 7.1175 | 7.1185 |

Monotone increasing toward ~7.119. The direct `s -> infinity` form gives a
solution for only 7 of the 10 values J = 10..19 — **J = 13, 15 and 18 give no
solution at all** inside the scan, the truncated series not even being monotone
there — and the 7 that do solve read 7.065, 7.015, 7.134, 7.147, 7.079, 7.127,
7.118. Midrange 7.081, full spread ±0.066.

So: **lambda = 7.08 ± 0.07 from the grand form alone**, consistent with the
7.110(1) of `results/series-analysis-da.md`. Quoting the J=19 endpoint as the
answer would be picking a value out of that spread; the interval is the result.
The point is not precision — it is one decimal place against six — but that the
exact diagonal polynomials and the raw growth constant are the same object seen
twice.

**A second assumption, not just truncation.** The `s -> infinity` limit needs the
law to track the truth as `x = H/k -> 0`, and the rows at s = 15, 20, 40 sit at
x = 0.07..0.026. `results/diagonal-law-below-onset.md` measures `g(x)` only down
to x = 0.10 and flags x <= 0.2 as unresolved. So the large-s rows rest on an
extrapolation of the defect's smallness into a region where it was never
measured. That is plausible — `g` is negative and steepening throughout the
resolved range — but it is an assumption, and it is independent of the truncation
error above.

The truncation error is honestly large. `|b_j|^(1/j)` reaches 20.8 at j=19 and is
still climbing, putting the radius of `B` near 0.048, while `y_c ≈ 0.0373` sits
close enough that the last retained term is 8e−03 rather than the 5e−07 that made
`mu_2` trustworthy — which is what produces both the ±0.066 spread and the three
J values with no solution.

Untried: standard series acceleration on `B(y)` — Pade or differential
approximants — before concluding the estimator is stuck. That works on the series
already in hand and needs no new `P_k`, and it would plausibly tame the
non-monotone saddle failures at J = 13, 15, 18.

## Why this does not extend

`[y^k]` needs `b_j` out to `j = k`, and the `P_k` table stops at 19, so the
saddle cannot reach further than the data it was built from. It buys precision on
`mu_s`, not new cells of the triangle. The `b_j` themselves are irregular in sign
and `|b_j|^(1/j)` is still climbing at j=19 (20.83), so the radius of `B` is not
resolved either — the saddle is safe only because `y*` is an order of magnitude
inside it.

## What this closes

The last line of `slope-slicings.md` proposed fitting the slope-2 offsets jointly
with a shared `mu` as "the one lever that would add real information". That is
superseded: the saddle gives `mu_2` to ~4.5 digits without any fitting. The rest
of `slope-slicings.md` is unaffected — its subject is whether the slope-2 slice
satisfies a **recurrence**, and it does not. Knowing `mu_2` exactly-ish does not
give a law; `theta` for that slice remains unidentified in roughly [−0.6, −0.2].
