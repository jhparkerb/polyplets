#!/usr/bin/env python3
# CRT-combine step for the R1xR3(xB) reach driver. Reads the per-(H,p) mod-p sweep
# outputs ({DIR}/rows_p{p}_H{H}.txt, each line "n B_H(n) mod p"), sums over heights H to
# get a(n) mod p for each prime p, then CRTs across the primes to recover exact a(n).
#
# INTEGRITY GATE (hardened): a complete sweep emits exactly one line per n=1..N with value
# in [0,p). Before combining, EVERY (H,p) output is validated to be present and complete;
# a missing / empty / truncated / duplicated / out-of-range file aborts non-zero. This bans
# the failure mode that once produced a wrong a(22): a crashed or raced sweep being
# silently summed as a zero. crt_combine NEVER trusts a partial result.
#
# USAGE: crt_combine.py DIR N p1 p2 p3...
import os
import sys
from functools import reduce

d, N = sys.argv[1], int(sys.argv[2])
primes = [int(x) for x in sys.argv[3:]]


def die(msg):
    sys.stderr.write(f"crt_combine: FATAL: {msg}\n")
    sys.exit(1)


def crt(rs, ms):
    M = reduce(lambda a, b: a * b, ms)
    x = 0
    for r, m in zip(rs, ms):
        Mi = M // m
        x += r * Mi * pow(Mi, -1, m)
    return x % M


# Validate + load every (H,p) sweep before any combining.
amod = {p: [0] * (N + 1) for p in primes}
for p in primes:
    for H in range(1, N + 1):
        path = os.path.join(d, f"rows_p{p}_H{H}.txt")
        if not os.path.exists(path):
            die(f"missing sweep output {path} (H={H} p={p} never completed)")
        seen = {}
        with open(path) as f:
            for ln in f:
                x = ln.split()
                if not x:
                    continue
                if len(x) != 2:
                    die(f"{path}: malformed line {ln.rstrip()!r}")
                n, v = int(x[0]), int(x[1])
                if n in seen:
                    die(f"{path}: duplicate n={n} (corruption / concurrent run on same dir)")
                if not (1 <= n <= N):
                    die(f"{path}: n={n} out of range 1..{N}")
                if not (0 <= v < p):
                    die(f"{path}: value {v} out of range for prime {p}")
                seen[n] = v
        missing = [n for n in range(1, N + 1) if n not in seen]
        if missing:
            die(f"{path}: incomplete (crashed/truncated), missing n={missing}")
        for n in range(1, N + 1):
            amod[p][n] = (amod[p][n] + seen[n]) % p

for n in range(1, N + 1):
    print(n, crt([amod[p][n] for p in primes], primes))
