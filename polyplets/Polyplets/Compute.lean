/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Sequence

/-!
# Deciding king connectivity, and the enumeration box

`Defs.lean` states king-connectivity via `Relation.ReflTransGen`. This file
decides it by a bounded closure computation: `S.card` rounds of neighbor
expansion inside `S` from a seed cell (`reachSet`). Soundness
(`reachSet_sound`) reads a king path off the expansion rounds; completeness
(`reachSet_complete`) is the finite fixpoint argument — the expansion chain is
monotone and confined to `S`, so it stalls within `S.card` rounds
(`stepExpand_reachSet`), and a stalled set absorbs king steps, hence contains
everything path-reachable. With it `IsPolyplet n S` and `S ∈ heightClass n H` are
decidable.

`box n H` is the finite box `[0, n-1] × [0, H-1]` that contains every polyplet
of height `H` (`mem_powersetCard_box`); `Weights.lean` enumerates its subsets
and `Enum.lean`'s bit-board flood is this closure on boards.
-/

namespace Polyplets

/-- King adjacency is decidable: it is a conjunction of decidable integer
(in)equalities. -/
instance : DecidableRel kingAdj := fun p q => by
  unfold kingAdj; infer_instance

/-! ## A computable connectivity check -/

/-- One round of neighbor expansion inside `S`: adjoin to `R` every cell of `S`
king-adjacent to some cell of `R`. -/
def stepExpand (S R : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  R ∪ S.filter fun q => ∃ p ∈ R, kingAdj p q

/-- The cells of `S` reachable from `p` by king steps inside `S`, computed as
`S.card` rounds of neighbor expansion from the seed `{p}`. `S.card` rounds
suffice because the expansion chain must stall within them
(`stepExpand_reachSet`). -/
def reachSet (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) : Finset (ℤ × ℤ) :=
  (stepExpand S)^[S.card] {p}

/-- Expansion only ever grows the reached set. -/
lemma subset_stepExpand (S R : Finset (ℤ × ℤ)) : R ⊆ stepExpand S R :=
  Finset.subset_union_left

/-- Starting from a seed inside `S`, every expansion round stays inside `S`. -/
lemma iterate_stepExpand_subset {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    ∀ k, (stepExpand S)^[k] {p} ⊆ S := by
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
lemma mem_iterate_self (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) :
    ∀ k, p ∈ (stepExpand S)^[k] {p} := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
      rw [Function.iterate_succ_apply']
      exact subset_stepExpand _ _ ih

/-- **Soundness of the closure**: every cell reached from a seed `p ∈ S` is
joined to `p` by a king path inside `S` — each expansion round extends the
paths by one king step. -/
lemma reachSet_sound {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    ∀ k, ∀ q ∈ (stepExpand S)^[k] {p},
      Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q := by
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
lemma iterate_card_grow (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) :
    ∀ k, (∀ j < k, (stepExpand S)^[j + 1] {p} ≠ (stepExpand S)^[j] {p}) →
      k + 1 ≤ ((stepExpand S)^[k] {p}).card := by
  intro k
  induction k with
  | zero => intro _; simp
  | succ k ih =>
      intro h
      have h1 : k + 1 ≤ ((stepExpand S)^[k] {p}).card :=
        ih fun j hj => h j (Nat.lt_succ_of_lt hj)
      have hne : (stepExpand S)^[k] {p} ≠ (stepExpand S)^[k + 1] {p} :=
        Ne.symm (h k (Nat.lt_succ_self k))
      have hsub : (stepExpand S)^[k] {p} ⊆ (stepExpand S)^[k + 1] {p} := by
        rw [Function.iterate_succ_apply']
        exact subset_stepExpand _ _
      have := Finset.card_lt_card (hsub.ssubset_of_ne hne)
      omega

/-- **The chain stalls**: `reachSet S p` is a fixed point of `stepExpand S`.
Either some round `j < S.card` already stalled (and the chain is constant from
there on), or the cardinality grew every round, exceeding `|S|` inside `S` —
impossible. -/
lemma stepExpand_reachSet {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} (hp : p ∈ S) :
    stepExpand S (reachSet S p) = reachSet S p := by
  by_cases h : ∃ j < S.card, (stepExpand S)^[j + 1] {p} = (stepExpand S)^[j] {p}
  · obtain ⟨j, hj, hfix⟩ := h
    have hx : stepExpand S ((stepExpand S)^[j] {p}) = (stepExpand S)^[j] {p} := by
      rw [← Function.iterate_succ_apply' (stepExpand S) j {p}]; exact hfix
    have hreach : reachSet S p = (stepExpand S)^[j] {p} := by
      rw [reachSet, ← Nat.sub_add_cancel hj.le, Function.iterate_add_apply]
      exact Function.iterate_fixed hx _
    rw [hreach, hx]
  · push Not at h
    have hgrow := iterate_card_grow S p S.card h
    have hcard := Finset.card_le_card (iterate_stepExpand_subset hp S.card)
    omega

/-- **Completeness of the closure**: every cell king-path-reachable from
`p ∈ S` lies in `reachSet S p` — the stalled closure absorbs king steps. -/
lemma reachSet_complete {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} (hp : p ∈ S)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q) :
    q ∈ reachSet S p := by
  induction h with
  | refl => exact mem_iterate_self S p _
  | @tail b c _ hbc ih =>
      rw [← stepExpand_reachSet hp]
      simp only [stepExpand, Finset.mem_union, Finset.mem_filter]
      exact Or.inr ⟨hbc.2.1, b, ih, hbc.2.2⟩

/-- `KingConnected` in terms of the computable closure: every cell of `S`
reaches every cell of `S`. -/
lemma kingConnected_iff_reach (S : Finset (ℤ × ℤ)) :
    KingConnected S ↔ ∀ p ∈ S, ∀ q ∈ S, q ∈ reachSet S p := by
  constructor
  · intro h p hp q hq
    exact reachSet_complete hp (h p hp q hq)
  · intro h p hp q hq
    exact reachSet_sound hp S.card q (h p hp q hq)

/-- King-connectivity is decidable, via the closure characterization. -/
instance : DecidablePred KingConnected := fun S =>
  decidable_of_iff _ (kingConnected_iff_reach S).symm

/-- `IsPolyplet` is decidable: a conjunction of decidable cardinality,
connectivity (`DecidablePred KingConnected`), and bounded quantifiers over a
`Finset`. -/
instance decidableIsPolyplet (n : ℕ) (S : Finset (ℤ × ℤ)) : Decidable (IsPolyplet n S) :=
  decidable_of_iff _ isPolyplet_iff_and.symm

instance decidableMemHeightClass (n H : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (S ∈ heightClass n H) :=
  inferInstanceAs (Decidable (IsPolyplet n S ∧ height S = H))

/-! ## The enumeration box -/

/-- The finite box `[0, n-1] × [0, H-1]` containing every polyplet of `n` cells
and height `H`. Built by casting `Finset.range` products
into `ℤ × ℤ`: `Finset.Icc` on `ℤ` compiles against the noncomputable
`Int.instConditionallyCompleteLinearOrder` in current mathlib, so it cannot be
used in a computable definition. -/
def box (n H : ℕ) : Finset (ℤ × ℤ) :=
  (Finset.range n ×ˢ Finset.range H).image fun p => ((p.1 : ℤ), (p.2 : ℤ))

/-- Membership in `box` is the four coordinate bounds. -/
lemma mem_box {n H : ℕ} {p : ℤ × ℤ} :
    p ∈ box n H ↔ 0 ≤ p.1 ∧ p.1 < n ∧ 0 ≤ p.2 ∧ p.2 < H := by
  simp only [box, Finset.mem_image, Finset.mem_product, Finset.mem_range, Prod.exists]
  constructor
  · rintro ⟨a, b, ⟨ha, hb⟩, rfl⟩
    refine ⟨by simp, by simpa using ha, by simp, by simpa using hb⟩
  · rintro ⟨h1, h2, h3, h4⟩
    refine ⟨p.1.toNat, p.2.toNat, ⟨by omega, by omega⟩, ?_⟩
    rw [Prod.ext_iff]
    constructor <;> simp <;> omega

/-- Every polyplet of height `H` is an `n`-element subset of the box — the
height bound is `mem_heightClass_iff_rows`, the width bound `IsPolyplet.x_le`. -/
lemma mem_powersetCard_box {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (h : S ∈ heightClass n H) : S ∈ (box n H).powersetCard n := by
  obtain ⟨hP, hy, -⟩ := mem_heightClass_iff_rows.mp h
  rw [Finset.mem_powersetCard]
  refine ⟨fun p hp => ?_, hP.card⟩
  rw [mem_box]
  have hx1 := hP.x_le hp
  have hx0 := hP.anchored.x_nonneg p hp
  have hy0 := hP.anchored.y_nonneg p hp
  have hy1 := hy p hp
  omega

end Polyplets
