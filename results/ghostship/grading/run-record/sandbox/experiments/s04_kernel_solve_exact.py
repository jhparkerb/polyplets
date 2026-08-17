#!/usr/bin/env python3
"""Session 04: EXACT-RATIONAL twin of s03_kernel_solve.py (same pipeline,
Fraction coefficients instead of mod-p).  Purpose: remove the single residual
mod-p caveat of docs/proofs/convex-box-kernel.md section 7 by rerunning the
per-x specializations (Part B) in exact arithmetic over Q.

Structure kept line-for-line parallel to s03_kernel_solve.py; only the
coefficient arithmetic differs.  Sanity gate: small bivariate exact run must
reproduce the DP table exactly (run this file directly).
"""
import sys, os
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_box import g_table, f_from_g

NX = 6       # max x-degree (bivariate sanity mode)
H = 6        # compare heights <= H
NU = 2 * H + 6   # max u-degree + margin

HALF = Fraction(1, 2)


class Ser:
    """Truncated series in x,u over Q with validity box (vx, vu)."""
    __slots__ = ("d", "vx", "vu")

    def __init__(self, d=None, vx=None, vu=None):
        self.d = d or {}
        self.vx = NX if vx is None else vx
        self.vu = NU if vu is None else vu

    def copy(self):
        return Ser(dict(self.d), self.vx, self.vu)

    def __add__(a, b):
        r = Ser(dict(a.d), min(a.vx, b.vx), min(a.vu, b.vu))
        for m, c in b.d.items():
            r.d[m] = r.d.get(m, 0) + c
        return r

    def __sub__(a, b):
        r = Ser(dict(a.d), min(a.vx, b.vx), min(a.vu, b.vu))
        for m, c in b.d.items():
            r.d[m] = r.d.get(m, 0) - c
        return r

    def __neg__(a):
        return Ser({m: -c for m, c in a.d.items()}, a.vx, a.vu)

    def __mul__(a, b):
        vx, vu = min(a.vx, b.vx), min(a.vu, b.vu)
        r = {}
        bd = b.d
        for (i1, j1), c1 in a.d.items():
            if c1 == 0 or i1 > vx or j1 > vu:
                continue
            for (i2, j2), c2 in bd.items():
                i, j = i1 + i2, j1 + j2
                if i <= vx and j <= vu:
                    m = (i, j)
                    r[m] = r.get(m, 0) + c1 * c2
        return Ser(r, vx, vu)

    def scal(a, k):
        return Ser({m: c * k for m, c in a.d.items()}, a.vx, a.vu)

    def get(a, i, j):
        return a.d.get((i, j), 0)

    def is_zero(a):
        return all(c == 0 for (i, j), c in a.d.items()
                   if i <= a.vx and j <= a.vu)

    def inv_unit(a):
        c0 = a.get(0, 0)
        assert c0 != 0, "inv of non-unit"
        ic0 = Fraction(1, 1) / c0
        r = Ser({(0, 0): ic0}, a.vx, a.vu)
        ad = {m: c for m, c in a.d.items() if m != (0, 0) and c}
        for i in range(a.vx + 1):
            for j in range(a.vu + 1):
                if i == 0 and j == 0:
                    continue
                acc = 0
                for (i1, j1), c1 in ad.items():
                    if i1 <= i and j1 <= j:
                        c2 = r.d.get((i - i1, j - j1), 0)
                        if c2:
                            acc += c1 * c2
                v = -acc * ic0
                if v:
                    r.d[(i, j)] = v
        return r


