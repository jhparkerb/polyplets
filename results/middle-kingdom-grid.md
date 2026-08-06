# Middle Kingdom Phase 0 — the classification grid, one enumeration

`docs/middle-kingdom-plan.md` Phase 0. `build/directed_cone_anchor`'s new
`grid` mode extends the existing Redelmeier untried-set DFS over all fixed
king animals (unchanged growth/canonicalization, same machinery validated to
n=12 against A006770 since 2026-07-30) to tally every cell of the
classification grid in one pass, instead of one filter at a time.

**Updated 2026-08-05 by Phase 3** (`results/middle-kingdom-phase3.md`): the
grid is 20 cells, not 16 -- `mdir` (Bacher's Definition 2) joined as a fifth
directedness row, since Phase 1c settled that `ctrlB` cannot stand in for it.
Findings 1 and 2 below are kept as written except where marked CORRECTED;
Finding 2's collapse list was both incomplete and internally contradictory,
and Phase 3 proves the corrected list rather than measuring it.

**Directedness** (5): none, `dir5` (Bacher 5-cone `{W,NW,N,NE,E}`), `dir4`
(half-plane 4-cone `{N,NE,E,SE}`), `ctrlB` (dir5nb's bottom-row-waived
predicate — **not** multi-directed), and since Phase 3 `mdir` (Bacher's
Definition 2 itself).

Phase 1c settled that last label (2026-08-05, `results/multi-directed.md`):
`ctrlB` is not a placeholder for multi-directed, it is a distinct class
**incomparable** with it — 4 animals at n=7 pass `ctrlB` and fail Bacher's
Definition 2, and 4 at n=4 do the reverse. Multi-directed was a fifth
directedness value this grid had no column for; Phase 3 added it as a row of
its own (`build/directed_cone_anchor mdir`'s predicate, evaluated in the same
pass). Its `none`-convexity row runs 1, 4, 20, 110, 636, 3790, 23036, … =
A222205, and all three of its convexity cells collapse onto the unfiltered
row.

**Convexity** (4): none, column-convex (per-column runs gap-free), HV-convex
(column-convex + row-convex), staircase (column-convex + column bottoms AND
tops nondecreasing left to right).

Gate: `make gate-king-grid` (`tests/gate_king_grid.py`) — GREEN, and since
Phase 3 it also pins the eight collapses and the four cells that must NOT
collapse.
Reproduce: `make build/directed_cone_anchor && build/directed_cone_anchor grid 14 8`.

## Acceptance (docs/middle-kingdom-plan.md Phase 0)

- [x] Row-1 (directedness=none) and column-1 (convexity=none) entries of the
  plan's reference table reproduced exactly, n up to the reference depth.
- [x] A006770 (fixtures/b006770.txt) reproduced exactly to n=12.
- [x] The two pre-existing RED controls (dir4, dir5nb) still diverge from
  A047781 exactly at n=3 (18 vs 19, 20 vs 19) — unchanged by the refactor.
- [x] New RED control (`gridbad`): staircase predicate with column-top
  monotonicity dropped fails to reproduce A225114 (diverges at n=3: 10 vs 9).
  It reproduces A007052 instead (1,3,10,34,116,396) — see finding 1 below.
- [x] n=12 in 9.6s (budget: under 10 minutes on 8 threads). Pushed to n=14 in
  302.8s wall / 2064.9s cpu (8 threads, gympie), well inside budget.

## The 20-cell table, n = 1..14

One block per convexity column; within a block the five directedness rows.
(Phase 0 measured the first four rows to n=14; Phase 3 re-ran the whole pass
with `mdir` added, 512.1 s wall / 3672.6 s cpu on 8 threads,
`results/mk_grid20_n14.txt`. The 16 original cells are unchanged.)

```
convexity = none
 n |           none           dir5           dir4          ctrlB           mdir
 1 |              1              1              1              1              1
 2 |              4              4              4              4              4
 3 |             20             19             18             20             20
 4 |            110             96             85            106            110
 5 |            638            501            413            576            636
 6 |           3832           2668           2044           3179           3790
 7 |          23592          14407          10248          17736          23036
 8 |         147941          78592          51876          99748         141946
 9 |         940982         432073         264550         564430         883360
10 |        6053180        2390004        1357070        3209194        5538098
11 |       39299408       13286043        6994780       18316729       34917224
12 |      257105146       74160672       36196706      104872413      221125102
13 |     1692931066      415382397      187938842      602013085     1405276324
14 |    11208974860     2333445468      978599560     3463412836     8956020294

convexity = col-convex
 n |           none           dir5           dir4          ctrlB           mdir
 1 |              1              1              1              1              1
 2 |              4              4              4              4              4
 3 |             18             17             17             18             18
 4 |             83             71             73             79             83
 5 |            385            289            314            339            385
 6 |           1788           1149           1351           1423           1788
 7 |           8305           4481           5813           5872           8305
 8 |          38575          17209          25012          23909          38575
 9 |         179170          65281         107621          96336         179170
10 |         832189         245169         463069         384934         832189
11 |        3865253         913153        1992482        1527712        3865253
12 |       17952864        3377505        8573203        6029421       17952864
13 |       83385309       12418561       36888569       23686066       83385309
14 |      387298083       45428161      158723236       92685759      387298083

convexity = HV-convex
 n |           none           dir5           dir4          ctrlB           mdir
 1 |              1              1              1              1              1
 2 |              4              4              4              4              4
 3 |             16             16             15             16             16
 4 |             61             61             53             61             61
 5 |            221            221            177            221            221
 6 |            766            766            567            766            766
 7 |           2566           2566           1767           2566           2566
 8 |           8390           8390           5417           8390           8390
 9 |          26982          26982          16465          26982          26982
10 |          85834          85834          49897          85834          85834
11 |         271174         271174         151288         271174         271174
12 |         853111         853111         459836         853111         853111
13 |        2677214        2677214        1402387        2677214        2677214
14 |        8389720        8389720        4292477        8389720        8389720

convexity = staircase
 n |           none           dir5           dir4          ctrlB           mdir
 1 |              1              1              1              1              1
 2 |              3              3              3              3              3
 3 |              9              9              9              9              9
 4 |             28             28             28             28             28
 5 |             87             87             87             87             87
 6 |            272            272            272            272            272
 7 |            850            850            850            850            850
 8 |           2659           2659           2659           2659           2659
 9 |           8318           8318           8318           8318           8318
10 |          26025          26025          26025          26025          26025
11 |          81427          81427          81427          81427          81427
12 |         254777         254777         254777         254777         254777
13 |         797175         797175         797175         797175         797175
14 |        2494307        2494307        2494307        2494307        2494307
```

Identifications: (none,none) = A006770. (none,colconvex) = A187077.
(none,hvconvex) = the novel HV-convex-by-area sequence (`results/convex-polyplets.md`,
measured to n=128 by `experiments/convex_tm.py`; matches here through n=14).
(none,staircase) = A225114. (dir5,none) = A047781. (dir4,none) = A055834
(dir4/none at n=12,13,14 = 36196706, 187938842, 978599560 — matches the
independently-derived values in `results/king-subfamilies.md`'s addendum
exactly, a free cross-check of that separate derivation). (ctrlB,none) =
the "cone-anchor control B" row already recorded in
`results/directed-cone-anchor.md`. (mdir,none) = **A222205**, "number of
multi-directed animals with n vertices" (Sloane 2013, from Bacher's paper) --
Phase 3's novelty check, which corrects the plan's "NOVEL" label for that row;
our 200 terms extend the entry's 23.

The 9 cells (dir5/dir4/ctrlB x colconvex/hvconvex/staircase), plus the 3 the
mdir row adds, were Phase 3's targets; all twelve are settled in
`results/middle-kingdom-phase3.md`. Two findings below bore directly on that
work.

## Finding 1 — A007052's "directed column-convex" label is a naming collision

The plan's grid table already fills `directed x column-convex = A007052`.
That identity, as actually proved in `results/king-subfamilies.md`
("Theorem (dcc)"), uses **column-convex + column-bottoms-nondecreasing**,
with no cone-reachability filter at all — not Bacher's 5-cone directedness
that the plan's own Definitions section specifies for the "directed" row.

Confirmed here two ways:
- `(dir5,colconvex)` in the table above (1,4,17,71,289,...) does NOT match
  A007052 (1,3,10,34,116,396) — diverges already at n=2 (4 vs 3).
- `gridbad`'s "staircase" column (bottoms-monotone, tops check dropped —
  i.e. exactly column-convex + bottoms-nondecreasing, no cone filter)
  reproduces A007052 **exactly**: 1,3,10,34,116,396.

