"""The diagonal law below its onset: does the FAILURE have structure?

Law: T(n, n-k) = P_k(n) * 3^(n-1-3k), proved for n >= 2k+1, verified to fail at
n = 2k. Below onset the cells are exactly the middle band (H = n-k <= n/2).
Define the defect
        D_k(n) = T(n, n-k) - P_k(n) * 3^(n-1-3k),      k+1 <= n <= 2k
and index it by depth below onset,  j = 2k+1-n  >= 1.
If D at fixed j is structured in k, the closed-form strip widens into the band.
"""
import glob, re
from fractions import Fraction

# --- banked triangle ---
T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            T[(int(p[0]), H)] = int(p[1])

# --- P_k coefficients from the wired table (descending degree / denom) ---
src = open('orchestrator/sweep.go').read()
block = src[src.index('var diagCoeffTable = map[int]diagCoeffs{'):]
block = block[:block.index('\n}\n')]
PK = {}
for m in re.finditer(r'(\d+):\s*\{\s*\[\]string\{([^}]*)\}\s*,\s*(\d+)\s*\}', block, re.S):
    k = int(m.group(1))
    coeffs = [int(x) for x in re.findall(r'-?\d+', m.group(2))]
    PK[k] = (coeffs, int(m.group(3)))
print(f"loaded P_k for k = {sorted(PK)}")

def P(k, n):
    coeffs, den = PK[k]
    v = Fraction(0)
    for c in coeffs:
        v = v * n + c
    return v / den

def law(k, n):
    """P_k(n) * 3^(n-1-3k) as an exact rational."""
    e = n - 1 - 3 * k
    return P(k, n) * (Fraction(3) ** e)

# sanity: law must reproduce banked cells at and above onset
bad = 0
for k in sorted(PK):
    for n in range(2 * k + 1, 41):
        H = n - k
        if (n, H) in T:
            if law(k, n) != T[(n, H)]:
                bad += 1
print(f"sanity check above onset: {bad} mismatches (expect 0)")

print()
print("defect D_k(n) = T - law, indexed by depth j = 2k+1-n below onset")
print("shown as D / 3^(n-1-3k)  = P_true - P_k  (i.e. the polynomial defect)")
print()
rows = {}
for k in sorted(PK):
    for n in range(k + 1, 2 * k + 1):
        H = n - k
        if (n, H) not in T: continue
        j = 2 * k + 1 - n
        d = Fraction(T[(n, H)]) - law(k, n)
        pd = d / (Fraction(3) ** (n - 1 - 3 * k))
        rows.setdefault(j, []).append((k, n, T[(n, H)], d, pd))

for j in sorted(rows)[:6]:
    print(f"--- j = {j}  (n = 2k+1-{j}) ---")
    for k, n, t, d, pd in rows[j][:12]:
        print(f"  k={k:2d} n={n:2d} H={n-k:2d}  T={t:<22d} defect/3^e = {pd}")
    print()
