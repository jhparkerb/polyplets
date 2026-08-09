"""P-finite (polynomial-coefficient) recurrence search on slope-s slicings.

Seeks  sum_{i=0..r} p_i(H) * T(s*(H-i)+k, H-i) = 0,  deg p_i <= d, over Q.
Homogeneous nullspace, exact rationals. Discipline: the last TWO points of the
slice are held out of the fit and must be predicted; and the fit is required to
have at least 2 more equations than unknowns, so a kernel is evidence rather
than an artifact of underdetermination. Onset scanned by dropping leading points.
"""
import glob, re
from fractions import Fraction

T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            T[(int(p[0]), H)] = int(p[1])

def slice_seq(s, k):
    Hs, seq = [], []
    H = 1
    while s * H + k <= 40:
        v = T.get((s * H + k, H))
        if v is None: break
        if v: Hs.append(H); seq.append(v)
        H += 1
    return Hs, seq

def kernel(rows, ncol):
    """Exact rational nullspace basis of the row list."""
    A = [[Fraction(x) for x in row] for row in rows]
    piv, r = [], 0
    for c in range(ncol):
        sel = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if sel is None: continue
        A[r], A[sel] = A[sel], A[r]
        inv = A[r][c]; A[r] = [x / inv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]; A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        piv.append(c); r += 1
    free = [c for c in range(ncol) if c not in piv]
    basis = []
    for fc in free:
        v = [Fraction(0)] * ncol; v[fc] = Fraction(1)
        for i, c in enumerate(piv):
            v[c] = -A[i][fc]
        basis.append(v)
    return basis

def eqn(Hs, seq, idx, r, d):
    """One equation's coefficient row at slice index idx (needs idx>=r)."""
    H = Hs[idx]
    row = []
    for i in range(r + 1):
        val = seq[idx - i]
        for e in range(d + 1):
            row.append(val * H ** e)
    return row

def search(s, k, maxr=5, maxd=5, onsets=6):
    Hs, seq = slice_seq(s, k)
    out = []
    for t in range(onsets):
        H2, s2 = Hs[t:], seq[t:]
        for r in range(1, maxr + 1):
            for d in range(0, maxd + 1):
                unk = (r + 1) * (d + 1)
                fit_idx = list(range(r, len(s2) - 2))       # hold out last 2
                if len(fit_idx) < unk + 2:                  # slack rule
                    continue
                rows = [eqn(H2, s2, i, r, d) for i in fit_idx]
                B = kernel(rows, unk)
                if not B: continue
                ok = []
                for v in B:
                    good = all(sum(a * b for a, b in zip(eqn(H2, s2, i, r, d), v)) == 0
                               for i in (len(s2) - 2, len(s2) - 1))
                    ok.append(good)
                if any(ok):
                    out.append((H2[0], r, d, len(B), sum(ok)))
    return Hs, seq, out

for s in (1, 2, 3):
    for k in (0, 1, 2):
        Hs, seq, hits = search(s, k)
        tag = f"s={s} k={k} ({len(seq)} pts, H={Hs[0]}..{Hs[-1]})"
        if hits:
            best = min(hits, key=lambda h: ((h[1] + 1) * (h[2] + 1), h[1]))
            print(f"{tag}: FOUND  onset H>={best[0]} order={best[1]} deg={best[2]} "
                  f"(kernel dim {best[3]}, {best[4]} pass holdout); {len(hits)} (r,d,onset) combos total")
        else:
            print(f"{tag}: none")

print()
print("=== envelope actually tested (onset t=0), per slice ===")
for s in (1, 2, 3):
    for k in (0,):
        Hs, seq = slice_seq(s, k)
        env = []
        for r in range(1, 6):
            dmax = -1
            for d in range(0, 6):
                unk = (r + 1) * (d + 1)
                if len(range(r, len(seq) - 2)) >= unk + 2: dmax = d
            if dmax >= 0: env.append(f"r={r}:d<={dmax}")
        print(f"s={s} k={k} ({len(seq)} pts): " + ", ".join(env))
