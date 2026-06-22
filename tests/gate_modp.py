#!/usr/bin/env python3
# Gate for R3 (u32 mod-p plain sweep). CRT of sum_H B_H(n) mod p_i over several
# ~31-bit primes must equal the exact a(n) from build/tma -- tested both unfolded
# and with --fold (the R1xR3 composition). Also reports the per-state memory win.
import subprocess
import sys

# Small primes whose product (6.4e13) >> a(12) (2.6e8) but each < a(12), so the
# CRT genuinely recombines reduced residues (not a no-op). The u32 storage win is
# independent of prime size; reach deployment uses ~31-bit primes (fewer needed).
N = 12
PRIMES = [40009, 40013, 40031]


def crt(residues, mods):
    x, M = 0, 1
    for a, m in zip(residues, mods):
        g = pow(M % m, -1, m)            # M coprime to m (distinct primes)
        x += M * (((a - x) * g) % m)
        M *= m
    return x % M


def rows(args):
    out = subprocess.run(args, capture_output=True, text=True)
    return {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}


def main():
    subprocess.run(
        ["c++", "-std=c++20", "-O3", "-pthread", "cpp/tma_modp_test.cpp",
         "-o", "build/tma_modp_test"], check=True)
    exact = rows(["build/tma", "square8", str(N)])
    ok = True
    for fold in (False, True):
        res = [rows(["build/tma_modp_test", str(N), str(p)] + (["--fold"] if fold else []))
               for p in PRIMES]
        bad = [n for n in range(1, N + 1)
               if crt([res[i][n] for i in range(len(PRIMES))], PRIMES) != exact[n]]
        if bad:
            print(f"  fold={fold}: MISMATCH at n={bad}"); ok = False
        else:
            print(f"  fold={fold}: CRT of {len(PRIMES)} primes == exact a(n), n=1..{N}  OK")
    print("GATE MODP:", "GREEN" if ok else "RED")
    sys.exit(0 if ok else 1)


main()
