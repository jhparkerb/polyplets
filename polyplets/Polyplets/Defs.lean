/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Data.Set.Card
import Polyplets.Universal.Defs

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

export Universal (Anchored translate mem_translate translate_mem translate_translate translate_zero
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

/-- `S` is the canonical (origin-anchored) representative of a fixed polyplet of
`n` cells with bounding-box height exactly `H`: it has `n` cells, is
king-connected, its bounding box sits at the origin (`Anchored`), and its
maximum y-coordinate is `H - 1` (so the y-extent is exactly `H`). The x-extent
(width) is unconstrained. -/
structure IsCanonical (n H : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `n` cells. -/
  card : S.card = n
  /-- King-connected. -/
  conn : KingConnected S
  /-- Bounding box at the origin. -/
  anchored : Anchored S
  /-- No cell above row `H - 1`. -/
  y_le : ∀ p ∈ S, p.2 ≤ (H : ℤ) - 1
  /-- Row `H - 1` is occupied. -/
  y_top : ∃ p ∈ S, p.2 = (H : ℤ) - 1

/-- `IsCanonical` as a conjunction (for decidability and for unfolding). -/
lemma isCanonical_iff_and {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    IsCanonical n H S ↔ S.card = n ∧ KingConnected S ∧
      (∀ p ∈ S, 0 ≤ p.1) ∧ (∃ p ∈ S, p.1 = 0) ∧
      (∀ p ∈ S, 0 ≤ p.2) ∧ (∃ p ∈ S, p.2 = 0) ∧
      (∀ p ∈ S, p.2 ≤ (H : ℤ) - 1) ∧ (∃ p ∈ S, p.2 = (H : ℤ) - 1) :=
  ⟨fun h => ⟨h.card, h.conn, h.anchored.x_nonneg, h.anchored.x_zero, h.anchored.y_nonneg,
    h.anchored.y_zero, h.y_le, h.y_top⟩,
   fun ⟨a, b, c, d, e, f, g, i⟩ => ⟨a, b, ⟨c, d, e, f⟩, g, i⟩⟩

/-- `T n H`: the number of fixed polyplets of `n` cells whose bounding box has
height exactly `H`, i.e. the number of origin-anchored canonical
representatives. `Set.ncard` returns `0` on the infinite case, which never
arises for the intended `n, H` (finiteness is proved where a theorem needs it).
-/
noncomputable def T (n H : ℕ) : ℕ :=
  {S : Finset (ℤ × ℤ) | IsCanonical n H S}.ncard

/-- `T 1 1 = 1`: the single cell `{(0, 0)}` is the only one-cell canonical set.
The seed of the `k = 0` diagonal (`King.lean`). -/
theorem T_1_1 : T 1 1 = 1 := by
  rw [T, Set.ncard_eq_one]
  refine ⟨{(0, 0)}, Set.ext fun S => ?_⟩
  simp only [Set.mem_setOf_eq, Set.mem_singleton_iff]
  constructor
  · intro h
    obtain ⟨p, hp⟩ := Finset.card_eq_one.mp h.card
    obtain ⟨q, hq, hq1⟩ := h.anchored.x_zero
    obtain ⟨r, hr, hr2⟩ := h.anchored.y_zero
    rw [hp, Finset.mem_singleton] at hq hr
    rw [hq] at hq1
    rw [hr] at hr2
    rw [hp, show p = (0, 0) from Prod.ext hq1 hr2]
  · rintro rfl
    exact ⟨rfl, kingConnected_singleton _,
      ⟨by simp, ⟨(0, 0), by simp⟩, by simp, ⟨(0, 0), by simp⟩⟩, by simp, ⟨(0, 0), by simp⟩⟩

end Polyplets
