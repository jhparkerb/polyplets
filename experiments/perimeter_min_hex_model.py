#!/usr/bin/env python3
"""Does the king min-end model transfer to tri6, with q6 in place of q4?

King's stable minimum-perimeter columns are exactly

    C(p, i) = sum over hulls H with pbox(H) = p of q4(i - deficit(H))

where q4 = [x^j] P(x)^4 counts a Young diagram at each of the box's 4 corners and
deficit(H) = nmax(p) - |H|. Only hulls whose OWN perimeter is p contribute in the
stable regime: a hull with a smaller perimeter has a maximum area that falls
further behind nmax(p) as p grows, so it is pushed past any fixed deficit i.

tri6's hulls are hexagons and its per-hull free-removal factor is q6 = [x^j]
P(x)^6 (measured directly, and confirmed against the A071734 near-miss at j=5).
So the same formula with q6 should reproduce tri6's stable columns. That is the
test: the hull inventory and the deficits come from the enumerator, q6 from the
partition function, and NOTHING is fitted.

Feed it the `# box` lines of a `--boxes` run and the census of a real run:

    ./build/perimeter_min tri6 30 0 --boxes 2>/dev/null | grep '^# box' > hulls.txt
    python3 experiments/perimeter_min_hex_model.py hulls.txt results/perimmin_tri6_p30_r6.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict


def qc(colours, nmax):
    """[x^j] prod_n (1-x^n)^-colours, exact."""
    q = [0] * (nmax + 1)
    q[0] = 1
    for n in range(1, nmax + 1):
        for _ in range(colours):
            for j in range(n, nmax + 1):
                q[j] += q[j - n]
    return q


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("hulls", help="'# box ...' lines from --boxes")
    ap.add_argument("census", help="an n p count census from a real run")
    ap.add_argument("--colours", type=int, default=6)
    ap.add_argument("--period", type=int, default=6)
    args = ap.parse_args()

    # hull inventory: pbox -> list of (cells, multiplicity)
    byp = defaultdict(list)
    for line in open(args.hulls):
        # Only the '# box' lines.  --boxes writes the hull inventory and the
        # census into the SAME stream, and the census header carries pmax=/rmax=
        # pairs that this regex happily matches -- so parsing every line finds a
        # hull with no pbox and dies.  Filter first.
        if not line.startswith("# box"):
            continue
        d = dict(re.findall(r"(\w+)=(-?\d+)", line))
        byp[int(d["pbox"])].append((int(d["cells"]), int(d["mult"])))
    if not byp:
        sys.exit(f"no '# box' lines in {args.hulls} -- was it run with --boxes?")

    tab = defaultdict(int)
    rmax = None
    for line in open(args.census):
        if line.startswith("#"):
            m = re.search(r"rmax=(-?\d+)", line)
            if m:
                rmax = int(m.group(1))
            continue
        if not line.strip():
            continue
        n, p, c = (int(f) for f in line.split())
        tab[(n, p)] += c
    imax = rmax

    # nmax(p) = the largest hull area available at perimeter <= p
    ps = sorted(byp)
    nmax_of, best = {}, 0
    for p in range(min(ps), max(ps) + 1):
        for cells, _ in byp.get(p, []):
            best = max(best, cells)
        nmax_of[p] = best

    q = qc(args.colours, imax + 2)
    print("q%d(0..%d) = %s" % (args.colours, imax, q[:imax + 1]))
    print()
    print("Model: C(p,i) = sum over hulls with pbox = p of q%d(i - deficit)"
          % args.colours)
    print("Nothing is fitted; hull areas and multiplicities come from --boxes.")
    print()

    # Test on the LARGEST p in each residue class, where stabilisation has had
    # the most room, and only where the measured column is itself stable.
    print("   p | i | predicted | measured")
    agree = bad = 0
    for cls in range(args.period):
        cand = [p for p in ps if p % args.period == cls and p in nmax_of]
        if not cand:
            continue
        p = max(cand)
        nm = nmax_of[p]
        for i in range(imax + 1):
            pred = sum(mult * q[i - (nm - cells)]
                       for cells, mult in byp.get(p, [])
                       if 0 <= i - (nm - cells) <= imax)
            meas = tab.get((nm - i, p), 0)
            # only judge columns the census shows as settled: compare against
            # the same column one period earlier
            prev = [x for x in cand if x == p - args.period]
            settled = bool(prev) and tab.get((nmax_of[prev[0]] - i, prev[0]), 0) == meas
            if not settled:
                continue
            ok = pred == meas
            agree += ok
            bad += (not ok)
            print("  %2d | %d | %9d | %8d  %s"
                  % (p, i, pred, meas, "" if ok else "<-- MISMATCH"))
    print()
    print("settled columns tested: %d, agreeing: %d, mismatching: %d"
          % (agree + bad, agree, bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
