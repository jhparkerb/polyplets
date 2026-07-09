# Even Keel D6 — fused stage worker (eliminate the map→merge round trip)

**Branch: `even-keel`** (continues D1–D5). This is the structural change
D6's diagnosis (`docs/even-keel-predictions.md`) proved is needed: the
merge phase is pinned at ~22 effective cores by memory bandwidth — it
re-reads the entire map output that the map just wrote. Config knobs
(unit-mult, merge-mult) are falsified. The fix is to fuse a stage's
map+reduce into ONE multi-threaded pass with the intermediate kept in RAM,
so the data is moved once, not written-then-reread.

**The proof this works already exists:** `experiments/full_column_bench.cpp`
`stageMapReduce` does exactly this (map → scatter by output key into
per-range buckets → per-bucket sort+dedup, all in one process, 80 threads)
and measured **74.6 effective cores** on a real 16M-record H18 stage, with
output verified byte-identical to the sort-merge path. Production's split
map+merge whole-column is ~37. D6 productionizes the benchmark.

## Resolved decisions (do not re-litigate; STOP and surface if code contradicts)

- **DDF1 — architecture:** a single multi-threaded C++ "fused stage" worker
  that, for one mid-column stage, reads the stage-input frontier, applies
  `kinkStageTransition` per record across threads, scatters emitted
  successors by OUTPUT key-range into per-thread-per-range in-memory
  buffers, barrier, then each thread sorts+dedups the ranges it owns and
  writes them. Lift the algorithm from `full_column_bench.cpp`'s
  `stageMapReduce` (proven, output-verified). It replaces
  `{mapPhase + mergePhase}` for stage rounds.
- **DDF2 — scope:** apply fusion to the MID-COLUMN STAGE rounds
  (`r = 0..H-1`) only — the fat, bandwidth-bound rounds. Leave `seed`
  (per-record, cheap, already ~58 cores) and `finalize` (single pass) on
  their current path for now. Do NOT touch the column kernel, kink-sharded,
  or holes paths.
- **DDF3 — threading model:** thread-per-core (`cfg.Cores` threads). Phase 1
  (map): each thread reads a contiguous slice of the input, emits into its
  OWN `threads`×`ranges` buffer set — zero shared mutable state. Barrier.
  Phase 2 (reduce): each thread owns `ranges/threads` output ranges,
  concatenates the per-thread contributions for its ranges, `sortRun` +
  `deduplicateRun`, writes each range's output file. This is exactly
  `stageMapReduce`. Ownership-transfer only; no locks on shared state.
  MANDATORY: a ThreadSanitizer build of the worker must be clean
  (add `ns-gate-fused-asan`/tsan alongside the existing ASan kernels).
- **DDF4 — partition cuts:** the output range boundaries use
  `BalancedCutsMulti` over the stage input (record-quantile, D1) — same as
  today's merge cuts. Number of ranges = `cfg.Cores` (80). The map-side
  scatter uses these SAME cuts so each key lands in exactly one range
  (per DDF-correctness below).
- **DDF5 — RAM:** in-RAM, no spill, for the target terms. Document the
  ceiling: an H18 fat stage is input ~16.5M + emitted ~2× + output ~16.5M
  ≈ 30GB in one process, fits dalby's 122GB. If a future term's stage would
  exceed a safe fraction of RAM (say 60%), the worker must FAIL LOUD with a
  clear "stage too large for in-RAM fusion, needs spill (unimplemented)"
  message, NOT silently OOM. Spill is explicit future work.
