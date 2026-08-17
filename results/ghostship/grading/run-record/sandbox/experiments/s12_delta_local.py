#!/usr/bin/env python3
"""Session 12: delta-Laurent LOCAL engine at the singular collision point.

Chassis change vs s09/s11 slice engine (y-adic, u = sqrt(y) series at y=0):
here the base ring is Laurent series in DELTA = sqrt(Delta) at the
singularity itself.  On the slice x = 1/4 the singular curve Delta = 0 is
crossed at y = 1/4, and setting Delta = delta^2 gives CLOSED FORMS

    y(delta)  = 5/4 - sqrt(1+delta^2)      (= 1/4 - delta^2/2 + ...)
    s0(delta) = 2(sqrt(1+delta^2) - delta) (staircase kernel root, -> s*=2)
    s1(delta) = 2(sqrt(1+delta^2) + delta)
    sqrt(Delta) = delta EXACTLY (rational in the ring)

so the whole s08 Temperley moment recursion (operators of s03, inhomogeneity
I^(r) = sum_{k<r} (-1)^(r-1-k) C(r,k) D^(r-k) M^(k), D = s d/ds) can be run
with scalars in the LAURENT field F_p((delta)) -- expansion of the SAME
algebraic functions M_r at the collision point instead of at y=0.  The
kernel evaluations (D00(s0) ~ delta, PK1(s0) = delta, D00(sig+) ~ delta^2)
now genuinely divide by powers of delta: the singular behaviour appears
DIRECTLY as Laurent poles instead of via a fitted P_r/Q_r extraction.

Since S_r(y)*Kx^(r+1)*Dx^(2r+2) = P_r + Q_r*sqrt(Dx)  (s09; Dx = Delta on
the slice, Kx = (1+5y)/4), the total at level r must satisfy

    tot_r(delta) = (P_r(y(delta)) + Q_r(y(delta))*delta)
                   / (Kx(y(delta))^(r+1) * delta^(4r+4)),

with leading Laurent coefficient  [delta^-(4r+4)] tot_r = c_r =
(r!)^2/2^(r+7)  (the s09 law) and vanishing delta^-(4r+3) coefficient
(cQ_r = 0).  Checks:

  V0  Delta(1/4, y(delta)) == delta^2 exactly; PK(s0) == 0; residuals of
      all closed-form seeds.
  V1  [king] level-0 total == the s03 PROVEN closed form
      -(M + 2x^2y^2(1+x+y)^2 delta)/(2K delta^4) at x=1/4, y=y(delta)
      (M from out_s02_KM.txt, hardcoded below) -- absolute anchor.
  V2  every level r: tot_r * Kx^(r+1) * delta^(4r+4) - (P_r + delta*Q_r)
      == 0 in the Laurent ring, with P_r, Q_r the CRT-reconstructed slice
      polynomials of the INDEPENDENT y-adic engine
      (out_s12_slice_PQ_r12.json / out_s09_slice_PQ_run1.json).
  V3  leading Laurent data: [delta^-(4r+4)] tot_r == (r!)^2/2^(r+7) mod p,
      [delta^-(4r+3)] tot_r == 0; full Laurent profile table emitted.
  V4  LOCALIZATION (new): per level r >= 1,
      (a) phase attribution: leading delta-valuation and coefficient of
          M00_r(1), M10_r(1), M11_r(1) separately (s09 finding 3: the M11
          phase carries the full singular coefficient);
      (b) dominant-inhomogeneity truncation: re-solve level r with
          I^(r) replaced by ONLY its k = r-1 term  r * D M^(r-1)
          (all lower ladder terms dropped) -- report the delta-order at
          which tot_r^dom diverges from tot_r; if the leading order
          survives, the c_r-induction only needs the r*D*M^(r-1) term.

Usage: python3 experiments/s12_delta_local.py [MAXR] [NUCAP] [mode]
       mode in {king, poly, both}  (default both)
Output: out_s12_delta_local.txt, out_s12_delta_profiles.json
"""
import sys, os, json, time
from math import comb, factorial
from fractions import Fraction as Fr

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 4
NUCAP_ARG = int(sys.argv[2]) if len(sys.argv) > 2 else 96
MODEARG = sys.argv[3] if len(sys.argv) > 3 else "both"
PRIMES = [(1 << 61) - 1, 10 ** 18 + 9]

