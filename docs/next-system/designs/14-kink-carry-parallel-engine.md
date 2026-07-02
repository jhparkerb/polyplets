# Design 14 — Parallel Kink-Carry engine

**Status: OPTION A CHOSEN (2026-07-02).** Smoke-tested serial kernel in
`experiments/kink_tm/`, results in `results/kink-carry.md` — that win stands.
**Option B is NO-GO** (`results/kink-carry-shard-duplication.md`): shard
duplication grows `~S^0.7-0.8`, no plateau, eating most of the kernel's win
at production shard counts. **Option A is GO on volume**
(`results/kink-carry-optionA-volume.md`): H merge barriers per column move
*less* total data than today's one big barrier, and the margin widens with H
(0.20× at H8 down to ~0.009× at H14, extrapolated). **Per-barrier fixed
overhead bounded from production telemetry** at ~6-30ms
(`results/kink-carry-optionA-barrier-overhead.md`) — negligible × H.
Proceeding to Phase 1 scoped to Option A: barrier = stage boundary, not
column boundary.

## What changes and what does not

The engine today (design 00–13) parallelises **within a column**: partition the
source frontier by key into map units, run `map_shard` per unit independently
(each source state → `Σ viableMasks` successor records), then a **single merge
barrier** combines the sorted per-unit Runs into the next column's frontier.
`map_shard`'s per-source cost is the masks-per-state exponential (~1.4k kept
successors/state at H12, growing with H) and its output is `Σ masks` records —
which is what drives sort/spill/merge (126 GB spill peak at a27 H16).

The **kink-carry kernel** replaces `map_shard` and *only* `map_shard`. A column
becomes H sequential micro-stages, each placing one new-column cell with
fan-out 2 (empty/occupied) and merging intermediate mixed-boundary states
(boundary + one carried NW cell + touch flags) by canonical key. Only
**end-of-column states** are emitted. Per-source work drops from `Σ masks` to
`2·H·(intermediate factor)`; the intermediate factor is a **measured flat
~3.6× the frontier**, independent of H. Measured end-to-end: **29× at H12,
~55× at H14, extrapolating ~150–200× at H16** — a per-term compute base drop
from ~4.4 to ~2.5, and end-of-column record volume ~1000× smaller.

Everything downstream of the map kernel is **unchanged and reused**: the
`Run<W>` output contract (sorted end-of-column states, keyLen H+2), `mergeRuns`,
the orchestrator's column loop, height overlap, checkpoint/resume, telemetry,
the spill/zstd machinery (now rarely triggered), and the diagonal P_k closed
forms (orthogonal — they still cap the top swept height; the two wins compose
multiplicatively).

## The parallelisation choice (Option A: shard each stage, H barriers/column)

Each of the H stages within a column is sharded for parallel compute (key-range
split, same partitioning production already does), fanned out independently
(fan-out 2, purely local — no duplication risk since a state's successors
depend only on itself), then **merged back into one canonical stage table**
before the next stage starts. H barriers per column instead of today's one.

Measured (`results/kink-carry-optionA-volume.md`, using `kinkSweep`'s existing
`stageStateSum` counter — no new code needed): total volume moved across all H
barriers is *already smaller* than today's single whole-column barrier, and
the margin widens with H (0.20× at H8 → ~0.009× at H14, extrapolated), because
stage size is flat ~3.6× the frontier while today's single barrier carries
`Σ masks`. Zero duplication by construction — every stage is exact.

Per-barrier fixed overhead bounded from real production telemetry
(`results/kink-carry-optionA-barrier-overhead.md`): tail columns with
near-zero frontier isolate the fixed floor of a full map+merge round-trip at
~6-30ms on dalby. `H × that` is well under a second per column — negligible
against both the volume win above and peak-column wall times measured in
hours. Still open, deferred to the Phase 2 wired-engine gate: whether H
small barriers serialize worker idle time worse than one big one — a
scheduling question the fixed-cost bound doesn't answer.

Rejected:
- **Option B (shard sources, private per-shard stage DP):** duplication grows
  `~S^0.7-0.8` with no plateau, NO-GO at production shard counts
  (`results/kink-carry-shard-duplication.md`).
