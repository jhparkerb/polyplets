# HANDOFF — 2026-06-29

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
