/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.King

/-!
# The leading coefficient of `P_k` is `25^k / k!`

`King.lean` proves `T(n, n-k) = P_k(n)·3^(n-1-3k)` with `P_k` of degree at
most `k` (`exists_isDiagonalPoly`). This file fixes the top coefficient, so the
degree is exactly `k`.

The route is the one the recursions themselves suggest. Divide `d_rec` by
`3^H`: the walk-top polynomial `δ_k` satisfies the difference equation
`δ_k(H) - δ_k(H-1) = Σ V(ℓ,j)·3^{-(1+ℓ)}·δ_{k-j}(H-1-ℓ)`. Only the `j = ℓ = 1`
term reaches degree `k-1`, so `k·[X^k]δ_k = (V(1,1)/9)·[X^{k-1}]δ_{k-1}` with
`V(1,1) = 25`, and `[X^0]δ_0 = 1/3` from `d(0,1) = 1`. Hence
`[X^k]δ_k = (25/9)^k/(3·k!)`. The top-row identity `T_of_d` adds only lower-degree terms, and
`P_k(n) = 3^(2k+1)·q_k(n-k)` scales this to `25^k/k!`.

Everything is stated for an arbitrary witness polynomial, not the one
`exists_delta` happens to construct: two polynomials over `ℚ` that agree at every
large natural number are equal (`eq_of_eval_nat_eventually`).
-/

namespace Polyplets

open Polynomial

/-! ## Polynomial lemmas -/

/-- Two rational polynomials agreeing at every natural number from `N` on are
equal. -/
lemma eq_of_eval_nat_eventually {p q : Polynomial ℚ} {N : ℕ}
    (h : ∀ n : ℕ, N ≤ n → p.eval (n : ℚ) = q.eval (n : ℚ)) : p = q := by
  refine eq_of_infinite_eval_eq p q ?_
  refine Set.infinite_of_injective_forall_mem (f := fun i : ℕ => ((N + i : ℕ) : ℚ)) ?_ ?_
  · intro i j hij
    dsimp only at hij
    have : N + i = N + j := by exact_mod_cast hij
    omega
  · intro i
    exact h (N + i) (by omega)

/-- The coefficients of a Taylor shift just below the degree bound: with
`natDegree p ≤ m + 1`, `[X^m] p(X + r) = [X^m] p + r·(m+1)·[X^{m+1}] p`. -/
lemma taylor_coeff_of_natDegree_le {p : Polynomial ℚ} {m : ℕ} (hp : p.natDegree ≤ m + 1)
    (r : ℚ) :
    (taylor r p).coeff m = p.coeff m + r * ((m + 1 : ℚ) * p.coeff (m + 1)) := by
  rw [taylor_coeff]
  have hH : hasseDeriv m p = C (p.coeff m) + C ((m + 1 : ℚ) * p.coeff (m + 1)) * X := by
    ext n
    rw [hasseDeriv_coeff]
    rcases n with _ | _ | n
    · simp
    · simp [Nat.choose_succ_self_right, add_comm]
    · have h0 : p.coeff (n + 2 + m) = 0 :=
        coeff_eq_zero_of_natDegree_lt (by omega)
      simp [h0, coeff_one]
  rw [hH]
  simp only [eval_add, eval_C, eval_mul, eval_X]
  ring

/-- Taylor shift fixes the top coefficient: `natDegree p ≤ m` gives
`[X^m] p(X + r) = [X^m] p`. -/
lemma taylor_coeff_top {p : Polynomial ℚ} {m : ℕ} (hp : p.natDegree ≤ m) (r : ℚ) :
    (taylor r p).coeff m = p.coeff m := by
  rw [taylor_coeff_of_natDegree_le (by omega) r,
    coeff_eq_zero_of_natDegree_lt (show p.natDegree < m + 1 by omega)]
  ring

