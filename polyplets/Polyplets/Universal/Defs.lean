/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib

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
* `L.M = max (1 ∪ {|d| : d ∈ D})` — the x-reach of a single step, the `1` of
  the king case. `M` is what the width bound (`Universal/Finite.lean`) is
  stated in terms of; it never enters the counting identities.

`IsCanonical L n H S` and `T L n H` are `Defs.lean`'s king definitions with
`kingAdj` replaced by `Adj L`.
-/

namespace Polyplets.Universal

/-- **A row-local lattice**: a finite nonempty set `D` of up-offsets. Within-row
adjacency is nearest-neighbor; between consecutive rows the allowed
x-displacements are exactly the elements of `D`. -/
structure RowLocal where
  /-- The up-offset set: `q` sits above `p` iff `q.2 = p.2 + 1` and
  `q.1 - p.1 ∈ D`. -/
  D : Finset ℤ
  /-- The up-offset set is nonempty (condition (U)). -/
  hD : D.Nonempty

namespace RowLocal

variable (L : RowLocal)

/-- **The drift count** `b = |D|`: the number of choices for a single upward
walk step. This is the `3` of the king lattice and the `b` of the universal
diagonal law. -/
def b : ℕ := L.D.card

/-- The drift count is positive. -/
lemma one_le_b : 1 ≤ L.b := Finset.card_pos.mpr L.hD

/-- **The x-reach of a step**: `max (1 ∪ {|d| : d ∈ D})`. A single adjacency
step moves the x-coordinate by at most `M` (`adj_abs_dx_le`); this replaces the
king lattice's `1` in the width bound, and nowhere else. -/
def M : ℤ := (insert (1 : ℤ) (L.D.image fun d => |d|)).max' (Finset.insert_nonempty _ _)

/-- A row step (`|dx| = 1`) is within reach. -/
lemma one_le_M : 1 ≤ L.M := Finset.le_max' _ _ (Finset.mem_insert_self _ _)

/-- The reach is nonnegative. -/
lemma M_nonneg : 0 ≤ L.M := le_trans (by norm_num) L.one_le_M

/-- Every up-offset is within reach. -/
lemma abs_le_M {d : ℤ} (hd : d ∈ L.D) : |d| ≤ L.M :=
  Finset.le_max' _ _ (Finset.mem_insert_of_mem (Finset.mem_image_of_mem _ hd))

end RowLocal

/-! ## Adjacency -/

/-- **Row-local adjacency**: distinct cells that are neighbors inside a row, or
sit on consecutive rows at an x-displacement drawn from `L.D`. (The `p ≠ q`
clause is implied by each disjunct; it is kept to match the paper's phrasing.)
-/
def Adj (L : RowLocal) (p q : ℤ × ℤ) : Prop :=
  p ≠ q ∧ ((p.2 = q.2 ∧ |p.1 - q.1| = 1) ∨
    (q.2 = p.2 + 1 ∧ q.1 - p.1 ∈ L.D) ∨
    (p.2 = q.2 + 1 ∧ p.1 - q.1 ∈ L.D))

/-- Row-local adjacency is symmetric: the row case is symmetric in `|dx|`, and
the two vertical cases swap. -/
lemma adj_symm {L : RowLocal} {p q : ℤ × ℤ} (h : Adj L p q) : Adj L q p := by
  obtain ⟨hne, hcase⟩ := h
  refine ⟨hne.symm, ?_⟩
  rcases hcase with ⟨hy, hx⟩ | ⟨hy, hd⟩ | ⟨hy, hd⟩
  · exact Or.inl ⟨hy.symm, by rw [abs_sub_comm]; exact hx⟩
  · exact Or.inr (Or.inr ⟨hy, hd⟩)
  · exact Or.inr (Or.inl ⟨hy, hd⟩)

/-- **Adjacency is row-local**: a step changes the row index by at most one.
This is the *only* property of adjacency that the separation surgery uses. -/
lemma adj_abs_dy_le {L : RowLocal} {p q : ℤ × ℤ} (h : Adj L p q) : |p.2 - q.2| ≤ 1 := by
  obtain ⟨-, hcase⟩ := h
  rw [abs_le]
  rcases hcase with ⟨hy, -⟩ | ⟨hy, -⟩ | ⟨hy, -⟩ <;> omega

/-- **Adjacency has bounded x-reach**: a step moves the x-coordinate by at most
`L.M`. In the king lattice `M = 1`, which is why king paths cannot skip a
column; in general they can, and only this weaker bound survives. -/
lemma adj_abs_dx_le {L : RowLocal} {p q : ℤ × ℤ} (h : Adj L p q) : |p.1 - q.1| ≤ L.M := by
  obtain ⟨-, hcase⟩ := h
  rcases hcase with ⟨-, hx⟩ | ⟨-, hd⟩ | ⟨-, hd⟩
  · rw [hx]; exact L.one_le_M
  · have := L.abs_le_M hd
    rw [abs_le] at this ⊢
    omega
  · have := L.abs_le_M hd
    rw [abs_le] at this ⊢
    omega

/-- **Reading off the drift**: if `q` sits one row above `p` and the two are
adjacent, their x-displacement is an up-offset. -/
lemma adj_up_mem {L : RowLocal} {p q : ℤ × ℤ} (h : Adj L p q) (hy : q.2 = p.2 + 1) :
    q.1 - p.1 ∈ L.D := by
  obtain ⟨-, hcase⟩ := h
  rcases hcase with ⟨hy', -⟩ | ⟨-, hd⟩ | ⟨hy', -⟩
  · omega
  · exact hd
  · omega

/-- **Realizing the drift**: any up-offset gives an adjacency between
consecutive rows. Converse of `adj_up_mem`; together they are the class-A
bijection's `b` choices. -/
lemma adj_of_up {L : RowLocal} {p q : ℤ × ℤ} (hy : q.2 = p.2 + 1)
    (hd : q.1 - p.1 ∈ L.D) : Adj L p q := by
  refine ⟨fun heq => ?_, Or.inr (Or.inl ⟨hy, hd⟩)⟩
  rw [heq] at hy
  omega

/-! ## Animals -/

/-- A finite cell set is `L`-connected: every pair of its cells is joined by a
path of `L`-adjacent steps that stays inside the set. -/
def Conn (L : RowLocal) (S : Finset (ℤ × ℤ)) : Prop :=
  ∀ p ∈ S, ∀ q ∈ S,
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q

/-- `S` is the canonical (origin-anchored) representative of a fixed `L`-animal
of `n` cells with bounding-box height exactly `H`: `n` cells, `L`-connected,
minimum x- and y-coordinates `0`, maximum y-coordinate `H - 1`. The x-extent is
unconstrained. -/
def IsCanonical (L : RowLocal) (n H : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = n ∧ Conn L S ∧
  (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧
  (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0) ∧
  (∀ p ∈ S, p.2 ≤ (H : ℤ) - 1) ∧ (∃ p ∈ S, p.2 = (H : ℤ) - 1)

/-- `T L n H`: the number of fixed `L`-animals of `n` cells whose bounding box
has height exactly `H`, i.e. the number of origin-anchored canonical
representatives. Finiteness is `Universal/Finite.lean`. -/
noncomputable def T (L : RowLocal) (n H : ℕ) : ℕ :=
  {S : Finset (ℤ × ℤ) | IsCanonical L n H S}.ncard

end Polyplets.Universal
