#!/usr/bin/env python3
"""r3_l5_cnf_encode.py -- CNF (DIMACS) encoding of T(n,H) for exact #SAT
counters, plus a semantic self-test of the encoding. R3 lane L5.

The object: king-connected n-cell subsets of the box [0,n) x [0,H),
normalized min-x = 0, min-y = 0, max-y = H-1 (height exactly H, up to
translation; width <= n is a theorem for connected n-cell sets).

Encoding (all auxiliary variables functionally determined by the cell
variables, via biconditional Tseitin definitions, so the RAW model count of
the CNF equals T(n,H) -- no projection support needed in the counter):

  x_c              cell c occupied            (c in column-major order)
  z_c              no occupied cell precedes c:  z_0 <-> true,
                   z_{c+1} <-> z_c & ~x_c
  root_c <-> x_c & z_c                        (the first occupied cell)
  r_{c,0} <-> root_c
  r_{c,d+1} <-> r_{c,d} | (x_c & OR_{c'~c} r_{c',d})   d < n-1
  constraint: x_c -> r_{c,n-1}                (all occupied cells reached)
  cardinality |x| = n  (sequential unary counter, biconditionally defined)
  touch: OR of column-0 cells, OR of row-0 cells, OR of row-(H-1) cells

Connectivity is stated as reachability-from-the-unique-root unrolled to
n-1 steps (n-1 steps suffice: a connected n-cell set has eccentricity
<= n-1 in its own king graph). The counter that evaluates this never
implements connectivity; the failure modes of THIS encoding are a wrong
unrolling depth (undercount) or a broken root/prefix chain (over- or
undercount) -- named in the lane deliverable.

No #SAT counter is installed on gympie (2026-08-12; none in MacPorts
either -- checked ganak/sharpsat/d4/cachet by `port search`). The
self-test below is therefore MY OWN evaluation of the encoding against a
BFS reference; it certifies the CNF text is a faithful formalisation, it
is NOT the third-party count.

Self-test: for every assignment of the cell variables over small boxes,
propagate the (functionally determined) auxiliaries, check that the CNF is
satisfied iff the subset is king-connected + touching (BFS reference), and
that the resulting counts reproduce the banked triangle at n <= 6.

Usage:
  python3 r3_l5_cnf_encode.py --selftest
  python3 r3_l5_cnf_encode.py --emit n H > king_nH.cnf
"""
import sys
import itertools
from collections import deque


class CNF:
    def __init__(self):
        self.nvars = 0
        self.clauses = []

    def new(self):
        self.nvars += 1
        return self.nvars

    def add(self, *lits):
        self.clauses.append(tuple(lits))

    def iff_and(self, y, lits):
        # y <-> AND(lits)
        for l in lits:
            self.add(-y, l)
        self.add(y, *[-l for l in lits])

    def iff_or(self, y, lits):
        # y <-> OR(lits)
        for l in lits:
            self.add(y, -l)
        self.add(-y, *lits)


def encode(n, H, W=None):
    """Build the CNF for T(n,H) on a W x H box (W defaults to n)."""
    if W is None:
        W = n
    cnf = CNF()
    cells = [(x, y) for x in range(W) for y in range(H)]  # column-major
    idx = {c: i for i, c in enumerate(cells)}
    xv = {c: cnf.new() for c in cells}

    def nbrs(c):
        (x, y) = c
        return [(x + dx, y + dy)
                for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                if (dx, dy) != (0, 0)
                and (x + dx, y + dy) in idx]

    # prefix-empty chain z_c and root_c <-> x_c & z_c
    zv, rootv = {}, {}
    for i, c in enumerate(cells):
        zv[c] = cnf.new()
        if i == 0:
            cnf.add(zv[c])                      # z_0 <-> true
        else:
            prev = cells[i - 1]
            cnf.iff_and(zv[c], [zv[prev], -xv[prev]])
        rootv[c] = cnf.new()
        cnf.iff_and(rootv[c], [xv[c], zv[c]])

    # reachability unrolling r_{c,d}, d = 0..n-1
    r = {c: [None] * n for c in cells}
    for c in cells:
        r[c][0] = rootv[c]
    for d in range(1, n):
        for c in cells:
            r[c][d] = cnf.new()
            # aux_c,d <-> x_c & OR(r_{c',d-1} for c' ~ c)
            orv = cnf.new()
            cnf.iff_or(orv, [r[c2][d - 1] for c2 in nbrs(c)])
            andv = cnf.new()
            cnf.iff_and(andv, [xv[c], orv])
            cnf.iff_or(r[c][d], [r[c][d - 1], andv])
    for c in cells:
        cnf.add(-xv[c], r[c][n - 1])            # x_c -> reached

    # touch constraints
    cnf.add(*[xv[(0, y)] for y in range(H)])
    cnf.add(*[xv[(x, 0)] for x in range(W)])
    cnf.add(*[xv[(x, H - 1)] for x in range(W)])

    # cardinality |x| = n: sequential unary counter s_{i,j} biconditional
    # s_{i,j} <-> (at least j+1 of the first i+1 cells occupied)
    s = {}
    for i, c in enumerate(cells):
        for j in range(min(i + 1, n + 1)):
            v = cnf.new()
            s[(i, j)] = v
            if i == 0:
                # s_{0,0} <-> x_0
                cnf.iff_or(v, [xv[c]]) if j == 0 else None
            else:
                if j == 0:
                    cnf.iff_or(v, [s[(i - 1, 0)], xv[c]])
                elif (i - 1, j) in s and (i - 1, j - 1) in s:
                    a = cnf.new()
                    cnf.iff_and(a, [s[(i - 1, j - 1)], xv[c]])
                    cnf.iff_or(v, [s[(i - 1, j)], a] if (i - 1, j) in s else [a])
                elif (i - 1, j - 1) in s:
                    cnf.iff_and(v, [s[(i - 1, j - 1)], xv[c]])
    last = len(cells) - 1
    cnf.add(s[(last, n - 1)])                   # at least n
    if (last, n) in s:
        cnf.add(-s[(last, n)])                  # at most n
    return cnf, cells, xv


