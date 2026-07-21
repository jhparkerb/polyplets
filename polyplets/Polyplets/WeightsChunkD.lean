/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.WeightsChunk

/-!
# `V 3 3` chunk value: column -4

`native_decide` leaf for -4 of the `V 3 3` partition
(`WeightsChunk.V_3_3_eq_sum_chunks`).
Enumerates ≈ 2.02M pairs (8-column window).
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

/-- `(CFGVchunk -4).card = 504` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_n4 : (CFGVchunk (-4 : ℤ)).card = 504 := by
  native_decide


end Polyplets
