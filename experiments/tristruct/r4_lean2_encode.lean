/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Compute

/-!
# r4 increment 3a — the encoding layer's faithfulness theorem

**UNCOMPILED. Written 2026-08-13 by scout/builder `r4-lean2`, which ran no Lean
on any machine. Nothing in this file is a theorem until a build says so.** See
`results/r4/r4-lean2.md (deleted)`.

## Why this file and not increment 2

`experiments/tristruct/r4_lean_funnel_probe.lean` compiled on 2026-08-13
(gate A silent, exit 0, `[propext, Classical.choice, Quot.sound]`, no
`sorryAx`), retiring the partition-sufficiency crux. `results/r4/r4-adv-cost.md (deleted)`
§5.2 then named the one place the programme is still priced on nothing and
attacked on nothing: **the encoding layer, E2 `encode_faithful`**, and
specifically its reverse direction, which the adversary expects to need "a
quotient argument, and the standard place this kind of development stalls".
This file goes there.

## The design decision the compile is testing

r3 and r4-lean both describe the state as a *canonical label vector* and expect
to prove that canonicalization is a normal form for partitions under
relabeling. That is the quotient argument, and it is avoidable. Here the label
of a cut-column row is defined **by the relation itself**:

> `lbl P c y` = the least row `y'` of column `c` such that `(c, y')` is
> king-reachable from `(c, y)` inside the prefix `P` — and `⊤` if `(c, y) ∉ P`.

Two prefixes then have the same label function exactly when they have the same
cut-column occupancy and the same restricted reachability, because
`reach P` is an equivalence relation on the cut column (`refl` / `reach_symm` /
`ReflTransGen.trans`) and "equal least element of the class" is "same class".
No relabeling, no quotient, no normal-form theorem. If this compiles, the
adversary's E2 risk is not reduced — it is *dissolved*, and `encode_faithful`
becomes a ~90-line lemma chain with no induction in it at all.

**That last sentence is a claim about UNCOMPILED source and is exactly the kind
of claim r3's L5 lane got wrong at nine errors and six sites.** The gate script
is the test.

## What this file reuses rather than rebuilds

`Polyplets/Compute.lean` already proves king-reachability equals a computable
closure — `reachSet_sound` (:83), `reachSet_complete` (:144),
`iterate_stepExpand_subset` (:57), `mem_iterate_self` (:71), all committed and
sorry-free. `rowCls` is defined off `reachSet` so that `mem_rowCls` is the only
place the two views are bridged, once. Nothing here re-proves connectivity
machinery.

`kingAdj_symm` and `reach_symm` are copied **verbatim** from the funnel probe,
where they elaborated. They are duplicated rather than imported because a file
under `experiments/` is not a module and cannot be imported; increment 6 merges
the probe, this file and the state file into one module under `Polyplets/`.

## What is deliberately NOT here

No `Fin H` packaging, no `Fintype`, no flags, no transition function, no fold,
no pins. Those are `r4_lean2_state.lean` (statements, three named holes) and
increments 4-6. The `sufficiency` theorem this encoding exists to serve is
stated in the state file and is **not** proved anywhere yet.

## Fragile points (mechanical risk, each with its repair)

1. `noncomputable section`. Used rather than per-definition `noncomputable`
   because whether `Finset.min` on `WithTop ℤ` resolves to a computable
   `LinearOrder` instance in this Mathlib is NOT ESTABLISHED — `Compute.lean`'s
   `box` docstring records that `Finset.Icc` on `ℤ` does not. A section is
   correct either way. Repair if the section is unwanted: drop it and add
   `noncomputable` only where the compiler asks.
2. `unfold lbl` + `rw [if_pos …]` / `rw [if_neg …]` — the standard failure is
   the `Decidable` instance in the goal not being the one `if_pos` expects.
   Repair: `split_ifs` / `by_cases` instead of `rw`. This is the idiom the
   funnel probe used successfully on `fnl`, which is why it is used here.
3. `reach` is an `abbrev`, as in the probe, so that `Relation.ReflTransGen`'s
   API and `Compute.lean`'s raw-form lemmas unify with it without unfolding.
4. `mem_rowCls` applies `reachSet_sound` / `reachSet_complete` /
   `iterate_stepExpand_subset` to a hypothesis stated with `reachSet`, relying
   on `reachSet`'s delta-unfolding. Repair: `simp only [reachSet] at *` first.
