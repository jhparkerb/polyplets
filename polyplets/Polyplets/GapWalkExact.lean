/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.BigOperators.Intervals
import Polyplets.GapWalkTrunc
import Polyplets.GapWalkRowVals

/-!
# Notary piece K, module 4: the exact walk

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`, wave K-β. Piece
T's cone lemma (`GapWalkTrunc.iter_agree`) says the capped walks agree
wherever the cone allows; this module names the **exact** (cap-free) walk
values it therefore defines,

* `jE F m g` — the `J`-class value at gap `g` after `m` steps,
* `pE F m g` — the `P`-class value,

and proves the facts the column-series module (`GapWalkColumns.lean`)
consumes:

* cap stability (`jE_eq`, `pE_eq`): any legal cap computes them;
* the start packages `StartData` — the two start vectors of the walk as
  one hypothesis bundle `(j01, j02, p02, pt)`, instantiated by
  `startData_interior` (4,1,4,6) and `startData_bare` (1,0,1,1);
* `J`-support `≤ 2m+2` (`jE_support`) and `pE_one : pE F m 1 = 0`;
* the **exact step recurrences** (`jE_step`, `pE_step`): the next value is
  a finite sum over the stated source windows — `J` sources up to the
  support bound, `P` sources up to gap `3` (for `J` targets: joins only
  come from `g ≤ 3`) resp. `gp + 2` (for `P` targets: `P`-locality);
* the end-functional bridge (`qEndF_eval`, `bareEndF_eval`,
  `walkFamilies_entry`): the numbers the walk emits are linear reads of
  `jE`/`pE`.

Every statement was verified numerically before this skeleton was written:
`experiments/notary_kbeta_statements.py` b1–b4, b6
(`build/notary_kbeta_statements.log`), against
`depth1_gap_walk.transitions` and the banked `walk_table_19` heads.

## Proof recipes

*Stability* (`iter_agree_of_le`): wrap `GapWalkTrunc.iter_agree` in
`Nat.le_total`-symmetry. `jE_eq`/`pE_eq` are its instances at the defining
caps `2m+5` and `g+2m+5`.

*Support*: `GapWalkTrunc.iter_J_support` at the defining cap.

*Recurrences*: write `jE F (m+1) gp` at cap `M := 2*m + gp + 7` via
`jE_eq`; one `iter` step is `funStep M`, a sum over `states M`. Convert the
list sum to `∑ g ∈ Finset.Icc 1 M` per class (`states` is a product list;
`GapWalkCanon.mem_states`), then trim: `J` sources above `2m+2` die by
`jE_support`, `P` sources above the window die by
`GapWalkRows.stepMul_P_to_J` / `stepMul_P_to_J2` / `stepMul_P_far_to_J`
(`J` targets) resp. `stepMul_P_local` (`P` targets, `g ≥ 3`). Inside the
windows, rewrite each `iter` value as `jE`/`pE` by `jE_eq`/`pE_eq` (the
window sits inside the cone at cap `M`).

*Ends*: `qEndF`/`bareEndF` are list sums over `states M` with weights
supported on `J` (all gaps) and `P` at `g ≤ 2`; the same conversion and
trimming, no recurrence.

*Entry*: `walkFamilies` is `walkAux` on `startInterior`/`startBare`;
`GapWalkRows.startInterior_eq`/`startBare_eq` turn the starts into
`canon`-form, `GapWalkCanon.walkAux_canon` turns the list into a
`List.range`-map, and `List.getD` of a `range`-map is evaluation.

Do not change any statement below; if one resists proof, leave it sorried
and report back.
-/

namespace Polyplets
namespace GapWalk

/-! ## The exact values -/

/-- The exact `J`-value at gap `g` after `m` steps: the capped walk at the
stable cap `2m+5` (`iter_agree`: every cap `≥ 2m+5` computes the same
`J`-row). -/
def jE (F : St → Nat) (m g : Nat) : Nat := iter (2 * m + 5) F m (g, true)

/-- The exact `P`-value at gap `g` after `m` steps: the capped walk at a cap
inside whose cone `(g, m)` lies (`iter_agree`: any cap `≥ 2m+5` with
`g + 2m ≤ cap` computes the same value). -/
def pE (F : St → Nat) (m g : Nat) : Nat :=
  iter (g + 2 * m + 5) F m (g, false)

/-- The start packages of both walk starts: heads `(j01, j02)` on the `J`
side, `(0, p02)` on the `P` side, nothing on `J` from gap 3, the constant
`pt` on `P` from gap 3. -/
structure StartData (F : St → Nat) (j01 j02 p02 pt : Nat) : Prop where
  head_j1 : F (1, true) = j01
  head_j2 : F (2, true) = j02
  head_p1 : F (1, false) = 0
  head_p2 : F (2, false) = p02
  deep_j : ∀ g, 3 ≤ g → F (g, true) = 0
  deep_p : ∀ g, 3 ≤ g → F (g, false) = pt

/-- The interior start (`dp_int`): `(4, 1, 4, 6)`. -/
theorem startData_interior : StartData startCount 4 1 4 6 := by
  sorry

/-- The bare start (`dp_bare`): `(1, 0, 1, 1)`. -/
theorem startData_bare : StartData bareCount 1 0 1 1 := by
  sorry

/-! ## Cap stability -/

/-- `iter_agree`, symmetrized: two legal caps agree on every `J`-value and
on `P`-values inside both cones. -/
theorem iter_agree_of_le (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) {M M' l : Nat}
    (hM : 2 * l + 5 ≤ M) (hM' : 2 * l + 5 ≤ M') :
    (∀ g, iter M F l (g, true) = iter M' F l (g, true)) ∧
      (∀ g, g + 2 * l ≤ M → g + 2 * l ≤ M' →
        iter M F l (g, false) = iter M' F l (g, false)) := by
  sorry

/-- Any cap `≥ 2m+5` computes `jE`. -/
theorem jE_eq (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {M m : Nat} (hM : 2 * m + 5 ≤ M) (g : Nat) :
    jE F m g = iter M F m (g, true) := by
  sorry

/-- Any cap `≥ 2m+5` whose cone contains `(g, m)` computes `pE`. -/
theorem pE_eq (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {M m g : Nat} (hM : 2 * m + 5 ≤ M) (hg : g + 2 * m ≤ M) :
    pE F m g = iter M F m (g, false) := by
  sorry

/-- Zero steps: the start itself. -/
theorem jE_zero (F : St → Nat) (g : Nat) : jE F 0 g = F (g, true) := rfl

/-- Zero steps: the start itself. -/
theorem pE_zero (F : St → Nat) (g : Nat) : pE F 0 g = F (g, false) := rfl

/-! ## Support -/

/-- `J`-support: after `m` steps nothing joined lives above gap `2m+2`. -/
theorem jE_support (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m g : Nat) (h : 2 * m + 2 < g) : jE F m g = 0 := by
  sorry

/-- Nothing ever lands pending at gap 1 (`stepMul_to_1_P`), and neither
start puts anything there. -/
theorem pE_one (F : St → Nat) (h1 : F (1, false) = 0) (m : Nat) :
    pE F m 1 = 0 := by
  sorry

/-! ## The exact step recurrences -/

/-- One step onto a `J` target: `J` sources through the support window,
`P` sources only from gaps `≤ 3` (joins never come from farther out). -/
theorem jE_step (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m gp : Nat) (hgp : 1 ≤ gp) :
    jE F (m + 1) gp =
      (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp true) +
      (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false gp true) := by
  sorry

/-- One step onto a `P` target at gap `≥ 2`: `J` sources through the
support window, `P` sources through the locality window `[1, gp+2]`. -/
theorem pE_step (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m gp : Nat) (hgp : 2 ≤ gp) :
    pE F (m + 1) gp =
      (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp false) +
      (∑ g ∈ Finset.Icc 1 (gp + 2), pE F m g * stepMul g false gp false) := by
  sorry

/-! ## The end-functional bridge -/

/-- `qEnd` of the `m`-step walk reads `J` at weights `4, 5, 6, 6, …` and
`P` at weights `2, 1, 0, …`: a linear read of the exact values. -/
theorem qEndF_eval (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    qEndF M (iter M F m) =
      4 * jE F m 1 + 5 * jE F m 2 +
        6 * ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g +
        2 * pE F m 1 + pE F m 2 := by
  sorry

/-- `bareEnd` of the `m`-step walk sums the `J`-row. -/
theorem bareEndF_eval (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    bareEndF M (iter M F m) =
      jE F m 1 + jE F m 2 + ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g := by
  sorry

/-- Entry `l` of `walkFamilies L` is the pair of end reads of the `l`-step
iterates of the two starts, at the family cap. -/
theorem walkFamilies_entry (L l : Nat) (hl : l < L) :
    (walkFamilies L).getD l (0, 0, 0) =
      (qEndF (2 * L + 3) (iter (2 * L + 3) startCount l),
       qEndF (2 * L + 3) (iter (2 * L + 3) bareCount l),
       bareEndF (2 * L + 3) (iter (2 * L + 3) bareCount l)) := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.jE_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms jE_step

/--
info: 'Polyplets.GapWalk.pE_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms pE_step

end GapWalk
end Polyplets
