#!/usr/bin/env python3
"""Polyiamonds as a fibred row-local lattice -- the hypotheses of Theorem A.

docs/proofs/universal-diagonal-law.md states Theorem A for lattices whose
minimal interior rows are single cuts with b upward continuations. Polyiamonds
do not have single-cell interior rows, so the theorem has to be read with the
RHOMBUS as the row unit: a receiver (even x + y, the only cell that can take an
edge from below) glued to a horizontally adjacent sender (odd x + y, the only
cell that can pass one up). This script checks, fail-closed, every hypothesis
that reading needs, plus the conclusion against the banked polynomials of
results/diagonal-formula.md.

  [1] brute enumeration reproduces A001420 (fixed polyiamonds, n >= 2);
  [2] the change of variables (x, y) -> (j, y, type) with j = (x - y) // 2 is
      an isomorphism onto the honeycomb graph carrying its translation group,
      height for height: an independent honeycomb enumerator returns the same
      T(n, H) table cell for cell;
  [3] hypothesis (M): every interior row has at least two cells; every 2-cell
      interior row is a rhombus with exactly one cell able to receive from
      below and exactly one able to send above, both of which do; and the
      drift step out of a fixed entry cell -- a minimal row plus the single
      edge up out of its exit -- has exactly b = 2 outcomes, whose j-offsets
      are D = {0, -1}, the polyhex drift set;
  [4] the conclusion T(2H-2+k, H) = q_k(H) 2^H against brute force, over the
      theorem's range H >= k+1 and the earlier measured onsets, with two RED
      controls: a degree-(k-1) fit must miss, and each q_k must FAIL one step
      below its measured onset.

Usage: python3 -m experiments.polyiamond_fibre_check
"""
import os
import sys
from collections import defaultdict
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from polyiamond_diagonal import nbr, interpolate, ev                # noqa: E402

NMAX = 14
A001420 = [3, 6, 14, 36, 94, 250, 675, 1838, 5053, 14016,
           39169, 110194, 311751]                      # A001420, n = 2..14

# results/diagonal-formula.md, high coefficient first, in H.
BANKED = {
    0: ([F(1, 4)], 2),
    1: ([F(1, 2), F(0)], 2),
    2: ([F(1, 2), F(11, 16), F(-13, 16)], 3),
    3: ([F(1, 3), F(11, 8), F(-29, 24), F(0)], 3),
    4: ([F(1, 6), F(11, 8), F(59, 384), F(-137, 128), F(-65, 32)], 4),
}




