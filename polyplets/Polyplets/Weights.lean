/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.NormNum.Basic
import Polyplets.Compute
import Polyplets.Universal.Separation

/-!
# Peeling weights: walk-top counts `d` and cluster configurations `V`, `Vᵗ`

The counting objects of the peeling recursion (`README.md`). The primary
object is `d k H`, the number of polyplets of height `H` and surplus `k`
whose **top row is a walk row** (holds exactly one cell); the recursion's
weights aggregate cluster configurations by (rows `ℓ`, surplus `j`) only:

* `V ℓ j` — interior weight: configurations of a cluster spanning rows
  `1..ℓ` (each with `≥ 2` cells, `ℓ + j` cells in total), together with the
  fixed walk cell `p = (0,0)` directly below and a free walk cell `q` on the
  row directly above, the whole connected, counted relative to `p`.
* `Vt ℓ j` — top-edge weight: the same without `q`.

Everything is a `Finset.card` of a computable enumeration in the style of
`Compute.lean` (window + `powersetCard` + decidable filter), so the kernel can
decide the smallest values. The enumeration windows are an encoding artifact: the
**window-independence lemmas** `mem_Dc`, `mem_CFGV`, `mem_CFGVt` characterize
membership by the propositional descriptions alone (the x-spread of a connected
set containing the origin is bounded by its cell count, `connected_abs_x_le`).
Downstream bijections (`Peel.lean`) must match against those propositional
descriptions, never the window encoding.

## The values the proofs consume

`V 1 1 = 25` and `Vt 1 1 = 5`, the paper enumeration (the `16 + 9` and `4 + 1`
gadgets of `docs/proofs/T-n-nm1.md`), and `d 0 1 = 1`, kernel-decided (each
under 3 GB; the next values up need 6–9 GB, measured 2026-10-12). More values
and the identities at their onset are in `Checks.lean`.
-/

namespace Polyplets

open Universal (IsWalkRow)

/-! ## Row size and walk-top polyplets -/

/-- The number of cells of `S` in row `y`. `rowSize S r = 1` is exactly
`Universal.IsWalkRow S r` (`isWalkRow_iff_rowSize`). -/
def rowSize (S : Finset (ℤ × ℤ)) (y : ℤ) : ℕ :=
  (S.filter fun c => c.2 = y).card

/-- `IsWalkRow` and `rowSize = 1` agree definitionally. -/
lemma isWalkRow_iff_rowSize {S : Finset (ℤ × ℤ)} {r : ℤ} :
    IsWalkRow S r ↔ rowSize S r = 1 := Iff.rfl

