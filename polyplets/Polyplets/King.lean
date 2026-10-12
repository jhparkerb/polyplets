/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.System
import Polyplets.Weights

/-!
# The king lattice: the polyplet development as an instance

`Universal/` proves the peeling recursion and the diagonal law for every
row-local lattice. The king lattice is `D = {-1, 0, 1}`, `b = 3`, and this
file is the dictionary between the two vocabularies:

* `kingLattice`, and the definitional bridges `adj_king` (`Adj kingLattice`
  is `kingAdj`), `conn_king`, `isAnimal_king`, `T_king`, `Dc_king`,
  `d_king`, `V_king`, `Vt_king`: the generic objects at the king lattice are
  the king objects of `Defs.lean` and `Weights.lean` on the nose;
* the king-named theorems the rest of the development consumes — `d_rec`,
  `c_ident`, `shape_d`, `shape`, `shape_production`, `production_int_onset`,
  `production_int_all`, `T_diag_pow` — each the universal theorem at
  `kingLattice` rewritten through the bridges.

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

/-- An animal on the king lattice is a polyplet: the `n`-cell, height-`H`
`L`-animals at `kingLattice` are exactly `heightClass n H`. -/
theorem isAnimal_king {n H : ℕ} {S : Finset (ℤ × ℤ)} :
    IsAnimal kingLattice n H S ↔ S ∈ Polyplets.heightClass n H := by
  rw [Polyplets.mem_heightClass_iff]
  exact ⟨fun h => ⟨⟨h.card, conn_king.mp h.conn, h.anchored⟩, h.y_le, h.y_top⟩,
    fun ⟨h, h1, h2⟩ => ⟨h.card, conn_king.mpr h.conn, h.anchored, h1, h2⟩⟩

/-- Row sizes agree definitionally. -/
theorem rowSize_king (S : Finset (ℤ × ℤ)) (y : ℤ) : rowSize S y = Polyplets.rowSize S y := rfl

/-- **The counts agree**: `T kingLattice = Polyplets.T`. -/
theorem T_king (n H : ℕ) : T kingLattice n H = Polyplets.T n H := by
  unfold T Polyplets.T
  congr 1
  ext S
  exact isAnimal_king

/-- The walk-top families agree. -/
theorem Dc_king (k H : ℕ) : Dc kingLattice k H = Polyplets.Dc k H := by
  ext S
  rw [mem_Dc, Polyplets.mem_Dc, isAnimal_king, rowSize_king]

/-- **The walk-top counts agree**: `d kingLattice = Polyplets.d`. -/
@[simp] theorem d_king (k H : ℕ) : d kingLattice k H = Polyplets.d k H := by
  change (Dc kingLattice k H).card = (Polyplets.Dc k H).card
  rw [Dc_king]

/-- V-configurations agree: the universal `cap = 1` cap row is the king file's
`row_top`. -/
theorem isVConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVConfig kingLattice ℓ j S ↔ Polyplets.IsVConfig ℓ j S := by
  constructor
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      h.cap_walk _ (by omega) (by simp), h.multi, conn_king.mp h.conn⟩
  · intro h
    refine ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      fun y h1 h2 => ?_, h.multi, conn_king.mpr h.conn⟩
    rw [show y = (ℓ : ℤ) + 1 by push_cast at h2; omega]
    exact h.row_top

/-- Vᵗ-configurations agree. -/
theorem isVtConfig_king {ℓ j : ℕ} {S : Finset (ℤ × ℤ)} :
    IsVtConfig kingLattice ℓ j S ↔ Polyplets.IsVtConfig ℓ j S := by
  constructor
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero, h.multi,
      conn_king.mp h.conn⟩
  · intro h
    exact ⟨h.card, h.origin, fun p hp => by simpa using h.rows p hp, h.row_zero,
      fun y h1 h2 => by push_cast at h2; omega, h.multi, conn_king.mpr h.conn⟩

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

/-- **The c-identity**: for `H ≥ k + 1`, a polyplet has a walk top row
(counted by `d k H`) or a multi top row — a top-edge `Vᵗ`-configuration
capping a shorter walk-top remainder. -/
theorem c_ident (k H : ℕ) (hH : k + 1 ≤ H) :
    T (H + k) H = d k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt ℓ j * d (k - j) (H - ℓ) := by
  have h := Universal.c_ident kingLattice k H hH
  rw [T_king] at h
  simpa using h

