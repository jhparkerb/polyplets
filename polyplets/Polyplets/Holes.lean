/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Defs
import Polyplets.Graph

/-!
# Holes: enclosed empty regions of king animals, and the box-ring lower bound

A king animal `S : Finset (ℤ × ℤ)` *encloses* a background cell `p ∉ S` when the
4-connected (rook) component of `p` in the complement of `S` is finite. The
enclosed cells form `enclosed S`; `S` is a `SingleHole` animal when `enclosed S`
is nonempty and rook-connected.

This file proves the **lower bound** half of the paper's Theorem 2: for every
`n ≥ 4` there is an `n`-cell king-connected single-hole animal enclosing exactly
`⌊(n−2)²/8 + ½⌋ = ((n−2)² + 4) / 8` cells (`maxhole_lower`).

## The construction

Everything is easiest in the diagonal coordinates `u = x + y`, `v = x − y`
(every cell has `u ≡ v [MOD 2]`, and a rook step changes both by exactly one).

* `dbox c a b` is the parity-aligned diagonal box with corner cell `c`:
  the cells with `u − u c ∈ [0, a)` and `v − v c ∈ [0, b)`. It has
  `(a * b + 1) / 2` cells (`dbox_card`).
* `boxHole a b = dbox (0,0) a b` is the hole; `hullBox a b = dbox (-1,0) (a+2) (b+2)`
  is the hole together with its diagonal frame; the animal is the frame
  `ringAnimal a b = hullBox a b \ boxHole a b`, of cardinality `a + b + 2`.
* `enclosed (ringAnimal a b) = boxHole a b` (`enclosed_ringAnimal`): the box is
  sealed (every rook neighbour of a box cell is in the box or in the ring) and
  every cell outside the hull escapes to infinity along a horizontal ray.
* Taking `a + b = n − 2` as equal as possible gives the extremal areas.

This is the family of `experiments/maxhole_box_construction.py`, transcribed;
see `results/maxhole-proof.md`. Note that `hullBox \ boxHole` has `a + b + 2`
cells for *all* `a, b`, including the `(2,1)` case where it strictly contains
the 4-neighbour ring of the box; so the `n = 5` "padding cell" of the python
docstring is here just the `(a,b) = (2,1)` member of the uniform family.
-/

namespace Polyplets

/-! ### Rook adjacency, components, holes -/

/-- Rook (4-neighbour) adjacency on the integer grid. -/
def rookAdj (p q : ℤ × ℤ) : Prop :=
  p ≠ q ∧ ((p.1 = q.1 ∧ |p.2 - q.2| = 1) ∨ (p.2 = q.2 ∧ |p.1 - q.1| = 1))

/-- One step of a rook walk through the complement of `S`. -/
def bgStep (S : Finset (ℤ × ℤ)) (x y : ℤ × ℤ) : Prop :=
  x ∉ S ∧ y ∉ S ∧ rookAdj x y

/-- The 4-component of `p` in the complement of `S`. -/
def compComponent (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) : Set (ℤ × ℤ) :=
  {q | Relation.ReflTransGen (bgStep S) p q}

/-- The enclosed (hole) cells of `S`: complement cells with a finite 4-component. -/
def enclosed (S : Finset (ℤ × ℤ)) : Set (ℤ × ℤ) :=
  {p | p ∉ S ∧ (compComponent S p).Finite}

/-- One step of a rook walk through the enclosed cells of `S`. -/
def holeStep (S : Finset (ℤ × ℤ)) (x y : ℤ × ℤ) : Prop :=
  x ∈ enclosed S ∧ y ∈ enclosed S ∧ rookAdj x y

/-- `S` encloses exactly one hole: its enclosed cells are nonempty and
rook-connected. -/
def SingleHole (S : Finset (ℤ × ℤ)) : Prop :=
  (enclosed S).Nonempty ∧
    ∀ p ∈ enclosed S, ∀ q ∈ enclosed S, Relation.ReflTransGen (holeStep S) p q

/-! ### Elementary adjacency facts -/

lemma rookAdj_symm {p q : ℤ × ℤ} (h : rookAdj p q) : rookAdj q p := by
  obtain ⟨hne, h⟩ := h
  refine ⟨hne.symm, ?_⟩
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩
  · exact Or.inl ⟨h1.symm, by rw [abs_sub_comm]; exact h2⟩
  · exact Or.inr ⟨h1.symm, by rw [abs_sub_comm]; exact h2⟩

/-- The horizontal rook step. -/
lemma rookAdj_horiz (p : ℤ × ℤ) {d : ℤ} (hd : d = 1 ∨ d = -1) :
    rookAdj p (p.1 + d, p.2) := by
  refine ⟨?_, Or.inr ⟨rfl, ?_⟩⟩
  · simp only [ne_eq, Prod.ext_iff, not_and]
    intro h; omega
  · simp only
    rw [abs_eq (by norm_num : (0:ℤ) ≤ 1)]
    omega

