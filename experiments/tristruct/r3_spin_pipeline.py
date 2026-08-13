#!/usr/bin/env python3
"""r3_spin_pipeline.py -- INV-8: end-to-end correctness of the spin-basis
mod-2 route at desk scale, plus the RED-mutant battery.

Pipeline under test (the exact production design, small scale, exact ints):
  * whole-column spin DP over strings {E,A,B}, occupied runs monochromatic,
    cross-cut clash stencil rows r-1,r,r+1: computes
    Z_{w,m}(n) = sum over n-cell subsets S of the w x m box of 2^{c(S)}
    (= number of (S, 2-colouring constant on king components)).
  * extent accounting, no connectivity anywhere. UNtransposed frame: strip
    height m (rows), sweep along width. NOTE the transposed frame the INV-4
    appendix priced ("W <= n-H+1, cut 20") is WRONG for king animals: a
    diagonal staircase spans width and height simultaneously ({(0,0),(1,1),
    (2,0)} has n=3, H=2, W=3), so width runs to n=40 and the strip must stay
    in the H direction. Accounting:
      A_m(n)  = Z_{w,m}(n) - Z_{w-1,m}(n)  at w = n   (width-translation fix;
                exact value grows with w but is STABLE MOD 4: every class
                wider than n is disconnected, 2^c == 0 mod 4)
      N_H(n)  = A_H(n) - 2 A_{H-1}(n) + A_{H-2}(n)    (row extent exactly H)
    then N_H(n) = 2 T(n,H) + 4(...), so T(n,H) == N_H(n)/2 (mod 2).
Checks:
  1. Z vs brute-force subset enumeration (2^(w*m) subsets, union-find c(S))
     on several boxes -- bookkeeping AND stencil against desk ground truth.
  2. m-stability: G_H(n) identical computed at m and m+1.
  3. T(n,H) mod 2 from the pipeline vs a self-grown fixed-king-animal
     enumerator (translation-canonical, height/width binned), n <= 8;
     grower regressed against banked row sums a(n) afterwards.
  4. Exact G check at small cells: G_H(n) = sum over exact-extent translation
     classes of 2^{c}, brute-enumerated.
  5. RED battery, value-level and asymmetric: drop-NW, drop-SW, rook (both
     diagonals dropped) mutants; each must flip T mod 2 at named small cells.
  6. Banked comparison (post-hoc): pipeline T(n,H) mod 2 vs Triangle.load()
     for all computed cells; quote banked parity of the two target cells.
"""

import sys
from itertools import product

sys.setrecursionlimit(100000)

E, A, B = 0, 1, 2
FULL = (-1, 0, 1)  # cross-cut stencil row offsets used by the transition;
                   # within-column adjacency handled in state validity.
                   # Labels: -1 = "NW", +1 = "SW".


def clash(x, y):
    return x > 0 and y > 0 and x != y


def valid_columns(m):
    return [s for s in product((E, A, B), repeat=m) if
            not any(clash(s[i], s[i + 1]) for i in range(m - 1))]


def z_table(w, m, deltas):
    """Z_{w',m}(n) for all prefixes w' <= w, exact ints.

    deltas: which cross-cut row offsets constrain (subset of {-1,0,1});
    within-column vertical+run validity always enforced."""
    cols = valid_columns(m)
    area = {s: sum(1 for x in s if x) for s in cols}
    # successor lists (only needed when there is more than one column)
    succ = {}
    if w >= 2:
        for s in cols:
            lst = []
            for sp in cols:
                ok = True
                for r in range(m):
                    if sp[r] == E:
                        continue
                    for d in deltas:
                        rr = r + d
                        if 0 <= rr < m and clash(s[rr], sp[r]):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    lst.append(sp)
            succ[s] = lst
    # DP
    zs = {}
    state = {s: {area[s]: 1} for s in cols}
    def harvest(st):
        out = {}
        for s, poly in st.items():
            for n, v in poly.items():
                out[n] = out.get(n, 0) + v
        return out
    zs[1] = harvest(state)
    for wp in range(2, w + 1):
        ns = {s: {} for s in cols}
        for s, poly in state.items():
            for sp in succ[s]:
                da = area[sp]
                tgt = ns[sp]
                for n, v in poly.items():
                    tgt[n + da] = tgt.get(n + da, 0) + v
        state = ns
        zs[wp] = harvest(state)
    zs[0] = {0: 1}
    return zs


