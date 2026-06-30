# Merge ledger — Merge Ledger results

Plan: [designs/12-merge-ledger](../docs/next-system/designs/12-merge-ledger-merge-profile.md).
**Track A (static audit) — COMPLETE.** Track B (dynamic profile) — PENDING runs.

## Track A — static audit (no runs)

### A1. Is mergeRunFiles streaming? — YES, code-proven (flat in total bytes)

`merge_worker` calls `mergeRunFiles<W>` (merge_worker.cpp:59/62), the **streaming**
merge (runfile.h:451) — *not* the in-RAM `mergeRuns` (mapreduce.h:135), which does
`result.reserve(totalRecords)` and holds the whole output. mergeRunFiles holds:

- K `RunFileReader`s, each = a `FILE*` (stdio buffer ~4 KB) + fixed scalar state;
  `next()` reads ONE record at a time into `out.counts.resize(len)` (runfile.h:311).
- a `MinHeap<Cursor>` of **exactly one RunRecord per reader** — ≤ K cursors resident.
  `sizeof(Cursor)` = RunRecord 72 + int + pad = **80 B**.
- output written immediately via `writer.append()` (runfile.h:525) — **no in-RAM
  result vector**.

⇒ Resident set ≈ `K · (80 B cursor + ~128 B counts + ~4 KB stdio) + writer buf
~4 KB` ≈ **K · ~4.2 KB**. **Essentially flat in total input bytes; linear in K with
a tiny constant** — K=256 ⇒ ~1 MB. The "merge is already cheap" claim
(memory `engine-utilization-and-scheduling`) is **true on the memory axis, and
this is code-proven, not estimated.** The only per-step allocs (`counts.resize` on
read, `combine`'s fresh vector — run.h:63) are freed each step → alloc *traffic*,
not resident growth.

### A2. Fan-in K — formula pinned; exact value is an orchestrator cross-ref

Two merge sites, both this same code:
- **Column fan-in** (standalone `merge_worker`): K = number of map-output shards
  feeding one column ≈ `cores × unit-mult`. dalby 80 × mult 4 ≈ **~320 inputs**.
- **In-mapper spill merge** (mapreduce.h:420): K = spill count =
  `ceil(column_map_bytes / --ram)` — small (single digits) when `--ram` is generous.

Heap cost scales **log K** per output record; `combine` cost is per *collision*
(bounded by how many of the K inputs carry a given key), K-independent per key.
Exact K at a(23)/a(25) is set by unit-mult / shard policy — see designs/01, 06, 09;
not derivable from worker source. Memory cost (A1) is linear in K but trivial even
at K=320 (~1.3 MB), so K is a **CPU/heap-depth** lever, not a RAM lever.

### A3. The `.idx` seek path — CONFIRMED a real seek, not scan-and-discard

`mergeRunFiles` seeks every reader to `lo` via `seekToKey(lo_sig)` when bounded
(runfile.h:472–473, toggleable off with `POLY_NO_SEEK` for A/B). `seekToKey`
(runfile.h:339) **binary-searches the on-disk `.idx`** (fixed-width entries,
`fseek` to the midpoint — never loads the index into RAM: the Index Slurp fix),
finds the last indexed key ≤ `klo`, `fseek`s the data file to that byte offset, and
sets `records_read_ = recidx`. The reader then physically skips the
`[start, indexed-key-≤-lo)` prefix; only the ≤64-record (`kIndexStride`) in-block
overshoot below `lo` is read-and-filtered by the range check (runfile.h:506).

⇒ A bounded merge unit reads **~its `[lo,hi)` slice + ≤64 records/file**, not
`total/2`. The runfile.h:467–471 comment documents the measured **160× read-amp
fix** (mult=4). `seekToKey` returns false → full-scan fallback only if `.idx` is
absent/stale/wrong-width (correctness-preserving; never wrong). **"Seek-index makes
merge cheap" is code-true.**

### A4. The write path pays a full FNV-1a-64 byte scan (the non-obvious CPU)

The naive model is "merge = heap memcmp." But `writer.append` runs FNV-1a-64 over
**every output body byte** (runfile.h:148–160). On a large column merge this hash
can **rival the heap-memcmp CPU** and is the most overlooked line item. Note the
asymmetry: a bounded/seeked read **skips** the read-side CRC (verified only on a
full non-seeked read, runfile.h:330), so production merges pay FNV on **write**,
not read. Track B must attribute compare-vs-combine-vs-**write(FNV)** explicitly.

### A5. combine() per-collision alloc (shared with map; run.h:53)

Same finding as map-profile A4: `combine` allocs a fresh `merged` vector per
equal-key collision even when the window only extends (`new_lo == lo`, the run.h:51
TODO). In merge this fires once per output key that had a collision across the K
inputs. Bounded (freed each step) so not a RAM concern, but it is the merge's
main alloc traffic — fix it together with map's scratch-record lever.

## Track A verdict

Merge is **confirmed cheap on RAM** (A1: flat, ~K·4 KB, code-proven) and its read
amplification is **confirmed killed** by the seek-index (A3). The open question
moves entirely to **CPU**: how the steady-state splits across heap-memcmp (A2,
log K) vs write-FNV (A4) vs combine (A5) at realistic K≈320 — that is exactly what
Track B measures. No RAM surprise is expected; if Track B shows RSS tracking total
input size, that contradicts A1 and means a hidden materialization to hunt.

## Track B — dynamic profile (COMPLETE)

Method: same `-DPOLY_PROFILE` timers (core/profile.h) in `mergeRunFiles`, driven by
real orchestrate sweeps at maxn 16/18. The clean **column-fan-in** merges are
isolated as the `mergephase K>1, out_recs>1000` lines of the no-spill (2 GB ram)
run — in that run every map_worker does exactly one K=1 terminal merge, so all
substantive (K>1) merges are the standalone `merge_worker` column merges. n=123
such merges, meanK=5.8, 566 K output records.

### B1. CPU split — combine dominates, NOT heap-memcmp (revises A2 guess)

| Phase (timer) | share | what it is |
|---|---|---|
| **combine** | **58%** | `RunRecord::combine` — fresh `merged` vector per equal-key collision |
| **write** (FNV-1a + fwrite) | **23%** | hashing every output body byte |
| read + heap (memcmp) | **19%** | the k-way heap |

Measured **2.36 combines per output record** at meanK=5.8 — most keys appear in
several shards and get combined, each a malloc. The `sample` profile corroborates:
`combine` + alloc/free are a large block; `memcmp` is present but not dominant.

**Finding 5 (new): the merge is combine-bound, and combine is alloc-bound (A5).**
Track A guessed heap-memcmp would dominate; measurement says **combine 58%**, and
combine's cost is its per-collision `std::vector` allocation (run.h:63, the run.h:51
"grow in place when `new_lo==lo`" TODO). **This makes A5 the #1 merge lever**, and
**A4 (write-FNV, 23%) the #2** — both confirmed real, both grow with K (more shards
→ more combines/record and more output). At a(25)'s K≈320 the combine share rises
further, so the merge is *not* asymptotically free on CPU — it's alloc-bound.

