# Subclasses of polyplets: directed, convex, stratified

A polyplet (king animal) is a finite set of cells of `Z²` connected under king
moves, counted up to translation; `a(n)` = A006770 is the number with `n`
cells. This file records what is known about the subclasses obtained by
restricting the shape: the five directedness predicates crossed with the four
convexity predicates (twenty classes, all identified), the directed and
multi-directed classes of Bacher, the column-convex and staircase classes with
their rational generating functions, convex polyplets by area and by
semiperimeter, the stratifications by edge-component count and by hole count,
the extremal hole statistics, and the connectivity of the single-cell move
graph. Grades: the eight collapses of the grid, the four theorems that place
the classical restrictions on known sequences, the squeeze that gives every
class between staircase and HV-convex the same growth constant, the maximum
hole area, and the exponential rarity of hole-free polyplets are proved; the
term series, growth constants and amplitude ratio are measured, with the digit
counts stated; every non-D-finiteness statement is an exclusion in a stated
box, not a proof; the sharp asymptotics of the phase-split series and the
parity-compression step of the maximum hole count are conjectured. Nothing
here has been submitted to OEIS.

## Definitions

All classes are sets of cells of `Z²`, 8-connected, counted up to translation
(fixed animals). A column-convex animal is a sequence of nonempty column
intervals `[b(j), t(j)]`, `j = 1..k`, on a contiguous run of columns, with
consecutive columns king-adjacent; `b` is the bottom profile, `t` the top
profile, `h(j) = t(j) − b(j) + 1` the column height, `d(j) = b(j+1) − b(j)`.

**Directedness.** From a canonical source, every cell must be reachable by
cone steps that stay inside the animal.

