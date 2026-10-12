/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.LinearAlgebra.Lagrange
import Polyplets.Compute
import Polyplets.Universal.System

/-!
# Instance toolkit: a computable counter for `T L`, and the values lemma

The universal diagonal law needs two pieces of machinery that are
lattice-generic but live outside the shape engine:

* **the computable twin** `Tc L W n H` — `Compute.lean`'s bounded-closure
  enumerator with `kingAdj ↦ Adj L`, plus `Tc_eq_T`. The one genuine change is
  the enumeration box: the king file's box is `[0, n-1] × [0, H-1]`, but a
  general row-local lattice can skip columns, so the width bound of
  `Universal/Finite.lean` is `p.1 ≤ M · (n − 1)`. Rather than compute `M`, `Tc`
  takes the box width `W` as a parameter and `Tc_eq_T` asks for
  `M · (n − 1) ≤ W − 1`; `Tc_eq_T_of_reach_le_one` is the convenient corollary
  `W = n` for every lattice of reach `1` (square, hex, king — the named
  instances except the five-neighbor `D = Icc (-2) 2` and the degenerate
  `D = {-2, 0, 2}`, both of reach `2`).
* **the values lemma** `isDiagonalPoly_of_eval` — Lagrange uniqueness: a
  degree-`≤ k` polynomial matching the witness at `k + 1` of the `k + 1` onset
  points *is* the witness, so it satisfies the diagonal law for `L`.

Nothing here is instance-specific; `King.lean` and `Universal/{Square,Hex}.lean`
supply the lattices and the anchor cells.
-/

namespace Polyplets.Universal

open Polynomial

/-! ## Decidability of the geometric predicates -/

/-- Row-local adjacency is decidable: a conjunction of decidable integer
(in)equalities and a `Finset` membership. -/
instance instDecidableAdj (L : RowLocal) : DecidableRel (Adj L) := fun p q => by
  unfold Adj; infer_instance

