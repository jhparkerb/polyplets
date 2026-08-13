#!/usr/bin/env python3
"""r3_l3_pinch.py — L3 contour-encoding lane measurements (round 3).

Enumerates fixed king animals (polyplets) n <= NMAX from scratch by rooted
growth (Redelmeier-style, own implementation, no shared code with any repo
engine) and measures, per animal:

  - holes: 4-connected components of the complement not touching the
    bounding frame (the repo convention, quoted from results/holes_n19.txt
    header: "4-connected components of the complement not touching the
    boundary; the Jordan dual of the 8-connected foreground");
  - pinch vertices: lattice vertices whose four incident cells show exactly
    one filled diagonal pair (boundary curve visits the vertex twice);
  - rook pieces: number of 4-connected components (L1's stratification);
  - the "single simple closed curve" class: hole-free AND pinch-free.

Validation (fail-closed): totals per n must equal A006770 row sums of the
banked hole table, and the full per-(n, holes) distribution must match
results/holes_n18.txt exactly for every n <= NMAX. Any mismatch aborts.

Also prints the per-height breakdown at n = NMAX (band analogue: H/n in
[0.375, 0.525] mirrors n=40, H=15..21) and the Motzkin comparison for the
banked cut ranks 21, 51, 127, 298 (results/boundary-push-tensornetwork.md).

Exact integer arithmetic throughout. Laptop-minutes scale.
"""
import sys, time
from collections import defaultdict

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 9
TABLE = sys.argv[2] if len(sys.argv) > 2 else 'results/holes_n18.txt'  # RED control: pass a corrupted copy

K8 = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
R4 = [(1,0),(-1,0),(0,1),(0,-1)]

# ---------- per-animal analysis ----------

def analyse(cells):
    """cells: frozenset of (x,y). Returns (holes, pinches, pieces, height)."""
    xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    height = y1 - y0 + 1
    cs = cells

    # pinch vertices: vertex v=(x,y) has incident cells (x-1,y-1),(x,y-1),
    # (x-1,y),(x,y).  Pinch iff exactly one diagonal pair filled.
    pinches = 0
    for vx in range(x0, x1 + 2):
        for vy in range(y0, y1 + 2):
            a = (vx-1, vy-1) in cs   # SW
            b = (vx,   vy-1) in cs   # SE
            c = (vx-1, vy)   in cs   # NW
            d = (vx,   vy)   in cs   # NE
            if (a and d and not b and not c) or (b and c and not a and not d):
                pinches += 1

    # holes: 4-connected complement components inside frame not touching it
    holes = 0
    seen = set()
    # frame = one-cell margin; flood from a frame cell to mark exterior
    fx0, fx1, fy0, fy1 = x0 - 1, x1 + 1, y0 - 1, y1 + 1
    stack = [(fx0, fy0)]
    seen.add((fx0, fy0))
    while stack:
        x, y = stack.pop()
        for dx, dy in R4:
            p = (x + dx, y + dy)
            if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1 \
               and p not in seen and p not in cs:
                seen.add(p); stack.append(p)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            p = (x, y)
            if p in cs or p in seen:
                continue
            holes += 1
            stack = [p]; seen.add(p)
            while stack:
                q = stack.pop()
                for dx, dy in R4:
                    r = (q[0] + dx, q[1] + dy)
                    if r not in seen and r not in cs \
                       and x0 <= r[0] <= x1 and y0 <= r[1] <= y1:
                        seen.add(r); stack.append(r)

    # rook pieces
    pieces = 0
    seen2 = set()
    for p in cs:
        if p in seen2:
            continue
        pieces += 1
        stack = [p]; seen2.add(p)
        while stack:
            q = stack.pop()
            for dx, dy in R4:
                r = (q[0] + dx, q[1] + dy)
                if r in cs and r not in seen2:
                    seen2.add(r); stack.append(r)

    return holes, pinches, pieces, height

# ---------- enumeration: rooted growth, fixed animals ----------
# Allowed cells: y > 0, or (y == 0 and x >= 0); root (0,0) is the reading-
# order minimum, so each fixed animal is produced exactly once.

stats = {n: defaultdict(int) for n in range(1, NMAX + 1)}
# keys: 'total','hole1','pinch1','multi','simple'; plus distributions
holedist = {n: defaultdict(int) for n in range(1, NMAX + 1)}
hstats = defaultdict(lambda: defaultdict(int))   # (n==NMAX) per-height

def allowed(p):
    return p[1] > 0 or (p[1] == 0 and p[0] >= 0)

