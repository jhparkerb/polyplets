#!/usr/bin/env python3
"""Session 08: KERNEL-METHOD DERIVATION of the area-moment generating
functions of convex king animals (and the polyomino control) — the
"Temperley moment method" sketched in docs/proofs/area-moments-method.md,
executed here for moment levels r = 1, 2.

Derivation (machine-executed below; see docs/proofs/area-moment-kernel.md):
Let Theta = q d/dq. Apply Theta^r to the PROVEN q-functional-equation
system (docs/proofs/convex-area-q-temperley.md §1) and set q = 1. Writing
M_ph^{(r)}(s) = Theta^r F_ph(s;q)|_{q=1} and D = s d/ds, every equation
becomes the SAME q=1 operator equation applied to the level-r unknowns
plus an explicitly known inhomogeneity:

    level 1:  I_ph = D F_ph(s)
    level 2:  I_ph = 2 D M_ph^{(1)}(s) - D^2 F_ph(s)

(proof of the rule: expand q = e^eps; c(q s) X(q) with slot X in
{G(qs;q), G(1;q), G'(1;q)} has eps^2-coefficient*2 equal to
c*X^{(2)} + 2 D[c X^{(1)}] + D^2[c X^{(0)}]; summing over the terms of an
equation F_ph = Op[..] and using the level-(r-1) equations telescopes the
D-terms into the stated inhomogeneity.)

Hence the level-r system is solved by the SAME kernel method as level 0
(s03): phase (0,0) is non-catalytic; the staircase kernel
P_K(s) = (s-1)(1-xs) - ys is killed at its power-series root s0; the
closing kernel (s-1)^2 - ys^2 at sigma_pm = 1/(1 -+ u), giving
M^{(r)}(1) etc. by linear algebra. All ingredients stay in Q(x,y,sqrt(D)):
THE MOMENT GFs ARE ALGEBRAIC, constructively, at every level r.

This script executes levels 0,1,2 in exact truncated series arithmetic mod
two ~2^60 primes and checks:
  C0  level-0 grid == validated DP table f(w,h) (re-derivation of s03)
  C1  [x^w u^2h] M^{(r)} == sum_n n^r f(w,h;n) from the doubly-validated
      joint truth table out_s04_area_truth.json, r=1,2, both modes
  C2  diagonal sum_w [x^w u^2(s-w)] M^{(r)} == a_r(s) from the independent
      moment DP out_s07_area_moments_r4_30.json, r<=4
  C3  M^{(1)} satisfies s07's fitted closed form:
      A + B*sqrt(Delta) - M1 * K^2 * Delta^4 == 0   [king]
      A' + B'*sqrt(Delta) - M1 * Delta^4 == 0        [poly]
      (checked by multiplication: no division by K needed)

Usage: python3 experiments/s08_moment_kernel.py [NX] [H] [maxlevel] [big]
Output: out_s08_moment_kernel.txt
"""
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s03_kernel_solve as K3
from s03_kernel_solve import SPoly, SRat

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

NX = int(sys.argv[1]) if len(sys.argv) > 1 else 10
H = int(sys.argv[2]) if len(sys.argv) > 2 else 10
MAXLEV = int(sys.argv[3]) if len(sys.argv) > 3 else 2
NU = 2 * H + 4

PRIMES = [(1 << 61) - 1, 10 ** 18 + 9]
if len(sys.argv) > 4 and sys.argv[4] == "big":
    # Mersenne prime 2^521-1: any checked coefficient difference would need
    # to be divisible by ~10^157 -- comparisons vs true integers are exact.
    PRIMES = [(1 << 521) - 1]

OUT = []


def say(msg):
    print(msg, flush=True)
    OUT.append(msg)


# ---------- helpers over the K3 classes ----------
def C(k):
    return K3.C(k)


def SP(*cs):
    return SPoly([c if isinstance(c, K3.Ser) else C(c) for c in cs])


def srat_add(*As):
    num, den = As[0].num, As[0].den
    for A in As[1:]:
        num = num * A.den + A.num * den
        den = den * A.den
    return SRat(num, den)


def srat_scale(A, k):  # k = Ser
    return SRat(A.num.scale(k), A.den)


def srat_int(A, k):  # k = int
    return SRat(SPoly([c.scal(k) for c in A.num.cs]), A.den)


def srat_D(A):
    """s d/ds A, as SRat with den = A.den^2."""
    num = SP(0, 1) * (A.num.deriv() * A.den - A.num * A.den.deriv())
    return SRat(num, A.den * A.den)


