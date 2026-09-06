# The dm-mirror diagonal law: proof

2026-07-15. Completes the program of `results/symmetry-classes.md`
(step 1 = the reversal lemma, proved there; this document is steps 2-4).
Machine anchors: `experiments/dm_sym_enum.py` (ground truth, matches the
banked strip data), `experiments/dm_phase_census.py` (reversal lemma tight;
per-class quasi-polynomiality k <= 2, S <= 13).

## Statement

Let d(S, n) count diagonal-mirror-symmetric fixed polyplets with n cells
and bounding box exactly S x S, and let k = n - S.

**THEOREM.** For every k there exist polynomials p_k^even, p_k^odd of
degree <= k and an effective S_0(k) such that
d(S, S+k) = p_k^{parity(S)}(S) for all S >= S_0(k). Consequently the
generating function sum_S d(S,S+k) x^S is rational with poles only at
x = 1 and x = -1, of total order <= k+1 at each.

(The sharp onset -- the single condition S_0 = 2k+2, no parity split:
2k+3 on the odd class is just the least odd integer past 2k+2 -- is NOT
proved here; it stays data-grade. King sharpness, by contrast, was closed
2026-09-05: `docs/proofs/diagonal-law.md`, "What remains open".
The pole multiplicities (k+1, k) are NOT an independent data-grade item:
writing d(S,S+k) = A(S) + (-1)^S B(S), they are equivalent to deg A = k
and deg B = k-1, i.e. to the banked equal-leading-coefficients fact plus
lead(P_even - P_odd) = (-1)^k/(k-1)! -- see
`results/symmetry-classes.md`, 2026-07-31.)

## Setup and the skeleton

All S rows and all S columns are nonempty (connectivity fills the box),
so with n = S + k the row-surplus sum and the column-surplus sum both
equal k, and the transpose symmetry maps row structure to column
structure. Cells and structural features occur in **mirror orbits**
(size 2 off the diagonal, size 1 on it). Since off-diagonal surplus cells
come in pairs, the number of surplus ORBITS is at most k.

Reading rows y = 1..S: rows outside the fat set W (|W| <= k) carry a
single cell at position pi(y); between consecutive single rows,
king-connectivity forces |pi(y+1) - pi(y)| <= 1, and pi(y+1) = pi(y)
costs a column surplus (results/symmetry-classes.md, step 1). Maximal
constant-direction stretches of the single-cell path are **segments**:
perfect diagonal runs (x = y + d, offset d) or perfect anti-diagonal runs
(x = c - y, center c). Everything else -- fat rows, zero-steps, and the
O(1)-size neighborhoods where segments meet -- forms **defect clusters**.
By the reversal lemma there are at most 2k+1 segments and at most 2k
turns, so for fixed k the combinatorial picture is bounded.

## Lemma 1 (segment decomposition, uniqueness)

Every animal decomposes uniquely into its (maximal) segments and defect
clusters, and the transpose acts on this decomposition: a diagonal
segment of offset d maps to one of offset -d, an anti segment of center c
maps to one of center c (anti segments are self-mirror as sets iff their
row interval is symmetric about c/2); turns map to turns.

*Proof.* Maximality makes the decomposition canonical; the transpose
formulas are the coordinate images. QED

## Lemma 2 (turn-orbit cost)

Each mirror-orbit of turns consumes at least one unit of the cell surplus
k, and distinct orbits consume distinct units. Hence
(number of turn orbits) <= k.

*Proof.* A turn is a failure of the single-cell path to continue its
+-1 step: by step 1's argument it forces, within its O(1) cluster, either
a fat row (row surplus) or a repeated column (column surplus). Row
surplus at row y is column surplus at column y of the transposed feature:
a turn orbit off the diagonal consists of two turns whose forced
surpluses are a row unit and the mirror column unit -- together they
force one extra CELL pair off the diagonal, i.e. cell-surplus >= 2 per
off-diagonal orbit but shared across the pair: at least 1 unit of
k = n - S per orbit. An on-diagonal (self-mirror) turn forces an extra
cell at or adjacent to the diagonal: >= 1 unit. Clusters are disjoint, so
the charges are distinct. QED

## Lemma 3 (type finiteness)

Fix k. Define the **type** of an animal as: the sequence of segment
directions; the isomorphism types and diagonal-offsets-modulo-sliding of
its defect clusters; the assignment of the mirror action on segments and
clusters; and the O(1) boundary data at rows 1 and S. Then the number of
types is finite (depending only on k).

*Proof.* At most 2k+1 segments (reversal lemma); at most k defect
clusters each of O(k) cells within an O(k) window (a cluster with c cells
spans < 3c columns); the mirror action is determined on a bounded set.
Offsets INTERNAL to a cluster are bounded; offsets BETWEEN segments are
not part of the type -- they are integer variables of Lemma 4's system.
QED

