"""Two exact-integer probes our earlier tests were blind to.

A. q-holonomic: sum_i c_i(H, q^H) S(H-i) = 0, coefficients polynomial in BOTH H
   and q^H.  (Note: a GLOBAL factor q^H is invisible here by design -- C-finite
   and P-finite are invariant under geometric rescaling, so that case was
   already covered.  What is new is q^H inside the coefficients.)
B. residues: is S(H) mod m eventually periodic?  (valuations tested earlier are
   a different property)

Controls in both: a sequence with the structure, which must be found, and the
real slice.
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

Hs = [H for H in range(1, 21) if T.get((2 * H, H))]
S  = [T[(2 * H, H)] for H in Hs]
Sk = [T[(H + 2, H)] for H in range(1, 21) if T.get((H + 2, H))]

# synthetic positive control: genuinely q-holonomic, S(H+1) = (2^H + 1) S(H)
QSYN = [1]
for H in range(1, 20):
    QSYN.append(QSYN[-1] * (2 ** H + 1))

def kernel(rows, ncol):
    A = [[Fraction(x) for x in r] for r in rows]
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
    out = []
    for fc in free:
        v = [Fraction(0)] * ncol; v[fc] = Fraction(1)
        for i, c in enumerate(piv): v[c] = -A[i][fc]
        out.append(v)
    return out

def row_of(seq, Hval, idx, r, d, B, q):
    row = []
    for i in range(r + 1):
        val = seq[idx - i]
        for a in range(d + 1):
            for b in range(B + 1):
                row.append(val * Hval ** a * q ** (b * Hval))
    return row

def qsearch(seq, Hs, qs=(2, 3, 5), maxr=3, maxd=2, maxB=2, onsets=4):
    hits = []
    for t in range(onsets):
        s2, H2 = seq[t:], Hs[t:]
        for q in qs:
            for r in range(1, maxr + 1):
                for d in range(0, maxd + 1):
                    for B in range(0, maxB + 1):
                        unk = (r + 1) * (d + 1) * (B + 1)
                        idxs = list(range(r, len(s2) - 2))
                        if len(idxs) < unk + 2: continue
                        rows = [row_of(s2, H2[i], i, r, d, B, q) for i in idxs]
                        for v in kernel(rows, unk):
                            ok = all(sum(a * b for a, b in
                                     zip(row_of(s2, H2[i], i, r, d, B, q), v)) == 0
                                     for i in (len(s2) - 2, len(s2) - 1))
                            if ok:
                                hits.append((H2[0], q, r, d, B)); break
    return hits

print("=" * 74)
print("A. q-HOLONOMIC SEARCH  (coefficients polynomial in H and q^H)")
print("=" * 74)
for label, seq, hh in (("CONTROL synthetic S(H+1)=(2^H+1)S(H)", QSYN, list(range(1, 21))),
                       ("CONTROL s=1 k=2 (constant-coeff, order 5)", Sk, list(range(1, 21))),
                       ("SLOPE-2 T(2H,H)", S, Hs)):
    hits = qsearch(seq, hh)
    if hits:
        best = min(hits, key=lambda h: (h[2], h[3], h[4]))
        print(f"{label:42s} FOUND: onset H>={best[0]} q={best[1]} r={best[2]} "
              f"d={best[3]} B={best[4]}  ({len(hits)} combos)")
    else:
        print(f"{label:42s} none")

print()
print("=" * 74)
print("B. RESIDUES MOD m: eventual periodicity  (period p, from index i0)")
print("=" * 74)
def periodic(seq, m, maxper=6, maxstart=8):
    res = [x % m for x in seq]
    for i0 in range(maxstart):
        tail = res[i0:]
        for p in range(1, maxper + 1):
            if len(tail) < 3 * p: continue          # need >=2 periods + holdout
            if all(tail[j] == tail[j % p] for j in range(len(tail))):
                return i0, p, tail[:p]
    return None

CAT = [1]
for i in range(19): CAT.append(CAT[-1] * 2 * (2 * i + 1) // (i + 2))
for label, seq in (("CONTROL Catalan (mod 2 is structured)", CAT),
                   ("CONTROL s=1 k=2 (carries 3^H)", Sk),
                   ("SLOPE-2 T(2H,H)", S)):
    print(f"\n{label}")
    for m in (2, 3, 4, 5, 7, 8, 9, 11):
        r = periodic(seq, m)
        res = [x % m for x in seq][:14]
        note = f"eventually periodic: start {r[0]}, period {r[1]}, cycle {r[2]}" if r else "no short period"
        print(f"  mod {m:2d}: {res} ...  {note}")
