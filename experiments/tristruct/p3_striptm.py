"""p3_striptm.py -- Proposer 3's own strip transfer matrix for king animals,
built from the lattice definition only (no repo kernel consulted, no banked
data consumed).

Object: S_H(n) = number of fixed king animals with n cells whose bounding box
has height <= H, counted once per vertical placement inside the height-H strip
(an animal of height h contributes H-h+1). Then

    T(n,H) = S_H(n) - 2*S_{H-1}(n) + S_{H-2}(n),   S_0 = S_{-1} = 0.

Method: column-by-column DP. An animal occupies a contiguous run of columns
(a wholly empty column would disconnect it, since king adjacency has |dx|<=1),
each column a nonempty subset of the H rows. State after a column =
(occupancy mask, partition of occupied cells into connectivity classes).
Transition to next mask: vertical runs of the new mask are internally
connected; a run joins an old class when some cell of the run is within
|dy| <= 1 of an occupied old cell (king adjacency across adjacent columns).
An old class touching no new cell dies => transition invalid (the animal
would disconnect). An animal is complete at any column where the state has
exactly one class.

Counting by n uses bignum limb packing: the count polynomial in x (x tracks
cells) is stored as one Python int with LIMB-bit limbs, so a transition is a
single shift-and-add. Counts stay far below 2^LIMB (checked).

Output: p3_striptm_out.txt with lines "n H T(n,H)" for H = 1..HMAX,
n = 1..NMAX, and a state-count table on stdout. Cross-checked against
p3_enum_out.txt (independent Redelmeier enumeration) for n <= 12.

Run from experiments/tristruct/:  python3 p3_striptm.py
"""

import os
import sys

HMAX = 6
NMAX = 110
LIMB = 512


def vruns(mask):
    """Maximal runs of consecutive set bits, as tuples of bit positions."""
    out, cur = [], []
    b = 0
    while mask >> b:
        if (mask >> b) & 1:
            cur.append(b)
        elif cur:
            out.append(tuple(cur))
            cur = []
        b += 1
    if cur:
        out.append(tuple(cur))
    return out


def canon(cells, cls):
    """Canonical partition label tuple for sorted cells, first-occurrence ids."""
    seen = {}
    out = []
    for c in cells:
        r = cls[c]
        if r not in seen:
            seen[r] = len(seen)
        out.append(seen[r])
    return tuple(out)


def build_states(H):
    """BFS the reachable (mask, partition) states; return states, edges, starts.

    edges[i] = list of (j, popcount_of_new_mask); starts = {state_id: popcount};
    accept[i] = True iff the partition has exactly one class.
    """
    masks = list(range(1, 1 << H))
    states = {}
    edges = []
    accept = []

    def sid(mask, part):
        key = (mask, part)
        if key not in states:
            states[key] = len(edges)
            edges.append(None)
            accept.append(max(part) == 0)
        return states[key]

    starts = {}
    todo = []
    for m in masks:
        rs = vruns(m)
        cells = [b for b in range(H) if (m >> b) & 1]
        cls = {}
        for i, r in enumerate(rs):
            for c in r:
                cls[c] = i
        i = sid(m, canon(cells, cls))
        if i not in starts:
            starts[i] = bin(m).count("1")
            todo.append(i)
    inv = {v: k for k, v in states.items()}
    qi = 0
    while qi < len(todo):
        i = todo[qi]
        qi += 1
        if edges[i] is not None:
            continue
        mask, part = inv[i]
        cells = [b for b in range(H) if (mask >> b) & 1]
        ncls = max(part) + 1
        out = []
        for m2 in masks:
            rs = vruns(m2)
            # union-find over old classes [0..ncls) + new runs [ncls..)
            parent = list(range(ncls + len(rs)))

            def find(a):
                while parent[a] != a:
                    parent[a] = parent[parent[a]]
                    a = parent[a]
                return a

            touched = [False] * ncls
            for ri, r in enumerate(rs):
                for c in r:
                    for dy in (-1, 0, 1):
                        c2 = c + dy
                        if 0 <= c2 < H and (mask >> c2) & 1:
                            oc = part[cells.index(c2)]
                            touched[oc] = True
                            ra, rb = find(ncls + ri), find(oc)
                            if ra != rb:
                                parent[ra] = rb
            if not all(touched):
                continue  # an old component would die: disconnection
            cells2 = [b for b in range(H) if (m2 >> b) & 1]
            cls2 = {}
            for ri, r in enumerate(rs):
                root = find(ncls + ri)
                for c in r:
                    cls2[c] = root
            j = sid(m2, canon(cells2, cls2))
            if j >= len(todo) or (j not in starts and edges[j] is None
                                  and j not in todo[qi:]):
                pass
            out.append((j, bin(m2).count("1")))
            if edges[j] is None and j not in todo:
                todo.append(j)
        edges[i] = out
        inv = {v: k for k, v in states.items()}
    # any state never expanded (unreachable as source) gets empty edges
    for i, e in enumerate(edges):
        if e is None:
            edges[i] = []
    return states, edges, starts, accept


