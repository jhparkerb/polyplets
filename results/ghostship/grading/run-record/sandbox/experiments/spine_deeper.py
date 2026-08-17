#!/usr/bin/env python3
"""Deeper 3-adic structure from the defect gas (2026-07-13 cross-pollination).

Checks, all pure algebra from enumerated cluster weights:
  1. mod-81 master equation (six terms; the four-pair stack enters at 27)
     matches the banked 18 coefficients of H and is a unique fixed point.
  2. G mod 27 from the boundary residue formula (only the pair-row boundary
     survives; denominator keeps three terms) matches banked g_j mod 27.
  3. The deficit-2 spine law T(3m+2, 2m+1) == 2 (mod 3), i.e.
     P_{m+1}(3m+2) == 18 (mod 27), holds on the derived series for
     m = 1..94 -- far beyond the banked triangle's reach (m <= 11).
  4. Onset sharpness ab initio: deg R_k = 2k+1 exactly for k <= 5
     (leading coefficients 1, 4, -80, 1753, -40928, 987355).

Negative result recorded: the all-pairs weight family W(2^l) is NOT
C-finite -- an order-7 fit on l <= 14 is refuted at l = 16 (non-integer
prediction). The gap between pending blocks is an unbounded walk, so the
family's GF is at best algebraic (kernel-method target); growth ~ 14.41.
This blocks the "rational top-coefficient GF" route to all-k onset
sharpness; k <= 5 stands verified, general k open.
"""
import os
import sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cluster_weight_dp import KNOWN_WEIGHTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KX = 300


def series_ops(MOD):
    def xmul(a, b):
        out = [0] * (KX + 1)
        for i, ai in enumerate(a):
            if ai:
                for j in range(KX + 1 - i):
                    if b[j]:
                        out[i + j] = (out[i + j] + ai * b[j]) % MOD
        return out

    def xinv(a):
        r = [pow(a[0], -1, MOD)] + [0] * KX
        for m in range(1, KX + 1):
            r[m] = (-r[0] * sum(a[i] * r[m - i]
                                for i in range(1, m + 1))) % MOD
        return r

    def xpow(a, p):
        base = a if p >= 0 else xinv(a)
        r = [1] + [0] * KX
        q = abs(p)
        while q:
            if q & 1:
                r = xmul(r, base)
            base = xmul(base, base)
            q >>= 1
        return r

    return xmul, xinv, xpow


def banked_series(K=17):
    import types, io, contextlib
    src = open(os.path.join(ROOT, "scripts", "derive_pk_fast.py")).read()
    mod = types.ModuleType("d")
    mod.__dict__['__file__'] = os.path.join(ROOT, "scripts", "derive_pk_fast.py")
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "d", "exec"), mod.__dict__)
        P, _ = mod.derive(K)

    def peval(poly, n):
        r = F(0)
        for c in reversed(poly):
            r = r * n + c
        return r

    Gs = [1] + [int(peval(P[k], 0)) for k in range(1, K + 1)]
    GH = [int(peval(P[k], 1)) if k else 1 for k in range(K + 1)]
    inv = [1] + [0] * K
    for m in range(1, K + 1):
        inv[m] = -sum(Gs[j] * inv[m - j] for j in range(1, m + 1))
    Hb = [sum(GH[i] * inv[m - i] for i in range(m + 1)) for m in range(K + 1)]
    return Gs, Hb


