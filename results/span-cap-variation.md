# The span cap, indexed by final cluster: 1.86x at best, 1x on RAM

2026-08-22, executing `docs/last-orders.md` C2.1. Desk arithmetic on the
measured cost ladder and the engine's own span justification; no compute job.

## The variation, and why it is not the killed idea

`docs/lastditch-ideas.md` §2 killed a per-level span cap: capping row spans at
`2·ell + e` at each intermediate level ell is **9× faster, 5× smaller, and
undercounts** — 333 against 339 at `(e,k) = (0,2)`, K = 9. The counterexample is
`{0,3}` over `{1,2}`: connected, four cells, span 3 = cells − 1, but its first
row alone spans 3 with two cells. A prefix's span is bounded by the *final*
cluster's cell count, not its own.

`cpp/severance_w3_families.cpp` states the correct bound in its header: a
cluster of `l` rows and excess `e`, plus the p below and q above, has `2l+e+2`
cells, so every row spans at most `2l+e+1 ≤ 2K+EMAX+1`. The engine applies the
right-hand side — one global cap of 47 at K = 21, emax = 4.

The variation C2.1 proposed is the *left*-hand side, applied honestly: run the
DP once per target cluster size `l`, capping span at `2l+e+1` in that pass.
Each pass is then exact by the header's own argument, because within pass `l`
every cluster really does end at `l` rows. That is a different scheme from the
one that undercounted, and it is not excluded by that counterexample.

## What it can buy, bounded rigorously

The measured ladder (`results/lastditch-cost-ladders.md` §3, dalby, emax = 4)
is 12.2 s at K = 8, 71.4 s at K = 10, 265.0 s at K = 12 — a per-unit-K ratio of
**r = 2.159**. For a cost that grows geometrically in the level, the top level
alone is `1 − 1/r` of a whole run:

    top level's share    = 0.537
    everything below it  = 0.463

Pass `l = K` of the variation computes level K at span `2K+e+1`, which is
exactly what the current single run does. So

    variation_total  >=  W(K)  =  0.537 x current_total

and the **best possible saving is 1/(1 − 1/r) = 1.86×** — achieved only if
every level below the top became free, which it does not, since pass `l` still
pays for levels 1..l.

**On RAM it buys nothing at all.** The peak state set is level K at full span,
present unchanged in pass K. Depth 5's problem was believed to be memory —
103 GB asserted, 110–390 GB on the review's own decelerating-ratio reading
(`results/undertow-review-queue.md` L-2), against dalby's 125 GB. A time-only
1.86× does not move that.

**Correction, 2026-08-22.** Depth 5's memory was measured and it is
**~8.5 GB**, or 16.1 GB pessimistic (`results/depth5-cost-settled.md`). The
argument above is unaffected — a time-only saving still buys nothing on RAM,
and the span cap still undercounts — but the motivating pressure it was
answering does not exist.

## Why the tightening looks bigger than it is

The span reduction itself is real. Shapes of `t` cells with span ≤ s number
exactly `C(s, t-1)`, so dropping the cap from 47 to 41:

| cells per row | shapes at 47 | at 41 | ratio |
|---|---|---|---|
| 4 | 16,215 | 10,660 | 0.657 |
| 5 | 178,365 | 101,270 | 0.568 |
| 6 | 1,533,939 | 749,398 | 0.489 |
| 8 | 62,891,499 | 22,481,940 | 0.357 |

A 2–3× cut in row placements at the sizes that matter — which is why the idea
looks attractive, and why the killed version measured 9× before it was found to
be wrong. But those factors apply at **low** `l`, where the cap is tight and
the work is small. At `l = K` the cap is `2K+e+1` either way and the ratio is 1.
The cost is concentrated exactly where the tightening cannot reach.

## Verdict

**Dead, and dead for the same structural reason as the original** — the
top level dominates and its span cannot be tightened — reached by a different
route, which is worth recording because the original kill was a correctness
argument and this one is a cost argument. The two are independent.

The accounting test from `docs/skeletonkey-reprompt.md` applied here cost one
paragraph of arithmetic against a measured ladder, which is what that test is
for. No compute was spent, and none should be: a scheme whose ceiling is 1.86×
on the axis that is not binding does not justify a K-pass restructure of a
gated engine.

## What would change this

Only a cap that tightens the **top** level. The header's bound at `l = K` is
`2K+e+1` and is tight — a K-row cluster with excess e really can have a row
spanning that far. Reducing it needs a different invariant, not a different
indexing of this one.
