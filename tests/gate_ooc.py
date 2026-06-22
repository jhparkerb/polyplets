#!/usr/bin/env python3
# Gate for Phase 4 (out-of-core sweep): db and next live as S disk partitions, only ~one
# partition resident at a time (RAM ~ peak/S, reach bounded by disk not RAM). Two checks:
# (1) out-of-core a(n) == exact A006770; (2) the result is INDEPENDENT of the partition
# count S (a strong correctness signal -- the spill+reduce must be associative/complete).
import os
import subprocess
import sys

N = 10
A006770 = {1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941,
           9: 940982, 10: 6053180}


def rows(args):
    out = subprocess.run(args, capture_output=True, text=True)
    return {int(n): int(c) for n, c in (ln.split() for ln in out.stdout.splitlines())}


def main():
    subprocess.run(
        ["c++", "-std=c++20", "-O3", "-Icpp", "cpp/tma_ooc_test.cpp",
         "-o", "build/tma_ooc_test"], check=True)
    os.makedirs("build/ooc_gate", exist_ok=True)
    s4 = rows(["build/tma_ooc_test", str(N), "4", "build/ooc_gate"])
    s16 = rows(["build/tma_ooc_test", str(N), "16", "build/ooc_gate"])
    bad = [n for n in range(1, N + 1) if s4.get(n) != A006770[n]]
    sindep = all(s4.get(n) == s16.get(n) for n in range(1, N + 1))
    ok = (not bad) and sindep
    print(f"  out-of-core a(n) == exact A006770, n=1..{N}: "
          f"{'OK' if not bad else 'MISMATCH ' + str(bad)}")
    print(f"  S-independent (S=4 == S=16): {'OK' if sindep else 'MISMATCH'}")
    print("GATE OOC:", "GREEN" if ok else "RED")
    sys.exit(0 if ok else 1)


main()
