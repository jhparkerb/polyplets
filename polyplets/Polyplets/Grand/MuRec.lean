/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.Mu
import Polyplets.Peel

/-!
# MuRec: the μ-recursion (the core theorem)

The mathematical heart of the grand-form staircase (`GRANDFORM-PLAN.md`): one
transfer step multiplies the walk-top diagonal family `d k H` by the fixed
multiplier series `μ`, exactly, for `H ≥ k + 1` (sharp onset):

`d k (H + 1) = ∑_{i ≤ k} μ i · d (k − i) H`.

The proof is a single strong induction on `H`, from the peeling recursion
`Peel.d_rec` alone — no power series, no polynomials, no analysis. Two helper
lemmas do the heavy lifting:

* `d_iter_up` — iterating the recursion upward `ℓ` steps multiplies by `μ^{∗ℓ}`.
* `d_iter_down` — the ν-inverse: `ν^{∗ℓ} ∗ μ^{∗ℓ} = eps` runs the iterate back
  down, so a `d`-value at height `H₀` is recovered from height `H₀ + ℓ`.

Both take the strong-induction hypothesis as an explicit `hrec` argument so they
live outside the induction. The main step feeds `d_rec` through `d_iter_down`
(one per interior cluster `(j, ℓ)`) and regroups the resulting triple sum along
the diagonal `s = j + t`, at which point `Mu.mu_bigRange` recognizes the
coefficient as `μ s − 3·eps s` and the algebra closes.

The statement was verified on banked data at all 170 in-range instances
(`experiments/staircase_check.py`); the numeric gate reproduces `d 2 4 = 1019`.
-/

namespace Polyplets

/-! ## Helper 1 — the upward iterate -/

/-- **Upward iterate.** Iterating the μ-recursion upward by `ℓ` transfer steps
multiplies the diagonal family by the `ℓ`-fold convolution power `μ^{∗ℓ}`:
`d k (H₀ + ℓ) = ∑_{i ≤ k} (μ^{∗ℓ}) i · d (k − i) H₀`, for `k + 1 ≤ H₀`. The
strong-induction hypothesis enters as `hrec` (used only up to height `H₀ + ℓ`). -/
lemma d_iter_up (H₀ ℓ : ℕ)
    (hrec : ∀ r, r < ℓ → ∀ k', k' + 1 ≤ H₀ + r →
      (d k' (H₀ + r + 1) : ℚ) =
        ∑ i ∈ Finset.range (k' + 1), mu i * (d (k' - i) (H₀ + r) : ℚ)) :
    ∀ k, k + 1 ≤ H₀ →
      (d k (H₀ + ℓ) : ℚ) =
        ∑ i ∈ Finset.range (k + 1), convPow mu ℓ i * (d (k - i) H₀ : ℚ) := by
  induction ℓ with
  | zero =>
    intro k _
    simp only [Nat.add_zero, convPow]
    rw [Finset.sum_eq_single 0]
    · simp [eps]
    · intro i _ hi
      simp [eps, hi]
    · intro h
      exact absurd (Finset.mem_range.mpr (Nat.succ_pos k)) h
  | succ ℓ ih =>
    intro k hk
    have ihℓ := ih (fun r hr => hrec r (by omega))
    change (d k (H₀ + ℓ + 1) : ℚ) =
      ∑ i ∈ Finset.range (k + 1), convPow mu (ℓ + 1) i * (d (k - i) H₀ : ℚ)
    have hstep : (d k (H₀ + ℓ + 1) : ℚ) =
        ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) (H₀ + ℓ) : ℚ) :=
      hrec ℓ (by omega) k (by omega)
    have key : (∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) (H₀ + ℓ) : ℚ)) =
        ∑ i ∈ Finset.range (k + 1), mu i *
          ∑ t ∈ Finset.range (k - i + 1), convPow mu ℓ t * (d (k - i - t) H₀ : ℚ) := by
      refine Finset.sum_congr rfl fun i hi => ?_
      rw [Finset.mem_range] at hi
      rw [ihℓ (k - i) (by omega)]
    have hcol : (∑ i ∈ Finset.range (k + 1), mu i *
          ∑ t ∈ Finset.range (k - i + 1), convPow mu ℓ t * (d (k - i - t) H₀ : ℚ)) =
        ∑ s ∈ Finset.range (k + 1), convPow mu (ℓ + 1) s * (d (k - s) H₀ : ℚ) :=
      sum_conv_collapse mu (convPow mu ℓ) (fun s => (d s H₀ : ℚ)) k
    rw [hstep, key, hcol]

