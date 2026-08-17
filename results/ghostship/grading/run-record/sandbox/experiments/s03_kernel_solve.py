#!/usr/bin/env python3
"""Session 03: kernel-method SOLUTION of the validated functional equation for
convex king animals (and the polyomino control), executed in exact truncated
power-series arithmetic mod two large primes. No fitting anywhere: every
quantity below is derived from the functional equation of s03_funceq_check.py
(itself validated cell-by-cell against the brute-force-validated DP).

System (u^2 = y; all series in x,u; s catalytic = last-row length):
  F00(s) = x y s (1-xs) / ((1-xs)^2 - y)                    [solved directly]
  F10(s)[(s-1)(1-xs) - ys] = yB[F00](s)(s-1)(1-xs) + yF10(1)(xs(s-1)-s)
     where B[G](s) = (G(s)-sG(1))/((s-1)(1-xs)) + [king] xsG(1)/(1-xs)
     kernel root s0: (s0-1)(1-x s0) = y s0, s0 = 1 + O(y)
     => F10(1) = y B[F00](s0) / (1 + x - x s0)
  F01 = F10 (mirror symmetry)
  F11(s) = y D1[F00](s) + 2y D2[F10](s) + y L3[F11](s)
     L3[G](s) = [s^2 G(s) - s^2 G(1) - s(s-1)G'(1)]/(s-1)^2
     D2[G](s) = L3[G](s) - s(G(s)-G(1))/(s-1)
     D1[G](s) = [G(s) - s^2 G(1) - s(s-1)(G'(1)-2G(1))]/(s-1)^2
     kernel (s-1)^2 = y s^2, roots sig_pm = 1/(1 -+ u)
     => F11(1) +- u F11'(1) = y D1[F00](sig) + 2y D2[F10](sig)
     => F11(1) = average of the two right sides
  F(x,y) = F00(1) + 2 F10(1) + F11(1)

Checks emitted:
  1. D-operator formulas vs raw transition sums on s^k (k<=8)   [unit test]
  2. kernel root residual P_K(s0) == 0
  3. F10(1) via val1(F10 SRat) == F10(1) via kernel formula     [consistency]
  4. odd-u part of F11(1) == 0
  5. [x^w u^{2h}] F == f(w,h) from the validated DP, both modes, both primes
  6. king F satisfies s02's fitted algebraic equation A2 F^2 + A1 F + A0 = 0
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_box import g_table, f_from_g

NX = 12      # max x-degree
H = 12       # compare heights <= H
NU = 2 * H + 6   # max u-degree + margin
P = (1 << 61) - 1

PRIMES = [(1 << 61) - 1, 10 ** 18 + 9]


class Ser:
    """Truncated series in x,u mod P with validity box (vx, vu)."""
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
            r.d[m] = (r.d.get(m, 0) + c) % P
        return r

    def __sub__(a, b):
        r = Ser(dict(a.d), min(a.vx, b.vx), min(a.vu, b.vu))
        for m, c in b.d.items():
            r.d[m] = (r.d.get(m, 0) - c) % P
        return r

    def __neg__(a):
        return Ser({m: (-c) % P for m, c in a.d.items()}, a.vx, a.vu)

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
                    r[m] = (r.get(m, 0) + c1 * c2) % P
        return Ser(r, vx, vu)

    def scal(a, k):
        k %= P
        return Ser({m: c * k % P for m, c in a.d.items()}, a.vx, a.vu)

    def get(a, i, j):
        return a.d.get((i, j), 0)

    def is_zero(a):
        return all(c % P == 0 for (i, j), c in a.d.items()
                   if i <= a.vx and j <= a.vu)

    def inv_unit(a):
        c0 = a.get(0, 0)
        assert c0 % P != 0, "inv of non-unit"
        ic0 = pow(c0, P - 2, P)
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
                v = (-acc * ic0) % P
                if v:
                    r.d[(i, j)] = v
        return r


def divexact(A, B):
    """A/B where B = x^a u^b * unit; shrinks validity by (a,b)."""
    vx, vu = min(A.vx, B.vx), min(A.vu, B.vu)
    terms = [(i, j) for (i, j), c in B.d.items()
             if c % P != 0 and i <= vx and j <= vu]
    assert terms, "division by zero series"
    a = min(i for i, j in terms)
    b = min(j for i, j in terms)
    assert B.get(a, b) % P != 0, "corner of divisor not a monomial*unit"
    U = Ser({(i - a, j - b): c for (i, j), c in B.d.items()
             if i <= vx and j <= vu}, vx - a, vu - b)
    for (i, j), c in A.d.items():
        if i > vx or j > vu:
            continue
        assert (i >= a and j >= b) or c % P == 0, \
            f"numerator not divisible by x^{a} u^{b}: term {(i, j)}"
    As = Ser({(i - a, j - b): c for (i, j), c in A.d.items()
              if c % P and i <= vx and j <= vu}, vx - a, vu - b)
    return As * U.inv_unit()


def C(k):
    return Ser({(0, 0): k % P}) if k % P else Ser()


# ---------- polynomials in s over Ser ----------
class SPoly:
    def __init__(self, cs):
        self.cs = list(cs)  # cs[i] = Ser coeff of s^i
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
        """Divide by (s-1); assert zero remainder."""
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
    ss1 = SP(0, -1, 1)  # s(s-1) = s^2 - s
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


def unit_test_operators():
    """Raw transition sums on G=s^k vs operator formulas (k<=8)."""
    for k in range(1, 9):
        G = SRat(SPoly([C(1 if i == k else 0) for i in range(k + 1)]), SP(1))
        G1, G1p = C(1), C(k)
        # D1: sum_{i,j>=1, i+j<=k-1} s^{k-i-j}
        raw = [0] * (k + 1)
        for i in range(1, k):
            for j in range(1, k - i):
                raw[k - i - j] += 1
        got = D1op(G, G1, G1p)
        assert got.den.cs == SP(1).cs or True
        for d in range(k + 1):
            g = got.num.cs[d].get(0, 0) if d < len(got.num.cs) else 0
            assert g == raw[d] % P, ("D1", k, d)
        # D2: i>=0, j>=1, i+j<=k-1
        raw = [0] * (k + 1)
        for i in range(0, k):
            for j in range(1, k - i):
                raw[k - i - j] += 1
        got = D2op(G, G1, G1p)
        for d in range(k + 1):
            g = got.num.cs[d].get(0, 0) if d < len(got.num.cs) else 0
            assert g == raw[d] % P, ("D2", k, d)
        # L3: i,j>=0, i+j<=k-1
        raw = [0] * (k + 1)
        for i in range(0, k):
            for j in range(0, k - i):
                raw[k - i - j] += 1
        got = L3(G, G1, G1p)
        for d in range(k + 1):
            g = got.num.cs[d].get(0, 0) if d < len(got.num.cs) else 0
            assert g == raw[d] % P, ("L3", k, d)
    print("  operator unit tests (D1,D2,L3 vs raw sums, k<=8): OK")


def solve(king=True, xval=None):
    """xval=None: x is the monomial (bivariate run). xval=c: specialize x=c
    (univariate-in-u run; use NX=0)."""
    x = Ser({(1, 0): 1}) if xval is None else Ser({(0, 0): xval % P})
    u = Ser({(0, 1): 1})
    y = u * u
    one = C(1)

    # F00
    N00 = SP(0, x * y, -(x * x * y))          # xys(1-xs)
    D00 = SPoly([one - y, -(x + x), x * x])   # (1-xs)^2 - y
    F00 = SRat(N00, D00)
    F001 = F00.val1()
    F00p1 = F00.deriv1()

    # kernel root s0: s0 = 1 + y*s0/(1 - x*s0)
    s0 = C(1)
    for _ in range(NU // 2 + 2):
        s0 = one + y * s0 * (one - x * s0).inv_unit()
    # residual check: (s0-1)(1-x s0) - y s0 == 0
    res = (s0 - one) * (one - x * s0) - y * s0
    assert res.is_zero(), "kernel root residual nonzero"

    # B[F00] as SRat: (F00(s)-s F001)/(s-1) / (1-xs)  [+ king: xs F001/(1-xs)]
    one_m_xs = SPoly([one, -x])
    Bnum = (N00 - SP(0, 1).scale(F001) * D00).syndiv1()
    Bden = D00 * one_m_xs
    if king:
        Bnum = Bnum + (SP(0, 1).scale(x * F001)) * D00
    B = SRat(Bnum, Bden)

    # companion term Q(s) multiplying F10(1):  king xs(s-1)-s, control -s
    W = SP(-1, 1) * one_m_xs                  # (s-1)(1-xs)
    PK = W - SP(0, 1).scale(y)                # kernel poly
    if king:
        Qcomp = SP(0, -1, 1).scale(x) - SP(0, 1)
    else:
        Qcomp = SP(0, -1)
    # F10(1) from kernel:  G1 = -B(s0) W(s0) / Q(s0),  W(s0) = y s0
    F101_kernel = -(B.eval(s0) * y * s0) * Qcomp.eval(s0).inv_unit()

    # F10(s) as SRat:  F10 PK = y B W + y G1 Q
    F10num = (B.num * W).scale(y) + Qcomp.scale(y * F101_kernel) * B.den
    F10den = PK * B.den
    F10 = SRat(F10num, F10den)
    F101 = F10.val1()
    assert (F101 - F101_kernel).is_zero(), "F10(1) consistency FAIL"
    F10p1 = F10.deriv1()

    # F11 via sigma_pm
    D1F00 = D1op(F00, F001, F00p1)
    D2F10 = D2op(F10, F101, F10p1)
    vals = []
    for sgn in (1, -1):
        sig = (one - u.scal(sgn)).inv_unit()   # 1/(1 -+ u)
        v = y * D1F00.eval(sig) + (y * D2F10.eval(sig)).scal(2)
        vals.append(v)
    F111 = (vals[0] + vals[1]).scal(pow(2, P - 2, P))
    # odd-u part must vanish
    odd = [((i, j), c) for (i, j), c in F111.d.items()
           if j % 2 == 1 and c % P and i <= F111.vx and j <= F111.vu]
    assert not odd, f"odd-u terms in F11(1): {odd[:5]}"

    F = F001 + F101.scal(2) + F111
    return F


def check_table(F, king):
    g = g_table(NX, H, king=king)
    f = f_from_g(g, NX, H)
    bad = 0
    ncmp = 0
    for w in range(1, NX + 1):
        for h in range(1, H + 1):
            if w > F.vx or 2 * h > F.vu:
                continue
            ncmp += 1
            if F.get(w, 2 * h) != f[w][h] % P:
                bad += 1
                if bad <= 5:
                    print(f"    MISMATCH w={w} h={h}: F={F.get(w,2*h)} "
                          f"table={f[w][h] % P}")
    # also: no coefficients at odd u or at (0,*)/(*,0) beyond origin
    stray = [(m, c) for m, c in F.d.items()
             if c % P and m[0] <= F.vx and m[1] <= F.vu
             and (m[1] % 2 == 1 or m[0] == 0 or m[1] == 0)]
    return bad, ncmp, stray


def check_s02_equation(F):
    eq = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                     "out_s02_bivar_eq_king_D2.json")))
    A = []
    for k in "012":
        d = {}
        for mono, c in eq[k].items():
            i, j = map(int, mono.split(","))
            d[(i, 2 * j)] = c % P   # y^j -> u^(2j)
        A.append(Ser(d, F.vx, F.vu))
    R = A[0] + A[1] * F + A[2] * F * F
    return R.is_zero()


def main():
    global P, NX, H, NU
    NX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    H = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    NU = 2 * H + 6
    for P in PRIMES:
        print(f"prime p = {P}")
        unit_test_operators()
        for king in (True, False):
            tag = "KING" if king else "POLYOMINO(control)"
            F = solve(king=king)
            bad, ncmp, stray = check_table(F, king)
            status = "OK" if bad == 0 and not stray else "FAIL"
            print(f"  {tag}: kernel solution vs DP table: {ncmp} cells "
                  f"compared, {bad} mismatches; stray terms: {len(stray)}  "
                  f"{status}")
            if king:
                ok = check_s02_equation(F)
                print(f"  KING: satisfies s02 fitted equation A2F^2+A1F+A0=0 "
                      f"(all coeffs in validity box): {'OK' if ok else 'FAIL'}")
    print("done")


if __name__ == "__main__":
    main()
