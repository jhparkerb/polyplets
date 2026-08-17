#!/usr/bin/env python3
"""Session 09: leading singular coefficients of the area-moment GFs A_r(t)
of convex king animals at t=1/4, for r far beyond the banked r<=4 — via the
SLICE x=1/4 of the s08 Temperley moment-kernel recursion.

Idea. The s08-derived bivariate moment GFs M_r(x,y) live in Q(x,y,sqrt(D)),
D = (1-x-y)^2-4xy, with conjectured denominator K^(r+1) D^(2r+2),
K = x+y+xy.  Writing M_r ~ C_r(x,y)/D^(2r+2) near D=0, the univariate
diagonal A_r(t)=M_r(t,t) has D(t,t)=1-4t, so

    A_r(t) ~ c_r/(1-4t)^(2r+2),   c_r = C_r(1/4,1/4).

The slice x=1/4 crosses D=0 transversally at y=1/4
(D(1/4,y) = (y-1/4)(y-9/4)), so C_r(1/4,1/4) is computable from the slice:
with S_r(y) := M_r(1/4,y),

    S_r(y) * Kx^(r+1) * Dx^(2r+2) = P_r(y) + Q_r(y)*sqrt(Dx),
    Kx=(1+5y)/4, Dx=(y-1/4)(y-9/4),
    c_r = P_r(1/4)/(9/16)^(r+1),  and the sqrt-correction
    cQ_r = Q_r(1/4)/(9/16)^(r+1)  (coefficient of (1-4t)^-(2r+3/2)).

Limit-law equivalence (s01 firm: a_0(s) ~ (s/128) 4^s, i.e. c_0=1/128):
E[area^r]/s^(2r) -> 128 c_r/(2r+1)!, and area/s^2 ->d U(1-U)/2 at moment
level iff  c_r = (r!)^2 / 2^(r+7)  for all r.  Banked anchors r<=4 agree.

Computation. With x NUMERIC (=1/4 mod p) the s08 recursion collapses to
ONE series variable u (y=u^2): scalars = truncated u-series mod p (K3.Ser
with NX=0).  To reach r=8 the s08 SRat denominators (which grow like 3^r)
are replaced by FRat: rational functions in s with denominator kept as a
FACTORED multiset over the fixed atom registry

    a0 = 1-xs,  a1 = D00 = (1-xs)^2-y,  a2 = PK1 = ((s-1)(1-xs)-ys)/(s-s0)

(all unit leading s-coefficient since x is numeric), with lcm-based
addition, ladder reuse of D=s d/ds derivatives across levels, and exact
factor cancellation (trial division) after every operation that grows
degrees.  Everything mod two 61-bit primes independently; rationals
recovered by CRT + Wang reconstruction.

Checks:
  S0  slice series of level 0 == s03 PROVEN closed form
      -(M + 2x^2y^2(1+x+y)^2 sqrt(D))/(2K D^2) at x=1/4      (all terms)
  S1  slice series of level 1 == s07/s08 bivariate M1 closed form
      (A + B sqrt(D))/(K^2 D^4) at x=1/4                     (all terms)
  S2  fits P_r,Q_r pass with >= SURPLUS_MIN surplus equations at the
      conjectured denominator (denominator law on the slice, every r)
  S3  (cP_r, cQ_r) for r<=4 == the same constants from the BANKED diagonal
      closed forms A_r(t) (s01/s03 r=0, s07 r=1,2, s07/s08 r=3,4)
  S4  HEADLINE: cP_r == (r!)^2/2^(r+7) for r=0..MAXR, king AND control

Usage: python3 experiments/s09_slice_moments.py [MAXR] [NU]
Output: out_s12_slice_r12.txt, out_s12_slice_PQ_r12.json
"""
import sys, os, json, time
from math import comb
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s03_kernel_solve as K3
from s03_kernel_solve import SPoly, Ser, divexact

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 8
NUARG = int(sys.argv[2]) if len(sys.argv) > 2 else 300
PHASES = len(sys.argv) > 3 and sys.argv[3] == "phases"
PRIMES = [(1 << 61) - 1, 10 ** 18 + 9]
SURPLUS_MIN = 12

OUT = []


def say(msg):
    print(msg, flush=True)
    OUT.append(str(msg))


def C(k):
    return K3.C(k)


def SP(*cs):
    return SPoly([c if isinstance(c, Ser) else C(c) for c in cs])


def sdiv_root(N, r):
    cs = N.cs
    n = len(cs) - 1
    if n == 0:
        return SPoly([Ser()]), cs[0]
    q = [None] * n
    acc = cs[n]
    for i in range(n - 1, -1, -1):
        q[i] = acc
        acc = cs[i] + acc * r
    return SPoly(q), acc


