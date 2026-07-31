/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.Weights

/-!
# Peeling: the d-recursion and the c-identity, for every row-local lattice

The two counting identities, proved by explicit bijections, over an arbitrary
row-local lattice `L`:

* `d_rec` : for `H ≥ k + 2`,
  `d L k H = b * d L k (H-1) + ∑_{j=1..k} ∑_{ℓ=1..j} V L ℓ j * d L (k-j) (H-1-ℓ)`;
* `c_ident` : for `H ≥ k + 1`,
  `T L (H+k) H = d L k H + ∑_{j=1..k} ∑_{ℓ=1..j} Vt L ℓ j * d L (k-j) (H-ℓ)`,

where `b = L.D.card` is the drift count. Both follow from a disjoint split on
the row profile near the top and three peeling bijections:

* **Class A** (walk top and walk second-top row): erasing the unique top cell
  and re-anchoring is a bijection onto `L.D × Dc L k (H-1)`; the extra datum is
  the x-offset of the top cell over the second-top cell, which is an up-offset
  of `L` (`card_classA`).
* **Class B** (walk top, multi second-top row): peeling the maximal cluster
  `[b, H-2]` together with the walk cells directly below (row `b-1`) and on
  top (row `H-1`) is a bijection onto `Σ (j,ℓ), CFGV L ℓ j × Dc L (k-j) (H-1-ℓ)`
  (`card_classB`).
* **Class C** (multi top row, for the c-identity): the same with the cluster
  reaching the top edge, onto `Σ (j,ℓ), CFGVt L ℓ j × Dc L (k-j) (H-ℓ)`
  (`card_classC`).

All three share one x-renormalization pattern: the peeled configuration is
based at its bottom walk cell (making it x-shift-invariant), the remainder is
re-anchored by `xNorm`, and gluing shifts the configuration onto the
remainder's unique top cell. Membership is always matched against the
propositional characterizations `mem_Dc`, `mem_CFGV`, `mem_CFGVt`.

## The verbatim wager, settled

This file is `Peel.lean` transcribed with `kingAdj ↦ Adj L` and
`KingConnected ↦ Conn L`. Every proof carries over unchanged. The drift count
enters at exactly **three** places, all inside class A:

* `peelA_mem_and_glue`: the recorded offset lies in `L.D` — king
  `|Δx| ≤ 1` becomes `adj_up_mem` (the top cell is one row above the second-top
  cell, so their x-displacement IS an up-offset, by definition of `Adj`);
* `glueA_mem_and_peel`: conversely every `δ ∈ L.D` re-attaches legally
  (`adj_of_up`);
* `card_classA`: the target is `L.D ×ˢ Dc L k (H-1)`, of cardinality
  `L.b * d L k (H-1)` — the king `3` is `L.D.card`, nothing else.

Classes B and C mention adjacency only through connectivity lemmas
(`conn_seg`, `conn_union`, `conn_shift`), which are lattice-agnostic. No
proof needed the reach `L.M`, the shape of `D`, or any arithmetic of `b`.
-/

namespace Polyplets.Universal

variable {L : RowLocal}

/-! ## Translation toolkit -/

/-- Translate a cell by `(a, b)`. -/
def shiftCell (a b : ℤ) (c : ℤ × ℤ) : ℤ × ℤ := (c.1 + a, c.2 + b)

lemma shiftCell_injective (a b : ℤ) : Function.Injective (shiftCell a b) := by
  intro c d h
  simp only [shiftCell, Prod.mk.injEq] at h
  exact Prod.ext_iff.mpr ⟨by omega, by omega⟩

/-- Translate every cell of `S` by `(a, b)`. -/
def shift (a b : ℤ) (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) := S.image (shiftCell a b)

lemma mem_shift {a b : ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} :
    c ∈ shift a b S ↔ (c.1 - a, c.2 - b) ∈ S := by
  simp only [shift, Finset.mem_image]
  constructor
  · rintro ⟨x, hx, rfl⟩
    simpa [shiftCell] using hx
  · intro h
    exact ⟨(c.1 - a, c.2 - b), h, by simp [shiftCell]⟩

lemma shift_mem {a b : ℤ} {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} (hc : c ∈ S) :
    shiftCell a b c ∈ shift a b S :=
  Finset.mem_image_of_mem _ hc

lemma shift_shift (a b a' b' : ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (shift a' b' S) = shift (a + a') (b + b') S := by
  rw [shift, shift, shift, Finset.image_image]
  congr 1
  funext c
  simp only [Function.comp_apply, shiftCell, Prod.mk.injEq]
  constructor <;> ring

@[simp] lemma shift_zero (S : Finset (ℤ × ℤ)) : shift 0 0 S = S := by
  have h : shiftCell 0 0 = id := funext fun c => by simp [shiftCell]
  rw [shift, h, Finset.image_id]

@[simp] lemma card_shift (a b : ℤ) (S : Finset (ℤ × ℤ)) : (shift a b S).card = S.card :=
  Finset.card_image_of_injective S (shiftCell_injective a b)

lemma shift_union (a b : ℤ) (A B : Finset (ℤ × ℤ)) :
    shift a b (A ∪ B) = shift a b A ∪ shift a b B :=
  Finset.image_union _ _

lemma shift_insert (a b : ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (insert c S) = insert (shiftCell a b c) (shift a b S) :=
  Finset.image_insert _ _ _

lemma shift_erase (a b : ℤ) (c : ℤ × ℤ) (S : Finset (ℤ × ℤ)) :
    shift a b (S.erase c) = (shift a b S).erase (shiftCell a b c) :=
  Finset.image_erase (shiftCell_injective a b) _ _

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

/-- **Translation invariance of adjacency.** Both the row case and the two
vertical cases are stated in differences of coordinates, so a common
translation cancels. -/
lemma adj_shiftCell {a b : ℤ} {c d : ℤ × ℤ} (h : Adj L c d) :
    Adj L (shiftCell a b c) (shiftCell a b d) := by
  obtain ⟨hne, hcase⟩ := h
  refine ⟨fun heq => hne (shiftCell_injective a b heq), ?_⟩
  have hx : (shiftCell a b c).1 - (shiftCell a b d).1 = c.1 - d.1 := by
    change c.1 + a - (d.1 + a) = c.1 - d.1
    ring
  have hx' : (shiftCell a b d).1 - (shiftCell a b c).1 = d.1 - c.1 := by
    change d.1 + a - (c.1 + a) = d.1 - c.1
    ring
  have hy0 : (shiftCell a b c).2 = (shiftCell a b d).2 ↔ c.2 = d.2 := by
    change (c.2 + b = d.2 + b) ↔ _
    omega
  have hy : (shiftCell a b c).2 = (shiftCell a b d).2 + 1 ↔ c.2 = d.2 + 1 := by
    change (c.2 + b = d.2 + b + 1) ↔ _
    omega
  have hy' : (shiftCell a b d).2 = (shiftCell a b c).2 + 1 ↔ d.2 = c.2 + 1 := by
    change (d.2 + b = c.2 + b + 1) ↔ _
    omega
  rcases hcase with ⟨hr, hd⟩ | ⟨hr, hd⟩ | ⟨hr, hd⟩
  · exact Or.inl ⟨hy0.mpr hr, by rw [hx]; exact hd⟩
  · exact Or.inr (Or.inl ⟨hy'.mpr hr, by rw [hx']; exact hd⟩)
  · exact Or.inr (Or.inr ⟨hy.mpr hr, by rw [hx]; exact hd⟩)

lemma conn_shift (a b : ℤ) {S : Finset (ℤ × ℤ)} (h : Conn L S) :
    Conn L (shift a b S) := by
  intro p hp q hq
  obtain ⟨p₀, hp₀, rfl⟩ := Finset.mem_image.mp hp
  obtain ⟨q₀, hq₀, rfl⟩ := Finset.mem_image.mp hq
  refine Relation.ReflTransGen.lift (shiftCell a b) ?_ (h p₀ hp₀ q₀ hq₀)
  rintro x y ⟨hx, hy, hadj⟩
  exact ⟨shift_mem hx, shift_mem hy, adj_shiftCell hadj⟩

lemma seg_shift (a b r r' : ℤ) (S : Finset (ℤ × ℤ)) :
    seg (shift a b S) r r' = shift a b (seg S (r - b) (r' - b)) := by
  ext c
  simp only [mem_seg, mem_shift]
  constructor
  · rintro ⟨h1, h2, h3⟩
    exact ⟨h1, by omega, by omega⟩
  · rintro ⟨h1, h2, h3⟩
    exact ⟨h1, by omega, by omega⟩

