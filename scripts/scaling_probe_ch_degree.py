#!/usr/bin/env python3
"""Scaling probe S2 (docs/scaling-exploration-brief.md, lane C, 2026-08-11).

Growth of the minimal-recurrence degree of the per-height cumulative series
C_H(x) (each rational; banked degrees 1, 2, 4, 9, 29, 68 for H = 1..6 -- the
"atoms" q_H of results/strip-engine.md). This probe recomputes C_H mod a
large prime to depth N via an independent column DP (partition frontier,
same mechanism as experiments/king_cis_probe.py but on a semi-infinite
strip with leftmost occupied column fixed), then Berlekamp-Massey mod p
gives the minimal LFSR order = deg of the minimal recurrence (mod p; a
lower bound on the Q-degree, generically exact for a large random prime).

Validation: (i) the series prefix is checked against the banked triangle
(C_H(n) = sum_{h<=H} (H-h+1) T(n,h), n <= 40, results/ns_a40/perheight);
(ii) H <= 6 must reproduce the banked degrees. The new measurement is H = 7
(and H = 8 if the box allows).

Usage: python3 scripts/scaling_probe_ch_degree.py H N
"""
import sys, time
import numpy as np

P = 1_000_003


def king_partition_transitions(H):
    """All (state, mask) -> (target_state, popcount) with state canonical
    partition tuples of length H (0 = empty). Returns state list + per-state
    transition lists. Dead transitions (a component loses contact) dropped;
    single-component detection flag per state for tallying."""
    from collections import deque
    start_states = {}
    trans = {}

    def canon(labels):
        lab, nxt, out = {}, 0, []
        for x in labels:
            if x == 0:
                out.append(0)
            else:
                if x not in lab:
                    nxt += 1
                    lab[x] = nxt
                out.append(lab[x])
        return tuple(out)

    def step(state, mask):
        comps = set(x for x in state if x)
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

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
        return canon(out)

    # discover reachable states by BFS from all first-column masks
    states = {}
    order = []
    q = deque()
    for mask in range(1, 1 << H):
        s = canon(tuple((1 if mask >> i & 1 else 0) for i in range(H)))
        # first column: components = runs of the mask under king adjacency
        # (vertical adjacency only within one column) -> label runs
        labels = [0] * H
        k = 0
        for i in range(H):
            if mask >> i & 1:
                if i > 0 and mask >> (i - 1) & 1:
                    labels[i] = labels[i - 1]
                else:
                    k += 1
                    labels[i] = k
        s = canon(labels)
        key = (s, mask.bit_count())
        start_states.setdefault(s, []).append(mask.bit_count())
        if s not in states:
            states[s] = len(order)
            order.append(s)
            q.append(s)
    while q:
        s = q.popleft()
        tl = []
        for mask in range(1, 1 << H):
            t = step(s, mask)
            if t is None:
                continue
            if t not in states:
                states[t] = len(order)
                order.append(t)
                q.append(t)
            tl.append((states[t], bin(mask).count('1')))
        trans[states[s]] = tl
    onecomp = np.array([1 if max(s) == 1 and len(set(x for x in s if x)) == 1
                        else 0 for s in order], dtype=np.int64)
    return order, states, trans, start_states, onecomp


def series_CH(H, N):
    order, states, trans, start_states, onecomp = king_partition_transitions(H)
    S = len(order)
    dp = np.zeros((S, N + 1), dtype=np.int64)
    for s, cs in start_states.items():
        for c in cs:
            if c <= N:
                dp[states[s], c] += 1
    out = np.zeros(N + 1, dtype=np.int64)
    out += (onecomp[:, None] * dp).sum(axis=0) % P
    for col in range(1, N):
        new = np.zeros_like(dp)
        nz = np.nonzero(dp.any(axis=1))[0]
        if len(nz) == 0:
            break
        for s in nz:
            row = dp[s]
            for (t, c) in trans[s]:
                if c <= N:
                    new[t, c:] += row[:N + 1 - c]
        dp = new % P
        out = (out + (onecomp[:, None] * dp).sum(axis=0)) % P
    return out % P, S


def berlekamp_massey(seq, p):
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for n in range(len(seq)):
        d = seq[n] % p
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % p
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = list(C)
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for i in range(len(B)):
                C[i + m] = (C[i + m] - coef * B[i]) % p
            L, B, b, m = n + 1 - L, T, d, 1
        else:
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for i in range(len(B)):
                C[i + m] = (C[i + m] - coef * B[i]) % p
            m += 1
    return L


if __name__ == '__main__':
    H = int(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    t0 = time.time()
    c, S = series_CH(H, N)
    t1 = time.time()
    # validate against banked triangle
    import os
    T = {}
    for h in range(1, H + 1):
        for line in open(f'results/ns_a40/perheight/h{h}.out'):
            n, v = line.split()
            T[(int(n), h)] = int(v)
    ok = all(
        c[n] == sum((H - h + 1) * T.get((n, h), 0) for h in range(1, H + 1)) % P
        for n in range(1, min(40, N) + 1))
    L = berlekamp_massey([int(x) for x in c[1:]], P)
    print(f'H={H} N={N} states={S} banked-prefix-check(n<=40): '
          f'{"OK" if ok else "MISMATCH"}  BM-degree={L} '
          f'(needs N >= 2*deg+slack to be trusted; series time {t1-t0:.1f}s)')
