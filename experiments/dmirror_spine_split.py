#!/usr/bin/env python3
"""Split the dmirror count by which ground-state spine the animal sits on.

docs/time-at-the-bar-report.md (deleted), A1.3's live half.  `results/symmetry-classes.md`
showed the grand form does not transfer to the dmirror family, and diagnosed
why: d(S, S) = 2 for every S >= 2, so the family is a SUM over two ground
states -- the main diagonal and the anti-diagonal -- and the log of a sum of
two exponentials is not linear in S.  The parity split was the natural repair
and it failed: every cumulant past the first is nonlinear on BOTH parity
classes.  The degree pattern deg(c_j) = 2*floor(j/2) is the signature of
exactly two families.

So the question is whether EACH FAMILY SEPARATELY has a grand form, and that
needs the two counted apart.  This does that.

THE SPLIT IS FREE, ONCE YOU SEE IT.  Sweep the animal by HOOKS: hook k is the
set of cells with min(i,j) = k, i.e. the corner (k,k) plus the mirror pairs
{(k,k+p), (k+p,k)}.  The main diagonal is then exactly the set of hook
CORNERS.  So counting by (n, number of occupied corners) separates the spines
with no geometry beyond what the sweep already tracks:

  * a main-spine animal at level k is within k defects of the full diagonal, so
    it has >= S-k occupied corners;
  * an anti-spine animal has the anti-diagonal (i, S-1-i), whose cells are ARM
    cells at offset p = S-1-2i, never corners -- except the centre cell when S
    is odd, which is the corner of hook (S-1)/2.  So it has <= k+1 corners.

For S > 2k those ranges are disjoint, which is exactly the regime the pinning
happens in.

AND IT TESTS SOMETHING THE DIAGNOSIS ASSUMED.  `dmirror-grand-form-fails.md`
asserts d = d_main + d_anti for large S.  That is a claim about EXHAUSTIVENESS
-- that no dmirror animal at level k sits near neither spine -- and it has
never been checked.  The corner-count histogram checks it directly: any weight
in the middle of the range is an animal belonging to neither family, and the
script reports it rather than assuming it away.

FAIL-CLOSED ANCHOR, AND IT IS THE WHOLE REASON TO TRUST THIS.  This enumerator
shares no code with cpp/sym/symtm.cpp, which produced the banked
`dmirror_strip` rows in results/sym_counts.txt.  Summing the histogram over
corner counts must reproduce those rows EXACTLY, cell for cell.  A single
disagreement means this file is wrong and nothing it says may be used.

Usage:
    python3 experiments/dmirror_spine_split.py [SMAX]     # default 12

Target machine: ayr or dalby.  Cost: exponential in S; S <= 12 is seconds,
S = 14 is minutes.  Pure Python, no dependencies.
"""

import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYM = os.path.join(ROOT, "results", "sym_counts.txt")


def banked():
    """d[(S, n)] from the tracked fallback table."""
    d = {}
    for ln in open(SYM):
        p = ln.split()
        if len(p) == 4 and p[0] == "dmirror_strip":
            d[(int(p[1]), int(p[2]))] = int(p[3])
    return d


# --------------------------------------------------------------------------
# Hook geometry.
#
# Hook k has positions 0..L-1 where L = S-k: position 0 is the corner (k,k)
# (one cell), position p >= 1 is the mirror PAIR {(k,k+p), (k+p,k)} (two
# cells).  A hook's occupancy is a bitmask over those positions.
#
# Adjacency, all derived from |di| <= 1 and |dj| <= 1:
#
#   within a hook   corner ~ position 1 (both arms touch the corner and each
#                   other); position p ~ position p+1 along each arm; the two
#                   arms meet only at p = 1 (cells (k,k+1) and (k+1,k) are
#                   diagonal neighbours).  So positions p and p+1 are adjacent
#                   for every p >= 0.
#   hook k to k+1   column-arm cell (k, k+p) touches (k+1, k+1+q) iff
#                   |p - q - 1| <= 1, i.e. q in {p-2, p-1, p}; the corner of
#                   hook k+1 is q = 0.  Row arms mirror it.  A column arm of
#                   hook k never reaches a ROW arm of hook k+1 (row distance
#                   >= 2) except through the corner, which the mirror already
#                   covers.
# --------------------------------------------------------------------------

