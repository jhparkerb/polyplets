#!/usr/bin/env python3
"""Independent brute enumeration of convex polyplets (HV-convex king animals).

Fixed (translation-class) king-connected animals grown cell-by-cell; dedup by
translation-normalized frozenset. Reports the ALL-polyplet count (must match
A006770) and the HV-convex subcount. Verification of the convex-polyplet
sequence before we treat it as ours.
"""
import sys

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180]  # n=1..10

def norm(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)

def is_hv_convex(cells):
    rows, cols = {}, {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
        cols.setdefault(x, []).append(y)
    for v in rows.values():
        if max(v) - min(v) + 1 != len(v): return False
    for v in cols.values():
        if max(v) - min(v) + 1 != len(v): return False
    return True

level = {norm([(0, 0)])}
allc, conv = [], []
for n in range(1, NMAX + 1):
    allc.append(len(level))
    conv.append(sum(1 for a in level if is_hv_convex(a)))
    if n < NMAX:
        nxt = set()
        for a in level:
            occ = set(a)
            cand = set()
            for x, y in a:
                for dx, dy in KING:
                    p = (x + dx, y + dy)
                    if p not in occ: cand.add(p)
            for p in cand:
                nxt.add(norm(occ | {p}))
        level = nxt

print("n  all_polyplets  A006770  ok   convex_polyplets")
for i in range(NMAX):
    ref = A006770[i] if i < len(A006770) else None
    ok = "OK" if ref == allc[i] else "MISMATCH"
    print(f"{i+1:2d}  {allc[i]:>13}  {str(ref):>8}  {ok:8}  {conv[i]}")
print("\nconvex:", ", ".join(str(c) for c in conv))
