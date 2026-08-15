# The diagonal law's error term: the thin-diagonal rate, exponent j−3/2, amplitude √6/27

2026-08-09, continuing `results/diagonal-law-below-onset.md`. That note measured
the closed form `T(n,n−k) = P_k(n)·3^(n−1−3k)` to be asymptotically exact below
its proved onset `n ≥ 2k+1`, and found **no** exact structure in the defect
(C-finite to order 8, P-finite to (r,d)=(4,4), all null). This note finds the
structure the algebraic searches could not see, because it is analytic.

*Revised 2026-08-09 after adversarial review. §1 and §2 now rest on
non-terminating controls (`experiments/defect_controls.py`); the earlier versions
of those sections quoted a control that terminated and therefore measured
nothing. The rate and exponent came out stronger under the honest controls, the
amplitude family weaker. Details in `docs/onset-defect-plans.md`.*

Write the defect at depth `j = 2k+1−n` below onset as `D_j(k) = T − law`.

## 1. The rate is 9 to 2e−05 at depth 1, and the exponent is j − 3/2 throughout

`experiments/onset_defect_nine.py`, `experiments/defect_nine_exponent.py`, and
the control apparatus in `experiments/defect_controls.py`. The defects are exact
`Fraction`s; the extraction runs in mpmath at 60 digits and agrees with float to
≤ 6e−11 relative, so arithmetic precision was never the limiting factor — the
correction-series tail is.

**The naive estimator is biased and the bias must be removed.** If
`D = C·9^k·k^θ` then `L_k := k(D_k/D_{k−1}/9 − 1) → θ`, killed by one Richardson
step. Run against a control whose correction series does **not** terminate, that
estimator carries a systematic of up to 0.02 in θ and 0.03 in `r` — enough to
account for every apparent drift in the raw numbers. What follows is the
bias-calibrated version: Richardson to order 3, with the matched control's own
offset subtracted, and the bar set by that control at the same data length.

| j | θ_j | j − 3/2 | rate r_j |
|---|---|---|---|
| 1 | **−0.5000 ± 0.0010** | −0.5 | **8.999998 ± 2.2e−05** |
| 2 | **+0.5000 ± 0.0025** | +0.5 | **9.000000 ± 2.1e−03** |
| 3 | +1.5002 ± 0.0065 | +1.5 | 8.9988 ± 5.6e−03 |
| 4 | +2.5006 ± 0.0110 | +2.5 | 8.9945 ± 8.9e−03 |
| 5 | +3.4974 ± 0.0130 | +3.5 | 9.0395 ± 5.1e−02 |
| 6 | +4.4999 ± 0.0090 | +4.5 | 9.0025 ± 7.2e−02 |
| 7 | +5.4983 ± 0.0385 | +5.5 | — |

`θ_j = j − 3/2` is consistent at **every** depth j = 1..7, pinned to ±0.001 at
j=1 and ±0.04 at j=7. `r = 9` holds to five decimals at j=1 and is inside the bar
at every other depth.

Two corrections to what an earlier version of this note said. The raw estimator's
θ appeared to drift low with j and its `r` appeared to fall away from 9 (8.98,
8.91, 8.77 at j = 3, 4, 5) — **both drifts are reproduced by a control whose θ
and rate are exactly right by construction.** They are the estimator, not the
data. In particular the old j=5 entry of 8.7707 was not evidence of a rate below
9. Conversely, "j ≥ 5 is out of resolution" was too pessimistic: it is out of
resolution *for the shipped estimator*, not for the data.

**Caveat on the calibration.** The matched control is built assuming
`θ_j = j − 3/2`, so this is a self-consistency test. It removes "θ drifts low" as
evidence *against* the law; it is not an independent proof of it.

## 2. The amplitude is √6/(27√π); the family is pinned for j ≤ 4 only

`experiments/defect_amplitude.py`, `experiments/defect_amplitude_family.py`,
`experiments/defect_controls.py`.

**The digit count comes from non-terminating controls.** An earlier version of
this note claimed a control fixed the precision. It did not: that control's
correction series terminated at 1/k², which Richardson of order ≥ 2 interpolates
exactly, so its reported ~1e−15 error was float roundoff and it measured nothing.
The suite now runs four flavours — smooth 1/k, geometric tail, half-power
(1/k^1.5), and log (log k/k) — and the relevant one sets the bar.

