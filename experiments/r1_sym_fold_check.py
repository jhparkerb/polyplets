#!/usr/bin/env python3
"""R1 (symmetry fold) validation, column-sweep model of build/tma.

Sweeps columns left-to-right for fixed-height-EXACTLY-H king animals (polyplets),
maintaining the live map  state -> Counter(size -> #partials)  exactly as build/tma's
FlatDB does. At every column it checks the premise of R1:

    count_c(Sig) == count_c(R*Sig)   for the vertical (top<->bottom) reflection R,

and measures the folding factor (#live states / #orbits) at the peak column -- the
memory reduction a symmetry-folded FlatDB would get. Also emits B_H(n) so the DP can
be cross-checked (sum_H B_H(n) = a(n)).

Usage: r1_sym_fold_check.py H N
"""
import sys
from collections import Counter, defaultdict

H = int(sys.argv[1]) if len(sys.argv) > 1 else 6
N = int(sys.argv[2]) if len(sys.argv) > 2 else 14
FULL = (1 << H) - 1
TOP, BOT = 1, 1 << (H - 1)


def rows_of(mask):
    return [r for r in range(H) if mask >> r & 1]


def uf_find(p, x):
    while p[x] != x:
        p[x] = p[p[x]]; x = p[x]
    return x


def canon(seq):
    """first-seen 0,1,2,... relabel of a sequence of component roots -> tuple."""
    m = {}; out = []
    for c in seq:
        if c not in m:
            m[c] = len(m)
        out.append(m[c])
    return tuple(out)


def col_labels(mask):
    r = rows_of(mask); k = len(r)
    p = list(range(k))
    for i in range(k):
        for j in range(i + 1, k):
            if r[j] - r[i] <= 1:                       # king vertical adjacency
                a, b = uf_find(p, i), uf_find(p, j)
                if a != b: p[a] = b
    return canon(uf_find(p, i) for i in range(k))


def step(mask1, lab1, mask2):
    """prev (mask1,lab1) extended by new column mask2; returns new label tuple or
    None if a prev component is stranded (can never reconnect)."""
    r1, r2 = rows_of(mask1), rows_of(mask2)
    n1, n2 = len(r1), len(r2)
    p = list(range(n1 + n2))

    def u(a, b):
        ra, rb = uf_find(p, a), uf_find(p, b)
        if ra != rb: p[ra] = rb
    for i in range(n1):                                # prev rows sharing a label
        for j in range(i + 1, n1):
            if lab1[i] == lab1[j]: u(i, j)
    for a in range(n2):                                # new column vertical adjacency
        for b in range(a + 1, n2):
            if r2[b] - r2[a] <= 1: u(n1 + a, n1 + b)
    for j in range(n2):                                # cross-column king adjacency
        for i in range(n1):
            if abs(r1[i] - r2[j]) <= 1: u(n1 + j, i)
    newroot = set(uf_find(p, n1 + j) for j in range(n2))
    for i in range(n1):
        if uf_find(p, i) not in newroot:
            return None                                # stranded prev component
    return canon(uf_find(p, n1 + j) for j in range(n2))


def reflect(state):
    """vertical (row r -> H-1-r) reflection of a boundary state."""
    mask, lab, tT, tB = state
    r = rows_of(mask)                                  # ascending; lab[i] is comp of r[i]
    refl = sorted((H - 1 - r[i], lab[i]) for i in range(len(r)))
    new_mask = 0
    for nr, _ in refl:
        new_mask |= 1 << nr
    return (new_mask, canon(c for _, c in refl), tB, tT)   # flags swap top<->bot


def terminal(state):
    mask, lab, tT, tB = state
    return tT and tB and (len(lab) == 0 or max(lab) == 0)  # both touched, one component


def reflect_mask(m):
    r = 0
    for i in range(H):
        if m >> i & 1:
            r |= 1 << (H - 1 - i)
    return r


def canon_state(st):
    rs = reflect(st)
    return st if st <= rs else rs


def folded_sweep():
    """R1 folded DP, ORBIT-SUM scheme: cur_f[cs] = sum over cs's reflection-orbit of
    the unfolded count. Seeding and transitions accumulate into canon(state) (so the
    two orbit members merge), harvest is plain weight-1. No palindrome special case;
    still ~2x memory (canonical states only) and ~2x compute (canonical sources only).
    Must reproduce B_H exactly."""
    live = defaultdict(Counter)
    for m in range(1, FULL + 1):
        st = (m, col_labels(m), bool(m & TOP), bool(m & BOT))
        live[canon_state(st)][bin(m).count("1")] += 1     # accumulate into canon -> orbit-sum
    BH = Counter()
    while live:
        for st, cnt in live.items():
            if terminal(st):
                BH += cnt                                 # weight 1 (cur_f is an orbit-sum)
        nxt = defaultdict(Counter)
        for st, cnt in live.items():
            mask1, lab1, tT, tB = st
            for m2 in range(1, FULL + 1):
                lab2 = step(mask1, lab1, m2)
                if lab2 is None:
                    continue
                add = bin(m2).count("1")
                tgt = (m2, lab2, tT or bool(m2 & TOP), tB or bool(m2 & BOT))
                bucket = nxt[canon_state(tgt)]
                for sz, c in cnt.items():
                    if sz + add <= N:
                        bucket[sz + add] += c
        live = {st: c for st, c in nxt.items() if c}
    return BH


