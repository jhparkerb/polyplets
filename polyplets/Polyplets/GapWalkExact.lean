/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.List.GetD
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

/-! ## Local helpers (list/Finset bookkeeping) -/

/-- The sum of a list of zeros is zero (local copy: the Canon/Trunc modules'
versions are `private` to those files). -/
private lemma sum_eq_zero_of_forall {l : List Nat} (h : ∀ x ∈ l, x = 0) : l.sum = 0 := by
  induction l with
  | nil => simp
  | cons x xs ih =>
    have hx : x = 0 := h x List.mem_cons_self
    have hxs : xs.sum = 0 := ih (fun y hy => h y (List.mem_cons_of_mem x hy))
    simp [hx, hxs]

/-- Splitting the sum of a `flatMap` of pairs into two separate mapped sums. -/
private lemma sum_flatMap_pair' (l : List Nat) (a b : Nat → Nat) :
    (l.flatMap fun i => [a i, b i]).sum = (l.map a).sum + (l.map b).sum := by
  induction l with
  | nil => simp
  | cons x xs ih =>
    simp only [List.flatMap_cons, List.sum_append, List.map_cons, List.sum_cons, List.sum_nil,
      add_zero]
    rw [ih]
    omega

/-- `Finset.Icc 1 n` sums the same as mapping `f ∘ (· + 1)` over `List.range n`. -/
private lemma sum_Icc_eq_range_map (n : Nat) (f : Nat → Nat) :
    ∑ g ∈ Finset.Icc 1 n, f g = ((List.range n).map fun i => f (i + 1)).sum := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_Icc_succ_top (by omega), ih, List.range_succ, List.map_append]
    simp