5. Names verified by grep against the vendored mathlib at `v4.31.0` on
   2026-08-13, not by elaboration: `Finset.min` (`Data/Finset/Max.lean:110`,
   valued in `WithTop α`, `⊤` on `∅` — note **`WithTop`, not `WithBot`**),
   `Finset.min_of_mem` (:134), `Finset.min_eq_top` (:142),
   `Finset.mem_of_min` (:145), `Finset.notMem_empty`
   (`Data/Finset/Empty.lean:104`), `Finset.mem_filter`
   (`Data/Finset/Filter.lean:127`), `Finset.mem_image`
   (`Data/Finset/Image.lean:284`), `Finset.ext` (`Data/Finset/Defs.lean:145`).
   `Prod.ext_iff` and `Relation.ReflTransGen.head` are verified by *use* in
   already-compiled files in this tree (`Compute.lean:186`, funnel probe:135),
   which is stronger evidence than a grep.
6. The `#guard_msgs` axiom pin at the foot. A mismatch there is a fact about
   the axiom footprint, **not** a hole in an argument. The gate script
   classifies a pin-only failure separately for exactly this reason. Unlike the
   funnel probe's pin, this one is a genuine guess: no `Classical.choice` is
   used explicitly here, but `Finset.min`'s order instances may drag it in.

## RED controls (the gate script runs 1 and 2)

1. *Over-merging.* In `rowCls`, replace `reachSet P (c, y)` with `P` — every
   cut-column cell then lands in every class, so all labels collapse and the
   state cannot distinguish two components from one. `mem_rowCls` must fail:
   `reachSet_sound` no longer applies. This is the semantic heart of the file
   and the mutation that matters.
2. *Occupancy guard.* In `lbl`, replace `else ⊤` with
   `else (rowCls P c y).min` — an absent row then gets a real label, and
   `lbl_eq_top_iff` becomes false. `lbl_eq_top` must fail.
3. *Symmetry.* In `rowCls_eq_of_reach`, drop the `reach_symm h` and use `h`
   twice. One direction of the class equality must then fail. Documented for a
   later pass, not run by the script — it costs a third elaboration and
   controls 1 and 2 already bracket the two things this file claims.
-/

namespace Polyplets
namespace R4Encode

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

/-! ## Layer A — relation hygiene (verbatim from the funnel probe) -/

/-- King adjacency is symmetric. -/
lemma kingAdj_symm {p q : ℤ × ℤ} (h : kingAdj p q) : kingAdj q p := by
  obtain ⟨hne, h1, h2⟩ := h
  refine ⟨hne.symm, ?_, ?_⟩
  · rwa [abs_sub_comm]
  · rwa [abs_sub_comm]

/-- Reachability inside `S` is symmetric, king adjacency being symmetric. -/
lemma reach_symm {S : Finset (ℤ × ℤ)} {a b : ℤ × ℤ} (h : reach S a b) :
    reach S b a := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | @tail u v _ huv ih =>
      exact Relation.ReflTransGen.head ⟨huv.2.1, huv.1, kingAdj_symm huv.2.2⟩ ih

/-! ## Layer R — the class of a cut-column row -/

