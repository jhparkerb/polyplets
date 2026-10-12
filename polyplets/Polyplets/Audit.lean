/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Report

/-!
# Axiom audit

Every theorem of `Report.lean`, and the internal results they rest on, must
depend on the standard three axioms only. Each `#print axioms` below is wrapped
in `#guard_msgs`, so the build fails if any footprint drifts.
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

end Polyplets
