/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.Order.Ring.Star
import Mathlib.Data.Finset.Max
import Mathlib.Data.Int.ConditionallyCompleteOrder
import Mathlib.Data.Int.Star
import Mathlib.Data.Set.Card
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.NormNum.Ineq

/-!
# Row-local lattices: basic definitions

The generic front of the universal diagonal law
(`docs/proofs/universal-diagonal-law.md`). A **row-local lattice** `L` is a
finite nonempty set `D` of *up-offsets*; adjacency is nearest-neighbor inside a
row together with the offsets of `D` between consecutive rows:

```
Adj L p q ↔ p ≠ q ∧ ((p.2 = q.2 ∧ |p.1 - q.1| = 1) ∨
                     (q.2 = p.2 + 1 ∧ q.1 - p.1 ∈ D) ∨
                     (p.2 = q.2 + 1 ∧ p.1 - q.1 ∈ D))
```

The named instances are square (`D = {0}`), hexagonal/brick (`D = {-1, 0}`),
king (`D = {-1, 0, 1}`), the five-neighbor lattice (`D = Icc (-2) 2`) and the
degenerate `D = {-2, 0, 2}`. The drift count is `b = D.card`.

**Scope note.** The paper's condition (R) allows an arbitrary finite
within-row adjacency containing `|dx| = 1`; this Lean class fixes within-row
adjacency to *exactly* `|dx| = 1`. Every named instance lies in the subclass.

Two numbers control the geometry:

* `L.b = L.D.card` — the drift count, the `3` of the king case;
* `L.reach = max (1 ∪ {|d| : d ∈ D})` — the x-reach of a single step, the `1` of
  the king case. `reach` is what the width bound (`RowLocal/Finite.lean`) is
  stated in terms of; it never enters the counting identities.

