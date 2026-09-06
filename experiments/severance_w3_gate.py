"""Fail-closed gate for Severance W3 (docs/onset-defect-severance-plan.md (deleted) §3).

The W3 deliverable is experiments/severance_w3_depths.py exposing

    D_series(j, K) -> list of exact Fractions [D_j(0..K)] with D_j(k) the
                      depth-j defect, computed from the extended gap-walk /
                      weight-family identity — never from the triangle.

This gate accepts depth j iff D_series(j, 19) matches the banked defect
T(2k+1−j, k+1−j) − law at EVERY banked cell k = j..19 (18 cells per depth),
where the banked side is assembled here from the triangle files and the
wired P_k — data the candidate must not consume. Depth 1 is included as a
known-good anchor (must match the closed depth-1 series).

Usage:
  python3 experiments/severance_w3_gate.py [J_MAX]     # default 4
  python3 experiments/severance_w3_gate.py --selftest  # RED control

Exit 0 = GATE GREEN; anything else = red.
"""

import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slope2_law_vs_truth import read_pk, read_tri, law          # noqa: E402
from depth1_gap_walk import walk_families, series_D1            # noqa: E402


def banked_defects(j, P, tri):
    """dict k -> exact D_j(k) from the banked triangle and wired P_k."""
    out = {}
    for k in range(j, 20):
        n, H = 2 * k + 1 - j, k + 1 - j
        if H < 1 or (n, H) not in tri:
            continue
        out[k] = Fr(tri[(n, H)]) - law(n, k, P)
    return out


def check_depth(j, series, P, tri):
    ref = banked_defects(j, P, tri)
    assert len(ref) >= 15, f"depth {j}: only {len(ref)} banked cells found — data misread?"
    for k, d in sorted(ref.items()):
        assert series[k] == d, \
            f"depth {j}: mismatch at k={k}: candidate {series[k]} != banked {d}"
    print(f"  depth {j}: {len(ref)} banked cells match exactly (k = {min(ref)}..{max(ref)})")


def anchors(P, tri):
    """The gate must itself be anchored: depth-1 closed series vs banked."""
    fams = walk_families(19)
    D1 = series_D1(fams, 19)
    check_depth(1, D1, P, tri)
    # triangle-read sanity: a couple of absolute cells
    assert tri[(2, 1)] == 1 and tri[(2, 2)] == 3 and tri[(3, 2)] == 10, \
        "triangle anchor misread"


def selftest():
    P, tri = read_pk(), read_tri()
    anchors(P, tri)
    fams = walk_families(19)
    D1 = list(series_D1(fams, 19))
    D1[7] += 1
    try:
        check_depth(1, D1, P, tri)
    except AssertionError:
        print("GATE SELFTEST GREEN: perturbed series caught")
        return
    raise SystemExit("selftest: perturbation NOT caught — gate is broken")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    jmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    P, tri = read_pk(), read_tri()
    anchors(P, tri)
    from severance_w3_depths import D_series                    # noqa: E402
    for j in range(2, jmax + 1):
        check_depth(j, D_series(j, 19), P, tri)
    print("GATE GREEN")


if __name__ == "__main__":
    main()
