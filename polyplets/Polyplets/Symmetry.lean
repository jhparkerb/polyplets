/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Sequence

/-!
# The eightfold count: Burnside identities for polyplets

`Sequence.lean` counts *fixed* polyplets — `a n`, the canonical animals of
`n` cells taken up to translation only. The paper's §7 companion sequences take
the further quotient by the eight symmetries of the square, and every one of
them is a Burnside average of fixed-point counts. This file builds that
apparatus.

The group is `D4`, a hand-rolled eight-element inductive with an explicit
multiplication table (all group laws by `decide`), together with its linear
action `D4.toFun` on `ℤ × ℤ`. Acting on *canonical* animals needs a
re-anchoring step, because a rotated canonical animal is generally no longer
origin-anchored:

* `Anchored S` : `min x = min y = 0` (the four anchoring clauses of
  `IsCanonicalAnimal`, isolated),
* `anchorVec S` : the lower-left corner of `S`'s bounding box,
* `reanchor S = S.image (· - anchorVec S)` : the canonical translate.

`reanchor` kills translations (`reanchor_image_add`) and fixes anchored sets
(`reanchor_eq_self`), which is exactly what the two `MulAction` laws need, so
`g • S = reanchor (S.image g.toFun)` is an action of `D4` on
`CA n = {S | IsCanonicalAnimal n S}`.

## Results

With `fixCount n g = #(fixed points of g)` and the rotation subgroup realized
as a second small group `C4` acting through `C4.hom : C4 →* D4`:

* `free_eq` : `8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n`
* `oneSided_eq` : `4 * OneSided n = a n + 2 * R90 n + R180 n`
* `bilateral_eq` : `2 * Bilateral n = Hm n + Dm n`
* `r90_vanish` : `R90 n = 0` unless `n % 4 ∈ {0, 1}`

The first two are Mathlib's Burnside lemma
(`MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group`) over `D4` resp.
`C4`, after collapsing the eight fixed-point counts by
`fixCount_inv` (`fixedBy g = fixedBy g⁻¹`, which pairs `r1` with `r3`) and
`fixCount_conj` (conjugation, which pairs the mirror `v` with `h` and `ad`
with `d`).

`bilateral_eq` counts the pairs `(g, x)` with `g` a reflection fixing `x` in
two ways. Summed over reflections it is `2 * Hm n + 2 * Dm n`; summed over
points it is `∑_{x achiral} #(reflections in the stabilizer of x)`, and
`card_stab_eq_two_mul` shows a stabilizer containing a reflection is half
reflections (translate by a fixed reflection), so this is
`½ ∑_{x achiral} #(stabilizer of x)` — which Burnside, applied to the
`D4`-invariant set of achiral animals, evaluates as `½ · 8 · Bilateral n`.

`r90_vanish` is elementary and centre-free. A quarter-turn-fixed `S` satisfies
`S.image σ = S` for the affine map `σ p = ρ p + t` (`ρ` the quarter turn, `t`
the re-anchoring translation). Since `ρ² = -1`, one has `σ⁴ = id`, and a point
fixed by `σ²` is already fixed by `σ` (`2 p` is pinned by `t`, and so is
`2 σ p`). So off the at-most-one `σ`-fixed point (`(1 - ρ)` is injective) the
`σ`-orbits all have exactly four elements: `card_div_four` peels them off one
at a time, leaving `n % 4 ∈ {0, 1}`.

## Anchors

`fixCountC` is the computable twin (filter the `box n n` enumeration of
`Compute.lean` by canonicality and `g`-fixedness), and `fixCountC_eq` transports
it. The anchors run to `n = 5` and match `results/sym_counts.txt`:
`r90 = 1, 0, 0, 2, 2`; `r180 = 1, 4, 4, 22, 22`;
`hmirror = dmirror = 1, 2, 4, 10, 22`. The `n = 6` row — where `hmirror = 58`
first parts company with `dmirror = 56`, so that it is the first row telling
the two mirror conventions apart — needs the `C(36,6) ≈ 1.9M`-subset
enumeration that `Sequence.lean`'s `a 6` note prices at ~700 s per group
element, so it is out of this module's budget; it was confirmed by an
independent brute force over the same `n × n` box (2026-07-30, all four
columns `n = 1 … 6` reproducing `results/sym_counts.txt` exactly, including the
`58` / `56` split). Nothing here depends on which mirror is which: `free_eq`
and `bilateral_eq` are symmetric in `Hm` and `Dm`, and the two definitions
`D4.h` (negate `y`) and `D4.d` (swap) are explicit. Derived spot checks
`Free 4 = 22`, `OneSided 4 = 34`, `Bilateral 4 = 10` close the loop against
A030222/A030233/A030234.
-/

namespace Polyplets

open scoped BigOperators

/-! ## The dihedral group of the square -/

/-- The eight symmetries of the square: the identity, the three rotations
`r1, r2, r3` (quarter turns counterclockwise), the two axis-parallel mirrors
`h` (negate `y`) and `v` (negate `x`), and the two diagonal mirrors `d` (swap)
and `ad` (swap and negate). -/
inductive D4 : Type
  | e | r1 | r2 | r3 | h | v | d | ad
  deriving DecidableEq, Fintype

namespace D4

/-- Composition table of `D4`, written so that `mul g g'` is "`g` after `g'`"
(matching `toFun_mul`). -/
def mul : D4 → D4 → D4
  | e, e => e   | e, r1 => r1 | e, r2 => r2 | e, r3 => r3
  | e, h => h   | e, v => v   | e, d => d   | e, ad => ad
  | r1, e => r1 | r1, r1 => r2 | r1, r2 => r3 | r1, r3 => e
  | r1, h => d  | r1, v => ad | r1, d => v  | r1, ad => h
  | r2, e => r2 | r2, r1 => r3 | r2, r2 => e  | r2, r3 => r1
  | r2, h => v  | r2, v => h  | r2, d => ad | r2, ad => d
  | r3, e => r3 | r3, r1 => e  | r3, r2 => r1 | r3, r3 => r2
  | r3, h => ad | r3, v => d  | r3, d => h  | r3, ad => v
  | h, e => h   | h, r1 => ad | h, r2 => v  | h, r3 => d
  | h, h => e   | h, v => r2  | h, d => r3  | h, ad => r1
  | v, e => v   | v, r1 => d  | v, r2 => h  | v, r3 => ad
  | v, h => r2  | v, v => e   | v, d => r1  | v, ad => r3
  | d, e => d   | d, r1 => h  | d, r2 => ad | d, r3 => v
  | d, h => r1  | d, v => r3  | d, d => e   | d, ad => r2
  | ad, e => ad | ad, r1 => v | ad, r2 => d | ad, r3 => h
  | ad, h => r3 | ad, v => r1 | ad, d => r2 | ad, ad => e

/-- Inversion in `D4`: everything but the two quarter turns is an involution. -/
def inv : D4 → D4
  | e => e | r1 => r3 | r2 => r2 | r3 => r1
  | h => h | v => v | d => d | ad => ad

instance instMul : Mul D4 := ⟨mul⟩
instance instOne : One D4 := ⟨e⟩
instance instInv : Inv D4 := ⟨inv⟩

instance instGroup : Group D4 :=
  Group.ofLeftAxioms (by decide) (by decide) (by decide)

