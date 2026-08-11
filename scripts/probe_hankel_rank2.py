#!/usr/bin/env python3
# probe_hankel_rank2.py — exact observability-space dimension (closure, not
# sampling; supersedes probe_hankel_rank.py's sampled ranks, which wobbled
# 233/235 at H=9). Same automaton. dim span{T_w accept : all words w} mod p,
# closed under every fill; with all states reachable from length-1 prefixes,
# this IS the Hankel rank of f over F_p, and rank over Q is >= it.
# Cost: H<=9 ~1 min; H=10 minutes (run via tmux if slow).
import sys
import numpy as np
from probe_hankel_rank import build

P = (1 << 31) - 1

def observability_dim(H, x_weight=1):
    alphabet, states, trans = build(H)
    S = len(states)
    idx = states
    accept = np.zeros(S, dtype=np.int64)
    for s, i in states.items():
        if len({v for v in s if v}) == 1: accept[i] = 1
    per_fill = []
    fillw = []
    for c in alphabet:
        tgt = np.full(S, -1, dtype=np.int64)
        for s, i in states.items():
            t = trans[(s, c)]
            if t is not None: tgt[i] = idx[t]
        per_fill.append(tgt)
        fillw.append(pow(x_weight, bin(c).count('1'), P))
    basis = []          # rows in echelon form: list of (pivot_index, vector)
    def reduce_add(v):
        v = v % P
        for piv, b in basis:
            if v[piv]:
                v = (v - v[piv] * b) % P
        nz = np.nonzero(v)[0]
        if len(nz) == 0: return False
        piv = int(nz[0])
        v = v * pow(int(v[piv]), P-2, P) % P
        basis.append((piv, v))
        return True
    work = [accept.copy()]
    reduce_add(accept)
    while work:
        v = work.pop()
        for tgt, w in zip(per_fill, fillw):
            nv = np.where(tgt >= 0, v[np.clip(tgt, 0, S-1)], 0) * w % P
            if nv.any():
                nvr = nv.copy()
                if reduce_add(nvr):
                    work.append(nv)
    return S, len(basis)

if __name__ == "__main__":
    hs = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(range(4, 10))
    prev = None
    print("H : states : obs-dim(x=1) : obs-dim(x=rand)")
    for H in hs:
        S, d1 = observability_dim(H, 1)
        _, d2 = observability_dim(H, 123456789)
        line = f"{H} : {S} : {d1} : {d2}"
        if prev: line += f"   ratio states x{S/prev[0]:.3f} dim x{d1/prev[1]:.3f}"
        prev = (S, d1)
        print(line); sys.stdout.flush()