def polydiv(N, Dp):
    """Divide SPoly N by SPoly Dp (unit leading scalar coeff).
    Return (quotient, remainder_is_zero)."""
    dd = len(Dp.cs) - 1
    Li = Dp.cs[-1].inv_unit()
    rem = [c.copy() for c in N.cs]
    nq = len(rem) - 1 - dd
    if nq < 0:
        return None, N.cs and all(c.is_zero() for c in N.cs)
    q = [None] * (nq + 1)
    for k in range(nq, -1, -1):
        c = rem[k + dd] * Li
        q[k] = c
        for j in range(dd + 1):
            rem[k + j] = rem[k + j] - c * Dp.cs[j]
    ok = all(rem[j].is_zero() for j in range(dd))
    return SPoly(q), ok


def polydiv_exact(N, Dp, tag):
    q, ok = polydiv(N, Dp)
    assert q is not None and ok, f"polydiv {tag}: not exact"
    return q


def sqrt_ser(A):
    """sqrt of Ser with constant term 1 (Newton, mod P)."""
    inv2 = pow(2, K3.P - 2, K3.P)
    r = C(1)
    for _ in range(16):
        r = (r + A * r.inv_unit()).scal(inv2)
    assert (r * r - A).is_zero(), "sqrt_ser failed"
    return r


# ---------------- FRat: rational function with factored denominator ------
class Ctx:
    pass


class FRat:
    __slots__ = ("num", "e", "ctx")

    def __init__(self, num, e, ctx):
        self.num, self.e, self.ctx = num, tuple(e), ctx

    def denpoly(self):
        return self.ctx.denpoly(self.e)

    def lift(self, E):
        """numerator w.r.t. the larger denominator exponent vector E."""
        n = self.num
        for i, (Ei, ei) in enumerate(zip(E, self.e)):
            assert Ei >= ei
            if Ei > ei:
                n = n * self.ctx.atom_pow(i, Ei - ei)
        return n

    def scal(self, k):  # k Ser or int
        if isinstance(k, int):
            return FRat(SPoly([c.scal(k) for c in self.num.cs]), self.e,
                        self.ctx)
        return FRat(self.num.scale(k), self.e, self.ctx)

    def D(self):
        """s d/ds, denominator exponents +1 on active atoms."""
        ctx = self.ctx
        act = [i for i, ei in enumerate(self.e) if ei > 0]
        Pact = SP(1)
        for i in act:
            Pact = Pact * ctx.atoms[i]
        num = self.num.deriv() * Pact
        for i in act:
            Pothers = SP(1)
            for j in act:
                if j != i:
                    Pothers = Pothers * ctx.atoms[j]
            num = num - self.num * ctx.datoms[i] * Pothers.scale(C(self.e[i]))
        num = SP(0, 1) * num
        e2 = tuple(ei + (1 if ei > 0 else 0) for ei in self.e)
        return FRat(num, e2, ctx)

    def reduce(self):
        ctx = self.ctx
        num, e = self.num, list(self.e)
        for i, a in enumerate(ctx.atoms):
            while e[i] > 0:
                q, ok = polydiv(num, a)
                if q is None or not ok:
                    break
                num = q
                e[i] -= 1
        return FRat(num, e, ctx)

    def eval(self, key):
        """evaluate at named point ('s0','sigp','sigm'); returns Ser."""
        ctx = self.ctx
        nv = self.num.eval(ctx.pts[key])
        dv = ctx.den_eval(key, self.e)
        return divexact(nv, dv)

    def val1(self):
        d1 = self.ctx.den_val1(self.e)
        return divexact(self.num.val1(), d1)

    def deriv1(self):
        ctx = self.ctx
        n1 = self.num.val1()
        np1 = self.num.deriv().val1()
        d1 = ctx.den_val1(self.e)
        dp1 = Ser()
        for i, ei in enumerate(self.e):
            if ei:
                t = ctx.datom_val1[i].scal(ei)
                for j, ej in enumerate(self.e):
                    p = ej - (1 if j == i else 0)
                    if p:
                        t = t * ctx.atom_val1_pow(j, p)
                dp1 = dp1 + t
        return divexact(np1 * d1 - n1 * dp1, d1 * d1)


def frat_add(*As):
    ctx = As[0].ctx
    E = tuple(max(a.e[i] for a in As) for i in range(len(As[0].e)))
    num = As[0].lift(E)
    for a in As[1:]:
        num = num + a.lift(E)
    return FRat(num, E, ctx)


