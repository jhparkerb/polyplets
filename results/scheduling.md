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
| work-stealing (`--steal-grain`) | **~0** at this scale, AND root-caused (see below) — not just "no straggler," but structurally blind below the progress-pulse stride. |
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

## Overlap+steal coexistence — fixed, but exposed a deeper issue

Stealing was **statically disabled whenever `OverlapHeights>1`** (the shared
pool's idle-core accounting wasn't height-local). That's overly conservative:
once every sibling height finishes — the common endgame, the dominant height
outliving its cheap siblings — that height becomes the pool's sole occupant and
local-idle == box-idle, exactly sequential mode's condition. **Fixed**: a dynamic
`activeHeights` counter, re-checked on every steal decision (not snapshotted once
at column start, since columns can run for hours), allows stealing once a height
is alone, blocks it while ≥2 heights share the pool. Byte-exact, full suite
green, unit-tested.

**But three real overlap+steal runs (maxn20, including a cleanly isolated
"H3 finishes, H13 runs alone for ~150s" scenario) showed ZERO steals fire** —
even with confirmed real ~2× per-unit compute imbalance present (one unit
burning 31 CPU-seconds vs siblings' 15–20s, near-identical output volume, so
NOT an output-skew effect — genuine per-key enumeration cost variance, exactly
the case `stealScore` is designed to rank). **Root cause: the progress-pulse
stride.** `core/mapreduce.h:341` emits a progress callback only every 2¹⁴=16384
*source* records consumed; `stealEligible` requires nonzero `processed` to size
a victim at all (`run.processed.Load() == 0` ⇒ ineligible, unconditionally). At
maxn20 col3, each of 8 units held ~11.8K input records — **below the stride**, so
`processed` never left 0 for any unit's entire lifetime, and the steal mechanism
had no signal to act on regardless of overlap.

**This isn't just a small-n artifact.** At a(24)/a(25) production scale (H16
frontier ≈ 4.7M, 256 units on dalby) each unit holds ≈18.4K records — only
**~1.1× the stride**. A unit there gets at most 0–1 progress pulses in its entire
run, leaving the same blind spot — the real explanation for "work-stealing does
~nothing" all session, superseding the earlier "no straggler at this scale" guess.

### Fixed — stride lowered 16384 → 1024, with a real measured payoff

Microbenchmarked first: the bitmask check + occasional `wallSeconds()` poll cost
the **same** (~0.7–0.85 ns/record, noise-level) from stride 2¹⁴ down to 2⁶ — the
perf concern that justified the old large stride was unfounded, so there was no
real tradeoff to make. Lowered to **1024** (named `kProgressStrideMask`,
core/mapreduce.h), with a compile-time tripwire (`static_assert ≤ 4096`,
verified to actually fire against a regression) so it can't silently regress.

**Live effect on the exact isolated H3+H13 scenario**: steals went from **0 →
15**, concentrated exactly on H13's lone columns. **Wall-clock A/B (3 reps,
steal off vs on, same scenario, fixed stride): 151.4s → 98.5s — a real 35%
reduction (1.54×).** Byte-exact throughout (a14, a18, full a(20) `--compare`
with overlap+steal+the new stride all active). Work-stealing is no longer a
dead lever — it was blind, not ineffective, and once given a usable signal it
delivers a substantial win on a dominant-height-alone scenario, the exact
shape of a(24)/a(25)'s endgame.

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