`IsAnimal L n H S` and `T L n H` are `Defs.lean`'s `heightClass n H` and `T n H`
with `kingAdj` replaced by `Adj L` (`King.lean`'s `isAnimal_king`).
-/

namespace Polyplets.RowLocal

/-- **A row-local lattice**: a finite nonempty set `D` of up-offsets. Within-row
adjacency is nearest-neighbor; between consecutive rows the allowed
x-displacements are exactly the elements of `D`. -/
structure Lattice where
  /-- The up-offset set: `q` sits above `p` iff `q.2 = p.2 + 1` and
  `q.1 - p.1 ∈ D`. -/
  D : Finset ℤ
  /-- The up-offset set is nonempty (condition (U)). -/
  hD : D.Nonempty

namespace Lattice

variable (L : Lattice)

/-- **The drift count** `b = |D|`: the number of choices for a single upward
walk step. This is the `3` of the king lattice and the `b` of the universal
diagonal law. -/
def b : ℕ := L.D.card

/-- The drift count is positive. -/
lemma one_le_b : 1 ≤ L.b := Finset.card_pos.mpr L.hD

/-- **The x-reach of a step**: `max (1 ∪ {|d| : d ∈ D})`. A single adjacency
step moves the x-coordinate by at most `reach` (`adj_abs_dx_le`); this replaces the
king lattice's `1` in the width bound, and nowhere else. -/
def reach : ℤ := (insert (1 : ℤ) (L.D.image fun d => |d|)).max' (Finset.insert_nonempty _ _)

/-- A row step (`|dx| = 1`) is within reach. -/
lemma one_le_reach : 1 ≤ L.reach := Finset.le_max' _ _ (Finset.mem_insert_self _ _)

/-- The reach is nonnegative. -/
lemma reach_nonneg : 0 ≤ L.reach := le_trans (by norm_num) L.one_le_reach

/-- Every up-offset is within reach. -/
lemma abs_le_reach {d : ℤ} (hd : d ∈ L.D) : |d| ≤ L.reach :=
  Finset.le_max' _ _ (Finset.mem_insert_of_mem (Finset.mem_image_of_mem _ hd))

end Lattice

/-! ## Adjacency -/

/-- **Row-local adjacency**: distinct cells that are neighbors inside a row, or
sit on consecutive rows at an x-displacement drawn from `L.D`. (The `p ≠ q`
clause is implied by each disjunct; it is kept to match the paper's phrasing.)
-/
def Adj (L : Lattice) (p q : ℤ × ℤ) : Prop :=
  p ≠ q ∧ ((p.2 = q.2 ∧ |p.1 - q.1| = 1) ∨
    (q.2 = p.2 + 1 ∧ q.1 - p.1 ∈ L.D) ∨
    (p.2 = q.2 + 1 ∧ p.1 - q.1 ∈ L.D))

/-- Row-local adjacency is symmetric: the row case is symmetric in `|dx|`, and
the two vertical cases swap. -/
lemma adj_symm {L : Lattice} {p q : ℤ × ℤ} (h : Adj L p q) : Adj L q p := by
  obtain ⟨hne, hcase⟩ := h
  refine ⟨hne.symm, ?_⟩
  rcases hcase with ⟨hy, hx⟩ | ⟨hy, hd⟩ | ⟨hy, hd⟩
  · exact Or.inl ⟨hy.symm, by rw [abs_sub_comm]; exact hx⟩
  · exact Or.inr (Or.inr ⟨hy, hd⟩)
  · exact Or.inr (Or.inl ⟨hy, hd⟩)

/-- **Adjacency is row-local**: a step changes the row index by at most one.
This is the *only* property of adjacency that the separation surgery uses. -/
lemma adj_abs_dy_le {L : Lattice} {p q : ℤ × ℤ} (h : Adj L p q) : |p.2 - q.2| ≤ 1 := by
  obtain ⟨-, hcase⟩ := h
  rw [abs_le]
  rcases hcase with ⟨hy, -⟩ | ⟨hy, -⟩ | ⟨hy, -⟩ <;> omega

/-- **Adjacency has bounded x-reach**: a step moves the x-coordinate by at most
`L.reach`. In the king lattice `reach = 1`, which is why king paths cannot skip a
column; in general they can, and only this weaker bound survives. -/
lemma adj_abs_dx_le {L : Lattice} {p q : ℤ × ℤ} (h : Adj L p q) : |p.1 - q.1| ≤ L.reach := by
  obtain ⟨-, hcase⟩ := h
  rcases hcase with ⟨-, hx⟩ | ⟨-, hd⟩ | ⟨-, hd⟩
  · rw [hx]; exact L.one_le_reach
  · have := L.abs_le_reach hd
    rw [abs_le] at this ⊢
    omega
  · have := L.abs_le_reach hd
    rw [abs_le] at this ⊢
    omega

/-- **Reading off the drift**: if `q` sits one row above `p` and the two are
adjacent, their x-displacement is an up-offset. -/
lemma adj_up_mem {L : Lattice} {p q : ℤ × ℤ} (h : Adj L p q) (hy : q.2 = p.2 + 1) :
    q.1 - p.1 ∈ L.D := by
  obtain ⟨-, hcase⟩ := h
  rcases hcase with ⟨hy', -⟩ | ⟨-, hd⟩ | ⟨hy', -⟩
  · omega
  · exact hd
  · omega

/-- **Realizing the drift**: any up-offset gives an adjacency between
consecutive rows. Converse of `adj_up_mem`; together they are the class-A
bijection's `b` choices. -/
lemma adj_of_up {L : Lattice} {p q : ℤ × ℤ} (hy : q.2 = p.2 + 1)
    (hd : q.1 - p.1 ∈ L.D) : Adj L p q := by
  refine ⟨fun heq => ?_, Or.inr (Or.inl ⟨hy, hd⟩)⟩
  rw [heq] at hy
  omega

/-! ## Animals -/

/-- A finite cell set is `L`-connected: every pair of its cells is joined by a
path of `L`-adjacent steps that stays inside the set. -/
def Connected (L : Lattice) (S : Finset (ℤ × ℤ)) : Prop :=
  ∀ p ∈ S, ∀ q ∈ S,
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q

/-! ## Translation

Every peeling bijection and both anchoring arguments move cell sets by a
vector. Adjacency depends only on coordinate differences, so translation
preserves it and hence connectivity; this is proved once here, for every
lattice. -/

/-- Translate every cell of `S` by the vector `v`. -/
def translate (v : ℤ × ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := S.image (· + v)

lemma mem_translate {v : ℤ × ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} :
    c ∈ translate v S ↔ c - v ∈ S := by
  simp only [translate, Finset.mem_image]
  constructor
  · rintro ⟨x, hx, rfl⟩
    simpa using hx
  · intro h
    exact ⟨c - v, h, by simp⟩

lemma translate_mem {v : ℤ × ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} (hc : c ∈ S) :
    c + v ∈ translate v S :=
  Finset.mem_image_of_mem _ hc

lemma translate_translate (v w : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    translate v (translate w S) = translate (w + v) S := by
  rw [translate, translate, translate, Finset.image_image]
  congr 1
  funext c
  simp only [Function.comp_apply, add_assoc]

@[simp] lemma translate_zero (S : Finset (ℤ × ℤ)) : translate 0 S = S := by
  simp [translate]

@[simp] lemma card_translate (v : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    (translate v S).card = S.card :=
  Finset.card_image_of_injective S (add_left_injective v)

lemma translate_union (v : ℤ × ℤ) (A B : Finset (ℤ × ℤ)) :
    translate v (A ∪ B) = translate v A ∪ translate v B :=
  Finset.image_union _ _

lemma translate_insert (v : ℤ × ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    translate v (insert c S) = insert (c + v) (translate v S) :=
  Finset.image_insert _ _ _

lemma translate_erase (v : ℤ × ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    translate v (S.erase c) = (translate v S).erase (c + v) :=
  Finset.image_erase (add_left_injective v) _ _

/-- **Adjacency is translation-invariant**: every clause of `Adj` is a
statement about coordinate differences. -/
lemma adj_add {L : Lattice} (v : ℤ × ℤ) {c d : ℤ × ℤ} (h : Adj L c d) :
    Adj L (c + v) (d + v) := by
  obtain ⟨hne, hcase⟩ := h
  refine ⟨fun heq => hne (add_left_injective v heq), ?_⟩
  simp only [Prod.fst_add, Prod.snd_add]
  rcases hcase with ⟨hr, hd⟩ | ⟨hr, hd⟩ | ⟨hr, hd⟩
  · exact Or.inl ⟨by omega, by rwa [show c.1 + v.1 - (d.1 + v.1) = c.1 - d.1 by omega]⟩
  · exact Or.inr (Or.inl ⟨by omega, by rwa [show d.1 + v.1 - (c.1 + v.1) = d.1 - c.1 by omega]⟩)
  · exact Or.inr (Or.inr ⟨by omega, by rwa [show c.1 + v.1 - (d.1 + v.1) = c.1 - d.1 by omega]⟩)

/-- **Connectivity transports along any adjacency-preserving map.** -/
lemma connected_image {L : Lattice} {f : ℤ × ℤ → ℤ × ℤ}
    (hf : ∀ p q, Adj L p q → Adj L (f p) (f q)) {S : Finset (ℤ × ℤ)} (hS : Connected L S) :
    Connected L (S.image f) := by
  intro p hp q hq
  simp only [Finset.mem_image] at hp hq
  obtain ⟨a, haS, rfl⟩ := hp
  obtain ⟨b, hbS, rfl⟩ := hq
  refine Relation.ReflTransGen.lift f (fun x y hxy => ?_) (hS a haS b hbS)
  exact ⟨Finset.mem_image_of_mem f hxy.1, Finset.mem_image_of_mem f hxy.2.1, hf _ _ hxy.2.2⟩

/-- Connectivity is translation-invariant. -/
lemma connected_translate {L : Lattice} (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} (h : Connected L S) :
    Connected L (translate v S) :=
  connected_image (fun _ _ => adj_add v) h

/-- `S` is origin-anchored: its bounding box has lower-left corner at the
origin. This is the translation quotient: every fixed animal has exactly one
anchored translate. -/
structure Anchored (S : Finset (ℤ × ℤ)) : Prop where
  /-- No cell left of column `0`. -/
  x_nonneg : ∀ p ∈ S, 0 ≤ p.1
  /-- Column `0` is occupied. -/
  x_zero : ∃ p ∈ S, p.1 = 0
  /-- No cell below row `0`. -/
  y_nonneg : ∀ p ∈ S, 0 ≤ p.2
  /-- Row `0` is occupied. -/
  y_zero : ∃ p ∈ S, p.2 = 0

/-- An anchored set is nonempty. -/
lemma Anchored.nonempty {S : Finset (ℤ × ℤ)} (hS : Anchored S) : S.Nonempty := by
  obtain ⟨p, hp, -⟩ := hS.x_zero
  exact ⟨p, hp⟩

/-- `S` is an `L`-animal of `n` cells with bounding-box height exactly `H`, as
the representative of its translation class with the bounding box at the
origin: `n` cells, `L`-connected, anchored, maximum y-coordinate `H - 1`. The
x-extent is unconstrained. -/
structure IsAnimal (L : Lattice) (n H : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `n` cells. -/
  card : S.card = n
  /-- `L`-connected. -/
  conn : Connected L S
  /-- Bounding box at the origin. -/
  anchored : Anchored S
  /-- No cell above row `H - 1`. -/
  y_le : ∀ p ∈ S, p.2 ≤ (H : ℤ) - 1
  /-- Row `H - 1` is occupied. -/
  y_top : ∃ p ∈ S, p.2 = (H : ℤ) - 1

/-- `IsAnimal` as a conjunction (for decidability and for unfolding). -/
lemma isAnimal_iff_and {L : Lattice} {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    IsAnimal L n H S ↔ S.card = n ∧ Connected L S ∧
      (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧
      (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0) ∧
      (∀ p ∈ S, p.2 ≤ (H : ℤ) - 1) ∧ (∃ p ∈ S, p.2 = (H : ℤ) - 1) :=
  ⟨fun h => ⟨h.card, h.conn, h.anchored.x_nonneg, h.anchored.x_zero, h.anchored.y_nonneg,
    h.anchored.y_zero, h.y_le, h.y_top⟩,
   fun ⟨a, b, c, d, e, f, g, i⟩ => ⟨a, b, ⟨c, d, e, f⟩, g, i⟩⟩

/-- `T L n H`: the number of fixed `L`-animals of `n` cells whose bounding box
has height exactly `H`, i.e. the number of origin-anchored representatives.
Finiteness is `RowLocal/Finite.lean`. -/
noncomputable def T (L : Lattice) (n H : ℕ) : ℕ :=
  {S : Finset (ℤ × ℤ) | IsAnimal L n H S}.ncard

/-! ## Paths skip no coordinate value -/

/-- **Paths don't skip a coordinate value.** For any adjacency `adj` and any
coordinate `proj` that `adj`-steps move by at most one, if an `adj`-path inside
`S` runs from a cell with `proj ≤ k` to a cell with `proj ≥ k+1`, then some cell
of `S` sits exactly at `proj = k`: the step crossing the `k`/`k+1` boundary
lands on it. Instantiated at `Prod.snd` for rows (`exists_y_eq_of_cross`,
`RowLocal/Finite.lean`) and, on the king lattice, at `Prod.fst` for columns
(`exists_x_eq_of_cross`, `Defs.lean`). -/
lemma exists_proj_eq_of_cross {adj : ℤ × ℤ → ℤ × ℤ → Prop} {S : Finset (ℤ × ℤ)}
    {p q : ℤ × ℤ} {k : ℤ} (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, adj a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ adj a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) : ∃ c ∈ S, proj c = k := by
  revert hq
  induction h with
  | refl => intro hq; exact absurd hq (by omega)
  | @tail b c _ hbc ih =>
      intro hq
      by_cases hb : k + 1 ≤ proj b
      · exact ih hb
      · exact ⟨b, hbc.1, by have h2 := hlip b c hbc.2.2; rw [abs_le] at h2; omega⟩

end Polyplets.RowLocal
