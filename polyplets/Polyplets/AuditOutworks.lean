/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Sequence
import Polyplets.UpperBound
import Polyplets.Growth
import Polyplets.IntCoeff
import Polyplets.Symmetry
import Polyplets.Holes
import Polyplets.HolesUpper
import Polyplets.Northcott
import Polyplets.Universal.King
import Polyplets.Universal.Square
import Polyplets.Universal.Hex

/-!
# Audit: the Outworks results in one place

Single audit point for the second Lean campaign (`OUTWORKS-PLAN.md`), the
companion of `Grand/Audit.lean`. Every `#print axioms` below is wrapped in
`#guard_msgs`, so the build FAILS if any axiom set drifts from the recorded
expectation.

Expected footprints, recorded in `PROOF-STATUS.md`:

* OW-1 — `a_eq_sum` standard three; the anchors `a_1 .. a_6` each carry
  exactly their own `native_decide` leaf (`a_6` guarded below as the
  representative: it is the one consumed downstream by `lambda_lb`).
* OW-3 — `a_le_choose`, `choose_le_pow` standard three (the exploration
  injection is a proof, not a computation; no `native_decide` in the file).
* OW-2 — `a_supermul`, `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le`
  standard three; `lambda_gt`/`lambda_lb` add exactly the `a_6` leaf.
  Machine-checked bracket: `3.95 < λ ≤ 3125/256`.
* OW-4 — `factorial_smul_int_coeff`, `production_factorial_int` standard.
* OW-7 — the three Burnside equations and `r90_vanish` standard three;
  the `n = 4` spot checks carry the anchor leaves they are derived from.
* OW-6 — `maxhole_lower`, `card_le_of_diag_window`, `area_max`,
  `maxhole_upper`, `maxhole` standard three (the last two conditional on
  the named `MoatBound` hypothesis; anchors are kernel `decide`, hence
  axiom-free beyond `propext`).
* OW-8 — all four Northcott results standard three.
* OW-5 — the universal diagonal law standard three at every row-local
  lattice; the instance `P₁` pins carry exactly their two anchor-cell
  leaves; `kingP1_eq_Pp1` standard (the generic king `P₁` IS `Pin.lean`'s).
-/

namespace Polyplets

/-! ## OW-1: the sequence -/

/-- info: 'Polyplets.a_eq_sum' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_eq_sum

/--
info: 'Polyplets.a_6' depends on axioms: [propext, Classical.choice, Quot.sound, a_6._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms a_6

/-! ## OW-3: the corset -/

/-- info: 'Polyplets.a_le_choose' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_le_choose

/-- info: 'Polyplets.choose_le_pow' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms choose_le_pow

/-! ## OW-2: the growth constant -/

/-- info: 'Polyplets.a_supermul' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_supermul

/-- info: 'Polyplets.lambda_tendsto' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_tendsto

/-- info: 'Polyplets.a_le_lambda_pow' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_le_lambda_pow

/-- info: 'Polyplets.lambda_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_le

/--
info: 'Polyplets.lambda_gt' depends on axioms: [propext, Classical.choice, Quot.sound, a_6._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms lambda_gt

/-! ## OW-4: the factorial residue -/

/--
info: 'Polyplets.factorial_smul_int_coeff' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms factorial_smul_int_coeff

/--
info: 'Polyplets.production_factorial_int' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms production_factorial_int

/-! ## OW-7: the Burnside apparatus -/

/-- info: 'Polyplets.free_eq' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms free_eq

/-- info: 'Polyplets.oneSided_eq' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms oneSided_eq

/-- info: 'Polyplets.bilateral_eq' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms bilateral_eq

/-- info: 'Polyplets.r90_vanish' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms r90_vanish

/-! ## OW-6: the diamond theorem -/

/-- info: 'Polyplets.maxhole_lower' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms maxhole_lower

/--
info: 'Polyplets.card_le_of_diag_window' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms card_le_of_diag_window

/-- info: 'Polyplets.area_max' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms area_max

/-- info: 'Polyplets.maxhole_upper' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms maxhole_upper

/-- info: 'Polyplets.maxhole' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms maxhole

/-! ## OW-8: Northcott -/

/--
info: 'Polyplets.mahlerMeasure_minpoly_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms mahlerMeasure_minpoly_le

/--
info: 'Polyplets.finite_setOf_isIntegral_of_house_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms finite_setOf_isIntegral_of_house_le

/--
info: 'Polyplets.finite_setOf_degree_le_of_house_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms finite_setOf_degree_le_of_house_le

/--
info: 'Polyplets.unbounded_degree_of_house_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms unbounded_degree_of_house_le

/-! ## OW-5: the universal diagonal law -/

/--
info: 'Polyplets.Universal.universal_shape' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Universal.universal_shape

/--
info: 'Polyplets.Universal.universal_shape_production' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Universal.universal_shape_production

/--
info: 'Polyplets.Universal.universal_production_int_all' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Universal.universal_production_int_all

/--
info: 'Polyplets.Universal.kingP1_eq_Pp1' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Universal.kingP1_eq_Pp1

end Polyplets
