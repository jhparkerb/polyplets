/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.LinearAlgebra.Matrix.Adjugate
import Polyplets.DepthOneKernelSol

-- Machine-generated polynomial literals are longer than the style line
-- limit by nature; see the module docstring for their provenance.
set_option linter.style.longLine false

/-!
# Notary piece K, module 8: uniqueness — the walk IS the closed form

Campaign *Notary*, piece **K** of `docs/notary-k-plan.md`, wave K-δ. The
walk's six unknown series satisfy the cleared polynomial system (rows
from the six closing equations of `GapWalkClosing.lean`); the closed-form
numerators satisfy the same system (`DepthOneKernelSol.lean`). This
module shows the system pins its solution: the difference vector is
killed by `Matrix.adjugate_mulVec`-style reasoning against a determinant
whose order-22 (interior) / order-18 (bare) coefficient is `−64 ≠ 0`.
Head theorems `trans*`: for every start with the right package,

    X^e · den · (walk unknown) = num .

Every statement was verified before this skeleton was written:
`experiments/notary_kdelta_gen4.py` (`build/notary_kdelta_gen4.log`)
emits the entries verbatim from the same data that
`DepthOneKernelSol.lean`'s proved rows consume, recomputes the symbolic
determinant in the reduced tuple algebra, and re-checks its valuation
and leading coefficient against the truncated-series determinant of
stage 2 (`build/notary_kdelta_gen2.log`, d6).

## Proof recipes

*Walk rows* (`walkRow*`): from the matching `GapWalkClosing` equation.
Multiply the equation by the row's clearing factor and rewrite the root
powers by the defining relations — for the `u₁`-rows: `Kernel.u1_def`
(`2*X*u1 = 1 - X - A`) and its square/cube/fourth (obtained by `congr`
arguments, e.g. `(2*X*u1)^2 = (1-X-A)^2`); for the `u₂`-rows the same
with `u2_def`; rows 5, 6 additionally clear their `w`-factors with
`Kernel.one_sub_u1_mul_w1` / `one_sub_u2_mul_w2` (each `RPser`/`P0ser`
carries `w` only in products `u^k * w`, and the row was premultiplied by
`(1-u)^2` — exactly two `w`-factors). After the rewrites the goal is a
polynomial identity in `X, A, B` and the six unknowns:
`linear_combination` with the γ-equation (times its clearing monomial)
plus multiples of `Kernel.A_sq`/`B_sq` closes it. Rows 3, 4 involve no
roots at all: `linear_combination (jS_col_one h)`-style from
`closing_eq3`/`closing_eq4` (transported: this module's rows are the
same equations times `X^E·D`-free clearings — compare the emitted
entries).

*Determinant* (`det_mat*`): expand `Matrix.det` by
`Matrix.det_succ_row_zero` / `Fin.sum_univ_succ` (or
`Matrix.det_fin_six`-style `simp [Matrix.det_succ_row_zero,
Fin.sum_univ_succ]`), `unfold` the entry defs, and close with `ring`
against `detTup*` (unfolded) using `Kernel.A_sq`/`B_sq` via
`linear_combination` — the reduction certificates are small because the
tuple algebra already reduced the determinant. Budget heartbeats
generously (`set_option maxHeartbeats 4000000 in`).

*Certificate* (`coeff_det*`): `detTup*` is an explicit combination
`c₀ + c₁·A + c₂·B + c₃·A·B`; extract the stated coefficient with
`coeff_mul` / `Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk` and the
`A`/`B` coefficient literals — `coeff k A = sqrtCoef aaC k` evaluates by
unfolding the `sqrtList` recursion (`norm_num [Kernel.sqrtCoef,
Kernel.sqrtList]`; the γ module `GapWalkClosing.lean` did the same at
order 2, here it goes to the stated order). The literals (exact, from
the generator): A: 1, -1, -2, -2, -4, -8, -18, -44, -110, -286, -764,
-2084, -5772, -16212, -46092; B: 1, 1, -2, 2, -4, 8, -18, 44, -110,
286, -764, 2084, -5772, 16212, -46092 (orders 0..14; extend by the same
recursion as needed).

*`det_ne_zero*`*: from `det_mat*` and `coeff_det*` (a series with a
nonzero coefficient is nonzero: `fun h => by simpa [h] using …`).

*Vectorizations* (`mulVec_*`): `funext`, `Fin.sum_univ_six`,
`Matrix.mulVec`, `Matrix.cons_val_*` simp lemmas; each component is the
corresponding `walkRow*` resp. `DepthOneKernelSol.row*` identity (for
the scaled version, multiply row `c`'s scaling through — the `scaledNum`
entries carry exactly the row scalings, and the right side gains the
common `X^E·D`).

