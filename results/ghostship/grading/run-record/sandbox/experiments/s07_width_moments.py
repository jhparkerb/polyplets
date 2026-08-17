#!/usr/bin/env python3
"""Session 07: exact width-fluctuation law of convex king animals by
semiperimeter.

w_r(s) = sum_{w+h=s} w^r f(w,h), r=0,1,2.  Generating functions:
W_r(t) = (x d/dx)^r F(x,y) |_{x=y=t} — PROVABLY algebraic in
Q(t,sqrt(1-4t)) because F(x,y) is (s03 kernel-proven closed form, and
d/dx maps the field to itself).  Here we compute w_r(s) from the
validated counting DP and IDENTIFY W_2 by exact linear algebra (W_1 =
(t/2) d/dt-symmetric: w_1(s) = s*a0(s)/2 by x<->y symmetry — checked).

Then: Var(w|s) = w_2/w_0 - (s/2)^2 -> sigma^2 * s: exact sigma^2 from
singularity analysis => box-width CLT scale.  Control included.

Output: out_s07_width_moments.txt
Usage: python3 experiments/s07_width_moments.py [SMAX]
"""
import os, sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s07_moment_fit as MF
from convex_box import g_table, f_from_g

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SMAX = (int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit()
        else 48)


def g_wedge(wmax, smax, king=True):
    """counts-only DP, heights limited to the wedge w+h<=smax."""
    reach = 1 if king else 0
    g = {}
    for w in range(1, wmax + 1):
        hmax = smax - w
        if hmax < 1:
            continue
        dp = {}
        for l in range(w):
            for r in range(l, w):
                dp[(l, r, 0, 0)] = 1
        for h in range(1, hmax + 1):
            g[(w, h)] = sum(dp.values())
            if h == hmax:
                break
            ndp = defaultdict(int)
            for (l, r, pl, pr), c in dp.items():
                lo_l = l if pl else 0
                hi_r = r if pr else w - 1
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        ndp[(lp, rp, npl, npr)] += c
            dp = dict(ndp)
    return g


def main():
    lines = []
    for mode, king in (("king", True), ("poly", False)):
        g = g_wedge(SMAX - 1, SMAX, king=king)
        f = {}
        for (w, h), v in g.items():
            f[(w, h)] = (v - 2 * g.get((w - 1, h), 0) + g.get((w - 2, h), 0))
        # small-box sanity vs banked machinery
        gg = g_table(8, 8, king=king)
        ff = f_from_g(gg, 8, 8)
        for w in range(1, 9):
            for h in range(1, 9):
                if (w, h) in f:
                    assert f[(w, h)] == ff[w][h], (mode, w, h)
        w0, w1, w2 = [], [], []
        for s in range(2, SMAX + 1):
            t0 = t1 = t2 = 0
            for w in range(1, s):
                v = f[(w, s - w)]
                t0 += v; t1 += w * v; t2 += w * w * v
            w0.append(t0); w1.append(t1); w2.append(t2)
        # symmetry check: w1(s) = s*w0(s)/2
        for i, s in enumerate(range(2, SMAX + 1)):
            assert 2 * w1[i] == s * w0[i], (mode, s)
        lines.append(f"[{mode}] w_1(s) == s*a0(s)/2 for all s<=%d "
                     "(x<->y symmetry): OK" % SMAX)
        # fit W_2
        MF.NTRUNC = SMAX + 1
        found = None
        amax = 3 if king else 0
        cands = sorted((a + b + d, a, b, d) for a in range(amax + 1)
                       for b in range(2, 7) for d in range(2, 15))
        for _, a, b, d in cands:
            if MF.NTRUNC - 2 * (d + 1) < 8:
                continue
            got = MF.try_fit(w2, 2, a, b, d, d, king)
            if got:
                found = (a, b, d, got)
                break
        assert found, f"no W_2 fit ({mode})"
        a, b, d, (P, Q, surplus) = found
        den = f"(2+t)^{a} (1-4t)^{b}" if king else f"(1-4t)^{b}"
        lines.append(f"[{mode}] W_2(t) = [P + Q*sqrt(1-4t)]/{den} "
                     f"(deg<={d}, surplus={surplus})")
        lines.append(f"  P = {MF.fmt_poly(P)}")
        lines.append(f"  Q = {MF.fmt_poly(Q)}")
        # asymptotics: leading integer-pole part p0 = P(1/4)/(9/4)^a,
        # w2(s) ~ p0 C(s+b-1,b-1) 4^s; a0(s) ~ (1/128) C(s+1,1) 4^s
        P14 = sum(Fraction(c) / 4 ** k for k, c in enumerate(P))
        Q14 = sum(Fraction(c) / 4 ** k for k, c in enumerate(Q))
        p0 = P14 / (Fraction(9, 4) ** a if king else 1)
        lines.append(f"  P(1/4)={P14}, Q(1/4)={Q14}, p_0={p0}")
        # E[w^2] = w2/a0 ~ (p0/c0) * C(s+b-1,b-1)/C(s+1,1)
        # with b: if b==4: ratio ~ s^2/6 + s*...: compute exact next order
        # Var(w) = E[w^2]-(s/2)^2; expand exactly in s using C-ratios:
        # C(s+3,3)/C(s+1,1) = (s+3)(s+2)/6 (for b=4)
        # exact singular expansions of W_2 and the PROVEN r=0 form,
        # evaluated at large s (integer parts exact via comb, half-integer
        # via lgamma) -> Var(w|s) = w2/a0 - s^2/4 (w1 = s*a0/2 is EXACT).
        import s07_moment_asymptotics as MA
        from math import comb, lgamma, exp
        pw, qw = MA.expansions(a, b, P, Q, king)
        if king:
            p0f, q0f = MA.expansions(1, 2, [0, 0, 2, -10, 14, -5, -4],
                                     [0, 0, 0, -1, -4, -4], True)
        else:
            p0f, q0f = MA.expansions(0, 2, [0, 0, 1, -6, 11, -4],
                                     [0, 0, 0, 0, -4], False)

        def val(pl, ql, bb, s):
            tot = Fraction(0)
            for k, c in enumerate(pl):
                m = bb - k
                if m >= 1:
                    tot += c * comb(s + m - 1, m - 1)
            v = float(tot)
            for k, c in enumerate(ql):
                g = bb - k - 0.5
                if g <= 0:
                    continue  # (1-4t)^{|g|}: O(s^{g-1}), negligible; and
                    # lgamma sign handling for negative Gamma not needed
                v += float(c) * exp(lgamma(s + g) - lgamma(g)
                                    - lgamma(s + 1))
            return v

        lines.append("  Var(w|s)/s from exact singular expansions "
                     "(k<8 terms):")
        for s_ in (10**3, 10**4, 10**5, 10**6, 10**7):
            R = val(pw, qw, b, s_)
            A0 = val(p0f, q0f, 2, s_)
            var = R / A0 - s_ * s_ / 4
            lines.append(f"    s=10^{len(str(s_))-1}: Var/s = "
                         f"{var/s_:.8f}")
        lines.append("")
    body = "\n".join(lines)
    print(body)
    with open(os.path.join(ROOT, "out_s07_width_moments.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")


if __name__ == "__main__":
    main()
