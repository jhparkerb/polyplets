# L1 — corner gluing: the assembly state space, measured (and it is larger)

2026-08-12. Round-3 lane deliverable for `docs/triangle-round3-brief.md`,
scored under `docs/skeptical-reader-standard.md`. Blind list filed first at
`results/triangle-r3-blind-l1.md` (nothing in it is revised below; the
measurement confirms its prediction 1 and its suspicion about candidates 2-3).
Script: `experiments/tristruct/r3_l1_piece_states.py`; logs
`r3_l1_piece_states.log` (validation), `r3_l1_closure.log` (closure). Laptop,
81 s total. Carries L2's single question in its own section at the end.

## Entry ticket

**Levels cleared: level 1 only, and only by the variant that cannot be
executed; the executable variant clears neither. The lane closes negative on
its own measurement.** Where is king-connectedness decided? In the corner-
gluing frame it is a graph condition on the piece-contact graph — pieces are
rook-connected polyominoes, and the animal is connected iff the contact graph
is. That formalisation is semantically independent of union-find-over-a-
frontier, and its ingredient counts (fixed polyominoes) are other people's
published enumerations: level 1 clears. But the two ways to *evaluate* the
condition are (a) a strip sweep, which the measurement below shows is a
frontier partition DP carrying *more* state than the engines' — component
labels at piece granularity PLUS rook-piece labels underneath them, the
brief's piece-level-labels trap realised and quantified, failure mode not
disjoint from the engines' (a wrong stranding or completion rule reproduces
identically) — so level 2 fails; or (b) joint whole-piece placement, which
keeps the independence story and is gas-shaped, priced out on the record at
surplus k = n−H = 19..25 (`results/defect-gas.md`, ≈20×/k, reach k ≈ 9-10
with C++ effort). No variant reaches the band.