*Uniqueness* (`unk_eq*`): let `v := fun c => (X^E·D) * unkVec F c −
scaledNum c`. From the two `mulVec` theorems, `(mat).mulVec v = 0`
(linearity: `Matrix.mulVec_sub`, `Matrix.mulVec_smul`). Then
`(mat).adjugate.mulVec ((mat).mulVec v) = (mat).det • v` — via
`Matrix.mulVec_mulVec` and `Matrix.adjugate_mul`; conclude
`(mat).det • v = 0`, so `v = 0` componentwise (domain, `det_ne_zero*`,
`smul_eq_zero`).

*Transcriptions* (`trans*`): component `c` of `unk_eq*` reads
`X^E·D·x_c = X^(E−e_c)·(D/d_c)·num_c`; both sides factor as
`X^(E−e_c)·(D/d_c) · (X^(e_c)·d_c·x_c − num_c) = 0` — cancel the
`X`-power (`X_ne_zero`, `pow_ne_zero`) and the ratio (a nonzero
constant) and the denominator relation `D = ratio · d_c` (a `ring`
identity between the emitted polynomials) in the domain.

Do not change any statement below; if one resists proof, leave it
sorried and report back.
-/

namespace Polyplets
namespace GapWalk

open PowerSeries

/-- The walk's six unknowns, vectorized. -/
noncomputable def unkVec (F : St → Nat) : Fin 6 → PowerSeries ℚ :=
  ![jS F 1, jS F 2, jS F 3, JmS F, pS F 2, pS F 3]

-- ==================== start: int ====================
noncomputable def m11Int : PowerSeries ℚ :=
  (1 * X ^ 3 + (-5) * X ^ 4) + ((-3) * X ^ 3) * Kernel.A
noncomputable def m12Int : PowerSeries ℚ :=
  (4 * X ^ 3 + (-6) * X ^ 4) + ((-4) * X ^ 3) * Kernel.A
noncomputable def m13Int : PowerSeries ℚ :=
  ((-2) * X ^ 3 + 2 * X ^ 4) + (2 * X ^ 3) * Kernel.A
noncomputable def m14Int : PowerSeries ℚ :=
  (2 * X ^ 2 + 4 * X ^ 3 + (-10) * X ^ 4) + ((-2) * X ^ 2 + (-6) * X ^ 3) * Kernel.A
noncomputable def m15Int : PowerSeries ℚ :=
  (2 * X ^ 2 + (-2) * X ^ 3 + (-4) * X ^ 4) + ((-2) * X ^ 2) * Kernel.A
noncomputable def m16Int : PowerSeries ℚ :=
  (1 * X ^ 3 + (-1) * X ^ 4) + ((-1) * X ^ 3) * Kernel.A
noncomputable def r1Int : PowerSeries ℚ :=
  ((-1) + (-2) * X + 5 * X ^ 2) + (1 + 3 * X) * Kernel.A
noncomputable def m21Int : PowerSeries ℚ :=
  ((-1) * X ^ 3 + (-5) * X ^ 4) + (3 * X ^ 3) * Kernel.B
noncomputable def m22Int : PowerSeries ℚ :=
  ((-4) * X ^ 3 + (-6) * X ^ 4) + (4 * X ^ 3) * Kernel.B
noncomputable def m23Int : PowerSeries ℚ :=
  (2 * X ^ 3 + 2 * X ^ 4) + ((-2) * X ^ 3) * Kernel.B
noncomputable def m24Int : PowerSeries ℚ :=
  (2 * X ^ 2 + (-4) * X ^ 3 + (-10) * X ^ 4) + ((-2) * X ^ 2 + 6 * X ^ 3) * Kernel.B
noncomputable def m25Int : PowerSeries ℚ :=
  (2 * X ^ 2 + 2 * X ^ 3 + (-4) * X ^ 4) + ((-2) * X ^ 2) * Kernel.B
noncomputable def m26Int : PowerSeries ℚ :=
  ((-1) * X ^ 3 + (-1) * X ^ 4) + (1 * X ^ 3) * Kernel.B
noncomputable def r2Int : PowerSeries ℚ :=
  ((-1) + 2 * X + 5 * X ^ 2) + (1 + (-3) * X) * Kernel.B
noncomputable def m31Int : PowerSeries ℚ :=
  (1 + (-5) * X ^ 2)
noncomputable def m32Int : PowerSeries ℚ :=
  ((-6) * X ^ 2)
