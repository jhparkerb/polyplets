# 06 — merge fan-in read amplification: fix + alternatives

## The bottleneck (measured)

Each column's merge runs M = cores·mult `merge_worker`s; each owns a key-range
`[klo,khi)` and is handed **all N map outputs** (which have *overlapping* key
ranges, so any worker's keys can be in any file). `mergeRunFiles` (core/runfile.h)
reaches its range by reading from the **start** of every input and *skipping*
records below klo (`if (key < lo) continue;`). Every one of the M workers does
this independently, so aggregate scan ≈ **M·total/2** — the frontier is re-read
~M/2 times.

Measured (`experiments/merge_read_bench.cpp`, `merge_strategy_bench.cpp`):

| fan-in | A read+skip | seek-index | bucketed / one-pass |
|---|---|---|---|
| mult=1 (M=80) | 40× | 1.0–1.4× | 1.0× |
| mult=4 (M=320) | **160×** | 1.4× (stride 16) | 1.0× |
| mult=8 (M=640) | 320× | 2.7× | 1.0× |

This explains the live a(21) telemetry: map fills 66 cores but merge sits at ~23
and eats 72–91% of the wall. With a(21)'s measured 28% map / 72% merge split,
killing the amplification predicts **~3.4–3.5× faster** (then map is the floor).

## IMPLEMENTED — option B: seek-to-range via a sparse index

`RunFileWriter` emits a sidecar `<path>.idx` (`[u32 keyLen][u64 count]{key,
u64 offset, u64 recidx}`, one entry every `kIndexStride=64` records, native byte
order — a machine-local seek aid, not part of the byte-identical output, and
map+merge of a column run on the same host). `RunFileReader::seekToKey(klo)`
binary-searches it and `fseek`s; `mergeRunFiles` seeks each input to klo instead
of scanning to it. The caller's existing `< lo` skip absorbs the small in-block
overshoot. CRC verification is skipped on a seeked reader (it covers only a
slice). No index ⇒ no-op fallback to scan, so it stays correct on un-indexed
inputs. Spills (`do_spill`) pass `write_index=false` (fully merged then deleted);
the orchestrator GC drops `.idx` via `removeRun`.

Recovers ~99% of the win for a contained change — **this is the a(22) fix.**

### Residual and its limit
The seek-index leaves a residual ≈ **M·N·stride/2** (each of M ranges over-reads
up to one stride per input). It's tunable by stride (1.4× at stride 16, 2.7× at
64) but still scales with (cores·mult)², so it creeps at extreme fan-in. For
a(21)/a(22) (mult≈4, stride 64 ⇒ ~2.7×, ~60× less merge work) that's deep in
diminishing returns — the merge is already a sliver of the wall.

## DOCUMENTED ALTERNATIVES (a(23)/cloud-native)

### Option C — bucketed shuffle (flat 1×, *and* it's the cloud shuffle)
Mappers route successors into per-key-range buckets *at write time* (fixed
hash/range partition), so each merger reads only its bucket — nothing to skip,
**flat 1× at any (cores·mult)²**. Cost: N×M bucket files (fd/inode pressure) or
in-memory partitioning; the map gains a partition router. **This is the MapReduce
shuffle** — bucketed runs are exactly what remote reducers read, so option C is
the foundation for horizontal / cloud-native a(23). Build it when scale (not
single-box speed) is the goal; for a(21)/a(22) wall-clock it buys ~nothing over
B (the last 1.4×→1.0× is buried under the 28% map floor).

### Option D — hierarchical / cascaded merge (flat 1×, sequential)
Replace the single-pass M-way partition with a tree of bounded-fan-in k-way
merges (N → N/k → … → 1), combining equal keys each pass, then slice the single
sorted output into M ranges (trivial, one sequential pass). Reads each record
`log_k(N)≈4×` instead of M/2×, all **sequential** (loves SSD/spill), with small
heaps (log k) and few opens. No extra files. Downside: the single merge isn't
range-parallel — parallelism comes from running the sub-merges of the tree
concurrently, which is more orchestration than B. A good complement to B if the
N-way heap / file-opens become the next bottleneck after amplification is gone.

## Build order
1. **B seek-index (done)** — a(22): ~3.5× on a(21)-class runs, minimal change.
2. **C bucketed shuffle** — when committing to cloud-native a(23) (it *is* the
   shuffle). Flat 1× and horizontally scalable.
3. **D hierarchical merge** — only if, post-B, the N-way heap/opens dominate
   (sequential, SSD-friendly); otherwise C subsumes the need at scale.

Evidence: `experiments/merge_read_bench.cpp`, `experiments/merge_strategy_bench.cpp`.
