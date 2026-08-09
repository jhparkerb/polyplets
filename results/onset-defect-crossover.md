# The near-onset layer: width j ~ k^0.4, and what does and does not hold

**Revised 2026-08-09 after adversarial review — the crossover curve and the
exponent interval are downgraded below; the family exclusions stand.**

2026-08-09. Plan **Boundary Layer** of `docs/onset-defect-plans.md`.
`experiments/boundary_layer.py`.

`results/onset-defect-law.md` §3 records that the near-onset resummation

```
D_j(k) ≈ (√6/27)·binom(2N,N)/4^N·binom(N,k)·9^k·(50/81)^(j−1),   N = k+j−1
```

is accurate close to the onset line and degrades smoothly with depth. Smooth
degradation implies a scaling variable. This note finds it.

## The residual surface

`residual = ln D_measured − ln D_predicted` over **168 banked below-onset cells**
(k = 4..19, all j with H ≥ 2). Two candidate families were scored by how tightly
the residual collapses onto a single curve — the spread within bins of the
scaling variable, normalised by the total spread:

- **A:** `residual = f(j/k^p)` — a boundary layer of width `k^p`.
- **B:** `residual = k^q·φ(j/k)` — a large-deviation form, which is what §3's
  per-band slopes suggest at first reading.

Each family was calibrated on synthetic surfaces built *exactly* in that family
over the same (k,j) extent, so the achievable floor is measured, not assumed.

| family | control floor | best measured score |
|---|---|---|
| A, `f(j/k^p)` | 0.0212 | **0.0224** |
| B, `k^q φ(j/k)` | 0.0270 | 0.0496 |

**Family A reaches its own floor; family B does not.** The large-deviation form is
excluded — the residual is a boundary-layer effect, not a large deviation, which
is the opposite of what §3's band table suggests when read casually.

## The exponent

```
p = 0.385,   interval [0.345, 0.485]
```

The interval is where the score stays within 15% of the best, with the floor
folded in. Calibration: surfaces built at known p = 0.35, 0.40, 0.45, 0.60 are
returned as 0.325, 0.390, 0.440, 0.590, so the scan is near-unbiased except that
it cannot separate 0.45 from 0.50.

| candidate | score / best |
|---|---|
| p = 2/5 | 1.05 |
| p = 1/2 (Gaussian crossover) | 1.18 |
| p = 2/3 (Airy, coalescing saddle) | 1.90 |
| p = 1 (no boundary layer) | 5.17 |

**Airy-type and no-layer are excluded** — robustly; no subset tried comes near
them.

**The best-fit value is fragile and 1/2 is NOT excluded** (review finding). Under
resampling the returned p moves a long way: 0.44 dropping k < 8, 0.315 keeping
j ≤ 5, 0.275 keeping u ≤ 2, 0.44/0.425 at nbin 16/24. The quoted interval
reproduces under the 15% rule but understates that sensitivity, and the scan's own
calibration cannot separate 0.45 from 0.50. So **"1/2 disfavoured by 18%" is not
supportable**; the only defensible statement is `p ≈ 0.4`, with 2/3 and 1
excluded.

## The crossover function

With `u = j/k^0.385`, a one-parameter curve fits the surface as a whole:

```
f(u) = c·u·(1 − u),      c = 0.612,   rms 0.147 vs range 16.91
```

**This fit does not survive review, and should not be used.** The rms is measured
against the *range*, which is dominated by the monotone `u > 1` tail that any
smooth decreasing function would capture. Inside the layer the fit is simply
wrong: over `u < 1` (31 cells) the measured residuals run +0.007 to +0.10, mostly
0.01–0.02, while the curve says 0.10–0.15 through the same range. Refitting `c` on
the interior alone gives **0.063**, ten times smaller. The "peak +0.15 at u = 1/2"
is the fit, not the data (~+0.02 there), and the freed-quadratic check inherits
the same tail domination.

**What is real** is the sign structure, which is in the data directly and needs no
fit: the residual is small and positive inside, negative and growing outside, and
crosses near `u ≈ 1`.

Two readings follow:

- **The layer's edge sits near u = 1**, i.e. `j ≈ k^0.4`. Inside, the resummation
  slightly under-predicts (residuals ~+0.01 to +0.02); outside, it over-predicts,
  the residual grows, and it never crosses back.
- At k = 19 the layer is `j ≲ 3`, close to the depth range where §2 of
  `onset-defect-law.md` finds the amplitude family supported (j ≤ 4). **Treat this
  as suggestive, not as independent confirmation** — §2's boundary is where
  rational recognition loses uniqueness, a bar-width statement, while the `u = 1`
  edge comes from the tail-dominated fit above, and 3-vs-4 is one small integer.

## What it does not do: reach g(x)

At fixed `x = H/k`, `j ≈ k(1−x)` so `u ≈ k^0.615·(1−x) → ∞`. The limit shape
`g(x)` of `results/diagonal-law-below-onset.md` therefore lives entirely in the
`u → ∞` tail of `f`, and on k ≤ 19 the data reaches only `u = 5.8`. The
crossover function is measured; its asymptote is not, and the fitted `u(1−u)`
cannot be that asymptote (it would eventually predict a defect exceeding the
count).

So the plan's stated goal — explain `g(x)` — is **not** achieved. What is achieved,
after review, is narrower than first written: the exclusion of the
large-deviation family and of the Airy and no-layer exponents, plus a
layer edge near `j ≈ k^0.4` visible directly in the residual's sign.

## Limits

- 168 cells, k ≤ 19, and `P_k` stops there.
- `p ≈ 0.4` is not a recognised crossover exponent, and **1/2 is not excluded** —
  the best-fit value moves between 0.275 and 0.44 under resampling.
- `f(u) = c·u(1−u)` is withdrawn: tail-dominated, and wrong by 10x inside the
  layer it purports to describe.
- The exponent interval, the fitted `c`, and the resampling figures are all
  computed off-script; `experiments/boundary_layer.py` prints none of them. They
  should be moved into the script before being cited again.
- The residual is defined against the §3 resummation, which is itself scoped to
  j = O(1). Both the surface and its collapse inherit that scoping.