P = PRIMES[0]      # rebound per run
NUCAP = NUCAP_ARG
INF = 10 ** 9

OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


# ---------------- Laurent series in delta, mod P, precision-tracked ------
class L:
    """sum_{e < pr} d[e]*delta^e + O(delta^pr); e may be negative."""
    __slots__ = ("d", "pr")

    def __init__(self, d=None, pr=None):
        self.pr = NUCAP if pr is None else min(pr, NUCAP)
        self.d = {}
        if d:
            for e, c in d.items():
                if e < self.pr and c % P:
                    self.d[e] = c % P

    def copy(self):
        return L(dict(self.d), self.pr)

    def vlb(self):
        """lower bound for the valuation."""
        return min(self.d) if self.d else self.pr

    def __add__(a, b):
        pr = min(a.pr, b.pr)
        d = dict(a.d)
        for e, c in b.d.items():
            d[e] = (d.get(e, 0) + c) % P
        return L(d, pr)

    def __sub__(a, b):
        pr = min(a.pr, b.pr)
        d = dict(a.d)
        for e, c in b.d.items():
            d[e] = (d.get(e, 0) - c) % P
        return L(d, pr)

    def __neg__(a):
        return L({e: -c for e, c in a.d.items()}, a.pr)

    def __mul__(a, b):
        pr = min(a.pr + b.vlb(), b.pr + a.vlb(), NUCAP)
        d = {}
        for e1, c1 in a.d.items():
            for e2, c2 in b.d.items():
                e = e1 + e2
                if e < pr:
                    d[e] = (d.get(e, 0) + c1 * c2) % P
        return L(d, pr)

    def scal(a, k):
        k %= P
        return L({e: c * k % P for e, c in a.d.items()}, a.pr)

    def is_zero(a):
        return not a.d

    def get(a, e):
        return a.d.get(e, 0)

    def inv(a):
        v = a.vlb()
        assert a.d, "inv of zero-to-precision series"
        assert a.d.get(v, 0) % P, "leading coeff vanished?"
        rel = a.pr - v            # relative precision of the unit part
        u = [0] * rel
        for e, c in a.d.items():
            u[e - v] = c % P
        iu0 = pow(u[0], P - 2, P)
        r = [0] * rel
        r[0] = iu0
        for n in range(1, rel):
            acc = 0
            for i in range(1, n + 1):
                if u[i] and r[n - i]:
                    acc += u[i] * r[n - i]
            r[n] = (-acc * iu0) % P
        return L({i - v: c for i, c in enumerate(r) if c},
                 rel - 2 * v if rel - 2 * v < NUCAP else NUCAP)


def C(k):
    if isinstance(k, Fr):
        return L({0: k.numerator * pow(k.denominator, P - 2, P) % P})
    return L({0: k % P})


def divL(A, B):
    return A * B.inv()


def sqrt_init(a, r0):
    """sqrt of L with known constant-term sqrt r0 (Newton)."""
    inv2 = pow(2, P - 2, P)
    r = C(r0)
    for _ in range(16):
        r = (r + a * r.inv()).scal(inv2)
    assert (r * r - a).is_zero(), "sqrt failed"
    return r


# ---------------- polynomials in s over L --------------------------------
class SPoly:
    __slots__ = ("cs",)

    def __init__(self, cs):
        self.cs = list(cs)
        while len(self.cs) > 1 and self.cs[-1].is_zero():
            self.cs.pop()

    def __add__(a, b):
        n = max(len(a.cs), len(b.cs))
        Z = L()
        return SPoly([(a.cs[i] if i < len(a.cs) else Z) +
                      (b.cs[i] if i < len(b.cs) else Z) for i in range(n)])

    def __sub__(a, b):
        n = max(len(a.cs), len(b.cs))
        Z = L()
        return SPoly([(a.cs[i] if i < len(a.cs) else Z) -
                      (b.cs[i] if i < len(b.cs) else Z) for i in range(n)])

    def __mul__(a, b):
        n = len(a.cs) + len(b.cs) - 1
        out = [L() for _ in range(n)]
        for i, ca in enumerate(a.cs):
            if ca.is_zero():
                continue
            for j, cb in enumerate(b.cs):
                out[i + j] = out[i + j] + ca * cb
        return SPoly(out)

    def scale(a, k):     # k = L
        return SPoly([c * k for c in a.cs])

    def eval(a, pt):     # pt = L, Horner
        r = a.cs[-1].copy()
        for c in reversed(a.cs[:-1]):
            r = r * pt + c
        return r

    def val1(a):
        r = L()
        for c in a.cs:
            r = r + c
        return r

    def deriv(a):
        return SPoly([a.cs[i].scal(i) for i in range(1, len(a.cs))]) \
            if len(a.cs) > 1 else SPoly([L()])

    def syndiv1(a):
        cs = a.cs
        q = [None] * (len(cs) - 1)
        acc = cs[-1].copy()
        for i in range(len(cs) - 2, -1, -1):
            q[i] = acc
            acc = acc + cs[i]
        assert acc.is_zero(), "syndiv1: nonzero remainder"
        return SPoly(q) if q else SPoly([L()])


