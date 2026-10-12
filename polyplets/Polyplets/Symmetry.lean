/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.GroupTheory.SpecificGroups.Dihedral
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Group
import Mathlib.Tactic.Push
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Set
import Polyplets.Sequence

/-!
# The eightfold count: Burnside identities for polyplets

`Sequence.lean` counts *fixed* polyplets — `a n`, the polyplets of
`n` cells taken up to translation only. The paper's §7 companion sequences take
the further quotient by the eight symmetries of the square, and every one of
them is a Burnside average of fixed-point counts. This file builds that
apparatus.

The group is Mathlib's `DihedralGroup 4` (`D4` below): `r i` is the rotation
by `i` quarterTurn turns and `sr i` the mirror in the `x`-axis followed by `r i`.
It acts on `ℤ × ℤ` through `D4.toFun`, built from one quarterTurn turn and one
mirror (`rot i = quarterTurn^[i.val]`). Acting on polyplets needs a
anchoring step, because a rotated polyplet is generally no longer
origin-anchored:

* `Anchored S` : `min x = min y = 0` (the anchoring field of
  `IsPolyplet`),
* `corner S` : the lower-left corner of `S`'s bounding box,
* `anchor S = S.image (· - corner S)` : the anchored translate.

`anchor` kills translations (`anchor_image_add`) and fixes anchored sets
(`anchor_eq_self`), which is exactly what the two `MulAction` laws need, so
`g • S = anchor (S.image g.toFun)` is an action of `D4` on
`polyplets n = {S | IsPolyplet n S}`.

## Results

With `fixCount n g = #(fixed points of g)` and the rotation subgroup realized
as the cyclic group `C4 = Multiplicative (ZMod 4)` acting through
`rotHom : C4 →* D4`:

* `eight_mul_Free` : `8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n`
* `four_mul_OneSided` : `4 * OneSided n = a n + 2 * R90 n + R180 n`
* `two_mul_Bilateral` : `2 * Bilateral n = Hm n + Dm n`
* `R90_eq_zero` : `R90 n = 0` unless `n % 4 ∈ {0, 1}`

The first two are Mathlib's Burnside lemma
(`MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group`) over `D4` resp.
`C4`, after collapsing the eight fixed-point counts by
`fixCount_inv` (`fixedBy g = fixedBy g⁻¹`, which pairs `r 1` with `r 3`) and
`fixCount_conj` (conjugation, which pairs the mirror `sr 2` with `sr 0` and
`sr 1` with `sr 3`).

`two_mul_Bilateral` counts the pairs `(g, x)` with `g` a reflection fixing `x` in
two ways. Summed over reflections it is `2 * Hm n + 2 * Dm n`; summed over
points it is `∑_{x achiral} #(reflections in the stabilizer of x)`, and
`card_stab_eq_two_mul` shows a stabilizer containing a reflection is half
reflections (translate by a fixed reflection), so this is
`½ ∑_{x achiral} #(stabilizer of x)` — which Burnside, applied to the
`D4`-invariant set of achiral animals, evaluates as `½ · 8 · Bilateral n`.

`R90_eq_zero` is elementary and center-free. A quarterTurn-turn-fixed `S` satisfies
`S.image σ = S` for the affine map `σ p = ρ p + t` (`ρ` the quarterTurn turn, `t`
the anchoring translation). Since `ρ² = -1`, one has `σ⁴ = id`, and a point
fixed by `σ²` is already fixed by `σ` (`2 p` is pinned by `t`, and so is
`2 σ p`). So off the at-most-one `σ`-fixed point (`(1 - ρ)` is injective) the
`σ`-orbits all have exactly four elements: `card_div_four` peels them off one
at a time, leaving `n % 4 ∈ {0, 1}`.

## Conventions

The counts `n ≤ 5` (R90, R180, Hm, Dm) are kernel-decided in `Checks.lean`
through the enumerator of `Enum.lean` (`fixCount_eq_length`), and `n = 1 … 6`
are also verified outside Lean by the committed brute force
`experiments/sym_brute_check.py` (run 2026-07-31, log alongside), including
the `n = 6` row where `hmirror = 58` first parts company with `dmirror = 56`;
the derived free/one-sided/bilateral values match A030222/A030233/A030234
through `n = 6`. The conventions are pinned by proof: `toFun_mul` says the
eight maps compose as the group multiplies, `toFun_sr0`, `toFun_sr3` and
`toFun_r2` say which map each generator is, and nothing published depends on
which mirror is which: `eight_mul_Free` and `two_mul_Bilateral` are symmetric in `Hm`
and `Dm`.
-/

