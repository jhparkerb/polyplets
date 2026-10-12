/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.EnumData
import Polyplets.Grand.Staircase
import Polyplets.Sequence
import Polyplets.Universal.Hex
import Polyplets.King
import Polyplets.Universal.Square

/-!
# Checks: validation facts that no theorem consumes

Small kernel-decided values and numeric instances of the recursions, kept
out of the library modules the way a test file is: the root target builds
this module, nothing imports it. Each value is a banked engine number
(`results/triangle.txt`, `results/sym_counts.txt`, OEIS) or a paper count;
a mismatch fails the build. The facts a proof actually needs (`T_1_1`,
`T_3_2`, `T_4_3`, `V_1_1`, `Vt_1_1`, `d_0_1`, the first anchor cell of each lattice)
live beside their consumers.

Everything up to six cells comes from the bit-board enumerator of `Enum.lean`
through the stored boards of `EnumData.lean` (`README.md`, "No
`native_decide`").
-/

namespace Polyplets

/-! ## The computable counter against the triangle -/

/-- Degenerate and impossible shapes count zero, as `T` does. -/
example : Tc 0 0 = 0 := by decide +kernel
example : Tc 0 3 = 0 := by decide +kernel
example : Tc 3 0 = 0 := by decide +kernel
example : Tc 2 3 = 0 := by decide +kernel

/-- `T 2 1 = 1`: the horizontal king domino. -/
theorem T_2_1 : T 2 1 = 1 := by rw [← Tc_eq_T]; decide +kernel

/-- `T 2 2 = 3`: vertical domino and the two diagonal king dominoes. -/
theorem T_2_2 : T 2 2 = 3 := by rw [← Tc_eq_T]; decide +kernel

/-- `T 3 1 = 1`: the horizontal tromino. -/
theorem T_3_1 : T 3 1 = 1 := by rw [← Tc_eq_T]; decide +kernel

/-- `a 1 = 1`: the single cell. -/
theorem a_1 : a 1 = 1 := by rw [← ac_eq_a 1]; decide +kernel

/-- `a 2 = 4`: the horizontal, vertical and two diagonal king dominoes. -/
theorem a_2 : a 2 = 4 := by rw [← ac_eq_a 2]; decide +kernel

/-! ## The weights, and the peeling identities at their onset -/

/-- `Vt 1 2 = 7` (cross-checked enumeration, 2026-07-20). -/
theorem Vt_1_2 : Vt 1 2 = 7 := by decide +kernel

/-- `d 0 2 = 3`: the free walk chain `3^(H-1)` at `H = 2`. -/
theorem d_0_2 : d 0 2 = 3 := by decide +kernel

/-- `d 1 2 = 5`: of the `T(3,2) = 10` animals, five have a walk top row. -/
theorem d_1_2 : d 1 2 = 5 := by decide +kernel

/-- The c-identity at its onset `k = 1, H = 2`: `T(3,2) = 10 = 5 + 5·1`. -/
theorem c_ident_check_k1_H2 : T 3 2 = d 1 2 + Vt 1 1 * d 0 1 := by
  norm_num [T_3_2, d_1_2, Vt_1_1, d_0_1]

/-- The μ-recursion at `(k, H) = (1, 2)`: `d 1 3 = μ₀·d 1 2 + μ₁·d 0 2`. -/
theorem d_mu_rec_check_k1_H2 : (d 1 3 : ℚ) = mu 0 * d 1 2 + mu 1 * d 0 2 := by
  have h := d_mu_rec 2 1 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add, Nat.sub_zero] using h

/-- …and its right-hand side evaluates to the banked `d 1 3 = 40`:
`3·5 + (25/3)·3`. -/
theorem d_mu_rec_value_check : mu 0 * (d 1 2 : ℚ) + mu 1 * (d 0 2 : ℚ) = 40 := by
  rw [mu_zero, mu_one, d_1_2, d_0_2]; norm_num

