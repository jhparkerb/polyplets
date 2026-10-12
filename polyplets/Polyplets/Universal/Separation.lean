/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.Push
import Polyplets.Universal.Finite

/-!
# Separation: walk rows glue and cut `L`-connected sets

Step 1 of the universal diagonal law: *adjacency changes the row index by at
most 1, so a single-cell row is a cut*. A *walk row* is a row holding exactly
one cell of `S`; `band S a b` is the band of cells with rows in `[a, b]`.

* **Glue** (`connected_union`): a union of two `L`-connected pieces sharing a cell
  is `L`-connected.
* **Cut** (`connected_band`): restricting an `L`-connected `S` to `band S r r'`
  preserves `L`-connectivity, provided each cut line is either a walk row of
  `S` or a boundary. Walk surgery in `graph L S` by strong induction on walk
  length: a step escaping the band leaves from THE unique walk-row cell on the
  cut line, and the rest of the walk re-enters through a boundary dart
  (`Walk.exists_boundary_dart`) landing on that same cell, so the excursion is
  excised with `Walk.dropUntil`.
* **Erase-top** (`connected_erase_top`): the corollary peeling case 1 consumes.

**Wager status: verbatim.** Every proof in this file is `Separation.lean`'s with
`kingAdj ↦ Adj L`. The only property of adjacency used anywhere — including in
the boundary-dart excision, the step the brief singles out as the most likely
hiding place for a king dependence — is `adj_abs_dy_le` (`|Δrow| ≤ 1`). No
x-offset, no `|Δx| ≤ 1`, no cardinality of `D` appears.
-/

namespace Polyplets.Universal

/-- The row band `[a, b]` of `S`: the cells whose row lies in `[a, b]`. -/
def band (S : Finset (ℤ × ℤ)) (a b : ℤ) : Finset (ℤ × ℤ) :=
  S.filter fun c => a ≤ c.2 ∧ c.2 ≤ b

/-- Row `r` is a *walk row* of `S`: it holds exactly one cell. -/
def IsWalkRow (S : Finset (ℤ × ℤ)) (r : ℤ) : Prop :=
  (S.filter fun c => c.2 = r).card = 1

lemma mem_band {S : Finset (ℤ × ℤ)} {a b : ℤ} {c : ℤ × ℤ} :
    c ∈ band S a b ↔ c ∈ S ∧ a ≤ c.2 ∧ c.2 ≤ b := Finset.mem_filter

/-- Two cells of `S` on a walk row coincide. -/
lemma IsWalkRow.eq_of_mem {S : Finset (ℤ × ℤ)} {r : ℤ} (h : IsWalkRow S r)
    {a b : ℤ × ℤ} (ha : a ∈ S) (har : a.2 = r) (hb : b ∈ S) (hbr : b.2 = r) :
    a = b :=
  Finset.card_le_one.mp (le_of_eq h)
    a (Finset.mem_filter.mpr ⟨ha, har⟩) b (Finset.mem_filter.mpr ⟨hb, hbr⟩)

/-- **Monotonicity.** A path inside `A` is a path inside any superset `S`. -/
lemma path_mono {L : RowLocal} {A S : Finset (ℤ × ℤ)} (hAS : A ⊆ S) {p q : ℤ × ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ A ∧ b ∈ A ∧ Adj L a b) p q) :
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ Adj L a b) p q :=
  Relation.ReflTransGen.mono (fun _ _ hab => ⟨hAS hab.1, hAS hab.2.1, hab.2.2⟩) h

/-- **Glue.** A union of two `L`-connected sets sharing a cell is `L`-connected:
route any pair through the shared cell. No walk-row hypothesis needed. -/
theorem connected_union {L : RowLocal} {S A B : Finset (ℤ × ℤ)} (hS : S = A ∪ B)
    (hA : Connected L A) (hB : Connected L B) (hAB : (A ∩ B).Nonempty) :
    Connected L S := by
  subst hS
  obtain ⟨x, hx⟩ := hAB
  rw [Finset.mem_inter] at hx
  have to_x : ∀ c ∈ A ∪ B,
      Relation.ReflTransGen
        (fun a b => a ∈ A ∪ B ∧ b ∈ A ∪ B ∧ Adj L a b) c x := by
    intro c hc
    rcases Finset.mem_union.mp hc with h | h
    · exact path_mono Finset.subset_union_left (hA c h x hx.1)
    · exact path_mono Finset.subset_union_right (hB c h x hx.2)
  have from_x : ∀ c ∈ A ∪ B,
      Relation.ReflTransGen
        (fun a b => a ∈ A ∪ B ∧ b ∈ A ∪ B ∧ Adj L a b) x c := by
    intro c hc
    rcases Finset.mem_union.mp hc with h | h
    · exact path_mono Finset.subset_union_left (hA x hx.1 c h)
    · exact path_mono Finset.subset_union_right (hB x hx.2 c h)
  intro p hp q hq
  exact (to_x p hp).trans (from_x q hq)

