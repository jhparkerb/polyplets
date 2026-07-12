#!/usr/bin/env python3
"""Figure: the height triangle with the diagonal-law band colored by T(n,H) mod 3.

Same geometry as spine_triangle_fig.py, but band cells are colored by residue:
0 -> near-surface light blue (the 'sea of zeros' above the spine, proved),
1 -> blue, 2 -> orange; the spine n=floor(3H/2) keeps a dark outline (its cells
are all residue 1 -- the proved first-nonzero law). Gray = outside the law.
Residues read from the banked triangle (results/ns_a36/perheight/).

Emits results/figs/spine_triangle_res3.svg; convert with
  rsvg-convert --zoom 2 -o results/figs/spine_triangle_res3.png <svg>
Palette CVD-validated (worst adjacent pair dE 53.1).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = {}
for f in os.listdir(os.path.join(ROOT, "results", "ns_a36", "perheight")):
    if f.startswith('h') and f.endswith('.out'):
        Hcol = int(f[1:-4])
        for ln in open(os.path.join(ROOT, "results", "ns_a36", "perheight", f)):
            n, c = ln.split(); T[(int(n), Hcol)] = int(c)

N = 36; CELL = 20; GAP = 2; STEP = CELL + GAP
ML, MT = 64, 96
W = ML + N * STEP + 268
Hh = MT + N * STEP + 150
R0 = "#E2E9F7"; R1 = "#2D5DB8"; R2 = "#D97706"
OUT = "#9CA3AF"; INK = "#1F2937"; MUT = "#6B7280"; SURF = "#FFFFFF"

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
     f'<rect width="{W}" height="{Hh}" fill="{SURF}"/>',
     f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">T(n,H) mod 3 in the diagonal-law band</text>',
     f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">band H &#8804; n &#8804; 2H&#8722;1 colored by residue; the spine cubic W&#179; = W&#178; + t generates every colored cell</text>']
s.append(f'<text x="{ML + N*STEP/2}" y="{MT-26}" font-size="13" fill="{MUT}" text-anchor="middle">height H &#8594;</text>')
s.append(f'<text x="20" y="{MT + N*STEP/2}" font-size="13" fill="{MUT}" text-anchor="middle" transform="rotate(-90 20 {MT+N*STEP/2})">cells n &#8595;</text>')
for v in range(5, N + 1, 5):
    s.append(f'<text x="{ML+(v-1)*STEP+CELL/2}" y="{MT-8}" font-size="11" fill="{MUT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{ML-8}" y="{MT+(v-1)*STEP+CELL/2+4}" font-size="11" fill="{MUT}" text-anchor="end">{v}</text>')

for n in range(1, N + 1):
    for Hc in range(1, n + 1):
        x = ML + (Hc - 1) * STEP; y = MT + (n - 1) * STEP
        band = (n <= 2 * Hc - 1)
        spine = (n == (3 * Hc) // 2)
        if band:
            r = T[(n, Hc)] % 3
            fill = (R0, R1, R2)[r]
            stroke = f' stroke="{INK}" stroke-width="1.8"' if spine else ''
            s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}"{stroke}/>')
        else:
            s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{OUT}" opacity="0.55"/>')

gx = ML + 6.5 * STEP; gy = MT + 29.5 * STEP
s.append(f'<text x="{gx}" y="{gy}" font-size="15" font-weight="bold" fill="{INK}">outside the law</text>')
s.append(f'<text x="{gx}" y="{gy+18}" font-size="13" fill="{INK}">(n &#8805; 2H)</text>')

ax = ML + N * STEP + 14
def note(y, c, txt, bold=False):
    return f'<text x="{ax}" y="{y}" font-size="12.5" fill="{c}" font-weight="{"bold" if bold else "normal"}">{txt}</text>'
s += [note(MT + 10, INK, 'above the spine:', True),
      note(MT + 26, MUT, 'all &#8801; 0 (proved: exponent'),
      note(MT + 42, MUT, '3H&#8722;2n&#8722;1 &#8805; 1 kills the cell)'),
      note(MT + 74, INK, 'the spine n = &#8970;3H/2&#8971;:', True),
      note(MT + 90, MUT, 'outlined; always &#8801; 1 (proved'),
      note(MT + 106, MUT, 'by Lagrange inversion)'),
      note(MT + 138, INK, 'below the spine:', True),
      note(MT + 154, MUT, 'mixed residues, given by the'),
      note(MT + 170, MUT, 'base-3 digit product in W'),
      note(MT + 186, MUT, '(and deeper 3-adic layers)'),
      note(MT + 218, INK, 'n = H diagonal:', True),
      note(MT + 234, MUT, 'T(H,H) = 3<tspan font-size="9" baseline-shift="30%">H&#8722;1</tspan> &#8801; 0 for H &#8805; 2')]

ly = MT + N * STEP + 34
def sw(x, color, op='1', stroke=''):
    return f'<rect x="{x}" y="{ly-13}" width="16" height="16" rx="3" fill="{color}" opacity="{op}"{stroke}/>'
s.append(sw(ML, R0) + f'<text x="{ML+24}" y="{ly}" font-size="13" fill="{INK}">&#8801; 0 (mod 3)</text>')
s.append(sw(ML + 150, R1) + f'<text x="{ML+174}" y="{ly}" font-size="13" fill="{INK}">&#8801; 1</text>')
s.append(sw(ML + 240, R2) + f'<text x="{ML+264}" y="{ly}" font-size="13" fill="{INK}">&#8801; 2</text>')
s.append(sw(ML + 330, R1, stroke=f' stroke="{INK}" stroke-width="1.8"') + f'<text x="{ML+354}" y="{ly}" font-size="13" fill="{INK}">spine n=&#8970;3H/2&#8971; (first nonzero in its column)</text>')
s.append(sw(ML + 700, OUT, '0.55') + f'<text x="{ML+724}" y="{ly}" font-size="13" fill="{INK}">outside the law</text>')
s.append(f'<text x="{ML}" y="{ly+30}" font-size="12" fill="{MUT}">residues from the banked exact triangle (n,H &#8804; 36); every colored cell is reproduced by the digit-product formula in W (342/342)</text>')
s.append('</svg>')

out = os.path.join(ROOT, "results", "figs", "spine_triangle_res3.svg")
open(out, 'w').write('\n'.join(s))
print("wrote", out)
