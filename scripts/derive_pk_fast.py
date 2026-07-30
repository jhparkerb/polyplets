#!/usr/bin/env python3
"""Fast P_k deriver via the exp recurrence (no sympy, no symbolic n).

P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j ).  The exp identity E'=f'E gives

    k P_k = sum_{j=1}^{k} j (a_j + b_j n) P_{k-j},     P_0 = 1,

so  P_k(n) = known_k(n) + a_k + b_k n,  where known_k = (1/k) sum_{j<k} j c_j P_{k-j}
and c_j(n) = a_j + b_j n. Each P_k needs exactly its two unknowns a_k,b_k, fit
from two diagonal data points T(n,n-k) (n >= 2k+1). Pure Fraction arithmetic.

Diagonal data T(n,n-k) are read ONLY from heights a run actually swept (see
REAL_H below); cells a run injected from a closed form are never used, so both
the fit and the holdout rest on real enumeration. Validation per k: leading
coeff = 25^k/k!, P_k * k! integral, and agreement with every extra (held-out)
REAL data point -- reported as "NO HOLDOUT" when no such point exists rather
than as a vacuous pass.
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
#
# PROVENANCE RULE.  Each banked run only *swept* heights up to some top real
# height; everything above it was injected from the very P_k closed forms this
# script derives.  The old loader globbed results/ns_a*/perheight/h{H}.out and
# took the lexically-first run containing row n -- which for a diagonal point
# at row n is ns_a{n}, precisely the run that injected that cell.  Every
# "holdout" was therefore the formula checked against its own output.
#
# REAL_H[run] = top height that run swept for real.  Verified cell by cell
# against each results/ns_a*/PROVENANCE.md on 2026-07-30 (AUDIT-2026-07-30 D2);
# the quoted phrase from each file is given.  Runs with no perheight/ dir
# (ns_a23..a25) are absent and simply never match.
REAL_H = {
    20: 20,  # "420 columns over 20 heights" (full real sweep, pre-diagonals)
    21: 21,  # full real sweep; only the k=0 top strip H21 is closed form
    26: 15,  # "real sweep H1-15 (top real H15)"
    27: 16,  # "dalby: H16 (the monster) ... ayr: swept tail H3-15"
    28: 15,  # "only H1,2 and the real sweep H3-15 run the engine"
    29: 16,  # "only H1,2 and the real sweep H3-16 run the engine"
    30: 17,  # "real sweep was H3-17 (top real height H17)"
    31: 18,  # "real sweep was H3-18 (top real height H18)"
    32: 18,  # "real sweep was H3-18.  P13 held the top real height at H18"
    33: 18,  # "real sweep was H3-18.  P14 held the top real height at H18"
    34: 18,  # "real sweep was H3-18.  P15 held the top real height at H18"
    35: 19,  # "the real sweep ran H3-H19 (H19 swept as a real height)"
    36: 19,  # "ayr: heights 1-18 real sweeps ... dalby: height 19 real sweep"
    37: 19,  # "Real sweeps H3-H19; H20-H37 via wired P_k closed forms"
    38: 20,  # "Real sweeps H3-H20 (first production H20 sweep)"
    39: 20,  # "Real sweeps H3-H20; H21-H39 via wired P_k closed forms"
    40: 21,  # "Real sweeps H3-H21 ... H21 is the tallest real sweep"
}

_cache = {}
def load_T(n, H):
    """T(n,H) from a run that actually SWEPT height H (never a P_k injection).

    Returns None when no banked run swept that cell for real -- callers must
    treat that as "no evidence", not as a missing file.
    """
    key = (n, H)
    if key in _cache:
        return _cache[key]
    val = None
    for run in sorted(REAL_H):
        if H > REAL_H[run] or run < n:
            continue                      # injected there, or row n absent
        f = os.path.join(ROOT, f"results/ns_a{run}/perheight/h{H}.out")
        if not os.path.exists(f):
            continue
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
    """P_k(n) from real-swept data = T(n,n-k) / 3^(n-1-3k)."""
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
        # held-out points beyond the two fit points -- REAL-SWEPT ONLY, so a
        # pass is genuine independent evidence.  None means "no holdout data
        # exists", which is a distinct state from "holdout passed".
        hold_ok = None; nheld = 0
        for nn in range(2*k+1, 2*k+12):
            if nn in (n1, n2):
                continue
            pd = Pdata(nn, k)
            if pd is None:
                continue
            nheld += 1
            if hold_ok is None:
                hold_ok = True
            if peval(P[k], nn) != pd:
                hold_ok = False
        held = "NO HOLDOUT (0 points)" if nheld == 0 else \
               f"holdout({nheld} real)={hold_ok}"
        tag = "ok" if (lead_ok and int_ok and hold_ok is not False) else "*** FAIL ***"
        print(f"P_{k:2d}: fit n={n1},{n2}  lead25^k/k!={lead_ok}  int={int_ok}  "
              f"{held}  a_k={a_k} b_k={b_k}  {tag}")
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
    P, _ = derive(kmax)
    for k in (int(x) for x in sys.argv[2:]):
        emit_go(P, k)
