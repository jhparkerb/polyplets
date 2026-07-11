#!/usr/bin/env python3
"""Auto-derive the king twig type-system, class by class, VERIFYING every
reduction against brute-force counts. A 'type' = frozenset of forbidden king
offsets around the marked cell c=(0,0). Reduction of a leaf case S (occupied
free-cells): remove c, re-mark u = lowest-then-leftmost cell of S, and the new
type's forbidden set = the locally known-empty cells around u (R=1 window). The
'discard distant' relaxation makes each reduction an OVER-count (<=), which we
confirm numerically. Cut cases (c a cut vertex) are flagged for convolution.
"""
from experiments.king_types import all_polyplets, type_count, OFF

KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
NAME = {v:k for k,v in OFF.items()}
def nm(offs): return "{"+",".join(sorted(NAME[o] for o in offs))+"}"

def free_cells(forbidden): return [d for d in KING8 if d not in forbidden]

def cluster_components(S):
    S=set(S); seen=set(); comps=[]
    for s in S:
        if s in seen: continue
        c=[]; st=[s]; seen.add(s)
        while st:
            p=st.pop(); c.append(p)
            for q in S:
                if q not in seen and max(abs(p[0]-q[0]),abs(p[1]-q[1]))==1:
                    seen.add(q); st.append(q)
        comps.append(c)
    return comps

def known_empty(forbidden, S):
    fc=set(free_cells(forbidden))
    return set(forbidden) | (fc-set(S)) | {(0,0)}

def reduce_leaf(forbidden, S):
    u=min(S, key=lambda p:(p[1],p[0]))          # lowest then leftmost
    ke=known_empty(forbidden, S)
    Tp=frozenset(o for o in KING8 if (u[0]+o[0], u[1]+o[1]) in ke)
    return u, Tp

def decompose(forbidden):
    """Return (leaf_terms, cut_cases). leaf_terms: list of (S, u, reduced_type)."""
    fc=free_cells(forbidden)
    leaf=[]; cut=[]
    for mask in range(1, 1<<len(fc)):
        S=[fc[i] for i in range(len(fc)) if mask>>i & 1]
        if len(cluster_components(S))==1:
            leaf.append((S,)+reduce_leaf(forbidden, S))
        else:
            cut.append(S)
    return leaf, cut

if __name__=="__main__":
    lv=all_polyplets(9)
    G8=frozenset({OFF[o] for o in ('W','SW','S','SE')})
    leaf, cut = decompose(G8)
    print(f"G8 = forbid {nm(G8)}   free = {nm(free_cells(G8))}")
    print(f"  {len(leaf)} leaf cases, {len(cut)} cut cases\n")
    print("LEAF cases:  S (occupied)            -> re-mark u ,  reduced type")
    types=set()
    for S,u,Tp in leaf:
        types.add(Tp)
        print(f"   {nm(S):22} u={NAME[u]:3} -> forbid {nm(Tp)}")
    print("\nCUT cases (need convolution):")
    for S in cut:
        print(f"   {nm(S)}   components: {[[NAME[c] for c in comp] for comp in cluster_components(S)]}")

    # verify: sum of leaf case_counts <= sum of reduced_type(n-1)
    print("\nNumerical check of leaf reductions (each case_count(n) <= Tp(n-1)):")
    def case_count(forbidden, S):
        forb=tuple(free_cells(forbidden)) # cells not forbidden and not in S must be empty
        empt=[o for o in free_cells(forbidden) if o not in S]
        return type_count(lv, forbid=tuple(forbidden)+tuple(empt), require=tuple(S))
    all_ok=True
    for S,u,Tp in leaf:
        cc=case_count(G8,S)
        Tc=type_count(lv, forbid=tuple(Tp))
        ok=all(cc[n] <= Tc[n-1] for n in range(2,10))
        all_ok &= ok
        print(f"   {nm(S):22} {'OK' if ok else 'FAIL'}   cc(9)={cc[9]}  Tp(8)={Tc[8]}")
    print("\nALL leaf reductions valid over-counts:", all_ok)
    print("distinct reduced types discovered:", len(types))
