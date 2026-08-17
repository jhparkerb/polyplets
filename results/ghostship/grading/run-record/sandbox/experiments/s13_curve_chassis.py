#!/usr/bin/env python3
"""Session 13: GROUND-TRUTH check of the v-general local recursion:
run the s12 delta-Laurent chassis at a DIFFERENT point of the singular
curve (x = v^2 with v = 1/3, i.e. slice x = 1/9, s* = 3) and compare
the extracted inner profiles and values against the v-general recursion
of s13_curve_recursion.py.

Checks per (mode, prime, r <= MAXR):
  G1  inner orders: M00 -(4r+2), M10 -(4r+4), M11 -(4r+6)
  G2  inner profiles == recursion's psi_r, chi_r, phi_r as rational
      functions of tau (mu = 8v^3(1-v)tau - 1), mod p, exactly
  G3  value law: lead M11(1) = c_r(v) = (r!)^2 2^(5r+3) (v(1-v))^(3r+5)
      at val -(4r+4)   [the s09 curve-amplitude law at x=1/9]
  G4  value law: lead M11'(1) = c_r(v)/(1-v)

Usage: python3 experiments/s13_curve_chassis.py [MAXR] [NUCAP]
Output: out_s13_curve_chassis.txt
"""
import sys, os
from fractions import Fraction as Fr
from math import comb, factorial

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 4
NUCAP = int(sys.argv[2]) if len(sys.argv) > 2 else 120
_argv = sys.argv
sys.argv = [sys.argv[0]]
import s12_delta_local as CH
import s13_curve_recursion as CR      # runs its checks on import (fast)
sys.argv = _argv

V = Fr(1, 3)
SSTAR = Fr(1, 1) / V                  # = 3
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def build_ctx_v(king):
    """v-general transplant of CH.build_ctx (x = V^2)."""
    ctx = CH.Ctx()
    xf = V * V
    x = CH.C(xf)
    delta = CH.L({1: 1})
    R = CH.sqrt_init(CH.C(4 * V * V) + delta * delta, 2 * V)
    y = CH.C(1 + V * V) - R
    y1, y2 = (1 - V) ** 2, (1 + V) ** 2
    Dx = (y - CH.C(y1)) * (y - CH.C(y2))
    assert (Dx - delta * delta).is_zero(), "Delta != delta^2"
    u = CH.sqrt_init(y, 1 - V)
    ctx.x, ctx.delta, ctx.y, ctx.u = x, delta, y, u
    one = CH.C(1)
    one_m_xs = CH.SPoly([one, CH.L({0: -1}) * x])
    W = CH.SP(-1, 1) * one_m_xs
    PK = W - CH.SP(0, 1).scale(y)
    s0 = (R - delta) * CH.C(Fr(1, 2) / xf)
    s1 = (R + delta) * CH.C(Fr(1, 2) / xf)
    assert PK.eval(s0).is_zero(), "PK(s0) != 0"
    assert PK.eval(s1).is_zero(), "PK(s1) != 0"
    PK1, remPK = CH.sdiv_root(PK, s0)
    assert remPK.is_zero(), "PK not divisible by (s-s0)"
    D00 = CH.SPoly([one - y, -(x + x), x * x])
    ctx.atoms = [one_m_xs, D00, PK1]
    ctx.datoms = [a.deriv() for a in ctx.atoms]
    ctx.one_m_xs, ctx.D00, ctx.PK1, ctx.W = one_m_xs, D00, PK1, W
    if king:
        ctx.Qcomp = CH.SP(0, -1, 1).scale(x) - CH.SP(0, 1)
    else:
        ctx.Qcomp = CH.SP(0, -1)
    ctx.pts = {"s0": s0,
               "sigp": (one - u).inv(),
               "sigm": (one + u).inv()}
    ctx._apow, ctx._dp, ctx._aev, ctx._av1 = {}, {}, {}, {}

    def atom_pow(i, e):
        key = (i, e)
        if key not in ctx._apow:
            r = CH.SP(1)
            for _ in range(e):
                r = r * ctx.atoms[i]
            ctx._apow[key] = r
        return ctx._apow[key]

    def denpoly(E):
        E = tuple(E)
        if E not in ctx._dp:
            r = CH.SP(1)
            for i, ei in enumerate(E):
                if ei:
                    r = r * atom_pow(i, ei)
            ctx._dp[E] = r
        return ctx._dp[E]

    def den_eval(key, E):
        r = CH.C(1)
        for i, ei in enumerate(E):
            if ei:
                k2 = (key, i, ei)
                if k2 not in ctx._aev:
                    base = ctx.atoms[i].eval(ctx.pts[key])
                    vv = base
                    for _ in range(ei - 1):
                        vv = vv * base
                    ctx._aev[k2] = vv
                r = r * ctx._aev[k2]
        return r

    ctx.atom_val1 = [a.val1() for a in ctx.atoms]
    ctx.datom_val1 = [a.val1() for a in ctx.datoms]

    def atom_val1_pow(i, e):
        key = (i, e)
        if key not in ctx._av1:
            vv = CH.C(1)
            for _ in range(e):
                vv = vv * ctx.atom_val1[i]
            ctx._av1[key] = vv
        return ctx._av1[key]

    def den_val1(E):
        r = CH.C(1)
        for i, ei in enumerate(E):
            if ei:
                r = r * atom_val1_pow(i, ei)
        return r

    ctx.atom_pow, ctx.denpoly = atom_pow, denpoly
    ctx.den_eval, ctx.den_val1 = den_eval, den_val1
    ctx.atom_val1_pow = atom_val1_pow
    ctx.king = king
    return ctx


