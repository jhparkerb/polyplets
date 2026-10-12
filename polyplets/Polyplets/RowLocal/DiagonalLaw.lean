/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.Choose
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Set
import Polyplets.DiscreteCalculus

/-!
# DiagonalLaw: the diagonal law from the two top-row identities

The diagonal law needs only a thin interface to the geometry: the two
identities about the top row (`d_rec`, `T_of_d`) and nothing else. This file
states that interface as a structure `TopRowRecursion` carrying a drift count `b : ℕ` (the
king lattice's `3`) and proves the four diagonal-law theorems from it:

* `TopRowRecursion.exists_delta` : `d k H = δ_k(H) · b^H` for `H ≥ k + 1`, `deg δ_k ≤ k`;
* `TopRowRecursion.exists_q` : `T(H+k, H) = q_k(H) · b^H` for `H ≥ k + 1`;
* `TopRowRecursion.exists_isDiagonalPoly` : `T(n, n-k) = P_k(n) · b^(n-1-3k)` for
  `n ≥ 2k+1` (`IsDiagonalPoly`; `zpow`, so the onset window `2k+1 ≤ n < 3k+1`
  is covered), with the zpow-free form `b^(3k+1) · T(n, n-k) = P_k(n) · b^n`
  as `IsDiagonalPoly.cleared`;
* `TopRowRecursion.IsDiagonalPoly.intValued` : any such `P_k` is integer-valued on `ℤ`
  (and, `IsDiagonalPoly.natDegree_le`, of degree `≤ k`: the law determines `P_k`).

The only arithmetic fact about `b` the proofs use is `(b : ℚ) ≠ 0`
(`TopRowRecursion.b_ne_zero`, from the field `hb : 1 ≤ b`), which is why the
"verbatim wager" of `docs/proofs/universal-diagonal-law.md` holds: steps 3–5
of that proof carry over with `b` in place of `3`. The geometric half (steps
1–2, a `TopRowRecursion` from any row-local lattice) is `RowLocal/Instance.lean`;
the king instance with its original names is `King.lean`.

## What the diagonal law needs from a lattice

Exactly the eight fields of `TopRowRecursion` — most of them data. The proofs use
NO base values, NO support or vanishing ranges for `V`/`Vt`, and NO
arithmetic property of `b` beyond `b ≠ 0`:

* the drift count `b` with `1 ≤ b` (the recursion's homogeneous coefficient;
  `1 ≤ b` is used only as `(b : ℚ) ≠ 0`, to divide by powers of `b`);
* the four numeric families `d`, `T`, `V`, `Vt` (opaque);
* the recursion `d_rec` and the top-row identity `T_of_d`.

Notably the ranges `Finset.Icc 1 k` / `Finset.Icc 1 j` in the two recursions
carry all the support information the induction needs: `ℓ ≤ j ≤ k` is what puts
every recursive `d (k-j) (H-1-ℓ)` above its own onset, by `omega`.

## Integrality: no p-adic argument needed

Step 5 of the paper proof argues integrality of `P_k` p-adically, prime by
prime over `p ∣ b`, which for the king case is `p = 3` — the one place where
primality of `3` could plausibly have been used. The Lean route never needs it:
`IsDiagonalPoly.eval_onset` reads `P_k(n)` off the zpow-free identity as
the *natural number* `T(n,n-k) · b^(3k+1-n)` on the onset window
`2k+1 ≤ n ≤ 3k+1` (exact division by `b^n`, valid for any `b ≠ 0`), and
`IsDiagonalPoly.intValued` extends by finite differences over the `k+1` consecutive
onset points. Both are prime-agnostic; `b` is never factored.
-/

namespace Polyplets.RowLocal

open Polynomial

/-! ## The interface -/

/-- **The two top-row identities**: the finite numeric interface that the
diagonal-law algebra consumes. `b` is the drift count (`3` for the king lattice, `|D|` in
general); `d k H` counts walk-top animals of surplus `k` and height `H`;
`T n H` counts all animals; `V`/`Vt` are the interior and top-edge
cluster weights. The two recursions are `RowLocal/TopRow.lean`'s `d_rec` and `T_of_d`
verbatim with `3 ↦ b`. -/
structure TopRowRecursion where
  /-- The drift count: the number of up-offsets of the lattice. -/
  b : ℕ
  /-- The drift count is positive (the up-offset set is nonempty). Used only
  through `(b : ℚ) ≠ 0`. -/
  hb : 1 ≤ b
  /-- `d k H`: walk-top animals of surplus `k` and height `H`. -/
  d : ℕ → ℕ → ℕ
  /-- `T n H`: all animals with `n` cells and height `H`. -/
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
  /-- **The top-row identity**: an animal has a walk top row or a top-edge
  cluster capping a shorter walk-top remainder. -/
  T_of_d : ∀ k H : ℕ, k + 1 ≤ H →
    T (H + k) H = d k H +
      ∑ j ∈ Finset.Icc 1 k, ∑ ℓ ∈ Finset.Icc 1 j, Vt ℓ j * d (k - j) (H - ℓ)

namespace TopRowRecursion

variable (S : TopRowRecursion)

/-- The drift count is invertible in `ℚ` — the only arithmetic fact about `b`
the diagonal law uses. -/
lemma b_ne_zero : (S.b : ℚ) ≠ 0 := by
  have := S.hb
  positivity

/-- Powers of the drift count are invertible in `ℚ`. -/
lemma b_pow_ne_zero (m : ℕ) : (S.b : ℚ) ^ m ≠ 0 := pow_ne_zero _ S.b_ne_zero

/-! ## The walk-top counts are polynomial times `b^H` -/

/-- The strong-induction step for `shape_d`: lower-surplus polynomials give the
surplus-`k` one. The
d-recursion divided by `b^H` is the difference equation `e(H) = e(H-1) + g(H)`;
telescoping from `H₀ = k+1` and summing `g` by `exists_poly_sum_Icc` gives
`δ_k`, with the base value absorbed into the constant term. -/
lemma exists_delta_step (k : ℕ)
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

/-- **The walk-top diagonal**: `d k H = δ_k(H) · b^H` for all
`H ≥ k + 1`, with `δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem exists_delta : ∀ k : ℕ, ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (S.d k H : ℚ) = δ.eval (H : ℚ) * (S.b : ℚ) ^ H := fun k =>
  Nat.strong_induction_on k S.exists_delta_step

/-- **The k-th diagonal**: `T(H+k, H) = q_k(H) · b^H` for all
`H ≥ k + 1`, with `q_k ∈ ℚ[X]` of degree `≤ k`. From `shape_d` through the
top-row identity: at `H ≥ k + 1` every `d`-term of `T_of_d` is exactly in range. -/
theorem exists_q (k : ℕ) : ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
    ∀ H : ℕ, k + 1 ≤ H → (S.T (H + k) H : ℚ) = q.eval (H : ℚ) * (S.b : ℚ) ^ H := by
  classical
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  choose δ hδdeg hδval using S.exists_delta
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
      exact_mod_cast S.T_of_d k H (by omega)
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

/-! ## The diagonal law in the report's coordinates -/

/-- **`P` is the polynomial of the `k`-th diagonal**: `T(n, n-k) = P(n) · b^(n-1-3k)`
for all `n ≥ 2k + 1`. The exponent is an integer (`zpow`), negative on the
onset window `2k+1 ≤ n < 3k+1`, where `P(n)` carries the compensating powers
of `b`. The `3` in `n - 1 - 3k` is structural bookkeeping (`k` from
`H = n - k` plus `2k + 1` from the normalization), NOT the king drift count:
it survives the generalization unchanged. -/
def IsDiagonalPoly (k : ℕ) (P : Polynomial ℚ) : Prop :=
  ∀ n : ℕ, 2 * k + 1 ≤ n →
    (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k)

/-- **The diagonal law**: for every `k` there is a `P_k ∈ ℚ[X]` of degree `≤ k`
with `T(n, n-k) = P_k(n) · b^(n-1-3k)` for all `n ≥ 2k + 1`; it is
`P_k(n) = b^(2k+1) · q_k(n - k)` for the `q_k` of `exists_q`. -/
theorem exists_isDiagonalPoly (k : ℕ) : ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
    S.IsDiagonalPoly k P := by
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  obtain ⟨q, hqdeg, hq⟩ := S.exists_q k
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
  refine ⟨P, ?_, ?_⟩
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

variable {S}

/-- The zpow-free form of the law: `b^(3k+1) · T(n, n-k) = P(n) · b^n`. -/
theorem IsDiagonalPoly.cleared {k : ℕ} {P : Polynomial ℚ} (hP : S.IsDiagonalPoly k P) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (S.b : ℚ) ^ (3 * k + 1) * (S.T n (n - k) : ℚ) = P.eval (n : ℚ) * (S.b : ℚ) ^ n := by
  intro n hn
  have hbne : (S.b : ℚ) ≠ 0 := S.b_ne_zero
  have hpow : (S.b : ℚ) ^ (3 * k + 1) * (S.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k) = (S.b : ℚ) ^ n := by
    rw [← zpow_natCast (S.b : ℚ) (3 * k + 1), ← zpow_add₀ hbne, ← zpow_natCast (S.b : ℚ) n]
    congr 1
    push_cast
    ring
  rw [hP n hn]
  linear_combination P.eval (n : ℚ) * hpow

/-! ## Uniqueness, and the degree bound for free -/

/-- **Uniqueness**: two polynomials satisfying the law at level `k` agree at
every `n ≥ 2k+1`, hence everywhere. -/
theorem IsDiagonalPoly.eq {k : ℕ} {P Q : Polynomial ℚ} (hP : S.IsDiagonalPoly k P)
    (hQ : S.IsDiagonalPoly k Q) : P = Q := by
  refine eq_of_infinite_eval_eq P Q ?_
  refine Set.infinite_of_injective_forall_mem
    (f := fun i : ℕ => ((2 * k + 1 + i : ℕ) : ℚ)) ?_ fun i => ?_
  · intro i j hij
    dsimp only at hij
    have : 2 * k + 1 + i = 2 * k + 1 + j := by exact_mod_cast hij
    omega
  · exact mul_right_cancel₀ (zpow_ne_zero _ S.b_ne_zero)
      ((hP _ (by omega)).symm.trans (hQ _ (by omega)))

/-- **The degree bound is automatic**: any polynomial satisfying the law at
level `k` is the witness of `exists_isDiagonalPoly`, so its degree is `≤ k`. -/
theorem IsDiagonalPoly.natDegree_le {k : ℕ} {P : Polynomial ℚ} (hP : S.IsDiagonalPoly k P) :
    P.natDegree ≤ k := by
  obtain ⟨Q, hQdeg, hQ⟩ := S.exists_isDiagonalPoly k
  rw [hP.eq hQ]
  exact hQdeg

/-! ## Integrality -/

/-- **Integrality at the onset window**: for `2k+1 ≤ n ≤ 3k+1` the
value `P_k(n)` is the natural number `T(n, n-k) · b^(3k+1-n)`. These are
exactly the `k+1` onset points `H = k+1 .. 2k+1` (`n = H+k`). Stated for any
`P` satisfying the law.

This is the step the paper proof runs p-adically over the primes dividing `b`;
here it is exact division by `b^n` and uses no factorization of `b`. -/
theorem IsDiagonalPoly.eval_onset {k : ℕ} {P : Polynomial ℚ} (hP : S.IsDiagonalPoly k P)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((S.T n (n - k) * S.b ^ (3 * k + 1 - n) : ℕ) : ℚ) := by
  have h := hP.cleared n hn1
  have hpow : (S.b : ℚ) ^ (3 * k + 1) = (S.b : ℚ) ^ (3 * k + 1 - n) * (S.b : ℚ) ^ n := by
    rw [← pow_add]
    congr 1
    omega
  have hb1 : ((S.b : ℚ)) ^ n ≠ 0 := S.b_pow_ne_zero _
  refine mul_right_cancel₀ hb1 ?_
  rw [← h, hpow]
  push_cast
  ring

/-- Integrality at the onset window, in `∃ z : ℤ` form. -/
theorem IsDiagonalPoly.eval_onset_int {k : ℕ} {P : Polynomial ℚ} (hP : S.IsDiagonalPoly k P)
    {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    ∃ z : ℤ, P.eval (n : ℚ) = (z : ℚ) :=
  ⟨(S.T n (n - k) * S.b ^ (3 * k + 1 - n) : ℕ), by
    rw [hP.eval_onset hn1 hn2]
    push_cast
    ring⟩

/-- **Integrality everywhere**: any `P` satisfying the law is integer-valued on
all of `ℤ` — the `k+1` onset points `n = 2k+1 .. 3k+1` are integer
(`IsDiagonalPoly.eval_onset`) and consecutive, so finite differences
(`int_valued_of_consecutive`, `DiscreteCalculus.lean`) extend integrality
everywhere, the degree being `≤ k` (`IsDiagonalPoly.natDegree_le`). -/
theorem IsDiagonalPoly.intValued {k : ℕ} {P : Polynomial ℚ} (hP : S.IsDiagonalPoly k P) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) := by
  refine int_valued_of_consecutive k P ((2 * k + 1 : ℕ) : ℤ) hP.natDegree_le fun i hi => ?_
  obtain ⟨z, hz⟩ := hP.eval_onset_int
    (show 2 * k + 1 ≤ 2 * k + 1 + i by omega) (show 2 * k + 1 + i ≤ 3 * k + 1 by omega)
  refine ⟨z, ?_⟩
  have hcast : ((((2 * k + 1 : ℕ) : ℤ) + (i : ℕ) : ℤ) : ℚ) = ((2 * k + 1 + i : ℕ) : ℚ) := by
    push_cast
    ring
  rw [hcast]
  exact hz

end TopRowRecursion

end Polyplets.RowLocal
