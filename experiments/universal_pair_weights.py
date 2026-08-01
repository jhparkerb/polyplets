#!/usr/bin/env python3
"""Pair weights W_pair for row-local lattices: direct count + end-to-end check.

Verifies (2026-07-31, hygiene sweep) the synthetic-lattice numerals of
docs/proofs/universal-diagonal-law.md 'Instances' section. The 2026-07-15
computation capped the pair's column gap at 2 (correct for king, where
max|dx| = 1 makes wider gaps unbridgeable) and silently undercounted every
lattice with max|dx| >= 2 -- interval b >= 4 and D = {-2, 0, 2}.

Two independent computations, no shared model code path:

1. Gadget count: W_pair(D) = #{(pair row placement, q placement)} with the
   walk cell p fixed at the origin of the row below, q free in the row
   above, and the 4-cell set {p, pair, q} connected. Generic D, generous
   window, union-find connectivity -- no gap cap.
2. End-to-end: enumerate the k = 1 diagonal T(n, n-1) directly (animals
   with n cells in exactly n-1 rows; consecutive occupied rows must hold
   an adjacent pair since only |dy| <= 1 edges exist -- a lattice fact,
   not the theorem), fit P_1 from two points, holdout the rest, and check
   [n] P_1 == W_pair(D).

Calibration: king (b=3) must give 25, hex (b=2) 9, square (b=1) 4.
Closed-form candidate for intervals (from the sweep):
   W_pair(b) = b^3 - b(b+1)/2 + 4.

Cost: < 30 s. Usage: python3 experiments/universal_pair_weights.py
"""
from fractions import Fraction as F
from itertools import combinations


def neighbors(cell, D):
    """Adjacency of a row-local lattice: |dx| = 1 within row; dx in D going
    up (and -D going down, symmetric closure)."""
    (x, y) = cell
    out = [(x - 1, y), (x + 1, y)]
    out += [(x + d, y + 1) for d in D]
    out += [(x - d, y - 1) for d in D]
    return out


def connected(cells, D):
    cells = set(cells)
    seen = {next(iter(cells))}
    stack = list(seen)
    while stack:
        c = stack.pop()
        for nb in neighbors(c, D):
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def w_pair(D):
    """Direct gadget count: p = (0,0) fixed; pair {(x1,1),(x2,1)}, x1 < x2;
    q = (xq,2) free. Window generous: 2*max|dx|+3 covers any bridgeable
    span (a connecting path visits each of the 3 rows' cells once)."""
    M = 2 * max(abs(d) for d in D) + 3 if D else 3
    R = range(-M, M + 1)
    total = 0
    for x1, x2 in combinations(R, 2):
        for xq in range(-2 * M, 2 * M + 1):
            cells = [(0, 0), (x1, 1), (x2, 1), (xq, 2)]
            if len(set(cells)) == 4 and connected(cells, D):
                total += 1
    return total


def diagonal_T(n, D):
    """T(n, n-1): n cells, exactly H = n-1 occupied rows (one pair row),
    counted up to translation (row 0 leftmost cell pinned at x = 0 via
    canonical shift). Direct DFS over row contents; consecutive rows must
    contain an adjacent cross-row pair (only |dy| <= 1 edges exist), which
    bounds the search window; full connectivity checked at the end."""
    H = n - 1
    maxd = max(abs(d) for d in D)
    # a gapped pair can be bridged only by a single cell adjacent to BOTH
    # its cells (above or below), so pair span <= 2*maxd and the far cell
    # sits at most 3*maxd + 1 from the previous row; generous window:
    span = 3 * maxd + 2
    counts = 0
    results = []

    def rows_link(rowA, rowB):
        """rowB sits directly above rowA: linked iff some (bx - ax) in D.
        Necessary between every consecutive occupied row pair, since only
        |dy| <= 1 edges exist; sufficiency of the whole is checked by the
        final union-find."""
        return any((bx - ax) in D for ax in rowA for bx in rowB)

    def rec(r, rows, pair_used):
        if r == H:
            if not pair_used:
                return
            cells = [(x, i) for i, row in enumerate(rows) for x in row]
            if connected(cells, D):
                results.append(1)
            return
        prev = rows[-1]
        lo = min(prev) - span
        hi = max(prev) + span
        for x in range(lo, hi + 1):
            if rows_link(prev, [x]):
                rec(r + 1, rows + [[x]], pair_used)
        if not pair_used:
            for x1 in range(lo, hi + 1):
                for x2 in range(x1 + 1, hi + span + 1):
                    if rows_link(prev, [x1, x2]):
                        rec(r + 1, rows + [[x1, x2]], True)
        return

    # row 0: canonical single cell at 0, or the pair row (canonical x1 = 0)
    rec(1, [[0]], False)
    for width in range(1, 2 * maxd + 3):
        rec(1, [[0, width]], True)
    return len(results)


