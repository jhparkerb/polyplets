/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkStacks
import Polyplets.GapWalkCanon

/-!
# Notary piece B, module 2: the peel recursion

Campaign *Notary*, piece **B**. Head theorems (`STKI_card_step`,
`STKB_card_step`): the stack counts satisfy the walk's own recursion,

    |STK (i+1) (g', c')| = Σ_{(g,c) ∈ states B} |STK i (g, c)| · stepMul g c g' c',

stated with the right side as `GapWalk.funStep` so `GapWalkBij` can consume
it verbatim. Pre-verified numerically (`verify_bij_statements.py`, checks
C/D/E: recursion, master fiber lemma exhaustively over all stacks of ≤ 2
rows, truncation).

## The geometry, once

Let `T` be a stack with top row `i` = `{tL = (xL, i), tR = (xL+g, i)}` and
class `c`, and put a new pair `u = (xL+a, i+1)`, `v = (xL+a+g', i+1)` on
top; `S = insert u (insert v T)`. King steps change `y` by at most 1 and
row `i` holds only `tL, tR`, so **the entire interface between `{u, v}` and
`T` is the four Booleans**

    x0 = near a         (u ~ tL)      x1 = near (a+g')       (v ~ tL)
    y0 = near (a−g)     (u ~ tR)      y1 = near (a+g'−g)     (v ~ tR)

plus `u ~ v ↔ g' = 1`. Every component of `T` holds `tL` or `tR` (that is
`stackOK`), so the component structure of `S` is a finite quotient of at
most four atoms `{comp(tL), comp(tR), {u}, {v}}` under these five edges —
and the two head lemmas are case analyses over them:

* `stack_cond_iff` (`ok`): `S` is again a stack — every component meets
  the new top row — iff class `J`: some contact at all
  (`touch0 ∨ touchg`), class `P`: both old components touched
  (`touch0 ∧ touchg`). Dead components are those of `T` missing every
  contact; `u`, `v` themselves always meet the top row.
* `class_iff` (`nc`): given `ok`, the new pair is joined iff `g' = 1`
  (direct edge), else — `J` source: both new cells attached,
  `(x0 ∨ y0) ∧ (x1 ∨ y1)`; `P` source: some old component touched by both
  new cells, `(x0 ∧ x1) ∨ (y0 ∧ y1)` (`GapWalk.joined x0 y0 x1 y1`).

Positive directions are path-gluing (`reach_tail`, `reach_mono`,
`reach_trans`, `reach_symm`); negative directions are `reach_closed` with
the explicit trap sets listed at each `sorry`.

## From the master lemma to the recursion

`isStackI_insert_iff` assembles `ok`/`nc` with the row bookkeeping into:
the assembled set is a stack in state `(g', c')` iff the Boolean
`okB && (ncB == c')` holds — the *very predicate* `stepMul` filters
(`stepMul_eq_card`). The recursion is then fiberwise counting under the
truncation `τ S = S.filter (·.2 ≤ i)`:

* every `S ∈ STK (i+1) (g', c')` truncates to a stack (`trunc` lemmas;
  the trap set for "every `T`-component keeps a row-`i` cell" is
  `{q ∈ T | reach T q tL ∨ reach T q tR} ∪ {u, v}`);
* its state lands in `states B`: `J`-truncations have `g ≤ 2i`
  (`isStackI_J_le`), `P`-truncations have `g ≤ g' + 2` (both tops lie in
  the touched window of width `g' + 2`, arithmetic from `ok`);
* the fiber over a fixed `T` is in bijection with the `stepMul` filter
  window via `a ↦ insert u (insert v T)` (`Finset.card_bij`; injectivity:
  distinct `a` give distinct top rows; surjectivity: read `a` off the
  top-left cell of `S`, which its own `∃`-witness provides).
-/

namespace Polyplets

open GapWalk (St states near joined stepMul funStep)

/-! ## The transition Booleans, named -/

/-- The legality Boolean of `stepMul`, exposed: `ok` at offset `a`. -/
def okB (g : ℕ) (c : Bool) (gp : ℕ) (a : ℤ) : Bool :=
  let touch0 := near a || near (a + (gp : ℤ))
  let touchg := near (a - (g : ℤ)) || near (a + (gp : ℤ) - (g : ℤ))
  if c then touch0 || touchg else touch0 && touchg

/-- The new-class Boolean of `stepMul`, exposed: `nc` at offset `a`. -/
def ncB (g : ℕ) (c : Bool) (gp : ℕ) (a : ℤ) : Bool :=
  if gp = 1 then true
  else if c then
    (near a || near (a - (g : ℤ))) && (near (a + (gp : ℤ)) || near (a + (gp : ℤ) - (g : ℤ)))
  else joined (near a) (near (a - (g : ℤ))) (near (a + (gp : ℤ))) (near (a + (gp : ℤ) - (g : ℤ)))

/-- `stepMul` counts exactly the window offsets where `okB && ncB == c'`:
its `List.filter` predicate is these Booleans at `a = n − (gp + 2)`.
(`Finset.range`/`List.range` filter-length bridge; `List.countP` route or
`rfl` after unfolding.) -/
theorem stepMul_eq_card (g : ℕ) (c : Bool) (gp : ℕ) (cp : Bool) :
    stepMul g c gp cp =
      ((Finset.range (g + gp + 5)).filter fun n : ℕ =>
        (okB g c gp ((n : ℤ) - ((gp : ℤ) + 2)) &&
         (ncB g c gp ((n : ℤ) - ((gp : ℤ) + 2)) == cp)) = true).card := by
  sorry

/-! ## The frame

Hypotheses shared by every lemma below (interior and bare alike): `T`'s
cells sit in rows `≤ i`, its row `i` is exactly the pair at gap `g`, every
cell reaches a top cell, and `c` records whether the tops are joined. The
hypotheses are spelled out per lemma (no section `variable`s: they would
not be auto-included, as none is mentioned in the statements). -/

section Frame

variable {i g : ℕ} {T : Finset (ℤ × ℤ)} {xL : ℤ} {c : Bool}

/-- New-row cells only see the two top cells of `T` (`kingAdj_y` plus the
row characterization). Stated for any cell on row `i + 1`. -/
theorem newRow_adj {b w : ℤ × ℤ}
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hb : b ∈ T) (hw : w.2 = (i : ℤ) + 1) (hadj : kingAdj b w) :
    b = (xL, (i : ℤ)) ∨ b = (xL + (g : ℤ), (i : ℤ)) := by
  sorry

/-- **`ok` is the stack condition.** With `u = (xL+a, i+1)`,
`v = (xL+a+g', i+1)`, `S = insert u (insert v T)`:

`←`  `J`: all of `T` reaches `tL` (tops joined, `stackOK`, symmetry), `tL`
     reaches whichever top is touched and thence the touching new cell;
     `u`, `v` reach themselves. `P`: each cell reaches its top, each top
     its toucher.
`→`  `J`, no contact at all: `T` itself is a trap set (`reach_closed` —
     no `T`-cell is adjacent to `u` or `v` by `newRow_adj`), yet
     `stackOK S u v` at `tL ∈ S` demands escape; contradiction. `P`,
     `¬touch0` (tL's side untouched): trap `{q ∈ T | reach T q tL}` —
     closed within `T` by `reach_tail`, closed toward `u, v` because their
     only `T`-neighbors are tops, `tR` is not in the trap (`hc`, class
     `P`), and `tL` has no contact. Symmetrically for `¬touchg`. -/
theorem stack_cond_iff
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ) :
    stackOK
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1) ↔
    okB g c gp a = true := by
  sorry

