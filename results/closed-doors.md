# Closed doors: routes past the enumeration

Every route this project tried for counting polyplets other than the column
transfer matrix and the diagonal formula, with the obstruction that closed it;
the measurements that closed them; the ideas never tried; and the conjectures
that remain open. Grades: the closures in sections 1 through 5 rest on exact
counts or measured state counts, each with its script and run; the congruence
of section 1.6 and the parametric master equation of section 6 are proved and
then checked against enumerated entries; the matching-pair relation of
section 4 is verified in exact arithmetic through order 9; everything under
open problems is conjectured or measured, not proved.

## What is in here

| section | the door, and what shut it |
|---|---|
| 1. The frontier does not compress | every attempt to make the transfer matrix smaller: low-rank states, the Hankel floor that grows at 2.43 per height, the char-0 cell-level transfer, the 2-adic filtration, and the one that worked as a congruence rather than a saving |
| 2. Re-slicing, recurrences, finite-lattice inclusion-exclusion | other ways to cut the lattice, the C-finite order each one costs, and why the finite-lattice method does not stack |
| 3. Handles on connectivity other than a partition | determinants, blocking, fattening, dual connectivity, relaxation hierarchies, exact-bulk-plus-tail: eight ideas and the four causes they all reduce to |
| 4. The percolation matching pair | the relation, verified in exact arithmetic through order 9, and what it does not buy |
| 5. Below the onset | two probes for the defect constants that did not yield them |
| 6. The master equation is lattice-parametric | proved, then checked against enumerated entries on three lattices |
| 7. Converse checks on the universal claims | where the universal statements stop being true |
| 8. Ideas not taken | what was measured before each was set aside |
| Open problems | what is still open, conjectured or measured but not proved |

## Terms

A **polyplet** is a finite set of cells of the square grid, connected under
king adjacency (edge or corner contact). `a(n)` counts polyplets of `n` cells
up to translation, OEIS A006770. `T(n,H)` counts those whose bounding box has
height exactly `H`; the table of `T(n,H)` is the triangle
(`results/triangle.txt`), and a value of it is an entry. `C_H(n)` counts
polyplets of height at most `H`, so `T(n,H) = C_H − 2C_{H−1} + C_{H−2}`.

The **column transfer matrix** is the production engine. It processes a strip
of height `H` one lattice cell at a time and carries, for each reachable
boundary state, a count by size; a boundary state records which boundary
cells are occupied and how they connect through the region already processed.
The set of boundary states at a column boundary, with their counts, is the
**frontier**; at height `H` the reachable column states number
`Motzkin(H+1) − 1`. The **cancellation DP** (`results/cutcount_b1/`) is an
independent program that produces `C_H(n)` by a coloring rule instead of
tracking connectivity.

The **diagonal formula** for level `k` is `T(n, n−k) = P_k(n) · 3^(n−1−3k)`,
with `P_k` a polynomial of degree `k` and leading coefficient `25^k / k!`. It
holds for `n ≥ 2k+1`, and `n = 2k+1` is the **onset** of level `k`. An entry
with `n ≤ 2k` is below the onset; its **depth** is `j = 2k+1−n` and its
**defect** `D_j(k)` is the entry minus the formula value. The **grand form**
`F(n,u) = C(u) · H(u)^n` (`docs/proofs/grand-form.md`) makes the cumulants
`c_k(n) = A_k n + B_k` linear in `n`. The engine's coefficient table
`diagCoeffTable` holds `P_1 … P_19`, fitted from enumerated entries; a height
is *injected* when its entries come from that table instead of a run.

`λ` is the growth constant `lim a(n)^(1/n)`; `μ_H` is the growth constant of
the strip of height `H` (the strip ladder). The **family DP**
(`cpp/severance_w3_families.cpp`) is the dynamic program that computes the
defects `D_j`, `j ≥ 2`, from clusters of bounded excess `e`, one level `K` at
a time.

## 1. The frontier does not compress

### 1.1 Spatial low-rank structure: a matrix-product state loses

Probe of 2026-07-02 (`experiments/frontier_svd/`, deleted in the 2026-08
tidy; readable with `git show 78602f8^:experiments/frontier_svd/svd_probe.py`).
The frontier count-vector lives on a chain of `H` boundary sites. If its
Schmidt rank `χ` across a central cut were small, a matrix-product state (MPS)
would store it in `H · χ²` entries. The rank was measured on the real vector.

| H | frontier states | exact rank χ, central cut | χ² / frontier | MPS cost H·χ² | frontier / MPS |
|---|---|---|---|---|---|
| 8 | 1,604 | 21 | 0.28 | 3,528 | 0.45 |
| 10 | 11,005 | 51 | 0.24 | 25,000 | 0.44 |
| 12 | 68,343 | 127 | 0.24 | 178,608 | 0.38 |
| 14 | 161,357 | 298 | 0.55 | 623,294 | 0.26 |

The rank grows about 2.4 per two units of height, so `χ ~ λ^(H/4)`, the
square root of the frontier. The singular values barely decay: at `H = 12` the
second is 0.60 of the first and 122 of the 127 exceed a relative `1e-6`. The
`H = 14` dump was taken at `maxn = 16`, off the peak column, which inflates
its ratio. Cutting the boundary splits the non-crossing partitions, and the
rank at the cut counts the ways components cross it, which is Catalan-like.
Exact storage is worse than the explicit frontier at every height and the
ratio falls with `H`.

At a relative truncation of `1e-3` the effective rank drops to about
`0.16 · √frontier` (42 against 127 at `H = 12`), storage about three times
smaller than the frontier, but the count is then approximate and the error
compounds across columns. A Temperley–Lieb link-pattern basis is the only
form that could help in principle; the known representations do not drop
below the Catalan dimension for exact work.

### 1.2 The temporal Hankel rank: the floor grows at 2.43 per height, not 3

`scripts/probe_hankel_rank2.py`, ayr, 2026-08-21. The observability
dimension of the column transfer over `F_p`, `p = 2^31 − 1`, is the rank of
the Hankel matrix of the column-level counting function, prefixes against
suffixes over column words. It is a floor on how many quantities any
field-linear method of this shape must carry across a cut. An earlier
analysis on another branch measured it to `H = 10`; seven points admitted
two readings that disagree at `H = 11`.

| H | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|
| char-0 Hankel rank | 6 | 17 | 35 | 88 | 204 | 501 | 1217 | **3016** |

| reading | predicted H = 11 |
|---|---|
| power-law quotient, floor base exactly 3 | 3091 |
| geometric quotient, floor base about 2.79 | 3281 |

Two weights, `x = 1` and `x = 123456789`, both give 3016, each in about
16.5 h single-core with 7.6 GB. `--anchor` reproduces the seven earlier
points. Two weights agreeing rule out an unlucky prime; the anchor rules out
a wrong automaton.

| fit window, geometric law | base |
|---|---|
| last 4 points | 2.4518 |
| last 5 points | 2.4241 |
| last 6 points | 2.4289 |
| all 8 points | 2.4051 |

The last three quotients are 2.4559, 2.4291, 2.4782. The floor grows near
2.43 per height, below the raw frontier's rate, so the gap widens with every
height and the "class closed" reading dies. No recurrence of order at most 3
with a constant term fits the eight points
(`experiments/height_dimension_ladders.py`, exact rational elimination);
order 4 cannot be tested on eight values. An OEIS lookup returned nothing.
This is headroom, not an engine: there is no explicit basis to build a
compressed transfer against.

| H | wall, single-core on ayr, one weight |
|---|---|
| 8 | ~20 s |
| 9 | ~155 s |
| 10 | ~2,495 s |
| 11 | 59,422 s |

The per-height cost ratios 7.8, 16, 23.8 grow an order of magnitude faster
than the floor; `H = 12` extrapolates to about 400 hours single-core.

### 1.3 Five sizes of height H, and which bounds which

- **Char-2 column rank** `r(H)`: rank over `GF(2)` of the Hankel matrix of the
  column-level function, rows indexed by the frontier partitions; equals
  A034299 at every measured point (`results/arithmetic-structure.md`).
- **Char-0 Hankel rank**: the same integer matrix over `Q`, measured mod
  `2^31 − 1` (section 1.2).
- **Reach-merged class count** `N(H)`: a state count, the classes of frontier
  partitions under the coarsest congruence the transition rule can see (1.6).
- **New-root degree** `deg ψ_H`: the denominator factors of the fixed-height
  generating function `G_H(x)` appearing first at height `H`
  (`results/anisotropic-not-dfinite.md`); a polynomial degree in the size
  variable, not a state-space dimension.
- **Cell-level compressed dimension** `d_p`: rank over `F_p` of the
  lattice-cell-granularity function, what an algorithm reading one cell at a
  time would carry; `d_2` the same over `GF(2)` (1.4).

| quantity | H known | at H = 8 | growth, range / last step | where |
|---|---|---|---|---|
| char-2 column rank `r(H)` | 4..13 | 112 | 2.04 / 2.00 | `results/arithmetic-structure.md` |
| char-0 Hankel rank | 4..11 | 204 | 2.43 / 2.48 | section 1.2 |
| reach-merged classes `N(H)` | 4..21 | 239 | 2.48 / 2.59 | section 1.6 |
| new-root degree `deg ψ_H` | 1..10 | 462 | 2.46 / 2.62 | `results/anisotropic-not-dfinite.md` |
| raw column frontier | all H | 834 | 2.69 / 2.81 | `Motzkin(H+1) − 1` |
| char-2 cell rank `d_2` | 4..8 | 1,155 | 2.45 / 2.24 | section 1.4 |
| char-0 cell dimension `d_p` | 4..8 | 1,826 | 2.75 / 2.64 | section 1.4 |

- `N(H) ≤` raw frontier: proved, a quotient of the frontier partitions.
- Hankel rank over any field `≤ N(H)`: proved, since two states in one class
  have identical Hankel rows. Tightest at `H = 11`: 3,016 against 3,441.
- Column rank `≤` cell rank in each characteristic: proved, the column Hankel
  matrix is a submatrix of the cell one.
- Char-2 rank `≤` rational rank of the same matrix: proved. The char-0
  numbers are mod-`p` ranks, themselves lower bounds for the rational rank,
  so `r(H) ≤` the measured char-0 value is observed at eight heights, not
  proved; likewise `d_2 ≤ d_p`.
