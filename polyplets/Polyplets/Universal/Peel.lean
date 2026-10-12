/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Polyplets.Universal.Weights

/-!
# Peeling: the two top-row identities, for every row-local lattice

The two counting identities, proved by explicit bijections, over an arbitrary
row-local lattice `L`:

* `d_rec` : for `H ≥ k + 2`,
  `d L k H = b * d L k (H-1) + ∑_{j=1..k} ∑_{ℓ=1..j} V L ℓ j * d L (k-j) (H-1-ℓ)`;
* `T_of_d` : for `H ≥ k + 1`,
  `T L (H+k) H = d L k H + ∑_{j=1..k} ∑_{ℓ=1..j} Vt L ℓ j * d L (k-j) (H-ℓ)`,

where `b = L.D.card` is the drift count. Both follow from a disjoint split on
the row profile near the top and three peeling bijections:

* **Class A** (walk top and walk second-top row): erasing the unique top cell
  and anchoring is a bijection onto `L.D × walkTop L k (H-1)`; the extra datum is
  the x-offset of the top cell over the second-top cell, which is an up-offset
  of `L` (`card_walkWalk`).
* **Classes B and C** are one bijection, `peelCluster cap H` with `glueCluster`, for a
  cluster whose top row `H - 1 - cap` has `cap` walk rows above it
  (`card_cluster`): peeling the maximal cluster `[b, H-1-cap]` together with the
  walk cell directly below (row `b-1`) and the `cap` walk cells above is a
  bijection onto `Σ (j,ℓ), configs L cap ℓ j × walkTop L (k-j) (H-cap-ℓ)`. Class B
  (walk top, multi second-top row) is `cap = 1`, onto the `V`-configurations
  (`card_walkCluster`); class C (multi top row, for `T_of_d`) is `cap = 0`,
  the cluster reaching the top edge, onto the `Vᵗ`-configurations
  (`card_clusterTop`).

Both share one x-renormalization pattern: the peeled configuration is
based at its bottom walk cell (making it x-shift-invariant), the remainder is
anchored by `anchorX`, and gluing shifts the configuration onto the
remainder's unique top cell. Membership is always matched against the
propositional characterizations `mem_walkTop` and `mem_configs`.

## The verbatim wager, settled

This file is `Peel.lean` transcribed with `kingAdj ↦ Adj L` and
`KingConnected ↦ Connected L`. Every proof carries over unchanged. The drift count
enters at exactly **three** places, all inside class A:

* `peelWalk_mem_and_glue`: the recorded offset lies in `L.D` — king
  `|Δx| ≤ 1` becomes `adj_up_mem` (the top cell is one row above the second-top
  cell, so their x-displacement IS an up-offset, by definition of `Adj`);
* `glueWalk_mem_and_peel`: conversely every `δ ∈ L.D` re-attaches legally
  (`adj_of_up`);
* `card_walkWalk`: the target is `L.D ×ˢ walkTop L k (H-1)`, of cardinality
  `L.b * d L k (H-1)` — the king `3` is `L.D.card`, nothing else.

Classes B and C mention adjacency only through connectivity lemmas
(`connected_band`, `connected_union`, `connected_translate`), which are lattice-agnostic. No
proof needed the reach `L.reach`, the shape of `D`, or any arithmetic of `b`.
-/

namespace Polyplets.Universal

variable {L : RowLocal}

/-! ## Translation toolkit, in the `(a, b)` coordinates the bijections use

Everything here is `translate` of `Universal/Defs.lean` with the vector split
into its two coordinates, which is how the peel and glue maps are written. -/

/-- Translate a cell by `(a, b)`. -/
abbrev shiftCell (a b : ℤ) (c : ℤ × ℤ) : ℤ × ℤ := c + (a, b)

