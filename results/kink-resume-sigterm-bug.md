# Kink kernel real-SIGTERM + resume: wrong a(n) values (FIXED 2026-07-09)

**Found:** 2026-07-08, while validating the persistent-workers change
(docs/utilization-bottleneck-log.md Bottleneck #5). **Confirmed pre-existing**
— reproduces identically on a clean checkout with none of this session's
changes applied, so it is not something the persistent-workers work
introduced.

## Resolution (2026-07-09)

**Root cause.** `sweepHeightKink` folded each column's seed-round completions
into the running height row `hTri` immediately after the seed round, *before*
the column's stage + finalize rounds ran. But every mid-column checkpoint —
the ctx-cancel path at the top of the loop and the three per-round error paths
— stamps `Col = col-1` and saves the *pre-column* input frontier. So if a
SIGTERM landed after the seed round but before the column finished (the large
majority of a column's wall time: the H stage rounds + finalize), the
checkpoint's saved triangle already included column `col`'s seed contribution
while its `Col` field claimed only `col-1` was done. On resume the sweep
restarted at `col` from the input frontier, re-ran the seed round, and counted
`col`'s completions a **second** time — a consistent over-count from the killed
height upward, exactly as observed.

The overlap path (`--overlap-heights`, production `dalby_term.sh`) was never
affected: it checkpoints only at height boundaries via a completed-height SET
and re-runs any in-flight height from scratch, so it never trusts a partial
`hTri`. The bug was specific to the sequential single-height resume path.

**Fix.** Defer the `addTriContribs(hTri, triContribs, ...)` fold until *after*
the finalize round succeeds (orchestrator/sweep.go), so `hTri` only ever
contains fully-completed columns and every mid-column checkpoint's saved
triangle is consistent with its `Col = col-1`.

**Gate.** `orchestrator/kink_resume_midcolumn_test.go`
(`TestKinkResumeMidColumn`, wired into `ns-gate-resume-boundaries`) kills the
run mid-column via a new `afterSeedRound` test seam, resumes, and asserts the
triangle. RED before the fix (`n=3 a(n)=21 known=20`), green after. The real
subprocess SIGTERM repro below now passes 5/5 (failed every time before).

---

## Original report (preserved)

## Repro

```
rm -rf /tmp/kink_resume_bug && mkdir -p /tmp/kink_resume_bug/spill
./build/ns/orchestrate --maxn 20 --kernel kink --counter u64 --cores 4 \
  --ram 67108864 --unit-mult 4 --merge-mult 1 --checkpoint-every 300 \
  --run-dir /tmp/kink_resume_bug --spill-dir /tmp/kink_resume_bug/spill \
  --checkpoint /tmp/kink_resume_bug/POLYCKPT &
PID=$!
sleep 0.6
kill -TERM $PID
wait $PID

./build/ns/orchestrate --maxn 20 --kernel kink --counter u64 --cores 4 \
  --ram 67108864 --unit-mult 4 --merge-mult 1 --resume \
  --run-dir /tmp/kink_resume_bug --spill-dir /tmp/kink_resume_bug/spill \
  --checkpoint /tmp/kink_resume_bug/POLYCKPT --compare
```

## Symptom

`--compare` against `fixtures/b006770.txt` fails from roughly n=8 onward
(exact first-failing n varies run to run, timing-dependent), always with the
resumed value **higher** than the known-correct value — a consistent
over-count pattern, not random corruption. Lower n (below wherever the kill
landed) match exactly; the divergence starts at or near the in-flight
height/column at kill time and propagates upward (later n's depend on
earlier heights' contributions, consistent with one height's row being
double-counted or a partial column's contribution being folded in twice).

Reproduced 3 times (varying kill timing ~0.3-0.6s, varying
`--checkpoint-every` from 0.001 to 300): fails every time, at a
timing-dependent but always-nonempty set of n values.

## What's ruled out

- **Not caused by the persistent-workers change** (`--persistent-workers`
  flag, `orchestrator/workerpool.go`): reproduces byte-for-byte identically
  with that flag omitted, exec-per-unit path, no pool involved.
- **Not caught by the existing resume gate**
  (`ns-gate-resume-boundaries` -> `TestKillResumeAllBoundaries`): that test
  passes clean. It exercises resume via a controlled in-process test-seam
  callback (`cfg.afterColumn`), not a real `SIGTERM` delivered to a real
  subprocess at an unpredictable moment, and does not appear to specify
  `--kernel kink` (defaults to the column kernel). Real production usage
  (`scripts/dalby_term.sh`) sends a real SIGTERM to a real kink-kernel
  process and resumes from that checkpoint -- the actual production path
  is not what the passing gate validates.

## Why this matters

`dalby_term.sh` supports `--resume` and real production runs have been
killed and resumed before (SIGTERM/SIGINT handling exists specifically for
this). If this bug is real under production conditions (not just this
rapid small-maxn repro), any historical run that was interrupted and
resumed could have a silently wrong banked value. **Not yet checked**
whether any currently-banked `results/ns_a*/` term was ever actually
computed via an interrupted-and-resumed run (most large runs completed in
one shot per their PROVENANCE.md wall-time notes) -- this needs auditing
before treating any specific banked value as suspect, not assumed.

## Next steps (not started)

1. Audit `results/ns_a*/PROVENANCE.md` for any run that mentions a
   kill/resume cycle during the actual production computation (as opposed
   to a deliberate resume-gate test) -- confirm whether any banked term is
   actually exposed to this.
2. Extend `TestKillResumeAllBoundaries` (or add a sibling test) to cover
   `--kernel kink` explicitly and/or drive a real subprocess with a real
   SIGTERM at multiple randomized timings, since the in-process callback
   seam clearly doesn't reach whatever state window causes this.
3. Bisect the timing: does the double-count happen only when SIGTERM lands
   mid-round (between map and merge), only at a column boundary, or
   anywhere? The kink kernel's own per-round checkpoint state
   (`writeCheckpoint(H, col, frontier, hTri)` combining the outer `triangle`
   with the current height's partial `hTri`) is the most likely place a
   partial contribution gets folded in twice on resume.
