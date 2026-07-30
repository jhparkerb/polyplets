/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Grand.Lead
import Polyplets.Grand.PinGrand

/-!
# Audit: the grand-form results in one place

Single audit point for the staircase formalization (`GRANDFORM-PLAN.md`).
Every `#print axioms` below is wrapped in `#guard_msgs`, so the build FAILS
if any axiom set drifts from the recorded expectation (previously these were
advisory; hardened 2026-07-21, `docs/lean-hostile-witness.md`).

Expected footprints, recorded in `PROOF-STATUS.md`:

* `d_mu_rec`, `T_staircase`, `grand_form`, `grand_form_prod` —
  `[propext, Classical.choice, Quot.sound]` (standard only; no
  `native_decide` anywhere in the cone).
* `mu_one`, `lead_coeff_25`, `shape_lead` — standard + the `V_1_1`
  `native_decide` leaf.
* `P16_grand_of_banked` — standard + the `P3_pinned` heavy-k=3
  `native_decide` set (weights/chunks/base enumerations); its 26 explicit
  hypotheses are the level-4..16 anchor pairs, every one a real-swept cell
  with `H ≤ 18`.
* `P18_grand_of_banked` (a(40)-close extension, 2026-07-29) — same
  footprint; its 30 explicit hypotheses are the level-4..18 anchor pairs,
  every one a real-swept cell with `H ≤ 20`.
* `shape_d`, `shape`, `shape_production`, `production_int_all`, `d_rec`,
  `c_ident` — standard only; this is the enforcement of `PROOF-STATUS.md`'s
  "no `native_decide` anywhere in the Shape/Peel/Separation path".
* `P1_closed` — standard + the `T_3_2`/`T_4_3` value leaves.
  `P2_closed` — standard + `T_5_3` and the j ≤ 2 weight/`d` leaves.
  `P3_pinned` — standard + the full heavy-k=3 set (15 `CFGVchunk` cards
  plus the weight/`d` leaves).
-/

namespace Polyplets

/-- info: 'Polyplets.d_mu_rec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms d_mu_rec

/-- info: 'Polyplets.T_staircase' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms T_staircase

/-- info: 'Polyplets.grand_form' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms grand_form

/-- info: 'Polyplets.grand_form_prod' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms grand_form_prod

