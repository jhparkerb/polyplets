# S2 remaining work: the efficient symmetric enumerator

The Burnside foundation (oracle/g1_naive.py count_symmetry, gate_s2.py) is
done and validated. It establishes:

    Free(n)      = (1/8)[ Fixed(n) + 2 R90(n) + R180(n) + 2 H(n) + 2 D(n) ]
    OneSided(n)  = (1/4)[ Fixed(n) + 2 R90(n) + R180(n) ]

where R90/R180/H/D are counts of fixed animals invariant under a 90deg / 180deg
rotation / axis-parallel mirror / diagonal mirror. Fixed(n) comes from G2;
the four symmetric counts are all that remain.

## Why this unlocks a submission immediately
Symmetric counts grow ~ sqrt(growth)^n ~ 2.6^n, far below Fixed's ~6.7^n, so
they are never the bottleneck. Free(n) is gated ONLY by Fixed(n):
- Free(18) needs the four symmetric counts at 18 -> a NEW term (A030222 ends at 17)
- Free(19) follows the moment the a(19) fixed campaign verifies.

## The orbit-graph reduction (the design) -- WRONG, DO NOT BUILD
*Rejected June 13, 2026 after working through E1; kept here as a documented
dead end so it is not re-attempted.*

The tempting claim was: g-symmetric animals of size n <-> connected subgraphs
of the ORBIT GRAPH (nodes = <g>-orbits of cells, weight = orbit size, edge if
any cells king-adjacent), countable with the E0 subgraph counter.

**This overcounts.** "Connected in the orbit graph => connected cell animal"
is FALSE. The quotient map by g is 2-to-1 (4-to-1 for R90); a connected set in
the quotient lifts to a connected animal only if it contains the fixed point
or winds around it -- otherwise the lift is two (or four) disjoint copies.

Minimal counterexample (R180 about the origin): the orbit {(1,0),(-1,0)} is a
single orbit-graph node, so E0 scores it as a valid weight-2 "connected"
symmetric animal. But the two cells are Chebyshev-distance 2 apart -- the
cell set is DISCONNECTED, not a polyplet. Concretely the method gives nonzero
R180C(2) where the truth is R180C(2)=0 (the four 2-cell symmetric dominoes are
all R180M/R180V, about edge/vertex midpoints, never cell-centered). The
orbit-graph count is an injection that overcounts, and patching it needs
winding/monodromy tracking -- not worth it.

## The correct method: direct symmetric generation
Grow connected symmetric animals cell-by-cell (Redelmeier-style), adding each
cell's orbit-image(s) at the same time, tracking the ACTUAL cell-connectivity
of the full animal, anchored on a canonical (e.g. minimum) cell to count each
once. This is the rare-object generation Shirakawa/Redelmeier use; symmetric
animals are ~2.6^n so it reaches n>=19 cheaply. The subtle cases to get right
(validate each against count_symmetry at small n):
- R180C / R90C: animal may or may not contain the center cell; the "winding
  around an empty center" animals (e.g. a symmetric ring) are real and must be
  generated -- this is exactly what the orbit-graph shortcut got wrong.
- R180M/V, R90V: no center cell (even-n / 4|n only); pairs/quads only.
- H/D mirrors: cells on the axis are self-paired (weight 1); off-axis paired.
  Shirakawa instead used a half-region transfer matrix with axis weighting for
  the mirror classes -- an alternative worth considering.

E0 (cpp/sym/subgraph_count.cpp) is a correct general utility but is NOT on the
S2 path; leave it as-is. Build the symmetric generator next, oracle-validated
at every placement.

### Concrete correct design (worked out June 13, 2026)
The clean insight that makes generation correct: **symmetry makes the partner
connect for free.** If we add a lower-half cell c that is king-adjacent to
some cell d already in the (symmetric) animal A, then by symmetry rho(c) is
adjacent to rho(d), and rho(d) is also in A -- so rho(c) connects too. Hence
growing one "half" while requiring each new cell to touch the current animal
keeps the *full* animal connected automatically. That is exactly what the
orbit-graph shortcut threw away (it never checked real adjacency to A).

Anchoring (count each animal once): the lower half is L = { c in A : c < rho(c)
lexicographically }; every cell of A is in L or rho(L) (or is the center).
min(A) lies in L. Generate L by Redelmeier rooted at min(A), adding only
lower-half cells > min(A) that are king-adjacent to the current full animal.

R180 needs two sub-generators (to handle the center as an optional bridge):
- **(b) no center:** seed = a lower-half cell; A0 = L ∪ rho(L); require A0
  connected throughout; anchor at min(A0). Used for M/V (no center cell exists)
  and for center-free C animals.
- **(a) center-containing (C only):** seed = {center cell}; grow lower-half
  cells adjacent to A1 = {center} ∪ L ∪ rho(L); Redelmeier-from-fixed-seed
  counts each once. This is the ONLY way to get "ring" animals where the two
  halves join *only* through the center -- the case the orbit graph missed.
R90 is the same idea with 4-cell orbits (quarter as the fundamental domain,
center optional); H/D mirrors with 2-cell orbits and self-paired axis cells
(or Shirakawa's half-region weighted TMA).

Validate (a)+(b) summed per placement against count_symmetry's Fix(g) at small
n; the oracle distinguishes overcount (spurious disconnected sets) from
undercount (missed ring/winding animals), so it pins down which sub-generator
is wrong.
