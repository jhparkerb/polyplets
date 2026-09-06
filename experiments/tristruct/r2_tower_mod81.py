#!/usr/bin/env python3
"""r2 tower builder (triangle-structure round 2, agent 1): the mod-81 master
equation made explicit, with G mod 81 -- one boundary-cluster level past the
mod-27 equation of results/diagonal-formula.md.

Prior art (credited, not re-claimed): experiments/spine_deeper.py check 1
already holds the mod-81 H-equation numerically (2026-07-13). New here:
  1. Mechanical survivor derivation from the valuation filter over the full
     k <= 5 weight table (not a hand-picked list), with a completeness proof
     from the row bound l <= k alone: interior clusters need k <= 4, boundary
     clusters need k <= 3, both inside the banked table. Zero new weights.
  2. The explicit monic master curve mod 81 (degree 9 in H), verified as a
     series identity -- the object agent 2's sympy division needs:
       E81 = H^9 - H^8 - 25 u H^6 - 36 u^2 H^5 - 45 u^2 H^4
                 - 72 u^3 H^2 - 27 u^4  == 0 (mod 81).
  3. G mod 81 from the boundary residue formula (spine_deeper stopped at
     G mod 27): eps_b, eps_t and the denominator each gain terms; checked
     against the banked g_j mod 81 for k <= 17.
  4. The d=3 deficit-family target on the fully derived series:
     P_k(3k-2) mod 81 for k = 3..118 -- v3 == 3 with unit cycle, v3 >= 4
     exactly at k == 1 (mod 3). Cross-checked against exact P_k for k <= 17.
  5. Per-level cost census m = 3..10 (mod 3^m): candidate clusters, weights
     in hand vs needing new DP, curve degree -- the go/no-go measurement.

Exact integer arithmetic throughout. Runtime ~1-2 min on a laptop.
"""
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "experiments"))

from cluster_weight_dp import KNOWN_WEIGHTS, compositions, interior, boundary

KX = 122  # series order


def v3(x):
    x = abs(x)
    assert x != 0
    v = 0
    while x % 3 == 0:
        x //= 3
        v += 1
    return v


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


def banked(K=17):
    """Exact P_k (k <= K) via scripts/derive_pk_fast.py (real-sweep anchors,
    REAL_H audited there), plus the integer G, H series it implies."""
    import types, io, contextlib
    path = os.path.join(ROOT, "scripts", "derive_pk_fast.py")
    src = open(path).read()
    mod = types.ModuleType("dpf")
    mod.__dict__['__file__'] = path
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "dpf", "exec"), mod.__dict__)
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
    return P, Gs, Hb, peval


def survivors_mod(M):
    """(interior, eps_bottom, eps_top, denominator) survivor term lists at
    mod 3^M, derived mechanically from the valuation filter over the full
    banked table. Completeness: v3(What) >= k-1 and v3(Bhat) >= k (row bound
    l <= k, defect-gas VALUATION LEMMA), so interior needs k <= M and
    boundary k <= M-1; caller must check the table covers that range."""
    MOD = 3 ** M
    ints, ebs, ets, dens = [], [], [], []
    for vec, (wi, wb, wt, _) in KNOWN_WEIGHTS.items():
        k, l = sum(vec) - len(vec), len(vec)
        what = wi * 3 ** (2 * k - l - 1)
        if v3(what) < M:
            ints.append((vec, k, l, what % MOD))
        if v3((l + 1) * what) < M:
            dens.append((vec, k, l, ((l + 1) * what) % MOD))
        bb, bt = wb * 3 ** (2 * k - l), wt * 3 ** (2 * k - l)
        if v3(bb) < M:
            ebs.append((vec, k, l, bb % MOD))
        if v3(bt) < M:
            ets.append((vec, k, l, bt % MOD))
    return ints, ebs, ets, dens


