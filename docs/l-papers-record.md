# The machine-written papers: numbering, and the literature searches

The six L papers in `paper/` are numbered L1, L3, L4, L5, L6 and L8. Ten
were drafted in August 2026; L2 was merged into L1 as its Part II, L7 into
L5, L10 into L8, and L9 (the cut-count identity) was withdrawn after its
statement was found to be an instance of a published correspondence; its
content is `docs/proofs/cutcount-identity.md`. The retired numbers are not
reused.

Each paper's novelty section points here for what was searched and what was
found. These were web searches over the combinatorics and statistical-
mechanics literature, following named authors and citation chains, with full
text pulled where free. A search is not a proof of absence; the point of the
record is that the next search starts after this one. Papers that could not
be obtained are in `literature/MISSING.md`.

## The pass of 2026-08-18

| paper | result |
|---|---|
| L9 | the whole statement is published; withdrawn |
| L6 | the structural theorem and the defect identity are published for the square lattice; attributed, claims narrowed to the king column |
| L5 | an antecedent for the kernel method; cited |
| L1 (Part II, mod 3) | no collision; one method-adjacent body of work, cited with why it does not apply |
| L8 | nothing close found; the paper claims nothing new on its first half |
| L1 (Part I), L3, L4 | no collision on the material added since their earlier searches |

**L9, the cut-count identity.** Searched: connected-subgraph counting by
transfer matrix with `q^{components}` weights; the Fortuin–Kasteleyn
random-cluster and Potts spin representations; Blöte–Nightingale transfer
matrices; Hoshen–Kopelman cluster labelling; Jensen's algorithm. The identity
is an instance of the Fortuin–Kasteleyn/Potts correspondence: counting
connected subgraphs is the `q → 0`, `v = 1` content of the random-cluster
partition function, and evaluating `q^c` by colouring components is the
standard spin representation. The scan-order labelling descends from
Hoshen–Kopelman (1976). What is not in the literature is the window-bounded
scan-order form: that a window of `H+1` cells suffices under king adjacency,
and that the rule is exactly what one engine implements. That is what
`docs/proofs/cutcount-identity.md` keeps, as the licence for the second
enumerator.

**L6, perimeter gradings.** Searched: Asinowski–Barequet–Zheng and
Barequet–Magal on fixed perimeter defect; the polycube generalisation;
minimal-perimeter animals. Their slides
(`mat.univie.ac.at/~slc/wpapers/s79vortrag/asinowski.pdf`) state the defect
identity `k = e + 2f` (`e` the excess of perimeter cells, `f` the circuit
rank), which is L6's `k = 2c + t` with `c = f`, `t = e`; and the theorem
that for fixed `k` the generating function of polyominoes with perimeter
`2n+2−k` is rational with cyclotomic denominator. Their `A(n,2n+2) = 1` and
`A(n,2n+1) = 4(n−2)` are the square-lattice `k = 0, 1` rows. The king
column, the onset formula `k(k+1)/2 + 3`, the agreement of period, degree,
onset and leading coefficient between the two lattices through `k = 6`, the
coefficient triangle and the minimum end are not in the slides.

The ANALCO 2018 paper with the proofs, "Polycubes with small perimeter
defect" (Proc. ANALCO 2018, 93–100), was obtained the same day and is in
`literature/`. Its argument (perimeter as `6n − e − 2|E|`, rationality by
shrinking cuts, finiteness of pattern classes from bounds on excess, L- and
degree-1 cells, the handshake bound at degree 6) is stated in face-adjacency
terms throughout; the cut condition in particular fails under king
adjacency. So the shape of the argument transports and the theorem does not:
L6's king results are a separate derivation, and its square-lattice
statements are their theorem re-derived. Their §4 conjectures that for any
dimension and fixed `k` the top factor of the characteristic polynomial is
`(x−1)^{k+1}`, so the count is asymptotically `γ n^k`; the table in
`results/perimeter.md` has exactly that for every `k ≤ 6` on both lattices.
For the square lattice that is evidence for a published conjecture, for the
king lattice evidence for the same conjecture on a lattice their framework
does not reach.