/-- The vertical rook step. -/
lemma rookAdj_vert (p : ℤ × ℤ) {d : ℤ} (hd : d = 1 ∨ d = -1) :
    rookAdj p (p.1, p.2 + d) := by
  refine ⟨?_, Or.inl ⟨rfl, ?_⟩⟩
  · simp only [ne_eq, Prod.ext_iff, not_and]
    intro _ h; omega
  · simp only
    rw [abs_eq (by norm_num : (0:ℤ) ≤ 1)]
    omega

/-- Any nonzero displacement with both coordinates in `[-1, 1]` is a king step. -/
lemma kingAdj_small_shift (p : ℤ × ℤ) {dx dy : ℤ} (hne : ¬(dx = 0 ∧ dy = 0))
    (hx : -1 ≤ dx) (hx' : dx ≤ 1) (hy : -1 ≤ dy) (hy' : dy ≤ 1) :
    kingAdj p (p.1 + dx, p.2 + dy) := by
  refine ⟨?_, ?_, ?_⟩
  · simp only [ne_eq, Prod.ext_iff, not_and]
    intro h1 h2; exact hne ⟨by omega, by omega⟩
  · rw [abs_le]; constructor <;> simp <;> omega
  · rw [abs_le]; constructor <;> simp <;> omega

/-- Rook steps are king steps. -/
lemma kingAdj_of_rookAdj {p q : ℤ × ℤ} (h : rookAdj p q) : kingAdj p q := by
  obtain ⟨hne, h⟩ := h
  refine ⟨hne, ?_, ?_⟩ <;> rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rw [abs_le] <;> rw [abs_eq (by norm_num : (0:ℤ) ≤ 1)] at h2 <;> omega

/-- A rook step changes both diagonal coordinates by exactly one. -/
lemma rookAdj_diag {p q : ℤ × ℤ} (h : rookAdj p q) :
    (q.1 + q.2 = p.1 + p.2 + 1 ∨ q.1 + q.2 = p.1 + p.2 - 1) ∧
      (q.1 - q.2 = p.1 - p.2 + 1 ∨ q.1 - q.2 = p.1 - p.2 - 1) := by
  obtain ⟨-, h⟩ := h
  rcases h with ⟨h1, h2⟩ | ⟨h1, h2⟩ <;>
    rw [abs_eq (by norm_num : (0:ℤ) ≤ 1)] at h2 <;> omega

/-! ### Parity-aligned diagonal boxes -/

/-- The parity-aligned diagonal box with corner cell `c`, diagonal extents `a`
(in `u = x + y`) and `b` (in `v = x - y`): the cells with `u - u c ∈ [0, a)` and
`v - v c ∈ [0, b)`. Only the cells of the parity class of `c` occur, and they are
enumerated here in two families (even/odd offset). -/
def dbox (c : ℤ × ℤ) (a b : ℕ) : Finset (ℤ × ℤ) :=
  (Finset.range ((a + 1) / 2) ×ˢ Finset.range ((b + 1) / 2)).image
      (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 : ℤ), (c.2 + q.1 - q.2 : ℤ))) ∪
    (Finset.range (a / 2) ×ˢ Finset.range (b / 2)).image
      (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 + 1 : ℤ), (c.2 + q.1 - q.2 : ℤ)))

lemma mem_dbox {c p : ℤ × ℤ} {a b : ℕ} :
    p ∈ dbox c a b ↔
      0 ≤ p.1 + p.2 - (c.1 + c.2) ∧ p.1 + p.2 - (c.1 + c.2) < a ∧
        0 ≤ p.1 - p.2 - (c.1 - c.2) ∧ p.1 - p.2 - (c.1 - c.2) < b := by
  simp only [dbox, Finset.mem_union, Finset.mem_image, Finset.mem_product, Finset.mem_range,
    Prod.exists, Prod.ext_iff]
  constructor
  · rintro (⟨i, j, ⟨hi, hj⟩, h1, h2⟩ | ⟨i, j, ⟨hi, hj⟩, h1, h2⟩) <;> omega
  · rintro ⟨h1, h2, h3, h4⟩
    obtain ⟨k, hk⟩ | ⟨k, hk⟩ := Int.even_or_odd (p.1 + p.2 - (c.1 + c.2))
    · exact Or.inl ⟨k.toNat, (k - (p.2 - c.2)).toNat, ⟨by omega, by omega⟩, by omega, by omega⟩
    · exact Or.inr ⟨k.toNat, (k - (p.2 - c.2)).toNat, ⟨by omega, by omega⟩, by omega, by omega⟩

