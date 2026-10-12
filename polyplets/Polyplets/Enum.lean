/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Data.Nat.Bitwise
import Mathlib.Data.Nat.Find
import Mathlib.Data.Prod.Lex
import Polyplets.Compute
import Polyplets.Symmetry
import Polyplets.Weights

/-!
# A king-animal enumerator the kernel can run

`Compute.lean` decides a cell count by filtering a powerset, which the kernel
can afford only for the smallest cells. This file enumerates the canonical
king animals of `n` cells as a list of **bit boards**: a cell `(x, y)` with
`0 ≤ x, y < 16` is bit `y * 16 + x` of a natural number, so a cell set is one
numeral and the geometry is shifts, `|||`, `&&&` and `^^^`, all of which the
kernel evaluates with bignum arithmetic. The list is built by growth:

* every canonical animal of `n + 1 ≥ 2` cells has a **leaf**, a cell whose
  removal leaves it connected (`exists_isLeaf`: a cell farthest from a seed);
* its **deletable cell** `del` is the leaf that is largest in row-major order
  (`IsDel`, unique by `isDel_unique`);
* so the animals of `n + 1` cells are, exactly once each, the re-anchored
  `P ∪ {c}` over the animals `P` of `n` cells and the frontier cells `c` for
  which `c` is the deletable cell of `P ∪ {c}` (`children`).

`L n` is that list and `L_spec` says its boards are the canonical animals of
`n` cells, each once, for `n ≤ 14`. Counts are then lengths of filtered
lists: `a n`, `T n H`, the walk-top counts, the cluster weights and the
fixed-point counts of the symmetries all have a kernel-checkable form
(`Checks.lean` evaluates them; `EnumData.lean` stores the boards for `n ≤ 6`
so that the evaluation is done once).
-/

namespace Polyplets.Enum

/-! ## Bit boards

`W = 16` columns; index `i` is the cell `(i % 16, i / 16)`. The literal `16`
is used throughout so that `omega` sees the arithmetic. -/

/-- The cell of a bit index. -/
def decode (i : ℕ) : ℤ × ℤ := (((i % 16 : ℕ) : ℤ), ((i / 16 : ℕ) : ℤ))

/-- The cells of a board: its set bits below `256`, decoded. -/
def cells (m : ℕ) : Finset (ℤ × ℤ) :=
  ((Finset.range 256).filter fun i => m.testBit i = true).image decode

/-- Every set bit lies below `256`. -/
def InBox (m : ℕ) : Prop := m < 2 ^ 256

/-- Every set bit lies below `256` and not in the last column, so that the
column shifts of `nbrs` do not wrap. -/
def NoWrap (m : ℕ) : Prop := ∀ i, m.testBit i = true → i < 256 ∧ i % 16 + 1 < 16

/-- `R` is a sub-board of `S`. -/
def Sub (R S : ℕ) : Prop := ∀ i, R.testBit i = true → S.testBit i = true

/-- The eight king neighbours of every set cell, as one board. Row-wrapped
bits (from a cell in the first or last column) are garbage; every consumer
masks with a `NoWrap` board. -/
def nbrs (m : ℕ) : ℕ :=
  (m <<< 1) ||| (m >>> 1) ||| (m <<< 16) ||| (m >>> 16) |||
  (m <<< 17) ||| (m >>> 17) ||| (m <<< 15) ||| (m >>> 15)

/-- One flood step inside `S` from the reached board `R`. -/
def grow (S R : ℕ) : ℕ := (R ||| nbrs R) &&& S

/-- `k` flood steps inside `S` from `R`. -/
def flood (S : ℕ) : ℕ → ℕ → ℕ
  | 0, R => R
  | k + 1, R => flood S k (grow S R)

/-- `S` is connected: `n` flood steps from its highest cell reach every cell
(`n ≥ |S|` suffices, `connected_iff`). -/
def connected (n S : ℕ) : Bool := flood S n (2 ^ Nat.log2 S) == S

/-- The highest-index cell of `scan` whose removal keeps `S` connected
(`256` if there is none); `fuel` bounds the scan. -/
def firstLeaf (n S : ℕ) : ℕ → ℕ → ℕ
  | 0, _ => 256
  | fuel + 1, scan =>
    if scan = 0 then 256 else
      if connected n (S ^^^ 2 ^ Nat.log2 scan) then Nat.log2 scan
      else firstLeaf n S fuel (scan ^^^ 2 ^ Nat.log2 scan)

/-- The set bits of `m`, highest first; `fuel` bounds the scan. -/
def bitsOf : ℕ → ℕ → List ℕ
  | 0, _ => []
  | fuel + 1, m => if m = 0 then [] else Nat.log2 m :: bitsOf fuel (m ^^^ 2 ^ Nat.log2 m)

/-- The smallest occupied column (`16` on the empty board). -/
def minX (m : ℕ) : ℕ := ((bitsOf 256 m).map (· % 16)).foldl min 16

/-- The smallest occupied row (`16` on the empty board). -/
def minY (m : ℕ) : ℕ := ((bitsOf 256 m).map (· / 16)).foldl min 16

/-- Slide the board so that its bounding box touches column `0` and row `0`. -/
def reanchor (m : ℕ) : ℕ := m >>> (minY m * 16 + minX m)

/-- The board of all cells outside the last column: the `NoWrap` mask. -/
def boxMask : ℕ :=
  57895161181645529494837117048595051142566530671229791132691030063130991362047

/-- Children of the anchored `(n-1)`-cell board `P`: slide `P` by `(1, 1)` so
that its frontier fits, and for each frontier cell `c` keep the re-anchored
`P ∪ {c}` exactly when `c` is its first leaf. -/
def children (n P : ℕ) : List ℕ :=
  let P' := P <<< 17
  let F := (nbrs P' ^^^ (nbrs P' &&& P')) &&& boxMask
  (bitsOf 256 F).filterMap fun c =>
    let S := P' ||| 2 ^ c
    if firstLeaf n S 256 S = c then some (reanchor S) else none

/-- The canonical king animals of `n` cells, as boards, each once. -/
def L : ℕ → List ℕ
  | 0 => []
  | 1 => [1]
  | n + 2 => (L (n + 1)).flatMap (children (n + 2))

/-- The bounding-box height of an anchored board. -/
def height (m : ℕ) : ℕ := Nat.log2 m / 16 + 1

/-- The number of cells of the board in row `y`. -/
def rowCount (m y : ℕ) : ℕ := ((bitsOf 256 m).filter fun i => i / 16 = y).length

/-! ## Decoding -/

lemma decode_inj {i j : ℕ} (h : decode i = decode j) : i = j := by
  simp only [decode, Prod.mk.injEq, Nat.cast_inj] at h
  omega

lemma mem_cells {m : ℕ} {p : ℤ × ℤ} :
    p ∈ cells m ↔ ∃ i, i < 256 ∧ m.testBit i = true ∧ decode i = p := by
  simp only [cells, Finset.mem_image, Finset.mem_filter, Finset.mem_range]
  constructor
  · rintro ⟨i, ⟨hi, hb⟩, he⟩
    exact ⟨i, hi, hb, he⟩
  · rintro ⟨i, hi, hb, he⟩
    exact ⟨i, ⟨hi, hb⟩, he⟩

lemma decode_mem_cells {m i : ℕ} (hi : i < 256) : decode i ∈ cells m ↔ m.testBit i = true := by
  rw [mem_cells]
  constructor
  · rintro ⟨j, hj, hb, he⟩
    rwa [decode_inj he] at hb
  · intro h
    exact ⟨i, hi, h, rfl⟩

lemma testBit_eq_false_of_inBox {m i : ℕ} (hm : InBox m) (hi : 256 ≤ i) :
    m.testBit i = false :=
  Nat.testBit_lt_two_pow (lt_of_lt_of_le hm (Nat.pow_le_pow_right (by norm_num) hi))

lemma inBox_of_testBit {m : ℕ} (h : ∀ i, m.testBit i = true → i < 256) : InBox m :=
  Nat.lt_pow_two_of_testBit m fun i hi => by
    by_contra hc
    have := h i (by simpa using hc)
    omega

lemma inBox_of_noWrap {m : ℕ} (h : NoWrap m) : InBox m :=
  inBox_of_testBit fun i hi => (h i hi).1

lemma inBox_of_sub {R S : ℕ} (h : Sub R S) (hS : InBox S) : InBox R :=
  inBox_of_testBit fun i hi => by
    by_contra hc
    have := testBit_eq_false_of_inBox (i := i) hS (by omega)
    rw [h i hi] at this
    exact absurd this (by decide)

lemma noWrap_of_sub {R S : ℕ} (h : Sub R S) (hS : NoWrap S) : NoWrap R :=
  fun i hi => hS i (h i hi)

/-- Boards with the same cells are equal. -/
lemma eq_of_cells_eq {m m' : ℕ} (hm : InBox m) (hm' : InBox m') (h : cells m = cells m') :
    m = m' := by
  refine Nat.eq_of_testBit_eq fun i => ?_
  by_cases hi : i < 256
  · have h1 := decode_mem_cells (m := m) hi
    have h2 := decode_mem_cells (m := m') hi
    rw [h] at h1
    have h3 := h2.symm.trans h1
    cases hb : m.testBit i <;> cases hb' : m'.testBit i <;> simp_all
  · rw [testBit_eq_false_of_inBox hm (by omega), testBit_eq_false_of_inBox hm' (by omega)]

lemma cells_subset {R S : ℕ} (h : Sub R S) : cells R ⊆ cells S := by
  intro p hp
  obtain ⟨i, hi, hb, rfl⟩ := mem_cells.mp hp
  exact (decode_mem_cells hi).mpr (h i hb)

lemma cells_lor (m m' : ℕ) : cells (m ||| m') = cells m ∪ cells m' := by
  ext p
  simp only [mem_cells, Finset.mem_union, Nat.testBit_lor, Bool.or_eq_true]
  constructor
  · rintro ⟨i, hi, h | h, rfl⟩
    · exact Or.inl ⟨i, hi, h, rfl⟩
    · exact Or.inr ⟨i, hi, h, rfl⟩
  · rintro (⟨i, hi, h, rfl⟩ | ⟨i, hi, h, rfl⟩)
    · exact ⟨i, hi, Or.inl h, rfl⟩
    · exact ⟨i, hi, Or.inr h, rfl⟩

lemma cells_land (m m' : ℕ) : cells (m &&& m') = cells m ∩ cells m' := by
  ext p
  simp only [mem_cells, Finset.mem_inter, Nat.testBit_land, Bool.and_eq_true]
  constructor
  · rintro ⟨i, hi, ⟨h1, h2⟩, rfl⟩
    exact ⟨⟨i, hi, h1, rfl⟩, ⟨i, hi, h2, rfl⟩⟩
  · rintro ⟨⟨i, hi, h1, rfl⟩, ⟨j, hj, h2, he⟩⟩
    rw [decode_inj he] at h2
    exact ⟨i, hi, ⟨h1, h2⟩, rfl⟩

lemma cells_pow {i : ℕ} (hi : i < 256) : cells (2 ^ i) = {decode i} := by
  ext p
  simp only [mem_cells, Finset.mem_singleton, Nat.testBit_two_pow, decide_eq_true_eq]
  constructor
  · rintro ⟨j, -, rfl, rfl⟩
    rfl
  · rintro rfl
    exact ⟨i, hi, rfl, rfl⟩

lemma cells_xor_pow {m i : ℕ} (h : m.testBit i = true) :
    cells (m ^^^ 2 ^ i) = (cells m).erase (decode i) := by
  ext p
  simp only [mem_cells, Finset.mem_erase, Nat.testBit_xor, Nat.testBit_two_pow]
  constructor
  · rintro ⟨j, hj, hb, rfl⟩
    have hne : i ≠ j := by
      rintro rfl
      simp [h] at hb
    refine ⟨fun he => hne (decode_inj he.symm), j, hj, ?_, rfl⟩
    simpa [hne] using hb
  · rintro ⟨hne, j, hj, hb, rfl⟩
    have hij : i ≠ j := fun he => hne (by rw [he])
    exact ⟨j, hj, by simpa [hij] using hb, rfl⟩

lemma cells_zero : cells 0 = ∅ := by
  ext p
  simp [mem_cells]

lemma ne_zero_of_cells_nonempty {m : ℕ} (h : (cells m).Nonempty) : m ≠ 0 := by
  rintro rfl
  rw [cells_zero] at h
  exact Finset.not_nonempty_empty h

/-- A bit set inside the box lies below `256`. -/
lemma lt_256_of_testBit {m i : ℕ} (hm : InBox m) (h : m.testBit i = true) : i < 256 := by
  by_contra hc
  rw [testBit_eq_false_of_inBox hm (by omega)] at h
  exact Bool.false_ne_true h

/-! ## The highest bit -/

lemma le_log2_of_testBit {m i : ℕ} (h : m.testBit i = true) : i ≤ Nat.log2 m := by
  have h0 : m ≠ 0 := by
    rintro rfl
    simp at h
  exact (Nat.le_log2 h0).mpr (Nat.ge_two_pow_of_testBit h)

lemma log2_lt_of_inBox {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) : Nat.log2 m < 256 :=
  (Nat.log2_lt h0).mpr hm

/-! ## Neighbours -/

/-- A bit of `nbrs m` is a bit of `m` moved by one of the eight index offsets. -/
lemma testBit_nbrs {m j : ℕ} :
    (nbrs m).testBit j = true ↔ ∃ i, m.testBit i = true ∧
      (i + 1 = j ∨ j + 1 = i ∨ i + 16 = j ∨ j + 16 = i ∨
        i + 17 = j ∨ j + 17 = i ∨ i + 15 = j ∨ j + 15 = i) := by
  simp only [nbrs, Nat.testBit_lor, Nat.testBit_shiftLeft, Nat.testBit_shiftRight,
    Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro (((((((⟨h1, h2⟩ | h) | ⟨h1, h2⟩) | h) | ⟨h1, h2⟩) | h) | ⟨h1, h2⟩) | h)
    · exact ⟨j - 1, h2, by omega⟩
    · exact ⟨1 + j, h, by omega⟩
    · exact ⟨j - 16, h2, by omega⟩
    · exact ⟨16 + j, h, by omega⟩
    · exact ⟨j - 17, h2, by omega⟩
    · exact ⟨17 + j, h, by omega⟩
    · exact ⟨j - 15, h2, by omega⟩
    · exact ⟨15 + j, h, by omega⟩
  · rintro ⟨i, hi, h | h | h | h | h | h | h | h⟩
    · exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl ⟨by omega,
        by rwa [show j - 1 = i by omega]⟩))))))
    · exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inr
        (by rwa [show 1 + j = i by omega])))))))
    · exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inr ⟨by omega,
        by rwa [show j - 16 = i by omega]⟩)))))
    · exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inr (by rwa [show 16 + j = i by omega])))))
    · exact Or.inl (Or.inl (Or.inl (Or.inr ⟨by omega, by rwa [show j - 17 = i by omega]⟩)))
    · exact Or.inl (Or.inl (Or.inr (by rwa [show 17 + j = i by omega])))
    · exact Or.inl (Or.inr ⟨by omega, by rwa [show j - 15 = i by omega]⟩)
    · exact Or.inr (by rwa [show 15 + j = i by omega])

