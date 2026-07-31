/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.Polynomial.Pochhammer
import Polyplets.Shape

/-!
# IntCoeff: the factorial residue `k! · P_k ∈ ℤ[X]`

`Shape.lean` proves that the production polynomial `P_k` is integer-*valued*
on all of `ℤ` (`production_int_all`). The paper (§6.1) states the sharper
classical residue: a polynomial of degree `≤ k` that is integer-valued on `ℤ`
has integer *coefficients* after multiplication by `k!`. That is what this
file adds.

* `binomQ j` — the binomial-coefficient polynomial `C(X, j) = descPochhammer j / j!`.
* `deltaPoly` — the forward difference `P(X+1) - P(X)`, with the degree drop
  (the same `taylor` argument `Shape.lean` runs inline inside
  `int_valued_of_consecutive`) and `deltaPoly (binomQ (j+1)) = binomQ j`.
* `exists_binom_expansion` — every `P` of degree `≤ k` that is integer-valued
  on `ℤ` is an *integer* combination `∑_{j ≤ k} c_j · binomQ j`. Proved by
  induction on `k` through `deltaPoly`: the difference has degree `≤ k - 1`
  and is again integer-valued, and the constant left over after antidifferencing
  is `P(0)`.
* `factorial_smul_int_coeff` — the generic residue: `k! • P = Q.map (ℤ → ℚ)`.
* `production_factorial_int` — applied to the shape witness of level `k`,
  repackaging `shape_production` with one extra conjunct.

No `native_decide` anywhere in this file.
-/

namespace Polyplets

open Polynomial

/-! ## The binomial basis -/

/-- `binomQ j` is the binomial-coefficient polynomial `C(X, j)`, i.e.
`X(X-1)⋯(X-j+1) / j!`. It has degree `j` and leading coefficient `(j!)⁻¹`. -/
noncomputable def binomQ (j : ℕ) : Polynomial ℚ :=
  C ((j.factorial : ℚ)⁻¹) * descPochhammer ℚ j

lemma binomQ_eval (j : ℕ) (x : ℚ) :
    (binomQ j).eval x = (j.factorial : ℚ)⁻¹ * (descPochhammer ℚ j).eval x := by
  rw [binomQ, eval_mul, eval_C]

/-- `C(X, 0) = 1`. -/
lemma binomQ_zero : binomQ 0 = 1 := by
  rw [binomQ, descPochhammer_zero, Nat.factorial_zero, Nat.cast_one, inv_one, map_one, mul_one]

/-- `C(0, j+1) = 0`: every positive-index basis element has zero constant term. -/
lemma binomQ_succ_eval_zero (j : ℕ) : (binomQ (j + 1)).eval 0 = 0 := by
  rw [binomQ_eval, descPochhammer_ne_zero_eval_zero ℚ (Nat.succ_ne_zero j), mul_zero]

/-! ## The forward difference operator -/

/-- The forward difference `ΔP = P(X+1) - P(X)`. -/
noncomputable def deltaPoly (P : Polynomial ℚ) : Polynomial ℚ := P.comp (X + C 1) - P

lemma deltaPoly_eval (P : Polynomial ℚ) (x : ℚ) :
    (deltaPoly P).eval x = P.eval (x + 1) - P.eval x := by
  rw [deltaPoly, eval_sub, eval_comp, eval_add, eval_X, eval_C]

lemma deltaPoly_sub (P Q : Polynomial ℚ) :
    deltaPoly (P - Q) = deltaPoly P - deltaPoly Q := by
  simp only [deltaPoly, sub_comp]
  ring

lemma deltaPoly_C_mul (a : ℚ) (P : Polynomial ℚ) :
    deltaPoly (C a * P) = C a * deltaPoly P := by
  simp only [deltaPoly, mul_comp, C_comp]
  ring

lemma deltaPoly_sum {ι : Type*} (s : Finset ι) (f : ι → Polynomial ℚ) :
    deltaPoly (∑ i ∈ s, f i) = ∑ i ∈ s, deltaPoly (f i) := by
  simp only [deltaPoly, Polynomial.sum_comp, Finset.sum_sub_distrib]

/-- The difference operator drops the degree. Same `taylor` argument that
`Shape.lean` runs inline inside `int_valued_of_consecutive`; hoisted here as a
named lemma about `deltaPoly`. -/
lemma deltaPoly_natDegree_le {P : Polynomial ℚ} {D : ℕ} (h : P.natDegree ≤ D + 1) :
    (deltaPoly P).natDegree ≤ D := by
  rcases eq_or_ne P 0 with rfl | hP0
  · simp [deltaPoly]
  · have hA : P.comp (X + C 1) = taylor 1 P := (taylor_apply 1 P).symm
    have hT0 : taylor 1 P ≠ 0 := by
      rw [ne_eq, taylor_eq_zero]
      exact hP0
    have hdlt : (deltaPoly P).degree < P.degree := by
      rw [deltaPoly, hA, ← degree_taylor P 1]
      exact degree_sub_lt (degree_taylor P 1) hT0 (leadingCoeff_taylor 1 P)
    rcases eq_or_ne (deltaPoly P) 0 with h0 | h0
    · rw [h0, natDegree_zero]
      exact Nat.zero_le D
    · have := natDegree_lt_natDegree h0 hdlt
      omega

