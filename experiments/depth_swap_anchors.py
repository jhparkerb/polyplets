#!/usr/bin/env python3
"""Depth-swapped anchors: pin mu_k below the staircase's onset.

The grand-form staircase (scripts/gen_grand_pin.py, docs/proofs/grand-form.md)

    T(H+1+k, H+1) = sum_{i=0..k} mu_i T(H+k-i, H)          (H >= k+1)

adds exactly one new constant mu_k per level, pinned from an instance at the
onset H = k+1.  Level 19's onset instance needs T(39,20) and T(40,21) and level
18's needs T(38,20) -- cells in the band no sweep reaches, which is why
docs/b1-closure-plan.md calls T(40,21) un-finessable.

This script tests, and then uses, the identity that removes that dependence.
Below onset the staircase's residual is not noise: at depth j = k+1-H it is

    R(k, H) = D_{j-1}(k) - sum_{i=0..j-1} mu_i D_{j-i}(k-i),      D_0 := 0

with D_j the below-onset defect of results/onset-defect-depths234.md, computed
by experiments/severance_w3_depths.py from bounded-excess cluster weights alone
-- no banked triangle, no wired P_k.  So mu_k can be pinned from the depth-j
instance instead, whose cells lie in columns k+1-j and k+2-j: for k = 18, 19 at
j = 2 and k = 20 at j = 3, every one of them is inside a sweep to H = 19.

Two modes:

  --identity   check R against the defect form at every instance the banked
               triangle can reach, with two RED controls that must fail.
  --rebuild    pin mu_18, mu_19, mu_20 that way and rebuild columns 20, 21, 22
               from column 19, reading NO cell above --hguard (default 19).
               The banked values are used only for the comparison at the end.

Both modes exit nonzero on any mismatch or any control that fails to fire.
"""
import argparse
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from experiments.severance_w3_depths import D_series           # noqa: E402

RESIDUAL_CELLS = [(38, 20), (39, 20), (40, 20), (39, 21), (40, 21), (40, 22)]
PIN_PLAN = ((18, 2), (19, 2), (20, 3))     # (level, depth) for the swapped pins


def read_triangle():
    d = {}
    with open(os.path.join(ROOT, "results", "triangle.txt")) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            n, H, t = line.split()
            d[(int(n), int(H))] = int(t)
    if not d:
        sys.exit("empty results/triangle.txt")
    return d


def load_defects(jmax, K):
    D = {0: [F(0)] * (K + 1)}
    for j in range(1, jmax + 1):
        D[j] = D_series(j, K)
    return D


def corr(D, mu, k, H, jmax):
    """Predicted staircase residual at (k, H); 0 at or above onset."""
    j = k + 1 - H
    if j <= 0:
        return F(0)
    if j > jmax:
        sys.exit(f"depth {j} needed at (k={k}, H={H}); only D_1..D_{jmax} loaded")
    acc = D[j - 1][k]
    for i in range(j):
        acc -= mu[i] * D[j - i][k - i]
    return acc


# --------------------------------------------------------------- identity mode
def run_identity(args):
    real = read_triangle()

    def T(n, H):
        return 3 ** (n - 1) if n == H else real.get((n, H))

    mu = {0: F(3)}
    for k in range(1, args.ktop + 1):
        a = T(2 * k + 2, k + 2)
        if a is None:
            break
        mu[k] = (F(a) - sum(mu[i] * T(2 * k + 1 - i, k + 1)
                            for i in range(k))) / F(T(k + 1, k + 1))

    D = load_defects(args.jmax, args.ktop)

    def residual(k, H):
        lhs = T(H + 1 + k, H + 1)
        if lhs is None:
            return None
        acc = F(0)
        for i in range(k + 1):
            v = T(H + k - i, H)
            if v is None:
                return None
            acc += mu[i] * v
        return F(lhs) - acc

    # the identity must hold exactly at and above onset, with zero residual
    for k in sorted(mu):
        for H in range(k + 1, 22):
            r = residual(k, H)
            if r is not None and r != 0:
                sys.exit(f"staircase FAILS above onset at (k={k}, H={H})")

    tested = agree = ctl_zero = ctl_nocorr = 0
    for j in range(1, args.jmax + 1):
        for k in range(j, args.ktop + 1):
            H = k + 1 - j
            if H < 1 or k not in mu:
                continue
            r = residual(k, H)
            if r is None:
                continue
            p = corr(D, mu, k, H, args.jmax)
            tested += 1
            agree += (r == p)
            ctl_zero += (r != 0)                     # RED: defects are not zero
            ctl_nocorr += (r != D[j - 1][k])         # RED: the mu-sum matters
            if r != p:
                print(f"  MISMATCH j={j} k={k} H={H}: measured {r} predicted {p}")
    print(f"identity instances tested: {tested}, holding: {agree}")
    print(f"RED control 'residual is zero' fires: {ctl_zero}/{tested}")
    print(f"RED control 'drop the mu-weighted sum' fires: {ctl_nocorr}/{tested}")
    if not tested or agree != tested or ctl_zero != tested or ctl_nocorr != tested:
        return 1
    return 0