noncomputable def m33Int : PowerSeries ℚ :=
  (1 * X ^ 2)
noncomputable def m34Int : PowerSeries ℚ :=
  ((-8) * X ^ 2)
noncomputable def m35Int : PowerSeries ℚ :=
  ((-2) * X ^ 2)
noncomputable def m36Int : PowerSeries ℚ :=
  ((-1) * X ^ 2)
noncomputable def r3Int : PowerSeries ℚ :=
  (4)
noncomputable def m41Int : PowerSeries ℚ :=
  (1 + (-8) * X ^ 2)
noncomputable def m42Int : PowerSeries ℚ :=
  (1 + (-12) * X ^ 2)
noncomputable def m43Int : PowerSeries ℚ :=
  (2 * X ^ 2)
noncomputable def m44Int : PowerSeries ℚ :=
  (1 + (-19) * X ^ 2)
noncomputable def m45Int : PowerSeries ℚ :=
  ((-4) * X ^ 2)
noncomputable def m46Int : PowerSeries ℚ :=
  ((-1) * X ^ 2)
noncomputable def r4Int : PowerSeries ℚ :=
  (5)
noncomputable def m51Int : PowerSeries ℚ :=
  (2 * X ^ 2 + (-11) * X ^ 3 + 16 * X ^ 4 + (-1) * X ^ 5 + (-6) * X ^ 6) + ((-2) * X ^ 2 + 9 * X ^ 3 + (-11) * X ^ 4 + 6 * X ^ 5) * Kernel.A
noncomputable def m52Int : PowerSeries ℚ :=
  (2 * X + (-10) * X ^ 2 + 4 * X ^ 3 + 34 * X ^ 4 + (-26) * X ^ 5 + (-12) * X ^ 6) + ((-2) * X + 8 * X ^ 2 + (-22) * X ^ 4 + 12 * X ^ 5) * Kernel.A
noncomputable def m53Int : PowerSeries ℚ :=
  (2 * X ^ 2 + (-8) * X ^ 3 + (-2) * X ^ 4 + 24 * X ^ 5) + ((-2) * X ^ 2 + 6 * X ^ 3 + 4 * X ^ 4 + (-12) * X ^ 5) * Kernel.A
noncomputable def m54Int : PowerSeries ℚ :=
  ((-4) * X ^ 2 + 16 * X ^ 3 + 4 * X ^ 4 + (-48) * X ^ 5) + (4 * X ^ 2 + (-12) * X ^ 3 + (-8) * X ^ 4 + 24 * X ^ 5) * Kernel.A
noncomputable def m55Int : PowerSeries ℚ :=
  ((-2) * X + 7 * X ^ 2 + 10 * X ^ 3 + (-40) * X ^ 4 + (-4) * X ^ 5 + 21 * X ^ 6) + (2 * X + (-5) * X ^ 2 + (-11) * X ^ 3 + 23 * X ^ 4 + 3 * X ^ 5) * Kernel.A
noncomputable def m56Int : PowerSeries ℚ :=
  ((-1) * X ^ 2 + 4 * X ^ 3 + 1 * X ^ 4 + (-12) * X ^ 5) + (1 * X ^ 2 + (-3) * X ^ 3 + (-2) * X ^ 4 + 6 * X ^ 5) * Kernel.A
noncomputable def r5Int : PowerSeries ℚ :=
  (2 + (-8) * X + (-2) * X ^ 2 + 24 * X ^ 3) + ((-2) + 6 * X + 4 * X ^ 2 + (-12) * X ^ 3) * Kernel.A
noncomputable def m61Int : PowerSeries ℚ :=
  ((-2) * X ^ 2 + (-11) * X ^ 3 + (-16) * X ^ 4 + (-1) * X ^ 5 + 6 * X ^ 6) + (2 * X ^ 2 + 9 * X ^ 3 + 11 * X ^ 4 + 6 * X ^ 5) * Kernel.B
noncomputable def m62Int : PowerSeries ℚ :=
  (2 * X + 10 * X ^ 2 + 4 * X ^ 3 + (-34) * X ^ 4 + (-26) * X ^ 5 + 12 * X ^ 6) + ((-2) * X + (-8) * X ^ 2 + 22 * X ^ 4 + 12 * X ^ 5) * Kernel.B
noncomputable def m63Int : PowerSeries ℚ :=
  ((-2) * X ^ 2 + (-8) * X ^ 3 + 2 * X ^ 4 + 24 * X ^ 5) + (2 * X ^ 2 + 6 * X ^ 3 + (-4) * X ^ 4 + (-12) * X ^ 5) * Kernel.B
