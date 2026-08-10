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
  sorry

theorem coeff_jS_odd (F : St → Nat) (g n : Nat) (h : ¬ 2 ∣ n) :
    coeff n (jS F g) = 0 := by
  sorry

@[simp] theorem coeff_pS_even (F : St → Nat) (g m : Nat) :
    coeff (2 * m) (pS F g) = (pE F m g : ℚ) := by
  sorry

theorem coeff_pS_odd (F : St → Nat) (g n : Nat) (h : ¬ 2 ∣ n) :
    coeff n (pS F g) = 0 := by
  sorry

/-- Nothing is ever pending at gap 1, in `s`. -/
theorem pS_one (F : St → Nat) (h1 : F (1, false) = 0) : pS F 1 = 0 := by
  sorry

/-! ## The transported column identities -/

theorem jS_col_one {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 1 = C (j01 : ℚ) +
      X ^ 2 * (5 * jS F 1 + 6 * jS F 2 + 8 * JmS F - jS F 3 +
        2 * pS F 2 + pS F 3) := by
  sorry

theorem jS_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 2 = C (j02 : ℚ) +
      X ^ 2 * (2 * jS F 1 + 3 * jS F 2 + 2 * JmS F + 2 * jS F 3 +
        jS F 4 + 2 * pS F 2) := by
  sorry

theorem jS_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 3 = X ^ 2 * (jS F 1 + 2 * jS F 2 + 3 * jS F 3 + 2 * jS F 4 +
      jS F 5) := by
  sorry

theorem jS_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 4 = X ^ 2 * (jS F 2 + 2 * jS F 3 + 3 * jS F 4 + 2 * jS F 5 +
      jS F 6) := by
  sorry

theorem jS_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    jS F (k + 5) = X ^ 2 * (jS F (k + 7) + 2 * jS F (k + 6) +
      3 * jS F (k + 5) + 2 * jS F (k + 4) + jS F (k + 3)) := by
  sorry

theorem pS_col_two {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 2 = C (p02 : ℚ) +
      X ^ 2 * ((pS F 4 - 2 * jS F 4) + 2 * (pS F 3 - 2 * jS F 3) +
        8 * JmS F + 4 * jS F 1 + 4 * jS F 2 + pS F 2) := by
  sorry

theorem pS_col_three {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 3 = C (pt : ℚ) +
      X ^ 2 * ((pS F 5 - 2 * jS F 5) + 2 * (pS F 4 - 2 * jS F 4) +
        3 * (pS F 3 - 2 * jS F 3) + 12 * JmS F + 6 * jS F 1 +
        6 * jS F 2 + 4 * pS F 2) := by
  sorry

theorem pS_col_four {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    pS F 4 = C (pt : ℚ) +
      X ^ 2 * ((pS F 6 - 2 * jS F 6) + 2 * (pS F 5 - 2 * jS F 5) +
        3 * (pS F 4 - 2 * jS F 4) + 2 * (pS F 3 - 2 * jS F 3) +
        12 * JmS F + 8 * jS F 1 + 8 * jS F 2 + 3 * pS F 2) := by
  sorry

theorem pS_col_generic {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (k : Nat) :
    pS F (k + 5) = C (pt : ℚ) +
      X ^ 2 * ((pS F (k + 7) - 2 * jS F (k + 7)) +
        2 * (pS F (k + 6) - 2 * jS F (k + 6)) +
        3 * (pS F (k + 5) - 2 * jS F (k + 5)) +
        2 * (pS F (k + 4) - 2 * jS F (k + 4)) +
        (pS F (k + 3) - 2 * jS F (k + 3)) +
        12 * JmS F + 8 * jS F 1 + 10 * jS F 2 + 2 * pS F 2) := by
  sorry

/-! ## The `Jm` column-sum recurrence (the equation-(4) primitive) -/

/-- Summing the generic `J`-columns: the deep mass steps by `9×` itself
with window-edge corrections and the two head feeds. -/
theorem JmY_step {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmY F = X * (jY F 1 + 3 * jY F 2 + 9 * JmY F - 3 * jY F 3 -
      jY F 4) := by
  sorry

/-- `JmY_step`, transported. -/
theorem JmS_step {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmS F = X ^ 2 * (jS F 1 + 3 * jS F 2 + 9 * JmS F - 3 * jS F 3 -
      jS F 4) := by
  sorry

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

/-- The weighted evaluation `Σ_{g≥3} g·ĵ_g·u^g`. -/
noncomputable def J3serW (F : St → Nat) (u : PowerSeries ℚ) : PowerSeries ℚ :=
  lfsum fun g => colJ3W F g * u ^ g

/-- Geometric collapse against a certified inverse:
`Σ_{g ≥ K} u^g = u^K·w`. -/
theorem lfsum_geom (u w : PowerSeries ℚ) (hu : constantCoeff u = 0)
    (hw : (1 - u) * w = 1) (K : Nat) :
    lfsum (fun g => (if g < K then 0 else 1) * u ^ g) = u ^ K * w := by
  sorry

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

/-! ## The three evaluated master identities (generic `u`, premultiplied) -/

/-- The `J`-master evaluated at any `u` of positive order:
`u²·(D(u)·J₃(u)) = u²·(u²·Q(u))`. -/
theorem master_J {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    u ^ 2 * ((u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3ser F u) =
      u ^ 2 * (u ^ 2 * Qser F j01 j02 u) := by
  sorry

/-- The `P`-master evaluated at any `u` of positive order. -/
theorem master_P {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u w : PowerSeries ℚ)
    (hu : constantCoeff u = 0) (hw : (1 - u) * w = 1) :
    u ^ 2 * ((u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) *
        (P3ser F u - 2 * J3ser F u)) =
      u ^ 2 * (u ^ 2 * (P0ser p02 pt u w - pS F 2 * u ^ 2 -
        2 * J3ser F u + X ^ 2 * RPser F u w)) := by
  sorry

/-- The `u`-derivative of the `J`-master, evaluated (multiplied through by
`u` so the weight-`g` family carries `u^g`, then premultiplied by `u²`). -/
theorem master_J_deriv {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) (u : PowerSeries ℚ)
    (hu : constantCoeff u = 0) :
    u ^ 2 * (u * Kernel.dP u * J3ser F u +
        (u ^ 2 - X ^ 2 * (1 + u + u ^ 2) ^ 2) * J3serW F u) =
      u ^ 2 * (2 * (u ^ 2 * Qser F j01 j02 u) +
        u ^ 3 * Qpser F j01 j02 u) := by
  sorry

/-! ## Root facts -/

theorem coeff_one_u1 : coeff 1 (Kernel.u1 : PowerSeries ℚ) = 1 := by
  sorry

theorem coeff_one_u2 : coeff 1 (Kernel.u2 : PowerSeries ℚ) = -1 := by
  sorry

theorem u1_ne_zero : (Kernel.u1 : PowerSeries ℚ) ≠ 0 := by
  sorry

theorem u2_ne_zero : (Kernel.u2 : PowerSeries ℚ) ≠ 0 := by
  sorry

/-! ## The six closing equations -/

/-- Equation (1): `Q(u₁) = 0`. -/
theorem closing_Q_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Qser F j01 j02 Kernel.u1 = 0 := by
  sorry

/-- Equation (2): `Q(u₂) = 0`. -/
theorem closing_Q_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Qser F j01 j02 Kernel.u2 = 0 := by
  sorry

/-- Equation (3): the `j₁` fixed point. -/
theorem closing_eq3 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    jS F 1 = C (j01 : ℚ) + X ^ 2 * (jS F 3 + c1S F) := by
  sorry

/-- Equation (4): the column sum `Jm·(1 − 9y) = Q(1)`. -/
theorem closing_eq4 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    JmS F * (1 - 9 * X ^ 2) =
      C (j01 : ℚ) + C (j02 : ℚ) - jS F 1 - jS F 2 +
        X ^ 2 * (c1S F + c2S F + c3S F + c4S F) := by
  sorry

/-- The differentiated `J`-master at `u₁`: `D′(u₁)·J₃(u₁) = u₁²·Q′(u₁)`. -/
theorem dJ3_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u1 * J3ser F Kernel.u1 =
      Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1 := by
  sorry

/-- The differentiated `J`-master at `u₂`. -/
theorem dJ3_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u2 * J3ser F Kernel.u2 =
      Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2 := by
  sorry

/-- Equation (5): the cleared `P`-side equation at `u₁`. -/
theorem closing_P_u1 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u1 *
        (P0ser p02 pt Kernel.u1 Kernel.w1 - pS F 2 * Kernel.u1 ^ 2 +
          X ^ 2 * RPser F Kernel.u1 Kernel.w1) -
      2 * Kernel.u1 ^ 2 * Qpser F j01 j02 Kernel.u1 = 0 := by
  sorry

/-- Equation (6): the cleared `P`-side equation at `u₂`. -/
theorem closing_P_u2 {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) :
    Kernel.dP Kernel.u2 *
        (P0ser p02 pt Kernel.u2 Kernel.w2 - pS F 2 * Kernel.u2 ^ 2 +
          X ^ 2 * RPser F Kernel.u2 Kernel.w2) -
      2 * Kernel.u2 ^ 2 * Qpser F j01 j02 Kernel.u2 = 0 := by
  sorry

/-! ## The end-functional bridge series -/

/-- The `q`-end stream as a series (in `y`): `4j₁ + 5j₂ + 6Jm + p₂`. -/
noncomputable def qSeries (F : St → Nat) : PowerSeries ℚ :=
  4 * jY F 1 + 5 * jY F 2 + 6 * JmY F + pY F 2

/-- The bare-end stream as a series (in `y`): `j₁ + j₂ + Jm`. -/
noncomputable def bSeries (F : St → Nat) : PowerSeries ℚ :=
  jY F 1 + jY F 2 + JmY F

/-- The `q`-end stream is the walk's emitted `qEnd` numbers. -/
theorem coeff_qSeries {F : St → Nat} {j01 j02 p02 pt : Nat}
    (h : StartData F j01 j02 p02 pt) {m M : Nat} (hM : 2 * m + 5 ≤ M) :
    coeff m (qSeries F) = (qEndF M (iter M F m) : ℚ) := by
  sorry

/-- The bare-end stream is the walk's emitted `bareEnd` numbers. -/
theorem coeff_bSeries (F : St → Nat)
    (hF : ∀ g, 3 ≤ g → F (g, true) = 0) {m M : Nat}
    (hM : 2 * m + 5 ≤ M) :
    coeff m (bSeries F) = (bareEndF M (iter M F m) : ℚ) := by
  sorry

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
