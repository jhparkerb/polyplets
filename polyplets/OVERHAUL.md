# Lean overhaul — working list

Branch `lean-overhaul`, started 2026-10-11. Target: `Polyplets/Report.lean`
states every claim of `paper/technical-report.tex` and proves it from
standard axioms only. Ledger: `README.md`.

## Queue

1. **Deferred until it is the easiest thing left, and now the only thing
   left**: one-sided → a(n)/4 and free → a(n)/8
   (`Report.SymmetryRatioClaim`). Needs the symmetric counts o(a(n)): an
   injection of each symmetric polyplet into something of about half the
   size, then `a_supermul` to show a(n/2)/a(n) → 0. The injection is the
   work (half of a symmetric animal need not be connected); not started.

## Done

- `Report.lean` drafted and in the root build (2026-10-11).
- `LeadingCoeff.lean`: leading coefficient 25^k/k!, and P_k fixed from rows
  2k+1 … 3k (2026-10-11).
- `Grand/PinAll.lean` replaces `Grand/PinGrand.lean` (2608 generated lines →
  ~330): one `mu_step`, one `grand_step`, a 15-level climb from
  `BankedAnchors` (2026-10-11).
- Option A (2026-10-12): levels 1–3 take their two onset cells as hypotheses
  like levels 4–18, so `BankedAnchors` is 36 cells and `Weights3Heavy` leaves
  the Report cone. Every `Report.lean` theorem is on
  `[propext, Classical.choice, Quot.sound]` alone.
- Delete outside the Report cone (2026-10-12): 60 modules, 24k lines, the
  V(3,3) hour of every cold build, `Draft/`, the build receipts and logs,
  the generators `gen_v33_chunks.py`, `gen_bui_cert.lean.py`, `gen_pin.py`,
  the `gate-notary` Makefile target; `Pin.lean` cut to the polynomials, the
  pin lemma and `P1_closed`. `README.md`'s "Removed" table says what each
  group proved; all of it is at commit `697f376`.
- `native_decide` burned down to zero (2026-10-12). Measured with
  `scripts/lean-decide-trials.sh` under `scripts/lean-guard.sh`: 14 cells
  close in the kernel under 3.5 GB and are now `decide +kernel`; the rest
  need 6–9+ GB and were deleted with their consumers (`P2_closed`, `mu_two`,
  `mu_three_of`, `lambda_gt`, the symmetry anchors, the Weights gates).
- Ledger fold (2026-10-12): `PROOF-STATUS.md`, `DESIGN.md`, the old
  `README.md` and `docs/lean-record.md` are one file, `README.md`; pointers
  across `docs/`, `results/` and `scripts/` fixed to it or to `697f376`.
  Historical audits and reviews under `docs/audits/`, `docs/reviews/`,
  `docs/pre-landing.md` and the `experiments/` scripts keep their old module
  names as records.
- `make lean` (2026-10-12): `sorry` and `native_decide` greps, then the root
  build; axiom footprints are the `#guard_msgs` in `Polyplets/Audit.lean`,
  one per Report theorem plus the internal results they rest on.
