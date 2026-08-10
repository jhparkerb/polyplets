/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.RingTheory.PowerSeries.Inverse
import Polyplets.GapWalkBridge

/-!
# Notary piece K, module 2: locally finite sums over `ℚ⟦X⟧`

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`. The kernel
derivation evaluates the walk's gap-generating series at the small kernel
roots — sums `Σ_g a_g·u^g` with infinitely many terms. Because `u` has
positive order, term `g` contributes nothing below coefficient `g`, so the
sum is *coefficient-wise finite*: no topology, no Mathlib summability. This
module is the small library that makes such sums honest citizens of
`PowerSeries ℚ`:

* `LocFin F` — the locality hypothesis: term `g` vanishes below order `g`;
* `lfsum F` — the sum, defined coefficient-wise
  (`coeff n = Σ_{g ≤ n} coeff n (F g)`);
* linearity, fixed-factor pull-through (`lfsum_mul_left`), finite collapse
  (`lfsum_of_support_lt`), head split (`lfsum_split`), reindexing
  (`lfsum_shift`), and the geometric fact that families `a_g·u^g` with
  `constantCoeff u = 0` are `LocFin`;
* the truncation homomorphism `truncL` onto the list model of
  `GapWalkBridge` (`tmul`, `tinvAux`) — how piece K's finite certificates
  (determinant coefficients) will be computed without leaving standard
  axioms.

Everything here is generic bookkeeping: no walk, no roots. Proof recipes
are one `ext`/`coeff` computation each; `PowerSeries.coeff_mul` gives the
antidiagonal form of products, `PowerSeries.coeff_inv` the inverse
recursion, and `Finset.sum_comm` / `Finset.sum_subset` the interchange of
the two finite sums in `lfsum_mul_left` (the discarded terms die by
`LocFin`).
-/

namespace Polyplets
namespace KernelSeries

open PowerSeries

/-- Locally finite family: term `g` has no coefficients below order `g`. -/
def LocFin (F : ℕ → PowerSeries ℚ) : Prop :=
  ∀ g n, n < g → (coeff n) (F g) = 0

/-- The coefficient-wise sum of a family: at order `n`, only terms
`g ≤ n` are read. Under `LocFin` this is the sum of the family in every
reasonable sense; without it, it is still a well-defined operation. -/
noncomputable def lfsum (F : ℕ → PowerSeries ℚ) : PowerSeries ℚ :=
  PowerSeries.mk fun n => ∑ g ∈ Finset.range (n + 1), (coeff n) (F g)

@[simp] theorem coeff_lfsum (F : ℕ → PowerSeries ℚ) (n : ℕ) :
    (coeff n) (lfsum F) = ∑ g ∈ Finset.range (n + 1), (coeff n) (F g) := by
  simp [lfsum, PowerSeries.coeff_mk]

/-- Under `LocFin`, the coefficient sum can read any horizon `≥ n`. -/
theorem coeff_lfsum_of_le (F : ℕ → PowerSeries ℚ) (hF : LocFin F)
    (n N : ℕ) (h : n < N) :
    (coeff n) (lfsum F) = ∑ g ∈ Finset.range N, (coeff n) (F g) := by
  rw [coeff_lfsum]
  refine Finset.sum_subset (Finset.range_subset_range.mpr h) ?_
  intro g _ hg
  simp only [Finset.mem_range, not_lt] at hg
  exact hF g n hg

theorem lfsum_add (F G : ℕ → PowerSeries ℚ) :
    lfsum (fun g => F g + G g) = lfsum F + lfsum G := by
  apply PowerSeries.ext
  intro n
  simp only [coeff_lfsum, map_add]
  rw [Finset.sum_add_distrib]

theorem lfsum_sub (F G : ℕ → PowerSeries ℚ) :
    lfsum (fun g => F g - G g) = lfsum F - lfsum G := by
  apply PowerSeries.ext
  intro n
  simp only [coeff_lfsum, map_sub]
  rw [Finset.sum_sub_distrib]

theorem lfsum_smul (c : ℚ) (F : ℕ → PowerSeries ℚ) :
    lfsum (fun g => c • F g) = c • lfsum F := by
  apply PowerSeries.ext
  intro n
  simp only [coeff_lfsum, map_smul, smul_eq_mul]
  rw [Finset.mul_sum]

/-- A fixed factor passes through a locally finite sum. This is the one
lemma where locality is essential: the interchange discards cross terms
`coeff j (F g)` with `j < g`, which `LocFin` kills. -/
theorem lfsum_mul_left (c : PowerSeries ℚ) (F : ℕ → PowerSeries ℚ)
    (hF : LocFin F) :
    c * lfsum F = lfsum fun g => c * F g := by
  apply PowerSeries.ext
  intro n
  rw [PowerSeries.coeff_mul, coeff_lfsum]
  have hstep : ∀ p ∈ Finset.antidiagonal n,
      (coeff p.1) c * (coeff p.2) (lfsum F) =
        ∑ g ∈ Finset.range (n + 1), (coeff p.1) c * (coeff p.2) (F g) := by
    intro p hp
    rw [coeff_lfsum_of_le F hF p.2 (n + 1) (Finset.Nat.antidiagonal.snd_lt hp),
      Finset.mul_sum]
  rw [Finset.sum_congr rfl hstep, Finset.sum_comm]
  refine Finset.sum_congr rfl fun g _ => ?_
  rw [coeff_mul]

/-- Splitting off the first `K` terms of a locally finite sum. -/
theorem lfsum_split (F : ℕ → PowerSeries ℚ) (hF : LocFin F) (K : ℕ) :
    lfsum F = (∑ g ∈ Finset.range K, F g) +
      lfsum fun g => if g < K then 0 else F g := by
  apply PowerSeries.ext
  intro n
  rw [map_add, coeff_lfsum, map_sum, coeff_lfsum]
  have hcoeff : ∀ g, (coeff n) (if g < K then (0 : PowerSeries ℚ) else F g) =
      if g < K then (0 : ℚ) else (coeff n) (F g) := by
    intro g; split <;> simp
  rw [Finset.sum_congr rfl fun g (_ : g ∈ Finset.range (n + 1)) => hcoeff g,
    Finset.sum_ite (fun _ : ℕ => (0 : ℚ)) (fun g => (coeff n) (F g)),
    Finset.sum_const_zero, zero_add]
  rcases Nat.lt_or_ge (n + 1) K with hK | hK
  · have hempty : (Finset.range (n + 1)).filter (fun g => ¬ g < K) = ∅ := by
      apply Finset.filter_eq_empty_iff.mpr
      intro g hg
      simp only [Finset.mem_range] at hg
      simp only [not_not]
      exact lt_trans hg hK
    rw [hempty, Finset.sum_empty, add_zero]
    exact Finset.sum_subset (Finset.range_subset_range.mpr hK.le) fun g _ hg => by
      simp only [Finset.mem_range, not_lt] at hg
      exact hF g n hg
  · have hEq : Finset.range K = (Finset.range (n + 1)).filter (fun g => g < K) := by
      ext g
      simp only [Finset.mem_range, Finset.mem_filter]
      exact ⟨fun h => ⟨lt_of_lt_of_le h hK, h⟩, fun h => h.2⟩
    rw [hEq]
    exact (Finset.sum_filter_add_sum_filter_not _ _ _).symm

/-- A locally finite family supported below `K` sums to its finite sum. -/
theorem lfsum_of_support_lt (F : ℕ → PowerSeries ℚ) (hF : LocFin F) (K : ℕ)
    (h : ∀ g, K ≤ g → F g = 0) :
    lfsum F = ∑ g ∈ Finset.range K, F g := by
  rw [lfsum_split F hF K]
  have hzero : (fun g => if g < K then (0 : PowerSeries ℚ) else F g) =
      fun _ => 0 := by
    funext g
    by_cases hg : g < K
    · simp [hg]
    · simp [hg, h g (le_of_not_gt hg)]
  have hz : lfsum (fun _ => (0 : PowerSeries ℚ)) = 0 := by
    apply PowerSeries.ext
    intro n
    simp
  rw [hzero, hz, add_zero]

/-- A locally finite family vanishing below `K` can be reindexed from 0. -/
theorem lfsum_shift (F : ℕ → PowerSeries ℚ) (hF : LocFin F) (K : ℕ)
    (h0 : ∀ g, g < K → F g = 0) :
    lfsum F = lfsum fun g => F (g + K) := by
  apply PowerSeries.ext
  intro n
  rw [coeff_lfsum, coeff_lfsum]
  have hLHS : ∑ g ∈ Finset.range (n + 1), (coeff n) (F g) =
      ∑ g ∈ (Finset.range (n + 1)).filter (fun g => K ≤ g), (coeff n) (F g) := by
    refine (Finset.sum_subset (Finset.filter_subset _ _) ?_).symm
    intro g hg hgs
    simp only [Finset.mem_filter, Finset.mem_range, not_and, not_le] at hgs
    rw [h0 g (hgs (Finset.mem_range.mp hg))]
    simp
  have hRHS : ∑ g ∈ Finset.range (n + 1), (coeff n) (F (g + K)) =
      ∑ g ∈ (Finset.range (n + 1)).filter (fun g => g + K ≤ n), (coeff n) (F (g + K)) := by
    refine (Finset.sum_subset (Finset.filter_subset _ _) ?_).symm
    intro g hg hgs
    simp only [Finset.mem_filter, Finset.mem_range, not_and, not_le] at hgs
    exact hF (g + K) n (hgs (Finset.mem_range.mp hg))
  rw [hLHS, hRHS]
  refine Finset.sum_nbij' (fun g => g - K) (fun g => g + K) ?_ ?_ ?_ ?_ ?_
  · intro a ha
    simp only [Finset.mem_filter, Finset.mem_range] at ha ⊢
    obtain ⟨ha1, ha2⟩ := ha
    refine ⟨Nat.lt_succ_iff.mpr (Nat.sub_le a K |>.trans (Nat.lt_succ_iff.mp ha1)), ?_⟩
    rw [Nat.sub_add_cancel ha2]
    exact Nat.lt_succ_iff.mp ha1
  · intro a ha
    simp only [Finset.mem_filter, Finset.mem_range] at ha ⊢
    exact ⟨Nat.lt_succ_iff.mpr ha.2, Nat.le_add_left K a⟩
  · intro a ha
    simp only [Finset.mem_filter, Finset.mem_range] at ha
    exact Nat.sub_add_cancel ha.2
  · intro a _
    exact Nat.add_sub_cancel a K
  · intro a ha
    simp only [Finset.mem_filter, Finset.mem_range] at ha
    rw [Nat.sub_add_cancel ha.2]

/-! ## Geometric locality -/

/-- Powers of a series with zero constant term gain order. -/
theorem coeff_pow_eq_zero (u : PowerSeries ℚ) (hu : constantCoeff u = 0)
    (g n : ℕ) (h : n < g) : (coeff n) (u ^ g) = 0 := by
  induction g generalizing n with
  | zero => omega
  | succ g ih =>
    rw [pow_succ, coeff_mul]
    apply Finset.sum_eq_zero
    intro p hp
    rw [Finset.mem_antidiagonal] at hp
    rcases Nat.eq_zero_or_pos p.2 with hp2 | hp2
    · rw [hp2, coeff_zero_eq_constantCoeff_apply, hu, mul_zero]
    · have hp1 : p.1 < g := by omega
      rw [ih p.1 hp1, zero_mul]

/-- Families `a_g · u^g` are locally finite when `u` has positive order. -/
theorem locFin_geom (a : ℕ → PowerSeries ℚ) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    LocFin fun g => a g * u ^ g := by
  intro g n hn
  rw [coeff_mul]
  apply Finset.sum_eq_zero
  intro p hp
  rw [Finset.mem_antidiagonal] at hp
  have hp2 : p.2 < g := by omega
  rw [coeff_pow_eq_zero u hu g p.2 hp2, mul_zero]

/-! ## The truncation homomorphism onto the list model

`GapWalkBridge`'s `tmul`/`tinvAux` compute truncated products and inverses
on `List ℚ`; these lemmas say they compute the coefficients of the real
thing. Piece K's finite certificates evaluate on the list side. -/

/-- The first `N` coefficients, as a list. -/
noncomputable def truncL (N : ℕ) (F : PowerSeries ℚ) : List ℚ :=
  (List.range N).map fun n => (coeff n) F

@[simp] theorem truncL_length (N : ℕ) (F : PowerSeries ℚ) :
    (truncL N F).length = N := by
  simp [truncL, List.length_map, List.length_range]

theorem truncL_getD (N n : ℕ) (F : PowerSeries ℚ) (h : n < N) :
    (truncL N F).getD n 0 = (coeff n) F := by
  have hn : n < (truncL N F).length := by rw [truncL_length]; exact h
  rw [List.getD_eq_getElem _ _ hn]
  show ((List.range N).map fun n => (coeff n) F)[n] = (coeff n) F
  rw [List.getElem_map]
  congr 1
  rw [List.getElem_range]

theorem truncL_mk (N : ℕ) (f : ℕ → ℚ) :
    truncL N (PowerSeries.mk f) = (List.range N).map f := by
  simp [truncL, PowerSeries.coeff_mk]

private theorem list_sum_range_eq_sum (n : ℕ) (f : ℕ → ℚ) :
    ((List.range n).map f).sum = ∑ i ∈ Finset.range n, f i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.sum_range_succ, Finset.sum_range_succ, ih]

/-- Truncation turns products into `tmul`. -/
theorem truncL_mul (N : ℕ) (F G : PowerSeries ℚ) :
    truncL N (F * G) = GapWalkBridge.tmul (truncL N F) (truncL N G) N := by
  show (List.range N).map (fun n => (coeff n) (F * G)) =
    GapWalkBridge.tmul (truncL N F) (truncL N G) N
  unfold GapWalkBridge.tmul
  refine List.map_congr_left ?_
  intro k hk
  rw [List.mem_range] at hk
  rw [coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ
    (fun i j => (coeff i) F * (coeff j) G), list_sum_range_eq_sum]
  refine Finset.sum_congr rfl ?_
  intro i hi
  rw [Finset.mem_range] at hi
  rw [truncL_getD N i F (by omega), truncL_getD N (k - i) G (by omega)]

private theorem tinvAux_length (a : List ℚ) (n : ℕ) :
    (GapWalkBridge.tinvAux a n).length = n + 1 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [GapWalkBridge.tinvAux, ih]

private theorem tinvAux_getD_lt (a : List ℚ) (n k : ℕ) (hk : k < n + 1) :
    (GapWalkBridge.tinvAux a (n + 1)).getD k 0 = (GapWalkBridge.tinvAux a n).getD k 0 := by
  have hlen : k < (GapWalkBridge.tinvAux a n).length := by rw [tinvAux_length]; exact hk
  show ((GapWalkBridge.tinvAux a n) ++
    [-(a.getD 0 0)⁻¹ * ((List.range (n + 1)).map fun i =>
      a.getD (i + 1) 0 * (GapWalkBridge.tinvAux a n).getD (n - i) 0).sum]).getD k 0 =
      (GapWalkBridge.tinvAux a n).getD k 0
  rw [List.getD_append _ _ _ k hlen]

private theorem tinvAux_getD_eq (F : PowerSeries ℚ) (N : ℕ) (_hF : constantCoeff F ≠ 0) :
    ∀ n, n ≤ N → ∀ k, k ≤ n →
      (GapWalkBridge.tinvAux (truncL (N + 1) F) n).getD k 0 = (coeff k) F⁻¹ := by
  intro n
  induction n with
  | zero =>
    intro _ k hk
    have hk0 : k = 0 := Nat.le_zero.mp hk
    subst hk0
    show (GapWalkBridge.tinvAux (truncL (N + 1) F) 0).getD 0 0 = (coeff 0) F⁻¹
    show ([(((truncL (N + 1) F)).getD 0 0)⁻¹] : List ℚ).getD 0 0 = (coeff 0) F⁻¹
    rw [truncL_getD (N + 1) 0 F (by omega), coeff_inv, coeff_zero_eq_constantCoeff_apply]
    simp
  | succ n ih =>
    intro hnN k hk
    rcases Nat.lt_or_ge k (n + 1) with hklt | hkge
    · rw [tinvAux_getD_lt _ n k hklt]
      exact ih (by omega) k (by omega)
    · have hkeq : k = n + 1 := le_antisymm hk hkge
      subst hkeq
      set a := truncL (N + 1) F with ha
      set b := GapWalkBridge.tinvAux a n with hb
      have haGetD : ∀ i, i < N + 1 → a.getD i 0 = (coeff i) F := by
        intro i hi; rw [ha]; exact truncL_getD (N + 1) i F hi
      have hgoal : (GapWalkBridge.tinvAux a (n + 1)).getD (n + 1) 0 =
          -(a.getD 0 0)⁻¹ * ((List.range (n + 1)).map fun i =>
            a.getD (i + 1) 0 * b.getD (n - i) 0).sum := by
        show (b ++ [-(a.getD 0 0)⁻¹ * ((List.range (n + 1)).map fun i =>
          a.getD (i + 1) 0 * b.getD (n - i) 0).sum]).getD (n + 1) 0 = _
        rw [List.getD_append_right _ _ _ (n + 1) (by rw [hb, tinvAux_length])]
        rw [hb, tinvAux_length]
        simp
      rw [hgoal]
      rw [haGetD 0 (by omega), coeff_zero_eq_constantCoeff_apply]
      rw [coeff_inv (n + 1) F]
      rw [if_neg (Nat.succ_ne_zero n)]
      rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ
        (fun i j => if j < n + 1 then (coeff i) F * (coeff j) F⁻¹ else 0)]
      rw [Finset.sum_range_succ']
      have hf0 : (if n + 1 - 0 < n + 1 then (coeff 0) F * (coeff (n + 1 - 0)) F⁻¹ else 0)
          = (0 : ℚ) := by simp
      rw [hf0, add_zero]
      congr 1
      rw [list_sum_range_eq_sum]
      refine Finset.sum_congr rfl ?_
      intro i hi
      rw [Finset.mem_range] at hi
      have h1 : n + 1 - (i + 1) < n + 1 := by omega
      rw [if_pos h1]
      rw [haGetD (i + 1) (by omega)]
      have heq : n + 1 - (i + 1) = n - i := by omega
      rw [heq]
      congr 1
      rw [hb]
      exact ih (by omega) (n - i) (by omega)

/-- Truncation turns inverses into `tinvAux` (field inverse, unit `F`). -/
theorem truncL_inv (N : ℕ) (F : PowerSeries ℚ)
    (hF : constantCoeff F ≠ 0) :
    truncL (N + 1) F⁻¹ = GapWalkBridge.tinvAux (truncL (N + 1) F) N := by
  apply List.ext_getElem
  · rw [truncL_length, tinvAux_length]
  · intro k h1 h2
    rw [← List.getD_eq_getElem _ 0 h1, ← List.getD_eq_getElem _ 0 h2]
    rw [truncL_length] at h1
    rw [truncL_getD (N + 1) k F⁻¹ h1]
    exact (tinvAux_getD_eq F N hF N le_rfl k (by omega)).symm

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.KernelSeries.lfsum_mul_left' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms lfsum_mul_left

/--
info: 'Polyplets.KernelSeries.truncL_inv' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms truncL_inv

end KernelSeries
end Polyplets
