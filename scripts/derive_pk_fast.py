#!/usr/bin/env python3
"""Fast P_k deriver via the exp recurrence (no sympy, no symbolic n).

P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j ).  The exp identity E'=f'E gives

    k P_k = sum_{j=1}^{k} j (a_j + b_j n) P_{k-j},     P_0 = 1,

so  P_k(n) = known_k(n) + a_k + b_k n,  where known_k = (1/k) sum_{j<k} j c_j P_{k-j}
and c_j(n) = a_j + b_j n. Each P_k needs exactly its two unknowns a_k,b_k, fit
from two diagonal data points T(n,n-k) (n >= 2k+1). Pure Fraction arithmetic.

Diagonal data T(n,n-k) are read from banked per-height sweeps
results/ns_a{n}/perheight/h{n-k}.out. Validation per k: leading coeff = 25^k/k!,
P_k * k! integral, and agreement with every extra (held-out) data point.
"""
import glob, os, sys
from fractions import Fraction as F
from math import factorial

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- dense polynomials in n as lists of Fraction (index = power) ----
def padd(a, b):
    n = max(len(a), len(b)); a = a + [F(0)]*(n-len(a)); b = b + [F(0)]*(n-len(b))
    return [x+y for x, y in zip(a, b)]
def pscale(a, s):
    return [x*s for x in a]
def pmul(a, b):
    r = [F(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i+j] += x*y
    return r
def peval(a, n):
    r = F(0)
    for c in reversed(a):
        r = r*n + c
    return r

# ---- diagonal data loader ----
_cache = {}
def load_T(n, H):
    key = (n, H)
    if key in _cache:
        return _cache[key]
    val = None
    for f in sorted(glob.glob(os.path.join(ROOT, f"results/ns_a*/perheight/h{H}.out"))):
        with open(f) as fh:
            for line in fh:
                p = line.split()
                if len(p) >= 2 and p[0] == str(n):
                    val = int(p[1]); break
        if val is not None:
            break
    _cache[key] = val
    return val

def Pdata(n, k):
    """P_k(n) from data = T(n,n-k) / 3^(n-1-3k)."""
    T = load_T(n, n - k)
    if T is None:
        return None
    ex = 1 + 3*k - n          # P_k(n) = T(n,n-k) * 3^(1+3k-n)
    return F(T) * F(3)**ex if ex >= 0 else F(T) / F(3)**(-ex)

def derive(kmax):
    P = {0: [F(1)]}          # P_0 = 1
    c = {}                    # c_j = [a_j, b_j] (poly a_j + b_j n)
    for k in range(1, kmax+1):
        # known_k = (1/k) sum_{j=1}^{k-1} j c_j P_{k-j}
        known = [F(0)]
        for j in range(1, k):
            known = padd(known, pscale(pmul(c[j], P[k-j]), F(j)))
        known = pscale(known, F(1, k))
        # fit a_k,b_k from two smallest valid data points n=2k+1, 2k+2
        pts = []
        n = 2*k+1
        while len(pts) < 2 and n <= 2*k+6:
            pd = Pdata(n, k)
            if pd is not None:
                pts.append((n, pd))
            n += 1
        if len(pts) < 2:
            raise SystemExit(f"P_{k}: need 2 data points, found {len(pts)}")
        (n1, d1), (n2, d2) = pts[0], pts[1]
        # d_i = known(n_i) + a_k + b_k n_i
        r1 = d1 - peval(known, n1)
        r2 = d2 - peval(known, n2)
        b_k = (r2 - r1) / (n2 - n1)
        a_k = r1 - b_k*n1
        c[k] = [a_k, b_k]
        P[k] = padd(known, [a_k, b_k])
        # --- validation ---
        lead_ok = P[k][k] == F(25**k, factorial(k))
        num = [ck*factorial(k) for ck in P[k]]
        int_ok = all(x.denominator == 1 for x in num)
        # held-out points beyond the two fit points
        hold_ok = True; nheld = 0
        for nn in range(2*k+1, 2*k+12):
            if nn in (n1, n2):
                continue
            pd = Pdata(nn, k)
            if pd is None:
                continue
            nheld += 1
            if peval(P[k], nn) != pd:
                hold_ok = False
        tag = "ok" if (lead_ok and int_ok and hold_ok) else "*** FAIL ***"
        print(f"P_{k:2d}: fit n={n1},{n2}  lead25^k/k!={lead_ok}  int={int_ok}  "
              f"holdout({nheld})={hold_ok}  a_k={a_k} b_k={b_k}  {tag}")
    return P, c

def emit_go(P, k):
    kf = factorial(k)
    num = [int(P[k][p]*kf) for p in range(k+1)]
    desc = list(reversed(num))
    print(f"\nGo diagCoeffTable case {k} (c{k}..c0, denom {k}!):")
    print(f"  {k}: {{[]string{{")
    for i in range(0, len(desc), 4):
        print("    " + ", ".join(f'"{x}"' for x in desc[i:i+4]) + ",")
    print(f"  }}, {kf}}},")

if __name__ == "__main__":
    kmax = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    P, c = derive(kmax)
    for k in (int(x) for x in sys.argv[2:]):
        emit_go(P, k)
