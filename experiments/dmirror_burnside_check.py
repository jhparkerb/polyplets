#!/usr/bin/env python3
"""Burnside tie between the dm-mirror strip counts and the joint box table.

THE IDENTITY.  Fix n and S.  Let B(n, S, S) be the number of fixed polyplets
with n cells whose bounding box is exactly S x S, and let d(S, n) be the number
of those that are invariant under the transpose (the dm-mirror strip count,
`results/dmirror-diagonals.md`).  The transpose maps an exact S x S box to
itself, so C_2 = {id, transpose} acts on the B(n, S, S) animals with exactly
d(S, n) fixed points.  Burnside makes the orbit count

    (B(n, S, S) + d(S, n)) / 2

a non-negative integer, i.e.

    B(n, S, S) == d(S, n)   (mod 2)     for every n and S.

That is the whole check.  It is mod 2 and therefore weak, but the two sides
come from unrelated programs: B from the row-transfer probe
`experiments/joint_box_probe.py`, d from the `dmirror_strip` rows of
`results/sym_counts.txt` (the hook-sweep symtm engine) or, in arm B, from the
pinned quasi-polynomials P_k.

ARM A (enumerated).  Both sides enumerated, S = 1..SMAX, k = n - S <= BUD.

ARM B (formula).  The cells the D(33) assembly takes from the closed forms
rather than from enumeration: n = 33, S = 33 - k for k <= BUD.  d is the
P_k^parity(S) value, re-pinned here from the banked strips by exact
differencing; B is enumerated.  The k = 4 cell (S = 29) is out of reach: the
row-transfer cache blows up at BUD = 4.

Fail-closed: mismatch, missing input, an unpinnable level, a pin with no
holdout, too few cells checked, an all-even (vacuous) comparison, or a RED
control that fails to fire all exit non-zero.

    python3 experiments/dmirror_burnside_check.py [--smax 12] [--bud 3]
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))

import joint_box_probe as JB              # noqa: E402
import dmirror_onset_probe as OP          # noqa: E402

FORMULA_N = 33          # the D(33) assembly; results/related-seqs-n33.md
MIN_ARM_A = 30          # cells arm A must actually compare
FAILURES = []
_TABLES = {}


def fail(msg):
    FAILURES.append(msg)
    print("FAIL: " + msg)


def box_table(H):
    """B(n, W, H) for one height, as a dict keyed (n, W)."""
    if H not in _TABLES:
        _TABLES[H] = JB.joint(H)
    return _TABLES[H]


def arm_a(d, smax, bud, sink):
    """Compare enumerated B against enumerated d.  Returns (cells, odd)."""
    checked = odd = 0
    for S in range(1, smax + 1):
        B = box_table(S)
        for k in range(bud + 1):
            if (S, k) not in d:
                continue
            b, dd = B.get((S + k, S), 0), d[(S, k)]
            checked += 1
            if (b - dd) % 2:
                sink.append("S=%d k=%d: B=%d d=%d differ mod 2" % (S, k, b, dd))
            elif b % 2:
                odd += 1
    return checked, odd


def edge_control(H, B):
    """Independent identities the row transfer must reproduce at every height
    it is asked for (results/joint-box-probe.md): the width-2 column."""
    if H >= 2:
        if B.get((H, 2), 0) != 2 ** H - 2:
            fail("edge control B(%d,2,%d) != 2^%d-2" % (H, H, H))
        if B.get((H + 1, 2), 0) != H * 2 ** (H - 1):
            fail("edge control B(%d,2,%d) != %d*2^%d" % (H + 1, H, H, H - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smax", type=int, default=12,
                    help="top S for arm A (enumerated both sides)")
    ap.add_argument("--bud", type=int, default=3,
                    help="surplus cap k <= bud for the row transfer")
    args = ap.parse_args()

    JB.BUD = args.bud
    JB.M = 3 + 2 * JB.BUD
    JB.shape_transitions.cache_clear()

    d = OP.load()
    if not d:
        fail("no dmirror_strip rows in results/sym_counts.txt")
        return finish()

    # ---- arm A: enumerated vs enumerated -----------------------------------
    sink = []
    checked, odd_cells = arm_a(d, args.smax, args.bud, sink)
    for m in sink:
        fail("arm A " + m)
    for S in range(1, args.smax + 1):
        edge_control(S, box_table(S))
    if checked < MIN_ARM_A:
        fail("arm A compared %d cells, need %d" % (checked, MIN_ARM_A))
    print("arm A: %d enumerated cells, %d of them odd on both sides"
          % (checked, odd_cells))

    # ---- arm B: the D(33) formula cells ------------------------------------
    wanted = args.bud + 1
    got = 0
    for k in range(args.bud + 1):
        S = FORMULA_N - k
        res, err = OP.analyse(d, k, S % 2, verbose=False)
        if err:
            fail("arm B k=%d: level not pinned (%s)" % (k, err))
            continue
        mono, onset, hold, pinlow, npts = res
        if hold < 1:
            fail("arm B k=%d: pinned with no holdout" % k)
            continue
        val = OP.evalpoly(mono, S)
        if val.denominator != 1:
            fail("arm B k=%d: P_k(%d) is not an integer" % (k, S))
            continue
        dd = int(val)
        B = box_table(S)
        edge_control(S, B)
        b = B.get((FORMULA_N, S), 0)
        got += 1
        mark = "ok" if (b - dd) % 2 == 0 else "MISMATCH"
        print("arm B k=%d  d(%d,%d)=%d (onset S>=%d, %d holdouts)  "
              "B(%d,%d,%d)=%d  %s"
              % (k, S, FORMULA_N, dd, onset, hold, FORMULA_N, S, S, b, mark))
        if (b - dd) % 2:
            fail("arm B S=%d k=%d: B=%d d=%d differ mod 2" % (S, k, b, dd))
    if got != wanted:
        fail("arm B compared %d cells, expected %d" % (got, wanted))

    if odd_cells == 0:
        fail("every compared cell was even on both sides -- vacuous check")

    # ---- RED controls: real mutations, run through arm A itself ------------
    # Tables are cached, so each replay costs nothing.
    def replay(shadow, label):
        red = []
        arm_a(shadow, args.smax, args.bud, red)
        if not red:
            fail("RED control did not fire: %s" % label)
        else:
            print("RED control fired (%s): %s" % (label, red[0]))

    shadow = dict(d)
    shadow[(args.smax, 0)] += 1
    replay(shadow, "one strip count off by 1")

    H = args.smax
    saved = _TABLES[H]
    _TABLES[H] = dict(saved)
    _TABLES[H][(H, H)] = _TABLES[H].get((H, H), 0) + 1
    try:
        replay(dict(d), "one box count off by 1")
    finally:
        _TABLES[H] = saved

    return finish()


def finish():
    if FAILURES:
        print("\n%d FAILURE(S)" % len(FAILURES))
        return 1
    print("\nBurnside tie holds on every cell compared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
