/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Compute

/-!
# r4 increment 3b — the packaged frontier state, and the three holes that remain

**UNCOMPILED. Written 2026-08-13 by scout/builder `r4-lean2`, which ran no Lean
on any machine.** See `results/r4/r4-lean2.md (deleted)`.

## What this file is and what its gate means

Unlike `r4_lean2_encode.lean`, this file is **not** claimed to be a proof. It
carries **exactly three `sorry`s**, each named and each corresponding to one
row of `results/r4/r4-lean.md (deleted)` §1.1. Its gate is therefore not "silence": it is

> zero `error:` lines, exactly three `declaration uses 'sorry'` warnings, and
> no other output.

Both halves are fail-closed. Fewer sorries than three means a hole was closed
without the ledger being updated; more means one was added; any other output
means a *statement* stopped type-checking, which is the failure mode this file
exists to catch. r3's L5 lane filed "complete written proofs, no step missing"
and produced nine errors at six sites; the discipline here is the opposite —
say in advance exactly where the argument is absent, and let the compile
confirm that everything around the absences is well-formed.

What the compile does settle, with no `sorry` involved:

- that `State H` really has `Fintype` and `DecidableEq` instances (the two
  `example`s below) — a state type with no `Fintype` is not a state type, and
  this is the kind of thing that silently fails at `H = 0` or on a `Pi` field;
- that `rowFin`'s in-range branch discharges its `Fin` bound by `omega`;
- that `encodeState` elaborates as a definition, so `encodeState_faithful` and
  `sufficiency` are statements about a real object rather than about `sorry`.

## The three holes, and why these three

- **HOLE 1 `labelFin_faithful`** — the `Fin H` packaging is injective on
  height-bounded prefixes, so `encodeCol`'s faithfulness
  (`r4_lean2_encode.lean`, claimed) transfers to the finite state. This is the
  *only* part of `results/r4/r4-adv-cost.md (deleted)` §5.2's E2 objection that the
  encode file does not address, and it is bookkeeping in the accurate sense:
  `rowFin` is injective on `[0, H)` and every label lies there.
- **HOLE 2 `strand_dead`** — r4-lean §1.1 D2, rated M there and singled out by
  the adversary as "a soundness *and* completeness claim about the death rule,
  i.e. a statement about columns the DP has not read yet". Stated here in the
  sharpest form I can state it: a prefix cell whose component misses the cut
  column reaches nothing in the future, ever.
- **HOLE 3 `sufficiency`** — r4-lean §1.1 D3, increment 2, stated with
  `encodeCol` equality as its hypothesis rather than the raw pair
  (`hcol`, `hrel`) the funnel probe's footer used. That is the composition
  point: `encode_faithful_colAt` converts one to the other, so increment 2 and
  increment 3 meet here and neither restates the other's interface.

## What is unattempted, and why it is not in this file

`step` (E3) and `step_correct` (E4) are **not** here, and I decline to write
their statements. A transition function has to be written against the
`reduction` lemma that increment 2 produces; stating it now would be guessing
at the shape of an object nobody has built, and a `def step := sorry` would
make every theorem downstream of it vacuous while looking like progress. The
same goes for `frontierT` (F1), `prefix_census` (F2) and `frontierT_eq_T` (G2).
`results/r4/r4-lean2.md (deleted)` §4 prices them as NOT ESTABLISHED rather than
guessing.

## Fragile points (mechanical risk, each with its repair)

1. `State H` is a bare product rather than a `structure`. Deliberate: a
   `structure` with a function field needs the `Fintype`/`DecidableEq` deriving
   handlers to fire, and a product gets both from `instFintypeProd`,
   `Pi.fintype` and `Fintype.decidablePiFintype`
   (`Data/Fintype/Defs.lean:204`). Cosmetic; increment 6 may promote it.
2. `labelFin` matches `lbl P c y : WithTop ℤ` against `Option ℤ` through a type
   ascription, relying on `WithTop α := Option α` unfolding. Repair:
   `WithTop.recTopCoe` (`Order/TypeTags.lean:59`, dual of `recBotCoe`).
3. `rowFin`'s `⟨y.toNat, by omega⟩` needs `omega` to relate `Int.toNat` to the
   `Fin` bound. It does support `Int.toNat`. Repair: `Int.toNat_lt'` by hand.
4. `decide (∃ p ∈ P, p.2 = 0)` needs `Finset.decidableExistsAndFinset`
   (`Data/Finset/Defs.lean:365`). Repair: `P.any fun p => p.2 = 0`.
5. `set_option linter.unusedVariables false` covers the holes section only in
   the sense that it appears after the definitions. Every hypothesis of a
   `sorry`-proved theorem is unused by construction, and one linter warning
   would corrupt the gate's exact warning count. Repair if the option name has
   drifted: delete the line and raise the expected warning count.