/-- The μ-recursion at `(k, H) = (2, 3)`. -/
theorem d_mu_rec_check_k2_H3 : (d 2 4 : ℚ) = mu 0 * d 2 3 + mu 1 * d 1 3 + mu 2 * d 0 3 := by
  have h := d_mu_rec 3 2 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add, Nat.sub_zero] using h

/-- The staircase at `(k, H) = (1, 2)`: `T 4 3 = μ₀·T 3 2 + μ₁·T 2 2`. -/
theorem T_staircase_check_k1_H2 : (T 4 3 : ℚ) = mu 0 * T 3 2 + mu 1 * T 2 2 := by
  have h := T_staircase 1 2 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add,
    Nat.sub_zero, Nat.sub_self] using h

/-- …and it evaluates: `55 = 3·10 + (25/3)·3`. -/
theorem T_staircase_value_check : mu 0 * (T 3 2 : ℚ) + mu 1 * (T 2 2 : ℚ) = 55 := by
  rw [mu_zero, mu_one, T_3_2, T_2_2]; norm_num

/-! ## The shape theorem at `k = 0` -/

/-- The shape-derived closed form gives the banked `T 3 3 = 9`. -/
theorem shape_check_T_3_3 : T 3 3 = 9 := by
  have h := T_diag_pow 3 (by omega)
  have he : ((3 : ℕ) : ℤ) - 1 = 2 := by omega
  rw [he] at h
  norm_num at h
  exact_mod_cast h

/-- The shape-derived `T 4 4 = 27`. -/
theorem shape_check_T_4_4 : T 4 4 = 27 := by
  have h := T_diag_pow 4 (by omega)
  have he : ((4 : ℕ) : ℤ) - 1 = 3 := by omega
  rw [he] at h
  norm_num at h
  exact_mod_cast h

/-! ## The generic enumerator against three families -/

/-- A006770 at `n = 3`: `1 + 10 + 9 = 20` fixed polyplets. -/
theorem king_rowSum_3 : Universal.rowSum Universal.kingLattice 3 3 = 20 := by decide +kernel

/-- A001207 at `n = 3`: `1 + 6 + 4 = 11` fixed 3-cell polyhexes. -/
theorem hex_rowSum_3 : Universal.rowSum Universal.hexLattice 3 3 = 11 := by decide +kernel

/-- A001168 at `n = 3`: `1 + 4 + 1 = 6` fixed trominoes. -/
theorem square_rowSum_3 : Universal.rowSum Universal.squareLattice 3 3 = 6 := by decide +kernel

/-! ## The bit-board enumerator: rows `≤ 6` of the triangle and everything on them -/

open Enum in
/-- The first six values of A006770 (`results/triangle.txt` row sums). -/
theorem a_3_to_6 : a 3 = 20 ∧ a 4 = 110 ∧ a 5 = 638 ∧ a 6 = 3832 := by
  rw [a_eq_length (by norm_num) (by norm_num), a_eq_length (by norm_num) (by norm_num),
    a_eq_length (by norm_num) (by norm_num), a_eq_length (by norm_num) (by norm_num), L5_eq, L6_eq]
  decide +kernel

open Enum in
/-- Rows `4`, `5` and `6` of `results/triangle.txt`; `T 4 3`, `T 4 4`, `T 5 3`,
`T 6 4` are elsewhere. -/
theorem T_rows_4_to_6 :
    T 4 1 = 1 ∧ T 4 2 = 27 ∧
    T 5 1 = 1 ∧ T 5 2 = 68 ∧ T 5 4 = 240 ∧ T 5 5 = 81 ∧
    T 6 1 = 1 ∧ T 6 2 = 167 ∧ T 6 3 = 996 ∧ T 6 5 = 945 ∧ T 6 6 = 243 := by
  simp only [T_eq_length (by norm_num : 1 ≤ 4) (by norm_num : 4 ≤ 14),
    T_eq_length (by norm_num : 1 ≤ 5) (by norm_num : 5 ≤ 14),
    T_eq_length (by norm_num : 1 ≤ 6) (by norm_num : 6 ≤ 14), L5_eq, L6_eq]
  decide +kernel

