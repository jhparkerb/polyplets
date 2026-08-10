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
  sorry

/-- Under `LocFin`, the coefficient sum can read any horizon `≥ n`. -/
theorem coeff_lfsum_of_le (F : ℕ → PowerSeries ℚ) (hF : LocFin F)
    (n N : ℕ) (h : n < N) :
    (coeff n) (lfsum F) = ∑ g ∈ Finset.range N, (coeff n) (F g) := by
  sorry

theorem lfsum_add (F G : ℕ → PowerSeries ℚ) :
    lfsum (fun g => F g + G g) = lfsum F + lfsum G := by
  sorry

theorem lfsum_sub (F G : ℕ → PowerSeries ℚ) :
    lfsum (fun g => F g - G g) = lfsum F - lfsum G := by
  sorry

theorem lfsum_smul (c : ℚ) (F : ℕ → PowerSeries ℚ) :
    lfsum (fun g => c • F g) = c • lfsum F := by
  sorry

/-- A fixed factor passes through a locally finite sum. This is the one
lemma where locality is essential: the interchange discards cross terms
`coeff j (F g)` with `j < g`, which `LocFin` kills. -/
theorem lfsum_mul_left (c : PowerSeries ℚ) (F : ℕ → PowerSeries ℚ)
    (hF : LocFin F) :
    c * lfsum F = lfsum fun g => c * F g := by
  sorry

/-- A family supported below `K` sums to its finite sum. -/
theorem lfsum_of_support_lt (F : ℕ → PowerSeries ℚ) (K : ℕ)
    (h : ∀ g, K ≤ g → F g = 0) :
    lfsum F = ∑ g ∈ Finset.range K, F g := by
  sorry

/-- Splitting off the first `K` terms of a locally finite sum. -/
theorem lfsum_split (F : ℕ → PowerSeries ℚ) (hF : LocFin F) (K : ℕ) :
    lfsum F = (∑ g ∈ Finset.range K, F g) +
      lfsum fun g => if g < K then 0 else F g := by
  sorry

/-- A locally finite family vanishing below `K` can be reindexed from 0. -/
theorem lfsum_shift (F : ℕ → PowerSeries ℚ) (hF : LocFin F) (K : ℕ)
    (h0 : ∀ g, g < K → F g = 0) :
    lfsum F = lfsum fun g => F (g + K) := by
  sorry

/-! ## Geometric locality -/

/-- Powers of a series with zero constant term gain order. -/
theorem coeff_pow_eq_zero (u : PowerSeries ℚ) (hu : constantCoeff u = 0)
    (g n : ℕ) (h : n < g) : (coeff n) (u ^ g) = 0 := by
  sorry

/-- Families `a_g · u^g` are locally finite when `u` has positive order. -/
theorem locFin_geom (a : ℕ → PowerSeries ℚ) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    LocFin fun g => a g * u ^ g := by
  sorry

/-! ## The truncation homomorphism onto the list model

`GapWalkBridge`'s `tmul`/`tinvAux` compute truncated products and inverses
on `List ℚ`; these lemmas say they compute the coefficients of the real
thing. Piece K's finite certificates evaluate on the list side. -/

/-- The first `N` coefficients, as a list. -/
noncomputable def truncL (N : ℕ) (F : PowerSeries ℚ) : List ℚ :=
  (List.range N).map fun n => (coeff n) F

@[simp] theorem truncL_length (N : ℕ) (F : PowerSeries ℚ) :
    (truncL N F).length = N := by
  sorry

theorem truncL_getD (N n : ℕ) (F : PowerSeries ℚ) (h : n < N) :
    (truncL N F).getD n 0 = (coeff n) F := by
  sorry

theorem truncL_mk (N : ℕ) (f : ℕ → ℚ) :
    truncL N (PowerSeries.mk f) = (List.range N).map f := by
  sorry

/-- Truncation turns products into `tmul`. -/
theorem truncL_mul (N : ℕ) (F G : PowerSeries ℚ) :
    truncL N (F * G) = GapWalkBridge.tmul (truncL N F) (truncL N G) N := by
  sorry

/-- Truncation turns inverses into `tinvAux` (field inverse, unit `F`). -/
theorem truncL_inv (N : ℕ) (F : PowerSeries ℚ)
    (hF : constantCoeff F ≠ 0) :
    truncL (N + 1) F⁻¹ = GapWalkBridge.tinvAux (truncL (N + 1) F) N := by
  sorry

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
