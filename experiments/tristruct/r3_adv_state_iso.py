#!/usr/bin/env python3
"""r3_adv_state_iso.py — independence adversary, round 3.

Settles, by measurement, whether the cancellation DP's colour-coincidence
partition states are the same object as the incumbent engines' connectivity
partition states (the Motzkin object of king-column-motzkin.md), and audits
the residue/CRT layer of results/triangle-r3-l6-wildcard.md as arithmetic.

Everything below is written from the identity A_n(q) = sum_S q^{c(S)}
(= #{(S, f: S->[q]) : f constant on king-adjacent pairs}) and from the
incumbent rule as stated in results/triangle-r3-harness.md Part 3.  It is a
third implementation: not the branch's probe, not L6's.

Parts:
  1. My own cell-at-a-time colour DP, exact integers, validated against my
     own brute-force BFS at small boxes; [q^0]=0 and A_n(1)=C(HW,n) checks.
  2. Stencil-insensitivity demo: drop the NW adjacency; both structural
     self-checks still PASS while [q^1] is wrong.  (The named audit gap.)
  3. Residue/CRT demo at probe scale: run mod small primes, reconstruct,
     compare exact; exhibit a vanishing residue (benign).
  4. Column-cut census, H=2..9: reachable colour states (projected at column
     boundaries) vs my own union-find incumbent DP (with stranded death);
     compare both to the closed forms sum_k C(H+1,2k)*Bell(k) and
     Motzkin(H+1)-1; exhibit the crossing witness ABAB at H=7; check
     containment (colour >= incumbent) and that no colour transition ever
     merges two existing classes.
  5. Window census to H=12 (my implementation) vs branch numbers; ratio
     trend for the extrapolation-risk note.
  6. CRT prime-count arithmetic against the exact banked T(40,15).

Laptop, exact integer arithmetic, throwaway.
"""

import sys, time, itertools
from collections import defaultdict
from math import comb

LOG = open(sys.argv[0].replace(".py", ".log"), "w")


def out(s):
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


# ---------------------------------------------------------------- colour DP
def canon(state):
    m, nxt, o = {}, 1, []
    for v in state:
        if v == 0:
            o.append(0)
        else:
            if v not in m:
                m[v] = nxt
                nxt += 1
            o.append(m[v])
    return tuple(o)


def colour_dp(H, W, mod=None, drop_nw=False):
    """Cell-at-a-time colour-coincidence DP over the H x W box.
    Window = last H+1 cells, column-major; slot j holds cell k-H-1+j where
    k is the cell being placed.  Neighbours of (col,r) among earlier cells:
    (col,r-1)=slot H, (col-1,r-1)=slot 0, (col-1,r)=slot 1, (col-1,r+1)=slot 2.
    Returns dict n -> (a0, a1) with A_n(q) = a0 + a1 q  (mod q^2), plus the
    per-n value A_n(1) accumulated in a separate full-integer channel is NOT
    kept; instead run with q literally = 1 via the identity channel below.
    Weights: empty 1; forced join 1; clash 0; free: join each live class 1,
    fresh class (q - b) with b = #live classes in the window.
    """
    NW = H + 1
    red = lambda x: x % mod if mod else x
    states = {(tuple([0] * NW), 0): (1, 0)}
    merged_ever = False
    for col in range(W):
        for r in range(H):
            nbr = []
            if r > 0:
                nbr.append(H)
                if col > 0 and not drop_nw:
                    nbr.append(0)          # NW across the cut
            if col > 0:
                nbr.append(1)              # W
                if r < H - 1:
                    nbr.append(2)          # SW
            new = defaultdict(lambda: (0, 0))

            def add(key, a0, a1):
                b0, b1 = new[key]
                new[key] = (red(b0 + a0), red(b1 + a1))

            for (win, n), (a0, a1) in states.items():
                cls = set(win[s] for s in nbr) - {0}
                add((canon(win[1:] + (0,)), n), a0, a1)          # empty
                if len(cls) == 0:
                    live = sorted(set(win) - {0})
                    b = len(live)
                    for x in live:                               # join
                        add((canon(win[1:] + (x,)), n + 1), a0, a1)
                    # fresh: multiply (a0 + a1 q)(q - b) mod q^2
                    add((canon(win[1:] + (max(win) + 1,)), n + 1),
                        red(-b * a0), red(a0 - b * a1))
                elif len(cls) == 1:
                    add((canon(win[1:] + (cls.pop(),)), n + 1), a0, a1)
                # >= 2 classes: clash, weight 0
            states = dict(new)
    res = defaultdict(lambda: (0, 0))
    for (win, n), (a0, a1) in states.items():
        b0, b1 = res[n]
        res[n] = (red(b0 + a0), red(b1 + a1))
    return dict(res)


