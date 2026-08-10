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
  induction N with
  | zero => simp
  | succ N ih =>
    rw [List.range_succ, List.filter_append, List.length_append, ih]
    by_cases h : lo ≤ N ∧ N < hi
    · rw [List.filter_cons_of_pos (by simpa using h), List.filter_nil]
      simp only [List.length_cons, List.length_nil]
      omega
    · rw [List.filter_cons_of_neg (by simpa using h), List.filter_nil]
      simp only [List.length_nil]
      omega

/-- Collapsing the conjunction of two interval predicates to their
intersection interval. -/
private theorem filter_and_interval (N loA hiA loB hiB : ℕ) :
    ((List.range N).filter fun i =>
        decide (loA ≤ i ∧ i < hiA) && decide (loB ≤ i ∧ i < hiB)) =
      (List.range N).filter fun i =>
        decide (max loA loB ≤ i ∧ i < min hiA hiB) := by
  apply List.filter_congr
  intro i _
  rw [Bool.eq_iff_iff]
  simp only [Bool.and_eq_true, decide_eq_true_eq]
  omega

/-- General inclusion–exclusion for `List.filter` lengths: no disjointness
hypothesis needed. -/
private theorem length_filter_or_general {α : Type*} (l : List α) (p q : α → Bool) :
    (l.filter fun a => p a || q a).length =
      (l.filter p).length + (l.filter q).length -
        (l.filter fun a => p a && q a).length := by
  induction l with
  | nil => simp
  | cons a l ih =>
    simp only [List.filter_cons]
    have hle' : (l.filter fun a => p a && q a).length ≤ (l.filter q).length := by
      rw [show (l.filter fun a => p a && q a) = (l.filter q).filter p from
        (List.filter_filter (p := p) (q := q)).symm]
      exact List.length_filter_le p (l.filter q)
    rcases hp : p a <;> rcases hq : q a <;> simp_all <;> omega

/-- Splitting a count by the target class: `ok`-satisfying placements split
exactly between the `nc = true` and `nc = false` targets. -/
private theorem length_filter_split {α : Type*} (l : List α) (ok nc : α → Bool) :
    (l.filter fun a => ok a && (nc a == true)).length +
        (l.filter fun a => ok a && (nc a == false)).length =
      (l.filter ok).length := by
  have hor : (l.filter fun a =>
      (ok a && (nc a == true)) || (ok a && (nc a == false))) = l.filter ok := by
    apply List.filter_congr
    intro a _
    cases ok a <;> cases nc a <;> decide
  have hand : (l.filter fun a =>
      (ok a && (nc a == true)) && (ok a && (nc a == false))).length = 0 := by
    rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
    intro a _
    cases ok a <;> cases nc a <;> decide
  have key := length_filter_or_general l (fun a => ok a && (nc a == true))
    (fun a => ok a && (nc a == false))
  rw [hor] at key
  omega

/-! ## Target gap 1 is always class `J` -/

/-- A landing on gap 1 is reclassified `J` unconditionally: the `P` variant
is empty, every source. -/
theorem stepMul_to_1_P (g : ℕ) (c : Bool) : stepMul g c 1 false = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, joined]
  simp

/-! ## The generic `P` row, `g ≥ 3` -/

/-- Bulk kernel: a pending pair at gap `g ≥ 3` moves to gap `gp ≥ 2`
(staying `P`) in exactly `bulkW g gp` ways. -/
theorem stepMul_P_bulk (g gp : ℕ) (hg : 3 ≤ g) (hgp : 2 ≤ gp) :
    stepMul g false gp false = bulkW g gp := by
  have hne1 : gp ≠ 1 := by omega
  rw [stepMul]
  rw [show ((List.range (g + gp + 5)).filter fun i : ℕ =>
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
      let ok := if false then touch0 || touchg else touch0 && touchg
      let nc : Bool :=
        if gp = 1 then true
        else if false then (x0 || y0) && (x1 || y1)
        else joined x0 y0 x1 y1
      ok && nc == false) =
      (List.range (g + gp + 5)).filter fun i : ℕ =>
        decide (max gp g + 1 ≤ i ∧ i < min gp g + 4) from by
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_neg hne1,
      if_neg (show (false = true) → False by decide)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
      decide_eq_true_eq, Bool.eq_false_iff, ne_eq]
    omega]
  rw [length_filter_range_interval, bulkW]
  split_ifs with hb
  · omega
  · omega