def divexact(A, B):
    """A/B where B = x^a u^b * unit; shrinks validity by (a,b)."""
    vx, vu = min(A.vx, B.vx), min(A.vu, B.vu)
    terms = [(i, j) for (i, j), c in B.d.items()
             if c != 0 and i <= vx and j <= vu]
    assert terms, "division by zero series"
    a = min(i for i, j in terms)
    b = min(j for i, j in terms)
    assert B.get(a, b) != 0, "corner of divisor not a monomial*unit"
    U = Ser({(i - a, j - b): c for (i, j), c in B.d.items()
             if i <= vx and j <= vu}, vx - a, vu - b)
    for (i, j), c in A.d.items():
        if i > vx or j > vu:
            continue
        assert (i >= a and j >= b) or c == 0, \
            f"numerator not divisible by x^{a} u^{b}: term {(i, j)}"
    As = Ser({(i - a, j - b): c for (i, j), c in A.d.items()
              if c and i <= vx and j <= vu}, vx - a, vu - b)
    return As * U.inv_unit()


def C(k):
    return Ser({(0, 0): k}) if k else Ser()


# ---------- polynomials in s over Ser ----------
class SPoly:
    def __init__(self, cs):
        self.cs = list(cs)
        while len(self.cs) > 1 and self.cs[-1].is_zero():
            self.cs.pop()

    def __add__(a, b):
        n = max(len(a.cs), len(b.cs))
        Z = Ser()
        return SPoly([(a.cs[i] if i < len(a.cs) else Z) +
                      (b.cs[i] if i < len(b.cs) else Z) for i in range(n)])

    def __sub__(a, b):
        n = max(len(a.cs), len(b.cs))
        Z = Ser()
        return SPoly([(a.cs[i] if i < len(a.cs) else Z) -
                      (b.cs[i] if i < len(b.cs) else Z) for i in range(n)])

    def __mul__(a, b):
        n = len(a.cs) + len(b.cs) - 1
        out = [Ser() for _ in range(n)]
        for i, ca in enumerate(a.cs):
            if ca.is_zero():
                continue
            for j, cb in enumerate(b.cs):
                out[i + j] = out[i + j] + ca * cb
        return SPoly(out)

    def scale(a, k):  # k = Ser
        return SPoly([c * k for c in a.cs])

    def eval(a, pt):  # pt = Ser, Horner
        r = a.cs[-1].copy()
        for c in reversed(a.cs[:-1]):
            r = r * pt + c
        return r

    def val1(a):
        r = Ser()
        for c in a.cs:
            r = r + c
        return r

    def deriv(a):
        return SPoly([a.cs[i].scal(i) for i in range(1, len(a.cs))]) \
            if len(a.cs) > 1 else SPoly([Ser()])

    def syndiv1(a):
        cs = a.cs
        q = [None] * (len(cs) - 1)
        acc = cs[-1].copy()
        for i in range(len(cs) - 2, -1, -1):
            q[i] = acc
            acc = acc + cs[i]
        assert acc.is_zero(), "syndiv1: nonzero remainder"
        return SPoly(q) if q else SPoly([Ser()])


def SP(*cs):
    return SPoly([c if isinstance(c, Ser) else C(c) for c in cs])


class SRat:
    def __init__(self, num, den):
        self.num, self.den = num, den

    def val1(self):
        return divexact(self.num.val1(), self.den.val1())

    def deriv1(self):
        n1, d1 = self.num.val1(), self.den.val1()
        np1, dp1 = self.num.deriv().val1(), self.den.deriv().val1()
        return divexact(np1 * d1 - n1 * dp1, d1 * d1)

    def eval(self, pt):
        return divexact(self.num.eval(pt), self.den.eval(pt))


# ---------- operators ----------
def L3(G, G1, G1p):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, -1, 1)
    num = s2 * G.num - (s2.scale(G1) + ss1.scale(G1p)) * G.den
    num = num.syndiv1().syndiv1()
    return SRat(num, G.den)


def D2op(G, G1, G1p):
    L = L3(G, G1, G1p)
    num2 = (SP(0, 1) * G.num - SP(0, 1).scale(G1) * G.den).syndiv1()
    return SRat(L.num - num2, G.den)


