#!/usr/bin/env python3
# Gate for Phase 3.2 (blocked drain-and-free store). The blocked sweep frees each db
# hash-partition the instant it is drained, so the live peak is ~1× (next) not db+next
# (~2×). Totals must match the exact engine. NOTE the RSS win only shows once the
# partitions exceed the allocator's return-to-OS threshold (~N>=14); at tiny N the
# freed pages are pooled, not returned (1.03× @ N=13 vs 1.94× @ N=14).
import subprocess
import sys

N = 13


def rows(args):
    out = subprocess.run(args, capture_output=True, text=True)
    return {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}


def main():
    subprocess.run(
        ["c++", "-std=c++20", "-O3", "-pthread", "cpp/tma_blocked_test.cpp",
         "-o", "build/tma_blocked_test"], check=True)
    exact = rows(["build/tma", "square8", str(N)])
    blk = rows(["build/tma_blocked_test", str(N)])
    bad = [n for n in range(1, N + 1) if blk.get(n) != exact.get(n)]
    ok = not bad
    print(f"  blocked a(n) == exact, n=1..{N}: {'OK' if ok else 'MISMATCH ' + str(bad)}")
    print("GATE BLOCKED:", "GREEN" if ok else "RED")
    sys.exit(0 if ok else 1)


main()
