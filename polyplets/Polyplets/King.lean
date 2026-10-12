/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.Instance
import Polyplets.Weights

/-!
# The king lattice: the polyplet development as an instance

`Universal/` proves the peeling recursion and the diagonal law for every
row-local lattice. The king lattice is `D = {-1, 0, 1}`, `b = 3`, and this
file is the dictionary between the two vocabularies:

* `kingLattice`, and the definitional bridges `adj_king` (`Adj kingLattice`
  is `kingAdj`), `connected_king`, `isAnimal_king`, `T_king`, `walkTop_king`,
  `d_king`, `V_king`, `Vt_king`: the generic objects at the king lattice are
  the king objects of `Defs.lean` and `Weights.lean` on the nose;
* the king-named theorems the rest of the development consumes — `d_rec`,
  `T_of_d`, `exists_delta`, `exists_q`, `exists_isDiagonalPoly`,
  `IsDiagonalPoly.eval_onset`, `IsDiagonalPoly.intValued`, `T_self` — each the
  universal theorem at `kingLattice` rewritten through the bridges.

`Weights.lean` keeps the king weights as computable enumerations (the kernel
decides `V 1 1 = 25` and `d 0 1 = 1`, which `LeadingCoeff.lean` consumes);
`V_king`/`Vt_king` identify them with the generic, noncomputable ones.
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

/-- **The definitional bridge**: row-local adjacency at the king lattice IS king
adjacency. Given `p ≠ q`, "`|Δx| ≤ 1` and `|Δy| ≤ 1`" and "same row with
`|Δx| = 1`, or consecutive rows with `Δx ∈ {-1,0,1}`" are the same condition. -/
theorem adj_king {p q : ℤ × ℤ} : Adj kingLattice p q ↔ Polyplets.kingAdj p q := by
  have hne : (p ≠ q) ↔ ¬ (p.1 = q.1 ∧ p.2 = q.2) := not_congr Prod.ext_iff
  rw [Adj, Polyplets.kingAdj, hne]
  simp only [mem_kingLattice_D, abs_le, abs_eq (by norm_num : (0 : ℤ) ≤ 1)]
  omega

/-- King-connectivity agrees. -/
theorem connected_king {S : Finset (ℤ × ℤ)} :
    Connected kingLattice S ↔ Polyplets.KingConnected S := by
  unfold Connected Polyplets.KingConnected
  simp only [adj_king]

