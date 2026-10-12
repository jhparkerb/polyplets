/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.NumberTheory.Bernoulli
import Mathlib.Algebra.Polynomial.Taylor
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Two facts about polynomials over `ℚ` on the integers

The algebra the diagonal law (`RowLocal/DiagonalLaw.lean`)
needs and nothing else:

* `exists_poly_sum_Icc` — the discrete antiderivative: every `g ∈ ℚ[X]` has a
  `G` of degree `≤ deg g + 1` with `∑_{i ∈ Icc a b} g(i) = G(b) − G(a−1)`,
  built from Faulhaber's formula (`sum_range_pow`);
* `int_valued_of_consecutive` — a polynomial of degree `≤ D` that is
  integer-valued at `D + 1` consecutive integers is integer-valued on all of
  `ℤ`, by finite differences (the difference polynomial drops a degree).

Mathlib has the forward-difference calculus (`fwdDiff`) but not this
integer-valuedness theorem (checked 2026-10-12).
-/

namespace Polyplets

open Polynomial

/-! ## Interval-sum bookkeeping -/

/-- An `Icc`-sum is a difference of prefix (`range`) sums. -/
lemma sum_Icc_eq_sum_range_sub (f : ℕ → ℚ) {a b : ℕ} (h : a ≤ b + 1) :
    ∑ i ∈ Finset.Icc a b, f i
      = (∑ i ∈ Finset.range (b + 1), f i) - ∑ i ∈ Finset.range a, f i := by
  rw [← Finset.Ico_add_one_right_eq_Icc, Finset.sum_Ico_eq_sub _ h]

/-! ## The discrete antiderivative, via Faulhaber -/

/-- The Faulhaber polynomial for exponent `p`: evaluates at every natural `n`
to the power sum `∑_{i < n} i^p` (`faulhaberPoly_eval`); degree `≤ p + 1`. -/
noncomputable def faulhaberPoly (p : ℕ) : Polynomial ℚ :=
  ∑ i ∈ Finset.range (p + 1),
    C (_root_.bernoulli i * ((p + 1).choose i) / (p + 1)) * X ^ (p + 1 - i)

lemma faulhaberPoly_natDegree_le (p : ℕ) : (faulhaberPoly p).natDegree ≤ p + 1 := by
  refine natDegree_sum_le_of_forall_le _ _ fun i _ => ?_
  refine le_trans (natDegree_C_mul_le _ _) ?_
  rw [natDegree_X_pow]
  omega

/-- **Faulhaber's formula**, packaged as a polynomial identity at the
naturals. -/
lemma faulhaberPoly_eval (p n : ℕ) :
    (faulhaberPoly p).eval (n : ℚ) = ∑ i ∈ Finset.range n, (i : ℚ) ^ p := by
  rw [sum_range_pow, faulhaberPoly, eval_finsetSum]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [eval_mul, eval_C, eval_pow, eval_X]
  ring

/-- **Discrete antiderivative.** Every `g : ℚ[X]` has a `G : ℚ[X]` with
`deg G ≤ deg g + 1` (and `G = 0` for `g = 0`) summing it over any integer
interval: `∑_{i ∈ Icc a b} g(i) = G(b) - G(a-1)`. The one real algebra input
of the diagonal law. -/
lemma exists_poly_sum_Icc (g : Polynomial ℚ) :
    ∃ G : Polynomial ℚ, G.natDegree ≤ g.natDegree + 1 ∧ (g = 0 → G = 0) ∧
      ∀ a b : ℕ, a ≤ b + 1 →
        ∑ i ∈ Finset.Icc a b, g.eval (i : ℚ) = G.eval (b : ℚ) - G.eval ((a : ℚ) - 1) := by
  set G₀ : Polynomial ℚ :=
    ∑ p ∈ Finset.range (g.natDegree + 1), C (g.coeff p) * faulhaberPoly p with hG₀
  have hG₀eval : ∀ n : ℕ, G₀.eval (n : ℚ) = ∑ i ∈ Finset.range n, g.eval (i : ℚ) := by
    intro n
    rw [hG₀, eval_finsetSum]
    calc ∑ p ∈ Finset.range (g.natDegree + 1), (C (g.coeff p) * faulhaberPoly p).eval (n : ℚ)
        = ∑ p ∈ Finset.range (g.natDegree + 1),
            ∑ i ∈ Finset.range n, g.coeff p * (i : ℚ) ^ p := by
          refine Finset.sum_congr rfl fun p _ => ?_
          rw [eval_mul, eval_C, faulhaberPoly_eval, Finset.mul_sum]
      _ = ∑ i ∈ Finset.range n, ∑ p ∈ Finset.range (g.natDegree + 1),
            g.coeff p * (i : ℚ) ^ p := Finset.sum_comm
      _ = ∑ i ∈ Finset.range n, g.eval (i : ℚ) := by
          refine Finset.sum_congr rfl fun i _ => ?_
          rw [eval_eq_sum_range]
  refine ⟨G₀.comp (X + C 1), ?_, ?_, ?_⟩
  · refine le_trans natDegree_comp_le ?_
    rw [natDegree_X_add_C, mul_one]
    refine natDegree_sum_le_of_forall_le _ _ fun p hp => ?_
    rw [Finset.mem_range] at hp
    refine le_trans (natDegree_C_mul_le _ _) (le_trans (faulhaberPoly_natDegree_le p) ?_)
    omega
  · intro hgz
    have hz : G₀ = 0 := by
      rw [hG₀]
      exact Finset.sum_eq_zero fun p _ => by rw [hgz]; simp
    rw [hz, zero_comp]
  · intro a b hab
    have hcomp : ∀ x : ℚ, (G₀.comp (X + C 1)).eval x = G₀.eval (x + 1) := fun x => by
      rw [eval_comp, eval_add, eval_X, eval_C]
    rw [sum_Icc_eq_sum_range_sub _ hab, hcomp, hcomp]
    have h1 : (b : ℚ) + 1 = ((b + 1 : ℕ) : ℚ) := by push_cast; ring
    have h2 : (a : ℚ) - 1 + 1 = (a : ℚ) := by ring
    rw [h1, h2, hG₀eval, hG₀eval]

