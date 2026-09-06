#!/usr/bin/env python3
"""B1 of docs/publication.md: staircase animals are supermultiplicative.

results/subclasses.md Lemma 3 paid a factor (i+j) for the column-join,
because it recovered the pair (X, Y) from the join plus the index of X's last
column. That index is not free information: column areas are positive, so the
prefix of columns of total area exactly i is unique, and at FIXED (i, j) the
join is already injective. This script measures the exact inequality

    M(i) M(j) <= M(i+j)

and the injectivity that proves it.

A staircase king animal (A225114) is a sequence of column intervals with both
boundaries nondecreasing; up to translation it is a height sequence
h_1..h_k >= 1 and offsets d_1..d_{k-1} = b_{j+1} - b_j with

    0 <= d_j <= h_j        (bottoms nondecreasing; king-adjacency of columns)
    h_{j+1} >= h_j - d_j   (tops nondecreasing: d_j >= h_j - h_{j+1})

Checks, in order:

  1. brute force over (h, d) reproduces the banked staircase series;
  2. the join X * Y with d = max(0, h_last(X) - h_first(Y)) lands in the class,
     is injective at fixed (i, j), and is inverted by "cut at cumulative area i";
  3. M(i) M(j) <= M(i+j) on every pair from the banked 700 terms;
  4. Fekete's lower bound mu >= sup_n M(n)^(1/n), reported at the best n.

RED controls, each of which must FAIL:

  * the stack counts P(n) (A001523, the outer blocks of Lemma 1) are NOT
    supermultiplicative -- P(2) P(20) > P(22) -- so check 3 is not vacuous;
  * the join with d = 0 always leaves the class, so check 2 is not vacuous;
  * the cut taken at cumulative area i+1 instead of i fails to invert.

Usage: python3 experiments/staircase_supermul.py [--brute 12] [--terms FILE]
"""
import argparse
import os
import sys
from decimal import Decimal, getcontext
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS = os.path.join(ROOT, "results", "mk_stair_terms_n700.txt")


def animals(n):
    """Every staircase animal of area n, as (heights, offsets), b_1 = 0."""
    out = []

    def rec(rem, hs, ds):
        if rem == 0:
            out.append((tuple(hs), tuple(ds)))
            return
        prev = hs[-1] if hs else None
        for h in range(1, rem + 1):
            if prev is None:
                hs.append(h)
                rec(rem - h, hs, ds)
                hs.pop()
                continue
            lo = max(0, prev - h)
            for d in range(lo, prev + 1):
                hs.append(h)
                ds.append(d)
                rec(rem - h, hs, ds)
                ds.pop()
                hs.pop()
    rec(n, [], [])
    return out


def is_animal(hs, ds):
    """Membership test, independent of how the sequence was built."""
    if len(ds) != len(hs) - 1 or any(h < 1 for h in hs):
        return False
    return all(0 <= d <= hs[j] and hs[j + 1] >= hs[j] - d for j, d in enumerate(ds))


def join(x, y, rule="max"):
    """Column-join: translate Y so the junction step is legal, then concatenate."""
    (hx, dx), (hy, dy) = x, y
    h, hp = hx[-1], hy[0]
    d = max(0, h - hp) if rule == "max" else 0
    return hx + hy, dx + (d,) + dy


def cut(z, i):
    """Recover the pair from the join, by the prefix of columns of area i."""
    hs, ds = z
    total = 0
    for k, h in enumerate(hs):
        total += h
        if total == i:
            return (hs[:k + 1], ds[:k]), (hs[k + 1:], ds[k + 1:])
    return None


def stacks(nmax):
    """P(n) = A001523, weakly unimodal compositions -- the RED control series."""
    @lru_cache(maxsize=None)
    def rec(rem, first):
        total = 1 if rem == first else 0
        for nxt in range(1, first + 1):
            if rem - first >= nxt:
                total += (first - nxt + 1) * rec(rem - first, nxt)
        return total

    out = [1] + [sum(rec(n, h) for h in range(1, n + 1)) for n in range(1, nmax + 1)]
    rec.cache_clear()
    return out


def banked(path):
    """The banked staircase series, 1-indexed with M(0) = 1."""
    out = [1]
    with open(path) as fh:
        for line in fh:
            if line.strip():
                n, v = line.split()
                assert int(n) == len(out), f"{path}: expected n={len(out)}, got {n}"
                out.append(int(v))
    return out


