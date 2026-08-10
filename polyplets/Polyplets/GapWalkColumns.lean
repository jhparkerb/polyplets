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
  rw [coeff_jY, jE_support F hF m g h, Nat.cast_zero]

/-- Nothing is ever pending at gap 1. -/
theorem pY_one (F : St → Nat) (h1 : F (1, false) = 0) : pY F 1 = 0 := by
  ext m
  rw [coeff_pY, pE_one F h1 m, Nat.cast_zero, map_zero]

/-! ## Finset surgery helpers -/

/-- Two finsets agreeing that `f` vanishes off each other have equal sums. -/
lemma sum_eq_of_zero_outside {M : Type*} [AddCommMonoid M] (f : Nat → M)
    (S W : Finset Nat) (hSW : ∀ g ∈ S, g ∉ W → f g = 0)
    (hWS : ∀ g ∈ W, g ∉ S → f g = 0) :
    ∑ g ∈ S, f g = ∑ g ∈ W, f g := by
  have h1 : ∑ g ∈ S, f g = ∑ g ∈ S ∪ W, f g := by
    apply Finset.sum_subset Finset.subset_union_left
    intro x hx hxS
    exact hWS x ((Finset.mem_union.mp hx).resolve_left hxS) hxS
  have h2 : ∑ g ∈ W, f g = ∑ g ∈ S ∪ W, f g := by
    apply Finset.sum_subset Finset.subset_union_right
    intro x hx hxW
    exact hSW x ((Finset.mem_union.mp hx).resolve_right hxW) hxW
  rw [h1, h2]

/-- A length-5 `Icc` sum, peeled from the top. -/
lemma sum_Icc_five {M : Type*} [AddCommMonoid M] (f : Nat → M) (a : Nat) :
    ∑ g ∈ Finset.Icc a (a + 4), f g = f a + f (a + 1) + f (a + 2) + f (a + 3) + f (a + 4) := by
  rw [Finset.sum_Icc_succ_top (by omega), Finset.sum_Icc_succ_top (by omega),
    Finset.sum_Icc_succ_top (by omega), Finset.sum_Icc_succ_top (by omega), Finset.Icc_self,
    Finset.sum_singleton]

/-- A length-3 `Icc` sum, peeled from the top. -/
lemma sum_Icc_three {M : Type*} [AddCommMonoid M] (f : Nat → M) (a : Nat) :
    ∑ g ∈ Finset.Icc a (a + 2), f g = f a + f (a + 1) + f (a + 2) := by
  rw [Finset.sum_Icc_succ_top (by omega), Finset.sum_Icc_succ_top (by omega), Finset.Icc_self,
    Finset.sum_singleton]

/-- A length-2 `Icc` sum, peeled from the top. -/
private lemma sum_Icc_two {M : Type*} [AddCommMonoid M] (f : Nat → M) (a : Nat) :
    ∑ g ∈ Finset.Icc a (a + 1), f g = f a + f (a + 1) := by
  rw [Finset.sum_Icc_succ_top (by omega), Finset.Icc_self, Finset.sum_singleton]

/-- A length-4 `Icc` sum, peeled from the top. -/
lemma sum_Icc_four {M : Type*} [AddCommMonoid M] (f : Nat → M) (a : Nat) :
    ∑ g ∈ Finset.Icc a (a + 3), f g = f a + f (a + 1) + f (a + 2) + f (a + 3) := by
  rw [Finset.sum_Icc_succ_top (by omega), Finset.sum_Icc_succ_top (by omega),
    Finset.sum_Icc_succ_top (by omega), Finset.Icc_self, Finset.sum_singleton]

/-- Splitting off the first two gaps of an `Icc 1 n` sum. -/
lemma sum_Icc_one_two_split {M : Type*} [AddCommMonoid M] (f : Nat → M) (n : Nat)
    (hn : 2 ≤ n) :
    ∑ g ∈ Finset.Icc 1 n, f g = f 1 + f 2 + ∑ g ∈ Finset.Icc 3 n, f g := by
  have hset : Finset.Icc 1 n = insert 1 (insert 2 (Finset.Icc 3 n)) := by
    ext x
    simp only [Finset.mem_Icc, Finset.mem_insert]
    omega
  rw [hset, Finset.sum_insert (by simp only [Finset.mem_insert, Finset.mem_Icc]; omega),
    Finset.sum_insert (by simp only [Finset.mem_Icc]; omega), add_assoc]

/-! ## The bulk step recurrences, `ℕ`-valued -/

