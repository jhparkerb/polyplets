# Glossary

Terms used in the notes, the results files and the code.

**animal** (lattice animal) — A finite connected set of cells on a lattice,
under whatever adjacency rule the family specifies. Polyominoes are the site
animals of the square lattice; the name comes from percolation theory.

**b-file** — The plain-text `n a(n)` list attached to an OEIS entry, usually
extending well past the terms shown inline; it is the sequence's record.

**Burnside's lemma** — Counts orbits of a group action by averaging the number
of objects fixed by each element. Free counts come from fixed counts plus the
counts of shapes invariant under each mirror and rotation.

**coloring recount** — The second enumeration program. Instead of tracking
which boundary cells are connected, it colors components and reads the
connected count off the coefficient of `q¹` (the Fortuin–Kasteleyn / Potts
device, `docs/proofs/cutcount-identity.md`). Code under `results/cutcount_b1/`.

**column kernel, kink kernel** — The two transitions of the production
transfer matrix: a whole column per step (`core/transition.h`) or one cell per
step with a carry byte for the one overwritten cell still king-reachable
(`core/kink.h`). `docs/engine-record.md`.

**connectivity (edge-, corner-, face-)** — The rule deciding when two cells
belong to the same animal. Polyominoes, polyhexes and polyiamonds are
edge-connected; polyplets also count a shared corner (king-move adjacency);
polycubes are face-connected. Changing the rule changes the adjacency graph
and nothing else, which is why one transfer-matrix engine serves several
families.

**diagonal law** — For fixed `k`, `T(n, n−k) = P_k(n)·3^(n−1−3k)` for
`n ≥ 2k+1`, with `P_k` an integer-valued polynomial of degree `k`
(`docs/proofs/diagonal-law.md`). "Level `k`" means the diagonal `k = n − H`;
"onset" is `n = 2k+1`; "below onset" is `n ≤ 2k`.

**level, depth, onset, defect** — Level `k` is the diagonal `H = n − k` of
the triangle, governed by `P_k`. Its onset is `n = 2k+1`, the smallest `n`
where the diagonal law holds. Depth `j` counts steps below the onset; the
defect `D_j(k)` is the exact amount by which the law fails there
(`results/below-onset.md`).

**fit, holdout** — The two constants of `P_k` are fitted from two enumerated
entries; a holdout is a further enumerated entry not used in the fit, which
the formula must reproduce.

