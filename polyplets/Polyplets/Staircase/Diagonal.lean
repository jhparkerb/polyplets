/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Staircase.WalkTop

/-!
# Staircase: the T-diagonal transfer step

The `T_of_d`-transported form of the μ-recursion (`docs/proofs/grand-form.md`): one
transfer step multiplies the *full* diagonal family `T (H + k) H` by the fixed
multiplier series `μ`, exactly, for `H ≥ k + 1` (sharp onset):

`T (H + 1 + k) (H + 1) = ∑_{i ≤ k} μ i · T (H + (k − i)) H`.

The proof rides the top-row peel `TopRow.T_of_d` through `WalkTop.d_staircase`. Both
sides expand by `T_of_d` into a `d`-head plus a `Vt`-weighted interior double
sum. Applying `d_staircase` to the head (at height `H + 1`) and to each interior
`d (k − j) ((H + 1) − ℓ)` (at height `(H − ℓ) + 1`) reveals, after transposing
the fresh μ-index `i` outward across the `(j, ℓ)`-sums, exactly the `T_of_d`
expansion of the right-hand side — one `T_of_d (k − i) H` per `i`. The index
swap is a plain `Finset.sum_comm`/`Finset.sum_comm'` transposition (`μ`'s index
passes through unchanged; the `ℓ`-sum rides along inside `j`) — no convolution
collapse is needed here, unlike `d_staircase`.

The statement was verified on the enumerated table at all 170 in-range instances
(`experiments/staircase_check.py`); `Checks.lean` instantiates it at
`(k, H) = (1, 2)`: `T 4 3 = 3·T 3 2 + (25/3)·T 2 2 = 55`.
-/

namespace Polyplets

/-! ## The staircase -/

/-- **The staircase**: one transfer step multiplies the T-diagonal family by
`μ`, exactly, for `H ≥ k + 1` (sharp onset). In the report's coordinates
(`n = H + k`) this relates diagonal `k` at `n + 1` to diagonals `k − i` at
`n − i`. Proved from `TopRow.T_of_d` through `WalkTop.d_staircase`. -/
theorem T_staircase : ∀ k H : ℕ, k + 1 ≤ H →
    (T (H + 1 + k) (H + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), mu i * (T (H + (k - i)) H : ℚ) := by
  intro k H hk
  -- Step 1: `T_of_d k (H+1)`, cast to ℚ.  The head is `d k (H+1)`; the interior
  -- is a `Vt`-weighted double sum over `d (k−j) ((H+1)−ℓ)`.
  have hLHS : (T (H + 1 + k) (H + 1) : ℚ) = (d k (H + 1) : ℚ) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (Vt ℓ j : ℚ) * (d (k - j) ((H + 1) - ℓ) : ℚ) := by
    exact_mod_cast T_of_d k (H + 1) (by omega)
  -- Step 2: `d_staircase` on the head.
  have hhead : (d k (H + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ) := d_staircase H k hk
  -- Step 3: `d_staircase` on each interior `d`, at height `(H−ℓ)+1`.
  have hint : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (Vt ℓ j : ℚ) * (d (k - j) ((H + 1) - ℓ) : ℚ)) =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) *
        ∑ i ∈ Finset.range ((k - j) + 1), mu i * (d ((k - j) - i) (H - ℓ) : ℚ) := by
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [Finset.mem_Icc] at hj
    refine Finset.sum_congr rfl fun ℓ hℓ => ?_
    rw [Finset.mem_Icc] at hℓ
    rw [show (H + 1) - ℓ = (H - ℓ) + 1 from by omega, d_staircase (H - ℓ) (k - j) (by omega)]
  -- Step 4: expand the RHS's each `T (H+(k−i)) H` by `T_of_d (k−i) H`.
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
      exact_mod_cast T_of_d (k - i) H (by omega)
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

end Polyplets
