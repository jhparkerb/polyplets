/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Shape

/-!
# AbstractShape: the diagonal law over an abstract peeling system

`Shape.lean` proves the king diagonal law from `Peel.lean` through a very thin
interface: the two recursions (`d_rec`, `c_ident`) and nothing else. This file
extracts that interface as a structure `PeelSystem` carrying a drift count
`b : ℕ` in place of the king's `3`, and re-proves the four shape theorems
generically:

* `PeelSystem.shape_d` : `d k H = δ_k(H) · b^H` for `H ≥ k + 1`, `deg δ_k ≤ k`;
* `PeelSystem.shape` : `T(H+k, H) = q_k(H) · b^H` for `H ≥ k + 1`;
* `PeelSystem.shape_production` : `T(n, n-k) = P_k(n) · b^(n-1-3k)` for
  `n ≥ 2k+1` (`zpow`, so the onset window `2k+1 ≤ n < 3k+1` is covered), plus
  the zpow-free companion `b^(3k+1) · T(n, n-k) = P_k(n) · b^n`;
* `PeelSystem.production_int_all` : any such `P_k` is integer-valued on `ℤ`.

The proof scripts are `Shape.lean`'s, with `3 ↦ S.b` and the literal
`(3 : ℚ) ≠ 0` side conditions replaced by `PeelSystem.b_ne_zero` (whence the
field `hb : 1 ≤ b`). This is the formalized half of the "verbatim wager" of
`docs/proofs/universal-diagonal-law.md`: steps 3–5 of that proof carry over
with `b` in place of `3`. The geometric half (steps 1–2: producing a
`PeelSystem` from a row-local lattice) is the next phase; this file is
lattice-agnostic and settles the algebra.

## What the shape law needs from a lattice

Exactly the eight fields of `PeelSystem` — most of them data. The proofs use
NO base values, NO support or vanishing ranges for `V`/`Vt`, and NO
arithmetic property of `b` beyond `b ≠ 0`:

* the drift count `b` with `1 ≤ b` (the recursion's homogeneous coefficient;
  `1 ≤ b` is used only as `(b : ℚ) ≠ 0`, to divide by powers of `b`);
* the four numeric families `d`, `T`, `V`, `Vt` (opaque);
* the recursion `d_rec` and the top-row identity `c_ident`.

Notably the ranges `Finset.Icc 1 k` / `Finset.Icc 1 j` in the two recursions
carry all the support information the induction needs: `ℓ ≤ j ≤ k` is what puts
every recursive `d (k-j) (H-1-ℓ)` above its own onset, by `omega`.

## Integrality: no p-adic argument needed

Step 5 of the paper proof argues integrality of `P_k` p-adically, prime by
prime over `p ∣ b`, which for the king case is `p = 3` — the one place where
primality of `3` could plausibly have been used. The Lean route never needs it:
tier 1 (`production_int_onset`) reads `P_k(n)` off the zpow-free identity as
the *natural number* `T(n,n-k) · b^(3k+1-n)` on the onset window
`2k+1 ≤ n ≤ 3k+1` (exact division by `b^n`, valid for any `b ≠ 0`), and tier 2
(`production_int_all`) extends by finite differences over the `k+1` consecutive
onset points. Both are prime-agnostic; `b` is never factored.
-/

namespace Polyplets.Universal

open Polynomial

/-! ## The interface -/

