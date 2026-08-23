#!/usr/bin/env python3
"""What degree is each spine family's level k, and does parity matter?

`results/dmirror-spine-split.md` states, from the S <= 11 data available when
it was written, that `d_main` has degree k-1 and `d_anti` degree k.  The
S = 12, 13, 14 rows are now measured and the k-1 reading does not survive
them: d_main's k=3 row is a single arithmetic progression across BOTH
parities, which is degree 1 where k-1 would be 2.

This measures the degree properly, with holdouts, and asks the second question
the tables raise: `d_anti` is period-2 quasi-polynomial (the anti-diagonal has
a centre cell only for odd S), but does `d_main` have any parity dependence at
all, or is one polynomial in S enough?

METHOD.  For each family and each level k, take the cells where the split is
DEFINED (S >= 2k+2) and fit the lowest degree d such that d+1 points pin a
polynomial that then reproduces every remaining point.  Done three ways: even
S alone, odd S alone, and all S pooled.  A pooled fit that survives its
holdouts is the statement that parity does not enter.

  * a level with fewer than d+2 points is reported UNPINNED, never fitted;
  * RED control: perturbing one value must break the pin it belongs to.

INPUT is the log of a `dmirror_spine_split.py` run.

Usage:
    python3 experiments/dmirror_spine_degrees.py LOGFILE

Target machine: ayr or dalby.  Cost: instant, exact rational arithmetic.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dmirror_onset_probe import newton_fit, evalpoly  # noqa: E402

ROW = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+|-)\s+(\d+)\s+(\d+)\s+(-?\d+)")


def load(path):
    """{(S, k): (main, anti)} over the rows where the split is defined."""
    out = {}
    for ln in open(path):
        m = ROW.match(ln)
        if not m:
            continue
        S, k = int(m.group(1)), int(m.group(2))
        if S < 2 * k + 2:
            continue
        out[(S, k)] = (int(m.group(5)), int(m.group(6)))
    return out


def degree(points):
    """Lowest d that pins with at least one surviving holdout.

    Returns (d, holdouts) or None if no degree is pinned by the data."""
    pts = sorted(points)
    for d in range(0, len(pts) - 1):
        poly = newton_fit(pts[:d + 1])
        hold = [(S, v) for S, v in pts[d + 1:] if evalpoly(poly, S) == v]
        if len(hold) == len(pts) - (d + 1) and hold:
            return d, len(hold)
    return None


def report(name, data, which, kmax):
    print("\n%s" % name)
    print("   %-3s %-22s %-22s %s" % ("k", "even S", "odd S", "pooled"))
    for k in range(kmax + 1):
        cells = sorted((S, v[which]) for (S, kk), v in data.items() if kk == k)
        if len(cells) < 3:
            continue
        cols = []
        for pts in ([c for c in cells if c[0] % 2 == 0],
                    [c for c in cells if c[0] % 2 == 1],
                    cells):
            r = degree(pts) if len(pts) >= 2 else None
            cols.append("unpinned (%d pts)" % len(pts) if r is None
                        else "degree %d, %d holdout(s)" % r)
        print("   %-3d %-22s %-22s %s" % (k, cols[0], cols[1], cols[2]))


def red(data):
    """Perturbing one value must break the pin that value belongs to."""
    cells = sorted((S, v[0]) for (S, k), v in data.items() if k == 2)
    good = degree(cells)
    bad = degree([(S, v + 1) if S == cells[-1][0] else (S, v) for S, v in cells])
    ok = good is not None and (bad is None or bad[0] > good[0])
    print("RED  perturbing the last k=2 d_main cell: %s -> %s   %s"
          % (good, bad, "OK" if ok else "FAILED"))
    return ok


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    data = load(sys.argv[1])
    if not data:
        print("no usable rows in %s" % sys.argv[1])
        return 1
    if not red(data):
        print("CONTROL FAILED -- nothing below is worth reading")
        return 1
    kmax = max(k for _, k in data)
    report("d_main (the main-diagonal family):", data, 0, kmax)
    report("d_anti (the anti-diagonal family):", data, 1, kmax)
    print("\nA pooled fit that survives its holdouts means parity does not "
          "enter that level.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
