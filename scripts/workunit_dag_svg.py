#!/usr/bin/env python3
"""ONE connected data-flow diagram of the fold engine for one height of a(n).

Trace it top to bottom: a seed frontier flows into column 0; each column does
MAP (U parallel units) then MERGE (R parallel ranges) and emits a new frontier
that flows into the next column; completed polyplets drip out the side into the
running T(n,H) total; every height runs this independently and their totals sum
to a(n). Real a(20) H20 frontier counts label the flow (grow to a peak, then the
geometric collapse — the "cliff").

The MAP→MERGE step is all-to-all (the column transition scatters keys, so every
merge range reads every map output) — shown as ONE labelled arrow, not U×R edges.

Usage: workunit_dag_svg.py [OUT.svg]
"""
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/next-system/designs/workunit-dag.svg"
C_SEED, C_MAP, C_MRG, C_T, C_A = "#d9f2d9", "#ffe7c2", "#ffd1d1", "#cfe8ff", "#e7d9f7"
FLOW, ALL2, COMP = "#1f6fd0", "#e07b00", "#119911"
P = []


def rect(x, y, w, h, fill, rx=7, stroke="#333", sw=1.3, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    P.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}"'
             f' fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def txt(x, y, s, size=13, anchor="middle", weight="normal", fill="#111", italic=False):
    st = ' font-style="italic"' if italic else ""
    P.append(f'<text x="{x:.0f}" y="{y:.0f}" font-family="Helvetica,Arial,sans-serif"'
             f' font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"'
             f' fill="{fill}"{st}>{s}</text>')


def arr(x1, y1, x2, y2, color, sw=2.2, mk="m_flow", label=None, lx=0):
    P.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"'
             f' stroke="{color}" stroke-width="{sw}" marker-end="url(#{mk})"/>')
    if label:
        txt((x1 + x2) / 2 + lx, (y1 + y2) / 2 + 4, label, 11, anchor="start", fill=color)


W, Hh = 720, 980
LANE = 250                                  # main-flow x-centre
P.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" '
         f'viewBox="0 0 {W} {Hh}" font-family="Helvetica,Arial,sans-serif">')
P.append('<defs>' + ''.join(
    f'<marker id="{i}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" '
    f'orient="auto"><path d="M0,0 L6.5,3 L0,6 Z" fill="{c}"/></marker>'
    for i, c in [("m_flow", FLOW), ("m_all", ALL2), ("m_comp", COMP)]) + '</defs>')
rect(0, 0, W, Hh, "#fff", rx=0, stroke="#fff")
txt(W / 2, 28, "fold engine — data flow for one height of a(n)", 17, weight="bold")
txt(W / 2, 46, "(real a(20) H20 frontier sizes; every height runs this independently)",
    11.5, fill="#555", italic=True)

# seed
rect(LANE - 70, 60, 140, 30, C_SEED)
txt(LANE, 80, "SEED · 1 state", 12.5, weight="bold")

# columns: (label, frontier_in, frontier_out)
cols = [("col 0", "1", "524,799"),
        ("col 1", "524,799", "27,308,254"),
        ("col 2  ◀ peak", "27,308,254", "13,478,564")]
BX, BW, BH = 120, 260, 150
ty_top = 250                                # T(n,H) collector bar
y = 108
TX = 470                                    # T-collector x
for ci, (lab, fin, fout) in enumerate(cols):
    # frontier flows in (vertical, in the gap)
    arr(LANE, y, LANE, y + 22, FLOW)
    txt(LANE + 12, y + 16, f"frontier {fin}", 11, anchor="start", fill=FLOW)
    by = y + 24
    rect(BX, by, BW, BH, "#fcfcff", stroke="#99a")
    txt(BX + 12, by + 20, lab, 13, anchor="start", weight="bold")
    # MAP box with unit ticks
    rect(BX + 20, by + 32, BW - 40, 34, C_MAP)
    txt(BX + BW / 2, by + 47, "MAP — U=120 units (parallel)", 11.5)
    for k in range(8):
        rect(BX + 32 + k * 26, by + 52, 18, 9, "#fff", rx=2, stroke="#c89", sw=0.8)
    # all-to-all arrow (in the gap between MAP and MERGE)
    arr(BX + BW / 2, by + 70, BX + BW / 2, by + 92, ALL2, 2.4, "m_all")
    txt(BX + BW / 2 + 14, by + 85, "all-to-all (keys scatter)", 10.5, anchor="start", fill=ALL2)
    # MERGE box with range ticks
    rect(BX + 20, by + 96, BW - 40, 34, C_MRG)
    txt(BX + BW / 2, by + 111, "MERGE — R=120 ranges (parallel)", 11.5)
    for k in range(8):
        rect(BX + 32 + k * 26, by + 116, 18, 9, "#fff", rx=2, stroke="#c66", sw=0.8)
    # completions drip to the right into T(n,H)
    arr(BX + BW, by + 113, TX, by + 113, COMP, 1.8, "m_comp")
    txt(BX + BW + 8, by + 108, "completed", 10, anchor="start", fill=COMP)
    # frontier out
    txt(LANE + 12, by + BH + 16, f"frontier {fout}", 11, anchor="start", fill=FLOW)
    y = by + BH + 24

# cliff note
arr(LANE, y - 4, LANE, y + 22, FLOW)
txt(LANE, y + 40, "⋮  cols 3,4,…  — frontier collapses ×0.42 per column", 11.5, fill="#a00")
txt(LANE, y + 56, "(the cliff: cols 6+ are a rounding error)", 11, fill="#a00", italic=True)

# T(n,H) collector bar on the right
rect(TX, 132, 200, y - 132, C_T)
txt(TX + 100, 152, "T(n, H)", 14, weight="bold")
txt(TX + 100, 170, "running total of", 10.5, fill="#333")
txt(TX + 100, 184, "completed n-cell", 10.5, fill="#333")
txt(TX + 100, 198, "polyplets of height H", 10.5, fill="#333")

# fold to a(n)
ay = y + 80
arr(TX + 100, y, TX + 100, ay, COMP)
rect(LANE - 20, ay, (TX + 100) - (LANE - 20) + 0, 0, "#fff", rx=0, stroke="#fff")  # spacer
rect(170, ay, 380, 44, C_A)
txt(360, ay + 20, "a(n) = Σ over H=1..n  of  T(n, H)", 13.5, weight="bold")
txt(360, ay + 37, "every height H is an INDEPENDENT copy of this flow", 11, fill="#444", italic=True)
arr(TX + 100, ay - 0, 470, ay, COMP)  # T -> a(n)

# legend (bottom-left)
lx, ly = 40, ay + 70
txt(lx, ly, "arrows:", 12, anchor="start", weight="bold")
for i, (c, lab) in enumerate([(FLOW, "frontier flows down (sequential: col→col)"),
                              (ALL2, "MAP→MERGE all-to-all (the bipartite fan-in)"),
                              (COMP, "completed polyplets → the count")]):
    yy = ly + 20 + i * 20
    P.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+34}" y2="{yy}" stroke="{c}" '
             f'stroke-width="2.4" marker-end="url(#{"m_flow" if c==FLOW else "m_all" if c==ALL2 else "m_comp"})"/>')
    txt(lx + 42, yy + 4, lab, 11, anchor="start")

P.append("</svg>")
open(OUT, "w").write("\n".join(P) + "\n")
print(f"wrote {OUT}")
