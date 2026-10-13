/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Report
import Polyplets.RowLocal.Hex
import Polyplets.RowLocal.Square
import Polyplets.StairGrowth
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

/-- info: 'Polyplets.report_Pk_degree' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_Pk_degree

/-- info: 'Polyplets.report_pin_row_3k' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_pin_row_3k

/-- info: 'Polyplets.report_T_sub_one' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_T_sub_one

/-- info: 'Polyplets.T_sub_two' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms T_sub_two

/-- info: 'Polyplets.RowLocal.hex_T_sub_one' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.hex_T_sub_one

/-- info: 'Polyplets.RowLocal.square_T_sub_one' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.square_T_sub_one

/-- info: 'Polyplets.Enum.boards_spec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Enum.boards_spec

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

/-- info: 'Polyplets.report_asymmetric' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_asymmetric

/-- info: 'Polyplets.report_growth' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_growth

/-- info: 'Polyplets.report_symmetryRatio' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms report_symmetryRatio

/-! ## The results they rest on -/

/-- info: 'Polyplets.exists_isDiagonalPoly' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms exists_isDiagonalPoly

/-- info: 'Polyplets.IsDiagonalPoly.intValued' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms IsDiagonalPoly.intValued

/-- info: 'Polyplets.d_staircase' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms d_staircase

/-- info: 'Polyplets.T_staircase' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms T_staircase

/-- info: 'Polyplets.climb' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms climb

/-- info: 'Polyplets.isDiagonalPoly_Pk' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms isDiagonalPoly_Pk

/-- info: 'Polyplets.lambda_gt_of_a_40' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms lambda_gt_of_a_40

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

/-- info: 'Polyplets.R90_eq_zero' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms R90_eq_zero

/-- info: 'Polyplets.RowLocal.exists_delta' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.exists_delta

/-- info: 'Polyplets.RowLocal.exists_q' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.exists_q

/-- info: 'Polyplets.RowLocal.exists_isDiagonalPoly' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.exists_isDiagonalPoly

/-- info: 'Polyplets.RowLocal.TopRowRecursion.IsDiagonalPoly.intValued' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms RowLocal.TopRowRecursion.IsDiagonalPoly.intValued

/-- info: 'Polyplets.Staircase.M_supermul' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Staircase.M_supermul

/-- info: 'Polyplets.Staircase.M_tendsto' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Staircase.M_tendsto

/-- info: 'Polyplets.Staircase.M_le_mu_pow' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Staircase.M_le_mu_pow

/-- info: 'Polyplets.Staircase.mu_le' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Staircase.mu_le

/-- info: 'Polyplets.Staircase.mu_gt_of_M_700' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms Staircase.mu_gt_of_M_700

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