/-- **The one bridge between the two views of reachability.** For an occupied
cut-column cell, membership in its row class is exactly "occupied, and reached
inside `P`". Everything downstream uses this and never touches `reachSet`
again. -/
lemma mem_rowCls {P : Finset (ℤ × ℤ)} {c y : ℤ} (hy : (c, y) ∈ P) {y' : ℤ} :
    y' ∈ rowCls P c y ↔ (c, y') ∈ P ∧ reach P (c, y) (c, y') := by
  simp only [rowCls, Finset.mem_image, Finset.mem_filter]
  constructor
  · rintro ⟨q, ⟨hqR, hq1⟩, hq2⟩
    have hq : q = (c, y') := by rw [Prod.ext_iff]; exact ⟨hq1, hq2⟩
    subst hq
    exact ⟨iterate_stepExpand_subset hy P.card hqR,
      reachSet_sound hy P.card _ hqR⟩
  · rintro ⟨hmem, hr⟩
    exact ⟨(c, y'), ⟨reachSet_complete hy hr, rfl⟩, rfl⟩

/-- A row is in its own class. -/
lemma self_mem_rowCls {P : Finset (ℤ × ℤ)} {c y : ℤ} (hy : (c, y) ∈ P) :
    y ∈ rowCls P c y :=
  (mem_rowCls hy).mpr ⟨hy, Relation.ReflTransGen.refl⟩

/-- **Classes of related rows coincide.** This is where the equivalence-relation
structure of `reach P` does the work that a quotient construction would
otherwise have to do: symmetry from `reach_symm`, transitivity from
`ReflTransGen.trans`. -/
lemma rowCls_eq_of_reach {P : Finset (ℤ × ℤ)} {c y z : ℤ}
    (hy : (c, y) ∈ P) (hz : (c, z) ∈ P) (h : reach P (c, y) (c, z)) :
    rowCls P c y = rowCls P c z := by
  ext y'
  rw [mem_rowCls hy, mem_rowCls hz]
  constructor
  · rintro ⟨hm, hr⟩
    exact ⟨hm, Relation.ReflTransGen.trans (reach_symm h) hr⟩
  · rintro ⟨hm, hr⟩
    exact ⟨hm, Relation.ReflTransGen.trans h hr⟩

/-! ## Layer L — the label -/

/-- An occupied row has a real label. -/
lemma lbl_ne_top {P : Finset (ℤ × ℤ)} {c y : ℤ} (hy : (c, y) ∈ P) :
    lbl P c y ≠ ⊤ := by
  unfold lbl
  rw [if_pos hy]
  intro hE
  rw [Finset.min_eq_top] at hE
  have hmem := self_mem_rowCls hy
  rw [hE] at hmem
  exact Finset.notMem_empty y hmem

/-- An unoccupied row has label `⊤`. -/
lemma lbl_eq_top {P : Finset (ℤ × ℤ)} {c y : ℤ} (hy : (c, y) ∉ P) :
    lbl P c y = ⊤ := by
  unfold lbl
  rw [if_neg hy]

/-- **The label reads off occupancy.** -/
lemma lbl_eq_top_iff {P : Finset (ℤ × ℤ)} {c y : ℤ} :
    lbl P c y = ⊤ ↔ (c, y) ∉ P :=
  ⟨fun h hy => lbl_ne_top hy h, lbl_eq_top⟩

/-- **The label reads off the component structure.** Two occupied cut-column
rows carry the same label exactly when they are joined inside the prefix. The
forward direction is the one the adversary expected to need a normal-form
argument; with the label defined as the least element of the class it is
`Finset.mem_of_min` plus symmetry and transitivity. -/
lemma lbl_eq_iff {P : Finset (ℤ × ℤ)} {c y z : ℤ}
    (hy : (c, y) ∈ P) (hz : (c, z) ∈ P) :
    lbl P c y = lbl P c z ↔ reach P (c, y) (c, z) := by
  unfold lbl
  rw [if_pos hy, if_pos hz]
  constructor
  · intro h
    obtain ⟨m, hm⟩ := Finset.min_of_mem (self_mem_rowCls hy)
    have hmz : (rowCls P c z).min = (m : WithTop ℤ) := by rw [← h]; exact hm
    have h1 := ((mem_rowCls hy).mp (Finset.mem_of_min hm)).2
    have h2 := ((mem_rowCls hz).mp (Finset.mem_of_min hmz)).2
    exact Relation.ReflTransGen.trans h1 (reach_symm h2)
  · intro h
    rw [rowCls_eq_of_reach hy hz h]

/-! ## The head theorem of the increment -/

/-- **`encode_faithful`, row-indexed form.** The label function determines, and
is determined by, exactly two things: which rows of the cut column the prefix
occupies, and which of those rows are joined inside the prefix. Nothing else
about the past survives, and nothing that the frontier DP needs is lost. -/
theorem encode_faithful (P P' : Finset (ℤ × ℤ)) (c : ℤ) :
    encodeCol P c = encodeCol P' c ↔
      ((∀ y : ℤ, (c, y) ∈ P ↔ (c, y) ∈ P') ∧
        ∀ y z : ℤ, (c, y) ∈ P → (c, z) ∈ P →
          (reach P (c, y) (c, z) ↔ reach P' (c, y) (c, z))) := by
  constructor
  · intro h
    have hpt : ∀ y : ℤ, lbl P c y = lbl P' c y := fun y => congrFun h y
    have hocc : ∀ y : ℤ, (c, y) ∈ P ↔ (c, y) ∈ P' := by
      intro y
      constructor
      · intro hy
        by_contra hy'
        exact lbl_ne_top hy ((hpt y).trans (lbl_eq_top hy'))
      · intro hy'
        by_contra hy
        exact lbl_ne_top hy' ((hpt y).symm.trans (lbl_eq_top hy))
    refine ⟨hocc, ?_⟩
    intro y z hy hz
    rw [← lbl_eq_iff hy hz,
      ← lbl_eq_iff ((hocc y).mp hy) ((hocc z).mp hz), hpt y, hpt z]
  · rintro ⟨hocc, hrel⟩
    funext y
    show lbl P c y = lbl P' c y
    by_cases hy : (c, y) ∈ P
    · have hy' : (c, y) ∈ P' := (hocc y).mp hy
      have hcls : rowCls P c y = rowCls P' c y := by
        ext y'
        rw [mem_rowCls hy, mem_rowCls hy']
        constructor
        · rintro ⟨hm, hr⟩
          exact ⟨(hocc y').mp hm, (hrel y y' hy hm).mp hr⟩
        · rintro ⟨hm, hr⟩
          have hmP : (c, y') ∈ P := (hocc y').mpr hm
          exact ⟨hmP, (hrel y y' hy hmP).mpr hr⟩
      unfold lbl
      rw [if_pos hy, if_pos hy', hcls]
    · have hy' : (c, y) ∉ P' := fun h' => hy ((hocc y).mpr h')
      rw [lbl_eq_top hy, lbl_eq_top hy']

/-! ## The interface to `sufficiency`

`encode_faithful` is stated on rows because that is how the label function is
indexed. The `sufficiency` theorem (increment 2, still unproved) wants its
hypotheses as a `colAt` equality and a relation agreement quantified over
`colAt`. These two lemmas are the translation, so that the two increments
compose without either restating the other's interface. -/

/-- Membership in the cut column. -/
lemma mem_colAt {S : Finset (ℤ × ℤ)} {c : ℤ} {p : ℤ × ℤ} :
    p ∈ colAt S c ↔ p ∈ S ∧ p.1 = c :=
  Finset.mem_filter

/-- Membership in the cut column, for a cell given by its row. -/
lemma mk_mem_colAt {S : Finset (ℤ × ℤ)} {c y : ℤ} :
    ((c, y) : ℤ × ℤ) ∈ colAt S c ↔ (c, y) ∈ S := by
  rw [mem_colAt]
  exact ⟨fun h => h.1, fun h => ⟨h, rfl⟩⟩

/-- Cut-column equality is row-wise occupancy agreement. -/
lemma colAt_eq_iff {P P' : Finset (ℤ × ℤ)} {c : ℤ} :
    colAt P c = colAt P' c ↔ ∀ y : ℤ, (c, y) ∈ P ↔ (c, y) ∈ P' := by
  constructor
  · intro h y
    rw [← mk_mem_colAt (S := P) (c := c) (y := y), h, mk_mem_colAt]
  · intro h
    ext p
    obtain ⟨x, y⟩ := p
    rw [mem_colAt, mem_colAt]
    constructor
    · rintro ⟨hp, hp1⟩
      -- `hp1 : (x, y).1 = c` is `x = c` only up to projection reduction, so it
      -- is retyped before `subst`; `subst hp1` on the raw form can fail.
      have hx : x = c := hp1
      subst hx
      exact ⟨(h y).mp hp, rfl⟩
    · rintro ⟨hp, hp1⟩
      have hx : x = c := hp1
      subst hx
      exact ⟨(h y).mpr hp, rfl⟩

/-- **`encode_faithful`, in the form `sufficiency` will consume it.** -/
theorem encode_faithful_colAt (P P' : Finset (ℤ × ℤ)) (c : ℤ) :
    encodeCol P c = encodeCol P' c ↔
      (colAt P c = colAt P' c ∧
        ∀ a ∈ colAt P c, ∀ b ∈ colAt P c, (reach P a b ↔ reach P' a b)) := by
  rw [encode_faithful]
  constructor
  · rintro ⟨hocc, hrel⟩
    refine ⟨colAt_eq_iff.mpr hocc, ?_⟩
    rintro a ha b hb
    obtain ⟨haP, ha1⟩ := mem_colAt.mp ha
    obtain ⟨hbP, hb1⟩ := mem_colAt.mp hb
    obtain ⟨ax, ay⟩ := a
    obtain ⟨bx, bz⟩ := b
    -- retyped before `subst`, as in `colAt_eq_iff`
    have hax : ax = c := ha1
    have hbx : bx = c := hb1
    subst hax
    subst hbx
    exact hrel ay bz haP hbP
  · rintro ⟨hcol, hrel⟩
    have hocc := colAt_eq_iff.mp hcol
    refine ⟨hocc, ?_⟩
    intro y z hy hz
    exact hrel (c, y) (mk_mem_colAt.mpr hy) (c, z) (mk_mem_colAt.mpr hz)

end

/-! ## Axiom footprint

A mismatch here is a fact about the footprint, **not** a hole in an argument;
the gate script reports a pin-only failure separately. Unlike the funnel
probe's pin this one is a genuine guess — nothing in this file invokes choice
explicitly, but `Finset.min`'s order instances on `WithTop ℤ` may.
-/

/-- info: 'Polyplets.R4Encode.encode_faithful_colAt' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms encode_faithful_colAt

end R4Encode
end Polyplets
