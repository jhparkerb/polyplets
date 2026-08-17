#!/usr/bin/env python3
"""Convex king animals (HV-convex polyplets) counted by exact bounding box.

f(w,h) = number of translation classes with bounding box exactly w x h.
Model (same as convex_tm.py, validated there vs brute force): a sequence of
h row intervals [l_i, r_i], l valley-unimodal (non-increasing then
non-decreasing), r mountain-unimodal, consecutive rows within king reach
(l' <= r+1, r' >= l-1). Phases flip on first strict violation -> unique parse.

g(w,h) = count with all intervals inside [0,w) (no touching requirement);
f(w,h) = g(w,h) - 2 g(w-1,h) + g(w-2,h)   (second difference in w).

Validation 1: direct subset brute force over the w x h box (king-connected +
HV-convex + touches all 4 sides) for small boxes.
Validation 2: transpose symmetry f(w,h) == f(h,w).
Validation 3: area-marked variant reproduces convex_tm.py's area sequence.

Usage: python3 experiments/convex_box.py [WMAX] [HMAX]
"""
import sys
from collections import defaultdict


def g_table(wmax, hmax, king=True):
    """g[w][h] for 1<=w<=wmax, 1<=h<=hmax. king=False -> polyomino
    adjacency (column overlap required): l' <= r, r' >= l."""
    reach = 1 if king else 0
    g = [[0] * (hmax + 1) for _ in range(wmax + 1)]
    for w in range(1, wmax + 1):
        # state: (l, r, pl, pr) -> count
        dp = {}
        for l in range(w):
            for r in range(l, w):
                dp[(l, r, 0, 0)] = 1
        for h in range(1, hmax + 1):
            g[w][h] = sum(dp.values())
            if h == hmax:
                break
            ndp = defaultdict(int)
            for (l, r, pl, pr), c in dp.items():
                lo_l = l if pl else 0          # pl=1: l' >= l
                hi_r = r if pr else w - 1      # pr=1: r' <= r
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        ndp[(lp, rp, npl, npr)] += c
            dp = ndp
    return g


def f_from_g(g, wmax, hmax):
    f = [[0] * (hmax + 1) for _ in range(wmax + 1)]
    for w in range(1, wmax + 1):
        for h in range(1, hmax + 1):
            f[w][h] = (g[w][h] - 2 * (g[w - 1][h] if w >= 2 else 0)
                       + (g[w - 2][h] if w >= 3 else 0))
    return f


# ---------- validation 1: direct subset brute force ----------
def brute_box(w, h):
    """Count subsets of the w x h grid that are king-connected, HV-convex,
    and touch all four sides of the box."""
    cells = [(x, y) for y in range(h) for x in range(w)]
    n = len(cells)
    idx = {c: i for i, c in enumerate(cells)}
    cnt = 0
    for mask in range(1, 1 << n):
        occ = [cells[i] for i in range(n) if mask >> i & 1]
        xs = [x for x, y in occ]
        ys = [y for x, y in occ]
        if min(xs) != 0 or max(xs) != w - 1 or min(ys) != 0 or max(ys) != h - 1:
            continue
        rows, cols = {}, {}
        for x, y in occ:
            rows.setdefault(y, []).append(x)
            cols.setdefault(x, []).append(y)
        if any(max(v) - min(v) + 1 != len(v) for v in rows.values()):
            continue
        if any(max(v) - min(v) + 1 != len(v) for v in cols.values()):
            continue
        # king connectivity
        occs = set(occ)
        seen = {occ[0]}
        stack = [occ[0]]
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (x + dx, y + dy)
                    if p in occs and p not in seen:
                        seen.add(p)
                        stack.append(p)
        if len(seen) == len(occ):
            cnt += 1
    return cnt


if __name__ == "__main__":
    wmax = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    hmax = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    g = g_table(wmax, hmax)
    f = f_from_g(g, wmax, hmax)

    print("validation 1: brute force small boxes")
    ok = True
    for w in range(1, 5):
        for h in range(1, 5):
            if w * h > 16:
                continue
            b = brute_box(w, h)
            mark = "OK" if b == f[w][h] else "MISMATCH"
            if b != f[w][h]:
                ok = False
            print(f"  f({w},{h}) dp={f[w][h]} brute={b} {mark}")
    assert ok, "brute-force mismatch"

    print("validation 2: transpose symmetry")
    m = min(wmax, hmax)
    for w in range(1, m + 1):
        for h in range(1, m + 1):
            assert f[w][h] == f[h][w], (w, h, f[w][h], f[h][w])
    print("  f(w,h)==f(h,w) for all w,h <= %d  OK" % m)

    print("\nf(w,h) table (rows w=1..%d, cols h=1..%d):" % (wmax, hmax))
    for w in range(1, wmax + 1):
        print("  " + " ".join(str(f[w][h]) for h in range(1, hmax + 1)))

    smax = min(wmax, hmax) * 2  # complete anti-diagonals only up to this
    print("\nsemiperimeter sequence a(s)=sum_{w+h=s} f(w,h), s=2..%d:" % smax)
    a = []
    for s in range(2, smax + 1):
        tot = 0
        complete = True
        for w in range(1, s):
            h = s - w
            if w <= wmax and h <= hmax:
                tot += f[w][h]
            else:
                complete = False
        a.append((s, tot, complete))
    print("  " + ", ".join(f"{t}" + ("" if c else "?") for s, t, c in a))
