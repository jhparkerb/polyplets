#!/usr/bin/env python3
"""H1: certified ingredients for results/anisotropic-not-dfinite.md.

Computes the new-root content psi_H = Q_H / gcd(Q_H, prod_{j<H} Q_j) of the
banked fixed-height GF denominators (validated H <= 10) and certifies, mod
p = 2^61 - 1 (rigorous over Q since gcd == 1 mod p with preserved degrees
implies gcd == 1 over Q):
  - deg psi_H = 1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289
  - every psi_H squarefree
  - every P_H/Q_H in lowest terms
These feed the pole-argument theorem excluding y-ODEs for the anisotropic
GF in the (order, x-degree) boxes listed in the results doc.
"""
import os
import re

P = (1 << 61) - 1
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = {1: 1, 2: 2, 3: 4, 4: 9, 5: 29, 6: 68, 7: 181,
            8: 462, 9: 1254, 10: 3289}


def pmod(c):
    c = [x % P for x in c]
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return c


def pdiv(a, b):
    a = a[:]
    db = len(b) - 1
    inv = pow(b[-1], -1, P)
    q = [0] * (len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        f = a[i] * inv % P
        q[i - db] = f
        if f:
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - f * b[j]) % P
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return q, a


def pgcd(a, b):
    a = pmod(a)
    b = pmod(b)
    while len(b) > 1 or b[0] != 0:
        _, r = pdiv(a, b)
        a, b = b, r
        while len(a) > 1 and a[-1] == 0:
            a.pop()
    return a


def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] = (r[i + j] + x * y) % P
    return pmod(r)


def deriv(a):
    return pmod([(i * c) % P for i, c in enumerate(a)][1:] or [0])


def main():
    txt = open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")).read()
    PQ = {}
    for m in re.finditer(
            r"H=(\d+)\s+order=\d+\s+(?:onset_n=\d+\s+)?validated=(\w+)"
            r".*?\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])", txt):
        if m.group(2) == "True":
            PQ[int(m.group(1))] = (eval(m.group(3)), eval(m.group(4)))
    assert sorted(PQ) == list(range(1, 11)), sorted(PQ)
    psi = {}
    prod = [1]
    for H in sorted(PQ):
        Pn, Qd = PQ[H]
        assert Qd[-1] % P != 0, f"degree drop H={H}"
        Qp = pmod(list(Qd))
        g = pgcd(Qp, prod) if len(prod) > 1 else [1]
        q_, r = pdiv(Qp, g)
        assert r == [0]
        psi[H] = q_
        assert len(q_) - 1 == EXPECTED[H], (H, len(q_) - 1)
        assert len(pgcd(q_, deriv(q_))) == 1, f"psi_{H} not squarefree"
        assert len(pgcd(pmod(list(Pn)), Qp)) == 1, f"P/Q not lowest terms H={H}"
        prod = pmul(prod, Qp)
    print("H1 ingredients certified mod 2^61-1: deg psi =",
          [EXPECTED[H] for H in sorted(EXPECTED)],
          "; squarefree; lowest terms  OK")


def mu_monotone():
    """Strict monotonicity of strip growth constants (exact coefficients)."""
    import re
    import mpmath as mp
    mp.mp.dps = 50
    txt = open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")).read()
    Qs = {}
    for m in re.finditer(
            r"H=(\d+)\s+order=\d+\s+(?:onset_n=\d+\s+)?validated=(\w+)"
            r".*?\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])", txt):
        if m.group(2) == "True":
            Qs[int(m.group(1))] = eval(m.group(4))
    prev = 0
    for H in sorted(Qs):
        q = Qs[H]

        def f(t):
            return sum(mp.mpf(c) * t ** i for i, c in enumerate(q))

        t = mp.mpf("0.05")
        step = mp.mpf("0.0004")
        ft = f(t)
        mu = None
        while t < mp.mpf("1.05"):
            t2 = t + step
            ft2 = f(t2)
            if ft * ft2 <= 0:
                lo, hi = t, t2
                for _ in range(150):
                    mid = (lo + hi) / 2
                    if f(lo) * f(mid) <= 0:
                        hi = mid
                    else:
                        lo = mid
                mu = 1 / ((lo + hi) / 2)
                break
            t, ft = t2, ft2
        assert mu is not None and mu > prev, (H, mu, prev)
        prev = mu
    print("strip growth constants strictly increasing (H <= 10)  OK")


def atom_irreducibility():
    """Multi-prime irreducibility certificates for psi_H, H <= 8.
    A proper factor's degree must be a subset-sum of the mod-p factor
    degrees for EVERY good prime; empty intersection => irreducible."""
    import re
    import warnings
    warnings.filterwarnings("ignore")
    import sympy as sp
    x = sp.symbols('x')
    txt = open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")).read()
    Qs = {}
    for m in re.finditer(
            r"H=(\d+)\s+order=\d+\s+(?:onset_n=\d+\s+)?validated=(\w+)"
            r".*?\nP: (\[[^\]]*\])\nQ: (\[[^\]]*\])", txt):
        if m.group(2) == "True":
            Qs[int(m.group(1))] = eval(m.group(4))
    polys = {H: sp.Poly(list(reversed(Qs[H])), x)
             for H in sorted(Qs) if H <= 8}
    psi = {}
    prod = sp.Poly(1, x)
    for H in sorted(polys):
        g = sp.gcd(polys[H], prod)
        ps, _ = sp.div(polys[H], g)
        psi[H] = sp.Poly(ps, x)
        prod = sp.Poly(prod * polys[H], x)
    PRIMES = {1: [2], 2: [3], 3: [7], 4: [11],
              5: [3, 5, 7], 6: [3, 5, 7],
              7: [5, 7, 11, 13, 17, 19], 8: [5, 7, 11, 13, 17, 19, 23]}
    for H in sorted(psi):
        d = int(sp.degree(psi[H]))
        achieve = None
        for p in PRIMES[H]:
            fl = sp.factor_list(psi[H].as_expr(), modulus=p)
            degs = []
            for fac, mult in fl[1]:
                degs += [int(sp.degree(fac, x))] * mult
            if sum(degs) != d:
                continue
            bits = 1
            for dd in degs:
                bits |= bits << dd
            cur = {i for i in range(d + 1) if (bits >> i) & 1}
            achieve = cur if achieve is None else (achieve & cur)
            if achieve == {0, d}:
                break
        assert achieve == {0, d}, (H, sorted(achieve)[:6])
    print("psi_H irreducible over Q for H = 1..8 "
          "(degrees 1,2,4,9,29,68,181,462)  OK")


if __name__ == "__main__":
    main()
    mu_monotone()
    atom_irreducibility()
