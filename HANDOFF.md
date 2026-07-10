# HANDOFF — 2026-07-10: a(35) DONE + VALIDATED (dalby+ayr disk-split)

**a(35) = 3561147281381782175236253062** — banked `results/ns_a35/`,
`A35_VALIDATE_PASS` (a(1)-a(34) all reproduce banked; growth 6.9106 → λ≈7.1).

Computed via the **two-machine split-by-height = split-by-DISK** (the win: each
machine's heights hit only its own disk, no cross-height I/O contention):
- **dalby** (ARM, 80c, rev `b8f13d41`): `--heights 1-2,19-35` = H19 (long pole)
  + closed forms. wall **25112s (~7.0h)**, NVMe (no tmpfs/OOM).
- **ayr** (x86, 32c, rev `d6e5679`, native build): `--heights 3-18`. wall
  **19831s (~5.5h)**.
- Concurrent → **~7.0h total vs ~16h single-machine (~2.3x)**. Driver
  `scripts/run_height_subset.sh`. Combine: scp'd ayr's 16 shards to dalby's 19,
  `combine -in perheight -maxn 35`.
- **Bonus available:** T(35,19) is a REAL swept value (P16 not wired) → first
  independent holdout for the fitted P16 (not yet run). See results/ns_a35/PROVENANCE.md.

**History this session (see git):** simplify pass + SIGTERM-resume fix landed;
two-media tmpfs idea gave 4.6x on a34 but OOM'd a35 (H19 > RAM, killed tmux) —
FAILED, see docs/a35-two-media-plan.md ceiling note. Pivoted to the dalby+ayr
disk-split (this run). a(35) is the first independent holdout for P_16.

**dalby git note:** stuck at `b455b8ff` (github fetch prompts for the id_rsa
passphrase; user ssh-agent not loaded in non-interactive ssh). run_height_subset.sh
was scp'd in; the ENGINE binary (b8f13d41) is current, so results are clean.

**This session's landed work (all on master, pushed):**
- `0f0d176` bake the four validated scheduling knobs (unit-mult=8, merge-mult=1,
  steal-grain=0.05, persistent-workers) + GOGC=1000 in as engine DEFAULTS; flags
  kept for gates/A-B. A bare `orchestrate --kernel kink` is now the deployed config.
- `dd91550` **FIX the kink real-SIGTERM+resume over-count** (was open since 07-08):
  seed-round contribution was folded into hTri before column completion, so a
  mid-column kill's checkpoint (Col=col-1) double-counted on resume. Fixed by
  deferring the fold to column completion. Red-first `TestKinkResumeMidColumn`
  gated; real subprocess repro 5/5 (was 0/5). Resume is safe again.
- `b8f13d41` remove dead code (deadcode analyzer): `manifest.go`, `SampleKeysMulti`,
  `VerifyCRC`, `SpotcheckWithInput`, the two throwaway `experiments/` benches.
- dalby returned to `master` (was on the stale `even-keel` branch).

---

# HANDOFF — 2026-07-09 (Even Keel D1-D5 landed, branch `even-keel`)

`docs/even-keel-plan.md` fully executed: D1 `BalancedCutsMulti` (true
record-quantile partition sampler reading the full `.idx` union, fixing
`SampleKeysMulti`'s per-file-fixed-count under-sampling of fat files —
commit `8aa2058`), D2 wired into `mapPhase`/`mergePhase` (`59fc834`), D3
per-round/per-column `eff_cores` telemetry (`60dd2cde`), D4 `make
ns-gates` + `go test ./...` clean, `a(1..14)` byte-identical, two-
unit-mult invariant confirmed via `ns-gate-parallel`. D5 production
confirmation ran on dalby (H=15 real-swept, maxn=30 — see
`docs/full-utilization-redesign.md`'s "D5 confirmation" section for the
full numbers and the corrected-height note): fat columns went from
~20-24 to ~33-35 effective cores (of 80), whole-sweep wall-clock 204.3s
-> 140.9s (1.45x), output byte-identical (`combine --diff-b` PASS). The
empirical stop-condition did NOT fire — direction matches the 6.8->74.6
benchmark, smaller magnitude explained by this run's smaller record
count, not by the fix failing. All three commits pushed to
`origin/even-keel`.

# HANDOFF — 2026-07-08 (utilization-flag deployment audit, branch `redesign`)

**Infrastructure-only, no term-chase compute.** Audited every real-sweep
entry point under `scripts/` for the 5 utilization fixes validated on
`scripts/dalby_term.sh` (`--overlap-heights`, `--merge-mult 1`,
`--unit-mult 8`, `GOGC=1000`, `--persistent-workers`) — the a34
whole-run 19.8% utilization figure predates all of them, and no
end-to-end real-term run has confirmed the combined win at full
production scale since. Only three scripts invoke `orchestrate` at all:
`dalby_term.sh` (already fully wired), `scripts/bench_util.sh`, and
`scripts/kink_validate.sh`. No dedicated ayr or gympie kink/orchestrate
entry points exist — `dalby` is the sole real-sweep production machine
for this engine (`[[machine-roles-an-push]]`); ayr's role is cross-ISA
recompute verification, gympie is ancillary. `bench_util.sh` and
`kink_validate.sh` both `cd ~/src/polyominoes-ns` like `dalby_term.sh`
does, but on dalby that worktree currently sits on the (unmerged,
dalby-local) `steal-wall-time-floor` branch, not `redesign` — the flags
exist there too (redesign branched off master post that merge) but this
path split is worth resolving before the next real term push.

**Worktree split resolved.** `origin/steal-wall-time-floor` (dalby's
`polyominoes-ns` checkout) has 0 commits not already in `origin/master`
(confirmed via `git log origin/master..origin/steal-wall-time-floor`,
empty) — it's a fully-merged, stale duplicate of work `redesign`
already contains. Repointed all three scripts from
`cd ~/src/polyominoes-ns` to `cd ~/src/polyominoes` (dalby's real
`redesign` worktree, already built at `aa4bbd29`). Left the
`polyominoes-ns` worktree itself in place, untouched — removing it was
denied as an out-of-scope destructive action, so it now just sits
unused; jasonp can retire it whenever convenient. Re-validated the same
bounded maxn=20 `--compare` run in `~/src/polyominoes` directly: correct
output, same interleaved-heights evidence `--overlap-heights` is live.

**Gaps found and fixed:**
- `kink_validate.sh` (production-scale independent-reimplementation
  validator, real dalby compute) had none of the 5 fixes:
  `--unit-mult 4` (stale pre-fix default), no `--merge-mult`, no
  `--overlap-heights`, no `--persistent-workers`, no `GOGC`. Now matches
  `dalby_term.sh` exactly: `--unit-mult 8 --merge-mult 1
  --overlap-heights "$MAXN" --persistent-workers`, `GOGC=1000`, plus a
  `--cost-profile-out` it wasn't writing before (needed to see the
  effect at all).
