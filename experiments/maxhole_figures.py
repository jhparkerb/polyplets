#!/usr/bin/env python3
"""Generate SVG figures for the max-hole proof (results/maxhole-proof.md).

fig1: the extremal diamond ring (r=4, n=16, encloses 25) -- construction + the
      four diagonal walls (why king packs at 1/8).
fig2: the (II') counting -- anti-diagonal levels u=x+y, exactly two foreground
      cells per interior level, capped by the v-extremes: n = ha+hm+2, tight.
Writes results/figs/maxhole_ring.svg and results/figs/maxhole_seal.svg.
"""
import os

CELL = 34
PAD = 40


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) == r}


def interior(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) <= r - 1}


def svg_header(w, h, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="sans-serif">\n'
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
            f'<text x="{w/2}" y="24" text-anchor="middle" font-size="17" '
            f'font-weight="bold" fill="#1a1a2e">{title}</text>\n')


def cell_rect(cx, cy, x, y, fill, stroke="#c8c8d0", sw=1, extra=""):
    px = cx + x * CELL
    py = cy - y * CELL
    return (f'<rect x="{px}" y="{py}" width="{CELL}" height="{CELL}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>\n')


def fig_ring(r, path):
    D = diamond(r); H = interior(r)
    n = len(D); A = len(H)
    span = r
    w = 2 * (span + 1) * CELL + 2 * PAD + 200
    h = 2 * (span + 1) * CELL + 2 * PAD + 20
    cx = PAD + span * CELL + CELL // 2 - CELL // 2
    cx = PAD + (span) * CELL
    cy = 40 + span * CELL
    s = svg_header(w, h, f"Extremal diamond ring: n = {n} cells enclose A = {A} = round((n-2)^2/8)")
    # background grid box cells (light) for context
    for x in range(-r, r + 1):
        for y in range(-r, r + 1):
            if (x, y) not in D and (x, y) not in H:
                s += cell_rect(cx, cy, x, y, "#f4f4f8")
    for (x, y) in sorted(H):
        s += cell_rect(cx, cy, x, y, "#bfe0ff")            # hole (light blue)
    for (x, y) in sorted(D):
        s += cell_rect(cx, cy, x, y, "#2b3a67", stroke="#1a2547")  # foreground (dark)
    # legend
    lx = cx + (r + 1) * CELL + 30
    s += cell_rect(lx, cy - 20, 0, 0, "#2b3a67", stroke="#1a2547")
    s += f'<text x="{lx+CELL+8}" y="{cy}" font-size="14" fill="#222">foreground ({n} cells)</text>\n'
    s += cell_rect(lx, cy + 20, 0, 0, "#bfe0ff")
    s += f'<text x="{lx+CELL+8}" y="{cy+40}" font-size="14" fill="#222">enclosed hole ({A} cells)</text>\n'
    s += (f'<text x="{lx}" y="{cy+90}" font-size="13" fill="#555">Each side is a 45&#176; wall:</text>\n'
          f'<text x="{lx}" y="{cy+110}" font-size="13" fill="#555">seals the 4-connected</text>\n'
          f'<text x="{lx}" y="{cy+130}" font-size="13" fill="#555">background at 1 cell/step</text>\n'
          f'<text x="{lx}" y="{cy+150}" font-size="13" fill="#555">&#8594; king packs at 1/8</text>\n'
          f'<text x="{lx}" y="{cy+170}" font-size="13" fill="#555">(rook wall needs 1/16).</text>\n')
    s += "</svg>\n"
    open(path, "w").write(s)


def fig_seal(r, path):
    """Anti-diagonal levels: two foreground cells per interior u-level."""
    D = diamond(r); H = interior(r)
    n = len(D)
    ha = max(x + y for x, y in H) - min(x + y for x, y in H) + 1
    hm = max(x - y for x, y in H) - min(x - y for x, y in H) + 1
    w = 2 * (r + 1) * CELL + 2 * PAD + 240
    h = 2 * (r + 1) * CELL + 2 * PAD + 20
    cx = PAD + r * CELL
    cy = 40 + r * CELL
    s = svg_header(w, h, f"Lemma (II'): n >= ha+hm+2   ({n} = {ha}+{hm}+2, tight)")
    for (x, y) in sorted(H):
        s += cell_rect(cx, cy, x, y, "#eef4ff")
    # colour foreground by whether it is a u-extreme/v-extreme corner or a "side" cell
    umax = max(x + y for x, y in D); umin = min(x + y for x, y in D)
    for (x, y) in sorted(D):
        u = x + y
        corner = u in (umax, umin)
        fill = "#c0392b" if corner else "#2b3a67"
        s += cell_rect(cx, cy, x, y, fill, stroke="#1a2547")
    # draw a couple of anti-diagonal guide lines (u = const) through interior levels
    for u in [umin + 1, 0, umax - 1]:
        # line x+y=u across the plotted range
        x1 = -r - 1; y1 = u - x1
        x2 = r + 1; y2 = u - x2
        px1 = cx + x1 * CELL + CELL / 2; py1 = cy - y1 * CELL + CELL / 2
        px2 = cx + x2 * CELL + CELL / 2; py2 = cy - y2 * CELL + CELL / 2
        s += (f'<line x1="{px1}" y1="{py1}" x2="{px2}" y2="{py2}" '
              f'stroke="#e08a00" stroke-width="1.5" stroke-dasharray="5,4"/>\n')
    lx = cx + (r + 1) * CELL + 30
    s += cell_rect(lx, cy - 20, 0, 0, "#2b3a67", stroke="#1a2547")
    s += f'<text x="{lx+CELL+8}" y="{cy}" font-size="14" fill="#222">2 per interior u-level</text>\n'
    s += cell_rect(lx, cy + 20, 0, 0, "#c0392b", stroke="#1a2547")
    s += f'<text x="{lx+CELL+8}" y="{cy+40}" font-size="14" fill="#222">u-extreme caps</text>\n'
    s += (f'<text x="{lx}" y="{cy+90}" font-size="13" fill="#555">Dashed = anti-diagonals</text>\n'
          f'<text x="{lx}" y="{cy+110}" font-size="13" fill="#555">u = x+y = const. The hole</text>\n'
          f'<text x="{lx}" y="{cy+130}" font-size="13" fill="#555">spans ha of them; each is</text>\n'
          f'<text x="{lx}" y="{cy+150}" font-size="13" fill="#555">crossed by 2 ring cells,</text>\n'
          f'<text x="{lx}" y="{cy+170}" font-size="13" fill="#555">+2 v-caps &#8594; ha+hm+2.</text>\n')
    s += "</svg>\n"
    open(path, "w").write(s)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "results", "figs"); os.makedirs(d, exist_ok=True)
    fig_ring(4, os.path.join(d, "maxhole_ring.svg"))
    fig_seal(4, os.path.join(d, "maxhole_seal.svg"))
    print("wrote results/figs/maxhole_ring.svg and results/figs/maxhole_seal.svg")
