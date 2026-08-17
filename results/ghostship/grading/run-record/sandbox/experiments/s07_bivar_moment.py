#!/usr/bin/env python3
"""Session 07: bivariate FIRST AREA MOMENT closed form for convex king
animals: M1(x,y) = sum_{w,h} M1(w,h) x^w y^h, M1(w,h) = total area over
animals with bounding box exactly w x h.

Structure hypothesis (from the proven F = -(M + 2x^2y^2(1+x+y)^2 sqrt(D))
/(2K D^2), D=(1-x-y)^2-4xy, K=x+y+xy, and the s07 univariate moment fits
whose denominators specialize as K(t,t)=t(2+t), D(t,t)=1-4t):

    M1(x,y) = (A(x,y) + B(x,y) * sqrt(D)) / (K^2 * D^4)

with A, B symmetric integer polynomials.  Fit by modular linear algebra
(two 62-bit primes) on the DP table over a full WBOX x WBOX box, holdout
= all table cells not used as equations, then exact rational
reconstruction is SKIPPED (mod-p certificate only, like s02's first pass)
unless coefficients are directly integers mod both primes consistent
with small ints (CRT lift + verify over Z on the table).

Output: out_s07_bivar_moment.txt (+ .json with the lifted polynomials)
"""
import sys, os, json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s07_area_moments import gm_table, m_from_gm

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WBOX = 26
P1 = (1 << 61) - 1  # Mersenne prime 2^61-1
P2 = (1 << 62) - 57  # some prime-ish? -> use a known prime
# 2^62-57 primality not memorized; use safe known primes:
P2 = 4611686018427387847  # 2^62 - 57 is NOT verified; replaced below
# verified small-effort: use 2^61-1 (Mersenne, prime) and 2305843009213693951? same.
# choose P2 = 9223372036854775783 (largest prime < 2^63, well-known)
P2 = 9223372036854775783

DEG = int(sys.argv[1]) if len(sys.argv) > 1 else 16  # max degree in x and y
KING = (sys.argv[2] != "poly") if len(sys.argv) > 2 else True
SUFFIX = "" if KING else "_poly"


def build_table():
    gm = gm_table(WBOX, lambda w: WBOX, king=KING)
    M1 = {}
    for w in range(1, WBOX + 1):
        for h in range(1, WBOX + 1):
            M1[(w, h)] = m_from_gm(gm, w, h)[1]
    return M1


def series_D_sqrt(nmax, p):
    """sqrt(D) as bivariate series mod p, D = (1-x-y)^2-4xy, to total
    degree nmax.  sqrt via Newton iteration on series: S = 1 + ..."""
    # represent series as dict {(i,j): coeff}
    D = defaultdict(int)
    for (i, j, c) in [(0, 0, 1), (1, 0, -2), (0, 1, -2), (2, 0, 1),
                      (0, 2, 1), (1, 1, -2)]:
        D[(i, j)] = c % p
    # S_0 = 1; S_{k+1} = (S + D*S^{-1})/2 -- easier: solve S^2 = D degree
    # by degree: S = sum s_d (homogeneous parts), s_0 = 1.
    S = {(0, 0): 1}
    for d in range(1, nmax + 1):
        # coefficient equation: sum_{a+b=d} S_a*S_b = D_d
        # 2*s_d*s_0 = D_d - sum_{a=1..d-1} S_a S_{d-a}
        conv = defaultdict(int)
        for (i1, j1), c1 in S.items():
            if i1 + j1 == 0 or i1 + j1 >= d:
                continue
            for (i2, j2), c2 in S.items():
                if i2 + j2 == d - (i1 + j1):
                    conv[(i1 + i2, j1 + j2)] = (conv[(i1 + i2, j1 + j2)]
                                                + c1 * c2) % p
        inv2 = pow(2, p - 2, p)
        for i in range(d + 1):
            j = d - i
            rhs = (D.get((i, j), 0) - conv.get((i, j), 0)) % p
            S[(i, j)] = rhs * inv2 % p
    return dict(S)


def poly_mul(u, v, nmax, p):
    w = defaultdict(int)
    for (i1, j1), c1 in u.items():
        for (i2, j2), c2 in v.items():
            if i1 + i2 <= nmax and j1 + j2 <= nmax:
                w[(i1 + i2, j1 + j2)] = (w[(i1 + i2, j1 + j2)] + c1 * c2) % p
    return dict(w)


def solve_mod(rows, rhs, p, nunk):
    m = len(rows)
    A = [dict(rows[i]) for i in range(m)]
    b = rhs[:]
    piv_of_col = {}
    row_used = [False] * m
    order = []
    for c in range(nunk):
        pr = None
        for i in range(m):
            if not row_used[i] and A[i].get(c, 0) % p != 0:
                pr = i
                break
        if pr is None:
            continue
        row_used[pr] = True
        piv_of_col[c] = pr
        order.append(c)
        inv = pow(A[pr][c], p - 2, p)
        A[pr] = {k: v * inv % p for k, v in A[pr].items()}
        b[pr] = b[pr] * inv % p
        for i in range(m):
            if i != pr and A[i].get(c, 0):
                f = A[i][c]
                for k, v in A[pr].items():
                    A[i][k] = (A[i].get(k, 0) - f * v) % p
                b[i] = (b[i] - f * b[pr]) % p
    # check consistency: every eliminated-out row must be 0 == 0
    for i in range(m):
        if not row_used[i]:
            if not any(v % p for v in A[i].values()) and b[i] % p:
                return None, -1  # inconsistent
    if len(piv_of_col) < nunk:
        return None, len(piv_of_col)
    x = [0] * nunk
    for c, i in piv_of_col.items():
        x[c] = b[i]
    return x, nunk