/-- Any list-map-sum over `states cap` splits into the `J` sum plus the `P`
sum over `Finset.Icc 1 cap`. -/
private lemma states_sum_eq_finset_sum (cap : Nat) (w : St → Nat) :
    ((states cap).map w).sum =
      (∑ g ∈ Finset.Icc 1 cap, w (g, true)) + (∑ g ∈ Finset.Icc 1 cap, w (g, false)) := by
  unfold states
  rw [List.map_flatMap]
  simp only [List.map_cons, List.map_nil]
  rw [sum_flatMap_pair' (List.range cap) (fun i => w (i + 1, true)) (fun i => w (i + 1, false))]
  rw [sum_Icc_eq_range_map cap (fun g => w (g, true)),
    sum_Icc_eq_range_map cap (fun g => w (g, false))]

/-- `funStep` at cap `cap` is the `J`-source sum plus the `P`-source sum,
both over `Finset.Icc 1 cap`. -/
private lemma funStep_eq_finset_sum (cap : Nat) (F : St → Nat) (t : St) :
    funStep cap F t = (∑ g ∈ Finset.Icc 1 cap, F (g, true) * stepMul g true t.1 t.2) +
      (∑ g ∈ Finset.Icc 1 cap, F (g, false) * stepMul g false t.1 t.2) := by
  unfold funStep
  exact states_sum_eq_finset_sum cap (fun s => F s * stepMul s.1 s.2 t.1 t.2)

/-- Peeling the bottom two elements off `Finset.Icc 1 n` (`n ≥ 2`). -/
private lemma sum_Icc_one_two_add (f : Nat → Nat) (n : Nat) (hn : 2 ≤ n) :
    ∑ g ∈ Finset.Icc 1 n, f g = f 1 + f 2 + ∑ g ∈ Finset.Icc 3 n, f g := by
  induction n, hn using Nat.le_induction with
  | base =>
    rw [show Finset.Icc 3 2 = (∅ : Finset ℕ) from Finset.Icc_eq_empty (by omega)]
    rw [Finset.sum_Icc_succ_top (show (1:ℕ) ≤ 1 + 1 by omega), Finset.Icc_self,
      Finset.sum_singleton]
    simp
  | succ n hn ih =>
    rw [Finset.sum_Icc_succ_top (by omega : (1:ℕ) ≤ n + 1), ih,
      Finset.sum_Icc_succ_top (by omega : (3:ℕ) ≤ n + 1)]
    omega

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
theorem startData_interior : StartData startCount 4 1 4 6 where
  head_j1 := startCount_1J
  head_j2 := startCount_2J
  head_p1 := startCount_1P
  head_p2 := startCount_2P
  deep_j := startCount_J_high
  deep_p := startCount_P_deep

/-- The bare start (`dp_bare`): `(1, 0, 1, 1)`. -/
theorem startData_bare : StartData bareCount 1 0 1 1 where
  head_j1 := by decide
  head_j2 := by decide
  head_p1 := by decide
  head_p2 := by decide
  deep_j := fun g hg => bareCount_J_high g (by omega)
  deep_p := fun g hg => by
    rw [bareCount, if_pos (by simp; omega)]

/-! ## Cap stability -/

/-- `iter_agree`, symmetrized: two legal caps agree on every `J`-value and
on `P`-values inside both cones. -/
theorem iter_agree_of_le (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) {M M' l : Nat}
    (hM : 2 * l + 5 ≤ M) (hM' : 2 * l + 5 ≤ M') :
    (∀ g, iter M F l (g, true) = iter M' F l (g, true)) ∧
      (∀ g, g + 2 * l ≤ M → g + 2 * l ≤ M' →
        iter M F l (g, false) = iter M' F l (g, false)) := by
  rcases Nat.le_total M M' with hle | hle
  · obtain ⟨hJ, hP⟩ := iter_agree F hF M M' hle l hM
    exact ⟨hJ, fun g hgM _hgM' => hP g hgM⟩
  · obtain ⟨hJ, hP⟩ := iter_agree F hF M' M hle l hM'
    exact ⟨fun g => (hJ g).symm, fun g _hgM hgM' => (hP g hgM').symm⟩

/-- Any cap `≥ 2m+5` computes `jE`. -/
theorem jE_eq (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {M m : Nat} (hM : 2 * m + 5 ≤ M) (g : Nat) :
    jE F m g = iter M F m (g, true) := by
  unfold jE
  exact (iter_agree_of_le F hF (le_refl (2 * m + 5)) hM).1 g

/-- Any cap `≥ 2m+5` whose cone contains `(g, m)` computes `pE`. -/
theorem pE_eq (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {M m g : Nat} (hM : 2 * m + 5 ≤ M) (hg : g + 2 * m ≤ M) :
    pE F m g = iter M F m (g, false) := by
  unfold pE
  exact (iter_agree_of_le F hF (by omega : 2 * m + 5 ≤ g + 2 * m + 5) hM).2 g (by omega) hg

/-- Zero steps: the start itself. -/
theorem jE_zero (F : St → Nat) (g : Nat) : jE F 0 g = F (g, true) := rfl

/-- Zero steps: the start itself. -/
theorem pE_zero (F : St → Nat) (g : Nat) : pE F 0 g = F (g, false) := rfl

/-! ## Support -/

/-- `J`-support: after `m` steps nothing joined lives above gap `2m+2`. -/
theorem jE_support (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m g : Nat) (h : 2 * m + 2 < g) : jE F m g = 0 := by
  unfold jE
  exact iter_J_support (2 * m + 5) F hF m g (by omega)

/-- Nothing ever lands pending at gap 1 (`stepMul_to_1_P`), and neither
start puts anything there. -/
theorem pE_one (F : St → Nat) (h1 : F (1, false) = 0) (m : Nat) :
    pE F m 1 = 0 := by
  cases m with
  | zero => rw [pE_zero]; exact h1
  | succ m =>
    unfold pE
    set M := 1 + 2 * (m + 1) + 5 with hMdef
    change funStep M (iter M F m) (1, false) = 0
    unfold funStep
    apply sum_eq_zero_of_forall
    intro x hx
    obtain ⟨s, _hs, rfl⟩ := List.mem_map.mp hx
    simp [stepMul_to_1_P]

/-! ## The exact step recurrences -/

/-- One step onto a `J` target: `J` sources through the support window,
`P` sources only from gaps `≤ 3` (joins never come from farther out). -/
theorem jE_step (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m gp : Nat) (hgp : 1 ≤ gp) :
    jE F (m + 1) gp =
      (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp true) +
      (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false gp true) := by
  set M := 2 * m + gp + 7 with hMdef
  have hM1 : 2 * (m + 1) + 5 ≤ M := by omega
  have hM0 : 2 * m + 5 ≤ M := by omega
  rw [jE_eq F hF hM1 gp]
  change funStep M (iter M F m) (gp, true) = _
  rw [funStep_eq_finset_sum]
  have hJ : (∑ g ∈ Finset.Icc 1 M, iter M F m (g, true) * stepMul g true gp true) =
      ∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp true := by
    rw [← Finset.sum_subset (Finset.Icc_subset_Icc_right (show 2 * m + 2 ≤ M by omega))
      (fun x hxM hxs => by
        simp only [Finset.mem_Icc] at hxM hxs
        have : iter M F m (x, true) = 0 := iter_J_support M F hF m x (by omega)
        simp [this])]
    apply Finset.sum_congr rfl
    intro g _hg
    rw [jE_eq F hF hM0 g]
  have hP : (∑ g ∈ Finset.Icc 1 M, iter M F m (g, false) * stepMul g false gp true) =
      ∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false gp true := by
    rw [← Finset.sum_subset (Finset.Icc_subset_Icc_right (show (3:ℕ) ≤ M by omega))
      (fun x hxM hxs => by
        simp only [Finset.mem_Icc] at hxM hxs
        have : stepMul x false gp true = 0 := stepMul_P_far_to_J x gp (by omega)
        simp [this])]
    apply Finset.sum_congr rfl
    intro g hg
    simp only [Finset.mem_Icc] at hg
    rw [pE_eq F hF hM0 (by omega)]
  rw [hJ, hP]

/-- One step onto a `P` target at gap `≥ 2`: `J` sources through the
support window, `P` sources through the locality window `[1, gp+2]`. -/
theorem pE_step (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m gp : Nat) (hgp : 2 ≤ gp) :
    pE F (m + 1) gp =
      (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp false) +
      (∑ g ∈ Finset.Icc 1 (gp + 2), pE F m g * stepMul g false gp false) := by
  set M := 2 * m + gp + 7 with hMdef
  have hM1 : 2 * (m + 1) + 5 ≤ M := by omega
  have hM0 : 2 * m + 5 ≤ M := by omega
  have hgM : gp + 2 * (m + 1) ≤ M := by omega
  rw [pE_eq F hF hM1 hgM]
  change funStep M (iter M F m) (gp, false) = _
  rw [funStep_eq_finset_sum]
  have hJ : (∑ g ∈ Finset.Icc 1 M, iter M F m (g, true) * stepMul g true gp false) =
      ∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true gp false := by
    rw [← Finset.sum_subset (Finset.Icc_subset_Icc_right (show 2 * m + 2 ≤ M by omega))
      (fun x hxM hxs => by
        simp only [Finset.mem_Icc] at hxM hxs
        have : iter M F m (x, true) = 0 := iter_J_support M F hF m x (by omega)
        simp [this])]
    apply Finset.sum_congr rfl
    intro g _hg
    rw [jE_eq F hF hM0 g]
  have hP : (∑ g ∈ Finset.Icc 1 M, iter M F m (g, false) * stepMul g false gp false) =
      ∑ g ∈ Finset.Icc 1 (gp + 2), pE F m g * stepMul g false gp false := by
    rw [← Finset.sum_subset (Finset.Icc_subset_Icc_right (show gp + 2 ≤ M by omega))
      (fun x hxM hxs => by
        simp only [Finset.mem_Icc] at hxM hxs
        have : stepMul x false gp false = 0 :=
          stepMul_P_local x gp false (by omega) (Or.inl (by omega))
        simp [this])]
    apply Finset.sum_congr rfl
    intro g hg
    simp only [Finset.mem_Icc] at hg
    rw [pE_eq F hF hM0 (by omega)]
  rw [hJ, hP]

/-! ## The end-functional bridge -/

/-- `qEnd` of the `m`-step walk reads `J` at weights `4, 5, 6, 6, …` and
`P` at weights `2, 1, 0, …`: a linear read of the exact values. -/
theorem qEndF_eval (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    qEndF M (iter M F m) =
      4 * jE F m 1 + 5 * jE F m 2 +
        6 * ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g +
        2 * pE F m 1 + pE F m 2 := by
  set G := iter M F m with hGdef
  have hstate : qEndF M G = ((states M).map fun s =>
      if s.2 then G s * (if s.1 ≤ 2 then s.1 + 3 else 6)
      else if s.1 ≤ 2 then G s * (3 - s.1) else 0).sum := by
    change qEnd (canon M G) = _
    unfold qEnd canon
    rw [List.map_map]
    rfl
  rw [hstate, states_sum_eq_finset_sum]
  rw [show (∑ g ∈ Finset.Icc 1 M,
        if (g, true).2 = true then G (g, true) * (if (g, true).1 ≤ 2 then (g, true).1 + 3 else 6)
        else if (g, true).1 ≤ 2 then G (g, true) * (3 - (g, true).1) else 0) =
      ∑ g ∈ Finset.Icc 1 M, G (g, true) * (if g ≤ 2 then g + 3 else 6) from
        Finset.sum_congr rfl (fun g _ => by simp),
    show (∑ g ∈ Finset.Icc 1 M,
        if (g, false).2 = true then
          G (g, false) * (if (g, false).1 ≤ 2 then (g, false).1 + 3 else 6)
        else if (g, false).1 ≤ 2 then G (g, false) * (3 - (g, false).1) else 0) =
      ∑ g ∈ Finset.Icc 1 M, if g ≤ 2 then G (g, false) * (3 - g) else 0 from
        Finset.sum_congr rfl (fun g _ => by simp)]
  have hJbig : (∑ g ∈ Finset.Icc 1 M, G (g, true) * (if g ≤ 2 then g + 3 else 6)) =
      ∑ g ∈ Finset.Icc 1 (2 * m + 2), G (g, true) * (if g ≤ 2 then g + 3 else 6) := by
    refine (Finset.sum_subset (Finset.Icc_subset_Icc_right (show 2 * m + 2 ≤ M by omega))
      ?_).symm
    intro x hxM hxs
    simp only [Finset.mem_Icc] at hxM hxs
    have : G (x, true) = 0 := iter_J_support M F hF m x (by omega)
    simp [this]
  have hJsplit : (∑ g ∈ Finset.Icc 1 (2 * m + 2), G (g, true) * (if g ≤ 2 then g + 3 else 6)) =
      G (1, true) * 4 + G (2, true) * 5 +
        ∑ g ∈ Finset.Icc 3 (2 * m + 2), G (g, true) * (if g ≤ 2 then g + 3 else 6) := by
    rw [sum_Icc_one_two_add _ (2 * m + 2) (by omega)]
    norm_num
  have hJtail : (∑ g ∈ Finset.Icc 3 (2 * m + 2), G (g, true) * (if g ≤ 2 then g + 3 else 6)) =
      6 * ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro g hg
    simp only [Finset.mem_Icc] at hg
    rw [show G (g, true) = jE F m g from (jE_eq F hF hM g).symm, if_neg (by omega)]
    omega
  have hP : (∑ g ∈ Finset.Icc 1 M, if g ≤ 2 then G (g, false) * (3 - g) else 0) =
      G (1, false) * 2 + G (2, false) := by
    have hshrink : (∑ g ∈ Finset.Icc 1 M, if g ≤ 2 then G (g, false) * (3 - g) else 0) =
        ∑ g ∈ Finset.Icc 1 2, if g ≤ 2 then G (g, false) * (3 - g) else 0 := by
      refine (Finset.sum_subset (Finset.Icc_subset_Icc_right (show (2:ℕ) ≤ M by omega))
        ?_).symm
      intro x hxM hxs
      simp only [Finset.mem_Icc] at hxM hxs
      simp [show ¬ x ≤ 2 by omega]
    rw [hshrink, sum_Icc_one_two_add _ 2 (le_refl 2)]
    simp
  have e1 : G (1, true) = jE F m 1 := (jE_eq F hF hM 1).symm
  have e2 : G (2, true) = jE F m 2 := (jE_eq F hF hM 2).symm
  have e3 : G (1, false) = pE F m 1 := (pE_eq F hF hM (by omega)).symm
  have e4 : G (2, false) = pE F m 2 := (pE_eq F hF hM (by omega)).symm
  rw [hJbig, hJsplit, hJtail, hP, e1, e2, e3, e4]
  omega

/-- `bareEnd` of the `m`-step walk sums the `J`-row. -/
theorem bareEndF_eval (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    bareEndF M (iter M F m) =
      jE F m 1 + jE F m 2 + ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g := by
  set G := iter M F m with hGdef
  have hstep : bareEndF M G = ∑ g ∈ Finset.Icc 1 M, G (g, true) := by
    have hstate : bareEndF M G = ((states M).map fun s => if s.2 then G s else 0).sum := by
      change bareEnd (canon M G) = _
      unfold bareEnd canon
      rw [List.map_map]
      rfl
    rw [hstate, states_sum_eq_finset_sum]
    simp
  have hbig : (∑ g ∈ Finset.Icc 1 M, G (g, true)) =
      ∑ g ∈ Finset.Icc 1 (2 * m + 2), G (g, true) := by
    refine (Finset.sum_subset (Finset.Icc_subset_Icc_right (show 2 * m + 2 ≤ M by omega))
      ?_).symm
    intro x hxM hxs
    simp only [Finset.mem_Icc] at hxM hxs
    have : G (x, true) = 0 := iter_J_support M F hF m x (by omega)
    simp [this]
  have hsplit : (∑ g ∈ Finset.Icc 1 (2 * m + 2), G (g, true)) =
      G (1, true) + G (2, true) + ∑ g ∈ Finset.Icc 3 (2 * m + 2), G (g, true) := by
    rw [sum_Icc_one_two_add _ (2 * m + 2) (by omega)]
  have htail : (∑ g ∈ Finset.Icc 3 (2 * m + 2), G (g, true)) =
      ∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g := by
    apply Finset.sum_congr rfl
    intro g hg
    exact (jE_eq F hF hM g).symm
  have e1 : G (1, true) = jE F m 1 := (jE_eq F hF hM 1).symm
  have e2 : G (2, true) = jE F m 2 := (jE_eq F hF hM 2).symm
  rw [hstep, hbig, hsplit, htail, e1, e2]

/-- Entry `l` of `walkFamilies L` is the pair of end reads of the `l`-step
iterates of the two starts, at the family cap. -/
theorem walkFamilies_entry (L l : Nat) (hl : l < L) :
    (walkFamilies L).getD l (0, 0, 0) =
      (qEndF (2 * L + 3) (iter (2 * L + 3) startCount l),
       qEndF (2 * L + 3) (iter (2 * L + 3) bareCount l),
       bareEndF (2 * L + 3) (iter (2 * L + 3) bareCount l)) := by
  have hstart : walkFamilies L =
      (List.range L).map fun l =>
        (qEndF (2 * L + 3) (iter (2 * L + 3) startCount l),
         qEndF (2 * L + 3) (iter (2 * L + 3) bareCount l),
         bareEndF (2 * L + 3) (iter (2 * L + 3) bareCount l)) := by
    change walkAux L (2 * L + 3) (startInterior (2 * L + 3)) (startBare (2 * L + 3)) = _
    have hI : startInterior (2 * L + 3) = canon (2 * L + 3) startCount := startInterior_eq _
    have hB : startBare (2 * L + 3) = canon (2 * L + 3) bareCount := startBare_eq _
    rw [hI, hB, walkAux_canon]
  rw [hstart, List.getD_eq_getElem _ _ (by simpa using hl)]
  simp

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