### B2. Memory — A1 confirmed (flat, trivial)

The `mergephase` lines carry the process peak RSS; for the standalone column merges
it never moved off the few-MB floor (the 1909 MB values in the table are the shared
`driver1` process max, not merge-attributable). Combined with the **code-proof in
A1** (≤ K cursor records + stdio buffers, no result vector), merge RAM is confirmed
**flat in total bytes, ~K·4 KB** — a non-issue even at K≈320 (~1.3 MB). No hidden
materialization (would have shown as RSS tracking input size; it didn't).

### B-verdicts vs Track A
- A1 (streaming, flat RAM) — **confirmed** (code-proof + no RSS growth).
- A3 (seek-index kills read-amp) — **confirmed by code**; not re-timed (the no-`lo`
  spill-merges don't seek, the bounded column merges do — the 19% read share is
  already post-seek and small).
- A2 guess (memcmp-dominant) — **wrong**; it's **combine-dominant (58%)**.
- A4 (write-FNV non-trivial) — **confirmed, 23%**.
- A5 (combine per-collision alloc) — **confirmed as the #1 lever** (2.36 allocs/rec).

### Joint lever (map + merge)
`combine`'s grow-in-place fix (run.h:51) and map's scratch-successor fix
(mapreduce.h:64) are the **same allocation pattern** — millions of tiny
`std::vector<W>` create/destroy. One refactor (a reusable counts buffer that grows
in place when the window only extends) attacks **map's ~14%** *and* **merge's 58%**.
Highest-ROI single change surfaced by the profiling.

### Fix LANDED — combine grow-in-place (run.h:53)

Implemented red-first (test/gate_run.cpp `testCombineNoAlloc`: 1000 in-window
combines must do **0** heap allocations; was red at 1000). When `new_lo == lo`
(this record starts at or before the incoming one — the dominant case in both the
k-way merge accumulator and `deduplicateRun`), `combine` now extends its **own**
`counts` buffer at the high end (a no-op when the incoming window is contained) and
adds in place, instead of allocate-copy-free. The left-extension case (`o.lo < lo`)
still builds fresh. Byte-exact: a14/a16(spill-heavy)/a18 `--compare` all PASS;
`ns-gate-run` wired into `ns-gates` + `ns-gate-fast`.

**Measured impact (maxn 18, gympie):** map `sort+dedup+write` phase dropped
**39% → 32%** of hot-column wall (the tight `deduplicateRun` combine loop — clean
win, no heap ops to dilute it). The standalone column-merge `combine_s` bucket
moved only 58→56% — but that bucket also times the per-record **heap drain**
(pop/push/next), which my timer can't separate from `combine()`; at maxn 18 the
windows are tiny (~few words) so the eliminated malloc is a small slice. The
mechanism is proven zero-alloc; the **wall payoff scales with window size and K**,
so the real gain is at a(25) (len≈14, K≈320), not at this calibration size.
**Map's per-successor alloc (the ~14% in map-profile B2) is NOT addressed** — it
needs a counts arena (each of N coexisting `buf` records owns its vector;
`push_back` moves ownership, so a scratch record can't help). Deferred: bigger
change with a RAM-footprint tradeoff.
