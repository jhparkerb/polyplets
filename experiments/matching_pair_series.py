#!/usr/bin/env python3
"""The Sykes-Essam matching relation, tested to the order the repo can reach.

`docs/last-orders.md` C1.2 asked whether the perimeter-defect campaign's
square-lattice series supply the perimeter-graded enumeration that
`results/matching-pair-convention.md` names as idea 2's real cost.  This
script answers that by doing the arithmetic rather than arguing it, and by
verifying the relation as far as brute force reaches.

The relation, in the convention pinned by matching-pair-convention.md:

    K_8(p) - K_4(1-p) = p - 4p^2 + 4p^3 - p^4

with K_a(x) the mean number of a-clusters per site at occupation density x,

    K_8(p)   = sum over FIXED king animals   p^n (1-p)^{t_8}
    K_4(1-p) = sum over FIXED rook animals   (1-p)^n p^{t_4}

t_a is the a-site-perimeter -- the count of distinct empty a-adjacent cells --
SAME lattice as the connectivity, which is the correction that file made.

The two sides are graded differently and that asymmetry is the whole cost:

  - the king side contributes at order p^n, so order N needs n <= N;
  - the rook side contributes at order p^{t_4}, so order N needs every rook
    animal of site-perimeter <= N, at UNBOUNDED size.

This script measures where that second requirement bites, by enumerating the
minimum site-perimeter per size and inverting it.

RED controls:
  - the enumerator must reproduce A001168 and A006770 at every size it reaches;
  - the king site-perimeter at n=1 must be 8 and the rook one 4;
  - a deliberately cross-lattice pairing (king connectivity, rook perimeter)
    must FAIL the relation, or the test cannot detect a convention error.

Usage: python3 experiments/matching_pair_series.py [--nmax-rook 12]
                                                   [--nmax-king 9]
"""
import argparse
import sys
from fractions import Fraction

ROOK = ((1, 0), (-1, 0), (0, 1), (0, -1))
KING = ROOK + ((1, 1), (1, -1), (-1, 1), (-1, -1))

# A001168 (fixed polyominoes) and A006770 (fixed polyplets), heads, for the
# enumerator's own control.
A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268, 505861]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180]


def canon(cells):
    xs = min(c[0] for c in cells)
    ys = min(c[1] for c in cells)
    return frozenset((x - xs, y - ys) for x, y in cells)


def fixed_animals(nmax, nbrs):
    """All fixed animals of 1..nmax cells, by naive growth + canonical dedup.

    Deliberately the simplest correct thing: this is a control and a small-n
    probe, not an enumerator.  Redelmeier lives in cpp/g2_redelmeier.cpp.
    """
    levels = [set(), {canon([(0, 0)])}]
    for _ in range(2, nmax + 1):
        nxt = set()
        for a in levels[-1]:
            for (x, y) in a:
                for dx, dy in nbrs:
                    c = (x + dx, y + dy)
                    if c not in a:
                        nxt.add(canon(set(a) | {c}))
        levels.append(nxt)
    return levels[1:]


def site_perimeter(cells, nbrs):
    """Distinct empty cells adjacent to the animal under `nbrs`."""
    per = set()
    for (x, y) in cells:
        for dx, dy in nbrs:
            c = (x + dx, y + dy)
            if c not in cells:
                per.add(c)
    return len(per)


def gnt(levels, nbrs):
    """{(n, t): count} over the enumerated fixed animals."""
    out = {}
    for n, lv in enumerate(levels, start=1):
        for a in lv:
            t = site_perimeter(a, nbrs)
            out[(n, t)] = out.get((n, t), 0) + 1
    return out


def poly_mul(a, b, N):
    """Truncated product of two coefficient lists, to order N."""
    out = [Fraction(0)] * (N + 1)
    for i, ai in enumerate(a):
        if ai == 0 or i > N:
            continue
        for j, bj in enumerate(b):
            if i + j > N:
                break
            out[i + j] += ai * bj
    return out


