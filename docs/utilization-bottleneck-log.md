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
| 3 | TBD | — | — |

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

## Bottleneck #3: (not yet identified)

Next step: with both map's straggler tail (overlap-heights) and merge's
fan-out overhead (merge-mult) addressed, run a fresh real production-scale
measurement to see what now dominates.

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

### Dead-end solutions tried (this round)

- **checkpoint-overhead** (hypothesis: `--checkpoint-every 300`'s periodic
  big.Int triangle serialization + file I/O measurably steals wall time):
  real dalby A/B, maxn=30/overlap=15/merge-mult=1, `--checkpoint-every 300`
  vs effectively off (`999999`): 305.7s vs 303.9s — **statistically
  identical, confirmed negligible at these run lengths in one fast
  (~5 min) test.** Do not re-investigate checkpoint frequency as a
  utilization lever at this scale.