/-! ## The shape theorem -/

/-- **Shape of the walk-top diagonal**: `d k H = δ_k(H) · 3^H` for all
`H ≥ k + 1`, with `δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem shape_d (k : ℕ) : ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H := by
  obtain ⟨δ, hdeg, h⟩ := universal_shape_d kingLattice k
  exact ⟨δ, hdeg, fun H hH => by simpa using h H hH⟩

/-- **Shape of the k-th diagonal**: `T(H+k, H) = q_k(H) · 3^H` for all
`H ≥ k + 1`, with `q_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem shape (k : ℕ) : ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (T (H + k) H : ℚ) = q.eval (H : ℚ) * 3 ^ H := by
  obtain ⟨q, hdeg, h⟩ := universal_shape kingLattice k
  refine ⟨q, hdeg, fun H hH => ?_⟩
  have hh := h H hH
  rw [T_king] at hh
  simpa using hh

/-- **Production form of the diagonal law**: for every `k` there is
`P_k ∈ ℚ[X]` of degree `≤ k` with `T(n, n-k) = P_k(n) · 3^(n-1-3k)` for all
`n ≥ 2k + 1` (the exponent an integer, negative on the onset window
`2k+1 ≤ n < 3k+1`), together with the zpow-free companion
`3^(3k+1) · T(n, n-k) = P_k(n) · 3^n`. -/
theorem shape_production (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) := by
  obtain ⟨P, hdeg, h1, h2⟩ := universal_shape_production kingLattice k
  refine ⟨P, hdeg, fun n hn => ?_, fun n hn => ?_⟩
  · have hh := h1 n hn
    rw [T_king] at hh
    simpa using hh
  · have hh := h2 n hn
    rw [T_king] at hh
    simpa using hh

/-- **Integrality at the pinning window**: for `2k+1 ≤ n ≤ 3k+1` the value
`P_k(n)` is the natural number `T(n, n-k) · 3^(3k+1-n)`. Stated for any `P`
satisfying the production identity. -/
theorem production_int_onset {k : ℕ} {P : Polynomial ℚ}
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ) := by
  have h := (peelSystem kingLattice).production_int_onset (P := P)
    (fun n hn => by simpa [T_king] using hP n hn) hn1 hn2
  simpa [T_king] using h

/-- **Integrality everywhere**: any `P` of degree `≤ k` satisfying the
production identity is integer-valued on all of `ℤ`. -/
theorem production_int_all {k : ℕ} {P : Polynomial ℚ} (hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (3 : ℚ) ^ (3 * k + 1) * (T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) :=
  universal_production_int_all kingLattice hdeg fun n hn => by
    rw [T_king]
    simpa using hP n hn

/-! ## The `k = 0` pin

`shape_production 0` gives a constant `P₀`, the single onset value `T 1 1 = 1`
(kernel-decided in `Compute.lean`) pins it, and the closed form
`T(n,n) = 3^(n-1)` follows. -/

/-- The `k = 0` diagonal pinned: `T(n, n) = 3^(n-1)` for `n ≥ 1`. -/
theorem T_diag_pow (n : ℕ) (hn : 1 ≤ n) : (T n n : ℚ) = (3 : ℚ) ^ ((n : ℤ) - 1) := by
  obtain ⟨P, hPdeg, hPzpow, -⟩ := shape_production 0
  have hPC : P = C (P.coeff 0) := eq_C_of_natDegree_le_zero hPdeg
  have h1 := hPzpow 1 (by omega)
  rw [hPC] at h1
  simp only [Nat.sub_zero, T_1_1, eval_C, Nat.cast_zero, Nat.cast_one, mul_zero,
    sub_zero] at h1
  norm_num at h1
  have h := hPzpow n (by omega)
  rw [hPC] at h
  simp only [Nat.sub_zero, eval_C, Nat.cast_zero, mul_zero, sub_zero] at h
  rw [h, ← h1, one_mul]

end Polyplets
