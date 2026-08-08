/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Upper.BuiData3

/-!
# The conditional Bui upper bound at RD = 3: `lambda ≤ 20000/2147 ≈ 9.31532`

The headline instance — the project's banked polyplet upper bound
(`docs/proofs/polyplet-upper-bound.md`: `λ ≤ 9.3154, PROVED`), here with its
certificate side machine-checked and its combinatorial side an explicit named
hypothesis. Same split as `Upper/BuiRD2.lean`, at the 5930-type RD = 3 system
with rate `x = 107350/10⁶ = 2147/20000`.

Note the evidence grade difference against RD = 2: the RD ≤ 2 recurrences
were brute-force verified (`n ≤ 9`); the RD = 3 system is valid *by
construction* (a larger split window only adds genuinely-empty cells to the
split type, tightening a valid over-count — see the doc), but was not
separately brute-forced. The hypothesis doc-comment records this.
-/

namespace Polyplets

/-- **The RD=3 king Bui system hypothesis**
(`docs/proofs/polyplet-upper-bound.md`, BREAKTHROUGH section;
`experiments/king_bui.py` at RD = 3).

Same shape as `KingBuiSystemRD2Holds` — intended witnesses are the
marked-corner counting functions `φ i n = #(P, c)` over the 5930-type RD = 3
closure, type `0` the G8 corner type, base bounds by isolation, casing
recurrences by the exact-partition / valid-split-over-count argument, anchor
by the lowest-leftmost corner cell.

Evidence grade: the RD = 3 system was **not** separately brute-forced
(`king_bui.py` skips verification above 250 types); it is valid by
construction — enlarging the split window from RD = 2 (whose 185 recurrences
were verified as over-counts for all `n ≤ 9`) only adds known-empty cells to
the split-off type, which tightens the convolution factor while keeping it an
over-count. That construction argument lives in the doc, not in Lean; this
`Prop` assumes its conclusion. -/
def KingBuiSystemRD3Holds : Prop := buiRD3.SystemHolds

/-- **Conditional headline upper bound on the polyplet growth constant**:
`lambda ≤ 20000/2147 = 9.31532…`, given the RD=3 system hypothesis — the
Lean rendering of the project's banked `λ ≤ 9.3154`. The certificate
arithmetic over all 5930 rows is kernel-checked (`buiRD3_valid`). -/
theorem lambda_le_of_bui_rd3 (h : KingBuiSystemRD3Holds) :
    lambda ≤ (20000 : ℝ) / 2147 := by
  have hmain := RatCert.lambda_le buiRD3 buiRD3_valid h
  have hCD : buiRD3.CD = 1000000 := rfl
  have hX : buiRD3.X = 107350 := rfl
  rw [hCD, hX] at hmain
  have hq : ((1000000 : ℕ) : ℝ) / ((107350 : ℕ) : ℝ) = (20000 : ℝ) / 2147 := by
    norm_num
  rwa [hq] at hmain

/-! ## Axiom audit

Plain `#print axioms`; the `#guard_msgs`-wrapped versions live in
`AuditOutworks.lean`. -/

#print axioms buiRD3_valid
#print axioms lambda_le_of_bui_rd3

end Polyplets
