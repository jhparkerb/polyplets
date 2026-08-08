/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib

/-!
# House arrest: bounded degree plus bounded house is a finite condition

An algebraic integer's *house* is the largest modulus among its Galois
conjugates — equivalently, among the complex roots of its minimal polynomial.
This file proves that for each fixed degree bound `d` and house bound `B`,
only finitely many algebraic integers qualify, and deduces the form actually
used downstream: a sequence of *pairwise distinct* algebraic integers with a
uniform house bound must have unbounded degree.

Nothing here mentions animals; the file is the project's reusable
number-theory shim.

## Main results

* `mahlerMeasure_minpoly_le` — a house bound `B` on `x` forces
  `M(minpoly ℤ x) ≤ (max 1 B) ^ deg(minpoly ℤ x)`.
* `finite_setOf_isIntegral_of_house_le` — Northcott at bounded degree and
  house: finitely many such `x : ℂ`.
* `finite_setOf_degree_le_of_house_le` — for an injective family `μ : ℕ → ℂ`
  of algebraic integers with uniform house bound, only finitely many indices
  carry degree `≤ d`.
* `unbounded_degree_of_house_le` — the step-4 form: such a family has
  unbounded degree.

## What this discharges

Step 4 (Northcott finiteness) of the unconditional
non-D-finiteness theorem of `results/anisotropic-not-dfinite.md`, i.e. "the
strip growth constants `μ_H`, pairwise distinct algebraic integers with house
`< λ ≤ 9.3154`, have unbounded degree".

Steps 1–3 and 5 remain unformalized and are out of scope here: Fatou's lemma
for integer rational series, Pringsheim positivity, the Perron–Frobenius
strict-monotonicity step (Mathlib has no Perron root theory), and any Lean
notion of D-finiteness at all. So this file is a reusable ingredient, not the
theorem.

## Why two forms (finiteness and unboundedness)

`finite_setOf_degree_le_of_house_le` is the finiteness form of step 4; it is
strictly stronger than the brief's pinned `unbounded_degree_of_house_le`
(which is derived from it below), matches the paper's step (iv) more
literally, and costs nothing extra — so both are proved and both are
guarded.

Correction (2026-07-31 adversarial review): an earlier revision of this note
claimed the finiteness form was *needed* because "bare unboundedness does not
contradict step 5 — the offending `H` could be one of the `r` exceptions".
That was a quantifier slip: step 5's exceptional set is finite, degrees on a
finite set are bounded, and unboundedness beyond that bound already yields
the contradiction (machine-checked during the review). Neither form is
mathematically deficient; the finiteness form is kept as the primary export
because it is the closer match to the paper's (iv).

## Provenance note

The heavy half is Mathlib's, not ours: `Polynomial.finite_mahlerMeasure_le`
(Northcott for the Mahler measure) and `Polynomial.pow_eq_one_of_mahlerMeasure_eq_one`
(Kronecker) landed in Mathlib in 2025 (Fabrizio Barroero,
`Mathlib/NumberTheory/MahlerMeasure.lean`). The 2026-07-30 claims audit's note
that "Mathlib only has fixed-field `finite_of_norm_le`" is superseded — record
that correction. What remains, and is all this file does, is the bridge from a
house bound to a Mahler-measure bound and back out to a statement about
numbers rather than polynomials.
-/

namespace Polyplets

open Polynomial

/-- The conjugates of an algebraic integer `x : ℂ` are the complex roots of its
minimal polynomial. A house bound `B` on those roots bounds the Mahler measure
of the minimal polynomial by `(max 1 B) ^ deg`.

