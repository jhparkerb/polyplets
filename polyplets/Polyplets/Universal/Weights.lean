/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.RowProfile

/-!
# Peeling weights: walk-top counts `d L` and cluster configurations `V L`, `Vᵗ L`

`Weights.lean` generically. The primary object is `d L k H`, the number of
canonical height-`H`, surplus-`k` `L`-animals whose **top row is a walk row**;
the recursion's weights aggregate cluster configurations by (rows `ℓ`,
surplus `j`) only:

* `V L ℓ j` — interior weight: configurations of a cluster spanning rows
  `1..ℓ` (each with `≥ 2` cells, `ℓ + j` cells in total), together with the
  fixed walk cell `p = (0,0)` directly below and a free walk cell `q` on the row
  directly above, the whole connected, counted relative to `p`;
* `Vt L ℓ j` — top-edge weight: the same without `q`.

The propositional descriptions `IsVConfig`/`IsVtConfig` are the king file's,
with `KingConnected ↦ Conn L`.

## Deviation from the king file: no window enumeration

`Weights.lean` materializes each family as an explicit `Finset` built from a
computable window (`box`, `window`, `powersetCard`, decidable filter) so that
`native_decide` can evaluate it, and then proves *window-independence* lemmas
(`mem_Dc`, `mem_CFGV`, `mem_CFGVt`) recovering the propositional description.
Phase B needs only the propositional descriptions — no value is ever evaluated
here — so the generic families are built directly as `Set.Finite.toFinset` of
the propositionally-described sets. The `mem_*` lemmas are then
`Set.Finite.mem_toFinset`, and the downstream bijections match against exactly
the same propositions as in the king proof.

Finiteness replaces window-independence: it is the same x-spread bound
(`conn_abs_x_le`, now with reach `M`) applied to the whole family at once.
A computable twin for the instance anchors is phase C's business.
-/

namespace Polyplets.Universal

/-! ## Row size and walk-top canonical sets -/

/-- The number of cells of `S` in row `y`. `rowSize S r = 1` is exactly
`IsWalkRow S r`. -/
def rowSize (S : Finset (ℤ × ℤ)) (y : ℤ) : ℕ :=
  (S.filter fun c => c.2 = y).card

/-- `IsWalkRow` and `rowSize = 1` agree definitionally. -/
lemma isWalkRow_iff_rowSize {S : Finset (ℤ × ℤ)} {r : ℤ} :
    IsWalkRow S r ↔ rowSize S r = 1 := Iff.rfl

