/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Staircase.Series
import Polyplets.Weights

/-!
# Mu: the root series `ν` and the multiplier `μ`

The coefficient-form root/multiplier of the staircase
(`docs/proofs/grand-form.md`). This layer sits on the convolution toolkit
of `Series.lean` and the cluster weights of `Weights.lean`.

* `vGuard ℓ` — the interior weights `V ℓ ·` as a `y`-sequence, guarded to vanish
  below index `ℓ` (and identically for `ℓ = 0`).
* `nu` — the root series `z*` of `docs/proofs/grand-form.md`: `ν₀ = 1/3` and,
  for `m ≥ 1`, the unique coefficient-by-coefficient solution of the root
  equation `eps = 3·ν + Σ_ℓ v_ℓ ∗ ν^{∗(ℓ+1)}`. A prefix-guarded well-founded
  recursion (the RHS reads `ν` only strictly below the index being defined).
* `nu_unfold` / `root` — de-guarding and the root identity in closed form.
* `mu` — the multiplier `1/z*`, defined **non-recursively** from `ν`; the
  inverse law `mu ∗ ν = eps` (`mu_conv_nu`) follows from `root`.

The numeric gate `mu_one` reuses the kernel-decided `V_1_1` of `Weights.lean`.
(`mu_two` and the conditional `mu_three_of` rested on `native_decide` weights
and were removed 2026-10-12.)
-/

namespace Polyplets

/-! ## The guarded interior weights `vGuard ℓ` -/

/-- Aggregated interior weights as a `y`-sequence per row count `ℓ`: `vGuard ℓ`
vanishes below index `ℓ` (each cluster row carries `≥ 1` surplus — encoded by
the guard, no combinatorial input needed) and is identically zero for
`ℓ = 0`. -/
def vGuard (ℓ : ℕ) : ℕ → ℚ := fun j => if ℓ ≤ j ∧ 1 ≤ ℓ then (V ℓ j : ℚ) else 0

/-- `vGuard ℓ` vanishes strictly below `ℓ`. -/
lemma vGuard_vanish_lt {ℓ : ℕ} : ∀ j, j < ℓ → vGuard ℓ j = 0 := by
  intro j hj
  simp only [vGuard]
  rw [if_neg]
  rintro ⟨hle, -⟩
  omega

/-- On its support, `vGuard ℓ` reads the interior weight `V ℓ j`. -/
lemma vGuard_eq {ℓ j : ℕ} (hle : ℓ ≤ j) (h1 : 1 ≤ ℓ) : vGuard ℓ j = (V ℓ j : ℚ) := by
  simp only [vGuard]
  rw [if_pos ⟨hle, h1⟩]

/-! ## The root series `ν` -/

set_option linter.unusedVariables false in
/-- The root series `ν` (= `z*` of `docs/proofs/grand-form.md`): `ν₀ = 1/3`, and
for `m ≥ 1` the unique solution of the root equation
`eps = 3·ν + Σ_ℓ v_ℓ ∗ ν^{∗(ℓ+1)}` coefficient-by-coefficient. The recursion is
well-founded: the RHS reads `ν s` only for `s ≤ m < m + 1` (the dependent guard
supplies the termination witness `h`). -/
noncomputable def nu : ℕ → ℚ
  | 0     => 1/3
  | m + 1 => -(1/3) * ∑ ℓ ∈ Finset.Icc 1 (m + 1),
      conv (vGuard ℓ) (convPow (fun s => if h : s ≤ m then nu s else 0) (ℓ + 1)) (m + 1)
  decreasing_by exact Nat.lt_succ_of_le h

/-- `ν₀ = 1/3`. -/
lemma nu_zero : nu 0 = 1/3 := by rw [nu]

/-! ## De-guarding: the closed-form root recursion -/

/-- The prefix guard agrees with `ν` on its support. -/
lemma nu_guard_eq (m : ℕ) :
    ∀ i, i ≤ m → (fun s => if _h : s ≤ m then nu s else 0) i = nu i := by
  intro i hi
  simp only [dif_pos hi]

