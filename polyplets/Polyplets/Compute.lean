/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.Push
import Polyplets.Finite

/-!
# A computable counter for `T`

`T n H` is defined noncomputably as an `ncard`. This file provides a computable
counterpart `Tc n H` — enumerate the `n`-element subsets of the box
`[0, n-1] × [0, H-1]` (the box `canonical_finite` proves contains every
canonical set) and count those passing a decidable canonicality check — and
proves `Tc_eq_T : Tc n H = T n H`.

The one nontrivial decidability ingredient is king-connectivity, which
`Defs.lean` states via `Relation.ReflTransGen`. We decide it by a bounded
closure computation: `S.card` rounds of neighbor expansion inside `S` from a
seed cell (`reachSet`). Soundness (`reachSet_sound`) reads a king path off the
expansion rounds; completeness (`reachSet_complete`) is the finite fixpoint
argument — the expansion chain is monotone and confined to `S`, so it stalls
within `S.card` rounds (`stepExpand_reachSet`), and a stalled set absorbs king
steps, hence contains everything path-reachable.

Kernel `decide` on `Tc` (and, through `Tc_eq_T`, on `T` itself) reaches the
smallest banked values of `results/triangle.txt`; its memory grows fast with
the cell (6 GB at `T 3 3`, past 8 GB at `T 5 4`), so the cells stop at
`T 4 3`. The three the proofs need are here, the rest in `Checks.lean`.
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

/-- Canonicality is decidable: a conjunction of decidable cardinality,
connectivity (`DecidablePred KingConnected`), and bounded quantifiers over a
`Finset`. -/
instance decidableIsCanonical (n H : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsCanonical n H S) := by
  unfold IsCanonical; infer_instance

/-! ## The computable counter -/

/-- The finite box `[0, n-1] × [0, H-1]` containing every canonical `n`-cell,
height-`H` set (`canonical_finite`). Built by casting `Finset.range` products
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

/-- **Computable counter for `T`**: enumerate the `n`-element subsets of the
box and count the canonical ones. Pure brute force — exponential in the box
size, meant for validation at small `n, H` only. -/
def Tc (n H : ℕ) : ℕ :=
  (((box n H).powersetCard n).filter fun S => IsCanonical n H S).card

/-- **The computable counter agrees with `T`.** The filtered enumeration is
exactly the materialized canonical set of `Finite.lean`: membership in the
box's `powersetCard` is implied by canonicality (height bounds from
`IsCanonical`, width bound from `canonical_x_le`). Degenerate cases need no
special handling: for `n = 0` or `H = 0` the `∃`-clauses of `IsCanonical` are
unsatisfiable, so both sides are `0`. -/
theorem Tc_eq_T (n H : ℕ) : Tc n H = T n H := by
  have hset : ((box n H).powersetCard n).filter (fun S => IsCanonical n H S)
      = (canonical_finite n H).toFinset := by
    ext S
    simp only [Finset.mem_filter, Finset.mem_powersetCard, Set.Finite.mem_toFinset,
      Set.mem_setOf_eq]
    constructor
    · exact fun h => h.2
    · intro h
      refine ⟨⟨fun p hp => ?_, h.1⟩, h⟩
      rw [mem_box]
      have hx1 := canonical_x_le h hp
      have hx0 := h.2.2.1 p hp
      have hy0 := h.2.2.2.2.1 p hp
      have hy1 := h.2.2.2.2.2.2.1 p hp
      omega
  rw [Tc, hset, T_eq_toFinset_card]

/-! ## The cells the development consumes

Three banked values (`results/triangle.txt`, provenance
`results/ns_a36/PROVENANCE.md`, two-algorithm confirmed range), transported to
the noncomputable `T` via `Tc_eq_T` and decided by the kernel: `T 1 1` seeds
the shape theorem's `k = 0` pin, `T 3 2` and `T 4 3` pin `P_1`. Further cells
are checked in `Checks.lean`. -/

/-- `T 1 1 = 1`: the single cell. -/
theorem T_1_1 : T 1 1 = 1 := by rw [← Tc_eq_T]; decide +kernel

/-- `T 3 2 = 10` (banked, `results/triangle.txt`), the first `P_1` onset
point. -/
theorem T_3_2 : T 3 2 = 10 := by rw [← Tc_eq_T]; decide +kernel

/-- `T 4 3 = 55` (banked, `results/triangle.txt`), the second `P_1` onset
point. -/
theorem T_4_3 : T 4 3 = 55 := by rw [← Tc_eq_T]; decide +kernel

/-!
Memory of kernel `decide` on this brute-force `Tc`, measured 2026-10-12
(`scripts/lean-decide-trials.sh`): the cells above peak at 2.7–3.3 GB;
`T 3 3` needs 6 GB; `T 5 4` (`C(20,5) = 15504` subsets) passes 8 GB and was
killed. Cells beyond `P_1`'s onset points enter the development only as
hypotheses (`Grand/PinAll.lean`, `BankedAnchors`).
-/

end Polyplets
