#!/usr/bin/env python3
"""Independent exact (big-integer) fixed-height king transfer matrix.

Counts B_H(n) = fixed polyplets of n cells with bounding-box height exactly H, by
sweeping columns left to right over an H-row strip. A boundary state is
(last-column occupancy mask, partition of its filled rows into the partial
animal's connected components, top-touched flag, bottom-touched flag) -- the same
Markov boundary the C++ engine uses, reimplemented from scratch as a cross-check.
No pruning and no modular reduction, so big ints give unbounded exact terms.

Used to (a) cross-check the C++ engine, (b) recover/validate the fixed-height
generating functions to higher H than the u64 engine reaches, and (c) test the
conjecture deg Q_H = 2^H - 1.  Usage: python3 gf/fixed_height.py [Hmax] [N]
"""
import sys, subprocess, os, functools
from fractions import Fraction as Fr
from recover import berlekamp_massey as bm  # single-source the exact BM core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMA = os.path.join(ROOT, "build", "tma")

sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)

# ---- union-find over small integer node ids ----
def find(p, x):
    while p[x] != x:
        p[x] = p[p[x]]; x = p[x]
    return x
def union(p, a, b):
    ra, rb = find(p, a), find(p, b)
    if ra != rb: p[ra] = rb

def col_components(rows):
    """labels for a single column's filled rows (vertical adjacency only)."""
    idx = {r: i for i, r in enumerate(rows)}
    p = list(range(len(rows)))
    for i, r in enumerate(rows):
        if r + 1 in idx: union(p, i, idx[r + 1])
    return canon([find(p, i) for i in range(len(rows))])

def canon(roots):
    """relabel a list of roots to 0,1,2,... in first-seen order."""
    m = {}; out = []
    for r in roots:
        if r not in m: m[r] = len(m)
        out.append(m[r])
    return tuple(out)

@functools.lru_cache(maxsize=None)
def step(m1, lab1, m2):
    """Transition from previous column (mask m1, component labels lab1) to next
    column mask m2. Returns the new component-label tuple for m2's rows, or None
    if a previous component is stranded (can never reconnect). Purely combinatorial
    on the bits, so memoised -- the same transition recurs at every column."""
    rows1 = [r for r in range(m1.bit_length()) if m1 >> r & 1]
    rows2 = [r for r in range(m2.bit_length()) if m2 >> r & 1]
    n1, n2 = len(rows1), len(rows2)
    # nodes 0..n1-1 = prev rows, n1..n1+n2-1 = new rows
    p = list(range(n1 + n2))
    pi = {r: i for i, r in enumerate(rows1)}
    ni = {r: n1 + j for j, r in enumerate(rows2)}
    for i in range(n1):                      # prev rows sharing a label
        for j in range(i + 1, n1):
            if lab1[i] == lab1[j]: union(p, i, j)
    for j, r in enumerate(rows2):            # new column vertical adjacency
        if r + 1 in ni: union(p, ni[r], ni[r + 1])
    for r in rows2:                          # king cross-column adjacency
        for dr in (-1, 0, 1):
            if r + dr in pi: union(p, ni[r], pi[r + dr])
    new_roots = {find(p, ni[r]) for r in rows2}
    for i in range(n1):                      # every prev component must reconnect
        if find(p, i) not in new_roots: return None
    return canon([find(p, ni[r]) for r in rows2])

def fixed_height(H, N):
    """B_H(0..N), exact."""
    full = (1 << H) - 1
    top, bot = 1, 1 << (H - 1)
    # start: first column = column 0, every nonempty mask
    db = {}
    for m in range(1, full + 1):
        rows = [r for r in range(H) if m >> r & 1]
        sig = (m, col_components(rows), bool(m & top), bool(m & bot))
        c = db.setdefault(sig, {})
        c[bin(m).count("1")] = c.get(bin(m).count("1"), 0) + 1
    res = [0] * (N + 1)
    while db:
        nxt = {}
        for (m1, lab1, tT, tB), counts in db.items():
            if len(set(lab1)) == 1 and tT and tB:        # valid terminal: harvest
                for sz, v in counts.items():
                    if sz <= N: res[sz] += v
            for m2 in range(1, full + 1):
                lab2 = step(m1, lab1, m2)
                if lab2 is None: continue
                add = bin(m2).count("1")
                sig = (m2, lab2, tT or bool(m2 & top), tB or bool(m2 & bot))
                c = nxt.setdefault(sig, {})
                for sz, v in counts.items():
                    if sz + add <= N: c[sz + add] = c.get(sz + add, 0) + v
        # drop sigs that received no in-budget counts, else db never empties
        db = {sig: c for sig, c in nxt.items() if c}
    return res

# ---- recurrence recovery (Berlekamp-Massey over Q) ----
def c_tma(H):
    """exact B_H(0..19) from the C++ engine, for cross-checking."""
    out = subprocess.run([TMA, "square8", "19", "--only-height", str(H)],
                         capture_output=True, text=True).stdout
    d = {0: 0}
    for line in out.split("\n"):
        q = line.split()
        if len(q) == 2 and q[0].isdigit(): d[int(q[0])] = int(q[1])
    return [d[n] for n in range(20)]

def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    # Checkpoint the per-height exact sequence: fixed_height(H,N) is an exponential
    # (2^H boundary states) DP -- the cost. A resume reloads banked heights and
    # recomputes only the rest, then re-derives the (cheap) recurrence + cross-check.
    ckpt = obs.Checkpoint(os.path.join(ROOT, "runs", "ckpt", f"fixed-height-H1_{Hmax}"),
                          {"script": "fixed_height", "Hmax": Hmax})
    with obs.Reporter(f"fixed-height-H1_{Hmax}", script=__file__, total=Hmax) as rep:
        for H in range(1, Hmax + 1):
            order_guess = 2 ** H - 1
            N = max(20, 2 * order_guess + 6)
            s = ckpt.get_or_none(f"H{H}-N{N}")
            if s is None:
                s = fixed_height(H, N)
                ckpt.save(f"H{H}-N{N}", s)
            xcheck = (s[:20] == c_tma(H)) if os.path.exists(TMA) else None
            C, L = bm(s)
            def rec(k): return -sum(C[i] * Fr(s[k - i]) for i in range(1, len(C)))
            validated = all(rec(k) == s[k] for k in range(L, len(s)))
            order = max((i for i, c in enumerate(C) if c != 0), default=0)
            print(f"H={H}: order {order}  (2^{H}-1={order_guess}: {order==order_guess})"
                  f"  validated:{validated}  xcheck-vs-C++:{xcheck}  [{len(s)} terms]"
                  f"  B_{H}(19)={s[19]}", flush=True)
            # exponential per-height work (2^H boundary states) -- heartbeat each
            # completed height with the conjecture check deg Q_H == 2^H-1.
            rep.beat(done=H, force=True, H=H, order=order,
                     order_ok=(order == order_guess), validated=validated,
                     xcheck=xcheck)
        rep.result = "ok"
    ckpt.clear()

if __name__ == "__main__":
    main()
