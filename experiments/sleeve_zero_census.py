#!/usr/bin/env python3
"""Sleeve-zero census: excess 3-adic valuation in the diagonal band.

The diagonal law gives T(n, n-k) = P_k(n) * 3^(n-1-3k) for n >= 2k+1.  Left of
the spine the exponent is negative: the cell carries a forced deficit
d = 3k+1-n >= 1, so integrality forces v3(P_k(n)) >= d.  GENERICALLY equality
holds (the cell is a unit mod 3, T(n,n-k) != 0 mod 3); a SLEEVE ZERO is a cell
with T(n,n-k) == 0 mod 3, i.e. excess divisibility v3(P_k(n)) > d.  Note

    v3(P_k(n)) = v3(T(n, n-k)) + d

so the census is exact from the banked triangle alone -- it does not need the
fitted P_k (which are pinned only to k <= 17).

Sleeve of row n: k from floor((n-1)/3)+1 (first k with d >= 1) up to the law's
diagonal reach k_max(n) = floor((n-1)/2).

Run: python3 experiments/sleeve_zero_census.py [nmax]
Doc: results/arithmetic-structure.md, "Row reading ... and the sleeve zeros".
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def v3(x):
    v = 0
    while x and x % 3 == 0:
        x //= 3
        v += 1
    return v


def main():
    T = {}
    NMAX = 0
    with open(os.path.join(ROOT, "results", "triangle.txt")) as fh:
        for line in fh:
            p = line.split()
            if len(p) == 3 and p[0].isdigit():
                n, H, val = int(p[0]), int(p[1]), int(p[2])
                T[(n, H)] = val
                NMAX = max(NMAX, n)
    if len(sys.argv) > 1:
        NMAX = min(NMAX, int(sys.argv[1]))
    print(f"sleeve-zero census from results/triangle.txt, n <= {NMAX}")
    print(" n | sleeve k-range | zeros (k: d -> v3(P_k(n))) | #  runs")

    first = {}
    for n in range(4, NMAX + 1):
        klo, khi = (n - 1) // 3 + 1, (n - 1) // 2
        if klo > khi:
            continue
        zeros = []
        for k in range(klo, khi + 1):
            d = 3 * k + 1 - n
            val = T[(n, n - k)]
            if val % 3 == 0:
                zeros.append((k, d, v3(val) + d))
        # longest run of consecutive k among the zeros
        run = best = 0
        prev = None
        for k, _, _ in zeros:
            run = run + 1 if prev is not None and k == prev + 1 else 1
            best = max(best, run)
            prev = k
        desc = "  ".join(f"k={k}: {d}->{v}" for k, d, v in zeros)
        print(f"{n:2d} | k={klo}..{khi:<5d}| {desc:<44s}| {len(zeros)}  run{best}")
        if len(zeros) >= 2 and "two" not in first:
            first["two"] = n
        if best >= 2 and "adjacent" not in first:
            first["adjacent"] = n
        if len(zeros) >= 3 and "three" not in first:
            first["three"] = n
        if best >= 3 and "three-in-a-row" not in first:
            first["three-in-a-row"] = n
        if len(zeros) >= 4 and "four" not in first:
            first["four"] = n
        if best >= 4 and "four-in-a-row" not in first:
            first["four-in-a-row"] = n

    print("\nfirsts:")
    for key in ("two", "adjacent", "three", "three-in-a-row", "four", "four-in-a-row"):
        print(f"  first {key:15s}: n={first[key]}" if key in first
              else f"  first {key:15s}: none up to n={NMAX}")


if __name__ == "__main__":
    main()