/-- `descPochhammer (j+1)` at `x + 1` peels off the leading factor:
`(x+1)·x·(x-1)⋯(x+1-j)`. -/
lemma descPochhammer_succ_eval_add_one (j : ℕ) (x : ℚ) :
    (descPochhammer ℚ (j + 1)).eval (x + 1) = (x + 1) * (descPochhammer ℚ j).eval x := by
  rw [descPochhammer_succ_left, eval_mul, eval_X, eval_comp, eval_sub, eval_X, eval_one,
    add_sub_cancel_right]

/-- `Δ descPochhammer (j+1) = (j+1) · descPochhammer j` — the telescoping identity
behind the binomial basis. -/
lemma deltaPoly_descPochhammer (j : ℕ) :
    deltaPoly (descPochhammer ℚ (j + 1)) = C ((j : ℚ) + 1) * descPochhammer ℚ j := by
  refine Polynomial.funext fun x => ?_
  rw [deltaPoly_eval, descPochhammer_succ_eval_add_one, descPochhammer_succ_eval, eval_mul, eval_C]
  ring

/-- **The basis property**: `Δ C(X, j+1) = C(X, j)`. -/
lemma deltaPoly_binomQ (j : ℕ) : deltaPoly (binomQ (j + 1)) = binomQ j := by
  have hjne : ((j.factorial : ℚ)) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero j)
  have h1 : ((j : ℚ) + 1) ≠ 0 := by positivity
  have key : (((j + 1).factorial : ℚ))⁻¹ * ((j : ℚ) + 1) = ((j.factorial : ℚ))⁻¹ := by
    have hf : (((j + 1).factorial : ℚ)) = ((j : ℚ) + 1) * (j.factorial : ℚ) := by
      rw [Nat.factorial_succ]
      push_cast
      ring
    rw [hf]
    field_simp
  simp only [binomQ, deltaPoly_C_mul, deltaPoly_descPochhammer]
  rw [← mul_assoc, ← C_mul, key]

/-! ## Integer expansion in the binomial basis -/

/-- Every `ℚ`-polynomial of degree `≤ k` that is integer-valued on `ℤ` is an
**integer** combination of the binomial basis `C(X, 0), …, C(X, k)`.

