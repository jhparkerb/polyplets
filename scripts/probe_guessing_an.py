#!/usr/bin/env python3
# probe_guessing_an.py — scaling-exploration lane A (2026-08-11, throwaway).
# Guessing probes on the banked a(n) = A006770, n = 1..40
# (results/b006770_upload.txt).
#
# (a) Holonomic (P-recurrence) guess over Q: sum_{i<=r} c_i(n) a(n+i) = 0,
#     deg c_i <= d. Exact nullspace (Fraction). Sweep every (r,d) box with
#     unknowns (r+1)(d+1) <= equations (40-r) minus 8 slack. A hit with >= 8
#     surplus equations is structure; empty sweep is the scored negative.
# (b) Algebraic guess mod 2 and mod 3 (Christol: algebraic over F_p(x) <=>
#     a(n) mod p is p-automatic): find P(x,F) = sum_j c_j(x) F^j = 0 mod x^41,
#     deg c_j <= dx, J <= 5, same 8-equation slack, exact linear algebra
#     over F_p. Not-all-zero solutions with slack reported; else negative.
# Cost: seconds, 1 core, foreground.
import sys
from fractions import Fraction

an = []
for line in open("/Users/jasonp/src/polyominoes/results/b006770_upload.txt"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    n, v = line.split()
    an.append(int(v))
N = len(an)
print(f"loaded {N} terms of A006770")
SLACK = 8

def nullspace_frac(rows, ncols):
    """rows: list of lists of Fraction/int. Return basis of nullspace (list of tuples)."""
    M = [[Fraction(x) for x in r] for r in rows]
    piv_cols, row = [], 0
    for col in range(ncols):
        p = None
        for r in range(row, len(M)):
            if M[r][col] != 0: p = r; break
        if p is None: continue
        M[row], M[p] = M[p], M[row]
        inv = M[row][col]
        M[row] = [x / inv for x in M[row]]
        for r in range(len(M)):
            if r != row and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f*b for a, b in zip(M[r], M[row])]
        piv_cols.append(col); row += 1
    free = [c for c in range(ncols) if c not in piv_cols]
    basis = []
    for fc in free:
        v = [Fraction(0)]*ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(piv_cols):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis

# (a) holonomic sweep
print("\n(a) P-recurrence boxes over Q, slack >= 8:")
found_a = []
for r in range(1, 8):
    eqs = N - r
    for d in range(0, 12):
        unk = (r+1)*(d+1)
        if unk > eqs - SLACK: break
        rows = []
        for n0 in range(1, eqs+1):  # n = n0, terms a(n0+i), 1-indexed an[]
            row = []
            for i in range(r+1):
                for k in range(d+1):
                    row.append((n0**k) * an[n0-1+i])
            rows.append(row)
        ns = nullspace_frac(rows, (r+1)*(d+1))
        if ns:
            found_a.append((r, d, len(ns)))
            print(f"  HIT r={r} d={d}: nullspace dim {len(ns)} with {eqs-unk} surplus eqs")
if not found_a:
    print(f"  none: no P-recurrence with (r+1)(d+1) <= eqs-{SLACK} for r<=7, d<=11")
    print("  boxes swept:", [(r, max(0, min(11, (N-r-SLACK)//(r+1)-1))) for r in range(1,8)])

# (b) algebraic mod p
def algebraic_guess(p):
    a = [x % p for x in an]
    # F = sum_{n>=1} a(n) x^n; powers F^j mod x^(N+1)
    F = [0] + a  # index = exponent, length N+1
    def mulmod(A, B):
        C = [0]*(N+1)
        for i, ai in enumerate(A):
            if ai:
                for j, bj in enumerate(B):
                    if i+j <= N and bj:
                        C[i+j] = (C[i+j] + ai*bj) % p
        return C
    pows = [[1] + [0]*N]
    for j in range(5):
        pows.append(mulmod(pows[-1], F))
    hits = []
    for J in range(1, 6):
        for dx in range(0, 40):
            unk = (J+1)*(dx+1)
            eqs = N + 1  # coefficients of x^0..x^N must vanish
            if unk > eqs - SLACK: break
            # unknown c_{j,k}: coefficient matrix rows = exponent e, cols = (j,k)
            rows = []
            for e in range(N+1):
                row = []
                for j in range(J+1):
                    for k in range(dx+1):
                        row.append(pows[j][e-k] if 0 <= e-k <= N else 0)
                rows.append(row)
            # nullspace over F_p
            M = [r[:] for r in rows]
            ncols = unk; pivc, rr = [], 0
            for col in range(ncols):
                pv = None
                for q in range(rr, len(M)):
                    if M[q][col] % p: pv = q; break
                if pv is None: continue
                M[rr], M[pv] = M[pv], M[rr]
                inv = pow(M[rr][col], p-2, p)
                M[rr] = [x*inv % p for x in M[rr]]
                for q in range(len(M)):
                    if q != rr and M[q][col] % p:
                        f = M[q][col]
                        M[q] = [(x - f*y) % p for x, y in zip(M[q], M[rr])]
                pivc.append(col); rr += 1
            dim = ncols - len(pivc)
            if dim > 0:
                hits.append((J, dx, dim, eqs-unk))
        # report smallest hit per J only
    return hits

for p in (2, 3):
    hits = algebraic_guess(p)
    print(f"\n(b) algebraic mod {p}, slack >= {SLACK}:")
    if hits:
        for J, dx, dim, surplus in hits[:6]:
            print(f"  HIT J={J} dx={dx}: nullspace dim {dim}, surplus {surplus}")
    else:
        print(f"  none: no P(x,F)=0 with deg_F <= 5, (J+1)(dx+1) <= {N+1-SLACK}")