- `deg ψ_H` against any rank: no relation, and the natural guess is false. It
  exceeds the char-0 Hankel rank from `H = 7` on (181 against 88; 3,289
  against 1,217). The only bound is `deg ψ_H ≤ deg Q_H ≤ H · N(H)`, at
  `H = 10` reading 3,289 ≤ 13,990. The minimal recurrence order of `T(n,H)`
  in `n` is `deg Q_H`, not `deg ψ_H`.
- `d_p` against the column-level quantities: no downward relation; it exceeds
  all of them at every shared height.

Growth respects the order the sizes do, so nothing is on course to cross.
`experiments/height_dimension_ladders.py` re-checks every inequality and both
orderings in under a second and exits nonzero on failure.

### 1.4 The cell-level compressed transfer in characteristic 0

`experiments/skeletonkey/cell_sparsity_modp.py`, ayr, 2026-08-22, data in
`results/skeletonkey/cellsparse.txt`, primes 131071 and 65521. The earlier
rank-compression analysis had rejected a compressed engine assuming the
compressed transfer is dense, and named sparsity as the one unprobed rescue.

| H | cell states | column states | d_p | d_p / col | d_p ratio | col ratio | mean nonzeros per row A₀ | dense d/2 | sparser by |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 300 | 20 | 32 | 1.60 | — | — | 1.06 | 16.0 | 15× |
| 5 | 1,550 | 50 | 99 | 1.98 | 3.094 | 2.500 | 1.24 | 49.5 | 40× |
| 6 | 7,938 | 126 | 249 | 1.98 | 2.515 | 2.520 | 1.39 | 124.5 | 90× |
| 7 | 40,894 | 322 | 692 | 2.15 | 2.779 | 2.556 | 1.77 | 346.0 | 195× |
| 8 | 212,670 | 834 | 1,826 | 2.19 | 2.639 | 2.590 | 2.15 | 913.0 | 425× |

The `H = 8` row took 2 h 47 min and about 7 GB. `cell states` is a
presentation size, `column states × (2^H − 1)`, not a live count; do not
divide by it. Gates: the char-2 cell rank reproduces the recorded 32, 93,
210, 516 at `H = 4..7`, and perturbed successor maps give ranks 373, 362,
374, none of them 93.

The sparsity rescue is real: the density assumption was wrong by more than
two orders of magnitude. The compressed engine still loses, on dimension: it
is already larger than the column frontier it would replace at every height
measured, and grows faster. The ratio's own 1.082 per height gives about 6×
worse at `H = 21`; it is decelerating (1.24, 1.00, 1.09, 1.02 per step), so
3× is as defensible. Both exceed 1.

    row weights at H = 8,  generator basis     A0 = 65.01,  A1 = 113.03
                            compressed basis    A0 =  2.15,  A1 =   2.68

A sparse basis exists in characteristic 0 and the compression finds it;
writing it down changes nothing, because dimension is what beats the char-0
engine. In characteristic 2 the cell-level dimension is smaller (1,155
against 1,826 at `H = 8`) and there the basis is unknown, so a basis hunt is
motivated by the char-2 collapse and never by char-0 sparsity. Limits: five
heights; two primes near `2^17` and `2^16` agreeing is evidence, not proof;
nobody has looked at the compressed basis vectors themselves.

### 1.5 The 2-adic filtration

Rank over `Z/2^m` counts elementary divisors of 2-valuation below `m`, so the
char-2 rank is the first layer of a filtration, and an exact `a(60)` needs
about 168 bits. The record already closes it. The collapse to A034299
(`r(21) = 932,071`) is at column granularity, and the column-level automaton
needs one `r × r` matrix per column mask, `2^H − 1` of them. At cell
granularity the char-2 rank is `Θ(H · 2^H)`, about `2e7` at `H = 21`, against
the engine's reachable `1.3e8`. The ceiling is about 6× in state count, exact
values need words about 2.6× wider than the engine carries, and the best case
is roughly 2×, under one height, against a cost growing about 2.9× per
height. The factor of `H` between column rank and cell rank is the whole
difference between a 6× win and a 20× one, and between either and the floor
of section 1.2.

### 1.6 The reach-merged frontier: a congruence, proved and counted to H = 21

Two frontier states are equivalent when they carry the same multiset of
block neighborhoods `N(b) = rows(b)` expanded by `±1` and clipped to
`[0, H)`. The transition reads nothing about a block except `N(b)`: a new
cell at row `r` attaches to `b` iff `r ∈ N(b)`, and `b` strands iff the new
column's mask misses `N(b)`. So this is a congruence of the language over any
semiring, not a mod-2 fact, and the merged set is exactly the end-of-column
frontier the engine writes out (`docs/engine-record.md`). Probe
`experiments/skeletonkey/nfamily_merge.py`, ayr, 2026-08-20, exact integers,
sharing no code with the engine.

| H | raw states | merged | ratio | raw growth | merged growth |
|---|---|---|---|---|---|
| 4 | 20 | 8 | 2.500 | — | — |
| 5 | 50 | 19 | 2.632 | 2.500 | 2.375 |
| 6 | 126 | 43 | 2.930 | 2.520 | 2.263 |
| 7 | 322 | 101 | 3.188 | 2.556 | 2.349 |
| 8 | 834 | 239 | 3.490 | 2.590 | 2.366 |
| 9 | 2,187 | 575 | 3.803 | 2.622 | 2.406 |
| 10 | 5,797 | 1,399 | 4.144 | 2.651 | 2.433 |
| 11 | 15,510 | 3,441 | 4.507 | 2.676 | 2.460 |
| 12 | 41,834 | 8,539 | 4.899 | 2.697 | 2.482 |

The merged column reproduces the independent `minauto` count 8,539 at `H = 12`
from the characteristic-2 work (`results/arithmetic-structure.md`). Gates,
all fail-closed: reachable count `Motzkin(H+1) − 1` at `H = 2..8`; the raw
automaton reproduces the cancellation DP's `C_H(n)` rows for every `n ≤ 12`;
`succ_key(key(s), m) == key(succ(s, m))` for every reachable state against
every column mask; the key automaton built with no partition state
reproduces the same `C_H(n)`; the automaton with touched-top and
touched-bottom flags emits `T(n,H)` directly and equals the telescope of
`C_H` for every `n ≤ 12`; on the rook lattice `N(b) = rows(b)`, so the counts
must equal the raw frontier, and do (3, 8, 20, 50, 126, 322, 834); no row is
covered by more than two neighborhoods; dropping the `±1` expansion gives 5,
9, 24, 67, 195 where king gives 5, 17, 72, 332, 1582. One bug: sorting the
neighborhood sets as `frozenset`s sorts by the subset partial order, so one
class could split in two; bitmasks fixed it and no gate changed.

**The exact-height flags** block merges between frontiers that differ only
in whether a boundary row was ever occupied.

| H | flagged raw | flagged merged | flagless raw | flagless merged | today ÷ best |
|---|---|---|---|---|---|
| 4 | 39 | 21 | 20 | 8 | 4.88 |
| 5 | 98 | 48 | 50 | 19 | 5.16 |
| 6 | 246 | 108 | 126 | 43 | 5.72 |
| 7 | 624 | 248 | 322 | 101 | 6.18 |
| 8 | 1,604 | 580 | 834 | 239 | 6.71 |

"Flagged raw" is what `core/kink_column.h` produces today. The flags are a
flat ~1.92× that does not compound, and they blunt the merge (2.77× flagged
against 3.49× flagless at `H = 8`); the telescope costs no extra runs. The
vertical mirror fold composes with the merge: 239 keys fold to 128 orbits at
`H = 8`. The merge is king-only: king adjacency blurs rows, so a component on
row 1 alone and one on rows 0 and 1 both reach `{0,1,2}` and no later column
can tell them apart, while on the rook lattice nothing merges. That is why it
does not appear in the polyomino literature.

**The census to H = 21.** `cpp/nkey_census.cpp`, two engines, dalby,
2026-08-23, rev `252921b10`. The first engine generates successors per source
state; the second (`--shared`) processes a batch of sources together one row
at a time, carrying only what the remaining rows can still see, so sources
that differ only below the current row share their remaining work.

| H | classes | ratio | wall, per-source engine | wall, shared engine |
|---|---|---|---|---|
| 13 | 21,355 | 2.5009 | seconds | 2.3 s |
| 14 | 53,763 | 2.5176 | 293 s | 7.9 s |
| 15 | 136,145 | 2.5323 | 1,960 s | 25.3 s |
| 16 | 346,539 | 2.5454 | 10,454 s | 103.8 s |
| 17 | 886,111 | 2.5570 | not run | 235.7 s |
| 18 | 2,275,103 | 2.5675 | not run | 705.0 s |
| 19 | 5,862,925 | 2.5770 | not run | 2,114.5 s |
| 20 | 15,159,215 | 2.5856 | not run | 6,430.3 s |
| 21 | 39,314,963 | 2.5935 | not run | 17,532.6 s |

Both engines run the class counts at `H = 4..13` and the rook control (with
the dilation off the count must be the raw frontier, `H = 2..10`) before any
height is reported. Count agreement alone is not enough: disabling the
stranded-block prune leaves every class count intact, because the successors
it invents are reachable by another route. So `--gate` also compares the two
engines' successor sets per source at every reachable key, `H ≤ 11` king and
`H ≤ 9` rook. Of five planted changes, three fire in both checks, allowing a
stranded block fires only in the successor-set check, and two
optimization-only changes stay green: a labeling that fails to canonicalize
costs duplicated work, never a wrong count. A retirement-rule hazard found by
reading the code (a closed group and the open run sharing an old block whose
last row had just passed, filed as two components) changes nothing at
`H = 14, 15` exactly and at `H = 16` by three agreeing engines.

Peak resident memory (RSS) of the shared engine at `H = 13..17` was 38.9,
95.1, 238.6, 578.5, 1,448.3 MB, about 2.47 per height, so the memory is the
key set. The batch cap bought nothing: at `H = 17` batch 131,072 ran 505.3 s
and 1,429 MB against 235.7 s and 1,448 MB unbatched. The first engine would
need roughly 475 days for `H = 21`; the shared engine is a constant factor of
about a hundred, not a change of exponent.

