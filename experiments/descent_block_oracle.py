#!/usr/bin/env python3
"""Independent re-derivation of the 4-cone-truncated (0,1) descent block.

Written to CHECK results/hv-growth-sandwich.md's block series without reusing
experiments/dir4_descent_block.py's recursion.  The block is defined here from
the geometry, not from a height kernel:

    a standalone phase-(0,1) run is a sequence of column intervals
    [b(j), t(j)], j = 1..k, with

        b nonincreasing         (the bottom is still falling: d := b' - b <= 0)
        t nonincreasing         (the top has already turned: t' <= t)
        king adjacency          b(j) <= t(j+1) + 1
        4-cone (dir4)           d >= -1

    counted up to translation (fix b(1) = 0) by area sum_j h(j).

`brute` enumerates those interval sequences directly by DFS over (b, t) pairs.
`dp` is a forward DP over the LAST column's height with prefix sums -- the
opposite direction from dir4_descent_block.py's backward recursion over the
FIRST column's height -- so agreement between the two is a real cross-check,
not the same arithmetic twice.

RED controls (each must DIVERGE from the true series, and its own DFS and DP
must agree with each other):
  none    drop the dir4 floor entirely (kernel min(h,h')+1 -- the unrestricted
          (0,1) block, which is a mirrored staircase and grows like mu)
  two     let the bottom fall by 2 (d >= -2)
  climb   let the h' = h+1 climb carry weight 2

Usage: python3 experiments/descent_block_oracle.py [--nmax 700]
                [--check results/mk_dir4_descblock_n700.txt] [--out FILE]
Target machine: gympie (laptop), single core.  MEASURED: --nmax 700 in ~20 s,
< 250 MB.  Kill = SIGINT; there is nothing to resume.
"""
import argparse
import sys

from seriestools import read_terms


def brute(nmax, red=None):
    """DFS over explicit interval sequences.  The oracle."""
    out = [0] * (nmax + 1)
    sys.setrecursionlimit(10000)

    def walk(b, t, area, w):
        out[area] += w
        h = t - b + 1
        room = nmax - area
        if red == 'none':
            lo_bp = b - room            # only adjacency + area bound the drop
        elif red == 'two':
            lo_bp = b - 2
        else:
            lo_bp = b - 1
        for bp in range(max(lo_bp, b - room), b + 1):
            # t nonincreasing, adjacency b <= tp + 1, nonempty interval
            for tp in range(max(bp, b - 1), t + 1):
                hp = tp - bp + 1
                if area + hp > nmax:
                    break
                ww = w
                if red == 'climb' and hp == h + 1:
                    ww = 2 * w
                walk(bp, tp, area + hp, ww)

    for h in range(1, nmax + 1):
        walk(0, h - 1, h, 1)
    return out


def dp(nmax, red=None):
    """Forward DP on the LAST column's height, with prefix sums.

    g[m][h] = weight of runs of area m whose last column has height h.  The
    step h -> h' has weight #{d in [max(dmin, -h'), min(0, h - h')]}, which for
    each variant is piecewise constant in h and so prefix-summable.
    """
    out = [0] * (nmax + 1)
    g = [[0] * (nmax + 2) for _ in range(nmax + 1)]
    for h in range(1, nmax + 1):
        g[h][h] += 1                     # the one-column runs
    for m in range(1, nmax + 1):
        row = g[m]
        suf = [0] * (nmax + 3)           # suf[h] = sum_{h'' >= h} row[h'']
        sufw = [0] * (nmax + 3)          # sufw[h] = sum_{h'' >= h} (h''+1) row
        for h in range(nmax, 0, -1):
            suf[h] = suf[h + 1] + row[h]
            sufw[h] = sufw[h + 1] + (h + 1) * row[h]
        out[m] = suf[1]
        if m == nmax:
            break
        for hp in range(1, nmax - m + 1):
            if red == 'none':
                # min(h,h')+1: (h'+1) when h >= h', (h+1) when h < h'
                v = (hp + 1) * suf[hp] + sufw[1] - sufw[hp]
            elif red == 'two':
                if hp == 1:
                    v = 2 * suf[1]
                else:
                    v = (3 * suf[hp] + 2 * row[hp - 1]
                         + (row[hp - 2] if hp >= 2 else 0))
            elif red == 'climb':
                v = 2 * suf[hp] + 2 * row[hp - 1]
            else:
                v = 2 * suf[hp] + row[hp - 1]
            if v:
                g[m + hp][hp] += v
    return out


def _walk_hv(nmax, dir4):
    """HV-convex animals by area, tallied by which middle phases they visit.

    Enumerates explicit column-interval sequences [b, t] up to translation and
    carries the two unimodality phase bits exactly as build/middle_kingdom_tm
    does: pb = 1 once b has risen (then d >= 0 forever), pt = 1 once t has
    fallen (then d <= s forever).  dir4=True adds the 4-cone floor (the bottom
    drops at most one row per step right); dir4=False leaves it unrestricted.

    Returns by_seen[m][n], m the bitmask of visited middle phases: bit 0 is
    (0,1), bit 1 is (1,0).  This is the load-bearing phase-path logic for both
    oracles below, so it lives in one place -- a fix here cannot land in one
    and miss the other.
    """
    by_seen = [[0] * (nmax + 1) for _ in range(4)]
    sys.setrecursionlimit(10000)

    def walk(b, t, area, pb, pt, seen):
        by_seen[seen][area] += 1
        h = t - b + 1
        for hp in range(1, nmax - area + 1):
            s = h - hp
            lo, hi = (max(-hp, -1) if dir4 else -hp), h
            if pb == 1:
                lo = max(lo, 0)
            if pt == 1:
                hi = min(hi, s)
            for d in range(lo, hi + 1):
                npb = 1 if d > 0 else pb
                npt = 1 if d < s else pt
                code = 1 if (npb, npt) == (0, 1) else (2 if (npb, npt) == (1, 0)
                                                       else 0)
                walk(b + d, b + d + hp - 1, area + hp, npb, npt, seen | code)

    for h in range(1, nmax + 1):
        walk(0, h - 1, h, 0, 0, 0)
    return by_seen


