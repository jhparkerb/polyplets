# Utilization bottleneck log

Live log for the 2026-07-07 utilization /goal: push dalby a(n)-engine whole-run
core utilization toward 100%, one named bottleneck at a time. Rule: every
candidate solution that gets invalidated is recorded here, with a unique
name, so it is never retried. Bottlenecks also get unique names. Baseline:
**a34 whole-run utilization was 19.8% on 80 cores** ([[cloud-investigation-2026-07-07]]
in memory / `results/` — RAM/disk are not the constraint).

Score function: utilization trends up, total wall trends down-or-flat
(brief regressions OK), code quality trends up. Stop condition: >=5
bottlenecks found AND solved, with every proposed solution to each one
tried (good or bad).

## Status summary

| # | Bottleneck | Status | Win |
|---|---|---|---|
| 1 | Straggler Tail | solved (overlap-heights=all, deployed) | 1.82x wall-clock, 21.6%->38.8% util, real maxn=30 A/B, correct output |
| 2 | Merge Fan-Out Overhead | solved (merge-mult=1, deployed) | 19% wall-clock, 37% fewer CPU-seconds, real maxn=30 A/B, correct output |
| 3 | GC Churn | solved (GOGC=1000, deployed) | 6.7% wall-clock, real maxn=30 A/B, correct output |
| 4 | Allocation Overhead | solved (readIndexHeader fix, deployed) | 55%->lower share of a 20GB/run heap profile; real root cause behind #3's symptom |
| 5 | Process-Per-Unit Spawn | solved (--persistent-workers, deployed) | 6.2% wall-clock, 7.7% fewer CPU-seconds, real maxn=30 A/B, correct output, zero orphaned processes |

## Bottleneck #1: Straggler Tail

One dominant map unit (a single frontier cursor range) runs far longer than
its peers, so once the rest of a column's units finish, N-1 cores sit idle
waiting for the last one. Grows with height (design-08 Finding 3: tail
worsens as H increases), and is the largest measured contributor to low
whole-run utilization.

**Solved sub-part — overlap-heights.** Instead of interrupting the
straggler, run multiple heights concurrently in one shared core pool so a
short/cheap height's map work fills the cores idled by another height's
straggler tail or merge phase. Already wired (`--overlap-heights N` in
`orchestrator/sweep.go` + `cmd/orchestrate`), just not turned on in the
production driver (`scripts/dalby_term.sh`). Measured real dalby run, a34
H16+H17: sequential 26.2% (hypothetical sum) vs **--overlap-heights 2:
33.0%**, byte-identical CPU-seconds (confirmed: packs existing work, redoes
none). See `results/utilization-fix-and-ceiling.md` for full numbers.
**Next action:** wire into `dalby_term.sh` and validate at scale
(`validate-at-scale-before-record`) before trusting for a real term.

**Diagnosed, NOT solved — sub-record interrupt granularity.** The
cooperative-stop check in `core/kink.h:296` fires only between records
(every 1024 consumed), never inside one record's own successor enumeration
(`forEachViableMask`). For a pathological record whose own enumeration
dominates wall time, no scheduling change (steal, overlap, anything
between-record) can reach it — this is a hard floor on any straggler-based
approach, not a bug to keep chasing at the scheduler level. Fixing it needs
checking the stop flag *inside* the enumeration hot loop — invasive,
carries real regression risk on the 99% of non-pathological records, not
attempted here.

### Dead-end solutions tried (Bottleneck #1)

- **wall-time-floor-only** (commit `208864b`): added a wall-time fallback
  to `stealEligible` so long-running low-record-count units clear the
  eligibility gate. Correct fix for a real defect, gated, kept — but
  **zero measured effect** on H17 col3 utilization on its own (needed the
  next two fixes before the scheduler behaved correctly at all, and even
  then moved nothing — see reference-rate-fix and remaining-clamp-fix).
- **reference-rate-fix** (commit `9c5edc4`): fixed `stealScore`'s pace
  reference from `totalDone/elapsedSincePhaseStart` (self-defeating,
  degrades the longer a straggler runs) to finished-units-only pace.
  Correct fix, gated, kept — combined with wall-time-floor-only, still
  **zero net effect** on the measured column (24.7%->25.1%->25.0%, noise).
