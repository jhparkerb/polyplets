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

## The order sequence (and TWO debunked conjectures)
The minimal recurrence orders (= deg Q_H), validated three independent ways:

    H:      1   2   3   4   5   6    7    8
    order:  1   3   7   15  42  106  278  711

Two wrong guesses were caught along the way -- a cautionary tale about reading
patterns off too few data points:
1. **2^H - 1** (1, 3, 7, 15, 31, 63): matched by coincidence through H=4, then
   wrong. Caught by recomputing at higher H with an independent engine.
2. **1, 3, 7, 15, 35, 67**: ALSO wrong. These came from Berlekamp-Massey on too
   few terms (~2(2^H-1)) -- underdetermined, so BM returned a spurious low-order
   recurrence that fit the available terms but not the true sequence. Caught by
   the mod-p engine with an ADAPTIVE term count (grow N until the recovered order
   sits well below N/2).

The true orders grow like ~0.45 * D_H (the boundary-state count D_H = 1, 5, 15,
39, 98, 246, 624, 1604), follow no clean closed form, and 1,3,7,15,42,106,278,711
is not in OEIS.

## Full generating functions, H=1..8
The complete rational GFs G_H(x) = P_H(x)/Q_H(x) -- BOTH numerator and denominator
-- are recovered and full-GF-validated (the series expansion of P/Q reproduces the
engine's B_H(n) for all n) for H=1..8. The exact coefficient lists are in
`results/fixed_height_gfs.txt` (small ones, H<=4, also shown above). The numerator
begins at x^H (B_H(n)=0 for n<H) and its leading coefficient is B_H(H)=3^(H-1).
Coefficient magnitudes grow fast -- max|coeff| roughly squares per height
(~1e11 at H=6, ~5e55 at H=8) -- so CRT needs a large prime pool (the recovery
uses 40 moduli near 2^31).

## Engines and verification (three independent implementations)
- `build/tma --only-height H` -- the production column transfer matrix (exact
  u64; overflows past ~n=28 at H=5, the original term wall).
- `gf/fixed_height.py` -- from-scratch big-integer transfer matrix (no overflow,
  no pruning). Cross-checks tma exactly. NOTE its built-in order recovery is
  UNRELIABLE (its N heuristic assumed order ~ 2^H-1, too few terms) -- use it as a
  sequence generator / cross-check, not for orders.
- `build/gf_modp` + `gf/modp_recover.py` -- the mod-p engine: counts mod several
  primes (no overflow, unbounded terms), Berlekamp-Massey mod p with adaptive N,
  CRT to lift the exact integer recurrence, validated against a fresh prime AND
  shown to annihilate the big-integer engine's exact sequence. This is the
  authoritative tool for orders/GFs. (Watch for composite "primes": 2147483479 is
  composite and silently corrupts the modular inverse.)

All three agree on B_H(n) wherever each is valid; the orders above are confirmed
by mod-p+CRT and by annihilating the independent big-int sequence. Every recovered
GF also reproduces the diagonal B_H(H) = 3^(H-1).
