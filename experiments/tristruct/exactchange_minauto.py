#!/usr/bin/env python3
"""Exact Change probe 4: the minimized automaton, built a priori.

Probe 3 (exactchange_kernel_probe.py) established that the GF(2) Nerode class
of a strip-automaton state is EXACTLY the multiset of its block neighborhoods
N(b) = rows(b) expanded +-1 -- and the transition rule reads nothing else, so
this holds over every field.  This script builds the minimized automaton
DIRECTLY on N-families, never touching partition states:

  state    = multiset of neighborhood sets {N(b)}
  step     = new mask's vertical runs attach to family member Nb iff the run
             intersects Nb; any Nb hit by no run strands (dead); runs merge
             through shared old blocks; new family = {rows(new block) +- 1}
  accept   = |family| == 1

Purposes:
  (1) anchor: state counts must equal the probe-3 Nerode counts and the
      observability rank must equal A034299 at every banked height;
  (2) extend the rank ladder to H = 13 (A034299 predicts 3643) at ~20x less
      state cost than the partition automaton -- the legitimacy test for the
      OEIS identification (9 banked terms vs an order-4 recurrence);
  (3) bank the minimized state-count sequence N(H) itself for OEIS lookup
      (8, 19, 43, 101, 239, 575, ... growth ~2.41 -- silver-ratio scent).

Usage: exactchange_minauto.py MAXH [--count-only]
"""
import sys
import time

BANKED_NERODE = {4: 8, 5: 19, 6: 43, 7: 101, 8: 239, 9: 575, 10: 1399}
BANKED_RANK = {4: 6, 5: 15, 6: 27, 7: 58, 8: 112, 9: 229, 10: 453, 11: 912,
               12: 1818}


def a034299(H):
    return (2 ** (H + 4) - (-1) ** H * (6 * H + 7) - 9) // 36


def mask_runs(mask, H):
    """Maximal vertical runs of mask, as row-sets (frozen bitmasks)."""
    runs = []
    r = 0
    while r < H:
        if mask >> r & 1:
            r0 = r
            while r < H and mask >> r & 1:
                r += 1
            runs.append(((1 << r) - 1) ^ ((1 << r0) - 1))
        else:
            r += 1
    return runs


def expand(rows, H):
    """rows bitmask -> neighborhood bitmask (rows +-1, clipped)."""
    full = (1 << H) - 1
    return (rows | rows << 1 | rows >> 1) & full


def build_min_automaton(H):
    """States: sorted tuple (with multiplicity) of N-bitmasks.  Returns
    (order, delta dict (si, mask)->sj or -1, accept list, masks, init dict
    mask->si)."""
    masks = list(range(1, 1 << H))
    runcache = {m: mask_runs(m, H) for m in masks}

    def initial(mask):
        return tuple(sorted(expand(r, H) for r in runcache[mask]))

    def step(fam, mask):
        runs = runcache[mask]
        nr = len(runs)
        # union-find over runs; old family members attach runs
        parent = list(range(nr))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for Nb in fam:
            hit = [i for i, r in enumerate(runs) if r & Nb]
            if not hit:
                return None            # stranded block
            for i in hit[1:]:
                parent[find(hit[0])] = find(i)
        comp = {}
        for i in range(nr):
            comp.setdefault(find(i), 0)
            comp[find(i)] |= runs[i]
        return tuple(sorted(expand(rows, H) for rows in comp.values()))

    states, order, todo = {}, [], []
    init = {}
    for m in masks:
        s = initial(m)
        init[m] = s
        if s not in states:
            states[s] = len(states)
            order.append(s)
            todo.append(s)
    delta = {}
    while todo:
        s = todo.pop()
        si = states[s]
        for m in masks:
            t = step(s, m)
            if t is None:
                delta[(si, m)] = -1
            else:
                if t not in states:
                    states[t] = len(states)
                    order.append(t)
                    todo.append(t)
                delta[(si, m)] = states[t]
    accept = [len(s) == 1 for s in order]
    initidx = {m: states[s] for m, s in init.items()}
    return order, delta, accept, masks, initidx