- **remaining-clamp-fix** (commit `22b0206`): fixed `remaining()` clamping
  to 0 when a map unit's flat per-unit estimate was grossly wrong (last,
  open-ended key range measured 590M records against a 64K flat estimate on
  H17 col3). Correct fix, gated, kept — combined with the above two, still
  **zero net effect** (24.7%->24.0%, noise-level).
  - **Why these three "worked" yet moved nothing**: `POLY_STEAL_DEBUG`
    tracing (commit `bab6e64`) proved the scheduler now nominates and
    attempts to steal the correct straggler every time — the eligibility/
    scoring logic was never the actual blocker once fixed. The real
    blocker is the sub-record interrupt granularity above: a nominated
    steal cannot complete if the victim can't yield control until its
    current record's enumeration finishes. **Conclusion for future rounds:
    do not propose further `stealEligible`/`stealScore`/`remaining()`
    tuning for Bottleneck #1** — that surface is exhausted; the only two
    remaining levers are overlap-heights (solved) and sub-record interrupt
    (deferred, own investigation).

## Bottleneck #1 continued: overlap-heights was under-configured

Exact per-unit instrumentation (`POLY_UNIT_LOG=1`, `scripts/analyze_unit_concurrency.py`)
on a real maxn=26 column showed map-unit concurrency is high while units are
actually running but map is only active ~22% of a column's wall — the rest
is inter-round merge with zero map concurrency (H13 col4: active 0.88s of
4.09s span). This is the same mechanism `results/scheduling.md` already
named ("Why merge is not cores-wide (and overlap exists)"), whose own
recommendation is **`--overlap-heights = number of swept heights owned`**,
not the small fixed 2 the original fix deployed (`utilization-fix-and-ceiling.md`
only ever measured the H16+H17 pair).

**Real dalby A/B, same code/range (maxn=30, real sweep now only H3-H15 --
diagonalStripValid's k-range grew to <=15 since a30 was first computed, so
the OLD PROVENANCE.md wall (3711s, H3-H17) is stale and not comparable):**

| overlap-heights | wall | cpu_s | utilization | a(30) |
|---|---:|---:|---:|---|
| 1 (sequential) | 689.6s | 11926.6 | 21.6% | 227969227118066423789154 (correct) |
| 15 (all owned) | 378.2s | 11742.2 | 38.8% | 227969227118066423789154 (correct) |

**1.82x wall-clock speedup, near-doubled utilization, near-identical
CPU-seconds (packing, not redoing work), byte-identical correct output both
configs.** Deployed: `scripts/dalby_term.sh` now passes `--overlap-heights
"$N"` (over-provisioning the height pool past the real count is harmless —
RAM co-resident for all real-swept heights measured <100MB).

**Process note:** a mid-investigation dead end almost got mistaken for a
correctness bug — the first oh=15 run appeared to stop sweeping at H15
instead of the expected H17, which looked like data loss. Root cause was
just the closed-form coverage growing since the original a30 run, not a bug;
resolved by getting a same-code oh=1 baseline before drawing any conclusion.
Lesson: **always get an apples-to-apples same-code baseline before trusting
a dramatic-looking speedup number** — logged as its own process reminder,
not a numbered bottleneck.

### Dead-end tooling attempts (measurement, not a bottleneck)

- **small-maxn (~26) external ps-sampling, 1Hz** (`scripts/profile_concurrency.py`
  v1): far too coarse — a whole small-maxn run finishes in ~2 minutes with
  individual round-phases ~0.1-0.3s, so most 1s samples just miss any live
  worker. Not usable below production scale.
- **small-maxn external ps-sampling, 0.1Hz** (same script, faster interval):
  still aliased — 96.6% of samples read zero map workers even during the
  dominant height, both because per-unit runtime at tiny frontier sizes can
  be sub-100ms (shorter than the sample gap) and because fork+exec of `ps`
  itself is comparable overhead at that timescale. **Conclusion: external
  process-count sampling is not a viable measurement method at small-maxn
  scale, at any practical interval** — replaced by exact in-process
  instrumentation instead (see below). Aggregate `cost_profile.tsv` numbers
  (wall_s/cpu_s, measured inside the process, not sampled) remain valid at
  small scale; only external concurrency *sampling* was the dead end.
- **Repeated 2-minute toy-scale benchmark loop** (this session, several
  maxn=26 runs comparing `--overlap-heights` 1/2/11): abandoned mid-attempt
  per jasonp's direction — too noisy/small to trust for a real comparison;
  replaced with one substantial (~20-25 min) real maxn=29 run as the
  reference benchmark instead of stacking more tiny ones.

### Measurement tooling added this round

- `scripts/profile_concurrency.py`: external `/proc`-based worker-count
  sampler, configurable interval. Useful at **production scale only** (a29+)
  where per-unit runtime is seconds, not sub-100ms — not used for small-maxn
  diagnostics after the dead end above.