def main():
    K = 17
    Gs, Hb = banked_series(K)

    # 1. mod-81 master equation
    xmul, xinv, xpow = series_ops(81)
    terms81 = [(25, 1, 2), (441, 2, 3), (1017, 2, 4),
               (43002 % 81, 3, 6), ((KNOWN_WEIGHTS[(2, 2, 2, 2)][0] * 27) % 81, 4, 8)]
    H = [1] + [0] * KX
    for _ in range(KX + 2):
        rhs = [1] + [0] * KX
        for w, k, p in terms81:
            Hp = xpow(H, -p)
            for m in range(KX + 1 - k):
                rhs[m + k] = (rhs[m + k] + w * Hp[m]) % 81
        if rhs == H:
            break
        H = rhs
    assert [h % 81 for h in Hb] == H[:K + 1], "mod-81 master equation"
    print("mod-81 master equation (6 terms) matches banked H  OK")

    # 2. G mod 27 from the boundary residue formula
    xm, xi, xp = series_ops(27)
    H27 = [h % 27 for h in H]
    u = [0, 1] + [0] * (KX - 1)
    uH2 = xm(u, xp(H27, -2))
    eps = [((1 if m == 0 else 0) + 15 * uH2[m]) % 27 for m in range(KX + 1)]
    u2 = xm(u, u)
    u3 = xm(u2, u)
    den = [((1 if m == 0 else 0) + 50 * uH2[m]
            + 18 * xm(u2, xp(H27, -3))[m]
            + 18 * xm(u3, xp(H27, -6))[m]) % 27 for m in range(KX + 1)]
    Hp = [((m + 1) * H[m + 1]) % 27 for m in range(KX)] + [0]
    fac = [((1 if m == 0 else 0) - xm(xm(u, Hp), xi(H27))[m]) % 27
           for m in range(KX + 1)]
    G27 = xm(xm(xm(eps, eps), fac), xi(den))
    assert G27[:K + 1] == [g % 27 for g in Gs], "G mod 27"
    print("G mod 27 from boundary residue matches banked g_j  OK")

    # 3. deficit-2 spine law: P_{m+1}(3m+2) == 18 (mod 27) for m = 1..94
    for m in range(1, 95):
        k = m + 1
        n = 3 * m + 2
        Hn = xp(H27, n)
        Pk = sum(G27[j] * Hn[k - j] for j in range(k + 1)) % 27
        assert Pk == 18, (m, Pk)
    print("T(3m+2,2m+1) == 2 (mod 3) [P == 18 mod 27] for m = 1..94  OK")

    # 4. onset sharpness ab initio, k <= 5: deg R_k == 2k+1, leading coeffs
    KM = 5

    def polyadd(a, b):
        n = max(len(a), len(b))
        return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                for i in range(n)]

    def polymul(a, b):
        r = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    r[i + j] += x * y
        return r

    def ymulp(A, B):
        R = {}
        for ka, pa in A.items():
            for kb, pb in B.items():
                if ka + kb <= KM:
                    R[ka + kb] = polyadd(R.get(ka + kb, [0]), polymul(pa, pb))
        return R

    zpow = lambda e: [0] * e + [1]

    def omz(e):
        r = [1]
        for _ in range(e):
            r = polymul(r, [1, -3])
        return r

    Eb = {0: zpow(1)}
    Et = {0: [1]}
    sig = {}
    Pp = {}
    for v, (wi, wb, wt, wp) in KNOWN_WEIGHTS.items():
        k, l = sum(v) - len(v), len(v)
        Eb[k] = polyadd(Eb.get(k, [0]), [wb * c for c in zpow(l + 1)])
        Et[k] = polyadd(Et.get(k, [0]), [wt * c for c in zpow(l)])
        sig[k] = polyadd(sig.get(k, [0]), [wi * c for c in zpow(l + 1)])
        Pp[k] = polyadd(Pp.get(k, [0]), [wp * c for c in zpow(l)])
    sp = [{0: [1]}]
    for _ in range(KM):
        sp.append(ymulp(sp[-1], sig))
    lead = []
    for k in range(KM + 1):
        num = [0]
        for kb, pb in Eb.items():
            for kt, pt in Et.items():
                km = k - kb - kt
                if km < 0:
                    continue
                for m in range(km + 1):
                    s = sp[m].get(km)
                    if s is None:
                        continue
                    num = polyadd(num, polymul(polymul(pb, pt),
                                               polymul(s, omz(k - m))))
        if k in Pp:
            num = polyadd(num, polymul(Pp[k], omz(k + 1)))
        while len(num) > 1 and num[-1] == 0:
            num.pop()
        assert len(num) - 1 == 2 * k + 1, f"deg R_{k}"
        lead.append(num[-1])
    assert lead == [1, 4, -80, 1753, -40928, 987355], lead
    print(f"onset sharpness ab initio k<=5: deg R_k = 2k+1, leads {lead}  OK")
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
