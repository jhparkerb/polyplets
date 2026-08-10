/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.RingTheory.PowerSeries.Inverse

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
  sorry

/-- Early coefficients are stable under longer runs of the recursion. -/
theorem sqrtList_getD_mono (t : ℕ → ℚ) {m n k : ℕ} (h : m ≤ n) (hk : k ≤ m) :
    (sqrtList t n).getD k 0 = (sqrtList t m).getD k 0 := by
  sorry

@[simp] theorem sqrtCoef_zero (t : ℕ → ℚ) : sqrtCoef t 0 = 1 := by
  sorry

theorem sqrtCoef_one (t : ℕ → ℚ) : sqrtCoef t 1 = t 1 / 2 := by
  sorry

/-- The recursion squares to its target (any `t` with `t 0 = 1`). -/
theorem sqrt_sq (t : ℕ → ℚ) (h0 : t 0 = 1) :
    PowerSeries.mk (sqrtCoef t) * PowerSeries.mk (sqrtCoef t) =
      PowerSeries.mk t := by
  sorry

theorem mk_aaC : (PowerSeries.mk aaC : PowerSeries ℚ) =
    1 - 2 * X - 3 * X ^ 2 := by
  sorry

theorem mk_bbC : (PowerSeries.mk bbC : PowerSeries ℚ) =
    1 + 2 * X - 3 * X ^ 2 := by
  sorry

theorem A_sq : A * A = 1 - 2 * X - 3 * X ^ 2 := by
  sorry

theorem B_sq : B * B = 1 + 2 * X - 3 * X ^ 2 := by
  sorry

@[simp] theorem constantCoeff_A : constantCoeff A = 1 := by
  sorry

@[simp] theorem constantCoeff_B : constantCoeff B = 1 := by
  sorry

/-! ## The small kernel roots -/

/-- `u₁ = ((1−X) − A)/(2X)`: the numerator vanishes to order 2, so the
shift by one lands in `X·ℚ⟦X⟧`. -/
noncomputable def u1 : PowerSeries ℚ :=
  PowerSeries.mk fun n => (2 : ℚ)⁻¹ * (coeff (n + 1)) (1 - X - A)

/-- `u₂ = (−(1+X) + B)/(2X)`. -/
noncomputable def u2 : PowerSeries ℚ :=
  PowerSeries.mk fun n => (2 : ℚ)⁻¹ * (coeff (n + 1)) (B - 1 - X)

@[simp] theorem constantCoeff_u1 : constantCoeff u1 = 0 := by
  sorry

@[simp] theorem constantCoeff_u2 : constantCoeff u2 = 0 := by
  sorry

/-- The defining product: `2X·u₁ = 1 − X − A`. -/
theorem u1_def : 2 * X * u1 = 1 - X - A := by
  sorry

/-- The defining product: `2X·u₂ = B − 1 − X`. -/
theorem u2_def : 2 * X * u2 = B - 1 - X := by
  sorry

/-- The linear kernel relation on the `+` branch: `u₁ = X(1+u₁+u₁²)`. -/
theorem u1_lin : u1 = X * (1 + u1 + u1 ^ 2) := by
  sorry

/-- The linear kernel relation on the `−` branch: `u₂ = −X(1+u₂+u₂²)`. -/
theorem u2_lin : u2 = -(X * (1 + u2 + u2 ^ 2)) := by
  sorry

/-- `D(u₁) = 0`, squared form. -/
theorem u1_kernel : u1 ^ 2 = X ^ 2 * (1 + u1 + u1 ^ 2) ^ 2 := by
  sorry

/-- `D(u₂) = 0`, squared form. -/
theorem u2_kernel : u2 ^ 2 = X ^ 2 * (1 + u2 + u2 ^ 2) ^ 2 := by
  sorry

/-! ## The tail units `1/(1−uᵢ)` -/

/-- `w₁ = (1−u₁)⁻¹`, the geometric tail at the first root. -/
noncomputable def w1 : PowerSeries ℚ := (1 - u1)⁻¹

/-- `w₂ = (1−u₂)⁻¹`. -/
noncomputable def w2 : PowerSeries ℚ := (1 - u2)⁻¹

theorem one_sub_u1_mul_w1 : (1 - u1) * w1 = 1 := by
  sorry

theorem one_sub_u2_mul_w2 : (1 - u2) * w2 = 1 := by
  sorry

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
