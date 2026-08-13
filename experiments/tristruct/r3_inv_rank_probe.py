#!/usr/bin/env python3
"""r3_inv_rank_probe.py -- queue row INV-4: does the minimal linear dimension
of the strip-counting functional COLLAPSE in characteristic 2?

Background. A-S1 (git show second-source:results/scaling-exploration-A.md)
measured the temporal Hankel rank of the height-H strip automaton mod
p = 2^31-1: H=4..10 -> 6,17,35,88,204,501,1217 against Motzkin(H+1)-1 states,
floor growth ~2.79x/height, non-constructive.  The CKN/BCKN literature gets
its big wins (2^(k/2) vs 2^k) from GF(2)-rank collapse of connectivity
matrices.  INV-4 asks whether the same collapse happens HERE: is the Hankel
rank of the strip functional over GF(2) (and over GF(2^16) for the
cell-graded version) materially below the mod-p rank?  If not, rank-based
compression buys nothing beyond A-S1's already-measured (and
non-constructive) headroom, and the row closes.

Object. The incumbent-rule strip automaton at height H: alphabet = nonempty
column fills (2^H-1 symbols), states = king-connectivity partitions of the
current column, stranded component -> dead sink, f(w) = [all placed cells
form exactly one king-connected component].  The automaton is DETERMINISTIC,
so every reachability vector is a unit vector and the Hankel rank of f over
any field equals the dimension of the observability closure
span{ g0 = accept, g -> g o delta_m (times t^|m| in the graded case) }.
T(n,H) is a fixed linear combination of these functionals (grading + exact-
height second difference), so this rank is the floor for any field-linear
realization of the mod-2 (resp. graded) count.

Regressions / RED:
  * state census must equal Motzkin(H+1)-1 (king-column-motzkin, and A-S1's
    table) at every H -- the automaton is rebuilt here from the definition;
  * graded f cross-checked against brute-force enumeration of connected
    subsets by (width, n) at H<=3, W<=4;
  * RED control: dropping the diagonal (r-1) adjacency from the merge step
    must break the Motzkin census (it does; assert inverted).

Outputs: for H=4..9(10): states, rank over GF(2) at x=1, rank over GF(2^16)
at random t (two t values; graded), alongside A-S1's mod-p rank quoted for
comparison.  Exact 'before' numbers at H=21: Motzkin(22)-1, the B1 column-cut
count sum_k C(22,2k)*Bell(k) (A-S6 closed form), and the valid spin-coloring
count (no AB/BA vertical adjacency).

Laptop, exact arithmetic, throwaway.  Usage: r3_inv_rank_probe.py [MAXH]
"""

import sys
import time
import numpy as np
from math import comb
from functools import lru_cache

# ---------- exact 'before' numbers ----------

@lru_cache(None)
def motzkin(n):
    if n <= 1:
        return 1
    return ((2 * n + 1) * motzkin(n - 1) + (3 * n - 3) * motzkin(n - 2)) // (n + 2)


@lru_cache(None)
def bell(n):
    if n == 0:
        return 1
    return sum(comb(n - 1, k) * bell(k) for k in range(n))


