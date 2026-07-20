# Lean architecture: the peeling recursion

2026-07-20. Replaces the GF/partial-fractions route of
`docs/proofs/diagonal-law.md` (steps 2/4/5) with an equivalent
Lean-tractable induction. The separation lemma (step 1) and the finite
cluster catalogue (step 3) are unchanged. Same theorem, same onset.

## Why not the doc's route

Two-variable formal power series, term extraction `[y^k]`, and partial
fractions over ℚ[[z]] are all heavy to formalize, and a naive per-arrangement
binomial sum does NOT have the onset termwise (e.g. k=4, four doubled rows at
H=5: polynomial C(-2,4)=5 vs true count 0 — only the SUM has onset k+1).
The recursion below gets the onset by induction with exact bookkeeping,
no cancellation argument needed.

## The recursion

Write c_k(H) := T(H+k, H) (canonical height-H animals, surplus k). Rows with
one cell are walk rows; maximal runs of multi-rows are clusters (type c:
row sizes s_1..s_ℓ ≥ 2, surplus k_c = Σ(s_i−1) ≥ ℓ_c). Weight constants
(cardinalities of finite config sets, values never needed):

- W_c  — interior: cluster + fixed walk cell p below + free walk cell q above,
  connected; counts configs relative to p, including q's offset.
- W^t_c — top-edge: same but nothing above.

**Peeling lemma.** For H ≥ k+2, case-split a surplus-k animal on its top
structure (the three cases are exhaustive and disjoint at this height; a
cluster touching the bottom would force H ≤ ℓ+1 ≤ k+1):

1. top row walk, second-top row walk: removing the top cell leaves a
   height-(H−1) canonical animal (its neighbours below are the UNIQUE
   second-top cell, so removal preserves connectivity — separation lemma);
   the removed cell had exactly 3 offsets. Contributes 3·c_k(H−1).
2. top row walk, cluster below it (with a walk row kept below the cluster):
   peel walk+cluster together. Contributes Σ_c W_c · c_{k−k_c}(H−1−ℓ_c).
3. top rows a cluster (walk row kept below): peel it.
   Contributes Σ_c W^t_c · c_{k−k_c}(H−ℓ_c).

> c_k(H) = 3·c_k(H−1) + Σ_c W_c·c_{k−k_c}(H−1−ℓ_c) + Σ_c W^t_c·c_{k−k_c}(H−ℓ_c)

for H ≥ k+2, sums over the finite catalogue of types with k_c ≤ k (note
k_c ≥ 1, so all c-terms have strictly smaller surplus: the system is
triangular).

Each case is a bijection: (peeled data) × (canonical remainder), with the
remainder re-anchored in x (the one fiddly renormalization pattern, reused
three times). Connectivity of the remainder = separation lemma; exhaustive
disjoint cases = row-profile of the top rows.

## Shape by strong induction on k

Base k=0: c_0(H) = 3^(H−1) (pure walk chain of offsets; direct bijection —
this is also the P_0 production formula).

Step: assume c_j(H) = q_j(H)·3^H (deg q_j ≤ j) for all j < k, H ≥ j+1. For
H ≥ k+2 every c-term on the right is in its valid range: H−1−ℓ_c ≥
k+1−ℓ_c ≥ k+1−k_c = (k−k_c)+1 — exact, no slack. So

> c_k(H) = 3·c_k(H−1) + g(H)·3^H, g ∈ ℚ[H], deg g ≤ max(k−k_c) ≤ k−1.

Telescoping from base H₀ = k+1: c_k(H) = 3^(H−H₀)·c_k(H₀) + Σ_{j=H₀+1}^H
3^(H−j)·g(j)·3^j = 3^H·(const + Σ_{j≤H} g(j)), and a discrete antiderivative
of a deg ≤ k−1 polynomial is deg ≤ k (binomial basis, hockey-stick
Σ_{j} C(j,d) = C(H+1,d+1)). Hence c_k(H) = q_k(H)·3^H for ALL H ≥ k+1 —
the base value is absorbed by the constant term, which is exactly why the
onset is k+1 and not k+2. Degree ≤ k. ∎

Integrality of P_k(n) = 3^(1+2k)·q_k(n−k): by the same induction q_k has
3-power-bounded denominators in the binomial basis (each peel divides by at
most 3^(1+ℓ) per unit of surplus...); do the bookkeeping in the induction —
v₃(denominators) ≤ 1+2k suffices (doc step 6). Verify the constant for small
k by native_decide before trusting the exponent.

Sanity check (k=1, done on paper): catalogue = one type (single doubled row,
ℓ=1). Recursion gives slope(q_1) = W/27 + W^t/9; known P_1 = 25n−45 forces
W + 3·W^t = 25, and direct enumeration of the doubled-row configs gives
W^t = 5, W = 10 — consistent, and 25 = 16+9, 5 = 4+1 are exactly the gadget
multiplicities of docs/proofs/T-n-nm1.md. The Lean build will re-verify via
native_decide weight enumeration where cheap.

## File plan (revised from PLAN.md)

- `Graph.lean` — bridge KingConnected ↔ SimpleGraph.Reachable on the induced
  king graph; all path surgery via mathlib's SimpleGraph.Walk API
  (takeUntil/dropUntil), which is built for exactly this.
- `Separation.lean` — walk row is a cut, both directions.
- `Catalogue.lean` — cluster types at surplus ≤ k (2^(k−1) compositions),
  weight config Finsets, finiteness (spread < cell-count bound, reuse
  canonical_x_le pattern).
- `Peel.lean` — the three peeling bijections + exhaustive/disjoint case split.
- `Shape.lean` — the induction: recurrence ⇒ q_k, onset, degree, integrality.
- `Compute.lean` — computable Tc = T + native_decide (in progress).
- `Pin.lean` — explicit P_k: shape + k+1 points; unconditional where points
  are native_decide-reachable, else conditional on banked values.

## Order of work

Graph → Separation → (Catalogue ∥ Peel case-split) → Peel bijections →
Shape → Pin. The long pole is Peel (three bijections with x-renormalization).
Weight VALUES are never needed for shape; small-k weight enumeration only as
a cross-check and possibly for Pin alternatives.
