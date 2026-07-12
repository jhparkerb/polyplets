#!/usr/bin/env python3
"""Figure: the T(n,H) triangle as the a(36) TM production run saw it —
which columns were really swept, which were derived, and the data flows.

From results/ns_a36/PROVENANCE.md: ayr swept heights 1-18 (1.94h wall),
dalby swept height 19 alone (the long pole, 3.28h), and heights 20-36 were
derived from wired P_k closed forms (k = 36-H <= 16), anchored at onset
cells inside the real region. T(36,19) is the genuine k=17 value (P_17
fit+holdout material). Style/palette matches triangle_regions_fig.py.

Emits results/figs/triangle_tm.svg; convert with
  rsvg-convert --zoom 2 -o results/figs/triangle_tm.png <svg>
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 36; CELL = 20; GAP = 2; STEP = CELL + GAP
ML, MT = 64, 96
W = ML + N * STEP + 300
Hh = MT + N * STEP + 150
SWEPT = "#93B4EC"          # real TM sweeps H=1..18 (ayr)
POLE = "#2D5DB8"           # H=19 long pole (dalby)
DERIVED = "#E2E9F7"        # H=20..36 wired P_k
INK = "#1F2937"; MUT = "#6B7280"; BLUE = "#2D5DB8"; ORG = "#D97706"
SUB = lambda t: f'<tspan font-size="9.5" dy="3.5">{t}</tspan><tspan dy="-3.5">&#8203;</tspan>'
HALO = 'paint-order="stroke" stroke="#FFFFFF" stroke-width="4"'

def cx(Hc): return ML + (Hc - 1) * STEP + CELL / 2
def cy(n):  return MT + (n - 1) * STEP + CELL / 2

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
     '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
     '<path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>',
     f'<rect width="{W}" height="{Hh}" fill="#FFFFFF"/>',
     f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">The a(36) run: what the TM actually computed</text>',
     f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">one real sweep per column up to H = 19; every taller column derived from the diagonal law, anchored in the swept region</text>',
     f'<text x="{ML + N*STEP/2}" y="{MT-26}" font-size="13" fill="{MUT}" text-anchor="middle">height H &#8594;</text>',
     f'<text x="20" y="{MT + N*STEP/2}" font-size="13" fill="{MUT}" text-anchor="middle" transform="rotate(-90 20 {MT+N*STEP/2})">cells n &#8595;</text>']
for v in range(5, N + 1, 5):
    s.append(f'<text x="{cx(v)}" y="{MT-8}" font-size="11" fill="{MUT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{ML-8}" y="{cy(v)+4}" font-size="11" fill="{MUT}" text-anchor="end">{v}</text>')

for n in range(1, N + 1):
    for Hc in range(1, n + 1):
        x = ML + (Hc - 1) * STEP; y = MT + (n - 1) * STEP
        fill = SWEPT if Hc <= 18 else (POLE if Hc == 19 else DERIVED)
        s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}"/>')

# dashed law boundary n = 2H-1 (context, light)
pts = []
for Hc in range(1, N + 1):
    nb = min(2 * Hc - 1, N)
    xl = ML + (Hc - 1) * STEP - GAP / 2
    xr = ML + Hc * STEP - GAP / 2
    yb = MT + nb * STEP - GAP / 2
    pts.append((xl, yb)); pts.append((xr, yb))
    if 2 * Hc - 1 >= N:
        break
path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
s.append(f'<path d="{path}" fill="none" stroke="{MUT}" stroke-width="1.6" stroke-dasharray="5,4" opacity="0.65"/>')

# solid split line between H=19 and H=20
xs = ML + 19 * STEP - GAP / 2
s.append(f'<line x1="{xs}" y1="{MT + 18.4*STEP}" x2="{xs}" y2="{MT + N*STEP + 4}" stroke="{INK}" stroke-width="2.4"/>')
s.append(f'<text x="{xs-6}" y="{MT + 19.4*STEP}" font-size="12" font-weight="bold" fill="{INK}" {HALO} text-anchor="end">real sweeps &#8804; H19</text>')
s.append(f'<text x="{xs+8}" y="{MT + 19.4*STEP}" font-size="12" font-weight="bold" fill="{INK}" {HALO}>H &#8805; 20: derived, no sweep</text>')

# ARROW: one sweep per column (H=10), emits T(n,10) for all n
x = cx(10)
s.append(f'<line x1="{x}" y1="{cy(11)-6}" x2="{x}" y2="{cy(35)+6}" stroke="{INK}" stroke-width="2.6" opacity="0.85" marker-end="url(#arr)"/>')
s.append(f'<text x="{x+8}" y="{cy(27)}" font-size="12" font-weight="bold" fill="{INK}" {HALO} transform="rotate(-90 {x+8} {cy(27)})" text-anchor="middle">one sweep: all of column H in one run</text>')

# ORANGE ARROWS: P_k anchoring, onset (2k+1,k+1) -> (36,36-k), k = 4, 10, 16
for k in (4, 10, 16):
    x1, y1 = cx(k + 1), cy(2 * k + 1)
    x2, y2 = cx(36 - k) - 6, cy(36) - 6
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ORG}" stroke-width="2.4" opacity="0.9" marker-end="url(#arr)"/>')
s.append(f'<text x="{cx(17)}" y="{cy(29)-8}" font-size="12" font-weight="bold" fill="{ORG}" {HALO} transform="rotate(45 {cx(17)} {cy(29)-8})" text-anchor="middle">P{SUB("k")}&#160;wired: onset cells fill the tall columns</text>')

# highlight the genuine k=17 cell (36,19)
x = ML + 18 * STEP; y = MT + 35 * STEP
s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="none" stroke="{ORG}" stroke-width="2.6"/>')

# row-36 sum arrow
y = cy(36)
s.append(f'<line x1="{ML + 36*STEP + 2}" y1="{y}" x2="{ML + 36*STEP + 50}" y2="{y}" stroke="{INK}" stroke-width="2.6" opacity="0.85" marker-end="url(#arr)"/>')
s.append(f'<text x="{ML + 36*STEP + 56}" y="{y+4}" font-size="12" font-weight="bold" fill="{INK}">&#931;&#160;= a(36)</text>')

ax = ML + N * STEP + 14
def note(y, c, txt, bold=False):
    return f'<text x="{ax}" y="{y}" font-size="12.5" fill="{c}" font-weight="{"bold" if bold else "normal"}">{txt}</text>'
s += [note(MT + 10, INK, 'the run (2026-07-10):', True),
      note(MT + 26, MUT, 'ayr: H = 1..18 real sweeps,'),
      note(MT + 42, MUT, '1.94 h wall on 32 cores'),
      note(MT + 62, MUT, 'dalby: H = 19 alone &#8212; the long'),
      note(MT + 78, MUT, 'pole, 3.28 h on 80 cores'),
      note(MT + 98, MUT, 'H = 20..36: no sweep at all;'),
      note(MT + 114, MUT, 'derived from wired P' + SUB('k') + ','),
      note(MT + 130, MUT, 'k = 36&#8722;H &#8804; 16'),
      note(MT + 160, INK, 'why split exactly there:', True),
      note(MT + 176, MUT, 'per-column cost grows steeply'),
      note(MT + 192, MUT, 'with H (H19 alone outweighs all'),
      note(MT + 208, MUT, 'of H &#8804; 18 combined) while tall'),
      note(MT + 224, MUT, 'columns hold the fewest animals;'),
      note(MT + 240, MUT, 'H20+ is where the law is pinned,'),
      note(MT + 256, MUT, 'so the sweeps stop at H = 19'),
      note(MT + 286, INK, 'orange arrows:', True),
      note(MT + 302, MUT, 'each derived column is filled'),
      note(MT + 318, MUT, 'along its k-diagonal from the'),
      note(MT + 334, MUT, 'onset cells (n = 2k+1, 2k+2) &#8212;'),
      note(MT + 350, MUT, 'all safely inside the swept region'),
      note(MT + 380, INK, 'orange box, T(36,19):', True),
      note(MT + 396, MUT, 'genuine k = 17 value from the'),
      note(MT + 412, MUT, 'H19 sweep; with real (34,17) and'),
      note(MT + 428, MUT, '(35,18) it fits + holdouts P' + SUB('17') + ' &#8212;'),
      note(MT + 444, MUT, 'the a(37) shortcut'),
      note(MT + 474, INK, 'dashed line:', True),
      note(MT + 490, MUT, 'law boundary n = 2H&#8722;1; every'),
      note(MT + 506, MUT, 'derived cell lies inside it'),
      note(MT + 536, INK, 'result:', True),
      note(MT + 552, MUT, 'a(36) = row-36 sum, banked after'),
      note(MT + 568, MUT, 'chain-match vs a(35) triangle')]

ly = MT + N * STEP + 34
def sw(x, color):
    return f'<rect x="{x}" y="{ly-13}" width="16" height="16" rx="3" fill="{color}"/>'
s.append(sw(ML, SWEPT) + f'<text x="{ML+24}" y="{ly}" font-size="13" fill="{INK}">real sweep, ayr (H &#8804; 18)</text>')
s.append(sw(ML + 200, POLE) + f'<text x="{ML+224}" y="{ly}" font-size="13" fill="{INK}">long pole, dalby (H = 19)</text>')
s.append(sw(ML + 400, DERIVED) + f'<text x="{ML+424}" y="{ly}" font-size="13" fill="{INK}">derived via P' + SUB('k') + ' (H &#8805; 20)</text>')
s.append(f'<text x="{ML}" y="{ly+30}" font-size="12" fill="{MUT}">source: results/ns_a36/PROVENANCE.md; validation incl. T(36,36) = 3&#179;&#8309;, T(36,35) = P&#8321;(36)&#183;3&#179;&#178;, full a(1)..a(35) chain-match</text>')
s.append('</svg>')

out = os.path.join(ROOT, "results", "figs", "triangle_tm.svg")
open(out, 'w').write('\n'.join(s))
print("wrote", out)