def b1_colcut(H):
    """A-S6: B1 column-cut states = sum_k C(H+1,2k) * Bell(k)."""
    return sum(comb(H + 1, 2 * k) * bell(k) for k in range(0, (H + 1) // 2 + 1))


def valid_colorings(H):
    """Column colorings over {E,A,B}, occupied runs monochromatic ==
    sequences avoiding adjacent AB/BA."""
    # vec = (ends E, ends A, ends B)
    e, a, b = 1, 1, 1
    for _ in range(H - 1):
        e, a, b = e + a + b, e + a, e + b
    return e + a + b


# ---------- the strip automaton ----------

def build_automaton(H, red=False):
    """States: canonical partition of a nonempty column mask into components.
    Representation: tuple over rows 0..H-1, -1 = empty, else block id in
    first-appearance order.  Returns (states list, delta[state][mask] ->
    state index or -1 (dead), accept bool array)."""
    DEAD = -1

    def canon(lbl):
        seen = {}
        out = []
        for v in lbl:
            if v < 0:
                out.append(-1)
            else:
                if v not in seen:
                    seen[v] = len(seen)
                out.append(seen[v])
        return tuple(out)

    def initial(mask):
        lbl, run = [], -2
        blk = -1
        for r in range(H):
            if mask >> r & 1:
                if run != r - 1:
                    blk += 1
                lbl.append(blk)
                run = r
            else:
                lbl.append(-1)
        return canon(tuple(lbl))

    def step(state, mask):
        # union-find over old blocks (tag 'o',i) and new runs
        parent = {}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry

        old_blocks = set(v for v in state if v >= 0)
        for b in old_blocks:
            parent[('o', b)] = ('o', b)
        # new cells: label by vertical run
        newlbl = [-1] * H
        run = -2
        blk = -1
        for r in range(H):
            if mask >> r & 1:
                if run != r - 1:
                    blk += 1
                    parent[('n', blk)] = ('n', blk)
                newlbl[r] = blk
                run = r
        # cross-column adjacency: new cell r ~ old cells r-1, r, r+1
        for r in range(H):
            if newlbl[r] < 0:
                continue
            offs = (0, 1) if red else (-1, 0, 1)
            for dr in offs:
                rr = r + dr
                if 0 <= rr < H and state[rr] >= 0:
                    union(('n', newlbl[r]), ('o', state[rr]))
        # stranding: any old block with no new neighbor -> dead
        newroots = {find(('n', b)) for b in range(blk + 1)}
        for b in old_blocks:
            if find(('o', b)) not in newroots:
                return None
        # relabel new column by root
        rootid = {}
        out = []
        for r in range(H):
            if newlbl[r] < 0:
                out.append(-1)
            else:
                rt = find(('n', newlbl[r]))
                if rt not in rootid:
                    rootid[rt] = len(rootid)
                out.append(rootid[rt])
        return canon(tuple(out))

    masks = list(range(1, 1 << H))
    states = {}
    order = []
    todo = []
    for m in masks:
        s = initial(m)
        if s not in states:
            states[s] = len(states)
            order.append(s)
            todo.append(s)
    while todo:
        s = todo.pop()
        for m in masks:
            t = step(s, m)
            if t is not None and t not in states:
                states[t] = len(states)
                order.append(t)
                todo.append(t)
    n = len(states)
    delta = np.full((n, len(masks)), DEAD, dtype=np.int64)
    for s, si in states.items():
        for mi, m in enumerate(masks):
            t = step(s, m)
            if t is not None:
                delta[si, mi] = states[t]
    accept = np.array([max(s) == 0 for s in order], dtype=bool)
    return order, delta, accept, masks


# ---------- brute-force cross-check of the graded functional ----------

def brute_check(H, W, red=False):
    """f over words = connected subsets of the HxW box using every column
    (nonempty fills only, width exactly W): count by n, compare automaton."""
    from itertools import product
    NB = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    def connected(cells):
        s = set(cells)
        seen, st = {cells[0]}, [cells[0]]
        while st:
            x, y = st.pop()
            for dx, dy in NB:
                c = (x + dx, y + dy)
                if c in s and c not in seen:
                    seen.add(c)
                    st.append(c)
        return len(seen) == len(s)

    order, delta, accept, masks = build_automaton(H, red=red)
    minit = {m: i for i, m in enumerate(masks)}
    # automaton counts by n over words of length W
    from collections import defaultdict
    cnt_auto = defaultdict(int)

    def rec(w, si, n):
        if w == W:
            if accept[si]:
                cnt_auto[n] += 1
            return
        for mi, m in enumerate(masks):
            t = delta[si, mi]
            if t >= 0:
                rec(w + 1, t, n + bin(m).count('1'))
    # initial states
    for m in masks:
        # rebuild initial: word starts with fill m
        si = None
        # find initial state by running step from scratch: use a fresh automaton entry
        # initial(m) is order index of canon(initial); recompute via automaton build order
        pass
    # simpler: drive from a virtual start: state after first fill m
    ord_idx = {s: i for i, s in enumerate(order)}

    def initial_state(m):
        lbl, run, blk = [], -2, -1
        for r in range(H):
            if m >> r & 1:
                if run != r - 1:
                    blk += 1
                lbl.append(blk)
                run = r
            else:
                lbl.append(-1)
        return ord_idx[tuple(lbl)]

    for m in masks:
        rec(1, initial_state(m), bin(m).count('1'))
    # brute force
    cnt_brute = defaultdict(int)
    for bits in product([0, 1], repeat=H * W):
        cells = [(i // H, i % H) for i, b in enumerate(bits) if b]
        if not cells:
            continue
        cols = {x for x, _ in cells}
        if cols != set(range(W)):
            continue
        if connected(cells):
            cnt_brute[len(cells)] += 1
    return dict(cnt_auto) == dict(cnt_brute), dict(cnt_auto), dict(cnt_brute)


# ---------- GF(2^16) tables ----------

POLY = 0x1100B  # x^16 + x^12 + x^3 + x + 1, primitive

def build_gf():
    exp = np.zeros(131070, dtype=np.uint32)
    log = np.zeros(65536, dtype=np.uint32)
    x = 1
    for i in range(65535):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 0x10000:
            x ^= POLY
    exp[65535:131070] = exp[0:65535]
    return exp, log


EXP, LOG = build_gf()


def gf_scale(vec, c):
    """vec * c elementwise over GF(2^16); vec uint16 numpy, c scalar != 0."""
    out = np.zeros_like(vec)
    nz = vec != 0
    out[nz] = EXP[(LOG[vec[nz]] + LOG[c]) % 65535]
    return out


def gf_pow(c, e):
    if e == 0:
        return 1
    return int(EXP[(int(LOG[c]) * e) % 65535])


# ---------- observability closure ranks ----------

def obs_rank_gf2_x1(delta, accept):
    """Rank over GF(2) of span{accept o (delta words)} with all weights 1."""
    n, na = delta.shape
    # rows as ints
    basis = {}  # pivot -> int row

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

    frontier = [accept.copy()]
    reduce_add(vec_to_int(accept))
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=bool)
                ok = d >= 0
                h[ok] = g[d[ok]]
                if reduce_add(vec_to_int(h)):
                    nxt.append(h)
        frontier = nxt
    return len(basis)


def obs_rank_gf216(delta, accept, masksizes, t):
    """Rank over GF(2^16) of the graded observability space, weight t^|m|."""
    n, na = delta.shape
    tw = np.array([gf_pow(t, s) for s in masksizes], dtype=np.uint16)
    basis = []  # list of (pivot index, row uint16 array), rows normalized

    def reduce_add(row):
        row = row.copy()
        for piv, b in basis:
            if row[piv]:
                row ^= gf_scale(b, int(row[piv]))
        nz = np.nonzero(row)[0]
        if len(nz) == 0:
            return None
        piv = int(nz[0])
        inv = EXP[(65535 - int(LOG[row[piv]])) % 65535]
        row = gf_scale(row, int(inv))
        basis.append((piv, row))
        return row

    g0 = accept.astype(np.uint16)
    r = reduce_add(g0)
    frontier = [g0]
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=np.uint16)
                ok = d >= 0
                h[ok] = g[d[ok]]
                h = gf_scale(h, int(tw[mi]))
                if reduce_add(h) is not None:
                    nxt.append(h)
        frontier = nxt
    return len(basis)


AS1_MODP = {4: 6, 5: 17, 6: 35, 7: 88, 8: 204, 9: 501, 10: 1217}


def main():
    maxh = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    print("exact 'before' numbers at H=21:")
    print("  incumbent column states Motzkin(22)-1 =", motzkin(22) - 1)
    print("  B1 column-cut sum C(22,2k)Bell(k)     =", b1_colcut(21))
    print("  valid spin colorings (q=2), H=21      =", valid_colorings(21))
    print("  valid spin colorings (q=2), H=20      =", valid_colorings(20))
    print("  3^21 =", 3 ** 21, " 3^20 =", 3 ** 20)
    print("  spatial floor M(11), M(12) =", motzkin(11), motzkin(12))

    # brute-force cross-check of the automaton semantics
    for (h, w) in ((2, 3), (3, 3), (3, 4)):
        ok, a, b = brute_check(h, w)
        print(f"brute check H={h} W={w}: {'OK' if ok else 'MISMATCH ' + str((a, b))}")
        assert ok

    # RED control: dropping one diagonal from the merge stencil must make the
    # automaton MISCOUNT against brute force (the census alone can coincide)
    ok_red, a_red, b_red = brute_check(3, 3, red=True)
    if ok_red:
        print("RED CONTROL FAILED: corrupted stencil still matches brute force")
        return 1
    print("RED control OK: corrupted stencil miscounts vs brute force at H=3 W=3")

    print("\nH  states  Motzkin-1  rank_GF2(x=1)  rank_GF(2^16) t1  t2  A-S1 mod-p")
    for H in range(4, maxh + 1):
        t0 = time.time()
        order, delta, accept, masks = build_automaton(H)
        assert len(order) == motzkin(H + 1) - 1, (H, len(order))
        msizes = [bin(m).count('1') for m in masks]
        r2 = obs_rank_gf2_x1(delta, accept)
        rng = np.random.default_rng(20260812 + H)
        t1, t2 = [int(x) for x in rng.integers(2, 65535, 2)]
        rg1 = obs_rank_gf216(delta, accept, msizes, t1)
        rg2 = obs_rank_gf216(delta, accept, msizes, t2)
        print(f"{H}  {len(order)}  {motzkin(H+1)-1}  {r2}  {rg1}  {rg2}  "
              f"{AS1_MODP.get(H,'-')}   ({time.time()-t0:.1f}s)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