/-- Off the last column, the eight index offsets are exactly king adjacency. -/
lemma kingAdj_decode_iff {i j : ℕ} (_hi : i < 256) (hi' : i % 16 + 1 < 16) (_hj : j < 256)
    (hj' : j % 16 + 1 < 16) :
    kingAdj (decode i) (decode j) ↔
      (i + 1 = j ∨ j + 1 = i ∨ i + 16 = j ∨ j + 16 = i ∨
        i + 17 = j ∨ j + 17 = i ∨ i + 15 = j ∨ j + 15 = i) := by
  simp only [kingAdj, decode, ne_eq, Prod.mk.injEq, Nat.cast_inj, abs_le]
  omega

/-- The cells of `nbrs R &&& B`, for `NoWrap` boards: the cells of `B` king-adjacent
to a cell of `R`. -/
lemma mem_cells_nbrs_land {R B : ℕ} (hR : NoWrap R) (hB : NoWrap B) {q : ℤ × ℤ} :
    q ∈ cells (nbrs R &&& B) ↔ q ∈ cells B ∧ ∃ p ∈ cells R, kingAdj p q := by
  rw [cells_land, Finset.mem_inter]
  constructor
  · rintro ⟨hq1, hq2⟩
    refine ⟨hq2, ?_⟩
    obtain ⟨j, hj, hbj, rfl⟩ := mem_cells.mp hq2
    obtain ⟨i, hbi, hrel⟩ := testBit_nbrs.mp ((decode_mem_cells hj).mp hq1)
    obtain ⟨hi, hi'⟩ := hR i hbi
    exact ⟨decode i, (decode_mem_cells hi).mpr hbi,
      (kingAdj_decode_iff hi hi' hj (hB j hbj).2).mpr hrel⟩
  · rintro ⟨hqB, p, hpR, hadj⟩
    obtain ⟨i, hi, hbi, rfl⟩ := mem_cells.mp hpR
    obtain ⟨j, hj, hbj, rfl⟩ := mem_cells.mp hqB
    refine ⟨(decode_mem_cells hj).mpr (testBit_nbrs.mpr ⟨i, hbi, ?_⟩), hqB⟩
    exact (kingAdj_decode_iff hi (hR i hbi).2 hj (hB j hbj).2).mp hadj

/-! ## The flood and connectivity -/

lemma cells_lor_land (A B C : ℕ) : cells ((A ||| B) &&& C) = cells (A &&& C) ∪ cells (B &&& C) := by
  rw [cells_land, cells_lor, cells_land, cells_land, Finset.union_inter_distrib_right]

lemma sub_grow (S R : ℕ) : Sub (grow S R) S := fun i hi => by
  simp only [grow, Nat.testBit_land, Bool.and_eq_true] at hi
  exact hi.2

lemma cells_grow {S R : ℕ} (hS : NoWrap S) (hR : Sub R S) :
    cells (grow S R) = stepExpand (cells S) (cells R) := by
  rw [grow, cells_lor_land, stepExpand]
  have h1 : cells (R &&& S) = cells R := by
    rw [cells_land]
    exact Finset.inter_eq_left.mpr (cells_subset hR)
  rw [h1]
  congr 1
  ext q
  rw [mem_cells_nbrs_land (noWrap_of_sub hR hS) hS, Finset.mem_filter]

lemma sub_flood {S : ℕ} : ∀ k R, Sub R S → Sub (flood S k R) S := by
  intro k
  induction k with
  | zero => intro R hR; exact hR
  | succ k ih => intro R _; exact ih _ (sub_grow S R)

lemma cells_flood {S : ℕ} (hS : NoWrap S) :
    ∀ k R, Sub R S → cells (flood S k R) = (stepExpand (cells S))^[k] (cells R) := by
  intro k
  induction k with
  | zero => intro R _; rfl
  | succ k ih =>
    intro R hR
    rw [flood, ih _ (sub_grow S R), cells_grow hS hR, Function.iterate_succ_apply]

lemma iterate_stepExpand_mono (S : Finset (ℤ × ℤ)) (p : ℤ × ℤ) {k k' : ℕ} (h : k ≤ k') :
    (stepExpand S)^[k] {p} ⊆ (stepExpand S)^[k'] {p} := by
  induction h with
  | refl => exact Finset.Subset.refl _
  | step _ ih =>
    refine ih.trans ?_
    rw [Function.iterate_succ_apply']
    exact subset_stepExpand _ _

lemma sub_pow_log2 {S : ℕ} (h0 : S ≠ 0) : Sub (2 ^ Nat.log2 S) S := fun i hi => by
  rw [Nat.testBit_two_pow, decide_eq_true_eq] at hi
  rw [← hi]
  exact Nat.testBit_log2 h0

/-- **The connectivity test is `KingConnected`**, for a `NoWrap` board with at
most `n` cells. -/
lemma connected_iff {n S : ℕ} (hS : NoWrap S) (h0 : S ≠ 0) (hn : (cells S).card ≤ n) :
    connected n S = true ↔ KingConnected (cells S) := by
  have hbox := inBox_of_noWrap hS
  have hL := log2_lt_of_inBox hbox h0
  have hp : decode (Nat.log2 S) ∈ cells S := (decode_mem_cells hL).mpr (Nat.testBit_log2 h0)
  have hcells : cells (flood S n (2 ^ Nat.log2 S))
      = (stepExpand (cells S))^[n] {decode (Nat.log2 S)} := by
    rw [cells_flood hS n _ (sub_pow_log2 h0), cells_pow hL]
  rw [connected, beq_iff_eq]
  constructor
  · intro h
    rw [h] at hcells
    intro q hq r hr
    rw [hcells] at hq hr
    exact (reflTransGen_symm (reachSet_sound hp n q hq)).trans (reachSet_sound hp n r hr)
  · intro h
    refine eq_of_cells_eq (inBox_of_sub (sub_flood n _ (sub_pow_log2 h0)) hbox) hbox ?_
    rw [hcells]
    refine le_antisymm (iterate_stepExpand_subset hp n) fun q hq => ?_
    exact iterate_stepExpand_mono _ _ hn (reachSet_complete hp (h _ hp q hq))

/-! ## Scanning the bits -/

/-- The number of set bits below `256`. -/
def nbits (m : ℕ) : ℕ := ((Finset.range 256).filter fun i => m.testBit i = true).card

lemma card_cells (m : ℕ) : (cells m).card = nbits m := by
  rw [cells, nbits]
  exact Finset.card_image_of_injOn fun _ _ _ _ h => decode_inj h

lemma inBox_xor_pow {m i : ℕ} (hm : InBox m) (hi : i < 256) : InBox (m ^^^ 2 ^ i) :=
  inBox_of_testBit fun j hj => by
    rw [Nat.testBit_xor, Nat.testBit_two_pow] at hj
    by_contra hc
    rw [testBit_eq_false_of_inBox hm (by omega), decide_eq_false (by omega)] at hj
    simp at hj

lemma nbits_xor_log2 {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) :
    nbits (m ^^^ 2 ^ Nat.log2 m) + 1 = nbits m := by
  have hmem : decode (Nat.log2 m) ∈ cells m :=
    (decode_mem_cells (log2_lt_of_inBox hm h0)).mpr (Nat.testBit_log2 h0)
  rw [← card_cells, ← card_cells, cells_xor_pow (Nat.testBit_log2 h0),
    Finset.card_erase_of_mem hmem]
  have := Finset.card_pos.mpr ⟨_, hmem⟩
  omega

lemma nbits_le (m : ℕ) : nbits m ≤ 256 :=
  (Finset.card_filter_le _ _).trans (by simp)

/-- `bitsOf` lists exactly the set bits, given fuel for all of them. -/
lemma mem_bitsOf {m : ℕ} (hm : InBox m) :
    ∀ fuel, nbits m ≤ fuel → ∀ j, (j ∈ bitsOf fuel m ↔ m.testBit j = true) := by
  intro fuel
  induction fuel generalizing m with
  | zero =>
    intro hf j
    simp only [bitsOf, List.not_mem_nil, false_iff]
    intro hb
    have hj : j < 256 := lt_256_of_testBit hm hb
    have : 0 < nbits m := Finset.card_pos.mpr
      ⟨j, Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hj, hb⟩⟩
    omega
  | succ fuel ih =>
    intro hf j
    by_cases h0 : m = 0
    · subst h0
      simp [bitsOf]
    · have hL := log2_lt_of_inBox hm h0
      have hrec := ih (inBox_xor_pow hm hL) (by have := nbits_xor_log2 hm h0; omega) j
      simp only [bitsOf, h0, if_false, List.mem_cons, hrec, Nat.testBit_xor, Nat.testBit_two_pow]
      constructor
      · rintro (rfl | h)
        · exact Nat.testBit_log2 h0
        · by_cases hj : Nat.log2 m = j
          · subst hj; exact Nat.testBit_log2 h0
          · simpa [hj] using h
      · intro h
        by_cases hj : Nat.log2 m = j
        · exact Or.inl hj.symm
        · exact Or.inr (by simpa [hj] using h)

lemma bitsOf_nodup {m : ℕ} (hm : InBox m) :
    ∀ fuel, nbits m ≤ fuel → (bitsOf fuel m).Nodup := by
  intro fuel
  induction fuel generalizing m with
  | zero => intro _; simp [bitsOf]
  | succ fuel ih =>
    intro hf
    by_cases h0 : m = 0
    · subst h0; simp [bitsOf]
    · have hL := log2_lt_of_inBox hm h0
      have hf' : nbits (m ^^^ 2 ^ Nat.log2 m) ≤ fuel := by
        have := nbits_xor_log2 hm h0; omega
      simp only [bitsOf, h0, if_false, List.nodup_cons]
      refine ⟨fun h => ?_, ih (inBox_xor_pow hm hL) hf'⟩
      rw [mem_bitsOf (inBox_xor_pow hm hL) fuel hf', Nat.testBit_xor, Nat.testBit_log2 h0,
        Nat.testBit_two_pow_self] at h
      simp at h

lemma mem_bitsOf' {m j : ℕ} (hm : InBox m) : j ∈ bitsOf 256 m ↔ m.testBit j = true :=
  mem_bitsOf hm 256 (nbits_le m) j

/-! ## Minima and re-anchoring -/

lemma foldl_min_le (l : List ℕ) (a : ℕ) : l.foldl min a ≤ a ∧ ∀ x ∈ l, l.foldl min a ≤ x := by
  induction l generalizing a with
  | nil => simp
  | cons b l ih =>
    simp only [List.foldl_cons, List.mem_cons, forall_eq_or_imp]
    obtain ⟨h1, h2⟩ := ih (min a b)
    exact ⟨h1.trans (min_le_left _ _), h1.trans (min_le_right _ _), h2⟩

lemma foldl_min_mem (l : List ℕ) (a : ℕ) : l.foldl min a = a ∨ l.foldl min a ∈ l := by
  induction l generalizing a with
  | nil => simp
  | cons b l ih =>
    simp only [List.foldl_cons, List.mem_cons]
    rcases ih (min a b) with h | h
    · rw [h]
      rcases le_total a b with hab | hab
      · exact Or.inl (min_eq_left hab)
      · exact Or.inr (Or.inl (min_eq_right hab))
    · exact Or.inr (Or.inr h)

lemma minX_le {m i : ℕ} (hm : InBox m) (hi : m.testBit i = true) : minX m ≤ i % 16 :=
  (foldl_min_le _ _).2 _ (List.mem_map.mpr ⟨i, (mem_bitsOf' hm).mpr hi, rfl⟩)

lemma minY_le {m i : ℕ} (hm : InBox m) (hi : m.testBit i = true) : minY m ≤ i / 16 :=
  (foldl_min_le _ _).2 _ (List.mem_map.mpr ⟨i, (mem_bitsOf' hm).mpr hi, rfl⟩)

lemma exists_minX {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) :
    ∃ i, m.testBit i = true ∧ i % 16 = minX m := by
  rcases foldl_min_mem ((bitsOf 256 m).map (· % 16)) 16 with h | h
  · exfalso
    have := minX_le hm (Nat.testBit_log2 h0)
    rw [minX] at this
    omega
  · obtain ⟨i, hi, he⟩ := List.mem_map.mp h
    exact ⟨i, (mem_bitsOf' hm).mp hi, he⟩

lemma exists_minY {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) :
    ∃ i, m.testBit i = true ∧ i / 16 = minY m := by
  rcases foldl_min_mem ((bitsOf 256 m).map (· / 16)) 16 with h | h
  · exfalso
    have := minY_le hm (Nat.testBit_log2 h0)
    have hL := log2_lt_of_inBox hm h0
    rw [minY] at this
    omega
  · obtain ⟨i, hi, he⟩ := List.mem_map.mp h
    exact ⟨i, (mem_bitsOf' hm).mp hi, he⟩

/-- The anchor vector of a board's cells is its pair of minima. -/
lemma anchorVec_cells {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) :
    anchorVec (cells m) = ((minX m : ℤ), (minY m : ℤ)) := by
  have hne : (cells m).Nonempty :=
    ⟨decode (Nat.log2 m), (decode_mem_cells (log2_lt_of_inBox hm h0)).mpr (Nat.testBit_log2 h0)⟩
  rw [anchorVec, dif_pos hne]
  obtain ⟨ix, hbx, hex⟩ := exists_minX hm h0
  obtain ⟨iy, hby, hey⟩ := exists_minY hm h0
  have hx : ix < 256 := lt_256_of_testBit hm hbx
  have hy : iy < 256 := lt_256_of_testBit hm hby
  refine Prod.ext ?_ ?_
  · refine le_antisymm ?_ ?_
    · have := Finset.inf'_le Prod.fst ((decode_mem_cells hx).mpr hbx)
      simpa [decode, hex] using this
    · refine Finset.le_inf' hne _ fun p hp => ?_
      obtain ⟨i, hi, hb, rfl⟩ := mem_cells.mp hp
      have := minX_le hm hb
      simp only [decode]
      omega
  · refine le_antisymm ?_ ?_
    · have := Finset.inf'_le Prod.snd ((decode_mem_cells hy).mpr hby)
      simpa [decode, hey] using this
    · refine Finset.le_inf' hne _ fun p hp => ?_
      obtain ⟨i, hi, hb, rfl⟩ := mem_cells.mp hp
      have := minY_le hm hb
      simp only [decode]
      omega

lemma inBox_shiftRight {m k : ℕ} (hm : InBox m) : InBox (m >>> k) :=
  lt_of_le_of_lt (Nat.shiftRight_le m k) hm

/-- **Re-anchoring a board re-anchors its cells.** -/
lemma cells_reanchor {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) :
    cells (reanchor m) = Polyplets.reanchor (cells m) := by
  rw [Polyplets.reanchor, anchorVec_cells hm h0, reanchor]
  ext q
  simp only [mem_cells, Finset.mem_image, Nat.testBit_shiftRight]
  constructor
  · rintro ⟨j, hj, hb, rfl⟩
    have hmx := minX_le hm hb
    have hmy := minY_le hm hb
    refine ⟨decode (minY m * 16 + minX m + j), ⟨_, ?_, hb, rfl⟩, ?_⟩
    · exact lt_256_of_testBit hm hb
    · have hx : j % 16 + minX m < 16 := by
        by_contra hc
        have h1 : (minY m * 16 + minX m + j) % 16 = j % 16 + minX m - 16 := by omega
        omega
      simp only [decode, Prod.mk_sub_mk, Prod.mk.injEq]
      constructor
      · rw [show (minY m * 16 + minX m + j) % 16 = j % 16 + minX m by omega]
        push_cast
        ring
      · rw [show (minY m * 16 + minX m + j) / 16 = j / 16 + minY m by omega]
        push_cast
        ring
  · rintro ⟨p, ⟨i, hi, hb, rfl⟩, rfl⟩
    have hmx := minX_le hm hb
    have hmy := minY_le hm hb
    refine ⟨i - (minY m * 16 + minX m), by omega, ?_, ?_⟩
    · rwa [show minY m * 16 + minX m + (i - (minY m * 16 + minX m)) = i by omega]
    · simp only [decode, Prod.mk_sub_mk, Prod.mk.injEq]
      constructor
      · rw [show (i - (minY m * 16 + minX m)) % 16 = i % 16 - minX m by omega]
        push_cast [hmx]
        ring
      · rw [show (i - (minY m * 16 + minX m)) / 16 = i / 16 - minY m by omega]
        push_cast [hmy]
        ring

/-- Sliding a board by `(1, 1)`, given room on the right and the top. -/
lemma cells_shiftLeft_17 {m : ℕ}
    (h : ∀ i, m.testBit i = true → i % 16 + 1 < 16 ∧ i / 16 + 1 < 16) :
    cells (m <<< 17) = translate (1, 1) (cells m) := by
  ext q
  simp only [mem_cells, mem_translate, Nat.testBit_shiftLeft, Bool.and_eq_true,
    decide_eq_true_eq]
  constructor
  · rintro ⟨j, hj, ⟨hj17, hb⟩, rfl⟩
    obtain ⟨hx, hy⟩ := h _ hb
    refine ⟨j - 17, by omega, hb, ?_⟩
    simp only [decode, Prod.mk_sub_mk, Prod.mk.injEq]
    constructor
    · rw [show (j - 17) % 16 = j % 16 - 1 by omega]
      push_cast [show 1 ≤ j % 16 by omega]
      ring
    · rw [show (j - 17) / 16 = j / 16 - 1 by omega]
      push_cast [show 1 ≤ j / 16 by omega]
      ring
  · rintro ⟨i, hi, hb, he⟩
    obtain ⟨hx, hy⟩ := h _ hb
    refine ⟨i + 17, by omega, ⟨by omega, by rwa [Nat.add_sub_cancel]⟩, ?_⟩
    have hq : q = decode i + (1, 1) := by rw [he]; simp
    subst hq
    simp only [decode, Prod.mk_add_mk, Prod.mk.injEq]
    rw [show (i + 17) % 16 = i % 16 + 1 by omega, show (i + 17) / 16 = i / 16 + 1 by omega]
    push_cast
    exact ⟨rfl, rfl⟩

/-! ## Height and row counts -/

lemma height_eq {m : ℕ} (hm : InBox m) (h0 : m ≠ 0) : height m = heightOf (cells m) := by
  rw [height, heightOf]
  congr 1
  refine le_antisymm ?_ ?_
  · have hL := log2_lt_of_inBox hm h0
    have := Finset.le_sup (f := fun p : ℤ × ℤ => p.2.toNat)
      ((decode_mem_cells hL).mpr (Nat.testBit_log2 h0))
    simp only [decode, Int.toNat_natCast] at this
    exact this
  · refine Finset.sup_le fun p hp => ?_
    obtain ⟨i, hi, hb, rfl⟩ := mem_cells.mp hp
    have := le_log2_of_testBit hb
    simp only [decode, Int.toNat_natCast]
    omega

lemma rowCount_eq {m : ℕ} (hm : InBox m) (y : ℕ) : rowCount m y = rowSize (cells m) y := by
  have hnd : ((bitsOf 256 m).filter fun i => i / 16 = y).Nodup :=
    (bitsOf_nodup hm 256 (nbits_le m)).filter _
  have himg : (cells m).filter (fun p => p.2 = (y : ℤ))
      = (((bitsOf 256 m).filter fun i => i / 16 = y).toFinset).image decode := by
    ext p
    simp only [Finset.mem_filter, mem_cells, Finset.mem_image, List.mem_toFinset,
      List.mem_filter, mem_bitsOf' hm, decide_eq_true_eq]
    constructor
    · rintro ⟨⟨i, hi, hb, rfl⟩, hy⟩
      refine ⟨i, ⟨hb, ?_⟩, rfl⟩
      simp only [decode] at hy
      exact_mod_cast hy
    · rintro ⟨i, ⟨hb, hy⟩, rfl⟩
      refine ⟨⟨i, ?_, hb, rfl⟩, ?_⟩
      · exact lt_256_of_testBit hm hb
      · simp only [decode]
        exact_mod_cast hy
  rw [rowCount, rowSize, himg, Finset.card_image_of_injOn fun _ _ _ _ h => decode_inj h,
    List.toFinset_card_of_nodup hnd]

/-! ## Leaves and the deletable cell -/

/-- `c` is a leaf of `S`: a cell whose removal leaves `S` connected. -/
def IsLeaf (S : Finset (ℤ × ℤ)) (c : ℤ × ℤ) : Prop := c ∈ S ∧ KingConnected (S.erase c)

/-- **Every connected set of two or more cells has a leaf**: a cell at the
largest flood distance from a seed. Removing it keeps every other cell on its
flood path to the seed, since that path runs through strictly nearer cells. -/
theorem exists_isLeaf {S : Finset (ℤ × ℤ)} (hS : KingConnected S) (h2 : 2 ≤ S.card) :
    ∃ c, IsLeaf S c := by
  classical
  obtain ⟨p, hp⟩ := Finset.card_pos.mp (by omega : 0 < S.card)
  have hex : ∃ k, (stepExpand S)^[k] {p} = S :=
    ⟨S.card, le_antisymm (iterate_stepExpand_subset hp _)
      fun q hq => reachSet_complete hp (hS p hp q hq)⟩
  have hNspec : (stepExpand S)^[Nat.find hex] {p} = S := Nat.find_spec hex
  have hN1 : 1 ≤ Nat.find hex := by
    rcases Nat.eq_zero_or_pos (Nat.find hex) with h0 | h0
    · rw [h0, Function.iterate_zero, id_eq] at hNspec
      rw [← hNspec, Finset.card_singleton] at h2
      omega
    · exact h0
  have hA : (stepExpand S)^[Nat.find hex - 1] {p} ≠ S := Nat.find_min hex (by omega)
  have hAsub : (stepExpand S)^[Nat.find hex - 1] {p} ⊆ S := iterate_stepExpand_subset hp _
  obtain ⟨q, hqS, hqA⟩ : ∃ q ∈ S, q ∉ (stepExpand S)^[Nat.find hex - 1] {p} := by
    by_contra hc
    push Not at hc
    exact hA (Finset.Subset.antisymm hAsub hc)
  -- every cell other than `q` is joined to `p` inside `S.erase q`
  have key : ∀ k, k ≤ Nat.find hex → ∀ r ∈ (stepExpand S)^[k] {p}, r ≠ q →
      Relation.ReflTransGen (fun a b => a ∈ S.erase q ∧ b ∈ S.erase q ∧ kingAdj a b) p r := by
    intro k
    induction k with
    | zero =>
      intro _ r hr _
      rw [Function.iterate_zero, id_eq, Finset.mem_singleton] at hr
      subst hr
      exact Relation.ReflTransGen.refl
    | succ k ih =>
      intro hk r hr hrq
      rw [Function.iterate_succ_apply'] at hr
      simp only [stepExpand, Finset.mem_union, Finset.mem_filter] at hr
      rcases hr with hr | ⟨hrS, a, ha, hadj⟩
      · exact ih (by omega) r hr hrq
      · have haq : a ≠ q := fun h =>
          hqA (h ▸ iterate_stepExpand_mono S p (by omega : k ≤ Nat.find hex - 1) ha)
        have haS : a ∈ S := iterate_stepExpand_subset hp k ha
        exact (ih (by omega) a ha haq).tail
          ⟨Finset.mem_erase.mpr ⟨haq, haS⟩, Finset.mem_erase.mpr ⟨hrq, hrS⟩, hadj⟩
  refine ⟨q, hqS, fun x hx y hy => ?_⟩
  obtain ⟨hxq, hxS⟩ := Finset.mem_erase.mp hx
  obtain ⟨hyq, hyS⟩ := Finset.mem_erase.mp hy
  rw [← hNspec] at hxS hyS
  exact (reflTransGen_symm (key _ le_rfl x hxS hxq)).trans (key _ le_rfl y hyS hyq)

/-- A cell of a connected set of two or more cells has a neighbour in it. -/
lemma exists_adj_of_connected {S : Finset (ℤ × ℤ)} (hS : KingConnected S) (h2 : 2 ≤ S.card)
    {c : ℤ × ℤ} (hc : c ∈ S) : ∃ q ∈ S, q ≠ c ∧ kingAdj c q := by
  obtain ⟨r, hr, hrc⟩ : ∃ r ∈ S, r ≠ c := by
    by_contra h
    push Not at h
    have : S ⊆ {c} := fun x hx => Finset.mem_singleton.mpr (h x hx)
    have := Finset.card_le_card this
    rw [Finset.card_singleton] at this
    omega
  rcases Relation.ReflTransGen.cases_head (hS c hc r hr) with h | ⟨q, ⟨-, hqS, hadj⟩, -⟩
  · exact absurd h.symm hrc
  · exact ⟨q, hqS, fun h => hadj.1 h.symm, hadj⟩

/-- Row-major order on cells: the order of bit indices. -/
def key (c : ℤ × ℤ) : Lex (ℤ × ℤ) := toLex (c.2, c.1)

lemma key_injective : Function.Injective key := fun a b h => by
  have h' := toLex.injective h
  simp only [Prod.mk.injEq] at h'
  exact Prod.ext h'.2 h'.1

lemma key_le_add {c d v : ℤ × ℤ} : key (c + v) ≤ key (d + v) ↔ key c ≤ key d := by
  simp only [key, Prod.Lex.toLex_le_toLex, Prod.fst_add, Prod.snd_add]
  omega

/-- `c` is the deletable cell of `S`: its leaf that is largest in row-major
order. -/
def IsDel (S : Finset (ℤ × ℤ)) (c : ℤ × ℤ) : Prop :=
  IsLeaf S c ∧ ∀ x ∈ S, IsLeaf S x → key x ≤ key c

theorem isDel_unique {S : Finset (ℤ × ℤ)} {c d : ℤ × ℤ} (hc : IsDel S c) (hd : IsDel S d) :
    c = d :=
  key_injective (le_antisymm (hd.2 c hc.1.1 hc.1) (hc.2 d hd.1.1 hd.1))

theorem exists_isDel {S : Finset (ℤ × ℤ)} (hS : KingConnected S) (h2 : 2 ≤ S.card) :
    ∃ c, IsDel S c := by
  classical
  obtain ⟨c0, hc0⟩ := exists_isLeaf hS h2
  obtain ⟨c, hc, hmax⟩ := Finset.exists_max_image (S.filter fun x => IsLeaf S x) key
    ⟨c0, Finset.mem_filter.mpr ⟨hc0.1, hc0⟩⟩
  exact ⟨c, (Finset.mem_filter.mp hc).2,
    fun x hx hlx => hmax x (Finset.mem_filter.mpr ⟨hx, hlx⟩)⟩

lemma kingConnected_translate_iff (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} :
    KingConnected (translate v S) ↔ KingConnected S := by
  refine ⟨fun h => ?_, kingConnected_translate v⟩
  have := kingConnected_translate (-v) h
  rwa [translate_translate, add_neg_cancel, translate_zero] at this

lemma isLeaf_translate (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} :
    IsLeaf (translate v S) (c + v) ↔ IsLeaf S c := by
  rw [IsLeaf, IsLeaf, mem_translate, add_sub_cancel_right, ← translate_erase,
    kingConnected_translate_iff]

lemma isDel_translate (v : ℤ × ℤ) {S : Finset (ℤ × ℤ)} {c : ℤ × ℤ} :
    IsDel (translate v S) (c + v) ↔ IsDel S c := by
  rw [IsDel, IsDel, isLeaf_translate]
  refine and_congr_right fun _ => ⟨fun h x hx hl => ?_, fun h x hx hl => ?_⟩
  · exact key_le_add.mp (h (x + v) (translate_mem hx) ((isLeaf_translate v).mpr hl))
  · obtain ⟨y, hy, rfl⟩ : ∃ y ∈ S, y + v = x := by
      rw [mem_translate] at hx
      exact ⟨x - v, hx, sub_add_cancel x v⟩
    exact key_le_add.mpr (h y hy ((isLeaf_translate v).mp hl))

/-- **The parent of a child.** The re-anchored `insert c P`, when `c` is its
deletable cell, has deletable cell `c - anchorVec (insert c P)`; removing it
and re-anchoring recovers `reanchor P`. -/
lemma child_parent {P : Finset (ℤ × ℤ)} {c : ℤ × ℤ} (hc : c ∉ P)
    (hdel : IsDel (insert c P) c) :
    IsDel (Polyplets.reanchor (insert c P)) (c - anchorVec (insert c P)) ∧
    (Polyplets.reanchor (insert c P)).erase (c - anchorVec (insert c P))
      = translate (-anchorVec (insert c P)) P := by
  rw [reanchor_eq_translate, sub_eq_add_neg]
  exact ⟨(isDel_translate _).mpr hdel, by rw [← translate_erase, Finset.erase_insert hc]⟩

/-- Two children of one parent with the same re-anchored form are the same
child. -/
lemma child_inj {P : Finset (ℤ × ℤ)} (hP : P.Nonempty) {c c' : ℤ × ℤ} (hc : c ∉ P)
    (hc' : c' ∉ P) (hdel : IsDel (insert c P) c) (hdel' : IsDel (insert c' P) c')
    (h : Polyplets.reanchor (insert c P) = Polyplets.reanchor (insert c' P)) : c = c' := by
  obtain ⟨d1, e1⟩ := child_parent hc hdel
  obtain ⟨d2, e2⟩ := child_parent hc' hdel'
  rw [← h] at d2 e2
  have he := isDel_unique d1 d2
  rw [← he, e1] at e2
  have h3 : translate (-anchorVec (insert c P) + anchorVec (insert c' P)) P = P := by
    have := congrArg (translate (anchorVec (insert c' P))) e2
    rwa [translate_translate, translate_translate, neg_add_cancel, translate_zero] at this
  have h4 := translate_eq_self hP h3
  have h5 : anchorVec (insert c' P) = anchorVec (insert c P) := by
    have := congrArg (· + anchorVec (insert c P)) h4
    simpa using this
  rw [h5] at he
  exact sub_left_injective he

/-- Children with the same re-anchored form have the same re-anchored parent. -/
lemma parent_eq_of_child_eq {P P' : Finset (ℤ × ℤ)} {c c' : ℤ × ℤ} (hc : c ∉ P) (hc' : c' ∉ P')
    (hdel : IsDel (insert c P) c) (hdel' : IsDel (insert c' P') c')
    (h : Polyplets.reanchor (insert c P) = Polyplets.reanchor (insert c' P')) :
    Polyplets.reanchor P = Polyplets.reanchor P' := by
  obtain ⟨d1, e1⟩ := child_parent hc hdel
  obtain ⟨d2, e2⟩ := child_parent hc' hdel'
  rw [← h] at d2 e2
  rw [← isDel_unique d1 d2, e1] at e2
  have h1 := congrArg Polyplets.reanchor e2
  rwa [show translate (-anchorVec (insert c P)) P = P.image (· + -anchorVec (insert c P))
    from rfl, show translate (-anchorVec (insert c' P')) P'
      = P'.image (· + -anchorVec (insert c' P')) from rfl,
    reanchor_image_add, reanchor_image_add] at h1

/-- A canonical animal with a cell adjoined, re-anchored, is a canonical animal. -/
lemma isCanonicalAnimal_insert_reanchor {n : ℕ} {P : Finset (ℤ × ℤ)} (hP : IsCanonicalAnimal n P)
    {c : ℤ × ℤ} (hc : c ∉ P) (hadj : ∃ p ∈ P, kingAdj p c) :
    IsCanonicalAnimal (n + 1) (Polyplets.reanchor (insert c P)) := by
  obtain ⟨p, hp, hpc⟩ := hadj
  exact ⟨by rw [reanchor_card, Finset.card_insert_of_notMem hc, hP.card],
    kingConnected_reanchor (kingConnected_insert hP.conn hp hpc),
    reanchor_anchored ⟨c, Finset.mem_insert_self c P⟩⟩

/-! ## The boards of a child -/

/-- The bit index of a cell of the board. -/
def encode (p : ℤ × ℤ) : ℕ := p.2.toNat * 16 + p.1.toNat

lemma decode_encode {p : ℤ × ℤ} (hx : 0 ≤ p.1) (hx' : p.1 < 16) (hy : 0 ≤ p.2) (hy' : p.2 < 16) :
    decode (encode p) = p := by
  obtain ⟨x, hxe⟩ := Int.eq_ofNat_of_zero_le hx
  obtain ⟨y, hye⟩ := Int.eq_ofNat_of_zero_le hy
  obtain ⟨px, py⟩ := p
  simp only at hxe hye hx' hy'
  subst hxe hye
  simp only [decode, encode, Int.toNat_natCast]
  rw [show (y * 16 + x) % 16 = x by omega, show (y * 16 + x) / 16 = y by omega]

lemma encode_lt {p : ℤ × ℤ} (hx : 0 ≤ p.1) (hx' : p.1 < 16) (hy : 0 ≤ p.2) (hy' : p.2 < 16) :
    encode p < 256 := by
  obtain ⟨x, hxe⟩ := Int.eq_ofNat_of_zero_le hx
  obtain ⟨y, hye⟩ := Int.eq_ofNat_of_zero_le hy
  obtain ⟨px, py⟩ := p
  simp only at hxe hye hx' hy'
  subst hxe hye
  simp only [encode, Int.toNat_natCast]
  omega

lemma boxMask_testBit (j : ℕ) : boxMask.testBit j = decide (j < 256 ∧ j % 16 + 1 < 16) := by
  by_cases hj : j < 256
  · revert j
    decide +kernel
  · rw [decide_eq_false (by omega), Nat.testBit_lt_two_pow]
    calc boxMask < 2 ^ 256 := by decide +kernel
      _ ≤ 2 ^ j := Nat.pow_le_pow_right (by norm_num) (by omega)

/-- The margin a parent board needs: two free columns and two free rows. -/
def Margin (m : ℕ) : Prop := ∀ i, m.testBit i = true → i % 16 + 2 < 16 ∧ i / 16 + 2 < 16

lemma margin_of_canonical {n : ℕ} {P : ℕ} (hbox : InBox P) (hP : IsCanonicalAnimal n (cells P))
    (hn : n ≤ 14) : Margin P := by
  intro i hi
  have hi' : i < 256 := by
    exact lt_256_of_testBit hbox hi
  have hx := canonicalAnimal_x_le hP ((decode_mem_cells hi').mpr hi)
  have hy := canonicalAnimal_y_le hP ((decode_mem_cells hi').mpr hi)
  simp only [decode] at hx hy
  omega

/-! ## The children of a board -/

lemma testBit_frontier (P' j : ℕ) :
    ((nbrs P' ^^^ (nbrs P' &&& P')) &&& boxMask).testBit j = true ↔
      (nbrs P').testBit j = true ∧ P'.testBit j = false ∧ j < 256 ∧ j % 16 + 1 < 16 := by
  rw [Nat.testBit_land, Nat.testBit_xor, Nat.testBit_land, boxMask_testBit]
  cases (nbrs P').testBit j <;> cases P'.testBit j <;> simp

lemma inBox_frontier (P' : ℕ) : InBox ((nbrs P' ^^^ (nbrs P' &&& P')) &&& boxMask) :=
  inBox_of_testBit fun j hj => ((testBit_frontier P' j).mp hj).2.2.1

lemma noWrap_shift17 {P : ℕ} (hM : Margin P) : NoWrap (P <<< 17) := by
  intro j hj
  rw [Nat.testBit_shiftLeft, Bool.and_eq_true, decide_eq_true_eq] at hj
  obtain ⟨hx, hy⟩ := hM _ hj.2
  omega

lemma cells_shift17_of_margin {P : ℕ} (hM : Margin P) :
    cells (P <<< 17) = translate (1, 1) (cells P) :=
  cells_shiftLeft_17 fun i hi => by have := hM i hi; omega

lemma noWrap_lor_pow {S j : ℕ} (hS : NoWrap S) (hj : j < 256) (hj' : j % 16 + 1 < 16) :
    NoWrap (S ||| 2 ^ j) := by
  intro i hi
  rw [Nat.testBit_lor, Bool.or_eq_true, Nat.testBit_two_pow, decide_eq_true_eq] at hi
  rcases hi with hi | rfl
  · exact hS i hi
  · exact ⟨hj, hj'⟩

lemma sub_xor_pow {S i : ℕ} (hi : S.testBit i = true) : Sub (S ^^^ 2 ^ i) S := fun k hk => by
  rw [Nat.testBit_xor, Nat.testBit_two_pow] at hk
  by_cases h : i = k
  · subst h
    simp [hi] at hk
  · simpa [h] using hk

/-- Removing a cell of a `NoWrap` board with at least two cells: the
connectivity test says whether the cell is a leaf. -/
lemma connected_erase_iff {n S i : ℕ} (hS : NoWrap S) (hn : (cells S).card ≤ n)
    (h2 : 2 ≤ (cells S).card) (hi : S.testBit i = true) :
    connected n (S ^^^ 2 ^ i) = true ↔ IsLeaf (cells S) (decode i) := by
  have hi' : i < 256 := (hS i hi).1
  have hcells : cells (S ^^^ 2 ^ i) = (cells S).erase (decode i) := cells_xor_pow hi
  have hcard : (cells (S ^^^ 2 ^ i)).card = (cells S).card - 1 := by
    rw [hcells, Finset.card_erase_of_mem ((decode_mem_cells hi').mpr hi)]
  have h0 : S ^^^ 2 ^ i ≠ 0 := by
    intro h
    rw [h, cells_zero, Finset.card_empty] at hcard
    omega
  rw [connected_iff (noWrap_of_sub (sub_xor_pow hi) hS) h0 (by omega), hcells, IsLeaf,
    decode_mem_cells hi', hi]
  simp

lemma key_decode_le {i j : ℕ} : key (decode i) ≤ key (decode j) ↔ i ≤ j := by
  simp only [key, decode, Prod.Lex.toLex_le_toLex, Nat.cast_lt, Nat.cast_inj, Nat.cast_le]
  omega

/-- **The first-leaf scan.** With fuel for every bit of `scan`, it returns `c`
exactly when `c` is a leaf in `scan` and no higher bit of `scan` is. -/
lemma firstLeaf_spec {n S : ℕ} (hS : NoWrap S) (hn : (cells S).card ≤ n)
    (h2 : 2 ≤ (cells S).card) :
    ∀ fuel scan, Sub scan S → nbits scan ≤ fuel → ∀ c, c < 256 →
      (firstLeaf n S fuel scan = c ↔
        scan.testBit c = true ∧ IsLeaf (cells S) (decode c) ∧
          ∀ j, scan.testBit j = true → c < j → ¬ IsLeaf (cells S) (decode j)) := by
  have hbox := inBox_of_noWrap hS
  intro fuel
  induction fuel with
  | zero =>
    intro scan hsub hf c hc
    have hbs := inBox_of_sub hsub hbox
    simp only [firstLeaf]
    constructor
    · intro h; omega
    · rintro ⟨hb, -, -⟩
      have : 0 < nbits scan := Finset.card_pos.mpr
        ⟨c, Finset.mem_filter.mpr ⟨Finset.mem_range.mpr hc, hb⟩⟩
      omega
  | succ fuel ih =>
    intro scan hsub hf c hc
    have hbs := inBox_of_sub hsub hbox
    by_cases h0 : scan = 0
    · subst h0
      simp [firstLeaf, show (256 : ℕ) ≠ c by omega]
    · have hL := log2_lt_of_inBox hbs h0
      have hbL : scan.testBit (Nat.log2 scan) = true := Nat.testBit_log2 h0
      have hSL : S.testBit (Nat.log2 scan) = true := hsub _ hbL
      have hleafL := connected_erase_iff hS hn h2 hSL
      simp only [firstLeaf, h0, if_false]
      by_cases hleaf : connected n (S ^^^ 2 ^ Nat.log2 scan) = true
      · rw [if_pos hleaf]
        have hL' := hleafL.mp hleaf
        constructor
        · rintro rfl
          exact ⟨hbL, hL', fun j hj hlt => absurd (le_log2_of_testBit hj) (by omega)⟩
        · rintro ⟨hb, -, hmax⟩
          by_contra hne
          exact hmax _ hbL (lt_of_le_of_ne (le_log2_of_testBit hb) (Ne.symm hne)) hL'
      · rw [if_neg hleaf]
        have hnotL : ¬ IsLeaf (cells S) (decode (Nat.log2 scan)) := fun h => hleaf (hleafL.mpr h)
        have hsub' : Sub (scan ^^^ 2 ^ Nat.log2 scan) S := fun k hk => hsub k (sub_xor_pow hbL k hk)
        have hf' : nbits (scan ^^^ 2 ^ Nat.log2 scan) ≤ fuel := by
          have := nbits_xor_log2 hbs h0; omega
        rw [ih _ hsub' hf' c hc]
        have hbit : ∀ k, (scan ^^^ 2 ^ Nat.log2 scan).testBit k = true ↔
            scan.testBit k = true ∧ k ≠ Nat.log2 scan := by
          intro k
          rw [Nat.testBit_xor, Nat.testBit_two_pow]
          by_cases hk : Nat.log2 scan = k
          · subst hk; simp [hbL]
          · simp [hk, Ne.symm hk]
        constructor
        · rintro ⟨hb, hl, hmax⟩
          refine ⟨((hbit c).mp hb).1, hl, fun j hj hlt => ?_⟩
          by_cases hjL : j = Nat.log2 scan
          · subst hjL; exact hnotL
          · exact hmax j ((hbit j).mpr ⟨hj, hjL⟩) hlt
        · rintro ⟨hb, hl, hmax⟩
          refine ⟨(hbit c).mpr ⟨hb, fun h => hnotL (h ▸ hl)⟩, hl, fun j hj hlt => ?_⟩
          exact hmax j ((hbit j).mp hj).1 hlt

/-- The data of one child board of the anchored `n`-cell board `P`: the
frontier index `j` that passes the first-leaf test gives the adjoined cell
`c = decode j - (1, 1)`. -/
lemma child_of_index {n P j : ℕ} (hbox : InBox P) (hP : IsCanonicalAnimal n (cells P))
    (hn : n ≤ 13)
    (hj : ((nbrs (P <<< 17) ^^^ (nbrs (P <<< 17) &&& (P <<< 17))) &&& boxMask).testBit j = true)
    (hfl : firstLeaf (n + 1) ((P <<< 17) ||| 2 ^ j) 256 ((P <<< 17) ||| 2 ^ j) = j) :
    InBox (reanchor ((P <<< 17) ||| 2 ^ j)) ∧
    ∃ c, c ∉ cells P ∧ (∃ p ∈ cells P, kingAdj p c) ∧ IsDel (insert c (cells P)) c ∧
      decode j = c + (1, 1) ∧
      cells (reanchor ((P <<< 17) ||| 2 ^ j)) = Polyplets.reanchor (insert c (cells P)) := by
  have hM := margin_of_canonical hbox hP (by omega)
  have hn1 : 1 ≤ n := by
    rw [← hP.card]
    exact Finset.card_pos.mpr hP.anchored.nonempty
  have hP'nw := noWrap_shift17 hM
  have hP'cells := cells_shift17_of_margin hM
  obtain ⟨hnb, hnotP, hj256, hjcol⟩ := (testBit_frontier _ _).mp hj
  set c' := decode j with hc'
  have hc'P' : c' ∉ cells (P <<< 17) := fun h => by
    rw [decode_mem_cells hj256] at h
    rw [h] at hnotP
    exact Bool.true_eq_false.mp hnotP
  have hS1nw := noWrap_lor_pow hP'nw hj256 hjcol
  have hS1cells : cells ((P <<< 17) ||| 2 ^ j) = insert c' (cells (P <<< 17)) := by
    rw [cells_lor, cells_pow hj256, Finset.insert_eq, Finset.union_comm]
  have hS1card : (cells ((P <<< 17) ||| 2 ^ j)).card = n + 1 := by
    rw [hS1cells, Finset.card_insert_of_notMem hc'P', hP'cells, card_translate, hP.card]
  have hS1ne : (P <<< 17) ||| 2 ^ j ≠ 0 := by
    intro h
    have h1 := hS1card
    rw [h, cells_zero, Finset.card_empty] at h1
    omega
  have hins : insert c' (translate (1, 1) (cells P))
      = translate (1, 1) (insert (c' - (1, 1)) (cells P)) := by
    rw [translate_insert, sub_add_cancel]
  refine ⟨inBox_shiftRight (inBox_of_noWrap hS1nw), c' - (1, 1), ?_, ?_, ?_,
    (sub_add_cancel c' (1, 1)).symm, ?_⟩
  · intro h
    apply hc'P'
    rw [hP'cells, mem_translate]
    exact h
  · obtain ⟨i, hi, hrel⟩ := testBit_nbrs.mp hnb
    obtain ⟨hi256, hicol⟩ := hP'nw i hi
    have hadj : kingAdj (decode i) c' := (kingAdj_decode_iff hi256 hicol hj256 hjcol).mpr hrel
    refine ⟨decode i - (1, 1), ?_, ?_⟩
    · have := (decode_mem_cells hi256).mpr hi
      rw [hP'cells, mem_translate] at this
      exact this
    · simpa [sub_eq_add_neg] using kingAdj_add (-(1, 1)) hadj
  · have hspec := (firstLeaf_spec hS1nw (le_of_eq hS1card) (by omega) 256 _ (fun _ h => h)
      (nbits_le _) j hj256).mp hfl
    obtain ⟨-, hleaf, hmax⟩ := hspec
    have hdel' : IsDel (cells ((P <<< 17) ||| 2 ^ j)) c' := by
      refine ⟨hleaf, fun x hx hlx => ?_⟩
      obtain ⟨i, hi256, hbi, rfl⟩ := mem_cells.mp hx
      by_contra hlt
      rw [not_le] at hlt
      have hji : j < i := by
        by_contra h
        exact absurd (key_decode_le.mpr (not_lt.mp h)) (not_le.mpr hlt)
      exact hmax i hbi hji hlx
    rw [hS1cells, hP'cells, hins] at hdel'
    exact (isDel_translate _).mp (by rwa [sub_add_cancel])
  · rw [cells_reanchor (inBox_of_noWrap hS1nw) hS1ne, hS1cells, hP'cells, hins, translate,
      reanchor_image_add]

/-- **Soundness of `children`**: every member is the re-anchored parent with
its deletable cell adjoined. -/
lemma children_sound {n P m : ℕ} (hbox : InBox P) (hP : IsCanonicalAnimal n (cells P))
    (hn : n ≤ 13) (hm : m ∈ children (n + 1) P) :
    InBox m ∧ ∃ c, c ∉ cells P ∧ (∃ p ∈ cells P, kingAdj p c) ∧ IsDel (insert c (cells P)) c ∧
      cells m = Polyplets.reanchor (insert c (cells P)) := by
  simp only [children, List.mem_filterMap] at hm
  obtain ⟨j, hjmem, hj⟩ := hm
  split at hj
  · rename_i hfl
    rw [Option.some.injEq] at hj
    subst hj
    rw [mem_bitsOf' (inBox_frontier _)] at hjmem
    obtain ⟨h1, c, h2, h3, h4, -, h5⟩ := child_of_index hbox hP hn hjmem hfl
    exact ⟨h1, c, h2, h3, h4, h5⟩
  · simp at hj

/-- **Completeness of `children`**: every adjoinable deletable cell occurs. -/
lemma children_complete {n P : ℕ} (hbox : InBox P) (hP : IsCanonicalAnimal n (cells P))
    (hn : n ≤ 13) {c : ℤ × ℤ} (hc : c ∉ cells P) (hadj : ∃ p ∈ cells P, kingAdj p c)
    (hdel : IsDel (insert c (cells P)) c) :
    ∃ m ∈ children (n + 1) P, cells m = Polyplets.reanchor (insert c (cells P)) := by
  have hM := margin_of_canonical hbox hP (by omega)
  have hP'nw := noWrap_shift17 hM
  have hP'cells := cells_shift17_of_margin hM
  obtain ⟨p, hp, hpc⟩ := hadj
  have hpx := canonicalAnimal_x_le hP hp
  have hpy := canonicalAnimal_y_le hP hp
  have hpx0 := hP.anchored.x_nonneg p hp
  have hpy0 := hP.anchored.y_nonneg p hp
  have hadjx := abs_le.mp hpc.2.1
  have hadjy := abs_le.mp hpc.2.2
  have hn1 : 1 ≤ n := by
    rw [← hP.card]
    exact Finset.card_pos.mpr hP.anchored.nonempty
  -- the shifted cells and their indices
  set c' := c + (1, 1) with hc'
  set p' := p + (1, 1) with hp'
  have hc'x : 0 ≤ c'.1 ∧ c'.1 < 15 := by simp only [hc', Prod.fst_add]; omega
  have hc'y : 0 ≤ c'.2 ∧ c'.2 < 15 := by simp only [hc', Prod.snd_add]; omega
  have hp'x : 0 ≤ p'.1 ∧ p'.1 < 15 := by simp only [hp', Prod.fst_add]; omega
  have hp'y : 0 ≤ p'.2 ∧ p'.2 < 15 := by simp only [hp', Prod.snd_add]; omega
  set j := encode c' with hj
  set i := encode p' with hi
  have hdj : decode j = c' := decode_encode hc'x.1 (by omega) hc'y.1 (by omega)
  have hdi : decode i = p' := decode_encode hp'x.1 (by omega) hp'y.1 (by omega)
  have hj256 : j < 256 ∧ j % 16 + 1 < 16 := by
    have h1 := congrArg Prod.fst hdj
    have h2 := congrArg Prod.snd hdj
    simp only [decode] at h1 h2
    omega
  have hi256 : i < 256 ∧ i % 16 + 1 < 16 := by
    have h1 := congrArg Prod.fst hdi
    have h2 := congrArg Prod.snd hdi
    simp only [decode] at h1 h2
    omega
  have hp'mem : p' ∈ cells (P <<< 17) := by
    rw [hP'cells]
    exact translate_mem hp
  have hc'mem : c' ∉ cells (P <<< 17) := by
    rw [hP'cells, mem_translate, hc', add_sub_cancel_right]
    exact hc
  have hbi : (P <<< 17).testBit i = true :=
    (decode_mem_cells hi256.1).mp (by rw [hdi]; exact hp'mem)
  have hbj : (P <<< 17).testBit j = false := by
    have := (decode_mem_cells (m := P <<< 17) hj256.1)
    rw [hdj] at this
    cases h : (P <<< 17).testBit j
    · rfl
    · exact absurd (this.mpr h) hc'mem
  have hadj' : kingAdj p' c' := kingAdj_add (1, 1) hpc
  have hF : ((nbrs (P <<< 17) ^^^ (nbrs (P <<< 17) &&& (P <<< 17))) &&& boxMask).testBit j
      = true := by
    rw [testBit_frontier]
    refine ⟨testBit_nbrs.mpr ⟨i, hbi, ?_⟩, hbj, hj256.1, hj256.2⟩
    rw [← kingAdj_decode_iff hi256.1 hi256.2 hj256.1 hj256.2, hdi, hdj]
    exact hadj'
  -- the first-leaf test passes at `j`
  have hS1nw := noWrap_lor_pow hP'nw hj256.1 hj256.2
  have hS1cells : cells ((P <<< 17) ||| 2 ^ j) = translate (1, 1) (insert c (cells P)) := by
    rw [cells_lor, cells_pow hj256.1, hdj, Finset.union_comm, ← Finset.insert_eq, hP'cells, hc',
      ← translate_insert]
  have hS1card : (cells ((P <<< 17) ||| 2 ^ j)).card = n + 1 := by
    rw [hS1cells, card_translate, Finset.card_insert_of_notMem hc, hP.card]
  have hdel' : IsDel (cells ((P <<< 17) ||| 2 ^ j)) c' := by
    rw [hS1cells, hc']
    exact (isDel_translate _).mpr hdel
  have hfl : firstLeaf (n + 1) ((P <<< 17) ||| 2 ^ j) 256 ((P <<< 17) ||| 2 ^ j) = j := by
    rw [firstLeaf_spec hS1nw (le_of_eq hS1card) (by omega) 256 _ (fun _ h => h) (nbits_le _)
      j hj256.1]
    refine ⟨?_, by rw [hdj]; exact hdel'.1, fun k hk hlt hleaf => ?_⟩
    · rw [Nat.testBit_lor, Nat.testBit_two_pow_self, Bool.or_true]
    · have hk256 := (hS1nw k hk).1
      have := hdel'.2 (decode k) ((decode_mem_cells hk256).mpr hk) hleaf
      rw [← hdj, key_decode_le] at this
      omega
  refine ⟨reanchor ((P <<< 17) ||| 2 ^ j), ?_, ?_⟩
  · simp only [children, List.mem_filterMap]
    exact ⟨j, (mem_bitsOf' (inBox_frontier _)).mpr hF, by simp [hfl]⟩
  · have hS1ne : (P <<< 17) ||| 2 ^ j ≠ 0 := by
      intro h
      have h1 := hS1card
      rw [h, cells_zero, Finset.card_empty] at h1
      omega
    rw [cells_reanchor (inBox_of_noWrap hS1nw) hS1ne, hS1cells, translate, reanchor_image_add]

/-- The boards of `children` are pairwise distinct. -/
lemma children_nodup {n P : ℕ} (hbox : InBox P) (hP : IsCanonicalAnimal n (cells P))
    (hn : n ≤ 13) : ((children (n + 1) P).map cells).Nodup := by
  have hPne : (cells P).Nonempty := hP.anchored.nonempty
  refine List.Nodup.map_on (fun m hm m' hm' h => ?_) ?_
  · obtain ⟨h1, -⟩ := children_sound hbox hP hn hm
    obtain ⟨h2, -⟩ := children_sound hbox hP hn hm'
    exact eq_of_cells_eq h1 h2 h
  · have hnd := List.Pairwise.and_mem.mp (bitsOf_nodup (inBox_frontier (P <<< 17)) 256 (nbits_le _))
    unfold children
    refine List.Pairwise.filterMap (S := (· ≠ ·)) _ (fun a a' ⟨ha, ha', hne⟩ b hb b' hb' => ?_) hnd
    dsimp only at hb hb'
    split at hb
    · rename_i hfl
      split at hb'
      · rename_i hfl'
        rw [Option.some.injEq] at hb hb'
        subst hb hb'
        intro heq
        rw [mem_bitsOf' (inBox_frontier _)] at ha ha'
        obtain ⟨-, c, hc, -, hdel, hdc, hcells⟩ := child_of_index hbox hP hn ha hfl
        obtain ⟨-, c', hc', -, hdel', hdc', hcells'⟩ := child_of_index hbox hP hn ha' hfl'
        have : c = c' := child_inj hPne hc hc' hdel hdel' (by rw [← hcells, ← hcells', heq])
        subst this
        exact hne (decode_inj (hdc.trans hdc'.symm))
      · simp at hb'
    · simp at hb

/-! ## The list of all animals -/

lemma L_succ (n : ℕ) (hn : 1 ≤ n) : L (n + 1) = (L n).flatMap (children (n + 1)) := by
  obtain ⟨k, rfl⟩ : ∃ k, n = k + 1 := ⟨n - 1, by omega⟩
  rfl

/-- `{(0, 0)}` is the only canonical animal of one cell. -/
lemma isCanonicalAnimal_one_iff {S : Finset (ℤ × ℤ)} :
    IsCanonicalAnimal 1 S ↔ S = {((0 : ℤ), (0 : ℤ))} := by
  constructor
  · intro h
    obtain ⟨p, hp⟩ := Finset.card_eq_one.mp h.card
    obtain ⟨q, hq, hq1⟩ := h.anchored.x_zero
    obtain ⟨r, hr, hr2⟩ := h.anchored.y_zero
    rw [hp, Finset.mem_singleton] at hq hr
    rw [hp]
    congr 1
    exact Prod.ext (hq ▸ hq1) (hr ▸ hr2)
  · rintro rfl
    refine ⟨Finset.card_singleton _, kingConnected_singleton _, ?_⟩
    · refine ⟨fun p hp => ?_, ⟨_, Finset.mem_singleton_self _, rfl⟩, fun p hp => ?_,
        ⟨_, Finset.mem_singleton_self _, rfl⟩⟩ <;>
      · rw [Finset.mem_singleton] at hp
        subst hp
        exact le_rfl

/-- **The enumeration is exact**: for `1 ≤ n ≤ 14`, the boards of `L n` are
in the box, pairwise distinct, and their cells are exactly the canonical
animals of `n` cells. -/
theorem L_spec : ∀ n, 1 ≤ n → n ≤ 14 →
    (∀ m ∈ L n, InBox m) ∧ ((L n).map cells).Nodup ∧
      ∀ S, IsCanonicalAnimal n S ↔ ∃ m ∈ L n, cells m = S := by
  intro n
  induction n with
  | zero => intro h; omega
  | succ n ih =>
    intro _ hn
    rcases Nat.eq_zero_or_pos n with rfl | hn1
    · refine ⟨?_, ?_, ?_⟩
      · intro m hm
        simp only [L, List.mem_singleton] at hm
        subst hm
        norm_num [InBox]
      · simp [L]
      · intro S
        rw [isCanonicalAnimal_one_iff]
        simp only [L, List.mem_singleton, exists_eq_left]
        rw [show (1 : ℕ) = 2 ^ 0 from rfl, cells_pow (by norm_num)]
        constructor <;> rintro rfl <;> rfl
    · obtain ⟨hbox, hnd, hmem⟩ := ih hn1 (by omega)
      rw [L_succ n hn1]
      have hcan : ∀ P ∈ L n, IsCanonicalAnimal n (cells P) := fun P hP =>
        (hmem _).mpr ⟨P, hP, rfl⟩
      refine ⟨?_, ?_, ?_⟩
      · intro m hm
        obtain ⟨P, hP, hmP⟩ := List.mem_flatMap.mp hm
        exact (children_sound (hbox P hP) (hcan P hP) (by omega) hmP).1
      · rw [List.map_flatMap, List.nodup_flatMap]
        refine ⟨fun P hP => children_nodup (hbox P hP) (hcan P hP) (by omega), ?_⟩
        rw [List.Nodup, List.pairwise_map] at hnd
        refine (List.Pairwise.and_mem.mp hnd).imp fun {P P'} ⟨hP, hP', hne⟩ => ?_
        intro S hS hS'
        obtain ⟨m, hm, rfl⟩ := List.mem_map.mp hS
        obtain ⟨m', hm', he⟩ := List.mem_map.mp hS'
        obtain ⟨-, c, hc, -, hdel, hcells⟩ :=
          children_sound (hbox P hP) (hcan P hP) (by omega) hm
        obtain ⟨-, c', hc', -, hdel', hcells'⟩ :=
          children_sound (hbox P' hP') (hcan P' hP') (by omega) hm'
        apply hne
        have := parent_eq_of_child_eq hc hc' hdel hdel' (by rw [← hcells, ← hcells', he])
        rwa [reanchor_eq_self (hcan P hP).anchored, reanchor_eq_self (hcan P' hP').anchored]
          at this
      · intro S
        constructor
        · intro hS
          have h2 : 2 ≤ S.card := by rw [hS.card]; omega
          obtain ⟨c₀, hdel⟩ := exists_isDel hS.conn h2
          have hc₀S := hdel.1.1
          have hQconn : KingConnected (S.erase c₀) := hdel.1.2
          have hQcard : (S.erase c₀).card = n := by
            rw [Finset.card_erase_of_mem hc₀S, hS.card, Nat.add_sub_cancel]
          have hQne : (S.erase c₀).Nonempty := Finset.card_pos.mp (by omega)
          have hP₀ : IsCanonicalAnimal n (Polyplets.reanchor (S.erase c₀)) :=
            ⟨by rw [reanchor_card, hQcard], kingConnected_reanchor hQconn, reanchor_anchored hQne⟩
          obtain ⟨P, hP, hPc⟩ := (hmem _).mp hP₀
          have hP₀eq : cells P = translate (-anchorVec (S.erase c₀)) (S.erase c₀) := by
            rw [hPc, reanchor_eq_translate]
          have hcnot : c₀ - anchorVec (S.erase c₀) ∉ cells P := by
            rw [hP₀eq, mem_translate, sub_neg_eq_add, sub_add_cancel]
            exact Finset.notMem_erase c₀ S
          have hadj : ∃ p ∈ cells P, kingAdj p (c₀ - anchorVec (S.erase c₀)) := by
            obtain ⟨q, hqS, hqne, hadj⟩ := exists_adj_of_connected hS.conn h2 hc₀S
            refine ⟨q - anchorVec (S.erase c₀), ?_, ?_⟩
            · rw [hP₀eq, mem_translate, sub_neg_eq_add, sub_add_cancel]
              exact Finset.mem_erase.mpr ⟨hqne, hqS⟩
            · have := kingAdj_add (-anchorVec (S.erase c₀)) (kingAdj_symm hadj)
              simpa [sub_eq_add_neg] using this
          have hins : insert (c₀ - anchorVec (S.erase c₀)) (cells P)
              = translate (-anchorVec (S.erase c₀)) S := by
            rw [hP₀eq, sub_eq_add_neg, ← translate_insert, Finset.insert_erase hc₀S]
          have hdel' : IsDel (insert (c₀ - anchorVec (S.erase c₀)) (cells P))
              (c₀ - anchorVec (S.erase c₀)) := by
            rw [hins, sub_eq_add_neg]
            exact (isDel_translate _).mpr hdel
          obtain ⟨m, hm, hmc⟩ :=
            children_complete (hbox P hP) (hcan P hP) (by omega) hcnot hadj hdel'
          refine ⟨m, List.mem_flatMap.mpr ⟨P, hP, hm⟩, ?_⟩
          rw [hmc, hins, translate, reanchor_image_add, reanchor_eq_self hS.anchored]
        · rintro ⟨m, hm, rfl⟩
          obtain ⟨P, hP, hmP⟩ := List.mem_flatMap.mp hm
          obtain ⟨-, c, hc, hadj, -, hcells⟩ :=
            children_sound (hbox P hP) (hcan P hP) (by omega) hmP
          rw [hcells]
          exact isCanonicalAnimal_insert_reanchor (hcan P hP) hc hadj

lemma ne_zero_of_mem_L {n m : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 14) (hm : m ∈ L n) : m ≠ 0 := by
  intro h
  have := ((L_spec n h1 hn).2.2 _).mpr ⟨m, hm, rfl⟩
  rw [h, cells_zero] at this
  exact Finset.not_nonempty_empty this.anchored.nonempty

/-! ## The counts -/

/-- **A count over the animals of `n` cells is the length of a filter of
`L n`**, for a board test `q` that decides the predicate `Q` on the cells. -/
lemma ncard_eq_length {n : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 14) {Q : Finset (ℤ × ℤ) → Prop}
    {q : ℕ → Bool} (hq : ∀ m ∈ L n, q m = true ↔ Q (cells m)) :
    {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S ∧ Q S}.ncard = ((L n).filter q).length := by
  obtain ⟨-, hnd, hmem⟩ := L_spec n h1 hn
  have hset : {S : Finset (ℤ × ℤ) | IsCanonicalAnimal n S ∧ Q S}
      = ↑((((L n).filter q).map cells).toFinset) := by
    ext S
    simp only [Set.mem_setOf_eq, Finset.mem_coe, List.mem_toFinset, List.mem_map, List.mem_filter]
    constructor
    · rintro ⟨hS, hQ⟩
      obtain ⟨m, hm, rfl⟩ := (hmem _).mp hS
      exact ⟨m, ⟨hm, (hq m hm).mpr hQ⟩, rfl⟩
    · rintro ⟨m, ⟨hm, hqm⟩, rfl⟩
      exact ⟨(hmem _).mpr ⟨m, hm, rfl⟩, (hq m hm).mp hqm⟩
  rw [hset, Set.ncard_coe_finset,
    List.toFinset_card_of_nodup (hnd.sublist (List.Sublist.map _ List.filter_sublist)),
    List.length_map]

/-- **`a n` is a list length.** -/
theorem a_eq_length {n : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 14) : a n = (L n).length := by
  have h := ncard_eq_length h1 hn (Q := fun _ => True) (q := fun _ => true) (fun _ _ => by simp)
  simpa [a, List.filter_true] using h

/-- **`T n H` is a filtered list length.** -/
theorem T_eq_length {n H : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 14) :
    T n H = ((L n).filter fun m => height m = H).length := by
  have hset : {S : Finset (ℤ × ℤ) | IsCanonical n H S}
      = {S | IsCanonicalAnimal n S ∧ heightOf S = H} := by
    ext S
    exact isCanonical_iff n H S
  rw [T, hset, ncard_eq_length h1 hn]
  intro m hm
  rw [decide_eq_true_eq, height_eq ((L_spec n h1 hn).1 m hm) (ne_zero_of_mem_L h1 hn hm)]

/-- **The walk-top count `d k H` is a filtered list length.** -/
theorem d_eq_length {k H : ℕ} (hH : 1 ≤ H) (hn : H + k ≤ 14) :
    d k H = ((L (H + k)).filter fun m => height m = H ∧ rowCount m (H - 1) = 1).length := by
  have hset : (Dc k H : Set (Finset (ℤ × ℤ)))
      = {S | IsCanonicalAnimal (H + k) S ∧ (heightOf S = H ∧ rowSize S ((H : ℤ) - 1) = 1)} := by
    ext S
    simp only [Finset.mem_coe, mem_Dc, isCanonical_iff, Set.mem_setOf_eq, and_assoc]
  rw [d, ← Set.ncard_coe_finset, hset, ncard_eq_length (by omega) hn]
  intro m hm
  have hbox := (L_spec _ (by omega) hn).1 m hm
  rw [decide_eq_true_eq, height_eq hbox (ne_zero_of_mem_L (by omega) hn hm), rowCount_eq hbox,
    Nat.cast_pred hH]

/-! ## Cluster configurations -/

/-- `rowSize` is unchanged by a horizontal translation. -/
lemma rowSize_translate_x (t : ℤ) (S : Finset (ℤ × ℤ)) (y : ℤ) :
    rowSize (translate (t, 0) S) y = rowSize S y := by
  rw [rowSize, rowSize]
  have : (translate (t, 0) S).filter (fun c => c.2 = y)
      = translate (t, 0) (S.filter fun c => c.2 = y) := by
    ext c
    simp only [Finset.mem_filter, mem_translate, Prod.snd_sub, sub_zero]
  rw [this, card_translate]

lemma anchorVec_snd_eq_zero {S : Finset (ℤ × ℤ)} (h0 : ∀ p ∈ S, 0 ≤ p.2) (hz : ∃ p ∈ S, p.2 = 0) :
    (anchorVec S).2 = 0 := by
  obtain ⟨p, hp, hp2⟩ := hz
  have hne : S.Nonempty := ⟨p, hp⟩
  rw [anchorVec, dif_pos hne]
  refine le_antisymm ?_ (Finset.le_inf' hne _ h0)
  have := Finset.inf'_le Prod.snd hp
  simpa [hp2] using this

/-- The single cell of a one-cell row. -/
lemma eq_of_rowSize_one {S : Finset (ℤ × ℤ)} {y : ℤ} (h : rowSize S y = 1) {p q : ℤ × ℤ}
    (hp : p ∈ S) (hq : q ∈ S) (hpy : p.2 = y) (hqy : q.2 = y) : p = q := by
  obtain ⟨r, hr⟩ := Finset.card_eq_one.mp h
  have hp' : p ∈ S.filter (fun c => c.2 = y) := Finset.mem_filter.mpr ⟨hp, hpy⟩
  have hq' : q ∈ S.filter (fun c => c.2 = y) := Finset.mem_filter.mpr ⟨hq, hqy⟩
  rw [hr, Finset.mem_singleton] at hp' hq'
  rw [hp', hq']

/-- **Configurations pinned at the origin and canonical animals with a one-cell
bottom row are in bijection**, for any condition `R` on the rows that a
horizontal translation preserves: slide the configuration so that its bounding
box touches column `0`, and back. -/
lemma ncard_config {N h : ℕ} {R : Finset (ℤ × ℤ) → Prop}
    (hR : ∀ (t : ℤ) S, R (translate (t, 0) S) ↔ R S)
    (hRtop : ∀ S, R S → ∃ p ∈ S, p.2 = (h : ℤ) - 1) :
    {S : Finset (ℤ × ℤ) | S.card = N ∧ ((0 : ℤ), (0 : ℤ)) ∈ S ∧
        (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (h : ℤ) - 1) ∧ rowSize S 0 = 1 ∧ R S ∧ KingConnected S}.ncard
      = {S : Finset (ℤ × ℤ) | IsCanonicalAnimal N S ∧
          (heightOf S = h ∧ rowSize S 0 = 1 ∧ R S)}.ncard := by
  -- the re-anchoring of a configuration is a horizontal slide
  have hre : ∀ S : Finset (ℤ × ℤ), ((0 : ℤ), (0 : ℤ)) ∈ S → (∀ p ∈ S, 0 ≤ p.2) →
      Polyplets.reanchor S = translate (-(anchorVec S).1, 0) S := by
    intro S h0 hrows
    rw [reanchor_eq_translate]
    congr 1
    exact Prod.ext rfl (by simp [anchorVec_snd_eq_zero hrows ⟨_, h0, rfl⟩])
  refine Set.ncard_congr (fun S _ => Polyplets.reanchor S) ?_ ?_ ?_
  · rintro S ⟨hcard, h0, hrows, hr0, hRS, hconn⟩
    have hne : S.Nonempty := ⟨_, h0⟩
    have hre' := hre S h0 fun p hp => (hrows p hp).1
    have hcan : IsCanonical N h (Polyplets.reanchor S) := by
      refine ⟨by rw [reanchor_card, hcard], kingConnected_reanchor hconn, reanchor_anchored hne,
        ?_, ?_⟩
      · intro p hp
        rw [hre', mem_translate] at hp
        have := (hrows _ hp).2
        simpa using this
      · obtain ⟨p, hp, hpy⟩ := hRtop S hRS
        refine ⟨p + (-(anchorVec S).1, 0), by rw [hre']; exact translate_mem hp, by simpa using hpy⟩
    refine ⟨((isCanonical_iff N h _).mp hcan).1, ((isCanonical_iff N h _).mp hcan).2, ?_, ?_⟩
    · rw [hre', rowSize_translate_x]
      exact hr0
    · rw [hre', hR]
      exact hRS
  · rintro S₁ S₂ ⟨-, h0₁, hrows₁, hr0₁, -, -⟩ ⟨-, h0₂, hrows₂, hr0₂, -, -⟩ heq
    have hre₁ := hre S₁ h0₁ fun p hp => (hrows₁ p hp).1
    have hre₂ := hre S₂ h0₂ fun p hp => (hrows₂ p hp).1
    rw [hre₁, hre₂] at heq
    have hm₁ : ((0 : ℤ), (0 : ℤ)) + (-(anchorVec S₁).1, 0)
        ∈ translate (-(anchorVec S₂).1, 0) S₂ := by
      rw [← heq]; exact translate_mem h0₁
    have hm₂ : ((0 : ℤ), (0 : ℤ)) + (-(anchorVec S₂).1, 0) ∈ translate (-(anchorVec S₂).1, 0) S₂ :=
      translate_mem h0₂
    have hrs : rowSize (translate (-(anchorVec S₂).1, 0) S₂) 0 = 1 := by
      rw [rowSize_translate_x]; exact hr0₂
    have := eq_of_rowSize_one hrs hm₁ hm₂ (by simp) (by simp)
    have hax : (anchorVec S₁).1 = (anchorVec S₂).1 := by
      simp only [Prod.mk_add_mk, Prod.mk.injEq] at this
      omega
    have h1 := congrArg (translate ((anchorVec S₂).1, 0)) heq
    rwa [hax, translate_translate, translate_translate, Prod.mk_add_mk, neg_add_cancel, add_zero,
      Prod.mk_zero_zero, translate_zero, translate_zero] at h1
  · rintro S' ⟨hS', hh, hr0, hRS'⟩
    have hcan := (isCanonical_iff N h S').mpr ⟨hS', hh⟩
    obtain ⟨q, hq, hqy⟩ : ∃ q ∈ S', q.2 = 0 := by
      obtain ⟨r, hr⟩ := Finset.card_eq_one.mp hr0
      have : r ∈ S'.filter (fun c => c.2 = 0) := by rw [hr]; exact Finset.mem_singleton_self r
      exact ⟨r, (Finset.mem_filter.mp this).1, (Finset.mem_filter.mp this).2⟩
    refine ⟨translate (-q.1, 0) S', ⟨?_, ?_, ?_, ?_, ?_, ?_⟩, ?_⟩
    · rw [card_translate, hS'.card]
    · have := translate_mem (v := (-q.1, 0)) hq
      rwa [show q + (-q.1, 0) = ((0 : ℤ), (0 : ℤ)) from Prod.ext (by simp) (by simp [hqy])] at this
    · intro p hp
      rw [mem_translate] at hp
      have h1 := hS'.anchored.y_nonneg _ hp
      have h2 := hcan.y_le _ hp
      simp only [Prod.snd_sub, sub_zero] at h1 h2
      exact ⟨h1, h2⟩
    · rw [rowSize_translate_x]; exact hr0
    · rw [hR]; exact hRS'
    · exact kingConnected_translate _ hS'.conn
    · have ha : anchorVec (translate (-q.1, 0) S') = (-q.1, 0) := by
        rw [show translate (-q.1, 0) S' = S'.image (fun p => p + (-q.1, 0)) from rfl,
          anchorVec_image_add hS'.anchored.nonempty, anchorVec_eq_zero hS'.anchored, zero_add]
      rw [reanchor_eq_translate, ha, translate_translate, add_neg_cancel, translate_zero]

/-- The cluster rows `1 … ℓ` of a board each hold at least two cells. -/
def Multi (m ℓ : ℕ) : Prop := ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowCount m i

instance (m ℓ : ℕ) : Decidable (Multi m ℓ) := by
  unfold Multi
  infer_instance

lemma multi_iff {m ℓ : ℕ} (hm : InBox m) :
    Multi m ℓ ↔ ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize (cells m) (i : ℤ) := by
  simp only [Multi, rowCount_eq hm]

/-- **The interior weight `V ℓ j` is a filtered list length.** -/
theorem V_eq_length {ℓ j : ℕ} (hn : ℓ + j + 2 ≤ 14) :
    V ℓ j = ((L (ℓ + j + 2)).filter fun m => height m = ℓ + 2 ∧ rowCount m 0 = 1 ∧
      rowCount m (ℓ + 1) = 1 ∧ Multi m ℓ).length := by
  have hset : (CFGV ℓ j : Set (Finset (ℤ × ℤ)))
      = {S | S.card = ℓ + j + 2 ∧ ((0 : ℤ), (0 : ℤ)) ∈ S ∧
          (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ ((ℓ + 2 : ℕ) : ℤ) - 1) ∧ rowSize S 0 = 1 ∧
          (rowSize S ((ℓ : ℤ) + 1) = 1 ∧ ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧
          KingConnected S} := by
    ext S
    simp only [Finset.mem_coe, mem_CFGV, Set.mem_setOf_eq]
    push_cast
    constructor
    · rintro ⟨a, b, c, d, e, f, g⟩
      exact ⟨a, b, fun p hp => ⟨(c p hp).1, by have := (c p hp).2; omega⟩, d, ⟨e, f⟩, g⟩
    · rintro ⟨a, b, c, d, ⟨e, f⟩, g⟩
      exact ⟨a, b, fun p hp => ⟨(c p hp).1, by have := (c p hp).2; omega⟩, d, e, f, g⟩
  rw [V, ← Set.ncard_coe_finset, hset, ncard_config (h := ℓ + 2)
    (R := fun S => rowSize S ((ℓ : ℤ) + 1) = 1 ∧ ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ))
    (fun t S => by simp only [rowSize_translate_x]) ?_, ncard_eq_length (by omega) hn]
  · intro m hm
    have hbox := (L_spec _ (by omega) hn).1 m hm
    simp only [decide_eq_true_eq, height_eq hbox (ne_zero_of_mem_L (by omega) hn hm),
      rowCount_eq hbox, multi_iff hbox, Nat.cast_zero, Nat.cast_add, Nat.cast_one]
  · rintro S ⟨htop, -⟩
    obtain ⟨r, hr⟩ := Finset.card_eq_one.mp htop
    have : r ∈ S.filter (fun c => c.2 = (ℓ : ℤ) + 1) := by
      rw [hr]; exact Finset.mem_singleton_self r
    rw [Finset.mem_filter] at this
    exact ⟨r, this.1, by rw [this.2]; push_cast; ring⟩

/-- **The top-edge weight `Vt ℓ j` is a filtered list length.** -/
theorem Vt_eq_length {ℓ j : ℕ} (hℓ : 1 ≤ ℓ) (hn : ℓ + j + 1 ≤ 14) :
    Vt ℓ j = ((L (ℓ + j + 1)).filter fun m => height m = ℓ + 1 ∧ rowCount m 0 = 1 ∧
      Multi m ℓ).length := by
  have hset : (CFGVt ℓ j : Set (Finset (ℤ × ℤ)))
      = {S | S.card = ℓ + j + 1 ∧ ((0 : ℤ), (0 : ℤ)) ∈ S ∧
          (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ ((ℓ + 1 : ℕ) : ℤ) - 1) ∧ rowSize S 0 = 1 ∧
          (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧ KingConnected S} := by
    ext S
    simp only [Finset.mem_coe, mem_CFGVt, Set.mem_setOf_eq]
    push_cast
    constructor
    · rintro ⟨a, b, c, d, e, f⟩
      exact ⟨a, b, fun p hp => ⟨(c p hp).1, by have := (c p hp).2; omega⟩, d, e, f⟩
    · rintro ⟨a, b, c, d, e, f⟩
      exact ⟨a, b, fun p hp => ⟨(c p hp).1, by have := (c p hp).2; omega⟩, d, e, f⟩
  rw [Vt, ← Set.ncard_coe_finset, hset, ncard_config (h := ℓ + 1)
    (R := fun S => ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ))
    (fun t S => by simp only [rowSize_translate_x]) ?_, ncard_eq_length (by omega) hn]
  · intro m hm
    have hbox := (L_spec _ (by omega) hn).1 m hm
    simp only [decide_eq_true_eq, height_eq hbox (ne_zero_of_mem_L (by omega) hn hm),
      rowCount_eq hbox, multi_iff hbox, Nat.cast_zero]
  · intro S hmulti
    have h2 : 2 ≤ (S.filter fun c => c.2 = (ℓ : ℤ)).card :=
      hmulti ℓ (Finset.mem_Icc.mpr ⟨hℓ, le_rfl⟩)
    obtain ⟨r, hr⟩ :=
      Finset.card_pos.mp (show 0 < (S.filter fun c => c.2 = (ℓ : ℤ)).card by omega)
    rw [Finset.mem_filter] at hr
    exact ⟨r, hr.1, by rw [hr.2]; push_cast; ring⟩

/-! ## Symmetries -/

/-- The board of `g` applied to the cells of `m`: each cell is moved, shifted
by `(8, 8)` to stay in the box, and the result is re-anchored. -/
def transform (g : D4) (m : ℕ) : ℕ :=
  reanchor ((bitsOf 256 m).foldl
    (fun acc i => acc ||| 2 ^ encode (D4.toFun g (decode i) + (8, 8))) 0)

lemma cells_foldl_lor (f : ℕ → ℕ) : ∀ (l : List ℕ) (a : ℕ), (∀ i ∈ l, f i < 256) →
    cells (l.foldl (fun acc i => acc ||| 2 ^ f i) a)
      = cells a ∪ (l.map fun i => decode (f i)).toFinset := by
  intro l
  induction l with
  | nil => intro a _; simp
  | cons i l ih =>
    intro a h
    rw [List.foldl_cons, ih _ fun k hk => h k (List.mem_cons_of_mem _ hk), cells_lor,
      cells_pow (h i (List.mem_cons_self ..)), List.map_cons, List.toFinset_cons]
    ext p
    simp only [Finset.mem_union, Finset.mem_singleton, Finset.mem_insert]
    tauto

lemma inBox_foldl_lor (f : ℕ → ℕ) : ∀ (l : List ℕ) (a : ℕ), InBox a → (∀ i ∈ l, f i < 256) →
    InBox (l.foldl (fun acc i => acc ||| 2 ^ f i) a) := by
  intro l
  induction l with
  | nil => intro a ha _; exact ha
  | cons i l ih =>
    intro a ha h
    rw [List.foldl_cons]
    refine ih _ ?_ fun k hk => h k (List.mem_cons_of_mem _ hk)
    refine inBox_of_testBit fun k hk => ?_
    rw [Nat.testBit_lor, Bool.or_eq_true, Nat.testBit_two_pow, decide_eq_true_eq] at hk
    rcases hk with hk | rfl
    · exact lt_256_of_testBit ha hk
    · exact h i (List.mem_cons_self ..)

/-- The eight symmetries permute and negate coordinates, so they preserve the
larger absolute coordinate. -/
lemma max_abs_toFun (g : D4) (p : ℤ × ℤ) :
    max |(D4.toFun g p).1| |(D4.toFun g p).2| = max |p.1| |p.2| := by
  have hquarter : ∀ p : ℤ × ℤ, max |(quarter p).1| |(quarter p).2| = max |p.1| |p.2| := by
    intro p
    simp only [quarter, abs_neg, max_comm]
  have hq : ∀ k (p : ℤ × ℤ), max |(quarter^[k] p).1| |(quarter^[k] p).2| = max |p.1| |p.2| := by
    intro k
    induction k with
    | zero => intro p; rfl
    | succ k ih =>
      intro p
      rw [Function.iterate_succ_apply', hquarter, ih]
  have hm : ∀ p : ℤ × ℤ, max |(mirror p).1| |(mirror p).2| = max |p.1| |p.2| := by
    intro p
    simp only [mirror, abs_neg]
  rcases g with i | i
  · exact hq _ p
  · exact (hm _).trans (hq _ p)

/-- The transformed board carries the transformed cells, re-anchored. -/
lemma cells_transform {n : ℕ} (g : D4) {m : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 7) (hm : m ∈ L n) :
    InBox (transform g m) ∧
      cells (transform g m) = Polyplets.reanchor ((cells m).image (D4.toFun g)) := by
  obtain ⟨hbox, -, hmem⟩ := L_spec n h1 (by omega)
  have hcan := (hmem _).mpr ⟨m, hm, rfl⟩
  have hb := hbox m hm
  set f : ℕ → ℕ := fun i => encode (D4.toFun g (decode i) + (8, 8)) with hf
  have hin : ∀ i ∈ bitsOf 256 m, f i < 256 ∧ decode (f i) = D4.toFun g (decode i) + (8, 8) := by
    intro i hi
    rw [mem_bitsOf' hb] at hi
    have hi256 : i < 256 := lt_256_of_testBit hb hi
    have hc := (decode_mem_cells hi256).mpr hi
    have hx := canonicalAnimal_x_le hcan hc
    have hy := canonicalAnimal_y_le hcan hc
    have hx0 := hcan.anchored.x_nonneg _ hc
    have hy0 := hcan.anchored.y_nonneg _ hc
    have hmax := max_abs_toFun g (decode i)
    have hbound : max |(decode i).1| |(decode i).2| ≤ 6 :=
      max_le (abs_le.mpr ⟨by omega, by omega⟩) (abs_le.mpr ⟨by omega, by omega⟩)
    have hbx : |(D4.toFun g (decode i)).1| ≤ 6 := by
      have := le_max_left |(D4.toFun g (decode i)).1| |(D4.toFun g (decode i)).2|
      rw [hmax] at this
      exact this.trans hbound
    have hby : |(D4.toFun g (decode i)).2| ≤ 6 := by
      have := le_max_right |(D4.toFun g (decode i)).1| |(D4.toFun g (decode i)).2|
      rw [hmax] at this
      exact this.trans hbound
    rw [abs_le] at hbx hby
    have hx1 : 0 ≤ (D4.toFun g (decode i) + (8, 8)).1 ∧
        (D4.toFun g (decode i) + (8, 8)).1 < 16 := by
      simp only [Prod.fst_add]; omega
    have hy1 : 0 ≤ (D4.toFun g (decode i) + (8, 8)).2 ∧
        (D4.toFun g (decode i) + (8, 8)).2 < 16 := by
      simp only [Prod.snd_add]; omega
    exact ⟨encode_lt hx1.1 hx1.2 hy1.1 hy1.2, decode_encode hx1.1 hx1.2 hy1.1 hy1.2⟩
  have hfold : cells ((bitsOf 256 m).foldl (fun acc i => acc ||| 2 ^ f i) 0)
      = translate (8, 8) ((cells m).image (D4.toFun g)) := by
    rw [cells_foldl_lor f _ _ fun i hi => (hin i hi).1, cells_zero, Finset.empty_union]
    ext p
    simp only [List.mem_toFinset, List.mem_map, mem_translate, Finset.mem_image, mem_cells]
    constructor
    · rintro ⟨i, hi, rfl⟩
      rw [(hin i hi).2, add_sub_cancel_right]
      refine ⟨decode i, ⟨i, ?_, (mem_bitsOf' hb).mp hi, rfl⟩, rfl⟩
      by_contra hc
      have := (mem_bitsOf' hb).mp hi
      rw [testBit_eq_false_of_inBox hb (by omega)] at this
      exact Bool.false_ne_true this
    · rintro ⟨q, ⟨i, hi, hbi, rfl⟩, he⟩
      refine ⟨i, (mem_bitsOf' hb).mpr hbi, ?_⟩
      rw [(hin i ((mem_bitsOf' hb).mpr hbi)).2, he, sub_add_cancel]
  have hbox' : InBox ((bitsOf 256 m).foldl (fun acc i => acc ||| 2 ^ f i) 0) :=
    inBox_foldl_lor f _ _ (by norm_num [InBox]) fun i hi => (hin i hi).1
  have hne : (bitsOf 256 m).foldl (fun acc i => acc ||| 2 ^ f i) 0 ≠ 0 := by
    intro h
    have := hfold
    rw [h, cells_zero] at this
    have hne' : (translate (8, 8) ((cells m).image (D4.toFun g))).Nonempty :=
      (hcan.anchored.nonempty.image _).image _
    rw [← this] at hne'
    exact Finset.not_nonempty_empty hne'
  refine ⟨inBox_shiftRight hbox', ?_⟩
  change cells (reanchor _) = _
  rw [cells_reanchor hbox' hne, hfold, translate, reanchor_image_add]

/-- **A fixed-point count of a symmetry is a filtered list length.** -/
theorem fixCount_eq_length {n : ℕ} (h1 : 1 ≤ n) (hn : n ≤ 7) (g : D4) :
    fixCount n g = ((L n).filter fun m => transform g m = m).length := by
  rw [fixCount_eq_ncard, ncard_eq_length h1 (by omega)]
  intro m hm
  obtain ⟨hbox', hcells⟩ := cells_transform g h1 hn hm
  have hbox := (L_spec n h1 (by omega)).1 m hm
  rw [decide_eq_true_eq, ← hcells]
  exact ⟨fun h => by rw [h], fun h => eq_of_cells_eq hbox' hbox h⟩

end Polyplets.Enum

namespace Polyplets

open Enum

/-! ## The onset cells the development consumes

Kernel-decided through the enumerator: `T 3 2` and `T 4 3` pin `P_1`
(`Pin.lean`, `Grand/PinAll.lean`), `a 3` is the base of the growth lower
bound `20 ^ (n / 3) ≤ a n` (`SymmetryRatio.lean`). Further cells are checked
in `Checks.lean`. -/

/-- `T 3 2 = 10` (`results/triangle.txt`), the first `P_1` onset point. -/
theorem T_3_2 : T 3 2 = 10 := by
  rw [T_eq_length (by norm_num) (by norm_num)]
  decide +kernel

/-- `T 4 3 = 55` (`results/triangle.txt`), the second `P_1` onset point. -/
theorem T_4_3 : T 4 3 = 55 := by
  rw [T_eq_length (by norm_num) (by norm_num)]
  decide +kernel

/-- `a 3 = 20` (`results/triangle.txt`, row sum). -/
theorem a_3 : a 3 = 20 := by
  rw [a_eq_length (by norm_num) (by norm_num)]
  decide +kernel

end Polyplets
