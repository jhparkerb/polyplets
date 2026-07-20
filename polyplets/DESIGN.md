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

## The recursion (v2 — corrected 2026-07-20, same day)

v1 ran the recursion on c_k(H) := T(H+k,H) directly; that DOUBLE-COUNTS:
peeling always produces a remainder whose top row is a walk row, so the
recursion closes over walk-top animals only. Corrected system, verified on
paper at T(4,3) = 15+25+15 = 55 ✓:

Primary object: **d_k(H)** := # canonical height-H surplus-k animals whose
TOP row is a walk row (one cell). Rows with one cell are walk rows; maximal
runs of multi-rows are clusters. Weights are aggregated by (rows ℓ, surplus
j) only — NO per-type list catalogue is needed:

- V(ℓ,j)  — interior weight: configs of a cluster spanning ℓ rows with
  surplus j (each row ≥ 2 cells), plus fixed walk cell p=(0,0) directly
  below, plus a free walk cell q directly above, all connected; counted
  relative to p. Finite (x-spread < total cell count).
- Vᵗ(ℓ,j) — top-edge weight: same without q.

**d-recursion** (peel the top of a walk-top animal; exhaustive disjoint split
on the second-top row; valid for H ≥ k+2, where clusters cannot touch the
bottom since ℓ ≤ j ≤ k ≤ H−2):

1. second-top row walk: peel the top cell — 3 offsets relative to the unique
   second-top cell; remainder is walk-top, height H−1, same surplus
   (connectivity of the remainder: separation lemma; the removed cell's only
   S-neighbours are in the second-top row, which is a single cell).
2. second-top row multi: peel top cell + the maximal cluster [b, H−2] under
   it, down to the walk row b−1; the peeled data is exactly a V-config
   (p = row-(b−1) cell, q = top cell); remainder is walk-top, height H−1−ℓ.

> d_k(H) = 3·d_k(H−1) + Σ_{j=1..k} Σ_{ℓ=1..j} V(ℓ,j)·d_{k−j}(H−1−ℓ),  H ≥ k+2

**c-identity** (split all animals by top row walk/multi; multi-top = top-edge
cluster capping a walk-top remainder; valid for H ≥ k+1 — a pure cluster
would need surplus ≥ H > k, and remainder height H−ℓ ≥ 1 holds):

> c_k(H) = d_k(H) + Σ_{j=1..k} Σ_{ℓ=1..j} Vᵗ(ℓ,j)·d_{k−j}(H−ℓ),  H ≥ k+1

Both sums are triangular (j ≥ 1 ⇒ strictly smaller surplus on the right).
Each case is a bijection: (peeled data) × (walk-top remainder), remainder
re-anchored in x (one renormalization pattern, reused three times: the
recorded offsets are shift-invariant, so erase/shift and add/shift invert).
Boundary absorption: at low H, walk-top animals over bottom-edge clusters
(e.g. profile (2,1) at H=2) are simply members of d — no extra classes; the
d-recursion is only ever INVOKED at H ≥ k+2 and the c-identity at H ≥ k+1,
where the case analyses are exact.

## Shape by strong induction on k

Base k=0: d_0(H) = c_0(H) = 3^(H−1) for H ≥ 1 (free walk chain of offsets —
also the P_0 production formula).

Step: assume d_j(H) = δ_j(H)·3^H (deg δ_j ≤ j) for all j < k and all
H ≥ j+1. In the d-recursion at H ≥ k+2 every term is in range:
H−1−ℓ ≥ k+1−ℓ ≥ k+1−j = (k−j)+1 — exact, no slack. So

> d_k(H) = 3·d_k(H−1) + g(H)·3^H, g ∈ ℚ[H], deg g ≤ k−1.

Telescoping from base H₀ = k+1: d_k(H) = 3^H·(3^(−H₀)·d_k(H₀) + Σ_{j=H₀+1}^H
g(j)); a discrete antiderivative of a deg ≤ k−1 polynomial is deg ≤ k
(binomial basis, hockey stick `Nat.sum_Icc_choose`). Hence d_k(H) =
δ_k(H)·3^H for ALL H ≥ k+1 — the base value is absorbed by the constant
term; that is exactly why the onset is k+1, not k+2. Then the c-identity
gives, for H ≥ k+1 (every d-term again exactly in range,
H−ℓ ≥ k+1−j = (k−j)+1):

> q_k(H) = δ_k(H) + Σ_{j,ℓ} Vᵗ(ℓ,j)·δ_{k−j}(H−ℓ)·3^(−ℓ), deg ≤ k. ∎

Integrality of P_k(n) = 3^(1+2k)·q_k(n−k): denominator bookkeeping through
the same induction (each step divides by bounded 3-powers); target
v₃(denom) ≤ 1+2k (doc step 6). Verify small-k constants by native_decide
before trusting the exponent.

Sanity check (k=1, done on paper, all three classes): V(1,1) = 25 (direct
enumeration: 16 adjacent-pair configs + 9 gap-2 configs — exactly the 16+9
gadgets of docs/proofs/T-n-nm1.md), Vᵗ(1,1) = 5 (= 4+1 gadgets). d_1(2) = 5;
d-recursion gives d_1(H) = (25H−35)/27·3^H (d_1(3) = 40 = 15+25 ✓);
c-identity gives q_1(H) = (25H−20)/27, i.e. T(H+1,H) = (25H−20)·3^(H−3) =
P_1(n)·3^(n−4) with P_1(n) = 25n−45 ✓, and T(4,3) = 55 ✓, T(3,2) = 10 ✓
(onset H = k+1 = 2 included).

## File plan (revised from PLAN.md)

- `Graph.lean` — bridge KingConnected ↔ SimpleGraph.Reachable on the induced
  king graph; all path surgery via mathlib's SimpleGraph.Walk API
  (takeUntil/dropUntil), which is built for exactly this.
- `Separation.lean` — walk row is a cut, both directions.
- `Weights.lean` — walk-top set D k H, config sets for V(ℓ,j)/Vᵗ(ℓ,j),
  finiteness (spread < cell-count bound, reuse canonical_x_le pattern). No
  list catalogue: weights aggregate by (ℓ, j) only.
- `Peel.lean` — the three peeling bijections + exhaustive/disjoint case
  split ⇒ the d-recursion (H ≥ k+2) and c-identity (H ≥ k+1).
- `Shape.lean` — the induction: recurrence ⇒ δ_k then q_k, onset, degree,
  integrality.
- `Compute.lean` — computable Tc = T + native_decide (in progress).
- `Pin.lean` — explicit P_k: shape + k+1 points; unconditional where points
  are native_decide-reachable, else conditional on banked values.

## Order of work

Graph → Separation → (Catalogue ∥ Peel case-split) → Peel bijections →
Shape → Pin. The long pole is Peel (three bijections with x-renormalization).
Weight VALUES are never needed for shape; small-k weight enumeration only as
a cross-check and possibly for Pin alternatives.
