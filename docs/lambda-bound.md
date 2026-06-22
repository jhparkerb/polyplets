# A rigorous upper bound on the polyplet growth constant

**Result.** Let `a(n)` be the number of fixed polyplets (king-/8-connected lattice
animals, A006770) with `n` cells, and `λ = lim_{n→∞} a(n)^{1/n}` its growth
constant. Then

    λ ≤ 7^7 / 6^6 = 823543 / 46656 = 17.6529…

This is the king-graph analogue of the classical spanning-tree (Eden) bound
`λ_polyomino ≤ 3^3/2^2 = 6.75` for ordinary (edge-connected) polyominoes.

## Proof

**Step 1 — a polyplet injects into an embedded king-tree.**
Every fixed polyplet `P` is connected in the king graph (each cell adjacent to its
≤ 8 neighbours N, S, E, W and the four diagonals). Root `P` at its
lexicographically minimal cell `r` and take the breadth-first spanning tree of the
king graph of `P` from `r`, breaking ties by a fixed neighbour ordering. This
assigns to `P` a *rooted embedded king-tree* `T_P`: a set of `n` cells (the nodes)
together with `n−1` tree edges, each edge a king-step between two cells.

The map `P ↦ T_P` is injective: the node set of `T_P` is exactly the cell set of
`P`, so `P` is recovered from `T_P`. Hence

    a(n) ≤ #{ rooted embedded king-trees on n cells, anchored at the origin }.    (1)

**Step 2 — drop the no-overlap constraint (overcount).**
Encode a rooted embedded king-tree abstractly: each non-root node stores the
king-direction of the edge to its parent. Two children of the same node occupy
distinct cells, hence point in distinct directions; and no child can point in the
direction *back toward the parent* (that cell is the parent, already in the tree).
So each node has at most **7** available directions for its children (8 minus the
toward-parent direction; the root has 8).

Counting these direction-labelled abstract trees **ignores** the global
requirement that distinct nodes occupy distinct cells — every embedded tree maps
to such an abstract tree, but not conversely, so this only over-counts:

    #{ embedded king-trees } ≤ #{ direction-labelled abstract trees }.            (2)

**Step 3 — count the direction-labelled trees.**
Let `T(x) = Σ t_n x^n` count rooted direction-labelled trees by their number of
nodes, where each node independently may or may not place a child in each of its 7
admissible directions (each present child rooting an independent subtree). Then a
node contributes a factor `(1 + T)` per admissible direction, so

    T(x) = x (1 + T(x))^7                                                         (3)

(the root, with 8 directions, contributes a bounded prefactor `x(1+T)^8` that does
not affect the exponential growth rate).

The dominant singularity `x_c` of `T` is where the defining equation has a double
root, i.e. where `d/dT [ x = T/(1+T)^7 ] = 0`:

    d/dT [ T (1+T)^{−7} ] = (1 − 6T)(1+T)^{−8} = 0  ⟹  T = 1/6,
    x_c = (1/6) / (7/6)^7 = 6^6 / 7^7.

By Pringsheim / the exponential-growth formula, `t_n ≍ x_c^{−n}` up to
sub-exponential factors, so `#{direction-labelled trees on n nodes} ≤ C·(7^7/6^6)^n`.

**Conclusion.** Chaining (1)–(3),

    a(n) ≤ C · (7^7/6^6)^n  ⟹  λ = lim a(n)^{1/n} ≤ 7^7/6^6 = 17.6529… ∎

(The limit defining `λ` exists by supermultiplicativity `a(m)·a(n) ≤ a(m+n+O(1))`,
proved as for polyominoes by king-adjacent concatenation; the same
supermultiplicativity makes each `a(n)^{1/n}` a rigorous *lower* bound, so our
exact data gives `λ ≥ a(20)^{1/20} ≈ 5.6` and the ratios `a(n)/a(n−1) ≈ 6.5`
[increasing] locate the true value near 7.)

## Remarks

- **Generality.** The argument bounds `λ` for site animals on *any* lattice of
  coordination number `z` by `(z−1)^{z−1}/(z−2)^{z−2}`: `z=4` → 6.75 (polyominoes),
  `z=6` (triangular) → `5^5/4^4 = 12.21`, `z=8` (king) → 17.65. Only Step 1's
  spanning-tree injection and Step 2's parent-direction exclusion are used.
- **Looseness.** `17.65` is ~2.5× the empirical `λ ≈ 7`; the slack is entirely in
  Step 2's discarded no-overlap constraint. It tightens systematically by forbidding
  longer-range overlaps in the tree, via a transfer matrix on consecutive edge
  directions.
- **Tightening (grandparent step), computed.** A child also never coincides with the
  **grandparent** cell `G = N−u−w` (`u` = parent→node, `w` = grandparent→parent king
  vectors): that forbids child direction `c = −(u+w)` exactly when `u+w` is itself a
  king-step. This is a 64-state system `T_{u,w}=x·∏_{c allowed}(1+T_{c,u})`; 24 of 64
  states drop to 6 child-directions (avg 6.625), and its growth constant gives
  **λ_polyplet ≤ 16.63** (`x_c ≈ 0.060130`, `experiments/lambda_tighten.py`) — a
  rigorous improvement on 17.65 (valid trees ⊆ grandparent-constrained ⊆ all trees).
- **Deeper edge-history, computed** (`experiments/lambda_tighten_deep.py`). Forbidding the
  child cell from coinciding with any of the last `d` ancestors (state = length-`d`
  direction history; still a rigorous over-count, monotone tighter in `d`) gives, for
  d = 1,2,3,4: **17.65, 16.63, 16.09, 15.83**. Per-step gains halve (1.02, 0.54, 0.27 —
  ratio ≈ ½), so the ancestor-exclusion family **saturates at ≈ 15.56**, still ~2× the
  true λ≈7.1 — it never excludes *non-ancestor* (sibling/cousin) overlaps. So **d=4 gives
  a rigorous `λ_polyplet ≤ 15.83`**, a real but modest improvement on 16.63, and the
  method has a hard floor near 15.5. A full Klarner–Rivest twig/perimeter treatment (which
  sharpens the polyomino bound 6.75 → 4.65) is where the next *substantial* gain lives —
  not more history.
- **Status.** Rigorous and, as far as we know, the first explicit upper bound on
  the polyplet growth constant. Candidate for the paper's asymptotics section.