- `bench_util.sh` (bounded utilization A/B harness) had `--unit-mult 4`
  hardcoded and no `--persistent-workers`/`GOGC`. Its `OVERLAP` and
  `MERGE_MULT` were already script parameters (by design, for A/B'ing
  those two specifically) so left as params; the other three are now
  hardcoded to the production values for the same reason `MERGE_MULT`'s
  own comment gives — a benchmark run that silently omits them isn't
  actually comparable to production, and future A/B of one of them
  specifically should edit the script deliberately.
- `dalby_term.sh` — already fully wired, no changes.

**Validated** on dalby (`~/src/polyominoes-ns`, `steal-wall-time-floor`
build, same flags present): a bounded real `--compare` run, maxn=20,
raw `orchestrate` invocation with the same flags now in both edited
scripts — wall-clock ~2s, `gate_parallel PASS (maxn=20)`, all of
a(1)..a(20) byte-exact against `fixtures/b006770.txt`. Flags confirmed
live, not just accepted-and-ignored: the startup banner echoed
`unit_mult=8 merge_mult=1`, and the first `cost_profile.tsv`/log rows
show `H=8, H=5, H=7, H=3` seed events interleaved rather than strictly
ascending — direct evidence `--overlap-heights` is sweeping heights
concurrently, not sequentially. Scratch run dirs
(`runs/util_flag_validate*`) and the stray uncommitted script edits used
for this check were cleaned off dalby afterward; the real fix lands via
this commit on `redesign`.

**Not done, explicitly out of scope for this pass:** no real term-chase
computation was started or resumed (parked, per standing instruction);
`polyominoes-ns` worktree left in place on dalby rather than removed
(deletion denied as destructive/out-of-scope) — dormant, safe to retire
whenever jasonp wants.

---

# HANDOFF — 2026-07-08 (utilization redesign, branch `redesign`)

**NOT yet merged; a real, first-class production kernel, still opt-in
by flag (not the default).** Per jasonp's 2026-07-08 `/goal` ("redesign
the software... especially look at ways to re-shard the work so units
can be more independent... no options off the table... fix this once
and for all"), branched off `master@79b0cce` (post the
`steal-wall-time-floor` merge below). That prior session's 8
bottlenecks were scheduling fixes on top of the existing per-round
barrier structure; this session found, validated, and fully deployed
the structural alternative `results/kink-carry.md`'s own "Caveats"
section named but never measured.

**The finding**: today's kink-carry column sweep synchronizes ALL
workers at every one of a column's H+1 rounds (seed, H mid-column stage
transitions, finalize) — a real barrier every round, not just a
scheduling inefficiency. The alternative: split a column's source
frontier into K independent shards up front, run each through seed + ALL
H mid-column stages PRIVATELY (zero synchronization during this phase),
merge all K shards' outputs exactly ONCE, then run the standard,
unmodified finalize step. H+1 barriers per column become 1.

