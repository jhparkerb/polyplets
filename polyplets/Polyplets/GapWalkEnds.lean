/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkStacks
import Polyplets.GapWalkRows
import Polyplets.GapWalkCanon
import Polyplets.GapWalkBridge

/-!
# Notary piece B, module 3: starts and ends

Campaign *Notary*, piece **B**. This module ties the two open boundaries of
the stack recursion to the walk's boundary data and to the configuration
counts of `Weights.lean` / `GapWalkBridge.lean`:

* **starts** — one-row stacks are counted by the walk's start vectors:
  `(STKI 1 g c).card = startCount (g, c)`,
  `(STKB 1 g c).card = bareCount (g, c)`;
* **ends** — closing a stack with the free contact cell `q` (or with
  nothing) turns stack counts into configuration counts:

      V  ℓ ℓ = qEndF   B (fun s => (STKI ℓ s).card)
      Vt ℓ ℓ = qEndF   B (fun s => (STKB ℓ s).card)   (via reflection)
      Vp ℓ ℓ = bareEndF B (fun s => (STKB ℓ s).card)

  for any cap `B` large enough (`2ℓ + 2` resp. `2ℓ`).

All statements pre-verified numerically (`verify_bij_statements.py`,
checks B/G: per-stack q-fibers equal `endMul`, assembled sums hit the
banked `V`/`Vt`/`Vp` at `ℓ ≤ 3`, and the reflection is a bijection onto
the `IsVtConfig` sets).

## The q-closure geometry

A single free cell `q = (x, i+1)` above a stack `T` (top pair `tL, tR` at
gap `g`, class `c`) sees only `tL, tR` (`newRow_adj` reasoning); the full
set `insert q T` is king-connected iff `J`: `q` touches either top (each
component *is* the whole stack), `P`: `q` touches both (it must merge
them): `connected_insert_q_iff`. Counting the admissible `x` gives
`endMul g c` — `qEnd`'s weights `g+3 / 6 / 3−g / 0` (`endCount_eq`), and
summing over stacks fiberwise gives the `V`-identities exactly as the peel
recursion did (truncation `τ = filter (·.2 ≤ ℓ)`, fibers of size
`endMul`).

## The reflection

`qEnd` on the *bare* walk counts "bare stack + `q` above" — the family
`BQ ℓ` below. `Vt ℓ ℓ` counts the same clusters with the contact cell
*below* (rows `1..ℓ` above `(0,0)`). The bijection is the y-flip
`flipMap`: reflect about the top row and re-anchor at the flipped `q`;
`Finset.card_bij'` with explicit inverse (re-anchor at the row-1 minimum,
which the `BQ` anchoring pins to recover the shift).
-/

namespace Polyplets

open GapWalk (St states near startCount bareCount qEndF bareEndF canon qEnd bareEnd)
open GapWalkBridge (IsVpConfig CFGVp Vp mem_CFGVp)

/-! ## The end multiplicities -/

/-- The weight `qEnd` gives one source state: the number of placements of
the free contact cell over a top pair at gap `g`, class `c`. -/
def endMul (g : ℕ) (c : Bool) : ℕ :=
  if c then (if g ≤ 2 then g + 3 else 6) else (if g ≤ 2 then 3 - g else 0)

/-- `qEndF` is the state-sum against `endMul` (unfold `qEnd`/`canon`;
the two `if`-trees agree term by term, `P` above gap 2 giving `0 = F·0`). -/
theorem qEndF_eq_sum (B : ℕ) (F : St → ℕ) :
    qEndF B F = ((states B).map fun s => F s * endMul s.1 s.2).sum := by
  sorry

/-- `bareEndF` is the state-sum reading the `J` values. -/
theorem bareEndF_eq_sum (B : ℕ) (F : St → ℕ) :
    bareEndF B F = ((states B).map fun s => if s.2 then F s else 0).sum := by
  sorry

