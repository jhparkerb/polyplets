# Converse sweep: exact counterexample hunts for the open universal claims

2026-07-31 (jasonp's move: for each believed-but-unproved universal statement,
try to *refute* it — a refutation needs one exact witness from banked data,
which is a finite, certificate-grade check, unlike the proofs themselves).
Script: `experiments/converse_sweep.py` (<5 s, pure exact arithmetic; P_k
re-pinned by Lagrange interpolation from `results/triangle.txt` with a
holdout assert on every other in-regime banked cell). Companion result, same
session: the ratio sequence a(n)/a(n−1) is provably NOT log-convex
(`results/open-conjectures.md` C2 entry; Lean witness `ratio_not_logConvex`).

## 1. Onset sharpness: converse DEAD through k = 13 (was: tested k ≤ 5)

Sharpness says the diagonal law T(n,n−k) = P_k(n)·3^(n−1−3k) fails at n = 2k
for every k. The converse (an accidental extension) is refuted in the
strongest possible way: for **every k = 1..13**, the formula value at n = 2k
is **not even an integer** — P_k(2k) is not divisible by 3^(k+1) — so it
cannot equal the banked T(2k,k) or any count. Sharpness evidence upgraded
from k ≤ 5 (ab initio) to k ≤ 13 (exact, banked-data-complete: k = 13 is the
interpolation ceiling at n ≤ 40).

## 2. "Denominator exactly k!": REFUTED for every k ≥ 5 — the 5-adic slack

The load-bearing, guarded fact k!·P_k ∈ ℤ[n] **stands** (all wired levels).
The stronger "exactly k!" (minimality) is **false from k = 5 on**: the true
minimal common denominator D_k of P_k's monomial coefficients satisfies

| k | 1–4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|
| k!/D_k | 1 | 5 | 5 | 5 | 5 | 5 | 5 | **25** | 5 | 5 |

Only powers of **5** drop out — the 2- and 3-adic content of k! is fully
needed, but the 5-adic content is partly cancelled, k = 11 doubly so. The
likely mechanism is the defect-species constant 25 = 5²: the leading
coefficient 25^k/k! carries v₅ = 2k in its numerator, and the lower
coefficients evidently inherit enough 5s to free part of v₅(k!). A closed law
for v₅(D_k) is a new (small) open question; the irregular k = 11 entry says
it is not simply v₅(k!) − 1.

Action: the open-items phrasing "denominator exactly k!" (HANDOFF) is
corrected to "k!·P_k ∈ ℤ[n] (proved integer-valued ⇒ divisibility; minimality
false — see results/converse-sweep.md)".

## 3. Companion sequences: the "past small n" hedges are now exact

Log-convexity (converse = exhibit one violating triple, done where present):

- **A006770 (fixed): no violation in 40 terms** — C2 survives its converse.
- A030222 (free): violated at n = 4 only. A030233 (one-sided): n = 4 only.
- A030235 (asymmetric): n = 3, 4, 6. A194596: n = 2, 4.
- A030234 (bilateral): violated at **every even n** through 30 (the known
  parity effect — the converse of "bilateral is log-convex" was already
  provable and now has its exact witness list).

Ratio-sequence log-convexity (the r(n) question, applied family-wide): NOT
log-convex for every member; the fixed count is log-concave at literally
every index, while free/one-sided/asymmetric/A194596 show an **even-n-only
violation pattern up to n ≈ 10–12 before becoming log-concave at every n** —
the bilateral parity signature leaking into the ratio domain of sequences
that are NOT parity-broken in level form. Unexplained; noted as a
observation, not a claim.

## Not quickly testable (recorded so the sweep is honest)

MoatBound / peeling lemma / multi-hole master inequality (brute-force
extension past n = 9 — compute-bounded, scripts exist); ψ₉/ψ₁₀ irreducibility
(a single prime with irreducible reduction would PROVE it — bounded attempt,
needs the atom polynomials extracted); N_k(±1) = (±2)^k, dm onset and
multiplicity split, mod-27 bonus depth, θ = −1 (no new data available at
project close).