def record(cells, n):
    holes, pinches, pieces, height = analyse(cells)
    s = stats[n]
    s['total'] += 1
    if holes: s['hole1'] += 1
    if pinches: s['pinch1'] += 1
    if pieces > 1: s['multi'] += 1
    if holes == 0 and pinches == 0: s['simple'] += 1
    s['pinchsum'] += pinches
    s['piecesum'] += pieces
    holedist[n][holes] += 1
    if n == NMAX:
        h = hstats[height]
        h['total'] += 1
        if holes: h['hole1'] += 1
        if pinches: h['pinch1'] += 1
        if holes == 0 and pinches == 0: h['simple'] += 1

def enumerate_animals():
    """Classic Redelmeier: each fixed animal of each size 1..NMAX is
    generated exactly once, at the moment its last cell is placed."""
    cells = set()
    seen = {(0, 0)}
    sys.setrecursionlimit(10000)

    def rec(untried, idx, size):
        for i in range(idx, len(untried)):
            c = untried[i]
            cells.add(c)
            record(cells, size + 1)
            if size + 1 < NMAX:
                new = []
                for dx, dy in K8:
                    p = (c[0] + dx, c[1] + dy)
                    if allowed(p) and p not in seen:
                        new.append(p)
                seen.update(new)
                rec(untried + new, i + 1, size + 1)
                seen.difference_update(new)
            cells.remove(c)
            # c stays in `seen` (proposed at a higher level), and idx=i+1
            # excludes it from deeper subtrees: Redelmeier's no-reuse rule.

    rec([(0, 0)], 0, 0)

t0 = time.time()
enumerate_animals()
t1 = time.time()

# ---------- validation against the banked hole table ----------
banked = defaultdict(dict)
with open(TABLE) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        n, k, cnt = map(int, line.split())
        banked[n][k] = cnt

ok = True
for n in range(1, NMAX + 1):
    mine = dict(holedist[n])
    theirs = {k: v for k, v in banked[n].items()}
    if mine != theirs:
        print(f'VALIDATION FAIL n={n}: mine={mine} banked={theirs}')
        ok = False
if not ok:
    sys.exit('ABORT: hole distribution mismatch against results/holes_n18.txt')
print(f'VALIDATION OK: per-(n,holes) distribution matches results/holes_n18.txt '
      f'exactly for all n <= {NMAX} (row sums = A006770)')
print(f'enumeration+analysis wall: {t1-t0:.1f} s\n')

hdr = ('n', 'total', '>=1 hole', 'share', '>=1 pinch', 'share',
       'multi-piece', 'share', 'simple-curve', 'share', 'mean pinches',
       'mean pieces')
print(('%3s %10s %10s %7s %10s %7s %10s %7s %12s %7s %12s %11s') % hdr)
for n in range(1, NMAX + 1):
    s = stats[n]; T = s['total']
    print('%3d %10d %10d %6.2f%% %10d %6.2f%% %10d %6.2f%% %12d %6.2f%% %12.3f %11.3f'
          % (n, T, s['hole1'], 100*s['hole1']/T, s['pinch1'], 100*s['pinch1']/T,
             s['multi'], 100*s['multi']/T, s['simple'], 100*s['simple']/T,
             s['pinchsum']/T, s['piecesum']/T))

print(f'\nPer-height at n={NMAX} (band analogue H/n in [0.375,0.525] '
      f'~ H={round(0.375*NMAX)}..{round(0.525*NMAX)}):')
print('%3s %10s %9s %9s %13s' % ('H', 'total', 'hole>=1', 'pinch>=1', 'simple-curve'))
for h in sorted(hstats):
    s = hstats[h]; T = s['total']
    print('%3d %10d %8.2f%% %8.2f%% %12.2f%%'
          % (h, T, 100*s['hole1']/T, 100*s['pinch1']/T, 100*s['simple']/T))

# ---------- Motzkin comparison for the banked cut ranks ----------
M = [0]*40; M[0] = 1; M[1] = 1
for i in range(2, 40):
    M[i] = ((2*i+1)*M[i-1] + 3*(i-1)*M[i-2]) // (i+2)
print('\nMotzkin numbers M0..M12:', M[:13])
print('banked central-cut ranks (results/boundary-push-tensornetwork.md): '
      'H=8:21 H=10:51 H=12:127 H=14:298')
for H, r in [(8,21),(10,51),(12,127),(14,298)]:
    m = M[H//2 + 1]
    print(f'  H={H}: rank {r} vs M({H//2+1}) = {m}  '
          f'{"EXACT" if r == m else f"(<= {m}, dump at maxn=16 off-peak)"}')