# ---------------- context on the slice x = x0 ----------------------------
def build_ctx(king, x0num, x0den):
    P = K3.P
    ctx = Ctx()
    x = C(x0num * pow(x0den, P - 2, P) % P)
    u = Ser({(0, 1): 1})
    y = u * u
    one = C(1)
    ctx.x, ctx.u, ctx.y, ctx.one = x, u, y, one
    one_m_xs = SPoly([one, -x])
    W = SP(-1, 1) * one_m_xs
    PK = W - SP(0, 1).scale(y)
    # Newton for the kernel root s0 (power-series branch, s0 = 1 + O(y)):
    # PK(s) = -x s^2 + (1+x-y)s - 1
    b = one + x - y
    s0 = C(1)
    for _ in range(12):
        val = -(x * s0 * s0) + b * s0 - one
        dval = -(x * s0).scal(2) + b
        s0 = s0 - val * dval.inv_unit()
    assert ((s0 - one) * (one - x * s0) - y * s0).is_zero(), "s0 residual"
    PK1, remPK = sdiv_root(PK, s0)
    assert remPK.is_zero(), "PK not divisible by (s-s0)"
    D00 = SPoly([one - y, -(x + x), x * x])
    ctx.atoms = [one_m_xs, D00, PK1]
    ctx.datoms = [a.deriv() for a in ctx.atoms]
    ctx.one_m_xs, ctx.D00, ctx.PK1, ctx.W = one_m_xs, D00, PK1, W
    if king:
        ctx.Qcomp = SP(0, -1, 1).scale(x) - SP(0, 1)
    else:
        ctx.Qcomp = SP(0, -1)
    ctx.pts = {"s0": s0,
               "sigp": (one - u).inv_unit(),
               "sigm": (one + u).inv_unit()}
    ctx._apow = {}
    ctx._dp = {}
    ctx._aev = {}
    ctx._av1 = {}

    def atom_pow(i, e):
        key = (i, e)
        if key not in ctx._apow:
            r = SP(1)
            for _ in range(e):
                r = r * ctx.atoms[i]
            ctx._apow[key] = r
        return ctx._apow[key]

    def denpoly(E):
        E = tuple(E)
        if E not in ctx._dp:
            r = SP(1)
            for i, ei in enumerate(E):
                if ei:
                    r = r * atom_pow(i, ei)
            ctx._dp[E] = r
        return ctx._dp[E]

    def den_eval(key, E):
        r = C(1)
        for i, ei in enumerate(E):
            if ei:
                k2 = (key, i, ei)
                if k2 not in ctx._aev:
                    base = ctx.atoms[i].eval(ctx.pts[key])
                    v = base
                    for _ in range(ei - 1):
                        v = v * base
                    ctx._aev[k2] = v
                r = r * ctx._aev[k2]
        return r

    ctx.atom_val1 = [a.val1() for a in ctx.atoms]
    ctx.datom_val1 = [a.val1() for a in ctx.datoms]

    def atom_val1_pow(i, e):
        key = (i, e)
        if key not in ctx._av1:
            v = C(1)
            for _ in range(e):
                v = v * ctx.atom_val1[i]
            ctx._av1[key] = v
        return ctx._av1[key]

    def den_val1(E):
        r = C(1)
        for i, ei in enumerate(E):
            if ei:
                r = r * atom_val1_pow(i, ei)
        return r

    ctx.atom_pow, ctx.denpoly = atom_pow, denpoly
    ctx.den_eval, ctx.den_val1 = den_eval, den_val1
    ctx.atom_val1_pow = atom_val1_pow
    ctx.king = king
    return ctx


# ---------------- operators (FRat versions of s03/s08) -------------------
def B_op(G, G1, ctx):
    num = (G.num - SP(0, 1).scale(G1) * G.denpoly()).syndiv1()
    if ctx.king:
        num = num + SP(0, 1).scale(ctx.x * G1) * G.denpoly()
    e = list(G.e)
    e[0] += 1  # * 1/(1-xs)
    return FRat(num, e, ctx)


def D1op(G, G1, G1p, ctx):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, -1, 1)
    num = G.num - (s2.scale(G1) + ss1.scale(G1p - G1.scal(2))) * G.denpoly()
    num = num.syndiv1().syndiv1()
    return FRat(num, G.e, ctx)


def D2op(G, G1, G1p, ctx):
    s2 = SP(0, 0, 1)
    ss1 = SP(0, -1, 1)
    numL = s2 * G.num - (s2.scale(G1) + ss1.scale(G1p)) * G.denpoly()
    numL = numL.syndiv1().syndiv1()
    num2 = (SP(0, 1) * G.num - SP(0, 1).scale(G1) * G.denpoly()).syndiv1()
    return FRat(numL - num2, G.e, ctx)