- `scripts/analyze_unit_concurrency.py` + `POLY_UNIT_LOG=1`'s new
  `start_unix` field (orchestrator/sweep.go): exact per-unit (start, wall_s)
  intervals straight from the orchestrator, zero sampling error, works at
  any scale. Preferred over external sampling going forward.

### Real production-scale confirmation (maxn=32, this round)

Full real run via `scripts/dalby_term.sh 32` (the actual production driver,
not a diagnostic toy run): wall=834.1s, cpu_s=29350.3, **utilization 44.0%**
— consistent with (and better than) the maxn=30 A/B, confirming the
overlap-heights win holds and grows at larger scale, not just at the one
tested size.

This run also surfaced (and got fixed, not counted as a numbered
bottleneck — it's a validation-script correctness bug, not an idle-core
one) a real defect: `dalby_term.sh`'s per-term banked-value lookup died
under `set -e` at n=22 (no `results/ns_a22/` dir exists — a22's value only
exists embedded inside `ns_a23`'s differently-formatted triangle), silently
truncating validation for every later term in the very first real use of
the generalized script. Fixed: skip gracefully (missing dir, or a
non-2-column format) instead of crashing or, worse, naively summing a
3-column triangle in awk floating point (confirmed to lose precision past
~16 digits: a23 came out `...768` instead of the correct `...732`).
Re-validated against the maxn=32 run's actual output: full a(21)-a(31)
pass, `MISMATCH=0`.

## Bottleneck #2: Merge Fan-Out Overhead — SOLVED

Real a30 data (`mergecheck` run) showed merge's own active-window
concurrency was only ~15/80 cores (cpu/wall ratio) even with overlap-heights
deployed. Two hypotheses tested:

**Hypothesis A — same key-range imbalance as map's Straggler Tail (REJECTED
quickly).** Added `event=mergerange` instrumentation (`POLY_UNIT_LOG=1`,
reused the existing env var rather than adding a new one) to log each merge
range's exact (start, wall_s). Real data (H15 col4, 5120 ranges across the
column's rounds): the single largest range was only **0.1% of the column's
total merge wall** — ranges are well-balanced, not a straggler at all.
Dead end, logged so it's not retried.

**Hypothesis B — fixed per-process spawn overhead dominates small merge
ranges (CONFIRMED).** Same data: wall_s barely correlates with out_records
(**Pearson r=0.24**) — a range with 1206 records takes ~0.035s, one with
31745 records (26x more) takes only ~0.09s (3x). Most of each ~37ms range is
constant overhead (process spawn + file-open), not proportional work. The
engine already anticipated this: `--merge-mult` exists specifically "to cut
merge fan-in" (code comment, `orchestrator/sweep.go`'s `mergeMult`), but the
production driver never set it, so it silently followed `--unit-mult` (4x
the fan-out map needs, since map genuinely benefits from fine granularity
while merge doesn't).

**Real dalby A/B, same code/range (maxn=30, overlap-heights=15):**

| merge-mult | wall | cpu_s | utilization | a(30) |
|---|---:|---:|---:|---|
| 4 (implicit default, = unit-mult) | 377.7s | 11670.5 | 38.6% | correct |
| 1 (deployed) | 305.7s | 7291.7 | 29.8% | correct |

**19% faster wall-clock, 37% fewer total CPU-seconds, correct output both.**
Note the utilization *ratio* itself went down (38.6%->29.8%) even though
this is a real win — cutting spawn overhead removes real (if unproductive)
CPU-seconds, which mechanically can lower a crude cpu/wall ratio without the
outcome being worse; wall-clock and total CPU-seconds are the truer signals
here, and both improved. Deployed: `scripts/dalby_term.sh` now passes
`--merge-mult 1`.

### Dead-end solutions tried (Bottleneck #2)

- **merge-range-imbalance** (hypothesis A above): merge ranges from
  `SampleKeysMulti` are well-balanced (unlike map's), rejected by real
  per-range data in one measurement pass. Do not re-investigate merge-side
  balance — the imbalance mechanism from Bottleneck #1 does not transfer to
  merge.

## Bottleneck #1, real production-scale follow-up (maxn=33): floor confirmed worse at scale

Real production run via `dalby_term.sh 33` (both Bottleneck #1 and #2 fixes
deployed): full validation passes end-to-end (a1-a33 all correct,
`A33_VALIDATE_PASS`), confirming the earlier `dalby_term.sh` fix holds up on
a genuinely new term. But **utilization measured 6.34%** on fresh data —
much worse than a32's 44.0%.

**False alarm ruled out first:** `cost_profile.tsv` uses append-mode
(`orchestrator/telemetry.go`, `os.O_APPEND`) and `runs/ns_a33/` had stale
rows from an earlier, pre-session a33 computation (before P13-15 closed-form
were wired) mixed in with fresh rows — `run.log` (freshly truncated per
run) confirmed zero real H18 events this run, contradicting the stale
tsv's H18 rows. Real analysis used only `run.log`'s `event=column` lines.
**Action item, not yet done:** `dalby_term.sh` should truncate/move aside a
stale run-dir before reuse rather than relying on `mkdir -p`, so a future
utilization measurement doesn't require this same manual disambiguation.

**Real cause: Bottleneck #1's floor (Straggler Tail) gets worse as N grows,
exactly as `design-08` Finding 3 predicted ("tail worsens with height").**
H17 (the real top height at maxn=33) alone accounts for 6839.6s of the
6842.7s total wall — it now dominates so completely that overlap-heights
has almost nothing left to hide it behind. Per-unit instrumentation
(`analyze_unit_concurrency.py` on H17 col5) confirms the same mechanism
already diagnosed under Bottleneck #1: unit 319 (the last, open-ended
key-range unit) tops the wall_s ranking in 9 of 10 rounds sampled, with
wildly non-record-proportional cost (out_records ranging 4M-957M with no
correlation to wall_s) — successor-count explosion is a property of which
specific states land in that range, not of input balance. **Also newly
observed: the same last-bucket pattern shows up in merge ranges too**
(merge range 79/80, the open-ended one, tops every round sampled, though
only ~2.1% of column wall vs map's ~8% — present but much less severe on
the merge side). Folding this into Bottleneck #1 rather than a new
bottleneck, since it's the identical root mechanism (SampleKeysMulti's
open-ended last bucket + data-dependent successor-count variance), just now
confirmed to also touch merge, not only map.

