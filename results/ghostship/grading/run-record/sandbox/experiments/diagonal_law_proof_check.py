#!/usr/bin/env python3
"""Machine checks for docs/proofs/diagonal-law.md (the diagonal law's shape).

Verifies, for k <= 3, from the enumerated cluster weights alone:
  1. rational structure: [y^k] F = R_k(z)/(1-3z)^(k+1) with R_k a polynomial,
     deg R_k <= 2k+1 (and tight: degrees are exactly 2k+1);
  2. the chain series reproduces the banked triangle T(H+k,H) for ALL
     H = 1..33 (chain identity, including edge and pure-cluster corrections);
  3. quasi-polynomiality: T(H+k,H)/3^H agrees with a degree-<=k polynomial
     for every H >= k+1 (the law, onset n >= 2k+1), and FAILS at H = k
     (onset sharp);
  4. integrality: 3^(1+2k) * q_k takes integer values (P_k integer-valued).

Weights provenance: experiments/defect_gas.py cluster_weight() /
boundary_weight(); pure-cluster weights from the 40/40 chain check.
"""
import os
from fractions import Fraction as F
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMAX = 3
HMAX = 33

INT = {(2,): 25, (3,): 49, (4,): 81, (2, 2): 339,
       (2, 3): 930, (3, 2): 930, (2, 2, 2): 4778}
BOT = {(2,): 5, (3,): 7, (4,): 9, (2, 2): 66,
       (2, 3): 177, (3, 2): 130, (2, 2, 2): 919}
PURE = {(2,): 1, (3,): 1, (4,): 1, (2, 2): 13,
        (2, 3): 25, (3, 2): 25, (2, 2, 2): 177}


def polyadd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
            for i in range(n)]


def polymul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, yy in enumerate(b):
                r[i + j] += x * yy
    return r


def ymul(A, B):
    R = {}
    for ka, pa in A.items():
        for kb, pb in B.items():
            if ka + kb <= KMAX:
                R[ka + kb] = polyadd(R.get(ka + kb, [F(0)]), polymul(pa, pb))
    return R


def zpow(e):
    return [F(0)] * e + [F(1)]


def omz_pow(e):
    r = [F(1)]
    for _ in range(e):
        r = polymul(r, [F(1), F(-3)])
    return r


def build_Rk():
    Eb = {0: zpow(1)}
    for v, w in BOT.items():
        k, l = sum(v) - len(v), len(v)
        if k <= KMAX:
            Eb[k] = polyadd(Eb.get(k, [F(0)]), [F(w) * c for c in zpow(l + 1)])
    Et = {0: [F(1)]}
    for v in BOT:
        k, l = sum(v) - len(v), len(v)
        if k <= KMAX:
            wt = BOT[tuple(reversed(v))]
            Et[k] = polyadd(Et.get(k, [F(0)]), [F(wt) * c for c in zpow(l)])
    sigma = {}
    for v, w in INT.items():
        k, l = sum(v) - len(v), len(v)
        if k <= KMAX:
            sigma[k] = polyadd(sigma.get(k, [F(0)]),
                               [F(w) * c for c in zpow(l + 1)])
    Pk = {}
    for v, w in PURE.items():
        k, l = sum(v) - len(v), len(v)
        if k <= KMAX:
            Pk[k] = polyadd(Pk.get(k, [F(0)]), [F(w) * c for c in zpow(l)])

    sig_pows = [{0: [F(1)]}]
    for _ in range(KMAX):
        sig_pows.append(ymul(sig_pows[-1], sigma))
    Rk = {}
    for k in range(KMAX + 1):
        num = [F(0)]
        for kb, pb in Eb.items():
            for kt, pt in Et.items():
                km = k - kb - kt
                if km < 0:
                    continue
                for m in range(km + 1):
                    s = sig_pows[m].get(km)
                    if s is None:
                        continue
                    num = polyadd(num, polymul(polymul(pb, pt),
                                               polymul(s, omz_pow(k - m))))
        if k in Pk:
            num = polyadd(num, polymul(Pk[k], omz_pow(k + 1)))
        while len(num) > 1 and num[-1] == 0:
            num.pop()
        Rk[k] = num
    return Rk


def banked_triangle():
    T = {}
    d = os.path.join(ROOT, "results", "ns_a36", "perheight")
    for f in os.listdir(d):
        if f.startswith('h') and f.endswith('.out'):
            Hc = int(f[1:-4])
            for ln in open(os.path.join(d, f)):
                n, c = ln.split()
                T[(int(n), Hc)] = int(c)
    return T


def main():
    Rk = build_Rk()
    T = banked_triangle()
    for k in range(KMAX + 1):
        deg = len(Rk[k]) - 1
        assert deg <= 2 * k + 1, (k, deg)
        assert deg == 2 * k + 1, f"bound not tight at k={k}"
        assert all(c.denominator == 1 for c in Rk[k]), "R_k not integral"

        ser = []
        for H in range(HMAX + 1):
            s = sum(Rk[k][d] * comb(H - d + k, k) * F(3) ** (H - d)
                    for d in range(min(len(Rk[k]), H + 1)))
            ser.append(s)
        for H in range(1, HMAX + 1):
            if (H + k, H) in T:
                assert ser[H] == T[(H + k, H)], (k, H)

        fit = [(H, F(T[(H + k, H)], 3 ** H)) for H in range(k + 1, 2 * k + 2)]

        def q(x):
            tot = F(0)
            for i, (hi, vi) in enumerate(fit):
                w = vi
                for j, (hj, _) in enumerate(fit):
                    if j != i:
                        w *= F(x - hj, hi - hj)
                tot += w
            return tot

        for H in range(k + 1, HMAX + 1):
            if (H + k, H) in T:
                assert q(H) == F(T[(H + k, H)], 3 ** H), (k, H)
        if k >= 1:
            assert q(k) != F(T[(2 * k, k)], 3 ** k), f"onset not sharp k={k}"
        for n in range(2 * k + 1, 2 * k + 30):
            v = 3 ** (1 + 2 * k) * q(n - k)
            assert v.denominator == 1, f"P_{k}({n}) not integer"
        print(f"k={k}: deg R_k = {deg} (tight), chain==banked H<=33, "
              f"law exact H>={k+1}, sharp at H={k}, P_k integer-valued  OK")
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
