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

## Bottleneck #2: (not yet identified)

Next step: run a fresh whole-run/whole-column utilization profile with
overlap-heights deployed to see what now dominates idle time once the
Straggler Tail's recoverable component is captured.
