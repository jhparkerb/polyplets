# The reach-merged frontier, counted: H = 14 and H = 15 measured, and what stops at 16

2026-08-23, executing `docs/time-at-the-bar.md` A1.1. Binary
`cpp/nkey_census.cpp`, run on dalby via `scripts/nkey_census_ladder.sh`, both
gates green before every reported height.

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

| H | classes | ratio | wall | peak RSS |
|---|---|---|---|---|
| 4–12 | 8 … 8,539 | — | — | — |
| 13 | 21,355 | 2.5009 | seconds | — |
| **14** | **53,763** | 2.5176 | 293 s | 17 MB |
| **15** | **136,145** | 2.5323 | 1,960 s | 35 MB |
| **16** | **346,539** | 2.5454 | 10,454 s | 80 MB |

H = 17 is in flight and had passed 886,106 classes after 4.1 h, so it will land
above 2.55 as well.

Wall times exclude the gate ladder, which runs before every height and costs
84 s. H = 14 and H = 15 are new; everything at or below 13 was already banked,
by the Python probe `experiments/skeletonkey/nfamily_merge.py`, and is
reproduced here as a gate.

**The extrapolation is good and it keeps being wrong.**
`docs/time-at-the-bar-report.md` projected 53,777 at H = 14 from the ratio
ladder through H = 13; measured **53,763**, 0.026% out. Re-anchored on H = 14
and H = 15, the same method projected 346,533 at H = 16; measured **346,539**,
0.002% out and this time *under* rather than over. Two heights, two directions,
both inside a thousandth — which is what a decelerating-increment fit does when
it is close to right and is exactly why it is not a substitute for the count.

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

## Where it stops, measured rather than assumed

Wall time per height: 293 s at H = 14, 1,960 s at H = 15, 10,454 s at H = 16 —
ratios of **6.7 and 5.3**, so the cost ratio decelerates too. At 5.0 per height
from here, H = 17 is ~15 h, H = 18 ~3 days, H = 19 ~15 days. **This
implementation reaches H = 17 (in flight, 4.1 h in) and H = 18 for anyone
willing to spend a long weekend on it. It does not reach 21.**

The reason is structural rather than incidental: successors are generated per
source state, so a partial fill that could serve many sources is rebuilt for
each of them. The production engine does not have this problem — its carry
sweeps cells globally, so intermediate states are shared — and porting that
sharing here is what would make H = 18..21 affordable. That is a build, and it
is a decision rather than a foregone conclusion.

## What can and cannot be said about H = 21

**Cannot:** a measured number. The census reached 15 (16 in flight), not 21.

**Can:** the extrapolation is now anchored two heights further than the merge
file's, and its shape is unchanged. The ratio increments decay by about 0.88
per height — `+0.0219, +0.0194, +0.0167, +0.0147` at H = 12..15 — and carrying
that forward gives

| H | 16 | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|---|
| ratio | 2.545 | 2.557 | 2.567 | 2.575 | 2.583 | 2.590 |
| classes | ~3.5e5 | ~8.9e5 | ~2.3e6 | ~5.9e6 | ~1.5e7 | **~3.9e7** |

That is six steps of extrapolation from a two-parameter fit with no closed form
underneath it, and it agrees with the pre-census projection to within a percent
because it is the same fit with two more anchors. It is quoted to price a
decision, not to stand in for the count, and
`results/skeletonkey-nfamily-merge.md`'s refusal to quote an H = 21 number for
any other purpose stands.

**What it would mean if it held.** Tens of millions of classes at H = 21,
against the a(40) run's measured end-of-column frontier of 355,390,806 records
and 363.4 GB of disk. The merge is a state-space cut of about an order of
magnitude at that height, which is the thing worth knowing about the H = 20 and
H = 21 decisions — and it is exactly what a census that reached 21 would turn
from a lean into a number.

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
stands. H = 16 was produced by the pre-fix binary and is being re-run under the
corrected rule; H = 17 likewise.

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
    build/nkey_census --gate          # both ladders, 84 s
    build/nkey_census 14 15           # the new heights
    scripts/nkey_census_ladder.sh 14 21
