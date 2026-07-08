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
