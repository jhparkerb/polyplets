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

## The orbit-graph reduction (the design)
A g-symmetric animal is a union of <g>-orbits of cells. Claim: g-symmetric
animals of size n <-> connected subgraphs of the ORBIT GRAPH with total
cell-weight n, where nodes are cell-orbits under <g>, edges join orbits whose
cells are (king-)adjacent, and node weight = orbit size (1, 2, or 4).
(Connected orbit graph <=> connected cell animal, since g maps any connecting
path to another; the projection/lift argument both ways.)

So each symmetric count = weighted connected-subgraph enumeration on a quotient
lattice = Redelmeier on a different graph. Cases (Mason placement matters):
- R180: center on cell (one weight-1 node, odd n possible) or on vertex/edge
  midpoint (all weight-2, even n only).
- R90:  center on cell or on vertex; weight-4 nodes + center.
- H/D:  axis through cells (weight-1 nodes on the axis) or between cells
  (all weight-2). Diagonal vs axis-parallel differ on the king lattice.

Implementation = a small per-case quotient neighbor structure feeding a
weighted Redelmeier. Validate every case against count_symmetry (the oracle)
at small n before trusting high-n output. Comparable care to the square-8
transition; deserves its own focused pass.
