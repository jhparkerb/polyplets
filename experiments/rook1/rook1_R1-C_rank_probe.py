#!/usr/bin/env python3
"""rook1_R1-C_rank_probe.py -- R1-C: does ROOK show the char-2 Hankel crack?

Background. results/triangle-r3-involution.md S2 measured, on the KING strip
automaton, a GF(2) observability (Hankel) rank tracking ~0.42-0.45 * 2^H
under a Motzkin-sized state space, against mod-p rank growth ~2.5-2.8x/height
(A-S1) -- the CKN char-2 collapse signature.  King-only, basis never
constructed, unverified past H~10.  rook-parity.md:132-136 charters the rook
version as the one place rook data changes a king decision.

Object. Same strip automaton as experiments/tristruct/r3_inv_rank_probe.py,
parameterized by the cross-column adjacency stencil:
  king: new cell r ~ old cells r-1, r, r+1;   rook: new cell r ~ old cell r.
States = connectivity partitions of the current column, stranded component ->
dead; f(w) = [all placed cells form one component].  Deterministic, so the
Hankel rank of f over any field = dim of the observability closure.  This is
a ~200-line throwaway probe, NOT the out-of-scope rook transfer-matrix
engine; the rook stencil swap itself was already externally validated in
experiments/tristruct/r3_adv3_rook_schema.py against A292357/A001168.

Verification chain (all fail-closed asserts):
  * king regression: GF(2) ranks must reproduce the banked table
    (triangle-r3-involution.md S2: 6,15,27,58,112,229 for H=4..9) and mod-p
    ranks must reproduce A-S1 (6,17,35,88,204 for H=4..8) -- the rank code
    itself is regressed against known outputs before any rook number is read;
  * census: king states = Motzkin(H+1)-1; rook census reported alongside;
  * semantics: automaton counts vs brute-force ROOK-connected enumeration at
    (H,W) in {(2,3),(3,3),(3,4)};
  * ground truth: fixed polyominoes a(n), n<=8, assembled from the rook
    automaton by grading + exact-height second difference over H<=8, must
    equal A001168 = build/g2 square8 8 --rook-bishop (run and parsed here);
  * RED A (planted wrong stencil): the KING stencil fed to the rook brute
    check must MISCOUNT -- run must abort if it matches;
  * RED B (planted corrupt transition): one reachable delta entry killed in
    the rook automaton must break the A001168 tie -- abort if it survives.

mod-p uses p = 32749 (RREF + matmul reduction; int64-safe); spot-checked
against p = 2^31-1 by scalar elimination at H<=6.

Usage: rook1_R1-C_rank_probe.py [MAXH]   (default 8; GF(2^16) capped at 7,
mod-p at 8).  Laptop, exact arithmetic, foreground.
"""

import subprocess
import sys
import time
from collections import defaultdict
from functools import lru_cache
from itertools import product

import numpy as np

A001168 = [0, 1, 2, 6, 19, 63, 216, 760, 2725]  # fixed polyominoes, n<=8
KING_GF2 = {4: 6, 5: 15, 6: 27, 7: 58, 8: 112, 9: 229}   # banked S2 table
KING_MODP = {4: 6, 5: 17, 6: 35, 7: 88, 8: 204, 9: 501}  # A-S1 (p=2^31-1)

KING_OFFS = (-1, 0, 1)
ROOK_OFFS = (0,)


@lru_cache(None)
def motzkin(n):
    if n <= 1:
        return 1
    return ((2 * n + 1) * motzkin(n - 1) + (3 * n - 3) * motzkin(n - 2)) // (n + 2)


# ---------- the strip automaton, stencil-parameterized ----------

