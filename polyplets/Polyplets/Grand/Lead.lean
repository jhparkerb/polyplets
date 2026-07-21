/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.ExpForm

/-!
# Lead: the leading coefficient `25^k/k!` and exact degree `k`

The `grand-form.md` Corollary 2, formalized: every diagonal polynomial `P_k` has
degree exactly `k` and leading coefficient `25^k/k!`.

`expPoly a b k` is the `Polynomial ℚ`-valued version of `expCoeff` (the affine
value `a_j + b_j·n` replaced by the linear polynomial `C(a j) + C(b j)·X`);
`expPoly_eval` ties it to `expCoeff`. A single coefficient induction
(`expPoly_coeff_top`) extracts the top coefficient `(b 1)^k/k!` — the only
degree-`k` contribution to `k·E_k` is `1·(b₁X)·E_{k−1}`'s top term. With
`bSeq_one : bSeq 1 = 25` (the sole `native_decide` dependency, via `mu_one`) this
gives `lead_coeff_25`. `shape_lead` composes it with `grand_form` and polynomial
uniqueness to conclude the corollary for any shape witness.
-/

namespace Polyplets

open Polynomial

/-! ## `bSeq 1 = 25` -/

/-- `bSeq 1 = 25`. Numeric: `mSeq 1 = 25` (via `mu_one`), `Wc 1 = −25`,
`logSeq Wc 1 = −25`. Carries `V_1_1`'s `Lean.ofReduceBool` through `mu_one`. -/
theorem bSeq_one : bSeq 1 = 25 := by
  have hm1 : mSeq 1 = 25 := by rw [mSeq, mu_one]; norm_num
  have hW1 : Wc 1 = -25 := by
    rw [Wc_unfold 1 le_rfl, Finset.Icc_self, Finset.sum_singleton, hm1]
    have hcp : convPow Wc 2 0 = 1 := by
      have h2 : convPow Wc 2 = conv Wc Wc := by
        rw [show (2 : ℕ) = 1 + 1 from rfl, convPow, convPow_Wc_one]
      rw [h2]
      simp only [conv]
      rw [Finset.sum_range_one, Nat.sub_zero, Wc_zero]
      norm_num
    rw [hcp]; norm_num
  have hL1 : logSeq Wc 1 = -25 := by
    rw [show (1 : ℕ) = 0 + 1 from rfl, logSeq]
    simp [hW1]
  rw [bSeq]; norm_num [hL1]

/-! ## The polynomial version of `expCoeff` -/

set_option linter.unusedVariables false in
/-- `expPoly a b k`: the `Polynomial ℚ` whose `eval n` is `expCoeff a b k n`, via
the derivative recursion with the affine value replaced by `C(a j) + C(b j)·X`. -/
noncomputable def expPoly (a b : ℕ → ℚ) : ℕ → Polynomial ℚ
  | 0     => 1
  | t + 1 => C (1 / ((t : ℚ) + 1)) * ∑ j ∈ Finset.Icc 1 (t + 1),
      C (j : ℚ) * (C (a j) + C (b j) * X) *
        (if h : t + 1 - j ≤ t then expPoly a b (t + 1 - j) else 0)
  decreasing_by exact Nat.lt_succ_of_le h

/-- De-guarded derivative recursion for `expPoly`. -/
lemma expPoly_unfold (a b : ℕ → ℚ) (t : ℕ) :
    C ((t : ℚ)) * expPoly a b t
      = ∑ j ∈ Finset.Icc 1 t, C (j : ℚ) * (C (a j) + C (b j) * X) * expPoly a b (t - j) := by
  cases t with
  | zero => simp
  | succ t =>
    rw [expPoly]
    have hg : (∑ j ∈ Finset.Icc 1 (t + 1), C (j : ℚ) * (C (a j) + C (b j) * X) *
          (if h : t + 1 - j ≤ t then expPoly a b (t + 1 - j) else 0))
        = ∑ j ∈ Finset.Icc 1 (t + 1),
            C (j : ℚ) * (C (a j) + C (b j) * X) * expPoly a b (t + 1 - j) := by
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Finset.mem_Icc] at hj; rw [dif_pos (by omega)]
    rw [hg, ← mul_assoc, ← C_mul]
    rw [show ((↑(t + 1) : ℚ)) * (1 / ((t : ℚ) + 1)) = 1 by push_cast; field_simp, C_1, one_mul]

