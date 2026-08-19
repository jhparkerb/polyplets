/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Weights
import Polyplets.GapWalk

/-!
# Notary piece B, module 1: partial stacks and the reach toolkit

Campaign *Notary*, piece **B** of `docs/notary-kernel-scoping.md` — the
walk-path ↔ configuration bijection. This module defines the objects the
bijection counts and the connectivity toolkit every later module uses.

A **partial stack** is the bottom part of an all-pairs cluster, cut below
some row `i`: rows `1..i` carry exactly two cells each, and below sits either
the fixed contact cell `p = (0, 0)` (*interior* stacks, `IsStackI`) or
nothing, with the row-1 leftmost cell pinned at `x = 0` (*bare* stacks,
`IsStackB`, the `count_stack` normalization of `IsVpConfig`). The membership
invariant is exactly "no component is dead": **every king-component of the
stack meets the top row**. Cells above row `i` can only ever attach through
row `i` (king steps move `y` by at most 1), so a component missing the top
row can never rejoin — these are precisely the partial configurations that
can still grow into a `CFGV`/`CFGVt`/`CFGVp` configuration.

The walk state `(g, c)` of `GapWalk.lean` is read off a stack as: `g` = gap
between the two top-row cells, and the class `c` is `J` iff the stack is a
single component — equivalently (and this is the form everything below
uses), iff the left top cell reaches the right one. With two-cell rows a
stack has at most two components, each holding one top cell, so the flag is
exhaustive.

`reach S p q` is the king-path relation inside `S` (the step relation of
`KingConnected`, made binary). It is decidable through `Compute.lean`'s
closure (`reachSet`), which makes the stack predicates decidable and the
stack sets below (`STKI`, `STKB`) computable Finsets in the `Weights.lean`
window idiom, with window-independence lemmas (`mem_STKI`, `mem_STKB`).

Everything here is pre-verified numerically
(`verify_bij_statements.py`, checks A/B/F: binary class, start counts,
supports and windows, for all stacks of `≤ 3` rows).
-/

namespace Polyplets

open GapWalk (St states)

/-! ## The reach relation -/

/-- King-path reachability inside `S`: the step relation of `KingConnected`,
made binary. `KingConnected S` is definitionally `∀ p ∈ S, ∀ q ∈ S,
reach S p q`. -/
def reach (S : Finset (ℤ × ℤ)) (p q : ℤ × ℤ) : Prop :=
  Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q

theorem reach_refl (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) : reach S p p :=
  Relation.ReflTransGen.refl

theorem reach_trans {S : Finset (ℤ × ℤ)} {p q r : ℤ × ℤ}
    (h1 : reach S p q) (h2 : reach S q r) : reach S p r :=
  Relation.ReflTransGen.trans h1 h2

