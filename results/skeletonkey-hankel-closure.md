# The transfer floor grows at 2.43, not 3, and both extrapolations missed

2026-08-21, branch `skeletonkey`. Probe `scripts/probe_hankel_rank2.py`, run on
ayr, exact closure mod `p = 2^31 - 1` (not sampling), gated against every
banked point of the ladder.

## The question

The incumbent column transfer carries `Motzkin(H+1) - 1` states, growing by a
factor of 3 per height; that count is the wall above H = 21. The observability
dimension of the same automaton is the *floor* on how many quantities any
method of this shape must carry across the cut. Whether the compressed-transfer
family (breadth candidate #3, `docs/skeletonkey-reprompt.md`) can ever pull
ahead of the incumbent turns on one comparison: does that floor also grow at 3,
or slower?

A-S1 (`git show second-source:results/scaling-exploration-A.md`) measured the
ladder to H = 10, independently reproduced by lane C:

    H     4    5    6    7    8    9   10
    dim   6   17   35   88  204  501 1217

Seven points admit two readings, which disagree at H = 11 by 6.2%:

| reading | H = 11 | consequence |
|---|---|---|
| power-law quotient, floor base exactly 3 | 3091 | class closed — no compressed method ever wins |
| geometric quotient, floor base ~2.79 | 3281 | a real opening |

## The measurement

Two independent `x` weights, 16h31m and 16h38m single-core on ayr, 7.6 GB each:

    11 : 15510 states : x=1         : 3016
    11 : 15510 states : x=123456789 : 3016

**3016.** Below both extrapolations — 75 under the power-law reading, 265 under
the geometric one. Neither fit shape survives its own prediction.

## Gate

`--anchor` reproduces the small end, and H = 8, 9, 10 were re-derived by this
code against A-S1's independently measured values:

    H=4  states=20    dim=6     banked=6     ok
    H=5  states=50    dim=17    banked=17    ok
    H=6  states=126   dim=35    banked=35    ok
    H=7  states=322   dim=88    banked=88    ok
    H=8  states=834   dim=204   banked=204   ok
    H=9  states=2187  dim=501   banked=501   ok
    H=10 states=5797  dim=1217  banked=1217  ok

All seven banked points reproduced, three of them at real scale. Two seeds
agreeing at H = 11 rules out an unlucky prime; the anchor rules out a wrong
automaton.

## What the eight points say

Refitting a pure geometric law over the tail:

| window | base |
|---|---|
| last 4 points | 2.4518 |
| last 5 points | 2.4241 |
| last 6 points | 2.4289 |
| all 8 points  | 2.4051 |

and the last three quotients are 2.4559, 2.4291, 2.4782. The base sits near
**2.43** and is stable across every fit window.

2.43 is well below the incumbent's 3. The floor grows strictly slower than the
transfer it bounds, so the gap widens with every height, and the "class closed"
reading is the one that dies.

## What this does not settle

A growth rate is not an engine. The headroom this establishes is the same
headroom A-S1 already called non-constructive (`docs/coin-lift-plan.md` §4):
there is no explicit basis to build a compressed transfer against, and
`docs/skeletonkey-reprompt.md` names that missing basis as the single largest
open technical question in the mission. This result says the room is real. It
says nothing about how to enter it.

Nor does it name the true growth law. 2.43 is a fit over eight points, not a
derivation; the quotients still wander (2.32, 2.46, 2.43, 2.48) with no sign of
settling on a recognisable constant.

And the next point is not cheap. Measured wall time for this code on ayr,
single-core, one `x` weight:

| H | wall |
|---|---|
| 8  | ~20 s |
| 9  | ~155 s |
| 10 | ~2495 s |
| 11 | 59422 s |

That is 7.8x, 16x, 23.8x per height — the *cost* of measuring the floor grows
an order of magnitude faster than the floor itself. Extrapolating the last
ratio puts H = 12 near 400 hours single-core, about 17 days, to buy one more
digit of the same fit rather than a mechanism.