**Built and validated at every layer, each independently gated**:
1. `core/kink_sharded.h` — the core algorithm (`kinkPrivateShardSweep`,
   `mergeAndFinalizeShardedColumn`). Traced and fixed a real correctness
   landmine along the way: `kinkStageTransition`'s budget check consults
   a record's own `ms`, which can be wrong on a not-yet-merged shard —
   fixed via `KinkStageCfg::permissiveBudget`. Honestly documented as
   "kept on as the safe default despite not yet finding a test case that
   proves it's necessary" — the asymmetry (silent undercounting vs.
   wasted compute) favors caution. `test/gate_kink_sharded.cpp`:
   multi-column harvested-triangle-row chains (the correct bar — NOT
   intermediate-table byte equality, which legitimately differs even at
   K=1 depending on prune timing, traced to `completionLowerBound` being
   a documented lower bound), 9 configs, all correct.
2. `worker/map_worker.cpp` — `--kernel kink --stage sharded` CLI mode.
   No new merge-worker mode needed: `--stage finalize` already merges
   multiple `--in` paths before running finalize.
   `test/gate_kink_sharded_worker_cli.cpp`: real subprocess, real file
   I/O, quantile-based key cuts (blind evenly-spaced hex cuts degenerate
   to one all-records shard — caught by checking each shard's own record
   count, not assumed correct from a passing gate).
3. `orchestrator/sweep_sharded.go` — `sweepColumnSharded` (Go dispatch:
   K parallel `--stage sharded` calls + one `--stage finalize` merge) and
   `ValidateShardedHeight` (exported comparison entry point).
   `orchestrator/kink_sweep_sharded_test.go`: real compiled workers, real
   multi-column sweeps, H=6/maxn=14 (K=4,K=8) and H=10/maxn=20 (K=8)
   byte-match the standard column kernel exactly. Caught and fixed a real
   bug here too: `sweepHeight` deletes its own frontier files as normal
   per-column cleanup, so the reference and sharded runs need separate
   seed copies, not a shared path.
4. `orchestrator/cmd/orchestrate` — `--kernel kink-sharded --sharded-k K`
   is now a REAL, first-class production kernel option on normal
   `orchestrate` runs, dispatched from `Run()` exactly like `column`/
   `kink` (`sweepHeightKinkSharded` conforms to `sweepHeightFn`: real
   column-granularity checkpoint writes, ctx cancellation, telemetry).
   Verified through the project's own AC-2 gate pattern, via the actual
   compiled binary:
   `orchestrate --kernel kink-sharded --sharded-k 8 --maxn 16 --compare`
   → `gate_parallel PASS (maxn=16)`, every known a(n) exact; a real
   SIGTERM-mid-run + `--resume --compare` at maxn=20 also → PASS. The
   earlier `--sharded-validate K --sharded-validate-height H` side tool
   still exists (quick single-height check, writes no checkpoint) and
   now calls the same production `sweepHeightKinkSharded`, not a
   separate driver.

Full `make ns-gates` (both ASan kernels) and `go test ./...` clean at
every commit.

**Effective speedup estimate** (synthetic uniform-random test data, K
shards / measured duplication factor D): K=8→~3.1x, K=16→~5.0x,
K=32→~8.7x, K=64→~15.7x.

**Still NOT the default kernel** — `--kernel kink-sharded` must be
requested explicitly; `column`/`kink` remain untouched and unaffected.
**Deliberately not yet done, scoped as follow-up given the stakes** (this
computes real a(n) values, per the standing "validate at scale before
record" practice): validation past H=12/maxn=22 or against real (not
synthetic/small-seed) frontier data — real frontiers are RGS-skewed,
expected to show worse duplication than the uniform-random test data
above; holes-path support (triangle only, matching the rest of the kink
kernel); work-stealing (the sharded path dispatches raw worker calls
directly, bypassing `mapPhase`'s steal machinery entirely — a scope gap,
not a correctness one). The `permissiveBudget` safety mechanism in
`core/kink.h` also remains unproven-necessary by any test built so far
(see `core/kink_sharded.h`'s "HONEST STATUS" comment) — kept on by
default regardless, given the risk asymmetry. Before this could be
recommended as the default for a real dalby a(n) push: real-scale
duplication measurement (the actual lever this whole redesign turns on)
and a head-to-head wall-clock comparison against `kink` at real H/maxn,
not just correctness.

**2026-07-08 update: first real-frontier validation, beyond H=12/maxn=22
synthetic-adjacent scale.** `./build/ns/orchestrate --maxn 26 --counter
u128 --sharded-validate 8 --sharded-validate-height 14 --run-dir
runs/sharded_validate_h14_m26` (real seed-from-column-0 sweep, genuinely
RGS-skewed frontier, not synthetic test data) —
`SHARDED_VALIDATE_PASS H=14 maxn=26 K=8 wall=1331.470s`, correct triangle
match. The run's own `cost_profile.tsv` splits reference vs. sharded
cleanly (two 27-row column-0..26 blocks): **reference 1103.7s wall,
sharded (K=8) 224.1s wall — a real 4.93x speedup**, *better* than the
`K=8→~3.1x` synthetic-data estimate above. Still only one (H, maxn)
point and still not a head-to-head at the actual dominant-height scale
(H17/maxn=33-class, hours long) — but the first real-data confirmation
that the redesign's core lever holds up outside synthetic test seeds,
and holds up favorably.

---

# HANDOFF — 2026-07-08 (utilization work, branch `steal-wall-time-floor`)

**Ready to merge to kink-carry/master, pending jasonp's review.** This
session's work (a(n) engine whole-run utilization, per jasonp's
2026-07-07 `/goal`, cleared 2026-07-08) lives on `steal-wall-time-floor`,
branched from `kink-carry@2cb81a4`. Term chase stays parked; this was a
separate, reopened thread specifically for utilization. Full `make
ns-gates` (both ASan kernels) and `go test ./...` clean at every commit;
a `/simplify` pass has run on the newest (steal-related) code.