/-- **`nc` is the new class.** Given the stack condition, the new pair is
joined iff `ncB`. Case tree (write `S`, `u`, `v` as above):

* `gp = 1`: `u ~ v` directly (`kingAdj`, same row, distance 1).
* `gp ≥ 2`, source `J`: joined iff both new cells have some contact.
  `←`: each new cell steps into the single old component and out to the
  other new cell's contact. `→`: if (say) `u` has no contact, trap `{u}`
  (its only possible `S`-neighbors are tops — excluded — and `v`, too far).
* `gp ≥ 2`, source `P`: joined iff some *single* old component is touched
  by both new cells (`joined x0 y0 x1 y1 = (x0 && x1) || (y0 && y1)`).
  `←`: `u → tL → v` (or via `tR`). `→`: contrapositive, four traps by
  `u`'s contact pattern, each excluding `v`:
  `u` touches neither top: trap `{u}`; only `tL`: trap
  `{u} ∪ {q ∈ T | reach T q tL}` (uses `¬x1`, from `¬joined` and `x0`);
  only `tR`: mirror; both: trap `{u} ∪ reachers(tL) ∪ reachers(tR)`
  (then `¬x1 ∧ ¬y1`, so `v` borders nothing in the trap). -/
theorem class_iff
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (hOK : stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (hc : c = true ↔ reach T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ)
    (hok : okB g c gp a = true) :
    (reach
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1)) ↔
    ncB g c gp a = true := by
  sorry