def strip_series(H, nmax):
    """S_H(n) for n = 0..nmax, exact ints."""
    states, edges, starts, accept = build_states(H)
    nstates = len(edges)
    trunc = 1 << (LIMB * (nmax + 1))
    dp = [0] * nstates
    for i, pc in starts.items():
        dp[i] += 1 << (LIMB * pc)
    total = 0
    for _col in range(nmax):
        for i in range(nstates):
            if accept[i]:
                total = (total + dp[i]) % trunc
        ndp = [0] * nstates
        for i in range(nstates):
            v = dp[i]
            if not v:
                continue
            for j, pc in edges[i]:
                ndp[j] = (ndp[j] + (v << (LIMB * pc))) % trunc
        dp = ndp
    for i in range(nstates):
        if accept[i]:
            total = (total + dp[i]) % trunc
    out = []
    lm = (1 << LIMB) - 1
    for n in range(nmax + 1):
        v = (total >> (LIMB * n)) & lm
        assert v < (1 << (LIMB - 8)), "limb overflow risk at n=%d" % n
        out.append(v)
    return out, nstates


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    series = {0: [0] * (NMAX + 1), -1: [0] * (NMAX + 1)}
    print("H  #states")
    for H in range(1, HMAX + 1):
        series[H], ns = strip_series(H, NMAX)
        print("%d  %d" % (H, ns))
        sys.stdout.flush()
    T = {}
    for H in range(1, HMAX + 1):
        for n in range(1, NMAX + 1):
            T[(n, H)] = (series[H][n] - 2 * series[H - 1][n]
                         + series[H - 2][n])
            assert T[(n, H)] >= 0
    # cross-check against the independent Redelmeier enumeration, n <= 12
    mine = {}
    with open(os.path.join(here, "p3_enum_out.txt")) as f:
        for line in f:
            n, h, v = line.split()
            mine[(int(n), int(h))] = int(v)
    bad = 0
    for (n, h), v in mine.items():
        if h <= HMAX and T[(n, h)] != v:
            print("TM vs enum MISMATCH n=%d H=%d tm=%d enum=%d"
                  % (n, h, T[(n, h)], v))
            bad += 1
    nchk = sum(1 for (n, h) in mine if h <= HMAX)
    print("TM vs enum: %d cells compared (n<=12, H<=%d), %d mismatches"
          % (nchk, HMAX, bad))
    with open(os.path.join(here, "p3_striptm_out.txt"), "w") as f:
        for H in range(1, HMAX + 1):
            for n in range(1, NMAX + 1):
                f.write("%d %d %d\n" % (n, H, T[(n, H)]))
    print("wrote p3_striptm_out.txt (H<=%d, n<=%d)" % (HMAX, NMAX))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
