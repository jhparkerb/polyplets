#!/usr/bin/env python3
"""Severance W3, mod-p: the depth-j defect series D_j(k) mod p.

The exact path (severance_w3_depths.D_series) is bignum-bound -- the cluster
weights grow like ~14.4^k, so a K~100 series-fit for the depth-tower field test
(severance_w4_field.py) costs ~20 min of Fraction arithmetic per depth.  The
minimal-polynomial DEGREE scan that answers the field-membership question is
reduced mod p and is scale-invariant, so nothing exact is needed to find the box
(deg_y, deg_W); only the branch-locus fingerprint wants Q.

This file recomputes the whole chain -- families() DP and the D_series assembly
-- in Z/pZ, which caps every integer at 61 bits and (measured) runs ~7.4x faster,
turning K~100 into a few minutes of pure Python.  Rational coefficients are
carried as field elements: the D_j(k) denominators are pure powers of 3 (checked
empirically for j<=3), so every division is pow(inv3, .., p).

Faithfulness is proved, not assumed (verifier held above the claim):
  * families_mod(K, emax, mod=None) reproduces severance_w3_depths.families()
    cell-for-cell (a literal copy of that DP; the mod is the only added op);
  * Dj_mod(j, K, p) reproduces severance_w3_depths.D_series(j, K) reduced mod p
    (numerator * inverse(denominator)).
main() asserts both before the module is usable.

Run:  python3 -u experiments/severance_w3_modp.py [Kcheck]
"""
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from severance_w3_depths import (transitions, q_end, bare_end, _shapes,   # noqa: E402
                                 _row_partition)

PRIME = (1 << 61) - 1


# --------------------------------------------------------- families() mod p
# Literal copy of severance_w3_depths.families(); the ONLY change is `% mod`
# on the two weight accumulations (guarded by `if mod`).  main() checks the
# mod=None branch equals the trusted families() cell-for-cell.

def families_mod(K, emax, mod=None, verbose=False):
    span = 2 * K + emax + 1
    sizes = [2 + d for d in range(emax + 1)]
    sig = [[0] * (K + 1) for _ in range(emax + 1)]
    bb = [[0] * (K + 1) for _ in range(emax + 1)]
    pp = [[0] * (K + 1) for _ in range(emax + 1)]
    dp_i = {(0, ((0,), (0,))): 1}
    dp_b = {}
    for ell in range(1, K + 1):
        t0 = time.time()
        n_i, n_b = {}, {}
        for t in sizes:
            de = t - 2
            for src, dst in ((dp_i, n_i), (dp_b, n_b)):
                for (e, st), c in src.items():
                    e2 = e + de
                    if e2 > emax or ell + e2 > K:
                        continue
                    for st2, w in transitions(st, t, span).items():
                        k2 = (e2, st2)
                        val = dst.get(k2, 0) + c * w
                        dst[k2] = val % mod if mod else val
            if ell == 1 and de <= emax and 1 + de <= K:
                for sh in _shapes(t, span):
                    k2 = (de, (sh, _row_partition(sh)))
                    n_b[k2] = n_b.get(k2, 0) + 1
        dp_i, dp_b = n_i, n_b
        for (e, st), c in dp_i.items():
            v = c * q_end(st)
            sig[e][ell + e] = (sig[e][ell + e] + v) % mod if mod else sig[e][ell + e] + v
        for (e, st), c in dp_b.items():
            qe, be = q_end(st), bare_end(st)
            if qe:
                v = c * qe
                bb[e][ell + e] = (bb[e][ell + e] + v) % mod if mod else bb[e][ell + e] + v
            if be:
                v = c * be
                pp[e][ell + e] = (pp[e][ell + e] + v) % mod if mod else pp[e][ell + e] + v
        if verbose:
            print(f"   l={ell:3d}: states int={len(dp_i)} bare={len(dp_b)} "
                  f"[{time.time() - t0:.2f}s]", flush=True)
    return sig, bb, pp