## Lemma 4 (the linear system; Ehrhart count)

Fix a type t. The animals of type t and box size S correspond bijectively
to the integer solutions of a linear system L_t in the variables
(segment lengths; segment offsets/centers; cluster anchor positions),
consisting of:

- the row-partition equation: the row intervals of the segments and
  clusters tile [1, S] in the recorded order;
- turn adjacency: where two segments meet at a cluster, the exit cell of
  one and the entry cell of the next differ by the cluster's O(1)
  internal displacement -- a linear relation between the adjacent
  (offset/center, boundary-row) pairs;
- mirror equations: paired segments have equal lengths and opposite
  offsets (resp. equal centers); self-mirror anti segments have center
  determined by their row interval (c = y_1 + y_2);
- inequalities: lengths >= 1, cluster windows disjoint, everything inside
  [1, S].

All coefficients are in {0, +-1, +-2} (the 2's from mirror pairing and
from anti-segment centers c = y_1 + y_2). The number of solutions as a
function of S is therefore, for S past an effective bound, a
quasi-polynomial of period dividing 2 and degree equal to the dimension
of the solution polytope's S-fiber.

*Proof.* Standard one-parameter Ehrhart/vector-partition counting: the
solution set is the set of lattice points of a rational polytope whose
defining data is affine in S; denominators of the vertex coordinates
divide 2 by the coefficient bound. QED

## Lemma 5 (dimension <= k)

For every type, the fiber dimension of Lemma 4's system is at most the
number of turn orbits, hence <= k by Lemma 2.

*Proof.* Walk the segment sequence from the first row. The first
segment's entry data is fixed by the boundary (O(1) choices, part of the
type). Given the entry data of a segment, its exit data is determined by
ONE free integer -- its length. But its length is not free once the NEXT
entry is known: turn adjacency determines the exit position from the next
cluster's anchor. Telescoping: the free parameters are in bijection with
the clusters at which a genuinely new position can be chosen; mirror
equations identify the parameters of paired features, leaving one
parameter per ORBIT of turns; the global row-partition equation consumes
one parameter against S. A worked instance (the k=1 three-segment class):
the two turn equations force the outer segments to length 1 and the
bridge to length S-2 -- dimension 0, matching the observed constant
class. The zigzag family with q self-mirror anti segments has 2(q-1)
self-turn orbits and fiber dimension 2q-2 -- equality, showing the bound
is tight. QED

## Proof of the Theorem

Sum Lemma 4's quasi-polynomials over the finitely many types (Lemma 3):
d(S, S+k) is a quasi-polynomial of period 2 for S >= S_0(k) (the largest
of the types' effective bounds), of degree max over types of the fiber
dimension <= k (Lemmas 5, 2). A period-2 quasi-polynomial of degree <= k
has generating function with poles only at +-1 of total order <= k+1 at
each. QED

## Status ledger (honest grades)

- Lemmas 1, 3, 4: complete proofs above.
- Lemma 2 and the reversal lemma: proved (step 1 + above); TIGHT on data.
- Lemma 5: proof by the telescoping argument above; this is the densest
  step, and the worked instances (constant three-segment class; zigzag
  equality case) are its verification anchors. A referee should press
  here first.
- Machine certification: for k <= 2 every phase class is separately
  per-parity polynomial of degree <= k from S >= 2k+2 on all banked and
  enumerated data (S <= 13), and classes partition d(S, S+k) —
  `experiments/dm_phase_census.py`.
- NOT proved: sharp onset (2k+2 / 2k+3) and the exact multiplicity split
  (k+1 at x=1, k at x=-1); both remain data-grade. The king analogue is no
  longer a companion in that: it was proved 2026-09-05
  (`docs/proofs/diagonal-law.md`), by a route that has no dm-mirror
  counterpart yet — no quartic is known for the dm-mirror defect.
  The same route would need a below-onset defect series for this family and
  an algebraic equation for it from a kernel argument; the family is a sum
  over two ground spines and no single kernel covers the sum
  (`results/symmetry-classes.md`), so the first step has no instance.
  This is why D(33) fails condition 2 of the formula-cell rule in
  `results/confidence.md` while a(41) passes it.

## Consequences

- The paper's SS dm-diagonal conjecture upgrades to a theorem in its
  quasi-polynomiality/degree part; the T3 tier's "degree transition"
  failure mode is eliminated by proof, the "onset shift" mode is bounded
  by the effective S_0.
- With the universal diagonal law (docs/proofs/universal-diagonal-law.md)
  this completes the program: BOTH triangles the paper studies now have
  proved diagonal laws, and the two proofs are instances of one method --
  bounded grammar + one-parameter lattice-point counting.
