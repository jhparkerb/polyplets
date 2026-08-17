#!/usr/bin/env python3
"""Session 03: degree-bound tracker for the kernel-method pipeline.

Mirrors every field operation of s03_kernel_solve.solve() in a degree-bound
semiring over the tower T = Q(x,u)[r], r^2 = Delta(x, y=u^2), u = sqrt(y).
Each element is tracked as   (a + b*r) / D   with
  a, b : degree bounds (deg_x, deg_u) of the numerator components (None = 0),
  D    : formal product of registered ATOMS (each atom = a polynomial that was
         actually inverted in the pipeline, with its own degree bound).
Additions take atom-wise max multiplicity (LCM-style), which is exact for the
common case den1 == den2 and a valid upper bound in general.  All bounds are
provable upper bounds on the true degrees.

Output: degree bounds (deg_x, deg_u) for the numerator components P, Q of the
final identity  2*K*Delta^2*F + M + S*r = (P + Q*r)/D, and the verification
box (2*max_x+2, 2*max_u+4) that a truncated-series check must cover so that
box-vanishing implies P = Q = 0 exactly (lex-min/Newton-polytope argument,
using that Delta is not a square in Q(x,y)).
"""
DEGD = (2, 4)   # degree of Delta in (x,u)

atoms = {}      # id -> (dx, du) bound
def register_atom(bnd):
    i = len(atoms)
    atoms[i] = bnd
    return i

def dsize(D):
    dx = sum(atoms[i][0] * m for i, m in D.items())
    du = sum(atoms[i][1] * m for i, m in D.items())
    return (dx, du)

def bmax(p, q):
    if p is None:
        return q
    if q is None:
        return p
    return (max(p[0], q[0]), max(p[1], q[1]))

def badd(p, q):
    if p is None or q is None:
        return None
    return (p[0] + q[0], p[1] + q[1])


class E:
    """Tower element bound: (a + b r)/D."""
    def __init__(self, a, b=None, D=None):
        self.a, self.b = a, b
        self.D = dict(D or {})

    def _common(self, o):
        return {i: max(self.D.get(i, 0), o.D.get(i, 0))
                for i in set(self.D) | set(o.D)}

    def _lift(self, D):
        """Numerator bounds when rewritten over superset denominator D."""
        extra = {i: m - self.D.get(i, 0) for i, m in D.items()}
        ex = (sum(atoms[i][0] * m for i, m in extra.items()),
              sum(atoms[i][1] * m for i, m in extra.items()))
        return badd(self.a, ex), badd(self.b, ex)

    def __add__(s, o):
        D = s._common(o)
        a1, b1 = s._lift(D)
        a2, b2 = o._lift(D)
        return E(bmax(a1, a2), bmax(b1, b2), D)

    __sub__ = __add__

    def __neg__(s):
        return E(s.a, s.b, s.D)

    def __mul__(s, o):
        D = {i: s.D.get(i, 0) + o.D.get(i, 0)
             for i in set(s.D) | set(o.D)}
        a = bmax(badd(s.a, o.a), badd(badd(s.b, o.b), DEGD))
        b = bmax(badd(s.a, o.b), badd(s.b, o.a))
        return E(a, b, D)

    def scal(s, k):
        return E(s.a, s.b, s.D)

    def inv_unit(s):
        # 1/((a+br)/D) = D*(a-br)/(a^2-b^2*Delta); register norm as atom
        norm = bmax(badd(s.a, s.a), badd(badd(s.b, s.b), DEGD))
        i = register_atom(norm)
        ds = dsize(s.D)
        return E(badd(s.a, ds), badd(s.b, ds), {i: 1})

    def numbound(s):
        return bmax(s.a, s.b), s.a, s.b


def divexact(A, B):
    return A * B.inv_unit()


ZERO = E(None)
def C(k):
    return E((0, 0)) if k else ZERO


class SPoly:
    def __init__(self, cs):
        self.cs = list(cs)

    def __add__(a, b):
        n = max(len(a.cs), len(b.cs))
        g = lambda l, i: l[i] if i < len(l) else ZERO
        return SPoly([g(a.cs, i) + g(b.cs, i) for i in range(n)])

    __sub__ = __add__

    def __mul__(a, b):
        n = len(a.cs) + len(b.cs) - 1
        out = [ZERO] * n
        for i, ca in enumerate(a.cs):
            for j, cb in enumerate(b.cs):
                out[i + j] = out[i + j] + ca * cb
        return SPoly(out)

    def scale(a, k):  # k = E
        return SPoly([c * k for c in a.cs])

    def eval(a, pt):
        r = a.cs[-1]
        for c in reversed(a.cs[:-1]):
            r = r * pt + c
        return r

    def val1(a):
        r = a.cs[0]
        for c in a.cs[1:]:
            r = r + c
        return r

    def deriv(a):
        return SPoly(a.cs[1:]) if len(a.cs) > 1 else SPoly([ZERO])

    def syndiv1(a):
        q = [ZERO] * (len(a.cs) - 1)
        acc = a.cs[-1]
        for i in range(len(a.cs) - 2, -1, -1):
            q[i] = acc
            acc = acc + a.cs[i]
        return SPoly(q) if q else SPoly([ZERO])