/-- **Walk-top polyplets**: the polyplets of `H + k` cells and height `H` whose
top row `H - 1` is a walk row. The enumeration domain is `Compute.lean`'s box;
`mem_Dc` shows the encoding is invisible. -/
def Dc (k H : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  ((box (H + k) H).powersetCard (H + k)).filter
    fun S => S ∈ heightClass (H + k) H ∧ rowSize S ((H : ℤ) - 1) = 1

/-- `d k H`: the number of polyplets of height `H` and surplus `k` whose top
row is a walk row — the primary object of the peeling recursion
(`d_k(H) = 3·d_k(H−1) + Σ V(ℓ,j)·d_{k−j}(H−1−ℓ)` for `H ≥ k + 2`,
proved in `Peel.lean`). -/
def d (k H : ℕ) : ℕ := (Dc k H).card

/-- **Propositional characterization of `Dc`** (window independence):
membership is exactly height class plus walk top row — the box enumeration is
an encoding artifact. -/
theorem mem_Dc {k H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ Dc k H ↔ S ∈ heightClass (H + k) H ∧ rowSize S ((H : ℤ) - 1) = 1 := by
  rw [Dc, Finset.mem_filter]
  constructor
  · exact fun h => h.2
  · intro h
    exact ⟨mem_powersetCard_box h.1, h⟩

/-! ## The x-spread bound -/

/-- **Columns between two cells are occupied.** In a king-connected `S`, the
x-distance between two cells is at most `card − 1`: a king path from `a` to `p`
plants a cell at every intermediate column (`exists_x_eq_of_cross`). -/
lemma connected_sub_x_le {S : Finset (ℤ × ℤ)} (hconn : KingConnected S)
    {a p : ℤ × ℤ} (ha : a ∈ S) (hp : p ∈ S) :
    p.1 - a.1 ≤ (S.card : ℤ) - 1 := by
  rcases le_total p.1 a.1 with h | h
  · have hpos : 0 < S.card := Finset.card_pos.mpr ⟨p, hp⟩
    omega
  · have hsub : Finset.Icc a.1 p.1 ⊆ S.image Prod.fst := by
      intro t ht
      rw [Finset.mem_Icc] at ht
      rw [Finset.mem_image]
      rcases ht.2.eq_or_lt with heq | hlt
      · exact ⟨p, hp, heq.symm⟩
      · obtain ⟨c, hcS, hct⟩ :=
          exists_x_eq_of_cross (hconn a ha p hp) ht.1 (by omega)
        exact ⟨c, hcS, hct⟩
    have hcard : (Finset.Icc a.1 p.1).card ≤ S.card :=
      le_trans (Finset.card_le_card hsub) Finset.card_image_le
    rw [Int.card_Icc] at hcard
    omega

/-- **x-spread bound (window independence).** In a king-connected set
containing the origin, every cell's `|x|` is at most `card − 1`. This is what
makes the enumeration windows below invisible: any set satisfying a config's
propositional description automatically fits its window. -/
lemma connected_abs_x_le {S : Finset (ℤ × ℤ)} (hconn : KingConnected S)
    (h0 : ((0 : ℤ), (0 : ℤ)) ∈ S) {p : ℤ × ℤ} (hp : p ∈ S) :
    |p.1| ≤ (S.card : ℤ) - 1 := by
  have h1 : p.1 - 0 ≤ (S.card : ℤ) - 1 := connected_sub_x_le hconn h0 hp
  have h2 : (0 : ℤ) - p.1 ≤ (S.card : ℤ) - 1 := connected_sub_x_le hconn hp h0
  rw [abs_le]
  exact ⟨by omega, by omega⟩

/-! ## Cluster configurations, aggregated by (rows ℓ, surplus j) -/

/-- The window `[-w, w] × [y0, y0 + h - 1]`, built computably as a cast image
of `Finset.range` products (`Finset.Icc` on `ℤ` compiles against a
noncomputable order instance in current mathlib, exactly as for
`Compute.lean`'s `box`). -/
def window (w y0 h : ℕ) : Finset (ℤ × ℤ) :=
  (Finset.range (2 * w + 1) ×ˢ Finset.range h).image
    fun p => ((p.1 : ℤ) - (w : ℤ), (p.2 : ℤ) + (y0 : ℤ))

/-- Membership in `window` is the four coordinate bounds. -/
lemma mem_window {w y0 h : ℕ} {p : ℤ × ℤ} :
    p ∈ window w y0 h ↔
      -(w : ℤ) ≤ p.1 ∧ p.1 ≤ (w : ℤ) ∧ (y0 : ℤ) ≤ p.2 ∧ p.2 < (y0 : ℤ) + (h : ℤ) := by
  simp only [window, Finset.mem_image, Finset.mem_product, Finset.mem_range, Prod.exists]
  constructor
  · rintro ⟨a, b, ⟨ha, hb⟩, rfl⟩
    refine ⟨?_, ?_, ?_, ?_⟩
    · change -(w : ℤ) ≤ (a : ℤ) - (w : ℤ)
      omega
    · change (a : ℤ) - (w : ℤ) ≤ (w : ℤ)
      omega
    · change (y0 : ℤ) ≤ (b : ℤ) + (y0 : ℤ)
      omega
    · change (b : ℤ) + (y0 : ℤ) < (y0 : ℤ) + (h : ℤ)
      omega
  · rintro ⟨h1, h2, h3, h4⟩
    refine ⟨(p.1 + w).toNat, (p.2 - y0).toNat, ⟨by omega, by omega⟩, ?_⟩
    rw [Prod.ext_iff]
    refine ⟨?_, ?_⟩
    · change (((p.1 + (w : ℤ)).toNat : ℤ)) - (w : ℤ) = p.1
      omega
    · change (((p.2 - (y0 : ℤ)).toNat : ℤ)) + (y0 : ℤ) = p.2
      omega

/-- `S` is a **V-configuration** for `(ℓ, j)` — the peeled data of case 2 of
the d-recursion: the fixed walk cell `p = (0,0)` alone on row
`0`; a cluster occupying exactly rows `1..ℓ`, every one of those rows with at
least two cells; a free walk cell `q` alone on row `ℓ + 1`; `ℓ + j + 2` cells
in total (so the cluster has `ℓ + j` cells — surplus `j`); and the whole
king-connected. Everything is encoded as the single finset
`S = {p} ∪ C ∪ {q}` and read off its row profile. Positions are relative to
`p`, pinned at the origin — there is deliberately **no x-anchoring clause**. -/
structure IsVConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `ℓ + j + 2` cells: the cluster's `ℓ + j`, plus `p` and `q`. -/
  card : S.card = ℓ + j + 2
  /-- The fixed walk cell `p = (0, 0)`. -/
  origin : ((0 : ℤ), (0 : ℤ)) ∈ S
  /-- Everything on rows `0 … ℓ + 1`. -/
  rows : ∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + 1
  /-- Row `0` is the walk cell alone. -/
  row_zero : rowSize S 0 = 1
  /-- Row `ℓ + 1` is the free walk cell `q` alone. -/
  row_top : rowSize S ((ℓ : ℤ) + 1) = 1
  /-- The cluster rows `1 … ℓ` each hold at least two cells. -/
  multi : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)
  /-- King-connected. -/
  conn : KingConnected S

/-- `IsVConfig` as a conjunction (for decidability). -/
lemma isVConfig_iff_and {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVConfig ℓ j S ↔ S.card = ℓ + j + 2 ∧ ((0 : ℤ), (0 : ℤ)) ∈ S ∧
      (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + 1) ∧ rowSize S 0 = 1 ∧
      rowSize S ((ℓ : ℤ) + 1) = 1 ∧ (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧
      KingConnected S :=
  ⟨fun h => ⟨h.card, h.origin, h.rows, h.row_zero, h.row_top, h.multi, h.conn⟩,
   fun ⟨a, b, c, d, e, f, g⟩ => ⟨a, b, c, d, e, f, g⟩⟩

/-- `S` is a **Vᵗ-configuration** for `(ℓ, j)` — the peeled data of the
multi-top case of the c-identity: a V-configuration without the free walk cell
`q` (the cluster caps the animal), hence `ℓ + j + 1` cells on rows `0..ℓ`. -/
structure IsVtConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `ℓ + j + 1` cells: the cluster's `ℓ + j`, plus `p`. -/
  card : S.card = ℓ + j + 1
  /-- The fixed walk cell `p = (0, 0)`. -/
  origin : ((0 : ℤ), (0 : ℤ)) ∈ S
  /-- Everything on rows `0 … ℓ`. -/
  rows : ∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ)
  /-- Row `0` is the walk cell alone. -/
  row_zero : rowSize S 0 = 1
  /-- The cluster rows `1 … ℓ` each hold at least two cells. -/
  multi : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)
  /-- King-connected. -/
  conn : KingConnected S

/-- `IsVtConfig` as a conjunction (for decidability). -/
lemma isVtConfig_iff_and {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVtConfig ℓ j S ↔ S.card = ℓ + j + 1 ∧ ((0 : ℤ), (0 : ℤ)) ∈ S ∧
      (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ)) ∧ rowSize S 0 = 1 ∧
      (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧ KingConnected S :=
  ⟨fun h => ⟨h.card, h.origin, h.rows, h.row_zero, h.multi, h.conn⟩,
   fun ⟨a, b, c, d, e, f⟩ => ⟨a, b, c, d, e, f⟩⟩

/-- V-configurations are decidable: decidable cardinality, membership, bounded
quantifiers, row sizes, and connectivity (`Compute.lean`). -/
instance decidableIsVConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsVConfig ℓ j S) :=
  decidable_of_iff _ isVConfig_iff_and.symm

/-- Vᵗ-configurations are decidable. -/
instance decidableIsVtConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsVtConfig ℓ j S) :=
  decidable_of_iff _ isVtConfig_iff_and.symm

/-- **The V-configurations for `(ℓ, j)`**, enumerated computably: choose the
cluster `C` as an `(ℓ+j)`-subset of the interior window (rows `1..ℓ`,
`|x| ≤ ℓ+j+1` — enough by `connected_abs_x_le`), choose `q` on row `ℓ + 1`,
keep the pairs whose assembled set `{(0,0)} ∪ C ∪ {q}` is a V-configuration,
and take the assembled sets. (Filtering *before* the image keeps the image —
whose deduplication is quadratic — on the few survivors; the pre-image pairs
are ~10⁵ at the sizes validated below.) `mem_CFGV` shows the encoding is
invisible. -/
def CFGV (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  ((((window (ℓ + j + 1) 1 ℓ).powersetCard (ℓ + j)) ×ˢ window (ℓ + j + 1) (ℓ + 1) 1).filter
    fun Cq => IsVConfig ℓ j (insert ((0 : ℤ), (0 : ℤ)) (insert Cq.2 Cq.1))).image
    fun Cq => insert ((0 : ℤ), (0 : ℤ)) (insert Cq.2 Cq.1)

/-- `V ℓ j`: the interior cluster weight — the number of V-configurations. -/
def V (ℓ j : ℕ) : ℕ := (CFGV ℓ j).card

/-- **The Vᵗ-configurations for `(ℓ, j)`**, enumerated computably: as `CFGV`
but with no `q` (window `|x| ≤ ℓ+j`, matching the smaller cell count). -/
def CFGVt (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (((window (ℓ + j) 1 ℓ).powersetCard (ℓ + j)).filter
    fun C => IsVtConfig ℓ j (insert ((0 : ℤ), (0 : ℤ)) C)).image
    fun C => insert ((0 : ℤ), (0 : ℤ)) C

/-- `Vt ℓ j`: the top-edge cluster weight — the number of Vᵗ-configurations. -/
def Vt (ℓ j : ℕ) : ℕ := (CFGVt ℓ j).card

/-! ## Window independence for the configuration sets -/

/-- **Propositional characterization of `CFGV`** (window independence):
membership is exactly `IsVConfig`. The encoding direction decomposes `S` by its
row profile — the unique row-`0` cell is the origin, the unique row-`(ℓ+1)`
cell is `q`, the rest is the cluster; the x-window is wide enough by
`connected_abs_x_le`. Downstream bijections must match against `IsVConfig`,
never this enumeration. -/
theorem mem_CFGV {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ CFGV ℓ j ↔ IsVConfig ℓ j S := by
  constructor
  · intro h
    rw [CFGV, Finset.mem_image] at h
    obtain ⟨Cq, hCq, heq⟩ := h
    rw [Finset.mem_filter] at hCq
    rw [← heq]
    exact hCq.2
  · intro hS
    obtain ⟨hcard, h0, hy, hr0, hrtop, -, hconn⟩ := id hS
    have hw0 : IsWalkRow S 0 := hr0
    have hwt : IsWalkRow S ((ℓ : ℤ) + 1) := hrtop
    obtain ⟨q, hqf⟩ := Finset.card_pos.mp
      (show 0 < (S.filter fun c => c.2 = (ℓ : ℤ) + 1).card by
        have h1 : (S.filter fun c => c.2 = (ℓ : ℤ) + 1).card = 1 := hrtop
        omega)
    rw [Finset.mem_filter] at hqf
    obtain ⟨hqS, hqy⟩ := hqf
    -- `S` decomposes as origin ∪ cluster ∪ top cell
    have hins :
        insert ((0 : ℤ), (0 : ℤ))
          (insert q (S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ))) = S := by
      ext c
      simp only [Finset.mem_insert, Finset.mem_filter]
      constructor
      · rintro (rfl | rfl | ⟨hcS, -⟩)
        · exact h0
        · exact hqS
        · exact hcS
      · intro hc
        have hyc := hy c hc
        by_cases hc0 : c.2 = 0
        · exact Or.inl (hw0.eq_of_mem hc hc0 h0 rfl)
        · by_cases hct : c.2 = (ℓ : ℤ) + 1
          · exact Or.inr (Or.inl (hwt.eq_of_mem hc hct hqS hqy))
          · exact Or.inr (Or.inr ⟨hc, by omega, by omega⟩)
    have hqC : q ∉ S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ) := by
      rw [Finset.mem_filter]
      rintro ⟨-, -, hle⟩
      omega
    have h0notin :
        ((0 : ℤ), (0 : ℤ)) ∉ insert q (S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ)) := by
      rw [Finset.mem_insert, Finset.mem_filter]
      rintro (heq | ⟨-, hge, -⟩)
      · rw [← heq] at hqy
        have h00 : (0 : ℤ) = (ℓ : ℤ) + 1 := hqy
        omega
      · have h01 : (1 : ℤ) ≤ 0 := hge
        omega
    have hCcard : (S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ)).card = ℓ + j := by
      have hc1 := Finset.card_insert_of_notMem h0notin
      have hc2 := Finset.card_insert_of_notMem hqC
      rw [hins, hc2] at hc1
      omega
    rw [CFGV, Finset.mem_image]
    refine ⟨(S.filter (fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ)), q), ?_, hins⟩
    rw [Finset.mem_filter]
    refine ⟨?_, ?_⟩
    · rw [Finset.mem_product]
      refine ⟨?_, ?_⟩
      · change (S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ)) ∈
          (window (ℓ + j + 1) 1 ℓ).powersetCard (ℓ + j)
        rw [Finset.mem_powersetCard]
        refine ⟨?_, hCcard⟩
        intro c hcf
        rw [Finset.mem_filter] at hcf
        obtain ⟨hcS, hc1, hc2⟩ := hcf
        have hx := connected_abs_x_le hconn h0 hcS
        rw [hcard, abs_le] at hx
        rw [mem_window]
        omega
      · change q ∈ window (ℓ + j + 1) (ℓ + 1) 1
        have hx := connected_abs_x_le hconn h0 hqS
        rw [hcard, abs_le] at hx
        rw [mem_window]
        omega
    · change IsVConfig ℓ j
        (insert ((0 : ℤ), (0 : ℤ))
          (insert q (S.filter fun c => 1 ≤ c.2 ∧ c.2 ≤ (ℓ : ℤ))))
      rw [hins]
      exact hS

