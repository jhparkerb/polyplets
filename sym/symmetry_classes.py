#!/usr/bin/env python3
"""Free-polyplet symmetry-class breakdown via the table of marks of D4.

Polyplets have only the coarse A030234 (bilateral) / A030235 (not) symmetry
counts; the polyomino world has the full 8-class D4 breakdown (A006746 axial,
A006748 diagonal, A006747 C2, A144553 C4, A056877 D2-ortho, A056878 D2-diag,
A142886 D4, A006749 asymmetric). This derives the polyplet analogues.

Let m_j = # free polyplets whose symmetry group is exactly conjugacy class [H_j],
S(K) = # fixed (translation-class) polyplets invariant under subgroup K. Then
S = M m with M the table of marks of D4, so m = M^{-1} S.

S for |K|<=2 is the cross-ISA-confirmed runs/sym20 data:
  S(C1)=Fixed (A006770), S(C2)=R180, S(C4)=R90, S(side-mirror)=H, S(diag-mirror)=D.
S(D2_ortho), S(D2_diag), S(D4) are computed here via sym/symcount.py (small).

Hard validation (must hold on the whole known overlap, else abort):
  sum of all classes == A030222 (free);
  sum of reflection-containing classes == (H+D)/2 == A030234 (bilateral, proven).
"""
import sys
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import symcount as sc                       # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tests"))
from common import read_bfile                # noqa: E402

MAXN = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SYMDIR = os.path.join(ROOT, "runs", "sym20")


def read_out(t):
    d = {}
    with open(os.path.join(SYMDIR, f"{t}.out")) as fh:
        for line in fh:
            p = line.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit():
                d[int(p[0])] = int(p[1])
    return d


# ---------- abstract D4 (2x2 matrices) and its table of marks ----------
def mm(P, Q):
    return tuple(tuple(sum(P[i][k] * Q[k][j] for k in range(2)) for j in range(2))
                 for i in range(2))


E = ((1, 0), (0, 1))
rot = ((0, -1), (1, 0))
r2 = mm(rot, rot)
mh = ((1, 0), (0, -1))   # reflect across x-axis (a "side" mirror)
md = ((0, 1), (1, 0))    # reflect across main diagonal
G = [E, rot, r2, mm(r2, rot), mh, ((-1, 0), (0, 1)), md, ((0, -1), (-1, 0))]


def ginv(g):
    return next(x for x in G if mm(g, x) == E)


def clo(gens):
    s = {E}
    while True:
        n = set(s)
        for a in s:
            for b in list(gens) + list(s):
                n.add(mm(a, b))
        if n == s:
            return frozenset(s)
        s = n


subs = {frozenset([E])}
for a in G:
    subs.add(clo([a]))
    for b in G:
        subs.add(clo([a, b]))
seen, reps = set(), []
for Hs in sorted(subs, key=lambda s: len(s)):
    if Hs in seen:
        continue
    cl = {frozenset(mm(mm(g, x), ginv(g)) for x in Hs) for g in G}
    seen |= cl
    reps.append(Hs)
reps.sort(key=len)
NS = len(reps)
M = [[Fraction(0)] * NS for _ in range(NS)]
for i, Hi in enumerate(reps):
    for j, Hj in enumerate(reps):
        c = sum(1 for g in G if all(mm(mm(ginv(g), x), g) in Hj for x in Hi))
        M[i][j] = Fraction(c, len(Hj))


def label(Hs):
    o = len(Hs)
    if o == 1:
        return "asymmetric"
    if o == 8:
        return "D4"
    if o == 4:
        if rot in Hs:
            return "C4"
        return "D2_ortho" if mh in Hs else "D2_diag"
    if r2 in Hs:
        return "C2"
    return "mirror_ortho" if mh in Hs else "mirror_diag"


labels = [label(h) for h in reps]


# ---------- S(K): doubly-symmetric counts via symcount placements ----------
ID = sc.ID
D2O = {  # {e, r^2, h, v} centred on cell / vertex / h-edge / v-edge
    "cell": [ID, lambda x, y: (-x, -y), lambda x, y: (x, -y), lambda x, y: (-x, y)],
    "vert": [ID, lambda x, y: (1 - x, 1 - y), lambda x, y: (x, 1 - y), lambda x, y: (1 - x, y)],
    "he":   [ID, lambda x, y: (1 - x, -y), lambda x, y: (x, -y), lambda x, y: (1 - x, y)],
    "ve":   [ID, lambda x, y: (-x, 1 - y), lambda x, y: (x, 1 - y), lambda x, y: (-x, y)],
}
D2D = {  # {e, r^2, d, d'} centred on cell / vertex
    "cell": [ID, lambda x, y: (-x, -y), lambda x, y: (y, x), lambda x, y: (-y, -x)],
    "vert": [ID, lambda x, y: (1 - x, 1 - y), lambda x, y: (y, x), lambda x, y: (1 - y, 1 - x)],
}
D4F = {  # full D4 centred on cell / vertex
    "cell": [ID, lambda x, y: (-y, x), lambda x, y: (-x, -y), lambda x, y: (y, -x),
             lambda x, y: (x, -y), lambda x, y: (-x, y), lambda x, y: (y, x), lambda x, y: (-y, -x)],
    "vert": [ID, lambda x, y: (1 - y, x), lambda x, y: (1 - x, 1 - y), lambda x, y: (y, 1 - x),
             lambda x, y: (x, 1 - y), lambda x, y: (1 - x, y), lambda x, y: (y, x), lambda x, y: (1 - y, 1 - x)],
}


