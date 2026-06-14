#!/usr/bin/env python3
"""Gate E1: the symmetric generator's R180 count vs the brute oracle.

Sum of the four R180 placements (cell / horizontal-edge / vertical-edge /
vertex centres) must equal count_symmetry's Fix(r180) at every n the oracle
reaches. This validates both the corrected generation method (Redelmeier on the
orbit graph + lift-connectivity filter) and the placement taxonomy: a missing
placement shows up as a short sum, a spurious count as an overage.
"""

import os
import sys

from common import ROOT, Gate

sys.path.insert(0, os.path.join(ROOT, "sym"))
sys.path.insert(0, os.path.join(ROOT, "oracle"))

from symcount import R180_PLACEMENTS, count_symmetry_type  # noqa: E402
from g1_naive import count_symmetry  # noqa: E402

MAXN = 9  # oracle reach (it generates all fixed animals)


def main():
    gate = Gate()
    oracle = count_symmetry("square8", MAXN)
    fix_r180 = oracle["classfix"][2]  # D4 index 2 = 180deg rotation

    gen = count_symmetry_type(R180_PLACEMENTS, MAXN)
    oracle_r180 = {n: fix_r180[n] for n in range(1, MAXN + 1)}
    bad = [n for n in range(1, MAXN + 1) if gen.get(n, 0) != fix_r180[n]]
    label = f"R180 sum vs oracle Fix(r180), n<={MAXN}"
    if bad:
        label += f"  MISMATCH at {bad}\n   gen={gen}\n   oracle={oracle_r180}"
    gate.check(not bad, label)
    return gate.verdict("E1")


if __name__ == "__main__":
    sys.exit(main())