/-- `p(X - r)` as a Taylor shift. -/
lemma comp_X_sub_C_eq_taylor (p : Polynomial ℚ) (r : ℚ) :
    p.comp (X - C r) = taylor (-r) p := by
  rw [taylor_apply, C_neg, sub_eq_add_neg]

lemma natDegree_C_mul_comp_X_sub_C_le (c r : ℚ) (p : Polynomial ℚ) :
    (C c * p.comp (X - C r)).natDegree ≤ p.natDegree := by
  refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
  rw [natDegree_X_sub_C, mul_one]

/-! ## The walk-top polynomials -/

/-- **Top coefficient of `δ_k`.** Any `δ` of degree `≤ k` with
`d k H = δ(H)·3^H` for all `H ≥ k+1` has `[X^k] δ = (25/9)^k / (3·k!)`. -/
theorem delta_coeff : ∀ (k : ℕ) (δ : Polynomial ℚ), δ.natDegree ≤ k →
    (∀ H : ℕ, k + 1 ≤ H → (d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H) →
    δ.coeff k = (25 / 9 : ℚ) ^ k / (3 * k.factorial) := by
  intro k
  induction k using Nat.strong_induction_on with
  | _ k ih =>
  intro δ hdeg hval
  rcases k with _ | m
  · -- `k = 0`: `δ` is the constant `1/3`, from `d 0 1 = 1`.
    have hC : δ = C (δ.coeff 0) := eq_C_of_natDegree_le_zero hdeg
    have h1 := hval 1 le_rfl
    rw [d_0_1, hC, eval_C] at h1
    rw [hC, coeff_C_zero]
    norm_num at h1 ⊢
    linarith
  -- `k = m + 1`: the difference equation.
  choose δ' hdeg' hval' using exists_delta
  set R : Polynomial ℚ := δ - δ.comp (X - C 1) with hR
  set S : Polynomial ℚ := ∑ j ∈ Finset.Icc 1 (m + 1), ∑ ℓ ∈ Finset.Icc 1 j,
    C ((V ℓ j : ℚ) / 3 ^ (1 + ℓ)) * (δ' (m + 1 - j)).comp (X - C ((1 : ℚ) + ℓ)) with hS
  have hRS : R = S := by
    refine eq_of_eval_nat_eventually (N := m + 3) fun H hH => ?_
    have h3H : (3 : ℚ) ^ H ≠ 0 := pow_ne_zero _ (by norm_num)
    refine mul_right_cancel₀ h3H ?_
    have hRe : R.eval (H : ℚ) = δ.eval (H : ℚ) - δ.eval ((H : ℚ) - 1) := by
      simp only [hR, eval_sub, eval_comp, eval_X, eval_C]
    have hSe : S.eval (H : ℚ) = ∑ j ∈ Finset.Icc 1 (m + 1), ∑ ℓ ∈ Finset.Icc 1 j,
        (V ℓ j : ℚ) / 3 ^ (1 + ℓ) * (δ' (m + 1 - j)).eval ((H : ℚ) - (1 + ℓ)) := by
      simp only [hS, eval_finsetSum, eval_mul, eval_C, eval_comp, eval_sub, eval_X]
    rw [hRe, hSe, Finset.sum_mul]
    have hd : (d (m + 1) H : ℚ) = 3 * d (m + 1) (H - 1) +
        ∑ j ∈ Finset.Icc 1 (m + 1), ∑ ℓ ∈ Finset.Icc 1 j,
          (V ℓ j : ℚ) * d (m + 1 - j) (H - 1 - ℓ) := by
      exact_mod_cast d_rec (m + 1) H (by omega)
    have e1 := hval H (by omega)
    have e2 := hval (H - 1) (by omega)
    have hc1 : ((H - 1 : ℕ) : ℚ) = (H : ℚ) - 1 := by
      rw [Nat.cast_sub (by omega)]; push_cast; ring
    have hpow : (3 : ℚ) ^ H = 3 * 3 ^ (H - 1) := by
      rw [← pow_succ']; congr 1; omega
    rw [hc1] at e2
    calc (δ.eval (H : ℚ) - δ.eval ((H : ℚ) - 1)) * 3 ^ H
        = (d (m + 1) H : ℚ) - 3 * d (m + 1) (H - 1) := by
          linear_combination (-1 : ℚ) * e1 + 3 * e2 - δ.eval ((H : ℚ) - 1) * hpow
      _ = ∑ j ∈ Finset.Icc 1 (m + 1), ∑ ℓ ∈ Finset.Icc 1 j,
          (V ℓ j : ℚ) * d (m + 1 - j) (H - 1 - ℓ) := by rw [hd]; ring
      _ = ∑ j ∈ Finset.Icc 1 (m + 1), (∑ ℓ ∈ Finset.Icc 1 j,
          (V ℓ j : ℚ) / 3 ^ (1 + ℓ) * (δ' (m + 1 - j)).eval ((H : ℚ) - (1 + ℓ))) * 3 ^ H := by
          refine Finset.sum_congr rfl fun j hj => ?_
          rw [Finset.sum_mul]
          refine Finset.sum_congr rfl fun ℓ hℓ => ?_
          rw [Finset.mem_Icc] at hj hℓ
          have e3 := hval' (m + 1 - j) (H - 1 - ℓ) (by omega)
          have hc : ((H - 1 - ℓ : ℕ) : ℚ) = (H : ℚ) - (1 + ℓ) := by
            rw [Nat.sub_sub, Nat.cast_sub (by omega)]; push_cast; ring
          have hpow2 : (3 : ℚ) ^ H = 3 ^ (H - 1 - ℓ) * 3 ^ (1 + ℓ) := by
            rw [← pow_add]; congr 1; omega
          have h3 : (3 : ℚ) ^ (1 + ℓ) ≠ 0 := pow_ne_zero _ (by norm_num)
          rw [e3, hc, hpow2]
          field_simp
  -- Coefficient `m` on both sides.
  have hRc : R.coeff m = (m + 1 : ℚ) * δ.coeff (m + 1) := by
    rw [hR, coeff_sub, comp_X_sub_C_eq_taylor, taylor_coeff_of_natDegree_le hdeg]
    ring
  have hSc : S.coeff m = 25 / 9 * ((25 / 9 : ℚ) ^ m / (3 * m.factorial)) := by
    rw [hS, finsetSum_coeff]
    rw [Finset.sum_eq_single_of_mem 1 (by simp)]
    · rw [Finset.Icc_self, Finset.sum_singleton, coeff_C_mul, comp_X_sub_C_eq_taylor]
      have hm : m + 1 - 1 = m := Nat.add_sub_cancel m 1
      rw [hm, taylor_coeff_top (hdeg' m), V_1_1, ih m (by omega) (δ' m) (hdeg' m) (hval' m)]
      norm_num
    · intro j hj hj1
      rw [Finset.mem_Icc] at hj
      rw [finsetSum_coeff]
      refine Finset.sum_eq_zero fun ℓ _ => ?_
      refine coeff_eq_zero_of_natDegree_lt ?_
      refine lt_of_le_of_lt (natDegree_C_mul_comp_X_sub_C_le _ _ _) ?_
      have := hdeg' (m + 1 - j)
      omega
  have hkey : (m + 1 : ℚ) * δ.coeff (m + 1) = 25 / 9 * ((25 / 9 : ℚ) ^ m / (3 * m.factorial)) := by
    rw [← hRc, ← hSc, hRS]
  have hfac : ((m + 1).factorial : ℚ) = (m + 1) * m.factorial := by
    push_cast [Nat.factorial_succ]; ring
  have hkey' : (m + 1 : ℚ) * δ.coeff (m + 1) * (3 * m.factorial) = 25 / 9 * (25 / 9 : ℚ) ^ m := by
    rw [hkey]
    have hmf : (m.factorial : ℚ) ≠ 0 := by positivity
    field_simp
  rw [hfac, pow_succ, eq_div_iff (by positivity)]
  linear_combination hkey'

/-! ## Transfer to the diagonal polynomial -/

/-- **The leading coefficient of `P_k` is `25^k/k!`.** For any `P` satisfying
the diagonal law at level `k`. -/
theorem IsDiagonalPoly.coeff_eq {k : ℕ} {P : Polynomial ℚ} (hP : IsDiagonalPoly k P) :
    P.coeff k = 25 ^ k / k.factorial := by
  have hdeg := hP.natDegree_le
  choose δ' hdeg' hval' using exists_delta
  set L : Polynomial ℚ := P.comp (X + C (k : ℚ)) with hL
  set Rt : Polynomial ℚ := C ((3 : ℚ) ^ (2 * k + 1)) * (δ' k +
    ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
      C ((Vt ℓ j : ℚ) / 3 ^ ℓ) * (δ' (k - j)).comp (X - C (ℓ : ℚ))) with hRt
  have hLR : L = Rt := by
    refine eq_of_eval_nat_eventually (N := k + 1) fun H hH => ?_
    have h3H : (3 : ℚ) ^ H ≠ 0 := pow_ne_zero _ (by norm_num)
    refine mul_right_cancel₀ h3H ?_
    have hLe : L.eval (H : ℚ) = P.eval ((H : ℚ) + k) := by
      simp only [hL, eval_comp, eval_add, eval_X, eval_C]
    have hRe : Rt.eval (H : ℚ) = 3 ^ (2 * k + 1) * ((δ' k).eval (H : ℚ) +
        ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
          (Vt ℓ j : ℚ) / 3 ^ ℓ * (δ' (k - j)).eval ((H : ℚ) - ℓ)) := by
      simp only [hRt, eval_mul, eval_C, eval_add, eval_finsetSum, eval_comp, eval_sub, eval_X]
    rw [hLe, hRe]
    -- the law at `n = H + k`, cleared of `zpow`
    have hprod : P.eval ((H : ℚ) + k) * 3 ^ H = 3 ^ (2 * k + 1) * (T (H + k) H : ℚ) := by
      have h := hP (H + k) (by omega)
      rw [Nat.add_sub_cancel] at h
      push_cast at h
      have hz : (3 : ℚ) ^ (((H : ℤ) + k) - 1 - 3 * k) = 3 ^ H / 3 ^ (2 * k + 1) := by
        rw [show ((H : ℤ) + k) - 1 - 3 * k = (H : ℤ) - ((2 * k + 1 : ℕ) : ℤ) by push_cast; ring,
          zpow_sub₀ (by norm_num), zpow_natCast, zpow_natCast]
      rw [h, hz]
      field_simp
    have hc : (T (H + k) H : ℚ) = d k H +
        ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) * d (k - j) (H - ℓ) := by
      exact_mod_cast T_of_d k H hH
    have hsum : ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, (Vt ℓ j : ℚ) * d (k - j) (H - ℓ)
        = (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) / 3 ^ ℓ * (δ' (k - j)).eval ((H : ℚ) - ℓ)) * 3 ^ H := by
      rw [Finset.sum_mul]
      refine Finset.sum_congr rfl fun j hj => ?_
      rw [Finset.sum_mul]
      refine Finset.sum_congr rfl fun ℓ hℓ => ?_
      rw [Finset.mem_Icc] at hj hℓ
      have e3 := hval' (k - j) (H - ℓ) (by omega)
      have hcast : ((H - ℓ : ℕ) : ℚ) = (H : ℚ) - ℓ := by rw [Nat.cast_sub (by omega)]
      have hpow : (3 : ℚ) ^ H = 3 ^ (H - ℓ) * 3 ^ ℓ := by rw [← pow_add]; congr 1; omega
      have h3 : (3 : ℚ) ^ ℓ ≠ 0 := pow_ne_zero _ (by norm_num)
      rw [e3, hcast, hpow]
      field_simp
    rw [hprod, hc, hval' k H hH, hsum]
    ring
  have hLc : L.coeff k = P.coeff k := by
    rw [hL, ← taylor_apply, taylor_coeff_top hdeg]
  have hRc : Rt.coeff k = 3 ^ (2 * k + 1) * ((25 / 9 : ℚ) ^ k / (3 * k.factorial)) := by
    rw [hRt, coeff_C_mul, coeff_add, finsetSum_coeff,
      delta_coeff k (δ' k) (hdeg' k) (hval' k)]
    rw [Finset.sum_eq_zero, add_zero]
    intro j hj
    rw [Finset.mem_Icc] at hj
    rw [finsetSum_coeff]
    refine Finset.sum_eq_zero fun ℓ _ => ?_
    refine coeff_eq_zero_of_natDegree_lt ?_
    refine lt_of_le_of_lt (natDegree_C_mul_comp_X_sub_C_le _ _ _) ?_
    have := hdeg' (k - j)
    omega
  rw [← hLc, hLR, hRc, pow_succ, pow_mul, div_pow]
  have hkf : (k.factorial : ℚ) ≠ 0 := by positivity
  field_simp
  ring

/-- **`P_k` has degree exactly `k`**: its top coefficient `25^k/k!` is not zero. -/
theorem IsDiagonalPoly.natDegree_eq {k : ℕ} {P : Polynomial ℚ} (hP : IsDiagonalPoly k P) :
    P.natDegree = k :=
  natDegree_eq_of_le_of_coeff_ne_zero hP.natDegree_le (by rw [hP.coeff_eq]; positivity)

/-! ## The diagonal polynomial from `k` values and the leading coefficient -/

/-- **`P_k` is fixed by rows `2k+1 … 3k`.** A polynomial of degree `≤ k` with
leading coefficient `25^k/k!` that matches `T` on those `k` rows satisfies
the diagonal law at level `k`. One row fewer than `RowLocal.isDiagonalPoly_of_eval`,
which needs `k + 1` points because it does not know the leading coefficient. -/
theorem isDiagonalPoly_of_coeff_of_eval_Icc (k : ℕ) (p : Polynomial ℚ) (hp : p.natDegree ≤ k)
    (hlc : p.coeff k = 25 ^ k / k.factorial)
    (hpts : ∀ n ∈ Finset.Icc (2 * k + 1) (3 * k),
      p.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ)) :
    IsDiagonalPoly k p := by
  obtain ⟨P, hPdeg, hP⟩ := exists_isDiagonalPoly k
  have hPlc : P.coeff k = 25 ^ k / k.factorial := hP.coeff_eq
  suffices hpP : p = P by rw [hpP]; exact hP
  rcases k with _ | m
  · rw [eq_C_of_natDegree_le_zero hp, eq_C_of_natDegree_le_zero hPdeg, hlc, hPlc]
  rw [← sub_eq_zero]
  have hdeg : (p - P).natDegree ≤ m := by
    rw [natDegree_le_iff_coeff_eq_zero]
    intro N hN
    rw [coeff_sub]
    rcases Nat.lt_or_ge (m + 1) N with h | h
    · rw [coeff_eq_zero_of_natDegree_lt (by omega), coeff_eq_zero_of_natDegree_lt (by omega),
        sub_zero]
    · have hN' : N = m + 1 := by omega
      rw [hN', hlc, hPlc, sub_self]
  refine eq_zero_of_natDegree_lt_card_of_eval_eq_zero' (p - P)
    ((Finset.Icc (2 * (m + 1) + 1) (3 * (m + 1))).image (Nat.cast : ℕ → ℚ)) ?_ ?_
  · intro x hx
    obtain ⟨n, hn, rfl⟩ := Finset.mem_image.mp hx
    have hn' := Finset.mem_Icc.mp hn
    rw [eval_sub, hpts n hn, hP.eval_onset hn'.1 (by omega), sub_self]
  · rw [Finset.card_image_of_injective _ Nat.cast_injective, Nat.card_Icc]
    omega

end Polyplets