def one_minus_p_pow(k, N):
    """(1-p)^k truncated to order N, exactly."""
    from math import comb
    return [Fraction((-1) ** i * comb(k, i)) if i <= k else Fraction(0)
            for i in range(N + 1)]


def p_pow(k, N):
    out = [Fraction(0)] * (N + 1)
    if k <= N:
        out[k] = Fraction(1)
    return out


def K8_series(g, N):
    """sum p^n (1-p)^t  over king animals, to order N."""
    acc = [Fraction(0)] * (N + 1)
    for (n, t), c in g.items():
        if n > N:
            continue
        term = poly_mul(p_pow(n, N), one_minus_p_pow(t, N), N)
        for i in range(N + 1):
            acc[i] += c * term[i]
    return acc


def K4_at_1mp_series(g, N):
    """sum (1-p)^n p^t  over rook animals, to order N."""
    acc = [Fraction(0)] * (N + 1)
    for (n, t), c in g.items():
        if t > N:
            continue
        term = poly_mul(one_minus_p_pow(n, N), p_pow(t, N), N)
        for i in range(N + 1):
            acc[i] += c * term[i]
    return acc


def min_perimeter_by_size(g):
    out = {}
    for (n, t) in g:
        out[n] = min(out.get(n, 10 ** 9), t)
    return out


