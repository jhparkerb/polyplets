/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalk

/-!
# Notary piece T, module 2: the walk as an iterated state function

Campaign *Notary*, piece **T** of `docs/notary-kernel-scoping.md` — truncation
exactness. `GapWalk.lean` runs the DP on association lists aligned with
`states gmax`; comparing two caps on that representation is painful. This
module rewrites the walk as iteration of a *function* `St → ℕ`:

* `canon cap F` — the association list of `F` over `states cap`; every list
  the walk ever touches has this shape;
* `funStep cap F` — one DP step as a function transformer;
* `iter cap F l` — `l` steps of the walk from start `F`;
* `qEndF` / `bareEndF` — the end functionals on the canonical list;
* `walkAux_canon` — the emitted family triples are exactly the end
  functionals of the iterates, `l = 0 .. n − 1`.

Then the cap-comparison toolkit: sums over `states (M + k)` split into the
`states M` part plus the `k` extra gaps (`funStep_split`), the split
collapses when every extra term dies (`*_split_zero`), and two value
functions that agree wherever the functional looks give equal outputs
(`*_congr`). Nothing here mentions the walk's geometry; every proof is list
bookkeeping (`List.map_map`, `List.range_add` / induction on `k`,
`List.sum_append`, congruence of `List.map` over a common index list).
-/

namespace Polyplets
namespace GapWalk

/-! ## The canonical representation -/

/-- The association list of the value function `F` over `states cap` —
the shape of every DP list the walk touches. -/
def canon (cap : Nat) (F : St → Nat) : List (St × Nat) :=
  (states cap).map fun s => (s, F s)

/-- One walk step as a function transformer: the value landing on target
`t`, summed over all sources below the cap. -/
def funStep (cap : Nat) (F : St → Nat) (t : St) : Nat :=
  ((states cap).map fun s => F s * stepMul s.1 s.2 t.1 t.2).sum

/-- `l` walk steps from start `F`, at cap `cap`. -/
def iter (cap : Nat) (F : St → Nat) : Nat → St → Nat
  | 0 => F
  | l + 1 => funStep cap (iter cap F l)

/-- `qEnd` on the canonical list. -/
def qEndF (cap : Nat) (F : St → Nat) : Nat := qEnd (canon cap F)

/-- `bareEnd` on the canonical list. -/
def bareEndF (cap : Nat) (F : St → Nat) : Nat := bareEnd (canon cap F)

/-! ## The walk in canonical form -/

theorem mem_states (cap g : Nat) (c : Bool) :
    (g, c) ∈ states cap ↔ 1 ≤ g ∧ g ≤ cap := by
  sorry

theorem stepDP_canon (cap : Nat) (F : St → Nat) :
    stepDP cap (canon cap F) = canon cap (funStep cap F) := by
  sorry

/-- The families the walk emits are the end functionals of the iterates. -/
theorem walkAux_canon (n cap : Nat) (F G : St → Nat) :
    walkAux n cap (canon cap F) (canon cap G) =
      (List.range n).map fun l =>
        (qEndF cap (iter cap F l), qEndF cap (iter cap G l),
         bareEndF cap (iter cap G l)) := by
  sorry

/-! ## Splitting a larger cap -/

/-- A `funStep` at cap `M + k` is the cap-`M` sum plus the `k` extra gaps. -/
theorem funStep_split (M k : Nat) (F : St → Nat) (t : St) :
    funStep (M + k) F t = funStep M F t +
      ((List.range k).map fun i =>
        F (M + i + 1, true) * stepMul (M + i + 1) true t.1 t.2 +
        F (M + i + 1, false) * stepMul (M + i + 1) false t.1 t.2).sum := by
  sorry

/-- The split collapses when every extra term dies. -/
theorem funStep_split_zero (M k : Nat) (F : St → Nat) (t : St)
    (h : ∀ i, i < k →
      F (M + i + 1, true) * stepMul (M + i + 1) true t.1 t.2 = 0 ∧
      F (M + i + 1, false) * stepMul (M + i + 1) false t.1 t.2 = 0) :
    funStep (M + k) F t = funStep M F t := by
  sorry

/-- `qEndF` ignores extra gaps carrying no `J`-mass: above gap 2 the `P`
branch of `qEnd` weighs 0, and the `J` branch is multiplied by zero. -/
theorem qEndF_split_zero (M k : Nat) (F : St → Nat) (h2 : 2 ≤ M)
    (h : ∀ i, i < k → F (M + i + 1, true) = 0) :
    qEndF (M + k) F = qEndF M F := by
  sorry

/-- `bareEndF` ignores extra gaps carrying no `J`-mass. -/
theorem bareEndF_split_zero (M k : Nat) (F : St → Nat)
    (h : ∀ i, i < k → F (M + i + 1, true) = 0) :
    bareEndF (M + k) F = bareEndF M F := by
  sorry

/-! ## Congruence over a common cap -/

/-- Term-by-term congruence for one step onto a fixed target: sources where
the values differ contribute nothing if their multiplicity is zero. -/
theorem funStep_congr (cap : Nat) (F G : St → Nat) (t : St)
    (h : ∀ g c, 1 ≤ g → g ≤ cap →
      F (g, c) = G (g, c) ∨ stepMul g c t.1 t.2 = 0) :
    funStep cap F t = funStep cap G t := by
  sorry

/-- `qEndF` reads `J` everywhere and `P` only at gaps `≤ 2`. -/
theorem qEndF_congr (cap : Nat) (F G : St → Nat)
    (hJ : ∀ g, 1 ≤ g → g ≤ cap → F (g, true) = G (g, true))
    (hP : ∀ g, 1 ≤ g → g ≤ 2 → F (g, false) = G (g, false)) :
    qEndF cap F = qEndF cap G := by
  sorry

/-- `bareEndF` reads only `J`. -/
theorem bareEndF_congr (cap : Nat) (F G : St → Nat)
    (hJ : ∀ g, 1 ≤ g → g ≤ cap → F (g, true) = G (g, true)) :
    bareEndF cap F = bareEndF cap G := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) and new `axiom` declarations are out of bounds. -/

/--
info: 'Polyplets.GapWalk.walkAux_canon' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
-/
#guard_msgs in
#print axioms walkAux_canon

/--
info: 'Polyplets.GapWalk.funStep_split_zero' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
-/
#guard_msgs in
#print axioms funStep_split_zero

end GapWalk
end Polyplets
