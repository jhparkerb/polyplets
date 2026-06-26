---
# Standing per-column telemetry — bake the sampler into the engine
*Source: docs/frontier/README.md "do-first" / suggestion #3. Consumers: docs/frontier/oq3-cost-model-calibration.md, docs/frontier/04-adaptive-per-column-config.md, docs/frontier/06-continuous-verification.md. Supersedes the external sampler scripts/a21_telemetry.sh + results/oq3-04-data-collection.md (the perishable scavenge).*

## Problem
oq3 (per-height peak RAM + wall), 04 (per-column state/RAM/throughput), 06 (per-column
count checksum) ALL need per-`(height,col)` telemetry from production sweeps. For a(21)
that data is **perishable**: the heartbeat log (`PROGRESS H=.. col=.. src=.. rate=..
elapsed=..`, sweep8.h L243) carries work + throughput, but RAM-per-column is scavenged by
an external `ps`+proctitle sampler (a21_telemetry.sh) joined offline on `(height,col)`.
Once a healthy frontier job is running we cannot re-instrument it (memory: a21-run-do-not-restart).
The fix: a **default-on, machine-readable per-column telemetry emitter inside the sweep
loop**, so a(22) and every future sweep produce the oq3/04/06 data for free. **Decide
before a(22) launches.** This is mostly *formalizing* what the heartbeat already emits +
adding a per-column RSS high-water + a CSV sink.

## What to emit — one CSV row per (height, col)
A clean machine-readable stream alongside the existing human `PROGRESS` heartbeat. Header:
```
ts,host,N,height,col,ncol,src,out,peak_rss_mb,wall_s,throughput,threads,nbatches,modp_total
```
| field | meaning | source today | consumer |
|-------|---------|--------------|----------|
| `height`,`col`,`ncol` | the join key + position | `H`, `col`, `maxn` in sweep loop (L206) | all |
| `src` | input frontier size (states in) | `total` at column top (L207–208) | 04, oq3 |
| `out` | output frontier size (states out) | next column's `total`, or sum `nextDB[*].size()` post-merge | 04 |
| `peak_rss_mb` | **per-column** RSS high-water | NEW — see §RSS | oq3, 04 |
| `wall_s` | seconds this column took | `steady_clock` at column boundaries | oq3, 04 |
| `throughput` | states/s = `src / wall_s` | derivable; already in heartbeat `rate` | 04 |
| `threads`,`nbatches` | the config that produced the row | `nthreads`, `nBatches` | 04 |
| `modp_total` | running mod-p count checksum, else empty | sweep8_modp.h accumulator (§modp) | 06 |

This is the union: oq3 reads `max(peak_rss_mb)` + final `wall_s` per height; 04 joins
`src`/`out`/`throughput`/`peak_rss_mb` across one height's columns; 06 watches `modp_total`.

## RSS subtlety — why getrusage is not enough
- `getrusage(ru_maxrss)` (obs.h `rss_mb()`) is the **whole-process monotonic peak** — it
  only ever rises, so it yields a per-**height** peak, never per-column. Useless for the
  per-column RAM curve 04 needs.
- `/proc/self/status` `VmRSS` (or `/proc/self/statm` RSS pages × pagesize) read AT a column
  boundary is a **point sample** — misses the in-column peak (the heavy merge transient).
- To get a per-column **peak**: maintain a high-water mark, sample `/proc` *within* the
  column, and reset the mark at each column boundary.

**Recommended:** piggyback on the heartbeat tick. The `PROGRESS` monitor thread already
wakes every `TMA_PROGRESS_SECS` (default 150s, sweep8.h L237–240); on each wake it reads
`/proc/self/statm` and does `g_colPeakRss = max(g_colPeakRss, sample)`. At each column
boundary (top of the `for col` loop, L206) the telemetry hook reads-and-resets that
high-water into the row. Cost: **one `/proc` read per heartbeat tick** (~once/150s) —
negligible. The mark is a single relaxed atomic; the count path never touches it.

**Portability:** `/proc` is Linux-only; the heavy production sweeps run on Linux dalby/ayr,
so `/proc` is the path. On macOS (gympie) fall back to `mach task_info`
(`MACH_TASK_BASIC_INFO.resident_size`) for the high-water, or simply emit `peak_rss_mb`
empty — gympie is not a frontier-pole box. `statm` is preferred over `status` (fixed-format,
no string parse).