| H | 18 | 19 | 20 | 21 |
|---|---|---|---|---|
| predicted ratio, chained | 2.567 | 2.575 | 2.583 | 2.590 |
| measured ratio | 2.5675 | 2.5770 | 2.5856 | 2.5935 |
| predicted classes | 2,274,647 | 5,858,390 | 15,143,935 | 39,262,367 |
| measured classes | 2,275,103 | 5,862,925 | 15,159,215 | 39,314,963 |
| error | +0.020% | +0.077% | +0.101% | +0.134% |

Two other projections were wrong. Wall time was out by up to 8× in the safe
direction (`H = 21` priced at ~1.6 days ran in 4 h 52 min), because the
projection was anchored on batch-capped runs. Peak RSS at `H = 18..21` was
3.60, 8.76, 22.73, 63.21 GB with the ratio climbing (2.434, 2.596, 2.781); at
the last ratio `H = 22` needs about 176 GB against dalby's 125, so the census
stops at `H = 21` on that hardware, for memory.

39,314,963 classes at `H = 21` against the a(40) run's end-of-column
frontier of 355,390,806 records and 363.4 GB of disk
(`results/ns_a40/PROVENANCE.md`) is a state-space cut of 9.04×. Adoption
would replace the `canonicalizeSig` call in `kinkFinalizeColumn`
(`core/kink_column.h`) with a reach-canonicalization and let the existing
dedup merge; the stage transition in `core/kink.h` already reads exactly
`N(b)`; the key fits the existing signature width because at most two blocks'
neighborhoods cover any row.

**Not established.** Whether the mid-column stage tables inherit the cut (the
congruence is proved at column boundaries only). What the telescope costs the
completion prune, which uses the boundary-row requirement; the counts above
have no `maxn` cap, so the 1.92× flag factor is an upper bound on what
telescoping is worth. Anything about wall clock: no engine change has been
written or timed. No closed form for `8, 19, 43, 101, 239, 575, 1399, 3441`:
no OEIS match, no constant-coefficient recurrence with surplus. For the
cancellation DP only the weaker statement holds: a merged-key automaton is an
alternative producer of its `C_H`, which does not mean its state admits the
same cut.

## 2. Re-slicing, recurrences, and finite-lattice inclusion–exclusion

### 2.1 The C-finite order of each slicing

Probe of 2026-07-02 (`experiments/recurrence_probe.py`, deleted in the
2026-08 tidy; readable with `git show 78602f8^:experiments/recurrence_probe.py`),
on the triangle through `n = 24` and the rows `H = 3..16` to `n = 25`. The
minimal constant-coefficient linear-recurrence order of a slicing measures
that direction's intrinsic complexity.

| diagonal `T(n, n−k)`, k | 0 | 1 | 2 | 3 | 4 and up |
|---|---|---|---|---|---|
| minimal order (root 3, all multiplicities) | 1 | 3 | 5 | 7 | ≥ 9, data-limited |

The order `2k+1` fits the full diagonal including its part below the onset.
The probe's first note inferred degree `2k` for `P_k` from it; the degree is
`k`, proved for `k ≤ 2` in `docs/proofs/diagonal-law.md` and recorded for
`k = 1..8` in `results/diagonal-formula.md`.

| row `T(n, H)`, H | 2 | 3 | 4 and up |
|---|---|---|---|
| minimal order | 3 | 7 | ≥ 11, data-limited |
| dominant root μ_H | 2.4142 = 1+√2 | 3.4437 | rising |

The diagonal is the low-complexity direction: order linear in `k`, against a
row order that outruns the data by `H = 4`. Extending the closed-form region
by one level costs one more coefficient; closed forms shave a fixed-width slab
off the top of each row and never collapse the bulk. Orders past about 11 are
lower bounds; slopes `s ≥ 2` were tested 2026-08-09 with nothing found
(`results/diagonal-formula.md`); a P-finite recurrence could be lower order
for the rows, untested.

**No 2D holonomic accelerator.** A joint relation
`Σ c[i,j,d,e] n^d H^e T(n−i, H−j) = 0`, fitted on `n ≤ maxn − 2` and required
to verify on the withheld largest-`n` entries mod `p`, does not exist up to
shifts `(4,3)` and coefficient degrees 3 in `n` and 2 in `H`
(`holonomic2d_probe.py`, deleted with the probe above). The 1-D slices are
each holonomic; they do not knit into a joint D-finite structure, so the
diagonal closed forms are essentially all of the recurrence family.

### 2.2 The finite-lattice method does not stack

2026-07-10, from recorded data. Jensen's finite-lattice method counts a plane
series by inclusion–exclusion over `W × L` rectangles, each by a column
transfer; its exponential lever is the bounding-box inequality
`H + W ≤ n + 1`, so the paid dimension is `min(H, W) ≤ n/2`. The engine
already caps the processed dimension at `n/2` by transpose symmetry
`B_{H,W} = B_{W,H}` (a height-`W` run enumerates all widths at once, so
heights `1 … ⌈n/2⌉` fill the whole bounding-box matrix; the a(36) run stops
at `H = 18, 19`), and the diagonal formula pushes the highest run height below
`n/2`. The hard floor for both methods is the square animal `H ≈ W ≈ n/2`.
Polyplets of 17 cells by shorter box side (`results/bbox_polyplets_n17_exact.txt`):

| min(H, W) | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|
| count at n = 17 | 3.63e11 | 8.97e11 | 1.25e12 (peak) | 9.16e11 | 3.39e11 |

Square-ish animals near `n/2` are numerous, not a tail. The method changes
the leading term by nothing and adds the signed rectangle passes. With
sections 1.1 and 2.1: a new axis, finite-lattice inclusion–exclusion, contour
compression and a holonomic recurrence are all measured or argued dead;
connectivity is global and does not compress, factor, or re-slice away.

### 2.3 Structure probes on the slope-2 slice

`experiments/band_structure.py` and `experiments/qholo_automatic.py`,
2026-08-09, on `S(H) = T(2H, H)`, `H = 1..20`, in the band the diagonal
formula does not cover. Each probe carries a control it must recognize and a
structureless control it must reject.

**p-adic valuations.** Mean `v_p(S(H))` against the generic expectation
`1/(p−1)`:

| sequence | v_2 mean | v_3 mean | v_5 mean | v_7 mean |
|---|---|---|---|---|
| generic expectation | 1.00 | 0.50 | 0.25 | 0.17 |
| slope-2 T(2H,H) | 0.50 | 0.60 | 0.15 | 0.00 |
| control: Catalan | 1.10 | 0.60 | 0.55 | 0.30 |
| control: s=1 k=2 (quadratic × 3^H) | 1.15 | 6.85 | 0.20 | 0.35 |

The control's 3-power grows linearly (0, 3, 0, 0, 0, 2, 4, 3, 5, 6, 6, 10, 9,
9, 11, 13, 12, 14, 15, 15). The slice shows nothing at any prime; `v_7 = 0`
throughout has `P = (6/7)^20 = 0.046` for one prime and four were tested. The
structureless control was built as `round(41.85^H H^−0.25)` in floating
point, so its `v_2` mean of 16 is a float artifact; that row is not a valid
null.

**Hankel determinants.** `det[S(i+j)]_{0..m−1}` computed exactly; a
sequence with a Stieltjes or J-fraction has tiny or smooth ones.

| m | slope-2 det digits | cofactor digits after removing primes < 10^4 | structureless control |
|---|---|---|---|
| 3 | 7 | 1 (smooth) | 11 → 1 |
| 5 | 21 | 15 | 28 → 24 |
| 7 | 45 | 43 | 54 → 51 |
| 9 | 76 | 75 | 87 → 83 |

Catalan returns `det = 1` at every `m`. The slice has no J-fraction and no
Stieltjes moment structure. The s=1 k=2 control's determinants vanish from
`m = 6` on, the fingerprint of its order-5 recurrence; the slope-2
determinants are nonzero through `m = 9`, which proves its minimal C-finite
order is at least 9.

**Finite-size scaling of μ_H.** The certified strip constants `H = 2..17`
(`results/growth-constant.md`) fitted to `μ_H = λ − c H^−x` on `H = 6..15`,
tested on `H = 16, 17`; `λ = 7.110(1)` is known independently.

| λ | x | c | max relative error on H = 16, 17 |
|---|---|---|---|
| 7.108 (fixed) | 1.2043 | 17.63 | 0.303% |
| 7.110 (fixed) | 1.2021 | 17.58 | 0.300% |
| 7.112 (fixed) | 1.2000 | 17.52 | 0.297% |
| free | 1.0017 | 13.44 | 0.010% at λ = 7.334 |

On synthetic data from the model (`x = 1`, `c = 9`) the fit returns
`x = 1.0000` with zero error. Letting `λ` float buys a 30× better test
residual and returns a `λ` 3% from a value known to one part in 7,000. With
`λ` fixed the residual is 0.3%, so the pure power-law correction is not the
right form. Reading: `x ≈ 1.2` at fixed `λ`, neither `x = 1` nor `x = 3/2`
excluded, and no conclusion about `λ` from this route.

**q-holonomic recurrences.** A global factor `q^H` is invisible to C-finite
and P-finite searches by design (it rescales `c_i` by `q^−i`), so "`3^H`
times something P-finite" was already covered. The gap is `q^H` inside the
coefficients: `Σ_i c_i(H, q^H) S(H−i) = 0`, searched with `q ∈ {2, 3, 5}`,
`r ≤ 3`, degrees in `H` and `q^H` bounded by the slack rule, onsets `0..3`,
last two points held out. The control `S(H+1) = (2^H + 1) S(H)` is found
(`q = 2`, `r = 1`, `d = 0`, `B = 1`); the s=1 k=2 control is found with
`B = 0`; the slice: none. Envelope from 20 points: `r = 1` permits
`(d+1)(B+1) ≤ 7`; `r = 2` permits `≤ 4`; `r = 3` permits `≤ 3`.

