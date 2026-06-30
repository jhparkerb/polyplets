# Quarry Survey — audit + profile the mapper (CPU & memory)

**Plan, not a run.** Companion to [12-merge-ledger](12-merge-ledger-merge-profile.md).
Goal: a defensible per-phase breakdown of where `map_worker` spends CPU and RAM,
so the a(25)-class tuning levers are picked from measurement, not the cost model's
"~85–90% enumeration" estimate (see memory `crt-counter-shaping-settled`).

## What we already have (do not rebuild)

`map_worker` emits one `event=done cpu_s wall_s peak_rss_mb records spill_bytes`
per invocation (worker/map_worker.cpp:144) and ~2 s `event=progress` pulses. The
orchestrator already separates `map_cpu_s/map_wall_s` from merge in telemetry.go:127
and logs per-column `frontier_in/out, wall_s, cpu_s, rss_max_mb` to the cost profile
(telemetry.go:283). **The whole-process totals are solved. The gap is *intra-process
attribution*** — the survey below carves that single `cpu_s`/`peak_rss_mb` into phases.

## The phases to attribute (map_shard_file, core/mapreduce.h:198)

| # | Phase | Code | A-priori cost |
|---|---|---|---|
| 1 | Reader open + `.idx` seek | :237–249 | small, O(inputs·log) |
| 2 | K-way heap read + equal-key combine | :304–359 | I/O + memcmp; the "frontier in" |
| 3 | `Classifier::complete` (completion test) | :365 | per source key |
| 4 | `forEachViableMask` enumeration | :374 | **suspected dominant** |
| 5 | `stepColumnSquare8` transition / mask | :376 | **suspected dominant** |
| 6 | `completionLowerBound` prune | :379 | per mask |
| 7 | successor build + `counts.assign` (heap alloc) | :383–408 | **suspected #2 / alloc churn** (TODO :64) |
| 8 | `do_spill`: `sortRun`+`deduplicateRun`+write | :286–300 | bursty; grows with spill count |
| 9 | final `mergeRunFiles` of spill files | :420 | = a merge; see Merge Ledger |

Hypotheses to confirm/refute: (a) phases 4+5 are ≥80% of CPU; (b) phase 7's
per-successor `succ.counts.assign` (millions of small heap allocs, flagged in the
:64 TODO) is the largest *non-enumeration* slice and the main allocator pressure;
(c) `do_spill`'s re-sort is cheap relative to enumeration *until* spill count is high.

## Track A — static audit (no run, do first)

1. Walk :66–122 / :302–414 and tag each phase with its allocation behavior:
   which heap-allocate per source key, per mask, per successor. Confirm `succ.counts`
   is the only per-successor allocation and quantify its size (`new_len` words).
2. Re-derive `record_est` (:283) against the *actual* `sizeof(RunRecord<W>)` +
   `counts` capacity + allocator rounding, for W=u64 and u128. Output: predicted
   bytes/record, to be checked against measured RSS/records in Track B (closes the
   Budget Blind loop — is the estimate now accurate or still optimistic?).
3. Note the two known TODO levers (:64): hoist a reusable scratch successor record
   (kill per-mask alloc), and structure-aware merge instead of `sort+dedup`. The
   survey is what decides whether either is worth building before a(25).

## Track B — dynamic profile (dedicated runs, never on a record job)

Run on a small-but-representative shard: a **peak-ish swept height at small maxn**
(e.g. `--H 8 --maxn 14` and `--H 10 --maxn 16`) so the enumeration/alloc mix matches
the real hot column without a multi-hour run. One mapper invocation in isolation,
fed a saved frontier input — not a full sweep.

**B1. Sampling profiler (zero code, first cut).**
- Linux (ayr/dalby): `perf record -g --call-graph dwarf -- ./build/.../map_worker …`
  then `perf report`; `perf stat` for IPC/cache-misses. Confirms the 4+5 vs 7 split.
- macOS (gympie): `sample <pid>` during the run, or `xctrace record --template
  'Time Profiler'`. `/usr/bin/time -l` for peak RSS + page faults (measure, don't
  reason — memory `measure-dont-reason`).

**B2. In-process phase timers (the durable deliverable).**
Add a compile-time-gated (`-DMAP_PROFILE`) accumulator set — `clock_gettime` deltas
into a `struct { double read, classify, enum_step, build, spill, merge; uint64
masks, succ, allocs; }` summed around the phases above. Emit one extra line at
finalize: `event=mapphase read_s=… enum_s=… build_s=… spill_s=… merge_s=…
masks=… succ=… bytes_per_rec=…`. Gated so the production hot loop carries **zero**
overhead when the flag is off (no per-mask branch). This is portable across all
three boxes and survives as a permanent `--profile`-style capability, unlike a
one-shot perf trace.

**B3. Memory anatomy.**
- Peak RSS vs `buf_bytes` budget: does actual peak track `--ram`, or overshoot
  (fragmentation / allocator retention)? Vary `--ram` over {128M, 256M, 512M} and
  plot peak RSS — confirms the spill trigger holds the line.
- Heap detail: Linux `heaptrack ./map_worker …` or `valgrind --tool=massif`;
  attribute live bytes to `counts` vectors vs heap/reader buffers. One run is enough.
- Cross-check measured `bytes_per_rec` (B2) against the audited `record_est` (A2).

## Run matrix

| Box | H / maxn | Tool | Yields |
|---|---|---|---|
| gympie | 8/14, 10/16 | `sample` + `time -l` + `-DMAP_PROFILE` | phase split, peak RSS |
| ayr | 10/16, 12/18 | `perf stat`+`record`, `heaptrack` | IPC/cache, alloc attribution |

Keep maxn small enough that each run is minutes. **Do not** profile against the
live frontier run or start anything >1 hr (memory `frontier-rules-a21-first`).

## Deliverable

`results/map-profile.md`: the phase pie (CPU %), peak-RSS-vs-budget curve,
measured bytes/record vs `record_est`, and a one-line verdict on each of the two
:64 TODO levers — **build before a(25) / not worth it** — with the number behind it.

## Guardrails

- `-DMAP_PROFILE` off by default; prove zero-overhead with an a(14) `--compare`
  timing A/B before and after the patch (gate parity, red-first per
  `quality-gates-red-first-fail-closed`).
- Profiling builds are throwaway; the record binary stays the clean `next-system`
  build (k≤7 injection commit + fix batch).