def solve_level(M00, I10, I11, ctx):
    """level solver, FRat edition (mirrors s08 solve_level)."""
    inv2 = pow(2, K3.P - 2, K3.P)
    u, y = ctx.u, ctx.y
    M001 = M00.val1()
    M00p1 = M00.deriv1()
    BM = B_op(M00, M001, ctx)

    T = BM.eval("s0") * y + I10.eval("s0")
    s0 = ctx.pts["s0"]
    M101 = -(T * s0 * ctx.Qcomp.eval(s0).inv_unit())
    E = tuple(max(a, b) for a, b in zip(BM.e, I10.e))
    num_raw = ((BM.lift(E).scale(y) + I10.lift(E)) * ctx.W
               + ctx.Qcomp.scale(y * M101) * ctx.denpoly(E))
    Q1, rem = sdiv_root(num_raw, s0)
    assert rem.is_zero(), "staircase numerator not killed at s0"
    e10 = list(E)
    e10[2] += 1  # * 1/PK1
    M10 = FRat(Q1, e10, ctx).reduce()
    assert (M10.val1() - M101).is_zero(), "M10(1) consistency"
    M10p1 = M10.deriv1()

    D1M = D1op(M00, M001, M00p1, ctx)
    D2M = D2op(M10, M101, M10p1, ctx)
    A2M = frat_add(D1M.scal(y), D2M.scal(y.scal(2)), I11)
    vp, vm = A2M.eval("sigp"), A2M.eval("sigm")
    M111 = (vp + vm).scal(inv2)
    odd = [m for m, c in M111.d.items()
           if m[1] % 2 == 1 and c % K3.P and m[1] <= M111.vu]
    assert not odd, f"odd-u part of M11(1): {odd[:4]}"
    M11p1 = divexact(vp - vm, u.scal(2))
    K11 = SPoly([ctx.one, C(-2), ctx.one - y])
    numM11 = (A2M.num * SP(1, -2, 1)
              - (SP(0, 0, 1).scale(M111)
                 + SP(0, -1, 1).scale(M11p1)).scale(y) * A2M.denpoly())
    Q11 = polydiv_exact(numM11, K11, "closing")
    M11 = FRat(Q11, A2M.e, ctx).reduce()
    assert (M11.val1() - M111).is_zero(), "M11(1) consistency"
    assert (M11.deriv1() - M11p1).is_zero(), "M11'(1) consistency"

    tot = M001 + M101.scal(2) + M111
    return dict(M00=M00, M10=M10, M11=M11, tot=tot)


def solve_all_levels(king, maxr, x0num, x0den):
    ctx = build_ctx(king, x0num, x0den)
    x, y, one = ctx.x, ctx.y, ctx.one
    N00 = SP(0, x * y, -(x * x * y))
    F00 = FRat(N00, (0, 1, 0), ctx)
    zero = FRat(SP(0), (0, 0, 0), ctx)
    L0 = solve_level(F00, zero, zero, ctx)
    levels = [L0]
    lad = {ph: {0: [L0[ph]]} for ph in ("M00", "M10", "M11")}
    for r in range(1, maxr + 1):
        t0 = time.time()
        I = {}
        for ph in ("M00", "M10", "M11"):
            for k in range(r):
                while len(lad[ph][k]) <= r - k:
                    lad[ph][k].append(lad[ph][k][-1].D().reduce())
            I[ph] = frat_add(*[
                lad[ph][k][r - k].scal((-1) ** (r - 1 - k) * comb(r, k))
                for k in range(r)])
        M00r = FRat(I["M00"].num * ctx.atom_pow(0, 2),
                    (I["M00"].e[0], I["M00"].e[1] + 1, I["M00"].e[2]),
                    ctx).reduce()
        Lr = solve_level(M00r, I["M10"].reduce(), I["M11"].reduce(), ctx)
        levels.append(Lr)
        for ph in ("M00", "M10", "M11"):
            lad[ph][r] = [Lr[ph]]
        say(f"    level {r}: {time.time()-t0:.1f}s  "
            f"degs num M00/M10/M11 = "
            f"{len(Lr['M00'].num.cs)-1}/{len(Lr['M10'].num.cs)-1}/"
            f"{len(Lr['M11'].num.cs)-1}  den e = "
            f"{Lr['M00'].e}/{Lr['M10'].e}/{Lr['M11'].e}  "
            f"tot.vu={Lr['tot'].vu}")
    return ctx, levels


# ---------------- univariate y-series helpers (lists mod P) --------------
def ser_to_ylist(S, ny):
    """Ser in u (even part) -> list of y-coefficients, checking oddness."""
    P = K3.P
    for (i, j), c in S.d.items():
        assert j % 2 == 0 or c % P == 0 or j > S.vu, f"odd term u^{j}"
    return [S.get(0, 2 * n) % P for n in range(ny)]


def ymul(a, b, ny):
    P = K3.P
    r = [0] * ny
    for i, ai in enumerate(a):
        if ai and i < ny:
            for j, bj in enumerate(b):
                if i + j < ny and bj:
                    r[i + j] = (r[i + j] + ai * bj) % P
    return r


def ypolyval(coeffs_mod, ypt):
    """polynomial (list mod P) at rational point mod P."""
    P = K3.P
    acc = 0
    for c in reversed(coeffs_mod):
        acc = (acc * ypt + c) % P
    return acc


def ysqrt(a, ny):
    """sqrt of y-series with a[0]=1."""
    P = K3.P
    inv2 = pow(2, P - 2, P)
    r = [0] * ny
    r[0] = 1
    for n in range(1, ny):
        acc = sum(r[i] * r[n - i] for i in range(1, n)) % P
        r[n] = (a[n] - acc) * inv2 % P
    return r


