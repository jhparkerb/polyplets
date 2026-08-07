#!/usr/bin/env python3
"""Does the minimum-perimeter ladder stabilise, and is it the partition function?

Input is a build/perimeter_min census (`n p count`).  The claim under test:

  C(p, i) = A(nmax(p) - i, p), the number of animals at perimeter p and area
  deficit i, is EVENTUALLY CONSTANT in p along each residue class -- and the
  constants are a convolution of the 4-coloured partition function.

WHY THAT SHAPE.  Take king (square8), where the fat shapes are filled boxes.
An animal of perimeter exactly p lives in a box with pbox <= p.  A box with
pbox = p - 2m has maximum area smaller than nmax(p) by an amount that GROWS
with p, so for fixed i and large enough p only the boxes with pbox = p can
contribute at all -- every smaller box has been pushed past deficit i.  That is
the stabilisation mechanism, and it says what the limit is:

  * the removals from a box that leave the perimeter untouched are exactly the
    four corner staircases (removing a corner cell of a filled box drops one
    ring cell and adds the removed cell: net zero), i.e. a Young diagram at each
    of the 4 corners, so a total removal of j has [x^j] P(x)^4 ways, where
    P(x) = prod 1/(1-x^n) is the partition generating function;
  * the boxes themselves contribute their own area deficit: at semi-perimeter
    S = w+h the balanced box is optimal and a skew of s costs s^2 (S even) or
    s(s+1) (S odd), which is where the period-4 dependence on p comes from.

  So, for p large relative to i:
      p = 0 mod 4:  C = q4(i) + 2 * sum_{s>=1} q4(i - s^2)
      p = 2 mod 4:  C = 2 * sum_{s>=0} q4(i - s(s+1))
      p odd:        C = 0                (pmin is even on this lattice)

The model is asserted for square8 only.  square4's fat shapes are DIAMONDS and
its corner combinatorics is not assumed here -- the script prints its ladder and
leaves the reading to the data.

Rows are only shown where the census is complete: the enumerator is exact for
area deficit i <= RMAX and perimeter <= PMAX, both read off the file header.

    python3 experiments/perimeter_min_model.py results/perimmin_square8_p40_r6.txt --lattice square8
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import defaultdict


def isqrt_ceil(v: int) -> int:
    r = math.isqrt(v)
    return r if r * r == v else r + 1


PMIN = {
    "square4": lambda n: 2 + isqrt_ceil(8 * n - 4),      # A261491
    "square8": lambda n: 2 * isqrt_ceil(4 * n) + 4,      # A235382
}


def partitions_4colour(nmax):
    """[x^j] prod_n (1-x^n)^-4, j = 0..nmax.  Exact integer convolution."""
    q = [0] * (nmax + 1)
    q[0] = 1
    for n in range(1, nmax + 1):
        for _ in range(4):                    # four colours = four factors
            for j in range(n, nmax + 1):
                q[j] += q[j - n]
    return q


def model_king(i, q4):
    """The predicted stable value at deficit i, per residue class of p mod 4."""
    even = q4[i] + 2 * sum(q4[i - s * s] for s in range(1, i + 1) if s * s <= i)
    odd = 2 * sum(q4[i - s * (s + 1)] for s in range(0, i + 1)
                  if s * (s + 1) <= i)
    return even, odd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--lattice", required=True, choices=sorted(PMIN))
    args = ap.parse_args()

    pmax_hdr = rmax_hdr = None
    tab = defaultdict(int)
    for line in open(args.census):
        if line.startswith("#"):
            m = re.search(r"pmax=(\d+) rmax=(-?\d+)", line)
            if m:
                pmax_hdr, rmax_hdr = int(m.group(1)), int(m.group(2))
            continue
        line = line.strip()
        if not line:
            continue
        n, p, c = (int(f) for f in line.split())
        tab[(n, p)] += c
    if pmax_hdr is None:
        print("census has no perimeter_min header -- refusing to guess its "
              "completeness domain")
        return 1
    imax = rmax_hdr
    print("census %s  complete for p <= %d and deficit i <= %d"
          % (args.census, pmax_hdr, imax))

    pmin = PMIN[args.lattice]
    # nmax(p) = max{n : pmin(n) <= p}
    nmax_of = {}
    n = 1
    while pmin(n) <= pmax_hdr:
        nmax_of[pmin(n)] = n
        n += 1
    best, running = 0, {}
    for p in range(min(nmax_of), pmax_hdr + 1):
        if p in nmax_of:
            best = nmax_of[p]
        if best:
            running[p] = best

    q4 = partitions_4colour(imax + 2)
    print("4-coloured partition numbers q4(0..%d) = %s"
          % (imax, q4[:imax + 1]))
    print()

    hdr = "   p  nmax |" + "".join("%8d" % i for i in range(imax + 1))
    print("C(p, i) = A(nmax(p)-i, p)")
    print(hdr)
    print("-" * len(hdr))
    for p in sorted(running):
        nm = running[p]
        row = "%4d  %4d |" % (p, nm)
        for i in range(imax + 1):
            nn = nm - i
            row += "%8s" % (tab.get((nn, p), 0) if nn >= 1 else "-")
        print(row)
    print()

    print("Stability: the last few p in each residue class mod 4")
    for cls in range(4):
        ps = [p for p in sorted(running) if p % 4 == cls]
        if not ps:
            continue
        print("  p = %d mod 4:" % cls)
        for i in range(imax + 1):
            live = [p for p in ps if running[p] - i >= 1]
            seq = [tab.get((running[p] - i, p), 0) for p in live]
            stable = len(set(seq[-3:])) == 1 and len(seq) >= 3
            # first p from which the value never changes again
            onset = None
            if stable:
                final = seq[-1]
                onset = live[next(j for j in range(len(seq))
                                  if all(v == final for v in seq[j:]))]
            print("    i=%d  %-46s %s%s"
                  % (i, seq, "STABLE" if stable else "",
                     "  from p=%d" % onset if onset is not None else ""))
    print()

    if args.lattice == "square8":
        print("Model vs measured (last p in each class):")
        print("   i | pred p=0(4) | meas | pred p=2(4) | meas")
        p0 = [p for p in sorted(running) if p % 4 == 0]
        p2 = [p for p in sorted(running) if p % 4 == 2]
        ok = True
        for i in range(imax + 1):
            ev, od = model_king(i, q4)
            m0 = tab.get((running[p0[-1]] - i, p0[-1]), 0) if p0 else None
            m2 = tab.get((running[p2[-1]] - i, p2[-1]), 0) if p2 else None
            good = (m0 == ev) and (m2 == od)
            ok &= good
            print("   %d | %11d | %4s | %11d | %4s  %s"
                  % (i, ev, m0, od, m2, "" if good else "<-- MISMATCH"))
        print()
        print("model reproduces the top row of every class: %s" % ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
