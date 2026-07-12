#!/usr/bin/env python3
"""Figure: the WHOLE height triangle colored by T(n,H) mod 3.

Inside the diagonal-law band (H <= n <= 2H-1): residue 0 whisper-blue, 1 strong
blue, 2 strong orange; spine cells outlined (proved structure). Outside the law
(n >= 2H): SAME whisper shade for 0, but LIGHTER blue/orange for 1/2 -- so the
lawful sleeve and the unstructured outside region can be compared at a glance.
A stepped dark line traces the law boundary. Residues from the banked triangle.

Emits results/figs/spine_triangle_res3_full.svg; convert with
  rsvg-convert --zoom 2 -o results/figs/spine_triangle_res3_full.png <svg>
CVD separation validated (worst adjacent pair dE 26.7).
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
R0 = "#E2E9F7"; R1 = "#2D5DB8"; R2 = "#D97706"      # in-band residues
R1L = "#93B4EC"; R2L = "#EDAE6B"                     # outside-the-law residues
INK = "#1F2937"; MUT = "#6B7280"; SURF = "#FFFFFF"

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
     f'<rect width="{W}" height="{Hh}" fill="{SURF}"/>',
     f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">The whole height triangle, T(n,H) mod 3</text>',
     f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">strong colors = diagonal-law band (spine cubic W&#179; = W&#178; + t); lighter colors = outside the law, where no mod-3 structure is known</text>']
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
        r = T[(n, Hc)] % 3
        fill = (R0, R1, R2)[r] if band else (R0, R1L, R2L)[r]
        stroke = f' stroke="{INK}" stroke-width="1.8"' if (band and spine) else ''
        s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}"{stroke}/>')

# stepped boundary line between band (n<=2H-1) and outside (n>=2H)
pts = []
for Hc in range(1, N + 1):
    nb = 2 * Hc - 1                      # last band row of column Hc
    if nb > N: nb = N
    xl = ML + (Hc - 1) * STEP - GAP / 2
    xr = ML + Hc * STEP - GAP / 2
    yb = MT + nb * STEP - GAP / 2
    pts.append((xl, yb)); pts.append((xr, yb))
    if 2 * Hc - 1 >= N: break
path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
s.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6,4" opacity="0.8"/>')

ax = ML + N * STEP + 14
def note(y, c, txt, bold=False):
    return f'<text x="{ax}" y="{y}" font-size="12.5" fill="{c}" font-weight="{"bold" if bold else "normal"}">{txt}</text>'
s += [note(MT + 10, INK, 'band (strong colors):', True),
      note(MT + 26, MUT, 'above the spine all &#8801; 0 (proved);'),
      note(MT + 42, MUT, 'spine outlined, &#8801; 1 (proved);'),
      note(MT + 58, MUT, 'sleeve below from the digit'),
      note(MT + 74, MUT, 'product in W + deeper layers'),
      note(MT + 106, INK, 'outside (lighter colors):', True),
      note(MT + 122, MUT, 'n &#8805; 2H, squat animals; the'),
      note(MT + 138, MUT, 'diagonal law does not apply'),
      note(MT + 154, MUT, 'and no mod-3 structure is'),
      note(MT + 170, MUT, 'known &#8212; visibly unpatterned'),
      note(MT + 202, INK, 'dashed line:', True),
      note(MT + 218, MUT, 'the law boundary n = 2H&#8722;1'),
      note(MT + 250, INK, 'column H = 1:', True),
      note(MT + 266, MUT, 'T(n,1) = 1 for all n, the'),
      note(MT + 282, MUT, 'all-&#8801;1 leftmost column')]

ly = MT + N * STEP + 34
def sw(x, color, op='1', stroke=''):
    return f'<rect x="{x}" y="{ly-13}" width="16" height="16" rx="3" fill="{color}" opacity="{op}"{stroke}/>'
s.append(sw(ML, R0) + f'<text x="{ML+24}" y="{ly}" font-size="13" fill="{INK}">&#8801; 0 (everywhere)</text>')
s.append(sw(ML + 165, R1) + f'<text x="{ML+189}" y="{ly}" font-size="13" fill="{INK}">&#8801; 1 band</text>')
s.append(sw(ML + 270, R2) + f'<text x="{ML+294}" y="{ly}" font-size="13" fill="{INK}">&#8801; 2 band</text>')
s.append(sw(ML + 375, R1L) + f'<text x="{ML+399}" y="{ly}" font-size="13" fill="{INK}">&#8801; 1 outside</text>')
s.append(sw(ML + 495, R2L) + f'<text x="{ML+519}" y="{ly}" font-size="13" fill="{INK}">&#8801; 2 outside</text>')
s.append(sw(ML + 615, R1, stroke=f' stroke="{INK}" stroke-width="1.8"') + f'<text x="{ML+639}" y="{ly}" font-size="13" fill="{INK}">spine (first nonzero in column, last in row)</text>')
s.append(f'<text x="{ML}" y="{ly+30}" font-size="12" fill="{MUT}">residues from the banked exact triangle (n,H &#8804; 36); in-band cells reproduced by the digit-product formula in W (342/342)</text>')
s.append('</svg>')

out = os.path.join(ROOT, "results", "figs", "spine_triangle_res3_full.svg")
open(out, 'w').write('\n'.join(s))
print("wrote", out)
