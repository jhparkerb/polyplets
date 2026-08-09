#!/usr/bin/env python3
"""Is the depth-j defect sequence D_j(k) P-finite?  Full honest envelope.

D_j(k) = T(2k+1-j, k+1-j) - P_k(...)*3^(...) is an EXACT rational for k<=19.
Its measured asymptotics 9^k k^(j-3/2) with amplitude sqrt6/(27 sqrt pi) is
exactly what an algebraic generating function singular like (1-9z)^-1/2 would
give -- and algebraic => D-finite => P-finite.  So this is the decisive test.

Discipline: exact rational nullspace; the last TWO points held out and required
to be predicted; at least 2 equations of slack beyond the unknowns; onset
scanned.  Positive controls that must fire, plus a structureless control that
must not.
"""
import os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law
P, tri = read_pk(), read_tri()

def nullspace(M, ncol):
    """exact nullspace basis of the row list M (each len ncol)."""
    M = [row[:] for row in M]
    piv, r = [], 0
    for c in range(ncol):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        inv = M[r][c]
        M[r] = [x/inv for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j]-f*M[r][j] for j in range(ncol)]
        piv.append(c); r += 1
        if r == len(M): break
    free = [c for c in range(ncol) if c not in piv]
    basis = []
    for fc in free:
        v = [F(0)]*ncol; v[fc] = F(1)
        for i, pc in enumerate(piv):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis

def search(seq, name, rmax=6, dmax=6, tmax=4):
    """seq = list of (k, Fraction). returns list of (r,d,t) that fit+predict."""
    hits = []
    for t in range(0, tmax+1):
        s = seq[t:]
        if len(s) < 8: continue
        fit, hold = s[:-2], s[-2:]
        for r in range(1, rmax+1):
            for d in range(0, dmax+1):
                unk = (r+1)*(d+1)
                eqs = len(fit) - r
                if eqs < unk + 2: continue
                rows = []
                for i in range(r, len(fit)):
                    k = fit[i][0]
                    row = []
                    for a in range(r+1):
                        v = fit[i-a][1]
                        kk = F(fit[i-a][0])
                        for e in range(d+1):
                            row.append(v * F(k)**e)
                    rows.append(row)
                ns = nullspace(rows, unk)
                if not ns: continue
                ok = False
                for vec in ns:
                    good = True
                    for (kh, vh) in hold:
                        # predict vh from the r previous actual values
                        idx = [x[0] for x in s].index(kh)
                        lead = sum(vec[0*(d+1)+e] * F(kh)**e for e in range(d+1))
                        if lead == 0: good = False; break
                        acc = F(0)
                        for a in range(1, r+1):
                            va = s[idx-a][1]
                            c = sum(vec[a*(d+1)+e] * F(kh)**e for e in range(d+1))
                            acc += c*va
                        if -acc/lead != vh: good = False; break
                    if good: ok = True; break
                if ok:
                    hits.append((r, d, t))
                    return hits   # minimal (r,d) first
    return hits

def report(seq, name, **kw):
    n = len(seq)
    h = search(seq, name, **kw)
    env = []
    for r in range(1, 7):
        best = max([d for d in range(0, 7)
                    if (r+1)*(d+1) + 2 <= n - 2 - r] or [-1])
        if best >= 0: env.append("r=%d:d<=%d" % (r, best))
    print("  %-34s %3d pts  %-14s  envelope %s"
          % (name, n, ("FOUND (r,d,t)=%s" % (h[0],)) if h else "none",
             ", ".join(env)))

print("== controls")
report([(k, F(3)**k * F(k*k+2)) for k in range(1, 20)], "poly*3^k (must fire)")
report([(k, F(9)**k * F(1, 1) * F(2*k).__class__(1)) for k in range(1, 20)],
       "9^k (must fire)")
import math
report([(k, F(math.comb(2*k, k)) * F(9, 4)**k) for k in range(1, 20)],
       "binom(2k,k)(9/4)^k  ~ 9^k/sqrt(pi k) (must fire)")
report([(k, F(int(str(abs(hash(('x', k)))) [:9]))) for k in range(1, 20)],
       "hash noise (must NOT fire)")

print()
print("== measured defects")
for j in (1, 2, 3):
    seq = []
    for k in range(2, 20):
        n = 2*k+1-j; H = n-k
        if H < 1 or (n, H) not in tri or k not in P: continue
        D = F(tri[(n, H)]) - law(n, k, P)
        if D <= 0: continue
        seq.append((k, D))
    report(seq, "D_%d(k)" % j)

print()
print("== the ratio D_1(k) / [binom(2k,k)(9/4)^k], which -> sqrt6/27")
seq = []
for k in range(2, 20):
    if (2*k, k) not in tri or k not in P: continue
    D = F(tri[(2*k, k)]) - law(2*k, k, P)
    seq.append((k, D / (F(math.comb(2*k, k)) * F(9, 4)**k)))
print("   tail:", " ".join("%.9f" % float(v) for _, v in seq[-4:]),
      "   sqrt6/27 = %.9f" % (math.sqrt(6)/27))
report(seq, "reduced D_1")