/-- The excision step shared by both escape directions. A walk `w` runs from a
cell of `B` (the far side of a cut line) to a cell outside it, and every dart
leaving `B` lands on the cut row `c`, which is a walk row of `S` whose cell is
`p`: then `w` passes through `p`, and `w.dropUntil p` is a walk from `p` no
longer than `w`. -/
private lemma exists_walk_from_cut {S : Finset (ℤ × ℤ)} {x q p : ℤ × ℤ} {c : ℤ}
    (w : (graph L S).Walk x q) (B : Set (ℤ × ℤ)) (hx : x ∈ B) (hq : q ∉ B)
    (hcross : ∀ a b : ℤ × ℤ, Adj L a b → a ∈ B → b ∉ B → b.2 = c)
    (hwc : IsWalkRow S c) (hpS : p ∈ S) (hpc : p.2 = c) :
    ∃ w' : (graph L S).Walk p q, w'.length ≤ w.length := by
  obtain ⟨d, hd, hdf, hds⟩ := w.exists_boundary_dart B hx hq
  have hdadj : (graph L S).Adj d.fst d.snd := d.adj
  have hdp : d.snd = p :=
    hwc.eq_of_mem hdadj.2.1 (hcross _ _ hdadj.2.2 hdf hds) hpS hpc
  have hpsup : p ∈ w.support := hdp ▸ w.dart_snd_mem_support_of_mem_darts hd
  exact ⟨w.dropUntil p hpsup, by rw [SimpleGraph.Walk.length_dropUntil]; omega⟩

