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

Exit 0 unless a tower cell disagrees with the incumbent (MISMATCH) or a
complete row sums to something other than the banked a(n) ("sum WRONG").
Until 2026-09-05 both were printed and the script exited 0 (AUDIT-2026-09-02
M3); a GAP is a report, not a failure, and still exits 0.
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


def cover(hmax=18, jmax=4, rows=(40,), rowdir=None):
    """Per row: how Motley (H <= hmax) and the Motley-pinned tower (H > hmax)
    cover it, and whether the tower agrees with the incumbent where it can.

    Returns one dict per row: row, mot (Motley heights), tower (tower heights),
    agree (tower cells equal to the incumbent, as (row, H)), wrong (tower cells
    that differ), gap (heights neither reaches), reached (top pinned level),
    total (the row sum, or None), status in
      MATCH   complete, sums to the banked a(row)
      NEW     complete, no banked a(row) to compare against
      WRONG   complete, sum differs from the banked a(row)
      GAP     some height covered by neither
      SKIP    Motley has no cells for this row at all
    scripts/provenance_table.py reads `agree` to tag the tower-from-Motley
    cells; main() prints the report and exits non-zero on wrong or WRONG."""
    global AB0
    mtri, inc, A = read_tri_motley(rowdir), read_tri(), known_a()
    AB0 = abinitio_levels()
    kcap = hmax + jmax - 2
    Dj = load_depths(jmax, kcap + 1)
    out = []
    for row in rows:
        ab, reached = build_tower(mtri, Dj, jmax, hmax, kcap, forbid_row=row)
        E = grand_form(ab, reached)
        agree, wrong, tower_h = [], [], []
        total = F(0)
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
                (agree if int(v) == inc[(row, H)] else wrong).append((row, H))
        mot = [H for H in range(1, min(hmax, row) + 1) if (row, H) in mtri]
        rec = dict(row=row, mot=mot, tower=tower_h, agree=agree, wrong=wrong,
                   gap=[], reached=reached, total=None, status="SKIP",
                   mtri_top=max(H for _, H in mtri))
        if not mot:
            out.append(rec)
            continue
        for H in mot:
            total += mtri[(row, H)]
        gap = sorted(set(range(1, row + 1)) - set(mot) - set(tower_h))
        rec["gap"], rec["total"] = gap, int(total)
        if gap:
            rec["status"] = "GAP"
        elif row not in A:
            rec["status"] = "NEW"
        else:
            rec["status"] = "MATCH" if int(total) == A[row] else "WRONG"
        out.append(rec)
    return out


def main():
    hmax = int(opt("--hmax", 18))
    jmax = int(opt("--jmax", 4))
    rows = [int(x) for x in opt("--rows", "40").split(",") if x]
    # --rowdir: which Motley C_H rows to telescope.  The banked
    # results/cutcount_b1/rows/ stop at n = 40; a ladder run at a higher Nmax
    # writes its own set, and row 41 can only be answered from those.
    rowdir = opt("--rowdir", None)
    recs = cover(hmax, jmax, rows, rowdir)
    print(f"Motley triangle H <= {recs[0]['mtri_top']}; depths j <= {jmax}; "
          f"levels 1..{W1_ABINITIO} ab initio")
    red = False
    for r in recs:
        row, mot, tower_h = r["row"], r["mot"], r["tower"]
        for n, H in r["wrong"]:
            print(f"    MISMATCH T({n},{H}) k={n-H}")
        if r["status"] == "SKIP":
            print(f"row {row:2d}: Motley has no cells for this row "
                  f"(its C rows stop at Nmax) -- skipped")
            continue
        # Rows at or below hmax are covered by Motley outright: the tower band
        # is empty and there is nothing for it to do.  Reporting them as a
        # crash (min() of an empty band) meant the pure-Motley rows were
        # claimed and never attested -- Lane A, S-A3.
        tag = {"MATCH": "COMPLETE, sum MATCHES a(%d)" % row,
               "NEW": "COMPLETE, a(%d) = %s" % (row, r["total"]),
               "WRONG": "COMPLETE but sum WRONG",
               "GAP": "GAP %s" % r["gap"]}[r["status"]]
        if not tower_h and len(mot) == row:
            print(f"row {row:2d}: Motley H<={max(mot):2d} ({len(mot)} cells), "
                  f"tower not needed -- {tag}")
        else:
            print(f"row {row:2d}: Motley H<={max(mot):2d} ({len(mot)} cells) + "
                  f"tower H>={min(tower_h)} ({len(tower_h)} cells), "
                  f"levels to k={r['reached']}, {len(r['agree'])} agree with "
                  f"the incumbent, {len(r['wrong'])} wrong -- {tag}")
        if r["wrong"] or r["status"] == "WRONG":
            red = True
    if red:
        raise SystemExit("undertow_ri RED: a tower cell or a row sum disagrees "
                         "with the incumbent")


if __name__ == "__main__":
    main()
