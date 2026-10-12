/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.Order.Group.Abs
import Mathlib.Data.Int.ConditionallyCompleteOrder
import Mathlib.Data.Int.Interval
import Mathlib.Data.Set.Card
import Polyplets.RowLocal.Defs

/-!
# Fixed polyplets: basic definitions

A *polyplet* (king-move animal) is a nonempty finite king-connected set of grid
cells in `ℤ × ℤ`. *Fixed* polyplets are counted up to translation; we pin the
translation quotient by the canonical representative whose bounding box has its
lower-left corner at the origin (`min x = min y = 0`).

`T n H` is the number of fixed polyplets of `n` cells whose bounding box has
height (y-extent) exactly `H`.
-/

namespace Polyplets

/-- King (Chebyshev-distance-one) adjacency on the integer grid: distinct cells
differing by at most one in each coordinate. -/
def kingAdj (p q : ℤ × ℤ) : Prop :=
  p ≠ q ∧ |p.1 - q.1| ≤ 1 ∧ |p.2 - q.2| ≤ 1

/-- King adjacency is symmetric. -/
lemma kingAdj_symm {p q : ℤ × ℤ} (h : kingAdj p q) : kingAdj q p :=
  ⟨h.1.symm, by rw [abs_sub_comm]; exact h.2.1, by rw [abs_sub_comm]; exact h.2.2⟩

/-- A finite cell set is king-connected: every pair of its cells is joined by a
path of king-adjacent steps that stays inside the set. -/
def KingConnected (S : Finset (ℤ × ℤ)) : Prop :=
  ∀ p ∈ S, ∀ q ∈ S,
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q

export RowLocal (Anchored translate mem_translate translate_mem translate_translate translate_zero
  card_translate translate_union translate_insert translate_erase)

/-- King adjacency is translation-invariant. -/
lemma kingAdj_add (v : ℤ × ℤ) {p q : ℤ × ℤ} (h : kingAdj p q) : kingAdj (p + v) (q + v) := by
  obtain ⟨hne, h1, h2⟩ := h
  refine ⟨fun hc => hne (add_left_injective v hc), ?_, ?_⟩
  · simpa using h1
  · simpa using h2

/-- King connectivity transports along any adjacency-preserving map. -/
lemma kingConnected_image {f : ℤ × ℤ → ℤ × ℤ}
    (hadj : ∀ p q, kingAdj p q → kingAdj (f p) (f q))
    {S : Finset (ℤ × ℤ)} (hS : KingConnected S) : KingConnected (S.image f) := by
  intro p hp q hq
  simp only [Finset.mem_image] at hp hq
  obtain ⟨a, haS, rfl⟩ := hp
  obtain ⟨b, hbS, rfl⟩ := hq
  refine Relation.ReflTransGen.lift f (fun x y hxy => ?_) (hS a haS b hbS)
  exact ⟨Finset.mem_image_of_mem f hxy.1, Finset.mem_image_of_mem f hxy.2.1, hadj _ _ hxy.2.2⟩

/-- King connectivity is translation-invariant. -/
lemma kingConnected_translate (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} (h : KingConnected S) :
    KingConnected (translate v S) :=
  kingConnected_image (fun _ _ => kingAdj_add v) h

/-- King adjacency, with the absolute values opened for `omega`. -/
lemma kingAdj_iff' {p q : ℤ × ℤ} :
    kingAdj p q ↔ (p.1 ≠ q.1 ∨ p.2 ≠ q.2) ∧
      -1 ≤ p.1 - q.1 ∧ p.1 - q.1 ≤ 1 ∧ -1 ≤ p.2 - q.2 ∧ p.2 - q.2 ≤ 1 := by
  simp only [kingAdj, abs_le, ne_eq, Prod.ext_iff, not_and_or, and_assoc]

/-- King paths reverse: the step relation is symmetric, so its reflexive
transitive closure is. -/
lemma reflTransGen_symm {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q) :
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) q p := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | @tail b c _ hbc ih =>
      exact Relation.ReflTransGen.head ⟨hbc.2.1, hbc.1, kingAdj_symm hbc.2.2⟩ ih

lemma kingConnected_singleton (p : ℤ × ℤ) : KingConnected {p} := by
  intro x hx y hy
  rw [Finset.mem_singleton] at hx hy
  subst hx hy
  exact Relation.ReflTransGen.refl

