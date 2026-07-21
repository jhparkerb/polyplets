/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.WeightsChunk

/-!
# `V 3 3` chunk values: columns 1, 2, 3, 4, 5, 6, 7

`native_decide` leaf for columns 1, 2, 3, 4, 5, 6, 7 of the `V 3 3` partition
(`WeightsChunk.V_3_3_eq_sum_chunks`).
Column 1 enumerates ≈ 0.81M pairs; columns 2..7 are empty
(no config's cluster starts that far right) over shrinking
windows. All light — folded into one file.
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

/-- `(CFGVchunk 1).card = 442` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p1 : (CFGVchunk (1 : ℤ)).card = 442 := by
  native_decide

/-- `(CFGVchunk 2).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p2 : (CFGVchunk (2 : ℤ)).card = 0 := by
  native_decide

/-- `(CFGVchunk 3).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p3 : (CFGVchunk (3 : ℤ)).card = 0 := by
  native_decide

/-- `(CFGVchunk 4).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p4 : (CFGVchunk (4 : ℤ)).card = 0 := by
  native_decide

/-- `(CFGVchunk 5).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p5 : (CFGVchunk (5 : ℤ)).card = 0 := by
  native_decide

/-- `(CFGVchunk 6).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p6 : (CFGVchunk (6 : ℤ)).card = 0 := by
  native_decide

/-- `(CFGVchunk 7).card = 0` (heavy `native_decide`; cross-checked enumeration). -/
theorem CFGVchunk_card_p7 : (CFGVchunk (7 : ℤ)).card = 0 := by
  native_decide


end Polyplets