def SP(*cs):
    return SPoly([c if isinstance(c, L) else C(c) for c in cs])


def sdiv_root(N, r):
    cs = N.cs
    n = len(cs) - 1
    if n == 0:
        return SPoly([L()]), cs[0]
    q = [None] * n
    acc = cs[n]
    for i in range(n - 1, -1, -1):
        q[i] = acc
        acc = cs[i] + acc * r
    return SPoly(q), acc


def polydiv(N, Dp):
    dd = len(Dp.cs) - 1
    Li = Dp.cs[-1].inv()
    rem = [c.copy() for c in N.cs]
    nq = len(rem) - 1 - dd
    if nq < 0:
        return None, all(c.is_zero() for c in N.cs)
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


# ---------------- FRat: factored-atom denominators (s09/s11 chassis) -----
class Ctx:
    pass


class FRat:
    __slots__ = ("num", "e", "ctx")

    def __init__(self, num, e, ctx):
        self.num, self.e, self.ctx = num, tuple(e), ctx

    def denpoly(self):
        return self.ctx.denpoly(self.e)

    def lift(self, E):
        n = self.num
        for i, (Ei, ei) in enumerate(zip(E, self.e)):
            assert Ei >= ei
            if Ei > ei:
                n = n * self.ctx.atom_pow(i, Ei - ei)
        return n

    def scal(self, k):
        if isinstance(k, int):
            return FRat(SPoly([c.scal(k) for c in self.num.cs]), self.e,
                        self.ctx)
        return FRat(self.num.scale(k), self.e, self.ctx)

    def D(self):
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
        ctx = self.ctx
        nv = self.num.eval(ctx.pts[key])
        dv = ctx.den_eval(key, self.e)
        return nv * dv.inv()

    def val1(self):
        return self.num.val1() * self.ctx.den_val1(self.e).inv()

    def deriv1(self):
        ctx = self.ctx
        n1 = self.num.val1()
        np1 = self.num.deriv().val1()
        d1 = ctx.den_val1(self.e)
        dp1 = L()
        for i, ei in enumerate(self.e):
            if ei:
                t = ctx.datom_val1[i].scal(ei)
                for j, ej in enumerate(self.e):
                    p = ej - (1 if j == i else 0)
                    if p:
                        t = t * ctx.atom_val1_pow(j, p)
                dp1 = dp1 + t
        return (np1 * d1 - n1 * dp1) * (d1 * d1).inv()


def frat_add(*As):
    ctx = As[0].ctx
    E = tuple(max(a.e[i] for a in As) for i in range(len(As[0].e)))
    num = As[0].lift(E)
    for a in As[1:]:
        num = num + a.lift(E)
    return FRat(num, E, ctx)


# ---------------- context at the collision (x = 1/4) ---------------------
def build_ctx(king):
    ctx = Ctx()
    x = C(Fr(1, 4))
    delta = L({1: 1})
    R = sqrt_init(C(1) + delta * delta, 1)          # sqrt(1+delta^2)
    y = C(Fr(5, 4)) - R                             # y(delta)
    # V0a: Delta(1/4,y) = (y-1/4)(y-9/4) == delta^2
    Dx = (y - C(Fr(1, 4))) * (y - C(Fr(9, 4)))
    assert (Dx - delta * delta).is_zero(), "Delta != delta^2"
    u = sqrt_init(y, Fr(1, 2))                      # sqrt(y), u(0)=1/2
    ctx.x, ctx.delta, ctx.y, ctx.u = x, delta, y, u
    one = C(1)
    one_m_xs = SPoly([one, -x])                     # 1 - xs
    W = SP(-1, 1) * one_m_xs                        # (s-1)(1-xs)
    PK = W - SP(0, 1).scale(y)                      # staircase kernel
    two = C(2)
    s0 = (R - delta).scal(2)                        # kernel root -> s*=2
    s1 = (R + delta).scal(2)
    assert PK.eval(s0).is_zero(), "PK(s0) != 0"
    assert PK.eval(s1).is_zero(), "PK(s1) != 0"
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
               "sigp": (one - u).inv(),
               "sigm": (one + u).inv()}
    ctx._apow, ctx._dp, ctx._aev, ctx._av1 = {}, {}, {}, {}

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