**L5, convex polyplets.** Searched: Bousquet-Mélou and Fédou on the
convex-polyomino `q`-differential system; festoons; Klarner–Rivest and
Bender constants; `q`-Bessel zeros; Kotesovec's constants for
A067675/A067676. Bousquet-Mélou and Fédou, Discrete Math. 137 (1995) 53–75,
is the antecedent of L5's kernel section: the same object on the square
lattice, solved by a `q`-differential system, with the Klarner–Rivest
function as the denominator whose smallest positive zero gives the growth
constant; L5's control arm reproduces their constants. The area-moment
collision found earlier (Richard, arXiv:0704.0716; Enting–Guttmann 1989) is
cited in three places. Gouyou-Beauchamps and Leroux (FPSAC 2004, §2.3) have
L5's block decomposition and mirror equality for convex polyominoes on the
honeycomb lattice; L5 cites them at both and in its related work.

**L1 Part II, the mod-3 arithmetic.** Searched: congruences modulo powers of
3; Krattenthaler–Müller's method; Rowland–Yassawi's automata for diagonals of
rational functions modulo `p^α`; Smith normal forms of combinatorial
triangles; base-3 digit-product formulas. Rowland–Yassawi (J. Théor. Nombres
Bordeaux 27 (2015) 245–288) is the closest machinery and does not apply: L4
proves the height generating function is not D-finite, so it is not such a
diagonal. Nothing found on the spine cubic, the digit product or the
all-3-powers Smith normal form.

**L8, below the onset.** Searched: corrections and error terms to
fixed-height and bounding-box animal formulas; defects below a formula's
threshold; algebraic generating functions for leading coefficients of such
families. Nothing close. The negative is weak: the object is defined relative
to this project's own diagonal law.

**L1 Part I, L3, L4.** Only material added since their earlier searches was
looked at. For L3's BFS-frame encoding (the repaired proof of the
`5^5/4^4` bound) no king number was found; the Barequet group's improved
polyomino and polycube bounds, a 2025 convolutional bound and a 2025
polyiamond bound are square-lattice or polyiamond. L4 was not re-searched.

Two of the three collisions above came from pulling the full text of sources
already listed in `literature/MISSING.md`, not from new searches. Re-try that
file before searching again.

## The pass of 2026-08-23 over L8's second half

Five searches: lattice-animal correction terms below a threshold; "below the
threshold" exact corrections to polynomial formulas; Jensen and Guttmann
percolation-probability series with correction terms; polyomino transfer
matrix with exact error terms below the validity threshold; the finite-lattice
method with exact corrections and onset.

The near neighbour: Baxter and Guttmann, J. Phys. A 21 (1988) 3193, then
Jensen and Guttmann (`arXiv:cond-mat/9509121`, `cond-mat/9511084`) extend
directed-percolation series by the same manoeuvre, a finite-lattice
calculation exact only to some order, corrected by terms `d_{N,r}` so that a
smaller calculation reaches further. The ambient family is the finite-lattice
method (Enting; Jensen), and L8's method belongs to it.

The distinction L8 claims: in the percolation work the corrections are
conjectured and fitted (a Catalan ansatz), so the extended series is a
prediction; in L8 the correction `D_j(k)` is computed exactly by an
enumeration that reads neither the triangle nor `P_k`, and the number of
unknowns per level is proved (two per level, in Lean). Nothing found applies
a correction of this kind to bounding-box-height animal counts or corrects a
diagonal law to pin polynomial levels from below its onset.

Limits of this pass: web search only, five queries, no citation database. A
closer instance, if one exists, would likely cite Baxter–Guttmann, and that
citation graph was not crawled.
