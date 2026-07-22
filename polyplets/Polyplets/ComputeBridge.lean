/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Compute

/-!
# ComputeBridge: completing the definitional bridge to the banked triangle

`Compute.lean` machine-checks a sparse set of nine nonzero cells against
`results/triangle.txt`. The hostile-witness audit (2026-07-21,
`docs/lean-hostile-witness.md`) found that set thinner than the prose
implied: the remaining nonzero `n ≤ 5` cells were unchecked, and the two
`n = 6` probes existed only as an "verified out-of-file" comment. This
module makes every nonzero cell with `n ≤ 5` — the full rows 1..5 — plus
the two `n = 6` probes real kernel-recorded theorems, so the claim
"Lean's `T` is the engine's `T(n,H)`" rests entirely on in-tree,
build-checked facts.

Kept out of `Compute.lean` so its (multi-minute) `native_decide` runs do
not sit on the critical path of the main proof chain's rebuilds; nothing
imports this module except the root aggregator.
-/

namespace Polyplets

set_option linter.style.nativeDecide false

/-- `T 4 1 = 1`: the horizontal king tetromino strip. -/
theorem T_4_1 : T 4 1 = 1 := by rw [← Tc_eq_T]; native_decide

/-- `T 4 2 = 27` (banked, `results/triangle.txt`). -/
theorem T_4_2 : T 4 2 = 27 := by rw [← Tc_eq_T]; native_decide

/-- `T 4 4 = 27 = 3^3`, the diagonal value `T(n,n) = 3^(n-1)` at `n = 4`. -/
theorem T_4_4 : T 4 4 = 27 := by rw [← Tc_eq_T]; native_decide

/-- `T 5 1 = 1`: the horizontal king pentomino strip. -/
theorem T_5_1 : T 5 1 = 1 := by rw [← Tc_eq_T]; native_decide

/-- `T 5 2 = 68` (banked, `results/triangle.txt`). -/
theorem T_5_2 : T 5 2 = 68 := by rw [← Tc_eq_T]; native_decide

/-- `T 5 5 = 81 = 3^4`, the diagonal value `T(n,n) = 3^(n-1)` at `n = 5`. -/
theorem T_5_5 : T 5 5 = 81 := by rw [← Tc_eq_T]; native_decide

/-- `T 6 4 = 1480` (banked, `results/triangle.txt`), a `P_2` point —
previously only a prose note in `Compute.lean` ("verified out-of-file");
now a kernel-recorded fact (~1 min `native_decide`). -/
theorem T_6_4 : T 6 4 = 1480 := by rw [← Tc_eq_T]; native_decide

/-- `T 6 5 = 945` (banked, `results/triangle.txt`), a `P_1` point —
previously only a prose note in `Compute.lean`; now a kernel-recorded
fact (~3 min `native_decide`). -/
theorem T_6_5 : T 6 5 = 945 := by rw [← Tc_eq_T]; native_decide

end Polyplets