def srat_Dj(A, j):
    """(s d/ds)^j A; denominator kept as A.den^(j+1), not squared each step."""
    num, den = A.num, A.den
    dden = den.deriv()
    e = 1
    for _ in range(j):
        num = SP(0, 1) * (num.deriv() * den
                          - SPoly([c.scal(e) for c in num.cs]) * dden)
        e += 1
    dpow = SP(1)
    for _ in range(e):
        dpow = dpow * den
    return SRat(num, dpow)


def sdiv_root(N, r):
    """Divide SPoly N by (s - r), r a Ser root. Return (quotient, remainder)."""
    cs = N.cs
    n = len(cs) - 1
    if n == 0:
        return SPoly([K3.Ser()]), cs[0]
    q = [None] * n
    acc = cs[n]
    for i in range(n - 1, -1, -1):
        q[i] = acc
        acc = cs[i] + acc * r
    return SPoly(q), acc


def polydiv_exact(N, Dp, tag):
    """Divide SPoly N by SPoly Dp (unit leading coeff); assert remainder 0."""
    dd = len(Dp.cs) - 1
    Li = Dp.cs[-1].inv_unit()
    rem = [c.copy() for c in N.cs]
    nq = len(rem) - 1 - dd
    assert nq >= 0, f"polydiv {tag}: deg N < deg D"
    q = [None] * (nq + 1)
    for k in range(nq, -1, -1):
        c = rem[k + dd] * Li
        q[k] = c
        for j in range(dd + 1):
            rem[k + j] = rem[k + j] - c * Dp.cs[j]
    for j in range(dd):
        assert rem[j].is_zero(), f"polydiv {tag}: nonzero remainder at s^{j}"
    return SPoly(q)


def sqrt_ser(A):
    """sqrt of Ser with constant term 1 (Newton, mod P)."""
    inv2 = pow(2, K3.P - 2, K3.P)
    r = C(1)
    for _ in range(14):
        r = (r + A * r.inv_unit()).scal(inv2)
    assert (r * r - A).is_zero(), "sqrt_ser failed"
    return r


# ---------- generic one-level solver ----------
def B_op(G, G1, king, one_m_xs, x):
    """B[G](s) = (G(s)-sG(1))/((s-1)(1-xs)) [+ king xsG(1)/(1-xs)] as SRat."""
    num = (G.num - SP(0, 1).scale(G1) * G.den).syndiv1()
    if king:
        num = num + SP(0, 1).scale(x * G1) * G.den
    return SRat(num, G.den * one_m_xs)


def solve_level(M00, I10, I11, king, ctx):
    """Solve the level-r catalytic system given the already-solved phase-00
    moment M00 (SRat) and inhomogeneities I10, I11 (SRat). Returns dict."""
    x, u, y, one = ctx["x"], ctx["u"], ctx["y"], ctx["one"]
    s0, sigp, sigm = ctx["s0"], ctx["sigp"], ctx["sigm"]
    one_m_xs, W, PK, PK1, Qcomp = (ctx["one_m_xs"], ctx["W"], ctx["PK"],
                                   ctx["PK1"], ctx["Qcomp"])
    inv2 = pow(2, K3.P - 2, K3.P)

    M001 = M00.val1()
    M00p1 = M00.deriv1()
    BM = B_op(M00, M001, king, one_m_xs, x)

    # staircase phase: M10 PK = y BM W + I10 W + y M10(1) Qcomp
    T = y * BM.eval(s0) + I10.eval(s0)
    M101 = -(T * s0 * Qcomp.eval(s0).inv_unit())
    DenC = BM.den * I10.den
    num_raw = ((BM.num * I10.den * W).scale(y)
               + I10.num * BM.den * W
               + (Qcomp * DenC).scale(y * M101))
    Q1, rem = sdiv_root(num_raw, s0)
    assert rem.is_zero(), "staircase numerator not killed at s0"
    M10 = SRat(Q1, PK1 * DenC)
    assert (M10.val1() - M101).is_zero(), "M10(1) consistency"
    M10p1 = M10.deriv1()

    # closing phase
    D1M = K3.D1op(M00, M001, M00p1)
    D2M = K3.D2op(M10, M101, M10p1)
    A2M = srat_add(srat_scale(D1M, y), srat_scale(D2M, y.scal(2)), I11)
    vp, vm = A2M.eval(sigp), A2M.eval(sigm)
    M111 = (vp + vm).scal(inv2)
    odd = [m for m, c in M111.d.items()
           if m[1] % 2 == 1 and c % K3.P and m[0] <= M111.vx
           and m[1] <= M111.vu]
    assert not odd, f"odd-u part of M11(1): {odd[:4]}"
    M11p1 = K3.divexact(vp - vm, u.scal(2))
    # M11 as SRat: M11 K11 = A2M (s-1)^2 - y[s^2 M111 + s(s-1) M11p1] A2M.den
    K11 = SPoly([one, C(-2), one - y])
    numM11 = (A2M.num * SP(1, -2, 1)
              - (SP(0, 0, 1).scale(M111)
                 + SP(0, -1, 1).scale(M11p1)).scale(y) * A2M.den)
    Q11 = polydiv_exact(numM11, K11, "closing")
    M11 = SRat(Q11, A2M.den)
    assert (M11.val1() - M111).is_zero(), "M11(1) consistency"
    assert (M11.deriv1() - M11p1).is_zero(), "M11'(1) consistency"

    tot = M001 + M101.scal(2) + M111
    return dict(M00=M00, M001=M001, M00p1=M00p1, M10=M10, M101=M101,
                M10p1=M10p1, M11=M11, M111=M111, M11p1=M11p1, tot=tot)