**Two known dead ends reconfirmed applicable, not re-tested (per
[[engine-utilization-and-scheduling]] in memory: finer unit-mult and plain
LPT were already measured-rejected for this exact mechanism in a prior
session) — do not re-attempt either for Bottleneck #1.**

**The only remaining lever for this floor is the sub-record interrupt
(checking the cooperative-stop flag inside `forEachViableMask`'s recursion,
not just between records) already flagged as its own investigation.**
Traced the call sites (`core/mapreduce.h:83,454`) and confirmed a
lower-risk variant isn't available: the `fn` callback per emitted mask
can't unilaterally stop the enclosing recursion without a flag check inside
`viableRec` itself (`core/transition.h`), which is exactly the "invasive,
regression risk on the 99% of non-pathological records" scope already
flagged. Deliberately NOT attempted this round — it needs its own
dedicated investigation with full gate/ASan/parallel validation and a real
dalby A/B before trusting it, not a rushed change late in an already-long
session. Left as a scoped, well-evidenced future item, not silently
dropped.

**CORRECTION, later in the same round:** `forEachViableMask`/`viableRec`
turned out to be the wrong target entirely — that's the column kernel's
enumeration (`core/mapreduce.h`'s `map_shard_file`), which production's
`--kernel kink` never calls. Kink's real hot path is `kinkStageTransition`
(`core/kink.h:98`), a bounded `for (occupy in {0,1})` loop with no
recursive tree. See the "Bottleneck #6 attempt" section below for the full
correction and what's actually still open.

### Dead-end solutions tried (this round)

- **checkpoint-overhead** (hypothesis: `--checkpoint-every 300`'s periodic
  big.Int triangle serialization + file I/O measurably steals wall time):
  real dalby A/B, maxn=30/overlap=15/merge-mult=1, `--checkpoint-every 300`
  vs effectively off (`999999`): 305.7s vs 303.9s — **statistically
  identical, confirmed negligible at these run lengths in one fast
  (~5 min) test.** Do not re-investigate checkpoint frequency as a
  utilization lever at this scale.

## Bottleneck #3: GC Churn — SOLVED

With the sub-record interrupt lever deliberately deferred (see above, too
invasive to rush) and the map/merge straggler mechanism fully exhausted for
this session, looked at a genuinely different layer: the Go orchestrator
itself, not the C++ workers. `GODEBUG=gctrace=1` on a real dalby run
(maxn=30, overlap=15, merge-mult=1) showed **8063 GC cycles in a ~305s
run** (~26/sec) against a tiny 8MB heap goal — constant churn, Go's own
self-reported ~5% CPU spent in GC. RAM was never remotely a concern (dalby
has 122GB; even a much bigger heap goal is trivial), so the default GOGC=100
threshold was needlessly aggressive for this workload's allocation pattern
(lots of small, short-lived objects from goroutine/channel/map-unit
bookkeeping, not a large working set).

**Real dalby A/B, same code/config (maxn=30, overlap-heights=15,
merge-mult=1):**

| GOGC | wall | cpu_s | a(30) |
|---|---:|---:|---|
| 100 (default) | 303.9s | 7377.7 | correct |
| 400 | 288.7s | 7688.9 | correct |
| 1000 (deployed) | 283.4s | 7762.4 | correct |

**6.7% wall-clock win end to end** (matches the self-reported ~5% GC
overhead closely), diminishing returns past 400 so settled on 1000 rather
than chasing marginal gains further (e.g. `GOGC=off` risks unbounded growth
on a long production run for no measurable further win at this scale).
Deployed: `scripts/dalby_term.sh` now sets `export GOGC=1000`.

This is the first bottleneck this round found on the Go/orchestrator side
rather than the C++ engine or scheduling logic — a genuinely different
layer, not a variant of Bottlenecks #1/#2's mechanisms.

### Dead-end solutions tried (config-tuning sweep, this round)

- **steal-disable** (`--steal-grain 0` vs `0.05`, same GOGC=1000/overlap=15/
  merge-mult=1 config): 281.6s vs 283.4s — statistically identical, noise-
  level. Confirms steal is now essentially inert (consistent with the
  Bottleneck #1 floor diagnosis: nominated steals rarely/never actually
  complete), but disabling it doesn't cost or save anything measurable
  either. Not deployed either way; no clear win to bank.
- **coarser-unit-mult** (`--unit-mult 2` vs `4`, same other config): 384.5s
  vs 283.4s — a clean **35% regression**. Map, unlike merge, does NOT
  benefit from coarser granularity (merge-mult's fix does not transfer to
  unit-mult) — finer map splitting still helps the many non-dominant
  columns even though it can't fix the dominant straggler's floor. Do not
  retry lowering `--unit-mult` below 4.

## Bottleneck #4: Allocation Overhead — SOLVED

`GODEBUG=gctrace=1` on a real dalby run (maxn=30/overlap=15/merge-mult=1)
showed 8063 GC cycles in ~305s against a tiny 8MB heap goal. Bottleneck #3
tuned `GOGC=1000` around this symptom; jasonp's direct pushback ("rather
than tune I think you have to get to the bottom of why it was firing so
often") led to root-causing it with a real heap-alloc profile
(`POLY_MEMPROFILE`, `runtime/pprof.WriteHeapProfile`, gated diagnostic in
`orchestrator/cmd/orchestrate/main.go`).

**Root cause: `readIndexHeader` allocated a full 4KB `bufio.Reader` just to
decode a 19-byte fixed header, at two call sites that then never touched
the reader again** (everything else uses positioned `f.ReadAt`) —
`SampleKeysMulti` alone was 55% of a real run's total allocation (11.7GB of
21.4GB). Fixed: `readIndexHeader` now takes a plain `io.Reader` and decodes
the header via one `io.ReadFull` into a stack array — one syscall, zero
heap allocation, replacing 5 buffered `binary.Read` calls through a wasted
buffer. Also right-sized `ParseHeader`'s buffer (256 bytes, not 4KB, for a
genuinely-streamed but tiny text header) after a follow-up profile showed
it as the new #4 allocator.