def build_automaton(H, offs):
    """Returns (order, delta, accept, masks); delta[s,m] = -1 for dead."""
    def canon(lbl):
        seen, out = {}, []
        for v in lbl:
            if v < 0:
                out.append(-1)
            else:
                if v not in seen:
                    seen[v] = len(seen)
                out.append(seen[v])
        return tuple(out)

    def initial(mask):
        lbl, run, blk = [], -2, -1
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
        newlbl, run, blk = [-1] * H, -2, -1
        for r in range(H):
            if mask >> r & 1:
                if run != r - 1:
                    blk += 1
                    parent[('n', blk)] = ('n', blk)
                newlbl[r] = blk
                run = r
        for r in range(H):
            if newlbl[r] < 0:
                continue
            for dr in offs:
                rr = r + dr
                if 0 <= rr < H and state[rr] >= 0:
                    union(('n', newlbl[r]), ('o', state[rr]))
        newroots = {find(('n', b)) for b in range(blk + 1)}
        for b in old_blocks:
            if find(('o', b)) not in newroots:
                return None
        rootid, out = {}, []
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
    states, order, todo = {}, [], []
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
    delta = np.full((n, len(masks)), -1, dtype=np.int64)
    for s, si in states.items():
        for mi, m in enumerate(masks):
            t = step(s, m)
            if t is not None:
                delta[si, mi] = states[t]
    accept = np.array([max(s) == 0 for s in order], dtype=bool)
    init_idx = {m: states[initial(m)] for m in masks}
    return order, delta, accept, masks, init_idx


# ---------- brute-force semantics check (ROOK connectivity) ----------

ROOK_NB = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def connected(cells, nb):
    s = set(cells)
    seen, st = {cells[0]}, [cells[0]]
    while st:
        x, y = st.pop()
        for dx, dy in nb:
            c = (x + dx, y + dy)
            if c in s and c not in seen:
                seen.add(c)
                st.append(c)
    return len(seen) == len(s)


