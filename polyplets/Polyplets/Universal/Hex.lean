/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Polyplets.Universal.Compute

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

## What is pinned here

* `hex_P1_pinned` / `hex_P1_closed` : `P₁(n) = 9n − 15`, i.e.
  `T(n, n−1) = (9n − 15)·2^(n−4)` for `n ≥ 3` (paper instance table, density
  `9 = 3²`), given the second anchor cell `T(4,3) = 21` as a hypothesis. The
  first anchor `T(3,2) = 6` the kernel decides from the generic enumerator;
  `T(4,3)` needs more than 8 GB in the kernel (measured 2026-10-12), so it
  enters as the hypothesis `hex_P1_pinned` and `hex_P1_closed` carry.
* `hex_rowSum_3` : the row sum of the computed height triangle at `n = 3`
  reproduces A001207 (fixed polyhexes) `11` — the same cross-family check as
  `Universal/Square.lean` runs against A001168.
-/

namespace Polyplets.Universal

open Polynomial

/-! ## The lattice -/

/-- **The hexagonal lattice** in brick coordinates: up-offsets `{-1, 0}`. -/
def hexLattice : RowLocal where
  D := {-1, 0}
  hD := ⟨0, by decide⟩

/-- Membership in the hexagonal up-offset set. -/
lemma mem_hexLattice_D {t : ℤ} : t ∈ hexLattice.D ↔ (t = -1 ∨ t = 0) := by
  change t ∈ ({-1, 0} : Finset ℤ) ↔ _
  simp only [Finset.mem_insert, Finset.mem_singleton]

/-- **The hexagonal drift count is 2.** -/
@[simp] lemma b_hex : hexLattice.b = 2 := by decide

/-- The hexagonal lattice has reach `1`: no step skips a column. -/
lemma M_hex_le : hexLattice.M ≤ 1 :=
  M_le_one _ (by decide)

/-- **The instance anchor**: row-local adjacency at the hexagonal lattice is
adjacency to one of the six hexagonal neighbors. -/
theorem adj_hex {p q : ℤ × ℤ} :
    Adj hexLattice p q ↔ (q.1 - p.1, q.2 - p.2) ∈
      ({(1, 0), (-1, 0), (0, 1), (-1, 1), (0, -1), (1, -1)} : Finset (ℤ × ℤ)) := by
  have hne : (p ≠ q) ↔ ¬ (p.1 = q.1 ∧ p.2 = q.2) := not_congr Prod.ext_iff
  rw [Adj, hne]
  simp only [mem_hexLattice_D, Finset.mem_insert, Finset.mem_singleton, Prod.mk.injEq,
    abs_eq (by norm_num : (0 : ℤ) ≤ 1)]
  omega

/-! ## The first anchor cell -/

/-- `T(3,2) = 6`: of the 11 fixed 3-cell polyhexes, one is flat and four are
strict staircases, leaving six of height exactly 2. -/
theorem T_hex_3_2 : T hexLattice 3 2 = 6 := by
  rw [← Tc_eq_T_of_M_le_one M_hex_le]; decide +kernel

/-! ## Cross-family check: A001207 -/

/-- A001207 at `n = 3`: `1 + 6 + 4 = 11` fixed 3-cell polyhexes. -/
theorem hex_rowSum_3 : rowSum hexLattice 3 3 = 11 := by decide +kernel

/-! ## Pinning `P₁` -/

/-- The hexagonal lattice's level-1 production polynomial `P₁ = 9X − 15`. -/
noncomputable def hexP1 : Polynomial ℚ := C 9 * X - C 15

/-- `P₁` has degree `≤ 1`. -/
lemma hexP1_deg : hexP1.natDegree ≤ 1 := by
  refine le_trans (natDegree_sub_le _ _) (max_le ?_ ?_)
  · exact le_trans (natDegree_C_mul_le _ _) (by simp)
  · simp

/-- `P₁` evaluated. -/
lemma hexP1_eval (x : ℚ) : hexP1.eval x = 9 * x - 15 := by simp [hexP1]

/-- Guard at the first pin point: `P₁(3) = T(3,2) · b^1 = 12`. -/
lemma hex_guard_3 : hexP1.eval (3 : ℚ) = ((T hexLattice 3 2 * hexLattice.b ^ 1 : ℕ) : ℚ) := by
  rw [hexP1_eval, T_hex_3_2, b_hex]; norm_num

/-- Guard at the second pin point: `P₁(4) = T(4,3) · b^0 = 21`, given the cell. -/
lemma hex_guard_4 (h43 : T hexLattice 4 3 = 21) :
    hexP1.eval (4 : ℚ) = ((T hexLattice 4 3 * hexLattice.b ^ 0 : ℕ) : ℚ) := by
  rw [hexP1_eval, h43, b_hex]; norm_num

/-- **The hexagonal `P₁`, pinned** (production form), given the second anchor
cell `T(4,3) = 21`. -/
theorem hex_P1_pinned (h43 : T hexLattice 4 3 = 21) : ∀ n : ℕ, 2 * 1 + 1 ≤ n →
    (T hexLattice n (n - 1) : ℚ)
      = hexP1.eval (n : ℚ) * (hexLattice.b : ℚ) ^ ((n : ℤ) - 1 - 3 * 1) := by
  refine pin hexLattice 1 hexP1 hexP1_deg ({3, 4} : Finset ℕ) (by decide) ?_ ?_
  · intro n hn; fin_cases hn <;> norm_num
  · intro n hn
    fin_cases hn
    · simp only [show (3 - 1 : ℕ) = 2 from rfl, show (3 * 1 + 1 - 3 : ℕ) = 1 from rfl]
      exact hex_guard_3
    · simp only [show (4 - 1 : ℕ) = 3 from rfl, show (3 * 1 + 1 - 4 : ℕ) = 0 from rfl]
      exact hex_guard_4 h43

/-- **The hexagonal `P₁`, human form**: the number of fixed polyhexes with `n`
cells and bounding-box height exactly `n − 1` is `(9n − 15)·2^(n−4)`, for every
`n ≥ 3`, given `T(4,3) = 21`. -/
theorem hex_P1_closed (h43 : T hexLattice 4 3 = 21) (n : ℕ) (hn : 3 ≤ n) :
    (T hexLattice n (n - 1) : ℚ) = (9 * (n : ℚ) - 15) * (2 : ℚ) ^ ((n : ℤ) - 4) := by
  have h := hex_P1_pinned h43 n (by omega)
  rw [b_hex] at h
  norm_num [hexP1_eval] at h ⊢
  rw [h]
  ring_nf

end Polyplets.Universal