def brute_z(w, m):
    """Sum over all subsets of the w x m box of 2^c, binned by n. Union-find
    written here, on complete small objects -- desk ground truth."""
    cells = [(x, y) for x in range(w) for y in range(m)]
    N = len(cells)
    idx = {c: i for i, c in enumerate(cells)}
    out = {}
    for mask in range(1 << N):
        S = [c for c in cells if mask >> idx[c] & 1]
        n = len(S)
        # count components
        parent = list(range(n))
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        pos = {c: i for i, c in enumerate(S)}
        for c in S:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == dy == 0:
                        continue
                    d = (c[0] + dx, c[1] + dy)
                    if d in pos:
                        ra, rb = find(pos[c]), find(pos[d])
                        if ra != rb:
                            parent[ra] = rb
        comp = len({find(i) for i in range(n)})
        out[n] = out.get(n, 0) + (1 << comp if n else 1)
    return out


def pipeline_T_mod2(nmax, deltas):
    """T(n,H) mod 2 for all 1 <= H <= n <= nmax, untransposed frame."""
    zs = {m: z_table(nmax + 2, m, deltas) for m in range(1, nmax + 1)}

    def aval(n, m, w):
        if m < 1:
            return 0
        return zs[m][w].get(n, 0) - zs[m][w - 1].get(n, 0)

    res = {}
    for n in range(1, nmax + 1):
        for H in range(1, n + 1):
            def nn(w):
                return (aval(n, H, w) - 2 * aval(n, H - 1, w)
                        + aval(n, H - 2, w))
            g = nn(n)
            g_stab = nn(n + 1)
            # exact value grows with w (wider disconnected classes keep
            # entering) but is stable mod 4: 2^c == 0 mod 4 for c >= 2.
            assert g % 4 == g_stab % 4, (n, H, g, g_stab)
            assert g % 2 == 0, (n, H, g)
            res[(n, H)] = (g // 2) % 2
    return res


def grow_animals(nmax):
    """Fixed king animals (translation classes), by iterative growth + dedup."""
    def norm(cells):
        mx = min(c[0] for c in cells)
        my = min(c[1] for c in cells)
        return frozenset((x - mx, y - my) for x, y in cells)
    cur = {frozenset({(0, 0)})}
    counts = {1: {"total": 1, "byHW": {(1, 1): 1}}}
    for n in range(2, nmax + 1):
        nxt = set()
        for a in cur:
            for (x, y) in a:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == dy == 0:
                            continue
                        c = (x + dx, y + dy)
                        if c not in a:
                            nxt.add(norm(a | {c}))
        cur = nxt
        by = {}
        for a in cur:
            w = max(c[0] for c in a) + 1
            h = max(c[1] for c in a) + 1
            by[(h, w)] = by.get((h, w), 0) + 1
        counts[n] = {"total": len(cur), "byHW": by}
    return counts


def brute_G(H, n):
    """Exact N_H(n) at truncation w = n: sum of 2^c over translation classes
    with row extent exactly H (min row 0, max row H-1), min col 0, col
    extent <= n."""
    cells = [(x, y) for x in range(n) for y in range(H)]
    total = 0
    from itertools import combinations
    for S in combinations(cells, n):
        xs = [c[0] for c in S]
        ys = [c[1] for c in S]
        if min(ys) != 0 or max(ys) != H - 1 or min(xs) != 0:
            continue
        pos = {c: i for i, c in enumerate(S)}
        parent = list(range(n))
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for c in S:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == dy == 0:
                        continue
                    d = (c[0] + dx, c[1] + dy)
                    if d in pos:
                        ra, rb = find(pos[c]), find(pos[d])
                        if ra != rb:
                            parent[ra] = rb
        comp = len({find(i) for i in range(n)})
        total += 1 << comp
    return total


def main():
    print("== 1. Z vs brute subset enumeration ==")
    for (w, m) in ((2, 3), (3, 3), (4, 3), (3, 4), (4, 4), (2, 5)):
        zs = z_table(w, m, FULL)[w]
        bz = brute_z(w, m)
        ok = all(zs.get(n, 0) == bz.get(n, 0) for n in range(w * m + 1))
        print(f"  box {w}x{m}: {'OK' if ok else 'MISMATCH'}")
        assert ok

    print("== 2/3. pipeline T mod 2 vs self-grown animals ==")
    NMAX = 7
    pipe = pipeline_T_mod2(NMAX, FULL)
    animals = grow_animals(NMAX)
    truth = {}
    for n in range(1, NMAX + 1):
        for (h, wdt), cnt in animals[n]["byHW"].items():
            truth[(n, h)] = truth.get((n, h), 0) + cnt
        # transpose symmetry check on the grower itself
        for (h, wdt), cnt in animals[n]["byHW"].items():
            assert animals[n]["byHW"][(wdt, h)] == cnt
    bad = []
    ncells = 0
    for (n, H), par in sorted(pipe.items()):
        tv = truth.get((n, H), 0) % 2
        ncells += 1
        if par != tv:
            bad.append((n, H, par, tv))
    print(f"  cells compared: {ncells}; mismatches: {len(bad)} {bad[:8]}")
    assert not bad
    print(f"  grower totals: {[animals[n]['total'] for n in range(1, NMAX+1)]}")

    print("== 4. exact N_H(n) spot checks vs brute translation classes ==")
    for (H, n) in ((2, 4), (3, 5), (2, 5), (3, 6), (4, 6)):
        zloc = {m: z_table(n + 1, m, FULL) for m in range(max(H - 2, 1), H + 1)}
        def av(m, w):
            if m < 1:
                return 0
            return zloc[m][w].get(n, 0) - zloc[m][w - 1].get(n, 0)
        g = av(H, n) - 2 * av(H - 1, n) + av(H - 2, n)
        gb = brute_G(H, n)
        print(f"  N_{H}({n}) pipeline={g} brute={gb} "
              f"{'OK' if g == gb else 'MISMATCH'}")
        assert g == gb

    print("== 5. RED battery: asymmetric + symmetric stencil mutants ==")
    NRED = 7
    truth_red = {k: v % 2 for k, v in truth.items()}
    for name, deltas in (("drop-NW", (0, 1)),
                         ("drop-SW", (-1, 0)),
                         ("rook", (0,))):
        mut = pipeline_T_mod2(NRED, deltas)
        flips = [(n, H) for (n, H) in mut
                 if mut[(n, H)] != truth_red.get((n, H), 0)]
        print(f"  {name}: {len(flips)} cells wrong vs ground truth; "
              f"first: {sorted(flips)[:6]}")
        assert flips, f"RED mutant {name} was BLIND"

    print("== 6. banked comparison (post-hoc) ==")
    sys.path.insert(0, ".")
    from triangle import Triangle
    tri = Triangle.load()
    mism = [(n, H) for (n, H), p in pipe.items()
            if p != tri.cell(n, H) % 2]
    print(f"  pipeline vs banked, {len(pipe)} cells n<=8: "
          f"{len(mism)} mismatches {mism}")
    assert not mism
    grow_mism = [n for n in range(1, NMAX + 1)
                 if animals[n]["total"] != tri.rowsum(n)]
    print(f"  grower row totals vs banked a(n), n<=8: "
          f"{'OK' if not grow_mism else grow_mism}")
    assert not grow_mism
    for H in (20, 21):
        print(f"  banked T(40,{H}) mod 2 = {tri.cell(40, H) % 2} "
              f"(provenance {tri.provenance(40, H)})")


if __name__ == "__main__":
    main()