/-- Coefficient `M + 1` of `conv (vGuard ℓ) ·` (with `ℓ ≥ 1`) reads its second
argument only at indices `≤ M`, so agreement up to `M` suffices. -/
lemma conv_vGuard_congr {ℓ : ℕ} (hℓ : 1 ≤ ℓ) {x y : ℕ → ℚ} {M : ℕ}
    (h : ∀ i, i ≤ M → x i = y i) :
    conv (vGuard ℓ) x (M + 1) = conv (vGuard ℓ) y (M + 1) := by
  rw [conv_left_vanish_lt vGuard_vanish_lt (M + 1), conv_left_vanish_lt vGuard_vanish_lt (M + 1)]
  refine Finset.sum_congr rfl fun j hj => ?_
  rw [Finset.mem_Icc] at hj
  rw [h (M + 1 - j) (by omega)]

/-- **De-guarding.** For `m ≥ 1`, the guarded prefix in `nu`'s recursion may be
replaced by `nu` itself: `vGuard ℓ` vanishes below `ℓ ≥ 1`, so the inner
`convPow … (ℓ+1)` is read only at indices `≤ m − 1`. -/
lemma nu_unfold (m : ℕ) (hm : 1 ≤ m) :
    nu m = -(1/3) * ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu (ℓ + 1)) m := by
  obtain ⟨k, rfl⟩ : ∃ k, m = k + 1 := ⟨m - 1, by omega⟩
  rw [nu]
  congr 1
  refine Finset.sum_congr rfl fun ℓ hℓmem => ?_
  rw [Finset.mem_Icc] at hℓmem
  exact conv_vGuard_congr hℓmem.1
    (fun i hi => convPow_congr_le (nu_guard_eq k) (ℓ + 1) i hi)

/-- **Root identity.** The closed-form fixed-point equation satisfied by `ν`:
`eps = 3·ν + Σ_ℓ v_ℓ ∗ ν^{∗(ℓ+1)}` coefficient-by-coefficient. -/
lemma root (m : ℕ) :
    eps m = 3 * nu m + ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu (ℓ + 1)) m := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · rw [nu_zero, Finset.Icc_eq_empty (by omega : ¬ (1 : ℕ) ≤ 0), Finset.sum_empty]
    norm_num [eps]
  · rw [nu_unfold m hm]
    have hε : eps m = 0 := by simp only [eps]; rw [if_neg (by omega)]
    rw [hε]; ring

/-! ## The multiplier `μ` -/

/-- The multiplier `μ` (= `1/z*`), defined **non-recursively** from `ν`:
`μ m = 3·eps m + Σ_ℓ v_ℓ ∗ ν^{∗ℓ}`. The inverse law `μ ∗ ν = eps` then follows
from the root identity. -/
noncomputable def mu : ℕ → ℚ :=
  fun m => 3 * eps m + ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) m

/-- `μ₀ = 3`. -/
lemma mu_zero : mu 0 = 3 := by
  simp only [mu, Finset.Icc_eq_empty (by omega : ¬ (1 : ℕ) ≤ 0), Finset.sum_empty]
  norm_num [eps]

/-- For `m ≥ 1` the unit term drops out of `μ`. -/
lemma mu_succ_eq {m : ℕ} (hm : 1 ≤ m) :
    mu m = ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) m := by
  have hε : eps m = 0 := by simp only [eps]; rw [if_neg (by omega)]
  simp only [mu, hε, mul_zero, zero_add]

/-! ## The inverse law `μ ∗ ν = eps` -/

/-- Convolution is linear in its first argument: it distributes over a finite
sum. -/
lemma conv_sum_left {ι : Type*} (s : Finset ι) (F : ι → ℕ → ℚ) (b : ℕ → ℚ) (m : ℕ) :
    conv (fun n => ∑ ℓ ∈ s, F ℓ n) b m = ∑ ℓ ∈ s, conv (F ℓ) b m := by
  simp only [conv, Finset.sum_mul]
  rw [Finset.sum_comm]