/-- The `J`-column bulk step: the joined value at the generic column `k+5`
after one more step is the five-term bulk window at order `m`. -/
private lemma jE_succ_bulk (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (m k : Nat) :
    jE F (m + 1) (k + 5) =
      jE F m (k + 3) + 2 * jE F m (k + 4) + 3 * jE F m (k + 5) +
        2 * jE F m (k + 6) + jE F m (k + 7) := by
  rw [jE_step F hF m (k + 5) (by omega)]
  have hPzero : (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false (k + 5) true) = 0 := by
    apply Finset.sum_eq_zero
    intro g _hg
    rw [stepMul_P_to_J g (k + 5) (by omega)]; ring
  rw [hPzero, Nat.add_zero]
  have key : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true (k + 5) true) =
      ∑ g ∈ Finset.Icc (k + 3) (k + 7), jE F m g * stepMul g true (k + 5) true := by
    apply sum_eq_of_zero_outside
    · intro g hgS hgW
      simp only [Finset.mem_Icc] at hgS hgW
      by_cases hg3 : 3 ≤ g
      · rw [stepMul_J_bulk g (k + 5) hg3 (by omega)]
        have hz : bulkW g (k + 5) = 0 := by
          simp only [bulkW]; split_ifs with hb
          · exfalso; omega
          · rfl
        rw [hz]; ring
      · rw [stepMul_J_to_J_far g (k + 5) (by omega) (by omega)]; ring
    · intro g hgW hgS
      simp only [Finset.mem_Icc] at hgW hgS
      rw [jE_support F hF m g (by omega)]; ring
  rw [key, sum_Icc_five]
  have e1 : stepMul (k + 3) true (k + 5) true = 1 := by
    rw [stepMul_J_bulk (k + 3) (k + 5) (by omega) (by omega)]
    simp only [bulkW]; split_ifs with hb <;> omega
  have e2 : stepMul (k + 4) true (k + 5) true = 2 := by
    rw [stepMul_J_bulk (k + 4) (k + 5) (by omega) (by omega)]
    simp only [bulkW]; split_ifs with hb <;> omega
  have e3 : stepMul (k + 5) true (k + 5) true = 3 := by
    rw [stepMul_J_bulk (k + 5) (k + 5) (by omega) (by omega)]
    simp only [bulkW]; split_ifs with hb <;> omega
  have e4 : stepMul (k + 6) true (k + 5) true = 2 := by
    rw [stepMul_J_bulk (k + 6) (k + 5) (by omega) (by omega)]
    simp only [bulkW]; split_ifs with hb <;> omega
  have e5 : stepMul (k + 7) true (k + 5) true = 1 := by
    rw [stepMul_J_bulk (k + 7) (k + 5) (by omega) (by omega)]
    simp only [bulkW]; split_ifs with hb <;> omega
  rw [e1, e2, e3, e4, e5]; ring

