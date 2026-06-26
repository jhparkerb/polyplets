# Frontier idea 04 — Adaptive per-column config (T, B, K)
*Source: docs/scheduling-design.md §"Unexplored axes" #4. Related: cpp/tma/sweep8.h (sweepSquare8HeightMT: nthreads=T, TMA_MERGE_BATCHES=B/nBatches, onColumn hook), docs/frontier/oq1-i7-hot-slot.md, docs/frontier/02-out-of-core-spill.md.*

## Idea
Within one height the columns are wildly uneven — early columns are small and cheap,
the peak column holds `res.peakStates` and is RAM-tight. We currently run a **fixed**
per-height (threads T, merge-batch B = `TMA_MERGE_BATCHES`, inter-height concurrency K).
Vary the config **per phase of the height** instead: more inter-height concurrency K /
fewer batches B early (small columns, cheap to merge), then T-max / high-B / K=1 at the
peak (RAM-bound). Attacks **wall** (idle cores on light columns) and **RAM headroom**
(over-batching small columns, or running K>1 into the peak) without new failure modes.

## Why it might matter here
The lever is real only if the per-column optimum actually moves. Cost is geometric in
column index up to the peak then tapers, and `nBatches` only bounds `loc` RAM — on a
small column high B is pure overhead (more expand/merge barrier passes for nothing); on
the peak column low B risks OOM. K (inter-height concurrency, the RAM↔utilization knob,
scheduling-design I2) is the big one: running two heights at once is fine while both are
in light columns but must collapse to K=1 before either hits its peak. So the *potential*
is "fill idle cores on the cheap two-thirds of every height" + "don't carry peak-config
RAM through the cheap columns." Whether that's 5% or 30% is exactly what the kill-test
measures — no projection.

## Smoke test (dead-on-arrival)
From an existing `h##.log` alone: do rate (states/s) and `src` vary >~2× across a height's
columns? If columns are uniform there's nothing to adapt. The logs already show rate
295→77 within col1 and src 52× col1→col2, so this **PASSES** — the wall half of the lever
has real variance. (The RAM-headroom half needs the per-column RSS sampler — see
results/oq3-04-data-collection.md.) Free, no run.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** is the gap between the *best per-column* config and the *fixed*
config large enough to bother — or do early and peak columns want essentially the same
(T, B, K)?
**Setup:** **pure instrumentation, no new run, no engine change.** The `onColumn(col,
live)` hook in sweepSquare8HeightMT already fires per column with the live state count.
Extend it to also log per-column **peak RSS** (sample /proc/self/statm or
`res.peakStates`-derived bytes) and **expand throughput** (states/s, from the existing
TMA_PROGRESS heartbeat / g_done). Re-read the logs from an **already-completed a(21)
height** at fixed config (h20.log etc. from the live a(22)/a(21) runs). Then compute,
per column, the config that *would* have been optimal (cores that could overlap from K,
B that minimizes barrier passes while keeping `loc` bounded) and sum the modelled wall /
RAM vs the fixed-config actual. Cost: ~hours of log parsing + a spreadsheet model; zero
compute.
**Measure:** (a) modelled wall reduction on the critical-path height from per-column T/K
vs fixed; (b) peak-RAM headroom (GB) freed by not carrying peak-config B/K through the
light columns.
**Two gates — do NOT conflate "variance exists" with "gap is exploitable":**
  - **G1 (free/passive, from logs + sampler):** does the config-OPTIMUM vary across columns
    *at all*? If early and peak columns want essentially the same (T,B,K), there is no gap
    to chase — **NO-GO** here, no replay needed. (The smoke test shows rate/src variance,
    but variance in *load* is not yet variance in *optimal config* — G1 is the latter.)
  - **G2 (active, only if G1 passes):** quantify the GAP — replay ONE column under 2–3
    candidate configs and measure the actual wall/RAM delta vs fixed. **NO-GO if** modelled
    wall reduction < ~15% AND RAM headroom < ~15–20% of the pole.
Decisive because adaptive config adds control-logic surface (and an OOM footgun if K
mis-times the peak); below ~15% *measured gap* it isn't worth that risk against a fixed
config that already works. A config-optimum that doesn't move (G1) is the cheaper kill.

## Substantial-improvement ladder (must clear ALL)
- **C1 — ≥15% wall reduction on the critical-path height OR ≥ ~Y GB peak-RAM headroom**
  — from the per-column model above; one or the other must clear the bar to justify it.
- **C2 — adds NO OOM risk** — RAM stays bounded *per column* (the schedule must drop to
  K=1 / high-B *before* any height's peak column, never after); verified the modelled
  peak RSS never exceeds the box budget at any column under the proposed schedule.
- **C3 — control logic is a static schedule, not a feedback controller** — keyed on
  column index / live-state count crossing thresholds (which the cost model already
  predicts), not runtime RAM-pressure reaction. Simple, deterministic, checkpoint-safe.
*Per-idea bar:* enough wall OR RAM headroom **at the pole** to matter, delivered by a
column-index schedule with **no new OOM mode**.

## Composition / foreclosures
Composes with — does not replace — the engine choice: it tunes whichever expand path is
live (batched merge today, or the I7 shared table, oq1-i7-hot-slot.md). If I7 lands and
makes RAM ~1-copy, the *RAM* half of this idea shrinks (less B/K headroom to win) but the
*wall* half (K overlap on light columns) survives. Forecloses nothing; it's a scheduling
layer over the existing knobs. Ordering: cheap enough (instrumentation only) to run
*before* committing to I7, since it reuses logs already on disk.

## If it passes: effort & where it lands
**S (ESTIMATE)** — the knobs (T = nthreads, B = TMA_MERGE_BATCHES, K via the driver's
inter-height launch) all exist; the work is a per-column schedule table + threading it
through sweepSquare8HeightMT's column loop and the multi-height driver. Lands in
cpp/tma/sweep8.h (column-loop config switch) + cpp/tma_main.cpp (K scheduling) under the
scheduling work-unit-queue (ROADMAP). The kill-test alone is worth doing regardless — it
calibrates the cost model (open-Q #3).