# ---------------- operators (verbatim transplant of s09/s11 FRat ops) ----
def B_op(G, G1, ctx):
    num = (G.num - SP(0, 1).scale(G1) * G.denpoly()).syndiv1()
    if ctx.king:
        num = num + SP(0, 1).scale(ctx.x * G1) * G.denpoly()
    e = list(G.e)
    e[0] += 1
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


TRACE = bool(os.environ.get("S12_TRACE"))


def solve_level(M00, I10, I11, ctx, tag=""):
    inv2 = pow(2, P - 2, P)
    y = ctx.y
    M001 = M00.val1()
    M00p1 = M00.deriv1()
    BM = B_op(M00, M001, ctx)

    T = BM.eval("s0") * y + I10.eval("s0")
    s0 = ctx.pts["s0"]
    M101 = -(T * s0 * ctx.Qcomp.eval(s0).inv())
    E = tuple(max(a, b) for a, b in zip(BM.e, I10.e))
    num_raw = ((BM.lift(E).scale(y) + I10.lift(E)) * ctx.W
               + ctx.Qcomp.scale(y * M101) * ctx.denpoly(E))
    Q1, rem = sdiv_root(num_raw, s0)
    assert rem.is_zero(), "staircase numerator not killed at s0"
    e10 = list(E)
    e10[2] += 1
    M10 = FRat(Q1, e10, ctx).reduce()
    assert (M10.val1() - M101).is_zero(), "M10(1) consistency"
    M10p1 = M10.deriv1()

    D1M = D1op(M00, M001, M00p1, ctx)
    D2M = D2op(M10, M101, M10p1, ctx)
    A2M = frat_add(D1M.scal(y), D2M.scal(y.scal(2)), I11)
    vp, vm = A2M.eval("sigp"), A2M.eval("sigm")
    M111 = (vp + vm).scal(inv2)
    if TRACE:
        for nm, FR in (("yD1[M00]", D1M.scal(y)), ("2yD2[M10]",
                       D2M.scal(y.scal(2))), ("I11", I11)):
            wp, wm = FR.eval("sigp"), FR.eval("sigm")
            av = (wp + wm).scal(inv2)
            say(f"      TRACE{tag} {nm}: sig+ {lead_data(wp,3)}  "
                f"avg {lead_data(av,3)}")
        say(f"      TRACE{tag} M10(1): {lead_data(M101,3)}  "
            f"M11(1): {lead_data(M111,3)}")
    M11p1 = (vp - vm) * (ctx.u.scal(2)).inv()
    K11 = SPoly([C(1), C(-2), C(1) - y])
    numM11 = (A2M.num * SP(1, -2, 1)
              - (SP(0, 0, 1).scale(M111)
                 + SP(0, -1, 1).scale(M11p1)).scale(y) * A2M.denpoly())
    Q11 = polydiv_exact(numM11, K11, "closing")
    M11 = FRat(Q11, A2M.e, ctx).reduce()
    assert (M11.val1() - M111).is_zero(), "M11(1) consistency"
    assert (M11.deriv1() - M11p1).is_zero(), "M11'(1) consistency"

    tot = M001 + M101.scal(2) + M111
    return dict(M00=M00, M10=M10, M11=M11, tot=tot,
                M001=M001, M101=M101, M111=M111)


def lead_data(a, nterms=6):
    """(valuation-lower-bound, list of leading coefficients)."""
    if not a.d:
        return None, []
    v = a.vlb()
    return v, [a.get(v + i) for i in range(min(nterms, a.pr - v))]