/-- **A peeling system**: the finite numeric interface that the diagonal-law
algebra consumes. `b` is the drift count (`3` for the king lattice, `|D|` in
general); `d k H` counts walk-top animals of surplus `k` and height `H`;
`T n H` counts all canonical animals; `V`/`Vt` are the interior and top-edge
cluster weights. The two recursions are `Peel.lean`'s `d_rec` and `c_ident`
verbatim with `3 ↦ b`. -/
structure PeelSystem where
  /-- The drift count: the number of up-offsets of the lattice. -/
  b : ℕ
  /-- The drift count is positive (the up-offset set is nonempty). Used only
  through `(b : ℚ) ≠ 0`. -/
  hb : 1 ≤ b
  /-- `d k H`: walk-top animals of surplus `k` and height `H`. -/
  d : ℕ → ℕ → ℕ
  /-- `T n H`: all canonical animals with `n` cells and height `H`. -/
  T : ℕ → ℕ → ℕ
  /-- `V ℓ j`: the interior cluster weight at span `ℓ`, surplus `j`. -/
  V : ℕ → ℕ → ℕ
  /-- `Vt ℓ j`: the top-edge cluster weight at span `ℓ`, surplus `j`. -/
  Vt : ℕ → ℕ → ℕ
  /-- **The d-recursion**: a walk-top animal splits by its second-top row —
  a drift step (`b` choices) or the base of a cluster. -/
  d_rec : ∀ k H : ℕ, k + 2 ≤ H →
    d k H = b * d k (H - 1) +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, V ℓ j * d (k - j) (H - 1 - ℓ)
  /-- **The c-identity**: a canonical animal has a walk top row or a top-edge
  cluster capping a shorter walk-top remainder. -/
  c_ident : ∀ k H : ℕ, k + 1 ≤ H →
    T (H + k) H = d k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt ℓ j * d (k - j) (H - ℓ)

namespace PeelSystem

variable (S : PeelSystem)

/-- The drift count is invertible in `ℚ` — the only arithmetic fact about `b`
the shape law uses. -/
lemma b_ne_zero : (S.b : ℚ) ≠ 0 := by
  have := S.hb
  positivity

/-- Powers of the drift count are invertible in `ℚ`. -/
lemma b_pow_ne_zero (m : ℕ) : (S.b : ℚ) ^ m ≠ 0 := pow_ne_zero _ S.b_ne_zero

/-! ## Shape of the walk-top counts -/