/-- Truncation direction: if the assembled set is a stack over its new top
pair, then `T` was a stack over the old one. Trap set:
`{q ∈ T | reach T q tL ∨ reach T q tR} ∪ {u, v}`, entered at `u`, walked
backwards from `reach S p u ∨ reach S p v` via `reach_symm`. -/
theorem trunc_stackOK
    (hg : 1 ≤ g)
    (hTy : ∀ p ∈ T, p.2 ≤ (i : ℤ))
    (htL : (xL, (i : ℤ)) ∈ T) (htR : (xL + (g : ℤ), (i : ℤ)) ∈ T)
    (hrow : ∀ q ∈ T, q.2 = (i : ℤ) →
      q = (xL, (i : ℤ)) ∨ q = (xL + (g : ℤ), (i : ℤ)))
    (gp : ℕ) (hgp : 1 ≤ gp) (a : ℤ)
    (hS : stackOK
      (insert (xL + a, (i : ℤ) + 1) (insert (xL + a + (gp : ℤ), (i : ℤ) + 1) T))
      (xL + a, (i : ℤ) + 1) (xL + a + (gp : ℤ), (i : ℤ) + 1)) :
    stackOK T (xL, (i : ℤ)) (xL + (g : ℤ), (i : ℤ)) := by
  sorry

end Frame

/-! ## The master fiber lemmas -/

