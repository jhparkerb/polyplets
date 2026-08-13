#!/usr/bin/env python3
"""r3_l4_algebraic_probe: is the GF of Fix(h)(n) or Fix(r180)(n) ALGEBRAIC
in a small box?

LEAD-1 remainder (queue): the P-recurrence probe excluded D-finiteness in the
box r<=6 d<=4; algebraic GFs are a subset of D-finite but an algebraic
relation P(x, F(x)) = 0 of bidegree (Dx, Dy) can correspond to an ODE far
outside that box, so it gets its own direct test.

Method: with F the series of banked terms, find nonzero P(x,y) =
sum c_ij x^i y^j, i <= Dx, j <= Dy, with P(x, F) = O(x^FIT) — a linear
nullspace problem in the c_ij over the coefficients of x^0..x^(FIT-1)
(fit region, n <= 26). Any candidate is then tested on the HOLDOUT
coefficients x^FIT..x^33 (n = 27..34): an algebraic relation fitted on the
head must annihilate the tail. Exact rational arithmetic throughout.

RED controls: Catalan (algebraic, must pass fit+holdout) and a
pseudorandom-digit series (must fail holdout even when the fit region
admits spurious solutions).
"""
from fractions import Fraction
import os, random

ROOT = "/Users/jasonp/src/polyominoes"
NTERMS = 34
FIT = 27          # coefficients x^0..x^26 (a_0 = 0 pad + n = 1..26)
SURPLUS_MIN = 2   # require fit equations >= unknowns + this to even try

def load(key):
    seq = {}
    with open(os.path.join(ROOT, "results/sym_counts.txt")) as f:
        for line in f:
            p = line.split()
            if len(p) == 3 and p[0] == key:
                seq[int(p[1])] = int(p[2])
    return [0] + [seq[n] for n in range(1, NTERMS + 1)]   # a_0 = 0

def series_pow(F, j, N):
    """F(x)^j truncated to N coefficients, exact."""
    out = [Fraction(0)] * N
    out[0] = Fraction(1)
    for _ in range(j):
        new = [Fraction(0)] * N
        for a in range(N):
            if out[a] == 0:
                continue
            for b in range(N - a):
                new[a + b] += out[a] * F[b]
        out = new
    return out

def nullspace(rows, ncols):
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

def probe(name, terms):
    N = len(terms)
    F = [Fraction(t) for t in terms]
    pows = {}
    hits = []
    for Dy in range(1, 5):
        for Dx in range(1, 9):
            ncols = (Dx + 1) * (Dy + 1)
            if FIT < ncols + SURPLUS_MIN:
                continue
            for j in range(Dy + 1):
                if j not in pows:
                    pows[j] = series_pow(F, j, N)
            # rows: coefficient of x^k in sum_ij c_ij x^i F^j, k in fit region
            def coeff_rows(ks):
                rows = []
                for k in ks:
                    row = []
                    for i in range(Dx + 1):
                        for j in range(Dy + 1):
                            row.append(pows[j][k - i] if k - i >= 0 else Fraction(0))
                    rows.append(row)
                return rows
            basis = nullspace(coeff_rows(range(FIT)), ncols)
            if not basis:
                continue
            hold = coeff_rows(range(FIT, N))
            for v in basis:
                if all(sum(a * b for a, b in zip(row, v)) == 0 for row in hold):
                    hits.append((Dx, Dy))
                    print(f"{name}: CANDIDATE algebraic relation bidegree "
                          f"(Dx={Dx}, Dy={Dy}) fits n<=26 AND holds out n=27..34")
                    break
    if not hits:
        print(f"{name}: NO algebraic relation, box Dx<=8 Dy<=4, "
              f"fit x^0..x^26, holdout x^27..x^33 (8 coefficients)")

def main():
    random.seed(20260812)
    # RED control 1 (must pass): Catalan numbers, GF algebraic (Dy=2)
    cat = [0] + [1]
    for n in range(1, NTERMS):
        cat.append(sum(cat[i + 1] * cat[n - i] for i in range(n)))
    probe("catalan(control:pass)", cat)
    # RED control 2 (must fail holdout): random digits
    rnd = [0] + [random.randint(1, 9) for _ in range(NTERMS)]
    probe("random(control:fail)", rnd)
    for key in ("hmirror", "r180"):
        probe(key, [t for t in load(key)])

if __name__ == "__main__":
    main()