/-- Translate every cell of `S` by `(a, b)`. -/
abbrev shift (a b : ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := translate (a, b) S

lemma mem_shift {a b : ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} :
    c ∈ shift a b S ↔ (c.1 - a, c.2 - b) ∈ S :=
  mem_translate

lemma shift_mem {a b : ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} (hc : c ∈ S) :
    shiftCell a b c ∈ shift a b S :=
  translate_mem hc

lemma shift_shift (a b a' b' : ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (shift a' b' S) = shift (a + a') (b + b') S := by
  rw [shift, shift, translate_translate, shift, Prod.mk_add_mk, add_comm a' a, add_comm b' b]

@[simp] lemma shift_zero (S : Finset (ℤ × ℤ)) : shift 0 0 S = S := translate_zero S

lemma card_shift (a b : ℤ) (S : Finset (ℤ × ℤ)) : (shift a b S).card = S.card :=
  card_translate _ S

lemma shift_union (a b : ℤ) (A B : Finset (ℤ × ℤ)) :
    shift a b (A ∪ B) = shift a b A ∪ shift a b B :=
  translate_union _ A B

lemma shift_insert (a b : ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (insert c S) = insert (shiftCell a b c) (shift a b S) :=
  translate_insert _ c S

lemma shift_erase (a b : ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (S.erase c) = (shift a b S).erase (shiftCell a b c) :=
  translate_erase _ c S

lemma rowSize_shift (a b : ℤ) (S : Finset (ℤ × ℤ)) (y : ℤ) :
    rowSize (shift a b S) y = rowSize S (y - b) := by
  rw [rowSize, rowSize]
  have h : (shift a b S).filter (fun c => c.2 = y)
      = shift a b (S.filter fun c => c.2 = y - b) := by
    ext c
    simp only [Finset.mem_filter, mem_shift]
    constructor
    · rintro ⟨h1, h2⟩
      exact ⟨h1, by omega⟩
    · rintro ⟨h1, h2⟩
      exact ⟨h1, by omega⟩
  rw [h, card_shift]

lemma connected_shift (a b : ℤ) {S : Finset (ℤ × ℤ)} (h : Connected L S) :
    Connected L (shift a b S) :=
  connected_translate (a, b) h

lemma band_shift (a b r r' : ℤ) (S : Finset (ℤ × ℤ)) :
    band (shift a b S) r r' = shift a b (band S (r - b) (r' - b)) := by
  ext c
  simp only [mem_band, mem_shift]
  constructor
  · rintro ⟨h1, h2, h3⟩
    exact ⟨h1, by omega, by omega⟩
  · rintro ⟨h1, h2, h3⟩
    exact ⟨h1, by omega, by omega⟩

/-! ## The x-renormalization `anchorX` -/

/-- The least x-coordinate of a cell of `S` (junk value `0` on the empty set). -/
noncomputable def minX (S : Finset (ℤ × ℤ)) : ℤ :=
  WithTop.untopD 0 (S.image Prod.fst).min

lemma minX_le {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} (hc : c ∈ S) : minX S ≤ c.1 := by
  have hne : (S.image Prod.fst).Nonempty := ⟨c.1, Finset.mem_image_of_mem _ hc⟩
  rw [minX, ← Finset.coe_min' hne, WithTop.untopD_coe]
  exact Finset.min'_le _ _ (Finset.mem_image_of_mem _ hc)

lemma exists_minX {S : Finset (ℤ × ℤ)} (h : S.Nonempty) : ∃ c ∈ S, c.1 = minX S := by
  obtain ⟨c, hc⟩ := h
  have hne : (S.image Prod.fst).Nonempty := ⟨c.1, Finset.mem_image_of_mem _ hc⟩
  have hval : minX S = (S.image Prod.fst).min' hne := by
    rw [minX, ← Finset.coe_min' hne, WithTop.untopD_coe]
  have hmem : minX S ∈ S.image Prod.fst := by
    rw [hval]
    exact Finset.min'_mem _ hne
  obtain ⟨d, hd, hd1⟩ := Finset.mem_image.mp hmem
  exact ⟨d, hd, hd1⟩

lemma minX_shift (a b : ℤ) {S : Finset (ℤ × ℤ)} (h : S.Nonempty) :
    minX (shift a b S) = minX S + a := by
  obtain ⟨c, hcS, hc1⟩ := exists_minX h
  obtain ⟨d, hdS, hd1⟩ :=
    exists_minX (show (shift a b S).Nonempty from h.image (shiftCell a b))
  have h1 : minX (shift a b S) ≤ c.1 + a := by
    have hle := minX_le (shift_mem hcS (a := a) (b := b))
    simpa [shiftCell] using hle
  have h2 : minX S ≤ d.1 - a := by
    have hpre : (d.1 - a, d.2 - b) ∈ S := mem_shift.mp hdS
    exact minX_le hpre
  omega

lemma minX_eq_zero {S : Finset (ℤ × ℤ)} (h0 : ∀ c ∈ S, 0 ≤ c.1)
    (he : ∃ c ∈ S, c.1 = 0) : minX S = 0 := by
  obtain ⟨c, hcS, hc1⟩ := he
  have h1 := minX_le hcS
  obtain ⟨d, hdS, hd1⟩ := exists_minX ⟨c, hcS⟩
  have h2 := h0 d hdS
  omega

/-- Re-anchor `S` in x so its least x-coordinate becomes `0` (rows untouched). -/
noncomputable def anchorX (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  shift (-minX S) 0 S

lemma anchorX_eq_self {S : Finset (ℤ × ℤ)} (h0 : ∀ c ∈ S, 0 ≤ c.1)
    (he : ∃ c ∈ S, c.1 = 0) : anchorX S = S := by
  rw [anchorX, minX_eq_zero h0 he, neg_zero, shift_zero]

/-- Shift invariance: anchoring forgets any prior x-translation. The
workhorse of all three round trips. -/
lemma anchorX_shift (a : ℤ) {S : Finset (ℤ × ℤ)} (h : S.Nonempty) :
    anchorX (shift a 0 S) = anchorX S := by
  rw [anchorX, minX_shift a 0 h, shift_shift]
  have he : -(minX S + a) + a = -minX S := by ring
  rw [he, add_zero, anchorX]

@[simp] lemma card_anchorX (S : Finset (ℤ × ℤ)) : (anchorX S).card = S.card := card_shift _ _ _

lemma connected_anchorX {S : Finset (ℤ × ℤ)} (h : Connected L S) :
    Connected L (anchorX S) := connected_shift _ _ h

@[simp] lemma rowSize_anchorX (S : Finset (ℤ × ℤ)) (y : ℤ) :
    rowSize (anchorX S) y = rowSize S y := by
  rw [anchorX, rowSize_shift, sub_zero]

lemma anchorX_x_nonneg {S : Finset (ℤ × ℤ)} : ∀ c ∈ anchorX S, 0 ≤ c.1 := by
  intro c hc
  rw [anchorX, mem_shift] at hc
  have h2 : minX S ≤ c.1 - -minX S := minX_le hc
  omega

lemma anchorX_exists_x_zero {S : Finset (ℤ × ℤ)} (h : S.Nonempty) :
    ∃ c ∈ anchorX S, c.1 = 0 := by
  obtain ⟨c, hcS, hc1⟩ := exists_minX h
  refine ⟨shiftCell (-minX S) 0 c, shift_mem hcS, ?_⟩
  change c.1 + -minX S = 0
  omega

lemma forall_row_anchorX {S : Finset (ℤ × ℤ)} {P : ℤ → Prop} (h : ∀ c ∈ S, P c.2) :
    ∀ c ∈ anchorX S, P c.2 := by
  intro c hc
  rw [anchorX, mem_shift] at hc
  have hP := h _ hc
  simpa using hP

lemma exists_row_anchorX {S : Finset (ℤ × ℤ)} {y : ℤ} (h : ∃ c ∈ S, c.2 = y) :
    ∃ c ∈ anchorX S, c.2 = y := by
  obtain ⟨c, hcS, hc2⟩ := h
  refine ⟨shiftCell (-minX S) 0 c, shift_mem hcS, ?_⟩
  change c.2 + 0 = y
  omega

/-- Canonicality of a anchored piece: everything except the x-anchoring is
inherited, and `anchorX` provides the anchoring. -/
lemma isAnimal_anchorX {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hcard : S.card = n) (hconn : Connected L S)
    (hy0 : ∀ c ∈ S, 0 ≤ c.2) (hy1 : ∀ c ∈ S, c.2 ≤ (H : ℤ) - 1)
    (he0 : ∃ c ∈ S, c.2 = 0) (he1 : ∃ c ∈ S, c.2 = (H : ℤ) - 1) :
    IsAnimal L n H (anchorX S) := by
  have hne : S.Nonempty := by
    obtain ⟨c, hc, -⟩ := he0
    exact ⟨c, hc⟩
  exact ⟨by rw [card_anchorX, hcard], connected_anchorX hconn,
    ⟨anchorX_x_nonneg, anchorX_exists_x_zero hne,
      forall_row_anchorX (P := fun t => 0 ≤ t) hy0, exists_row_anchorX he0⟩,
    forall_row_anchorX (P := fun t => t ≤ (H : ℤ) - 1) hy1, exists_row_anchorX he1⟩

/-! ## The unique cell of a walk row -/

/-- The cell of `S` in row `y` with least x (junk x-value `0` if the row is
empty). On a walk row this is THE row cell; its second coordinate is `y` by
definition. -/
noncomputable def rowCell (S : Finset (ℤ × ℤ)) (y : ℤ) : ℤ × ℤ :=
  (WithTop.untopD 0 ((S.filter fun c => c.2 = y).image Prod.fst).min, y)

@[simp] lemma rowCell_snd (S : Finset (ℤ × ℤ)) (y : ℤ) : (rowCell S y).2 = y := rfl

lemma filter_row_eq_singleton {S : Finset (ℤ × ℤ)} {y : ℤ} {u : ℤ × ℤ}
    (hw : IsWalkRow S y) (hu : u ∈ S) (hu2 : u.2 = y) :
    S.filter (fun c => c.2 = y) = {u} := by
  obtain ⟨a, ha⟩ := Finset.card_eq_one.mp hw
  have hmem : u ∈ S.filter (fun c => c.2 = y) := Finset.mem_filter.mpr ⟨hu, hu2⟩
  rw [ha, Finset.mem_singleton] at hmem
  rw [ha, hmem]

lemma rowCell_eq {S : Finset (ℤ × ℤ)} {y : ℤ} {u : ℤ × ℤ}
    (hw : IsWalkRow S y) (hu : u ∈ S) (hu2 : u.2 = y) :
    rowCell S y = u := by
  rw [rowCell, filter_row_eq_singleton hw hu hu2, Finset.image_singleton,
    Finset.min_singleton, WithTop.untopD_coe]
  exact Prod.ext_iff.mpr ⟨rfl, hu2.symm⟩

lemma IsWalkRow.exists_mem {S : Finset (ℤ × ℤ)} {y : ℤ} (h : IsWalkRow S y) :
    ∃ c ∈ S, c.2 = y := by
  obtain ⟨a, ha⟩ := Finset.card_eq_one.mp h
  have hmem : a ∈ S.filter fun c => c.2 = y := by
    rw [ha]
    exact Finset.mem_singleton_self a
  rw [Finset.mem_filter] at hmem
  exact ⟨a, hmem.1, hmem.2⟩

lemma rowCell_mem {S : Finset (ℤ × ℤ)} {y : ℤ} (h : IsWalkRow S y) : rowCell S y ∈ S := by
  obtain ⟨c, hc, hc2⟩ := h.exists_mem
  rw [rowCell_eq h hc hc2]
  exact hc

/-! ## Row-size and segment bookkeeping -/

lemma rowSize_band {S : Finset (ℤ × ℤ)} {a b y : ℤ} (ha : a ≤ y) (hb : y ≤ b) :
    rowSize (band S a b) y = rowSize S y := by
  rw [rowSize, rowSize]
  congr 1
  ext c
  simp only [Finset.mem_filter, mem_band]
  constructor
  · rintro ⟨⟨h1, -, -⟩, h4⟩
    exact ⟨h1, h4⟩
  · rintro ⟨h1, h4⟩
    exact ⟨⟨h1, by omega, by omega⟩, h4⟩

/-- The cell count of a row band is the sum of its row sizes. -/
lemma card_seg_sum (S : Finset (ℤ × ℤ)) (a b : ℤ) :
    (band S a b).card = ∑ y ∈ Finset.Icc a b, rowSize S y := by
  rw [Finset.card_eq_sum_card_fiberwise (f := Prod.snd) (t := Finset.Icc a b) ?_]
  · refine Finset.sum_congr rfl fun y hy => ?_
    rw [Finset.mem_Icc] at hy
    rw [← rowSize_band hy.1 hy.2, rowSize]
  · intro c hc
    rw [Finset.mem_coe, mem_band] at hc
    rw [Finset.mem_coe, Finset.mem_Icc]
    exact ⟨hc.2.1, hc.2.2⟩

/-- Split an integer-interval sum at `b`. -/
lemma sum_Icc_split (f : ℤ → ℕ) {a b c : ℤ} (h1 : a ≤ b + 1) (h2 : b ≤ c) :
    ∑ y ∈ Finset.Icc a c, f y
      = (∑ y ∈ Finset.Icc a b, f y) + ∑ y ∈ Finset.Icc (b + 1) c, f y := by
  rw [← Finset.sum_union ?_]
  · congr 1
    ext y
    simp only [Finset.mem_union, Finset.mem_Icc]
    omega
  · rw [Finset.disjoint_left]
    intro y hy hy'
    rw [Finset.mem_Icc] at hy hy'
    omega

lemma rowSize_union_right {A B : Finset (ℤ × ℤ)} {y : ℤ} (h : ∀ c ∈ A, c.2 ≠ y) :
    rowSize (A ∪ B) y = rowSize B y := by
  rw [rowSize, rowSize, Finset.filter_union,
    Finset.filter_eq_empty_iff.mpr fun c hc => h c hc, Finset.empty_union]

lemma rowSize_erase {S : Finset (ℤ × ℤ)} {w : ℤ × ℤ} {y : ℤ} (h : w.2 ≠ y) :
    rowSize (S.erase w) y = rowSize S y := by
  rw [rowSize, rowSize, Finset.filter_erase, Finset.erase_eq_of_notMem]
  rw [Finset.mem_filter]
  rintro ⟨-, h2⟩
  exact h h2

/-- A pair of king-adjacent cells is king-connected. -/
lemma connected_pair {u v : ℤ × ℤ} (h : Adj L u v) :
    Connected L {u, v} := by
  intro p hp q hq
  have hu : u ∈ ({u, v} : Finset (ℤ × ℤ)) := by simp
  have hv : v ∈ ({u, v} : Finset (ℤ × ℤ)) := by simp
  simp only [Finset.mem_insert, Finset.mem_singleton] at hp hq
  rcases hp with rfl | rfl <;> rcases hq with rfl | rfl
  · exact .refl
  · exact .single ⟨hu, hv, h⟩
  · exact .single ⟨hv, hu, adj_symm h⟩
  · exact .refl

lemma rowSize_insert_new_row {S : Finset (ℤ × ℤ)} {w : ℤ × ℤ} {y : ℤ}
    (hw : w.2 = y) (h : ∀ c ∈ S, c.2 ≠ y) : rowSize (insert w S) y = 1 := by
  rw [rowSize, Finset.filter_insert, if_pos hw,
    Finset.filter_eq_empty_iff.mpr fun c hc => h c hc]
  exact Finset.card_singleton w

lemma rowSize_insert_other {S : Finset (ℤ × ℤ)} {w : ℤ × ℤ} {y : ℤ}
    (hw : w.2 ≠ y) : rowSize (insert w S) y = rowSize S y := by
  rw [rowSize, Finset.filter_insert, if_neg hw, rowSize]

/-! ## Class A: walk top over walk second-top

Peeling the top cell of a class-A animal and anchoring is a bijection onto
`L.D × walkTop L k (H-1)`; the recorded offset `δ` (top cell x minus second-top cell
x) is x-shift-invariant, which is what makes the round trips close after
`anchorX`. This is the ONLY place in the geometric port where the lattice's
up-offset set is visible, and it is visible only as the index set of the
bijection — the king file's `{-1, 0, 1}` is `L.D`. -/

/-- Class-A forward map: erase the unique top cell, anchor the remainder,
and record the top cell's x-offset over the second-top cell. -/
noncomputable def peelWalk (H : ℕ) (S : Finset (ℤ × ℤ)) : ℤ × Finset (ℤ × ℤ) :=
  ((rowCell S ((H : ℤ) - 1)).1 - (rowCell S ((H : ℤ) - 2)).1,
    anchorX (S.erase (rowCell S ((H : ℤ) - 1))))

/-- Class-A backward map: re-attach a top cell at the recorded offset over the
remainder's unique top cell, then anchor. -/
noncomputable def glueWalk (H : ℕ) (x : ℤ × Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  anchorX (insert ((rowCell x.2 ((H : ℤ) - 2)).1 + x.1, (H : ℤ) - 1) x.2)

/-- Forward well-definedness and the peel-then-glue round trip for class A. -/
lemma peelWalk_mem_and_glue {k H : ℕ} (hH : k + 2 ≤ H) {S : Finset (ℤ × ℤ)}
    (hS : S ∈ walkTop L k H) (hw2 : rowSize S ((H : ℤ) - 2) = 1) :
    peelWalk H S ∈ L.D ×ˢ walkTop L k (H - 1) ∧ glueWalk H (peelWalk H S) = S := by
  obtain ⟨hc, hw1⟩ := mem_walkTop.mp hS
  have hwr1 : IsWalkRow S ((H : ℤ) - 1) := hw1
  have hwr2 : IsWalkRow S ((H : ℤ) - 2) := hw2
  set w := rowCell S ((H : ℤ) - 1) with hw_def
  set w' := rowCell S ((H : ℤ) - 2) with hw'_def
  have hwS : w ∈ S := rowCell_mem hwr1
  have hw'S : w' ∈ S := rowCell_mem hwr2
  have hwy : w.2 = (H : ℤ) - 1 := rfl
  have hw'y : w'.2 = (H : ℤ) - 2 := rfl
  -- the top cell is king-adjacent to the second-top cell
  have hadj : Adj L w w' := by
    obtain ⟨z, hzS, hzy⟩ := hc.anchored.y_zero
    have hwz : w ≠ z := by
      intro heq
      rw [← heq] at hzy
      rw [hwy] at hzy
      omega
    rcases Relation.ReflTransGen.cases_head (hc.conn w hwS z hzS) with heq | ⟨x, hstep, -⟩
    · exact absurd heq hwz
    · obtain ⟨-, hxS, hadjwx⟩ := hstep
      have hxy : x.2 = (H : ℤ) - 2 := by
        have h1 := adj_abs_dy_le hadjwx
        rw [abs_le] at h1
        have h2 := hc.y_le x hxS
        rcases eq_or_lt_of_le h2 with heq2 | hlt
        · have hxw : x = w := hwr1.eq_of_mem hxS heq2 hwS hwy
          exact absurd hxw.symm hadjwx.1
        · rw [hwy] at h1
          omega
      have hxw' : x = w' := hwr2.eq_of_mem hxS hxy hw'S hw'y
      rw [← hxw']
      exact hadjwx
  -- the recorded offset is an up-offset of the lattice
  have hδ : w.1 - w'.1 ∈ L.D :=
    adj_up_mem (adj_symm hadj) (by rw [hwy, hw'y]; ring)
  -- the erased remainder
  set S' := S.erase w with hS'_def
  have hS'card : S'.card = (H - 1) + k := by
    rw [hS'_def, Finset.card_erase_of_mem hwS, hc.card]
    omega
  have hS'conn : Connected L S' := by
    rw [hS'_def]
    refine connected_erase_top hc.conn hc.y_le hwr1 ?_ hwS hwy
    have he : (H : ℤ) - 1 - 1 = (H : ℤ) - 2 := by ring
    rw [he]
    exact hwr2
  have hS'rows : ∀ c ∈ S', c.2 ≤ (H : ℤ) - 2 := by
    intro c hcm
    obtain ⟨hcw, hcS⟩ := Finset.mem_erase.mp hcm
    have h1 := hc.y_le c hcS
    rcases eq_or_lt_of_le h1 with heq | hlt
    · exact absurd (hwr1.eq_of_mem hcS heq hwS hwy) hcw
    · omega
  have hS'y0 : ∀ c ∈ S', 0 ≤ c.2 := fun c hcm =>
    hc.anchored.y_nonneg c (Finset.mem_erase.mp hcm).2
  have hw'S' : w' ∈ S' := by
    rw [hS'_def]
    refine Finset.mem_erase.mpr ⟨?_, hw'S⟩
    intro heq
    have h := hw'y
    rw [heq, hwy] at h
    omega
  have hS'e0 : ∃ c ∈ S', c.2 = 0 := by
    obtain ⟨z, hzS, hzy⟩ := hc.anchored.y_zero
    refine ⟨z, ?_, hzy⟩
    rw [hS'_def]
    refine Finset.mem_erase.mpr ⟨?_, hzS⟩
    intro heq
    rw [heq, hwy] at hzy
    omega
  have hS'e1 : ∃ c ∈ S', c.2 = (H : ℤ) - 2 := ⟨w', hw'S', hw'y⟩
  have hS'w : rowSize S' ((H : ℤ) - 2) = 1 := by
    rw [hS'_def, rowSize_erase (by rw [hwy]; omega)]
    exact hw2
  have hS'ne : S'.Nonempty := ⟨w', hw'S'⟩
  -- forward membership
  have hR : anchorX S' ∈ walkTop L k (H - 1) := by
    rw [mem_walkTop]
    refine ⟨isAnimal_anchorX hS'card hS'conn hS'y0 (fun c hcm => ?_) hS'e0 ?_, ?_⟩
    · have := hS'rows c hcm
      omega
    · obtain ⟨c, hcm, hcy⟩ := hS'e1
      exact ⟨c, hcm, by omega⟩
    · rw [rowSize_anchorX]
      have he2 : ((H - 1 : ℕ) : ℤ) - 1 = (H : ℤ) - 2 := by omega
      rw [he2]
      exact hS'w
  constructor
  · simp only [peelWalk, ← hw_def, ← hw'_def, ← hS'_def]
    rw [Finset.mem_product]
    exact ⟨hδ, hR⟩
  -- round trip: glue the peel back
  · have hwalkR : IsWalkRow (anchorX S') ((H : ℤ) - 2) := by
      rw [isWalkRow_iff_rowSize, rowSize_anchorX]
      exact hS'w
    have hw'shift : shiftCell (-minX S') 0 w' ∈ anchorX S' := by
      rw [show anchorX S' = shift (-minX S') 0 S' from rfl]
      exact shift_mem hw'S'
    have hu : rowCell (anchorX S') ((H : ℤ) - 2) = shiftCell (-minX S') 0 w' := by
      refine rowCell_eq hwalkR hw'shift ?_
      change w'.2 + 0 = (H : ℤ) - 2
      omega
    have hcell : ((shiftCell (-minX S') 0 w').1 + (w.1 - w'.1), (H : ℤ) - 1)
        = shiftCell (-minX S') 0 w := by
      change (w'.1 + -minX S' + (w.1 - w'.1), (H : ℤ) - 1) = (w.1 + -minX S', w.2 + 0)
      rw [Prod.mk.injEq, hwy]
      constructor
      · ring
      · ring
    calc glueWalk H (peelWalk H S)
        = anchorX (insert ((rowCell (anchorX S') ((H : ℤ) - 2)).1 + (w.1 - w'.1),
            (H : ℤ) - 1) (anchorX S')) := by
          simp only [glueWalk, peelWalk, ← hw_def, ← hw'_def, ← hS'_def]
      _ = anchorX (shift (-minX S') 0 (insert w S')) := by
          rw [hu, hcell, show anchorX S' = shift (-minX S') 0 S' from rfl, ← shift_insert]
      _ = anchorX (insert w S') := anchorX_shift _ ⟨w, Finset.mem_insert_self w S'⟩
      _ = anchorX S := by rw [hS'_def, Finset.insert_erase hwS]
      _ = S := anchorX_eq_self hc.anchored.x_nonneg hc.anchored.x_zero

/-- Backward well-definedness and the glue-then-peel round trip for class A. -/
lemma glueWalk_mem_and_peel {k H : ℕ} (hH : k + 2 ≤ H) {x : ℤ × Finset (ℤ × ℤ)}
    (hx : x ∈ L.D ×ˢ walkTop L k (H - 1)) :
    (glueWalk H x ∈ walkTop L k H ∧ rowSize (glueWalk H x) ((H : ℤ) - 2) = 1) ∧
      peelWalk H (glueWalk H x) = x := by
  obtain ⟨δ, R⟩ := x
  rw [Finset.mem_product] at hx
  obtain ⟨hδm, hR⟩ := hx
  obtain ⟨hcR, hwR⟩ := mem_walkTop.mp hR
  have hwRtop : IsWalkRow R ((H : ℤ) - 2) := by
    rw [isWalkRow_iff_rowSize]
    have he : (H : ℤ) - 2 = ((H - 1 : ℕ) : ℤ) - 1 := by omega
    rw [he]
    exact hwR
  set u := rowCell R ((H : ℤ) - 2) with hu_def
  have huR : u ∈ R := rowCell_mem hwRtop
  have huy : u.2 = (H : ℤ) - 2 := rfl
  set w₀ : ℤ × ℤ := (u.1 + δ, (H : ℤ) - 1) with hw₀_def
  have hw₀y : w₀.2 = (H : ℤ) - 1 := rfl
  have hRrows : ∀ c ∈ R, 0 ≤ c.2 ∧ c.2 ≤ (H : ℤ) - 2 := by
    intro c hcm
    have h1 := hcR.anchored.y_nonneg c hcm
    have h2 := hcR.y_le c hcm
    omega
  have hw₀R : w₀ ∉ R := by
    intro hmem
    have h2 := (hRrows w₀ hmem).2
    rw [hw₀y] at h2
    omega
  set G₀ := insert w₀ R with hG₀_def
  have hG₀card : G₀.card = H + k := by
    rw [hG₀_def, Finset.card_insert_of_notMem hw₀R, hcR.card]
    omega
  -- any up-offset re-attaches legally: `w₀` sits one row above `u` at
  -- displacement `δ ∈ L.D`
  have hadj : Adj L u w₀ := by
    refine adj_of_up (by rw [hw₀y, huy]; ring) ?_
    have hxδ : w₀.1 - u.1 = δ := by
      change u.1 + δ - u.1 = δ
      ring
    rw [hxδ]
    exact hδm
  have hG₀eq : G₀ = R ∪ {u, w₀} := by
    rw [hG₀_def]
    ext c
    simp only [Finset.mem_insert, Finset.mem_union, Finset.mem_singleton]
    constructor
    · rintro (rfl | hcm)
      · exact Or.inr (Or.inr rfl)
      · exact Or.inl hcm
    · rintro (hcm | rfl | rfl)
      · exact Or.inr hcm
      · exact Or.inr huR
      · exact Or.inl rfl
  have hG₀conn : Connected L G₀ :=
    connected_union hG₀eq hcR.conn (connected_pair hadj)
      ⟨u, Finset.mem_inter.mpr ⟨huR, by simp⟩⟩
  have hG₀y0 : ∀ c ∈ G₀, 0 ≤ c.2 := by
    intro c hcm
    rcases Finset.mem_insert.mp (hG₀_def ▸ hcm) with rfl | hcm'
    · rw [hw₀y]
      omega
    · exact (hRrows c hcm').1
  have hG₀y1 : ∀ c ∈ G₀, c.2 ≤ (H : ℤ) - 1 := by
    intro c hcm
    rcases Finset.mem_insert.mp (hG₀_def ▸ hcm) with rfl | hcm'
    · rw [hw₀y]
    · have := (hRrows c hcm').2
      omega
  have hG₀e0 : ∃ c ∈ G₀, c.2 = 0 := by
    obtain ⟨z, hzR, hzy⟩ := hcR.anchored.y_zero
    exact ⟨z, by rw [hG₀_def]; exact Finset.mem_insert_of_mem hzR, hzy⟩
  have hG₀e1 : ∃ c ∈ G₀, c.2 = (H : ℤ) - 1 :=
    ⟨w₀, by rw [hG₀_def]; exact Finset.mem_insert_self _ _, hw₀y⟩
  have hG₀top : rowSize G₀ ((H : ℤ) - 1) = 1 := by
    rw [hG₀_def]
    refine rowSize_insert_new_row hw₀y fun c hcm heq => ?_
    have := (hRrows c hcm).2
    omega
  have hG₀2 : rowSize G₀ ((H : ℤ) - 2) = 1 := by
    rw [hG₀_def, rowSize_insert_other (by rw [hw₀y]; omega)]
    exact hwRtop
  have hgl : glueWalk H (δ, R) = anchorX G₀ := by
    simp only [glueWalk]
    rw [← hu_def, ← hw₀_def, ← hG₀_def]
  have hGmem : glueWalk H (δ, R) ∈ walkTop L k H := by
    rw [hgl, mem_walkTop]
    refine ⟨isAnimal_anchorX hG₀card hG₀conn hG₀y0 hG₀y1 hG₀e0 hG₀e1, ?_⟩
    rw [rowSize_anchorX]
    exact hG₀top
  have hG2' : rowSize (glueWalk H (δ, R)) ((H : ℤ) - 2) = 1 := by
    rw [hgl, rowSize_anchorX]
    exact hG₀2
  refine ⟨⟨hGmem, hG2'⟩, ?_⟩
  -- round trip: peel the glue back apart
  have hGw1 : IsWalkRow (anchorX G₀) ((H : ℤ) - 1) := by
    rw [isWalkRow_iff_rowSize, rowSize_anchorX]
    exact hG₀top
  have hGw2 : IsWalkRow (anchorX G₀) ((H : ℤ) - 2) := by
    rw [isWalkRow_iff_rowSize, rowSize_anchorX]
    exact hG₀2
  have hwG : rowCell (anchorX G₀) ((H : ℤ) - 1) = shiftCell (-minX G₀) 0 w₀ := by
    refine rowCell_eq hGw1 ?_ ?_
    · rw [show anchorX G₀ = shift (-minX G₀) 0 G₀ from rfl]
      exact shift_mem (by rw [hG₀_def]; exact Finset.mem_insert_self _ _)
    · change w₀.2 + 0 = (H : ℤ) - 1
      rw [hw₀y]
      ring
  have huG : rowCell (anchorX G₀) ((H : ℤ) - 2) = shiftCell (-minX G₀) 0 u := by
    refine rowCell_eq hGw2 ?_ ?_
    · rw [show anchorX G₀ = shift (-minX G₀) 0 G₀ from rfl]
      exact shift_mem (by rw [hG₀_def]; exact Finset.mem_insert_of_mem huR)
    · change u.2 + 0 = (H : ℤ) - 2
      rw [huy]
      ring
  have hδrec : (rowCell (anchorX G₀) ((H : ℤ) - 1)).1
      - (rowCell (anchorX G₀) ((H : ℤ) - 2)).1 = δ := by
    rw [hwG, huG]
    change w₀.1 + -minX G₀ - (u.1 + -minX G₀) = δ
    rw [show w₀.1 = u.1 + δ from rfl]
    ring
  have herase : (anchorX G₀).erase (rowCell (anchorX G₀) ((H : ℤ) - 1))
      = shift (-minX G₀) 0 R := by
    rw [hwG, show anchorX G₀ = shift (-minX G₀) 0 G₀ from rfl, ← shift_erase, hG₀_def,
      Finset.erase_insert hw₀R]
  have hRne : R.Nonempty := by
    obtain ⟨z, hzR, -⟩ := hcR.anchored.y_zero
    exact ⟨z, hzR⟩
  rw [hgl]
  simp only [peelWalk]
  rw [hδrec, herase, anchorX_shift (-minX G₀) hRne,
    anchorX_eq_self hcR.anchored.x_nonneg hcR.anchored.x_zero]

/-- **Class-A count**: walk-top animals whose second-top row is also a walk
row are `b · d L k (H-1)` — the up-offset and the anchored remainder are a
bijection. The king file's `3` is `L.D.card = L.b`. -/
lemma card_walkWalk (k H : ℕ) (hH : k + 2 ≤ H) :
    ((walkTop L k H).filter fun S => rowSize S ((H : ℤ) - 2) = 1).card
      = L.b * d L k (H - 1) := by
  have h3 : (L.D ×ˢ walkTop L k (H - 1)).card = L.b * d L k (H - 1) := by
    rw [Finset.card_product]
    rfl
  rw [← h3]
  refine Finset.card_nbij' (peelWalk H) (glueWalk H) ?_ ?_ ?_ ?_
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    rw [Finset.mem_coe]
    exact (peelWalk_mem_and_glue hH hS.1 hS.2).1
  · intro x hx
    rw [Finset.mem_coe] at hx
    rw [Finset.mem_coe, Finset.mem_filter]
    exact (glueWalk_mem_and_peel hH hx).1
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    exact (peelWalk_mem_and_glue hH hS.1 hS.2).2
  · intro x hx
    rw [Finset.mem_coe] at hx
    exact (glueWalk_mem_and_peel hH hx).2

/-! ## Cluster peeling: shared machinery for classes B and C -/

/-- The bottom row of the maximal all-multi run of rows ending at `t`: the
least `r ∈ [0, t]` such that every row of `[r, t]` holds at least two cells
(junk `0` if there is none — the callers always have `rowSize S t ≥ 2`, so
`t` itself qualifies). -/
noncomputable def clusterBottom (S : Finset (ℤ × ℤ)) (t : ℤ) : ℤ :=
  WithTop.untopD 0
    (((Finset.Icc 0 t).filter fun r => ∀ y ∈ Finset.Icc r t, 2 ≤ rowSize S y).min)

/-- The defining properties of `clusterBottom`: it lies in `[0, t]`, the rows
`[clusterBottom, t]` are all multi, it is minimal with that property, and (if
positive) the row below it is not multi. -/
lemma clusterBottom_spec {S : Finset (ℤ × ℤ)} {t : ℤ} (ht : 0 ≤ t)
    (h2 : 2 ≤ rowSize S t) :
    (0 ≤ clusterBottom S t ∧ clusterBottom S t ≤ t) ∧
    (∀ y, clusterBottom S t ≤ y → y ≤ t → 2 ≤ rowSize S y) ∧
    (∀ r, 0 ≤ r → r ≤ t → (∀ y, r ≤ y → y ≤ t → 2 ≤ rowSize S y) →
      clusterBottom S t ≤ r) ∧
    (1 ≤ clusterBottom S t → ¬ 2 ≤ rowSize S (clusterBottom S t - 1)) := by
  set F := (Finset.Icc 0 t).filter (fun r => ∀ y ∈ Finset.Icc r t, 2 ≤ rowSize S y)
    with hF
  have htF : t ∈ F := by
    rw [hF, Finset.mem_filter, Finset.mem_Icc]
    refine ⟨⟨ht, le_refl t⟩, ?_⟩
    intro y hy
    rw [Finset.mem_Icc] at hy
    have hyt : y = t := le_antisymm hy.2 hy.1
    rw [hyt]
    exact h2
  have hFne : F.Nonempty := ⟨t, htF⟩
  have hbval : clusterBottom S t = F.min' hFne := by
    rw [clusterBottom, ← hF, ← Finset.coe_min' hFne, WithTop.untopD_coe]
  have hbF : clusterBottom S t ∈ F := by
    rw [hbval]
    exact Finset.min'_mem _ _
  rw [hF, Finset.mem_filter, Finset.mem_Icc] at hbF
  obtain ⟨⟨hb0, hbt⟩, hbmulti⟩ := hbF
  have hmulti : ∀ y, clusterBottom S t ≤ y → y ≤ t → 2 ≤ rowSize S y :=
    fun y h1 h2' => hbmulti y (Finset.mem_Icc.mpr ⟨h1, h2'⟩)
  have hminle : ∀ r, 0 ≤ r → r ≤ t →
      (∀ y, r ≤ y → y ≤ t → 2 ≤ rowSize S y) → clusterBottom S t ≤ r := by
    intro r hr0 hrt hrmulti
    have hrF : r ∈ F := by
      rw [hF, Finset.mem_filter, Finset.mem_Icc]
      refine ⟨⟨hr0, hrt⟩, fun y hy => ?_⟩
      rw [Finset.mem_Icc] at hy
      exact hrmulti y hy.1 hy.2
    rw [hbval]
    exact Finset.min'_le _ _ hrF
  refine ⟨⟨hb0, hbt⟩, hmulti, hminle, ?_⟩
  intro hb1 hcon
  have hle := hminle (clusterBottom S t - 1) (by omega) (by omega) ?_
  · omega
  · intro y hy1 hy2
    rcases eq_or_lt_of_le hy1 with heq | hlt
    · rw [← heq]
      exact hcon
    · exact hmulti y (by omega) hy2

/-- The peeled-data type of classes B and C: surplus `j`, cluster rows `ℓ`,
the based configuration, and the anchored walk-top remainder. -/
abbrev PeelData : Type :=
  Σ _ : ℕ, Σ _ : ℕ, Finset (ℤ × ℤ) × Finset (ℤ × ℤ)

/-- Backward map of classes B and C: shift the configuration so its origin
lands on the remainder's unique top cell (row `t - ℓ`), union, anchor.
`t` is the cluster's top row: `H - 2` for class B, `H - 1` for class C. -/
noncomputable def glueCluster (t : ℤ) (x : PeelData) : Finset (ℤ × ℤ) :=
  anchorX (x.2.2.2 ∪
    shift (rowCell x.2.2.2 (t - (x.2.1 : ℤ))).1 (t - (x.2.1 : ℤ)) x.2.2.1)

/-- Forward map of classes B and C, for the cluster whose top row
`t = H - 1 - cap` has `cap` walk rows above it: peel the maximal cluster over
rows `[b, t]` (`b = clusterBottom`) together with the walk cell on row `b - 1`
and the `cap` walk cells above; the configuration is based at the row-`(b-1)`
walk cell, the remainder `[0, b-1]` is anchored. Class B is `cap = 1`,
class C is `cap = 0`. -/
noncomputable def peelCluster (cap H : ℕ) (S : Finset (ℤ × ℤ)) : PeelData :=
  ⟨(band S (clusterBottom S ((H : ℤ) - 1 - cap)) ((H : ℤ) - 1 - cap)).card
      - ((H : ℤ) - cap - clusterBottom S ((H : ℤ) - 1 - cap)).toNat,
   ((H : ℤ) - cap - clusterBottom S ((H : ℤ) - 1 - cap)).toNat,
   shift (-(rowCell S (clusterBottom S ((H : ℤ) - 1 - cap) - 1)).1)
       (-(clusterBottom S ((H : ℤ) - 1 - cap) - 1))
       (band S (clusterBottom S ((H : ℤ) - 1 - cap) - 1) ((H : ℤ) - 1)),
   anchorX (band S 0 (clusterBottom S ((H : ℤ) - 1 - cap) - 1))⟩

/-- The `cap` rows above row `H - 1 - cap` are walk rows: the source
condition of classes B and C besides the multi row `H - 1 - cap` itself. -/
def CapWalk (cap H : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  ∀ y ∈ Finset.Ioc ((H : ℤ) - 1 - cap) ((H : ℤ) - 1), rowSize S y = 1

noncomputable instance (cap H : ℕ) (S : Finset (ℤ × ℤ)) : Decidable (CapWalk cap H S) := by
  unfold CapWalk
  infer_instance

lemma capWalk_iff {cap H : ℕ} {S : Finset (ℤ × ℤ)} :
    CapWalk cap H S ↔ ∀ y : ℤ, (H : ℤ) - 1 - cap < y → y ≤ (H : ℤ) - 1 → rowSize S y = 1 := by
  simp only [CapWalk, Finset.mem_Ioc, and_imp]

/-- With one cap row, `CapWalk` says the top row is a walk row. -/
lemma capWalk_one_iff {H : ℕ} {S : Finset (ℤ × ℤ)} :
    CapWalk 1 H S ↔ rowSize S ((H : ℤ) - 1) = 1 := by
  rw [capWalk_iff]
  constructor
  · intro h
    exact h _ (by omega) le_rfl
  · intro h y h1 h2
    rw [show y = (H : ℤ) - 1 from by push_cast at h1; omega]
    exact h

/-- With no cap row, `CapWalk` is vacuous. -/
lemma capWalk_zero {H : ℕ} {S : Finset (ℤ × ℤ)} : CapWalk 0 H S := by
  rw [capWalk_iff]
  intro y h1 h2
  push_cast at h1
  omega

/-- The target of classes B and C: configurations with `cap` walk rows on top,
paired with walk-top remainders, indexed by `(j, ℓ)`. -/
noncomputable def target (L : RowLocal) (cap k H : ℕ) : Finset PeelData :=
  (Finset.Icc 1 k).sigma fun j => (Finset.Icc 1 j).sigma fun ℓ =>
    configs L cap ℓ j ×ˢ walkTop L (k - j) (H - cap - ℓ)

lemma anchorX_def' (S : Finset (ℤ × ℤ)) : anchorX S = shift (-minX S) 0 S := rfl

lemma band_union (A B : Finset (ℤ × ℤ)) (a b : ℤ) :
    band (A ∪ B) a b = band A a b ∪ band B a b :=
  Finset.filter_union _ _ _

lemma shiftCell_origin (a b : ℤ) : shiftCell a b ((0 : ℤ), (0 : ℤ)) = (a, b) := by
  change ((0 : ℤ) + a, (0 : ℤ) + b) = (a, b)
  rw [Prod.mk.injEq]
  constructor <;> ring

lemma shiftCell_to_origin {p : ℤ × ℤ} {b : ℤ} (hpy : p.2 = b) :
    shiftCell (-p.1) (-b) p = ((0 : ℤ), (0 : ℤ)) := by
  change (p.1 + -p.1, p.2 + -b) = ((0 : ℤ), (0 : ℤ))
  rw [Prod.mk.injEq, hpy]
  constructor <;> ring

lemma band_xShift (a r r' : ℤ) (S : Finset (ℤ × ℤ)) :
    band (shift a 0 S) r r' = shift a 0 (band S r r') := by
  rw [band_shift, sub_zero, sub_zero]

/-- The anchored bottom band `[0, b-1]` of a connected animal with a walk
row at `b - 1` is a walk-top canonical animal of height `b`. Shared by all
three peeling classes. -/
lemma anchorX_seg_mem_walkTop {k' H' : ℕ} {S : Finset (ℤ × ℤ)} {b : ℤ}
    (hconn : Connected L S) (hy0 : ∀ c ∈ S, 0 ≤ c.2)
    (hb : 1 ≤ b) (hHb : (H' : ℤ) = b)
    (hwb : rowSize S (b - 1) = 1)
    (h0occ : ∃ c ∈ S, c.2 = 0)
    (hcard : (band S 0 (b - 1)).card = H' + k') :
    anchorX (band S 0 (b - 1)) ∈ walkTop L k' H' := by
  rw [mem_walkTop]
  have hwr : IsWalkRow S (b - 1) := hwb
  have hconnQ : Connected L (band S 0 (b - 1)) :=
    connected_band hconn (Or.inr hy0) (Or.inl hwr)
  have hyQ0 : ∀ c ∈ band S 0 (b - 1), 0 ≤ c.2 := fun c hc => (mem_band.mp hc).2.1
  have hyQ1 : ∀ c ∈ band S 0 (b - 1), c.2 ≤ (H' : ℤ) - 1 := by
    intro c hc
    have := (mem_band.mp hc).2.2
    omega
  have he0 : ∃ c ∈ band S 0 (b - 1), c.2 = 0 := by
    obtain ⟨c, hcS, hc2⟩ := h0occ
    exact ⟨c, mem_band.mpr ⟨hcS, by omega, by omega⟩, hc2⟩
  have he1 : ∃ c ∈ band S 0 (b - 1), c.2 = (H' : ℤ) - 1 := by
    obtain ⟨c, hcS, hc2⟩ := hwr.exists_mem
    exact ⟨c, mem_band.mpr ⟨hcS, by omega, by omega⟩, by omega⟩
  refine ⟨isAnimal_anchorX hcard hconnQ hyQ0 hyQ1 he0 he1, ?_⟩
  rw [rowSize_anchorX, show (H' : ℤ) - 1 = b - 1 by omega, rowSize_band (by omega) le_rfl]
  exact hwb

/-- Rows that each hold one cell contribute one each to a row sum. -/
lemma sum_rowSize_walk {S : Finset (ℤ × ℤ)} {a b : ℤ}
    (h : ∀ y, a ≤ y → y ≤ b → rowSize S y = 1) :
    ∑ y ∈ Finset.Icc a b, rowSize S y = (b + 1 - a).toNat := by
  rw [Finset.sum_congr rfl fun y hy => h y (Finset.mem_Icc.mp hy).1 (Finset.mem_Icc.mp hy).2,
    Finset.sum_const, smul_eq_mul, mul_one, Int.card_Icc]

/-- Cluster bookkeeping for classes B and C, for the cluster whose top row is
`t = H - 1 - cap` with `cap` walk rows above it: bounds of `b = clusterBottom`,
the walk row below the cluster, and the cell-count identities the bijection
needs. -/
lemma cluster_facts {cap k H : ℕ} (hH : k + 1 + cap ≤ H) {S : Finset (ℤ × ℤ)}
    (hSc : IsAnimal L (H + k) H S)
    (hw : ∀ y : ℤ, (H : ℤ) - 1 - cap < y → y ≤ (H : ℤ) - 1 → rowSize S y = 1)
    (hm : ¬ rowSize S ((H : ℤ) - 1 - cap) = 1) :
    1 ≤ clusterBottom S ((H : ℤ) - 1 - cap) ∧
    clusterBottom S ((H : ℤ) - 1 - cap) ≤ (H : ℤ) - 1 - cap ∧
    (∀ y, clusterBottom S ((H : ℤ) - 1 - cap) ≤ y → y ≤ (H : ℤ) - 1 - cap →
      2 ≤ rowSize S y) ∧
    rowSize S (clusterBottom S ((H : ℤ) - 1 - cap) - 1) = 1 ∧
    ((band S 0 (clusterBottom S ((H : ℤ) - 1 - cap) - 1)).card
      + (band S (clusterBottom S ((H : ℤ) - 1 - cap)) ((H : ℤ) - 1 - cap)).card + cap
        = H + k) ∧
    (clusterBottom S ((H : ℤ) - 1 - cap)
      ≤ ((band S 0 (clusterBottom S ((H : ℤ) - 1 - cap) - 1)).card : ℤ)) ∧
    (2 * ((H : ℤ) - cap - clusterBottom S ((H : ℤ) - 1 - cap))
      ≤ ((band S (clusterBottom S ((H : ℤ) - 1 - cap)) ((H : ℤ) - 1 - cap)).card : ℤ)) ∧
    (band S (clusterBottom S ((H : ℤ) - 1 - cap) - 1) ((H : ℤ) - 1)).card
      = (band S (clusterBottom S ((H : ℤ) - 1 - cap)) ((H : ℤ) - 1 - cap)).card + 1 + cap := by
  set t : ℤ := (H : ℤ) - 1 - cap with ht_def
  have hocc : ∀ y, 0 ≤ y → y ≤ (H : ℤ) - 1 → 1 ≤ rowSize S y := fun y h0 h1 =>
    Finset.card_pos.mpr (animal_fiber_nonempty hSc h0 h1)
  have hm2 : 2 ≤ rowSize S t := by
    have := hocc t (by omega) (by omega)
    omega
  obtain ⟨⟨hb0, hbt⟩, hmulti, hminle, hwalk'⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ t by omega) hm2
  set b := clusterBottom S t with hb_def
  -- total cell count as a row sum
  have hself : band S 0 ((H : ℤ) - 1) = S :=
    band_eq_self fun p hp => ⟨hSc.anchored.y_nonneg p hp, hSc.y_le p hp⟩
  have htotal : (H : ℕ) + k = ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y := by
    rw [← card_seg_sum, hself, hSc.card]
  have hsplit1 : ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y
      = (∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y)
        + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
    have h := sum_Icc_split (rowSize S) (a := 0) (b := b - 1) (c := (H : ℤ) - 1)
      (by omega) (by omega)
    simpa using h
  have hsplit2 : ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y
      = (∑ y ∈ Finset.Icc b t, rowSize S y)
        + ∑ y ∈ Finset.Icc (t + 1) ((H : ℤ) - 1), rowSize S y :=
    sum_Icc_split (rowSize S) (by omega) (by omega)
  have hcap : ∑ y ∈ Finset.Icc (t + 1) ((H : ℤ) - 1), rowSize S y = cap := by
    rw [sum_rowSize_walk fun y h1 h2 => hw y (by omega) h2]
    omega
  have hn1sum : (band S 0 (b - 1)).card = ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y :=
    card_seg_sum S 0 (b - 1)
  have hn2sum : (band S b t).card = ∑ y ∈ Finset.Icc b t, rowSize S y := card_seg_sum S b t
  -- per-row lower bounds
  have hn1b : (b : ℤ) ≤ ((band S 0 (b - 1)).card : ℤ) := by
    have hle : (Finset.Icc (0 : ℤ) (b - 1)).card • 1
        ≤ ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hocc y hy.1 (by omega)
    rw [smul_eq_mul, mul_one, Int.card_Icc] at hle
    rw [hn1sum]
    omega
  have hn2l : 2 * ((H : ℤ) - cap - b) ≤ ((band S b t).card : ℤ) := by
    have hle : (Finset.Icc b t).card • 2 ≤ ∑ y ∈ Finset.Icc b t, rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hmulti y hy.1 hy.2
    rw [smul_eq_mul, Int.card_Icc] at hle
    rw [hn2sum]
    omega
  have hn12 : (band S 0 (b - 1)).card + (band S b t).card + cap = H + k := by
    rw [hn1sum, hn2sum]
    omega
  have hb1 : 1 ≤ b := by omega
  have hwalkb : rowSize S (b - 1) = 1 := by
    have h1 := hocc (b - 1) (by omega) (by omega)
    have h2 := hwalk' hb1
    omega
  have hPcard : (band S (b - 1) ((H : ℤ) - 1)).card = (band S b t).card + 1 + cap := by
    have hs1 : ∑ y ∈ Finset.Icc (b - 1) ((H : ℤ) - 1), rowSize S y
        = (∑ y ∈ Finset.Icc (b - 1) (b - 1), rowSize S y)
          + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
      have h := sum_Icc_split (rowSize S) (a := b - 1) (b := b - 1) (c := (H : ℤ) - 1)
        (by omega) (by omega)
      simpa using h
    rw [card_seg_sum, hs1, Finset.Icc_self, Finset.sum_singleton, hwalkb, hsplit2, hcap,
      hn2sum]
    omega
  exact ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩

/-- Forward well-definedness and the peel-then-glue round trip for classes B
and C. -/
lemma peelCluster_mem_and_glue {cap k H : ℕ} (hH : k + 1 + cap ≤ H) {S : Finset (ℤ × ℤ)}
    (hSc : IsAnimal L (H + k) H S)
    (hw : ∀ y : ℤ, (H : ℤ) - 1 - cap < y → y ≤ (H : ℤ) - 1 → rowSize S y = 1)
    (hm : ¬ rowSize S ((H : ℤ) - 1 - cap) = 1) :
    peelCluster cap H S ∈ target L cap k H ∧
      glueCluster ((H : ℤ) - 1 - cap) (peelCluster cap H S) = S := by
  obtain ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩ := cluster_facts hH hSc hw hm
  simp only [peelCluster, glueCluster]
  set t : ℤ := (H : ℤ) - 1 - cap with ht_def
  set b := clusterBottom S t with hb_def
  set ln := ((H : ℤ) - cap - b).toNat with hln_def
  set jn := (band S b t).card - ln with hjn_def
  set p := rowCell S (b - 1) with hp_def
  have hlz : (ln : ℤ) = (H : ℤ) - cap - b := by omega
  have hln1 : 1 ≤ ln := by omega
  have hlnn2 : ln ≤ (band S b t).card := by omega
  have hwrb : IsWalkRow S (b - 1) := hwalkb
  have hpS : p ∈ S := rowCell_mem hwrb
  have hpy : p.2 = b - 1 := rfl
  have hpP : p ∈ band S (b - 1) ((H : ℤ) - 1) :=
    mem_band.mpr ⟨hpS, by omega, by omega⟩
  -- the peeled configuration is a configuration with `cap` walk rows on top
  have hPconn : Connected L (band S (b - 1) ((H : ℤ) - 1)) :=
    connected_band hSc.conn (Or.inl hwrb) (Or.inr hSc.y_le)
  set C0 := shift (-p.1) (-(b - 1)) (band S (b - 1) ((H : ℤ) - 1)) with hC0_def
  have hC0card : C0.card = ln + jn + 1 + cap := by
    rw [hC0_def, card_shift, hPcard]
    omega
  have h00 : ((0 : ℤ), (0 : ℤ)) ∈ C0 := by
    have h := shift_mem (a := -p.1) (b := -(b - 1)) hpP
    rwa [shiftCell_to_origin hpy] at h
  have hC0rows : ∀ c ∈ C0, 0 ≤ c.2 ∧ c.2 ≤ (ln : ℤ) + cap := by
    intro c hcm
    rw [hC0_def, mem_shift, mem_band] at hcm
    have h1 : b - 1 ≤ c.2 - -(b - 1) := hcm.2.1
    have h2 : c.2 - -(b - 1) ≤ (H : ℤ) - 1 := hcm.2.2
    omega
  have hC0rs : ∀ y : ℤ, 0 ≤ y → y ≤ (ln : ℤ) + cap →
      rowSize C0 y = rowSize S (y + (b - 1)) := by
    intro y h0 h1
    rw [hC0_def, rowSize_shift, rowSize_band (by omega) (by omega)]
    congr 1
    ring
  have hC0r0 : rowSize C0 0 = 1 := by
    rw [hC0rs 0 le_rfl (by omega), show (0 : ℤ) + (b - 1) = b - 1 from by ring]
    exact hwalkb
  have hC0cap : ∀ y : ℤ, (ln : ℤ) < y → y ≤ (ln : ℤ) + cap → rowSize C0 y = 1 := by
    intro y h1 h2
    rw [hC0rs y (by omega) h2]
    exact hw _ (by omega) (by omega)
  have hC0multi : ∀ i ∈ Finset.Icc 1 ln, 2 ≤ rowSize C0 (i : ℤ) := by
    intro i hi
    rw [Finset.mem_Icc] at hi
    rw [hC0rs _ (by omega) (by omega)]
    exact hmulti _ (by omega) (by omega)
  have hC0V : C0 ∈ configs L cap ln jn := by
    rw [mem_configs]
    exact ⟨hC0card, h00, hC0rows, hC0r0, hC0cap, hC0multi, connected_shift _ _ hPconn⟩
  -- the anchored remainder is a shorter walk-top animal
  have hR0 : anchorX (band S 0 (b - 1)) ∈ walkTop L (k - jn) (H - cap - ln) :=
    anchorX_seg_mem_walkTop hSc.conn hSc.anchored.y_nonneg hb1 (by omega) hwalkb
      hSc.anchored.y_zero (by omega)
  clear_value jn ln
  have hjmem : jn ∈ Finset.Icc 1 k := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have hlmem : ln ∈ Finset.Icc 1 jn := Finset.mem_Icc.mpr ⟨hln1, by omega⟩
  constructor
  · exact Finset.mem_sigma.mpr ⟨hjmem, Finset.mem_sigma.mpr ⟨hlmem,
      Finset.mem_product.mpr ⟨hC0V, hR0⟩⟩⟩
  -- the round trip: glue the peeled pieces back
  · have hSne : S.Nonempty := by
      obtain ⟨z, hzS, -⟩ := hSc.anchored.y_zero
      exact ⟨z, hzS⟩
    have hr : t - (ln : ℤ) = b - 1 := by omega
    have hwQ : IsWalkRow (anchorX (band S 0 (b - 1))) (b - 1) := by
      rw [isWalkRow_iff_rowSize, rowSize_anchorX, rowSize_band (by omega) le_rfl]
      exact hwalkb
    have hpQ : p ∈ band S 0 (b - 1) := mem_band.mpr ⟨hpS, by omega, le_of_eq hpy⟩
    have hu' : rowCell (anchorX (band S 0 (b - 1))) (b - 1)
        = shiftCell (-minX (band S 0 (b - 1))) 0 p := by
      refine rowCell_eq hwQ ?_ ?_
      · rw [anchorX_def']
        exact shift_mem hpQ
      · change p.2 + 0 = b - 1
        rw [hpy]
        ring
    have hQP : band S 0 (b - 1) ∪ band S (b - 1) ((H : ℤ) - 1) = S := by
      ext c
      simp only [Finset.mem_union, mem_band]
      constructor
      · rintro (⟨h, -, -⟩ | ⟨h, -, -⟩) <;> exact h
      · intro hcS
        have h0 := hSc.anchored.y_nonneg c hcS
        have h1 := hSc.y_le c hcS
        by_cases hcb : c.2 ≤ b - 1
        · exact Or.inl ⟨hcS, h0, hcb⟩
        · exact Or.inr ⟨hcS, by omega, h1⟩
    rw [hr, hu', hC0_def,
      show (shiftCell (-minX (band S 0 (b - 1))) 0 p).1
        = p.1 + -minX (band S 0 (b - 1)) from rfl,
      shift_shift,
      show p.1 + -minX (band S 0 (b - 1)) + -p.1 = -minX (band S 0 (b - 1)) from by ring,
      show b - 1 + -(b - 1) = (0 : ℤ) from by ring,
      anchorX_def' (band S 0 (b - 1)), ← shift_union, hQP, anchorX_shift _ hSne,
      anchorX_eq_self hSc.anchored.x_nonneg hSc.anchored.x_zero]

/-- Backward well-definedness and the glue-then-peel round trip for classes B
and C: the glued animal is canonical, its `cap` top rows are walk rows, its row
`t = H - 1 - cap` is not, and peeling recovers the data. -/
lemma glueCluster_mem_and_peel {cap k H : ℕ} (hH : k + 1 + cap ≤ H) {x : PeelData}
    (hx : x ∈ target L cap k H) :
    (IsAnimal L (H + k) H (glueCluster ((H : ℤ) - 1 - cap) x) ∧
      (∀ y : ℤ, (H : ℤ) - 1 - cap < y → y ≤ (H : ℤ) - 1 →
        rowSize (glueCluster ((H : ℤ) - 1 - cap) x) y = 1) ∧
      ¬ rowSize (glueCluster ((H : ℤ) - 1 - cap) x) ((H : ℤ) - 1 - cap) = 1) ∧
    peelCluster cap H (glueCluster ((H : ℤ) - 1 - cap) x) = x := by
  obtain ⟨j, ℓ, C, R⟩ := x
  rw [target, Finset.mem_sigma, Finset.mem_sigma, Finset.mem_product] at hx
  have hjm : j ∈ Finset.Icc 1 k := hx.1
  have hlm : ℓ ∈ Finset.Icc 1 j := hx.2.1
  have hCm : C ∈ configs L cap ℓ j := hx.2.2.1
  have hRm : R ∈ walkTop L (k - j) (H - cap - ℓ) := hx.2.2.2
  rw [Finset.mem_Icc] at hjm hlm
  obtain ⟨hj1, hjk⟩ := hjm
  obtain ⟨hl1, hlj⟩ := hlm
  have hCv : IsConfig L cap ℓ j C := mem_configs.mp hCm
  obtain ⟨hcR, hwR⟩ := mem_walkTop.mp hRm
  simp only [glueCluster, peelCluster]
  set t : ℤ := (H : ℤ) - 1 - cap with ht_def
  set r := t - (ℓ : ℤ) with hr_def
  have hwRr : IsWalkRow R r := by
    rw [isWalkRow_iff_rowSize, show r = ((H - cap - ℓ : ℕ) : ℤ) - 1 from by omega]
    exact hwR
  set u := rowCell R r with hu_def
  have huR : u ∈ R := rowCell_mem hwRr
  have huy : u.2 = r := rfl
  set C' := shift u.1 r C with hC'_def
  have hRrows : ∀ c ∈ R, 0 ≤ c.2 ∧ c.2 ≤ r := by
    intro c hcm
    have h1 := hcR.anchored.y_nonneg c hcm
    have h2 := hcR.y_le c hcm
    omega
  have hCrows := hCv.rows
  have hC'rows : ∀ c ∈ C', r ≤ c.2 ∧ c.2 ≤ (H : ℤ) - 1 := by
    intro c hcm
    rw [hC'_def, mem_shift] at hcm
    have h1 : 0 ≤ c.2 - r := (hCrows _ hcm).1
    have h2 : c.2 - r ≤ (ℓ : ℤ) + cap := (hCrows _ hcm).2
    omega
  have huC' : u ∈ C' := by
    have h0 := shift_mem (a := u.1) (b := r) hCv.origin
    rw [shiftCell_origin, show ((u.1, r) : ℤ × ℤ) = u from by rw [← huy]] at h0
    exact h0
  have hinter : R ∩ C' = {u} := by
    ext c
    rw [Finset.mem_inter, Finset.mem_singleton]
    constructor
    · rintro ⟨hcR', hcC'⟩
      exact hwRr.eq_of_mem hcR'
        (le_antisymm (hRrows c hcR').2 (hC'rows c hcC').1) huR huy
    · rintro rfl
      exact ⟨huR, huC'⟩
  have hcardU : (R ∪ C').card = H + k := by
    have h := Finset.card_union_add_card_inter R C'
    rw [hinter, Finset.card_singleton] at h
    have hC'c : C'.card = ℓ + j + 1 + cap := by
      rw [hC'_def, card_shift]
      exact hCv.card
    have hRc : R.card = (H - cap - ℓ) + (k - j) := hcR.card
    omega
  have hC'conn : Connected L C' := by
    rw [hC'_def]
    exact connected_shift _ _ hCv.conn
  have hconnU : Connected L (R ∪ C') :=
    connected_union rfl hcR.conn hC'conn ⟨u, Finset.mem_inter.mpr ⟨huR, huC'⟩⟩
  have hUy0 : ∀ c ∈ R ∪ C', 0 ≤ c.2 := by
    intro c hcm
    rcases Finset.mem_union.mp hcm with h | h
    · exact (hRrows c h).1
    · have := (hC'rows c h).1
      omega
  have hUy1 : ∀ c ∈ R ∪ C', c.2 ≤ (H : ℤ) - 1 := by
    intro c hcm
    rcases Finset.mem_union.mp hcm with h | h
    · have := (hRrows c h).2
      omega
    · exact (hC'rows c h).2
  have hUe0 : ∃ c ∈ R ∪ C', c.2 = 0 := by
    obtain ⟨z, hzR, hzy⟩ := hcR.anchored.y_zero
    exact ⟨z, Finset.mem_union_left _ hzR, hzy⟩
  -- the configuration's top row `ℓ + cap` is occupied: a walk row if `cap ≥ 1`,
  -- the cluster's top row if `cap = 0`
  have hCtop : 1 ≤ rowSize C ((ℓ : ℤ) + cap) := by
    rcases Nat.eq_zero_or_pos cap with h0 | hpos
    · have := hCv.multi ℓ (Finset.mem_Icc.mpr ⟨hl1, le_rfl⟩)
      rw [h0, Nat.cast_zero, add_zero]
      omega
    · exact (hCv.cap_walk _ (by omega) le_rfl).ge
  have hUe1 : ∃ c ∈ R ∪ C', c.2 = (H : ℤ) - 1 := by
    obtain ⟨c0, hc0f⟩ := Finset.card_pos.mp hCtop
    rw [Finset.mem_filter] at hc0f
    refine ⟨shiftCell u.1 r c0, Finset.mem_union_right _ ?_, ?_⟩
    · rw [hC'_def]
      exact shift_mem hc0f.1
    · change c0.2 + r = (H : ℤ) - 1
      have := hc0f.2
      omega
  have hrsAbove : ∀ y : ℤ, r < y → rowSize (R ∪ C') y = rowSize C (y - r) := by
    intro y hy
    rw [rowSize_union_right fun c hcm => by have := (hRrows c hcm).2; omega,
      hC'_def, rowSize_shift]
  have hGcap : ∀ y : ℤ, t < y → y ≤ (H : ℤ) - 1 → rowSize (R ∪ C') y = 1 := by
    intro y h1 h2
    rw [hrsAbove _ (by omega)]
    exact hCv.cap_walk _ (by omega) (by omega)
  have hG₀m : 2 ≤ rowSize (R ∪ C') t := by
    rw [hrsAbove _ (by omega), show t - r = (ℓ : ℤ) from by omega]
    exact hCv.multi ℓ (Finset.mem_Icc.mpr ⟨hl1, le_rfl⟩)
  have hwC'r : IsWalkRow C' r := by
    rw [isWalkRow_iff_rowSize, hC'_def, rowSize_shift, sub_self]
    exact hCv.row_zero
  have hG₀r : rowSize (R ∪ C') r = 1 := by
    rw [rowSize, Finset.filter_union, filter_row_eq_singleton hwRr huR huy,
      filter_row_eq_singleton hwC'r huC' huy, Finset.union_self]
    exact Finset.card_singleton u
  refine ⟨⟨isAnimal_anchorX hcardU hconnU hUy0 hUy1 hUe0 hUe1,
    fun y h1 h2 => by rw [rowSize_anchorX]; exact hGcap y h1 h2,
    by rw [rowSize_anchorX]; omega⟩, ?_⟩
  -- the round trip: peel the glued animal back apart
  have hRne : R.Nonempty := by
    obtain ⟨z, hzR, -⟩ := hcR.anchored.y_zero
    exact ⟨z, hzR⟩
  -- the recomputed cluster bottom is `r + 1`
  have hm2X : 2 ≤ rowSize (anchorX (R ∪ C')) t := by
    rw [rowSize_anchorX]
    exact hG₀m
  obtain ⟨⟨hb0', hbt'⟩, hmulti', hminle', -⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ t from by omega) hm2X
  have hble : clusterBottom (anchorX (R ∪ C')) t ≤ r + 1 := by
    refine hminle' (r + 1) (by omega) (by omega) ?_
    intro y hy1 hy2
    rw [rowSize_anchorX, hrsAbove y (by omega),
      show y - r = (((y - r).toNat : ℕ) : ℤ) from by omega]
    exact hCv.multi _ (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
  have hbgt : r < clusterBottom (anchorX (R ∪ C')) t := by
    by_contra hcon
    push Not at hcon
    have h2 := hmulti' r hcon (by omega)
    rw [rowSize_anchorX, hG₀r] at h2
    omega
  have hbeq : clusterBottom (anchorX (R ∪ C')) t = r + 1 := by omega
  -- the interior cluster band of the configuration
  have hsegRempty : band R (r + 1) t = ∅ := by
    rw [band, Finset.filter_eq_empty_iff]
    intro c hcm
    have := (hRrows c hcm).2
    omega
  have hsegC' : band C' (r + 1) t = shift u.1 r (band C 1 (ℓ : ℤ)) := by
    rw [hC'_def, band_shift, show r + 1 - r = (1 : ℤ) from by ring,
      show t - r = (ℓ : ℤ) from by omega]
  have hCcard : (band C 1 (ℓ : ℤ)).card = ℓ + j := by
    have hCself : band C 0 ((ℓ : ℤ) + cap) = C := band_eq_self hCrows
    have h1 := card_seg_sum C 0 ((ℓ : ℤ) + cap)
    have h2 := card_seg_sum C 1 (ℓ : ℤ)
    have hs1 : ∑ y ∈ Finset.Icc (0 : ℤ) ((ℓ : ℤ) + cap), rowSize C y
        = (∑ y ∈ Finset.Icc (0 : ℤ) 0, rowSize C y)
          + ∑ y ∈ Finset.Icc (1 : ℤ) ((ℓ : ℤ) + cap), rowSize C y := by
      have h := sum_Icc_split (rowSize C) (a := (0 : ℤ)) (b := 0) (c := (ℓ : ℤ) + cap)
        (by omega) (by omega)
      rwa [show (0 : ℤ) + 1 = 1 from by ring] at h
    have hs2 : ∑ y ∈ Finset.Icc (1 : ℤ) ((ℓ : ℤ) + cap), rowSize C y
        = (∑ y ∈ Finset.Icc (1 : ℤ) (ℓ : ℤ), rowSize C y)
          + ∑ y ∈ Finset.Icc ((ℓ : ℤ) + 1) ((ℓ : ℤ) + cap), rowSize C y :=
      sum_Icc_split (rowSize C) (by omega) (by omega)
    have hs3 : ∑ y ∈ Finset.Icc ((ℓ : ℤ) + 1) ((ℓ : ℤ) + cap), rowSize C y = cap := by
      rw [sum_rowSize_walk fun y hy1 hy2 => hCv.cap_walk y (by omega) hy2]
      omega
    rw [hCself] at h1
    rw [show Finset.Icc (0 : ℤ) 0 = {(0 : ℤ)} from Finset.Icc_self 0,
      Finset.sum_singleton] at hs1
    have hr0' : rowSize C 0 = 1 := hCv.row_zero
    have hCcardv : C.card = ℓ + j + 1 + cap := hCv.card
    omega
  -- the walk cell of the recomputed base row
  have hcellX : rowCell (anchorX (R ∪ C')) r = shiftCell (-minX (R ∪ C')) 0 u := by
    refine rowCell_eq ?_ ?_ ?_
    · rw [isWalkRow_iff_rowSize, rowSize_anchorX]
      exact hG₀r
    · rw [anchorX_def']
      exact shift_mem (Finset.mem_union_left _ huR)
    · change u.2 + 0 = r
      omega
  have hsegtopX : band (anchorX (R ∪ C')) r ((H : ℤ) - 1)
      = shift (-minX (R ∪ C')) 0 C' := by
    rw [anchorX_def', band_xShift]
    congr 1
    rw [band_union]
    have h1 : band R r ((H : ℤ) - 1) = {u} := by
      ext c
      rw [mem_band, Finset.mem_singleton]
      constructor
      · rintro ⟨hcR', h1', -⟩
        exact hwRr.eq_of_mem hcR' (le_antisymm (hRrows c hcR').2 h1') huR huy
      · rintro rfl
        exact ⟨huR, le_of_eq huy.symm, by omega⟩
    have h2 : band C' r ((H : ℤ) - 1) = C' := band_eq_self fun c hcm => hC'rows c hcm
    rw [h1, h2]
    exact Finset.union_eq_right.mpr (Finset.singleton_subset_iff.mpr huC')
  have hsegbotX : band (anchorX (R ∪ C')) 0 r = shift (-minX (R ∪ C')) 0 R := by
    rw [anchorX_def', band_xShift]
    congr 1
    rw [band_union]
    have h1 : band R 0 r = R := band_eq_self fun c hcm => hRrows c hcm
    have h2 : band C' 0 r = {u} := by
      ext c
      rw [mem_band, Finset.mem_singleton]
      constructor
      · rintro ⟨hcC', -, h2'⟩
        exact hwC'r.eq_of_mem hcC' (le_antisymm h2' (hC'rows c hcC').1) huC' huy
      · rintro rfl
        exact ⟨huC', by omega, le_of_eq huy⟩
    rw [h1, h2]
    exact Finset.union_eq_left.mpr (Finset.singleton_subset_iff.mpr huR)
  rw [hbeq, show r + 1 - 1 = r from by ring]
  simp only [Sigma.mk.injEq, heq_eq_eq, Prod.mk.injEq]
  refine ⟨?_, by omega, ?_, ?_⟩
  · -- the surplus component
    rw [anchorX_def', band_xShift, band_union, hsegRempty, Finset.empty_union, hsegC',
      card_shift, card_shift, hCcard]
    omega
  · -- the configuration component
    rw [hcellX, hsegtopX,
      show (shiftCell (-minX (R ∪ C')) 0 u).1 = u.1 + -minX (R ∪ C') from rfl,
      shift_shift, hC'_def, shift_shift,
      show -(u.1 + -minX (R ∪ C')) + -minX (R ∪ C') + u.1 = (0 : ℤ) from by ring,
      show -r + 0 + r = (0 : ℤ) from by ring, shift_zero]
  · -- the remainder component
    rw [hsegbotX, anchorX_shift _ hRne, anchorX_eq_self hcR.anchored.x_nonneg hcR.anchored.x_zero]

/-- **The cluster count**: canonical animals whose `cap` top rows are walk
rows and whose row `H - 1 - cap` is not are counted by configurations with
`cap` walk rows on top times shorter walk-top remainders, aggregated over
`(j, ℓ)`. Class B is `cap = 1`, class C is `cap = 0`. -/
lemma card_cluster (cap k H : ℕ) (hH : k + 1 + cap ≤ H) :
    ((animals L k H).filter fun S =>
      CapWalk cap H S ∧ ¬ rowSize S ((H : ℤ) - 1 - cap) = 1).card =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        (configs L cap ℓ j).card * d L (k - j) (H - cap - ℓ) := by
  have htarget : (target L cap k H).card = ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
      (configs L cap ℓ j).card * d L (k - j) (H - cap - ℓ) := by
    rw [target, Finset.card_sigma]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [Finset.card_sigma]
    exact Finset.sum_congr rfl fun ℓ _ => by rw [Finset.card_product]; rfl
  rw [← htarget]
  refine Finset.card_nbij' (peelCluster cap H) (glueCluster ((H : ℤ) - 1 - cap)) ?_ ?_ ?_ ?_
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter, mem_animals] at hS
    rw [Finset.mem_coe]
    exact (peelCluster_mem_and_glue hH hS.1 (capWalk_iff.mp hS.2.1) hS.2.2).1
  · intro x hx
    rw [Finset.mem_coe] at hx
    rw [Finset.mem_coe, Finset.mem_filter, mem_animals]
    obtain ⟨⟨h1, h2, h3⟩, -⟩ := glueCluster_mem_and_peel hH hx
    exact ⟨h1, capWalk_iff.mpr h2, h3⟩
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter, mem_animals] at hS
    exact (peelCluster_mem_and_glue hH hS.1 (capWalk_iff.mp hS.2.1) hS.2.2).2
  · intro x hx
    rw [Finset.mem_coe] at hx
    exact (glueCluster_mem_and_peel hH hx).2

/-- **Class-B count**: walk-top animals with a multi second-top row are
counted by interior cluster configurations times shorter walk-top remainders,
aggregated over `(j, ℓ)`. The `cap = 1` case of `card_cluster`. -/
lemma card_walkCluster (k H : ℕ) (hH : k + 2 ≤ H) :
    ((walkTop L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 2) = 1).card =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V L ℓ j * d L (k - j) (H - 1 - ℓ) := by
  have key : ((walkTop L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 2) = 1)
      = (animals L k H).filter fun S =>
        CapWalk 1 H S ∧ ¬ rowSize S ((H : ℤ) - 1 - ((1 : ℕ) : ℤ)) = 1 := by
    rw [walkTop, Finset.filter_filter]
    refine Finset.filter_congr fun S _ => ?_
    rw [capWalk_one_iff, Nat.cast_one, show (H : ℤ) - 1 - 1 = (H : ℤ) - 2 from by ring]
  rw [key]
  exact card_cluster 1 k H (by omega)

/-- **Class-C count**: canonical animals with a multi top row are counted by
top-edge cluster configurations times shorter walk-top remainders, aggregated
over `(j, ℓ)`. The `cap = 0` case of `card_cluster`. -/
lemma card_clusterTop (k H : ℕ) (hH : k + 1 ≤ H) :
    ((animals L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 1) = 1).card =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt L ℓ j * d L (k - j) (H - ℓ) := by
  have key : ((animals L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 1) = 1)
      = (animals L k H).filter fun S =>
        CapWalk 0 H S ∧ ¬ rowSize S ((H : ℤ) - 1 - ((0 : ℕ) : ℤ)) = 1 := by
    refine Finset.filter_congr fun S _ => ?_
    rw [Nat.cast_zero, sub_zero]
    exact ⟨fun h => ⟨capWalk_zero, h⟩, fun h => h.2⟩
  have h := card_cluster (L := L) 0 k H (by omega)
  simp only [Nat.sub_zero] at h
  rw [key]
  exact h

/-! ## The main theorems -/

/-- **The d-recursion**: for `H ≥ k + 2`, a walk-top animal
splits by its second-top row — walk (class A: `b` up-offsets on a height-`H-1`
walk-top remainder) or the base of a cluster (class B: an interior
`V`-configuration capping a shorter walk-top remainder). -/
theorem d_rec (L : RowLocal) (k H : ℕ) (hH : k + 2 ≤ H) :
    d L k H = L.b * d L k (H - 1) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V L ℓ j * d L (k - j) (H - 1 - ℓ) := by
  classical
  have hsplit := Finset.card_filter_add_card_filter_not (s := walkTop L k H)
    (fun S => rowSize S ((H : ℤ) - 2) = 1)
  rw [d, ← hsplit, card_walkWalk k H hH, card_walkCluster k H hH]

/-- **The top-row identity**: for `H ≥ k + 1`, an animal has a walk top
row (counted by `d L k H`) or a multi top row — a top-edge `Vᵗ`-configuration
capping a shorter walk-top remainder (class C). -/
theorem T_of_d (L : RowLocal) (k H : ℕ) (hH : k + 1 ≤ H) :
    T L (H + k) H = d L k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt L ℓ j * d L (k - j) (H - ℓ) := by
  classical
  have hsplit := Finset.card_filter_add_card_filter_not (s := animals L k H)
    (fun S => rowSize S ((H : ℤ) - 1) = 1)
  rw [← card_animals, ← hsplit, filter_animals_walkTop, card_clusterTop k H hH]
  rfl

end Polyplets.Universal
