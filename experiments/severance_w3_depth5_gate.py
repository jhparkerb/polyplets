#!/usr/bin/env python3
"""B13: the depth-5 gate, written red-first, BEFORE D_5 exists.

severance_w3_gate.py accepts depths j <= 4 by comparing the ab-initio
D_series(j, 19) against the banked defect T(2k+1-j, k+1-j) - law at every
banked cell.  Depth 5 has the same banked surface waiting -- the 15 cells
T(2k-4, k-4), k = 5..19 -- and, until now, no gate.  This file is that gate,
written while D_5 does not yet exist, so that when the emax = 4 family table
lands it lands into a gate that predates it rather than one written to fit it.

Status at authoring (2026-08-20): **this gate cannot run green.**  D_series(5,
19) needs the excess <= 4 family table (results/severance_w3_families_K*_e4
.txt, K >= 19), which does not exist yet; the emax = 4 K-ladder producing it
is running on ayr.  That is fine and expected.  Until the table exists the
production run exits RED with a message saying exactly that -- it does NOT
fall back to the pure-Python emax = 4 DP, which is a multi-hour computation,
and a hang is not a gate.

What runs today: --selftest, which proves the comparator red-first with no
D_5 anywhere.  It extracts the empirical depth-5 series from the banked cells
themselves (T - law -- the values a correct D_5 must reproduce), confirms the
comparator passes it (a tautology by construction: this validates the
HARNESS, not depth 5), then perturbs one entry and proves the comparator
fires.  The comparator is severance_w3_gate.check_depth itself, imported, not
reimplemented -- the code proved red here is the code the future table will
face.

Usage:
  python3 experiments/severance_w3_depth5_gate.py             # RED until the
                                                              #   e4 table lands
  python3 experiments/severance_w3_depth5_gate.py --selftest  # runnable now

Exit 0 = GATE GREEN; anything else = red.
"""

import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from slope2_law_vs_truth import read_pk, read_tri, law           # noqa: E402
from severance_w3_gate import anchors, banked_defects, check_depth  # noqa: E402

J = 5
K = 19


def empirical_series(P, tri):
    """The depth-5 series the banked triangle implies: T - law at each cell.
    This is what D_series(5, 19) must equal; it is extracted, not derived,
    and exists only where cells are banked."""
    ref = banked_defects(J, P, tri)
    out = [Fr(0)] * (K + 1)
    for k, d in ref.items():
        out[k] = d
    return out, sorted(ref)


def main():
    P, tri = read_pk(), read_tri()
    anchors(P, tri)
    import severance_w3_depths as W
    if W._load_table(K, J - 1) is None:
        raise SystemExit(
            f"GATE RED: no emax={J-1} family table (results/severance_w3_"
            f"families_K*_e{J-1}.txt, K >= {K}) -- D_{J} cannot be computed "
            f"ab initio yet.  Expected from the ayr emax=4 K-ladder; the "
            f"pure-Python fallback is deliberately NOT taken (hours, and a "
            f"hang is not a gate).  This gate predates D_{J} by design and "
            f"stays red until the table lands.")
    check_depth(J, W.D_series(J, K), P, tri)
    print("GATE GREEN")


def selftest():
    P, tri = read_pk(), read_tri()
    anchors(P, tri)
    emp, ks = empirical_series(P, tri)
    assert len(ks) >= 15, f"depth {J}: only {len(ks)} banked cells -- surface gone?"
    check_depth(J, emp, P, tri)      # tautological pass: harness sanity only
    print(f"  harness: empirical depth-{J} series accepted over k = "
          f"{ks[0]}..{ks[-1]} (tautology by construction -- proves the "
          f"plumbing, not depth {J})")
    bad = list(emp)
    bad[12] += Fr(1, 3 ** 17)
    try:
        check_depth(J, bad, P, tri)
    except AssertionError:
        print("GATE SELFTEST GREEN: perturbed depth-5 series caught")
        return
    raise SystemExit("selftest: perturbation NOT caught -- gate is broken")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
