#!/usr/bin/env python3
"""Independent strip transfer-matrix engine for the polyplet triangle T(n,H).

A SECOND, kink-independent computation path (the lever from
results/diagonal-formula.md). It sweeps a height-H strip column by column
with a king-connectivity partition state, counting king-connected cell sets by
area with horizontal translation fixed (leftmost occupied column = 0). That
yields the strip cumulative

    C_H(n) = sum_{h<=H} (H-h+1) * T(n,h)        (vertical placements counted)

and the triangle is recovered by the exact second difference in H:

    T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n)   (with C_0 = C_{-1} = 0).

Shares NO enumeration with the kink NW-carry kernel that produced the banked
triangle, so agreement is a genuine cross-check. Correctness is anchored at
small n by an independent brute-force enumerator (brute_T), and the large-n
values are compared against results/ns_a35 / ns_a36.

Usage: strip_engine.py [Hmax=10] [Nmax=36]
"""
import os, sys, time
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Independent brute force (translation classes of king-connected n-cell sets),
# binned by bounding-box height. Ground truth for small n; no strip, no TM.
# ---------------------------------------------------------------------------
def brute_T(nmax):
    def canonform(cells):
        mnr = min(r for r, c in cells)
        mnc = min(c for r, c in cells)
        return frozenset((r - mnr, c - mnc) for r, c in cells)

    T = defaultdict(int)
    cur = {frozenset({(0, 0)})}
    for n in range(1, nmax + 1):
        for s in cur:
            rs = [r for r, _ in s]
            H = max(rs) - min(rs) + 1
            T[(n, H)] += 1
        if n == nmax:
            break
        nxt = set()
        for s in cur:
            for (r, c) in s:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        cell = (r + dr, c + dc)
                        if cell in s:
                            continue
                        ns = set(s)
                        ns.add(cell)
                        nxt.add(canonform(ns))
        cur = nxt
    return T


# ---------------------------------------------------------------------------
# Strip transfer matrix -> C_H(n).
# ---------------------------------------------------------------------------
def canon(labels):
    """Canonicalize component labels: first-seen order from row 0; 0 = empty."""
    remap = {}
    nxt = 1
    out = []
    for v in labels:
        if v == 0:
            out.append(0)
        else:
            r = remap.get(v)
            if r is None:
                r = nxt
                remap[v] = r
                nxt += 1
            out.append(r)
    return tuple(out)


def strip_C(H, N):
    """C[0..N] with C[n] = # king-connected n-cell sets in the H-row strip,
    leftmost occupied column fixed at 0, vertical placement free."""
    memo = {}  # (state, S) -> ('ext', newstate) | None(prune)

    def compute_ext(state, S):
        occ = state
        newrows = [(S >> r) & 1 for r in range(H)]
        newcells = [r for r in range(H) if newrows[r]]
        prev_comps = set(v for v in occ if v)

        parent = {}

        def find(x):
            parent.setdefault(x, x)
            root = x
            while parent[root] != root:
                root = parent[root]
            while parent[x] != root:
                parent[x], x = root, parent[x]
            return root

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for r in newcells:
            find(('n', r))
            if r + 1 < H and newrows[r + 1]:
                union(('n', r), ('n', r + 1))
        touched = set()
        for r in newcells:
            for dr in (-1, 0, 1):
                rr = r + dr
                if 0 <= rr < H and occ[rr]:
                    g = occ[rr]
                    touched.add(g)
                    union(('n', r), ('p', g))
        if len(touched) < len(prev_comps):
            return None  # a previous component was buried -> disconnected
        rootid = {}
        nxt = 1
        newlabels = [0] * H
        for r in newcells:
            root = find(('n', r))
            rid = rootid.get(root)
            if rid is None:
                rid = nxt
                rootid[root] = rid
                nxt += 1
            newlabels[r] = rid
        return ('ext', canon(newlabels))

    C = [0] * (N + 1)
    dp = defaultdict(lambda: [0] * (N + 1))

    # Start: first (leftmost) column, nonempty; components = vertical runs of S.
    for S in range(1, 1 << H):
        cells = bin(S).count("1")
        if cells > N:
            continue
        labels = [0] * H
        nxt = 1
        r = 0
        while r < H:
            if (S >> r) & 1:
                lab = nxt
                nxt += 1
                while r < H and (S >> r) & 1:
                    labels[r] = lab
                    r += 1
            else:
                r += 1
        dp[canon(labels)][cells] += 1

    subsets = list(range(1, 1 << H))
    while dp:
        ndp = defaultdict(lambda: [0] * (N + 1))
        for state, vec in dp.items():
            hi = 0
            for n in range(N, -1, -1):
                if vec[n]:
                    hi = n
                    break
            if hi == 0 and vec[0] == 0:
                continue
            # Close option: an empty next column finalizes iff single component.
            comps = set(x for x in state if x)
            if len(comps) == 1:
                for n in range(N + 1):
                    if vec[n]:
                        C[n] += vec[n]
            # Extend options.
            for S in subsets:
                add = bin(S).count("1")
                if add > N - 1:
                    continue
                key = (state, S)
                if key in memo:
                    act = memo[key]
                else:
                    act = compute_ext(state, S)
                    memo[key] = act
                if act is None:
                    continue
                nst = act[1]
                nv = ndp[nst]
                lim = min(hi, N - add)
                for n in range(lim + 1):
                    v = vec[n]
                    if v:
                        nv[n + add] += v
        # drop depleted states
        dp = defaultdict(lambda: [0] * (N + 1))
        for st, vec in ndp.items():
            if any(vec):
                dp[st] = vec
    return C


