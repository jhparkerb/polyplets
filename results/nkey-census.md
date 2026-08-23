# The reach-merged frontier, counted: H = 17 measured, and the method that stopped has been replaced

2026-08-23, executing `docs/time-at-the-bar.md` A1.1. Binary
`cpp/nkey_census.cpp` — two engines, `scripts/nkey_census_ladder.sh` and
`scripts/nkey_census_shared_ladder.sh` — run on dalby, every gate green before
every reported height.

## What A1.1 asked for

`results/skeletonkey-nfamily-merge.md` establishes that two strip states are
equivalent iff they carry the same multiset of block neighbourhoods, and that
the merged set is exactly the end-of-column frontier `results/kink-carry.md`
names as the engine's wall. It then **refuses to quote a class count at
H = 21**, correctly: the ratio compounds with no closed form, no OEIS match on
`8, 19, 43, 101, 239, 575, 1399, 3441, 8539`, and no recurrence with surplus.

A1.1's item was to replace that extrapolation with a measurement, because the
two soft spots `results/confidence.md` names — the H = 20 sweep that would turn
`P_21` into a holdout, and the H = 21 cell that never fitted — are both priced
against this frontier.

## The measurement

| H | classes | ratio | wall (per-source) | wall (shared) |
|---|---|---|---|---|
| 4–12 | 8 … 8,539 | — | — | — |
| 13 | 21,355 | 2.5009 | seconds | 2.3 s |
| **14** | **53,763** | 2.5176 | 293 s | 7.9 s |
| **15** | **136,145** | 2.5323 | 1,960 s | 25.3 s |
| **16** | **346,539** | 2.5454 | 10,454 s | 103.8 s |
| **17** | **886,111** | 2.5570 | not run | **235.7 s** |
| **18** | **2,275,103** | 2.5675 | not run | **705.0 s** |
| **19** | **5,862,925** | 2.5770 | not run | **2,114.5 s** |
| **20** | **15,159,215** | 2.5856 | not run | **6,430.3 s** |
| **21** | **39,314,963** | 2.5935 | not run | **17,532.6 s** |

H = 17 is new and was produced by the second engine below. The extrapolation
that priced it from H <= 16 said the ratio would be **2.557**; measured,
2.5570.

**H = 18 through 21 landed 2026-08-23**, rev `252921b10`, on dalby, in one
ladder of 7 h 20 min wall (`dalby:~/var/nkey-shared-18up/census.txt`). The full
gate ladder — the king class counts to H = 13, the rook RED control, and the
cross-engine successor-SET check on both adjacencies — ran green before every
one of the four heights, 148 checks with nothing outside `ok`. **This closes the
open item that `docs/state-2026-08-23.md` §5 called "the frontier census past
H = 17": the H = 20 and H = 21 decisions now have a measured frontier rather
than a six-step extrapolation.**

Wall times exclude the gate ladder, which runs before every height. H = 14
through 17 are new; everything at or below 13 was already banked, by the Python
probe `experiments/skeletonkey/nfamily_merge.py`, and is reproduced here as a
gate.

**The extrapolation is good and it keeps being wrong.**
`docs/time-at-the-bar-report.md` projected 53,777 at H = 14 from the ratio
ladder through H = 13; measured **53,763**, 0.026% out. Re-anchored on H = 14
and H = 15, the same method projected 346,533 at H = 16; measured **346,539**,
0.002% out and this time *under* rather than over. Through H = 16 it put the
H = 17 ratio at 2.557; measured, 2.5570. Three heights, both directions, all
inside a thousandth — which is what a decelerating-increment fit does when it is
close to right and is exactly why it is not a substitute for the count.

## Gates

Both fail-closed, both run before any height is reported, and the binary
refuses to report one if either fails.

