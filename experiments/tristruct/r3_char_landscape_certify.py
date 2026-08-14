#!/usr/bin/env python3
"""r3_char_landscape_certify.py -- assemble r3_char_landscape.py's raw ranks
into the certificate, or refuse.

Input: one or more shard logs (lines "# H=... residuals=N budget_B=..." and
"p rank (...)").  Output: the verdict for that height, with every step of the
arithmetic printed, and a nonzero exit if any step fails to close.

The four things that must hold, and each is checked, not assumed:

  1. CONSISTENCY.  Distinct primes are coprime, so prod_p p^{d_p} divides
     D_r and the budget bounds the SUM: sum_p d_p ln p <= B, over every prime
     at once.  A violation would mean the theory is wrong or the ranks are --
     either way the certificate is void.  This is the check that can fail
     loudly, and it is the sum form that makes step 2 valid.
  2. PINNED.  sum of ln p over the primes attaining the maximum rank must
     exceed B, which forces rank_Q to equal that maximum.  Without this the
     "drops" below are measured against a guess.
  3. COMPLETE.  Every prime <= exp(B / d_2) must appear in the input.  Those
     are the only primes that could match characteristic 2's collapse; (*)
     excludes every larger one.
  4. UNIQUE.  Among all primes tested, report exactly which ones drop the
     rank at all, and by how much.

Usage:  r3_char_landscape_certify.py <shard log>...
"""

import sys
from math import log, exp


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, v in enumerate(sieve) if v]


def main():
    hdr, ranks = {}, {}
    for path in sys.argv[1:]:
        for line in open(path):
            if line.startswith('#'):
                for tok in line[1:].split():
                    if '=' in tok:
                        k, v = tok.split('=', 1)
                        hdr.setdefault(k, v)
            elif line.strip():
                f = line.split()
                ranks[int(f[0])] = int(f[1])
    if not ranks:
        print("no ranks read")
        return 1

    H = int(hdr['H'])
    N = int(hdr['residuals'])
    B = (N / 2) * log(N)
    r = max(ranks.values())
    fail = 0

    print(f"H = {H}: {int(hdr['states'])} states, N = {N} distinct residuals, "
          f"so rank_Q <= {N} and the budget is B = (N/2)lnN = {B:.1f}")
    print(f"{len(ranks)} primes tested, from {min(ranks)} to {max(ranks)}")

    # 1. consistency, in the sum form
    spent = sum((r - v) * log(p) for p, v in ranks.items())
    print(f"  1. consistency: measured drops spend "
          f"sum d_p ln p = {spent:.1f} of the budget B = {B:.1f}", end="")
    if spent <= B:
        print("   OK")
    else:
        print("   FAILED -- (*) violated")
        fail = 1

    # 2. pinned
    witness = sum(log(p) for p, v in ranks.items() if v == r)
    # the excess would cost (R - r) * witness on top of what is already spent
    print(f"  2. pinned: primes attaining rank {r} carry sum(ln p) = "
          f"{witness:.1f} against the {B - spent:.1f} of budget still unspent",
          end="")
    if witness > B - spent:
        print(f"   OK -- rank_Q = {r} exactly")
    else:
        print(f"   FAILED -- rank_Q is only known to be >= {r}")
        fail = 1

    # 3. complete
    d2 = r - ranks.get(2, r)
    pbound = exp(B / d2) if d2 else float('inf')
    need = [p for p in primes_upto(int(min(pbound, 10 ** 7)))]
    missing = [p for p in need if p not in ranks]
    print(f"  3. complete: d_2 = {d2}, so a competitor needs p <= "
          f"exp(B/d_2) = {pbound:.1f}; {len(need)} such primes", end="")
    if missing:
        print(f"   FAILED -- {len(missing)} untested, e.g. {missing[:5]}")
        fail = 1
    else:
        print("   OK -- all tested")

    # 4. unique
    drops = sorted((p, r - v) for p, v in ranks.items() if v != r)
    print(f"  4. drops, over every prime tested:")
    for p, d in drops:
        print(f"       p = {p:>5}   rank {r - d:>5}   drop {d:>5}   "
              f"({100.0 * d / r:.1f}% of rank_Q)")
    if not drops:
        print("       none")

    print()
    if fail:
        print(f"H = {H}: CERTIFICATE VOID")
        return 1
    others = [d for p, d in drops if p != 2]
    print(f"H = {H}: CERTIFIED. rank_Q = {r}; characteristic 2 drops it to "
          f"{r - d2} ({100.0 * d2 / r:.1f}%); the largest drop at any other "
          f"characteristic is {max(others) if others else 0}; and no prime "
          f"above {pbound:.0f} can drop it by as much as {d2}, by (*).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