private lemma half_mul_half (a b : ℕ) :
    (a + 1) / 2 * ((b + 1) / 2) + a / 2 * (b / 2) = (a * b + 1) / 2 := by
  obtain ⟨p, rfl | rfl⟩ := Nat.even_or_odd' a <;> obtain ⟨q, rfl | rfl⟩ := Nat.even_or_odd' b
  · rw [show (2 * p + 1) / 2 = p by omega, show (2 * q + 1) / 2 = q by omega,
      show 2 * p / 2 = p by omega, show 2 * q / 2 = q by omega,
      show 2 * p * (2 * q) = 4 * (p * q) by ring]
    omega
  · rw [show (2 * p + 1) / 2 = p by omega, show (2 * q + 1 + 1) / 2 = q + 1 by omega,
      show 2 * p / 2 = p by omega, show (2 * q + 1) / 2 = q by omega,
      show 2 * p * (2 * q + 1) = 4 * (p * q) + 2 * p by ring,
      show p * (q + 1) = p * q + p by ring]
    omega
  · rw [show (2 * p + 1 + 1) / 2 = p + 1 by omega, show (2 * q + 1) / 2 = q by omega,
      show (2 * p + 1) / 2 = p by omega, show 2 * q / 2 = q by omega,
      show (2 * p + 1) * (2 * q) = 4 * (p * q) + 2 * q by ring,
      show (p + 1) * q = p * q + q by ring]
    omega
  · rw [show (2 * p + 1 + 1) / 2 = p + 1 by omega, show (2 * q + 1 + 1) / 2 = q + 1 by omega,
      show (2 * p + 1) / 2 = p by omega, show (2 * q + 1) / 2 = q by omega,
      show (2 * p + 1) * (2 * q + 1) = 4 * (p * q) + 2 * p + 2 * q + 1 by ring,
      show (p + 1) * (q + 1) = p * q + p + q + 1 by ring]
    omega

/-- The parity sublattice of an `a × b` diagonal box, corner-aligned, has
`⌈ab/2⌉` cells. -/
lemma dbox_card (c : ℤ × ℤ) (a b : ℕ) : (dbox c a b).card = (a * b + 1) / 2 := by
  have hinj : ∀ e : ℤ, Function.Injective
      (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 + e : ℤ), (c.2 + q.1 - q.2 : ℤ))) := by
    rintro e ⟨i, j⟩ ⟨i', j'⟩ h
    simp only [Prod.mk.injEq] at h ⊢
    omega
  have hinj0 : Function.Injective
      (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 : ℤ), (c.2 + q.1 - q.2 : ℤ))) := by
    have := hinj 0
    simpa using this
  have hdisj : Disjoint
      ((Finset.range ((a + 1) / 2) ×ˢ Finset.range ((b + 1) / 2)).image
        (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 : ℤ), (c.2 + q.1 - q.2 : ℤ))))
      ((Finset.range (a / 2) ×ˢ Finset.range (b / 2)).image
        (fun q : ℕ × ℕ => ((c.1 + q.1 + q.2 + 1 : ℤ), (c.2 + q.1 - q.2 : ℤ)))) := by
    rw [Finset.disjoint_left]
    rintro p hp hp'
    simp only [Finset.mem_image, Finset.mem_product, Finset.mem_range, Prod.exists,
      Prod.ext_iff] at hp hp'
    obtain ⟨i, j, -, h1, h2⟩ := hp
    obtain ⟨i', j', -, h1', h2'⟩ := hp'
    omega
  rw [dbox, Finset.card_union_of_disjoint hdisj, Finset.card_image_of_injective _ hinj0,
    Finset.card_image_of_injective _ (hinj 1), Finset.card_product, Finset.card_product,
    Finset.card_range, Finset.card_range, Finset.card_range, Finset.card_range]
  exact half_mul_half a b

/-! ### The box hole, its hull and the ring animal -/

/-- The hole: the parity-aligned diagonal box `u ∈ [0, a), v ∈ [0, b)`. -/
def boxHole (a b : ℕ) : Finset (ℤ × ℤ) := dbox (0, 0) a b

/-- The hull of the hole: the diagonal box `u ∈ [-1, a], v ∈ [-1, b]`. -/
def hullBox (a b : ℕ) : Finset (ℤ × ℤ) := dbox (-1, 0) (a + 2) (b + 2)

/-- The animal: the diagonal frame around the hole. -/
def ringAnimal (a b : ℕ) : Finset (ℤ × ℤ) := hullBox a b \ boxHole a b

lemma mem_boxHole {p : ℤ × ℤ} {a b : ℕ} :
    p ∈ boxHole a b ↔
      0 ≤ p.1 + p.2 ∧ p.1 + p.2 < a ∧ 0 ≤ p.1 - p.2 ∧ p.1 - p.2 < b := by
  rw [boxHole, mem_dbox]; constructor <;> (intro h; refine ⟨?_, ?_, ?_, ?_⟩ <;> simp at h ⊢ <;>
    omega)

