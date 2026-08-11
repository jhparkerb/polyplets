"""Column transfer-matrix for fixed animals by exact bounding-box height,
on the SQUARE lattice and the TRIANGULAR lattice (polyiamonds), written for
the cross-lattice control role of docs/triangle-structure-team-brief.md.

Independent of every kernel in this repo (reads none of core/, cpp/,
orchestrator/); the only inputs are the lattice definitions, matching
xlat_enum.cpp:

  square : cells Z^2, u ~ v iff |dx|+|dy| = 1
  tri    : (x,y) ~ (x+-1,y) always; (x,y) ~ (x,y+1) iff x+y+p odd, p in {0,1}
           the parity offset; fixed polyiamonds are counted modulo
           translations with dx+dy even, so totals sum over p = 0 and p = 1.

Method: sweep columns x = 0,1,2,... of a strip of height <= H (rows
y = 0..H-1).  A connected animal occupies a contiguous run of columns, so
anchor the leftmost occupied column at x = 0.  DP state after a column:
(mask of occupied cells in that column, set-partition of the mask into
components of the animal-so-far).  A transition to a nonempty next-column
mask is valid iff every current component touches the new column (a
component that loses frontier contact can never reconnect); an animal may
terminate at any column whose state has exactly one component.  Exact
integer arithmetic throughout.

C_H(n) = # animals with n cells fitting in height <= H, each counted once
per vertical placement, i.e. C_H = sum_{h<=H} (H-h+1) T(n,h).  Hence the
second difference  T(n,H) = C_H(n) - 2 C_{H-1}(n) + C_{H-2}(n).

Self-check (run as a script): every T(n,H) cell with H <= HMAX must equal
the independent Redelmeier enumerator's output in data/square_enum_n14.txt
and data/tri_enum_n16.txt (written by build/xlat_enum, a different
algorithm by the same author).  Output: data/square_col_tm_n60.txt and
data/tri_col_tm_n60.txt, lines "n H T(n,H)" for H <= HMAX.

Usage: python3 xlat_striptm.py   (from experiments/tristruct/, ~seconds)
"""

import os
import sys
from itertools import combinations

HMAX = 5          # emit exact-height columns H = 1..HMAX (needs C_1..C_5)
NMAX = 140


def canon_partition(blocks):
    """Canonical form of a set partition: sorted tuple of sorted tuples."""
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def components(cells, edges):
    """Connected components of `cells` under the edge set `edges`."""
    parent = {c: c for c in cells}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in edges:
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    out = {}
    for c in cells:
        out.setdefault(find(c), []).append(c)
    return canon_partition(out.values())


def intra_edges(lattice, H, xparity, p):
    """Vertical edges inside one column at x with x mod 2 == xparity."""
    if lattice == 'square':
        return [(y, y + 1) for y in range(H - 1)]
    # tri: (x,y) ~ (x,y+1) iff x+y+p odd
    return [(y, y + 1) for y in range(H - 1) if (xparity + y + p) & 1]


