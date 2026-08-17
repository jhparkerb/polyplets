#!/usr/bin/env python3
"""Phase 2 of Certificate Squeeze: slack audit. Locate where the ~31% over-count lives
before engineering tighter types (measure, don't reason).

For each type T in the RD=2 system, slack(T,n) = rhs(T,n) / true_count(T,n). slack=1
means that recurrence is exact; slack>1 is the looseness that inflates the bound. Also
reports the base-fact slack G8(n)/A(n) (we bound G8; truth is A <= G8 <= n*A).

Single-pass counting: each type's forbidden set is a set of offsets; a marked cell (P,c)
counts for type T iff every offset in T is EMPTY at c. We compute, in one sweep over all
(P,c), the empty-offset bitmask over the union of all offsets used, then add to every type
whose mask is a subset. Types are grouped by which offsets they use so the per-(P,c) work
is small.

Usage: python3 -m experiments.king_slack [NMAX]
"""
import sys, statistics as st
from experiments.king_types import all_polyplets, type_count, OFF

KING8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
def free_cells(f): return [d for d in KING8 if d not in f]
RD = 2
WD = [(dx,dy) for dx in range(-RD,RD+1) for dy in range(-RD,RD+1) if (dx,dy)!=(0,0)]
def d_type(f, d):
    ke = {(0,0)} | (set(KING8) - {d}) | set(f)
    return frozenset(o for o in WD if (d[0]+o[0], d[1]+o[1]) in ke)
def canonical(free): return min(free, key=lambda p:(p[1], p[0]))

recur = {}
G8 = frozenset({OFF[o] for o in ('W','SW','S','SE')})
seen = {G8}; q = [G8]
while q:
    T = q.pop(); fr = free_cells(T)
    if not fr: recur[T] = None; continue
    d = canonical(fr); Tp = frozenset(set(T) | {d}); D = d_type(T, d)
    recur[T] = (Tp, D)
    for X in (Tp, D):
        if X not in seen: seen.add(X); q.append(X)
print(f"RD={RD} system: {len(recur)} types")

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 8
lv = all_polyplets(NMAX)

# ---- single-pass type counting ----
# bit index for every offset that appears in any type
OFFS = sorted(set().union(*[set(T) for T in recur]))
bit = {o:i for i,o in enumerate(OFFS)}
types = list(recur)
tmask = {T: sum(1<<bit[o] for o in T) for T in types}
tc = {T: {n:0 for n in lv} for T in types}
# group types by the offsets they touch so we test few candidates per (P,c)
for n, polys in lv.items():
    acc = tc  # local ref
    for P in polys:
        cells = P
        for (cx,cy) in cells:
            # empty-offset mask: bit set if that offset is EMPTY around c
            em = 0
            for o,i in bit.items():
                if (cx+o[0], cy+o[1]) not in cells: em |= 1<<i
            for T in types:
                if tmask[T] & em == tmask[T]:      # T subset of empty  => counts
                    acc[T][n] += 1

def rhs(T, n):
    r = recur[T]
    if r is None: return 1 if n == 1 else 0
    Tp, D = r
    return tc[Tp].get(n,0) + sum(tc[Tp].get(i,0)*tc[D].get(n-i,0) for i in range(1,n))

nb, na = NMAX-1, NMAX       # slack reported at the top two sizes
rows = []
for T in recur:
    if recur[T] is None: continue
    sa = rhs(T,na)/tc[T][na] if tc[T][na] else float('nan')
    sb = rhs(T,nb)/tc[T][nb] if tc[T][nb] else float('nan')
    rows.append((sa, sb, len(T), T))
rows.sort(reverse=True)

print(f"\ntop-15 loosest recurrences (slack = rhs/true):")
print(f"{'slack@'+str(na):>9} {'slack@'+str(nb):>9} {'|T|':>4}  forbidden offsets")
for sa,sb,nt,T in rows[:15]:
    print(f"{sa:9.4f} {sb:9.4f} {nt:4d}  {sorted(T)}")

sl = [r[0] for r in rows]
print(f"\nslack@{na} distribution over {len(sl)} recurrences:")
print(f"  max {max(sl):.4f}  median {st.median(sl):.4f}  min {min(sl):.4f}")
print(f"  #>1.5: {sum(1 for s in sl if s>1.5)}   #>1.2: {sum(1 for s in sl if s>1.2)}   #<=1.05: {sum(1 for s in sl if s<=1.05)}")
grow = [r[0]-r[1] for r in rows]
print(f"  slack@{na} - slack@{nb}: max {max(grow):+.4f} median {st.median(grow):+.4f}  (growing => compounds)")

A = {n: len(lv[n]) for n in lv}
g8 = type_count(lv, forbid=tuple(G8))
print("\nbase-fact slack  G8(n)/A(n)  (we bound G8; A <= G8 <= n*A):")
for n in range(1, NMAX+1):
    print(f"  n={n}: A={A[n]:>8}  G8={g8.get(n,0):>9}  ratio {g8.get(n,0)/A[n]:.4f}")
