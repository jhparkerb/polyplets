/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkRows

/-!
# Notary piece K, module 1: closed-form values of the gap-walk rows

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md` — the kernel method
at all orders. `GapWalkRows.lean` proved the *vanishing* facts about
`stepMul`; this module proves the **values**: the generic rows at `g ≥ 3`
(bulk `(1,2,3,2,1)` kernel, `J`-background `8/2/8/12`, fold-downs at
`gp ≤ 2`), the four boundary rows `g ≤ 2` (finite heads plus uniform
tails), and the start vector. These are the closed-form transition rows the
functional equations of the kernel derivation read off; piece T priced them
as K's cost center and never consumed them — K does.

Every statement here was verified numerically before this skeleton was
written: `experiments/notary_k_measure.py` m1 checks the claimed closed
forms against `depth1_gap_walk.transitions` for `g ≤ 29`, `gp ≤ 60`
(`build/notary_k_measure.log`), and `build/notary_k_rowvals_check.lean`
re-evaluates the Lean `stepMul` itself over the same grid.

## Proof recipe

`stepMul g c gp c'` is `(List.range (g + gp + 5)).filter p |>.length` where
`p` is a Bool combination of window tests `near t = (t.natAbs ≤ 1)` in the
placement `a := (i : ℤ) − (gp + 2)`. Each `near` is an interval in `i`; the
satisfying set of every lemma below is a union of at most three disjoint
intervals whose endpoints are affine in `g`, `gp`. Two helpers reduce
counting to arithmetic:

* `length_filter_range_interval` — a single-interval count over
  `List.range`;
* `length_filter_congr_disjoint` — split a predicate into a disjoint
  Bool-disjunction of interval predicates (`List.filter_congr` pointwise,
  discharged by `omega` after `simp only [near, joined, ...]`, then
  `List.length_filter_add`-style bookkeeping via
  `List.countP_eq_length_filter` if convenient).

For the literal boundary statements (`g ≤ 2`, `gp ≤ 4`) everything is a
closed computation: `decide`.

The bulk weight is `bulkW g gp = 3 − |gp − g|` clipped at distance 2; the
identities `8 − bulkW g 1`, `2 + bulkW g 2`, `12 − 2·bulkW g gp` below are
exactly `generic_row` of `experiments/severance_w2_kernel.py` (asserted
against the walk in its stage 0).
-/

namespace Polyplets
namespace GapWalk

/-- The bulk kernel weight `(1,2,3,2,1)`: `3 − |gp − g|` at distance `≤ 2`,
else `0`. -/
def bulkW (g gp : ℕ) : ℕ :=
  if ((gp : ℤ) - g).natAbs ≤ 2 then 3 - ((gp : ℤ) - g).natAbs else 0

/-! ## Counting helpers -/

/-- Counting an interval inside `List.range`. -/
theorem length_filter_range_interval (N lo hi : ℕ) :
    ((List.range N).filter fun i => decide (lo ≤ i ∧ i < hi)).length =
      min hi N - min lo N := by
  sorry

/-! ## Target gap 1 is always class `J` -/

/-- A landing on gap 1 is reclassified `J` unconditionally: the `P` variant
is empty, every source. -/
theorem stepMul_to_1_P (g : ℕ) (c : Bool) : stepMul g c 1 false = 0 := by
  sorry

/-! ## The generic `P` row, `g ≥ 3` -/

/-- Bulk kernel: a pending pair at gap `g ≥ 3` moves to gap `gp ≥ 2`
(staying `P`) in exactly `bulkW g gp` ways. -/
theorem stepMul_P_bulk (g gp : ℕ) (hg : 3 ≤ g) (hgp : 2 ≤ gp) :
    stepMul g false gp false = bulkW g gp := by
  sorry

/-- The unique generic join: gap 3 folding onto gap 1. -/
theorem stepMul_P3_join : stepMul 3 false 1 true = 1 := by
  sorry

/-- A pending pair at gap `g ≥ 3` never lands joined at gap 2. -/
theorem stepMul_P_to_J2 (g : ℕ) (hg : 3 ≤ g) :
    stepMul g false 2 true = 0 := by
  sorry

/-! ## The generic `J` row, `g ≥ 3` -/