```
C_1 = 0.05118432,  control-backed bar 3e−07 relative
√6/(27√π) = 0.05118432,  sitting 5e−08 away — inside the bar
```

Six to seven significant figures, not eight. The old "2.3e−08" was a single
Richardson order's point value, about 10× tighter than anything controlled.

Two things make the recognition solid rather than lucky:

- **Contamination is bounded.** The order-to-order step signature of the real
  data falls ~50× between orders 2 and 5; a half-power or log contaminant at the
  amplitudes the control suite uses falls only ~5×. Adding `1 + ε/k^1.5` to the
  matched control, ε = 5e−04 already overshoots — so any half-power term is
  bounded at amplitude ≲ 5e−04, three orders below the tested flavour.
- **The recognition is unique.** Over all `√m/(n√π)` with m ≤ 200, n ≤ 400,
  exactly **one** value lies within 1e−06 of the measurement.

`k^(j−3/2)` is the coefficient asymptotics of a singularity `(1−9z)^(−(2j−1)/2)`,
so put `A_j = C_j·Γ(j−1/2)`. Then `R_j := A_j/A_1·(81/25)^(j−1)` measures as

| j | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| measured | 1.000000 | 1.000001 | 1.499785 | 2.498812 | 4.370843 | 7.866341 | 14.441622 |
| `binom(2j−2,j−1)/2^(j−1)` | 1 | 1 | 3/2 | 5/2 | 35/8 | 63/8 | 231/16 |
| bar | 5.5e−07 | 1.8e−04 | 4.1e−04 | 1.1e−03 | 2.9e−03 | 6.2e−03 | 1.1e−02 |
| rationals q ≤ 32 inside bar | 1 | 1 | **3/2 only** | **5/2 only** | 8 | 18 | 20 |

**Supported: j ≤ 4.** The binomial value is the *only* rational with denominator
≤ 32 inside the bar, at j = 3 and j = 4.

**Consistent but not selected: j = 5, 6, 7.** The binomial value is inside the
bar, but so are 8, 18 and 20 other simple rationals — among them 118/27, 118/15
and 130/9, which is exactly what the script's own recognizer reports when its
tolerance is set to what the data actually supports rather than a hard-coded
2e−04. At j=5, 118/27 = 4.370370 is *closer* to the measurement than 35/8.

So the form

```
A_j = (√6/27) · (25/81)^(j−1) · binom(2j−2, j−1) / 2^(j−1)
```

is verified for j ≤ 4 and extrapolated for j ≥ 5 — **four** numbers with **two**
degrees of overdetermination, not the seven-fold confirmation an earlier version
of this note claimed. It is also conditional on `θ_j = j − 3/2`: the C_j
extraction assumes it, and since `|d ln C/dθ| ≈ 4.9`, relaxing θ by its §1
interval widens every bar by ~20×, at which point even j=3 admits 19/13, 22/15,
25/17 and others.

Since `Σ_M binom(2M,M)(t/2)^M = (1−2t)^(−1/2)`, the depths sum:
`Σ_j A_j t^(j−1) = (√6/27)/√(1 − 50t/81)` — subject to the same scoping.

## 2b. Second Term: the 1/k coefficient is not recognisable, and is anomalously small

> **SUPERSEDED 2026-08-09, `results/onset-defect-depth1-closed.md`:** the
> depth-1 generating function is algebraic and `a` is exact —
> `a = 3293/92928 − 3251√3/185856 = 0.005138939956706…`, an element of
> `Q(√3)` outside every field searched below. The kill criterion was right to
> fire. The section stands as the honest record of what k ≤ 19 could see.

`experiments/second_term.py`, `experiments/second_term_recognise.py`. Plan
**Second Term** of `docs/onset-defect-plans.md`, worked 2026-08-09. Its kill
criterion fired; the by-products are worth more than the target was.

**The target.** `D_1(k) = C_1·9^k·k^(−1/2)·(1 + a/k + …)`. Dividing by the
*conjectured exact* `C_1` and forming `k·B_k` where
`B_k = D_1(k)·9^(−k)·k^(1/2)/C_1 − 1`, the limit is `a`.

