/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Growth

/-!
# The convolution-certificate upper bound (Bui's method, abstract layer)

`docs/proofs/polyplet-upper-bound.md` proves `λ ≤ 9.3154` by the Bui
convolution-certificate method (`experiments/king_bui.py`,
`experiments/king_certificate.py`): a finite family of marked-animal counting
functions `φ_T` closes, by single-free-cell casing, into recurrences

* base types (`rule T = none`, all eight king neighbors forbidden):
  `φ_T 1 ≤ 1` and `φ_T n = 0` for `n ≥ 2` — the marked cell is isolated;
* split types (`rule T = some (T', D)`):
  `φ_T n ≤ φ_{T'} n + ∑_{i=1}^{n-1} φ_{T'} i · φ_D (n-i)` — the cased free
  cell `d` is either empty (an exact partition onto `T' = T + {d forbidden}`)
  or occupied (a valid split over-count into a `d`-piece of type `D`
  convolved with the `c`-side).

This file proves the *certificate* half of that argument, unconditionally: if
a positive rational `u` satisfies the super-solution system `F_x(u) ≤ u` for
a rational `x > 0`, then every `φ` satisfying the system inequalities obeys
`x^n · φ_T n ≤ u_T` — division-free, over `ℚ` — and an anchor `a n ≤ φ_root n`
then forces `lambda ≤ 1/x` through `lambda_tendsto`.

The two layers:

* `BuiSystem` / `BuiSystem.Satisfies` / `BuiSystem.IsSuperSolution` — the abstract system over
  an arbitrary index type: `rule` (the casing table), `rank` (a termination
  measure: the number of free king neighbors in the concrete system) with
  `rank_lt` making the `T'`-chain well-founded.
* `BuiSystem.certSum_le` — the monotone-iteration bound: the truncated
  weighted sums `certSum φ x T N = ∑_{n=1}^N x^n φ_T n` are dominated by `u`,
  by strong induction on `N` (outer) and on `rank` (inner: the `d`-empty
  branch stays at the same `n`, but strictly grows the forbidden set).
* `BuiSystem.pow_mul_le` — the single-term form `x^n · φ_T n ≤ u_T`.
* `lambda_le_of_pow_bound` — `a n ≤ C·y^n` for all `n ≥ 1` forces
  `lambda ≤ y` (`C^{1/n} → 1` against `lambda_tendsto`).
* `lambda_le_of_buiSystem` — the assembled abstract theorem:
  system + super-solution + anchor `⟹ lambda ≤ 1/x`.
* `RatCert` / `RatCert.valid` / `RatCert.SystemHolds` / `RatCert.lambda_le` —
  the exported-data interface: a certificate with all entries over one common
  denominator `CD`, whose entire arithmetic content (`F_x(u) ≤ u`, rank
  descent, index bounds) is one `Bool` check on integers, decidable by the
  kernel; `RatCert.lambda_le` turns `valid = true` plus the (combinatorial,
  *hypothesis*) `SystemHolds` bundle into `lambda ≤ CD / X`.

Nothing here assumes anything about polyplets: the combinatorial content
enters only through `SystemHolds`, which the concrete instances
(`Upper/BuiRD2.lean`, `Upper/BuiRD3.lean`) take as their one named hypothesis.
-/

namespace Polyplets

open scoped Topology

/-! ## The abstract system -/

/-- An abstract Bui convolution system on an index type `ι`: every index is
either a *base* type (`rule T = none`) or cases into a pair
`rule T = some (T', D)` — the `d`-empty continuation `T'` and the split-off
convolution factor `D`. `rank` is a termination measure for the `T'`-chain
(concretely: the number of free king neighbors, which the casing strictly
decreases); the `D`-factor needs no measure because it only ever appears at a
strictly smaller truncation order. -/
structure BuiSystem (ι : Type*) where
  /-- The casing table: `none` = base type, `some (T', D)` = split. -/
  rule : ι → Option (ι × ι)
  /-- Termination measure for the `d`-empty chain. -/
  rank : ι → ℕ
  /-- Casing strictly decreases the measure on the `T'`-side. -/
  rank_lt : ∀ ⦃T T' D⦄, rule T = some (T', D) → rank T' < rank T

