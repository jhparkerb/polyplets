/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Analysis.SpecificLimits.Normed
import Polyplets.Enum
import Polyplets.Growth

/-!
# Symmetric animals are negligible: one-sided → a(n)/4, free → a(n)/8

`Symmetry.lean` has the Burnside identities
`4 · OneSided n = a n + 2 R90 n + R180 n` and
`8 · Free n = a n + 2 R90 n + R180 n + 2 Hm n + 2 Dm n`. This file proves
that each symmetric count is `o(a n)`, so `4 · OneSided n / a n → 1` and
`8 · Free n / a n → 1` (`symmetryRatio`, the report's `SymmetryRatioClaim`).
Nothing is assumed: the comparison is supermultiplicativity (`a_supermul`)
against the kernel-decided `a 3 = 20`.

## The two encodings

A symmetric polyplet `S` of `n` cells is fixed by an affine
involution `σ` of the plane (`S.image σ = S`), and is recovered from a
*half* `W ⊆ S` with `W ∪ W.image σ = S`; the count of symmetric animals is
at most the count of halves, and a half is a polyplet of about
`n / 2` cells.

* For the mirrors (`Hm`, `Dm`) the half is geometric: `upperHalf h S` is the
  closed half-plane `h ≥ 0` for a signed distance `h` to the axis
  (`h ∘ σ = -h`). It is king-connected (`upperHalf_connected`: a path of `S`
  folds into the upper half, because a king step across the axis lands next
  to the reflection of its endpoint) and it meets its reflection exactly on
  the axis. Its size is `(n + f) / 2` with `f` axis cells, so a mirror
  animal with many axis cells has a large half; those are counted crudely
  (`card_le_crude`: axis cells are a subset of one line, the `u` cells off
  the axis a subset of the `n × n` box), which is `2ⁿ · poly(n)` for fixed
  `u`, and `2 < 20^(1/3) ≤ a(n)^(1/n)`.
* For the half turn (`R180`) no half-plane works (the two half-planes of a
  `Z`-shaped animal are joined only through each other), so the half is
  combinatorial: a maximal connected `W` meeting each `σ`-orbit at most once
  covers every orbit (`exists_half`). It has `(n + 1) / 2` cells, since the
  only fixed point is the centre, and the position of the centre is one of
  `(4n + 1)²` offsets.
* `R90 ≤ R180`: a quarterTurn-turn-symmetric animal is half-turn-symmetric.

## The analysis

`20 ^ (n / 3) ≤ a n` (`pow_le_a`), hence `2 ^ n ≤ 4 · a n` and
`a (n - u) / a n ≤ 4 / 2 ^ u`. `Hm n / a n` is then at most a tail
`16 / 2 ^ K` plus `K` terms of order `poly(n) · (2/5) ^ (n / 3)`, which is
`tendsto_zero_of_eventually_le`'s shape; `R180 n / a n ≤ (4n + 1)² / a (n / 2)`
is a squeeze.
-/

namespace Polyplets

open Finset Filter Topology

/-! ## Tools -/

lemma mem_image_of_involutive {σ : ℤ × ℤ → ℤ × ℤ} (hσσ : ∀ p, σ (σ p) = p)
    {S : Finset (ℤ × ℤ)} {p : ℤ × ℤ} : p ∈ S.image σ ↔ σ p ∈ S := by
  constructor
  · intro hp
    obtain ⟨q, hq, rfl⟩ := Finset.mem_image.1 hp
    rwa [hσσ]
  · intro hp
    exact Finset.mem_image.2 ⟨σ p, hp, hσσ p⟩

lemma mem_of_image_eq {σ : ℤ × ℤ → ℤ × ℤ} {S : Finset (ℤ × ℤ)}
    (hSσ : S.image σ = S)
    {p : ℤ × ℤ} (hp : p ∈ S) : σ p ∈ S := by
  rw [← hSσ]; exact Finset.mem_image_of_mem σ hp

/-- **Reconstruction.** If `S` is anchored and `S = V ∪ σ '' V`, then `S` is
the anchoring of `V' ∪ σ' '' V'`, where `V' = anchor V` and `σ'` is `σ`
conjugated by the translation that anchored `V`. -/
lemma eq_reanchor_of_union {S V : Finset (ℤ × ℤ)} (σ : ℤ × ℤ → ℤ × ℤ)
    (hS : Anchored S) (hV : V ∪ V.image σ = S) :
    S = anchor (anchor V ∪
      (anchor V).image (fun p => σ (p + corner V) - corner V)) := by
  set v := corner V
  have hV' : V = (anchor V).image (fun p => p + v) := by
    have hid : (fun p : ℤ × ℤ => p + v) ∘ (fun p => p - v) = id := funext fun p => by simp
    rw [anchor, Finset.image_image, hid, Finset.image_id]
  have hcomp : σ ∘ (fun p : ℤ × ℤ => p + v) =
      (fun p => p + v) ∘ (fun p => σ (p + v) - v) := funext fun p => by simp
  have hX : S = (anchor V ∪ (anchor V).image (fun p => σ (p + v) - v)).image
      (fun p => p + v) := by
    rw [Finset.image_union, Finset.image_image, ← hcomp, ← Finset.image_image, ← hV', hV]
  conv_lhs => rw [← anchor_eq_self hS, hX]
  exact anchor_image_add _ _

/-! ## The geometric half, for the mirrors -/

/-- The closed upper half of `S` with respect to the signed distance `h`. -/
def upperHalf (h : ℤ × ℤ → ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  S.filter fun p => 0 ≤ h p

/-- The cells of `S` on the axis `h = 0`. -/
def axisCells (h : ℤ × ℤ → ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  S.filter fun p => h p = 0

section Half

variable {σ : ℤ × ℤ → ℤ × ℤ} {h : ℤ × ℤ → ℤ} {S : Finset (ℤ × ℤ)}

lemma mem_upperHalf {p : ℤ × ℤ} : p ∈ upperHalf h S ↔ p ∈ S ∧ 0 ≤ h p :=
  Finset.mem_filter

lemma upperHalf_subset : upperHalf h S ⊆ S := Finset.filter_subset _ _

lemma upperHalf_union (hσσ : ∀ p, σ (σ p) = p) (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) : upperHalf h S ∪ (upperHalf h S).image σ = S := by
  ext p
  simp only [Finset.mem_union, mem_upperHalf, mem_image_of_involutive hσσ, hh]
  constructor
  · rintro (⟨hp, -⟩ | ⟨hp, -⟩)
    · exact hp
    · have := mem_of_image_eq hSσ hp
      rwa [hσσ] at this
  · intro hp
    by_cases h0 : 0 ≤ h p
    · exact Or.inl ⟨hp, h0⟩
    · exact Or.inr ⟨mem_of_image_eq hSσ hp, by omega⟩

lemma upperHalf_inter (hσσ : ∀ p, σ (σ p) = p) (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) : upperHalf h S ∩ (upperHalf h S).image σ = axisCells h S := by
  ext p
  simp only [Finset.mem_inter, mem_upperHalf, axisCells, Finset.mem_filter,
    mem_image_of_involutive hσσ, hh]
  constructor
  · rintro ⟨⟨hp, h1⟩, -, h2⟩
    exact ⟨hp, by omega⟩
  · rintro ⟨hp, h0⟩
    exact ⟨⟨hp, by omega⟩, mem_of_image_eq hSσ hp, by omega⟩

/-- Counting a set covered by `W` and its image under an involution. -/
lemma card_add_card_inter_image {σ : ℤ × ℤ → ℤ × ℤ} (hσσ : ∀ p, σ (σ p) = p)
    {S W : Finset (ℤ × ℤ)} (hWS : W ∪ W.image σ = S) :
    S.card + (W ∩ W.image σ).card = 2 * W.card := by
  have hinj : Function.Injective σ := Function.LeftInverse.injective hσσ
  have := Finset.card_union_add_card_inter W (W.image σ)
  rw [hWS, Finset.card_image_of_injective _ hinj] at this
  omega

lemma two_mul_card_upperHalf (hσσ : ∀ p, σ (σ p) = p) (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) :
    2 * (upperHalf h S).card = S.card + (axisCells h S).card := by
  have := card_add_card_inter_image hσσ (upperHalf_union hσσ hh hSσ)
  rw [upperHalf_inter hσσ hh hSσ] at this
  omega

/-- **The upper half is connected.** A path of `S` folds into the upper half:
steps inside either half stay adjacent, and a step across the axis lands on
(or next to) the reflection of its endpoint (`hcross`). -/
lemma upperHalf_connected (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) (hadj : ∀ p q, kingAdj p q → kingAdj (σ p) (σ q))
    (hcross : ∀ p q, kingAdj p q → 0 ≤ h p → h q < 0 → σ q = p ∨ kingAdj p (σ q))
    (hS : KingConnected S) : KingConnected (upperHalf h S) := by
  set V := upperHalf h S with hVdef
  let fold : ℤ × ℤ → ℤ × ℤ := fun r => if 0 ≤ h r then r else σ r
  have hfold : ∀ r ∈ S, fold r ∈ V := by
    intro r hr
    simp only [fold]
    split_ifs with h0
    · exact mem_upperHalf.2 ⟨hr, h0⟩
    · exact mem_upperHalf.2 ⟨mem_of_image_eq hSσ hr, by rw [hh]; omega⟩
  have hfoldV : ∀ r ∈ V, fold r = r := fun r hr => by
    simp [fold, (mem_upperHalf.1 hr).2]
  have hstep : ∀ r r', r ∈ S → r' ∈ S → kingAdj r r' →
      fold r = fold r' ∨ (fold r ∈ V ∧ fold r' ∈ V ∧ kingAdj (fold r) (fold r')) := by
    intro r r' hr hr' hrr'
    have h1 := hfold r hr
    have h2 := hfold r' hr'
    simp only [fold] at h1 h2 ⊢
    by_cases a : 0 ≤ h r <;> by_cases b : 0 ≤ h r' <;>
      simp only [a, b, ↓reduceIte] at h1 h2 ⊢
    · exact Or.inr ⟨h1, h2, hrr'⟩
    · rcases hcross r r' hrr' a (by omega) with e | e
      · exact Or.inl e.symm
      · exact Or.inr ⟨h1, h2, e⟩
    · rcases hcross r' r (kingAdj_symm hrr') b (by omega) with e | e
      · exact Or.inl e
      · exact Or.inr ⟨h1, h2, kingAdj_symm e⟩
    · exact Or.inr ⟨h1, h2, hadj _ _ hrr'⟩
  intro p hp q hq
  have key : ∀ r, Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p r →
      Relation.ReflTransGen (fun a b => a ∈ V ∧ b ∈ V ∧ kingAdj a b) p (fold r) := by
    intro r hr
    induction hr with
    | refl => rw [hfoldV p hp]
    | @tail b c _ hbc ih =>
        rcases hstep b c hbc.1 hbc.2.1 hbc.2.2 with e | ⟨h1, h2, h3⟩
        · rwa [← e]
        · exact ih.tail ⟨h1, h2, h3⟩
  have := key q (hS p (upperHalf_subset hp) q (upperHalf_subset hq))
  rwa [hfoldV q hq] at this

/-- Some cell of the upper half has `h ≤ 1`: the top cell of a step across
the axis, or any cell when the whole animal lies on the axis. -/
lemma exists_upperHalf_le_one (hh : ∀ p, h (σ p) = -h p) (hSσ : S.image σ = S)
    (hlip : ∀ p q, kingAdj p q → |h p - h q| ≤ 2)
    (hS : KingConnected S) (hne : S.Nonempty) : ∃ p ∈ upperHalf h S, h p ≤ 1 := by
  obtain ⟨p, hp⟩ := hne
  by_cases hlow : ∃ q ∈ S, h q < 0
  · obtain ⟨q, hq, hq0⟩ := hlow
    have hp' : ∃ p ∈ S, 0 ≤ h p := by
      by_cases h0 : 0 ≤ h p
      · exact ⟨p, hp, h0⟩
      · exact ⟨σ p, mem_of_image_eq hSσ hp, by rw [hh]; omega⟩
    obtain ⟨p, hp, hp0⟩ := hp'
    obtain ⟨a, ha, b, hb, ha0, hb0, hab⟩ :=
      exists_edge_of_connected hS (fun r => 0 ≤ h r) hp hq hp0 (by omega)
    refine ⟨a, mem_upperHalf.2 ⟨ha, ha0⟩, ?_⟩
    have := hlip a b hab
    rw [abs_le] at this
    omega
  · simp only [not_exists, not_and, not_lt] at hlow
    refine ⟨p, mem_upperHalf.2 ⟨hp, hlow p hp⟩, ?_⟩
    have := hlow (σ p) (mem_of_image_eq hSσ hp)
    rw [hh] at this
    omega

/-- The minimum of `h` over a finset (junk `0` on the empty set). -/
noncomputable def hmin (h : ℤ × ℤ → ℤ) (V : Finset (ℤ × ℤ)) : ℤ :=
  if hV : V.Nonempty then V.inf' hV h else 0

lemma hmin_eq (h : ℤ × ℤ → ℤ) {V : Finset (ℤ × ℤ)} (hV : V.Nonempty) :
    hmin h V = V.inf' hV h := dif_pos hV

/-- On the upper half, `0 ≤ hmin h ≤ 1`. -/
lemma hmin_upperHalf (hh : ∀ p, h (σ p) = -h p) (hSσ : S.image σ = S)
    (hlip : ∀ p q, kingAdj p q → |h p - h q| ≤ 2)
    (hS : KingConnected S) (hne : S.Nonempty) (hV : (upperHalf h S).Nonempty) :
    0 ≤ hmin h (upperHalf h S) ∧ hmin h (upperHalf h S) ≤ 1 := by
  rw [hmin_eq h hV]
  constructor
  · exact Finset.le_inf' hV h fun p hp => (mem_upperHalf.1 hp).2
  · obtain ⟨p, hp, hp1⟩ := exists_upperHalf_le_one hh hSσ hlip hS hne
    exact (Finset.inf'_le h hp).trans hp1

end Half

/-! ## The combinatorial half, for the half turn -/

/-- A good half of an `σ`-symmetric set: connected, meeting each `σ`-orbit at
most once. -/
def IsHalf (σ : ℤ × ℤ → ℤ × ℤ) (W : Finset (ℤ × ℤ)) : Prop :=
  KingConnected W ∧ ∀ p ∈ W, σ p ∈ W → σ p = p

/-- **A maximal good half covers every orbit.** -/
lemma exists_half {σ : ℤ × ℤ → ℤ × ℤ} (hσσ : ∀ p, σ (σ p) = p)
    (hadj : ∀ p q, kingAdj p q → kingAdj (σ p) (σ q))
    {S : Finset (ℤ × ℤ)} (hS : KingConnected S) (hSσ : S.image σ = S) (hne : S.Nonempty) :
    ∃ W ⊆ S, IsHalf σ W ∧ W.Nonempty ∧ W ∪ W.image σ = S := by
  classical
  set C := S.powerset.filter (fun W => W.Nonempty ∧ IsHalf σ W) with hCdef
  have hmemC : ∀ W, W ∈ C ↔ W ⊆ S ∧ W.Nonempty ∧ IsHalf σ W := fun W => by
    simp [hCdef, Finset.mem_filter, Finset.mem_powerset]
  obtain ⟨p₀, hp₀⟩ := hne
  have hC : C.Nonempty := by
    refine ⟨{p₀}, (hmemC _).2 ⟨Finset.singleton_subset_iff.2 hp₀,
      Finset.singleton_nonempty p₀, kingConnected_singleton p₀, ?_⟩⟩
    · intro p hp hσp
      rw [Finset.mem_singleton] at hp hσp
      subst hp
      exact hσp
  obtain ⟨W, hWC, hmax⟩ := Finset.exists_max_image C Finset.card hC
  obtain ⟨hWS, hWne, hWgood⟩ := (hmemC W).1 hWC
  refine ⟨W, hWS, hWgood, hWne, ?_⟩
  -- a good half one cell bigger than `W` contradicts maximality
  have hbig : ∀ c, c ∈ S → c ∉ W ∪ W.image σ → ∀ w ∈ W, kingAdj w c → False := by
    intro c hc hcn w hw hwc
    have hcW : c ∉ W := fun h => hcn (Finset.mem_union_left _ h)
    have hcσ : c ∉ W.image σ := fun h => hcn (Finset.mem_union_right _ h)
    have hgood : IsHalf σ (insert c W) := by
      refine ⟨kingConnected_insert hWgood.1 hw hwc, ?_⟩
      intro p hp hσp
      rw [Finset.mem_insert] at hp hσp
      rcases hp with rfl | hp
      · rcases hσp with e | e
        · exact e
        · exact absurd ((mem_image_of_involutive hσσ).2 e) hcσ
      · rcases hσp with e | e
        · exact absurd (Finset.mem_image_of_mem σ hp) (e ▸ hcσ)
        · exact hWgood.2 p hp e
    have hmem : insert c W ∈ C :=
      (hmemC _).2 ⟨Finset.insert_subset hc hWS, Finset.insert_nonempty c W, hgood⟩
    have := hmax _ hmem
    rw [Finset.card_insert_of_notMem hcW] at this
    omega
  apply Finset.Subset.antisymm
  · exact Finset.union_subset hWS ((Finset.image_subset_image hWS).trans hSσ.subset)
  · intro q hq
    by_contra hqn
    obtain ⟨w₀, hw₀⟩ := hWne
    have key : ∀ r,
        Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) w₀ r →
        r ∈ W ∪ W.image σ := by
      intro r hr
      induction hr with
      | refl => exact Finset.mem_union_left _ hw₀
      | @tail b c _ hbc ih =>
          by_contra hc
          rcases Finset.mem_union.1 ih with hb | hb
          · exact hbig c hbc.2.1 hc b hb hbc.2.2
          · obtain ⟨w, hw, rfl⟩ := Finset.mem_image.1 hb
            have hσc : σ c ∈ S := mem_of_image_eq hSσ hbc.2.1
            have hσcn : σ c ∉ W ∪ W.image σ := by
              intro h
              rcases Finset.mem_union.1 h with h | h
              · exact hc (Finset.mem_union_right _ ((mem_image_of_involutive hσσ).2 h))
              · exact hc (Finset.mem_union_left _ (by
                  have := (mem_image_of_involutive hσσ).1 h
                  rwa [hσσ] at this))
            have hadj' : kingAdj w (σ c) := by
              have := hadj _ _ hbc.2.2
              rwa [hσσ] at this
            exact hbig (σ c) hσc hσcn w hw hadj'
    exact hqn (key q (hS w₀ (hWS hw₀) q hq))

lemma card_of_isHalf {σ : ℤ × ℤ → ℤ × ℤ} (hσσ : ∀ p, σ (σ p) = p)
    {S W : Finset (ℤ × ℤ)} (hW : IsHalf σ W) (hWS : W ∪ W.image σ = S) :
    S.card + (W.filter fun p => σ p = p).card = 2 * W.card := by
  have h1 := card_add_card_inter_image hσσ hWS
  have h2 : W ∩ W.image σ = W.filter fun p => σ p = p := by
    ext p
    simp only [Finset.mem_inter, mem_image_of_involutive hσσ, Finset.mem_filter]
    constructor
    · rintro ⟨hp, hσp⟩
      exact ⟨hp, hW.2 p hp hσp⟩
    · rintro ⟨hp, e⟩
      exact ⟨hp, by rw [e]; exact hp⟩
  rw [h2] at h1
  omega

/-! ## The fixed animals as a finset -/

/-- The polyplets of `n` cells, as a finset. -/
noncomputable def polypletsFinset (n : ℕ) : Finset (Finset (ℤ × ℤ)) := (polyplets_finite n).toFinset

lemma mem_polypletsFinset {n : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ polypletsFinset n ↔ IsPolyplet n S := by
  simp [polypletsFinset, polyplets]

lemma card_polypletsFinset (n : ℕ) : (polypletsFinset n).card = a n :=
  (Set.ncard_eq_toFinset_card _ (polyplets_finite n)).symm

/-- The polyplets of `n` cells fixed by `g`. -/
noncomputable def fixedFinset (n : ℕ) (g : D4) : Finset (Finset (ℤ × ℤ)) :=
  (polypletsFinset n).filter fun S => anchor (S.image (D4.toFun g)) = S

lemma mem_fixedFinset {n : ℕ} {g : D4} {S : Finset (ℤ × ℤ)} :
    S ∈ fixedFinset n g ↔ IsPolyplet n S ∧ anchor (S.image (D4.toFun g)) = S := by
  simp [fixedFinset, mem_polypletsFinset]

lemma fixCount_eq_card_fixedFinset (n : ℕ) (g : D4) : fixCount n g = (fixedFinset n g).card := by
  have hfin : {S | IsPolyplet n S ∧ anchor (S.image (D4.toFun g)) = S} =
      ↑(fixedFinset n g) := by
    ext S
    simp [mem_fixedFinset]
  rw [fixCount_eq_ncard, hfin, Set.ncard_coe_finset]

/-- A finset counted by an encoding with a left inverse. -/
lemma card_le_of_recon {α β : Type*} {s : Finset α} {t : Finset β} (Φ : α → β)
    (recon : β → α) (hmaps : ∀ x ∈ s, Φ x ∈ t) (hrecon : ∀ x ∈ s, recon (Φ x) = x) :
    s.card ≤ t.card :=
  Finset.card_le_card_of_injOn Φ (fun x hx => hmaps x hx)
    (fun x hx y hy he => by rw [← hrecon x hx, ← hrecon y hy, he])

/-- A fibred count, split at `K`: the fibres below `K` bounded one way, the
fibres from `K` to `n` another. -/
lemma card_le_split {α : Type*} (s : Finset α) (f : α → ℕ) {n K : ℕ} (hK : K ≤ n)
    (hf : ∀ x ∈ s, f x ≤ n) (c₁ c₂ : ℕ → ℕ)
    (h₁ : ∀ k, (s.filter fun x => f x = k).card ≤ c₁ k)
    (h₂ : ∀ k, (s.filter fun x => f x = k).card ≤ c₂ k) :
    s.card ≤ (∑ k ∈ Finset.range K, c₁ k) + ∑ k ∈ Finset.Icc K n, c₂ k := by
  rw [Finset.card_eq_sum_card_fiberwise (f := f) (t := Finset.range (n + 1))
      (fun x hx => by rw [Finset.mem_coe, Finset.mem_range]; exact Nat.lt_succ_of_le (hf x hx)),
    ← Finset.sum_range_add_sum_Ico _ (Nat.le_succ_of_le hK), Nat.succ_eq_add_one,
    Finset.Ico_add_one_right_eq_Icc]
  gcongr with k _ k _
  · exact h₁ k
  · exact h₂ k

/-- The pairs `(animal of `m` cells, offset in {0, 1})` satisfying anything. -/
lemma card_filter_polypletsFinset_le (m : ℕ) (P : Finset (ℤ × ℤ) × ℤ → Prop) [DecidablePred P] :
    ((polypletsFinset m ×ˢ ({0, 1} : Finset ℤ)).filter P).card ≤ 2 * a m := by
  calc ((polypletsFinset m ×ˢ ({0, 1} : Finset ℤ)).filter P).card
      ≤ (polypletsFinset m ×ˢ ({0, 1} : Finset ℤ)).card := Finset.card_filter_le _ _
    _ = 2 * a m := by
        rw [Finset.card_product, card_polypletsFinset]
        simp [mul_comm]

/-! ## The box and the crude count -/

/-- The `n × n` box every polyplet of at most `n` cells lives in. -/
noncomputable def boxN (n : ℕ) : Finset (ℤ × ℤ) :=
  Finset.Icc (0 : ℤ) (n - 1) ×ˢ Finset.Icc (0 : ℤ) (n - 1)

lemma mem_boxN {n : ℕ} {p : ℤ × ℤ} :
    p ∈ boxN n ↔
      (0 ≤ p.1 ∧ p.1 ≤ (n : ℤ) - 1) ∧ (0 ≤ p.2 ∧ p.2 ≤ (n : ℤ) - 1) := by
  simp [boxN, Finset.mem_product, Finset.mem_Icc]

lemma card_boxN (n : ℕ) : (boxN n).card = n * n := by
  simp [boxN, Int.card_Icc]

lemma mem_boxN_of_isPolyplet {m n : ℕ} (hmn : m ≤ n) {S : Finset (ℤ × ℤ)}
    (hS : IsPolyplet m S) {p : ℤ × ℤ} (hp : p ∈ S) : p ∈ boxN n := by
  rw [mem_boxN]
  have h1 := IsPolyplet.x_le hS hp
  have h2 := IsPolyplet.y_le hS hp
  have h3 := hS.anchored.x_nonneg p hp
  have h4 := hS.anchored.y_nonneg p hp
  omega

/-- **The crude count.** A family of pairs `(V', b)` whose `V'` lie in the
`n × n` box, split by a key into the cells on one line (`ax`) and `u` cells off
it, has at most `#keys · 2 ^ n · (n²) ^ u` members: the line part is a subset
of `n` columns, the off part a `u`-subset of the box. -/
lemma card_le_crude {K : Type*} (A : Finset (Finset (ℤ × ℤ) × ℤ))
    (key : Finset (ℤ × ℤ) × ℤ → K) (Ks : Finset K)
    (ax : K → ℤ × ℤ → Prop) [∀ k, DecidablePred (ax k)] (lineY : K → ℤ → ℤ)
    (n u : ℕ)
    (hkey : ∀ z ∈ A, key z ∈ Ks)
    (hb : ∀ z ∈ A, ∀ w ∈ A, key z = key w → z.2 = w.2)
    (hline : ∀ k p, ax k p → p.2 = lineY k p.1)
    (hbox : ∀ z ∈ A, ∀ p ∈ z.1, p ∈ boxN n)
    (hoff : ∀ z ∈ A, (z.1.filter fun p => ¬ ax (key z) p).card = u) :
    A.card ≤ Ks.card * 2 ^ n * (n * n) ^ u := by
  classical
  let enc : Finset (ℤ × ℤ) × ℤ → K × Finset ℤ × Finset (ℤ × ℤ) := fun z =>
    (key z, (z.1.filter (ax (key z))).image Prod.fst, z.1.filter fun p => ¬ ax (key z) p)
  have hax : ∀ z ∈ A, z.1.filter (ax (key z)) =
      ((z.1.filter (ax (key z))).image Prod.fst).image fun x => (x, lineY (key z) x) := by
    intro z _
    ext p
    simp only [Finset.mem_image, Finset.mem_filter, exists_exists_and_eq_and]
    constructor
    · intro hp
      exact ⟨p, hp, Prod.ext rfl (hline _ _ hp.2).symm⟩
    · rintro ⟨q, hq, rfl⟩
      have := hline _ _ hq.2
      simpa [← this] using hq
  have hmaps : Set.MapsTo enc ↑A
      ↑(Ks ×ˢ (Finset.Icc (0 : ℤ) (n - 1)).powerset ×ˢ (boxN n).powersetCard u) := by
    intro z hz
    rw [Finset.mem_coe] at hz ⊢
    rw [Finset.mem_product, Finset.mem_product, Finset.mem_powerset, Finset.mem_powersetCard]
    refine ⟨hkey z hz, ?_, ?_, hoff z hz⟩
    · intro x hx
      obtain ⟨p, hp, rfl⟩ := Finset.mem_image.1 hx
      have := (mem_boxN.1 (hbox z hz p (Finset.mem_filter.1 hp).1)).1
      rw [Finset.mem_Icc]
      exact this
    · intro p hp
      exact hbox z hz p (Finset.mem_filter.1 hp).1
  have hinj : Set.InjOn enc A := by
    intro z hz w hw he
    simp only [enc, Prod.mk.injEq] at he
    obtain ⟨hk, hxs, hoff'⟩ := he
    refine Prod.ext ?_ (hb z hz w hw hk)
    have hz' := hax z hz
    have hw' := hax w hw
    rw [hk] at hz' hoff' hxs
    have e1 : z.1.filter (ax (key w)) = w.1.filter (ax (key w)) := by
      rw [hz', hxs]
      exact hw'.symm
    rw [← Finset.filter_union_filter_not_eq (ax (key w)) z.1,
      ← Finset.filter_union_filter_not_eq (ax (key w)) w.1, e1, hoff']
  calc A.card
      ≤ (Ks ×ˢ (Finset.Icc (0 : ℤ) (n - 1)).powerset ×ˢ (boxN n).powersetCard u).card :=
        Finset.card_le_card_of_injOn enc hmaps hinj
    _ = Ks.card * 2 ^ n * (n * n).choose u := by
        rw [Finset.card_product, Finset.card_product, Finset.card_powerset,
          Finset.card_powersetCard, Int.card_Icc, card_boxN]
        simp [mul_assoc]
    _ ≤ Ks.card * 2 ^ n * (n * n) ^ u := by
        gcongr
        exact Nat.choose_le_pow _ _

/-! ## Minima -/

lemma hmin_image {f g : ℤ × ℤ → ℤ} {φ : ℤ × ℤ → ℤ × ℤ} {c : ℤ}
    (hfg : ∀ p, f (φ p) = g p + c) {V : Finset (ℤ × ℤ)} (hV : V.Nonempty) :
    hmin f (V.image φ) = hmin g V + c := by
  have hVi : (V.image φ).Nonempty := hV.image φ
  rw [hmin_eq f hVi, hmin_eq g hV]
  apply le_antisymm
  · obtain ⟨p, hp, hpe⟩ := Finset.exists_mem_eq_inf' hV g
    rw [hpe, ← hfg]
    exact Finset.inf'_le f (Finset.mem_image_of_mem φ hp)
  · refine Finset.le_inf' hVi f fun q hq => ?_
    obtain ⟨p, hp, rfl⟩ := Finset.mem_image.1 hq
    rw [hfg]
    have := Finset.inf'_le g hp
    omega

lemma hmin_two_mul_add {f : ℤ × ℤ → ℤ} {c : ℤ} {V : Finset (ℤ × ℤ)}
    (hV : V.Nonempty) : hmin (fun p => 2 * f p + c) V = 2 * hmin f V + c := by
  rw [hmin_eq _ hV, hmin_eq f hV]
  apply le_antisymm
  · obtain ⟨p, hp, hpe⟩ := Finset.exists_mem_eq_inf' hV f
    rw [hpe]
    exact Finset.inf'_le (fun p => 2 * f p + c) hp
  · refine Finset.le_inf' hV _ fun q hq => ?_
    have := Finset.inf'_le f hq
    omega

lemma corner_fst_eq_hmin {V : Finset (ℤ × ℤ)} (hV : V.Nonempty) :
    (corner V).1 = hmin Prod.fst V := by
  rw [corner, dif_pos hV, hmin_eq _ hV]

lemma corner_snd_eq_hmin {V : Finset (ℤ × ℤ)} (hV : V.Nonempty) :
    (corner V).2 = hmin Prod.snd V := by
  rw [corner, dif_pos hV, hmin_eq _ hV]

lemma hmin_mem {f : ℤ × ℤ → ℤ} {V : Finset (ℤ × ℤ)} (hV : V.Nonempty) :
    ∃ p ∈ V, hmin f V = f p := by
  rw [hmin_eq f hV]
  exact Finset.exists_mem_eq_inf' hV f

/-- The fixed animals are nonempty, and so is any half of them. -/
lemma fixedFinset_nonempty {n : ℕ} {g : D4} {S : Finset (ℤ × ℤ)} (hS : S ∈ fixedFinset n g) :
    S.Nonempty :=
  (mem_fixedFinset.1 hS).1.nonempty

/-- A symmetry of a nonempty finite set whose square is a translation squares
to the identity. -/
lemma translation_eq_zero {σ : ℤ × ℤ → ℤ × ℤ} {w : ℤ × ℤ}
    (hw : ∀ p, σ (σ p) = p + w) {S : Finset (ℤ × ℤ)} (hSσ : S.image σ = S)
    (hne : S.Nonempty) : w = 0 := by
  refine translate_eq_self hne ?_
  change S.image (fun p => p + w) = S
  rw [show (fun p : ℤ × ℤ => p + w) = σ ∘ σ from funext fun p => (hw p).symm,
    ← Finset.image_image, hSσ, hSσ]

/-- The image of a fixed animal under its symmetry, anchored, is itself:
in terms of the conjugated map `σ`. -/
lemma image_eq_of_fix {n : ℕ} {g : D4} {S : Finset (ℤ × ℤ)} (hS : S ∈ fixedFinset n g)
    (σ : ℤ × ℤ → ℤ × ℤ)
    (hσ : ∀ p, σ p = D4.toFun g p - corner (S.image (D4.toFun g))) :
    S.image σ = S := by
  have h := (mem_fixedFinset.1 hS).2
  rw [anchor, Finset.image_image] at h
  convert h using 2
  funext p
  exact hσ p

/-- The upper half of a fixed animal is nonempty. -/
lemma upperHalf_nonempty {σ : ℤ × ℤ → ℤ × ℤ} {h : ℤ × ℤ → ℤ}
    {S : Finset (ℤ × ℤ)} (hh : ∀ p, h (σ p) = -h p) (hSσ : S.image σ = S)
    (hne : S.Nonempty) :
    (upperHalf h S).Nonempty := by
  obtain ⟨p, hp⟩ := hne
  by_cases h0 : 0 ≤ h p
  · exact ⟨p, mem_upperHalf.2 ⟨hp, h0⟩⟩
  · exact ⟨σ p, mem_upperHalf.2 ⟨mem_of_image_eq hSσ hp, by rw [hh]; omega⟩⟩

/-- The cells of the upper half off the axis. -/
lemma card_upperHalf_off {σ : ℤ × ℤ → ℤ × ℤ} {h : ℤ × ℤ → ℤ}
    {S : Finset (ℤ × ℤ)} (hσσ : ∀ p, σ (σ p) = p) (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) :
    2 * ((upperHalf h S).filter fun p => ¬ h p = 0).card + (axisCells h S).card = S.card := by
  have h1 := two_mul_card_upperHalf hσσ hh hSσ
  have h2 := Finset.card_filter_add_card_filter_not (s := upperHalf h S) (fun p => h p = 0)
  have h3 : (upperHalf h S).filter (fun p => h p = 0) = axisCells h S := by
    ext p
    simp only [Finset.mem_filter, mem_upperHalf, axisCells]
    constructor
    · rintro ⟨⟨hp, -⟩, e⟩; exact ⟨hp, e⟩
    · rintro ⟨hp, e⟩; exact ⟨⟨hp, by omega⟩, e⟩
  rw [h3] at h2
  omega

/-- The upper half's size and its off-axis count, from the animal's. -/
lemma card_upperHalf_eq {σ : ℤ × ℤ → ℤ × ℤ} {h : ℤ × ℤ → ℤ}
    {S : Finset (ℤ × ℤ)} (hσσ : ∀ p, σ (σ p) = p) (hh : ∀ p, h (σ p) = -h p)
    (hSσ : S.image σ = S) :
    (upperHalf h S).card = S.card - ((upperHalf h S).filter fun p => ¬ h p = 0).card ∧
      ((upperHalf h S).filter fun p => ¬ h p = 0).card ≤ S.card := by
  have h1 := two_mul_card_upperHalf hσσ hh hSσ
  have h2 := card_upperHalf_off hσσ hh hSσ
  omega

/-! ## The axis-parallel mirror `sr 0` -/

namespace AxisMirror

/-- The translation that anchors the mirrored animal. -/
noncomputable def t (S : Finset (ℤ × ℤ)) : ℤ × ℤ := corner (S.image mirror)

/-- The mirror symmetry of `S`, as a map of the plane. -/
def σ (t : ℤ × ℤ) (p : ℤ × ℤ) : ℤ × ℤ := (p.1 - t.1, -p.2 - t.2)

/-- Twice the signed distance to the axis `2y = -t₂`. -/
def h (t : ℤ × ℤ) (p : ℤ × ℤ) : ℤ := 2 * p.2 + t.2

variable {n : ℕ} {S : Finset (ℤ × ℤ)}

lemma image_σ (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : S.image (σ (t S)) = S :=
  image_eq_of_fix hS (σ (t S)) fun p => by simp [σ, t, D4.toFun_sr0, mirror, Prod.ext_iff]

lemma t_fst (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : (t S).1 = 0 := by
  have := translation_eq_zero (w := (-2 * (t S).1, 0))
    (fun p => by simp only [σ, Prod.ext_iff, Prod.fst_add, Prod.snd_add]; constructor <;> ring)
    (image_σ hS) (fixedFinset_nonempty hS)
  rw [Prod.ext_iff] at this
  simp only [Prod.fst_zero] at this
  omega

lemma σσ {t : ℤ × ℤ} (ht : t.1 = 0) (p : ℤ × ℤ) : σ t (σ t p) = p := by
  simp only [σ, Prod.ext_iff]
  constructor <;> omega

lemma hσ (t p : ℤ × ℤ) : h t (σ t p) = -h t p := by
  simp only [h, σ]; ring

lemma adj (t : ℤ × ℤ) (p q : ℤ × ℤ) (hpq : kingAdj p q) : kingAdj (σ t p) (σ t q) := by
  rw [kingAdj_iff'] at *
  simp only [σ]
  omega

lemma cross {t : ℤ × ℤ} (ht : t.1 = 0) (p q : ℤ × ℤ) (hpq : kingAdj p q)
    (hp : 0 ≤ h t p) (hq : h t q < 0) :
    σ t q = p ∨ kingAdj p (σ t q) := by
  by_cases e : σ t q = p
  · exact Or.inl e
  · right
    rw [kingAdj_iff'] at *
    simp only [σ, h, Prod.ext_iff] at *
    omega

lemma lip (t : ℤ × ℤ) (p q : ℤ × ℤ) (hpq : kingAdj p q) : |h t p - h t q| ≤ 2 := by
  rw [kingAdj_iff'] at hpq
  rw [abs_le]
  simp only [h]
  omega

/-- The upper half. -/
noncomputable def V (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := upperHalf (h (t S)) S

/-- The axis offset, `0` or `1`. -/
noncomputable def b (S : Finset (ℤ × ℤ)) : ℤ := hmin (h (t S)) (V S)

/-- The number of cells of the half off the axis. -/
noncomputable def u (S : Finset (ℤ × ℤ)) : ℕ := ((V S).filter fun p => ¬ h (t S) p = 0).card

/-- The encoding: the anchored half and the axis offset. -/
noncomputable def Φ (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) × ℤ := (anchor (V S), b S)

/-- The decoding. -/
noncomputable def recon (z : Finset (ℤ × ℤ) × ℤ) : Finset (ℤ × ℤ) :=
  anchor (z.1 ∪ z.1.image fun p => (p.1, -p.2 - z.2))

lemma V_nonempty (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : (V S).Nonempty :=
  upperHalf_nonempty (hσ (t S)) (image_σ hS) (fixedFinset_nonempty hS)

lemma b_eq (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) :
    b S = (t S).2 + 2 * (corner (V S)).2 := by
  have hV := V_nonempty hS
  rw [b, corner_snd_eq_hmin hV]
  change hmin (fun p => 2 * p.2 + (t S).2) (V S) = _
  rw [hmin_two_mul_add hV]
  ring

lemma b_mem (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : 0 ≤ b S ∧ b S ≤ 1 :=
  hmin_upperHalf (hσ (t S)) (image_σ hS) (lip (t S)) (mem_fixedFinset.1 hS).1.conn
    (fixedFinset_nonempty hS) (V_nonempty hS)

lemma recon_Φ (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : recon (Φ S) = S := by
  have ht := t_fst hS
  have hb := b_eq hS
  have := eq_reanchor_of_union (σ (t S)) (mem_fixedFinset.1 hS).1.anchored
    (upperHalf_union (σσ ht) (hσ (t S)) (image_σ hS))
  rw [recon, Φ]
  conv_rhs => rw [this]
  congr 3
  funext p
  simp only [σ, Prod.ext_iff, Prod.fst_add, Prod.snd_add, Prod.fst_sub, Prod.snd_sub]
  have hb' : b S = (t S).2 + 2 * (corner (upperHalf (h (t S)) S)).2 := hb
  change _ ∧ -p.2 - b S = _
  rw [hb']
  constructor <;> omega

lemma V_card (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : (V S).card = n - u S := by
  have := (card_upperHalf_eq (σσ (t_fst hS)) (hσ (t S)) (image_σ hS)).1
  rwa [(mem_fixedFinset.1 hS).1.card] at this

lemma u_le (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : u S ≤ n := by
  have := (card_upperHalf_eq (σσ (t_fst hS)) (hσ (t S)) (image_σ hS)).2
  rwa [(mem_fixedFinset.1 hS).1.card] at this

/-- The target of the encoding: a anchored animal of `n - u` cells with `u`
cells off the axis `2y + b = 0`, and the offset `b ∈ {0, 1}`. -/
noncomputable def A (n u : ℕ) : Finset (Finset (ℤ × ℤ) × ℤ) :=
  (polypletsFinset (n - u) ×ˢ ({0, 1} : Finset ℤ)).filter fun z =>
    (z.1.filter fun p => ¬ 2 * p.2 + z.2 = 0).card = u

lemma Φ_mem (hS : S ∈ fixedFinset n (DihedralGroup.sr 0)) : Φ S ∈ A n (u S) := by
  have ht := t_fst hS
  have hV := V_nonempty hS
  have hb := b_eq hS
  rw [A, Finset.mem_filter, Finset.mem_product, mem_polypletsFinset]
  refine ⟨⟨⟨?_, ?_, anchor_anchored hV⟩, ?_⟩, ?_⟩
  · rw [Φ, anchor_card]
    exact V_card hS
  · exact kingConnected_anchor
      (upperHalf_connected (hσ (t S)) (image_σ hS) (adj (t S)) (cross ht)
        (mem_fixedFinset.1 hS).1.conn)
  · have := b_mem hS
    simp only [Φ, Finset.mem_insert, Finset.mem_singleton]
    omega
  · simp only [Φ, anchor, Finset.filter_image, u]
    rw [Finset.card_image_of_injective _ (sub_left_injective)]
    congr 1
    apply Finset.filter_congr
    intro p _
    simp only [Prod.snd_sub, h, hb]
    omega

lemma fiber_le (n u : ℕ) :
    ((fixedFinset n (DihedralGroup.sr 0)).filter fun S => AxisMirror.u S = u).card ≤ (A n u).card :=
  card_le_of_recon Φ recon
    (fun S hS => by
      rw [Finset.mem_filter] at hS
      rw [← hS.2]
      exact Φ_mem hS.1)
    (fun S hS => recon_Φ (Finset.mem_filter.1 hS).1)

lemma A_le_a (n u : ℕ) : (A n u).card ≤ 2 * a (n - u) :=
  card_filter_polypletsFinset_le (n - u) _

lemma A_le_crude (n u : ℕ) : (A n u).card ≤ 2 * 2 ^ n * (n * n) ^ u := by
  have := card_le_crude (A n u) (fun z => z.2) ({0, 1} : Finset ℤ)
    (fun b p => 2 * p.2 + b = 0) (fun b x => -b / 2) n u
    (fun z hz => ((Finset.mem_product.1 (Finset.mem_filter.1 hz).1).2))
    (fun z _ w _ e => e)
    (fun k p e => by omega)
    (fun z hz p hp => mem_boxN_of_isPolyplet (Nat.sub_le n u)
      (mem_polypletsFinset.1 (Finset.mem_product.1 (Finset.mem_filter.1 hz).1).1) hp)
    (fun z hz => (Finset.mem_filter.1 hz).2)
  simpa using this

theorem Hm_le (n K : ℕ) (hK : K ≤ n) :
    Hm n ≤ (∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u) +
      ∑ u ∈ Finset.Icc K n, 2 * a (n - u) := by
  rw [Hm, fixCount_eq_card_fixedFinset]
  refine card_le_split _ AxisMirror.u hK (fun S hS => u_le hS) _ _ (fun u => ?_)
    (fun u => (fiber_le n u).trans (A_le_a n u))
  refine (fiber_le n u).trans ((A_le_crude n u).trans ?_)
  exact Nat.mul_le_mul_right _ (Nat.mul_le_mul_right _ (by omega))

end AxisMirror


/-! ## The diagonal mirror `sr 3` -/

namespace DiagMirror

/-- The translation that anchors the transposed animal. -/
noncomputable def t (S : Finset (ℤ × ℤ)) : ℤ × ℤ :=
  corner (S.image fun p => (p.2, p.1))

/-- The diagonal symmetry of `S`, as a map of the plane. -/
def σ (t : ℤ × ℤ) (p : ℤ × ℤ) : ℤ × ℤ := (p.2 - t.1, p.1 - t.2)

/-- The signed distance to the axis `y - x = t₁`. -/
def h (t : ℤ × ℤ) (p : ℤ × ℤ) : ℤ := p.2 - p.1 - t.1

/-- The diagonal offset of a cell. -/
def dg (p : ℤ × ℤ) : ℤ := p.2 - p.1

variable {n : ℕ} {S : Finset (ℤ × ℤ)}

lemma image_σ (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : S.image (σ (t S)) = S :=
  image_eq_of_fix hS (σ (t S)) fun p => by simp [σ, t, D4.toFun_sr3, Prod.ext_iff]

lemma t_sum (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : (t S).1 + (t S).2 = 0 := by
  have := translation_eq_zero (w := (-((t S).1 + (t S).2), -((t S).1 + (t S).2)))
    (fun p => by simp only [σ, Prod.ext_iff, Prod.fst_add, Prod.snd_add]; constructor <;> ring)
    (image_σ hS) (fixedFinset_nonempty hS)
  rw [Prod.ext_iff] at this
  simp only [Prod.fst_zero] at this
  omega

lemma σσ {t : ℤ × ℤ} (ht : t.1 + t.2 = 0) (p : ℤ × ℤ) : σ t (σ t p) = p := by
  simp only [σ, Prod.ext_iff]
  constructor <;> omega

lemma hσ {t : ℤ × ℤ} (ht : t.1 + t.2 = 0) (p : ℤ × ℤ) : h t (σ t p) = -h t p := by
  simp only [h, σ]; omega

lemma adj (t : ℤ × ℤ) (p q : ℤ × ℤ) (hpq : kingAdj p q) : kingAdj (σ t p) (σ t q) := by
  rw [kingAdj_iff'] at *
  simp only [σ]
  omega

lemma cross {t : ℤ × ℤ} (ht : t.1 + t.2 = 0) (p q : ℤ × ℤ) (hpq : kingAdj p q)
    (hp : 0 ≤ h t p) (hq : h t q < 0) : σ t q = p ∨ kingAdj p (σ t q) := by
  by_cases e : σ t q = p
  · exact Or.inl e
  · right
    rw [kingAdj_iff'] at *
    simp only [σ, h, Prod.ext_iff] at *
    omega

lemma lip (t : ℤ × ℤ) (p q : ℤ × ℤ) (hpq : kingAdj p q) : |h t p - h t q| ≤ 2 := by
  rw [kingAdj_iff'] at hpq
  rw [abs_le]
  simp only [h]
  omega

/-- The upper half. -/
noncomputable def V (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := upperHalf (h (t S)) S

/-- The axis offset, `0` or `1`. -/
noncomputable def b (S : Finset (ℤ × ℤ)) : ℤ := hmin (h (t S)) (V S)

/-- The number of cells of the half off the axis. -/
noncomputable def u (S : Finset (ℤ × ℤ)) : ℕ := ((V S).filter fun p => ¬ h (t S) p = 0).card

/-- The encoding: the anchored half and the axis offset. -/
noncomputable def Φ (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) × ℤ := (anchor (V S), b S)

/-- The axis of a anchored half with offset `b`: the diagonal `y - x = c`. -/
noncomputable def c (z : Finset (ℤ × ℤ) × ℤ) : ℤ := hmin dg z.1 - z.2

/-- The decoding. -/
noncomputable def recon (z : Finset (ℤ × ℤ) × ℤ) : Finset (ℤ × ℤ) :=
  anchor (z.1 ∪ z.1.image fun p => (p.2 - c z, p.1 + c z))

lemma V_nonempty (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : (V S).Nonempty :=
  upperHalf_nonempty (hσ (t_sum hS)) (image_σ hS) (fixedFinset_nonempty hS)

lemma c_Φ (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) :
    c (Φ S) = (t S).1 + (corner (V S)).1 - (corner (V S)).2 := by
  have hV := V_nonempty hS
  rw [c, Φ, anchor, hmin_image (g := h (t S)) (c := (t S).1 + (corner (V S)).1 -
    (corner (V S)).2) (fun p => by simp only [dg, h, Prod.fst_sub, Prod.snd_sub]; ring) hV]
  rw [b]
  ring

lemma b_mem (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : 0 ≤ b S ∧ b S ≤ 1 :=
  hmin_upperHalf (hσ (t_sum hS)) (image_σ hS) (lip (t S)) (mem_fixedFinset.1 hS).1.conn
    (fixedFinset_nonempty hS) (V_nonempty hS)

lemma recon_Φ (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : recon (Φ S) = S := by
  have ht := t_sum hS
  have hc : c (Φ S) = (t S).1 + (corner (upperHalf (h (t S)) S)).1 -
    (corner (upperHalf (h (t S)) S)).2 := c_Φ hS
  have := eq_reanchor_of_union (σ (t S)) (mem_fixedFinset.1 hS).1.anchored
    (upperHalf_union (σσ ht) (hσ ht) (image_σ hS))
  rw [recon, hc]
  conv_rhs => rw [this]
  congr 3
  funext p
  simp only [σ, Prod.ext_iff, Prod.fst_add, Prod.snd_add, Prod.fst_sub, Prod.snd_sub]
  constructor <;> omega

lemma V_card (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : (V S).card = n - u S := by
  have ht := t_sum hS
  have := (card_upperHalf_eq (σσ ht) (hσ ht) (image_σ hS)).1
  rwa [(mem_fixedFinset.1 hS).1.card] at this

lemma u_le (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : u S ≤ n := by
  have ht := t_sum hS
  have := (card_upperHalf_eq (σσ ht) (hσ ht) (image_σ hS)).2
  rwa [(mem_fixedFinset.1 hS).1.card] at this

/-- The target of the encoding: a anchored animal of `n - u` cells with `u`
cells off its axis, and the offset `b ∈ {0, 1}`. -/
noncomputable def A (n u : ℕ) : Finset (Finset (ℤ × ℤ) × ℤ) :=
  (polypletsFinset (n - u) ×ˢ ({0, 1} : Finset ℤ)).filter fun z =>
    (z.1.filter fun p => ¬ dg p = c z).card = u

lemma Φ_mem (hS : S ∈ fixedFinset n (DihedralGroup.sr 3)) : Φ S ∈ A n (u S) := by
  have ht := t_sum hS
  have hV := V_nonempty hS
  have hc := c_Φ hS
  rw [A, Finset.mem_filter, Finset.mem_product, mem_polypletsFinset]
  refine ⟨⟨⟨?_, ?_, anchor_anchored hV⟩, ?_⟩, ?_⟩
  · rw [Φ, anchor_card]
    exact V_card hS
  · exact kingConnected_anchor
      (upperHalf_connected (hσ ht) (image_σ hS) (adj (t S)) (cross ht)
        (mem_fixedFinset.1 hS).1.conn)
  · have := b_mem hS
    simp only [Φ, Finset.mem_insert, Finset.mem_singleton]
    omega
  · rw [hc]
    simp only [Φ, anchor, Finset.filter_image, u]
    rw [Finset.card_image_of_injective _ (sub_left_injective)]
    congr 1
    apply Finset.filter_congr
    intro p _
    simp only [Prod.fst_sub, Prod.snd_sub, h, dg]
    omega

lemma fiber_le (n u : ℕ) :
    ((fixedFinset n (DihedralGroup.sr 3)).filter fun S => DiagMirror.u S = u).card ≤ (A n u).card :=
  card_le_of_recon Φ recon
    (fun S hS => by
      rw [Finset.mem_filter] at hS
      rw [← hS.2]
      exact Φ_mem hS.1)
    (fun S hS => recon_Φ (Finset.mem_filter.1 hS).1)

lemma A_le_a (n u : ℕ) : (A n u).card ≤ 2 * a (n - u) :=
  card_filter_polypletsFinset_le (n - u) _

lemma A_le_crude (n u : ℕ) : (A n u).card ≤ 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u := by
  have hmem : ∀ z ∈ A n u, IsPolyplet (n - u) z.1 ∧ z.2 ∈ ({0, 1} : Finset ℤ) := by
    intro z hz
    have := Finset.mem_product.1 (Finset.mem_filter.1 hz).1
    exact ⟨mem_polypletsFinset.1 this.1, this.2⟩
  have := card_le_crude (A n u) (fun z => (c z, z.2))
    (Finset.Icc (-(n : ℤ)) n ×ˢ ({0, 1} : Finset ℤ))
    (fun k p => dg p = k.1) (fun k x => x + k.1) n u
    (fun z hz => by
      obtain ⟨hz1, hz2⟩ := hmem z hz
      rw [Finset.mem_product, Finset.mem_Icc]
      refine ⟨?_, hz2⟩
      obtain ⟨p, hp, hpe⟩ := hmin_mem (f := dg) hz1.nonempty
      have hb := mem_boxN_of_isPolyplet (Nat.sub_le n u) hz1 hp
      rw [mem_boxN] at hb
      simp only [Finset.mem_insert, Finset.mem_singleton] at hz2
      simp only [c, hpe, dg]
      omega)
    (fun z _ w _ e => (Prod.mk.inj e).2)
    (fun k p e => by simp only [dg] at e; omega)
    (fun z hz p hp => mem_boxN_of_isPolyplet (Nat.sub_le n u) (hmem z hz).1 hp)
    (fun z hz => (Finset.mem_filter.1 hz).2)
  rw [Finset.card_product, Int.card_Icc] at this
  have h2 : ((n : ℤ) + 1 - -(n : ℤ)).toNat = 2 * n + 1 := by omega
  rw [h2] at this
  simpa [mul_assoc, mul_comm, mul_left_comm] using this

theorem Dm_le (n K : ℕ) (hK : K ≤ n) :
    Dm n ≤ (∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u) +
      ∑ u ∈ Finset.Icc K n, 2 * a (n - u) := by
  rw [Dm, fixCount_eq_card_fixedFinset]
  exact card_le_split _ DiagMirror.u hK (fun S hS => u_le hS) _ _
    (fun u => (fiber_le n u).trans (A_le_crude n u))
    (fun u => (fiber_le n u).trans (A_le_a n u))

end DiagMirror

/-! ## The half turn `r 2` -/

namespace HalfTurn

/-- The translation that anchors the rotated animal. -/
noncomputable def t (S : Finset (ℤ × ℤ)) : ℤ × ℤ := corner (S.image fun p => -p)

/-- The half-turn symmetry of `S`, as a map of the plane. -/
def σ (t : ℤ × ℤ) (p : ℤ × ℤ) : ℤ × ℤ := -p - t

variable {n : ℕ} {S : Finset (ℤ × ℤ)}

lemma image_σ (hS : S ∈ fixedFinset n (DihedralGroup.r 2)) : S.image (σ (t S)) = S :=
  image_eq_of_fix hS (σ (t S)) fun p => by simp [σ, t, D4.toFun_r2]

lemma σσ (t p : ℤ × ℤ) : σ t (σ t p) = p := by
  simp [σ]

lemma adj (t : ℤ × ℤ) (p q : ℤ × ℤ) (hpq : kingAdj p q) : kingAdj (σ t p) (σ t q) := by
  rw [kingAdj_iff'] at *
  simp only [σ, Prod.fst_sub, Prod.snd_sub, Prod.fst_neg, Prod.snd_neg]
  omega

open Classical in
/-- A good half of the animal, chosen once. -/
noncomputable def W (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  if hex : ∃ W ⊆ S, IsHalf (σ (t S)) W ∧ W.Nonempty ∧ W ∪ W.image (σ (t S)) = S then
    Classical.choose hex else ∅

lemma W_spec (hS : S ∈ fixedFinset n (DihedralGroup.r 2)) :
    W S ⊆ S ∧ IsHalf (σ (t S)) (W S) ∧ (W S).Nonempty ∧
      W S ∪ (W S).image (σ (t S)) = S := by
  have hex := exists_half (σσ (t S)) (adj (t S)) (mem_fixedFinset.1 hS).1.conn (image_σ hS)
    (fixedFinset_nonempty hS)
  rw [W, dif_pos hex]
  exact Classical.choose_spec hex

/-- The encoding: the anchored half and the centre offset. -/
noncomputable def Φ (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) × (ℤ × ℤ) :=
  (anchor (W S), t S + corner (W S) + corner (W S))

/-- The decoding. -/
noncomputable def recon (z : Finset (ℤ × ℤ) × (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  anchor (z.1 ∪ z.1.image fun p => -p - z.2)

lemma recon_Φ (hS : S ∈ fixedFinset n (DihedralGroup.r 2)) : recon (Φ S) = S := by
  have := eq_reanchor_of_union (σ (t S)) (mem_fixedFinset.1 hS).1.anchored (W_spec hS).2.2.2
  rw [recon, Φ]
  conv_rhs => rw [this]
  congr 3
  funext p
  simp only [σ, Prod.ext_iff, Prod.fst_add, Prod.snd_add, Prod.fst_sub, Prod.snd_sub,
    Prod.fst_neg, Prod.snd_neg]
  constructor <;> ring

lemma W_card (hS : S ∈ fixedFinset n (DihedralGroup.r 2)) : (W S).card = (n + 1) / 2 := by
  obtain ⟨-, hgood, -, hunion⟩ := W_spec hS
  have h1 := card_of_isHalf (σσ (t S)) hgood hunion
  rw [(mem_fixedFinset.1 hS).1.card] at h1
  have h2 : ((W S).filter fun p => σ (t S) p = p).card ≤ 1 := by
    rw [Finset.card_le_one]
    intro p hp q hq
    rw [Finset.mem_filter] at hp hq
    have hp' := hp.2
    have hq' := hq.2
    simp only [σ, Prod.ext_iff, Prod.fst_sub, Prod.snd_sub, Prod.fst_neg, Prod.snd_neg] at hp' hq'
    rw [Prod.ext_iff]
    omega
  omega

/-- The centre offset is bounded by the box. -/
lemma Φ_snd_mem (hS : S ∈ fixedFinset n (DihedralGroup.r 2)) :
    (Φ S).2 ∈ Finset.Icc (-(2 * (n : ℤ))) (2 * n) ×ˢ
      Finset.Icc (-(2 * (n : ℤ))) (2 * n) := by
  obtain ⟨hWS, -, hWne, -⟩ := W_spec hS
  have hcan := (mem_fixedFinset.1 hS).1
  obtain ⟨w, hw⟩ := hWne
  have hw1 := mem_boxN_of_isPolyplet le_rfl hcan (hWS hw)
  have hw2 := mem_boxN_of_isPolyplet le_rfl hcan (mem_of_image_eq (image_σ hS) (hWS hw))
  obtain ⟨p1, hp1, hp1e⟩ := hmin_mem (f := Prod.fst) ⟨w, hw⟩
  obtain ⟨p2, hp2, hp2e⟩ := hmin_mem (f := Prod.snd) ⟨w, hw⟩
  have hb1 := mem_boxN_of_isPolyplet le_rfl hcan (hWS hp1)
  have hb2 := mem_boxN_of_isPolyplet le_rfl hcan (hWS hp2)
  rw [mem_boxN] at hw1 hw2 hb1 hb2
  rw [Finset.mem_product, Finset.mem_Icc, Finset.mem_Icc]
  simp only [Φ, Prod.fst_add, Prod.snd_add, corner_fst_eq_hmin ⟨w, hw⟩,
    corner_snd_eq_hmin ⟨w, hw⟩,
    hp1e, hp2e]
  simp only [σ, Prod.fst_sub, Prod.snd_sub, Prod.fst_neg, Prod.snd_neg] at hw2
  omega

theorem R180_le (n : ℕ) :
    R180 n ≤ a ((n + 1) / 2) * ((4 * n + 1) * (4 * n + 1)) := by
  rw [R180, fixCount_eq_card_fixedFinset]
  have hcard : (polypletsFinset ((n + 1) / 2) ×ˢ (Finset.Icc (-(2 * (n : ℤ))) (2 * n) ×ˢ
      Finset.Icc (-(2 * (n : ℤ))) (2 * n))).card =
      a ((n + 1) / 2) * ((4 * n + 1) * (4 * n + 1)) := by
    rw [Finset.card_product, Finset.card_product, card_polypletsFinset, Int.card_Icc]
    have : (2 * (n : ℤ) + 1 - -(2 * (n : ℤ))).toNat = 4 * n + 1 := by omega
    rw [this]
  rw [← hcard]
  refine card_le_of_recon Φ recon (fun S hS => ?_) (fun S hS => recon_Φ hS)
  rw [Finset.mem_product, mem_polypletsFinset]
  refine ⟨⟨?_, ?_, anchor_anchored (W_spec hS).2.2.1⟩, Φ_snd_mem hS⟩
  · rw [Φ, anchor_card]
    exact W_card hS
  · exact kingConnected_anchor (W_spec hS).2.1.1

end HalfTurn

/-- A quarterTurn-turn-symmetric animal is half-turn-symmetric. -/
theorem R90_le_R180 (n : ℕ) : R90 n ≤ R180 n := by
  rw [R90, R180, fixCount, fixCount, Nat.card_coe_set_eq, Nat.card_coe_set_eq]
  refine Set.ncard_le_ncard ?_ (Set.toFinite _)
  intro S hS
  simp only [MulAction.mem_fixedBy] at hS ⊢
  have : DihedralGroup.r (2 : ZMod 4) = DihedralGroup.r 1 * DihedralGroup.r 1 := by
    rw [DihedralGroup.r_mul_r]; rfl
  rw [this, mul_smul, hS, hS]


/-! ## The growth lower bound -/

/-- `20 ^ (n / 3) ≤ a n`: supermultiplicativity against `a 3 = 20`. -/
theorem pow_le_a (n : ℕ) : 1 ≤ n → 20 ^ (n / 3) ≤ a n := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    intro hn
    rcases lt_or_ge n 4 with h4 | h4
    · interval_cases n
      · simpa using one_le_a (by norm_num : 1 ≤ 1)
      · simpa using one_le_a (by norm_num : 1 ≤ 2)
      · rw [a_3]; norm_num
    · have h1 := ih (n - 3) (by omega) (by omega)
      have h2 : a 3 * a (n - 3) ≤ a n := by
        have := a_supermul (m := 3) (n := n - 3)
        rwa [show 3 + (n - 3) = n by omega] at this
      rw [show n / 3 = (n - 3) / 3 + 1 by omega, pow_succ, a_3] at *
      omega

/-- `2 ^ n ≤ 4 · 20 ^ (n / 3)`. -/
lemma two_pow_le (n : ℕ) : 2 ^ n ≤ 4 * 20 ^ (n / 3) := by
  induction n using Nat.strong_induction_on with
  | _ n ih =>
    rcases lt_or_ge n 3 with h3 | h3
    · interval_cases n <;> norm_num
    · obtain ⟨m, rfl⟩ : ∃ m, n = m + 3 := ⟨n - 3, by omega⟩
      have := ih m (by omega)
      rw [pow_add, show (m + 3) / 3 = m / 3 + 1 by omega, pow_succ]
      omega

lemma two_pow_le_four_mul_a (n : ℕ) (hn : 1 ≤ n) : 2 ^ n ≤ 4 * a n := by
  have := pow_le_a n hn
  have := two_pow_le n
  omega

/-- `a (n - u) / a n ≤ 4 / 2 ^ u`: the tail of the mirror count. -/
lemma a_sub_div_le (n u : ℕ) (hun : u ≤ n) (hn : 1 ≤ n) :
    (a (n - u) : ℝ) / a n ≤ 4 * (1 / 2) ^ u := by
  have ha : (0 : ℝ) < a n := by exact_mod_cast one_le_a hn
  rcases Nat.eq_zero_or_pos u with rfl | hu
  · rw [Nat.sub_zero, div_self ha.ne']
    norm_num
  rcases eq_or_lt_of_le hun with rfl | hlt
  · rw [Nat.sub_self, a_zero]
    simp only [Nat.cast_zero, zero_div]
    positivity
  · have h1 : a (n - u) * a u ≤ a n := by
      have := a_supermul (m := n - u) (n := u)
      rwa [Nat.sub_add_cancel hun] at this
    have h1' : (a (n - u) : ℝ) * a u ≤ a n := by exact_mod_cast h1
    have h2 : (2 : ℝ) ^ u ≤ 4 * a u := by exact_mod_cast two_pow_le_four_mul_a u hu
    have h0 : (0 : ℝ) ≤ a (n - u) := Nat.cast_nonneg _
    rw [div_le_iff₀ ha, one_div_pow, mul_one_div, div_mul_eq_mul_div,
      le_div_iff₀ (by positivity)]
    nlinarith

/-! ## The limits -/

/-- A nonnegative sequence bounded, for every `K`, by a null sequence plus a
constant `c K` with `c K → 0`, is null. -/
lemma tendsto_zero_of_eventually_le {f : ℕ → ℝ} (hf : ∀ n, 0 ≤ f n)
    (g : ℕ → ℕ → ℝ) (c : ℕ → ℝ)
    (hg : ∀ K, Tendsto (g K) atTop (𝓝 0)) (hc : Tendsto c atTop (𝓝 0))
    (hle : ∀ K, ∀ᶠ n in atTop, f n ≤ g K n + c K) : Tendsto f atTop (𝓝 0) := by
  rw [Metric.tendsto_atTop]
  intro ε hε
  obtain ⟨K, hK⟩ : ∃ K, |c K| < ε / 2 := by
    obtain ⟨N, hN⟩ := (Metric.tendsto_atTop.1 hc) (ε / 2) (by positivity)
    exact ⟨N, by simpa [Real.dist_eq] using hN N le_rfl⟩
  obtain ⟨N₁, hN₁⟩ := (Metric.tendsto_atTop.1 (hg K)) (ε / 2) (by positivity)
  obtain ⟨N₂, hN₂⟩ := Filter.eventually_atTop.1 (hle K)
  refine ⟨max N₁ N₂, fun n hn => ?_⟩
  have h1 := hN₁ n (le_of_max_le_left hn)
  have h2 := hN₂ n (le_of_max_le_right hn)
  rw [Real.dist_eq, sub_zero] at h1 ⊢
  rw [abs_of_nonneg (hf n)]
  have := abs_lt.1 h1
  have := abs_lt.1 hK
  linarith

/-- `(q + 1) ^ k · r ^ q → 0` for `0 ≤ r < 1`. -/
lemma tendsto_succ_pow_mul_pow (k : ℕ) {r : ℝ} (hr0 : 0 < r) (hr : r < 1) :
    Tendsto (fun q : ℕ => ((q : ℝ) + 1) ^ k * r ^ q) atTop (𝓝 0) := by
  have h := (tendsto_pow_const_mul_const_pow_of_abs_lt_one k (abs_lt.2 ⟨by linarith, hr⟩)).comp
    (tendsto_add_atTop_nat 1)
  have h2 := h.const_mul (1 / r)
  rw [mul_zero] at h2
  refine h2.congr fun q => ?_
  simp only [Function.comp, Nat.cast_add, Nat.cast_one, pow_succ]
  field_simp

/-- The head of the mirror bound. -/
lemma head_le (n K : ℕ) (hn : 1 ≤ n) :
    ((∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u : ℕ) : ℝ) / a n ≤
      48 * K * 9 ^ K * (((n / 3 : ℕ) : ℝ) + 1) ^ (2 * K + 1) * (2 / 5 : ℝ) ^ (n / 3) := by
  set q := n / 3 with hq
  have hN : (∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u) ≤
      48 * K * 9 ^ K * (q + 1) ^ (2 * K + 1) * 8 ^ q := by
    calc (∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u)
        ≤ ∑ _u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ K := by
          apply Finset.sum_le_sum
          intro u hu
          rw [Finset.mem_range] at hu
          exact Nat.mul_le_mul_left _ (Nat.pow_le_pow_right (by positivity) hu.le)
      _ = K * (2 * (2 * n + 1) * 2 ^ n * (n * n) ^ K) := by
          rw [Finset.sum_const, Finset.card_range, smul_eq_mul]
      _ ≤ K * (2 * (6 * (q + 1)) * (4 * 8 ^ q) * (9 * ((q + 1) * (q + 1))) ^ K) := by
          have h1 : 2 * n + 1 ≤ 6 * (q + 1) := by omega
          have h2 : 2 ^ n ≤ 4 * 8 ^ q := by
            calc 2 ^ n ≤ 2 ^ (3 * q + 2) := Nat.pow_le_pow_right (by norm_num) (by omega)
              _ = 4 * 8 ^ q := by rw [pow_add, pow_mul]; norm_num; ring
          have h3 : n * n ≤ 9 * ((q + 1) * (q + 1)) := by
            have : n ≤ 3 * (q + 1) := by omega
            nlinarith
          gcongr
      _ = 48 * K * 9 ^ K * (q + 1) ^ (2 * K + 1) * 8 ^ q := by
          rw [mul_pow, show (q + 1) * (q + 1) = (q + 1) ^ 2 by ring, ← pow_mul]
          ring
  have h20 : (20 : ℝ) ^ q ≤ a n := by exact_mod_cast pow_le_a n hn
  have hN' : ((∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u : ℕ) : ℝ) ≤
      48 * K * 9 ^ K * ((q : ℝ) + 1) ^ (2 * K + 1) * 8 ^ q := by exact_mod_cast hN
  calc ((∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u : ℕ) : ℝ) / a n
      ≤ (48 * K * 9 ^ K * ((q : ℝ) + 1) ^ (2 * K + 1) * 8 ^ q) / 20 ^ q := by
        apply div_le_div₀ (by positivity) hN' (by positivity) h20
    _ = 48 * K * 9 ^ K * ((q : ℝ) + 1) ^ (2 * K + 1) * (2 / 5 : ℝ) ^ q := by
        rw [mul_div_assoc, ← div_pow]
        norm_num

/-- The tail of the mirror bound. -/
lemma tail_le (n K : ℕ) (hn : 1 ≤ n) :
    ((∑ u ∈ Finset.Icc K n, 2 * a (n - u) : ℕ) : ℝ) / a n ≤ 16 * (1 / 2 : ℝ) ^ K := by
  push_cast
  rw [div_eq_mul_inv, Finset.sum_mul]
  calc ∑ u ∈ Finset.Icc K n, 2 * (a (n - u) : ℝ) * (a n : ℝ)⁻¹
      ≤ ∑ u ∈ Finset.Icc K n, 8 * (1 / 2 : ℝ) ^ u := by
        apply Finset.sum_le_sum
        intro u hu
        rw [Finset.mem_Icc] at hu
        have := a_sub_div_le n u hu.2 hn
        rw [div_eq_mul_inv] at this
        rw [mul_assoc]
        linarith
    _ = 8 * (1 / 2 : ℝ) ^ K * ∑ d ∈ Finset.range (n + 1 - K), (1 / 2 : ℝ) ^ d := by
        rw [Finset.mul_sum, ← Finset.Ico_add_one_right_eq_Icc, Finset.sum_Ico_eq_sum_range]
        apply Finset.sum_congr rfl
        intro d _
        rw [pow_add]
        ring
    _ ≤ 8 * (1 / 2 : ℝ) ^ K * 2 := by
        gcongr
        exact sum_geometric_two_le _
    _ = 16 * (1 / 2 : ℝ) ^ K := by ring

/-- The mirror bound's shape gives a null ratio. -/
theorem tendsto_ratio_zero {f : ℕ → ℕ}
    (hf : ∀ n K, K ≤ n →
      f n ≤ (∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u) +
        ∑ u ∈ Finset.Icc K n, 2 * a (n - u)) :
    Tendsto (fun n => (f n : ℝ) / a n) atTop (𝓝 0) := by
  refine tendsto_zero_of_eventually_le (fun n => by positivity)
    (fun K n =>
      48 * K * 9 ^ K * (((n / 3 : ℕ) : ℝ) + 1) ^ (2 * K + 1) * (2 / 5 : ℝ) ^ (n / 3))
    (fun K => 16 * (1 / 2 : ℝ) ^ K) ?_ ?_ ?_
  · intro K
    have h := ((tendsto_succ_pow_mul_pow (2 * K + 1) (r := 2 / 5) (by norm_num)
      (by norm_num)).const_mul (48 * (K : ℝ) * 9 ^ K)).comp
      (Nat.tendsto_div_const_atTop (n := 3) (by norm_num))
    rw [mul_zero] at h
    refine h.congr fun n => ?_
    simp only [Function.comp]
    ring
  · have h := (tendsto_pow_atTop_nhds_zero_of_lt_one (r := (1 / 2 : ℝ)) (by norm_num)
      (by norm_num)).const_mul 16
    rwa [mul_zero] at h
  · intro K
    rw [Filter.eventually_atTop]
    refine ⟨max K 1, fun n hn => ?_⟩
    have hK : K ≤ n := le_of_max_le_left hn
    have hn1 : 1 ≤ n := le_of_max_le_right hn
    have h := hf n K hK
    have ha : (0 : ℝ) < a n := by exact_mod_cast one_le_a hn1
    calc (f n : ℝ) / a n
        ≤ (((∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u) +
            ∑ u ∈ Finset.Icc K n, 2 * a (n - u) : ℕ) : ℝ) / a n := by
          gcongr
      _ = ((∑ u ∈ Finset.range K, 2 * (2 * n + 1) * 2 ^ n * (n * n) ^ u : ℕ) : ℝ) / a n +
            ((∑ u ∈ Finset.Icc K n, 2 * a (n - u) : ℕ) : ℝ) / a n := by
          rw [Nat.cast_add, add_div]
      _ ≤ _ := add_le_add (head_le n K hn1) (tail_le n K hn1)

theorem tendsto_Hm : Tendsto (fun n => (Hm n : ℝ) / a n) atTop (𝓝 0) :=
  tendsto_ratio_zero fun n K hK => AxisMirror.Hm_le n K hK

theorem tendsto_Dm : Tendsto (fun n => (Dm n : ℝ) / a n) atTop (𝓝 0) :=
  tendsto_ratio_zero fun n K hK => DiagMirror.Dm_le n K hK

theorem tendsto_R180 : Tendsto (fun n => (R180 n : ℝ) / a n) atTop (𝓝 0) := by
  have hg : Tendsto
      (fun n : ℕ => 256 * ((((n / 2 : ℕ) : ℝ) + 1) ^ 2 * (1 / 2 : ℝ) ^ (n / 2)))
      atTop (𝓝 0) := by
    have h := ((tendsto_succ_pow_mul_pow 2 (r := 1 / 2) (by norm_num) (by norm_num)).const_mul
      256).comp (Nat.tendsto_div_const_atTop (n := 2) (by norm_num))
    rwa [mul_zero] at h
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le' tendsto_const_nhds hg
    (Filter.Eventually.of_forall fun n => by positivity) ?_
  rw [Filter.eventually_atTop]
  refine ⟨2, fun n hn => ?_⟩
  set p := n / 2 with hp
  have hp1 : 1 ≤ p := by omega
  have ha : (0 : ℝ) < a n := by exact_mod_cast one_le_a (by omega : 1 ≤ n)
  have hap : (0 : ℝ) < a p := by exact_mod_cast one_le_a hp1
  have h1 : a ((n + 1) / 2) * a p ≤ a n := by
    have := a_supermul (m := (n + 1) / 2) (n := p)
    rwa [show (n + 1) / 2 + p = n by omega] at this
  have h1' : (a ((n + 1) / 2) : ℝ) * a p ≤ a n := by exact_mod_cast h1
  have h2 : (2 : ℝ) ^ p ≤ 4 * a p := by exact_mod_cast two_pow_le_four_mul_a p hp1
  have h3 : (R180 n : ℝ) ≤ a ((n + 1) / 2) * ((4 * n + 1) * (4 * n + 1)) := by
    exact_mod_cast HalfTurn.R180_le n
  have h4 : (4 * (n : ℝ) + 1) ≤ 8 * ((p : ℝ) + 1) := by
    have : n ≤ 2 * p + 1 := by omega
    have : (n : ℝ) ≤ 2 * p + 1 := by exact_mod_cast this
    linarith
  rw [div_le_iff₀ ha]
  -- R180 n ≤ a((n+1)/2) (4n+1)² ≤ a((n+1)/2) · 64 (p+1)² ≤ 64 (p+1)² a n / a p
  --   ≤ 256 (p+1)² a n / 2^p
  have h5 : (R180 n : ℝ) * 2 ^ p ≤ 256 * ((p : ℝ) + 1) ^ 2 * a n := by
    have h6 : (R180 n : ℝ) ≤ a ((n + 1) / 2) * (64 * ((p : ℝ) + 1) ^ 2) := by
      refine h3.trans (mul_le_mul_of_nonneg_left ?_ (Nat.cast_nonneg _))
      have := mul_le_mul h4 h4 (by positivity) (by positivity)
      nlinarith
    have h7 : (a ((n + 1) / 2) : ℝ) * 2 ^ p ≤ 4 * a n := by nlinarith
    nlinarith [sq_nonneg ((p : ℝ) + 1), (Nat.cast_nonneg (R180 n) : (0 : ℝ) ≤ R180 n)]
  rw [one_div_pow]
  have h8 : (0 : ℝ) < 2 ^ p := by positivity
  calc (R180 n : ℝ) = (R180 n : ℝ) * 2 ^ p / 2 ^ p := by field_simp
    _ ≤ 256 * ((p : ℝ) + 1) ^ 2 * a n / 2 ^ p := by gcongr
    _ = 256 * (((p : ℝ) + 1) ^ 2 * (1 / 2 ^ p)) * a n := by ring

theorem tendsto_R90 : Tendsto (fun n => (R90 n : ℝ) / a n) atTop (𝓝 0) := by
  refine tendsto_of_tendsto_of_tendsto_of_le_of_le tendsto_const_nhds tendsto_R180
    (fun n => by positivity) fun n => ?_
  have : (R90 n : ℝ) ≤ R180 n := by exact_mod_cast R90_le_R180 n
  gcongr

/-- **One-sided polyplets approach `a(n)/4`, free polyplets `a(n)/8`.** -/
theorem symmetryRatio :
    Tendsto (fun n => 4 * (OneSided n : ℝ) / a n) atTop (𝓝 1) ∧
    Tendsto (fun n => 8 * (Free n : ℝ) / a n) atTop (𝓝 1) := by
  have h1 := tendsto_R90
  have h2 := tendsto_R180
  have h3 := tendsto_Hm
  have h4 := tendsto_Dm
  constructor
  · have h : Tendsto (fun n => 1 + 2 * ((R90 n : ℝ) / a n) + (R180 n : ℝ) / a n) atTop
        (𝓝 (1 + 2 * 0 + 0)) := (tendsto_const_nhds.add (h1.const_mul 2)).add h2
    rw [show (1 : ℝ) + 2 * 0 + 0 = 1 by ring] at h
    refine h.congr' ?_
    filter_upwards [eventually_ge_atTop 1] with n hn
    have ha : (a n : ℝ) ≠ 0 := by exact_mod_cast Nat.one_le_iff_ne_zero.1 (one_le_a hn)
    have e : (4 * OneSided n : ℝ) = a n + 2 * R90 n + R180 n := by
      exact_mod_cast four_mul_OneSided n
    rw [e]
    field_simp
  · have h : Tendsto (fun n => 1 + 2 * ((R90 n : ℝ) / a n) + (R180 n : ℝ) / a n +
        2 * ((Hm n : ℝ) / a n) + 2 * ((Dm n : ℝ) / a n)) atTop
        (𝓝 (1 + 2 * 0 + 0 + 2 * 0 + 2 * 0)) :=
      (((tendsto_const_nhds.add (h1.const_mul 2)).add h2).add (h3.const_mul 2)).add
        (h4.const_mul 2)
    rw [show (1 : ℝ) + 2 * 0 + 0 + 2 * 0 + 2 * 0 = 1 by ring] at h
    refine h.congr' ?_
    filter_upwards [eventually_ge_atTop 1] with n hn
    have ha : (a n : ℝ) ≠ 0 := by exact_mod_cast Nat.one_le_iff_ne_zero.1 (one_le_a hn)
    have e : (8 * Free n : ℝ) = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n := by
      exact_mod_cast eight_mul_Free n
    rw [e]
    field_simp

end Polyplets
