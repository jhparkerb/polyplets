"""Alternative slicings/combinations of the height triangle.

1. row polynomial F_n(y) = sum_H T(n,H) y^H at special y (3 is the law's base)
2. alternating row sums
3. parity structure: number of odd entries per row
4. real-rootedness / log-concavity of rows and columns
5. atom degrees vs sqrt(lambda)^H
"""
import glob, re, math
from fractions import Fraction
import numpy as np

T, A = {}, {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            n, v = int(p[0]), int(p[1])
            T[(n, H)] = v
            if v: A[n] = A.get(n, 0) + v
row = {n: [T.get((n, H), 0) for H in range(1, n + 1)] for n in range(1, 41)}

def cfin(seq, maxord=8):
    """minimal C-finite order over Q with the last point held out"""
    N = len(seq)
    for r in range(1, maxord + 1):
        rows, rhs = [], []
        for i in range(r, N - 1):
            rows.append([Fraction(seq[i - j - 1]) for j in range(r)]); rhs.append(Fraction(seq[i]))
        if len(rows) < r + 2: continue
        A_ = [rw[:] + [rhs[i]] for i, rw in enumerate(rows)]
        piv, rr = [], 0
        for c in range(r):
            sel = next((i for i in range(rr, len(A_)) if A_[i][c] != 0), None)
            if sel is None: continue
            A_[rr], A_[sel] = A_[sel], A_[rr]
            inv = A_[rr][c]; A_[rr] = [x / inv for x in A_[rr]]
            for i in range(len(A_)):
                if i != rr and A_[i][c] != 0:
                    f = A_[i][c]; A_[i] = [a - f * b for a, b in zip(A_[i], A_[rr])]
            piv.append(c); rr += 1
        if any(A_[i][r] != 0 for i in range(rr, len(A_))) or len(piv) < r: continue
        c = [Fraction(0)] * r
        for i, cc in enumerate(piv): c[cc] = A_[i][r]
        if sum(c[j] * seq[N - 2 - j] for j in range(r)) == seq[N - 1]: return r
    return None

print("1. ROW POLYNOMIAL AT SPECIAL POINTS  F_n(y) = sum_H T(n,H) y^H")
for y in (Fraction(-1), Fraction(1, 3), Fraction(-1, 3), Fraction(3), Fraction(1, 9), Fraction(9)):
    vals = []
    for n in range(1, 41):
        v = sum(Fraction(T.get((n, H), 0)) * y ** H for H in range(1, n + 1))
        vals.append(v)
    tail = vals[6:]
    r = cfin(tail)
    # is it eventually an integer / nice?
    ints = all(v.denominator == 1 for v in vals)
    print(f"  y={str(y):6s}: C-finite order={r}   all-integer={ints}   "
          f"first few: {[str(v) for v in vals[:4]]}")

print("\n2. ALTERNATING ROW SUMS  sum_H (-1)^H T(n,H)   (= -F_n(-1), shown above)")
alt = [sum((-1) ** H * T.get((n, H), 0) for H in range(1, n + 1)) for n in range(1, 41)]
print(f"   first 12: {alt[:12]}")
print(f"   C-finite order (n>=7): {cfin(alt[6:])}")
print(f"   signs: {''.join('+' if x > 0 else ('0' if x == 0 else '-') for x in alt)}")

print("\n3. PARITY: number of odd entries in row n")
odd = [sum(1 for H in range(1, n + 1) if T.get((n, H), 0) % 2) for n in range(1, 41)]
print(f"   {odd}")
print(f"   powers of 2? {[x & (x - 1) == 0 for x in odd[:20]]}")
print(f"   C-finite order: {cfin([Fraction(x) for x in odd[6:]])}")

print("\n4. LOG-CONCAVITY / REAL-ROOTEDNESS")
def logconc(seq):
    s = [x for x in seq if x]
    return all(s[i] * s[i] >= s[i - 1] * s[i + 1] for i in range(1, len(s) - 1))
bad_rows = [n for n in range(3, 41) if not logconc(row[n])]
cols = {H: [T[(n, H)] for n in range(1, 41) if T.get((n, H))] for H in range(1, 21)}
bad_cols = [H for H, s in cols.items() if len(s) > 2 and not logconc(s)]
print(f"   rows log-concave in H: {'ALL' if not bad_rows else 'fail at n=' + str(bad_rows)}")
print(f"   columns log-concave in n: {'ALL' if not bad_cols else 'fail at H=' + str(bad_cols)}")
for n in (20, 30, 40):
    c = [float(x) for x in row[n] if x]
    c = [x / max(c) for x in c]
    rts = np.roots(c[::-1])
    nreal = sum(1 for z in rts if abs(z.imag) < 1e-8 * max(1, abs(z.real)))
    print(f"   row {n}: degree {len(c)-1}, real roots {nreal}/{len(rts)}, "
          f"max |Im| {max(abs(z.imag) for z in rts):.3g}")

print("\n5. ATOM DEGREES vs sqrt(lambda)^H   (lambda = 7.110, sqrt = 2.6665)")
deg = [1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289]
for i in range(1, len(deg)):
    print(f"   H={i+1:2d}: deg={deg[i]:5d}  ratio={deg[i]/deg[i-1]:.4f}")
Hs = np.arange(5, 11); ys = np.log([deg[h - 1] for h in Hs])
Amat = np.column_stack([np.ones(len(Hs)), Hs])
(c0, c1), *_ = np.linalg.lstsq(Amat, ys, rcond=None)
print(f"   fit deg ~ C*b^H over H=5..10: b = {math.exp(c1):.4f}  (sqrt(lambda) = {math.sqrt(7.110):.4f})")
