"""The defect along a fixed diagonal, below onset, as a function of H.

D_k(H) = T(H+k,H) - P_k(H+k)*3^(H+k-1-3k),  supported on H <= k (zero above).
If the transfer-matrix picture is right, the law is the leading pole and the
defect should behave like a subleading geometric term: D_k(H) ~ Q_k(H) * b^H
with b < 3.  Tested by ratios and by exact recurrence search in H.
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

print("D_k(H) = T - law, below onset (H <= k).  Ratios D_k(H)/D_k(H-1):\n")
for k in (10, 13, 16, 19):
    Hs, D = [], []
    for H in range(1, k + 1):
        n = H + k
        if (n, H) not in T: continue
        d = Fraction(T[(n, H)]) - law(k, n)
        if d != 0: Hs.append(H); D.append(d)
    ratios = [float(D[i] / D[i - 1]) for i in range(1, len(D))]
    print(f"k={k:2d}: H={Hs[0]}..{Hs[-1]}, {len(D)} nonzero defects")
    print(f"      ratios: {['%.4f' % r for r in ratios]}")
    print(f"      sign pattern: {''.join('+' if d > 0 else '-' for d in D)}")
    print()

# normalize by 3^H and look for a cleaner base
print("D_k(H) / 3^H, successive ratios (would be b/3 if D ~ Q*b^H):\n")
for k in (13, 16, 19):
    vals = []
    for H in range(1, k + 1):
        n = H + k
        if (n, H) not in T: continue
        d = Fraction(T[(n, H)]) - law(k, n)
        if d != 0: vals.append((H, d / Fraction(3) ** H))
    r = [float(vals[i][1] / vals[i - 1][1]) for i in range(1, len(vals))]
    print(f"k={k}: {['%.4f' % x for x in r]}")
