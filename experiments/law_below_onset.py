"""How WRONG is the diagonal law below its onset?

The law is proved for n >= 2k+1 and verified to fail at n <= 2k. Measure the
relative error of P_k(n)*3^(n-1-3k) against the banked T(n,n-k) in the invalid
region, as a function of depth j = 2k+1-n below onset.
"""
import glob, re
from fractions import Fraction

T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2: T[(int(p[0]), H)] = int(p[1])

src = open('orchestrator/sweep.go').read()
block = src[src.index('var diagCoeffTable = map[int]diagCoeffs{'):]
block = block[:block.index('\n}\n')]
PK = {}
for m in re.finditer(r'(\d+):\s*\{\s*\[\]string\{([^}]*)\}\s*,\s*(\d+)\s*\}', block, re.S):
    PK[int(m.group(1))] = ([int(x) for x in re.findall(r'-?\d+', m.group(2))], int(m.group(3)))

def law(k, n):
    coeffs, den = PK[k]
    v = Fraction(0)
    for c in coeffs: v = v * n + c
    return v / den * Fraction(3) ** (n - 1 - 3 * k)

import math
print("relative error of the law below onset:  -log10 |law/T - 1|  (digits correct)")
print("rows = depth j below onset (j=0 is the onset itself, where it is exact)\n")
hdr = "  k:" + "".join(f"{k:7d}" for k in range(6, 20))
print(hdr)
for j in range(0, 9):
    line = f"j={j}:"
    for k in range(6, 20):
        n = 2 * k + 1 - j
        H = n - k
        if (n, H) not in T or k not in PK or H < 1:
            line += "      ."; continue
        t = Fraction(T[(n, H)])
        rel = abs(law(k, n) / t - 1)
        if rel == 0:
            line += "    EX "
        else:
            line += f"{-math.log10(float(rel)):7.1f}"
    print(line)

print("\nsame thing read as: how many leading digits of the true cell does the")
print("closed form get right, in the region where it is provably invalid.")
