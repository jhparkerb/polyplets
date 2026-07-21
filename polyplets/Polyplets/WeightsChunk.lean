/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Weights

/-!
# Chunked enumeration of the heavy leaf `V 3 3`

The single `native_decide` for `V 3 3 = 4778` enumerates the full
`CFGV 3 3` window — `C(45,6)·15 ≈ 1.2·10⁸` cluster/`q` pairs — and overflows the
compiler's evaluation stack (a non-tail-recursive `List` fold in the compiled
`Finset.filter`/`image` chain). This module partitions the enumeration into
per-column chunks small enough to `native_decide` individually and reassembles
the total by generic `Finset` algebra (no `native_decide` in the partition
lemma itself).

## The partition

`CFGVchunk 3 3 m` re-runs the `CFGV 3 3` enumeration but (a) restricts the
cluster window to the eight columns `[m, min (m+7) 7]` and (b) keeps only the
configurations whose cluster (rows `1..3`) has **minimum x-coordinate exactly
`m`**. Because any V-configuration is king-connected with `card = 8`, every two
cells differ in x by at most `7` (`connected_sub_x_le`); so a config whose
leftmost cluster column is `m` fits entirely in `[m, m+7]`, and — being also
`|x| ≤ 7` (`connected_abs_x_le`) — in `[m, min (m+7) 7]`. Hence the narrow
window loses nothing, while `powersetCard 6` now ranges over `≤ C(24,6) = 134596`
subsets, i.e. `≤ 134596·15 ≈ 2.0·10⁶` pairs per chunk — the known-good scale.

The chunks over `m ∈ [-7, 7]` are pairwise disjoint (a set's cluster has a
unique minimum column) and cover `CFGV 3 3`, so
`V 3 3 = ∑_{m=-7}^{7} (CFGVchunk 3 3 m).card` (`V_3_3_eq_sum_chunks`, generic).
The fifteen chunk cardinalities are the `native_decide` leaves, split across
`WeightsChunkA..` for parallel `lake` builds.
-/

namespace Polyplets

set_option maxRecDepth 4000
-- `CFGV_eq_biUnion`'s proof term is large enough to overflow this style linter's
-- own recursion; the check is irrelevant here (no constructor-named variables).
set_option linter.constructorNameAsVariable false

/-! ## An offset rectangular window -/

/-- The rectangular window `[x0, x1] × [y0, y1]`, built computably as a cast
image of `Finset.range` products (as `Weights.window`, but with an arbitrary
lower x-corner rather than a symmetric `[-w, w]`). Empty when `x1 < x0` or
`y1 < y0`. -/
def windowXY (x0 x1 y0 y1 : ℤ) : Finset (ℤ × ℤ) :=
  (Finset.range (x1 - x0 + 1).toNat ×ˢ Finset.range (y1 - y0 + 1).toNat).image
    fun p => ((p.1 : ℤ) + x0, (p.2 : ℤ) + y0)

/-- Membership in `windowXY` is the four coordinate bounds. -/
lemma mem_windowXY {x0 x1 y0 y1 : ℤ} {p : ℤ × ℤ} :
    p ∈ windowXY x0 x1 y0 y1 ↔ x0 ≤ p.1 ∧ p.1 ≤ x1 ∧ y0 ≤ p.2 ∧ p.2 ≤ y1 := by
  simp only [windowXY, Finset.mem_image, Finset.mem_product, Finset.mem_range, Prod.exists]
  constructor
  · rintro ⟨a, b, ⟨ha, hb⟩, rfl⟩
    rw [Int.lt_toNat] at ha hb
    refine ⟨?_, ?_, ?_, ?_⟩
    · change x0 ≤ (a : ℤ) + x0; omega
    · change (a : ℤ) + x0 ≤ x1; omega
    · change y0 ≤ (b : ℤ) + y0; omega
    · change (b : ℤ) + y0 ≤ y1; omega
  · rintro ⟨h1, h2, h3, h4⟩
    refine ⟨(p.1 - x0).toNat, (p.2 - y0).toNat, ⟨?_, ?_⟩, ?_⟩
    · rw [Int.lt_toNat]; rw [Int.toNat_of_nonneg (by omega)]; omega
    · rw [Int.lt_toNat]; rw [Int.toNat_of_nonneg (by omega)]; omega
    · rw [Prod.ext_iff]
      refine ⟨?_, ?_⟩
      · change ((p.1 - x0).toNat : ℤ) + x0 = p.1
        rw [Int.toNat_of_nonneg (by omega)]; omega
      · change ((p.2 - y0).toNat : ℤ) + y0 = p.2
        rw [Int.toNat_of_nonneg (by omega)]; omega