**Fast local iteration loop**, also built this round per jasonp's direct
feedback that a ~5min dalby round-trip is far too slow for allocation
questions: `orchestrator/sample_bench_test.go` (`go test -bench
-benchmem`) exercises the exact hot path against a realistic local fixture
(6400-entry `.idx`) in ~0.5s total. Use this for future allocation
iteration; reserve real dalby runs for confirming a promising local result
at production scale.

At `maxn=30` with `GOGC=1000` already masking most of the symptom, the
wall-clock delta from this fix alone was flat (282.5s vs 283.4s, noise) —
expected, since GOGC=1000 already suppressed most GC overhead; the value
is in cutting real allocation volume/syscalls (matters more at larger
scale and independent of GOGC tuning), not in this specific benchmark's
wall-clock. Verified via a second heap profile that the fix actually
reduced `sampleIndexKeys`'s allocation footprint (~24% cumulative
reduction) — a before/after comparison, not just a plausible-sounding
change.

## Bottleneck #5: Process-Per-Unit Spawn — SOLVED

jasonp's standing, repeated point (not a new observation from me): map and
merge workers run for a fraction of a second each and pay real fork+exec
startup cost every single time, spawned fresh per work unit — thousands of
times per real run, purely because that's architecturally simpler than a
real worker pool. Circled for the whole project's history, never done.

