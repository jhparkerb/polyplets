#!/usr/bin/env python3
"""SVG (no deps): smallest polyplets whose bottom-left corner cell c is a CUT
VERTEX. Exact unit squares -> edge-touch (shared side) vs corner-touch (meet at a
point, king adjacency) are geometrically correct."""
import sys

C = (0, 0)
CASES = [
    ("Case {E, NW}   (n=3)",     {(-1,1):'NW', (0,0):'c', (1,0):'E'}),
    ("Case {NE, NW}   (n=3)",    {(-1,1):'NW', (0,0):'c', (1,1):'NE'}),
    ("Case {E, NE, NW}   (n=4)", {(-1,1):'NW', (0,0):'c', (1,0):'E', (1,1):'NE'}),
]
FORBIDDEN = {(-1,0):'W', (-1,-1):'SW', (0,-1):'S', (1,-1):'SE'}
PIECE = ['#3a7bd5', '#e8833a', '#4aa96c', '#a05fc0']

def king_components(cells):
    cells = set(cells); seen = set(); comps = []
    for s in cells:
        if s in seen: continue
        comp = []; st = [s]; seen.add(s)
        while st:
            x, y = st.pop(); comp.append((x, y))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx == dy == 0: continue
                    p = (x+dx, y+dy)
                    if p in cells and p not in seen: seen.add(p); st.append(p)
        comps.append(comp)
    return comps

S = 48            # cell px
XMIN, XMAX, YMIN, YMAX = -1, 1, -1, 1
PW = (XMAX-XMIN+1)*S            # panel grid width  (3 cells)
PH = (YMAX-YMIN+1)*S           # panel grid height (3 cells)
TITLE_H = 46
PANEL_W = PW + 56
PANEL_H = PH + TITLE_H + 10
GAP = 26; SIDE = 34

def cellxy(px, py, x, y):
    return px + (x - XMIN)*S, py + (YMAX - y)*S     # SVG y-down flip

def panel(px, py, cd, remove_c, title):
    out = []
    tx = px + PANEL_W/2
    out.append(f'<text x="{tx}" y="{py+18}" font-size="13.5" font-weight="bold" '
               f'text-anchor="middle" fill="#222">{title}</text>')
    sub = f"remove c → {len(king_components({k for k in cd if not(remove_c and k==C)}))} pieces" \
          if remove_c else "polyplet: c bridges everything"
    out.append(f'<text x="{tx}" y="{py+37}" font-size="12.5" text-anchor="middle" '
               f'fill="#666">{sub}</text>')
    gy = py + TITLE_H
    cells = {k: v for k, v in cd.items() if not (remove_c and k == C)}
    comp_of = {c: i for i, comp in enumerate(king_components(cells)) for c in comp}
    # light grid
    for x in range(XMIN, XMAX+1):
        for y in range(YMIN, YMAX+1):
            sx, sy = cellxy(px+12, gy, x, y)
            out.append(f'<rect x="{sx}" y="{sy}" width="{S}" height="{S}" '
                       f'fill="none" stroke="#eee" stroke-width="1"/>')
    if not remove_c:
        for (x, y), nm in FORBIDDEN.items():
            sx, sy = cellxy(px+12, gy, x, y)
            out.append(f'<rect x="{sx+3}" y="{sy+3}" width="{S-6}" height="{S-6}" '
                       f'fill="none" stroke="#c9c9c9" stroke-width="1.5" stroke-dasharray="4 3"/>')
            out.append(f'<text x="{sx+S/2}" y="{sy+S/2+4}" font-size="11" '
                       f'text-anchor="middle" fill="#c0c0c0">{nm}</text>')
    for (x, y), name in cells.items():
        sx, sy = cellxy(px+12, gy, x, y)
        if (not remove_c) and (x, y) == C: fc = '#d9534f'
        elif remove_c: fc = PIECE[comp_of[(x, y)] % len(PIECE)]
        else: fc = '#9ec5e8'
        out.append(f'<rect x="{sx}" y="{sy}" width="{S}" height="{S}" fill="{fc}" '
                   f'stroke="#111" stroke-width="2.5"/>')
        out.append(f'<text x="{sx+S/2}" y="{sy+S/2+6}" font-size="18" '
                   f'font-weight="bold" text-anchor="middle" fill="white">{name}</text>')
    return "\n".join(out)

BLOCK = 2*PANEL_W + GAP
W = max(BLOCK + 2*SIDE, 660)
PX0 = (W - BLOCK)/2
H = 44 + 3*PANEL_H
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'font-family="sans-serif" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       f'<text x="{W/2}" y="26" font-size="15" font-weight="bold" text-anchor="middle" '
       f'fill="#111">Smallest polyplets where corner cell c is a CUT VERTEX</text>']
for r, (title, cd) in enumerate(CASES):
    py = 44 + r*PANEL_H
    svg.append(panel(PX0, py, cd, False, title))
    svg.append(panel(PX0+PANEL_W+GAP, py, cd, True, title))
svg.append('</svg>')
out = sys.argv[1] if len(sys.argv) > 1 else "cut_examples.svg"
open(out, "w").write("\n".join(svg))
print("wrote", out)