/-- `φ` satisfies the system inequalities: base types count at most the
isolated marked cell, split types obey the casing recurrence
`φ_T n ≤ φ_{T'} n + ∑_{i=1}^{n-1} φ_{T'} i · φ_D (n-i)`. -/
def BuiSystem.Satisfies {ι : Type*} (S : BuiSystem ι) (φ : ι → ℕ → ℕ) : Prop :=
  (∀ T, S.rule T = none → φ T 1 ≤ 1 ∧ ∀ n, 2 ≤ n → φ T n = 0) ∧
  (∀ T T' D, S.rule T = some (T', D) → ∀ n : ℕ,
    φ T n ≤ φ T' n + ∑ i ∈ Finset.Ico 1 n, φ T' i * φ D (n - i))

/-- `u` is a nonnegative super-solution at `x`: `F_x(u) ≤ u` componentwise,
where `F_x(u)_T = x` at base types and `u_{T'} + u_{T'}·u_D` at split types. -/
def BuiSystem.IsSuperSolution {ι : Type*} (S : BuiSystem ι) (x : ℚ) (u : ι → ℚ) : Prop :=
  (∀ T, 0 ≤ u T) ∧
  (∀ T, S.rule T = none → x ≤ u T) ∧
  (∀ T T' D, S.rule T = some (T', D) → u T' + u T' * u D ≤ u T)

/-- The truncated weighted sum `∑_{n=1}^N x^n · φ_T n` — the division-free
stand-in for the generating function `Φ_T(x)` truncated at order `N`. -/
def certSum {ι : Type*} (φ : ι → ℕ → ℕ) (x : ℚ) (T : ι) (N : ℕ) : ℚ :=
  ∑ n ∈ Finset.Icc 1 N, x ^ n * (φ T n : ℚ)

/-- **Triangle-into-box bound for the Cauchy convolution.** The double sum over
the triangle `{(i, n-i) : 1 ≤ i < n ≤ M+1}` of a product of nonnegative
sequences is at most the product of the two box sums up to `M`: the map
`(n, i) ↦ (i, n-i)` injects the triangle into the box `[1,M] × [1,M]`. -/
private lemma conv_triangle_le {F G : ℕ → ℚ} (hF : ∀ i, 0 ≤ F i)
    (hG : ∀ j, 0 ≤ G j) (M : ℕ) :
    ∑ n ∈ Finset.Icc 1 (M + 1), ∑ i ∈ Finset.Ico 1 n, F i * G (n - i)
      ≤ (∑ i ∈ Finset.Icc 1 M, F i) * (∑ j ∈ Finset.Icc 1 M, G j) := by
  classical
  set s : Finset ((_ : ℕ) × ℕ) := (Finset.Icc 1 (M + 1)).sigma fun n => Finset.Ico 1 n with hs
  have hinj : Set.InjOn (fun p : (_ : ℕ) × ℕ => (p.2, p.1 - p.2)) s := by
    rintro ⟨n, i⟩ hp ⟨m, j⟩ hq h
    have hp' := Finset.mem_sigma.mp (Finset.mem_coe.mp hp)
    have hq' := Finset.mem_sigma.mp (Finset.mem_coe.mp hq)
    simp only [Finset.mem_Icc, Finset.mem_Ico] at hp' hq'
    simp only [Prod.mk.injEq] at h
    obtain ⟨hij, hsub⟩ := h
    have hnm : n = m := by omega
    subst hnm; subst hij; rfl
  have hsub : s.image (fun p : (_ : ℕ) × ℕ => (p.2, p.1 - p.2))
      ⊆ Finset.Icc 1 M ×ˢ Finset.Icc 1 M := by
    intro q hq
    rw [Finset.mem_image] at hq
    obtain ⟨⟨n, i⟩, hp, rfl⟩ := hq
    have hp' := Finset.mem_sigma.mp hp
    simp only [Finset.mem_Icc, Finset.mem_Ico] at hp'
    simp only [Finset.mem_product, Finset.mem_Icc]
    omega
  calc ∑ n ∈ Finset.Icc 1 (M + 1), ∑ i ∈ Finset.Ico 1 n, F i * G (n - i)
      = ∑ p ∈ s, F p.2 * G (p.1 - p.2) :=
        Finset.sum_sigma' (Finset.Icc 1 (M + 1)) (fun n => Finset.Ico 1 n)
          (fun n i => F i * G (n - i))
    _ = ∑ q ∈ s.image (fun p : (_ : ℕ) × ℕ => (p.2, p.1 - p.2)), F q.1 * G q.2 := by
        rw [Finset.sum_image hinj]
    _ ≤ ∑ q ∈ Finset.Icc 1 M ×ˢ Finset.Icc 1 M, F q.1 * G q.2 :=
        Finset.sum_le_sum_of_subset_of_nonneg hsub
          fun q _ _ => mul_nonneg (hF _) (hG _)
    _ = (∑ i ∈ Finset.Icc 1 M, F i) * (∑ j ∈ Finset.Icc 1 M, G j) := by
        rw [Finset.sum_mul_sum]
        exact Finset.sum_product _ _ _