/-- The `P`-column bulk step at the generic column `k+5`, packaged additively
(the deep-`J` spray `12 − 2·bulkW` is moved to the other side as `+`, so the
identity stays in `ℕ` without truncated subtraction). -/
private lemma pE_succ_bulk (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m k : Nat) :
    pE F (m + 1) (k + 5) +
      (2 * jE F m (k + 3) + 4 * jE F m (k + 4) + 6 * jE F m (k + 5) +
        4 * jE F m (k + 6) + 2 * jE F m (k + 7)) =
      8 * jE F m 1 + 10 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        2 * pE F m 2 + (pE F m (k + 3) + 2 * pE F m (k + 4) + 3 * pE F m (k + 5) +
          2 * pE F m (k + 6) + pE F m (k + 7)) := by
  rw [pE_step F hF m (k + 5) (by omega), show k + 5 + 2 = k + 7 from by omega]
  have keyJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true (k + 5) false) +
      (2 * jE F m (k + 3) + 4 * jE F m (k + 4) + 6 * jE F m (k + 5) + 4 * jE F m (k + 6) +
        2 * jE F m (k + 7)) =
      8 * jE F m 1 + 10 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega)]
    rw [show stepMul 1 true (k + 5) false = 8 from stepMul_1J_tail (k + 5) (by omega),
      show stepMul 2 true (k + 5) false = 10 from stepMul_2J_tail (k + 5) (by omega)]
    have hspray : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true (k + 5) false) +
        (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g (k + 5))) =
        12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
      rw [← Finset.sum_add_distrib, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro g hg
      simp only [Finset.mem_Icc] at hg
      have hs := stepMul_J_spray g (k + 5) (by omega) (by omega)
      have hb : bulkW g (k + 5) ≤ 3 := by simp only [bulkW]; split_ifs <;> omega
      have hsum12 : stepMul g true (k + 5) false + 2 * bulkW g (k + 5) = 12 := by omega
      rw [← Nat.mul_add, hsum12, Nat.mul_comm]
    have hbulkwindow : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g (k + 5))) =
        2 * jE F m (k + 3) + 4 * jE F m (k + 4) + 6 * jE F m (k + 5) + 4 * jE F m (k + 6) +
          2 * jE F m (k + 7) := by
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g (k + 5))) =
          ∑ g ∈ Finset.Icc (k + 3) (k + 7), jE F m g * (2 * bulkW g (k + 5)) := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          have hz : bulkW g (k + 5) = 0 := by
            simp only [bulkW]; split_ifs with hb
            · exfalso; omega
            · rfl
          rw [hz]; ring
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          rw [jE_support F hF m g (by omega)]; ring
      rw [hwin, sum_Icc_five]
      have e1 : bulkW (k + 3) (k + 5) = 1 := by simp only [bulkW]; split_ifs <;> omega
      have e2 : bulkW (k + 4) (k + 5) = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e3 : bulkW (k + 5) (k + 5) = 3 := by simp only [bulkW]; split_ifs <;> omega
      have e4 : bulkW (k + 6) (k + 5) = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e5 : bulkW (k + 7) (k + 5) = 1 := by simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3, e4, e5]; ring
    omega
  have keyP : (∑ g ∈ Finset.Icc 1 (k + 7), pE F m g * stepMul g false (k + 5) false) =
      2 * pE F m 2 + (pE F m (k + 3) + 2 * pE F m (k + 4) + 3 * pE F m (k + 5) +
        2 * pE F m (k + 6) + pE F m (k + 7)) := by
    rw [sum_Icc_one_two_split _ (k + 7) (by omega)]
    rw [pE_one F h1 m, zero_mul, zero_add,
      show stepMul 2 false (k + 5) false = 2 from stepMul_2P_tail (k + 5) (by omega)]
    have hsplit : (∑ g ∈ Finset.Icc 3 (k + 7), pE F m g * stepMul g false (k + 5) false) =
        pE F m (k + 3) + 2 * pE F m (k + 4) + 3 * pE F m (k + 5) + 2 * pE F m (k + 6) +
          pE F m (k + 7) := by
      have hwin : (∑ g ∈ Finset.Icc 3 (k + 7), pE F m g * stepMul g false (k + 5) false) =
          ∑ g ∈ Finset.Icc (k + 3) (k + 7), pE F m g * stepMul g false (k + 5) false := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          rw [stepMul_P_local g (k + 5) false (by omega) (by omega)]; ring
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          omega
      rw [hwin, sum_Icc_five]
      have e1 : stepMul (k + 3) false (k + 5) false = 1 := by
        rw [stepMul_P_bulk (k + 3) (k + 5) (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e2 : stepMul (k + 4) false (k + 5) false = 2 := by
        rw [stepMul_P_bulk (k + 4) (k + 5) (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e3 : stepMul (k + 5) false (k + 5) false = 3 := by
        rw [stepMul_P_bulk (k + 5) (k + 5) (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e4 : stepMul (k + 6) false (k + 5) false = 2 := by
        rw [stepMul_P_bulk (k + 6) (k + 5) (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e5 : stepMul (k + 7) false (k + 5) false = 1 := by
        rw [stepMul_P_bulk (k + 7) (k + 5) (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3, e4, e5]; ring
    rw [hsplit]; ring
  omega

private lemma jE_succ_to1 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m : Nat) :
    jE F (m + 1) 1 + jE F m 3 =
      5 * jE F m 1 + 6 * jE F m 2 + 8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        (2 * pE F m 2 + pE F m 3) := by
  rw [jE_step F hF m 1 (by omega)]
  have hP : (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false 1 true) =
      2 * pE F m 2 + pE F m 3 := by
    rw [sum_Icc_one_two_split _ 3 (by omega), Finset.Icc_self, Finset.sum_singleton,
      show stepMul 1 false 1 true = 3 from stepMul_1P_1J,
      show stepMul 2 false 1 true = 2 from stepMul_2P_1J, stepMul_P3_join,
      pE_one F h1 m]
    ring
  rw [hP]
  have hJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 1 true) + jE F m 3 =
      5 * jE F m 1 + 6 * jE F m 2 + 8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega),
      show stepMul 1 true 1 true = 5 from stepMul_1J_1J,
      show stepMul 2 true 1 true = 6 from stepMul_2J_1J]
    have hcore : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 1 true) +
        jE F m 3 = 8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
      have hpt : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 1 true) +
          (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * bulkW g 1) =
          8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
        rw [← Finset.sum_add_distrib, Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro g hg
        simp only [Finset.mem_Icc] at hg
        have hs := stepMul_J_to_1J g (by omega)
        have hb : bulkW g 1 ≤ 3 := by simp only [bulkW]; split_ifs <;> omega
        have heq : stepMul g true 1 true + bulkW g 1 = 8 := by omega
        rw [← Nat.mul_add, heq, Nat.mul_comm]
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * bulkW g 1) = jE F m 3 := by
        have hw2 : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * bulkW g 1) =
            ∑ g ∈ ({3} : Finset Nat), jE F m g * bulkW g 1 := by
          apply sum_eq_of_zero_outside
          · intro g hgS hgW
            simp only [Finset.mem_Icc] at hgS
            simp only [Finset.mem_singleton] at hgW
            have hz : bulkW g 1 = 0 := by
              simp only [bulkW]; split_ifs with hb
              · exfalso; omega
              · rfl
            rw [hz]; ring
          · intro g hgW hgS
            simp only [Finset.mem_singleton] at hgW
            subst hgW
            simp only [Finset.mem_Icc] at hgS
            rw [jE_support F hF m 3 (by omega)]; ring
        rw [hw2, Finset.sum_singleton]
        have : bulkW 3 1 = 1 := by simp only [bulkW]; split_ifs <;> omega
        rw [this, Nat.mul_one]
      omega
    omega
  omega

private lemma jE_succ_to2 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m : Nat) :
    jE F (m + 1) 2 =
      2 * jE F m 1 + 3 * jE F m 2 + 2 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        2 * jE F m 3 + jE F m 4 + 2 * pE F m 2 := by
  rw [jE_step F hF m 2 (by omega)]
  have hP : (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false 2 true) = 2 * pE F m 2 := by
    rw [sum_Icc_one_two_split _ 3 (by omega), Finset.Icc_self, Finset.sum_singleton,
      show stepMul 1 false 2 true = 2 from stepMul_1P_2J,
      show stepMul 2 false 2 true = 2 from stepMul_2P_2J,
      stepMul_P_to_J2 3 (by omega), pE_one F h1 m]
    ring
  rw [hP]
  have hJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 2 true) =
      2 * jE F m 1 + 3 * jE F m 2 + 2 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        2 * jE F m 3 + jE F m 4 := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega),
      show stepMul 1 true 2 true = 2 from stepMul_1J_2J,
      show stepMul 2 true 2 true = 3 from stepMul_2J_2J]
    have hcore : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 2 true) =
        2 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) + 2 * jE F m 3 + jE F m 4 := by
      have hpt : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 2 true) =
          ∑ g ∈ Finset.Icc 3 (2 * m + 2), (jE F m g * 2 + jE F m g * bulkW g 2) := by
        apply Finset.sum_congr rfl
        intro g hg
        simp only [Finset.mem_Icc] at hg
        have hs := stepMul_J_to_2J g (by omega)
        rw [hs]; ring
      rw [hpt, Finset.sum_add_distrib, ← Finset.sum_mul]
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * bulkW g 2) =
          2 * jE F m 3 + jE F m 4 := by
        have hw2 : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * bulkW g 2) =
            ∑ g ∈ Finset.Icc 3 4, jE F m g * bulkW g 2 := by
          apply sum_eq_of_zero_outside
          · intro g hgS hgW
            simp only [Finset.mem_Icc] at hgS hgW
            have hz : bulkW g 2 = 0 := by
              simp only [bulkW]; split_ifs with hb
              · exfalso; omega
              · rfl
            rw [hz]; ring
          · intro g hgW hgS
            simp only [Finset.mem_Icc] at hgW hgS
            rw [jE_support F hF m g (by omega)]; ring
        rw [hw2, sum_Icc_two]
        have e1 : bulkW 3 2 = 2 := by simp only [bulkW]; split_ifs <;> omega
        have e2 : bulkW 4 2 = 1 := by simp only [bulkW]; split_ifs <;> omega
        rw [e1, e2]; ring
      rw [hwin]; ring
    omega
  omega

