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

## Track B — dynamic profile (PENDING)

Needs the K-sweep runs (K ∈ {4,16,64,256}) with `-DMERGE_PROFILE` timers +
perf/heaptrack, per the plan: compare-vs-combine-vs-write split, RSS-vs-K and
RSS-vs-bytes curves (confirm the flat A1 prediction), and whether write-FNV (A4)
is the dominant frame at K≈320.
