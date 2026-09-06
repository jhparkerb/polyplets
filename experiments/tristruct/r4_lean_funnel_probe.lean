/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Finite

/-!
# r4 increment 1 — the funnel probe

**UNCOMPILED. Written 2026-08-12 by scout `r4-lean`, which ran no Lean on any
machine. Nothing in this file is a theorem until a build says so.** See
`results/r4/r4-lean.md (deleted)`, job request R4-LEAN-JOB-1.

## What this file is for

It is a *calibration* increment for the definition-level theorem (r3's L3-5):
proving that the abstract frontier recurrence counts exactly the king-connected
`n`-cell sets of height exactly `H`. It proves nothing about the recurrence.
It tests one question and is sized to answer only that:

> Does the frontier state's **sufficiency for the past** reduce to a
> single-step lemma discharged by `Relation.ReflTransGen.lift'`, or does it
> require a hand-rolled path-splitting induction over the vertex list of a
> king walk?

r3 (`results/triangle-r3-l3-proofscope.md (deleted)` §4, §7) identified the
partition-sufficiency induction as the load-bearing risk of the whole
programme and could not calibrate it. The construction below claims the answer
is the first: funnel every prefix cell to a representative in the cut column,
and the induction is Mathlib's (`Mathlib/Logic/Relation.lean:737`), leaving a
four-case single-step lemma (`redStep_of_step`) as the only content.

**If this file compiles, the crux is a day, not a month, and the residual risk
of the programme moves to the state-encoding layer. If `redStep_of_step` fails
with `unsolved goals`, the claim above is wrong and the schedule reverts to
r3's — which is exactly the information the increment is bought to get.** A
failure naming an identifier is neither answer; see "fragile points".

## What is deliberately NOT here

No `State` type, no `Fintype`, no label vector, no transition function, no
fold, no `frontierT`, no `native_decide` pin, no cell counting. Those are
increments 2-6. The `sufficiency` corollary this construction is aimed at is
stated as a comment at the foot of the file and is *not* proved here: it needs
the `reduction` lemma (both directions plus the funnel-inverse bookkeeping),
which is increment 2.

## Fragile points (mechanical risk, each with its repair)

1. `open scoped Classical in` before `fnl` — needed for the `dite` on a
   `Prop`-valued existential. If the scoped-instance form has drifted, replace
   the definition body with `by classical exact ...` and change every
   `unfold fnl` below to `simp only [fnl]`.
2. `unfold fnl` + `rw [if_pos/if_neg/dif_pos/dif_neg]` — the standard failure
   is the `Decidable` instance in the goal not being syntactically the one
   `dif_pos` expects. Repair: `split` / `split_ifs` instead of `rw`.
3. `reach` is an `abbrev`, not a `def`, on purpose: dot-notation
   (`.trans`, `.single`) and `induction` must see through it to
   `Relation.ReflTransGen`. If the linter objects to a reducible `Prop`
   abbreviation, make it a `def` and insert `unfold reach` at the head of
   `reach_symm` and `reach_of_redStep`.
4. `Relation.ReflTransGen.cases_head` (`Mathlib/Logic/Relation.lean:477`),
   `.mono` (703), `.lift'` (737), `reflTransGen_closed` (742),
   `Finset.subset_union_left` / `_right`, `Finset.mem_union_left` / `_right`,
   `abs_sub_comm`, `abs_le` — names verified by grep against the vendored
   mathlib at `v4.31.0` on 2026-08-12, not by elaboration.
5. The `#guard_msgs` axiom pin at the foot. A mismatch there is a fact about
   the axiom footprint, **not** a hole in an argument, and must not be read as
   one.

## RED controls (a referee corrupts, reruns, watches it notice)

1. *Stencil:* in `cut_edge_cols`, weaken `kingAdj`'s x-bound use by replacing
   `have h := hadj.2.1` with `have h := hadj.2.2` (the y-bound). `omega` must
   then fail — the conclusion is about columns and no longer follows.
2. *Sufficiency:* in `redStep`, delete the `reach P x y` conjunct from the
   first clause (i.e. let *any* two cut-column cells count as joined).
   `redStep_of_step` still compiles — this mutation is *sound-direction* only —
   but `reach_of_redStep` must fail, which is the point: it is the clause that
   stops the state from over-merging.
3. *Death rule:* in `Unstranded`, replace `∃ a' ∈ colAt P c` with
   `∃ a' ∈ P`. `redStep_of_step`'s first case must then fail, because
   `fnl_mem_col` no longer lands in the cut column.

Control 1 is the only one that is free (one token). Controls 2 and 3 cost a
second and third elaboration each and are for the job's second pass, not the
first.
-/

namespace Polyplets
namespace R4Funnel

/-- Reachability by king steps confined to `S`. This is exactly the relation
`KingConnected` quantifies over (`Polyplets/Defs.lean:29`); it is an `abbrev`
so that `Relation.ReflTransGen`'s API and `induction` see through it. -/
abbrev reach (S : Finset (ℤ × ℤ)) (a b : ℤ × ℤ) : Prop :=
  Relation.ReflTransGen (fun x y => x ∈ S ∧ y ∈ S ∧ kingAdj x y) a b

/-- The cells of `S` in column `c` — the cut column, i.e. the frontier. -/
def colAt (S : Finset (ℤ × ℤ)) (c : ℤ) : Finset (ℤ × ℤ) :=
  S.filter fun p => p.1 = c

/-- **The viability condition on a prefix.** Every cell of `P` reaches the cut
column from inside `P`. Equivalently: no component of `P` is stranded behind
the cut. A prefix that fails this can never become connected, which is the
content of the frontier DP's death rule (lemma `strand_dead`, increment 2). -/
def Unstranded (P : Finset (ℤ × ℤ)) (c : ℤ) : Prop :=
  ∀ a ∈ P, ∃ a' ∈ colAt P c, reach P a a'

/-- **The reduced step relation.** The past `P` enters only through its cut
column and through reachability-in-`P` *restricted to that column*; the future
`M` enters in full. That asymmetry is the formal content of "the frontier state
is a sufficient statistic for the past". -/
def redStep (P M : Finset (ℤ × ℤ)) (c : ℤ) (x y : ℤ × ℤ) : Prop :=
    (x ∈ colAt P c ∧ y ∈ colAt P c ∧ reach P x y)
  ∨ (x ∈ M ∧ y ∈ M ∧ reach M x y)
  ∨ (kingAdj x y ∧ ((x ∈ colAt P c ∧ y ∈ M) ∨ (x ∈ M ∧ y ∈ colAt P c)))

/-! ## Layer A — arithmetic and relation hygiene -/

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

/-- Reachability is monotone in the ambient set. -/
lemma reach_mono {S S' : Finset (ℤ × ℤ)} (hsub : S ⊆ S') {a b : ℤ × ℤ}
    (h : reach S a b) : reach S' a b :=
  Relation.ReflTransGen.mono (fun _ _ hxy => ⟨hsub hxy.1, hsub hxy.2.1, hxy.2.2⟩) h

/-- A cell outside `S` reaches nothing inside it but itself. -/
lemma reach_of_notMem {S : Finset (ℤ × ℤ)} {x b : ℤ × ℤ} (hx : x ∉ S)
    (h : reach S x b) : b = x := by
  rcases Relation.ReflTransGen.cases_head h with rfl | ⟨z, hz, -⟩
  · rfl
  · exact absurd hz.1 hx

/-- **The stencil, as one line of arithmetic.** A king edge crossing the cut
lands squarely on it: its tail is in column `c` and its head in column `c+1`.
This is the local form of `Finite.lean`'s `exists_adj_cross_of_reflTransGen`,
which is the same fact along a whole path. -/
lemma cut_edge_cols {a b : ℤ × ℤ} {c : ℤ} (ha : a.1 ≤ c) (hb : c < b.1)
    (hadj : kingAdj a b) : a.1 = c ∧ b.1 = c + 1 := by
  have h := hadj.2.1
  rw [abs_le] at h
  omega

/-! ## Layer B — the funnel -/

open scoped Classical in
/-- **The funnel map.** Cut-column cells and everything outside `P` are fixed;
any other cell of `P` is sent to some cut-column cell it reaches inside `P`
(which exists exactly when `P` is `Unstranded`). Choice is unavoidable here —
the representative is not canonical — and it does not need to be: nothing below
depends on *which* representative is chosen. -/
noncomputable def fnl (P : Finset (ℤ × ℤ)) (c : ℤ) (x : ℤ × ℤ) : ℤ × ℤ :=
  if x ∈ colAt P c then x
  else if h : ∃ a', a' ∈ colAt P c ∧ reach P x a' then h.choose
  else x

/-- The funnel fixes everything outside the prefix — in particular every cell
of the future `M`. -/
lemma fnl_eq_self_of_notMem {P : Finset (ℤ × ℤ)} {c : ℤ} {x : ℤ × ℤ}
    (hx : x ∉ P) : fnl P c x = x := by
  have hcol : x ∉ colAt P c := fun h => hx (Finset.mem_filter.mp h).1
  have hno : ¬ ∃ a', a' ∈ colAt P c ∧ reach P x a' := by
    rintro ⟨a', ha', hreach⟩
    have hax : a' = x := reach_of_notMem hx hreach
    subst hax
    exact hcol ha'
  unfold fnl
  rw [if_neg hcol, dif_neg hno]

/-- The funnel image of a prefix cell is a cut-column cell it reaches. -/
lemma fnl_mem_col {P : Finset (ℤ × ℤ)} {c : ℤ} (hu : Unstranded P c)
    {x : ℤ × ℤ} (hx : x ∈ P) :
    fnl P c x ∈ colAt P c ∧ reach P x (fnl P c x) := by
  unfold fnl
  by_cases hcol : x ∈ colAt P c
  · rw [if_pos hcol]
    exact ⟨hcol, Relation.ReflTransGen.refl⟩
  · rw [if_neg hcol]
    have h : ∃ a', a' ∈ colAt P c ∧ reach P x a' := hu x hx
    rw [dif_pos h]
    exact h.choose_spec

/-! ## Layer C — the crux

`redStep_of_step` is the whole content. Everything after it is Mathlib. -/

/-- **The crux, in single-step form.** Every king edge of `P ∪ M` lifts to a
reduced path between the funnel images of its endpoints. Four cases: inside the
past (funnel both ends and glue), inside the future (funnel is the identity),
and the two crossings (the stencil forces the past-side endpoint into the cut
column, so its funnel is itself). -/
lemma redStep_of_step {P M : Finset (ℤ × ℤ)} {c : ℤ}
    (hP : ∀ p ∈ P, p.1 ≤ c) (hM : ∀ p ∈ M, c < p.1) (hu : Unstranded P c)
    (x y : ℤ × ℤ) (hstep : x ∈ P ∪ M ∧ y ∈ P ∪ M ∧ kingAdj x y) :
    Relation.ReflTransGen (redStep P M c) (fnl P c x) (fnl P c y) := by
  obtain ⟨hx, hy, hadj⟩ := hstep
  have hPM : ∀ z ∈ P, z ∉ M := by
    intro z hz hzM
    have h1 := hP z hz
    have h2 := hM z hzM
    omega
  rcases Finset.mem_union.mp hx with hxP | hxM <;>
    rcases Finset.mem_union.mp hy with hyP | hyM
  · obtain ⟨hfx, hrx⟩ := fnl_mem_col hu hxP
    obtain ⟨hfy, hry⟩ := fnl_mem_col hu hyP
    refine Relation.ReflTransGen.single (Or.inl ⟨hfx, hfy, ?_⟩)
    exact Relation.ReflTransGen.trans
      (Relation.ReflTransGen.trans (reach_symm hrx)
        (Relation.ReflTransGen.single ⟨hxP, hyP, hadj⟩)) hry
  · have hxc : x.1 = c := (cut_edge_cols (hP x hxP) (hM y hyM) hadj).1
    have hxcol : x ∈ colAt P c := Finset.mem_filter.mpr ⟨hxP, hxc⟩
    have hfx : fnl P c x = x := by unfold fnl; rw [if_pos hxcol]
    have hfy : fnl P c y = y := fnl_eq_self_of_notMem (fun h => hPM y h hyM)
    rw [hfx, hfy]
    exact Relation.ReflTransGen.single (Or.inr (Or.inr ⟨hadj, Or.inl ⟨hxcol, hyM⟩⟩))
  · have hyc : y.1 = c :=
      (cut_edge_cols (hP y hyP) (hM x hxM) (kingAdj_symm hadj)).1
    have hycol : y ∈ colAt P c := Finset.mem_filter.mpr ⟨hyP, hyc⟩
    have hfy : fnl P c y = y := by unfold fnl; rw [if_pos hycol]
    have hfx : fnl P c x = x := fnl_eq_self_of_notMem (fun h => hPM x h hxM)
    rw [hfx, hfy]
    exact Relation.ReflTransGen.single (Or.inr (Or.inr ⟨hadj, Or.inr ⟨hxM, hycol⟩⟩))
  · have hfx : fnl P c x = x := fnl_eq_self_of_notMem (fun h => hPM x h hxM)
    have hfy : fnl P c y = y := fnl_eq_self_of_notMem (fun h => hPM y h hyM)
    rw [hfx, hfy]
    exact Relation.ReflTransGen.single
      (Or.inr (Or.inl ⟨hxM, hyM, Relation.ReflTransGen.single ⟨hxM, hyM, hadj⟩⟩))

/-- **Soundness of the reduction.** Any king path in `P ∪ M` projects to a
reduced path between the funnel images — no path-splitting induction is
written, because `Relation.ReflTransGen.lift'` is the induction. -/
theorem redReach_of_reach {P M : Finset (ℤ × ℤ)} {c : ℤ}
    (hP : ∀ p ∈ P, p.1 ≤ c) (hM : ∀ p ∈ M, c < p.1) (hu : Unstranded P c)
    {x y : ℤ × ℤ} (h : reach (P ∪ M) x y) :
    Relation.ReflTransGen (redStep P M c) (fnl P c x) (fnl P c y) :=
  Relation.ReflTransGen.lift' (fnl P c) (redStep_of_step hP hM hu) h

/-- Each reduced step is a genuine king path in `P ∪ M`. This is the direction
that stops the state from over-merging: without the `reach P` conjunct in
`redStep`'s first clause it is false (RED control 2). -/
lemma reach_of_redStep {P M : Finset (ℤ × ℤ)} {c : ℤ} {x y : ℤ × ℤ}
    (h : redStep P M c x y) : reach (P ∪ M) x y := by
  rcases h with ⟨-, -, hr⟩ | ⟨-, -, hr⟩ | ⟨hadj, hxy⟩
  · exact reach_mono Finset.subset_union_left hr
  · exact reach_mono Finset.subset_union_right hr
  · rcases hxy with ⟨hx, hy⟩ | ⟨hx, hy⟩
    · exact Relation.ReflTransGen.single
        ⟨Finset.mem_union_left _ (Finset.mem_filter.mp hx).1,
         Finset.mem_union_right _ hy, hadj⟩
    · exact Relation.ReflTransGen.single
        ⟨Finset.mem_union_right _ hx,
         Finset.mem_union_left _ (Finset.mem_filter.mp hy).1, hadj⟩

/-- **Completeness of the reduction.** -/
theorem reach_of_redReach {P M : Finset (ℤ × ℤ)} {c : ℤ} {x y : ℤ × ℤ}
    (h : Relation.ReflTransGen (redStep P M c) x y) : reach (P ∪ M) x y :=
  Relation.reflTransGen_closed (fun _ _ hab => reach_of_redStep hab) h

/-! ## Axiom footprint

A mismatch here is a fact about the footprint, not a hole in an argument.
`Classical.choice` enters through `fnl`'s representative choice and is expected.
-/

/-- info: 'Polyplets.R4Funnel.redReach_of_reach' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms redReach_of_reach

/-! ## What increment 2 must add, stated but NOT proved here

```
theorem sufficiency {P P' M : Finset (ℤ × ℤ)} {c : ℤ}
    (hP : ∀ p ∈ P, p.1 ≤ c) (hP' : ∀ p ∈ P', p.1 ≤ c) (hM : ∀ p ∈ M, c < p.1)
    (hu : Unstranded P c) (hu' : Unstranded P' c)
    (hcol : colAt P c = colAt P' c)
    (hrel : ∀ a ∈ colAt P c, ∀ b ∈ colAt P c, reach P a b ↔ reach P' a b) :
    KingConnected (P ∪ M) ↔ KingConnected (P' ∪ M)
```

That is the theorem the whole programme rests on: the DP may forget everything
about the past except `colAt P c` and the restricted relation `hrel` names. It
follows from a `reduction` lemma packaging `redReach_of_reach` and
`reach_of_redReach` into an iff on `colAt P c ∪ M`, plus the degenerate cases
(`P = ∅`, `M = ∅`). Increment 2. -/

end R4Funnel
end Polyplets
