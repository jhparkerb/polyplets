# GF-4 — `Polyplets/Grand/Staircase.lean`: the T-diagonal staircase

Read first: `polyplets/GRANDFORM-PLAN.md`; `Polyplets/Grand/MuRec.lean`
(your input `d_mu_rec`); `Polyplets/Peel.lean` lines 1737–1749 (`c_ident`);
`Polyplets/Shape.lean`'s `shape` proof (lines ~238–275) for the house
pattern of consuming `c_ident` in ℚ with the (k−j, H−ℓ) range arithmetic —
your proof reuses exactly that bookkeeping.

## Main theorem

```lean
/-- **The staircase**: one transfer step multiplies the T-diagonal family by
μ, exactly, for H ≥ k+1 (sharp onset). In production coordinates
(n = H + k) this relates diagonal k at n+1 to diagonals k−i at n−i. -/
theorem T_staircase : ∀ k H : ℕ, k + 1 ≤ H →
    (T (H + 1 + k) (H + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), mu i * (T (H + (k - i)) H : ℚ)
```

## Proof sketch

1. `c_ident k (H+1)` (hypothesis `k + 1 ≤ H + 1` ✓), cast to ℚ:
   `(T (H+1+k) (H+1) : ℚ) = d k (H+1) + Σ_{j ∈ Icc 1 k} Σ_{ℓ ∈ Icc 1 j}
   Vt ℓ j · d (k−j) (H+1−ℓ)`.
   Careful with the LHS shape: `c_ident` states `T (H + k) H` at height
   `H+1`, i.e. literally `T ((H+1) + k) (H+1)` — matches.
2. Rewrite `d k (H+1)` by `d_mu_rec H k` (✓ `k+1 ≤ H`).
3. For each (j, ℓ): `H + 1 − ℓ = (H − ℓ) + 1` (`ℓ ≤ j ≤ k ≤ H − 1`, omega);
   rewrite `d (k−j) ((H−ℓ)+1)` by `d_mu_rec (H−ℓ) (k−j)`
   (validity `(k−j) + 1 ≤ H − ℓ`: from `ℓ ≤ j`, omega):
   `= Σ_{i ∈ range (k−j+1)} mu i · d (k−j−i) (H−ℓ)`.
4. Swap the i-sum outward across the (j, ℓ)-sums. Target after swapping:
   `Σ_{i ∈ range (k+1)} mu i · [ d (k−i) H + Σ_{j ∈ Icc 1 (k−i)}
   Σ_{ℓ ∈ Icc 1 j} Vt ℓ j · d ((k−i)−j) (H−ℓ) ]`.
   The index-set identity behind the swap:
   `{(j, i) : 1 ≤ j ≤ k, 0 ≤ i ≤ k−j} ≃ {(i, j) : 0 ≤ i ≤ k, 1 ≤ j ≤ k−i}`
   with `(k−j)−i = (k−i)−j` (omega). Use `Finset.sum_sigma`/
   `Finset.sum_comm'`; note (unlike GF-3) no convolution collapse is needed
   here — μ's index i passes through unchanged. The ℓ-sum rides along
   untouched inside j.
5. The bracket is `c_ident (k−i) H` (validity `(k−i) + 1 ≤ H` ✓), giving
   `(T (H + (k−i)) H : ℚ)`. Assemble. ∎

## Gate (end of file)

```lean
theorem T_staircase_check_k1_H2 :
    (T 4 3 : ℚ) = mu 0 * T 3 2 + mu 1 * T 2 2 := …  -- from T_staircase 1 2
```
with the value check `55 = 3·10 + (25/3)·3` (`T 3 2 = 10` is a native_decide
in the repo — find it via `rg "T 3 2" polyplets/`; `T 2 2 = 3` similarly or
via `T_diag_pow`; `T 4 3 = 55` exists in `Weights.lean`'s checks or follows
from `c_ident_check_k1_H3` + values. If a literal you want is missing, add
it by the cheapest existing route — small `native_decide` on `Tc` mirroring
`Compute.lean`'s pattern is acceptable here).

## Pitfalls

- Do not introduce n-coordinates here; `PinGrand`/`ExpForm` handle that.
  Keep the theorem in (k, H) exactly as displayed — the ℕ-subtraction
  `k − i` (i ≤ k) is safe, and `H + (k − i)` avoids `H + k − i` ambiguity.
- Cast to ℚ once at the top of the proof; all three `c_ident`/`d_mu_rec`
  rewrites should happen ℚ-side (`exact_mod_cast` on entry, as `shape` does).

## Done criteria

Green build, no `sorry`; `#print axioms T_staircase` = standard only
(gates may add `Lean.ofReduceBool`). This is milestone 1 — after this file
the orchestrator merges `lean-grandform` → master.
Commit `lean-gf: Staircase — T-diagonal transfer step`.