def canon_tri(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    dx = mx - ((mx + my) % 2)          # keep x + y parity: dx + my is even
    return frozenset((x - dx, y - my) for x, y in cells)


def hnbr(c):
    """Honeycomb: R_j ~ S_j, R_j ~ S_{j-1} in a row; S_j ~ R_j one row up."""
    j, y, t = c
    if t == 0:
        return [(j, y, 1), (j - 1, y, 1), (j, y - 1, 1)]
    return [(j, y, 0), (j + 1, y, 0), (j, y + 1, 0)]


def canon_hex(cells):
    mj = min(j for j, _, _ in cells)
    my = min(y for _, y, _ in cells)
    return frozenset((j - mj, y - my, t) for j, y, t in cells)


def grow(seeds, neighbors, canon, nmax):
    """All animals up to nmax cells, keyed by canonical form."""
    seen = {canon({s}) for s in seeds}
    frontier = list(seen)
    byn = defaultdict(list)
    for a in frontier:
        byn[1].append(a)
    while frontier:
        nxt = []
        for a in frontier:
            if len(a) >= nmax:
                continue
            for c in a:
                for b in neighbors(c):
                    if b in a:
                        continue
                    q = canon(a | {b})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.append(q)
                    byn[len(q)].append(q)
        frontier = nxt
    return byn


def table(byn):
    T = defaultdict(int)
    for n, animals in byn.items():
        for a in animals:
            ys = [c[1] for c in a]
            T[(n, max(ys) - min(ys) + 1)] += 1
    return T


def to_hex(c):
    """The change of variables. Receiver (x+y even) -> R_{(x-y)/2}, sender
    (x+y odd) -> S_{(x-y-1)/2}."""
    x, y = c
    return (((x - y) // 2, y, 0) if (x + y) % 2 == 0
            else ((x - y - 1) // 2, y, 1))


def minimal_rows(x, y, span=4):
    """Every 2-cell row containing (x, y) as its only receiver-capable cell
    and holding exactly one sender-capable cell, searched in a window."""
    out = []
    for other in range(x - span, x + span + 1):
        if other == x:
            continue
        row = sorted([x, other])
        recv = [c for c in row if (c + y) % 2 == 0]
        send = [c for c in row if (c + y) % 2 == 1]
        if recv == [x] and len(send) == 1 and row[1] - row[0] == 1:
            out.append((tuple(row), send[0]))
    return out






def main():
    fails = []

    print(f"[1] brute polyiamonds to n = {NMAX} against A001420")
    tri = grow([(0, 0), (1, 0)], nbr, canon_tri, NMAX)
    got = [len(tri[n]) for n in range(2, NMAX + 1)]
    if got != A001420[:NMAX - 1]:
        fails.append(f"A001420 mismatch: {got} vs {A001420[:NMAX - 1]}")
    if len(tri[1]) != 2:
        fails.append(f"n=1 classes {len(tri[1])}, want 2 (up and down)")
    print(f"    n = 2..{NMAX}: {got}  OK" if not fails else f"    FAIL {fails}")

    print("\n[2] change of variables: polyiamonds == honeycomb site animals")
    hexa = grow([(0, 0, 0), (0, 0, 1)], hnbr, canon_hex, NMAX)
    for c in [(x, y) for x in range(-3, 4) for y in range(-3, 4)]:
        want = {to_hex(d) for d in nbr(c)}
        if want != set(hnbr(to_hex(c))):
            fails.append(f"adjacency not carried at {c}")
            break
    Ttri = table(tri)
    Thex = table(hexa)
    if Ttri != Thex:
        diff = [k for k in set(Ttri) | set(Thex)
                if Ttri.get(k, 0) != Thex.get(k, 0)]
        fails.append(f"T tables differ at {sorted(diff)[:6]}")
    else:
        print(f"    adjacency carried; T(n, H) equal on all "
              f"{len(Ttri)} cells with n <= {NMAX}  OK")

    print("\n[3] hypothesis (M): minimal interior rows are rhombi, b = 2")
    checked = 0
    for n in tri:
        for a in tri[n]:
            ys = [y for _, y in a]
            lo, hi = min(ys), max(ys)
            for y in range(lo + 1, hi):
                row = sorted(x for x, yy in a if yy == y)
                if len(row) < 2:
                    fails.append(f"interior row of {len(row)} cell(s): "
                                 f"{sorted(a)}")
                    break
                if len(row) > 2:
                    continue
                recv = [x for x in row if (x + y) % 2 == 0]
                send = [x for x in row if (x + y) % 2 == 1]
                if (row[1] - row[0] != 1 or len(recv) != 1 or len(send) != 1
                        or (recv[0], y - 1) not in a
                        or (send[0], y + 1) not in a):
                    fails.append(f"2-cell interior row not a used rhombus: "
                                 f"{sorted(a)} at y={y}")
                    break
                checked += 1
    print(f"    every interior row has >= 2 cells; {checked} two-cell interior "
          f"rows, all rhombi with one used port each  OK")
    drift = set()
    for y in (0, 1):
        for x in range(-4, 5):
            if (x + y) % 2:
                continue
            rows = minimal_rows(x, y)
            if len(rows) != 2:
                fails.append(f"drift count {len(rows)} != 2 at ({x}, {y})")
            for _, s in rows:
                drift.add(to_hex((s, y + 1))[0] - to_hex((x, y))[0])
    if drift != {0, -1}:
        fails.append(f"drift offsets {sorted(drift)} != {{0, -1}}")
    else:
        print("    drift step out of any entry cell: b = 2, offsets D = "
              "{0, -1} in j -- the polyhex drift set  OK")
    for H in range(2, 8):
        want, got_ = 2 ** (H - 2), Ttri.get((2 * H - 2, H), 0)
        if want != got_:
            fails.append(f"T({2*H-2}, {H}) = {got_}, want 2^{H-2} = {want}")
    print(f"    n_min(H) = 2H-2 and T(2H-2, H) = 2^(H-2) to H = 7  OK")

    print("\n[4] T(2H-2+k, H) = q_k(H) 2^H against brute force")
    for k, (q, onset) in sorted(BANKED.items()):
        pts = [(H, F(Ttri[(2 * H - 2 + k, H)], 2 ** H))
               for H in range(2, NMAX)
               if 2 * H - 2 + k <= NMAX and (2 * H - 2 + k, H) in Ttri]
        good = [(H, v) for H, v in pts if H >= onset]
        if len(good) < 2:
            fails.append(f"k={k}: only {len(good)} points at or past onset")
            continue
        bad = [(H, v, ev(q, H)) for H, v in good if ev(q, H) != v]
        if bad:
            fails.append(f"k={k}: banked q_k misses at {bad[:3]}")
            continue
        thm = [H for H, _ in good if H >= k + 1]
        below = [(H, v) for H, v in pts if H < onset]
        red_onset = "n/a"
        if below:
            H, v = below[-1]
            if ev(q, H) == v:
                fails.append(f"k={k}: RED onset control passed at H={H}")
            red_onset = f"fails at H={H} ({ev(q,H)} vs {v})"
        red_deg = "no degree control (needs %d values, has %d)" % (
            k + 1, len(good))
        if k >= 1 and len(good) >= k + 1:
            low = interpolate(good[:k])
            if all(ev(low, H) == v for H, v in good[:k + 1]):
                fails.append(f"k={k}: RED degree control passed "
                             f"(degree {k-1} fit reproduces {k+1} points)")
            red_deg = "degree-%d fit misses" % (k - 1)
        print(f"    k={k}: {len(good)} values H={good[0][0]}..{good[-1][0]}, "
              f"all match; theorem range H>={k+1} covered by "
              f"{len(thm)}; RED {red_onset}; {red_deg}")

    if fails:
        print("\nFAIL")
        for f_ in fails:
            print("   ", f_)
        return 1
    print("\nAll checks passed: polyiamonds satisfy (M) with b = 2, and the "
          "\nconclusion holds over the theorem's range and earlier.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
