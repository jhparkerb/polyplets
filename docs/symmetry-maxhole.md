# A symmetry premium for maxhole: M_asym(n) = M(n−1)

Splitting the max hole area M(n) (the proven diamond optimum, `docs/diamond-optimality.md`)
by the symmetry of the enclosing polyplet (`experiments/b2_sym_maxhole.py`, exhaustive
n≤9):

| n | M(n) | M_asym(n) | M_sym(n) | M(n−1) |
|---|-----:|----------:|---------:|-------:|
| 4 | 1 | 0 | 1 | 0 |
| 5 | 1 | 1 | 1 | 1 |
| 6 | 2 | 1 | 2 | 1 |
| 7 | 3 | 2 | 3 | 2 |
| 8 | 5 | 3 | 5 | 3 |
| 9 | 6 | 5 | 6 | 5 |

Two facts, both clean:

1. **The optimum is always symmetric**: M_sym(n) = M(n) at every n. The hole-area maximizer
   (the L¹ diamond) is D4-symmetric, so restricting to symmetric polyplets loses nothing.

2. **Conjecture: `M_asym(n) = M(n−1)`** — the best *asymmetric* (trivial-stabilizer)
   n-cell polyplet encloses exactly what the symmetric (n−1)-cell optimum does. Verified for
   all n≤9. M_asym(n) = 0,0,0,0,1,1,2,3,5 (n=1..9), i.e. M(n) shifted by one.
   - **Lower bound `≥` is constructive** (provable): take an (n−1)-cell shape achieving
     M(n−1) and add one cell on the outer boundary that breaks every symmetry without
     touching the hole; the result is an asymmetric n-cell polyplet enclosing M(n−1).
   - **Upper bound `= M(n−1)`** is the open half: breaking the diamond's symmetry costs you
     a full cell of enclosure, never less. Equivalently M(n) is attained *only* near the
     symmetric diamond, and any genuinely asymmetric shape is at least one cell behind.

So the "symmetry premium" is M(n) − M(n−1) ∈ {0,1}; an asymmetric enclosure runs exactly one
diamond-step behind. A small, clean companion to the maxhole story
(`M(n)=⌈⌊(n−2)²/4⌋/2⌉`, so the conjecture is `M_asym(n)=⌈⌊(n−3)²/4⌋/2⌉`).
