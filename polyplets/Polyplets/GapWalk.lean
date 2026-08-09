/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.NormNum

/-!
# The two-class gap walk, and the all-pairs cluster weights it computes

The transfer object behind the depth-1 closure of the below-onset defect
(`results/onset-defect-depth1-closed.md`, campaign *Severance* W4). A cluster
whose every row holds exactly two cells is traversed row by row; the state is
the **gap** `g ≥ 1` between the two cells of the current row together with a
**class** flag saying whether the partial animal below is already joined
(`J`) or still consists of two pending components (`P`). The bulk transition
multiplicities of the walk are the familiar `(1, 2, 3, 2, 1)` kernel with
exceptional rows at `g ≤ 2`; here they are not written down as a kernel but
**recomputed from the geometry**, exactly as the reference implementation does.

The spec transcribed by this file is `experiments/depth1_gap_walk.py`:

* `stepMul` ↔ `transitions(g, c, gp_max)` — the count, for a source state
  `(g, c)` and a target state `(g', c')`, of normalized placements of the next
  pair row;
* `startInterior` / `startBare` ↔ the two start vectors `dp_int` / `dp_bare`
  (a fixed contact cell `p` below, resp. the first pair row alone);
* `qEnd` / `bareEnd` ↔ `q_end` / `bare_end` — closing with a free contact row
  above, resp. with nothing above;
* `walkFamilies` ↔ `walk_families(L)`, `gmax = 2L + 3`, returning the triples
  `(W(2^l), W^b(2^l), W^p(2^l))` for `l = 1 .. L`.

The one place where the transcription is not literal is `joined`, which
replaces the Python union–find over `{A, B, x, y}` by the boolean it computes:
`A` and `B` (the two pending components below) are joined only *through* the
two new cells `x, y`, so the only `x`–`y` paths are `x–A–y` and `x–B–y`, and
`x ∼ y` iff `x` and `y` share a contact. Everything else is line-for-line.

## What is proved here

`walk_table` evaluates the walk at `L = 6` and the eighteen corollaries below
state the resulting family weights against the banked literals, one theorem per
number:

* interior `W(2^l)`: 25, 339, 4778, 68314, 981085, 14115141;
* bottom edge `W^b(2^l)`: 5, 66, 919, 13103, 187965, 2703074;
* pure `W^p(2^l)`: 1, 13, 177, 2515, 36021, 517701.

Provenance of the literals: rows `e = 0`, `k = 1 .. 6` of the verified table
`results/severance_w3_families_K19_e3.txt` (columns `sig bb pp`), the same
values that `experiments/depth1_gap_walk.py` prints and cross-checks against
`cluster_weight_dp.KNOWN_WEIGHTS` (`l ≤ 5`) and against a fresh `count_stack`
DP holdout at `l = 6` (`2703074`, `517701`); `l ≤ 3` agree with the
`native_decide` leaves `V 1 1 = 25`, `V 2 2 = 339`, `V 3 3 = 4778`,
`Vᵗ 1 1 = 5`, `Vᵗ 2 2 = 66`, `Vᵗ 3 3 = 919` of `Weights.lean` /
`Weights3.lean` / `Weights3Heavy.lean`.

## Open

The bijection between cluster configurations (the `CFGV` world of
`Weights.lean` / `WeightsChunk.lean`) and walk paths is **not** formalized
here: `walk_table` certifies the walk's own arithmetic. The agreement with
`V ℓ ℓ` / `Vᵗ ℓ ℓ` (and the pure `Vp ℓ ℓ`) at `ℓ ≤ 3` is now *proved* as
literal equalities in `GapWalkBridge.lean` (campaign Notary), which also pins
the walk to the two-source table at `l ≤ 19` and closes the depth-1 assembly
at `k ≤ 8` inside Lean. The `g ≤ gmax` truncation argument is now **closed**
(campaign Notary, piece T): `GapWalkTrunc.lean` proves every cap `M ≥ 2L + 3`
emits the same family triples (`walkFamiliesCap_exact`), via the vanishing
rows of `GapWalkRows.lean` and the iterated-function form of
`GapWalkCanon.lean`. Supplying the bijection itself remains open; it is
priced in `docs/notary-kernel-scoping.md` (piece B).
-/