/-- Joined source to gap 1: background 8, minus the bulk fold at `g = 3`. -/
theorem stepMul_J_to_1J (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 1 true = 8 - bulkW g 1 := by
  sorry

/-- Joined source to `(2, J)`: background 2 plus the bulk block. -/
theorem stepMul_J_to_2J (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 2 true = 2 + bulkW g 2 := by
  sorry

/-- Joined source to `(2, P)`: background 8 minus twice the bulk block. -/
theorem stepMul_J_to_2P (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 2 false = 8 - 2 * bulkW g 2 := by
  sorry

/-- Joined source to a joined target at gap `≥ 3`: the bulk block alone. -/
theorem stepMul_J_bulk (g gp : ℕ) (hg : 3 ≤ g) (hgp : 3 ≤ gp) :
    stepMul g true gp true = bulkW g gp := by
  sorry

/-- The rank-one spray: a joined source reaches every `(gp, P)`, `gp ≥ 3`,
with weight 12, corrected by `−2·bulkW` inside the bulk window. -/
theorem stepMul_J_spray (g gp : ℕ) (hg : 3 ≤ g) (hgp : 3 ≤ gp) :
    stepMul g true gp false = 12 - 2 * bulkW g gp := by
  sorry

/-! ## The four boundary rows: heads (literal) and tails (symbolic)

Heads from `severance_w2_kernel.BOUNDARY`, asserted against the walk by its
stage 0 and by m1. -/

theorem stepMul_1J_1J : stepMul 1 true 1 true = 5 := by sorry
theorem stepMul_1J_2J : stepMul 1 true 2 true = 2 := by sorry
theorem stepMul_1J_2P : stepMul 1 true 2 false = 4 := by sorry
theorem stepMul_1J_3J : stepMul 1 true 3 true = 1 := by sorry
theorem stepMul_1J_3P : stepMul 1 true 3 false = 6 := by sorry

/-- Row `(1, J)` tail: weight 8 to every `(gp, P)`, `gp ≥ 4`. -/
theorem stepMul_1J_tail (gp : ℕ) (h : 4 ≤ gp) :
    stepMul 1 true gp false = 8 := by
  sorry

theorem stepMul_2J_1J : stepMul 2 true 1 true = 6 := by sorry
theorem stepMul_2J_2J : stepMul 2 true 2 true = 3 := by sorry
theorem stepMul_2J_2P : stepMul 2 true 2 false = 4 := by sorry
theorem stepMul_2J_3J : stepMul 2 true 3 true = 2 := by sorry
theorem stepMul_2J_3P : stepMul 2 true 3 false = 6 := by sorry
theorem stepMul_2J_4J : stepMul 2 true 4 true = 1 := by sorry
theorem stepMul_2J_4P : stepMul 2 true 4 false = 8 := by sorry

/-- Row `(2, J)` tail: weight 10 to every `(gp, P)`, `gp ≥ 5`. -/
theorem stepMul_2J_tail (gp : ℕ) (h : 5 ≤ gp) :
    stepMul 2 true gp false = 10 := by
  sorry

theorem stepMul_1P_1J : stepMul 1 false 1 true = 3 := by sorry
theorem stepMul_1P_2J : stepMul 1 false 2 true = 2 := by sorry
theorem stepMul_1P_2P : stepMul 1 false 2 false = 2 := by sorry
theorem stepMul_1P_3P : stepMul 1 false 3 false = 5 := by sorry

/-- Row `(1, P)` tail: weight 4 to every `(gp, P)`, `gp ≥ 4`. -/
theorem stepMul_1P_tail (gp : ℕ) (h : 4 ≤ gp) :
    stepMul 1 false gp false = 4 := by
  sorry

theorem stepMul_2P_1J : stepMul 2 false 1 true = 2 := by sorry
theorem stepMul_2P_2J : stepMul 2 false 2 true = 2 := by sorry
theorem stepMul_2P_2P : stepMul 2 false 2 false = 1 := by sorry
theorem stepMul_2P_3P : stepMul 2 false 3 false = 4 := by sorry
theorem stepMul_2P_4P : stepMul 2 false 4 false = 3 := by sorry

/-- Row `(2, P)` tail: weight 2 to every `(gp, P)`, `gp ≥ 5`. -/
theorem stepMul_2P_tail (gp : ℕ) (h : 5 ≤ gp) :
    stepMul 2 false gp false = 2 := by
  sorry

/-! ## The start vectors -/

theorem startCount_1J : startCount (1, true) = 4 := by sorry
theorem startCount_1P : startCount (1, false) = 0 := by sorry
theorem startCount_2J : startCount (2, true) = 1 := by sorry
theorem startCount_2P : startCount (2, false) = 4 := by sorry

/-- The interior start's `P`-tail: 6 placements at every gap `g ≥ 3`. -/
theorem startCount_P_deep (g : ℕ) (hg : 3 ≤ g) :
    startCount (g, false) = 6 := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.stepMul_J_spray' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms stepMul_J_spray

/--
info: 'Polyplets.GapWalk.stepMul_P_bulk' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms stepMul_P_bulk

end GapWalk
end Polyplets
