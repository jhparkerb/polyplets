#!/usr/bin/env python3
# Gate for R3 (u32 mod-p plain sweep). CRT of sum_H B_H(n) mod p_i over several
# ~31-bit primes must equal the exact a(n) from build/tma -- tested both unfolded
# and with --fold (the R1xR3 composition). Also reports the per-state memory win.
import sys

from common import require_binary, run

# Small primes whose product (6.4e13) >> a(n) but each is far below it, so the
# CRT genuinely recombines reduced residues (not a no-op). The u32 storage win is
# independent of prime size; reach deployment uses ~31-bit primes (fewer needed).
#
# Depth: this gate is seven square8 sweeps -- three primes x {plain, --fold},
# plus the exact build/tma run -- and each further n costs ~4x. What it asserts
# is an IDENTITY (CRT of the residues == the exact count), which holds at every
# n, so the push tier runs it at n=11: a(11) = 39,299,408, still four orders
# above the primes and seven below their product. --deep restores n=12.
N = 12 if "--deep" in sys.argv else 11
PRIMES = [40009, 40013, 40031]


def crt(residues, mods):
    x, M = 0, 1
    for a, m in zip(residues, mods):
        g = pow(M % m, -1, m)            # M coprime to m (distinct primes)
        x += M * (((a - x) * g) % m)
        M *= m
    return x % M


def rows(args):
    # common.run raises on a non-zero exit.  Until 2026-09-05 this used
    # subprocess.run without checking, so an engine that printed its rows and
    # then died (an assert after the output, a failed final check) was GREEN
    # here (AUDIT-2026-09-02, gate hygiene).
    out = run(args[0], *args[1:])
    return {int(n): int(c) for n, c in (ln.split() for ln in out.splitlines())}


def main():
    # build/tma_modp_test is a make target (gate-modp depends on it). This used
    # to compile it here on every run; fail closed if it is missing rather than
    # rebuilding it behind make's back.
    if not require_binary("build/tma_modp_test", "build/tma_modp_test"):
        sys.exit(2)
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