lemma mem_hullBox {p : ℤ × ℤ} {a b : ℕ} :
    p ∈ hullBox a b ↔
      -1 ≤ p.1 + p.2 ∧ p.1 + p.2 ≤ a ∧ -1 ≤ p.1 - p.2 ∧ p.1 - p.2 ≤ b := by
  rw [hullBox, mem_dbox]
  constructor <;> (intro h; refine ⟨?_, ?_, ?_, ?_⟩ <;> simp at h ⊢ <;> omega)

lemma mem_ringAnimal {p : ℤ × ℤ} {a b : ℕ} :
    p ∈ ringAnimal a b ↔
      (-1 ≤ p.1 + p.2 ∧ p.1 + p.2 ≤ a ∧ -1 ≤ p.1 - p.2 ∧ p.1 - p.2 ≤ b) ∧
        ¬(0 ≤ p.1 + p.2 ∧ p.1 + p.2 < a ∧ 0 ≤ p.1 - p.2 ∧ p.1 - p.2 < b) := by
  rw [ringAnimal, Finset.mem_sdiff, mem_hullBox, mem_boxHole]

lemma boxHole_subset_hullBox (a b : ℕ) : boxHole a b ⊆ hullBox a b := by
  intro p hp
  rw [mem_boxHole] at hp
  rw [mem_hullBox]
  omega

lemma boxHole_card (a b : ℕ) : (boxHole a b).card = (a * b + 1) / 2 := dbox_card _ a b

lemma ringAnimal_card (a b : ℕ) : (ringAnimal a b).card = a + b + 2 := by
  rw [ringAnimal, Finset.card_sdiff_of_subset (boxHole_subset_hullBox a b), boxHole_card,
    hullBox, dbox_card, show (a + 2) * (b + 2) = a * b + 2 * a + 2 * b + 4 by ring]
  omega

/-! ### The hole is rook-connected -/

/-- One step of a rook walk inside a cell set. -/
private abbrev rookStep (S : Finset (ℤ × ℤ)) (x y : ℤ × ℤ) : Prop :=
  x ∈ S ∧ y ∈ S ∧ rookAdj x y

/-- One step of a king walk inside a cell set. -/
private abbrev kingStep (S : Finset (ℤ × ℤ)) (x y : ℤ × ℤ) : Prop :=
  x ∈ S ∧ y ∈ S ∧ kingAdj x y

