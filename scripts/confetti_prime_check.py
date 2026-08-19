#!/usr/bin/env python3
"""Early single-prime check on a Confetti residue row, before all 5 land.

For each n with a banked T(n,H) in the incumbent triangle, predict
    C_H(n) = T(n,H) + 2 C_{H-1}(n) - C_{H-2}(n)   (mod p)
and compare against the measured residue.  Necessary condition only: it does
not test the CRT reconstruction and is blind to errors that are multiples
of p.  The decisive check remains the held-out prime in
scripts/dalby_confetti_h18.sh.

Usage: confetti_prime_check.py H p C_H.p<p>.out C_{H-1}.out C_{H-2}.out triangle.txt
Exits 2 on any mismatch or on zero cells compared (fail-closed).
"""
import sys


def rows(path):
    d = {}
    for line in open(path):
        n, v = line.split()
        d[int(n)] = int(v)
    return d


def main(argv):
    if len(argv) != 7:
        print(__doc__, file=sys.stderr)
        return 2
    H, p = int(argv[1]), int(argv[2])
    res, Cm1, Cm2 = rows(argv[3]), rows(argv[4]), rows(argv[5])

    want = {}
    for line in open(argv[6]):
        if line.startswith('#'):
            continue
        n, h, v = line.split()
        if int(h) == H:
            want[int(n)] = int(v)

    match = mismatch = 0
    for n in sorted(want):
        if not (n in res and n in Cm1 and n in Cm2):
            continue
        pred = (want[n] + 2 * Cm1[n] - Cm2[n]) % p
        if pred == res[n] % p:
            match += 1
        else:
            mismatch += 1
            print(f"MISMATCH n={n}: predict {pred} measured {res[n] % p}")

    print(f"C_{H} mod {p} vs incumbent triangle: {match} match, {mismatch} mismatch")
    if mismatch or match == 0:
        print("FAIL" if mismatch else "FAIL zero_cells_compared")
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
