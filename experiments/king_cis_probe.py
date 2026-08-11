#!/usr/bin/env python3
"""Probe (second-source coverage map, Teammate C, 2026-08-11; throwaway).

Counts connected induced (non-null) subgraphs of the n x n king graph by a
column DP carrying a king-connectivity partition of the previous column --
the repo's connectivity notion -- and compares against OEIS A286139's b-file
(terms 1..16 computed independently by Andrew Howroyd; n<=4 brute-forced by
Giovanni Resta via Mathematica ConnectedGraphQ). Agreement = external,
definition-level confirmation of the king-connectivity rule on boxes up to
n x n with cluster sizes up to n^2 (beyond any banked enumeration depth).

Each connected subset is tallied once, at its rightmost occupied column:
after processing column c, every state whose partition has exactly one
component contributes (stopping there yields a connected subset).
A state loses a component with no cell in the new column -> discarded
(the subset can never reconnect; its completion was tallied earlier).
"""
import sys, time

A286139 = [1, 15, 388, 37196, 14765089, 24076152503, 159850328891568,
           4290837646252661680, 463376724731585422732393,
           200665409586497566263900755703]


def count_cis(n):
    # state: tuple of length n, 0 = empty, else component label (canonical)
    total = 0
    dp = {}
    empty = tuple([0] * n)
    for _ in range(n):  # columns
        ndp = {}
        src = dict(dp)
        src[empty] = src.get(empty, 0) + 1  # subsets may start at this column
        for state, cnt in src.items():
            comps = set(x for x in state if x)
            for mask in range(1 if state == empty else 0, 1 << n):
                if mask == 0:
                    continue
                # union-find over old components and new cells
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
                newcells = [i for i in range(n) if mask >> i & 1]
                for i in newcells:
                    parent[('n', i)] = ('n', i)
                for i in newcells:
                    if i > 0 and (mask >> (i - 1) & 1):
                        union(('n', i), ('n', i - 1))
                    for j in (i - 1, i, i + 1):  # king adjacency to old column
                        if 0 <= j < n and state[j]:
                            union(('n', i), ('o', state[j]))
                # any old component with no new-column contact dies -> invalid
                touched = set(find(('o', c)) for c in comps)
                alive_roots = set(find(('n', i)) for i in newcells)
                if not touched <= alive_roots:
                    continue
                # canonical relabel of new column
                lab, nxt, out = {}, 0, [0] * n
                for i in newcells:
                    r = find(('n', i))
                    if r not in lab:
                        nxt += 1
                        lab[r] = nxt
                    out[i] = lab[r]
                key = tuple(out)
                ndp[key] = ndp.get(key, 0) + cnt
        dp = ndp
        for state, cnt in dp.items():
            if len(set(x for x in state if x)) == 1:
                total += cnt
    return total


if __name__ == '__main__':
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    for n in range(1, nmax + 1):
        t0 = time.time()
        v = count_cis(n)
        ref = A286139[n - 1] if n <= len(A286139) else None
        verdict = 'MATCH' if v == ref else ('MISMATCH' if ref else 'no-ref')
        print(f'n={n} {v} {verdict} ({time.time()-t0:.1f}s)', flush=True)
