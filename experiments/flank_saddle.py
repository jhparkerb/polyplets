#!/usr/bin/env python3
"""Tall-flank large-deviation check: saddle-point on the grand form G*H^n
reproduces the exact banked diagonal cells (see the appendix of
results/height-distribution-collapse.md). Asserts ratio in [0.98, 1.06]
for k = 3..14 at n = 36.
"""
import types, os, io, contextlib, math
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    src = open(os.path.join(ROOT, "scripts", "derive_pk_fast.py")).read()
    mod = types.ModuleType("d")
    mod.__dict__['__file__'] = os.path.join(ROOT, "scripts", "derive_pk_fast.py")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "d", "exec"), mod.__dict__)
        Pk, _ = mod.derive(17)

    def peval(poly, n):
        r = F(0)
        for c in reversed(poly):
            r = r * n + c
        return r

    K = 17
    G = [float(peval(Pk[j], 0)) if j else 1.0 for j in range(K + 1)]
    GH = [float(peval(Pk[j], 1)) if j else 1.0 for j in range(K + 1)]
    inv = [1.0] + [0.0] * K
    for m in range(1, K + 1):
        inv[m] = -sum(G[j] * inv[m - j] for j in range(1, m + 1))
    Hs = [sum(GH[i] * inv[m - i] for i in range(m + 1)) for m in range(K + 1)]

    def ev(s, y):
        return sum(c * y ** i for i, c in enumerate(s))

    def evd(s, y):
        return sum(i * c * y ** i for i, c in enumerate(s)) / ev(s, y)

    T = {}
    d = os.path.join(ROOT, "results", "ns_a36", "perheight")
    for f in os.listdir(d):
        if f.startswith('h') and f.endswith('.out'):
            Hcol = int(f[1:-4])
            for ln in open(os.path.join(d, f)):
                nn, c = ln.split()
                T[(int(nn), Hcol)] = int(c)

    n = 36
    for k in range(3, 15):
        lo, hi = 1e-9, 0.04
        for _ in range(200):
            mid = (lo + hi) / 2
            if n * evd(Hs, mid) + evd(G, mid) - k > 0:
                hi = mid
            else:
                lo = mid
        ys = (lo + hi) / 2
        eps = ys * 1e-4
        var = (n * (evd(Hs, ys + eps) - evd(Hs, ys - eps)) +
               (evd(G, ys + eps) - evd(G, ys - eps))) / (2 * eps) * ys
        approx = math.exp((n - 1 - 3 * k) * math.log(3) + math.log(ev(G, ys))
                          + n * math.log(ev(Hs, ys)) - k * math.log(ys)
                          - 0.5 * math.log(2 * math.pi * var))
        ratio = approx / T[(n, n - k)]
        assert 0.98 < ratio < 1.06, (k, ratio)
    print("flank saddle: ratios within [0.98, 1.06] for k=3..14 at n=36  OK")


if __name__ == "__main__":
    main()
