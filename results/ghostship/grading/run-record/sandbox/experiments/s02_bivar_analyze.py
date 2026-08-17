#!/usr/bin/env python3
"""Session 02: analyze the fitted bivariate quadratic for F(x,y).

1. exact univariate specialization x=y=t checked against the 200-term
   semiperimeter series (and s01's univariate quadratic by annihilation).
2. discriminant D(x,y) = A1^2 - 4 A2 A0; conjecture: D = S^2 * Delta^odd
   with Delta = (1-x-y)^2 - 4xy. Extract the Delta-valuation and the square
   part S (via exact bivariate polynomial square root).
"""
import json
from fractions import Fraction

def load(path):
    with open(path) as f:
        raw = json.load(f)
    A = {}
    for k, d in raw.items():
        A[int(k)] = {tuple(int(t) for t in key.split(',')): int(c) for key, c in d.items()}
    return A

# ---- bivariate poly ops: dict (i,j)->int ----
def pmul(a, b):
    c = {}
    for (i1, j1), v1 in a.items():
        for (i2, j2), v2 in b.items():
            k = (i1 + i2, j1 + j2)
            c[k] = c.get(k, 0) + v1 * v2
    return {k: v for k, v in c.items() if v}

def padd(a, b, s=1):
    c = dict(a)
    for k, v in b.items():
        c[k] = c.get(k, 0) + s * v
    return {k: v for k, v in c.items() if v}

def pscale(a, s):
    return {k: v * s for k, v in a.items() if v * s}

def pdivmod_by(a, d):
    """Divide a by d (both bivariate, exact int), lex order on (total,i).
    Returns (q, r) with a = q*d + r; simple multivariate division."""
    def lt(p):
        # leading term by (total degree, i) descending
        return max(p.keys(), key=lambda k: (k[0] + k[1], k[0]))
    q = {}
    r = dict(a)
    dl = lt(d)
    dlc = d[dl]
    while r:
        rl = lt(r)
        if rl[0] >= dl[0] and rl[1] >= dl[1] and r[rl] % dlc == 0:
            m = (rl[0] - dl[0], rl[1] - dl[1])
            coef = r[rl] // dlc
            q[m] = q.get(m, 0) + coef
            r = padd(r, pmul({m: coef}, d), -1)
        else:
            break
    return q, r