/-! ## Helper 2 — the downward iterate (inverts with ν) -/

/-- **Downward iterate.** The ν-inverse of `d_iter_up`: because
`ν^{∗ℓ} ∗ μ^{∗ℓ} = eps`, a `d`-value at height `H₀` is recovered from height
`H₀ + ℓ` by convolving with `ν^{∗ℓ}`:
`d k H₀ = ∑_{i ≤ k} (ν^{∗ℓ}) i · d (k − i) (H₀ + ℓ)`, for `k + 1 ≤ H₀`. -/
lemma d_iter_down (H₀ ℓ : ℕ)
    (hrec : ∀ r, r < ℓ → ∀ k', k' + 1 ≤ H₀ + r →
      (d k' (H₀ + r + 1) : ℚ) =
        ∑ i ∈ Finset.range (k' + 1), mu i * (d (k' - i) (H₀ + r) : ℚ)) :
    ∀ k, k + 1 ≤ H₀ →
      (d k H₀ : ℚ) =
        ∑ i ∈ Finset.range (k + 1), convPow nu ℓ i * (d (k - i) (H₀ + ℓ) : ℚ) := by
  intro k hk
  have hup : (∑ i ∈ Finset.range (k + 1), convPow nu ℓ i * (d (k - i) (H₀ + ℓ) : ℚ)) =
      ∑ i ∈ Finset.range (k + 1), convPow nu ℓ i *
        ∑ t ∈ Finset.range (k - i + 1), convPow mu ℓ t * (d (k - i - t) H₀ : ℚ) := by
    refine Finset.sum_congr rfl fun i hi => ?_
    rw [Finset.mem_range] at hi
    rw [d_iter_up H₀ ℓ hrec (k - i) (by omega)]
  have hcol : (∑ i ∈ Finset.range (k + 1), convPow nu ℓ i *
        ∑ t ∈ Finset.range (k - i + 1), convPow mu ℓ t * (d (k - i - t) H₀ : ℚ)) =
      ∑ s ∈ Finset.range (k + 1), conv (convPow nu ℓ) (convPow mu ℓ) s * (d (k - s) H₀ : ℚ) :=
    sum_conv_collapse (convPow nu ℓ) (convPow mu ℓ) (fun s => (d s H₀ : ℚ)) k
  rw [hup, hcol, conv_comm (convPow nu ℓ) (convPow mu ℓ), mu_conv_nu_pow ℓ]
  rw [Finset.sum_eq_single 0]
  · simp [eps]
  · intro i _ hi
    simp [eps, hi]
  · intro h
    exact absurd (Finset.mem_range.mpr (Nat.succ_pos k)) h

/-! ## The μ-recursion -/

