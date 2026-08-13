#!/usr/bin/env python3
"""r3_l4_fixedh_exact: exact minimal recurrence order of I_H(<h>)(n) at
fixed H, by direct realization of the palindromic-column king TM.

Queue row L4-9: replace the extrapolated fixed-H order wall with exact
numbers per H in the band. Method mirrors the banked full-family GF
recovery (results/fixed_height_gfs.txt header: "mod-p transfer matrix +
Berlekamp-Massey"): build the height-H column TM restricted to vertically
palindromic masks (= the hmirror symmetric family, per symtm's hmirror
mode), enumerate reachable states exactly, generate the fixed-H series
mod two independent primes, and Berlekamp-Massey each to the minimal
LFSR order; orders must agree between primes.

Validation carried inside every run:
  - exact big-integer dp for n <= 32 compared per-cell against the banked
    symtm table (results/percell_raw/hmirror.byheight.n32.out summed over
    W) -- a third rule-class-internal realization agreeing with symtm;
  - --plain mode: same code with ALL nonempty masks must reproduce the
    Motzkin(H+1)-1 reachable-state closure of king-column-motzkin.md
    (second-source branch), cross-checking the state-counting convention.

Throwaway per the round-3 measurement boundary. Usage:
  r3_l4_fixedh_exact.py H            # palindromic: states, series, order
  r3_l4_fixedh_exact.py H --plain    # plain-mask state census only
"""
import collections, os, sys, time
import numpy as np
from scipy.sparse import csr_matrix

ROOT = "/Users/jasonp/src/polyominoes"
P1, P2 = 46337, 46349          # both prime (checked below); p^2 * 1e5 < 2^63
MOTZKIN = [1, 1, 2, 4, 9, 21, 51, 127, 323, 835, 2188, 5798, 15511, 41835,
           113634, 310572, 853467, 2356779, 6536382, 18199284, 50852019,
           142547559, 400763223, 1129760415]

def is_prime(n):
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True
assert is_prime(P1) and is_prime(P2)

def palindromic_masks(H):
    h = (H + 1) // 2
    out = []
    for top in range(1, 1 << h):
        m = 0
        for r in range(h):
            if top >> r & 1:
                m |= 1 << r
                m |= 1 << (H - 1 - r)
        out.append(m)
    return sorted(set(out))

def all_masks(H):
    return list(range(1, 1 << H))

def step(labels, t, mask, H):
    """Production-rule column step. labels: tuple len H (0=empty). Returns
    (labels', t', k) or None if a previous component is stranded."""
    L = max(labels)
    # exact stranding pre-check: every old component needs a new neighbour
    need = [0] * (L + 1)
    for r in range(H):
        l = labels[r]
        if l:
            nb = 1 << r
            if r > 0: nb |= 1 << (r - 1)
            if r < H - 1: nb |= 1 << (r + 1)
            need[l] |= nb
    for l in range(1, L + 1):
        if need[l] and not (need[l] & mask):
            return None
    # union-find over slots: 0..H-1 new rows, H..H+L-1 old labels
    parent = list(range(H + L))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    rows = [r for r in range(H) if mask >> r & 1]
    for r in rows:
        if r + 1 < H and mask >> (r + 1) & 1:
            union(r, r + 1)
        for rr in (r - 1, r, r + 1):
            if 0 <= rr < H and labels[rr]:
                union(r, H + labels[rr] - 1)
    newroots = set(find(r) for r in rows)
    for l in range(1, L + 1):
        if find(H + l - 1) not in newroots:
            return None   # united only among old comps: stranded
    canon = {}
    out = [0] * H
    for r in rows:
        root = find(r)
        if root not in canon:
            canon[root] = len(canon) + 1
        out[r] = canon[root]
    return tuple(out), t or (mask & 1), len(rows)

def seed_state(mask, H):
    return step((0,) * H, 0, mask, H)

def build(H, masks, tlimit, label):
    """BFS the reachable state space; returns states dict, edges, seeds."""
    t0 = time.monotonic()
    states = {}
    edges = []      # (src, dst, k)
    seeds = []      # (idx, k)
    todo = []
    def intern(s):
        if s not in states:
            states[s] = len(states)
            todo.append(s)
        return states[s]
    for m in masks:
        r = seed_state(m, H)
        if r:
            seeds.append((intern(r[:2]), r[2]))
    qi = 0
    while qi < len(todo):
        s = todo[qi]; qi += 1
        si = states[s]
        labels, t = s
        for m in masks:
            r = step(labels, t, m, H)
            if r:
                edges.append((si, intern(r[:2]), r[2]))
        if time.monotonic() - t0 > tlimit:
            print(f"{label}: ABORT after {time.monotonic()-t0:.0f}s: "
                  f"{len(states)} states interned, {qi} expanded, BFS incomplete")
            return None
    print(f"{label}: {len(states)} reachable states, {len(edges)} edges, "
          f"{len(seeds)} seeds, BFS {time.monotonic()-t0:.1f}s")
    return states, edges, seeds

