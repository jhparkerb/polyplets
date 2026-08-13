#!/usr/bin/env python3
"""r3_spin_counts.py -- INV-8 spin-basis repricing: exact state counts.

Independent verification (from the definition, not the predecessor's probe) of
the reachable spin-basis state counts for the q=2 colour DP on a height-m king
strip, plus the cell-at-a-time window census and the whole-column pair count
that decides the kernel shape.

Facts established here, all exact integer arithmetic:
  1. Valid whole-column states (strings over {E,A,B}, occupied runs
     monochromatic) satisfy t_m = 2 t_{m-1} + t_{m-2}, t_1 = 3, t_2 = 7
     (companion Pell / A001333(m+1)); brute-enumerated m <= 12.
  2. Reachability: every valid string is reachable (empty column -> any valid
     string is a legal transition); checked mechanically at m <= 7.
  3. Cell-at-a-time window census W(m) = max over kink row r of valid
     colourings of the (m+1)-cell mixed frontier; enumerated exactly m <= 9,
     compared to t_{m+1}.
  4. Whole-column compatible-pair count P_m (exact row-transfer DP): shows the
     whole-column kernel is priced out and cell-at-a-time is mandatory.
"""

from itertools import product

E, A, B = 0, 1, 2


def clash(x, y):
    return x > 0 and y > 0 and x != y


def valid_column(s):
    return not any(clash(s[i], s[i + 1]) for i in range(len(s) - 1))


def t_brute(m):
    return sum(1 for s in product((E, A, B), repeat=m) if valid_column(s))


def t_rec(mmax):
    t = {0: 1, 1: 3}
    for m in range(2, mmax + 1):
        t[m] = 2 * t[m - 1] + t[m - 2]
    return t


def compat(s, sp):
    """Whole-column transition: new column sp against old column s.

    A new cell at row r is king-adjacent to old-column rows r-1, r, r+1."""
    m = len(s)
    for r in range(m):
        if sp[r] == E:
            continue
        for rr in (r - 1, r, r + 1):
            if 0 <= rr < m and clash(s[rr], sp[r]):
                return False
    return True


def reachable(m):
    """BFS closure from the all-empty column under the transition."""
    start = tuple([E] * m)
    seen = {start}
    frontier = [start]
    all_valid = [s for s in product((E, A, B), repeat=m) if valid_column(s)]
    while frontier:
        nxt = []
        for s in frontier:
            for sp in all_valid:
                if sp not in seen and compat(s, sp):
                    seen.add(sp)
                    nxt.append(sp)
        frontier = nxt
    return seen, set(all_valid)


def window_cells(m, r):
    """Mixed frontier after placing rows 0..r-1 of column x+1 (kink at r):
    new-column cells (1, 0..r-1) plus old-column cells (0, r-1..m-1)."""
    cells = [(1, i) for i in range(r)]
    cells += [(0, i) for i in range(max(r - 1, 0), m)]
    return cells


def king_adjacent(p, q):
    return max(abs(p[0] - q[0]), abs(p[1] - q[1])) == 1


def window_census(m):
    best = 0
    for r in range(m + 1):
        cells = window_cells(m, r)
        pairs = [(i, j) for i in range(len(cells)) for j in range(i + 1, len(cells))
                 if king_adjacent(cells[i], cells[j])]
        cnt = 0
        for colours in product((E, A, B), repeat=len(cells)):
            if not any(clash(colours[i], colours[j]) for i, j in pairs):
                cnt += 1
        best = max(best, cnt)
    return best


def pair_count(m):
    """Exact count of compatible whole-column state pairs (s, s') via a
    row-by-row transfer over symbol pairs (a_r, b_r)."""
    syms = [(a, b) for a in (E, A, B) for b in (E, A, B) if not clash(a, b)]
    ok_step = {}
    for s1 in syms:
        for s2 in syms:
            a1, b1 = s1
            a2, b2 = s2
            bad = clash(a1, a2) or clash(b1, b2) or clash(a1, b2) or clash(b1, a2)
            ok_step[(s1, s2)] = not bad
    vec = {s: 1 for s in syms}
    for _ in range(m - 1):
        nv = {s: 0 for s in syms}
        for s1, w in vec.items():
            for s2 in syms:
                if ok_step[(s1, s2)]:
                    nv[s2] += w
        vec = nv
    return sum(vec.values())


