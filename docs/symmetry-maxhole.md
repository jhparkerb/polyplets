# Maxhole by symmetry: the optimum is always symmetric (and M_asym has no clean formula)

Splitting the max hole area M(n) (the proven diamond optimum, `docs/diamond-optimality.md`)
by the symmetry of the enclosing polyplet (`experiments/b2_sym_maxhole.py`, exhaustive,
n≤10):

| n | M(n) | M_asym(n) | M_sym(n) | M(n−1) | M_asym = M(n−1)? |
|---|-----:|----------:|---------:|-------:|:----------------:|
| 4 | 1 | 0 | 1 | 0 | yes |
| 5 | 1 | 1 | 1 | 1 | yes |
| 6 | 2 | 1 | 2 | 1 | yes |
| 7 | 3 | 2 | 3 | 2 | yes |
| 8 | 5 | 3 | 5 | 3 | yes |
| 9 | 6 | 5 | 6 | 5 | yes |
| **10** | **8** | **7** | **8** | **6** | **NO** |

## The one clean fact (survives)
**The maxhole optimum is always symmetric**: M_sym(n) = M(n) at every n through 10. The
hole-area maximizer (the L¹ diamond) is D4-symmetric, so restricting to symmetric polyplets
loses nothing. There *is* a real symmetry premium — asymmetric polyplets enclose strictly
less than M(n) for n≥6.

## The tempting conjecture (REFUTED at n=10)
`M_asym(n) = M(n−1)` held for all n≤9 and looked clean — but it was a small-n coincidence.
At **n=10, M_asym(10) = 7, not M(9) = 6**: breaking the diamond's symmetry costs only one
cell of enclosure here (8→7), not two (8→6). The constructive lower bound `M_asym(n) ≥
M(n−1)` still holds, but equality fails, so M_asym lags M(n) by an *irregular* amount:

    M(n)       : 0,0,0,1,1,2,3,5,6,8   (n=1..10)
    M_asym(n)  : 0,0,0,0,1,1,2,3,5,7
    premium    : 0,0,0,1,0,1,1,2,1,1   <- no clean formula

So `M_asym(n)` has **no simple closed form** on current evidence. Worth keeping only as: (a)
the clean "optimum is always symmetric" fact, and (b) a cautionary example — a 6-term run
(n=4..9) of agreement was not the law. (This is why the n=10 brute-force extension was worth
running: it killed a premature conjecture.)
