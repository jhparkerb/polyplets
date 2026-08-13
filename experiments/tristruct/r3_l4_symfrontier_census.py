#!/usr/bin/env python3
"""r3_l4_symfrontier_census.py -- L4-9: exact state census of the
hmirror-quotient fixed-height strip TM, verified against a closed form.

Claim under test: the reachable frontier states of the connectivity TM
restricted to h-symmetric columns (the realization behind I_H(<h>) --byheight)
are exactly the pairs

    (nonempty h-symmetric column mask, reversal-invariant non-crossing
     partition of its runs)

and their number is

    S(H) = sum_{k>=1} C(N,k) * C(k, floor(k/2)),   N = ceil(H/2)

(#symmetric masks with k runs = C(N,k), proved by hockey-stick in the
deliverable; #reversal-invariant NC partitions of k points = C(k,floor(k/2))).

Three-way check per H: (1) reachability closure of a from-scratch union-find
transition over symmetric columns; (2) direct count of the predicted state
set; (3) the closed form. All three must agree, and the reachable SET must
equal the predicted SET (not just the counts).

Controls:
  POSITIVE -- the same closure over ALL masks (not just symmetric) must
  reproduce the banked/proved full-frontier census Motzkin(H+1)-1
  (king-column-motzkin theorem), validating the union-find/stranding
  transition against an independently proved value.
  RED -- an asymmetric stencil (NE diagonal dropped) breaks the mirror
  symmetry, so the reachable set must leave the reversal-invariant class
  and the census must change at some H.
  Recorded observation: a symmetric rook stencil (both diagonals dropped)
  reaches the SAME state set at H<=8 -- the census is stencil-robust
  between rook and king; the discriminating observable is the count the
  TM produces, not its state census. That is why the RED must be
  asymmetric to bite at census level.
"""
import sys
from math import comb
from itertools import combinations


def sym_masks(H):
    """All nonempty h-symmetric masks of an H-column, as sorted row tuples."""
    N = (H + 1) // 2
    out = []
    for bits in range(1, 1 << N):
        rows = set()
        for i in range(N):
            if bits >> i & 1:
                rows.add(i)
                rows.add(H - 1 - i)
        out.append(tuple(sorted(rows)))
    return out


def runs(mask):
    """Maximal intervals of a sorted row tuple, as (lo, hi) pairs."""
    rs, lo, hi = [], mask[0], mask[0]
    for r in mask[1:]:
        if r == hi + 1:
            hi = r
        else:
            rs.append((lo, hi))
            lo = hi = r
    rs.append((lo, hi))
    return rs


def touches(old, new, stencil):
    """Does old run touch new run in the next column?

    stencil: 'king' (both diagonals), 'rook' (none), 'noNE' (NE dropped:
    new cell r sees old rows {r, r+1} only -- mirror-asymmetric).
    """
    (a, b), (c, d) = old, new
    if stencil == 'king':
        return c <= b + 1 and d >= a - 1
    if stencil == 'rook':
        return c <= b and d >= a
    if stencil == 'noNE':
        return c <= b and d >= a - 1
    raise ValueError(stencil)


def canon(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def step(mask_o, part_o, mask_n, stencil):
    """One column transition; None if any old block strands."""
    ro, rn = runs(mask_o), runs(mask_n)
    parent = list(range(len(rn)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for block in part_o:
        touched = [j for j in range(len(rn))
                   if any(touches(ro[i], rn[j], stencil) for i in block)]
        if not touched:
            return None  # stranded component: dead prefix
        r0 = find(touched[0])
        for j in touched[1:]:
            parent[find(j)] = r0
    groups = {}
    for j in range(len(rn)):
        groups.setdefault(find(j), []).append(j)
    return canon(groups.values())


def all_masks(H):
    out = []
    for bits in range(1, 1 << H):
        out.append(tuple(r for r in range(H) if bits >> r & 1))
    return out


def closure(H, stencil='king', masks=None):
    if masks is None:
        masks = sym_masks(H)
    seen = set()
    frontier = []
    for m in masks:
        s = (m, canon([[i] for i in range(len(runs(m)))]))
        seen.add(s)
        frontier.append(s)
    while frontier:
        nxt = []
        for mask_o, part_o in frontier:
            for mask_n in masks:
                p = step(mask_o, part_o, mask_n, stencil)
                if p is not None and (mask_n, p) not in seen:
                    seen.add((mask_n, p))
                    nxt.append((mask_n, p))
        frontier = nxt
    return seen


def set_partitions(k):
    if k == 0:
        yield []
        return
    for rest in set_partitions(k - 1):
        yield rest + [[k - 1]]
        for i in range(len(rest)):
            yield rest[:i] + [rest[i] + [k - 1]] + rest[i + 1:]


def noncrossing(part):
    blk = {}
    for i, b in enumerate(part):
        for x in b:
            blk[x] = i
    xs = sorted(blk)
    for a, b, c, d in combinations(xs, 4):
        if blk[a] == blk[c] and blk[b] == blk[d] and blk[a] != blk[b]:
            return False
    return True


def rev_invariant(part, k):
    return canon(part) == canon([[k - 1 - x for x in b] for b in part])


def predicted(H):
    out = set()
    for m in sym_masks(H):
        k = len(runs(m))
        for p in set_partitions(k):
            if noncrossing(p) and rev_invariant(p, k):
                out.add((m, canon(p)))
    return out


def S_closed(H):
    N = (H + 1) // 2
    return sum(comb(N, k) * comb(k, k // 2) for k in range(1, N + 1))


def main():
    hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 13
    print("H  closure  predicted  closed-form  sets-equal")
    ok = True
    for H in range(1, hmax + 1):
        got = closure(H)
        pred = predicted(H)
        cf = S_closed(H)
        eq = got == pred
        ok &= eq and len(got) == cf
        print(f"{H:2d} {len(got):8d} {len(pred):9d} {cf:11d}  {eq}")
    # cb(k) really counts reversal-invariant NC partitions (direct, k<=8)
    for k in range(1, 9):
        n = sum(1 for p in set_partitions(k)
                if noncrossing(p) and rev_invariant(p, k))
        assert n == comb(k, k // 2), (k, n)
    print("cb(k) = #rev-invariant NC partitions verified directly, k<=8")
    # POSITIVE control: full-mask closure = Motzkin(H+1)-1 (banked theorem)
    motzkin = [1, 1, 2, 4, 9, 21, 51, 127, 323, 835, 2188]
    pos = all(len(closure(H, masks=all_masks(H))) == motzkin[H + 1] - 1
              for H in range(2, 9))
    print(f"POSITIVE (full masks -> Motzkin(H+1)-1, H=2..8): {pos}")
    # RED: asymmetric stencil (NE dropped) must change the census somewhere
    red = any(len(closure(H, stencil='noNE')) != S_closed(H)
              for H in range(2, 9))
    print(f"RED (noNE stencil changes census, some H<=8): {red}")
    # observation: symmetric rook stencil reaches the same state SET
    rook_same = all(closure(H, stencil='rook') == closure(H)
                    for H in range(2, 9))
    print(f"observation: rook closure set == king closure set, H<=8: "
          f"{rook_same}")
    if not (ok and pos and red):
        print("FAIL")
        sys.exit(1)
    print("PASS")
    # band table from the closed form
    print("\nband: H, states S, exact-height dim S(H)+S(H-2), "
          "order ceiling H*(that)")
    for H in range(15, 22):
        d = S_closed(H) + S_closed(H - 2)
        print(f"H={H}: S={S_closed(H):6d}  dim={d:6d}  ceil={H*d}")


if __name__ == "__main__":
    main()