def solve_all(king, maxr):
    ctx = build_ctx(king)
    x, y = ctx.x, ctx.y
    N00 = SP(0, x * y, -(x * x * y))
    F00 = FRat(N00, (0, 1, 0), ctx)
    zero = FRat(SP(0), (0, 0, 0), ctx)
    L0 = solve_level(F00, zero, zero, ctx)
    levels = [L0]
    doms = [None]
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
        Lr = solve_level(M00r, I["M10"].reduce(), I["M11"].reduce(), ctx,
                         tag=f" r{r}")
        levels.append(Lr)
        for ph in ("M00", "M10", "M11"):
            lad[ph][r] = [Lr[ph]]
        # V4b: dominant-inhomogeneity side solve (does NOT feed the ladder)
        Idom = {ph: lad[ph][r - 1][1].scal(r) for ph in ("M00", "M10", "M11")}
        M00d = FRat(Idom["M00"].num * ctx.atom_pow(0, 2),
                    (Idom["M00"].e[0], Idom["M00"].e[1] + 1,
                     Idom["M00"].e[2]), ctx).reduce()
        Ld = solve_level(M00d, Idom["M10"].reduce(), Idom["M11"].reduce(),
                         ctx, tag=f" r{r}dom")
        doms.append(Ld)
        say(f"    level {r}: {time.time()-t0:.1f}s  tot.pr={Lr['tot'].pr}  "
            f"tot.val={Lr['tot'].vlb()}")
    return ctx, levels, doms


# ---------------- checks -------------------------------------------------
# M(x,y) of the s03 PROVEN level-0 closed form, transcribed from
# out_s02_KM.txt (receipt: "M = A1/Delta^2 = ..."):
M_MONOS = [(-2, 1, 2), (-2, 2, 1), (6, 1, 3), (8, 2, 2), (6, 3, 1),
           (-6, 1, 4), (-8, 2, 3), (-8, 3, 2), (-6, 4, 1), (2, 1, 5),
           (6, 3, 3), (2, 5, 1), (2, 2, 5), (2, 3, 4), (2, 4, 3),
           (2, 5, 2), (2, 3, 5), (-4, 4, 4), (2, 5, 3)]


def check_V1_king(ctx, tot0):
    x, y, delta = ctx.x, ctx.y, ctx.delta
    xp = {0: C(1)}
    yp = {0: C(1)}
    for i in range(1, 6):
        xp[i] = xp[i - 1] * x
        yp[i] = yp[i - 1] * y
    M = L()
    for c, i, j in M_MONOS:
        M = M + (xp[i] * yp[j]).scal(c)
    K = x + y + x * y
    w = C(1) + x + y
    num = M + (xp[2] * yp[2] * w * w * delta).scal(2)
    den = (K * delta * delta * delta * delta).scal(2)
    Fcf = -(num * den.inv())
    diff = Fcf - tot0
    return diff.is_zero(), lead_data(diff)


def load_PQ():
    for fn in ("out_s12_slice_PQ_r12.json", "out_s09_slice_PQ_run1.json"):
        p = os.path.join(ROOT, fn)
        if os.path.exists(p):
            return fn, json.load(open(p))
    return None, None


def check_V2(ctx, levels, pq, mode):
    """tot_r * Kx^(r+1) * delta^(4r+4) == P_r(y) + delta*Q_r(y),
    P_r, Q_r taken as mod-p coefficient lists (keys pC/qC) at this prime."""
    y, delta = ctx.y, ctx.delta
    Kx = C(Fr(1, 4)) * (C(1) + y.scal(5))          # (1+5y)/4
    res = []
    for r, Lr in enumerate(levels):
        rec = pq.get(str(r))
        if rec is None or str(P) not in rec.get("pC", {}):
            res.append((r, "no-PQ"))
            continue
        Pv, Qv = L(), L()
        yp = C(1)
        n = max(len(rec["pC"][str(P)]), len(rec["qC"][str(P)]))
        pc, qc = rec["pC"][str(P)], rec["qC"][str(P)]
        for i in range(n):
            if i < len(pc) and pc[i]:
                Pv = Pv + yp.scal(pc[i])
            if i < len(qc) and qc[i]:
                Qv = Qv + yp.scal(qc[i])
            yp = yp * y
        lhs = Lr["tot"]
        for _ in range(r + 1):
            lhs = lhs * Kx
        sh = 4 * r + 4                    # multiply by delta^(4r+4): shift
        lhs = L({e + sh: c for e, c in lhs.d.items()}, lhs.pr + sh)
        d = lhs - (Pv + delta * Qv)
        if d.is_zero():
            res.append((r, "OK"))
        else:
            dm = lhs - (Pv - delta * Qv)
            res.append((r, "OK(-delta)" if dm.is_zero()
                        else f"FAIL(val{d.vlb()})"))
    return res