def SP(*cs):
    return SPoly([c if isinstance(c, E) else C(c) for c in cs])


class SRat:
    def __init__(self, num, den):
        self.num, self.den = num, den

    def val1(self):
        return divexact(self.num.val1(), self.den.val1())

    def deriv1(self):
        n1, d1 = self.num.val1(), self.den.val1()
        np1, dp1 = self.num.deriv().val1(), self.den.deriv().val1()
        return divexact(np1 * d1 + n1 * dp1, d1 * d1)

    def eval(self, pt):
        return divexact(self.num.eval(pt), self.den.eval(pt))


def L3(G, G1, G1p):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, 1, 1)
    num = s2 * G.num + (s2.scale(G1) + ss1.scale(G1p)) * G.den
    num = num.syndiv1().syndiv1()
    return SRat(num, G.den)


def D2op(G, G1, G1p):
    L = L3(G, G1, G1p)
    num2 = (SP(0, 1) * G.num + SP(0, 1).scale(G1) * G.den).syndiv1()
    return SRat(L.num + num2, G.den)


def D1op(G, G1, G1p):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, 1, 1)
    num = G.num + (s2.scale(G1) + ss1.scale(G1p + G1.scal(2))) * G.den
    num = num.syndiv1().syndiv1()
    return SRat(num, G.den)


def solve_bounds(king=True):
    x = E((1, 0))
    u = E((0, 1))
    y = E((0, 2))
    one = E((0, 0))
    r = E(None, (0, 0))

    N00 = SP(0, E((2, 2)), E((2, 2)))          # xys(1-xs)
    D00 = SP(E((0, 2)), E((1, 0)), E((2, 0)))  # (1-xs)^2 - y
    F00 = SRat(N00, D00)
    F001 = F00.val1()
    F00p1 = F00.deriv1()

    # s0 = ((1+x-y) - r)/(2x): register atom for x
    ax = register_atom((1, 0))
    s0 = E((1, 2), (0, 0), {ax: 1})

    one_m_xs = SP(one, x)
    Bnum = (N00 + SP(0, 1).scale(F001) * D00).syndiv1()
    Bden = D00 * one_m_xs
    if king:
        Bnum = Bnum + (SP(0, 1).scale(x * F001)) * D00
    B = SRat(Bnum, Bden)

    W = SP(1, 1) * one_m_xs
    PK = W + SP(0, 1).scale(y)
    if king:
        Qcomp = SP(0, 1, 1).scale(x) + SP(0, 1)
    else:
        Qcomp = SP(0, 1)
    F101 = (B.eval(s0) * y * s0) * Qcomp.eval(s0).inv_unit()

    F10num = (B.num * W).scale(y) + Qcomp.scale(y * F101) * B.den
    F10den = PK * B.den
    F10 = SRat(F10num, F10den)
    F10p1 = F10.deriv1()

    D1F00 = D1op(F00, F001, F00p1)
    D2F10 = D2op(F10, F101, F10p1)
    vals = []
    for sgn in (1, -1):
        au = register_atom((0, 1))              # atom 1 -+ u
        sig = E((0, 0), None, {au: 1})          # 1/(1 -+ u)
        v = y * D1F00.eval(sig) + (y * D2F10.eval(sig)).scal(2)
        vals.append(v)
    F111 = (vals[0] + vals[1]).scal(1)
    F = F001 + F101.scal(2) + F111

    # identity: 2 K Delta^2 * F + M + S*r
    poly = lambda dx, du: E((dx, du))
    KD2 = poly(5, 10)   # 2*K*Delta^2
    M = poly(5, 10)
    S = poly(4, 8)
    T1 = KD2 * F + M + S * r
    return F, T1


for king in (True, False):
    atoms.clear()
    F, T1 = solve_bounds(king)
    nb, a, b = T1.numbound()
    ds = dsize(T1.D)
    print(("KING" if king else "CONTROL") + ":")
    print(f"  final F: a<={F.a} b<={F.b} den atoms size {dsize(F.D)}")
    print(f"  identity numerator components: P<={a}  Q<={b}")
    print(f"  identity denominator size: {ds}")
    bx = 2 * max(a[0], b[0]) + 2
    bu = 2 * max(a[1], b[1]) + 4
    print(f"  => sufficient verification box: x-deg <= {bx}, u-deg <= {bu}")