def obs_rank(order, delta, accept, masks):
    """GF(2) observability rank; frontier vectors as numpy bool, reduction
    rows as ints (same scheme as exactchange_phi_probe.obs_basis_gf2)."""
    import numpy as np
    n = len(order)
    D = np.full((n, len(masks)), -1, dtype=np.int64)
    for mi, m in enumerate(masks):
        for s in range(n):
            D[s, mi] = delta[(s, m)]
    basis = {}

    def reduce_add(row):
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                return True
        return False

    def vec_to_int(v):
        return int.from_bytes(np.packbits(v[::-1]).tobytes(), 'big')

    g0 = np.array(accept, dtype=bool)
    reduce_add(vec_to_int(g0))
    frontier = [g0]
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(len(masks)):
                d = D[:, mi]
                h = np.zeros(n, dtype=bool)
                ok = d >= 0
                h[ok] = g[d[ok]]
                if reduce_add(vec_to_int(h)):
                    nxt.append(h)
        frontier = nxt
    return len(basis)


def brute_anchor(H, W):
    """Count connected king subsets of HxW using every column, via the
    minimized automaton, against BFS brute force.  Semantic RED anchor."""
    from itertools import product
    order, delta, accept, masks, initidx = build_min_automaton(H)
    total = 0
    cur = {}
    for m in masks:
        cur[initidx[m]] = cur.get(initidx[m], 0) + 1
    for _ in range(W - 1):
        nxt = {}
        for si, c in cur.items():
            for m in masks:
                t = delta[(si, m)]
                if t >= 0:
                    nxt[t] = nxt.get(t, 0) + c
        cur = nxt
    total = sum(c for si, c in cur.items() if accept[si])

    NB = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
          if (dx, dy) != (0, 0)]
    brute = 0
    for bits in product([0, 1], repeat=H * W):
        cells = [(i // H, i % H) for i, b in enumerate(bits) if b]
        if not cells or {x for x, _ in cells} != set(range(W)):
            continue
        seen, st = {cells[0]}, [cells[0]]
        cs = set(cells)
        while st:
            x, y = st.pop()
            for dx, dy in NB:
                c = (x + dx, y + dy)
                if c in cs and c not in seen:
                    seen.add(c)
                    st.append(c)
        if len(seen) == len(cells):
            brute += 1
    return total, brute


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    maxh = int(args[0]) if args else 12
    minh = int(args[1]) if len(args) > 1 else 4
    count_only = "--count-only" in sys.argv

    # semantic anchor: the minimized automaton must COUNT correctly
    for (h, w) in ((2, 3), (3, 3), (3, 4)):
        a, b = brute_anchor(h, w)
        assert a == b, f"brute anchor H={h} W={w}: auto {a} != brute {b}"
        print(f"brute anchor H={h} W={w}: {a} OK", flush=True)

    print("\nH  minstates  rank  A034299  (times)")
    for H in range(minh, maxh + 1):
        t0 = time.time()
        order, delta, accept, masks, _ = build_min_automaton(H)
        n = len(order)
        tb = time.time() - t0
        if H in BANKED_NERODE:
            assert n == BANKED_NERODE[H], f"H={H}: {n} != banked Nerode"
        if count_only:
            print(f"{H}  {n}  -  {a034299(H)}   (build {tb:.1f}s)", flush=True)
            continue
        r = obs_rank(order, delta, accept, masks)
        want = a034299(H)
        flag = "OK" if r == want else "** MISMATCH **"
        if H in BANKED_RANK:
            assert r == BANKED_RANK[H], f"H={H}: rank {r} != banked"
        print(f"{H}  {n}  {r}  {want}  {flag}  (build {tb:.1f}s, "
              f"rank {time.time()-t0-tb:.1f}s)", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
