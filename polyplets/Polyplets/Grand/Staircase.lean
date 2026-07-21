/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.MuRec

/-!
# Staircase: the T-diagonal transfer step

The `c_ident`-transported form of the μ-recursion (`GRANDFORM-PLAN.md`): one
transfer step multiplies the *full* diagonal family `T (H + k) H` by the fixed
multiplier series `μ`, exactly, for `H ≥ k + 1` (sharp onset):

`T (H + 1 + k) (H + 1) = ∑_{i ≤ k} μ i · T (H + (k − i)) H`.

The proof rides the top-row peel `Peel.c_ident` through `MuRec.d_mu_rec`. Both
sides expand by `c_ident` into a `d`-head plus a `Vt`-weighted interior double
sum. Applying `d_mu_rec` to the head (at height `H + 1`) and to each interior
`d (k − j) ((H + 1) − ℓ)` (at height `(H − ℓ) + 1`) reveals, after transposing
the fresh μ-index `i` outward across the `(j, ℓ)`-sums, exactly the `c_ident`
expansion of the right-hand side — one `c_ident (k − i) H` per `i`. The index
swap is a plain `Finset.sum_comm`/`Finset.sum_comm'` transposition (`μ`'s index
passes through unchanged; the `ℓ`-sum rides along inside `j`) — no convolution
collapse is needed here, unlike GF-3.

The statement was verified on banked data at all 170 in-range instances
(`experiments/staircase_check.py`); the numeric gate reproduces
`T 4 3 = 3·T 3 2 + (25/3)·T 2 2 = 55`.
-/

namespace Polyplets

/-! ## The staircase -/