def recenter_at(spoly, center_num, P):
    """coeffs of (s - c)^j for integer center c (c = 3 here)."""
    cs = spoly.cs
    out = []
    for j in range(len(cs)):
        acc = CH.L()
        for i in range(j, len(cs)):
            k = comb(i, j) * pow(center_num, i - j, P)
            acc = acc + cs[i].scal(k)
        out.append(acc)
    return out


def inner_profile(G, ctx, P):
    """(ord, num-poly-in-T mod p at leading delta-order, den-poly mod p)"""
    njs = recenter_at(G.num, 3, P)
    m = None
    for j, n in enumerate(njs):
        if n.d:
            c = n.vlb() + 2 * j
            if m is None or c < m:
                m = c
    if m is None:
        return None
    nump = {}
    for j, n in enumerate(njs):
        e = m - 2 * j
        if e < n.pr:
            c = n.get(e)
            if c:
                nump[j] = c
        elif n.d or e >= n.pr:
            return "PREC"
    ordv = m
    denp = [1]
    for i in range(3):
        e = G.e[i]
        if not e:
            continue
        ajs = recenter_at(ctx.atoms[i], 3, P)
        am = min(a.vlb() + 2 * j for j, a in enumerate(ajs) if a.d)
        ordv -= e * am
        ap = {}
        for j, a in enumerate(ajs):
            ee = am - 2 * j
            if ee < a.pr and a.get(ee):
                ap[j] = a.get(ee)
        app = [0] * (max(ap) + 1)
        for j, c in ap.items():
            app[j] = c
        for _ in range(e):
            new = [0] * (len(denp) + len(app) - 1)
            for i2, ci in enumerate(denp):
                for j2, cj in enumerate(app):
                    new[i2 + j2] = (new[i2 + j2] + ci * cj) % P
            denp = new
    npoly = [0] * (max(nump) + 1 if nump else 1)
    for j, c in nump.items():
        npoly[j] = c
    return ordv, npoly, denp


