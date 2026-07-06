# Design 14 Phase 0.1c: Option A per-barrier fixed overhead — bounded from production telemetry

**2026-07-02.** Follow-up to `results/kink-carry-optionA-volume.md`, which
left one open question: real per-barrier orchestration overhead (dispatch,
worker fork/exec, sync, wait) × H, unmeasurable from a serial probe. This
closes that gap using **existing production telemetry** instead of building
the wired Option A engine — the "third option" (analytic/measured bound
instead of shard-and-guess).

## Method

`orchestrator/telemetry.go` already logs `wall_s` (map+merge+barrier,
combined) per (H, col) for every real run. At the tail of any height, frontier
size collapses toward zero while the column still pays every fixed cost a
barrier has: worker dispatch, fork/exec, sync/wait, merge round-trip. Those
tail columns are a **real, in-production measurement of the fixed floor**,
uncontaminated by volume.

## Result

`results/ns_a27/cost_profile_dalby.tsv` (H16, dalby, 80 cores):

| col | frontier_in | wall_s |
|---|---|---|
| 25 | 67  | 0.030 |
| 26 | 24  | 0.014 |
| 27 | 8   | 0.006 |

`results/ns_a26/cost_profile.tsv` (H15, dalby, 80 cores):

| col | frontier_in | wall_s |
|---|---|---|
| 23 | 159 | 0.066 |
| 24 | 64  | 0.031 |
| 25 | 23  | 0.014 |
| 26 | 8   | 0.006 |

Consistent across two independent runs and two heights: full column
round-trip (map dispatch + fork/exec + merge barrier) floors at
**~6-30 ms** even at near-zero frontier. No fixed plateau above that —
wall keeps dropping with frontier, meaning fixed overhead is already a small
fraction of even these tiny columns.

## Bound on Option A's added cost

Option A pays this fixed floor **H times per column** instead of once.
At H16 (the dominant height): `16 × ~0.01-0.03s ≈ 0.2-0.5s` of added fixed
tax per column. Compare against:
- The volume savings already measured (`kink-carry-optionA-volume.md`):
  ratio shrinks to ~0.003-0.009× by H14-16, i.e. a 100-300× reduction in
  data moved through the barrier(s) combined.
- Any column with non-trivial frontier: even the *smallest* real measured
  columns above (frontier ~8-70) still take 6-30ms **total**, so 16 such
  barriers costs well under a second — negligible next to peak-column wall
  times that run to hours (H_max's peak column ~9h at a(21) scale, per
  `designs/09-cost-model-and-work-assignment.md`).

## Verdict

The previously-open question is closed: real per-barrier fixed overhead is
on the order of **tens of milliseconds**, not seconds — H barriers/column
adds well under a second of fixed tax against savings measured in
100-300× volume reduction. Nothing in production telemetry suggests H small
barriers will serialize worse than one big one; if anything, smaller
per-barrier volume should shorten the merge's I/O-bound tail
(`results/scheduling.md`: merge is light/I-O bound, saturates on a few
workers regardless of size).

This does not replace the Phase 2 wired-engine gate (real per-stage
dispatch under the *new* code path, not inferred from the old one) — but it
removes the last reason to hesitate before starting Phase 1. No hybrid or
hand-derived mixing-rate model was needed; the answer was already sitting in
banked telemetry from a26/a27.