# ---------------------------------------------------------------- rebuild mode
def run_rebuild(args):
    banked = read_triangle()
    reads = []

    def swept(n, H):
        """Banked cell, guarded to the heights a sweep actually reaches."""
        if H > args.hguard:
            sys.exit(f"GUARD VIOLATION: read of T({n},{H}) above H={args.hguard}")
        if n == H:
            return 3 ** (n - 1)
        v = banked.get((n, H))
        if v is None:
            sys.exit(f"missing swept cell T({n},{H})")
        reads.append((n, H))
        return v

    D = load_defects(args.jmax, args.ktop)
    mu = {0: F(3)}

    # levels whose onset instance is inside the swept band: ordinary pinning
    for k in range(1, args.hguard - 1):
        mu[k] = (F(swept(2 * k + 2, k + 2))
                 - sum(mu[i] * swept(2 * k + 1 - i, k + 1)
                       for i in range(k))) / F(swept(k + 1, k + 1))

    # the rest: pinned below onset, corrected by the ab-initio defects
    for k, j in PIN_PLAN:
        H = k + 1 - j
        mu[k] = (F(swept(H + 1 + k, H + 1))
                 - sum(mu[i] * swept(H + k - i, H) for i in range(k))
                 - corr(D, mu, k, H, args.jmax)) / F(swept(H, H))
        print(f"mu_{k} pinned at depth {j} from columns {H}, {H + 1}")

    print(f"highest banked height read: H = {max(H for _, H in reads)} "
          f"(guard {args.hguard})")

    # cross-check against the mu the ordinary banked anchors would give
    mu_ref, k = {0: F(3)}, 1
    while (2 * k + 2, k + 2) in banked:
        mu_ref[k] = (F(banked[(2 * k + 2, k + 2)])
                     - sum(mu_ref[i] * banked[(2 * k + 1 - i, k + 1)]
                           for i in range(k))) / F(3 ** k)
        k += 1
    shared = sorted(set(mu) & set(mu_ref))
    bad_mu = [k for k in shared if mu[k] != mu_ref[k]]
    print(f"mu agrees with the onset-anchor route for k = {shared}"
          + (f"  MISMATCH at {bad_mu}" if bad_mu else ""))

    # rebuild the columns above the guard, each from the one below
    col = {}

    def cell(n, H):
        if H <= args.hguard:
            return F(swept(n, H)) if n >= H else None
        return col.get((n, H))

    for H in range(args.hguard, args.hguard + 3):
        for k in range(0, args.ktop + 1):
            n = H + 1 + k
            if n > args.nmax:
                continue
            acc, ok = F(0), True
            for i in range(k + 1):
                v = cell(H + k - i, H)
                if v is None:
                    ok = False
                    break
                acc += mu[i] * v
            if ok:
                col[(n, H + 1)] = acc + corr(D, mu, k, H, args.jmax)

    print()
    allok = True
    for (n, H) in RESIDUAL_CELLS:
        got, want = col.get((n, H)), banked.get((n, H))
        if got is None or want is None or got != F(want):
            allok = False
            print(f"  T({n},{H}): {'NOT PRODUCED' if got is None else 'MISMATCH'}")
        else:
            print(f"  T({n},{H}): MATCH")
    extra = [(n, H) for (n, H) in col
             if (n, H) not in RESIDUAL_CELLS and (n, H) in banked]
    bad = [(n, H) for (n, H) in extra if col[(n, H)] != F(banked[(n, H)])]
    print(f"\nother rebuilt cells checked: {len(extra)}, mismatches: {len(bad)}")
    if bad:
        print(f"  first: {sorted(bad)[:5]}")
    return 0 if allok and not bad and not bad_mu else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--hguard", type=int, default=19,
                    help="highest banked height the rebuild may read")
    ap.add_argument("--jmax", type=int, default=3, help="deepest defect loaded")
    ap.add_argument("--ktop", type=int, default=20)
    ap.add_argument("--nmax", type=int, default=40)
    args = ap.parse_args()
    if not (args.identity or args.rebuild):
        args.identity = args.rebuild = True
    rc = 0
    if args.identity:
        rc |= run_identity(args)
        print()
    if args.rebuild:
        rc |= run_rebuild(args)
    return rc


if __name__ == "__main__":
    sys.exit(main())