/-- One round of neighbor expansion inside `S`: adjoin to `R` every cell of `S`
`L`-adjacent to some cell of `R`. -/
def stepExpand (L : RowLocal) (S R : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  R ∪ S.filter fun q => ∃ p ∈ R, Adj L p q

/-- The cells of `S` reachable from `p` by `L`-steps inside `S`, computed as
`S.card` rounds of neighbor expansion from the seed `{p}`. -/
def reachSet (L : RowLocal) (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) : Finset (ℤ × ℤ) :=
  (stepExpand L S)^[S.card] {p}

/-- Expansion only ever grows the reached set. -/
lemma subset_stepExpand (L : RowLocal) (S R : Finset (ℤ × ℤ)) : R ⊆ stepExpand L S R :=
  Finset.subset_union_left

/-- Starting from a seed inside `S`, every expansion round stays inside `S`. -/
lemma iterate_stepExpand_subset {L : RowLocal} {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    ∀ k, (stepExpand L S)^[k] {p} ⊆ S := by
  intro k
  induction k with
  | zero => simpa using hp
  | succ k ih =>
      rw [Function.iterate_succ_apply']
      intro q hq
      simp only [stepExpand, Finset.mem_union, Finset.mem_filter] at hq
      rcases hq with h | ⟨hqS, -⟩
      · exact ih h
      · exact hqS

/-- The seed survives every expansion round. -/
lemma mem_iterate_self (L : RowLocal) (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) :
    ∀ k, p ∈ (stepExpand L S)^[k] {p} := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
      rw [Function.iterate_succ_apply']
      exact subset_stepExpand _ _ _ ih

/-- **Soundness of the closure**: every cell reached from a seed `p ∈ S` is
joined to `p` by an `L`-path inside `S`. -/
lemma reachSet_sound {L : RowLocal} {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    ∀ k, ∀ q ∈ (stepExpand L S)^[k] {p},
      Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q := by
  intro k
  induction k with
  | zero =>
      intro q hq
      simp only [Function.iterate_zero_apply, Finset.mem_singleton] at hq
      subst hq
      exact Relation.ReflTransGen.refl
  | succ k ih =>
      rw [Function.iterate_succ_apply']
      intro q hq
      simp only [stepExpand, Finset.mem_union, Finset.mem_filter] at hq
      rcases hq with h | ⟨hqS, a, haR, hadj⟩
      · exact ih q h
      · exact (ih a haR).tail ⟨iterate_stepExpand_subset hp k haR, hqS, hadj⟩

/-- While the expansion chain has not stalled, its cardinality grows by at
least one per round. -/
lemma iterate_card_grow (L : RowLocal) (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) :
    ∀ k, (∀ j < k, (stepExpand L S)^[j + 1] {p} ≠ (stepExpand L S)^[j] {p}) →
      k + 1 ≤ ((stepExpand L S)^[k] {p}).card := by
  intro k
  induction k with
  | zero => intro _; simp
  | succ k ih =>
      intro h
      have h1 : k + 1 ≤ ((stepExpand L S)^[k] {p}).card :=
        ih fun j hj => h j (Nat.lt_succ_of_lt hj)
      have hne : (stepExpand L S)^[k] {p} ≠ (stepExpand L S)^[k + 1] {p} :=
        Ne.symm (h k (Nat.lt_succ_self k))
      have hsub : (stepExpand L S)^[k] {p} ⊆ (stepExpand L S)^[k + 1] {p} := by
        rw [Function.iterate_succ_apply']
        exact subset_stepExpand _ _ _
      have := Finset.card_lt_card (hsub.ssubset_of_ne hne)
      omega

/-- **The chain stalls**: `reachSet L S p` is a fixed point of `stepExpand L S`. -/
lemma stepExpand_reachSet {L : RowLocal} {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    stepExpand L S (reachSet L S p) = reachSet L S p := by
  by_cases h : ∃ j < S.card, (stepExpand L S)^[j + 1] {p} = (stepExpand L S)^[j] {p}
  · obtain ⟨j, hj, hfix⟩ := h
    have hx : stepExpand L S ((stepExpand L S)^[j] {p}) = (stepExpand L S)^[j] {p} := by
      rw [← Function.iterate_succ_apply' (stepExpand L S) j {p}]; exact hfix
    have hreach : reachSet L S p = (stepExpand L S)^[j] {p} := by
      rw [reachSet, ← Nat.sub_add_cancel hj.le, Function.iterate_add_apply]
      exact Function.iterate_fixed hx _
    rw [hreach, hx]
  · push Not at h
    have hgrow := iterate_card_grow L S p S.card h
    have hcard := Finset.card_le_card (iterate_stepExpand_subset (L := L) hp S.card)
    omega

/-- **Completeness of the closure**: every cell `L`-path-reachable from `p ∈ S`
lies in `reachSet L S p`. -/
lemma reachSet_complete {L : RowLocal} {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} (hp : p ∈ S)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q) :
    q ∈ reachSet L S p := by
  induction h with
  | refl => exact mem_iterate_self L S p _
  | @tail b c _ hbc ih =>
      rw [← stepExpand_reachSet hp]
      simp only [stepExpand, Finset.mem_union, Finset.mem_filter]
      exact Or.inr ⟨hbc.2.1, b, ih, hbc.2.2⟩

/-- `Connected L` in terms of the computable closure. -/
lemma connected_iff_reach (L : RowLocal) (S : Finset (ℤ × ℤ)) :
    Connected L S ↔ ∀ p ∈ S, ∀ q ∈ S, q ∈ reachSet L S p := by
  constructor
  · intro h p hp q hq
    exact reachSet_complete hp (h p hp q hq)
  · intro h p hp q hq
    exact reachSet_sound hp S.card q (h p hp q hq)

/-- `L`-connectivity is decidable, via the closure characterization. -/
instance instDecidableConnected (L : RowLocal) : DecidablePred (Connected L) := fun S =>
  decidable_of_iff _ (connected_iff_reach L S).symm

/-- Canonicality is decidable. -/
instance instDecidableIsAnimal (L : RowLocal) (n H : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsAnimal L n H S) :=
  decidable_of_iff _ isAnimal_iff_and.symm

/-! ## The computable counter -/

/-- **Computable counter for `T L`**: enumerate the `n`-element subsets of the
box `[0, W-1] × [0, H-1]` and count the animals. Pure brute force —
exponential in `W · H`, meant for anchor cells only. The box is
`Compute.lean`'s (`Polyplets.box`), reused with an explicit width. -/
def Tc (L : RowLocal) (W n H : ℕ) : ℕ :=
  (((Polyplets.box W H).powersetCard n).filter fun S => IsAnimal L n H S).card

/-- **The computable counter agrees with `T L`**, provided the box is wide
enough to contain every canonical animal: `M · (n − 1) ≤ W − 1`
(`Universal/Finite.lean`'s `animal_x_le`). -/
theorem Tc_eq_T (L : RowLocal) (W n H : ℕ) (hW : L.reach * ((n : ℤ) - 1) ≤ (W : ℤ) - 1) :
    Tc L W n H = T L n H := by
  have hset : ((Polyplets.box W H).powersetCard n).filter (fun S => IsAnimal L n H S)
      = (animals_finite L n H).toFinset := by
    ext S
    simp only [Finset.mem_filter, Finset.mem_powersetCard, Set.Finite.mem_toFinset,
      Set.mem_setOf_eq]
    constructor
    · exact fun h => h.2
    · intro h
      refine ⟨⟨fun p hp => ?_, h.card⟩, h⟩
      rw [Polyplets.mem_box]
      obtain ⟨B, hB1, hB2⟩ : ∃ B : ℤ, p.1 ≤ B ∧ B ≤ (W : ℤ) - 1 :=
        ⟨_, animal_x_le h hp, hW⟩
      have hx0 := h.anchored.x_nonneg p hp
      have hy0 := h.anchored.y_nonneg p hp
      have hy1 := h.y_le p hp
      omega
  rw [Tc, hset, T_eq_toFinset_card]

/-- **Reach one**: a lattice all of whose up-offsets are `0` or `±1` has
`M = 1`. -/
lemma reach_le_one (L : RowLocal) (h : ∀ d ∈ L.D, |d| ≤ 1) : L.reach ≤ 1 := by
  refine Finset.max'_le _ _ _ fun y hy => ?_
  rcases Finset.mem_insert.mp hy with rfl | hy
  · exact le_rfl
  · obtain ⟨d, hd, rfl⟩ := Finset.mem_image.mp hy
    exact h d hd

/-- The convenient specialization of `Tc_eq_T` for a reach-`1` lattice: the box
`[0, n-1] × [0, H-1]` suffices, exactly as in the king case. -/
theorem Tc_eq_T_of_reach_le_one {L : RowLocal} (hM : L.reach ≤ 1) (n H : ℕ) :
    Tc L n n H = T L n H := by
  refine Tc_eq_T L n n H ?_
  have h1 := L.one_le_reach
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · push_cast
    linarith
  · have hx : (0 : ℤ) ≤ (n : ℤ) - 1 := by
      have : (1 : ℤ) ≤ (n : ℤ) := by exact_mod_cast hn
      linarith
    calc L.reach * ((n : ℤ) - 1) ≤ 1 * ((n : ℤ) - 1) := by
          exact mul_le_mul_of_nonneg_right hM hx
      _ = (n : ℤ) - 1 := one_mul _

/-- The `n`-th row sum of the height triangle, computably: the number of fixed
`L`-animals with `n` cells, summed over all heights `H ≤ n`. (Heights above `n`
contribute nothing: a height-`H` animal needs at least `H` cells.) -/
def rowSum (L : RowLocal) (W n : ℕ) : ℕ := ∑ H ∈ Finset.range (n + 1), Tc L W n H

/-! ## The diagonal polynomial from its values -/

/-- **The diagonal polynomial from `k + 1` values.** A polynomial `p` of degree
`≤ k` matching the witness of `exists_isDiagonalPoly` at `k+1` distinct onset
points `s ⊆ [2k+1, 3k+1]` *is* that witness (Lagrange uniqueness,
`Polynomial.eq_of_degrees_lt_of_eval_finset_eq`), hence satisfies the law for
`L`. The hypothesis at each point is the count `T(n, n-k) · b^(3k+1-n)` that
`IsDiagonalPoly.eval_onset` forces on the witness. -/
theorem isDiagonalPoly_of_eval (L : RowLocal) (k : ℕ) (p : Polynomial ℚ) (hp : p.natDegree ≤ k)
    (s : Finset ℕ) (hcard : k + 1 ≤ s.card)
    (hin : ∀ n ∈ s, 2 * k + 1 ≤ n ∧ n ≤ 3 * k + 1)
    (hpts : ∀ n ∈ s, p.eval (n : ℚ) = ((T L n (n - k) * L.b ^ (3 * k + 1 - n) : ℕ) : ℚ)) :
    IsDiagonalPoly L k p := by
  obtain ⟨P, hPdeg, hP⟩ := exists_isDiagonalPoly L k
  have hpP : p = P := by
    have hinj : Set.InjOn (Nat.cast : ℕ → ℚ) s := fun a _ b _ h => by exact_mod_cast h
    have hcard' : (s.image (Nat.cast : ℕ → ℚ)).card = s.card :=
      Finset.card_image_of_injOn hinj
    apply Polynomial.eq_of_degrees_lt_of_eval_finset_eq (s.image (Nat.cast : ℕ → ℚ))
    · calc p.degree ≤ (p.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hp
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · calc P.degree ≤ (P.natDegree : WithBot ℕ) := Polynomial.degree_le_natDegree
        _ ≤ (k : WithBot ℕ) := by exact_mod_cast hPdeg
        _ < ((s.image (Nat.cast : ℕ → ℚ)).card : WithBot ℕ) := by
            rw [hcard']; exact_mod_cast (by omega : k < s.card)
    · intro x hx
      rw [Finset.mem_image] at hx
      obtain ⟨n, hn, rfl⟩ := hx
      obtain ⟨hn1, hn2⟩ := hin n hn
      rw [hpts n hn, hP.eval_onset hn1 hn2]
  rw [hpP]
  exact hP

end Polyplets.Universal
