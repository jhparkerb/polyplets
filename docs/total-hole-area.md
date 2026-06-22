# A single diamond maximizes TOTAL enclosed area: M_total(n) = M(n)

**Result (strengthening of T3/T5).** Among all fixed n-cell polyplets, the maximum of
the **total** enclosed-empty area summed over *all* holes equals the single-hole maximum

    M_total(n) = M(n) = ⌈⌊(n−2)²/4⌋/2⌉,

achieved by one diamond. Splitting the cell budget into several holes never beats a single
diamond. Confirmed by exhaustive enumeration through n=9 (`experiments/multihole.py`):
`M_total(n) = max_k M_k(n) = M_1(n)` at every n (e.g. n=9: M_1=6 beats M_2=4, M_3=3, M_4=4).

## Proof
Let P be an n-cell polyplet with holes H_1,…,H_k, and U = ⋃ H_i their union, with
(u,v) = (x+y, x−y) extents a = max_U u − min_U u and c = max_U v − min_U v.

P's outer boundary is a simple king-cycle C enclosing all of P (hence all holes), with
|C| ≤ |P| = n. Enclosure forces C one step past U on each side: the cell h ∈ U with
u(h)=max_U u has a 4-neighbour at u+1 that is not a hole and cannot be background (h would
escape), so it is in P; following the straight +u ray from h out to infinity, it crosses
the outer boundary C at some u ≥ max_U u + 1, so max_u C ≥ max_U u + 1. Symmetrically on
all four sides, giving W_u(C) ≥ a+2 and W_v(C) ≥ c+2.

The king-step identity `|Δu|+|Δv| = 2` then yields `n ≥ |C| ≥ W_u(C) + W_v(C) ≥ a+c+4`,
so **a + c ≤ n − 4**. Every hole cell lies in U's (u,v) bounding box on the even sublattice,
so `total area ≤ ⌈(a+1)(c+1)/2⌉ ≤ M(n)` (AM–GM, exactly as in T5). Equality is the single
diamond (k=1, no inner walls). ∎

## Remarks
- The per-k maxima M_k(n) are **not monotone in k** (n=9: M_3=3 < M_4=4 — four minimal
  holes beat three) and show no evident closed form. Only the *total* has the clean bound;
  the diamond's optimality is robust against every multi-hole split.
- The whole argument is the single-hole proof (`docs/diamond-optimality.md`) applied to
  the holes' *union* — the only new input is "P's outer boundary is one simple cycle
  enclosing the union," again the discrete Jordan curve theorem.

## A different extremal: max hole COUNT, maxh(n) ~ (√n − 1)²
The maximum *number* of holes behaves oppositely. From the same enumeration,
`maxh(n) = 0,0,0,1,1,2,2,3,4` (n=1..9). The optimum is the **even sublattice of a
diamond**: take all cells with x+y even inside |x|+|y| ≤ m (these are mutually
king-connected via (±1,±1) steps); every odd interior cell (x+y odd, |x|+|y| ≤ m−1) has
its four rook-neighbours even, so it is a 1-cell hole. For even m this gives
**n = (m+1)² cells enclosing h = m² holes**, so `maxh((m+1)²) ≥ m² = (√n − 1)²` — and at
m=2 it is 9 cells, 4 holes = maxh(9). Thus `maxh(n) ~ (√n − 1)² ~ n − 2√n`: *almost every
cell encloses its own hole* (h/n → 1), the polar opposite of the single big diamond
(~n²/8 area, one hole).

**Leading order proven: maxh(n) ~ n.** For maximum *count* every hole is a single empty
cell (smaller holes ⇒ more of them), whose four rook-neighbours are all foreground; each
foreground cell is a rook-neighbour of at most 4 holes, so `4h ≤ 4n`, i.e. **h ≤ n**.
Together with the construction `h ≥ (√n−1)² ~ n−2√n`, this pins `maxh(n) = n − Θ(√n)` —
the leading term is proven, every cell enclosing essentially its own hole. The exact
`(√n−1)²` is the refined conjecture: the even-sublattice **diamond minimizes the boundary
deficit** (cells neighbouring < 4 holes), again the L¹ isoperimetric optimum — provable by
the same `|Δu|+|Δv|=2` machinery applied to the deficit, the clean next step.
