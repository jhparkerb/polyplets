/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.RowLocal.DiagonalLaw
import Polyplets.RowLocal.TopRow

/-!
# The diagonal law for every row-local lattice

The geometric front (`RowLocal/{Defs, Graph, Finite,
Separation, RowProfile, Weights, Peel}.lean`) discharges every field of
`TopRowRecursion`, so the abstract shape engine of `RowLocal/DiagonalLaw.lean`
applies to **every** row-local lattice `L`. Composing the two halves gives
Theorem A of `docs/proofs/universal-diagonal-law.md` in Lean:

* `exists_delta` : `d L k H = δ_k(H) · b^H` for `H ≥ k + 1`;
* `exists_q` : `T L (H+k) H = q_k(H) · b^H` for `H ≥ k + 1`;
* `exists_isDiagonalPoly` : `T L (n, n-k) = P_k(n) · b^(n-1-3k)` for
  `n ≥ 2k+1` (`IsDiagonalPoly L k P_k`), with the zpow-free form
  `IsDiagonalPoly.cleared`;
* `IsDiagonalPoly.intValued` : the `P_k` are integer-valued on `ℤ`,

with `b = L.D.card` throughout. No hypothesis on `L` beyond `D` finite and
nonempty; in particular no primality, no symmetry of `D`, no bound on `|D|`.
-/

namespace Polyplets.RowLocal

open Polynomial

/-- **The top-row identities of a row-local lattice.** Every field is an object
of the generic geometric tree, and the two identity fields ARE `RowLocal/TopRow`'s
`d_rec` and `T_of_d`. -/
noncomputable def topRowRecursion (L : Lattice) : TopRowRecursion where
  b := L.b
  hb := L.one_le_b
  d := d L
  T := T L
  V := V L
  Vt := Vt L
  d_rec := d_rec L
  T_of_d := T_of_d L

@[simp] lemma topRowRecursion_b (L : Lattice) : (topRowRecursion L).b = L.b := rfl

@[simp] lemma topRowRecursion_d (L : Lattice) : (topRowRecursion L).d = d L := rfl

@[simp] lemma topRowRecursion_T (L : Lattice) : (topRowRecursion L).T = T L := rfl

@[simp] lemma topRowRecursion_V (L : Lattice) : (topRowRecursion L).V = V L := rfl

@[simp] lemma topRowRecursion_Vt (L : Lattice) : (topRowRecursion L).Vt = Vt L := rfl

/-! ## Theorem A -/

/-- **Shape of the walk-top diagonal, universally**: for every row-local lattice
and every surplus `k`, `d L k H = δ_k(H) · b^H` for all `H ≥ k + 1`, with
`δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem exists_delta (L : Lattice) (k : ℕ) :
    ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (d L k H : ℚ) = δ.eval (H : ℚ) * (L.b : ℚ) ^ H :=
  (topRowRecursion L).exists_delta k

/-- **The universal diagonal law (Theorem A)**: for every row-local lattice and
every `k` there is `q_k ∈ ℚ[X]` of degree `≤ k` with
`T(H+k, H) = q_k(H) · b^H` for all `H ≥ k + 1`, where `b = |D|`. -/
theorem exists_q (L : Lattice) (k : ℕ) :
    ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (T L (H + k) H : ℚ) = q.eval (H : ℚ) * (L.b : ℚ) ^ H :=
  (topRowRecursion L).exists_q k

/-- **`P` is the polynomial of the `k`-th diagonal of `L`**:
`T(n, n-k) = P(n) · b^(n-1-3k)` for all `n ≥ 2k+1`. The `3` in the exponent is
structural bookkeeping, not the king drift count. -/
def IsDiagonalPoly (L : Lattice) (k : ℕ) (P : Polynomial ℚ) : Prop :=
  ∀ n : ℕ, 2 * k + 1 ≤ n →
    (T L n (n - k) : ℚ) = P.eval (n : ℚ) * (L.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k)

/-- The predicate is the abstract one at `topRowRecursion L`, definitionally. -/
lemma isDiagonalPoly_topRowRecursion {L : Lattice} {k : ℕ} {P : Polynomial ℚ} :
    (topRowRecursion L).IsDiagonalPoly k P ↔ IsDiagonalPoly L k P := Iff.rfl

/-- **The diagonal law in the report's coordinates, universally**: for every
row-local lattice and every `k` there is a `P_k` of degree `≤ k` with
`T(n, n-k) = P_k(n) · b^(n-1-3k)` for `n ≥ 2k+1`. -/
theorem exists_isDiagonalPoly (L : Lattice) (k : ℕ) :
    ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧ IsDiagonalPoly L k P :=
  (topRowRecursion L).exists_isDiagonalPoly k

/-- The zpow-free form: `b^(3k+1) · T(n, n-k) = P(n) · b^n`. -/
theorem IsDiagonalPoly.cleared {L : Lattice} {k : ℕ} {P : Polynomial ℚ}
    (hP : IsDiagonalPoly L k P) :
    ∀ n : ℕ, 2 * k + 1 ≤ n →
      (L.b : ℚ) ^ (3 * k + 1) * (T L n (n - k) : ℚ) = P.eval (n : ℚ) * (L.b : ℚ) ^ n :=
  TopRowRecursion.IsDiagonalPoly.cleared (isDiagonalPoly_topRowRecursion.mpr hP)

/-- **The values on the onset window are counts**: for `2k+1 ≤ n ≤ 3k+1`,
`P(n) = T(n, n-k) · b^(3k+1-n)`. -/
theorem IsDiagonalPoly.eval_onset {L : Lattice} {k : ℕ} {P : Polynomial ℚ}
    (hP : IsDiagonalPoly L k P) {n : ℕ} (hn1 : 2 * k + 1 ≤ n) (hn2 : n ≤ 3 * k + 1) :
    P.eval (n : ℚ) = ((T L n (n - k) * L.b ^ (3 * k + 1 - n) : ℕ) : ℚ) :=
  TopRowRecursion.IsDiagonalPoly.eval_onset (isDiagonalPoly_topRowRecursion.mpr hP) hn1 hn2

/-- **Integrality, universally**: any `P` of degree `≤ k` satisfying the law
for `L` is integer-valued on all of `ℤ`. -/
theorem IsDiagonalPoly.intValued {L : Lattice} {k : ℕ} {P : Polynomial ℚ}
    (hdeg : P.natDegree ≤ k) (hP : IsDiagonalPoly L k P) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) :=
  TopRowRecursion.IsDiagonalPoly.intValued hdeg (isDiagonalPoly_topRowRecursion.mpr hP)

end Polyplets.RowLocal