def psqrt(a):
    """Exact square root of bivariate poly with integer coeffs, or None.
    Treat as poly in x with coeffs poly in y: use series-style recursion."""
    if not a:
        return {}
    # order by x-degree
    maxi = max(i for i, j in a)
    # a_i(y) coefficients
    def xcoef(p, i):
        return {j: v for (ii, j), v in p.items() if ii == i}
    # find lowest x-degree
    mini = min(i for i, j in a)
    if mini % 2:
        return None
    a0 = xcoef(a, mini)
    # sqrt of a0 (univariate in y)
    r0 = usqrt(a0)
    if r0 is None:
        return None
    half = mini // 2
    root = {(half, j): v for j, v in r0.items()}
    # iterate: root_{k}: determined by matching x^ (mini + k)
    known = pmul(root, root)
    for k in range(1, (maxi - mini) // 2 + 1):
        # coefficient of x^(mini+k) in a minus known, divided by 2*r0
        target = padd(xdict(a, mini + k), xdict(known, mini + k), -1)
        # target (poly in y) = 2 * r0 * newcoef  => newcoef = target / (2 r0)
        nc = udiv(target, uscale(r0, 2))
        if nc is None:
            return None
        add = {(half + k, j): v for j, v in nc.items()}
        if add:
            known = padd(known, padd(pmul(add, add), pscale(pmul(root, add), 2)))
            root = padd(root, add)
    return root if pmul(root, root) == a else None

def xdict(p, i):
    return {j: v for (ii, j), v in p.items() if ii == i}

def usqrt(a):
    """Square root of univariate int poly dict j->c, or None."""
    if not a:
        return {}
    lo = min(a); hi = max(a)
    if lo % 2:
        return None
    import math
    s = math.isqrt(abs(a[lo]))
    if s * s != a[lo]:
        return None
    if a[lo] < 0:
        return None
    r = {lo // 2: s}
    for k in range(1, (hi - lo) // 2 + 1):
        # coefficient of y^(lo+k) of r^2 must equal a.get(lo+k)
        acc = 0
        for j1, v1 in r.items():
            j2 = lo + k - j1
            if j2 in r and j1 < j2:
                acc += 2 * v1 * r[j2]
            elif j2 == j1:
                acc += v1 * v1
        num = a.get(lo + k, 0) - acc
        den = 2 * s
        if num % den:
            return None
        r[lo // 2 + k] = num // den
    return r if umul(r, r) == {k: v for k, v in a.items() if v} else None

def umul(a, b):
    c = {}
    for j1, v1 in a.items():
        for j2, v2 in b.items():
            c[j1 + j2] = c.get(j1 + j2, 0) + v1 * v2
    return {k: v for k, v in c.items() if v}

def uscale(a, s):
    return {k: v * s for k, v in a.items()}

def udiv(a, b):
    """Exact division of univariate int polys (dict), None if not exact."""
    if not a:
        return {}
    a = dict(a); q = {}
    bh = max(b); bc = b[bh]
    while a:
        ah = max(a)
        if ah < bh:
            return None
        if a[ah] % bc:
            return None
        m = ah - bh; c = a[ah] // bc
        q[m] = c
        for j, v in b.items():
            a[j + m] = a.get(j + m, 0) - c * v
            if a[j + m] == 0:
                del a[j + m]
    return q

def polystr(p, maxterms=200):
    ts = sorted(p.items(), key=lambda kv: (kv[0][0] + kv[0][1], kv[0][0]))
    out = []
    for (i, j), c in ts[:maxterms]:
        m = (f'x^{i}' if i else '') + (f'y^{j}' if j else '')
        out.append(f'{"+" if c > 0 else "-"}{abs(c)}{m}')
    return ' '.join(out)

def main():
    A = load('out_s02_bivar_eq_king_D2.json')
    A2, A1, A0 = A[2], A[1], A[0]

    # 1. univariate specialization vs 200-term series
    a200 = [int(x) for x in open('king_semiperim_200.txt').read().replace(',', ' ').split()]
    M = 150
    Fser = [0] * (M + 1)
    for s in range(2, M + 1):
        Fser[s] = a200[s - 2]
    def spec(p):
        out = {}
        for (i, j), c in p.items():
            out[i + j] = out.get(i + j, 0) + c
        return out
    P2, P1, P0 = spec(A2), spec(A1), spec(A0)
    # compute P2*F^2 + P1*F + P0 mod t^(M+1)
    F2ser = [0] * (M + 1)
    for i in range(2, M + 1):
        if Fser[i]:
            for j in range(2, M + 1 - i):
                F2ser[i + j] += Fser[i] * Fser[j]
    res = [0] * (M + 1)
    for d, c in P2.items():
        for k in range(0, M + 1 - d):
            res[d + k] += c * F2ser[k]
    for d, c in P1.items():
        for k in range(0, M + 1 - d):
            res[d + k] += c * Fser[k]
    for d, c in P0.items():
        if d <= M:
            res[d] += c
    print('specialization x=y=t annihilates 200-term univariate series to t^%d:' % M,
          'YES' if all(v == 0 for v in res) else 'NO first nonzero at %d' % next(i for i, v in enumerate(res) if v))

    # 2. discriminant
    disc = padd(pmul(A1, A1), pscale(pmul(A2, A0), -4))
    print('disc total degree:', max(i + j for i, j in disc), 'terms:', len(disc))
    Delta = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (0, 2): 1, (1, 1): -2}
    val = 0
    cur = disc
    while True:
        q, r = pdivmod_by(cur, Delta)
        if r:
            break
        cur = q
        val += 1
    print('Delta-valuation of disc:', val)
    print('remaining part: total degree', max(i + j for i, j in cur), 'terms', len(cur))
    # try square root of remaining (if val odd, radicand = Delta)
    S = psqrt(cur)
    if S is not None:
        print('remaining part IS a perfect square: S =', polystr(S))
        print('=> disc = Delta^%d * S^2, radicand = %s' % (val, 'Delta' if val % 2 else 'NONE (square!)'))
    else:
        print('remaining part not a perfect square as-is; trying small factors')
        for name, fac in [('x', {(1, 0): 1}), ('y', {(0, 1): 1}),
                          ('1-x', {(0, 0): 1, (1, 0): -1}), ('1-y', {(0, 0): 1, (0, 1): -1}),
                          ('1-x-y', {(0, 0): 1, (1, 0): -1, (0, 1): -1}),
                          ('x-y', {(1, 0): 1, (0, 1): -1}),
                          ('1+x+y', {(0, 0): 1, (1, 0): 1, (0, 1): 1}),
                          ('2+x+y', {(0, 0): 2, (1, 0): 1, (0, 1): 1}),
                          ('4-x-y-2xy... placeholder', None)]:
            if fac is None:
                continue
            v = 0
            c2 = cur
            while True:
                q, r = pdivmod_by(c2, fac)
                if r:
                    break
                c2 = q
                v += 1
            if v:
                print(f'  factor ({name})^{v} divides remaining part')
        # dump for manual work
        with open('out_s02_disc_squarepart.json', 'w') as f:
            json.dump({f'{i},{j}': c for (i, j), c in cur.items()}, f)
        print('dumped remaining part to out_s02_disc_squarepart.json')

    # 3. print the equation coefficients in readable form
    for k, name in [(2, 'A2'), (1, 'A1'), (0, 'A0')]:
        print(f'{name} =', polystr(A[k]))

if __name__ == '__main__':
    main()
