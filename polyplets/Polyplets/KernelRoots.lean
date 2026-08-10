/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.RingTheory.PowerSeries.Inverse
import Mathlib.RingTheory.PowerSeries.NoZeroDivisors
import Mathlib.Data.List.GetD

/-!
# Notary piece K, module 3: the kernel's square roots and small roots

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`. The kernel of the
gap walk is `D(u) = u² − y(1+u+u²)²` with `y = s²`; its two small roots are

    u₁ = ((1−s) − A)/(2s),   A = √(1−2s−3s²),
    u₂ = (−(1+s) + B)/(2s),  B = √(1+2s−3s²),

honest elements of `s·ℚ⟦s⟧`. This module builds them and proves their
defining identities, with no walk and no summation theory:

* `sqrtList`/`sqrtCoef` — the square-root coefficient recursion
  `a₀ = 1`, `aₙ = (tₙ − Σ_{0<i<n} aᵢ·aₙ₋ᵢ)/2` (Mathlib's `Binomial.lean`
  exports nothing usable on this toolchain; the hand-rolled recursion is
  also exactly what the finite certificates of wave K-δ will evaluate);
* `A`, `B` with `A² = 1−2X−3X²`, `B² = 1+2X−3X²`, constant term 1;
* `u1`, `u2` as shifted series with `2X·u1 = 1−X−A`, `2X·u2 = B−1−X`;
* the **linear** kernel relations `u1 = X(1+u1+u1²)`,
  `u2 = −X(1+u2+u2²)` (each root picks a sign branch; squaring gives
  `D(uᵢ) = 0`), plus the squared form;
* the tail units `w1 = (1−u1)⁻¹`, `w2 = (1−u2)⁻¹`.

Numerically pre-verified: `experiments/notary_k_measure.py` m4 checks the
recursions square correctly, the shifted series satisfy the kernel
identity to `s`-order 51, and both agree with the sympy roots of
`severance_w2_kernel.py` (`build/notary_k_measure.log`).

## Proof recipes

`sqrt_sq`: coefficient `n` of the square is `Σ_{i≤n} aᵢaₙ₋ᵢ`; peel the two
end terms (`Finset.sum_range_succ` at both ends, or `Finset.sum_Ioo` after
splitting `{0}` and `{n}`), then the recursion cancels the middle. The
stability lemma `sqrtList_getD_mono` (a longer run of the recursion agrees
on early coefficients) makes `sqrtCoef` well-behaved; prove it by induction
on the length difference, `List.getD_append`.

`u1_lin`: from `2X·u1 = 1−X−A` and `A² = 1−2X−3X²`: expand
`(1−X−2X·u1)² = 1−2X−3X²` and cancel; the resulting identity
`4X²·(1+u1+u1²) = 4X·u1` cancels one `X` because `ℚ⟦X⟧` is a domain
(`mul_left_cancel₀`, `X ≠ 0`). Same shape for `u2` with the opposite sign.

The definitions of `u1`, `u2` are coefficient shifts; their defining
products need `coeff 0` and `coeff 1` of `1−X−A` (resp. `B−1−X`) to vanish
— that is `sqrtCoef t 0 = 1` and `sqrtCoef t 1 = t 1 / 2`.
-/

namespace Polyplets
namespace Kernel

open PowerSeries

/-! ## Square roots by coefficient recursion -/

/-- Coefficients `0..n` of `√(series with coefficients t)`, `t 0 = 1`:
`a₀ = 1`, `aₙ = (tₙ − Σ_{0<i<n} aᵢ·aₙ₋ᵢ)/2`. -/
def sqrtList (t : ℕ → ℚ) : ℕ → List ℚ
  | 0 => [1]
  | n + 1 =>
      let p := sqrtList t n
      p ++ [(t (n + 1) -
        ∑ i ∈ Finset.Ioo 0 (n + 1), p.getD i 0 * p.getD (n + 1 - i) 0) / 2]

/-- Coefficient `n` of the square root. -/
def sqrtCoef (t : ℕ → ℚ) (n : ℕ) : ℚ := (sqrtList t n).getD n 0

/-- `1 − 2s − 3s²`, as a coefficient function. -/
def aaC : ℕ → ℚ
  | 0 => 1
  | 1 => -2
  | 2 => -3
  | _ + 3 => 0

/-- `1 + 2s − 3s²`, as a coefficient function. -/
def bbC : ℕ → ℚ
  | 0 => 1
  | 1 => 2
  | 2 => -3
  | _ + 3 => 0

/-- `A = √(1−2s−3s²) = √((1−3s)(1+s))`. -/
noncomputable def A : PowerSeries ℚ := PowerSeries.mk (sqrtCoef aaC)

/-- `B = √(1+2s−3s²) = √((1+3s)(1−s))`. -/
noncomputable def B : PowerSeries ℚ := PowerSeries.mk (sqrtCoef bbC)

@[simp] theorem sqrtList_length (t : ℕ → ℚ) (n : ℕ) :
    (sqrtList t n).length = n + 1 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [sqrtList, List.length_append, ih]

/-- Early coefficients are stable under longer runs of the recursion. -/
theorem sqrtList_getD_mono (t : ℕ → ℚ) {m n k : ℕ} (h : m ≤ n) (hk : k ≤ m) :
    (sqrtList t n).getD k 0 = (sqrtList t m).getD k 0 := by
  induction n with
  | zero =>
      have : m = 0 := Nat.le_zero.mp h
      subst this; rfl
  | succ n ih =>
      rcases Nat.lt_or_ge m (n + 1) with h' | h'
      · have hmn : m ≤ n := Nat.lt_succ_iff.mp h'
        have hkn : k < (sqrtList t n).length := by
          rw [sqrtList_length]; omega
        change (sqrtList t n ++ [_]).getD k 0 = _
        rw [List.getD_append _ _ _ _ hkn]
        exact ih hmn
      · have : m = n + 1 := le_antisymm h h'
        subst this; rfl

@[simp] theorem sqrtCoef_zero (t : ℕ → ℚ) : sqrtCoef t 0 = 1 := by
  rfl

theorem sqrtCoef_one (t : ℕ → ℚ) : sqrtCoef t 1 = t 1 / 2 := by
  change (sqrtList t 1).getD 1 0 = t 1 / 2
  change (sqrtList t 0 ++ [(t 1 - ∑ i ∈ Finset.Ioo 0 1,
    (sqrtList t 0).getD i 0 * (sqrtList t 0).getD (1 - i) 0) / 2]).getD 1 0 = t 1 / 2
  have hIoo : Finset.Ioo 0 1 = (∅ : Finset ℕ) := by decide
  simp [sqrtList, hIoo]

/-- The recursion equation at the `sqrtCoef` level, unfolded from `sqrtList`. -/
private theorem sqrtCoef_succ (t : ℕ → ℚ) (n : ℕ) :
    sqrtCoef t (n + 1) = (t (n + 1) -
      ∑ i ∈ Finset.Ioo 0 (n + 1), sqrtCoef t i * sqrtCoef t (n + 1 - i)) / 2 := by
  have hlen : (sqrtList t n).length = n + 1 := sqrtList_length t n
  have hstep : sqrtCoef t (n + 1) =
      (sqrtList t n ++ [(t (n + 1) -
        ∑ i ∈ Finset.Ioo 0 (n + 1),
          (sqrtList t n).getD i 0 * (sqrtList t n).getD (n + 1 - i) 0) / 2]).getD (n + 1) 0 :=
    rfl
  rw [hstep, List.getD_append_right _ _ _ _ (by omega), hlen]
  have hz : n + 1 - (n + 1) = 0 := by omega
  rw [hz, List.getD_cons_zero]
  have hsum : ∑ i ∈ Finset.Ioo 0 (n + 1),
      (sqrtList t n).getD i 0 * (sqrtList t n).getD (n + 1 - i) 0 =
      ∑ i ∈ Finset.Ioo 0 (n + 1), sqrtCoef t i * sqrtCoef t (n + 1 - i) := by
    refine Finset.sum_congr rfl fun i hi => ?_
    simp only [Finset.mem_Ioo] at hi
    show (sqrtList t n).getD i 0 * (sqrtList t n).getD (n + 1 - i) 0 =
      sqrtCoef t i * sqrtCoef t (n + 1 - i)
    rw [show (sqrtList t n).getD i 0 = sqrtCoef t i from
        sqrtList_getD_mono t (by omega : i ≤ n) (le_refl i),
      show (sqrtList t n).getD (n + 1 - i) 0 = sqrtCoef t (n + 1 - i) from
        sqrtList_getD_mono t (by omega : n + 1 - i ≤ n) (le_refl (n + 1 - i))]
  rw [hsum]

/-- The recursion squares to its target (any `t` with `t 0 = 1`). -/
theorem sqrt_sq (t : ℕ → ℚ) (h0 : t 0 = 1) :
    PowerSeries.mk (sqrtCoef t) * PowerSeries.mk (sqrtCoef t) =
      PowerSeries.mk t := by
  ext n
  rw [PowerSeries.coeff_mul, PowerSeries.coeff_mk]
  simp only [PowerSeries.coeff_mk]
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk
    (fun p => sqrtCoef t p.1 * sqrtCoef t p.2)]
  induction n with
  | zero => simp [sqrtCoef_zero, h0]
  | succ m ih =>
      rw [Finset.sum_range_succ (fun k => sqrtCoef t k * sqrtCoef t (m + 1 - k)),
        Finset.sum_range_succ' (fun k => sqrtCoef t k * sqrtCoef t (m + 1 - k))]
      have hzero1 : m + 1 - 0 = m + 1 := by omega
      have hzero2 : m + 1 - (m + 1) = 0 := by omega
      rw [hzero1, hzero2, sqrtCoef_zero]
      have hIcoRange : ∑ i ∈ Finset.Ico 1 (m + 1), sqrtCoef t i * sqrtCoef t (m + 1 - i) =
          ∑ k ∈ Finset.range m, sqrtCoef t (k + 1) * sqrtCoef t (m + 1 - (k + 1)) := by
        rw [Finset.sum_Ico_eq_sum_range]
        have hm1 : m + 1 - 1 = m := by omega
        rw [hm1]
        refine Finset.sum_congr rfl fun k _ => ?_
        rw [Nat.add_comm 1 k]
      have hIoo : Finset.Ico 1 (m + 1) = Finset.Ioo 0 (m + 1) := by
        ext x; simp only [Finset.mem_Ico, Finset.mem_Ioo]; omega
      rw [← hIcoRange, hIoo]
      have hS : (∑ i ∈ Finset.Ioo 0 (m + 1), sqrtCoef t i * sqrtCoef t (m + 1 - i)) =
          t (m + 1) - 2 * sqrtCoef t (m + 1) := by
        rw [sqrtCoef_succ t m]; ring
      rw [hS]
      ring

theorem mk_aaC : (PowerSeries.mk aaC : PowerSeries ℚ) =
    1 - 2 * X - 3 * X ^ 2 := by
  ext n
  rw [PowerSeries.coeff_mk, show (2 : PowerSeries ℚ) = C 2 from (map_ofNat C 2).symm,
    show (3 : PowerSeries ℚ) = C 3 from (map_ofNat C 3).symm]
  simp only [map_sub, coeff_one, coeff_C_mul, coeff_X, coeff_X_pow]
  rcases n with _ | _ | _ | n
  · simp [aaC]
  · simp [aaC]
  · simp [aaC]
  · simp [aaC]

theorem mk_bbC : (PowerSeries.mk bbC : PowerSeries ℚ) =
    1 + 2 * X - 3 * X ^ 2 := by
  ext n
  rw [PowerSeries.coeff_mk, show (2 : PowerSeries ℚ) = C 2 from (map_ofNat C 2).symm,
    show (3 : PowerSeries ℚ) = C 3 from (map_ofNat C 3).symm]
  simp only [map_sub, map_add, coeff_one, coeff_C_mul, coeff_X, coeff_X_pow]
  rcases n with _ | _ | _ | n
  · simp [bbC]
  · simp [bbC]
  · simp [bbC]
  · simp [bbC]

theorem A_sq : A * A = 1 - 2 * X - 3 * X ^ 2 := by
  rw [A, sqrt_sq aaC rfl, mk_aaC]

theorem B_sq : B * B = 1 + 2 * X - 3 * X ^ 2 := by
  rw [B, sqrt_sq bbC rfl, mk_bbC]

@[simp] theorem constantCoeff_A : constantCoeff A = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, A, PowerSeries.coeff_mk, sqrtCoef_zero]

@[simp] theorem constantCoeff_B : constantCoeff B = 1 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, B, PowerSeries.coeff_mk, sqrtCoef_zero]

/-! ## The small kernel roots -/

/-- `u₁ = ((1−X) − A)/(2X)`: the numerator vanishes to order 2, so the
shift by one lands in `X·ℚ⟦X⟧`. -/
noncomputable def u1 : PowerSeries ℚ :=
  PowerSeries.mk fun n => (2 : ℚ)⁻¹ * (coeff (n + 1)) (1 - X - A)

/-- `u₂ = (−(1+X) + B)/(2X)`. -/
noncomputable def u2 : PowerSeries ℚ :=
  PowerSeries.mk fun n => (2 : ℚ)⁻¹ * (coeff (n + 1)) (B - 1 - X)

@[simp] theorem constantCoeff_u1 : constantCoeff u1 = 0 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, u1, PowerSeries.coeff_mk]
  have h1 : (coeff (1 : ℕ)) (1 - X - A : PowerSeries ℚ) = 0 := by
    simp only [map_sub, coeff_one, coeff_one_X, A, PowerSeries.coeff_mk]
    rw [sqrtCoef_one]
    norm_num [aaC]
  rw [h1]; ring

@[simp] theorem constantCoeff_u2 : constantCoeff u2 = 0 := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, u2, PowerSeries.coeff_mk]
  have h1 : (coeff (1 : ℕ)) (B - 1 - X : PowerSeries ℚ) = 0 := by
    simp only [map_sub, coeff_one, coeff_one_X, B, PowerSeries.coeff_mk]
    rw [sqrtCoef_one]
    norm_num [bbC]
  rw [h1]; ring

/-- The defining product: `2X·u₁ = 1 − X − A`. -/
theorem u1_def : 2 * X * u1 = 1 - X - A := by
  ext n
  rcases n with _ | n
  · simp [hA]
  · rw [show (2 : PowerSeries ℚ) * X * u1 = X * (2 * u1) from by ring, coeff_succ_X_mul, u1,
      show (2 : PowerSeries ℚ) = C 2 from (map_ofNat C 2).symm, coeff_C_mul, coeff_mk]
    ring
  where hA : constantCoeff A = 1 := constantCoeff_A

/-- The defining product: `2X·u₂ = B − 1 − X`. -/
theorem u2_def : 2 * X * u2 = B - 1 - X := by
  ext n
  rcases n with _ | n
  · simp [hB]
  · rw [show (2 : PowerSeries ℚ) * X * u2 = X * (2 * u2) from by ring, coeff_succ_X_mul, u2,
      show (2 : PowerSeries ℚ) = C 2 from (map_ofNat C 2).symm, coeff_C_mul, coeff_mk]
    ring
  where hB : constantCoeff B = 1 := constantCoeff_B

/-- The linear kernel relation on the `+` branch: `u₁ = X(1+u₁+u₁²)`. -/
theorem u1_lin : u1 = X * (1 + u1 + u1 ^ 2) := by
  have hA : A = 1 - X - 2 * X * u1 := by linear_combination u1_def
  have key : (1 - X - 2 * X * u1) ^ 2 = 1 - 2 * X - 3 * X ^ 2 := by
    rw [← hA, pow_two]; exact A_sq
  have h4 : (4 : PowerSeries ℚ) * X * (X * (1 + u1 + u1 ^ 2) - u1) = 0 := by
    linear_combination key
  have h4ne : (4 : PowerSeries ℚ) ≠ 0 := by
    intro h
    have h' := congrArg constantCoeff h
    rw [show constantCoeff (4 : PowerSeries ℚ) = 4 from map_ofNat constantCoeff 4,
      map_zero] at h'
    norm_num at h'
  have hXne : (X : PowerSeries ℚ) ≠ 0 := X_ne_zero
  have h4Xne : (4 : PowerSeries ℚ) * X ≠ 0 := mul_ne_zero h4ne hXne
  rw [show (4 : PowerSeries ℚ) * X * (X * (1 + u1 + u1 ^ 2) - u1) =
      (4 * X) * (X * (1 + u1 + u1 ^ 2) - u1) from by ring] at h4
  rcases mul_eq_zero.mp h4 with h | h
  · exact absurd h h4Xne
  · linear_combination -h

/-- The linear kernel relation on the `−` branch: `u₂ = −X(1+u₂+u₂²)`. -/
theorem u2_lin : u2 = -(X * (1 + u2 + u2 ^ 2)) := by
  have hB : B = 1 + X + 2 * X * u2 := by linear_combination -u2_def
  have key : (1 + X + 2 * X * u2) ^ 2 = 1 + 2 * X - 3 * X ^ 2 := by
    rw [← hB, pow_two]; exact B_sq
  have h4 : (4 : PowerSeries ℚ) * X * (X * (1 + u2 + u2 ^ 2) + u2) = 0 := by
    linear_combination key
  have h4ne : (4 : PowerSeries ℚ) ≠ 0 := by
    intro h
    have h' := congrArg constantCoeff h
    rw [show constantCoeff (4 : PowerSeries ℚ) = 4 from map_ofNat constantCoeff 4,
      map_zero] at h'
    norm_num at h'
  have hXne : (X : PowerSeries ℚ) ≠ 0 := X_ne_zero
  have h4Xne : (4 : PowerSeries ℚ) * X ≠ 0 := mul_ne_zero h4ne hXne
  rw [show (4 : PowerSeries ℚ) * X * (X * (1 + u2 + u2 ^ 2) + u2) =
      (4 * X) * (X * (1 + u2 + u2 ^ 2) + u2) from by ring] at h4
  rcases mul_eq_zero.mp h4 with h | h
  · exact absurd h h4Xne
  · linear_combination h

/-- `D(u₁) = 0`, squared form. -/
theorem u1_kernel : u1 ^ 2 = X ^ 2 * (1 + u1 + u1 ^ 2) ^ 2 := by
  calc u1 ^ 2 = (X * (1 + u1 + u1 ^ 2)) ^ 2 := congrArg (· ^ 2) u1_lin
    _ = X ^ 2 * (1 + u1 + u1 ^ 2) ^ 2 := by ring

/-- `D(u₂) = 0`, squared form. -/
theorem u2_kernel : u2 ^ 2 = X ^ 2 * (1 + u2 + u2 ^ 2) ^ 2 := by
  calc u2 ^ 2 = (-(X * (1 + u2 + u2 ^ 2))) ^ 2 := congrArg (· ^ 2) u2_lin
    _ = X ^ 2 * (1 + u2 + u2 ^ 2) ^ 2 := by ring

/-! ## The tail units `1/(1−uᵢ)` -/

/-- `w₁ = (1−u₁)⁻¹`, the geometric tail at the first root. -/
noncomputable def w1 : PowerSeries ℚ := (1 - u1)⁻¹

/-- `w₂ = (1−u₂)⁻¹`. -/
noncomputable def w2 : PowerSeries ℚ := (1 - u2)⁻¹

theorem one_sub_u1_mul_w1 : (1 - u1) * w1 = 1 := by
  refine PowerSeries.mul_inv_cancel _ ?_
  rw [map_sub, constantCoeff_u1, map_one]
  norm_num

theorem one_sub_u2_mul_w2 : (1 - u2) * w2 = 1 := by
  refine PowerSeries.mul_inv_cancel _ ?_
  rw [map_sub, constantCoeff_u2, map_one]
  norm_num

/-- `D′(u) = 2u − 2X²(1+u+u²)(1+2u)`: the kernel derivative, as a
polynomial expression — consumed by the cleared P-side equations of wave
K-γ. No lemmas here; it rides along with the roots. -/
noncomputable def dP (u : PowerSeries ℚ) : PowerSeries ℚ :=
  2 * u - 2 * X ^ 2 * (1 + u + u ^ 2) * (1 + 2 * u)

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.Kernel.u1_lin' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms u1_lin

/--
info: 'Polyplets.Kernel.sqrt_sq' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms sqrt_sq

end Kernel
end Polyplets