/-- The unique generic join: gap 3 folding onto gap 1. -/
theorem stepMul_P3_join : stepMul 3 false 1 true = 1 := by decide

/-- A pending pair at gap `g ≥ 3` never lands joined at gap 2. -/
theorem stepMul_P_to_J2 (g : ℕ) (hg : 3 ≤ g) :
    stepMul g false 2 true = 0 := by
  rw [stepMul, List.length_eq_zero_iff, List.filter_eq_nil_iff]
  intro i _
  simp only [near, joined, Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq,
    decide_eq_true_eq, if_neg (by omega : ¬ (2 : ℕ) = 1),
    if_neg (show (false = true) → False by decide)]
  omega

/-! ## The generic `J` row, `g ≥ 3` -/

/-- Joined source to gap 1: background 8, minus the bulk fold at `g = 3`. -/
theorem stepMul_J_to_1J (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 1 true = 8 - bulkW g 1 := by
  have hstep : stepMul g true 1 true =
      ((List.range (g + 1 + 5)).filter fun i : ℕ =>
        decide (1 ≤ i ∧ i < 5) || decide (g + 1 ≤ i ∧ i < g + 5)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_true]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq, and_true]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval, bulkW]
  split_ifs with hb <;> omega

/-- Joined source to `(2, J)`: background 2 plus the bulk block. -/
theorem stepMul_J_to_2J (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 2 true = 2 + bulkW g 2 := by
  have hstep : stepMul g true 2 true =
      ((List.range (g + 2 + 5)).filter fun i : ℕ =>
        (decide (3 ≤ i ∧ i < 4) || decide (g + 1 ≤ i ∧ i < 6)) ||
          decide (g + 3 ≤ i ∧ i < g + 4)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_true, if_neg (by decide : ¬ (2 : ℕ) = 1)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq]
    omega
  have hab0 : ((List.range (g + 2 + 5)).filter fun i : ℕ =>
      decide (3 ≤ i ∧ i < 4) && decide (g + 1 ≤ i ∧ i < 6)).length = 0 := by
    rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
    intro i _
    simp only [Bool.and_eq_true, decide_eq_true_eq, not_and]
    omega
  have habc0 : ((List.range (g + 2 + 5)).filter fun i : ℕ =>
      (decide (3 ≤ i ∧ i < 4) || decide (g + 1 ≤ i ∧ i < 6)) &&
        decide (g + 3 ≤ i ∧ i < g + 4)).length = 0 := by
    rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
    intro i _
    simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, not_and]
    omega
  rw [hstep, length_filter_or_general, length_filter_or_general, hab0, habc0,
    length_filter_range_interval, length_filter_range_interval, length_filter_range_interval,
    bulkW]
  split_ifs with hb <;> omega