/-- **Master fiber lemma, interior.** Adding the pair at offset `a`, span
`g'` to an interior `i`-row stack in state `(g, c)` yields an interior
`(i+1)`-row stack in state `(g', c')` exactly when `stepMul`'s Boolean
holds. Assemble: `stack_cond_iff` + `class_iff` (frame from
`isStackI_top`, `hTy` from the bounds clause, `hrow` from the top
extraction) for the `∃`-clause; cardinality (`u, v` new, distinct), row
bounds, `rowSize` updates (`rowSize_insert_*`), and the top-witness
uniqueness for the `→` direction (the witness of the assembled stack's
`∃`-clause must be `u`: its row is `i+1`, and `row_eq_pair` pins the row to
`{u, v}` with `u` left). -/
theorem isStackI_insert_iff {i g : ℕ} {c : Bool} {T : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (hT : IsStackI i g c T)
    (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) (a : ℤ) :
    IsStackI (i + 1) g' c'
      (insert (rowMinX T (i : ℤ) + a, (i : ℤ) + 1)
        (insert (rowMinX T (i : ℤ) + a + (g' : ℤ), (i : ℤ) + 1) T)) ↔
    (okB g c g' a && (ncB g c g' a == c')) = true := by
  sorry

/-- **Master fiber lemma, bare.** Identical assembly over `IsStackB`
(the two extra clauses — anchor cell and row-1 left bound — hold in the
assembled set iff they held in `T`, as the new cells sit on row
`i + 1 ≥ 2`). -/
theorem isStackB_insert_iff {i g : ℕ} {c : Bool} {T : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (hT : IsStackB i g c T)
    (g' : ℕ) (hg' : 1 ≤ g') (c' : Bool) (a : ℤ) :
    IsStackB (i + 1) g' c'
      (insert (rowMinX T (i : ℤ) + a, (i : ℤ) + 1)
        (insert (rowMinX T (i : ℤ) + a + (g' : ℤ), (i : ℤ) + 1) T)) ↔
    (okB g c g' a && (ncB g c g' a == c')) = true := by
  sorry

/-! ## Truncation lands in the source states -/

/-- Truncating an `(i+1)`-row interior stack gives an `i`-row interior
stack. Row bookkeeping: `τ S` keeps rows `≤ i` verbatim, drops exactly the
two top cells; connectivity: `trunc_stackOK`; class/gap: read off row `i`
(`row_two_cells`); the `∃`-witness is the left row-`i` cell. -/
theorem isStackI_trunc {i g' : ℕ} {c' : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI (i + 1) g' c' S) :
    ∃ g c, IsStackI i g c (S.filter fun p => p.2 ≤ (i : ℤ)) ∧
      1 ≤ g ∧ (c = true → g ≤ 2 * i) ∧ (c = false → g ≤ g' + 2) := by
  sorry

theorem isStackB_trunc {i g' : ℕ} {c' : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB (i + 1) g' c' S) :
    ∃ g c, IsStackB i g c (S.filter fun p => p.2 ≤ (i : ℤ)) ∧
      1 ≤ g ∧ (c = true → g ≤ 2 * i) ∧ (c = false → g ≤ g' + 2) := by
  sorry

/-! ## The recursion -/

/-- **The interior stack counts satisfy the walk recursion.** Fiberwise
count over the truncation map into
`U = (states B).toFinset.biUnion (fun s => STKI i s.1 s.2)`
(`Finset.card_eq_sum_card_fiberwise`, target membership by
`isStackI_trunc` + the gap bounds + `mem_STKI`); split the sum over the
`biUnion` (`Finset.sum_biUnion`; disjointness from
`isStackI_state_unique`); per `T`, the fiber
`(STKI (i+1) g' c').filter (fun S => τ S = T)` is in `Finset.card_bij`
with the `stepMul_eq_card` window via `n ↦` the assembled set at
`a = n − (g' + 2)`:

* membership: `isStackI_insert_iff` (←) plus `τ (assembled) = T`;
* injectivity: two offsets giving the same set give the same row-`(i+1)`
  left cell, and the assembled left cell is `rowMinX T i + a` (its row is
  exactly the two new cells, `a`-monotone);
* surjectivity: for `S` in the fiber, `S = insert u (insert v (τ S))` with
  `u` the top-left witness (rows `≤ i` are `τ S`, row `i+1` is `{u, v}` by
  `row_eq_pair`); its offset lies in the window because `okB` holds
  (`isStackI_insert_iff` (→) after rebuilding `S` in assembled form), and
  `okB` pins `−g'−1 ≤ a ≤ g+1` (omega on the `near`s);

finally `List.sum_toFinset` (with `states_nodup`) turns the `Finset` sum
into `funStep`'s list sum. -/
theorem STKI_card_step (i : ℕ) (hi : 1 ≤ i) (g' : ℕ) (hg' : 1 ≤ g')
    (c' : Bool) (B : ℕ) (hB1 : 2 * i ≤ B) (hB2 : g' + 2 ≤ B) :
    (STKI (i + 1) g' c').card =
      funStep B (fun s => (STKI i s.1 s.2).card) (g', c') := by
  sorry

/-- **The bare stack counts satisfy the walk recursion.** Same proof over
`IsStackB`. -/
theorem STKB_card_step (i : ℕ) (hi : 1 ≤ i) (g' : ℕ) (hg' : 1 ≤ g')
    (c' : Bool) (B : ℕ) (hB1 : 2 * i ≤ B) (hB2 : g' + 2 ≤ B) :
    (STKB (i + 1) g' c').card =
      funStep B (fun s => (STKB i s.1 s.2).card) (g', c') := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.STKI_card_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms STKI_card_step

/--
info: 'Polyplets.STKB_card_step' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms STKB_card_step

end Polyplets
