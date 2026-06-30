# Scheduling / utilization — outcomes

How to keep all cores busy across the map→merge phase structure. Each column is
map (cores-wide) → barrier → merge (light, I/O-bound); each height is a serial
chain of such columns (col c+1's map needs col c's merge). Heights are
independent chains. Wall floor = the longest chain = the tallest swept height's
critical path (h16 for a(24)/a(25)).

## Measured (maxn18, gympie, 6 cores)

| Lever | Result |
|---|---|
| **overlap-heights** (sweep heights concurrently, shared pool) | **~18% wall** (30.0s → 24.5s), pure utilization (checkpoint-skip ruled out: seq with ckpt off is still 30.2s). The operative lever. |
| work-stealing (`--steal-grain`) | **~0** at this scale (30.0 vs 30.1) — no straggler to steal; and it's disabled under overlap anyway. May bite at a(25) scale (untested). |
| overlap depth | diminishing returns past ~2; overlap-all marginally best. |
| **big-first ordering** (tallest height launched first) | **no-op at overlap-all** (asc 25.3s vs desc 25.3s). Only bites when overlap-depth is capped BELOW the height count; irrelevant when all heights fit concurrently. |

## Why merge is not cores-wide (and overlap exists)

Merge is the light, I/O-bound half (combine + write of already-sorted,
range-partitioned data; seek-index reads only slices). It saturates with a few
workers (Amdahl + disk bandwidth), and its all-to-all nature means a single
column can't absorb all cores anyway. So during merge (and the map straggler
tail) cores idle — which is exactly the gap overlap fills with another height's map.

## Operative recommendation for a(24)/a(25)

**Per machine: `--overlap-heights = (number of swept heights it owns)`** — i.e.,
overlap them all. RAM is not a constraint: all a(24) swept frontiers co-resident
≈ <1 GB (h16 ~0.45 GB dominates; each lower height ≤0.42× the one above);
a(25) ≈ ~1–1.5 GB. Trivial on dalby's 122 GB. Ordering (big-first) is moot at
overlap-all but kept as defensively correct for any RAM-capped/larger-n case.

This is now **safe for a multi-hour run**: overlap mode writes
**height-boundary checkpoints** (the completed-height set + accumulated
triangle), so a crash resumes by skipping done heights and re-running only those
in flight — no restart-from-zero. (commit: height-boundary checkpoints.)

## The irreducible floor

Even at 100% bulk utilization, the wall can't drop below the tallest height's
serial column chain (h16). At the very end, when the cheap heights are done, h16
runs alone and its own merge/straggler idle is unrecoverable by *any* scheduler —
only finer within-h16-column splitting touches it, bounded by the all-to-all
merge (the lever measured-marginal at small scale; the a(25) endgame is where it
would actually matter, if anywhere). A dynamic dataflow queue would express the
priority more precisely than the coarse overlap semaphore, but the gain over
overlap-all + within-column units is the slice between "good" and "optimal"
backfill — bounded underneath by that same h16 chain, and not worth the
orchestrator rewrite pre-record.