def build_ctx(king):
    x = K3.Ser({(1, 0): 1})
    u = K3.Ser({(0, 1): 1})
    y = u * u
    one = C(1)
    one_m_xs = SPoly([one, -x])
    W = SP(-1, 1) * one_m_xs
    PK = W - SP(0, 1).scale(y)
    # kernel root s0 = 1 + y s0/(1-x s0)
    s0 = C(1)
    for _ in range(NU // 2 + 2):
        s0 = one + y * s0 * (one - x * s0).inv_unit()
    assert ((s0 - one) * (one - x * s0) - y * s0).is_zero(), "s0 residual"
    PK1, remPK = sdiv_root(PK, s0)
    assert remPK.is_zero(), "PK not divisible by (s-s0)"
    if king:
        Qcomp = SP(0, -1, 1).scale(x) - SP(0, 1)
    else:
        Qcomp = SP(0, -1)
    sigp = (one - u).inv_unit()
    sigm = (one + u).inv_unit()
    return dict(x=x, u=u, y=y, one=one, one_m_xs=one_m_xs, W=W, PK=PK,
                PK1=PK1, Qcomp=Qcomp, s0=s0, sigp=sigp, sigm=sigm)


def solve_all_levels(king):
    ctx = build_ctx(king)
    x, y, one, one_m_xs = ctx["x"], ctx["y"], ctx["one"], ctx["one_m_xs"]
    # level 0: F00 = xys(1-xs)/((1-xs)^2 - y)
    N00 = SP(0, x * y, -(x * x * y))
    D00 = SPoly([one - y, -(x + x), x * x])
    F00 = SRat(N00, D00)
    zero = SRat(SP(0), SP(1))
    L0 = solve_level(F00, zero, zero, king, ctx)
    levels = [L0]
    from math import comb
    for r in range(1, MAXLEV + 1):
        # I^{(r)}_ph = sum_{k=0}^{r-1} (-1)^{r-1-k} C(r,k) D^{r-k} M^{(k)}_ph
        I = {}
        for ph in ("M00", "M10", "M11"):
            terms = [srat_int(srat_Dj(levels[k][ph], r - k),
                              (-1) ** (r - 1 - k) * comb(r, k))
                     for k in range(r)]
            I[ph] = srat_add(*terms)
        # phase (0,0) is non-catalytic: M00^{(r)} = I00 (1-xs)^2 / D00
        M00r = SRat(I["M00"].num * one_m_xs * one_m_xs, I["M00"].den * D00)
        levels.append(solve_level(M00r, I["M10"], I["M11"], king, ctx))
    return ctx, levels


# ---------- checks ----------
def check_grid_truth(levels, mode, truth):
    """C1: moment grids vs joint truth table (boxes w,h<=10)."""
    P = K3.P
    ok = bad = 0
    for key, dist in truth[mode].items():
        w, h = map(int, key.split(","))
        for r in range(1, len(levels)):
            Mr = levels[r]["tot"]
            if w > Mr.vx or 2 * h > Mr.vu:
                continue
            want = sum(int(n) ** r * c for n, c in dist.items()) % P
            got = Mr.get(w, 2 * h) % P
            if got == want:
                ok += 1
            else:
                bad += 1
                if bad <= 5:
                    say(f"    C1 MISMATCH {mode} r={r} w={w} h={h}: "
                        f"got {got} want {want}")
    return ok, bad


def check_diag(levels, mode, d52):
    """C2: diagonal vs independent univariate moment DP (SMAX=52 run)."""
    P = K3.P
    start = d52["start"]
    ok = bad = 0
    for r in range(1, len(levels)):
        Mr = levels[r]["tot"]
        seq = d52[mode][f"a{r}"]
        for s in range(2, min(NX, H) + 2):
            want = seq[s - start] % P
            got = sum(Mr.get(w, 2 * (s - w)) for w in range(1, s)) % P
            if got == want:
                ok += 1
            else:
                bad += 1
                if bad <= 5:
                    say(f"    C2 MISMATCH {mode} r={r} s={s}: "
                        f"got {got} want {want}")
    return ok, bad


def check_closed_form(levels, mode, ctx):
    """C3: A + B sqrt(Delta) - M1 * K^2 Delta^4 == 0 (king; poly: no K)."""
    P = K3.P
    fn = ("out_s07_bivar_moment.json" if mode == "king"
          else "out_s07_bivar_moment_poly.json")
    cf = json.load(open(os.path.join(ROOT, fn)))
    x, u, y = ctx["x"], ctx["u"], ctx["y"]
    one = ctx["one"]

    def poly_of(dct):
        # JSON stores only the i<=j representative of each symmetric pair
        d = {}
        for mono, c in dct.items():
            i, j = map(int, mono.split(","))
            d[(i, 2 * j)] = c % P
            d[(j, 2 * i)] = c % P
        return K3.Ser(d)

    A, B = poly_of(cf["A"]), poly_of(cf["B"])
    Delta = (one - x - y) * (one - x - y) - (x * y).scal(4)
    sq = sqrt_ser(Delta)
    D2 = Delta * Delta
    D4 = D2 * D2
    M1 = levels[1]["tot"]
    lhs = A + B * sq
    rhs = M1 * D4
    if mode == "king":
        K = x + y + x * y
        rhs = rhs * K * K
    return (lhs - rhs).is_zero()


def main():
    say(f"s08 moment-kernel run: NX={NX} H={H} NU={NU} maxlevel={MAXLEV}")
    truth = json.load(open(os.path.join(ROOT, "out_s04_area_truth.json")))
    d52 = json.load(open(os.path.join(ROOT, "out_s07_area_moments_r4_30.json")))
    from convex_box import g_table, f_from_g
    import time
    allok = True
    for P in PRIMES:
        K3.P = P
        K3.NX, K3.NU = NX, NU
        say(f"prime p = {P}")
        for king, mode in ((True, "king"), (False, "poly")):
            t0 = time.time()
            ctx, levels = solve_all_levels(king)
            # C0: level-0 grid vs DP table
            g = g_table(NX, H, king=king)
            f = f_from_g(g, NX, H)
            F = levels[0]["tot"]
            bad0 = sum(1 for w in range(1, NX + 1) for h in range(1, H + 1)
                       if w <= F.vx and 2 * h <= F.vu
                       and F.get(w, 2 * h) != f[w][h] % P)
            say(f"  [{mode}] C0 level-0 kernel solution vs DP table: "
                f"{'OK' if bad0 == 0 else 'FAIL'}")
            allok &= bad0 == 0
            ok1, bad1 = check_grid_truth(levels, mode, truth)
            say(f"  [{mode}] C1 moment grids r=1..{MAXLEV} vs joint truth "
                f"table: {ok1} cells OK, {bad1} bad "
                f"{'OK' if bad1 == 0 else 'FAIL'}")
            allok &= bad1 == 0
            ok2, bad2 = check_diag(levels, mode, d52)
            say(f"  [{mode}] C2 diagonal vs independent univariate DP "
                f"(s<={min(NX, H) + 1}): {ok2} OK, {bad2} bad "
                f"{'OK' if bad2 == 0 else 'FAIL'}")
            allok &= bad2 == 0
            if MAXLEV >= 1:
                ok3 = check_closed_form(levels, mode, ctx)
                say(f"  [{mode}] C3 derived M1 satisfies s07 fitted closed "
                    f"form (A+B*sqrtD == M1*K^2*D^4): "
                    f"{'OK' if ok3 else 'FAIL'}")
                allok &= ok3
            say(f"  [{mode}] wall {time.time() - t0:.1f}s")
    say(f"VERDICT: {'ALL CHECKS PASS' if allok else 'FAILURES PRESENT'}")
    tag = f"_{NX}x{H}_r{MAXLEV}" + ("_big" if len(PRIMES) == 1 else "")
    with open(os.path.join(ROOT, f"out_s08_moment_kernel{tag}.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