namespace Polyplets
namespace GapWalk

/-! ## States -/

/-- A walk state: the gap `g ≥ 1` between the two cells of the current pair
row, and the class flag (`true` = `J`, the animal below is joined;
`false` = `P`, two pending components). -/
abbrev St : Type := Nat × Bool

/-- The state list for gaps `1 ≤ g ≤ gmax`, both classes. -/
def states (gmax : Nat) : List St :=
  (List.range gmax).flatMap fun i => [(i + 1, true), (i + 1, false)]

/-- King-contact test: a cell at `t` touches a cell at `0`. -/
def near (t : ℤ) : Bool := t.natAbs ≤ 1

/-- Connectivity of the two new cells through the two pending components,
the boolean computed by the Python union–find on `{A, B, x, y}`: `A` and `B`
are joined only through `x` and `y`, so `x ∼ y` iff they share a contact. -/
def joined (xA xB yA yB : Bool) : Bool := (xA && yA) || (xB && yB)

/-! ## The transition table -/

/-- Multiplicity of the transition `(g, c) → (g', c')`: the number of
normalized placements `a` of the next pair row `{a, a + g'}` that keep the
animal legal and produce class `c'`. Transcribes `transitions(g, c, ·)`, whose
`a` ranges over `-(g' + 2) .. g + 2`. -/
def stepMul (g : Nat) (cJ : Bool) (gp : Nat) (ncJ : Bool) : Nat :=
  ((List.range (g + gp + 5)).filter fun i : Nat =>
    let a : ℤ := (i : ℤ) - ((gp : ℤ) + 2)
    let G : ℤ := g
    let t0 : ℤ := a
    let t1 : ℤ := a + (gp : ℤ)
    let x0 := near t0
    let x1 := near t1
    let y0 := near (t0 - G)
    let y1 := near (t1 - G)
    let touch0 := x0 || x1
    let touchg := y0 || y1
    let ok := if cJ then touch0 || touchg else touch0 && touchg
    let nc : Bool :=
      if gp = 1 then true
      else if cJ then (x0 || y0) && (x1 || y1)
      else joined x0 y0 x1 y1
    ok && nc == ncJ).length

/-- One row of the walk: `dp` is the value vector aligned with `states gmax`. -/
def stepDP (gmax : Nat) (dp : List (St × Nat)) : List (St × Nat) :=
  (states gmax).map fun t =>
    (t, (dp.map fun p => p.2 * stepMul p.1.1 p.1.2 t.1 t.2).sum)

/-! ## Start vectors and end functionals -/

/-- Interior start: the first pair row placed against the fixed contact cell
`p = (0,0)` below (`dp_int`). -/
def startInterior (gmax : Nat) : List (St × Nat) :=
  (states gmax).map fun s =>
    (s, ((List.range (s.1 + 5)).filter fun i : Nat =>
      let a : ℤ := (i : ℤ) - ((s.1 : ℤ) + 2)
      let t0 : ℤ := a
      let t1 : ℤ := a + (s.1 : ℤ)
      let nc : Bool := if s.1 = 1 then true else near t0 && near t1
      (near t0 || near t1) && nc == s.2).length)

/-- Bare start: the first pair row alone, one normalized placement per gap
(`dp_bare`). -/
def startBare (gmax : Nat) : List (St × Nat) :=
  (states gmax).map fun s => (s, if s.2 == (s.1 == 1) then 1 else 0)

/-- Close with the free single-cell contact row `q` above (`q_end`). -/
def qEnd (dp : List (St × Nat)) : Nat :=
  (dp.map fun p =>
    if p.1.2 then p.2 * (if p.1.1 ≤ 2 then p.1.1 + 3 else 6)
    else if p.1.1 ≤ 2 then p.2 * (3 - p.1.1) else 0).sum

/-- Close with nothing above: the stack itself must already be one
component (`bare_end`). -/
def bareEnd (dp : List (St × Nat)) : Nat :=
  (dp.map fun p => if p.1.2 then p.2 else 0).sum