def colour_dp_at_q(H, W, qval, drop_nw=False):
    """Same DP with q evaluated at an integer (full polynomial check
    channel): returns n -> A_n(qval) as exact integers."""
    NW = H + 1
    states = {(tuple([0] * NW), 0): 1}
    for col in range(W):
        for r in range(H):
            nbr = []
            if r > 0:
                nbr.append(H)
                if col > 0 and not drop_nw:
                    nbr.append(0)
            if col > 0:
                nbr.append(1)
                if r < H - 1:
                    nbr.append(2)
            new = defaultdict(int)
            for (win, n), w in states.items():
                cls = set(win[s] for s in nbr) - {0}
                new[(canon(win[1:] + (0,)), n)] += w
                if len(cls) == 0:
                    live = sorted(set(win) - {0})
                    for x in live:
                        new[(canon(win[1:] + (x,)), n + 1)] += w
                    new[(canon(win[1:] + (max(win) + 1,)), n + 1)] += \
                        w * (qval - len(live))
                elif len(cls) == 1:
                    new[(canon(win[1:] + (cls.pop(),)), n + 1)] += w
            states = dict(new)
    res = defaultdict(int)
    for (win, n), w in states.items():
        res[n] += w
    return dict(res)


def brute(H, W, kings=True):
    """My own brute-force count of connected n-subsets of the H x W box."""
    cells = [(c, r) for c in range(W) for r in range(H)]
    cnt = defaultdict(int)
    for n in range(1, len(cells) + 1):
        for S in itertools.combinations(cells, n):
            Ss = set(S)
            seen, stack = {S[0]}, [S[0]]
            while stack:
                c, r = stack.pop()
                for dc in (-1, 0, 1):
                    for dr in (-1, 0, 1):
                        if kings and (dc, dr) != (0, 0):
                            p = (c + dc, r + dr)
                            if p in Ss and p not in seen:
                                seen.add(p)
                                stack.append(p)
            if len(seen) == n:
                cnt[n] += 1
    return cnt


# ------------------------------------------------------- incumbent (UF) DP
def uf_column_states(H, W):
    """My own whole-column union-find DP, per harness Part 3: labels per row,
    3-row cross-cut stencil, stranded-component death.  Returns the set of
    reachable nonempty column states (canonical label tuples) and whether
    any transition merged two distinct old labels (it will: that is the
    incumbent's defining move)."""
    def step(old, mask):
        # tokens: new rows 0..H-1 -> 0..H-1 ; old label L -> H+L
        parent = {}

        def find(x):
            while parent.get(x, x) != x:
                parent[x] = parent.get(parent[x], parent[x])
                x = parent[x]
            return x

        def unite(x, y):
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[rx] = ry
                return True
            return False

        merged_old = False
        for r in range(H):
            if not mask >> r & 1:
                continue
            if r and mask >> (r - 1) & 1:
                unite(r, r - 1)
            olds = set()
            for rr in (r - 1, r, r + 1):
                if 0 <= rr < H and old[rr]:
                    olds.add(old[rr])
            for L in olds:
                unite(r, H + L)
            if len(olds) >= 2:
                merged_old = True
        # stranded death: every old label's root must own a new cell
        newroots = {find(r) for r in range(H) if mask >> r & 1}
        for L in set(old) - {0}:
            if find(H + L) not in newroots:
                return None, False
        lab = [0] * H
        m, nxt = {}, 1
        for r in range(H):
            if mask >> r & 1:
                rt = find(r)
                if rt not in m:
                    m[rt] = nxt
                    nxt += 1
                lab[r] = m[rt]
        return tuple(lab), merged_old

    seen, frontier, any_merge = set(), set(), False
    for mask in range(1, 1 << H):
        st, _ = step(tuple([0] * H), mask)
        if st:
            seen.add(st)
            frontier.add(st)
    for _ in range(W - 1):
        nxt = set()
        for old in frontier:
            for mask in range(1, 1 << H):
                st, mg = step(old, mask)
                any_merge |= mg
                if st and st not in seen:
                    seen.add(st)
                    nxt.add(st)
                elif st:
                    nxt.add(st)
        frontier = nxt
    return seen, any_merge


