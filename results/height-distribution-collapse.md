# The polyplet height distribution has a universal limit shape (data collapse)

2026-07-11 (research during the a(22) fleet run). `experiments/height_collapse.py`
on the FULL exact height triangle `results/ns_a36/perheight/hH.out` (all H=1..36,
n≤36; row sums verified == a(n) against the b-file for n≤33, chain-consistent to 36).

> **Refreshed on the final n≤40 data 2026-07-31 — see "Refreshed at n=40" at the
> bottom.** The n≤36 numbers below all reproduce exactly; the addendum extends them.

## Question

[[nu-exponent]] established the mean height grows as ⟨H⟩ ~ n^ν with ν→0.6407 (the
2D lattice-animal extent exponent). Does the *whole* height distribution T(n,H)/a(n)
have a universal limit shape — i.e. single-parameter scaling P_n(H) ≈ (1/⟨H⟩)·g(H/⟨H⟩)?

## Result — a universal shape g, tightening with n

**Parameter-free shape collapse** (scale each row by its own mean, no exponent
assumed): plot ⟨H⟩·P_n(H) against x = H/⟨H⟩. The rows collapse onto one curve, and
the collapse **tightens monotonically with n** (relative variance across a window):

| n-window | collapse rel-variance |
|---|---|
| 8,12,16,20 | 0.191 |
| 16,20,24,28 | 0.101 |
| 24,28,32,36 | **0.065** |

The moments of H/⟨H⟩ converge, confirming a limiting shape:

| n | std/mean | skew |
|---|---|---|
| 12 | 0.2335 | +0.249 |
| 20 | 0.2295 | +0.311 |
| 28 | 0.2274 | +0.337 |
| 36 | 0.2261 | +0.351 |

So the limit shape g has **coefficient of variation ≈ 0.225** and is **right-skewed
(skew ≈ 0.35+)** — a longer tail toward tall/spindly shapes. The collapsed g(x=H/⟨H⟩)
at n=36:

```
 x=0.55 |######
 x=0.65 |##################
 x=0.75 |##################################
 x=0.85 |###############################################
 x=0.95 |###################################################   <- peak ~0.95
 x=1.05 |###############################################
 x=1.15 |######################################
 x=1.25 |##########################
 x=1.35 |################
 x=1.45 |#########
 x=1.55 |####
 x=1.70 |#
```

## The exponent is finite-size renormalized at n≤36 (honest caveat)

Fixing the *value* of ν is the hard part. Two estimates from the full data:
- **mean-based ν_eff = d log⟨H⟩ / d log n** drifts **0.712 (n=12) → 0.678 (n=36)**,
  monotonically down toward the asymptotic 0.6407 but not there — n≤36 is still
  pre-asymptotic, corrections are large.
- an **exponent collapse** x=H/n^ν prefers ν_eff ≈ 0.71 (finite-size-inflated), so
  forcing the asymptotic 0.6407 gives a visibly worse collapse than 0.71 at these n.

**Reading:** the single-parameter scaling *form* is confirmed (the shape is
universal and its collapse sharpens with n), but the *exponent* at n≤36 is an
effective ~0.68 renormalized upward from the true 0.6407 by confluent corrections
(consistent with the paper's Δ₁=1/2 correction and [[nu-exponent]]'s drift). The
clean, robust statement is **shape universality + a slowly-converging effective
exponent**, not a pinned 0.6407 at these sizes.

## Provenance / novelty

Uses the full untruncated triangle (all H, n≤36) — this supersedes the truncation
caveat in [[nu-exponent]] (which analyzed an H≤18 slice and stopped at n≤19). The
shape collapse and the moment convergence (std/mean, skew of H/⟨H⟩) are new.
Data `results/ns_a36/perheight/`; script `experiments/height_collapse.py`.
Companion to [[hole-free-growth-constant]] (topological) and the diagonal closed
forms (deterministic top of the triangle).


## The tall flank is analytic: large-deviation rate from the grand form (2026-07-14)

The extreme tall tail (H = (1-alpha)n, alpha < 1/2 -- beyond the bulk
scaling window above) is governed by the now-proven diagonal law's grand
form G(y)H(y)^n: by steepest descent,

  (1/n) ln T(n,(1-alpha)n)  ->  psi(alpha) = (1-3 alpha) ln 3
                                 + min_{y>0} [ ln H(y) - alpha ln y ],

the Legendre transform of ln H. Numerically (18-term banked series,
`experiments/flank_saddle.py`): the saddle-point evaluation with Gaussian
prefactor reproduces the exact banked cells T(36, 36-k) to ~1-3% across
k = 3..14 (ratio 1.028 -> 1.009, tightening as the saddle moves away from
the truncation), degrading only at the band edge alpha -> 1/2 (k >= 15),
where the law's onset boundary sits and G(y*) changes sign -- the expected
breakdown. Status: semi-analytic (truncated series); the rate function
itself is exact modulo H's coefficients, all of which are theorems of the
gas up to k=5 and pinned to k=17.

## Refreshed at n=40 (2026-07-31)

Both analyses rerun on the final banked triangle, `results/ns_a40/perheight`
(all H, n≤40). Commands: `python3 experiments/height_collapse.py` and
`python3 experiments/flank_saddle.py` (both now take the per-height directory —
and the saddle script an `n` — as arguments, defaulting to the a(40) data).
Rerunning them on `results/ns_a36/perheight` reproduces every banked number below
to the digits quoted above, so these are extensions, not corrections.

**Collapse keeps tightening, and faster than the n≤36 window suggested:**

| n-window | collapse rel-variance |
|---|---|
| 8,12,16,20 | 0.1905 |
| 16,20,24,28 | 0.1008 |
| 24,28,32,36 | 0.0645 |
| **28,32,36,40** | **0.0384** |

The moments continue their monotone convergence:

| n | std/mean | skew |
|---|---|---|
| 28 | 0.2274 | +0.337 |
| 36 | 0.2261 | +0.351 |
| **40** | **0.2255** | **+0.356** |

So the limit shape's coefficient of variation is ≈0.225 (still drifting down in
the 4th decimal) and the right skew is still creeping up — the shape universality
statement is unchanged and better supported; ⟨H⟩ = 15.170 at n=40.

**mean-based ν_eff continues its slow descent:** 0.7124 (n=12) → 0.6779 (n=36) →
**0.6757 (n=40)**. Four more terms buy ~0.002 — still far above the asymptotic
0.6407, confirming the "pre-asymptotic, large corrections" reading. See
[[nu-exponent]] for the full refreshed slope sequence.

**Tall flank at n=40 — the agreement window widens.** Saddle/exact ratios for
T(40, 40−k):

| k | 3 | 8 | 12 | 15 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|
| saddle/exact | 1.0279 | 1.0103 | **1.0077** | 1.0101 | 1.0187 | 1.0307 | 1.0611 |

At n=36 the ratio bottomed at 1.0091 (k=10–11) and had degraded past 1.02 by
k=15; at n=40 it bottoms lower (**1.0077** at k=12) and stays inside 2% all the
way to **k=17** and inside 3.1% to k=18, breaking down only at k=19 (6.1%) and
failing outright at k=20 = n/2 — one past the law's reach k_max(40)=19 — where
G(y\*) changes sign, the expected band-edge breakdown. So the refreshed statement is: the large-deviation
rate reproduces the exact cells to **~1–3% across k=3..18 (α up to 0.45)** at n=40,
tightening in the middle of the range as n grows, which is what a genuine saddle
asymptotic should do.
