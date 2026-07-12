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


if __name__ == "__main__":
    main()