noncomputable def m64Int : PowerSeries ℚ :=
  (4 * X ^ 2 + 16 * X ^ 3 + (-4) * X ^ 4 + (-48) * X ^ 5) + ((-4) * X ^ 2 + (-12) * X ^ 3 + 8 * X ^ 4 + 24 * X ^ 5) * Kernel.B
noncomputable def m65Int : PowerSeries ℚ :=
  ((-2) * X + (-7) * X ^ 2 + 10 * X ^ 3 + 40 * X ^ 4 + (-4) * X ^ 5 + (-21) * X ^ 6) + (2 * X + 5 * X ^ 2 + (-11) * X ^ 3 + (-23) * X ^ 4 + 3 * X ^ 5) * Kernel.B
noncomputable def m66Int : PowerSeries ℚ :=
  (1 * X ^ 2 + 4 * X ^ 3 + (-1) * X ^ 4 + (-12) * X ^ 5) + ((-1) * X ^ 2 + (-3) * X ^ 3 + 2 * X ^ 4 + 6 * X ^ 5) * Kernel.B
noncomputable def r6Int : PowerSeries ℚ :=
  ((-2) + (-8) * X + 2 * X ^ 2 + 24 * X ^ 3) + (2 + 6 * X + (-4) * X ^ 2 + (-12) * X ^ 3) * Kernel.B
theorem walkRow1Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m11Int * (jS F 1) + m12Int * (jS F 2) + m13Int * (jS F 3) + m14Int * (JmS F) + m15Int * (pS F 2) + m16Int * (pS F 3) = r1Int := by
  sorry

theorem walkRow2Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m21Int * (jS F 1) + m22Int * (jS F 2) + m23Int * (jS F 3) + m24Int * (JmS F) + m25Int * (pS F 2) + m26Int * (pS F 3) = r2Int := by
  sorry

theorem walkRow3Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m31Int * (jS F 1) + m32Int * (jS F 2) + m33Int * (jS F 3) + m34Int * (JmS F) + m35Int * (pS F 2) + m36Int * (pS F 3) = r3Int := by
  sorry

theorem walkRow4Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m41Int * (jS F 1) + m42Int * (jS F 2) + m43Int * (jS F 3) + m44Int * (JmS F) + m45Int * (pS F 2) + m46Int * (pS F 3) = r4Int := by
  sorry

theorem walkRow5Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m51Int * (jS F 1) + m52Int * (jS F 2) + m53Int * (jS F 3) + m54Int * (JmS F) + m55Int * (pS F 2) + m56Int * (pS F 3) = r5Int := by
  sorry

theorem walkRow6Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    m61Int * (jS F 1) + m62Int * (jS F 2) + m63Int * (jS F 3) + m64Int * (JmS F) + m65Int * (pS F 2) + m66Int * (pS F 3) = r6Int := by
  sorry

-- det(int): valuation 22, coeff 22 = -64
noncomputable def detTupInt : PowerSeries ℚ :=
  ((-64) * X ^ 10 + 1376 * X ^ 12 + (-8176) * X ^ 14 + (-2312) * X ^ 16 + 116384 * X ^ 18 + (-156848) * X ^ 20 + 74448 * X ^ 22 + (-8424) * X ^ 24) + (64 * X ^ 10 + 64 * X ^ 11 + (-1184) * X ^ 12 + (-928) * X ^ 13 + 5264 * X ^ 14 + 1808 * X ^ 15 + 9648 * X ^ 16 + 14112 * X ^ 17 + (-77152) * X ^ 18 + (-18224) * X ^ 19 + 66576 * X ^ 20 + 12384 * X ^ 21 + (-18576) * X ^ 22) * Kernel.A + (64 * X ^ 10 + (-64) * X ^ 11 + (-1184) * X ^ 12 + 928 * X ^ 13 + 5264 * X ^ 14 + (-1808) * X ^ 15 + 9648 * X ^ 16 + (-14112) * X ^ 17 + (-77152) * X ^ 18 + 18224 * X ^ 19 + 66576 * X ^ 20 + (-12384) * X ^ 21 + (-18576) * X ^ 22) * Kernel.B + ((-64) * X ^ 10 + 1056 * X ^ 12 + (-3408) * X ^ 14 + (-13320) * X ^ 16 + 48568 * X ^ 18 + (-23352) * X ^ 20 + 2808 * X ^ 22) * (Kernel.A * Kernel.B)
-- DET_VALUATION_Int = 22

/-! ### The int system as a matrix -/

