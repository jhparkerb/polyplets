#!/usr/bin/env python3
"""Machine-check of the MOAT-CYCLE proof of max-hole lemma (II'): n >= ha+hm+2.

The 5-step argument (results/subclasses.md):
  1. moat walk: trace the outer contour of the hole region; the cell across each
     boundary edge is foreground (else leak/extension), and consecutive outside
     cells are king-adjacent (incl. at pinch corners, where they are the diagonal
     sealing pair) -> closed king-walk gamma in F around the hole
  2. gamma's winding number is constant and nonzero across the 4-connected hole
  3. loop-erasure at repeated cells (winding adds over the split; keep a nonzero
     part) -> SIMPLE cycle sigma in F still winding the whole hole
  4. nonzero winding forces sigma to attain u >= u_max+1, u <= u_min-1,
     v >= v_max+1, v <= v_min-1 (escape-segment argument: otherwise the extreme
     hole cell connects to infinity without meeting sigma)
  5. per king step |du|+|dv| <= 2 in diagonal coords; closed + spanning
     -> |sigma| >= ((2(ha+1)+2(hm+1))/2 = ha+hm+2; sigma simple -> n >= ha+hm+2.

This script executes steps 1-3 literally on random single-hole king animals and
checks 4-5 (plus tightness stats). Run: python3 -m experiments.maxhole_moat_check
"""
import random
from collections import deque


def hole_components(cells):
    cells = set(cells); xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}; dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in cells and p not in seen:
                seen.add(p); dq.append(p)
    es = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
          if (x, y) not in cells and (x, y) not in seen}
    comps = []
    while es:
        s = next(iter(es)); comp = {s}; es.discard(s); dq = deque([s])
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p in es:
                    es.discard(p); comp.add(p); dq.append(p)
        comps.append(comp)
    return comps


def king_conn(cells):
    cells = set(cells); c0 = next(iter(cells)); seen = {c0}; dq = deque([c0])
    while dq:
        x, y = dq.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if (dx or dy) and p in cells and p not in seen:
                    seen.add(p); dq.append(p)
    return len(seen) == len(cells)


def trace_outer_contour(R):
    """Directed boundary edges of the union of unit squares R, R kept on the LEFT;
    saddles resolved by the sharpest-left-turn rule (diagonal R squares not joined)."""
    R = set(R); E = set()
    for (x, y) in R:
        if (x, y - 1) not in R: E.add(((x, y), (x + 1, y)))
        if (x + 1, y) not in R: E.add(((x + 1, y), (x + 1, y + 1)))
        if (x, y + 1) not in R: E.add(((x + 1, y + 1), (x, y + 1)))
        if (x - 1, y) not in R: E.add(((x, y + 1), (x, y)))
    frm = {}
    for e in E:
        frm.setdefault(e[0], []).append(e)
    def nxt(e):
        a, b = e
        cands = frm.get(b, [])
        if len(cands) == 1:
            return cands[0]
        dx, dy = b[0] - a[0], b[1] - a[1]
        def turnkey(e2):
            (c, d) = e2; ex, ey = d[0] - c[0], d[1] - c[1]
            cross = dx * ey - dy * ex; dot = dx * ex + dy * ey
            return (0 if cross > 0 else (1 if cross == 0 and dot > 0 else 2))
        return sorted(cands, key=turnkey)[0]
    start = min([e for e in E if e[1][0] - e[0][0] == 1], key=lambda e: (e[0][1], e[0][0]))
    seq = [start]; e = start
    while True:
        e = nxt(e)
        if e == start:
            break
        seq.append(e)
        if len(seq) > 8 * len(E) + 16:
            raise RuntimeError("trace loop")
    return seq


def outside_cell(e):
    (a, b) = e; dx, dy = b[0] - a[0], b[1] - a[1]
    if (dx, dy) == (1, 0):  return (a[0], a[1] - 1)
    if (dx, dy) == (0, 1):  return (a[0], a[1])
    if (dx, dy) == (-1, 0): return (b[0], b[1])
    if (dx, dy) == (0, -1): return (b[0] - 1, b[1])


