#!/usr/bin/env python3
"""Session 02: fit an algebraic equation for the bivariate box GF
F(x,y) = sum_{w,h>=1} f(w,h) x^w y^h  of convex king animals.

Ansatz: A2(x,y) F^2 + A1(x,y) F + A0(x,y) = 0 with total-degree bounds
(t2,t1,t0) mirroring the univariate specialization degrees (5,8,11).

Method: linear system on series coefficients (i+j <= TFIT), solved modulo a
63-bit prime; nullspace vector lifted by rational reconstruction; then the
candidate is verified EXACTLY (bigint arithmetic) on all coefficients with
i+j <= THOLD > TFIT -- a deep exact holdout, s01 methodology.

Also checks the x=y=t specialization against s01's univariate quadratic and
extracts the discriminant A1^2 - 4 A2 A0 for factoring (conjecture: radicand
Delta = (1-x-y)^2 - 4xy, which specializes to 1-4t).
"""
from fractions import Fraction
import sys

P = (1 << 61) - 1  # Mersenne prime

def load_banked():
    with open('out_convex_box_38.txt') as f:
        lines = f.read().splitlines()
    idx = lines.index('f(w,h) table (rows w=1..38, cols h=1..38):')
    tab = [[0] * 39 for _ in range(39)]
    for w, line in enumerate(lines[idx + 1:idx + 39], start=1):
        for h, v in enumerate(line.split(), start=1):
            tab[w][h] = int(v)
    return tab

def ratrec(a, p):
    """Rational reconstruction of a mod p (|num|,|den| < sqrt(p/2))."""
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
    """All-free-variable count + one nullspace vector mod p (last free var),
    plus the full reduced matrix for extracting minimal solutions."""
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

def monomials(tdeg):
    return [(p, q) for p in range(tdeg + 1) for q in range(tdeg + 1 - p)]

def main():
    args = [a for a in sys.argv[1:] if a != 'control']
    control = 'control' in sys.argv[1:]
    TFIT = int(args[0]) if len(args) > 0 else 22
    THOLD = int(args[1]) if len(args) > 1 else 32
    t2, t1, t0 = (int(x) for x in (args[2:5] or [6, 9, 12]))
    if control:
        sys.path.insert(0, 'experiments')
        import convex_box as cb
        W = THOLD
        g = cb.g_table(W, W, king=False)
        tab = cb.f_from_g(g, W, W)
        print('CONTROL: convex POLYOMINO box table (king=False), W =', W)
    else:
        tab = load_banked()
        W = 38

    # F coefficients: F[i][j] = f(i,j) for i,j>=1 else 0
    N = THOLD + 1
    F1 = [[0] * N for _ in range(N)]
    for i in range(1, min(W, N - 1) + 1):
        for j in range(1, N - 1):
            if i + j <= THOLD and j <= W:
                F1[i][j] = tab[i][j]
    # F^2 up to total degree THOLD
    F2 = [[0] * N for _ in range(N)]
    for i1 in range(1, N):
        for j1 in range(1, N - i1):
            if F1[i1][j1] == 0:
                continue
            for i2 in range(1, N - i1 - j1 + 1):
                for j2 in range(1, N - i1 - j1 - i2 + 1):
                    v = F1[i2][j2]
                    if v:
                        F2[i1 + i2][j1 + j2] += F1[i1][j1] * v
    powers = {0: None, 1: F1, 2: F2}

    mon = {2: monomials(t2), 1: monomials(t1), 0: monomials(t0)}
    cols = [(d, p, q) for d in (2, 1, 0) for (p, q) in mon[d]]
    ncols = len(cols)
    eqs = [(i, j) for i in range(N) for j in range(N - i) if i + j <= TFIT]
    print(f'unknowns={ncols} equations={len(eqs)} (TFIT={TFIT}, THOLD={THOLD}, degs={t2},{t1},{t0})')

    rows = []
    for (i, j) in eqs:
        row = []
        for (d, p, q) in cols:
            if d == 0:
                row.append(1 if (p == i and q == j) else 0)
            else:
                Fd = powers[d]
                row.append(Fd[i - p][j - q] % P if (i >= p and j >= q) else 0)
        rows.append(row)

    vecs = nullspace_modp(rows, ncols, P)
    print(f'nullspace dim mod p = {len(vecs)}')
    if not vecs:
        print('NONE at these degrees')
        return

    # lift the first vector; try others if lift fails
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
            print(f'lifted nullspace vector #{vi}')
            break
    if not ok:
        print('rational reconstruction failed on all vectors')
        return
    # clear denominators
    from math import gcd, lcm
    L = 1
    for f in lifted:
        L = lcm(L, f.denominator)
    ints = [int(f * L) for f in lifted]
    g = 0
    for x in ints:
        g = gcd(g, x)
    if g:
        ints = [x // g for x in ints]

    A = {2: {}, 1: {}, 0: {}}
    for (d, p, q), c in zip(cols, ints):
        if c:
            A[d][(p, q)] = c

    # EXACT holdout verification on 2 <= i+j <= THOLD
    bad = 0
    checked = 0
    for i in range(N):
        for j in range(N - i):
            if not (i + j <= THOLD):
                continue
            s = 0
            for d in (2, 1, 0):
                for (p, q), c in A[d].items():
                    if i >= p and j >= q:
                        s += c * (1 if d == 0 and (i - p, j - q) != (0, 0) else 0) if False else 0
            # recompute cleanly
            s = 0
            for (p, q), c in A[2].items():
                if i >= p and j >= q:
                    s += c * F2[i - p][j - q]
            for (p, q), c in A[1].items():
                if i >= p and j >= q:
                    s += c * F1[i - p][j - q]
            c = A[0].get((i, j))
            if c:
                s += c
            checked += 1
            if s != 0:
                bad += 1
    print(f'EXACT check on i+j<={THOLD}: {checked} coefficients, {bad} nonzero residues '
          f'({"ALL ZERO - HOLDOUT PASS" if bad == 0 else "FAIL"})')
    print(f'holdout margin: fitted on i+j<={TFIT}, verified through i+j<={THOLD}')

    def polystr(d):
        terms = sorted(A[d].items())
        return ' + '.join(f'{c}*x^{p}*y^{q}' for (p, q), c in terms)
    print('A2 =', polystr(2))
    print('A1 =', polystr(1))
    print('A0 =', polystr(0))

    # symmetry check A_d(x,y) == A_d(y,x)?
    for d in (2, 1, 0):
        sym = all(A[d].get((q, p)) == c for (p, q), c in A[d].items())
        print(f'A{d} symmetric under x<->y: {sym}')

    # specialize x=y=t, compare with s01 univariate (up to common factor)
    def spec(d, maxdeg):
        out = [0] * (maxdeg + 1)
        for (p, q), c in A[d].items():
            if p + q <= maxdeg:
                out[p + q] += c
        return out
    print('A2(t,t) =', spec(2, t2))
    print('A1(t,t) =', spec(1, t1))
    print('A0(t,t) =', spec(0, t0))

    import json
    with open('out_s02_bivar_eq.json', 'w') as f:
        json.dump({str(d): {f'{p},{q}': c for (p, q), c in A[d].items()} for d in A}, f)
    print('equation saved to out_s02_bivar_eq.json')

if __name__ == '__main__':
    main()
