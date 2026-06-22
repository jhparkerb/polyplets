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