def winding(poly, p):
    import math
    tot = 0.0
    for i in range(len(poly)):
        a = poly[i]; b = poly[(i + 1) % len(poly)]
        a1 = math.atan2(a[1] - p[1], a[0] - p[0]); a2 = math.atan2(b[1] - p[1], b[0] - p[0])
        d = a2 - a1
        while d > math.pi: d -= 2 * math.pi
        while d < -math.pi: d += 2 * math.pi
        tot += d
    return round(tot / (2 * math.pi))


def loop_erase(walk, refpt):
    w = walk[:]
    while True:
        pos = {}; rep = None
        for i, c in enumerate(w):
            if c in pos:
                rep = (pos[c], i); break
            pos[c] = i
        if rep is None:
            return w
        i, j = rep
        loopA = w[i:j]; loopB = w[:i] + w[j:]
        wa = winding(loopA, refpt) if len(loopA) >= 3 else 0
        wb = winding(loopB, refpt) if len(loopB) >= 3 else 0
        if wa and wb: w = loopA if len(loopA) <= len(loopB) else loopB
        elif wa: w = loopA
        elif wb: w = loopB
        else: return None


def diamond(r):
    return {(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1) if abs(x) + abs(y) == r}


def main():
    random.seed(123)
    tested = pinched = tight = 0; fail = []
    for trial in range(6000):
        c = set(diamond(random.randint(1, 4)))
        for _ in range(random.randint(0, 12)):
            cell = random.choice(list(c))
            d = random.choice([(1, 0), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 0), (0, -1), (-1, 1)])
            c.add((cell[0] + d[0], cell[1] + d[1]))
        if not king_conn(c):
            continue
        comps = hole_components(c)
        if len(comps) != 1:
            continue
        H = comps[0]; tested += 1
        us = [x + y for x, y in H]; vs = [x - y for x, y in H]
        ha = max(us) - min(us) + 1; hm = max(vs) - min(vs) + 1
        gamma = []
        for e in trace_outer_contour(H):
            oc = outside_cell(e)
            if not gamma or gamma[-1] != oc:
                gamma.append(oc)
        if gamma and gamma[0] == gamma[-1]:
            gamma.pop()
        if any(g not in c for g in gamma):
            fail.append((trial, "B-cell not in F")); continue
        if not all(max(abs(gamma[i][0] - gamma[(i + 1) % len(gamma)][0]),
                       abs(gamma[i][1] - gamma[(i + 1) % len(gamma)][1])) <= 1
                   for i in range(len(gamma))):
            fail.append((trial, "not king-adjacent")); continue
        href = next(iter(H))
        wall = [winding(gamma, h) for h in H]
        if len(set(wall)) != 1 or wall[0] == 0:
            fail.append((trial, "winding bad")); continue
        if len(gamma) != len(set(gamma)):
            pinched += 1
        sig = loop_erase(gamma, href)
        if sig is None or len(sig) != len(set(sig)):
            fail.append((trial, "loop-erase")); continue
        if any(winding(sig, h) == 0 for h in H):
            fail.append((trial, "sigma misses hole")); continue
        su = [x + y for x, y in sig]; sv = [x - y for x, y in sig]
        if not (max(su) >= max(us) + 1 and min(su) <= min(us) - 1
                and max(sv) >= max(vs) + 1 and min(sv) <= min(vs) - 1):
            fail.append((trial, "extremes")); continue
        if len(sig) < ha + hm + 2:
            fail.append((trial, f"len {len(sig)} < {ha+hm+2}")); continue
        if len(sig) == ha + hm + 2:
            tight += 1
    print(f"single-hole shapes: {tested}  pinched contours: {pinched}  tight: {tight}")
    print(f"FAILURES: {len(fail)}", fail[:8])


if __name__ == "__main__":
    main()
