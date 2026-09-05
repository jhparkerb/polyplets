#!/usr/bin/env python3
"""Derive the king perimeter-defect classes from the square ones, and check it.

The maximum-end census in results/perimeter-defect-diagonals.md was measured and
interpolated.  This script checks the derivation that replaces the measurement:

  PARITY REDUCTION.  Diagonal king steps preserve the parity of x+y, so a king
  animal all of whose cells share that parity is a polyomino B in the rotated
  coordinates (u, v) = ((x+y)/2, (x-y)/2).  For such an animal

      k_king(A) = k_square(B) + c(B) + h(B)

  with c the cycle rank of B's adjacency graph and h its number of holes.  A
  king animal with no orthogonal edge is exactly a same-parity animal, so

      A_king(n, k) = sum_c P(n, k-c, c)  +  M(n, k)

  where P(n, j, c) is the square census graded by cycle rank -- the c column of
  results/perimdefect_square4_n78_k6.txt -- and M(n, k) counts the king animals
  that do carry an orthogonal edge.  That last step needs h = 0, which holds for
  k <= 3: the cheapest polyomino with a hole is 3x3 less its centre and one
  corner, with k_square = 4, c = 0, h = 1, so a hole costs k_king = 5.  Past
  k = 3 the banked square census cannot supply the correction, since it grades
  by c and not by h, and the identity is checked instead against this script's
  own enumeration.

Checks, all fail-closed (nonzero exit on the first mismatch):

  1  the reduction, cell by cell, on an independent enumeration of the animals;
  2  the feature costs (turn 1, orthogonal step 2, 3-branch 2, 4-branch 4);
  3  the orthogonal-edge bound, #orthogonal edges <= floor(k/2);
  4  the census identity above, for every n <= 78 and every k <= 3, on the
     banked censuses -- including M = 0 for k <= 1, which is the statement that
     the two lattices agree exactly there;
  5  the closed forms for A_king(n, k), k <= 4, and for the census residual
     R(n, k) = A_king(n, k) - sum_c P(n, k-c, c), k <= 5, at every n in the data
     files from their stated onsets;  R = M for k <= 3;
  6  a red control: each closed form is perturbed and must be rejected.

    python3 experiments/perimeter_defect_features.py
    python3 experiments/perimeter_defect_features.py --nmax 14
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from fractions import Fraction

KING = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
DIAG = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
ORTH = [(0, -1), (-1, 0), (1, 0), (0, 1)]

SQUARE_CENSUS = "results/perimdefect_square4_n78_k6.txt"
KING_CENSUS = "results/perimdefect_square8_n78_k6.txt"

FAILURES: list[str] = []


QUIET = False


def fail(msg: str) -> None:
    FAILURES.append(msg)
    if not QUIET:
        print("FAIL: " + msg)


# --------------------------------------------------------------------------
# geometry


def site_perimeter(cells, offsets):
    seen = set()
    for x, y in cells:
        for dx, dy in offsets:
            c = (x + dx, y + dy)
            if c not in cells:
                seen.add(c)
    return len(seen)


def defect(cells, offsets):
    """p_max(n) - p, with p_max = (deg/2)(n+1)."""
    return (len(offsets) // 2) * (len(cells) + 1) - site_perimeter(cells, offsets)


def edges(cells, offsets):
    return sum(1 for x, y in cells for dx, dy in offsets
               if (x + dx, y + dy) in cells) // 2


def holes(cells):
    """Number of finite 4-connected components of the complement."""
    xs = [p[0] for p in cells]
    ys = [p[1] for p in cells]
    lo = (min(xs) - 1, min(ys) - 1)
    hi = (max(xs) + 1, max(ys) + 1)
    outside = {lo}
    stack = [lo]
    while stack:
        x, y = stack.pop()
        for dx, dy in ORTH:
            w = (x + dx, y + dy)
            if lo[0] <= w[0] <= hi[0] and lo[1] <= w[1] <= hi[1] \
                    and w not in cells and w not in outside:
                outside.add(w)
                stack.append(w)
    rest = {(x, y)
            for x in range(lo[0], hi[0] + 1)
            for y in range(lo[1], hi[1] + 1)
            if (x, y) not in cells and (x, y) not in outside}
    n = 0
    while rest:
        stack = [rest.pop()]
        n += 1
        while stack:
            x, y = stack.pop()
            for dx, dy in ORTH:
                w = (x + dx, y + dy)
                if w in rest:
                    rest.discard(w)
                    stack.append(w)
    return n


def to_polyomino(cells):
    """(x, y) -> ((x+y)/2, (x-y)/2); valid only when x+y has one parity."""
    return frozenset(((x + y) // 2, (x - y) // 2) for x, y in cells)


def canon(cells):
    mx = min(p[0] for p in cells)
    my = min(p[1] for p in cells)
    return frozenset((p[0] - mx, p[1] - my) for p in cells)


def grow(nmax, kmax, offsets, moves):
    """All fixed animals up to n = nmax with king defect <= kmax, by growth.

    The defect never decreases when a cell is added (cpp/perimeter_defect.cpp),
    so pruning on it is exact.  `moves` restricts the growth directions --
    DIAG generates exactly the same-parity animals.
    """
    level = {frozenset([(0, 0)]): 0}
    out = {1: dict(level)}
    for size in range(2, nmax + 1):
        nxt = {}
        for A in level:
            for x, y in A:
                for dx, dy in moves:
                    c = (x + dx, y + dy)
                    if c in A:
                        continue
                    B = canon(set(A) | {c})
                    if B in nxt:
                        continue
                    k = defect(B, offsets)
                    if k <= kmax:
                        nxt[B] = k
        level = nxt
        out[size] = level
    return out


# --------------------------------------------------------------------------
# checks


def check_reduction(nmax, kmax):
    """k_king = k_square + c + h on every same-parity animal."""
    animals = grow(nmax, kmax, KING, DIAG)
    tot = 0
    for n in sorted(animals):
        for A, k in animals[n].items():
            par = {(x + y) % 2 for x, y in A}
            if len(par) != 1:
                fail("diagonal growth produced a mixed-parity animal at n=%d" % n)
                return
            B = to_polyomino(A)
            if len(B) != len(A):
                fail("the rotated map is not injective at n=%d" % n)
                return
            h = holes(B)
            c = edges(B, ORTH) - len(B) + 1
            pred = defect(B, ORTH) + c + h
            tot += 1
            if pred != k:
                fail("reduction: n=%d k=%d but k_sq+c+h=%d for %s"
                     % (n, k, pred, sorted(A)))
                return
            if h and k <= 4:
                fail("a hole at k=%d, but a hole is supposed to cost 5" % k)
                return
    print("  reduction verified on %d same-parity animals, n <= %d, k <= %d"
          % (tot, nmax, kmax))
    print("  no hole below k = 5, so h = 0 is forced for k <= 3")
    return animals


def check_features():
    """Each local feature costs what the table says."""
    d = {"NE": (1, 1), "NW": (-1, 1), "SE": (1, -1), "SW": (-1, -1),
         "N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}

    def path(steps):
        p = (0, 0)
        cells = [p]
        for s in steps:
            p = (p[0] + d[s][0], p[1] + d[s][1])
            cells.append(p)
        assert len(set(cells)) == len(cells)
        return frozenset(cells)

    L = 6
    cases = [
        ("straight diagonal segment", path(["NE"] * (2 * L)), 0),
        ("one 90-degree turn", path(["NE"] * L + ["SE"] * L), 1),
        ("two turns, opposite sense", path(["NE"] * L + ["SE"] * L + ["NE"] * L), 2),
        ("two turns, same sense", path(["NE"] * L + ["SE"] * L + ["SW"] * L), 2),
        ("three turns", path(["NE"] * L + ["SE"] * L + ["NE"] * L + ["SE"] * L), 3),
        ("one orthogonal step", path(["NE"] * L + ["E"] + ["NE"] * L), 2),
        ("orthogonal step that also turns", path(["NE"] * L + ["E"] + ["SE"] * L), 2),
    ]
    for arms, cost, name in [(("NE", "NW", "SE"), 2, "3-branch"),
                             (("NE", "NW", "SE", "SW"), 4, "4-branch")]:
        cells = {(0, 0)}
        for a in arms:
            p = (0, 0)
            for _ in range(L):
                p = (p[0] + d[a][0], p[1] + d[a][1])
                cells.add(p)
        cases.append((name, frozenset(cells), cost))
    # the smallest cycle: the 2x2 polyomino, k_sq = 2, c = 1, so k_king = 3
    cases.append(("smallest cycle (diamond)", frozenset({(0, 0), (1, 1), (1, -1), (2, 0)}), 3))
    for name, cells, want in cases:
        got = defect(cells, KING)
        if got != want:
            fail("feature cost: %s costs %d, expected %d" % (name, got, want))
    print("  %d feature costs verified" % len(cases))


def excess(cells, offsets):
    """t = sum over perimeter cells of (animal neighbours - 1)."""
    m = defaultdict(int)
    for x, y in cells:
        for dx, dy in offsets:
            c = (x + dx, y + dy)
            if c not in cells:
                m[c] += 1
    return sum(v - 1 for v in m.values())


def check_excess_identity(animals_all):
    """k = 2c + t - (deg/2 - 2)(n - 1): zero shift on square, 2(n-1) on king.

    Proposition kct of paper/L6-perimeter-gradings.tex states the square form on
    both lattices, which is false on king -- a diagonal stick has t = 2(n-1) and
    k = 0.  The enumerator only ever uses the monotonicity, so no count moves.
    """
    for n in sorted(animals_all):
        for A, k in animals_all[n].items():
            c = edges(A, KING) - n + 1
            if k != 2 * c + excess(A, KING) - 2 * (n - 1):
                fail("excess identity fails on king at n=%d k=%d" % (n, k))
                return
    stick = frozenset((i, 0) for i in range(9))
    ell = frozenset([(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)])
    for cells in (stick, ell):
        c = edges(cells, ORTH) - len(cells) + 1
        if defect(cells, ORTH) != 2 * c + excess(cells, ORTH):
            fail("excess identity fails on square")
            return
    print("  excess identity verified: k = 2c + t on square, 2c + t - 2(n-1) on king")


def check_cycle_rank_cap(king):
    """c <= floor(k/3) on the king census, against the header's floor(k/2)."""
    for (n, k, c), cnt in king.items():
        if cnt and c > k // 3:
            fail("cycle-rank cap: n=%d k=%d carries c=%d > floor(k/3)" % (n, k, c))
            return
    print("  king cycle-rank cap c <= floor(k/3) holds over the whole census")


