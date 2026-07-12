#!/usr/bin/env python3
"""Joint box table B(n, W, H) probe -- see results/joint-box-probe.md.

Row transfer with connectivity partitions plus box-edge offsets (dl, dr);
transitions cached per row shape. Validates every computed marginal against
the banked triangle. Usage: python3 experiments/joint_box_probe.py [Hmax]
"""
import os
import sys
import time
from itertools import combinations
from collections import defaultdict
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUD = 2
M = 3 + 2 * BUD


def rowpart(cells):
    lab = list(range(len(cells)))
    for i in range(len(cells) - 1):
        if cells[i + 1] - cells[i] <= 1:
            lab[i + 1] = lab[i]
    cmap = {}
    out = []
    for x in lab:
        if x not in cmap:
            cmap[x] = len(cmap)
        out.append(cmap[x])
    return tuple(out)


@lru_cache(maxsize=None)
def shape_transitions(cells, part):
    spread = cells[-1]
    nb = len(set(part))
    out = []
    for s in range(1, BUD + 2):
        for T in combinations(range(-M, spread + M + 1), s):
            lab = list(range(nb + s))

            def find(x):
                while lab[x] != x:
                    lab[x] = lab[lab[x]]
                    x = lab[x]
                return x

            def uni(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    lab[ra] = rb

            touched = [False] * nb
            for j, t in enumerate(T):
                for i, c in enumerate(cells):
                    if abs(t - c) <= 1:
                        uni(part[i], nb + j)
                        touched[part[i]] = True
            for j in range(s - 1):
                if T[j + 1] - T[j] <= 1:
                    uni(nb + j, nb + j + 1)
            if not all(touched[b] for b in set(part)):
                continue
            roots = [find(nb + j) for j in range(s)]
            cmap = {}
            npart = []
            for r in roots:
                if r not in cmap:
                    cmap[r] = len(cmap)
                npart.append(cmap[r])
            shift = T[0]
            out.append((tuple(t - shift for t in T), tuple(npart),
                        shift, T[-1] - T[0], s - 1))
    return out


def joint(H):
    dp = defaultdict(int)
    for s in range(1, BUD + 2):
        for rest in combinations(range(1, M + 1), s - 1):
            cells = (0,) + rest
            dp[(cells, rowpart(cells), 0, 0, s - 1)] += 1
    for _ in range(H - 1):
        ndp = defaultdict(int)
        for (cells, part, dl, dr, sur), v in dp.items():
            spread = cells[-1]
            for (nc, np_, shift, nspread, ds) in shape_transitions(cells, part):
                if sur + ds > BUD:
                    continue
                ndp[(nc, np_, max(shift + dl, 0),
                     max(spread + dr - shift - nspread, 0), sur + ds)] += v
        dp = ndp
    B = defaultdict(int)
    for (cells, part, dl, dr, sur), v in dp.items():
        if len(set(part)) == 1:
            B[(H + sur, dl + cells[-1] + dr + 1)] += v
    return B


def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    T = {}
    d = os.path.join(ROOT, "results", "ns_a36", "perheight")
    for f in os.listdir(d):
        if f.startswith('h') and f.endswith('.out'):
            Hc = int(f[1:-4])
            for ln in open(os.path.join(d, f)):
                n, c = ln.split()
                T[(int(n), Hc)] = int(c)
    t0 = time.time()
    for H in range(1, Hmax + 1):
        B = joint(H)
        for k in range(BUD + 1):
            if (H + k, H) in T:
                s = sum(v for (nn, W), v in B.items() if nn == H + k)
                assert s == T[(H + k, H)], (H, k, s)
        assert B.get((H, 2), 0) == (2 ** H - 2 if H >= 2 else 0)
        if H >= 2:
            assert B.get((H + 1, 2), 0) == H * 2 ** (H - 1)
    print(f"joint table H<={Hmax}, k<=2: marginals + edge laws OK "
          f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
