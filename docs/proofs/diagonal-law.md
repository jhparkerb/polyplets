# The diagonal law is a theorem (shape, onset, integrality)

2026-07-12. This closes the main conditionality of the whole diagonal thread:
the *shape* of the diagonal law — polynomial × 3-power, degree ≤ k, onset
n ≥ 2k+1, integer-valued P_k — is proved below from an exact combinatorial
decomposition. Machine checks: `experiments/diagonal_law_proof_check.py`
(rational structure, degree bounds tight, exactness for every banked H,
sharp onset, k ≤ 3). Companions: `results/defect-gas.md` (the decomposition
and the enumerated weights), `results/ternary-spine.md` (the downstream
mod-3 structure).

## Statement

**THEOREM.** For every k ≥ 0 there is a polynomial q_k of degree ≤ k with

> T(H+k, H) = q_k(H) · 3^H  for ALL H ≥ k+1,

equivalently, with P_k(n) := 3^(1+2k) q_k(n−k):

> T(n, n−k) = P_k(n) · 3^(n−1−3k)  for all n ≥ 2k+1,

and P_k takes integer values at every integer. (Validity from n = 2k+1 is
proved; that it *fails* at n = 2k is verified on all banked data, k ≤ 17.)

## Setup

Read a height-H king animal row by row (every row nonempty). Rows with one
cell are **walk rows**; maximal runs of rows with ≥ 2 cells are **clusters**.
A cluster's type is its stack of row sizes (s_1, …, s_ℓ), s_i ≥ 2; its
**surplus** is k = Σ(s_i − 1) ≥ ℓ. Weights (all finite — a connected piece
with c cells has spread < c):

- **interior weight** W_c: configurations of the cluster together with the
  single walk cells p below (fixed) and q above (free), connected;
- **edge weights** W^b_c, W^t_c: same with p (resp. q) absent, for clusters
  touching the bottom (resp. top) end; W^t of a type = W^b of its reversal;
- **pure weights** W^p_c: animals that are a single cluster and nothing else.

## Step 1 — separation lemma

*A walk row is a cut: an animal is connected iff each segment between
consecutive walk rows (endpoints included) is connected.*

King adjacency changes the row index by at most 1, so any path from a cell
below row r to a cell above row r contains a cell of row r; if row r is a
walk row, that cell is unique. (⇐) overlapping connected segments share the
walk cells. (⇒) given two cells in a segment [r, r′], take a path in the
animal; every excursion below r or above r′ begins and ends at the unique
walk cell of r (or r′), so excising excursions leaves a path inside the
segment. ∎

## Step 2 — chain identity

Let y mark surplus and z mark rows, F(y,z) = Σ T(n,H) y^(n−H) z^H. By
Step 1 every animal decomposes **uniquely** into: an optional bottom-edge
cluster, an alternating chain cut at its walk rows, and an optional top-edge
cluster — or it is a single pure cluster. Configurations of each piece are
counted relative to the shared walk cell, so choices multiply, and rows and
surplus add (exponents multiply as monomials). Hence the exact identity

> F = E_b · (1 − S)^(−1) · E_t + P,

with S = 3z + Σ_c W_c y^(k_c) z^(ℓ_c+1) (a plain step, or a cluster plus the
walk row above it), E_b = z(1 + Σ_c W^b_c y^(k_c) z^(ℓ_c)),
E_t = 1 + Σ_c W^t_c y^(k_c) z^(ℓ_c), P = Σ_c W^p_c y^(k_c) z^(ℓ_c).
Machine-verified against the banked triangle: 40/40 at (k ≤ 3, H ≤ 10) and
per-order to H = 33 in the checker.

## Step 3 — row bound and finiteness

Each cluster row carries ≥ 1 surplus, so **ℓ_c ≤ k_c**. At surplus level k
the catalogue is the 2^(k−1) compositions of k, all weights finite. This is
the load-bearing triviality (it also drives the mod-3 collapse in
`results/defect-gas.md`).

## Step 4 — rational structure

Extract [y^k] F. Writing σ = S − 3z (every σ-term has y-order ≥ 1),
(1−S)^(−1) = Σ_m σ^m/(1−3z)^(m+1), and [y^k]σ^m needs m ≤ k. So

> [y^k] F = R_k(z) / (1−3z)^(k+1),  R_k ∈ ℤ[z],  **deg R_k ≤ 2k+1**.

Degree count, using ℓ ≤ k on every piece: an E_b factor at surplus k_b has
z-degree ≤ k_b+1; an E_t factor ≤ k_t; a σ^m term at surplus k_m has degree
Σ(ℓ_i+1) ≤ k_m+m, and is multiplied by (1−3z)^(k−m) to reach the common
denominator; the pure part contributes deg ≤ k plus (1−3z)^(k+1). Total
≤ (k_b+1) + (k_m+m) + k_t + (k−m) = 2k+1. (Checker: degrees are exactly
1, 3, 5, 7 for k = 0..3 — the bound is tight.)