/-! ## The per-column chunks of `CFGV 3 3` -/

/-- The cluster cells (rows `1..3`) of an assembled surplus-3 config. -/
def clusterCells (S : Finset (ℤ × ℤ)) : Finset (ℤ × ℤ) :=
  S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ 3

/-- `m` is the **leftmost cluster column** of `S`: every cluster cell has
`x ≥ m`, and some cluster cell sits exactly on column `m`. A set has a unique
such `m` (it is the minimum), which is what makes the chunks disjoint. -/
def IsClusterLeft (S : Finset (ℤ × ℤ)) (m : ℤ) : Prop :=
  (∀ c ∈ clusterCells S, m ≤ c.1) ∧ (∃ c ∈ clusterCells S, c.1 = m)

/-- Leftmost-cluster-column is decidable: bounded quantifiers over a finset. -/
instance decidableIsClusterLeft (S : Finset (ℤ × ℤ)) (m : ℤ) :
    Decidable (IsClusterLeft S m) := by
  unfold IsClusterLeft; infer_instance

/-- **Chunk `m` of `CFGV 3 3`.** The `CFGV 3 3` enumeration restricted to the
cluster window `[m, min (m+7) 7] × {1,2,3}` (eight columns — enough by
`connected_sub_x_le`/`connected_abs_x_le` once the leftmost column is `m`) and
to configs whose cluster's leftmost column is exactly `m`. Enumerates
`≤ C(24,6)·15 ≈ 2.0·10⁶` pairs, so `native_decide` reaches `(CFGVchunk m).card`. -/
def CFGVchunk (m : ℤ) : Finset (Finset (ℤ × ℤ)) :=
  (((windowXY m (min (m + 7) 7) 1 3).powersetCard 6 ×ˢ window 7 4 1).filter
    fun Cq =>
      IsVConfig 3 3 (insert ((0 : ℤ), (0 : ℤ)) (insert Cq.2 Cq.1)) ∧
        IsClusterLeft (insert ((0 : ℤ), (0 : ℤ)) (insert Cq.2 Cq.1)) m).image
    fun Cq => insert ((0 : ℤ), (0 : ℤ)) (insert Cq.2 Cq.1)

