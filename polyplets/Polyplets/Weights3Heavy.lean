/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Pin
import Polyplets.WeightsChunkA
import Polyplets.WeightsChunkB
import Polyplets.WeightsChunkC
import Polyplets.WeightsChunkD
import Polyplets.WeightsChunkE
import Polyplets.WeightsChunkF
import Polyplets.WeightsChunkG
import Polyplets.WeightsChunkH
import Polyplets.WeightsChunkTail

/-!
# The three heavy surplus-3 leaves, and the unconditional `k = 3` diagonal

`Pin.P3_pinned_of_heavy` reduces the `k = 3` diagonal law to three
`native_decide` facts whose enumerations are too large for the default build's
per-check compile budget:

* `V 3 3 = 4778` — `C(45,6)·15 ≈ 1.2·10⁸` cluster/`q` pairs;
* `Vᵗ 3 3 = 919` — `C(39,6) ≈ 3.3·10⁶` subsets;
* `d 3 4 = 4687` — `C(28,7) ≈ 1.2·10⁶` subsets.

The `V 3 3` enumeration overflows the compiler's evaluation stack in one shot, so
it is **chunked**: `WeightsChunk.lean` partitions `CFGV 3 3` by leftmost cluster
column into fifteen sets each enumerating `≤ 2.0·10⁶` pairs (proved
`native_decide`-free that `V 3 3 = ∑_{m=-7}^{7} (CFGVchunk m).card`), and
`WeightsChunkA..H`/`WeightsChunkTail` carry the fifteen per-chunk `native_decide`
cardinalities (one heavy column m=-7..0 per file, the light m=1..7 folded into
`WeightsChunkTail`; nine modules, for parallel `lake` builds ≤ 9-wide). The
assembly below is pure arithmetic. `Vᵗ 3 3` (`3.3·10⁶`) and `d 3 4` (`1.2·10⁶`)
stay single `native_decide`s — both build below the overflow threshold.

This module is **deliberately excluded from `Polyplets.lean`'s default target**
so those hour-scale `native_decide` compilations do not gate ordinary builds.
Build it explicitly (`lake build Polyplets.Weights3Heavy`) to obtain the
unconditional `P3_pinned`.

All three values are independently cross-checked out of Lean (2026-07-20);
the fifteen chunk cardinalities are cross-checked by `scripts/gen_v33_chunks.py
--check` (leftmost-column histogram of the 4778 configs, sum 4778). They are
consistent with the banked `results/triangle.txt` onset values that
`P3_pinned_of_heavy` reproduces from them (`T(7,4)=7898`, `T(8,5)=47066`,
`T(9,6)=241864`, `T(10,7)=1134865`).
-/

namespace Polyplets

set_option linter.style.nativeDecide false
set_option maxRecDepth 4000

/-- The per-column chunk cardinalities as a cheap (`native_decide`-free) value
function. Evaluating `(CFGVchunk m).card` in the kernel would re-run the heavy
enumeration, so the assembly of `V 3 3` never reduces those cards directly —
`chunkVal` carries the values, and `chunkVal_eq` swaps them in pointwise. -/
def chunkVal : ℤ → ℕ := fun m =>
  if m = -7 then 4 else if m = -6 then 43 else if m = -5 then 203
  else if m = -4 then 504 else if m = -3 then 835 else if m = -2 then 1033
  else if m = -1 then 1032 else if m = 0 then 682 else if m = 1 then 442 else 0

/-- On `[-7, 7]` the chunk cardinality equals its banked value — proved column by
column from the `native_decide` chunk lemmas (the cards are *rewritten*, never
evaluated). -/
theorem chunkVal_eq :
    ∀ m ∈ Finset.Icc (-7 : ℤ) 7, (CFGVchunk m).card = chunkVal m := by
  intro m hm
  rw [Finset.mem_Icc] at hm
  obtain ⟨h1, h2⟩ := hm
  interval_cases m <;>
    simp only [CFGVchunk_card_n7, CFGVchunk_card_n6, CFGVchunk_card_n5,
      CFGVchunk_card_n4, CFGVchunk_card_n3, CFGVchunk_card_n2, CFGVchunk_card_n1,
      CFGVchunk_card_p0, CFGVchunk_card_p1, CFGVchunk_card_p2, CFGVchunk_card_p3,
      CFGVchunk_card_p4, CFGVchunk_card_p5, CFGVchunk_card_p6, CFGVchunk_card_p7] <;>
    decide

/-- `V 3 3 = 4778`, assembled from the fifteen per-column chunk cardinalities
(`WeightsChunk.V_3_3_eq_sum_chunks`) — the heavy `native_decide`s live in the
chunk files; here the cards are swapped for `chunkVal` (`chunkVal_eq`) and the
remaining sum of small numerals is closed by `decide`. -/
theorem V_3_3 : V 3 3 = 4778 := by
  rw [V_3_3_eq_sum_chunks, Finset.sum_congr rfl chunkVal_eq,
    show (Finset.Icc (-7 : ℤ) 7)
        = {-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7} from by
      ext x
      simp only [Finset.mem_Icc, Finset.mem_insert, Finset.mem_singleton]
      omega]
  decide

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
