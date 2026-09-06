# Glossary

Brief reference for terms used across the repo's docs and results notes.

**animal** (lattice animal) — A finite connected cluster on a lattice, under
whatever adjacency rule the family specifies (see *connectivity*); the
statistical-mechanics name for polyominoes and their relatives.
*Site animals* are connected sets of lattice cells/vertices, *bond animals*
connected sets of lattice edges. Polyominoes are exactly the site animals of
the square lattice; polyhexes are the site animals of the triangular lattice.
The term comes from percolation theory.

**b-file** — A plain-text file attached to an OEIS entry listing `n a(n)` pairs,
usually extending far beyond the terms shown inline. The b-file extent, not the
display data, is a sequence's true record.

**benzenoid** — A simply connected polyhex (no holes), so called because these
are the carbon skeletons of benzenoid hydrocarbons ([A018190](https://oeis.org/A018190)).

**Burnside's lemma** — Counts orbits under a group action by averaging the
number of objects fixed by each group element. Here: free polyomino counts are
derived from fixed counts plus counts of shapes invariant under each mirror /
rotation, decomposed by where the axis or center sits on the lattice.

**connectivity (edge-, corner-, face-)** — The adjacency rule declaring when
two cells belong to the same animal; it is part of each family's definition.
Polyominoes, polyhexes, and polyiamonds are *edge-connected*: two cells are
neighbors only if they share a full edge. Polyplets relax this to
*corner-connectivity*: a shared corner also counts (edge-or-corner = king-move
adjacency on the square lattice). Polycubes use *face-connectivity*, the 3D
analog of sharing an edge (corner- and edge-touching variants of polycubes
exist but are separate, rarely-studied families). Caution: "edge" also appears
in an unrelated sense — polysticks are made *of* lattice edges, connected
through shared endpoints (vertices). The site-animal view unifies all of
these: take cells as vertices of an adjacency graph (4-neighbor for
polyominoes, 8-neighbor for polyplets, 6-neighbor for polyhexes/polycubes) and
an animal is a connected induced subgraph; changing the connectivity rule just
changes the graph, which is why one TMA engine can serve several families by
swapping its transition table.

**fixed / one-sided / free** — The three symmetry conventions for counting.
*Fixed*: shapes distinct up to translation only ([A001168](https://oeis.org/A001168)).
*One-sided*: rotations also identified, reflections distinct ([A000988](https://oeis.org/A000988)).
*Free*: rotations and reflections both identified ([A000105](https://oeis.org/A000105)).

**growth constant** (Klarner's constant, λ; τ for polyhexes) — The limit
a(n)^(1/n) as n → ∞: asymptotically, each extra cell multiplies the count by
this factor. For polyominoes λ ≈ 4.0625696 (rigorously only 4.0025 < λ <
4.5252); for polyhexes τ ≈ 5.1831478; for polyplets λ ≈ 7.11 (estimate, no
published value; Domb–Sykes/ratio fit on the 36 known terms plus an
independent μ_H strip-extrapolation, both converging on ~7.11). Rigorously
bracketed **6.543 ≤ λ ≤ 9.3154**: lower from the certified strip ladder (μ₁₇ ≥
6.543, exact Collatz–Wielandt certificate 2026-07-31, superseding Bacher's
3+2√2 ≈ 5.828 directed / 6.475 multi-directed, extended to 6.475196280297,
results/subclasses.md); upper 9.3154 from a
Bui-style finite-type convolution certificate, machine-verified in exact rational
arithmetic (the first polyplet upper bound, ours — none published). Derivation:
[proofs/polyplet-upper-bound.md](proofs/polyplet-upper-bound.md).

**Mason nomenclature (M90, M90V, M45, R180C, R180M, R180V, R90C, R90V)** —
John Mason's labels for symmetry *placements*: the symmetry element (Mirror
axis, 180° or 90° Rotation center) combined with where it sits on the lattice
(through cell centers, cell boundaries/edge midpoints, or vertices). Each
placement gets its own count of invariant fixed polyominoes; Burnside combines
them into free and one-sided totals.

**mod-p / CRT counting** — Running an exact enumeration with counts reduced
modulo one or more word-sized primes, then recombining full integers via the
Chinese Remainder Theorem. Saves memory per database entry versus big integers,
and independent runs under different primes double as verification.

**Motzkin paths / Motzkin numbers** — Lattice paths counting balanced
non-crossing arrangements; the number of valid TMA boundary signatures of
width W is Motzkin-like, ≈ 3^W, which is why TMA memory is exponential in the
boundary width rather than in n.

**OEIS** — The On-Line Encyclopedia of Integer Sequences (oeis.org), the
registry of record for all the counts discussed here.

**polycube** — The 3D analog of a polyomino: a face-connected set of unit
cubes. Fixed [A001931](https://oeis.org/A001931), free
[A000162](https://oeis.org/A000162), both known to n = 22.

**polyhex** — An edge-connected set of cells in the regular hexagonal tiling;
equivalently a site animal on the triangular lattice. Fixed
[A001207](https://oeis.org/A001207) (n ≤ 46), free
[A000228](https://oeis.org/A000228) (n ≤ 36).

**polyiamond** — An edge-connected set of unit triangles in the triangular
tiling. Fixed counts [A001420](https://oeis.org/A001420) are known to n = 75.

**polyomino** — An edge-connected set of unit squares on the square lattice;
the central object of this project family.

**polyplet** (polyking, pseudo-polyomino) — Like a polyomino, but cells are
considered connected when they touch edge-to-edge *or* corner-to-corner
(king-move adjacency). Fixed [A006770](https://oeis.org/A006770) (n ≤ 18),
free [A030222](https://oeis.org/A030222) (n ≤ 17). Target of the option-2
project.

**polystick** (polyedge) — A connected set of unit edges of the square
lattice; the bond-animal counterpart of the polyomino. Fixed
[A096267](https://oeis.org/A096267) (n ≤ 24), free
[A019988](https://oeis.org/A019988) (n ≤ 18).

**pruning** — Discarding TMA signatures that provably cannot be completed into
a shape that will be counted (not enough remaining cell budget to connect all
components, span the box, or satisfy the aspect criterion). The single biggest
practical lever: it, more than hardware, took the square-lattice record from
56 to 70.

**Redelmeier's algorithm** — The classic 1981 method that generates every
polyomino exactly once with no duplicate checking. Cost is proportional to the
number of shapes generated (~λ^n), so it tops out around n ≈ 24–28 on the
square lattice; its modern role is as a brute-force verification oracle and as
the engine for counting rare symmetric subclasses.

**signature** — The TMA's state: an encoding of one boundary line's occupancy
plus the connectivity relations among its occupied cells through the
already-swept region (a 5-letter alphabet in Jensen's square-lattice version).
The number of distinct signatures, not the number of shapes, determines TMA
time and memory.

**transfer-matrix algorithm (TMA)** — Counts animals *without generating
them*: sweep a boundary across a bounding region cell by cell, maintaining a
database from each reachable signature to the number of partial shapes having
that boundary, by size. Exponential in boundary width (~3^W states) instead of
in n (~λ^n shapes), which is why every modern record on every lattice is a
TMA result. Jensen's algorithm (2001–2003) and the Barequet–Ben-Shachar
45°-rotated variant (2024) are the square-lattice instances.

## The technical report's words

`paper/technical-report.tex` (jasonp's prose) and the repo's notes name the
same things differently. The paper's word first, then the repo's, then the
literature's or OEIS's where one exists. Where the two columns differ the
paper's usage is recorded, not argued with.

| paper | repo, code, notes | literature / OEIS |
|---|---|---|
| polyplet, king polyplet | polyplet; king animal; `square8` (the lattice name in `g2` and `tma`) | polyplet, polyking, pseudo-polyomino; site animal on the king lattice; A006770 "polyominoes which need only touch at corners" |
| height H of the bounding box | H; a "column" of the sweep is one height | — |
| T(n,H) | the triangle, `results/triangle.txt`; per-height rows `h<H>.out` | staged as the T(n,H) triangle, `oeis/draft-Tnh-triangle.txt` |
| diagonals of the triangle, H > n/2 | level k = n − H; the diagonal law; in-onset means n ≥ 2k+1 | — |
| formulas, closed forms | P_k; the wired table `diagCoeffTable`; a height is injected when composed from P_k instead of swept | — |
| fixed from earlier rows; fitted; verified against values from later rows | pinned, two anchors per level; holdout; re-pinned from below-onset cells (Undertow) | — |
| transfer matrix | the column kernel (`core/transition.h`) and the kink kernel (`core/kink.h`); the sweep; `orchestrate` | the finite-lattice or transfer-matrix method, Jensen 2001 |
| a transfer-matrix method that uses coloring instead of tracking connectivity | Motley, cutcount; `cpp/motley_par.cpp`, `results/cutcount_b1/` | the Fortuin–Kasteleyn / Potts spin representation of q^{components} |
| Redelmeier enumeration | `g2` (`cpp/g2_redelmeier.cpp`); brute force; the fleet run | Redelmeier 1981 |
| Burnsides congruences | the subgroup census, a(n) mod 4, `results/symmetry-classes.md` | Burnside's lemma; D4 orbit sizes |
| double-checked, agree, confirms | two-source (two programs sharing no code); rule-independent (a second connectivity rule); tiers T1, T2, T2⁻ in `README.md` and `results/confidence.md` | — |
| joiner, domino, split | the doubled row; the pair weight 25 = 16 + 9 (`docs/proofs/T-n-nm1.md`, `results/diagonal-formula.md`) | — |
| holes | hole count k; the Euler-characteristic coordinate (`cpp/tma/euler.h`); flood fill (`g2 --holes`) | the A(n,k) hole triangle, staged |
| one-sided, free, bilateral, asymmetric, non-polyominoes | the companions; the symmetry corpus `results/sym_counts.txt` | A030233, A030222, A030234, A030235, A194596 |
| growth rate λ | λ; the Fekete floor a(40)^{1/40}; the differential-approximant estimate; the certified bracket (L3) | Klarner's constant, the growth constant |
