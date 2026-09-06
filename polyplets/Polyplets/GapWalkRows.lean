/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalk

/-!
# Notary piece T, module 1: vanishing rows of the gap-walk transition table

Campaign *Notary*, piece **T** of `docs/notary-kernel-scoping.md (deleted)` — truncation
exactness. This module proves the four **vanishing** facts about `stepMul`
that the truncation argument consumes, plus the support of the two start
vectors. No closed-form row values are computed here (those belong to piece
K); every statement says a multiplicity is *zero*.

The four `stepMul` facts, each verified numerically for `g ≤ 40`, `gp ≤ 80`
against `experiments/depth1_gap_walk.py::transitions` before this skeleton
was written:

* `stepMul_P_to_J` — a `P` source never produces a `J` state at gap `≥ 3`:
  joining the two pending components needs both new cells in contact range,
  which forces the new gap `≤ 2`.
* `stepMul_P_far_to_J` — a `P` source at gap `≥ 4` never joins at all: the
  only generic join is the bulk `g → g − 2 = 1` move, which needs `g = 3`.
* `stepMul_P_local` — a `P` source at gap `g ≥ 3` only reaches gaps in
  `[g − 2, g + 2]` (either class): the new row must touch both components,
  pinning its two cells to the two contact windows.
* `stepMul_J_to_J_far` — a `J` target at gap `gp ≥ 3` needs its source
  within two below: `gp ≤ g + 2`. (The unbounded `J → P` spray at weight 12
  is class `P` and is not constrained here.)

## Proof recipe (per lemma)

`stepMul` (and `startCount`) is the length of a `List.filter` over
`List.range`; a zero statement says the predicate is false at every index:

    rw [stepMul]
    rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
    intro i hi
    simp only [near, joined, ...]   -- expose the Bool structure
    -- everything is linear arithmetic in ℤ over a := (i : ℤ) − (gp + 2)
    -- with `Int.natAbs`; split the ifs / Bool connectives, then `omega`

`omega` handles `Int.natAbs` directly. Lemma names for the Bool unfolding:
`Bool.and_eq_true`, `Bool.or_eq_true`, `beq_iff_eq`, `decide_eq_true_eq`;
`split_ifs` for the `if gp = 1` / `if cJ` branches. Mind that `hi` gives
`i < g + gp + 5`, which is *not needed* for the zero lemmas — the predicate
is false for every integer `a`, so never mind the range bound.
-/

namespace Polyplets
namespace GapWalk

/-! ## The `stepMul` vanishing lemmas -/

/-- From a pending-components source, a joined state at gap `≥ 3` is
unreachable: `x ∼ y` needs `x` and `y` in a common contact window, forcing
the new gap `≤ 2` (and `gp = 1` is below 3 anyway). Holds for every source
gap `g`, boundary rows included. -/
theorem stepMul_P_to_J (g gp : Nat) (h : 3 ≤ gp) :
    stepMul g false gp true = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
    decide_eq_true_eq, if_neg (by omega : ¬ gp = 1),
    if_neg (show (false = true) → False by decide)]
  omega

/-- From a pending-components source at gap `≥ 4`, no placement joins: the
generic `P` row's only `J` entry is the bulk move to gap `g − 2 = 1`. Holds
for every target gap `gp`. -/
theorem stepMul_P_far_to_J (g gp : Nat) (h : 4 ≤ g) :
    stepMul g false gp true = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  by_cases hgp1 : gp = 1
  · simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
      decide_eq_true_eq, if_pos hgp1,
      if_neg (show (false = true) → False by decide)]
    omega
  · simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
      decide_eq_true_eq, if_neg hgp1,
      if_neg (show (false = true) → False by decide)]
    omega

/-- Locality of the generic `P` row: a source at gap `g ≥ 3` reaches only
gaps in `[g − 2, g + 2]`, either class — the new row must touch both
pending components, whose contact windows sit `g` apart. -/
theorem stepMul_P_local (g gp : Nat) (c : Bool) (hg : 3 ≤ g)
    (h : gp + 2 < g ∨ g + 2 < gp) :
    stepMul g false gp c = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
    decide_eq_true_eq,
    if_neg (show (false = true) → False by decide)]
  split_ifs <;> omega

/-- A joined target at gap `gp ≥ 3` needs its source within two below:
both new cells must sit in contact windows, and those windows span
`[−1, g + 1]`, so `gp ≤ g + 2`. -/
theorem stepMul_J_to_J_far (g gp : Nat) (hgp : 3 ≤ gp) (h : g + 2 < gp) :
    stepMul g true gp true = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
    decide_eq_true_eq, if_neg (by omega : ¬ gp = 1),
    if_true]
  omega

/-! ## The start vectors as cap-independent state functions

`startInterior gmax` / `startBare gmax` assign each state a value that does
not depend on `gmax`; naming those per-state functions lets the truncation
module compare walks at different caps over a common start. -/

/-- The per-state interior start count (`dp_int` of the reference): the body
of `startInterior`, verbatim, as a function of the state alone. -/
def startCount (s : St) : Nat :=
  ((List.range (s.1 + 5)).filter fun i : Nat =>
    let a : ℤ := (i : ℤ) - ((s.1 : ℤ) + 2)
    let t0 : ℤ := a
    let t1 : ℤ := a + (s.1 : ℤ)
    let nc : Bool := if s.1 = 1 then true else near t0 && near t1
    (near t0 || near t1) && nc == s.2).length

/-- The per-state bare start count (`dp_bare` of the reference). -/
def bareCount (s : St) : Nat := if s.2 == (s.1 == 1) then 1 else 0

theorem startInterior_eq (gmax : Nat) :
    startInterior gmax = (states gmax).map fun s => (s, startCount s) := rfl

theorem startBare_eq (gmax : Nat) :
    startBare gmax = (states gmax).map fun s => (s, bareCount s) := rfl

/-- The interior start places one pair row against a single contact cell;
it can only be joined if both cells touch that cell, forcing gap `≤ 2`. -/
theorem startCount_J_high (g : Nat) (h : 3 ≤ g) :
    startCount (g, true) = 0 := by
  rw [startCount, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
    decide_eq_true_eq, if_neg (by omega : ¬ g = 1)]
  omega

/-- The bare start is joined only at gap 1, by definition. -/
theorem bareCount_J_high (g : Nat) (h : 2 ≤ g) :
    bareCount (g, true) = 0 := by
  rw [bareCount, if_neg (by simp; omega)]

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.stepMul_P_local' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms stepMul_P_local

/--
info: 'Polyplets.GapWalk.stepMul_J_to_J_far' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms stepMul_J_to_J_far

end GapWalk
end Polyplets
