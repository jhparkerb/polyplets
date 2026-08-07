#!/usr/bin/env python3
"""Grade a site-perimeter census by defect and fit each defect class.

Input is g2's `--siteperim` table, one `n p count` row per line.  The defect is
k = pmax(n) - p with pmax(n) = 2n+2 on square4 and 4n+4 on square8 (the second
is measured, not proved -- see docs/perimeter-defect-plan.md).

For each k we look for the cheapest closed form that fits: a plain polynomial
first, then a quasi-polynomial of period 2, then 3.  A fit is only reported if
it is *overdetermined* -- every residue class must have spare points beyond the
ones consumed by the interpolation, or we have fitted noise.

    python3 experiments/perimeter_defect_fit.py results/siteperim_square4_n20.txt --lattice square4

docs/perimeter-defect-plan.md, question 1 and question 3.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from fractions import Fraction

PMAX = {
    "square4": lambda n: 2 * n + 2,
    "square8": lambda n: 4 * n + 4,
}

# Every residue class of a candidate quasi-polynomial must survive this many
# checks beyond the points its own interpolation used.  Two is the bar the
# height-grading work used (results/polyiamond-diagonal-law.md); one spare
# point is a coincidence, two is a fit.
SPARE_PER_CLASS = 2


def load(path):
    """-> {n: {p: count}}, ignoring the observability lines g2 emits."""
    table = defaultdict(dict)
    with open(path) as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 3 or not parts[0].isdigit():
                continue
            n, p, c = (int(x) for x in parts)
            table[n][p] = c
    return dict(table)


def check_pmax(table, pmax):
    """The grading is meaningless if the assumed maximum perimeter is wrong."""
    bad = [(n, max(row), pmax(n)) for n, row in sorted(table.items()) if max(row) != pmax(n)]
    return bad


def grade(table, pmax, kmax):
    """-> {k: [(n, count), ...]} sorted by n, only for n where the class is live."""
    out = {}
    for k in range(kmax + 1):
        pts = []
        for n in sorted(table):
            p = pmax(n) - k
            if p in table[n]:
                pts.append((n, table[n][p]))
            elif pts:
                # a class that has switched on cannot switch off; a hole means
                # a genuine zero, which is a legitimate data point
                pts.append((n, 0))
        out[k] = pts
    return out


def lagrange(points):
    """Exact interpolation of a degree-(len-1) polynomial; -> callable on int n."""
    xs = [Fraction(x) for x, _ in points]
    ys = [Fraction(y) for _, y in points]

    def f(n):
        n = Fraction(n)
        total = Fraction(0)
        for i, yi in enumerate(ys):
            term = yi
            for j, xj in enumerate(xs):
                if i != j:
                    term *= (n - xj) / (xs[i] - xj)
            total += term
        return total

    return f


def coeffs(points):
    """Monomial coefficients, highest degree first, via finite differences."""
    f = lagrange(points)
    d = len(points) - 1
    # solve the Vandermonde system exactly by Gaussian elimination on 0..d
    rows = []
    for x in range(d + 1):
        rows.append([Fraction(x) ** (d - j) for j in range(d + 1)] + [f(x)])
    for col in range(d + 1):
        piv = next(r for r in range(col, d + 1) if rows[r][col] != 0)
        rows[col], rows[piv] = rows[piv], rows[col]
        pv = rows[col][col]
        rows[col] = [v / pv for v in rows[col]]
        for r in range(d + 1):
            if r != col and rows[r][col] != 0:
                fac = rows[r][col]
                rows[r] = [a - fac * b for a, b in zip(rows[r], rows[col])]
    return [rows[i][-1] for i in range(d + 1)]


def fmt_poly(cs):
    d = len(cs) - 1
    parts = []
    for i, c in enumerate(cs):
        if c == 0:
            continue
        e = d - i
        mono = "" if e == 0 else ("n" if e == 1 else f"n^{e}")
        parts.append(f"{c}{'*' if mono and c != 1 else ''}{mono}" if c != 1 or not mono else mono)
    return " + ".join(parts).replace("+ -", "- ") if parts else "0"


def try_fit(points, onset, period, degree):
    """Fit from `onset` with the given period/degree; -> per-class polys or None.

    Fitting consumes the first degree+1 points of each residue class and every
    later point must then agree, with SPARE_PER_CLASS of them at minimum.
    """
    live = [(n, c) for n, c in points if n >= onset]
    classes = defaultdict(list)
    for n, c in live:
        classes[n % period].append((n, c))
    if len(classes) != period:
        return None
    fits = {}
    for r, pts in classes.items():
        if len(pts) < degree + 1 + SPARE_PER_CLASS:
            return None
        used, rest = pts[: degree + 1], pts[degree + 1 :]
        f = lagrange(used)
        if any(f(n) != c for n, c in rest):
            return None
        fits[r] = used
    return fits


def search(points, nmax_data, max_degree=6, periods=(1, 2, 3)):
    """Cheapest (period, degree, onset) that fits.  Plain polynomial preferred.

    The periods worth trying are not arbitrary.  The defect-k class lives on
    heights H >= ceil((n+k)/(k+1)) -- an exact, attained floor on the king
    lattice -- so the bottom of the height range advances in a pattern of period
    k+1 in n, and the H-marginal can only pick up cyclotomic factors Phi_d with
    d | (k+1).  Passing periods=divisors(k+1) tests that directly.
    """
    if not points:
        return None
    first_n = points[0][0]
    for period in periods:
        for degree in range(0, max_degree + 1):
            for onset in range(first_n, nmax_data + 1):
                fits = try_fit(points, onset, period, degree)
                if fits is not None:
                    return dict(period=period, degree=degree, onset=onset, fits=fits)
    return None


def describe(res, points):
    period, degree, onset = res["period"], res["degree"], res["onset"]
    lines = []
    kind = "polynomial" if period == 1 else f"quasi-polynomial (period {period})"
    holdouts = [(n, c) for n, c in points if n < onset]
    lines.append(f"  {kind}, degree {degree}, onset n >= {onset}"
                 f"  [{len(holdouts)} holdout(s): {holdouts}]")
    for r in sorted(res["fits"]):
        cs = coeffs(res["fits"][r])
        tag = "" if period == 1 else f"n = {r} mod {period}: "
        lines.append(f"    {tag}{fmt_poly(cs)}")
    if period > 1:
        lines.append("    -> genuinely n-dependent" if not _classes_agree(res)
                     else "    -> WARNING: classes coincide, period is spurious")
    return "\n".join(lines)


def _classes_agree(res):
    ref = None
    for r in sorted(res["fits"]):
        cs = coeffs(res["fits"][r])
        if ref is None:
            ref = cs
        elif cs != ref:
            return False
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("--lattice", choices=sorted(PMAX), required=True)
    ap.add_argument("--kmax", type=int, default=4)
    ap.add_argument("--max-degree", type=int, default=6)
    args = ap.parse_args(argv)

    table = load(args.table)
    if not table:
        sys.exit(f"no data rows in {args.table}")
    pmax = PMAX[args.lattice]

    bad = check_pmax(table, pmax)
    if bad:
        print(f"pmax law VIOLATED for {args.lattice} at (n, observed, expected): {bad}")
        print("the defect grading below is meaningless until that is resolved")
        return 1
    nmax = max(table)
    print(f"{args.table}: {args.lattice}, n <= {nmax}, pmax(n) = {pmax(nmax)} at n={nmax} confirmed")

    graded = grade(table, pmax, args.kmax)
    for k in range(args.kmax + 1):
        pts = graded[k]
        print(f"\nk = {k}: {[(n, c) for n, c in pts]}")
        res = search(pts, nmax, args.max_degree)
        if res is None:
            print(f"  NO FIT up to degree {args.max_degree}, period <= 3, "
                  f"with {SPARE_PER_CLASS} spare point(s) per class -- need more n")
        else:
            print(describe(res, pts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
