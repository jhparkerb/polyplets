/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Defs

/-!
# The king graph of a cell set: bridge to mathlib's `SimpleGraph`

`Defs.lean` states king-connectivity of a finite cell set `S` via
`Relation.ReflTransGen` of the step relation "both endpoints in `S` and
king-adjacent". The walk surgery ahead (the separation lemma, the peeling
bijections) wants mathlib's `SimpleGraph.Walk` API — `dropUntil`, boundary
darts — so this file packages the step relation as a `SimpleGraph` on `ℤ × ℤ`
(`kingGraph S`, adjacency definitionally the step relation) and proves the two
connectivity notions coincide (`kingConnected_iff_reachable`).
-/

namespace Polyplets

/-- King adjacency is symmetric. -/
lemma kingAdj_symm {p q : ℤ × ℤ} (h : kingAdj p q) : kingAdj q p :=
  ⟨h.1.symm, by rw [abs_sub_comm]; exact h.2.1, by rw [abs_sub_comm]; exact h.2.2⟩

/-- The king graph induced by `S`: vertices are all of `ℤ × ℤ`, and two cells
are adjacent iff both lie in `S` and are king-adjacent. `Adj` is definitionally
the step relation of `KingConnected`. -/
def kingGraph (S : Finset (ℤ × ℤ)) : SimpleGraph (ℤ × ℤ) where
  Adj a b := a ∈ S ∧ b ∈ S ∧ kingAdj a b
  symm := ⟨fun _ _ h => ⟨h.2.1, h.1, kingAdj_symm h.2.2⟩⟩
  loopless := ⟨fun _ h => h.2.2.1 rfl⟩

/-- `kingGraph` adjacency, unfolded. -/
lemma kingGraph_adj {S : Finset (ℤ × ℤ)} {a b : ℤ × ℤ} :
    (kingGraph S).Adj a b ↔ a ∈ S ∧ b ∈ S ∧ kingAdj a b := Iff.rfl

/-- **The bridge.** `KingConnected S` is pairwise `Reachable` in `kingGraph S`:
the `ReflTransGen` of `Defs.lean` is literally `ReflTransGen (kingGraph S).Adj`,
which mathlib identifies with `Reachable`
(`SimpleGraph.reachable_iff_reflTransGen`). -/
theorem kingConnected_iff_reachable (S : Finset (ℤ × ℤ)) :
    KingConnected S ↔ ∀ p ∈ S, ∀ q ∈ S, (kingGraph S).Reachable p q := by
  unfold KingConnected
  constructor
  · intro h p hp q hq
    rw [SimpleGraph.reachable_iff_reflTransGen]
    exact h p hp q hq
  · intro h p hp q hq
    have hpq := h p hp q hq
    rwa [SimpleGraph.reachable_iff_reflTransGen] at hpq

/-- **Walks stay inside `S`.** Every vertex on a `kingGraph S`-walk starting
inside `S` lies in `S`: the start is given, and every edge endpoint is in `S`
by adjacency. -/
lemma mem_of_mem_walk_support {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} (hp : p ∈ S)
    (w : (kingGraph S).Walk p q) : ∀ v ∈ w.support, v ∈ S := by
  revert hp
  induction w with
  | nil =>
    intro hp v hv
    rw [SimpleGraph.Walk.support_nil, List.mem_singleton] at hv
    exact hv ▸ hp
  | cons hadj w ih =>
    intro hp v hv
    rw [SimpleGraph.Walk.support_cons, List.mem_cons] at hv
    rcases hv with rfl | hv
    · exact hp
    · exact ih hadj.2.1 v hv

end Polyplets
