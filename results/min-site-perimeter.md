# Minimum site perimeter of king animals, n = 1..14

Phase 4a of `docs/middle-kingdom-followups-plan.md`: `unexplored-avenues.md`
idea 7, re-scoped to a min-reduce over the enumeration `directed_cone_anchor
grid` already does (no new search). Phase 4b (closed form + proof, if the
data supports one) is a separate, Opus-only phase and is **not** done here.

## Convention (pinned before the reduce was written)

Site perimeter = the number of distinct **empty** cells adjacent to the
animal. Two adjacencies are possible on this lattice (`unexplored-avenues.md`
idea 10: "boundary" is convention-dependent here in a way the square lattice
hides), so the convention had to be pinned before writing the code, not
discovered by trying both and picking the nicer answer.

**Pinned: KING (8-)adjacency.** Source: `results/polyplet-zoo.md`'s
site-perimeter row ("king/8-adjacency variant ... cross-checked vs a
percolation-literature source"), traced to its actual implementation in
`cpp/g2_redelmeier.cpp`'s `--siteperim` mode, whose header comment states the
convention explicitly and names the cross-check:

> the site perimeter is the number of distinct EMPTY king-(8-)adjacent cells
> of the animal -- the percolation perimeter for the king/nnSquare lattice.
> Cross-SOURCE check vs Mertens 1990 Table IVB (published polynomials)

Full citation (from `oeis/A006770.txt`'s own OEIS links field): S. Mertens,
"Lattice animals: a fast enumeration algorithm and new perimeter
polynomials", J. Stat. Phys. 58 (5-6) (1990) 1095-1108.

The rook (orthogonal, 4-)adjacency variant is kept as the RED control
(`minSPRook`) and is deliberately the wrong convention for this lattice.

## Implementation

`cpp/directed_cone_anchor.cpp`'s `grid` mode does one Redelmeier DFS pass
over ALL fixed king animals of every size <= N, already tallying 20
directedness x convexity cells per animal (`gridTally()`, Phase 0 of
`docs/middle-kingdom-plan.md`). Phase 4a adds a `sitePerim(g, size, king)`
function (king=true: 8 offsets; king=false: 4 offsets; O(size) per call via
the same generation-stamp dedup `reach()`/`multiDirected()` already use) and
two per-n running minima, `minSPKing`/`minSPRook`, updated unconditionally
for every animal generated -- the same population as the `(none,none)` grid
cell, i.e. A006770. The two minima print as two trailing columns after the
existing 20 counts (columns 22 and 23 of `results/mk_siteperim_n14.txt`).

RED-first: `tests/gate_site_perim.py` (`make gate-site-perim`) was run
against a binary with the Phase 4a code hunks reverted (rebuilt clean, no
stale-binary risk) and failed by construction -- `minSPKing`/`minSPRook`
didn't exist, so the gate read the wrong trailing columns and every check
failed. Restoring the code and rebuilding turned the gate GREEN. The gate
also cross-checks `minSPKing` against an independent oracle, `build/g2`'s
`square8` lattice (a completely different DFS: fixed-origin placed/inAnimal
array growth, not the untried-set DFS) with `--siteperim`, which uses the
same king-adjacency for both growth and perimeter counting -- same
population, same convention, different code. Agreement is exact for n=1..9
(the gate's budget; the full n=1..14 comparison below repeats it).

## The sequence, n = 1..14

`minSPKing` (the pinned convention -- **this is the deliverable**):

```
n:     1  2  3  4  5  6  7  8  9 10 11 12 13 14
a(n):  8 10 12 12 14 14 16 16 16 18 18 18 20 20
```

`minSPRook` (RED control -- deliberately the wrong adjacency):

```
n:     1  2  3  4  5  6  7  8  9 10 11 12 13 14
a(n):  4  6  7  8  8  9 10 10 11 11 12 12 12 13
```

The two diverge at every n from 1 onward (RED control confirmed: `king !=
rook` for all n in range, checked in `tests/gate_site_perim.py`).

## Perfect-square hand check

A k*k solid block's king neighborhood is the Minkowski sum with the 3x3 king
ball, a (k+2)x(k+2) square; subtracting the k^2 occupied cells gives site
perimeter 4k+4.

| n = k^2 | k | 4k+4 (hand) | minSPKing (measured) |
|---|---|---|---|
| 1 | 1 | 8 | 8 |
| 4 | 2 | 12 | 12 |
| 9 | 3 | 16 | 16 |

Exact match at every perfect square in range. (The rook control does **not**
reproduce a clean 4k formula at k=3: 4*3=12 but minSPRook(9)=11 -- a
non-square shape beats the block under rook adjacency, which is expected:
see the A261491 discussion below.)

## Cost: wall time and peak RSS vs the 512 s baseline

**The plan's expectation ("should not move that materially") was wrong, and
the measurement says so plainly.**

| | baseline (Phase 0/3, 20-cell grid, no site-perim) | this run (+ minSPKing/minSPRook) | change |
|---|---|---|---|
| wall | 512.1 s | 689.79 s | **+34.7%** |
| cpu (8 threads) | 3672.6 s | 5117.6 s (obs.h) / 5113.51 s user (`/usr/bin/time -l`) | **+39.3%** |
| peak RSS | 1.9 MB (obs.h `peak_rss_mb`) | 1.9 MB (`maximum resident set size` = 1998848 bytes = 1.91 MB) | unchanged |

Same host (gympie), same thread count (8), same compiler flags (`-O3 -Wall
-Wextra -Werror`, unchanged `build/directed_cone_anchor` Makefile rule), same
invocation (`build/directed_cone_anchor grid 14 8`) -- the only difference
between the two runs is the Phase 4a source diff itself (confirmed by the
RED-first revert-and-rebuild above), so the comparison is apples-to-apples on
every axis except source code.

**Why, from the code:** `gridTally()`'s existing four directedness checks
(`reach(Dir5)`, `reach(Dir4)`, `reach(Dir5NoBottom)`, `multiDirected()`
condition (1)) do a 5-, 4-, 5-, 5-offset flood respectively -- 19
neighbour-offset checks per cell -- plus `convexity()`'s O(size)
non-offset bucket pass. Phase 4a adds `sitePerim(king)` (8 offsets/cell) and
`sitePerim(rook)` (4 offsets/cell): **12 more offset checks per cell, a ~63%
increase over the 19 already there.** The realized wall/cpu increase (35-39%)
is smaller than that 63%, consistent with `gridTally()` being a large but not
total share of per-node cost -- the DFS's own candidate-generation and
recursion bookkeeping in `rec()` doesn't scale with animal size and dilutes
the ratio. For a sanity comparison: the precedent of adding the entire `mdir`
row in Phase 3 (`results/middle-kingdom-grid.md`) -- one predicate,
14->19 offsets by the same counting, a smaller *offset* increase (36%) than
Phase 4a's (63%) -- cost 302.8s -> 512.1s, **+69.1% wall**, a *larger*
realized increase than Phase 4a's 35%. That's because `multiDirected()`'s
condition (2) does a per-keystone backward walk with no fixed offset count
(the file's own comment: "bounded by size per keystone in the worst case"),
which the simple offset count misses entirely; `sitePerim()` has no such
walk -- it is a single stamped flood, the cheapest kind of pass already in
this file. Parallel efficiency did not regress (cpu/wall = 7.17 baseline vs
7.42 here, out of 8 threads) -- the added cost is genuine per-thread compute,
not new contention.

**Bottom line: +34.7% wall, +39.3% cpu, RSS unchanged. Not immaterial. Still
well inside a laptop-scale budget (both runs are single-digit minutes), so it
does not change Phase 4a's laptop-only classification, but it is a real,
explained cost, not noise.**

## RED control

`minSPRook` (orthogonal adjacency -- deliberately wrong for this lattice) is
strictly less than `minSPKing` at every n = 1..14: `king - rook` = 4, 4, 5,
4, 6, 5, 6, 6, 5, 7, 6, 6, 8, 7. It does not reproduce 4k+4 at n=9 (11, not
12) -- confirming it is a materially different quantity, not the same answer
under a relabeled convention.

## OEIS lookups (`experiments/oeis_lookup.py`, read-only)

**Full sequence (n=1..14), `minSPKing`:**
```
8,10,12,12,14,14,16,16,16,18,18,18,20,20
```
**HIT: A235382** "a(n) = smallest number of unit squares required to enclose
n units of area", offset 0 -- exact match for all 14 terms (A235382's a(1)
through a(14) against ours). OEIS gives the closed form directly:
`a(n) = A027709(n) + 4 = 2*ceiling(2*sqrt(n)) + 4`.

**6-term prefix, `minSPKing`:** `8,10,12,12,14,14` -- same hit, A235382,
same exact match on the first 6 terms.

**minSPKing = A027709(n) + 4 confirmed directly against A027709's own data**
(offset 0: `0,4,6,8,8,10,10,12,12,12,14,14,14,16,16,...`, so
A027709(1..14) = `4,6,8,8,10,10,12,12,12,14,14,14,16,16`); adding 4
reproduces `minSPKing` exactly for every n=1..14. This is an exact identity
over the full measured range, not a coincidence of small n: the +4 is the
four corner cells of the king-neighborhood ring that edge/rook adjacency
never counts (the same arithmetic as the k*k-block hand check above, and
apparently it generalizes to every n's *minimizing* shape, not just squares).
A235382's name ("enclose n units of area" with unit squares, i.e. cells that
may touch only at a corner) is consistent with this being the same quantity
under different phrasing, though the identification rests on the numeric/
formula match, not on independently re-deriving A235382's own proof (its
only OEIS comment attributes the result to "the students Daring, et al." in
an unfetched external link).

## A027709/A027710 comparison -- stated plainly

The plan asked to compare against "A027709/A027710, the square-lattice
analogue" and say plainly whether ours matches (a match would mean the king
constraint is not biting). **Neither citation is right as given, and the
verdict is not a bare match:**

- **A027709** (minimal EDGE perimeter of a square-lattice polyomino) is a
  real, relevant sequence, but `minSPKing` does not equal it -- it equals
  `A027709(n) + 4`, an exact but nontrivial relationship, at every n
  measured. This is precisely quantified, not zero: **the king constraint
  bites by a constant +4 at every n**, not by an unpredictable or growing
  amount, but not by nothing either. A bare "matches A027709" would be the
  wrong claim; so would "matches nothing."
- **A027710** is **not a perimeter sequence at all** -- confirmed by direct
  lookup (`experiments/oeis_lookup.py --full id:A027710`): "Number of ways of
  placing n labeled balls into n unlabeled (but 3-colored) boxes," a
  Bell/Stirling-triangle combinatorics sequence with an e.g.f.
  `exp(3(e^x-1))`. It shares no defining relationship with any perimeter
  notion; the ID pairing in `docs/middle-kingdom-followups-plan.md` and
  `results/unexplored-avenues.md` is simply mistaken (OEIS A-numbers are
  assigned by submission order, not by topic, so adjacent IDs carry no
  implication of relatedness). This is flagged here rather than silently
  substituted.
- The genuine square-lattice *site*-perimeter analogue -- same methodology,
  rook adjacency used for both growth and perimeter counting, verified via
  `build/g2 square4 --siteperim` (an independent oracle, run separately from
  the RED control above) -- is **A261491**, `a(n) = ceiling(2 + sqrt(8n-4))`,
  offset 1. Its own OEIS comment (Sean A. Irvine, 2020) states it directly:
  "a(n) is the minimum (cell) perimeter of any polyomino of n cells" (Go-board
  framing: minimum stones to surround n points with orthogonal-only
  adjacency). This is exactly what `minSPRook` -- the RED control, **not**
  the pinned convention -- reproduces term for term through n=14: `g2
  square4 --siteperim`'s per-n minimum over n=1..14 is
  `4,6,7,8,8,9,10,10,11,11,12,12,12,13`, identical to `minSPRook` above.

**Plainly stated: `minSPKing`, the quantity Phase 4a actually pinned and
computed, matches neither A027709 nor A027710 outright. It matches A027709
plus a constant 4, and A235382 exactly. The sequence that matches a genuine
square-lattice site-perimeter analogue (A261491) term for term is the ROOK
column -- the deliberately-wrong RED control, not the deliverable. So: the
king constraint is not "not biting" in the trivial sense the plan flagged as
the interesting negative outcome -- it bites, by a clean, constant, fully
quantified +4 relative to the classical square-lattice edge-perimeter
problem, at every n measured.**

## Reproduce

```
make build/directed_cone_anchor build/g2
make gate-site-perim                              # small-n RED-first + oracle cross-check, seconds
scripts/run_site_perim_n14.sh                      # 689.8 s wall, 8 threads, gympie
python3 experiments/oeis_lookup.py 8,10,12,12,14,14,16,16,16,18,18,18,20,20
python3 experiments/oeis_lookup.py 8,10,12,12,14,14
python3 experiments/oeis_lookup.py --full id:A027709
python3 experiments/oeis_lookup.py --full id:A027710
python3 experiments/oeis_lookup.py --full id:A261491
python3 experiments/oeis_lookup.py --full id:A235382
build/g2 square4 14 --siteperim                    # rook-lattice independent cross-check, <1 s
build/g2 square8 9  --siteperim                    # king-lattice independent oracle, gate budget, <1 s
```

## Phase 4b — the closed form is already known; kill criterion fired

Phase 4b of `docs/middle-kingdom-followups-plan.md` was "guess a closed form,
then prove it by an extremal argument", with an explicit kill criterion: *if
`oeis_lookup.py` returns a hit in Phase 4a, this is a known sequence and the
phase reduces to a one-paragraph note plus a cross-reference. Do not prove
someone else's theorem.* It returned a hit — A235382, confirmed by direct
lookup (`--full id:A235382`: "a(n) = smallest number of unit squares required
to enclose n units of area", offset 0), which carries the closed form in its
own formula field: `a(n) = 2*ceiling(2*sqrt(n)) + 4 = A027709(n) + 4`
(A027709 also confirmed by direct lookup: "Minimal perimeter of polyomino
with n square cells", offset 0, `a(n) = 2*ceiling(2*sqrt(n))`). So the closed
form for `minSPKing` is **someone else's published result, not ours** — we
verify it against our data and stop there. Phase 4b produced no new theorem,
by design.

**Verified exactly on every n the enumeration reached**
(`experiments/min_site_perim_closed_form.py`, exit 0):

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `2*ceil(2*sqrt(n))+4` | 8 | 10 | 12 | 12 | 14 | 14 | 16 | 16 | 16 | 18 | 18 | 18 | 20 | 20 |
| `minSPKing` (measured) | 8 | 10 | 12 | 12 | 14 | 14 | 16 | 16 | 16 | 18 | 18 | 18 | 20 | 20 |

Fourteen of fourteen. The check is **integer-exact**: `math.sqrt` at a perfect
square can land a hair below the true root, which would make `ceil` off by one
at exactly n = 4 and n = 9 — the two perfect squares in range, and both step
boundaries of the formula. The script therefore never touches a float, using
`ceil(2*sqrt(n))` = least `m >= 0` with `m^2 >= 4n`, obtained from
`math.isqrt(4n)` (exact integer floor-sqrt) with a `+1` unless `4n` is a
perfect square.

**Scope, honestly.** Our enumeration reaches n = 14 and the verification above
covers exactly that range. The closed form is *asserted by OEIS for all n*; we
have neither independently verified it beyond n = 14 nor re-derived its proof
— which is the point of the kill criterion. Carrying forward the caveat from
the OEIS section above: A235382's only comment attributes the result to "the
students Daring, et al." via an external link that was not fetched, so the
provenance of the proof itself is unexamined here. What is ours is the n ≤ 14
king-lattice data and its agreement with the formula.

Cross-reference: `results/unexplored-avenues.md` idea 7, first bullet, is
closed by this section together with Phase 4a above.

## Provenance

Measured 2026-08-05 on gympie, `git=54440c2-dirty`. `minSPKing`/`minSPRook`
columns confirmed byte-identical to `results/mk_grid20_n14.txt` on all 21
preceding columns (the Phase 0/3 grid table, unaffected by this change), and
the `(none,none)` column matches `fixtures/b006770.txt` exactly through
n=14 -- no mismatch against any banked reference.
