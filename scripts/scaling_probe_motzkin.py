#!/usr/bin/env python3
"""Scaling probe S4 (lane C, 2026-08-11): the Motzkin identity for the
whole-column king strip state space, and its proposed bijection.

Identity under test: #(reachable nonempty whole-column connectivity states
at height H) + 1 = Motzkin(H+1), observed on H = 1..7 by probe S3b and
matching the strip engine's banked census 834, 2187, 5797 at H = 8, 9, 10.
This probe (i) recounts H = 8..10 with this file's own BFS (independent of
cpp/strip_tm.cpp), (ii) tests the structural claim behind the proposed
bijection at small H exhaustively:

  A state = (occupancy mask, partition of its maximal runs into components),
  and the claim is that a partition occurs iff it is NON-CROSSING on the
  runs. Two king paths in the left half-strip cannot cross without touching:
  a crossing forces two diagonally-crossing steps through one 2x2 block,
  whose four cells are mutually king-adjacent, merging the components. If
  the reachable states are exactly (mask, NC partition of runs), then

    #states + 1 = sum_r C(H+1, 2r) * Catalan(r) = Motzkin(H+1)

  by the classical binomial-Catalan formula for Motzkin numbers
  (#masks with exactly r runs = C(H+1, 2r)).

Usage:
  python3 scripts/scaling_probe_motzkin.py count H      # state census
  python3 scripts/scaling_probe_motzkin.py bijection H  # exhaustive check
"""
import sys
from math import comb

sys.path.insert(0, 'scripts')
from scaling_probe_ch_degree import king_partition_transitions


def motzkin(n):
    M = [1, 1]
    for k in range(2, n + 1):
        M.append(((2 * k + 1) * M[k - 1] + (3 * k - 3) * M[k - 2]) // (k + 2))
    return M[n]


def catalan(n):
    return comb(2 * n, n) // (n + 1)


def runs_of(state):
    """maximal runs of occupied cells: list of (start, end, block label set).
    Returns None if any run spans two component labels (cannot happen: king
    vertical adjacency merges them -- checked as an invariant)."""
    H = len(state)
    runs = []
    i = 0
    while i < H:
        if state[i]:
            j = i
            labels = set()
            while j < H and state[j]:
                labels.add(state[j])
                j += 1
            runs.append((i, j - 1, labels))
            i = j
        else:
            i += 1
    return runs


def is_noncrossing(pairing):
    """pairing: list of block ids per run. Crossing iff exist runs
    a<b<c<d with block(a)=block(c) != block(b)=block(d)."""
    n = len(pairing)
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                for d in range(c + 1, n):
                    if pairing[a] == pairing[c] != pairing[b] == pairing[d]:
                        return False
    return True


def all_nc_states(H):
    """every (mask, non-crossing partition of runs), canonical labels."""
    out = set()
    for mask in range(1, 1 << H):
        # run structure
        base = [1 if mask >> i & 1 else 0 for i in range(H)]
        rr = runs_of(tuple(base))
        r = len(rr)
        # all set partitions of r runs, filtered to non-crossing
        def parts(k, assign, nxt):
            if k == r:
                if is_noncrossing(assign):
                    # canonical relabel in first-occurrence order, write out
                    lab, nl, st = {}, 0, [0] * H
                    for (idx, (s, e, _)) in enumerate(rr):
                        b = assign[idx]
                        if b not in lab:
                            nl += 1
                            lab[b] = nl
                        for i in range(s, e + 1):
                            st[i] = lab[b]
                    out.add(tuple(st))
                return
            for b in range(nxt + 1):
                parts(k + 1, assign + [b], max(nxt, b + 1))
        parts(0, [], 0)
    return out


if __name__ == '__main__':
    mode, H = sys.argv[1], int(sys.argv[2])
    if mode == 'count':
        order, *_ = king_partition_transitions(H)
        S = len(order)
        m = motzkin(H + 1)
        pred = sum(comb(H + 1, 2 * r) * catalan(r)
                   for r in range(0, (H + 1) // 2 + 1))
        print(f'H={H}: states={S} states+1={S + 1} Motzkin(H+1)={m} '
              f'binomial-Catalan sum={pred} '
              f'{"MATCH" if S + 1 == m == pred else "MISMATCH"}', flush=True)
    elif mode == 'bijection':
        order, *_ = king_partition_transitions(H)
        reach = set(order)
        # invariant: every run is single-labelled in every reachable state
        bad_runs = [s for s in reach
                    if any(len(labels) != 1 for (_, _, labels) in runs_of(s))]
        nc = all_nc_states(H)
        only_reach = reach - nc
        only_nc = nc - reach
        print(f'H={H}: reachable={len(reach)} NC-run-states={len(nc)} '
              f'run-invariant-violations={len(bad_runs)} '
              f'reach-not-NC={len(only_reach)} NC-not-reached={len(only_nc)} '
              f'{"BIJECTION HOLDS" if not bad_runs and not only_reach and not only_nc else "FAILS"}',
              flush=True)
        if only_reach:
            print(' crossing/reached examples:', list(only_reach)[:5])
        if only_nc:
            print(' unreached NC examples:', list(only_nc)[:5])