So A007052 sits at (none, "bottoms-monotone-only") — a fifth convexity
variant this grid doesn't have a slot for, not at any cell of the 4x4 grid.
The plan's table entry for that cell should be read as "known, but the
identity is with a different, weaker predicate than the row label says" —
worth a one-line correction when Phase 3 writes this cell up. Same caution
applies to any other pre-filled cell inherited from `king-subfamilies.md`
before assuming the row/column labels there match this grid's definitions
exactly.

**Resolved by Phase 3.** The real `(dir5,colconvex)` cell is a new sequence,
1,4,17,71,289,1149,… with g.f. `x(1-5x+9x^2-6x^3+2x^4)/((1-x)(1-4x+2x^2)^2)`
and growth `2+sqrt(2)` carrying an extra factor `n`. A007052's denominator
`1-4x+2x^2` appears there squared, which is the naming collision's real cause:
Bacher-directedness on a column-convex animal means the bottom profile is
valley-unimodal, i.e. TWO A007052-style monotone runs glued at the valley,
where A007052 itself is one run (`results/middle-kingdom-phase3.md`).

## Finding 2 — HV-convex and staircase collapse under directedness (CORRECTED)

Across all n = 1..14 measured: `(dir5,hvconvex) == (none,hvconvex)` and
`(dir5,staircase) == (none,staircase)`, term for term. Every HV-convex (and
every staircase) king animal is Bacher-5-cone-directed already -- the
directedness filter removes nothing.

