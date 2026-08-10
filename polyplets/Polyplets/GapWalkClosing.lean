/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.RingTheory.PowerSeries.Expand
import Mathlib.RingTheory.PowerSeries.NoZeroDivisors
import Polyplets.GapWalkColumns
import Polyplets.KernelSeries
import Polyplets.KernelRoots

/-!
# Notary piece K, module 6: evaluation at the kernel roots — the closing

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`, wave K-γ. This
is where the three K-α/K-β strands meet: the column identities of
`GapWalkColumns` (transported to the `s`-variable by `expand 2`), the
locally-finite-sum library of `KernelSeries`, and the kernel roots of
`KernelRoots`. Output: the **six closing equations** per start — the
cleared 6×6 system of `experiments/notary_k_measure.py` m5 — as exact
`ℚ⟦s⟧` identities satisfied by the walk's own series, plus the
end-functional bridge series.

Contents:

* `jS`/`pS`/`JmS` — the column series in the `s`-variable
  (`expand 2`, so `y = s²`; even series), with the transported column
  identities (`jS_col_*`, `pS_col_*`) and the `Jm` column-sum recurrence
  (`JmY_step`, the one new walk-level fact here — the equation-(4)
  primitive);
* `J3ser`/`P3ser`/`J3serW` — the walk series evaluated at any `u` with
  zero constant term, as `lfsum`s (`J3serW` carries the weight `g`, the
  `u`-derivative bookkeeping);
* `lfsum_geom` — the geometric collapse `Σ_{g ≥ K} u^g = u^K·w` against a
  certified inverse `(1−u)·w = 1`;
* `master_J` / `master_P` / `master_J_deriv` — the three evaluated master
  identities, for **generic** `u` (premultiplied by `u²` so every index
  shift is legal without division);
* the root facts `coeff_one_u1/u2`, `u1_ne_zero/u2_ne_zero`, and the six
  closing equations `closing_Q_u1/u2`, `closing_eq3`, `closing_eq4`,
  `closing_P_u1/u2` (with the intermediate `dJ3_u1/u2`);
* `qSeries`/`bSeries` — the emitted-family series as combinations of the
  six unknowns, tied to the walk's end functionals.

Every statement was verified numerically before this skeleton was
written: `experiments/notary_kgamma_statements.py` g1–g7
(`build/notary_kgamma_statements.log`) — the three masters checked at
both roots *and* at the non-root `u = s + s²` (they are generic-`u`
identities), the closing equations at s-order ≤ 36, both starts.

## Proof recipes

*Transports*: apply `e2` (an `ℚ`-algebra map) to the K-β identity;
`map_add`, `map_mul`, `map_sub`, `map_ofNat`, `PowerSeries.expand_C`,
`PowerSeries.expand_X` push it through; `e2 X = X ^ 2`.

*`JmY_step`*: same toolkit as the K-β column proofs (`PowerSeries.ext`;
coefficient 0 is an empty sum; coefficient `m+1` via `jE_step` at each
target `g ∈ Icc 3 (2m+4)`, `Finset.sum_comm` to swap target/source sums,
then per-source column sums: deep sources `g' ≥ 5` contribute `9`,
`g' = 3` contributes `6`, `g' = 4` contributes `8`, sources `1`, `2`
contribute `1`, `3`; `P` sources contribute `0` by
`GapWalkRows.stepMul_P_to_J`). The K-β file `GapWalkColumns.lean` has
`private` Finset window helpers worth replicating.

*`lfsum_geom`*: multiply by `(1−u)`; `lfsum_mul_left` + `lfsum_sub` +
`lfsum_shift` telescope `Σ_{g≥K} u^g − Σ_{g≥K} u^{g+1}` to `u^K`; then
`hw` cancels.

*Masters*: all families have the shape `a g * u ^ g`, so `LocFin` is
`locFin_geom`. Strategy: expand `(1+u+u²)² = 1 + 2u + 3u² + 2u³ + u⁴`;
each product `u^{2+k} · lfsum (fun g => a g * u^g)` becomes, by
`lfsum_mul_left` and then `lfsum_shift` (backwards: the shifted family
`fun n => (if n < 2+k then 0 else a (n−(2+k))) * u^n` re-indexes to it),
an `lfsum` over a common exponent `n`. Combine everything with
`lfsum_add`/`lfsum_sub` into a single `lfsum` of a bracket family
`fun n => (bracket n) * u^n`; show the bracket is pointwise equal to the
finite right-side column family (case-split `n`: below the boundary both
sides are cutoff zeros; the finitely many boundary exponents use
`jS_col_one`…`jS_col_four` resp. the `pS_col_*`; generic `n` uses
`jS_col_generic`/`pS_col_generic` at `k := n − 11`-style indices); then
`lfsum_of_support_lt` collapses the finite side to the stated polynomial.
The `w`-tails of `master_P` enter through `lfsum_geom` (the `C pt`
constants of `pS_col_*` sum to geometric tails). This is the hardest
module of piece K; structure your private lemmas as one reusable
"shifted-window lfsum" toolkit and three assemblies.

*Root facts*: `Kernel.u1 = mk fun n => 2⁻¹ * coeff (n+1) (1 − X − A)`
definitionally, so `coeff 1 u1 = 2⁻¹ * coeff 2 (1 − X − A)`;
`coeff 2 A = sqrtCoef aaC 2` evaluates by unfolding the `sqrtList`
recursion (`simp [sqrtList, sqrtCoef]`/`norm_num`; the value is `−2`,
giving `coeff 1 u1 = 1`). `u ≠ 0` follows from a nonzero coefficient.

*Closing equations*: instantiate the masters at `u1`/`u2` (`hu` from
`constantCoeff_u1/u2`; `w` from `one_sub_u1_mul_w1/u2`); the kernel
identity `u1_kernel` makes `u² − X²(1+u+u²)² = 0` (`sub_eq_zero`), so
the premultiplied master reads `0 = u^4 · RHS`; `ℚ⟦s⟧` is a domain
(`u1_ne_zero`, `pow_ne_zero`, `mul_eq_zero`) so the right factor
vanishes. `closing_eq3` is `jS_col_one` rearranged (`linear_combination`).
`closing_eq4` is a `linear_combination` of `JmS_step`, `jS_col_one`,
`jS_col_two`. `dJ3_u1/u2`: the derivative master at the root, with
`closing_Q_u1/u2` killing the `Q` term and `u³` cancelled. `closing_P_*`:
the P-master at the root gives `P0 − p₂u² + X²·R_P = 2·J₃(uᵢ)` (cancel
`u⁴`), multiply by `Kernel.dP uᵢ` and rewrite `dP uᵢ · J3ser` by `dJ3_*`.

*Bridge*: `qEndF_eval`/`bareEndF_eval` of `GapWalkExact` + `pE_one`;
coefficient bookkeeping only.

Do not change any statement below; if one resists proof, leave it
sorried and report back.
-/

namespace Polyplets
namespace GapWalk

open PowerSeries Polyplets.KernelSeries Polyplets.Kernel

/-! ## The column series in the `s`-variable -/

/-- `expand 2`: the algebra map `y ↦ s²`. -/
noncomputable def e2 : PowerSeries ℚ →ₐ[ℚ] PowerSeries ℚ :=
  PowerSeries.expand 2 (by norm_num)

/-- The joined column at gap `g`, in `s` (`y = s²`). -/
noncomputable def jS (F : St → Nat) (g : Nat) : PowerSeries ℚ := e2 (jY F g)

/-- The pending column at gap `g`, in `s`. -/
noncomputable def pS (F : St → Nat) (g : Nat) : PowerSeries ℚ := e2 (pY F g)

/-- The deep-`J` mass, in `s`. -/
noncomputable def JmS (F : St → Nat) : PowerSeries ℚ := e2 (JmY F)

@[simp] theorem coeff_jS_even (F : St → Nat) (g m : Nat) :
    coeff (2 * m) (jS F g) = (jE F m g : ℚ) := by
  change coeff (2 * m) (e2 (jY F g)) = (jE F m g : ℚ)
  rw [e2, PowerSeries.coeff_expand_mul, coeff_jY]

theorem coeff_jS_odd (F : St → Nat) (g n : Nat) (h : ¬ 2 ∣ n) :
    coeff n (jS F g) = 0 := by
  change coeff n (e2 (jY F g)) = 0
  rw [e2, PowerSeries.coeff_expand_of_not_dvd 2 (by norm_num) _ h]

@[simp] theorem coeff_pS_even (F : St → Nat) (g m : Nat) :
    coeff (2 * m) (pS F g) = (pE F m g : ℚ) := by
  change coeff (2 * m) (e2 (pY F g)) = (pE F m g : ℚ)
  rw [e2, PowerSeries.coeff_expand_mul, coeff_pY]

theorem coeff_pS_odd (F : St → Nat) (g n : Nat) (h : ¬ 2 ∣ n) :
    coeff n (pS F g) = 0 := by
  change coeff n (e2 (pY F g)) = 0
  rw [e2, PowerSeries.coeff_expand_of_not_dvd 2 (by norm_num) _ h]

/-- Nothing is ever pending at gap 1, in `s`. -/
theorem pS_one (F : St → Nat) (h1 : F (1, false) = 0) : pS F 1 = 0 := by
  change e2 (pY F 1) = 0
  rw [pY_one F h1, map_zero]

/-! ## The transported column identities -/

