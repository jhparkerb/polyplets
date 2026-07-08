**CORRECTION (same session, found ~20 min after writing this doc): the
entire analysis below targets the wrong function.** `forEachViableMask`/
`s8::viableRec` (`core/transition.h`) is the **column kernel**'s
enumeration mechanism (`map_shard_file`, `core/mapreduce.h`), which
production does **not** use. `--kernel kink` (what `dalby_term.sh` and
every real dalby run in this round actually ran) uses
`kinkStageTransition` (`core/kink.h:98`) instead — a simple `for (occupy
in {0,1})` loop, **O(1)/O(H)-bounded per call, no recursive tree, no
combinatorial mask enumeration at all**. There is no analog of
`viableRec`'s "76% of leaves pruned, dominant cost is the descent" story
in the kink kernel's actual hot path. The ~10.7% overhead number and the
"no clean resume cursor for a partial tree" problem below are real
findings **about the column kernel**, which is not the bottleneck anyone
is trying to fix here. Kept below for the record (the methodology --
local throwaway benchmark before touching dalby -- is still the right
approach) but **do not act on the numbers or conclusions as if they
apply to `--kernel kink`.** The real question -- what in
`kinkStageTransition`'s O(H)-bounded per-record path (or elsewhere in
`map_shard_stage_file`) causes unit 319's measured 100x+ wall-time
variance at similar-to-lower record counts -- is open, not this.

---

# Sub-record interrupt: measured cost, and why it's not a quick fix (WRONG TARGET, see correction above)

**Status: measured and scoped, NOT implemented.** This is the design/cost
analysis for the highest-value remaining utilization lever
(docs/utilization-bottleneck-log.md), done with a local, throwaway
benchmark (`experiments/bench_viablemask.cpp`, not wired into any gate) so
the cost question could be answered in seconds rather than a multi-hour
real dalby A/B, per the "tighten the feedback loop" push earlier in this
round.

## The problem, restated precisely

`core/kink.h:296`'s cooperative-stop check (used by work-stealing) fires
only **between records** (every 1024 consumed). A single pathological
record's own successor enumeration (`forEachViableMask` ->
`s8::viableRec`, `core/transition.h`) can dominate a unit's wall time, and
no scheduling change can interrupt it mid-enumeration. Real production
data (maxn=33, H17 col5) confirmed the same unit (319, the last open-ended
key range) topping the cost ranking in 9 of 10 sampled rounds, with wall
time uncorrelated to record count (4M records -> 46s; 957M records -> 21s)
-- the cost is which specific states landed in that range, not how much
input it got.

## What was measured

Two candidate check placements, benchmarked on a representative H=20
boundary signature (2.09M tree nodes / 1.04M emitted masks per call, a
~2.0x node-to-leaf ratio -- pruning cuts most branches early, so the tree
isn't wildly larger than the leaf count):

| Placement | Overhead vs baseline | Actually interrupts a pathological record? |
|---|---:|---|
| Lambda-level (per emitted mask, in the caller's callback) | ~3.5% (2.49 -> 2.58 ns/call) | **No** -- returning from the lambda doesn't stop `viableRec`'s sibling branches. The tree walk itself continues to completion regardless. |
| Recursion-level (inside `viableRec`, one added line at function entry) | **~10.7%** (2.49 -> 2.76 ns/call) | Yes -- this is the placement that actually aborts the walk. |
| Counter-gated (check every K=16..1024 leaves, lambda-level) | ~13-17% -- **worse than checking every time** | No (same lambda-level limitation) |

**The counter-gating result is itself informative**: `g_terminate` is a
`volatile sig_atomic_t`, already about as cheap as a check can be (one
load, no atomics, no syscall) -- cheap enough that the counter
increment/mask/compare needed to gate it costs MORE than just checking it
unconditionally. Don't build a stride/counter mechanism for this if it's
ever revisited; check every call.

## Why 10.7% is a real number, not a rounding error

Applied uniformly to every record's enumeration, everywhere, all the time
-- not just the pathological ones. At maxn=33 real scale, map's share of
the run's 55,825 cpu-seconds is roughly 60% (~33,000 cpu-s); a 10.7%
enumeration-wide slowdown costs on the order of 3,500 additional
cpu-seconds. Most of that likely lands on already-idle cores (H17's
measured utilization is only ~5-10%, so there's real spare capacity to
absorb it without touching wall time) -- but the units that sit ON the
critical path (the ones gating when a column can finish) pay it directly,
including the pathological unit itself while it's still doing its own
(now slower) enumeration before any interrupt could even trigger. Whether
the net effect is a wall-clock win depends on whether the eventual
interrupt+steal saves more than the check costs on that critical path --
genuinely uncertain without trying it, not a foregone conclusion either
way.

## The harder problem underneath: what does "resume" even mean here?

The check-cost question turned out to be the EASY part. The current
between-records interrupt has a clean semantic: the worker stops at a
record boundary and reports a `stop_key` cursor (an already-sorted-by-key
position); a fresh unit picks up `[stop_key, hi)` and re-enumerates from
there -- no missing or duplicated work, because records are processed
in a defined key order and "everything before the cursor is done, at a
record granularity" is a coherent, checkable invariant.

A MID-record interrupt has no equivalent clean boundary. `viableRec` is a
**pruned binary recursion tree** over which cells get occupied (r=0..H-1,
each a 0/1 branch) -- "I got partway through" doesn't correspond to a key
position at all, it corresponds to a specific point in an in-progress
tree traversal (which branches were already visited, which were pruned,
which remain). To correctly resume:

- The resumer would need to reconstruct enough tree-position state to
  continue enumerating the REMAINING masks without re-emitting ones
  already processed (duplicate would double-count a successor
  contribution) or skipping ones not yet reached (would silently
  undercount).
- The pruning logic (`cov | sufSup[r] != all`, the `topReach` budget cut)
  is data-dependent on the ancestor path, not just a linear position --
  there's no simple "resume mask" to hand off, unlike a sorted-key cursor.
- Getting this wrong doesn't crash or error -- it silently produces a
  wrong `a(n)`, the worst failure mode for a project whose whole output
  is exact integer sequences. This is exactly the shape of bug that
  wouldn't be caught by `--compare` against SMALL known values (a subtly
  wrong partial-tree resume might only manifest at the frontier sizes
  large enough to trigger a real mid-record interrupt in the first place
  -- i.e. exactly the untested-at-small-scale regime).

## Conclusion

Not a "add one check" fix. It's two problems stacked: a real but
tolerable ~10.7% enumeration-wide cost (now measured, not guessed), and a
genuinely hard correctness problem (defining and safely resuming a partial
tree-traversal state) that has no existing analog in this codebase to
crib from. Implementing it properly needs: a precise resume-state design,
a red-first test that actually exercises a forced mid-record interrupt
(not just a between-records one, which the existing gates already cover),
full gate + ASan validation, and a real dalby A/B measuring the NET
wall-clock effect (not just the enumeration overhead) before it could be
trusted for a real term. Scoped as a dedicated follow-up, not attempted
further this round -- the risk of a silent wrong-answer bug, at this hour
in an already very long session, outweighs finishing it now.
