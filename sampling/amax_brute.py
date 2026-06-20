#!/usr/bin/env python3
"""Exact maximum hole area of an n-cell polyplet, by brute force.

A_max(n) = max over all fixed n-cell king-connected animals of the number of
enclosed empty cells (bounded 4-connected background regions, the primary
convention). Enumerates all fixed polyplets of each size by growth and floods.
Exact but exponential -- practical only for small n (a(9) ~ 1e6; beyond is slow).

Usage:  python3 sampling/amax_brute.py [N]    (default 9); prints "n A_max(n)".
"""
import os
import sys
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)


def neigh(c):
    r, k = c
    return [(r + dr, k + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
            if (dr, dc) != (0, 0)]


def canon(S):
    mr = min(r for r, _ in S); mc = min(c for _, c in S)
    return frozenset((r - mr, c - mc) for r, c in S)


def hole_area(S):
    S = set(S); rs = [r for r, _ in S]; cs = [c for _, c in S]
    r0, r1, c0, c1 = min(rs) - 1, max(rs) + 1, min(cs) - 1, max(cs) + 1
    seen = {(r0, c0)}; q = deque([(r0, c0)])
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if r0 <= nr <= r1 and c0 <= nc <= c1 \
                    and (nr, nc) not in S and (nr, nc) not in seen:
                seen.add((nr, nc)); q.append((nr, nc))
    return (r1 - r0 + 1) * (c1 - c0 + 1) - len(S) - len(seen)


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    sys.stdout.write(obs.file_header("amax_brute", f"amax-1_{N}", __file__))
    with obs.Reporter(f"amax-1_{N}", script=__file__, total=N) as rep:
        gen = {1: {canon({(0, 0)})}}
        a1 = max(hole_area(S) for S in gen[1])
        print(f"1 {a1}", flush=True)
        rep.beat(done=1, force=True, n=1, A_max=a1, animals=len(gen[1]))
        for k in range(2, N + 1):
            nxt = set()
            for S in gen[k - 1]:
                cand = {nb for cell in S for nb in neigh(cell) if nb not in S}
                for nb in cand:
                    nxt.add(canon(S | {nb}))
            gen[k] = nxt
            del gen[k - 1]                   # free memory; keep only current size
            ak = max(hole_area(S) for S in gen[k])
            print(f"{k} {ak}", flush=True)
            # exponential growth (a(k) animals enumerated): heartbeat each size with
            # the live animal count so the slope is visible before it gets slow.
            rep.beat(done=k, force=True, n=k, A_max=ak, animals=len(gen[k]))
        rep.result = "ok"


if __name__ == "__main__":
    main()