No `Fintype.card (State H)` check is included. The count is `(H+1)^H * 4`,
which is arithmetic, not something a compile needs to confirm, and a `decide`
over `Pi.fintype` is exactly the sort of kernel reduction that would fail the
gate for a reason having nothing to do with the mathematics.

## RED control (the gate script runs it)

In `rowFin`, weaken the range test `y < (H : ℤ)` to `y ≤ (H : ℤ)`. `omega` can
then no longer discharge `y.toNat < H`, so an `error:` line appears and the
gate must FAIL. This exercises the half of the gate that a sorry-count check
alone would not: that "no errors" is really being enforced.
-/

namespace Polyplets
namespace R4State

noncomputable section

-- BEGIN SHARED DEFS (byte-identical in both r4_lean2 files; the gate diffs them)

/-- Reachability by king steps confined to `S` — exactly the relation
`KingConnected` quantifies over (`Polyplets/Defs.lean:29`). An `abbrev` so that
`Relation.ReflTransGen`'s API and `Compute.lean`'s raw-form lemmas see through
it. -/
abbrev reach (S : Finset (ℤ × ℤ)) (a b : ℤ × ℤ) : Prop :=
  Relation.ReflTransGen (fun x y => x ∈ S ∧ y ∈ S ∧ kingAdj x y) a b

/-- The cells of `S` in column `c` — the cut column, i.e. the frontier. -/
def colAt (S : Finset (ℤ × ℤ)) (c : ℤ) : Finset (ℤ × ℤ) :=
  S.filter fun p => p.1 = c

/-- Every cell of `P` reaches the cut column from inside `P`: no component of
the prefix is stranded behind the cut. -/
def Unstranded (P : Finset (ℤ × ℤ)) (c : ℤ) : Prop :=
  ∀ a ∈ P, ∃ a' ∈ colAt P c, reach P a a'

/-- The rows of the cut column reachable from `(c, y)` inside `P`. Defined off
`Compute.lean`'s computable closure `reachSet` so that the bridge between the
`ReflTransGen` view and the closure view is made once, in `mem_rowCls`. -/
def rowCls (P : Finset (ℤ × ℤ)) (c y : ℤ) : Finset ℤ :=
  ((reachSet P (c, y)).filter fun q => q.1 = c).image Prod.snd

/-- **The label of a cut-column row**: the least row of the cut column in its
component, and `⊤` for a row the prefix does not occupy. This is the canonical
form — defined *by the relation*, so no relabeling normal-form theorem is
needed anywhere. -/
def lbl (P : Finset (ℤ × ℤ)) (c y : ℤ) : WithTop ℤ :=
  if (c, y) ∈ P then (rowCls P c y).min else ⊤

/-- **The frontier state's partition component**: the whole label function.
`encode_faithful` says this single object is a sufficient statistic for the
cut column's occupancy *and* its component structure. -/
def encodeCol (P : Finset (ℤ × ℤ)) (c : ℤ) : ℤ → WithTop ℤ :=
  fun y => lbl P c y

-- END SHARED DEFS

/-! ## The packaged state

The encode file's `encodeCol` is indexed by `ℤ` and is not a finite object. The
DP needs a `Fintype`. This section does the packaging and nothing else.
-/

/-- **The finite frontier state**: one label per row of the cut column, plus
the two sticky flags recording that the prefix has met the bottom and the top
row of the bounding box. A bare product rather than a `structure` so that
`Fintype` and `DecidableEq` come from existing instances (`instFintypeProd`,
`Pi.fintype`, `Fintype.decidablePiFintype`) rather than from a deriving
handler that has to fire on a function field. -/
abbrev State (H : ℕ) : Type := (Fin H → Option (Fin H)) × Bool × Bool

/-- A state type with no `DecidableEq` is not a state type. -/
example (H : ℕ) : DecidableEq (State H) := inferInstance

/-- A state type with no `Fintype` is not a state type. -/
example (H : ℕ) : Fintype (State H) := inferInstance

/-- Row index of a cut-column cell as an element of `Fin H`, when in range. -/
def rowFin (H : ℕ) (y : ℤ) : Option (Fin H) :=
  if h : 0 ≤ y ∧ y < (H : ℤ) then some ⟨y.toNat, by omega⟩ else none

/-- The label function of `r4_lean2_encode.lean`, packaged into `Fin H`-indexed
form. `WithTop ℤ` is `Option ℤ`, which is what the `match` reads. -/
def labelFin (H : ℕ) (P : Finset (ℤ × ℤ)) (c : ℤ) : Fin H → Option (Fin H) :=
  fun i =>
    match (lbl P c (i.val : ℤ) : Option ℤ) with
    | none => none
    | some m => rowFin H m

/-- **The packaged frontier state.** The flags are properties of the whole
prefix, not of the cut column, which is why they are carried separately: the
label function forgets them. -/
def encodeState (H : ℕ) (P : Finset (ℤ × ℤ)) (c : ℤ) : State H :=
  (labelFin H P c,
    decide (∃ p ∈ P, p.2 = 0),
    decide (∃ p ∈ P, p.2 = (H : ℤ) - 1))

