# OW-8 "House Arrest" — `Polyplets/Northcott.lean`: bounded degree + house ⇒ finite

Read first: `polyplets/OUTWORKS-PLAN.md`;
`results/anisotropic-not-dfinite.md` §"THE UNCONDITIONAL THEOREM" (the
five-step proof whose step 4 this discharges). Size S — **smaller than the
claims-audit estimated**, because the pinned Mathlib already contains the
heavy half (checked):

- `Polynomial.finite_mahlerMeasure_le (n : ℕ) (B : ℝ≥0)` — **Northcott for
  the Mahler measure**: integer polynomials of degree ≤ n and Mahler
  measure ≤ B form a finite set
  (`Mathlib/NumberTheory/MahlerMeasure.lean:110`; same file:
  `boxPoly`/`ncard_boxPoly`, and Kronecker —
  `pow_eq_one_of_mahlerMeasure_eq_one:183` — already done, cite, don't
  re-prove).
- `Mathlib/Analysis/Polynomial/MahlerMeasure.lean`: `mahlerMeasure`,
  `mahlerMeasure_mul` (:126), `prod_mahlerMeasure_eq_mahlerMeasure_prod`
  (:148), `mahlerMeasure_X_sub_C : (X − C z).mahlerMeasure = max 1 ‖z‖`
  (:187).

So the deliverable reduces to: express "house ≤ B" as a Mahler-measure
bound on the minimal polynomial, and push finiteness through.

## Deliverables

```lean
/-- The conjugates of an algebraic integer `x : ℂ` are the complex roots of
its minimal polynomial. House bound ⇒ Mahler measure bound. -/
theorem mahlerMeasure_minpoly_le {x : ℂ} (hx : IsIntegral ℤ x) {B : ℝ}
    (hB : ∀ z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots, ‖z‖ ≤ B) :
    ((minpoly ℤ x).map (Int.castRingHom ℂ)).mahlerMeasure
      ≤ max 1 B ^ (minpoly ℤ x).natDegree

/-- Northcott at bounded degree and house: finitely many algebraic integers
with degree ≤ d and all conjugates in the closed disc of radius B. -/
theorem finite_setOf_isIntegral_of_house_le (d : ℕ) (B : ℝ) :
    {x : ℂ | IsIntegral ℤ x ∧ (minpoly ℤ x).natDegree ≤ d ∧
      ∀ z ∈ ((minpoly ℤ x).map (Int.castRingHom ℂ)).roots, ‖z‖ ≤ B}.Finite

/-- The step-4 form: distinct algebraic integers with uniformly bounded
house have unbounded degree. -/
theorem unbounded_degree_of_house_le {B : ℝ} {μ : ℕ → ℂ}
    (hinj : Function.Injective μ) (hint : ∀ H, IsIntegral ℤ (μ H))
    (hhouse : ∀ H, ∀ z ∈ ((minpoly ℤ (μ H)).map (Int.castRingHom ℂ)).roots,
      ‖z‖ ≤ B) :
    ∀ d : ℕ, ∃ H, d < (minpoly ℤ (μ H)).natDegree
```

## Proof routes

1. `mahlerMeasure_minpoly_le`: `minpoly ℤ x` is monic
   (`minpoly.monic hx`); over ℂ it splits
   (`IsAlgClosed.splits_codomain`), so
   `p.map = C (lead) * ∏_{z ∈ roots} (X − C z)` —
   `Polynomial.eq_prod_roots_of_splits` / `prod_multiset_X_sub_C_of_monic`
   (grep the exact modern name; `Polynomial.prod_multiset_X_sub_C` family).
   Then `mahlerMeasure_mul` + `prod_mahlerMeasure_eq_mahlerMeasure_prod` +
   `mahlerMeasure_X_sub_C` give
   `M(p) = ∏ max 1 ‖z‖ ≤ (max 1 B)^{#roots}` and
   `#roots = natDegree` (splits + `Polynomial.roots_count`-style:
   `(Polynomial.natDegree_eq_card_roots)` for split polynomials).
   Monotonicity `max 1 ‖z‖ ≤ max 1 B`: from `hB` per root.
2. `finite_setOf_isIntegral_of_house_le`: the map
   `x ↦ minpoly ℤ x` sends the set into
   `{p : ℤ[X] | p.natDegree ≤ d ∧ p.mahlerMeasureℂ ≤ (max 1 B)^d}` —
   NOTE `finite_mahlerMeasure_le`'s exact phrasing (which measure of which
   cast, `ℝ≥0` bound): read its statement in the source and adapt; lift
   `max 1 B ^ d` into `ℝ≥0` via `Real.toNNReal` (monotone bookkeeping).
   Fibers are finite: x is a root of its minimal polynomial
   (`minpoly.aeval`), a nonzero polynomial has finitely many roots in ℂ
   (`Polynomial.setOf_isRoot_finite` / `Set.Finite` of roots — via
   `Polynomial.roots` membership `Polynomial.mem_roots`). Assemble with
   `Set.Finite.biUnion` (finite image, finite fibers) or
   `Set.Finite.of_finite_image` + `Set.InjOn`-free fiber argument —
   cleanest: the set ⊆ ⋃_{p ∈ finite set} {roots of p}, a finite union of
   finite sets.
3. `unbounded_degree_of_house_le`: contrapositive — degrees ≤ d for all H
   puts the injective sequence inside the finite set of (2):
   `Set.Finite.subset` + infinite range of an injective ℕ-sequence
   (`Set.infinite_range_of_injective`). Note the house bound at level d
   uses the same B — no uniformity subtleties.

## Notes

- Degenerate B < 0: `hB` is then vacuous only if there are no roots
  (degree-0 minpoly impossible for integral x over ℤ — degree ≥ 1);
  the statements remain true as written (max 1 B handles it); don't add
  hypotheses.
- Keep the statement vocabulary exactly as above (`minpoly ℤ`, roots of
  the ℂ-cast) — it is the form step 4 of the paper proof consumes, and
  `Polyplets`-namespaced even though nothing here mentions animals: the
  file is the project's reusable number-theory shim. Module doc should
  say what it discharges and what remains blocked, per below.
- No native_decide; standard axioms only.

## Module-doc note (for the eventual paper cross-reference — include it)

Discharges: step 4 (Northcott/Kronecker finiteness) of the unconditional
non-D-finiteness theorem (`results/anisotropic-not-dfinite.md`), i.e. "the
strip growth constants μ_H, pairwise distinct algebraic integers with
house < λ ≤ 9.3154, have unbounded degree" — modulo steps 1–3, 5 which
remain unformalized and out of scope: Fatou's lemma for integer rational
series, Pringsheim positivity, the Perron–Frobenius strict-monotonicity
step (Mathlib has no Perron root theory), and any Lean notion of
D-finiteness. Mathlib's own Northcott (`finite_mahlerMeasure_le`) landed
2025 (Barroero) — the claims-audit note that "Mathlib only has
fixed-field `finite_of_norm_le`" is superseded; record that correction.

## Done criteria

`lake build` green, no `sorry`; `#print axioms` of all three deliverables
= standard three, guarded. Commit
`lean-ow: Northcott — bounded degree + house is finite`.
