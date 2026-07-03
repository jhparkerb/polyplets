# HANDOFF — 2026-06-29

## 2026-07-03 — gate hardening: ns-gate-spill "failure" was fd limit, not kink-carry

While starting Design 14 Phase 3 (validate kink-carry via a(29)), `make
ns-gates` on dalby appeared to fail `ns-gate-spill` (wrong a(11)=39242406).
**kink-carry was NOT the cause.** Controlled A/B (scripts/gate_spill_ab.sh,
same box/gcc): `next-system` fails it IDENTICALLY. Root cause = `ulimit -n
1024`: the `--ram 1MB` gate forces >1024 simultaneous spill files, fopen
fails. Proven: `ulimit -n 8192` -> gate passes, spill bytes = 567231991
(matches gympie's correct-behavior reference). Does not affect production
(1GB/worker -> few big files; a(29) validated fine).

It exposed a real **fail-OPEN** bug though: `core/runfile.h`
RunFileWriter/mergeRunFiles silently DROPPED data on open failure (append()
no-op'd, finalize() returned 0) -> plausible undercount with no signal. For
a(30)+ (no --compare oracle) that's a silent-corruption hazard, violating
the fail-closed rule.

**Fixed + committed on kink-carry** (red->green->headroom in git log):
- `77102d7` RED: gate_runfile fork-based fail-closed tests (writer + merge
  open-failure must abort). Failing at that commit by construction.
- `9ee3050` GREEN: RunFileWriter constructor + mergeRunFiles now `exit(1)`
  on open failure instead of dropping data.
- `f75c0b7` `core/fdlimit.h` `raiseFdLimitToHard()` (setrlimit soft->hard,
  no root; both boxes' hard cap >=524288), called from driver1/map_worker/
  merge_worker main().
- `5aec4cf` the A/B diagnostic script.

**VERIFIED:** full `make ns-gates` GREEN on dalby (gcc 15) at default
`ulimit -n 1024` — gate_spill + gate_runfile + all four kink gates pass.
dalby is at kink-carry `5aec4cf`. **ayr is stale** (kink-carry `30c5580`,
lacks these fixes) — sync before it does any task-5 work.

**Not yet done:** the actual dalby-scale a(29)/a24 `--kernel kink` cell-diff
run (the real Phase 3 validation) — a compute job needing go-ahead. Nothing
capability-blocks trusting kink-carry: the a(20) `--kernel kink --compare`
production-path gate already passed. Nothing pushed to origin (github sync
broken on all boxes — task #1).

---

## 2026-07-02 (later) — a(29) lands, dalby free; a24 kink precheck PASSED

**a(29) = 33145129805782422061325** landed dalby-solo (PID 2243059, rev
`7e28071`), wall **26202.2s (~7.28h)**, 80 cores. Combined+validated:
a(1)-a(20) byte-match the b-file, a(21)-a(28) match certified results
(including this session's a28), growth a29/a28 = 6.8700 (monotone, still
rising toward λ≈7.1). Banked to `results/ns_a29/` and committed
(`74478be`), not yet pushed. **dalby is now free**, no live jobs.

**Design 14 Phase 3 ayr pre-check PASSED** while waiting on dalby:
`scripts/ayr_a24_kink_precheck.sh` ran `orchestrate --maxn 24 --kernel
kink` on ayr, rc=0 in **232s**. Total value byte-matched
`results/ns_a24/a_n.txt`. Note this ran fast because current code's
closed-form diagonal (P8-P11, k=2..12) now covers heights down to H=13 at
maxn=24 — the real sweep only needed to reach H=12, unlike the *historical*
column-kernel a(24) run (predates P8-P11) whose dominant real height was
H16. Don't reuse that old H16 timing as a cost basis for kink-kernel runs
on current code — the closed-form coverage has grown since. This was a
total-value check only, not the full per-height cell diff (`combine
--diff-b`) the formal Phase 3 gate does.

**Both dalby and ayr are free now.** Next candidates: Design 14 Phase 3
proper (dalby-scale `--kernel kink --compare`, full cell diff + retune) or
a(30) per [[a26-a30-diagonal-plan]] ([[a26-a30-diagonal-plan]] memory) —
either needs jasonp's go-ahead before launching (both would run >1h).
ayr's worktree is still on `kink-carry` (rev `30c5580`) — resync to
`next-system` before its next production a(n) run, if that's what's picked
next.

---

## 2026-07-02 (post-/clear) — a(28) landed on ayr; dalby a(29) still running

**a(28) = 4824589228356722264087** (first sextillion term) was sitting
unrecorded on ayr — `scripts/ayr_a28.sh` had completed (all 28 heights
present, no live process, run.log ends with the final `wall=11723.8s`
summary line) while ayr's worktree had since moved to `kink-carry` for
Phase 2 gate work, so nobody had gone back to combine+bank it. Recomputed
via `combine -in runs/ns_a28/perheight -maxn 28`: a(1)-a(20) byte-match the
b-file, a(21)-a(27) match certified `results/ns_a2{1..7}` exactly, growth
a28/a27 = 6.8616 (monotone). Banked to `results/ns_a28/` (triangle.txt,
PROVENANCE.md, perheight/, cost_profile_ayr.tsv) this session, not yet
committed. Tier: computed, single-source, pending certification — same as
a26/a27 before it. **ayr is now free** (job long done); its worktree is
still on `kink-carry` rev `30c5580` and needs resync to `next-system`
before its next production a(n) run.

**dalby a(29)** (orchestrate PID 2243059) is still on H16, now col=6 (H15
finished last session), rate declining column-tail-like (same shape H15
col5 showed on this same box, and H15 tail showed on ayr's a28 run) —
normal, not stuck. No `eta=` field in this engine's heartbeat, so no ETA
quoted. A persistent Monitor is armed against this PID's run.log to notify
on completion; do not poll manually.

**Design 14 Phase 3** (`orchestrate --maxn 24 --kernel kink --compare` on
dalby) is still queued behind dalby's a(29) — needs explicit go-ahead once
dalby frees up, per standing job-launch rule.

---

## 2026-07-02 (session end, pre-/clear) — SAVE-STATE

**Branch `kink-carry`, tip `b3ff955`, pushed to origin. Tree clean** (one
untracked file `autonomy` at repo root, not created by this session — leave
it, don't delete without checking with jasonp).

### Live jobs
- **dalby — a(29)**, orchestrate PID **2243059**, ~4h44m in, healthy (RSS
  106MB, low CPU%% between heartbeats is normal — heartbeats show real
  progress: H16 col6, rate ~4-5k rec/s). H15 has finished; only H16 (the top
  real height) is left grinding. Launch estimate was ~4-5h wall, so this is
  in the expected final stretch. **Do not touch** (correctness-or-dead-box
  bar only, per standing rule). No armed waiter from this session — if you
  want a completion notification, arm one against PID 2243059 on dalby.
- **ayr — free.** Its `~/src/polyominoes-ns` worktree is on `kink-carry`
  (rev `30c5580`, map_worker/merge_worker/orchestrate/combine freshly
  rebuilt there) — **NOT** `next-system`. Re-sync to `next-system` before
  ayr's next production a(n) run.
- **gympie — idle** (local dev box, this session's work happened here).

### What finished this session: Design 14 Phase 2, all of it (2.1-2.9)
Kink-carry parallel engine wired behind `--kernel kink` (default stays
`column` — production untouched). Sequence: 2.1 keyLen de-hardcoding, 2.2
`core/kink_column.h` seed/finalize, 2.3 file-backed stage kernel, 2.4
map_worker CLI wiring, 2.5 Go `Kernel` field threading, 2.6 `mapPhase`/
`mergePhase` extension + `sweepHeightKink` (caught and fixed a real
filename-collision bug along the way), 2.7 `combine --diff-b` per-height
cell-diff tool, 2.8 **the real gate — PASS on ayr**: a(20) `--kernel kink
--compare` byte-matches the b-file, and every single `T(n,H)` cell matches
the column kernel for H=1..20 (not just the summed total). 2.9 closed out
the design doc (`docs/next-system/designs/14-kink-carry-parallel-engine.md`,
status now "PHASE 2 DONE") and this file. Each step was its own commit,
red-first tested, full `make ns-gates` green before moving on.

### NEXT: Phase 3 — dalby-scale a(24) validation (needs go-ahead)
`orchestrate --maxn 24 --kernel kink --compare` on dalby, byte-matching the
full triangle + every T(n,H) against banked `results/ns_a24/`. Doubles as
the independent-reimplementation closure the a(23) validation plan names
([[a23-readiness-and-validation]]) — retroactively hardens a(21)-a(29).
Also retune unit-mult/overlap-heights/steal-grain under the new cost shape
(map now cheap, merge-barrier-dominated) rather than assuming the
column-kernel defaults carry over. Real compute job — needs explicit
go-ahead, and dalby is busy with a(29) until that finishes.

### Loose end, not urgent
A stray background-task notification arrived this session for a task
("H=14 oracle probe") this session never started and produced no output.
Not investigated — harmless, but flag it if it recurs or if jasonp knows
what it was.

---

## 2026-07-02 (latest) — Design 14 Phase 2 DONE — a(20) --kernel kink gate PASS

Branch **`kink-carry`**, tip `30c5580` (pushed to origin). Tree clean.
dalby a(29) still running untouched; no other live jobs.

**2.8 gate ran on ayr with jasonp's go-ahead** (`scripts/kink_gate_a20.sh`,
~30s wall): both `orchestrate --maxn 20 --kernel kink --compare` and the
`--kernel column` baseline byte-matched the b-file (a(1..20)), and
`combine --diff-b` confirmed **every T(n,H) cell identical between the two
kernels for H=1..20**, not just the summed total. Full Phase 2 (2.1–2.8) is
done; design doc `docs/next-system/designs/14-kink-carry-parallel-engine.md`
updated to status "PHASE 2 DONE" with the settled implementation shape
(harvest-at-seed, column-level checkpointing, the filename-collision bug
found and fixed in 2.6 — see the doc's Phase 2 section for detail).
`--kernel` CLI default stays `column`; kink is reachable only by explicit
flag, so production a(n) runs are untouched.

**ayr note:** its `~/src/polyominoes-ns` worktree is now on `kink-carry`
(rev `30c5580`) with a freshly rebuilt map_worker/merge_worker/orchestrate/
combine — NOT `next-system`. Re-sync to `next-system` before ayr's next
production a(n) run.

### NEXT: Phase 3 — dalby-scale a(24) validation
Per the design doc: `orchestrate --maxn 24 --kernel kink --compare` on
dalby (a24 is certified) byte-matching the full triangle and every T(n,H)
against banked `results/ns_a24/`. This run doubles as the independent
reimplementation the a(23) validation plan
([[a23-readiness-and-validation]]) names as the closure for the
shared-enumeration-bug gap — retroactively hardens a(21)-a(29). Also:
measure real wall/per-height cost/intermediate RAM and retune
unit-mult/overlap-heights/steal-grain under the new (map-cheap,
merge-barrier-dominated) cost shape — the column-kernel defaults don't
necessarily carry over. This is a real compute job at a24 scale: needs the
standing job-launch go-ahead before running, same as always.

---

## 2026-07-02 (still later) — Design 14 Phase 2: 2.7 DONE, 2.8 needs go-ahead

Branch **`kink-carry`**, tip `abd7228`. Tree clean.

- **2.7** `abd7228` — `combine --diff-b DIR[,...]`: compares `--in`'s
  per-height `h<H>.out` rows against another dir set CELL BY CELL (every
  `T(n,H)`), not just the summed `a(n)` total the normal mode checks. Missing
  height on either side, or any differing cell, fails loud with a per-height
  report. Red-first (`TestRunDiffCatchesCellMismatch`/`MissingHeight`
  verified to fail against a broken `runDiff` first). Full `make ns-gates`
  green.

### NEXT: 2.8 — the real gate, NEEDS EXPLICIT GO-AHEAD before launch
Per the plan file: `orchestrate --maxn 20 --kernel kink --compare` (byte-matches
the b-file) **and** `combine --diff-b` diffing kink's `--per-height-out`
against a `--kernel column` a(20) run's, cell by cell. Short (a(20) scale),
but per the standing job-launch rule this specific launch needs jasonp's
explicit assent first — ask before running it, don't just launch. `--kernel`
CLI default stays `column` until this is green, so nothing in production is
at risk either way. 2.9 (close-out) is just doc updates once 2.8 passes:
design doc Phase 2 -> DONE, this handoff's NEXT -> Phase 3 (dalby-scale a(24)
validation).

---

## 2026-07-02 (later still) — Design 14 Phase 2: 2.5-2.6 DONE, next up 2.7

Branch **`kink-carry`**, tip `3eed44b`. Tree clean. dalby a(29) still running
untouched throughout (see its own note below); no other live jobs.

- **2.5** `dafda52` — `SweepConfig.Kernel`/`Checkpoint.Kernel` ("column"
  default, "kink"), `checkResumeConfig` fail-closed guard on kernel mismatch,
  `MapArgs.Kernel`/`Stage` threaded into `RunMapWorker`'s CLI args, `--kernel`
  flag on `cmd/orchestrate` (validated `column`/`kink`). Gate: Go unit tests
  (checkpoint round-trip + `TestResumeKernelMismatch`).
- **2.6** `3eed44b` — `mapPhase`/`mergePhase` extended with additive
  `keyLen`/`stage` params (default = today's column-kernel values, proven
  byte-identical by the unchanged full gate suite); `Run`/`runOverlap` get a
  one-line `sweepHeightFn` dispatch on `cfg.Kernel`. New `sweepHeightKink`:
  per column, one seed round (H+2->H+4, harvests via classify), H mid-column
  stage rounds (H+4->H+4), one finalize round (H+4->H+2) — barriers at every
  stage (Option A) instead of once per column. Work-stealing gated off for
  seed/finalize (in-RAM, no SIGTERM stop protocol), stays on for the
  file-backed mid-column stages. **Fixed a real bug found while writing
  this**: map/merge output filenames were keyed only on `(H,col,idx)`, which
  every round of a kink column shares — a later round's merge would
  overwrite an earlier round's still-live output, and column-boundary GC
  would delete a just-produced round's table because it aliased the
  previous round's name. Both now tag the filename with the round's stage
  string. Gate: new `orchestrator/kink_sweep_test.go` drives `sweepHeight`
  and `sweepHeightKink` through the real compiled workers at H=6/maxn=14 and
  H=10/maxn=20 (off Run's closed-form short-circuits) and diffs the
  resulting triangle rows byte-for-byte — PASS at both. Full `make ns-gates`
  green (4m38s) after each commit.

### NEXT: 2.7 — per-height triangle diff tool
Per the plan file (`/Users/jasonp/.claude/plans/declarative-wobbling-canyon.md`):
no existing tool does a cell-by-cell T(n,H) comparison between two
`--per-height-out` directories (`combine` only sums-and-compares the final
`a(n)` total). Add a small comparison mode — new flag on `combine` or a
standalone script — diffing two `h<H>.out` directory sets row-by-row,
failing loud on any mismatch. No compute job, no go-ahead needed.

**Then 2.8 — the real gate (needs explicit go-ahead before launch):**
`orchestrate --maxn 20 --kernel kink --compare` (byte-matches the b-file)
**and** the 2.7 tool diffing kink's `--per-height-out` against a
`--kernel column` a(20) run's, cell by cell. Ships dark (`--kernel` default
stays `column`) until this is green. Confirm with jasonp immediately before
this specific launch even though it's short (a(20) scale, not production).
2.9 closes out: design doc + this handoff updated to Phase 3 (dalby-scale
a(24) validation).

---

## 2026-07-02 (late night) — Design 14 Phase 2: 2.1-2.4 DONE, paused before 2.5

Branch **`kink-carry`**, tip `8561103`. Tree is CLEAN at this commit (an
in-progress 2.5 edit — one line adding `Kernel string` to `SweepConfig` in
`orchestrator/sweep.go` — was reverted per jasonp's request rather than left
half-done; nothing uncommitted). a(28)[ayr] finished cleanly during this
session (rc=0, ~3h15m wall, see its own note below) — combine/validate is
still outstanding and is jasonp's call, not touched here. a(29)[dalby]
status not rechecked this session.

**Plan file**: `/Users/jasonp/.claude/plans/declarative-wobbling-canyon.md`
has the full Phase 2 sequencing (2.1 through 2.9) approved by jasonp,
including three decisions locked in before coding started:
- Extend `mapPhase`/`mergePhase` in place with additive keyLen/Stage params
  (not a private fork) for 2.6.
- In-RAM-only seed/finalize for Phase 2; file-backed variants deferred to
  Phase 3.
- Column-level checkpointing for Phase 2; stage-level deferred.

**Steps 2.1-2.4 done, each its own commit, each gated green
(`make ns-gates`, full suite, ~4.5min):**
- **2.1** `ca9a524` — de-hardcoded `keyLen` in `orchestrator/runref.go`'s
  `SampleKeys`/`SampleKeysMulti`/`SplitRangeByIndex` (was hardcoded H+2
  internally); added `columnKeyLen(H)`/`kinkKeyLen(H)` Go helpers; threaded
  explicit `columnKeyLen(H)` through the 3 production call sites in
  `sweep.go` (byte-identical no-op for the column kernel). Added optional
  `--keylen`/`MergeArgs.KeyLen` to `merge_worker.cpp`/`worker.go`.
- **2.2** `8a50a04` — new `core/kink_column.h`: `kinkSeedStage0` (column
  start: harvest via `Classifier::complete`, then seed stage 0 — order-
  preserving constant 2-byte key suffix, no sort/dedup needed) and
  `kinkFinalizeColumn` (column end: drop carry with stranding check,
  canonicalize, admissibility-prune, R1-fold, dedup — no classify, harvest
  already happened at seed). Re-read `experiments/kink_tm/kink_tm.cpp`'s
  `kinkSweep()` column loop directly to settle a design-doc ambiguity:
  harvest is at column START not column end. Gate: `test/gate_kink_column.cpp`
  (`make ns-gate-kink-column`), red-verified two ways (dropping seed's
  classify call fails to compile via `-Werror`; skipping the stranding
  check compiles but fails the gate with a record mismatch).
- **2.3** `3c8db4d` — `map_shard_stage_file<W>` in `core/kink.h`: file-backed
  spilling twin of Phase 1's `map_shard_stage`, mirroring
  `map_shard_file`'s shell (K-way heap, spill, progress pulse, SIGTERM
  stop-key) but no Classifier/Output param, `kinkKeyLen(H)` threaded
  explicitly everywhere including into `mergeRunFiles`'s final-write call.
  `KinkStageCfg` gained `ram_budget_bytes`/`spill_dir` fields. New
  `kKinkProgressStrideMask` (distinctly named — `map_worker.cpp` includes
  both `mapreduce.h` and `kink.h` in the same TU as of 2.4, so
  `mapreduce.h`'s `kProgressStrideMask` can't be reused without a name
  collision). Gate: `test/gate_kink_stage_file.cpp`, red-verified (dropping
  explicit keyLen from the final `mergeRunFiles` call corrupts every record
  read back — CRC mismatches). SIGTERM stop-key round-tripping explicitly
  deferred to 2.4's CLI-level gate (driven by a real subprocess, not
  synthesized in-process).
- **2.4** `8561103` — `map_worker.cpp` CLI wiring: `--kernel column|kink`
  (default `column`) + `--stage seed|<int>|finalize`. `seed`/`finalize` are
  in-RAM (new `readRangedRunFiles`/`writeRunFile` helpers in
  `map_worker.cpp`, mirroring `map_shard_file`'s range-filter/output shape,
  still respect `--lo`/`--hi`); the mid-column `<int>` stage is file-backed
  via 2.3's `map_shard_stage_file`. Rejects `--holes` with `--kernel kink`.
  Gate: `test/gate_kink_worker_cli.cpp` drives the REAL compiled binary
  (not the functions directly) through seed→H stages→finalize for one real
  column from a genuine seed record, byte-matches `--kernel column` on the
  same input. Red-verified at the wiring layer (wrong keyLen on seed's
  output write corrupts the whole chain, caught immediately) — deep
  logic-correctness red-verification lives in 2.2's gate instead, since a
  genuine empty-seed sweep at this small scale doesn't reach the stranding
  edge case synthetic random states in `gate_kink_column.cpp` do.

### NEXT: 2.5 — Go orchestrator `Kernel` field threading
Per the plan file: `SweepConfig.Kernel string` (empty="column");
`Checkpoint.Kernel string` added to the struct and the
`config maxn=... kernel=%s` line in `orchestrator/checkpoint.go`, parsed in
`parseConfig`; `checkResumeConfig` (`orchestrator/sweep.go:104-129`) gets a
fail-closed guard (`resume.Kernel != cfg.Kernel`) alongside the existing
maxn/counter/fold checks, red-first tested the same way those are (grep for
their existing test, mirror it — likely `resume_test.go`). `MapArgs.Kernel`/
`MapArgs.Stage` threaded into `RunMapWorker`'s CLI arg assembly
(`orchestrator/worker.go`). `cmd/orchestrate/main.go`: `--kernel` flag,
default `column`, validated against `{"column","kink"}`, copied into
`SweepConfig`. Gate: Go unit tests only (checkpoint round-trip with `Kernel`
set + a resume-kernel-mismatch fail-closed test) — no real sweep yet.

**Then 2.6** (the big one): extend `mapPhase`/`mergePhase` with additive
keyLen/Stage-selector params, new `sweepHeightKink` function (parallel to
`sweepHeight`, not a modification — isolates risk since it's unreachable
except via the still-dark `--kernel kink` flag), `Run`/`runOverlap` gain a
one-line kernel dispatch. Gate: the cheap pre-check —
`orchestrator/kink_sweep_test.go` comparing `sweepHeightKink` vs
`sweepHeight` triangle rows at small (H,maxn) pairs (e.g. H=6/maxn=14,
H=10/maxn=20) against a real built `map_worker`/`merge_worker` — run this
BEFORE committing to the full a(20) gate (2.7/2.8 in the plan file).

Full sequencing 2.5 through 2.9 (incl. the a(20) gate requiring explicit
go-ahead before launch) is in the plan file; don't skip ahead of it.

## 2026-07-02 (night, earlier) — a(28) orchestrate on ayr EXITED rc=0

`ayr a28 orchestrate 1596596 EXITED at 2026-07-02T17:35:24-04:00`, wall
≈11724s (~3h15m), per the tmux waiter log. **Not yet combined/validated** —
that's `combine --maxn 28 --in runs/ns_a28/<box>/perheight` + the a1-27
prefix/growth checks per the standing recipe (see the a28 launch entry
below), and it's jasonp's call when to run it, not done automatically here.
dalby's a(29) run status was not rechecked this session.


## 2026-07-02 (later night) — Design 14 Phase 1 DONE: stage kernel ported to core/

Branch **`kink-carry`**, building on the Phase 0 tip below. a(28)[ayr]/a(29)[dalby]
still running untouched (see launch entry further down).

**Phase 1 (library only, ships dark) is done and gated green.** New
`core/kink.h`:
- `kinkStageTransition` — the per-record kink-carry stage fan-out (`occupy in
  {0,1}`, union-find over N/W/NW/SW, canonicalize, stranding check on the
  outgoing carry), extracted from `experiments/kink_tm/kink_tm.cpp`'s
  `kinkSweep`. The probe now calls this SAME function (refactor only, no
  logic change) so the probe and the port can never drift apart — re-ran the
  probe's own whole-column byte-match gate after the extraction (`kink_tm 8
  16`, `kink_tm 10 18`) and the numbers are unchanged from `results/kink-carry.md`.
- `map_shard_stage<W>` — adapts `kinkStageTransition` from single dense
  per-state count vectors to the production ranged `RunRecord<W>` window
  format (same lo/len shift-and-clip idea `core/mapreduce.h`'s `map_shard`
  uses for `forEachViableMask`). Consumes a shard of the *current stage's*
  mixed-state table (keyLen H+4: boundary + carry byte + touch/placed flags)
  and produces that shard's successor `Run<W>` for stage+1 — same
  `Run<W>`/`mergeRuns` contract as today.
- **Classifier / column-boundary harvest+seed+finalize (canonicalizeSig,
  completionLowerBound prune, foldSig, classify) are NOT in this function** —
  those are column-boundary concerns and are Phase 2 wiring, not built yet.

**Red-first gate:** `test/gate_kink.cpp` (`make ns-gate-kink`, now in both
`ns-gates` and `ns-gate-fast` — cheap, ~0.1s). For random synthetic
stage-table shards at H=4..10 (3 stage positions x 3 trials each): (1)
`map_shard_stage`'s ranged output matches ground truth (same records expanded
to dense per-n vectors, run through `kinkStageTransition` directly, no
windowing) and (2) shard invariance — splitting a table into shards, mapping
each independently, and merging via `mergeRuns` is byte-identical to running
the whole table at once (the actual Option A parallelism claim this whole
design rests on). Verified red: injecting a windowing bug (dropping the
lo-shift) fails the gate. A bug inside the *shared* `kinkStageTransition`
itself is correctly out of this gate's scope — that's `kink_tm`'s own
whole-column-vs-baseline gate's job (still green, see above).

Design doc (`docs/next-system/designs/14-kink-carry-parallel-engine.md`)
Phase 1 section updated to DONE with these specifics.

### NEXT: Phase 2 — wire `map_shard_stage` behind `--kernel kink`, gate at a(20)
Per the design doc: orchestrator column loop grows a stage sub-loop (H cycles
of partition-by-key → parallel `map_shard_stage` → merge → next stage), then
the existing end-of-column harvest/prune/fold (still needs building: the
column-start seed-from-column-table step and the end-of-column
drop-carry+stranding+canonicalize+prune+fold+classify step — neither exists
in `core/` yet, only the mid-column per-stage transition does).
`map_worker --kernel kink|column` (default column). Checkpoint granularity
becomes stage-level. Gate: full `a(20) --kernel kink --compare` byte-matches
both the b-file and a whole-column a(20) run. Do not skip ahead past this
gate before Phase 3 (dalby-scale validation, a24 byte-match).

## 2026-07-02 (night) — Design 14 (parallel kink-carry) Phase 0 fully de-risked; start Phase 1

Branch **`kink-carry`** (off master `b6dcfaf`, NOT pushed), tip `e3c330c`. a(28)
[ayr] + a(29) [dalby] still running untouched throughout — see the launch entry
below; do not touch them, only correctness/dead-box justifies it.

**The research-goal thread** (`/goal`: find a sub-exponential-base algorithmic
win) found one: **Kink Carry** — cell-at-a-time boundary sweep (literature-
standard TM, carrying the one king-adjacency NW cell the whole-column engine
was avoiding) instead of whole-column transfer. Serial win is real and
production-validated: `results/kink-carry.md` — 29x@H12, ~55x@H14 (measured),
extrapolated ~150-200x@H16, compute base ~4.4->~2.5/term. Gated byte-identical
against `results/ns_a27/perheight/h{12,14}.out`.

**Parallelization now fully resolved — Option A, GO on all three axes:**
- Option B (shard sources, private per-shard DP) — **NO-GO**: duplication
  grows ~S^0.7-0.8 unbounded, `results/kink-carry-shard-duplication.md`.
- Option A (shard *each stage*, H merge barriers/column instead of 1) —
  **GO on volume**: total data moved across all H barriers is already less
  than today's ONE barrier, gap widens with H (0.20x@H8 -> ~0.009x@H14
  extrap). No new code — reused `kinkSweep`'s existing `stageStateSum`
  counter. `results/kink-carry-optionA-volume.md`.
  - **GO on fixed overhead**: mined real dalby telemetry (`ns_a26`/`ns_a27`
    `cost_profile*.tsv` tail columns, frontier->0) for the fixed floor of a
    map+merge round-trip: ~6-30ms. `H x that` < 1s/column, negligible vs the
    100-300x volume win and hour-scale peak-column walls. No wired engine
    needed to get this number. `results/kink-carry-optionA-barrier-overhead.md`.

**Design doc updated and current:** `docs/next-system/designs/14-kink-carry-parallel-engine.md`,
status **"OPTION A CHOSEN"**. Phase 0 (0.1/0.1b/0.1c) all DONE. Phase 1/2 text
already rewritten for Option A's actual shape: the column loop gains an
inner stage sub-loop (H sequential stage-map-then-merge cycles instead of 1
map-then-merge), barrier = stage boundary not column boundary. Read that doc's
Phase 1 section before writing code — it has the concrete plan (port the
single-stage fan-out into `map_shard_stage<W,Classifier>`, keyed on the mixed
boundary+carry+touch-flags state, same `Run<W>`/`mergeRuns` contract, v1 scope
= triangle only, holes stays on the column kernel — `sig.b[H+2]` conflicts
with the carry byte).

### NEXT: Phase 1 — port the stage kernel into `core/` (library only, ships dark)
Per the design doc: `map_shard_stage<W, Classifier>` in `core/`, consuming a
shard of the current stage's mixed-state table, producing that shard's
successor records as a sorted `Run`. Red-first tests at H=4..10: byte-identical
to the unsharded `kinkSweep` stage transition on random stage-table shards.
Orchestrator still calls the old column path — this phase does not touch a(n)
production runs. `experiments/kink_tm/kink_tm.cpp` is the reference
implementation to port from (the serial `kinkSweep` stage-transition body).
Do not skip ahead to Phase 2 wiring before Phase 1's own byte-match gate is
green. Consider whether to merge `kink-carry` back to `next-system`/`master`
before or after Phase 1 lands (not yet decided).

## 2026-07-02 (evening) — a(28) + a(29) LAUNCHED (concurrent, one term per box) 🚀

Both deployed at rev **`7e28071`** (next-system; P9..P12 wired + simplify cleanup),
rebuilt **WITH zstd spill compression** (POLY_ZSTD on both boxes; ayr libzstd-dev
now present). a18 `--compare` PASS on both before launch.

- **ayr — a(28)** ≈ 4.8e21 (FIRST SEXTILLION): `scripts/ayr_a28.sh`, solo, maxn=28,
  top real height **H15** (a26-tier). orchestrate PID **1596596**, tmux `0:a28`,
  waiter `bpbb4nhsu` (tail --pid). 32c, u128, 1GiB/worker (32GiB cap, fits 78),
  overlap 13, ckpt 300s. Est ~3h.
- **dalby — a(29)** ≈ 3.3e22: `scripts/dalby_a29.sh`, solo, maxn=29, top real
  height **H16** (a27-tier). orchestrate PID **2243059**, tmux `0:a29`, waiter
  `bpgekpfwf`. 80c, u128, 1GiB/worker (~80GiB cap, fits 125; measured 38G used
  early), overlap 14, ckpt 300s. Est ~4-5h.
- **Deploy note:** dalby fetches github over **https** (git@ publickey fails);
  ayr fetches over **git@ ssh** (https prompts for creds). Don't cross them.
- **On completion (each):** `build/ns/combine --maxn N --in runs/ns_aN/<box>/perheight`
  → a(N); validate a1-20 vs b-file (combine --compare auto) + a21-27 vs
  results/ns_a2{1..7}/ by hand + monotone-growth guard + growth ~6.86. Record
  results/ns_a2{8,9}/, tier computed (single-source high heights, cert pending).
- **Byproducts:** a28 gives T(28,16) (diagonal-12, n=28) and a29 gives T(29,16/17)
  → diagonal-12 point at n=28,29 + diagonal-13 points → enough to validate **P_13**
  (needs diag-13 at n>=27; a27 gave n=27, a28/a29 give n=28,29 → 3 pts).

**RESEARCH THREAD (while they run):** eke more from the engine / investigate new
approaches. Reach base-reduction is closed (45° diagonal FALSIFIED, [[column-tm-already-sqrt-lambda]]);
open levers to weigh: #12 u64-per-state (halves RAM/spill; top un-banked lever),
and any fresh angle. (Ranged rows are ALREADY the shipped ns record format —
core/run.h `[sig|lo:u8|len:u8|counts]` — the ~1.9x is banked, don't re-chase.)

## 2026-07-02 (later) — P_11 CLOSED → a(28) unblocked ✅

Commit `2ddd474` on next-system. **The a(28) coding blocker (task #13) is done.**

- **P_11(n) fully derived + validated** (`scripts/derive_p11.py`, analog of
  derive_p9/p10). The validated P_9+P_10 fits pin the shared series symbols
  {a7..a10,b8..b10} exactly → **10 of 12 P_11 coeffs clean from theory**; only
  a11,b11 needed data, from the 2 new sweeps T(26,15)+T(27,16). **Held-out a25
  diagonal-11 points n=23,24,25 all matched**; leading coeff 25^11/11! confirmed.
- **Wired:** `orchestrator/sweep.go` diagCoeffTable **case 11** + guard
  `diagonalStripValid` extended to **k<=11** (maxn>=2*11+1=23). Keeps a28 top
  real height at **H=maxn-11 (cheap same-tier)**.
- **Red-first tests:** `orchestrator/diag_p11_test.go` (pins diagonalCell(n,11)
  on all 5 real pts, 3 held out; drives contributeDiagonalStrip k=11 at maxn=28;
  guard at 22/23/28) + `diagthreshold_test.go` updated (k=11 valid, k=12 new
  boundary). Both panic pre-wiring (verified). ns-gate-fast + closedform green.
- **Note:** the classic "a20 --compare byte-match" step is moot for this change —
  at maxn=20 the k=11 strip is below its 2k+1=23 threshold and never dispatches,
  so a20 output is byte-identical by construction. The maxn=28 strip-contribution
  integration test covers the path a20 can't reach.

### IMMEDIATE NEXT (gated on jasonp's go): launch a(28) — first sextillion
Same recipe as the "THEN: launch a28" block below (now unblocked). Before launch:
sync dalby+ayr to next-system `2ddd474`, **rebuild WITH compression** (both boxes
have libzstd-dev), dalby+ayr split like a27, u128, rebalance from a27 cost
profile. a28 ≈ 4.8e21. Requires explicit assent (a(n)-push launch rule).

## 2026-07-02 (late) — SESSION SAVE-STATE (before Claude Code binary update)

**No live jobs. dalby + ayr both FREE.** a(26) and a(27) both landed this session.

### Frontier state
- **a(26) = 102607513847014153892** — landed, `results/ns_a26/`. T(26,15)=5614506356004078534.
- **a(27) = 703126792093436034256** — landed, `results/ns_a27/`. dalby+ayr split (H16
  3.76h / H3-15 2.7h), rev `b390518`, u128, guarded combine. growth 6.8526.
  **T(27,16) = 27798973373501478242.**
- Both P11 equations now in hand (T(26,15) + T(27,16)).

### IMMEDIATE NEXT (task #13, in_progress): close P11 → unlock a28
1. `scripts/derive_p11_sizing.py` — solve P11 fully (7/12 coeffs from theory + the
   2 new points). Held-out validate.
2. Wire `orchestrator/sweep.go` `diagonalCell` **case 11**; extend `diagonalStripValid`
   guard to **k<=11**. Red-first test (heightnm2 style) + a20 --compare byte-match.
3. Closing P11 keeps a28 top-real-height at **H16 (cheap same-tier)** not H17 (new ~3x
   tier). a28 ≈ 4.8e21 = **first sextillion** term.

### THEN: launch a28 (next term)
- Sync dalby+ayr to latest next-system (`b14e0b1` + P11 commit), **rebuild WITH
  compression** — BOTH boxes now have libzstd-dev (ayr installed 2026-07-02). Makefile
  auto-detects zstd → POLY_ZSTD on both. Default spill level 3 (26x).
- a28 dalby+ayr split like a27 (dalby H16 + closed-forms, ayr H3-15). Rebalance
  from a27 cost profile. u128. Standing user auth covers a(n)≤a30 launches.

### Engine changes THIS SESSION (on next-system, pushed origin `b14e0b1`) — NOT yet on dalby/ayr
- **Single-spill fast-path** (core/mapreduce.h) — skip self-merge when a column fits RAM. Validated a20 byte-identical. ~2%.
- **combine monotone-growth guard** (orchestrator/cmd/combine) — fail-closed on a(n)<=a(n-1); caught the a26 stale-u64 near-miss. Red-first test.
- **zstd spill compression** (POLY_ZSTD, core/runfile.h, spill files only) — 26x@zstd-3, validated byte-identical incl resume + many-blocks. `ns-gate-spill-zstd`.
- **Clean-room verifier** (experiments/cleanroom/cleanroom_verify.cpp) — independent DSU transfer-matrix, matches triangle to n<=14. 2nd independent kernel check.
- dalby worktree ~`fd578de` (guarded combine built); ayr ~`b390518`. Both need sync+rebuild for a28.

### Queued levers (measured, not yet built)
- **#12 u64-per-state records** (u128 row accumulator) — MEASURED per-state max 40 bits at a27 → halve RAM/spill, spill less, raise --ram. After compression deploys. Sequence after #13 (shares mapreduce.h/classifier.h). SAFETY: per-state u64 not provably overflow-free at a30 (aggregate grows); combine() fail-loud guard aborts-not-corrupts; re-measure a29 per-state max before a30.

### Measured DEAD-ENDS this session (don't re-attempt — see results/ + memories)
- 2D-holonomic accelerator: NONE (results/boundary-push-recurrence.md).
- Tensor-network frontier compression: chi^2~frontier, MPS loses (results/boundary-push-tensornetwork.md).
- Map arena allocator: counts.assign 2/3405 samples, negligible (results/map-body-profile.md).
- viableRec: ~20% branch-mispredict INTRINSIC, cache fine (2.6% L1), const fine, PGO no-go on dalby, context-struct arg-pack measured NEUTRAL/-0.15% ([[pgo-no-go-dalby]]).
- Cloud burst: DECIDED no ([[no-cloud-burst]]).
- Completion-pruning (#4): headroom exists (79% multi-comp) but high-risk, oracle-gated, deferred.

### New memories this session
no-cloud-burst, ask-for-missing-libs, no-root-without-asking (HARD: no sudo on ayr w/o asking), pgo-no-go-dalby. Updated a24-a25-state (now a24-a27).

---

## 2026-06-29 — earlier

## 2026-07-02 — a(26) LANDED + a(27) split LAUNCHED 🚀

**a(26) = 102607513847014153892** (new term). dalby-solo, ~68min, u128, rev
`246cb09`. Validated: a1-20 = b-file, a21-25 = certified, growth 6.8429. Recorded
`results/ns_a26/` + PROVENANCE. T(26,15)=5614506356004078534 → closes one P11 eqn.
NEAR-MISS: stale u64 combine binary wrapped the first a(26) (caught by
growth check); rebuilt combine → correct. See task #9 (guard) + PROVENANCE.

**a(27) split RUNNING** (rev `b390518`, both machines clean tree, all binaries
incl. combine rebuilt):
- **dalby**: H16 + closed-forms H1,2,17-27. orchestrate PID **2215524**, tmux
  `0:a27`, waiter `brd3728nl`. (orchestrate baked rev shows "unknown" — built
  without -ldflags gitRev; workers correctly stamped b390518, tree clean, so
  provenance holds. Minor; not worth restarting.)
- **ayr**: swept tail H3-15. PID **1523246**, tmux `0:a27`, waiter `bq1cp0wn9`.
- Est ~3.4h wall (ayr-bound H3-15; dalby H16 ~2.8h). Cost check confirmed the
  staged split is optimal (moving H15 to dalby is worse).
- **On completion:** `combine_a27.sh` on dalby (rsyncs ayr rows, --require-cover).
  Uses FRESH combine. Validate a1-26 prefix + growth ~6.84.

---

## 2026-07-02 — a(27) dalby+ayr split STAGED (not launched)

Scripts `scripts/{dalby,ayr,combine}_a27.sh` (rev incl. `9892168`), pushed +
pre-synced to ayr. **ayr prepped**: built native at `246cb09` via `$HOME/go/bin`
go1.26 (the cross-compile memory was wrong — corrected); smoke-tested a1–18 =
b-file at both u64 **and** u128.
- Split: **dalby** H16 (68% of cost) + all closed-form heights (H1,2,17–27);
  **ayr** swept tail H3–15. Est ~4h wall (vs ~5h dalby-solo). u128.
- **Before launch:** rebalance the height split against a26's real
  `cost_profile.tsv` (a26 sweeps H1–15 @ maxn26 → near-exact H3–15 costs);
  move H14/H15 dalby↔ayr if the halves are unbalanced. Then combine on dalby
  via `combine_a27.sh` (rsyncs ayr rows, `--require-cover` H1..27).
- a27 needs only P9/P10 (already wired); P11 not required until a28.

## 2026-07-02 ~07:37 EDT — a(26) frontier run LAUNCHED (dalby-solo) 🚀

Rev **`246cb09`** (clean, native build on dalby `~/src/polyominoes-ns`).
First term of the docs/a26-a30-diagonal-plan.md push. `scripts/dalby_a26.sh`.

- **dalby**: orchestrate PID **2086881**, tmux `0:a26`, waiter `bbxvuyztq`
  (tail --pid). `--maxn 26 --counter u128 --overlap-heights 14 --cores 80
  --unit-mult 4 --steal-grain 0.05 --ram 1GiB/worker`.
- **Shape:** real sweep H1–15 (top real H=15); closed-form inject H16–24
  (k=2..10 diagonals, P9/P10 now wired) + pole H25 + top H26. First run on
  the widened big.Int result pipeline + u128 counter (a25 was the u64 ceiling).
- **Predicted cost:** ~303K cpu-s, ~1.1h wall @ 80 cores (plan cost table).
- **Byproduct:** real T(26,15) → closes one of P11's 2 missing equations.
- **On completion:** validate a1–20 vs b-file prefix, a21–25 vs
  results/ns_a2{1..5}/RESULT.md; record a(26) + perheight in results/ns_a26/.
  Tier: computed, pending certification (high heights single-source).



## 2026-06-29 ~13:57 EDT — a(23) frontier run LAUNCHED (dalby + ayr split) 🚀

Rev **`6db27b5`** (clean, native build both hosts; ayr got Go 1.26 in `$HOME/go`).
Disjoint height-split, combine on completion. a(21)/a(22) are free byproducts.

- **dalby**: heights **17–23**, 80c, PID **1458809**, tmux `0:a23`, waiter
  `bo0e6di6b`. Sweeps H=17,18 (the cost); injects H=19–23 (k≤4 diagonals).
  `~/src/polyominoes-ns/runs/ns_a23`, log `runs/ns_a23/dalby.log`.
- **ayr**: heights **1–16**, 30c, PID **1396930**, tmux `0:a23`, waiter
  `beu50rd3c`. Cheap bulk; flew to H=10 in 13 s. `runs/ns_a23`, `ayr.log`.
- **Split rationale:** with k≤4 injection the cost concentrates in the tall swept
  heights (H=18 ≈44%, H=17 ≈26%, halving below). dalby (80c) takes the two
  monsters + free injected; ayr (30c) takes 1–16 → wall ≈ max(hosts), dalby
  (H=18) the critical path.
- **Config:** u64, unit-mult 4, **steal-grain 0.05**, ram 1 GB/worker (spills to
  disk beyond). Disk free: dalby 346 GB, ayr 396 GB.
- **Calibration:** clean a(20) = **2h25m** on dalby (PASS, byte-validated). a(23)
  est. multi-day.
- **On completion:** `rsync` both `perheight/` → one dir →
  `combine --require-cover --compare` (byte-checks a(1..21) prefix; a(22),a(23)
  are new). Tier: **computed, pending certification** — high heights single-source.

## 2026-06-29 — audit campaign DONE + process changes + dalby straggler note

### Audit actioned (supersedes the "not yet actioned" section below)
`BUGS-OF-SHAME.md` → **`AUDIT-2026-06-28.md`** (renamed `3e27f68`), with a per-item
disposition table (commit hash next to each fix). Worked the whole audit on
`next-system`: **20 fix commits, each test-first with the failing test captured
in the commit log**, plus the rename and 3 process commits. WS (T2.3) and A1 are
now committed (`b8b448b`, `2d782e2`) — supersedes "Uncommitted work … NOT
committed" below.
- **FIXED:** A1, A3, A5, A7, B1, B2, B4, B6, B7, B8, C2, D1, D2, D5, D6, Lenient
  Cat, Fail-Open Counter, Silent Truncator (+ A2 refuse-at-start guard, B3
  verify-tool contract).
- **DEFERRED (recorded in the doc):** A4+D7 (holes through the orchestrator), C1
  (fitted T(n,n−1) — until derived/validated), A2 big.Int widening (a26+), A6
  (mod-p producer). **SKIPPED:** Wrong Room, B9.
- Plus a tail-end finale: clangd LSP false positives killed (`6b3bd7a`) — see
  `compile_commands.json` generator + `.clangd`.

### Process changes (catch regressions fast)
- **Pre-push fast gate:** `make install-hooks` → `core.hooksPath=.githooks` → runs
  `make ns-gate-fast` (~16s, measured). No GitHub Actions.
- **`make ns-gate-closedform`** — invariant gate asserting known closed forms are
  contributed directly, never enumerated (the tripwire the H=maxn incident lacked).
- **`docs/engineering-standards.md`** — fail-closed defaults + red-first fixes.
- **`docs/job-checklist.md` item 4** — explicit gate: deployed binary's `GIT_REV`
  is clean AND contains the change you intend (the A1 provenance lesson).

### dalby a(21) — COMPLETED 2026-06-29T07:29:44-04:00 ✅
**a(21) = 6,954,084,405,510,437** (new frontier term). orchestrate 993738 exited
clean (status 0) after ~35.8 h wall; all three waiters fired (`bejohjmiv` stale,
`bw113qsu5`, and this session's `b5c4r8lw5`). Recorded in **`results/ns_a21/`**
(triangle.txt + perheight h1–21 + PROVENANCE.md).
- **Validated:** a(1)–a(19) match the A006770 b-file exactly; a(20) matches the
  prior validated run; growth a21/a20 = 6.78068; **h1–h17 byte-identical between
  dalby and ayr** (sha256, independent runs).
- **NOT yet independently certified:** the novel high heights **h18–h21 are
  single-source** (dalby only; ayr salvage stops at h17). Needs the mod-p shadow
  (A6, deferred) or an independent reimplementation before OEIS-final. Per
  validate-before-record, a(21) is **our computed value, certification pending**.
- Note: this ran on the UNFIXED `35eb9e1` (brute-forced the H21 closed form → the
  long straggler tail). A re-run on a current binary (A1 + work-stealing) would be
  far cheaper but isn't needed for the value. **Publishing is jasonp's call.**

---

# HANDOFF — 2026-06-28 (late evening)

## 2026-06-28 ~23:00 — LIVE STATE: jobs + operational concerns

### Running jobs (measured)

- **dalby — a(21), new engine, rev `35eb9e1` (UNFIXED).** orchestrate PID
  **993738**, **1d 03h20m** in, on **H21 col2** (the pole; col2 ≈ the costliest
  column of the run), elapsed_s≈27600 (~7.7h into col2), `processed` near-flat at
  9.08B (merge/tail of col2), RAM 3 GB used / 121 GB avail, disk 342 GB free.
  Healthy. **DO NOT RESTART** (correctness-or-dead-box only; it's deep into the
  pole). After col2 the frontier collapses ×0.42/col and cols 3–20 finish fast,
  then the run is done. Completion waiter: **`bw113qsu5`** = `tail --pid 993738`
  on dalby (supersedes any stale pre-compaction `bejohjmiv`). NOTE: this run
  still brute-forces H21 (= 3^20 closed form) — see BUGS-OF-SHAME A1; we are NOT
  touching it.
  - Post-run: `combine --in runs/ns_a21/perheight --maxn 21` → a(21); cross-check
    vs ayr salvaged h1–16/h17; growth gate a21/a20 ≈ 6.78.

- **ayr — work-stealing A/B benchmark (a(17), unit-mult=1).** `scripts/ns_steal_ab.sh
  17 8 1 128 0.05`, script PID **1377714**, tmux `0:steal`, ~1h in; OFF phase
  done, ON phase running (~H15). Completion waiter: **`b4lj97lo3`** = `tail --pid
  1377714` on ayr — will fire with the mult=1 headline. (The earlier mult=4 A/B
  finished: byte-identical both ways, but only **0.3%** map-wall recovered —
  stealing is defeated by high unit-mult; this mult=1 rerun tests the low-mult
  regime where stealing should engage continuously. See BUGS-OF-SHAME D2.)

- **gympie — idle** (local dev box). 10-perf-core cap.

### Waiter inventory (only these two; no pollers)
- `bw113qsu5` → dalby a(21) orchestrate 993738 (tail --pid).
- `b4lj97lo3` → ayr A/B script 1377714 (tail --pid).
- Killed this session: an orphaned ayr `until grep` poll loop (PID 1380036) that
  survived a `TaskStop` as a remote orphan — violated the no-polling directive.

### Uncommitted work on gympie (next-system, HEAD `952b111`) — NOT committed
Working tree (8 modified + 3 untracked); this is real, gated work sitting uncommitted:
- **Top-height closed-form fix** (`orchestrator/sweep.go`: `contributeTopHeight`/
  `topHeightClosedForm` + `mapPhase` guard; `orchestrator/topheight_test.go`):
  H==maxn now injects T(n,n)=3^(n-1) with NO map/merge. Gates green
  (ns-gate-parallel a14 closed-form PASS, full orchestrator suite ok). This is
  BUGS-OF-SHAME **A1** — uncommitted; the running dalby binary lacks it.
- **Work-stealing (T2.3)** across `core/mapreduce.h`, `worker/map_worker.cpp`
  (clean SIGTERM stop-at-cursor + `seekToKey`), `orchestrator/{worker,accounting,
  runref,sweep,telemetry}.go`, CLI `--steal-grain`. Correctness PROVEN
  result-invariant (a17 11 steals byte-identical; a16 rebuilt byte-identical; all
  byte-identity + resume gates pass with steal off). Measured win is config-
  dependent (≈0 at unit-mult=4; mult=1 rerun in flight on ayr).
- **`scripts/ns_steal_ab.sh`** (A/B harness), **`BUGS-OF-SHAME.md`** (the audit).

### Top operational concern: BUGS-OF-SHAME.md (audit, not yet actioned)
Full audit at repo root. Highest-priority items, in fix order:
1. **A1** commit the top-height fix (it exists only in the working tree).
2. **A2/A3** silent wrong answers: `--counter u128` truncates to u64 in the Go
   result pipeline; the FR-7 counter-overflow "refuse at start" guard is
   documented in `core/counter.h` but unimplemented.
3. **A4** holes are unreachable through the orchestrator (lost capability vs old
   `build/tma_holes`); keyLen hardcoded H+2, no `--holes` in MapArgs/merge_worker.
4. **A5** `combine` has no integrity guard (the old `gate-driver` bug class);
   **B1** resume trusts CLI flags over the checkpoint; **B2** `--require-cover`
   defaults false.
5. **D1** designs 07/09 cost model is anchored on H=N being ~55% — but H=N is now
   the free closed form; re-derive with H=N removed (real pole is H=N−1), which
   unlocks **C1** the T(n,n−1)=(25n−45)·3^(n−4) closed form (~24% of wall, fit not
   yet derived — validate before a record run).

### dalby stale ayr deploy note
ayr's `~/src/polyominoes-ns` worktree has the uncommitted sources rsync'd in
(for the A/B) + a cross-compiled `orchestrate` (rev label `952b111-steal`); its
git HEAD is older. This is benchmark-only; reconcile when committing.

## 2026-06-28 PM — a(20) PASSED + an engine-architecture analysis session

**a(20) seek-index validation PASSED** (waiter `bdey8w0ly` fired): new engine ==
old a(20) = **1,025,573,519,362,016** byte-identical. The seek-index merge fix is
**validated at scale** (multi-GB files, >2GB seeks) — the gate before trusting the
engine for records. Stats harvested to `results/ns_a20/` (16.5h wall, 73% util,
merge 2.9% of wall, costliest H20c2=19,800s). a(20) `--per-height-out` also yields
the full T(n,H)≤20 triangle (fills the #31 notch — verify when convenient).

**dalby a(21)** (PID 993738, unfixed engine) is on **H21 — the pole, last height**.
Per-column cost is front-loaded: a few heavy columns (col2≈the costliest of the run,
~9h on the unfixed engine) then the frontier collapses ×0.42/col and the last ~15
columns finish in minutes. **Do NOT restart** (the fix would save nothing this late;
it's near done). Waiter `bejohjmiv` armed. Live straggler tails on H21 peak columns
are expected (1 of 80 workers grinding) — not a hang.

**Analysis output this session (committed; no engine code changed, live runs
untouched): designs/07–10 + tooling.** Conclusions now in memory
[[engine-utilization-and-scheduling]] and [[merge-shuffle-ranking-locality]]:
- **#32 height scheduling (07):** LPT/dynamic-pull beat meet-in-the-middle (which is
  47% bad); `scripts/heightsplit_plan.py`.
- **Straggler tail (08):** the real utilization lever (~18% map-wall, grows); fix =
  **work-stealing T2.3**, NOT LPT unit-ordering nor finer `--unit-mult` (both
  measured-rejected). Tools: `POLY_UNIT_LOG`, `scripts/{unit_cost_analysis,sched_sim}.py`.
- **Cost model (09):** frontier collapses ×0.42/col past peak; cost front-loaded in
  cols 0–4; `active_width+H≈N+6` empirical, mechanism OPEN (king-diagonal refuted the
  cell-budget story).
- **Shuffle/ranking/locality (10):** the merge all-to-all is conserved; a DENSE RGS
  ranking EXISTS → hash-resident shuffle-free frontier viable through ~a21 (=#20 RAM
  wall); a LOCAL/banded ranking cannot (expansion) → don't chase a partition-preserving
  encoding. Papers saved to `papers/` (MapReduce + twisted-cylinders).

## 2026-06-28 10:10 — live status (measured; two jobs running, both healthy)

**ayr — a(20) seek-index validation** (orchestrate PID 1276058, log
`~/src/polyominoes-ns/runs/ns_a20/a20.log` — note: under the `-ns` worktree, NOT
`~/src/polyominoes`): **on the final height H20**, H1-19 all done, ~11h51m in.
H20 col0+col1 done (col1=2255s), now in **H20 col2 (the peak column)**, ~2h45m
in, map phase plateaued (processed flat at 896M → in/near merge). Cost model: col2
is the most expensive column of the run; columns 3..20 taper after it. So the
`--compare` verdict (must byte-match **a(20)=1,025,573,519,362,016**) is **a few
hours out** — col2 nearly done, then the tapering tail. Not hard-pinned (no ETA
in the log; this is the last, costliest strip). Waiter `bdey8w0ly` armed.
**This is the gate before any a(21) restart-with-fix decision.**

**dalby — a(21)** (orchestrate PID 993738, rev 35eb9e1 = UNFIXED engine, tmux
`0:a21`, launch pane 993720 alive): **on H20 col 3/21**, ~14h22m in, RAM 79GB,
healthy. H20 col2 (peak, unfixed engine) took **16451s = 4.6h** (map-bound:
map=15844s merge=607s — confirms tall heights are MAP-bound even unfixed). Tail
remaining: H20 cols 3-20 taper, then the **entire H21** (tallest strip, frontier
~2× H20 → its peak column alone ~9h). So **~15-25h more, UNMEASURED** — no hard
ETA. RAM-safety watcher 1122969 assumed alive (triggers >108GB). Waiter
`bejohjmiv` armed (watches orchestrate PID 993738 directly).

**Waiter hygiene (2026-06-28):** had **6 background shells**; pruned to the **2
required** (one correct completion-waiter per box: `bdey8w0ly`→ayr/1276058,
`bejohjmiv`→dalby/993738). Killed redundants: `bn2by19hw` (duplicate ayr waiter,
wrong log path) and `bgeacm4js` (dalby waiter on the launch pane 993720 not the
orchestrate); the old probe/iostat monitors had already exited.

**Stats harvest setup (commit `a393e53`):** per-column telemetry now logs
`map_units`/`merge_ranges` (worker-invocation fan counts); `scripts/job_stats.py`
rolls any run log up to per-column/-height/-job **wall, cpu-s, eff_cores, util%,
peak RSS, map-vs-merge split, costliest columns**. ON EACH JOB'S EXIT: scp the
final log, `python3 scripts/job_stats.py <log> --tsv results/<job>.tsv`, save the
rollup into `results/`, commit. Caveat: both CURRENT logs predate the fan-count
fields → `map_units`/`merge_ranges` render `-` for these two runs; every run from
here carries them. Cost-model note recorded in memory
`column-compute-cost-vs-count` (compute cost = frontier size, NOT polyplet count;
top strip is costliest yet adds fewest — "never call the top height trivial").

**Landed this session (next-system):** seek-index merge fix `de4e183` (~16.7x on
real mergeRunFiles; merge CPU 22-34c→<1.5c; a(20) telemetry confirms map fills
~27/30 but merge now LATENCY-bound, idling box 24-45% of wall) → next lever is
cross-height **overlap** `c619107` (`--overlap-heights K`, K=1=sequential
unchanged; validated correct + race-clean; hides merge idle behind another
height's map). `experiments/merge_{read,strategy,engine}_bench.cpp`,
`docs/next-system/designs/06`.

**DECISION PENDING on a(20) verdict:**
- a(20) `--compare` **PASS** → seek-index earned the record. a(21) is only hours
  in → cross-compile c619107 orchestrate on gympie + ship to ayr-style, **restart
  a(21) on dalby with the fix** (~3x faster on a validated engine). Bring to
  jasonp first.
- a(20) **FAIL/mismatch** → seek-index has a scale bug → do NOT touch a(21);
  debug the seek path.

**Also ready (deferred to after a(20)):** overlap re-test on ayr via
`scripts/ns_overlap_ayr.sh 4` (needs c619107 cross-compiled+shipped first) to
measure the utilization win vs the sequential a(20). ayr old-engine H18
cross-check was killed (a(21) old-engine cross-check caps at H1-17, ample).

## 2026-06-27 ~22:11 — seek-index merge fix + a(20) validation on ayr

**The merge bottleneck is fixed in code.** `mergeRunFiles` re-read ~M/2× the
frontier (skip-to-klo from the start of every input; measured 160× at mult=4 —
the in-memory amplification that capped merge at ~22-34 cores while map hit
55-66; confirmed by dalby's live capture: disk idle `r/s=0` at the middle
heights, so membw-bound, not I/O). Fix = sparse `key→offset` `.idx` sidecar +
`RunFileReader::seekToKey` + `mergeRunFiles` seeks to klo. **16.7× on the real
`mergeRunFiles`** (A/B, `experiments/merge_engine_bench.cpp`); profiling confirms
the old hotspot was `__pop_heap`/`__sift_up`/`next`/`fread` (the discarded
prefix). Result-invariant: parallel/spill/holes/resume gates all PASS
byte-identical. Commit `de4e183`; alternatives (bucketed shuffle = cloud
shuffle; hierarchical merge) in `docs/next-system/designs/06`.

**RUNNING — a(20) at-scale validation on ayr** (x86): `scripts/ns_a20_ayr.sh`,
tmux `0:a20`, orchestrate **PID 1276058** rev `aebdd82`, cores=30 mult=4,
`--compare` (must byte-match a(20)=1,025,573,519,362,016) + per-height-out, ckpt
900s, log `runs/ns_a20/a20.log`. Waiter armed. Predicted ~15-20 h (→ ~2026-06-28
PM). Purpose: prove the seek-index correct at a(20) scale (multi-GB files, >2GB
`fseek`) — which the a14-a17 gates can't reach — **before** it's trusted for the
a(21) record. Bonus: cross-ISA (x86 vs dalby arm) + x86 re-benchmark.
- ayr setup: old-engine H18 cross-check **killed** (was col 3/21, weeks out;
  a(21) old-engine cross-check now caps at H1-17 — 17 independent rows, ample).
  ayr's system Go (1.19.8) too old → orchestrate **cross-compiled on gympie**
  (CGO_ENABLED=0 linux/amd64, static) + workers built native; a(13) smoke PASS.
- **Plan:** if a(20) byte-matches, the fix has earned the record → **restart a(21)
  on dalby with the fix** (a(21) is only hours in; ~3× faster on a validated
  engine). If a(20) mismatches, the fix has a scale bug — do NOT touch a(21).

## 2026-06-27 ~18:00 — a(21) LAUNCHED (new engine, single-instance, dalby)

**Running:** `scripts/ns_a21.sh 4 runs/ns_probe/n18_m4/profile.tsv 80 1 6.76` in dalby
tmux `0:a21`, pane 993720, log `runs/ns_a21_launch.log`, run dir `runs/ns_a21/`.
Config: maxn=21, cores=80, **unit-mult=4**, ram=1 GB/worker, per-height-out,
checkpoint 900s, cost-profile-ref scaled from a(18). rev `35eb9e1`.
A-priori ETA **7.4 d (eta 2026-07-05)** — conservative (a18-basis); likely faster.

- **WATCH (the scale unknown): disk/spill volume.** No predictor estimate; 346 GB
  free on /. RAM should stay ~80 GB (spill-bounded by the 1 GB/worker budget) — the
  predictor's "232 GB peak RSS" is an artifact (it scales per-worker RSS ignoring
  spill). Stress peaks at the middle heights (~day 2-3). If disk→full or RAM→125 GB:
  SIGTERM the orchestrate (checkpoints), retune (lower --ram or --cores), `--resume`.
- **No `--compare` on the run** (a21 not in fixtures → would FAIL at n=21).
- **Post-run validation:** `combine --in runs/ns_a21/perheight --maxn 21` → a(21);
  then `combine --maxn 20 --compare` (n≤20 vs fixtures) + `ns_crosscheck.sh` vs the
  old engine's salvaged h1..h16 (and ayr's h17, done) + growth gate (a21/a20 ≈ 6.78).

### Utilization exploration findings (a(18), why single-instance)
- Map scales with mult (48-72 cores, NOT bandwidth-bound); **merge structurally
  under-utilizes (~34 cores)** — fan-in I/O + load imbalance. Within-height tuning
  (unit-mult, merge-mult) caps ~35.
- Cross-height overlap (batch model) helps: 2×80 **oversubscribed = 52 cores / 32%
  faster** — but **bounded by RAM/spill**, not CPU (3×/niced-crew collapsed to 26 on
  a spill-I/O storm; nice/cgroups arbitrate but don't create I/O capacity).
- **At a(21) (300× frontiers) spill dominates** → a18 overstates achievable a21
  utilization; oversubscription would amplify spill. Hence single-instance with
  generous RAM. a(21) itself is the definitive spill-at-scale measurement that
  decides the a(22)/a(23) answer: **shared-pool scheduler** (one process, shared RAM,
  controlled in-flight heights, sequential-friendly merge) vs cgroups-niced-crew stopgap.
- New flags this session: `--merge-mult` (decouple merge ranges), map/merge phase-split
  telemetry, `scripts/ns_multi.sh` (multi-instance harness w/ nice). All committed.

## 2026-06-27 PM — cut dalby over to the new engine

Decision (jasonp): stop the old-engine a(21) on **dalby** and run a(21) on the new
engine instead; old campaign was ~4–6 weeks (dalby H20→H19 serialized + ayr H18).

- **dalby**: old H20 + driver + all waiters/telemetry KILLED; box idle (verified
  RAM 78→1 GB). The new-engine a(21) will run here once the probe passes.
- **ayr**: UNTOUCHED — H17/H18 keep running as the independent old-engine
  cross-check (extends per-cell agreement through H18; H1–16 already saved).
- **Salvaged**: `runs/a21fold/h1..h16.out` on ayr = full per-cell T(n,H) for H≤16
  (verified Σ T(21,H1–16) = a21.partial = 6,937,832,928,078,101). ~99.8% of a(21)'s
  mass, per-cell. Only H19/H20 frontier cells will rest on the new engine alone.

### New-engine work this session (next-system, all committed, gates green)

- `--unit-mult` (decouple units from cores; semaphore stays = cores).
- Per-column cost telemetry + cost profile + live calibrated ETA (`--cost-profile-ref`).
- Within-column heartbeat (worker pulse + orchestrator ticker; cadence = √checkpoint).
- A-priori predictor (`build/ns/predict`): scales a profile to target n; validated
  by predicting a(20) from a(19).
- Multi-machine height-split (`--heights`, `--per-height-out`, `build/ns/combine`,
  `scripts/ns_heightsplit.sh`) — Phase B, for a(22)/a(23); `ns-gate-split` PASS.
- Fixtures extended with a(19)=151609203011580, a(20)=1025573519362016.

### Next: probe then gated a(21) launch

- `scripts/ns_probe.sh` (dalby): a(19) at unit-mult 1/4/8 → pick fastest, then a(20)
  at best mult with predicted reference profile. Validates core utilization,
  per-term R, predictor error, and correctness (--compare on known a19/a20).
- **a(21) launch gate**: a19 AND a20 --compare PASS, predictor within tolerance,
  projected wall ≲36h, fits 125 GB, telemetry live. Else hold.
- Need to push next-system to origin + build on dalby before the probe.

---

## What's running (pre-cutover snapshot — dalby section now stale)

### Old engine a(21) — split ayr + dalby, weeks from done

Both machines are early in their sweeps. `c=N/21` in the process title is the
**column index** (0–21), and the `~N%` is **within-column shard progress**, not
overall-height progress. Column cost grows ~4× per column, so being at col 3–5
means the vast majority of the work is still ahead.

- **dalby** (80c Neoverse N1): **H20** pid 30478, col 3/21, ~23% through col 3.
  Running 9d 17h so far. H19 already done.
  `~/src/polyominoes/runs/a21fold/h20.log` for heartbeat.

- **ayr** (32c x86): **H17** pid 1214013, col 5/21, ~24% through col 5 (37h elapsed).
  **H18** pid 1213956, col 3/21, ~5% through col 3 (38h elapsed).
  H1–H16 done. `runs/a21fold/h17.log`, `h18.log` for heartbeats.
  Driver: pid 1213926, `scripts/an_fold_parallel.sh 21 2 14`, tmux `0:a21`.

- **H21 = 3^20 = 3,486,784,401** (closed form, add by hand when combining).
- **ayr partial** (H1–H16): 6,937,832,928,078,101 in `runs/a21fold/a21.partial`.
- **Combine** when all heights done: rsync dalby `runs/a21fold/h*.out` to ayr,
  sum h*.out cols at n=21 across both machines, add H21.
  Gate: a(21)/a(20) where a(20)=1,025,573,519,362,016 should be ~6.78
  (A006770 ratios climb toward lambda~7.10; NOT ~4 — that was a real-polyomino
  leftover). The salvaged H1-16 partial already gives 6,937,832,928,078,101 /
  a(20) = 6.765, so a(21) lands ~6.95e15.

- **Do not restart** either machine — correctness-or-dead-box bar only.

### dalby telemetry
- `scripts/a21_telemetry.sh 30` in tmux `0:telem`, pid 157284.
- CSV: `runs/a21fold/telemetry.csv`. Console: `runs/a21fold/telemetry_console.log`.
- Self-exits after fold ends.

### New engine a(21) — armed on dalby, waiting for H20 to finish
- Waiter in dalby tmux `0:ns-a21`: `tail --pid 30478 -f /dev/null && ... && scripts/dalby_ns_a21.sh`
- Fires automatically when H20 exits. Builds from `~/src/polyominoes-ns`
  (next-system branch), runs with --cores 80, 1 GB RAM/worker, checkpoint every 15 min.
- Run dir: `~/src/polyominoes-ns/runs/ns_a21/`, log: `runs/ns_a21/run.log`.
- Predicted ~8h wall, ~80 GB peak RAM.

## Code state (next-system branch)

- **Branch**: `next-system` at `cdc99fa` (local; not yet pushed).
- **All ns-gates green** (including new gates added this session):
  arch, math, regression, fold, spill, parallel, resume-boundaries, u128,
  holes (321 tuples matched vs old engine), verify (CRC catch confirmed).
- **M5 tasks completed this session**:
  - T5.1 `docs/formats.md` — byte-level format spec for POLYRUN, POLYCKPT,
    triangle, manifest, residues.
  - T5.2 `orchestrator/manifest.go` + `orchestrator/cmd/runcat/main.go` —
    WriteManifest and the runcat text-dump tool (built as `build/ns/runcat`).
  - T5.3 `verify/verify.go` + `verify/cmd/verify/main.go` — independent Go
    verifier (no orchestrator import). Checks CRC, record-count, manifest
    cross-refs, row-sum, growth-ratio, residues. `ns-gate-verify` PASS.
  - T5.4 `core/classifier.h` + run.h + mapreduce.h + runfile.h — `ClassifyHoles`
    with holes count encoded in key byte H+2 (keyLen extends H+2→H+3 for the
    holes path). `ns-gate-holes` PASS: 321 (H,n,k) tuples byte-identical to
    `build/tma_holes` at n=14.
- **Remaining M5**: T5.5 GF recovery (`Counter<ModP>` + residue emission) — not yet started.
- **Worktree on dalby**: `~/src/polyominoes-ns` at `cc7268d` (behind; scripts
  patched in-place). The waiter will build from that worktree, not from the
  current HEAD, so the new M5 code is NOT in the waiting a(21) run.

## Open performance question for the new engine

The new engine's parallelism model:

- **Process-per-unit**: each map/merge unit is a separate single-threaded C++ process.
- **`numUnits == cfg.Cores == 80`**: exactly 80 map units per column, all fired
  simultaneously, then `wg.Wait()` (barrier). Same for merge.
- **Load imbalance problem**: the key-space is sampled uniformly by key, but
  cost is NOT uniform by key. Heavy states (many viable masks, near the pole
  signature) cluster in certain key ranges. Fast units finish and cores idle
  while the tail catches up. There is NO work-stealing in the current code.
- **Fix**: change `numUnits = cfg.Cores * K` (e.g. K=4 → 320 units) while
  keeping the semaphore at 80. Fast-finishing units free their slot and the
  next queued unit starts. Peak RAM unchanged (only 80 run concurrently).
  This is a ~5-line change to `orchestrator/sweep.go` plus a `--unit-mult` flag.
  Sonnet identified this but didn't implement it yet — good candidate for Opus.

## Milestone state

| Milestone | Status |
|-----------|--------|
| M0 libenum core | DONE |
| M1 NVMe spill engine | DONE |
| M2 Go orchestrator + checkpoint | DONE |
| M3 a(21) cross-check | T3.2 in flight (waiter armed); T3.3 gated on a(22) |
| M3.5 sizing pre-flight | DONE (GO on dalby, ~5.8 days new engine) |
| M4 a(23) record term | blocked on M3 |
| M5 deliverable + outputs | T5.1–T5.4 DONE; T5.5 (GF recovery) not started |

## When the new engine a(21) finishes

1. Read `runs/ns_a21/run.log` — check `event=done` line for actual wall/RAM vs prediction.
2. Compare triangle output to old engine's combined T(n,H) table:
   `--compare` validates n≤18 automatically; n=19/20/21 need manual row-by-row diff.
3. If PASS → T3.2 closed. Update `fixtures/b006770.txt` with a(19), a(20), a(21).
4. Plan a(22) run (T3.3): old engine ~5-6 days on dalby; new engine ~2 days once T3.2 green.

## Pending coding work (no compute needed)

- **`--unit-mult` flag** in `orchestrator/sweep.go`: `numUnits = cfg.Cores * mult`,
  semaphore stays at cfg.Cores. Exposes as `--unit-mult N` CLI flag (default 1).
  Expected to improve effective core utilization on heavy columns.
- **T5.5 GF recovery**: `Counter<ModP>` + `Classifier<gf>` accumulating per-(H,n)
  residues for CRT recovery. Non-blocking (best-effort for M5).
- **#33 an_fold_parallel.sh kill fix**: add `trap` to reap child tma sweeps.
  Do after the live a(21) runs finish (don't churn the driver under a running job).
- **#30 OAMap<V> unification**: collapse FlatDB/FlatDB32/HoleDB/PerimDB into one
  template. Gated on a(21) in hand (same no-churn-during-run rule).