/-- The inductive step of `d_mu_rec`, packaged for `Nat.strong_induction_on`. -/
lemma d_mu_rec_step (H : ℕ)
    (M_ih : ∀ m, m < H → ∀ k, k + 1 ≤ m →
      (d k (m + 1) : ℚ) = ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) m : ℚ)) :
    ∀ k, k + 1 ≤ H →
      (d k (H + 1) : ℚ) = ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ) := by
  intro k hk
  -- Step 1: the peeling recursion at `H + 1`, cast to ℚ.
  have hrec := d_rec k (H + 1) (by omega)
  simp only [Nat.add_sub_cancel] at hrec
  have hrecQ : (d k (H + 1) : ℚ) = 3 * (d k H : ℚ) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (V ℓ j : ℚ) * (d (k - j) (H - ℓ) : ℚ) := by exact_mod_cast hrec
  -- Step 2: expand each `d (k−j) (H−ℓ)` downward with `d_iter_down` and switch
  -- `V ℓ j` to its guarded form `v ℓ j`.
  have hB : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (V ℓ j : ℚ) * (d (k - j) (H - ℓ) : ℚ)) =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, v ℓ j *
        ∑ t ∈ Finset.range (k - j + 1), convPow nu ℓ t * (d (k - j - t) H : ℚ) := by
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [Finset.mem_Icc] at hj
    refine Finset.sum_congr rfl fun ℓ hℓ => ?_
    rw [Finset.mem_Icc] at hℓ
    have hdd := d_iter_down (H - ℓ) ℓ
      (fun r hr k'' hk'' => M_ih (H - ℓ + r) (by omega) k'' hk'') (k - j) (by omega)
    rw [show H - ℓ + ℓ = H from by omega] at hdd
    rw [← v_eq (by omega) (by omega), hdd]
  -- Step 3a: transpose the `j`/`ℓ` order to `∑_ℓ ∑_{j ≥ ℓ}`.
  have hswap : (∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, v ℓ j *
        ∑ t ∈ Finset.range (k - j + 1), convPow nu ℓ t * (d (k - j - t) H : ℚ)) =
      ∑ ℓ ∈ Finset.Icc 1 k, ∑ j ∈ Finset.Icc ℓ k, v ℓ j *
        ∑ t ∈ Finset.range (k - j + 1), convPow nu ℓ t * (d (k - j - t) H : ℚ) := by
    apply Finset.sum_comm'
    intro j ℓ
    simp only [Finset.mem_Icc]
    omega
  -- Step 3b: for each `ℓ`, extend the inner range and collapse `(j, t)` by
  -- `sum_conv_collapse`; the `v ℓ`-vanishing absorbs the range mismatch.
  have hcollapse : (∑ ℓ ∈ Finset.Icc 1 k, ∑ j ∈ Finset.Icc ℓ k, v ℓ j *
        ∑ t ∈ Finset.range (k - j + 1), convPow nu ℓ t * (d (k - j - t) H : ℚ)) =
      ∑ ℓ ∈ Finset.Icc 1 k, ∑ s ∈ Finset.range (k + 1),
        conv (v ℓ) (convPow nu ℓ) s * (d (k - s) H : ℚ) := by
    refine Finset.sum_congr rfl fun ℓ _ => ?_
    have hext : (∑ j ∈ Finset.Icc ℓ k, v ℓ j *
          ∑ t ∈ Finset.range (k - j + 1), convPow nu ℓ t * (d (k - j - t) H : ℚ)) =
        ∑ i ∈ Finset.range (k + 1), v ℓ i *
          ∑ t ∈ Finset.range (k - i + 1), convPow nu ℓ t * (d (k - i - t) H : ℚ) := by
      refine Finset.sum_subset ?_ ?_
      · intro x hx
        rw [Finset.mem_Icc] at hx
        rw [Finset.mem_range]
        omega
      · intro i hi hni
        rw [Finset.mem_range] at hi
        rw [Finset.mem_Icc] at hni
        rw [v_vanish_lt i (by omega), zero_mul]
    rw [hext]
    exact sum_conv_collapse (v ℓ) (convPow nu ℓ) (fun s => (d s H : ℚ)) k
  -- Step 3c: transpose back and factor out `d (k−s) H`.
  have hfactor : (∑ ℓ ∈ Finset.Icc 1 k, ∑ s ∈ Finset.range (k + 1),
        conv (v ℓ) (convPow nu ℓ) s * (d (k - s) H : ℚ)) =
      ∑ s ∈ Finset.range (k + 1), (mu s - 3 * eps s) * (d (k - s) H : ℚ) := by
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun s hs => ?_
    rw [Finset.mem_range] at hs
    rw [← Finset.sum_mul]
    have hcoeff : (∑ ℓ ∈ Finset.Icc 1 k, conv (v ℓ) (convPow nu ℓ) s) = mu s - 3 * eps s := by
      rw [mu_bigRange (m := k) s (by omega)]; ring
    rw [hcoeff]
  -- Step 4: assemble.  `∑ eps s · d (k−s) H = d k H` cancels the `3·d k H` head.
  have heps : (∑ s ∈ Finset.range (k + 1), eps s * (d (k - s) H : ℚ)) = (d k H : ℚ) := by
    have h : conv eps (fun s => (d s H : ℚ)) k = (d k H : ℚ) := by rw [eps_conv]
    simpa only [conv] using h
  have hexpand : (∑ s ∈ Finset.range (k + 1), (mu s - 3 * eps s) * (d (k - s) H : ℚ)) =
      (∑ s ∈ Finset.range (k + 1), mu s * (d (k - s) H : ℚ)) -
        3 * ∑ s ∈ Finset.range (k + 1), eps s * (d (k - s) H : ℚ) := by
    rw [Finset.mul_sum, ← Finset.sum_sub_distrib]
    refine Finset.sum_congr rfl fun s _ => ?_
    ring
  rw [hrecQ, hB, hswap, hcollapse, hfactor, hexpand, heps]
  ring