/-- Joined source to `(2, P)`: background 8 minus twice the bulk block. -/
theorem stepMul_J_to_2P (g : ℕ) (hg : 3 ≤ g) :
    stepMul g true 2 false = 8 - 2 * bulkW g 2 := by
  have hsplit : stepMul g true 2 true + stepMul g true 2 false =
      ((List.range (g + 2 + 5)).filter fun i : ℕ =>
        let a : ℤ := (i : ℤ) - ((2 : ℤ) + 2)
        let G : ℤ := g
        let t0 : ℤ := a
        let t1 : ℤ := a + (2 : ℤ)
        let x0 := near t0
        let x1 := near t1
        let y0 := near (t0 - G)
        let y1 := near (t1 - G)
        let touch0 := x0 || x1
        let touchg := y0 || y1
        (if true then touch0 || touchg else touch0 && touchg)).length := by
    rw [stepMul, stepMul]
    exact length_filter_split (List.range (g + 2 + 5))
      (fun i : ℕ =>
        let a : ℤ := (i : ℤ) - ((2 : ℤ) + 2)
        let G : ℤ := g
        let t0 : ℤ := a
        let t1 : ℤ := a + (2 : ℤ)
        let x0 := near t0
        let x1 := near t1
        let y0 := near (t0 - G)
        let y1 := near (t1 - G)
        let touch0 := x0 || x1
        let touchg := y0 || y1
        (if true then touch0 || touchg else touch0 && touchg))
      (fun i : ℕ =>
        let a : ℤ := (i : ℤ) - ((2 : ℤ) + 2)
        let G : ℤ := g
        let t0 : ℤ := a
        let t1 : ℤ := a + (2 : ℤ)
        let x0 := near t0
        let x1 := near t1
        let y0 := near (t0 - G)
        let y1 := near (t1 - G)
        (if (2 : ℕ) = 1 then true
          else if true then (x0 || y0) && (x1 || y1) else joined x0 y0 x1 y1))
  have hok : ((List.range (g + 2 + 5)).filter fun i : ℕ =>
      let a : ℤ := (i : ℤ) - ((2 : ℤ) + 2)
      let G : ℤ := g
      let t0 : ℤ := a
      let t1 : ℤ := a + (2 : ℤ)
      let x0 := near t0
      let x1 := near t1
      let y0 := near (t0 - G)
      let y1 := near (t1 - G)
      let touch0 := x0 || x1
      let touchg := y0 || y1
      (if true then touch0 || touchg else touch0 && touchg)).length =
        10 - bulkW g 2 := by
    rw [show ((List.range (g + 2 + 5)).filter fun i : ℕ =>
        let a : ℤ := (i : ℤ) - ((2 : ℤ) + 2)
        let G : ℤ := g
        let t0 : ℤ := a
        let t1 : ℤ := a + (2 : ℤ)
        let x0 := near t0
        let x1 := near t1
        let y0 := near (t0 - G)
        let y1 := near (t1 - G)
        let touch0 := x0 || x1
        let touchg := y0 || y1
        (if true then touch0 || touchg else touch0 && touchg)) =
        (List.range (g + 2 + 5)).filter fun i : ℕ =>
          decide (1 ≤ i ∧ i < 6) || decide (g + 1 ≤ i ∧ i < g + 6) from by
      apply List.filter_congr
      intro i _
      simp only [near, if_true]
      rw [Bool.eq_iff_iff]
      simp only [Bool.or_eq_true, decide_eq_true_eq]
      omega]
    rw [length_filter_or_general, filter_and_interval, length_filter_range_interval,
      length_filter_range_interval, length_filter_range_interval, bulkW]
    split_ifs with hb <;> omega
  rw [hok, stepMul_J_to_2J g hg] at hsplit
  rw [bulkW] at hsplit ⊢
  split_ifs at hsplit ⊢ <;> omega

/-- Joined source to a joined target at gap `≥ 3`: the bulk block alone. -/
theorem stepMul_J_bulk (g gp : ℕ) (hg : 3 ≤ g) (hgp : 3 ≤ gp) :
    stepMul g true gp true = bulkW g gp := by
  have hne1 : gp ≠ 1 := by omega
  rw [stepMul]
  rw [show ((List.range (g + gp + 5)).filter fun i : ℕ =>
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
      let ok := if true then touch0 || touchg else touch0 && touchg
      let nc : Bool :=
        if gp = 1 then true
        else if true then (x0 || y0) && (x1 || y1)
        else joined x0 y0 x1 y1
      ok && nc == true) =
      (List.range (g + gp + 5)).filter fun i : ℕ =>
        decide (max gp g + 1 ≤ i ∧ i < min gp g + 4) from by
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_neg hne1, if_true]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq]
    omega]
  rw [length_filter_range_interval, bulkW]
  split_ifs with hb
  · omega
  · omega

