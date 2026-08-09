"""Minimal constant-coefficient recurrence in H for slices n = s*H + k of the
banked polyplet height triangle, with holdout. Slope s=1 is the known diagonal
law (root 3); s>=2 cuts the middle band and has never been tested."""
import glob, re, sys
from fractions import Fraction

T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            T[(int(p[0]), H)] = int(p[1])

def minimal_order(seq, maxord=8):
    """smallest r with a constant-coeff recurrence fitting all but the last
    point, verified on that held-out last point."""
    N = len(seq)
    for r in range(1, maxord + 1):
        rows, rhs = [], []
        for i in range(r, N - 1):                       # holdout = final point
            rows.append([Fraction(seq[i - j - 1]) for j in range(r)])
            rhs.append(Fraction(seq[i]))
        if len(rows) < r + 1:                            # need slack, not just r
            continue
        c = solve(rows, rhs, r)
        if c is None:
            continue
        pred = sum(c[j] * seq[N - 2 - j] for j in range(r))
        if pred == seq[N - 1]:
            return r, c
    return None, None

def solve(rows, rhs, r):
    A = [row[:] + [rhs[i]] for i, row in enumerate(rows)]
    piv = []
    row = 0
    for col in range(r):
        sel = next((i for i in range(row, len(A)) if A[i][col] != 0), None)
        if sel is None:
            continue
        A[row], A[sel] = A[sel], A[row]
        inv = A[row][col]
        A[row] = [x / inv for x in A[row]]
        for i in range(len(A)):
            if i != row and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[row])]
        piv.append(col); row += 1
    for i in range(row, len(A)):
        if A[i][r] != 0:
            return None                                   # inconsistent
    if len(piv) < r:
        return None                                       # underdetermined
    c = [Fraction(0)] * r
    for i, col in enumerate(piv):
        c[col] = A[i][r]
    return c

for s in (1, 2, 3):
    for k in (0, 1, 2):
        seq, Hs = [], []
        H = 1
        while True:
            n = s * H + k
            if n > 40 or H > 40:
                break
            v = T.get((n, H))
            if v is None:
                break
            seq.append(v); Hs.append(H); H += 1
        seq2 = [x for x in seq if x]                       # drop leading zeros
        off = len(seq) - len(seq2)
        if len(seq2) < 6:
            print(f"s={s} k={k}: only {len(seq2)} nonzero points, skipped"); continue
        r, c = minimal_order(seq2)
        ratio = seq2[-1] / seq2[-2]
        print(f"s={s} k={k}: H={Hs[off]}..{Hs[-1]} ({len(seq2)} pts) "
              f"minimal order={r} last-ratio={ratio:.5f}")
        if r:
            print(f"           coeffs {[str(x) for x in c]}")