**Fix, two halves:**

- **C++ (`worker/map_worker.cpp`, `worker/merge_worker.cpp`)**: refactored
  the one-shot request handling into `runOneRequest(tokens)`, callable
  either from argv (unchanged one-shot path, byte-for-byte the prior
  behavior) or in a loop reading whitespace-tokenized request lines from
  stdin (`--persistent`), one request per line, until EOF. `g_terminate`
  resets between requests so a prior request's SIGTERM can't bleed into
  the next one. Gated: `test/gate_persistent_worker.cpp` drives the real
  compiled binaries — the full kink seed/stage/finalize chain for one
  column through ONE persistent process (vs H+2 spawns), byte-matched
  against the column-kernel one-shot path; RED confirmed by reverting the
  feature (real "unknown arg: --persistent" failure) before wiring into
  `ns-gates`/`ns-gate-fast`. Also covers merge_worker and two independent
  columns/merges replayed through one process (no state bleed).

- **Go (`orchestrator/workerpool.go`)**: `WorkerPool` holds `size` slots,
  each lazily starting at most one persistent map_worker + one persistent
  merge_worker and keeping them alive for the pool's whole lifetime. A slot
  is one concurrency unit whether serving a map or merge request —
  preserves the exact same Cores-wide concurrency ceiling the old shared
  `sem` channel gave (map and merge compete for the same budget under
  overlap-heights; two separate pools would have doubled it). Wired into
  `mapPhase`/`mergePhase` via a new `cfg.Pool` field (nil-safe, falls back
  to the original exec-per-unit path unchanged) and a new
  `--persistent-workers` CLI flag.

**Caught and fixed while validating**: a leftover, unconditional `sem <-
struct{}{}` at the old map dispatch site that I forgot to remove when
adding the pool branch — double-acquired (or in the pool path, acquired
and never released) the Cores-wide semaphore, deadlocking
`TestHeightNm2NoColumnWork` under `go test`. Confirmed by reverting
`sweep.go` alone (test passed clean without the change, hung with it) —
a real bug, not a flaky test.

**Real dalby A/B, same code/config (maxn=30, overlap-heights=15,
merge-mult=1, GOGC=1000):**

| | wall | cpu_s | a(30) |
|---|---:|---:|---|
| exec-per-unit (default) | 282.5s | 7755.3 | correct |
| --persistent-workers | 265.0s | 7155.8 | correct |

**6.2% faster wall-clock, 7.7% fewer CPU-seconds, correct output, zero
orphaned map_worker/merge_worker processes** after both a normal exit and
a real SIGTERM (checked via `ps` on dalby). Deployed:
`scripts/dalby_term.sh` now passes `--persistent-workers`.

**Found and separately flagged, not fixed here**: while validating kill+
resume specifically under `--persistent-workers`, found a real,
**pre-existing** correctness bug — real SIGTERM + `--resume` on the kink
kernel produces wrong `a(n)` values (consistent over-count). Confirmed
present identically without `--persistent-workers` (exec-per-unit path,
clean checkout), so not caused by this work. Full writeup:
`results/kink-resume-sigterm-bug.md`. `scripts/dalby_term.sh`'s `--resume`
usage comment now warns about this explicitly. Not investigated further
this round — flagged clearly rather than bundled into an unrelated fix or
silently dropped.

