#!/usr/bin/env python3
# probe_hankel_rank.py — scaling-exploration lane A (2026-08-11, throwaway probe).
#
# Question: does the EXACT minimal linear realization of the height-H king-strip
# counting automaton have dimension below the frontier state count?
# Object: the Hankel matrix of the word function
#     f(w) = [cells(w) form exactly ONE king-connected component],
# w a word of nonempty column-fills (alphabet 2^H - 1). Row space is spanned by
# rows indexed by reachable automaton states; minimal realization dim = rank.
# If rank ~= #states: NO field-linear method (weighted automaton, temporal MPS,
# rank-compressed DP) can beat the frontier dimension — a lower bound.
# If rank << #states: an exactly-compressed transfer exists; measure its growth.
#
# Distinct from results/closed-doors.md, which measured the
# SPATIAL (within-column) Schmidt rank of the frontier vector. This is the
# TEMPORAL cut: prefix x suffix over column words.
#
# Method: build incumbent-style automaton (connectivity partitions + stranded-
# death sink), reachable states from all single-column starts; observability
# vectors by backward application over BFS-sampled suffix words until columns
# >= 1.5x states; rank by vectorized Gaussian elimination mod p = 2^31 - 1.
# Also x-weighted variant (cell weight x, random x mod p) — rank over Q(x)
# is >= the weighted-point rank.
#
# Cost: H <= 9 foreground (<5 min, 1 core). H=10 only via --big (tmux).
import sys, random
import numpy as np

P = (1 << 31) - 1
random.seed(11)

def runs_partition(fill, H):
    """components of a single column = vertical runs; return tuple part ids."""
    part = [0]*H
    nid = 0
    for r in range(H):
        if fill >> r & 1:
            if r > 0 and (fill >> (r-1) & 1):
                part[r] = part[r-1]
            else:
                nid += 1
                part[r] = nid
    return tuple(part)

def canon(part):
    m, nxt, out = {}, 0, []
    for x in part:
        if x == 0: out.append(0)
        else:
            if x not in m: nxt += 1; m[x] = nxt
            out.append(m[x])
    return tuple(out)

def transition(state, fill, H):
    """state: tuple part ids of prev column (0=empty). Returns new state or None (dead)."""
    if fill == 0: return None
    # union-find over prev-column blocks + new-column cells (this IS the
    # incumbent rule; we are measuring its Hankel rank, so that is the point)
    parent = {}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    old_blocks = {x for x in state if x}
    for b in old_blocks: parent[('o', b)] = ('o', b)
    new_cells = [r for r in range(H) if fill >> r & 1]
    for r in new_cells: parent[('n', r)] = ('n', r)
    for r in new_cells:
        if r > 0 and (fill >> (r-1) & 1): union(('n', r), ('n', r-1))
        for dr in (-1, 0, 1):
            rr = r + dr
            if 0 <= rr < H and state[rr]:
                union(('n', r), ('o', state[rr]))
    # stranded death: an old block with no representative among new cells dies
    reach = {find(('n', r)) for r in new_cells}
    for b in old_blocks:
        if find(('o', b)) not in reach:
            return None
    newpart = [0]*H
    roots, nid = {}, 0
    for r in new_cells:
        root = find(('n', r))
        if root not in roots: nid += 1; roots[root] = nid
        newpart[r] = roots[root]
    return canon(tuple(newpart))

def build(H):
    alphabet = list(range(1, 1 << H))
    start_states = {}
    for c in alphabet:
        start_states.setdefault(canon(runs_partition(c, H)), []).append(c)
    frontier = list(start_states)
    states = {s: i for i, s in enumerate(frontier)}
    trans = {}
    while frontier:
        s = frontier.pop()
        for c in alphabet:
            t = transition(s, c, H)
            trans[(s, c)] = t
            if t is not None and t not in states:
                states[t] = len(states)
                frontier.append(t)
    return alphabet, states, trans

def hankel_rank(H, x_weight=None, colfactor=1.5, seed=1):
    alphabet, states, trans = build(H)
    S = len(states)
    idx = states      # read-only alias; the comprehension rebuilt it verbatim
    accept = np.zeros(S, dtype=np.int64)
    for s, i in states.items():
        blocks = {v for v in s if v}
        accept[i] = 1 if len(blocks) == 1 else 0
    rng = random.Random(seed)
    xw = 1 if x_weight is None else x_weight
    # suffix vectors: v[s] = weighted completions of suffix word w from state s
    # backward: (T_c v)[s] = weight(c) * v[trans(s,c)]
    fillw = {c: pow(xw, bin(c).count('1'), P) for c in alphabet}
    cols, pool = [accept], [accept]
    target = int(colfactor * S) + 8
    # organize transitions per fill as index arrays for vectorization
    per_fill = {}
    for c in alphabet:
        tgt = np.full(S, -1, dtype=np.int64)
        for s, i in states.items():
            t = trans[(s, c)]
            if t is not None: tgt[i] = idx[t]
        per_fill[c] = tgt
    while len(cols) < target:
        newpool = []
        picks = rng.sample(alphabet, min(len(alphabet), max(4, target // max(1, len(pool)) // 2 + 2)))
        for v in pool:
            for c in picks:
                tgt = per_fill[c]
                nv = np.where(tgt >= 0, v[np.clip(tgt, 0, S-1)], 0) * fillw[c] % P
                if nv.any():
                    newpool.append(nv); cols.append(nv)
                    if len(cols) >= target: break
            if len(cols) >= target: break
        if not newpool: break
        pool = newpool
    M = np.stack(cols, axis=1) % P  # S x cols
    # Gaussian elimination mod P, vectorized over columns
    rank, row = 0, 0
    M = M.copy()
    ncols = M.shape[1]
    for col in range(ncols):
        piv = None
        for r in range(row, S):
            if M[r, col] % P: piv = r; break
        if piv is None: continue
        M[[row, piv]] = M[[piv, row]]
        inv = pow(int(M[row, col]), P-2, P)
        M[row] = M[row] * inv % P
        mask = M[row+1:, col] % P != 0
        if mask.any():
            M[row+1:][mask] = (M[row+1:][mask] - np.outer(M[row+1:, col][mask], M[row])) % P
        rank += 1; row += 1
        if row == S: break
    return S, rank, len(cols)

if __name__ == "__main__":
    big = "--big" in sys.argv
    hs = range(4, 11 if big else 10)
    print("H : states : rank(x=1) : rank(x=rand) : cols")
    prev = {}
    for H in hs:
        S, r1, nc = hankel_rank(H, None)
        xr = random.Random(99).randrange(2, P)
        S2, r2, nc2 = hankel_rank(H, xr)
        line = f"{H} : {S} : {r1} : {r2} : {nc}"
        if prev:
            line += f"   ratios S x{S/prev['S']:.3f} r1 x{r1/prev['r1']:.3f}"
        prev = dict(S=S, r1=r1)
        print(line); sys.stdout.flush()
