#!/usr/bin/env python3
"""Compare 2-param r_n = lam(1 + th/n) vs 3-param lam(1 + th/n + c/n^(1+D1))
window stability for the A006770 ratio fit. Least squares via normal
equations in exact float; D1 scanned on a grid (the fit is linear given D1)."""
from fractions import Fraction

a = {}
for line in open("/Users/jasonp/src/polyominoes/results/b006770_upload.txt"):
    if line.startswith("#"):
        continue
    n, v = line.split()
    a[int(n)] = int(v)
a[33] = 74631481980411777590683952
a[34] = 515316838423862758858377704

r = {n: a[n] / a[n - 1] for n in range(2, 35)}


def lstsq(rows, rhs):
    import itertools
    m = len(rows[0])
    A = [[sum(rows[i][p] * rows[i][q] for i in range(len(rows))) for q in range(m)] for p in range(m)]
    b = [sum(rows[i][p] * rhs[i] for i in range(len(rows))) for p in range(m)]
    # gaussian
    for col in range(m):
        piv = max(range(col, m), key=lambda i: abs(A[i][col]))
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]
        for i in range(m):
            if i != col and A[i][col]:
                f = A[i][col] / A[col][col]
                A[i] = [x - f * y for x, y in zip(A[i], A[col])]
                b[i] -= f * b[col]
    return [b[i] / A[i][i] for i in range(m)]


def fit2(ns):
    rows = [[1.0, 1.0 / n] for n in ns]
    rhs = [r[n] for n in ns]
    lam, lt = lstsq(rows, rhs)
    return lam, lt / lam


def fit3(ns, D1):
    rows = [[1.0, 1.0 / n, 1.0 / n ** (1 + D1)] for n in ns]
    rhs = [r[n] for n in ns]
    lam, lt, lc = lstsq(rows, rhs)
    resid = sum((sum(c * v for c, v in zip(row, (lam, lt, lc))) - y) ** 2
                for row, y in zip(rows, rhs))
    return lam, lt / lam, lc / lam, resid


print("2-param windows (start..34):")
for s in (10, 15, 20, 25):
    ns = list(range(s, 35))
    lam, th = fit2(ns)
    print(f"  n={s:2d}..34  lam={lam:.6f}  theta={th:+.4f}")

for D1 in (0.5, 1.0, 1.5, 2.0):
    print(f"3-param, Delta1={D1}:")
    for s in (10, 15, 20, 25):
        ns = list(range(s, 35))
        lam, th, c, resid = fit3(ns, D1)
        print(f"  n={s:2d}..34  lam={lam:.6f}  theta={th:+.4f}  c={c:+.3f}  rss={resid:.3e}")
