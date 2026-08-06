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
import Polyplets.Upper.BuiRD2
import Polyplets.Upper.BuiRD3
import Polyplets.StairAnimals
import Polyplets.StairGrowth

/-!
# Audit: the Outworks results in one place

Single audit point for the second Lean campaign (`OUTWORKS-PLAN.md`), the
companion of `Grand/Audit.lean`. Every `#print axioms` below is wrapped in
`#guard_msgs`, so the build FAILS if any axiom set drifts from the recorded
expectation.

Expected footprints — every line below is ENFORCED by a guard in this file
(2026-07-31 adversarial-review fix: the instance `P₁` pins, the row-sum
gates, `universal_shape_d`, `lambda_lb`, the `n = 4` spot checks,
`maxhole_lower_banked` and `strip_sum_le_a` were previously asserted here
but unguarded):

* OW-1 — `a_eq_sum`, `strip_sum_le_a` standard three; the anchors
  `a_1 .. a_6` each carry exactly their own `native_decide` leaf (`a_6`
  guarded as the representative — it is the one consumed downstream by
  `lambda_lb`; `a_1 .. a_5` are certified through the guarded `Free_4`/
  `OneSided_4` consumers at `a_4` and otherwise advisory).
* OW-3 — `a_le_choose`, `choose_le_pow` standard three (the exploration
  injection is a proof, not a computation; no `native_decide` in the file).
* OW-2 — `a_supermul`, `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le`
  standard three; `lambda_gt` and `lambda_lb` add exactly the `a_6` leaf.
  Machine-checked bracket: `3.95 < λ ≤ 3125/256`. `lambda_gt_of_banked`
  (the conditional `6.22 < λ` from banked `a 40`) is standard three — its
  numeric input is a hypothesis, not a computation.
* OW-4 — `factorial_smul_int_coeff`, `production_factorial_int` standard.
* OW-7 — the three Burnside equations and `r90_vanish` standard three;
  the `n = 4` spot checks carry exactly the anchor leaves they are derived
  from (guarded below; the raw `R90_*`/`R180_*`/`Hm_*`/`Dm_*` anchors each
  carry their own leaf, certified at `n = 4` through the spot checks).
* OW-6 — `maxhole_lower`, `maxhole_lower_banked`, `card_le_of_diag_window`,
  `area_max`, `maxhole_upper`, `maxhole` standard three (the last two
  conditional on the named `MoatBound` hypothesis; the `decide` anchors are
  kernel-checked, axiom-free beyond `propext`).
