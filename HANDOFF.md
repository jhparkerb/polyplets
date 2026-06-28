# HANDOFF — 2026-06-28 10:10 EDT

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