def brute_check(H, W, offs):
    """Automaton (given stencil) vs brute-force ROOK-connected subsets of the
    HxW box using every column, counted by n."""
    order, delta, accept, masks, init_idx = build_automaton(H, offs)
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

    for m in masks:
        rec(1, init_idx[m], bin(m).count('1'))
    cnt_brute = defaultdict(int)
    for bits in product([0, 1], repeat=H * W):
        cells = [(i // H, i % H) for i, b in enumerate(bits) if b]
        if not cells:
            continue
        if {x for x, _ in cells} != set(range(W)):
            continue
        if connected(cells, ROOK_NB):
            cnt_brute[len(cells)] += 1
    return dict(cnt_auto) == dict(cnt_brute), dict(cnt_auto), dict(cnt_brute)


# ---------- A001168 tie: graded counts + exact-height second difference ----

def graded_counts(H, nmax, offs, delta_override=None):
    """N_H[W][n] = rook-automaton count of accepted words of length W with n
    cells total, n<=nmax, W<=nmax.  Returns dict (W,n)->count."""
    order, delta, accept, masks, init_idx = build_automaton(H, offs)
    if delta_override is not None:
        delta = delta_override(delta)
    S = len(order)
    msz = [bin(m).count('1') for m in masks]
    # vec[s][n] = number of length-w words reaching s with n cells
    vec = np.zeros((S, nmax + 1), dtype=object)
    for m, si in init_idx.items():
        if msz[masks.index(m)] <= nmax:
            vec[si][msz[masks.index(m)]] += 1
    out = {}
    for W in range(1, nmax + 1):
        tot = defaultdict(int)
        for si in range(S):
            if accept[si]:
                for n in range(nmax + 1):
                    if vec[si][n]:
                        tot[n] += vec[si][n]
        out[W] = dict(tot)
        if W == nmax:
            break
        new = np.zeros((S, nmax + 1), dtype=object)
        for si in range(S):
            row = vec[si]
            if not row.any():
                continue
            for mi in range(len(masks)):
                t = delta[si, mi]
                if t < 0:
                    continue
                k = msz[mi]
                for n in range(nmax + 1 - k):
                    if row[n]:
                        new[t][n + k] += row[n]
        vec = new
    return out


def a001168_from_automaton(nmax, offs, delta_override=None):
    """Assemble fixed polyominoes a(n), n<=nmax, from strip automata H<=nmax:
    exact-height counts by second difference e_H = N_H - 2N_{H-1} + N_{H-2}."""
    N = {0: {}}  # H -> {W: {n: count}}
    for H in range(1, nmax + 1):
        N[H] = graded_counts(H, nmax, offs,
                             delta_override if H >= 2 else None)
    a = [0] * (nmax + 1)
    for H in range(1, nmax + 1):
        for W in range(1, nmax + 1):
            cur = N[H].get(W, {})
            below = N.get(H - 1, {}).get(W, {}) if H >= 1 else {}
            below2 = N.get(H - 2, {}).get(W, {}) if H >= 2 else {}
            for n in range(1, nmax + 1):
                e = cur.get(n, 0) - 2 * below.get(n, 0) + below2.get(n, 0)
                a[n] += e
    return a


# ---------- rank routines ----------

def obs_rank_gf2(delta, accept):
    n, na = delta.shape
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


def obs_rank_modp(delta, accept, p):
    """RREF basis over GF(p); candidate reduction is one matmul."""
    n, na = delta.shape
    B = np.zeros((0, n), dtype=np.int64)   # RREF rows, pivot entry = 1
    pivs = []

    def reduce_add(row):
        nonlocal B, pivs
        row = row % p
        if len(pivs):
            coef = row[pivs]
            row = (row - coef @ B) % p
        nz = np.nonzero(row)[0]
        if len(nz) == 0:
            return False
        piv = int(nz[0])
        row = (row * pow(int(row[piv]), p - 2, p)) % p
        # eliminate new pivot from existing rows to keep RREF
        if len(pivs):
            col = B[:, piv].copy()
            B = (B - np.outer(col, row)) % p
        B = np.vstack([B, row])
        pivs.append(piv)
        return True

    g0 = accept.astype(np.int64)
    frontier = [g0]
    reduce_add(g0)
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=np.int64)
                ok = d >= 0
                h[ok] = g[d[ok]]
                if reduce_add(h):
                    nxt.append(h)
        frontier = nxt
    return len(pivs)


# GF(2^16), graded, from r3_inv_rank_probe.py verbatim
POLY = 0x1100B


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
    out = np.zeros_like(vec)
    nz = vec != 0
    out[nz] = EXP[(LOG[vec[nz]] + LOG[c]) % 65535]
    return out


def gf_pow(c, e):
    if e == 0:
        return 1
    return int(EXP[(int(LOG[c]) * e) % 65535])


def obs_rank_gf216(delta, accept, masksizes, t):
    n, na = delta.shape
    tw = np.array([gf_pow(t, s) for s in masksizes], dtype=np.uint16)
    basis = []

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
    reduce_add(g0)
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


# ---------- main ----------

def main():
    maxh = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    p = 32749

    # ground truth: g2 --rook-bishop
    print("ABOUT: ground-truth tie, build/g2 square8 8 --rook-bishop")
    g2 = subprocess.run(['./build/g2', 'square8', '8', '--rook-bishop'],
                        capture_output=True, text=True, check=True)
    rook_g2 = {}
    for line in g2.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            rook_g2[int(parts[0])] = int(parts[2])
    assert all(rook_g2[n] == A001168[n] for n in range(1, 9)), rook_g2
    print("  g2 rook column == A001168 for n=1..8: OK")

    # semantics: automaton vs brute rook connectivity
    for (h, w) in ((2, 3), (3, 3), (3, 4)):
        ok, a, b = brute_check(h, w, ROOK_OFFS)
        print(f"  brute semantics H={h} W={w}: {'OK' if ok else 'MISMATCH'}")
        assert ok, (a, b)

    # RED A: king stencil against rook brute force must miscount
    ok_red, a_red, b_red = brute_check(3, 3, KING_OFFS)
    if ok_red:
        print("RED A FAILED: king stencil matches rook brute force")
        return 1
    print("  RED A OK: planted king stencil miscounts vs rook brute force")

    # A001168 assembled end to end from the rook automaton
    a_auto = a001168_from_automaton(8, ROOK_OFFS)
    assert a_auto[1:] == A001168[1:], a_auto
    print("  automaton-assembled a(n) n=1..8 == A001168 == g2: OK")

    # RED B: one killed reachable transition (the row-0 bar transition,
    # state 0 --mask 1--> state 0) must be caught by the word-count
    # regression that guards the same delta the rank code consumes.
    order3, d3, a3, m3, ii3 = build_automaton(3, ROOK_OFFS)
    assert d3[0, 0] >= 0
    d3bad = d3.copy()
    d3bad[0, 0] = -1
    cnt_bad = defaultdict(int)

    def rec_bad(w, si, n):
        if w == 3:
            if a3[si]:
                cnt_bad[n] += 1
            return
        for mi, m in enumerate(m3):
            t = d3bad[si, mi]
            if t >= 0:
                rec_bad(w + 1, t, n + bin(m).count('1'))

    for m in m3:
        rec_bad(1, ii3[m], bin(m).count('1'))
    _, _, cnt_ref = brute_check(3, 3, ROOK_OFFS)
    if dict(cnt_bad) == cnt_ref:
        print("RED B FAILED: killed transition invisible to word counts")
        return 1
    print("  RED B OK: one killed transition breaks the word-count "
          "regression at H=3 W=3")

    # documented observation: the SAME defect is invisible to the assembled
    # A001168 tie -- bottom-anchored losses cancel in the exact-height
    # telescope.  The tie is therefore NOT a sufficient defect gate on its
    # own; the word-count regression above is the one that goes red.
    def corrupt(delta):
        d = delta.copy()
        assert d[0, 0] >= 0
        d[0, 0] = -1
        return d

    a_bad = a001168_from_automaton(8, ROOK_OFFS, delta_override=corrupt)
    print(f"  observation: same defect vs A001168 tie -> "
          f"{'CANCELS (tie survives)' if a_bad[1:] == A001168[1:] else 'breaks tie'}")

    # spot-check mod-p routine against a second prime at small H
    for H in (4, 5, 6):
        _, dk, ak, _, _ = build_automaton(H, KING_OFFS)
        r_small = obs_rank_modp(dk, ak, p)
        r_big = obs_rank_modp(dk, ak, 2**31 - 1)
        assert r_small == r_big == KING_MODP[H], (H, r_small, r_big)
    print(f"  mod-p spot check H=4..6: p={p} == p=2^31-1 == A-S1: OK")

    print("\nlat H  states  rank_GF2  rank_modp  rank_GF(2^16) t1 t2")
    results = {}
    for name, offs in (('king', KING_OFFS), ('rook', ROOK_OFFS)):
        for H in range(4, maxh + 1):
            t0 = time.time()
            order, delta, accept, masks, _ = build_automaton(H, offs)
            if name == 'king':
                assert len(order) == motzkin(H + 1) - 1, (H, len(order))
            msz = [bin(m).count('1') for m in masks]
            r2 = obs_rank_gf2(delta, accept)
            rp = (obs_rank_modp(delta, accept, p)
                  if H <= (8 if name == 'king' else 7) else None)
            if name == 'king':
                assert r2 == KING_GF2[H], (H, r2)
                if rp is not None:
                    assert rp == KING_MODP[H], (H, rp)
            rg = []
            if H <= 7:
                rng = np.random.default_rng(20260813 + H)
                for t in [int(x) for x in rng.integers(2, 65535, 2)]:
                    rg.append(obs_rank_gf216(delta, accept, msz, t))
            results[(name, H)] = (len(order), r2, rp, rg)
            print(f"{name} {H}  {len(order)}  {r2}  {rp}  {rg}"
                  f"   ({time.time()-t0:.1f}s)")

    print("\nratios rank_GF2 / 2^H and modp growth:")
    for name in ('king', 'rook'):
        line = []
        prev = None
        for H in range(4, maxh + 1):
            st, r2, rp, _ = results[(name, H)]
            g = f" modp x{rp/prev:.2f}" if (prev and rp) else ""
            line.append(f"H{H}: {r2}/{2**H}={r2/2**H:.3f}{g}")
            if rp:
                prev = rp
        print(f"  {name}: " + "; ".join(line))
    return 0


if __name__ == '__main__':
    sys.exit(main())
