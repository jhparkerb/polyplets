/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Pin

/-!
# The three heavy surplus-3 leaves, and the unconditional `k = 3` diagonal

`Pin.P3_pinned_of_heavy` reduces the `k = 3` diagonal law to three
`native_decide` facts whose enumerations are too large for the default build's
per-check compile budget:

* `V 3 3 = 4778` — `C(45,6)·15 ≈ 1.2·10⁸` cluster/`q` pairs;
* `Vᵗ 3 3 = 919` — `C(39,6) ≈ 3.3·10⁶` subsets;
* `d 3 4 = 4687` — `C(28,7) ≈ 1.2·10⁶` subsets.

This module is **deliberately excluded from `Polyplets.lean`'s default target**
so those hour-scale `native_decide` compilations do not gate ordinary builds.
Build it explicitly (`lake build Polyplets.Weights3Heavy`) to obtain the
unconditional `P3_pinned`.

All three values are independently cross-checked out of Lean (2026-07-20) and
consistent with the banked `results/triangle.txt` onset values that
`P3_pinned_of_heavy` reproduces from them (`T(7,4)=7898`, `T(8,5)=47066`,
`T(9,6)=241864`, `T(10,7)=1134865`).
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

/-- `V 3 3 = 4778` (heavy `native_decide`; cross-checked enumeration). -/
theorem V_3_3 : V 3 3 = 4778 := by native_decide

/-- `Vᵗ 3 3 = 919` (heavy `native_decide`; cross-checked enumeration). -/
theorem Vt_3_3 : Vt 3 3 = 919 := by native_decide

/-- `d 3 4 = 4687` (heavy `native_decide`; cross-checked enumeration). -/
theorem d_3_4 : d 3 4 = 4687 := by native_decide

/-- **k=3 diagonal, unconditional**: `T(n, n-3) = P_3(n)·3^(n-10)` for `n ≥ 7`,
with `P_3 = (15625n³ - 100050n² + 122213n - 32940)/6`. Discharges the three
heavy-leaf hypotheses of `Pin.P3_pinned_of_heavy`. -/
theorem P3_pinned : ∀ n : ℕ, 2 * 3 + 1 ≤ n →
    (T n (n - 3) : ℚ) = Pp3.eval (n : ℚ) * (3 : ℚ) ^ ((n : ℤ) - 1 - 3 * 3) :=
  P3_pinned_of_heavy V_3_3 Vt_3_3 d_3_4

end Polyplets