**Residues mod m.** `S(H) mod m` for `m = 2, 3, 4, 5, 7, 8, 9, 11`, asking for
eventual periodicity with period `≤ 6` from index 8. The s=1 k=2 control
fires (period 4 mod 2; identically 0 mod 3 and 9 from index 5). The slice: no
short period at any modulus. The Catalan control also returns none, yet
Catalan mod 2 is 2-automatic (nonzero exactly at `n = 2^k − 1`), so this
detects periodicity, not automaticity; deciding automaticity needs far more
than 20 terms, and the question cannot be closed on recorded data.

The slice carries no detectable arithmetic or determinantal structure, and
the two exact-integer tests cannot be talked into a positive by a good fit.

### 2.4 P-recurrence and algebraic exclusion boxes for A006770

`build/prec_guess` (`cpp/prec_guess.cpp`) on the 40 recorded terms
(`results/b006770_upload.txt`), prime `2^61 − 1`, 2026-08-05. `prec` tests
`Σ_{i=0..J} p_i(n) a(n+i) = 0` with `deg p_i ≤ D`; `alg` tests
`Σ_{j=0..K} q_j(t) F(t)^j = 0` with `deg q_j ≤ L`. Boxes nest, so excluding
the maximal box excludes every box inside it. Full column rank mod `p` is a
proof over `Q`: some maximal minor is nonzero mod `p`, hence over `Q`. A rank
defect mod `p` would be only a candidate; none occurred.

| box (J,D) or (K,L) | `prec` | `alg` |
|---|---|---|
| (4,5) | EXCLUDED | EXCLUDED |
| (5,4) | EXCLUDED | EXCLUDED |
| (4,6) | EXCLUDED | EXCLUDED |
| (3,7) | EXCLUDED | EXCLUDED |
| (3,8) | EXCLUDED | EXCLUDED |
| (2,11) | EXCLUDED | EXCLUDED |
| (6,3) | EXCLUDED | EXCLUDED |
| (7,3) | EXCLUDED | EXCLUDED |
| (5,5) | INCONCLUSIVE (35 rows ≤ 36 unknowns) | EXCLUDED |
| (6,4) | INCONCLUSIVE (34 rows ≤ 35 unknowns) | — |

These exclude a small P-recurrence or algebraic relation; they are not a
non-D-finiteness proof. The unconditional theorem in
`results/anisotropic-not-dfinite.md` concerns the two-variable by-height
generating function; the ordinary (isotropic) generating function being
non-D-finite remains a conjecture, and these boxes are a data point
consistent with it.

## 3. Handles on connectivity other than a partition

The four mechanisms of 3.1, 3.2, 3.5 and 3.6 were generated on 2026-08-20 in
a deliberate search for something that leverages a property of animals or of
the lattice other than height; all closed by counting.

### 3.1 The determinant handle

For a set `S`, let `L_S` be the Laplacian of its induced king-subgraph;
`det(L_S + ε I)` vanishes to order exactly the number of components, and the
coefficient of `ε^1` is `n · τ(S)` when `S` is connected and zero otherwise,
`τ` the spanning-tree count. Orders of vanishing compose under gluing in a way
partitions do not. The output is weighted by `τ(S)`, and no commutative edge
weighting divides the weight out: a single edge forces every weight to 1, and
a triangle (present on the king lattice) then gives `τ = 3`. Characteristic 3
sends 3 to 0; characteristic 2 sends it to 1 but the `2 × 2` block is `K_4`
with `τ = 16 = 0`. A determinant counts every spanning tree democratically,
and connectivity needs one representative per set; choosing one is a
canonical-order choice, which is what Redelmeier's enumeration already is.
Weights in `{0, 1}` give an exact indicator of connectivity through a fixed
sublattice, which closes on locality (3.8). Summed over `S`, the construction
counts lattice trees on the king lattice, a different functional and not
easier.

### 3.2 Blocking and inflation

Map each cell to the `2 × 2` block containing it. Blocking preserves
king-connectivity exactly (floor-division by 2 moves each coordinate by at
most 1), the blocked lattice is the king lattice again, and a block is a
king-clique, so the fine set is connected iff the contact graph on blocks is.
The contact rule is local (east-west contact needs the facing columns
nonempty; diagonal contact needs the two facing corners), so the fine geometry
collapses into a 15-letter alphabet, the nonempty subsets of a block, plus a
per-edge rule. Inflation, the inverse, has 15 options per cell (the empty
subset excluded) and not every choice stays connected: two adjacent coarse
cells filled with their outer columns only leave fine cells three columns
apart.

The correspondence
`a(n) = Σ_{coarse A} #{fillings of A totaling n cells with connected contact graph}`
is exact, a bijection, and a restatement: the coarse animal has between `n/4`
and `n` cells, so `a(n)` appears on its own right-hand side (the `m = n` term
is one cell per block, four choices each), and the fiber is the same problem
one scale down. Dropping the contact constraint gives
`A(x) ≤ A((1+x)^4 − 1)` coefficientwise, whose consequence for `λ`,
`u ≤ 4u + 6u² + 4u³ + u⁴`, holds for every positive `u`. The clique gift is a
level-1 accident: `4 × 4` blocks are not cliques, and their internal linkage
regenerates the partition state. Fillings where contact is automatic give
injections, hence concatenation-style lower bounds on `λ`, which is where the
certified 6.543 already comes from (`results/growth-constant.md`).

### 3.3 The fattening bijection

The route: fatten each king cell `(x, y)` to the block
`{2x, 2x+1} × {2y, 2y+1}`, fill a marked corner cell at each pinch, and apply
polyomino contour technology to the image class verbatim.
`experiments/skeletonkey/l3_3_fattening.py`, ayr, 2026-08-20, over every
polyplet to `n = 8` (176,138, gated against A006770). A grid corner pinches
when exactly one diagonal pair of the four cells meeting there is in the
animal; the two absent cells are the candidate blocks for a filler.

| convention | pinch-free | full-block decode | injective |
|---|---|---|---|
| `none` (control: fill nothing) | NO, first at n = 2 | — | yes |
| `lex` (filler to the lex-smaller candidate block) | YES | recovers every animal | YES |
| `lexmax` | YES | recovers every animal | YES |
| `both` (fill both candidates) | NO, first at n = 6 | FAILS at n = 4 | yes |

`both` fails on the diamond `{(0,1), (1,0), (1,2), (2,1)}`: all four pinches
fill the empty center block and the image becomes the plus-pentomino's. `lex`
is injective for a reason: block `(x, y)` owns refined cell `(2x, 2y)` at grid
corner `(x, y)`, the candidates there are `(x−1, y−1)` and `(x, y)`, and the
block itself is the lex-larger, so no block wins the mark at its own
bottom-left corner and full blocks are exactly the animal. The map is a
bijection onto a class of pinch-free, edge-bounded polyominoes with a
linear-time inverse.

The working construction buys nothing. The map is local, so counting the
image class is counting polyplets with a local recoding between, and
class-agnostic machinery pays for a lattice of twice the height:

    king column      H = 21   Motzkin(22) − 1 =             400,763,222
    refined column   h = 42   Motzkin(43) − 1 = 1,614,282,136,160,911,721

a factor of `4.0e9`; the way back down is to re-impose the block alignment,
which is the king transfer matrix in refined coordinates. An `n`-cell
polyplet's image has `4n` cells before marks, so a(40) would be carried by
polyominoes of at least 160 cells against a literature record of 70 by area
(`docs/publication.md`). Not settled: whether the fattened boundary is the
perimeter the matching-pair convention of section 4 means; injectivity is
proved for `lex` and only measured for `lexmax`; the image class's own cut
rank was not measured.

### 3.4 The dual-connectivity transfer matrix

The route: track the complement's 4-connectivity (planar, hence
non-crossing) and recover components from `C = χ + holes`. The
doomed-configuration prune forces the component count to be carried, and the
per-block-pattern state cost is `b · Cat(b)` against the engine's `Cat(b)`
(`experiments/dual_connectivity_blockcount.py`, 2026-08-22, five controls).
The ratio is exactly `b` at every block count; the dual ties at `b ≤ 1`,
0.0001% of the frontier at `H = 21`, and wins nowhere. The campaign record
(`docs/lastditch-campaign.md`) states the kill as `b · Cat(b)` against
`Bell(b)`, 11,440 against 4,140 at `b = 8`; the engine pays `Cat(b) = 1,430`
per pattern, not `Bell(b)`, and the true factor at `b = 8` is 8. That
`Cat(b)` is the engine's per-pattern cost follows from
`Σ_b C(H+1, 2b) · Cat(b) = Motzkin(H+1)` reproducing the recorded `H = 21`
column count 400,763,222 exactly, an inference from the aggregate rather than
a reading of the engine.

Binary strings of length `H` with exactly `b` maximal runs number
`C(H+1, 2b)`. At `H = 21`:

| b | patterns | Cat(b) | engine states | dual states | ratio |
|---|---|---|---|---|---|
| 3 | 74,613 | 5 | 373,065 | 1,119,195 | 3× |
| 5 | 646,646 | 42 | 27,159,132 | 135,795,660 | 5× |
| 6 | 646,646 | 132 | 85,357,272 | 512,143,632 | 6× |
| 7 | 319,770 | 429 | 137,181,330 | 960,269,310 | 7× |
| 8 | 74,613 | 1,430 | 106,696,590 | 853,572,720 | 8× |
| 9 | 7,315 | 4,862 | 35,565,530 | 320,089,770 | 9× |

| b ≤ | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|
| cumulative share of the frontier | 0.10% | 1.21% | 7.99% | 29.29% | 63.52% | 90.14% | 99.02% |

Totals at `H = 21`, the empty pattern counted once in each:

    engine   Σ C·Cat(b)    =   400,763,223   ( = Motzkin(22) )
    dual     Σ C·b·Cat(b)  = 2,840,372,305   ( 7.1× )
    Bell     Σ C·Bell(b)   =   941,574,417   ( 2.3× )

The frontier sits at `b = 6..8`, about `H/3`, where the dual is 6–8× worse.
This counts states, not per-state work; the dual's inner loop carries a
component count the engine does not and has no reason to be cheaper. The
prune that forces the count to be carried is an independent argument,
untouched.

### 3.5 Relaxation hierarchies

**Cut families.** Connectivity is "no separating cut"; restrict the family
(forbid vertical cuts, then staircases with at most `k` turns), each level a
rigorous upper bound with less state. It does not interpolate: "every
adjacent column pair is linked" is satisfied by two parallel horizontal bars
ten rows apart, and every repair must remember which run connects to which,
which is the partition state.

