# Merge Ledger — audit + profile the merger (CPU & memory)

**Plan, not a run.** Companion to [11-quarry-survey](11-quarry-survey-map-profile.md).
Goal: confirm-or-refute the standing claim that **merge is already cheap** (memory
`engine-utilization-and-scheduling`: "merge already cheap (seek-index)") with a real
per-phase ledger, and rule out merge as a hidden RAM or straggler contributor at
a(25) scale. A cheap result is a *finding*, not a foregone conclusion — measure it.

## What we already have (do not rebuild)

`merge_worker` emits `event=done cpu_s wall_s peak_rss_mb records spill_bytes`
(worker/merge_worker.cpp:69). The orchestrator tracks `merge_wall_s/merge_cpu_s`
separately (telemetry.go:127). Note: the mapper *also* runs a merge internally
(`mergeRunFiles` of its spill files, mapreduce.h:420) — so "merge cost" has two
sites: the standalone `merge_worker` (column fan-in) and the in-mapper spill merge.
**Both are the same `mergeRunFiles`/`mergeRuns` code; profile it once, attribute twice.**

## The phases to attribute (mergeRuns, core/mapreduce.h:135; mergeRunFiles, runfile.h)

| # | Phase | Code | A-priori cost |
|---|---|---|---|
| 1 | Open readers + seek to `klo` via `.idx` | merge_worker:51, runfile.h | small (this is the "already cheap" lever) |
| 2 | Heap init (one record/run) | mapreduce.h:152–156 | O(K) |
| 3 | Steady state: `memcmp` compare + heap push/pop | :160–183 | **suspected dominant** |
| 4 | `RunRecord::combine` on equal keys | :177 | range-union + componentwise add; grows with fan-in |
| 5 | `result.push_back` / streamed write + `.idx` | :184 / runfile.h | I/O bound |

Hypotheses: (a) CPU is dominated by phase 3 heap+memcmp, scaling with
`total_records · log K`; (b) `combine` (phase 4) is a small fraction unless fan-in K
is large or keys collide heavily; (c) memory is K reader buffers + the output writer
buffer + (for the in-RAM `mergeRuns`) the `result.reserve(totalRecords)` — the
file-backed `mergeRunFiles` should be ~flat in RAM (streamed), which is the property
to **verify**, since a non-streamed reserve would be a Budget-Blind-class RAM lever.

## Track A — static audit (no run, do first)

1. Confirm `mergeRunFiles` is genuinely streaming: does it hold only K cursor
   records + the write buffer, or does it materialize a `Run<W>` like the in-RAM
   `mergeRuns` (:158 `result.reserve(totalRecords)`)? Read runfile.h:451+ and tag the
   resident set. If it materializes, that is the headline finding.
2. Fan-in audit: how large does K (input run count) get for the dominant column at
   a(23)/a(25)? Cross-ref the merge-fan-in work (designs/06). `combine` cost and heap
   depth both scale with K — fix the realistic K before profiling.
3. `.idx` seek path: verify `klo/khi` bounding actually seeks (skips prefix) rather
   than scan-and-discard — that is the "seek-index makes merge cheap" claim; confirm
   it in code before trusting it in the ledger.

## Track B — dynamic profile (dedicated runs, never on a record job)

Drive the standalone `merge_worker` over a saved set of sorted spill/shard files
from a small height (reuse the Quarry Survey inputs: H 8/maxn 14, H 10/maxn 16).
Vary K (number of `--in` files) to expose the K-scaling of phases 3–4.

**B1. Sampling profiler.** Same tooling as Quarry Survey:
- Linux: `perf record -g` + `perf stat` (expect high IPC, memcmp-bound, low cache miss
  if streamed); macOS: `sample` / `xctrace`. `time -l` / `time -v` for peak RSS.
- Key question perf answers in one trace: is `memcmp` (phase 3) really the top frame,
  and is `combine` (phase 4) negligible at realistic K?

**B2. In-process phase timers (`-DMERGE_PROFILE`).**
Same idiom as the map plan: `clock_gettime` accumulators around phases 3/4/5 plus
counters `{compares, combines, out_recs, K}`. Emit `event=mergephase compare_s=…
combine_s=… write_s=… compares=… combines=… K=…` at finalize. Zero-overhead when
off. Because the mapper's spill merge uses the *same* function, this instrumentation
lights up **both** merge sites for free.

**B3. Memory anatomy.**
- Plot peak RSS vs K and vs total input bytes. The expected result is **flat in
  total bytes** (streamed) and gently rising in K (cursor records + buffers). If RSS
  tracks total input size, phase-A1 found a non-streaming merge → that is the report.
- `heaptrack`/`massif` one run to attribute live bytes: reader buffers vs writer
  buffer vs cursor records vs (if present) the materialized result vector.

## Run matrix

| Box | Inputs | K sweep | Tool | Yields |
|---|---|---|---|---|
| gympie | H8/maxn14 spills | K ∈ {4,16,64} | `sample`+`time -l`+`-DMERGE_PROFILE` | compare-vs-combine split, RSS(K) |
| ayr | H10/maxn16 spills | K ∈ {16,64,256} | `perf`, `heaptrack` | memcmp-bound confirm, streaming confirm |

Minutes per run; **never** against the live frontier job; nothing >1 hr.

## Deliverable

`results/merge-ledger.md`: CPU split (compare vs combine vs write), RSS-vs-K and
RSS-vs-bytes curves with the **streamed-or-not** verdict, realistic K at a(23)/a(25),
and a one-line ruling: **is "merge already cheap" still true at a(25), or does
fan-in K change the story?** Feeds back into designs/06 (fan-in) and 09 (cost model).

## Guardrails

- `-DMERGE_PROFILE` off by default; same zero-overhead A/B proof as the map plan.
- Reuse one shared `-DPROFILE` build switch across both workers if the patches land
  together (keeps the production binary identical).
- Bit-exactness is untouched: merge is commutative+associative (DESIGN §0); confirm
  the profiled build still passes `ns-gate-parallel` (a14/a17 byte-exact).