/-- An animal on the king lattice is a polyplet: the `n`-cell, height-`H`
`L`-animals at `kingLattice` are exactly `heightClass n H`. -/
theorem isAnimal_king {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    IsAnimal kingLattice n H S ↔ S ∈ Polyplets.heightClass n H := by
  rw [Polyplets.mem_heightClass_iff]
  exact ⟨fun h => ⟨⟨h.card, connected_king.mp h.conn, h.anchored⟩, h.y_le, h.y_top⟩,
    fun ⟨h, h1, h2⟩ => ⟨h.card, connected_king.mpr h.conn, h.anchored, h1, h2⟩⟩

/-- Row sizes agree definitionally. -/
theorem rowSize_king (S : Finset (ℤ × ℤ)) (y : ℤ) : rowSize S y = Polyplets.rowSize S y := rfl

/-- **The counts agree**: `T kingLattice = Polyplets.T`. -/
theorem T_king (n H : ℕ) : T kingLattice n H = Polyplets.T n H := by
  unfold T Polyplets.T
  congr 1
  ext S
  exact isAnimal_king

/-- The walk-top families agree. -/
theorem walkTop_king (k H : ℕ) : walkTop kingLattice k H = Polyplets.walkTop k H := by
  ext S
  rw [mem_walkTop, Polyplets.mem_walkTop, isAnimal_king, rowSize_king]

/-- **The walk-top counts agree**: `d kingLattice = Polyplets.d`. -/
@[simp] theorem d_king (k H : ℕ) : d kingLattice k H = Polyplets.d k H := by
  change (walkTop kingLattice k H).card = (Polyplets.walkTop k H).card
  rw [walkTop_king]

/-- V-configurations agree: the universal `cap = 1` cap row is the king file's
`row_top`. -/
theorem isInteriorConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsInteriorConfig kingLattice ℓ j S ↔ Polyplets.IsInteriorConfig ℓ j S := by
  constructor
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      h.cap_walk _ (by omega) (by simp), h.multi, connected_king.mp h.conn⟩
  · intro h
    refine ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      fun y h1 h2 => ?_, h.multi, connected_king.mpr h.conn⟩
    rw [show y = (ℓ : ℤ) + 1 by push_cast at h2; omega]
    exact h.row_top

/-- Vᵗ-configurations agree. -/
theorem isTopConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsTopConfig kingLattice ℓ j S ↔ Polyplets.IsTopConfig ℓ j S := by
  constructor
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero, h.multi,
      connected_king.mp h.conn⟩
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      fun y h1 h2 => by push_cast at h2; omega, h.multi, connected_king.mpr h.conn⟩

/-- The V-families agree. -/
theorem interiorConfigs_king (ℓ j : ℕ) :
    interiorConfigs kingLattice ℓ j = Polyplets.interiorConfigs ℓ j := by
  ext S
  rw [mem_interiorConfigs, Polyplets.mem_interiorConfigs, isInteriorConfig_king]

/-- The Vᵗ-families agree. -/
theorem topConfigs_king (ℓ j : ℕ) : topConfigs kingLattice ℓ j = Polyplets.topConfigs ℓ j := by
  ext S
  rw [mem_topConfigs, Polyplets.mem_topConfigs, isTopConfig_king]

/-- **The interior weights agree**: `V kingLattice = Polyplets.V`. -/
@[simp] theorem V_king (ℓ j : ℕ) : V kingLattice ℓ j = Polyplets.V ℓ j := by
  change (interiorConfigs kingLattice ℓ j).card = (Polyplets.interiorConfigs ℓ j).card
  rw [interiorConfigs_king]

/-- **The top-edge weights agree**: `Vt kingLattice = Polyplets.Vt`. -/
@[simp] theorem Vt_king (ℓ j : ℕ) : Vt kingLattice ℓ j = Polyplets.Vt ℓ j := by
  change (topConfigs kingLattice ℓ j).card = (Polyplets.topConfigs ℓ j).card
  rw [topConfigs_king]

end Polyplets.Universal

namespace Polyplets

open Polynomial Universal

/-! ## The peeling identities -/

/-- **The d-recursion**: for `H ≥ k + 2`, a walk-top animal splits by its
second-top row — walk (three offsets on a height-`H-1` walk-top remainder) or
the base of a cluster (an interior `V`-configuration capping a shorter walk-top
remainder). -/
theorem d_rec (k H : ℕ) (hH : k + 2 ≤ H) :
    d k H = 3 * d k (H - 1) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V ℓ j * d (k - j) (H - 1 - ℓ) := by
  simpa using Universal.d_rec kingLattice k H hH

/-- **The top-row identity**: for `H ≥ k + 1`, a polyplet has a walk top row
(counted by `d k H`) or a multi top row — a top-edge `Vᵗ`-configuration
capping a shorter walk-top remainder. -/
theorem T_of_d (k H : ℕ) (hH : k + 1 ≤ H) :
    T (H + k) H = d k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt ℓ j * d (k - j) (H - ℓ) := by
  have h := Universal.T_of_d kingLattice k H hH
  rw [T_king] at h
  simpa using h

/-! ## The diagonal law -/

/-- **Shape of the walk-top diagonal**: `d k H = δ_k(H) · 3^H` for all
`H ≥ k + 1`, with `δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem exists_delta (k : ℕ) : ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H := by
  obtain ⟨δ, hdeg, h⟩ := Universal.exists_delta kingLattice k
  exact ⟨δ, hdeg, fun H hH => by simpa using h H hH⟩

/-- **Shape of the k-th diagonal**: `T(H+k, H) = q_k(H) · 3^H` for all
`H ≥ k + 1`, with `q_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem exists_q (k : ℕ) : ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (T (H + k) H : ℚ) = q.eval (H : ℚ) * 3 ^ H := by
  obtain ⟨q, hdeg, h⟩ := Universal.exists_q kingLattice k
  refine ⟨q, hdeg, fun H hH => ?_⟩
  have hh := h H hH
  rw [T_king] at hh
  simpa using hh

/-- **`P` is the polynomial of the `k`-th diagonal**: `T(n, n-k) = P(n) · 3^(n-1-3k)`
for all `n ≥ 2k + 1` — the report's diagonal law, for a given `P`. The
exponent is an integer (`zpow`), negative on the onset window
`2k+1 ≤ n < 3k+1`. -/
def IsDiagonalPoly (k : ℕ) (P : Polynomial ℚ) : Prop :=
  ∀ n : ℕ, 2 * k + 1 ≤ n → (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k)

/-- The king instance of the row-local predicate. -/
lemma isDiagonalPoly_king {k : ℕ} {P : Polynomial ℚ} :
    Universal.IsDiagonalPoly kingLattice k P ↔ IsDiagonalPoly k P := by
  simp only [Universal.IsDiagonalPoly, IsDiagonalPoly, T_king, b_king, Nat.cast_ofNat]

/-- **The diagonal law**: for every `k` there is `P_k ∈ ℚ[X]` of degree `≤ k`
with `T(n, n-k) = P_k(n) · 3^(n-1-3k)` for all `n ≥ 2k + 1`. -/
theorem exists_isDiagonalPoly (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    IsDiagonalPoly k P := by
  obtain ⟨P, hdeg, h⟩ := Universal.exists_isDiagonalPoly kingLattice k
  exact ⟨P, hdeg, isDiagonalPoly_king.mp h⟩

/-- The zpow-free form of the law: `3^(3k+1) · T(n, n-k) = P(n) · 3^n`. -/
theorem IsDiagonalPoly.cleared {k : ℕ} {P : Polynomial ℚ} (hP : IsDiagonalPoly k P) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n := by
  have h := (isDiagonalPoly_king.mpr hP).cleared
  simpa [T_king] using h

/-- **The values on the onset window are counts**: for `2k+1 ≤ n ≤ 3k+1`,
`P(n)` is the natural number `T(n, n-k) · 3^(3k+1-n)`. -/
theorem IsDiagonalPoly.eval_onset {k : ℕ} {P : Polynomial ℚ} (hP : IsDiagonalPoly k P)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ) := by
  have h := (isDiagonalPoly_king.mpr hP).eval_onset hn1 hn2
  simpa [T_king] using h

/-- **Integrality everywhere**: any `P` of degree `≤ k` satisfying the law is
integer-valued on all of `ℤ`. -/
theorem IsDiagonalPoly.intValued {k : ℕ} {P : Polynomial ℚ} (hdeg : P.natDegree ≤ k)
    (hP : IsDiagonalPoly k P) : ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) :=
  (isDiagonalPoly_king.mpr hP).intValued hdeg

/-! ## The `k = 0` diagonal

`exists_isDiagonalPoly 0` gives a constant `P₀`, the single onset value
`T 1 1 = 1` (`Defs.lean`) pins it, and the closed form `T(n,n) = 3^(n-1)`
follows. -/

/-- **`T(n, n) = 3^(n-1)`** for `n ≥ 1`: the `k = 0` diagonal. -/
theorem T_self (n : ℕ) (hn : 1 ≤ n) : (T n n : ℚ) = (3 : ℚ) ^ ((n : ℤ) - 1) := by
  obtain ⟨P, hPdeg, hP⟩ := exists_isDiagonalPoly 0
  have hPC : P = C (P.coeff 0) := eq_C_of_natDegree_le_zero hPdeg
  have h1 := hP 1 (by omega)
  rw [hPC] at h1
  simp only [Nat.sub_zero, T_1_1, eval_C, Nat.cast_zero, Nat.cast_one, mul_zero,
    sub_zero] at h1
  norm_num at h1
  have h := hP n (by omega)
  rw [hPC] at h
  simp only [Nat.sub_zero, eval_C, Nat.cast_zero, mul_zero, sub_zero] at h
  rw [h, ← h1, one_mul]

end Polyplets