/-! ## The families -/

/-- `walk_families`' loop: emit the triple, then advance both DPs. -/
def walkAux : Nat → Nat → List (St × Nat) → List (St × Nat) → List (Nat × Nat × Nat)
  | 0, _, _, _ => []
  | n + 1, gmax, di, db =>
      (qEnd di, qEnd db, bareEnd db) :: walkAux n gmax (stepDP gmax di) (stepDP gmax db)

/-- `(W(2^l), W^b(2^l), W^p(2^l))` for `l = 1 .. L`, via the gap walk with
gap cap `gmax = 2L + 3` (`walk_families`). -/
def walkFamilies (L : Nat) : List (Nat × Nat × Nat) :=
  walkAux L (2 * L + 3) (startInterior (2 * L + 3)) (startBare (2 * L + 3))

/-- Interior all-pairs weight `W(2^l)` from the `L`-row walk. -/
def W (L l : Nat) : Nat := ((walkFamilies L).getD (l - 1) (0, 0, 0)).1

/-- Bottom-edge all-pairs weight `W^b(2^l)` (= top edge, by palindromy). -/
def Wb (L l : Nat) : Nat := ((walkFamilies L).getD (l - 1) (0, 0, 0)).2.1

/-- Pure all-pairs weight `W^p(2^l)` from the `L`-row walk. -/
def Wp (L l : Nat) : Nat := ((walkFamilies L).getD (l - 1) (0, 0, 0)).2.2

set_option maxRecDepth 10000 in
set_option maxHeartbeats 2000000 in
-- six walk rows over 30 states, each transition multiplicity recounted from the
-- geometry: ~10^5 kernel reductions, an order of magnitude past the default
/-- The walk's own output at `L = 6`, evaluated in the kernel. -/
theorem walk_table :
    walkFamilies 6 =
      [(25, 5, 1), (339, 66, 13), (4778, 919, 177), (68314, 13103, 2515),
        (981085, 187965, 36021), (14115141, 2703074, 517701)] := by
  decide

/-! ## The eighteen banked values, one theorem each

Literals from `results/severance_w3_families_K19_e3.txt`, rows `e = 0`,
`k = 1 .. 6`; `l = 6` is the fresh-DP holdout of the depth-1 campaign
(`experiments/depth1_gap_walk.py`, `count_stack` cross-check). -/

theorem W_one : W 6 1 = 25 := by rw [W, walk_table]; rfl

theorem W_two : W 6 2 = 339 := by rw [W, walk_table]; rfl

theorem W_three : W 6 3 = 4778 := by rw [W, walk_table]; rfl

theorem W_four : W 6 4 = 68314 := by rw [W, walk_table]; rfl

theorem W_five : W 6 5 = 981085 := by rw [W, walk_table]; rfl

theorem W_six : W 6 6 = 14115141 := by rw [W, walk_table]; rfl

theorem Wb_one : Wb 6 1 = 5 := by rw [Wb, walk_table]; rfl

theorem Wb_two : Wb 6 2 = 66 := by rw [Wb, walk_table]; rfl

theorem Wb_three : Wb 6 3 = 919 := by rw [Wb, walk_table]; rfl

theorem Wb_four : Wb 6 4 = 13103 := by rw [Wb, walk_table]; rfl

theorem Wb_five : Wb 6 5 = 187965 := by rw [Wb, walk_table]; rfl

theorem Wb_six : Wb 6 6 = 2703074 := by rw [Wb, walk_table]; rfl

theorem Wp_one : Wp 6 1 = 1 := by rw [Wp, walk_table]; rfl

theorem Wp_two : Wp 6 2 = 13 := by rw [Wp, walk_table]; rfl

theorem Wp_three : Wp 6 3 = 177 := by rw [Wp, walk_table]; rfl

theorem Wp_four : Wp 6 4 = 2515 := by rw [Wp, walk_table]; rfl

theorem Wp_five : Wp 6 5 = 36021 := by rw [Wp, walk_table]; rfl

theorem Wp_six : Wp 6 6 = 517701 := by rw [Wp, walk_table]; rfl

end GapWalk
end Polyplets
