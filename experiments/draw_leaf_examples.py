#!/usr/bin/env python3
"""SVG: the deciding cell is N. Contrast a CUT case with its LEAF version
(same shape + N), showing that filling N reconnects everything so c is just a
leaf. Reuses the exact-unit-square drawing so touch types are geometric."""
import sys

C = (0, 0); N = (0, 1)
CASES = [
    ("{E, NW}  -  N empty",     {(-1,1):'NW',(0,0):'c',(1,0):'E'}),
    ("{E, N, NW}  -  N filled",  {(-1,1):'NW',(0,0):'c',(0,1):'N',(1,0):'E'}),
    ("{E, NE, N, NW}  -  all four", {(-1,1):'NW',(0,0):'c',(0,1):'N',(1,1):'NE',(1,0):'E'}),
]
PIECE = ['#3a7bd5', '#e8833a', '#4aa96c', '#a05fc0']

def comps(cells):
    cells=set(cells); seen=set(); out=[]
    for s in cells:
        if s in seen: continue
        c=[]; st=[s]; seen.add(s)
        while st:
            x,y=st.pop(); c.append((x,y))
            for dx in(-1,0,1):
                for dy in(-1,0,1):
                    if dx==dy==0: continue
                    p=(x+dx,y+dy)
                    if p in cells and p not in seen: seen.add(p); st.append(p)
        out.append(c)
    return out

S=48; XMIN,XMAX,YMIN,YMAX=-1,1,-1,1
PW=(XMAX-XMIN+1)*S; PH=(YMAX-YMIN+1)*S; TH=46
PANEL_W=PW+56; PANEL_H=PH+TH+10; GAP=26; SIDE=34
def cxy(px,py,x,y): return px+(x-XMIN)*S, py+(YMAX-y)*S

def panel(px,py,cd,rm,title):
    o=[]; tx=px+PANEL_W/2
    o.append(f'<text x="{tx}" y="{py+18}" font-size="12.5" font-weight="bold" text-anchor="middle" fill="#222">{title}</text>')
    cells={k:v for k,v in cd.items() if not(rm and k==C)}
    sub=f"remove c -> {len(comps(cells))} piece(s)" if rm else "intact (c = red)"
    o.append(f'<text x="{tx}" y="{py+37}" font-size="12" text-anchor="middle" fill="#666">{sub}</text>')
    gy=py+TH; co={c:i for i,cc in enumerate(comps(cells)) for c in cc}
    for x in range(XMIN,XMAX+1):
        for y in range(YMIN,YMAX+1):
            sx,sy=cxy(px+12,gy,x,y)
            o.append(f'<rect x="{sx}" y="{sy}" width="{S}" height="{S}" fill="none" stroke="#eee" stroke-width="1"/>')
    for (x,y),name in cells.items():
        sx,sy=cxy(px+12,gy,x,y)
        if (not rm) and (x,y)==C: fc='#d9534f'
        elif rm: fc=PIECE[co[(x,y)]%len(PIECE)]
        else: fc='#9ec5e8'
        o.append(f'<rect x="{sx}" y="{sy}" width="{S}" height="{S}" fill="{fc}" stroke="#111" stroke-width="2.5"/>')
        # highlight N as "the hub"
        if (x,y)==N:
            o.append(f'<rect x="{sx-2}" y="{sy-2}" width="{S+4}" height="{S+4}" fill="none" stroke="#2e8b57" stroke-width="4"/>')
        o.append(f'<text x="{sx+S/2}" y="{sy+S/2+6}" font-size="17" font-weight="bold" text-anchor="middle" fill="white">{name}</text>')
    return "\n".join(o)

BLOCK=2*PANEL_W+GAP; W=max(BLOCK+2*SIDE, 660); PX0=(W-BLOCK)/2; TOP=70; H=TOP+3*PANEL_H
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="white"/>',
     f'<text x="{W/2}" y="24" font-size="14.5" font-weight="bold" text-anchor="middle" fill="#111">The deciding cell is N (green ring): fill it, and c stops being a bridge</text>',
     f'<text x="{W/2}" y="45" font-size="11.5" text-anchor="middle" fill="#555">Cut  &#8660;  N empty AND NW stranded  (3 cases).</text>',
     f'<text x="{W/2}" y="60" font-size="11.5" text-anchor="middle" fill="#555">N filled &#8660; leaf (8 cases).    NW absent &#8660; leaf (4 cases).</text>']
for r,(t,cd) in enumerate(CASES):
    py=TOP+r*PANEL_H
    svg.append(panel(PX0,py,cd,False,t)); svg.append(panel(PX0+PANEL_W+GAP,py,cd,True,t))
svg.append('</svg>')
out=sys.argv[1] if len(sys.argv)>1 else "leaf_examples.svg"
open(out,"w").write("\n".join(svg)); print("wrote",out)