def hook_cells(S, k):
    """Cells of hook k, as (position, (i, j)) with position 0 the corner.

    Position p >= 1 contributes TWO cells, (k, k+p) and (k+p, k).  They are the
    same position because the mirror symmetry forces them to be occupied
    together -- but they are DIFFERENT CELLS and are not adjacent to each other
    unless p = 1, which is why they must carry separate component labels.  The
    first version of this file collapsed each pair to one node and counted
    disconnected animals as connected; the banked-row anchor caught it at
    S = 4.
    """
    out = [(0, (k, k))]
    for p in range(1, S - k):
        out.append((p, (k, k + p)))
        out.append((p, (k + p, k)))
    return out


def adjacent(a, b):
    return a != b and abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


class DSU:
    __slots__ = ("p",)

    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def geometry(S):
    """Per hook: the cell list, within-hook edges, and edges to the next hook.

    Built from the coordinates by brute force -- no hand-derived adjacency
    rules, which is where the first version went wrong."""
    cells = [hook_cells(S, k) for k in range(S)]
    within, between = [], []
    for k in range(S):
        cs = cells[k]
        within.append([(a, b) for a in range(len(cs)) for b in range(a + 1, len(cs))
                       if adjacent(cs[a][1], cs[b][1])])
        if k + 1 < S:
            ns = cells[k + 1]
            between.append([(a, b) for a in range(len(cs)) for b in range(len(ns))
                            if adjacent(cs[a][1], ns[b][1])])
        else:
            between.append([])
    return cells, within, between


def label_hook(cells, within, occ, inherited):
    """Component labels over the OCCUPIED cells of one hook.

    `occ` is a mask over POSITIONS; a cell is occupied iff its position's bit
    is set.  `inherited` is a list of (cell index in this hook, old label).
    Returns (tuple of occupied cell indices, canonical label tuple, set of old
    labels that reached this hook)."""
    idxs = [i for i, (p, _) in enumerate(cells) if occ >> p & 1]
    pos_of = {i: n for n, i in enumerate(idxs)}
    dsu = DSU(len(idxs))
    for a, b in within:
        if a in pos_of and b in pos_of:
            dsu.union(pos_of[a], pos_of[b])
    byold = defaultdict(list)
    for i, old in inherited:
        byold[old].append(pos_of[i])
    for group in byold.values():
        for x in group[1:]:
            dsu.union(group[0], x)
    roots, labels = {}, []
    for n in range(len(idxs)):
        r = dsu.find(n)
        if r not in roots:
            roots[r] = len(roots)
        labels.append(roots[r])
    return tuple(idxs), tuple(labels), set(byold)