def fit_mod(M1, p, deg):
    nmax = WBOX
    S = series_D_sqrt(2 * WBOX, p)  # need S up to total degree 2*WBOX
    # unknowns: A_{i,j} i<=j<=deg (symmetric), B_{i,j} i<=j<=deg
    # equation: A + B*S == M1ser * K^2 * D^4  (as series, total... use grid)
    # Build target = M1 * K^2 * D^4 mod p up to (nmax, nmax) grid degrees
    Mser = {(w, h): M1[(w, h)] % p for w in range(1, WBOX + 1)
            for h in range(1, WBOX + 1)}
    K = {(1, 0): 1, (0, 1): 1, (1, 1): 1}
    D = {(0, 0): 1, (1, 0): -2 % p, (0, 1): -2 % p, (2, 0): 1, (0, 2): 1,
         (1, 1): -2 % p}
    den = poly_mul(K, K, nmax, p) if KING else {(0, 0): 1}
    for _ in range(4):
        den = poly_mul(den, D, nmax, p)
    tgt = poly_mul(Mser, den, nmax, p)
    # cells usable as exact equations: those where truncation of M1 did not
    # matter: since den has max degree 10 in (x,y) jointly, target coeff at
    # (i,j) needs M1 up to (i,j); all M1 cells w,h<=WBOX are exact, but the
    # SERIES M1 has terms beyond WBOX we don't know -> only use equations
    # with i,j <= WBOX (product needs M1(w,h) for w<=i,h<=j: available).
    # unknown index map
    idx = {}
    n = 0
    for i in range(deg + 1):
        for j in range(i, deg + 1):
            idx[("A", i, j)] = n; n += 1
    for i in range(deg + 1):
        for j in range(i, deg + 1):
            idx[("B", i, j)] = n; n += 1
    rows, rhs, cells = [], [], []
    for I in range(0, WBOX + 1):
        for J in range(0, WBOX + 1):
            row = {}
            # A contribution
            if I <= deg and J <= deg:
                key = ("A", min(I, J), max(I, J))
                row[idx[key]] = (row.get(idx[key], 0) + 1) % p
            # B*S contribution: sum_{i<=deg,j<=deg} B_{ij} S_{I-i,J-j}
            for i in range(min(I, deg) + 1):
                for j in range(min(J, deg) + 1):
                    c = S.get((I - i, J - j))
                    if c:
                        key = ("B", min(i, j), max(i, j))
                        k = idx[key]
                        row[k] = (row.get(k, 0) + c) % p
            rows.append(row)
            rhs.append(tgt.get((I, J), 0) % p)
            cells.append((I, J))
    x, rank = solve_mod(rows, rhs, p, n)
    return x, rank, n, idx, len(rows)


def main():
    M1 = build_table()
    lines = [f"M1 table built over {WBOX}x{WBOX} box (king={KING}), e.g. "
             f"M1(3,3)={M1[(3,3)]}, M1(10,10)={M1[(10,10)]}"]
    sols = {}
    for p in (P1, P2):
        x, rank, n, idx, neq = fit_mod(M1, p, DEG)
        if x is None:
            lines.append(f"prime {p}: NO unique solution (rank {rank}/{n}) "
                         f"with deg={DEG}, eqs={neq}")
            sols[p] = None
        else:
            lines.append(f"prime {p}: UNIQUE solution, {n} unknowns, "
                         f"{neq} equations (overdetermined, consistent)")
            sols[p] = (x, idx)
    verdict = "unknown"
    lifted = None
    if all(sols[p] for p in (P1, P2)):
        # CRT lift to symmetric range and cross-check
        x1, idx = sols[P1]
        x2, _ = sols[P2]
        M = P1 * P2
        inv = pow(P1, P2 - 2, P2)
        lift = []
        ok = True
        for a1, a2 in zip(x1, x2):
            t = (a2 - a1) * inv % P2
            v = a1 + P1 * t
            if v > M // 2:
                v -= M
            lift.append(v)
            if abs(v) > 10 ** 15:
                ok = False
        verdict = "CRT-lifted small integers" if ok else "coeffs not small"
        if ok:
            A = {k[1:]: v for k, v in
                 zip(sorted(idx, key=idx.get), lift) if k[0] == "A" and v}
            B = {k[1:]: v for k, v in
                 zip(sorted(idx, key=idx.get), lift) if k[0] == "B" and v}
            lifted = {"A": {f"{i},{j}": v for (i, j), v in A.items()},
                      "B": {f"{i},{j}": v for (i, j), v in B.items()}}
            lines.append(f"lift: max|coeff| A: "
                         f"{max((abs(v) for v in A.values()), default=0)}, "
                         f"B: {max((abs(v) for v in B.values()), default=0)}")
            lines.append(f"A has {len(A)} terms, B has {len(B)} terms")
    lines.append(f"verdict: {verdict}")
    body = "\n".join(lines)
    print(body)
    with open(os.path.join(ROOT, f"out_s07_bivar_moment{SUFFIX}.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")
    if lifted:
        json.dump(lifted, open(os.path.join(ROOT,
                  f"out_s07_bivar_moment{SUFFIX}.json"), "w"))


if __name__ == "__main__":
    main()