def gauss_solve(M, rhs, P):
    """dense Gaussian elimination mod P; M list of rows; returns x or None."""
    n = len(M)
    m = len(M[0])
    A = [row[:] + [rhs[i]] for i, row in enumerate(M)]
    piv = []
    r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if A[i][c] % P), None)
        if p is None:
            return None
        A[r], A[p] = A[p], A[r]
        inv = pow(A[r][c], P - 2, P)
        A[r] = [v * inv % P for v in A[r]]
        for i in range(n):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(v - f * w) % P for v, w in zip(A[i], A[r])]
        piv.append(c)
        r += 1
        if r == m:
            break
    if r < m:
        return None
    for i in range(m, n):
        if A[i][m] % P:
            return None  # inconsistent surplus among used rows
    return [A[i][m] for i in range(m)]


# ---------------- banked anchors (exact, over Q) -------------------------
# diagonal closed forms A_r(t) = (P + Q*sqrt(1-4t)) / (2+t)^(r+1)(1-4t)^(2r+2)
# [king], /(1-4t)^(2r+2) [poly].  Sources: s01/s03 (r=0),
# results/convex-area-moments.md (r=1,2), out_s07_r4_fit.txt (r=3,4).
BANKED = {
    ("king", 0): ([0, 0, 2, -10, 14, -5, -4], [0, 0, 0, -1, -4, -4]),
    ("king", 1): ([0, 0, 4, -52, 230, -348, 120, -84, -54, 80, 32],
                  [0, 0, 0, 8, -29, -34, 100, -40, -32]),
    ("king", 2): ([0, 0, 8, 12, -444, 474, 7140, -23614, 25140, 766,
                   -17936, 5936, 4928, -2304, -1024],
                  [0, 0, 0, -128, 1010, -2093, -470, 3534, 1428, -6548,
                   16, 3344, 960]),
    ("king", 3): ([0, 0, 16, -3424, 46892, -253712, 675710, -847744,
                   159010, 451456, 1428778, -3149064, -770056, 3687200,
                   288480, -1753600, -311296, 270336, 73728],
                  [0, 0, 0, 3200, -38132, 167408, -314133, 76902, 776778,
                   -1166004, -221316, 1126152, 215440, -437536, -218624,
                   -29184]),
    ("king", 4): ([0, 0, 32, 114000, -1960824, 14225684, -57454956,
                   139446362, -162473428, -155341346, 875006676,
                   -1094354194, 42126768, 890704200, -377901728,
                   -40928064, -112532480, -312147968, 192892928,
                   234995712, -10878976, -47185920, -9437184],
                  [0, 0, 0, -114176, 1738760, -11048060, 39099950,
                   -82177717, 69357562, 130365762, -376221972, 136195596,
                   466488368, -347886512, -329206432, 220635952,
                   169206208, -35343424, -41845248, -7296000]),
    ("poly", 0): ([0, 0, 1, -6, 11, -4], [0, 0, 0, 0, -4]),
    ("poly", 1): ([0, 0, 1, -12, 50, -76, 42, -48, 32],
                  [0, 0, 0, 0, 4, -16]),
    ("poly", 2): ([0, 0, 1, -16, 172, -1116, 4062, -8304, 10160, -7872,
                   3840, -1024],
                  [0, 0, 0, 0, -54, 528, -1896, 3216, -2736, 960]),
    ("poly", 3): ([0, 0, 1, -16, -424, 8276, -56890, 210976, -477784,
                   663264, -443424, -132608, 475136, -319488, 73728],
                  [0, 0, 0, 0, 586, -8168, 47224, -152848, 313040,
                   -408448, 306432, -98304]),
    ("poly", 4): ([0, 0, 1, -8, 10664, -207212, 1811654, -9638384,
                   35825928, -98692256, 201999552, -300807168, 321847296,
                   -255799296, 171163648, -105250816, 47185920, -9437184],
                  [0, 0, 0, 0, -10482, 184128, -1442448, 6922656,
                   -23361984, 57844416, -102811008, 124974720, -96575808,
                   41587200, -7296000]),
}


def anchor_consts(mode, r):
    """(cP, cQ) = singular-coefficient pair from the banked diagonal form."""
    Pc, Qc = BANKED[(mode, r)]
    t = Fr(1, 4)
    Pv = sum(c * t ** i for i, c in enumerate(Pc))
    Qv = sum(c * t ** i for i, c in enumerate(Qc))
    if mode == "king":
        d = Fr(9, 4) ** (r + 1)
        return Pv / d, Qv / d
    return Pv, Qv


# ---------------- s02/s03 and s07 bivariate closed forms on the slice ----
M_POLY = {(1, 2): -2, (2, 1): -2, (1, 3): 6, (2, 2): 8, (3, 1): 6,
          (1, 4): -6, (2, 3): -8, (3, 2): -8, (4, 1): -6, (1, 5): 2,
          (3, 3): 6, (5, 1): 2, (2, 5): 2, (3, 4): 2, (4, 3): 2,
          (5, 2): 2, (3, 5): 2, (4, 4): -4, (5, 3): 2}


