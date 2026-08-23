#!/usr/bin/env python3
"""Does EACH spine family have a grand form? -- the second half of A1.3.

`results/dmirror-grand-form-fails.md` established that the dmirror family as a
whole does not: every cumulant past the first is nonlinear in S, on both parity
classes, and deg(c_j) = 2*floor(j/2) is the signature of exactly two families
added together.  `experiments/dmirror_spine_split.py` then counted the two
families apart -- anchored on all 423 banked `dmirror_strip` cells, which it
reproduces exactly.

This asks the question that split was for: with d_main and d_anti separated,
is EITHER of them a single-family object with the grand-form shape -- every
cumulant exactly linear in S?

If yes for both, the two-family reading is confirmed and the dmirror levels are
finitely determined after all, just with four new constants per level instead of
two.  If no, the diagnosis in dmirror-grand-form-fails.md is incomplete and the
obstruction is something other than the two-spine sum.

INPUT is the log of a `dmirror_spine_split.py` run, parsed rather than
recomputed -- the sweep is exponential in S and there is no reason to pay for it
twice.  Only rows where the split is DEFINED (S >= 2k+2) are used; the script
refuses to read a row outside that regime.

CONTROLS.
  (a) A planted single family must report LINEAR, and a planted sum of two must
      report NONLINEAR -- the same pair dmirror_grand_form.py uses, so a
      disagreement between the two scripts is visible.
  (b) A level pinned with no point to spare is reported as unpinned, never as a
      measurement.

Usage:
    python3 experiments/dmirror_spine_cumulants.py LOGFILE

Target machine: ayr or dalby.  Cost: instant, exact rational arithmetic.
"""

import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dmirror_grand_form import (  # noqa: E402
    cumulants, pdeg, controls, report as gf_report)
from dmirror_onset_probe import newton_fit, evalpoly  # noqa: E402

def load(path):
    """{(S, k): (main, anti)} for rows where the split is defined.

    Reads both producers.  experiments/dmirror_spine_split.py prints
    S k total banked main anti neither; cpp/dmirror_spine.cpp has no banked
    column (it gates against the banked rows rather than printing them), so its
    rows are S k total main anti neither.  Anything else on the line is a
    marker and is ignored.  A row whose numeric width is neither 6 nor 7 is
    skipped rather than guessed at."""
    out = {}
    for ln in open(path):
        tok = []
        for t in ln.split():
            if t.lstrip("-").isdigit() or t == "-":
                tok.append(t)
            else:
                break
        if len(tok) not in (6, 7) or tok[0] == "-" or tok[1] == "-":
            continue
        S, k = int(tok[0]), int(tok[1])
        if S < 2 * k + 2:
            continue
        mi, ai = (4, 5) if len(tok) == 7 else (3, 4)
        if tok[mi] == "-" or tok[ai] == "-":
            continue
        out[(S, k)] = (int(tok[mi]), int(tok[ai]))
    return out


def pin(points, k):
    """Exact polynomial through the deepest points, with a holdout.

    A level of degree <= k needs k+1 points to pin and one more to check.
    Returns (poly, holdouts) or (None, reason)."""
    pts = sorted(points)
    if len(pts) < k + 2:
        return None, "only %d points, need %d" % (len(pts), k + 2)
    poly = newton_fit(pts[-(k + 1):])
    hold = 0
    for S, v in reversed(pts[:-(k + 1)]):
        if evalpoly(poly, S) != v:
            break
        hold += 1
    if hold == 0:
        return None, "pinned but the first holdout FAILED -- not degree %d" % k
    return (poly, hold), None


def analyse(name, data, which, kmax):
    print("\n%s:" % name)
    polys = {}
    for parity in (0, 1):
        pol = {}
        for k in range(0, kmax + 1):
            pts = [(S, v[which]) for (S, kk), v in data.items()
                   if kk == k and S % 2 == parity]
            res, err = pin(pts, k)
            if res is None:
                print("   k=%d %-5s NOT PINNED (%s)"
                      % (k, "even" if parity == 0 else "odd", err))
                break
            pol[k] = list(res[0])
            print("   k=%d %-5s pinned, %d holdout(s), degree %d"
                  % (k, "even" if parity == 0 else "odd", res[1], pdeg(res[0])))
        polys[parity] = pol
    kmax_ok = min(max(polys[0]) if polys[0] else -1,
                  max(polys[1]) if polys[1] else -1)
    if kmax_ok < 2:
        print("   only k <= %d pinned on both parities -- c_2 is the "
              "discriminator and it is out of reach" % kmax_ok)
        return None
    print("   cumulants to k = %d:" % kmax_ok)
    out = {}
    for parity in (0, 1):
        c = cumulants([polys[parity][k] for k in range(kmax_ok + 1)], kmax_ok)
        degs = {j: pdeg(v) for j, v in c.items()}
        lin = all(d <= 1 for d in degs.values())
        print("     %-5s %s  => %s"
              % ("even" if parity == 0 else "odd",
                 "  ".join("c_%d:deg %d" % (j, d) for j, d in sorted(degs.items())),
                 "GRAND FORM SHAPE" if lin else "NOT linear"))
        out[parity] = lin
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    print("Do the spine families separately have a grand form?  Controls first.\n")
    if not controls(4):
        print("\nCONTROLS FAILED -- nothing below is worth reading")
        return 1
    data = load(sys.argv[1])
    if not data:
        print("\nno usable rows in %s" % sys.argv[1])
        return 1
    ks = sorted({k for _, k in data})
    print("\n%d split rows, levels k = %d..%d" % (len(data), ks[0], ks[-1]))
    m = analyse("d_main (the main-diagonal family)", data, 0, max(ks))
    a = analyse("d_anti (the anti-diagonal family)", data, 1, max(ks))

    print("\nVERDICT")
    if m and a and all(m.values()) and all(a.values()):
        print("  BOTH families have the grand-form shape.  The two-spine")
        print("  diagnosis is confirmed: the dmirror levels ARE finitely")
        print("  determined, with four new constants per level rather than two,")
        print("  and A1.3's step 1 fails only because the two were summed.")
    elif m is None or a is None:
        print("  Not enough banked levels to decide.  Run the split to a")
        print("  larger S; c_2 is the discriminator and it needs k <= 2 pinned")
        print("  on both parities of both families.")
    else:
        print("  At least one family is NOT of grand-form shape.  The")
        print("  two-spine sum is then not the whole obstruction, and")
        print("  results/dmirror-grand-form-fails.md's diagnosis is incomplete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