Induction on `k`. The difference `ΔP` has degree `≤ k-1` and is again
integer-valued, so by the inductive hypothesis `ΔP = ∑_{j<k} c_j · C(X,j)`.
The polynomial `P' = ∑_{j<k} c_j · C(X, j+1)` has the same difference, so
`P - P'` is constant; the constant is `P(0)` because every `C(X, j+1)` vanishes
at `0`, and `P(0)` is an integer. -/
lemma exists_binom_expansion :
    ∀ (k : ℕ) (P : Polynomial ℚ), P.natDegree ≤ k →
      (∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ)) →
      ∃ c : ℕ → ℤ, P = ∑ j ∈ Finset.range (k + 1), C ((c j : ℚ)) * binomQ j := by
  intro k
  induction k with
  | zero =>
    intro P hdeg hval
    obtain ⟨z, hz⟩ := hval 0
    rw [Int.cast_zero] at hz
    refine ⟨fun _ => z, ?_⟩
    conv_lhs => rw [eq_C_of_natDegree_le_zero hdeg]
    rw [coeff_zero_eq_eval_zero, hz]
    simp [binomQ_zero]
  | succ k ih =>
    intro P hdeg hval
    -- the difference: one degree down, still integer-valued
    have hΔdeg : (deltaPoly P).natDegree ≤ k := deltaPoly_natDegree_le hdeg
    have hΔval : ∀ m : ℤ, ∃ z : ℤ, (deltaPoly P).eval (m : ℚ) = (z : ℚ) := by
      intro m
      obtain ⟨z1, hz1⟩ := hval (m + 1)
      obtain ⟨z2, hz2⟩ := hval m
      refine ⟨z1 - z2, ?_⟩
      rw [deltaPoly_eval]
      have hcast : ((m : ℚ) + 1) = ((m + 1 : ℤ) : ℚ) := by push_cast; ring
      rw [hcast, hz1, hz2]
      push_cast
      ring
    obtain ⟨c, hc⟩ := ih (deltaPoly P) hΔdeg hΔval
    -- the shifted combination has the same difference
    set P' : Polynomial ℚ :=
      ∑ j ∈ Finset.range (k + 1), C ((c j : ℚ)) * binomQ (j + 1) with hP'
    have hΔP' : deltaPoly P' = deltaPoly P := by
      rw [hP', deltaPoly_sum, hc]
      exact Finset.sum_congr rfl fun j _ => by rw [deltaPoly_C_mul, deltaPoly_binomQ]
    have hΔzero : deltaPoly (P - P') = 0 := by
      rw [deltaPoly_sub, hΔP', sub_self]
    -- hence `P - P'` is constant
    have hRconst : ∀ n : ℕ, (P - P').eval (n : ℚ) = (P - P').eval 0 := by
      intro n
      induction n with
      | zero => simp
      | succ n ihn =>
        have hstep := deltaPoly_eval (P - P') (n : ℚ)
        rw [hΔzero, eval_zero] at hstep
        have hcast : ((n + 1 : ℕ) : ℚ) = (n : ℚ) + 1 := by push_cast; ring
        rw [hcast]
        linarith
    have hRC : P - P' = C ((P - P').eval 0) := by
      have hroot : P - P' - C ((P - P').eval 0) = 0 := by
        refine Polynomial.eq_zero_of_infinite_isRoot _ ?_
        refine Set.infinite_of_injective_forall_mem
          (f := (Nat.cast : ℕ → ℚ)) Nat.cast_injective ?_
        intro n
        simp only [Set.mem_setOf_eq, IsRoot.def]
        rw [eval_sub, eval_C, hRconst n, sub_self]
      exact sub_eq_zero.mp hroot
    -- the constant is `P(0)`, an integer
    obtain ⟨z0, hz0⟩ := hval 0
    rw [Int.cast_zero] at hz0
    have hP'0 : P'.eval 0 = 0 := by
      rw [hP', eval_finsetSum]
      exact Finset.sum_eq_zero fun j _ => by rw [eval_mul, binomQ_succ_eval_zero, mul_zero]
    have hconst : (P - P').eval 0 = (z0 : ℚ) := by
      rw [eval_sub, hP'0, hz0, sub_zero]
    have hPeq : P = P' + C ((z0 : ℚ)) := by
      rw [← hconst, ← hRC]
      ring
    refine ⟨fun i => if i = 0 then z0 else c (i - 1), ?_⟩
    rw [Finset.sum_range_succ', hPeq]
    congr 1
    simp [binomQ_zero]

/-! ## The factorial residue -/

/-- **Factorial residue (generic form)**: a `ℚ`-polynomial of degree `≤ k` that
is integer-valued on `ℤ` has integer coefficients after multiplication by `k!`.

Expand in the binomial basis with integer coefficients
(`exists_binom_expansion`); then `k! · C(X, j) = (k!/j!) · descPochhammer j`
with `k!/j!` a natural number for `j ≤ k`, and `descPochhammer ℤ j` maps onto
`descPochhammer ℚ j`. -/
theorem factorial_smul_int_coeff {k : ℕ} {P : Polynomial ℚ}
    (hdeg : P.natDegree ≤ k)
    (hval : ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ)) :
    ∃ Q : Polynomial ℤ, (k.factorial : ℚ) • P = Q.map (Int.castRingHom ℚ) := by
  obtain ⟨c, hc⟩ := exists_binom_expansion k P hdeg hval
  refine ⟨∑ j ∈ Finset.range (k + 1),
    C (c j * ((k.factorial / j.factorial : ℕ) : ℤ)) * descPochhammer ℤ j, ?_⟩
  rw [Polynomial.map_sum, hc, smul_eq_C_mul, Finset.mul_sum]
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [Finset.mem_range] at hj
  have hjne : ((j.factorial : ℚ)) ≠ 0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero j)
  have hdvd : j.factorial ∣ k.factorial := Nat.factorial_dvd_factorial (by omega)
  have hkey : ((c j * ((k.factorial / j.factorial : ℕ) : ℤ) : ℤ) : ℚ)
      = (k.factorial : ℚ) * ((c j : ℚ) * (j.factorial : ℚ)⁻¹) := by
    rw [Int.cast_mul, Int.cast_natCast, Nat.cast_div hdvd hjne, div_eq_mul_inv]
    ring
  simp only [Polynomial.map_mul, Polynomial.map_C, descPochhammer_map, Int.coe_castRingHom]
  rw [hkey, binomQ, C_mul, C_mul]
  ring

/-- **Factorial residue (applied)**: every shape witness `P_k` of level `k`
satisfies `k! · P_k ∈ ℤ[X]`. Repackages `shape_production` with one extra
conjunct, so downstream text can cite a single theorem. -/
theorem production_factorial_int (k : ℕ) :
    ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
      (∀ n : ℕ, 2 * k + 1 ≤ n →
        (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) ∧
      ∃ Q : Polynomial ℤ, (k.factorial : ℚ) • P = Q.map (Int.castRingHom ℚ) := by
  obtain ⟨P, hdeg, -, hprod⟩ := shape_production k
  exact ⟨P, hdeg, hprod, factorial_smul_int_coeff hdeg (production_int_all hdeg hprod)⟩

#print axioms factorial_smul_int_coeff
#print axioms production_factorial_int

end Polyplets
