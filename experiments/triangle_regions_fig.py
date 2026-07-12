#!/usr/bin/env python3
"""Figure: the T(n,H) triangle — what is closed-form vs computed, with the
data-flow arrows: column-TM sweeps, diagonal-law propagation, row sums.

Regions: simple exact formulas (H=1 column, n=H diagonal), the diagonal-law
band n <= 2H-1 (P_k pinned k<=17 covers every band cell for n<=36; k<=3
additionally derived ab initio from cluster weights), and the outside where
no closed form exists (TM/enumeration only). The P_17 fit/holdout trio is
outlined. Colors from the CVD-validated palette of the spine figures.

Emits results/figs/triangle_regions.svg; convert with
  rsvg-convert --zoom 2 -o results/figs/triangle_regions.png <svg>
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 36; CELL = 20; GAP = 2; STEP = CELL + GAP
ML, MT = 64, 96
W = ML + N * STEP + 300
Hh = MT + N * STEP + 150
BAND_DERIVED = "#93B4EC"   # law band, k <= 3: P_k derived from cluster weights
BAND_PINNED = "#E2E9F7"    # law band, 4 <= k <= 17: P_k pinned by fits
SIMPLE = "#EDAE6B"         # one-line closed forms: H=1, n=H
OUTSIDE = "#F3F4F6"        # no closed form: TM/enumeration only
INK = "#1F2937"; MUT = "#6B7280"; BLUE = "#2D5DB8"; ORG = "#D97706"
SUB_K = '<tspan font-size="9.5" dy="3.5">k</tspan><tspan dy="-3.5">&#8203;</tspan>'
SUP_EXP = '<tspan font-size="9.5" dy="-4.5">n&#8722;1&#8722;3k</tspan><tspan dy="4.5">&#8203;</tspan>'


def cx(Hc): return ML + (Hc - 1) * STEP + CELL / 2
def cy(n):  return MT + (n - 1) * STEP + CELL / 2

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
     '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
     '<path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>',
     f'<rect width="{W}" height="{Hh}" fill="#FFFFFF"/>',
     f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">T(n,H): closed forms, and where the numbers flow</text>',
     f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">regions = what covers each cell; arrows = how cells are computed or implied</text>',
     f'<text x="{ML + N*STEP/2}" y="{MT-26}" font-size="13" fill="{MUT}" text-anchor="middle">height H &#8594;</text>',
     f'<text x="20" y="{MT + N*STEP/2}" font-size="13" fill="{MUT}" text-anchor="middle" transform="rotate(-90 20 {MT+N*STEP/2})">cells n &#8595;</text>']
for v in range(5, N + 1, 5):
    s.append(f'<text x="{cx(v)}" y="{MT-8}" font-size="11" fill="{MUT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{ML-8}" y="{cy(v)+4}" font-size="11" fill="{MUT}" text-anchor="end">{v}</text>')

for n in range(1, N + 1):
    for Hc in range(1, n + 1):
        x = ML + (Hc - 1) * STEP; y = MT + (n - 1) * STEP
        if Hc == 1 or Hc == n:
            fill = SIMPLE
        elif n <= 2 * Hc - 1:
            fill = BAND_DERIVED if n - Hc <= 3 else BAND_PINNED
        else:
            fill = OUTSIDE
        s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}"/>')

# P17 fit/holdout trio outlined: (34,17) (35,18) (36,19)
for n, Hc in ((34, 17), (35, 18), (36, 19)):
    x = ML + (Hc - 1) * STEP; y = MT + (n - 1) * STEP
    s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="none" stroke="{ORG}" stroke-width="2.4"/>')

# dashed law boundary n = 2H-1
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
s.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6,4" opacity="0.8"/>')

# ARROW 1: column-TM sweep down column H=12 (computes ALL n in one sweep)
x = cx(12)
s.append(f'<line x1="{x}" y1="{cy(13)-6}" x2="{x}" y2="{cy(35)+6}" stroke="{INK}" stroke-width="2.6" opacity="0.85" marker-end="url(#arr)"/>')
s.append(f'<text x="{x+8}" y="{cy(28)}" font-size="12" font-weight="bold" fill="{INK}" transform="rotate(-90 {x+8} {cy(28)})" text-anchor="middle">TM sweep: one run per column</text>')

# ARROW 2: diagonal-law propagation along k = 8 (onset (17,9) -> (36,28))
s.append(f'<line x1="{cx(9)}" y1="{cy(17)}" x2="{cx(27.6)}" y2="{cy(35.6)}" stroke="{BLUE}" stroke-width="2.6" opacity="0.9" marker-end="url(#arr)"/>')
s.append(f'<text x="{cx(20)+10}" y="{cy(26)-8}" font-size="12" font-weight="bold" fill="{BLUE}" transform="rotate(45 {cx(20)+10} {cy(26)-8})" text-anchor="middle">P' + '<tspan font-size="9" dy="3">8</tspan><tspan dy="-3"> law: onset cells imply the diagonal</tspan>' + '</text>')

# ARROW 3: row sum -> a(n), row n=32
y = cy(32)
s.append(f'<line x1="{ML + 32*STEP + 2}" y1="{y}" x2="{ML + 32*STEP + 58}" y2="{y}" stroke="{INK}" stroke-width="2.6" opacity="0.85" marker-end="url(#arr)"/>')
s.append(f'<text x="{ML + 32*STEP + 64}" y="{y+4}" font-size="12" font-weight="bold" fill="{INK}">&#931;<tspan font-size="9" dy="3">H</tspan><tspan dy="-3"> = a(32)</tspan></text>')

ax = ML + N * STEP + 14
def note(y, c, txt, bold=False):
    return f'<text x="{ax}" y="{y}" font-size="12.5" fill="{c}" font-weight="{"bold" if bold else "normal"}">{txt}</text>'
s += [note(MT + 10, INK, 'one-line closed forms:', True),
      note(MT + 26, MUT, 'T(n,1) = 1;  T(n,n) = 3&#8319;&#8315;&#185;'),
      note(MT + 56, INK, 'diagonal-law band (n &#8804; 2H&#8722;1):', True),
      note(MT + 72, MUT, 'T = P' + SUB_K + '(n)&#183;3' + SUP_EXP + ', k = n&#8722;H,'),
      note(MT + 88, MUT, 'deg P' + SUB_K + ' = k &#8212; SHAPE now a theorem'),
      note(MT + 104, MUT, '(docs/proofs/diagonal-law.md);'),
      note(MT + 120, MUT, 'P' + SUB_K + ' pinned k &#8804; 17: covers every'),
      note(MT + 136, MUT, 'band cell in this triangle'),
      note(MT + 158, MUT, 'darker cells k &#8804; 3: P' + SUB_K + ' derived ab'),
      note(MT + 174, MUT, 'initio from cluster weights'),
      note(MT + 204, INK, 'outside the band (n &#8805; 2H):', True),
      note(MT + 220, MUT, 'no closed form &#8212; TM/enumeration'),
      note(MT + 236, MUT, 'only; and NO bounded-depth cross-'),
      note(MT + 252, MUT, 'column recurrence exists (Atom'),
      note(MT + 268, MUT, 'Ledger root-separation theorem)'),
      note(MT + 298, INK, 'arrows (the three data flows):', True),
      note(MT + 314, MUT, 'black &#8595;: column TM computes T(&#183;,H)'),
      note(MT + 330, MUT, 'for all n in one sweep, per height'),
      note(MT + 346, MUT, 'blue &#8600;: law propagates a diagonal'),
      note(MT + 362, MUT, 'from its first k+1 cells (n &#8805; 2k+1)'),
      note(MT + 378, MUT, 'black &#8594;: row sums give a(n)'),
      note(MT + 408, INK, 'orange boxes (k = 17 diagonal):', True),
      note(MT + 424, MUT, 'P&#8321;&#8327; fit at (34,17)+(35,18),'),
      note(MT + 440, MUT, 'holdout (36,19) &#10003; &#8212; the trusted-'),
      note(MT + 456, MUT, 'P&#8321;&#8327; route to a(37) top heights'),
      note(MT + 486, INK, 'mod-3 structure:', True),
      note(MT + 502, MUT, 'see spine_triangle figures')]

ly = MT + N * STEP + 34
def sw(x, color):
    return f'<rect x="{x}" y="{ly-13}" width="16" height="16" rx="3" fill="{color}"/>'
s.append(sw(ML, SIMPLE) + f'<text x="{ML+24}" y="{ly}" font-size="13" fill="{INK}">exact one-liners</text>')
s.append(sw(ML + 160, BAND_DERIVED) + f'<text x="{ML+184}" y="{ly}" font-size="13" fill="{INK}">law, P' + SUB_K + ' derived (k&#8804;3)</text>')
s.append(sw(ML + 350, BAND_PINNED) + f'<text x="{ML+374}" y="{ly}" font-size="13" fill="{INK}">law, P' + SUB_K + ' pinned (k&#8804;17)</text>')
s.append(sw(ML + 540, OUTSIDE) + f'<text x="{ML+564}" y="{ly}" font-size="13" fill="{INK}">no closed form (TM only)</text>')
s.append(f'<text x="{ML}" y="{ly+30}" font-size="12" fill="{MUT}">dashed line: law boundary n = 2H&#8722;1; every cell shown is banked exact (n &#8804; 36)</text>')
s.append('</svg>')

out = os.path.join(ROOT, "results", "figs", "triangle_regions.svg")
open(out, 'w').write('\n'.join(s))
print("wrote", out)