/-! ## The x-renormalization `xNorm` -/

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
noncomputable def xNorm (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  shift (-minX S) 0 S

lemma xNorm_eq_self {S : Finset (ℤ × ℤ)} (h0 : ∀ c ∈ S, 0 ≤ c.1)
    (he : ∃ c ∈ S, c.1 = 0) : xNorm S = S := by
  rw [xNorm, minX_eq_zero h0 he, neg_zero, shift_zero]

/-- Shift invariance: re-anchoring forgets any prior x-translation. The
workhorse of all three round trips. -/
lemma xNorm_shift (a : ℤ) {S : Finset (ℤ × ℤ)} (h : S.Nonempty) :
    xNorm (shift a 0 S) = xNorm S := by
  rw [xNorm, minX_shift a 0 h, shift_shift]
  have he : -(minX S + a) + a = -minX S := by ring
  rw [he, add_zero, xNorm]

@[simp] lemma card_xNorm (S : Finset (ℤ × ℤ)) : (xNorm S).card = S.card := card_shift _ _ _

lemma conn_xNorm {S : Finset (ℤ × ℤ)} (h : Conn L S) :
    Conn L (xNorm S) := conn_shift _ _ h

@[simp] lemma rowSize_xNorm (S : Finset (ℤ × ℤ)) (y : ℤ) :
    rowSize (xNorm S) y = rowSize S y := by
  rw [xNorm, rowSize_shift, sub_zero]

lemma xNorm_x_nonneg {S : Finset (ℤ × ℤ)} : ∀ c ∈ xNorm S, 0 ≤ c.1 := by
  intro c hc
  rw [xNorm, mem_shift] at hc
  have h2 : minX S ≤ c.1 - -minX S := minX_le hc
  omega

lemma xNorm_exists_x_zero {S : Finset (ℤ × ℤ)} (h : S.Nonempty) :
    ∃ c ∈ xNorm S, c.1 = 0 := by
  obtain ⟨c, hcS, hc1⟩ := exists_minX h
  refine ⟨shiftCell (-minX S) 0 c, shift_mem hcS, ?_⟩
  change c.1 + -minX S = 0
  omega

lemma forall_row_xNorm {S : Finset (ℤ × ℤ)} {P : ℤ → Prop} (h : ∀ c ∈ S, P c.2) :
    ∀ c ∈ xNorm S, P c.2 := by
  intro c hc
  rw [xNorm, mem_shift] at hc
  have hP := h _ hc
  simpa using hP

lemma exists_row_xNorm {S : Finset (ℤ × ℤ)} {y : ℤ} (h : ∃ c ∈ S, c.2 = y) :
    ∃ c ∈ xNorm S, c.2 = y := by
  obtain ⟨c, hcS, hc2⟩ := h
  refine ⟨shiftCell (-minX S) 0 c, shift_mem hcS, ?_⟩
  change c.2 + 0 = y
  omega

/-- Canonicality of a re-anchored piece: everything except the x-anchoring is
inherited, and `xNorm` provides the anchoring. -/
lemma isCanonical_xNorm {n H : ℕ} {S : Finset (ℤ × ℤ)}
    (hcard : S.card = n) (hconn : Conn L S)
    (hy0 : ∀ c ∈ S, 0 ≤ c.2) (hy1 : ∀ c ∈ S, c.2 ≤ (H : ℤ) - 1)
    (he0 : ∃ c ∈ S, c.2 = 0) (he1 : ∃ c ∈ S, c.2 = (H : ℤ) - 1) :
    IsCanonical L n H (xNorm S) := by
  have hne : S.Nonempty := by
    obtain ⟨c, hc, -⟩ := he0
    exact ⟨c, hc⟩
  exact ⟨by rw [card_xNorm, hcard], conn_xNorm hconn,
    xNorm_x_nonneg, xNorm_exists_x_zero hne,
    forall_row_xNorm (P := fun t => 0 ≤ t) hy0, exists_row_xNorm he0,
    forall_row_xNorm (P := fun t => t ≤ (H : ℤ) - 1) hy1, exists_row_xNorm he1⟩

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

lemma rowSize_seg {S : Finset (ℤ × ℤ)} {a b y : ℤ} (ha : a ≤ y) (hb : y ≤ b) :
    rowSize (seg S a b) y = rowSize S y := by
  rw [rowSize, rowSize]
  congr 1
  ext c
  simp only [Finset.mem_filter, mem_seg]
  constructor
  · rintro ⟨⟨h1, -, -⟩, h4⟩
    exact ⟨h1, h4⟩
  · rintro ⟨h1, h4⟩
    exact ⟨⟨h1, by omega, by omega⟩, h4⟩

/-- The cell count of a row band is the sum of its row sizes. -/
lemma card_seg_sum (S : Finset (ℤ × ℤ)) (a b : ℤ) :
    (seg S a b).card = ∑ y ∈ Finset.Icc a b, rowSize S y := by
  rw [Finset.card_eq_sum_card_fiberwise (f := Prod.snd) (t := Finset.Icc a b) ?_]
  · refine Finset.sum_congr rfl fun y hy => ?_
    rw [Finset.mem_Icc] at hy
    rw [← rowSize_seg hy.1 hy.2, rowSize]
  · intro c hc
    rw [Finset.mem_coe, mem_seg] at hc
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

lemma rowSize_union_left {A B : Finset (ℤ × ℤ)} {y : ℤ} (h : ∀ c ∈ B, c.2 ≠ y) :
    rowSize (A ∪ B) y = rowSize A y := by
  rw [rowSize, rowSize, Finset.filter_union,
    Finset.filter_eq_empty_iff.mpr fun c hc => h c hc, Finset.union_empty]

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
lemma conn_pair {u v : ℤ × ℤ} (h : Adj L u v) :
    Conn L {u, v} := by
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

Peeling the top cell of a class-A animal and re-anchoring is a bijection onto
`L.D × Dc L k (H-1)`; the recorded offset `δ` (top cell x minus second-top cell
x) is x-shift-invariant, which is what makes the round trips close after
`xNorm`. This is the ONLY place in the geometric port where the lattice's
up-offset set is visible, and it is visible only as the index set of the
bijection — the king file's `{-1, 0, 1}` is `L.D`. -/

/-- Class-A forward map: erase the unique top cell, re-anchor the remainder,
and record the top cell's x-offset over the second-top cell. -/
noncomputable def peelA (H : ℕ) (S : Finset (ℤ × ℤ)) : ℤ × Finset (ℤ × ℤ) :=
  ((rowCell S ((H : ℤ) - 1)).1 - (rowCell S ((H : ℤ) - 2)).1,
    xNorm (S.erase (rowCell S ((H : ℤ) - 1))))

/-- Class-A backward map: re-attach a top cell at the recorded offset over the
remainder's unique top cell, then re-anchor. -/
noncomputable def glueA (H : ℕ) (x : ℤ × Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  xNorm (insert ((rowCell x.2 ((H : ℤ) - 2)).1 + x.1, (H : ℤ) - 1) x.2)

/-- Forward well-definedness and the peel-then-glue round trip for class A. -/
lemma peelA_mem_and_glue {k H : ℕ} (hH : k + 2 ≤ H) {S : Finset (ℤ × ℤ)}
    (hS : S ∈ Dc L k H) (hw2 : rowSize S ((H : ℤ) - 2) = 1) :
    peelA H S ∈ L.D ×ˢ Dc L k (H - 1) ∧ glueA H (peelA H S) = S := by
  obtain ⟨hc, hw1⟩ := mem_Dc.mp hS
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
    obtain ⟨z, hzS, hzy⟩ := hc.2.2.2.2.2.1
    have hwz : w ≠ z := by
      intro heq
      rw [← heq] at hzy
      rw [hwy] at hzy
      omega
    rcases Relation.ReflTransGen.cases_head (hc.2.1 w hwS z hzS) with heq | ⟨x, hstep, -⟩
    · exact absurd heq hwz
    · obtain ⟨-, hxS, hadjwx⟩ := hstep
      have hxy : x.2 = (H : ℤ) - 2 := by
        have h1 := adj_abs_dy_le hadjwx
        rw [abs_le] at h1
        have h2 := hc.2.2.2.2.2.2.1 x hxS
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
    rw [hS'_def, Finset.card_erase_of_mem hwS, hc.1]
    omega
  have hS'conn : Conn L S' := by
    rw [hS'_def]
    refine conn_erase_top hc.2.1 hc.2.2.2.2.2.2.1 hwr1 ?_ hwS hwy
    have he : (H : ℤ) - 1 - 1 = (H : ℤ) - 2 := by ring
    rw [he]
    exact hwr2
  have hS'rows : ∀ c ∈ S', c.2 ≤ (H : ℤ) - 2 := by
    intro c hcm
    obtain ⟨hcw, hcS⟩ := Finset.mem_erase.mp hcm
    have h1 := hc.2.2.2.2.2.2.1 c hcS
    rcases eq_or_lt_of_le h1 with heq | hlt
    · exact absurd (hwr1.eq_of_mem hcS heq hwS hwy) hcw
    · omega
  have hS'y0 : ∀ c ∈ S', 0 ≤ c.2 := fun c hcm =>
    hc.2.2.2.2.1 c (Finset.mem_erase.mp hcm).2
  have hw'S' : w' ∈ S' := by
    rw [hS'_def]
    refine Finset.mem_erase.mpr ⟨?_, hw'S⟩
    intro heq
    have h := hw'y
    rw [heq, hwy] at h
    omega
  have hS'e0 : ∃ c ∈ S', c.2 = 0 := by
    obtain ⟨z, hzS, hzy⟩ := hc.2.2.2.2.2.1
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
  have hR : xNorm S' ∈ Dc L k (H - 1) := by
    rw [mem_Dc]
    refine ⟨isCanonical_xNorm hS'card hS'conn hS'y0 (fun c hcm => ?_) hS'e0 ?_, ?_⟩
    · have := hS'rows c hcm
      omega
    · obtain ⟨c, hcm, hcy⟩ := hS'e1
      exact ⟨c, hcm, by omega⟩
    · rw [rowSize_xNorm]
      have he2 : ((H - 1 : ℕ) : ℤ) - 1 = (H : ℤ) - 2 := by omega
      rw [he2]
      exact hS'w
  constructor
  · simp only [peelA, ← hw_def, ← hw'_def, ← hS'_def]
    rw [Finset.mem_product]
    exact ⟨hδ, hR⟩
  -- round trip: glue the peel back
  · have hwalkR : IsWalkRow (xNorm S') ((H : ℤ) - 2) := by
      rw [isWalkRow_iff_rowSize, rowSize_xNorm]
      exact hS'w
    have hw'shift : shiftCell (-minX S') 0 w' ∈ xNorm S' := by
      rw [show xNorm S' = shift (-minX S') 0 S' from rfl]
      exact shift_mem hw'S'
    have hu : rowCell (xNorm S') ((H : ℤ) - 2) = shiftCell (-minX S') 0 w' := by
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
    calc glueA H (peelA H S)
        = xNorm (insert ((rowCell (xNorm S') ((H : ℤ) - 2)).1 + (w.1 - w'.1),
            (H : ℤ) - 1) (xNorm S')) := by
          simp only [glueA, peelA, ← hw_def, ← hw'_def, ← hS'_def]
      _ = xNorm (shift (-minX S') 0 (insert w S')) := by
          rw [hu, hcell, show xNorm S' = shift (-minX S') 0 S' from rfl, ← shift_insert]
      _ = xNorm (insert w S') := xNorm_shift _ ⟨w, Finset.mem_insert_self w S'⟩
      _ = xNorm S := by rw [hS'_def, Finset.insert_erase hwS]
      _ = S := xNorm_eq_self hc.2.2.1 hc.2.2.2.1

/-- Backward well-definedness and the glue-then-peel round trip for class A. -/
lemma glueA_mem_and_peel {k H : ℕ} (hH : k + 2 ≤ H) {x : ℤ × Finset (ℤ × ℤ)}
    (hx : x ∈ L.D ×ˢ Dc L k (H - 1)) :
    (glueA H x ∈ Dc L k H ∧ rowSize (glueA H x) ((H : ℤ) - 2) = 1) ∧
      peelA H (glueA H x) = x := by
  obtain ⟨δ, R⟩ := x
  rw [Finset.mem_product] at hx
  obtain ⟨hδm, hR⟩ := hx
  obtain ⟨hcR, hwR⟩ := mem_Dc.mp hR
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
    have h1 := hcR.2.2.2.2.1 c hcm
    have h2 := hcR.2.2.2.2.2.2.1 c hcm
    omega
  have hw₀R : w₀ ∉ R := by
    intro hmem
    have h2 := (hRrows w₀ hmem).2
    rw [hw₀y] at h2
    omega
  set G₀ := insert w₀ R with hG₀_def
  have hG₀card : G₀.card = H + k := by
    rw [hG₀_def, Finset.card_insert_of_notMem hw₀R, hcR.1]
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
  have hG₀conn : Conn L G₀ :=
    conn_union hG₀eq hcR.2.1 (conn_pair hadj)
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
    obtain ⟨z, hzR, hzy⟩ := hcR.2.2.2.2.2.1
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
  have hgl : glueA H (δ, R) = xNorm G₀ := by
    simp only [glueA]
    rw [← hu_def, ← hw₀_def, ← hG₀_def]
  have hGmem : glueA H (δ, R) ∈ Dc L k H := by
    rw [hgl, mem_Dc]
    refine ⟨isCanonical_xNorm hG₀card hG₀conn hG₀y0 hG₀y1 hG₀e0 hG₀e1, ?_⟩
    rw [rowSize_xNorm]
    exact hG₀top
  have hG2' : rowSize (glueA H (δ, R)) ((H : ℤ) - 2) = 1 := by
    rw [hgl, rowSize_xNorm]
    exact hG₀2
  refine ⟨⟨hGmem, hG2'⟩, ?_⟩
  -- round trip: peel the glue back apart
  have hGw1 : IsWalkRow (xNorm G₀) ((H : ℤ) - 1) := by
    rw [isWalkRow_iff_rowSize, rowSize_xNorm]
    exact hG₀top
  have hGw2 : IsWalkRow (xNorm G₀) ((H : ℤ) - 2) := by
    rw [isWalkRow_iff_rowSize, rowSize_xNorm]
    exact hG₀2
  have hwG : rowCell (xNorm G₀) ((H : ℤ) - 1) = shiftCell (-minX G₀) 0 w₀ := by
    refine rowCell_eq hGw1 ?_ ?_
    · rw [show xNorm G₀ = shift (-minX G₀) 0 G₀ from rfl]
      exact shift_mem (by rw [hG₀_def]; exact Finset.mem_insert_self _ _)
    · change w₀.2 + 0 = (H : ℤ) - 1
      rw [hw₀y]
      ring
  have huG : rowCell (xNorm G₀) ((H : ℤ) - 2) = shiftCell (-minX G₀) 0 u := by
    refine rowCell_eq hGw2 ?_ ?_
    · rw [show xNorm G₀ = shift (-minX G₀) 0 G₀ from rfl]
      exact shift_mem (by rw [hG₀_def]; exact Finset.mem_insert_of_mem huR)
    · change u.2 + 0 = (H : ℤ) - 2
      rw [huy]
      ring
  have hδrec : (rowCell (xNorm G₀) ((H : ℤ) - 1)).1
      - (rowCell (xNorm G₀) ((H : ℤ) - 2)).1 = δ := by
    rw [hwG, huG]
    change w₀.1 + -minX G₀ - (u.1 + -minX G₀) = δ
    rw [show w₀.1 = u.1 + δ from rfl]
    ring
  have herase : (xNorm G₀).erase (rowCell (xNorm G₀) ((H : ℤ) - 1))
      = shift (-minX G₀) 0 R := by
    rw [hwG, show xNorm G₀ = shift (-minX G₀) 0 G₀ from rfl, ← shift_erase, hG₀_def,
      Finset.erase_insert hw₀R]
  have hRne : R.Nonempty := by
    obtain ⟨z, hzR, -⟩ := hcR.2.2.2.2.2.1
    exact ⟨z, hzR⟩
  rw [hgl]
  simp only [peelA]
  rw [hδrec, herase, xNorm_shift (-minX G₀) hRne,
    xNorm_eq_self hcR.2.2.1 hcR.2.2.2.1]

/-- **Class-A count**: walk-top animals whose second-top row is also a walk
row are `b · d L k (H-1)` — the up-offset and the re-anchored remainder are a
bijection. The king file's `3` is `L.D.card = L.b`. -/
lemma card_classA (k H : ℕ) (hH : k + 2 ≤ H) :
    ((Dc L k H).filter fun S => rowSize S ((H : ℤ) - 2) = 1).card
      = L.b * d L k (H - 1) := by
  have h3 : (L.D ×ˢ Dc L k (H - 1)).card = L.b * d L k (H - 1) := by
    rw [Finset.card_product]
    rfl
  rw [← h3]
  refine Finset.card_nbij' (peelA H) (glueA H) ?_ ?_ ?_ ?_
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    rw [Finset.mem_coe]
    exact (peelA_mem_and_glue hH hS.1 hS.2).1
  · intro x hx
    rw [Finset.mem_coe] at hx
    rw [Finset.mem_coe, Finset.mem_filter]
    exact (glueA_mem_and_peel hH hx).1
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    exact (peelA_mem_and_glue hH hS.1 hS.2).2
  · intro x hx
    rw [Finset.mem_coe] at hx
    exact (glueA_mem_and_peel hH hx).2

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
the based configuration, and the re-anchored walk-top remainder. -/
abbrev PeelData : Type :=
  Σ _ : ℕ, Σ _ : ℕ, Finset (ℤ × ℤ) × Finset (ℤ × ℤ)

/-- Shared backward map of classes B and C: shift the configuration so its
origin lands on the remainder's unique top cell (row `t - ℓ`), union,
re-anchor. `t` is the cluster's top row: `H-2` for class B, `H-1` for
class C. -/
noncomputable def glueTop (t : ℤ) (x : PeelData) : Finset (ℤ × ℤ) :=
  xNorm (x.2.2.2 ∪
    shift (rowCell x.2.2.2 (t - (x.2.1 : ℤ))).1 (t - (x.2.1 : ℤ)) x.2.2.1)

/-- Class-B forward map: peel the maximal cluster over rows
`[b, H-2]` (`b = clusterBottom`) together with its bracketing walk cells
(rows `b-1` and `H-1`); the configuration is based at the row-`(b-1)` walk
cell, the remainder `[0, b-1]` is re-anchored. -/
noncomputable def peelB (H : ℕ) (S : Finset (ℤ × ℤ)) : PeelData :=
  ⟨(seg S (clusterBottom S ((H : ℤ) - 2)) ((H : ℤ) - 2)).card
      - ((H : ℤ) - 1 - clusterBottom S ((H : ℤ) - 2)).toNat,
   ((H : ℤ) - 1 - clusterBottom S ((H : ℤ) - 2)).toNat,
   shift (-(rowCell S (clusterBottom S ((H : ℤ) - 2) - 1)).1)
       (-(clusterBottom S ((H : ℤ) - 2) - 1))
       (seg S (clusterBottom S ((H : ℤ) - 2) - 1) ((H : ℤ) - 1)),
   xNorm (seg S 0 (clusterBottom S ((H : ℤ) - 2) - 1))⟩

/-- Class-C forward map: as `peelB`, with the cluster reaching the top edge
(rows `[b, H-1]`), so only the bottom bracketing walk cell exists. -/
noncomputable def peelC (H : ℕ) (S : Finset (ℤ × ℤ)) : PeelData :=
  ⟨(seg S (clusterBottom S ((H : ℤ) - 1)) ((H : ℤ) - 1)).card
      - ((H : ℤ) - clusterBottom S ((H : ℤ) - 1)).toNat,
   ((H : ℤ) - clusterBottom S ((H : ℤ) - 1)).toNat,
   shift (-(rowCell S (clusterBottom S ((H : ℤ) - 1) - 1)).1)
       (-(clusterBottom S ((H : ℤ) - 1) - 1))
       (seg S (clusterBottom S ((H : ℤ) - 1) - 1) ((H : ℤ) - 1)),
   xNorm (seg S 0 (clusterBottom S ((H : ℤ) - 1) - 1))⟩

/-- The class-B target: `V`-configurations paired with walk-top remainders,
indexed by `(j, ℓ)`. -/
noncomputable def targetB (L : RowLocal) (k H : ℕ) : Finset PeelData :=
  (Finset.Icc 1 k).sigma fun j => (Finset.Icc 1 j).sigma fun ℓ =>
    CFGV L ℓ j ×ˢ Dc L (k - j) (H - 1 - ℓ)

/-- The class-C target: `Vᵗ`-configurations paired with walk-top remainders,
indexed by `(j, ℓ)`. -/
noncomputable def targetC (L : RowLocal) (k H : ℕ) : Finset PeelData :=
  (Finset.Icc 1 k).sigma fun j => (Finset.Icc 1 j).sigma fun ℓ =>
    CFGVt L ℓ j ×ˢ Dc L (k - j) (H - ℓ)

lemma xNorm_def' (S : Finset (ℤ × ℤ)) : xNorm S = shift (-minX S) 0 S := rfl

lemma seg_union (A B : Finset (ℤ × ℤ)) (a b : ℤ) :
    seg (A ∪ B) a b = seg A a b ∪ seg B a b :=
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

lemma seg_xShift (a r r' : ℤ) (S : Finset (ℤ × ℤ)) :
    seg (shift a 0 S) r r' = shift a 0 (seg S r r') := by
  rw [seg_shift, sub_zero, sub_zero]

/-- The re-anchored bottom band `[0, b-1]` of a connected animal with a walk
row at `b - 1` is a walk-top canonical animal of height `b`. Shared by all
three peeling classes. -/
lemma xNorm_seg_mem_Dc {k' H' : ℕ} {S : Finset (ℤ × ℤ)} {b : ℤ}
    (hconn : Conn L S) (hy0 : ∀ c ∈ S, 0 ≤ c.2)
    (hb : 1 ≤ b) (hHb : (H' : ℤ) = b)
    (hwb : rowSize S (b - 1) = 1)
    (h0occ : ∃ c ∈ S, c.2 = 0)
    (hcard : (seg S 0 (b - 1)).card = H' + k') :
    xNorm (seg S 0 (b - 1)) ∈ Dc L k' H' := by
  rw [mem_Dc]
  have hwr : IsWalkRow S (b - 1) := hwb
  have hconnQ : Conn L (seg S 0 (b - 1)) :=
    conn_seg hconn (Or.inr hy0) (Or.inl hwr)
  have hyQ0 : ∀ c ∈ seg S 0 (b - 1), 0 ≤ c.2 := fun c hc => (mem_seg.mp hc).2.1
  have hyQ1 : ∀ c ∈ seg S 0 (b - 1), c.2 ≤ (H' : ℤ) - 1 := by
    intro c hc
    have := (mem_seg.mp hc).2.2
    omega
  have he0 : ∃ c ∈ seg S 0 (b - 1), c.2 = 0 := by
    obtain ⟨c, hcS, hc2⟩ := h0occ
    exact ⟨c, mem_seg.mpr ⟨hcS, by omega, by omega⟩, hc2⟩
  have he1 : ∃ c ∈ seg S 0 (b - 1), c.2 = (H' : ℤ) - 1 := by
    obtain ⟨c, hcS, hc2⟩ := hwr.exists_mem
    exact ⟨c, mem_seg.mpr ⟨hcS, by omega, by omega⟩, by omega⟩
  refine ⟨isCanonical_xNorm hcard hconnQ hyQ0 hyQ1 he0 he1, ?_⟩
  rw [rowSize_xNorm, show (H' : ℤ) - 1 = b - 1 by omega, rowSize_seg (by omega) le_rfl]
  exact hwb

/-- Cluster bookkeeping for class B (`t = H - 2`, a walk row above the
cluster): bounds of `b = clusterBottom`, the walk row below the cluster, and
the three cell-count identities the bijection needs. -/
lemma clusterB_facts {k H : ℕ} (hH : k + 2 ≤ H) {S : Finset (ℤ × ℤ)}
    (hSc : IsCanonical L (H + k) H S) (hw1 : rowSize S ((H : ℤ) - 1) = 1)
    (hm : ¬ rowSize S ((H : ℤ) - 2) = 1) :
    1 ≤ clusterBottom S ((H : ℤ) - 2) ∧ clusterBottom S ((H : ℤ) - 2) ≤ (H : ℤ) - 2 ∧
    (∀ y, clusterBottom S ((H : ℤ) - 2) ≤ y → y ≤ (H : ℤ) - 2 → 2 ≤ rowSize S y) ∧
    rowSize S (clusterBottom S ((H : ℤ) - 2) - 1) = 1 ∧
    ((seg S 0 (clusterBottom S ((H : ℤ) - 2) - 1)).card
      + (seg S (clusterBottom S ((H : ℤ) - 2)) ((H : ℤ) - 2)).card + 1 = H + k) ∧
    (clusterBottom S ((H : ℤ) - 2)
      ≤ ((seg S 0 (clusterBottom S ((H : ℤ) - 2) - 1)).card : ℤ)) ∧
    (2 * ((H : ℤ) - 1 - clusterBottom S ((H : ℤ) - 2))
      ≤ ((seg S (clusterBottom S ((H : ℤ) - 2)) ((H : ℤ) - 2)).card : ℤ)) ∧
    (seg S (clusterBottom S ((H : ℤ) - 2) - 1) ((H : ℤ) - 1)).card
      = (seg S (clusterBottom S ((H : ℤ) - 2)) ((H : ℤ) - 2)).card + 2 := by
  have hocc : ∀ y, 0 ≤ y → y ≤ (H : ℤ) - 1 → 1 ≤ rowSize S y := fun y h0 h1 =>
    Finset.card_pos.mpr (canonical_fiber_nonempty hSc h0 h1)
  have hm2 : 2 ≤ rowSize S ((H : ℤ) - 2) := by
    have := hocc ((H : ℤ) - 2) (by omega) (by omega)
    omega
  obtain ⟨⟨hb0, hbt⟩, hmulti, hminle, hwalk'⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ (H : ℤ) - 2 by omega) hm2
  set b := clusterBottom S ((H : ℤ) - 2) with hb_def
  -- total cell count as a row sum
  have hself : seg S 0 ((H : ℤ) - 1) = S :=
    seg_eq_self fun p hp => ⟨hSc.2.2.2.2.1 p hp, hSc.2.2.2.2.2.2.1 p hp⟩
  have htotal : (H : ℕ) + k = ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y := by
    rw [← card_seg_sum, hself, hSc.1]
  have hsplit1 : ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y
      = (∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y)
        + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
    have h := sum_Icc_split (rowSize S) (a := 0) (b := b - 1) (c := (H : ℤ) - 1)
      (by omega) (by omega)
    simpa using h
  have hsplit2 : ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y
      = (∑ y ∈ Finset.Icc b ((H : ℤ) - 2), rowSize S y)
        + ∑ y ∈ Finset.Icc ((H : ℤ) - 1) ((H : ℤ) - 1), rowSize S y := by
    have h := sum_Icc_split (rowSize S) (a := b) (b := (H : ℤ) - 2) (c := (H : ℤ) - 1)
      (by omega) (by omega)
    rw [show (H : ℤ) - 2 + 1 = (H : ℤ) - 1 from by ring] at h
    exact h
  have htop1 : ∑ y ∈ Finset.Icc ((H : ℤ) - 1) ((H : ℤ) - 1), rowSize S y = 1 := by
    rw [Finset.Icc_self, Finset.sum_singleton]
    exact hw1
  have hn1sum : (seg S 0 (b - 1)).card = ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y :=
    card_seg_sum S 0 (b - 1)
  have hn2sum : (seg S b ((H : ℤ) - 2)).card
      = ∑ y ∈ Finset.Icc b ((H : ℤ) - 2), rowSize S y := card_seg_sum S b ((H : ℤ) - 2)
  -- per-row lower bounds
  have hn1b : (b : ℤ) ≤ ((seg S 0 (b - 1)).card : ℤ) := by
    have hle : (Finset.Icc (0 : ℤ) (b - 1)).card • 1
        ≤ ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hocc y hy.1 (by omega)
    rw [smul_eq_mul, mul_one, Int.card_Icc] at hle
    rw [hn1sum]
    omega
  have hn2l : 2 * ((H : ℤ) - 1 - b) ≤ ((seg S b ((H : ℤ) - 2)).card : ℤ) := by
    have hle : (Finset.Icc b ((H : ℤ) - 2)).card • 2
        ≤ ∑ y ∈ Finset.Icc b ((H : ℤ) - 2), rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hmulti y hy.1 hy.2
    rw [smul_eq_mul, Int.card_Icc] at hle
    rw [hn2sum]
    omega
  have hn12 : (seg S 0 (b - 1)).card + (seg S b ((H : ℤ) - 2)).card + 1 = H + k := by
    rw [hn1sum, hn2sum]
    omega
  have hb1 : 1 ≤ b := by omega
  have hwalkb : rowSize S (b - 1) = 1 := by
    have h1 := hocc (b - 1) (by omega) (by omega)
    have h2 := hwalk' hb1
    omega
  have hPcard : (seg S (b - 1) ((H : ℤ) - 1)).card
      = (seg S b ((H : ℤ) - 2)).card + 2 := by
    have hs1 : ∑ y ∈ Finset.Icc (b - 1) ((H : ℤ) - 1), rowSize S y
        = (∑ y ∈ Finset.Icc (b - 1) (b - 1), rowSize S y)
          + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
      have h := sum_Icc_split (rowSize S) (a := b - 1) (b := b - 1) (c := (H : ℤ) - 1)
        (by omega) (by omega)
      simpa using h
    rw [card_seg_sum, hs1, Finset.Icc_self, Finset.sum_singleton, hwalkb, hsplit2,
      htop1, hn2sum]
    omega
  exact ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩

/-- Cluster bookkeeping for class C (`t = H - 1`, the cluster caps the
animal). -/
lemma clusterC_facts {k H : ℕ} (hH : k + 1 ≤ H) {S : Finset (ℤ × ℤ)}
    (hSc : IsCanonical L (H + k) H S) (hm : ¬ rowSize S ((H : ℤ) - 1) = 1) :
    1 ≤ clusterBottom S ((H : ℤ) - 1) ∧ clusterBottom S ((H : ℤ) - 1) ≤ (H : ℤ) - 1 ∧
    (∀ y, clusterBottom S ((H : ℤ) - 1) ≤ y → y ≤ (H : ℤ) - 1 → 2 ≤ rowSize S y) ∧
    rowSize S (clusterBottom S ((H : ℤ) - 1) - 1) = 1 ∧
    ((seg S 0 (clusterBottom S ((H : ℤ) - 1) - 1)).card
      + (seg S (clusterBottom S ((H : ℤ) - 1)) ((H : ℤ) - 1)).card = H + k) ∧
    (clusterBottom S ((H : ℤ) - 1)
      ≤ ((seg S 0 (clusterBottom S ((H : ℤ) - 1) - 1)).card : ℤ)) ∧
    (2 * ((H : ℤ) - clusterBottom S ((H : ℤ) - 1))
      ≤ ((seg S (clusterBottom S ((H : ℤ) - 1)) ((H : ℤ) - 1)).card : ℤ)) ∧
    (seg S (clusterBottom S ((H : ℤ) - 1) - 1) ((H : ℤ) - 1)).card
      = (seg S (clusterBottom S ((H : ℤ) - 1)) ((H : ℤ) - 1)).card + 1 := by
  have hocc : ∀ y, 0 ≤ y → y ≤ (H : ℤ) - 1 → 1 ≤ rowSize S y := fun y h0 h1 =>
    Finset.card_pos.mpr (canonical_fiber_nonempty hSc h0 h1)
  have hm2 : 2 ≤ rowSize S ((H : ℤ) - 1) := by
    have := hocc ((H : ℤ) - 1) (by omega) (by omega)
    omega
  obtain ⟨⟨hb0, hbt⟩, hmulti, hminle, hwalk'⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ (H : ℤ) - 1 by omega) hm2
  set b := clusterBottom S ((H : ℤ) - 1) with hb_def
  have hself : seg S 0 ((H : ℤ) - 1) = S :=
    seg_eq_self fun p hp => ⟨hSc.2.2.2.2.1 p hp, hSc.2.2.2.2.2.2.1 p hp⟩
  have htotal : (H : ℕ) + k = ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y := by
    rw [← card_seg_sum, hself, hSc.1]
  have hsplit1 : ∑ y ∈ Finset.Icc 0 ((H : ℤ) - 1), rowSize S y
      = (∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y)
        + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
    have h := sum_Icc_split (rowSize S) (a := 0) (b := b - 1) (c := (H : ℤ) - 1)
      (by omega) (by omega)
    simpa using h
  have hn1sum : (seg S 0 (b - 1)).card = ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y :=
    card_seg_sum S 0 (b - 1)
  have hn2sum : (seg S b ((H : ℤ) - 1)).card
      = ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := card_seg_sum S b ((H : ℤ) - 1)
  have hn1b : (b : ℤ) ≤ ((seg S 0 (b - 1)).card : ℤ) := by
    have hle : (Finset.Icc (0 : ℤ) (b - 1)).card • 1
        ≤ ∑ y ∈ Finset.Icc 0 (b - 1), rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hocc y hy.1 (by omega)
    rw [smul_eq_mul, mul_one, Int.card_Icc] at hle
    rw [hn1sum]
    omega
  have hn2l : 2 * ((H : ℤ) - b) ≤ ((seg S b ((H : ℤ) - 1)).card : ℤ) := by
    have hle : (Finset.Icc b ((H : ℤ) - 1)).card • 2
        ≤ ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
      refine Finset.card_nsmul_le_sum _ _ _ fun y hy => ?_
      rw [Finset.mem_Icc] at hy
      exact hmulti y hy.1 hy.2
    rw [smul_eq_mul, Int.card_Icc] at hle
    rw [hn2sum]
    omega
  have hn12 : (seg S 0 (b - 1)).card + (seg S b ((H : ℤ) - 1)).card = H + k := by
    rw [hn1sum, hn2sum]
    omega
  have hb1 : 1 ≤ b := by omega
  have hwalkb : rowSize S (b - 1) = 1 := by
    have h1 := hocc (b - 1) (by omega) (by omega)
    have h2 := hwalk' hb1
    omega
  have hPcard : (seg S (b - 1) ((H : ℤ) - 1)).card
      = (seg S b ((H : ℤ) - 1)).card + 1 := by
    have hs1 : ∑ y ∈ Finset.Icc (b - 1) ((H : ℤ) - 1), rowSize S y
        = (∑ y ∈ Finset.Icc (b - 1) (b - 1), rowSize S y)
          + ∑ y ∈ Finset.Icc b ((H : ℤ) - 1), rowSize S y := by
      have h := sum_Icc_split (rowSize S) (a := b - 1) (b := b - 1) (c := (H : ℤ) - 1)
        (by omega) (by omega)
      simpa using h
    rw [card_seg_sum, hs1, Finset.Icc_self, Finset.sum_singleton, hwalkb, hn2sum]
    omega
  exact ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩

/-- Forward well-definedness and the peel-then-glue round trip for class B. -/
lemma peelB_mem_and_glue {k H : ℕ} (hH : k + 2 ≤ H) {S : Finset (ℤ × ℤ)}
    (hS : S ∈ Dc L k H) (hm : ¬ rowSize S ((H : ℤ) - 2) = 1) :
    peelB H S ∈ targetB L k H ∧ glueTop ((H : ℤ) - 2) (peelB H S) = S := by
  obtain ⟨hc, hw1⟩ := mem_Dc.mp hS
  obtain ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩ :=
    clusterB_facts hH hc hw1 hm
  simp only [peelB, glueTop]
  set b := clusterBottom S ((H : ℤ) - 2) with hb_def
  set ln := ((H : ℤ) - 1 - b).toNat with hln_def
  set jn := (seg S b ((H : ℤ) - 2)).card - ln with hjn_def
  set p := rowCell S (b - 1) with hp_def
  have hlz : (ln : ℤ) = (H : ℤ) - 1 - b := by omega
  have hln1 : 1 ≤ ln := by omega
  have hlnn2 : ln ≤ (seg S b ((H : ℤ) - 2)).card := by omega
  have hwrb : IsWalkRow S (b - 1) := hwalkb
  have hpS : p ∈ S := rowCell_mem hwrb
  have hpy : p.2 = b - 1 := rfl
  have hpP : p ∈ seg S (b - 1) ((H : ℤ) - 1) :=
    mem_seg.mpr ⟨hpS, by omega, by omega⟩
  -- the peeled configuration is a V-configuration
  have hPconn : Conn L (seg S (b - 1) ((H : ℤ) - 1)) :=
    conn_seg hc.2.1 (Or.inl hwrb) (Or.inr hc.2.2.2.2.2.2.1)
  have hC0card :
      (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))).card = ln + jn + 2 := by
    rw [card_shift, hPcard]
    omega
  have h00 : ((0 : ℤ), (0 : ℤ)) ∈ shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)) := by
    have h := shift_mem (a := -p.1) (b := -(b - 1)) hpP
    rwa [shiftCell_to_origin hpy] at h
  have hC0rows : ∀ c ∈ shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)),
      0 ≤ c.2 ∧ c.2 ≤ (ln : ℤ) + 1 := by
    intro c hcm
    rw [mem_shift, mem_seg] at hcm
    have h1 : b - 1 ≤ c.2 - -(b - 1) := hcm.2.1
    have h2 : c.2 - -(b - 1) ≤ (H : ℤ) - 1 := hcm.2.2
    omega
  have hC0rs : ∀ y : ℤ, 0 ≤ y → y ≤ (ln : ℤ) + 1 →
      rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) y
        = rowSize S (y + (b - 1)) := by
    intro y h0 h1
    rw [rowSize_shift, rowSize_seg (by omega) (by omega)]
    congr 1
    ring
  have hC0r0 : rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) 0 = 1 := by
    rw [hC0rs 0 le_rfl (by omega), show (0 : ℤ) + (b - 1) = b - 1 from by ring]
    exact hwalkb
  have hC0rtop :
      rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) ((ln : ℤ) + 1) = 1 := by
    rw [hC0rs _ (by omega) le_rfl, show (ln : ℤ) + 1 + (b - 1) = (H : ℤ) - 1 from by omega]
    exact hw1
  have hC0multi : ∀ i ∈ Finset.Icc 1 ln,
      2 ≤ rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) (i : ℤ) := by
    intro i hi
    rw [Finset.mem_Icc] at hi
    rw [hC0rs _ (by omega) (by omega)]
    exact hmulti _ (by omega) (by omega)
  have hC0V : shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)) ∈ CFGV L ln jn := by
    rw [mem_CFGV]
    exact ⟨hC0card, h00, hC0rows, hC0r0, hC0rtop, hC0multi,
      conn_shift _ _ hPconn⟩
  -- the re-anchored remainder is a shorter walk-top animal
  have hR0 : xNorm (seg S 0 (b - 1)) ∈ Dc L (k - jn) (H - 1 - ln) := by
    refine xNorm_seg_mem_Dc hc.2.1 hc.2.2.2.2.1 hb1 (by omega) hwalkb
      hc.2.2.2.2.2.1 (by omega)
  clear_value jn ln
  have hjmem : jn ∈ Finset.Icc 1 k := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have hlmem : ln ∈ Finset.Icc 1 jn := Finset.mem_Icc.mpr ⟨hln1, by omega⟩
  constructor
  · exact Finset.mem_sigma.mpr ⟨hjmem, Finset.mem_sigma.mpr ⟨hlmem,
      Finset.mem_product.mpr ⟨hC0V, hR0⟩⟩⟩
  -- the round trip: glue the peeled pieces back
  · have hSne : S.Nonempty := by
      obtain ⟨z, hzS, -⟩ := hc.2.2.2.2.2.1
      exact ⟨z, hzS⟩
    have hr : (H : ℤ) - 2 - (ln : ℤ) = b - 1 := by omega
    have hwQ : IsWalkRow (xNorm (seg S 0 (b - 1))) (b - 1) := by
      rw [isWalkRow_iff_rowSize, rowSize_xNorm, rowSize_seg (by omega) le_rfl]
      exact hwalkb
    have hpQ : p ∈ seg S 0 (b - 1) := mem_seg.mpr ⟨hpS, by omega, le_of_eq hpy⟩
    have hu' : rowCell (xNorm (seg S 0 (b - 1))) (b - 1)
        = shiftCell (-minX (seg S 0 (b - 1))) 0 p := by
      refine rowCell_eq hwQ ?_ ?_
      · rw [xNorm_def']
        exact shift_mem hpQ
      · change p.2 + 0 = b - 1
        rw [hpy]
        ring
    have hQP : seg S 0 (b - 1) ∪ seg S (b - 1) ((H : ℤ) - 1) = S := by
      ext c
      simp only [Finset.mem_union, mem_seg]
      constructor
      · rintro (⟨h, -, -⟩ | ⟨h, -, -⟩) <;> exact h
      · intro hcS
        have h0 := hc.2.2.2.2.1 c hcS
        have h1 := hc.2.2.2.2.2.2.1 c hcS
        by_cases hcb : c.2 ≤ b - 1
        · exact Or.inl ⟨hcS, h0, hcb⟩
        · exact Or.inr ⟨hcS, by omega, h1⟩
    rw [hr, hu',
      show (shiftCell (-minX (seg S 0 (b - 1))) 0 p).1
        = p.1 + -minX (seg S 0 (b - 1)) from rfl,
      shift_shift,
      show p.1 + -minX (seg S 0 (b - 1)) + -p.1 = -minX (seg S 0 (b - 1)) from by ring,
      show b - 1 + -(b - 1) = (0 : ℤ) from by ring,
      xNorm_def' (seg S 0 (b - 1)), ← shift_union, hQP, xNorm_shift _ hSne,
      xNorm_eq_self hc.2.2.1 hc.2.2.2.1]

/-- Backward well-definedness and the glue-then-peel round trip for class B. -/
lemma glueB_mem_and_peel {k H : ℕ} (hH : k + 2 ≤ H) {x : PeelData}
    (hx : x ∈ targetB L k H) :
    (glueTop ((H : ℤ) - 2) x ∈ Dc L k H ∧
      ¬ rowSize (glueTop ((H : ℤ) - 2) x) ((H : ℤ) - 2) = 1) ∧
    peelB H (glueTop ((H : ℤ) - 2) x) = x := by
  obtain ⟨j, ℓ, C, R⟩ := x
  rw [targetB, Finset.mem_sigma, Finset.mem_sigma, Finset.mem_product] at hx
  have hjm : j ∈ Finset.Icc 1 k := hx.1
  have hlm : ℓ ∈ Finset.Icc 1 j := hx.2.1
  have hCm : C ∈ CFGV L ℓ j := hx.2.2.1
  have hRm : R ∈ Dc L (k - j) (H - 1 - ℓ) := hx.2.2.2
  rw [Finset.mem_Icc] at hjm hlm
  obtain ⟨hj1, hjk⟩ := hjm
  obtain ⟨hl1, hlj⟩ := hlm
  have hCv : IsVConfig L ℓ j C := mem_CFGV.mp hCm
  obtain ⟨hcR, hwR⟩ := mem_Dc.mp hRm
  simp only [glueTop, peelB]
  set r := (H : ℤ) - 2 - (ℓ : ℤ) with hr_def
  have hwRr : IsWalkRow R r := by
    rw [isWalkRow_iff_rowSize, show r = ((H - 1 - ℓ : ℕ) : ℤ) - 1 from by omega]
    exact hwR
  set u := rowCell R r with hu_def
  have huR : u ∈ R := rowCell_mem hwRr
  have huy : u.2 = r := rfl
  set C' := shift u.1 r C with hC'_def
  have hRrows : ∀ c ∈ R, 0 ≤ c.2 ∧ c.2 ≤ r := by
    intro c hcm
    have h1 := hcR.2.2.2.2.1 c hcm
    have h2 := hcR.2.2.2.2.2.2.1 c hcm
    omega
  have hCrows := hCv.2.2.1
  have hC'rows : ∀ c ∈ C', r ≤ c.2 ∧ c.2 ≤ (H : ℤ) - 1 := by
    intro c hcm
    rw [hC'_def, mem_shift] at hcm
    have h1 : 0 ≤ c.2 - r := (hCrows _ hcm).1
    have h2 : c.2 - r ≤ (ℓ : ℤ) + 1 := (hCrows _ hcm).2
    omega
  have huC' : u ∈ C' := by
    have h0 := shift_mem (a := u.1) (b := r) hCv.2.1
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
    have hC'c : C'.card = ℓ + j + 2 := by
      rw [hC'_def, card_shift]
      exact hCv.1
    have hRc : R.card = (H - 1 - ℓ) + (k - j) := hcR.1
    omega
  have hC'conn : Conn L C' := by
    rw [hC'_def]
    exact conn_shift _ _ hCv.2.2.2.2.2.2
  have hconnU : Conn L (R ∪ C') :=
    conn_union rfl hcR.2.1 hC'conn ⟨u, Finset.mem_inter.mpr ⟨huR, huC'⟩⟩
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
    obtain ⟨z, hzR, hzy⟩ := hcR.2.2.2.2.2.1
    exact ⟨z, Finset.mem_union_left _ hzR, hzy⟩
  have hUe1 : ∃ c ∈ R ∪ C', c.2 = (H : ℤ) - 1 := by
    have hwtop : IsWalkRow C ((ℓ : ℤ) + 1) := hCv.2.2.2.2.1
    obtain ⟨c0, hc0C, hc0y⟩ := hwtop.exists_mem
    refine ⟨shiftCell u.1 r c0, Finset.mem_union_right _ ?_, ?_⟩
    · rw [hC'_def]
      exact shift_mem hc0C
    · change c0.2 + r = (H : ℤ) - 1
      omega
  have hrsAbove : ∀ y : ℤ, r < y → rowSize (R ∪ C') y = rowSize C (y - r) := by
    intro y hy
    rw [rowSize_union_right fun c hcm => by have := (hRrows c hcm).2; omega,
      hC'_def, rowSize_shift]
  have hG₀top : rowSize (R ∪ C') ((H : ℤ) - 1) = 1 := by
    rw [hrsAbove _ (by omega), show (H : ℤ) - 1 - r = (ℓ : ℤ) + 1 from by omega]
    exact hCv.2.2.2.2.1
  have hG₀m : 2 ≤ rowSize (R ∪ C') ((H : ℤ) - 2) := by
    rw [hrsAbove _ (by omega), show (H : ℤ) - 2 - r = (ℓ : ℤ) from by omega]
    exact hCv.2.2.2.2.2.1 ℓ (Finset.mem_Icc.mpr ⟨hl1, le_rfl⟩)
  have hwC'r : IsWalkRow C' r := by
    rw [isWalkRow_iff_rowSize, hC'_def, rowSize_shift, sub_self]
    exact hCv.2.2.2.1
  have hG₀r : rowSize (R ∪ C') r = 1 := by
    rw [rowSize, Finset.filter_union, filter_row_eq_singleton hwRr huR huy,
      filter_row_eq_singleton hwC'r huC' huy, Finset.union_self]
    exact Finset.card_singleton u
  have hDc : xNorm (R ∪ C') ∈ Dc L k H := by
    rw [mem_Dc]
    refine ⟨isCanonical_xNorm hcardU hconnU hUy0 hUy1 hUe0 hUe1, ?_⟩
    rw [rowSize_xNorm]
    exact hG₀top
  have hnot : ¬ rowSize (xNorm (R ∪ C')) ((H : ℤ) - 2) = 1 := by
    rw [rowSize_xNorm]
    omega
  refine ⟨⟨hDc, hnot⟩, ?_⟩
  -- the round trip: peel the glued animal back apart
  have hRne : R.Nonempty := by
    obtain ⟨z, hzR, -⟩ := hcR.2.2.2.2.2.1
    exact ⟨z, hzR⟩
  -- the recomputed cluster bottom is `r + 1`
  have hm2X : 2 ≤ rowSize (xNorm (R ∪ C')) ((H : ℤ) - 2) := by
    rw [rowSize_xNorm]
    exact hG₀m
  obtain ⟨⟨hb0', hbt'⟩, hmulti', hminle', -⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ (H : ℤ) - 2 from by omega) hm2X
  have hble : clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 2) ≤ r + 1 := by
    refine hminle' (r + 1) (by omega) (by omega) ?_
    intro y hy1 hy2
    rw [rowSize_xNorm, hrsAbove y (by omega),
      show y - r = (((y - r).toNat : ℕ) : ℤ) from by omega]
    exact hCv.2.2.2.2.2.1 _ (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
  have hbgt : r < clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 2) := by
    by_contra hcon
    push Not at hcon
    have h2 := hmulti' r hcon (by omega)
    rw [rowSize_xNorm, hG₀r] at h2
    omega
  have hbeq : clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 2) = r + 1 := by omega
  -- the interior cluster band of the configuration
  have hsegRempty : seg R (r + 1) ((H : ℤ) - 2) = ∅ := by
    rw [seg, Finset.filter_eq_empty_iff]
    intro c hcm
    have := (hRrows c hcm).2
    omega
  have hsegC' : seg C' (r + 1) ((H : ℤ) - 2) = shift u.1 r (seg C 1 (ℓ : ℤ)) := by
    rw [hC'_def, seg_shift, show r + 1 - r = (1 : ℤ) from by ring,
      show (H : ℤ) - 2 - r = (ℓ : ℤ) from by omega]
  have hCcard : (seg C 1 (ℓ : ℤ)).card = ℓ + j := by
    have hCself : seg C 0 ((ℓ : ℤ) + 1) = C := seg_eq_self hCrows
    have h1 := card_seg_sum C 0 ((ℓ : ℤ) + 1)
    have h2 := card_seg_sum C 1 (ℓ : ℤ)
    have hs1 : ∑ y ∈ Finset.Icc (0 : ℤ) ((ℓ : ℤ) + 1), rowSize C y
        = (∑ y ∈ Finset.Icc (0 : ℤ) 0, rowSize C y)
          + ∑ y ∈ Finset.Icc (1 : ℤ) ((ℓ : ℤ) + 1), rowSize C y := by
      have h := sum_Icc_split (rowSize C) (a := (0 : ℤ)) (b := 0) (c := (ℓ : ℤ) + 1)
        (by omega) (by omega)
      rwa [show (0 : ℤ) + 1 = 1 from by ring] at h
    have hs2 : ∑ y ∈ Finset.Icc (1 : ℤ) ((ℓ : ℤ) + 1), rowSize C y
        = (∑ y ∈ Finset.Icc (1 : ℤ) (ℓ : ℤ), rowSize C y)
          + ∑ y ∈ Finset.Icc ((ℓ : ℤ) + 1) ((ℓ : ℤ) + 1), rowSize C y :=
      sum_Icc_split (rowSize C) (by omega) (by omega)
    rw [hCself] at h1
    rw [show Finset.Icc (0 : ℤ) 0 = {(0 : ℤ)} from Finset.Icc_self 0,
      Finset.sum_singleton] at hs1
    rw [show Finset.Icc ((ℓ : ℤ) + 1) ((ℓ : ℤ) + 1) = {((ℓ : ℤ) + 1)} from
      Finset.Icc_self _, Finset.sum_singleton] at hs2
    have hr0' : rowSize C 0 = 1 := hCv.2.2.2.1
    have hrt' : rowSize C ((ℓ : ℤ) + 1) = 1 := hCv.2.2.2.2.1
    have hCcardv : C.card = ℓ + j + 2 := hCv.1
    omega
  -- the walk cell of the recomputed base row
  have hcellX : rowCell (xNorm (R ∪ C')) r = shiftCell (-minX (R ∪ C')) 0 u := by
    refine rowCell_eq ?_ ?_ ?_
    · rw [isWalkRow_iff_rowSize, rowSize_xNorm]
      exact hG₀r
    · rw [xNorm_def']
      exact shift_mem (Finset.mem_union_left _ huR)
    · change u.2 + 0 = r
      omega
  have hsegtopX : seg (xNorm (R ∪ C')) r ((H : ℤ) - 1)
      = shift (-minX (R ∪ C')) 0 C' := by
    rw [xNorm_def', seg_xShift]
    congr 1
    rw [seg_union]
    have h1 : seg R r ((H : ℤ) - 1) = {u} := by
      ext c
      rw [mem_seg, Finset.mem_singleton]
      constructor
      · rintro ⟨hcR', h1', -⟩
        exact hwRr.eq_of_mem hcR' (le_antisymm (hRrows c hcR').2 h1') huR huy
      · rintro rfl
        exact ⟨huR, le_of_eq huy.symm, by omega⟩
    have h2 : seg C' r ((H : ℤ) - 1) = C' := seg_eq_self fun c hcm => hC'rows c hcm
    rw [h1, h2]
    exact Finset.union_eq_right.mpr (Finset.singleton_subset_iff.mpr huC')
  have hsegbotX : seg (xNorm (R ∪ C')) 0 r = shift (-minX (R ∪ C')) 0 R := by
    rw [xNorm_def', seg_xShift]
    congr 1
    rw [seg_union]
    have h1 : seg R 0 r = R := seg_eq_self fun c hcm => hRrows c hcm
    have h2 : seg C' 0 r = {u} := by
      ext c
      rw [mem_seg, Finset.mem_singleton]
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
    rw [xNorm_def', seg_xShift, seg_union, hsegRempty, Finset.empty_union, hsegC',
      card_shift, card_shift, hCcard]
    omega
  · -- the configuration component
    rw [hcellX, hsegtopX,
      show (shiftCell (-minX (R ∪ C')) 0 u).1 = u.1 + -minX (R ∪ C') from rfl,
      shift_shift, hC'_def, shift_shift,
      show -(u.1 + -minX (R ∪ C')) + -minX (R ∪ C') + u.1 = (0 : ℤ) from by ring,
      show -r + 0 + r = (0 : ℤ) from by ring, shift_zero]
  · -- the remainder component
    rw [hsegbotX, xNorm_shift _ hRne, xNorm_eq_self hcR.2.2.1 hcR.2.2.2.1]

/-- **Class-B count**: walk-top animals with a multi second-top row are
counted by interior cluster configurations times shorter walk-top remainders,
aggregated over `(j, ℓ)`. -/
lemma card_classB (k H : ℕ) (hH : k + 2 ≤ H) :
    ((Dc L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 2) = 1).card =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V L ℓ j * d L (k - j) (H - 1 - ℓ) := by
  have htarget : (targetB L k H).card = ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
      V L ℓ j * d L (k - j) (H - 1 - ℓ) := by
    rw [targetB, Finset.card_sigma]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [Finset.card_sigma]
    exact Finset.sum_congr rfl fun ℓ _ => by rw [Finset.card_product]; rfl
  rw [← htarget]
  refine Finset.card_nbij' (peelB H) (glueTop ((H : ℤ) - 2)) ?_ ?_ ?_ ?_
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    rw [Finset.mem_coe]
    exact (peelB_mem_and_glue hH hS.1 hS.2).1
  · intro x hx
    rw [Finset.mem_coe] at hx
    rw [Finset.mem_coe, Finset.mem_filter]
    exact (glueB_mem_and_peel hH hx).1
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    exact (peelB_mem_and_glue hH hS.1 hS.2).2
  · intro x hx
    rw [Finset.mem_coe] at hx
    exact (glueB_mem_and_peel hH hx).2

/-! ## Class C -/

/-- Forward well-definedness and the peel-then-glue round trip for class C. -/
lemma peelC_mem_and_glue {k H : ℕ} (hH : k + 1 ≤ H) {S : Finset (ℤ × ℤ)}
    (hS : S ∈ allCanon L k H) (hm : ¬ rowSize S ((H : ℤ) - 1) = 1) :
    peelC H S ∈ targetC L k H ∧ glueTop ((H : ℤ) - 1) (peelC H S) = S := by
  have hc := mem_allCanon.mp hS
  obtain ⟨hb1, hbt, hmulti, hwalkb, hn12, hn1b, hn2l, hPcard⟩ :=
    clusterC_facts hH hc hm
  simp only [peelC, glueTop]
  set b := clusterBottom S ((H : ℤ) - 1) with hb_def
  set ln := ((H : ℤ) - b).toNat with hln_def
  set jn := (seg S b ((H : ℤ) - 1)).card - ln with hjn_def
  set p := rowCell S (b - 1) with hp_def
  have hlz : (ln : ℤ) = (H : ℤ) - b := by omega
  have hln1 : 1 ≤ ln := by omega
  have hlnn2 : ln ≤ (seg S b ((H : ℤ) - 1)).card := by omega
  have hwrb : IsWalkRow S (b - 1) := hwalkb
  have hpS : p ∈ S := rowCell_mem hwrb
  have hpy : p.2 = b - 1 := rfl
  have hpP : p ∈ seg S (b - 1) ((H : ℤ) - 1) :=
    mem_seg.mpr ⟨hpS, by omega, by omega⟩
  have hPconn : Conn L (seg S (b - 1) ((H : ℤ) - 1)) :=
    conn_seg hc.2.1 (Or.inl hwrb) (Or.inr hc.2.2.2.2.2.2.1)
  have hC0card :
      (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))).card = ln + jn + 1 := by
    rw [card_shift, hPcard]
    omega
  have h00 : ((0 : ℤ), (0 : ℤ)) ∈ shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)) := by
    have h := shift_mem (a := -p.1) (b := -(b - 1)) hpP
    rwa [shiftCell_to_origin hpy] at h
  have hC0rows : ∀ c ∈ shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)),
      0 ≤ c.2 ∧ c.2 ≤ (ln : ℤ) := by
    intro c hcm
    rw [mem_shift, mem_seg] at hcm
    have h1 : b - 1 ≤ c.2 - -(b - 1) := hcm.2.1
    have h2 : c.2 - -(b - 1) ≤ (H : ℤ) - 1 := hcm.2.2
    omega
  have hC0rs : ∀ y : ℤ, 0 ≤ y → y ≤ (ln : ℤ) →
      rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) y
        = rowSize S (y + (b - 1)) := by
    intro y h0 h1
    rw [rowSize_shift, rowSize_seg (by omega) (by omega)]
    congr 1
    ring
  have hC0r0 : rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) 0 = 1 := by
    rw [hC0rs 0 le_rfl (by omega), show (0 : ℤ) + (b - 1) = b - 1 from by ring]
    exact hwalkb
  have hC0multi : ∀ i ∈ Finset.Icc 1 ln,
      2 ≤ rowSize (shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1))) (i : ℤ) := by
    intro i hi
    rw [Finset.mem_Icc] at hi
    rw [hC0rs _ (by omega) (by omega)]
    exact hmulti _ (by omega) (by omega)
  have hC0V : shift (-p.1) (-(b - 1)) (seg S (b - 1) ((H : ℤ) - 1)) ∈ CFGVt L ln jn := by
    rw [mem_CFGVt]
    exact ⟨hC0card, h00, hC0rows, hC0r0, hC0multi, conn_shift _ _ hPconn⟩
  have hR0 : xNorm (seg S 0 (b - 1)) ∈ Dc L (k - jn) (H - ln) := by
    refine xNorm_seg_mem_Dc hc.2.1 hc.2.2.2.2.1 hb1 (by omega) hwalkb
      hc.2.2.2.2.2.1 (by omega)
  clear_value jn ln
  have hjmem : jn ∈ Finset.Icc 1 k := Finset.mem_Icc.mpr ⟨by omega, by omega⟩
  have hlmem : ln ∈ Finset.Icc 1 jn := Finset.mem_Icc.mpr ⟨hln1, by omega⟩
  constructor
  · exact Finset.mem_sigma.mpr ⟨hjmem, Finset.mem_sigma.mpr ⟨hlmem,
      Finset.mem_product.mpr ⟨hC0V, hR0⟩⟩⟩
  · have hSne : S.Nonempty := by
      obtain ⟨z, hzS, -⟩ := hc.2.2.2.2.2.1
      exact ⟨z, hzS⟩
    have hr : (H : ℤ) - 1 - (ln : ℤ) = b - 1 := by omega
    have hwQ : IsWalkRow (xNorm (seg S 0 (b - 1))) (b - 1) := by
      rw [isWalkRow_iff_rowSize, rowSize_xNorm, rowSize_seg (by omega) le_rfl]
      exact hwalkb
    have hpQ : p ∈ seg S 0 (b - 1) := mem_seg.mpr ⟨hpS, by omega, le_of_eq hpy⟩
    have hu' : rowCell (xNorm (seg S 0 (b - 1))) (b - 1)
        = shiftCell (-minX (seg S 0 (b - 1))) 0 p := by
      refine rowCell_eq hwQ ?_ ?_
      · rw [xNorm_def']
        exact shift_mem hpQ
      · change p.2 + 0 = b - 1
        rw [hpy]
        ring
    have hQP : seg S 0 (b - 1) ∪ seg S (b - 1) ((H : ℤ) - 1) = S := by
      ext c
      simp only [Finset.mem_union, mem_seg]
      constructor
      · rintro (⟨h, -, -⟩ | ⟨h, -, -⟩) <;> exact h
      · intro hcS
        have h0 := hc.2.2.2.2.1 c hcS
        have h1 := hc.2.2.2.2.2.2.1 c hcS
        by_cases hcb : c.2 ≤ b - 1
        · exact Or.inl ⟨hcS, h0, hcb⟩
        · exact Or.inr ⟨hcS, by omega, h1⟩
    rw [hr, hu',
      show (shiftCell (-minX (seg S 0 (b - 1))) 0 p).1
        = p.1 + -minX (seg S 0 (b - 1)) from rfl,
      shift_shift,
      show p.1 + -minX (seg S 0 (b - 1)) + -p.1 = -minX (seg S 0 (b - 1)) from by ring,
      show b - 1 + -(b - 1) = (0 : ℤ) from by ring,
      xNorm_def' (seg S 0 (b - 1)), ← shift_union, hQP, xNorm_shift _ hSne,
      xNorm_eq_self hc.2.2.1 hc.2.2.2.1]

/-- Backward well-definedness and the glue-then-peel round trip for class C. -/
lemma glueC_mem_and_peel {k H : ℕ} (hH : k + 1 ≤ H) {x : PeelData}
    (hx : x ∈ targetC L k H) :
    (glueTop ((H : ℤ) - 1) x ∈ allCanon L k H ∧
      ¬ rowSize (glueTop ((H : ℤ) - 1) x) ((H : ℤ) - 1) = 1) ∧
    peelC H (glueTop ((H : ℤ) - 1) x) = x := by
  obtain ⟨j, ℓ, C, R⟩ := x
  rw [targetC, Finset.mem_sigma, Finset.mem_sigma, Finset.mem_product] at hx
  have hjm : j ∈ Finset.Icc 1 k := hx.1
  have hlm : ℓ ∈ Finset.Icc 1 j := hx.2.1
  have hCm : C ∈ CFGVt L ℓ j := hx.2.2.1
  have hRm : R ∈ Dc L (k - j) (H - ℓ) := hx.2.2.2
  rw [Finset.mem_Icc] at hjm hlm
  obtain ⟨hj1, hjk⟩ := hjm
  obtain ⟨hl1, hlj⟩ := hlm
  have hCv : IsVtConfig L ℓ j C := mem_CFGVt.mp hCm
  obtain ⟨hcR, hwR⟩ := mem_Dc.mp hRm
  simp only [glueTop, peelC]
  set r := (H : ℤ) - 1 - (ℓ : ℤ) with hr_def
  have hwRr : IsWalkRow R r := by
    rw [isWalkRow_iff_rowSize, show r = ((H - ℓ : ℕ) : ℤ) - 1 from by omega]
    exact hwR
  set u := rowCell R r with hu_def
  have huR : u ∈ R := rowCell_mem hwRr
  have huy : u.2 = r := rfl
  set C' := shift u.1 r C with hC'_def
  have hRrows : ∀ c ∈ R, 0 ≤ c.2 ∧ c.2 ≤ r := by
    intro c hcm
    have h1 := hcR.2.2.2.2.1 c hcm
    have h2 := hcR.2.2.2.2.2.2.1 c hcm
    omega
  have hCrows := hCv.2.2.1
  have hC'rows : ∀ c ∈ C', r ≤ c.2 ∧ c.2 ≤ (H : ℤ) - 1 := by
    intro c hcm
    rw [hC'_def, mem_shift] at hcm
    have h1 : 0 ≤ c.2 - r := (hCrows _ hcm).1
    have h2 : c.2 - r ≤ (ℓ : ℤ) := (hCrows _ hcm).2
    omega
  have huC' : u ∈ C' := by
    have h0 := shift_mem (a := u.1) (b := r) hCv.2.1
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
    have hC'c : C'.card = ℓ + j + 1 := by
      rw [hC'_def, card_shift]
      exact hCv.1
    have hRc : R.card = (H - ℓ) + (k - j) := hcR.1
    omega
  have hC'conn : Conn L C' := by
    rw [hC'_def]
    exact conn_shift _ _ hCv.2.2.2.2.2
  have hconnU : Conn L (R ∪ C') :=
    conn_union rfl hcR.2.1 hC'conn ⟨u, Finset.mem_inter.mpr ⟨huR, huC'⟩⟩
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
    obtain ⟨z, hzR, hzy⟩ := hcR.2.2.2.2.2.1
    exact ⟨z, Finset.mem_union_left _ hzR, hzy⟩
  have hCtop : 2 ≤ rowSize C (ℓ : ℤ) :=
    hCv.2.2.2.2.1 ℓ (Finset.mem_Icc.mpr ⟨hl1, le_rfl⟩)
  have hUe1 : ∃ c ∈ R ∪ C', c.2 = (H : ℤ) - 1 := by
    have hpos : 0 < (C.filter fun c => c.2 = (ℓ : ℤ)).card := by
      have h2 : 2 ≤ (C.filter fun c => c.2 = (ℓ : ℤ)).card := hCtop
      omega
    obtain ⟨c0, hc0f⟩ := Finset.card_pos.mp hpos
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
  have hG₀m : 2 ≤ rowSize (R ∪ C') ((H : ℤ) - 1) := by
    rw [hrsAbove _ (by omega), show (H : ℤ) - 1 - r = (ℓ : ℤ) from by omega]
    exact hCtop
  have hwC'r : IsWalkRow C' r := by
    rw [isWalkRow_iff_rowSize, hC'_def, rowSize_shift, sub_self]
    exact hCv.2.2.2.1
  have hG₀r : rowSize (R ∪ C') r = 1 := by
    rw [rowSize, Finset.filter_union, filter_row_eq_singleton hwRr huR huy,
      filter_row_eq_singleton hwC'r huC' huy, Finset.union_self]
    exact Finset.card_singleton u
  have hAll : xNorm (R ∪ C') ∈ allCanon L k H :=
    mem_allCanon.mpr (isCanonical_xNorm hcardU hconnU hUy0 hUy1 hUe0 hUe1)
  have hnot : ¬ rowSize (xNorm (R ∪ C')) ((H : ℤ) - 1) = 1 := by
    rw [rowSize_xNorm]
    omega
  refine ⟨⟨hAll, hnot⟩, ?_⟩
  have hRne : R.Nonempty := by
    obtain ⟨z, hzR, -⟩ := hcR.2.2.2.2.2.1
    exact ⟨z, hzR⟩
  have hm2X : 2 ≤ rowSize (xNorm (R ∪ C')) ((H : ℤ) - 1) := by
    rw [rowSize_xNorm]
    exact hG₀m
  obtain ⟨⟨hb0', hbt'⟩, hmulti', hminle', -⟩ :=
    clusterBottom_spec (show (0 : ℤ) ≤ (H : ℤ) - 1 from by omega) hm2X
  have hble : clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 1) ≤ r + 1 := by
    refine hminle' (r + 1) (by omega) (by omega) ?_
    intro y hy1 hy2
    rw [rowSize_xNorm, hrsAbove y (by omega),
      show y - r = (((y - r).toNat : ℕ) : ℤ) from by omega]
    exact hCv.2.2.2.2.1 _ (Finset.mem_Icc.mpr ⟨by omega, by omega⟩)
  have hbgt : r < clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 1) := by
    by_contra hcon
    push Not at hcon
    have h2 := hmulti' r hcon (by omega)
    rw [rowSize_xNorm, hG₀r] at h2
    omega
  have hbeq : clusterBottom (xNorm (R ∪ C')) ((H : ℤ) - 1) = r + 1 := by omega
  have hsegRempty : seg R (r + 1) ((H : ℤ) - 1) = ∅ := by
    rw [seg, Finset.filter_eq_empty_iff]
    intro c hcm
    have := (hRrows c hcm).2
    omega
  have hsegC' : seg C' (r + 1) ((H : ℤ) - 1) = shift u.1 r (seg C 1 (ℓ : ℤ)) := by
    rw [hC'_def, seg_shift, show r + 1 - r = (1 : ℤ) from by ring,
      show (H : ℤ) - 1 - r = (ℓ : ℤ) from by omega]
  have hCcard : (seg C 1 (ℓ : ℤ)).card = ℓ + j := by
    have hCself : seg C 0 (ℓ : ℤ) = C := seg_eq_self hCrows
    have h1 := card_seg_sum C 0 (ℓ : ℤ)
    have h2 := card_seg_sum C 1 (ℓ : ℤ)
    have hs1 : ∑ y ∈ Finset.Icc (0 : ℤ) (ℓ : ℤ), rowSize C y
        = (∑ y ∈ Finset.Icc (0 : ℤ) 0, rowSize C y)
          + ∑ y ∈ Finset.Icc (1 : ℤ) (ℓ : ℤ), rowSize C y := by
      have h := sum_Icc_split (rowSize C) (a := (0 : ℤ)) (b := 0) (c := (ℓ : ℤ))
        (by omega) (by omega)
      rwa [show (0 : ℤ) + 1 = 1 from by ring] at h
    rw [hCself] at h1
    rw [show Finset.Icc (0 : ℤ) 0 = {(0 : ℤ)} from Finset.Icc_self 0,
      Finset.sum_singleton] at hs1
    have hr0' : rowSize C 0 = 1 := hCv.2.2.2.1
    have hCcardv : C.card = ℓ + j + 1 := hCv.1
    omega
  have hcellX : rowCell (xNorm (R ∪ C')) r = shiftCell (-minX (R ∪ C')) 0 u := by
    refine rowCell_eq ?_ ?_ ?_
    · rw [isWalkRow_iff_rowSize, rowSize_xNorm]
      exact hG₀r
    · rw [xNorm_def']
      exact shift_mem (Finset.mem_union_left _ huR)
    · change u.2 + 0 = r
      omega
  have hsegtopX : seg (xNorm (R ∪ C')) r ((H : ℤ) - 1)
      = shift (-minX (R ∪ C')) 0 C' := by
    rw [xNorm_def', seg_xShift]
    congr 1
    rw [seg_union]
    have h1 : seg R r ((H : ℤ) - 1) = {u} := by
      ext c
      rw [mem_seg, Finset.mem_singleton]
      constructor
      · rintro ⟨hcR', h1', -⟩
        exact hwRr.eq_of_mem hcR' (le_antisymm (hRrows c hcR').2 h1') huR huy
      · rintro rfl
        exact ⟨huR, le_of_eq huy.symm, by omega⟩
    have h2 : seg C' r ((H : ℤ) - 1) = C' := seg_eq_self fun c hcm => hC'rows c hcm
    rw [h1, h2]
    exact Finset.union_eq_right.mpr (Finset.singleton_subset_iff.mpr huC')
  have hsegbotX : seg (xNorm (R ∪ C')) 0 r = shift (-minX (R ∪ C')) 0 R := by
    rw [xNorm_def', seg_xShift]
    congr 1
    rw [seg_union]
    have h1 : seg R 0 r = R := seg_eq_self fun c hcm => hRrows c hcm
    have h2 : seg C' 0 r = {u} := by
      ext c
      rw [mem_seg, Finset.mem_singleton]
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
  · rw [xNorm_def', seg_xShift, seg_union, hsegRempty, Finset.empty_union, hsegC',
      card_shift, card_shift, hCcard]
    omega
  · rw [hcellX, hsegtopX,
      show (shiftCell (-minX (R ∪ C')) 0 u).1 = u.1 + -minX (R ∪ C') from rfl,
      shift_shift, hC'_def, shift_shift,
      show -(u.1 + -minX (R ∪ C')) + -minX (R ∪ C') + u.1 = (0 : ℤ) from by ring,
      show -r + 0 + r = (0 : ℤ) from by ring, shift_zero]
  · rw [hsegbotX, xNorm_shift _ hRne, xNorm_eq_self hcR.2.2.1 hcR.2.2.2.1]

/-- **Class-C count**: canonical animals with a multi top row are counted by
top-edge cluster configurations times shorter walk-top remainders, aggregated
over `(j, ℓ)`. -/
lemma card_classC (k H : ℕ) (hH : k + 1 ≤ H) :
    ((allCanon L k H).filter fun S => ¬ rowSize S ((H : ℤ) - 1) = 1).card =
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt L ℓ j * d L (k - j) (H - ℓ) := by
  have htarget : (targetC L k H).card = ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
      Vt L ℓ j * d L (k - j) (H - ℓ) := by
    rw [targetC, Finset.card_sigma]
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [Finset.card_sigma]
    exact Finset.sum_congr rfl fun ℓ _ => by rw [Finset.card_product]; rfl
  rw [← htarget]
  refine Finset.card_nbij' (peelC H) (glueTop ((H : ℤ) - 1)) ?_ ?_ ?_ ?_
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    rw [Finset.mem_coe]
    exact (peelC_mem_and_glue hH hS.1 hS.2).1
  · intro x hx
    rw [Finset.mem_coe] at hx
    rw [Finset.mem_coe, Finset.mem_filter]
    exact (glueC_mem_and_peel hH hx).1
  · intro S hS
    rw [Finset.mem_coe, Finset.mem_filter] at hS
    exact (peelC_mem_and_glue hH hS.1 hS.2).2
  · intro x hx
    rw [Finset.mem_coe] at hx
    exact (glueC_mem_and_peel hH hx).2

/-! ## The main theorems -/

/-- **The d-recursion** (DESIGN.md v2): for `H ≥ k + 2`, a walk-top animal
splits by its second-top row — walk (class A: `b` up-offsets on a height-`H-1`
walk-top remainder) or the base of a cluster (class B: an interior
`V`-configuration capping a shorter walk-top remainder). -/
theorem d_rec (L : RowLocal) (k H : ℕ) (hH : k + 2 ≤ H) :
    d L k H = L.b * d L k (H - 1) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V L ℓ j * d L (k - j) (H - 1 - ℓ) := by
  classical
  have hsplit := Finset.card_filter_add_card_filter_not (s := Dc L k H)
    (fun S => rowSize S ((H : ℤ) - 2) = 1)
  rw [d, ← hsplit, card_classA k H hH, card_classB k H hH]

/-- **The c-identity**: for `H ≥ k + 1`, a canonical animal has a walk top
row (counted by `d L k H`) or a multi top row — a top-edge `Vᵗ`-configuration
capping a shorter walk-top remainder (class C). -/
theorem c_ident (L : RowLocal) (k H : ℕ) (hH : k + 1 ≤ H) :
    T L (H + k) H = d L k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt L ℓ j * d L (k - j) (H - ℓ) := by
  classical
  have hsplit := Finset.card_filter_add_card_filter_not (s := allCanon L k H)
    (fun S => rowSize S ((H : ℤ) - 1) = 1)
  rw [← card_allCanon, ← hsplit, filter_allCanon_walkTop, card_classC k H hH]
  rfl

end Polyplets.Universal
