#!/usr/bin/env python3
"""Session 02, v2: general algebraic fitter for the bivariate box GF.

usage: s02_bivar_fit2.py TFIT THOLD d_D,d_{D-1},...,d_0 [control]
  fits sum_{k=0..D} A_k(x,y) F^k = 0, deg_total A_k <= given list
  (list is for k=D down to k=0), on series coefficients i+j<=TFIT,
  verifies exactly on i+j<=THOLD.
"""
import sys
from fractions import Fraction
from math import gcd, lcm

P = (1 << 61) - 1

def load_banked():
    with open('out_convex_box_38.txt') as f:
        lines = f.read().splitlines()
    idx = lines.index('f(w,h) table (rows w=1..38, cols h=1..38):')
    tab = [[0] * 39 for _ in range(39)]
    for w, line in enumerate(lines[idx + 1:idx + 39], start=1):
        for h, v in enumerate(line.split(), start=1):
            tab[w][h] = int(v)
    return tab, 38

def ratrec(a, p):
    a %= p
    r0, r1 = p, a
    s0, s1 = 0, 1
    bound = int((p // 2) ** 0.5)
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if s1 == 0 or r1 > bound or abs(s1) > bound:
        return None
    return Fraction(r1, s1)

def nullspace_modp(rows, ncols, p):
    m = [r[:] for r in rows]
    nr = len(m)
    piv = []
    r = 0
    for c in range(ncols):
        pr = next((i for i in range(r, nr) if m[i][c] % p != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = pow(m[r][c], p - 2, p)
        m[r] = [(x * inv) % p for x in m[r]]
        for i in range(nr):
            if i != r and m[i][c] % p != 0:
                f = m[i][c]
                m[i] = [(a - f * b) % p for a, b in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == nr:
            break
    pivset = set(piv)
    free = [c for c in range(ncols) if c not in pivset]
    vecs = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for i, c in enumerate(piv):
            v[c] = (-m[i][fc]) % p
        vecs.append(v)
    return vecs

def mul_trunc(A, B, N):
    C = [[0] * N for _ in range(N)]
    for i1 in range(N):
        Ai = A[i1]
        for j1 in range(N - i1):
            a = Ai[j1]
            if a == 0:
                continue
            for i2 in range(N - i1 - j1 + 1):
                if i1 + i2 >= N:
                    break
                Bi = B[i2]
                row = C[i1 + i2]
                for j2 in range(N - i1 - j1 - i2 + 1):
                    b = Bi[j2]
                    if b:
                        row[j1 + j2] += a * b
    return C

def monomials(tdeg):
    return [(p, q) for p in range(tdeg + 1) for q in range(tdeg + 1 - p)]

def main():
    args = [a for a in sys.argv[1:] if a != 'control']
    control = 'control' in sys.argv[1:]
    TFIT = int(args[0]); THOLD = int(args[1])
    degs = [int(x) for x in args[2].split(',')]  # A_D ... A_0
    D = len(degs) - 1
    if control:
        sys.path.insert(0, 'experiments')
        import convex_box as cb
        W = min(THOLD, 34)
        g = cb.g_table(W, W, king=False)
        tab = cb.f_from_g(g, W, W)
        print('CONTROL polyomino table, W =', W)
    else:
        tab, W = load_banked()

    N = THOLD + 1
    F1 = [[0] * N for _ in range(N)]
    for i in range(1, min(W, N - 1) + 1):
        for j in range(1, N - i):
            if j <= W:
                F1[i][j] = tab[i][j]
    powers = [None, F1]
    for k in range(2, D + 1):
        powers.append(mul_trunc(powers[-1], F1, N))

    cols = []
    for k in range(D, -1, -1):
        for (p, q) in monomials(degs[D - k]):
            cols.append((k, p, q))
    ncols = len(cols)
    eqs = [(i, j) for i in range(N) for j in range(N - i) if i + j <= TFIT]
    print(f'D={D} degs={degs} unknowns={ncols} equations={len(eqs)} TFIT={TFIT} THOLD={THOLD}')

    rows = []
    for (i, j) in eqs:
        row = []
        for (k, p, q) in cols:
            if k == 0:
                row.append(1 if (p == i and q == j) else 0)
            elif i >= p and j >= q:
                row.append(powers[k][i - p][j - q] % P)
            else:
                row.append(0)
        rows.append(row)

    vecs = nullspace_modp(rows, ncols, P)
    print(f'nullspace dim mod p = {len(vecs)}')
    if not vecs:
        print('NONE at these degrees')
        return

    lifted_any = None
    for vi, v in enumerate(vecs):
        lifted = []
        ok = True
        for a in v:
            f = ratrec(a, P)
            if f is None:
                ok = False
                break
            lifted.append(f)
        if ok:
            lifted_any = (vi, lifted)
            break
    if lifted_any is None:
        print('rational reconstruction failed (need CRT with 2nd prime)')
        return
    vi, lifted = lifted_any
    print(f'lifted vector #{vi}')
    L = 1
    for f in lifted:
        L = lcm(L, f.denominator)
    ints = [int(f * L) for f in lifted]
    g = 0
    for x in ints:
        g = gcd(g, x)
    if g:
        ints = [x // g for x in ints]

    A = {k: {} for k in range(D + 1)}
    for (k, p, q), c in zip(cols, ints):
        if c:
            A[k][(p, q)] = c

    bad = checked = 0
    first_bad = None
    for i in range(N):
        for j in range(N - i):
            if i + j > THOLD:
                continue
            s = 0
            for k in range(D, 0, -1):
                Pk = powers[k]
                for (p, q), c in A[k].items():
                    if i >= p and j >= q:
                        s += c * Pk[i - p][j - q]
            c = A[0].get((i, j))
            if c:
                s += c
            checked += 1
            if s != 0:
                bad += 1
                if first_bad is None:
                    first_bad = (i, j)
    verdict = 'HOLDOUT PASS' if bad == 0 else f'FAIL (first at {first_bad})'
    print(f'EXACT check i+j<={THOLD}: {checked} coeffs, {bad} bad -> {verdict}')
    for k in range(D, -1, -1):
        nt = len(A[k])
        print(f'A{k}: {nt} terms', sorted(A[k].items())[:12], '...' if nt > 12 else '')
        sym = all(A[k].get((q, p)) == c for (p, q), c in A[k].items())
        print(f'   symmetric: {sym}')
    import json
    tag = 'control' if control else 'king'
    with open(f'out_s02_bivar_eq_{tag}_D{D}.json', 'w') as fo:
        json.dump({str(k): {f'{p},{q}': c for (p, q), c in A[k].items()} for k in A}, fo)
    print(f'saved out_s02_bivar_eq_{tag}_D{D}.json')

if __name__ == '__main__':
    main()
