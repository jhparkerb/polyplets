#!/usr/bin/env python3
# CRT-combine step for the R1xR3(xB) reach driver. Reads the per-(H,p) mod-p sweep
# outputs ({DIR}/rows_p{p}_H*.txt, each line "n B_H(n) mod p"), sums over heights H to
# get a(n) mod p for each prime p, then CRTs across the primes to recover exact a(n).
# Named on-disk (not a heredoc) so the combine is traceable and re-runnable.
#
# USAGE: crt_combine.py DIR N p1 p2 p3...
import glob
import sys
from functools import reduce

d, N = sys.argv[1], int(sys.argv[2])
primes = [int(x) for x in sys.argv[3:]]


def crt(rs, ms):
    M = reduce(lambda a, b: a * b, ms)
    x = 0
    for r, m in zip(rs, ms):
        Mi = M // m
        x += r * Mi * pow(Mi, -1, m)
    return x % M


amod = {p: [0] * (N + 1) for p in primes}
for p in primes:
    for path in glob.glob(f"{d}/rows_p{p}_H*.txt"):
        for ln in open(path):
            x = ln.split()
            if len(x) == 2:
                n = int(x[0])
                amod[p][n] = (amod[p][n] + int(x[1])) % p

for n in range(1, N + 1):
    print(n, crt([amod[p][n] for p in primes], primes))
