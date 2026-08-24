# Depth 6 costs about 36 hours and 74 GB — the assertion survives, and its method does not

2026-08-23, executing `docs/time-at-the-bar-report.md` B2's own recommendation:
"one rung of a `J = 6` ladder would settle it the way five rungs settled depth
5". Four rungs, measured on dalby at fixed 8 threads,
`scripts/lastditch/emax5_kladder.sh`, analysis
`experiments/depth6_cost_ladder.py`.

## The answer

**`families 21 5` projects to ~36.3 h and ~74.2 GB at 8 threads.** The asserted
band was 20–60 h and 50–100 GB. **The assertion holds**, which is the opposite
of what happened to depth 5 — there the same style of assertion was out by an
order of magnitude (`results/depth5-cost-settled.md`).

| source | wall | RSS |
|---|---|---|
| asserted, B2 low | 20 h | 50 GB |
| asserted, B2 high | 60 h | 100 GB |
| **measured ladder, decelerating** | **36.3 h** | **74.2 GB** |
| measured ladder, with the holdout's own bias applied | ~44 h | ~85 GB |
| measured ladder, deceleration stops dead | 251 h | 347 GB |

## The ladder

Eight threads throughout, matching the depth-5 ladder rung for rung, because
the family DP's RSS scales with thread count and a K-slope mixing widths is not
a slope.

| K | wall (s) | RSS (MB) | wall ×/+2K | RSS ×/+2K |
|---|---|---|---|---|
| 8 | 40.04 | 413.8 | — | — |
| 10 | 369.50 | 2,230.0 | 9.23 | 5.39 |
| 12 | 1,951.05 | 7,063.8 | 5.28 | 3.17 |
| 14 | 7,633.96 | 16,877.0 | 3.91 | 2.39 |

Both ratios decelerate, as at depth 5, which is why the projection steps with a
decaying ratio rather than a geometric mean over the range. The extrapolator is
**imported from** `experiments/depth5_cost_ladder.py` rather than
reimplemented, so the two depths are priced by the same arithmetic and any
difference between them is in the data.

## The holdout, and it is worse than depth 5's

`K = 14` predicted from the three rungs below it:

    wall   predicted   6,295 s    measured   7,634 s    -17.5%
    RSS    predicted  14,627 MB   measured  16,877 MB   -13.3%

Depth 5's holdout was 6.9% under on wall and 8.0% over on RSS. This one is
about twice as loose and it errs in one direction: **the extrapolator
underestimates**. Carrying that bias to `K = 21` is what the ~44 h / ~85 GB row
above is, and it is the number to plan against rather than the central one.

## What the assertion got wrong even though its answer was right

B2 obtained 20–60 h and 50–100 GB by "applying the per-excess ladder's ~6× RSS
and ~7–9× wall **once**" to depth 5's projection — that is, treating the
per-excess factor as a constant. It is not:

| K | wall, emax 5 ÷ emax 4 | RSS, emax 5 ÷ emax 4 |
|---|---|---|
| 8 | 6.14 | 3.21 |
| 10 | 7.67 | 4.82 |
| 12 | 8.90 | 6.14 |
| 14 | **10.43** | **6.86** |

The factor grows with K, by about 20% per two units. So the assertion landed in
range by cancelling errors, and **the same method applied to `J = 7` would be
badly wrong** — anyone tempted to price depth 7 that way should run the ladder
instead.

## What it means for the five terms

`Hs = 20` with `J = 6` reaches `n ≤ 45` against a 277 GB pole, where `Hs = 21`
with `J = 4` reaches the same `n` against 580 GB and does not fit dalby's
563 GB free. The depth-6 leg of that route now has measured numbers:

- **RAM forces the thread count.** At 8 threads the projection is ~74 GB
  (~85 GB with the bias), inside dalby's 125 GB. At 16 threads it is ~148 GB
  and does not fit. So depth 6 runs at 8 threads, and that fixes the wall.
- **Wall is then 1.5 to 2 days** for the one `families 21 5` cell, on a box
  whose other 72 cores are idle during it. That is a scheduling fact rather
  than an obstacle, and it is the shape of the run to plan around.
- **Disk is not the constraint anywhere on this route.** The pole is the
  H = 20 sweep at 277 GB, and the family DP's own footprint is RAM.

**None of this is a request, and nothing here says the route should be run.**
It is the measurement B2 asked for, and whether any of it runs is jasonp's
call.

## What it does not settle

Review row **B13 stands and is untouched**: `experiments/severance_w3_depth5_gate.py`
must pass against the banked depth-5 cells at `k ≤ 19` before `D_5` is used at
`k = 21`, and it is correctly RED in production until the `emax = 4` table
exists. A measured price for depth 6 does not create the depth-5 table that
gate is waiting for, and depth 6 is one rung further out than that.
[**2026-08-24: B13 closed** — the table landed and the gate is green
(`results/depth5-gate-green.md`). Depth 6 is still one rung further out. Note
also that the depth-5 run overshot its own RSS bracket by 14%, and this file's
depth-6 projection uses the same method.]

The projection is also two and a half rungs of extrapolation from four points,
with a holdout that missed by 17.5%. It is a price, not a measurement, and the
only measurement here is the ladder.

## Reproduce

    bash scripts/lastditch/emax5_kladder.sh          # dalby, ~2.2 h total
    python3 experiments/depth6_cost_ladder.py
