/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Weights

/-!
# Surplus-3 cluster leaves (`native_decide`)

The `j = 3` interior/top cluster weights `V ℓ j`, `Vᵗ ℓ j` and the base
walk-top count `d 3 4`, the leaves the surplus-3 (`k = 3`) peeling recursion
needs beyond the `j ≤ 2` weights of `Weights.lean`. Each is a one-off
`native_decide` on the computable enumeration of `Weights.lean`; the results
are cached in the `.olean`, so the cost is paid once.

Values (independently cross-checked out of Lean, 2026-07-20):
`V 1 3 = 81`, `Vᵗ 1 3 = 9`, `V 2 3 = 1860`, `Vᵗ 2 3 = 307`,
`V 3 3 = 4778`, `Vᵗ 3 3 = 919`, `d 3 4 = 4687`.

The three heavy leaves — `V 3 3`, `Vᵗ 3 3`, `d 3 4` — enumerate `C(45,6)·15`,
`C(39,6)`, and `C(28,7)` subsets respectively; whether they land within the
per-check compile budget is measured below (see the timing note).
-/

namespace Polyplets

set_option linter.style.nativeDecide false

/-! ## Light surplus-3 leaves (`ℓ ≤ 2`) -/

/-- `V 1 3 = 81` (cross-checked enumeration). -/
theorem V_1_3 : V 1 3 = 81 := by native_decide

/-- `Vᵗ 1 3 = 9` (cross-checked enumeration). -/
theorem Vt_1_3 : Vt 1 3 = 9 := by native_decide

/-- `Vᵗ 2 3 = 307` (cross-checked enumeration). -/
theorem Vt_2_3 : Vt 2 3 = 307 := by native_decide

/-- `V 2 3 = 1860` (cross-checked enumeration). -/
theorem V_2_3 : V 2 3 = 1860 := by native_decide

end Polyplets