**8 bottlenecks found and solved, deployed to `scripts/dalby_term.sh`,
each independently real-dalby-validated with correct output:**

1. **Straggler Tail** — `--overlap-heights` was only ever measured at a
   fixed 2 (one pair); raised to "all owned heights" per
   `results/scheduling.md`'s own original recommendation. 1.82x
   wall-clock at maxn=30 (21.6%->38.8% util).
2. **Merge Fan-Out Overhead** — merge was fanning out at map's granularity
   (320-way) for no reason; `--merge-mult 1` cuts fan-out to 80-way. 19%
   faster wall, 37% fewer CPU-seconds at maxn=30.
3. **GC Churn** — `GOGC=1000` (default 100 was firing ~26 GCs/sec against
   an 8MB heap goal for no reason; RAM was never remotely tight). 6.7%
   faster wall at maxn=30.
4. **Allocation Overhead** — the real root cause behind #3's symptom,
   found via a real heap-alloc profile (`POLY_MEMPROFILE`, gated
   diagnostic in `cmd/orchestrate/main.go`): `readIndexHeader` was
   allocating a full 4KB `bufio.Reader` just to decode a 19-byte header,
   at two call sites, 55% of a real run's total allocation. Fixed with a
   single `io.ReadFull` into a stack array. Also right-sized
   `ParseHeader`'s buffer. New fast local-iteration tool for this class of
   question: `orchestrator/sample_bench_test.go` (`go test -bench
   -benchmem`, ~0.5s vs a ~5min dalby round trip).
5. **Process-Per-Unit Spawn** — jasonp's standing, repeated point (not new
   from me): map/merge workers ran for a fraction of a second and paid
   real fork+exec cost every single time, thousands of times per run.
   `--persistent-workers` (new flag): a pool of long-lived `--persistent`
   map_worker/merge_worker processes fed via stdin instead of spawned
   fresh per unit (`orchestrator/workerpool.go` + the same feature in both
   worker CLIs). 6.2% faster wall, 7.7% fewer CPU-seconds at maxn=30, zero
   orphaned processes after normal exit or a real SIGTERM.

**Bottlenecks #1-#5 combined only bought 0.6% at real maxn=33 scale**
(6842.7s -> 6803.2s) — H17 (the dominant real-swept height) consumed
nearly the entire wall clock once it was the pool's sole occupant, and
none of those 5 touched that specific floor. Chased a sub-record
interrupt design (`forEachViableMask`/`viableRec`) that turned out to
target the wrong function entirely (that's the **column kernel**'s
enumeration, unused by production's `--kernel kink`; caught and corrected
same session, `results/sub-record-interrupt-design.md`). Real data then
showed the actual pattern: concurrency collapsed progressively across a
column's own kink-sweep stages (~43 active cores early, ~2.5 late, at
near-constant frontier size) — not a single pathological unit. A first
real fix attempt (`recordLess` lo-tiebreak, avoiding `combine()`'s
expensive left-extension path) was real but only bought 0.07% at scale.

**6. Kink-Stage Concurrency Collapse — the actual fix**: `--unit-mult 8`
(up from 4). Genuinely untested territory, not a dead-end retry — the one
prior "finer unit-mult rejected" memory finding was measured on the OLD
engine (pre-kink-carry), the same mistargeting class already caught once
this round. Real maxn=33 confirmation: **6798.6s -> 5674.2s (16.5%
faster), utilization 10.2%->12.4%** — the first real-scale utilization
GAIN this entire round, and the first fix that demonstrably moves H17's
dominant floor rather than only helping a secondary cost swallowed by it.

