#!/usr/bin/env python3
"""r3_char_landscape.py -- is characteristic 2 the ONLY place the strip
functional collapses?

Coin Lift died at G2 (results/coin-lift-g2.md): lifting GF(2) to Z/4 or Z/8
buys nothing.  This asks the wider question that kill invites -- whether some
other characteristic, or some other ring, or some other auxiliary object, can
do what GF(2) does.  The answer is a floor plus a finite sweep; this computes
the sweep and the raw material for the certificate that closes it.

THE FLOOR.  Let f be the strip-counting functional at height H and M its
observability matrix over Z: rows the reachable states, columns the distinct
residuals a o delta_w.  The automaton is deterministic, so every residual is a
0/1 vector, there are finitely many, and they generate the Hankel column
module.  Write r = rank_Q(M) and d_p = r - rank_{F_p}(M).

  (T1) For any field F, rank_F(M) depends only on char F: M has entries in the
       prime field and rank is invariant under field extension.  So no
       extension of GF(2) beats GF(2) -- Biased Coin Flip's GF(2^k) buys
       probability, never dimension.

  (T2) Multiplicative grading is exactly rank-preserving.  The area-graded
       Hankel entry is t^|u| f(uv) t^|v|, so the graded matrix is D M D' with
       D, D' invertible diagonal: same rank over any ring where t is a unit.
       Coin Roll is free by theorem, and no weighting of that shape can help.

  (T3) For ANY commutative ring R with 1 != 0, any R-linear realization of f
       -- any weighted automaton, cut-and-count with any auxiliary group, any
       Coin-Flip-shaped scheme -- has dimension >= min over prime fields of
       rank(M).  Reduce modulo a maximal ideal m: the realization becomes one
       over the field R/m of the same dimension, and Hankel rank over a field
       is a floor on realization dimension.  With T1, the entire landscape of
       ring-linear methods is indexed by ONE parameter, the characteristic.

  (T4) Only finitely many characteristics can matter, and the bound is
       explicit.  If rank_{F_p} = r - d_p then at least d_p invariant factors
       of M are divisible by p, so p^{d_p} divides the r-th determinantal
       divisor D_r.  D_r divides every nonzero r x r minor, and Hadamard
       bounds any such minor of a 0/1 matrix with columns of length r by
       r^{r/2}.  Since r <= N (the residuals generate), for every prime p

             d_p * ln p  <=  (N/2) * ln N  =:  B                       (*)

       Summed over primes, (*) is a budget: every drop anywhere in the
       landscape is paid for out of the one number B.

Two consequences the certifier uses.  First, (*) PINS rank_Q rather than
assuming a big prime is generic: if every prime tested returns the same rank
v, a true rank_Q = R > v would drop by R - v at all of them, costing
(R - v) * sum(ln p), so R = v as soon as sum(ln p) > B.  Second, a prime
matching characteristic 2's drop needs d_p >= d_2, hence ln p <= B / d_2 --
and every prime below that is swept here by direct computation.  Below the
bound: measured.  Above it: excluded by (*).

Usage:  r3_char_landscape.py H [SHARD] [NSHARD]
Cost:   H=7 <1 s per prime, H=8 ~5 s, H=9 ~55 s (gympie).  Shard across cores;
        each shard repeats the automaton build (11 s at H=9) and prints raw
        "p rank" lines for r3_char_landscape_certify.py to assemble.
"""

import sys
import time
from math import log, ceil

import numpy as np

from r3_inv_rank_probe import build_automaton, motzkin
from r3_lift_snf_probe import module_generators, invariant_valuations


def distinct_residuals(delta, accept):
    """Exact count of distinct residuals a o delta_w.  They generate the
    Hankel column module, so rank_Q <= this -- which is what makes B a
    rigorous budget rather than an estimate off a measured rank."""
    n, na = delta.shape
    a = accept.astype(np.uint8)
    seen = {a.tobytes()}
    frontier = [a]
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=np.uint8)
                ok = d >= 0
                h[ok] = g[d[ok]]
                b = h.tobytes()
                if b not in seen:
                    seen.add(b)
                    nxt.append(h)
        frontier = nxt
    return len(seen)


def rank_mod(delta, accept, p):
    """rank over F_p, via the observability closure taken mod p."""
    return invariant_valuations(module_generators(delta, accept, 1, p), 1, p)[0]


def is_prime(m):
    if m < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if m % q == 0:
            return m == q
    d, s = m - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, m)
        if x in (1, m - 1):
            continue
        for _ in range(s - 1):
            x = x * x % m
            if x == m - 1:
                break
        else:
            return False
    return True


def primes_upto(n):
    sieve = [True] * (n + 1)
    sieve[0:2] = [False, False]
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = [False] * len(sieve[i * i::i])
    return [i for i, v in enumerate(sieve) if v]


def big_primes(k):
    """k primes just under 2^31, so p*p stays inside int64."""
    out, m = [], (1 << 31) - 1
    while len(out) < k:
        if is_prime(m):
            out.append(m)
        m -= 2
    return out


def plan(delta, accept, nres):
    """The prime list to test: every prime below B/d_2 (where a competitor to
    characteristic 2 would have to live), plus enough primes near 2^31 that
    sum(ln p) clears B and pins rank_Q."""
    B = (nres / 2) * log(nres)
    r0 = rank_mod(delta, accept, big_primes(1)[0])
    d2 = r0 - rank_mod(delta, accept, 2)
    pmax = int(2.718281828459045 ** (B / d2)) if d2 else 0
    small = primes_upto(min(pmax, 200000))
    need = ceil((B - sum(log(p) for p in small)) / log(2 ** 31)) + 2
    return B, r0, d2, pmax, small + big_primes(max(need, 3)), len(small), need


def main():
    H = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    shard = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    nshard = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    t0 = time.time()
    order, delta, accept, masks = build_automaton(H)
    assert len(order) == motzkin(H + 1) - 1, (H, len(order))
    nres = distinct_residuals(delta, accept)
    B, r0, d2, pmax, plist, nsmall, nbig = plan(delta, accept, nres)
    print(f"# H={H} states={len(order)} residuals={nres} budget_B={B:.1f} "
          f"working_r={r0} d_2={d2} sweep_pmax={pmax} nsmall={nsmall} "
          f"nbig={max(nbig,3)} build={time.time()-t0:.1f}s "
          f"shard={shard}/{nshard}", flush=True)

    for i, p in enumerate(plist):
        if i % nshard != shard:
            continue
        t = time.time()
        print(f"{p} {rank_mod(delta, accept, p)}   ({time.time()-t:.1f}s)",
              flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
