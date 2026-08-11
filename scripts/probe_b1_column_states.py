#!/usr/bin/env python3
# probe_b1_column_states.py — scaling lane A follow-on 2 (2026-08-11, throwaway).
# Column-aligned reachable state count of B1's colour-symmetrized automaton
# (results/second-source-candidates-B.md, coincidence partitions, clash-zeroing,
# no death rule), for comparison on equal cuts against:
#   - the incumbent connectivity automaton states (2187 at H=9), and
#   - the measured Hankel rank of the computed function (501 at H=9),
# which floors EVERY linear realization of the same count. The gap
# S_B1 / rank is B1's representation overhead; S_B1 / S_incumbent is the
# price of rule-independence in its chosen basis.
#
# State at a column boundary: canonical partition of the column's occupied
# runs into colour classes (vertical adjacency forces same colour within a
# run; classes with no cell in the current column are gone). Transition on
# next fill: each new run's class is forced by king-adjacency to previous-
# column classes (two distinct forced classes -> clash, branch dropped);
# free runs choose any pattern: join a surviving forced/previous class or
# group with other free runs (set partition). Reachable closure by BFS.
# Cost: seconds at H<=9, ~a minute at H=10; 1 core, foreground.
import sys
from itertools import combinations

def runs(fill, H):
    out, cur = [], None
    for r in range(H):
        if fill >> r & 1:
            if cur is None: cur = [r, r]
            else: cur[1] = r
        else:
            if cur: out.append(tuple(cur)); cur = None
    if cur: out.append(tuple(cur))
    return out  # list of (lo, hi) inclusive

def king_adj(run_a, run_b):
    # runs in adjacent columns touch iff intervals within distance 1
    return not (run_a[1] < run_b[0] - 1 or run_b[1] < run_a[0] - 1)

def canon_state(fill, classes):
    m, nxt, out = {}, 0, []
    for c in classes:
        if c not in m: nxt += 1; m[c] = nxt
        out.append(m[c])
    return (fill, tuple(out))

def set_partitions(items):
    if not items: yield []
    else:
        first, rest = items[0], items[1:]
        for part in set_partitions(rest):
            for i in range(len(part)):
                yield part[:i] + [[first] + part[i]] + part[i+1:]
            yield [[first]] + part

def successors(state, fill2, H):
    fill1, classes1 = state
    r1, r2 = runs(fill1, H), runs(fill2, H)
    if not r2: return []
    # forced class per new run from adjacency to old runs
    forced = []
    for b in r2:
        fs = {classes1[i] for i, a in enumerate(r1) if king_adj(a, b)}
        if len(fs) > 1: return []          # clash: branch weight 0
        forced.append(fs.pop() if fs else None)
    out = []
    free_idx = [i for i, f in enumerate(forced) if f is None]
    old_class_ids = sorted(set(classes1))
    # each free run: joins one old class or groups with other free runs (fresh)
    # enumerate: map each free run to an old class or to a fresh-group; fresh
    # groups = set partition of the fresh subset.
    def assign(i, cur, used_old):
        if i == len(free_idx):
            fresh = [j for j in free_idx if cur[j] is None]
            for part in set_partitions(fresh):
                cl = list(cur)
                for gi, grp in enumerate(part):
                    for j in grp: cl[j] = ('f', gi)
                out.append(canon_state(fill2, [cl[k] if forced[k] is None else forced[k] for k in range(len(r2))]))
            return
        j = free_idx[i]
        for oc in old_class_ids:
            cur2 = list(cur); cur2[j] = oc
            assign(i+1, cur2, used_old | {oc})
        cur2 = list(cur); cur2[j] = None   # defer to fresh grouping
        assign(i+1, cur2, used_old)
    base = [forced[k] for k in range(len(r2))]
    start = [None if forced[k] is None else forced[k] for k in range(len(r2))]
    assign(0, start, set())
    return out

def count_states(H):
    alphabet = list(range(1, 1 << H))
    seen = set()
    frontier = []
    for c in alphabet:
        rs = runs(c, H)
        for part in set_partitions(list(range(len(rs)))):
            cl = [0]*len(rs)
            for gi, grp in enumerate(part):
                for j in grp: cl[j] = gi
            s = canon_state(c, cl)
            if s not in seen:
                seen.add(s); frontier.append(s)
    while frontier:
        s = frontier.pop()
        for c in alphabet:
            for t in successors(s, c, H):
                if t not in seen:
                    seen.add(t); frontier.append(t)
    return len(seen)

if __name__ == "__main__":
    hs = [int(a) for a in sys.argv[1:]] or list(range(4, 10))
    prev = None
    print("H : B1 column states : ratio")
    for H in hs:
        n = count_states(H)
        line = f"{H} : {n}"
        if prev: line += f" : x{n/prev:.3f}"
        prev = n
        print(line); sys.stdout.flush()