/-- **Gluing two connected sets across one king edge.** Paths inside either half
lift into the union (the step predicate only weakens), and the bridge edge
`x₀ → y₀` — traversable in both directions, king adjacency being symmetric —
routes between the halves. -/
lemma kingConnected_union_of_adj {X Y : Finset (ℤ × ℤ)} {x₀ y₀ : ℤ × ℤ}
    (hX : KingConnected X) (hY : KingConnected Y) (hx₀ : x₀ ∈ X) (hy₀ : y₀ ∈ Y)
    (hadj : kingAdj x₀ y₀) : KingConnected (X ∪ Y) := by
  have liftX : ∀ p ∈ X, ∀ q ∈ X,
      Relation.ReflTransGen (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) p q :=
    fun p hp q hq => (hX p hp q hq).mono fun a b hab =>
      ⟨Finset.mem_union_left _ hab.1, Finset.mem_union_left _ hab.2.1, hab.2.2⟩
  have liftY : ∀ p ∈ Y, ∀ q ∈ Y,
      Relation.ReflTransGen (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) p q :=
    fun p hp q hq => (hY p hp q hq).mono fun a b hab =>
      ⟨Finset.mem_union_right _ hab.1, Finset.mem_union_right _ hab.2.1, hab.2.2⟩
  have bridge : (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) x₀ y₀ :=
    ⟨Finset.mem_union_left _ hx₀, Finset.mem_union_right _ hy₀, hadj⟩
  have bridge' : (fun a b => a ∈ X ∪ Y ∧ b ∈ X ∪ Y ∧ kingAdj a b) y₀ x₀ :=
    ⟨Finset.mem_union_right _ hy₀, Finset.mem_union_left _ hx₀, kingAdj_symm hadj⟩
  intro p hp q hq
  rcases Finset.mem_union.mp hp with hp | hp <;> rcases Finset.mem_union.mp hq with hq | hq
  · exact liftX p hp q hq
  · exact ((liftX p hp x₀ hx₀).tail bridge).trans (liftY y₀ hy₀ q hq)
  · exact ((liftY p hp y₀ hy₀).tail bridge').trans (liftX x₀ hx₀ q hq)
  · exact liftY p hp q hq

/-- Inserting a cell adjacent to a connected set keeps it connected. -/
lemma kingConnected_insert {W : Finset (ℤ × ℤ)} {w q : ℤ × ℤ} (hW : KingConnected W)
    (hw : w ∈ W) (hadj : kingAdj w q) : KingConnected (insert q W) := by
  rw [Finset.insert_eq]
  exact kingConnected_union_of_adj (kingConnected_singleton q) hW (Finset.mem_singleton_self q)
    hw (kingAdj_symm hadj)

/-- Along a path in `S` from a cell satisfying `P` to one that does not, some
king step leaves `P`. -/
lemma exists_edge_of_connected {S : Finset (ℤ × ℤ)} (hS : KingConnected S)
    (P : ℤ × ℤ → Prop) {p q : ℤ × ℤ} (hp : p ∈ S) (hq : q ∈ S) (hPp : P p)
    (hPq : ¬ P q) :
    ∃ a ∈ S, ∃ b ∈ S, P a ∧ ¬ P b ∧ kingAdj a b := by
  have key : ∀ r, Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p r →
      ¬ P r → ∃ a ∈ S, ∃ b ∈ S, P a ∧ ¬ P b ∧ kingAdj a b := by
    intro r hr
    induction hr with
    | refl => exact fun h => absurd hPp h
    | @tail b c _ hbc ih =>
        intro hc
        by_cases hb : P b
        · exact ⟨b, hbc.1, c, hbc.2.1, hb, hc, hbc.2.2⟩
        · exact ih hb
  exact key q (hS p hp q hq) hPq

/-! ## King paths skip no column -/

/-- **King paths don't skip a column**: `RowLocal.exists_proj_eq_of_cross` at
`Prod.fst`, which a king step moves by at most one. -/
lemma exists_x_eq_of_cross {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : p.1 ≤ k) (hq : k + 1 ≤ q.1) : ∃ c ∈ S, c.1 = k :=
  RowLocal.exists_proj_eq_of_cross Prod.fst (fun _ _ hab => hab.2.1) h hp hq

/-! ## Polyplets, and the two counts `a` and `T` -/

/-- `S` is a polyplet of `n` cells, as the representative of its translation
class whose bounding box has its corner at the origin: `n` cells, king-connected,
`Anchored` (min x = min y = 0). This is the report's fixed polyplet of size `n`;
`a n` counts these. -/
structure IsPolyplet (n : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `n` cells. -/
  card : S.card = n
  /-- King-connected. -/
  conn : KingConnected S
  /-- Bounding box at the origin. -/
  anchored : Anchored S

/-- `IsPolyplet` as a conjunction (for decidability and for unfolding). -/
lemma isPolyplet_iff_and {n : ℕ} {S : Finset (ℤ × ℤ)} :
    IsPolyplet n S ↔ S.card = n ∧ KingConnected S ∧
      (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧ (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0) :=
  ⟨fun h => ⟨h.card, h.conn, h.anchored.x_nonneg, h.anchored.x_zero, h.anchored.y_nonneg,
    h.anchored.y_zero⟩,
   fun ⟨a, b, c, d, e, f⟩ => ⟨a, b, ⟨c, d, e, f⟩⟩⟩

/-- A polyplet is nonempty (column `0` is occupied). -/
lemma IsPolyplet.nonempty {n : ℕ} {S : Finset (ℤ × ℤ)} (hS : IsPolyplet n S) : S.Nonempty :=
  hS.anchored.nonempty

/-- The polyplets of `n` cells, as a set of cell sets. -/
def polyplets (n : ℕ) : Set (Finset (ℤ × ℤ)) := {S | IsPolyplet n S}

lemma mem_polyplets {n : ℕ} {S : Finset (ℤ × ℤ)} : S ∈ polyplets n ↔ IsPolyplet n S := Iff.rfl

/-- `a n`: the number of fixed polyplets of `n` cells (A006770). `Set.ncard`
returns the junk value `0` on infinite sets; `polyplets_finite`
(`Sequence.lean`) shows that never happens. `a 0 = 0`: the empty set is not
anchored, so every statement about `a` carries `1 ≤ n`. -/
noncomputable def a (n : ℕ) : ℕ := (polyplets n).ncard

/-- The bounding-box height of a cell set: one more than the largest
y-coordinate. Through `Int.toNat`, so that it is a total `ℕ`-valued function;
on a polyplet every y-coordinate is `≥ 0`, so nothing is lost. -/
def height (S : Finset (ℤ × ℤ)) : ℕ := S.sup (fun p => p.2.toNat) + 1

/-- Heights are positive, definitionally. -/
lemma one_le_height (S : Finset (ℤ × ℤ)) : 1 ≤ height S := Nat.le_add_left 1 _

/-- The polyplets of `n` cells whose bounding box has height `H`. -/
def heightClass (n H : ℕ) : Set (Finset (ℤ × ℤ)) := {S | IsPolyplet n S ∧ height S = H}

lemma mem_heightClass {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ heightClass n H ↔ IsPolyplet n S ∧ height S = H := Iff.rfl

/-- `T n H`: the number of fixed polyplets of `n` cells whose bounding box has
height exactly `H`. Finiteness is `heightClass_finite` (`Sequence.lean`), so
`Set.ncard`'s junk value never arises for the intended `n, H`. -/
noncomputable def T (n H : ℕ) : ℕ := (heightClass n H).ncard

/-- `{(0, 0)}` is the only polyplet of one cell. -/
lemma isPolyplet_one_iff {S : Finset (ℤ × ℤ)} :
    IsPolyplet 1 S ↔ S = {((0 : ℤ), (0 : ℤ))} := by
  constructor
  · intro h
    obtain ⟨p, hp⟩ := Finset.card_eq_one.mp h.card
    obtain ⟨q, hq, hq1⟩ := h.anchored.x_zero
    obtain ⟨r, hr, hr2⟩ := h.anchored.y_zero
    rw [hp, Finset.mem_singleton] at hq hr
    rw [hp]
    congr 1
    exact Prod.ext (hq ▸ hq1) (hr ▸ hr2)
  · rintro rfl
    refine ⟨Finset.card_singleton _, kingConnected_singleton _, ?_⟩
    · refine ⟨fun p hp => ?_, ⟨_, Finset.mem_singleton_self _, rfl⟩, fun p hp => ?_,
        ⟨_, Finset.mem_singleton_self _, rfl⟩⟩ <;>
      · rw [Finset.mem_singleton] at hp
        subst hp
        exact le_rfl

/-- `T 1 1 = 1`: the single cell `{(0, 0)}` is the only one-cell polyplet.
The seed of the `k = 0` diagonal (`King.lean`). -/
theorem T_1_1 : T 1 1 = 1 := by
  rw [T, Set.ncard_eq_one]
  refine ⟨{(0, 0)}, Set.ext fun S => ?_⟩
  simp only [mem_heightClass, isPolyplet_one_iff, Set.mem_singleton_iff]
  exact ⟨And.left, fun h => ⟨h, by subst h; simp [height]⟩⟩

end Polyplets
