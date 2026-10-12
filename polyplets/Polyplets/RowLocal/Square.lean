/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Polyplets.RowLocal.Compute

/-!
# The square lattice: ordinary polyominoes

`D = {0}`, so `b = |D| = 1` and the universal diagonal law
(`RowLocal/Instance.lean`) reads

```
T(n, n-k) = P_k(n) · 1^(n-1-3k) = P_k(n)     for n ≥ 2k+1,
```

i.e. **the by-height diagonals of ordinary fixed polyominoes are eventually
polynomial in `n`, of degree `≤ k`.** The drift factor degenerates: with one
up-offset there is exactly one way to continue a walk row upward.

`adj_square` identifies the instance: `Adj squareLattice` is the ℓ¹ adjacency
`|Δx| + |Δy| = 1` of the ordinary square lattice, so `T squareLattice n H`
counts fixed polyominoes of `n` cells and bounding-box height exactly `H`.

## What is determined here

* `isDiagonalPoly_squareP1` / `square_T_sub_one` : `P₁(n) = 4n − 8`, i.e.
  `T(n, n−1) = 4n − 8` for `n ≥ 3` (paper instance table, density `4 = 2²`),
  given the second cell `T(4,3) = 8` as a hypothesis. The first
  `T(3,2) = 4` the kernel decides from the generic enumerator `Tc`, and
  `RowLocal/Compute.lean`'s `isDiagonalPoly_of_eval` does the Lagrange step; `T(4,3)` needs more
  than 8 GB in the kernel (measured 2026-10-12).
* `Checks.lean`: the row sum of the computed height triangle at `n = 3`
  reproduces A001168 (fixed polyominoes) `6`.
-/

namespace Polyplets.RowLocal

open Polynomial

/-! ## The lattice -/

/-- **The square lattice**: the single up-offset `0`. Together with the
nearest-neighbor row adjacency this is ordinary (rook-step) polyomino
adjacency. -/
def squareLattice : Lattice where
  D := {0}
  hD := ⟨0, by decide⟩

/-- Membership in the square up-offset set. -/
lemma mem_squareLattice_D {t : ℤ} : t ∈ squareLattice.D ↔ t = 0 := by
  change t ∈ ({0} : Finset ℤ) ↔ _
  simp

/-- **The square drift count is 1.** -/
@[simp] lemma b_square : squareLattice.b = 1 := by decide

/-- The square lattice has reach `1`: no step skips a column. -/
lemma square_reach_le : squareLattice.reach ≤ 1 :=
  reach_le_one _ (by decide)

/-- **The instance bridge**: row-local adjacency at the square lattice IS
ordinary ℓ¹ (edge) adjacency of the square lattice. -/
theorem adj_square {p q : ℤ × ℤ} :
    Adj squareLattice p q ↔ |p.1 - q.1| + |p.2 - q.2| = 1 := by
  have hne : (p ≠ q) ↔ ¬ (p.1 = q.1 ∧ p.2 = q.2) := not_congr Prod.ext_iff
  rw [Adj, hne]
  simp only [mem_squareLattice_D]
  rcases abs_cases (p.1 - q.1) with ⟨h1, h1'⟩ | ⟨h1, h1'⟩ <;>
    rcases abs_cases (p.2 - q.2) with ⟨h2, h2'⟩ | ⟨h2, h2'⟩ <;>
      rw [h1, h2] <;> omega

/-! ## The first cell

The generic enumerator at `W = n` (legitimate because `M ≤ 1`), decided by the
kernel; `Tc_eq_T_of_reach_le_one` transports the value to the noncomputable `T`.
The second anchor `T(4,3) = 8` needs more than 8 GB in the kernel (measured
2026-10-12) and enters the pin below as a hypothesis. -/

/-- `T(3,2) = 4`: the four L-trominoes. -/
theorem T_square_3_2 : T squareLattice 3 2 = 4 := by
  rw [← Tc_eq_T_of_reach_le_one square_reach_le]; decide +kernel

/-! ## Pinning `P₁` -/

/-- The square lattice's level-1 diagonal polynomial `P₁ = 4X − 8`. -/
noncomputable def squareP1 : Polynomial ℚ := C 4 * X - C 8

/-- `P₁` has degree `≤ 1`. -/
lemma squareP1_deg : squareP1.natDegree ≤ 1 := by
  refine le_trans (natDegree_sub_le _ _) (max_le ?_ ?_)
  · exact le_trans (natDegree_C_mul_le _ _) (by simp)
  · simp

/-- `P₁` evaluated. -/
lemma squareP1_eval (x : ℚ) : squareP1.eval x = 4 * x - 8 := by simp [squareP1]

/-- Guard at the first pin point: `P₁(3) = T(3,2) · b^1 = 4`. -/
lemma squareP1_eval_three :
    squareP1.eval (3 : ℚ) = ((T squareLattice 3 2 * squareLattice.b ^ 1 : ℕ) : ℚ) := by
  rw [squareP1_eval, T_square_3_2, b_square]; norm_num

/-- Guard at the second pin point: `P₁(4) = T(4,3) · b^0 = 8`, given the cell. -/
lemma squareP1_eval_four (h43 : T squareLattice 4 3 = 8) :
    squareP1.eval (4 : ℚ) = ((T squareLattice 4 3 * squareLattice.b ^ 0 : ℕ) : ℚ) := by
  rw [squareP1_eval, h43, b_square]; norm_num

/-- **The square `P₁`**, given the second cell
`T(4,3) = 8`: Lagrange uniqueness identifies `4X − 8` with the witness of
`RowLocal.exists_isDiagonalPoly`. -/
theorem isDiagonalPoly_squareP1 (h43 : T squareLattice 4 3 = 8) :
    IsDiagonalPoly squareLattice 1 squareP1 := by
  refine isDiagonalPoly_of_eval squareLattice 1 squareP1 squareP1_deg ({3, 4} : Finset ℕ)
    (by decide) ?_ ?_
  · intro n hn; fin_cases hn <;> norm_num
  · intro n hn
    fin_cases hn
    · simp only [show (3 - 1 : ℕ) = 2 from rfl, show (3 * 1 + 1 - 3 : ℕ) = 1 from rfl]
      exact squareP1_eval_three
    · simp only [show (4 - 1 : ℕ) = 3 from rfl, show (3 * 1 + 1 - 4 : ℕ) = 0 from rfl]
      exact squareP1_eval_four h43

/-- **The square `P₁`, human form**: the number of fixed polyominoes with `n`
cells and bounding-box height exactly `n − 1` is `4n − 8`, for every `n ≥ 3`,
given `T(4,3) = 8`. (The drift factor is `1^(n-4) = 1`, so the law
*is* the closed form.) -/
theorem square_T_sub_one (h43 : T squareLattice 4 3 = 8) (n : ℕ) (hn : 3 ≤ n) :
    (T squareLattice n (n - 1) : ℚ) = 4 * (n : ℚ) - 8 := by
  have h := isDiagonalPoly_squareP1 h43 n (by omega)
  rw [b_square] at h
  simpa [squareP1_eval] using h

end Polyplets.RowLocal