open Enum in
/-- The walk-top counts on rows `≤ 6` (`results/triangle.txt` with the walk-top
filter; `d 0 H = 3^(H-1)`). -/
theorem d_rows_le_6 : d 0 3 = 9 ∧ d 0 4 = 27 ∧ d 1 3 = 40 ∧ d 2 3 = 136 ∧ d 2 4 = 1019 := by
  simp only [d_eq_length (by norm_num : 1 ≤ 3) (by norm_num : 3 + 0 ≤ 14),
    d_eq_length (by norm_num : 1 ≤ 4) (by norm_num : 4 + 0 ≤ 14),
    d_eq_length (by norm_num : 1 ≤ 3) (by norm_num : 3 + 1 ≤ 14),
    d_eq_length (by norm_num : 1 ≤ 3) (by norm_num : 3 + 2 ≤ 14),
    d_eq_length (by norm_num : 1 ≤ 4) (by norm_num : 4 + 2 ≤ 14), Nat.reduceAdd, L5_eq, L6_eq]
  decide +kernel

open Enum in
/-- The cluster weights on at most six cells (cross-checked enumerations,
2026-07-20). -/
theorem weights_le_6 :
    V 1 2 = 49 ∧ V 2 2 = 339 ∧ V 1 3 = 81 ∧ Vt 2 2 = 66 ∧ Vt 1 3 = 9 ∧ Vt 2 3 = 307 := by
  simp only [V_eq_length (by norm_num : 1 + 2 + 2 ≤ 14), V_eq_length (by norm_num : 2 + 2 + 2 ≤ 14),
    V_eq_length (by norm_num : 1 + 3 + 2 ≤ 14),
    Vt_eq_length (by norm_num : 1 ≤ 2) (by norm_num : 2 + 2 + 1 ≤ 14),
    Vt_eq_length (by norm_num : 1 ≤ 1) (by norm_num : 1 + 3 + 1 ≤ 14),
    Vt_eq_length (by norm_num : 1 ≤ 2) (by norm_num : 2 + 3 + 1 ≤ 14), Nat.reduceAdd, L5_eq,
    L6_eq]
  decide +kernel

open Enum in
/-- The symmetry counts for `n ≤ 5` (`results/sym_counts.txt`): quarter turns,
half turns, the axis mirror and the diagonal mirror. -/
theorem symmetry_le_5 :
    R90 1 = 1 ∧ R90 2 = 0 ∧ R90 3 = 0 ∧ R90 4 = 2 ∧ R90 5 = 2 ∧
    R180 1 = 1 ∧ R180 2 = 4 ∧ R180 3 = 4 ∧ R180 4 = 22 ∧ R180 5 = 22 ∧
    Hm 1 = 1 ∧ Hm 2 = 2 ∧ Hm 3 = 4 ∧ Hm 4 = 10 ∧ Hm 5 = 22 ∧
    Dm 1 = 1 ∧ Dm 2 = 2 ∧ Dm 3 = 4 ∧ Dm 4 = 10 ∧ Dm 5 = 22 := by
  simp only [R90, R180, Hm, Dm, fixCount_eq_length (by norm_num : 1 ≤ 1) (by norm_num : 1 ≤ 7),
    fixCount_eq_length (by norm_num : 1 ≤ 2) (by norm_num : 2 ≤ 7),
    fixCount_eq_length (by norm_num : 1 ≤ 3) (by norm_num : 3 ≤ 7),
    fixCount_eq_length (by norm_num : 1 ≤ 4) (by norm_num : 4 ≤ 7),
    fixCount_eq_length (by norm_num : 1 ≤ 5) (by norm_num : 5 ≤ 7), L5_eq]
  decide +kernel

end Polyplets
