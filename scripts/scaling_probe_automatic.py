#!/usr/bin/env python3
"""Scaling probe S1 (docs/scaling-exploration-brief.md, lane C, 2026-08-11).

Is a(n) mod p (p = 2, 3) p-automatic? By Christol, a(n) mod p is p-automatic
iff F(x) = sum a(n) x^n is algebraic over F_p(x). Two tests on the 40 banked
terms (results/ns_a40/triangle.txt):

1. Algebraicity: seek nontrivial P(x,y) = sum c_ij x^i y^j with P(x,F) = 0
   mod x^40 over F_p, for degree grids with unknowns well below 40 equations.
   Nullity 0 = no low-degree algebraic relation within the data.
   (A spurious solution to a random system survives with prob ~ p^-(surplus).)
2. p-kernel lower bound: count distinct truncated subsequences
   n -> a(p^e n + r) mod p, e <= depth, compared as far as the data allows.
   A p-automatic sequence has a FINITE p-kernel; the count is a lower bound
   on the automaton size (weak with 40 terms; the algebraic test is the
   informative one).

Contrast to keep straight (results/ternary-spine.md): the triangle's
in-regime diagonal family mod 3 IS 3-automatic (spine cubic W^3 = W^2 + t,
Christol). a(n) is a row sum crossing regimes; automaticity does not follow.
Note also results/unexplored-avenues.md: BM on a(n) mod p finds order ~n/2
(no C-finite structure) -- that is the linear-recurrence test, weaker than
and different from this one.
"""
import sys

a = {}
for line in open('results/ns_a40/triangle.txt'):
    n, v = line.split()
    a[int(n)] = int(v)
N = 40
seq = [0] + [a[n] for n in range(1, N + 1)]  # seq[n] = a(n), a(0)=0


def poly_mul_trunc(A, B, p, N):
    C = [0] * (N + 1)
    for i, x in enumerate(A):
        if x:
            for j, y in enumerate(B):
                if i + j > N:
                    break
                C[i + j] = (C[i + j] + x * y) % p
    return C


def nullity(p, Dx, Dy):
    F = [s % p for s in seq]
    # powers F^0..F^Dy truncated
    pw = [[1] + [0] * N]
    for _ in range(Dy):
        pw.append(poly_mul_trunc(pw[-1], F, p, N))
    # columns: x^i * F^j -> coefficient vector (equations = coeffs x^0..x^N)
    cols = []
    for j in range(Dy + 1):
        for i in range(Dx + 1):
            v = [0] * (N + 1)
            for k in range(N + 1 - i):
                v[i + k] = pw[j][k]
            cols.append(v)
    # Gaussian elimination over F_p on the transpose: rank of column set
    m = [list(c) for c in cols]
    rank, rows = 0, N + 1
    piv = 0
    for r in range(rows):
        pivot = None
        for c in range(piv, len(m)):
            if m[c][r]:
                pivot = c
                break
        if pivot is None:
            continue
        m[piv], m[pivot] = m[pivot], m[piv]
        inv = pow(m[piv][r], p - 2, p)
        for c in range(len(m)):
            if c != piv and m[c][r]:
                f = (m[c][r] * inv) % p
                for k in range(r, rows):
                    m[c][k] = (m[c][k] - f * m[piv][k]) % p
        piv += 1
        if piv == len(m):
            break
    rank = piv
    unknowns = (Dx + 1) * (Dy + 1)
    return unknowns, N + 1, unknowns - rank


def kernel_count(p, depth):
    from itertools import product
    kers = set()
    total = 0
    for e in range(depth + 1):
        q = p ** e
        for r in range(q):
            sub = tuple(seq[q * n + r] % p for n in range(1, (N - r) // q + 1))
            if len(sub) >= 4:
                kers.add((len(sub), sub))  # truncation-aware: keep length
                total += 1
    # distinct as truncated words (conservative lower bound: two kernel
    # elements are surely distinct only if they differ on shared indices)
    reps = []
    for L, s in sorted(kers, key=lambda t: -t[0]):
        if not any(s == t[:L] for t in reps):
            reps.append(s)
    return total, len(reps)


for p in (2, 3):
    print(f'--- mod {p}')
    print('seq mod p (n=1..40):', ''.join(str(s % p) for s in seq[1:]))
    for (Dx, Dy) in [(5, 3), (4, 4), (3, 5), (7, 3), (9, 2), (6, 4), (11, 2)]:
        unk, eq, nul = nullity(p, Dx, Dy)
        surplus = eq - unk
        print(f'  deg_x<={Dx} deg_y<={Dy}: unknowns={unk} equations={eq} '
              f'surplus={surplus} nullity={nul} '
              f'{"ALGEBRAIC-CANDIDATE" if nul else "no relation"}')
    tot, distinct = kernel_count(p, 3)
    print(f'  {p}-kernel to depth 3: {tot} subsequences (len>=4), '
          f'>= {distinct} provably distinct (automaton size lower bound)')