The proof is the factorization `M(p) = ‖lead p‖ * ∏_{z ∈ roots} max 1 ‖z‖`
(`mahlerMeasure_eq_leadingCoeff_mul_prod_roots`); the minimal polynomial is
monic so the leading factor is `1`, each root factor is at most `max 1 B`, and
there are exactly `natDegree` roots because `ℂ` is algebraically closed. -/
theorem mahlerMeasure_minpoly_le {x : ℂ} (hx : IsIntegral ℤ x) {B : ℝ}
    (hB : ∀ z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots, ‖z‖ ≤ B) :
    ((minpoly ℤ x).map (Int.castRingHom ℂ)).mahlerMeasure
      ≤ max 1 B ^ (minpoly ℤ x).natDegree := by
  set p : ℂ[X] := (minpoly ℤ x).map (Int.castRingHom ℂ) with hp
  have hmonic : p.Monic := (minpoly.monic hx).map _
  have hcard : p.roots.card = p.natDegree :=
    splits_iff_card_roots.mp (IsAlgClosed.splits p)
  have hdeg : p.natDegree = (minpoly ℤ x).natDegree :=
    (minpoly.monic hx).natDegree_map _
  rw [mahlerMeasure_eq_leadingCoeff_mul_prod_roots, hmonic.leadingCoeff, norm_one, one_mul]
  calc (p.roots.map fun a ↦ max 1 ‖a‖).prod
      ≤ (p.roots.map fun _ ↦ max 1 B).prod :=
        Multiset.prod_map_le_prod_map₀ _ _
          (fun i _ ↦ le_trans zero_le_one (le_max_left 1 ‖i‖))
          (fun i hi ↦ max_le_max le_rfl (hB i hi))
    _ = max 1 B ^ (minpoly ℤ x).natDegree := by
        rw [Multiset.map_const', Multiset.prod_replicate, hcard, hdeg]

/-- **Northcott at bounded degree and house**: there are only finitely many
algebraic integers `x : ℂ` whose minimal polynomial has degree at most `d` and
all of whose conjugates lie in the closed disc of radius `B`.

Each such `x` is a root of its minimal polynomial, which lives in the finite
set supplied by `Polynomial.finite_mahlerMeasure_le` at degree bound `d` and
Mahler-measure bound `(max 1 B) ^ d`; a finite union of finite root sets is
finite. -/
theorem finite_setOf_isIntegral_of_house_le (d : ℕ) (B : ℝ) :
    {x : ℂ | IsIntegral ℤ x ∧ (minpoly ℤ x).natDegree ≤ d ∧
      ∀ z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots, ‖z‖ ≤ B}.Finite := by
  have hB0 : (0 : ℝ) ≤ max 1 B ^ d := by positivity
  -- The finite pool of candidate minimal polynomials (Mathlib's Northcott).
  have hPfin := Polynomial.finite_mahlerMeasure_le d (Real.toNNReal (max 1 B ^ d))
  -- Every qualifying `x` is a root of a polynomial from that pool.
  refine Set.Finite.subset
    (hPfin.biUnion (t := fun p ↦ {z : ℂ | z ∈ (p.map (Int.castRingHom ℂ)).roots})
      fun p _ ↦ Multiset.finite_toSet _) ?_
  rintro x ⟨hx, hdeg, hhouse⟩
  have hmem : minpoly ℤ x ∈ {p : ℤ[X] | p.natDegree ≤ d ∧
      (p.map (Int.castRingHom ℂ)).mahlerMeasure ≤ (Real.toNNReal (max 1 B ^ d) : ℝ)} := by
    refine ⟨hdeg, ?_⟩
    rw [Real.coe_toNNReal _ hB0]
    exact (mahlerMeasure_minpoly_le hx hhouse).trans
      (pow_le_pow_right₀ (le_max_left 1 B) hdeg)
  have hne : (minpoly ℤ x).map (Int.castRingHom ℂ) ≠ 0 :=
    ((minpoly.monic hx).map (Int.castRingHom ℂ)).ne_zero
  have hroot : x ∈ {z : ℂ | z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots} := by
    have h := minpoly.aeval ℤ x
    rw [aeval_def, eval₂_eq_eval_map] at h
    simpa [Set.mem_setOf_eq, mem_roots, hne] using h
  exact Set.mem_biUnion hmem hroot

/-- For a family of pairwise distinct algebraic integers with a uniformly
bounded house, only **finitely many indices** carry degree at most `d`.

This is the honest strength of Northcott here, and it is what step 5 of the
paper argument needs (see the divergence note in the module doc): the family
is injective, so the indices with small degree inject into the finite set of
`finite_setOf_isIntegral_of_house_le`. -/
theorem finite_setOf_degree_le_of_house_le {B : ℝ} {μ : ℕ → ℂ}
    (hinj : Function.Injective μ) (hint : ∀ H, IsIntegral ℤ (μ H))
    (hhouse : ∀ H, ∀ z ∈ ((minpoly ℤ (μ H)).map (Int.castRingHom ℂ)).roots,
      ‖z‖ ≤ B) (d : ℕ) :
    {H : ℕ | (minpoly ℤ (μ H)).natDegree ≤ d}.Finite := by
  refine Set.Finite.subset (s := μ ⁻¹'
    {x : ℂ | IsIntegral ℤ x ∧ (minpoly ℤ x).natDegree ≤ d ∧
      ∀ z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots, ‖z‖ ≤ B})
    (Set.Finite.preimage hinj.injOn (finite_setOf_isIntegral_of_house_le d B))
    fun H hH ↦ ⟨hint H, hH, hhouse H⟩

/-- **The step-4 form.** Pairwise distinct algebraic integers with a uniformly
bounded house have unbounded degree: for every `d` some member of the family
has minimal-polynomial degree exceeding `d`.

Immediate from `finite_setOf_degree_le_of_house_le`: if every degree were at
most `d`, all of `ℕ` — an infinite set — would sit inside a finite one. -/
theorem unbounded_degree_of_house_le {B : ℝ} {μ : ℕ → ℂ}
    (hinj : Function.Injective μ) (hint : ∀ H, IsIntegral ℤ (μ H))
    (hhouse : ∀ H, ∀ z ∈ ((minpoly ℤ (μ H)).map (Int.castRingHom ℂ)).roots,
      ‖z‖ ≤ B) :
    ∀ d : ℕ, ∃ H, d < (minpoly ℤ (μ H)).natDegree := by
  intro d
  by_contra hcon
  simp only [not_exists, not_lt] at hcon
  exact Set.infinite_univ
    ((finite_setOf_degree_le_of_house_le hinj hint hhouse d).subset fun H _ ↦ hcon H)

end Polyplets

#print axioms Polyplets.mahlerMeasure_minpoly_le
#print axioms Polyplets.finite_setOf_isIntegral_of_house_le
#print axioms Polyplets.finite_setOf_degree_le_of_house_le
#print axioms Polyplets.unbounded_degree_of_house_le
