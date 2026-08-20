#!/usr/bin/env python3
# probe_hankel_rank2.py — exact observability-space dimension (closure, not
# sampling; supersedes probe_hankel_rank.py's sampled ranks, which wobbled
# 233/235 at H=9). Same automaton. dim span{T_w accept : all words w} mod p,
# closed under every fill; with all states reachable from length-1 prefixes,
# this IS the Hankel rank of f over F_p, and rank over Q is >= it.
#
# PURPOSE (H=11, 2026-08-20). A-S1 (second-source:results/scaling-exploration-A.md)
# measured this ladder to H=10: 6, 17, 35, 88, 204, 501, 1217, independently
# reproduced by lane C. Two readings of those seven points disagree about the
# asymptotics, and H=11 separates them:
#     power-law quotient, floor base exactly 3  -> predicts 3091  (class closed)
#     geometric quotient, floor base ~2.79      -> predicts 3281  (a real opening)
# 6.2% apart, so one closure settles which.
#
# COMMAND     python3 scripts/probe_hankel_rank2.py --anchor
#             python3 scripts/probe_hankel_rank2.py --x 1 11
#             python3 scripts/probe_hankel_rank2.py --x 123456789 11
# MACHINE     ayr (gympie is banned for project processes)
# COST        A-S1 sized H=11 at 7.2 h and 0.37 GB per x-value, from its own
#             measured 26.5 min for the H=10 pair. That timing was on gympie;
#             ayr's per-core speed is not the same, so treat 7.2 h as the
#             origin of the estimate and read the heartbeat for the truth.
#             Single-core each, so the two x-values run side by side.
# GATE        --anchor reproduces H=4..7 = 6, 17, 35, 88 and exits nonzero
#             otherwise. Run it before trusting an H=11 number.
# KILL        ps to find the pid, then kill <pid>. No resume: a killed run
#             restarts from scratch (the closure has no checkpoint).
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_hankel_rank import build

# A-S1's ladder, second-source:results/scaling-exploration-A.md.
BANKED = {4: 6, 5: 17, 6: 35, 7: 88, 8: 204, 9: 501, 10: 1217}
HEARTBEAT_S = 60.0

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
    t0 = last = time.time()
    while work:
        v = work.pop()
        for tgt, w in zip(per_fill, fillw):
            nv = np.where(tgt >= 0, v[np.clip(tgt, 0, S-1)], 0) * w % P
            if nv.any():
                nvr = nv.copy()
                if reduce_add(nvr):
                    work.append(nv)
        now = time.time()
        if now - last >= HEARTBEAT_S:
            last = now
            print("event=heartbeat job=hankel_closure H=%d x=%d elapsed_s=%.1f "
                  "dim=%d queue=%d states=%d" % (H, x_weight, now - t0,
                                                 len(basis), len(work), S),
                  flush=True)
    return S, len(basis)


def anchor():
    """RED-adjacent gate: the cheap heights must reproduce A-S1's ladder."""
    bad = 0
    for H in (4, 5, 6, 7):
        S, d = observability_dim(H, 1)
        ok = (d == BANKED[H])
        print("anchor H=%d states=%d dim=%d banked=%d %s"
              % (H, S, d, BANKED[H], "ok" if ok else "MISMATCH"))
        bad += 0 if ok else 1
    if bad:
        print("ANCHOR FAILED: %d height(s) disagree with A-S1" % bad)
        sys.exit(1)
    print("ANCHOR OK")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--anchor" in args:
        anchor()
        sys.exit(0)
    xs = None
    if "--x" in args:
        i = args.index("--x")
        xs = [int(args[i + 1])]
        del args[i:i + 2]
    hs = [int(a) for a in args if a.isdigit()] or list(range(4, 10))
    prev = None
    print("H : states : obs-dim(x=1) : obs-dim(x=rand)", flush=True)
    for H in hs:
        if xs is None:
            S, d1 = observability_dim(H, 1)
            _, d2 = observability_dim(H, 123456789)
            line = f"{H} : {S} : {d1} : {d2}"
        else:
            S, d1 = observability_dim(H, xs[0])
            line = f"{H} : {S} : x={xs[0]} : {d1}"
        if H in BANKED:
            line += "   banked %d %s" % (BANKED[H],
                                         "ok" if d1 == BANKED[H] else "MISMATCH")
        if prev: line += f"   ratio states x{S/prev[0]:.3f} dim x{d1/prev[1]:.3f}"
        prev = (S, d1)
        print(line, flush=True)
