/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Basic
import Polyplets.GapWalkExact

/-!
# Notary piece K, module 5: the column series and the master identities

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`, wave K-β. The
gap walk's per-gap generating series, in the `y`-variable
(`X = y`; the `s`-variable `y = s²` enters later via `expand 2`):

* `jY F g` — `Σ_m jE F m g · y^m`, the joined column at gap `g`;
* `pY F g` — the pending column;
* `JmY F` — `Σ_m (Σ_{3 ≤ g ≤ 2m+2} jE F m g) · y^m`, the deep-`J` mass
  (finite per order by `J`-support).

The payload is the **two master identities of `docs/notary-k-plan.md` §2,
per `u`-column**: each column of `D·J₃ = u²·Q` and of
`D·(P₃ − 2J₃) = u²·(P0 − p₂u² − 2J₃ + y·R_P)` is one series identity among
the columns — the exceptional columns `u³..u⁶` as literal identities, the
generic columns as one `k`-indexed family each. (Column `u³` of the P-side
is a tautology — `R_P`'s `u¹`-entry is defined to make it one — and is not
stated.) In this per-column form the identities are exactly the step
recurrence of `GapWalkExact.lean` with the closed-form rows of
`GapWalkRowVals.lean` substituted; the closing module (wave K-γ) multiplies
column `g` by `uᵢ^g` and `lfsum`s the family to evaluate at the kernel
roots.

Every statement was verified numerically before this skeleton was written:
`experiments/notary_kbeta_statements.py` b5
(`build/notary_kbeta_statements.log`), coefficient-wise to `y`-order 14,
generic index `k ≤ 19`, both starts.

## Proof recipe

Each identity is `PowerSeries.ext`; `coeff_mk` reads off both sides.
Coefficient `0`: the start data (`jE_zero`/`pE_zero` + the `StartData`
fields; `Polyplets.GapWalk.coeff` facts: `coeff (m+1) (X * S) = coeff m S`
is `PowerSeries.coeff_succ_X_mul`, `coeff 0 (X * S) = 0`, `coeff_C`).
Coefficient `m+1`: the step recurrence (`jE_step`/`pE_step`) with the row
values of `GapWalkRowVals.lean` substituted, then `Finset` bookkeeping:

* split the `J`-source window `Icc 1 (2m+2)` into `{1}`, `{2}`, and
  `Icc 3 (2m+2)`;
* on `Icc 3 (2m+2)` the row value is a constant background plus a `bulkW`
  correction supported on `[gp−2, gp+2]`: pull the background out (it
  multiplies `coeff m (JmY F)`), and evaluate the correction as at most
  five explicit terms — terms outside `Icc 3 (2m+2)` are added/removed by
  `Finset.sum_subset` and die by `jE_support`;
* the `P`-source windows are at most five explicit terms plus, on `P`
  targets, the constant-tail sources `g = 2` (`stepMul_2P_tail` etc.) —
  and `pE F m 1 = 0` (`pE_one`) kills the gap-1 source. On the generic
  columns the `P`-window `Icc 1 (gp+2)` splits into `{1}`, `{2}`,
  `Icc 3 (gp−3)` (all-zero by `stepMul_P_local`), and `Icc (gp−2) (gp+2)`
  (the `bulkW` window);
* `Nat.cast` pushes through everything (`Nat.cast_sum`, `push_cast`).

The generic-column proofs (`jY_col_generic`, `pY_col_generic`) subsume the
boundary ones in shape; prove them first and let the boundary proofs reuse
the same sum surgery with the boundary heads of `GapWalkRowVals.lean`.

Do not change any statement below; if one resists proof, leave it sorried
and report back.
-/

namespace Polyplets
namespace GapWalk

open PowerSeries

/-! ## The column series -/

/-- The joined column at gap `g`: `Σ_m jE F m g · y^m`. -/
noncomputable def jY (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  mk fun m => (jE F m g : ℚ)

/-- The pending column at gap `g`: `Σ_m pE F m g · y^m`. -/
noncomputable def pY (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  mk fun m => (pE F m g : ℚ)

/-- The deep-`J` mass `Jm`: per order, the (finite, by `J`-support) sum of
the joined row from gap 3 up. -/
noncomputable def JmY (F : St → Nat) : PowerSeries ℚ :=
  mk fun m => ∑ g ∈ Finset.Icc 3 (2 * m + 2), (jE F m g : ℚ)

@[simp] theorem coeff_jY (F : St → Nat) (g m : Nat) :
    coeff m (jY F g) = (jE F m g : ℚ) := coeff_mk m _

@[simp] theorem coeff_pY (F : St → Nat) (g m : Nat) :
    coeff m (pY F g) = (pE F m g : ℚ) := coeff_mk m _

@[simp] theorem coeff_JmY (F : St → Nat) (m : Nat) :
    coeff m (JmY F) = ∑ g ∈ Finset.Icc 3 (2 * m + 2), (jE F m g : ℚ) :=
  coeff_mk m _

/-- `J`-support, in column form: column `g` vanishes below order
`(g − 2)/2`. -/
theorem coeff_jY_support (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) {m g : Nat} (h : 2 * m + 2 < g) :
    coeff m (jY F g) = 0 := by
  sorry

/-- Nothing is ever pending at gap 1. -/
theorem pY_one (F : St → Nat) (h1 : F (1, false) = 0) : pY F 1 = 0 := by
  sorry

/-! ## The `J`-master identity, per column

Columns `u³, u⁴, u⁵, u⁶` and the generic family `u^{k+7}`. In each, the
left side is the column at the *previous* gap (`u²·Q` shifts by two) and
the right side is `y` times the kernel window plus the `R_J` column. -/

/-- Column `u³`: the `j₁` equation. -/
theorem jY_col_one {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 1 = C (j01 : ℚ) +
      X * (5 * jY F 1 + 6 * jY F 2 + 8 * JmY F - jY F 3 +
        2 * pY F 2 + pY F 3) := by
  sorry

/-- Column `u⁴`: the `j₂` equation. -/
theorem jY_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 2 = C (j02 : ℚ) +
      X * (2 * jY F 1 + 3 * jY F 2 + 2 * JmY F + 2 * jY F 3 +
        jY F 4 + 2 * pY F 2) := by
  sorry

/-- Column `u⁵`: the first interior column, fed by the heads. -/
theorem jY_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 3 = X * (jY F 1 + 2 * jY F 2 + 3 * jY F 3 + 2 * jY F 4 +
      jY F 5) := by
  sorry

/-- Column `u⁶`: the second interior column. -/
theorem jY_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 4 = X * (jY F 2 + 2 * jY F 3 + 3 * jY F 4 + 2 * jY F 5 +
      jY F 6) := by
  sorry

/-- Generic column `u^{k+7}`: the pure bulk recurrence. -/
theorem jY_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    jY F (k + 5) = X * (jY F (k + 7) + 2 * jY F (k + 6) +
      3 * jY F (k + 5) + 2 * jY F (k + 4) + jY F (k + 3)) := by
  sorry

/-! ## The `P`-master identity, per column

Stated on the combination the kernel clears: `f_g := pY g − 2·jY g` in the
window, with the deep-`J` sprays and the boundary tails as coefficients on
`JmY`, `jY 1`, `jY 2`, `pY 2`. Column `u³` is the `R_P`-defining tautology
and is omitted. -/

/-- Column `u⁴`: the `p₂` equation. -/
theorem pY_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pY F 2 = C (p02 : ℚ) +
      X * ((pY F 4 - 2 * jY F 4) + 2 * (pY F 3 - 2 * jY F 3) +
        8 * JmY F + 4 * jY F 1 + 4 * jY F 2 + pY F 2) := by
  sorry

/-- Column `u⁵`: the `p₃` equation. -/
theorem pY_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pY F 3 = C (pt : ℚ) +
      X * ((pY F 5 - 2 * jY F 5) + 2 * (pY F 4 - 2 * jY F 4) +
        3 * (pY F 3 - 2 * jY F 3) + 12 * JmY F + 6 * jY F 1 +
        6 * jY F 2 + 4 * pY F 2) := by
  sorry

/-- Column `u⁶`. -/
theorem pY_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pY F 4 = C (pt : ℚ) +
      X * ((pY F 6 - 2 * jY F 6) + 2 * (pY F 5 - 2 * jY F 5) +
        3 * (pY F 4 - 2 * jY F 4) + 2 * (pY F 3 - 2 * jY F 3) +
        12 * JmY F + 8 * jY F 1 + 8 * jY F 2 + 3 * pY F 2) := by
  sorry

/-- Generic column `u^{k+7}`: bulk window on `f = pY − 2·jY`, deep sprays,
boundary tails. -/
theorem pY_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    pY F (k + 5) = C (pt : ℚ) +
      X * ((pY F (k + 7) - 2 * jY F (k + 7)) +
        2 * (pY F (k + 6) - 2 * jY F (k + 6)) +
        3 * (pY F (k + 5) - 2 * jY F (k + 5)) +
        2 * (pY F (k + 4) - 2 * jY F (k + 4)) +
        (pY F (k + 3) - 2 * jY F (k + 3)) +
        12 * JmY F + 8 * jY F 1 + 10 * jY F 2 + 2 * pY F 2) := by
  sorry

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.jY_col_generic' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms jY_col_generic

/--
info: 'Polyplets.GapWalk.pY_col_generic' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms pY_col_generic

end GapWalk
end Polyplets
