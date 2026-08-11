# probe_cutcount_dp.py — second-source team, Teammate B probe (throwaway).
# Purpose: validate + measure the "consistent-cut / coloring transform" counter:
#   A_n(q) = sum over n-cell subsets S of an HxW king strip of q^{c(S)}.
#   N_{n,1} = [q^1] A_n(q) = number of king-CONNECTED n-cell subsets.
#   Computed mod q^2 by a cell-at-a-time frontier DP whose state is the
#   COLOR-EQUALITY pattern (arbitrary partition, no stranded-component death,
#   no connectivity decision). Connectivity emerges from algebra, not union-find.
# Validation: brute force over all 2^(HW) subsets at small sizes.
# Measurement: reachable state counts per height (the resource that binds).
# Command: python3 experiments/probe_cutcount_dp.py   (gympie, <15 min, <2 GB)
import sys
from itertools import product

def brute(H, W):
    """A_n(q) coefficients by brute force: returns dict n -> list of N_{n,j}."""
    cells = [(r, c) for c in range(W) for r in range(H)]
    idx = {v: i for i, v in enumerate(cells)}
    nb = [[] for _ in cells]
    for (r, c) in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr or dc) and (r+dr, c+dc) in idx:
                    nb[idx[(r, c)]].append(idx[(r+dr, c+dc)])
    out = {}
    for mask in range(1 << len(cells)):
        S = [i for i in range(len(cells)) if mask >> i & 1]
        n = len(S)
        seen, comps = set(), 0
        for s in S:
            if s in seen: continue
            comps += 1
            stack = [s]; seen.add(s)
            while stack:
                v = stack.pop()
                for u in nb[v]:
                    if mask >> u & 1 and u not in seen:
                        seen.add(u); stack.append(u)
        d = out.setdefault(n, {})
        d[comps] = d.get(comps, 0) + 1
    return out

