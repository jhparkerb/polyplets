#!/usr/bin/env python3
"""Incumbent-free oracle for T(n,H) on the near-diagonal, at ANY height.

r4-gen6, round 4. Computes T(H+k, H) exactly from the Lean-verified aggregated
cluster weights of polyplets/Polyplets/Weights.lean (+ Weights3, Weights3Heavy)
and the row-decomposition recursion those files carry as checked theorems
(`d_rec_check_k1_H3`, `d_rec_check_k2_H4`).  No transfer matrix, no B1, no strip
engine, no spin engine, no fitted P_k: the value chain is
docs/proofs/diagonal-law.md (theorem) + six Lean `native_decide` integers.

Reach: k <= 3 from the Lean weights below.  Extending to k <= 5 needs the
aggregated V(l,j), Vt(l,j) for j = 4,5 summed out of KNOWN_WEIGHTS in
experiments/cluster_weight_dp.py (milliseconds; see queue row R4-G63).

Validity: H >= 4.  Below that the *pure* weights W^p (animal = one cluster, no
walk row) would be needed; they fire only when H - l == 0, i.e. H <= 3 at
l <= 3, so the guard costs nothing at the heights this exists for.

Run: python3 experiments/tristruct/r4_gen6_weight_oracle.py
"""
import os
import sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Aggregated interior / edge cluster weights: (rows l, surplus j) -> weight.
# Lean theorems: V_1_1, Vt_1_1, V_1_2, Vt_1_2, V_2_2, Vt_2_2 (Weights.lean);
# V 1 3 = 81, Vt 1 3 = 9, V 2 3 = 1860, Vt 2 3 = 307 (Weights3.lean);
# V 3 3 = 4778, Vt 3 3 = 919 (Weights3Heavy.lean).
V = {(1, 1): 25, (1, 2): 49, (2, 2): 339, (1, 3): 81, (2, 3): 1860, (3, 3): 4778}
VT = {(1, 1): 5, (1, 2): 7, (2, 2): 66, (1, 3): 9, (2, 3): 307, (3, 3): 919}
KMAX = max(j for _, j in V)


@lru_cache(None)
def d(k, H):
    """Height-H surplus-k animals whose TOP row is a walk row (one cell)."""
    if H < 0:
        return 0
    if H == 0:
        return 1 if k == 0 else 0
    if k == 0:
        return 3 ** (H - 1)
    s = 3 * d(k, H - 1)          # walk step
    for (l, j), w in V.items():  # cluster of l rows, surplus j, walk row above
        if j > k:
            continue
        i = H - 1 - l
        if i < 0:
            continue
        # i == 0: the cluster sits on the bottom edge, no walk cell below it,
        # so the interior weight is replaced by the edge weight.
        s += (w if i >= 1 else VT[(l, j)]) * d(k - j, i)
    return s


def T(k, H):
    """T(H+k, H), exact.  Requires H >= 4 (see module docstring)."""
    s = d(k, H)
    for (l, j), w in VT.items():   # optional top-edge cluster
        if j <= k and H - l >= 1:
            s += w * d(k - j, H - l)
    return s


def banked():
    t = {}
    with open(os.path.join(ROOT, "results/triangle.txt")) as f:
        for line in f:
            if line.startswith("#"):
                continue
            n, h, v = line.split()
            t[(int(n), int(h))] = int(v)
    return t


def main():
    B = banked()
    ok = bad = 0
    print("k   H    n   T(H+k,H) ab initio                       verdict")
    for k in range(KMAX + 1):
        for H in range(4, 41):
            if H + k > 40:
                continue
            o, b = T(k, H), B[(H + k, H)]
            if o == b:
                ok += 1
                v = "match"
            else:
                bad += 1
                v = "*** MISMATCH banked=%d ***" % b
            if H >= 17:
                print("%d %4d %4d   %-30d %s" % (k, H, H + k, o, v))
    print()
    print("checked %d cells, %d mismatches" % (ok + bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
