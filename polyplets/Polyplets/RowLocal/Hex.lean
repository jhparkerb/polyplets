/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.RowLocal.Compute

/-!
# The hexagonal lattice: polyhexes

`D = {-1, 0}`, so `b = |D| = 2`. In the brick (sheared-square) coordinates used
throughout, the six neighbors of a cell are

```
(±1, 0),  (0, ±1),  (-1, +1),  (+1, -1)
```

(`adj_hex`) — the standard hexagonal lattice. The universal diagonal law
therefore gives `T(n, n-k) = P_k(n) · 2^(n-1-3k)` for `n ≥ 2k+1`: **the
by-height diagonals of fixed polyhexes are a polynomial times `2^n`.**

## What is determined here

* `isDiagonalPoly_hexP1` / `hex_T_sub_one` : `P₁(n) = 9n − 15`, i.e.
  `T(n, n−1) = (9n − 15)·2^(n−4)` for `n ≥ 3` (paper instance table, density
  `9 = 3²`), unconditionally: the kernel decides both onset cells,
  `T(3,2) = 6` and `T(4,3) = 21`, from the generic enumerator `Tc` (the second
  at 5.7 GB and 12 s, measured 2026-10-12).
* `Checks.lean`: the row sum of the computed height triangle at `n = 3`
  reproduces A001207 (fixed polyhexes) `11` — the same cross-family check as
  for the square lattice against A001168.
-/

namespace Polyplets.RowLocal

open Polynomial

/-! ## The lattice -/

/-- **The hexagonal lattice** in brick coordinates: up-offsets `{-1, 0}`. -/
def hexLattice : Lattice where
  D := {-1, 0}
  hD := ⟨0, by decide⟩

/-- Membership in the hexagonal up-offset set. -/
lemma mem_hexLattice_D {t : ℤ} : t ∈ hexLattice.D ↔ (t = -1 ∨ t = 0) := by
  change t ∈ ({-1, 0} : Finset ℤ) ↔ _
  simp only [Finset.mem_insert, Finset.mem_singleton]

/-- **The hexagonal drift count is 2.** -/
@[simp] lemma b_hex : hexLattice.b = 2 := by decide

/-- The hexagonal lattice has reach `1`: no step skips a column. -/
lemma hex_reach_le : hexLattice.reach ≤ 1 :=
  reach_le_one _ (by decide)

/-- **The instance bridge**: row-local adjacency at the hexagonal lattice is
adjacency to one of the six hexagonal neighbors. -/
theorem adj_hex {p q : ℤ × ℤ} :
    Adj hexLattice p q ↔ (q.1 - p.1, q.2 - p.2) ∈
      ({(1, 0), (-1, 0), (0, 1), (-1, 1), (0, -1), (1, -1)} : Finset (ℤ × ℤ)) := by
  have hne : (p ≠ q) ↔ ¬ (p.1 = q.1 ∧ p.2 = q.2) := not_congr Prod.ext_iff
  rw [Adj, hne]
  simp only [mem_hexLattice_D, Finset.mem_insert, Finset.mem_singleton, Prod.mk.injEq,
    abs_eq (by norm_num : (0 : ℤ) ≤ 1)]
  omega

/-! ## The two onset cells -/

/-- `T(3,2) = 6`: of the 11 fixed 3-cell polyhexes, one is flat and four are
strict staircases, leaving six of height exactly 2. -/
theorem T_hex_3_2 : T hexLattice 3 2 = 6 := by
  rw [← Tc_eq_T_of_reach_le_one hex_reach_le]; decide +kernel

/-- `T(4,3) = 21`. -/
theorem T_hex_4_3 : T hexLattice 4 3 = 21 := by
  rw [← Tc_eq_T_of_reach_le_one hex_reach_le]; decide +kernel

/-! ## `P₁` -/

/-- The hexagonal lattice's level-1 diagonal polynomial `P₁ = 9X − 15`. -/
noncomputable def hexP1 : Polynomial ℚ := C 9 * X - C 15

/-- `P₁` has degree `≤ 1`. -/
lemma hexP1_natDegree_le : hexP1.natDegree ≤ 1 := by
  refine le_trans (natDegree_sub_le _ _) (max_le ?_ ?_)
  · exact le_trans (natDegree_C_mul_le _ _) (by simp)
  · simp

/-- `P₁` evaluated. -/
lemma hexP1_eval (x : ℚ) : hexP1.eval x = 9 * x - 15 := by simp [hexP1]

/-- `P₁` at the first onset point: `P₁(3) = T(3,2) · b^1 = 12`. -/
lemma hexP1_eval_three : hexP1.eval (3 : ℚ) = ((T hexLattice 3 2 * hexLattice.b ^ 1 : ℕ) : ℚ) := by
  rw [hexP1_eval, T_hex_3_2, b_hex]; norm_num

/-- `P₁` at the second onset point: `P₁(4) = T(4,3) · b^0 = 21`, given the cell. -/
lemma hexP1_eval_four :
    hexP1.eval (4 : ℚ) = ((T hexLattice 4 3 * hexLattice.b ^ 0 : ℕ) : ℚ) := by
  rw [hexP1_eval, T_hex_4_3, b_hex]; norm_num

/-- **The hexagonal `P₁`.** -/
theorem isDiagonalPoly_hexP1 : IsDiagonalPoly hexLattice 1 hexP1 :=
  isDiagonalPoly_one_of_eval hexLattice hexP1 hexP1_natDegree_le hexP1_eval_three
    hexP1_eval_four

/-- **The hexagonal `P₁`, human form**: the number of fixed polyhexes with `n`
cells and bounding-box height exactly `n − 1` is `(9n − 15)·2^(n−4)`, for every
`n ≥ 3`. -/
theorem hex_T_sub_one (n : ℕ) (hn : 3 ≤ n) :
    (T hexLattice n (n - 1) : ℚ) = (9 * (n : ℚ) - 15) * (2 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := isDiagonalPoly_hexP1 n (by omega)
  simp only [topRowRecursion_T, topRowRecursion_b, b_hex] at h
  norm_num [hexP1_eval] at h ⊢
  rw [h]
  ring_nf

end Polyplets.RowLocal
