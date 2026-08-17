#!/usr/bin/env python3
"""Session 13: check the derived value law  lead M11^(r)'(1) = 2 c_r.

Predicted by K11-root removability at z = -4 in the local transfer
(results/convex-area-local-transfer.md section 2): M11'(1) has leading
Laurent coefficient 2c_r at valuation -(4r+4), i.e. EXACTLY twice the
M11(1) leading coefficient, in both modes.

Usage: python3 experiments/s13_dr_check.py [MAXR] [NUCAP]
Output: out_s13_dr_check.txt
"""
import sys, os
from math import factorial

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
NUCAP = int(sys.argv[2]) if len(sys.argv) > 2 else 150
_argv = sys.argv
sys.argv = [sys.argv[0]]
import s12_delta_local as CH
sys.argv = _argv

OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


allok = True
for p in [(1 << 61) - 1, 10 ** 18 + 9]:
    CH.P = p
    CH.NUCAP = NUCAP
    for mode in ("king", "poly"):
        ctx, levels, doms = CH.solve_all(mode == "king", MAXR)
        for r, Lr in enumerate(levels):
            d1 = Lr["M11"].deriv1()
            v, cs = CH.lead_data(d1, 2)
            cr = factorial(r) ** 2 * pow(2, (r + 7) * (p - 2), p) % p
            ok = (v == -(4 * r + 4)) and cs and cs[0] == 2 * cr % p
            allok &= ok
            say(f"[{mode} p={p}] r={r}: val M11'(1)={v} "
                f"(want {-(4*r+4)}), lead==2c_r: {'OK' if ok else 'FAIL'}")
say(f"d_r = 2 c_r law, r<={MAXR}, both modes, both primes: "
    f"{'PASS' if allok else 'FAIL'}")
with open(os.path.join(ROOT, "out_s13_dr_check.txt"), "w") as fp:
    fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