def supermul_violations(seq, nmax):
    """Pairs with f(i) f(j) > f(i+j), i, j >= 1."""
    bad = []
    for i in range(1, nmax + 1):
        for j in range(i, nmax + 1 - i):
            if seq[i] * seq[j] > seq[i + j]:
                bad.append((i, j))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brute", type=int, default=12,
                    help="largest area enumerated cell by cell (default 12)")
    ap.add_argument("--terms", default=TERMS, help="banked staircase series")
    args = ap.parse_args()
    if args.brute < 4:
        ap.error("--brute must be at least 4 to reach a nontrivial join")

    M = banked(args.terms)
    nmax = len(M) - 1
    print(f"banked staircase series: {nmax} terms from {os.path.relpath(args.terms, ROOT)}")

    # 1. the representation reproduces the banked series
    pool = {n: animals(n) for n in range(1, args.brute + 1)}
    for n in range(1, args.brute + 1):
        got, want = len(pool[n]), M[n]
        assert got == want, f"brute force M({n}) = {got}, banked {want}"
        assert all(is_animal(*z) for z in pool[n]), f"n={n}: built a non-animal"
    print(f"1. brute force over (h, d) reproduces M(1..{args.brute}) = "
          f"{', '.join(str(M[n]) for n in range(1, min(args.brute, 6) + 1))}, ...  OK")

    # 2. the join lands in the class, injects at fixed (i, j), and is cut-invertible
    pairs = 0
    for i in range(1, args.brute):
        for j in range(1, args.brute + 1 - i):
            seen = set()
            for x in pool[i]:
                for y in pool[j]:
                    z = join(x, y)
                    assert is_animal(*z), f"join left the class at ({i},{j})"
                    assert sum(z[0]) == i + j, f"join lost area at ({i},{j})"
                    assert cut(z, i) == (x, y), f"cut failed to invert at ({i},{j})"
                    seen.add(z)
                    pairs += 1
            assert len(seen) == len(pool[i]) * len(pool[j]), \
                f"join not injective at ({i},{j}): {len(seen)} images"
            assert len(seen) <= M[i + j], f"more images than animals at ({i},{j})"
    print(f"2. {pairs} joins over i+j <= {args.brute}: in class, injective at fixed "
          f"(i,j), inverted by the area-i cut  OK")

    # RED controls for check 2
    escapes = any(not is_animal(*join(a, b, rule="zero"))
                  for i in range(1, args.brute) for j in range(1, args.brute + 1 - i)
                  for a in pool[i] for b in pool[j])
    assert escapes, "RED control alive: the d=0 join never left the class"
    miscut = any(cut(join(a, b), i + 1) != (a, b)
                 for i in range(1, args.brute) for j in range(1, args.brute + 1 - i)
                 for a in pool[i] for b in pool[j])
    assert miscut, "RED control alive: cutting at area i+1 still inverted"
    print("   RED: d=0 join leaves the class; the area-(i+1) cut fails to invert  OK")

    # 3. the inequality on the full banked series
    bad = supermul_violations(M, nmax)
    print(f"3. M(i) M(j) <= M(i+j): {len(bad)} violations over all i+j <= {nmax}"
          f"  {'OK' if not bad else 'FAIL ' + str(bad[:5])}")
    assert not bad, bad[:5]

    P = stacks(min(nmax, 60))
    badp = supermul_violations(P, min(nmax, 60))
    assert badp, "RED control alive: the stack counts were supermultiplicative"
    i, j = badp[0]
    print(f"   RED: stacks P(n) = A001523 violate it, first at (i,j) = ({i},{j}): "
          f"{P[i]}*{P[j]} > {P[i + j]}  OK")

    # 4. Fekete: the limit is the sup, so every term is a certified lower bound
    getcontext().prec = 50
    roots = [(Decimal(M[n]).ln() / n, n) for n in range(1, nmax + 1)]
    best_root, best_n = max(roots)
    print(f"4. Fekete: mu = sup_n M(n)^(1/n) >= M({best_n})^(1/{best_n}) = "
          f"{best_root.exp():.20f}")
    assert best_root.exp() < Decimal("3.128943269730886253"), "bound exceeds banked mu"
    return 0


if __name__ == "__main__":
    sys.exit(main())