noncomputable def matInt : Matrix (Fin 6) (Fin 6) (PowerSeries ℚ) :=
  !![m11Int, m12Int, m13Int, m14Int, m15Int, m16Int;
    m21Int, m22Int, m23Int, m24Int, m25Int, m26Int;
    m31Int, m32Int, m33Int, m34Int, m35Int, m36Int;
    m41Int, m42Int, m43Int, m44Int, m45Int, m46Int;
    m51Int, m52Int, m53Int, m54Int, m55Int, m56Int;
    m61Int, m62Int, m63Int, m64Int, m65Int, m66Int]

noncomputable def rvecInt : Fin 6 → PowerSeries ℚ :=
  ![r1Int, r2Int, r3Int, r4Int, r5Int, r6Int]

/-- The six scaled numerators: column `c` carries `X^(E−e_c)·(D/d_c)`. -/
noncomputable def scaledNumInt : Fin 6 → PowerSeries ℚ :=
  ![X ^ 2 * 2 * numJ1Int, X ^ 1 * numJ2Int, 2 * numJ3Int, X ^ 1 * numJmInt, X ^ 1 * 2 * numP2Int, 2 * numP3Int]

/-- The determinant of the cleared system, in closed basis form. -/
theorem det_matInt : (matInt).det = detTupInt := by
  sorry

/-- The determinant certificate: the order-22 coefficient is `−64`. -/
theorem coeff_detInt : coeff 22 (detTupInt) = -64 := by
  sorry

theorem det_ne_zeroInt : (matInt).det ≠ 0 := by
  sorry

/-- The walk satisfies the system (the six `walkRow` theorems, vectorized). -/
theorem mulVec_walkInt {F : St → Nat} (h : StartData F 4 1 4 6) :
    (matInt).mulVec (unkVec F) = rvecInt := by
  sorry

/-- The closed forms satisfy the system (the six `DepthOneKernelSol` rows,
vectorized and rescaled). -/
theorem mulVec_scaledNumInt :
    (matInt).mulVec (scaledNumInt) = (X ^ 4 * denAllInt) • rvecInt := by
  sorry

/-- Uniqueness: the two solutions of the cleared system agree after the
common `X^E·D` scaling (adjugate against the determinant, in the domain). -/
theorem unk_eqInt {F : St → Nat} (h : StartData F 4 1 4 6) (c : Fin 6) :
    (X ^ 4 * denAllInt) * unkVec F c = scaledNumInt c := by
  sorry

theorem transJ1Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 2 * denJ1Int * (jS F 1) = numJ1Int := by
  sorry

theorem transJ2Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 3 * denJ2Int * (jS F 2) = numJ2Int := by
  sorry

theorem transJ3Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 4 * denJ3Int * (jS F 3) = numJ3Int := by
  sorry