lemma mul_def (g g' : D4) : g * g' = mul g g' := rfl

/-- The action of `D4` on the integer plane, by the eight linear maps of the
square lattice. -/
def toFun : D4 → ℤ × ℤ → ℤ × ℤ
  | e,  p => (p.1, p.2)
  | r1, p => (-p.2, p.1)
  | r2, p => (-p.1, -p.2)
  | r3, p => (p.2, -p.1)
  | h,  p => (p.1, -p.2)
  | v,  p => (-p.1, p.2)
  | d,  p => (p.2, p.1)
  | ad, p => (-p.2, -p.1)

@[simp] lemma toFun_one (p : ℤ × ℤ) : toFun 1 p = p := rfl

lemma toFun_mul (g g' : D4) (p : ℤ × ℤ) : toFun (g * g') p = toFun g (toFun g' p) := by
  rw [mul_def]
  cases g <;> cases g' <;> simp [toFun, mul]

/-- Every element of `D4` acts by an additive map, which is what makes
re-anchoring commute with the action. -/
lemma toFun_add (g : D4) (p q : ℤ × ℤ) : toFun g (p + q) = toFun g p + toFun g q := by
  cases g <;> refine Prod.ext ?_ ?_ <;> simp [toFun] <;> ring

lemma toFun_injective (g : D4) : Function.Injective (toFun g) := by
  intro p q hpq
  cases g <;> · simp only [toFun, Prod.mk.injEq] at hpq; exact Prod.ext (by omega) (by omega)

/-- The king relation is `D4`-invariant: `|Δx|, |Δy| ≤ 1` is symmetric under
swapping and negating coordinates. -/
lemma toFun_kingAdj (g : D4) {p q : ℤ × ℤ} (hpq : kingAdj p q) :
    kingAdj (toFun g p) (toFun g q) := by
  obtain ⟨hne, h1, h2⟩ := hpq
  rw [abs_le] at h1 h2
  refine ⟨fun hc => hne (toFun_injective g hc), ?_, ?_⟩ <;>
    cases g <;> simp only [toFun, abs_le] <;> omega

/-- The four reflections. -/
def refls : Finset D4 := {h, v, d, ad}

end D4

/-! ## Translations and re-anchoring -/

/-- Translation by `t` preserves king adjacency. -/
lemma kingAdj_add {p q : ℤ × ℤ} (t : ℤ × ℤ) (hpq : kingAdj p q) :
    kingAdj (p + t) (q + t) := by
  obtain ⟨hne, h1, h2⟩ := hpq
  refine ⟨fun hc => hne (by simpa using hc), ?_, ?_⟩ <;> simpa using ‹_›

/-- King paths transport along any adjacency-preserving map. -/
lemma reflTransGen_image {f : ℤ × ℤ → ℤ × ℤ} (hadj : ∀ p q, kingAdj p q → kingAdj (f p) (f q))
    {S : Finset (ℤ × ℤ)} {a b : ℤ × ℤ}
    (hab : Relation.ReflTransGen (fun x y => x ∈ S ∧ y ∈ S ∧ kingAdj x y) a b) :
    Relation.ReflTransGen
      (fun x y => x ∈ S.image f ∧ y ∈ S.image f ∧ kingAdj x y) (f a) (f b) := by
  induction hab with
  | refl => exact Relation.ReflTransGen.refl
  | @tail c c' _ hcc' ih =>
      exact ih.tail ⟨Finset.mem_image_of_mem f hcc'.1,
        Finset.mem_image_of_mem f hcc'.2.1, hadj _ _ hcc'.2.2⟩

/-- King-connectivity is preserved by any adjacency-preserving map. -/
lemma kingConnected_image {f : ℤ × ℤ → ℤ × ℤ}
    (hadj : ∀ p q, kingAdj p q → kingAdj (f p) (f q))
    {S : Finset (ℤ × ℤ)} (hS : KingConnected S) : KingConnected (S.image f) := by
  intro p hp q hq
  simp only [Finset.mem_image] at hp hq
  obtain ⟨a, haS, rfl⟩ := hp
  obtain ⟨b, hbS, rfl⟩ := hq
  exact reflTransGen_image hadj (hS a haS b hbS)

/-- `S` is origin-anchored: its bounding box has lower-left corner at the
origin. These are exactly the four anchoring clauses of `IsCanonicalAnimal`. -/
def Anchored (S : Finset (ℤ × ℤ)) : Prop :=
  (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧ (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0)

/-- `IsCanonicalAnimal` is "`n` cells, king-connected, anchored". -/
lemma isCanonicalAnimal_iff (n : ℕ) (S : Finset (ℤ × ℤ)) :
    IsCanonicalAnimal n S ↔ S.card = n ∧ KingConnected S ∧ Anchored S := Iff.rfl

lemma Anchored.nonempty {S : Finset (ℤ × ℤ)} (hS : Anchored S) : S.Nonempty := by
  obtain ⟨p, hp, -⟩ := hS.2.1
  exact ⟨p, hp⟩

lemma IsCanonicalAnimal.nonempty {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    S.Nonempty := Anchored.nonempty hS.2.2

/-- The lower-left corner of `S`'s bounding box (junk value `0` when `S` is
empty). -/
def anchorVec (S : Finset (ℤ × ℤ)) : ℤ × ℤ :=
  if h : S.Nonempty then (S.inf' h Prod.fst, S.inf' h Prod.snd) else (0, 0)

/-- The canonical translate of `S`: slide its bounding box to the origin. -/
def reanchor (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := S.image (fun p => p - anchorVec S)

/-- A coordinate whose values shift by a constant under a translation has its
minimum shifted by that same constant. -/
lemma inf'_image_add {S : Finset (ℤ × ℤ)} (h : S.Nonempty) (t : ℤ × ℤ)
    (hi : (S.image (fun p => p + t)).Nonempty) (f : ℤ × ℤ → ℤ) (c : ℤ)
    (hf : ∀ p, f (p + t) = f p + c) :
    (S.image (fun p => p + t)).inf' hi f = S.inf' h f + c := by
  obtain ⟨a, ha, hae⟩ := Finset.exists_mem_eq_inf' h f
  refine le_antisymm ?_ ?_
  · have hmem : a + t ∈ S.image (fun p => p + t) := Finset.mem_image_of_mem _ ha
    have hle : (S.image (fun p => p + t)).inf' hi f ≤ f (a + t) := Finset.inf'_le f hmem
    rw [hf a] at hle
    omega
  · refine Finset.le_inf' _ _ ?_
    rintro b hb
    simp only [Finset.mem_image] at hb
    obtain ⟨c', hc', rfl⟩ := hb
    have hle : S.inf' h f ≤ f c' := Finset.inf'_le f hc'
    rw [hf c']
    omega

lemma anchorVec_image_add {S : Finset (ℤ × ℤ)} (h : S.Nonempty) (t : ℤ × ℤ) :
    anchorVec (S.image (fun p => p + t)) = anchorVec S + t := by
  have hi : (S.image (fun p => p + t)).Nonempty := h.image _
  rw [anchorVec, anchorVec, dif_pos h, dif_pos hi]
  rw [inf'_image_add h t hi Prod.fst t.1 (fun p => rfl),
    inf'_image_add h t hi Prod.snd t.2 (fun p => rfl)]
  rfl

/-- **Re-anchoring kills translations.** -/
lemma reanchor_image_add (S : Finset (ℤ × ℤ)) (t : ℤ × ℤ) :
    reanchor (S.image (fun p => p + t)) = reanchor S := by
  rcases S.eq_empty_or_nonempty with rfl | h
  · simp [reanchor]
  · rw [reanchor, reanchor, anchorVec_image_add h t, Finset.image_image]
    exact Finset.image_congr fun p _ => by simp only [Function.comp_apply]; abel

/-- An anchored set has its bounding-box corner at the origin. -/
lemma anchorVec_eq_zero {S : Finset (ℤ × ℤ)} (hS : Anchored S) : anchorVec S = 0 := by
  obtain ⟨p, hpS, hp⟩ := hS.2.1
  obtain ⟨q, hqS, hq⟩ := hS.2.2.2
  have h : S.Nonempty := hS.nonempty
  have h1 : S.inf' h Prod.fst ≤ p.1 := Finset.inf'_le Prod.fst hpS
  have h2 : S.inf' h Prod.snd ≤ q.2 := Finset.inf'_le Prod.snd hqS
  rw [anchorVec, dif_pos h]
  refine Prod.ext ?_ ?_
  · refine le_antisymm ?_ ?_
    · rw [hp] at h1; exact h1
    · exact Finset.le_inf' h _ fun b hb => hS.1 b hb
  · refine le_antisymm ?_ ?_
    · rw [hq] at h2; exact h2
    · exact Finset.le_inf' h _ fun b hb => hS.2.2.1 b hb

/-- **Re-anchoring fixes anchored sets.** -/
lemma reanchor_eq_self {S : Finset (ℤ × ℤ)} (hS : Anchored S) : reanchor S = S := by
  rw [reanchor, anchorVec_eq_zero hS]
  simp

/-- The re-anchored set is anchored. -/
lemma reanchor_anchored {S : Finset (ℤ × ℤ)} (h : S.Nonempty) : Anchored (reanchor S) := by
  obtain ⟨a, ha, hae⟩ := Finset.exists_mem_eq_inf' h Prod.fst
  obtain ⟨b, hb, hbe⟩ := Finset.exists_mem_eq_inf' h Prod.snd
  have hv : anchorVec S = (S.inf' h Prod.fst, S.inf' h Prod.snd) := dif_pos h
  refine ⟨?_, ⟨a - anchorVec S, Finset.mem_image_of_mem _ ha, ?_⟩,
    ?_, ⟨b - anchorVec S, Finset.mem_image_of_mem _ hb, ?_⟩⟩
  · rintro p hp
    simp only [reanchor, Finset.mem_image] at hp
    obtain ⟨q, hq, rfl⟩ := hp
    have hle : S.inf' h Prod.fst ≤ q.1 := Finset.inf'_le Prod.fst hq
    simp only [hv, Prod.fst_sub]
    omega
  · simp only [hv, Prod.fst_sub, hae]; omega
  · rintro p hp
    simp only [reanchor, Finset.mem_image] at hp
    obtain ⟨q, hq, rfl⟩ := hp
    have hle : S.inf' h Prod.snd ≤ q.2 := Finset.inf'_le Prod.snd hq
    simp only [hv, Prod.snd_sub]
    omega
  · simp only [hv, Prod.snd_sub, hbe]; omega

lemma reanchor_card (S : Finset (ℤ × ℤ)) : (reanchor S).card = S.card :=
  Finset.card_image_of_injective _ (fun p q hpq => by
    have : p - anchorVec S + anchorVec S = q - anchorVec S + anchorVec S := by rw [hpq]
    simpa using this)

lemma kingConnected_reanchor {S : Finset (ℤ × ℤ)} (hS : KingConnected S) :
    KingConnected (reanchor S) :=
  kingConnected_image (f := fun p => p - anchorVec S)
    (fun p q hpq => by simpa [sub_eq_add_neg] using kingAdj_add (-anchorVec S) hpq) hS

/-! ## The action on canonical animals -/

/-- Canonicality survives "apply a symmetry, then re-anchor". -/
lemma isCanonicalAnimal_reanchor {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S)
    (g : D4) : IsCanonicalAnimal n (reanchor (S.image (D4.toFun g))) := by
  have hne : (S.image (D4.toFun g)).Nonempty := hS.nonempty.image _
  refine ⟨?_, ?_, reanchor_anchored hne⟩
  · rw [reanchor_card, Finset.card_image_of_injective _ (D4.toFun_injective g)]
    exact hS.1
  · exact kingConnected_reanchor (kingConnected_image (fun _ _ => D4.toFun_kingAdj g) hS.2.1)

/-- The canonical animals of `n` cells, as a set. -/
def CA (n : ℕ) : Set (Finset (ℤ × ℤ)) := {S | IsCanonicalAnimal n S}

lemma mem_CA {n : ℕ} {S : Finset (ℤ × ℤ)} : S ∈ CA n ↔ IsCanonicalAnimal n S := Iff.rfl

lemma CA_finite (n : ℕ) : (CA n).Finite := canonicalAnimal_finite n

lemma a_eq_natCard (n : ℕ) : a n = Nat.card (CA n) := (Nat.card_coe_set_eq (CA n)).symm

/-- Images compose along the group law. -/
lemma image_toFun_mul (g g' : D4) (T : Finset (ℤ × ℤ)) :
    T.image (D4.toFun (g * g')) = (T.image (D4.toFun g')).image (D4.toFun g) := by
  rw [Finset.image_image]
  refine Finset.image_congr ?_
  intro p _
  simpa using D4.toFun_mul g g' p

/-- Images of translates are translates of images: the additivity of the action
in the form re-anchoring needs. -/
lemma image_toFun_add (g : D4) (T : Finset (ℤ × ℤ)) (u : ℤ × ℤ) :
    (T.image (fun p => p + u)).image (D4.toFun g)
      = (T.image (D4.toFun g)).image (fun p => p + D4.toFun g u) := by
  rw [Finset.image_image, Finset.image_image]
  refine Finset.image_congr ?_
  intro p _
  simpa using D4.toFun_add g p u

lemma reanchor_eq_image_add (T : Finset (ℤ × ℤ)) :
    reanchor T = T.image (fun p => p + -anchorVec T) := by
  simp only [reanchor, sub_eq_add_neg]

instance instSMulD4CA (n : ℕ) : SMul D4 (CA n) :=
  ⟨fun g S => ⟨reanchor (S.1.image (D4.toFun g)), isCanonicalAnimal_reanchor S.2 g⟩⟩

lemma smul_CA_val {n : ℕ} (g : D4) (S : CA n) :
    (g • S).1 = reanchor (S.1.image (D4.toFun g)) := rfl

instance instMulActionD4CA (n : ℕ) : MulAction D4 (CA n) where
  one_smul S := by
    refine Subtype.ext ?_
    rw [smul_CA_val]
    have hid : S.1.image (D4.toFun 1) = S.1 := by
      rw [show D4.toFun 1 = id from funext fun p => D4.toFun_one p]
      exact Finset.image_id
    rw [hid, reanchor_eq_self S.2.2.2]
  mul_smul g g' S := by
    refine Subtype.ext ?_
    rw [smul_CA_val, smul_CA_val, smul_CA_val,
      image_toFun_mul g g' S.1,
      reanchor_eq_image_add (S.1.image (D4.toFun g')),
      image_toFun_add g (S.1.image (D4.toFun g')) (-anchorVec (S.1.image (D4.toFun g'))),
      reanchor_image_add]

/-! ## Finiteness bridges -/

instance instFiniteCA (n : ℕ) : Finite (CA n) := (CA_finite n).to_subtype

noncomputable instance instFintypeCA (n : ℕ) : Fintype (CA n) := Fintype.ofFinite _

noncomputable instance instFintypeFixedByD4 (n : ℕ) (g : D4) :
    Fintype (MulAction.fixedBy (CA n) g) := Fintype.ofFinite _

noncomputable instance instFintypeOrbitsD4 (n : ℕ) :
    Fintype (MulAction.orbitRel.Quotient D4 (CA n)) := Fintype.ofFinite _

/-! ## The fixed-point counts -/

/-- The number of canonical animals of `n` cells fixed by `g`. -/
noncomputable def fixCount (n : ℕ) (g : D4) : ℕ := Nat.card (MulAction.fixedBy (CA n) g)

/-- Quarter-turn-symmetric animals. -/
noncomputable def R90 (n : ℕ) : ℕ := fixCount n D4.r1

/-- Half-turn-symmetric animals. -/
noncomputable def R180 (n : ℕ) : ℕ := fixCount n D4.r2

/-- Animals symmetric in an axis-parallel mirror (`y ↦ -y`); the `hmirror`
column of `results/sym_counts.txt`. -/
noncomputable def Hm (n : ℕ) : ℕ := fixCount n D4.h

/-- Animals symmetric in a diagonal mirror (swap coordinates); the `dmirror`
column of `results/sym_counts.txt`. -/
noncomputable def Dm (n : ℕ) : ℕ := fixCount n D4.d

/-- Free polyplets: `D4`-orbits of canonical animals (A030222). -/
noncomputable def Free (n : ℕ) : ℕ := Nat.card (MulAction.orbitRel.Quotient D4 (CA n))

lemma fixCount_one (n : ℕ) : fixCount n 1 = a n := by
  rw [fixCount, a_eq_natCard]
  refine Nat.card_congr (Equiv.subtypeUnivEquiv ?_)
  intro x
  simp [MulAction.fixedBy]

/-- `g` and `g⁻¹` have the same fixed points, which is what pairs `r1` with
`r3`. -/
lemma fixCount_inv (n : ℕ) (g : D4) : fixCount n g⁻¹ = fixCount n g := by
  rw [fixCount, fixCount]
  refine Nat.card_congr (Equiv.subtypeEquivRight fun x => ?_)
  simp only [MulAction.fixedBy, Set.mem_setOf_eq]
  constructor
  · intro hx; conv_lhs => rw [← hx]
    rw [smul_smul, mul_inv_cancel, one_smul]
  · intro hx; conv_lhs => rw [← hx]
    rw [smul_smul, inv_mul_cancel, one_smul]

/-- Conjugate elements have equinumerous fixed-point sets; this pairs the
mirror `v` with `h` and `ad` with `d`. -/
lemma fixCount_conj (n : ℕ) (g c : D4) : fixCount n (c * g * c⁻¹) = fixCount n g := by
  rw [fixCount, fixCount]
  refine Nat.card_congr ⟨fun x => ⟨c⁻¹ • x.1, ?_⟩, fun y => ⟨c • y.1, ?_⟩, ?_, ?_⟩
  · have hx := x.2
    simp only [MulAction.fixedBy, Set.mem_setOf_eq] at hx ⊢
    have h1 : g * c⁻¹ = c⁻¹ * (c * g * c⁻¹) := by group
    calc g • c⁻¹ • x.1 = (g * c⁻¹) • x.1 := smul_smul _ _ _
      _ = (c⁻¹ * (c * g * c⁻¹)) • x.1 := by rw [h1]
      _ = c⁻¹ • ((c * g * c⁻¹) • x.1) := (smul_smul _ _ _).symm
      _ = c⁻¹ • x.1 := by rw [hx]
  · have hy := y.2
    simp only [MulAction.fixedBy, Set.mem_setOf_eq] at hy ⊢
    have h2 : c * g * c⁻¹ * c = c * g := by group
    calc (c * g * c⁻¹) • c • y.1 = ((c * g * c⁻¹) * c) • y.1 := smul_smul _ _ _
      _ = (c * g) • y.1 := by rw [h2]
      _ = c • (g • y.1) := (smul_smul _ _ _).symm
      _ = c • y.1 := by rw [hy]
  · intro x; ext; simp
  · intro y; ext; simp

/-- The two quarter turns are inverse, hence equinumerously fixed. -/
lemma fixCount_r3 (n : ℕ) : fixCount n D4.r3 = fixCount n D4.r1 := by
  have h : (D4.r3 : D4) = D4.r1⁻¹ := by decide
  rw [h, fixCount_inv]

/-- The two axis-parallel mirrors are conjugate by a quarter turn. -/
lemma fixCount_v (n : ℕ) : fixCount n D4.v = fixCount n D4.h := by
  have h : (D4.v : D4) = D4.r1 * D4.h * D4.r1⁻¹ := by decide
  rw [h, fixCount_conj]

/-- The two diagonal mirrors are conjugate by a quarter turn. -/
lemma fixCount_ad (n : ℕ) : fixCount n D4.ad = fixCount n D4.d := by
  have h : (D4.ad : D4) = D4.r1 * D4.d * D4.r1⁻¹ := by decide
  rw [h, fixCount_conj]

/-! ## Burnside over the full symmetry group -/

lemma card_fixedBy_eq_fixCount (n : ℕ) (g : D4) :
    Fintype.card (MulAction.fixedBy (CA n) g) = fixCount n g :=
  (Nat.card_eq_fintype_card).symm

/-- Sum over `D4` of a function, unfolded into its eight terms. -/
lemma D4.sum_univ {M : Type*} [AddCommMonoid M] (f : D4 → M) :
    ∑ g : D4, f g = f e + f r1 + f r2 + f r3 + f h + f v + f d + f ad := by
  have : (Finset.univ : Finset D4) = {e, r1, r2, r3, h, v, d, ad} := by decide
  rw [this]
  simp only [Finset.sum_insert, Finset.mem_insert, Finset.mem_singleton, Finset.sum_singleton,
    reduceCtorEq, or_self, not_false_eq_true]
  abel

/-- **Burnside's lemma for `D4`.** -/
theorem free_eq (n : ℕ) (_hn : 1 ≤ n) :
    8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n := by
  have hb := MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group D4 (CA n)
  rw [D4.sum_univ (fun g => Fintype.card (MulAction.fixedBy (CA n) g))] at hb
  simp only [card_fixedBy_eq_fixCount] at hb
  rw [show (D4.e : D4) = 1 from rfl, fixCount_one, fixCount_r3, fixCount_v, fixCount_ad] at hb
  have hcard : Fintype.card D4 = 8 := by decide
  have hfree : Fintype.card (MulAction.orbitRel.Quotient D4 (CA n)) = Free n :=
    (Nat.card_eq_fintype_card).symm
  rw [hcard, hfree] at hb
  simp only [R90, R180, Hm, Dm]
  omega

/-! ## Burnside over the rotation subgroup -/

/-- The cyclic group of order four, acting on canonical animals through the
rotations of `D4`. Realizing the rotation subgroup as a group in its own right
(rather than as a `Subgroup D4`) keeps the four-term Burnside sum concrete. -/
inductive C4 : Type
  | c0 | c1 | c2 | c3
  deriving DecidableEq, Fintype

namespace C4

/-- Addition table of `ℤ/4`, written multiplicatively. -/
def mul : C4 → C4 → C4
  | c0, c0 => c0 | c0, c1 => c1 | c0, c2 => c2 | c0, c3 => c3
  | c1, c0 => c1 | c1, c1 => c2 | c1, c2 => c3 | c1, c3 => c0
  | c2, c0 => c2 | c2, c1 => c3 | c2, c2 => c0 | c2, c3 => c1
  | c3, c0 => c3 | c3, c1 => c0 | c3, c2 => c1 | c3, c3 => c2

/-- Negation in `ℤ/4`, written multiplicatively. -/
def inv : C4 → C4
  | c0 => c0 | c1 => c3 | c2 => c2 | c3 => c1

instance instMul : Mul C4 := ⟨mul⟩
instance instOne : One C4 := ⟨c0⟩
instance instInv : Inv C4 := ⟨inv⟩

instance instGroup : Group C4 :=
  Group.ofLeftAxioms (by decide) (by decide) (by decide)

/-- The rotation embedding. -/
def toD4 : C4 → D4
  | c0 => D4.e | c1 => D4.r1 | c2 => D4.r2 | c3 => D4.r3

/-- `C4` as a subgroup of `D4`, bundled. -/
def hom : C4 →* D4 where
  toFun := toD4
  map_one' := rfl
  map_mul' := by decide

lemma sum_univ {M : Type*} [AddCommMonoid M] (f : C4 → M) :
    ∑ c : C4, f c = f c0 + f c1 + f c2 + f c3 := by
  have h : (Finset.univ : Finset C4) = {c0, c1, c2, c3} := by decide
  rw [h]
  simp only [Finset.sum_insert, Finset.mem_insert, Finset.mem_singleton, Finset.sum_singleton,
    reduceCtorEq, or_self, not_false_eq_true]
  abel

end C4

instance instMulActionC4CA (n : ℕ) : MulAction C4 (CA n) := MulAction.compHom _ C4.hom

noncomputable instance instFintypeFixedByC4 (n : ℕ) (c : C4) :
    Fintype (MulAction.fixedBy (CA n) c) := Fintype.ofFinite _

noncomputable instance instFintypeOrbitsC4 (n : ℕ) :
    Fintype (MulAction.orbitRel.Quotient C4 (CA n)) := Fintype.ofFinite _

/-- One-sided polyplets: rotation-orbits of canonical animals (A030233). -/
noncomputable def OneSided (n : ℕ) : ℕ := Nat.card (MulAction.orbitRel.Quotient C4 (CA n))

lemma card_fixedByC4 (n : ℕ) (c : C4) :
    Fintype.card (MulAction.fixedBy (CA n) c) = fixCount n (C4.toD4 c) := by
  rw [fixCount, Nat.card_eq_fintype_card]
  exact Fintype.card_congr' rfl

/-- **Burnside's lemma for the rotation subgroup.** -/
theorem oneSided_eq (n : ℕ) (_hn : 1 ≤ n) :
    4 * OneSided n = a n + 2 * R90 n + R180 n := by
  have hb := MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group C4 (CA n)
  rw [C4.sum_univ (fun c => Fintype.card (MulAction.fixedBy (CA n) c))] at hb
  simp only [card_fixedByC4, C4.toD4] at hb
  rw [show (D4.e : D4) = 1 from rfl, fixCount_one, fixCount_r3] at hb
  have hcard : Fintype.card C4 = 4 := by decide
  have hone : Fintype.card (MulAction.orbitRel.Quotient C4 (CA n)) = OneSided n :=
    (Nat.card_eq_fintype_card).symm
  rw [hcard, hone] at hb
  simp only [R90, R180]
  omega

/-! ## Quarter-turn symmetry forces `n ≡ 0, 1 (mod 4)` -/

/-- **Free order-four orbits have four elements.** A finite set carried into
itself by an injective `σ` with `σ⁴ = id` and no `σ`- or `σ²`-fixed points has
cardinality divisible by four: peel off one four-element orbit at a time. -/
lemma card_div_four {σ : ℤ × ℤ → ℤ × ℤ} (hinj : Function.Injective σ)
    (h4 : ∀ p, σ (σ (σ (σ p))) = p) :
    ∀ (m : ℕ) (T : Finset (ℤ × ℤ)), T.card = m → (∀ p ∈ T, σ p ∈ T) →
      (∀ p ∈ T, σ p ≠ p) → (∀ p ∈ T, σ (σ p) ≠ p) → 4 ∣ m := by
  intro m
  induction m using Nat.strong_induction_on with
  | _ m ih =>
    intro T hcard hmap hfix hfix2
    rcases T.eq_empty_or_nonempty with rfl | ⟨p, hp⟩
    · simp only [Finset.card_empty] at hcard; omega
    · have hp1 : σ p ≠ p := hfix p hp
      have hp2 : σ (σ p) ≠ p := hfix2 p hp
      have hp3 : σ (σ (σ p)) ≠ p := by
        intro hc
        have := congrArg σ hc
        rw [h4 p] at this
        exact hp1 this.symm
      have h12 : σ p ≠ σ (σ p) := fun hc => hp1 (hinj hc).symm
      have h13 : σ p ≠ σ (σ (σ p)) := fun hc => hp2 (hinj hc).symm
      have h23 : σ (σ p) ≠ σ (σ (σ p)) := fun hc => h12 (hinj hc)
      set O : Finset (ℤ × ℤ) := {p, σ p, σ (σ p), σ (σ (σ p))} with hOdef
      have hpT1 : σ p ∈ T := hmap p hp
      have hpT2 : σ (σ p) ∈ T := hmap _ hpT1
      have hpT3 : σ (σ (σ p)) ∈ T := hmap _ hpT2
      have hOT : O ⊆ T := by
        intro q hq
        simp only [hOdef, Finset.mem_insert, Finset.mem_singleton] at hq
        rcases hq with rfl | rfl | rfl | rfl <;> assumption
      have hOcard : O.card = 4 := by
        rw [hOdef]
        rw [Finset.card_insert_of_notMem (by
              simp only [Finset.mem_insert, Finset.mem_singleton]
              push Not
              exact ⟨Ne.symm hp1, Ne.symm hp2, Ne.symm hp3⟩),
          Finset.card_insert_of_notMem (by
              simp only [Finset.mem_insert, Finset.mem_singleton]
              push Not
              exact ⟨h12, h13⟩),
          Finset.card_insert_of_notMem (by
              simp only [Finset.mem_singleton]
              exact h23),
          Finset.card_singleton]
      have hge : 4 ≤ m := by
        rw [← hcard, ← hOcard]
        exact Finset.card_le_card hOT
      have hsub : (T \ O).card = m - 4 := by
        have := Finset.card_sdiff_add_card_eq_card hOT
        rw [hcard, hOcard] at this
        omega
      have hmap' : ∀ q ∈ T \ O, σ q ∈ T \ O := by
        intro q hq
        rw [Finset.mem_sdiff] at hq ⊢
        refine ⟨hmap q hq.1, ?_⟩
        intro hc
        apply hq.2
        simp only [hOdef, Finset.mem_insert, Finset.mem_singleton] at hc ⊢
        rcases hc with hc | hc | hc | hc
        · right; right; right
          refine hinj ?_
          rw [hc, h4 p]
        · left; exact hinj hc
        · right; left; exact hinj hc
        · right; right; left; exact hinj hc
      have hdvd : 4 ∣ m - 4 :=
        ih (m - 4) (by omega) (T \ O) hsub hmap'
          (fun q hq => hfix q (Finset.mem_sdiff.mp hq).1)
          (fun q hq => hfix2 q (Finset.mem_sdiff.mp hq).1)
      omega

/-- **The arithmetic core of `r90_vanish`.** If the affine quarter turn
`σ p = (-p.2 + A, p.1 + B)` carries `S` onto itself then `|S| ≡ 0` or `1`
mod `4`. -/
lemma quarter_turn_card_mod (n : ℕ) (S : Finset (ℤ × ℤ)) (A B : ℤ)
    (hcard : S.card = n)
    (himg : S.image (fun p : ℤ × ℤ => (-p.2 + A, p.1 + B)) = S) :
    n % 4 = 0 ∨ n % 4 = 1 := by
  set σ : ℤ × ℤ → ℤ × ℤ := fun p => (-p.2 + A, p.1 + B) with hσ
  have hinj : Function.Injective σ := by
    intro x y hxy
    rw [hσ] at hxy
    simp only [Prod.mk.injEq] at hxy
    exact Prod.ext (by omega) (by omega)
  have h4 : ∀ p, σ (σ (σ (σ p))) = p := by
    intro p
    rw [hσ]
    refine Prod.ext ?_ ?_ <;> simp <;> ring
  have hmapS : ∀ p ∈ S, σ p ∈ S := by
    intro p hp
    rw [← himg]
    exact Finset.mem_image_of_mem _ hp
  set F : Finset (ℤ × ℤ) := S.filter (fun p => σ p = p) with hF
  have hFS : F ⊆ S := Finset.filter_subset _ _
  have hF1 : F.card ≤ 1 := by
    rw [Finset.card_le_one]
    intro x hx y hy
    rw [hF, Finset.mem_filter] at hx hy
    have hx2 := hx.2
    have hy2 := hy.2
    rw [hσ] at hx2 hy2
    simp only [Prod.ext_iff] at hx2 hy2
    exact Prod.ext (by omega) (by omega)
  have hmapT : ∀ p ∈ S \ F, σ p ∈ S \ F := by
    intro p hp
    rw [Finset.mem_sdiff] at hp ⊢
    refine ⟨hmapS p hp.1, ?_⟩
    intro hc
    apply hp.2
    rw [hF, Finset.mem_filter] at hc ⊢
    refine ⟨hp.1, ?_⟩
    exact hinj hc.2
  have hfixT : ∀ p ∈ S \ F, σ p ≠ p := by
    intro p hp hc
    rw [Finset.mem_sdiff] at hp
    exact hp.2 (by rw [hF, Finset.mem_filter]; exact ⟨hp.1, hc⟩)
  have hfix2T : ∀ p ∈ S \ F, σ (σ p) ≠ p := by
    intro p hp hc
    rw [Finset.mem_sdiff] at hp
    refine hp.2 ?_
    rw [hF, Finset.mem_filter]
    refine ⟨hp.1, ?_⟩
    rw [hσ] at hc ⊢
    simp only [Prod.ext_iff] at hc ⊢
    omega
  have hdvd : 4 ∣ (S \ F).card :=
    card_div_four hinj h4 (S \ F).card (S \ F) rfl hmapT hfixT hfix2T
  have hsum : (S \ F).card + F.card = S.card := Finset.card_sdiff_add_card_eq_card hFS
  omega

/-- **Quarter-turn symmetry is impossible unless `n ≡ 0, 1 (mod 4)`.** -/
theorem r90_vanish (n : ℕ) (h : ¬ (n % 4 = 0 ∨ n % 4 = 1)) : R90 n = 0 := by
  rw [R90, fixCount]
  have hempty : IsEmpty (MulAction.fixedBy (CA n) D4.r1) := by
    constructor
    rintro ⟨x, hx⟩
    have h1 : reanchor (x.1.image (D4.toFun D4.r1)) = x.1 := congrArg Subtype.val hx
    obtain ⟨v, hveq⟩ : ∃ v : ℤ × ℤ, reanchor (x.1.image (D4.toFun D4.r1))
        = x.1.image (fun p : ℤ × ℤ => (-p.2 + -v.1, p.1 + -v.2)) := by
      refine ⟨anchorVec (x.1.image (D4.toFun D4.r1)), ?_⟩
      rw [reanchor, Finset.image_image]
      refine Finset.image_congr ?_
      intro p _
      simp only [Function.comp_apply, D4.toFun]
      refine Prod.ext ?_ ?_ <;> simp [sub_eq_add_neg]
    rw [hveq] at h1
    exact h (quarter_turn_card_mod n x.1 (-v.1) (-v.2) x.2.1 h1)
  exact Nat.card_of_isEmpty

/-! ## Achiral animals and the bilateral count -/

/-- Reflections stay reflections under conjugation. -/
lemma D4.conj_refls : ∀ c g : D4, g ∈ D4.refls → c * g * c⁻¹ ∈ D4.refls := by decide

/-- A reflection times a rotation is a reflection. -/
lemma D4.refl_mul_not_refl : ∀ a b : D4, a ∈ D4.refls → b ∉ D4.refls → a * b ∈ D4.refls := by
  decide

/-- A reflection times a reflection is a rotation. -/
lemma D4.inv_refl_mul_refl : ∀ a b : D4, a ∈ D4.refls → b ∈ D4.refls → a⁻¹ * b ∉ D4.refls := by
  decide

/-- The `D4`-invariant set of canonical animals fixed by at least one
reflection: the *achiral* animals. -/
def achiral (n : ℕ) : SubMulAction D4 (CA n) where
  carrier := {x | ∃ g ∈ D4.refls, g • x = x}
  smul_mem' := by
    rintro c x ⟨g, hg, hgx⟩
    refine ⟨c * g * c⁻¹, D4.conj_refls c g hg, ?_⟩
    have hrw : c * g * c⁻¹ * c = c * g := by group
    calc (c * g * c⁻¹) • c • x = (c * g * c⁻¹ * c) • x := smul_smul _ _ _
      _ = (c * g) • x := by rw [hrw]
      _ = c • (g • x) := (smul_smul _ _ _).symm
      _ = c • x := by rw [hgx]

noncomputable instance instFintypeAchiral (n : ℕ) : Fintype (achiral n) := Fintype.ofFinite _

noncomputable instance instFintypeFixedByAchiral (n : ℕ) (g : D4) :
    Fintype (MulAction.fixedBy (achiral n) g) := Fintype.ofFinite _

noncomputable instance instFintypeOrbitsAchiral (n : ℕ) :
    Fintype (MulAction.orbitRel.Quotient D4 (achiral n)) := Fintype.ofFinite _

/-- Bilateral polyplets: `D4`-orbits of achiral canonical animals (A030234). -/
noncomputable def Bilateral (n : ℕ) : ℕ :=
  Nat.card (MulAction.orbitRel.Quotient D4 (achiral n))

/-- Double counting a relation over two finite index sets. -/
lemma sum_card_filter_comm {α β : Type*}
    (s : Finset α) (t : Finset β) (R : α → β → Prop) [∀ a b, Decidable (R a b)] :
    ∑ a ∈ s, (t.filter (R a)).card = ∑ b ∈ t, (s.filter (fun a => R a b)).card := by
  simp only [Finset.card_filter]
  exact Finset.sum_comm

lemma D4.sum_refls {M : Type*} [AddCommMonoid M] (f : D4 → M) :
    ∑ g ∈ D4.refls, f g = f h + f v + f d + f ad := by
  rw [D4.refls]
  simp only [Finset.sum_insert, Finset.mem_insert, Finset.mem_singleton, Finset.sum_singleton,
    reduceCtorEq, or_self, not_false_eq_true]
  abel

lemma smul_achiral_iff {n : ℕ} (g : D4) (y : achiral n) :
    g • y = y ↔ g • (y : CA n) = (y : CA n) := by
  constructor
  · intro hy; exact congrArg Subtype.val hy
  · intro hy; exact Subtype.ext hy

/-- A reflection fixes the same animals inside the achiral subset as it does
overall — anything a reflection fixes is achiral by definition. -/
lemma card_fixedBy_achiral_refl (n : ℕ) {g : D4} (hg : g ∈ D4.refls) :
    Nat.card (MulAction.fixedBy (achiral n) g) = fixCount n g := by
  rw [fixCount]
  refine Nat.card_congr ⟨fun y => ⟨(y.1 : CA n), ?_⟩,
    fun x => ⟨⟨x.1, ⟨g, hg, x.2⟩⟩, ?_⟩, ?_, ?_⟩
  · exact (smul_achiral_iff g y.1).mp y.2
  · exact Subtype.ext x.2
  · intro y; rfl
  · intro x; rfl

/-- **Burnside over the achiral animals**, in double-counted form. -/
lemma sum_stab_achiral (n : ℕ) :
    ∑ y : achiral n, (Finset.univ.filter (fun g : D4 => g • y = y)).card
      = Bilateral n * 8 := by
  have hb := MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group D4 (achiral n)
  have hterm : ∀ g : D4, Fintype.card (MulAction.fixedBy (achiral n) g)
      = (Finset.univ.filter (fun y : achiral n => g • y = y)).card := fun g => by
    rw [← Nat.card_eq_fintype_card, ← Nat.card_eq_finsetCard]
    exact Nat.card_congr (Equiv.subtypeEquivRight fun y => by simp)
  simp only [hterm] at hb
  rw [show Fintype.card D4 = 8 from by decide,
    show Fintype.card (MulAction.orbitRel.Quotient D4 (achiral n)) = Bilateral n from
      (Nat.card_eq_fintype_card).symm] at hb
  rw [← hb]
  exact (sum_card_filter_comm Finset.univ Finset.univ
    (fun (g : D4) (y : achiral n) => g • y = y)).symm

/-- The reflection half of the same double count. -/
lemma sum_stab_refl_achiral (n : ℕ) :
    ∑ y : achiral n, (D4.refls.filter (fun g => g • y = y)).card
      = 2 * Hm n + 2 * Dm n := by
  rw [sum_card_filter_comm Finset.univ D4.refls (fun (y : achiral n) (g : D4) => g • y = y)]
  have hterm : ∀ g : D4, (Finset.univ.filter (fun y : achiral n => g • y = y)).card
      = Nat.card (MulAction.fixedBy (achiral n) g) := fun g => by
    rw [← Nat.card_eq_finsetCard]
    exact (Nat.card_congr (Equiv.subtypeEquivRight fun y => by simp)).symm
  simp only [hterm]
  rw [D4.sum_refls (fun g => Nat.card (MulAction.fixedBy (achiral n) g))]
  rw [card_fixedBy_achiral_refl n (by decide : D4.h ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : D4.v ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : D4.d ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : D4.ad ∈ D4.refls),
    fixCount_v, fixCount_ad]
  simp only [Hm, Dm]
  omega

/-- **A stabilizer containing a reflection is exactly half reflections**:
multiplying by a fixed reflection in the stabilizer swaps its rotations and its
reflections. -/
lemma card_stab_eq_two_mul (n : ℕ) (y : achiral n) :
    (Finset.univ.filter (fun g : D4 => g • y = y)).card
      = 2 * (D4.refls.filter (fun g => g • y = y)).card := by
  obtain ⟨g0, hg0refl, hg0⟩ := y.2
  have hg0y : g0 • y = y := (smul_achiral_iff g0 y).mpr hg0
  have hg0inv : g0⁻¹ • y = y := by
    conv_lhs => rw [← hg0y]
    rw [smul_smul, inv_mul_cancel, one_smul]
  have hsplit := Finset.card_filter_add_card_filter_not
    (s := Finset.univ.filter (fun g : D4 => g • y = y)) (p := fun g : D4 => g ∈ D4.refls)
  have hKr : (Finset.univ.filter (fun g : D4 => g • y = y)).filter
      (fun g : D4 => g ∈ D4.refls) = D4.refls.filter (fun g => g • y = y) := by
    ext g
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    exact and_comm
  have hbij : ((Finset.univ.filter (fun g : D4 => g • y = y)).filter
      (fun g : D4 => ¬ g ∈ D4.refls)).image (fun g => g0 * g)
      = D4.refls.filter (fun g => g • y = y) := by
    ext g
    simp only [Finset.mem_image, Finset.mem_filter, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨k, ⟨hk1, hk2⟩, rfl⟩
      refine ⟨?_, ?_⟩
      · exact D4.refl_mul_not_refl _ _ hg0refl hk2
      · rw [← smul_smul, hk1, hg0y]
    · rintro ⟨h1, h2⟩
      refine ⟨g0⁻¹ * g, ⟨?_, ?_⟩, ?_⟩
      · rw [← smul_smul, h2, hg0inv]
      · exact D4.inv_refl_mul_refl _ _ hg0refl h1
      · group
  have hinj : Function.Injective (fun g : D4 => g0 * g) := fun a b hab => by
    have := congrArg (fun z => g0⁻¹ * z) hab
    simpa [← mul_assoc] using this
  have hcardn : ((Finset.univ.filter (fun g : D4 => g • y = y)).filter
      (fun g : D4 => ¬ g ∈ D4.refls)).card = (D4.refls.filter (fun g => g • y = y)).card := by
    rw [← hbij, Finset.card_image_of_injective _ hinj]
  rw [hKr, hcardn] at hsplit
  omega

/-- **The bilateral half-sum.** -/
theorem bilateral_eq (n : ℕ) (_hn : 1 ≤ n) : 2 * Bilateral n = Hm n + Dm n := by
  have h1 := sum_stab_achiral n
  have h2 := sum_stab_refl_achiral n
  have h3 : ∑ y : achiral n, (Finset.univ.filter (fun g : D4 => g • y = y)).card
      = 2 * ∑ y : achiral n, (D4.refls.filter (fun g => g • y = y)).card := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl fun y _ => card_stab_eq_two_mul n y
  omega

/-! ## Computable twin and banked anchors -/

/-- `g`-fixedness of a cell set, phrased so it is decidable: `reanchor` is
computable and `Finset` equality is decidable. -/
def fixPred (g : D4) (S : Finset (ℤ × ℤ)) : Prop := reanchor (S.image (D4.toFun g)) = S

instance decidableFixPred (g : D4) (S : Finset (ℤ × ℤ)) : Decidable (fixPred g S) := by
  unfold fixPred; infer_instance

instance decidableIsCanonicalAnimal (n : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsCanonicalAnimal n S) := by
  unfold IsCanonicalAnimal; infer_instance

/-- Every canonical animal of `n` cells is an `n`-subset of the `n × n` box —
the enumeration `fixCountC` runs over. -/
lemma mem_powersetCard_box {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsCanonicalAnimal n S) :
    S ∈ (box n n).powersetCard n := by
  rw [Finset.mem_powersetCard]
  refine ⟨fun p hp => ?_, hS.1⟩
  rw [mem_box]
  have hx1 := canonicalAnimal_x_le hS hp
  have hy1 := canonicalAnimal_y_le hS hp
  have hx0 := hS.2.2.1 p hp
  have hy0 := hS.2.2.2.2.1 p hp
  omega

/-- Computable counterpart of `fixCount`: enumerate the `n`-element subsets of
the `n × n` box and count the canonical `g`-fixed ones. Brute force, so useful
only for small `n` — see the cost note in the module header. -/
def fixCountC (n : ℕ) (g : D4) : ℕ :=
  (((box n n).powersetCard n).filter fun S => IsCanonicalAnimal n S ∧ fixPred g S).card

/-- The computable twin agrees with `fixCount`. -/
theorem fixCountC_eq (n : ℕ) (g : D4) : fixCountC n g = fixCount n g := by
  rw [fixCountC, fixCount, ← Nat.card_eq_finsetCard]
  refine Nat.card_congr ⟨fun S => ⟨⟨S.1, ((Finset.mem_filter.mp S.2).2).1⟩, ?_⟩,
    fun x => ⟨x.1.1, ?_⟩, ?_, ?_⟩
  · exact Subtype.ext ((Finset.mem_filter.mp S.2).2).2
  · rw [Finset.mem_filter]
    exact ⟨mem_powersetCard_box x.1.2, x.1.2, congrArg Subtype.val x.2⟩
  · intro S; rfl
  · intro x; rfl

/-! The right-hand sides are the `r90`, `r180`, `hmirror` and `dmirror32`
columns of `results/sym_counts.txt` (an absent `r90` row there means `0`).
`native_decide` is the approved route for this validation section
(PLAN.md, scope interview 2026-07-20). -/

set_option linter.style.nativeDecide false

theorem R90_1 : R90 1 = 1 := by change fixCount 1 D4.r1 = 1; rw [← fixCountC_eq]; native_decide
theorem R90_2 : R90 2 = 0 := by change fixCount 2 D4.r1 = 0; rw [← fixCountC_eq]; native_decide
theorem R90_3 : R90 3 = 0 := by change fixCount 3 D4.r1 = 0; rw [← fixCountC_eq]; native_decide
theorem R90_4 : R90 4 = 2 := by change fixCount 4 D4.r1 = 2; rw [← fixCountC_eq]; native_decide
theorem R90_5 : R90 5 = 2 := by change fixCount 5 D4.r1 = 2; rw [← fixCountC_eq]; native_decide

theorem R180_1 : R180 1 = 1 := by change fixCount 1 D4.r2 = 1; rw [← fixCountC_eq]; native_decide
theorem R180_2 : R180 2 = 4 := by change fixCount 2 D4.r2 = 4; rw [← fixCountC_eq]; native_decide
theorem R180_3 : R180 3 = 4 := by change fixCount 3 D4.r2 = 4; rw [← fixCountC_eq]; native_decide
theorem R180_4 : R180 4 = 22 := by change fixCount 4 D4.r2 = 22; rw [← fixCountC_eq]; native_decide
theorem R180_5 : R180 5 = 22 := by change fixCount 5 D4.r2 = 22; rw [← fixCountC_eq]; native_decide

theorem Hm_1 : Hm 1 = 1 := by change fixCount 1 D4.h = 1; rw [← fixCountC_eq]; native_decide
theorem Hm_2 : Hm 2 = 2 := by change fixCount 2 D4.h = 2; rw [← fixCountC_eq]; native_decide
theorem Hm_3 : Hm 3 = 4 := by change fixCount 3 D4.h = 4; rw [← fixCountC_eq]; native_decide
theorem Hm_4 : Hm 4 = 10 := by change fixCount 4 D4.h = 10; rw [← fixCountC_eq]; native_decide
theorem Hm_5 : Hm 5 = 22 := by change fixCount 5 D4.h = 22; rw [← fixCountC_eq]; native_decide

theorem Dm_1 : Dm 1 = 1 := by change fixCount 1 D4.d = 1; rw [← fixCountC_eq]; native_decide
theorem Dm_2 : Dm 2 = 2 := by change fixCount 2 D4.d = 2; rw [← fixCountC_eq]; native_decide
theorem Dm_3 : Dm 3 = 4 := by change fixCount 3 D4.d = 4; rw [← fixCountC_eq]; native_decide
theorem Dm_4 : Dm 4 = 10 := by change fixCount 4 D4.d = 10; rw [← fixCountC_eq]; native_decide
theorem Dm_5 : Dm 5 = 22 := by change fixCount 5 D4.d = 22; rw [← fixCountC_eq]; native_decide

/-! The banked `r90` column has no rows for `n = 2, 3`, which `r90_vanish`
independently explains; `R90_2` and `R90_3` above confirm the two agree. -/

example : R90 2 = 0 := r90_vanish 2 (by norm_num)
example : R90 3 = 0 := r90_vanish 3 (by norm_num)

/-! ## Derived spot checks against the companion sequences -/

/-- `Free 4 = 22` (A030222), from `free_eq` and the anchors. -/
theorem Free_4 : Free 4 = 22 := by
  have h := free_eq 4 (by norm_num)
  rw [a_4, R90_4, R180_4, Hm_4, Dm_4] at h
  omega

/-- `OneSided 4 = 34` (A030233), from `oneSided_eq` and the anchors. -/
theorem OneSided_4 : OneSided 4 = 34 := by
  have h := oneSided_eq 4 (by norm_num)
  rw [a_4, R90_4, R180_4] at h
  omega

/-- `Bilateral 4 = 10` (A030234), from `bilateral_eq` and the anchors. -/
theorem Bilateral_4 : Bilateral 4 = 10 := by
  have h := bilateral_eq 4 (by norm_num)
  rw [Hm_4, Dm_4] at h
  omega

/-! ## Axiom audit

Plain `#print axioms` here; the `#guard_msgs`-wrapped versions are integrated
into the campaign audit point by the orchestrator. The four headline theorems
must carry the standard three; the anchors add exactly the `native_decide`
constant. -/

#print axioms free_eq
#print axioms oneSided_eq
#print axioms bilateral_eq
#print axioms r90_vanish
#print axioms Free_4
#print axioms OneSided_4
#print axioms Bilateral_4

end Polyplets
