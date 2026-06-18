# Fixed-height generating functions for polyplets

Each fixed-height row B_H(n) (number of fixed polyplets of n cells with
bounding-box height exactly H) is C-finite: it satisfies a constant-coefficient
linear recurrence and has a rational generating function
G_H(x) = sum_n B_H(n) x^n = P_H(x) / Q_H(x). Recovered by Berlekamp-Massey over Q
from terms produced by the column transfer matrix (`build/tma square8 N
--only-height H`); recovery tool `gf/recover.py`.

## Exact GFs (validated)
- **H=1:** G = x / (1 - x).            (B_1(n) = 1 for all n)
- **H=2:** G = (3x^2 + x^3) / (1 - 3x + x^2 + x^3).
- **H=3:** G = (9x^3 - 8x^4 - 2x^5 + 4x^6 + x^7)
             / (1 - 7x + 15x^2 - 9x^3 - 3x^4 + 5x^5 - x^6 - x^7).

H=1,2,3 are validated: the recurrence, fit on a prefix, reproduces every
remaining term out to n=36 and matches the independently-computed B_H(19).

- **H=4:** order-15 recurrence, denominator
  1 - 11x + 41x^2 - 49x^3 - 39x^4 + 113x^5 + 7x^6 - 155x^7 + 57x^8 + 67x^9
    - 63x^10 - 19x^11 + 17x^12 - x^13 - 5x^14 - x^15.
  Now held-out-validated by the independent big-integer engine (below).

## The order sequence (and a debunked conjecture)
The minimal recurrence orders (= deg Q_H), validated:

    H:      1   2   3   4   5   6
    order:  1   3   7   15  35  67

An EARLIER conjecture that this is 2^H - 1 (1, 3, 7, 15, ...) was **FALSE** -- it
matched only by coincidence through H=4, then breaks (H=5 is 35, not 31; H=6 is
67, not 63). It was caught precisely by recomputing at higher H with an
independent implementation. The orders stay well below the boundary-state count
D_H = 1, 5, 15, 39, 98, 246, but follow no clean closed form yet; the sequence
1, 3, 7, 15, 35, 67 is not in OEIS.

## Independent verification
`gf/fixed_height.py` is a from-scratch big-integer fixed-height king transfer
matrix (no overflow, no pruning -- so no modular-reduction subtleties). It:
- reproduces the C++ engine's B_H(n) exactly for n<=19 at every H (cross-check);
- held-out-validates the recovered recurrence for H=1..6 (the recurrence,
  recovered by Berlekamp-Massey, reproduces every term beyond its order);
- thereby confirms H=4 (order 15) and disproves 2^H-1 at H=5,6.

## Next
A mod-p C++ transfer matrix (counts mod several primes, Berlekamp-Massey mod p,
CRT + rational reconstruction) extends the GFs to higher H than the Python engine
reaches in reasonable time. NOTE the mod-p trap: the prune's "is this count
nonzero?" test breaks under modular reduction (a true count = 0 mod p reads as
absent), so the reachable-size info must be tracked structurally, separate from
the mod-p magnitudes. Cross-check every recovered GF against the diagonal
B_H(H) = 3^(H-1).
