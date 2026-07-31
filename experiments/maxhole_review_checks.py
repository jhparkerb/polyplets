#!/usr/bin/env python3
"""Exhaustive small-n checks backing the OW-6 Lean modules (Holes/HolesUpper).

Purpose: replace the unreproducible random-sample statistics that the
2026-07-31 adversarial review found in HolesUpper.lean's module doc
(docs/reviews/outworks-adversarial.md, MINOR list) with deterministic,
exhaustive counts, and bank the review's independent verifications:

  1. Enumerate ALL fixed king animals n = 2..9 (growth method; counts must
     reproduce A006770: 4, 20, 110, 638, 3832, 23592, 147941, 940982).
  2. Over the single-hole ones (enclosed cells one 4-connected region):
     - MoatBound (II'):  n >= ha + hm + 2       (expect 0 violations)
     - (I') area bound:  |H| <= ceil(ha*hm/2)   (expect 0 violations)
     - substitute 1 (level charging): every u-level of the hole's range
       carries >= 1 animal cell (expect violations — refuted), and the
       >= 2 variant (more violations);
     - substitute 2 (gap charging): every u-gap {l, l+1} for
       u0-1 <= l <= u1 carries >= 2 animal cells, likewise v
       (expect 0 violations — holds but is too weak, see the module doc).
  3. The diagonal-frame family: |hullBox \\ boxHole| = a+b+2 for ALL a, b
     (vs the 4-neighbour ring's a+b+1 when min=1 & max even), and
     boxHole rook-disconnected iff min(a,b) = 1 and max(a,b) >= 3.

Exact command:  python3 experiments/maxhole_review_checks.py \
                  | tee experiments/maxhole_review_checks.log
Target machine: any (run 2026-07-31 on the local Mac).
Predicted cost: ~3-8 min wall, ~2 GB RAM (dominated by the n = 9 animal
set, ~941k frozensets). Pure stdlib, single process.
Resume/kill:    stateless — kill any time, rerun from scratch.
"""

import sys
from collections import deque

K8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
R4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

A006770 = {2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941, 9: 940982}


def canon(s):
    mx = min(x for x, y in s)
    my = min(y for x, y in s)
    return frozenset((x - mx, y - my) for x, y in s)


def grow(prev):
    out = set()
    for s in prev:
        for (x, y) in s:
            for dx, dy in K8:
                p = (x + dx, y + dy)
                if p not in s:
                    out.add(canon(s | {p}))
    return out


def enclosed(S):
    xs = [x for x, y in S]
    ys = [y for x, y in S]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    seen = {(x0, y0)}
    dq = deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in R4:
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in S and p not in seen:
                seen.add(p)
                dq.append(p)
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
            if (x, y) not in S and (x, y) not in seen}


def rook_conn(H):
    if not H:
        return False
    H = set(H)
    c0 = next(iter(H))
    seen = {c0}
    dq = deque([c0])
    while dq:
        x, y = dq.popleft()
        for dx, dy in R4:
            p = (x + dx, y + dy)
            if p in H and p not in seen:
                seen.add(p)
                dq.append(p)
    return len(seen) == len(H)


def animal_checks():
    print("== exhaustive single-hole checks, n = 2..9 ==", flush=True)
    cur = {frozenset({(0, 0)})}
    viol_moat = viol_I = viol_s2 = 0
    viol_s1_ge1 = viol_s1_ge2 = 0
    nsingle_total = 0
    best = {}
    for n in range(2, 10):
        cur = grow(cur)
        assert len(cur) == A006770[n], f"A006770({n}) mismatch: {len(cur)}"
        nsingle = 0
        for S in cur:
            H = enclosed(S)
            if not H or not rook_conn(H):
                continue
            nsingle += 1
            us = [x + y for x, y in H]
            vs = [x - y for x, y in H]
            u0, u1 = min(us), max(us)
            v0, v1 = min(vs), max(vs)
            ha, hm = u1 - u0 + 1, v1 - v0 + 1
            if n < ha + hm + 2:
                viol_moat += 1
            if len(H) > (ha * hm + 1) // 2:
                viol_I += 1
            Su = [x + y for x, y in S]
            Sv = [x - y for x, y in S]
            # substitute 1: animal cells at every u-level of the hole's range
            lv = [sum(1 for u in Su if u == l) for l in range(u0, u1 + 1)]
            if min(lv) < 1:
                viol_s1_ge1 += 1
            if min(lv) < 2:
                viol_s1_ge2 += 1
            # substitute 2: >= 2 animal cells in every u-gap and v-gap
            ok = all(sum(1 for u in Su if u in (l, l + 1)) >= 2
                     for l in range(u0 - 1, u1 + 1)) and \
                 all(sum(1 for v in Sv if v in (l, l + 1)) >= 2
                     for l in range(v0 - 1, v1 + 1))
            if not ok:
                viol_s2 += 1
            best[n] = max(best.get(n, 0), len(H))
        nsingle_total += nsingle
        print(f"n={n} animals={len(cur)} single-hole={nsingle} "
              f"maxarea={best.get(n, 0)}", flush=True)
    print(f"single-hole total (n<=9): {nsingle_total}")
    print(f"MoatBound (II') violations: {viol_moat}")
    print(f"(I') area violations: {viol_I}")
    print(f"substitute 1 (>=1 cell per u-level) violations: {viol_s1_ge1}")
    print(f"substitute 1 (>=2 cells per u-level) violations: {viol_s1_ge2}")
    print(f"substitute 2 (gap charging >=2) violations: {viol_s2}")


def box_hole(a, b):
    return {(x, y) for x in range(-b, a + b) for y in range(-b, a + b)
            if 0 <= x + y <= a - 1 and 0 <= x - y <= b - 1}


def family_checks(amax=12):
    print(f"== diagonal-frame family checks, 1 <= a, b <= {amax} ==", flush=True)
    ring_short = []
    disc = []
    for a in range(1, amax + 1):
        for b in range(1, amax + 1):
            box = box_hole(a, b)
            ring4 = {(x + dx, y + dy) for x, y in box for dx, dy in R4} - box
            # hullBox = cells with x+y in [-1, a] and x-y in [-1, b]
            hull = {(x, y) for x in range(-b - 1, a + b + 1)
                    for y in range(-b - 1, a + b + 1)
                    if -1 <= x + y <= a and -1 <= x - y <= b}
            frame = hull - box
            assert len(frame) == a + b + 2, (a, b, len(frame))
            if len(ring4) != a + b + 2:
                ring_short.append((a, b, len(ring4)))
            if not rook_conn(box):
                disc.append((a, b))
    print(f"|hullBox \\ boxHole| = a+b+2: all {amax * amax} pairs PASS")
    print(f"4-neighbour ring short of a+b+2 at: {ring_short}")
    expect = [(a, b) for a in range(1, amax + 1) for b in range(1, amax + 1)
              if min(a, b) == 1 and max(a, b) >= 3]
    print(f"boxHole rook-disconnected at: {sorted(disc)}")
    print(f"  == {{min=1, max>=3}}: {sorted(disc) == sorted(expect)}")


if __name__ == "__main__":
    family_checks()
    animal_checks()
    print("done", flush=True)