- **DDF6 — orchestrator integration:** in `sweepHeightKink`'s round loop,
  replace the `mapPhase(...)` + `mergePhase(...)` pair for stage rounds with
  a single `fusedStagePhase(...)` that dispatches the fused worker with
  `--cores` threads and waits. Preserve: checkpoint at column boundaries,
  ctx-cancellation, per-round telemetry (emit the fused worker's own
  effective-cores as `map_eff_cores` with `merge_eff_cores=` omitted/0 —
  document that fusion collapses the two). The frontier hand-off (stage r's
  output files become stage r+1's input) is unchanged in shape.
- **DDF7 — scheduling scope:** the fused worker uses all `Cores` threads
  itself, so it is incompatible with fine-grained cross-height overlap
  DURING a stage. Scope D6 to `--overlap-heights 1` (the dominant-height
  path — H18 is 70% of wall and runs effectively alone; this is the case
  that matters and the one we confirm). If `--overlap-heights > 1` is
  requested WITH fusion, either (a) fall back to the old map+merge path for
  that run, or (b) reject with a clear message. Resolved: (a) FALL BACK —
  fusion only engages when `overlap-heights == 1`, so existing multi-height
  runs are byte-for-byte unaffected. Integrating fusion with the
  multi-height scheduler is explicit future work.
- **DDF8 — worker lifecycle:** spawn the fused worker fresh per stage
  (H+1 per column — cheap vs today's N units × H spawns). Persistent-worker
  reuse is a later optimization, not required for D6.
- **DDF9 — correctness bar:** the fused stage output MUST be byte-identical
  to the current map+merge output for the same input, and end-to-end
  `a(n)` MUST be byte-identical. Fusion changes only HOW the reduce is
  computed, never the result (same records, same combine, C1/DDF-correct).

**DDF-correctness (the one real hazard, stated explicitly):** the map-side
scatter partitions emitted records by output key using the balanced cuts.
Every record whose key falls in range j goes to range j, from every thread.
So range j's owner sees EVERY contribution to its keys before it
sorts+dedups → the full window is present → `ms`-pruning stays exact and
the combine is complete. A key must NEVER be split across two ranges
(that would fragment its window) — the cuts are on whole keys (a cut is a
key boundary), so this holds by construction. This is the same property the
current merge relies on; fusion preserves it.

## Deliverables

### F1 — the fused stage worker

**Files:** new `worker/fused_stage.cpp` (or a `--stage fused` mode in
`worker/map_worker.cpp` — implementer's choice, but a separate binary is
cleaner to TSan-gate); `Makefile` (build target + tsan gate).

**Steps:**
1. Lift `stageMapReduce` from `experiments/full_column_bench.cpp` into a
   real worker: CLI args mirroring the map worker (`--in` frontier paths,
   `--H`, `--maxn`, `--stage r`, `--counter`, `--out-dir`, `--ranges`,
   `--rev`), reading the real run-file format via `readRangedRunFiles` and
   writing range outputs via `writeRunFile` (with `.idx`, so the next
   stage's `BalancedCutsMulti` works).
2. Compute the range cuts inside the worker via the same record-quantile
   logic (or accept them as args from the orchestrator — resolved: ACCEPT
   from orchestrator, which already has `BalancedCutsMulti`; keeps the cut
   logic in one place).
3. Emit an accounting line with effective-cores (sum of per-thread busy /
   region wall), mirroring D3.
4. FAIL-LOUD on the DDF5 RAM ceiling.

**Tests:** `test/gate_fused_stage.cpp` — feed a known stage input, run the
fused worker AND the existing map+merge path, assert byte-identical output
run files (same records, same combined counts). Include a tight-budget
config (maxn near H) to stress the `ms` boundary. TSan build clean.

### F2 — orchestrator dispatch

**Files:** `orchestrator/sweep.go` (`sweepHeightKink` round loop + a new
`fusedStagePhase`); `orchestrator/worker.go` (args marshalling for the new
worker).

**Steps:**
1. Add `fusedStagePhase(ctx, cfg, H, col, r, frontier, cuts, tel, ...)` that
   dispatches the fused worker with `--cores` threads, waits, returns the
   output range files + acct + tri contribs.
2. In `sweepHeightKink`, when `cfg.OverlapHeights == 1` and the round is a
   stage round, call `fusedStagePhase` instead of `mapPhase`+`mergePhase`.
   Otherwise (overlap>1, or seed/finalize) keep the existing path (DDF7).
3. Preserve checkpoint/ctx/telemetry exactly.

**Tests:** existing `orchestrator` suite green; the two-unit-mult invariant
(DDF9) still holds.

### F3 — correctness gate + F4 telemetry

Fold F3 into F1's gate (byte-identical) and the D4 end-to-end gate. F4 =
the fused worker's eff-cores on the `event=kink_round` line (DDF6).

### F5 — production confirmation (dalby, the payoff)

**Steps:** H16 @ maxn=34 A/B, fused (even-keel D6) vs the pre-D6 even-keel
binary (`934f8c0a`, map+merge), `--overlap-heights 1 --heights 16`,
identical flags, revs verified in banners, byte-identical output checked
(`combine --diff-b`). Report whole-column effective cores and wall. Then,
IF and only IF H16 confirms (whole-column eff jumps from ~37 toward ~60+),
bounded H17 (@maxn34, ~40min×2) as the frontier-scale point. H18 (5.2hr)
only on explicit go-ahead.

**Expected (the prediction to be held to):** H16 whole-column eff ~37 →
**~55-65** (map+reduce fused, no bandwidth-bound merge re-read), wall a
further ~1.5-1.8x beyond D5's 2.84x (so ~4.5-5x vs the original OLD),
byte-identical.
- *If invalidated (fused eff < 50):* the merge cap was NOT the map→merge
  round-trip bandwidth — re-open the diagnosis (profile the fused worker's
  own map vs reduce phase; is the reduce itself bandwidth-bound even
  in-RAM?). This is the key stop-condition.

## Out of scope (explicit)

- Multi-height overlap + fusion integration (DDF7 falls back to old path).
- Spill for stages exceeding RAM (DDF5 fails loud instead).
- Seed/finalize fusion (DDF2 — they're cheap).
- Persistent fused workers (DDF8 — fresh per stage is fine).
- Any substrate change beyond the fused worker itself (no whole-engine
  in-process rewrite; this is one worker, not γ).

## Validation

`make ns-gates` + `go test ./...` green at every commit; the new
byte-identical fused-stage gate and its TSan build MUST pass before F5.
Nothing merges toward master until F5's H16 confirms byte-identical output
AND the effective-cores jump.
