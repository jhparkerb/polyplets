#!/usr/bin/env python3
"""r3_l6_residue_dp.py — L6 wildcard probe, round 3.

Independently re-derived implementation (from the identity, not from the
second-source branch's probe code) of the color-coincidence partition DP:

    A_n(q) = sum over n-cell subsets S of an H x W box of q^{c(S)}
           = #{ (S, f: S -> [q]) : f equal on king-adjacent pairs of S }

computed cell-at-a-time in Z[q]/(q^2); then C_1(n) = [q^1] A_n(q) is the
number of king-connected n-cell subsets of the box.  No connectivity is
decided anywhere: no union-find, no stranded-component death.  Connectivity
is read off as a polynomial coefficient at the end.

State: tuple over the window of H+1 cells; entry 0 = empty, entries 1..b =
color-class (coincidence partition) in canonical first-appearance order.
Transition per cell:
  - empty: weight 1
  - occupied, neighbors in exactly one class X: forced join X, weight 1
  - occupied, neighbors in >= 2 classes: distinct classes have distinct
    colors, so weight 0 (clash-zeroing)
  - occupied, no occupied window neighbor: color free among q -- join any
    of the b live classes (weight 1 each; a color class may span
    disconnected cells) or a fresh class (weight q - b)
Coefficients (a0, a1) mod M; multiply by (q-b): (a0,a1) -> (-b*a0, a0-b*a1).

Checks:
  1. exact (M = 2^61-1 as modulus, values far below) vs brute-force BFS count
     of king-connected n-subsets at small (H,W), every n.
  2. [q^0] A_n = 0 for all n >= 1 (structural).
  3. RED control: corrupt one transition weight, expect mismatch.
Measurements: reachable window-state census and per-column wall by H.

Laptop, exact integer arithmetic, throwaway.
"""

import sys, time, itertools
from collections import defaultdict

M = (1 << 61) - 1  # modulus; large prime so small-case results are exact


def neighbors_in_window(H, r):
    """Window = last H+1 cells in column-major order (col*H + row).
    New cell at (col, r).  Occupied earlier cells adjacent to it, as window
    indices (0 = oldest = (col-1, r+1 side)...): window[i] holds the cell
    H+1 positions back... We index window so that window[H] would be the new
    cell; predecessors at offsets: same column above = 1 back; previous
    column rows r-1, r, r+1 = H, H+1... use explicit positions:
    cell k = col*H + r; window covers cells k-H-1 .. k-1 at slots 0..H.
    Neighbor cells of (col, r) among earlier cells:
      (col, r-1)   -> k-1        -> slot H-1   (if r > 0)
      (col-1, r-1) -> k-H-1      -> slot 0     (wait: k-(H+1) is out; slots
                                    hold k-H-1+j at slot j, j=0..H)
    slot(j) holds cell k-H-1+j, so cell c -> slot c-k+H+1.
      (col, r-1)   = k-1   -> slot H
      (col-1, r-1) = k-H-1 -> slot 0
      (col-1, r)   = k-H   -> slot 1
      (col-1, r+1) = k-H+1 -> slot 2
    """
    out = []
    if r > 0:
        out.append(H)      # (col, r-1)
        out.append(0)      # (col-1, r-1)
    out.append(1)          # (col-1, r)
    if r < H - 1:
        out.append(2)      # (col-1, r+1)
    return out


def canon(state):
    """Renumber classes in first-appearance order."""
    mapping, nxt, out = {}, 1, []
    for v in state:
        if v == 0:
            out.append(0)
        else:
            if v not in mapping:
                mapping[v] = nxt
                nxt += 1
            out.append(mapping[v])
    return tuple(out)


