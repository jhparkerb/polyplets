/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Graph

/-!
# Separation: walk rows glue and cut king-connected sets

The structural engine of the peeling recursion (DESIGN.md). A *walk row* is a
row holding exactly one cell of `S`; `seg S a b` is the band of cells with rows
in `[a, b]`.

* **Glue** (`kingConnected_union`): a union of two king-connected pieces
  sharing a cell is king-connected — routes every pair through the shared
  cell. Used to assemble a peeled animal back from its parts.
* **Cut** (`kingConnected_seg`): restricting a king-connected `S` to
  `seg S r r'` preserves king-connectivity, provided each cut line is either a
  walk row of `S` or a boundary (no cells of `S` beyond it). Proof is walk
  surgery in `kingGraph S` by strong induction on walk length: a walk step
  escaping the band leaves from THE unique walk-row cell on the cut line, and
  the rest of the walk must re-enter through a boundary dart
  (`Walk.exists_boundary_dart`) landing on that same cell, so the whole
  excursion is excised with `Walk.dropUntil`.
* **Erase-top** (`kingConnected_erase_top`): the corollary peeling case 1
  consumes — when the top row and the row under it are both walk rows,
  removing the unique top cell preserves king-connectivity.
-/

namespace Polyplets

/-- The row band `[a, b]` of `S`: the cells whose row lies in `[a, b]`. -/
def seg (S : Finset (ℤ × ℤ)) (a b : ℤ) : Finset (ℤ × ℤ) :=
  S.filter fun c => a ≤ c.2 ∧ c.2 ≤ b

/-- Row `r` is a *walk row* of `S`: it holds exactly one cell. -/
def IsWalkRow (S : Finset (ℤ × ℤ)) (r : ℤ) : Prop :=
  (S.filter fun c => c.2 = r).card = 1

lemma mem_seg {S : Finset (ℤ × ℤ)} {a b : ℤ} {c : ℤ × ℤ} :
    c ∈ seg S a b ↔ c ∈ S ∧ a ≤ c.2 ∧ c.2 ≤ b := Finset.mem_filter

/-- Two cells of `S` on a walk row coincide. -/
lemma IsWalkRow.eq_of_mem {S : Finset (ℤ × ℤ)} {r : ℤ} (h : IsWalkRow S r)
    {a b : ℤ × ℤ} (ha : a ∈ S) (har : a.2 = r) (hb : b ∈ S) (hbr : b.2 = r) :
    a = b :=
  Finset.card_le_one.mp (le_of_eq h)
    a (Finset.mem_filter.mpr ⟨ha, har⟩) b (Finset.mem_filter.mpr ⟨hb, hbr⟩)

/-- **Monotonicity.** A king path inside `A` is a king path inside any superset
`S`: the step relation only mentions membership. -/
lemma kingPath_mono {A S : Finset (ℤ × ℤ)} (hAS : A ⊆ S) {p q : ℤ × ℤ}
    (h : Relation.ReflTransGen (fun a b => a ∈ A ∧ b ∈ A ∧ kingAdj a b) p q) :
    Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q :=
  Relation.ReflTransGen.mono (fun _ _ hab => ⟨hAS hab.1, hAS hab.2.1, hab.2.2⟩) h

/-- **Glue.** A union of two king-connected sets sharing a cell is
king-connected: route any pair through the shared cell, lifting each piece's
paths into the union by monotonicity. No walk-row hypothesis needed. -/
theorem kingConnected_union {S A B : Finset (ℤ × ℤ)} (hS : S = A ∪ B)
    (hA : KingConnected A) (hB : KingConnected B) (hAB : (A ∩ B).Nonempty) :
    KingConnected S := by
  subst hS
  obtain ⟨x, hx⟩ := hAB
  rw [Finset.mem_inter] at hx
  have to_x : ∀ c ∈ A ∪ B,
      Relation.ReflTransGen
        (fun a b => a ∈ A ∪ B ∧ b ∈ A ∪ B ∧ kingAdj a b) c x := by
    intro c hc
    rcases Finset.mem_union.mp hc with h | h
    · exact kingPath_mono Finset.subset_union_left (hA c h x hx.1)
    · exact kingPath_mono Finset.subset_union_right (hB c h x hx.2)
  have from_x : ∀ c ∈ A ∪ B,
      Relation.ReflTransGen
        (fun a b => a ∈ A ∪ B ∧ b ∈ A ∪ B ∧ kingAdj a b) x c := by
    intro c hc
    rcases Finset.mem_union.mp hc with h | h
    · exact kingPath_mono Finset.subset_union_left (hA x hx.1 c h)
    · exact kingPath_mono Finset.subset_union_right (hB x hx.2 c h)
  intro p hp q hq
  exact (to_x p hp).trans (from_x q hq)