- **Sibling engine:** duplicates the orchestrator/merge/test harness for no
  benefit. Option A lives in-tree behind a `--kernel` flag, default-off until
  byte-match validated — the same pattern the holes/perim variants used.

## Work-stealing under the kink kernel

Under Option A a steal happens **within a stage**, same shape as today: split
the stage-shard's remaining key-range at a cursor, un-started keys become a
new unit. No duplication — a stolen sub-shard is still just a smaller local
fan-out into the same merge barrier, not an independent private DP. The
existing SIGTERM → stop-at-boundary → `StopKey` machinery carries over
unchanged; the boundary is a stage-local key cursor instead of a column-level
one. Cheaper than Option B's steal story would have been (no rediscovery
cost) — nothing new to measure here beyond the existing steal-overhead
telemetry.

## Milestones (red-first; each gate byte-identical, not approximate)

### Phase 0 — De-risk by measurement (no production code)
- **0.1 Duplication curve (Option B). DONE — NO-GO.** Measured
  (`experiments/kink_tm/kink_shard_probe.cpp`, H=8/12, `--keyrange` and
  `--hash`, gated byte-identical at every S): duplication grows
  `~S^0.7-0.8` with no plateau (1.5× at S=2 → 8.1× at S=32, H=12,
  key-range). Does not hold to the < ~2× bar at production shard counts
  (128-320). Full data: `results/kink-carry-shard-duplication.md`.
- **0.1b Merge-barrier volume (Option A). DONE — GO.** Measured
  (`experiments/kink_tm/kink_tm.cpp`, `stageStateSum` counter, H=8/10/12/14):
  total volume across all H barriers is smaller than today's single barrier
  at every H tested, and the ratio shrinks with H (0.20× at H8 → ~0.009× at
  H14, extrapolated). Zero duplication by construction. Full data:
  `results/kink-carry-optionA-volume.md`. **Decision: Option A chosen.**
- **0.1c Per-barrier fixed overhead. DONE — bounded, negligible.** No new
  code: mined `results/ns_a26/cost_profile.tsv` and
  `results/ns_a27/cost_profile_dalby.tsv` for tail columns (frontier→0),
  which isolate the fixed floor of a real map+merge round-trip (dispatch,
  fork/exec, sync, barrier) from volume cost. Floors at **~6-30ms** on
  dalby, consistent across two heights/runs. `H × that ≈ 0.2-0.5s` added
  fixed tax per column at H16 — negligible against the 100-300× volume
  reduction from 0.1b and against peak-column wall times measured in hours.
  Full data: `results/kink-carry-optionA-barrier-overhead.md`. Closes the
  open question from 0.1b without needing the wired engine.
- **0.2 Production record format.** Confirm the ~3.6× intermediate factor and
  the per-worker RAM projection hold with **ranged u128 rows** (not the probe's
  full u64 rows) at H16 shape. Establishes the real bytes/intermediate-state.
- Deliverable: numbers appended to `results/kink-carry.md`; go/no-go on B.