def main():
    t = t_rec(24)

    print("== 1. valid whole-column states: brute vs recurrence ==")
    for m in range(1, 13):
        tb = t_brute(m)
        mark = "OK" if tb == t[m] else "MISMATCH"
        print(f"  m={m:2d}  brute={tb:8d}  rec={t[m]:8d}  {mark}")
        assert tb == t[m]
    print("  exact by recurrence:")
    for m in (19, 20, 21, 22, 23):
        print(f"  t_{m} = {t[m]:,}")

    print("== 2. reachability (from empty column) ==")
    for m in range(1, 8):
        seen, allv = reachable(m)
        mark = "OK" if seen == allv else "MISMATCH"
        print(f"  m={m}  reachable={len(seen)}  valid={len(allv)}  {mark}")
        assert seen == allv

    print("== 3. cell-at-a-time window census W(m) vs t_(m+1) ==")
    ratios = []
    for m in range(2, 10):
        w = window_census(m)
        ratios.append((m, w, t[m + 1], w / t[m + 1]))
        print(f"  m={m}  W={w:7d}  t_{m+1}={t[m+1]:7d}  W/t = {w / t[m+1]:.4f}")

    print("== 4. whole-column compatible pairs P_m ==")
    prev = None
    for m in list(range(2, 12)) + [19, 20, 21]:
        p = pair_count(m)
        g = f"  x{p/prev:.3f}" if prev is not None and m <= 11 else ""
        print(f"  m={m:2d}  P={p:,}{g}")
        if m <= 11:
            prev = p

    print("== 5. window census follows the same Pell recurrence ==")
    # W(m) = 2 W(m-1) + W(m-2) observed on the enumerated points; W <= t_{m+1}
    # unconditionally (the window constraint graph contains a Hamiltonian
    # path of its m+1 cells, so window colourings inject into path strings).
    W = {2: 15, 3: 37}
    for m in range(4, 22):
        W[m] = 2 * W[m - 1] + W[m - 2]
    for m, w, tnext, _r in ratios:
        mark = "OK" if W[m] == w else "MISMATCH"
        print(f"  m={m}  enumerated={w}  recurrence={W[m]}  {mark}")
        assert W[m] == w
    for m in (18, 19, 20, 21):
        print(f"  W({m}) = {W[m]:,}   (unconditional bound t_{m+1} = {t[m+1]:,})")

    print("== 6. cost model (slot-ops), untransposed design ==")
    # T(40,H) mod 2 for H in {20,21} needs strips m = H-2..H, i.e.
    # m in {18,19,20,21}; sweep = 41 columns (widths run to n=40 for king
    # animals, +1 stability column); stages per column = m; branching <= 3;
    # 41 area slots; window states = W(m).
    total = 0
    for m in (18, 19, 20, 21):
        ops = 41 * m * W[m] * 3 * 41
        total += ops
        print(f"  run m={m}: window {W[m]:>12,}  slot-ops = {ops:.3e}")
    print(f"  TOTAL slot-ops = {total:.3e}")
    print(f"  wall at measured 40 ns/slot-op (dalby B1 anchor): "
          f"{total*40e-9/86400:.1f} thread-days")
    # RAM, largest run (m=21), sorted-array double buffer:
    # key u64 (44 bits used) + 41 slots x 2 bits = 11 B payload per buffer.
    per_state = 2 * (8 + 11)
    print(f"  RAM peak (m=21): {W[21]*per_state/2**30:.1f} GiB at "
          f"{per_state} B/state (x1.5 margin: {W[21]*per_state*1.5/2**30:.1f} GiB)")


if __name__ == "__main__":
    main()
