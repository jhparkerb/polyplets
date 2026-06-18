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
  Fit on all 32 available exact terms (B_4 overflows u64 at n=32), clean integer
  coefficients, but NOT yet held-out-validated -- this is the wall the mod-p
  engine removes. See [[shelf]] / task #26.

## The order conjecture
The minimal recurrence order (= deg Q_H) is

    H:      1   2   3   4
    order:  1   3   7   15      = 2^H - 1

far below the boundary-state count D_H = 1, 5, 15, 39, ... (~2.6^H). Conjecture:
**deg Q_H = 2^H - 1**, the number of nonempty column-occupancy patterns of an
H-row strip -- suggesting the denominator is the characteristic polynomial of the
(2^H-1)-dimensional occupancy transfer matrix, with connectivity tracking
affecting only the numerator. Consequence: reaching height H's GF needs only
~2(2^H-1) terms, not ~2 D_H -- cheaper than feared. Unconfirmed past H=4; the
mod-p engine (unbounded terms, no overflow) is needed to test H>=5 (order 31+)
and to held-out-validate H=4.

## Next
Build the mod-p transfer-matrix engine: compute B_H(n) mod several primes to
2(2^H-1)+margin terms, Berlekamp-Massey mod p, CRT + rational reconstruction to
lift to the exact integer recurrence. Confirms H=4 and extends to higher H.
Cross-check every recovered GF against the diagonal B_H(H) = 3^(H-1).
