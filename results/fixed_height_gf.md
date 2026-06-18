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

## Structure of the GFs: coefficients vs. spectrum (2026-06-18)
Do the GF coefficients have structure? A clean dichotomy:
- **Coefficients: none.** Q_H is not palindromic/anti-palindromic (no naive
  reciprocity), has content 1 (primitive), and there is NO inversion relation
  B_H(-n) = eps * B_H(n-c) (tested H=2..6, eps=+/-1, all shifts: none). The
  coefficients are determined algebraic invariants (principal-minor sums of the
  transfer matrix) but arithmetically wild -- the shadow of the full sequence's
  believed non-D-finiteness. (Known polyomino/animal inversion relations are
  PERIMETER/anisotropic phenomena, not single-variable area GFs like these.)
- **Spectrum: rich.** The smallest pole is 1/lambda_H; the per-height growth
  constants climb monotonically toward lambda_king ~ 7.10:
    H:        1   2       3       4       5       6       7
    lambda_H: 1   1+sqrt2 3.4437  4.1823  4.7178  5.1153  5.4176
  lambda_2 = 1+sqrt(2) exactly (sympy). The dominant root is real at every H
  (Perron-Frobenius; the transfer matrix is nonnegative), and a growing fraction
  of roots sit inside the unit disk. (H>=8 full root sets are numerically nasty --
  degree 711, coeffs ~1e55; np.roots and mpmath.polyroots both choke. Get
  lambda_H from the ratio B_H(n)/B_H(n-1) instead.)

## The per-height growth constants lambda_H, and a factor-lifetime law (2026-06-18)
lambda_H = 1/(smallest pole of G_H) is the growth rate of height-exactly-H
polyplets as n->infinity. Computed by power iteration on the recurrence (robust;
roots of the big Q_H are numerically nasty). Values H=2..9:

  H:        2        3        4        5        6        7        8        9
  lambda_H: 2.41421  3.44372  4.18232  4.71780  5.11532  5.41785  5.65337  5.84046

- lambda_2 = 1 + sqrt(2) exactly; otherwise lambda_H are high-degree algebraic
  numbers (algebraic degrees 2, 4, 9, 29, 68 for H=2..6) -- NOT an elementary
  family. The dominant root is real (Perron-Frobenius).
- lambda_H increases monotonically toward lambda_king ~ 7.10, but SLOWLY and
  sub-geometrically: increments 1.03, .74, .54, .40, .30, .24, .19 with ratios
  RISING toward 1 (.72 -> .79). Aitken extrapolation climbs 6.06 -> 6.56 and is
  still rising at H=9 -- consistent with 7.10 but too slow to pin it; the direct
  a(n)-ratio method remains the better lambda_king estimator.

### Factor-lifetime law (a real structural finding)
Q_H is highly reducible, and consecutive denominators share almost everything:
deg gcd(Q_H, Q_{H+1}) is nearly deg Q_H. The co-degree that DROPS,
delta_H = deg Q_H - deg gcd(Q_H, Q_{H+1}), is

  H:        2  3  4  5   6   7    8
  delta_H:  0  1  2  4   9   29   68

These drops are exactly the algebraic degrees 1, 2, 4, 9, 29, 68 of the factors
carrying the eigenvalue born at height H-2 (1 = the x-1 / eigenvalue-1 factor;
2 = lambda_2's; 4 = lambda_3's; 9 = lambda_4's; 29 = lambda_5's; 68 = lambda_6's).
=> **Each irreducible factor of Q_H divides exactly THREE consecutive Q_H** (the
one born at height H0 appears in Q_{H0}, Q_{H0+1}, Q_{H0+2}, then retires).
Verified for factors born at H=1..6. Plausibly a finite-range (3-row) coupling
from king adjacency reaching +/-1 rows; not yet proven. This is the clean
structure the lambda_H sequence itself lacks: it lives in the GF factorization,
not in the coefficients or the growth constants.

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