def strip_counts(lattice, H, nmax, p=0):
    """C_H(n) for n = 1..nmax on the given lattice (parity offset p for tri).

    Returns a list c with c[n] = C_H(n).  Inter-column adjacency is
    horizontal only for both lattices ((x,y) ~ (x+1,y)); all vertical
    adjacency is intra-column (for tri, on the parity rule).
    """
    masks = [tuple(sorted(s)) for k in range(1, H + 1)
             for s in combinations(range(H), k)]
    out = [0] * (nmax + 1)
    # dp: {(mask, partition): [count by n]}  after the current column
    dp = {}
    x = 0
    for m in masks:
        if len(m) > nmax:
            continue
        part = components(m, intra_edges(lattice, H, x % 2, p))
        key = (m, part)
        vec = dp.setdefault(key, [0] * (nmax + 1))
        vec[len(m)] += 1
    while dp:
        # terminate: single-component states are complete animals
        for (m, part), vec in dp.items():
            if len(part) == 1:
                for n in range(1, nmax + 1):
                    out[n] += vec[n]
        x += 1
        ndp = {}
        ie = intra_edges(lattice, H, x % 2, p)
        for (m, part), vec in dp.items():
            minn = next((n for n in range(nmax + 1) if vec[n]), None)
            if minn is None:
                continue
            for m2 in masks:
                if minn + len(m2) > nmax:
                    continue
                # inter-column adjacency is horizontal only: y ~ y.  Every
                # old component must touch the new column or it is orphaned.
                if any(not any(y in m2 for y in blk) for blk in part):
                    continue
                cells2 = list(m2)
                edges = [e for e in ie if e[0] in m2 and e[1] in m2]
                # union-find over new cells seeded by old-block links
                parent = {c: c for c in cells2}

                def find(a):
                    while parent[a] != a:
                        parent[a] = parent[parent[a]]
                        a = parent[a]
                    return a

                for a, b in edges:
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        parent[ra] = rb
                # old blocks: link all their cross cells together
                for blk in part:
                    touch = [y for y in blk if y in m2]
                    for y in touch[1:]:
                        ra, rb = find(touch[0]), find(y)
                        if ra != rb:
                            parent[ra] = rb
                blocks = {}
                for c in cells2:
                    blocks.setdefault(find(c), []).append(c)
                part2 = canon_partition(blocks.values())
                key = (m2, part2)
                nvec = ndp.setdefault(key, [0] * (nmax + 1))
                add = len(m2)
                for n in range(minn, nmax + 1 - add):
                    if vec[n]:
                        nvec[n + add] += vec[n]
        dp = ndp
    return out


def exact_height_columns(lattice, nmax, hmax):
    """{(n,H): T(n,H)} for H = 1..hmax via second differences of C_H."""
    ps = (0, 1) if lattice == 'tri' else (0,)
    C = {}
    for H in range(0, hmax + 1):
        if H == 0:
            C[0] = [0] * (nmax + 1)
        else:
            tot = [0] * (nmax + 1)
            for p in ps:
                c = strip_counts(lattice, H, nmax, p)
                for n in range(nmax + 1):
                    tot[n] += c[n]
            C[H] = tot
    T = {}
    for H in range(1, hmax + 1):
        lo = C[H - 2] if H >= 2 else [0] * (nmax + 1)
        for n in range(1, nmax + 1):
            v = C[H][n] - 2 * C[H - 1][n] + lo[n]
            if v:
                T[(n, H)] = v
    return T


def load_enum(path):
    """Parse 'n H count' lines from an xlat_enum output file."""
    cells = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 3 and parts[1] != 'SUM':
                cells[(int(parts[0]), int(parts[1]))] = int(parts[2])
    return cells


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    checks = {'square': 'data/square_enum_n14.txt',
              'tri': 'data/tri_enum_n16.txt'}
    for lattice, checkfile in checks.items():
        T = exact_height_columns(lattice, NMAX, HMAX)
        ref = load_enum(os.path.join(here, checkfile))
        bad = 0
        ncheck = 0
        for (n, H), v in ref.items():
            if H > HMAX:
                continue
            ncheck += 1
            if T.get((n, H), 0) != v:
                bad += 1
                print(f"MISMATCH {lattice} n={n} H={H}: "
                      f"tm={T.get((n, H), 0)} enum={v}")
        status = 'OK' if bad == 0 else f'{bad} MISMATCHES'
        print(f"{lattice}: {ncheck} cells (H<={HMAX}) vs {checkfile}: {status}")
        if bad:
            sys.exit(1)
        out = os.path.join(here, f'data/{lattice}_col_tm_n{NMAX}.txt')
        with open(out, 'w') as f:
            for (n, H) in sorted(T):
                f.write(f"{n} {H} {T[(n, H)]}\n")
        print(f"wrote {out}")


if __name__ == '__main__':
    main()
