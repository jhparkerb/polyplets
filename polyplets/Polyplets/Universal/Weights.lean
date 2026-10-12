/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Order.Interval.Finset.Nat
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

Both are instances of one structure, `IsConfig L cap ℓ j`, a cluster with
`cap` walk rows on top (`cap = 1` for `V`, `cap = 0` for `Vᵗ`), so the peeling
bijections of `Peel.lean` are written once. The king file's `IsInteriorConfig` and
`IsTopConfig` are the same two descriptions with `KingConnected` for `Connected L`,
identified with these at `kingLattice` by `King.lean`'s bridges.

## Deviation from the king file: no window enumeration

`Weights.lean` materializes each family as an explicit `Finset` built from a
computable window (`box`, `window`, `powersetCard`, decidable filter) so that
the kernel can decide the three small values it consumes, and then proves
*window-independence* lemmas (`mem_walkTop`, `mem_interiorConfigs`, `mem_topConfigs`) recovering
the propositional description. The bijections need only the propositional
descriptions — no value is ever evaluated here — so the generic families are
built directly as `Set.Finite.toFinset` of the propositionally-described
sets, and the `mem_*` lemmas are `Set.Finite.mem_toFinset`.

Finiteness replaces window-independence: it is the same x-spread bound
(`connected_abs_x_le`, now with reach `M`) applied to the whole family at once.
The instance anchors come from `Universal/Compute.lean`'s counter.
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
noncomputable def animals (L : RowLocal) (k H : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (animals_finite L (H + k) H).toFinset

lemma mem_animals {L : RowLocal} {k H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ animals L k H ↔ IsAnimal L (H + k) H S :=
  Set.Finite.mem_toFinset _

lemma card_animals (L : RowLocal) (k H : ℕ) :
    (animals L k H).card = T L (H + k) H := (T_eq_toFinset_card L (H + k) H).symm

/-- **Walk-top canonical sets**: the canonical `(n = H + k, H)` animals whose
top row `H - 1` is a walk row. -/
noncomputable def walkTop (L : RowLocal) (k H : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (animals L k H).filter fun S => rowSize S ((H : ℤ) - 1) = 1

/-- `d L k H`: the number of canonical height-`H` surplus-`k` `L`-animals whose
top row is a walk row — the primary object of the peeling recursion. -/
noncomputable def d (L : RowLocal) (k H : ℕ) : ℕ := (walkTop L k H).card

/-- **Propositional characterization of `walkTop`**: membership is exactly
canonicality plus walk top row. -/
theorem mem_walkTop {L : RowLocal} {k H : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ walkTop L k H ↔ IsAnimal L (H + k) H S ∧ rowSize S ((H : ℤ) - 1) = 1 := by
  rw [walkTop, Finset.mem_filter, mem_animals]

/-- The walk-top part of the full enumeration is exactly `walkTop L k H`. -/
lemma filter_animals_walkTop (L : RowLocal) (k H : ℕ) :
    (animals L k H).filter (fun S => rowSize S ((H : ℤ) - 1) = 1) = walkTop L k H := rfl

/-! ## Cluster configurations, aggregated by (rows ℓ, surplus j) -/

/-- `S` is a **cluster configuration** with `cap` walk rows on top, for
`(ℓ, j)`: the fixed walk cell `p = (0,0)` alone on row `0`; a cluster occupying
exactly rows `1..ℓ`, every one of those rows with at least two cells and `ℓ + j`
cells in all; then `cap` further rows `ℓ+1 .. ℓ+cap`, each a single walk cell;
and the whole `L`-connected. Positions are relative to `p`, pinned at the
origin — there is deliberately **no x-anchoring clause**. The peeling
bijections use `cap = 1` (an interior cluster bracketed by walk cells: the
V-configurations) and `cap = 0` (a cluster at the top edge: the
Vᵗ-configurations). -/
structure IsConfig (L : RowLocal) (cap ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop where
  /-- `ℓ + j + 1 + cap` cells: the cluster's `ℓ + j`, plus `p`, plus the cap. -/
  card : S.card = ℓ + j + 1 + cap
  /-- The fixed walk cell `p = (0, 0)`. -/
  origin : ((0 : ℤ), (0 : ℤ)) ∈ S
  /-- Everything on rows `0 … ℓ + cap`. -/
  rows : ∀ p ∈ S, 0 ≤ p.2 ∧ p.2 ≤ (ℓ : ℤ) + cap
  /-- Row `0` is the walk cell alone. -/
  row_zero : rowSize S 0 = 1
  /-- The cap rows `ℓ + 1 … ℓ + cap` are walk rows. -/
  cap_walk : ∀ y : ℤ, (ℓ : ℤ) < y → y ≤ (ℓ : ℤ) + cap → rowSize S y = 1
  /-- The cluster rows `1 … ℓ` each hold at least two cells. -/
  multi : ∀ i ∈ Finset.Icc 1 ℓ, 2 ≤ rowSize S (i : ℤ)
  /-- `L`-connected. -/
  conn : Connected L S

/-- `S` is a **V-configuration** for `(ℓ, j)` — the peeled data of case 2 of
the d-recursion: an interior cluster, with a free walk cell `q` alone on row
`ℓ + 1` above it; `ℓ + j + 2` cells in total. -/
abbrev IsInteriorConfig (L : RowLocal) (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop := IsConfig L 1 ℓ j S

/-- `S` is a **Vᵗ-configuration** for `(ℓ, j)` — a V-configuration without the
free walk cell `q` (the cluster caps the animal), hence `ℓ + j + 1` cells on
rows `0..ℓ`. -/
abbrev IsTopConfig (L : RowLocal) (ℓ j : ℕ) (S : Finset (ℤ × ℤ)) : Prop := IsConfig L 0 ℓ j S

/-- **Finiteness of a configuration family**: a configuration has
`ℓ + j + 1 + cap` cells, is connected and contains the origin, so it lies in
the box `[-M(ℓ+j+cap), M(ℓ+j+cap)] × [0, ℓ+cap]`. -/
lemma config_finite (L : RowLocal) (cap ℓ j : ℕ) :
    {S : Finset (ℤ × ℤ) | IsConfig L cap ℓ j S}.Finite := by
  apply Set.Finite.subset
    (Finset.powerset (Finset.Icc (-(L.reach * ((ℓ : ℤ) + (j : ℤ) + cap)), (0 : ℤ))
      (L.reach * ((ℓ : ℤ) + (j : ℤ) + cap), (ℓ : ℤ) + cap))).finite_toSet
  intro S hS
  obtain ⟨hcard, h0, hrows, -, -, -, hconn⟩ := hS
  rw [Finset.mem_coe, Finset.mem_powerset]
  intro p hpS
  have hx : |p.1| ≤ L.reach * ((ℓ : ℤ) + (j : ℤ) + cap) := by
    refine le_trans (connected_abs_x_le hconn h0 hpS) (le_of_eq ?_)
    rw [hcard]
    push_cast
    ring
  rw [abs_le] at hx
  have hy := hrows p hpS
  simp only [Finset.mem_Icc, Prod.le_def]
  refine ⟨⟨by omega, hy.1⟩, by omega, hy.2⟩

/-- **The configurations with `cap` walk rows on top, for `(ℓ, j)`** as a
finset. -/
noncomputable def configs (L : RowLocal) (cap ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  (config_finite L cap ℓ j).toFinset

/-- **Propositional characterization of `configs`**: membership is exactly
`IsConfig`. Downstream bijections match against this, never the
construction. -/
theorem mem_configs {L : RowLocal} {cap ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ configs L cap ℓ j ↔ IsConfig L cap ℓ j S := Set.Finite.mem_toFinset _

/-- **The V-configurations for `(ℓ, j)`** as a finset. -/
noncomputable abbrev interiorConfigs (L : RowLocal) (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  configs L 1 ℓ j

/-- **The Vᵗ-configurations for `(ℓ, j)`** as a finset. -/
noncomputable abbrev topConfigs (L : RowLocal) (ℓ j : ℕ) : Finset (Finset (ℤ × ℤ)) :=
  configs L 0 ℓ j

/-- `V L ℓ j`: the interior cluster weight — the number of V-configurations. -/
noncomputable def V (L : RowLocal) (ℓ j : ℕ) : ℕ := (interiorConfigs L ℓ j).card

/-- `Vt L ℓ j`: the top-edge cluster weight — the number of
Vᵗ-configurations. -/
noncomputable def Vt (L : RowLocal) (ℓ j : ℕ) : ℕ := (topConfigs L ℓ j).card

/-- Membership in `interiorConfigs` is exactly `IsInteriorConfig`. -/
theorem mem_interiorConfigs {L : RowLocal} {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ interiorConfigs L ℓ j ↔ IsInteriorConfig L ℓ j S := mem_configs

/-- Membership in `topConfigs` is exactly `IsTopConfig`. -/
theorem mem_topConfigs {L : RowLocal} {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    S ∈ topConfigs L ℓ j ↔ IsTopConfig L ℓ j S := mem_configs

end Polyplets.Universal