/-- Walk-surgery core of the cut theorem, by strong induction on walk length
(phrased as induction on an upper bound `N`). Given a `graph L S`-walk between
two cells of the band, the band endpoints are reachable inside
`graph L (band S r r')`: a step escaping the band leaves from THE unique
walk-row cell on the crossed cut line, and the rest of the walk must re-enter
through that same cell (`exists_walk_from_cut`), so the excursion is excised
and the walk shortened. -/
private lemma reachable_seg_aux {L : RowLocal} {S : Finset (ℤ × ℤ)} {r r' : ℤ}
    (hr : IsWalkRow S r ∨ ∀ p ∈ S, r ≤ p.2)
    (hr' : IsWalkRow S r' ∨ ∀ p ∈ S, p.2 ≤ r') :
    ∀ N (p q : ℤ × ℤ), p ∈ band S r r' → q ∈ band S r r' →
      ∀ w : (graph L S).Walk p q, w.length ≤ N →
      (graph L (band S r r')).Reachable p q := by
  intro N
  induction N with
  | zero =>
    intro p q hp hq w hw
    cases w with
    | nil => exact SimpleGraph.Reachable.refl p
    | cons hadj w' =>
      rw [SimpleGraph.Walk.length_cons] at hw
      omega
  | succ N ih =>
    intro p q hp hq w hw
    cases w with
    | nil => exact SimpleGraph.Reachable.refl p
    | @cons _ x _ hadj w' =>
      have hlen : w'.length ≤ N := by
        rw [SimpleGraph.Walk.length_cons] at hw
        omega
      have hxS : x ∈ S := hadj.2.1
      by_cases hx : x ∈ band S r r'
      · -- step stays in the band: prepend it to the IH's reachability
        have hstep : (graph L (band S r r')).Adj p x :=
          graph_adj.mpr ⟨hp, hx, hadj.2.2⟩
        exact hstep.reachable.trans (ih x q hx hq w' hlen)
      · -- step escapes the band, above or below
        have hx2 : x.2 < r ∨ r' < x.2 := by
          by_contra hcon
          push Not at hcon
          exact hx (mem_band.mpr ⟨hxS, hcon.1, hcon.2⟩)
        rcases hx2 with hbelow | habove
        · -- escape below: `p` is THE row-`r` cell; excise down to the re-entry
          have hwr : IsWalkRow S r := by
            rcases hr with h | h
            · exact h
            · exact absurd (h x hxS) (by omega)
          have hp2 : p.2 = r := by
            have hk := adj_abs_dy_le hadj.2.2
            rw [abs_le] at hk
            have := (mem_band.mp hp).2.1
            omega
          obtain ⟨w'', hw''⟩ := exists_walk_from_cut w' {v : ℤ × ℤ | v.2 < r} hbelow
            (by simp only [Set.mem_setOf_eq, not_lt]; exact (mem_band.mp hq).2.1)
            (fun a b hab ha hb => by
              have hk := adj_abs_dy_le hab
              rw [abs_le] at hk
              simp only [Set.mem_setOf_eq, not_lt] at ha hb
              omega)
            hwr (mem_band.mp hp).1 hp2
          exact ih p q hp hq w'' (by omega)
        · -- escape above: `p` is THE row-`r'` cell; excise down to the re-entry
          have hwr' : IsWalkRow S r' := by
            rcases hr' with h | h
            · exact h
            · exact absurd (h x hxS) (by omega)
          have hp2 : p.2 = r' := by
            have hk := adj_abs_dy_le hadj.2.2
            rw [abs_le] at hk
            have := (mem_band.mp hp).2.2
            omega
          obtain ⟨w'', hw''⟩ := exists_walk_from_cut w' {v : ℤ × ℤ | r' < v.2} habove
            (by simp only [Set.mem_setOf_eq, not_lt]; exact (mem_band.mp hq).2.2)
            (fun a b hab ha hb => by
              have hk := adj_abs_dy_le hab
              rw [abs_le] at hk
              simp only [Set.mem_setOf_eq, not_lt] at ha hb
              omega)
            hwr' (mem_band.mp hp).1 hp2
          exact ih p q hp hq w'' (by omega)

/-- **Cut.** Restricting an `L`-connected `S` to the row band `[r, r']`
preserves `L`-connectivity, provided each cut line is either a walk row of `S`
or a boundary. -/
theorem connected_band {L : RowLocal} {S : Finset (ℤ × ℤ)} (hS : Connected L S)
    {r r' : ℤ}
    (hr : IsWalkRow S r ∨ ∀ p ∈ S, r ≤ p.2)
    (hr' : IsWalkRow S r' ∨ ∀ p ∈ S, p.2 ≤ r') :
    Connected L (band S r r') := by
  rw [connected_iff_reachable] at hS ⊢
  intro p hp q hq
  obtain ⟨w⟩ := hS p (mem_band.mp hp).1 q (mem_band.mp hq).1
  exact reachable_seg_aux hr hr' w.length p q hp hq w le_rfl

/-- The band is all of `S` when it brackets every row. -/
lemma band_eq_self {S : Finset (ℤ × ℤ)} {a b : ℤ}
    (h : ∀ p ∈ S, a ≤ p.2 ∧ p.2 ≤ b) : band S a b = S :=
  Finset.filter_true_of_mem h

/-- **Erase-top** (consumed by peeling case 1). If every cell of `S` sits in row
`≤ t`, rows `t` and `t - 1` are both walk rows, and `w` is the unique row-`t`
cell, then removing `w` keeps `S` `L`-connected. -/
theorem connected_erase_top {L : RowLocal} {S : Finset (ℤ × ℤ)} {t : ℤ} {w : ℤ × ℤ}
    (hS : Connected L S) (htop : ∀ p ∈ S, p.2 ≤ t)
    (hwt : IsWalkRow S t) (hwt' : IsWalkRow S (t - 1))
    (hwS : w ∈ S) (hw2 : w.2 = t) :
    Connected L (S.erase w) := by
  obtain ⟨m, hmS, hm⟩ := S.exists_min_image Prod.snd ⟨w, hwS⟩
  have hseg : band S m.2 (t - 1) = S.erase w := by
    ext c
    rw [mem_band, Finset.mem_erase]
    constructor
    · rintro ⟨hcS, -, hct⟩
      refine ⟨fun hcw => ?_, hcS⟩
      subst hcw
      omega
    · rintro ⟨hcw, hcS⟩
      refine ⟨hcS, hm c hcS, ?_⟩
      by_contra hct
      push Not at hct
      have hc2 : c.2 = t := by
        have := htop c hcS
        omega
      exact hcw (hwt.eq_of_mem hcS hc2 hwS hw2)
  rw [← hseg]
  exact connected_band hS (Or.inr hm) (Or.inl hwt')

end Polyplets.Universal
