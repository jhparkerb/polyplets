# Even Keel — implementation plan for Design α (balanced-partition full utilization)

**Branch: `even-keel`** (off `redesign`, which carries the design docs and
the three benchmarks that are this plan's evidence base). Every design
decision is resolved below (§Resolved decisions) so the implementer never
has to make a hard call mid-stream. If a step's reality contradicts a
resolved decision, STOP and surface it — do not improvise a different
design.

## What we are building and why (one paragraph)

Measured fact (`experiments/full_column_bench.cpp`, dalby, 2026-07-09): a
real fat H18 stage of 16M records reduces at **74.6 of 80 effective cores
with balanced record-quantile partitioning, vs 6.8 with the current
even-key-range scheme** — same data, same real `kinkStageTransition`,
byte-identical output. So the production kink kernel's ~13.7-effective-core
ceiling on the dominant height is a **partitioning artifact**, not a
fundamental limit. The record-level parallelism to fill the machine is
already in the data; the current partition sampler piles it into a few fat
buckets. Even Keel replaces the sampler so map and merge units carry equal
RECORD counts, which the benchmark proves lifts a fat column ~11x (6.8→74.6
cores) and drops H18's wall floor from 9,336s toward ~1,720s (4–6x on the
70%-of-wall dominant height). This is NOT a rewrite and NOT a new substrate
— it is a surgical fix to `SampleKeysMulti` plus the telemetry to prove it
at production scale, on the existing process+file kink kernel.

## The root cause, precisely (so the fix is aimed correctly)

`orchestrator/runref.go:SampleKeysMulti(paths, H, keyLen, numCuts)` samples
**`numCuts` keys PER FILE** (via `SampleKeys`→`sampleIndexKeys`), dedups
across files, sorts, then `subsampleEvenly`. When the previous round's units
emitted wildly uneven record counts (normal — RGS skew + variable
transition fan-out), a file holding 590M records contributes the SAME
`numCuts` samples as a file holding 64K. The big file is under-sampled, so
the record-rank quantiles are wrong and its records collapse into one range
— specifically the open-ended last bucket `[last_cut, "")` from
`cutsToBounds`. That bucket is the measured 590M-vs-64K straggler
(`docs/utilization-bottleneck-log.md`, `results/steal-tail-h18.md`).

