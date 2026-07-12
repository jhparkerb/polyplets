#!/usr/bin/env python3
"""Figure: the height triangle T(n,H) with the diagonal-law band shaded.

Regions: white H>n (structurally empty); light blue H <= n <= 2H-1 (the
diagonal-law regime, where the spine cubic W^3 = W^2 + t governs T mod 3 --
results/ternary-spine.md); dark blue spine n = floor(3H/2) (each column's first
nonzero entry mod 3, always == 1); gray n >= 2H (outside the law).

Emits SVG; convert with  rsvg-convert --zoom 2 -o results/figs/spine_triangle.png
Colors CVD-validated (dataviz skill validator: worst adjacent pair dE 31.6).
"""
N=36; CELL=20; GAP=2; STEP=CELL+GAP
ML,MT = 64, 96
W = ML + N*STEP + 260
Hh = MT + N*STEP + 150
BAND="#AECBFA"; SPINE="#2D5DB8"; OUT="#9CA3AF"; INK="#1F2937"; MUT="#6B7280"; SURF="#FFFFFF"
def pk(sz=12.5):
    return f'P<tspan font-size="{sz*0.72:.1f}" baseline-shift="-22%">k</tspan>'
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" font-family="Helvetica,Arial,sans-serif">',
   f'<rect width="{W}" height="{Hh}" fill="{SURF}"/>',
   f'<text x="{ML}" y="34" font-size="22" font-weight="bold" fill="{INK}">The height triangle T(n,H) and the reach of the spine cubic</text>',
   f'<text x="{ML}" y="58" font-size="14" fill="{MUT}">rows n = cells, columns H = bounding-box height; shaded band = diagonal-law regime, where W&#179; = W&#178; + t governs T(n,H) mod 3</text>']
s.append(f'<text x="{ML + N*STEP/2}" y="{MT-26}" font-size="13" fill="{MUT}" text-anchor="middle">height H &#8594;</text>')
s.append(f'<text x="20" y="{MT + N*STEP/2}" font-size="13" fill="{MUT}" text-anchor="middle" transform="rotate(-90 20 {MT+N*STEP/2})">cells n &#8595;</text>')
for v in range(5,N+1,5):
    s.append(f'<text x="{ML+(v-1)*STEP+CELL/2}" y="{MT-8}" font-size="11" fill="{MUT}" text-anchor="middle">{v}</text>')
    s.append(f'<text x="{ML-8}" y="{MT+(v-1)*STEP+CELL/2+4}" font-size="11" fill="{MUT}" text-anchor="end">{v}</text>')
for n in range(1,N+1):
    for H in range(1,n+1):
        x=ML+(H-1)*STEP; y=MT+(n-1)*STEP
        spine = (n == (3*H)//2)
        band  = (n <= 2*H-1)
        fill = SPINE if spine else (BAND if band else OUT)
        op   = '1' if (spine or band) else '0.55'
        s.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{fill}" opacity="{op}"/>')
gx=ML+6.5*STEP; gy=MT+29.5*STEP
s.append(f'<text x="{gx}" y="{gy}" font-size="15" font-weight="bold" fill="{INK}">outside the law</text>')
s.append(f'<text x="{gx}" y="{gy+18}" font-size="13" fill="{INK}">(n &#8805; 2H)</text>')
bx=ML+18.6*STEP; by=MT+25.4*STEP
s.append(f'<text x="{bx}" y="{by}" font-size="15" font-weight="bold" fill="{INK}" transform="rotate(56 {bx} {by})">diagonal-law band: H &#8804; n &#8804; 2H&#8722;1</text>')
ax=ML+N*STEP+14
def note(y,c,txt,bold=False):
    return f'<text x="{ax}" y="{y}" font-size="12.5" fill="{c}" font-weight="{"bold" if bold else "normal"}">{txt}</text>'
s+= [note(MT+10, INK,'n = H diagonal:',True), note(MT+26, MUT,'T(H,H) = 3<tspan font-size="9" baseline-shift="30%">H&#8722;1</tspan>'),
     note(MT+58, SPINE,'spine  n = &#8970;3H/2&#8971;:',True), note(MT+74, MUT,'first entry &#8802; 0 mod 3'), note(MT+90, MUT,'in each column; always &#8801; 1'),
     note(MT+122, INK,'band  H &#8804; n &#8804; 2H&#8722;1:',True), note(MT+138, MUT,f'T(n,n&#8722;k) = {pk()}(n)&#183;3<tspan font-size="9" baseline-shift="30%">n&#8722;1&#8722;3k</tspan>'),
     note(MT+154, MUT,f'{pk()}(n) mod 3 comes from the'), note(MT+170, MUT,'base-3 digit product in W'),
     note(MT+202, INK,'gray  n &#8805; 2H:',True), note(MT+218, MUT,'squat animals; outside'), note(MT+234, MUT,'the diagonal law'),
     note(MT+266, INK,'white  H &gt; n:',True), note(MT+282, MUT,'no animals (an animal is'), note(MT+298, MUT,'at most n rows tall)')]
ly=MT+N*STEP+34
def sw(x,color,op='1'): return f'<rect x="{x}" y="{ly-13}" width="16" height="16" rx="3" fill="{color}" opacity="{op}"/>'
s.append(sw(ML,BAND)+f'<text x="{ML+24}" y="{ly}" font-size="13" fill="{INK}">diagonal-law band (spine cubic governs mod 3)</text>')
s.append(sw(ML+360,SPINE)+f'<text x="{ML+384}" y="{ly}" font-size="13" fill="{INK}">spine n=&#8970;3H/2&#8971; (first nonzero mod 3, &#8801;1)</text>')
s.append(sw(ML+710,OUT,'0.55')+f'<text x="{ML+734}" y="{ly}" font-size="13" fill="{INK}">outside the law</text>')
s.append(f'<text x="{ML}" y="{ly+30}" font-size="12" fill="{MUT}">W&#179; = W&#178; + t over GF(3);  T(n,n&#8722;k) = {pk(12)}(n)&#183;3<tspan font-size="8.6" baseline-shift="30%">n&#8722;1&#8722;3k</tspan> for n &#8804; 2H&#8722;1;  n,H &#8804; 36 shown (banked range)</text>')
s.append('</svg>')
import os
out=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"results","figs","spine_triangle.svg")
open(out,'w').write('\n'.join(s))
print("wrote", out)