/-- `expPoly` evaluates to `expCoeff`. -/
lemma expPoly_eval (a b : ℕ → ℚ) (k : ℕ) (n : ℚ) :
    (expPoly a b k).eval n = expCoeff a b k n := by
  have key : (fun k => (expPoly a b k).eval n) = expSeq (fun j => a j + b j * n) := by
    refine expSeq_eq_of ?_ ?_
    · simp [expPoly]
    · intro t
      have hu := congrArg (Polynomial.eval n) (expPoly_unfold a b t)
      simpa only [eval_mul, eval_C, eval_finsetSum, eval_add, eval_X, mul_assoc] using hu
  calc (expPoly a b k).eval n = (fun k => (expPoly a b k).eval n) k := rfl
    _ = expSeq (fun j => a j + b j * n) k := by rw [key]
    _ = expCoeff a b k n := rfl

/-! ## Degree and top coefficient -/

/-- A linear polynomial has degree `≤ 1`. -/
lemma natDegree_linear_le (c d : ℚ) : (C c + C d * X).natDegree ≤ 1 := by
  refine le_trans (natDegree_add_le _ _) (max_le ?_ ?_)
  · rw [natDegree_C]; exact Nat.zero_le _
  · exact le_trans (natDegree_C_mul_le _ _) (le_of_eq natDegree_X)

/-- Coefficient of a linear-times-polynomial product one above the split. -/
lemma coeff_linear_mul (c d : ℚ) (P : Polynomial ℚ) (m : ℕ) :
    ((C c + C d * X) * P).coeff (m + 1) = c * P.coeff (m + 1) + d * P.coeff m := by
  rw [add_mul, coeff_add, coeff_C_mul, mul_assoc (C d) X P, coeff_C_mul, coeff_X_mul]

/-- `(expPoly a b k).natDegree ≤ k`. -/
lemma expPoly_natDegree_le (a b : ℕ → ℚ) (k : ℕ) : (expPoly a b k).natDegree ≤ k := by
  induction k using Nat.strong_induction_on with
  | _ k IH =>
    cases k with
    | zero => simp [expPoly]
    | succ t =>
      rw [expPoly]
      refine le_trans (natDegree_C_mul_le _ _) ?_
      refine natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
      rw [Finset.mem_Icc] at hj
      rw [dif_pos (by omega)]
      have h1 : (C (j : ℚ) * (C (a j) + C (b j) * X)).natDegree ≤ 1 :=
        le_trans (natDegree_C_mul_le _ _) (natDegree_linear_le _ _)
      calc (C (j : ℚ) * (C (a j) + C (b j) * X) * expPoly a b (t + 1 - j)).natDegree
          ≤ (C (j : ℚ) * (C (a j) + C (b j) * X)).natDegree + (expPoly a b (t + 1 - j)).natDegree :=
            natDegree_mul_le
        _ ≤ 1 + (t + 1 - j) := add_le_add h1 (IH (t + 1 - j) (by omega))
        _ ≤ t + 1 := by omega

/-- **Top coefficient.** `(expPoly a b k).coeff k = (b 1)^k / k!` — the only
degree-`k` contribution is the `j = 1` term's `b₁·X·E_{k−1}` top. -/
lemma expPoly_coeff_top (a b : ℕ → ℚ) (k : ℕ) :
    (expPoly a b k).coeff k = (b 1) ^ k / (k.factorial : ℚ) := by
  induction k with
  | zero => simp [expPoly]
  | succ k IH =>
    have hu := congrArg (fun p => Polynomial.coeff p (k + 1)) (expPoly_unfold a b (k + 1))
    simp only [coeff_C_mul, finsetSum_coeff, mul_assoc] at hu
    -- only the j = 1 term contributes to coeff (k+1); the rest vanish by degree
    rw [Finset.sum_eq_single_of_mem 1 (Finset.mem_Icc.mpr (by omega)) ?_] at hu
    · rw [show k + 1 - 1 = k by omega, coeff_linear_mul] at hu
      have hz : (expPoly a b k).coeff (k + 1) = 0 :=
        coeff_eq_zero_of_natDegree_lt (lt_of_le_of_lt (expPoly_natDegree_le a b k) (by omega))
      rw [hz, IH] at hu
      -- hu : ↑(k+1) * coeff (k+1) = ↑1 * (a 1 * 0 + b 1 * (b1^k / k!))
      have hne : ((k + 1 : ℕ) : ℚ) ≠ 0 := by push_cast; positivity
      rw [show ((k + 1 : ℕ) : ℚ) = (k : ℚ) + 1 by push_cast; ring] at hu
      have hfac : ((k + 1).factorial : ℚ) = ((k : ℚ) + 1) * (k.factorial : ℚ) := by
        rw [Nat.factorial_succ]; push_cast; ring
      rw [hfac]
      have hkf : (k.factorial : ℚ) ≠ 0 := by positivity
      field_simp at hu ⊢
      linear_combination hu
    · intro j hj hj1
      rw [Finset.mem_Icc] at hj
      have hdeg : ((C (a j) + C (b j) * X) * expPoly a b (k + 1 - j)).natDegree < k + 1 :=
        lt_of_le_of_lt natDegree_mul_le (lt_of_le_of_lt
          (add_le_add (natDegree_linear_le _ _) (expPoly_natDegree_le a b (k + 1 - j))) (by omega))
      rw [coeff_eq_zero_of_natDegree_lt hdeg, mul_zero]

