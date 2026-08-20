#!/usr/bin/env python3
"""Rule-independent tower: every level pinned from MOTLEY's cells alone.

The wired diagCoeffTable came from the incumbent sweep, so a tower that reads
it inherits the incumbent's connectivity rule.  This builds the tower from
nothing but

  * Motley's own banked C_H rows, telescoped to T(n,H) for H <= HMAX -- a
    different rule, proved in docs/proofs/cutcount-identity.md;
  * the ab-initio depth identities D_j(k) of Severance W3, which read neither
    triangle nor wired table;
  * the grand form, which is a Lean-complete theorem;

and then asks what it says about the cells Motley cannot reach.

Usage: undertow_ri.py [--hmax 18] [--jmax 3] [--row 40]
"""
import os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "experiments" else HERE
sys.path.insert(0, os.path.join(ROOT, "experiments"))

from undertow_pin import (all_pairs, extract_ab, grand_form, load_depths,  # noqa
                          peval, pin_level, pow3, read_tri_motley)
from slope2_law_vs_truth import read_pk, read_tri                          # noqa

# Levels 1..9 are ab initio: Severance W1 derived P_1..P_9 from cluster
# weights alone and matched the wired table coefficient for coefficient
# (results/severance-w1-anchor-cut.md).  Reading them out of the wired table
# is reading numbers a second source already produced, not inheriting the
# incumbent's rule.  Level 1 also cannot be pinned by depth at all -- its
# depth-2 cell would be T(1,0).
W1_ABINITIO = 9


def opt(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main():
    hmax = int(opt("--hmax", 18))
    jmax = int(opt("--jmax", 3))
    row = int(opt("--row", 40))
    mtri = read_tri_motley()
    inc = read_tri()
    kcap = hmax + jmax - 2
    Dj = load_depths(jmax, kcap + 1)

    ab = {j: v for j, v in extract_ab(read_pk(), W1_ABINITIO).items()}
    print(f"levels 1..{W1_ABINITIO} seeded from Severance W1's ab-initio P_k")
    for k in range(W1_ABINITIO + 1, kcap + 1):
        pairs = [d for d in all_pairs(k, jmax, mtri, hmax)
                 if all(2 * k + 1 - j != row for j in d)]
        if not pairs:
            print(f"  level k={k}: no Motley pair at j<={jmax}, H<={hmax} -- STOP")
            kcap = k - 1
            break
        sols = {d: pin_level(k, dict(ab), d, mtri, Dj) for d in pairs}
        if len(set(sols.values())) != 1:
            raise SystemExit(f"level k={k}: Motley depth pairs DISAGREE")
        ab[k] = next(iter(sols.values()))
    print(f"levels {W1_ABINITIO+1}..{kcap} pinned from MOTLEY cells only "
          f"(jmax={jmax}, every pinning cell H<={hmax})")

    E = grand_form(ab, kcap)
    ok = bad = 0
    covered = []
    for H in range(row - kcap, row + 1):
        k = row - H
        if k == 0:
            v = F(3) ** (row - 1)
        else:
            v = peval(E[k], row) * pow3(row - 1 - 3 * k)
            j = 2 * k + 1 - row
            if j > 0:
                v += Dj[j][k] if j in Dj else None
        if v.denominator != 1:
            raise SystemExit(f"T({row},{H}) not integral")
        covered.append(H)
        if (row, H) in inc:
            if int(v) == inc[(row, H)]:
                ok += 1
            else:
                bad += 1
                print(f"  MISMATCH T({row},{H}) k={k}: tower {int(v)} != incumbent {inc[(row,H)]}")
    print(f"row {row}: tower covers H = {min(covered)}..{max(covered)} "
          f"({len(covered)} cells); {ok} match the incumbent, {bad} wrong")
    mot = [H for H in range(1, row + 1) if H <= hmax and (row, H) in mtri]
    gap = sorted(set(range(1, row + 1)) - set(mot) - set(covered))
    print(f"row {row}: Motley covers H = 1..{max(mot)} ({len(mot)} cells)")
    print(f"row {row}: GAP = {gap if gap else 'NONE'}")


if __name__ == "__main__":
    main()