/-- **Propositional characterization of `CFGVchunk`** (window independence):
membership is `IsVConfig 3 3` together with leftmost cluster column `m`. The
narrow window is invisible — a config with leftmost cluster column `m` is
king-connected with `card = 8`, so all its cluster cells lie within `7` columns
of `m` and within `|x| ≤ 7`, i.e. inside `[m, min (m+7) 7]`. -/
theorem mem_CFGVchunk {m : ℤ} {S : Finset (ℤ × ℤ)} :
    S ∈ CFGVchunk m ↔ IsVConfig 3 3 S ∧ IsClusterLeft S m := by
  constructor
  · intro h
    rw [CFGVchunk, Finset.mem_image] at h
    obtain ⟨Cq, hCq, heq⟩ := h
    rw [Finset.mem_filter] at hCq
    rw [← heq]
    exact hCq.2
  · rintro ⟨hV, hleft⟩
    obtain ⟨hcard, h0, hy, hr0, hrtop, -, hconn⟩ := id hV
    have hw0 : IsWalkRow S 0 := hr0
    have hwt : IsWalkRow S ((3 : ℤ) + 1) := hrtop
    obtain ⟨q, hqf⟩ := Finset.card_pos.mp
      (show 0 < (S.filter fun c => c.2 = (3 : ℤ) + 1).card by
        have h1 : (S.filter fun c => c.2 = (3 : ℤ) + 1).card = 1 := hrtop
        omega)
    rw [Finset.mem_filter] at hqf
    obtain ⟨hqS, hqy⟩ := hqf
    -- `S` decomposes as origin ∪ cluster ∪ top cell (as in `mem_CFGV`)
    have hins :
        insert ((0 : ℤ), (0 : ℤ)) (insert q (clusterCells S)) = S := by
      ext c
      simp only [clusterCells, Finset.mem_insert, Finset.mem_filter]
      constructor
      · rintro (rfl | rfl | ⟨hcS, -⟩)
        · exact h0
        · exact hqS
        · exact hcS
      · intro hc
        have hyc := hy c hc
        by_cases hc0 : c.2 = 0
        · exact Or.inl (hw0.eq_of_mem hc hc0 h0 rfl)
        · by_cases hct : c.2 = (3 : ℤ) + 1
          · exact Or.inr (Or.inl (hwt.eq_of_mem hc hct hqS hqy))
          · exact Or.inr (Or.inr ⟨hc, by omega, by omega⟩)
    have hqC : q ∉ clusterCells S := by
      rw [clusterCells, Finset.mem_filter]
      rintro ⟨-, -, hle⟩
      omega
    have h0notin :
        ((0 : ℤ), (0 : ℤ)) ∉ insert q (clusterCells S) := by
      rw [clusterCells, Finset.mem_insert, Finset.mem_filter]
      rintro (heq | ⟨-, hge, -⟩)
      · rw [← heq] at hqy
        have h00 : (0 : ℤ) = (3 : ℤ) + 1 := hqy
        omega
      · have h01 : (1 : ℤ) ≤ 0 := hge
        omega
    have hCcard : (clusterCells S).card = 6 := by
      have hc1 := Finset.card_insert_of_notMem h0notin
      have hc2 := Finset.card_insert_of_notMem hqC
      rw [hins, hc2] at hc1
      omega
    -- witness cell on the leftmost column, for the `x ≤ m + 7` bound
    obtain ⟨w, hwC, hwx⟩ := hleft.2
    have hwS : w ∈ S := (Finset.mem_filter.mp hwC).1
    rw [CFGVchunk, Finset.mem_image]
    refine ⟨(clusterCells S, q), ?_, hins⟩
    rw [Finset.mem_filter]
    refine ⟨?_, ?_⟩
    · rw [Finset.mem_product]
      refine ⟨?_, ?_⟩
      · change (clusterCells S) ∈ (windowXY m (min (m + 7) 7) 1 3).powersetCard 6
        rw [Finset.mem_powersetCard]
        refine ⟨?_, hCcard⟩
        intro c hcf
        have hcS : c ∈ S := (Finset.mem_filter.mp hcf).1
        obtain ⟨-, hc1, hc2⟩ := Finset.mem_filter.mp hcf
        have hxabs := connected_abs_x_le hconn h0 hcS
        rw [hcard, abs_le] at hxabs
        have hxsub := connected_sub_x_le hconn hwS hcS
        rw [hcard] at hxsub
        rw [mem_windowXY]
        refine ⟨hleft.1 c hcf, le_min ?_ ?_, hc1, hc2⟩
        · rw [hwx] at hxsub; push_cast at hxsub ⊢; omega
        · push_cast at hxabs; omega
      · change q ∈ window 7 4 1
        have hx := connected_abs_x_le hconn h0 hqS
        rw [hcard, abs_le] at hx
        rw [mem_window]
        push_cast at hx ⊢
        omega
    · rw [hins]
      exact ⟨hV, hleft⟩

