/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.GapWalkBridge
import Polyplets.DepthOneConstants

/-!
# Notary wave 2: `Φ` annihilates the walk series — finitely, in Lean

Campaign *Notary* (`docs/notary-lean-plan.md (deleted)`; wave-2 scope note in
`docs/notary-kernel-scoping.md (deleted)`). `DepthOneConstants.lean` pins the quartic
`Φ` and its branch data; `GapWalkBridge.lean` closes the assembly at
`k ≤ 8` and pins the walk to `k ≤ 19`. This module extends the finite anchor
to the algebraic claim itself:

* `nSeries` — the integer series `N(x) = 3·F₁(3x) + 1` of
  `results/below-onset.md` §3, built from the walk assembly
  `F₁ = P̂ − B²/(3+S)` (`GapWalkBridge.f1Series`);
* `n_matches_banked` — its coefficients at `k ≤ 19` against the banked
  two-source numerators (`N_k = 3^(k+1)·D_1(k)`);
* `phi_annihilates` — **`Φ(x, N(x)) ≡ 0 mod x^61`**, exact rational
  arithmetic, `native_decide`. The `(8,4)` fit that produced `Φ` used series
  orders `0..56`; the kernel-method derivation used none. A Lean check to
  order 60 is therefore holdout past the fit window on the fitted route and
  fully independent data on the derived route.
* `phiCList_eval_*` — the coefficient lists used here evaluate to the
  `DepthOneConstants.phiC*` polynomials: the two modules pin the same `Φ`.

What this module does **not** prove: `Φ(x, N(x)) = 0` at all orders — that
is the kernel-method formalization priced in
`docs/notary-kernel-scoping.md (deleted)` (piece K). This is the strongest finite
statement short of it.

Provenance of the literals: `build/notary_series_check.py` (log
`build/notary_series_check.log`) recomputes both theorem statements in
exact arithmetic from `experiments/depth1_gap_walk.py` +
`experiments/depth1_recurrence.py::PHI_COEFFS`; the `k ≤ 19` numerators
match the banked defect of `results/below-onset.md` §2–3.
-/

namespace Polyplets
namespace DepthOneSeries

open GapWalkBridge

/-- `N(x) = 3·F₁(3x) + 1` truncated at `x^K`: coefficient `k` is
`3^(k+1) · [y^k]F₁` plus the `+1` at `k = 0`. Integer-valued (in `ℚ`). -/
def nSeries (K : ℕ) : List ℚ :=
  let f1 := f1Series K
  (List.range (K + 1)).map fun k =>
    3 ^ (k + 1) * f1.getD k 0 + if k = 0 then 1 else 0

/-- The walk series against the banked numerators, `k ≤ 19`
(`N_k = 3^(k+1) D_1(k)`; `4, 80, 1753, …` are `lead(R_k)` up to sign,
`results/below-onset.md` §2). -/
theorem n_matches_banked :
    (nSeries 19) =
      [0, 4, 80, 1753, 40928, 987355, 24323825, 607833256, 15348306104,
        390644841751, 10005018039887, 257541479547202, 6657119707685177,
        172680956445731314, 4492576464734738672, 117181887700179597973,
        3063340649106577472792, 80238354502426558817167,
        2105343902604309083418359, 55326941647956397207781050] := by
  native_decide

/-! ## The quartic's coefficients, as series -/

/-- `x`-coefficients of the `W^0` coefficient of `Φ` (degrees `0..8`). -/
def phiCList0 : List ℚ :=
  [0, -64, 2736, 16560, -4920, -63720, 89667, -30618, 19683]

/-- `W^1`. -/
def phiCList1 : List ℚ :=
  [16, -1580, 25920, 144249, -175746, -537516, 989982, -461457, 236196]

/-- `W^2`. -/
def phiCList2 : List ℚ :=
  [144, -8808, 115470, 514107, -1174698, -1324026, 4153842, -2421009, 1062882]

/-- `W^3`. -/
def phiCList3 : List ℚ :=
  [420, -21803, 254538, 870723, -3116316, -488133, 7413930, -5373459, 2125764]

/-- `W^4`. -/
def phiCList4 : List ℚ :=
  [392, -20719, 257193, 564573, -3338583, 2238435, 4323699, -4310577, 1594323]

/-- `Φ(x, N)` on truncated series: `Σ_j c_j(x) · N(x)^j`, coefficients
`0..n−1`. -/
def phiApply (nser : List ℚ) (n : ℕ) : List ℚ :=
  let n1 := tmul nser nser n
  let n2 := tmul n1 nser n
  let n3 := tmul n2 nser n
  let one : List ℚ := 1 :: List.replicate (n - 1) 0
  [phiCList0, phiCList1, phiCList2, phiCList3, phiCList4].zipWith
      (fun c p => tmul c p n) [one, nser, n1, n2, n3]
    |>.foldl (fun acc t => (List.range n).map fun k =>
        acc.getD k 0 + t.getD k 0) (List.replicate n 0)

/-- **`Φ` annihilates the walk series through `x^60`.** The `(8,4)` fit
behind `Φ` used orders `0..56`; the kernel derivation used none. -/
theorem phi_annihilates :
    (phiApply (nSeries 60) 61).all (· == 0) = true := by
  native_decide

/-! ## The two pins of `Φ` are the same `Φ` -/

/-- Horner evaluation of a coefficient list. -/
def evalPoly (c : List ℚ) (x : ℚ) : ℚ := c.foldr (fun a acc => a + x * acc) 0

theorem phiCList0_eval (x : ℚ) :
    evalPoly phiCList0 x = DepthOneConstants.phiC0 x := by
  simp only [evalPoly, phiCList0, DepthOneConstants.phiC0, List.foldr]; ring

theorem phiCList1_eval (x : ℚ) :
    evalPoly phiCList1 x = DepthOneConstants.phiC1 x := by
  simp only [evalPoly, phiCList1, DepthOneConstants.phiC1, List.foldr]; ring

theorem phiCList2_eval (x : ℚ) :
    evalPoly phiCList2 x = DepthOneConstants.phiC2 x := by
  simp only [evalPoly, phiCList2, DepthOneConstants.phiC2, List.foldr]; ring

theorem phiCList3_eval (x : ℚ) :
    evalPoly phiCList3 x = DepthOneConstants.phiC3 x := by
  simp only [evalPoly, phiCList3, DepthOneConstants.phiC3, List.foldr]; ring

theorem phiCList4_eval (x : ℚ) :
    evalPoly phiCList4 x = DepthOneConstants.phiC4 x := by
  simp only [evalPoly, phiCList4, DepthOneConstants.phiC4, List.foldr]; ring

/-! ## Axiom audits (AuditOutworks pattern) -/

/--
info: 'Polyplets.DepthOneSeries.n_matches_banked' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 n_matches_banked._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms n_matches_banked

/--
info: 'Polyplets.DepthOneSeries.phi_annihilates' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 phi_annihilates._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms phi_annihilates

/-- info: 'Polyplets.DepthOneSeries.phiCList4_eval' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms phiCList4_eval

end DepthOneSeries
end Polyplets