```
a = 0.005139 ± 0.000033      (2.2 significant figures)
```

**Caveat on that bar (review finding).** `experiments/second_term_recognise.py`
as shipped prints `± 2.0e−02` and "3903 rationals", using the half-power control
at amplitude 0.3. The tighter bar quoted here rescales that control down to the
ε ≤ 5e−04 contamination bound of §2, and the rescaling was done at the shell, not
in the script. The arithmetic reproduces, and the kill criterion fires under
either bar — but this precision is **not backed by shipped code**, and the
ε-bound it rests on is itself soft. Treat ±3.3e−05 as indicative and ±2e−02 as
what the repo can currently defend.

The bar is the worst of: a data-like geometric tail (6.7e−08), a half-power
contaminant at its measured upper bound ε = 5e−04 (3.3e−05), a log contaminant at
the same bound (7.4e−06), and the order-to-order spread (2.4e−06). **526 rationals
with q ≤ 4000 lie inside that bar.** Recognition is not possible on k ≤ 19, and
per the plan the work stops rather than fitting harder.

**By-product 1: `C_1` is confirmed an order of magnitude more sharply.** A wrong
`C_1` does not shift the limit of `k·B_k` — it makes it **diverge linearly**, so
this construction is far more sensitive than the amplitude extraction. Injecting
a relative error ε into `C_1` and watching the Richardson order-spread:

| ε | 1e−09 | 1e−08 | 3e−08 | 1e−07 | 1e−06 | 1e−05 |
|---|---|---|---|---|---|---|
| spread / baseline | 1.0 | 1.1 | 1.3 | 2.1 | 12.4 | 114.8 |

Flat to ε ~ 1e−08, proportional beyond. So `C_1 = √6/(27√π)` holds to roughly
**1e−07 relative**, sharper than the 3e−07 of §2.

Three caveats, all from review. The argument is sound in principle — a wrong `C_1`
injects a term linear in k, which cannot be absorbed by a 1/k Richardson basis, so
nothing is being fitted away. But 3e−08 is the point where the spread rises only
1.3×, and a partial cancellation against the true tail could mask up to ~1e−07,
so the earlier "3e−08" was about 3× optimistic. The whole construction is also
conditional on `θ = −1/2` exactly. And **no script in the repo computes this
table** — it was run at the shell. It should be moved into
`experiments/second_term.py` before being relied on.

**By-product 2: the `25/81` depth ratio is confirmed the same way.** Running the
identical construction at j = 2 with `C_2 = A_1·(25/81)/Γ(3/2)`, `k·B_k` is again
bounded, converging to `a_2 = 0.6851` with orders 3–5 agreeing to 4e−05. Had the
`25/81` been wrong, this would have diverged. That is a much stronger statement
about the j=2 amplitude than the `R_j` table of §2, which only bracketed it.

**By-product 3: `a` is anomalously small, and rules out the obvious closed form.**
`|a| = 0.0051` means the bare leading term `C_1·9^k·k^(−1/2)` is already accurate
to 3e−04 relative by k = 19, with almost no 1/k correction to find — which is
precisely why `a` cannot be measured well. It also discriminates: the central
binomial `binom(2k,k)/4^k` has `a = −1/8 = −0.125`, twenty-four times larger and
of the opposite sign. So `D_1(k)` is **not** a constant times
`binom(2k,k)(9/4)^k`, confirming from the asymptotic side what the P-finite search
(Appendix) found algebraically.

**What would move this.** ~~Nothing available. The bar is set by the correction
tail at k ≤ 19, and `P_k` stops at 19.~~ **MOVED, by derivation rather than
data (Ridgeline, 2026-08-14, `results/ridgeline-depth-amplitudes.md`):**
the amplitude family is one derived constant, α = 50/81, and **j = 5 is
35/8**; the rival rationals this section reports were artefacts of scanning
the Γ-weighted normalisation. This section's measurements stand; its
extrapolation scoping is superseded.

## 3. The resummation is a boundary layer, not a global scaling form