def slice_closed_form_check(level, tot, ny, x0num, x0den):
    """S0/S1: compare slice series of level 0/1 with banked closed forms."""
    P = K3.P
    xm = x0num * pow(x0den, P - 2, P) % P

    def poly_y(dct):
        """dict (i,j)->c  ->  y-list of sum c x0^i y^j."""
        r = [0] * ny
        for (i, j), c in dct.items():
            if j < ny:
                r[j] = (r[j] + c * pow(xm, i, P)) % P
        return r

    # Delta, K on the slice as y-lists
    Dx = [(1 - xm) * (1 - xm) % P, (-2 * (1 + xm)) % P, 1] + [0] * (ny - 3)
    Kx = [xm, (1 + xm) % P] + [0] * (ny - 2)
    c0 = Dx[0]
    ic0 = pow(c0, P - 2, P)
    sq_norm = ysqrt([v * ic0 % P for v in Dx], ny)
    # sqrt(Delta) with constant term (1-x0) — the global branch +1 at (0,0)
    r0 = (1 - xm) % P
    sqD = [v * r0 % P for v in sq_norm]

    if level == 0:
        # F = -(M + 2x^2y^2(1+x+y)^2 sqrt(D)) / (2 K D^2)
        Mp = poly_y(M_POLY)
        w = [0] * ny
        # 2 x^2 y^2 (1+x+y)^2 on slice: (1+x0)^2 y^2 + 2(1+x0) y^3 + y^4
        base = {2: (1 + xm) * (1 + xm) % P, 3: 2 * (1 + xm) % P, 4: 1}
        for j, c in base.items():
            if j < ny:
                w[j] = 2 * pow(xm, 2, P) * c % P
        num = [(a + b) % P for a, b in
               zip(Mp, ymul(w, sqD, ny))]
        den = ymul(ymul(Kx, Dx, ny), Dx, ny)
        den = [2 * v % P for v in den]
    else:
        fn = "out_s07_bivar_moment.json" if MODE == "king" \
            else "out_s07_bivar_moment_poly.json"
        cf = json.load(open(os.path.join(ROOT, fn)))

        def sym(dct):
            d = {}
            for mono, c in dct.items():
                i, j = map(int, mono.split(","))
                d[(i, j)] = c
                d[(j, i)] = c
            return d

        A = poly_y(sym(cf["A"]))
        B = poly_y(sym(cf["B"]))
        num = [(a + b) % P for a, b in zip(A, ymul(B, sqD, ny))]
        D2 = ymul(Dx, Dx, ny)
        den = ymul(D2, D2, ny)
        if MODE == "king":
            den = ymul(den, ymul(Kx, Kx, ny), ny)
    # closed = num/den as y-series
    # invert den (unit constant term)
    inv = [0] * ny
    i0 = pow(den[0], P - 2, P)
    inv[0] = i0
    for n in range(1, ny):
        acc = sum(den[i] * inv[n - i] for i in range(1, n + 1) if den[i]) % P
        inv[n] = (-acc) * i0 % P
    closed = ymul(num, inv, ny)
    if level == 0:
        closed = [(-v) % P for v in closed]
    S = ser_to_ylist(tot, ny)
    bad = [n for n in range(ny) if S[n] != closed[n]]
    return bad


def fit_PQ(S, r, ny, P, xm, max_extra=0, max_eA=0):
    """Fit S * Kx^(r+1) Dx^(2r+2) (1-y)^e ((1-xm)^2-y)^eA = P + Q*sqrt(Dx)
    over F_P.  Returns (e, eA, d, pC, qC trimmed, surplus) or None.
    With extras=0 (the assembled-total case) scans d upward for the minimal
    fit; with extras allowed (phase values) tries the max usable d per
    (e, eA) in one shot and trims."""
    Dx = [(1 - xm) * (1 - xm) % P, (-2 * (1 + xm)) % P, 1]
    Kx = [xm, (1 + xm) % P]
    base = [1]
    for _ in range(r + 1):
        base = [sum(base[i] * Kx[n - i] for i in
                    range(max(0, n - 1), min(len(base), n + 1))) % P
                for n in range(len(base) + 1)]
    for _ in range(2 * r + 2):
        base = [sum(base[i] * Dx[n - i] for i in
                    range(max(0, n - 2), min(len(base), n + 1))) % P
                for n in range(len(base) + 2)]
    i0 = pow(Dx[0], P - 2, P)
    sq = ysqrt([Dx[0] * i0 % P, Dx[1] * i0 % P, i0] + [0] * (ny - 3), ny)
    r0 = (1 - xm) % P
    sq = [v * r0 % P for v in sq]
    A0 = (1 - xm) * (1 - xm) % P
    dmax = (ny - SURPLUS_MIN - 2) // 2
    for eA in range(max_eA + 1):
        for e in range(max_extra + 1):
            den = base
            for _ in range(e):        # * (1-y)
                den = [((den[n] if n < len(den) else 0)
                        - (den[n - 1] if 1 <= n <= len(den) else 0)) % P
                       for n in range(len(den) + 1)]
            for _ in range(eA):       # * ((1-xm)^2 - y)
                den = [((A0 * den[n] if n < len(den) else 0)
                        - (den[n - 1] if 1 <= n <= len(den) else 0)) % P
                       for n in range(len(den) + 1)]
            denl = den + [0] * max(0, ny - len(den))
            T = ymul(S, denl[:ny], ny)
            dcands = (range(2, dmax + 1) if max_extra == 0 and max_eA == 0
                      else [dmax])
            for d in dcands:
                rows = [[sq[n - m] if 0 <= n - m < ny else 0
                         for m in range(d + 1)]
                        for n in range(d + 1, ny)]
                rhs = [T[n] for n in range(d + 1, ny)]
                sol = gauss_solve(rows, rhs, P)
                if sol is None:
                    continue
                q = sol
                p = [(T[n] - sum(q[m] * sq[n - m] for m in
                                 range(min(d, n) + 1))) % P
                     for n in range(d + 1)]
                while p and p[-1] == 0:
                    p.pop()
                while q and q[-1] == 0:
                    q.pop()
                return (e, eA, d, p, q, ny - 1 - d - (d + 1))
    return None