**The fix:** cut on TRUE global record-quantiles. Each `.idx` sidecar holds
exactly one entry per 64 records (`core/runfile.h`, `kIndexStride=64`). The
**union of ALL files' index entries is therefore a uniform 1-per-64 sample
of ALL records across all files, regardless of key-range overlap** — read
that full union, sort it, and take evenly-spaced quantiles. A key that
appears in several files' indexes is simply represented in proportion to
how many records carry it, which is exactly correct for record-balanced
cuts (a hot key gets finer cuts around it). This is the same principle
`SplitRangeByIndex` already relies on ("a simple sorted union of their
in-range index keys is record-balanced") — Even Keel generalizes it from
disjoint frontier files to the overlapping map-output files that mergePhase
partitions.

## Resolved decisions (do not re-litigate)

- **DD1 — partition algorithm:** true global record-quantile via the full
  index-entry union (above). NOT per-file fixed-count sampling. NOT
  key-value ranges. NOT hashing.
- **DD2 — map vs merge cuts:** each phase computes its own balanced cuts
  from its own input files (mapPhase from the frontier; mergePhase from the
  map outputs). They are different data; do not share cuts.
- **DD3 — partition counts:** UNCHANGED. Map = `cores*unitMult` units
  (unit-mult=8, capped by minPerUnit as today); merge = `cores*mergeMult`
  ranges (merge-mult=1 = 80). Only the *balance* of the cuts changes, never
  the count. Do not touch unit-mult/merge-mult.
- **DD4 — reduce primitive:** sort-merge (existing `deduplicateRun` /
  `mergeRunFiles`). NOT hash-aggregation — `experiments/reduce_bench.cpp`
  measured hash-agg at parity-or-worse for this workload (short keys, low
  fan-in, conserved value-copy). Do not introduce a hash table.
- **DD5 — substrate:** UNCHANGED. Go orchestrator + C++ subprocess workers +
  run files. The tmpfs test measured file-I/O at ~7% of wall; no in-process
  rewrite. Do not touch the worker/subprocess boundary.
- **DD6 — in-flight straggler stealing:** UNCHANGED in this effort. Balanced
  up-front partitioning removes the dominant *record-count* straggler (the
  proven win). The existing steal machinery (`stealEligible`,
  `splitRemainder`, `SplitRangeByIndex`) stays as-is to catch residual
  *compute-per-record* skew. Do NOT modify steal logic here; D5 only
  MEASURES whether residual skew remains and, if it does, files a follow-up
  — it does not fix it in this plan.
- **DD7 — correctness bar:** every change is exactly count-preserving. The
  gate is byte-identical `a(n)`: `make ns-gates` clean, and a real
  `--compare` run reproducing known values. Partition boundaries never
  affect the result (the merge recombines by output key regardless of how
  input work was split) — this is the existing invariant; Even Keel must
  preserve it, and the tests in D4 prove it.
- **DD8 — cost ceiling of the sampler:** reading the full index union is
  O(total_records / 64) bytes. At 16M records that is ~250K entries ≈ 10 MB,
  sorted once per round. This is <0.1s against multi-hundred-second fat
  columns — negligible. If profiling ever shows the union read is a
  material cost (it will not at frontier scale), cap it at a large stride
  (e.g. sample 1-per-N index entries for N chosen to keep ≥ 100×numCuts
  samples) — but implement the simple full-union first and only add the cap
  if D5's telemetry shows sampler wall > 1% of round wall.

## Deliverables

Each is independently committable and testable. Do them in order; D1 is the
core, D3 is needed to *prove* D1+D2 at scale, D4 is the correctness gate,
D5 is the production confirmation.

---

### D1 — `BalancedCutsMulti`: the record-quantile sampler

**Goal:** a function that returns record-balanced cut keys from a set of
run files by reading the full `.idx` union.

**Files:** `orchestrator/runref.go` (new function + a small helper);
`orchestrator/runref_test.go` (new tests).

**Steps:**
1. Add `func BalancedCutsMulti(paths []string, keyLen, numCuts int) ([]string, error)`.
   - For each path, open `path+".idx"`, read+validate its header with the
     existing `readIndexHeader`, then read ALL `count` entries (each is
     `keyLen` key bytes + 16 bytes offset/recidx — stride `keyLen+16`,
     header `idxHeaderBytes`). Collect each entry's `bytesToHex(key)`.
     Reuse the exact on-disk layout constants already in `runref.go`
     (`idxHeaderBytes`, entry width). Read the entries in bulk (one
     `io.ReadFull` of `count*(keyLen+16)` into a buffer, then slice), not
     one `ReadAt` per entry — this is a hot path.
   - Drop each file's entry 0 (the run minimum) so a cut never equals a
     run's first key (mirrors `sampleIndexKeys`' existing "skip entry 0").
   - Concatenate all files' entries into one `[]string`, `sort.Strings` it
     (hex sorts as raw bytes), then return `subsampleEvenly(all, numCuts)`.
   - Degenerate cases, matching `SampleKeysMulti`'s contracts exactly:
     `numCuts <= 0` → `(nil, nil)`; a file with a missing/short/only-entry-0
     index contributes no entries (skip it, do not error — same tolerance as
     `SplitRangeByIndex`); if the total union is empty → `(nil, nil)`.
2. **Fallback parity:** if a file has NO readable `.idx` at all,
   `SampleKeys` currently falls back to `sampleBodyKeys` (streaming the run
   body). `BalancedCutsMulti` must preserve availability: if a path's `.idx`
   is unreadable, fall back to `SampleKeys(path, H, keyLen, k)` for that one
   file with `k` proportional to its share (see step 3) and merge those
   samples in. Production runs always write `.idx` (`writeRunFile(...,
   write_index=true)`), so this path is rare; it exists only so a missing
   sidecar degrades to today's behavior instead of dropping a file's records
   from the quantile. Keep it simple: on `.idx` failure, call the existing
   `SampleKeys` with `numCuts` and append its results to the union before
   sorting. (This slightly over-weights an index-less file, acceptable
   because it is the rare degraded path.)
3. `H` is not needed by the index reader (the header is self-describing) but
   keep it in the signature for call-site symmetry with `SampleKeysMulti`,
   or omit it — implementer's choice, but if omitted, update both call sites
   in D2 accordingly. (Resolved: OMIT `H`; the index path never uses it.)