- `none`: king-connected only.
- `dir5` (Bacher's directed animals): cone `{W, NW, N, NE, E}`, source the
  leftmost cell of the bottom row. A consequence, not an added rule: the
  bottom row is one contiguous run.
- `dir4` (half-plane directed): cone `{N, NE, E, SE}`, source the bottom cell
  of the leftmost column. The cone has a downward step, so `dir4` and `dir5`
  are not nested either way.
- `ctrlB` (control B): the `dir5` cone, flooded from every cell of the global
  bottom row. It began as a control for the `dir5` filter and is a class of its
  own, incomparable with multi-directed.
- `mdir` (multi-directed, Bacher's Definition 2): sources are the local minima
  of `b`, keystones its local maxima; every cell must be cone-reachable from
  some source, and every keystone from a source strictly to its left and one
  strictly to its right. Stated in full under "Multi-directed king animals".

**Convexity.**

- `none`.
- column-convex: every column one contiguous run; rows unconstrained.
  Row-convex is the transpose and has the same counts.
- HV-convex ("convex"): every row and every column one contiguous run.
  Equivalently `b` is valley-unimodal (nonincreasing then nondecreasing) and
  `t` is peak-unimodal (Corollary 4 below).
- staircase: column intervals with `b` and `t` both nondecreasing left to
  right. Strictly inside HV-convex.
- The grounded families (bargraph, stack, Ferrers) are excluded from the grid:
  crossing them with directedness adds only trivial classes.

**Generating functions and verdicts.** A sequence is rational, algebraic or
D-finite according to its generating function `F`. "Excluded in the box
`(J, D)`" means no P-recurrence `Σ_{i≤J} p_i(n) a(n+i) = 0` with `deg p_i ≤ D`
exists; "not algebraic in the box `(K, L)`" means no relation
`Σ_{j≤K} q_j(t) F^j = 0` with `deg q_j ≤ L`. Both are decided by
`build/prec_guess` (`cpp/prec_guess.cpp`) as a full-column-rank test modulo
`p = 2^61 − 1`: the matrix is integral, so full rank mod `p` is full rank over
`Q`, and a box excludes every smaller box. A rank defect is only a candidate
and is then checked on rows withheld from the fit and under a second prime.
"Trusted digits" of a growth constant are the agreement between the
extrapolation on the full series and on the series shortened by thirty terms,
minus a two-digit guard (`experiments/convex_growth.py`).

## The directedness–convexity grid

Rows are directedness, columns convexity. Every one of the twenty classes is
identified.

| | none | column-convex | HV-convex | staircase |
|---|---|---|---|---|
| **none** | A006770 | A187077 | not in OEIS (convex polyplets) | A225114 |
| **dir5** (5-cone) | A047781 | not in OEIS | = (none, HV) | = A225114 |
| **dir4** (4-cone) | A055834 | A018902 | not in OEIS | = A225114 |
| **ctrlB** (bottom row waived) | not in OEIS | not in OEIS | = (none, HV) | = A225114 |
| **multi-directed** | A222205 | = A187077 | = (none, HV) | = A225114 |

Five sequences of the grid are absent from OEIS: HV-convex by area, control B
unfiltered, (dir5, column-convex), (ctrlB, column-convex) and
(dir4, HV-convex). HV-convex by semiperimeter and (dir4, HV-convex) by
semiperimeter are two more, counted by a different statistic. Two earlier
labels were wrong and are corrected here: the multi-directed row is A222205
(Sloane 2013, from Bacher's paper), not new; and "directed column-convex =
A007052" was a naming collision, A007052 being column-convex with `b`
nondecreasing and no cone condition at all.

### Reference values

The table every check of the grid campaign compares against; a mismatch means
the program is wrong, not the table. Growth column: estimates or exact values
as stated.

| sequence | first terms | growth |
|---|---|---|
| all king animals A006770 | 1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180 | 7.110 (est) |
| directed A047781 | 1, 4, 19, 96, 501, 2668, 14407, 78592, 432073, 2390004 | 3+2√2 = 5.82843 |
| half-plane directed A055834 | 1, 4, 18, 85, 413, 2044 | 27/5 = 5.4 |
| column-convex A187077 | 1, 4, 18, 83, 385 | 4.64468 (quartic root) |
| directed column-convex A007052 | 1, 3, 10, 34, 116, 396 | 2+√2 = 3.41421 |
| staircase A225114 | 1, 3, 9, 28, 87, 272 | — |
| **HV-convex by area (novel)** | 1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834 | 3.1289432697308862523 (Phase 2b, 199 digits) |
| **HV-convex by semiperimeter (novel)** | 1, 2, 9, 36, 154, 668, 2916, 12740 | ~4.13 falling |
| multi-directed = A222205 | 1, 4, 20, 110, 636, 3790, 23036, 141946 | 6.475196280297 (12 digits, 400-term series) |
| cone-anchor control B (bottom row waived) | 1, 4, 20, 106, 576, 3179, 17736, 99748 | — |
| convex polyomino by area (CONTROL) = A067675 | 1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312 | 2.3091385933304947311 (Phase 2b, 121 digits) |
| convex polyomino by semiperimeter A005436 (CONTROL) | 1, 2, 7, 28, 120, 528, 2344 | — |

Spot value, measured 2026-08-05 on gympie by `python3 experiments/convex_tm.py 128`
(about 4 minutes), term `n = 128` of HV-convex by area:

```
2509948162052912103766963600364762350348141297853178810057013197
```

### The brute-force table, n = 1..14

One Redelmeier pass over all fixed king animals evaluates every class on every
animal generated (`build/directed_cone_anchor grid 14 8`,
`cpp/directed_cone_anchor.cpp`; the enumeration is the one validated against
A006770). Measured 2026-08-05 on gympie, 8 threads, source `git=54440c2-dirty`:
the sixteen-class run took 302.8 s wall, 2064.9 s cpu, peak RSS 1.9 MB; the
twenty-class run with the `mdir` row added took 512.1 s wall, 3672.6 s cpu,
1.9 MB, and left the sixteen original columns unchanged. Data:
`results/mk_grid20_n14.txt`. Gate: `make gate-king-grid`
(`tests/gate_king_grid.py`), which also checks the eight equalities that must
hold and the four that must not.

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

Identifications on the table: (none, none) = A006770 through `n = 12` against
`fixtures/b006770.txt`; (none, column-convex) = A187077; (none, HV-convex) =
the convex-polyplet series, matching the row transfer matrix through `n = 14`;
(none, staircase) = A225114; (dir5, none) = A047781; (dir4, none) = A055834,
where the values at `n = 12, 13, 14` equal those obtained by direct cone
growth in `experiments/directed_halfplane.cpp`; (ctrlB, none) = control B;
(mdir, none) = A222205, all 23 published terms matching.

Controls of the grid mode, all required to fail and failing: `dir4` and
`ctrlB` diverge from A047781 at `n = 3` (18 and 20 against 19); the `gridbad`
mode, a staircase predicate with the top-monotonicity dropped, diverges from
A225114 at `n = 3` (10 against 9) and reproduces A007052 instead.

### A007052 is column-convex with nondecreasing bottoms, and no cone class

The theorem under "Column-convex, staircase and the grounded families" places
A007052 at column-convex plus `b` nondecreasing, with no reachability
condition. The grid confirms that this is a different predicate from
`(dir5, column-convex)`: the latter runs 1, 4, 17, 71, 289, …, diverging from
A007052 at `n = 2`, while the `gridbad` predicate (exactly bottoms-monotone,
no cone) reproduces 1, 3, 10, 34, 116, 396. The cause is visible in the
`(dir5, column-convex)` generating function below: A007052's denominator
`1 − 4x + 2x²` appears squared, because 5-cone directedness on a column-convex
animal means `b` is valley-unimodal, two A007052-style monotone runs glued at
the valley, where A007052 is a single run.

### Why eight of the twelve open classes collapse

Every collapse is a proposition. Throughout, king-adjacency of consecutive
columns is exactly `d(j) ∈ [−h(j+1), h(j)]`, giving `h(j) + h(j+1) + 1`
placements of a height-`h(j+1)` column against a height-`h(j)` one.

**Lemma A (a column is reached iff its bottom is).** Neither forward cone
contains a southward step: `{W, NW, N, NE, E}` and `{N, NE, E, SE}` both move
strictly up or stay level. Inside one column of a column-convex animal
reachability only climbs, so the reached part of a column is an up-set
`[r(j), t(j)]`, and the animal is directed iff `r(j) = b(j)` for every `j`.
From a fully reached column `j`, the bottom cell of the next column is
enterable
- (5-cone, either direction) iff `b(j±1) ≥ b(j)`: entry at height `b(j±1)`
  needs `b(j±1)` or `b(j±1)−1` occupied in column `j`, and `b(j±1) ≤ t(j)+1`
  is king-adjacency, which always holds;
- (4-cone, rightward only) iff `b(j+1) ≥ b(j) − 1`: the SE step buys exactly
  one row of descent.

**Proposition 1 (dir5).** A column-convex king animal is Bacher-5-cone
directed iff `b` is valley-unimodal (nonincreasing, then nondecreasing).
Forward: the source is the leftmost cell of the bottom row, which sits on the
unique local-minimum plateau; propagate right and left by Lemma A. Backward:
let `P` be any local-minimum plateau at height `v` other than the global one.
Every cone step into `P`'s bottom row starts at height `v` or `v−1` in the
column immediately left or right of `P`, and both of those columns have bottom
strictly above `v`, so no such cell exists; nothing inside `P` at height `v`
can be reached from inside `P` either, because that row is where the flood
would have to start. So `P`'s bottom row is unreachable and the animal is not
directed.

**Proposition 2 (dir4).** A column-convex king animal is half-plane-4-cone
directed iff `b(j+1) ≥ b(j) − 1` for every `j`. The source is the bottom of
the leftmost column and propagation is rightward only, so Lemma A applies
column by column with no case analysis.

**Proposition 3 (ctrlB).** A column-convex king animal passes the bottom-row-
waived predicate iff every local minimum of `b` equals `min b`. The sources
are the bottoms of the columns attaining `min b`; from those, Lemma A reaches
exactly the columns joined to a source by a monotone run of `b`, which is every
column iff no local minimum sits above the global one.

**Corollary 4 (HV-convexity contains directedness).** Row-convexity forces `b`
valley-unimodal: if `b(j−1) > b(j) < b(j+1)`, the row `y = b(j) − 1` is
occupied in columns `j−1` and `j+1` (king-adjacency gives `b(j) ≤ t(j±1)+1`)
and empty in column `j`, a gap. Dually `t` is peak-unimodal, and the converse
holds too, so **HV-convex = column-convex + `b` valley-unimodal + `t`
peak-unimodal.** With Proposition 1 this says HV-convex ⊂ dir5 outright.
Staircase (bottoms and tops nondecreasing) is inside HV-convex, and also
satisfies Proposition 2's condition trivially. Since dir5 ⊆ ctrlB always
(same cone, larger source set) and dir5 ⊂ multi-directed (Bacher: one source,
no keystone), five collapses follow at once:

    (dir5, HV) = (ctrlB, HV) = (mdir, HV) = (none, HV)      [the convex-polyplet series]
    (dir5, stair) = (dir4, stair) = (ctrlB, stair) = (mdir, stair) = A225114

**Proposition 5 (every column-convex king animal is multi-directed).**
Bacher's Definition 2 asks (1) every cell reachable from some source, where
sources are the local minima of `b`, and (2) every keystone (local maximum of
`b`) reachable from a source strictly left and one strictly right. For (1),
every column reaches a local minimum of `b` by a monotone run, and Lemma A
propagates the bottom back along it. For (2), the keystone at the leftmost
column of a local-maximum plateau is reached from the nearest source on its
left along the ascending run, and from the nearest source on its right along
the run that descends to it, whose last leg is a sequence of W steps across the
plateau at the keystone's own height. The blocking rule ("no other keystone at
the keystone's height") never bites: keystone marks sit at their own column
bottoms, which are strictly lower on both runs, and the plateau's other columns
carry no mark because the leftmost column takes it. Hence the entire
multi-directed row of the grid equals the unfiltered row.

`dir4` is the exception on the HV-convex column because its cone has no
westward step, so it cannot enter a column to the left of and below its source
column, which HV-convexity permits. `(dir5, column-convex)` and
`(ctrlB, column-convex)` do not collapse either: column-convexity alone does
not force directedness (17 against 18 at `n = 3`; 79 against 83 at `n = 4`).
All eight equalities and all four inequalities hold on the brute-force table
through `n = 14`.

The meta-finding that every classical restriction lands king animals in known
territory (compositions, partitions, an existing entry) survives in sharpened
form: convexity subsumes directedness. HV-convexity implies 5-cone
directedness, staircase implies both cones, column-convexity implies
multi-directedness.

### The four classes that do not collapse

`cpp/middle_kingdom_tm.cpp` (`build/middle_kingdom_tm`) counts bottom profiles
directly, with state (column height, unimodality phases), or (column height,
height above the running minimum, phase) for `ctrlB`; modes
`cc ccmono ccdir5 ccdir4 ccctrlb hv hvdir4 hvmono stair hvdir4asc` and the
controls `ccdir4bad ccctrlbbad hvdir4ascbad`. It reproduces the brute-force
table for all six column-convex classes through `n = 14`, and its `hv` mode
reproduces all 700 terms of the independent row transfer matrix
`build/convex_area_tm` (`make gate-middle-kingdom`, `tests/gate_middle_kingdom.py`).

| class | first terms | µ | generating function |
|---|---|---|---|
| (none, col-convex) = A187077 | 1, 4, 18, 83, 385, 1788 | 4.644680109386463104 (root of x⁴−7x³+13x²−10x+2) | rational (published) |
| (dir5, col-convex) | 1, 4, 17, 71, 289, 1149 | 2+√2 exactly, with a double pole | rational, denominator (1−x)(1−4x+2x²)² |
| (dir4, col-convex) = A018902 | 1, 4, 17, 73, 314, 1351 | (5+√13)/2 = 4.302775637731994647 | rational, x(1−x)/(1−5x+3x²) |
| (ctrlB, col-convex) | 1, 4, 18, 79, 339, 1423 | 3.811527945110 (12 digits) | not D-finite in the boxes below |
| (dir4, HV-convex) | 1, 4, 15, 53, 177, 567 | 3.128943269730886252277 = the HV-convex constant (49 digits checked) | not D-finite in the boxes below |

**(dir5, column-convex).** 1, 4, 17, 71, 289, 1149, 4481, 17209, 65281,
245169, 913153, 3377505, 12418561, 45428161; 700 terms in
`results/mk_ccdir5_terms_n700.txt`. Valley-unimodal profiles split into a
nonincreasing run and a nondecreasing one. Each run's transfer operator has
rank 1 (`d ≤ 0` admits `h(j+1)+1` placements, `d ≥ 0` admits `h(j)+1`), and
both runs have the same ratio `p(x) = (2x−x²)/(1−x)²`, so the two geometric
series multiply and the pole is double:

    F(x) = x(1 − 5x + 9x² − 6x³ + 2x⁴) / [ (1−x)(1 − 4x + 2x²)² ]
    a(n) = 9a(n−1) − 28a(n−2) + 36a(n−3) − 20a(n−4) + 4a(n−5),  n > 5
    a(n) ~ C·n·(2+√2)ⁿ,   C = 0.10370…   (measured a(n)/(n µⁿ): 0.103899 at n=300, 0.1037013 at n=700)

Recurrence and numerator checked against all 700 terms. No OEIS match on nine
terms or on the six-term prefix (`experiments/oeis_lookup.py`, 2026-08-05);
no literature hit, directed column-convex animals being enumerated only on the
square lattice.

**(dir4, column-convex) = A018902.** 1, 4, 17, 73, 314, 1351, 5813, 25012,
107621, 463069, 1992482, 8573203, 36888569, 158723236
(`results/mk_ccdir4_terms_n700.txt`). Proposition 2's condition `d ≥ −1`
makes the placement count `h(j) + 2`, independent of the new column's height,
so the transfer operator has rank 1 and

    F(x) = x(1−x)/(1 − 5x + 3x²),   a(n) = 5a(n−1) − 3a(n−2),   µ = (5+√13)/2.

This is A018902 (offset 0, g.f. `(1−x)/(1−5x+3x²)`), matched termwise to
`n = 20` against the entry's data. The entry's formula section says A018902
is the INVERT transform of A007052; the animals explain why: cut the profile at
every descent (each is by exactly one row) and the pieces are
bottoms-nondecreasing column-convex animals, so the class is a sequence of
A007052 objects. The entry's comments are compositions, closed walks on `K₂`,
Pisot sequences and words, with no lattice-animal reading. Draft comment,
staged, jasonp's call:

> a(n) is the number of column-convex polyplets with n+1 cells (column-convex
> king-lattice animals: sets of cells of Z² whose columns are each a contiguous
> run, connected under king moves, counted up to translation) that are directed
> in the four-step cone {N, NE, E, SE} from the bottom cell of the leftmost
> column. Equivalently, those whose column-bottom profile never drops by more
> than one row from one column to the next; cutting the profile at each drop
> gives the INVERT relation to A007052 above a combinatorial meaning, A007052
> being the same class with the profile nondecreasing. Verified for n <= 19.
> Cf. A007052, A187077, A055834, A006770.

**(ctrlB, column-convex).** 1, 4, 18, 79, 339, 1423, 5872, 23909, 96336,
384934, 1527712, 6029421, 23686066, 92685759; 250 terms in
`results/mk_ccctrlb_terms_n250.txt`. "Every local minimum of `b` at the global
minimum" is not a local rule on the profile steps, so the transfer matrix
carries the height above the running minimum and has `O(n²)` states. Cost on
gympie: `n = 150` in 5.3 s and 194 MB, `n = 250` in 66.3 s and 938 MB, fixing
the scaling at `O(n^4.95)` time and `O(n^3.2)` memory; `n = 400` is priced at
about 11 minutes and 4 GB and was not run.

- `µ = 3.811527945110`, twelve digits: the raw-ratio cross-check at `N`
  against `N − 60` gives a floor of 10, the Aitken cross-check 40, and the
  ratio's own increment at `n = 250` is `5e−14` under a geometric correction.
  `θ = 0`. The correction ratio is 0.895759813791, and
  `µ × 0.895759813791 = 3.41421356237 = 2+√2` to twelve digits: the
  subdominant singularity of this class is the dominant one of
  `(dir5, column-convex)`, as dir5 ⊂ ctrlB predicts.
- Not rational: no constant-coefficient recurrence of order ≤ 12 (rank 13 of 13).
- Not D-finite in order ≤ 12 / degree ≤ 12, nor order ≤ 14 / degree ≤ 8.
- Not algebraic in degree ≤ 8 / t-degree ≤ 14, nor degree ≤ 6 / t-degree ≤ 20.
- PSLQ on `µ`: no integer relation of degree ≤ 4 at height ≤ 10⁵; the
  degree 5–8 hits fail the capacity test.

No OEIS match on nine terms or the six-term prefix. `ctrlB` is not a natural
class; its interest is that it is the only column-convex class with no closed
form, where the other four directedness predicates give rational generating
functions.

**(dir4, HV-convex).** 1, 4, 15, 53, 177, 567, 1767, 5417, 16465, 49897,
151288, 459836, 1402387, 4292477; 700 terms in
`results/mk_hvdir4_terms_n700.txt`. HV-convexity is `b` valley-unimodal and
`t` peak-unimodal; Proposition 2 adds `d ≥ −1`, which bites only on the
descending part of `b`.

- `µ = 3.128943269730886252277447995387754160532091221904`, agreeing with the
  HV-convex-by-area constant in every one of the 49 significant digits
  measured (`convex_growth.py` trusted-digit count 51). That agreement is a
  theorem, Proposition 6 below.
- `d_n/d_(n−1)` is 0.803651401483 for this class against 0.481008794 for
  unrestricted HV-convex, both flat to all digits printed, both `θ = 0`. The
  diagnostic reports the largest correction present: the 4-cone series carries
  0.481008794 as well, behind an extra exponential at
  `0.803651401483 = 2.5145796…/µ` ("Every class between staircase and
  HV-convex" below).
- Amplitude `C = 0.45030318571234118235` against 0.97445221313500464915. The
  ratio `a_dir4(n)/a_HV(n)` converges to the amplitude ratio; extrapolated
  directly (`experiments/ratio_amplitude.py`, Aitken on the ratio sequence,
  `n = 600` against `n = 700`) it is
  0.462109049209942440035662387700305832841163439729980425 to 54 trusted
  digits, later 251 by the identity of Proposition 11. PSLQ at 54 digits finds
  no integer relation in any in-capacity box (degree ≤ 12 at height ≤ 1e2,
  ≤ 5 at 1e4, ≤ 3 at 1e6, ≤ 2 at 1e8).
- Not D-finite at order ≤ 24 / degree ≤ 24 and not algebraic at degree ≤ 20 /
  t-degree ≤ 20, the boxes cleared for the unrestricted series.
- A bijection with the unrestricted class is ruled out, not by different
  subdominant singularities (that reading of Table B was wrong) but because
  the 4-cone class splits into a half growing at `µ` and a half growing at
  2.5145796… with no counterpart on the unrestricted side (Proposition 7).

No OEIS match on nine terms or the six-term prefix.

### Novelty checks and staged material

Re-checked 2026-08-05 with `experiments/oeis_lookup.py` (oeis.org answers 403
to some clients; a plain User-Agent gets through): HV-convex by area
(1,4,16,61,221,766,2566,8390), HV-convex by semiperimeter
(1,2,9,36,154,668,2916,12740) and control B unfiltered
(1,4,20,106,576,3179,17736,99748) all return no match. The multi-directed
row is A222205: the entry has 23 terms, no b-file, no growth constant, and a
formula line pointing at Bacher's Theorem 9; the extension is 200 terms and a
twelve-digit growth constant.

b-files in OEIS format, none submitted:

| file | sequence | terms |
|---|---|---|
| `results/b222205_upload.txt` | A222205, multi-directed animals | 200 (n = 1..200) |
| `results/b_hvconvex_area_upload.txt` | HV-convex polyplets by area | 700 (n = 1..700) |
| `results/b_hvconvex_perimeter_upload.txt` | HV-convex polyplets by semiperimeter | 199 (s = 2..200) |
| `results/b_ccdir5_upload.txt` | (dir5, column-convex) | 700 (n = 1..700) |
| `results/b_ccctrlb_upload.txt` | (ctrlB, column-convex) | 250 (n = 1..250) |
| `results/b_hvdir4_upload.txt` | (dir4, HV-convex) | 700 (n = 1..700) |
| `results/b_ctrlb_unfiltered_upload.txt` | control B unfiltered | 14 (n = 1..14, brute-force bound) |

Draft OEIS comments, staged and jasonp's call, all quoted in this file:
A055834 (4-cone directed king animals, conjecture-grade), A007052 (directed
column-convex polyplets with the Temperley derivation), A225114 (staircase
king animals = skew shapes with no empty rows or columns, with the bijection),
A018902 (above), and the A187077 correction with its derivation. Earlier
drafts of the A007052 and A225114 comments are in
`oeis/draft-comments-subfamilies.txt`; the versions in this file are current.
`oeis/SUBMISSION.md` records the pacing; the comment-grade edits go in the
discuss-first wave.

## Directed king animals and the two controls

### Bacher's directed class, A047781

Source: Axel Bacher, *Directed and multi-directed animals in the king's
lattice*, arXiv:1301.1365 (v3, 2015),
`papers/bacher_2015_directed_multidirected_king_lattice.pdf`. Exact results,
verified against the paper and OEIS:

- count `d(n) = 1, 4, 19, 96, 501, 2668, 14407, 78592, …` = A047781;
- generating function `D(t) = ¼·((1+t)/√(1−6t+t²) − 1)`;
- growth constant exactly `3 + 2√2 ≈ 5.8284` (singularities at `t = 3 ± 2√2`;
  `√(1−6t+t²)` is the Schröder radical);
- half-animals (left width 0) are the small Schröder numbers A001003
  (1, 1, 3, 11, 45, 197).

Independent re-derivation: `1/√(1−6t+t²) = Σ Pₙ(3) tⁿ` (Legendre polynomials
at 3) `= 1 + 3t + 13t² + 63t³ + 321t⁴ + 1683t⁵ + …`; multiply by `(1+t)`,
subtract 1, divide by 4: `t + 4t² + 19t³ + 96t⁴ + 501t⁵`, which is A047781.

Context: half-animals are Motzkin, Catalan and small-Schröder on the square,
triangular and king lattices, with directed growth constants 3, 4 and
`3+2√2`; all three share `µⁿ n^(−1/2)` asymptotics. No exact reduction or
bijection between undirected and directed animals is known on any lattice.
Directedness is solvable because a forward cone imposes a layer order that
turns the global connectivity constraint into layer-to-layer compatibility
(a one-dimensional transfer matrix, Viennot's heaps of pieces, Dhar's
hard-particle gas), which is exactly the part of the undirected problem that
is hard.

### The enumerate-and-filter check against the closed form

Filtering the fixed king-animal enumeration down to directed animals must
reproduce A047781, and A047781 has a closed form, so the reference side is a
formula available at any `n`. Tools: `cpp/directed_cone_anchor.cpp`
(`build/directed_cone_anchor`, modes `dir5 cone5 dir4 dir5nb mdir mdirbad grid
gridperim`), driver `experiments/directed_cone_anchor.py`, log
`experiments/directed_cone_anchor.log`. The bottom-row contiguity is a
consequence of the cone: no cone step decreases `y`, so a bottom-row cell can
be entered only from another bottom-row cell by W or E, and every cell of that
run has the same forward-reachable set, so Bacher's source choice involves no
double count.

| route | what it is | reach |
|---|---|---|
| **filter** | Redelmeier untried-set DFS over ALL fixed king animals, O(cells) BFS directedness test applied to every animal generated | n <= 15 |
| **cone growth** | same DFS with the step set restricted to the cone (bottom row may not grow west), no filter -- each directed animal generated once | n <= 17 |
| **brute** | from-scratch Python: frozenset growth + explicit translation canonicalisation + dict reachability; shares no code with the C++ | n <= 9 |
| **closed form** | `D(t) = 1/4 ((1+t)/sqrt(1-6t+t^2) - 1)`, three independent evaluations | n <= 25 |

The closed form is computed three ways that must agree: the Legendre
recurrence `(n+1)P_{n+1}(3) = 3(2n+1)P_n(3) − n P_{n−1}(3)` with
`d(n) = (P_n + P_{n−1})/4`; an exact `Fraction` series square root of
`1/(1−6t+t²)`; and the central Delannoy sum `P_n(3) = Σ_k C(n,k) C(n+k,k)`.
All three agree through `n = 25` and with the 8 published terms.

| n | A006770 (all fixed king animals) | filter -> directed | cone growth | closed form `[t^n] D(t)` |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 |
| 2 | 4 | 4 | 4 | 4 |
| 3 | 20 | 19 | 19 | 19 |
| 4 | 110 | 96 | 96 | 96 |
| 5 | 638 | 501 | 501 | 501 |
| 6 | 3832 | 2668 | 2668 | 2668 |
| 7 | 23592 | 14407 | 14407 | 14407 |
| 8 | 147941 | 78592 | 78592 | 78592 |
| 9 | 940982 | 432073 | 432073 | 432073 |
| 10 | 6053180 | 2390004 | 2390004 | 2390004 |
| 11 | 39299408 | 13286043 | 13286043 | 13286043 |
| 12 | 257105146 | 74160672 | 74160672 | 74160672 |
| 13 | 1692931066 | 415382397 | 415382397 | 415382397 |
| 14 | 11208974860 | 2333445468 | 2333445468 | 2333445468 |
| 15 | 74570549714 | 13141557519 | 13141557519 | 13141557519 |
| 16 | -- | -- | 74174404608 | 74174404608 |
| 17 | -- | -- | 419472490257 | 419472490257 |

Zero mismatches on every route at every `n` in range; the unfiltered totals
match A006770 through `n = 15`. No b-file for A047781 or A055834 exists in
`fixtures/`, so the driver hard-codes the published terms with their
provenance.

Controls, all fail-closed (an empty comparison fails; the divergence checks
fail if they do not diverge):

| control | what changed | n=1..6 | vs A047781 |
|---|---|---|---|
| **A: wrong cone** | 4-step `{N, NE, E, SE}`, source = bottommost of leftmost column | 1, 4, **18**, 85, 413, 2044 | **diverges at n=3, 18 vs 19** |
| **B: bottom row waived** | same 5-step cone, BFS seeded from *every* bottom-row cell | 1, 4, **20**, 106, 576, 3179 | **diverges at n=3, 20 vs 19** |
| C: no filter | filter removed entirely | 1, 4, 20, 110, 638, 3832 | = A006770, diverges at n=3 |

The `n = 3` split is the single animal `{(0,0), (1,1), (2,0)}`, whose bottom
row is split: not directed, dropped by control A along with one more, kept by
control B. Control A reproduces A055834 and, run to `n = 14`, confirms the
values 36196706, 187938842, 978599560 obtained by direct cone growth in
`experiments/directed_halfplane.cpp`. Control B is a third sequence, matching
neither A047781, A006770 nor the multi-directed class.

Cost, gympie, 8 threads, 2026-07-31; work scales as A006770 (about 6.7x per
term) for the filter route and as A047781 (about 5.83x) for cone growth:

| run | mode | n | wall | CPU | peak RSS |
|---|---|---:|---:|---:|---:|
| filter | `dir5` | 15 | 457.6 s | 3484 s | 1.8 MB |
| cone growth | `cone5` | 17 | 194.8 s | 1505 s | 1.8 MB |
| control A | `dir4` | 14 | 81.0 s | 633 s | 1.8 MB |
| control B | `dir5nb` | 14 | 84.6 s | 629 s | 1.8 MB |
| brute | Python | 9 | 21.6 s | 21.5 s | -- |

`n = 16` by the filter route is about an hour and `n = 18` by cone growth
about 40 minutes; neither was run. Scope: this validates the enumeration and
per-animal predicate machinery (canonical-translate DFS, cell-set bookkeeping,
sharded parallel decomposition) against an exact formula on a subfamily. It is
not a check of `a(n)`: the frontier engine shares no code with this tool, and
directedness discards the connectivity that makes the undirected count hard.
The binary's stamp reads `ce506bc-dirty` from concurrent unrelated edits; the
source was unmodified.

### The 4-cone class, A055834

Model: `n`-cell sets containing the origin, every cell reachable from the
origin by steps `(0,1), (1,0), (1,1), (1,−1)` within the set, the four-step
forward cone `{N, NE, E, SE}`. Terms 1, 4, 18, 85, 413, 2044, …, diverging
from Bacher's five-step class at `n = 3` (18 against 19), with growth
`27/5 = 5.4` (Kotesovec's asymptotic on the entry). Verification: a
Redelmeier-style DFS (`experiments/directed_halfplane.cpp`, about 6 s to
`n = 15`) matches Alekseyev's formula `a(n) = Σ_k C(n+k−1,n)·C(k,n−k)` and the
A055834 data (offset 0) exactly for all `n ≤ 15`, including 36196706 (n=12),
187938842 (n=13), 978599560 (n=14), 5108177816 (n=15). The entry (Kimberling
2000) is defined only as the array diagonal `T(2n,n)` of A055830, with no
combinatorial interpretation; an OEIS search on the terms hits A055834
uniquely. Draft comment, staged, jasonp's call:

> Conjecture: for n >= 1, a(n) is the number of n-celled directed
> polyplets in the four-step cone (directed site animals on the king
> lattice with steps (0,1), (1,0), (1,1), (1,-1)), i.e., sets of n cells
> of Z^2 containing the origin such that every cell can be reached from
> the origin by those steps without leaving the set. Verified for n <= 15.
> Cf. A006770, A030222, A047781.

Prior art: Bacher's paper is the five-step model only. The quarter-cone
variant with steps `(1,0), (0,1), (1,1)` is `C(2n−1, n−1)` = A001700, which
already cites the directed-animal literature (Bousquet-Mélou, Discr. Math.
180 (1998) Eq. (1); Baril, Bevan and Kirgizov); do not claim it. The comment
stays conjecture-grade until the four-step cone has a heaps-of-pieces
derivation; the generating function is algebraic via A001002 (Kruchinin's
formula on the entry), so one likely exists.

### Control B

Control B floods the five-step cone from every cell of the global bottom row.
It was written as a control for the directed filter, turned out to be a class
of its own, and is not the multi-directed class: the two are incomparable
(next section). Its unfiltered row of the grid has no transfer matrix and is
known only to `n = 14` by brute force (`results/b_ctrlb_unfiltered_upload.txt`).

## Multi-directed king animals, A222205

### Bacher's Definition 2

For an animal `A` and abscissa `i`, let `b(i)` be the ordinate of the
bottommost site of `A` in column `i` (`+∞` if that column is empty; the
occupied columns form an interval, so the only `+∞` values are the two
sentinels past the ends).

- A **source** is a site realizing a local minimum of `b`.
- A **keystone** is a site realizing a local maximum of `b`.
- On a plateau of equal `b`, the leftmost column takes the mark. With `+∞`
  sentinels the extrema alternate source, keystone, …, source: `s` sources and
  `s−1` keystones.

`A` is **multi-directed** iff both hold:

1. every site of `A` is reachable from some source by a forward-cone path
   (`{W, NW, N, NE, E}`) staying inside `A`;
2. every keystone `t` is reachable from a source strictly to its left and
   from one strictly to its right, along paths that pass through no other
   keystone at `t`'s own height.

A directed animal has one source and no keystone, so directed ⊂
multi-directed. Proposition 3 of the paper is a bijection with connected heaps
of segments (heaps with no empty column), which is where the enumeration comes
from. Two things the repository had assumed are not in the definition: the
sources are not confined to the global bottom row, and a split bottom row is
neither necessary nor sufficient.

### Control B is incomparable with multi-directed

Cross-tabulation by a from-scratch Python brute force over all fixed king
animals (`python3 experiments/multidirected_king.py 12 --crosstab 8`):

| n | both | multi-directed only | control B only | neither | m(n) | all (A006770) |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 0 | 0 | 1 | 1 |
| 2 | 4 | 0 | 0 | 0 | 4 | 4 |
| 3 | 20 | 0 | 0 | 0 | 20 | 20 |
| 4 | 106 | 4 | 0 | 0 | 110 | 110 |
| 5 | 576 | 60 | 0 | 2 | 636 | 638 |
| 6 | 3179 | 611 | 0 | 42 | 3790 | 3832 |
| 7 | 17732 | 5304 | **4** | 552 | 23036 | 23592 |
| 8 | 99670 | 42276 | **78** | 5917 | 141946 | 147941 |

Multi-directed but not control B, smallest witness at `n = 4` (four of them):

```
.X.      b = (0, 2, 1);  sources (0,0) and (2,1);  keystone (1,2)
X.X
X..
```

`(2,1)` is a source (column 2's bottom is a local minimum of `b`) but is not
on the global bottom row and no cone path reaches it from `(0,0)`.

Control B but not multi-directed, smallest witness at `n = 7` (four of them):

```
...X.    b = (0, 1, 2, 0, 1);  sources (0,0) and (3,0);  keystone (2,2)
..X.X
.X..X
X..X.
```

Every cell is reachable from the bottom row `{(0,0), (3,0)}`, but the
keystone `(2,2)` is reachable only from the left source; walking back from it
hits nothing at `(3,2)`, `(3,1)` or `(2,1)`, so condition 2 fails.

### Terms by three routes

| route | what it is | reach |
|---|---|---|
| **generating function** | `M = D/(1−B)` from the Nordic decomposition (Theorem 8), exact integer power series | n = 400 in 30 s; n = 200 in 2.1 s |
| **brute force (C++)** | Redelmeier DFS over ALL fixed king animals, Definition 2 evaluated on each | n = 14, 162.5 s wall / 1290.5 s cpu, 8 threads |
| **brute force (Python)** | from-scratch frozenset growth, dict reachability, shares no code with either | n = 8 |

```
S = t(1+S)^2 / (1 - t(1+S))            half-animals, A001003
R = S + t(1+S)
D = S + S^2/(1-R)                      directed, A047781
Q = (2-2t)S - t
B = sum_{k>=0} S(1+S)^k * QR^k/(1-QR^k)
M = D/(1-B)
```

`v(S) = v(R) = v(Q) = 1`, so the `k`-th summand of `B` has valuation `k+2`
and only `k ≤ N−2` matters mod `t^(N+1)`. Zero mismatches: series against C++
for every `n = 1…14`, Python against both for `n = 1…8`, unfiltered totals
equal to A006770 through `n = 14`.

| n | m(n) multi-directed | d(n) directed A047781 | control B | all A006770 |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1 | 1 |
| 2 | 4 | 4 | 4 | 4 |
| 3 | 20 | 19 | 20 | 20 |
| 4 | 110 | 96 | 106 | 110 |
| 5 | 636 | 501 | 576 | 638 |
| 6 | 3790 | 2668 | 3179 | 3832 |
| 7 | 23036 | 14407 | 17736 | 23592 |
| 8 | 141946 | 78592 | 99748 | 147941 |
| 9 | 883360 | 432073 | 564430 | 940982 |
| 10 | 5538098 | 2390004 | 3209194 | 6053180 |
| 11 | 34917224 | 13286043 | 18316729 | 39299408 |
| 12 | 221125102 | 74160672 | 104872413 | 257105146 |
| 13 | 1405276324 | 415382397 | 602013085 | 1692931066 |
| 14 | 8956020294 | 2333445468 | 3463412836 | 11208974860 |

`m(n) = A006770(n)` for `n ≤ 4`; the first two non-multi-directed animals
appear at `n = 5`. Full list `n = 1…200`: `results/multidirected_terms_n200.txt`.

### Growth constant

Two singularities not to be conflated: `ρ_B ≈ 0.16346`, the pole of the
intermediate series `B`, the root of `ρ³ − 7ρ² − 5ρ + 1 = 0` (Bacher Lemma 11),
with `1/ρ_B ≈ 6.118`, which is not the growth constant; and `ρ_M ≈ 0.15444`,
the radius of `M`, defined transcendentally by `B(ρ_M) = 1` (Theorem 10), with
`µ = 1/ρ_M` (Corollary 12). Measured on the 400-term series:

```
m(50)/m(49)   = 6.473424386397
m(100)/m(99)  = 6.475173428889
m(200)/m(199) = 6.475196273747
m(300)/m(299) = 6.475196280295
m(400)/m(399) = 6.475196280297     Aitken-extrapolated: 6.475196280297
```

`µ = 6.475196280297`. `M` has a simple pole, so `m(n) ~ Cµⁿ` with no
subexponential factor, and the ratios converge geometrically at rate
`ρ_M/ρ_B = 0.9448`. This confirms and extends Bacher's numerical `6.475…`; it
stays numerical, with no minimal polynomial, because `ρ_M` is defined through
the non-D-finite `B`. Consistency with the growth-constant bracket:
`6.4752 < 6.543`, the certified strip lower bound (`results/growth-constant.md`),
as multi-directed ⊂ all polyplets requires.

Lower bounds on the polyplet growth constant `λ` from these families, in the
order they were obtained:

| bound | value | form | note |
|---|---|---|---|
| directed (lower) | 5.8284 | `3+2√2` (exact algebraic) | fully rigorous |
| **multi-directed (lower)** | **6.4752** | `1/ρ_M`, `B(ρ_M)=1` | tighter, but numerical |
| polyplet λ | ~7.11 | unknown | heuristic only |
| **Bui certificate (upper)** | **9.3154** | `20000/2147`, exact cert | fully rigorous |

These were the first rigorous statements about `λ`; the floor is now the
certified strip constant 6.543 (`results/growth-constant.md`), and `3+2√2`
remains the best closed-form bound. The upper bound is
`docs/proofs/polyplet-upper-bound.md`. Convex polyplets' 3.129 is a valid but
weak lower bound, of no use for the bracket.

### Tools and controls

| file | role |
|---|---|
| `experiments/multidirected_king.py` | the GF scheme, the from-scratch Python brute force, `--crosstab` |
| `cpp/directed_cone_anchor.cpp` modes `mdir` / `mdirbad` | Definition 2 on the Redelmeier enumeration; `mdirbad` drops condition 2 |
| `tests/gate_multidirected.py` (`make gate-multidirected`) | the gate |
| `results/multidirected_terms_n200.txt` | n = 1…200 |

| control | what changed | n = 1…8 | verdict |
|---|---|---|---|
| **mdirbad** | Definition 2's condition 2 (keystone two-sided) dropped | 1, 4, 20, 110, 636, **3792**, 23082, 142596 | diverges at n=6, 3792 vs 3790 |
| **dir5nb** (control B) | sources = global bottom row instead of local minima of `b` | 1, 4, 20, **106**, 576, 3179, 17736, 99748 | diverges at n=4, 106 vs 110 |
| **dir5** | Bacher directed (one source, no keystone) | 1, 4, **19**, 96, 501, 2668, 14407, 78592 | strict subset, diverges at n=3 |

`mdirbad` isolates condition 2 and is a strict superset termwise. The gate
also checks `B(1/µ) = 0.999979 ≈ 1` on the computed `B` series, and that the
ratio is not drifting to `1/ρ_B`. A latent bug fixed in the process: the
generation stamps in `directed_cone_anchor.cpp` are `uint32_t` and were
incremented without a wrap guard; `mdir` burns one generation per keystone per
animal, so `bump()` now zeroes the marker array on wrap. No recorded run had
wrapped.

## Column-convex, staircase and the grounded families

Classifier and checks: `experiments/king_subfamilies.py`.

| subfamily (king lattice) | first terms | identity |
|---|---|---|
| column-convex | 1,4,18,83,385,... | A187077 (Bevan; derivation below) |
| bargraph (grounded columns) | 2^(n-1) | compositions -- king contact trivializes connectivity |
| Ferrers (grounded, monotone) | 1,2,3,5,7,11,... | partitions A000041 (trivially) |
| stack (grounded, unimodal) | 1,2,4,8,15,27,47,79 | unimodal compositions A001523 |
| **directed column-convex** | 1,3,10,34,116,396,... | **A007052** -- new interpretation |
| **staircase (both boundaries monotone)** | 1,3,9,28,87,272,... | **A225114 = skew shapes** -- new, with proof |
| **4-cone directed column-convex** | 1,4,17,73,314,1351,... | **A018902** -- new interpretation (above) |

**Theorem (dcc).** Directed column-convex polyplets (column intervals,
bottoms nondecreasing) with `n` cells are counted by A007052
("order-consecutive partitions"): placements of a height-`h'` column against
height-`h` are `h+1` (bottom shift in `[0,h]`, king reach caps at `top+1`),
independent of `h'`, so Temperley's method closes to
`GF = x(1−x)/(1−4x+2x²)`, `a(n) = 4a(n−1) − 2a(n−2)`, growth exactly `2+√2`.
Matches A007052's generating function (offset 1 against 0); 10 terms verified.
A007052 previously had poker, Pell and path interpretations but no
lattice-animal one.

**Theorem (staircase).** King staircase animals (column intervals, bottoms and
tops nondecreasing) are the skew Young diagrams with no empty rows or columns
(A225114), by the identity map: monotone boundaries make the columns a skew
shape; "no empty rows" forces `bottom_{i+1} ≤ top_i + 1`, which is exactly
king contact, and conversely. 8 terms verified against the entry; the animal
side is brute-forced to `n = 14` (1, 3, 9, 28, 87, 272, 850, 2659, 8318,
26025, 81427, 254777, 797175, 2494307, `results/mk_grid20_n14.txt`). Draft
comment, staged, jasonp's call:

> a(n) is also the number of staircase polyplets with n cells: king-lattice
> animals (sets of cells of Z^2 joined by edge or corner contact, counted up
> to translation) in which every column is a contiguous interval and both the
> column bottoms and the column tops are nondecreasing from left to right.
> The identity is the identity map on diagrams. Monotone bottoms and tops
> make the occupied columns a skew shape; a diagram with no empty row is one
> in which bottom(j+1) <= top(j) + 1 for every pair of consecutive columns,
> and that inequality is exactly corner contact between those columns, so the
> no-empty-row condition and king-connectivity are the same condition.
> Verified for n <= 8. Cf. A006770, A007052, A018902, A187077.

**Column-convex polyplets (A187077), derived.** Temperley's method with the
last column's height as catalytic variable (king contact gives `h+h'+1`
placements) closes to a 2×2 linear system:
`GF = x(1−x)³/(1−7x+13x²−10x³+2x⁴)`, growth 4.64468… (quartic root).
Brute-validated `n ≤ 8`; tool `experiments/colconvex_king.py`. This is
A187077 (row-convex polyplets, the transpose), same generating function. The
derivation agrees with the functional equation, with the brute force (which
reproduces A006770 for `n ≤ 8` as control) and with Bevan's 23 published
terms; the brute-force grid column above agrees through `n = 14`. By
Proposition 5, A187077 is simultaneously the (multi-directed, column-convex)
class of the grid.

**The A187077 entry's comment is wrong in its plain reading.** The entry says
"Equivalent to a sequence of row-convex polyhexes (A059716)". Brute-forcing
the hexagonal lattice, with all fixed polyhexes reproducing A001207 as control,
gives row-convex polyhexes = A059716 = 1, 3, 11, 42, 162, …, against A187077
= 1, 4, 18, 83, 385, …. The structural reason: a king row-interval has
`h+h'+1` placements against the next row, a hexagonal brick-row has `h+h'`.
The entry carries no derivation. Draft correction comment, staged, jasonp's
call:

> The comment "Equivalent to a sequence of row-convex polyhexes (A059716)" is
> not correct in its plain reading. Row-convex polyhexes are counted by
> A059716 itself, 1, 3, 11, 42, 162, ..., while this sequence is 1, 4, 18,
> 83, 385, ..., so the two agree only at the first term, and their generating
> functions differ. Checked by direct enumeration on both lattices, with all
> fixed polyhexes reproducing A001207 as a control. The two classes are
> analogous but not equinumerous, and one placement is the whole difference:
> a row of length h admits h + h' + 1 positions for a length-h' row beside it
> on the king lattice, against h + h' on the hexagonal lattice. What this
> sequence counts is row-convex polyplets -- king-lattice animals (sets of
> cells of Z^2 joined by edge or corner contact, counted up to translation)
> in which every row is a single contiguous run. Column-convex polyplets are
> the transpose and give the same counts. Verified for n <= 14 by direct
> enumeration.

Draft formula line for the same edit:

> The g.f. follows from Temperley's method with the height of the last column
> as catalytic variable (working with the transposed, column-convex form).
> Writing F(x,q) for the sum of x^cells * q^(height of the last column), the
> h + h' + 1 placement rule gives F(x,q) = t/(1-t) + A*t*(2-t)/(1-t)^2 +
> B*t/(1-t) with t = q*x, A = F(x,1), B = F_q(x,1); the two equations
> obtained at q = 1 solve to A(x) = x*(1-x)^3/(1 - 7x + 13x^2 - 10x^3 + 2x^4).

## Convex polyplets by area

A convex polyplet is an HV-convex king animal. The original finding, with its
row transfer matrix (state `(left-phase, right-phase, width)`), the first 38
terms and the first non-D-finiteness verdict (no P-recurrence of order ≤ 6,
degree ≤ 5, with the convex-polyomino control failing the same test), is
`docs/proofs/convex-mirage.md`: convexity is the classical tractability lever
by perimeter and not by area. What follows strengthens every part of it.

### Series and tools

- 1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174, 853111,
  2677214, 8389720, 26271014, 82230035, 257333334, 805229818, 2519563026,
  7883577553, …
- Brute-force cross-check of the first ten terms by Redelmeier growth plus an
  HV-convex filter, reproducing A006770 through `n = 10`
  (`experiments/convex_polyplets.py`).
- `experiments/convex_tm.py`: the row transfer matrix (row intervals,
  unimodal-envelope phase automaton, unique parse), restored 2026-07-13 after
  the original tool was lost; regenerates the 38 terms. Its inner offset loop
  was a box convolution collapsible to `O(1)` sub-intervals per phase target,
  which took `n = 128` from 110.7 s to 8.3 s with every term unchanged.
- `cpp/convex_area_tm.cpp` (`build/convex_area_tm N [king]`): the same DP on
  `mpz_class`, identical to the Python at `n = 128` and `n = 200`. `king = 0`
  switches to edge adjacency (`dl` in `[−wp+1, w−1]` instead of `[−wp, w]`,
  the rule `cpp/convex_perim_tm.cpp` already used for its own control) and
  reproduces A067675, fixed convex polyominoes by area.
- Not in OEIS; no king convex enumeration in the literature, all classical
  convex work being edge-connected. Classical anchors: Bender 2.30914 for
  convex polyominoes by area, Temperley 3.2056 for column-convex polyominoes.

| n | tool | wall_s | peak_rss_mb |
|---|---|---|---|
| 100 | convex_tm.py (prefix-sum) | 3.07 | 17.2 |
| 128 | convex_tm.py (prefix-sum) | 8.31 | — |
| 200 | convex_tm.py (prefix-sum) | 47.92 | 23.3 |
| 128 | convex_area_tm (C++/GMP) | 0.30 | 6.6 |
| 200 | convex_area_tm (C++/GMP) | 1.65 | 14.2 |
| 500 | convex_area_tm (C++/GMP) | 75.6 | 108.4 |

| series | file | wall_s | peak_rss_mb |
|---|---|---|---|
| king, n=700 | `results/convex_area_terms_n700_king.txt` | 484.5 | 271.9 |
| control (A067675), n=700 | `results/convex_area_terms_n700_poly.txt` | 409.9 | 225.6 |

Both 700-term runs on gympie, concurrently; the king file's first 500 lines
equal `results/convex_area_terms_n500.txt`. The ratio at `n = 496..500` is
3.128943269730886, flat to 16 digits.

### Not D-finite and not algebraic in the box (24, 24)

Both series are excluded at order ≤ 24 and degree ≤ 24 on 700 terms, and
separately shown to satisfy no algebraic equation of degree ≤ 24 in either
variable. Two facts make this one test rather than 625: the boxes nest, so the
maximal box settles every box inside it; and full column rank mod `p` is a
proof over `Q`. Algebraicity is tested separately even though algebraic
implies D-finite, because a degree-24 algebraic function can induce an ODE
outside the excluded box.

| series | mode | box | unknowns | rows | rank | verdict |
|---|---|---|---|---|---|---|
| king | prec | (20,20) | 441 | 680 | 441 | EXCLUDED |
| king | prec | (24,24) | 625 | 676 | 625 | EXCLUDED |
| king | prec | (20,20), skip 50 rows | 441 | 630 | 441 | EXCLUDED |
| king | prec | (20,20), second prime | 441 | 680 | 441 | EXCLUDED |
| king | alg | (20,20) | 441 | 701 | 441 | EXCLUDED |
| king | alg | (24,24) | 625 | 701 | 625 | EXCLUDED |
| control | prec | (20,20) | 441 | 680 | 441 | EXCLUDED |
| control | prec | (24,24) | 625 | 676 | 625 | EXCLUDED |
| control | prec | (20,20), skip 50 rows | 441 | 630 | 441 | EXCLUDED |
| control | prec | (20,20), second prime | 441 | 680 | 441 | EXCLUDED |
| control | alg | (20,20) | 441 | 701 | 441 | EXCLUDED |
| control | alg | (24,24) | 625 | 701 | 625 | EXCLUDED |

`(25,25)` is the first box 700 terms cannot decide (676 unknowns, 675 rows).
The skipped rows test "holds eventually" rather than "holds from `n = 1`".
The 500-term file reproduces the earlier (6,5) exclusion directly.

The guesser is kept powered by `make gate-convex-dfinite`
(`tests/gate_convex_dfinite.py`, about 4 s), four arms:

| arm | series | box | must be | is |
|---|---|---|---|---|
| prec + | HV-convex by semiperimeter (order-5 degree-2 recurrence) | (5,2) | CANDIDATE | nullity 1, predicts all 172 withheld rows |
| prec - | same series | (2,1) | EXCLUDED | rank 6 of 6 |
| alg + | A005436, algebraic by Delest-Viennot | (2,8) | CANDIDATE | nullity 1, holds on all 69 withheld rows |
| alg - | same series | (2,4) | EXCLUDED | rank 15 of 15 |

The A005436 control series is `results/a005436_perim_s100.txt`
(`build/convex_perim_tm 100 0`).

### µ, θ and the amplitude

`experiments/convex_growth.py <terms_file>`. The discriminator is the ratio of
successive differences of `r_n = a(n+1)/a(n)`: constant below 1 means a
geometric correction (isolated subdominant singularity), drift toward 1 a
branch point and `θ ≠ 0`. Over the last five `n` of each 700-term series:

| series | d_n/d_(n-1) | reading |
|---|---|---|
| king | 0.48100879371, constant to all 12 printed digits | geometric |
| control | 0.625135968591, constant to all 12 printed digits | geometric |

The direct probe `n (r_n/µ − 1)` is at the `1e−216` (king) and `1e−137`
(control) level. `θ = 0` for both, and

```
a(n) = C mu^n (1 + O(rho^n)),   rho = 0.481008794 (king), 0.625135969 (control)
```

µ, convex polyplets by area, 199 trusted digits:

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549
```

µ, convex polyominoes by area (A067675), 121 trusted digits, reproducing
Bender's 2.30914 and extending it:

```
2.309138593330494731098720305017212531911814472581628401694402900284456440748316
842717281615774412174374610237798122137142
```

Amplitudes, stable to all 40 printed digits between `n = 699` and `700`:

```
C_king    = 0.9744522131350046491513294208602433274254
C_control = 2.919598509713607055384709515651335685915
```

### µ is not algebraic in the searched boxes

PSLQ on `(1, µ, …, µ^d)` at the trusted precision. A hit is reported as an
artifact unless `(d+1) log10(height)` is below half the trusted digit count;
a 137-digit run manufactured a degree-6 "relation" of height `7e11` that way.

| mu | precision fed | degree <= | height <= | result |
|---|---|---|---|---|
| king | 199 | 20 | 1e8 | none at any degree |
| king | 199 | 30 | 1e6 | none at any degree |
| king | 199 | 12 | 1e15 | none at any degree |
| king | 137 (500-term series) | 20 | 1e5 | none at any degree |
| control | 121 | 12 | 1e8 | none at any degree |
| control | 121 | 20 | 1e4 | none at any degree |
| control | 121 | 20 | 1e8 | hits at degree 15-20, all REJECTED-ARTIFACT (capacity 125-142 vs 121 trusted) |

A worked rejection: the cubic `3219x³ − 7630x² − 18493x + 33955`, offered
from a 16-digit value of µ, has nearest root
3.12894326973088625330312785623831607097 against
µ = 3.12894326973088625227744799538775416053: agreement to 18 digits and
disagreement at the 19th. A degree-3 relation of height `3.4e4` absorbs about
18 digits of input, so any 16-to-18-digit decimal admits such a cubic.

### The area generating function as a q-series

Imported 2026-08-17 from the Ghost Ship experiment, fourteen unattended
sessions run against a sandbox cut at `74b2c20` and blind to everything above
dated 2026-08-05 or later; the record of that experiment is
`docs/lessons-learned.md`, and its receipts are readable with
`git show e5e7870:results/ghostship/grading/run-record/sandbox/<path>`
(abbreviated `GS/` below). The loop independently re-derived the
semiperimeter series to `s = 200` and its degree-2 algebraicity, matching
`results/convex_perim_terms_s200.txt` on all 199 shared terms; nothing below
claims those.

**The bivariate box generating function, derived.** From an explicit
four-phase catalytic functional equation, eliminating the catalytic variable
with no fitting anywhere:

    F(x,y) = Sum_{w,h} f(w,h) x^w y^h
           = -(M + 2x^2 y^2 (1+x+y)^2 sqrt(D)) / (2 K D^2)
      D = (1-x-y)^2 - 4xy,  K = x + y + xy

`f(w,h)` = translation classes with bounding box exactly `w × h`. The king
modification is absorbed by the factor `K = x+y+xy` and the weight
`(1+x+y)²`. Derivation: `GS/docs/proofs/convex-box-kernel.md`; note
`GS/results/convex-box.md`. Specializing, the univariate closed form solves
the quadratic recorded under "Convex polyplets by semiperimeter":

    F(t) = [t^2(2 - 10t + 14t^2 - 5t^3 - 4t^4) - t^3 (1+2t)^2 sqrt(1-4t)]
           / ((2+t)(1-4t)^2)

Verified 2026-08-17 from this expression alone in exact `Fraction`
arithmetic: it reproduces all 200 terms of `GS/king_semiperim_200.txt` and
hence all 199 of `results/convex_perim_terms_s200.txt`. The discriminant
factors as `4t⁶ (1−4t)⁵ (1+2t)⁴`, so `√(1−4t)` is the only radical, the same
radicand as classical convex polyominoes. Asymptotics: `a(s) ~ (s/128) 4^s`,
next order `−(1/64)(2s+1)C(2s,s)`, term for term the shape of A005436's exact
formula `(2n+3)4^(n−4) − 4(n−3)C(2n−7,n−4)`. Measured ratio king/A005436:
1.2440 (s=8), 1.0990 (20), 1.0450 (40), 1.0207 (80), 1.0076 (201), tending
to 1 roughly as `1 + 1.5/s`; the limit is measured, not proved.

**Fixed-height structure.** `f(w,h)` is a polynomial in `w` of degree
`2h−2` for all `w ≥ 1`: `f(w,2) = 2w² − 1`,
`f(w,3) = w⁴ + (2/3)w³ − (1/2)w² − (13/6)w + 2`; `h = 4, 5` recorded
(`GS/out_row_polynomials.txt`). Fixed-height area generating functions are
rational with cyclotomic denominators: `A_2 = q²(3−q)/(1−q)³`,
`A_3 = q³(7+2q+3q²−4q³+2q⁴)/((1−q)⁴(1−q³))`, `A_4` with denominator
`(1−q)⁴(1−q³)²(1−q⁴)`; slices sum to the area sequence for `n ≤ 12`
(`GS/out_area_fixed_height.txt`, `GS/out_area_slices_check.txt`; mechanism
proved in `GS/docs/proofs/convex-area-q-temperley.md`). Row numerators satisfy
`N_h(1) = A153337`, proved at generating-function level, plus halving
identities at `x = −1` (`GS/docs/proofs/row-gf-specializations.md`).

**Certified constants.** The area generating function is a finite combination
of four q-adically convergent q-series from the q-deformed functional
equation, with 50-term predictions checked against an independent transfer
matrix and a control mode hitting the A067675/A067676 b-files 50/50; 60 exact
terms in `GS/out_s05_terms60.txt`. The growth constant is `µ = 1/q_c` with
`q_c` the smallest positive zero of the Temperley denominator

    K(q) = Sum_m (-1)^m (2 - q^m) q^{m(m+1)/2} / (q;q)_m^2

    mu = 3.128943269730886252277447995387754160532...
    A  = 0.974452213135004649151329420860243327425...

both certified to 44+ digits by exact-rational interval arithmetic with a
simple-pole certificate (`GS/out_s10_certify_amplitude.txt`,
`GS/results/convex-area-asymptotics.md`); control values reproduce the
published Kotesovec and Klarner–Rivest digits.

**The exponential spectrum is the reciprocal zero set of K.** The Prony
spectrum of the unrestricted and staircase series (next section) consists of
the next zeros of `K`, sign included (`experiments/convex_kernel_zeros.py`,
mpmath at 60 dps, sign changes on a grid then bisected, both signs scanned):

| Prony (measured) | zero of K | 1/q |
|---|---|---|
| `lambda_1 = 3.12894326973088...` | `q_1 = 0.3195967180593874655186029` | `3.128943269730886252277448` |
| `lambda_2 = 1.50504922775900...` | `q_2 = 0.6644300940833578091864194` | `1.505049227759003934665694` |
| `lambda_3 = 1.28433727098118...` | `q_3 = 0.7786116798090276393820133` | `1.284337270981181428551058` |
| `lambda_4 = -1.25776216033063...` | `q_4 = -0.795062875589391242237668` | `-1.257762160330635483241742` |

Agreement is to every digit printed (14; `λ_1` to 39). `λ_4` is negative and
comes from a negative zero the positive-axis scan never looked for. The
subdominant rate `ρ = λ_2/λ_1 = q_1/q_2 = 0.481008794` is thereby a ratio of
two zeros of `K`; the sharp asymptotic itself is still not proved.

**Two OEIS identifications on the directed-convex subfamily.**
`a_dir(s) = A014300(s−1)` (nodes of odd outdegree in ordered rooted trees) and
`d(n,n) = A112029(n−1) = Σ_k C(n−1+k,k)²`, both verified against b-files;
neither entry carries a polyomino, convex, king or polyplet interpretation
(`GS/results/directed-convex-king.md`). Absent from OEIS as of 2026-08-17
(the control query for A005436 hits): the semiperimeter series, the twist
`2, 5, 20, 81, 344`, the 60-term area series, and directed-convex king by
area `1, 3, 10, 33, 107, 342`.

**Lead, not result: non-D-finiteness of the area generating function.**
`K(q)` has at least 40 located real zeros in `(0,1)` accumulating at `q = 1`
under `K(e^−ε) ~ 2·3^(1/4) √(ε/2π) cos(V/ε − π/12)` with `V = 2 Cl₂(π/3)`, the
Gieseking constant; `F(1,1,q)` has poles at these zeros with nonzero residues
at the first four, and a D-finite generating function has finitely many
singularities. Two gaps: a rigorous steepest-descent treatment of the
oscillation near `q = 1`, and nonvanishing of the residue at infinitely many
zeros (`GS/results/K-oscillation-gieseking.md`).

**Published, do not re-derive.** The area-moment limit law
`c_r = (r!)²/2^(r+7)`, `E[area^r]/s^(2r) → (r!)²/((2r+1)! 2^r)`, i.e.
`area/s² → U(1−U)/2`, is Richard, *Limit distributions and scaling
functions*, arXiv:0704.0716, Table 1 (convex polygons carry the rectangles
law `β_{1,1/2}`). What survives is area-moment algebraicity for every `r` by
the same elimination (`GS/docs/proofs/area-moment-kernel.md`) and the
statement that king and polyomino give the identical law; Enting and
Guttmann, J. Phys. A 22 (1989), covers the control family.

**Negative attempt, 2026-08-18.** Whether the descending half's growth
constant `ν = 2.5145796…` (next section) is `1/(smallest zero of det)`, `det`
the 2×2 determinant of the s04 solution, could not be tested: `det` built as a
truncated q-series does not converge (smallest positive zero 1.2433 at 24
terms, no sign change at 32, 1.1794 at 40 and 48, king and control returning
identical values). Nothing is concluded; a convergent construction of `det` is
needed (`experiments/convex_det_zeros.py`).

### Fixed-height area generating functions and root recycling

Fixed-height convex-polyplet area generating functions were recovered exactly
for `H ≤ 7` (phase-automaton DP, brute-validated `n ≤ 8` including row sums,
Berlekamp–Massey with 12 to 15 withheld terms): denominator orders 1, 3, 7,
14, 25, 36, 53 (`results/convex_height_denominators.json`,
`experiments/convex_heights.py`). New-root content `ψ_H`, certified mod `p`,
has degrees 1, 2, 3, 5, 7, 6, 8, near-linear, with `ψ_2` not squarefree: the
convex family's strip spectra reuse earlier roots, the opposite of the full
family's root separation (`ψ` degrees 1, 2, 4, 9, 29, 68, 181, 462, 1254,
3289; `results/anisotropic-not-dfinite.md`). Consequences: the pole-argument
exclusion boxes for the convex anisotropic generating function are weak (with
three levels of `deg ψ > 5`, only `r ≤ 2` and `D ≤ 5`-class statements), so
this route does not strengthen the by-area verdict; and root separation is a
feature of the unrestricted family, not a default. The dominant poles
`1/µ_H` are strictly decreasing toward `1/3.129`, one new root per level
forever, which supports only order-0 exclusions.

## Convex polyplets by semiperimeter

For a convex animal the semiperimeter is the bounding box `W + H` and the
edge-perimeter is `2(W + H)`. By semiperimeter the class is D-finite and in
fact algebraic; by area it is neither. The wild/tame split is a property of
the statistic crossed with HV-convexity, and it survives the 4-cone
restriction.

### The unrestricted series

1, 2, 9, 36, 154, 668, 2916, 12740, …; 199 terms (`s = 2..200`) in
`results/convex_perim_terms_s200.txt`, from `cpp/convex_perim_tm.cpp`
(`build/convex_perim_tm SMAX [king] [mode]`), the C++/GMP port of
`experiments/convex_perimeter.py`'s box DP after its `O(W)` inner loop was
turned into a difference-array range update. Python and C++ agree at
`Smax = 30` on both series (king and the A005436 control).

| s | tool | wall_s | peak_rss_mb |
|---|---|---|---|
| 36 | convex_perimeter.py (orig) | 10.26 | — |
| 36 | convex_perimeter.py (rp-collapsed) | 1.44 | — |
| 60 | convex_perimeter.py (rp-collapsed) | 21.8 | — |
| 60 | convex_perim_tm (C++/GMP) | 2.44 | 6.3 |
| 100 | convex_perim_tm (C++/GMP) | 34.0 | 78.6 |
| 200 | convex_perim_tm (C++/GMP) | 1246.4 | 345.5 |

- P-recurrence of order 5, degree 2, found by `find_prec` on `s ≤ 22` and
  predicting all 172 remaining rows to `s = 200`. The polyomino control
  reproduces A005436 and its recurrence at (2,4) calibrates the guesser. The
  ratio is still falling at `s = 200`: 4.02172.
- Algebraic of degree 2: minimal box `(2, 9)`, nullity 1, fitted on 34 rows
  and holding on all 166 later ones, 0 failures over `Z`; `(2, 8)` excluded,
  rational excluded to t-degree 98 (`results/hv_perim_find_alg.log`):

```
q_0 = 2t^2 -21t^3 +88t^4 -196t^5 +242t^6 -119t^7 +72t^8 +16t^9
q_1 = -4t +52t^2 -252t^3 +554t^4 -520t^5 +96t^6 +128t^7
q_2 = 2 -31t +176t^2 -416t^3 +256t^4 +256t^5
```

The closed form `F(t)` above solves this quadratic.

### The 4-cone class by semiperimeter

`cpp/convex_perim_tm.cpp` gained a `dir4` mode and a `dir4bad` control
(`mode` in `{hv, dir4, dir4bad}`, default `hv`; `dir4` requires `king = 1`,
and `king = 0` forces `hv`). The row-built DP has state (row interval `[l, r]`,
two unimodality phase flags), so Proposition 2 had to be translated onto it.
For a column `j` left of the bottom row, `b(j)` is the first row `i` with
`l(i) ≤ j`, a right-continuous inverse of `l` on its descending phase. A row
where `l` drops by `k ≥ 1` covers `k` new columns with `b` constant across
them, which Proposition 2 allows; a row where `l` does not drop wastes a row
index, and if `l` drops again on a later row of the same phase, the columns
either side of the wasted row differ in `b` by at least 2, which Proposition 2
forbids. The symmetric pattern on the right boundary's ascending phase only
makes `b` rise across the gap, which is unrestricted. So `dir4` = "in the
left-descending phase `lp < l` strictly on every row; the first row that fails
to strictly decrease locks the phase", one comparison changed (`lp ≥ l` for
`lp > l` in the `npl` transition). Hand-checked on `l = [5,4,4,2]` (rejected:
`b(4) − b(3) = −2`), `l = [5,3,3,3]` (accepted) and `l = [5,3,1]` (accepted).
`dir4bad` is the unstrengthened rule, identical to `hv` at every `s`, and
diverges from `dir4` at `s = 5` (34 against 36).

Brute force: `build/directed_cone_anchor gridperim 14 8` tallies the
`HV ∧ dir4` animals by `W + H`, reusing the grid mode's predicates; an
area-`≤ N` enumeration settles `s` completely only while
`⌊s/2⌋⌈s/2⌉ ≤ N`, so `N = 14` settles `s ≤ 7` and is a lower bound beyond.
Run: 74.4 s wall, 1.9 MB (`results/mk_dir4_perim_brute_n14.log`,
`results/mk_dir4_perim_brute_n14.txt`).

| s | brute hv | brute dir4 | TM hv | TM dir4 | complete? |
|---|---|---|---|---|---|
| 2 | 1 | 1 | 1 | 1 | yes |
| 3 | 2 | 2 | 2 | 2 | yes |
| 4 | 9 | 9 | 9 | 9 | yes |
| 5 | 36 | 34 | 36 | 34 | yes |
| 6 | 154 | 137 | 154 | 137 | yes |
| 7 | 668 | 553 | 668 | 553 | yes |
| 8 | 2909 | 2230 | 2916 | 2237 | no (lower bound) |
| 9 | 11946 | 8358 | 12740 | 9038 | no (lower bound) |

`dir4(s) ≤ hv(s)` at every `s` in `2..200`, with equality only at
`s = 2, 3, 4`; `dir4(200)/hv(200) = 0.01019`. `build/convex_perim_tm 11 0 hv`
still reproduces A005436's first ten terms. No OEIS match on
`1,2,9,34,137,553,2237,9038,36435,146511`. Gate: `make gate-mk-dir4-perim`
(`tests/gate_mk_dir4_perim.py`). Series: 199 terms in
`results/mk_dir4_perim_terms_s200.txt`, from `build/convex_perim_tm 200 1 dir4`
on gympie.

| run | wall_s | peak_rss_mb |
|---|---|---|
| baseline: `hv` (unrestricted) king, s=200 | 1246.4 | 345.5 |
| `dir4`, s=200 | 1072.7 | 325.2 |

The restricted run is faster because the same loop carries smaller integers;
`cpu_s = 1072.6`, single-threaded.

**Verdict: algebraic of degree 4.** `F(t) = Σ_s a(s) t^s` satisfies
`Σ_{j=0..4} q_j(t) F^j = 0` with `deg q_j ≤ 22`. The box `(4, 22)` has nullity
exactly 1 on 200 rows at both primes, and the relation was recovered exactly
over `Q` (`experiments/dir4_perim_find_alg.py`, exact-`Fraction` elimination):
fitted on the first 119 rows, it annihilates all 81 later rows and all 200
rows over `Z`. Primitive integer form, low degree first:

```
q_0 = 9t^4 -120t^5 +676t^6 -2140t^7 +4283t^8 -5576t^9 +4198t^10 -906t^11
      -1270t^12 +1350t^13 -96t^14 +364t^15 +888t^16 +526t^17 +349t^18
      +246t^19 +98t^20 +16t^21 +t^22
q_1 = -30t^3 +482t^4 -3174t^5 +11056t^6 -21912t^7 +24026t^8 -9132t^9
      -11860t^10 +13626t^11 +492t^12 -2894t^13 +6540t^14 +8332t^15 +7390t^16
      +6696t^17 +4312t^18 +1616t^19 +314t^20 +24t^21
q_2 = 37t^2 -700t^3 +5389t^4 -21320t^5 +44037t^6 -37722t^7 -13978t^8
      +48384t^9 -20464t^10 -33324t^11 +20515t^12 +32808t^13 +26909t^14
      +36302t^15 +40156t^16 +26936t^17 +10841t^18 +2516t^19 +286t^20 +8t^21
q_3 = -20t +438t^2 -3916t^3 +17882t^4 -40900t^5 +28522t^6 +51028t^7
      -69112t^8 -44984t^9 +48224t^10 +20452t^11 -21166t^12 +31956t^13
      +110234t^14 +124676t^15 +81772t^16 +34364t^17 +9190t^18 +1424t^19
      +96t^20
q_4 = 4 -100t +1029t^2 -5446t^3 +14407t^4 -10250t^5 -32039t^6 +43974t^7
      +65620t^8 -55556t^9 -141788t^10 -55634t^11 +115295t^12 +212542t^13
      +190333t^14 +112426t^15 +46834t^16 +13732t^17 +2689t^18 +312t^19
      +16t^20
```

Five-digit coefficients are themselves evidence: the non-minimal `(19,3)`
P-recurrence for the same object has coefficients of about 60 digits. The box
is minimal both ways: `(4,21)` excluded, degree 3 excluded to t-degree 48,
degree 2 to 65, rational to 98. `find_prec` finds an exact P-recurrence in the
box `(19, 3)`, 80 unknowns, trained on 84 rows and predicting all 96
remaining, with 0 failures on re-substitution over `Q`
(`experiments/dir4_perim_find_prec.py`, `results/dir4_perim_find_prec.log`);
`(19,2)` and `(18,3)` are excluded. The exclusion frontier, the smallest order
at which each degree stops being excluded, is
`(27,2) (19,3) (17,4) (15,5) (15,6) (14,7) (14,8) (13,9) (13,10) (13,11) (13,12)`;
degrees 0 and 1 are excluded to orders 70 and 65. The identity is verified on
the 199 terms in hand, not proved past `s = 200`; the cheapest strengthening
is `build/convex_perim_tm 206 1 dir4` (about 21 minutes), six terms predicted
before computed, not run.

Controls for a positive verdict, where the risk is a guesser that says
CANDIDATE to anything:

| arm | what it is | must be | is |
|---|---|---|---|
| prec + | unrestricted HV-convex by semiperimeter, stored (5,2) recurrence | CANDIDATE | nullity 1, predicts all 172 withheld rows |
| prec - | same series, box (2,1) | EXCLUDED | rank 6 of 6 |
| alg + | A005436, algebraic by Delest-Viennot, box (2,8) | CANDIDATE | nullity 1, holds on all 69 withheld rows |
| alg - | same series, box (2,4) | EXCLUDED | rank 15 of 15 |
| **null** | **199 terms of the by-area king series** -- same length, rigorously non-D-finite (EXCLUDED at (24,24) on 700 terms) | EXCLUDED in every box where dir4 is a candidate | EXCLUDED, nullity 0, at every box tested here -- both modes, all five scripts |
| **power** | the unrestricted (D-finite) series in the very boxes that decide dir4 | CANDIDATE | CANDIDATE with the withheld entry fully passing at every box that contains its own order-5 operator; EXCLUDED only at `(2,62)`, whose order 2 is below 5 |

The null control is what lets the high-order candidates be trusted: `(17,9)`,
`(30,4)`, `(48,2)` come back excluded with nullity 0 on a series of identical
length. The nullity law is the internal consistency check: a minimal
`(K0, L0)` relation forces nullity `(K−K0+1)(L−L0+1)` as the box opens.
Measured against predicted for `(4, 22)`:

```
        L=20  21  22  23  24  25  26  27  28        L=20  21  22  23  24  25  26  27  28
  K=3      0   0   0   0   0   0   0   0   0   K=3     0   0   0   0   0   0   0   0   0
  K=4      0   0   1   2   3   4   5   6   7   K=4     0   0   1   2   3   4   5   6   7
  K=5      0   0   2   4   6   8  10  12  14   K=5     0   0   2   4   6   8  10  12  14
  K=6      0   0   3   6   9  12  15  18   -   K=6     0   0   3   6   9  12  15  18   -
  K=7      0   0   4   8   -   -   -   -   -   K=7     0   0   4   8   -   -   -   -   -
     measured (dir4)                                predicted by (4,22)
```

The same grid on the null control is all zeros. So HV-convex is quadratic and
(dir4, HV-convex) quartic: the 4-cone restriction raises the algebraic degree
from 2 to 4 and the t-degree from 9 to 22 without leaving the algebraic class,
while by area it changes nothing about tractability. Gate:
`make gate-dir4-perim-alg` (`tests/gate_dir4_perim_alg.py`, 3.4 s), which checks
the quartic, its minimality, the nullity law at four boxes, the null control,
the A005436 control and the degree-2 result; flipping one coefficient of `q_0`
fails it. Logs: `results/dir4_perim_dfinite.log`,
`results/dir4_perim_nullcontrol.log`, `results/dir4_perim_boundary.log`,
`results/dir4_perim_minimal_box.log`, `results/dir4_perim_nullity_grid.log`,
`results/dir4_perim_nullity_ladder.log`, `results/dir4_perim_find_alg.log`.

## Every class between staircase and HV-convex has growth constant µ

The 49-digit agreement between (dir4, HV-convex) and HV-convex is a theorem,
and not a bijection: a squeeze that applies to every intermediate class.

**Proposition 6.** Let `A(n)` count HV-convex king animals of area `n`, and
let `C` be any class with

    staircase  ⊆  C  ⊆  HV-convex.

Then `lim C(n)^(1/n)` exists and equals `lim A(n)^(1/n) = µ = 3.128943269730886…`.

(dir4, HV-convex), (dir5, HV-convex), (ctrlB, HV-convex) and
(mdir, HV-convex) are such classes, and so is anything else between the two
ends. A by-product: A225114 has growth constant `µ`, measured to 204 digits;
the entry carries no asymptotic.

### The operator comparison

`cpp/middle_kingdom_tm.cpp`'s PROFILE engine carries state `(h, pb, pt)`, the
last column's height and the two unimodality phases, and steps by
`d = b(j+1) − b(j)` with `s := h − h'` marking where the top turns (`d > s`
iff `t` rises). Modes `hv` and `hvdir4` differ in one line: the floor on `d`
is `−h'` for `hv` and `−1` for `hvdir4`. Each phase bit flips at most once and
never flips back, so the operator is block-triangular in the four phases:

| phase | meaning | step constraint | operator entry `K(h, h')` |
|---|---|---|---|
| `(0,0)` | `b` falls, `t` rises (heights grow) | `s ≤ d ≤ 0` | `h' − h + 1`, `h' ≥ h` |
| `(1,0)` | both rise | `d ≥ max(0, s)` | `min(h, h') + 1` |
| `(0,1)` | both fall | `d ≤ min(0, s)` | `min(h, h') + 1` |
| `(1,1)` | `b` rises, `t` falls (heights shrink) | `0 ≤ d ≤ s` | `h − h' + 1`, `h' ≤ h` |

The 4-cone floor `d ≥ −1` bites only where `pb = 0`, i.e. on blocks `(0,0)`
and `(0,1)`, where it replaces the entries by ones in `{0, 1, 2}`; blocks
`(1,0)` and `(1,1)` are untouched entry for entry. Block `(1,0)` is the
staircase operator `min(h, h') + 1`, and Proposition 6 says that block alone
fixes `µ`. This answers the finite-rank criterion below: the infinite-rank
coupling in this family is the single entry `min(h, h') + 1`, appearing once
in each middle block, and the 4-cone condition rewrites one copy and leaves
the other intact. The criterion's prediction that A225114 has no rational
generating function is confirmed: on 700 terms the staircase series is
excluded at order ≤ 24 / degree ≤ 24 (rank 625 of 625) and non-algebraic at
degree ≤ 20 / t-degree ≤ 20 (rank 441 of 441).

### The proof

Read an HV-convex animal left to right: it fattens, then shears, then thins.
The shearing middle is a staircase animal and the two ends are stacks; stacks
are too few to carry an exponential, and staircase animals glue end to end
without waste. Throughout, an HV-convex king animal is a column sequence with
`b` valley-unimodal and `t` peak-unimodal (Corollary 4), and `M(n)` counts the
staircase ones.

**Lemma 1 (three-block factorization).** Give column `j` the phase
`(pb, pt)` with `pb = 1` iff some earlier step had `d > 0` and `pt = 1` iff
some earlier step had `t` decreasing. Both bits are monotone in `j`, so the
columns split into three consecutive (possibly empty) runs `C1 C2 C3` carrying
phases `(0,0)`; one of `(1,0)` or `(0,1)`; and `(1,1)`. Taken standalone,
`C1` and `C3` are monotone-height blocks (heights nondecreasing and
nonincreasing respectively; reversing the column order carries one to the
other), counted by `P(n)`; `C2` is a staircase animal (phase `(1,0)`) or the
vertical mirror of one (phase `(0,1)`), counted by `M(n)`. The animal is
recovered from `(C1, C2, C3)`, the two junction offsets, and one bit naming
`C2`'s phase. Each junction offset `d` lies in `[−h', h]` with `h + h' ≤ n`,
so it takes at most `n + 1` values, and

    A(n)  ≤  2 (n+1)^2  ·  sum_{i+j+l=n}  P(i) M(j) P(l),     P(0) = M(0) = 1.   (*)

*Attribution.* Gouyou-Beauchamps and Leroux, *Enumeration of symmetry classes
of convex polyominoes on the honeycomb lattice*, FPSAC 2004
(arXiv:math/0403168, `papers/gouyou-beauchamps_leroux_2004_convex_polyominoes_honeycomb.pdf`),
§2.3, decompose a convex polyomino into blocks by the growth phases of its two
profiles, with the extreme blocks identified as stack polyominoes and the
middle blocks as staircase polyominoes with `H02 = Pa = H20`. That is Lemma 1,
Lemma 2's identification and Proposition 9 for convex polyominoes on the
honeycomb lattice. The square-lattice companion (Leroux, Rassart and
Robitaille, Adv. Appl. Math. 21 (1998) 343–380) uses a different route. What
is not theirs: the king lattice (their middle entry is `min(h,h')`, ours
`min(h,h')+1`), a class with no exact solution, and Propositions 6, 7, 10
and 11. `paper/L5-convex-polyplets.tex` carries this attribution in three
places by requirement of `docs/publication-split.md`.

**Lemma 2 (the outer blocks are stacks, hence sub-exponential).**
`P(n) = A001523(n)`, the number of stacks (weakly unimodal compositions of
`n`), and `P(n) ≤ E(n) := (n+1)^{4√n+6}`, so `P(n)^{1/n} → 1`.

*Proof.* In a phase-`(1,1)` block the column intervals are nested,
`[b(j+1), t(j+1)] ⊆ [b(j), t(j)]`, so the set of columns meeting row `y` is a
prefix `1..r(y)`; since `{y : r(y) ≥ k} = [b(k), t(k)]` is a decreasing nested
family of intervals, `r` is weakly unimodal with `Σ_y r(y) = n`, and the stack
is rebuilt from `r`, so `P(n)` counts weakly unimodal compositions. Cutting
such a composition at its peak gives two partitions, so
`P(n) ≤ (n+1)² p(n)²`. Put `s = ⌈√n⌉` and split a partition of `n` at `s`:
the parts `≤ s` are fixed by `s` multiplicities in `[0, n]`, at most
`(n+1)^s` choices; the parts `> s` number at most `L = ⌊n/(s+1)⌋`, at most
`(L+1)n^L ≤ (n+1)^{L+1}` choices. Hence `p(n) ≤ (n+1)^{s+L+1} ≤ (n+1)^{2√n+2}`,
`P(n) ≤ (n+1)^{4√n+6}`, and `log P(n)/n → 0`. ∎ (Hardy–Ramanujan would give
`e^{O(√n)}`; the elementary bound keeps the squeeze free of analytic input.)
Measured: `P(n) = 1, 2, 4, 8, 15, 27, 47, 79, 130, 209, 330, 512` matches
A001523 (`experiments/monotone_block_growth.py`), and `P(n)^(1/n)` falls
1.706 → 1.168 over `n = 10..400`.

**Lemma 3 (the staircase count is supermultiplicative).**
`M(i) M(j) ≤ M(i+j)` for all `i, j ≥ 0` (with `M(0) = 1`), and therefore
`lim M(n)^(1/n)` exists and equals `sup_n M(n)^(1/n)`.

*Proof.* Given staircase animals `X` (area `i`, last column height `h`) and
`Y` (area `j`, first column height `h'`), slide `Y` up by `d = max(0, h − h')`
and butt the column sequences together. That `d` is the smallest legal slide
(`b` not dropping forces `d ≥ 0`, `t` not dropping forces `d ≥ h − h'`), a
function of `X` and `Y`, not a choice. The join is in the class: `d ≥ 0`
keeps bottoms nondecreasing, `d − s ≥ 0` keeps tops nondecreasing, and
`d ≤ h` makes the junction king-adjacent; area is `i + j`. The join is
injective at fixed `(i, j)`: every column is nonempty, so the cumulative
areas are strictly increasing and hit `i` exactly once; cut there. Fekete's
lemma in supermultiplicative form gives the limit as a supremum, which is
mathlib's `Subadditive.tendsto_lim` applied to `−log M`, as
`polyplets/Polyplets/Growth.lean` does for `λ`. ∎

*By-product: every recorded term is a rigorous lower bound on `µ`.*
`µ ≥ M(n)^(1/n)` for each `n` with no extrapolation. At `n = 700`,

    µ  ≥  M(700)^(1/700)  =  3.12340450886853853211…

exact arithmetic on a recorded term. An earlier version of the lemma paid a
factor `i + j` for the index of `X`'s last column and cited Barequet,
Ben-Shachar and Osegueda, Comput. Geom. 98 (2021) 101790, §2.2
(`papers/barequet_benshachar_osegueda_2021_concatenation_arguments.pdf`); the
index is not free information, so neither is needed here.
Measured (`experiments/staircase_supermul.py`, 0.6 s): brute force over
`(h, d)` reproduces `M(1..12)`; over all `i + j ≤ 12` every one of 1182960
joins lands in the class, the map is injective at fixed `(i, j)` and the
area-`i` cut inverts it; on the 700 recorded terms `M(i)M(j) ≤ M(i+j)` has
zero violations. Three controls required to fail: the stacks `P(n)` are not
supermultiplicative (`P(2)P(20) = 22480 > 22277 = P(22)`); the join with
`d = 0` leaves the class; cutting at cumulative area `i + 1` fails to invert.

*Proof of Proposition 6.* Write `µ = lim M(n)^(1/n) = sup_n M(n)^(1/n)`,
which exists by Lemma 3 and is `≥ 1`. Fix `ε > 0` and take `C_ε` with
`M(j) ≤ C_ε (µ+ε)^j`. In (*), bound `P(i), P(l) ≤ E(n)` by Lemma 2, which
applies since `E` is nondecreasing:

    A(n)  ≤  2 (n+1)^4 E(n)^2 C_ε (µ+ε)^n,

and `E(n)^{1/n} → 1`, so `limsup A(n)^(1/n) ≤ µ`. In the other direction,
`M(n) ≤ C(n) ≤ A(n)` termwise, so `liminf C(n)^(1/n) ≥ µ` and
`limsup C(n)^(1/n) ≤ µ`. ∎

The square-lattice analogue is classical: convex polyominoes by area grow at
2.30914… (Bender 1974) and the parallelogram subclass A006958 has the same
constant, measured at 2.309138593330495, flat from `n = 100` to `400`
(`experiments/square_staircase_area.py`, which builds both series from the
one operator, `min(h,h')` square and `min(h,h')+1` king, and reproduces
A006958 and A225114 as positive controls). What the proposition adds is the
king case, where neither class is solved, and the statement for every
intermediate class. Staircase ⊆ (dir4, HV-convex) is Proposition 2.

Brute force against `results/mk_grid20_n14.txt`:

| n | staircase `M` | (dir4, HV) | HV-convex `A` |
|---|---|---|---|
| 1 | 1 | 1 | 1 |
| 3 | 9 | 15 | 16 |
| 8 | 2659 | 5417 | 8390 |
| 14 | 2494307 | 4292477 | 8389720 |

`M(n) ≤ D(n) ≤ A(n)` at every `n ≤ 14`, and the bound (*) holds at every
`n ≤ 14` (`experiments/monotone_block_growth.py`; at `n = 14`,
`8389720 ≤ 3848993100`). `make gate-middle-kingdom` checks the `stair` mode
against the grid's staircase column, the termwise chain
`stair ≤ hvmono ≤ hvdir4 ≤ hv`, and a control: dropping the tops condition
from `stair` gives `ccmono` = A007052 = 1, 3, 10, 34, …, which must not equal
A225114 = 1, 3, 9, 28, ….

### The numerics: four series, one constant

Modes `stair` (`d ≥ 0` and `d ≥ s`) and `hvmono` (`d ≥ 0`, `t`
peak-unimodal), 700 terms each in 0.87 s / 50 MB and 1.28 s / 58 MB on
gympie (`scripts/mk_stair_growth.sh`; series `results/mk_stair_terms_n700.txt`,
`results/mk_hvmono_terms_n700.txt`; log `results/mk_stair_growth.log`). All
four series through `experiments/convex_growth.py` at 500 digits of working
precision:

| class | first terms | trusted digits of µ | amplitude `C` | `d_n/d_(n−1)` |
|---|---|---|---|---|
| staircase (A225114) | 1, 3, 9, 28, 87, 272 | 204 | 0.28932146397165132308 | 0.48100879371 |
| HV-convex, `b` nondecreasing | 1, 3, 10, 33, 107, 342 | 202 | 0.37545302027992473174 | 0.48100879371 |
| (dir4, HV-convex) | 1, 4, 15, 53, 177, 567 | 51 | 0.45030318571234118235 | **0.803651401483** |
| HV-convex | 1, 4, 16, 61, 221, 766 | 199 | 0.97445221313500464915 | 0.48100879371 |

The staircase µ at 204 digits reproduces every one of the 199 digits the
HV-convex series gives and continues past them:

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549                 <- the 199 above
                                        000485           <- staircase, beyond them
```

`hvmono` does the same at its 202 digits. The amplitude column gives
`C_dir4 / C_HV = 0.46210904920994244003`, against the directly extrapolated
0.462109049209942440035662387700305832841163439729980425 (Table B).

### Where the subdominant singularities come from

Of the four diagonal blocks, exactly two carry exponential weight standalone:

| block | unrestricted | under the 4-cone condition |
|---|---|---|
| `(0,0)` | heights nondecreasing, sub-exponential (Lemma 2) | still sub-exponential |
| `(1,0)` | staircase, growth **µ = 3.1289…** | untouched |
| `(0,1)` | mirror staircase, growth **µ** | truncated, growth **2.5146…** |
| `(1,1)` | heights nonincreasing, sub-exponential (Lemma 2) | untouched |

The truncated `(0,0)` block stays sub-exponential: with `h' ≥ h` the entry
`min(2, h' − h + 1)` is 2 only at a strict rise, strict rises take distinct
heights, so there are at most `√(2n)` of them and the weight is `≤ 2^√(2n)`.
The truncated `(0,1)` block is the exception: it is not height-monotone
(`h' ≤ h` at weight 2, `h' = h+1` at weight 1, `h' > h+1` forbidden), so
heights can climb one row at a time. Counted by area
(`experiments/dir4_descent_block.py`, DP against a brute-force oracle at
`n ≤ 12`, with a control on the climb weight) it is

    1, 3, 8, 21, 54, 138, 350, 885, 2233, 5626, …

with no OEIS match on ten or thirteen terms (the six-term prefix collides
with A127358, A135473 and A077849, all diverging by `n = 9`, 2230 against
2233), and its growth constant `ν` on 700 terms is

    2.5145796438787291885104371943430998201410308559007832719354957107238409922963
    2690389299337761749953732175539964789209170137762869374741150849461805388232
                                                              (153 trusted digits)

Reproduced independently by `experiments/descent_block_oracle.py`, a DFS over
explicit column intervals `[b, t]` with `b` and `t` nonincreasing and
`d ≥ −1`, checked against a forward DP on the last column's height, agreeing
on all 700 terms, with three controls required to diverge (dropping the
4-cone floor returns the mirror staircase A225114; loosening to `d ≥ −2`;
weighting the climb 2). The 153 is `convex_growth.py`'s figure, set by its
Aitken-against-Richardson cross-check, the wrong comparison when the
correction is geometric; Prony on the same terms trusts 242. The
`--compare` figure of 193 digits against the 4-cone series' subdominant is a
raw agreement of two Aitken extrapolations; measured independently the two
numbers agree to 236 digits and the weaker is trusted to 217.

**The series splits, and so does the spectrum.** Partition the class by
whether an animal's phase path ever visits `(0,1)`:

    D(n)  =  D_asc(n)  +  D_desc(n).

`build/middle_kingdom_tm hvdir4asc` deletes the `(0,1)` state
(`results/mk_hvdir4asc_terms_n700.txt`, log `results/mk_hvdir4asc_n700.log`),
and `D_desc = hvdir4 − hvdir4asc` (`results/mk_hvdir4desc_terms_n700.txt`,
derived, `n = 2..700`). Oracle for both: `experiments/descent_block_oracle.py
--phases 14`, agreeing with the engine on every `n ≤ 14` and with the block DP
on all 700 terms.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| `D` = hvdir4 | 1 | 4 | 15 | 53 | 177 | 567 | 1767 | 5417 |
| `D_asc` | 1 | 3 | 10 | 34 | 115 | 382 | 1244 | 3993 |
| `D_desc` | 0 | 1 | 5 | 19 | 62 | 185 | 523 | 1424 |

Read the exponential spectrum of each 700-term series by Prony's method
(`experiments/prony_spectrum.py`: the constant-coefficient recurrence the tail
obeys best, then the roots of its characteristic polynomial; trusted digits
are the agreement between fits at window `N` against `N−50` and order `k`
against `k+1`, minus a guard):

| series | `λ_1` | `λ_2` | `λ_3` | `λ_4` |
|---|---|---|---|---|
| staircase | **3.12894326973088…** | **1.50504922775900…** | 1.28433727098118… | −1.25776216033063… |
| HV-convex | same | same | same | same |
| `hvmono` | same | same | same | same |
| **`D_asc`** | same | same | same | same |
| block `T` | **2.51457964387872…** | **1.43040460381247…** | 1.24846593371011… | 1.17441805313317… |
| **`D_desc`** | same | same | same | same |
| `D` = dir4 | 3.12894326973088… | 2.51457964387872… | 1.50504922775900… | 1.43040460381247… |

`D`'s spectrum is the other two interleaved, and the interleaving continues
(`λ_5(D)` is the staircase's `λ_3`, `λ_6(D)` its `λ_4`). Digits, from
`results/subdominant_identification.log` (`agree` = shared digits;
`bearable` = the smaller of the two trusted counts):

| claimed coincidence | agree | bearable |
|---|---|---|
| `λ_1(D_desc)` = `λ_1(block)` | 246 | **226** |
| `λ_2(D_desc)` = `λ_2(block)` | 72 | 64 |
| `λ_1(D_asc)` = `λ_1(staircase)` | 310 | **284** |
| `λ_2(D_asc)` = `λ_2(staircase)` | 86 | **76** |
| `λ_3(D_asc)` = `λ_3(staircase)` | 37 | 32 |
| `λ_2(D)` = `λ_1(block)` | 236 | **217** |
| `λ_3(D)` = `λ_2(staircase)` | 78 | **69** |
| `λ_4(D)` = `λ_2(block)` | 62 | 55 |
| `λ_2(staircase)` = `λ_2(HV-convex)` | 85 | 77 |

Negative controls: the block's `λ_1` and `λ_2` match no root of `D_asc`
(best 0 and 1 digits), and the staircase's `λ_2` matches no root of `D_desc`
(best 1 digit).

**Lemma 4.** `lim T(n)^(1/n)` exists; write `ν` for it.

*Proof.* Let `T_h(n)` count runs whose first column has height `h`, and
`T_1 = T_(h=1)`. (i) `T(n) ≥ 2T(n−1)`: append a height-1 column, admitted at
weight 2 from any height. (ii) `T_h(n) ≤ 2T(n−h)`: delete the first column;
the step out of it had weight ≤ 2. With (i), `T_h(n) ≤ 2^(2−h) T(n−1)`, so
`Σ_(h≥4) T_h(n) ≤ T(n−1)/2 ≤ T(n)/4` and `T(n) ≤ 4·max_(h≤3) T_h(n)`.
(iii) `T_h(n) ≤ T_1(n + h(h−1)/2)`: prepend the climb `1, 2, …, h−1`, each
step the weight-1 `h' = h+1` transition; for `h ≤ 3` that costs at most 3,
and `T_1` is nondecreasing by (i)'s argument. So `T(n) ≤ 4 T_1(n+3)`.
(iv) `T_1(i) T_1(j) ≤ T_1(i+j)`: join two runs starting at height 1 by the
step "last height → 1", weight 2; the pair is recovered from the join and the
prefix area. Fekete gives `lim T_1(n)^(1/n) = sup_n T_1(n)^(1/n)`, and
`T_1 ≤ T ≤ 4T_1(·+3)` squeezes `T` onto the same limit. ∎

**Proposition 7.** `lim D_asc(n)^(1/n) = µ` and `lim D_desc(n)^(1/n) = ν`.

*Proof.* `D_asc ≥ M` termwise: a staircase animal has `d ≥ 0` and `d ≥ s` at
every step, so it never enters `(0,1)`, which needs `d ≤ 0` and `d < s`. With
`D_asc ≤ D` and Proposition 6, `lim D_asc(n)^(1/n) = µ`. For `D_desc`,
Lemma 1's factorization with `T` in place of `M` gives
`D_desc(n) ≤ 2(n+1)^2 Σ_(i+j+l=n) P0(i) T(j) P1(l) ≤ 2(n+1)^4 E(n)^2 C_ε (ν+ε)^n`,
so `limsup D_desc(n)^(1/n) ≤ ν`. Conversely, take a `T`-run of area `m` whose
first column is `[0, h−1]` and prepend the column `[0, h]`: the joining step
has `d = 0 ≤ 0` and `s = 1 > d`, so it enters `(0,1)`, the run's own steps
keep it there, and the result is a (dir4, HV-convex) animal of area
`m + h + 1`. With `h = 1`, `D_desc(n) ≥ T_1(n−2)`, so
`liminf D_desc(n)^(1/n) ≥ ν` by Lemma 4. ∎

So `ν` is the growth constant of an explicitly counted half of the series,
not an artifact of extrapolation. What is not proved is the step to Table B's
diagnostic, which measures the second exponential of `D` itself:

**Conjecture 8.** `D_asc(n) = C µ^n (1 + O(ρ^n))` with
`ρ = 0.48100879370959…`, and `D_desc(n) = C' ν^n (1 + O(σ^n))` with
`σ = 0.568844421888…`, where
`C = 0.45030318571234118235361371383386342153…` and
`C' = 2.5795006951239199769623573391294166…`.

Granting it, `D(n) = C µ^n + C' ν^n + O((µρ)^n + (νσ)^n)` with
`µρ = 1.50504922775900…` and `νσ = 1.43040460381247…`, both below `ν`, so the
subdominant exponential of `D` is exactly `ν` and Table B's 0.803651401483 is
`ν/µ`. Measured support: the two correction ratios are `λ_2/λ_1` of the two
halves, trusted to 76 and 64 digits; the amplitudes are the 40 digits
`convex_growth.py` prints. No series in this family has a proved sharp
asymptotic, not even the dominant one: Proposition 6 and Lemma 3 give
exponential rates, never `A(n) ~ Cµ^n`. One route exists: A225114's entry
carries a conjectured continued fraction (Kurkov, Sep 2024),

    g.f. = 1/(2 − 1/(1 − x/(1 − x/(1 − x²/(1 − x²/(1 − x³/(1 − x³/(1 − …)))))))),

whose depth-24 convergent reproduces 41 terms of A225114 and whose poles, as
`1/x`, land on the measured staircase spectrum to 30, 27, 14 and 16 digits on
`λ_1 … λ_4`, improving with depth (`experiments/staircase_cf_poles.py`, with
a control that changes one partial numerator and diverges at `n = 6`). A
proof would supply the meromorphic continuation and spectral gap; the same
would then be wanted for `T`, which has no entry and no conjectured form.

**The corrected reading of Table B.** Both series carry 0.481008794:

| series | `d_n/d_(n−1)` | what it is |
|---|---|---|
| HV-convex, `hvmono`, staircase | 0.481008794 | `λ_2/λ_1`, the staircase block's own correction |
| `D_asc` — a subclass of (dir4, HV-convex) | **0.48100879371** | the same one |
| `D_desc` and the block `T` | 0.568844421888 | the block's own correction |
| (dir4, HV-convex) | 0.803651401483 | `ν/µ`, the *extra* exponential in front |

The 0.4810 in row two is measured on 4-cone-directed animals directly; as
`λ_2/λ_1` from that series' spectrum it is `0.48100879370959321158558…`,
trusted to 76 digits, and the same run trusts that series' `µ` to 200 digits
against 51 for the unsplit series. The restricted series has an extra
exponential in front of the shared one, and the diagnostic reports only the
largest correction present. The bijection is ruled out for a proved reason: it
would have to account for a half of one side, growing at 2.5146, with no
counterpart on the other.

### The amplitude ratio is a ratio of two explicit feed vectors

Table B's binding constraint was a convergence rate: `D(n)/A(n)` approaches
its limit at `(ν/µ)^n = 0.8037^n`, `1e−66` at `n = 700`, while
`D_asc(n)/A(n)` approaches the same limit at `ρ^n`, `1e−222`. Same script and
discipline (`experiments/ratio_amplitude.py`, raw and Aitken, `n = 600`
against `700`, minus a 2-digit guard):

| numerator, over `convex_area_terms_n700_king` | raw | Aitken | TRUSTED |
|---|---|---|---|
| `D` = hvdir4 — Table B's own | 56 | 239 | **54** |
| `D_asc` = hvdir4asc | 187 | 253 | **185** |

The first row reproduces Table B's 54 digits and its decimal string. The two
rows must have the same limit: `D = D_asc + D_desc` with
`lim D_desc(n)^(1/n) = ν < µ` (Proposition 7), so the descending half
contributes nothing at order `µ^n`.

**Proposition 9 (the mirror halves).** Partition the HV-convex animals by
which middle phase their path visits; no path visits both `(1,0)` and `(0,1)`.
Then `A_(1,0)(n) = A_(0,1)(n)` for every `n`, and the remainder, the paths
`(0,0) → (1,1)`, is sub-exponential. Hence if `C_HV = lim A(n)/µ^n` exists,
`C_HV = 2 C(A_(1,0))`. (The mirror equality is Gouyou-Beauchamps and Leroux's
`H02 = Pa = H20`; the factor 1/2 and the sub-exponential remainder are added
here.)

*Proof.* The vertical mirror `[b(j), t(j)] ↦ [−t(j), −b(j)]` is an
area-preserving involution of the class that leaves every column height alone
and carries `d(j)` to `−(t(j+1) − t(j))`, so the phase bits swap,
`(pb, pt) ↦ (pt, pb)`: phases `(0,0)` and `(1,1)` are fixed and
`(1,0) ↔ (0,1)`. The remainder factors as a phase-`(0,0)` block joined to a
phase-`(1,1)` block at one step, both stacks by Lemma 2, so it is at most
`(n+1)^2 E(n)^2`. ∎

Brute-forced (`experiments/descent_block_oracle.py --mirror 14`, log
`results/hv_mirror_split_n14.log`):

| n | 1 | 2 | 3 | 4 | 5 | … | 13 | 14 |
|---|---|---|---|---|---|---|---|---|
| HV-convex | 1 | 4 | 16 | 61 | 221 | … | 2677214 | 8389720 |
| via `(1,0)` | 0 | 1 | 6 | 26 | 100 | … | 1333383 | 4184875 |
| via `(0,1)` | 0 | 1 | 6 | 26 | 100 | … | 1333383 | 4184875 |
| via neither | 1 | 2 | 4 | 9 | 21 | … | 10448 | 19970 |

**Proposition 10 (the staircase eigenvector is a three-term recurrence).**
Let `T(x)` be the staircase block's operator, `T(x)_{h,h'} = x^{h'}(min(h,h')+1)`
for `h, h' ≥ 1`, and let `φ` solve

    φ(0) = 1,  φ(1) = 2,  φ(h) = (2 − x^{h−1}) φ(h−1) − φ(h−2)   (h ≥ 2).

For `0 < x < 1`: `T(x) φ = φ` iff `φ(h) − φ(h−1) → 0`; that happens at
exactly one `x = x_c`; and `x_c = 1/µ`.

*Proof.* Write `Q(h) = Σ_{h'>h} x^{h'} φ(h')`. Splitting `T(x)φ = φ` at
`h' = h` gives `φ(h) = Σ_{h'≤h} x^{h'}(h'+1)φ(h') + (h+1) Q(h)`; differencing
once gives `φ(h) − φ(h−1) = x^h φ(h) + Q(h)` (and `φ(0) = φ(1)/2` from
`h = 1`), differencing again gives the recurrence. Conversely, define
`Q(h) := φ(h) − φ(h−1) − x^h φ(h)` from the recurrence's solution; the second
difference makes `Q(h−1) − Q(h) = x^h φ(h)` an identity, so
`Q(h) = Q(∞) + Σ_{h'>h} x^{h'} φ(h')` and the eigenvector equation holds iff
`Q(∞) = 0`. Since `x < 1`, the solution space is spanned by one asymptotically
constant and one asymptotically linear solution, and `Q(∞) = 0` is exactly
"the linear one is absent", one analytic condition on `x`. At such an `x`,
`φ` is positive: the differences `δ(h) = φ(h) − φ(h−1)` obey
`δ(h) = δ(h−1) − x^{h−1} φ(h−1)` with `δ(1) = 1`, so `δ` strictly decreases
while `φ > 0`, and `δ(h) → 0` forces `δ > 0` throughout; `φ` increases from 2
to `2.5374225302…`. `T(x)` is positive and compact on
`{f : |f(h)| ≤ C(1+h)}`, so by Krein–Rutman a positive eigenvector's
eigenvalue is the spectral radius. `M(x) = v0(x) (I − T(x))^{−1} 1` with
`v0(h) = x^h` is the staircase generating function, of radius `1/µ`, and the
spectral radius of `T(x)` increases continuously in `x`, so it reaches 1 at
`x = 1/µ`. ∎

*By-product.* Shooting on the recurrence computes `µ` to arbitrary precision
in `O(hmax)` operations with no series: 987 digits in 1.6 s on one core
(`--dps 1000 --hmax 2200`), reproducing all 199 recorded digits and matching
the staircase series' `…922549000485` beyond them:

```
3.128943269730886252277447995387754160532091221904394134964974649949244385837182
5761582306328816478323463483522101893703960816757649304814623377841406484754329
8805623983850111109827008627878918922549                 <- the 199 above
                                        000485072072     <- the shooting
```

**Proposition 11 (the ratio), conditional on the amplitudes existing.**
Write `U(h,h') = h'−h+1` and `U4(h,h') = min(2, h'−h+1)` for `h' ≥ h` (the
`(0,0)` block, unrestricted and 4-cone-truncated), `L(h,h') = min(h, h'+1)`
(the map `(0,0) → (1,0)`, and also `(0,0) → (0,1)`, the same matrix), each
carrying `x^{h'}`, and

    w  = v0 (I − U )^{−1} L,      w4 = v0 (I − U4)^{−1} L,      evaluated at x_c.

If `C(D_asc) = lim D_asc(n)/µ^n` and `C_HV = lim A(n)/µ^n` exist, then

    r  =  C_dir4 / C_HV  =  (1/2) · (w4 · φ) / (w · φ).                    (*)

*Proof.* The phase automaton makes the path decomposition exact as generating
functions: `A_(1,0)(x) = w(x) (I − T(x))^{−1} q(x)` with
`q = 1 + L_{(1,0)→(1,1)} (I − T_{(1,1)})^{−1} 1`, and
`D_(1,0)(x) = w4(x) (I − T(x))^{−1} q(x)` with the same `T` and `q`, since the
4-cone floor bites only inside the `(0,0)` block. The `(0,0)` and `(1,1)`
blocks are stacks, so `w`, `w4` and `q` are finite at `x_c`. By
Proposition 10 and Krein–Rutman the pole of `(I − T(x))^{−1}` at `x_c` is
simple with rank-one residue `φ ψ^T / ⟨ψ, φ⟩`, so
`lim_{x→x_c⁻} (1 − µx) A_(1,0)(x) = N · (w · φ)` and
`lim_{x→x_c⁻} (1 − µx) D_(1,0)(x) = N · (w4 · φ)` with the same
`N = ⟨ψ, q⟩ / (⟨ψ, φ⟩ · (−x_c Λ'(x_c)))`, which cancels. If the amplitudes
exist, Abel's theorem makes those limits `C(A_(1,0))` and `C(D_(1,0))`;
`C_HV = 2 C(A_(1,0))` by Proposition 9 and `C_dir4 = C(D_asc) = C(D_(1,0))`,
the `D_desc` and "via neither" parts being `o(µ^n)`. ∎

The hypothesis is strictly weaker than Conjecture 8. `r` is a ratio of two
`q`-series in `q = 1/µ`, both computed by `O(hmax)` prefix-sum recurrences
(`experiments/amplitude_feed_vectors.py`; log `results/amplitude_feed_vectors.log`;
constants `results/amplitude_ratio_constants.txt`):

    w  · φ  =  1.29770192341040021939895011278…
    w4 · φ  =  1.19935960397018718067118376153…

The 251 trusted digits (the identity supplies 987 at `--dps 1000 --hmax 2200`):

    0.4621090492099424400356623877003058328411634397299804247065092921445229505114
    444835410198048486182340620897552570414665332043843876381701390681440910143562
    899341315538121788620454046737283009596825392081974838100954958864643192857487
    4902351771539511812

| route | own cross-check | trusted |
|---|---|---|
| Table B, `D/A` extrapolated | raw vs Aitken, n=600 vs 700 | 54 |
| `D_asc/A` extrapolated | raw vs Aitken, n=600 vs 700 | 185 |
| identity (*) | `hmax` 1200 vs `hmax` 1000 | 492 |

The extrapolation and the identity agree to 293 digits and share no
arithmetic; taking the Aitken-against-Aitken agreement (253) as the weaker
side's count gives 251 trusted digits with a 2-digit guard, and Table B's
stricter rule gives 185. Negative controls, in
`experiments/amplitude_feed_vectors.py` and checked by
`make gate-middle-kingdom`: dropping the factor 1/2 agrees with the
measurement to 0 digits; truncating the `(0,0)` block at `min(3, ·)` agrees to
1; the `φ` recurrence at `x = 1/3.13` fails its eigen-equation at `1e−2`
where `x_c` gives `1e−528`.

**PSLQ, the enlarged boxes, the same verdict.** A box is in capacity while
`(terms) × log10(height)` stays below half the digits fed; the positive
control `(1 + √2)/3` is found at degree 2 on every run. At 185 digits
(`results/amplitude_pslq_185.log`):

    NO relation in any in-capacity box --
      degree <= 45 at height <= 1e2, <= 22 at 1e4, <= 14 at 1e6,
      <= 10 at 1e8, <= 6 at 1e12, <= 3 at 1e20, <= 2 at 1e30

At 251 digits (`results/amplitude_pslq_251.log`):

    NO relation in any in-capacity box --
      degree <= 30 at height <= 1e4, <= 20 at 1e5, <= 10 at 1e11,
      <= 5 at 1e20, <= 3 at 1e30, <= 2 at 1e40

`2r` is excluded in the same degree-12 / height-1e2 box. Over `Q(µ)`, PSLQ on
`{µ^i r^j}` at 251 digits finds no relation in any in-capacity box:

    mu-degree <= 5, r-degree <= 6 at height <= 1e2
    mu-degree <= 4, r-degree <= 5 at height <= 1e4
    mu-degree <= 3, r-degree <= 4 at height <= 1e6
    mu-degree <= 2, r-degree <= 4 at height <= 1e8

`experiments/amplitude_pslq.py --digits 60 --field 2:3` returns a "relation"
of height 48186 with capacity 56 against 60 digits fed, which the rule
rejects. Since `µ` has no proof of irrationality, `Q(µ)` is a field of unknown
degree and "algebraic over `Q(µ)`" cannot be settled either way; the identity
(*) gives a reason to expect no: `r` is a ratio of two `q`-series at
`q = 1/µ`, and `µ` is itself the reciprocal of a zero of an entire
`q`-function, the same shape as Kurkov's continued fraction.

Cost of routes not taken: extending the split series to `n ≈ 1050` (for 300
trusted digits by Table B's rule, `0.3179 n`) is 10.6 s for
`middle_kingdom_tm hvdir4asc 1100` but about 50 minutes for the partner
`convex_area_tm`, which scales as `N⁴`; PSLQ cost, not precision, now bounds
the boxes (degree 22 at 185 digits took 41 s, degree 45 took 1669 s, degree 30
at 251 digits took 303 s; a degree-120 box extrapolates to hours). Neither
run.

Novelty: HV-convex king animals are not in OEIS or the literature under any
name; no source states the squeeze for intermediate classes; Propositions 6,
7, 10 and 11 have no counterpart found (`docs/publication.md`, items N1–N3).
A225114's entry, re-fetched 2026-08-05 (`experiments/oeis_lookup.py --full
id:A225114`), has 24 terms, one comment and the conjectured continued
fraction, no asymptotic and no growth constant; A001523 confirmed on twelve
terms. Read-only lookups: `D_asc = 1, 3, 10, 34, 115, 382, 1244, 3993, 12689,
40065` and `D_desc = 1, 5, 19, 62, 185, 523, 1424, 3776, 9832, 25283` return
no match; none of the constants `1.4304046`, `1.2484659`, `1.28433727`,
`−1.25776216`, `1.29770192`, `1.19935960`, `2.53742253` or the `φ` recurrence
occurs anywhere in the repository's records.

## Reference values of the follow-up campaign (Tables A–D)

Measured 2026-08-05 on gympie, `git=54440c2-dirty`; the values every later
check compares against. A mismatch means the program is wrong, not the table.

**A. A006770, exclusion boxes on the 40 recorded terms** (`build/prec_guess`,
input `results/b006770_upload.txt`, prime 2^61−1, seconds per box):

| box (J,D) | `prec` verdict | `alg` verdict |
|---|---|---|
| (4,5) (5,4) (4,6) (3,7) (3,8) (2,11) (6,3) (7,3) | EXCLUDED | EXCLUDED |
| (5,5) | INCONCLUSIVE (35 rows ≤ 36 unknowns) | EXCLUDED |
| (6,4) | INCONCLUSIVE (34 rows ≤ 35 unknowns) | — |

The boxes are small because 40 terms is short; a finite-box exclusion is not
a non-D-finiteness proof (`results/closed-doors.md`).

**B. (dir4, HV-convex) against unrestricted HV-convex** (700-term series,
`results/mk_hvdir4_terms_n700.txt`, `results/convex_area_terms_n700_king.txt`):

```
amplitude ratio a_dir4(n)/a_HV(n), 54 trusted digits (n=600 vs n=700, minus 2 guard):
0.462109049209942440035662387700305832841163439729980425
subdominant ratio d_n/d_(n-1):  dir4  0.803651401483    unrestricted  0.481008794
PSLQ at 54 digits: NO relation in any in-capacity box --
  degree <= 12 at height <= 1e2, <= 5 at 1e4, <= 3 at 1e6, <= 2 at 1e8
```

The numbers are right; the reading "the two series do not share the
subdominant" was wrong (see "The corrected reading of Table B").

**C. A006770 by the geometric-case growth pipeline**
(`experiments/convex_growth.py results/b006770_upload.txt`): `d_n/d_(n−1)`
rises 0.94519 → 0.95062 over `n = 35..39`, drifting toward 1, the power-law
signature, against a flat 0.481 for HV-convex. Trusted digits: 0; the tool's
`µ = 7.1058` is wrong at the third digit, correctly, because Aitken on ratios
is the wrong accelerator when `θ ≠ 0`. This corroborates `θ = −1.000(1)`
(`results/growth-constant.md`) by a method that assumes no ansatz.

**D. Strip growth constants, two-parameter finite-size fit**
`ln µ_H = ln λ − a/H − b/H²` on consecutive triples of the certified `µ_H`
(`H = 2..17`, `results/growth-constant.md`):

| triple | λ | a | b |
|---|---|---|---|
| [11,12,13] | 7.29817 | 1.65351 | 3.19705 |
| [13,14,15] | 7.25820 | 1.51121 | 4.11872 |
| [15,16,17] | 7.22999 | 1.39472 | 4.99006 |

`H(ln λ − ln µ_H)` with `λ = 7.1102` is still falling at `H = 17` by 0.035
per step, increments shrinking only about 6.5% per step where a clean `1/H²`
correction predicts `(16/17)² = 11.4%`; identical for `λ = 7.111`. The
treatment (`experiments/strip_fss.py`) is in `results/growth-constant.md`.

The follow-up campaign's other outcomes live elsewhere: the minimum site
perimeter of king animals is A235382, `2⌈2√n⌉ + 4`, found by the grid pass's
min-reduce and verified rather than derived
(`experiments/min_site_perim_closed_form.py`, `tests/gate_site_perim.py`,
`results/perimeter.md`).

## When does a subclass have a closed form?

The question: given an attribute of polyplets, does conditioning on it give a
class one can count (rational or algebraic generating function, polynomial
cost) rather than enumerate? Two conditions.

1. **Conditioning must make the connectivity constraint one-dimensional.**
   Connectivity is the wall; an attribute buys a counting shortcut only if it
   collapses the two-dimensional constraint to a layer or heap recursion.
2. **The transfer operator must have finite rank in the unbounded state
   variable.** A one-dimensional profile evolution still carries an unbounded
   integer (the last column's height, the last row's width). If the operator
   entry `K(h, h')` is a finite sum `Σ_i f_i(h) g_i(h')`, Temperley's method
   closes to a finite linear system and the generating function is rational.
   If the predicate forces a comparison, an order relation, a `min`, a `max`
   or a running extremum, the rank is infinite and nothing closes.

The earlier version, "convexity ⇒ one-dimensional profile ⇒ algebraic or
rational", was falsified in three places inside the repository:
(ctrlB, column-convex), a profile evolution with rational excluded to order 12
and D-finite excluded in (12,12); the grounded row, where Ferrers polyplets
are the partition numbers A000041 (a `q`-series) and stacks A001523 sit beside
them; and HV-convex by area. The unbounded integer alone disqualifies nothing:
`K = h + h' + 1` (column-convex) has rank 2, which is why its derivation
closes on a 2×2 system; `K = h + 2` (4-cone) has rank 1; `min`/`max` coupling
has neither. Every rank quoted is measured with the area sequence its operator
generates by `experiments/kernel_rank_probe.py`. The mechanism is visible in
three places: the unbounded gap between pending blocks in the all-pairs
cluster family (`results/diagonal-formula.md`, not C-finite); the width in
the convex-area row transfer matrix, clipped by `min`/`max` onto phase targets
(not itself a running extremum); and ctrlB's running minimum, the literal
case. No family has a proof of no closed form; every negative is an exclusion
box.

What passes: directedness (forward cone ⇒ heaps of pieces ⇒ algebraic;
multi-directed is exactly solved through connected heaps and still
non-D-finite, so "exactly solved" and "closed form" differ); column-convex
by area (rank 2, A187077; the same operator with `h + h' − 1`, edge
adjacency, gives the classical column-convex polyomino count A001169,
`a(n) = 5a(n−1) − 7a(n−2) + 4a(n−3)`, ten terms reproduced, the rule's one
check outside the repository); directedness on top of column-convexity
(Propositions 1–5, each surviving operator rank 1: `h + 2` for A018902, two
rank-1 runs for the 5-cone class, `h + 1` for A007052); bargraphs
(`2^(n−1)`); bounded height (finite state, rational in `n`,
`results/fixed_height_gfs.txt`, cost exponential in `H`); convex families by
perimeter (A005436 algebraic by Delest–Viennot; HV-convex king animals
algebraic by semiperimeter, above). What does not: one-dimensional but
infinite-rank (HV-convex by area, ctrlB, Ferrers, stacks, and staircase, where
`K = min(h, h') + 1` generates A225114 from `n = 1` and the predicted
non-rationality was confirmed the same day at (24,24)); not even
one-dimensional (holes, edge-component count, perimeter, symmetry class,
parity, contact counts), which are stratified by enumeration and never
counted.

The area/perimeter split, explained and not: by semiperimeter the counting
variable is the bounding box `W + H`, so the unbounded state parameter is
bounded by the counting variable and the infinite-rank coupling cannot arise;
by area the width is free. The rule sorts rational from not-rational; it does
not say where a failing family lands, and by semiperimeter every family lands
algebraic (A005436, degree 2 for HV-convex king, degree 4 for the 4-cone
class) without the rule predicting it, nor does it explain why the polyomino
control A067675 fails by area in the same boxes.

None of the countable subclasses composes back to `a(n)`: directed does not
reduce to undirected, convex does not reduce to all. Parked lead (2026-07-10):
is there a small set of attributes whose joint value determines a polyplet
uniquely, a separating rather than partitioning invariant set? Recorded and
not pursued: the family "every local minimum of `b` within `k` rows of the
global minimum", between the rational 5-cone class and ctrlB, needs an
unbounded counter for every finite `k` (a later descent retroactively
invalidates an earlier local minimum), so every member sits on the wrong side
of the rule.

## Component-count stratification

`C(n, c)` = fixed polyplets of `n` cells with exactly `c` edge-connected (rook)
components; a polyplet's edge-components are polyominoes joined only at
corners. `experiments/component_stratification.py`, 2026-07-10.

| n\c | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | | | | | | | | |
| 2 | 2 | 2 | | | | | | | |
| 3 | 6 | 8 | 6 | | | | | | |
| 4 | 19 | 36 | 36 | 19 | | | | | |
| 5 | 63 | 156 | 200 | 156 | 63 | | | | |
| 6 | 216 | 660 | 1038 | 1040 | 662 | 216 | | | |
| 7 | 760 | 2752 | 5142 | 6236 | 5166 | 2776 | 760 | | |
| 8 | 2725 | 11390 | 24620 | 34962 | 35097 | 24860 | 11562 | 2725 | |
| 9 | 9910 | 46936 | 115050 | 186860 | 218824 | 188612 | 116936 | 47944 | 9910 |

- `Σ_c C(n,c) = A006770` and `C(n,1) = A001168` (fixed polyominoes).
- `C(n,n) = A001168` too, proved: `c = n` means every cell edge-isolated, so
  the animal is held together by diagonal contacts only; diagonal neighbors
  share checkerboard color, so it is a polyomino on the 45°-rotated
  sublattice. Prior art: A364928 (Achterberg 2023, corner-connected
  polyominoes ↔ ordinary polyominoes) is the free case; the fixed statement is
  not separately recorded.
- The distribution peaks near `c ≈ n/2` and is near-symmetric under
  `c ↔ n+1−c` (exact at the edges). `mean_c(n) = Σ_c c·C(n,c)/a(n)` runs
  1, 1.5, 2, 2.5, 3, 3.501, 4.003, 4.506, 5.009 for `n = 1..9`: a typical
  polyplet is about `n/2` edge-components of about 2 cells each. The framing
  "`mean_c = (n+1)/2`" is withdrawn: `Σ_c c·C(6,c) = 13416 ≠ 13412 = (7/2)a(6)`.
  The polyomino fraction `C(n,1)/a(n)` is about 1% at `n = 9` and shrinking.
- This fragmentation is the mechanism behind `λ ≈ 7.11 ≫ 4.06`: `a(n)` is
  dominated by corner-assemblies of small pieces. A species-style composition
  `a(n) = f(A001168)` does not close: corner-gluing is geometrically
  constrained (no overlap, specific adjacency, global connectivity), not free.
- Not in OEIS (row- and antidiagonal-flattened; columns `c = 2` and `c = 3`);
  no literature decomposes king animals by edge-component count.
  `experiments/tristruct/r3_l1_piece_states.py` reproduces the table for
  `n ≤ 7` from a piece-tracking DP.

## Rook and diagonal edges in a typical polyplet

A sampled distribution, retired 2026-07-31 as a closed door: it was collected
for "cheap core plus sparse correction" decompositions of king adjacency,
which were all measured dead (`results/closed-doors.md`), so the exact
`(size, rook-edge-count)` table, a small extension of the `--contacts` flag in
`cpp/g2_redelmeier.cpp`, is not worth building. The structural fact beneath
it, zero rook edges iff A001168, is the `bishopConn` check in the same program
and the identity `C(n,n) = A001168` above.

2000 uniform-random `n = 12` polyplets from `build/tma_sample` (seed 42),
king-adjacent pairs counted by type and stratified by rook-edge count:

| rook edges | count | fraction |
|---|---|---|
| 0 (entirely diagonal) | 4 | 0.20% |
| 1 | 36 | 1.80% |
| 2 | 89 | 4.45% |
| 3 | 195 | 9.75% |
| 4 | 305 | 15.25% |
| 5 | 366 | 18.30% |
| 6 | 397 | 19.85% (peak) |
| 7 | 285 | 14.25% |
| 8 | 177 | 8.85% |
| 9 | 93 | 4.65% |
| 10 | 40 | 2.00% |
| 11 | 11 | 0.55% |
| 12 | 2 | 0.10% |

Unimodal, peaking near the middle of the spanning-tree range, not
concentrated near 0: rook and diagonal edges occur in comparable amounts in a
typical polyplet, so an expansion from the pure-diagonal case would need the
whole histogram. Is the all-diagonal case a dominant term to correct toward?
No.

## Structure of a typical polyplet at n = 12

From the same 2000-specimen sample, 2026-07-07, plus exact facts from the
enumerations (the catalog `results/polyplet-zoo.md` is folded here; its rows
on height, symmetry and holes belong to `results/confidence.md`,
`results/symmetry-classes.md` and the hole sections below):

- Cut vertices: 99.9% of specimens have at least one, mean 6.7 of 12.
  Biconnected blocks: mean largest block 3.97 cells, mean block 2.39 cells,
  mean 8.47 blocks per shape. Large polyplets are near the tree-like extreme.
- Rook-only components: 99.8% are not single polyominoes, mean 6.575 pieces
  of 12, needing mean 5.575 diagonal glue edges.
- The rook↔bishop dual (swap which edges are rook and which diagonal, keeping
  the abstract graph): realized for 1% of specimens and proved impossible for
  99% by exhaustive search, not budget-limited; the self-dual asymmetric class
  at `n = 3` is a small-`n` artifact.
- Rook and bishop adjacency are an exact isomorphic pair via
  `(p, q) = ((c+r)/2, (c−r)/2)` on one checkerboard color, which is why
  `rookConn == bishopConn == A001168` exactly; the fraction of either is
  `A001168(n)/a(n) ~ (4.06/7.11)^n`, measured 0.20% at `n = 12`.
- Edge-perimeter `P = 4n − 2·(rook edges)` is tracked exactly by the
  production transfer matrix (`--perimeter`); its maximum `4n` is attained by
  the zero-rook-edge shapes.
- Interior cells `I` (all four rook neighbors present) are bracketed exactly
  by the perimeter, `n − P ≤ I ≤ n − P/4` (next section); the upper bound is
  tight for real shapes (mean slack 2.73 cells), the lower nearly useless
  (mean slack 25).
- Cyclomatic number is not tracked; it would follow from block sizes.
- Every cheap statistic (perimeter, holes, height, rook-edge count) is exact
  already or a small extension; every statistic needing global shape knowledge
  (cut vertices, blocks, interior-minus-cut-vertex counts) resists incremental
  tracking in a column pass because it depends on connectivity resolved
  later, not on the local frontier. Killed the same session, not merely
  omitted: crossing-partition compression of the frontier, a literal
  anti-diagonal pass, the three edge-type-layer decompositions (correction not
  sparse, 96.7%–99.8% disconnected), and #SAT/ASP/ZDD/Gröbner/holographic
  alternatives to the counting engine (`results/closed-doors.md`).

## Holes

A hole is a bounded 4-component of the complement (the convention fixed in
`results/closed-doors.md`, under the matching-pair convention). `A_k(n)`
counts polyplets with `k` holes; the exact table to `n = 18` is
`results/holes_n18.txt`, produced by `tma_holes square8 18 --holes` on ayr
(x86, 44 h single core, commit `8e41a63`), reproduced identically on dalby
(`results/holes_n18.dalby.txt`), single-engine at `n = 18` and cross-checked
against `g2 --holes` at small `n` by `tests/gate_holes.py` and `tests/gate_g2.py`.

### Hole-free polyplets are exponentially rare

**Theorem (Madras 1999, corollary).** `λ₀ < λ` strictly, and the hole-free
fraction `A₀(n)/a(n)` decays exponentially. Madras's pattern theorem
(*A pattern theorem for lattice clusters*, Ann. Comb. 3 (1999) 357–384,
`papers/madras_1999_pattern_theorem_lattice_clusters.pdf`, Theorem 2.1): for a
proper pattern `P = (P₁, P₂)` of sites required present and absent, clusters
containing at most `εn` translates are exponentially rare. Take `P₁` = the
eight neighbors of a cell, `P₂` = the cell: hole-free animals contain zero
translates. His §3.1(f), the spread-out lattice of range `M` in the sup norm,
is the king lattice at `M = 1`, so it applies directly; his Theorem 2.2 and
Corollary 3.6 also make the ratio limit `a(n+1)/a(n) → λ` a theorem for king
animals. The same argument proves the polyomino statement (`P₁` = four
neighbors), which is therefore not merely believed. Whittington and Soteros's
1990 survey (`papers/soteros_whittington_1990_rigorous_results_wild_guesses.pdf`,
§4) does exactly this and records that such gaps can be made quantitative
(`λ − λ₀ ≥ 0.00003758·λ₀`, Madras et al. 1988). Madras never mentions holes;
the corollary is ours, the theorem his.

Measured (`experiments/holefree_growth.py` on `results/holes_n18.txt`;
Domb–Sykes plus Richardson plus a log-linear fit):

| quantity | growth constant | θ (finite-size) | method |
|---|---|---|---|
| a(n) total | **λ ≈ 7.096** | −0.93 (→ universal −1) | Domb-Sykes + Richardson + log-linear fit |
| A₀(n) hole-free | **λ₀ ≈ 6.94** | −0.93 (same) | same |
| gap λ − λ₀ | **≈ 0.157** | | |

Two facts make `λ₀ < λ` robust at `n ≤ 18`: `log(A₀/a)` against `n` is linear
to five decimals (second difference about `1e−5` over `n = 12..18`), slope
`−0.0222` per cell, `ρ = 0.9779`; and the measured decay 0.97800 equals the
fitted `λ₀/λ = 0.97789` to four decimals. Quote the ratio `ρ = λ₀/λ ≈ 0.978`
and the exponential decay, not the third digit of `λ₀`: the same pipeline
returns `λ ≈ 7.096` against the true 7.110, so the method carries about 0.014
of error at this reach, which the gap survives elevenfold. Both classes share
`θ ≈ −0.93`; mean hole count per cell climbs 0.0132 → 0.0160 → 0.0176 at
`n = 10, 14, 18`, so holes are extensive; `A₁` and `A₂` approach `λ` from
finite size (`A₁`'s ratio still descending through 7.08). Madras's own §5
poses the shape of this measurement as an open problem (pure exponential decay
of a pattern-avoiding fraction with no power-law factor, ratio equal to the
ratio of growth constants), so the measurement is a data point on a stated
problem. Guttmann, Jensen, Wong and Enting (J. Phys. A 33 (2000) 1735–1764,
`papers/guttmann_jensen_wong_enting_2000_punctured_polygons_polyominoes.pdf`)
give `κ = 3.9709` for hole-free square polyominoes against `τ = 4.062591(9)`,
with finitely-punctured classes sharing `κ` and the exponent rising by one per
puncture, `a_n^(k) ~ κⁿ n^{k−1}`; their `κ/τ = 0.97743` against our
`λ₀/λ = 0.97800` is recorded as an observation only.

The `n = 19` term: `results/holes_n19.txt`, assembled from recovered dalby
telemetry with stamp `git=2c5e3e7-dirty`, which `docs/job-checklist.md` bars
from first-class recording; all 95 entries with `n ≤ 18` agree exactly with
`results/holes_n18.txt`, all 55 with `n ≤ 14` with the flood oracle
`results/holes_n14.txt`, and row sums equal `a(n)` through `n = 19`. Treat as
provisional. `a(19) = 151 609 203 011 580`; `A₀(19) = 108 898 235 427 176`,
`A₁(19) = 35 127 667 632 232`; max 11 holes; hole-free fraction 0.7183
(0.7344 at `n = 18`).

| quantity | n≤18 (stored control) | n≤19 (incl. degraded term) | Δ |
|---|---|---|---|
| λ | 7.0958 | 7.0974 | +0.0016 |
| λ₀ | **6.9389** | **6.9411** | +0.0022 |
| gap λ − λ₀ | 0.1569 | 0.1563 | −0.0006 |
| ratio λ₀/λ | 0.97789 | 0.97798 | +0.00009 |
| θ (both classes) | −0.93 | −0.94 | −0.01 |
| measured fraction decay ρ | 0.97800 (17→18) | **0.97801** (18→19) | +0.00001 |

Nothing changes qualitatively. Cost of more terms, from the per-height logs
`results/dalby-run-telemetry-202606/holes_n{16,17,18,19}_ph/h*.log`
(`tma_holes … --holes --per-height`, 8 threads; `n = 19` also cost 201
CPU-hours):

| n | Σ per-height wall | worst single height (critical path) | ratio vs n−1 |
|---|---|---|---|
| 16 | 2 490 s (0.7 h) | h16 = 950 s | — |
| 17 | 12 511 s (3.5 h) | h17 = 4 524 s | ×5.02 |
| 18 | 52 334 s (14.5 h) | h18 = 17 204 s | ×4.18 |
| 19 | 220 828 s (61.3 h) | **h19 = 77 818 s (21.6 h)** | ×4.22 |

| target | Σ per-height wall (est.) | worst height = critical path (est.) |
|---|---|---|
| n=19 (measured) | 61 h ≈ 2.6 days | 21.6 h |
| n=20 | ~258 h ≈ 11 days | ~3.8 days |
| n=21 | ~1 080 h ≈ 45 days | ~16 days |
| n=22 | ~4 550 h ≈ 190 days | ~67 days |

`n = 20` is a multi-day dalby campaign and `n = 22` a multi-month one;
declined.

### The hole-fill identity

For an `n`-cell polyplet `b` with exactly one hole of area 1 at `x`,
`T = b ∪ {x}` is an `(n+1)`-cell hole-free polyplet and `b = T ∖ {x}`, so
`b ↔ (T, x)` is a bijection between `{n-cell, 1-hole, area-1 polyplets}` and
`{(T, x) : T hole-free of size n+1, x an interior cell of T whose removal
keeps T connected}`. The forgetful map `(T, x) ↦ T` is not injective. With
`d(c) = 4 − rook-degree(c)`, `P = Σ_c d(c)` and `I = #{c : d(c) = 0}`,

    n − P ≤ I ≤ n − P/4,

exact from the definitions (checked on the 2000 samples, zero violations),
and

    1-hole-area-1(n) = Σ over hole-free T of size n+1 of #{interior cells of T that are not cut vertices}.

Structure, not a lever: filling a hole is always defined, but the reverse
needs `T`'s interior-cell and cut-vertex sets, which the production engines do
not track; the identity expresses a smaller quantity in terms of a bigger,
already-computed one, never the reverse, and the multi-cell generalization
does not change that. Prior art: Guttmann, Jensen, Wong and Enting prove in
their appendix that `k`-punctured polyominoes share the growth constant with
the exponent shifted by exactly 1 per puncture, by concatenation rather than
bijection; what is ours is the exact bijection for area-1 holes on the king
lattice with the failure of injectivity spelled out.

### Maximum enclosed hole area, M(n)

`M(n)` = maximum total enclosed empty area over `n`-cell polyplets. Exact by
`g2 --maxhole` for `n ≤ 17` (`results/maxhole.txt`; `M(17) = 28` matched the
prediction).

**Theorem (all holes).** For every `n`-cell king animal `F`, the total area of
the enclosed holes is at most `M(n) = ⌊((n−2)²+4)/8⌋` = `round((n−2)²/8)`,
and the bound is attained for every `n ≥ 4`.

Both halves are the grid isoperimetric inequality, cited, not ours. The
single-hole bound is Sieben 2008 Theorem 4.1 (`σ(e) = ⌊e²/8 − e/2 + 1⌋`, the
maximum size of an animal of site-perimeter `e`; and Theorem 5.3,
`ε(s) = ⌈2 + √(8s−4)⌉`, the minimum site-perimeter of an `s`-cell animal),
with `σ` equal to `M` on the nose. A sealed hole `H` of area `A` is
4-connected, hence a polyomino; every cell edge-adjacent to `H` from outside
is foreground (a background one would lie in `H`'s own 4-component), so
`n ≥ |sp(H)| ≥ sp_min(A)` and `A ≤ M(n)`. Nothing in it is king-specific:
the "king factor 1/8 against the rook 1/16" is site-perimeter against
edge-perimeter, the 8 of `√(8n−4)`.

*Proof of the multi-hole bound (the union argument).* The inequality holds for
an arbitrary finite subset of `Z²` with no connectivity hypothesis: Wang and
Wang 1977 (`papers/wang_wang_1977_discrete_isoperimetric_problems.pdf`, an
ordering of `Zⁿ` whose every prefix minimizes the boundary, the points not in
the set at Euclidean distance 1, which in `Z²` is `N(A)`), with the `Z²` count
explicit in Altshuler, Yanovsky, Vainsencher, Wagner and Bruckstein (DGCI 2006,
`papers/altshuler_etal_2006_minimal_perimeter_polyominoes.pdf`, Theorem 1,
reproved in their §3.1; their minimizers are connected, so `n(k) = ε(k)` and
allowing disconnection buys nothing). Let `A = ⋃ᵢ Hᵢ` be the union of the
bounded 4-components of `Z² ∖ F`. Take `c ∈ N(A)`: `c ∉ A`, and `c` is
4-adjacent to some hole `H_i`; were `c` background it would lie in `H_i`. So
`N(A) ⊆ F` and `n ≥ |N(A)| ≥ n(|A|) = ε(|A|)`, whence `|A| ≤ σ(n) = M(n)`. ∎

Wang–Wang's §6 lists the ordering's first thirteen points of `Z²`, the diagonal
diamond grown shell by shell, with the boundary defined as ours; their
Corollary 2 covers Manhattan-ball boundaries, not the 8-neighborhood, so the
4-connected-background convention is theirs and the 8-connected one is not
(for that, Altshuler et al. §3.2, `n₈ ≥ 4(√k+1)`, minimizers square); their
Corollary 1 says standard spheres also maximize interior points, and Corollary
5 is the abstract form of the superadditivity checked numerically. Bezrukov
(Bolyai Soc. Math. Stud. 3, 1994, §7b) has the `Zⁿ` case as the limit of the
torus problem with the same diamond order. Prellberg and Owczarek (CMP 201,
1999, eq. 3.1) state without proof the bond-perimeter twin: the maximum area of
a square-lattice polygon of perimeter `2n` is `n²/4` (`n` even) or `(n²−1)/4`.
`experiments/maxhole_sieben_check.py` checks: minimum site perimeter
brute-forced over all fixed polyominoes to `n = 9` against `ε` (with an
off-by-one control that must not match); `M(n) = max{A : ε(A) ≤ n}` for
`n ≤ 2000`; `σ(e) = M(e)`; Sieben's `ε` and Altshuler's `n(k)` agreeing at
every `k ≤ 200,000`; superadditivity; the 17 rows of `results/maxhole.txt`;
and the load-bearing hypothesis, every `≥ 2`-component subset of size
`k ≤ 10` (pairs, 3.4M configurations) and `k ≤ 8` (triples) failing to beat
`ε(k)`, tying only at `k = 2`.

*Construction (lower bound, all n ≥ 4).* Parity-aligned diagonal-box holes:
in diagonal coordinates `u = x+y`, `v = x−y`, `Hole(a,b)` = all cells with
`u ∈ [0, a−1]`, `v ∈ [0, b−1]`, corner-aligned so the populated parity class
dominates (area `⌈ab/2⌉`); the animal is its 4-neighbor ring, which has
exactly `a+b+2` cells off the degenerate margin, is king-connected, and
encloses exactly the box. Choosing `a+b = n−2` with the near-equal
parity-optimal split achieves `round((n−2)²/8)` for every `n ≥ 4` (`n = 5`
via the `n = 4` diamond plus one padding cell). Verified `n ≤ 60`
(`experiments/maxhole_box_construction.py`). Caveat from the adversarial
review of the Lean formalization (`docs/reviews/outworks-adversarial.md`): the
ring has `a+b+1` cells when `min(a,b) = 1` with `max(a,b)` even, and is a
multi-hole animal when `min(a,b) = 1` with `max(a,b) ≥ 3`
(`experiments/maxhole_review_checks.py`, all `a, b ≤ 12`); the optimizing
split never enters that margin. The diamond ring `{|x|+|y| = r}` is the
`a = b` odd case, `n = 4r` cells enclosing `2r² − 2r + 1`; the "slightly
asymmetric" optima at `n ≢ 0 (mod 4)` are the boxes with `|a−b| ∈ {1, 2}`.
Sieben's minimizers are the same diagonal diamonds and boxes.

*Independent reproofs of the single-hole bound, kept as checks.* (I')
`A ≤ ⌈ha·hm/2⌉`, with `ha`, `hm` the ranges of `u`, `v` over the hole, an
elementary parity count. (II') `n ≥ ha + hm + 2`, the moat-cycle argument,
machine-checked on 3,927 random single-hole animals (116 with pinched
contours, 3,356 tight; `experiments/maxhole_moat_check.py`, 0 failures):
(1) trace the outer contour of the hole region; across every boundary edge
lies a foreground cell, consecutive outside cells are equal, 4-adjacent or
diagonal (at pinch corners exactly the diagonal sealing pair), so they form a
closed king walk `γ ⊆ F` with winding 1 around the hole; (2) all hole centers
lie in one component of the complement of `γ`'s polygon, so one winding
number; (3) loop-erase `γ` to a simple cycle `σ ⊆ F` with nonzero winding
around every hole cell; (4) if `σ` stayed in `u ≤ u_max`, the top hole cell's
center would escape to infinity along `(1,1)` without meeting `σ`, so `σ`
attains `u ≥ u_max+1` and symmetrically the other three caps; (5) a king step
has `|Δu| + |Δv| ≤ 2`, `σ` spans `u` across `ha+1` and `v` across `hm+1`, so
`|σ| ≥ ha+hm+2` and `n ≥ |σ|`. Maximizing `⌈ha·hm/2⌉` over integers with
`ha+hm ≤ n−2` gives `M(n)` exactly for every residue. Rigor still owed on
step 1's contour construction and step 3's winding bookkeeping.
`polyplets/Polyplets/HolesUpper.lean` takes (II') as the named hypothesis
`MoatBound`, mathlib having no discrete-Jordan material, so the Lean bound is
conditional; `polyplets/Polyplets/Holes.lean` uses the floor form
`floor_maxhole_formula` (identical to the rounded form, checked to `n = 399`)
and the diagonal frame `hullBox ∖ boxHole`, which has `a+b+2` cells for all
`a, b`. Verification: `python3 -m experiments.maxhole_proof_check`.

*Superseded routes, recorded.* The multi-hole reduction by filling holes:
`F′ = F ∪ holes` is hole-free of size `N = n + A`, `A ≤ interior₄(F′)`,
`n ≥ |shell₄(F′)|`, and the master inequality
`interior₄(F′) ≤ round((|shell₄(F′)|−2)²/8)` (6,000 random filled animals, 0
violations, 1,028 tight; solid diamonds exactly tight) would give the bound;
its range-form core is false for disconnected interiors (two lone interior
cells in separate lobes: 11 filled cells, shell 9, `r_u + r_v = 8 > 7`). The
peeling lemma (hole-free `F′` with shell `S` and interior `I`, `|I| ≥ 2` ⟹
`|shell₄(I)| ≤ |S| − 4`) telescopes to exactly `round((m−2)²/8)` from the
bases `f(4..7) = 1, 1, 2, 3` (verified `m ≤ 199`) and is 0/7,645 on filled
animals plus adversarial families; its sub-lemmas (A-int)
`|shell₄(J)| ≤ r_u(J) + r_v(J) − 2` per interior component (false for general
king sets, 0/7,599 with 6,744 tight on interior components) and (Σ)
`Σ_j max(r_u,j + r_v,j − 2, 1) ≤ |S| − 4` (0/7,645, 885 tight) remain
unproved (`experiments/maxhole_peeling_check.py`). Refuted en route: the
union-range core, the per-component sum `Σ(r_u,j + r_v,j + 2) ≤ |S|` (a
7-cell example), and (A) for general king-connected sets. The merge lemma (a
`k ≥ 2`-hole animal admits `W ⊆ F`, `|W| = t`, with `F ∖ W` a king animal of
fewer holes and area `≥ A + t`) fails at the first multi-hole animal, `n = 6`,
`(0,2) (1,1) (1,3) (2,0) (2,2) (3,1)` with holes `{(1,2)}`, `{(2,1)}` sealed
across a shared diagonal: no cell can be removed without opening a hole; 6230
failures over all `n ≤ 9` (`experiments/maxhole_merge_probe.py`).

| n | multi-hole animals | max A (multi) | M(n) | slack |
|---|---|---|---|---|
| 6 | 2 | 2 | 2 | **0** |
| 7 | 42 | 2 | 3 | 1 |
| 8 | 544 | 3 | 5 | 2 |
| 9 | 5741 | 4 | 6 | 2 |

What is ours: the question (the polyomino hole literature counts holes,
Kahle and Roldán, Baralić and Uppal, Guttmann et al., rather than measuring
their area), the enumeration to `n = 17`, and the reproofs. A paper states
both halves with the citations. Citations in order: Wang and Wang, SIAM J.
Appl. Math. 32(4) (1977) 860–870; Sieben, European J. Combin. 29(1) (2008)
108–117 (`papers/sieben_2008_minimum_site_perimeter.pdf`); Altshuler et al.,
DGCI 2006, LNCS 4245, 17–28 (five authors).

### Maximum hole count

`maxholes(n) = n − ⌈2√n⌉ + 1`, which is A248333, matching all eleven measured
terms; the lower bound is proved by construction and the upper bound is open.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| max holes | 0 | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 4 | 4 | 5 |
| `n − ⌈2√n⌉ + 1` | 0 | 0 | 0 | 1 | 1 | 2 | 2 | 3 | 4 | 4 | 5 |

`n ≤ 9` from `experiments/king_extremal.py --nmax 9` (gympie, about four
minutes); `n = 10` on ayr, 16 minutes and 8.8 GB; `n = 11` on ayr 2026-08-23
at jasonp's direction, 4.28 h and 62.7 GB single core over all 39,299,408
animals, predicted 5, measured 5, the first term the formula had not seen.
The `n = 11` run re-derives `a(11) = 39,299,408` = A006770. Cost prediction
was 2 h and 55 GB from a 6.4×-per-term ratio; the real ratio to `n = 11` is
about 16×, so `n = 12` by this route is not worth it, and a targeted search
for high-hole animals is the right tool.

*Construction.* The even-parity sublattice `{(i, j) : i + j even}` is
king-connected by diagonal steps (a square lattice rotated 45° with spacing
√2), and every enclosed odd cell has all four orthogonal neighbors occupied,
so it is a singleton hole. An `a × b` block of the rotated lattice uses
`n = ab` cells and encloses `(a−1)(b−1)`. Maximizing complete unit squares
over `n` sites of a grid is the classical `n − ⌈2√n⌉ + 1`, attained by a
quasi-square grown by gnomons, which is how A248333 is defined; its terms,
offset by one, are 0, 0, 0, 1, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11,
12, 12, …. This is the "four king cells enclose a hole where the square
lattice needs eight" observation made quantitative (the diamond
`(0,0),(1,1),(2,0),(1,−1)` at `n = 4`).

*The gap.* On a single parity class, holes are at least the complete unit
squares, and the maximum of that over `n` sites is the classical count; but
an even-parity set with gaps can join odd cells into one 4-component, so
"holes = complete unit squares" needs the set solid in the rotated lattice.
**Conjecture (compression).** For every king-connected `A` there is a
single-parity king-connected `A'` with `|A'| ≤ |A|` and at least as many
bounded 4-components in its complement. Given it, the bound follows. A
mixed-parity animal beating every single-parity one of its size would have
been found by the exhaustive runs to `n = 11` if one existed that small.
`⌊n/2⌋ − 1` is ruled out (3 at `n = 9` against 4).

### Extremal diameter and articulation points

Exhaustive over all fixed king animals to `n = 9` (`experiments/king_extremal.py`,
four controls: A006770 reproduced; a 6-cell line has diameter 5 and 4
articulation points; a 3×3 block has neither articulation points nor holes;
the 8-cell ring has one hole). Diameter is the king graph's longest shortest
path; articulation points are cut vertices.

| n | animals | min diam | max diam | max artic | max holes |
|---|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 0 | 0 |
| 2 | 4 | 1 | 1 | 0 | 0 |
| 3 | 20 | 1 | 2 | 1 | 0 |
| 4 | 110 | 1 | 3 | 2 | 1 |
| 5 | 638 | 2 | 4 | 3 | 1 |
| 6 | 3,832 | 2 | 5 | 4 | 2 |
| 7 | 23,592 | 2 | 6 | 5 | 2 |
| 8 | 147,941 | 2 | 7 | 6 | 3 |
| 9 | 940,982 | 2 | 8 | 7 | 4 |

Three of the four are elementary: max diameter `n − 1` and max articulation
points `n − 2`, both by the straight line; min diameter `⌈√n⌉ − 1` by packing
into the smallest enclosing square (the `n = 10` run gives 3). No OEIS entry
for the min-diameter sequence (A000196 and unrelated hits).

## The single-cell move graph is connected for n ≤ 10

From an `n`-animal `A`, lift a non-cut-vertex cell and place it at any empty
position king-adjacent to the rest; this is the standard cell-move chain, and
connectivity of its graph on fixed animals is irreducibility, the first gate
on a uniform sampler. Reformulation that makes it cheap: `A` and `B` are
adjacent iff they share a common connected `(n−1)`-subanimal, so bucket every
animal by its legal deletions and union-find
(`experiments/move_graph_connectivity.py`, single-threaded Python, 2026-08-07,
gympie, `results/move_graph_20260807.log`):

| n | animals | components | largest | verdict | wall |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | connected | 0.0 s |
| 2 | 4 | 1 | 4 | connected | 0.0 s |
| 3 | 20 | 1 | 20 | connected | 0.0 s |
| 4 | 110 | 1 | 110 | connected | 0.0 s |
| 5 | 638 | 1 | 638 | connected | 0.0 s |
| 6 | 3832 | 1 | 3832 | connected | 0.1 s |
| 7 | 23592 | 1 | 23592 | connected | 0.5 s |
| 8 | 147941 | 1 | 147941 | connected | 4.4 s |
| 9 | 940982 | 1 | 940982 | connected | 35.6 s |
| 10 | 6053180 | 1 | 6053180 | connected | 289.7 s |

The vertex counts reproduce A006770 through `n = 10` independently. No animal
with `n ≥ 2` is stuck: every connected graph on two or more vertices has two
non-cut vertices. Wall grows 8.1× per term; `n = 11` is about 40 minutes and
memory-bound, `n = 12` needs C++. What this does not establish: it is a
census, not a proof (the proof route, every animal reaches a canonical bar, is
not written); irreducibility says nothing about mixing time, so no sampler
payoff follows. The square-lattice case is very likely a lemma of Janse van
Rensburg and Madras, J. Phys. A 30 (1997) 8035–8066, wanted in
`papers/MISSING.md`; novelty is not claimed.

## Machinery retargetable beyond polyplets

An inventory (2026-08-04), not results: novelty unchecked on every item,
nothing run on a non-king problem except where marked, no competitiveness
claimed, costs unestimated.

- **A1. The universal diagonal law** (`docs/proofs/universal-diagonal-law.md`),
  stated for the row-local class and already run on square, hex and king
  (`experiments/universal_law_check.py`, `experiments/hex_gas.py`,
  `experiments/diagonal_law_proof_check.py`; Lean `polyplets/Polyplets/Universal/`).
  Not instanced: triangular, the spread-8 neighborhood, `|dx| ≤ 2` lattices,
  directed and anisotropic variants; the obvious target is the A001168
  near-diagonal closed forms by the same peeling recursion and modular spine.
- **A2. The symmetry-companion machine** (`cpp/sym/symtm.cpp`,
  `scripts/derive_related.py`, `results/sym_counts.txt`) for any polyform
  family with a dihedral action; the subgroup-invariant counts are missing on
  every lattice.
- **B1. Certified spectral-radius bounds** (`cpp/strip_mu_cert.cpp`, a
  Collatz–Wielandt certificate in integers, needing neither positivity of `v`
  nor irreducibility) and the upper half `experiments/certificate_bound.py`
  (already run on Bui's rook six-type system, `λ_2 ≤ 4.63`): a
  machine-checkable two-sided bracket for constrained-coding capacity,
  subshift entropy, language growth rates.
- **B2. Mechanized non-D-finiteness** from strip generating functions
  (`experiments/anisotropic_dfinite.py`, `results/anisotropic-not-dfinite.md`):
  the widest reach, for self-avoiding walks and polygons by width, directed
  and convex families, percolation and dimer strips, bounded-height heap
  models.
- **B3. `polyplets/Polyplets/Northcott.lean`**, a standalone number-theory
  file: a house bound forces `M(minpoly) ≤ (max 1 B)^deg`, hence unbounded
  degree for pairwise distinct algebraic integers with a uniform house bound.
- **C1. The column-step engine** behind the `libenum` seam
  (`docs/engine-design.md`): commutative-associative reduce, work-stealing
  orchestrator, spill/merge, CRT counting, checkpoint and cross-architecture
  recount; retargets needing only a new transition table: SAW/SAP, percolation
  clusters, Potts/Ising strips, dimers, spanning forests.
- **C2. The measured infrastructure findings** (`docs/engine-record.md`):
  how to saturate a small heterogeneous fleet on a disk-bound enumeration.
- **C3. Verification methodology** as the deliverable: confidence tiers,
  fail-closed gates (`docs/engineering-standards.md`), per-term provenance,
  `docs/observability.md` (adopted wholesale by the `../oeis` sibling), and
  the computed-table-into-Lean pattern (`scripts/gen_pin.py`, `#guard_msgs`
  axiom footprints, in-tree `native_decide` bridges).
- **D1. Statistical physics**: king is the matching lattice of `Z²` for site
  percolation (`p_c` values sum to 1), so perimeter-refined counts plus the
  Sykes–Essam identity give `p_c` against the known 0.40725; finite-size
  scaling of the certified `µ_H` ladder against Yang–Lee predictions.
- **D2. The repository as primary source** on AI-assisted research, no
  compute; jasonp's call.

Ranked cheapest first: B2, B1, A1, then C3/D2 as write-ups, then C1 as a real
port.

## Open problems

- No proof that any series in this family is non-D-finite: HV-convex by area,
  (ctrlB, column-convex), (dir4, HV-convex), staircase A225114, and the
  polyomino control A067675 are all exclusions in boxes. The one concrete
  lead is the zeros of `K(q)` accumulating at `q = 1`.
- No series in the family has a proved sharp asymptotic `A(n) ~ Cµ^n`, not
  even the dominant one; Conjecture 8 (the phase-split asymptotics with
  `ρ = 0.4810…` and `σ = 0.5688…`) is measured to 76 and 64 digits. Kurkov's
  continued fraction for A225114 is the route.
- The amplitude ratio `r = (1/2)(w4·φ)/(w·φ)`: conditional on the amplitudes
  existing; neither `q`-series has a closed form; PSLQ negative in every box
  over `Q` and `Q(µ)`, bounded now by PSLQ cost, not precision. Whether `µ`
  is algebraic, or even irrational, is open; no integer polynomial of degree
  ≤ 20 at height ≤ 1e8, ≤ 30 at 1e6, or ≤ 12 at 1e15 has it as a root.
- Whether `ν = 2.5145796…` is the reciprocal of the smallest zero of the
  `det` of the s04 solution: untested, needs a convergent construction.
- `ρ_M` for A222205 has no minimal polynomial, being defined through the
  non-D-finite series `B`.
- The A055834 interpretation is conjecture-grade until the 4-cone class has a
  heaps-of-pieces derivation (Bousquet-Mélou–Conway's non-planar `L_n` family
  is the place to check).
- The `(ctrlB, column-convex)` exclusion box is the smaller only because its
  series stops at 250 terms; `n = 400` (11 minutes, 4 GB) would carry it to
  about (16,16). Not run.
- The quartic for (dir4, HV-convex) by semiperimeter is verified on 199 terms,
  not proved; six out-of-sample terms cost 21 minutes.
- Maximum hole count: the parity-compression conjecture, the whole remaining
  gap to `maxholes(n) ≤ n − ⌈2√n⌉ + 1`.
- Maximum hole area in Lean is conditional on `MoatBound`; the union
  argument would need the isoperimetric inequality as a hypothesis instead.
- The peeling lemma and its sub-lemmas (A-int) and (Σ) are verified and
  unproved, no longer needed for `M(n)`.
- A composition `a(n) = f(A001168)` over corner-gluing does not close; the
  `C(n, c)` triangle is the recorded output.
- Irreducibility of the move chain at general `n`, and its mixing time.
- Separating invariants: a small attribute set that determines a polyplet.
- A rigorous numeric gap `λ − λ₀` for hole-free king animals, by the
  Madras–Soteros–Whittington route.

## Reproduce

All laptop-scale unless marked. Grid and column transfer matrices:

```
make build/directed_cone_anchor build/middle_kingdom_tm build/convex_area_tm build/convex_perim_tm build/prec_guess
make gate-king-grid gate-multidirected gate-middle-kingdom gate-convex-dfinite gate-mk-dir4-perim gate-dir4-perim-alg
build/directed_cone_anchor grid 14 8 > results/mk_grid20_n14.txt           # 512 s wall / 3673 s cpu, 8 threads
build/directed_cone_anchor gridperim 14 8 > results/mk_dir4_perim_brute_n14.txt   # 74 s
build/directed_cone_anchor mdir 14 8                                        # 162 s
python3 experiments/directed_cone_anchor.py --dir5 15 --cone5 17 --ctrl 14 --threads 8   # ~14 min
python3 experiments/directed_cone_anchor.py --brute 9 --dir5 11 --cone5 12 --ctrl 11 --threads 8
python3 experiments/multidirected_king.py 200 --out results/multidirected_terms_n200.txt
python3 experiments/multidirected_king.py 12 --crosstab 8
build/middle_kingdom_tm ccdir5 700 > results/mk_ccdir5_terms_n700.txt      # 2.9 s
build/middle_kingdom_tm ccctrlb 250 > results/mk_ccctrlb_terms_n250.txt    # 66 s, 938 MB
build/middle_kingdom_tm hvdir4asc 700 > results/mk_hvdir4asc_terms_n700.txt
scripts/mk_stair_growth.sh                                                 # stair, hvmono, ~15 s
python3 experiments/oeis_lookup.py 1,4,17,71,289,1149,4481,17209,65281
```

Convex by area and the exclusions:

```
build/convex_area_tm 700 1 > /dev/null   # king, ~8 min
build/convex_area_tm 700 0 > /dev/null   # control, ~7 min
build/prec_guess prec results/convex_area_terms_n700_king.txt 24 24
build/prec_guess alg  results/convex_area_terms_n700_king.txt 24 24
build/prec_guess prec results/mk_stair_terms_n700.txt 24 24
build/prec_guess alg  results/mk_stair_terms_n700.txt 20 20
python3 experiments/convex_growth.py results/convex_area_terms_n700_king.txt --prec 500 --algdeg 20 --maxcoeff 100000000
python3 experiments/convex_growth.py results/mk_hvdir4_terms_n700.txt --prec 500 --algdeg 20 --maxcoeff 100000000
python3 experiments/convex_heights.py
python3 experiments/convex_kernel_zeros.py
```

Convex by semiperimeter:

```
build/convex_perim_tm 200 1 > results/convex_perim_terms_s200.txt          # 1246 s
build/convex_perim_tm 200 1 dir4 > results/mk_dir4_perim_terms_s200.txt    # 1073 s
scripts/dir4_perim_dfinite_sweep.sh; scripts/dir4_perim_dfinite_nullcontrol.sh
scripts/dir4_perim_boundary_scan.sh; scripts/dir4_perim_minimal_box.sh; scripts/dir4_perim_nullity_grid.sh
python3 experiments/dir4_perim_find_alg.py 4 22
python3 experiments/dir4_perim_find_prec.py 19 3
```

The squeeze, the split, the spectrum and the amplitude ratio (the long pole is
the seven-series spectrum, 8 minutes; the two PSLQ sweeps are tens of minutes
each):

```
python3 experiments/staircase_supermul.py
python3 experiments/monotone_block_growth.py --nmax 400
python3 experiments/square_staircase_area.py
python3 experiments/dir4_descent_block.py --nmax 700 --out results/mk_dir4_descblock_n700.txt \
        --compare results/mk_hvdir4_terms_n700.txt --prec 400
python3 experiments/descent_block_oracle.py --nmax 700 --brute 13 --check results/mk_dir4_descblock_n700.txt
python3 experiments/descent_block_oracle.py --phases 14
python3 experiments/descent_block_oracle.py --mirror 14
python3 experiments/subdominant_identification.py --order 10 --dps 1500
python3 experiments/staircase_cf_poles.py --depth 24 --terms 40
python3 experiments/ratio_amplitude.py results/mk_hvdir4asc_terms_n700.txt results/convex_area_terms_n700_king.txt --prec 700 --drop 100
python3 experiments/ratio_amplitude.py results/mk_hvdir4_terms_n700.txt results/convex_area_terms_n700_king.txt --prec 700 --drop 100
python3 experiments/amplitude_feed_vectors.py --dps 500 --hmax 1200 --emit results/amplitude_ratio_constants.txt
scripts/amplitude_pslq_sweep.sh 185 results/amplitude_pslq_185.log
scripts/amplitude_pslq_sweep.sh 251 results/amplitude_pslq_251.log 2:1e40,3:1e30,5:1e20,10:1e11,20:1e5,30:1e4 5:6:1e2,4:5:1e4,3:4:1e6,2:4:1e8
python3 experiments/kernel_rank_probe.py
```

Stratifications, holes and the move graph:

```
python3 experiments/component_stratification.py
python3 experiments/holefree_growth.py
python3 -m experiments.maxhole_proof_check
python3 -m experiments.maxhole_sieben_check
python3 experiments/maxhole_moat_check.py; python3 experiments/maxhole_box_construction.py
python3 experiments/maxhole_peeling_check.py; python3 experiments/maxhole_merge_probe.py
python3 experiments/king_extremal.py --nmax 9      # ~4 min; --nmax 10 is 16 min / 8.8 GB, --nmax 11 is 4.3 h / 63 GB (ayr)
python3 experiments/move_graph_connectivity.py
```

Series and data: `results/mk_{cc,ccdir5,ccdir4,hvdir4,hvdir4asc,hvdir4desc,stair,hvmono}_terms_n700.txt`,
`results/mk_ccctrlb_terms_n250.txt`, `results/mk_dir4_descblock_n700.txt`,
`results/mk_grid20_n14.txt`, `results/multidirected_terms_n200.txt`,
`results/convex_area_terms_n{500,700_king,700_poly}.txt`,
`results/convex_perim_terms_s200.txt`, `results/mk_dir4_perim_terms_s200.txt`,
`results/a005436_perim_s100.txt`, `results/maxhole.txt`,
`results/holes_n{14,18,19}.txt`, the `results/b*_upload.txt` files above,
`results/convex_height_denominators.json`, and the logs named in the text.

## Sources

- `results/middle-kingdom.md` (deleted 2026-09-06; its content is above)
- `results/middle-kingdom-grid.md` (deleted 2026-09-06; its content is above)
- `results/middle-kingdom-phase3.md` (deleted 2026-09-06; its content is above)
- `docs/middle-kingdom-plan.md` (deleted 2026-09-06; its content is above)
- `docs/middle-kingdom-followups-plan.md` (deleted 2026-09-06; its content is above)
- `results/mk-dir4-perimeter.md` (deleted 2026-09-06; its content is above)
- `results/hv-growth-sandwich.md` (deleted 2026-09-06; its content is above)
- `results/king-subfamilies.md` (deleted 2026-09-06; its content is above)
- `results/countable-subpopulations-criterion.md` (deleted 2026-09-06; its content is above)
- `results/convex-polyplets.md` (deleted 2026-09-06; its content is above)
- `results/convex-anisotropic.md` (deleted 2026-09-06; its content is above)
- `results/directed-king-animals.md` (deleted 2026-09-06; its content is above)
- `results/directed-cone-anchor.md` (deleted 2026-09-06; its content is above)
- `results/multi-directed.md` (deleted 2026-09-06; its content is above)
- `results/beyond-polyplets.md` (deleted 2026-09-06; its content is above)
- `results/polyplet-zoo.md` (deleted 2026-09-06; its content is above)
- `results/component-stratification.md` (deleted 2026-09-06; its content is above)
- `results/move-graph-connectivity.md` (deleted 2026-09-06; its content is above)
- `results/rook-bishop-edge-distribution.md` (deleted 2026-09-06; its content is above)
- `results/king-extremal.md` (deleted 2026-09-06; its content is above)
- `results/hole-fill-interior-cell-identity.md` (deleted 2026-09-06; its content is above)
- `results/hole-free-growth-constant.md` (deleted 2026-09-06; its content is above)
- `results/maxhole-closed-form.md` (deleted 2026-09-06; its content is above)
- `results/maxhole-proof.md` (deleted 2026-09-06; its content is above)
