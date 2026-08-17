#!/usr/bin/env python3
"""s09: exact-Fraction re-expansion of the banked A_r closed forms
(r=0..4, king+poly; numerators as hardcoded in s09_slice_moments.BANKED,
sourced from s01/s03, results/convex-area-moments.md, out_s07_r4_fit.txt)
against the independent moment-DP sequences out_s07_area_moments_r4_57.json.
Doubles as (a) typo-proof of the s09 anchor table and (b) an independent
VERIFY of the s07/s08 fitted closed forms. Output: out_s09_anchor_check.txt
"""
import json, sys
from fractions import Fraction as Fr
sys.path.insert(0, 'experiments')
from s09_slice_moments import BANKED, anchor_consts

d = json.load(open('out_s07_area_moments_r4_57.json'))
N = 50
SQ = [Fr(1)]
for k in range(1, N):
    SQ.append(SQ[-1] * Fr(Fr(1, 2) - (k - 1), k) * (-4))

def mulser(a, b):
    return [sum(a[i] * b[n - i] for i in range(n + 1)) for n in range(N)]

def invser(a):
    r = [Fr(1) / a[0]]
    for n in range(1, N):
        r.append(-sum(a[i] * r[n - i] for i in range(1, n + 1)) / a[0])
    return r

out = []
allok = True
for mode in ('king', 'poly'):
    for r in range(5):
        P, Q = BANKED[(mode, r)]
        P = [Fr(c) for c in P] + [Fr(0)] * N
        Q = [Fr(c) for c in Q] + [Fr(0)] * N
        num = [P[n] + sum(Q[i] * SQ[n - i] for i in range(n + 1))
               for n in range(N)]
        den = [Fr(1)] + [Fr(0)] * (N - 1)
        twot = [Fr(2), Fr(1)] + [Fr(0)] * (N - 2)
        onem4 = [Fr(1), Fr(-4)] + [Fr(0)] * (N - 2)
        if mode == 'king':
            for _ in range(r + 1):
                den = mulser(den, twot)
    # king den also gets (1-4t) powers below
        for _ in range(2 * r + 2):
            den = mulser(den, onem4)
        ser = mulser(num, invser(den))
        seq = d[mode][f'a{r}']
        start = d['start']
        bad = sum(1 for s in range(start, start + len(seq))
                  if s < N and ser[s] != seq[s - start])
        nch = sum(1 for s in range(start, start + len(seq)) if s < N)
        cP, cQ = anchor_consts(mode, r)
        line = (f"{mode} r={r}: banked closed form vs DP57 sequence: "
                f"{'OK' if bad == 0 else 'FAIL'} ({nch} terms)  "
                f"anchor cP={cP} cQ={cQ}")
        allok &= bad == 0
        print(line)
        out.append(line)
out.append("VERDICT: " + ("ALL OK" if allok else "FAILURES"))
print(out[-1])
open('out_s09_anchor_check.txt', 'w').write(__doc__ + "\n" + "\n".join(out) + "\n")