/-- The strong-induction step for `shape_d` (`Shape.lean`'s `shape_d_step`
with `3 ↦ S.b`): lower-surplus polynomials give the surplus-`k` one. The
d-recursion divided by `b^H` is the difference equation `e(H) = e(H-1) + g(H)`;
telescoping from `H₀ = k+1` and summing `g` by `exists_poly_sum_Icc` gives
`δ_k`, with the base value absorbed into the constant term. -/
lemma shape_d_step (k : ℕ)
    (IH : ∀ j, j < k → ∃ δ : Polynomial ℚ, δ.natDegree ≤ j ∧
      ∀ H : ℕ, j + 1 ≤ H → (S.d j H : ℚ) = δ.eval (H : ℚ) * (S.b : ℚ) ^ H) :
    ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (S.d k H : ℚ) = δ.eval (H : ℚ) * (S.b : ℚ) ^ H := by
  classical
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  -- totalize the induction hypothesis into a plain family of polynomials
  obtain ⟨δ', hδ'deg, hδ'val⟩ : ∃ δ' : ℕ → Polynomial ℚ,
      (∀ j, j < k → (δ' j).natDegree ≤ j) ∧
      (∀ j, j < k → ∀ H : ℕ, j + 1 ≤ H →
        (S.d j H : ℚ) = (δ' j).eval (H : ℚ) * (S.b : ℚ) ^ H) := by
    choose δfun hdeg hval using IH
    exact ⟨fun j => if h : j < k then δfun j h else 0,
      fun j hj => by simp only [dif_pos hj]; exact hdeg j hj,
      fun j hj H hH => by simp only [dif_pos hj]; exact hval j hj H hH⟩
  -- the inhomogeneity of the difference equation for `d k H / b^H`
  set g : Polynomial ℚ := ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
    C ((S.V ℓ j : ℚ) / (S.b : ℚ) ^ (ℓ + 1)) * (δ' (k - j)).comp (X - C ((ℓ : ℚ) + 1)) with hg
  have hgdeg : g.natDegree ≤ k - 1 := by
    rw [hg]
    refine natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
    refine natDegree_sum_le_of_forall_le _ _ fun ℓ _ => ?_
    rw [Finset.mem_Icc] at hj
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    have hd := hδ'deg (k - j) (by omega)
    omega
  obtain ⟨G, hGdeg₀, hG0, hGsum⟩ := exists_poly_sum_Icc g
  have hGdeg : G.natDegree ≤ k := by
    rcases Nat.eq_zero_or_pos k with rfl | hk
    · have hgz : g = 0 := by
        rw [hg, Finset.Icc_eq_empty (by omega), Finset.sum_empty]
      rw [hG0 hgz, natDegree_zero]
    · omega
  refine ⟨C ((S.d k (k + 1) : ℚ) / (S.b : ℚ) ^ (k + 1) - G.eval ((k : ℚ) + 1)) + G, ?_, ?_⟩
  · exact le_trans (natDegree_add_le _ _) (max_le (by simp) hGdeg)
  · intro H hH
    induction H, hH using Nat.le_induction with
    | base =>
      have hcast : ((k + 1 : ℕ) : ℚ) = (k : ℚ) + 1 := by push_cast; ring
      simp only [eval_add, eval_C, hcast]
      have hb1 : ((S.b : ℚ)) ^ (k + 1) ≠ 0 := S.b_pow_ne_zero _
      field_simp
      ring
    | succ m hm ihm =>
      -- the d-recursion at `H = m + 1`, cast to ℚ
      have hrec := S.d_rec k (m + 1) (by omega)
      simp only [Nat.add_sub_cancel] at hrec
      have hrecQ : (S.d k (m + 1) : ℚ) = (S.b : ℚ) * (S.d k m : ℚ)
          + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
              (S.V ℓ j : ℚ) * (S.d (k - j) (m - ℓ) : ℚ) := by exact_mod_cast hrec
      -- every d-term is in range for the lower-surplus polynomials
      have hsum : ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
          (S.V ℓ j : ℚ) * (S.d (k - j) (m - ℓ) : ℚ)
          = g.eval ((m + 1 : ℕ) : ℚ) * (S.b : ℚ) ^ (m + 1) := by
        rw [hg, eval_finsetSum, Finset.sum_mul]
        refine Finset.sum_congr rfl fun j hj => ?_
        rw [eval_finsetSum, Finset.sum_mul]
        refine Finset.sum_congr rfl fun ℓ hℓ => ?_
        rw [Finset.mem_Icc] at hj hℓ
        have hlm : ℓ ≤ m := by omega
        have hrange : (k - j) + 1 ≤ m - ℓ := by omega
        rw [hδ'val (k - j) (by omega) (m - ℓ) hrange]
        simp only [eval_mul, eval_C, eval_comp, eval_sub, eval_X]
        have hcast : ((m - ℓ : ℕ) : ℚ) = ((m + 1 : ℕ) : ℚ) - ((ℓ : ℚ) + 1) := by
          rw [Nat.cast_sub hlm]
          push_cast
          ring
        have hpow : (S.b : ℚ) ^ (m + 1) = (S.b : ℚ) ^ (m - ℓ) * (S.b : ℚ) ^ (ℓ + 1) := by
          rw [← pow_add]
          congr 1
          omega
        rw [hcast, hpow]
        have hb1 : ((S.b : ℚ)) ^ (ℓ + 1) ≠ 0 := S.b_pow_ne_zero _
        field_simp
      -- the discrete-derivative property of the antiderivative at `m + 1`
      have hδstep :
          (C ((S.d k (k + 1) : ℚ) / (S.b : ℚ) ^ (k + 1) - G.eval ((k : ℚ) + 1)) + G).eval
            ((m + 1 : ℕ) : ℚ)
          = (C ((S.d k (k + 1) : ℚ) / (S.b : ℚ) ^ (k + 1)
              - G.eval ((k : ℚ) + 1)) + G).eval (m : ℚ)
            + g.eval ((m + 1 : ℕ) : ℚ) := by
        have h1 := hGsum (m + 1) (m + 1) (by omega)
        rw [Finset.Icc_self, Finset.sum_singleton] at h1
        have hcast : ((m + 1 : ℕ) : ℚ) - 1 = (m : ℚ) := by push_cast; ring
        rw [hcast] at h1
        simp only [eval_add, eval_C]
        rw [h1]
        ring
      rw [hrecQ, hsum, ihm, hδstep]
      ring

/-- **Shape of the walk-top diagonal**: `d k H = δ_k(H) · b^H` for all
`H ≥ k + 1`, with `δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem shape_d : ∀ k : ℕ, ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (S.d k H : ℚ) = δ.eval (H : ℚ) * (S.b : ℚ) ^ H := fun k =>
  Nat.strong_induction_on k S.shape_d_step

/-- **Shape of the k-th diagonal**: `T(H+k, H) = q_k(H) · b^H` for all
`H ≥ k + 1`, with `q_k ∈ ℚ[X]` of degree `≤ k`. From `shape_d` through the
c-identity: at `H ≥ k + 1` every `d`-term of `c_ident` is exactly in range. -/
theorem shape (k : ℕ) : ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (S.T (H + k) H : ℚ) = q.eval (H : ℚ) * (S.b : ℚ) ^ H := by
  classical
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  choose δ hδdeg hδval using S.shape_d
  refine ⟨δ k + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
    C ((S.Vt ℓ j : ℚ) / (S.b : ℚ) ^ ℓ) * (δ (k - j)).comp (X - C (ℓ : ℚ)), ?_, ?_⟩
  · refine le_trans (natDegree_add_le _ _) (max_le (hδdeg k) ?_)
    refine natDegree_sum_le_of_forall_le _ _ fun j hj => ?_
    refine natDegree_sum_le_of_forall_le _ _ fun ℓ _ => ?_
    rw [Finset.mem_Icc] at hj
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    have := hδdeg (k - j)
    omega
  · intro H hH
    have hcQ : (S.T (H + k) H : ℚ) = (S.d k H : ℚ)
        + ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j,
            (S.Vt ℓ j : ℚ) * (S.d (k - j) (H - ℓ) : ℚ) := by
      exact_mod_cast S.c_ident k H (by omega)
    rw [hcQ, eval_add, add_mul, hδval k H hH]
    congr 1
    rw [eval_finsetSum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun j hj => ?_
    rw [eval_finsetSum, Finset.sum_mul]
    refine Finset.sum_congr rfl fun ℓ hℓ => ?_
    rw [Finset.mem_Icc] at hj hℓ
    have hlH : ℓ ≤ H := by omega
    have hrange : (k - j) + 1 ≤ H - ℓ := by omega
    rw [hδval (k - j) (H - ℓ) hrange]
    simp only [eval_mul, eval_C, eval_comp, eval_sub, eval_X]
    have hcast : ((H - ℓ : ℕ) : ℚ) = (H : ℚ) - (ℓ : ℚ) := by
      rw [Nat.cast_sub hlH]
    have hpow : (S.b : ℚ) ^ H = (S.b : ℚ) ^ (H - ℓ) * (S.b : ℚ) ^ ℓ := by
      rw [← pow_add]
      congr 1
      omega
    rw [hcast, hpow]
    have hb1 : ((S.b : ℚ)) ^ ℓ ≠ 0 := S.b_pow_ne_zero _
    field_simp

/-! ## The production form -/

/-- **Production form of the diagonal law**: for every `k` there is
`P_k ∈ ℚ[X]` of degree `≤ k` with

* `T(n, n-k) = P_k(n) · b^(n-1-3k)` for all `n ≥ 2k + 1`, the exponent an
  integer (`zpow`) — negative on the onset window `2k+1 ≤ n < 3k+1`, where
  `P_k(n)` carries the compensating powers of `b`; and
* the zpow-free companion `b^(3k+1) · T(n, n-k) = P_k(n) · b^n`.

`P_k(n) = b^(2k+1) · q_k(n - k)` for the `q_k` of `shape`. The `3` in the
exponent `n - 1 - 3k` is structural bookkeeping (`k` from `H = n - k` plus
`2k + 1` from the normalization), NOT the king drift count: it survives the
generalization unchanged. -/
theorem shape_production (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
    (∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.b : ℚ) ^ (3 * k + 1) * (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ n) := by
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  obtain ⟨q, hqdeg, hq⟩ := S.shape k
  have hbase : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.T n (n - k) : ℚ) = q.eval ((n : ℚ) - (k : ℚ)) * (S.b : ℚ) ^ (n - k) := by
    intro n hn
    have hkn : k ≤ n := by omega
    have h1 := hq (n - k) (by omega)
    rw [Nat.sub_add_cancel hkn] at h1
    rw [h1, Nat.cast_sub hkn]
  set P : Polynomial ℚ := C ((S.b : ℚ) ^ (2 * k + 1)) * q.comp (X - C (k : ℚ)) with hP
  have hPeval : ∀ x : ℚ, P.eval x = (S.b : ℚ) ^ (2 * k + 1) * q.eval (x - (k : ℚ)) := by
    intro x
    rw [hP, eval_mul, eval_C, eval_comp, eval_sub, eval_X, eval_C]
  refine ⟨P, ?_, ?_, ?_⟩
  · rw [hP]
    refine le_trans (natDegree_C_mul_le _ _) (le_trans natDegree_comp_le ?_)
    rw [natDegree_X_sub_C, mul_one]
    exact hqdeg
  · intro n hn
    have hkn : k ≤ n := by omega
    rw [hbase n hn, hPeval]
    have hz : (S.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k)
        = (S.b : ℚ) ^ (n - k) / (S.b : ℚ) ^ (2 * k + 1) := by
      have hexp : (n : ℤ) - 1 - 3 * k = ((n - k : ℕ) : ℤ) - ((2 * k + 1 : ℕ) : ℤ) := by omega
      rw [hexp, zpow_sub₀ hbne, zpow_natCast, zpow_natCast]
    rw [hz]
    have hb1 : ((S.b : ℚ)) ^ (2 * k + 1) ≠ 0 := S.b_pow_ne_zero _
    field_simp
  · intro n hn
    have hkn : k ≤ n := by omega
    rw [hbase n hn, hPeval]
    have hpow : (S.b : ℚ) ^ (3 * k + 1) * (S.b : ℚ) ^ (n - k)
        = (S.b : ℚ) ^ (2 * k + 1) * (S.b : ℚ) ^ n := by
      rw [← pow_add, ← pow_add]
      congr 1
      omega
    linear_combination q.eval ((n : ℚ) - (k : ℚ)) * hpow

/-! ## Integrality -/

/-- **Integrality at the pinning window** (tier 1): for `2k+1 ≤ n ≤ 3k+1` the
value `P_k(n)` is the natural number `T(n, n-k) · b^(3k+1-n)`. These are
exactly the `k+1` onset points `H = k+1 .. 2k+1` (`n = H+k`). Stated for any
`P` satisfying the production identity.

This is the step the paper proof runs p-adically over the primes dividing `b`;
here it is exact division by `b^n` and uses no factorization of `b`. -/
theorem production_int_onset {k : ℕ} {P : Polynomial ℚ}
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.b : ℚ) ^ (3 * k + 1) * (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ n)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((S.T n (n - k) * S.b ^ (3 * k + 1 - n) : ℕ) : ℚ) := by
  have h := hP n hn1
  have hpow : (S.b : ℚ) ^ (3 * k + 1) = (S.b : ℚ) ^ (3 * k + 1 - n) * (S.b : ℚ) ^ n := by
    rw [← pow_add]
    congr 1
    omega
  have hb1 : ((S.b : ℚ)) ^ n ≠ 0 := S.b_pow_ne_zero _
  refine mul_right_cancel₀ hb1 ?_
  rw [← h, hpow]
  push_cast
  ring

/-- Tier-1 integrality in `∃ z : ℤ` form. -/
theorem production_int_onset' {k : ℕ} {P : Polynomial ℚ}
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.b : ℚ) ^ (3 * k + 1) * (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ n)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    ∃ z : ℤ, P.eval (n : ℚ) = (z : ℚ) :=
  ⟨(S.T n (n - k) * S.b ^ (3 * k + 1 - n) : ℕ), by
    rw [S.production_int_onset hP hn1 hn2]
    push_cast
    ring⟩

/-- **Integrality tier 2**: any `P` of degree `≤ k` satisfying the production
identity is integer-valued on all of `ℤ` — the `k+1` onset points
`n = 2k+1 .. 3k+1` are integer (tier 1) and consecutive, so finite differences
(`int_valued_of_consecutive`, a lattice-independent lemma of `Shape.lean`)
extend integrality everywhere. -/
theorem production_int_all {k : ℕ} {P : Polynomial ℚ} (hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.b : ℚ) ^ (3 * k + 1) * (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ n) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) := by
  refine int_valued_of_consecutive k P ((2 * k + 1 : ℕ) : ℤ) hdeg fun i hi => ?_
  obtain ⟨z, hz⟩ := S.production_int_onset' hP
    (show 2 * k + 1 ≤ 2 * k + 1 + i by omega) (show 2 * k + 1 + i ≤ 3 * k + 1 by omega)
  refine ⟨z, ?_⟩
  have hcast : ((((2 * k + 1 : ℕ) : ℤ) + (i : ℕ) : ℤ) : ℚ) = ((2 * k + 1 + i : ℕ) : ℚ) := by
    push_cast
    ring
  rw [hcast]
  exact hz

end PeelSystem

/-! ## Gate GD-1: the king lattice as a peeling system

The king case is a `PeelSystem` with `b = 3`, its two recursion fields
discharged by `Peel.lean`'s theorems verbatim. The `example`s below check that
the generic theorems instantiated at `kingSystem` are the *same statements*
`Shape.lean` proves directly (term-mode, no bridging tactic), which is the
GD-1 gate. The king tree itself is untouched. -/

/-- The king lattice (up-offsets `{-1, 0, 1}`, so `b = 3`) as a peeling
system: every field is a `Peel.lean`/`Weights.lean` object, and the two
recursion fields ARE `d_rec` and `c_ident`. -/
noncomputable def kingSystem : PeelSystem where
  b := 3
  hb := by norm_num
  d := Polyplets.d
  T := Polyplets.T
  V := Polyplets.V
  Vt := Polyplets.Vt
  d_rec := Polyplets.d_rec
  c_ident := Polyplets.c_ident

@[simp] lemma kingSystem_b : kingSystem.b = 3 := rfl

@[simp] lemma kingSystem_d : kingSystem.d = Polyplets.d := rfl

@[simp] lemma kingSystem_T : kingSystem.T = Polyplets.T := rfl

/-- `Shape.lean`'s `shape_d` statement, transcribed. Inhabited twice below. -/
def KingShapeD : Prop := ∀ k : ℕ, ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
  ∀ H : ℕ, k + 1 ≤ H → (Polyplets.d k H : ℚ) = δ.eval (H : ℚ) * 3 ^ H

/-- `Shape.lean`'s `shape` statement, transcribed. -/
def KingShape : Prop := ∀ k : ℕ, ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
  ∀ H : ℕ, k + 1 ≤ H → (Polyplets.T (H + k) H : ℚ) = q.eval (H : ℚ) * 3 ^ H

/-- `Shape.lean`'s `shape_production` statement, transcribed. -/
def KingShapeProduction : Prop := ∀ k : ℕ, ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
  (∀ n : ℕ, 2 * k + 1 ≤ n →
    (Polyplets.T n (n - k) : ℚ) = P.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
  (∀ n : ℕ, 2 * k + 1 ≤ n →
    (3 : ℚ) ^ (3 * k + 1) * (Polyplets.T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n)

/-- `Shape.lean`'s `production_int_all` statement, transcribed. -/
def KingProductionIntAll : Prop := ∀ (k : ℕ) (P : Polynomial ℚ), P.natDegree ≤ k →
  (∀ n : ℕ, 2 * k + 1 ≤ n →
    (3 : ℚ) ^ (3 * k + 1) * (Polyplets.T n (n - k) : ℚ) = P.eval (n : ℚ) * 3 ^ n) →
  ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ)

-- Each transcription is the ORIGINAL theorem's type: `Shape.lean`'s proofs
-- inhabit it term-mode, with no bridging tactic.
example : KingShapeD := Polyplets.shape_d
example : KingShape := Polyplets.shape
example : KingShapeProduction := Polyplets.shape_production
example : KingProductionIntAll := fun _ _ hdeg hP => Polyplets.production_int_all hdeg hP

-- **GD-1**: the generic theorems at `kingSystem` inhabit the very same types.
example : KingShapeD := kingSystem.shape_d
example : KingShape := kingSystem.shape
example : KingShapeProduction := kingSystem.shape_production
example : KingProductionIntAll := fun _ _ hdeg hP => kingSystem.production_int_all hdeg hP

/-! ## Axiom audit -/

#print axioms PeelSystem.shape_d
#print axioms PeelSystem.shape
#print axioms PeelSystem.shape_production
#print axioms PeelSystem.production_int_all
#print axioms kingSystem

end Polyplets.Universal
