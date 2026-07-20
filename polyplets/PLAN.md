# Lean goal plan — all diagonal formulas used in production

2026-07-20. Goal: complete Lean proofs of the diagonal formulas used to compute
T(n,H) values; where full proof is out of reach, prove as much as possible and
state exactly what remains computational input.

## Scope decisions (interview 2026-07-20)

- **Scope: P_0..P_16** — the set `diagonalCell` actually uses in the a(n)
  engine (k=0 is T(n,n)=3^(n-1)).
- **Route: shape theorem + verified points.** Formalize the diagonal-law shape
  theorem (docs/proofs/diagonal-law.md): T(n,n-k) = P_k(n)·3^(n-1-3k) for
  n ≥ 2k+1, deg P_k ≤ k, P_k integer-valued. Then each explicit P_k is pinned
  by k+1 verified values T(H+k,H), H = k+1..2k+1. `native_decide` approved.
- **Branch rebased onto master** (was P13-era); mathlib via `lake exe cache
  get`, never build mathlib from source.

## Reach assessment (honest, up front)

| k | route | expectation |
|---|-------|-------------|
| 0 | direct (single-cluster-free chain, 3^(H-1) offsets... actually pure walk) | unconditional |
| 1 | shape + 2 points (T(3,2)=10, T(4,3)=55) or the existing direct gadget proof | unconditional |
| 2..~3 | shape + brute-force `native_decide` points | unconditional if enumeration fits |
| ~4..~8 | shape + points needs a **verified column DP** (brute force dies combinatorially); weight-route alternative also explodes | unconditional only if the verified DP lands and native_decide carries it |
| ~9..16 | onset points reach H=2k+1 up to 33 — production-scale compute (C++ engine hours at H=19); weight enumeration measured dead (~20x/k, k=17 ≈ 10^17 s) | **conditional**: Lean theorem "shape + (banked onset values) ⇒ P_k", banked values as explicit hypotheses |

The conditional tier is not a cop-out: the shape theorem reduces each P_k from
an infinite claim to k+1 finite integers, and those integers are exactly the
banked, two-algorithm-validated triangle entries. The residual trust is the
same enumeration trust the project already carries, made precise as
hypotheses.

## Architecture

Formalize the diagonal-law proof **without two-variable formal power series**:
for fixed k the chain identity becomes a finite sum. A canonical height-H
animal with n = H+k cells has all rows occupied and total surplus k, so rows
with ≥ 2 cells number ≤ k and group into maximal **clusters** (types = stacks
of row sizes, surplus k_c = Σ(s_i−1), rows ℓ_c ≤ k_c). The decomposition:

1. **Separation lemma** (walk row = cut): connectivity ⟺ each inter-walk-row
   segment connected. Both directions; the reverse direction subsumes the old
   k=1 step (c-rev).
2. **Chain bijection**: canonical animal ⟷ (optional bottom-edge cluster,
   alternating walk/cluster chain, optional top-edge cluster | pure cluster),
   configurations counted relative to the shared walk cells; inter-row walk
   offsets are a free 3-chain (generalizes the old step (e) gadget argument).
3. **Counting identity**: T(H+k,H) = Σ over arrangements (cluster multiset
   from the finite surplus-≤k catalogue × placement) of
   (Π weights) · (placement binomial in H, degree ≤ k) · 3^(free walk steps).
   Valid exactly for H ≥ k+1 (onset = every arrangement fits or its binomial
   vanishes).
4. **Shape**: therefore T(H+k,H) = q_k(H)·3^H with deg q_k ≤ k, and
   P_k(n) = 3^(1+2k) q_k(n−k) is integer-valued (binomial basis).
5. **Pinning**: shape + verified points ⇒ the explicit production polynomial,
   per k (unconditional tier), or with banked-value hypotheses (conditional
   tier).

Weights only need **finiteness** for shape (spread < cell count); their values
are never needed unless we chase the weight route (we don't — measured dead).

## Files

- `Defs.lean`, `Finite.lean`, `RowProfile.lean` — existing, green.
- `Compute.lean` (new) — computable `Tc n H`, `Tc = T`, native_decide
  validation against `results/triangle.txt` values.
- `Separation.lean` (new) — separation lemma.
- `Chain.lean` (new) — cluster catalogue, chain bijection, counting identity.
- `Shape.lean` (new) — shape theorem + integrality.
- `Pin.lean` (new) — explicit P_k theorems, unconditional and conditional.
- `Diagonal.lean` — existing k=1/k=2 targets; will be re-derived from
  Shape+Pin; direct gadget route (steps c-rev/d/e) optional after that.

## Validation policy

Every new counting definition gets a native_decide check against banked
triangle values before use (anti-confabulation). The banked values used as
conditional hypotheses are quoted verbatim from `results/triangle.txt`
(provenance: results/ns_a36/, two-algorithm confirmed range noted per value).

## Execution

Task DAG in session task list: plan(1) → compute(2) ∥ separation(3) →
chain(4) → shape(5) → pin(6) + conditional(7); k=1 direct completion(8)
optional. Long pole: the chain bijection (4). Agents used for proof grinding;
lake builds stay within the 10-core gympie budget (mathlib always from cache).