**Runs per column.** Bound the maximal runs per column by `r`. A genuine
hierarchy: `r = 1` is column-convex (A187077, `results/subclasses.md`), every
level is a lower bound on `a(n)`, and the state is polynomial in the height.
Column-convex polyplets run 1, 4, 18, 83, 385 with ratios near 4.6 against
`λ = 7.12`; every fixed `r` has the same disease with a larger constant,
because bounding runs per column is a large-deviation restriction on a
typical animal. At `n = 60` the `r = 1` level is off by about eleven orders
of magnitude.

### 3.6 Exact bulk plus estimated tail

`experiments/skeletonkey/height_tail_extrapolation.py` on the per-height rows
of `results/ns_a40/perheight/`, seconds on ayr; its control is that
perturbing a row must move the quantile. Fitting the rows,
`<H> = 1.228 n^0.682` (against the extent exponent `ν → 0.6407`,
`results/growth-constant.md`). Exact quantiles of the height of an `n`-cell
polyplet:

| n | `<H>` | q0.5 | q0.9 | q0.99 | q0.999 |
|---|---|---|---|---|---|
| 20 | 9.46 | 9 | 12 | 15 | 17 |
| 30 | 12.48 | 12 | 16 | 20 | 22 |
| 40 | 15.17 | 15 | 20 | 24 | 27 |

At `n = 40` the run ceiling `H = 19` sits just under the 0.9 quantile and the
diagonal formula holds immediately above it. The same collapse at `n = 60`
gives `<H> = 20.0`, q0.5 = 19.8, q0.9 = 26.4, q0.99 = 31.7, and a formula
floor at `H = 29`: the untouched heights run from the median past the
ninetieth percentile, so there is no small remainder to estimate. The
collapse extrapolates quantiles, not tail shares: row 40 predicted from row
30 gives 14.6, 19.4, 24.3, 26.7, 29.2 against exact 15, 20, 24, 27, 29, while
the same prediction read as tail shares is off by 2 to 4 at the far end. Nor
is the bulk free: `results/fixed_height_gfs.txt` stops at `H = 11` with
recurrence orders 1, 3, 7, 15, 42, 106, 278, 711, 1897, 5005 through H = 10,
about 2.6 per height, and `H = 19` would need on the order of `1e7` terms.
(The banked H = 11 order, 13381, is not used here: that entry was refuted on
2026-09-05 as a CRT wraparound and the argument is refitted through H = 10 --
`results/diagonal-formula.md`, `results/anisotropic-not-dfinite.md`.) In general, covering all
but a vanishing part of the class needs `H_max ≈ 2 n^0.68` at cost about
`3^H_max`, against about `3^(n/2)` for the entire exact computation; those
cross near `n = 76`. Computing the bulk exactly and estimating the tail is
never cheaper than computing everything, at any `n` that could be run.

### 3.7 Combinations tried

All closed: the determinant as the bookkeeping blocking needs between scales
(dies with 3.1); the same in characteristic 2 (spanning trees mod 2 weight
animals by tree parity, which is not `a(n) mod 2`); blocking with the
cell-level rank (1.5); the hierarchies with the capture cause; and the
matching pair (section 4), which needs square-lattice data graded to order
about 200 in the percolation variable against a literature record of 70 by
area, totals only.

### 3.8 The four causes

Every closure above, and every closure elsewhere in this record, is one of:

1. **Locality.** No local grading separates connected from disconnected. The
   additive invariants a bounded-state run can carry are area, perimeter and
   Euler characteristic, and `χ = C − h` never separates its terms: an animal
   and a two-component set with one hole both have `χ = 1`. Isolating
   connectivity needs cancellation, whose floor is a color per frontier cell.
2. **Capture.** Any subclass defined by bounding a local complexity measure
   (runs per column, frontier components, box dimensions, convexity defects)
   has a strictly smaller growth constant, so what it captures decays
   geometrically in `n`; no such family gives a useful one-sided bound or an
   "exact bulk plus small correction" split.
3. **Bijection.** A re-encoding carries identical information and pays the
   same floor, however much machinery exists for the target class (3.2, 3.3).
4. **Exponent against constant.** Everything here is `c^n`. The engine is
   about `1.66^n` (2.25e8 reachable states at `H = 19` is 2.75 per height, and
   two heights buy one unit of `n`). Every asymptotically cleverer geometry
   (bulk-only runs, corner-transfer coarse-graining at `exp(boundary)` cost)
   has a better exponent and a worse constant, and loses in every range that
   can be run.

A breakthrough would have to be non-local, capture a constant share of the
class, not be a re-encoding, and improve the constant rather than the
exponent. Cause 2 rules out deterministic decompositions essentially by
definition; it does not apply to a sampler, whose coverage is not a
bounded-complexity class.

What is left holding a real number is the gap between the engine's frontier
and the Hankel floor. The 2026-08-20 note put that floor at
`Motzkin(H/2 + 1)`, 15,511 at `H = 21`, and priced closing it at moving the
base from about 1.66 to about 1.32 per unit of `n`, roughly twenty-five
terms; the measurement of 2026-08-21 (1.2) puts the floor at 3,016 already
at `H = 11`, growing 2.43 per height, and the record holds the measured one.
The obstruction: the compression exists at column granularity; an algorithm
must read one cell at a time; and the cell-level rank is `Θ(H · 2^H)` rather
than `2^H`.

### 3.9 The span cap in the family DP, indexed by final cluster

A per-level span cap (`2·ℓ + e` at intermediate level `ℓ`) is 9× faster, 5×
smaller, and undercounts: 333 against 339 at `(e, k) = (0, 2)`, `K = 9`. The
counterexample is `{0, 3}` over `{1, 2}`: connected, four cells, span 3, and
its first row alone spans 3 with two cells; a prefix's span is bounded by the
final cluster's cell count, not its own (`docs/lastditch-campaign.md`).

The honest variation (2026-08-22, desk arithmetic): run the DP once per
target cluster size `ℓ`, capping span at `2ℓ + e + 1` in that pass, exact by
the engine's own header argument. The measured cost (dalby, `emax = 4`,
`results/undertow.md`) is 12.2 s at `K = 8`, 71.4 s at `K = 10`, 265.0 s at
`K = 12`, a per-unit-`K` ratio `r = 2.159`, so the top level alone is
`1 − 1/r = 0.537` of a run. Pass `ℓ = K` computes level `K` at full span, as
the single run does now, so the best possible saving is
`1/(1 − 1/r) = 1.86×`, and on RAM nothing, since the peak state set is level
`K` at full span. Shapes of `t` cells with span `≤ s` number `C(s, t−1)`:

| cells per row | shapes at cap 47 | at cap 41 | ratio |
|---|---|---|---|
| 4 | 16,215 | 10,660 | 0.657 |
| 5 | 178,365 | 101,270 | 0.568 |
| 6 | 1,533,939 | 749,398 | 0.489 |
| 8 | 62,891,499 | 22,481,940 | 0.357 |

Those factors apply at low `ℓ`, where the work is small; at `ℓ = K` the ratio
is 1. Dead for the same structural reason as the original, by a cost argument
independent of the correctness one; only a cap that tightens the top level
would change it, which needs a different invariant. The motivating memory
pressure (depth 5 priced at 103 GB and more) did not exist: depth 5 measured
about 8.5 GB, 16.1 GB pessimistic (`results/undertow.md`).

## 4. The percolation matching pair

The king lattice is the matching lattice of `Z²` for site percolation, which
is why `p_c(square site) = 0.59275` and `p_c(king site) = 0.40725` sum to 1.
So A001168 and A006770 are the two halves of a matching pair, and the
Sykes–Essam identity relates their perimeter-refined counts.

**The convention.** `experiments/matching_pair_euler.py`, 2026-08-07, over
all 65,535 nonempty subsets `S` of a `4 × 4` box, with `V = |S|`, `E_4`/`E_8`
the adjacent pairs under rook/king, `Q` the `2 × 2` blocks inside `S`, `T` the
king 3-cliques, `C_a` the `a`-connected components of `S`, `H_a` the bounded
`a`-components of the complement:

    C_4(S) − H_8(S) == V − E_4 + Q          : 65535/65535 hold
    C_8(S) − H_4(S) == V − E_8 + T − Q      : 65535/65535 hold
    C_4 − H_4 == V − E_4 + Q                : 57144/65535
    C_8 − H_8 == V − E_8 + T − Q            : 57144/65535

The pairing is foreground `a`-connectivity against background
matching-`a`-connectivity. The perimeter is same-lattice: a set `C` is a
maximal `a`-connected cluster exactly when every site `a`-adjacent to `C` is
vacant, so its weight is `p^|C| q^(t_a(C))` with `t_a` the `a`-site
perimeter. The earlier idea note had this backwards; the Redelmeier
program's `--siteperim` (`cpp/g2_redelmeier.cpp`, checked against Mertens
1990 Table IVB) was already right. Per site there are 2 rook edge classes,
4 king edge classes, 1 block and 4 king triangles, so the Euler densities are
`p − 2p² + p⁴` and `p − 4p² + 4p³ − p⁴`, and with `K_a(x)` the mean number of
`a`-clusters per site at density `x`:

    K_8(p) − K_4(1 − p) = p − 4p² + 4p³ − p⁴

The Euler formulas are standard digital topology and the relation is
Sykes–Essam 1964; no novelty is claimed. The `4 × 4` census is evidence for a
local identity, not a proof; the density form assumes translation invariance;
nothing addresses `p ≥ p_c`.

**The relation, verified.** `experiments/matching_pair_series.py`,
2026-08-22, exact rational arithmetic: coefficients 1, −4, 4, −1, then exact
zero at orders 5 through 9. The first failing order is `p^10`, with residual
exactly `−6053180 = −A006770(10)`, the omitted king term. Controls: the
enumerator reproduces A001168 to `n = 11` and A006770 to `n = 9`; a single
cell has king perimeter 8 and rook perimeter 4; the cross-lattice convention
does not reproduce 1, −4, 4, −1.