### Phase 1 — Stage kernel as a `map_shard` variant (library only). DONE
- Option A means the column loop itself gains a level: instead of 1
  map-then-merge per column, it runs **H sequential stage-map-then-merge
  cycles**. Ported the single-stage fan-out (`occupy in {0,1}`, union-find,
  canonicalize) into `core/kink.h`: `kinkStageTransition` (the per-record
  transition, extracted so `experiments/kink_tm/kink_tm.cpp`'s `kinkSweep`
  calls the SAME function — probe and port can't drift apart) and
  `map_shard_stage<W>` (the ranged-`RunRecord` adaptation, mirroring how
  `core/mapreduce.h`'s `map_shard` adapts `forEachViableMask`). Consumes a
  shard of the *current stage's* table (mixed-state key: boundary + carry
  byte + touch flags, keyLen H+4) and produces a sorted `Run` of that shard's
  successor records — same `Run<W>`/`mergeRuns` contract as today, just keyed
  on the stage's mixed state instead of the end-of-column state.
  `Classifier`/column-boundary harvest+finalize (canonicalizeSig/
  completionLowerBound/foldSig at end-of-column) are NOT part of this
  function — those are column-boundary concerns, Phase 2 wiring.
- **Scope v1 = triangle only.** The holes path uses `sig.b[H+2]` for the Euler
  hole count, which the kink state needs for the carry — conflict. Holes stay on
  the column kernel (they are an a19/a20-era concern, off the a(30) path).
- Red-first tests: `test/gate_kink.cpp` (`make ns-gate-kink`, wired into
  `ns-gates`/`ns-gate-fast`). For random stage-table shards at H=4..10:
  (1) `map_shard_stage`'s ranged output matches ground truth — the same
  source records expanded to dense per-n vectors and run through
  `kinkStageTransition` directly, no windowing; (2) shard invariance — split
  a table into shards, `map_shard_stage` each, `mergeRuns` — byte-identical to
  running the whole table at once (the actual Option A parallelism claim).
  Verified red: injecting a windowing bug (dropping the lo-shift) fails the
  gate; a bug inside the *shared* `kinkStageTransition` itself is (correctly)
  out of this gate's scope — that's covered by `kink_tm`'s existing
  whole-column byte-match gate, re-run clean after the extraction
  (`kink_tm 8 16`, `kink_tm 10 18`: "counts identical", numbers unchanged from
  `results/kink-carry.md`). Orchestrator still calls the old path; this phase
  ships dark.

### Phase 2 — Wire behind `--kernel`, gate at a(20)
- Orchestrator column loop grows a stage sub-loop under `--kernel kink`: H
  cycles of (partition current stage table by key → parallel
  `map_shard_stage` → merge → next stage), then the existing end-of-column
  harvest/prune/fold. `map_worker --kernel kink|column` (default column).
  Checkpoint granularity becomes stage-level (finer than today's
  column-level — strictly easier to resume). Telemetry gains a per-stage
  breakdown; steal cursor is a stage-local key boundary (see below).
- **Gate:** full a(20) `--kernel kink --compare` byte-matches the b-file AND a
  whole-column a(20) run — the entire triangle and every T(n,H) identical.

### Phase 3 — Validate at scale + tune (dalby)
- a(24) `--kernel kink --compare` on dalby (a24 is certified): byte-match the
  full triangle and every T(n,H) against banked `results/ns_a24/`. This run is
  simultaneously the **independent reimplementation** the a(23) validation plan
  ([[a23-readiness-and-validation]]) names as the only closure for the
  shared-enumeration-bug gap — so it retroactively hardens a(21)–a(29).
- Measure: real wall, per-height cost profile, intermediate RAM, and the unit
  sweet spot / overlap-heights / steal-grain under the *new* cost shape (map now
  cheap; the merge barrier and end-of-column volume dominate — retune from the
  column-kernel defaults).

### Phase 4 — Production a(30)+
- Only after the Phase-3 byte-match. Re-measure the ladder as each term lands;
  project a(31)–a(33). Expectation from `results/kink-carry.md`: a29's dominant
  H16 (~10⁶ cpu-s whole-column) drops to ~10³–10⁴ cpu-s; a(30)–a(33) go from
  days to hours on dalby. New wall = frontier RAM at D_H ~ 2.6^H (H≈n/2−const)
  plus u128 row bandwidth — a distant ceiling (~a35+).

## Correctness surface (the parts to watch in the port)
- Canonicalise boundary **and** carry together every stage; apply the R1 fold
  **only** at end-of-column, never to intermediates (the probe does both).
- Stranding check as the carry drops off (each stage and at column end): a
  carried component whose label appears nowhere else is unreachable → dead.
- Completion harvest at column start (closable = single component + both touch
  flags), identical to the column loop.
- Every record run keeps the standing bar: gate a(1..18) vs known, full a(20)
  `--compare` byte-match, a21–27 vs banked totals.

## What this moots (stop paying rent)
- Completion-prune tightening (queue #4): already closed at ~2–4%
  ([[completion-oracle]]); irrelevant here — the kink kernel deletes the mask
  enumeration the prune was shaving.
- The map micro-opt backlog (viableRec 91%, PGO, arg-pack): all scoped to the
  *whole-column* kernel; the kink kernel has no `forEachViableMask` hot loop.
- Spill/zstd on the frontier path: intermediates stay in RAM; only the
  (~1000× smaller) end-of-column frontier can spill, and only past the D_H RAM
  wall (~a35+). Spill becomes a distant-scale concern, not a per-term cost.