Combining §2 with the per-depth singularity gives the formal bivariate statement
`(√6/27)·(1 − 9z − (50/81)t)^(−1/2)`, i.e. pointwise

```
D_j(k) ≈ (√6/27)·binom(2N,N)/4^N·binom(N,k)·9^k·(50/81)^(j−1),   N = k+j−1
```

**Tested and it does not hold globally** (`experiments/defect_bivariate.py`).
Residual `ln D_measured − ln D_predicted`, and its slope per unit k inside each
band of `x = H/k` — a wrong exponential rate shows as a nonzero slope:

| x band | 0.85–1.00 | 0.70–0.85 | 0.55–0.70 | 0.40–0.55 | 0.25–0.40 | 0.10–0.25 |
|---|---|---|---|---|---|---|
| slope per k | **−0.009** | −0.077 | −0.201 | −0.398 | −0.677 | −1.146 |

So the form is right in a layer around the onset line and degrades smoothly with
depth. The reason is visible in the derivation: §2's amplitudes are asymptotic in
k at **fixed** j, and the resummation needs `j ~ k(1−x)`, which is a uniformity
the data refuses. Predicting the `g(x)` table of `diagonal-law-below-onset.md`
from this form fails outright — it gives `g(0.35) = +0.66` where the measurement
gives −0.22, and `g > 0` would mean a defect exceeding the count. **The §2 law is
a near-onset law. It does not explain g(x).**

## 4. Where the rate comes from: it is the thin-diagonal rate per cell

**Revised 2026-08-09** while working the Spectral Edge plan, which exposed a
framing error in the first version of this section.

On the depth-j line `n = 2k+1−j`, so `k = (n+j−1)/2` and

```
9^k = 3^(n+j−1)
```

**Measured per cell, the defect's rate is exactly 3** — and `T(n,n) = 3^(n−1)` is
the thin diagonal, one cell per row, three ways to place the next one. So the
statement is

```
D_j(k) ≈ C_j · 3^(j−1) · 3^n · k^(j−3/2)
```

the defect at any fixed depth grows exactly like the number of *maximally thin*
animals of the same cell count, modulated by a power of k.

The first version of this section called the rate "the square of the thin-diagonal
growth", reading `9 = 3²`. That is the same measured fact in a different variable:
on every line we can reach, `n` and `2k` differ by a constant, so `9^k` and `3^n`
are indistinguishable. **The data cannot separate the two readings**, and the
per-cell one is simpler and requires no two-strand story. The squared reading also
had an impossibility hiding in it: 9 exceeds every `μ_H` (which climb to
λ = 7.11), so nothing in the strip spectrum could ever sit there. 3 can.

### The cross-lattice test, restated

On the square lattice a one-cell row admits exactly one continuation, so
`T_sq(n,n) = 1` and the per-cell prediction is a defect that does not grow at all.
`experiments/square_defect_rate.py` on `results/bbox_square4_n21.txt`:

- `T_sq(n,n−k)` is a polynomial in n of degree exactly k, first valid at exactly
  `n = 2k+1`, for k = 0..5 — independent corroboration of the onset formula on a
  lattice whose diagonal law was never part of this project.
- Depth-1 defect `T_sq(2k,k) − poly` for k = 1..5: **+1, −1, +1, −1, +1.**

Magnitude exactly 1, no growth, against the polyplets' `3^n`. The prediction holds,
including a sign alternation the king lattice does not have. Note what this test
can and cannot do: since 1 = 1², it confirms the per-cell reading but **cannot**
discriminate it from the squared reading.

**Nor can anything else** (review finding, 2026-08-09). On any lattice whose onset
is also `n = 2k+1`, a thin rate `g` gives `g^n = (g²)^k·g^(1−j)`, so the two
readings are the *same function of (k,j)* wherever the defect exists. No statistic
in any such triangle separates them. An earlier version of this paragraph, and a
report to jasonp, claimed the Third Lattice plan would discriminate; that is
false. What Third Lattice tests is whether the defect rate is tied to the thin
rate **at all** — real and worth doing, but a different question.

## 5. What changes

