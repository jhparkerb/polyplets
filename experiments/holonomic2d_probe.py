#!/usr/bin/env python3
"""holonomic2d_probe.py -- does T(n,H) obey a 2D P-recursive (holonomic) relation
coupling neighbours in BOTH n and H?  If yes, expensive frontier cells can be
computed from cheaper ones -- a genuine compute accelerator, not just a check.

Ansatz:  sum_{i=0..I, j=0..J, d=0..D}  c[i,j,d] * n^d * T(n-i, H-j)  =  0
for all interior cells.  We solve for the c[i,j,d] over a FIT set and require the
relation to also hold on a HELD-OUT set (cells at the largest n) -- that guards
against overfitting (a relation that only matches where it was fit is spurious).

Mod-p linear algebra (values are ~1e18; a rational relation reduces mod p, and a
genuine one holds mod two independent primes + on held-out cells).
"""
import os
from itertools import product

P1 = 2147483647      # 2^31-1
P2 = 2147483629      # another prime

def load(path, T):
    for line in open(path):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        a = s.split()
        if len(a) == 3 and all(x.lstrip('-').isdigit() for x in a):
            n, H, v = int(a[0]), int(a[1]), int(a[2])
            T[(n, H)] = v

def nullspace_modp(rows, ncols, p):
    """rows: list of length-ncols int lists. Return basis of right nullspace mod p."""
    M = [[x % p for x in r] for r in rows]
    nrows = len(M)
    pivot_col = {}
    r = 0
    for c in range(ncols):
        piv = next((rr for rr in range(r, nrows) if M[rr][c] % p), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for rr in range(nrows):
            if rr != r and M[rr][c]:
                f = M[rr][c]
                M[rr] = [(M[rr][k] - f * M[r][k]) % p for k in range(ncols)]
        pivot_col[c] = r
        r += 1
        if r == nrows:
            break
    free = [c for c in range(ncols) if c not in pivot_col]
    basis = []
    for fc in free:
        vec = [0] * ncols
        vec[fc] = 1
        for c, rr in pivot_col.items():
            vec[c] = (-M[rr][fc]) % p
        basis.append(vec)
    return basis

def build_rows(T, cells, terms, p):
    rows = []
    for (n, H) in cells:
        row = []
        for (i, j, d, e) in terms:
            row.append((pow(n, d, p) * pow(H, e, p) * (T[(n - i, H - j)] % p)) % p)
        rows.append(row)
    return rows

def term_val(vec, terms, T, n, H, p):
    return sum(vec[k] * ((pow(n, terms[k][2], p) * pow(H, terms[k][3], p)
                          * (T[(n - terms[k][0], H - terms[k][1])] % p)) % p)
               for k in range(len(terms))) % p

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    T = {}
    load(os.path.join(root, 'results/ns_a24/triangle.txt'), T)
    # a25 swept rows (H3-16 to n=25)
    p_a25 = os.path.join(root, 'results/ns_a25/swept_rows.txt')
    if os.path.exists(p_a25):
        h = None
        for line in open(p_a25):
            s = line.strip()
            if s.startswith('===H'):
                h = int(s[4:].rstrip('='))
            elif s and h is not None:
                a = s.split()
                if len(a) == 2 and all(x.lstrip('-').isdigit() for x in a):
                    T[(int(a[0]), h)] = int(a[1])
    maxn = max(n for n, _ in T)
    print(f"loaded {len(T)} cells, n up to {maxn}\n")

    print("searching  sum c[i,j,d,e] n^d H^e T(n-i,H-j) = 0  (fit n<=maxn-2, verify n>maxn-2)")
    found = []
    windows = sorted(product([1, 2, 3, 4], [1, 2, 3], [0, 1, 2, 3], [0, 1, 2]),
                     key=lambda t: ((t[0]+1)*(t[1]+1)*(t[2]+1)*(t[3]+1), t))
    for I, J, D, E in windows:
        terms = [(i, j, d, e) for i in range(I+1) for j in range(J+1)
                 for d in range(D+1) for e in range(E+1)]
        ncols = len(terms)
        def valid(n, H):
            return all((n-i, H-j) in T for i in range(I+1) for j in range(J+1))
        fit = [(n, H) for (n, H) in T if valid(n, H) and n <= maxn-2]
        hold = [(n, H) for (n, H) in T if valid(n, H) and n > maxn-2]
        if len(fit) < ncols + 8 or not hold:
            continue
        basis = nullspace_modp(build_rows(T, fit, terms, P1), ncols, P1)
        genuine = [v for v in basis
                   if all(term_val(v, terms, T, n, H, P1) == 0 for (n, H) in hold)]
        if genuine:
            found.append((I, J, D, E, len(fit), len(hold), ncols, len(genuine)))
            print(f"  (I,J,D,E)=({I},{J},{D},{E})  fit={len(fit)} hold={len(hold)} unknowns={ncols}"
                  f"  -> {len(genuine)} relation(s) verify on held-out")
            if len(found) >= 3:
                break
    if not found:
        print("  NONE up to (I,J,D,E)=(4,3,3,2). Strong evidence T(n,H) is NOT 2D-holonomic")
        print("  (no global cell-from-neighbours accelerator). The exploitable structure is")
        print("  1D-per-slice only: the diagonal closed forms we already use.")
    else:
        print("\n  ==> a verified 2D relation exists; smallest window above. Worth deriving")
        print("      exactly (over Q) and testing as a cell-from-neighbours computation.")

if __name__ == '__main__':
    main()
