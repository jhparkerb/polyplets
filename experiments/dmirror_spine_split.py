#!/usr/bin/env python3
"""Split the dmirror count by which ground-state spine the animal sits on.

docs/time-at-the-bar-report.md, A1.3's live half.  `results/dmirror-grand-form-fails.md`
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

def within_pairs(L):
    """Adjacent position pairs inside one hook of length L."""
    return [(p, p + 1) for p in range(L - 1)]


def between_pairs(L, L2):
    """(p in hook k, q in hook k+1) adjacent pairs.  L = S-k, L2 = S-k-1."""
    out = []
    for p in range(L):
        for q in (p - 2, p - 1, p):
            if 0 <= q < L2:
                out.append((p, q))
    return out


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


def canon_labels(occ, L, extra_edges, inherited):
    """Component labels for the occupied positions of one hook.

    `occ` is the mask, `extra_edges` the within-hook adjacent pairs, and
    `inherited` a list of (position, oldlabel) links from the previous hook.
    Returns (labels tuple over occupied positions in order, number of distinct
    inherited old labels that reached this hook, mapping oldlabel -> newlabel).
    """
    pos = [p for p in range(L) if occ >> p & 1]
    idx = {p: i for i, p in enumerate(pos)}
    dsu = DSU(len(pos))
    for a, b in extra_edges:
        if a in idx and b in idx:
            dsu.union(idx[a], idx[b])
    # inherited links merge positions that shared an old component
    byold = defaultdict(list)
    for p, old in inherited:
        if p in idx:
            byold[old].append(idx[p])
    for group in byold.values():
        for x in group[1:]:
            dsu.union(group[0], x)
    roots = {}
    labels = []
    for i in range(len(pos)):
        r = dsu.find(i)
        if r not in roots:
            roots[r] = len(roots)
        labels.append(roots[r])
    return tuple(pos), tuple(labels), byold, dsu, idx


def sweep(S):
    """Histogram h[(n, corners)] of dmirror animals with bbox exactly SxS."""
    hist = defaultdict(int)
    # state: (occupancy mask of the current hook, label tuple, touched flag)
    #        -> {(n_so_far, corners_so_far): count}
    L0 = S
    cur = {}
    within0 = within_pairs(L0)
    for occ in range(1, 1 << L0):                    # hook 0 must be nonempty
        pos, labels, _, _, _ = canon_labels(occ, L0, within0, [])
        n = sum(1 if p == 0 else 2 for p in pos)
        corners = 1 if occ & 1 else 0
        touched = 1 if (occ >> (L0 - 1)) & 1 else 0  # reaches coordinate S-1
        key = (occ, labels, touched)
        cur.setdefault(key, defaultdict(int))[(n, corners)] += 1

    for k in range(S - 1):
        L, L2 = S - k, S - k - 1
        between = between_pairs(L, L2)
        within2 = within_pairs(L2)
        nxt = defaultdict(lambda: defaultdict(int))
        for (occ, labels, touched), counts in cur.items():
            pos = [p for p in range(L) if occ >> p & 1]
            lab = {p: labels[i] for i, p in enumerate(pos)}
            nlab = len(set(labels))
            # harvest: the animal ends at this hook iff it is connected and
            # the bbox is exact.  Remaining hooks empty.
            if nlab == 1 and touched:
                for (n, c), v in counts.items():
                    hist[(n, c)] += v
            for occ2 in range(1 << L2):
                if occ2 == 0:
                    continue                          # a gap kills the animal
                inherited = []
                for p, q in between:
                    if (occ >> p & 1) and (occ2 >> q & 1):
                        inherited.append((q, lab[p]))
                reached = {old for _, old in inherited}
                if len(reached) != nlab:
                    continue                          # a component stranded
                pos2, labels2, _, _, _ = canon_labels(
                    occ2, L2, within2, inherited)
                add_n = sum(1 if p == 0 else 2 for p in pos2)
                add_c = 1 if occ2 & 1 else 0
                t2 = touched or ((occ2 >> (L2 - 1)) & 1)
                key2 = (occ2, labels2, 1 if t2 else 0)
                dst = nxt[key2]
                for (n, c), v in counts.items():
                    dst[(n + add_n, c + add_c)] += v
        cur = nxt

    # final hook (k = S-1, length 1): harvest whatever is closable
    for (occ, labels, touched), counts in cur.items():
        if len(set(labels)) == 1 and touched:
            for (n, c), v in counts.items():
                hist[(n, c)] += v
    return hist


def main():
    smax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    bank = banked()
    print("dmirror spine split -- independent enumerator, anchored on the "
          "banked rows\n")
    print("  %-4s %-5s %-12s %-12s %-10s %-10s %-8s"
          % ("S", "k", "total", "banked", "main", "anti", "neither"))
    bad = 0
    rows = {}
    for S in range(2, smax + 1):
        hist = sweep(S)
        bytotal = defaultdict(int)
        for (n, c), v in hist.items():
            bytotal[n] += v
        for n in sorted(bytotal):
            k = n - S
            if k < 0 or k > 6:
                continue
            tot = bytotal[n]
            b = bank.get((S, n))
            main = sum(v for (nn, c), v in hist.items()
                       if nn == n and c >= S - k)
            anti = sum(v for (nn, c), v in hist.items()
                       if nn == n and c <= k + 1)
            other = tot - main - anti
            ok = (b is None) or (b == tot)
            if not ok:
                bad += 1
            rows[(S, k)] = (main, anti, other)
            print("  %-4d %-5d %-12d %-12s %-10d %-10d %-8d%s"
                  % (S, k, tot, b if b is not None else "-", main, anti, other,
                     "" if ok else "   <== MISMATCH"))
    print("\nanchor: %s" % ("all banked cells reproduced"
                            if bad == 0 else "%d MISMATCHES" % bad))
    if bad:
        print("This enumerator is WRONG. Nothing above may be used.")
        return 1
    nonempty = [(S, k) for (S, k), (m, a, o) in rows.items() if o]
    print("exhaustiveness: %s"
          % ("d = d_main + d_anti at every cell measured"
             if not nonempty else
             "cells with animals near NEITHER spine: %s" % nonempty[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
