# Map profile — Quarry Survey results

Plan: [designs/11-quarry-survey](../docs/next-system/designs/11-quarry-survey-map-profile.md).
**Track A (static audit) — COMPLETE.** Track B (dynamic profile) — PENDING runs.

## Track A — static audit (no runs)

### A1. Per-phase allocation map (map_shard_file, core/mapreduce.h:198)

Walked every phase; tagged heap behavior. Confirmed against `Sig` (32 B inline,
no heap — signature.h:31) and `transition.h:42` (stepColumnSquare8 was moved OFF
`std::vector` to stack arrays precisely because "allocation … dominated the hot
path"; forEachViableMask is likewise stack/union-find over fixed arrays).

| Phase | Code | Heap allocs | Per |
|---|---|---|---|
| Reader open + `.idx` seek | :237–249 | K FILE bufs (~4 KB each) | once / input |
| K-way read + equal-key combine | :304–359 | `next()` does `out.counts.resize(len)`; `combine()` allocs a fresh vector | per record read / per collision |
| `Classifier::complete` | :365 | none | — |
| **`forEachViableMask` + `stepColumnSquare8`** | :374–376 | **none (stack only)** | — |
| `completionLowerBound` prune | :379 | none | per mask |
| **successor build `succ.counts.assign`** | :407 | **1 malloc** | **per surviving mask** |
| `do_spill`: sortRun + dedup + write | :286–300 | sort in place; dedup `combine` allocs; writer FNV-hashes every byte | per spill |
| final `mergeRunFiles` | :420 | = a merge (see merge-ledger) | once |

**Confirmed:** `succ.counts` (mapreduce.h:407) is the **sole per-successor heap
allocation** — exactly as the :64 TODO claims. `succ.sig` is the inline 32-byte
`Sig`; enumeration and the transition are allocation-free. Size of one `counts`
alloc = `new_len` words, `new_len ≈ window width ≈ 0.56·maxn` (run.h:11 + memory
`profile-rows-measured`): ~14 words ≈ **112 B (u64) / 224 B (u128)** at maxn=25,
plus an 8–16 B glibc chunk header rounded to 16.

### A2. `record_est` vs actual resident (closes the Budget Blind loop)

`record_est = sizeof(RunRecord<W>) + maxn·sizeof(W) + 32` (mapreduce.h:283).
Measured `sizeof(RunRecord<W>) = 72` for **both** u64 and u128 (the `vector` is
3 pointers = 24 B irrespective of W; compiled check). So at maxn=25:

| | record_est | actual mean resident/record |
|---|---|---|
| u64 | 72 + 200 + 32 = **304 B** | object ≈ 72 (amortized ~96 w/ vector slack) + counts ≈ 128 ≈ **~224 B** |
| u128 | 72 + 400 + 32 = **504 B** | ≈ 96 + 240 ≈ **~336 B** |

**Finding 1 — record_est is conservative in steady state (good).** It charges
`counts = maxn` words (25) but the real window is ~0.56·maxn (~14), an overcharge
that more than offsets the object-slack undercharge → buf_bytes overstates true
mean resident, so `do_spill` fires *early*. Safe against steady-state OOM; the
Budget-Blind direction (72 vs the old H+4) is correct.

**Finding 2 — record_est models the mean, not the two peak-RSS transients.** It is
blind to:
- **(a) buf geometric doubling.** `buf` is a `std::vector<RunRecord>` with **no
  reserve** (mapreduce.h:271); it doubles by push_back. At a doubling the backing
  array holds up to 2× the live object count, and *during the realloc copy* old+new
  coexist → up to ~3× N·72 B for the object array alone, transiently — invisible to
  `buf_bytes` (which counts only `record_est × N`). At `--ram 1 GB` (~3.3 M records
  by the model) that array is ~237 MB live but spikes ~700 MB at a doubling.
- **(b) millions of tiny `counts` mallocs** → fragmentation + per-chunk header the
  flat `+32` only partly tracks (14% overhead on a 112-B u64 alloc).

⇒ **Prediction for Track B:** `peak_rss_mb` exceeds `--ram` by up to ~2× at a
doubling boundary, gap widest just before a spill. **Cheap fix (independent of the
two TODO levers):** spill on a *record-count* threshold, or `buf.reserve()` once to
the budget cap and treat overflow as the spill trigger — converts the doubling
transient into a hard ceiling. Worth pricing against the OOM margin for a(25).

### A3. The two TODO levers (mapreduce.h:64) — static verdict

- **Hoist a reusable scratch successor + reuse its counts buffer** → removes the
  per-surviving-mask malloc (millions/column; the A1 sole-allocation). Static
  expectation: the single largest malloc-traffic reducer in map, low risk.
  **Recommend build** — confirm its CPU share in Track B (perf/heaptrack) but the
  allocation-count win is certain.
- **Replace sort+dedup with structure-aware k-way merge.** Inputs arrive already
  sorted by the reader heap; `do_spill`'s `std::sort` re-sorts partially-ordered
  data. Only bites when spill count is high. **Defer to Track B** — weight by the
  measured `do_spill` share; not worth it if spills are rare per column.

### A4. Cross-cutting: combine() allocates per collision (run.h:53)

`combine` allocates a fresh `std::vector<W> merged` on **every** equal-key
collision (run.h:63), even when `new_lo == lo` and the window only extends at the
high end (the run.h:51 TODO — could grow in place). Fires in map dedup, the spill
merge, AND the merge worker. Flagged for [merge-ledger](merge-ledger.md) A-track.

### A5. Cross-cutting: the write path pays a full FNV-1a-64 byte scan

`RunFileWriter::append` hashes **every body byte** through FNV-1a-64
(runfile.h:148–160) on every spill and the final merge. The "map is just
enumeration" model omits this; on a large output it is a real, separate CPU line
item. Track B should size `do_spill` + final-merge write CPU including this hash.

## Track B — dynamic profile (COMPLETE)

Method: `-DPOLY_PROFILE`-gated phase timers (core/profile.h, zero-overhead when
off — production rebuild clean under `-Werror`, a14/a16/a18 `--compare` all PASS)
in `build/ns-prof/`, driven by real orchestrate sweeps at maxn 16/18 on gympie (6
cores). Plus a `sample` function profile of a single-process `driver1` sweep at
maxn 17. Raw: `build/profile_n18*.txt`, `build/sample_map.txt` (throwaway).

### B1. Phase split — enumeration does NOT dominate as much as assumed

At realistic `--ram` (2 GB, mid-run spills = 0; each map invocation does exactly
**one terminal `do_spill` then a trivial 1-file merge** — that's the architecture,
not thrash), weighted over the **20 hottest H12 columns** (the a(25) cost drivers):

| Phase (timer) | share | what it is |
|---|---|---|
| **map** (classify + enumerate + step + build/assign) | **61%** | the successor generation |
| **spill** (sortRun + deduplicateRun + write+FNV of the full buffer) | **39%** | terminal sort of the output |
| merge (1-file spill merge) | ~0% | trivial at realistic ram |
| read (heap-drain of the input frontier) | **0%** | negligible — input is one sorted file |

**Finding 3 (new): the terminal `sortRun` of the unordered successor buffer is
~39% of hot-column map wall — not a rare-spill cost but an every-column one.** The
"85–90% enumeration" model undercounts the sort. This **revises the designs/11 A3
verdict**: the second TODO lever (k-way-merge instead of sort+dedup) does *not*
apply at realistic ram (only 1 spill to "merge") — the real target is the terminal
`std::sort` itself, which is intrinsic while successors are generated unordered
(a generate-into-buckets scheme would be the lever, not a smarter spill merge).

### B2. Function-level split (`sample`, leaf self-time) — prices the alloc lever

| Bucket | % of cycles | functions |
|---|---|---|
| **enumeration** | **57%** | `stepColumnSquare8` alone **~44%** + the per-mask lambda + `viableRec` |
| **alloc / free churn** | **14%** | malloc/**free**/emplace/memmove of the per-successor `counts` |
| sort | **~19%** | `__partition` + `recordLess` + sort-side `memcmp` |
| Sig zeroing | 4% | `memset`/`bzero` of the 32-byte `Sig` per record (only ~14 B used) |
| combine | 3% | `RunRecord::combine` |
| write (fwrite) | ~0% | (FNV inlined; small in this window) |

**Finding 4 (new): alloc/free churn is ~14% of map cycles, and `free` (the xzone
free path) costs ~4× `malloc`** — it's the *freeing* of millions of tiny `counts`
vectors that hurts. **This prices the A3 lever-1 (scratch successor record): up to
~14% map speedup, low risk. Recommend build.** Confirms the designs/11 A1 finding
that `succ.counts` is the sole per-successor alloc — and that removing it is worth
real cycles, not just allocation count.

### B3. Memory — Finding 2 confirmed, but the model is self-correcting at scale

- **buf doubling slack is real:** measured `buf.capacity()/buf.size()` up to **1.92**
  at the spill point (Finding 2a confirmed — ~half the backing array is empty slack).
- **`record_est` is ~1.2–1.3× actual** resident at the full buffer (model overcounts;
  conservative → spills early → safe). Over partial buffers the mean ratio is ~2×.
- **Peak RSS vs `--ram`:** at GB-scale budget, peak RSS ≈ **1.0–1.05× `--ram`**
  (2 GB budget → measured peak 1909–2114 MB). The model's ~1.2× over-charge happens
  to **cancel** the ~1.26× doubling-realloc + counts-frag overhead, so **`--ram` is a
  faithful peak-RSS proxy at scale (±10%)**. At a *tiny* budget (16 MB) peak hit
  1.54× — fixed overhead (code, reader buffers) dominates there, not at GB scale.

⇒ **a(25) sizing: budget `--ram` ≈ target peak RSS directly** (the Track-A "~2×
peak" worry is real per-component but nets out). The cheap count-threshold spill
fix is *not* needed for safety at GB scale — the two errors already cancel.

### B-verdicts vs Track A
- A1 (sole per-successor alloc) — **confirmed**, and worth ~14% (B2).
- A2/Finding 1 (record_est conservative) — **confirmed**, ~1.2–1.3× at full buffer.
- A3 lever 1 (scratch record) — **promoted to BUILD** (~14% cycles, B2).
- A3 lever 2 (k-way vs sort+dedup) — **withdrawn**; real target is the terminal
  `sortRun` (Finding 3), addressable only by generate-into-buckets.
- Finding 2 (peak > --ram) — **refined**: true per-component, but nets to ≈1.0× at
  GB scale; `--ram` is a good peak proxy.
