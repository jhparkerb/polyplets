#!/usr/bin/env python3
"""Probe: Sykes-Essam matching identity as a SERIES check, order by order.

K_8(p) - K_4(1-p) = p - 4p^2 + 4p^3 - p^4   (per-site mean cluster numbers)

K_8(p)   = sum over fixed king animals  g8[n][t] p^n (1-p)^t   (t = king site perimeter)
K_4(1-p) = sum over fixed rook animals  g4[s][t] (1-p)^s p^t   (t = rook site perimeter)

To check to order p^M: king animals n <= M (all perimeters), rook animals with
site perimeter t <= M (all sizes s; min rook site perimeter grows ~sqrt(8s),
so s <= ((M-2)^2+4)/8 suffices, Sieben 2008 eps(s) = ceil(2+sqrt(8s-4))).
"""
import sys
from math import comb
from collections import defaultdict

KING = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
ROOK = [(1,0),(-1,0),(0,1),(0,-1)]

def enumerate_fixed(deltas, max_n):
    """Redelmeier: fixed animals counted by (size, site-perimeter)."""
    g = defaultdict(int)
    sys.setrecursionlimit(100000)
    def lt_origin(c):
        return c[0] < 0 or (c[0] == 0 and c[1] < 0)
    def nbrs(c):
        return [(c[0]+dy, c[1]+dx) for dy,dx in deltas]
    cluster = []
    cluster_set = set()
    blocked = set()

    def record():
        per = set()
        for c in cluster:
            for nb in nbrs(c):
                if nb not in cluster_set:
                    per.add(nb)
        g[(len(cluster), len(per))] += 1

    def rec(untried):
        while untried:
            c = untried.pop()
            cluster.append(c); cluster_set.add(c)
            record()
            if len(cluster) < max_n:
                new = [nb for nb in nbrs(c)
                       if nb not in blocked and not lt_origin(nb)]
                blocked.update(new)
                rec(untried + new)
                blocked.difference_update(new)
            cluster.pop(); cluster_set.discard(c)
            # c stays blocked: it entered `blocked` when its creator added it,
            # and the creator unblocks it after this whole call returns.

    origin = (0,0)
    blocked.add(origin)
    first = [nb for nb in nbrs(origin) if not lt_origin(nb)]
    blocked.update(first)
    cluster.append(origin); cluster_set.add(origin)
    record()
    if max_n > 1:
        rec(list(first))
    return dict(g)

M = int(sys.argv[1]) if len(sys.argv) > 1 else 9

gk = enumerate_fixed(KING, M)
smax = ((M-2)**2 + 4)//8
gr = enumerate_fixed(ROOK, smax)

king_totals = defaultdict(int); rook_totals = defaultdict(int)
for (n,t),c in gk.items(): king_totals[n] += c
for (s,t),c in gr.items(): rook_totals[s] += c
MERTENS_KING = [1,4,20,110,638,3832,23592,147941,940982,6053180]
A001168 = [1,2,6,19,63,216,760,2725,9910,36446]
kt = [king_totals[i] for i in range(1,M+1)]
rt = [rook_totals[i] for i in range(1,smax+1)]
print("king totals:", kt, "match-published:", kt == MERTENS_KING[:M])
print("rook totals:", rt, "match-A001168:", rt == A001168[:smax])

coeff = [0]*(M+1)
for (n,t),c in gk.items():
    for m in range(n, M+1):
        coeff[m] += c * (-1)**(m-n) * comb(t, m-n)
for (s,t),c in gr.items():
    if t > M: continue
    for m in range(t, M+1):
        coeff[m] -= c * (-1)**(m-t) * comb(s, m-t)
rhs = ([0,1,-4,4,-1] + [0]*M)[:M+1]
allok = all(coeff[m] == rhs[m] for m in range(1, M+1))
for m in range(1, M+1):
    print(f"p^{m}: LHS {coeff[m]}  RHS {rhs[m]}  {'OK' if coeff[m]==rhs[m] else 'FAIL'}")
print("IDENTITY", "HOLDS to order p^%d" % M if allok else "FAILS")

for s in range(1, min(M,4)+1):
    poly = sorted((t,c) for (n,t),c in gk.items() if n==s)
    print(f"D_king_{s}(q) =", " + ".join(f"{c} q^{t}" for t,c in poly))