/-- `μ i` on the fixed range `Icc 1 m` (for `i ≤ m`): the extra terms `ℓ > i`
vanish because `vGuard ℓ` vanishes below `ℓ`. -/
lemma mu_bigRange {m : ℕ} : ∀ i, i ≤ m →
    mu i = 3 * eps i + ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) i := by
  intro i hi
  simp only [mu]
  congr 1
  refine Finset.sum_subset ?_ ?_
  · intro ℓ hℓ
    rw [Finset.mem_Icc] at hℓ ⊢
    omega
  · intro ℓ hℓm hℓi
    rw [Finset.mem_Icc] at hℓm hℓi
    exact conv_eq_zero_of_lt vGuard_vanish_lt (by omega)

/-- **The inverse law.** `μ ∗ ν = eps`: distribute `conv · ν` through `μ`'s
defining sum and re-collapse `ν^{∗ℓ} ∗ ν = ν^{∗(ℓ+1)}`, then apply `root`. -/
theorem mu_conv_nu : conv mu nu = eps := by
  funext m
  have hconv : conv mu nu m = ∑ i ∈ Finset.range (m + 1), mu i * nu (m - i) := rfl
  have step1 : conv mu nu m
      = ∑ i ∈ Finset.range (m + 1),
          (3 * eps i + ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) i) * nu (m - i) := by
    rw [hconv]
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    rw [mu_bigRange (m := m) i (by omega)]
  have hA : ∑ i ∈ Finset.range (m + 1), 3 * eps i * nu (m - i) = 3 * nu m := by
    have hen : conv eps nu m = nu m := by rw [eps_conv]
    have hexp : conv eps nu m = ∑ i ∈ Finset.range (m + 1), eps i * nu (m - i) := rfl
    rw [hexp] at hen
    rw [← hen, Finset.mul_sum]
    exact Finset.sum_congr rfl fun i _ => by ring
  have hB : ∑ i ∈ Finset.range (m + 1),
        (∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) i) * nu (m - i)
      = ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu (ℓ + 1)) m := by
    have h1 : ∑ i ∈ Finset.range (m + 1),
          (∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) i) * nu (m - i)
        = conv (fun i => ∑ ℓ ∈ Finset.Icc 1 m, conv (vGuard ℓ) (convPow nu ℓ) i) nu m := rfl
    rw [h1, conv_sum_left]
    refine Finset.sum_congr rfl fun ℓ _ => ?_
    rw [conv_assoc]
    congr 1
    rw [conv_comm, convPow]
  rw [step1]
  simp_rw [add_mul]
  rw [Finset.sum_add_distrib, hA, hB]
  exact (root m).symm

/-- The inverse law lifts to convolution powers:
`μ^{∗ℓ} ∗ ν^{∗ℓ} = eps`. -/
theorem mu_conv_nu_pow (ℓ : ℕ) : conv (convPow mu ℓ) (convPow nu ℓ) = eps :=
  conv_convPow_inv mu_conv_nu ℓ

/-! ## Numeric gate

`μ₁ = 25/3` unconditionally, from the kernel-decided weight `V_1_1`. -/

/-- The first convolution power unfolded. -/
lemma convPow_nu_one : convPow nu 1 = nu := by simp only [convPow, conv_eps]

/-! Interior-weight values as `vGuard`-coefficients. -/

lemma vGuard_10 : vGuard 1 0 = 0 := by simp [vGuard]
lemma vGuard_11 : vGuard 1 1 = 25 := by rw [vGuard_eq (by norm_num) (by norm_num), V_1_1]; norm_num

/-- **Gate μ₁.** `μ₁ = 25/3`, via `V_1_1`. -/
theorem mu_one : mu 1 = 25 / 3 := by
  rw [mu_succ_eq (le_refl 1), Finset.Icc_self, Finset.sum_singleton, convPow_nu_one]
  simp only [conv, Finset.sum_range_succ, Finset.sum_range_zero]
  norm_num [vGuard_10, vGuard_11, nu_zero]

end Polyplets
