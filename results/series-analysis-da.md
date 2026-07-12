# Differential-approximant series analysis: λ = 7.110(1), θ = −1.000(1)

2026-07-11 (research during the a(22) fleet run). `experiments/series_da.py` on the
exact 36-term sequence a(1..36)=A006770 (a(1..33) from the verified b-file, a(34..36)
the banked frontier values).

## What and why

The paper (§ growth) estimates λ≈7.111 and θ≈−1.02…−1.03 with Δ₁=1/2 by a **ratio
method** — fitting r_n=a(n)/a(n−1) to λ(1+θ/n+c/n^{1+Δ₁}). Ratio methods are biased
by unmodelled corrections (the paper's own two-parameter fit drifted, giving θ≈−0.95;
adding the confluent term moved it to −1.02). This settles λ and θ by an **independent,
more powerful method the paper did not use: differential approximants (DAs)** — fit
the generating function f(x)=Σa_n xⁿ to a first-order ODE
    Q₀(x) f(x) + Q₁(x) f′(x) = P(x)
and read the dominant singularity x_c (a root of Q₁) and its exponent directly.
λ=1/x_c; near x_c, f ~ (1−x/x_c)^{−g} with g = Q₀(x_c)/Q₁′(x_c), and a_n ~ λⁿ n^{g−1},
so **θ = g − 1**. Universality predicts θ = −1 (⇒ g = 0, a *logarithmic* dominant
singularity). DAs are evaluated over a spectrum of polynomial degrees (Σ deg = N−2);
the series is rescaled by λ₀≈7.11 so the linear system is well-conditioned.

## Method validation (calibration on synthetic a_n = round(nθ · λⁿ))

| true (λ, θ) | recovered λ (median) | recovered θ |
|---|---|---|
| (7.11, −1.0) | 7.1100 | −1.000 |
| (7.11, −0.5) | 7.1100 | −0.500 |
| (4.06, −1.0) | 4.0600 | −1.000 |

Exact recovery, including θ = −0.5 (so the method is **not** biased toward θ=−1),
and λ=4.06 recovered even when rescaled by λ₀=7.0 (so it is **not** anchored to the
rescaling). A sign convention in g was fixed against this calibration.

## Result (polyplets, 36 terms)

**λ = 7.1102, θ = −0.9996**, from 42 approximants, and robust:

- **Rescaling-independent:** λ_median = 7.1102 for λ₀ ∈ {6.8, 7.0, 7.11, 7.3}
  (breaks only at λ₀=7.5, where approximants latch onto spurious roots).
- **Converged in N:** λ = 7.1102, θ ≈ −0.9996 already at N=28, unchanged through N=36.

## Reading

- **λ ≈ 7.110(1).** Independent confirmation of the paper's ratio-confluent 7.111;
  the DA sits a hair lower (7.1102 vs 7.1109–7.1111). Both agree at 7.110–7.111;
  the 4th digit is beyond what 36 terms resolve.
- **θ = −1.000(1) — the universal 2D lattice-animal exponent, pinned cleanly.** This
  is *sharper* than the paper's ratio-method −1.02…−1.03, which was pulled off −1 by
  the unmodelled confluent term; the DA absorbs all corrections into the ODE and lands
  on −1.000 to three decimals. Equivalently, the generating function has a **logarithmic
  dominant singularity** at x=1/λ — the θ=−1 signature. This corroborates the paper's
  universality claim (companion to the extent exponent ν≈0.64, [[nu-exponent]], and
  the confluent Δ₁=1/2) by a method that does not assume the correction structure.
- The DA does not independently pin Δ₁ (that needs sub-dominant-singularity analysis);
  it is consistent with the paper's Δ₁=1/2 picture, not an independent test of it.

## Paper note

Candidate strengthening (jasonp's call): the paper reports θ∈[−1.03,−1.02] "consistent
with −1." An independent DA giving θ=−1.000(1) is a cleaner statement of the same
universality — worth a sentence if the growth § is revisited. Not edited here.

## Provenance

`experiments/series_da.py` (calibrated, self-contained). Data: `results/b006770_upload.txt`
(n≤33) + banked a(34..36). Companion asymptotics: [[nu-exponent]] (ν),
[[height-distribution-collapse]] (shape), [[hole-free-growth-constant]] (λ₀).
