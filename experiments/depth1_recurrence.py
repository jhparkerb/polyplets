#!/usr/bin/env python3
"""The depth-1 defect IS P-finite — at (r,d) = (35,4), from the curve.

experiments/depth1_minpoly.py pins the quartic Phi(x, W) annihilating
N(x) = sum N_k x^k, N_k = 3^(k+1) D_1(k).  Algebraic => D-finite: this script
derives the order-4 linear ODE for N over Q(x) (coefficient degrees 29..36),
converts it to the recurrence

    sum_{s=-32..3} q_s(n) N_{n+s} = 0,   deg_n q_s <= 4,

and verifies the recurrence EXACTLY (integer arithmetic) on the gap-walk
series.  Order 35, degree 4: this is why every P-finite search failed —
the envelopes (r,d) <= (4,4) (defect_pfinite_full) and (6,8)
(depth1_asymptotics) never stood a chance.  The old "not P-finite in the
reachable envelope" verdicts were correct as scoped and are now explained.

Run from repo root: python3 experiments/depth1_recurrence.py
"""
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import walk_families, series_D1            # noqa: E402

x, W = sp.symbols('x W')
# Phi from depth1_minpoly.py (holdout-verified through x^200 there)
PHI_COEFFS = [
    x*(19683*x**7 - 30618*x**6 + 89667*x**5 - 63720*x**4 - 4920*x**3
       + 16560*x**2 + 2736*x - 64),
    (27*x - 1)*(8748*x**7 - 16767*x**6 + 36045*x**5 - 18573*x**4
                - 7197*x**3 + 5076*x**2 + 1148*x - 16),
    3*(27*x - 1)*(13122*x**7 - 29403*x**6 + 50193*x**5 - 14487*x**4
                  - 15039*x**3 + 5790*x**2 + 1640*x - 48),
    (27*x - 1)**2*(2916*x**6 - 7155*x**5 + 9636*x**4 + 54*x**3
                   - 4284*x**2 + 877*x + 420),
    (27*x - 1)**2*(2187*x**6 - 5751*x**5 + 5502*x**4 + 3486*x**3
                   - 4329*x**2 + 449*x + 392),
]


def main():
    t0 = time.time()
    Phi = sum(c * W ** j for j, c in enumerate(PHI_COEFFS))
    Kx = sp.QQ.frac_field(x)
    P = sp.Poly(Phi, W, domain=Kx)
    PW = P.diff(W)
    s_, t_, h = sp.gcdex(PW.as_expr(), P.as_expr(), W)
    assert not sp.simplify(h).has(W)
    inv_PW = sp.Poly(s_ / h, W, domain=Kx)
    Px = sp.Poly(sp.diff(Phi, x), W, domain=Kx)
    Fprime = (sp.Poly(-Px.as_expr(), W, domain=Kx) * inv_PW) % P

    def tovec(p):
        c = sp.Poly(p, W, domain=Kx).all_coeffs()[::-1]
        c = list(c) + [0] * (4 - len(c))
        return [sp.together(ci.as_expr() if hasattr(ci, 'as_expr') else ci)
                for ci in c[:4]]

    def dvec(vec):
        out = sp.Poly(0, W, domain=Kx)
        for j, cj in enumerate(vec):
            out = out + sp.Poly(sp.diff(cj, x) * W ** j, W, domain=Kx)
            if j > 0:
                out = (out + (sp.Poly(j * cj * W ** (j - 1), W, domain=Kx)
                              * Fprime) % P) % P
        return tovec(out)

    vecs = [tovec(sp.Poly(W, W, domain=Kx))]
    for _ in range(4):
        vecs.append(dvec(vecs[-1]))
    M = sp.Matrix([[sp.together(v[j]) for j in range(4)] for v in vecs]).T
    ns = M.nullspace()
    assert len(ns) == 1, f"ODE nullspace dim {len(ns)}"
    v = ns[0]
    den = sp.lcm([sp.fraction(sp.cancel(e))[1] for e in v])
    pol = [sp.expand(sp.cancel(e * den)) for e in v]
    g = sp.gcd(pol)
    pol = [sp.cancel(e / g) for e in pol]
    degs = [sp.degree(e, x) if e != 0 else -1 for e in pol]
    print(f"ODE: order {len(pol) - 1}, coefficient x-degrees {degs}  "
          f"[{time.time() - t0:.0f}s]")

    n = sp.symbols('n')
    rec = defaultdict(lambda: sp.Integer(0))
    for i, p in enumerate(pol):
        for (m,), c in sp.Poly(p, x).terms():
            sft = i - m
            rec[sft] += c * sp.prod([(n + sft - t) for t in range(i)])
    shifts = sorted(rec.keys())
    order = shifts[-1] - shifts[0]
    degn = max(sp.degree(sp.expand(rec[s]), n) for s in shifts)
    print(f"recurrence: shifts {shifts[0]}..{shifts[-1]}, ORDER {order}, "
          f"max deg_n {degn}")

    KK = 90
    fams = walk_families(KK)
    D1 = series_D1(fams, KK)
    N = [0] + [int(D1[k] * Fr(3) ** (k + 1)) for k in range(1, KK + 1)]
    qs = {s2: sp.expand(rec[s2]) for s2 in shifts}
    nver = 0
    for base in range(-shifts[0], KK - shifts[-1] + 1):
        tot = 0
        for s2 in shifts:
            tot += int(qs[s2].subs(n, base)) * N[base + s2]
        assert tot == 0, f"recurrence FAILS at n = {base}"
        nver += 1
    print(f"recurrence verified exactly (integers) at {nver} positions, "
          f"n = {-shifts[0]}..{KK - shifts[-1]}")
    print("=> N_k is P-finite at (r,d) = (35,4); the searched envelopes")
    print("   (4,4) and (6,8) were far too small, as the curve now explains.")
    print(f"total {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