## Disclosure block (phase-1 mapping per the brief)

    claim:                             corner-gluing/piece-assembly cannot reach T(40,H), H=15..21, exact or mod-p; measured, obstruction named
    share of a(40) reached:            0%  (target band H=15..21, 50.84%, provenance 'real-sweep' — tri.provenance(40,H) quoted for all seven cells, loader rule experiments/tristruct/triangle.py:53-58; the route reaches none of it)
    bits against enumeration error:    0
    bits against formula-chain error:  0   conditional on: nothing (no formula proposed)
    rule independence:                 level 1 yes (contact-graph condition, external ingredients); level 2 no for the executable strip form (refined frontier partition DP, shared failure mode); the level-2-clean form is gas-shaped and priced out
    derivation independence:           measurement consumed banked cells only as validation targets: T(n,H) for H≤6, n≤10 and the C(n,c) table of results/component-stratification.md (n≤7); no band cell read or consumed
    input footprint:                   ~68 cells for validation, max n = 10; 0 band cells
    checker:                           none earned (negative lane); the phase-2 artifact this route would have ended in does not exist; the measurement itself: experiments/tristruct/r3_l1_piece_states.py, 81 s laptop, RED control included (validate subcommand plants a corrupt expected value and fails as required)
    sensitivity:                       deferred per the brief's phase-1 mapping (no checker to sensitise)
    prior-work grep:                   git log --all --oneline --name-only -- 'results/*.md' 'docs/*.md' 'docs/**/*.md'  (both docs terms per the standard; 510-path sweep), filtered -iE 'corner|glu|piece|assembl|stratif|compos'; hits: results/component-stratification.md (the lane's named input) and commit f8c2e16 (n=19 sampling: rook-component mean 10.07, 74.4% tree gluing-graphs — a statistic, not a state-space or assembly-DP measurement). The measurement below is new to the project.

## The measurement: piece-assembly state space vs cell frontier

Two column-sweep DPs over the height-H strip, identical framework, exact
integer arithmetic (`r3_l1_piece_states.py`):

- **CELL** — boundary state = occupancy + king-component partition of the
  occupied runs + touch flags: the engines' frontier object at run
  granularity.
- **PIECE** — the coarsest state that can track corner-glued assembly:
  occupancy + **rook-piece partition** of the runs (which runs belong to the
  same polyomino piece, connected behind the frontier) + king partition of
  the pieces + flags. This is the minimum any assembly DP must carry: it
  needs the rook labels to know piece identity/completion and the king
  labels to know which pieces have connected — the brief's trap, made
  executable.

**Validation before measurement** (`validate`, log `r3_l1_piece_states.log`):
the PIECE DP reproduces the banked `T(n,H)` exactly for H = 1..6, n ≤ 10
(cells named: provenance `'real-sweep'` for H = 3..6, `'closed-form-lowstrip'`
for H ≤ 2, quoted from `tri.provenance` at run time), and reproduces the full
`C(n,c)` stratification table of `results/component-stratification.md` for
n ≤ 7 (all 28 cells, exact, c tracked as completed + live pieces). RED
control: a deliberately corrupted expected value fails as required. So the
PIECE state definition is faithful — it counts exactly the corner-glued
assemblies — before its size is measured.

**The closure** (`closure`, log `r3_l1_closure.log`): number of distinct
reachable live core states (flagless), any n, any width:

| H | cell states | piece states | piece/cell | cell ratio | piece ratio |
|---|---|---|---|---|---|
| 2 | 3    | 3    | 1.000 | —     | —     |
| 3 | 8    | 9    | 1.125 | 2.667 | 3.000 |
| 4 | 20   | 25   | 1.250 | 2.500 | 2.778 |
| 5 | 50   | 72   | 1.440 | 2.500 | 2.880 |
| 6 | 126  | 210  | 1.667 | 2.520 | 2.917 |
| 7 | 322  | 629  | 1.953 | 2.556 | 2.995 |
| 8 | 834  | 1917 | 2.299 | 2.590 | 3.048 |
| 9 | 2187 | 5943 | 2.717 | 2.622 | 3.100 |

Independent cross-check of the CELL column: 3, 8, 20, 50, 126, 322, 834,
2187 = Motzkin(H+1) − 1 for H = 2..9 exactly — the second-source branch's
banked count for the king column TM (`results/king-column-motzkin.md`, listed
in the harness index Part 1C), reproduced here from scratch. So the baseline
is the real object, not a strawman.

**Growth law.** Cell states grow as Motzkin ~ 3^H/H^{3/2} (per-H ratio 2.50 →
2.62, rising toward 3). Piece states grow with per-H ratio 2.78 → 3.10,
**monotone increasing and already past 3 at H = 9**, so the piece base is
strictly larger than the cell base; the piece/cell overhead multiplies by
×1.15-1.18 per unit H on every measured step. The core conclusion needs no
extrapolation: **at every measured H ≥ 3 the coarsest faithful piece-assembly
state space is strictly larger than the cell frontier, and the gap widens
with H.** (Extrapolated to the band, flagged as extrapolation: overhead
≈ 7× at H = 15, ≈ 18× at H = 21 — but the sign of the verdict rests on the
measured monotone divergence, not on these numbers.)

**Why, structurally.** The boundary of a strip is made of cells whatever the
assembly vocabulary; piece identity is *extra* information on top of the king
labels (the rook partition refines the king partition — vertically adjacent
occupied cells are edge-adjacent, so runs are piece atoms, and distinct king
components cannot interleave, so both partitions are non-crossing and
nested). "Pieces are coarser than cells" is true of the animal and false of
the frontier: an assembly DP must remember strictly more per boundary column
than the engines do, never less. The lane's one real hope is measured
backwards. A mod-p variant changes counter width, not state count, so it
inherits the same verdict.

## The external-ingredient variant, and what is actually citable

The independence story — ingredient counts computed by other people — only
survives if pieces are placed *whole*, never re-enumerated cell by cell (a
strip sweep re-enumerates every piece interior and consumes no external
number). What exists to consume:

- **By size:** A001168 (fixed polyominoes) b-file to **n = 70**
  (`curl https://oeis.org/A001168/b001168.txt`, 70 terms, checked
  2026-08-12) — comfortably past every piece a 40-cell animal can contain.
- **By size × height** (what a height-limited gluing actually needs, pieces
  up to ~39 cells at heights up to 21): NOT ESTABLISHED as published.
  OEIS holds fixed-height slices for small heights only (A059483 for 2×k,
  A059680 for 4×k, A059681 for 5×k, plus A292357 by width×height without a
  cell count), nothing approaching the needed range; it would have to be
  recomputed, forfeiting the "other people's numbers" story for most of the
  mass.

But the variant dies upstream of its ingredient table.
`results/component-stratification.md` banks that the composition is not
free — corner contacts are geometrically constrained (non-overlap plus
corner-only contact between distinct pieces are cell-geometric conditions) —
so whole-piece placement means *joint* placement of ~n/2 ≈ 20 interacting
pieces (measured mean component count 10.07 at n = 19, commit f8c2e16;
`component-stratification.md` puts the typical animal at ~n/2 pieces of ~2
cells). Joint placement of components is exactly the shape
`results/defect-gas.md` priced: ≈20× per unit of surplus k, measured k=4:
3.1 s, k=5: 65 s, k=6: >530 s, realistic reach k ≈ 7 (Python) to k ≈ 9-10
(C++), against the band's k = n−H = 19..25. Priced out by roughly nine
orders of magnitude of measured growth rate.

## Cost verdict

**The route does not reach H = 15..21 at n = 40, exact or modulo any prime,
at any cost worth stating.** Its two executable forms are (a) a strip DP
whose state space is measured strictly larger than the cell frontier the
production engines already pay — worse than the thing it would replace, and
level-2-shared anyway; (b) whole-piece joint placement, gas-shaped, priced
out on the project's own measurement by the surplus gap 9-10 vs 19-25. No
phase-2 proposal is earned. The obstruction, named: **piece structure refines
the frontier instead of coarsening it, and the only frontier-free evaluation
of the contact-graph condition is joint placement.**

## L2's single question: is there an inversion route that is not gas-shaped?

**No route found, and every named inversion form lands in one of two priced
shapes.** Any inversion that recovers connected counts from unconstrained
ones — Möbius inversion over the partition lattice, the exponential-formula
log, a Mayer/cluster expansion, deletion-contraction on the contact graph —
takes as its ingredient the number of *placements* of multisets of
components with prescribed contact and avoidance relations. That ingredient
does not factor into per-component terms, because the constraint is
geometric: `results/component-stratification.md` banks precisely that no
free-composition GF exists for corner gluing. So the ingredient must be
produced either by joint placement of the interacting components — the gas
DP, measured at ≈20×/k with reach k ≈ 9-10 against the band's k = 19..25
(`results/defect-gas.md`, reach verdict) — or by a frontier sweep, which is
the rule class this round exists to escape. The cost of every inversion route
inspected is governed by joint placement; the inversion step only ever adds
sign bookkeeping on top of it. NOT ESTABLISHED: an in-principle impossibility
proof that *no* non-gas-shaped inversion exists — what is established is
that each named form is gas- or frontier-shaped, which is the cited
paragraph the brief asked for.

## NOT ESTABLISHED

- The piece-state growth base (measured only ≥ 3.1 and rising at H = 9; the
  extrapolated 7-18× band overheads are extrapolation, marked above).
- Published fixed-polyomino tables by (size, height) to the needed range
  (sizes ≤ 39, heights ≤ 21): not found; A001168-by-size to n = 70 is the
  only ingredient table confirmed citable.
- An impossibility proof for non-gas-shaped inversion (see L2 section); the
  lane's negative rests on measurements and the banked no-free-GF result,
  not on that proof.

## Appended 2026-08-12: successor rows filed

Per the mid-round amendment, the lane's two closures (L1-1 strip assembly DP,
L1-2 whole-piece placement/inversion) each filed successors in
`results/triangle-r3-queue.md`: L1-3 (band-geometry c-distribution — the gas
price is per-component, so the family survives exactly where components are
few; measurable with this lane's validated DP), L1-4 (tree-contact-graph
stratum via grafting GFs — acyclicity is what would make composition free,
and 74.4% of n=19 animals are trees), L1-5 (external per-stratum anchor via
the 45° bijection for a phase-2 stratified sweep), and L1-6 (cross-lane
pruning fact: the measured Motzkin floor plus the piece result close "find a
better boundary vocabulary" as a family — the remaining search space is
no-cut/implicit methods).