/--
info: 'Polyplets.mu_one' depends on axioms: [propext, Classical.choice, Quot.sound, V_1_1._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms mu_one

/--
info: 'Polyplets.lead_coeff_25' depends on axioms: [propext, Classical.choice, Quot.sound, V_1_1._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms lead_coeff_25

/--
info: 'Polyplets.shape_lead' depends on axioms: [propext, Classical.choice, Quot.sound, V_1_1._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms shape_lead

/--
info: 'Polyplets.P16_grand_of_banked' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 CFGVchunk_card_n1._native.native_decide.ax_1_1,
 CFGVchunk_card_n2._native.native_decide.ax_1_1,
 CFGVchunk_card_n3._native.native_decide.ax_1_1,
 CFGVchunk_card_n4._native.native_decide.ax_1_1,
 CFGVchunk_card_n5._native.native_decide.ax_1_1,
 CFGVchunk_card_n6._native.native_decide.ax_1_1,
 CFGVchunk_card_n7._native.native_decide.ax_1_1,
 CFGVchunk_card_p0._native.native_decide.ax_1_1,
 CFGVchunk_card_p1._native.native_decide.ax_1_1,
 CFGVchunk_card_p2._native.native_decide.ax_1_1,
 CFGVchunk_card_p3._native.native_decide.ax_1_1,
 CFGVchunk_card_p4._native.native_decide.ax_1_1,
 CFGVchunk_card_p5._native.native_decide.ax_1_1,
 CFGVchunk_card_p6._native.native_decide.ax_1_1,
 CFGVchunk_card_p7._native.native_decide.ax_1_1,
 T_1_1._native.native_decide.ax_1_1,
 T_3_2._native.native_decide.ax_1_1,
 T_4_3._native.native_decide.ax_1_1,
 T_5_3._native.native_decide.ax_1_1,
 V_1_1._native.native_decide.ax_1_1,
 V_1_2._native.native_decide.ax_1_1,
 V_1_3._native.native_decide.ax_1_1,
 V_2_2._native.native_decide.ax_1_1,
 V_2_3._native.native_decide.ax_1_1,
 Vt_1_1._native.native_decide.ax_1_1,
 Vt_1_2._native.native_decide.ax_1_1,
 Vt_1_3._native.native_decide.ax_1_1,
 Vt_2_2._native.native_decide.ax_1_1,
 Vt_2_3._native.native_decide.ax_1_1,
 Vt_3_3._native.native_decide.ax_1_1,
 d_0_1._native.native_decide.ax_1_1,
 d_0_2._native.native_decide.ax_1_1,
 d_0_3._native.native_decide.ax_1_1,
 d_0_4._native.native_decide.ax_1_1,
 d_1_2._native.native_decide.ax_1_1,
 d_1_3._native.native_decide.ax_1_1,
 d_2_3._native.native_decide.ax_1_1,
 d_2_4._native.native_decide.ax_1_1,
 d_3_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms P16_grand_of_banked

/--
info: 'Polyplets.P18_grand_of_banked' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 CFGVchunk_card_n1._native.native_decide.ax_1_1,
 CFGVchunk_card_n2._native.native_decide.ax_1_1,
 CFGVchunk_card_n3._native.native_decide.ax_1_1,
 CFGVchunk_card_n4._native.native_decide.ax_1_1,
 CFGVchunk_card_n5._native.native_decide.ax_1_1,
 CFGVchunk_card_n6._native.native_decide.ax_1_1,
 CFGVchunk_card_n7._native.native_decide.ax_1_1,
 CFGVchunk_card_p0._native.native_decide.ax_1_1,
 CFGVchunk_card_p1._native.native_decide.ax_1_1,
 CFGVchunk_card_p2._native.native_decide.ax_1_1,
 CFGVchunk_card_p3._native.native_decide.ax_1_1,
 CFGVchunk_card_p4._native.native_decide.ax_1_1,
 CFGVchunk_card_p5._native.native_decide.ax_1_1,
 CFGVchunk_card_p6._native.native_decide.ax_1_1,
 CFGVchunk_card_p7._native.native_decide.ax_1_1,
 T_1_1._native.native_decide.ax_1_1,
 T_3_2._native.native_decide.ax_1_1,
 T_4_3._native.native_decide.ax_1_1,
 T_5_3._native.native_decide.ax_1_1,
 V_1_1._native.native_decide.ax_1_1,
 V_1_2._native.native_decide.ax_1_1,
 V_1_3._native.native_decide.ax_1_1,
 V_2_2._native.native_decide.ax_1_1,
 V_2_3._native.native_decide.ax_1_1,
 Vt_1_1._native.native_decide.ax_1_1,
 Vt_1_2._native.native_decide.ax_1_1,
 Vt_1_3._native.native_decide.ax_1_1,
 Vt_2_2._native.native_decide.ax_1_1,
 Vt_2_3._native.native_decide.ax_1_1,
 Vt_3_3._native.native_decide.ax_1_1,
 d_0_1._native.native_decide.ax_1_1,
 d_0_2._native.native_decide.ax_1_1,
 d_0_3._native.native_decide.ax_1_1,
 d_0_4._native.native_decide.ax_1_1,
 d_1_2._native.native_decide.ax_1_1,
 d_1_3._native.native_decide.ax_1_1,
 d_2_3._native.native_decide.ax_1_1,
 d_2_4._native.native_decide.ax_1_1,
 d_3_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms P18_grand_of_banked

/-!
## The Shape/Peel chain (added 2026-07-30, AUDIT-2026-07-30 L3)

The guards above covered only the Grand results, so the headline claim
"Shape/Peel/Separation carry no `native_decide` anywhere" was advisory
prose in `PROOF-STATUS.md` with nothing enforcing it.  These guards make
that claim fail the build if it ever stops being true.
-/

/-- info: 'Polyplets.shape_d' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms shape_d

/-- info: 'Polyplets.shape' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms shape

/-- info: 'Polyplets.shape_production' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms shape_production

/--
info: 'Polyplets.production_int_all' depends on axioms: [propext, Classical.choice, Quot.sound]
-/
#guard_msgs in
#print axioms production_int_all

/-- info: 'Polyplets.d_rec' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms d_rec

/-- info: 'Polyplets.c_ident' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms c_ident

/--
info: 'Polyplets.P1_closed' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 T_3_2._native.native_decide.ax_1_1,
 T_4_3._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms P1_closed

/--
info: 'Polyplets.P2_closed' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 T_5_3._native.native_decide.ax_1_1,
 V_1_1._native.native_decide.ax_1_1,
 V_1_2._native.native_decide.ax_1_1,
 V_2_2._native.native_decide.ax_1_1,
 Vt_1_1._native.native_decide.ax_1_1,
 Vt_1_2._native.native_decide.ax_1_1,
 Vt_2_2._native.native_decide.ax_1_1,
 d_0_2._native.native_decide.ax_1_1,
 d_0_3._native.native_decide.ax_1_1,
 d_0_4._native.native_decide.ax_1_1,
 d_1_3._native.native_decide.ax_1_1,
 d_2_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms P2_closed

/--
info: 'Polyplets.P3_pinned' depends on axioms: [propext,
 Classical.choice,
 Quot.sound,
 CFGVchunk_card_n1._native.native_decide.ax_1_1,
 CFGVchunk_card_n2._native.native_decide.ax_1_1,
 CFGVchunk_card_n3._native.native_decide.ax_1_1,
 CFGVchunk_card_n4._native.native_decide.ax_1_1,
 CFGVchunk_card_n5._native.native_decide.ax_1_1,
 CFGVchunk_card_n6._native.native_decide.ax_1_1,
 CFGVchunk_card_n7._native.native_decide.ax_1_1,
 CFGVchunk_card_p0._native.native_decide.ax_1_1,
 CFGVchunk_card_p1._native.native_decide.ax_1_1,
 CFGVchunk_card_p2._native.native_decide.ax_1_1,
 CFGVchunk_card_p3._native.native_decide.ax_1_1,
 CFGVchunk_card_p4._native.native_decide.ax_1_1,
 CFGVchunk_card_p5._native.native_decide.ax_1_1,
 CFGVchunk_card_p6._native.native_decide.ax_1_1,
 CFGVchunk_card_p7._native.native_decide.ax_1_1,
 V_1_1._native.native_decide.ax_1_1,
 V_1_2._native.native_decide.ax_1_1,
 V_1_3._native.native_decide.ax_1_1,
 V_2_2._native.native_decide.ax_1_1,
 V_2_3._native.native_decide.ax_1_1,
 Vt_1_1._native.native_decide.ax_1_1,
 Vt_1_2._native.native_decide.ax_1_1,
 Vt_1_3._native.native_decide.ax_1_1,
 Vt_2_2._native.native_decide.ax_1_1,
 Vt_2_3._native.native_decide.ax_1_1,
 Vt_3_3._native.native_decide.ax_1_1,
 d_0_1._native.native_decide.ax_1_1,
 d_0_2._native.native_decide.ax_1_1,
 d_0_3._native.native_decide.ax_1_1,
 d_0_4._native.native_decide.ax_1_1,
 d_1_2._native.native_decide.ax_1_1,
 d_1_3._native.native_decide.ax_1_1,
 d_2_3._native.native_decide.ax_1_1,
 d_2_4._native.native_decide.ax_1_1,
 d_3_4._native.native_decide.ax_1_1]
-/
#guard_msgs in
#print axioms P3_pinned

end Polyplets