def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    Nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 36

    # banked triangle (kink-derived), prefer a36 then a35
    def load_banked():
        T = {}
        for base in ("results/ns_a36/perheight", "results/ns_a35/perheight"):
            d = os.path.join(ROOT, base)
            if not os.path.isdir(d):
                continue
            for H in range(1, 60):
                f = os.path.join(d, f"h{H}.out")
                if not os.path.exists(f):
                    continue
                with open(f) as fh:
                    for line in fh:
                        p = line.split()
                        if len(p) >= 2:
                            T[(int(p[0]), H)] = int(p[1])
            break
        return T

    banked = load_banked()
    bmax = max((n for (n, _) in banked), default=0)

    print(f"strip engine: Hmax={Hmax} Nmax={Nmax}  (banked up to n={bmax})")

    # independent small-n ground truth
    nb = 9
    print(f"brute-force anchor to n={nb} ...", flush=True)
    bt = brute_T(nb)

    # compute C_H for H = 0..Hmax  (C_0 == all zero)
    Ccols = {-1: [0] * (Nmax + 1), 0: [0] * (Nmax + 1)}
    for H in range(1, Hmax + 1):
        t0 = time.time()
        Ccols[H] = strip_C(H, Nmax)
        print(f"  C_{H:<2d} computed in {time.time()-t0:6.1f}s", flush=True)

    # recover T and validate
    print()
    print("== validation: strip-engine T(n,H) vs brute (n<=9) and banked ==")
    brute_ok = brute_bad = bank_ok = bank_bad = 0
    first_bad = None
    Teng = {}
    for H in range(1, Hmax + 1):
        for n in range(H, Nmax + 1):
            t = Ccols[H][n] - 2 * Ccols[H - 1][n] + Ccols[H - 2][n]
            Teng[(n, H)] = t
            if n <= nb:
                exp = bt.get((n, H), 0)
                if t == exp:
                    brute_ok += 1
                else:
                    brute_bad += 1
                    first_bad = first_bad or ("brute", n, H, t, exp)
            if (n, H) in banked:
                if t == banked[(n, H)]:
                    bank_ok += 1
                else:
                    bank_bad += 1
                    first_bad = first_bad or ("bank", n, H, t, banked[(n, H)])
    print(f"  vs brute (n<=9):  {brute_ok} match, {brute_bad} MISMATCH")
    print(f"  vs banked triangle: {bank_ok} match, {bank_bad} MISMATCH")
    if first_bad:
        src, n, H, got, exp = first_bad
        print(f"  first mismatch [{src}] T({n},{H}): engine={got} expected={exp}")
    else:
        print("  ALL AGREE -> triangle columns H<=%d independently confirmed" % Hmax)

    # show the atom-degree byproduct: C_H recurrence orders are the atom degrees
    print()
    print("== C_H head values (independent), n = H..H+4 ==")
    for H in range(1, Hmax + 1):
        row = [Ccols[H][n] for n in range(H, min(H + 5, Nmax + 1))]
        print(f"  C_{H:<2d}: " + " ".join(str(x) for x in row))


if __name__ == "__main__":
    main()