**7. Stealing Silently Broken — the real reason #1's steal attempts
measured nothing.** Investigating why `htop` kept showing one process busy
found the actual root cause: `stealEligible`'s `processed>0` gate was
permanently blocked for any unit finishing under 2s, because the C++
progress emitter unconditionally throttled its first report to a 2s
cadence. Bottleneck #1's three "fixes" (commits 208864b/9c5edc4/22b0206)
were all correct but downstream of this — the eligibility/scoring logic
was never the real blocker. Fix: first progress report fires immediately.
Real H17-isolated A/B: steals=0 before, 9468 steals after, 3523.9s total
(map-steal alone).

**8. Merge Range Straggler — merge had ZERO rebalancing, the whole
session.** Every prior fix only ever touched map; merge ranges launched as
fixed goroutines with no requeue path at all. Added the same
terminate/stop_key/on_progress work-stealing machinery `mergeRunFiles`
needed (simpler resume semantics than kink's mask enumeration — no
partial-tree-state problem, just "re-merge with lo_hex=stop_key") plus a
full `mergePhase` rewrite to a queue+steal pool. Real H17-isolated A/B:
**3523.9s (map-steal only) -> 3103.2s (map+merge steal), 11.9% further
improvement**, byte-identical H17 output confirmed correct.

**Best wins of the session, found only after jasonp pushed back hard on
the pace/depth up to that point** — both were real, previously-invisible
mechanisms hiding behind misdiagnosed or absent instrumentation, not
tuning knobs.

A `/simplify` pass on the #7/#8 diff (4 parallel review angles) found and
fixed a real gap: merge-side steals weren't being counted in telemetry at
all (`mergePhase` never took a `*telemetry` param). Also deduped SIGTERM
handling + the progress emitter (previously copy-pasted verbatim between
`map_worker.cpp` and `merge_worker.cpp`) into `worker/worker_util.h`.
Deferred as documented TODOs (`orchestrator/sweep.go`): unifying
`mapPhase`/`mergePhase`'s ~90%-duplicated scheduler bodies, and
`splitRemainder`'s `.idx` I/O held under the scheduler mutex on every
steal (now hit hundreds of times per column) — both real, both flagged
by the review, both deliberately not attempted mid-cleanup on code just
validated at production scale.

**Also found, separately flagged, NOT this session's fault, NOT fixed**:
a real, pre-existing correctness bug — real `SIGTERM` + `--resume` on the
kink kernel produces wrong `a(n)` values. Confirmed present identically
without any of this session's changes. `results/kink-resume-sigterm-bug.md`
has the full repro; `dalby_term.sh`'s `--resume` usage comment now warns
about it. **Do not trust a resumed kink-kernel run's output without
independently re-validating it** until this is fixed.

Full bottleneck-by-bottleneck log with every dead end (named, so none get
retried) and every real-dalby A/B: `docs/utilization-bottleneck-log.md`.

---

# HANDOFF — 2026-07-07

Frontier **a(34) = 515316838423862758858377704**, banked+validated, term chase
**parked**. **MERGED TO MASTER 2026-07-06** (master is the repo's public
face; kink-carry remains the working branch). Big tidy DONE — README.md is
the fork-and-reproduce entry point. Durable facts live in `MEMORY.md`,
`results/*.md`, `README.md`, and git history — this file is the live state.
GitHub repo RENAMED to `jhparkerb/polyplets` 2026-07-06; remotes updated
on all three hosts. Local dirs stay `~/src/polyominoes` until the running
jobs finish (their cwd lives there).

**No live jobs right now** — dalby and ayr both idle, all three machines'
working trees clean. Everything below is either fully landed or explicitly
parked with a reason, not silently stalled.

## Frontier / what's banked
- **a(1)…a(34)** all banked under `results/ns_a{n}/` (triangle, PROVENANCE,
  perheight, cost_profile). a(1)-a(20) match the b-file; a(21)-a(34) chain-match
  each prior term; ayr cross-ISA verify folded into a34 PROVENANCE.
- **Diagonal closed forms P_2…P_15 wired** (`orchestrator/sweep.go`
  diagCoeffTable, `diagonalStripValid` k≤15); deriver `scripts/derive_pk_fast.py`.
- **Symmetric counts (Hall of Mirrors, `cpp/sym/symtm.cpp`)** — all four types
  built, gated (`tests/gate_symtm.py`) and byte-matched to `runs/sym24/`:
  - **r90, r180, hmirror: n=34 banked** (gympie `runs/sym34/`;
    r180(34)=48710062997772, hmirror(34)=17385821908346).
  - **dmirror: n=32 banked** (`runs/sym32/dmirror.out`, D(32)=2156235549286;
    32-strip farm dalby+ayr complete 2026-07-05, prefix-matches sym24+sym28).
    Engine is the **Shrink Ray** compact-frontier rewrite (b358e39): flat
    sharded storage, ~1.6× RAM + ~2× speed vs the unordered_map frontier
    that OOMed dalby. Farm cost: dalby S=26..31 3.0M cpu-s / ayr S≤25
    1.7M cpu-s.
