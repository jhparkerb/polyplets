#!/usr/bin/env python3
"""Cumulant-form fitter for the dmirror diagonal quasi-polynomials
(the derive_pk_fast.py trick transplanted to Hall of Mirrors).

Ansatz:  d(S, S+k) = 2 * [y^k] exp( sum_j c_j(S) y^j ),
         c_j(S) = u_j(S) + (-1)^S v_j(S),  u_j, v_j polynomials in S.

P_0 = 2 (the two spines) is the global factor. The exp identity makes each
level's unknowns LINEAR given the lower levels:

    d(S,S+k)/2 = c_k(S) + [y^k] exp(sum_{j<k} c_j y^j),

so level k is a small exact linear solve for u_k, v_k coefficients from
in-regime diagonal points (S >= 2k+2 even / 2k+3 odd, the measured onset
law), with every remaining point demanded as an EXACT witness. Degree caps
(du, dv) per level are chosen minimally: the smallest caps whose solution
survives all witnesses, requiring >= MIN_WIT spare points. The content of
the ansatz is exactly these caps -- if cumulant degrees grew like k, the
form would compress nothing and this script would refuse honestly.

Usage: dmirror_pk_exp.py KMAX SYMDIR [SYMDIR ...]
       e.g. dmirror_pk_exp.py 6 runs/sym26 runs/sym32
"""
import sys
from fractions import Fraction

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from dmirror_diagonals import load  # noqa: E402  (same triangle loader)

MIN_WIT = 3

# ---- dense polynomials in S: list of Fraction, index = power ----
def padd(a, b):
    n = max(len(a), len(b))
    a = a + [Fraction(0)] * (n - len(a))
    b = b + [Fraction(0)] * (n - len(b))
    return [x + y for x, y in zip(a, b)]

def pmul(a, b):
    r = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return r

def pscale(a, s):
    return [x * s for x in a]

def peval(a, S):
    r = Fraction(0)
    for c in reversed(a):
        r = r * S + c
    return r

def pdeg(a):
    for i in range(len(a) - 1, -1, -1):
        if a[i]:
            return i
    return -1

def pstr(a):
    terms = []
    for i in range(len(a) - 1, -1, -1):
        if not a[i]:
            continue
        s = f"{a[i]}" if i == 0 else (f"{a[i]}*S" if i == 1 else f"{a[i]}*S^{i}")
        terms.append(s)
    return " + ".join(terms).replace("+ -", "- ") or "0"

# ---- series in y with polynomial coefficients ----
def exp_series(c, K):
    """[y^0..y^K] of exp(sum_{j>=1} c[j] y^j); c = {level: poly}."""
    E = [[Fraction(1)]] + [[Fraction(0)] for _ in range(K)]
    for n in range(1, K + 1):
        acc = [Fraction(0)]
        for j in range(1, n + 1):
            if j in c:
                acc = padd(acc, pscale(pmul(c[j], E[n - j]), Fraction(j)))
        E[n] = pscale(acc, Fraction(1, n))
    return E

def solve_exact(rows, rhs):
    """Gaussian elimination over Fraction; returns solution or None."""
    m, n = len(rows), len(rows[0])
    A = [list(r) + [v] for r, v in zip(rows, rhs)]
    piv = []
    r = 0
    for col in range(n):
        p = next((i for i in range(r, m) if A[i][col]), None)
        if p is None:
            return None  # singular for these points
        A[r], A[p] = A[p], A[r]
        A[r] = [x / A[r][col] for x in A[r]]
        for i in range(m):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        piv.append(col)
        r += 1
        if r == n:
            break
    if r < n:
        return None
    return [A[i][n] for i in range(n)]

def diag_points(d, k):
    """In-regime exact points [(S, eps, value)] for diagonal k (onset law)."""
    pts = []
    for (S, n), c in sorted(d.items()):
        if n - S != k:
            continue
        onset = 2 * k + 2 if S % 2 == 0 else 2 * k + 3
        if S >= onset:
            pts.append((S, 1 if S % 2 == 0 else -1, c))
    return pts

def fit_level(d, k, c, kmaxcap):
    """Fit u_k, v_k with minimal degree caps; returns (u, v, caps, nwit)."""
    pts = diag_points(d, k)
    # residual r(S) = d/2 - [y^k]exp(lower levels), parity-resolved
    def resid(S, eps, val):
        cc = {j: padd(c[j][0], pscale(c[j][1], eps)) for j in c}
        E = exp_series(cc, k)
        return Fraction(val, 2) - peval(E[k], S)
    res = [(S, eps, resid(S, eps, val)) for S, eps, val in pts]
    for du in range(0, kmaxcap + 1):
        for dv in range(-1, du + 1):  # dv=-1 means v_k = 0
            nunk = (du + 1) + (dv + 1)
            if nunk + MIN_WIT > len(res):
                continue
            # solve on the LAST nunk points (deepest in regime), verify rest
            solve_pts, wit = res[-nunk:], res[:-nunk]
            rows = [[Fraction(S) ** p for p in range(du + 1)] +
                    [eps * Fraction(S) ** p for p in range(dv + 1)]
                    for S, eps, _ in solve_pts]
            sol = solve_exact(rows, [r for _, _, r in solve_pts])
            if sol is None:
                continue
            u = sol[:du + 1]
            v = sol[du + 1:] if dv >= 0 else [Fraction(0)]
            ok = all(peval(u, S) + eps * peval(v, S) == r for S, eps, r in wit)
            if ok:
                return u, v, (du, dv), len(wit)
    return None

def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: dmirror_pk_exp.py KMAX SYMDIR [SYMDIR ...]")
    kmax = int(sys.argv[1])
    d = load(sys.argv[2:])
    print(f"triangle: {len(d)} (S,n) values")
    c = {}  # level -> (u poly, v poly)
    for k in range(1, kmax + 1):
        got = fit_level(d, k, c, kmaxcap=k)
        if got is None:
            print(f"level {k}: NO consistent fit within degree caps -- "
                  f"stopping (ansatz exhausted or data too thin)")
            break
        u, v, caps, nwit = got
        c[k] = (u, v)
        print(f"level {k}: deg(u)={pdeg(u)} deg(v)={pdeg(v)} "
              f"witnesses={nwit} EXACT")
        print(f"  u_{k} = {pstr(u)}")
        print(f"  v_{k} = {pstr(v)}")
    print()
    # emit P_k per parity from the fitted cumulants
    for k in sorted(c):
        for eps, name in ((1, "even"), (-1, "odd")):
            cc = {j: padd(c[j][0], pscale(c[j][1], eps)) for j in c if j <= k}
            E = exp_series(cc, k)
            print(f"P_{k} {name}(S) = {pstr(pscale(E[k], 2))}")

if __name__ == "__main__":
    main()
