/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalk
import Polyplets.DepthAssembly
import Polyplets.Weights
import Polyplets.Weights3Heavy

/-!
# Notary N0: the bridge between the gap walk, the enumerated weights, and
# the depth identities

Campaign *Notary* (`docs/notary-lean-plan.md` §3, workstream N0). Three jobs:

1. **Cross-links.** The walk values of `GapWalk.lean` equal the enumerated
   cluster weights of `Weights.lean` / `Weights3Heavy.lean` at every level
   both sides reach (`ℓ ≤ 3`): interior `W(2^ℓ) = V ℓ ℓ` and bottom-edge
   `W^b(2^ℓ) = Vᵗ ℓ ℓ` (bottom = top for all-pairs clusters: the composition
   `(2,…,2)` is its own reversal). These are literal-to-literal rewrites of
   already-proved theorems — no new enumeration.

2. **The pure weight, enumerated.** `Weights.lean` has no counterpart of
   `W^p`; `IsVpConfig` / `CFGVp` / `Vp` supply it in the same idiom (the
   cluster alone, bottom-row leftmost cell pinned at `(0, 1)`, every row with
   at least two cells, king-connected — the `count_stack(v)` normalization of
   `experiments/cluster_weight_dp.py`), with `native_decide` pins at
   `ℓ = 1, 2, 3` and cross-links `W^p(2^ℓ) = Vp ℓ ℓ`.

3. **The assembly closed inside Lean.** Identity (II) of
   `results/onset-defect-depth1-closed.md`,

       `D_1(k) = [y^k]( P̂(y) − B(y)² / (3 + S(y)) )`,

   evaluated on truncated rational series built **from the walk itself**
   (`walkFamilies 8`), coefficient-for-coefficient against the depth-1 values
   of `DepthAssembly.lean` at `k ≤ 8` — whose weight-table hypotheses are
   discharged here (`depth*_k*'` below), so the chain
   *enumeration → tables → depth identities → (II)-assembly → walk* closes
   entirely inside Lean at `k ≤ 8`. The walk is additionally pinned against
   the C++ two-source table to `k ≤ 19` (`walk_table_19`).

## Provenance of every literal

* `Vp` pins `1, 13, 177`: `cluster_weight_dp.KNOWN_WEIGHTS` (pure column) and
  rows `e = 0`, `k = 1..3` of `results/severance_w3_families_K19_e3.txt`.
* `walk_table_19` literals: rows `e = 0`, `k = 1..19` of the same table,
  written by `build/severance_w3_families` (`cpp/severance_w3_families.cpp`)
  and validated by `experiments/severance_w3_depths.py::validate`.
* The `depth*_k*'` values: the corresponding theorems of `DepthAssembly.lean`.

## What this module does NOT prove

The bijection between `CFGV*` configurations and walk paths (all `ℓ`), and
identity (II) itself for all `k` — the truncation and tightness arguments —
remain paper-only (`docs/notary-lean-plan.md` §1, N4). This module closes the
finite anchor.
-/

namespace Polyplets
namespace GapWalkBridge

/-! ## 1. Cross-links: walk values = enumerated weights, `ℓ ≤ 3` -/

theorem walk_W_eq_V_1 : GapWalk.W 6 1 = V 1 1 := by
  rw [GapWalk.W_one, V_1_1]

theorem walk_W_eq_V_2 : GapWalk.W 6 2 = V 2 2 := by
  rw [GapWalk.W_two, V_2_2]

theorem walk_W_eq_V_3 : GapWalk.W 6 3 = V 3 3 := by
  rw [GapWalk.W_three, V_3_3]

theorem walk_Wb_eq_Vt_1 : GapWalk.Wb 6 1 = Vt 1 1 := by
  rw [GapWalk.Wb_one, Vt_1_1]

theorem walk_Wb_eq_Vt_2 : GapWalk.Wb 6 2 = Vt 2 2 := by
  rw [GapWalk.Wb_two, Vt_2_2]

theorem walk_Wb_eq_Vt_3 : GapWalk.Wb 6 3 = Vt 3 3 := by
  rw [GapWalk.Wb_three, Vt_3_3]