/-- **The monotone-iteration bound.** If `φ` satisfies the system and `u` is a
super-solution at `x > 0`, every truncated weighted sum is dominated by `u`:
`certSum φ x T N ≤ u T`. Strong induction on `N`; within a fixed `N`, an inner
induction on `rank T` handles the `d`-empty branch (same `N`, smaller rank),
while both convolution factors drop to `N - 1` and use the outer hypothesis. -/
theorem BuiSystem.certSum_le {ι : Type*} (S : BuiSystem ι) {φ : ι → ℕ → ℕ}
    {x : ℚ} {u : ι → ℚ} (hφ : S.Satisfies φ) (hx : 0 < x) (hu : S.IsSuperSolution x u) :
    ∀ N T, certSum φ x T N ≤ u T := by
  obtain ⟨hbase, hrec⟩ := hφ
  obtain ⟨hupos, hsupb, hsupr⟩ := hu
  have hSnn : ∀ T M, 0 ≤ certSum φ x T M := fun T M =>
    Finset.sum_nonneg fun n _ => mul_nonneg (pow_nonneg hx.le n) (Nat.cast_nonneg _)
  -- the base-type bound, at every truncation order
  have hbaseN : ∀ N T, S.rule T = none → certSum φ x T N ≤ u T := by
    intro N T hT
    refine le_trans ?_ (hsupb T hT)
    rw [certSum]
    calc ∑ n ∈ Finset.Icc 1 N, x ^ n * (φ T n : ℚ)
        ≤ ∑ n ∈ Finset.Icc 1 N, (if n = 1 then x else 0) := by
          refine Finset.sum_le_sum fun n hn => ?_
          rcases eq_or_ne n 1 with rfl | hne
          · rw [if_pos rfl, pow_one]
            have h1 : (φ T 1 : ℚ) ≤ 1 := by exact_mod_cast (hbase T hT).1
            calc x * (φ T 1 : ℚ) ≤ x * 1 := mul_le_mul_of_nonneg_left h1 hx.le
              _ = x := mul_one x
          · rw [Finset.mem_Icc] at hn
            rw [if_neg hne, (hbase T hT).2 n (by omega)]
            simp
      _ ≤ x := by
          rw [Finset.sum_ite_eq' (Finset.Icc 1 N) 1 (fun _ => x)]
          split
          · exact le_rfl
          · exact hx.le
  intro N
  induction N using Nat.strong_induction_on with
  | _ N ihN =>
    cases N with
    | zero =>
      intro T
      rw [certSum, Finset.Icc_eq_empty (by omega), Finset.sum_empty]
      exact hupos T
    | succ M =>
      suffices h : ∀ r T, S.rank T ≤ r → certSum φ x T (M + 1) ≤ u T by
        intro T; exact h (S.rank T) T le_rfl
      intro r
      induction r with
      | zero =>
        intro T hT
        cases hrT : S.rule T with
        | none => exact hbaseN (M + 1) T hrT
        | some pr =>
          obtain ⟨T', D⟩ := pr
          exact absurd (S.rank_lt hrT) (by omega)
      | succ r ihr =>
        intro T hT
        cases hrT : S.rule T with
        | none => exact hbaseN (M + 1) T hrT
        | some pr =>
          obtain ⟨T', D⟩ := pr
          have hT' : S.rank T' ≤ r := by have := S.rank_lt hrT; omega
          -- termwise cast of the casing recurrence, with `x^n` split across
          -- the convolution
          have step1 : certSum φ x T (M + 1)
              ≤ certSum φ x T' (M + 1)
                + ∑ n ∈ Finset.Icc 1 (M + 1), ∑ i ∈ Finset.Ico 1 n,
                    (x ^ i * (φ T' i : ℚ)) * (x ^ (n - i) * (φ D (n - i) : ℚ)) := by
            rw [certSum, certSum, ← Finset.sum_add_distrib]
            refine Finset.sum_le_sum fun n hn => ?_
            have hcast : (φ T n : ℚ)
                ≤ (φ T' n : ℚ) + ∑ i ∈ Finset.Ico 1 n, (φ T' i : ℚ) * (φ D (n - i) : ℚ) := by
              have h := hrec T T' D hrT n
              have hq : ((φ T n : ℕ) : ℚ)
                  ≤ ((φ T' n + ∑ i ∈ Finset.Ico 1 n, φ T' i * φ D (n - i) : ℕ) : ℚ) := by
                exact_mod_cast h
              push_cast at hq
              exact hq
            calc x ^ n * (φ T n : ℚ)
                ≤ x ^ n * ((φ T' n : ℚ)
                    + ∑ i ∈ Finset.Ico 1 n, (φ T' i : ℚ) * (φ D (n - i) : ℚ)) :=
                  mul_le_mul_of_nonneg_left hcast (pow_nonneg hx.le n)
              _ = x ^ n * (φ T' n : ℚ) + ∑ i ∈ Finset.Ico 1 n,
                    (x ^ i * (φ T' i : ℚ)) * (x ^ (n - i) * (φ D (n - i) : ℚ)) := by
                  rw [mul_add, Finset.mul_sum]
                  congr 1
                  refine Finset.sum_congr rfl fun i hi => ?_
                  rw [Finset.mem_Ico] at hi
                  rw [show x ^ n = x ^ i * x ^ (n - i) by rw [← pow_add]; congr 1; omega]
                  ring
          -- the triangle-into-box convolution bound, both factors at order `M`
          have step2 : ∑ n ∈ Finset.Icc 1 (M + 1), ∑ i ∈ Finset.Ico 1 n,
                (x ^ i * (φ T' i : ℚ)) * (x ^ (n - i) * (φ D (n - i) : ℚ))
              ≤ certSum φ x T' M * certSum φ x D M :=
            conv_triangle_le
              (fun i => mul_nonneg (pow_nonneg hx.le i) (Nat.cast_nonneg _))
              (fun j => mul_nonneg (pow_nonneg hx.le j) (Nat.cast_nonneg _)) M
          have hT'N : certSum φ x T' (M + 1) ≤ u T' := ihr T' hT'
          have hT'M : certSum φ x T' M ≤ u T' := ihN M (by omega) T'
          have hDM : certSum φ x D M ≤ u D := ihN M (by omega) D
          have hprod : certSum φ x T' M * certSum φ x D M ≤ u T' * u D :=
            mul_le_mul hT'M hDM (hSnn D M) (hupos T')
          calc certSum φ x T (M + 1)
              ≤ certSum φ x T' (M + 1) + certSum φ x T' M * certSum φ x D M := by
                refine le_trans step1 ?_
                exact add_le_add (le_refl (certSum φ x T' (M + 1))) step2
            _ ≤ u T' + u T' * u D := add_le_add hT'N hprod
            _ ≤ u T := hsupr T T' D hrT

/-- **The single-term certificate bound**, division-free over `ℚ`:
`x^n · φ_T n ≤ u_T` for every `n ≥ 1` — one nonnegative term of `certSum`
against the full truncated sum. -/
theorem BuiSystem.pow_mul_le {ι : Type*} (S : BuiSystem ι) {φ : ι → ℕ → ℕ}
    {x : ℚ} {u : ι → ℚ} (hφ : S.Satisfies φ) (hx : 0 < x) (hu : S.IsSuperSolution x u)
    (T : ι) (n : ℕ) (hn : 1 ≤ n) : x ^ n * (φ T n : ℚ) ≤ u T := by
  refine le_trans ?_ (S.certSum_le hφ hx hu n T)
  rw [certSum]
  exact Finset.single_le_sum (f := fun m => x ^ m * (φ T m : ℚ))
    (fun m _ => mul_nonneg (pow_nonneg hx.le m) (Nat.cast_nonneg _))
    (Finset.mem_Icc.mpr ⟨hn, le_rfl⟩)

/-! ## From an exponential ceiling to `lambda` -/

/-- **The root-test transfer.** An exponential ceiling `a n ≤ C · y^n`
(all `n ≥ 1`, `C ≥ 1`, `y > 0`) forces `lambda ≤ y`: along `lambda_tendsto`,
`a(n)^{1/n} ≤ C^{1/n} · y → y` since `C^{1/n} = exp(log C / n) → 1`. -/
theorem lambda_le_of_pow_bound {C y : ℝ} (hC : 1 ≤ C) (hy : 0 < y)
    (h : ∀ n : ℕ, 1 ≤ n → (a n : ℝ) ≤ C * y ^ n) : lambda ≤ y := by
  have hC0 : (0 : ℝ) < C := lt_of_lt_of_le one_pos hC
  -- the majorant sequence tends to `y`
  have hexp : Filter.Tendsto (fun n : ℕ => Real.exp (Real.log C * (n : ℝ)⁻¹))
      Filter.atTop (𝓝 1) := by
    have hinv : Filter.Tendsto (fun n : ℕ => ((n : ℝ))⁻¹) Filter.atTop (𝓝 0) :=
      Filter.Tendsto.inv_tendsto_atTop tendsto_natCast_atTop_atTop
    have h0 : Filter.Tendsto (fun n : ℕ => Real.log C * (n : ℝ)⁻¹)
        Filter.atTop (𝓝 0) := by
      simpa using hinv.const_mul (Real.log C)
    have h1 := (Real.continuous_exp.tendsto 0).comp h0
    rw [Real.exp_zero] at h1
    exact h1
  have hlim : Filter.Tendsto (fun n : ℕ => C ^ ((n : ℝ)⁻¹) * y) Filter.atTop (𝓝 y) := by
    have h1 : Filter.Tendsto (fun n : ℕ => C ^ ((n : ℝ)⁻¹)) Filter.atTop (𝓝 1) := by
      refine hexp.congr fun n => ?_
      rw [Real.rpow_def_of_pos hC0]
    simpa using h1.mul_const y
  refine le_of_tendsto_of_tendsto lambda_tendsto hlim ?_
  filter_upwards [Filter.eventually_ge_atTop 1] with n hn
  have hnR : ((n : ℝ)) ≠ 0 := by
    have : (0 : ℝ) < (n : ℝ) := by exact_mod_cast hn
    exact ne_of_gt this
  calc (a n : ℝ) ^ ((n : ℝ)⁻¹)
      ≤ (C * y ^ n) ^ ((n : ℝ)⁻¹) :=
        Real.rpow_le_rpow (Nat.cast_nonneg _) (h n hn) (by positivity)
    _ = C ^ ((n : ℝ)⁻¹) * (y ^ n) ^ ((n : ℝ)⁻¹) :=
        Real.mul_rpow hC0.le (by positivity)
    _ = C ^ ((n : ℝ)⁻¹) * y := by
        rw [← Real.rpow_natCast y n, ← Real.rpow_mul hy.le,
          mul_inv_cancel₀ hnR, Real.rpow_one]

/-- **The abstract certificate theorem.** A Bui system satisfied by counting
functions `φ`, a rational super-solution `u` at `x > 0`, and the anchor
`a n ≤ φ_root n` together force `lambda ≤ 1/x`. -/
theorem lambda_le_of_buiSystem {ι : Type*} (S : BuiSystem ι) {φ : ι → ℕ → ℕ}
    {x : ℚ} {u : ι → ℚ} (root : ι) (hφ : S.Satisfies φ) (hx : 0 < x)
    (hu : S.IsSuperSolution x u) (hroot : ∀ n : ℕ, 1 ≤ n → a n ≤ φ root n) :
    lambda ≤ ((x⁻¹ : ℚ) : ℝ) := by
  have hxinv : (0 : ℝ) < ((x⁻¹ : ℚ) : ℝ) := by
    have h : (0 : ℚ) < x⁻¹ := inv_pos.mpr hx
    exact_mod_cast h
  refine lambda_le_of_pow_bound (C := max ((u root : ℚ) : ℝ) 1)
    (le_max_right _ _) hxinv ?_
  intro n hn
  have h1 : x ^ n * ((a n : ℕ) : ℚ) ≤ u root := by
    have hφn := S.pow_mul_le hφ hx hu root n hn
    have hanchor : ((a n : ℕ) : ℚ) ≤ (φ root n : ℚ) := by exact_mod_cast hroot n hn
    calc x ^ n * ((a n : ℕ) : ℚ) ≤ x ^ n * (φ root n : ℚ) :=
          mul_le_mul_of_nonneg_left hanchor (pow_nonneg hx.le n)
      _ ≤ u root := hφn
  have h2 : ((a n : ℕ) : ℚ) ≤ u root * (x⁻¹) ^ n := by
    have hxn : (0 : ℚ) < x ^ n := pow_pos hx n
    have h1' : ((a n : ℕ) : ℚ) * x ^ n ≤ u root := by rw [mul_comm]; exact h1
    rw [inv_pow, ← div_eq_mul_inv, le_div_iff₀ hxn]
    exact h1'
  have h3 : (a n : ℝ) ≤ ((u root : ℚ) : ℝ) * ((x⁻¹ : ℚ) : ℝ) ^ n := by
    exact_mod_cast h2
  calc (a n : ℝ) ≤ ((u root : ℚ) : ℝ) * ((x⁻¹ : ℚ) : ℝ) ^ n := h3
    _ ≤ max ((u root : ℚ) : ℝ) 1 * ((x⁻¹ : ℚ) : ℝ) ^ n :=
        mul_le_mul_of_nonneg_right (le_max_left _ _) (by positivity)

/-! ## The exported-data interface

A concrete certificate is exported (by `scripts/gen_bui_cert.lean.py`) with
all entries over one common denominator `CD`: type `i`'s certificate value is
`u_i = num i / CD` and the contraction rate is `x = X / CD`. The three tables
(casing rule, rank, numerator) are balanced search trees keyed by the type
index, so that a lookup is `log n` comparisons of `ℕ` literals — which the
kernel evaluates in constant time each — rather than a walk down a list.
`valid` packs every side condition — positivity, index bounds, rank descent,
and the super-solution inequalities in cleared-denominator integer form
`num a · CD + num a · num b ≤ num i · CD` — into one `Bool` the kernel decides
(`decide +kernel`); for the 5930-type RD = 3 certificate that is the whole
arithmetic side of the bound. -/

/-- A balanced binary search tree over `ℕ` keys: the certificate's index map.
The exported data files write these as literals. -/
inductive NatMap (α : Type) where
  /-- The empty map. -/
  | leaf : NatMap α
  /-- A node: everything in `l` has key `< k`, everything in `r` key `> k`. -/
  | node (l : NatMap α) (k : ℕ) (v : α) (r : NatMap α) : NatMap α

namespace NatMap

variable {α : Type}

/-- Look up key `i`. -/
def find? : NatMap α → ℕ → Option α
  | leaf, _ => none
  | node l k v r, i => if i < k then l.find? i else if k < i then r.find? i else some v

end NatMap

/-- A rational Bui certificate in exported form: `n` types indexed `0 … n-1`;
`rules` is the casing table (`none` = base, `some (a, b)` = split into
continuation `a` and convolution factor `b`); `ranks` the termination measure;
`nums i / CD` the certificate value `u_i`; `X / CD` the rate `x`; `root` the
anchor type. -/
structure RatCert where
  /-- Common denominator of all certificate entries. -/
  CD : ℕ
  /-- Numerator of the rate: `x = X / CD`, bounding `lambda ≤ CD / X`. -/
  X : ℕ
  /-- Index of the anchor (root) type. -/
  root : ℕ
  /-- The number of types. -/
  n : ℕ
  /-- The casing table. -/
  rules : NatMap (Option (ℕ × ℕ))
  /-- The termination measure (free-neighbor counts). -/
  ranks : NatMap ℕ
  /-- Certificate numerators: `u_i = num i / CD`. -/
  nums : NatMap ℕ

namespace RatCert

/-- The casing rule of type `i`; types outside `0 … n-1` are base types. -/
def rule (c : RatCert) (i : ℕ) : Option (ℕ × ℕ) :=
  if i < c.n then (c.rules.find? i).getD none else none

/-- The rank of type `i` (`0` if absent). -/
def rank (c : RatCert) (i : ℕ) : ℕ := (c.ranks.find? i).getD 0

/-- The certificate numerator of type `i` (`0` if absent). -/
def num (c : RatCert) (i : ℕ) : ℕ := (c.nums.find? i).getD 0

/-- The per-row check: base rows need `x ≤ u_i`, split rows need index bounds,
rank descent, and `u_a + u_a·u_b ≤ u_i` — all in cleared-denominator integer
arithmetic. -/
def rowOK (c : RatCert) (i : ℕ) : Bool :=
  match c.rule i with
  | none => decide (c.X ≤ c.num i)
  | some (a, b) =>
    decide (a < c.n) && decide (b < c.n) && decide (c.rank a < c.rank i) &&
    decide (c.num a * c.CD + c.num a * c.num b ≤ c.num i * c.CD)

/-- The whole-certificate check: positivity of `CD` and `X`, the anchor index
in range, and every row's `rowOK`. -/
def valid (c : RatCert) : Bool :=
  decide (0 < c.CD) && decide (0 < c.X) && decide (c.root < c.n) &&
  (List.range c.n).all c.rowOK

/-- **The combinatorial hypothesis bundle for an exported certificate**: there
exist counting functions on the certificate's index set satisfying the base
bounds, the casing recurrences, and the anchor `a n ≤ φ_root n`. This is the
part the Lean development does *not* prove for the king instances — see the
doc-comments on `KingBuiSystemRD2Holds` / `KingBuiSystemRD3Holds` for exactly
what stands behind it. -/
def SystemHolds (c : RatCert) : Prop :=
  ∃ φ : ℕ → ℕ → ℕ,
    (∀ i, i < c.n → c.rule i = none → φ i 1 ≤ 1 ∧ ∀ n, 2 ≤ n → φ i n = 0) ∧
    (∀ i a b, i < c.n → c.rule i = some (a, b) → ∀ n : ℕ,
      φ i n ≤ φ a n + ∑ j ∈ Finset.Ico 1 n, φ a j * φ b (n - j)) ∧
    (∀ n : ℕ, 1 ≤ n → a n ≤ φ c.root n)

/-- A split rule only occurs inside the index range. -/
lemma lt_of_rule_eq_some {c : RatCert} {i a b : ℕ} (h : c.rule i = some (a, b)) : i < c.n := by
  by_contra hcon
  simp [rule, hcon] at h

/-- **The certificate payoff**: a kernel-checked `valid` certificate plus its
combinatorial hypothesis bundle bound the growth constant, `lambda ≤ CD / X`. -/
theorem lambda_le (c : RatCert) (hv : c.valid = true) (hs : c.SystemHolds) :
    lambda ≤ (c.CD : ℝ) / (c.X : ℝ) := by
  classical
  simp only [valid, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hv
  obtain ⟨⟨⟨hCD, hX⟩, hrootlt⟩, hrows⟩ := hv
  have hrow : ∀ i, i < c.n → c.rowOK i = true := fun i hi =>
    hrows i (List.mem_range.mpr hi)
  -- unpack the two row shapes
  have hrowBase : ∀ i, i < c.n → c.rule i = none → c.X ≤ c.num i := by
    intro i hi hnone
    have h := hrow i hi
    simp only [rowOK, hnone, decide_eq_true_eq] at h
    exact h
  have hrowRec : ∀ i a b, i < c.n → c.rule i = some (a, b) →
      a < c.n ∧ b < c.n ∧ c.rank a < c.rank i ∧
      c.num a * c.CD + c.num a * c.num b ≤ c.num i * c.CD := by
    intro i a b hi hsome
    have h := hrow i hi
    simp only [rowOK, hsome, Bool.and_eq_true, decide_eq_true_eq] at h
    exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩
  -- assemble the abstract system over `ℕ`
  obtain ⟨φ₀, hb₀, hr₀, ha₀⟩ := hs
  have hCDQ : (0 : ℚ) < (c.CD : ℚ) := by exact_mod_cast hCD
  set x : ℚ := (c.X : ℚ) / (c.CD : ℚ) with hxdef
  have hxpos : 0 < x := by
    rw [hxdef]
    have hXQ : (0 : ℚ) < (c.X : ℚ) := by exact_mod_cast hX
    exact div_pos hXQ hCDQ
  set u : ℕ → ℚ := fun i => if i < c.n then (c.num i : ℚ) / (c.CD : ℚ) else x with hudef
  set φ : ℕ → ℕ → ℕ :=
    fun i n => if i < c.n then φ₀ i n else (if n = 1 then 1 else 0) with hφdef
  have hrank_lt : ∀ ⦃i a b⦄, c.rule i = some (a, b) → c.rank a < c.rank i := by
    intro i a b hsome
    exact (hrowRec i a b (lt_of_rule_eq_some hsome) hsome).2.2.1
  set S : BuiSystem ℕ := ⟨c.rule, c.rank, hrank_lt⟩ with hSdef
  have hSat : S.Satisfies φ := by
    constructor
    · intro i hnone
      by_cases hi : i < c.n
      · simp only [hφdef, hi, if_true]
        exact hb₀ i hi hnone
      · simp only [hφdef, hi, if_false]
        refine ⟨le_rfl, fun n hn => ?_⟩
        rw [if_neg (by omega)]
    · intro i A B hsome n
      have hi := lt_of_rule_eq_some hsome
      have hab := hrowRec i A B hi hsome
      simp only [hφdef, hi, hab.1, hab.2.1, if_true]
      exact hr₀ i A B hi hsome n
  have hSuper : S.IsSuperSolution x u := by
    refine ⟨?_, ?_, ?_⟩
    · intro i
      simp only [hudef]
      split
      · positivity
      · exact hxpos.le
    · intro i hnone
      by_cases hi : i < c.n
      · have hXle := hrowBase i hi hnone
        simp only [hudef, hi, if_true, hxdef]
        rw [div_le_div_iff_of_pos_right hCDQ]
        exact_mod_cast hXle
      · simp only [hudef, hi, if_false]
        exact le_rfl
    · intro i A B hsome
      have hi := lt_of_rule_eq_some hsome
      have hab := hrowRec i A B hi hsome
      simp only [hudef, hi, hab.1, hab.2.1, if_true]
      have hint : ((c.num A : ℚ) * c.CD + (c.num A : ℚ) * c.num B)
          ≤ (c.num i : ℚ) * c.CD := by exact_mod_cast hab.2.2.2
      have hc2 : (0 : ℚ) < (c.CD : ℚ) * (c.CD : ℚ) := by positivity
      have key : ((c.num A : ℚ) * c.CD + (c.num A : ℚ) * c.num B) / ((c.CD : ℚ) * c.CD)
          ≤ ((c.num i : ℚ) * c.CD) / ((c.CD : ℚ) * c.CD) := by
        rw [div_le_div_iff_of_pos_right hc2]
        exact hint
      have e1 : (c.num A : ℚ) / c.CD + ((c.num A : ℚ) / c.CD) * ((c.num B : ℚ) / c.CD)
          = ((c.num A : ℚ) * c.CD + (c.num A : ℚ) * c.num B) / ((c.CD : ℚ) * c.CD) := by
        field_simp
      have e2 : (c.num i : ℚ) / c.CD = ((c.num i : ℚ) * c.CD) / ((c.CD : ℚ) * c.CD) := by
        rw [mul_div_mul_right _ _ (ne_of_gt hCDQ)]
      rw [e1, e2]
      exact key
  have hanchor : ∀ n : ℕ, 1 ≤ n → a n ≤ φ c.root n := by
    intro n hn
    simp only [hφdef, hrootlt, if_true]
    exact ha₀ n hn
  have hmain := lambda_le_of_buiSystem S (root := c.root) hSat hxpos hSuper hanchor
  have hcast : ((x⁻¹ : ℚ) : ℝ) = (c.CD : ℝ) / (c.X : ℝ) := by
    rw [hxdef, inv_div]
    push_cast
    ring
  rwa [hcast] at hmain

end RatCert

end Polyplets
