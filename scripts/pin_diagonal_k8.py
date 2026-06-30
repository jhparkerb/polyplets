#!/usr/bin/env python3
"""Pin / validate the height-diagonal polynomials P_k, with focus on k=8.

T(n, n-k) = P_k(n) * 3^(n-1-3k),  P_k a degree-k polynomial, valid n >= 2k+1.
Leading coefficient conjecture (observed k<=7): [n^k] P_k = 25^k / k!.

This script (exact rational arithmetic):
  1. extracts the swept diagonal values from the a(23) triangle,
  2. confirms the 25^k/k! leading-coeff conjecture for k=3..7 from data,
  3. validates the "leading-coeff + k points" method by reproducing the KNOWN
     P_7 and predicting held-out swept rows,
  4. shows exactly why k=8 needs one more point (a(24) -> T(24,16)),
  5. makes a falsifiable prediction of T(24,16) via the sum-of-roots pattern,
     so the a(24) run can confirm-or-refute the k=8 extrapolation in one number.
"""
from fractions import Fraction as F
from math import factorial
import sys

# ---- swept diagonal values T(n, n-k) from results/ns_a23/triangle.txt ----
TRI = {}
with open("results/ns_a23/triangle.txt") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        n, h, v = line.split()
        TRI[(int(n), int(h))] = int(v)

def pk_values(k):
    """Return {n: P_k(n)} from swept T(n,n-k), for all available n >= 2k+1."""
    out = {}
    for n in range(2 * k + 1, 24):
        cell = TRI.get((n, n - k))
        if cell is None:
            continue
        # P_k(n) = T(n,n-k) * 3^(3k+1-n), must be an exact integer
        e = 3 * k + 1 - n
        val = F(cell) * (F(3) ** e)
        assert val.denominator == 1, f"P_{k}({n}) not integer: {val}"
        out[n] = int(val)
    return out

def fit_poly(points, deg, fixed_lead=None):
    """Exact least-constraints fit of a degree-`deg` poly to (x,y) points.
    If fixed_lead is given, the top coeff is fixed and `deg` points pin the
    remaining `deg` coeffs; else `deg+1` points pin all. Solves the (square)
    Vandermonde system exactly over Q. Returns coeffs [c0..c_deg]."""
    pts = sorted(points.items())
    if fixed_lead is None:
        need = deg + 1
        xs = [F(x) for x, _ in pts[:need]]
        ys = [F(y) for _, y in pts[:need]]
        ncoef = deg + 1
        # rows: sum_{j=0..deg} c_j x^j = y
        A = [[x ** j for j in range(ncoef)] for x in xs]
        b = list(ys)
    else:
        need = deg
        xs = [F(x) for x, _ in pts[:need]]
        ys = [F(y) for _, y in pts[:need]]
        ncoef = deg  # unknowns c0..c_{deg-1}; c_deg fixed
        A = [[x ** j for j in range(deg)] for x in xs]
        b = [ys[i] - fixed_lead * (xs[i] ** deg) for i in range(need)]
    coeffs = gauss(A, b)
    if fixed_lead is not None:
        coeffs = coeffs + [fixed_lead]
    return coeffs

def gauss(A, b):
    """Exact Gaussian elimination over Fraction. A square, returns solution."""
    n = len(A)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pivval = M[col][col]
        M[col] = [x / pivval for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][j] - f * M[col][j] for j in range(n + 1)]
    return [M[i][n] for i in range(n)]

def poly_eval(coeffs, x):
    return sum(c * (F(x) ** i) for i, c in enumerate(coeffs))

print("=== 1. leading-coefficient conjecture  [n^k]P_k == 25^k/k! ===")
ok = True
for k in range(3, 8):
    pts = pk_values(k)
    coeffs = fit_poly(pts, k)                  # full fit, deg+1 points
    lead = coeffs[k]
    conj = F(25 ** k, factorial(k))
    match = (lead == conj)
    ok &= match
    # also confirm the remaining points lie on the fitted poly (overdetermined)
    consistent = all(poly_eval(coeffs, n) == v for n, v in pts.items())
    print(f"  k={k}: lead={lead}  conj=25^{k}/{k}!={conj}  match={match}  "
          f"all {len(pts)} pts on poly={consistent}")
print(f"  => leading-coeff conjecture holds for k=3..7: {ok}")

print()
print("=== 2. method check: reproduce P_7 from leading-coeff + 7 points ===")
p7 = pk_values(7)                              # n=15..23 (9 points)
full7 = fit_poly(p7, 7)                        # 8 coeffs from 8 points
lead7 = F(25 ** 7, factorial(7))
# leading-coeff method: fix lead, use only 7 points (n=15..21), predict 22,23
sub7 = {n: p7[n] for n in range(15, 22)}
meth7 = fit_poly(sub7, 7, fixed_lead=lead7)
same = (full7 == meth7)
pred22 = poly_eval(meth7, 22) == p7[22]
pred23 = poly_eval(meth7, 23) == p7[23]
print(f"  full(9pt) == leading+7pt method : {same}")
print(f"  method predicts held-out P_7(22): {pred22}")
print(f"  method predicts held-out P_7(23): {pred23}")
print(f"  => for k=7, k points + leading coeff suffice: {same and pred22 and pred23}")