**Why the perimeter-defect series cannot feed it.** The rook side
contributes at order `p^(t_4)`, so an order-`N` test needs every polyomino
with `t_4 ≤ N`, the smallest perimeters; the defect grading
(`results/perimeter.md`) is `k = pmax(n) − p`, the largest. Over every fixed
polyomino to `n = 11`:

| n | min t₄ | max t₄ | what `k ≤ 6` reaches |
|---|---|---|---|
| 5 | 8 | 12 | t ≥ 6 |
| 7 | 10 | 16 | t ≥ 10 |
| 9 | 11 | 20 | t ≥ 14 |
| 11 | 12 | 24 | t ≥ 18 |

The windows are disjoint from `n = 8` on: max `t₄` grows like `2n`, min `t₄`
like `3.67 √n` (measured over `n = 4..11`). A structural mismatch, not a cost.

| order | needs every polyomino with t₄ ≤ | sizes to about |
|---|---|---|
| p^10 | 10 | n = 7 |
| p^16 | 16 | n = 19 |
| p^20 | 20 | n = 29 |
| p^30 | 30 | n = 66 |

Quadratic in the order, against a king side that is linear. Order 20 means
every polyomino to about `n = 29` with its site perimeter, which this record
does not have. The identity constrains perimeter-refined counts, so it is not
a check on a(40) unless the perimeter refinement is pushed to `n = 40`.

## 5. Below the onset: two probes that did not yield the defect constants

Both 2026-08-09. The depth-1 defect was derived the same day by a different
route (`results/below-onset.md`), which supersedes 5.1 at depth 1.

### 5.1 The discarded terms

With `μ := 1/z*` and `G := E_b · E_t · u^(−1) = Σ_i g_i(y) z^i` in the
grand-form proof, `[z^H](F − P) = μ^(H+1) (Ĉ − ρ_H)`, `ρ_H := Σ_{i>H} g_i z*^i`,
so exactly

    T(H+k, H) = [y^k](C · μ^H)  −  [y^k](μ^(H+1) ρ_H)  +  [y^k][z^H] P

Two discarded terms, switched off above the onset by two facts:
`ord_y(ρ_H) ≥ H`, and `deg_z [y^k]P ≤ k`. Both cut in at `H ≤ k`, which is
why the onset is sharp and the same for both. From the Lean-verified cluster
weights at `k ≤ 3`:

| (k, H) | formula | ρ-term | P-term | defect |
|---|---|---|---|---|
| (2, 2) | | −10.04 | 13 | 2.96 |
| (3, 3) | 78923/81 ≈ 974.4 | 155.4 | 177 | 21.6 |

At `(3, 3)` the ρ-term alone is 7× the defect: the rate and amplitude live in
the cancellation, and an asymptotic for `g_i` alone overshoots. At depth `j`,
extracting `[y^k]` from `ρ_H` reaches `j − 1` orders past its valuation,
predicting `θ_j − θ_1 = j − 1`, consistent with the measured `θ_j = j − 3/2`
at depths 1..7 (`results/below-onset.md`), but a retrodiction resting on an
asserted step. The cluster weights are Lean-verified only to `j ≤ 3`, which
cannot give an asymptotic in `i`. Untested route: `P_1 … P_19` determine
`a_j, b_j` to `j = 19` (`experiments/grand_form_saddle.py`), and if the
proof's Lagrange map inverts, `μ(y)` and `z*(y)` follow to order 19 without
new weights, leaving the edge series `E_b, E_t` unrecovered.

### 5.2 The strip spectrum

`experiments/spectral_edge.py`. The question was whether the row-transfer
operator shows a continuum edge at `9 = 3²`. On the depth-`j` line
`n = 2k+1−j`, `9^k = 3^(n+j−1)`, so per cell the defect rate is 3, the
thin-diagonal rate, and 9 exceeds every `μ_H` (they climb to `λ = 7.11`), so
no eigenvalue could sit there. The spectrum is the reciprocal roots of `Q_H`
in `results/fixed_height_gfs.txt`.

| H | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| order | 3 | 7 | 15 | 42 | 106 | 278 | 711 |
| dominant root | 2.414214 | 3.443718 | 4.182321 | 4.717801 | 5.115324 | 5.417609 | 13.666 |

Exact at `H = 2, 3` (`1 + √2`, `3.4437`), monotone through `H = 7`; at `H = 8`
float root-finding on a degree-711 polynomial breaks (13.67 exceeds `λ`), so
the usable range is `H ≤ 7`.

| band | 2.5–2.9 | 2.9–3.1 | 3.1–3.5 |
|---|---|---|---|
| H = 5 (42 roots) | 0 | 0 | 1 |
| H = 6 (106) | 2 | 0 | 0 |
| H = 7 (278) | 4 | 0 | 2 |

Zero eigenvalues within 2% of 3 at every `H ≤ 7`, and `Q_H(1/3) ≠ 0` for all
`H ≤ 8` in rationals. The strip operator governs growth at fixed `H`, while
the defect lives on lines where `n` and `H` grow together; it is probably the
wrong object regardless of range. What survives is the framing
`D_j(k) ≈ C_j · 3^(j−1) · 3^n · k^(j−3/2)`: the formula's error at fixed depth
is the count of thin animals times a power of `k`.

## 6. The master equation is lattice-parametric

Not a closed door. The one piece of the diagonal-formula machinery that
`docs/proofs/universal-diagonal-law.md` left king-only, assembling `c_k` for
`k ≥ 2` from the cluster weights, is one substitution
(`experiments/skeletonkey/parametric_master.py`, 2026-08-20).

The renewal chain is `1 = 3z + Σ_c W_c y^k z^(l+1)` at `z = 1/μ`. The 3 is
the drift-step weight, the number of continuations of a one-cell row, which
for a row-local lattice with drift set `D` is `b = |D|`. With `μ = b·H` and
`u = y·μ/b³`:

    H(u) = 1 + Σ_c Ŵ_c u^(k_c) H^(−(k_c + l_c)),     Ŵ_c = W_c · b^(2k_c − l_c − 1)

and since `F(n,u) = C(u) · H(u)^n`, the cumulant slopes are
`A_k = [u^k] log H`. `cluster_weight(D, sizes)` in `experiments/gas_cumulants.py`
is already parametric. The `A_k` in the universal-law proof came from a
drift-parametric dynamic program over the triangle; this route reaches them
from the weights alone, sharing no code path.

| lattice | b | Ŵ inputs | `log H` | recorded slopes |
|---|---|---|---|---|
| square | 1 | 4, 9, 12, … | `4u − 19u² + (472/3)u³` | 4, −19, 472/3 |
| hex | 2 | 9, 64, 120, … | `9u − (37/2)u²` | 9, −37/2 |
| king | 3 | 25, 441, 1017, … | `25u − (209/2)u² + (4474/3)u³` | 25, −209/2 |

King `4474/3` at `k = 3` was a prediction, checked against the coefficient
table: with `P_1 = 25n − 45`, `P_2 = (625n² − 2459n + 1134)/2`,
`P_3 = (15625n³ − 100050n² + 122213n − 32940)/6`, the cumulant
`c_3 = P_3 − P_1 P_2 + P_1³/3` has vanishing `n³` and `n²` coefficients and
`n` coefficient `8948/6 = 4474/3`. Gates: weights must match the recorded
table on all three lattices; every `A_k` must match; bumping `W(2,2)` from 12
to 13 moves the square slopes to `4, −18, 388/3, −1014`.

**The `k = 4` run (2026-08-20).** From the weights alone, king
`A_k = 25, −209/2, 4474/3, −22701/4`; the fourth is the coefficient table's
number to the fraction. The four-row clusters cost: `(2,2,2,2) = 68314` took
6,621 s; `(2,3,2) = 18308`; `(2,2,3) = (3,2,2) = 13459`.

**The two constants per level, king, from the coefficient table to k = 19**
(`--wired-only`, under a second):

| k | A_k | B_k |
|---|---|---|
| 1 | 25 | −45 |
| 2 | −209/2 | −891/2 |
| 3 | 4474/3 | −10350 |
| 4 | −22701/4 | −846963/4 |
| 5 | 16144 | −3781134 |
| 6 | 15126941/3 | −119091015 |
| 7 | −687296991/7 | −14478715359/7 |
| 8 | 16995497259/8 | −422154856107/8 |
| 9 | −74756868461/9 | −1487291768649 |
| 10 | 987107242503/5 | −157865366062953/5 |
| 11 | −167395577383614/11 | −5691866601417228/11 |
| 12 | 2763085221702553/2 | −70608382970548959/2 |
| 13 | −720698320820505951/13 | 725307892812247635/13 |
| 14 | 23806059560272857169/14 | −336304442725786678509/14 |
| 15 | −493233295413187159171/15 | −211243195829544461505 |
| 16 | 4737043349049134006715/16 | −48607562060310698638155/16 |
| 17 | 166978491890346163441779/17 | −7614668303432519358253869/17 |
| 18 | −8798698594866651300807629/18 | 1842210899412762378532347/2 |
| 19 | 215000982004527315731741127/19 | −3197921036512955745255968241/19 |

`k · A_k` is an integer at all nineteen orders. The sign alternates except
between `k = 5, 6` and `k = 16, 17`; no explanation is offered. `c_k` is
generically of degree `k` in `n`, so linearity requires `k − 1` vanishing
coefficients at each order, 171 in all, and all 171 hold: a consistency
check between extensivity (a consequence of the proved grand form) and a
table fitted from enumerated entries. Adding 1 to `P_19`'s `n²` coefficient
breaks linearity; a perturbation of a `P_k`'s constant or `n¹` term never
can, so the audit fixes the `n² … n^k` coefficients of each `P_k` and says
nothing about the other two.

**Hex `A_4` by a second route (2026-09-05).** `experiments/hex_diag_deep.py`
generates `T_hex(n, n−k)` for `k ≤ 6`, `H ≤ 20`, in 19 s
(`results/hex_diagonal_cells.txt`); fitting `T_hex(n, n−k) = P_k(n) · 2^(n−1−3k)`
gives `P_1 … P_6` with 72 entries outside the fit all exact, and linear
cumulants:

| k | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| hex `A_k` | 9 | −37/2 | 32 | 3915/4 | −103671/5 | 968878/3 |

`3915/4` is the weights-route number to the fraction, by a route sharing no
code. `A_5` and `A_6` are targets the weights route has not been run against.

