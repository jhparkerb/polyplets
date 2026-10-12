/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Report
import Polyplets.StairGrowth
import Polyplets.Universal.System
import Polyplets.Upper.BuiRD2
import Polyplets.Upper.BuiRD3

/-!
# Axiom audit

Every theorem of `Report.lean`, the internal results they rest on, and the
headline theorems the L-papers cite must depend on the standard three axioms
only. Each `#print axioms` below is wrapped in `#guard_msgs`, so the build
fails if any footprint drifts.
-/

namespace Polyplets

/-! ## The report's claims -/

/-- info: 'Polyplets.report_a_eq_sum' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_a_eq_sum

/-- info: 'Polyplets.report_T_diag' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_T_diag

/-- info: 'Polyplets.report_diagonal_law' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_diagonal_law

/-- info: 'Polyplets.report_leading_coeff' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_leading_coeff

/-- info: 'Polyplets.report_pin_row_3k' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_pin_row_3k

/-- info: 'Polyplets.report_T_n_nm1' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_T_n_nm1

/-- info: 'Polyplets.P2_closed' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms P2_closed

/-- info: 'Polyplets.Enum.L_spec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Enum.L_spec

/-- info: 'Polyplets.report_Pk_known' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_Pk_known

/-- info: 'Polyplets.report_free' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_free

/-- info: 'Polyplets.report_oneSided' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_oneSided

/-- info: 'Polyplets.report_bilateral' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_bilateral

/-- info: 'Polyplets.report_growth' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_growth

/-- info: 'Polyplets.report_symmetryRatio' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_symmetryRatio

/-! ## The results they rest on -/

/-- info: 'Polyplets.shape_production' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms shape_production

/-- info: 'Polyplets.production_int_all' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms production_int_all

/-- info: 'Polyplets.d_mu_rec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms d_mu_rec

/-- info: 'Polyplets.T_staircase' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms T_staircase

/-- info: 'Polyplets.grand_all' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms grand_all

/-- info: 'Polyplets.Pk_prod' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Pk_prod

/-- info: 'Polyplets.lambda_gt_of_banked' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_gt_of_banked

/-! ## The L-papers' headline theorems -/

/-- info: 'Polyplets.a_supermul' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_supermul

/-- info: 'Polyplets.a_le_choose' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms a_le_choose

/-- info: 'Polyplets.choose_le_pow' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms choose_le_pow

/-- info: 'Polyplets.r90_vanish' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms r90_vanish

/-- info: 'Polyplets.Universal.universal_shape_d' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Universal.universal_shape_d

/-- info: 'Polyplets.Universal.universal_shape' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Universal.universal_shape

/-- info: 'Polyplets.Universal.universal_shape_production' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Universal.universal_shape_production

/-- info: 'Polyplets.Universal.universal_production_int_all' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Universal.universal_production_int_all

/-- info: 'Polyplets.Stair.M_supermul' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.M_supermul

/-- info: 'Polyplets.Stair.M_tendsto' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.M_tendsto

/-- info: 'Polyplets.Stair.M_le_mu_pow' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.M_le_mu_pow

/-- info: 'Polyplets.Stair.mu_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.mu_le

/-- info: 'Polyplets.Stair.mu_gt_of_banked' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Stair.mu_gt_of_banked

/-- info: 'Polyplets.BuiSystem.certSum_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms BuiSystem.certSum_le

/-- info: 'Polyplets.RatCert.lambda_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RatCert.lambda_le

/-- info: 'Polyplets.lambda_le_of_bui_rd2' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_le_of_bui_rd2

/-- info: 'Polyplets.lambda_le_of_bui_rd3' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_le_of_bui_rd3

end Polyplets