## Appended 2026-08-12, second dispatch: L1-3 measured, L1-4 closed

**L1-3 — the c-distribution under band geometry. Verdict: squeezing
ANTI-concentrates; the small-c stratified route closes.** Measured with the
validated PIECE DP with exact c tracking, every row fail-closed against the
banked `T(n,H)` (`Triangle.load()`, full validation; all cells named here are
`'real-sweep'`, H = 3..8). Logs: `r3_l1_band_quick.log` (fixed-n sweep),
`r3_l1_band_axis.log` (fixed-ratio sweep).

**Run-provenance note, recorded plainly.** Every probe in this lane ran on
gympie, which the project forbids for jobs; the round's "laptop minutes"
dispatch was in error (the lead's, acknowledged by them mid-round) and a
stop order followed. The wider grid `r3_l1_band_cdist.py` was KILLED
MID-FLIGHT BY THE LEAD at 21 min (log empty — nothing from it is used); the
fixed-n quick sweep was KILLED at 10 min after its first six rows (those six
are used and are the squeeze-axis table below); the ~30 s fixed-ratio pass
completed before the stop order arrived. No further compute runs here; the
unmeasured remainder is filed below as NOT ESTABLISHED with its cost on the
compute boxes.

Squeeze axis, fixed n = 12, height rising:

| n/H | mean_c/n | P(c<=3) |
|---|---|---|
| 4.00 | 0.436 | 1.9e-1 |
| 3.00 | 0.481 | 1.2e-1 |
| 2.40 | 0.510 | 8.4e-2 |
| 2.00 | 0.532 | 6.2e-2 |
| 1.71 | 0.551 | 4.6e-2 |
| 1.50 | 0.572 | 3.1e-2 |

Monotone the wrong way for the stratified hope: taller = MORE fragmented,
heading exactly toward the H = n drift-walk limit, which is exact with no
compute — each of the n−1 row offsets is ±1 (corner contact, new piece) with
weight 2/3, so mean_c = 1 + 2(n−1)/3 ≈ 0.69n.

How thin this is, stated explicitly: the evidence is n ≤ 16, H ≤ 8 — eleven
measured cells plus the exact diagonal limit. The direction is uniform at
every measured point on both axes and agrees with the provable endpoint,
which is why the closure is claimed; the n = 40 numbers (~21 pieces, ~1e-7
small-c share) are extrapolations and marked as such.

Band axis, ratio n/H ≈ 2.25-2.40 (the band is 40/H = 1.9-2.7), n growing:
mean_c/n = 0.494, 0.511, 0.510, 0.517, 0.520 at n = 7, 9, 12, 14, 16 —
flat-to-rising at ≈ 0.52, so a band cell at n = 40 is typically **~21
pieces**, slightly MORE fragmented than the whole-family ~n/2. And
P(c ≤ 3) = 5.3e-1, 2.6e-1, 8.4e-2, 3.2e-2, 1.2e-2 over the same n — geometric
decay ≈ ×0.63 per cell, extrapolating to ~1e-7 at n = 40 (extrapolation,
marked). The externally-computable small-c strata carry a vanishing share of
every band cell; the whole-family "~n/2 pieces" statement survives height
restriction and sharpens against the route. Closed the honest way: the trend
points away from it at every measured point on both axes.

**L1-4 — tree-contact-graph grafting: closed per the lead's conditional,
with the family argument.** L1-3 did not leave it live, and the obstruction
is family-wide: acyclicity removes the graph-side obstruction to free
composition, not the geometric one — grafted subtrees still occupy the same
plane, and the only measured geometric independence anywhere in this problem
is the defect gas's separation-≥-1 renewal factorization
(`results/defect-gas.md`: cluster weights factorize EXACTLY at row
separation ≥ 1), a 1D structure already exploited and priced out at band
surplus. With band animals measured at ~21 tiny pieces, tree grafting is
~21-piece joint geometry — the L1-2 closure again. No measurement spent, per
the dispatch.

**NOT ESTABLISHED — the unmeasured remainder, as a phase-2 proposal
(queue row L1-11).** The killed grid's missing points, and what firming the
trend to convincing scale would take on a compute box: squeeze-axis tail
(12,10) and (12,12) — the (12,12) endpoint is already exact by the
drift-walk formula, so only (12,10) carries information — and band-axis
extension (18,8), (20,9), (22,10) at ratio ≈ 2.2. Measured anchor: (16,7)
took 21.7 s single-core Python (M4); the step cost grows ≈ ×20 per
band-axis increment, so (18,8) ≈ 7 min, (20,9) ≈ 2.5 h, (22,10) ≈ 2 days
single-core Python — one process per cell, embarrassingly parallel, trivial
RAM at these sizes; a C++ port (~100× per the project's usual factor) puts
(22,10) at ~30 min. Runs on ayr or dalby only, jasonp's call, per the
job-start checklist.

Queue rows filed for this dispatch: L1-7 (closes L1-3, the measurement),
L1-8 (closes L1-4, the family argument), L1-9 (OPEN — the aligned survivor:
top strata c ≥ n−j are the externally-computable ones via the 45° bijection
and fragmentation RISES with height; value is as per-cell external anchor
for a phase-2 stratified sweep, merging with L1-5; honest prior: share
exponentially small), L1-10 (OPEN, cross-lane to L3/L6: band animals are
gases of ~21 tiny pieces, so contour encodings must trace ~21 disjoint piece
outlines per animal — quantitative sharpening of L3's obstruction).