def scount(placements):
    tot = {}
    for grp in placements.values():
        for n, c in sc.count_symmetric(grp, MAXN, anchor=None).items():
            tot[n] = tot.get(n, 0) + c
    return tot


def solve(Mat, b):
    n = len(b)
    A = [[Mat[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [A[r][k] - f * A[c][k] for k in range(n + 1)]
    return [A[i][n] for i in range(n)]


def main():
    fixed = read_bfile("b006770.txt")
    fixed[19] = 151609203011580          # a(19), confirmed
    R90, R180 = read_out("r90"), read_out("r180")
    Hc, Dc = read_out("hmirror"), read_out("dmirror")
    free_known = read_bfile("b030222.txt")

    free_known[18] = 2808898025438       # confirmed (sym/free_polyplets)
    free_known[19] = 18951156321090      # confirmed

    # methodology self-check: reproduce the confirmed order-<=2 counts via symcount
    # (placements are n-independent; validated at n<=12, skip the slow recompute above that)
    for name, types, ref in ([] if MAXN > 12 else [
        ("r90", sc.R90_PLACEMENTS, R90), ("r180", sc.R180_PLACEMENTS, R180),
        ("hmirror", sc.HMIRROR_PLACEMENTS, Hc), ("dmirror", sc.DMIRROR_PLACEMENTS, Dc)]):
        anc = sc._anchor_xmin0 if name == "hmirror" else (sc._anchor_diag if name == "dmirror" else None)
        got = {}
        for g in types.values():
            for n, c in sc.count_symmetric(g, MAXN, anc).items():
                got[n] = got.get(n, 0) + c
        bad = [n for n in range(1, MAXN + 1) if got.get(n, 0) != ref.get(n, 0)]
        if bad:
            print(f"METHODOLOGY MISMATCH {name} at n={bad[:5]} (got {got.get(bad[0])}, ref {ref.get(bad[0])})")
            return 1

    Sdo, Sdd, Sd4 = scount(D2O), scount(D2D), scount(D4F)
    Ssrc = {"asymmetric": fixed, "C2": R180, "C4": R90, "mirror_ortho": Hc,
            "mirror_diag": Dc, "D2_ortho": Sdo, "D2_diag": Sdd, "D4": Sd4}

    classes = {lab: {} for lab in set(labels)}
    fail = 0
    for n in range(1, MAXN + 1):
        S = [Fraction(Ssrc[labels[i]].get(n, 0)) for i in range(NS)]
        m = solve(M, S)
        for i in range(NS):
            classes[labels[i]][n] = m[i]
        tot = sum(m)
        refl = sum(m[i] for i in range(NS) if "mirror" in labels[i] or labels[i] in ("D2_ortho", "D2_diag", "D4"))
        bil = Fraction(Hc.get(n, 0) + Dc.get(n, 0), 2)
        okint = all(v.denominator == 1 and v >= 0 for v in m)
        oksum = (n not in free_known) or (tot == free_known[n])
        okbil = (refl == bil)
        if not (okint and oksum and okbil):
            fail += 1
            print(f"VALIDATION FAIL n={n}: int/nonneg={okint} sum={tot}"
                  f"{'' if oksum else ' != A030222 '+str(free_known.get(n))} "
                  f"refl={refl} bilat={bil} {'OK' if okbil else 'MISMATCH'}")

    order = ["asymmetric", "mirror_ortho", "mirror_diag", "C2", "C4",
             "D2_ortho", "D2_diag", "D4"]
    print(f"\n{'n':>3} " + " ".join(f"{k:>12}" for k in order) + f" {'sum':>14} note")
    for n in range(1, MAXN + 1):
        row = [int(classes[k][n]) for k in order]
        note = "ok vs A030222" if (n in free_known and sum(row) == free_known[n]) else \
               ("NEW" if n not in free_known else "!!!")
        print(f"{n:>3} " + " ".join(f"{v:>12}" for v in row) + f" {sum(row):>14} {note}")
    print(f"\n{'VALIDATED' if fail == 0 else str(fail)+' FAILURES'} "
          f"(classes sum to A030222 and reflections to (H+D)/2 on the overlap)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