## Hard invariant — telemetry must not change any count
Telemetry is **read-only observation**; it MUST NOT perturb the dense gate (byte-identical
to the serial sweep, gate case M, sweep8.h L256–262). Guarantees, by construction:
- **Separate output stream.** CSV goes to its own fd/file; the counting path (`dbS`,
  `nextDB`, `localRow`, the merge) is never read or written by the emitter.
- **No shared mutable state with the count.** The RSS high-water is a private atomic the
  count path never reads; the emitter only *reads* `src`/`out`/`nthreads` (already-computed
  scalars) and `modp_total` (a value the modp engine already maintains).
- **Boundary-only writes.** Rows are emitted at the column boundary, off the hot expand/merge
  loops. `/proc` reads happen on the existing monitor thread, which is already running and
  already only reads atomics. No new lock, no new contention on the count.
- This preserves the existing property that output is independent of thread/batch scheduling
  (L260–262) — telemetry adds no scheduling-visible state.

## Interface
- **Default-on with an off switch.** `TMA_TELEMETRY=0` disables; unset/anything-else = on.
  (The data is the point; opt-out, not opt-in. Cost when on is negligible.) Mirrors the
  existing `TMA_PROGRESS` env convention.
- **CSV path convention:** derive from the heartbeat log path — `h##.log` → `h##.telemetry.csv`
  in the same `runs/.../` dir; override with `TMA_TELEMETRY_CSV=<path>`. Header written once
  on open (append-safe: skip header if file non-empty, matching a21_telemetry.sh).
- **Composes with `--modp`:** when the sweep is a mod-p shadow (sweep8_modp.h) or runs a
  shadow alongside, `modp_total` carries the running validated count (06's checksum column);
  on the plain count sweep the column is empty. 06's comparator reads `modp_total` straight
  from this CSV instead of needing its own sink.

## Why now
- Makes a21_telemetry.sh (the external `ps`/proctitle scavenge) **obsolete for a(22)+** —
  no offline `(height,col)` join, no MISS_LIMIT self-exit race, no proctitle-format coupling.
- Permanently removes the "perishable / can't re-instrument a healthy frontier job" problem
  (memory: a21-run-do-not-restart) — the data is emitted from inside the run that produces it.
- Cost is **~one `/proc` read per heartbeat tick** plus one CSV line per column. The heartbeat
  ALREADY emits `src`/`rate`/`elapsed`/`eta_col` per column (sweep8.h L243–248); this is
  mostly a CSV sink + the RSS high-water on top of code that already runs.
- a(22) is the next pole. Bake it in once and every future sweep self-instruments.

## Effort — t-shirt **S** (ESTIMATE, not a wall-clock)
Files that change:
- `cpp/tma/sweep8.h` — the `for col` loop (L206): wall-clock per column, read-and-reset RSS
  high-water, emit the CSV row at the boundary; teach the existing monitor thread (L234) to
  sample `/proc/self/statm` into the high-water on each tick.
- `cpp/obs.h` — add a `rss_now_mb()` point-sampler (`/proc/self/statm` on Linux, `task_info`
  on macOS) beside the existing `rss_mb()` peak; keep the one-fork pattern.
- `cpp/tma/proctitle.h` — none needed (the proctitle column tracking stays; the CSV no longer
  depends on it). The external sampler's proctitle parse is what this retires.
- driver (`tma_main.cpp`) — wire `TMA_TELEMETRY_CSV` default from the log path; thread
  `modp_total` through when a shadow is active.
- `cpp/tma/sweep8_modp.h` — expose its running total to the emitter (read-only) for the
  `modp_total` column.

## Uncertain (verify against engine before implementing)
- **`out` (output frontier size):** NOT emitted today. It equals the *next* column's `src`
  (the `total` recomputed at L207–208), or `sum_s nextDB[s].size()` after the merge. Cheapest
  is to log `src` only and let the consumer shift-join `out(col)=src(col+1)`; emitting `out`
  directly costs one extra `size()` sweep over `S` shards at the boundary (cheap, but a
  choice). Recommend: emit `out` explicitly so each row is self-contained.
- **`modp_total` readability:** 06 asserts the modp accumulator is readable mid-sweep "by
  construction"; confirmed the count is carried through the validated transition (sweep8_modp.h),
  but it is a per-shard accumulator — summing it at the boundary is the same `size()`/reduce
  cost as `out`. Confirm the reduce is boundary-only (not per-state) before crediting "free".