**CORRECTED 2026-08-05 (Phase 3).** As first written, this finding named only
the two `dir5` collapses and then said in the same sentence both that
`ctrlB/hvconvex` does NOT collapse and that `ctrlB` "trivially inherits dir5's
collapse". The second clause is the right one, the first was wrong, and the
list was short by two more. Measured over all n = 1..14 in the 20-cell table
above, **eight** cells equal the corresponding unfiltered cell:

```
(dir5,hvconvex)  (ctrlB,hvconvex)  (mdir,hvconvex)   = (none,hvconvex)
(dir5,staircase) (dir4,staircase)  (ctrlB,staircase) (mdir,staircase) = A225114
(mdir,colconvex) = (none,colconvex) = A187077
```

and four do not: `(dir5,colconvex)`, `(dir4,colconvex)`, `(ctrlB,colconvex)`
and `(dir4,hvconvex)`. `dir4` is the exception on the HV-convex column because
its cone `{N,NE,E,SE}` has no westward step, so it cannot enter a column that
sits to the LEFT of and below its source column, which HV-convexity permits.

Phase 3 proves all eight rather than leaving them empirical
(`results/middle-kingdom-phase3.md`, Lemma A and Propositions 1-5): on a
column-convex animal every directedness predicate here is a condition on the
bottom profile `b` alone, HV-convexity is exactly "b valley-unimodal and t
peak-unimodal", and "b valley-unimodal" IS 5-cone directedness. So HV-convex
sits inside dir5, which sits inside ctrlB and inside multi-directed; staircase
sits inside all four; and every column-convex animal is multi-directed.

Also note: `dir5/colconvex` and `ctrlB/colconvex` do NOT collapse to
`none/colconvex` at any n>=3 measured (diverge starting n=3: 17 vs 18, and
18 vs 18 respectively at n=3 but diverging by n=4: 79 vs 83) -- column-convex
alone is not restrictive enough to force directedness the way HV-convex is.
Those two, plus `dir4/colconvex` and `dir4/hvconvex`, are the four cells Phase
3 had to enumerate; three of them turned out to be new sequences.

## Provenance

Measured 2026-08-05 on gympie, `git=54440c2-dirty` (Phase 0 code changes
uncommitted at measurement time), 8 threads. `build/directed_cone_anchor`
`grid 14 8`, 16 cells: wall_s=302.8, cpu_s=2064.9, peak_rss_mb=1.9. Re-run the
same day with the `mdir` row added (20 cells, `results/mk_grid20_n14.txt`):
wall_s=512.1, cpu_s=3672.6, peak_rss_mb=1.9.