def D1op(G, G1, G1p):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, -1, 1)
    num = G.num - (s2.scale(G1) + ss1.scale(G1p - G1.scal(2))) * G.den
    num = num.syndiv1().syndiv1()
    return SRat(num, G.den)


def solve(king=True, xval=None):
    x = Ser({(1, 0): 1}) if xval is None else Ser({(0, 0): xval})
    u = Ser({(0, 1): 1})
    y = u * u
    one = C(1)

    N00 = SP(0, x * y, -(x * x * y))
    D00 = SPoly([one - y, -(x + x), x * x])
    F00 = SRat(N00, D00)
    F001 = F00.val1()
    F00p1 = F00.deriv1()

    s0 = C(1)
    for _ in range(NU // 2 + 2):
        s0 = one + y * s0 * (one - x * s0).inv_unit()
    res = (s0 - one) * (one - x * s0) - y * s0
    assert res.is_zero(), "kernel root residual nonzero"

    one_m_xs = SPoly([one, -x])
    Bnum = (N00 - SP(0, 1).scale(F001) * D00).syndiv1()
    Bden = D00 * one_m_xs
    if king:
        Bnum = Bnum + (SP(0, 1).scale(x * F001)) * D00
    B = SRat(Bnum, Bden)

    W = SP(-1, 1) * one_m_xs
    PK = W - SP(0, 1).scale(y)
    if king:
        Qcomp = SP(0, -1, 1).scale(x) - SP(0, 1)
    else:
        Qcomp = SP(0, -1)
    F101_kernel = -(B.eval(s0) * y * s0) * Qcomp.eval(s0).inv_unit()

    F10num = (B.num * W).scale(y) + Qcomp.scale(y * F101_kernel) * B.den
    F10den = PK * B.den
    F10 = SRat(F10num, F10den)
    F101 = F10.val1()
    assert (F101 - F101_kernel).is_zero(), "F10(1) consistency FAIL"
    F10p1 = F10.deriv1()

    D1F00 = D1op(F00, F001, F00p1)
    D2F10 = D2op(F10, F101, F10p1)
    vals = []
    for sgn in (1, -1):
        sig = (one - u.scal(sgn)).inv_unit()
        v = y * D1F00.eval(sig) + (y * D2F10.eval(sig)).scal(2)
        vals.append(v)
    F111 = (vals[0] + vals[1]).scal(HALF)
    odd = [((i, j), c) for (i, j), c in F111.d.items()
           if j % 2 == 1 and c and i <= F111.vx and j <= F111.vu]
    assert not odd, f"odd-u terms in F11(1): {odd[:5]}"

    F = F001 + F101.scal(2) + F111
    return F


def main():
    """Sanity gate: exact bivariate run vs DP table, both modes."""
    global NX, H, NU
    NX = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    H = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    NU = 2 * H + 6
    for king in (True, False):
        tag = "KING" if king else "POLYOMINO(control)"
        F = solve(king=king)
        g = g_table(NX, H, king=king)
        f = f_from_g(g, NX, H)
        bad = 0
        ncmp = 0
        for w in range(1, NX + 1):
            for h in range(1, H + 1):
                if w > F.vx or 2 * h > F.vu:
                    continue
                ncmp += 1
                got = F.get(w, 2 * h)
                if got != f[w][h]:
                    bad += 1
                    print(f"    MISMATCH w={w} h={h}: F={got} table={f[w][h]}")
        nonint = [(m, c) for m, c in F.d.items()
                  if m[0] <= F.vx and m[1] <= F.vu
                  and isinstance(c, Fraction) and c.denominator != 1 and c]
        print(f"  {tag}: exact-Q kernel solution vs DP table: {ncmp} cells, "
              f"{bad} mismatches; non-integer coeffs: {len(nonint)}  "
              f"{'OK' if bad == 0 and not nonint else 'FAIL'}")
        assert bad == 0 and not nonint


if __name__ == "__main__":
    main()
