"""Is the below-onset defect structured in k at fixed depth j?

Searches, in the variable k, at each fixed j:
  - minimal C-finite recurrence (holdout)
  - P-finite recurrence, poly coefficients (holdout, slack rule)
Controls: a synthetic hypergeometric sequence (must be found) and a
structureless one (must not be).
"""
import glob, re, math
from fractions import Fraction
exec(open('experiments/pfinite_slices.py').read().split("for s in (1, 2, 3):")[0])

def solve(rows, rhs, r):
    A = [row[:] + [rhs[i]] for i, row in enumerate(rows)]
    piv, row = [], 0
    for col in range(r):
        sel = next((i for i in range(row, len(A)) if A[i][col] != 0), None)
        if sel is None: continue
        A[row], A[sel] = A[sel], A[row]
        inv = A[row][col]; A[row] = [x / inv for x in A[row]]
        for i in range(len(A)):
            if i != row and A[i][col] != 0:
                f = A[i][col]; A[i] = [a - f * b for a, b in zip(A[i], A[row])]
        piv.append(col); row += 1
    for i in range(row, len(A)):
        if A[i][r] != 0: return None
    if len(piv) < r: return None
    c = [Fraction(0)] * r
    for i, col in enumerate(piv): c[col] = A[i][r]
    return c

# rebuild defect data
src = open('orchestrator/sweep.go').read()
block = src[src.index('var diagCoeffTable = map[int]diagCoeffs{'):]
block = block[:block.index('\n}\n')]
PK = {}
for m in re.finditer(r'(\d+):\s*\{\s*\[\]string\{([^}]*)\}\s*,\s*(\d+)\s*\}', block, re.S):
    PK[int(m.group(1))] = ([int(x) for x in re.findall(r'-?\d+', m.group(2))], int(m.group(3)))

def P(k, n):
    coeffs, den = PK[k]
    v = Fraction(0)
    for c in coeffs: v = v * n + c
    return v / den

DEF = {}
for k in sorted(PK):
    for n in range(k + 1, 2 * k + 1):
        H = n - k
        if (n, H) not in T: continue
        j = 2 * k + 1 - n
        d = Fraction(T[(n, H)]) - P(k, n) * Fraction(3) ** (n - 1 - 3 * k)
        DEF.setdefault(j, []).append((k, d / Fraction(3) ** (n - 1 - 3 * k)))

def cfinite(seq, maxord=8):
    N = len(seq)
    for r in range(1, maxord + 1):
        rows, rhs = [], []
        for i in range(r, N - 1):
            rows.append([Fraction(seq[i - j - 1]) for j in range(r)])
            rhs.append(Fraction(seq[i]))
        if len(rows) < r + 1: continue
        c = solve(rows, rhs, r)
        if c is None: continue
        if sum(c[j] * seq[N - 2 - j] for j in range(r)) == seq[N - 1]:
            return r, c
    return None, None

def pfinite(ks, seq, maxr=4, maxd=4):
    best = None
    for r in range(1, maxr + 1):
        for d in range(0, maxd + 1):
            unk = (r + 1) * (d + 1)
            idxs = list(range(r, len(seq) - 2))
            if len(idxs) < unk + 2: continue
            rows = []
            for i in idxs:
                row = []
                for a in range(r + 1):
                    for e in range(d + 1):
                        row.append(seq[i - a] * Fraction(ks[i]) ** e)
                rows.append(row)
            B = kernel(rows, unk)
            for v in B:
                ok = True
                for i in (len(seq) - 2, len(seq) - 1):
                    tot = Fraction(0)
                    for a in range(r + 1):
                        for e in range(d + 1):
                            tot += v[a * (d + 1) + e] * seq[i - a] * Fraction(ks[i]) ** e
                    if tot != 0: ok = False; break
                if ok and (best is None or (r, d) < best):
                    best = (r, d)
    return best

print("=== controls ===")
ctl_ks = list(range(1, 20))
hyper = [Fraction(25 ** k, math.factorial(k)) * (k * k + 3) for k in ctl_ks]   # exact
generic = [Fraction((7 ** k * (k * k + 3)) % 999983 + k) for k in ctl_ks]
print(f"  hypergeometric 25^k/k!*(k^2+3): C-finite {cfinite(hyper)[0]}, "
      f"P-finite {pfinite(ctl_ks, hyper)}")
print(f"  structureless:                  C-finite {cfinite(generic)[0]}, "
      f"P-finite {pfinite(ctl_ks, generic)}")

print("\n=== below-onset defects ===")
for j in sorted(DEF):
    ks = [k for k, _ in DEF[j]]
    seq = [d for _, d in DEF[j]]
    if len(seq) < 8: continue
    r, c = cfinite(seq)
    pf = pfinite(ks, seq)
    ratios = [float(seq[i + 1] / seq[i]) for i in range(len(seq) - 1)]
    print(f"j={j}: {len(seq)} pts (k={ks[0]}..{ks[-1]})  C-finite order={r}  "
          f"P-finite (r,d)={pf}  last ratios {['%.3f' % x for x in ratios[-4:]]}")
