# R1-A plan — base anatomy audit

2026-08-13. Scout. Question, one sentence: what is the incumbent engine's
per-n cost base, measured — and what numeric measured-clause threshold does
that fix for the bar?

## Steps, in order

1. Read `results/rook1/R1-K.md` §1d (the pinned readings of the three
   contradictory base claims) — start from it, do not redo it.
   Produces: the three claims as R1-K pinned them.
2. Read the three sources themselves on this branch:
   `results/kink-carry.md:46,69`, `results/ns_a40/PROVENANCE.md` (esp. lines
   16–25). Produces: verified quotes with line anchors.
3. Locate existing per-term run data for n = 24..30: banked records and run
   logs already in-tree (grep `results/`, `logs/` if present, `experiments/`
   for cpu-seconds-per-term tables; ns_a40 provenance; any a(24)..a(30)
   run records). Produces: a table n, cost(n), source path, quantity
   (cpu-s / wall-s / states) for each row.
4. Fit log(cost ratio): least-squares slope of ln cost(n) vs n over the
   window; report b = e^slope, residuals per point. Script under
   `experiments/rook1/rook1_R1-A_basefit.py` with log beside it, same stem.
   Seconds-scale, foreground, gympie. Produces: b MEASURED with window and
   residuals.
5. Reconcile 2.42 / 1.61 / 1.73: say which is the per-n cost base, which is
   a bound/measurement of a different quantity, which is wrong. Queue row K1.
6. Propose the numeric measured-clause threshold (clause 1 of
   docs/rook-parity-bar.md): the fitted curve and the number a challenger
   must come in strictly below on n = 24..30.
7. State whether K3 fired (b ~ 1.73 ⇒ incumbent already at parity).
8. File ≥2 successor queue rows, different in kind. Run
   ./scripts/check_receipts.sh. Stop; report b, threshold, K3 to lead.

## What would make me stop

- No in-tree per-term cost data on n = 24..30 at the cpu-seconds level:
  then the fit is impossible desk-only; I file the job request row and
  deliver the reconciliation (steps 1–2, 5) with the fit marked
  NOT ESTABLISHED.
- Any step that needs compute beyond seconds-scale foreground: queue row +
  field block, per docs/r3-job-dispatch.md.
