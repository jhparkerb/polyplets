# Lean overhaul — working list

Branch `lean-overhaul`, started 2026-10-11. Target: `Polyplets/Report.lean`
states every claim of `paper/technical-report.tex` and proves it from
standard axioms only. `native_decide` is tolerated until the proofs are in
place, then burned down.

## Queue, easiest first

1. Delete or quarantine modules `Report.lean` does not import (his call per
   group). Known duplicate: `Grand/Lead.lean` (`shape_lead`, via
   `ExpForm`+`Series`+`Mu`, 1300 lines) proves the same leading coefficient
   as `LeadingCoeff.lean` (220 lines on top of `Shape`); keep one.
2. Pointers to the deleted `Grand/PinGrand.lean` and `scripts/gen_grand_pin.py`
   in `docs/lean-record.md`, `docs/publication.md`, `docs/proofs/T-n-nm1.md`,
   `scripts/run_strip_h14.sh`, `Pin.lean`, `Weights3Heavy.lean`, `README.md`,
   `PROOF-STATUS.md`: fix during the ledger fold (item 4).
3. Burn down `native_decide`: 39 values under `report_Pk_known`, 2 under
   `report_leading_coeff` (`V_1_1`, `d_0_1`). Try `decide`/`simp`/kernel
   reduction first; list by name what resists.
4. Fold `PROOF-STATUS.md`, `PLAN.md`, `DESIGN.md`, `GRANDFORM-PLAN.md`,
   `OUTWORKS-PLAN.md` into one short ledger in `Report.lean`'s order.
5. `make lean` gate on gympie: root build, no `sorry`, axiom sets of
   `Report.lean` theorems unchanged.
6. **Deferred until it is the easiest thing left**: one-sided → a(n)/4 and
   free → a(n)/8 (`Report.SymmetryRatioClaim`). Needs the symmetric counts
   shown o(a(n)).

## Done

- `Report.lean` drafted and in the root build (2026-10-11).
- `LeadingCoeff.lean`: leading coefficient 25^k/k!, and P_k fixed from rows
  2k+1 … 3k (2026-10-11).
- `Grand/PinAll.lean` replaces `Grand/PinGrand.lean` (2608 generated lines →
  ~330): one `mu_step`, one `grand_step`, a 15-level climb from
  `BankedAnchors` (2026-10-11).