namespace Polyplets

open scoped BigOperators

/-! ## The dihedral group of the square and its action on the plane -/

/-- The eight symmetries of the square: Mathlib's `DihedralGroup 4`, with `r i`
the rotation by `i` quarterTurn turns and `sr i` the mirror in the `x`-axis followed
by `r i`. -/
abbrev D4 := DihedralGroup 4

open DihedralGroup (r sr)

/-- A quarterTurn turn counterclockwise about the origin. -/
def quarterTurn (p : ℤ × ℤ) : ℤ × ℤ := (-p.2, p.1)

/-- The mirror in the `x`-axis. -/
def mirror (p : ℤ × ℤ) : ℤ × ℤ := (p.1, -p.2)

lemma quarterTurn_add (p q : ℤ × ℤ) : quarterTurn (p + q) = quarterTurn p + quarterTurn q := by
  simp [quarterTurn, add_comm]

lemma quarterTurn_injective : Function.Injective quarterTurn := by
  intro p q h
  simp only [quarterTurn, Prod.mk.injEq, neg_inj] at h
  exact Prod.ext h.2 h.1

/-- The king relation survives a quarterTurn turn: `|Δx|, |Δy| ≤ 1` is symmetric
under swapping and negating coordinates. -/
lemma quarterTurn_kingAdj {p q : ℤ × ℤ} (h : kingAdj p q) :
    kingAdj (quarterTurn p) (quarterTurn q) := by
  obtain ⟨hne, h1, h2⟩ := h
  refine ⟨fun hc => hne (quarterTurn_injective hc), ?_, h1⟩
  simp only [quarterTurn]
  rw [abs_le] at h2 ⊢
  constructor <;> omega

lemma mirror_add (p q : ℤ × ℤ) : mirror (p + q) = mirror p + mirror q := by
  simp [mirror, add_comm]

lemma mirror_injective : Function.Injective mirror := by
  intro p q h
  simp only [mirror, Prod.mk.injEq, neg_inj] at h
  exact Prod.ext h.1 h.2

lemma mirror_kingAdj {p q : ℤ × ℤ} (h : kingAdj p q) : kingAdj (mirror p) (mirror q) := by
  obtain ⟨hne, h1, h2⟩ := h
  refine ⟨fun hc => hne (mirror_injective hc), h1, ?_⟩
  simp only [mirror]
  rw [abs_le] at h2 ⊢
  constructor <;> omega

@[simp] lemma mirror_mirror (p : ℤ × ℤ) : mirror (mirror p) = p := by simp [mirror]

lemma quarterTurn_iterate_four : quarterTurn^[4] = id := by
  funext p
  change quarterTurn (quarterTurn (quarterTurn (quarterTurn p))) = p
  simp [quarterTurn]

/-- Iterating the quarterTurn turn only matters modulo four. -/
lemma quarterTurn_iterate_mod (k : ℕ) : quarterTurn^[k] = quarterTurn^[k % 4] := by
  conv_lhs => rw [← Nat.mod_add_div k 4, Function.iterate_add, Function.iterate_mul,
    quarterTurn_iterate_four, Function.iterate_id, Function.comp_id]