/-- The rank-one spray: a joined source reaches every `(gp, P)`, `gp ≥ 3`,
with weight 12, corrected by `−2·bulkW` inside the bulk window. -/
theorem stepMul_J_spray (g gp : ℕ) (hg : 3 ≤ g) (hgp : 3 ≤ gp) :
    stepMul g true gp false = 12 - 2 * bulkW g gp := by
  have hne1 : gp ≠ 1 := by omega
  have hsplit : stepMul g true gp true + stepMul g true gp false =
      ((List.range (g + gp + 5)).filter fun i : ℕ =>
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
        (if true then touch0 || touchg else touch0 && touchg)).length := by
    rw [stepMul, stepMul]
    exact length_filter_split (List.range (g + gp + 5))
      (fun i : ℕ =>
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
        (if true then touch0 || touchg else touch0 && touchg))
      (fun i : ℕ =>
        let a : ℤ := (i : ℤ) - ((gp : ℤ) + 2)
        let G : ℤ := g
        let t0 : ℤ := a
        let t1 : ℤ := a + (gp : ℤ)
        let x0 := near t0
        let x1 := near t1
        let y0 := near (t0 - G)
        let y1 := near (t1 - G)
        (if gp = 1 then true
          else if true then (x0 || y0) && (x1 || y1) else joined x0 y0 x1 y1))
  have hok : ((List.range (g + gp + 5)).filter fun i : ℕ =>
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
      (if true then touch0 || touchg else touch0 && touchg)).length =
        12 - bulkW g gp := by
    rw [show ((List.range (g + gp + 5)).filter fun i : ℕ =>
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
        (if true then touch0 || touchg else touch0 && touchg)) =
        (List.range (g + gp + 5)).filter fun i : ℕ =>
          ((decide (gp + 1 ≤ i ∧ i < gp + 4) || decide (1 ≤ i ∧ i < 4)) ||
              decide (g + gp + 1 ≤ i ∧ i < g + gp + 4)) ||
            decide (g + 1 ≤ i ∧ i < g + 4) from by
      apply List.filter_congr
      intro i _
      simp only [near, if_true]
      rw [Bool.eq_iff_iff]
      simp only [Bool.or_eq_true, decide_eq_true_eq]
      omega]
    have h1 : ((List.range (g + gp + 5)).filter fun i : ℕ =>
        decide (gp + 1 ≤ i ∧ i < gp + 4) && decide (1 ≤ i ∧ i < 4)).length = 0 := by
      rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
      intro i _
      simp only [Bool.and_eq_true, decide_eq_true_eq, not_and]
      omega
    have h2 : ((List.range (g + gp + 5)).filter fun i : ℕ =>
        (decide (gp + 1 ≤ i ∧ i < gp + 4) || decide (1 ≤ i ∧ i < 4)) &&
          decide (g + gp + 1 ≤ i ∧ i < g + gp + 4)).length = 0 := by
      rw [List.length_eq_zero_iff, List.filter_eq_nil_iff]
      intro i _
      simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, not_and]
      omega
    have h3 : (((List.range (g + gp + 5)).filter fun i : ℕ =>
        ((decide (gp + 1 ≤ i ∧ i < gp + 4) || decide (1 ≤ i ∧ i < 4)) ||
            decide (g + gp + 1 ≤ i ∧ i < g + gp + 4)) &&
          decide (g + 1 ≤ i ∧ i < g + 4))) =
        (List.range (g + gp + 5)).filter fun i : ℕ =>
          decide (max gp g + 1 ≤ i ∧ i < min gp g + 4) := by
      apply List.filter_congr
      intro i _
      rw [Bool.eq_iff_iff]
      simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq]
      omega
    rw [length_filter_or_general, length_filter_or_general, length_filter_or_general,
      h1, h2, h3, length_filter_range_interval, length_filter_range_interval,
      length_filter_range_interval, length_filter_range_interval, length_filter_range_interval,
      bulkW]
    split_ifs with hb <;> omega
  rw [hok, stepMul_J_bulk g gp hg hgp] at hsplit
  rw [bulkW] at hsplit ⊢
  split_ifs at hsplit ⊢ <;> omega

/-! ## The four boundary rows: heads (literal) and tails (symbolic)

Heads from `severance_w2_kernel.BOUNDARY`, asserted against the walk by its
stage 0 and by m1. -/

theorem stepMul_1J_1J : stepMul 1 true 1 true = 5 := by decide
theorem stepMul_1J_2J : stepMul 1 true 2 true = 2 := by decide
theorem stepMul_1J_2P : stepMul 1 true 2 false = 4 := by decide
theorem stepMul_1J_3J : stepMul 1 true 3 true = 1 := by decide
theorem stepMul_1J_3P : stepMul 1 true 3 false = 6 := by decide

/-- Row `(1, J)` tail: weight 8 to every `(gp, P)`, `gp ≥ 4`. -/
theorem stepMul_1J_tail (gp : ℕ) (h : 4 ≤ gp) :
    stepMul 1 true gp false = 8 := by
  have hstep : stepMul 1 true gp false =
      ((List.range (1 + gp + 5)).filter fun i : ℕ =>
        decide (1 ≤ i ∧ i < 5) || decide (gp + 1 ≤ i ∧ i < gp + 5)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_true, if_neg (by omega : ¬ gp = 1)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval]
  omega