/-- **The q-window count**: offsets `d = x − xL` with the class-appropriate
contact Boolean, counted over the window `range (g+5)` at `d = n − 2`,
total `endMul g c`. Proof: `g ≤ 2` is two concrete gaps (substitute and
`decide`); `g ≥ 3`, class `J`: the filter is the six-element set
`{1, 2, 3, g+1, g+2, g+3}` (`Finset.ext` + omega on the `near`s, then an
insert-chain cardinality); class `P`: the filter is empty (omega). -/
theorem endCount_eq (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    ((Finset.range (g + 5)).filter fun n : ℕ =>
      (if c then near ((n : ℤ) - 2) || near ((n : ℤ) - 2 - (g : ℤ))
       else near ((n : ℤ) - 2) && near ((n : ℤ) - 2 - (g : ℤ))) = true).card =
      endMul g c := by
  sorry

/-! ## The q-closure frame -/

section Frame

variable {i g : ℕ} {T : Finset (ℤ × ℤ)} {xL : ℤ} {c : Bool}

/-- **Closing with one free cell.** `insert (x, i+1) T` is king-connected
iff the class-appropriate contact Boolean holds at offset `x − xL`.
`←`: `J`: all of `T` reaches the touched top (`stackOK` + joined tops),
one edge more reaches `q`, and connectivity is pairwise reach through `q`'s
component; `P`: both components reach `q`, hence each other. `→`: `J`, no
contact: trap `T` (`reach_closed`; `q`'s only possible `T`-neighbors are
tops, untouched) against `reach (insert q T) tL q` from connectivity; `P`,
`tL`-side untouched: trap `{p ∈ T | reach T p tL}` — closed within `T`,
`tR` outside it (class `P`), `q` not adjacent to `tL`. -/
theorem connected_insert_q_iff
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (x : ℤ) :
    KingConnected (insert (x, (i : ℤ) + 1) T) ↔
      ((if c then near (x - xL) || near (x - xL - (g : ℤ))
        else near (x - xL) && near (x - xL - (g : ℤ))) = true) := by
  sorry

end Frame

/-! ## Starts -/

/-- One-row interior stacks are the walk's interior start vector. The set
`S = {(0,0), (a,1), (a+g,1)}`: membership analysis is a three-cell special
case (reach in a 3-set: `(0,0)` reaches a top iff adjacent to one —
trap `{(0,0)}` otherwise; the tops are joined iff `g = 1` or `(0,0)`
touches both — traps `{u}` resp. `{u, (0,0)}` otherwise), matching
`startCount`'s filter Boolean at `a = n − (g+2)`; then the same
window bijection as the peel recursion (`n ↦` the 3-set, left cell
`a`-monotone; surjectivity reads `a` off the top-left witness). -/
theorem STKI_one_card (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    (STKI 1 g c).card = startCount (g, c) := by
  sorry

/-- One-row bare stacks are the bare start vector: the anchoring pins
`S = {(0,1), (g,1)}` (witness pair = the two row-1 cells, leftmost at 0),
`stackOK` is trivial (both cells are tops), and the tops are joined iff
they are adjacent, i.e. `g = 1` (trap `{(0,1)}` for `g ≥ 2`) — so the
count is `1` when `c` matches `g == 1`, else `0`, which is
`bareCount (g, c)`. -/
theorem STKB_one_card (g : ℕ) (hg : 1 ≤ g) (c : Bool) :
    (STKB 1 g c).card = bareCount (g, c) := by
  sorry

/-! ## The interior end: `V ℓ ℓ` -/

/-- **Interior assembly.** Partition `CFGV ℓ ℓ` (membership = `IsVConfig`,
`mem_CFGV`) fiberwise along `S' ↦ topState (τ S') ℓ`-style truncation into
the stack sets, exactly as in `STKI_card_step`:

* `IsVConfig ℓ ℓ S'` forces exactly two cells in rows `1..ℓ`
  (`card_eq_sum_rowSize`: `2ℓ + 2 = 1 + 2ℓ + 1` with every interior row
  `≥ 2`), a unique `q` on row `ℓ+1`;
* `τ S' = S'.filter (·.2 ≤ ℓ)` is an interior stack (q-truncation trap),
  whose state lies in `states B`: `J`-gaps `≤ 2ℓ ≤ B`, `P`-gaps `≤ 2`
  (both `near`s at the `q`-contact);
* the fiber over a stack `T` in state `(g, c)` counts admissible `q`
  columns: `connected_insert_q_iff` matches the `endCount_eq` window
  (bijection `n ↦ insert (xL + n − 2, ℓ+1) T`), giving `endMul g c`;
* sum against `qEndF_eq_sum` (`Finset.sum_biUnion` +
  `isStackI_state_unique` disjointness + `List.sum_toFinset`/
  `states_nodup`). -/
theorem V_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    V ℓ ℓ = qEndF B (fun s => (STKI ℓ s.1 s.2).card) := by
  sorry

/-! ## The bare ends: `Vp ℓ ℓ` and (via reflection) `Vt ℓ ℓ` -/

/-- **Pure assembly.** A pure configuration *is* a connected bare stack:
`IsVpConfig ℓ ℓ S ↔ ∃ g, IsStackB ℓ g true S` (`stackOK` comes for free
from connectivity; conversely `stackOK_reach_iff_connected`). Partition
`CFGVp ℓ ℓ` fiberwise along `topState · ℓ` into `(states B).toFinset`
(gaps `≤ card − 1 = 2ℓ − 1 ≤ B`), fibers = `STKB ℓ g true` for `J` states
and empty for `P` states, and compare with `bareEndF_eq_sum`. -/
theorem Vp_eq_bareEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ ≤ B) :
    Vp ℓ ℓ = bareEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  sorry

/-- The **bare-stack-plus-contact family** `BQ ℓ`: what `qEnd` on the bare
walk counts directly — rows `1..ℓ` two cells each anchored bare-style, one
extra cell on row `ℓ+1`, all king-connected. -/
def IsBQ (ℓ : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = 2 * ℓ + 1 ∧
  ((0 : ℤ), (1 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 1 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + 1) ∧
  (∀ p ∈ S, p.2 = 1 → 0 ≤ p.1) ∧
  rowSize S ((ℓ : ℤ) + 1) = 1 ∧
  (∀ r ∈ Finset.Icc 1 ℓ, rowSize S (r : ℤ) = 2) ∧
  KingConnected S

instance (ℓ : ℕ) (S : Finset (ℤ × ℤ)) : Decidable (IsBQ ℓ S) := by
  unfold IsBQ; infer_instance

/-- `BQ ℓ`, enumerated in the window idiom (connected with an anchor on
row 1, `card = 2ℓ + 1`, so `|x| ≤ 2ℓ` by `connected_sub_x_le`; width
`2ℓ + 1` for slack). -/
def BQ (ℓ : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  ((window (2 * ℓ + 1) 1 (ℓ + 1)).powersetCard (2 * ℓ + 1)).filter (IsBQ ℓ)

/-- Window independence for `BQ` (mirror `mem_CFGVp`). -/
theorem mem_BQ {ℓ : ℕ} (hℓ : 1 ≤ ℓ) {S : Finset (ℤ × ℤ)} :
    S ∈ BQ ℓ ↔ IsBQ ℓ S := by
  sorry

/-- **Bare assembly.** `(BQ ℓ).card` counted fiberwise over bare-stack
truncations — the identical argument to `V_eq_qEndF` with `IsStackB`
replacing `IsStackI` (anchor clauses pass to the truncation verbatim: the
dropped cell sits on row `ℓ + 1 ≥ 2`). -/
theorem BQ_card_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    (BQ ℓ).card = qEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  sorry

/-- **The reflection.** `Vt ℓ ℓ = (BQ ℓ).card` by the y-flip about row
`ℓ + 1` (`Finset.card_bij'`):

* forward `CFGVt ℓ ℓ → BQ ℓ`:
  `S' ↦ S'.image (flipMap (rowMinX S' ℓ) (ℓ + 1))` — the contact cell
  `(0,0)` becomes the row-`(ℓ+1)` cell, old row `r` becomes new row
  `ℓ+1−r`, and the shift re-anchors the new row 1 (old row `ℓ`) at
  minimum `x = 0`;
* inverse `BQ ℓ → CFGVt ℓ ℓ`:
  `D ↦ D.image (flipMap (rowMinX D (ℓ+1)) (ℓ + 1))` — re-anchor at the
  unique top cell, which lands on `(0,0)`;
* round trips by `flipMap_flipMap` (each composite is a translation whose
  shift the anchors force to zero: `rowMinX` of the image row computes to
  minus the original shift);
* membership transport: `Finset.card_image_of_injective`
  (`flipMap_injective`) for the cardinality, `rowSize` under images of
  injective maps for the row profile, `kingConnected_image` +
  `kingAdj_flipMap` for connectivity, `mem_CFGVt` on the config side.
  For row extraction under the flip: `rowMinX (S.image (flipMap cx cy)) y
  = rowMinX S (cy − y) − cx` (min of a shifted image; prove as a private
  helper via `rowMinX_mem`/`rowMinX_le` antisymmetry rather than `min`
  algebra). -/
theorem Vt_eq_BQ_card (ℓ : ℕ) (hℓ : 1 ≤ ℓ) : Vt ℓ ℓ = (BQ ℓ).card := by
  sorry

/-- **Bottom-edge assembly**, the composite the walk emits. -/
theorem Vt_eq_qEndF (ℓ : ℕ) (hℓ : 1 ≤ ℓ) (B : ℕ) (hB : 2 * ℓ + 2 ≤ B) :
    Vt ℓ ℓ = qEndF B (fun s => (STKB ℓ s.1 s.2).card) := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms
(kernel `decide` on the concrete small gaps is fine). -/

/--
info: 'Polyplets.V_eq_qEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms V_eq_qEndF

/--
info: 'Polyplets.Vt_eq_qEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Vt_eq_qEndF

/--
info: 'Polyplets.Vp_eq_bareEndF' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Vp_eq_bareEndF

end Polyplets
