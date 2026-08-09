# The diagonal law below its onset: exactness stops, accuracy does not

2026-08-09. The diagonal law `T(n,n-k) = P_k(n)*3^(n-1-3k)` is proved for
`n >= 2k+1` and verified to fail at `n <= 2k` (`docs/proofs/diagonal-law.md`).
Everything below onset is the middle band: `H = n-k <= n/2`. This note measures
**how** it fails there, using the wired `P_k` (k = 1..19,
`orchestrator/sweep.go`) against the banked triangle.

Sanity gate, run first: the law reproduces every banked cell at and above onset,
0 mismatches (`experiments/defect_below_onset.py`).

## 1. The law is wrong below onset by a vanishing relative amount

Correct leading digits of `T(n,n-k)` given by the closed form, at depth
`j = 2k+1-n` below onset (`experiments/law_below_onset.py`):

| j \ k | 8 | 11 | 14 | 17 | 19 |
|---|---|---|---|---|---|
| 1 | 5.1 | 7.2 | 9.2 | 11.2 | **12.6** |
| 2 | 3.6 | 5.5 | 7.5 | 9.4 | 10.7 |
| 4 | 1.3 | 3.1 | 4.9 | 6.7 | 7.9 |
| 6 | -0.8 | 1.2 | 2.9 | 4.6 | 5.7 |
| 8 | -5.4 | -0.6 | 1.3 | 2.8 | 3.9 |

So the closed form predicts `T(38,19)` — a cell it is provably not valid for —
to **12.6 correct digits**. The relative error behaves as
`~ C * (0.21)^k * (25)^j`. The defect `T - law` is positive throughout: the law
underestimates below onset.

## 2. The error has a large-deviation limit shape

`experiments/defect_collapse.py`. With `x = H/k`, the quantity
`(1/k) ln((T - law)/T)` converges as `g_k(x) = g(x) + c(x)/k`. Richardson in
`1/k` over k = 10..19 gives residuals of ~1e-3 for `x >= 0.3`:

| x = H/k | g(x) | c(x) | digits at k=19 | at k=40 |
|---|---|---|---|---|
| 0.35 | -0.2232 | 4.14 | 1.8 | 3.9 |
| 0.50 | -0.3326 | 1.73 | 2.7 | 5.8 |
| 0.65 | -0.5416 | 0.66 | 4.5 | 9.4 |
| 0.80 | -0.8587 | 0.21 | 7.1 | 14.9 |
| 0.95 | -1.3084 | -0.07 | 10.8 | 22.7 |

`g(x) < 0` at every x tested down to 0.10 — **there is no crossing**. For any
fixed ratio `H/k`, the closed form's relative error decays exponentially in k.

The reading that matters: exactness stops abruptly at the onset, but accuracy
does not stop anywhere. The law is asymptotically exact throughout the region
where it is invalid; what it loses at `n = 2k` is the last digit, not the
leading behaviour.

## 3. The defect has no exact structure of its own

Searched in k at each fixed depth j (`experiments/defect_structure.py`):
C-finite to order 8 and P-finite to (r,d) = (4,4), holdout of the last two
points, slack rule enforced.

- control, exact `25^k/k! * (k^2+3)`: **found**, P-finite (r,d) = (1,3) — right
  answer for a hypergeometric term.
- control, structureless: not found.
- **defects at j = 1..12: nothing.**

Along the other direction (`experiments/defect_in_H.py`) the defect ratios
decline smoothly to zero at the onset with ratio-of-ratios roughly constant
(0.75 at k=13, 0.82 at k=19, drifting to 1) — the signature of the scaling form
above, not of a geometric or hypergeometric term.

So the below-onset region carries **analytic** structure (a limit shape) and no
**algebraic** structure, which is the same verdict `results/slope-slicings.md`
and `results/band-structure-probes.md` reach from other directions.

**Followed up the same day, `results/onset-defect-law.md`:** the analytic
structure is sharper than a limit shape. At each fixed depth j the defect is
`D_j(k) ~ C_j·9^k·k^(j−3/2)` — rate 9 to 2e−05 at j=1, exponent
`j − 3/2` consistent at every depth j = 1..7, `C_1 = √6/(27√π)` at 5e−08 against
a 3e−07 bar, and the family
`A_j = C_j Γ(j−1/2) = (√6/27)(25/81)^(j−1) binom(2j−2,j−1)/2^(j−1)`
verified for j ≤ 4 and extrapolated beyond. Measured per cell the rate is
exactly 3, the thin-diagonal rate `T(n,n) = 3^(n−1)` itself (`9^k = 3^(n+j−1)` on
the depth-j line); confirmed on the square lattice, where that rate is 1 and the
depth-1 defect does not grow at all, being exactly `(−1)^(k+1)`. None of this contradicts the null above: half-integer exponents and √6
are invisible to a C-finite or P-finite search. It does **not** yield `g(x)` —
the resummation over j is a near-onset boundary layer only.

## 4. What this is good for

- **A cheap high-precision check on the most expensive cells of any future
  run.** The wired `P_k` predicts below-onset cells to 8-12 digits at k in the
  teens; a swept value disagreeing in the leading digits is a bug signal, at
  zero compute. It is a smoke test, not a second source: it cannot certify an
  exact integer.
- It does **not** help a(41) directly. For n=41 every cell with k <= 19 is at or
  above onset already (n >= 2k+1 requires k <= 20), and the expensive cells
  H = 20, 21 need `P_21`, `P_20`, which need pinning data at n >= 41 that does
  not exist.

## Limits

- `P_k` is wired only to k = 19, and `P_19` is fitted-no-holdout, so the k=19
  column inherits that status.
- The Richardson limit is trustworthy for `x >= 0.3` (residual ~1e-3); at
  `x <= 0.2` residuals reach 0.03 and `c(x)` grows past 20, so `g` there is not
  resolved and the "no crossing" claim is a measurement over the resolved range
  plus an unresolved tail.
- Everything rests on the banked triangle; no independent enumeration was run.