def fixed_point(terms, MOD):
    """H = 1 + sum w u^k H^-(k+l), solved as a series fixed point."""
    xmul, xinv, xpow = series_ops(MOD)
    H = [1] + [0] * KX
    for _ in range(KX + 2):
        rhs = [1] + [0] * KX
        for _, k, l, w in terms:
            Hp = xpow(H, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    rhs[m + k] = (rhs[m + k] + w * Hp[m]) % MOD
        if rhs == H:
            break
        H = rhs
    return H


def main():
    t0 = time.time()
    M, MOD = 4, 81
    P, Gs, Hb, peval = banked(17)

    # ---- 1. survivors mod 81, mechanically, with completeness ----
    ints, ebs, ets, dens = survivors_mod(M)
    maxk_table = max(sum(v) - len(v) for v in KNOWN_WEIGHTS)
    assert maxk_table >= M, "table must cover interior k <= M"
    assert sorted(v for v, *_ in ints) == \
        [(2,), (2, 2), (2, 2, 2), (2, 2, 2, 2), (3,)]
    assert sorted(v for v, *_ in ebs) == sorted(v for v, *_ in ets) == \
        [(2,), (2, 2), (2, 2, 2), (3,)]
    print("interior survivors mod 81:",
          [(v, w) for v, _, _, w in sorted(ints)])
    print("boundary survivors mod 81 (eps terms):",
          [(v, w) for v, _, _, w in sorted(ebs)])
    print("denominator terms mod 81:",
          [(v, w) for v, _, _, w in sorted(dens)])

    # ---- 2. H mod 81 and the explicit monic curve ----
    xmul, xinv, xpow = series_ops(MOD)
    H81 = fixed_point(ints, MOD)
    assert H81[:18] == [h % MOD for h in Hb], "H mod 81 vs banked"
    print("mod-81 master equation fixed point matches banked H, k <= 17  OK")

    D = max(k + l for _, k, l, _ in ints)          # = 8
    # E = H^(D+1) - H^D - sum w u^k H^(D-k-l), must vanish identically
    E = xpow(H81, D + 1)
    HD = xpow(H81, D)
    for m in range(KX + 1):
        E[m] = (E[m] - HD[m]) % MOD
    for _, k, l, w in ints:
        Hp = xpow(H81, D - k - l)
        for m in range(KX + 1 - k):
            if Hp[m]:
                E[m + k] = (E[m + k] - w * Hp[m]) % MOD
    assert all(c == 0 for c in E), "explicit curve E81"
    terms_str = " - ".join(f"{w}*u^{k}*H^{D - k - l}"
                           for _, k, l, w in sorted(ints, key=lambda t: (t[1], t[2])))
    print(f"explicit curve (deg {D + 1}, monic): "
          f"H^{D + 1} - H^{D} - {terms_str} == 0 (mod 81)  OK")

    # ---- 3. G mod 81 from the boundary residue formula ----
    u = [0, 1] + [0] * (KX - 1)

    def eps_series(terms):
        out = [1] + [0] * KX
        for _, k, l, w in terms:
            Hp = xpow(H81, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    out[m + k] = (out[m + k] + w * Hp[m]) % MOD
        return out

    eb, et = eps_series(ebs), eps_series(ets)
    assert eb == et, "eps_b == eps_t mod 81"
    den = eps_series(dens)  # same shape: 1 + sum (l+1)What u^k H^-(k+l)
    Hp = [((m + 1) * H81[m + 1]) % MOD for m in range(KX)] + [0]
    fac = [((1 if m == 0 else 0) - xmul(xmul(u, Hp), xinv(H81))[m]) % MOD
           for m in range(KX + 1)]
    G81 = xmul(xmul(xmul(eb, et), fac), xinv(den))
    assert G81[:18] == [g % MOD for g in Gs], "G mod 81 vs banked"
    print("G mod 81 from boundary residue matches banked g_j, k <= 17  OK")

    # ---- 4. the d=3 target on the derived series ----
    def Pk_mod(k, n):
        Hn = xpow(H81, n)
        return sum(G81[j] * Hn[k - j] for j in range(k + 1)) % MOD

    # cross-check against the exact banked P_k first
    for k in range(3, 18):
        n = 3 * k - 2
        exact = int(peval(P[k], n)) % MOD
        assert exact == Pk_mod(k, n), (k, exact)
    print("P_k(3k-2) mod 81: derived series == exact banked P_k, k = 3..17  OK")

    res = {}
    for k in range(3, KX - 3):
        p = Pk_mod(k, 3 * k - 2)
        assert p % 27 == 0, (k, p)
        res[k] = (p // 27) % 3
    ks = sorted(res)
    assert all(res[k] == res[k + 3] for k in ks if k + 3 in res), "period 3"
    assert all((res[k] == 0) == (k % 3 == 1) for k in ks), "zeros at k==1 mod 3"
    cyc = [res[3], res[4], res[5]]
    print(f"d=3 family on derived series, k = 3..{ks[-1]}: "
          f"P_k(3k-2) == 27*r_k (mod 81), r cycle (k=3,4,5,...) = {cyc}, "
          f"r == 0 iff k == 1 (mod 3)  OK")

    # ---- 5. per-level cost census, m = 3..10 ----
    print("\nper-level cost census (interior clusters, mod 3^m):")
    print("  bar: v3(W) + 2k - l - 1 <= m-1;  row bound => k <= m")
    pair_w = {}
    for L in (6, 7, 8):
        t1 = time.time()
        pair_w[L] = interior((2,) * L)
        print(f"  live DP: W(2^{L}) = {pair_w[L]}  "
              f"v3 = {v3(pair_w[L])}  [{time.time() - t1:.1f}s]")
    print("   m | cand | known | surv | newDP | tier(1-row) | deg(curve)")
    for m in range(3, 11):
        cand = [c for k in range(1, m + 1) for c in compositions(k)
                if 2 * k - len(c) - 1 <= m - 1]
        known = surv = new = 0
        maxdeg = 0
        for c in cand:
            k, l = sum(c) - len(c), len(c)
            if c in KNOWN_WEIGHTS:
                w = KNOWN_WEIGHTS[c][0]
            elif l == 1:
                w = (2 * c[0] + 1) ** 2      # proved closed form
            elif c == (2,) * l and l in pair_w:
                w = pair_w[l]
            else:
                new += 1
                continue
            known += 1
            if v3(w) + 2 * k - l - 1 <= m - 1:
                surv += 1
                maxdeg = max(maxdeg, k + l + 1)
        tier = (m + 1) // 2
        print(f"  {m:2d} | {len(cand):4d} | {known:5d} | {surv:4d} | "
              f"{new:5d} | {tier:11d} | {maxdeg:3d}(+)" if new else
              f"  {m:2d} | {len(cand):4d} | {known:5d} | {surv:4d} | "
              f"{new:5d} | {tier:11d} | {maxdeg:3d}")
    print(f"\nALL CHECKS PASS  [{time.time() - t0:.0f}s total]")


if __name__ == "__main__":
    main()