**The depth-1 defect is parametric too (2026-09-05).**
`experiments/depth1_parametric.py`, with the drift set `D` as parameter
(square `{0}`, hex `{−1, 0}`, king `{−1, 0, 1}`). The gap walk's generic row
is counting: a new pair at gap `gp` far from the old pair has
`2|D ∪ (D − gp)|` placements, `2|D ∩ (D − gp)|` of which leave the pair joined,
and near the old gap the autocorrelation weight `k_d` of `D` moves `2k_d`
from class P and adds `k_d` to J. So the bulk block is the autocorrelation of
`D`, `u^(b−1) − y(1 + u + … + u^(b−1))²`, and the only non-template rows are
the gaps `g < b`: two for king, one for hex, none for square. The assembly
identity is `D_1(k) = [y^k](P̂ − B²/(b + S))`, `b` where the king note has 3.

Square, derived: with `b = 1` the walk closes on two states,
`S = 4y/(1−3y)`, `B = (1−y)/(1−3y)`, `P̂ = y/(1−3y)`, so `F_1 = −1/(1+y)` and
`D_1(k) = (−1)^(k+1)` for all `k ≥ 1`, previously measured at `k ≤ 6`
(`results/undertow.md`). Hex, derived: the block `u − y(1+u)²` has one small
root `u₁ = (1−A)/(1+A)`, `A = √(1−4y)`, and `F_1` is quadratic over `Q(y)`
where king's is quartic. In the king normalization `y = bx`,
`N = b·F_1(bx) + 1`:

    Φ_hex(x, W) = (8x−1)(8x²−9x+3) W² − (2x−1)(8x−1) W + x

with branch point `x = 1/8 = 1/b³` against king's `1/27`.
`N_k = 2^(k+1) D_1(k)` is integral: 1, 7, 45, 303, 2133, 15447, 113869, …,
not in OEIS as of 2026-09-05, annihilated by `Φ_hex` through `x^25`.

Hex onset sharpness, proved: `Φ_hex ≡ (W+1)((1+x)W + x)` in `F_2[x, W]`;
`F_2[[x]]` is a domain, `N(0) = 0` kills the first factor, so `(1+x) N̄ = x`
and `N_k` is odd for every `k ≥ 1`, hence `D_1(k) ≠ 0` and the hex onset
`n ≥ 2k+1` is sharp, by the same argument as the king mod-3 proof. On the
square lattice `N(x) = x/(1+x)` outright, which is what both reduce to mod
`b`. Checked: the parametric walk reproduces `experiments/depth1_gap_walk.py`
for king at `k ≤ 20`; the square closed form against the walk to `k = 25`;
the hex closed form against the walk to `k = 25` and against
`T_hex(2k, k) − P_k(2k)/2^(k+1)` at `k ≤ 6`. Controls: `b → b+1` breaks all
three lattices, a perturbed `N_3` is not annihilated, a non-interval `D` is
refused.

**Not established.** `B_k` from the weights: only the slopes come from
`log H`, the constants need `C(u)`, and the `B_k` above come from the
coefficient table, king only, with no cross-route agreement. Depth `j ≥ 2` on
any lattice but king: the family DP is a different machine from the gap walk
and is king-only; the square targets `−4, 8, −3, 10, −1` (`results/undertow.md`)
are unclaimed. Hex `A_5, A_6` await a `K = 5` weights run. Validating the
below-onset machinery against published square counts is not free: the
formula covers `H ≥ (n+1)/2`, the rest of each row must be enumerated, so
`n = 56` needs square entries at `H ≤ 28`.

## 7. Converse checks on the universal claims

`experiments/converse_sweep.py`, 2026-07-31, under five seconds, exact
arithmetic, `P_k` re-derived by Lagrange interpolation from
`results/triangle.txt` with an assertion on every other in-range entry. For
each believed-but-unproved universal statement, try to refute it with one
exact witness.

**Onset sharpness.** For every `k = 1..13` the formula value at `n = 2k` is
not an integer (`P_k(2k)` is not divisible by `3^(k+1)`), so no accidental
extension exists; `k = 13` is the interpolation ceiling at `n ≤ 40`. The
onset is now proved sharp for every `k` (`docs/proofs/diagonal-law.md`).

**"Denominator exactly k!" is false from k = 5.** `k! · P_k ∈ Z[n]` stands.
The minimal common denominator `D_k` of `P_k`'s monomial coefficients:

| k | 1–4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k!/D_k | 1 | 5 | 5 | 5 | 5 | 5 | 5 | 25 | 5 | 5 | 5 | 25 | 25 | 25 | 25 |

Two independent sources agree on every shared level: Lagrange interpolation
(`k ≤ 13`) and the production numerators in `polyplets/pin-data.md`
(`k ≤ 18`). It is forced: the leading coefficient `25^k/k!` is proved
(`lead_coeff_25` in Lean) and its lowest-terms denominator has no factor of
5, so minimality was incompatible with it from the first `k` with `5 | k!`.
Only powers of 5 drop. The law for the dropped power,
`c_k = v₅(k!) − H(k)` with `H(k) = v₅(⌊k/2⌋!) − [k ≡ 1 (mod 10)]`, exact at
`k = 1..19` (`results/arithmetic-structure.md`), was resolved the same day and
then demoted: the minimal denominator is a property of the monomial-basis
representation of an integer-valued polynomial and is load-bearing nowhere.
The retained claim is `k! · P_k ∈ Z[n]` plus "minimality is false".

**Log-convexity witnesses.** A006770 (fixed): no violation in 40 terms.
A030222 (free): violated at `n = 4` only. A030233 (one-sided): `n = 4` only.
A030235 (asymmetric): `n = 3, 4, 6`. A194596: `n = 2, 4`. A030234
(bilateral): every even `n` through 30 (two interleaved families,
`results/symmetry-classes.md`). The ratio sequence `a(n)/a(n−1)` is not
log-convex for any member: the fixed count's ratios are log-concave at every
index, while free, one-sided, asymmetric and A194596 show an even-`n`-only
violation pattern up to `n ≈ 10–12` before becoming log-concave, the
bilateral parity signature leaking into the ratio domain of sequences that
are not parity-broken. Unexplained; an observation.

**Not quickly testable.** The moat bound, peeling lemma and multi-hole
inequality past `n = 9` (compute-bounded); `ψ₉/ψ₁₀` irreducibility (one prime
with irreducible reduction would prove it); the mod-27 depth and `θ = −1`.
The diagonal-mirror boundary values `N_k(±1) = (±2)^k` reduce to
leading-coefficient statements (`docs/proofs/dm-diagonal-law.md`).

## 8. Ideas not taken, and what was measured before they were set aside

From the idea notes of 2026-08-03 and 2026-08-04; novelty was unchecked on
every item and the cost estimates there were growth-rate arithmetic.

- **Burnside run backwards.** `D4` orbit sizes divide 8, so
  `a(n) = n1 + 2 n2 + 4 n4 + 8 n8`, and `n1` (full `D4` symmetry) forces
  `n ≡ 0, 1 (mod 4)`, hence `a(n)` is even whenever `n ≡ 2, 3 (mod 4)`.
  Measured (`experiments/orbit_parity_probe.py`): `a(n)` is odd exactly at
  `n = 1, 8, 17, 21, 24, 25, 28, 29, 40`; A001168 is odd at
  `n = 1, 4, 5, 8, 12, 16, 21, 25`. `D2ax = {e, h, v, r180}` is the
  height-preserving subgroup, so `T(n,H) ≡ I_H(D2ax) (mod 2)`, one bit per
  entry. Executed as the subgroup census (`results/symmetry-classes.md`). The
  subgroup-invariant counts are not the per-element `Fix(g)` Burnside needs,
  so nothing here moves the five companion sequences stranded at `n = 32–34`
  by the diagonal-mirror count. Berlekamp–Massey on the 40 terms mod
  `2, 3, 5, 7, 11, 13` (`experiments/modp_bm_probe.py`) finds order about
  `n/2` in every case: no C-finite structure mod any small prime, which
  neither rules out nor supports algebraicity.
- **The matching pair.** Section 4. No sentence in the paper gets shorter.
- **A bridge-credit upper bound on λ.** Closed 2026-08-07
  (`experiments/band_charge_probe.py`, `results/growth-constant.md`): the
  band encoding is not injective, and assuming its alignment factor is 1
  gives `λ ≤ μ_H`, against the certified `μ_17 = 6.543 < λ`.
- **A λ atlas over row-local lattices** (square, hex, king, and a spread
  coordination-8 set with few triangles): is `λ` a function of coordination
  number or of local cycle structure? Prediction before measuring: spread-8
  lands above king's 7.11, toward the tree bound `(q−1)^(q−1)/(q−2)^(q−2)`
  (`experiments/lambda_atlas_probe.py`).
- **What a typical polyplet looks like**: a local weak limit of the
  neighborhood of a random cell; whether rescaled occupancy has a limit shape
  (it should not). Blocked on the absence of a uniform sampler past
  enumeration scale.
- **Universality.** Lattice animals are conjecturally in the Yang–Lee edge
  class in `d − 2` dimensions, the origin of `θ = −1`. The central-charge fit
  to the strip constants is closed: the approach to `λ` is not analytic in
  `1/H` at `H ≤ 17`, the surface term still falling at `H = 17` with
  increments shrinking about 6.5% per height where `1/H²` demands about
  11.4% (`results/growth-constant.md`). Whether the king lattice is in the
  same class as the square lattice is open (`experiments/theta_universality.py`).
- **Extremal questions.** Minimum site perimeter is closed: the data hit
  A235382 = A027709(n) + 4 on every measured term and the closed form is
  published (`results/perimeter.md`). Diameter, articulation points and hole
  count at fixed `n` are untouched (`experiments/king_extremal.py`).
- **The move graph.** Single-cell moves preserving connectivity give one
  component at every `n ≤ 10`, and no animal with `n ≥ 2` is stuck
  (`results/subclasses.md`); mixing, the second gate for a sampler, is
  unmeasured.
- **Inverse and decision problems.** Reconstruction from row and column sums
  (NP-hard for general polyominoes, polynomial for hv-convex ones; citations
  unverified); realizability of a property vector at size `n`.
