#!/usr/bin/env python3
"""r3_l4_precurrence_probe: is Fix(h)(n) or Fix(r180)(n) P-recursive in a
small box?

Motivation (queue row L4-2, successor to LEAD-1): the answer-size floor kills
EXPLICIT quotient enumeration of the mod-4 inputs at n=40; an IMPLICIT route
would need the invariant-count sequences to satisfy some solvable structure.
The cheapest such structure to test is a P-recurrence: if one existed, the
banked n<=34 series would extend to n=40 by recurrence, delivering the mod-4
inputs with no enumeration at all. Same instrument as
results/isotropic-dfinite-boxes.md used on A006770 itself.

Method: exact rational nullspace search for sum_{i=0..r} p_i(n) a(n+i) = 0,
deg p_i <= d, over the banked terms, requiring >= 5 surplus equations; any
candidate in the nullspace is then verified on ALL banked terms. Exact
arithmetic (Fraction). Laptop seconds.
"""
from fractions import Fraction
import itertools, os

ROOT = "/Users/jasonp/src/polyominoes"

def load(key):
    seq = {}
    with open(os.path.join(ROOT, "results/sym_counts.txt")) as f:
        for line in f:
            p = line.split()
            if len(p) == 3 and p[0] == key:
                seq[int(p[1])] = int(p[2])
    return [seq[n] for n in range(1, max(seq) + 1)]

def nullspace(rows, ncols):
    """Exact RREF nullspace basis of the matrix (list of Fraction rows)."""
    m = [r[:] for r in rows]
    pivots = []
    ri = 0
    for c in range(ncols):
        piv = next((i for i in range(ri, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[ri], m[piv] = m[piv], m[ri]
        inv = m[ri][c]
        m[ri] = [x / inv for x in m[ri]]
        for i in range(len(m)):
            if i != ri and m[i][c] != 0:
                f = m[i][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[ri])]
        pivots.append(c)
        ri += 1
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        v = [Fraction(0)] * ncols
        v[fc] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -m[i][fc]
        basis.append(v)
    return basis

def check(seq, r, d, coeffs):
    """coeffs indexed [i*(d+1)+j] for p_i(n) = sum_j c_ij n^j; verify on all n."""
    ok = True
    for n in range(1, len(seq) - r + 1):
        s = Fraction(0)
        for i in range(r + 1):
            p = sum(coeffs[i * (d + 1) + j] * Fraction(n) ** j for j in range(d + 1))
            s += p * seq[n - 1 + i]
        if s != 0:
            ok = False
            break
    return ok

def probe(name, seq, surplus=5):
    N = len(seq)
    found = []
    for r in range(1, 7):
        for d in range(0, 5):
            ncols = (r + 1) * (d + 1)
            neq = N - r
            if neq < ncols + surplus:
                continue
            rows = []
            for n in range(1, neq + 1):
                row = []
                for i in range(r + 1):
                    for j in range(d + 1):
                        row.append(Fraction(n) ** j * seq[n - 1 + i])
                rows.append(row)
            basis = nullspace(rows, ncols)
            genuine = [v for v in basis if check(seq, r, d, v)]
            if genuine:
                found.append((r, d, len(genuine)))
                print(f"{name}: CANDIDATE recurrence order {r} degree {d} "
                      f"({len(genuine)} independent), verified on all {N} terms")
    if not found:
        print(f"{name}: NO P-recurrence in the box r<=6, d<=4 with >=5 "
              f"surplus equations, over {N} banked terms")

def main():
    for key in ("hmirror", "r180"):
        probe(key, load(key))

if __name__ == "__main__":
    main()