theorem transJmInt {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 3 * denJmInt * (JmS F) = numJmInt := by
  sorry

theorem transP2Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 3 * denP2Int * (pS F 2) = numP2Int := by
  sorry

theorem transP3Int {F : St → Nat} (h : StartData F 4 1 4 6) :
    X ^ 4 * denP3Int * (pS F 3) = numP3Int := by
  sorry

-- ==================== start: bare ====================
noncomputable def m11Bare : PowerSeries ℚ :=
  (1 * X ^ 2 + (-5) * X ^ 3) + ((-3) * X ^ 2) * Kernel.A
noncomputable def m12Bare : PowerSeries ℚ :=
  (4 * X ^ 2 + (-6) * X ^ 3) + ((-4) * X ^ 2) * Kernel.A
noncomputable def m13Bare : PowerSeries ℚ :=
  ((-2) * X ^ 2 + 2 * X ^ 3) + (2 * X ^ 2) * Kernel.A
noncomputable def m14Bare : PowerSeries ℚ :=
  (2 * X + 4 * X ^ 2 + (-10) * X ^ 3) + ((-2) * X + (-6) * X ^ 2) * Kernel.A
noncomputable def m15Bare : PowerSeries ℚ :=
  (2 * X + (-2) * X ^ 2 + (-4) * X ^ 3) + ((-2) * X) * Kernel.A
noncomputable def m16Bare : PowerSeries ℚ :=
  (1 * X ^ 2 + (-1) * X ^ 3) + ((-1) * X ^ 2) * Kernel.A
noncomputable def r1Bare : PowerSeries ℚ :=
  ((-1) + 1 * X) + (1) * Kernel.A
noncomputable def m21Bare : PowerSeries ℚ :=
  ((-1) * X ^ 2 + (-5) * X ^ 3) + (3 * X ^ 2) * Kernel.B
noncomputable def m22Bare : PowerSeries ℚ :=
  ((-4) * X ^ 2 + (-6) * X ^ 3) + (4 * X ^ 2) * Kernel.B
noncomputable def m23Bare : PowerSeries ℚ :=
  (2 * X ^ 2 + 2 * X ^ 3) + ((-2) * X ^ 2) * Kernel.B
noncomputable def m24Bare : PowerSeries ℚ :=
  (2 * X + (-4) * X ^ 2 + (-10) * X ^ 3) + ((-2) * X + 6 * X ^ 2) * Kernel.B
noncomputable def m25Bare : PowerSeries ℚ :=
  (2 * X + 2 * X ^ 2 + (-4) * X ^ 3) + ((-2) * X) * Kernel.B
noncomputable def m26Bare : PowerSeries ℚ :=
  ((-1) * X ^ 2 + (-1) * X ^ 3) + (1 * X ^ 2) * Kernel.B
noncomputable def r2Bare : PowerSeries ℚ :=
  (1 + 1 * X) + ((-1)) * Kernel.B
noncomputable def m31Bare : PowerSeries ℚ :=
  (1 + (-5) * X ^ 2)
noncomputable def m32Bare : PowerSeries ℚ :=
  ((-6) * X ^ 2)
noncomputable def m33Bare : PowerSeries ℚ :=
  (1 * X ^ 2)
noncomputable def m34Bare : PowerSeries ℚ :=
  ((-8) * X ^ 2)
noncomputable def m35Bare : PowerSeries ℚ :=
  ((-2) * X ^ 2)
noncomputable def m36Bare : PowerSeries ℚ :=
  ((-1) * X ^ 2)
noncomputable def r3Bare : PowerSeries ℚ :=
  (1)
noncomputable def m41Bare : PowerSeries ℚ :=
  (1 + (-8) * X ^ 2)
noncomputable def m42Bare : PowerSeries ℚ :=
  (1 + (-12) * X ^ 2)
noncomputable def m43Bare : PowerSeries ℚ :=
  (2 * X ^ 2)
noncomputable def m44Bare : PowerSeries ℚ :=
  (1 + (-19) * X ^ 2)
noncomputable def m45Bare : PowerSeries ℚ :=
  ((-4) * X ^ 2)
noncomputable def m46Bare : PowerSeries ℚ :=
  ((-1) * X ^ 2)
noncomputable def r4Bare : PowerSeries ℚ :=
  (1)
noncomputable def m51Bare : PowerSeries ℚ :=
  (2 * X + (-11) * X ^ 2 + 16 * X ^ 3 + (-1) * X ^ 4 + (-6) * X ^ 5) + ((-2) * X + 9 * X ^ 2 + (-11) * X ^ 3 + 6 * X ^ 4) * Kernel.A
noncomputable def m52Bare : PowerSeries ℚ :=
  (2 + (-10) * X + 4 * X ^ 2 + 34 * X ^ 3 + (-26) * X ^ 4 + (-12) * X ^ 5) + ((-2) + 8 * X + (-22) * X ^ 3 + 12 * X ^ 4) * Kernel.A
noncomputable def m53Bare : PowerSeries ℚ :=
  (2 * X + (-8) * X ^ 2 + (-2) * X ^ 3 + 24 * X ^ 4) + ((-2) * X + 6 * X ^ 2 + 4 * X ^ 3 + (-12) * X ^ 4) * Kernel.A
noncomputable def m54Bare : PowerSeries ℚ :=
  ((-4) * X + 16 * X ^ 2 + 4 * X ^ 3 + (-48) * X ^ 4) + (4 * X + (-12) * X ^ 2 + (-8) * X ^ 3 + 24 * X ^ 4) * Kernel.A
noncomputable def m55Bare : PowerSeries ℚ :=
  ((-2) + 7 * X + 10 * X ^ 2 + (-40) * X ^ 3 + (-4) * X ^ 4 + 21 * X ^ 5) + (2 + (-5) * X + (-11) * X ^ 2 + 23 * X ^ 3 + 3 * X ^ 4) * Kernel.A
noncomputable def m56Bare : PowerSeries ℚ :=
  ((-1) * X + 4 * X ^ 2 + 1 * X ^ 3 + (-12) * X ^ 4) + (1 * X + (-3) * X ^ 2 + (-2) * X ^ 3 + 6 * X ^ 4) * Kernel.A
noncomputable def r5Bare : PowerSeries ℚ :=
  (1 + (-5) * X + 5 * X ^ 2 + 3 * X ^ 3) + ((-1) + 4 * X + (-3) * X ^ 2) * Kernel.A
noncomputable def m61Bare : PowerSeries ℚ :=
  ((-2) * X + (-11) * X ^ 2 + (-16) * X ^ 3 + (-1) * X ^ 4 + 6 * X ^ 5) + (2 * X + 9 * X ^ 2 + 11 * X ^ 3 + 6 * X ^ 4) * Kernel.B
noncomputable def m62Bare : PowerSeries ℚ :=
  (2 + 10 * X + 4 * X ^ 2 + (-34) * X ^ 3 + (-26) * X ^ 4 + 12 * X ^ 5) + ((-2) + (-8) * X + 22 * X ^ 3 + 12 * X ^ 4) * Kernel.B
noncomputable def m63Bare : PowerSeries ℚ :=
  ((-2) * X + (-8) * X ^ 2 + 2 * X ^ 3 + 24 * X ^ 4) + (2 * X + 6 * X ^ 2 + (-4) * X ^ 3 + (-12) * X ^ 4) * Kernel.B
noncomputable def m64Bare : PowerSeries ℚ :=
  (4 * X + 16 * X ^ 2 + (-4) * X ^ 3 + (-48) * X ^ 4) + ((-4) * X + (-12) * X ^ 2 + 8 * X ^ 3 + 24 * X ^ 4) * Kernel.B
noncomputable def m65Bare : PowerSeries ℚ :=
  ((-2) + (-7) * X + 10 * X ^ 2 + 40 * X ^ 3 + (-4) * X ^ 4 + (-21) * X ^ 5) + (2 + 5 * X + (-11) * X ^ 2 + (-23) * X ^ 3 + 3 * X ^ 4) * Kernel.B
noncomputable def m66Bare : PowerSeries ℚ :=
  (1 * X + 4 * X ^ 2 + (-1) * X ^ 3 + (-12) * X ^ 4) + ((-1) * X + (-3) * X ^ 2 + 2 * X ^ 3 + 6 * X ^ 4) * Kernel.B
noncomputable def r6Bare : PowerSeries ℚ :=
  (1 + 5 * X + 5 * X ^ 2 + (-3) * X ^ 3) + ((-1) + (-4) * X + (-3) * X ^ 2) * Kernel.B
theorem walkRow1Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m11Bare * (jS F 1) + m12Bare * (jS F 2) + m13Bare * (jS F 3) + m14Bare * (JmS F) + m15Bare * (pS F 2) + m16Bare * (pS F 3) = r1Bare := by
  sorry

theorem walkRow2Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m21Bare * (jS F 1) + m22Bare * (jS F 2) + m23Bare * (jS F 3) + m24Bare * (JmS F) + m25Bare * (pS F 2) + m26Bare * (pS F 3) = r2Bare := by
  sorry

theorem walkRow3Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m31Bare * (jS F 1) + m32Bare * (jS F 2) + m33Bare * (jS F 3) + m34Bare * (JmS F) + m35Bare * (pS F 2) + m36Bare * (pS F 3) = r3Bare := by
  sorry

theorem walkRow4Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m41Bare * (jS F 1) + m42Bare * (jS F 2) + m43Bare * (jS F 3) + m44Bare * (JmS F) + m45Bare * (pS F 2) + m46Bare * (pS F 3) = r4Bare := by
  sorry

theorem walkRow5Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m51Bare * (jS F 1) + m52Bare * (jS F 2) + m53Bare * (jS F 3) + m54Bare * (JmS F) + m55Bare * (pS F 2) + m56Bare * (pS F 3) = r5Bare := by
  sorry

theorem walkRow6Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    m61Bare * (jS F 1) + m62Bare * (jS F 2) + m63Bare * (jS F 3) + m64Bare * (JmS F) + m65Bare * (pS F 2) + m66Bare * (pS F 3) = r6Bare := by
  sorry

-- det(bare): valuation 18, coeff 18 = -64
noncomputable def detTupBare : PowerSeries ℚ :=
  ((-64) * X ^ 6 + 1376 * X ^ 8 + (-8176) * X ^ 10 + (-2312) * X ^ 12 + 116384 * X ^ 14 + (-156848) * X ^ 16 + 74448 * X ^ 18 + (-8424) * X ^ 20) + (64 * X ^ 6 + 64 * X ^ 7 + (-1184) * X ^ 8 + (-928) * X ^ 9 + 5264 * X ^ 10 + 1808 * X ^ 11 + 9648 * X ^ 12 + 14112 * X ^ 13 + (-77152) * X ^ 14 + (-18224) * X ^ 15 + 66576 * X ^ 16 + 12384 * X ^ 17 + (-18576) * X ^ 18) * Kernel.A + (64 * X ^ 6 + (-64) * X ^ 7 + (-1184) * X ^ 8 + 928 * X ^ 9 + 5264 * X ^ 10 + (-1808) * X ^ 11 + 9648 * X ^ 12 + (-14112) * X ^ 13 + (-77152) * X ^ 14 + 18224 * X ^ 15 + 66576 * X ^ 16 + (-12384) * X ^ 17 + (-18576) * X ^ 18) * Kernel.B + ((-64) * X ^ 6 + 1056 * X ^ 8 + (-3408) * X ^ 10 + (-13320) * X ^ 12 + 48568 * X ^ 14 + (-23352) * X ^ 16 + 2808 * X ^ 18) * (Kernel.A * Kernel.B)
-- DET_VALUATION_Bare = 18

/-! ### The bare system as a matrix -/

noncomputable def matBare : Matrix (Fin 6) (Fin 6) (PowerSeries ℚ) :=
  !![m11Bare, m12Bare, m13Bare, m14Bare, m15Bare, m16Bare;
    m21Bare, m22Bare, m23Bare, m24Bare, m25Bare, m26Bare;
    m31Bare, m32Bare, m33Bare, m34Bare, m35Bare, m36Bare;
    m41Bare, m42Bare, m43Bare, m44Bare, m45Bare, m46Bare;
    m51Bare, m52Bare, m53Bare, m54Bare, m55Bare, m56Bare;
    m61Bare, m62Bare, m63Bare, m64Bare, m65Bare, m66Bare]

noncomputable def rvecBare : Fin 6 → PowerSeries ℚ :=
  ![r1Bare, r2Bare, r3Bare, r4Bare, r5Bare, r6Bare]

/-- The six scaled numerators: column `c` carries `X^(E−e_c)·(D/d_c)`. -/
noncomputable def scaledNumBare : Fin 6 → PowerSeries ℚ :=
  ![X ^ 2 * numJ1Bare, X ^ 1 * 2 * numJ2Bare, numJ3Bare, X ^ 1 * numJmBare, X ^ 1 * numP2Bare, numP3Bare]

/-- The determinant of the cleared system, in closed basis form. -/
theorem det_matBare : (matBare).det = detTupBare := by
  sorry

/-- The determinant certificate: the order-18 coefficient is `−64`. -/
theorem coeff_detBare : coeff 18 (detTupBare) = -64 := by
  sorry

theorem det_ne_zeroBare : (matBare).det ≠ 0 := by
  sorry

/-- The walk satisfies the system (the six `walkRow` theorems, vectorized). -/
theorem mulVec_walkBare {F : St → Nat} (h : StartData F 1 0 1 1) :
    (matBare).mulVec (unkVec F) = rvecBare := by
  sorry

/-- The closed forms satisfy the system (the six `DepthOneKernelSol` rows,
vectorized and rescaled). -/
theorem mulVec_scaledNumBare :
    (matBare).mulVec (scaledNumBare) = (X ^ 3 * denAllBare) • rvecBare := by
  sorry

/-- Uniqueness: the two solutions of the cleared system agree after the
common `X^E·D` scaling (adjugate against the determinant, in the domain). -/
theorem unk_eqBare {F : St → Nat} (h : StartData F 1 0 1 1) (c : Fin 6) :
    (X ^ 3 * denAllBare) * unkVec F c = scaledNumBare c := by
  sorry

theorem transJ1Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 1 * denJ1Bare * (jS F 1) = numJ1Bare := by
  sorry

theorem transJ2Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 2 * denJ2Bare * (jS F 2) = numJ2Bare := by
  sorry

theorem transJ3Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 3 * denJ3Bare * (jS F 3) = numJ3Bare := by
  sorry

theorem transJmBare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 2 * denJmBare * (JmS F) = numJmBare := by
  sorry

theorem transP2Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 2 * denP2Bare * (pS F 2) = numP2Bare := by
  sorry

theorem transP3Bare {F : St → Nat} (h : StartData F 1 0 1 1) :
    X ^ 3 * denP3Bare * (pS F 3) = numP3Bare := by
  sorry


/-! ## Axiom audits (AuditOutworks pattern)

Expected: standard axioms only; `native_decide` (`Lean.ofReduceBool`) is
out of bounds here, as is anything beyond the standard three. -/

/--
info: 'Polyplets.GapWalk.transJ1Int' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms transJ1Int

/--
info: 'Polyplets.GapWalk.transP3Bare' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms transP3Bare

end GapWalk
end Polyplets
