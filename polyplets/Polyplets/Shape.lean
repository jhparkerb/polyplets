/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.NumberTheory.Bernoulli
import Polyplets.Peel

/-!
# Shape: the diagonal law by strong induction on the surplus

The shape theorem of DESIGN.md v2, built on `Peel.lean`'s `d_rec` and
`c_ident`:

* `shape_d` : for every surplus `k` there is `δ_k ∈ ℚ[X]` with `deg ≤ k` and
  `d k H = δ_k(H) · 3^H` for all `H ≥ k + 1`.
* `shape` : likewise `T(H+k, H) = q_k(H) · 3^H` for all `H ≥ k + 1`.
* `shape_production` : the production form used by the counting engine,
  `T(n, n-k) = P_k(n) · 3^(n-1-3k)` for `n ≥ 2k + 1`, with the exponent an
  integer (`zpow`) so the statement covers the negative-exponent onset window
  `2k+1 ≤ n < 3k+1`; plus the zpow-free companion
  `3^(3k+1) · T(n, n-k) = P_k(n) · 3^n` that `Pin.lean` should consume.
* `production_int_onset` : integrality at the pinning window — for
  `2k+1 ≤ n ≤ 3k+1`, `P_k(n)` is the natural number `T(n,n-k) · 3^(3k+1-n)`.
* `production_int_all` : (tier 2) any such `P_k` is integer-valued on all of
  `ℤ`, by finite differences from the `k+1` onset points.

The proof of `shape_d` is strong induction on `k` (`shape_d_step`): the
d-recursion divided by `3^H` is a first-order difference equation
`e(H) = e(H-1) + g(H)` whose inhomogeneity `g` is a polynomial of degree
`≤ k - 1` built from the lower-surplus `δ_j`; summing it from the base
`H₀ = k + 1` needs a polynomial discrete antiderivative, provided by
Faulhaber's formula (`sum_range_pow`) through the standalone lemma
`exists_poly_sum_Icc`. The onset is `k + 1`, not `k + 2`, because the base
value is absorbed into the constant term of `δ_k`.

Numeric guard: `shape_production` at `k = 0` plus the single onset value
`T 1 1 = 1` pins `P_0 = 1`, giving `T(n,n) = 3^(n-1)` (`T_diag_pow`) — checked
against the independently `native_decide`d `T 3 3 = 9` and `T 4 4 = 27`
(`Compute.lean` proves the former directly). This is exactly the
shape-plus-points pattern `Pin.lean` runs at every `k`.
-/

namespace Polyplets

open Polynomial

/-! ## Interval-sum bookkeeping -/

/-- An `Icc`-sum is a difference of prefix (`range`) sums. -/
lemma sum_Icc_eq_sum_range_sub (f : ℕ → ℚ) {a b : ℕ} (h : a ≤ b + 1) :
    ∑ i ∈ Finset.Icc a b, f i
      = (∑ i ∈ Finset.range (b + 1), f i) - ∑ i ∈ Finset.range a, f i := by
  have hdisj : Disjoint (Finset.range a) (Finset.Icc a b) := by
    rw [Finset.disjoint_left]
    intro i hi hi'
    rw [Finset.mem_range] at hi
    rw [Finset.mem_Icc] at hi'
    omega
  have hun : Finset.range (b + 1) = Finset.range a ∪ Finset.Icc a b := by
    ext i
    simp only [Finset.mem_union, Finset.mem_range, Finset.mem_Icc]
    omega
  rw [hun, Finset.sum_union hdisj]
  ring

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
of the shape theorem. -/
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

/-! ## Shape of the walk-top counts -/

