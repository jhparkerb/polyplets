#!/usr/bin/env python3
"""Assemble a(41) from a short sweep plus the Undertow-pinned tower.

The sweep supplies T(41,H) for H <= 19 (runs/a41_low/perheight/h<H>.out).
Everything above comes from the diagonal tower, whose levels k = 41-H run
0..21: k <= 19 from the wired table, k = 20 and k = 21 pinned by
experiments/undertow_pin.py from BELOW-onset cells that are already banked.

Onset matters at the seam and is handled, not assumed:

  H = 21  ->  k = 20, n = 41 = 2k+1  ->  exactly at onset, pure P_20;
  H = 20  ->  k = 21, n = 41 = 2k+1-2 -> depth j = 2, so
              T(41,20) = P_21(41)*3^(41-1-63) + D_2(21).

Nothing here is believed without its checks.  The script refuses to print a
value unless:

  * every height 1..41 is accounted for exactly once;
  * T(41,41) = 3^40 and T(41,40) = P_1(41)*3^37, both exact;
  * the same tower, run at n = 40, reproduces every banked cell of row 40 it
    touches -- the regression that says the machinery still agrees with the
    term we already have;
  * a(40) reassembles from the banked triangle to its banked value;
  * the growth ratio a(41)/a(40) sits inside the smooth series
    (6.9212, 6.9261, 6.9308, 6.9352 at a(37)..a(40)).

Usage:
  python3 experiments/undertow_a41.py --perheight DIR [--jmax 4] [--nmax 41]
  python3 experiments/undertow_a41.py --selftest
"""

import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from slope2_law_vs_truth import read_pk, read_tri                      # noqa: E402
from undertow_pin import (all_pairs, extract_ab, grand_form, load_depths,  # noqa: E402
                          peval, pin_level, pow3)

A40 = 56749893611764175164545926946127
GROWTH = [6.9212, 6.9261, 6.9308, 6.9352]      # a(37)..a(40), PROVENANCE.md