theorem stepMul_2J_1J : stepMul 2 true 1 true = 6 := by decide
theorem stepMul_2J_2J : stepMul 2 true 2 true = 3 := by decide
theorem stepMul_2J_2P : stepMul 2 true 2 false = 4 := by decide
theorem stepMul_2J_3J : stepMul 2 true 3 true = 2 := by decide
theorem stepMul_2J_3P : stepMul 2 true 3 false = 6 := by decide
theorem stepMul_2J_4J : stepMul 2 true 4 true = 1 := by decide
theorem stepMul_2J_4P : stepMul 2 true 4 false = 8 := by decide

/-- Row `(2, J)` tail: weight 10 to every `(gp, P)`, `gp ≥ 5`. -/
theorem stepMul_2J_tail (gp : ℕ) (h : 5 ≤ gp) :
    stepMul 2 true gp false = 10 := by
  have hstep : stepMul 2 true gp false =
      ((List.range (2 + gp + 5)).filter fun i : ℕ =>
        decide (1 ≤ i ∧ i < 6) || decide (gp + 1 ≤ i ∧ i < gp + 6)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_true, if_neg (by omega : ¬ gp = 1)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval]
  omega

theorem stepMul_1P_1J : stepMul 1 false 1 true = 3 := by decide
theorem stepMul_1P_2J : stepMul 1 false 2 true = 2 := by decide
theorem stepMul_1P_2P : stepMul 1 false 2 false = 2 := by decide
theorem stepMul_1P_3P : stepMul 1 false 3 false = 5 := by decide

/-- Row `(1, P)` tail: weight 4 to every `(gp, P)`, `gp ≥ 4`. -/
theorem stepMul_1P_tail (gp : ℕ) (h : 4 ≤ gp) :
    stepMul 1 false gp false = 4 := by
  have hstep : stepMul 1 false gp false =
      ((List.range (1 + gp + 5)).filter fun i : ℕ =>
        decide (2 ≤ i ∧ i < 4) || decide (gp + 2 ≤ i ∧ i < gp + 4)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_neg (by omega : ¬ gp = 1),
      if_neg (show (false = true) → False by decide)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval]
  omega

theorem stepMul_2P_1J : stepMul 2 false 1 true = 2 := by decide
theorem stepMul_2P_2J : stepMul 2 false 2 true = 2 := by decide
theorem stepMul_2P_2P : stepMul 2 false 2 false = 1 := by decide
theorem stepMul_2P_3P : stepMul 2 false 3 false = 4 := by decide
theorem stepMul_2P_4P : stepMul 2 false 4 false = 3 := by decide

/-- Row `(2, P)` tail: weight 2 to every `(gp, P)`, `gp ≥ 5`. -/
theorem stepMul_2P_tail (gp : ℕ) (h : 5 ≤ gp) :
    stepMul 2 false gp false = 2 := by
  have hstep : stepMul 2 false gp false =
      ((List.range (2 + gp + 5)).filter fun i : ℕ =>
        decide (3 ≤ i ∧ i < 4) || decide (gp + 3 ≤ i ∧ i < gp + 4)).length := by
    rw [stepMul]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, joined, if_neg (by omega : ¬ gp = 1),
      if_neg (show (false = true) → False by decide)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval]
  omega

/-! ## The start vectors -/

theorem startCount_1J : startCount (1, true) = 4 := by decide
theorem startCount_1P : startCount (1, false) = 0 := by decide
theorem startCount_2J : startCount (2, true) = 1 := by decide
theorem startCount_2P : startCount (2, false) = 4 := by decide

/-- The interior start's `P`-tail: 6 placements at every gap `g ≥ 3`. -/
theorem startCount_P_deep (g : ℕ) (hg : 3 ≤ g) :
    startCount (g, false) = 6 := by
  have hstep : startCount (g, false) =
      ((List.range (g + 5)).filter fun i : ℕ =>
        decide (1 ≤ i ∧ i < 4) || decide (g + 1 ≤ i ∧ i < g + 4)).length := by
    rw [startCount]
    congr 1
    apply List.filter_congr
    intro i _
    simp only [near, if_neg (by omega : ¬ g = 1)]
    rw [Bool.eq_iff_iff]
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq,
      Bool.eq_false_iff, ne_eq]
    omega
  rw [hstep, length_filter_or_general, filter_and_interval, length_filter_range_interval,
    length_filter_range_interval, length_filter_range_interval]
  omega

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
