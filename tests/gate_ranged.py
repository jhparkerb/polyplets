#!/usr/bin/env python3
# Gate for R2 (ranged counts-row sweep). The ranged two-pass DP stores each row only
# on its support [minSize, maxn]; the omitted entries are zero, so totals must match
# the exact engine byte-for-byte. Also reports the peak store-bytes ratio (the win).
import subprocess
import sys

N = 13


def rows(args):
    out = subprocess.run(args, capture_output=True, text=True)
    return {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}


def main():
    subprocess.run(
        ["c++", "-std=c++20", "-O3", "-pthread", "cpp/tma_ranged_test.cpp",
         "-o", "build/tma_ranged_test"], check=True)
    exact = rows(["build/tma", "square8", str(N)])
    out = subprocess.run(["build/tma_ranged_test", str(N)], capture_output=True, text=True)
    ranged = {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}
    bad = [n for n in range(1, N + 1) if ranged.get(n) != exact.get(n)]
    ok = not bad
    if bad:
        print(f"  MISMATCH at n={bad}")
    else:
        print(f"  ranged a(n) == exact a(n), n=1..{N}  OK")
    # peak memory line (informational)
    for ln in out.stderr.splitlines():
        if "peak_" in ln:
            print("  " + ln.strip())
    print("GATE RANGED:", "GREEN" if ok else "RED")
    sys.exit(0 if ok else 1)


main()
