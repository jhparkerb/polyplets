#!/usr/bin/env python3
"""Figure: the T(n,H) triangle, n <= 40, each cell coloured by what checked it.

The classes come from scripts/provenance_table.sources(), the gated per-cell
table, so the picture cannot disagree with results/provenance-table.md.  Five
classes in priority order: enumerated once (the congruence-only cells), the
Redelmeier recount (n <= 22), the colouring transfer matrix Motley (H <= 19),
a wired closed form on a really-swept cell (H = 20, 21), and an injected closed
form (H >= 22).  Every cell also carries the mod-2 parity census.

Emits results/figs/triangle_provenance.svg; convert with
  rsvg-convert --zoom 2 -o results/figs/triangle_provenance.png <svg>
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import provenance_table as pt  # noqa: E402

N = pt.NMAX
CELL, GAP = 18, 2
STEP = CELL + GAP
ML, MT = 64, 96
W = ML + N * STEP + 450
Hh = MT + N * STEP + 60
INK, MUT = "#1F2937", "#6B7280"

CLASSES = [  # (key, fill, legend text); first match wins
    ("once", "#D97706", "enumerated once, the mod-2 parity its only other check"),
    ("B", "#2D5DB8", "Redelmeier recount, n ≤ 22"),
    ("M", "#93B4EC", "colouring transfer matrix (Motley), H ≤ 19"),
    ("P", "#DCE6F8", "wired closed form on a really-swept cell, H = 20, 21"),
    ("F", "#F3F4F6", "injected closed form, H ≥ 22, holdout-validated elsewhere"),
]


def cls(n, h):
    s = pt.sources(n, h)
    exact = s - {"C", "F", "U"}
    if not exact and "F" not in s:
        return "once"
    for key, _, _ in CLASSES[1:]:
        if key in s:
            return key
    raise SystemExit(f"cell ({n},{h}) has no class: {s}")


count = {k: 0 for k, _, _ in CLASSES}
fill = dict((k, f) for k, f, _ in CLASSES)
once = []
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
     f'<rect width="{W}" height="{Hh}" fill="#FFFFFF"/>',
     f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">T(n,H), n ≤ {N}: what checked each cell</text>',
     f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">colour = the strongest check on the cell; every cell also passes the mod-2 parity census (results/subgroup-mod4.md)</text>',
     f'<text x="{ML + N * STEP / 2}" y="{MT - 20}" font-size="13" fill="{MUT}" text-anchor="middle">height H →</text>',
     f'<text x="20" y="{MT + N * STEP / 2}" font-size="13" fill="{MUT}" text-anchor="middle" transform="rotate(-90 20 {MT + N * STEP / 2})">cells n ↓</text>']
for v in range(5, N + 1, 5):
    s.append(f'<text x="{ML + (v - 1) * STEP + CELL / 2}" y="{MT - 8}" font-size="11" fill="{MUT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{ML - 8}" y="{MT + (v - 1) * STEP + CELL / 2 + 4}" font-size="11" fill="{MUT}" text-anchor="end">{v}</text>')
for n in range(1, N + 1):
    for h in range(1, n + 1):
        k = cls(n, h)
        count[k] += 1
        if k == "once":
            once.append(f"T({n},{h})")
        x, y = ML + (h - 1) * STEP, MT + (n - 1) * STEP
        s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill[k]}"/>')

# the closed-form boundary H > n/2, i.e. n <= 2H - 1, as a staircase
pts = []
for h in range(1, N + 1):
    nb = min(2 * h - 1, N)
    yb = MT + nb * STEP - GAP / 2
    pts += [(ML + (h - 1) * STEP - GAP / 2, yb), (ML + h * STEP - GAP / 2, yb)]
    if 2 * h - 1 >= N:
        break
s.append('<path d="M ' + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
         + f'" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5,4" opacity="0.7"/>')

ax = ML + N * STEP + 16
y = MT + 4
s.append(f'<text x="{ax}" y="{y}" font-size="13" font-weight="bold" fill="{INK}">cells, by check</text>')
for key, f, text in CLASSES:
    y += 26
    s.append(f'<rect x="{ax}" y="{y - 13}" width="16" height="16" rx="2" fill="{f}" stroke="#D1D5DB" stroke-width="0.5"/>')
    s.append(f'<text x="{ax + 24}" y="{y}" font-size="12" fill="{INK}"><tspan font-weight="bold">{count[key]}</tspan>  {text}</text>')
y += 34
for line in ("dashed staircase: H > n/2, the cells with a closed form",
             "orange cells: " + ", ".join(once),
             "they and every injected cell are also reproduced by the",
             "tower fitted to Motley's cells (tag U, a formula-level check)",
             "",
             f"total {sum(count.values())} cells; source: scripts/provenance_table.py"):
    s.append(f'<text x="{ax}" y="{y}" font-size="11.5" fill="{MUT}">{line}</text>')
    y += 17
s.append("</svg>")

out = os.path.join(ROOT, "results", "figs", "triangle_provenance.svg")
open(out, "w").write("\n".join(s))
print("wrote", out, "cells", count)