lemma quarterTurn_iterate_add (k : ℕ) (p q : ℤ × ℤ) :
    quarterTurn^[k] (p + q) = quarterTurn^[k] p + quarterTurn^[k] q := by
  induction k with
  | zero => rfl
  | succ k ih => simp only [Function.iterate_succ_apply', ih, quarterTurn_add]

lemma quarterTurn_iterate_kingAdj (k : ℕ) {p q : ℤ × ℤ} (h : kingAdj p q) :
    kingAdj (quarterTurn^[k] p) (quarterTurn^[k] q) := by
  induction k with
  | zero => exact h
  | succ k ih => simp only [Function.iterate_succ_apply']; exact quarterTurn_kingAdj ih

/-- A mirror image of a quarterTurn turn is three quarterTurn turns of the mirror image. -/
lemma mirror_quarterTurn (p : ℤ × ℤ) : mirror (quarterTurn p) = quarterTurn^[3] (mirror p) := by
  change mirror (quarterTurn p) = quarterTurn (quarterTurn (quarterTurn (mirror p)))
  simp [mirror, quarterTurn]

lemma mirror_quarterTurn_iterate (k : ℕ) (p : ℤ × ℤ) :
    mirror (quarterTurn^[k] p) = quarterTurn^[3 * k] (mirror p) := by
  induction k with
  | zero => rfl
  | succ k ih =>
    rw [Function.iterate_succ_apply', mirror_quarterTurn, ih, ← Function.iterate_add_apply]
    congr 1
    ring

/-- Rotation by `i` quarterTurn turns. -/
def rot (i : ZMod 4) : ℤ × ℤ → ℤ × ℤ := quarterTurn^[i.val]

lemma rot_one (p : ℤ × ℤ) : rot 1 p = quarterTurn p := rfl

lemma rot_add (i j : ZMod 4) : rot (i + j) = rot i ∘ rot j := by
  rw [rot, rot, rot, ZMod.val_add, ← quarterTurn_iterate_mod, Function.iterate_add]

lemma mirror_rot (i : ZMod 4) (p : ℤ × ℤ) : mirror (rot i p) = rot (-i) (mirror p) := by
  rw [rot, rot, mirror_quarterTurn_iterate, show (-i : ZMod 4) = 3 * i by
    rw [show (3 : ZMod 4) = -1 by decide, neg_one_mul], ZMod.val_mul, ← quarterTurn_iterate_mod]
  rfl

namespace D4

/-- The action of `D4` on the integer plane: `r i` rotates by `i` quarterTurn turns,
`sr i` mirrors in the `x`-axis and then rotates. -/
def toFun : D4 → ℤ × ℤ → ℤ × ℤ
  | .r i => rot i
  | .sr i => mirror ∘ rot i

@[simp] lemma toFun_one (p : ℤ × ℤ) : toFun 1 p = p := rfl

lemma toFun_mul (g g' : D4) (p : ℤ × ℤ) : toFun (g * g') p = toFun g (toFun g' p) := by
  rcases g with i | i <;> rcases g' with j | j
  · rw [DihedralGroup.r_mul_r]
    exact congrFun (rot_add i j) p
  · rw [DihedralGroup.r_mul_sr]
    change mirror (rot (j - i) p) = rot i (mirror (rot j p))
    rw [mirror_rot, mirror_rot, ← Function.comp_apply (f := rot i), ← rot_add, neg_sub,
      sub_eq_add_neg]
  · rw [DihedralGroup.sr_mul_r]
    change mirror (rot (i + j) p) = mirror (rot i (rot j p))
    rw [rot_add]
    rfl
  · rw [DihedralGroup.sr_mul_sr]
    change rot (j - i) p = mirror (rot i (mirror (rot j p)))
    rw [mirror_rot, mirror_mirror, ← Function.comp_apply (f := rot (-i)), ← rot_add,
      neg_add_eq_sub]

/-- Every element of `D4` acts by an additive map, which is what makes
anchoring commute with the action. -/
lemma toFun_add (g : D4) (p q : ℤ × ℤ) : toFun g (p + q) = toFun g p + toFun g q := by
  rcases g with i | i
  · exact quarterTurn_iterate_add _ p q
  · change mirror (rot i (p + q)) = mirror (rot i p) + mirror (rot i q)
    rw [rot, quarterTurn_iterate_add, mirror_add]

lemma toFun_injective (g : D4) : Function.Injective (toFun g) := by
  rcases g with i | i
  · exact quarterTurn_injective.iterate _
  · exact mirror_injective.comp (quarterTurn_injective.iterate _)

/-- The king relation is `D4`-invariant. -/
lemma toFun_kingAdj (g : D4) {p q : ℤ × ℤ} (hpq : kingAdj p q) :
    kingAdj (toFun g p) (toFun g q) := by
  rcases g with i | i
  · exact quarterTurn_iterate_kingAdj _ hpq
  · exact mirror_kingAdj (quarterTurn_iterate_kingAdj _ hpq)

/-- The generators as maps: `sr 0` is the `x`-axis mirror, `sr 3` the
coordinate swap, `r 2` the half turn. -/
lemma toFun_sr0 : toFun (sr 0) = mirror := rfl

lemma toFun_sr3 : toFun (sr 3) = fun p => (p.2, p.1) := by
  funext p
  have h3 : (3 : ZMod 4).val = 3 := rfl
  simp [toFun, rot, h3, quarterTurn, mirror, Function.iterate_succ, Function.comp]

lemma toFun_r2 : toFun (r 2) = fun p => -p := by
  funext p
  have h2 : (2 : ZMod 4).val = 2 := rfl
  simp [toFun, rot, h2, quarterTurn, Function.iterate_succ, Function.comp, Prod.ext_iff]

/-- The four reflections. -/
def refls : Finset D4 := {sr 0, sr 1, sr 2, sr 3}

/-- A sum over `D4` is a sum over the rotations plus a sum over the mirrors. -/
lemma sum_univ {M : Type*} [AddCommMonoid M] (f : D4 → M) :
    ∑ g : D4, f g = ∑ i : ZMod 4, f (r i) + ∑ i : ZMod 4, f (sr i) := by
  rw [← Fintype.sum_equiv DihedralGroup.equivSum.symm (fun x => f (DihedralGroup.equivSum.symm x))
    f (fun _ => rfl), Fintype.sum_sum_type]
  rfl

end D4

/-- A sum over `ZMod 4`, unfolded. -/
lemma ZMod.sum_univ_four {M : Type*} [AddCommMonoid M] (f : ZMod 4 → M) :
    ∑ i : ZMod 4, f i = f 0 + f 1 + f 2 + f 3 :=
  Fin.sum_univ_four f

/-- The lower-left corner of `S`'s bounding box (junk value `0` when `S` is
empty). -/
def corner (S : Finset (ℤ × ℤ)) : ℤ × ℤ :=
  if h : S.Nonempty then (S.inf' h Prod.fst, S.inf' h Prod.snd) else (0, 0)

/-- The anchored translate of `S`: slide its bounding box to the origin. -/
def anchor (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := S.image (fun p => p - corner S)

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

lemma corner_image_add {S : Finset (ℤ × ℤ)} (h : S.Nonempty) (t : ℤ × ℤ) :
    corner (S.image (fun p => p + t)) = corner S + t := by
  have hi : (S.image (fun p => p + t)).Nonempty := h.image _
  rw [corner, corner, dif_pos h, dif_pos hi]
  rw [inf'_image_add h t hi Prod.fst t.1 (fun p => rfl),
    inf'_image_add h t hi Prod.snd t.2 (fun p => rfl)]
  rfl

/-- **Anchoring kills translations.** -/
lemma anchor_image_add (S : Finset (ℤ × ℤ)) (t : ℤ × ℤ) :
    anchor (S.image (fun p => p + t)) = anchor S := by
  rcases S.eq_empty_or_nonempty with rfl | h
  · simp [anchor]
  · rw [anchor, anchor, corner_image_add h t, Finset.image_image]
    exact Finset.image_congr fun p _ => by simp only [Function.comp_apply]; abel

/-- A nonempty finite set is fixed only by the zero translation. -/
lemma translate_eq_self {S : Finset (ℤ × ℤ)} {v : ℤ × ℤ} (h : S.Nonempty)
    (hS : translate v S = S) : v = 0 := by
  have := corner_image_add h v
  rw [show S.image (fun p => p + v) = translate v S from rfl, hS] at this
  simpa using this

/-- An anchored set has its bounding-box corner at the origin. -/
lemma corner_eq_zero {S : Finset (ℤ × ℤ)} (hS : Anchored S) : corner S = 0 := by
  obtain ⟨p, hpS, hp⟩ := hS.x_zero
  obtain ⟨q, hqS, hq⟩ := hS.y_zero
  have h : S.Nonempty := hS.nonempty
  have h1 : S.inf' h Prod.fst ≤ p.1 := Finset.inf'_le Prod.fst hpS
  have h2 : S.inf' h Prod.snd ≤ q.2 := Finset.inf'_le Prod.snd hqS
  rw [corner, dif_pos h]
  refine Prod.ext ?_ ?_
  · refine le_antisymm ?_ ?_
    · rw [hp] at h1; exact h1
    · exact Finset.le_inf' h _ fun b hb => hS.x_nonneg b hb
  · refine le_antisymm ?_ ?_
    · rw [hq] at h2; exact h2
    · exact Finset.le_inf' h _ fun b hb => hS.y_nonneg b hb

/-- **Anchoring fixes anchored sets.** -/
lemma anchor_eq_self {S : Finset (ℤ × ℤ)} (hS : Anchored S) : anchor S = S := by
  rw [anchor, corner_eq_zero hS]
  simp

/-- The anchored set is anchored. -/
lemma anchor_anchored {S : Finset (ℤ × ℤ)} (h : S.Nonempty) : Anchored (anchor S) := by
  obtain ⟨a, ha, hae⟩ := Finset.exists_mem_eq_inf' h Prod.fst
  obtain ⟨b, hb, hbe⟩ := Finset.exists_mem_eq_inf' h Prod.snd
  have hv : corner S = (S.inf' h Prod.fst, S.inf' h Prod.snd) := dif_pos h
  refine ⟨?_, ⟨a - corner S, Finset.mem_image_of_mem _ ha, ?_⟩,
    ?_, ⟨b - corner S, Finset.mem_image_of_mem _ hb, ?_⟩⟩
  · rintro p hp
    simp only [anchor, Finset.mem_image] at hp
    obtain ⟨q, hq, rfl⟩ := hp
    have hle : S.inf' h Prod.fst ≤ q.1 := Finset.inf'_le Prod.fst hq
    simp only [hv, Prod.fst_sub]
    omega
  · simp only [hv, Prod.fst_sub, hae]; omega
  · rintro p hp
    simp only [anchor, Finset.mem_image] at hp
    obtain ⟨q, hq, rfl⟩ := hp
    have hle : S.inf' h Prod.snd ≤ q.2 := Finset.inf'_le Prod.snd hq
    simp only [hv, Prod.snd_sub]
    omega
  · simp only [hv, Prod.snd_sub, hbe]; omega

lemma anchor_card (S : Finset (ℤ × ℤ)) : (anchor S).card = S.card :=
  Finset.card_image_of_injective _ (fun p q hpq => by
    have : p - corner S + corner S = q - corner S + corner S := by rw [hpq]
    simpa using this)

lemma kingConnected_anchor {S : Finset (ℤ × ℤ)} (hS : KingConnected S) :
    KingConnected (anchor S) :=
  kingConnected_image (f := fun p => p - corner S)
    (fun p q hpq => by simpa [sub_eq_add_neg] using kingAdj_add (-corner S) hpq) hS

/-! ## The action on polyplets -/

/-- Being a polyplet survives "apply a symmetry, then anchor". -/
lemma isPolyplet_anchor {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S)
    (g : D4) : IsPolyplet n (anchor (S.image (D4.toFun g))) := by
  have hne : (S.image (D4.toFun g)).Nonempty := hS.nonempty.image _
  refine ⟨?_, ?_, anchor_anchored hne⟩
  · rw [anchor_card, Finset.card_image_of_injective _ (D4.toFun_injective g)]
    exact hS.card
  · exact kingConnected_anchor (kingConnected_image (fun _ _ => D4.toFun_kingAdj g) hS.conn)

lemma a_eq_natCard (n : ℕ) : a n = Nat.card (polyplets n) :=
  (Nat.card_coe_set_eq (polyplets n)).symm

/-- Images compose along the group law. -/
lemma image_toFun_mul (g g' : D4) (T : Finset (ℤ × ℤ)) :
    T.image (D4.toFun (g * g')) = (T.image (D4.toFun g')).image (D4.toFun g) := by
  rw [Finset.image_image]
  refine Finset.image_congr ?_
  intro p _
  simpa using D4.toFun_mul g g' p

/-- Images of translates are translates of images: the additivity of the action
in the form anchoring needs. -/
lemma image_toFun_add (g : D4) (T : Finset (ℤ × ℤ)) (u : ℤ × ℤ) :
    (T.image (fun p => p + u)).image (D4.toFun g)
      = (T.image (D4.toFun g)).image (fun p => p + D4.toFun g u) := by
  rw [Finset.image_image, Finset.image_image]
  refine Finset.image_congr ?_
  intro p _
  simpa using D4.toFun_add g p u

lemma anchor_eq_image_add (T : Finset (ℤ × ℤ)) :
    anchor T = T.image (fun p => p + -corner T) := by
  simp only [anchor, sub_eq_add_neg]

lemma anchor_eq_translate (T : Finset (ℤ × ℤ)) :
    anchor T = translate (-corner T) T :=
  anchor_eq_image_add T

instance instSMulD4Polyplets (n : ℕ) : SMul D4 (polyplets n) :=
  ⟨fun g S => ⟨anchor (S.1.image (D4.toFun g)), isPolyplet_anchor S.2 g⟩⟩

lemma smul_polyplets_val {n : ℕ} (g : D4) (S : polyplets n) :
    (g • S).1 = anchor (S.1.image (D4.toFun g)) := rfl

instance instMulActionD4Polyplets (n : ℕ) : MulAction D4 (polyplets n) where
  one_smul S := by
    refine Subtype.ext ?_
    rw [smul_polyplets_val]
    have hid : S.1.image (D4.toFun 1) = S.1 := by
      rw [show D4.toFun 1 = id from funext fun p => D4.toFun_one p]
      exact Finset.image_id
    rw [hid, anchor_eq_self S.2.anchored]
  mul_smul g g' S := by
    refine Subtype.ext ?_
    rw [smul_polyplets_val, smul_polyplets_val, smul_polyplets_val,
      image_toFun_mul g g' S.1,
      anchor_eq_image_add (S.1.image (D4.toFun g')),
      image_toFun_add g (S.1.image (D4.toFun g')) (-corner (S.1.image (D4.toFun g'))),
      anchor_image_add]

/-! ## Finiteness bridges -/

instance instFinitePolyplets (n : ℕ) : Finite (polyplets n) := (polyplets_finite n).to_subtype

noncomputable instance instFintypeCA (n : ℕ) : Fintype (polyplets n) := Fintype.ofFinite _

noncomputable instance instFintypeFixedByD4 (n : ℕ) (g : D4) :
    Fintype (MulAction.fixedBy (polyplets n) g) := Fintype.ofFinite _

noncomputable instance instFintypeOrbitsD4 (n : ℕ) :
    Fintype (MulAction.orbitRel.Quotient D4 (polyplets n)) := Fintype.ofFinite _

/-! ## The fixed-point counts -/

/-- The number of polyplets of `n` cells fixed by `g`. -/
noncomputable def fixCount (n : ℕ) (g : D4) : ℕ := Nat.card (MulAction.fixedBy (polyplets n) g)

/-- Quarter-turn-symmetric animals. -/
noncomputable def R90 (n : ℕ) : ℕ := fixCount n (r 1)

/-- Half-turn-symmetric animals. -/
noncomputable def R180 (n : ℕ) : ℕ := fixCount n (r 2)

/-- Animals symmetric in an axis-parallel mirror (`y ↦ -y`); the `hmirror`
column of `results/sym_counts.txt`. -/
noncomputable def Hm (n : ℕ) : ℕ := fixCount n (sr 0)

/-- Animals symmetric in a diagonal mirror (swap coordinates); the `dmirror`
column of `results/sym_counts.txt`. -/
noncomputable def Dm (n : ℕ) : ℕ := fixCount n (sr 3)

/-- Free polyplets: `D4`-orbits of polyplets (A030222). -/
noncomputable def Free (n : ℕ) : ℕ := Nat.card (MulAction.orbitRel.Quotient D4 (polyplets n))

/-- The fixed-point count is the number of polyplets fixed by `g`, as
a set of finsets. -/
lemma fixCount_eq_ncard (n : ℕ) (g : D4) :
    fixCount n g = {S | IsPolyplet n S ∧ anchor (S.image (D4.toFun g)) = S}.ncard := by
  have hset : Subtype.val '' MulAction.fixedBy (polyplets n) g
      = {S | IsPolyplet n S ∧ anchor (S.image (D4.toFun g)) = S} := by
    ext S
    simp only [Set.mem_image, MulAction.fixedBy, Set.mem_setOf_eq, Subtype.exists, mem_polyplets,
      exists_and_right, exists_eq_right]
    constructor
    · rintro ⟨hS, h⟩
      exact ⟨hS, congrArg Subtype.val h⟩
    · rintro ⟨hS, h⟩
      exact ⟨hS, Subtype.ext h⟩
  rw [fixCount, Nat.card_coe_set_eq, ← Set.ncard_image_of_injective _ Subtype.val_injective, hset]

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
mirror `sr 2` with `sr 0` and `sr 1` with `sr 3`. -/
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

/-- The two quarterTurn turns are inverse, hence equinumerously fixed. -/
lemma fixCount_r3 (n : ℕ) : fixCount n (r 3) = fixCount n (r 1) := by
  rw [show (r 3 : D4) = (r 1)⁻¹ by decide, fixCount_inv]

/-- The two axis-parallel mirrors are conjugate by a quarterTurn turn. -/
lemma fixCount_sr2 (n : ℕ) : fixCount n (sr 2) = fixCount n (sr 0) := by
  rw [show (sr 2 : D4) = r 1 * sr 0 * (r 1)⁻¹ by decide, fixCount_conj]

/-- The two diagonal mirrors are conjugate by a quarterTurn turn. -/
lemma fixCount_sr1 (n : ℕ) : fixCount n (sr 1) = fixCount n (sr 3) := by
  rw [show (sr 1 : D4) = r 1 * sr 3 * (r 1)⁻¹ by decide, fixCount_conj]

/-! ## Burnside over the full symmetry group -/

lemma card_fixedBy_eq_fixCount (n : ℕ) (g : D4) :
    Fintype.card (MulAction.fixedBy (polyplets n) g) = fixCount n g :=
  (Nat.card_eq_fintype_card).symm

/-- **Burnside's lemma for `D4`.** -/
theorem eight_mul_Free (n : ℕ) :
    8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n := by
  have hb := MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group D4 (polyplets n)
  rw [D4.sum_univ (fun g => Fintype.card (MulAction.fixedBy (polyplets n) g)), ZMod.sum_univ_four,
    ZMod.sum_univ_four] at hb
  simp only [card_fixedBy_eq_fixCount] at hb
  rw [DihedralGroup.r_zero, fixCount_one, fixCount_r3, fixCount_sr2, fixCount_sr1] at hb
  have hcard : Fintype.card D4 = 8 := DihedralGroup.card
  have hfree : Fintype.card (MulAction.orbitRel.Quotient D4 (polyplets n)) = Free n :=
    (Nat.card_eq_fintype_card).symm
  rw [hcard, hfree] at hb
  simp only [R90, R180, Hm, Dm]
  omega

/-! ## Burnside over the rotation subgroup -/

/-- The cyclic group of order four, `Multiplicative (ZMod 4)`, which acts on
polyplets through the rotations of `D4`. -/
abbrev C4 := Multiplicative (ZMod 4)

/-- The rotation subgroup, as a homomorphism `C4 →* D4`. -/
def rotHom : C4 →* D4 where
  toFun c := r c.toAdd
  map_one' := rfl
  map_mul' _ _ := (DihedralGroup.r_mul_r _ _).symm

lemma rotHom_apply (c : C4) : rotHom c = r c.toAdd := rfl

/-- A sum over `C4`, unfolded. -/
lemma C4.sum_univ {M : Type*} [AddCommMonoid M] (f : C4 → M) :
    ∑ c : C4, f c = f (.ofAdd 0) + f (.ofAdd 1) + f (.ofAdd 2) + f (.ofAdd 3) :=
  Fin.sum_univ_four f

instance instMulActionC4Polyplets (n : ℕ) : MulAction C4 (polyplets n) := MulAction.compHom _ rotHom

noncomputable instance instFintypeFixedByC4 (n : ℕ) (c : C4) :
    Fintype (MulAction.fixedBy (polyplets n) c) := Fintype.ofFinite _

noncomputable instance instFintypeOrbitsC4 (n : ℕ) :
    Fintype (MulAction.orbitRel.Quotient C4 (polyplets n)) := Fintype.ofFinite _

/-- One-sided polyplets: rotation-orbits of polyplets (A030233). -/
noncomputable def OneSided (n : ℕ) : ℕ := Nat.card (MulAction.orbitRel.Quotient C4 (polyplets n))

lemma card_fixedByC4 (n : ℕ) (c : C4) :
    Fintype.card (MulAction.fixedBy (polyplets n) c) = fixCount n (rotHom c) := by
  rw [fixCount, Nat.card_eq_fintype_card]
  exact Fintype.card_congr' rfl

/-- **Burnside's lemma for the rotation subgroup.** -/
theorem four_mul_OneSided (n : ℕ) :
    4 * OneSided n = a n + 2 * R90 n + R180 n := by
  have hb := MulAction.sum_card_fixedBy_eq_card_orbits_mul_card_group C4 (polyplets n)
  rw [C4.sum_univ (fun c => Fintype.card (MulAction.fixedBy (polyplets n) c))] at hb
  simp only [card_fixedByC4, rotHom_apply, toAdd_ofAdd] at hb
  rw [DihedralGroup.r_zero, fixCount_one, fixCount_r3] at hb
  have hcard : Fintype.card C4 = 4 := ZMod.card 4
  have hone : Fintype.card (MulAction.orbitRel.Quotient C4 (polyplets n)) = OneSided n :=
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

/-- **The arithmetic core of `R90_eq_zero`.** If the affine quarterTurn turn
`σ p = (-p.2 + A, p.1 + B)` carries `S` onto itself then `|S| ≡ 0` or `1`
mod `4`. -/
lemma quarterTurn_card_mod (n : ℕ) (S : Finset (ℤ × ℤ)) (A B : ℤ)
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
theorem R90_eq_zero (n : ℕ) (h : ¬ (n % 4 = 0 ∨ n % 4 = 1)) : R90 n = 0 := by
  rw [R90, fixCount]
  have hempty : IsEmpty (MulAction.fixedBy (polyplets n) (r 1 : D4)) := by
    constructor
    rintro ⟨x, hx⟩
    have h1 : anchor (x.1.image (D4.toFun (r 1))) = x.1 := congrArg Subtype.val hx
    obtain ⟨v, hveq⟩ : ∃ v : ℤ × ℤ, anchor (x.1.image (D4.toFun (r 1)))
        = x.1.image (fun p : ℤ × ℤ => (-p.2 + -v.1, p.1 + -v.2)) := by
      refine ⟨corner (x.1.image (D4.toFun (r 1))), ?_⟩
      rw [anchor, Finset.image_image]
      refine Finset.image_congr ?_
      intro p _
      simp only [Function.comp_apply, D4.toFun, rot_one, quarterTurn]
      refine Prod.ext ?_ ?_ <;> simp [sub_eq_add_neg]
    rw [hveq] at h1
    exact h (quarterTurn_card_mod n x.1 (-v.1) (-v.2) x.2.1 h1)
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

/-- The `D4`-invariant set of polyplets fixed by at least one
reflection: the *achiral* animals. -/
def achiral (n : ℕ) : SubMulAction D4 (polyplets n) where
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

/-- Bilateral polyplets: `D4`-orbits of achiral polyplets (A030234). -/
noncomputable def Bilateral (n : ℕ) : ℕ :=
  Nat.card (MulAction.orbitRel.Quotient D4 (achiral n))

/-- Asymmetric polyplets: the free polyplets with no reflection symmetry, free
minus bilateral (A030235). -/
noncomputable def Asym (n : ℕ) : ℕ := Free n - Bilateral n

/-- Double counting a relation over two finite index sets. -/
lemma sum_card_filter_comm {α β : Type*}
    (s : Finset α) (t : Finset β) (R : α → β → Prop) [∀ a b, Decidable (R a b)] :
    ∑ a ∈ s, (t.filter (R a)).card = ∑ b ∈ t, (s.filter (fun a => R a b)).card := by
  simp only [Finset.card_filter]
  exact Finset.sum_comm

lemma D4.sum_refls {M : Type*} [AddCommMonoid M] (f : D4 → M) :
    ∑ g ∈ D4.refls, f g = f (sr 0) + f (sr 1) + f (sr 2) + f (sr 3) := by
  rw [D4.refls, Finset.sum_insert (by decide), Finset.sum_insert (by decide),
    Finset.sum_insert (by decide), Finset.sum_singleton]
  abel

lemma smul_achiral_iff {n : ℕ} (g : D4) (y : achiral n) :
    g • y = y ↔ g • (y : polyplets n) = (y : polyplets n) := by
  constructor
  · intro hy; exact congrArg Subtype.val hy
  · intro hy; exact Subtype.ext hy

/-- A reflection fixes the same animals inside the achiral subset as it does
overall — anything a reflection fixes is achiral by definition. -/
lemma card_fixedBy_achiral_refl (n : ℕ) {g : D4} (hg : g ∈ D4.refls) :
    Nat.card (MulAction.fixedBy (achiral n) g) = fixCount n g := by
  rw [fixCount]
  refine Nat.card_congr ⟨fun y => ⟨(y.1 : polyplets n), ?_⟩,
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
  rw [show Fintype.card D4 = 8 from DihedralGroup.card,
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
  rw [card_fixedBy_achiral_refl n (by decide : sr 0 ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : sr 1 ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : sr 2 ∈ D4.refls),
    card_fixedBy_achiral_refl n (by decide : sr 3 ∈ D4.refls),
    fixCount_sr2, fixCount_sr1]
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
theorem two_mul_Bilateral (n : ℕ) : 2 * Bilateral n = Hm n + Dm n := by
  have h1 := sum_stab_achiral n
  have h2 := sum_stab_refl_achiral n
  have h3 : ∑ y : achiral n, (Finset.univ.filter (fun g : D4 => g • y = y)).card
      = 2 * ∑ y : achiral n, (D4.refls.filter (fun g => g • y = y)).card := by
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl fun y _ => card_stab_eq_two_mul n y
  omega

end Polyplets