/-- The full canonical enumeration finset at `(H + k, H)`. -/
noncomputable def allCanon (L : RowLocal) (k H : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (canonical_finite L (H + k) H).toFinset

lemma mem_allCanon {L : RowLocal} {k H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ allCanon L k H ↔ IsCanonical L (H + k) H S :=
  Set.Finite.mem_toFinset _

lemma card_allCanon (L : RowLocal) (k H : ℕ) :
    (allCanon L k H).card = T L (H + k) H := (T_eq_toFinset_card L (H + k) H).symm

/-- **Walk-top canonical sets**: the canonical `(n = H + k, H)` animals whose
top row `H - 1` is a walk row. -/
noncomputable def Dc (L : RowLocal) (k H : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (allCanon L k H).filter fun S => rowSize S ((H : ℤ) - 1) = 1

/-- `d L k H`: the number of canonical height-`H` surplus-`k` `L`-animals whose
top row is a walk row — the primary object of the peeling recursion. -/
noncomputable def d (L : RowLocal) (k H : ℕ) : ℕ := (Dc L k H).card

/-- **Propositional characterization of `Dc`**: membership is exactly
canonicality plus walk top row. -/
theorem mem_Dc {L : RowLocal} {k H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ Dc L k H ↔ IsCanonical L (H + k) H S ∧ rowSize S ((H : ℤ) - 1) = 1 := by
  rw [Dc, Finset.mem_filter, mem_allCanon]

/-- The walk-top part of the full enumeration is exactly `Dc L k H`. -/
lemma filter_allCanon_walkTop (L : RowLocal) (k H : ℕ) :
    (allCanon L k H).filter (fun S => rowSize S ((H : ℤ) - 1) = 1) = Dc L k H := rfl

/-! ## Cluster configurations, aggregated by (rows ℓ, surplus j) -/

/-- `S` is a **V-configuration** for `(ℓ, j)` — the peeled data of case 2 of the
d-recursion: the fixed walk cell `p = (0,0)` alone on row `0`; a cluster
occupying exactly rows `1..ℓ`, every one of those rows with at least two cells;
a free walk cell `q` alone on row `ℓ + 1`; `ℓ + j + 2` cells in total; and the
whole `L`-connected. Positions are relative to `p`, pinned at the origin —
there is deliberately **no x-anchoring clause**. -/
def IsVConfig (L : RowLocal) (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = ℓ + j + 2 ∧
  ((0 : ℤ), (0 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + 1) ∧
  rowSize S 0 = 1 ∧
  rowSize S ((ℓ : ℤ) + 1) = 1 ∧
  (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧
  Conn L S

/-- `S` is a **Vᵗ-configuration** for `(ℓ, j)` — a V-configuration without the
free walk cell `q` (the cluster caps the animal), hence `ℓ + j + 1` cells on
rows `0..ℓ`. -/
def IsVtConfig (L : RowLocal) (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop :=
  S.card = ℓ + j + 1 ∧
  ((0 : ℤ), (0 : ℤ)) ∈ S ∧
  (∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ)) ∧
  rowSize S 0 = 1 ∧
  (∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)) ∧
  Conn L S

/-- **Finiteness of the V-family**: a V-configuration has `ℓ + j + 2` cells, is
connected and contains the origin, so it lies in the box
`[-M(ℓ+j+1), M(ℓ+j+1)] × [0, ℓ+1]`. -/
lemma vconfig_finite (L : RowLocal) (ℓ j : ℕ) :
    {S : Finset (ℤ × ℤ) | IsVConfig L ℓ j S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc (-(L.M * ((ℓ : ℤ) + (j : ℤ) + 1)), (0 : ℤ))
      (L.M * ((ℓ : ℤ) + (j : ℤ) + 1), (ℓ : ℤ) + 1))).finite_toSet
  intro S hS
  obtain ⟨hcard, h0, hrows, -, -, -, hconn⟩ := hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  have hx : |p.1| ≤ L.M * ((ℓ : ℤ) + (j : ℤ) + 1) := by
    refine le_trans (conn_abs_x_le hconn h0 hpS) (le_of_eq ?_)
    rw [hcard]
    push_cast
    ring
  rw [abs_le] at hx
  have hy := hrows p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  refine ⟨⟨by omega, hy.1⟩, by omega, hy.2⟩

/-- **Finiteness of the Vᵗ-family**. -/
lemma vtconfig_finite (L : RowLocal) (ℓ j : ℕ) :
    {S : Finset (ℤ × ℤ) | IsVtConfig L ℓ j S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc (-(L.M * ((ℓ : ℤ) + (j : ℤ))), (0 : ℤ))
      (L.M * ((ℓ : ℤ) + (j : ℤ)), (ℓ : ℤ)))).finite_toSet
  intro S hS
  obtain ⟨hcard, h0, hrows, -, -, hconn⟩ := hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  have hx : |p.1| ≤ L.M * ((ℓ : ℤ) + (j : ℤ)) := by
    refine le_trans (conn_abs_x_le hconn h0 hpS) (le_of_eq ?_)
    rw [hcard]
    push_cast
    ring
  rw [abs_le] at hx
  have hy := hrows p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  refine ⟨⟨by omega, hy.1⟩, by omega, hy.2⟩

/-- **The V-configurations for `(ℓ, j)`** as a finset. -/
noncomputable def CFGV (L : RowLocal) (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (vconfig_finite L ℓ j).toFinset

/-- `V L ℓ j`: the interior cluster weight — the number of V-configurations. -/
noncomputable def V (L : RowLocal) (ℓ j : ℕ) : ℕ := (CFGV L ℓ j).card

/-- **The Vᵗ-configurations for `(ℓ, j)`** as a finset. -/
noncomputable def CFGVt (L : RowLocal) (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (vtconfig_finite L ℓ j).toFinset

/-- `Vt L ℓ j`: the top-edge cluster weight — the number of
Vᵗ-configurations. -/
noncomputable def Vt (L : RowLocal) (ℓ j : ℕ) : ℕ := (CFGVt L ℓ j).card

/-- **Propositional characterization of `CFGV`**: membership is exactly
`IsVConfig`. Downstream bijections match against this, never the construction. -/
theorem mem_CFGV {L : RowLocal} {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ CFGV L ℓ j ↔ IsVConfig L ℓ j S := Set.Finite.mem_toFinset _

/-- **Propositional characterization of `CFGVt`**: membership is exactly
`IsVtConfig`. -/
theorem mem_CFGVt {L : RowLocal} {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ CFGVt L ℓ j ↔ IsVtConfig L ℓ j S := Set.Finite.mem_toFinset _

end Polyplets.Universal