/-! ## Integer values by finite differences -/

/-- **Finite differences**: a `ℚ`-polynomial of degree
`≤ D` taking integer values at the `D+1` consecutive integers
`a, a+1, …, a+D` takes integer values at every integer. Induction on `D`
through the difference polynomial `P(X+1) - P(X)`, whose degree drops by one
(`taylor` API), then integer induction up and down from `a`. -/
theorem int_valued_of_consecutive :
    ∀ (D : ℕ) (P : Polynomial ℚ) (a : ℤ), P.natDegree ≤ D →
      (∀ i : ℕ, i ≤ D → ∃ z : ℤ, P.eval ((a + i : ℤ) : ℚ) = (z : ℚ)) →
      ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) := by
  intro D
  induction D with
  | zero =>
    intro P a hdeg hval m
    obtain ⟨z, hz⟩ := hval 0 le_rfl
    refine ⟨z, ?_⟩
    have hPC : P = C (P.coeff 0) := eq_C_of_natDegree_le_zero hdeg
    rw [hPC, eval_C] at hz ⊢
    exact hz
  | succ D ih =>
    intro P a hdeg hval m
    -- the difference polynomial, one degree down
    set Q : Polynomial ℚ := P.comp (X + C 1) - P with hQ
    have hQeval : ∀ x : ℚ, Q.eval x = P.eval (x + 1) - P.eval x := by
      intro x
      rw [hQ, eval_sub, eval_comp, eval_add, eval_X, eval_C]
    have hQdeg : Q.natDegree ≤ D := by
      rcases eq_or_ne P 0 with rfl | hP0
      · simp [hQ]
      · have hA : P.comp (X + C 1) = taylor 1 P := (taylor_apply 1 P).symm
        have hT0 : taylor 1 P ≠ 0 := by
          rw [ne_eq, taylor_eq_zero]
          exact hP0
        have hdlt : Q.degree < P.degree := by
          rw [hQ, hA, ← degree_taylor P 1]
          exact degree_sub_lt (degree_taylor P 1) hT0 (leadingCoeff_taylor 1 P)
        rcases eq_or_ne Q 0 with hQ0 | hQ0
        · rw [hQ0, natDegree_zero]
          exact Nat.zero_le D
        · have := natDegree_lt_natDegree hQ0 hdlt
          omega
    have hQval : ∀ i : ℕ, i ≤ D → ∃ z : ℤ, Q.eval ((a + i : ℤ) : ℚ) = (z : ℚ) := by
      intro i hi
      obtain ⟨z1, hz1⟩ := hval (i + 1) (by omega)
      obtain ⟨z2, hz2⟩ := hval i (by omega)
      refine ⟨z1 - z2, ?_⟩
      rw [hQeval]
      have hcast : ((a + i : ℤ) : ℚ) + 1 = ((a + (i + 1 : ℕ) : ℤ) : ℚ) := by
        push_cast
        ring
      rw [hcast, hz1, hz2]
      push_cast
      ring
    have hQall : ∀ m' : ℤ, ∃ z : ℤ, Q.eval (m' : ℚ) = (z : ℚ) := ih Q a hQdeg hQval
    obtain ⟨z0, hz0⟩ := hval 0 (by omega)
    have hz0' : P.eval ((a : ℤ) : ℚ) = (z0 : ℚ) := by
      have : ((a + (0 : ℕ) : ℤ) : ℚ) = ((a : ℤ) : ℚ) := by push_cast; ring
      rw [← this]
      exact hz0
    have hup : ∀ m' : ℤ, a ≤ m' → ∃ z : ℤ, P.eval (m' : ℚ) = (z : ℚ) := by
      intro m' hm'
      induction m', hm' using Int.leInduction with
      | base => exact ⟨z0, hz0'⟩
      | succ n hn ihn =>
        obtain ⟨z1, hz1⟩ := ihn
        obtain ⟨z2, hz2⟩ := hQall n
        refine ⟨z1 + z2, ?_⟩
        -- P(n+1) = P(n) + Q(n)
        have hstep := hQeval ((n : ℤ) : ℚ)
        rw [hz1, hz2] at hstep
        have hcast : ((n + 1 : ℤ) : ℚ) = ((n : ℤ) : ℚ) + 1 := by push_cast; ring
        rw [hcast]
        push_cast
        linarith
    have hdown : ∀ m' : ℤ, m' ≤ a → ∃ z : ℤ, P.eval (m' : ℚ) = (z : ℚ) := by
      intro m' hm'
      induction m', hm' using Int.leInductionDown with
      | base => exact ⟨z0, hz0'⟩
      | pred n hn ihn =>
        obtain ⟨z1, hz1⟩ := ihn
        obtain ⟨z2, hz2⟩ := hQall (n - 1)
        refine ⟨z1 - z2, ?_⟩
        -- P(n-1) = P(n) - Q(n-1)
        have hstep := hQeval (((n - 1 : ℤ) : ℤ) : ℚ)
        have hcast : ((n - 1 : ℤ) : ℚ) + 1 = ((n : ℤ) : ℚ) := by push_cast; ring
        rw [hcast, hz1, hz2] at hstep
        push_cast at hstep ⊢
        linarith
    rcases le_total a m with h | h
    · exact hup m h
    · exact hdown m h

end Polyplets