def prof_matches(prof_mu, npoly, denp, P):
    """check N(T)/D(T) == sum c_m mu(T)^-m, mu(T) = (8V^3(1-V))T - 1."""
    slope = Fr(8) * V ** 3 * (1 - V)
    sl = (slope.numerator * pow(slope.denominator, P - 2, P)) % P
    mupoly = [(-1) % P, sl]
    M = max(prof_mu)
    # accumulate P_T = sum c_m mu^(M-m)
    mupows = [[1]]
    for _ in range(M):
        prev = mupows[-1]
        new = [0] * (len(prev) + 1)
        for i, ci in enumerate(prev):
            for j, cj in enumerate(mupoly):
                new[i + j] = (new[i + j] + ci * cj) % P
        mupows.append(new)
    PT = [0]
    for m, c in prof_mu.items():
        cm = (c.numerator * pow(c.denominator, P - 2, P)) % P
        pw = mupows[M - m]
        if len(pw) > len(PT):
            PT = PT + [0] * (len(pw) - len(PT))
        for i, ci in enumerate(pw):
            PT[i] = (PT[i] + cm * ci) % P
    # lhs = N*mu^M - PT*D
    muM = mupows[M]
    L1 = [0] * (len(npoly) + len(muM) - 1)
    for i, ci in enumerate(npoly):
        for j, cj in enumerate(muM):
            L1[i + j] = (L1[i + j] + ci * cj) % P
    L2 = [0] * (len(PT) + len(denp) - 1)
    for i, ci in enumerate(PT):
        for j, cj in enumerate(denp):
            L2[i + j] = (L2[i + j] + ci * cj) % P
    n = max(len(L1), len(L2))
    return all((L1[i] if i < len(L1) else 0) == (L2[i] if i < len(L2) else 0)
               for i in range(n))


def main():
    say(f"s13 curve chassis: v={V} (slice x={V*V}, s*={SSTAR}) "
        f"MAXR={MAXR} NUCAP={NUCAP}")
    cs, chis, phis = CR.run_v(V, MAXR)
    # psi profiles in mu
    kap = 32 * V ** 3 * (1 - V) ** 3
    psis = [{1: -4 * V ** 2 * (1 - V) ** 3}]
    for r in range(1, MAXR + 1):
        p = CR.dmu(psis[r - 1])
        p = {m + 1: -r * kap * c for m, c in p.items()}
        psis.append({m: c for m, c in p.items() if c})
    allok = True
    for p in [(1 << 61) - 1, 10 ** 18 + 9]:
        CH.P = p
        CH.NUCAP = NUCAP
        CH.build_ctx = build_ctx_v          # monkeypatch
        for mode in ("king", "poly"):
            ctx, levels, doms = CH.solve_all(mode == "king", MAXR)
            for r, Lr in enumerate(levels):
                res = []
                for ph, prof, base in (("M00", psis[r], 2),
                                       ("M10", chis[r], 4),
                                       ("M11", phis[r], 6)):
                    ip = inner_profile(Lr[ph], ctx, p)
                    if ip in (None, "PREC"):
                        res.append(f"{ph}:{ip}")
                        allok = False
                        continue
                    ordv, npoly, denp = ip
                    g1 = (ordv == -(4 * r + base))
                    g2 = prof_matches(prof, npoly, denp, p)
                    allok &= g1 and g2
                    res.append(f"{ph}:{'ord-OK' if g1 else 'ORD-FAIL'}"
                               f",{'prof-OK' if g2 else 'PROF-FAIL'}")
                crv = cs[r]
                cm = (crv.numerator * pow(crv.denominator, p - 2, p)) % p
                v1, l1 = CH.lead_data(Lr["M111"], 1)
                g3 = (v1 == -(4 * r + 4)) and l1 and l1[0] == cm
                dm = (crv / (1 - V))
                dm = (dm.numerator * pow(dm.denominator, p - 2, p)) % p
                d1 = Lr["M11"].deriv1()
                v2, l2 = CH.lead_data(d1, 1)
                g4 = (v2 == -(4 * r + 4)) and l2 and l2[0] == dm
                allok &= g3 and g4
                res.append(f"c_r(v):{'OK' if g3 else 'FAIL'}")
                res.append(f"d_r(v):{'OK' if g4 else 'FAIL'}")
                say(f"[{mode} p={p}] r={r}: " + " ".join(res))
    say(f"G1-G4 ALL: {'PASS' if allok else 'FAIL'}")
    with open(os.path.join(ROOT, "out_s13_curve_chassis.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipt: out_s13_curve_chassis.txt")


if __name__ == "__main__":
    main()