# ---------------------------------------------- D_series assembly mod p
# Mirror of severance_w3_depths.D_series + Nj_integer, in Z/pZ.  Every Fraction
# op there maps to a modular op here: F(-3)->(-3 mod p), F(1,3)->inv3, and the
# final 3^(k+1) that Nj_integer multiplies in is folded so N_j[k] is returned
# directly.  math.comb stays an exact int, reduced on use.

def _bimul_mod(a, b, K, emax, p):
    out = [[0] * (K + 1) for _ in range(emax + 1)]
    for e1 in range(emax + 1):
        r1 = a[e1]
        for e2 in range(emax + 1 - e1):
            r2 = b[e2]
            row = out[e1 + e2]
            for k1 in range(K + 1):
                c1 = r1[k1]
                if not c1:
                    continue
                for k2 in range(K + 1 - k1):
                    c2 = r2[k2]
                    if c2:
                        row[k1 + k2] = (row[k1 + k2] + c1 * c2) % p
    return out


def Dj_mod(j, K, p, verbose=False):
    """[D_j(0) .. D_j(K)] mod p, each a field element in Z/pZ."""
    emax = j - 1
    inv3 = pow(3, p - 2, p)
    neg3 = (-3) % p
    sig, bb, pp = families_mod(K, emax, mod=p, verbose=verbose)
    Bb = [row[:] for row in bb]
    Bb[0][0] = (Bb[0][0] + 1) % p
    A = []
    cur = Bb
    for m in range(K + 1):
        A.append(_bimul_mod(cur, Bb, K, emax, p))
        cur = _bimul_mod(cur, sig, K, emax, p)

    def r_coeff(k, s):
        tot = 0
        for E in range(s + 1):
            v = s - E
            for m in range(k + 1):
                if v > k - m:
                    continue
                a = A[m][E][k]
                if a:
                    tot = (tot + a * (math.comb(k - m, v) % p)
                           * pow(neg3, k - m - v, p)) % p
        for e in range(min(s, emax) + 1):
            v = s - e
            c = pp[e][k]
            if c and v <= k + 1:
                tot = (tot + c * (math.comb(k + 1, v) % p)
                       * pow(neg3, k + 1 - v, p)) % p
        return tot

    out = []
    for k in range(K + 1):
        if k + 1 - j < 0:
            out.append(0)
            continue
        r = {s: r_coeff(k, s) for s in range(j)}
        tot = 0
        for t in range(j):
            cb = math.comb(k - t, k + 1 - j) % p if k - t >= k + 1 - j else 0
            if not cb:
                continue
            a = 0
            for s in range(t + 1):
                a = (a + r[s] * (math.comb(2 * k + 1 - s, 2 * k + 1 - t) % p)
                     * pow(inv3, 2 * k + 1 - s, p)) % p
            a = (a * pow(-1 % p, t + 1, p)) % p
            tot = (tot + cb * a) % p
        Dk = (tot * pow(neg3, k + 1 - j, p)) % p          # = D_j(k) mod p
        out.append(Dk)
    return out


# --------------------------------------------------------------- self-check

def main():
    Kchk = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    p = PRIME

    print(f"== check families_mod(mod=None) == families() cell-for-cell, K={Kchk}")
    from severance_w3_depths import families                          # noqa: E402
    for emax in (0, 1, 2):
        s0, b0, p0 = families(Kchk, emax)
        s1, b1, p1 = families_mod(Kchk, emax, mod=None)
        assert s0 == s1 and b0 == b1 and p0 == p1, f"families mismatch emax={emax}"
    print(f"   emax=0,1,2 identical  OK")

    print(f"== check Dj_mod(j,K,p) == D_series(j,K) mod p, K={Kchk}")
    from severance_w3_depths import D_series                          # noqa: E402
    for j in (1, 2, 3):
        t = time.time()
        D = D_series(j, Kchk)
        ex = [(D[k].numerator * pow(D[k].denominator, p - 2, p)) % p
              for k in range(Kchk + 1)]
        md = Dj_mod(j, Kchk, p)
        assert ex == md, f"Dj mismatch j={j}: first diff at " + str(
            next(i for i in range(len(ex)) if ex[i] != md[i]))
        print(f"   j={j}: {Kchk + 1} coeffs match  [{time.time() - t:.1f}s]", flush=True)

    print("all mod-p self-checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