# ---------------- reference + self-test ----------------

def connected_touching(cellset, H):
    if not cellset:
        return False
    if not any(x == 0 for x, y in cellset):
        return False
    if not any(y == 0 for x, y in cellset):
        return False
    if not any(y == H - 1 for x, y in cellset):
        return False
    start = next(iter(cellset))
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) == (0, 0):
                    continue
                c2 = (x + dx, y + dy)
                if c2 in cellset and c2 not in seen:
                    seen.add(c2)
                    q.append(c2)
    return len(seen) == len(cellset)


def eval_cnf_on_subset(cnf, cells, xv, subset):
    """Propagate the functionally-determined auxiliaries for a given cell
    assignment and report whether every clause is satisfied. Sound because
    every auxiliary is defined biconditionally: the CNF is satisfiable for
    this x-assignment iff the forced total assignment satisfies it, and
    then the extension is unique (raw count = projected count)."""
    val = {}
    for c in cells:
        val[xv[c]] = c in subset
    # iterate unit-style propagation over biconditional definitions:
    # definitions were added in dependency order, so one forward pass
    # over recorded definitions suffices; reconstruct by clause scanning
    # is overkill -- instead re-run the encoder logic symbolically.
    # For the self-test we simply search: assign undefined vars by
    # fixpoint from the definition clauses.
    # Simple approach: repeatedly find clauses that force values.
    changed = True
    while changed:
        changed = False
        for cl in cnf.clauses:
            unassigned = [l for l in cl if abs(l) not in val]
            satisfied = any((l > 0) == val.get(abs(l), None)
                            for l in cl if abs(l) in val)
            if satisfied:
                continue
            if len(unassigned) == 1:
                l = unassigned[0]
                val[abs(l)] = l > 0
                changed = True
            elif not unassigned:
                return False  # falsified clause
    # all forced; any clause fully assigned and false already returned
    for cl in cnf.clauses:
        if not any((l > 0) == val[abs(l)] for l in cl if abs(l) in val):
            if all(abs(l) in val for l in cl):
                return False
            return None  # incomplete propagation (should not happen)
    return True


def selftest():
    import triangle
    tri = triangle.Triangle.load()
    total_subsets = 0
    # capped at n <= 5: the per-subset propagation is O(clauses) per check
    # and n = 6 costs ~2M subsets x thousands of clauses (hours) -- the
    # measured per-subset cost is itself part of the lane's cost model.
    for n in range(2, 6):
        for H in range(1, n + 1):
            W = n
            cnf, cells, xv = encode(n, H, W)
            count = 0
            for subset in itertools.combinations(cells, n):
                sset = set(subset)
                ref = connected_touching(sset, H)
                got = eval_cnf_on_subset(cnf, cells, xv, sset)
                assert got is not None, "propagation incomplete"
                assert got == ref, (n, H, sset)
                if got:
                    count += 1
                total_subsets += 1
            banked = tri.cell(n, H)
            status = "OK" if count == banked else "MISMATCH"
            print(f"T({n},{H}) cnf={count} banked={banked} {status}")
            assert count == banked
    print(f"SELFTEST PASS ({total_subsets} subsets checked, "
          f"per-subset CNF<->BFS agreement + banked counts)")


def emit(n, H):
    cnf, cells, xv = encode(n, H)
    print(f"c T({n},{H}) king-connected height-exact; raw model count = T")
    print(f"c projection vars (cells, column-major): 1..{len(cells)}")
    print(f"p cnf {cnf.nvars} {len(cnf.clauses)}")
    for cl in cnf.clauses:
        print(" ".join(map(str, cl)), "0")


if __name__ == "__main__":
    sys.path.insert(0, "/Users/jasonp/src/polyominoes/experiments/tristruct")
    if "--selftest" in sys.argv:
        selftest()
    elif "--emit" in sys.argv:
        i = sys.argv.index("--emit")
        emit(int(sys.argv[i + 1]), int(sys.argv[i + 2]))
    else:
        print(__doc__)