- **king** — the class counts must be `8, 19, 43, 101, 239, 575, 1399, 3441,
  8539` at H = 4..12 (`results/skeletonkey-nfamily-merge.md`, and Exact
  Change's independent `minauto` at H = 12) and `21,355` at H = 13. All ten
  reproduced.
- **rook, the RED control** — with the `±1` dilation switched off the key
  degenerates to the state, so the count must be the raw frontier
  `Motzkin(H+1) − 1` exactly. It is, at H = 2..10: `3, 8, 20, 50, 126, 322,
  834, 2187, 5797`.

## The algorithm, and the version that was too slow

The Python probe iterates all `2^H` column masks per state, which cost 962 s
and 18 GB at H = 13 and puts H = 14 over an hour. This sweeps the column one
row at a time, deduplicating partial fills at each row.

The first version of that was **still too slow** — 3 m 49 s for the gate ladder
alone — because a partial fill kept the full identity of every group it had
formed, so two fills that differed only in already-decided history stayed
distinct. The fix is to retire a group as soon as no later row can reach any
old block it attaches to: after that its identity cannot matter, only its
dilated mask, so it drops into a plain sorted multiset and the two fills
collapse. Same gates, 1 m 24 s.

## Where the first engine stops, measured rather than assumed

Wall time per height: 293 s at H = 14, 1,960 s at H = 15, 10,454 s at H = 16 —
ratios of **6.7 and 5.3**, so the cost ratio decelerates too. At 5.0 per height
from there, H = 17 is ~15 h, H = 18 ~3 days, H = 19 ~15 days. **That
implementation reaches H = 17 and H = 18 for anyone willing to spend a long
weekend on it. It does not reach 21.**

The reason is structural rather than incidental: successors are generated per
source state, so a partial fill that could serve many sources is rebuilt for
each of them. The production engine does not have this problem — its carry
sweeps cells globally, so intermediate states are shared.

## The second engine: the partial fills shared between sources

`nkey_census --shared`. A whole batch of source keys is swept together, one row
at a time, and the state carries only what the remaining rows can still see:
each old block's dilated mask restricted to rows at or above the sweep, beside
the partial-fill structure the first engine already used. Two sources that
differ only below the sweep are then the same state and their remaining work is
done once.

A block is dropped only when nothing can reach it again — no later row attaches
to it, **and** the run in progress does not hold it. Both halves are needed;
leaving the second out is the merge failure `384bd2e` fixed, in a new place.
A block dropped without ever having been touched strands a component and that
column is dead, which is the first engine's `touched != allOld` test.

**Measured against the first engine on the same box**, at the same heights,
reproducing every banked value: **37x at H = 14, 77x at H = 15, 101x at
H = 16**. Peak RSS 38.9, 95.1, 238.6, 578.5, 1,448.3 MB at H = 13..17 — a ratio
of about 2.47 per height, which is the class count's own growth, so the memory
is the reachable key set and not the sweep.

**The batch cap was costing half the speed and buying nothing.** `--batch` was
introduced to bound the sweep front. At H = 17: batch 131,072 is 505.3 s and
1,429 MB, unbatched is **235.7 s and 1,448 MB**. Twice the speed for 1.4% more
memory, because the memory is the key set. The default is high now and the flag
is an escape hatch for a height that actually runs out.

### The gate, and why count agreement was not enough

Both engines run the banked king ladder and the rook RED control before any
height is reported. That is not sufficient on its own, and this was checked
rather than assumed: **disabling the stranded-block prune leaves every banked
class count intact**, because the successors it invents are already reachable
by another route. A control a real defect walks through is not a control.

So `--gate` also compares the two engines' **successor sets per source**, at
every reachable key, for H <= 11 king and H <= 9 rook. Five planted changes:

| planted | class counts | successor sets |
|---|---|---|
| drop a block the open run still holds | FIRES | FIRES |
| allow a stranded block | silent | **FIRES** |
| retire a group the open run can merge with | FIRES | FIRES |
| block masking off (optimisation only) | green | green |
| canonical relabelling off (optimisation only) | green | green |

The last two are the soundness argument for the sharing: a labelling that fails
to canonicalise costs duplicated work and never a wrong count, because the
answer is a set of keys and every key is sorted before it is counted.

## What can and cannot be said about H = 21

**Cannot, yet:** a measured number. The census has reached 17. The H = 18..21
ladder is running on the shared engine, unbatched.

**What it now costs.** The shared engine's own ratio across H = 14..17 is 3.4,
3.2, 4.1, 4.9 batched; the one unbatched height measured is H = 17 at 235.7 s.
Carrying 4.9 forward from there — the least favourable of the four, and the
ladder will replace it with measurements — puts H = 18 at ~19 min, H = 19 at
~1.6 h, H = 20 at ~7.8 h and H = 21 at ~1.6 days, with RSS at the measured
2.47 per height reaching ~55 GB against dalby's 125. The first engine at its
own 5.3 would need roughly **475 days** for the same height. That is the whole
of what the second engine buys, and it is a constant factor of about a hundred
rather than a change of exponent.

**The extrapolation held for four more heights, and it is now retired.** It was
anchored through H = 16, predicted the H = 17 ratio at 2.557 against a measured
2.5570, and was carried on to H = 21. Against the measurements, each row chained
off its measured predecessor:

| H | 18 | 19 | 20 | 21 |
|---|---|---|---|---|
| predicted ratio | 2.567 | 2.575 | 2.583 | 2.590 |
| measured ratio | **2.5675** | **2.5770** | **2.5856** | **2.5935** |
| predicted classes | 2,274,647 | 5,858,390 | 15,143,935 | 39,262,367 |
| measured classes | **2,275,103** | **5,862,925** | **15,159,215** | **39,314,963** |
| error | +0.020% | +0.077% | +0.101% | +0.134% |

Seven heights now, all inside two parts in a thousand, with the error growing
monotonically and always in the same direction — the decelerating-increment fit
decelerates very slightly too fast. There is no longer any reason to quote it:
the numbers it was standing in for are measured.

**Two other projections in this file were wrong, and the way they were wrong is
the useful part.** The class counts were right to a thousandth seven times
running. The other two quantities were not.

- **Wall time was out by up to 8x, in the safe direction.** H = 18 was priced at
  ~19 min and ran in 11.7; H = 21 was priced at ~1.6 days and ran in 4 h 52 min.
  The error grows with height: 1.6x, 2.7x, 4.4x, 7.9x. The cause is known and is
  not a modelling failure — the projection was anchored on measurements taken
  with the sweep batch capped, and `252921b` removed the cap, which the same
  file records as worth 2x on its own. A projection outlives the build it was
  measured on.
- **The RSS ratio is not constant, and that is the one that binds.** This file
  assumed 2.47 per height and put H = 21 at ~55 GB. Measured: **3.60, 8.76,
  22.73, 63.21 GB** at H = 18..21, with the ratio *climbing* — 2.434, 2.596,
  2.781. Extending at the last measured ratio puts H = 22 at about **176 GB**
  against dalby's 125, so **this ladder stops at H = 21 on this hardware**, and
  it stops for memory rather than for time. Anyone extending it should re-derive
  the ratio rather than reusing 2.47, exactly as the depth-6 pricing had to stop
  treating its per-excess factor as constant
  (`results/depth6-cost-settled.md`).

**What it means, now that it is measured rather than assumed.** 39,314,963
classes at H = 21, against the a(40) run's measured end-of-column frontier of
355,390,806 records and 363.4 GB of disk. The merge is a state-space cut of
**9.04x** at that height. That was the thing worth knowing about the H = 20 and
H = 21 decisions, and it was previously a lean rather than a number.

## The retirement rule, and the check it needed

The compression above retires a group when nothing can reach it. The first
version tested that against the old blocks a *later row* can still attach to,
and left out the ones the *run in progress* has already attached to — so a
closed group and the open run could share an old block whose last row had just
passed, be one component, and be filed as two. Found by reading the code rather
than by any gate failing.

Fixed, and then checked rather than assumed: with the stricter rule the binary
reproduces **H = 14 = 53,763 and H = 15 = 136,145 exactly**, so the hazard is
real in the code and unreachable at these heights, and every number above
stands. **H = 16 = 346,539 is now confirmed post-fix by the second engine**,
which is a different algorithm and not merely a different build. **The
per-source re-run on ayr landed 2026-08-23 and returned 346,539 too**, so the
height now has the post-fix per-source engine, the shared engine and the
pre-fix binary all agreeing, and the retirement hazard is confirmed
unreachable at H = 16 by the slow route as well as the fast one. H = 17 was never produced
by the four-bit-era binary: the run that would have was stamped `a825ad114`,
which predates the fix, and it was stopped once the shared engine returned the
height in four minutes.

## What this does not settle

Unchanged from the merge file, and repeated so the item is not oversold:
whether the mid-column stage tables inherit the cut (the congruence is proved at
column boundaries only); what the telescope costs the completion prune; and
anything about wall clock in the production engine, since no engine change has
been written or timed. On Motley specifically the weaker statement is still the
right one: a merged-key automaton is an alternative producer of Motley's `C_H`,
which does not mean Motley's cancellation DP state admits the same cut.

## Reproduce

    make build/nkey_census
    build/nkey_census --gate          # BOTH engines' ladders + the cross-check
    build/nkey_census --shared 17     # the new height, ~4 min
    scripts/nkey_census_shared_ladder.sh 18 21
    scripts/nkey_census_ladder.sh 14 17   # the first engine, for comparison
