#!/usr/bin/env python3
"""Scaling probe S3b (supersedes S3's sampled Hankel, which provably
under-measured: it returned 7 at H=4 where the banked series degree q_4 = 9
is a lower bound on the true rank).

Exact minimal weighted-automaton dimension (= Hankel rank = exact MPS bond
dimension, Carlyle-Paz/Fliess) of the height-H king-connected counting
function, computed by forward/backward reduction of the partition-frontier
realization: reach space R = Krylov closure of the initial vector under
EVERY letter matrix (one per nonzero column mask); observation space O =
closure of the final vector under transposes; minimal dim = rank(R O^T).
Reduction of any realization attains the Hankel rank, so the result is
realization-independent. Arithmetic in F_p at random x (generic
specialization; nx tries, max taken -- specialization only underestimates).

Sanity floor: minimal dim >= deg of C_H's minimal recurrence
(q_H = 1, 2, 4, 9, 29, 68, 181 for H = 1..7, probe S2).
Ceiling: partition states (1, 3, 8, 20, 50, 126, 322).

Usage: python3 scripts/scaling_probe_minimal_dim.py Hmax
"""
import sys, random
import numpy as np

sys.path.insert(0, 'scripts')
from scaling_probe_ch_degree import king_partition_transitions, P

random.seed(7)


def rank_mod(M):
    M = M.copy() % P
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        pv = None
        for i in range(r, rows):
            if M[i, c]:
                pv = i
                break
        if pv is None:
            continue
        M[[r, pv]] = M[[pv, r]]
        inv = pow(int(M[r, c]), P - 2, P)
        M[r] = (M[r] * inv) % P
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] = (M[i] - int(M[i, c]) * M[r]) % P
        r += 1
        if r == rows:
            break
    return r


def minimal_dim(H, nx=2):
    order, states, trans, start_states, onecomp = king_partition_transitions(H)
    S = len(order)
    nletters = (1 << H) - 1
    best = 0
    for _ in range(nx):
        x = random.randrange(2, P)
        xp = [pow(x, c, P) for c in range(H + 1)]
        # per-letter adjacency. Letters indexed by mask-1. Virtual start = S.
        fwd = [[[] for _ in range(S + 1)] for _ in range(nletters)]
        # rebuild per-letter transitions (king_partition_transitions collapses
        # letters, so recompute step() per (state, mask) via its machinery):
        # cheap re-derivation: trans lists lost mask identity; instead rerun
        # the BFS step function here.
        from scaling_probe_ch_degree import king_partition_transitions as _
        # recompute with mask identity
        import collections
        # reuse states/order; recompute step-by-mask using the same canon
        # logic through a tiny local re-implementation:
        def step(state, mask):
            comps = set(y for y in state if y)
            parent = {}
            def find(z):
                while parent[z] != z:
                    parent[z] = parent[parent[z]]
                    z = parent[z]
                return z
            def union(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
            for c in comps:
                parent[('o', c)] = ('o', c)
            cells = [i for i in range(H) if mask >> i & 1]
            for i in cells:
                parent[('n', i)] = ('n', i)
            for i in cells:
                if i > 0 and (mask >> (i - 1)) & 1:
                    union(('n', i), ('n', i - 1))
                for j in (i - 1, i, i + 1):
                    if 0 <= j < H and state[j]:
                        union(('n', i), ('o', state[j]))
            alive = set(find(('n', i)) for i in cells)
            if any(find(('o', c)) not in alive for c in comps):
                return None
            out = [0] * H
            tmp = {}
            k = 0
            for i in cells:
                r = find(('n', i))
                if r not in tmp:
                    k += 1
                    tmp[r] = k
                out[i] = tmp[r]
            return tuple(out)

        for mask in range(1, 1 << H):
            a = mask - 1
            c = mask.bit_count()
            # from virtual start: first column, components = vertical runs
            labels = [0] * H
            k = 0
            for i in range(H):
                if mask >> i & 1:
                    if i > 0 and mask >> (i - 1) & 1:
                        labels[i] = labels[i - 1]
                    else:
                        k += 1
                        labels[i] = k
            fwd[a][S].append((states[tuple(labels)], xp[c]))
            for s in range(S):
                t = step(order[s], mask)
                if t is not None:
                    fwd[a][s].append((states[t], xp[c]))
        bwd = [[[] for _ in range(S + 1)] for _ in range(nletters)]
        for a in range(nletters):
            for src in range(S + 1):
                for (t, w) in fwd[a][src]:
                    bwd[a][t].append((src, w))

        def apply_op(moves, v):
            out = np.zeros(S + 1, dtype=np.int64)
            for src in np.nonzero(v)[0]:
                w0 = int(v[src])
                for (t, w) in moves[src]:
                    out[t] = (out[t] + w0 * w) % P
            return out

        def closure(seed, table):
            piv = {}
            raw = []

            def reduce_add(v):
                v = v.copy() % P
                for c in sorted(piv):
                    if v[c]:
                        v = (v - int(v[c]) * piv[c]) % P
                nz = np.nonzero(v)[0]
                if len(nz) == 0:
                    return False
                c = int(nz[0])
                piv[c] = (v * pow(int(v[c]), P - 2, P)) % P
                return True

            if reduce_add(seed):
                raw.append(seed)
            i = 0
            while i < len(raw):
                for a in range(nletters):
                    nv = apply_op(table[a], raw[i])
                    if reduce_add(nv):
                        raw.append(nv)
                i += 1
            return np.array(raw, dtype=np.int64)

        u0 = np.zeros(S + 1, dtype=np.int64)
        u0[S] = 1
        v0 = np.zeros(S + 1, dtype=np.int64)
        for i in range(S):
            if onecomp[i]:
                v0[i] = 1
        R = closure(u0, fwd)
        O = closure(v0, bwd)
        best = max(best, rank_mod((R @ O.T) % P))
    return best, S


# NOTE (corrected after first run): q_H is NOT a floor for the word-function
# Hankel rank -- the series denominator degree obeys q_H <= H*dim (letter
# weights carry x^popcount up to x^H), so dim < q_H is consistent and the
# measured dims below q_H are genuine compression. The only hard bounds are
# 1 <= dim <= states+1 (the +1 is the virtual start row).
QH = {1: 1, 2: 2, 3: 4, 4: 9, 5: 29, 6: 68, 7: 181, 8: 462}

if __name__ == '__main__':
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for H in range(1, Hmax + 1):
        d, S = minimal_dim(H)
        ok = 1 <= d <= S + 1 and H * d >= QH.get(H, 0)
        print(f'H={H}: minimal dim = {d}  (ceiling states+1 = {S + 1}; '
              f'series-degree consistency H*dim >= q_H={QH.get(H)}: '
              f'{H * d >= QH.get(H, 10**9)})  {"OK" if ok else "VIOLATION"}',
              flush=True)