def series_modp(states, edges, seeds, H, N, p=None):
    """p=None: exact int64 (safe for n<=32: totals < Fix(h)(32)=2.5e12)."""
    S = len(states)
    close = np.zeros(S, dtype=np.int64)
    for s, i in states.items():
        labels, t = s
        if t and max(labels) == 1 and len(set(l for l in labels if l)) == 1:
            close[i] = 1
    bykk = collections.defaultdict(lambda: ([], [], []))
    for src, dst, k in edges:
        d, r, c = bykk[k]
        d.append(1); r.append(dst); c.append(src)
    mats = {k: csr_matrix((np.array(d, dtype=np.int64),
                           (np.array(r), np.array(c))), shape=(S, S))
            for k, (d, r, c) in bykk.items()}
    maxk = max(list(mats) + [k for _, k in seeds])
    hist = [np.zeros(S, dtype=np.int64) for _ in range(maxk + 1)]  # hist[j] = v_{n-j}
    out = []
    for n in range(1, N + 1):
        v = np.zeros(S, dtype=np.int64)
        for k, M in mats.items():
            if k <= n:
                v += M.dot(hist[k - 1])
        for idx, k in seeds:
            if k == n:
                v[idx] += 1
        if p is not None:
            v %= p
        hist.insert(0, v)
        hist.pop()
        out.append(int(close.dot(v)) % (p if p is not None else 1 << 62))
    return out

def series_exact(states, edges, seeds, H, N):
    S = len(states)
    close = [0] * S
    for s, i in states.items():
        labels, t = s
        if t and set(l for l in labels if l) == {1} and max(labels) == 1:
            close[i] = 1
    maxk = max([k for _, _, k in edges] + [k for _, k in seeds])
    hist = [[0] * S for _ in range(maxk + 1)]
    out = []
    for n in range(1, N + 1):
        v = [0] * S
        for src, dst, k in edges:
            if k <= n:
                v[dst] += hist[k - 1][src]
        for idx, k in seeds:
            if k == n:
                v[idx] += 1
        hist.insert(0, v)
        hist.pop()
        out.append(sum(c * x for c, x in zip(close, v)))
    return out

def berlekamp_massey(seq, p):
    N = len(seq)
    s = np.array(seq, dtype=np.int64) % p
    C = np.zeros(N + 1, dtype=np.int64); C[0] = 1
    B = np.zeros(N + 1, dtype=np.int64); B[0] = 1
    L, m, b = 0, 1, 1
    for n in range(N):
        if L:
            d = (int(s[n]) + int(np.dot(C[1:L + 1], s[n - L:n][::-1]))) % p
        else:
            d = int(s[n]) % p
        if d == 0:
            m += 1
        else:
            coef = d * pow(b, p - 2, p) % p
            if 2 * L <= n:
                T = C.copy()
                C[m:] = (C[m:] - coef * B[:N + 1 - m]) % p
                L, B, b, m = n + 1 - L, T, d, 1
            else:
                C[m:] = (C[m:] - coef * B[:N + 1 - m]) % p
                m += 1
    return L

def banked_series(H):
    ih = collections.Counter()
    with open(os.path.join(ROOT, "results/percell_raw/hmirror.byheight.n32.out")) as f:
        for line in f:
            n, HH, W, c = map(int, line.split())
            if HH == H:
                ih[n] += c
    return [ih.get(n, 0) for n in range(1, 33)]

def main():
    H = int(sys.argv[1])
    plain = "--plain" in sys.argv
    if plain:
        res = build(H, all_masks(H), 240, f"plain H={H}")
        if res:
            states, _, _ = res
            noflag = len(set(s[0] for s in states))
            want = MOTZKIN[H + 1] - 1
            print(f"plain H={H}: labels-only states {noflag}, "
                  f"Motzkin({H+1})-1 = {want}: "
                  f"{'MATCH' if noflag == want else 'MISMATCH'}")
        return
    res = build(H, palindromic_masks(H), 600, f"hmirror H={H}")
    if res is None:
        return
    states, edges, seeds = res
    # validation: exact dp vs banked symtm table, n <= 32 (int64 exact:
    # totals bounded by Fix(h)(32) = 2546382907164 < 2^63)
    ex = series_modp(states, edges, seeds, H, 32)
    bank = banked_series(H)
    mism = sum(1 for a, b in zip(ex, bank) if a != b)
    print(f"hmirror H={H}: exact dp vs banked symtm, n=1..32: "
          f"{mism} mismatches" + ("" if mism == 0 else "  <-- FAILURE"))
    if mism:
        return
    # adaptive order hunt: ONE dp pass mod P1*P2 (linear over Z/pq; entries
    # < 2.15e9, csr row sums stay under 2^63), then BM per prime.
    S = len(states)
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 512
    while True:
        t0 = time.monotonic()
        seq = series_modp(states, edges, seeds, H, N, P1 * P2)
        r1 = berlekamp_massey([x % P1 for x in seq], P1)
        r2 = berlekamp_massey([x % P2 for x in seq], P2)
        dt = time.monotonic() - t0
        print(f"hmirror H={H}: N={N} -> BM orders p1:{r1} p2:{r2} ({dt:.0f}s)")
        if r1 == r2 and N >= 2 * r1 + 64:
            print(f"hmirror H={H}: MINIMAL ORDER {r1} "
                  f"(two primes agree, N={N} >= 2r+64; {S} states)")
            return
        if N > 16 * (S + 1):
            print(f"hmirror H={H}: NOT STABILISED at N={N} (S={S}) -- stop")
            return
        N *= 2

if __name__ == "__main__":
    main()
