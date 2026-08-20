#!/usr/bin/env python3
"""How far is a(n) rule-independent, using nothing the incumbent produced?

The wired `diagCoeffTable` came from the production sweep, so a tower that
reads it inherits the incumbent's connectivity rule. This one is built from:

  * Severance W1's ab-initio P_1..P_9 (cluster weights; matched the wired
    table coefficient for coefficient, results/severance-w1-anchor-cut.md) --
    also the only way to start, since level 1's depth-2 cell would be T(1,0);
  * MOTLEY's own banked C_H rows, telescoped T = C_H - 2C_{H-1} + C_{H-2},
    for the higher levels -- a different rule, proved in
    docs/proofs/cutcount-identity.md;
  * the ab-initio depth defects D_j(k) of Severance W3, which read neither
    triangle nor wired table;
  * the grand form, a Lean-complete theorem.

Each row is answered with a tower that EXCLUDES that row from its own pinning
set, so no cell is ever predicted from itself. Motley covers H <= hmax, the
tower covers H > hmax, and the report says which heights neither reaches.

Usage:
  python3 experiments/undertow_ri.py [--hmax 18] [--jmax 4] [--rows 36,37,...]
                                    [--rowdir DIR]
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from undertow_pin import (all_pairs, grand_form, load_depths, padd, ptrim,  # noqa: E402
                          peval, pin_level, pow3, read_tri_motley)
from slope2_law_vs_truth import read_tri                                   # noqa: E402

W1_ABINITIO = 9
AB0 = {}


def abinitio_levels():
    """(a_k, b_k) for k = 1..9 straight from Severance W1's cluster weights.

    Not from the wired diagCoeffTable: W1 matched that table coefficient for
    coefficient, but the table is the incumbent's file, and this whole exercise
    is about not reading the incumbent's files."""
    from severance_w1_assemble import load_weights, assemble_R, pk_from_R
    W = load_weights(os.path.join(ROOT, "results", "severance_w1_weights_k9.txt"))
    R = assemble_R(W, W1_ABINITIO)
    ab = {}
    for k in range(1, W1_ABINITIO + 1):
        E = grand_form(ab, k)                       # levels < k
        rem = ptrim(padd(pk_from_R(R[k], k), [-c for c in E[k]]))
        if len(rem) > 2:
            raise SystemExit(f"grand form violated at k={k} on the ab-initio P_k")
        ab[k] = (rem[0] if rem else F(0), rem[1] if len(rem) > 1 else F(0))
    return ab


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def known_a():
    out = {}
    for cand in ("fixtures/b006770.txt", "results/b006770_upload.txt"):
        p = os.path.join(ROOT, cand)
        if not os.path.exists(p):
            continue
        for line in open(p):
            q = line.split()
            if len(q) == 2 and q[0].isdigit():
                out[int(q[0])] = int(q[1])
    return out


def build_tower(mtri, Dj, jmax, hmax, kcap, forbid_row):
    """Levels 1..kcap; W1 below, Motley-pinned above, `forbid_row` untouchable."""
    ab = dict(AB0)
    reached = W1_ABINITIO
    for k in range(W1_ABINITIO + 1, kcap + 1):
        pairs = [d for d in all_pairs(k, jmax, mtri, hmax)
                 if all(2 * k + 1 - j != forbid_row for j in d)]
        if not pairs:
            break
        sols = {d: pin_level(k, dict(ab), d, mtri, Dj) for d in pairs}
        if len(set(sols.values())) != 1:
            raise SystemExit(f"level k={k}: Motley depth pairs DISAGREE")
        ab[k] = next(iter(sols.values()))
        reached = k
    return ab, reached


def main():
    hmax = int(opt("--hmax", 18))
    jmax = int(opt("--jmax", 4))
    rows = [int(x) for x in opt("--rows", "40").split(",") if x]
    # --rowdir: which Motley C_H rows to telescope.  The banked
    # results/cutcount_b1/rows/ stop at n = 40; a ladder run at a higher Nmax
    # writes its own set, and row 41 can only be answered from those.
    rowdir = opt("--rowdir", None)
    mtri, inc, A = read_tri_motley(rowdir), read_tri(), known_a()
    global AB0
    AB0 = abinitio_levels()
    kcap = hmax + jmax - 2
    Dj = load_depths(jmax, kcap + 1)
    print(f"Motley triangle H <= {max(H for _, H in mtri)}; depths j <= {jmax}; "
          f"levels 1..{W1_ABINITIO} ab initio")

    for row in rows:
        ab, reached = build_tower(mtri, Dj, jmax, hmax, kcap, forbid_row=row)
        E = grand_form(ab, reached)
        ok = bad = 0
        total = F(0)
        tower_h = []
        for H in range(max(hmax + 1, row - reached), row + 1):
            k = row - H
            v = (F(3) ** (row - 1) if k == 0
                 else peval(E[k], row) * pow3(row - 1 - 3 * k))
            j = 2 * k + 1 - row
            if k and j > 0:
                if j not in Dj or k >= len(Dj[j]):
                    continue                    # no exact depth here; not covered
                v += Dj[j][k]
            if v.denominator != 1:
                raise SystemExit(f"T({row},{H}) not integral")
            tower_h.append(H)
            total += v
            if (row, H) in inc:
                ok += 1 if int(v) == inc[(row, H)] else 0
                bad += 0 if int(v) == inc[(row, H)] else 1
                if int(v) != inc[(row, H)]:
                    print(f"    MISMATCH T({row},{H}) k={k}")
        # Rows at or below hmax are covered by Motley outright: the tower band
        # is empty and there is nothing for it to do.  Reporting them as a
        # crash (min() of an empty band) meant the pure-Motley rows were
        # claimed and never attested -- Lane A, S-A3.
        mot = [H for H in range(1, min(hmax, row) + 1) if (row, H) in mtri]
        if mot and not tower_h and len(mot) == row:
            total_m = sum(mtri[(row, H)] for H in mot)
            tag = "COMPLETE, sum MATCHES a(%d)" % row if A.get(row) == total_m \
                else ("COMPLETE, a(%d) = %d" % (row, total_m) if row not in A
                      else "COMPLETE but sum WRONG")
            print(f"row {row:2d}: Motley H<={max(mot):2d} ({len(mot)} cells), "
                  f"tower not needed -- {tag}")
            continue
        if not mot:
            print(f"row {row:2d}: Motley has no cells for this row "
                  f"(its C rows stop at Nmax) -- skipped")
            continue
        for H in mot:
            total += mtri[(row, H)]
        gap = sorted(set(range(1, row + 1)) - set(mot) - set(tower_h))
        line = (f"row {row:2d}: Motley H<={max(mot):2d} ({len(mot)} cells) + "
                f"tower H>={min(tower_h)} ({len(tower_h)} cells), "
                f"levels to k={reached}, {ok} agree with the incumbent, {bad} wrong")
        if gap:
            line += f" -- GAP {gap}"
        elif row in A:
            line += (" -- COMPLETE, sum MATCHES a(%d)" % row if int(total) == A[row]
                     else " -- COMPLETE but sum WRONG")
        else:
            line += f" -- COMPLETE, a({row}) = {int(total)}"
        print(line)


if __name__ == "__main__":
    main()
