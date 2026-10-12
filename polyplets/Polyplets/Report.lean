/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.Tactic.Choose
import Mathlib.Tactic.Ring
import Polyplets.Grand.PinAll
import Polyplets.LeadingCoeff
import Polyplets.Symmetry
import Polyplets.SymmetryRatio
import Polyplets.Growth

/-!
# The technical report's claims, as Lean statements

One entry per claim in `paper/technical-report.tex`, in the report's order,
each stated as close to the report's sentence as Lean allows and proved by a
short reference into the rest of the tree. The definitions it rests on are
`T` (`Defs.lean`) and `a` (`Sequence.lean`).

A claim Lean does not yet prove is stated as a `Prop` definition, not a
theorem: it type-checks, so the statement is fixed, but nothing asserts it.

Out of scope: the computed tables (a(n), T(n,H) beyond small rows, the
symmetry-class and hole counts). Those are enumeration output, not theorems.
-/

namespace Polyplets

open Polynomial

/-! ## Definitions section -/

/-- **The row sums of `T(n,H)` produce `a(n)`.** -/
theorem report_a_eq_sum (n : ℕ) : a n = ∑ H ∈ Finset.Icc 1 n, T n H :=
  a_eq_sum n

/-! ## Results: fixed polyplets by height -/

/-- **`T(n,n) = 3^(n-1)`.** -/
theorem report_T_diag (n : ℕ) (hn : 1 ≤ n) : T n n = 3 ^ (n - 1) := by
  have h := T_self n hn
  rw [show (n : ℤ) - 1 = ((n - 1 : ℕ) : ℤ) by omega, zpow_natCast] at h
  exact_mod_cast h

/-- **The diagonal law.** When `H > n/2`, `T(n,H) = P_{n-H}(n)·3^(3H-2n-1)`,
where `P_k` has degree at most `k` and is integer-valued. -/
theorem report_diagonal_law : ∃ P : ℕ → Polynomial ℚ, ∀ k : ℕ,
    (P k).natDegree ≤ k ∧
    (∀ m : ℤ, ∃ z : ℤ, (P k).eval (m : ℚ) = z) ∧
    ∀ n H : ℕ, H ≤ n → n < 2 * H →
      n - H = k → (T n H : ℚ) = (P k).eval (n : ℚ) * 3 ^ (3 * (H : ℤ) - 2 * n - 1) := by
  choose P hdeg hz using exists_isDiagonalPoly
  refine ⟨P, fun k => ⟨hdeg k, (hz k).intValued (hdeg k), ?_⟩⟩
  intro n H hHn hlt hk
  subst hk
  have h := hz (n - H) n (by omega)
  rw [show n - (n - H) = H by omega] at h
  rw [h]
  congr 2
  push_cast [Nat.cast_sub hHn]
  ring

/-- **The leading coefficient of `P_k` is exactly `25^k/k!`.** For any
polynomial satisfying the diagonal law at level `k` (`IsDiagonalPoly k P`:
`T(n, n-k) = P(n)·3^(n-1-3k)` for `n ≥ 2k+1`), not only the witness
`report_diagonal_law` picks. -/
theorem report_leading_coeff (k : ℕ) (P : Polynomial ℚ) (hdeg : P.natDegree ≤ k)
    (hP : IsDiagonalPoly k P) : P.coeff k = 25 ^ k / k.factorial :=
  hP.coeff_eq hdeg

/-- **`P_k` can be fixed after computing the `3k`-th row.** A polynomial of
degree `≤ k` with the known leading coefficient that matches `T` on rows
`2k+1 … 3k` satisfies the diagonal law at level `k`. -/
theorem report_pin_row_3k (k : ℕ) (p : Polynomial ℚ) (hp : p.natDegree ≤ k)
    (hlc : p.coeff k = 25 ^ k / k.factorial)
    (hpts : ∀ n ∈ Finset.Icc (2 * k + 1) (3 * k),
      p.eval (n : ℚ) = ((T n (n - k) * 3 ^ (3 * k + 1 - n) : ℕ) : ℚ)) :
    IsDiagonalPoly k p :=
  isDiagonalPoly_of_coeff_of_eval_Icc k p hp hlc hpts

/-- **The worked example in Methods**: `T(n, n-1) = (25n - 45)·3^(n-4)`. -/
theorem report_T_n_nm1 (n : ℕ) (hn : 3 ≤ n) :
    (T n (n - 1) : ℚ) = (25 * (n : ℚ) - 45) * (3 : ℚ) ^ ((n : ℤ) - 4) :=
  T_sub_one n hn

/-- **`P_k` is explicitly known for `k ≤ 18`**, given the 36 enumerated
anchor cells, two per level (`BankedAnchors`: `anchorA`, `anchorB` in
`Grand/PinAll.lean`).
`Pk k` is the polynomial of `Pin.lean`. -/
theorem report_Pk_known (hA : BankedAnchors) (k : ℕ) (hk : k ≤ 18) :
    IsDiagonalPoly k (Pk k) :=
  Pk_prod hA k hk

/-! ## Results: non-fixed polyplets

The report gives counts only. Lean has the Burnside identities the counts are
computed through; `Free`, `OneSided`, `Bilateral` are `Symmetry.lean`'s orbit
counts. The report defines asymmetric as free minus bilateral, so
`#bilateral + #asymmetric = #free` is definitional and gets no entry. -/

theorem report_free (n : ℕ) :
    8 * Free n = a n + 2 * R90 n + R180 n + 2 * Hm n + 2 * Dm n := free_eq n

theorem report_oneSided (n : ℕ) : 4 * OneSided n = a n + 2 * R90 n + R180 n :=
  oneSided_eq n

theorem report_bilateral (n : ℕ) : 2 * Bilateral n = Hm n + Dm n := bilateral_eq n

/-- **One-sided approaches `a(n)/4` and free approaches `a(n)/8`.** -/
def SymmetryRatioClaim : Prop :=
  Filter.Tendsto (fun n => 4 * (OneSided n : ℝ) / a n) Filter.atTop (nhds 1) ∧
  Filter.Tendsto (fun n => 8 * (Free n : ℝ) / a n) Filter.atTop (nhds 1)

/-- The symmetric counts are `o(a n)` (`SymmetryRatio.lean`: every symmetric
animal is recovered from a connected half of about `n / 2` cells), so the
Burnside identities give the limits. -/
theorem report_symmetryRatio : SymmetryRatioClaim := symmetryRatio

/-! ## Results: growth rate -/

/-- **`a(n)^{1/n} → λ`.** The value `λ ≈ 7.11` is read off the table, not proved. -/
theorem report_growth :
    Filter.Tendsto (fun n => (a n : ℝ) ^ ((n : ℝ)⁻¹)) Filter.atTop (nhds lambda) :=
  lambda_tendsto

end Polyplets