def sweep():
    # live: state -> Counter(size -> count)
    live = defaultdict(Counter)
    for m in range(1, FULL + 1):
        st = (m, col_labels(m), bool(m & TOP), bool(m & BOT))
        live[st][bin(m).count("1")] += 1
    BH = Counter()
    peak_states = peak_orbits = 0
    sym_ok = True
    col = 0
    while live:
        # R1 premise: count(Sig) == count(R*Sig), per size, at this column
        for st, cnt in live.items():
            rcnt = live.get(reflect(st), Counter())
            if cnt != rcnt:
                sym_ok = False
        # orbit reduction at this column
        orbits = set()
        for st in live:
            rs = reflect(st)
            orbits.add(st if st <= rs else rs)
        if len(live) > peak_states:
            peak_states, peak_orbits = len(live), len(orbits)
        # terminal animals ending at this column
        for st, cnt in live.items():
            if terminal(st):
                BH += cnt
        # extend every state by one column
        nxt = defaultdict(Counter)
        for st, cnt in live.items():
            mask1, lab1, tT, tB = st
            for m2 in range(1, FULL + 1):
                lab2 = step(mask1, lab1, m2)
                if lab2 is None:
                    continue
                add = bin(m2).count("1")
                ns = (m2, lab2, tT or bool(m2 & TOP), tB or bool(m2 & BOT))
                tgt = nxt[ns]
                for sz, c in cnt.items():
                    if sz + add <= N:
                        tgt[sz + add] += c
        live = {st: c for st, c in nxt.items() if c}
        col += 1
    return BH, sym_ok, peak_states, peak_orbits


def debug_lockstep():
    """Run unfolded U and folded F in lockstep; report the first column where the
    folded store's canonical count diverges from the unfolded count cur[cs]."""
    U = defaultdict(Counter); F = defaultdict(Counter)
    for m in range(1, FULL + 1):
        st = (m, col_labels(m), bool(m & TOP), bool(m & BOT)); sz = bin(m).count("1")
        U[st][sz] += 1
        if canon_state(st) == st: F[st][sz] += 1
    col = 0
    while U or F:
        keys = set(canon_state(s) for s in U) | set(F)
        for cs in keys:
            u = U.get(cs, Counter()); f = F.get(cs, Counter())
            if u != f:
                print(f"col {col}: MISMATCH cs={cs}")
                print(f"   unfolded cur[cs]   = {dict(u)}")
                print(f"   folded   cur_f[cs] = {dict(f)}")
                print(f"   pal={cs==reflect(cs)}  R*cs={reflect(cs)}  U[R*cs]={dict(U.get(reflect(cs),Counter()))}")
                return
        def adv(live, folded):
            nx = defaultdict(Counter)
            for st, cnt in live.items():
                m1, l1, tT, tB = st; ip = folded and (st == reflect(st))
                for m2 in range(1, FULL + 1):
                    if ip and m2 > reflect_mask(m2): continue
                    l2 = step(m1, l1, m2)
                    if l2 is None: continue
                    add = bin(m2).count("1")
                    tg = (m2, l2, tT or bool(m2 & TOP), tB or bool(m2 & BOT))
                    key = canon_state(tg) if folded else tg
                    for sz, c in cnt.items():
                        if sz + add <= N: nx[key][sz + add] += c
            return {s: c for s, c in nx.items() if c}
        U = adv(U, False); F = adv(F, True); col += 1
    print("no mismatch: cur_f == cur throughout (bug is in harvest weighting)")


if len(sys.argv) > 3 and sys.argv[3] == "debug":
    debug_lockstep(); sys.exit(0)

BH, sym_ok, ps, po = sweep()
BHf = folded_sweep()
unf = [BH.get(n, 0) for n in range(1, N + 1)]
fld = [BHf.get(n, 0) for n in range(1, N + 1)]
print(f"H={H} N={N}")
print(f"  B_H(n) unfolded: {unf}")
print(f"  B_H(n) FOLDED:   {fld}")
print(f"  folded DP reproduces unfolded B_H: {'YES' if unf == fld else 'NO -- BUG'}")
print(f"  R1 symmetry count(Sig)==count(R*Sig) at every column: {'HOLDS' if sym_ok else 'FAILS'}")
print(f"  peak live states = {ps},  orbits (folded) = {po},  fold factor = {ps / po:.3f}x")