/-- **Propositional characterization of `CFGVt`** (window independence):
membership is exactly `IsVtConfig`. Same decomposition as `mem_CFGV`, without
the top cell. -/
theorem mem_CFGVt {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ CFGVt ℓ j ↔ IsVtConfig ℓ j S := by
  constructor
  · intro h
    rw [CFGVt, Finset.mem_image] at h
    obtain ⟨C, hC, heq⟩ := h
    rw [Finset.mem_filter] at hC
    rw [← heq]
    exact hC.2
  · intro hS
    obtain ⟨hcard, h0, hy, hr0, -, hconn⟩ := id hS
    have hw0 : IsWalkRow S 0 := hr0
    have hins : insert ((0 : ℤ), (0 : ℤ)) (S.filter fun c => 1 ≤ c.2) = S := by
      ext c
      simp only [Finset.mem_insert, Finset.mem_filter]
      constructor
      · rintro (rfl | ⟨hcS, -⟩)
        · exact h0
        · exact hcS
      · intro hc
        have hyc := hy c hc
        by_cases hc0 : c.2 = 0
        · exact Or.inl (hw0.eq_of_mem hc hc0 h0 rfl)
        · exact Or.inr ⟨hc, by omega⟩
    have h0notin : ((0 : ℤ), (0 : ℤ)) ∉ S.filter fun c => 1 ≤ c.2 := by
      rw [Finset.mem_filter]
      rintro ⟨-, hge⟩
      have h01 : (1 : ℤ) ≤ 0 := hge
      omega
    have hCcard : (S.filter fun c => 1 ≤ c.2).card = ℓ + j := by
      have hc1 := Finset.card_insert_of_notMem h0notin
      rw [hins] at hc1
      omega
    rw [CFGVt, Finset.mem_image]
    refine ⟨S.filter (fun c => 1 ≤ c.2), ?_, hins⟩
    rw [Finset.mem_filter]
    refine ⟨?_, ?_⟩
    · rw [Finset.mem_powersetCard]
      refine ⟨?_, hCcard⟩
      intro c hcf
      rw [Finset.mem_filter] at hcf
      obtain ⟨hcS, hc1⟩ := hcf
      have hx := connected_abs_x_le hconn h0 hcS
      rw [hcard, abs_le] at hx
      have hyc := hy c hcS
      rw [mem_window]
      omega
    · rw [hins]
      exact hS

/-! ## The values the proofs consume

Kernel-decided through the window enumerations (0.4–2.6 s, under 1 GB), and
independently cross-checked by a direct enumeration outside Lean
(2026-07-20). The larger values (`V 1 2 = 49`, `V 2 2 = 339`, `Vt 2 2 = 66`,
`d 0 3 = 9`, `d 1 3 = 40`, `d 2 3 = 136`, `d 2 4 = 1019`, `T 5 3 = 248`) need
6–9 GB through these windows; `Checks.lean` and `Grand/PinAll.lean` take
them from the enumerator of `Enum.lean` instead. -/

/-- `V 1 1 = 25`: the paper-enumerated `16 + 9` gadget count. -/
theorem V_1_1 : V 1 1 = 25 := by decide +kernel

/-- `Vt 1 1 = 5`: the paper-enumerated `4 + 1` gadget count. -/
theorem Vt_1_1 : Vt 1 1 = 5 := by decide +kernel

/-- `d 0 1 = 1`: the single cell (`d 0 H = 3^(H-1)`, a free walk chain). -/
theorem d_0_1 : d 0 1 = 1 := by decide +kernel
end Polyplets
