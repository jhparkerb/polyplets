# Post-teardown engineering plan — next-system a(21) and beyond

Status: 2026-06-27. dalby idled (old split a(21) abandoned; H1–16 salvaged as a
per-cell cross-check, see below). New engine will produce a(21) on dalby. These
docs design the work agreed in the consolidated plan before that launch.

## Why we stopped the old engine

Old engine on dalby was using ~6.5 of 80 cores (time-averaged lower), so "4 weeks
remaining" was a ~6-core number. The campaign was also further than it looked:
dalby H19 was deferred (RAM) to run *after* H20, so dalby alone was H20→H19
serialized, ~4–6 weeks total. The new engine's only job is to beat that — but the
8h prediction is an optimistic extrapolation, not a measured fact. We resolve that
by measurement (doc 03), not argument.

## What we salvaged (cross-validation budget)

`runs/a21fold/h1..h16.out` on ayr hold the **full per-cell T(n,H) column vectors**
for H≤16, every n≤21 (verified: Σ T(21,H) over H1–16 = a21.partial =
6,937,832,928,078,101). That is per-cell agreement on 16 of 21 rows, ~99.8% of
a(21)'s mass — far stronger than the n≤18 row-sum fixtures. ayr keeps running
H17/H18 (untouched) to extend the independent check to H18. Only H19/H20 frontier
cells will rest on the new engine alone.

## Features

| # | Doc | What | Effort | When |
|---|-----|------|--------|------|
| 2 | [01-unit-mult.md](01-unit-mult.md) | Decouple unit count from core count; fill idle cores | ~1–2h | before launch |
| 4 | [02-progress-eta.md](02-progress-eta.md) | A-priori predictor + live calibrated ETA + within-column heartbeat | ~1 day | **all of it before launch** |
| 3 | [03-probe-calibration.md](03-probe-calibration.md) | Measure util/scaling on a(19)/a(20); decide work-stealing; validate predictor | ~1–3h wall | after 2 & 4 |
| 5 | [04-multi-machine-height-split.md](04-multi-machine-height-split.md) | Per-height split across machines + combine | ~half day | Phase B (during a(21) run) |
| 32 | [07-height-scheduling.md](07-height-scheduling.md) | Cross-machine height-assignment scheme (Q2‖Cmax): LPT/dynamic-pull beat meet-in-the-middle; calculator + sims | paper (no compute) | a(22)/M4 |
| T2.3 | [08-straggler-tail-sizing.md](08-straggler-tail-sizing.md) | Map straggler tail sized (~18% of map-wall, growing); work-stealing beats predictive LPT 92% vs 71%, predictor-free; per-unit trace tools + sched_sim | measured (gympie probes) | a(22)/M4 |

## Sequencing and gates

1. **unit-mult** (doc 01) — small, low-risk, lands first. Re-run ns-gate-parallel
   at mult∈{1,4,8} to prove result invariance.
2. **progress + ETA, all of it** (doc 02) — per-column telemetry, calibrated ETA,
   within-column heartbeat, and the a-priori predictor. This blocks the dalby launch
   (jasonp's call): we do not start the a(21) job without working progress and ETA.
3. **probe** (doc 03) — a(19) K-sweep then a(20) at best K. **Launch gate for
   a(21):** a(19) AND a(20) `--compare` PASS, *and* predictor error on a(20) within
   tolerance. Records the earned a-priori a(21) ETA. Also decides whether
   work-stealing is needed (separate design only if the probe shows tail-idle that
   high unit-mult cannot fix).
4. **a(21)** on dalby (single box; ayr busy with the cross-check, and a(21) fits
   dalby alone).
5. **multi-machine** (doc 04) — built while a(21) runs; it is the lever for
   a(22)/a(23), not for a(21).

## Decisions

- **Progress and ETA block the dalby launch** — decided (jasonp, 2026-06-27). The
  whole progress/ETA feature — per-column telemetry, calibrated ETA, within-column
  heartbeat, and the a-priori predictor — must be working before the a(21) job
  starts. Not a fast-follow.
- **Multi-machine timing** — open. Recommended Phase B (built while a(21) runs),
  since a(21) fits dalby alone and ayr is busy with the cross-check. Needs jasonp's
  confirmation.

## Pre-probe chore

`fixtures/b006770.txt` stops at n=18; add a(19) and a(20) (1,025,573,519,362,016)
so `--compare` validates the probe runs. (a(20) and a(21) fit u64; u64 counter
holds through a(25).)