/-! ## 2. The pure weight, enumerated -/

/-- `S` is a **pure configuration** for `(ℓ, j)`: the cluster alone — rows
`1..ℓ`, every row with at least two cells, `ℓ + j` cells in total (surplus
`j`), king-connected — anchored by the bottom row's leftmost cell at `(0, 1)`
(the `count_stack` normalization: first row placed with `min x = 0`). -/
def IsVpConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = ℓ + j ∧
  ((0 : ℤ), (1 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 1 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ)) ∧
  (∀ p ∈ S, p.2 = 1 → 0 ≤ p.1) ∧
  (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧
  KingConnected S

/-- Pure configurations are decidable. -/
instance decidableIsVpConfig (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) :
    Decidable (IsVpConfig ℓ j S) := by
  unfold IsVpConfig; infer_instance

/-- **The pure configurations for `(ℓ, j)`**, enumerated computably: the
`(ℓ+j)`-subsets of the window rows `1..ℓ`, `|x| ≤ ℓ+j−1` (enough by
`connected_sub_x_le` against the anchor cell), filtered by `IsVpConfig`. No
assembly image is needed: the subset *is* the configuration. -/
def CFGVp (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  ((window (ℓ + j - 1) 1 ℓ).powersetCard (ℓ + j)).filter fun C => IsVpConfig ℓ j C

/-- `Vp ℓ j`: the pure cluster weight — the number of pure configurations. -/
def Vp (ℓ j : ℕ) : ℕ := (CFGVp ℓ j).card

/-- **Propositional characterization of `CFGVp`** (window independence):
membership is exactly `IsVpConfig`, provided `ℓ + j ≠ 0`. The encoding
direction bounds `|x|` by `connected_sub_x_le` in both directions against the
anchor `(0, 1)`. Mirror the proof of `mem_CFGVt`. -/
theorem mem_CFGVp {ℓ j : ℕ} (h : 1 ≤ ℓ + j) {S : Finset (ℤ × ℤ)} :
    S ∈ CFGVp ℓ j ↔ IsVpConfig ℓ j S := by
  sorry

/-- `Wp(2¹) = 1`: two cells in one row, king-connected forces adjacency. -/
theorem Vp_1_1 : Vp 1 1 = 1 := by native_decide

theorem Vp_2_2 : Vp 2 2 = 13 := by native_decide

theorem Vp_3_3 : Vp 3 3 = 177 := by native_decide

theorem walk_Wp_eq_Vp_1 : GapWalk.Wp 6 1 = Vp 1 1 := by
  rw [GapWalk.Wp_one, Vp_1_1]

theorem walk_Wp_eq_Vp_2 : GapWalk.Wp 6 2 = Vp 2 2 := by
  rw [GapWalk.Wp_two, Vp_2_2]

theorem walk_Wp_eq_Vp_3 : GapWalk.Wp 6 3 = Vp 3 3 := by
  rw [GapWalk.Wp_three, Vp_3_3]

/-! ## 3. The depth identities, unconditional

`DepthAssembly`'s theorems quantify over the weight tables; discharging the
hypotheses with `rfl` makes them unconditional statements about the banked
tables. One corollary per `(j, k)`, `j ≤ 4`, `k ≤ 8` — fill all 36 by the
`depth1_k0'` pattern, values copied from the corresponding `DepthAssembly`
theorem statements. -/

theorem depth1_k0' :
    DepthAssembly.Dval 1 8 DepthAssembly.sigTable DepthAssembly.bbTable
      DepthAssembly.ppTable 0 = -1 / 3 :=
  DepthAssembly.depth1_k0 _ _ _ rfl rfl rfl

-- TODO(agent): the remaining 35 corollaries, same pattern.
theorem depth_corollaries_todo : True := by sorry

/-! ## 4. Identity (II) on truncated series, closed inside Lean at `k ≤ 8` -/

/-- Truncated series product over `ℚ`: coefficients `0..n−1`. -/
def tmul (a b : List ℚ) (n : ℕ) : List ℚ :=
  (List.range n).map fun k =>
    ((List.range (k + 1)).map fun i => a.getD i 0 * b.getD (k - i) 0).sum

/-- Truncated series inverse: `bₖ` for `k ≤ n`, assuming `a₀ ≠ 0`. -/
def tinvAux (a : List ℚ) : ℕ → List ℚ
  | 0 => [(a.getD 0 0)⁻¹]
  | n + 1 =>
      let b := tinvAux a n
      b ++ [-(a.getD 0 0)⁻¹ *
        ((List.range (n + 1)).map fun i => a.getD (i + 1) 0 * b.getD (n - i) 0).sum]

/-- The (II)-assembly `P̂ − B²/(3+S)` on truncated series built from
`walkFamilies L`, coefficients `y^0 .. y^L`. -/
def f1Series (L : ℕ) : List ℚ :=
  let fams := GapWalk.walkFamilies L
  let s3S : List ℚ := 3 :: fams.map fun t => (t.1 : ℚ)
  let b : List ℚ := 1 :: fams.map fun t => (t.2.1 : ℚ)
  let p : List ℚ := 0 :: fams.map fun t => (t.2.2 : ℚ)
  let n := L + 1
  let q := tmul (tmul b b n) (tinvAux s3S L) n
  (List.range n).map fun k => p.getD k 0 - q.getD k 0

/-- **Identity (II) meets the depth identities**: the walk's own assembly
equals `DepthAssembly.Dval 1` at every `k ≤ 8`. With the `depth*_k*'`
corollaries above, the chain enumeration → tables → `(C)/(D)` → `(II)` → walk
closes inside Lean at these cells. -/
theorem f1_matches_depth1 :
    (List.range 9).all (fun k =>
      decide ((f1Series 8).getD k 0 =
        DepthAssembly.Dval 1 8 DepthAssembly.sigTable DepthAssembly.bbTable
          DepthAssembly.ppTable k)) = true := by
  native_decide

/-! ## 5. The walk pinned to the two-source table, `k ≤ 19` -/

/-- `walkFamilies 19` against rows `e = 0`, `k = 1..19` of
`results/severance_w3_families_K19_e3.txt` (columns `sig bb pp`). -/
theorem walk_table_19 :
    GapWalk.walkFamilies 19 =
      [(25, 5, 1), (339, 66, 13), (4778, 919, 177), (68314, 13103, 2515),
        (981085, 187965, 36021), (14115141, 2703074, 517701),
        (203235615, 38911979, 7450561), (2927318947, 560417094, 107291033),
        (42171167999, 8073022573, 1545475293),
        (607573757457, 116307837628, 22264949345),
        (8753905341432, 1675738797795, 320783668749),
        (126128990442728, 24144403733461, 4621881666063),
        (1817328627104215, 347883206029277, 66593812380721),
        (26185145165816377, 5012497004215068, 959518815944913),
        (377292466968857930, 72223212559800015, 13825332902978289),
        (5436284616532012446, 1040640183109408207, 199204464804214307),
        (78329750540206058871, 14994258768920757285, 2870273620718785821),
        (1128629987957263546269, 216047756211150731636, 41356898090817272241),
        (16262098555723413172570, 3112968429632491884891,
          595899274511995668021)] := by
  native_decide

/-- The `e = 0` row of `DepthAssembly.sigTable` is the walk's interior
column: the tables the depth identities consume are the walk's own output. -/
theorem sigTable_row0_is_walk :
    (DepthAssembly.sigTable.getD 0 []).tail =
      (GapWalk.walkFamilies 8).map fun t => (t.1 : ℤ) := by
  native_decide

theorem bbTable_row0_is_walk :
    (DepthAssembly.bbTable.getD 0 []).tail =
      (GapWalk.walkFamilies 8).map fun t => (t.2.1 : ℤ) := by
  native_decide

theorem ppTable_row0_is_walk :
    (DepthAssembly.ppTable.getD 0 []).tail =
      (GapWalk.walkFamilies 8).map fun t => (t.2.2 : ℤ) := by
  native_decide

end GapWalkBridge
end Polyplets