/-- **The μ-recursion**: one transfer step multiplies the walk-top diagonal
family by the fixed series `μ`, exactly, for `H ≥ k + 1` (sharp onset). Proved by
strong induction on `H` from `Peel.d_rec` through the `μ`/`ν` inverse pair. -/
theorem d_mu_rec : ∀ H k : ℕ, k + 1 ≤ H →
    (d k (H + 1) : ℚ) = ∑ i ∈ Finset.range (k + 1), mu i * (d (k - i) H : ℚ) :=
  fun H => Nat.strong_induction_on H d_mu_rec_step

/-! ## Numeric gates -/

/-- **Gate (k, H) = (1, 2).** The recursion smoke test:
`d 1 3 = μ₀·d 1 2 + μ₁·d 0 2`. -/
theorem d_mu_rec_check_k1_H2 :
    (d 1 3 : ℚ) = mu 0 * d 1 2 + mu 1 * d 0 2 := by
  have h := d_mu_rec 2 1 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add, Nat.sub_zero] using h

/-- The `(1, 2)` gate evaluates: `40 = 3·5 + (25/3)·3` (verified arithmetic). -/
theorem d_mu_rec_value_check : (40 : ℚ) = 3 * 5 + (25 / 3) * 3 := by norm_num

/-- **Gate (k, H) = (2, 3).** The recursion at `d 2 4`:
`d 2 4 = μ₀·d 2 3 + μ₁·d 1 3 + μ₂·d 0 3`. -/
theorem d_mu_rec_check_k2_H3 :
    (d 2 4 : ℚ) = mu 0 * d 2 3 + mu 1 * d 1 3 + mu 2 * d 0 3 := by
  have h := d_mu_rec 3 2 (by norm_num)
  simpa only [Finset.sum_range_succ, Finset.sum_range_zero, zero_add, Nat.sub_zero] using h

/-- The `(2, 3)` gate reproduces the banked `d 2 4 = 1019` from the native_decide
values `d 2 3 = 136`, `d 1 3 = 40`, `d 0 3 = 9` and `μ₀ = 3, μ₁ = 25/3,
μ₂ = 833/27`: `3·136 + (25/3)·40 + (833/27)·9 = 408 + 611 = 1019`. -/
theorem d_mu_rec_value_check_k2 :
    mu 0 * (d 2 3 : ℚ) + mu 1 * (d 1 3 : ℚ) + mu 2 * (d 0 3 : ℚ) = 1019 := by
  rw [mu_zero, mu_one, mu_two, d_2_3, d_1_3, d_0_3]; norm_num

/-! ## Axiom sanity check -/

section Sanity

#print axioms d_mu_rec

end Sanity

end Polyplets