private lemma jE_succ_to3 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0) (m : Nat) :
    jE F (m + 1) 3 =
      jE F m 1 + 2 * jE F m 2 + 3 * jE F m 3 + 2 * jE F m 4 + jE F m 5 := by
  rw [jE_step F hF m 3 (by omega)]
  have hP : (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false 3 true) = 0 := by
    apply Finset.sum_eq_zero
    intro g _hg
    rw [stepMul_P_to_J g 3 (by omega)]; ring
  rw [hP, Nat.add_zero, sum_Icc_one_two_split _ (2 * m + 2) (by omega),
    show stepMul 1 true 3 true = 1 from stepMul_1J_3J,
    show stepMul 2 true 3 true = 2 from stepMul_2J_3J]
  have hcore : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 3 true) =
      3 * jE F m 3 + 2 * jE F m 4 + jE F m 5 := by
    have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 3 true) =
        ∑ g ∈ Finset.Icc 3 5, jE F m g * stepMul g true 3 true := by
      apply sum_eq_of_zero_outside
      · intro g hgS hgW
        simp only [Finset.mem_Icc] at hgS hgW
        rw [stepMul_J_bulk g 3 (by omega) (by omega)]
        have hz : bulkW g 3 = 0 := by simp only [bulkW]; split_ifs with hb <;> omega
        rw [hz]; ring
      · intro g hgW hgS
        simp only [Finset.mem_Icc] at hgW hgS
        rw [jE_support F hF m g (by omega)]; ring
    rw [hwin, sum_Icc_three]
    have e1 : stepMul 3 true 3 true = 3 := by
      rw [stepMul_J_bulk 3 3 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
    have e2 : stepMul 4 true 3 true = 2 := by
      rw [stepMul_J_bulk 4 3 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
    have e3 : stepMul 5 true 3 true = 1 := by
      rw [stepMul_J_bulk 5 3 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
    rw [e1, e2, e3]; ring
  omega

/-- Target gap 4: window `[2,6]`, mixing the literal head at g=2 with bulk. -/
private lemma jE_succ_to4 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0) (m : Nat) :
    jE F (m + 1) 4 =
      jE F m 2 + 2 * jE F m 3 + 3 * jE F m 4 + 2 * jE F m 5 + jE F m 6 := by
  rw [jE_step F hF m 4 (by omega)]
  have hP : (∑ g ∈ Finset.Icc 1 3, pE F m g * stepMul g false 4 true) = 0 := by
    apply Finset.sum_eq_zero
    intro g _hg
    rw [stepMul_P_to_J g 4 (by omega)]; ring
  rw [hP, Nat.add_zero]
  have hJ1 : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 4 true) =
      ∑ g ∈ Finset.Icc 2 (2 * m + 2), jE F m g * stepMul g true 4 true := by
    apply sum_eq_of_zero_outside
    · intro g hgS hgW
      simp only [Finset.mem_Icc] at hgS hgW
      rw [stepMul_J_to_J_far g 4 (by omega) (by omega)]; ring
    · intro g hgW hgS
      simp only [Finset.mem_Icc] at hgW hgS
      omega
  rw [hJ1]
  have hJ2 : (∑ g ∈ Finset.Icc 2 (2 * m + 2), jE F m g * stepMul g true 4 true) =
      ∑ g ∈ Finset.Icc 2 6, jE F m g * stepMul g true 4 true := by
    apply sum_eq_of_zero_outside
    · intro g hgS hgW
      simp only [Finset.mem_Icc] at hgS hgW
      by_cases hg3 : 3 ≤ g
      · rw [stepMul_J_bulk g 4 hg3 (by omega)]
        have hz : bulkW g 4 = 0 := by simp only [bulkW]; split_ifs with hb <;> omega
        rw [hz]; ring
      · exfalso; omega
    · intro g hgW hgS
      simp only [Finset.mem_Icc] at hgW hgS
      rw [jE_support F hF m g (by omega)]; ring
  rw [hJ2, show (6:ℕ) = 2 + 4 from rfl, sum_Icc_five]
  have e2 : stepMul 2 true 4 true = 1 := stepMul_2J_4J
  have e3 : stepMul 3 true 4 true = 2 := by
    rw [stepMul_J_bulk 3 4 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
  have e4 : stepMul 4 true 4 true = 3 := by
    rw [stepMul_J_bulk 4 4 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
  have e5 : stepMul 5 true 4 true = 2 := by
    rw [stepMul_J_bulk 5 4 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
  have e6 : stepMul 6 true 4 true = 1 := by
    rw [stepMul_J_bulk 6 4 (by omega) (by omega)]; simp only [bulkW]; split_ifs <;> omega
  rw [e2, e3, e4, e5, e6]; ring

private lemma pE_succ_to2 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m : Nat) :
    pE F (m + 1) 2 + (4 * jE F m 3 + 2 * jE F m 4) =
      4 * jE F m 1 + 4 * jE F m 2 + 8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        (pE F m 2 + 2 * pE F m 3 + pE F m 4) := by
  rw [pE_step F hF m 2 (by omega), show (2:ℕ) + 2 = 4 from rfl]
  have keyJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 2 false) +
      (4 * jE F m 3 + 2 * jE F m 4) =
      4 * jE F m 1 + 4 * jE F m 2 + 8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega),
      show stepMul 1 true 2 false = 4 from stepMul_1J_2P,
      show stepMul 2 true 2 false = 4 from stepMul_2J_2P]
    have hspray : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 2 false) +
        (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 2)) =
        8 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
      rw [← Finset.sum_add_distrib, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro g hg
      simp only [Finset.mem_Icc] at hg
      have hs := stepMul_J_to_2P g (by omega)
      have hb : bulkW g 2 ≤ 3 := by simp only [bulkW]; split_ifs <;> omega
      have hsum8 : stepMul g true 2 false + 2 * bulkW g 2 = 8 := by omega
      rw [← Nat.mul_add, hsum8, Nat.mul_comm]
    have hbulkwindow : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 2)) =
        4 * jE F m 3 + 2 * jE F m 4 := by
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 2)) =
          ∑ g ∈ Finset.Icc 3 4, jE F m g * (2 * bulkW g 2) := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          have hz : bulkW g 2 = 0 := by simp only [bulkW]; split_ifs with hb <;> omega
          rw [hz]; ring
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          rw [jE_support F hF m g (by omega)]; ring
      rw [hwin, sum_Icc_two]
      have e1 : bulkW 3 2 = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e2 : bulkW 4 2 = 1 := by simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2]; ring
    omega
  have keyP : (∑ g ∈ Finset.Icc 1 4, pE F m g * stepMul g false 2 false) =
      pE F m 2 + 2 * pE F m 3 + pE F m 4 := by
    rw [sum_Icc_one_two_split _ 4 (by omega)]
    rw [pE_one F h1 m, zero_mul, zero_add,
      show stepMul 2 false 2 false = 1 from stepMul_2P_2P]
    have hsplit : (∑ g ∈ Finset.Icc 3 4, pE F m g * stepMul g false 2 false) =
        2 * pE F m 3 + pE F m 4 := by
      rw [sum_Icc_two]
      have e1 : stepMul 3 false 2 false = 2 := by
        rw [stepMul_P_bulk 3 2 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e2 : stepMul 4 false 2 false = 1 := by
        rw [stepMul_P_bulk 4 2 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2]; ring
    rw [hsplit]; ring
  omega

private lemma pE_succ_to3 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m : Nat) :
    pE F (m + 1) 3 + (6 * jE F m 3 + 4 * jE F m 4 + 2 * jE F m 5) =
      6 * jE F m 1 + 6 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        (4 * pE F m 2 + 3 * pE F m 3 + 2 * pE F m 4 + pE F m 5) := by
  rw [pE_step F hF m 3 (by omega), show (3:ℕ) + 2 = 5 from rfl]
  have keyJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 3 false) +
      (6 * jE F m 3 + 4 * jE F m 4 + 2 * jE F m 5) =
      6 * jE F m 1 + 6 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega),
      show stepMul 1 true 3 false = 6 from stepMul_1J_3P,
      show stepMul 2 true 3 false = 6 from stepMul_2J_3P]
    have hspray : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 3 false) +
        (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 3)) =
        12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
      rw [← Finset.sum_add_distrib, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro g hg
      simp only [Finset.mem_Icc] at hg
      have hs := stepMul_J_spray g 3 (by omega) (by omega)
      have hb : bulkW g 3 ≤ 3 := by simp only [bulkW]; split_ifs <;> omega
      have hsum12 : stepMul g true 3 false + 2 * bulkW g 3 = 12 := by omega
      rw [← Nat.mul_add, hsum12, Nat.mul_comm]
    have hbulkwindow : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 3)) =
        6 * jE F m 3 + 4 * jE F m 4 + 2 * jE F m 5 := by
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 3)) =
          ∑ g ∈ Finset.Icc 3 5, jE F m g * (2 * bulkW g 3) := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          have hz : bulkW g 3 = 0 := by simp only [bulkW]; split_ifs with hb <;> omega
          rw [hz]; ring
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          rw [jE_support F hF m g (by omega)]; ring
      rw [hwin, sum_Icc_three]
      have e1 : bulkW 3 3 = 3 := by simp only [bulkW]; split_ifs <;> omega
      have e2 : bulkW 4 3 = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e3 : bulkW 5 3 = 1 := by simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3]; ring
    omega
  have keyP : (∑ g ∈ Finset.Icc 1 5, pE F m g * stepMul g false 3 false) =
      4 * pE F m 2 + 3 * pE F m 3 + 2 * pE F m 4 + pE F m 5 := by
    rw [sum_Icc_one_two_split _ 5 (by omega)]
    rw [pE_one F h1 m, zero_mul, zero_add,
      show stepMul 2 false 3 false = 4 from stepMul_2P_3P]
    have hsplit : (∑ g ∈ Finset.Icc 3 5, pE F m g * stepMul g false 3 false) =
        3 * pE F m 3 + 2 * pE F m 4 + pE F m 5 := by
      rw [sum_Icc_three]
      have e1 : stepMul 3 false 3 false = 3 := by
        rw [stepMul_P_bulk 3 3 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e2 : stepMul 4 false 3 false = 2 := by
        rw [stepMul_P_bulk 4 3 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e3 : stepMul 5 false 3 false = 1 := by
        rw [stepMul_P_bulk 5 3 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3]; ring
    rw [hsplit]; ring
  omega

private lemma pE_succ_to4 (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0)
    (h1 : F (1, false) = 0) (m : Nat) :
    pE F (m + 1) 4 + (4 * jE F m 3 + 6 * jE F m 4 + 4 * jE F m 5 + 2 * jE F m 6) =
      8 * jE F m 1 + 8 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) +
        (3 * pE F m 2 + 2 * pE F m 3 + 3 * pE F m 4 + 2 * pE F m 5 + pE F m 6) := by
  rw [pE_step F hF m 4 (by omega), show (4:ℕ) + 2 = 6 from rfl]
  have keyJ : (∑ g ∈ Finset.Icc 1 (2 * m + 2), jE F m g * stepMul g true 4 false) +
      (4 * jE F m 3 + 6 * jE F m 4 + 4 * jE F m 5 + 2 * jE F m 6) =
      8 * jE F m 1 + 8 * jE F m 2 + 12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
    rw [sum_Icc_one_two_split _ (2 * m + 2) (by omega),
      show stepMul 1 true 4 false = 8 from stepMul_1J_tail 4 (by omega),
      show stepMul 2 true 4 false = 8 from stepMul_2J_4P]
    have hspray : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * stepMul g true 4 false) +
        (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 4)) =
        12 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
      rw [← Finset.sum_add_distrib, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro g hg
      simp only [Finset.mem_Icc] at hg
      have hs := stepMul_J_spray g 4 (by omega) (by omega)
      have hb : bulkW g 4 ≤ 3 := by simp only [bulkW]; split_ifs <;> omega
      have hsum12 : stepMul g true 4 false + 2 * bulkW g 4 = 12 := by omega
      rw [← Nat.mul_add, hsum12, Nat.mul_comm]
    have hbulkwindow : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 4)) =
        4 * jE F m 3 + 6 * jE F m 4 + 4 * jE F m 5 + 2 * jE F m 6 := by
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g * (2 * bulkW g 4)) =
          ∑ g ∈ Finset.Icc 3 6, jE F m g * (2 * bulkW g 4) := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          have hz : bulkW g 4 = 0 := by simp only [bulkW]; split_ifs with hb <;> omega
          rw [hz]; ring
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          rw [jE_support F hF m g (by omega)]; ring
      rw [hwin, show (6:ℕ) = 3 + 3 from rfl]
      have e1 : bulkW 3 4 = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e2 : bulkW 4 4 = 3 := by simp only [bulkW]; split_ifs <;> omega
      have e3 : bulkW 5 4 = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e4 : bulkW 6 4 = 1 := by simp only [bulkW]; split_ifs <;> omega
      rw [show Finset.Icc (3:ℕ) (3+3) = insert 3 (Finset.Icc 4 6) from by
          ext x; simp only [Finset.mem_Icc, Finset.mem_insert]; omega,
        Finset.sum_insert (by simp only [Finset.mem_Icc]; omega),
        show (6:ℕ) = 4 + 2 from rfl, sum_Icc_three]
      rw [e1, e2, e3, e4]; ring
    omega
  have keyP : (∑ g ∈ Finset.Icc 1 6, pE F m g * stepMul g false 4 false) =
      3 * pE F m 2 + 2 * pE F m 3 + 3 * pE F m 4 + 2 * pE F m 5 + pE F m 6 := by
    rw [sum_Icc_one_two_split _ 6 (by omega)]
    rw [pE_one F h1 m, zero_mul, zero_add,
      show stepMul 2 false 4 false = 3 from stepMul_2P_4P]
    have hsplit : (∑ g ∈ Finset.Icc 3 6, pE F m g * stepMul g false 4 false) =
        2 * pE F m 3 + 3 * pE F m 4 + 2 * pE F m 5 + pE F m 6 := by
      rw [show (6:ℕ) = 3 + 3 from rfl, sum_Icc_four]
      have e1 : stepMul 3 false 4 false = 2 := by
        rw [stepMul_P_bulk 3 4 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e2 : stepMul 4 false 4 false = 3 := by
        rw [stepMul_P_bulk 4 4 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e3 : stepMul 5 false 4 false = 2 := by
        rw [stepMul_P_bulk 5 4 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      have e4 : stepMul 6 false 4 false = 1 := by
        rw [stepMul_P_bulk 6 4 (by omega) (by omega)]
        simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3, e4]; ring
    rw [hsplit]; ring
  omega

/-! ## Coefficient bookkeeping for `PowerSeries ℚ` numerals -/

private lemma coeff_2mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (2 * S) = 2 * coeff m S := by
  rw [show (2 : PowerSeries ℚ) = C 2 from (map_ofNat C 2).symm, coeff_C_mul]

private lemma coeff_3mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (3 * S) = 3 * coeff m S := by
  rw [show (3 : PowerSeries ℚ) = C 3 from (map_ofNat C 3).symm, coeff_C_mul]

private lemma coeff_4mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (4 * S) = 4 * coeff m S := by
  rw [show (4 : PowerSeries ℚ) = C 4 from (map_ofNat C 4).symm, coeff_C_mul]

private lemma coeff_5mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (5 * S) = 5 * coeff m S := by
  rw [show (5 : PowerSeries ℚ) = C 5 from (map_ofNat C 5).symm, coeff_C_mul]

private lemma coeff_6mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (6 * S) = 6 * coeff m S := by
  rw [show (6 : PowerSeries ℚ) = C 6 from (map_ofNat C 6).symm, coeff_C_mul]

private lemma coeff_8mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (8 * S) = 8 * coeff m S := by
  rw [show (8 : PowerSeries ℚ) = C 8 from (map_ofNat C 8).symm, coeff_C_mul]

private lemma coeff_10mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (10 * S) = 10 * coeff m S := by
  rw [show (10 : PowerSeries ℚ) = C 10 from (map_ofNat C 10).symm, coeff_C_mul]

private lemma coeff_12mul (S : PowerSeries ℚ) (m : Nat) :
    coeff m (12 * S) = 12 * coeff m S := by
  rw [show (12 : PowerSeries ℚ) = C 12 from (map_ofNat C 12).symm, coeff_C_mul]

private lemma bulkW_le3 (g gp : Nat) : bulkW g gp ≤ 3 := by
  simp only [bulkW]; split_ifs <;> omega

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
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_jY, show jE F 0 1 = j01 from by rw [jE_zero]; exact h.head_j1, map_add,
      PowerSeries.coeff_zero_C, PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_jY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, map_sub, coeff_5mul, coeff_6mul, coeff_8mul, coeff_2mul,
      coeff_jY, coeff_pY, coeff_JmY]
    have hn := jE_succ_to1 F h.deep_j h.head_p1 m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Column `u⁴`: the `j₂` equation. -/
theorem jY_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 2 = C (j02 : ℚ) +
      X * (2 * jY F 1 + 3 * jY F 2 + 2 * JmY F + 2 * jY F 3 +
        jY F 4 + 2 * pY F 2) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_jY, show jE F 0 2 = j02 from by rw [jE_zero]; exact h.head_j2, map_add,
      PowerSeries.coeff_zero_C, PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_jY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, coeff_2mul, coeff_3mul, coeff_jY, coeff_pY, coeff_JmY]
    have hn := jE_succ_to2 F h.deep_j h.head_p1 m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Column `u⁵`: the first interior column, fed by the heads. -/