def colour_column_states(H, W):
    """Reachable colour states projected at column boundaries (win[1:] =
    the just-finished column), via reachability-only cell-at-a-time DP.
    Also verifies no transition ever merges two distinct existing classes."""
    NW = H + 1
    states = {tuple([0] * NW)}
    proj = set()
    for col in range(W):
        for r in range(H):
            nbr = []
            if r > 0:
                nbr.append(H)
                if col > 0:
                    nbr.append(0)
            if col > 0:
                nbr.append(1)
                if r < H - 1:
                    nbr.append(2)
            new = set()
            for win in states:
                cls = set(win[s] for s in nbr) - {0}
                new.add(canon(win[1:] + (0,)))
                if len(cls) == 0:
                    live = sorted(set(win) - {0})
                    for x in live:
                        new.add(canon(win[1:] + (x,)))
                    new.add(canon(win[1:] + (max(win) + 1,)))
                elif len(cls) == 1:
                    new.add(canon(win[1:] + (cls.pop(),)))
                # >= 2: dropped -- never merged.  (Merging would mean a
                # successor identifying two distinct labels of win; the
                # three branches above extend/retire/join-at-birth only.)
            states = new
        if col >= 1:
            for win in states:
                colst = canon(win[1:])
                if any(colst):
                    proj.add(colst)
    return proj


def bell(k):
    B = [[1]]
    for i in range(1, k + 1):
        row = [B[-1][-1]]
        for j in range(i):
            row.append(row[-1] + B[-1][j])
        B.append(row)
    return B[k][0]


