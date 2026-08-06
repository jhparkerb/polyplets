/-
Proposition 6 (`results/hv-growth-sandwich.md`) as a Lean *architecture*: every
statement is real and typechecks; every `sorry` is a contract with a line
estimate. The final theorem is genuinely proved from the contracts above it.
-/
import Mathlib
import Polyplets.StairAnimals

open Filter Topology

namespace Polyplets.Prop6

/-! ## 1. The three families as counting functions (B3, ~250 lines) -/

/-- Stacks: the column intervals nest, because the two boundaries move
oppositely. This is a different class from `Stair.Valid`, not a reflection of it
— reflecting a staircase gives another staircase. Same `List Col` encoding.

Two reflections do save work, and neither relates stacks to staircases:
reversing the column order swaps the fattening block with the thinning block
(both stacks), and flipping top-to-bottom swaps the two staircase orientations.
Each is an area-preserving involution, so each halves a development. -/
def Stack.Valid : List Stair.Col → Prop := sorry

/-- `M n` — staircase king animals of area `n`, up to translation. Finiteness
(heights, offsets and length all `≤ n`) is the `canonicalAnimal_finite` pattern;
`Nat.card` returning junk `0` off that set is the `Set.ncard` convention. -/
noncomputable def M (n : ℕ) : ℕ :=
  Nat.card {l : List Stair.Col // Stair.Valid l ∧ Stair.area l = n}

/-- `P n` — stacks of area `n`. -/
noncomputable def P (n : ℕ) : ℕ :=
  Nat.card {l : List Stair.Col // Stack.Valid l ∧ Stair.area l = n}

/-- HV-convex king animals, origin-anchored, stated geometrically in the
`Defs.lean` idiom: king-connected, every row and every column an unbroken run.
This is the layer that does not exist yet, and Corollary 4 — that it forces
valley-unimodal bottoms and peak-unimodal tops — is proved against it. -/
def IsHVCanonical (n : ℕ) (S : Finset (ℤ × ℤ)) : Prop := sorry

/-- `A n` — HV-convex king animals of area `n`. -/
noncomputable def A (n : ℕ) : ℕ := {S : Finset (ℤ × ℤ) | IsHVCanonical n S}.ncard

/-! ## 2. The three lemmas -/

/-- **Lemma 3.** The column-join is injective at fixed areas. `StairAnimals.lean`
already has `join_valid`, `cut_join`, `join_injOn`; what is owed is the counting
layer that turns them into this. ~400 lines, no new mathematics. -/
theorem lemma3 (i j : ℕ) : M i * M j ≤ M (i + j) := sorry

/-- **Lemma 2.** Stacks are sub-exponential. The row-width transpose (a bijection
onto weakly unimodal compositions) plus the `√n` split. Mathlib has `Nat.Partition`
and its `Fintype` but nothing on unimodality and no cardinality bound, so both
halves are built from scratch. ~600–900 lines. -/
theorem lemma2 (n : ℕ) : P n ≤ (n + 1) ^ (4 * Nat.sqrt n + 6) := sorry

/-- **Lemma 1.** The three-block factorisation, as a counting inequality: phase
bits are monotone, so the columns split `C1 C2 C3`, and the animal is recovered
from the three blocks, two junction offsets and one phase bit. Needs Corollary 4
first, then a `Finset` injection. The cost centre, ~1500 lines. -/
theorem lemma1 (n : ℕ) :
    A n ≤ 2 * (n + 1) ^ 2 *
      ∑ i ∈ Finset.range (n + 1), ∑ j ∈ Finset.range (n + 1), P i * M j * P (n - i - j) :=
  sorry

/-! ## 3. Fekete, *generalized out of* `Growth.lean`, not copied from it -/

/-- Everything `Growth.lean:648-730` actually uses about `a`: supermultiplicative,
positive, and under some exponential ceiling. Extracting this moves ~83 lines out
of `Growth.lean` and makes `mu` an instantiation instead of a second copy.
`lambda` becomes `polypletFekete.growth`, with `lambda_tendsto` and
`a_le_lambda_pow` surviving as wrappers so `AuditOutworks.lean`'s pinned axiom
footprints still hold. -/
structure Fekete where
  f : ℕ → ℕ
  c : ℝ
  one_le_c : 1 ≤ c
  supermul : ∀ m n, f m * f n ≤ f (m + n)
  one_le : ∀ {k : ℕ}, 1 ≤ k → 1 ≤ f k
  ceiling : ∀ k : ℕ, (f k : ℝ) ≤ c ^ k

namespace Fekete

variable (F : Fekete)

noncomputable def negLog (k : ℕ) : ℝ := -Real.log (F.f k)

theorem subadditive : Subadditive F.negLog := sorry

theorem bddBelow : BddBelow (Set.range fun k : ℕ => F.negLog k / k) := sorry

/-- The growth constant. `Growth.lean`'s `lambda` and our `mu` are two values of it. -/
noncomputable def growth : ℝ := Real.exp (-F.subadditive.lim)

theorem tendsto : Tendsto (fun n : ℕ => (F.f n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 F.growth) := sorry

/-- Limit-is-supremum: every banked term is a rigorous floor. -/
theorem le_growth_pow {n : ℕ} (hn : 1 ≤ n) : (F.f n : ℝ) ≤ F.growth ^ n := sorry

end Fekete

theorem M_pos {n : ℕ} (hn : 1 ≤ n) : 1 ≤ M n := sorry

/-- The ceiling: heights form a composition of `n` (`2 ^ (n-1)` choices) and each
offset is bounded by the previous height (`≤ 2 ^ n`). -/
theorem M_le_pow (n : ℕ) : M n ≤ 4 ^ n := sorry

/-- The staircase instance. Lemma 3 is the only interesting field. -/
noncomputable def stairFekete : Fekete where
  f := M
  c := 4
  one_le_c := by norm_num
  supermul := lemma3
  one_le := M_pos
  ceiling := fun k => by exact_mod_cast M_le_pow k

/-- `µ = 3.128943269730886…` -/
noncomputable def mu : ℝ := stairFekete.growth

theorem M_tendsto : Tendsto (fun n : ℕ => (M n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 mu) :=
  stairFekete.tendsto

/-! ## 4. The squeeze -/

/-- Lemma 1 bounds `A` by a convolution; Lemma 2 kills the two outer factors
because `(n+1) ^ (4√n+6)` has `n`-th root `→ 1`; Lemma 3 supplies `µ` for the
middle. ε-management in `ℝ`, ~250 lines. -/
theorem A_tendsto : Tendsto (fun n : ℕ => (A n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 mu) := sorry

/-- **Proposition 6.** Any family trapped between the staircase animals and the
HV-convex ones has growth constant `µ`. -/
theorem prop6 (C : ℕ → ℕ) (hlo : ∀ n, M n ≤ C n) (hhi : ∀ n, C n ≤ A n) :
    Tendsto (fun n : ℕ => (C n : ℝ) ^ ((n : ℝ)⁻¹)) atTop (𝓝 mu) := by
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le M_tendsto A_tendsto (fun n => ?_) (fun n => ?_)
  · exact Real.rpow_le_rpow (Nat.cast_nonneg _) (by exact_mod_cast hlo n) (by positivity)
  · exact Real.rpow_le_rpow (Nat.cast_nonneg _) (by exact_mod_cast hhi n) (by positivity)

end Polyplets.Prop6

#print axioms Polyplets.Prop6.prop6