theorem jY_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 3 = X * (jY F 1 + 2 * jY F 2 + 3 * jY F 3 + 2 * jY F 4 +
      jY F 5) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_jY, show jE F 0 3 = 0 from by rw [jE_zero]; exact h.deep_j 3 (by omega),
      Nat.cast_zero, PowerSeries.coeff_zero_X_mul]
  | succ m =>
    rw [coeff_jY, PowerSeries.coeff_succ_X_mul]
    simp only [map_add, coeff_2mul, coeff_3mul, coeff_jY]
    have hn := jE_succ_to3 F h.deep_j m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Column `u⁶`: the second interior column. -/
theorem jY_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jY F 4 = X * (jY F 2 + 2 * jY F 3 + 3 * jY F 4 + 2 * jY F 5 +
      jY F 6) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_jY, show jE F 0 4 = 0 from by rw [jE_zero]; exact h.deep_j 4 (by omega),
      Nat.cast_zero, PowerSeries.coeff_zero_X_mul]
  | succ m =>
    rw [coeff_jY, PowerSeries.coeff_succ_X_mul]
    simp only [map_add, coeff_2mul, coeff_3mul, coeff_jY]
    have hn := jE_succ_to4 F h.deep_j m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Generic column `u^{k+7}`: the pure bulk recurrence. -/