def run_dp(H, W, red=False):
    """Return (C1[n] mod M for n=0..H*W, max_states, per_column_walls).

    States keyed by (window tuple, n_so_far); window slides one cell at a
    time.  First column: no previous column; we seed with an all-empty
    window of H+1 zeros and let slots refer to virtual empty cells (correct:
    cells before cell 0 are empty).
    """
    NW = H + 1
    states = {(tuple([0] * NW), 0): (1, 0)}   # (a0, a1); A(q) starts as 1
    max_states = 0
    walls = []
    for col in range(W):
        t0 = time.time()
        for r in range(H):
            nbr = neighbors_in_window(H, r)
            if col == 0:
                nbr = [s for s in nbr if s == H]  # no previous column
            new = defaultdict(lambda: (0, 0))

            def add(key, a0, a1):
                b0, b1 = new[key]
                new[key] = ((b0 + a0) % M, (b1 + a1) % M)

            for (win, n), (a0, a1) in states.items():
                nb_classes = set(win[s] for s in nbr) - {0}
                # empty cell
                add((canon(win[1:] + (0,)), n), a0, a1)
                # occupied cell
                if len(nb_classes) == 0:
                    live = sorted(set(win) - {0})
                    b = len(live)
                    if red:
                        b += 1  # RED control: corrupt the weight
                    # join any live class (color free, may span disconnected
                    # cells), weight 1 each
                    for x in live:
                        add((canon(win[1:] + (x,)), n + 1), a0, a1)
                    # fresh class, weight q - b
                    w2 = canon(win[1:] + (max(win) + 1,))
                    add((w2, n + 1),
                        (-b * a0) % M, (a0 - b * a1) % M)
                elif len(nb_classes) == 1:
                    x = nb_classes.pop()
                    add((canon(win[1:] + (x,)), n + 1), a0, a1)
                # else: clash, weight 0 -> drop
            states = dict(new)
            max_states = max(max_states, len(states))
        walls.append(time.time() - t0)
    c1 = defaultdict(int)
    c0 = defaultdict(int)
    for (win, n), (a0, a1) in states.items():
        c0[n] = (c0[n] + a0) % M
        c1[n] = (c1[n] + a1) % M
    for n in range(1, H * W + 1):
        assert c0[n] == 0, f"[q^0] != 0 at n={n}: {c0[n]}"
    return c1, max_states, walls


def brute(H, W, nmax):
    """Brute-force count of king-connected n-subsets of the H x W box."""
    cells = [(c, r) for c in range(W) for r in range(H)]
    cnt = defaultdict(int)
    for n in range(1, nmax + 1):
        for S in itertools.combinations(cells, n):
            Sset = set(S)
            seen = {S[0]}
            stack = [S[0]]
            while stack:
                (c, r) = stack.pop()
                for dc in (-1, 0, 1):
                    for dr in (-1, 0, 1):
                        p = (c + dc, r + dr)
                        if p in Sset and p not in seen:
                            seen.add(p)
                            stack.append(p)
            if len(seen) == n:
                cnt[n] += 1
    return cnt


def main():
    log = open(sys.argv[0].replace(".py", ".log"), "w")

    def out(s):
        print(s)
        log.write(s + "\n")
        log.flush()

    # 1. correctness vs brute force
    for (H, W, nmax) in [(2, 4, 8), (3, 3, 9), (3, 4, 7), (4, 3, 7)]:
        c1, _, _ = run_dp(H, W)
        bf = brute(H, W, nmax)
        for n in range(1, nmax + 1):
            assert c1[n] == bf[n] % M, (H, W, n, c1[n], bf[n])
        out(f"OK  H={H} W={W}: DP [q^1] == brute-force connected counts, "
            f"n<= {nmax}")

    # 2. RED control: corrupt the fresh-class weight; either the structural
    # [q^0]=0 self-check trips or the counts mismatch brute force
    try:
        c1r, _, _ = run_dp(3, 3, red=True)
        bf = brute(3, 3, 9)
        bad = [n for n in range(1, 10) if c1r[n] != bf[n] % M]
        assert bad, "RED control failed to fail"
        out(f"RED corrupted weight: mismatch vs brute force at n={bad}")
    except AssertionError as e:
        if "failed to fail" in str(e):
            raise
        out(f"RED corrupted weight: caught by structural self-check ({e})")

    # 3. census + timing by H (fixed W, mid-column steady state)
    out("H  W  max_window_states  sec/col(last)  growth")
    prev = None
    for H in range(4, 12):
        W = 8
        t0 = time.time()
        c1, mx, walls = run_dp(H, W)
        g = f"{mx/prev:.3f}" if prev else "-"
        out(f"{H}  {W}  {mx}  {walls[-1]:.3f}  {g}")
        prev = mx
    log.close()


if __name__ == "__main__":
    main()