/-- Walk-surgery core of the cut theorem, by strong induction on walk length
(phrased as induction on an upper bound `N`). Given a `kingGraph S`-walk
between two cells of the band, the band endpoints are reachable inside
`kingGraph (seg S r r')`: a step escaping the band leaves from THE unique
walk-row cell on the crossed cut line (the boundary alternative contradicts
the escapee's existence), and `Walk.exists_boundary_dart` finds the re-entry
dart of the remaining walk, whose head is on the cut row, hence IS that same
unique cell — so `Walk.dropUntil` excises the whole excursion, strictly
shortening the walk. -/
private lemma reachable_seg_aux {S : Finset (ℤ × ℤ)} {r r' : ℤ}
    (hr : IsWalkRow S r ∨ ∀ p ∈ S, r ≤ p.2)
    (hr' : IsWalkRow S r' ∨ ∀ p ∈ S, p.2 ≤ r') :
    ∀ N (p q : ℤ × ℤ), p ∈ seg S r r' → q ∈ seg S r r' →
      ∀ w : (kingGraph S).Walk p q, w.length ≤ N →
      (kingGraph (seg S r r')).Reachable p q := by
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
      by_cases hx : x ∈ seg S r r'
      · -- step stays in the band: prepend it to the IH's reachability
        have hstep : (kingGraph (seg S r r')).Adj p x :=
          kingGraph_adj.mpr ⟨hp, hx, hadj.2.2⟩
        exact hstep.reachable.trans (ih x q hx hq w' hlen)
      · -- step escapes the band, above or below
        have hx2 : x.2 < r ∨ r' < x.2 := by
          by_contra hcon
          push Not at hcon
          exact hx (mem_seg.mpr ⟨hxS, hcon.1, hcon.2⟩)
        rcases hx2 with hbelow | habove
        · -- escape below: p is THE row-r cell; excise down to the re-entry
          have hwr : IsWalkRow S r := by
            rcases hr with h | h
            · exact h
            · exact absurd (h x hxS) (by omega)
          have hp2 : p.2 = r := by
            have hk := hadj.2.2.2.2
            rw [abs_le] at hk
            have := (mem_seg.mp hp).2.1
            omega
          obtain ⟨d, hd, hdf, hds⟩ :=
            w'.exists_boundary_dart {v : ℤ × ℤ | v.2 < r} hbelow
              (by
                simp only [Set.mem_setOf_eq, not_lt]
                exact (mem_seg.mp hq).2.1)
          have hdadj : (kingGraph S).Adj d.fst d.snd := d.adj
          have hds2 : d.snd.2 = r := by
            have hk := hdadj.2.2.2.2
            rw [abs_le] at hk
            simp only [Set.mem_setOf_eq] at hdf
            simp only [Set.mem_setOf_eq, not_lt] at hds
            omega
          have hdp : d.snd = p :=
            hwr.eq_of_mem hdadj.2.1 hds2 (mem_seg.mp hp).1 hp2
          have hpsup : p ∈ w'.support :=
            hdp ▸ w'.dart_snd_mem_support_of_mem_darts hd
          refine ih p q hp hq (w'.dropUntil p hpsup) ?_
          calc (w'.dropUntil p hpsup).length
              ≤ w'.length := by rw [SimpleGraph.Walk.length_dropUntil]; omega
            _ ≤ N := hlen
        · -- escape above: p is THE row-r' cell; excise down to the re-entry
          have hwr' : IsWalkRow S r' := by
            rcases hr' with h | h
            · exact h
            · exact absurd (h x hxS) (by omega)
          have hp2 : p.2 = r' := by
            have hk := hadj.2.2.2.2
            rw [abs_le] at hk
            have := (mem_seg.mp hp).2.2
            omega
          obtain ⟨d, hd, hdf, hds⟩ :=
            w'.exists_boundary_dart {v : ℤ × ℤ | r' < v.2} habove
              (by
                simp only [Set.mem_setOf_eq, not_lt]
                exact (mem_seg.mp hq).2.2)
          have hdadj : (kingGraph S).Adj d.fst d.snd := d.adj
          have hds2 : d.snd.2 = r' := by
            have hk := hdadj.2.2.2.2
            rw [abs_le] at hk
            simp only [Set.mem_setOf_eq] at hdf
            simp only [Set.mem_setOf_eq, not_lt] at hds
            omega
          have hdp : d.snd = p :=
            hwr'.eq_of_mem hdadj.2.1 hds2 (mem_seg.mp hp).1 hp2
          have hpsup : p ∈ w'.support :=
            hdp ▸ w'.dart_snd_mem_support_of_mem_darts hd
          refine ih p q hp hq (w'.dropUntil p hpsup) ?_
          calc (w'.dropUntil p hpsup).length
              ≤ w'.length := by rw [SimpleGraph.Walk.length_dropUntil]; omega
            _ ≤ N := hlen

/-- **Cut.** Restricting a king-connected `S` to the row band `[r, r']`
preserves king-connectivity, provided each cut line is either a walk row of
`S` or a boundary (no cells of `S` beyond it). (No `r ≤ r'` hypothesis is
needed: an empty band is vacuously king-connected.) -/
theorem kingConnected_seg {S : Finset (ℤ × ℤ)} (hS : KingConnected S)
    {r r' : ℤ}
    (hr : IsWalkRow S r ∨ ∀ p ∈ S, r ≤ p.2)
    (hr' : IsWalkRow S r' ∨ ∀ p ∈ S, p.2 ≤ r') :
    KingConnected (seg S r r') := by
  rw [kingConnected_iff_reachable] at hS ⊢
  intro p hp q hq
  obtain ⟨w⟩ := hS p (mem_seg.mp hp).1 q (mem_seg.mp hq).1
  exact reachable_seg_aux hr hr' w.length p q hp hq w le_rfl

/-- The band is all of `S` when it brackets every row. -/
lemma seg_eq_self {S : Finset (ℤ × ℤ)} {a b : ℤ}
    (h : ∀ p ∈ S, a ≤ p.2 ∧ p.2 ≤ b) : seg S a b = S :=
  Finset.filter_true_of_mem h

/-- **Erase-top** (consumed by peeling case 1). If every cell of `S` sits in
row `≤ t`, rows `t` and `t - 1` are both walk rows, and `w` is the unique
row-`t` cell, then removing `w` keeps `S` king-connected: `S.erase w` is
exactly the band from the minimum row up to `t - 1`, whose cut lines qualify
for `kingConnected_seg` (boundary below, walk row above). -/
theorem kingConnected_erase_top {S : Finset (ℤ × ℤ)} {t : ℤ} {w : ℤ × ℤ}
    (hS : KingConnected S) (htop : ∀ p ∈ S, p.2 ≤ t)
    (hwt : IsWalkRow S t) (hwt' : IsWalkRow S (t - 1))
    (hwS : w ∈ S) (hw2 : w.2 = t) :
    KingConnected (S.erase w) := by
  obtain ⟨m, hmS, hm⟩ := S.exists_min_image Prod.snd ⟨w, hwS⟩
  have hseg : seg S m.2 (t - 1) = S.erase w := by
    ext c
    rw [mem_seg, Finset.mem_erase]
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
  exact kingConnected_seg hS (Or.inr hm) (Or.inl hwt')

end Polyplets