/-! ## The three holes

Each statement below is claimed to type-check and is claimed to be *true*.
Neither claim is that it is proved: the proofs are absent and are named as
absent. The unused-variable linter is turned off from here down because every
hypothesis of a `sorry`-proved theorem is unused by construction, and a
linter warning would corrupt the gate's exact warning count.
-/

set_option linter.unusedVariables false

/-- **HOLE 1 — the `Fin H` packaging is faithful.** `r4_lean2_encode.lean`
claims `encodeCol` determines the cut column's occupancy and component
structure; this says the finite packaging loses nothing, given that the prefix
lies inside the bounding box. Forward: every label is the row of an occupied
cut-column cell, hence in `[0, H)`, where `rowFin` is injective, and every
out-of-range row is unoccupied in both prefixes so both labels are `⊤`.
Backward: `labelFin` is a function of `lbl`, so it needs no hypotheses at all.

This is the residue of `results/r4/r4-adv-cost.md (deleted)` §5.2's E2 objection that the
encode file does not touch, and it is the one part of it that really is
bookkeeping. -/
theorem labelFin_faithful (H : ℕ) (P P' : Finset (ℤ × ℤ)) (c : ℤ)
    (hP : ∀ p ∈ P, p.1 = c → 0 ≤ p.2 ∧ p.2 < (H : ℤ))
    (hP' : ∀ p ∈ P', p.1 = c → 0 ≤ p.2 ∧ p.2 < (H : ℤ)) :
    labelFin H P c = labelFin H P' c ↔ encodeCol P c = encodeCol P' c := by
  sorry

/-- **HOLE 2 — `strand_dead`, the death rule** (r4-lean §1.1 D2). A prefix cell
whose component misses the cut column can never reach anything placed later:
any king path from it into the future must cross the cut, and the crossing edge
plants a cell of its own component in the cut column
(`Polyplets/Finite.lean:61`, `exists_adj_cross_of_reflTransGen`, is the
committed lemma that does this). Soundness *and* completeness of the DP's
death rule is this one statement: the DP is entitled to discard such a prefix,
and is obliged to, because keeping it would count sets that never connect. -/
theorem strand_dead {P M : Finset (ℤ × ℤ)} {c : ℤ} {a b : ℤ × ℤ}
    (hP : ∀ p ∈ P, p.1 ≤ c) (hM : ∀ p ∈ M, c < p.1)
    (haP : a ∈ P) (hbM : b ∈ M)
    (hstr : ∀ a' ∈ colAt P c, ¬ reach P a a') :
    ¬ reach (P ∪ M) a b := by
  sorry

/-- **HOLE 3 — `sufficiency`** (r4-lean §1.1 D3, increment 2). The theorem the
whole programme rests on: two prefixes with the same encoded state are
interchangeable in front of any future. Stated with `encodeCol` equality rather
than with the raw pair (cut-column equality, restricted-reachability
agreement), because `encode_faithful_colAt` in `r4_lean2_encode.lean` converts
one to the other — so increment 2 and increment 3 meet exactly here, and
neither has to restate the other's interface.

The funnel probe proved the two halves this needs
(`redReach_of_reach`, `reach_of_redReach`, both compiled 2026-08-13). What is
missing is the packaging into an `iff` on `colAt P c ∪ M` plus the degenerate
cases `P = ∅` and `M = ∅`. -/
theorem sufficiency {P P' M : Finset (ℤ × ℤ)} {c : ℤ}
    (hP : ∀ p ∈ P, p.1 ≤ c) (hP' : ∀ p ∈ P', p.1 ≤ c) (hM : ∀ p ∈ M, c < p.1)
    (hu : Unstranded P c) (hu' : Unstranded P' c)
    (henc : encodeCol P c = encodeCol P' c) :
    KingConnected (P ∪ M) ↔ KingConnected (P' ∪ M) := by
  sorry

/-! ## Hole ledger

Exactly three, and the gate script counts them:

| # | name | r4-lean §1.1 row | why it is open |
|---|---|---|---|
| 1 | `labelFin_faithful` | E2 (residue) | unattempted; expected short |
| 2 | `strand_dead` | D2 | unattempted; the adversary rates it non-trivial |
| 3 | `sufficiency` | D3 | increment 2; the funnel probe supplies both halves |

Not stated at all, deliberately: `step` (E3), `step_correct` (E4),
`frontierT` (F1), `prefix_census` (F2), `completion` (G1), `frontierT_eq_T`
(G2), pins (H1). A `def step := sorry` would make everything downstream of it
vacuous while looking like progress. `results/r4/r4-lean2.md (deleted)` §4 prices those
rows as NOT ESTABLISHED rather than guessing at them.
-/

end

end R4State
end Polyplets