## Step 5 — partial fractions ⇒ the law, with sharp-shaped onset

Change basis: R_k(z) = Σ_{j≥0} a_j (1−3z)^j with a_j = coefficients of
R_k((1−w)/3) ∈ 3^(−(2k+1))ℤ. Then

> [y^k] F = Σ_{j<k+1} a_j (1−3z)^(j−k−1) + D(z),

where D = Σ_{j≥k+1} a_j (1−3z)^(j−k−1) is a polynomial of degree
≤ (2k+1) − (k+1) = k. Taking [z^H] for **H ≥ k+1** (past deg D):

> T(H+k, H) = Σ_{i=1}^{k+1} a_{k+1−i} C(H+i−1, i−1) 3^H =: q_k(H) 3^H,

a polynomial in H of degree ≤ k times 3^H, exactly. The onset n ≥ 2k+1 is
H ≥ k+1: it is exactly the reach of the correction polynomial D, whose
degree bound comes from ℓ ≤ k. ∎

## Step 6 — integrality of P_k

P_k(n) = 3^(1+2k) q_k(n−k) = Σ_i 3^(1+2k) a_{k+1−i} C(n−k+i−1, i−1), and
v₃(a_j) ≥ −(2k+1) with binomials integer, so **P_k(n) ∈ ℤ for every integer
n**. Equivalently, P_k's coefficients in the Newton (binomial) basis are
integers — verified numerically at every wired level k = 1..19.

(An earlier note here claimed integer *coefficients in the monomial basis*
as a stronger fact "banked empirically for k ≤ 17". That is FALSE for every
k ≥ 2 and always was: the leading coefficient is 25^k/k!, so P_2's is 625/2.
Measured at all 19 wired levels, no monomial coefficient set is integral.
Retracted AUDIT-2026-07-30 P8. The nearby fact that *is* true, and is what
the engine's storage form relies on, is stated as an open item below:
k!·P_k ∈ ℤ[n]. Nothing downstream needs either — all mod-3^j arguments use
values.)

## Corollary — the grand form G·H^n

**Upgraded 2026-07-21: this corollary is now a standalone THEOREM with a
full proof and sharp onset — `grand-form.md` (machine check:
`experiments/grand_form_check.py`). The paragraph below is the original
sketch.**

D(z) has the single perturbed root z*(y) near 1/3 (unique as a formal
series); the residue resummation of Step 5 across k gives formal series
C(y), μ(y) = 1/z* with A_H(y) := Σ_k T(H+k,H) y^k = C(y)·μ(y)^H per y-order
for H ≥ k+1. Taking logs, the cumulants of A_H are *exactly linear in H* in
the law's range — this is the G(y)H(y)^n grand form used throughout
(`results/diagonal-closed-forms.md`), with H = μ/3 in the law's units, and
it is what the master equation of `results/defect-gas.md` solves. The
Ternary Spine's remaining conditionality therefore reduces to the finitely
many enumerated weights that enter each modulus (5 integers mod 27).

## What remains open (deliberately)

- **Onset sharpness in general**: the theorem proves validity from n = 2k+1;
  failure at n = 2k is a non-cancellation (deg D = k exactly). Verified on
  all banked data AND ab initio for k ≤ 5 from the weight table (deg R_k =
  2k+1 exactly; leading coefficients 1, 4, −80, 1753, −40928, 987355 —
  `experiments/spine_deeper.py`). Not proved for all k; note the natural
  route (rational GF for the top coefficient) fails because the all-pairs
  weight family is not C-finite (refuted at ℓ=16; unbounded gap walk).
- **Denominator exactly k!: is k!·P_k ∈ ℤ[n] for all k?** Observed at every
  wired level k = 1..19 — it is how `orchestrator/sweep.go`'s
  `diagCoeffTable` stores each P_k (integer numerator coefficients over the
  divisor k!), and the k!-divide guard checks the division is exact at every
  evaluation. Not proved. The leading coefficient 25^k/k! shows k! cannot be
  improved; what is open is that no *larger* denominator is ever needed.
  (This replaces a garbled entry that claimed integer coefficients in the
  MONOMIAL basis "observed k ≤ 17" — measured false at every k ≥ 2, since
  25^k/k! is not an integer; retracted AUDIT-2026-07-30 P8. Integer *values*
  are proved above, and the equivalent Newton-basis integrality is verified
  numerically k = 1..19.)
- Closed forms for multi-row cluster weights (open question raised, not a
  gap in this proof).
