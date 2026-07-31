/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.System

/-!
# Gate GD-2: the generic construction at the king lattice

The king lattice is `D = {-1, 0, 1}`, `b = 3`. This file discharges the phase-B
gate: instantiating the generic geometric tree at `kingLattice` reproduces the
EXISTING `Peel.lean`/`Weights.lean` objects on the nose.

The chain is definitional all the way down:

* `adj_king` : `Adj kingLattice = kingAdj` (an `omega`-grade case bash — the
  king `|Δx| ≤ 1 ∧ |Δy| ≤ 1` form versus the row/up split);
* `conn_king`, `isCanonical_king`, `T_king`, `Dc_king`, `d_king`,
  `CFGV_king`, `V_king`, `CFGVt_king`, `Vt_king` — the objects agree;
* `b_king` : `kingLattice.b = 3`.

Two consequences are recorded:

* **the values agree** — spot-checks against the banked king numbers
  (`V 1 1 = 25`, `Vt 1 1 = 5`, `d 2 3 = 136`, `T(5,3) = 248`) and against the
  two numeric identity gates of `Weights.lean`, all re-derived here through the
  generic definitions;
* **the recursions agree** — `d_rec_king` and `c_ident_king` re-prove
  `Peel.lean`'s `d_rec` and `c_ident` from the generic geometry, so the
  `PeelSystem` built from them (`kingSystemGeneric`) inhabits exactly the same
  statements `Shape.lean` proves (`KingShapeD`, `KingShape`,
  `KingShapeProduction`, `KingProductionIntAll` of `AbstractShape.lean`).

The existing king tree is not touched; the numeric anchors reused here are its
own `native_decide` theorems, so these statements carry `Lean.ofReduceBool`
exactly where the king tree already did. Every generic result is
standard-axioms.
-/

namespace Polyplets.Universal

/-- The king lattice: up-offsets `{-1, 0, 1}`. -/
def kingLattice : RowLocal where
  D := {-1, 0, 1}
  hD := ⟨0, by decide⟩

/-- Membership in the king up-offset set is the king x-bound. -/
lemma mem_kingLattice_D {t : ℤ} : t ∈ kingLattice.D ↔ (-1 ≤ t ∧ t ≤ 1) := by
  change t ∈ ({-1, 0, 1} : Finset ℤ) ↔ _
  simp only [Finset.mem_insert, Finset.mem_singleton]
  omega

/-- **The king drift count is 3.** -/
@[simp] lemma b_king : kingLattice.b = 3 := by decide

/-- **The definitional anchor**: row-local adjacency at the king lattice IS king
adjacency. Given `p ≠ q`, "`|Δx| ≤ 1` and `|Δy| ≤ 1`" and "same row with
`|Δx| = 1`, or consecutive rows with `Δx ∈ {-1,0,1}`" are the same condition. -/
theorem adj_king {p q : ℤ × ℤ} : Adj kingLattice p q ↔ Polyplets.kingAdj p q := by
  have hne : (p ≠ q) ↔ ¬ (p.1 = q.1 ∧ p.2 = q.2) := not_congr Prod.ext_iff
  rw [Adj, Polyplets.kingAdj, hne]
  simp only [mem_kingLattice_D, abs_le, abs_eq (by norm_num : (0 : ℤ) ≤ 1)]
  omega

/-- King-connectivity agrees. -/
theorem conn_king {S : Finset (ℤ × ℤ)} : Conn kingLattice S ↔ Polyplets.KingConnected S := by
  unfold Conn Polyplets.KingConnected
  simp only [adj_king]

