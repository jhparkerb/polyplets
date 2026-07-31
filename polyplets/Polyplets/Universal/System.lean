/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Universal.AbstractShape
import Polyplets.Universal.Peel

/-!
# A peeling system for every row-local lattice

Phase B's deliverable: the geometric front (`Universal/{Defs, Graph, Finite,
Separation, RowProfile, Weights, Peel}.lean`) discharges every field of
`PeelSystem`, so the abstract shape engine of `Universal/AbstractShape.lean`
applies to **every** row-local lattice `L`. Composing the two halves gives
Theorem A of `docs/proofs/universal-diagonal-law.md` in Lean:

* `universal_shape_d` : `d L k H = δ_k(H) · b^H` for `H ≥ k + 1`;
* `universal_shape` : `T L (H+k) H = q_k(H) · b^H` for `H ≥ k + 1`;
* `universal_shape_production` : `T L (n, n-k) = P_k(n) · b^(n-1-3k)` for
  `n ≥ 2k+1`, plus the zpow-free companion;
* `universal_production_int_all` : the `P_k` are integer-valued on `ℤ`,

with `b = L.D.card` throughout. No hypothesis on `L` beyond `D` finite and
nonempty; in particular no primality, no symmetry of `D`, no bound on `|D|`.
-/

namespace Polyplets.Universal

open Polynomial

/-- **The peeling system of a row-local lattice.** Every field is an object of
the generic geometric tree, and the two recursion fields ARE `Universal/Peel`'s
`d_rec` and `c_ident`. -/
noncomputable def peelSystem (L : RowLocal) : PeelSystem where
  b := L.b
  hb := L.one_le_b
  d := d L
  T := T L
  V := V L
  Vt := Vt L
  d_rec := d_rec L
  c_ident := c_ident L

@[simp] lemma peelSystem_b (L : RowLocal) : (peelSystem L).b = L.b := rfl

@[simp] lemma peelSystem_d (L : RowLocal) : (peelSystem L).d = d L := rfl

@[simp] lemma peelSystem_T (L : RowLocal) : (peelSystem L).T = T L := rfl

@[simp] lemma peelSystem_V (L : RowLocal) : (peelSystem L).V = V L := rfl

@[simp] lemma peelSystem_Vt (L : RowLocal) : (peelSystem L).Vt = Vt L := rfl

/-! ## Theorem A -/

/-- **Shape of the walk-top diagonal, universally**: for every row-local lattice
and every surplus `k`, `d L k H = δ_k(H) · b^H` for all `H ≥ k + 1`, with
`δ_k ∈ ℚ[X]` of degree `≤ k`. -/
theorem universal_shape_d (L : RowLocal) (k : ℕ) :
    ∃ δ : Polynomial ℚ, δ.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (d L k H : ℚ) = δ.eval (H : ℚ) * (L.b : ℚ) ^ H :=
  (peelSystem L).shape_d k

/-- **The universal diagonal law (Theorem A)**: for every row-local lattice and
every `k` there is `q_k ∈ ℚ[X]` of degree `≤ k` with
`T(H+k, H) = q_k(H) · b^H` for all `H ≥ k + 1`, where `b = |D|`. -/
theorem universal_shape (L : RowLocal) (k : ℕ) :
    ∃ q : Polynomial ℚ, q.natDegree ≤ k ∧
      ∀ H : ℕ, k + 1 ≤ H → (T L (H + k) H : ℚ) = q.eval (H : ℚ) * (L.b : ℚ) ^ H :=
  (peelSystem L).shape k

/-- **Production form, universally**: `T(n, n-k) = P_k(n) · b^(n-1-3k)` for
`n ≥ 2k+1`, plus the zpow-free companion. The `3` in the exponent is structural
bookkeeping, not the king drift count. -/
theorem universal_shape_production (L : RowLocal) (k : ℕ) :
    ∃ P : Polynomial ℚ, P.natDegree ≤ k ∧
      (∀ n : ℕ, 2 * k + 1 ≤ n →
        (T L n (n - k) : ℚ) = P.eval (n : ℚ) * (L.b : ℚ) ^ ((n : ℤ) - 1 - 3 * k)) ∧
      (∀ n : ℕ, 2 * k + 1 ≤ n →
        (L.b : ℚ) ^ (3 * k + 1) * (T L n (n - k) : ℚ)
          = P.eval (n : ℚ) * (L.b : ℚ) ^ n) :=
  (peelSystem L).shape_production k

/-- **Integrality, universally**: any `P` of degree `≤ k` satisfying the
production identity for `L` is integer-valued on all of `ℤ`. -/
theorem universal_production_int_all (L : RowLocal) {k : ℕ} {P : Polynomial ℚ}
    (hdeg : P.natDegree ≤ k)
    (hP : ∀ n : ℕ, 2 * k + 1 ≤ n →
      (L.b : ℚ) ^ (3 * k + 1) * (T L n (n - k) : ℚ) = P.eval (n : ℚ) * (L.b : ℚ) ^ n) :
    ∀ m : ℤ, ∃ z : ℤ, P.eval (m : ℚ) = (z : ℚ) :=
  (peelSystem L).production_int_all hdeg hP

/-! ## Axiom audit -/

#print axioms peelSystem
#print axioms universal_shape_d
#print axioms universal_shape
#print axioms universal_shape_production
#print axioms universal_production_int_all

end Polyplets.Universal
