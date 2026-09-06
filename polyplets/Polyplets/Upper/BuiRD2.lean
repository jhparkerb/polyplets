/-
Copyright (c) 2026 Jason H Parker. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Jason H Parker
-/
import Polyplets.Upper.BuiData2

/-!
# The conditional Bui upper bound at RD = 2: `lambda ≤ 10⁶/106251 ≈ 9.4117`

The certificate side — that the exported 185-row system's rational
super-solution really satisfies `F_x(u) ≤ u` at `x = 106251/10⁶`, with rank
descent and index bounds — is *proved* (`buiRD2_valid`, a kernel `decide`),
and the monotone-iteration argument turning a super-solution into a growth
bound is *proved* (`Upper/Certificate.lean`, standard axioms). What remains a
hypothesis is the combinatorial claim that the king counting functions
actually satisfy the 185 system inequalities: `KingBuiSystemRD2Holds`.

This split mirrors `HolesUpper.lean`'s `MoatBound`: one named proposition
carrying exactly the unformalized step, consumed by a conditional theorem.
-/

namespace Polyplets

/-- **The RD=2 king Bui system hypothesis** (`docs/proofs/polyplet-upper-bound.md`,
BREAKTHROUGH section; `experiments/king_bui.py`).

The intended witnesses are the marked-corner counting functions
`φ i n = #(P, c)` — `P` an `n`-cell king animal (fixed polyplet), `c` a cell
of `P` whose neighborhood avoids type `i`'s forbidden set (the type table is
in `Upper/BuiData2.lean`) — with type `0` the G8 corner type (W, SW, S, SE
forbidden). For them:

* the **base bounds** hold because a marked cell with all eight king
  neighbors forbidden is an isolated animal (`n = 1` only, one such pair);
* the **casing recurrences** hold because casing on the free cell `d`
  partitions into `d`-empty (exactly type `T' = T + {d}`, an equality) and
  `d`-occupied, which the split into the `d`-piece (type `D`) convolved with
  the `c`-side over-counts (every animal splits, the recombination is not
  injective — an inequality in the right direction);
* the **anchor** `a n ≤ φ 0 n` holds because every nonempty animal's
  lowest-leftmost cell has W, SW, S, SE empty.

None of this is formalized here — that is exactly what this `Prop` assumes.
Evidence: every recurrence of this 185-type system was verified as a valid
over-count against brute-force enumeration for all `n ≤ 9`
(`experiments/king_bui.py`, RD ≤ 2 check `all recurrences valid over-counts:
True`), and the doc gives the by-construction argument for all `n`. -/
def KingBuiSystemRD2Holds : Prop := buiRD2.SystemHolds

/-- **Conditional upper bound on the polyplet growth constant**:
`lambda ≤ 10⁶/106251 = 9.41167…`, given the RD=2 system hypothesis. The
certificate arithmetic is kernel-checked (`buiRD2_valid`); the monotone
iteration and the `lambda_tendsto` transfer are proved in
`Upper/Certificate.lean`. Compare the unconditional `lambda_le`
(`λ ≤ 3125/256 ≈ 12.207`): the Bui route sharpens it by 2.8 at the price of
the named hypothesis. -/
theorem lambda_le_of_bui_rd2 (h : KingBuiSystemRD2Holds) :
    lambda ≤ (1000000 : ℝ) / 106251 := by
  have hmain := RatCert.lambda_le buiRD2 buiRD2_valid h
  have hCD : buiRD2.CD = 1000000 := rfl
  have hX : buiRD2.X = 106251 := rfl
  rw [hCD, hX] at hmain
  exact_mod_cast hmain

/-! ## Axiom audit

Plain `#print axioms`; the `#guard_msgs`-wrapped versions live in
`AuditOutworks.lean`. `buiRD2_valid` is a kernel `decide` — no axioms at all —
so the conditional theorem carries only the standard three. -/

#print axioms buiRD2_valid
#print axioms lambda_le_of_bui_rd2

end Polyplets