def sweep(S):
    """Histogram h[(n, corners)] of dmirror animals with bbox exactly SxS."""
    cells, within, between = geometry(S)
    hist = defaultdict(int)
    npos = [S - k for k in range(S)]

    cur = defaultdict(lambda: defaultdict(int))
    cs0 = cells[0]
    for occ in range(1, 1 << npos[0]):               # hook 0 must be nonempty
        idxs, labels, _ = label_hook(cs0, within[0], occ, [])
        n = len(idxs)
        corners = 1 if occ & 1 else 0
        touched = 1 if any(max(cs0[i][1]) == S - 1 for i in idxs) else 0
        cur[(occ, idxs, labels, touched)][(n, corners)] += 1

    for k in range(S):
        nxt = defaultdict(lambda: defaultdict(int))
        for (occ, idxs, labels, touched), counts in cur.items():
            nlab = len(set(labels))
            if nlab == 1 and touched:                # the animal ends here
                for nc, v in counts.items():
                    hist[nc] += v
            if k + 1 >= S:
                continue
            lab = {i: labels[t] for t, i in enumerate(idxs)}
            occ_set = set(idxs)
            cs2 = cells[k + 1]
            for occ2 in range(1, 1 << npos[k + 1]):
                inherited = []
                for a, b in between[k]:
                    if a in occ_set and (occ2 >> cs2[b][0] & 1):
                        inherited.append((b, lab[a]))
                if len({o for _, o in inherited}) != nlab:
                    continue                          # a component stranded
                idxs2, labels2, _ = label_hook(cs2, within[k + 1], occ2,
                                               inherited)
                add_n = len(idxs2)
                add_c = 1 if occ2 & 1 else 0
                t2 = touched or any(max(cs2[i][1]) == S - 1 for i in idxs2)
                dst = nxt[(occ2, idxs2, labels2, 1 if t2 else 0)]
                for (n, c), v in counts.items():
                    dst[(n + add_n, c + add_c)] += v
        cur = nxt
    return hist


def main():
    smax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    bank = banked()
    print("dmirror spine split -- independent enumerator, anchored on the "
          "banked rows\n")
    print("The split is only DEFINED where S > 2k: below that the two corner-"
          "count\nranges overlap and 'main' and 'anti' are not disjoint sets. "
          "Rows with\nS <= 2k are anchored but not split.\n")
    print("  %-4s %-4s %-14s %-14s %-10s %-10s %-9s"
          % ("S", "k", "total", "banked", "main", "anti", "neither"))
    bad = mismatch = 0
    rows = {}
    for S in range(2, smax + 1):
        hist = sweep(S)
        bytotal = defaultdict(int)
        for (n, c), v in hist.items():
            bytotal[n] += v
        for n in sorted(bytotal):
            k = n - S
            if k < 0:
                continue
            tot = bytotal[n]
            b = bank.get((S, n))
            if b is not None and b != tot:
                mismatch += 1
                print("  %-4d %-4d %-14d %-14d %s" % (S, k, tot, b,
                                                      "<== MISMATCH"))
                continue
            if S <= 2 * k:
                continue
            main = sum(v for (nn, c), v in hist.items()
                       if nn == n and c >= S - k)
            anti = sum(v for (nn, c), v in hist.items()
                       if nn == n and c <= k + 1)
            other = tot - main - anti
            if other:
                bad += 1
            rows[(S, k)] = (main, anti, other)
            print("  %-4d %-4d %-14d %-14s %-10d %-10d %-9d%s"
                  % (S, k, tot, b if b is not None else "-", main, anti, other,
                     "   <== NEITHER SPINE" if other else ""))
    print("\nanchor: %s"
          % ("every banked cell reproduced, %d cells" % len(bank)
             if mismatch == 0 else "%d MISMATCHES -- this file is WRONG" % mismatch))
    if mismatch:
        return 1
    print("exhaustiveness (S > 2k only): %s"
          % ("d = d_main + d_anti at every cell measured, %d cells" % len(rows)
             if bad == 0 else "%d cell(s) carry animals near NEITHER spine" % bad))

    # the split, laid out per level for the cumulant test
    print("\nd_main(S, S+k), the main-diagonal family alone:")
    for k in range(0, 5):
        pts = [(S, rows[(S, k)][0]) for S in range(2, smax + 1)
               if (S, k) in rows]
        if pts:
            print("  k=%d  %s" % (k, "  ".join("%d:%d" % t for t in pts)))
    print("\nd_anti(S, S+k), the anti-diagonal family alone:")
    for k in range(0, 5):
        pts = [(S, rows[(S, k)][1]) for S in range(2, smax + 1)
               if (S, k) in rows]
        if pts:
            print("  k=%d  %s" % (k, "  ".join("%d:%d" % t for t in pts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
