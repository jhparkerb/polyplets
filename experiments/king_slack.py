#!/usr/bin/env python3
"""Phase 2 of Certificate Squeeze: slack audit. Locate where the ~31% over-count lives
before engineering tighter types (measure, don't reason).

For each type T in the RD=2 system, slack(T,n) = rhs(T,n) / true_count(T,n) at n=8,9.
rhs is the over-counting recurrence used in king_bui.py. slack=1 means that recurrence
is exact; slack>1 is the looseness that inflates the bound. Also reports the base-fact
slack G8(n)/A(n) (we bound G8; truth is A <= G8 <= n*A).

Usage: python3 -m experiments.king_slack
"""
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

NMAX = 9
lv = all_polyplets(NMAX)
tc = {T: type_count(lv, forbid=tuple(T)) for T in recur}
def rhs(T, n):
    r = recur[T]
    if r is None: return 1 if n == 1 else 0
    Tp, D = r
    return tc[Tp].get(n,0) + sum(tc[Tp].get(i,0)*tc[D].get(n-i,0) for i in range(1,n))

# per-type slack at n=8,9
rows = []
for T in recur:
    if recur[T] is None: continue
    s8 = rhs(T,8)/tc[T][8] if tc[T][8] else float('nan')
    s9 = rhs(T,9)/tc[T][9] if tc[T][9] else float('nan')
    rows.append((s9, s8, len(T), T))
rows.sort(reverse=True)

print("\ntop-15 loosest recurrences (slack = rhs/true):")
print(f"{'slack@9':>9} {'slack@8':>9} {'|T|':>4}  forbidden offsets")
for s9,s8,nt,T in rows[:15]:
    print(f"{s9:9.4f} {s8:9.4f} {nt:4d}  {sorted(T)}")

import statistics as st
sl9 = [r[0] for r in rows]
print(f"\nslack@9 distribution over {len(sl9)} recurrences:")
print(f"  max {max(sl9):.4f}  median {st.median(sl9):.4f}  min {min(sl9):.4f}")
print(f"  #>1.5: {sum(1 for s in sl9 if s>1.5)}   #>1.2: {sum(1 for s in sl9 if s>1.2)}   #<=1.05 (near-exact): {sum(1 for s in sl9 if s<=1.05)}")

# does slack grow with n? (diffuse+growing => intrinsic; flat => a few fixable types)
grow = [r[0]-r[1] for r in rows]
print(f"  slack@9 - slack@8: max {max(grow):+.4f} median {st.median(grow):+.4f}  (growing => over-count compounds)")

# base fact G8/A
A = [len(lv[n]) for n in range(NMAX+1)]           # A(n) = a(n) polyplets
g8 = type_count(lv, forbid=tuple(G8))
print("\nbase-fact slack  G8(n)/A(n)  (we bound G8; A <= G8 <= n*A):")
for n in range(1, NMAX+1):
    print(f"  n={n}: A={A[n]:>8}  G8={g8.get(n,0):>9}  ratio {g8.get(n,0)/A[n]:.4f}")
print("  ^ if G8/A grows ~linearly the anchor itself leaks a factor; if it flattens, G8 is a tight anchor.")