- **Tiling, and the point-contact convention.** Which polyplets tile the
  plane, rep-tiles, Heesch numbers. Worth more than the tiling questions: a
  polyplet realized as a closed region joins at points, so "tile", "hole",
  "boundary" and "simply connected" are convention-dependent in a way the
  square lattice hides. If a published king-lattice number ever disagrees with
  this record, look there first.
- **The stretched-exponential refit** was done: `μ_1 → 1.0068` against a
  calibrated 1% resolving power, `θ → −0.981` as a by-product
  (`results/growth-constant.md`).

## Open problems

- **Strict log-convexity of A006770**: `a(n)² < a(n−1) a(n+1)` for `n ≥ 3`,
  zero violations at `n ≤ 40`; if proved, each ratio is a lower bound on `λ`
  (`a(40)/a(39) = 6.935 ≤ λ`). The margin `a(n−1)a(n+1)/a(n)² − 1` tracks
  `−θ/n²` (`n² ·` margin climbs from 0.89 to 0.97 over `n = 5..39`), so a
  refuting term would contradict the whole smooth-asymptotics picture and has
  no finite-certificate route short of a term past a(40). Liu–Wang 2007
  (`literature/liu_wang_2007_log_convexity_combinatorial_sequences.pdf`) has two
  kinds of tool, closure operations on already-log-convex sequences and
  three-term recurrences, and `a(n)` has neither; the concatenation arguments
  give quasi-supermultiplicativity, a different inequality. Never attempted:
  total positivity of the transfer matrix, or an injection
  `A_{n−1} × A_{n+1} → A_n × A_n`, none known for lattice animals.
- **Ratio log-concavity, theorem.** `r(n) = a(n)/a(n−1)` satisfies
  `r(n)² > r(n−1) r(n+1)` for all `n = 3..39` in exact arithmetic; the witness
  at `n = 3` is `20³ · 1 = 8000 > 7040 = 4³ · 110` on Lean-proved terms
  (`ratio_not_logConvex`). The picture is `r(n) ≈ λ(1 − 1/n)`; the all-`n`
  statement is conjectural.
- **The diagonal-mirror numerators** `N_k(±1) = (±2)^k`: verified at
  `k = 1..5`, reduced to leading-coefficient statements; `k = 6` needs
  `d(27,33)` and `d(29,35)`, the diagonal-mirror wall at `n = 33, 35`
  (`results/symmetry-classes.md`).
- **The Smith normal form of the triangle** is a 3-group (proved: `T_N` is
  lower-triangular with `det = 3^(N(N−1)/2)`), and the count of nontrivial
  factors `⌈(N−1)/3⌉` is a theorem via the mod-3 cubic; the individual
  exponents have no formula (`results/arithmetic-structure.md`).
- **The new-root degrees** 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289 have no
  low-order constant-coefficient recurrence; the "ratios drift to about 2.65"
  reading is retired as a trend on ten terms of a sequence that cannot be
  extended. The degrees stay, as the irreducibility certificates behind
  `results/anisotropic-not-dfinite.md`.
- **The growth law of the Hankel floor** (1.2): 2.43 is a fit over eight
  points, the quotients still wander, and `H = 12` costs about 17 days
  single-core.
- **An explicit char-2 basis** for the column-level collapse, the largest
  open technical question behind any compressed transfer (1.2–1.5).
- **Whether mid-column stage tables inherit the reach-merge cut**, and its
  cost against the completion prune (1.6).
- **Isotropic non-D-finiteness** of the ordinary generating function (2.4).
- **Automaticity of the slope-2 slice** mod small primes (2.3), undecidable
  on 20 terms; and the Klazar resonance (P-recursive mod `2^k` with no
  P-recursive parent) against the mod-3 structure, on which the
  Berlekamp–Massey probe is a question, not a lead.
- **The universality class** of the king lattice against the square lattice
  (section 8).
- **The below-onset constants at depth `j ≥ 2`** from the cancellation of the
  two discarded terms (5.1); depth 1 is derived (`results/below-onset.md`).
- **Depth `j ≥ 2` and `B_k` on lattices other than king** (section 6).

## What would move them: the resource asks of 2026-08-04

None was authorized or costed beyond the figures quoted.

- **Correspondence.** Gill Barequet, one question: is it known that
  finite-type convolution bounds cannot reach `λ`? The slack audit
  (`experiments/king_slack.py`) found the 9.3154 certificate's over-count
  diffuse and compounding at +0.022 per cell, the signature of a non-local
  over-count no finite context can see. Guttmann or Jensen: the anisotropic
  theorem's novelty, and the `θ = −1.000(1)` correction structure. Tremblay
  and Vernay held the prior a(18) record and their enumerator is public
  (`github.com/J-Vernay/discrete-figures`); as of 2026-08-04 it had never been
  run here, and the a(40) record then showed `H = 15..19`, 43.84% of the row,
  with no independent program. Since then `a(n)` is rule-independent for
  `n ≤ 39` and a(40) is short one entry (`docs/lastditch-campaign.md`).
- **Papers** (`literature/MISSING.md`): Conway 1995 on the finite-lattice method
  for percolation series, Conway and Guttmann 1995, Enting 1980. The first
  decides whether the four-direction bounding-box decomposition is a
  rediscovery.
- **One textbook gap**: total positivity (Karlin, or Brenti's memoir), for
  the log-convexity attack.
- **Compute, RAM not cores.** The diagonal-mirror count at 24 h and 126 GB
  (`results/symmetry-classes.md`) is both the mod-8 step of the orbit
  congruence and what the five companion sequences need; a 256 GB machine
  makes it an overnight run. The strip ladder at `H = 18, 19` buys about
  +0.05 on the certified lower bound per height at about 3× cost per height
  and is memory-limited near `H ≈ 18` (`results/growth-constant.md`), the
  one item with a guaranteed payoff. The mod-4 orbit census has since been
  run (`results/symmetry-classes.md`).
- **People.** The `λ` upper bound needs connectivity and unbounded extent at
  once, which neither the strip ladder (full connectivity, bounded extent)
  nor the twig-based bound (unbounded extent, relaxed connectivity) achieves;
  no purchase fixes that.

## Reproduce

    # frontier compression
    python3 scripts/probe_hankel_rank2.py --anchor          # reproduces H = 4..10
    python3 scripts/probe_hankel_rank2.py 11                # ~16.5 h single-core, 7.6 GB
    python3 experiments/height_dimension_ladders.py         # the five-sizes inequalities, < 1 s
    experiments/skeletonkey/cell_sparsity_modp.py 8 results/skeletonkey/cellsparse.txt   # H = 8: 2 h 47 min, ~7 GB
    python3 experiments/skeletonkey/nfamily_merge.py 8 12 12
    make build/nkey_census
    build/nkey_census --gate                                # both engines' gates and the cross-check
    build/nkey_census --shared 17                           # ~4 min
    scripts/nkey_census_shared_ladder.sh 18 21              # 7 h 20 min on dalby, 63 GB at H = 21
    scripts/nkey_census_ladder.sh 14 17                     # the per-source engine

    # slicings and structure probes
    python3 experiments/band_structure.py
    python3 experiments/qholo_automatic.py
    make build/prec_guess
    build/prec_guess prec results/b006770_upload.txt 4 5    # and the other boxes of section 2.4
    build/prec_guess alg  results/b006770_upload.txt 4 5

    # connectivity handles
    python3 experiments/skeletonkey/l3_3_fattening.py 8
    python3 experiments/dual_connectivity_blockcount.py --height 21
    python3 experiments/skeletonkey/height_tail_extrapolation.py

    # matching pair
    python3 experiments/matching_pair_euler.py 4            # ~3 min
    python3 experiments/matching_pair_series.py --nmax-rook 11 --nmax-king 9   # ~3 min

    # below onset
    python3 experiments/spectral_edge.py

    # parametric master equation
    python3 experiments/skeletonkey/parametric_master.py --wired-only
    python3 experiments/skeletonkey/parametric_master.py 4  # the K = 4 weights run; (2,2,2,2) takes ~1.8 h
    python3 experiments/hex_diag_deep.py --generate --kmax 6 --hmax 20
    python3 experiments/depth1_parametric.py --kernel --kmax 25

    # converse checks and idea probes
    python3 experiments/converse_sweep.py
    python3 experiments/orbit_parity_probe.py
    python3 experiments/modp_bm_probe.py

The matrix-product-state and C-finite-order probes of 1.1 and 2.1 were
deleted in the 2026-08 tidy and are readable with
`git show 78602f8^:experiments/frontier_svd/svd_probe.py` and
`git show 78602f8^:experiments/recurrence_probe.py`.

## Sources

- `results/skeletonkey-four-mechanisms.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-cell-sparsity.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-hankel-closure.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-l3-3-fattening.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-nfamily-merge.md` (deleted 2026-09-06; its content is above)
- `results/skeletonkey-parametric-master.md` (deleted 2026-09-06; its content is above)
- `results/nkey-census.md` (deleted 2026-09-06; its content is above)
- `results/dual-connectivity-blockcount.md` (deleted 2026-09-06; its content is above)
- `results/span-cap-variation.md` (deleted 2026-09-06; its content is above)
- `results/band-structure-probes.md` (deleted 2026-09-06; its content is above)
- `results/boundary-push-recurrence.md` (deleted 2026-09-06; its content is above)
- `results/boundary-push-tensornetwork.md` (deleted 2026-09-06; its content is above)
- `results/matching-pair-convention.md` (deleted 2026-09-06; its content is above)
- `results/matching-pair-series.md` (deleted 2026-09-06; its content is above)
- `results/discarded-term.md` (deleted 2026-09-06; its content is above)
- `results/strip-spectrum-defect-rate.md` (deleted 2026-09-06; its content is above)
- `results/finite-lattice-crossover.md` (deleted 2026-09-06; its content is above)
- `results/converse-sweep.md` (deleted 2026-09-06; its content is above)
- `results/isotropic-dfinite-boxes.md` (deleted 2026-09-06; its content is above)
- `results/unexplored-avenues.md` (deleted 2026-09-06; its content is above)
- `results/open-conjectures.md` (deleted 2026-09-06; its content is above)
- `results/resource-asks.md` (deleted 2026-09-06; its content is above)