/-- The strong-induction step for `shape_d`: lower-surplus polynomials give
the surplus-`k` one. The d-recursion divided by `3^H` is the difference
equation `e(H) = e(H-1) + g(H)`; telescoping from `H₀ = k+1` and summing `g`
by `exists_poly_sum_Icc` gives `δ_k`, with the base value absorbed into the
constant term (hence onset `k+1`, not `k+2`). -/
lemma shape_d_step (k : ℕ)
    (IH : ∀ j, j < k → ∃ δ : Polynomial ℚ, δ.natDegree ≤ j ∧
      ∀ H : ℕ, j + 1 ≤ H → (d j H : ℚ) = δ.eval (H : ℚ) * 3 ^ H) :
    ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H := by
  classical
  -- totalize the induction hypothesis into a plain family of polynomials
  obtain ⟨δ', hδ'deg, hδ'val⟩ : ∃ δ' : ℕ → Polynomial ℚ,
      (∀ j, j < k → (δ' j).natDegree ≤ j) ∧
      (∀ j, j < k → ∀ H : ℕ, j + 1 ≤ H → (d j H : ℚ) = (δ' j).eval (H : ℚ) * 3 ^ H) := by
    choose δfun hdeg hval using IH
    exact ⟨fun j => if h : j < k then δfun j h else 0,
      fun j hj => by simp only [dif_pos hj]; exact hdeg j hj,
      fun j hj H hH => by simp only [dif_pos hj]; exact hval j hj H hH⟩
  -- the inhomogeneity of the difference equation for d k H / 3^H
  set g : Polynomial ℚ := ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
    C ((V ℓ j : ℚ) / 3 ^ (ℓ + 1)) * (δ' (k - j)).comp (X - C ((ℓ : ℚ) + 1)) with hg
  have hgdeg : g.natDegree ≤ k - 1 := by
    rw [hg]
    refine natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
    refine natDegree_sum_le_of_forall_le _ _ fun ℓ _ => ?_
    rw [Finset.mem_Icc] at hj
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    have hd := hδ'deg (k - j) (by omega)
    omega
  obtain ⟨G, hGdeg₀, hG0, hGsum⟩ := exists_poly_sum_Icc g
  have hGdeg : G.natDegree ≤ k := by
    rcases Nat.eq_zero_or_pos k with rfl | hk
    · have hgz : g = 0 := by
        rw [hg, Finset.Icc_eq_empty (by omega), Finset.sum_empty]
      rw [hG0 hgz, natDegree_zero]
    · omega
  refine ⟨C ((d k (k + 1) : ℚ) / 3 ^ (k + 1) - G.eval ((k : ℚ) + 1)) + G, ?_, ?_⟩
  · exact le_trans (natDegree_add_le _ _) (max_le (by simp) hGdeg)
  · intro H hH
    induction H, hH using Nat.le_induction with
    | base =>
      have hcast : ((k + 1 : ℕ) : ℚ) = (k : ℚ) + 1 := by push_cast; ring
      simp only [eval_add, eval_C, hcast]
      have h3 : ((3 : ℚ)) ^ (k + 1) ≠ 0 := pow_ne_zero _ (by norm_num)
      field_simp
      ring
    | succ m hm ihm =>
      -- the d-recursion at H = m + 1, cast to ℚ
      have hrec := d_rec k (m + 1) (by omega)
      simp only [Nat.add_sub_cancel] at hrec
      have hrecQ : (d k (m + 1) : ℚ) = 3 * (d k m : ℚ)
          + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
              (V ℓ j : ℚ) * (d (k - j) (m - ℓ) : ℚ) := by exact_mod_cast hrec
      -- every d-term is in range for the lower-surplus polynomials
      have hsum : ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
          (V ℓ j : ℚ) * (d (k - j) (m - ℓ) : ℚ)
          = g.eval ((m + 1 : ℕ) : ℚ) * 3 ^ (m + 1) := by
        rw [hg, eval_finsetSum, Finset.sum_mul]
        refine Finset.sum_congr rfl fun j hj => ?_
        rw [eval_finsetSum, Finset.sum_mul]
        refine Finset.sum_congr rfl fun ℓ hℓ => ?_
        rw [Finset.mem_Icc] at hj hℓ
        have hlm : ℓ ≤ m := by omega
        have hrange : (k - j) + 1 ≤ m - ℓ := by omega
        rw [hδ'val (k - j) (by omega) (m - ℓ) hrange]
        simp only [eval_mul, eval_C, eval_comp, eval_sub, eval_X]
        have hcast : ((m - ℓ : ℕ) : ℚ) = ((m + 1 : ℕ) : ℚ) - ((ℓ : ℚ) + 1) := by
          rw [Nat.cast_sub hlm]
          push_cast
          ring
        have hpow : (3 : ℚ) ^ (m + 1) = 3 ^ (m - ℓ) * 3 ^ (ℓ + 1) := by
          rw [← pow_add]
          congr 1
          omega
        rw [hcast, hpow]
        have h3 : ((3 : ℚ)) ^ (ℓ + 1) ≠ 0 := pow_ne_zero _ (by norm_num)
        field_simp
      -- the discrete-derivative property of the antiderivative at m + 1
      have hδstep : (C ((d k (k + 1) : ℚ) / 3 ^ (k + 1) - G.eval ((k : ℚ) + 1)) + G).eval
            ((m + 1 : ℕ) : ℚ)
          = (C ((d k (k + 1) : ℚ) / 3 ^ (k + 1) - G.eval ((k : ℚ) + 1)) + G).eval (m : ℚ)
            + g.eval ((m + 1 : ℕ) : ℚ) := by
        have h1 := hGsum (m + 1) (m + 1) (by omega)
        rw [Finset.Icc_self, Finset.sum_singleton] at h1
        have hcast : ((m + 1 : ℕ) : ℚ) - 1 = (m : ℚ) := by push_cast; ring
        rw [hcast] at h1
        simp only [eval_add, eval_C]
        rw [h1]
        ring
      rw [hrecQ, hsum, ihm, hδstep]
      ring

/-- **Shape of the walk-top diagonal**: `d k H = δ_k(H) · 3^H` for all
`H ≥ k + 1`, with `δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem shape_d : ∀ k : ℕ, ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H := fun k =>
  Nat.strong_induction_on k shape_d_step

/-- **Shape of the k-th diagonal**: `T(H+k, H) = q_k(H) · 3^H` for all
`H ≥ k + 1`, with `q_k ∈ ℚ[X]` of degree `≤ k`. From `shape_d` through the
c-identity: at `H ≥ k + 1` every `d`-term of `c_ident` is exactly in range. -/
theorem shape (k : ℕ) : ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (T (H + k) H : ℚ) = q.eval (H : ℚ) * 3 ^ H := by
  classical
  choose δ hδdeg hδval using shape_d
  refine ⟨δ k + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
    C ((Vt ℓ j : ℚ) / 3 ^ ℓ) * (δ (k - j)).comp (X - C (ℓ : ℚ)), ?_, ?_⟩
  · refine le_trans (natDegree_add_le _ _) (max_le (hδdeg k) ?_)
    refine natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
    refine natDegree_sum_le_of_forall_le _ _ fun ℓ _ => ?_
    rw [Finset.mem_Icc] at hj
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    have := hδdeg (k - j)
    omega
  · intro H hH
    have hcQ : (T (H + k) H : ℚ) = (d k H : ℚ)
        + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
            (Vt ℓ j : ℚ) * (d (k - j) (H - ℓ) : ℚ) := by
      exact_mod_cast c_ident k H (by omega)
    rw [hcQ, eval_add, add_mul, hδval k H hH]
    congr 1
    rw [eval_finsetSum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [eval_finsetSum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun ℓ hℓ => ?_
    rw [Finset.mem_Icc] at hj hℓ
    have hlH : ℓ ≤ H := by omega
    have hrange : (k - j) + 1 ≤ H - ℓ := by omega
    rw [hδval (k - j) (H - ℓ) hrange]
    simp only [eval_mul, eval_C, eval_comp, eval_sub, eval_X]
    have hcast : ((H - ℓ : ℕ) : ℚ) = (H : ℚ) - (ℓ : ℚ) := by
      rw [Nat.cast_sub hlH]
    have hpow : (3 : ℚ) ^ H = 3 ^ (H - ℓ) * 3 ^ ℓ := by
      rw [← pow_add]
      congr 1
      omega
    rw [hcast, hpow]
    have h3 : ((3 : ℚ)) ^ ℓ ≠ 0 := pow_ne_zero _ (by norm_num)
    field_simp

/-! ## The production form -/

/-- **Production form of the diagonal law**: for every `k` there is
`P_k ∈ ℚ[X]` of degree `≤ k` with

* `T(n, n-k) = P_k(n) · 3^(n-1-3k)` for all `n ≥ 2k + 1`, the exponent an
  integer (`zpow`) — negative on the onset window `2k+1 ≤ n < 3k+1`, where
  `P_k(n)` carries the compensating powers of three; and
* the zpow-free companion `3^(3k+1) · T(n, n-k) = P_k(n) · 3^n`, the form
  `Pin.lean` should consume (no subtraction anywhere: `n - k` occurs only
  inside `T`).

`P_k(n) = 3^(2k+1) · q_k(n - k)` for the `q_k` of `shape`. -/
theorem shape_production (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) := by
  obtain ⟨q, hqdeg, hq⟩ := shape k
  have hbase : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = q.eval ((n : ℚ) - (k : ℚ)) * 3 ^ (n - k) := by
    intro n hn
    have hkn : k ≤ n := by omega
    have h1 := hq (n - k) (by omega)
    rw [Nat.sub_add_cancel hkn] at h1
    rw [h1, Nat.cast_sub hkn]
  set P : Polynomial ℚ := C ((3 : ℚ) ^ (2 * k + 1)) * q.comp (X - C (k : ℚ)) with hP
  have hPeval : ∀ x : ℚ, P.eval x = (3 : ℚ) ^ (2 * k + 1) * q.eval (x - (k : ℚ)) := by
    intro x
    rw [hP, eval_mul, eval_C, eval_comp, eval_sub, eval_X, eval_C]
  refine ⟨P, ?_, ?_, ?_⟩
  · rw [hP]
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    exact hqdeg
  · intro n hn
    have hkn : k ≤ n := by omega
    rw [hbase n hn, hPeval]
    have hz : (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k) = (3 : ℚ) ^ (n - k) / (3 : ℚ) ^ (2 * k + 1) := by
      have hexp : (n : ℤ) - 1 - 3 * k = ((n - k : ℕ) : ℤ) - ((2 * k + 1 : ℕ) : ℤ) := by omega
      rw [hexp, zpow_sub₀ (by norm_num : (3 : ℚ) ≠ 0), zpow_natCast, zpow_natCast]
    rw [hz]
    have h3 : ((3 : ℚ)) ^ (2 * k + 1) ≠ 0 := pow_ne_zero _ (by norm_num)
    field_simp
  · intro n hn
    have hkn : k ≤ n := by omega
    rw [hbase n hn, hPeval]
    have hpow : (3 : ℚ) ^ (3 * k + 1) * (3 : ℚ) ^ (n - k)
        = (3 : ℚ) ^ (2 * k + 1) * (3 : ℚ) ^ n := by
      rw [← pow_add, ← pow_add]
      congr 1
      omega
    linear_combination q.eval ((n : ℚ) - (k : ℚ)) * hpow

/-! ## Integrality -/

/-- **Integrality at the pinning window** (tier 1): for `2k+1 ≤ n ≤ 3k+1` the
value `P_k(n)` is the natural number `T(n, n-k) · 3^(3k+1-n)`. These are
exactly the `k+1` onset points `H = k+1 .. 2k+1` (`n = H+k`) that `Pin.lean`
pins with. Stated for any `P` satisfying the production identity, so it
applies to any witness. -/
theorem production_int_onset {k : ℕ} {P : Polynomial ℚ}
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ) := by
  have h := hP n hn1
  have hpow : (3 : ℚ) ^ (3 * k + 1) = (3 : ℚ) ^ (3 * k + 1 - n) * (3 : ℚ) ^ n := by
    rw [← pow_add]
    congr 1
    omega
  have h3 : ((3 : ℚ)) ^ n ≠ 0 := pow_ne_zero _ (by norm_num)
  refine mul_right_cancel₀ h3 ?_
  rw [← h, hpow]
  push_cast
  ring

/-- Tier-1 integrality in `∃ z : ℤ` form. -/
theorem production_int_onset' {k : ℕ} {P : Polynomial ℚ}
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    ∃ z : ℤ, P.eval (n : ℚ) = (z : ℚ) :=
  ⟨(T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ), by
    rw [production_int_onset hP hn1 hn2]
    push_cast
    ring⟩

/-- **Finite differences** (tier 2 workhorse): a `ℚ`-polynomial of degree
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

/-- **Integrality tier 2**: any `P` of degree `≤ k` satisfying the production
identity is integer-valued on all of `ℤ` — the `k+1` onset points
`n = 2k+1 .. 3k+1` are integer (tier 1) and consecutive, so finite
differences extend integrality everywhere. -/
theorem production_int_all {k : ℕ} {P : Polynomial ℚ} (hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) := by
  refine int_valued_of_consecutive k P ((2 * k + 1 : ℕ) : ℤ) hdeg fun i hi => ?_
  obtain ⟨z, hz⟩ := production_int_onset' hP
    (show 2 * k + 1 ≤ 2 * k + 1 + i by omega) (show 2 * k + 1 + i ≤ 3 * k + 1 by omega)
  refine ⟨z, ?_⟩
  have hcast : ((((2 * k + 1 : ℕ) : ℤ) + (i : ℕ) : ℤ) : ℚ) = ((2 * k + 1 + i : ℕ) : ℚ) := by
    push_cast
    ring
  rw [hcast]
  exact hz

/-! ## Numeric guard: the `k = 0` pin

The Pin pattern run at `k = 0`: `shape_production 0` gives a constant `P₀`,
the single onset value `T 1 1 = 1` (a `native_decide` fact from
`Compute.lean`) pins it, and the closed form `T(n,n) = 3^(n-1)` follows —
cross-checked against the independently `native_decide`d `T 3 3 = 9`. -/

/-- The `k = 0` diagonal pinned: `T(n, n) = 3^(n-1)` for `n ≥ 1`. -/
theorem T_diag_pow (n : ℕ) (hn : 1 ≤ n) : (T n n : ℚ) = (3 : ℚ) ^ ((n : ℤ) - 1) := by
  obtain ⟨P, hPdeg, hPzpow, -⟩ := shape_production 0
  have hPC : P = C (P.coeff 0) := eq_C_of_natDegree_le_zero hPdeg
  have h1 := hPzpow 1 (by omega)
  rw [hPC] at h1
  simp only [Nat.sub_zero, T_1_1, eval_C, Nat.cast_zero, Nat.cast_one, mul_zero,
    sub_zero] at h1
  norm_num at h1
  have h := hPzpow n (by omega)
  rw [hPC] at h
  simp only [Nat.sub_zero, eval_C, Nat.cast_zero, mul_zero, sub_zero] at h
  rw [h, ← h1, one_mul]

/-- Guard: the shape-derived closed form reproduces the `native_decide`d
`T 3 3 = 9` (`Compute.lean`'s `T_3_3`). -/
theorem shape_check_T_3_3 : T 3 3 = 9 := by
  have h := T_diag_pow 3 (by omega)
  have he : ((3 : ℕ) : ℤ) - 1 = 2 := by omega
  rw [he] at h
  norm_num at h
  exact_mod_cast h

/-- Guard: the shape-derived `T 4 4 = 27`. -/
theorem shape_check_T_4_4 : T 4 4 = 27 := by
  have h := T_diag_pow 4 (by omega)
  have he : ((4 : ℕ) : ℤ) - 1 = 3 := by omega
  rw [he] at h
  norm_num at h
  exact_mod_cast h

end Polyplets