* OW-8 — all four Northcott results standard three.
* OW-5 — the universal diagonal law (`universal_shape_d` included)
  standard three at every row-local lattice; the instance `P₁` pins carry
  exactly their two anchor-cell leaves; each row-sum gate carries exactly
  its own leaf; `kingP1_eq_Pp1` standard (the generic king `P₁` IS
  `Pin.lean`'s `Pp1`).
* Bui in Lean (`Upper/`) — the abstract certificate machinery
  (`BuiSystem.certSum_le`, `BuiSystem.pow_mul_le`, `lambda_le_of_pow_bound`,
  `lambda_le_of_buiSystem`, `RatCert.lambda_le`) standard three;
  `buiRD2_valid` is a kernel `decide` (`[propext]` only — no
  `native_decide`); the conditional `lambda_le_of_bui_rd2`
  (`λ ≤ 10⁶/106251` given `KingBuiSystemRD2Holds`) standard three.
  The RD=3 headline instance carries exactly the one `buiRD3_valid`
  native leaf (5930 rows are past what the kernel evaluator will do):
  `lambda_le_of_bui_rd3` (`λ ≤ 20000/2147` given `KingBuiSystemRD3Holds`)
  = standard three + that leaf.
* Sortie B1 (`StairAnimals.lean`) — `Stair.join_valid`, `Stair.cut_join`,
  `Stair.join_injOn` carry `[propext, Quot.sound]`, without
  `Classical.choice`: the join and the cut are computable. The counting layer
  over them (`StairGrowth.lean`: `Stair.M_supermul`, `Stair.M_tendsto`,
  `Stair.M_le_mu_pow`, `Stair.mu_le`, `Stair.mu_gt_of_banked`) is standard
  three — `Nat.card` and `Subadditive` bring `Classical.choice` — and carries
  no native leaf, the banked `M 700` being a hypothesis.
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

/-- info: 'Polyplets.strip_sum_le_a' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms strip_sum_le_a

/--
info: 'Polyplets.ratio_not_logConvex' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 a_1._native.native_decide.ax_1_1,
 a_2._native.native_decide.ax_1_1,
 a_3._native.native_decide.ax_1_1,
 a_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms ratio_not_logConvex

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

/--
info: 'Polyplets.lambda_lb' depends on axioms: [propext, Classical.choice, Quot.sound, a_6._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms lambda_lb

/-- info: 'Polyplets.lambda_gt_of_banked' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_gt_of_banked

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

/--
info: 'Polyplets.Free_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Dm_4._native.native_decide.ax_1_1,
 Hm_4._native.native_decide.ax_1_1,
 R180_4._native.native_decide.ax_1_1,
 R90_4._native.native_decide.ax_1_1,
 a_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Free_4

/--
info: 'Polyplets.OneSided_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 R180_4._native.native_decide.ax_1_1,
 R90_4._native.native_decide.ax_1_1,
 a_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms OneSided_4

/--
info: 'Polyplets.Bilateral_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Dm_4._native.native_decide.ax_1_1,
 Hm_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Bilateral_4

/-! ## OW-6: the diamond theorem -/

/-- info: 'Polyplets.maxhole_lower' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms maxhole_lower

/--
info: 'Polyplets.maxhole_lower_banked' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms maxhole_lower_banked

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

/--
info: 'Polyplets.Universal.universal_shape_d' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Universal.universal_shape_d

/-! ### OW-5 instance pins — each carries exactly its two anchor-cell leaves -/

/--
info: 'Polyplets.Universal.square_P1_pinned' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_square_3_2._native.native_decide.ax_1_1,
 Universal.T_square_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.square_P1_pinned

/--
info: 'Polyplets.Universal.square_P1_closed' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_square_3_2._native.native_decide.ax_1_1,
 Universal.T_square_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.square_P1_closed

/--
info: 'Polyplets.Universal.hex_P1_pinned' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_hex_3_2._native.native_decide.ax_1_1,
 Universal.T_hex_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.hex_P1_pinned

/--
info: 'Polyplets.Universal.hex_P1_closed' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_hex_3_2._native.native_decide.ax_1_1,
 Universal.T_hex_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.hex_P1_closed

/--
info: 'Polyplets.Universal.king_P1_pinned_via_universal' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_king_3_2._native.native_decide.ax_1_1,
 Universal.T_king_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_P1_pinned_via_universal

/--
info: 'Polyplets.Universal.king_P1_pinned_king_form' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_king_3_2._native.native_decide.ax_1_1,
 Universal.T_king_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_P1_pinned_king_form

/--
info: 'Polyplets.Universal.king_P1_closed_via_universal' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.T_king_3_2._native.native_decide.ax_1_1,
 Universal.T_king_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_P1_closed_via_universal

/-! ### OW-5 cross-family gates — each carries exactly its own leaf -/

/--
info: 'Polyplets.Universal.square_rowSum_3' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.square_rowSum_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.square_rowSum_3

/--
info: 'Polyplets.Universal.square_rowSum_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.square_rowSum_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.square_rowSum_4

/--
info: 'Polyplets.Universal.square_rowSum_5' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.square_rowSum_5._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.square_rowSum_5

/--
info: 'Polyplets.Universal.hex_rowSum_3' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.hex_rowSum_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.hex_rowSum_3

/--
info: 'Polyplets.Universal.hex_rowSum_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.hex_rowSum_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.hex_rowSum_4

/--
info: 'Polyplets.Universal.hex_rowSum_5' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.hex_rowSum_5._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.hex_rowSum_5

/--
info: 'Polyplets.Universal.king_rowSum_3' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.king_rowSum_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_rowSum_3

/--
info: 'Polyplets.Universal.king_rowSum_4' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.king_rowSum_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_rowSum_4

/--
info: 'Polyplets.Universal.king_rowSum_5' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 Universal.king_rowSum_5._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms Universal.king_rowSum_5

/-! ## Bui in Lean: the convolution-certificate upper bound -/

/--
info: 'Polyplets.BuiSystem.certSum_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms BuiSystem.certSum_le

/--
info: 'Polyplets.BuiSystem.pow_mul_le' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms BuiSystem.pow_mul_le

/--
info: 'Polyplets.lambda_le_of_pow_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms lambda_le_of_pow_bound

/--
info: 'Polyplets.lambda_le_of_buiSystem' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms lambda_le_of_buiSystem

/-- info: 'Polyplets.RatCert.lambda_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RatCert.lambda_le

/-- info: 'Polyplets.buiRD2_valid' depends on axioms: [propext] -/
#guard_msgs in
#print axioms buiRD2_valid

/--
info: 'Polyplets.lambda_le_of_bui_rd2' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms lambda_le_of_bui_rd2

/--
info: 'Polyplets.buiRD3_valid' depends on axioms: [propext, buiRD3_valid._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms buiRD3_valid

/--
info: 'Polyplets.lambda_le_of_bui_rd3' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 buiRD3_valid._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms lambda_le_of_bui_rd3

/-! ## Sortie B1: the staircase column-join

`results/hv-growth-sandwich.md` Lemma 3. The join stays in the class and is
injective once both areas are fixed, which is what makes the staircase count
supermultiplicative on the nose. Not even `Classical.choice` -- the join and
the cut are computable and the proofs are constructive.
-/

/-- info: 'Polyplets.Stair.join_valid' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms Stair.join_valid

/-- info: 'Polyplets.Stair.cut_join' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms Stair.cut_join

/-- info: 'Polyplets.Stair.join_injOn' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms Stair.join_injOn

/-! ## The staircase growth constant `µ`

`StairGrowth.lean`: the counting layer over B1, and Fekete. `M_supermul` is
Lemma 3 as a cardinality — the statement `make gate-middle-kingdom` can only
check on 700 terms, here for all `i` and `j`. `M_le_mu_pow` is the
limit-is-supremum half that makes every banked term a floor, and
`mu_gt_of_banked` cashes one in. Classical choice enters through `Nat.card` and
Mathlib's `Subadditive`; no `native_decide` leaf anywhere — the banked `M 700`
is a hypothesis, as in `lambda_gt_of_banked`.
-/

/--
info: 'Polyplets.Stair.M_supermul' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Stair.M_supermul

/-- info: 'Polyplets.Stair.M_tendsto' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.M_tendsto

/--
info: 'Polyplets.Stair.M_le_mu_pow' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Stair.M_le_mu_pow

/-- info: 'Polyplets.Stair.mu_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.mu_le

/--
info: 'Polyplets.Stair.mu_gt_of_banked' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms Stair.mu_gt_of_banked

end Polyplets