def motzkin(n):
    M = [1, 1]
    for i in range(2, n + 1):
        M.append((M[i - 1] * (2 * i + 1) + M[i - 2] * (3 * i - 3)) // (i + 2))
    return M[n]


def is_noncrossing(labels):
    """labels = per-run class ids in top-to-bottom order."""
    for i, j in itertools.combinations(range(len(labels)), 2):
        for k, l in itertools.combinations(range(len(labels)), 2):
            if i < k < j < l and labels[i] == labels[j] != labels[k] == labels[l]:
                return False
    return True


def runs_partition(colst):
    """Column label tuple -> per-run class ids, top to bottom."""
    runsl, prev = [], 0
    for v in colst:
        if v and not prev:
            runsl.append(v)
        prev = v
    return runsl


def main():
    t00 = time.time()

    # ---- Part 1: correctness of my own implementation
    out("== Part 1: colour DP vs my own brute force (exact integers) ==")
    for (H, W) in [(2, 4), (3, 3), (3, 4), (4, 3)]:
        dp = colour_dp(H, W)
        bf = brute(H, W)
        for n in range(1, H * W + 1):
            a0, a1 = dp.get(n, (0, 0))
            assert a0 == 0, f"[q^0]!=0 at H{H}W{W} n{n}"
            assert a1 == bf.get(n, 0), (H, W, n, a1, bf.get(n, 0))
        q1 = colour_dp_at_q(H, W, 1)
        for n in range(0, H * W + 1):
            assert q1.get(n, 0) == comb(H * W, n), ("q=1", H, W, n)
        out(f"  OK H={H} W={W}: [q^1]==brute all n; [q^0]==0; "
            f"A_n(1)==C({H*W},n)")

    # ---- Part 2: the structural checks do NOT cover the stencil
    out("== Part 2: drop NW adjacency; do the self-checks notice? ==")
    H, W = 3, 4
    dp = colour_dp(H, W, drop_nw=True)
    q1 = colour_dp_at_q(H, W, 1, drop_nw=True)
    q0_ok = all(dp.get(n, (0, 0))[0] == 0 for n in range(1, 13))
    binom_ok = all(q1.get(n, 0) == comb(12, n) for n in range(13))
    bf = brute(H, W)
    wrong = [n for n in range(1, 13) if dp.get(n, (0, 0))[1] != bf.get(n, 0)]
    out(f"  [q^0]=0 still passes: {q0_ok}; A_n(1)=C(12,n) still passes: "
        f"{binom_ok}; [q^1] wrong at n={wrong}")
    assert q0_ok and binom_ok and wrong

    # ---- Part 3: residue/CRT at probe scale
    out("== Part 3: residues mod small primes + CRT reconstruction ==")
    H, W = 3, 4
    exact = {n: colour_dp(H, W)[n][1] for n in range(1, 13)}
    primes = [5, 7, 11, 13]
    resid = {p: {n: colour_dp(H, W, mod=p)[n][1] % p for n in range(1, 13)}
             for p in primes}
    for p in primes:
        for n in range(1, 13):
            assert resid[p][n] == exact[n] % p, (p, n)
    # CRT
    from math import prod
    Pr = prod(primes)
    for n in range(1, 13):
        x = 0
        for p in primes:
            Np = Pr // p
            x += resid[p][n] * Np * pow(Np, -1, p)
        assert x % Pr == exact[n] % Pr, ("CRT", n)
    vanish = [(n, p) for p in primes for n in range(1, 13)
              if exact[n] and exact[n] % p == 0]
    out(f"  OK: per-prime residues == exact mod p; CRT reconstruction == "
        f"exact (mod {Pr}); vanishing residues (n,p)={vanish[:4]}... benign")

    # ---- Part 4: the column-cut census — the isomorphism question
    out("== Part 4: column-cut state sets, colour vs incumbent ==")
    out("H  colour  closedform(Bell)  incumbent  Motzkin(H+1)-1  "
        "colour>=incumbent  crossing_states")
    for H in range(2, 10):
        W = max(6, H)
        cs = colour_column_states(H, W)
        ufs, any_merge = uf_column_states(H, W)
        bells = sum(comb(H + 1, 2 * k) * bell(k)
                    for k in range(1, (H + 1) // 2 + 1))
        motz = motzkin(H + 1) - 1
        crossing = [s for s in cs if not is_noncrossing(runs_partition(s))]
        contain = ufs <= cs
        out(f"{H}  {len(cs)}  {bells}  {len(ufs)}  {motz}  {contain}  "
            f"{len(crossing)}")
        assert len(cs) == bells, (H, len(cs), bells)
        assert len(ufs) == motz, (H, len(ufs), motz)
        assert contain
        if H < 7:
            assert not crossing
        if H == 7:
            wit = (1, 0, 2, 0, 1, 0, 2)
            out(f"  H=7 witness ABAB {wit}: in colour set: {wit in cs}; "
                f"in incumbent set: {wit in ufs}; "
                f"crossing count at H=7: {len(crossing)}")
            assert wit in cs and wit not in ufs and len(crossing) == 1
        if H == 9:
            out(f"  branch cross-check: colour 2242? {len(cs)==2242}; "
                f"incumbent 2187? {len(ufs)==2187}")
        assert any_merge or H < 3, "incumbent never merged?!"
        # (H=2: a column is a single run, so only one old label can exist)
    out("  incumbent transitions DO merge distinct old labels (union-find); "
        "colour transitions NEVER do (extend/join-at-birth/retire/clash only)")

    # ---- Part 5: window census vs branch, ratio trend
    out("== Part 5: window census (distinct windows, steady state) ==")
    branch = {4: 45, 5: 111, 6: 279, 7: 718, 8: 1884, 9: 5041, 10: 13733,
              11: 38065, 12: 107241, 13: 306858, 14: 891074}
    prev = None
    for H in range(4, 13):
        NW = H + 1
        states = {tuple([0] * NW)}
        mx = 0
        for col in range(8):
            for r in range(H):
                nbr = []
                if r > 0:
                    nbr.append(H)
                    if col > 0:
                        nbr.append(0)
                if col > 0:
                    nbr.append(1)
                    if r < H - 1:
                        nbr.append(2)
                new = set()
                for win in states:
                    cls = set(win[s] for s in nbr) - {0}
                    new.add(canon(win[1:] + (0,)))
                    if len(cls) == 0:
                        live = sorted(set(win) - {0})
                        for x in live:
                            new.add(canon(win[1:] + (x,)))
                        new.add(canon(win[1:] + (max(win) + 1,)))
                    elif len(cls) == 1:
                        new.add(canon(win[1:] + (cls.pop(),)))
                states = new
                mx = max(mx, len(states))
        g = f"{mx/prev:.3f}" if prev else "-"
        mark = "==branch" if branch.get(H) == mx else \
            f"BRANCH {branch.get(H)} DIFFERS"
        out(f"  H={H}  windows={mx}  ratio={g}  {mark}")
        prev = mx

    # ---- Part 6: CRT prime-count arithmetic for the band
    out("== Part 6: how many 8-bit prime runs cover T(40,15)? ==")
    T4015 = 6374412577120147022430261962743   # harness Part 2, real-sweep
    ps = [p for p in range(255, 2, -2)
          if all(p % d for d in range(3, int(p ** .5) + 1, 2))]
    from math import prod, log2
    for k in range(10, 17):
        pr = prod(ps[:k])
        out(f"  k={k}: product of {k} largest 8-bit primes = 2^"
            f"{log2(pr):.2f}  {'>=' if pr > T4015 else '< '} T(40,15)"
            f" = 2^{log2(T4015):.2f}")
    kmin = next(k for k in range(1, 30) if prod(ps[:k]) > T4015)
    out(f"  minimum runs with largest 8-bit primes: {kmin} "
        f"(L6 claimed 13)")

    out(f"total {time.time()-t00:.1f}s")


if __name__ == "__main__":
    main()
