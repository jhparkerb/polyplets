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

export Universal (Anchored)

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

end Polyplets
