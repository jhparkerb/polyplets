#!/usr/bin/env python3
"""Lane B's independent recount of a(41). NOT derived from undertow_a41.py.

Route, chosen to be different where difference is possible:
  * levels k = 1..19 pinned from their two ONSET anchors T(2k+1,k+1),
    T(2k+2,k+2) in the banked triangle -- the classical rule, no wired
    diagCoeffTable, no defect series anywhere below k = 20;
  * own polynomial representation (dict), own grand-form recurrence, own
    2x2 solver, own assembly loop;
  * D_j imported from severance_w3_depths/depth1_gap_walk ONLY for k >= 20
    (unavoidable: no onset anchor exists there), and first cross-checked at
    every k <= 19 against this script's own empirical extraction
    D_j(k) = T_banked - main term;
  * swept heights read straight from results/a41/h*.out and re-verified
    against results/triangle.txt cell by cell for n <= 40.

Shared with the lead's route, unavoidably: the grand-form theorem, the
D_series code at k = 20, 21, and the level-21 pinning cells T(40,19),
T(39,18).  Everything else is disjoint.
"""
import os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

CLAIM = 393811462683918679824582849262105

# ---------- polynomials in n as {deg: Fraction} ----------
def padd(u, v):
    w = dict(u)
    for d, c in v.items():
        w[d] = w.get(d, F(0)) + c
    return {d: c for d, c in w.items() if c}

def pmul(u, v):
    w = {}
    for d1, c1 in u.items():
        for d2, c2 in v.items():
            w[d1 + d2] = w.get(d1 + d2, F(0)) + c1 * c2
    return {d: c for d, c in w.items() if c}

def pscale(u, s):
    return {d: c * s for d, c in u.items() if c * s}

def pev(u, n):
    return sum(c * F(n) ** d for d, c in u.items()) if u else F(0)

# ---------- grand form: E_k from (a_j, b_j), j <= k ----------
def gf(ab, K):
    """E[0..K], E_k = [y^k] exp(sum_j (a_j + b_j n) y^j), own recurrence."""
    E = [{0: F(1)}]
    for k in range(1, K + 1):
        acc = {}
        for j, (a, b) in ab.items():
            if j <= k:
                acc = padd(acc, pscale(pmul({0: F(a), 1: F(b)}, E[k - j]), F(j)))
        E.append(pscale(acc, F(1, k)))
    return E

def p3(e):
    return F(3) ** e

# ---------- data ----------
def read_triangle():
    tri = {}
    for line in open(os.path.join(ROOT, "results", "triangle.txt")):
        p = line.split()
        if len(p) == 3 and p[0].isdigit():
            tri[(int(p[0]), int(p[1]))] = int(p[2])
    return tri

def read_a41_rows():
    swept = {}
    for H in range(1, 20):
        for line in open(os.path.join(ROOT, "results", "a41", f"h{H}.out")):
            n, v = line.split()
            swept[(int(n), H)] = int(v)
    return swept

def read_a_known():
    out = {}
    for line in open(os.path.join(ROOT, "fixtures", "b006770.txt")):
        q = line.split()
        if len(q) == 2 and q[0].isdigit():
            out[int(q[0])] = int(q[1])
    return out

# ---------- pinning ----------
def solve2(eqs):
    """eqs: [(coef_a, coef_b, rhs)] x2 -> (a, b)."""
    (p, q, u), (r, t, v) = eqs
    det = p * t - q * r
    assert det != 0, "singular"
    return ((u * t - q * v) / det, (p * v - u * r) / det)

def pin_from_cells(k, ab, cells, tri, D):
    """cells: list of (n, defect_value).  T(n,n-k) = P_k(n)*3^(n-1-3k) + D."""
    E = gf(ab, k)
    eqs = []
    for n, d in cells:
        s = p3(n - 1 - 3 * k)
        rhs = F(tri[(n, n - k)]) - d - pev(E[k], n) * s
        eqs.append((s, s * n, rhs))
    return solve2(eqs)

