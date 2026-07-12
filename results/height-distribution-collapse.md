# The polyplet height distribution has a universal limit shape (data collapse)

2026-07-11 (research during the a(22) fleet run). `experiments/height_collapse.py`
on the FULL exact height triangle `results/ns_a36/perheight/hH.out` (all H=1..36,
n≤36; row sums verified == a(n) against the b-file for n≤33, chain-consistent to 36).

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