- **Related sequences: all five banked to full current reach**
  (`results/related-seqs-n32.md`): A030233 to n=34; the D-dependent four
  (A030222/34/35/194596) to n=32. n=33 for the four lands with the dalby
  run (T3, P_4-assisted — OEIS comment-only). Combiner
  `scripts/derive_related.py` via symdir `runs/sym32.derive/` (symlinks
  sym34 r90/r180/hmirror + sym32 dmirror); validates all 95 known OEIS
  terms, /4 and /8 divisibility asserts.
- **OEIS staging (2026-07-05)**: b-files `results/b*_upload.txt` for all six
  sequences (A006770+A030233 to a(33), the four D-dependent to n=32);
  a(34)/A030233(34) staged as *conjectured comments*, deliberately out of
  the b-files (no held-out P_16 check until a(35)). Entry files
  `oeis/A*.txt` updated with %C/%E, signatures normalized to full-date
  form. **Pre-submission checklist** (from jasonp's past editor threads) is
  in `oeis/README.md` — check every batch against it; signature dates must
  be set to the actual submission day. Submission is jasonp's.
- **dmirror diagonal quasi-polynomials** (`results/dmirror-diagonals.md`):
  d(S,S+k) is period-2 quasi-polynomial, degree k per parity class, leading
  S^k/k!, onset ≈2k+2. **P_0..P_4 pinned BOTH parities** (P_4-odd pinned by
  the completed n=32 farm's S=23 strip; P_4-even also cross-validated by two
  independent methods); **P_5 both parities fitted** via the cumulant/exp
  form (`scripts/dmirror_pk_exp.py`), now with 6 exact witnesses/parity —
  unchanged from the 4-witness fit (forward confirmation); level 6 refuses.
  GF-basis structure: G_k = N_k(x)/((1-x)^(k+1)(1+x)^k), N_k(±1) = (±2)^k
  for k≥1; G_k generates the polynomial law (raw counts agree in-regime
  only — paper wording fixed accordingly). No low-order bivariate closure.
  These formulas replace the RAM-impossible sparse strips: n=33 needs only
  P_4 (direct S≤28), n=34 only P_5 (direct S≤28).
- **Paper (`paper/polyplets-report.tex`)**: computational-report form,
  through five external review rounds + one big self-check round.
  Growth §3 upgraded to the confluent 3-param fit (Δ₁=1/2, λ≈7.111,
  θ→-1.02 emergent; `paper/lambda_fit.py`). GF bound recomputed beyond
  frontier (a(35)≥5.07e26, a(40)≥4.27e30; 16% capture at 34).
  **`paper/verify_claims.py` re-targeted at the full report — 397 checks
  GREEN** (parses tables from the .tex; caught + fixed 3 overclaims:
  G_k definition, residual-factor claim, N_k boundary k≥1). Restored
  91bdcdc-deleted data files it needs (results/fixed_height_gfs.txt etc.).
  Remaining TODO: n33-cost (job-gated).

## Jobs landed (2026-07-07 early morning; both started 2026-07-06)
- **dalby — M(17) max-hole-area sweep DONE 2026-07-07 04:27** (78-way
  split, wall 74,870s ≈ 20.8h, 4.928M cpu-s ≈ 1369 core-h). **Result:
  M(17)=28 — confirms Conjecture 1's prediction exactly** (fitted on
  n≤16, no forward test until this run). results/maxhole.txt pulled to
  the Mac (was stale at n≤16 locally, now synced through n=17). Paper
  updated (`paper/polyplets-report.tex`, the M(n) paragraph + Conjecture
  1 + open problem block): verified range n≤16→n≤17, next untested
  prediction is now M(18)=32 (exact, no rounding ambiguity).
- **ayr — dmirror n=33 cross-ISA recompute DONE 2026-07-07 03:34**
  (queue S=25,24,23,22,21,20 fully drained). **Cross-ISA byte-compare
  (ayr x86 vs dalby ARM): ALL SIX STRIPS MATCH** (S=25 matched earlier;
  S=24..20 matched this morning) — closes the "S≤25 compare pending"
  item in `results/related-seqs-n33.md`.
- ~~dalby n=33 direct strips~~ **DONE 2026-07-06 07:39** (24.0h wall,
  6.71M cpu-s, peak 126.2GB) — **completion drill EXECUTED**: strips on
  gympie runs/sym33/, all n<=32 prefixes byte-match n=32 farm (413/413);
  **D(33)=5475149862148** via fail-closed `scripts/dmirror_hybrid_sum.py`
  (closed forms reproduced 124 overlap cells before supplying 15 sparse
  cells); companions n=33 (T3) banked results/related-seqs-n33.md + staged
  as conjectured OEIS comments; **P_5-even conventionally PINNED** (equals
  exp fit; P_5-odd stays fitted, 7 witnesses; level 6 refuses); paper
  updated (D(33) ‡ cell, companions block, n=33 cost, dagger narrowed),
  verify_claims 398 GREEN.
