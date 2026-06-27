# 02 — progress, ETA, and a-priori prediction

## Problem

The engine is a black box during a run. The only signals are:

- `event=done cpu_s=.. wall_s=.. peak_rss_mb=.. records=.. spill_bytes=..` emitted
  by each worker **at process exit** (map_worker.cpp:120, merge_worker.cpp:69).
- one `H=.. col=.. frontier_records=.. acct=..` line **after** each column
  (sweep.go:209).

There is no `done` fraction, no `eta`, no within-column progress, and no pre-launch
prediction. Worse, `runWorker` discards worker stderr (`cmd.Stderr = nil`,
worker.go:111) and only parses stdout after the worker exits (worker.go:117–127), so
a long-running column emits nothing until it finishes. `Acct.WallS` (accounting.go:13)
**sums** per-worker wall, so it is not wall-clock — column wall-clock is not recorded
anywhere today.

Goal (jasonp): an a-priori estimate of job duration, and honest live "what's done /
what remains." Per the no-fabricated-ETAs rule, every estimate states its basis and a
band, never a bare point.

## Three layers (independent, shippable in order)

### A. Per-column wall + frontier telemetry  (orchestrator only, ~1h)

Time each column in `sweepHeight` (wrap mapPhase+mergePhase, sweep.go:171–190 with
`time.Now()`), and replace the line-209 print with a structured event:

```
event=column H=<h> col=<c> wall_s=<this column> cum_wall_s=<run> \
  frontier_in=<records read> frontier_out=<totalRecs> \
  peak_rss_mb=<col max> spill_bytes=<col sum>
```

`frontier_in` is the size of the frontier entering the column (len/records of the
input runs — already sampled by `SampleKeysMulti`); `frontier_out` is `totalRecs`
(sweep.go:192). This alone gives a live, honest per-column cost trace with zero
worker changes, and is the data the ETA model consumes.

### B. Live calibrated ETA  (orchestrator only, ~half day)

Cost model: per-column map work ≈ proportional to `frontier_in` (records expanded),
with a slowly-drifting cost-per-record. We never know *future* frontier sizes a
priori within a height, so blend two sources:

1. **Shape prior** from the calibration run (doc 03): record the full per-(H,col)
   `frontier_in`/`wall_s` profile for a(19)/a(20); scale it to a(21) by the measured
   per-term work ratio. This gives an initial total and per-column breakdown.
2. **Online correction**: as real columns complete, track the ratio
   actual_wall / predicted_wall and reweight the remaining estimate. The ETA tightens
   monotonically as the run proceeds.

Emit after each column:

```
event=eta done_frac=<cost-weighted, not column-count> \
  eta_wall_s=<remaining> eta_at=<absolute ts> basis=<calib-run|online> band=<±%>
```

`done_frac` is cost-weighted (Σ cost of completed cols / Σ cost of all cols), never
naive columns-done/total — the back columns dominate.

### C. Within-column heartbeat  (worker + core + orchestrator, ~half day)

So a single long column is not opaque:

- **Core**: `map_shard_file` (core/libenum.h, called at map_worker.cpp:105/110) emits
  `event=progress done_recs=<processed> total_recs=<input>` to stdout every ~30s.
  Input record count is known up front (the run header); processed count is the loop
  counter. The natural emit site is the existing per-spill / SIGTERM-check point
  (map_worker.cpp:25–26 references that loop).
- **Orchestrator**: `runWorker` (worker.go:105) already line-scans stdout; forward
  `event=progress` lines via a callback to a per-column aggregator instead of only
  buffering. Keep progress on **stdout** (stderr stays discarded). Aggregate across
  the ≤cores running units → live column %done and an instantaneous rate.

## A-priori predictor (pre-launch, standalone, ~2h)

A small Go tool / function:

```
predict(box, cores, target_n, calib{n, wall_s, peak_rss_mb, spill_bytes})
  → wall_band, rss, disk
```

- `wall(target) = calib.wall * R^(target-calib.n) / coreScale(box, cores)` where R is
  the measured per-term **work** ratio (records grow ~4.4×/term for this engine;
  measure it from a(19)→a(20), do not assume).
- `rss(target) = calib.rss * R^(target-calib.n)` (state count scales with R).
- `disk(target) = calib.spill_bytes * R^(target-calib.n)`.

Output a band, the calibration basis, and the binding uncertainty (core-scaling and
N1/M1-per-core). The probe validates it by predicting a(20) from a(19) and checking
the error before we trust the a(21) number.

## Data already available vs to add

Available: `frontier_records` (sweep.go:209), per-worker `records`/`spill_bytes`/
`peak_rss_mb`/`cpu_s`/`wall_s` (accounting.go:74–85). To add: per-column wall-clock
timing (A), the input-record denominator passed to the heartbeat (C), and the
predictor (standalone).

## What blocks the launch

All three layers + the predictor must be working **before** the a(21) job starts on
dalby — jasonp's call: progress and ETA block the launch. The within-column heartbeat
is the difference between a multi-hour a(21) column being opaque or legible, so it
ships too, not as a fast-follow.

## Effort

A ~1h, B ~half day, C ~half day, predictor ~2h.