def run_mode(mode, maxr):
    king = (mode == "king")
    say(f"[{mode}] building levels 0..{maxr}, NUCAP={NUCAP}, p={P}")
    t0 = time.time()
    ctx, levels, doms = solve_all(king, maxr)
    say(f"[{mode}] solve wall {time.time()-t0:.0f}s")

    # V1 (king only)
    if king:
        ok, ld = check_V1_king(ctx, levels[0]["tot"])
        say(f"[{mode}] V1 level-0 == s03 closed form at collision: "
            f"{'OK' if ok else f'FAIL {ld}'}")

    # V2
    fn, pq = load_PQ()
    if pq is not None:
        key = "king" if king else "poly"
        sub = pq.get(key) if isinstance(pq, dict) else None
        if sub:
            res = check_V2(ctx, levels, sub, mode)
            say(f"[{mode}] V2 vs {fn}: " +
                " ".join(f"r{r}:{v}" for r, v in res))
        else:
            say(f"[{mode}] V2 skipped: no '{key}' key in {fn} "
                f"(keys {list(pq)[:6]})")
    else:
        say(f"[{mode}] V2 skipped: no PQ receipt found")

    # V3 + V4a + V4b tables
    prof = {}
    say(f"[{mode}] V3/V4 Laurent profiles (val: coeffs, mod p):")
    for r, Lr in enumerate(levels):
        tot = Lr["tot"]
        v, cs = lead_data(tot, 8)
        cr = factorial(r) ** 2 * pow(2, (r + 7) * (P - 2), P) % P
        v_ok = (v == -(4 * r + 4))
        c_ok = (cs and cs[0] == cr)
        q_ok = (len(cs) > 1 and cs[1] == 0) if r >= 1 else True
        say(f"  r={r}: tot val={v} (want {-(4*r+4)}: "
            f"{'OK' if v_ok else 'FAIL'}) "
            f"lead={'OK' if c_ok else 'FAIL'}(c_r=(r!)^2/2^(r+7)) "
            f"next={'OK(=0)' if q_ok else 'NONZERO'}")
        ph = {}
        for name, val in (("M00(1)", Lr["M001"]), ("M10(1)", Lr["M101"]),
                          ("M11(1)", Lr["M111"])):
            pv, pcs = lead_data(val, 4)
            ph[name] = (pv, pcs)
            say(f"        {name}: val={pv} lead={pcs[:2] if pcs else []}")
        if doms[r] is not None:
            d = doms[r]["tot"] - tot
            dv, dcs = lead_data(d, 4)
            keep = (dv is None) or (dv > tot.vlb())
            gap = None if dv is None else dv - tot.vlb()
            say(f"        V4b dom-only tot differs from delta-order "
                f"{dv} (gap {gap}): leading order "
                f"{'PRESERVED' if keep else 'CHANGED'}")
            prof[f"r{r}_domgap"] = gap
        prof[f"r{r}"] = dict(val=v, coeffs=[int(c) for c in cs],
                             phases={k: (pv, [int(c) for c in pcs])
                                     for k, (pv, pcs) in ph.items()})
    return prof


def main():
    global P, NUCAP
    say(f"s12 delta-Laurent local engine: MAXR={MAXR} NUCAP={NUCAP_ARG} "
        f"modes={MODEARG} primes={PRIMES}")
    modes = ["king", "poly"] if MODEARG == "both" else [MODEARG]
    allprof = {}
    for p in PRIMES:
        P = p
        NUCAP = NUCAP_ARG
        say(f"== prime {p} ==")
        for mode in modes:
            allprof[f"{mode}_p{p}"] = run_mode(mode, MAXR)
    suf = os.environ.get("S12_OUT_SUFFIX", "")
    with open(os.path.join(ROOT, f"out_s12_delta_profiles{suf}.json"),
              "w") as fp:
        json.dump(allprof, fp, indent=1)
    with open(os.path.join(ROOT, f"out_s12_delta_local{suf}.txt"),
              "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say(f"receipts: out_s12_delta_local{suf}.txt, "
        f"out_s12_delta_profiles{suf}.json")


if __name__ == "__main__":
    main()
