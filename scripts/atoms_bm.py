#!/usr/bin/env python3
# atoms_bm.py — scaling-exploration probe (Teammate B): minimal LFSR order of
# C_H(n) mod p, i.e. the atom degree q_H = the Hankel rank of the strip series.
#
# Purpose: extend the measured atom-degree sequence 1,2,4,9,29,68 (results/
#   triangle-structure.md) to H=7,8(,9). q_H lower-bounds the dimension of ANY
#   weighted-automaton / linear-scan engine for C_H (up to /H from the area
#   marking) and upper-bounds the dimension of a compressed exact linear engine
#   — its growth ratio is the scaling number of docs/scaling-exploration-brief.md.
# Input: results/atoms_ext/C<H>.p<i>.txt from `build/cutcount_b1 --modp`.
# Checks: (a) first 40 terms == banked C_H mod p (banked = sum over
#   results/ns_a40/perheight); (b) BM order run on a prefix, holdout-verified on
#   the remaining terms; (c) two primes must agree.
# Command: python3 scripts/atoms_bm.py <H> <p> <file> [<p2> <file2>]
# Cost: seconds. Machine: gympie.
import sys, os

def bm(seq, p):
    """Berlekamp-Massey over GF(p): returns minimal LFSR length L."""
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for i, s in enumerate(seq):
        d = s
        for j in range(1, L + 1):
            d = (d + C[j] * seq[i - j]) % p
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coef * B[j]) % p
            L, B, b, m = i + 1 - L, T, d, 1
        else:
            coef = d * pow(b, p - 2, p) % p
            C = C + [0] * (len(B) + m - len(C))
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coef * B[j]) % p
            m += 1
    return L, C

def check_predicts(seq, C, L, p, start):
    for i in range(start, len(seq)):
        d = seq[i]
        for j in range(1, L + 1):
            d = (d + C[j] * seq[i - j]) % p
        if d % p:
            return i
    return None

def banked_CH(H, p):
    tri = {}
    for h in range(1, H + 1):
        path = f"results/ns_a40/perheight/h{h}.out"
        with open(path) as f:
            for line in f:
                a = line.split()
                if len(a) == 2:
                    tri[(int(a[0]), h)] = int(a[1]) % p
    out = []
    for n in range(1, 41):
        out.append(sum((H - h + 1) * tri.get((n, h), 0) for h in range(1, H + 1)) % p)
    return out

def load(path):
    return [int(l.split()[1]) for l in open(path)]

def analyze(H, p, path):
    seq = load(path)
    bk = banked_CH(H, p)
    agree = all(seq[i] % p == bk[i] for i in range(min(40, len(seq))))
    print(f"H={H} p={p}: n<=40 vs banked: {'OK' if agree else 'MISMATCH'}")
    if not agree:
        sys.exit(2)
    # BM on a prefix, holdout on the rest
    cut = int(len(seq) * 0.75)
    L, C = bm(seq[:cut], p)
    bad = check_predicts(seq, C, L, p, cut)
    print(f"H={H} p={p}: BM order on {cut} terms = {L}; holdout on remaining "
          f"{len(seq)-cut} terms: {'OK' if bad is None else f'FAILS at n={bad+1}'}")
    if bad is not None:
        print(f"  (order not yet converged — need more terms)")
        return None
    return L

if __name__ == "__main__":
    H = int(sys.argv[1])
    L1 = analyze(H, int(sys.argv[2]), sys.argv[3])
    if len(sys.argv) > 5:
        L2 = analyze(H, int(sys.argv[4]), sys.argv[5])
        if L1 is not None and L2 is not None:
            print(f"H={H}: primes {'AGREE' if L1==L2 else 'DISAGREE'}: q_{H} = {L1}")