/-- Canonicality agrees. -/
theorem isCanonical_king {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    IsCanonical kingLattice n H S ↔ Polyplets.IsCanonical n H S := by
  unfold IsCanonical Polyplets.IsCanonical
  rw [conn_king]

/-- Row sizes agree definitionally. -/
theorem rowSize_king (S : Finset (ℤ × ℤ)) (y : ℤ) : rowSize S y = Polyplets.rowSize S y := rfl

/-- **The counts agree**: `T kingLattice = Polyplets.T`. -/
theorem T_king (n H : ℕ) : T kingLattice n H = Polyplets.T n H := by
  unfold T Polyplets.T
  congr 1
  ext S
  exact isCanonical_king

/-- The walk-top families agree. -/
theorem Dc_king (k H : ℕ) : Dc kingLattice k H = Polyplets.Dc k H := by
  ext S
  rw [mem_Dc, Polyplets.mem_Dc, isCanonical_king, rowSize_king]

/-- **The walk-top counts agree**: `d kingLattice = Polyplets.d`. -/
@[simp] theorem d_king (k H : ℕ) : d kingLattice k H = Polyplets.d k H := by
  change (Dc kingLattice k H).card = (Polyplets.Dc k H).card
  rw [Dc_king]

/-- V-configurations agree. -/
theorem isVConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVConfig kingLattice ℓ j S ↔ Polyplets.IsVConfig ℓ j S := by
  unfold IsVConfig Polyplets.IsVConfig
  simp only [rowSize_king, conn_king]

/-- Vᵗ-configurations agree. -/
theorem isVtConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVtConfig kingLattice ℓ j S ↔ Polyplets.IsVtConfig ℓ j S := by
  unfold IsVtConfig Polyplets.IsVtConfig
  simp only [rowSize_king, conn_king]

/-- The V-families agree. -/
theorem CFGV_king (ℓ j : ℕ) : CFGV kingLattice ℓ j = Polyplets.CFGV ℓ j := by
  ext S
  rw [mem_CFGV, Polyplets.mem_CFGV, isVConfig_king]

/-- The Vᵗ-families agree. -/
theorem CFGVt_king (ℓ j : ℕ) : CFGVt kingLattice ℓ j = Polyplets.CFGVt ℓ j := by
  ext S
  rw [mem_CFGVt, Polyplets.mem_CFGVt, isVtConfig_king]

/-- **The interior weights agree**: `V kingLattice = Polyplets.V`. -/
@[simp] theorem V_king (ℓ j : ℕ) : V kingLattice ℓ j = Polyplets.V ℓ j := by
  change (CFGV kingLattice ℓ j).card = (Polyplets.CFGV ℓ j).card
  rw [CFGV_king]

/-- **The top-edge weights agree**: `Vt kingLattice = Polyplets.Vt`. -/
@[simp] theorem Vt_king (ℓ j : ℕ) : Vt kingLattice ℓ j = Polyplets.Vt ℓ j := by
  change (CFGVt kingLattice ℓ j).card = (Polyplets.CFGVt ℓ j).card
  rw [CFGVt_king]

/-! ## The recursions agree

The generic bijections re-prove `Peel.lean`'s two identities at the king
lattice, `L.b` landing on the literal `3`. -/

/-- **`Peel.lean`'s `d_rec`, re-derived from the generic geometry.** -/
theorem d_rec_king (k H : ℕ) (hH : k + 2 ≤ H) :
    Polyplets.d k H = 3 * Polyplets.d k (H - 1) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        Polyplets.V ℓ j * Polyplets.d (k - j) (H - 1 - ℓ) := by
  have h := d_rec kingLattice k H hH
  simpa using h

/-- **`Peel.lean`'s `c_ident`, re-derived from the generic geometry.** -/
theorem c_ident_king (k H : ℕ) (hH : k + 1 ≤ H) :
    Polyplets.T (H + k) H = Polyplets.d k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
        Polyplets.Vt ℓ j * Polyplets.d (k - j) (H - ℓ) := by
  have h := c_ident kingLattice k H hH
  rw [T_king] at h
  simpa using h

/-- The king peeling system, with both recursion fields supplied by the
**generic** construction rather than by `Peel.lean`. -/
noncomputable def kingSystemGeneric : PeelSystem where
  b := 3
  hb := by norm_num
  d := Polyplets.d
  T := Polyplets.T
  V := Polyplets.V
  Vt := Polyplets.Vt
  d_rec := d_rec_king
  c_ident := c_ident_king

-- **GD-2, statement level**: the generic route inhabits exactly the four
-- statements `Shape.lean` proves — the same `example`s as GD-1, now routed
-- through the generic geometry.
example : KingShapeD := kingSystemGeneric.shape_d
example : KingShape := kingSystemGeneric.shape
example : KingShapeProduction := kingSystemGeneric.shape_production
example : KingProductionIntAll := fun _ _ hdeg hP => kingSystemGeneric.production_int_all hdeg hP

/-! ## GD-2 spot-checks against the banked king values

Each is the generic object evaluated at `kingLattice`, discharged by the
existing king theorem. The `native_decide` lives in the king tree, not here. -/

/-- `V kingLattice 1 1 = 25` — the paper's `16 + 9` gadget count. -/
theorem gd2_V_1_1 : V kingLattice 1 1 = 25 := by rw [V_king]; exact Polyplets.V_1_1

/-- `Vt kingLattice 1 1 = 5` — the paper's `4 + 1` gadget count. -/
theorem gd2_Vt_1_1 : Vt kingLattice 1 1 = 5 := by rw [Vt_king]; exact Polyplets.Vt_1_1

/-- `d kingLattice 2 3 = 136`. -/
theorem gd2_d_2_3 : d kingLattice 2 3 = 136 := by rw [d_king]; exact Polyplets.d_2_3

/-- `T kingLattice 5 3 = 248` — the banked `results/triangle.txt` value. -/
theorem gd2_T_5_3 : T kingLattice 5 3 = 248 := by rw [T_king]; exact Polyplets.T_5_3

/-- **Numeric gate on the generic d-recursion**, `k = 2, H = 4`:
`1019 = 3·136 + 25·5 + 49·3 + 339·1`, with `3 = kingLattice.b`. -/
theorem gd2_d_rec_k2_H4 :
    d kingLattice 2 4 = kingLattice.b * d kingLattice 2 3
      + V kingLattice 1 1 * d kingLattice 1 2
      + V kingLattice 1 2 * d kingLattice 0 2
      + V kingLattice 2 2 * d kingLattice 0 1 := by
  simp only [d_king, V_king, b_king]
  exact Polyplets.d_rec_check_k2_H4

/-- **Numeric gate on the generic c-identity**, `k = 2, H = 3`:
`T(5,3) = 248 = 136 + 5·5 + 7·3 + 66·1`. -/
theorem gd2_c_ident_k2_H3 :
    T kingLattice 5 3 = d kingLattice 2 3
      + Vt kingLattice 1 1 * d kingLattice 1 2
      + Vt kingLattice 1 2 * d kingLattice 0 2
      + Vt kingLattice 2 2 * d kingLattice 0 1 := by
  simp only [d_king, Vt_king, T_king]
  exact Polyplets.c_ident_check_k2_H3

/-! ## Axiom audit -/

#print axioms adj_king
#print axioms T_king
#print axioms d_king
#print axioms V_king
#print axioms Vt_king
#print axioms d_rec_king
#print axioms c_ident_king
#print axioms kingSystemGeneric
#print axioms gd2_V_1_1
#print axioms gd2_Vt_1_1
#print axioms gd2_d_2_3
#print axioms gd2_T_5_3
#print axioms gd2_d_rec_k2_H4
#print axioms gd2_c_ident_k2_H3

end Polyplets.Universal