theorem jS_col_one {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 1 = C (j01 : ℚ) +
      X ^ 2 * (5 * jS F 1 + 6 * jS F 2 + 8 * JmS F - jS F 3 +
        2 * pS F 2 + pS F 3) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (jY_col_one h)

theorem jS_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 2 = C (j02 : ℚ) +
      X ^ 2 * (2 * jS F 1 + 3 * jS F 2 + 2 * JmS F + 2 * jS F 3 +
        jS F 4 + 2 * pS F 2) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (jY_col_two h)

theorem jS_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 3 = X ^ 2 * (jS F 1 + 2 * jS F 2 + 3 * jS F 3 + 2 * jS F 4 +
      jS F 5) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (jY_col_three h)

theorem jS_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 4 = X ^ 2 * (jS F 2 + 2 * jS F 3 + 3 * jS F 4 + 2 * jS F 5 +
      jS F 6) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (jY_col_four h)

theorem jS_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    jS F (k + 5) = X ^ 2 * (jS F (k + 7) + 2 * jS F (k + 6) +
      3 * jS F (k + 5) + 2 * jS F (k + 4) + jS F (k + 3)) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (jY_col_generic h k)

theorem pS_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 2 = C (p02 : ℚ) +
      X ^ 2 * ((pS F 4 - 2 * jS F 4) + 2 * (pS F 3 - 2 * jS F 3) +
        8 * JmS F + 4 * jS F 1 + 4 * jS F 2 + pS F 2) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (pY_col_two h)

theorem pS_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 3 = C (pt : ℚ) +
      X ^ 2 * ((pS F 5 - 2 * jS F 5) + 2 * (pS F 4 - 2 * jS F 4) +
        3 * (pS F 3 - 2 * jS F 3) + 12 * JmS F + 6 * jS F 1 +
        6 * jS F 2 + 4 * pS F 2) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (pY_col_three h)

theorem pS_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 4 = C (pt : ℚ) +
      X ^ 2 * ((pS F 6 - 2 * jS F 6) + 2 * (pS F 5 - 2 * jS F 5) +
        3 * (pS F 4 - 2 * jS F 4) + 2 * (pS F 3 - 2 * jS F 3) +
        12 * JmS F + 8 * jS F 1 + 8 * jS F 2 + 3 * pS F 2) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (pY_col_four h)

theorem pS_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    pS F (k + 5) = C (pt : ℚ) +
      X ^ 2 * ((pS F (k + 7) - 2 * jS F (k + 7)) +
        2 * (pS F (k + 6) - 2 * jS F (k + 6)) +
        3 * (pS F (k + 5) - 2 * jS F (k + 5)) +
        2 * (pS F (k + 4) - 2 * jS F (k + 4)) +
        (pS F (k + 3) - 2 * jS F (k + 3)) +
        12 * JmS F + 8 * jS F 1 + 10 * jS F 2 + 2 * pS F 2) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (pY_col_generic h k)

/-! ## The `Jm` column-sum recurrence (the equation-(4) primitive) -/

/-- The `ℕ`-level column-sum recurrence: the deep `J` mass at order `m+1`,
plus the two edge corrections, is nine times the deep mass at order `m`
plus the two head feeds. -/
private lemma jE_Jm_step_nat (F : St → Nat) (hF : ∀ g, 3 ≤ g → F (g, true) = 0) (m : Nat) :
    (∑ g ∈ Finset.Icc 3 (2 * m + 4), jE F (m + 1) g) + 3 * jE F m 3 + jE F m 4 =
      jE F m 1 + 3 * jE F m 2 + 9 * (∑ g ∈ Finset.Icc 3 (2 * m + 2), jE F m g) := by
  have hstep : ∀ g ∈ Finset.Icc 3 (2 * m + 4), jE F (m + 1) g =
      ∑ g' ∈ Finset.Icc 1 (2 * m + 2), jE F m g' * stepMul g' true g true := by
    intro g hg
    simp only [Finset.mem_Icc] at hg
    rw [jE_step F hF m g (by omega)]
    have hP : (∑ g' ∈ Finset.Icc 1 3, pE F m g' * stepMul g' false g true) = 0 := by
      apply Finset.sum_eq_zero
      intro g' _hg'
      rw [stepMul_P_to_J g' g (by omega)]; ring
    rw [hP, Nat.add_zero]
  have hsum : (∑ g ∈ Finset.Icc 3 (2 * m + 4), jE F (m + 1) g) =
      ∑ g ∈ Finset.Icc 3 (2 * m + 4), ∑ g' ∈ Finset.Icc 1 (2 * m + 2),
        jE F m g' * stepMul g' true g true :=
    Finset.sum_congr rfl hstep
  rw [hsum, Finset.sum_comm]
  have hsplit : (∑ g' ∈ Finset.Icc 1 (2 * m + 2), ∑ g ∈ Finset.Icc 3 (2 * m + 4),
      jE F m g' * stepMul g' true g true) =
      ∑ g' ∈ Finset.Icc 1 (2 * m + 2), jE F m g' *
        (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul g' true g true) := by
    apply Finset.sum_congr rfl
    intro g' _hg'
    rw [Finset.mul_sum]
  rw [hsplit, sum_Icc_one_two_split _ (2 * m + 2) (by omega)]
  have hA1 : (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul 1 true g true) = 1 := by
    have heq : (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul 1 true g true) =
        ∑ g ∈ ({3} : Finset Nat), stepMul 1 true g true := by
      apply sum_eq_of_zero_outside
      · intro g hgS hgW
        simp only [Finset.mem_singleton] at hgW
        simp only [Finset.mem_Icc] at hgS
        rw [stepMul_J_to_J_far 1 g (by omega) (by omega)]
      · intro g hgW hgS
        simp only [Finset.mem_singleton] at hgW
        subst hgW
        exact absurd (Finset.mem_Icc.mpr ⟨le_refl 3, by omega⟩) hgS
    rw [heq, Finset.sum_singleton, stepMul_1J_3J]
  have hA2 : (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul 2 true g true) = 3 := by
    have heq : (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul 2 true g true) =
        ∑ g ∈ ({3, 4} : Finset Nat), stepMul 2 true g true := by
      apply sum_eq_of_zero_outside
      · intro g hgS hgW
        simp only [Finset.mem_insert, Finset.mem_singleton] at hgW
        simp only [Finset.mem_Icc] at hgS
        rw [stepMul_J_to_J_far 2 g (by omega) (by omega)]
      · intro g hgW hgS
        simp only [Finset.mem_insert, Finset.mem_singleton] at hgW
        rcases hgW with rfl | rfl <;>
          exact absurd (Finset.mem_Icc.mpr (by omega)) hgS
    rw [heq, show ({3, 4} : Finset ℕ) = insert 3 {4} from rfl,
      Finset.sum_insert (by decide), Finset.sum_singleton, stepMul_2J_3J, stepMul_2J_4J]
  have hAgen : ∀ g' ∈ Finset.Icc 3 (2 * m + 2),
      (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul g' true g true) +
        (if g' = 3 then 3 else if g' = 4 then 1 else 0) = 9 := by
    intro g' hg'
    simp only [Finset.mem_Icc] at hg'
    obtain ⟨hg'1, hg'2⟩ := hg'
    have hrw : (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul g' true g true) =
        ∑ g ∈ Finset.Icc 3 (2 * m + 4), bulkW g' g := by
      apply Finset.sum_congr rfl
      intro g hg
      simp only [Finset.mem_Icc] at hg
      exact stepMul_J_bulk g' g (by omega) (by omega)
    rw [hrw]
    rcases Nat.lt_or_ge g' 5 with hg5 | hg5
    · interval_cases g'
      · have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 4), bulkW 3 g) =
            ∑ g ∈ Finset.Icc 3 5, bulkW 3 g := by
          apply sum_eq_of_zero_outside
          · intro g hgS hgW
            simp only [Finset.mem_Icc] at hgS hgW
            simp only [bulkW]; split_ifs with hb <;> omega
          · intro g hgW hgS
            simp only [Finset.mem_Icc] at hgW hgS
            exact absurd (⟨by omega, by omega⟩ : 3 ≤ g ∧ g ≤ 2 * m + 4) hgS
        rw [hwin, sum_Icc_three]
        have e1 : bulkW 3 3 = 3 := by simp only [bulkW]; split_ifs <;> omega
        have e2 : bulkW 3 4 = 2 := by simp only [bulkW]; split_ifs <;> omega
        have e3 : bulkW 3 5 = 1 := by simp only [bulkW]; split_ifs <;> omega
        rw [e1, e2, e3]; norm_num
      · have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 4), bulkW 4 g) =
            ∑ g ∈ Finset.Icc 3 6, bulkW 4 g := by
          apply sum_eq_of_zero_outside
          · intro g hgS hgW
            simp only [Finset.mem_Icc] at hgS hgW
            simp only [bulkW]; split_ifs with hb <;> omega
          · intro g hgW hgS
            simp only [Finset.mem_Icc] at hgW hgS
            exact absurd (⟨by omega, by omega⟩ : 3 ≤ g ∧ g ≤ 2 * m + 4) hgS
        rw [hwin, show (6 : ℕ) = 3 + 3 from rfl, sum_Icc_four]
        have e1 : bulkW 4 3 = 2 := by simp only [bulkW]; split_ifs <;> omega
        have e2 : bulkW 4 4 = 3 := by simp only [bulkW]; split_ifs <;> omega
        have e3 : bulkW 4 5 = 2 := by simp only [bulkW]; split_ifs <;> omega
        have e4 : bulkW 4 6 = 1 := by simp only [bulkW]; split_ifs <;> omega
        rw [e1, e2, e3, e4]; norm_num
    · have hif : (if g' = 3 then (3 : ℕ) else if g' = 4 then 1 else 0) = 0 := by
        rw [if_neg (by omega), if_neg (by omega)]
      rw [hif, Nat.add_zero]
      obtain ⟨k, rfl⟩ : ∃ k, g' = k + 5 := ⟨g' - 5, by omega⟩
      have hwin : (∑ g ∈ Finset.Icc 3 (2 * m + 4), bulkW (k + 5) g) =
          ∑ g ∈ Finset.Icc (k + 3) (k + 7), bulkW (k + 5) g := by
        apply sum_eq_of_zero_outside
        · intro g hgS hgW
          simp only [Finset.mem_Icc] at hgS hgW
          simp only [bulkW]; split_ifs with hb <;> omega
        · intro g hgW hgS
          simp only [Finset.mem_Icc] at hgW hgS
          exact absurd (⟨by omega, by omega⟩ : 3 ≤ g ∧ g ≤ 2 * m + 4) hgS
      rw [hwin, sum_Icc_five]
      have e1 : bulkW (k + 5) (k + 3) = 1 := by simp only [bulkW]; split_ifs <;> omega
      have e2 : bulkW (k + 5) (k + 4) = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e3 : bulkW (k + 5) (k + 5) = 3 := by simp only [bulkW]; split_ifs <;> omega
      have e4 : bulkW (k + 5) (k + 6) = 2 := by simp only [bulkW]; split_ifs <;> omega
      have e5 : bulkW (k + 5) (k + 7) = 1 := by simp only [bulkW]; split_ifs <;> omega
      rw [e1, e2, e3, e4, e5]
  have hgen : (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g' *
      (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul g' true g true)) + 3 * jE F m 3 + jE F m 4 =
      9 * (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g') := by
    have hpt : (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g' *
        (∑ g ∈ Finset.Icc 3 (2 * m + 4), stepMul g' true g true)) +
        (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g' *
          (if g' = 3 then 3 else if g' = 4 then 1 else 0)) =
        9 * (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g') := by
      rw [← Finset.sum_add_distrib, Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro g' hg'
      rw [← Nat.mul_add, hAgen g' hg']; ring
    have hcorr : (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g' *
        (if g' = 3 then 3 else if g' = 4 then 1 else 0)) = 3 * jE F m 3 + jE F m 4 := by
      have hwin : (∑ g' ∈ Finset.Icc 3 (2 * m + 2), jE F m g' *
          (if g' = 3 then (3 : ℕ) else if g' = 4 then 1 else 0)) =
          ∑ g' ∈ ({3, 4} : Finset Nat), jE F m g' *
            (if g' = 3 then (3 : ℕ) else if g' = 4 then 1 else 0) := by
        apply sum_eq_of_zero_outside
        · intro g' hg'S hg'W
          simp only [Finset.mem_insert, Finset.mem_singleton] at hg'W
          rw [if_neg (by omega), if_neg (by omega)]; ring
        · intro g' hg'W hg'S
          simp only [Finset.mem_insert, Finset.mem_singleton] at hg'W
          simp only [Finset.mem_Icc] at hg'S
          rcases hg'W with rfl | rfl
          · rw [jE_support F hF m 3 (by omega)]; ring
          · rw [jE_support F hF m 4 (by omega)]; ring
      rw [hwin, show ({3, 4} : Finset ℕ) = insert 3 {4} from rfl,
        Finset.sum_insert (by decide), Finset.sum_singleton]
      have e1 : (if (3 : ℕ) = 3 then (3 : ℕ) else if 3 = 4 then 1 else 0) = 3 := by norm_num
      have e2 : (if (4 : ℕ) = 3 then (3 : ℕ) else if 4 = 4 then 1 else 0) = 1 := by norm_num
      rw [e1, e2]; ring
    omega
  rw [hA1, hA2, Nat.mul_one]
  omega

/-! ### Coefficient bookkeeping for small numerals -/

private lemma coeff_3mulS (S : PowerSeries ℚ) (m : Nat) :
    coeff m (3 * S) = 3 * coeff m S := by
  rw [show (3 : PowerSeries ℚ) = C 3 from (map_ofNat C 3).symm, coeff_C_mul]

private lemma coeff_9mulS (S : PowerSeries ℚ) (m : Nat) :
    coeff m (9 * S) = 9 * coeff m S := by
  rw [show (9 : PowerSeries ℚ) = C 9 from (map_ofNat C 9).symm, coeff_C_mul]

/-- Summing the generic `J`-columns: the deep mass steps by `9×` itself
with window-edge corrections and the two head feeds. -/
theorem JmY_step {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmY F = X * (jY F 1 + 3 * jY F 2 + 9 * JmY F - 3 * jY F 3 -
      jY F 4) := by
  apply PowerSeries.ext
  intro n
  cases n with
  | zero =>
    rw [coeff_JmY, show Finset.Icc 3 (2 * 0 + 2) = (∅ : Finset ℕ) from
        Finset.Icc_eq_empty (by omega), Finset.sum_empty,
      PowerSeries.coeff_zero_X_mul]
  | succ m =>
    rw [coeff_JmY, show 2 * (m + 1) + 2 = 2 * m + 4 from by ring,
      PowerSeries.coeff_succ_X_mul]
    simp only [map_add, map_sub, coeff_3mulS, coeff_9mulS, coeff_jY, coeff_JmY]
    have hn := jE_Jm_step_nat F h.deep_j m
    have hq := congrArg (fun z : ℕ => (z : ℚ)) hn
    push_cast at hq
    linarith [hq]

/-- `JmY_step`, transported. -/
theorem JmS_step {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmS F = X ^ 2 * (jS F 1 + 3 * jS F 2 + 9 * JmS F - 3 * jS F 3 -
      jS F 4) := by
  simpa [jS, pS, JmS, e2, map_add, map_sub, map_mul, map_ofNat, PowerSeries.expand_C,
    PowerSeries.expand_X] using congrArg e2 (JmY_step h)

/-! ## Evaluated series -/

/-- The `J₃` column family: gaps `≥ 3` only. -/
noncomputable def colJ3 (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  if g < 3 then 0 else jS F g

/-- The `P₃` column family: gaps `≥ 3` only. -/
noncomputable def colP3 (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  if g < 3 then 0 else pS F g

/-- The weighted `J₃` family (`u`-derivative bookkeeping): weight `g`. -/
noncomputable def colJ3W (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  if g < 3 then 0 else C (g : ℚ) * jS F g

/-- `J₃` evaluated at `u`: `Σ_{g≥3} ĵ_g·u^g`. -/
noncomputable def J3ser (F : St → Nat) (u : PowerSeries ℚ) : PowerSeries ℚ :=
  lfsum fun g => colJ3 F g * u ^ g

/-- `P₃` evaluated at `u`. -/
noncomputable def P3ser (F : St → Nat) (u : PowerSeries ℚ) : PowerSeries ℚ :=
  lfsum fun g => colP3 F g * u ^ g

/-- The combined `P₃ − 2J₃` column family (gaps `≥ 3` only): the `pS_col_*`
identities are already stated in terms of these paired differences. -/
private noncomputable def colPJ3 (F : St → Nat) (g : Nat) : PowerSeries ℚ :=
  if g < 3 then 0 else pS F g - 2 * jS F g

/-- `P₃(u) − 2J₃(u)` as a single `lfsum` over `colPJ3`. -/
private lemma P3ser_sub_two_J3ser (F : St → Nat) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    P3ser F u - 2 * J3ser F u = lfsum (fun g => colPJ3 F g * u ^ g) := by
  unfold P3ser J3ser
  rw [lfsum_mul_left (2 : PowerSeries ℚ) (fun g => colJ3 F g * u ^ g) (locFin_geom (colJ3 F) u hu),
    ← lfsum_sub]
  congr 1
  funext g
  simp only [colPJ3, colP3, colJ3]
  split_ifs <;> ring

/-- The weighted evaluation `Σ_{g≥3} g·ĵ_g·u^g`. -/
noncomputable def J3serW (F : St → Nat) (u : PowerSeries ℚ) : PowerSeries ℚ :=
  lfsum fun g => colJ3W F g * u ^ g

/-- Geometric collapse against a certified inverse:
`Σ_{g ≥ K} u^g = u^K·w`. -/
theorem lfsum_geom (u w : PowerSeries ℚ) (hu : constantCoeff u = 0)
    (hw : (1 - u) * w = 1) (K : Nat) :
    lfsum (fun g => (if g < K then 0 else 1) * u ^ g) = u ^ K * w := by
  have hS_locfin : LocFin (fun g => u ^ g) := by
    have h := locFin_geom (fun _ => (1 : PowerSeries ℚ)) u hu
    simpa only [one_mul] using h
  have hshiftA : ∀ K : Nat, lfsum (fun g => (if g < K then (0 : PowerSeries ℚ) else 1) * u ^ g) =
      u ^ K * lfsum (fun g => u ^ g) := by
    intro K
    have hGK : LocFin (fun g => (if g < K then (0 : PowerSeries ℚ) else 1) * u ^ g) :=
      locFin_geom _ u hu
    rw [lfsum_shift _ hGK K (fun g hg => by simp [if_pos hg])]
    have heq : (fun g => (if g + K < K then (0 : PowerSeries ℚ) else 1) * u ^ (g + K)) =
        fun g => u ^ K * u ^ g := by
      funext g
      rw [if_neg (by omega), one_mul, pow_add, mul_comm]
    rw [heq]
    exact (lfsum_mul_left (u ^ K) (fun g => u ^ g) hS_locfin).symm
  set S := lfsum (fun g => u ^ g) with hSdef
  have hD0 : lfsum (fun g => (if g < 0 then (0 : PowerSeries ℚ) else 1) * u ^ g) -
      lfsum (fun g => (if g < 1 then (0 : PowerSeries ℚ) else 1) * u ^ g) = 1 := by
    rw [← lfsum_sub]
    have heq : (fun g => (if g < 0 then (0 : PowerSeries ℚ) else 1) * u ^ g -
        (if g < 1 then (0 : PowerSeries ℚ) else 1) * u ^ g) =
        (fun g => if g = 0 then (1 : PowerSeries ℚ) else 0) := by
      funext g
      rcases g with _ | g <;> simp
    rw [heq]
    have hDlocfin : LocFin (fun g => if g = 0 then (1 : PowerSeries ℚ) else 0) := by
      intro g n hn
      rcases g with _ | g
      · omega
      · simp
    rw [lfsum_of_support_lt _ hDlocfin 1 (fun g hg => by simp [show g ≠ 0 from by omega])]
    simp
  have hS0 : lfsum (fun g => (if g < 0 then (0 : PowerSeries ℚ) else 1) * u ^ g) = S := by
    have h0 := hshiftA 0
    simpa using h0
  have hS1 : lfsum (fun g => (if g < 1 then (0 : PowerSeries ℚ) else 1) * u ^ g) = u * S := by
    have h1 := hshiftA 1
    simpa using h1
  rw [hS0, hS1] at hD0
  have hSw : (1 - u) * S = 1 := by linear_combination hD0
  have h1u_ne : (1 - u : PowerSeries ℚ) ≠ 0 := by
    intro h
    rw [h, zero_mul] at hw
    exact zero_ne_one hw
  have heqmul : (1 - u) * (S - w) = 0 := by rw [mul_sub, hSw, hw]; ring
  have hSeqw : S = w := by
    rcases mul_eq_zero.mp heqmul with h | h
    · exact absurd h h1u_ne
    · exact sub_eq_zero.mp h
  rw [hshiftA K, hSeqw]

/-- A constant times a geometric tail, as a single shifted `lfsum`. -/
private lemma const_mul_geom_tail (c u w : PowerSeries ℚ) (hu : constantCoeff u = 0)
    (hw : (1 - u) * w = 1) (K : Nat) :
    c * (u ^ K * w) = lfsum (fun n => (if n < K then 0 else c) * u ^ n) := by
  rw [← lfsum_geom u w hu hw K,
    lfsum_mul_left c (fun g => (if g < K then (0 : PowerSeries ℚ) else 1) * u ^ g)
      (locFin_geom (fun g => if g < K then (0 : PowerSeries ℚ) else 1) u hu)]
  congr 1
  funext n
  split_ifs <;> ring

/-! ## The right-side polynomials -/

/-- `R_J` column 1. -/
noncomputable def c1S (F : St → Nat) : PowerSeries ℚ :=
  -2 * jS F 3 + 8 * JmS F + 5 * jS F 1 + 6 * jS F 2 + pS F 3 + 2 * pS F 2

/-- `R_J` column 2. -/
noncomputable def c2S (F : St → Nat) : PowerSeries ℚ :=
  2 * JmS F + 2 * jS F 1 + 3 * jS F 2 + 2 * pS F 2

/-- `R_J` column 3. -/
noncomputable def c3S (F : St → Nat) : PowerSeries ℚ := jS F 1 + 2 * jS F 2

/-- `R_J` column 4. -/
noncomputable def c4S (F : St → Nat) : PowerSeries ℚ := jS F 2

/-- `Q(u) = J0(u) − j₁u − j₂u² + y·R_J(u)`. -/
noncomputable def Qser (F : St → Nat) (j01 j02 : Nat) (u : PowerSeries ℚ) :
    PowerSeries ℚ :=
  C (j01 : ℚ) * u + C (j02 : ℚ) * u ^ 2 - jS F 1 * u - jS F 2 * u ^ 2 +
    X ^ 2 * (c1S F * u + c2S F * u ^ 2 + c3S F * u ^ 3 + c4S F * u ^ 4)

/-- `Q′(u)`, the `u`-derivative of `Qser`. -/
noncomputable def Qpser (F : St → Nat) (j01 j02 : Nat) (u : PowerSeries ℚ) :
    PowerSeries ℚ :=
  C (j01 : ℚ) + 2 * C (j02 : ℚ) * u - jS F 1 - 2 * jS F 2 * u +
    X ^ 2 * (c1S F + 2 * c2S F * u + 3 * c3S F * u ^ 2 +
      4 * c4S F * u ^ 3)

/-- `R_P(u)` against a certified inverse `w = (1−u)⁻¹`. -/
noncomputable def RPser (F : St → Nat) (u w : PowerSeries ℚ) :
    PowerSeries ℚ :=
  (2 * jS F 3 - pS F 3) * u +
    JmS F * (8 * u ^ 2 + 12 * u ^ 3 * w) +
    jS F 1 * (4 * u ^ 2 + 6 * u ^ 3 + 8 * u ^ 4 * w) +
    jS F 2 * (4 * u ^ 2 + 6 * u ^ 3 + 8 * u ^ 4 + 10 * u ^ 5 * w) +
    pS F 2 * (u ^ 2 + 4 * u ^ 3 + 3 * u ^ 4 + 2 * u ^ 5 * w)

/-- `P0(u) = p02·u² + pt·u³/(1−u)`, both starts uniformly. -/
noncomputable def P0ser (p02 pt : Nat) (u w : PowerSeries ℚ) :
    PowerSeries ℚ :=
  C (p02 : ℚ) * u ^ 2 + C (pt : ℚ) * u ^ 3 * w

/-! ### The shifted-window `lfsum` toolkit -/

/-- `u^c` times an `lfsum` reindexes the family by `c` (zero below `c`). -/
private lemma lfsum_shift_mul (a : ℕ → PowerSeries ℚ) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) (c : ℕ) :
    u ^ c * lfsum (fun g => a g * u ^ g) =
      lfsum (fun n => (if n < c then 0 else a (n - c)) * u ^ n) := by
  have ha : LocFin (fun g => a g * u ^ g) := locFin_geom a u hu
  have hshift : LocFin (fun n => (if n < c then (0 : PowerSeries ℚ) else a (n - c)) * u ^ n) :=
    locFin_geom (fun n => if n < c then 0 else a (n - c)) u hu
  rw [lfsum_shift _ hshift c (fun g hg => by simp [if_pos hg])]
  have heq : (fun g => (if g + c < c then (0 : PowerSeries ℚ) else a (g + c - c)) * u ^ (g + c)) =
      fun g => u ^ c * (a g * u ^ g) := by
    funext g
    rw [if_neg (by omega), show g + c - c = g from by omega, pow_add]
    ring
  rw [heq]
  exact lfsum_mul_left (u ^ c) (fun g => a g * u ^ g) ha

/-- A finitely-supported family (zero from `K` on) collapses `lfsum` to its
explicit finite sum, backwards: build an `lfsum` from a finite polynomial. -/
private lemma lfsum_eq_of_finite (F : ℕ → PowerSeries ℚ) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) (K : Nat) (h : ∀ g, K ≤ g → F g = 0) :
    lfsum (fun n => F n * u ^ n) = ∑ g ∈ Finset.range K, F g * u ^ g :=
  lfsum_of_support_lt (fun n => F n * u ^ n) (locFin_geom F u hu) K
    (fun g hg => by rw [h g hg, zero_mul])

/-! ## The three evaluated master identities (generic `u`, premultiplied) -/

/-- The `J`-master evaluated at any `u` of positive order:
`u²·(D(u)·J₃(u)) = u²·(u²·Q(u))`. -/
theorem master_J {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    u ^ 2 * ((u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3ser F u) =
      u ^ 2 * (u ^ 2 * Qser F j01 j02 u) := by
  have hcore : (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3ser F u =
      u ^ 2 * Qser F j01 j02 u := by
    set a : ℕ → PowerSeries ℚ := colJ3 F with hadef
    set F1 : ℕ → PowerSeries ℚ := fun n => if n < 1 then 0 else a (n - 1) with hF1def
    set F2 : ℕ → PowerSeries ℚ := fun n => if n < 2 then 0 else a (n - 2) with hF2def
    set F3 : ℕ → PowerSeries ℚ := fun n => if n < 3 then 0 else a (n - 3) with hF3def
    set F4 : ℕ → PowerSeries ℚ := fun n => if n < 4 then 0 else a (n - 4) with hF4def
    have hJ3 : J3ser F u = lfsum (fun g => a g * u ^ g) := rfl
    have e1 : u ^ 1 * J3ser F u = lfsum (fun n => F1 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 1
    have e2 : u ^ 2 * J3ser F u = lfsum (fun n => F2 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 2
    have e3 : u ^ 3 * J3ser F u = lfsum (fun n => F3 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 3
    have e4 : u ^ 4 * J3ser F u = lfsum (fun n => F4 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 4
    have hexpand : (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3ser F u =
        u ^ 2 * J3ser F u - X ^ 2 * J3ser F u - (2 * X ^ 2) * (u ^ 1 * J3ser F u) -
          (3 * X ^ 2) * (u ^ 2 * J3ser F u) - (2 * X ^ 2) * (u ^ 3 * J3ser F u) -
          X ^ 2 * (u ^ 4 * J3ser F u) := by ring
    rw [e1, e2, e3, e4, hJ3] at hexpand
    -- The finite right-side family.
    set rhsF : ℕ → PowerSeries ℚ := fun n =>
      if n = 3 then C (j01 : ℚ) - jS F 1 + X ^ 2 * c1S F
      else if n = 4 then C (j02 : ℚ) - jS F 2 + X ^ 2 * c2S F
      else if n = 5 then X ^ 2 * c3S F
      else if n = 6 then X ^ 2 * c4S F
      else 0 with hrhsFdef
    have hrhs : u ^ 2 * Qser F j01 j02 u = lfsum (fun n => rhsF n * u ^ n) := by
      have hfin : ∀ g, 7 ≤ g → rhsF g = 0 := by
        intro g hg
        simp only [hrhsFdef]
        rw [if_neg (by omega), if_neg (by omega), if_neg (by omega), if_neg (by omega)]
      rw [lfsum_eq_of_finite rhsF u hu 7 hfin]
      simp only [Finset.sum_range_succ, Finset.sum_range_zero, hrhsFdef]
      norm_num [Qser]
      ring
    have hfinal : lfsum (fun n => F2 n * u ^ n) - X ^ 2 * lfsum (fun n => a n * u ^ n) -
        (2 * X ^ 2) * lfsum (fun n => F1 n * u ^ n) -
        (3 * X ^ 2) * lfsum (fun n => F2 n * u ^ n) -
        (2 * X ^ 2) * lfsum (fun n => F3 n * u ^ n) -
        X ^ 2 * lfsum (fun n => F4 n * u ^ n) = lfsum (fun n => rhsF n * u ^ n) := by
      rw [lfsum_mul_left (X ^ 2) (fun n => a n * u ^ n) (locFin_geom a u hu),
        lfsum_mul_left (2 * X ^ 2) (fun n => F1 n * u ^ n) (locFin_geom F1 u hu),
        lfsum_mul_left (3 * X ^ 2) (fun n => F2 n * u ^ n) (locFin_geom F2 u hu),
        lfsum_mul_left (2 * X ^ 2) (fun n => F3 n * u ^ n) (locFin_geom F3 u hu),
        lfsum_mul_left (X ^ 2) (fun n => F4 n * u ^ n) (locFin_geom F4 u hu)]
      rw [← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub]
      congr 1
      funext n
      have hcase : F2 n - X ^ 2 * a n - (2 * X ^ 2) * F1 n - (3 * X ^ 2) * F2 n -
          (2 * X ^ 2) * F3 n - X ^ 2 * F4 n = rhsF n := by
        simp only [hF1def, hF2def, hF3def, hF4def, hadef, hrhsFdef, colJ3, c1S, c2S, c3S, c4S]
        rcases Nat.lt_or_ge n 7 with hn7 | hn7
        · interval_cases n
          · norm_num
          · norm_num
          · norm_num
          · norm_num
            have j1 := jS_col_one h
            simp only [map_natCast] at j1
            linear_combination j1
          · norm_num
            have j2 := jS_col_two h
            simp only [map_natCast] at j2
            linear_combination j2
          · norm_num
            linear_combination jS_col_three h
          · norm_num
            linear_combination jS_col_four h

        · obtain ⟨k, rfl⟩ : ∃ k, n = k + 7 := ⟨n - 7, by omega⟩
          have hk3 : k + 7 - 2 = k + 5 := by omega
          have hk1 : k + 7 - 1 = k + 6 := by omega
          have hk2 : k + 7 - 3 = k + 4 := by omega
          have hk4 : k + 7 - 4 = k + 3 := by omega
          rw [if_neg (show ¬ k + 7 < 2 by omega), if_neg (show ¬ k + 7 < 1 by omega),
            if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 7 < 4 by omega)]
          rw [hk3, hk1, hk2, hk4]
          rw [if_neg (show ¬ k + 5 < 3 by omega), if_neg (show ¬ k + 6 < 3 by omega),
            if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 4 < 3 by omega),
            if_neg (show ¬ k + 3 < 3 by omega)]
          rw [if_neg (show k + 7 ≠ 3 by omega), if_neg (show k + 7 ≠ 4 by omega),
            if_neg (show k + 7 ≠ 5 by omega), if_neg (show k + 7 ≠ 6 by omega)]
          linear_combination jS_col_generic h k
      linear_combination hcase * u ^ n
    rw [hJ3, hexpand, hfinal]
    exact hrhs.symm
  rw [hcore]

/-! ### Reusable pieces of the `J`-master, exposed for the derivative and
`P`-master proofs (duplicated bookkeeping from `master_J`'s proof, kept in
lockstep with it — do not edit `master_J` itself). -/

/-- The finite right-side family of the `J`-master (same as `master_J`'s
local `rhsF`, exposed at top level). -/
private noncomputable def rhsFJ (F : St → Nat) (j01 j02 : Nat) : ℕ → PowerSeries ℚ :=
  fun n =>
    if n = 3 then C (j01 : ℚ) - jS F 1 + X ^ 2 * c1S F
    else if n = 4 then C (j02 : ℚ) - jS F 2 + X ^ 2 * c2S F
    else if n = 5 then X ^ 2 * c3S F
    else if n = 6 then X ^ 2 * c4S F
    else 0

private lemma rhsFJ_support (F : St → Nat) (j01 j02 : Nat) :
    ∀ g, 7 ≤ g → rhsFJ F j01 j02 g = 0 := by
  intro g hg
  simp only [rhsFJ]
  rw [if_neg (by omega), if_neg (by omega), if_neg (by omega), if_neg (by omega)]

/-- The pointwise bracket identity behind `master_J` (same as its local
`hcase`, exposed at top level, `n` fully generic). -/
private lemma colJ3_case {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (n : ℕ) :
    (if n < 2 then (0 : PowerSeries ℚ) else colJ3 F (n - 2)) - X ^ 2 * colJ3 F n -
      (2 * X ^ 2) * (if n < 1 then 0 else colJ3 F (n - 1)) -
      (3 * X ^ 2) * (if n < 2 then 0 else colJ3 F (n - 2)) -
      (2 * X ^ 2) * (if n < 3 then 0 else colJ3 F (n - 3)) -
      X ^ 2 * (if n < 4 then 0 else colJ3 F (n - 4)) = rhsFJ F j01 j02 n := by
  simp only [rhsFJ, colJ3, c1S, c2S, c3S, c4S]
  rcases Nat.lt_or_ge n 7 with hn7 | hn7
  · interval_cases n
    · norm_num
    · norm_num
    · norm_num
    · norm_num
      have j1 := jS_col_one h
      simp only [map_natCast] at j1
      linear_combination j1
    · norm_num
      have j2 := jS_col_two h
      simp only [map_natCast] at j2
      linear_combination j2
    · norm_num
      linear_combination jS_col_three h
    · norm_num
      linear_combination jS_col_four h
  · obtain ⟨k, rfl⟩ : ∃ k, n = k + 7 := ⟨n - 7, by omega⟩
    have hk3 : k + 7 - 2 = k + 5 := by omega
    have hk1 : k + 7 - 1 = k + 6 := by omega
    have hk2 : k + 7 - 3 = k + 4 := by omega
    have hk4 : k + 7 - 4 = k + 3 := by omega
    rw [if_neg (show ¬ k + 7 < 2 by omega), if_neg (show ¬ k + 7 < 1 by omega),
      if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 7 < 4 by omega)]
    rw [hk3, hk1, hk2, hk4]
    rw [if_neg (show ¬ k + 5 < 3 by omega), if_neg (show ¬ k + 6 < 3 by omega),
      if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 4 < 3 by omega),
      if_neg (show ¬ k + 3 < 3 by omega)]
    rw [if_neg (show k + 7 ≠ 3 by omega), if_neg (show k + 7 ≠ 4 by omega),
      if_neg (show k + 7 ≠ 5 by omega), if_neg (show k + 7 ≠ 6 by omega)]
    linear_combination jS_col_generic h k

/-- The pointwise bracket identity behind `master_P`: the `colPJ3`-window
bracket equals the finite `pS_col_*` heads, the geometric-tail constants
(grouped by their `w`-shift threshold), and the `−2·colJ3` shift member
that the `−2·J3ser` right-side term contributes. -/
private lemma colPJ3_case {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (n : ℕ) :
    (if n < 2 then (0 : PowerSeries ℚ) else colPJ3 F (n - 2)) - X ^ 2 * colPJ3 F n -
      2 * X ^ 2 * (if n < 1 then 0 else colPJ3 F (n - 1)) -
      3 * X ^ 2 * (if n < 2 then 0 else colPJ3 F (n - 2)) -
      2 * X ^ 2 * (if n < 3 then 0 else colPJ3 F (n - 3)) -
      X ^ 2 * (if n < 4 then 0 else colPJ3 F (n - 4)) =
    (if n = 3 then X ^ 2 * (2 * jS F 3 - pS F 3)
      else if n = 4 then C (p02 : ℚ) - pS F 2 +
        X ^ 2 * (8 * JmS F + 4 * jS F 1 + 4 * jS F 2 + pS F 2)
      else if n = 5 then X ^ 2 * (6 * jS F 1 + 6 * jS F 2 + 4 * pS F 2)
      else if n = 6 then X ^ 2 * (8 * jS F 2 + 3 * pS F 2)
      else 0)
      + (if n < 5 then (0 : PowerSeries ℚ) else C (pt : ℚ) + 12 * X ^ 2 * JmS F)
      + (if n < 6 then (0 : PowerSeries ℚ) else 8 * X ^ 2 * jS F 1)
      + (if n < 7 then (0 : PowerSeries ℚ) else 10 * X ^ 2 * jS F 2 + 2 * X ^ 2 * pS F 2)
      - 2 * (if n < 2 then (0 : PowerSeries ℚ) else colJ3 F (n - 2)) := by
  rcases Nat.lt_or_ge n 7 with hn7 | hn7
  · interval_cases n
    · norm_num [colPJ3, colJ3]
    · norm_num [colPJ3, colJ3]
    · norm_num [colPJ3, colJ3]
    · -- n = 3
      norm_num [colPJ3, colJ3]
      ring
    · -- n = 4
      norm_num [colPJ3, colJ3]
      have p2 := pS_col_two h
      simp only [map_natCast] at p2
      linear_combination p2
    · -- n = 5
      norm_num [colPJ3, colJ3]
      have p3 := pS_col_three h
      simp only [map_natCast] at p3
      linear_combination p3
    · -- n = 6
      norm_num [colPJ3, colJ3]
      have p4 := pS_col_four h
      simp only [map_natCast] at p4
      linear_combination p4
  · obtain ⟨k, rfl⟩ : ∃ k, n = k + 7 := ⟨n - 7, by omega⟩
    have hk3 : k + 7 - 2 = k + 5 := by omega
    have hk1 : k + 7 - 1 = k + 6 := by omega
    have hk2 : k + 7 - 3 = k + 4 := by omega
    have hk4 : k + 7 - 4 = k + 3 := by omega
    rw [if_neg (show ¬ k + 7 < 2 by omega), if_neg (show ¬ k + 7 < 1 by omega),
      if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 7 < 4 by omega),
      hk3, hk1, hk2, hk4,
      if_neg (show k + 7 ≠ 3 by omega), if_neg (show k + 7 ≠ 4 by omega),
      if_neg (show k + 7 ≠ 5 by omega), if_neg (show k + 7 ≠ 6 by omega),
      if_neg (show ¬ k + 7 < 5 by omega), if_neg (show ¬ k + 7 < 6 by omega),
      if_neg (show ¬ k + 7 < 7 by omega), if_neg (show ¬ k + 7 < 2 by omega)]
    have pgen := pS_col_generic h k
    simp only [map_natCast] at pgen
    simp only [colPJ3, colJ3, map_natCast]
    rw [if_neg (show ¬ k + 5 < 3 by omega), if_neg (show ¬ k + 6 < 3 by omega),
      if_neg (show ¬ k + 7 < 3 by omega), if_neg (show ¬ k + 4 < 3 by omega),
      if_neg (show ¬ k + 3 < 3 by omega), if_neg (show ¬ k + 5 < 3 by omega)]
    linear_combination pgen

/-- Pure weight bookkeeping: multiplying the shifted-window bracket by the
weight `C n` distributes correctly against the derivative bracket built
from `C (n − i)`-weighted shifts (`i = 0, 1, 2, 3, 4`), for *any* family
`a`. No column identity is needed here — it is index arithmetic in the
weight only, so it is proved for a fully generic `a`. -/
private lemma weight_shift_bracket (a : ℕ → PowerSeries ℚ) (n : ℕ) :
    (if n < 2 then (0 : PowerSeries ℚ) else C (((n - 2 : ℕ) : ℚ)) * a (n - 2)) -
        X ^ 2 * (C (n : ℚ) * a n) -
      2 * X ^ 2 * (if n < 1 then 0 else C (((n - 1 : ℕ) : ℚ)) * a (n - 1)) -
      3 * X ^ 2 * (if n < 2 then 0 else C (((n - 2 : ℕ) : ℚ)) * a (n - 2)) -
      2 * X ^ 2 * (if n < 3 then 0 else C (((n - 3 : ℕ) : ℚ)) * a (n - 3)) -
      X ^ 2 * (if n < 4 then 0 else C (((n - 4 : ℕ) : ℚ)) * a (n - 4)) +
      (2 * (if n < 2 then (0 : PowerSeries ℚ) else a (n - 2)) -
        2 * X ^ 2 * (if n < 1 then 0 else a (n - 1)) -
        6 * X ^ 2 * (if n < 2 then 0 else a (n - 2)) -
        6 * X ^ 2 * (if n < 3 then 0 else a (n - 3)) -
        4 * X ^ 2 * (if n < 4 then 0 else a (n - 4))) =
      C (n : ℚ) *
        ((if n < 2 then (0 : PowerSeries ℚ) else a (n - 2)) - X ^ 2 * a n -
          2 * X ^ 2 * (if n < 1 then 0 else a (n - 1)) -
          3 * X ^ 2 * (if n < 2 then 0 else a (n - 2)) -
          2 * X ^ 2 * (if n < 3 then 0 else a (n - 3)) -
          X ^ 2 * (if n < 4 then 0 else a (n - 4))) := by
  rcases Nat.lt_or_ge n 4 with hn4 | hn4
  · interval_cases n <;> norm_num [map_natCast, map_ofNat] <;> ring
  · have h1 : (((n - 1 : ℕ) : ℚ)) = (n : ℚ) - 1 := by
      rw [Nat.cast_sub (by omega)]; norm_num
    have h2 : (((n - 2 : ℕ) : ℚ)) = (n : ℚ) - 2 := by
      rw [Nat.cast_sub (by omega)]; norm_num
    have h3 : (((n - 3 : ℕ) : ℚ)) = (n : ℚ) - 3 := by
      rw [Nat.cast_sub (by omega)]; norm_num
    have h4 : (((n - 4 : ℕ) : ℚ)) = (n : ℚ) - 4 := by
      rw [Nat.cast_sub (by omega)]; norm_num
    simp only [if_neg (show ¬ n < 1 by omega), if_neg (show ¬ n < 2 by omega),
      if_neg (show ¬ n < 3 by omega), if_neg (show ¬ n < 4 by omega)]
    rw [h1, h2, h3, h4]
    simp only [map_sub, map_ofNat, map_one]
    ring

/-- The `P`-master evaluated at any `u` of positive order. -/
theorem master_P {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u w : PowerSeries ℚ)
    (hu : constantCoeff u = 0) (hw : (1 - u) * w = 1) :
    u ^ 2 * ((u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) *
        (P3ser F u - 2 * J3ser F u)) =
      u ^ 2 * (u ^ 2 * (P0ser p02 pt u w - pS F 2 * u ^ 2 -
        2 * J3ser F u + X ^ 2 * RPser F u w)) := by
  have hcore : (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * (P3ser F u - 2 * J3ser F u) =
      u ^ 2 * (P0ser p02 pt u w - pS F 2 * u ^ 2 -
        2 * J3ser F u + X ^ 2 * RPser F u w) := by
    set b : ℕ → PowerSeries ℚ := colPJ3 F with hbdef
    set G1 : ℕ → PowerSeries ℚ := fun n => if n < 1 then 0 else b (n - 1) with hG1def
    set G2 : ℕ → PowerSeries ℚ := fun n => if n < 2 then 0 else b (n - 2) with hG2def
    set G3 : ℕ → PowerSeries ℚ := fun n => if n < 3 then 0 else b (n - 3) with hG3def
    set G4 : ℕ → PowerSeries ℚ := fun n => if n < 4 then 0 else b (n - 4) with hG4def
    have hcomb : P3ser F u - 2 * J3ser F u = lfsum (fun g => b g * u ^ g) :=
      P3ser_sub_two_J3ser F u hu
    have e1 : u ^ 1 * (P3ser F u - 2 * J3ser F u) = lfsum (fun n => G1 n * u ^ n) := by
      rw [hcomb]; exact lfsum_shift_mul b u hu 1
    have e2 : u ^ 2 * (P3ser F u - 2 * J3ser F u) = lfsum (fun n => G2 n * u ^ n) := by
      rw [hcomb]; exact lfsum_shift_mul b u hu 2
    have e3 : u ^ 3 * (P3ser F u - 2 * J3ser F u) = lfsum (fun n => G3 n * u ^ n) := by
      rw [hcomb]; exact lfsum_shift_mul b u hu 3
    have e4 : u ^ 4 * (P3ser F u - 2 * J3ser F u) = lfsum (fun n => G4 n * u ^ n) := by
      rw [hcomb]; exact lfsum_shift_mul b u hu 4
    have hexpand : (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * (P3ser F u - 2 * J3ser F u) =
        u ^ 2 * (P3ser F u - 2 * J3ser F u) - X ^ 2 * (P3ser F u - 2 * J3ser F u) -
          (2 * X ^ 2) * (u ^ 1 * (P3ser F u - 2 * J3ser F u)) -
          (3 * X ^ 2) * (u ^ 2 * (P3ser F u - 2 * J3ser F u)) -
          (2 * X ^ 2) * (u ^ 3 * (P3ser F u - 2 * J3ser F u)) -
          X ^ 2 * (u ^ 4 * (P3ser F u - 2 * J3ser F u)) := by ring
    rw [e1, e2, e3, e4, hcomb] at hexpand
    -- The right side: finite polynomial heads, three geometric-tail
    -- constants, and the `−2·J3ser` shifted family.
    set finF : ℕ → PowerSeries ℚ := fun n =>
      if n = 3 then X ^ 2 * (2 * jS F 3 - pS F 3)
      else if n = 4 then C (p02 : ℚ) - pS F 2 +
        X ^ 2 * (8 * JmS F + 4 * jS F 1 + 4 * jS F 2 + pS F 2)
      else if n = 5 then X ^ 2 * (6 * jS F 1 + 6 * jS F 2 + 4 * pS F 2)
      else if n = 6 then X ^ 2 * (8 * jS F 2 + 3 * pS F 2)
      else 0 with hfinFdef
    set shiftF : ℕ → PowerSeries ℚ := fun n => if n < 2 then 0 else colJ3 F (n - 2) with
      hshiftFdef
    have hJ3u : J3ser F u = lfsum (fun g => colJ3 F g * u ^ g) := rfl
    have eShift : u ^ 2 * J3ser F u = lfsum (fun n => shiftF n * u ^ n) := by
      rw [hJ3u]; exact lfsum_shift_mul (colJ3 F) u hu 2
    have hfinFfin : ∀ g, 7 ≤ g → finF g = 0 := by
      intro g hg
      simp only [hfinFdef]
      rw [if_neg (by omega), if_neg (by omega), if_neg (by omega), if_neg (by omega)]
    have hfinlf : (C (p02 : ℚ) * u ^ 4 - pS F 2 * u ^ 4 +
        X ^ 2 * (2 * jS F 3 - pS F 3) * u ^ 3 + X ^ 2 * JmS F * 8 * u ^ 4 +
        X ^ 2 * jS F 1 * (4 * u ^ 4 + 6 * u ^ 5) +
        X ^ 2 * jS F 2 * (4 * u ^ 4 + 6 * u ^ 5 + 8 * u ^ 6) +
        X ^ 2 * pS F 2 * (u ^ 4 + 4 * u ^ 5 + 3 * u ^ 6)) =
        lfsum (fun n => finF n * u ^ n) := by
      rw [lfsum_eq_of_finite finF u hu 7 hfinFfin]
      simp only [Finset.sum_range_succ, Finset.sum_range_zero, hfinFdef]
      norm_num
      ring
    have htail1 : (C (pt : ℚ) + 12 * X ^ 2 * JmS F) * (u ^ 5 * w) =
        lfsum (fun n => (if n < 5 then (0 : PowerSeries ℚ) else
          C (pt : ℚ) + 12 * X ^ 2 * JmS F) * u ^ n) :=
      const_mul_geom_tail _ u w hu hw 5
    have htail2 : (8 * X ^ 2 * jS F 1) * (u ^ 6 * w) =
        lfsum (fun n => (if n < 6 then (0 : PowerSeries ℚ) else 8 * X ^ 2 * jS F 1) * u ^ n) :=
      const_mul_geom_tail _ u w hu hw 6
    have htail3 : (10 * X ^ 2 * jS F 2 + 2 * X ^ 2 * pS F 2) * (u ^ 7 * w) =
        lfsum (fun n => (if n < 7 then (0 : PowerSeries ℚ) else
          10 * X ^ 2 * jS F 2 + 2 * X ^ 2 * pS F 2) * u ^ n) :=
      const_mul_geom_tail _ u w hu hw 7
    have hrhs_decomp : u ^ 2 * (P0ser p02 pt u w - pS F 2 * u ^ 2 -
        2 * J3ser F u + X ^ 2 * RPser F u w) =
        (C (p02 : ℚ) * u ^ 4 - pS F 2 * u ^ 4 +
          X ^ 2 * (2 * jS F 3 - pS F 3) * u ^ 3 + X ^ 2 * JmS F * 8 * u ^ 4 +
          X ^ 2 * jS F 1 * (4 * u ^ 4 + 6 * u ^ 5) +
          X ^ 2 * jS F 2 * (4 * u ^ 4 + 6 * u ^ 5 + 8 * u ^ 6) +
          X ^ 2 * pS F 2 * (u ^ 4 + 4 * u ^ 5 + 3 * u ^ 6)) +
        (C (pt : ℚ) + 12 * X ^ 2 * JmS F) * (u ^ 5 * w) +
        (8 * X ^ 2 * jS F 1) * (u ^ 6 * w) +
        (10 * X ^ 2 * jS F 2 + 2 * X ^ 2 * pS F 2) * (u ^ 7 * w) -
        2 * (u ^ 2 * J3ser F u) := by
      unfold P0ser RPser; ring
    have hfinal :
        lfsum (fun n => G2 n * u ^ n) - X ^ 2 * lfsum (fun g => b g * u ^ g) -
          2 * X ^ 2 * lfsum (fun n => G1 n * u ^ n) - 3 * X ^ 2 * lfsum (fun n => G2 n * u ^ n) -
          2 * X ^ 2 * lfsum (fun n => G3 n * u ^ n) - X ^ 2 * lfsum (fun n => G4 n * u ^ n) =
        u ^ 2 * (P0ser p02 pt u w - pS F 2 * u ^ 2 - 2 * J3ser F u + X ^ 2 * RPser F u w) := by
      rw [hrhs_decomp, hfinlf, htail1, htail2, htail3, eShift,
        lfsum_mul_left (X ^ 2) (fun g => b g * u ^ g) (locFin_geom b u hu),
        lfsum_mul_left (2 * X ^ 2) (fun n => G1 n * u ^ n) (locFin_geom G1 u hu),
        lfsum_mul_left (3 * X ^ 2) (fun n => G2 n * u ^ n) (locFin_geom G2 u hu),
        lfsum_mul_left (2 * X ^ 2) (fun n => G3 n * u ^ n) (locFin_geom G3 u hu),
        lfsum_mul_left (X ^ 2) (fun n => G4 n * u ^ n) (locFin_geom G4 u hu),
        lfsum_mul_left (2 : PowerSeries ℚ) (fun n => shiftF n * u ^ n) (locFin_geom shiftF u hu)]
      rw [← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub,
        ← lfsum_add, ← lfsum_add, ← lfsum_add, ← lfsum_sub]
      congr 1
      funext n
      have hcase := colPJ3_case h n
      simp only [hG1def, hG2def, hG3def, hG4def, hbdef, hfinFdef, hshiftFdef]
      linear_combination u ^ n * hcase
    rw [hcomb, hexpand, hfinal]
  rw [hcore]

/-- The `u`-derivative of the `J`-master, evaluated (multiplied through by
`u` so the weight-`g` family carries `u^g`, then premultiplied by `u²`). -/
theorem master_J_deriv {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    u ^ 2 * (u * Kernel.dP u * J3ser F u +
        (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3serW F u) =
      u ^ 2 * (2 * (u ^ 2 * Qser F j01 j02 u) +
        u ^ 3 * Qpser F j01 j02 u) := by
  have hcore : u * Kernel.dP u * J3ser F u +
      (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3serW F u =
      2 * (u ^ 2 * Qser F j01 j02 u) + u ^ 3 * Qpser F j01 j02 u := by
    set a : ℕ → PowerSeries ℚ := colJ3 F with hadef
    set aw : ℕ → PowerSeries ℚ := fun g => C (g : ℚ) * a g with hawdef
    have haw_col : ∀ g, colJ3W F g = aw g := by
      intro g
      simp only [hawdef, hadef, colJ3W, colJ3]
      split_ifs <;> simp
    have hJ3 : J3ser F u = lfsum (fun g => a g * u ^ g) := rfl
    have hJ3w : J3serW F u = lfsum (fun g => aw g * u ^ g) := by
      unfold J3serW
      congr 1
      funext g
      rw [haw_col g]
    set F1 : ℕ → PowerSeries ℚ := fun n => if n < 1 then 0 else a (n - 1) with hF1def
    set F2 : ℕ → PowerSeries ℚ := fun n => if n < 2 then 0 else a (n - 2) with hF2def
    set F3 : ℕ → PowerSeries ℚ := fun n => if n < 3 then 0 else a (n - 3) with hF3def
    set F4 : ℕ → PowerSeries ℚ := fun n => if n < 4 then 0 else a (n - 4) with hF4def
    set F1w : ℕ → PowerSeries ℚ := fun n => if n < 1 then 0 else aw (n - 1) with hF1wdef
    set F2w : ℕ → PowerSeries ℚ := fun n => if n < 2 then 0 else aw (n - 2) with hF2wdef
    set F3w : ℕ → PowerSeries ℚ := fun n => if n < 3 then 0 else aw (n - 3) with hF3wdef
    set F4w : ℕ → PowerSeries ℚ := fun n => if n < 4 then 0 else aw (n - 4) with hF4wdef
    have e1 : u ^ 1 * J3ser F u = lfsum (fun n => F1 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 1
    have e2 : u ^ 2 * J3ser F u = lfsum (fun n => F2 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 2
    have e3 : u ^ 3 * J3ser F u = lfsum (fun n => F3 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 3
    have e4 : u ^ 4 * J3ser F u = lfsum (fun n => F4 n * u ^ n) := by
      rw [hJ3]; exact lfsum_shift_mul a u hu 4
    have e1w : u ^ 1 * J3serW F u = lfsum (fun n => F1w n * u ^ n) := by
      rw [hJ3w]; exact lfsum_shift_mul aw u hu 1
    have e2w : u ^ 2 * J3serW F u = lfsum (fun n => F2w n * u ^ n) := by
      rw [hJ3w]; exact lfsum_shift_mul aw u hu 2
    have e3w : u ^ 3 * J3serW F u = lfsum (fun n => F3w n * u ^ n) := by
      rw [hJ3w]; exact lfsum_shift_mul aw u hu 3
    have e4w : u ^ 4 * J3serW F u = lfsum (fun n => F4w n * u ^ n) := by
      rw [hJ3w]; exact lfsum_shift_mul aw u hu 4
    have hexpand1 : u * Kernel.dP u * J3ser F u =
        2 * (u ^ 2 * J3ser F u) - 2 * X ^ 2 * (u ^ 1 * J3ser F u) -
          6 * X ^ 2 * (u ^ 2 * J3ser F u) - 6 * X ^ 2 * (u ^ 3 * J3ser F u) -
          4 * X ^ 2 * (u ^ 4 * J3ser F u) := by
      unfold Kernel.dP; ring
    have hexpand2 : (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3serW F u =
        u ^ 2 * J3serW F u - X ^ 2 * J3serW F u - 2 * X ^ 2 * (u ^ 1 * J3serW F u) -
          3 * X ^ 2 * (u ^ 2 * J3serW F u) - 2 * X ^ 2 * (u ^ 3 * J3serW F u) -
          X ^ 2 * (u ^ 4 * J3serW F u) := by ring
    rw [e1, e2, e3, e4] at hexpand1
    rw [e1w, e2w, e3w, e4w, hJ3w] at hexpand2
    set rhsFw : ℕ → PowerSeries ℚ := fun n => C (n : ℚ) * rhsFJ F j01 j02 n with hrhsFwdef
    have hrhsw : 2 * (u ^ 2 * Qser F j01 j02 u) + u ^ 3 * Qpser F j01 j02 u =
        lfsum (fun n => rhsFw n * u ^ n) := by
      have hfin : ∀ g, 7 ≤ g → rhsFw g = 0 := by
        intro g hg
        simp only [hrhsFwdef]
        rw [rhsFJ_support F j01 j02 g hg, mul_zero]
      rw [lfsum_eq_of_finite rhsFw u hu 7 hfin]
      simp only [Finset.sum_range_succ, Finset.sum_range_zero, hrhsFwdef, rhsFJ]
      norm_num [Qser, Qpser, map_natCast, map_ofNat]
      ring
    have hfinal :
        (2 * lfsum (fun n => F2 n * u ^ n) - 2 * X ^ 2 * lfsum (fun n => F1 n * u ^ n) -
            6 * X ^ 2 * lfsum (fun n => F2 n * u ^ n) - 6 * X ^ 2 * lfsum (fun n => F3 n * u ^ n) -
            4 * X ^ 2 * lfsum (fun n => F4 n * u ^ n)) +
          (lfsum (fun n => F2w n * u ^ n) - X ^ 2 * lfsum (fun n => aw n * u ^ n) -
            2 * X ^ 2 * lfsum (fun n => F1w n * u ^ n) -
            3 * X ^ 2 * lfsum (fun n => F2w n * u ^ n) -
            2 * X ^ 2 * lfsum (fun n => F3w n * u ^ n) -
            X ^ 2 * lfsum (fun n => F4w n * u ^ n)) =
        lfsum (fun n => rhsFw n * u ^ n) := by
      rw [lfsum_mul_left (2 : PowerSeries ℚ) (fun n => F2 n * u ^ n) (locFin_geom F2 u hu),
        lfsum_mul_left (2 * X ^ 2 : PowerSeries ℚ) (fun n => F1 n * u ^ n) (locFin_geom F1 u hu),
        lfsum_mul_left (6 * X ^ 2 : PowerSeries ℚ) (fun n => F2 n * u ^ n) (locFin_geom F2 u hu),
        lfsum_mul_left (6 * X ^ 2 : PowerSeries ℚ) (fun n => F3 n * u ^ n) (locFin_geom F3 u hu),
        lfsum_mul_left (4 * X ^ 2 : PowerSeries ℚ) (fun n => F4 n * u ^ n) (locFin_geom F4 u hu),
        lfsum_mul_left (X ^ 2 : PowerSeries ℚ) (fun n => aw n * u ^ n) (locFin_geom aw u hu),
        lfsum_mul_left (2 * X ^ 2 : PowerSeries ℚ) (fun n => F1w n * u ^ n) (locFin_geom F1w u hu),
        lfsum_mul_left (3 * X ^ 2 : PowerSeries ℚ) (fun n => F2w n * u ^ n) (locFin_geom F2w u hu),
        lfsum_mul_left (2 * X ^ 2 : PowerSeries ℚ) (fun n => F3w n * u ^ n) (locFin_geom F3w u hu),
        lfsum_mul_left (X ^ 2 : PowerSeries ℚ) (fun n => F4w n * u ^ n) (locFin_geom F4w u hu)]
      rw [← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub,
        ← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_sub, ← lfsum_add]
      congr 1
      funext n
      have hb := weight_shift_bracket a n
      have hc := colJ3_case h n
      simp only [← hadef] at hc
      simp only [hF1def, hF2def, hF3def, hF4def, hF1wdef, hF2wdef, hF3wdef, hF4wdef, hawdef,
        hrhsFwdef]
      linear_combination u ^ n * hb + u ^ n * C (n : ℚ) * hc
    rw [hJ3w, hexpand1, hexpand2, hfinal]
    exact hrhsw.symm
  rw [hcore]

/-! ## Root facts -/

theorem coeff_one_u1 : coeff 1 (Kernel.u1 : PowerSeries ℚ) = 1 := by
  rw [Kernel.u1, PowerSeries.coeff_mk]
  have hA2 : coeff (2 : ℕ) (Kernel.A : PowerSeries ℚ) = -2 := by
    rw [Kernel.A, PowerSeries.coeff_mk]
    show (Kernel.sqrtList Kernel.aaC 2).getD 2 0 = -2
    rw [Kernel.sqrtList]
    rw [show Finset.Ioo 0 (1 + 1) = ({1} : Finset ℕ) from by decide, Finset.sum_singleton]
    rw [Kernel.sqrtList]
    rw [show Finset.Ioo 0 (0 + 1) = (∅ : Finset ℕ) from by decide, Finset.sum_empty]
    norm_num [Kernel.aaC, Kernel.sqrtList]
  have h1 : coeff (2 : ℕ) (1 - X - Kernel.A : PowerSeries ℚ) = 2 := by
    simp only [map_sub, PowerSeries.coeff_one, PowerSeries.coeff_X, hA2]
    norm_num
  rw [h1]; norm_num

theorem coeff_one_u2 : coeff 1 (Kernel.u2 : PowerSeries ℚ) = -1 := by
  rw [Kernel.u2, PowerSeries.coeff_mk]
  have hB2 : coeff (2 : ℕ) (Kernel.B : PowerSeries ℚ) = -2 := by
    rw [Kernel.B, PowerSeries.coeff_mk]
    show (Kernel.sqrtList Kernel.bbC 2).getD 2 0 = -2
    rw [Kernel.sqrtList]
    rw [show Finset.Ioo 0 (1 + 1) = ({1} : Finset ℕ) from by decide, Finset.sum_singleton]
    rw [Kernel.sqrtList]
    rw [show Finset.Ioo 0 (0 + 1) = (∅ : Finset ℕ) from by decide, Finset.sum_empty]
    norm_num [Kernel.bbC, Kernel.sqrtList]
  have h1 : coeff (2 : ℕ) (Kernel.B - 1 - X : PowerSeries ℚ) = -2 := by
    simp only [map_sub, PowerSeries.coeff_one, PowerSeries.coeff_X, hB2]
    norm_num
  rw [h1]; norm_num

theorem u1_ne_zero : (Kernel.u1 : PowerSeries ℚ) ≠ 0 := by
  intro h
  have := coeff_one_u1
  rw [h, map_zero] at this
  norm_num at this

theorem u2_ne_zero : (Kernel.u2 : PowerSeries ℚ) ≠ 0 := by
  intro h
  have := coeff_one_u2
  rw [h, map_zero] at this
  norm_num at this

/-! ## The six closing equations -/

/-- Equation (1): `Q(u₁) = 0`. -/
theorem closing_Q_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Qser F j01 j02 Kernel.u1 = 0 := by
  have hm := master_J h Kernel.u1 Kernel.constantCoeff_u1
  rw [show Kernel.u1 ^ 2 - X ^ 2 * (1 + Kernel.u1 + Kernel.u1 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u1_kernel, zero_mul, mul_zero] at hm
  have h4 : Kernel.u1 ^ 2 * (Kernel.u1 ^ 2 * Qser F j01 j02 Kernel.u1) =
      Kernel.u1 ^ 4 * Qser F j01 j02 Kernel.u1 := by ring
  rw [h4] at hm
  rcases mul_eq_zero.mp hm.symm with h0 | h0
  · exact absurd h0 (pow_ne_zero 4 u1_ne_zero)
  · exact h0

/-- Equation (2): `Q(u₂) = 0`. -/
theorem closing_Q_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Qser F j01 j02 Kernel.u2 = 0 := by
  have hm := master_J h Kernel.u2 Kernel.constantCoeff_u2
  rw [show Kernel.u2 ^ 2 - X ^ 2 * (1 + Kernel.u2 + Kernel.u2 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u2_kernel, zero_mul, mul_zero] at hm
  have h4 : Kernel.u2 ^ 2 * (Kernel.u2 ^ 2 * Qser F j01 j02 Kernel.u2) =
      Kernel.u2 ^ 4 * Qser F j01 j02 Kernel.u2 := by ring
  rw [h4] at hm
  rcases mul_eq_zero.mp hm.symm with h0 | h0
  · exact absurd h0 (pow_ne_zero 4 u2_ne_zero)
  · exact h0

/-- Equation (3): the `j₁` fixed point. -/
theorem closing_eq3 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 1 = C (j01 : ℚ) + X ^ 2 * (jS F 3 + c1S F) := by
  rw [c1S]
  linear_combination jS_col_one h

/-- Equation (4): the column sum `Jm·(1 − 9y) = Q(1)`. -/
theorem closing_eq4 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmS F * (1 - 9 * X ^ 2) =
      C (j01 : ℚ) + C (j02 : ℚ) - jS F 1 - jS F 2 +
        X ^ 2 * (c1S F + c2S F + c3S F + c4S F) := by
  rw [c1S, c2S, c3S, c4S]
  linear_combination JmS_step h + jS_col_one h + jS_col_two h

/-- The differentiated `J`-master at `u₁`: `D′(u₁)·J₃(u₁) = u₁²·Q′(u₁)`. -/
theorem dJ3_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u1 * J3ser F Kernel.u1 =
      Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1 := by
  have hm := master_J_deriv h Kernel.u1 Kernel.constantCoeff_u1
  rw [show Kernel.u1 ^ 2 - X ^ 2 * (1 + Kernel.u1 + Kernel.u1 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u1_kernel, zero_mul, add_zero] at hm
  rw [closing_Q_u1 h, mul_zero, mul_zero, zero_add] at hm
  have h4 : Kernel.u1 ^ 3 * (Kernel.dP Kernel.u1 * J3ser F Kernel.u1) =
      Kernel.u1 ^ 3 * (Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1) := by
    have heq : Kernel.u1 ^ 2 * (Kernel.u1 * Kernel.dP Kernel.u1 * J3ser F Kernel.u1) =
        Kernel.u1 ^ 3 * (Kernel.dP Kernel.u1 * J3ser F Kernel.u1) := by ring
    have heq2 : Kernel.u1 ^ 2 * (Kernel.u1 ^ 3 * Qpser F j01 j02 Kernel.u1) =
        Kernel.u1 ^ 3 * (Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1) := by ring
    rw [heq, heq2] at hm
    exact hm
  exact mul_left_cancel₀ (pow_ne_zero 3 u1_ne_zero) h4

/-- The differentiated `J`-master at `u₂`. -/
theorem dJ3_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u2 * J3ser F Kernel.u2 =
      Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2 := by
  have hm := master_J_deriv h Kernel.u2 Kernel.constantCoeff_u2
  rw [show Kernel.u2 ^ 2 - X ^ 2 * (1 + Kernel.u2 + Kernel.u2 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u2_kernel, zero_mul, add_zero] at hm
  rw [closing_Q_u2 h, mul_zero, mul_zero, zero_add] at hm
  have h4 : Kernel.u2 ^ 3 * (Kernel.dP Kernel.u2 * J3ser F Kernel.u2) =
      Kernel.u2 ^ 3 * (Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2) := by
    have heq : Kernel.u2 ^ 2 * (Kernel.u2 * Kernel.dP Kernel.u2 * J3ser F Kernel.u2) =
        Kernel.u2 ^ 3 * (Kernel.dP Kernel.u2 * J3ser F Kernel.u2) := by ring
    have heq2 : Kernel.u2 ^ 2 * (Kernel.u2 ^ 3 * Qpser F j01 j02 Kernel.u2) =
        Kernel.u2 ^ 3 * (Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2) := by ring
    rw [heq, heq2] at hm
    exact hm
  exact mul_left_cancel₀ (pow_ne_zero 3 u2_ne_zero) h4

/-- Equation (5): the cleared `P`-side equation at `u₁`. -/
theorem closing_P_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u1 *
        (P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 +
          X ^ 2 * RPser F Kernel.u1 Kernel.w1) -
      2 * Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1 = 0 := by
  have hm := master_P h Kernel.u1 Kernel.w1 Kernel.constantCoeff_u1 Kernel.one_sub_u1_mul_w1
  rw [show Kernel.u1 ^ 2 - X ^ 2 * (1 + Kernel.u1 + Kernel.u1 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u1_kernel, zero_mul, mul_zero] at hm
  have h4 : Kernel.u1 ^ 2 * (Kernel.u1 ^ 2 *
      (P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 -
        2 * J3ser F Kernel.u1 + X ^ 2 * RPser F Kernel.u1 Kernel.w1)) =
      Kernel.u1 ^ 4 *
      (P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 -
        2 * J3ser F Kernel.u1 + X ^ 2 * RPser F Kernel.u1 Kernel.w1) := by ring
  rw [h4] at hm
  have heq0 : P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 -
      2 * J3ser F Kernel.u1 + X ^ 2 * RPser F Kernel.u1 Kernel.w1 = 0 := by
    rcases mul_eq_zero.mp hm.symm with h0 | h0
    · exact absurd h0 (pow_ne_zero 4 u1_ne_zero)
    · exact h0
  have heq1 : P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 +
      X ^ 2 * RPser F Kernel.u1 Kernel.w1 = 2 * J3ser F Kernel.u1 := by
    linear_combination heq0
  linear_combination Kernel.dP Kernel.u1 * heq1 + 2 * dJ3_u1 h

/-- Equation (6): the cleared `P`-side equation at `u₂`. -/
theorem closing_P_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u2 *
        (P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 +
          X ^ 2 * RPser F Kernel.u2 Kernel.w2) -
      2 * Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2 = 0 := by
  have hm := master_P h Kernel.u2 Kernel.w2 Kernel.constantCoeff_u2 Kernel.one_sub_u2_mul_w2
  rw [show Kernel.u2 ^ 2 - X ^ 2 * (1 + Kernel.u2 + Kernel.u2 ^ 2) ^ 2 = 0 from by
    linear_combination Kernel.u2_kernel, zero_mul, mul_zero] at hm
  have h4 : Kernel.u2 ^ 2 * (Kernel.u2 ^ 2 *
      (P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 -
        2 * J3ser F Kernel.u2 + X ^ 2 * RPser F Kernel.u2 Kernel.w2)) =
      Kernel.u2 ^ 4 *
      (P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 -
        2 * J3ser F Kernel.u2 + X ^ 2 * RPser F Kernel.u2 Kernel.w2) := by ring
  rw [h4] at hm
  have heq0 : P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 -
      2 * J3ser F Kernel.u2 + X ^ 2 * RPser F Kernel.u2 Kernel.w2 = 0 := by
    rcases mul_eq_zero.mp hm.symm with h0 | h0
    · exact absurd h0 (pow_ne_zero 4 u2_ne_zero)
    · exact h0
  have heq1 : P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 +
      X ^ 2 * RPser F Kernel.u2 Kernel.w2 = 2 * J3ser F Kernel.u2 := by
    linear_combination heq0
  linear_combination Kernel.dP Kernel.u2 * heq1 + 2 * dJ3_u2 h

/-! ## The end-functional bridge series -/

/-- The `q`-end stream as a series (in `y`): `4j₁ + 5j₂ + 6Jm + p₂`. -/
noncomputable def qSeries (F : St → Nat) : PowerSeries ℚ :=
  4 * jY F 1 + 5 * jY F 2 + 6 * JmY F + pY F 2

/-- The bare-end stream as a series (in `y`): `j₁ + j₂ + Jm`. -/
noncomputable def bSeries (F : St → Nat) : PowerSeries ℚ :=
  jY F 1 + jY F 2 + JmY F

private lemma coeff_4mulS (S : PowerSeries ℚ) (m : Nat) :
    coeff m (4 * S) = 4 * coeff m S := by
  rw [show (4 : PowerSeries ℚ) = C 4 from (map_ofNat C 4).symm, coeff_C_mul]

private lemma coeff_5mulS (S : PowerSeries ℚ) (m : Nat) :
    coeff m (5 * S) = 5 * coeff m S := by
  rw [show (5 : PowerSeries ℚ) = C 5 from (map_ofNat C 5).symm, coeff_C_mul]

private lemma coeff_6mulS (S : PowerSeries ℚ) (m : Nat) :
    coeff m (6 * S) = 6 * coeff m S := by
  rw [show (6 : PowerSeries ℚ) = C 6 from (map_ofNat C 6).symm, coeff_C_mul]

/-- The `q`-end stream is the walk's emitted `qEnd` numbers. -/
theorem coeff_qSeries {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    coeff m (qSeries F) = (qEndF M (iter M F m) : ℚ) := by
  rw [qSeries]
  simp only [map_add, coeff_4mulS, coeff_5mulS, coeff_6mulS, coeff_jY, coeff_pY, coeff_JmY]
  have hq := qEndF_eval F h.deep_j hM
  rw [hq, pE_one F h.head_p1 m]
  push_cast
  ring

/-- The bare-end stream is the walk's emitted `bareEnd` numbers. -/
theorem coeff_bSeries (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) {m M : Nat}
    (hM : 2 * m + 5 ≤ M) :
    coeff m (bSeries F) = (bareEndF M (iter M F m) : ℚ) := by
  rw [bSeries]
  simp only [map_add, coeff_jY, coeff_JmY]
  have hb := bareEndF_eval F hF hM
  rw [hb]
  push_cast
  ring

/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only. If a finished proof uses strictly fewer
axioms, tighten the `info` string to the actual list; `native_decide`
(`Lean.ofReduceBool`) is out of bounds here, as is declaring new axioms. -/

/--
info: 'Polyplets.GapWalk.closing_Q_u1' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms closing_Q_u1

/--
info: 'Polyplets.GapWalk.closing_P_u2' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms closing_P_u2

end GapWalk
end Polyplets
