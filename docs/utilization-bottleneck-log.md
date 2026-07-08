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
| 1 | Straggler Tail | partially solved | overlap-heights: +9pp on measured H16+H17 pair (24.7%->33.0%), full-sweep deploy pending |
| 2 | TBD | — | — |

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

## Bottleneck #2: Map/Merge Round Serialization (candidate, under test)

Exact per-unit instrumentation (`POLY_UNIT_LOG=1`, `scripts/analyze_unit_concurrency.py`
— see Measurement tooling below) on a real maxn=26 column showed: within a
single height's own round sequence (seed, stage0..stageN, finalize), map-unit
concurrency is high while map units are actually running (mean ~45/80 cores
during active map time) but **map is only active ~22% of a column's wall** —
the other ~78% is inter-round merge, where map concurrency is exactly zero
(H13 col4: active_time=0.88s of 4.09s span, gaps up to 0.3s each, 14 gaps).

This is very likely NOT a new bottleneck — `results/scheduling.md` already
names and explains this exact mechanism ("Why merge is not cores-wide (and
overlap exists)") and its own recommendation is **`--overlap-heights =
(number of swept heights owned)`**, i.e. overlap ALL heights, not a small
fixed number. Bottleneck #1's deployed fix used `--overlap-heights 2`
(the only pair actually measured in `utilization-fix-and-ceiling.md`), which
is far more conservative than this doc's own prior recommendation.
**Currently testing**: real maxn=29 benchmark run (`runs/ns_a29_bench`,
~20-25 min, current production config) as the reference; next step is the
same config swept with `--overlap-heights` set to the full owned-height count
to see whether raising it past 2 recovers more of this gap. If it does, this
folds into Bottleneck #1's overlap-heights fix (a config change, not new
code) rather than being its own bottleneck #2 — will reclassify after the
comparison.

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