theorem jY_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    jY F (k + 5) = X * (jY F (k + 7) + 2 * jY F (k + 6) +
      3 * jY F (k + 5) + 2 * jY F (k + 4) + jY F (k + 3)) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_jY, show jE F 0 (k + 5) = 0 from by
        rw [jE_zero]; exact h.deep_j (k + 5) (by omega), Nat.cast_zero,
      PowerSeries.coeff_zero_X_mul]
  | succ m =>
    rw [coeff_jY, PowerSeries.coeff_succ_X_mul, map_add, map_add, map_add, map_add,
      coeff_2mul, coeff_3mul, coeff_2mul, coeff_jY, coeff_jY, coeff_jY, coeff_jY, coeff_jY]
    have hn := jE_succ_bulk F h.deep_j m k
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

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
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_pY, show pE F 0 2 = p02 from by rw [pE_zero]; exact h.head_p2, map_add,
      PowerSeries.coeff_zero_C, PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_pY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, map_sub, coeff_2mul, coeff_4mul, coeff_8mul,
      coeff_pY, coeff_jY, coeff_JmY]
    have hn := pE_succ_to2 F h.deep_j h.head_p1 m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Column `u⁵`: the `p₃` equation. -/
theorem pY_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pY F 3 = C (pt : ℚ) +
      X * ((pY F 5 - 2 * jY F 5) + 2 * (pY F 4 - 2 * jY F 4) +
        3 * (pY F 3 - 2 * jY F 3) + 12 * JmY F + 6 * jY F 1 +
        6 * jY F 2 + 4 * pY F 2) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_pY, show pE F 0 3 = pt from by
        rw [pE_zero]; exact h.deep_p 3 (by omega), map_add, PowerSeries.coeff_zero_C,
      PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_pY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, map_sub, coeff_2mul, coeff_3mul, coeff_6mul, coeff_4mul, coeff_12mul,
      coeff_pY, coeff_jY, coeff_JmY]
    have hn := pE_succ_to3 F h.deep_j h.head_p1 m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