- **n=34 dmirror: DECLINED 2026-07-06** (jasonp, at the close deadline).
  Measured n=33 peaks supersede the old ~90-160GB estimate: S=28@34 (k<=6)
  extrapolates to ~175-200GB and S=27@34 (k<=7) similar, vs dalby's 189GB
  incl. swap — marginal-to-infeasible, and P_6 (the formula escape) is
  unpinnable without n=34 data (circular). If ever revisited: probe
  S=28@34 alone first. The related-seqs reach is final at n=32 (T2) /
  n=33 (T3, comments); term chase for a(35)+ stays parked.

## Engine hot-path optimization (2026-07-07, branch `tm-hotpath-optim`)

Pushed to origin, NOT merged (jasonp's call whether/when). Two real,
gate+ASan-validated fixes on top of `kink-carry`'s `0fe41b4`:
1. `RunRecord.H`/`.keyLen`: `int`->`uint8_t` (bounded <=38, never lossy).
   `sizeof(RunRecord<W>)` 72->64 bytes, compiler-verified.
2. `succ.counts` in both hot paths (`map_shard_file`, `map_shard_stage_file`)
   now allocates from a `std::pmr::monotonic_buffer_resource` scoped to one
   spill epoch instead of the default allocator (map-profile.md's B2
   finding: 415.8M allocations counted in a34's swept portion, ~14% of map
   cycles predicted).

**Measured, not assumed:** on gympie (macOS/clang) fix 2 was a small
*regression* (~2-3% slower, likely `polymorphic_allocator`'s virtual-
dispatch overhead beating macOS's already-fast small-object allocator).
On **dalby** (Linux/ARM/g++, the actual production target) combined
fixes 1+2 gave a real, reproducible **4.47% speedup** (2 reps each,
n=28, `baseline_times=[259.9,260]` vs `fixed_times=[248.65,249]`).
Environment mattered more than the fix itself.

**Reach extrapolation** (a34's real 3.70h/80-core baseline, 4.4x/term
growth, applying the measured 4.47%): **a(36) fits in a week, a(37)
does not, on every configuration** (dalby-alone or full 122-core fleet,
optimized or not) -- 1.9-3.0 days for a(36) either way, 8.2-13.1 days
for a(37) either way. The optimization shifts wall time by a few hours
per row, never crosses the a(36)/a(37) boundary. An earlier version of
this table had an off-by-one loop bug that mislabeled a(37) as
reachable at 45.0h (that was actually a(36)'s wall) -- corrected, this
version is right.

A scary-looking multi-minute hang on gympie during gate-suite
re-validation turned out to be **not a bug**: driver1's `--ram 1MB`
forced-constant-spilling test legitimately takes ~4.5 minutes under
system contention (XProtect was pegging two cores at the time), not an
infinite loop. Confirmed by running the identical gate suite + ASan on
idle dalby: all gates PASS clean, including `gate_spill` and
`ns-gate-asan` on both kernels. Lesson: an unexplained slowdown on a
loaded/contended dev machine isn't automatically a code defect --
cross-check on the actual clean target environment before concluding
there's a bug.

**Terminal-sort investigation: fully closed, not abandoned.** The
codebase's own `map-profile.md` flags the terminal `sortRun` as the
next-biggest cost (~19-39% of hot-column wall) after the alloc fix.
Three genuinely different attacks were tested against REAL captured
signature data (dumped via a temporary, since-reverted debug hook) and
all three came back measured-negative, not just "seemed hard":
- **Radix bucket by leading signature byte**: real data shows severe
  skew (only 2/256 buckets ever populated) -- signature bytes are a
  restricted growth string (RGS) encoding of a partition, which has a
  hard mathematical bound (byte[i] <= 1+max(byte[0..i))), verified
  against ~5M real records (1 violation, parse-boundary noise). This
  isn't an implementation quirk, it's inherent to RGS; reordering which
  cell maps to which byte position does not help.
- **Recursive (multi-level) radix bucketing**, jasonp's suggestion to
  exploit the skew via recursion: measured at depths 1-4, total cost
  (sort-cost + partition-pass cost) stays flat at 99.9-100.9% of plain
  sort. Sort-cost alone does shrink as predicted, but partition-pass
  cost grows right alongside it and eats the saving.
- **Hash-bucket for balance + k-way merge** (near-perfect balance,
  stddev 7,629 vs 140k-197k for raw bytes): PROVEN algebraically, not
  just measured, to never beat plain comparison sort -- N*log2(N/K) +
  N*log2(K) = N*log2(N) exactly, independent of K, so bucketing can
  only match plain sort minus the extra O(N) routing-pass overhead.
  General fact, not specific to this encoding: bucketing can't beat the
  N log N comparison-sort floor unless key width is genuinely bounded
  independent of N, which ours isn't (needs ~log(N) bits to distinguish
  N growing frontier states).
- **Generation-order "nearly sorted" hypothesis** (successors might
  arrive close to sorted, making an adaptive sort cheap): measured on
  real data, 1.84M ascending runs out of ~5M records, mean run length
  2.71 -- barely above the ~2.0 expected for a PURE RANDOM permutation.
  Real but weak structure, ~6.5% theoretical ceiling before accounting
  for the overhead of tracking 1.84M run boundaries.

**Net: nothing left on the terminal-sort lever that survives contact
with real numbers.** If revisited, the honest starting point is that
all four natural attacks are closed, not unexplored -- a fifth idea
would need to be a genuinely different shape, not a variant of these.

## Data ceiling (why the term chase is parked)
- **P_16 is derivable** (fit from T(33,17)+T(34,18), self-consistent) but has
  **no independent holdout** until a(35); a(34)'s top cell has no closed-form
  cross-check. More terms need a fresh sweep — not planned pre-close.
- **Transfer-matrix Option 5** (`scripts/diag_transfer_gen.py`) infeasible:
  state count ~7.4×/k. Dead end without a rewritten engine.

## Open independent threads
- **Lean proof** (branch `lean-diagonal-proofs`, `polyplets/PROOF-STATUS.md`):
  (a) finiteness, (b) row profile, (c-fwd), (d-local) done+green; remain
  (c-rev), (d-global gap≤2), (e) offset-chain count.
- **Steal-tail diagnostic** (`results/steal-tail-h18.md`): banked, not
  deployed (trusted config).

## OEIS submission readiness (supersedes the hard 2026-07-06 date)
Batch is staged and checklist-clean, but **submission is now gated on
jasonp's own readiness process, at his insistence** — the OEIS AI policy
makes the author personally responsible for correctness, and editors now
routinely ask "how much of this is AI-generated?". Research on the policy
+ accepted/rejected precedents: `docs/oeis-ai-policy.md`.
- **The viva** (local-only files, deliberately uncommitted, in
  .git/info/exclude: docs/viva-exam.md, viva-reserve.md [chmod 000],
  viva-state.md, drill1-counting.md, drill2-tiers.md): exam taken
  2026-07-05, 56.5/100 vs bar (>=80, no core question below half).
  **Drill 1 (counting arguments) DONE 2026-07-06** — all of A1/A2/B1/B2/
  C1/C2 closed. **Drill 2 (tiers + validation) graded 2026-07-06/07** —
  D1 tier definitions done (one contested point resolved, jasonp's
  answer stands); E1 shared-logic mitigations strong but missing the
  held-out P_k item; F1 mod-p mechanism correct but doesn't name the
  reimplementation as the closing answer. Cold retake variants still
  pending after a spacing gap. **Full grading state: docs/viva-state.md**
  (local).
- Before submitting, also: jasonp rewrites all staged %C lines in his own
  words (Claude meaning-checks only); signature dates -> actual
  submission day; pink-box replies are jasonp's alone, always.

## Remaining work ledger
1. ~~Housekeeping~~ DONE 2026-07-06 (the big tidy: process docs, one-shot
   scripts, experiments/, stale drafts, autonomy/, polyplets/ removed;
   README.md replaces ROADMAP.md as the repo face).
2. ~~M(17) on dalby~~ DONE 2026-07-07 04:27 — M(17)=28 confirmed, paper
   Conjecture-1 note + maxhole.txt updated (see "Jobs landed" above).
3. ~~Engine hot-path optimization pass~~ DONE 2026-07-07 — branch
   `tm-hotpath-optim` pushed, validated (dalby gates+ASan clean), real
   4.47% win measured, reach ceiling confirmed unchanged (a36 yes/a37
   no either way). NOT merged -- jasonp's call. Terminal-sort lever
   fully investigated and closed (see section above); nothing else
   queued there.
4. Paper: final read-through after the tidy passes.
5. Viva: cold retakes (V8/V12/V13 drill-1-flavor, V18/V19/V20 drill-2-
   flavor per docs/viva-state.md), then %C authorship pass (jasonp's own
   words), then jasonp submits.
6. **Lessons-learned document** (jasonp + Claude collaboration) — after
   compute and paper are done, BEFORE submitting. jasonp's explicit ask
   2026-07-06.

## Starting a fresh session from here
Read this file first, then `MEMORY.md`'s index (auto-loaded) for standing
practices. The two active branches: `kink-carry` (general work, docs,
paper, results -- this file lives here) and `tm-hotpath-optim` (engine
optimization, pushed, unmerged, nothing pending on it). No open threads
need immediate action; next steps are entirely jasonp's pacing (viva
retakes, whether/when to merge the optimization branch, whether to revisit
a35+ compute at all given the reach ceiling above).
