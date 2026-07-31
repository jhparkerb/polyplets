/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.Defs

/-!
# The lattice graph of a cell set: bridge to mathlib's `SimpleGraph`

`Universal/Defs.lean` states `L`-connectivity of a finite cell set `S` via
`Relation.ReflTransGen`. The walk surgery ahead (the separation lemma, the width
bound, the peeling bijections) wants mathlib's `SimpleGraph.Walk` API —
`dropUntil`, boundary darts, `toPath` — so this file packages the step relation
as a `SimpleGraph` on `ℤ × ℤ` (`graph L S`, adjacency definitionally the step
relation) and proves the two connectivity notions coincide
(`conn_iff_reachable`).

This is `Graph.lean` with `kingAdj ↦ Adj L`.
-/

namespace Polyplets.Universal

/-- The `L`-graph induced by `S`: vertices are all of `ℤ × ℤ`, and two cells are
adjacent iff both lie in `S` and are `L`-adjacent. `Adj` is definitionally the
step relation of `Conn`. -/
def graph (L : RowLocal) (S : Finset (ℤ × ℤ)) : SimpleGraph (ℤ × ℤ) where
  Adj a b := a ∈ S ∧ b ∈ S ∧ Adj L a b
  symm := ⟨fun _ _ h => ⟨h.2.1, h.1, adj_symm h.2.2⟩⟩
  loopless := ⟨fun _ h => h.2.2.1 rfl⟩

/-- `graph` adjacency, unfolded. -/
lemma graph_adj {L : RowLocal} {S : Finset (ℤ × ℤ)} {a b : ℤ × ℤ} :
    (graph L S).Adj a b ↔ a ∈ S ∧ b ∈ S ∧ Adj L a b := Iff.rfl

/-- **The bridge.** `Conn L S` is pairwise `Reachable` in `graph L S`: the
`ReflTransGen` of `Universal/Defs.lean` is literally
`ReflTransGen (graph L S).Adj`. -/
theorem conn_iff_reachable (L : RowLocal) (S : Finset (ℤ × ℤ)) :
    Conn L S ↔ ∀ p ∈ S, ∀ q ∈ S, (graph L S).Reachable p q := by
  unfold Conn
  constructor
  · intro h p hp q hq
    rw [SimpleGraph.reachable_iff_reflTransGen]
    exact h p hp q hq
  · intro h p hp q hq
    have hpq := h p hp q hq
    rwa [SimpleGraph.reachable_iff_reflTransGen] at hpq

/-- **Walks stay inside `S`.** Every vertex on a `graph L S`-walk starting
inside `S` lies in `S`. -/
lemma mem_of_mem_walk_support {L : RowLocal} {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (hp : p ∈ S) (w : (graph L S).Walk p q) : ∀ v ∈ w.support, v ∈ S := by
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

end Polyplets.Universal
