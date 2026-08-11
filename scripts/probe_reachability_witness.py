#!/usr/bin/env python3
# probe_reachability_witness.py — machine check of the A-S6 reachability lemma
# (2026-08-11, throwaway). For EVERY (nonempty fill, non-crossing partition of
# its runs) at height H, build the explicit rails-and-spurs witness prefix and
# run it through the incumbent automaton (probe_hankel_rank.build machinery):
# the end state must equal exactly (fill, partition), alive, no strandings.
#
# Witness: blocks of the partition with >= 2 runs get, at nesting depth
# delta (1 = outermost among non-singleton blocks), a vertical RAIL in column
# -2*(D - delta + 1) spanning the block's full row interval, plus a horizontal
# SPUR at the bottom row of each member run, from the rail column to column -1.
# Singleton blocks get nothing. Prefix = columns -2D .. -1, then the fill.
# Separations used by the proof (all rechecked implicitly by the automaton):
# distinct runs have bottom rows >= 2 apart; non-crossing spans are nested or
# >= 2 apart; nested blocks have strictly deeper (closer) rails, >= 2 columns
# apart.
# Cost: H <= 7 foreground seconds; H = 8 ~ a minute. 1 core.
import sys
from probe_hankel_rank import build, canon, runs_partition, transition

def runs_of(fill, H):
    out, cur = [], None
    for r in range(H):
        if fill >> r & 1:
            if cur is None: cur = [r, r]
            else: cur[1] = r
        else:
            if cur: out.append(tuple(cur)); cur = None
    if cur: out.append(tuple(cur))
    return out

def noncrossing_partitions(k):
    """all non-crossing partitions of 0..k-1 (as tuples of frozensets)."""
    if k == 0: yield (); return
    # element 0 is in a block with some subset; non-crossing structure:
    # block of 0 = {0} u S; between consecutive members the elements form
    # independent NC partitions, and after the last member too.
    def helper(elems):
        if not elems: yield (); return
        first, rest = elems[0], elems[1:]
        n = len(rest)
        # choose members of first's block among rest, non-crossing:
        # pick indices i1<...<im in rest; segments between them partitioned NC
        for mask in range(1 << n):
            members = [rest[i] for i in range(n) if mask >> i & 1]
            block = frozenset([first] + members)
            # segments: split rest by membership
            segs, cur = [], []
            for x in rest:
                if x in block:
                    segs.append(cur); cur = []
                else:
                    cur.append(x)
            segs.append(cur)
            def prod(i):
                if i == len(segs): yield (); return
                for p1 in helper(segs[i]):
                    for p2 in prod(i+1):
                        yield p1 + p2
            for p in prod(0):
                yield (block,) + p
    yield from helper(list(range(k)))

def witness_word(fill, part, H):
    """columns left->right (list of fills), NOT including `fill` itself."""
    rs = runs_of(fill, H)
    blocks = [sorted(b) for b in part if len(b) >= 2]
    if not blocks: return []
    # nesting depth: number of other non-singleton blocks strictly containing span
    spans = {}
    for i, b in enumerate(blocks):
        spans[i] = (rs[b[0]][0], rs[b[-1]][1])  # (lo row, hi row)
    depth = {}
    for i in range(len(blocks)):
        d = 1
        for j in range(len(blocks)):
            if i != j:
                lo_i, hi_i = spans[i]; lo_j, hi_j = spans[j]
                if lo_j <= lo_i and hi_i <= hi_j and (lo_j, hi_j) != (lo_i, hi_i):
                    d += 1
        depth[i] = d
    D = max(depth.values())
    width = 2 * D           # columns -2D..-1
    cols = [0] * width      # cols[0] = column -2D ... cols[-1] = column -1
    for i, b in enumerate(blocks):
        rail_col = width - 2 * (D - depth[i] + 1)   # index in cols
        lo, hi = spans[i]
        for r in range(lo, hi + 1):
            cols[rail_col] |= 1 << r
        for m in b:
            spur_row = rs[m][0]                     # bottom row of member run
            for cidx in range(rail_col, width):
                cols[cidx] |= 1 << spur_row
    return cols

def state_of_word(word, H):
    """run word through the automaton; None if dead."""
    if not word: return None
    s = canon(runs_partition(word[0], H))
    for c in word[1:]:
        s = transition(s, c, H)
        if s is None: return None
    return s

def check(H):
    total = fails = 0
    for fill in range(1, 1 << H):
        rs = runs_of(fill, H)
        k = len(rs)
        for part in noncrossing_partitions(k):
            total += 1
            word = witness_word(fill, part, H) + [fill]
            end = state_of_word(word, H)
            # expected state: run index -> block id
            blkid = {}
            for bi, b in enumerate(sorted(part, key=min)):
                for m in b: blkid[m] = bi + 1
            expect = [0] * H
            for ri, (lo, hi) in enumerate(rs):
                for r in range(lo, hi + 1):
                    expect[r] = blkid[ri]
            expect = canon(tuple(expect))
            if end != expect:
                fails += 1
                if fails <= 5:
                    print(f"  FAIL H={H} fill={fill:0{H}b} part={sorted(map(sorted,part))} got={end} want={expect}")
    return total, fails

if __name__ == "__main__":
    hs = [int(a) for a in sys.argv[1:]] or [4, 5, 6, 7]
    for H in hs:
        total, fails = check(H)
        print(f"H={H}: {total} (fill, NC-partition) pairs, {fails} failures"
              + ("  ALL WITNESSED" if fails == 0 else ""))
        sys.stdout.flush()