/-- **The staircase**: one transfer step multiplies the T-diagonal family by
`μ`, exactly, for `H ≥ k + 1` (sharp onset). In production coordinates
(`n = H + k`) this relates diagonal `k` at `n + 1` to diagonals `k − i` at
`n − i`. Proved from `Peel.c_ident` through `MuRec.d_mu_rec`. -/
theorem T_staircase : ∀ k H : ℕ, k + 1 ≤ H →
    (T (H + 1 + k) (H + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), mu i * (T (H + (k - i)) H : ℚ) := by
  intro k H hk
  -- Step 1: `c_ident k (H+1)`, cast to ℚ.  The head is `d k (H+1)`; the interior
  -- is a `Vt`-weighted double sum over `d (k−j) ((H+1)−ℓ)`.
  have hLHS : (T (H + 1 + k) (H + 1) : ℚ) = (d k (H + 1) : ℚ) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (Vt ℓ j : ℚ) * (d (k - j) ((H + 1) - ℓ) : ℚ) := by
    exact_mod_cast c_ident k (H + 1) (by omega)
  -- Step 2: `d_mu_rec` on the head.
  have hhead : (d k (H + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ) := d_mu_rec H k hk
  -- Step 3: `d_mu_rec` on each interior `d`, at height `(H−ℓ)+1`.
  have hint : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (Vt ℓ j : ℚ) * (d (k - j) ((H + 1) - ℓ) : ℚ)) =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) *
        ∑ i ∈ Finset.range ((k - j) + 1), mu i * (d ((k - j) - i) (H - ℓ) : ℚ) := by
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [Finset.mem_Icc] at hj
    refine Finset.sum_congr rfl fun ℓ hℓ => ?_
    rw [Finset.mem_Icc] at hℓ
    rw [show (H + 1) - ℓ = (H - ℓ) + 1 from by omega, d_mu_rec (H - ℓ) (k - j) (by omega)]
  -- Step 4: expand the RHS's each `T (H+(k−i)) H` by `c_ident (k−i) H`.
  have hRHStot : (∑ i ∈ Finset.range (k + 1), mu i * (T (H + (k - i)) H : ℚ)) =
      (∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ)) +
        ∑ i ∈ Finset.range (k + 1), mu i *
          (∑ j ∈ Finset.Icc 1 (k - i), ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) * (d ((k - i) - j) (H - ℓ) : ℚ)) := by
    rw [← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    have hc : (T (H + (k - i)) H : ℚ) = (d (k - i) H : ℚ) +
        ∑ j ∈ Finset.Icc 1 (k - i), ∑ ℓ ∈ Finset.Icc 1 j,
          (Vt ℓ j : ℚ) * (d ((k - i) - j) (H - ℓ) : ℚ) := by
      exact_mod_cast c_ident (k - i) H (by omega)
    rw [hc, mul_add]
  -- Step 5: the two interiors agree by transposing the μ-index `i` outward.
  have hinterior : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) *
        ∑ i ∈ Finset.range ((k - j) + 1), mu i * (d ((k - j) - i) (H - ℓ) : ℚ)) =
      ∑ i ∈ Finset.range (k + 1), mu i *
        (∑ j ∈ Finset.Icc 1 (k - i), ∑ ℓ ∈ Finset.Icc 1 j,
          (Vt ℓ j : ℚ) * (d ((k - i) - j) (H - ℓ) : ℚ)) := by
    -- 5a: pull `Vt ℓ j` into the `i`-sum.
    have h1 : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) *
          ∑ i ∈ Finset.range ((k - j) + 1), mu i * (d ((k - j) - i) (H - ℓ) : ℚ)) =
        ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
          ∑ i ∈ Finset.range ((k - j) + 1),
            (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ)) :=
      Finset.sum_congr rfl fun j _ => Finset.sum_congr rfl fun ℓ _ => Finset.mul_sum _ _ _
    -- 5b: swap the (independent) `ℓ`- and `i`-sums under `j`.
    have h2 : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
            ∑ i ∈ Finset.range ((k - j) + 1),
              (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ))) =
        ∑ j ∈ Finset.Icc 1 k, ∑ i ∈ Finset.range ((k - j) + 1),
          ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ)) :=
      Finset.sum_congr rfl fun j _ => Finset.sum_comm
    -- 5c: swap the `j`- and `i`-sums (joint predicate `1 ≤ j`, `i + j ≤ k`).
    have h3 : (∑ j ∈ Finset.Icc 1 k, ∑ i ∈ Finset.range ((k - j) + 1),
            ∑ ℓ ∈ Finset.Icc 1 j,
              (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ))) =
        ∑ i ∈ Finset.range (k + 1), ∑ j ∈ Finset.Icc 1 (k - i),
          ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ)) := by
      apply Finset.sum_comm'
      intro j i
      simp only [Finset.mem_Icc, Finset.mem_range]
      omega
    -- 5d: fix the `d`-index (`(k−j)−i = (k−i)−j`) and re-order factors.
    have h4 : (∑ i ∈ Finset.range (k + 1), ∑ j ∈ Finset.Icc 1 (k - i),
            ∑ ℓ ∈ Finset.Icc 1 j,
              (Vt ℓ j : ℚ) * (mu i * (d ((k - j) - i) (H - ℓ) : ℚ))) =
        ∑ i ∈ Finset.range (k + 1), mu i *
          (∑ j ∈ Finset.Icc 1 (k - i), ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) * (d ((k - i) - j) (H - ℓ) : ℚ)) := by
      refine Finset.sum_congr rfl fun i _ => ?_
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Finset.mem_Icc] at hj
      rw [Finset.mul_sum]
      refine Finset.sum_congr rfl fun ℓ hℓ => ?_
      rw [Finset.mem_Icc] at hℓ
      rw [show (k - j) - i = (k - i) - j from by omega]
      ring
    rw [h1, h2, h3, h4]
  -- Assemble: heads cancel; interiors agree by `hinterior`.
  rw [hLHS, hhead, hint, hRHStot, hinterior]

/-! ## Numeric gate -/

/-- **Gate (k, H) = (1, 2).** The staircase smoke test:
`T 4 3 = μ₀·T 3 2 + μ₁·T 2 2`, instantiating `T_staircase 1 2`. -/
theorem T_staircase_check_k1_H2 :
    (T 4 3 : ℚ) = mu 0 * T 3 2 + mu 1 * T 2 2 := by
  have h := T_staircase 1 2 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add,
    Nat.sub_zero, Nat.sub_self] using h

/-- The `(1, 2)` gate evaluates: `55 = 3·10 + (25/3)·3` from `T 3 2 = 10`,
`T 2 2 = 3`, `μ₀ = 3`, `μ₁ = 25/3` (verified arithmetic). -/
theorem T_staircase_value_check :
    mu 0 * (T 3 2 : ℚ) + mu 1 * (T 2 2 : ℚ) = 55 := by
  rw [mu_zero, mu_one, T_3_2, T_2_2]; norm_num

/-! ## Axiom sanity check -/

section Sanity

#print axioms T_staircase

end Sanity

end Polyplets