/-! ## The `25^k/k!` corollary and exact degree -/

/-- **Leading coefficient, proved.** `(expPoly aSeq bSeq k).coeff k = 25^k/k!`. -/
theorem lead_coeff_25 (k : ℕ) :
    (expPoly aSeq bSeq k).coeff k = 25 ^ k / (k.factorial : ℚ) := by
  rw [expPoly_coeff_top aSeq bSeq k, bSeq_one]

/-- `(expPoly aSeq bSeq k).natDegree = k` — the top coefficient is nonzero. -/
theorem expPoly_natDegree_eq (k : ℕ) : (expPoly aSeq bSeq k).natDegree = k := by
  refine le_antisymm (expPoly_natDegree_le aSeq bSeq k) ?_
  refine le_natDegree_of_ne_zero ?_
  rw [lead_coeff_25]
  positivity

/-! ## The shape corollary -/

/-- **Corollary 2 (grand-form.md), formalized.** Any shape witness `P` (a
degree-`≤k` polynomial reproducing the `T`-diagonals for all `n ≥ 2k+1`, exactly
`shape_production`'s conclusion) has degree exactly `k` and leading coefficient
`25^k/k!`. Proved by identifying `P` with `expPoly aSeq bSeq k` on the infinite
onset set (`grand_form`), then reading off the top coefficient. -/
theorem shape_lead (k : ℕ) (P : Polynomial ℚ) (_hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) :
    P.natDegree = k ∧ P.coeff k = 25 ^ k / (k.factorial : ℚ) := by
  have hpt : ∀ m : ℕ, 2 * k + 1 ≤ m → P.eval (m : ℚ) = (expPoly aSeq bSeq k).eval (m : ℚ) := by
    intro m hm
    have hmk : k ≤ m := by omega
    have hg := grand_form k (m - k) (by omega)
    rw [show (m - k) + k = m by omega,
      show ((m - k : ℕ) : ℚ) + (k : ℚ) = (m : ℚ) by rw [Nat.cast_sub hmk]; ring] at hg
    have h1 := hP m hm
    rw [expPoly_eval]
    have h3m : (3 : ℚ) ^ m ≠ 0 := by positivity
    exact mul_right_cancel₀ h3m (h1.symm.trans hg)
  have hPQ : P = expPoly aSeq bSeq k := by
    refine eq_of_infinite_eval_eq _ _ ?_
    refine Set.infinite_of_injective_forall_mem
      (f := fun n : ℕ => ((n + (2 * k + 1) : ℕ) : ℚ)) ?_ ?_
    · intro x y hxy
      simpa using hxy
    · intro n
      exact hpt (n + (2 * k + 1)) (by omega)
  rw [hPQ]
  exact ⟨expPoly_natDegree_eq k, lead_coeff_25 k⟩

/-! ## Axiom sanity check -/

section Sanity

#print axioms bSeq_one
#print axioms expPoly_eval
#print axioms expPoly_coeff_top
#print axioms lead_coeff_25
#print axioms expPoly_natDegree_eq
#print axioms shape_lead

end Sanity

end Polyplets