# ---------------- CRT + rational reconstruction --------------------------
def crt(res, mods):
    M = 1
    x = 0
    for r, p in zip(res, mods):
        _, inv, _ = ext_gcd(M % p, p)
        x = x + M * ((r - x) * inv % p)
        M *= p
    return x % M, M


def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y


def rat_recon(m, M):
    """Wang reconstruction: find p/q == m mod M with |p|,|q| <= sqrt(M/2)."""
    r0, t0 = M, 0
    r1, t1 = m % M, 1
    bound = int((M // 2) ** 0.5)
    while r1 > bound:
        qq = r0 // r1
        r0, r1 = r1, r0 - qq * r1
        t0, t1 = t1, t0 - qq * t1
    if t1 == 0 or abs(t1) > bound:
        return None
    if t1 < 0:
        r1, t1 = -r1, -t1
    assert (r1 - t1 * m) % M == 0
    return Fr(r1, t1)


# ---------------- main -------------------------------------------------
MODE = None


def run_mode(mode, x0num, x0den):
    global MODE
    MODE = mode
    king = mode == "king"
    results = {}
    for P in PRIMES:
        K3.P = P
        K3.NX = 0
        K3.NU = NUARG
        say(f"  prime {P}")
        t0 = time.time()
        ctx, levels = solve_all_levels(king, MAXR, x0num, x0den)
        say(f"  solve_all_levels wall {time.time()-t0:.1f}s")
        xm = x0num * pow(x0den, P - 2, P) % P
        for r, L in enumerate(levels):
            tot = L["tot"]
            ny = tot.vu // 2 + 1
            S = ser_to_ylist(tot, ny)
            # closed-form slice checks (S0 king-only: control M poly unbanked)
            if r == 1 or (r == 0 and king):
                bad = slice_closed_form_check(r, tot, ny, x0num, x0den)
                say(f"    S{r} slice vs banked closed form: "
                    f"{'OK all ' + str(ny) + ' terms' if not bad else 'FAIL at ' + str(bad[:5])}")
                assert not bad, f"S{r} closed-form check failed"
            # fit P_r, Q_r
            fit = fit_PQ(S, r, ny, P, xm)
            assert fit, f"no P/Q fit found for r={r} mode={mode} p={P}"
            extra_e, eA, d, pC, qC, surplus = fit
            assert extra_e == 0 and eA == 0, "unexpected extra factor in tot"
            y4 = pow(4, P - 2, P)
            Kc = 9 * pow(16, P - 2, P) % P
            iK = pow(Kc, (P - 2), P)
            iKr = pow(iK, r + 1, P)
            cP = ypolyval(pC, y4) * iKr % P
            cQ = ypolyval(qC, y4) * iKr % P
            fact2 = 1
            for i in range(1, r + 1):
                fact2 = fact2 * i * i
            tgt = fact2 * pow(pow(2, r + 7, P), P - 2, P) % P
            say(f"    r={r}: degP={len(pC)-1} degQ={len(qC)-1} "
                f"surplus={surplus}  cP==({r}!)^2/2^{r+7}: "
                f"{'MATCH' if cP == tgt else 'MISMATCH cP=' + str(cP) + ' tgt=' + str(tgt)}")
            entry = dict(P=P, cP=cP, cQ=cQ, pC=pC, qC=qC, surplus=surplus,
                         match=(cP == tgt))
            if PHASES:
                ph_fits = {}
                for ph, wt in (("M00", 1), ("M10", 2), ("M11", 1)):
                    V = L[ph].val1()
                    nyp = V.vu // 2 + 1
                    Sp = ser_to_ylist(V, nyp)
                    f = fit_PQ(Sp, r, nyp, P, xm, max_extra=r + 2,
                               max_eA=2 * r + 2)
                    if f is None:
                        say(f"      phase {ph}: NO FIT (needs other atoms)")
                        ph_fits[ph] = None
                        continue
                    e, eA, d, pC2, qC2, sur2 = f
                    y4b = pow(4, P - 2, P)
                    Kcb = 9 * pow(16, P - 2, P) % P
                    # extra factors at y=1/4: (1-y)->3/4, ((1-x)^2-y)->5/16
                    scale = pow(Kcb, r + 1, P) \
                        * pow(3 * pow(4, P - 2, P) % P, e, P) \
                        * pow(5 * pow(16, P - 2, P) % P, eA, P) % P
                    cPp = ypolyval(pC2, y4b) * pow(scale, P - 2, P) % P
                    cQp = ypolyval(qC2, y4b) * pow(scale, P - 2, P) % P
                    say(f"      phase {ph}: extra=(1-y)^{e}(D001)^{eA} "
                        f"degP={len(pC2)-1} degQ={len(qC2)-1} sur={sur2} "
                        f"cP_res={cPp} cQ_res={cQp}")
                    ph_fits[ph] = dict(e=e, eA=eA, degP=len(pC2) - 1,
                                       degQ=len(qC2) - 1, sur=sur2,
                                       cP=cPp, cQ=cQp)
                entry["phases"] = ph_fits
            results.setdefault(r, []).append(entry)
        # anchors r<=4 vs banked diagonal forms
        for r in range(min(4, MAXR) + 1):
            aP, aQ = anchor_consts(mode, r)
            got = results[r][-1]
            aPm = aP.numerator % P * pow(aP.denominator % P, P - 2, P) % P
            aQm = aQ.numerator % P * pow(aQ.denominator % P, P - 2, P) % P
            okP = aPm == got["cP"]
            okQ = aQm == got["cQ"]
            say(f"    S3 r={r} anchor: cP {'OK' if okP else 'FAIL'}, "
                f"cQ {'OK' if okQ else 'FAIL'}")
            assert okP and okQ, f"anchor mismatch r={r} mode={mode}"
    return results


def main():
    say(f"s09 slice-moment run: MAXR={MAXR} NU={NUARG} x0=1/4 "
        f"primes={PRIMES}")
    allres = {}
    for mode in ("king", "poly"):
        say(f"[{mode}]")
        allres[mode] = run_mode(mode, 1, 4)
    # cross-prime consistency + reconstruction of cQ_r
    say("")
    say("reconstructed singular coefficients (CRT over both primes):")
    say(f"{'mode':6s} {'r':>2s}  cP (= (r!)^2/2^(r+7)?)   cQ")
    js = {}
    for mode in ("king", "poly"):
        js[mode] = {}
        for r in sorted(allres[mode]):
            entries = allres[mode][r]
            mods = [e["P"] for e in entries]
            mm, MM = crt([e["cP"] for e in entries], mods)
            cP = rat_recon(mm, MM)
            mm, MM = crt([e["cQ"] for e in entries], mods)
            cQ = rat_recon(mm, MM)
            tgt = Fr(1)
            for i in range(1, r + 1):
                tgt *= Fr(i * i)
            tgt /= Fr(2) ** (r + 7)
            mark = "MATCH" if cP == tgt else "MISMATCH"
            say(f"{mode:6s} {r:2d}  {str(cP):>20s} {mark:9s} {str(cQ)}")
            js[mode][r] = dict(cP=str(cP), cQ=str(cQ),
                               match=(cP == tgt),
                               surplus=[e["surplus"] for e in entries],
                               pC={str(e['P']): e['pC'] for e in entries},
                               qC={str(e['P']): e['qC'] for e in entries})
            if PHASES and all(e.get("phases") for e in entries):
                phj = {}
                for ph in ("M00", "M10", "M11"):
                    fs = [e["phases"][ph] for e in entries]
                    if any(f is None for f in fs):
                        phj[ph] = None
                        continue
                    mm, MM = crt([f["cP"] for f in fs], mods)
                    pcP = rat_recon(mm, MM)
                    mm, MM = crt([f["cQ"] for f in fs], mods)
                    pcQ = rat_recon(mm, MM)
                    say(f"       phase {ph}: extra=(1-y)^{fs[0]['e']}"
                        f"(D001)^{fs[0]['eA']} "
                        f"degP={fs[0]['degP']} degQ={fs[0]['degQ']} "
                        f"cP={pcP} cQ={pcQ}")
                    phj[ph] = dict(e=fs[0]["e"], eA=fs[0]["eA"],
                                   degP=fs[0]["degP"],
                                   degQ=fs[0]["degQ"], cP=str(pcP),
                                   cQ=str(pcQ))
                js[mode][r]["phases"] = phj
    with open(os.path.join(ROOT, "out_s12_slice_PQ_r12.json"), "w") as fp:
        json.dump(js, fp)
    with open(os.path.join(ROOT, "out_s12_slice_r12.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipts written: out_s12_slice_r12.txt, out_s12_slice_PQ_r12.json")


if __name__ == "__main__":
    main()
