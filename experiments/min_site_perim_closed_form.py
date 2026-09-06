#!/usr/bin/env python3
"""Verify A235382's closed form against Phase 4a's measured minSPKing, n=1..14.

results/subclasses.md Phase 4b: the kill criterion fired --
experiments/oeis_lookup.py hit A235382, which already carries the closed form
a(n) = A027709(n) + 4 = 2*ceiling(2*sqrt(n)) + 4. So this is a verification,
not a derivation: nothing here re-proves A235382.

INTEGER-EXACT ON PURPOSE. math.sqrt(n) at a perfect square can land a hair
under the true root, in which case math.ceil rounds to the wrong integer and
n=4 and n=9 -- the two perfect squares in range, and the two n where the
formula is at a step boundary -- silently disagree. So ceiling(2*sqrt(n)) is
computed with integers only:

    ceil(2*sqrt(n)) = least m >= 0 with m >= 2*sqrt(n)
                    = least m >= 0 with m^2 >= 4n            (both sides >= 0)

and that m comes straight from math.isqrt (exact integer floor-sqrt): take
r = isqrt(4n), then m = r if r*r == 4n else r+1. No float ever enters.

Usage: python3 experiments/min_site_perim_closed_form.py
Exit 0 if every n matches, 1 (and a printed diff) if any n does not.
"""
import math
import sys

# results/perimeter.md, "The sequence, n = 1..14", minSPKing column.
# MEASURED -- build/directed_cone_anchor grid 14 8. Never edit to fit a guess.
MEASURED = [8, 10, 12, 12, 14, 14, 16, 16, 16, 18, 18, 18, 20, 20]


def ceil_2sqrt(n):
    """ceiling(2*sqrt(n)), integer-exactly -- no float, no rounding hazard."""
    r = math.isqrt(4 * n)
    return r if r * r == 4 * n else r + 1


def closed_form(n):
    """A235382: a(n) = 2*ceiling(2*sqrt(n)) + 4."""
    return 2 * ceil_2sqrt(n) + 4


def main():
    bad = []
    print("  n | 2*ceil(2*sqrt(n))+4 | minSPKing (measured) | match")
    print("----+---------------------+----------------------+------")
    for n, meas in enumerate(MEASURED, start=1):
        pred = closed_form(n)
        ok = pred == meas
        if not ok:
            bad.append((n, pred, meas))
        print("%3d | %19d | %20d | %s" % (n, pred, meas, "yes" if ok else "NO"))
    print()
    if bad:
        print("MISMATCH at n = %s -- Phase 4b stops and reports."
              % ", ".join(str(n) for n, _, _ in bad))
        return 1
    print("All %d terms match exactly (integer arithmetic only)." % len(MEASURED))

    # The float trap this script exists to dodge, shown rather than asserted.
    naive = [2 * math.ceil(2 * math.sqrt(n)) + 4
             for n in range(1, len(MEASURED) + 1)]
    if naive == [closed_form(n) for n in range(1, len(MEASURED) + 1)]:
        print("(Float ceil happens to agree on this platform at n<=14; the "
              "integer path is used regardless, since that agreement is not "
              "guaranteed.)")
    else:
        print("(Float ceil DISAGREES with the integer path on this platform: "
              "%s -- exactly the trap avoided.)" % naive)
    return 0


if __name__ == "__main__":
    sys.exit(main())
