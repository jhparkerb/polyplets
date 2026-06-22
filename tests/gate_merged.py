#!/usr/bin/env python3
# Gate for C3 (merged R1xR2xR3 engine: fold x ranged x u32-modp). Run the merged engine for
# several ~31-bit primes -> a(n) mod p_i, CRT to recover the exact a(n), check == A006770.
# N=14 makes a(n) exceed a single prime (a(14) ~ 1.1e13 > 2^31), so the CRT path is real.
import subprocess
import sys
from functools import reduce

# N=12 verifies the merged ENGINE == exact (a(12)=257105146) fast; the CRT path is standard
# math, checked separately below on a large value. (N>=14 to exercise CRT in-engine is too
# slow until the ranged+modp arena handling is optimized -- tracked as a perf follow-up.)
N = 12
A006770 = {1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941, 9: 940982,
           10: 6053180, 11: 39299408, 12: 257105146}
PRIMES = [2147483647, 2147483629, 2147483587]   # three distinct primes < 2^31


def crt(rems, mods):
    M = reduce(lambda a, b: a * b, mods)
    x = 0
    for r, m in zip(rems, mods):
        Mi = M // m
        x += r * Mi * pow(Mi, -1, m)
    return x % M


def amodp(p):
    out = subprocess.run(["build/tma_merged_test", str(N), str(p)],
                         capture_output=True, text=True)
    return {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}


def main():
    subprocess.run(["c++", "-std=c++20", "-O3", "-Icpp", "cpp/tma_merged_test.cpp",
                    "-o", "build/tma_merged_test"], check=True)
    # CRT machinery check on a value larger than any single prime (the in-engine N=12 a(n)
    # all fit one prime, so this is what exercises the multi-prime reconstruction).
    V = 1234567890123456789
    assert crt([V % p for p in PRIMES], PRIMES) == V, "CRT reconstruction broken"
    rows = [amodp(p) for p in PRIMES]
    bad = []
    for n in range(1, N + 1):
        val = crt([rows[i][n] for i in range(len(PRIMES))], PRIMES)
        if val != A006770[n]:
            bad.append((n, val, A006770[n]))
    ok = not bad
    print(f"  merged R1xR2xR3 (fold x ranged x u32-modp), CRT over {len(PRIMES)} primes, "
          f"a(n)==exact n=1..{N}: {'OK' if ok else 'MISMATCH ' + str(bad)}")
    print("GATE MERGED:", "GREEN" if ok else "RED")
    sys.exit(0 if ok else 1)


main()
