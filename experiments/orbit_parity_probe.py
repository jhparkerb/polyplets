#!/usr/bin/env python3
"""Orbit-counting congruence probe for fixed polyplets (A006770).

D4 acts on fixed (translation-class) king animals.  Orbit sizes divide 8,
so  a(n) = n1 + 2 n2 + 4 n4 + 8 n8  with n_k = #orbits of size k.
Hence  a(n) = n1 (mod 2),  a(n) = n1 + 2 n2 (mod 4), etc.

n1 counts animals with FULL D4 symmetry.  Their cells fall into D4-orbits of
size 8, 4 (on an axis or a diagonal) or 1 (the centre), so n = 8p + 4q + r
with r in {0,1}: no such animal exists unless n = 0 or 1 (mod 4).

Prediction: a(n) is EVEN whenever n = 2 or 3 (mod 4).

This script brute-forces small n and checks the whole ladder.
"""
import itertools
from collections import defaultdict

NB = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def canon(cells):
    xs = min(c[0] for c in cells); ys = min(c[1] for c in cells)
    return frozenset((x - xs, y - ys) for x, y in cells)


def grow(maxn):
    """All fixed polyplets by size, via naive BFS over canonical forms."""
    levels = [set(), {canon([(0, 0)])}]
    for n in range(2, maxn + 1):
        nxt = set()
        for a in levels[n - 1]:
            for (x, y) in a:
                for dx, dy in NB:
                    c = (x + dx, y + dy)
                    if c not in a:
                        nxt.add(canon(a | {c}))
        levels.append(nxt)
    return levels


def d4(cells):
    """The 8 images of a cell set under D4, each canonicalised."""
    out = []
    for k in range(4):
        for flip in (False, True):
            s = []
            for (x, y) in cells:
                for _ in range(k):
                    x, y = -y, x
                if flip:
                    x = -x
                s.append((x, y))
            out.append(canon(s))
    return out


MAXN = 9
levels = grow(MAXN)
print(f"{'n':>3} {'a(n)':>10} {'n1':>5} {'n2':>6} {'n4':>8} {'n8':>10} "
      f"{'a%2':>4} {'n1%2':>5} {'a%4':>4} {'(n1+2n2)%4':>11} {'a%8':>4} {'pred%8':>7}")
for n in range(1, MAXN + 1):
    A = levels[n]
    seen = set(); sizes = defaultdict(int)
    for a in A:
        if a in seen:
            continue
        orb = set(d4(a))
        seen |= orb
        sizes[len(orb)] += 1
    n1, n2, n4, n8 = sizes[1], sizes[2], sizes[4], sizes[8]
    an = len(A)
    assert an == n1 + 2 * n2 + 4 * n4 + 8 * n8
    print(f"{n:>3} {an:>10} {n1:>5} {n2:>6} {n4:>8} {n8:>10} "
          f"{an%2:>4} {n1%2:>5} {an%4:>4} {(n1+2*n2)%4:>11} "
          f"{an%8:>4} {(n1+2*n2+4*n4)%8:>7}")

# The mod-4 congruence class claim, checked against the full banked b-file.
a = {}
for line in open('results/b006770_upload.txt'):
    line = line.strip()
    if line and not line.startswith('#'):
        k, v = line.split(); a[int(k)] = int(v)
bad = [n for n, v in a.items() if n % 4 in (2, 3) and v % 2 == 1]
odd = [n for n, v in a.items() if v % 2 == 1]
print(f"\nbanked terms n=1..{max(a)}")
print(f"  n with a(n) ODD          : {odd}")
print(f"  their n mod 4            : {sorted({n%4 for n in odd})}")
print(f"  violations of 'n=2,3 mod 4 => a(n) even': {bad}")