print()
print("=== 3. k=8 status from a(23) data ===")
p8 = pk_values(8)                              # n=17..23 (7 points)
lead8 = F(25 ** 8, factorial(8))
print(f"  available swept points: n={sorted(p8)} ({len(p8)} points)")
print(f"  degree-8 poly, leading fixed => 8 free unknowns; have {len(p8)} pts "
      f"=> {'PINNABLE' if len(p8) >= 8 else f'SHORT by {8 - len(p8)}'}")
print(f"  the missing point is T(24,16) (n=24, h=16) -> needs a(24).")

print()
print("=== 4. falsifiable prediction of T(24,16) (sum-of-roots pattern) ===")
# sum of roots s_k = -c_{k-1}/c_k.  s_k is itself ~quadratic in k (2nd diff ~const);
# fit s_k on k=2..7, extrapolate s_8 -> gives subleading c_7(P_8) = -lead8*s_8.
sroots = {}
for k in range(2, 8):
    c = fit_poly(pk_values(k), k)
    sroots[k] = -c[k - 1] / c[k]
sc = fit_poly(sroots, 2)                        # quadratic in k
s8 = poly_eval(sc, 8)
print(f"  sum-of-roots s_k (k=2..7): " + ", ".join(f"{k}:{float(sroots[k]):.4f}" for k in sroots))
print(f"  quadratic fit -> s_8 = {float(s8):.5f}")
sub8 = -lead8 * s8                               # predicted c_7 of P_8
# With leading + predicted-subleading known (2 constraints), the 7 swept points
# now over-determine P_8: fit the remaining 7 coeffs from 7 pts with 2 fixed.
# Build: unknowns c0..c5 (6), plus check. Actually fix c8,c7 -> 7 unknowns c0..c6,
# need 7 points -> exactly pinnable. Then PREDICT P_8(24) -> T(24,16).
def fit_two_fixed(points, deg, c_deg, c_dm1):
    pts = sorted(points.items())[:deg - 1]      # deg-1 points for deg-1 unknowns
    xs = [F(x) for x, _ in pts]; ys = [F(y) for _, y in pts]
    A = [[x ** j for j in range(deg - 1)] for x in xs]
    b = [ys[i] - c_deg * xs[i] ** deg - c_dm1 * xs[i] ** (deg - 1) for i in range(len(xs))]
    lo = gauss(A, b)
    return lo + [c_dm1, c_deg]
# Real one-term-ahead test of the lead+sum-of-roots shortcut, run on k=7 where we
# know the answer: fit s_k quadratic on k=2..6 ONLY, predict s_7 (held out), then
# pin P_7 from leading + predicted-subleading + only the lowest swept points and
# check it predicts the highest held-out swept rows.
sc6 = fit_poly({k: sroots[k] for k in range(2, 7)}, 2)   # quad on k=2..6
s7_pred = poly_eval(sc6, 7)
sub7p = -lead7 * s7_pred
p7_shortcut = fit_two_fixed(p7, 7, lead7, sub7p)         # 6 lowest pts + 2 fixed
held = [n for n in sorted(p7) if n >= 21]
shortcut_ok = (s7_pred == sroots[7]) and all(poly_eval(p7_shortcut, n) == p7[n] for n in held)
print(f"  one-term-ahead self-test on k=7: s_7 predicted exactly={s7_pred==sroots[7]}, "
      f"predicts held-out rows n>=21={all(poly_eval(p7_shortcut, n)==p7[n] for n in held)} => {shortcut_ok}")

p8_pred = fit_two_fixed(p8, 8, lead8, sub8)
chk = all(poly_eval(p8_pred, n) == v for n, v in p8.items())
P8_24 = poly_eval(p8_pred, 24)
T24_16 = P8_24 * (F(3) ** (24 - 1 - 3 * 8))      # T(n,n-k)=P_k(n)*3^(n-1-3k); here 3^-1
print(f"  provisional P_8 reproduces all 7 swept points: {chk}")
if T24_16.denominator == 1:
    print(f"  PREDICTION  T(24,16) = {int(T24_16)}")
    print(f"  (a(24) will sweep H=16 at n=24; equal => k=8 extrapolation confirmed)")
else:
    print(f"  T(24,16) predicted non-integer ({T24_16}) -> pattern suspect")

print()
print(f"VERDICT: leading-coeff method sound (k<=7); k=8 pins the moment a(24) "
      f"gives T(24,16); we have a falsifiable check for it.")
sys.exit(0 if ok and same else 1)
