#!/usr/bin/env python3
"""Session 02: explicit radical closed form for F(x,y).

F = (-A1 - S*Delta^2*sqrt(Delta)) / (2*A2), S = 2x^2y^2(1+x+y)^2  (sign TBD)

Verify WITHOUT inverting A2: check  2*A2*F + A1 = -+ S*Delta^2*sqrt(Delta)
as exact bivariate series through total degree DMAX, where F comes from the
banked table and sqrt(Delta) from Newton iteration on series.
Then examine A2's structure: A2(t,t) vs univariate P2=(2+t)(1-4t)^4;
Delta-divisibility of A2, A1.
"""
import json
from fractions import Fraction

DMAX = 30

def load(path):
    with open(path) as f:
        raw = json.load(f)
    return {int(k): {tuple(int(t) for t in key.split(',')): int(c) for key, c in d.items()}
            for k, d in raw.items()}

def load_table():
    with open('out_convex_box_38.txt') as f:
        lines = f.read().splitlines()
    idx = lines.index('f(w,h) table (rows w=1..38, cols h=1..38):')
    tab = [[0] * 39 for _ in range(39)]
    for w, line in enumerate(lines[idx + 1:idx + 39], start=1):
        for h, v in enumerate(line.split(), start=1):
            tab[w][h] = int(v)
    return tab

def series_mul(a, b, N):
    c = {}
    for (i1, j1), v1 in a.items():
        if i1 + j1 > N:
            continue
        for (i2, j2), v2 in b.items():
            if i1 + i2 + j1 + j2 <= N:
                k = (i1 + i2, j1 + j2)
                c[k] = c.get(k, 0) + v1 * v2
    return {k: v for k, v in c.items() if v}

def main():
    A = load('out_s02_bivar_eq_king_D2.json')
    A2, A1, A0 = A[2], A[1], A[0]
    tab = load_table()
    F = {}
    for i in range(1, 39):
        for j in range(1, 39):
            if i + j <= DMAX:
                F[(i, j)] = tab[i][j]

    Delta = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (0, 2): 1, (1, 1): -2}
    # sqrt(Delta) by Newton: R_{n+1} = (R + Delta/R)/2 on truncated series
    R = {(0, 0): Fraction(1)}
    for it in range(8):
        # compute Delta / R via series inversion of R
        # invert R: Rinv with R*Rinv = 1
        Rinv = {(0, 0): Fraction(1) / R[(0, 0)]}
        for d in range(1, DMAX + 1):
            for i in range(d + 1):
                j = d - i
                s = Fraction(0)
                for (p, q), v in R.items():
                    if (p, q) != (0, 0) and p <= i and q <= j:
                        s += v * Rinv.get((i - p, j - q), Fraction(0))
                Rinv[(i, j)] = -s / R[(0, 0)]
        DR = series_mul({k: Fraction(v) for k, v in Delta.items()}, Rinv, DMAX)
        Rn = {}
        for k in set(R) | set(DR):
            Rn[k] = (R.get(k, Fraction(0)) + DR.get(k, Fraction(0))) / 2
        if Rn == R:
            break
        R = Rn
    # check R^2 == Delta
    R2 = series_mul(R, R, DMAX)
    ok = all(R2.get(k, Fraction(0)) == Fraction(Delta.get(k, 0))
             for k in set(R2) | set((k, ) for k in [])) and \
         all(Fraction(v) == R2.get(k, Fraction(0)) for k, v in Delta.items() if sum(k) <= DMAX)
    print('sqrt(Delta) Newton series valid to degree', DMAX, ':', ok)
    # integer-ness check
    assert all(v.denominator == 1 for v in R.values()), 'sqrt series not integral (fine, but note)'

    # LHS = 2*A2*F + A1  (series, exact)
    LHS = series_mul(A2, F, DMAX)
    LHS = {k: 2 * v for k, v in LHS.items()}
    for k, v in A1.items():
        if sum(k) <= DMAX:
            LHS[k] = LHS.get(k, 0) + v
    LHS = {k: v for k, v in LHS.items() if v}

    # RHS = -+ S*Delta^2*sqrt(Delta)
    S = {(2, 2): 2, (2, 3): 4, (3, 2): 4, (2, 4): 2, (3, 3): 4, (4, 2): 2}
    D2 = series_mul(Delta, Delta, DMAX)
    SD2 = series_mul(S, D2, DMAX)
    RHS = series_mul(SD2, {k: int(v) for k, v in R.items()}, DMAX)

    plus = all(LHS.get(k, 0) == RHS.get(k, 0) for k in set(LHS) | set(RHS))
    minus = all(LHS.get(k, 0) == -RHS.get(k, 0) for k in set(LHS) | set(RHS))
    print('2*A2*F + A1 == +S*Delta^2*sqrt(Delta):', plus)
    print('2*A2*F + A1 == -S*Delta^2*sqrt(Delta):', minus)
    if plus or minus:
        sign = '+' if plus else '-'
        print(f'CLOSED FORM: F(x,y) = [-A1 {sign} 2x^2y^2(1+x+y)^2 Delta^2 sqrt(Delta)] / (2 A2)')

    # A2 structure
    def spec(p):
        out = {}
        for (i, j), c in p.items():
            out[i + j] = out.get(i + j, 0) + c
        return out
    def ustr(u):
        return ' '.join(f'{"+" if c > 0 else "-"}{abs(c)}t^{d}' for d, c in sorted(u.items()))
    A2t = spec(A2)
    print('A2(t,t) =', ustr(A2t))
    # divide by (1-4t)^k and (2+t)
    def udivmod(a, b):
        a = dict(a); q = {}
        bh = max(b); bc = b[bh]
        while a and max(a) >= bh:
            ah = max(a)
            if a[ah] % bc:
                return None, a
            m = ah - bh; c = a[ah] // bc
            q[m] = c
            for j, v in b.items():
                nj = j + m
                a[nj] = a.get(nj, 0) - c * v
                if a[nj] == 0:
                    del a[nj]
        return (q, a)
    cur = dict(A2t); k4 = 0
    while True:
        q, r = udivmod(cur, {0: 1, 1: -4})
        if r or q is None:
            break
        cur = q; k4 += 1
    print(f'A2(t,t) = (1-4t)^{k4} *', ustr(cur))
    q, r = udivmod(cur, {0: 2, 1: 1})
    if not r:
        print('   ... = (1-4t)^%d (2+t) *' % k4, ustr(q))

    # bivariate Delta-valuation of A2 and A1
    def pdiv(a, d):
        def lt(p):
            return max(p.keys(), key=lambda k: (k[0] + k[1], k[0]))
        q = {}; r = dict(a)
        dl = lt(d); dlc = d[dl]
        while r:
            rl = lt(r)
            if rl[0] >= dl[0] and rl[1] >= dl[1] and r[rl] % dlc == 0:
                m = (rl[0] - dl[0], rl[1] - dl[1])
                coef = r[rl] // dlc
                q[m] = q.get(m, 0) + coef
                for (p2, q2), v in d.items():
                    kk = (p2 + m[0], q2 + m[1])
                    r[kk] = r.get(kk, 0) - coef * v
                    if r[kk] == 0:
                        del r[kk]
            else:
                break
        return q, r
    for name, poly in [('A2', A2), ('A1', A1), ('A0', A0)]:
        cur = poly; v = 0
        while True:
            q, r = pdiv(cur, Delta)
            if r:
                break
            cur = q; v += 1
        print(f'Delta-valuation of {name}: {v}')

if __name__ == '__main__':
    main()
