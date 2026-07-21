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
Expected output, recorded in `PROOF-STATUS.md`:

* `d_mu_rec`, `T_staircase`, `grand_form`, `grand_form_prod` —
  `[propext, Classical.choice, Quot.sound]` (standard only; no
  `native_decide` anywhere in the cone).
* `mu_one`, `lead_coeff_25`, `shape_lead` — standard + the `V_1_1`
  `native_decide` leaf.
* `P16_grand_of_banked` — standard + the `P3_pinned` heavy-k=3
  `native_decide` set (weights/chunks/base enumerations); its 26 explicit
  hypotheses are the level-4..16 anchor pairs, every one a real-swept cell
  with `H ≤ 18`.
-/

namespace Polyplets

#print axioms d_mu_rec
#print axioms T_staircase
#print axioms grand_form
#print axioms grand_form_prod
#print axioms mu_one
#print axioms lead_coeff_25
#print axioms shape_lead
#print axioms P16_grand_of_banked

end Polyplets