/-- Every box cell reaches the corner `(0,0)` by rook steps inside the box
(fuelled induction on `3x + |y|`, which strictly decreases along the descent). -/
private lemma boxHole_reach_aux (a b : ℕ) (ha : 2 ≤ a) (hb : 2 ≤ b) :
    ∀ (N : ℕ) (p : ℤ × ℤ), p ∈ boxHole a b → 3 * p.1.toNat + p.2.natAbs ≤ N →
      Relation.ReflTransGen (rookStep (boxHole a b)) p (0, 0) := by
  intro N
  induction N with
  | zero =>
      rintro ⟨x, y⟩ hp hN
      rw [mem_boxHole] at hp
      simp only at hp hN
      obtain ⟨h1, h2, h3, h4⟩ := hp
      have hx : x = 0 := by omega
      have hy : y = 0 := by omega
      subst hx; subst hy
      exact .refl
  | succ N ih =>
      rintro ⟨x, y⟩ hp hN
      have hp' := hp
      rw [mem_boxHole] at hp'
      simp only at hp' hN
      obtain ⟨h1, h2, h3, h4⟩ := hp'
      by_cases hbase : x = 0 ∧ y = 0
      · obtain ⟨rfl, rfl⟩ := hbase; exact .refl
      · by_cases hA : 1 ≤ x + y ∧ 1 ≤ x - y
        · refine Relation.ReflTransGen.head (b := (x + -1, y)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_)
          · rw [mem_boxHole]; simp only; omega
          · exact rookAdj_horiz (x, y) (Or.inr rfl)
          · rw [mem_boxHole]; simp only; omega
          · simp only; omega
        · by_cases hB : x + y = 0
          · refine Relation.ReflTransGen.head (b := (x, y + 1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_)
            · rw [mem_boxHole]; simp only; omega
            · exact rookAdj_vert (x, y) (Or.inl rfl)
            · rw [mem_boxHole]; simp only; omega
            · simp only; omega
          · refine Relation.ReflTransGen.head (b := (x, y + -1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_)
            · rw [mem_boxHole]; simp only; omega
            · exact rookAdj_vert (x, y) (Or.inr rfl)
            · rw [mem_boxHole]; simp only; omega
            · simp only; omega

/-- For `a, b ≥ 2` the box hole is rook-connected. -/
lemma boxHole_rook_connected (a b : ℕ) (ha : 2 ≤ a) (hb : 2 ≤ b) :
    ∀ p ∈ boxHole a b, ∀ q ∈ boxHole a b,
      Relation.ReflTransGen (rookStep (boxHole a b)) p q := by
  have hsymm : ∀ x y, rookStep (boxHole a b) x y → rookStep (boxHole a b) y x := by
    rintro x y ⟨h1, h2, h3⟩; exact ⟨h2, h1, rookAdj_symm h3⟩
  intro p hp q hq
  have hpr := boxHole_reach_aux a b ha hb _ p hp le_rfl
  have hqr := boxHole_reach_aux a b ha hb _ q hq le_rfl
  refine hpr.trans ?_
  exact Relation.ReflTransGen.mono (fun x y h => hsymm y x h) hqr.swap

/-- Degenerate case: for `b = 1` and `a ≤ 2` the box hole is the single cell
`(0,0)`.  (This is the `n = 4` and `n = 5` end of the family.) -/
lemma boxHole_eq_singleton {a b : ℕ} (ha : 1 ≤ a) (ha2 : a ≤ 2) (hb : b = 1) :
    boxHole a b = {(0, 0)} := by
  subst hb
  ext ⟨x, y⟩
  rw [mem_boxHole, Finset.mem_singleton, Prod.ext_iff]
  simp only
  omega

/-! ### The ring animal is king-connected -/

/-- The left wall `u = -1` descends to the base corner `(-1, 0)`. -/
private lemma ring_left_reach (a b : ℕ) :
    ∀ (N : ℕ) (p : ℤ × ℤ), p ∈ ringAnimal a b → p.1 + p.2 = -1 →
      (p.1 - p.2 + 1).toNat ≤ N →
      Relation.ReflTransGen (kingStep (ringAnimal a b)) p (-1, 0) := by
  intro N
  induction N with
  | zero =>
      rintro ⟨x, y⟩ hp hu hN
      rw [mem_ringAnimal] at hp
      simp only at hp hu hN
      have hx : x = -1 := by omega
      have hy : y = 0 := by omega
      subst hx; subst hy; exact .refl
  | succ N ih =>
      rintro ⟨x, y⟩ hp hu hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hu hN
      by_cases hbase : x - y = -1
      · have hx : x = -1 := by omega
        have hy : y = 0 := by omega
        subst hx; subst hy; exact .refl
      · refine Relation.ReflTransGen.head (b := (x + -1, y + 1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_ ?_)
        · rw [mem_ringAnimal]; simp only; omega
        · exact kingAdj_small_shift (x, y) (by omega) (by omega) (by omega) (by omega) (by omega)
        · rw [mem_ringAnimal]; simp only; omega
        · simp only; omega
        · simp only; omega

/-- The bottom wall `v = -1` descends to the base corner `(-1, 0)`. -/
private lemma ring_bottom_reach (a b : ℕ) :
    ∀ (N : ℕ) (p : ℤ × ℤ), p ∈ ringAnimal a b → p.1 - p.2 = -1 →
      (p.1 + p.2 + 1).toNat ≤ N →
      Relation.ReflTransGen (kingStep (ringAnimal a b)) p (-1, 0) := by
  intro N
  induction N with
  | zero =>
      rintro ⟨x, y⟩ hp hv hN
      rw [mem_ringAnimal] at hp
      simp only at hp hv hN
      have hx : x = -1 := by omega
      have hy : y = 0 := by omega
      subst hx; subst hy; exact .refl
  | succ N ih =>
      rintro ⟨x, y⟩ hp hv hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hv hN
      by_cases hbase : x + y = -1
      · have hx : x = -1 := by omega
        have hy : y = 0 := by omega
        subst hx; subst hy; exact .refl
      · refine Relation.ReflTransGen.head (b := (x + -1, y + -1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_ ?_)
        · rw [mem_ringAnimal]; simp only; omega
        · exact kingAdj_small_shift (x, y) (by omega) (by omega) (by omega) (by omega) (by omega)
        · rw [mem_ringAnimal]; simp only; omega
        · simp only; omega
        · simp only; omega

/-- The top wall `v = b` runs left along the wall and drops onto the left wall. -/
private lemma ring_top_reach (a b : ℕ) :
    ∀ (N : ℕ) (p : ℤ × ℤ), p ∈ ringAnimal a b → p.1 - p.2 = b →
      (p.1 + p.2 + 1).toNat ≤ N →
      Relation.ReflTransGen (kingStep (ringAnimal a b)) p (-1, 0) := by
  intro N
  induction N with
  | zero =>
      rintro ⟨x, y⟩ hp hv hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hv hN
      exact ring_left_reach a b _ _ hp (by simp only; omega) le_rfl
  | succ N ih =>
      rintro ⟨x, y⟩ hp hv hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hv hN
      by_cases hleft : x + y = -1
      · exact ring_left_reach a b _ _ hp (by simp only; omega) le_rfl
      · by_cases hdrop : x + y = 0
        · refine Relation.ReflTransGen.head (b := (x + -1, y)) ⟨hp, ?_, ?_⟩ ?_
          · rw [mem_ringAnimal]; simp only; omega
          · exact kingAdj_of_rookAdj (rookAdj_horiz (x, y) (Or.inr rfl))
          · refine ring_left_reach a b _ _ ?_ (by simp only; omega) le_rfl
            rw [mem_ringAnimal]; simp only; omega
        · refine Relation.ReflTransGen.head (b := (x + -1, y + -1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_ ?_)
          · rw [mem_ringAnimal]; simp only; omega
          · exact kingAdj_small_shift (x, y) (by omega) (by omega) (by omega) (by omega) (by omega)
          · rw [mem_ringAnimal]; simp only; omega
          · simp only; omega
          · simp only; omega

/-- The right wall `u = a` runs down along the wall and drops onto the bottom
wall. -/
private lemma ring_right_reach (a b : ℕ) :
    ∀ (N : ℕ) (p : ℤ × ℤ), p ∈ ringAnimal a b → p.1 + p.2 = a →
      (p.1 - p.2 + 1).toNat ≤ N →
      Relation.ReflTransGen (kingStep (ringAnimal a b)) p (-1, 0) := by
  intro N
  induction N with
  | zero =>
      rintro ⟨x, y⟩ hp hu hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hu hN
      exact ring_bottom_reach a b _ _ hp (by simp only; omega) le_rfl
  | succ N ih =>
      rintro ⟨x, y⟩ hp hu hN
      have hp' := hp
      rw [mem_ringAnimal] at hp'
      simp only at hp' hu hN
      by_cases hbot : x - y = -1
      · exact ring_bottom_reach a b _ _ hp (by simp only; omega) le_rfl
      · by_cases hdrop : x - y = 0
        · refine Relation.ReflTransGen.head (b := (x + -1, y)) ⟨hp, ?_, ?_⟩ ?_
          · rw [mem_ringAnimal]; simp only; omega
          · exact kingAdj_of_rookAdj (rookAdj_horiz (x, y) (Or.inr rfl))
          · refine ring_bottom_reach a b _ _ ?_ (by simp only; omega) le_rfl
            rw [mem_ringAnimal]; simp only; omega
        · refine Relation.ReflTransGen.head (b := (x + -1, y + 1)) ⟨hp, ?_, ?_⟩ (ih _ ?_ ?_ ?_)
          · rw [mem_ringAnimal]; simp only; omega
          · exact kingAdj_small_shift (x, y) (by omega) (by omega) (by omega) (by omega) (by omega)
          · rw [mem_ringAnimal]; simp only; omega
          · simp only; omega
          · simp only; omega

/-- Every ring cell reaches the base corner `(-1, 0)`. -/
private lemma ringAnimal_reach_base (a b : ℕ) (p : ℤ × ℤ) (hp : p ∈ ringAnimal a b) :
    Relation.ReflTransGen (kingStep (ringAnimal a b)) p (-1, 0) := by
  have hp' := hp
  rw [mem_ringAnimal] at hp'
  have hcase : p.1 + p.2 = -1 ∨ p.1 - p.2 = -1 ∨ p.1 - p.2 = b ∨ p.1 + p.2 = a := by omega
  rcases hcase with h | h | h | h
  · exact ring_left_reach a b _ _ hp h le_rfl
  · exact ring_bottom_reach a b _ _ hp h le_rfl
  · exact ring_top_reach a b _ _ hp h le_rfl
  · exact ring_right_reach a b _ _ hp h le_rfl

/-- The ring animal is a king animal. -/
theorem ringAnimal_kingConnected (a b : ℕ) : KingConnected (ringAnimal a b) := by
  have hsymm : ∀ x y, kingStep (ringAnimal a b) x y → kingStep (ringAnimal a b) y x := by
    rintro x y ⟨h1, h2, h3⟩; exact ⟨h2, h1, kingAdj_symm h3⟩
  intro p hp q hq
  have hpr := ringAnimal_reach_base a b p hp
  have hqr := ringAnimal_reach_base a b q hq
  exact hpr.trans (Relation.ReflTransGen.mono (fun x y h => hsymm y x h) hqr.swap)

/-! ### The ring animal encloses exactly the box -/

/-- The box is sealed: a background rook walk started inside the box never
leaves it, because every cell one rook step outside the box lies in the ring. -/
lemma component_subset_boxHole (a b : ℕ) {p : ℤ × ℤ} (hp : p ∈ boxHole a b) :
    compComponent (ringAnimal a b) p ⊆ ↑(boxHole a b) := by
  intro q hq
  simp only [compComponent, Set.mem_setOf_eq] at hq
  induction hq with
  | refl => exact Finset.mem_coe.mpr hp
  | tail _ hstep ih =>
      obtain ⟨-, hnot, hadj⟩ := hstep
      have hd := rookAdj_diag hadj
      rw [Finset.mem_coe, mem_boxHole] at ih ⊢
      rw [mem_ringAnimal] at hnot
      omega

/-- A cell with a one-way horizontal escape ray in the complement of `S` has an
infinite complement component. -/
lemma component_infinite_of_ray (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) {e : ℤ}
    (he : e = 1 ∨ e = -1) (h : ∀ k : ℕ, ((p.1 + e * k, p.2) : ℤ × ℤ) ∉ S) :
    (compComponent S p).Infinite := by
  have hmem : ∀ k : ℕ, ((p.1 + e * k, p.2) : ℤ × ℤ) ∈ compComponent S p := by
    intro k
    induction k with
    | zero => simpa [compComponent] using Relation.ReflTransGen.refl
    | succ k ihk =>
        have hcast : ((p.1 + e * ((k + 1 : ℕ) : ℤ), p.2) : ℤ × ℤ)
            = ((p.1 + e * (k : ℤ)) + e, p.2) := by push_cast; ring_nf
        rw [hcast]
        exact Relation.ReflTransGen.tail ihk ⟨h k, by rw [← hcast]; exact h (k + 1),
          rookAdj_horiz (p.1 + e * (k : ℤ), p.2) he⟩
  refine Set.infinite_of_injective_forall_mem
    (f := fun k : ℕ => ((p.1 + e * k, p.2) : ℤ × ℤ)) ?_ hmem
  intro k l hkl
  simp only [Prod.mk.injEq] at hkl
  have hne : e ≠ 0 := by rcases he with rfl | rfl <;> norm_num
  have h1 : e * (k : ℤ) = e * (l : ℤ) := by linarith [hkl.1]
  exact Nat.cast_injective (mul_left_cancel₀ hne h1)

/-- Every cell outside the hull escapes to infinity. -/
lemma component_infinite_of_not_mem_hullBox (a b : ℕ) {p : ℤ × ℤ}
    (hp : p ∉ hullBox a b) : (compComponent (ringAnimal a b) p).Infinite := by
  rw [mem_hullBox] at hp
  by_cases hpos : (a : ℤ) < p.1 + p.2 ∨ (b : ℤ) < p.1 - p.2
  · refine component_infinite_of_ray _ _ (e := 1) (Or.inl rfl) fun k hmem => ?_
    rw [mem_ringAnimal] at hmem
    simp only at hmem
    omega
  · refine component_infinite_of_ray _ _ (e := -1) (Or.inr rfl) fun k hmem => ?_
    rw [mem_ringAnimal] at hmem
    simp only at hmem
    omega

/-- The enclosed cells of the ring animal are exactly the box hole. -/
theorem enclosed_ringAnimal (a b : ℕ) : enclosed (ringAnimal a b) = ↑(boxHole a b) := by
  ext p
  constructor
  · rintro ⟨hpS, hfin⟩
    by_contra hpb
    rw [Finset.mem_coe] at hpb
    have hph : p ∉ hullBox a b := fun h =>
      hpS (by rw [ringAnimal, Finset.mem_sdiff]; exact ⟨h, hpb⟩)
    exact component_infinite_of_not_mem_hullBox a b hph hfin
  · intro hp
    rw [Finset.mem_coe] at hp
    refine ⟨?_, ?_⟩
    · rw [ringAnimal, Finset.mem_sdiff]
      tauto
    · exact Set.Finite.subset (boxHole a b).finite_toSet (component_subset_boxHole a b hp)

/-- The ring animal has a single hole, given that its box is rook-connected. -/
theorem ringAnimal_singleHole (a b : ℕ) (ha : 1 ≤ a) (hb : 1 ≤ b)
    (hconn : ∀ p ∈ boxHole a b, ∀ q ∈ boxHole a b,
      Relation.ReflTransGen (rookStep (boxHole a b)) p q) :
    SingleHole (ringAnimal a b) := by
  have hmem : ∀ x : ℤ × ℤ, x ∈ boxHole a b → x ∈ enclosed (ringAnimal a b) := by
    intro x hx
    rw [enclosed_ringAnimal]
    exact Finset.mem_coe.mpr hx
  refine ⟨⟨(0, 0), ?_⟩, ?_⟩
  · refine hmem _ ?_
    rw [mem_boxHole]
    simp only
    omega
  · intro p hp q hq
    rw [enclosed_ringAnimal, Finset.mem_coe] at hp hq
    refine Relation.ReflTransGen.mono ?_ (hconn p hp q hq)
    rintro x y ⟨hx, hy, hxy⟩
    exact ⟨hmem x hx, hmem y hy, hxy⟩

/-! ### The lower bound -/

private lemma area_eq (m : ℕ) : ((m + 1) / 2 * (m / 2) + 1) / 2 = (m ^ 2 + 4) / 8 := by
  obtain ⟨t, rfl | rfl⟩ := Nat.even_or_odd' m
  · rw [show (2 * t + 1) / 2 = t by omega, show 2 * t / 2 = t by omega,
      show (2 * t) ^ 2 = 4 * (t * t) by ring]
    omega
  · rw [show (2 * t + 1 + 1) / 2 = t + 1 by omega, show (2 * t + 1) / 2 = t by omega,
      show (2 * t + 1) ^ 2 = 4 * (t * t) + 4 * t + 1 by ring,
      show (t + 1) * t = t * t + t by ring]
    omega

/-- **Theorem 2, lower bound.** For every `n ≥ 4` there is an `n`-cell king
animal with a single hole enclosing `⌊(n−2)²/8 + ½⌋ = ((n−2)² + 4) / 8` cells:
the diagonal ring around the parity-aligned box `a × b` with `a + b = n − 2` as
equal as possible. -/
theorem maxhole_lower (n : ℕ) (hn : 4 ≤ n) :
    ∃ S : Finset (ℤ × ℤ), S.card = n ∧ KingConnected S ∧ SingleHole S ∧
      (enclosed S).ncard = ((n - 2) ^ 2 + 4) / 8 := by
  set m := n - 2 with hm
  have hm2 : 2 ≤ m := by omega
  set a := (m + 1) / 2 with hadef
  set b := m / 2 with hbdef
  have ha1 : 1 ≤ a := by omega
  have hb1 : 1 ≤ b := by omega
  refine ⟨ringAnimal a b, ?_, ringAnimal_kingConnected _ _, ?_, ?_⟩
  · rw [ringAnimal_card]; omega
  · refine ringAnimal_singleHole a b ha1 hb1 ?_
    by_cases hbig : 2 ≤ b
    · exact boxHole_rook_connected a b (by omega) hbig
    · have hsing : boxHole a b = {(0, 0)} :=
        boxHole_eq_singleton ha1 (by omega) (by omega)
      intro p hp q hq
      rw [hsing, Finset.mem_singleton] at hp hq
      subst hp; subst hq
      exact .refl
  · rw [enclosed_ringAnimal, Set.ncard_coe_finset, boxHole_card, hadef, hbdef, area_eq]

/-- The paper writes the extremal area as `⌊x²/8 + ½⌋` (round half up); over the
naturals that is the expression `(x² + 4) / 8` used above. -/
theorem floor_maxhole_formula (x : ℕ) :
    ⌊((x : ℚ) ^ 2 / 8 + 1 / 2)⌋ = ((x ^ 2 + 4) / 8 : ℕ) := by
  have h : ((x : ℚ) ^ 2 / 8 + 1 / 2) = ((((x : ℤ) ^ 2 + 4 : ℤ) : ℚ) / ((8 : ℕ) : ℚ)) := by
    push_cast; ring
  rw [h, Rat.floor_intCast_div_natCast]
  push_cast [Int.natCast_div]
  norm_num

/-! ### Numeric anchors

The banked exact values `M(n)` for `n = 4, …, 10` (`results/maxhole.txt`) are
`1, 1, 2, 3, 5, 6, 8`; the construction attains each of them. -/

theorem maxhole_lower_anchors :
    ((4 - 2) ^ 2 + 4) / 8 = 1 ∧ ((5 - 2) ^ 2 + 4) / 8 = 1 ∧ ((6 - 2) ^ 2 + 4) / 8 = 2 ∧
      ((7 - 2) ^ 2 + 4) / 8 = 3 ∧ ((8 - 2) ^ 2 + 4) / 8 = 5 ∧ ((9 - 2) ^ 2 + 4) / 8 = 6 ∧
      ((10 - 2) ^ 2 + 4) / 8 = 8 := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> decide

/-- The construction realises the banked `M(n)` for `n = 4, …, 10`. -/
theorem maxhole_lower_banked (n : ℕ) (hn : 4 ≤ n) (hn' : n ≤ 10) :
    ∃ S : Finset (ℤ × ℤ), S.card = n ∧ KingConnected S ∧ SingleHole S ∧
      (enclosed S).ncard = [1, 1, 2, 3, 5, 6, 8].getD (n - 4) 0 := by
  obtain ⟨S, h1, h2, h3, h4⟩ := maxhole_lower n hn
  refine ⟨S, h1, h2, h3, ?_⟩
  rw [h4]
  interval_cases n <;> decide

/-! ### Sanity gates on the parametrisation

Small instances of the ring, evaluated by the kernel. -/

example : (ringAnimal 1 1).card = 4 := by decide
example : (ringAnimal 2 1).card = 5 := by decide
example : (ringAnimal 2 2).card = 6 := by decide
example : (ringAnimal 3 2).card = 7 := by decide
example : (ringAnimal 3 3).card = 8 := by decide
example : (boxHole 3 3).card = 5 := by decide

/-! ### Axiom audit -/

#print axioms enclosed_ringAnimal
#print axioms ringAnimal_kingConnected
#print axioms ringAnimal_singleHole
#print axioms ringAnimal_card
#print axioms boxHole_card
#print axioms maxhole_lower
#print axioms floor_maxhole_formula
#print axioms maxhole_lower_anchors
#print axioms maxhole_lower_banked

end Polyplets
