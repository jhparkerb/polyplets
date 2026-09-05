# The transfer floor grows at 2.43, not 3, and both extrapolations missed

2026-08-21, branch `skeletonkey`. Probe `scripts/probe_hankel_rank2.py`, run on
ayr, exact closure mod `p = 2^31 - 1`, gated against every banked point of the
ladder.

## The question

The observability dimension of the incumbent column transfer is the *floor* on
how many quantities any method of this shape must carry across the cut.
Whether the compressed-transfer family (breadth candidate #3,
`docs/skeletonkey-reprompt.md`) can ever pull ahead turns on one comparison:
does that floor grow at the incumbent's 3 per height, or slower?

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

Eight points also fix no recurrence: none of order ≤ 3 with a constant term
fits them (`experiments/height_dimension_ladders.py`, exact rational
elimination), and an OEIS lookup returns nothing. Order 4 is sometimes quoted
as excluded too and is not — five unknowns against four windows carries no
surplus, homogeneous or not, so eight values cannot test it.

## Five ladders, and which bounds which

Five numbers in this record answer to "how big is height H", and they are five
different objects; this section is the one place that says which. The **char-2
column rank** `r(H)` is the rank over GF(2) of the Hankel matrix of the strip
automaton's column-level functional, rows indexed by the `Motzkin(H+1) − 1`
frontier partitions; it equals A034299 at every measured point. The **char-0
Hankel rank** above is the rank of that same integer Hankel matrix over ℚ,
measured mod `p = 2^31 − 1` at `x = 1`. The **reach-merged frontier count**
`N(H)` is not a rank but a state count — the number of N-family classes of
frontier partitions, the coarsest congruence the transition rule can see. The
**new-root degree** `deg ψ_H` counts the denominator factors of the fixed-height
generating function `G_H(x)` appearing first at height H: a degree over ℚ of a
polynomial in the cell-counting variable, not the dimension of any state space
(H = 11 was refuted 2026-09-05 as a CRT wraparound). The **cell-level compressed
dimension** `d_p` is the rank over `F_p` of the *cell*-granularity functional,
what an algorithm reading one cell at a time would carry; `d_2` is the same
object over GF(2).

| quantity | H known | at H = 8 | growth (range / last rung) | source |
|---|---|---|---|---|
| char-2 column rank `r(H)` | 4..13 | 112 | 2.04 / 2.00 | `exactchange-probes.md` §1 |
| char-0 Hankel rank | 4..11 | 204 | 2.43 / 2.48 | this file |
| reach-merged classes `N(H)` | 4..21 | 239 | 2.48 / 2.59 | `nkey-census.md` |
| new-root degree `deg ψ_H` | 1..10 | 462 | 2.46 / 2.62 | `anisotropic-not-dfinite.md` |
| raw column frontier | all H | 834 | 2.69 / 2.81 | `Motzkin(H+1) − 1` |
| char-2 cell rank `d_2` | 4..8 | 1,155 | 2.45 / 2.24 | `skeletonkey-cell-sparsity.md` |
| char-0 cell dimension `d_p` | 4..8 | 1,826 | 2.75 / 2.64 | `skeletonkey-cell-sparsity.md` |

The relations, each with its reason, and marked where there is none:

- **`N(H)` ≤ raw frontier. Proved**: the merged set is a quotient of the
  frontier partitions.
- **Hankel rank over any field ≤ `N(H)`. Proved**: two states in one N-family
  have the same successor family and acceptance, so they have identical Hankel
  rows, and the number of distinct rows bounds the rank. That direction of the
  congruence is a proof over every field (`results/exactchange-probes.md` §6),
  not a fit. Tightest at H = 11, 3,016 against 3,441.
- **Column rank ≤ cell rank, in each characteristic. Proved**: restricting
  prefixes and suffixes to whole-column boundaries exhibits the column Hankel
  matrix as a submatrix of the cell one.
- **char-2 rank ≤ the rational rank of the same matrix. Proved** (reduction
  cannot raise rank). But the char-0 numbers are mod-`p` ranks, themselves only
  lower bounds for the rational rank, so `r(H) ≤` the *measured* char-0 value
  is **observed at eight heights, not proved**; likewise `d_2 ≤ d_p`. Two
  distinct primes are not ordered.
- **`deg ψ_H` against any rank: no relation established**, and the natural
  guess is false — it *exceeds* the char-0 Hankel rank from H = 7 on (181
  against 88; 3,289 against 1,217). The only bound tying them together is
  crude: a column carries at most H cells, so `deg ψ_H ≤ deg Q_H ≤ H · N(H)`,
  which at H = 10 reads 3,289 ≤ 13,990. The minimal recurrence order of
  `T(n,H)` in n is `deg Q_H`, not `deg ψ_H`: ψ drops every denominator factor
  inherited from a lower height.
- **`d_p` against the column-level ladders: no relation established downward**,
  and it exceeds all of them at every shared height (1,826 against 239 at
  H = 8), which is why that engine loses.

Growth respects the order the sizes do — 2.00 < 2.48 < 2.59 < 2.81 on the last
measured rung — so nothing here is on course to cross.
`experiments/height_dimension_ladders.py` re-checks every inequality and both
orderings from banked numbers in under a second, and exits nonzero on failure.

## What this does not settle

A growth rate is not an engine. The headroom this establishes is the same
headroom A-S1 already called non-constructive (`docs/coin-lift-plan.md` §4):
there is no explicit basis to build a compressed transfer against, which
`docs/skeletonkey-reprompt.md` names as the largest open technical question in
the mission. This result says the room is real, not how to enter it.

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