**Tests (`runref_test.go`), RED-first where a bug would hide:**
- `TestBalancedCutsRecordEqual`: build two run files with DELIBERATELY
  uneven record counts (e.g. file A = 100 records over keys `00..63`, file B
  = 10,000 records over keys `64..c7`) with real `.idx` sidecars (use the
  existing test helper that writes a run + index — see how
  `TestSampleKeysMultiSorted` builds `pathA`/`pathB`). Ask for `numCuts`
  such that you split into e.g. 10 buckets. Assert every bucket holds within
  ±10% of `total/10` records (compute per-bucket counts by binary-searching
  each record's key against the returned cuts). The CURRENT `SampleKeysMulti`
  must FAIL this (file B's records pile up); `BalancedCutsMulti` must PASS.
  Include the `SampleKeysMulti`-fails assertion as a documented sub-test so
  the regression is captured in the commit (red-first evidence).
- `TestBalancedCutsSorted`: cuts strictly ascending (extend the existing
  `TestSampleKeysMultiSorted`).
- `TestBalancedCutsDegenerate`: empty paths, numCuts<=0, single tiny file,
  missing-index file → matches the `(nil,nil)`/fallback contracts.

**Done-criteria:** new tests pass; `go test ./orchestrator/...` clean;
`go vet` clean.

---

### D2 — Wire `BalancedCutsMulti` into map and merge partitioning

**Goal:** both phases cut on balanced record-quantiles.

**Files:** `orchestrator/sweep.go` (two call sites); possibly
`orchestrator/sweep_sharded.go` (leave the kink-sharded path ALONE — it is
inert/opt-in and out of scope; do NOT change its `SampleKeysMulti` call).

**Steps:**
1. In `mapPhase` (~sweep.go:1131): replace
   `cuts, err := SampleKeysMulti(frontier, H, keyLen, numUnits-1)` with
   `BalancedCutsMulti(frontier, keyLen, numUnits-1)`.
2. In `mergePhase` (~sweep.go:1451): replace
   `cuts, err := SampleKeysMulti(mapOuts, H, keyLen, numRanges-1)` with
   `BalancedCutsMulti(mapOuts, keyLen, numRanges-1)`.
3. Leave `cutsToBounds`, the unit/range counts, and the steal setup exactly
   as they are. The open-ended last bucket `[last_cut,"")` is now correct
   because `last_cut` sits at the true (n-1)/n record-quantile.
4. Do NOT delete `SampleKeysMulti` yet — the kink-sharded path and tests
   still reference it. Leave it in place.

**Tests:** the existing `orchestrator` suite must stay green (behavior is
result-identical, only balance changes). Add nothing here; D4 covers the
end-to-end correctness.

**Done-criteria:** `go build ./...` clean; `go test ./orchestrator/...`
clean.

---

### D3 — Per-round effective-cores telemetry

**Goal:** production runs must EMIT the effective-cores number per round so
D5 can prove the fix at scale (and so any regression is visible), matching
the metric the benchmark used: `sum(per-worker busy seconds) / round wall`.

**Files:** `orchestrator/telemetry.go` (or wherever `event=kink_round` is
emitted — grep `kink_round`); `orchestrator/sweep.go` (mapPhase/mergePhase
already track per-unit CPU via `Acct`).

**Steps:**
1. Each map/merge round already collects per-worker CPU seconds (`Acct.CPUS`
   summed from `WorkerResult`). The round also has a wall time. Emit, on the
   existing `event=kink_round` line, two new fields:
   `map_eff_cores=map_cpu_s/map_wall_s` and
   `merge_eff_cores=merge_cpu_s/merge_wall_s` (guard divide-by-zero → 0).
   These are exactly `cpu/wall` (NOT divided by cores) so the reader sees
   "cores busy"; a value near `cfg.Cores` means full utilization.
2. Also add a per-COLUMN roll-up on the `event=column` line:
   `eff_cores=cpu_s/wall_s` (the column's own aggregate). `cost_profile.tsv`
   already has per-column `wall_s` and `cpu_s`; no schema change needed there
   — its `util%` is derivable. This step is only the log line, for live
   observation.
3. Keep it a pure addition — no existing field renamed or removed
   (downstream awk in `scripts/bench_util.sh` and analysis parse positionally
   / by `key=`; appending is safe, reordering is not).

**Tests:** a small unit test that a synthetic round with known cpu/wall
emits the expected `map_eff_cores`. Gate suite stays green.

**Done-criteria:** a local `--compare` run shows the new fields; values are
sane (≤ cores, > 0 on real rounds).

---

### D4 — Correctness gate: balanced partitioning is count-preserving

**Goal:** prove Even Keel changes NOTHING about the answer.

**Files:** `orchestrator/` test; reuse existing `--compare` machinery.

**Steps:**
1. `make ns-gates` (both ASan kernels) and `go test ./...` — must be clean.
2. Add a gate-level test that runs a small full sweep (e.g. maxn=16 or 18,
   the same size `gate_parallel` uses) with the balanced sampler and asserts
   every `a(1..maxn)` matches `fixtures/b006770.txt` byte-for-byte. If a
   `gate_parallel`-style harness already does this, just confirm it passes on
   `even-keel` — the balanced cuts must not change any value.
3. Explicit invariant test: run the SAME small sweep twice with different
   `--unit-mult` (hence different partition counts AND different balance) and
   assert byte-identical output — codifies DD7 (partition boundaries never
   affect the result).

**Done-criteria:** all gates green; `a(1..18)` byte-identical to known
values on `even-keel`; the two-unit-mult invariant test passes.

---

### D5 — Production-scale confirmation on a real fat height

**Goal:** show the 6.8→74.6 benchmark result reproduces on a REAL sweep, and
quantify the real wall-clock win. This is the "then real" half of the
approved plan.

**Steps (dalby, each run bounded < 1 hour; ASK before anything longer):**
1. Pick a real fat but bounded height: `--heights 17 --maxn 30` (H17 is
   real-swept at maxn=30 and fat; calibrate timing first with a smaller
   height as in this session's `iotest`). Run once on `master`/`redesign`
   (old sampler) and once on `even-keel` (balanced), IDENTICAL flags
   otherwise, `--compare` or per-height-out for correctness.
2. From `cost_profile.tsv` + the new D3 telemetry, report per-column and
   whole-height effective cores, OLD vs NEW. Expected: fat columns jump from
   ~13-14 toward ~50-75 effective cores; wall drops materially.
3. Confirm byte-identical per-height output (`combine --diff-b` against the
   old run's per-height files, or `--compare` on both).
4. Record the numbers in `docs/full-utilization-redesign.md` (a "D5
   confirmation" note) and `HANDOFF.md`.
5. **Residual-skew check (feeds DD6):** if any fat column's effective cores
   stay well below ~60 after balancing, the residual is compute-per-record
   skew (not record-count) — file a follow-up for in-flight compute-time
   stealing (the existing `stealScore` wall-path, currently gated by
   `remaining()<2*indexStride`). Do NOT fix it in this plan; just measure and
   report.

**Done-criteria:** a real fat height shows a large, byte-identical-output
effective-cores improvement, recorded. If it does NOT (fat columns stay near
13.7 even balanced), STOP and surface — the benchmark and production would
disagree and that must be understood before proceeding.

## Sequencing and validation

D1 → D2 → D3 in order (D3 can land alongside D2). D4 gates the merge-back:
nothing merges toward master until D4 is green. D5 is the empirical sign-off.
Run `make ns-gates` + `go test ./...` at every commit (the pre-push hook
enforces this). Keep commits small and each independently green.

## Out of scope (explicit, so nobody gilds the lily)

- No substrate/in-process rewrite (γ — dead, I/O is 7%).
- No hash-aggregation reduce (ρ — measured parity-or-worse).
- No changes to steal logic, unit-mult/merge-mult, GOGC, persistent-workers
  (all deployed and validated; DD3/DD6).
- No touching the kink-sharded code path (inert, opt-in, superseded by α).
- No cross-height scheduling changes (the model showed X is insensitive once
  ceilings rise; that is a SEPARATE later effort, worth ~30% on top, tracked
  in `docs/full-utilization-redesign.md`'s schedule-model section — not here).

## Evidence base (all on `redesign`/`even-keel`)

- `experiments/full_column_bench.cpp` — the 6.8→74.6 measurement.
- `experiments/reduce_bench.cpp` — ρ-vs-α parity (why DD4 = sort-merge).
- `scripts/iotest_tmpfs.sh` — I/O = 7% (why DD5 = keep substrate).
- `docs/full-utilization-redesign.md` — full derivation, constraints C1–C8,
  the schedule model, and the measured verdicts.
