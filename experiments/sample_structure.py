"""Structural analysis of the existing 10k uniform n=19 polyplet samples
(results/a19_samples.txt) -- no new sampling. Covers three enqueued items at once:
  #15 rook-component count distribution
  #13 hole-AREA distribution (not just #holes): primary 4-connected background
  #17 gluing-graph: nodes=rook-components, edges=diagonal adjacencies between them;
      is it a tree (cycles = E-V+1 = 0)?
"""
import sys
from collections import defaultdict, Counter

def specimens(path):
    rows=None; H=0
    for line in open(path):
        line=line.rstrip("\n")
        if line.startswith("# specimen"):
            parts=line.split(); H=int(parts[parts.index("height")+1]); rows=[]; need=H
        elif rows is not None and need>0 and line and line[0] in ".#":
            rows.append(line); need-=1
            if need==0:
                yield rows; rows=None
class DSU:
    def __init__(s,n): s.p=list(range(n))
    def f(s,x):
        while s.p[x]!=x: s.p[x]=s.p[s.p[x]]; x=s.p[x]
        return x
    def u(s,a,b): s.p[s.f(a)]=s.f(b)

def analyze(rows):
    cells={(r,c) for r,row in enumerate(rows) for c,ch in enumerate(row) if ch=='#'}
    idx={cell:i for i,cell in enumerate(cells)}; n=len(cells)
    # rook components (4-adj)
    d=DSU(n)
    for (r,c) in cells:
        for dr,dc in ((1,0),(0,1)):
            if (r+dr,c+dc) in cells: d.u(idx[(r,c)],idx[(r+dr,c+dc)])
    comp={cell:d.f(idx[cell]) for cell in cells}
    roots=set(comp.values()); ncomp=len(roots)
    # gluing graph: edges between distinct rook-comps via diagonal adjacency
    edges=set()
    for (r,c) in cells:
        for dr,dc in ((1,1),(1,-1),(-1,1),(-1,-1)):
            o=(r+dr,c+dc)
            if o in cells and comp[o]!=comp[(r,c)]:
                edges.add(frozenset((comp[(r,c)],comp[o])))
    E=len(edges); cycles=E-ncomp+1   # connected king-animal => one component
    # holes: 4-connected empty regions not reachable from exterior
    minr=min(r for r,_ in cells); maxr=max(r for r,_ in cells)
    minc=min(c for _,c in cells); maxc=max(c for _,c in cells)
    seen=set(); stack=[]
    # seed exterior from expanded-box border
    for r in range(minr-1,maxr+2):
        for c in (minc-1,maxc+1):
            if (r,c) not in cells: stack.append((r,c)); seen.add((r,c))
    for c in range(minc-1,maxc+2):
        for r in (minr-1,maxr+1):
            if (r,c) not in cells and (r,c) not in seen: stack.append((r,c)); seen.add((r,c))
    while stack:
        r,c=stack.pop()
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            o=(r+dr,c+dc)
            if minr-1<=o[0]<=maxr+1 and minc-1<=o[1]<=maxc+1 and o not in cells and o not in seen:
                seen.add(o); stack.append(o)
    hole_areas=[]
    interior=set()
    for r in range(minr,maxr+1):
        for c in range(minc,maxc+1):
            if (r,c) not in cells and (r,c) not in seen: interior.add((r,c))
    # group interior empties into 4-connected hole regions
    hidx={cell:i for i,cell in enumerate(interior)}; hd=DSU(len(interior))
    for (r,c) in interior:
        for dr,dc in ((1,0),(0,1)):
            if (r+dr,c+dc) in interior: hd.u(hidx[(r,c)],hidx[(r+dr,c+dc)])
    hsz=Counter()
    for cell in interior: hsz[hd.f(hidx[cell])]+=1
    hole_areas=list(hsz.values())
    return ncomp, cycles, hole_areas

def main():
    path="results/a19_samples.txt"
    comps=Counter(); cyc=Counter(); harea=Counter(); nspec=0; treecnt=0
    for rows in specimens(path):
        nc,cy,ha=analyze(rows); nspec+=1
        comps[nc]+=1; cyc[cy]+=1
        if cy==0: treecnt+=1
        for a in ha: harea[a]+=1
    print(f"n=19, {nspec} specimens")
    print("#15 rook-component count: mean=%.3f  dist=%s" %
          (sum(k*v for k,v in comps.items())/nspec, dict(sorted(comps.items()))))
    print("#17 gluing-graph cycles (E-V+1): mean=%.4f  tree-fraction=%.4f  dist=%s" %
          (sum(k*v for k,v in cyc.items())/nspec, treecnt/nspec, dict(sorted(cyc.items()))))
    tot=sum(harea.values())
    print("#13 hole-area dist (area:count, frac): total holes=%d, mean area=%.3f" %
          (tot, sum(k*v for k,v in harea.items())/tot if tot else 0))
    for a,c in sorted(harea.items()):
        print(f"     area {a:2d}: {c:5d}  ({100*c/tot:.1f}%)")

main()