/-! ## The partition (generic `Finset` algebra, no `native_decide`) -/

/-- Each chunk sits inside the full config set. -/
theorem CFGVchunk_subset (m : ℤ) : CFGVchunk m ⊆ CFGV 3 3 := by
  intro S hS
  rw [mem_CFGVchunk] at hS
  rw [mem_CFGV]
  exact hS.1

/-- Distinct chunks are disjoint: a config's cluster has a unique leftmost
column. -/
theorem CFGVchunk_disjoint {m m' : ℤ} (h : m ≠ m') :
    Disjoint (CFGVchunk m) (CFGVchunk m') := by
  rw [Finset.disjoint_left]
  intro S hSm hSm'
  rw [mem_CFGVchunk] at hSm hSm'
  obtain ⟨hlb, cm, hcm, hcmx⟩ := hSm.2
  obtain ⟨hlb', cm', hcm', hcmx'⟩ := hSm'.2
  have h1 : m ≤ m' := by have := hlb cm' hcm'; rwa [hcmx'] at this
  have h2 : m' ≤ m := by have := hlb' cm hcm; rwa [hcmx] at this
  exact h (le_antisymm h1 h2)

/-- `CFGV 3 3` is the disjoint union of its per-column chunks over
`m ∈ [-7, 7]`. -/
theorem CFGV_eq_biUnion :
    CFGV 3 3 = (Finset.Icc (-7 : ℤ) 7).biUnion CFGVchunk := by
  refine Finset.Subset.antisymm ?_ ?_
  · intro S hS
    rw [Finset.mem_biUnion]
    rw [mem_CFGV] at hS
    obtain ⟨hcard, h0, hy, hr0, hrtop, hrows, hconn⟩ := id hS
    -- cluster is nonempty: row 1 holds ≥ 2 cells
    have hrow1 : 2 ≤ rowSize S 1 := hrows 1 (by decide)
    obtain ⟨c1, hc1⟩ := Finset.card_pos.mp
      (show 0 < (S.filter fun c => c.2 = (1 : ℤ)).card by
        have h1 : rowSize S 1 = (S.filter fun c => c.2 = (1 : ℤ)).card := rfl
        omega)
    rw [Finset.mem_filter] at hc1
    have hc1y := hc1.2
    have hc1cl : c1 ∈ clusterCells S := by
      rw [clusterCells, Finset.mem_filter]
      exact ⟨hc1.1, by omega, by omega⟩
    -- least cluster column
    obtain ⟨c0, hc0, hmin⟩ :=
      (clusterCells S).exists_min_image Prod.fst ⟨c1, hc1cl⟩
    have hc0S : c0 ∈ S := (Finset.mem_filter.mp hc0).1
    refine ⟨c0.1, ?_, ?_⟩
    · rw [Finset.mem_Icc]
      have hx := connected_abs_x_le hconn h0 hc0S
      rw [hcard, abs_le] at hx
      push_cast at hx
      omega
    · rw [mem_CFGVchunk]
      exact ⟨hS, hmin, c0, hc0, rfl⟩
  · rw [Finset.biUnion_subset]
    intro m _
    exact CFGVchunk_subset m

/-- **The partition lemma.** `V 3 3` is the sum of the fifteen chunk
cardinalities — proved by generic `Finset` algebra, with no `native_decide`. -/
theorem V_3_3_eq_sum_chunks :
    V 3 3 = ∑ m ∈ Finset.Icc (-7 : ℤ) 7, (CFGVchunk m).card := by
  change (CFGV 3 3).card = _
  rw [CFGV_eq_biUnion,
    Finset.card_biUnion (fun m _ m' _ hmm' => CFGVchunk_disjoint hmm')]

end Polyplets
