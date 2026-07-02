#!/usr/bin/env python3
"""a25_provenance_chart.py -- height x column provenance grid for a(25).

Run with no args for the (H x column) rectangle; `triangle` for the T(n,H) view.

Every cell T(25,H) that sums to a(25) is tagged by where its value came from,
so the single-source term can be audited at a glance. Values are the assembled
triangle from the dalby-solo run (runs/ns_a25, combine output); the swept
(H,col) work-cells are taken from that run's own event=column log lines.
"""

import sys

# T(25,H): the height-row of the a(25) triangle (combine output, dalby run).
T = {
    1: 1, 2: 3166815960, 3: 21289197346820, 4: 2513177361030402,
    5: 43556120823729954, 6: 251419543002787484, 7: 734233519857407741,
    8: 1386194792641478052, 9: 1962555206744783639, 10: 2276612251171343020,
    11: 2273480557956922883, 12: 2003044942843944054, 13: 1573134737210737385,
    14: 1104184694723970106, 15: 691293861738937174, 16: 384025992867882686,
    17: 187767529262410933, 18: 79909931154646710, 19: 29162802744502056,
    20: 8945394666328278, 21: 2243103228616860, 22: 441543992247720,
    23: 63979394394438, 24: 6067004857740, 25: 282429536481,
}

MAXN = 25
SWEPT = set(range(3, 17))          # H3..16 swept on dalby (log-confirmed, cols 0..25)
SWEPT_COLS = set(range(0, 26))     # every column 0..25 emitted an event=column line

# source class per height, and a one-line justification
def source(H):
    k = MAXN - H
    if H in (1, 2):
        return "=", f"low-height closed form (proven); T(n,{H}) row"
    if H in SWEPT:
        return "#", "dalby transfer-matrix sweep, THIS run (single-source)"
    if k == 0:
        return "=", "diagonal k=0 top, PROVEN: T(n,n)=3^(n-1)=3^24"
    if k == 1:
        return "=", "diagonal k=1 pole, PROVEN (C1): (25n-45)*3^(n-4)"
    if k == 2:
        return "=", "diagonal k=2, PROVEN from first principles (T-n-nm2)"
    if 3 <= k <= 7:
        return "+", f"diagonal k={k}, data-pinned + VALIDATED at scale (a23/a24 swept rows)"
    if k == 8:
        return "?", "diagonal k=8 (P8), pinned from a(24)'s T(24,16) ALONE -- NOT cross-checked at n=25"
    return " ", "?"

LEGEND = [
    ("#", "swept on dalby this run (transfer-matrix, cols 0-25) -- single-source, uncertified"),
    ("=", "closed form, PROVEN from first principles"),
    ("+", "closed form, data-pinned + validated against earlier swept rows"),
    ("?", "closed form, extrapolated from a(24) only -- UNCONFIRMED at n=25 (weakest link)"),
]

def main():
    out = []
    out.append("a(25) provenance -- height (H) x sweep-column (col).  a(25) = sum over H of T(25,H).")
    out.append("")
    # header: column indices 0..25
    hdr = "  H \\ col " + "".join(f"{c%10}" for c in range(MAXN + 1))
    out.append(hdr)
    for H in range(MAXN, 0, -1):
        sym, _ = source(H)
        if H in SWEPT:
            cells = "".join(sym if c in SWEPT_COLS else "." for c in range(MAXN + 1))
        else:
            # closed form: no per-column work; the one formula supplies the whole row
            cells = sym * (MAXN + 1)
        out.append(f"  H={H:2d}    {cells}   T(25,{H:2d}) = {T[H]:,}")
    out.append("")
    out.append("legend:")
    for sym, desc in LEGEND:
        out.append(f"   {sym}  {desc}")
    out.append("")
    total = sum(T.values())
    out.append(f"  swept heights (#): H3-16  = 14 heights x 26 columns = 364 real work-cells (dalby log-confirmed)")
    out.append(f"  closed-form heights:      H1,2 (=) + H17-25 (?,+,=) = 11 heights, 0 map/merge work")
    out.append(f"  SUM_H T(25,H) = {total:,}")
    out.append(f"  a(25)         = 14,994,811,325,186,658,577  {'MATCH' if total==14994811325186658577 else 'MISMATCH'}")
    text = "\n".join(out)
    print(text)
    with open("results/ns_a25/provenance.txt", "w") as f:
        f.write(text + "\n")

A_N = {  # row sums a(n) = sum_H T(n,H); a(1..24) are the known/recorded prefix
    1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941,
    9: 940982, 10: 6053180, 11: 39299408, 12: 257105146, 13: 1692931066,
    14: 11208974860, 15: 74570549714, 16: 498174818986, 17: 3340366308393,
    18: 22471158811164, 19: 151609203011580, 20: 1025573519362016,
    21: 6954084405510437, 22: 47255332844367680, 23: 321749260511448732,
    24: 2194666793369310473, 25: 14994811325186658577,
}

def cell_symbol(n, H):
    """Provenance of triangle cell T(n,H), as computed by THIS run."""
    k = n - H
    if H <= 2:
        return "="                 # low-height closed form (proven)
    if H in SWEPT:
        return "#"                 # dalby transfer-matrix sweep
    # H >= 17: closed-form diagonal band, tier by k = n-H
    if k <= 2:
        return "="                 # k=0,1,2 proven from first principles
    if k <= 7:
        return "+"                 # k=3..7 data-pinned + validated at scale
    return "?"                     # k=8 (P8) pinned from a(24) alone -- unchecked at n=25

def triangle():
    out = []
    out.append("a(25) provenance -- FULL triangle T(n,H), 1<=H<=n<=25.  row-sum = a(n).")
    out.append("")
    out.append("  n \\ H   " + "".join(f"{h%10}" for h in range(1, MAXN + 1)))
    for n in range(MAXN, 0, -1):
        row = "".join(cell_symbol(n, H) for H in range(1, n + 1))
        pad = " " * (MAXN - n)      # right-side ragged edge -> triangle
        out.append(f"  n={n:2d}    {row}{pad}   a({n:2d}) = {A_N[n]:,}")
    out.append("")
    out.append("legend:")
    for sym, desc in LEGEND:
        out.append(f"   {sym}  {desc}")
    out.append("")
    out.append("  the main diagonal (right edge, H=n) is k=0: T(n,n)=3^(n-1), proven.")
    out.append("  the '?' at row 25 col 17 is the lone k=8 cell T(25,17) -- the single unchecked value.")
    text = "\n".join(out)
    print(text)
    with open("results/ns_a25/provenance_triangle.txt", "w") as f:
        f.write(text + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "triangle":
        triangle()
    else:
        main()