def brute_hvdir4(nmax):
    """Brute force over (dir4, HV-convex) animals, split by phase path.

    Independent oracle for build/middle_kingdom_tm's hvdir4 / hvdir4asc /
    hvdir4ascbad modes.  Returns (all, asc, ascbad) where `asc` drops every
    animal whose phase path ever visits (0,1) and `ascbad` -- the RED control
    -- drops (1,0) instead.
    """
    m = _walk_hv(nmax, dir4=True)
    tot = [sum(c) for c in zip(*m)]
    asc = [x + y for x, y in zip(m[0], m[2])]   # never visited (0,1)
    bad = [x + y for x, y in zip(m[0], m[1])]   # never visited (1,0)
    return tot, asc, bad


def brute_hv_mirror(nmax):
    """UNRESTRICTED HV-convex animals, split by which middle phase they visit.

    results/hv-growth-sandwich.md's feed-vector identity for the amplitude
    ratio turns on C_HV = 2 C(A_(1,0)), which follows from the vertical mirror
    [b,t] -> [-t,-b]: it preserves area and every column height, and swaps the
    phase bits (pb,pt) -> (pt,pb), so it is an involution carrying the
    (1,0)-visiting animals onto the (0,1)-visiting ones.  This enumerates all
    three parts and checks that equality termwise, which is the whole content
    of the factor 1/2.

    Returns (all, via_10, via_01, neither).
    """
    m = _walk_hv(nmax, dir4=False)
    tot = [sum(c) for c in zip(*m)]
    nei = [x + y for x, y in zip(m[0], m[3])]   # visited both, or neither
    return tot, m[2], m[1], nei


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=700)
    ap.add_argument('--brute', type=int, default=13)
    ap.add_argument('--check', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--phases', type=int, default=0,
                    help='also brute-force (dir4, HV-convex) split by phase '
                         'path up to this n, for the engine modes hvdir4asc / '
                         'hvdir4ascbad')
    ap.add_argument('--mirror', type=int, default=0,
                    help='brute-force UNRESTRICTED HV-convex split by middle '
                         'phase up to this n and check A_(1,0) == A_(0,1), '
                         'the factor 1/2 in the amplitude-ratio identity')
    args = ap.parse_args()

    if args.mirror:
        tot, v10, v01, nei = brute_hv_mirror(args.mirror)
        print(f"HV-convex        n<={args.mirror}: {tot[1:]}")
        print(f"  via (1,0)                     : {v10[1:]}")
        print(f"  via (0,1)                     : {v01[1:]}")
        print(f"  via neither                   : {nei[1:]}")
        if v10[1:] != v01[1:]:
            print("FAIL: the mirror involution does not equate the two halves")
            return 1
        if v10[1:] == tot[1:] or v10[2:] == nei[2:]:
            print("FAIL: the split is degenerate")
            return 1
        print("ok   A_(1,0) == A_(0,1) termwise, and neither half is the whole;"
              " the RED reading A_(1,0) == A_neither is false")
        return 0

    if args.phases:
        tot, asc, bad = brute_hvdir4(args.phases)
        print(f"hvdir4       n<={args.phases}: {tot[1:]}")
        print(f"hvdir4asc    n<={args.phases}: {asc[1:]}")
        print(f"hvdir4ascbad n<={args.phases}: {bad[1:]}")
        if asc[1:] == tot[1:] or bad[1:] == asc[1:]:
            print("FAIL: the phase split is a no-op somewhere")
            return 1
        print("ok   asc != all, and the RED control asc-bad != asc")
        return 0

    nb = args.brute
    ok_b, ok_d = brute(nb), dp(nb)
    print(f"brute (interval DFS)  n<={nb}: {ok_b[1:]}")
    print(f"dp    (last column)   n<={nb}: {ok_d[1:nb + 1]}")
    if ok_b[1:] != ok_d[1:nb + 1]:
        print("FAIL: DP != independent interval enumeration")
        return 1
    print("ok   DP == independent interval enumeration")

    for red in ('none', 'two', 'climb'):
        rb, rd = brute(nb, red=red), dp(nb, red=red)
        if rb[1:] != rd[1:nb + 1]:
            print(f"FAIL: RED '{red}' DFS != DP: {rb[1:8]} vs {rd[1:8]}")
            return 1
        if rb[1:] == ok_b[1:]:
            print(f"FAIL: RED '{red}' must diverge and did not")
            return 1
        first = next(i for i in range(1, nb + 1) if rb[i] != ok_b[i])
        print(f"ok   RED '{red}' diverges from n={first}: {rb[1:8]}")

    R = dp(args.nmax)
    print(f"\nT(n), n = 1..12: {R[1:13]}")
    if args.out:
        with open(args.out, 'w') as fh:
            for n in range(1, args.nmax + 1):
                fh.write(f"{n} {R[n]}\n")
        print(f"wrote {args.out}")
    if args.check:
        ref = read_terms(args.check)
        m = min(len(ref), args.nmax)
        bad = [n for n in range(1, m + 1) if ref[n - 1] != R[n]]
        if bad:
            print(f"MISMATCH against {args.check} at n = {bad[:10]}")
            return 1
        print(f"ok   matches {args.check} on all {m} terms")
    return 0


if __name__ == '__main__':
    sys.exit(main())
