/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.WeightsChunk

/-!
# `V 3 3` chunk value: column -6

`native_decide` leaf for -6 of the `V 3 3` partition
(`WeightsChunk.V_3_3_eq_sum_chunks`).
Enumerates ≈ 2.02M pairs (8-column window).
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

/-- `(CFGVchunk -6).card = 43` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_n6 : (CFGVchunk (-6 : ℤ)).card = 43 := by
  native_decide


end Polyplets
