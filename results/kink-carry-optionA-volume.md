# Design 14 Phase 0.1 (Option A): merge-barrier volume — GO

**2026-07-02.** `experiments/kink_tm/kink_tm.cpp`. Follow-up to
`results/kink-carry-shard-duplication.md` (Option B: NO-GO). This measures
Option A instead: H merge barriers per column (one after each stage), zero
duplication by construction (every stage is a single canonicalized table,
never sharded-and-privately-run).

## Method

No new code needed — `kinkSweep`'s existing `stageStateSum` counter (sum of
`stage.size()` over all H stages, over the whole run) is *exactly* the total
record volume that would flow through Option A's H barriers per column,
summed over the whole run. It was computed all along but never printed.
Exposed it and compared against `columnSweep`'s `kept-records` (today's
single-barrier volume, `Σ masks` per column, summed over the run).

## Result

| H | maxn | whole-column barrier volume (today, 1/column) | Option A volume (H barriers/column, summed) | ratio |
|---|---|---|---|---|
| 8  | 15 | 812,669     | 166,407     | 0.205× |
| 10 | 18 | 19,848,039  | 1,646,580   | 0.083× |
| 12 | 22 | 626,679,092 | 17,096,571  | 0.027× |
| 14 | 26 | ~19.4B (extrapolated from the H8/10/12 growth trend, whole-column not run — too slow) | 170,227,633 | ~0.009× |

Option A's total merge volume — even summed across all H barriers — is
already smaller than today's single barrier, and the ratio **shrinks with H**
(masks/state explodes; stage size stays flat ~3.6× the frontier, as already
established in `results/kink-carry.md`). At H16-18, the heights that dominate
every recent record run, extrapolation puts the ratio well under 0.01×.

## Verdict: GO

Reverses the naive "H barriers must cost more than 1 barrier" intuition:
because per-barrier volume is frontier-sized (~3.6×) rather than
masks-sized, H small barriers move *less total data* than one big one, by a
growing margin as H increases. This clears the volume side of Option A
cleanly — better than the design doc's Option B ever measured.

What's NOT yet measured (real overhead, not volume):
- Fixed per-barrier orchestration cost (dispatch/sync/wait) × H, on the real
  distributed engine — not visible to a serial probe. Production's existing
  per-column barrier overhead (known from telemetry) × H is the number to
  check this against; if per-barrier fixed cost is small relative to the
  ~10-100× volume savings shown here, Option A wins outright.
- Checkpoint/resume granularity: Option A's natural checkpoint boundary is a
  stage, not a column — finer-grained than today, should only help.
- Whether H small barriers serialize the pipeline (worker idle time waiting
  on merge) worse than 1 big barrier does today — a scheduling question, not
  a volume question.

## Decision

Option A is the path forward for Design 14. Proceed to scoping it into
Phase 1 (library port) with the barrier as a stage boundary rather than a
column boundary; the remaining open question (real per-barrier overhead) is
a Phase 2/3-scale measurement once the engine is wired, not a blocker to
starting the port.