def dp(H, W, count_states_only=False):
    """Frontier DP, column-major, frontier = last H+1 cells (0=empty, else
    canonical block id). Weight per (state): dict n -> (c0, c1) mod q^2.
    Returns dict n -> (N_{n,0}=A_n(0), N_{n,1}), plus max state count seen."""
    # frontier tuple f[0..H]: f[H] is the cell processed H+1 cells ago... we
    # keep newest at end. New cell at (r,c): prior neighbours are positions
    # (len-1) [same col r-1, skip if r==0], and prev col r-1,r,r+1 at offsets
    # H-1+... : with frontier of size H+1 (newest last), prev-column row r+dr
    # sits at offset (H) - (H - dr) ... easier: keep frontier as list of the
    # last H+1 processed cells in order; neighbour offsets from the end:
    #   same column r-1  -> offset 1 (last processed) if r>0
    #   prev column r+1  -> offset H-1+1 = H ... derive: cells processed since
    #   (r+1, c-1): rows r+2..H-1 of col c-1 (H-2-r cells) + rows 0..r-1 of
    #   col c (r cells) => offset = H-2-r + r + 1 = H-1. So:
    #   prev col r+1 -> offset H-1 (if r+1 < H), r -> H, r-1 -> H+1 == oldest
    # frontier length H+1 holds offsets 1..H+1.
    maxstates = 0
    canon_cache = {}
    def canon(f):
        if f in canon_cache: return canon_cache[f]
        m, nxt, out = {}, 1, []
        for x in f:
            if x == 0: out.append(0)
            else:
                if x not in m: m[x] = nxt; nxt += 1
                out.append(m[x])
        r = tuple(out)
        canon_cache[f] = r
        return r
    # state -> dict area -> [c0, c1]
    states = {tuple([0]*(H+1)): {0: [1, 0]}}
    for c in range(W):
        for r in range(H):
            new = {}
            for f, areas in states.items():
                nbrs = []
                if r > 0 and f[-1]: nbrs.append(f[-1])
                if c > 0:
                    if r+1 < H and f[1]: nbrs.append(f[1])   # offset H-1 from end of len H+1 list = index 2? see below
                    if f[2-(1 if r+1<H else 0)]: pass
            # (rebuilt below — see real loop)
            break
        break
    # The offset bookkeeping above is fiddly; do it with explicit coordinates.
    # frontier as dict of the last H+1 cells keyed by (row, col) is clearer.
    from collections import deque
    Frontier = tuple  # of (cellstate over window)
    # window: list of block-ids for cells [(c,r) processed], keep last H+1.
    start = ((), {0: [1, 0]})
    states = {(): {0: [1, 0]}}
    order = [(c, r) for c in range(W) for r in range(H)]
    pos = {v: i for i, v in enumerate(order)}
    for i, (c, r) in enumerate(order):
        neigh_idx = []
        for dr, dc in ((-1, 0), (-1, -1), (0, -1), (1, -1)):
            rr, cc = r+dr, c+dc
            if 0 <= rr < H and cc >= 0:
                j = pos[(cc, rr)]
                if j < i and i - j <= H+1: neigh_idx.append(i - j - 1)  # 0 = newest
        new = {}
        for f, areas in states.items():
            fl = list(f)  # newest first
            def add(key, mult_c0, mult_c1, shift):
                # weight (mult_c0 + mult_c1*q); shift area by `shift`
                kk = canon(tuple(key[:H+1]))
                tgt = new.setdefault(kk, {})
                for n, (c0, c1) in areas.items():
                    e = tgt.setdefault(n+shift, [0, 0])
                    e[0] += c0*mult_c0
                    e[1] += c1*mult_c0 + c0*mult_c1
            # empty cell
            add([0]+fl, 1, 0, 0)
            # occupied cell
            occ = sorted({fl[j] for j in neigh_idx if j < len(fl) and fl[j]})
            if len(occ) == 1:
                add([occ[0]]+fl, 1, 0, 1)
            elif len(occ) == 0:
                blocks = sorted({x for x in fl if x})
                b = len(blocks)
                for bid in blocks:               # coincide with existing block
                    add([bid]+fl, 1, 0, 1)
                nid = max(blocks, default=0)+1   # fresh colour: weight (q - b)
                add([nid]+fl, -b, 1, 1)
            # len(occ) >= 2: weight 0 (distinct colours meet) — drop.
        states = new
        maxstates = max(maxstates, len(states))
        if count_states_only and len(states) > 5_000_000:
            return None, maxstates
    # close out: sum everything
    total = {}
    for f, areas in states.items():
        for n, (c0, c1) in areas.items():
            e = total.setdefault(n, [0, 0])
            e[0] += c0; e[1] += c1
    return total, maxstates

if __name__ == "__main__":
    import time
    # 1) validate against brute force
    for (H, W) in [(2, 3), (3, 3), (3, 4), (2, 6), (4, 3)]:
        bt = brute(H, W)
        t, _ = dp(H, W)
        ok = True
        for n in bt:
            if n == 0: continue
            want1 = bt[n].get(1, 0)
            got1 = t.get(n, [0, 0])[1]
            want0 = 0  # A_n(0) = 0 for n>=1 (q^c has no constant term)
            got0 = t.get(n, [0, 0])[0]
            if want1 != got1 or got0 != want0:
                ok = False
                print(f"MISMATCH H={H} W={W} n={n}: dp(q^1)={got1} brute={want1} dp(q^0)={got0}")
        print(f"validate H={H} W={W}: {'OK' if ok else 'FAIL'}")
    # 2) measure state growth per height
    for H in range(4, 13):
        t0 = time.time()
        res = dp(H, H+2, count_states_only=True)
        print(f"H={H}: max frontier states = {res[1]}  ({time.time()-t0:.1f}s)")
        sys.stdout.flush()
        if time.time()-t0 > 240: break