def main():
    cases = [
        ("square b=1", (0,)),
        ("hex b=2", (-1, 0)),
        ("king b=3", (-1, 0, 1)),
        ("interval b=4", (-1, 0, 1, 2)),
        ("interval b=5", (-2, -1, 0, 1, 2)),
        ("D={-2,0,2}", (-2, 0, 2)),
    ]
    doc_claim = {"interval b=4": 45, "interval b=5": 69, "D={-2,0,2}": 48}
    print("== 0. closed form on wider intervals (gadget only) ==")
    for b in (6, 7, 8):
        D = tuple(range(-(b // 2), b - b // 2))
        w = w_pair(D)
        cf = b**3 - b * (b + 1) // 2 + 4
        assert w == cf, (b, w, cf)
        print(f"  interval b={b}: W_pair = {w} == b^3 - b(b+1)/2 + 4  ok")

    print("\n== 1. gadget counts (no gap cap) vs doc numerals ==")
    W = {}
    for name, D in cases:
        w = w_pair(D)
        W[name] = w
        b = len(D)
        interval = max(D) - min(D) + 1 == b
        cf = b**3 - b * (b + 1) // 2 + 4 if interval else None
        note = ""
        if name in doc_claim:
            note = f"  doc said {doc_claim[name]}" + \
                   ("  <-- UNDERCOUNT CONFIRMED" if doc_claim[name] != w
                    else "  (doc correct)")
        cftag = f"  closed form {cf} {'ok' if cf == w else '*** MISMATCH ***'}" \
            if cf is not None else ""
        print(f"  {name:14s} W_pair = {w}{cftag}{note}")

    print("\n== 2. end-to-end: k=1 diagonal, fit + holdouts ==")
    for name, D in cases:
        b = len(D)
        vals = {}
        nmax = 8 if b <= 4 else 7
        for n in range(3, nmax + 1):
            vals[n] = diagonal_T(n, D)
        # P_1(n) = T(n,n-1) * b^(4-n) must be linear in n (law with k=1)
        P = {n: F(v) * F(b) ** (4 - n) for n, v in vals.items()}
        slope = P[4] - P[3]
        icept = P[3] - 3 * slope
        holds = all(P[n] == slope * n + icept for n in range(5, nmax + 1))
        lead_ok = slope == W[name]
        print(f"  {name:14s} P_1(n) = {slope}n {'+' if icept >= 0 else '-'} "
              f"{abs(icept)}  holdouts n<=%d: %s  [n]P_1 == W_pair: %s"
              % (nmax, "PASS" if holds else "FAIL",
                 "PASS" if lead_ok else "*** FAIL ***"))
        assert holds and lead_ok, name

    print("\n== 3. mod-p verdicts for Theorem B ==")
    for name, D in cases:
        b = len(D)
        for p in (2, 3, 5, 7):
            if b % p == 0:
                print(f"  {name:14s} p={p}: w = W_pair mod p = {W[name] % p}"
                      + ("  (degenerate branch)" if W[name] % p == 0 else
                         "  (unit)"))


if __name__ == "__main__":
    main()