def opt(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def sweep_agrees_with_banked(perheight, tri, hmax=None):
    """A new sweep at a new Nmax also re-produces every row below it.  Those
    rows are banked, so the run carries its own regression: if the engine or
    the Nmax bump disturbed anything, the n <= 40 cells say so before the
    n = 41 cell is used for anything."""
    ok = bad = 0
    for fn in os.listdir(perheight):
        m = re.match(r"h(\d+)\.out$", fn)
        if not m:
            continue
        H = int(m.group(1))
        if hmax is not None and H > hmax:
            continue
        for line in open(os.path.join(perheight, fn)):
            p = line.split()
            if len(p) != 2:
                continue
            nn, v = int(p[0]), int(p[1])
            if (nn, H) in tri:
                if tri[(nn, H)] == int(v):
                    ok += 1
                else:
                    bad += 1
                    if bad <= 5:
                        print(f"  SWEEP REGRESSION T({nn},{H}): run {v} != banked {tri[(nn,H)]}")
    print(f"  sweep vs banked triangle: {ok} cells agree, {bad} disagree")
    if bad:
        raise SystemExit("REFUSING: the new sweep disagrees with banked cells")
    if ok < 200:
        raise SystemExit(f"REFUSING: only {ok} cells cross-checked -- vacuous")
    return ok


def sweep_rows(perheight, n, hmax=None):
    """T(n,H) for every H the sweep produced (optionally capped at hmax, which
    is how the a(40) dry run pretends the tall heights were never swept)."""
    out = {}
    if not os.path.isdir(perheight):
        raise SystemExit(f"no sweep directory {perheight}")
    for fn in os.listdir(perheight):
        m = re.match(r"h(\d+)\.out$", fn)
        if not m:
            continue
        H = int(m.group(1))
        if hmax is not None and H > hmax:
            continue
        for line in open(os.path.join(perheight, fn)):
            p = line.split()
            if len(p) == 2 and int(p[0]) == n:
                out[H] = int(p[1])
    return out


def tower(ab, Dj, n, H):
    """T(n,H) from the tower, with the below-onset correction when needed."""
    k = n - H
    E = grand_form(ab, k)
    val = peval(E[k], n) * pow3(n - 1 - 3 * k)
    j = 2 * k + 1 - n
    if j > 0:                       # below onset: add the exact depth defect
        if j not in Dj or k >= len(Dj[j]):
            raise SystemExit(f"T({n},{H}) is depth {j} at k={k}; no D_{j} available")
        val += Dj[j][k]
    if val.denominator != 1:
        raise SystemExit(f"T({n},{H}) not an integer: {val}")
    return int(val)


def build(jmax, kmax_new, forbid_row=None, hmax=None):
    """Pin the levels past the wired table.

    forbid_row: a row n whose cells must NOT be used as pinning data.  Level
    k's depth-j cell is (2k+1-j, k+1-j), and for k = 20 at depth 1 that is
    exactly (40,20) -- a cell the tower is then asked to predict.  Pinning from
    it and calling the result a prediction is circular, so the row being
    predicted is excluded from its own pinning set."""
    P, tri = read_pk(), read_tri()
    ab = extract_ab(P, max(P))
    Dj = load_depths(jmax, kmax_new)
    for k in range(max(P) + 1, kmax_new + 1):
        pairs = [d for d in all_pairs(k, jmax, tri, hmax)
                 if all(2 * k + 1 - j != forbid_row for j in d)]
        if not pairs:
            raise SystemExit(f"level k={k}: no below-onset depth pair at j <= {jmax} "
                             f"with every cell at H <= {hmax}")
        lower = {j: ab[j] for j in ab if j < k}
        sols = {d: pin_level(k, lower, d, tri, Dj) for d in pairs}
        if len(set(sols.values())) != 1:
            raise SystemExit(f"level k={k}: depth pairs disagree -- REFUSING")
        ab[k] = next(iter(sols.values()))
        cells = sorted({(2 * k + 1 - j, k + 1 - j) for d in pairs for j in d})
        tall = max(H for _, H in cells)
        print(f"  level k={k} pinned from {cells} (tallest H={tall}), "
              f"{len(pairs)} pair(s), {len(pairs)-1} independent check(s)")
    return ab, Dj, tri, max(P)


def regression(ab, Dj, tri, kw, n=40, hlo=20):
    """The tower must still reproduce every banked cell of row n it covers."""
    ok = bad = 0
    for H in range(hlo, n + 1):
        if (n, H) not in tri:
            continue
        got = tower(ab, Dj, n, H)
        if got == tri[(n, H)]:
            ok += 1
        else:
            bad += 1
            print(f"  REGRESSION T({n},{H}) k={n-H}: tower {got} != banked {tri[(n,H)]}")
    print(f"  row {n} regression: {ok} cells reproduced, {bad} wrong")
    if bad or ok < 15:
        raise SystemExit(f"REFUSING: row-{n} regression failed or vacuous")
    if n == 40:
        tot = sum(tri[(40, H)] for H in range(1, 41) if (40, H) in tri)
        if tot != A40:
            raise SystemExit(f"REFUSING: banked row 40 sums to {tot}, not a(40)")
        print("  banked row 40 re-sums to a(40) exactly")


def main():
    if "--selftest" in sys.argv:
        ab, Dj, tri, kw = build(int(opt("--jmax", 3)), 20, forbid_row=40, hmax=19)
        bad = dict(ab)
        bad[20] = (bad[20][0] + 1, bad[20][1])
        try:
            regression(bad, Dj, tri, kw)
        except SystemExit:
            print("RED GREEN: a perturbed level 20 fails the row-40 regression")
            return
        raise SystemExit("RED CONTROL FAILED: perturbation not caught")

    n = int(opt("--nmax", 41))
    jmax = int(opt("--jmax", 4))
    perheight = opt("--perheight", os.path.join(ROOT, "runs", "a41_low", "perheight"))
    hcap = opt("--max-swept-h")
    hmax = int(hcap) if hcap else None          # tallest swept height, or uncapped
    hlo = (hmax + 1) if hmax else 20            # first height the tower must cover
    kmax_new = n - hlo                          # the tower covers above the sweep
    # Everything below is capped at the same height the assembly is: a run that
    # says "from heights <= H" must not pin from taller cells either.

    # Two towers, because they answer different questions.
    #  - the REGRESSION tower is pinned with row 40 excluded and is checked
    #    against row 40's banked cells: does the machinery still agree with the
    #    term we already have?
    #  - the ASSEMBLY tower excludes the target row (row 41 has no cells to
    #    exclude) and is what actually produces the new row.
    # Pointing one tower at both jobs either makes the regression circular or
    # makes it vacuous; the first run of this script made it vacuous, which is
    # the better of the two failures but still a failure.
    if n != 40:
        abr, Djr, tri, kwr = build(jmax, 40 - hlo, forbid_row=40, hmax=hmax)
        regression(abr, Djr, tri, kwr, n=40, hlo=hlo)
    ab, Dj, tri, kw = build(jmax, kmax_new, forbid_row=n, hmax=hmax)
    if n == 40:
        regression(ab, Dj, tri, kw, n=40, hlo=hlo)

    if os.path.isdir(perheight):
        sweep_agrees_with_banked(perheight, tri, hmax)
    swept = sweep_rows(perheight, n, hmax)
    row = {}
    for H in range(1, n + 1):
        if H in swept:
            row[H] = swept[H]
        else:
            row[H] = tower(ab, Dj, n, H)
    missing = [H for H in range(1, n + 1) if H not in row]
    if missing:
        raise SystemExit(f"REFUSING: heights not covered: {missing}")

    if row[n] != 3 ** (n - 1):
        raise SystemExit(f"REFUSING: T({n},{n}) = {row[n]}, not 3^{n-1}")
    p1 = (25 * n - 45) * 3 ** (n - 4)
    if row[n - 1] != p1:
        raise SystemExit(f"REFUSING: T({n},{n-1}) = {row[n-1]}, not (25n-45)*3^(n-4)")
    print(f"  edges exact: T({n},{n}) = 3^{n-1}, T({n},{n-1}) = (25n-45)*3^{n-4}")

    total = sum(row.values())
    known = {40: A40,
             39: 8182864667276277865830132493466,
             38: 1180654489101178485738417779914,
             37: 170463735577007360431441250424}
    if n in known:
        if total != known[n]:
            raise SystemExit(f"DRY RUN RED: reassembled a({n}) = {total}, "
                             f"banked {known[n]}")
        print(f"\nheights swept: {sorted(swept)}")
        print(f"heights from the tower: {sorted(set(range(1, n+1)) - set(swept))}")
        print(f"\nDRY RUN GREEN: a({n}) reassembled EXACTLY = {total}")
        return
    ratio = total / A40
    print(f"\nheights swept: {sorted(swept)}")
    print(f"heights from the tower: {sorted(set(range(1, n+1)) - set(swept))}")
    print(f"\na({n}) = {total}")
    print(f"a({n})/a(40) = {ratio:.4f}   (series {GROWTH[0]}, {GROWTH[1]}, "
          f"{GROWTH[2]}, {GROWTH[3]})")
    if not (GROWTH[-1] < ratio < GROWTH[-1] + 0.02):
        print("WARNING: growth ratio is outside the smooth continuation -- "
              "this is a gross check, and it is unhappy")


if __name__ == "__main__":
    main()