def check_orthogonal_bound(animals_all):
    for n in sorted(animals_all):
        for A, k in animals_all[n].items():
            e = sum(1 for x, y in A for dx, dy in [(1, 0), (0, 1)]
                    if (x + dx, y + dy) in A)
            if e > k // 2:
                fail("orthogonal-edge bound: n=%d k=%d has %d orthogonal edges"
                     % (n, k, e))
                return
    print("  orthogonal-edge bound #orth <= floor(k/2) verified")


def load_census(path):
    """(n, k, c) -> count, summing the bounding-box-height column away."""
    out = defaultdict(int)
    with open(path) as fh:
        for line in fh:
            n, k, c, _h, cnt = line.split()
            out[(int(n), int(k), int(c))] += int(cnt)
    return out


def census_totals(cells):
    out = defaultdict(int)
    for (n, k, _c), v in cells.items():
        out[(n, k)] += v
    return out


def check_census_identity(sq, king, nmax_data, kmax_data):
    """A_king(n,k) - sum_c P(n,k-c,c) = M(n,k) >= 0, and M = 0 for k <= 1."""
    kt = census_totals(king)
    M = {}
    for k in range(0, kmax_data + 1):
        for n in range(1, nmax_data + 1):
            diag = sum(sq.get((n, k - c, c), 0) for c in range(0, k // 2 + 1))
            m = kt.get((n, k), 0) - diag
            M[(n, k)] = m
            if m < 0:
                fail("census identity: M(%d,%d) = %d is negative" % (n, k, m))
                return None
            if k <= 1 and m != 0:
                fail("census identity: M(%d,%d) = %d, expected 0" % (n, k, m))
                return None
    print("  census identity holds for all n <= %d, k <= %d (residual >= 0, and"
          " = 0 for k <= 1)" % (nmax_data, kmax_data))
    return M


def check_mixed_against_enumeration(animals_all, M, nmax):
    """M from the censuses equals the enumerated count of animals with an
    orthogonal edge."""
    got = defaultdict(int)
    for n in sorted(animals_all):
        for A, k in animals_all[n].items():
            if any((x + dx, y + dy) in A
                   for x, y in A for dx, dy in [(1, 0), (0, 1)]):
                got[(n, k)] += 1
    for n in range(1, nmax + 1):
        for k in range(0, 4):
            if got[(n, k)] != M.get((n, k), 0):
                fail("mixed count: n=%d k=%d enumerated %d, census gives %d"
                     % (n, k, got[(n, k)], M.get((n, k), 0)))
                return
    print("  mixed-parity counts agree with the enumeration, n <= %d, k <= 3" % nmax)


# closed forms.  Each entry: k -> (onset, period, [coefficients by residue]),
# coefficients low-order first.
def Q(*a):
    return [Fraction(x) for x in a]


KING_FORMULA = {
    0: (2, 1, [Q(2)]),
    1: (3, 1, [Q(-8, 4)]),
    2: (6, 1, [Q(56, -30, 6)]),
    3: (9, 2, [Q(-860, 360, -69, Fraction(13, 2)),
               Q(-839, Fraction(715, 2), -69, Fraction(13, 2))]),
    4: (13, 2, [Q(13798, Fraction(-33919, 6), Fraction(11995, 12),
                  Fraction(-1231, 12), Fraction(17, 3)),
                Q(Fraction(26987, 2), Fraction(-67319, 12), Fraction(2995, 3),
                  Fraction(-1231, 12), Fraction(17, 3))]),
}

RESIDUAL_FORMULA = {
    2: (3, 1, [Q(-16, 8)]),
    3: (4, 1, [Q(212, -128, 20)]),
    4: (8, 2, [Q(-3456, Fraction(5786, 3), Fraction(-811, 2), Fraction(191, 6)),
               Q(Fraction(-6937, 2), Fraction(11581, 6), Fraction(-811, 2),
                 Fraction(191, 6))]),
    5: (12, 2, [Q(69848, Fraction(-104759, 3), Fraction(44155, 6),
                  Fraction(-2368, 3), Fraction(109, 3)),
                Q(Fraction(139841, 2), Fraction(-104780, 3), Fraction(44155, 6),
                  Fraction(-2368, 3), Fraction(109, 3))]),
}


def evaluate(spec, n):
    _onset, period, coeffs = spec
    c = coeffs[n % period]
    return sum(c[j] * Fraction(n) ** j for j in range(len(c)))


def check_formulas(table, values, nmax_data, label, perturb=None):
    checked = 0
    for k, spec in sorted(table.items()):
        onset = spec[0]
        for n in range(onset, nmax_data + 1):
            want = values.get((n, k), 0)
            got = evaluate(spec, n)
            if perturb is not None and (n, k) == perturb:
                got += 1
            if got != want:
                fail("%s k=%d n=%d: formula gives %s, census gives %d"
                     % (label, k, n, got, want))
                return checked
            checked += 1
    if not QUIET:
        print("  %s: %d values matched, k in %s" % (label, checked, sorted(table)))
    return checked


def check_red_control(table, values, nmax_data, label):
    """A perturbed formula must be rejected -- otherwise the check is asleep."""
    global QUIET
    before = len(FAILURES)
    QUIET = True
    k = max(table)
    n = min(nmax_data, table[k][0] + 3)
    check_formulas(table, values, nmax_data, label + " (red control)", perturb=(n, k))
    QUIET = False
    if len(FAILURES) == before:
        fail("red control: a perturbed %s formula was accepted" % label)
        return
    del FAILURES[before:]
    print("  red control for %s rejected a perturbed formula, as it must" % label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=13,
                    help="largest n for the independent enumeration")
    ap.add_argument("--square", default=SQUARE_CENSUS)
    ap.add_argument("--king", default=KING_CENSUS)
    args = ap.parse_args()

    print("1. parity reduction, k_king = k_square + c + h")
    check_reduction(args.nmax, 6)

    print("2. feature costs")
    check_features()

    print("3. orthogonal-edge bound and the excess identity")
    animals_all = grow(args.nmax, 4, KING, KING)
    check_orthogonal_bound(animals_all)
    check_excess_identity(animals_all)

    print("4. census identity")
    sq = load_census(args.square)
    king = load_census(args.king)
    nmax_data = max(n for n, _k, _c in king)
    kmax_data = max(k for _n, k, _c in king)
    check_cycle_rank_cap(king)
    M = check_census_identity(sq, king, nmax_data, kmax_data)
    if M is None:
        return 1

    print("5. mixed counts against the enumeration")
    check_mixed_against_enumeration(animals_all, M, args.nmax)

    print("6. closed forms")
    kt = census_totals(king)
    check_formulas(KING_FORMULA, kt, nmax_data, "A_king(n,k)")
    check_formulas(RESIDUAL_FORMULA, M, nmax_data, "R(n,k)")

    print("7. red controls")
    check_red_control(KING_FORMULA, kt, nmax_data, "A_king(n,k)")
    check_red_control(RESIDUAL_FORMULA, M, nmax_data, "R(n,k)")

    if FAILURES:
        print("\n%d CHECK(S) FAILED" % len(FAILURES))
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