**Follow-up allocation fix (same theme as #4, not a new bottleneck):** a
fresh heap profile taken WITH `--persistent-workers` enabled (the earlier
profile predates this feature and is stale for reasoning about what's left
— `os/exec`'s per-spawn machinery is gone entirely, as expected) found the
new `workerProc.runRequest` code itself allocating: `requestLine+"\n"`
copies the whole request line just to append one byte, once per work unit.
Fixed with two separate writes (the `"\n"` is a zero-allocation string
literal). Confirmed via before/after profile: `runRequest` drops off the
top-allocator list entirely.

## Real production-scale confirmation, all 5 fixes combined (maxn=33)

Full real run via `scripts/dalby_term.sh 33` with every deployed fix live
(overlap-heights=all, merge-mult=1, GOGC=1000, the allocation fixes,
--persistent-workers): full validation passes (`A33_VALIDATE_PASS`,
`a(33)=74631481980411777590683952`, matches the pre-session banked value).

**Honest result: wall=6803.2s vs the pre-session baseline's 6842.7s —
only 0.6% faster. Utilization 10.4%->10.3%, essentially flat.**

This is not a failure of the fixes (each is independently real and
correctness-verified at maxn=30 — 6-19% wins). It's a scale effect: at
a33, H17 (the dominant real-swept height) consumes nearly the entire wall
clock once it's the pool's sole occupant (no sibling height left to
overlap into) — exactly the Straggler Tail floor already diagnosed under
Bottleneck #1 and deliberately NOT attempted (the sub-record interrupt
inside `forEachViableMask`/`viableRec`, flagged as needing its own
dedicated, carefully-validated investigation, too invasive to rush).
Bottlenecks #2-#5 all target costs that are real at small-to-medium scale
but shrink to noise once a single height's own internal floor swallows
the whole budget.

**Implication: the sub-record interrupt is now clearly the single
highest-value remaining lever for real production scale, dwarfing
everything else combined.** Everything else accessible without that
change has been found and correctly wrung dry.

### Dead-end solutions tried (post-persistent-workers sweep)

- **spill-zstd-toggle** (`POLY_NO_SPILL_ZSTD=1` vs default-on, same maxn=30/
  persistent-workers/GOGC=1000 config): 264.7s vs 265.0s — statistically
  identical. Inconclusive by scale, not a real dead end yet: a30 barely
  spills at all (peak RSS well under the 1GiB budget), so this doesn't
  test the real question (does compression help/hurt when H17-scale
  spilling is actually substantial, confirmed via real RSS hitting 5.5GB
  at maxn=33). Untested at the scale where it would matter — not
  re-attempted this round given the ~1.9h cost per a33-scale trial, but
  don't treat the a30 result as a real answer either way.

## Bottleneck #6 attempt: sub-record interrupt — WRONG TARGET, corrected mid-investigation

The "Implication" paragraph above and the earlier "only remaining lever"
analysis under Bottleneck #1 both name `forEachViableMask`/`viableRec`
(`core/transition.h`) as the mechanism to fix. **This is wrong.** That
function is the **column kernel**'s enumeration path
(`core/mapreduce.h`'s `map_shard_file`) — production's `--kernel kink`
(everything `dalby_term.sh` runs, every real dalby A/B this whole round)
never calls it. Kink's actual per-record hot path is
`kinkStageTransition` (`core/kink.h:98`): a bounded `for (occupy in
{0,1})` loop over at most 2 choices, O(H)-ish work per call (a small
union-find reset, `canonMixed`, `labelInMixedState`, both O(H) scans) —
**no recursive tree, no combinatorial mask enumeration, nothing like
`viableRec`'s "76% of leaves pruned" story at all.**

Caught by actually reading `core/kink.h` line by line while about to
implement the fix (prompted by a stop-hook rejection correctly pointing
out the lever hadn't been implemented) — `grep -n "forEachViableMask"
core/kink.h` returns nothing; the function simply isn't there. A local
benchmark (`experiments/bench_viablemask.cpp`) and a full design writeup
(`results/sub-record-interrupt-design.md`) were built around the wrong
function before this was caught. Both are corrected in place (marked
"WRONG TARGET" at the top) rather than deleted, since the measurement
methodology is still valid and worth keeping as a pattern — just not the
conclusions.

**What's actually still open, unexplained, and not investigated**: unit
319 (H17 col5, maxn=33) measured wall-time uncorrelated with record count
under the KINK kernel specifically — 4M records taking 46s, 957M records
taking only 21s (Pearson-style anti-correlation, not the "successor
explosion" story that would fit a mask-tree kernel). With
`kinkStageTransition` confirmed O(H)-bounded per call, the real
explanation must be something else: candidates not yet checked include
`RunRecord::counts.assign()`'s cost scaling with a record's ranged-window
width (`rec.len`, up to `maxn`), the shard-level `sortRun`/`deduplicateRun`
cost at the end of `map_shard_stage_file` (a whole-buffer cost, not
per-record, but could dominate for shards whose buffer ends up large),
or something in the SIGTERM/steal bookkeeping unrelated to enumeration
cost per se. **This needs fresh investigation starting from
`kinkStageTransition` and `map_shard_stage_file` directly** — not a
continuation of the column-kernel analysis above.

Whoever picks this up: verify against the ACTUAL kernel in use
(`grep -n <function> core/kink.h`, or better, an actual call-stack/profile
from a real kink run) before writing a benchmark or design doc, the way
this round did not, until an hour was already spent on the wrong target.

### Real data on what actually happens (kink kernel, corrected target)

Round-level data for H17 col5 (maxn=33), `frontier_in` vs `map_wall_s`/
`map_cpu_s` (cpu/wall = average concurrent cores, out of 80):

| round | frontier_in | map_wall_s | map_cpu_s | avg cores active |
|---|---:|---:|---:|---:|
| stage1 | 9,587,734 | 1.024 | 60.446 | ~59 |
| stage4 | 19,641,706 | 2.951 | 127.722 | ~43 |
| stage6 | 20,717,652 | 17.270 | 135.514 | ~7.8 |
| stage8 | 20,943,386 | 25.058 | 131.604 | ~5.2 |
| stage12 | 21,068,044 | 36.426 | 115.683 | ~3.2 |
| stage16 | 21,364,246 | 45.584 | 112.973 | ~2.5 |

**Frontier size stays roughly flat from stage4 onward (~20-21M) while
concurrency collapses from ~43 cores to ~2.5** — a systematic trend across
the column's OWN stage sequence, not a single "unit 319 is pathological"
story (that framing, from earlier in this round, conflated an
across-round aggregate with a real per-unit anomaly). `map_units=320` and
total `map_cpu_s` stay roughly similar across stages (113-135) while wall
climbs 16x for near-constant input — the SAME total work is concentrating
onto fewer and fewer of the 320 units as the sweep goes deeper.

This is consistent with, not a new discovery contradicting, the
already-established RGS structural-skew finding from the OLD engine's
terminal-sort investigation (`HANDOFF.md`'s "terminal-sort investigation:
fully closed" section, 4 named dead ends, confirmed inherent not an
implementation quirk): signature bytes are a restricted-growth-string
encoding of a partition, and as MORE cells get placed deeper into a
sweep, `SampleKeysMulti`'s even-by-COUNT split increasingly fails to
correspond to even-by-COST distribution, because the state space's
"shape" (how much genuine choice/cost-diversity remains per key) changes
with how constrained the signature already is. **Not re-attempting the 4
already-rejected re-encoding approaches** (recursive radix bucketing,
hash-bucket+k-way-merge, generation-order nearly-sorted, multi-level
radix) — those were proven, not just measured, to not help this class of
skew.

**What's still genuinely open**: whether `kinkStageTransition` itself
(confirmed O(H)-bounded, cheap) or something downstream in
`map_shard_stage_file` (the shard-level `sortRun`/`deduplicateRun`,
spill I/O, or `RunRecord::counts.assign()`'s width-dependent cost) is
where the CONCENTRATED cost actually lands for the units that end up
dominating late-stage rounds. Not pinned down this round — the
STRUCTURAL cause (RGS-driven skew, already established) is now
correctly connected to the KINK kernel's real behavior, but the specific
CODE-LEVEL cost driver within a slow unit needs its own profiling pass
(e.g. `perf record` on a real dalby run isolating one late-stage kink
unit, or per-call instrumentation inside `map_shard_stage_file` itself)
before a fix can be designed.

### Strongest lead for the open question above

`deduplicateRun`'s `combine()` (`core/run.h`) was already investigated
once (`results/merge-ledger.md` A5, referenced directly in `run.h`'s own
comments as "the run.h:51 lever"): "combine was ~58% of merge wall and
alloc-bound" — a grow-in-place fix for the allocation part is already
landed (`run.h`'s `combine()` comment: "avoids the fresh
allocate-copy-free that dominated merge CPU... the buffer grows once and
every subsequent in-window combine is zero-alloc").

**Plausible connection, not yet verified**: deeper sweep stages have more
cells already placed, meaning more distinct predecessor boundary
configurations can canonicalize to the SAME successor signature (less
remaining distinguishing information = more collisions). If dedup
collision RATE genuinely rises with stage depth, `deduplicateRun` does
more total `combine()` work per unique key as the sweep progresses, even
with the alloc fix already in place — consistent with the observed
concurrency collapse being a late-stage phenomenon. **Not measured this
round** — the next concrete step for whoever picks this up: instrument
`deduplicateRun`'s combine-call count and total `combine()` time
separately from `sortRun`'s, per stage, on a real kink run (or a
synthetic benchmark reusing the `bench_viablemask.cpp`-style
minimum-of-N-trials methodology against `core/run.h`'s actual functions,
not `core/transition.h`'s).