**fixed / one-sided / free** — Shapes distinct up to translation only
([A001168](https://oeis.org/A001168)); rotations also identified
([A000988](https://oeis.org/A000988)); rotations and reflections both
identified ([A000105](https://oeis.org/A000105)).

**product form** — `P_k(n) = [y^k] exp(Σ_j (a_j + b_j n) y^j)`: each level adds
exactly two rational constants (`docs/proofs/product-form.md`).

**growth constant** (λ; Klarner's constant) — `lim a(n)^(1/n)`. Polyominoes
λ ≈ 4.0625696 (rigorously 4.0025 < λ < 4.5252); polyhexes τ ≈ 5.1831478;
polyplets λ ≈ 7.11 (estimate), rigorously 6.543 ≤ λ ≤ 9.3154
(`results/growth-constant.md`, `docs/proofs/polyplet-upper-bound.md`).

**height run, frontier, map, merge, unit, spill, injection** — The engine's
own words; defined at the top of `docs/engine-record.md`.

**injected height** — A row `T(·,H)` composed from the diagonal formulas
instead of enumerated. Which heights are injected in each run is in the
per-term `results/ns_a*/PROVENANCE.md`.

**Mason nomenclature (M90, M90V, M45, R180C, R180M, R180V, R90C, R90V)** —
John Mason's labels for where a symmetry element (mirror axis, rotation
center) sits on the lattice; each placement has its own invariant count.

**mod-p / CRT counting** — Counting modulo several word-sized primes and
recombining by the Chinese remainder theorem. The production engine does not
do this; the coloring recount does.

**Motzkin paths** — The valid boundary signatures of a polyomino transfer
matrix of width `W` number about `3^W`, which is why memory is exponential in
the boundary width and not in `n`. King adjacency allows crossing partitions,
so that encoding does not apply here.

**OEIS** — The On-Line Encyclopedia of Integer Sequences (oeis.org).

**polycube** — Face-connected unit cubes. Fixed
[A001931](https://oeis.org/A001931), free [A000162](https://oeis.org/A000162).

**polyhex** — Edge-connected hexagons; equivalently a site animal on the
triangular point lattice. Fixed [A001207](https://oeis.org/A001207), free
[A000228](https://oeis.org/A000228).

**polyiamond** — Edge-connected unit triangles. Fixed
[A001420](https://oeis.org/A001420).

**polyomino** — Edge-connected unit squares.

**polyplet** (polyking, pseudo-polyomino, king animal) — Cells connected
edge-to-edge or corner-to-corner. Fixed [A006770](https://oeis.org/A006770),
free [A030222](https://oeis.org/A030222). The subject of this repository.

**polystick** (polyedge) — A connected set of unit edges of the square
lattice. Fixed [A096267](https://oeis.org/A096267), free
[A019988](https://oeis.org/A019988).

**pruning** — Dropping transfer-matrix states that cannot be completed within
the cell budget. `docs/engine-record.md` §5 measures the production prune
against the exact optimum.

**Redelmeier's algorithm** — Generates every animal exactly once with no
duplicate check; cost proportional to the number of shapes, so it reaches
about n = 22 here. Its role is as an independent check (`build/g2`).

**second source, two-source** — A value computed by two programs sharing no
code; "rule-independent" means the two programs also use different
connectivity rules. `results/confidence.md` says which terms have which.

**signature** — A transfer-matrix state: one boundary line's occupancy plus
the connectivity among its occupied cells through the swept region. The
number of signatures, not of shapes, sets time and memory.

**provenance tags** — The letters in `results/provenance-table.md`: B
Redelmeier, G fixed-height generating functions, R small-height recurrences,
S strip transfer matrix, P closed forms on enumerated heights, F closed forms
above them, M coloring recount, U closed forms refitted to the coloring
recount, C the mod-2/mod-4 subgroup congruence.

**T(n, H)** — The number of fixed polyplets with `n` cells whose bounding box
has height exactly `H`; `a(n) = Σ_H T(n,H)`. The table is
`results/triangle.txt`, per-height rows are `h<H>.out`.

**transfer-matrix algorithm** — Counts animals without generating them: sweep
a boundary across the box, keeping for each reachable signature the number of
partial shapes by size. Jensen (2001–2003) for the square lattice.

## The technical report's words

`paper/technical-report.tex` and the repository name the same things
differently. The paper's word first, then the repository's, then the
literature's or OEIS's where one exists.

| paper | repository, code, notes | literature / OEIS |
|---|---|---|
| polyplet, king polyplet | polyplet; king animal; `square8` (the lattice name in `g2` and `tma`) | polyplet, polyking, pseudo-polyomino; A006770 "polyominoes which need only touch at corners" |
| height H of the bounding box | H; a "column" of the sweep is one height | — |
| T(n,H) | the triangle, `results/triangle.txt`; per-height rows `h<H>.out` | staged as the T(n,H) triangle, `oeis/draft-Tnh-triangle.txt` |
| diagonals of the triangle, H > n/2 | level k = n − H; the diagonal law; in-onset means n ≥ 2k+1 | — |
| formulas, closed forms | P_k; the formula table `diagCoeffTable`; a height is injected when composed from P_k instead of swept | — |
| fixed from earlier rows; fitted; verified against values from later rows | determined from two entries per level; holdout; determined from below-onset entries | — |
| transfer matrix | the column kernel (`core/transition.h`) and the kink kernel (`core/kink.h`); the sweep; `orchestrate` | the finite-lattice or transfer-matrix method, Jensen 2001 |
| a transfer-matrix method that uses coloring instead of tracking connectivity | the coloring recount; `cpp/motley_par.cpp`, `results/cutcount_b1/` | the Fortuin–Kasteleyn / Potts spin representation of q^{components} |
| Redelmeier enumeration | `g2` (`cpp/g2_redelmeier.cpp`); brute force; the fleet run | Redelmeier 1981 |
| Burnside congruences | the subgroup census, a(n) mod 4, `results/symmetry-classes.md` | Burnside's lemma; D4 orbit sizes |
| double-checked, agree, confirms | two-source (two programs sharing no code); rule-independent (a second connectivity rule); see `results/confidence.md` | — |
| joiner, domino, split | the doubled row; the pair weight 25 = 16 + 9 (`docs/proofs/T-n-nm1.md`, `results/diagonal-formula.md`) | — |
| holes | hole count k; the Euler-characteristic coordinate (`cpp/tma/euler.h`); flood fill (`g2 --holes`) | the A(n,k) hole triangle, staged |
| one-sided, free, bilateral, asymmetric, non-polyominoes | the companions; the symmetry corpus `results/sym_counts.txt` | A030233, A030222, A030234, A030235, A194596 |
| growth rate λ | λ; a(40)^{1/40} as a lower bound; the differential-approximant estimate; the certified bracket | Klarner's constant, the growth constant |