/-- Column `u⁶`. -/
theorem pY_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pY F 4 = C (pt : ℚ) +
      X * ((pY F 6 - 2 * jY F 6) + 2 * (pY F 5 - 2 * jY F 5) +
        3 * (pY F 4 - 2 * jY F 4) + 2 * (pY F 3 - 2 * jY F 3) +
        12 * JmY F + 8 * jY F 1 + 8 * jY F 2 + 3 * pY F 2) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_pY, show pE F 0 4 = pt from by
        rw [pE_zero]; exact h.deep_p 4 (by omega), map_add, PowerSeries.coeff_zero_C,
      PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_pY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, map_sub, coeff_2mul, coeff_3mul, coeff_8mul, coeff_12mul,
      coeff_pY, coeff_jY, coeff_JmY]
    have hn := pE_succ_to4 F h.deep_j h.head_p1 m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

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
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_pY, show pE F 0 (k + 5) = pt from by
        rw [pE_zero]; exact h.deep_p (k + 5) (by omega), map_add, PowerSeries.coeff_zero_C,
      PowerSeries.coeff_zero_X_mul, add_zero]
  | succ m =>
    rw [coeff_pY, map_add, PowerSeries.coeff_C, if_neg (Nat.succ_ne_zero m),
      PowerSeries.coeff_succ_X_mul, zero_add]
    simp only [map_add, map_sub, coeff_2mul, coeff_3mul, coeff_8mul, coeff_10mul, coeff_12mul,
      coeff_pY, coeff_jY, coeff_JmY]
    have hn := pE_succ_bulk F h.deep_j h.head_p1 m k
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith

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