def red_controls(rook_levels, king_levels):
    ok = True
    rc = [len(lv) for lv in rook_levels]
    kc = [len(lv) for lv in king_levels]
    good = rc == A001168[:len(rc)]
    print(f"RED  enumerator reproduces A001168 to n={len(rc)}  "
          f"{'OK' if good else 'FAILED ' + str(rc)}")
    ok &= good
    good = kc == A006770[:len(kc)]
    print(f"RED  enumerator reproduces A006770 to n={len(kc)}  "
          f"{'OK' if good else 'FAILED ' + str(kc)}")
    ok &= good
    a1 = canon([(0, 0)])
    good = (site_perimeter(a1, KING) == 8 and site_perimeter(a1, ROOK) == 4)
    print(f"RED  single cell has king perimeter 8, rook perimeter 4  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    # The convention control: pair king CONNECTIVITY with rook PERIMETER --
    # the reading results/matching-pair-convention.md corrected -- and the
    # relation must FAIL.  Without this the test cannot tell a right
    # convention from a wrong one.
    N = 4
    g8_wrong = {}
    for n, lv in enumerate(king_levels, start=1):
        for a in lv:
            t = site_perimeter(a, ROOK)      # deliberately the other lattice
            g8_wrong[(n, t)] = g8_wrong.get((n, t), 0) + 1
    g4_ok = gnt(rook_levels, ROOK)
    lhs = K8_series(g8_wrong, N)
    rhs4 = K4_at_1mp_series(g4_ok, N)
    diff = [lhs[i] - rhs4[i] for i in range(N + 1)]
    want = [Fraction(0), Fraction(1), Fraction(-4), Fraction(4), Fraction(-1)]
    good = diff != want
    print(f"RED  the cross-lattice convention (king connectivity, rook "
          f"perimeter) FAILS the relation  {'OK' if good else 'FAILED'}")
    ok &= good
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax-rook", type=int, default=12)
    ap.add_argument("--nmax-king", type=int, default=9)
    args = ap.parse_args()

    print("=" * 70)
    print("Sykes-Essam for the king/rook matching pair, to the reachable order")
    print("=" * 70)

    rook_levels = fixed_animals(args.nmax_rook, ROOK)
    king_levels = fixed_animals(args.nmax_king, KING)
    g4 = gnt(rook_levels, ROOK)
    g8 = gnt(king_levels, KING)

    print(f"enumerated: rook to n={args.nmax_rook}, king to n={args.nmax_king}")
    print()

    print("--- 1. Where the rook side's grading bites ---")
    mp = min_perimeter_by_size(g4)
    print(f"  {'n':>3}  {'min t_4':>7}   -- the smallest rook site-perimeter "
          f"at each size")
    for n in sorted(mp):
        print(f"  {n:>3}  {mp[n]:>7}")
    # An order-N test needs EVERY rook animal with t <= N.  The largest N for
    # which the enumeration is complete is the smallest min-perimeter among
    # sizes NOT enumerated, minus one.
    # min t_4 is non-decreasing in n over this range; the first omitted size
    # bounds what is complete.
    bound = mp[args.nmax_rook]
    print(f"\n  every rook animal with t_4 <= {bound - 1} is enumerated "
          f"(size {args.nmax_rook + 1} already has min t_4 >= {bound}),")
    print(f"  so the relation is testable to order p^{bound - 1} "
          f"from n <= {args.nmax_rook}.")
    print()

    # The testable order is the MINIMUM of the two sides' completeness:
    # the rook side is complete to order bound-1, the king side to n_max_king.
    N_rook = bound - 1
    N = min(N_rook, args.nmax_king)
    print(f"  king side is complete to order p^{args.nmax_king}; "
          f"the test order is min({N_rook}, {args.nmax_king}) = {N}.")
    print()
    print(f"--- 2. The relation at order p^{N} ---")
    k8 = K8_series(g8, N)
    k4 = K4_at_1mp_series(g4, N)
    lhs = [k8[i] - k4[i] for i in range(N + 1)]
    rhs = [Fraction(0), Fraction(1), Fraction(-4), Fraction(4), Fraction(-1)]
    rhs += [Fraction(0)] * (N + 1 - len(rhs))
    print(f"  {'ord':>4}  {'K_8 - K_4(1-p)':>18}  {'predicted':>10}  match")
    agree = 0
    for i in range(N + 1):
        m = (lhs[i] == rhs[i])
        agree += m
        if i <= min(N, 12):
            print(f"  {i:>4}  {str(lhs[i]):>18}  {str(rhs[i]):>10}  "
                  f"{'YES' if m else 'no'}")
    print(f"\n  orders matching: {agree}/{N + 1}")
    print()
    print(f"  For the record, the first TRUNCATED order: at p^"
          f"{args.nmax_king + 1} the residual is exactly -a({args.nmax_king+1})"
          f" of A006770, the missing king term, which is what a purely")
    print(f"  truncation-driven failure looks like.")
    k8x = K8_series(g8, args.nmax_king + 1)
    k4x = K4_at_1mp_series(g4, args.nmax_king + 1)
    resid = k8x[args.nmax_king + 1] - k4x[args.nmax_king + 1]
    print(f"    residual at p^{args.nmax_king+1} = {resid}   "
          f"(-A006770({args.nmax_king+1}) = "
          f"{-A006770[args.nmax_king] if args.nmax_king < len(A006770) else 'n/a'})")
    print()

    print("--- 3. What a deeper test would cost ---")
    # invert min-perimeter growth: fit t_min(n) ~ c*sqrt(n)
    ns = sorted(mp)
    big = [n for n in ns if n >= 4]
    import math
    cs = [mp[n] / math.sqrt(n) for n in big]
    c = sum(cs) / len(cs)
    print(f"  min t_4 grows about {c:.2f}*sqrt(n) over the measured range")
    for target in (10, 16, 20, 30):
        n_needed = int((target / c) ** 2)
        print(f"  order p^{target:<3} needs every rook animal with t_4 <= "
              f"{target}, i.e. sizes up to about n = {n_needed}")
    print()

    print("--- 4. Does the perimeter-DEFECT data supply that? ---")
    print("  Defect grading is k = pmax(n) - p, so the banked k <= 6 series")
    print("  cover the LARGEST perimeters at each size.  The relation needs")
    print("  the SMALLEST.  Measured, at each size enumerated here:")
    print(f"  {'n':>3}  {'min t_4':>7}  {'max t_4':>7}  "
          f"{'defect k<=6 reaches':>20}")
    mx = {}
    for (n, t) in g4:
        mx[n] = max(mx.get(n, 0), t)
    for n in sorted(mp):
        print(f"  {n:>3}  {mp[n]:>7}  {mx[n]:>7}  "
              f"{'t >= ' + str(mx[n] - 6):>20}")
    print()

    print("--- RED controls ---")
    if not red_controls(rook_levels, king_levels):
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