/-- The step relation is symmetric (`kingAdj_symm`), hence so is its
reflexive-transitive closure. -/
theorem reach_symm {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (h : reach S p q) : reach S q p := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | tail hab hbc ih =>
      exact Relation.ReflTransGen.head ⟨hbc.2.1, hbc.1, kingAdj_symm hbc.2.2⟩ ih

/-- Reach is monotone in the ambient set. -/
theorem reach_mono {S T : Finset (ℤ × ℤ)} (hST : S ⊆ T) {p q : ℤ × ℤ}
    (h : reach S p q) : reach T p q :=
  Relation.ReflTransGen.mono
    (fun _ _ h => ⟨hST h.1, hST h.2.1, h.2.2⟩) h

/-- Extend a reach by one king edge. -/
theorem reach_tail {S : Finset (ℤ × ℤ)} {p a b : ℤ × ℤ}
    (h : reach S p a) (ha : a ∈ S) (hb : b ∈ S) (hadj : kingAdj a b) :
    reach S p b :=
  Relation.ReflTransGen.tail h ⟨ha, hb, hadj⟩

/-- A nontrivial reach starts inside `S`. -/
theorem reach_mem_left {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (hne : p ≠ q) (h : reach S p q) : p ∈ S := by
  rcases Relation.ReflTransGen.cases_head h with rfl | ⟨b, hstep, _⟩
  · exact absurd rfl hne
  · exact hstep.1

/-- A nontrivial reach ends inside `S`. -/
theorem reach_mem_right {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (hne : p ≠ q) (h : reach S p q) : q ∈ S :=
  reach_mem_left (Ne.symm hne) (reach_symm h)

/-- **The closed-set principle** — the workhorse of every non-reachability
argument downstream: a set `C` closed under king steps of `S` traps every
reach that starts in it. Induction over the `ReflTransGen`. -/
theorem reach_closed {S : Finset (ℤ × ℤ)} {C : Set (ℤ × ℤ)}
    (hcl : ∀ a ∈ C, ∀ b ∈ S, kingAdj a b → b ∈ C)
    {p q : ℤ × ℤ} (hp : p ∈ C) (h : reach S p q) : q ∈ C := by
  induction h with
  | refl => exact hp
  | tail hab hbc ih => exact hcl _ ih _ hbc.2.1 hbc.2.2

/-- Reach through the computable closure of `Compute.lean`: this is what
makes `reach` decidable. Forward: `Relation.ReflTransGen.cases_head` splits
off triviality, then `reachSet_complete`; backward: `reachSet_sound` at
`k = S.card` (which is `reachSet`'s definition). -/
theorem reach_iff_reachSet {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} :
    reach S p q ↔ p = q ∨ (p ∈ S ∧ q ∈ reachSet S p) := by
  constructor
  · intro h
    rcases Relation.ReflTransGen.cases_head h with rfl | ⟨b, hstep, _⟩
    · exact Or.inl rfl
    · exact Or.inr ⟨hstep.1, reachSet_complete hstep.1 h⟩
  · rintro (rfl | ⟨hp, hq⟩)
    · exact Relation.ReflTransGen.refl
    · exact reachSet_sound hp S.card q hq

instance (S : Finset (ℤ × ℤ)) (p q : ℤ × ℤ) : Decidable (reach S p q) :=
  decidable_of_iff _ reach_iff_reachSet.symm

/-- King adjacency moves the row by at most one. -/
theorem kingAdj_y {a b : ℤ × ℤ} (h : kingAdj a b) : |a.2 - b.2| ≤ 1 :=
  h.2.2

/-- **x-spread along a reach**: a king path plants a cell in every column it
crosses (`exists_x_eq_of_cross`), so the horizontal distance covered inside
`S` is at most `S.card − 1`. Signed version; mirror the proof of
`connected_sub_x_le` (`Weights.lean`), which consumed a two-sided
`KingConnected` — here the single path `h` serves the `q.1 > p.1` case and
the trivial bound needs only `q ∈ S` for `card ≥ 1`. -/
theorem reach_sub_x_le {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (h : reach S p q) (hq : q ∈ S) : q.1 - p.1 ≤ (S.card : ℤ) - 1 := by
  rcases le_total q.1 p.1 with hle | hle
  · have hpos : 0 < S.card := Finset.card_pos.mpr ⟨q, hq⟩
    omega
  · have hsub : Finset.Icc p.1 q.1 ⊆ S.image Prod.fst := by
      intro t ht
      rw [Finset.mem_Icc] at ht
      rw [Finset.mem_image]
      rcases ht.2.eq_or_lt with heq | hlt
      · exact ⟨q, hq, heq.symm⟩
      · obtain ⟨c, hcS, hct⟩ := exists_x_eq_of_cross h ht.1 (by omega)
        exact ⟨c, hcS, hct⟩
    have hcard : (Finset.Icc p.1 q.1).card ≤ S.card :=
      le_trans (Finset.card_le_card hsub) Finset.card_image_le
    rw [Int.card_Icc] at hcard
    omega

/-- Two-sided x-spread, from `reach_sub_x_le` on `h` and `reach_symm h`. -/
theorem reach_abs_x_le {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ}
    (h : reach S p q) (hp : p ∈ S) (hq : q ∈ S) :
    |q.1 - p.1| ≤ (S.card : ℤ) - 1 := by
  have h1 : q.1 - p.1 ≤ (S.card : ℤ) - 1 := reach_sub_x_le h hq
  have h2 : p.1 - q.1 ≤ (S.card : ℤ) - 1 := reach_sub_x_le (reach_symm h) hp
  rw [abs_le]
  exact ⟨by omega, h1⟩

/-! ## Row bookkeeping -/

/-- A row of size 2 is exactly its two exhibited distinct cells:
`S.filter (·.2 = y)` has card 2 and contains both, so equals `{a, b}`
(`Finset.eq_of_subset_of_card_le`). -/
theorem row_eq_pair {S : Finset (ℤ × ℤ)} {y : ℤ} {a b : ℤ × ℤ}
    (hsize : rowSize S y = 2) (ha : a ∈ S) (hb : b ∈ S)
    (hay : a.2 = y) (hby : b.2 = y) (hne : a ≠ b) :
    ∀ q ∈ S, q.2 = y → q = a ∨ q = b := by
  have hsub : ({a, b} : Finset (ℤ × ℤ)) ⊆ S.filter fun c => c.2 = y := by
    intro c hc
    rw [Finset.mem_insert, Finset.mem_singleton] at hc
    rw [Finset.mem_filter]
    rcases hc with rfl | rfl
    · exact ⟨ha, hay⟩
    · exact ⟨hb, hby⟩
  have hcard2 : ({a, b} : Finset (ℤ × ℤ)).card = 2 := Finset.card_pair hne
  have heq : ({a, b} : Finset (ℤ × ℤ)) = S.filter fun c => c.2 = y :=
    Finset.eq_of_subset_of_card_le hsub (by rw [hcard2]; exact hsize.le)
  intro q hq hqy
  have : q ∈ ({a, b} : Finset (ℤ × ℤ)) := by
    rw [heq, Finset.mem_filter]; exact ⟨hq, hqy⟩
  rwa [Finset.mem_insert, Finset.mem_singleton] at this

/-- A row of size 2 exhibits two cells, ordered by `x`. -/
theorem row_two_cells {S : Finset (ℤ × ℤ)} {y : ℤ} (h2 : rowSize S y = 2) :
    ∃ a b : ℤ × ℤ, a ∈ S ∧ b ∈ S ∧ a.2 = y ∧ b.2 = y ∧ a.1 < b.1 ∧
      ∀ q ∈ S, q.2 = y → q = a ∨ q = b := by
  obtain ⟨u, v, huv, heq⟩ := Finset.card_eq_two.mp h2
  have huf : u ∈ S.filter fun c => c.2 = y := by rw [heq]; exact Finset.mem_insert_self _ _
  have hvf : v ∈ S.filter fun c => c.2 = y := by
    rw [heq]; exact Finset.mem_insert_of_mem (Finset.mem_singleton_self _)
  rw [Finset.mem_filter] at huf hvf
  obtain ⟨huS, huy⟩ := huf
  obtain ⟨hvS, hvy⟩ := hvf
  rcases lt_or_gt_of_ne (fun h => huv (Prod.ext h (huy.trans hvy.symm))) with hlt | hgt
  · exact ⟨u, v, huS, hvS, huy, hvy, hlt, row_eq_pair h2 huS hvS huy hvy huv⟩
  · exact ⟨v, u, hvS, huS, hvy, huy, hgt,
      fun q hq hqy => (row_eq_pair h2 huS hvS huy hvy huv q hq hqy).symm⟩

/-- Cardinality is the sum of row sizes over any covering row range
(`Finset.card_eq_sum_card_fiberwise` along `p ↦ (p.2 − y0).toNat`). -/
theorem card_eq_sum_rowSize {S : Finset (ℤ × ℤ)} {y0 : ℤ} {h : ℕ}
    (hy : ∀ p ∈ S, y0 ≤ p.2 ∧ p.2 < y0 + h) :
    S.card = (Finset.range h).sum fun r => rowSize S (y0 + r) := by
  have := Finset.card_eq_sum_card_fiberwise
    (s := S) (f := fun p : ℤ × ℤ => (p.2 - y0).toNat) (t := Finset.range h)
    (by
      intro p hp
      rw [Finset.mem_coe] at hp
      rw [Finset.mem_coe, Finset.mem_range]
      dsimp only
      obtain ⟨h1, h2⟩ := hy p hp
      omega)
  rw [this]
  apply Finset.sum_congr rfl
  intro r hr
  rw [Finset.mem_range] at hr
  have hcongr : S.filter (fun p => (p.2 - y0).toNat = r) = S.filter (fun p => p.2 = y0 + r) := by
    apply Finset.filter_congr
    intro p hp
    obtain ⟨h1, h2⟩ := hy p hp
    constructor
    · intro heq; omega
    · intro heq; omega
  rw [rowSize, hcongr]

theorem rowSize_insert_same {S : Finset (ℤ × ℤ)} {u : ℤ × ℤ} {y : ℤ}
    (hu : u ∉ S) (hy : u.2 = y) :
    rowSize (insert u S) y = rowSize S y + 1 := by
  unfold rowSize
  rw [Finset.filter_insert, if_pos hy]
  apply Finset.card_insert_of_notMem
  intro hmem
  exact hu (Finset.mem_filter.mp hmem).1

theorem rowSize_insert_other {S : Finset (ℤ × ℤ)} {u : ℤ × ℤ} {y : ℤ}
    (hy : u.2 ≠ y) : rowSize (insert u S) y = rowSize S y := by
  unfold rowSize
  rw [Finset.filter_insert, if_neg hy]

/-- Row extraction: the leftmost `x` in row `y` (junk `0` on empty rows;
`Finset.min : WithBot`, read through `Option.getD`). -/
def rowMinX (S : Finset (ℤ × ℤ)) (y : ℤ) : ℤ :=
  ((S.filter fun p => p.2 = y).image Prod.fst).min.getD 0

/-- Row extraction: the rightmost `x` in row `y`. -/
def rowMaxX (S : Finset (ℤ × ℤ)) (y : ℤ) : ℤ :=
  ((S.filter fun p => p.2 = y).image Prod.fst).max.getD 0

theorem rowMinX_mem {S : Finset (ℤ × ℤ)} {y : ℤ} (h : 1 ≤ rowSize S y) :
    (rowMinX S y, y) ∈ S := by
  have hne : (S.filter fun p => p.2 = y).Nonempty :=
    Finset.card_pos.mp (by change 0 < rowSize S y; omega)
  have himne : ((S.filter fun p => p.2 = y).image Prod.fst).Nonempty := hne.image _
  obtain ⟨x0, hx0⟩ := Finset.min_of_nonempty himne
  have hmem := Finset.mem_of_min hx0
  rw [Finset.mem_image] at hmem
  obtain ⟨c, hcf, hcx⟩ := hmem
  rw [Finset.mem_filter] at hcf
  have hval : rowMinX S y = x0 := by unfold rowMinX; rw [hx0]; rfl
  rw [hval, ← hcx, ← hcf.2]
  exact hcf.1

theorem rowMinX_le {S : Finset (ℤ × ℤ)} {y : ℤ} {p : ℤ × ℤ}
    (hp : p ∈ S) (hy : p.2 = y) : rowMinX S y ≤ p.1 := by
  have hpf : p.1 ∈ (S.filter fun c => c.2 = y).image Prod.fst := by
    rw [Finset.mem_image]
    exact ⟨p, Finset.mem_filter.mpr ⟨hp, hy⟩, rfl⟩
  have hmin := Finset.min_le hpf
  obtain ⟨x0, hx0⟩ := Finset.min_of_nonempty
    (⟨p.1, hpf⟩ : ((S.filter fun c => c.2 = y).image Prod.fst).Nonempty)
  have hval : rowMinX S y = x0 := by unfold rowMinX; rw [hx0]; rfl
  rw [hval]
  rw [hx0] at hmin
  exact_mod_cast hmin

theorem rowMaxX_mem {S : Finset (ℤ × ℤ)} {y : ℤ} (h : 1 ≤ rowSize S y) :
    (rowMaxX S y, y) ∈ S := by
  have hne : (S.filter fun p => p.2 = y).Nonempty :=
    Finset.card_pos.mp (by change 0 < rowSize S y; omega)
  have himne : ((S.filter fun p => p.2 = y).image Prod.fst).Nonempty := hne.image _
  obtain ⟨x0, hx0⟩ := Finset.max_of_nonempty himne
  have hmem := Finset.mem_of_max hx0
  rw [Finset.mem_image] at hmem
  obtain ⟨c, hcf, hcx⟩ := hmem
  rw [Finset.mem_filter] at hcf
  have hval : rowMaxX S y = x0 := by unfold rowMaxX; rw [hx0]; rfl
  rw [hval, ← hcx, ← hcf.2]
  exact hcf.1

theorem le_rowMaxX {S : Finset (ℤ × ℤ)} {y : ℤ} {p : ℤ × ℤ}
    (hp : p ∈ S) (hy : p.2 = y) : p.1 ≤ rowMaxX S y := by
  have hpf : p.1 ∈ (S.filter fun c => c.2 = y).image Prod.fst := by
    rw [Finset.mem_image]
    exact ⟨p, Finset.mem_filter.mpr ⟨hp, hy⟩, rfl⟩
  have hmax := Finset.le_max hpf
  obtain ⟨x0, hx0⟩ := Finset.max_of_nonempty
    (⟨p.1, hpf⟩ : ((S.filter fun c => c.2 = y).image Prod.fst).Nonempty)
  have hval : rowMaxX S y = x0 := by unfold rowMaxX; rw [hx0]; rfl
  rw [hval]
  rw [hx0] at hmax
  exact_mod_cast hmax

/-- Membership in `states`, reproved locally (`GapWalkCanon.lean`'s `mem_states`
is not imported here). -/
private theorem mem_states' (cap g : Nat) (c : Bool) :
    (g, c) ∈ states cap ↔ 1 ≤ g ∧ g ≤ cap := by
  unfold states
  simp only [List.mem_flatMap, List.mem_range, List.mem_cons, List.not_mem_nil, or_false]
  constructor
  · rintro ⟨i, hi, h | h⟩ <;> (injection h with h1 h2; omega)
  · rintro ⟨h1, h2⟩
    refine ⟨g - 1, by omega, ?_⟩
    have hg : g - 1 + 1 = g := by omega
    cases c
    · exact Or.inr (by simp [hg])
    · exact Or.inl (by simp [hg])

/-- The state list of the walk has no duplicates (needed to convert
`Finset` sums over `(states cap).toFinset` into the walk's list sums). -/
theorem states_nodup (cap : ℕ) : (states cap).Nodup := by
  induction cap with
  | zero => simp [states]
  | succ n ih =>
      have hsplit : states (n + 1) = states n ++ [(n + 1, true), (n + 1, false)] := by
        unfold states
        rw [List.range_succ, List.flatMap_append]
        rfl
      rw [hsplit, List.nodup_append']
      refine ⟨ih, by simp, ?_⟩
      intro x hx hx2
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hx2
      obtain ⟨-, hg⟩ := (mem_states' n x.1 x.2).mp hx
      rcases hx2 with heq | heq
      · rw [heq] at hg; exact absurd hg (by omega)
      · rw [heq] at hg; exact absurd hg (by omega)

/-! ## Partial stacks -/

/-- Every cell of `S` king-reaches one of the two designated top cells —
"no component is dead". -/
def stackOK (S : Finset (ℤ × ℤ)) (tL tR : ℤ × ℤ) : Prop :=
  ∀ p ∈ S, reach S p tL ∨ reach S p tR

instance (S : Finset (ℤ × ℤ)) (tL tR : ℤ × ℤ) : Decidable (stackOK S tL tR) := by
  unfold stackOK; infer_instance

/-- `S` is an **interior partial stack** of `i` rows in state `(g, c)`:
the contact cell `p = (0,0)` alone on row 0, rows `1..i` with exactly two
cells each, every king-component meeting the top row `i` whose two cells
sit at gap `g`, and class flag `c` = "the two top cells are joined".
The top-pair witness `p` is necessarily the *left* top cell (`g ≥ 1` and
the row holds exactly two cells), hence unique. -/
def IsStackI (i g : ℕ) (c : Bool) (S : Finset (ℤ × ℤ)) : Prop :=
  1 ≤ g ∧
  S.card = 2 * i + 1 ∧
  ((0 : ℤ), (0 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (i : ℤ)) ∧
  rowSize S 0 = 1 ∧
  (∀ r ∈ Finset.Icc 1 i, rowSize S (r : ℤ) = 2) ∧
  ∃ p ∈ S, p.2 = (i : ℤ) ∧ (p.1 + (g : ℤ), (i : ℤ)) ∈ S ∧
    stackOK S p (p.1 + (g : ℤ), (i : ℤ)) ∧
    (c = true ↔ reach S p (p.1 + (g : ℤ), (i : ℤ)))

/-- `S` is a **bare partial stack** of `i` rows in state `(g, c)`: rows
`1..i` only, two cells each, anchored like `IsVpConfig` (row-1 leftmost cell
at `(0, 1)`), same top-row state reading. -/
def IsStackB (i g : ℕ) (c : Bool) (S : Finset (ℤ × ℤ)) : Prop :=
  1 ≤ g ∧
  S.card = 2 * i ∧
  ((0 : ℤ), (1 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 1 ≤ p.2 ∧ p.2 ≤ (i : ℤ)) ∧
  (∀ p ∈ S, p.2 = 1 → 0 ≤ p.1) ∧
  (∀ r ∈ Finset.Icc 1 i, rowSize S (r : ℤ) = 2) ∧
  ∃ p ∈ S, p.2 = (i : ℤ) ∧ (p.1 + (g : ℤ), (i : ℤ)) ∈ S ∧
    stackOK S p (p.1 + (g : ℤ), (i : ℤ)) ∧
    (c = true ↔ reach S p (p.1 + (g : ℤ), (i : ℤ)))

instance (i g : ℕ) (c : Bool) (S : Finset (ℤ × ℤ)) :
    Decidable (IsStackI i g c S) := by
  unfold IsStackI; infer_instance

instance (i g : ℕ) (c : Bool) (S : Finset (ℤ × ℤ)) :
    Decidable (IsStackB i g c S) := by
  unfold IsStackB; infer_instance

/-! ## Top-pair extraction

With `1 ≤ i` the top row has exactly two cells (`r = i` lies in the `Icc`),
so the witness of the `∃` clause is forced to be the left one,
`(rowMinX S i, i)`, with the right one `g` to its east at `rowMaxX S i`. -/

/-- Common extraction argument for `isStackI_top`/`isStackB_top`: given just
the top-row-size clause and the `∃` top-pair witness (the two fields whose
shape is identical between `IsStackI` and `IsStackB`), the top pair is
`(rowMinX, i), (rowMinX + g, i)`. By `row_eq_pair` the witness `p` and
`p + (g, 0)` are the row's two cells; `p` is forced left (`g ≥ 1`), so
`p.1 = rowMinX` (`rowMinX_le`/`rowMinX_mem`) and dually for `rowMaxX`. -/
private theorem top_extraction {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (hg1 : 1 ≤ g)
    (hrow : ∀ r ∈ Finset.Icc 1 i, rowSize S (r : ℤ) = 2)
    (hex : ∃ p ∈ S, p.2 = (i : ℤ) ∧ (p.1 + (g : ℤ), (i : ℤ)) ∈ S ∧
      stackOK S p (p.1 + (g : ℤ), (i : ℤ)) ∧
      (c = true ↔ reach S p (p.1 + (g : ℤ), (i : ℤ)))) :
    (rowMinX S (i : ℤ), (i : ℤ)) ∈ S ∧
    (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∈ S ∧
    rowMinX S (i : ℤ) + (g : ℤ) = rowMaxX S (i : ℤ) ∧
    stackOK S (rowMinX S (i : ℤ), (i : ℤ)) (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∧
    (c = true ↔ reach S (rowMinX S (i : ℤ), (i : ℤ))
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ))) ∧
    ∀ q ∈ S, q.2 = (i : ℤ) →
      q = (rowMinX S (i : ℤ), (i : ℤ)) ∨ q = (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) := by
  obtain ⟨p, hpS, hpi, hpgS, hOK, hc⟩ := hex
  have hsize2 : rowSize S (i : ℤ) = 2 := hrow i (Finset.mem_Icc.mpr ⟨hi, le_refl i⟩)
  have hgpos : (0 : ℤ) < (g : ℤ) := by exact_mod_cast hg1
  have hne : p ≠ (p.1 + (g : ℤ), (i : ℤ)) := by
    intro heq
    have hfst : p.1 = p.1 + (g : ℤ) := congrArg Prod.fst heq
    omega
  have hpair := row_eq_pair hsize2 hpS hpgS hpi rfl hne
  have hminmem := rowMinX_mem (S := S) (y := (i : ℤ)) (by omega)
  have hminle := rowMinX_le (S := S) hpS hpi
  have hmaxmem := rowMaxX_mem (S := S) (y := (i : ℤ)) (by omega)
  have hgle2 := le_rowMaxX (S := S) (y := (i : ℤ)) hpgS rfl
  have hminp : rowMinX S (i : ℤ) = p.1 := by
    rcases hpair _ hminmem rfl with heq | heq
    · exact congrArg Prod.fst heq
    · have hfst : rowMinX S (i : ℤ) = p.1 + (g : ℤ) := congrArg Prod.fst heq
      omega
  have hmaxp : rowMaxX S (i : ℤ) = p.1 + (g : ℤ) := by
    rcases hpair _ hmaxmem rfl with heq | heq
    · have hfst : rowMaxX S (i : ℤ) = p.1 := congrArg Prod.fst heq
      omega
    · exact congrArg Prod.fst heq
  have hpeq : ((p.1 : ℤ), (i : ℤ)) = p := by rw [← hpi]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · rw [hminp, hpeq]; exact hpS
  · rw [hminp]; exact hpgS
  · rw [hminp, hmaxp]
  · rw [hminp, hpeq]; exact hOK
  · rw [hminp, hpeq]; exact hc
  · intro q hq hqi
    rw [hminp, hpeq]
    exact hpair q hq hqi

/-- Extraction, interior: the top pair of a stack is
`(rowMinX, i), (rowMinX + g, i)` with `rowMinX + g = rowMaxX`, and the
`stackOK`/class clauses hold at that pair. -/
theorem isStackI_top {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI i g c S) :
    (rowMinX S (i : ℤ), (i : ℤ)) ∈ S ∧
    (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∈ S ∧
    rowMinX S (i : ℤ) + (g : ℤ) = rowMaxX S (i : ℤ) ∧
    stackOK S (rowMinX S (i : ℤ), (i : ℤ)) (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∧
    (c = true ↔ reach S (rowMinX S (i : ℤ), (i : ℤ))
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ))) ∧
    ∀ q ∈ S, q.2 = (i : ℤ) →
      q = (rowMinX S (i : ℤ), (i : ℤ)) ∨ q = (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) :=
  top_extraction hi h.1 h.2.2.2.2.2.1 h.2.2.2.2.2.2

/-- Extraction, bare: same statement, same proof. -/
theorem isStackB_top {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB i g c S) :
    (rowMinX S (i : ℤ), (i : ℤ)) ∈ S ∧
    (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∈ S ∧
    rowMinX S (i : ℤ) + (g : ℤ) = rowMaxX S (i : ℤ) ∧
    stackOK S (rowMinX S (i : ℤ), (i : ℤ)) (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∧
    (c = true ↔ reach S (rowMinX S (i : ℤ), (i : ℤ))
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ))) ∧
    ∀ q ∈ S, q.2 = (i : ℤ) →
      q = (rowMinX S (i : ℤ), (i : ℤ)) ∨ q = (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) :=
  top_extraction hi h.1 h.2.2.2.2.2.1 h.2.2.2.2.2.2

/-- The state extractor: gap and joined-flag of row `y`, computably. On a
stack this recovers `(g, c)` (`isStackI_topState` below). -/
def topState (S : Finset (ℤ × ℤ)) (y : ℤ) : ℕ × Bool :=
  ((rowMaxX S y - rowMinX S y).toNat,
    decide (reach S (rowMinX S y, y) (rowMaxX S y, y)))

/-- Common argument for `isStackI_topState`/`isStackB_topState`: given the
top-pair extraction data, `topState` recovers `(g, c)`. -/
private theorem topState_extraction {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (h : (rowMinX S (i : ℤ), (i : ℤ)) ∈ S ∧
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∈ S ∧
      rowMinX S (i : ℤ) + (g : ℤ) = rowMaxX S (i : ℤ) ∧
      stackOK S (rowMinX S (i : ℤ), (i : ℤ)) (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) ∧
      (c = true ↔ reach S (rowMinX S (i : ℤ), (i : ℤ))
        (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ))) ∧
      ∀ q ∈ S, q.2 = (i : ℤ) →
        q = (rowMinX S (i : ℤ), (i : ℤ)) ∨ q = (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ))) :
    topState S (i : ℤ) = (g, c) := by
  obtain ⟨-, -, heq, -, hiff, -⟩ := h
  unfold topState
  have h1 : (rowMaxX S (i : ℤ) - rowMinX S (i : ℤ)).toNat = g := by
    rw [← heq]; simp
  have h2 : decide (reach S (rowMinX S (i : ℤ), (i : ℤ)) (rowMaxX S (i : ℤ), (i : ℤ))) = c := by
    rw [← heq]
    cases c with
    | true => rw [decide_eq_true_eq]; exact hiff.mp rfl
    | false =>
        rw [decide_eq_false_iff_not]
        intro hr
        exact absurd (hiff.mpr hr) (by decide)
  rw [h1, h2]

theorem isStackI_topState {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI i g c S) : topState S (i : ℤ) = (g, c) :=
  topState_extraction (isStackI_top hi h)

theorem isStackB_topState {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB i g c S) : topState S (i : ℤ) = (g, c) :=
  topState_extraction (isStackB_top hi h)

/-- A set is a stack in at most one state (immediate from `*_topState`). -/
theorem isStackI_state_unique {i g₁ g₂ : ℕ} {c₁ c₂ : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h1 : IsStackI i g₁ c₁ S) (h2 : IsStackI i g₂ c₂ S) :
    g₁ = g₂ ∧ c₁ = c₂ :=
  Prod.ext_iff.mp ((isStackI_topState hi h1).symm.trans (isStackI_topState hi h2))

theorem isStackB_state_unique {i g₁ g₂ : ℕ} {c₁ c₂ : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h1 : IsStackB i g₁ c₁ S) (h2 : IsStackB i g₂ c₂ S) :
    g₁ = g₂ ∧ c₁ = c₂ :=
  Prod.ext_iff.mp ((isStackB_topState hi h1).symm.trans (isStackB_topState hi h2))

/-! ## Supports and windows -/

/-- A joined stack is one component, so its top gap is bounded by the
x-spread: `g ≤ card − 1 = 2i` (`reach_abs_x_le` on the top pair). -/
theorem isStackI_J_le {i g : ℕ} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI i g true S) : g ≤ 2 * i := by
  obtain ⟨hL, hR, -, -, hiff, -⟩ := isStackI_top hi h
  have hreach : reach S (rowMinX S (i : ℤ), (i : ℤ))
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) := hiff.mp rfl
  have hbound := reach_abs_x_le hreach hL hR
  rw [abs_le] at hbound
  have hcardZ : (S.card : ℤ) = 2 * (i : ℤ) + 1 := by exact_mod_cast h.2.1
  omega

/-- Bare version (card `2i` gives the sharper `2i − 1`; state what B4
consumes). -/
theorem isStackB_J_le {i g : ℕ} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB i g true S) : g ≤ 2 * i := by
  obtain ⟨hL, hR, -, -, hiff, -⟩ := isStackB_top hi h
  have hreach : reach S (rowMinX S (i : ℤ), (i : ℤ))
      (rowMinX S (i : ℤ) + (g : ℤ), (i : ℤ)) := hiff.mp rfl
  have hbound := reach_abs_x_le hreach hL hR
  rw [abs_le] at hbound
  have hcardZ : (S.card : ℤ) = 2 * (i : ℤ) := by exact_mod_cast h.2.1
  omega

/-- Every cell of an interior stack has `|x| ≤ 4i + 2g`: the anchor reaches
a top cell (spread `≤ 2i` by `reach_abs_x_le`, so that top has `|x| ≤ 2i`
and the other `|x| ≤ 2i + g`), and every cell is within `2i` of one top. -/
theorem isStackI_x_le {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackI i g c S) :
    ∀ p ∈ S, |p.1| ≤ 4 * (i : ℤ) + 2 * (g : ℤ) := by
  obtain ⟨hL, hR, _, hOK, -, -⟩ := isStackI_top hi h
  have hcardZ : (S.card : ℤ) = 2 * (i : ℤ) + 1 := by exact_mod_cast h.2.1
  have h0 : ((0 : ℤ), (0 : ℤ)) ∈ S := h.2.2.1
  have hspread : ∀ {a b : ℤ × ℤ}, reach S a b → a ∈ S → b ∈ S →
      |b.1 - a.1| ≤ 2 * (i : ℤ) := by
    intro a b hr ha hb
    have hbnd := reach_abs_x_le hr ha hb
    rw [abs_le] at hbnd ⊢
    omega
  have htops : |rowMinX S (i : ℤ)| ≤ 2 * (i : ℤ) + (g : ℤ) ∧
      |rowMinX S (i : ℤ) + (g : ℤ)| ≤ 2 * (i : ℤ) + (g : ℤ) := by
    rcases hOK ((0 : ℤ), (0 : ℤ)) h0 with h1 | h1
    · have hb := hspread (reach_symm h1) hL h0
      simp only [abs_le] at hb ⊢
      omega
    · have hb := hspread (reach_symm h1) hR h0
      simp only [abs_le] at hb ⊢
      omega
  intro p hp
  simp only [abs_le]
  rcases hOK p hp with h1 | h1
  · have hb := hspread h1 hp hL
    simp only [abs_le] at hb
    have ht := htops.1
    simp only [abs_le] at ht
    omega
  · have hb := hspread h1 hp hR
    simp only [abs_le] at hb
    have ht := htops.2
    simp only [abs_le] at ht
    omega

/-- Bare version, anchored at `(0, 1)` instead of the origin. -/
theorem isStackB_x_le {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)}
    (hi : 1 ≤ i) (h : IsStackB i g c S) :
    ∀ p ∈ S, |p.1| ≤ 4 * (i : ℤ) + 2 * (g : ℤ) := by
  obtain ⟨hL, hR, _, hOK, -, -⟩ := isStackB_top hi h
  have hcardZ : (S.card : ℤ) = 2 * (i : ℤ) := by exact_mod_cast h.2.1
  have h0 : ((0 : ℤ), (1 : ℤ)) ∈ S := h.2.2.1
  have hspread : ∀ {a b : ℤ × ℤ}, reach S a b → a ∈ S → b ∈ S →
      |b.1 - a.1| ≤ 2 * (i : ℤ) := by
    intro a b hr ha hb
    have hbnd := reach_abs_x_le hr ha hb
    rw [abs_le] at hbnd ⊢
    omega
  have htops : |rowMinX S (i : ℤ)| ≤ 2 * (i : ℤ) + (g : ℤ) ∧
      |rowMinX S (i : ℤ) + (g : ℤ)| ≤ 2 * (i : ℤ) + (g : ℤ) := by
    rcases hOK ((0 : ℤ), (1 : ℤ)) h0 with h1 | h1
    · have hb := hspread (reach_symm h1) hL h0
      simp only [abs_le] at hb ⊢
      omega
    · have hb := hspread (reach_symm h1) hR h0
      simp only [abs_le] at hb ⊢
      omega
  intro p hp
  simp only [abs_le]
  rcases hOK p hp with h1 | h1
  · have hb := hspread h1 hp hL
    simp only [abs_le] at hb
    have ht := htops.1
    simp only [abs_le] at ht
    omega
  · have hb := hspread h1 hp hR
    simp only [abs_le] at hb
    have ht := htops.2
    simp only [abs_le] at ht
    omega

/-! ## The stack sets, as computable Finsets -/

/-- Interior stacks of `i` rows in state `(g, c)`, enumerated in the
`Weights.lean` window idiom. `mem_STKI` shows the window is invisible. -/
def STKI (i g : ℕ) (c : Bool) : Finset (Finset (ℤ × ℤ)) :=
  ((window (4 * i + 2 * g) 0 (i + 1)).powersetCard (2 * i + 1)).filter
    (IsStackI i g c)

/-- Bare stacks of `i` rows in state `(g, c)`. -/
def STKB (i g : ℕ) (c : Bool) : Finset (Finset (ℤ × ℤ)) :=
  ((window (4 * i + 2 * g) 1 i).powersetCard (2 * i)).filter
    (IsStackB i g c)

/-- **Window independence**: membership in `STKI` is exactly `IsStackI`
(for `1 ≤ i`; the encoding direction is `isStackI_x_le` plus the row
bounds, via `mem_window`). -/
theorem mem_STKI {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)} (hi : 1 ≤ i) :
    S ∈ STKI i g c ↔ IsStackI i g c S := by
  rw [STKI, Finset.mem_filter]
  constructor
  · exact fun hmem => hmem.2
  · intro hS
    refine ⟨?_, hS⟩
    rw [Finset.mem_powersetCard]
    refine ⟨?_, hS.2.1⟩
    intro p hp
    have hx := isStackI_x_le hi hS p hp
    rw [abs_le] at hx
    have hy := hS.2.2.2.1 p hp
    rw [mem_window]
    refine ⟨?_, ?_, ?_, ?_⟩
    · push_cast; omega
    · push_cast; omega
    · omega
    · push_cast; omega

theorem mem_STKB {i g : ℕ} {c : Bool} {S : Finset (ℤ × ℤ)} (hi : 1 ≤ i) :
    S ∈ STKB i g c ↔ IsStackB i g c S := by
  rw [STKB, Finset.mem_filter]
  constructor
  · exact fun hmem => hmem.2
  · intro hS
    refine ⟨?_, hS⟩
    rw [Finset.mem_powersetCard]
    refine ⟨?_, hS.2.1⟩
    intro p hp
    have hx := isStackB_x_le hi hS p hp
    rw [abs_le] at hx
    have hy := hS.2.2.2.1 p hp
    rw [mem_window]
    refine ⟨?_, ?_, ?_, ?_⟩
    · push_cast; omega
    · push_cast; omega
    · omega
    · push_cast; omega

/-- `J`-support of the interior stack counts (what the B4 cone induction
consumes on the far side of `2l + 2`). -/
theorem STKI_card_J_high (i g : ℕ) (hi : 1 ≤ i) (hg : 2 * i < g) :
    (STKI i g true).card = 0 := by
  rw [Finset.card_eq_zero]
  rw [Finset.eq_empty_iff_forall_notMem]
  intro S hS
  rw [mem_STKI hi] at hS
  exact absurd (isStackI_J_le hi hS) (by omega)

theorem STKB_card_J_high (i g : ℕ) (hi : 1 ≤ i) (hg : 2 * i < g) :
    (STKB i g true).card = 0 := by
  rw [Finset.card_eq_zero]
  rw [Finset.eq_empty_iff_forall_notMem]
  intro S hS
  rw [mem_STKB hi] at hS
  exact absurd (isStackB_J_le hi hS) (by omega)

/-! ## Class and connectivity -/

/-- On a stack, "the top cells are joined" is full connectivity: every cell
reaches a top cell, and the two tops reach each other, so everything is
mutually reachable via `reach_symm`/`reach_trans`. -/
theorem stackOK_reach_iff_connected {S : Finset (ℤ × ℤ)} {tL tR : ℤ × ℤ}
    (hL : tL ∈ S) (hR : tR ∈ S) (hOK : stackOK S tL tR) :
    reach S tL tR ↔ KingConnected S := by
  constructor
  · intro h p hp q hq
    have hPtoL : ∀ a ∈ S, reach S a tL := fun a ha =>
      (hOK a ha).elim id (fun hr => reach_trans hr (reach_symm h))
    exact reach_trans (hPtoL p hp) (reach_symm (hPtoL q hq))
  · intro h
    exact h tL hL tR hR

/-! ## Isometry transport (for the reflection in `GapWalkEnds`) -/

/-- Transport of connectivity along any injective, adjacency-preserving
cell map (`Relation.ReflTransGen.lift` on the step relation). -/
private theorem reach_image_aux {S : Finset (ℤ × ℤ)} {f : ℤ × ℤ → ℤ × ℤ}
    (hadj : ∀ a b, kingAdj (f a) (f b) ↔ kingAdj a b) {p q : ℤ × ℤ}
    (h : reach S p q) : reach (S.image f) (f p) (f q) := by
  induction h with
  | refl => exact Relation.ReflTransGen.refl
  | tail hab hbc ih =>
      exact Relation.ReflTransGen.tail ih
        ⟨Finset.mem_image_of_mem f hbc.1, Finset.mem_image_of_mem f hbc.2.1,
          (hadj _ _).mpr hbc.2.2⟩

theorem kingConnected_image_of_adj_iff {S : Finset (ℤ × ℤ)} {f : ℤ × ℤ → ℤ × ℤ}
    (hf : Function.Injective f)
    (hadj : ∀ a b, kingAdj (f a) (f b) ↔ kingAdj a b)
    (h : KingConnected S) : KingConnected (S.image f) := by
  intro p' hp' q' hq'
  rw [Finset.mem_image] at hp' hq'
  obtain ⟨p, hpS, rfl⟩ := hp'
  obtain ⟨q, hqS, rfl⟩ := hq'
  exact reach_image_aux hadj (h p hpS q hqS)

/-- The reflection maps used by the `Vt` bijection: translate by `-cx`,
flip `y` about `cy/2`. -/
def flipMap (cx cy : ℤ) : ℤ × ℤ → ℤ × ℤ := fun p => (p.1 - cx, cy - p.2)

theorem flipMap_injective (cx cy : ℤ) : Function.Injective (flipMap cx cy) := by
  intro a b hab
  unfold flipMap at hab
  rw [Prod.ext_iff] at hab ⊢
  omega

theorem kingAdj_flipMap (cx cy : ℤ) (a b : ℤ × ℤ) :
    kingAdj (flipMap cx cy a) (flipMap cx cy b) ↔ kingAdj a b := by
  unfold flipMap kingAdj
  constructor
  · rintro ⟨hne, hx, hy⟩
    refine ⟨?_, ?_, ?_⟩
    · intro heq; exact hne (by rw [heq])
    · simpa using hx
    · rw [abs_sub_comm] at hy
      simpa using hy
  · rintro ⟨hne, hx, hy⟩
    refine ⟨?_, ?_, ?_⟩
    · intro heq
      apply hne
      rw [Prod.ext_iff] at heq ⊢
      omega
    · simpa using hx
    · rw [abs_sub_comm]
      simpa using hy

/-- Two flips about the same `cy` compose to a translation; the exact
inverse-shift form the bijection needs. -/
theorem flipMap_flipMap (cx cy dx : ℤ) (p : ℤ × ℤ) :
    flipMap dx cy (flipMap cx cy p) = (p.1 - cx - dx, p.2) := by
  unfold flipMap
  rw [Prod.ext_iff]
  refine ⟨rfl, ?_⟩
  ring

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.mem_STKI' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms mem_STKI

/--
info: 'Polyplets.reach_closed' depends on axioms: [propext, Quot.sound]
-/
#guard_msgs in
#print axioms reach_closed

end Polyplets