def main():
    tri = read_triangle()
    swept = read_a41_rows()
    A = read_a_known()

    # 0. the swept files vs the banked triangle, every shared cell
    sh = [(n, H) for (n, H) in swept if (n, H) in tri]
    bad = [c for c in sh if swept[c] != tri[c]]
    print(f"swept a41 rows vs banked triangle: {len(sh)} shared cells, "
          f"{len(bad)} mismatch")
    assert not bad

    # 1. levels 1..19 from ONSET anchors only (no defects, no wired table)
    ab = {}
    for k in range(1, 20):
        ab[k] = pin_from_cells(k, ab, [(2 * k + 1, F(0)), (2 * k + 2, F(0))], tri, None)

    # 2. own mini-audit: every other banked in-onset cell predicted
    E = gf(ab, 19)
    ok = bad = 0
    for k in range(1, 20):
        for n in range(2 * k + 3, 41):        # anchors were 2k+1, 2k+2
            if (n, n - k) not in tri:
                continue
            v = pev(E[k], n) * p3(n - 1 - 3 * k)
            ok, bad = (ok + 1, bad) if v == tri[(n, n - k)] else (ok, bad + 1)
    print(f"anchor-pinned k<=19 predict banked in-onset cells: {ok} ok, {bad} wrong")
    assert bad == 0

    # 3. defects: empirical extraction at k <= 19 vs the imported series
    from depth1_gap_walk import walk_families, series_D1
    from severance_w3_depths import D_series
    D = {1: list(series_D1(walk_families(21), 21))}
    for j in (2, 3, 4):
        D[j] = list(D_series(j, 21))
    ok = bad = 0
    for j in (1, 2, 3, 4):
        for k in range(j, 20):
            n, H = 2 * k + 1 - j, k + 1 - j
            if H < 1 or (n, H) not in tri:
                continue
            emp = F(tri[(n, H)]) - pev(E[k], n) * p3(n - 1 - 3 * k)
            ok, bad = (ok + 1, bad) if emp == D[j][k] else (ok, bad + 1)
    print(f"imported D_j vs own empirical extraction at k<=19: {ok} ok, {bad} wrong")
    assert bad == 0

    # 4. level 20 from depths (1,2), then depths 3,4 as own holdouts
    ab[20] = pin_from_cells(20, ab, [(40, D[1][20]), (39, D[2][20])], tri, D)
    E = gf(ab, 20)
    for j, tag in ((3, "T(38,18)"), (4, "T(37,17)")):
        n = 41 - j
        v = pev(E[20], n) * p3(n - 1 - 60) + D[j][20]
        assert v == tri[(n, n - 20)], f"level-20 holdout {tag} FAILED"
    print("level 20 pinned from depths (1,2); depths 3 and 4 hold out OK")

    # 5. level 21 from depths (3,4) -- the only banked pair; no check exists
    ab[21] = pin_from_cells(21, ab, [(40, D[3][21]), (39, D[4][21])], tri, D)
    print("level 21 pinned from T(40,19)+D_3(21), T(39,18)+D_4(21) -- no third cell")

    # 6. assemble a(41): swept H<=19, tower H=20..41
    E = gf(ab, 21)
    def tower(n, H):
        k = n - H
        if k == 0:
            return F(3) ** (n - 1)
        v = pev(E[k], n) * p3(n - 1 - 3 * k)
        j = 2 * k + 1 - n
        if j > 0:
            v += D[j][k]
        return v

    total = sum(swept[(41, H)] for H in range(1, 20))
    parts = {}
    for H in range(20, 42):
        v = tower(41, H)
        assert v.denominator == 1, f"T(41,{H}) not integral"
        parts[H] = int(v)
        total += int(v)
    print(f"\nseam cells: T(41,21) = {parts[21]}  (level 20, at onset)")
    print(f"            T(41,20) = {parts[20]}  (level 21, depth 2; "
          f"D_2(21) = {D[2][21]})")
    print(f"edge: T(41,41) = 3^40: {'OK' if parts[41] == 3**40 else 'WRONG'}")
    print(f"\na(41) recount = {total}")
    print(f"lead's value  = {CLAIM}")
    print("AGREE" if total == CLAIM else "DISAGREE")

    # 7. regression: a(40) from the same pipeline, row 40 forbidden
    ab40 = {k: ab[k] for k in range(1, 20)}
    ab40[20] = pin_from_cells(20, ab40, [(39, D[2][20]), (38, D[3][20])], tri, D)
    E40 = gf(ab40, 20)
    a40 = sum(tri[(40, H)] for H in range(1, 41))   # banked row-40 sum
    t40 = sum(swept[(40, H)] for H in range(1, 20))
    for H in range(20, 41):
        k = 40 - H
        v = (F(3) ** 39 if k == 0 else pev(E40[k], 40) * p3(39 - 3 * k))
        j = 2 * k + 1 - 40
        if j > 0:
            v += D[j][k]
        assert v.denominator == 1
        t40 += int(v)
    print(f"\nregression: a(40) from a41 swept rows + row-40-free tower = "
          f"{'MATCHES banked row-40 sum' if t40 == a40 else 'WRONG: %d' % t40}")
    assert t40 == a40
    assert A[20] == sum(tri[(20, H)] for H in range(1, 21))  # fixture anchors the triangle

if __name__ == "__main__":
    main()