- `diagonal-law-below-onset.md` §3 says the defect has no structure of its own.
  That stands as written — it was a statement about *algebraic* structure, and
  the constants here are `√6`, `π`, half-integer exponents, none of which a
  C-finite or P-finite search can see. This note is the analytic counterpart, and
  the two are consistent: an order-1 P-finite ratio `9(k+a)/(k+b)` would
  reproduce `9^k k^(−1/2)` asymptotically, and that search came back empty, so the
  defect is not exactly hypergeometric — only asymptotically.
- Practically: the below-onset smoke test of that note gets quantitative.
  `experiments/defect_holdout.py` fits the amplitude on k <= 14 only — recovering
  `√6/(27√π)` to 2.0e−06, a figure **not** re-audited under the new control suite
  (its k ≤ 14 window has its own, wider bar; treat the exponent of that number as
  indicative) — and then predicts cells it never saw:

  | k | 15 | 16 | 17 | 18 | 19 |
  |---|---|---|---|---|---|
  | digits of `T(2k,k)`, law alone | 9.9 | 10.5 | 11.2 | 11.9 | 12.6 |
  | law + §2 defect estimate | 13.2 | 13.9 | 14.6 | 15.3 | **16.0** |

  A flat +3.4 digits across the holdout. `T(38,19)` — a cell the closed form is
  provably not valid for — comes out to 16 correct digits. Still a smoke test,
  still not a second source: it cannot certify an exact integer.

## Limits

- `P_k` is wired only to k ≤ 19, and `P_19` is fitted-no-holdout, so the k=19
  column inherits that status.
- `θ_j = j − 3/2` is consistent for j = 1..7, at ±0.001 (j=1) to ±0.04 (j=7),
  after calibrating the estimator's bias — but the calibration control assumes
  the law, so it is self-consistency, not independent confirmation.
- The amplitude identification `C_1 = √6/(27√π)` is a numerical recognition at
  5e−08 relative against a control-backed bar of 3e−07, over 18 exact data
  points. Not a derivation.
- The amplitude family is **verified only for j ≤ 4**. At j ≥ 5 the binomial form
  is consistent with the data but not selected by it — 8 to 20 other simple
  rationals fit equally well.
- Every `C_j` bar is conditional on `θ_j`: a 0.01 shift in θ moves `C_j` by ~5%.
- §3 is a negative result about a formal resummation, not about the underlying
  singularity; whether a uniform (j,k) form exists is open.
- The square-lattice arm rests on n ≤ 21 and k ≤ 5.

## Appendix: the defect is not D-finite in the reachable envelope

`experiments/defect_pfinite_full.py`. `D_j(k)` is an exact rational for k <= 19,
so the question "is the defect's generating function algebraic?" is decidable up
to an envelope: algebraic => D-finite => P-finite. Exact rational nullspace, last
two points held out and required to be predicted, >= 2 equations of slack, onset
scanned t = 0..4.

Controls, all firing or not firing as they must:

| sequence | result |
|---|---|
| `poly(k)*3^k` | FOUND (r,d) = (1,2) |
| `9^k` | FOUND (1,0) |
| `binom(2k,k)(9/4)^k`, the nearest hypergeometric to the measured asymptotics | FOUND (1,1) |
| hash noise | none |

| defect | points | result | envelope reached |
|---|---|---|---|
| `D_1(k)` | 18 | **none** | r=1:d<=5, r=2:d<=3, r=3:d<=1, r=4:d<=1 |
| `D_2(k)` | 18 | **none** | same |
| `D_3(k)` | 17 | **none** | r=1:d<=5, r=2:d<=2, r=3:d<=1 |
| `D_1(k)/[binom(2k,k)(9/4)^k]` | 18 | **none** | same as D_1 |

The third control matters most: a sequence with exactly the measured asymptotics
`~ 9^k/sqrt(pi k)` is found immediately at (1,1), so the search is not blind to
the shape being proposed. The defect is not that sequence times anything simple.
Its reduced form converges to the right constant the slow way instead —
`D_1/[binom(2k,k)(9/4)^k]` reads 0.0913508 at k=19 against `sqrt6/27 = 0.0907218`,
an O(1/k) approach, which is a second confirmation of the amplitude from a
different normalisation.

Consistent with the banked theorem that the anisotropic generating function is
not D-finite (`results/anisotropic-not-dfinite.md`).
