#!/usr/bin/env python3
"""r2 adversary (triangle-structure round 2, agent 3): independent audit of
the d=3 sleeve unit formula proof (results/triangle-r2-d3-proof.md) and its
mod-81 tower input (results/triangle-r2-tower-mod81.md).

Independent of agents 1/2's code paths wherever the check is load-bearing:
  - own series toolkit, own v3, own composition generator;
  - survivor lists re-derived from cluster_weight_dp.KNOWN_WEIGHTS with an
    independent valuation filter, and completeness re-proved (the kill bounds
    2k-l-1 >= 4 for interior k >= 5, 2k-l >= 4 for boundary k >= 4 are
    asserted composition-by-composition, weight-independent);
  - the certificate polynomials (E81, A, B, epsp, dp, Mnum, N) rebuilt from
    the re-derived survivor lists, and the division N mod (E81, 81) decided
    by an OWN monic-reduction routine over (Z/81)[u][H] -- no sympy.
    (Legitimate: E81 is monic in H, so division-with-remainder in Z[u][H] is
    exact and commutes with coefficientwise reduction mod 81.)
  - the theorem's valuation claims checked EXACTLY (not mod 81) on the banked
    P_k, k = 3..17, and against the real-sweep triangle cells as integers
    (27*T == P_k(3k-2)), k = 3..11, provenance quoted;
  - a perturbation battery: six deliberate corruptions (target cycle, a
    below-onset constant, one weight each in dp / epsp / E81, and the mod-27
    curve promoted verbatim) must each make the division remainder NONZERO.
    A certificate that passed any of these would be worthless.

Exact integer arithmetic throughout. Runtime ~1 min.
"""
import io
import contextlib
import os
import sys
import time
import types
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments"))

from cluster_weight_dp import KNOWN_WEIGHTS

MOD = 81
KX = 140  # series order for the numeric guards (agents used 122)


# ---------- own toolkit ----------

def v3(x):
    x = abs(x)
    assert x != 0
    v = 0
    while x % 3 == 0:
        x //= 3
        v += 1
    return v


def smul(a, b):
    out = [0] * (KX + 1)
    for i, ai in enumerate(a):
        if ai:
            for j in range(KX + 1 - i):
                if b[j]:
                    out[i + j] = (out[i + j] + ai * b[j]) % MOD
    return out


def sinv(a):
    assert a[0] % 3 != 0, "series unit required"
    r = [pow(a[0], -1, MOD)] + [0] * KX
    for m in range(1, KX + 1):
        r[m] = (-r[0] * sum(a[i] * r[m - i] for i in range(1, m + 1))) % MOD
    return r


def spow(a, p):
    base = a if p >= 0 else sinv(a)
    r = [1] + [0] * KX
    for _ in range(abs(p)):
        r = smul(r, base)
    return r


def compositions(k):
    """All row-size vectors (s_1..s_l), s_i >= 2, sum(s_i - 1) = k."""
    if k == 0:
        return [()]
    out = []
    for s in range(2, k + 2):
        for tail in compositions(k - (s - 1)):
            out.append((s,) + tail)
    return out


# ---------- banked chain (data load, shared by necessity) ----------

def load_banked(K=17):
    path = os.path.join(ROOT, "scripts", "derive_pk_fast.py")
    mod = types.ModuleType("dpf")
    mod.__dict__['__file__'] = path
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(open(path).read(), "dpf", "exec"), mod.__dict__)
        P, _ = mod.derive(K)

    def peval(poly, n):
        r = F(0)
        for c in reversed(poly):
            r = r * n + c
        return int(r) if F(r).denominator == 1 else r
    return P, peval


# ---------- dict polynomials over (Z/81)[u][H]: key (i, j) = H^i u^j ----------

def pmul(a, b):
    out = {}
    for (i1, j1), c1 in a.items():
        for (i2, j2), c2 in b.items():
            key = (i1 + i2, j1 + j2)
            out[key] = (out.get(key, 0) + c1 * c2) % MOD
    return {k: c for k, c in out.items() if c}


def padd(*polys):
    out = {}
    for p in polys:
        for k, c in p.items():
            out[k] = (out.get(k, 0) + c) % MOD
    return {k: c for k, c in out.items() if c}


def pscale(a, s):
    return {k: (c * s) % MOD for k, c in a.items() if (c * s) % MOD}


def dH(a):
    return {(i - 1, j): (c * i) % MOD for (i, j), c in a.items()
            if i and (c * i) % MOD}


def dU(a):
    return {(i, j - 1): (c * j) % MOD for (i, j), c in a.items()
            if j and (c * j) % MOD}


def reduce_monic(N, E):
    """Remainder of N mod E in (Z/81)[u][H]; E must be monic of degree d in H.
    Unique because E is monic; agrees with the reduction of the Z[u][H]
    remainder mod 81."""
    d = max(i for i, _ in E)
    assert E[(d, 0)] == 1, "monic required"
    lower = {k: c for k, c in E.items() if k[0] < d}
    N = dict(N)
    while True:
        top = [(i, j) for (i, j) in N if i >= d]
        if not top:
            return N
        i, j = max(top)
        c = N.pop((i, j))
        if not c:
            continue
        for (ei, ej), ec in lower.items():
            key = (i - d + ei, j + ej)
            N[key] = (N.get(key, 0) - c * ec) % MOD
        N = {k: cc for k, cc in N.items() if cc}


def poly_at_series(p, Hs):
    """Evaluate p(H, u) at H = Hs(u) as a series mod 81."""
    out = [0] * (KX + 1)
    for (i, j), c in p.items():
        Hp = spow(Hs, i)
        for m in range(KX + 1 - j):
            if Hp[m]:
                out[m + j] = (out[m + j] + c * Hp[m]) % MOD
    return out


def main():
    t0 = time.time()

    # ---- A. completeness of the survivor derivation, weight-independent ----
    # Row bound l <= k (proved, diagonal-law.md Step 3) holds per composition
    # by construction (every s_i >= 2 gives >= 1 surplus per row). Kill
    # bounds, checked composition-by-composition through k = 8:
    for k in range(1, 9):
        for c in compositions(k):
            l = len(c)
            assert l <= k
            if k >= 5:
                assert 2 * k - l - 1 >= 4, ("interior kill", c)
            if k >= 4:
                assert 2 * k - l >= 4, ("boundary kill", c)
    # (k >= 9: 2k-l-1 >= k-1 >= 8 and 2k-l >= k >= 9, monotone; no check
    # needed. So mod 81 completeness needs the weight table only for
    # interior k <= 4, boundary k <= 3, denominator k <= 4.)
    for k in range(1, 6):
        for c in compositions(k):
            assert c in KNOWN_WEIGHTS, ("table gap", c)
    assert len(KNOWN_WEIGHTS) == 31 == sum(len(compositions(k))
                                           for k in range(1, 6))
    print("A. completeness: kill bounds hold per composition (k <= 8, then "
          "monotone); KNOWN_WEIGHTS = all 31 types k <= 5  OK")

    # ---- B. survivor lists, independently filtered ----
    ints, ebs, ets, dens = [], [], [], []
    for vec, (wi, wb, wt, _) in KNOWN_WEIGHTS.items():
        k, l = sum(vec) - len(vec), len(vec)
        what = wi * 3 ** (2 * k - l - 1)
        if v3(what) <= 3:
            ints.append((k, l, what % MOD, vec))
        if v3((l + 1) * what) <= 3:
            dens.append((k, l, ((l + 1) * what) % MOD, vec))
        if v3(wb * 3 ** (2 * k - l)) <= 3:
            ebs.append((k, l, (wb * 3 ** (2 * k - l)) % MOD, vec))
        if v3(wt * 3 ** (2 * k - l)) <= 3:
            ets.append((k, l, (wt * 3 ** (2 * k - l)) % MOD, vec))
    # against the values STATED in the two md files (retyped, not imported):
    assert sorted(t[:3] for t in ints) == \
        [(1, 1, 25), (2, 1, 36), (2, 2, 45), (3, 3, 72), (4, 4, 27)]
    assert sorted(t[:3] for t in ebs) == sorted(t[:3] for t in ets) == \
        [(1, 1, 15), (2, 1, 27), (2, 2, 27), (3, 3, 27)]
    assert sorted(t[:3] for t in dens) == \
        [(1, 1, 50), (2, 1, 72), (2, 2, 54), (3, 3, 45), (4, 4, 54)]
    print("B. survivor lists re-derived; match both md files' stated "
          "coefficients  OK")

    # ---- C. exact valuations from the banked P_k (not mod-81 series) ----
    P, peval = load_banked(17)
    finer = {}
    for k in range(3, 18):
        val = peval(P[k], 3 * k - 2)
        assert isinstance(val, int)
        v = v3(val)
        r = (val // 27) % 3
        if k % 3 == 1:
            assert v >= 4, (k, v)
            finer[k] = v
        else:
            assert v == 3 and r == (2, 0, 1)[k % 3], (k, v, r)
    assert finer == {4: 7, 7: 4, 10: 4, 13: 5, 16: 4}
    from triangle import Triangle
    tri = Triangle.load()
    for k in range(3, 12):
        n, Hh = 3 * k - 2, 2 * k - 2
        assert tri.provenance(n, Hh) == "real-sweep", (n, Hh)
        assert 27 * tri.cell(n, Hh) == peval(P[k], n), (n, Hh)
    print("C. exact: v3(P_k(3k-2)) = 3 with residue cycle (2,0,1) at "
          "k !== 1, >= 4 at k == 1 (mod 3), k = 3..17 (finer: 7,4,4,5,4 at "
          "k = 4,7,10,13,16); 27*T == P_k(3k-2) as INTEGERS on all nine "
          "real-sweep cells  OK")

    # ---- D. H, G mod 81 rebuilt with own code; against banked series ----
    Gs = [1] + [peval(P[k], 0) for k in range(1, 18)]
    GH = [1] + [peval(P[k], 1) for k in range(1, 18)]
    ginv = [1] + [0] * 17
    for m in range(1, 18):
        ginv[m] = -sum(Gs[i] * ginv[m - i] for i in range(1, m + 1))
    Hb = [sum(GH[i] * ginv[m - i] for i in range(m + 1)) for m in range(18)]

    H81 = [1] + [0] * KX
    for _ in range(KX + 1):
        rhs = [1] + [0] * KX
        for k, l, w, _ in ints:
            Hp = spow(H81, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    rhs[m + k] = (rhs[m + k] + w * Hp[m]) % MOD
        if rhs == H81:
            break
        H81 = rhs
    assert H81[:18] == [h % MOD for h in Hb], "H mod 81 vs banked"

    def eps(terms):
        out = [1] + [0] * KX
        for k, l, w, _ in terms:
            Hp = spow(H81, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    out[m + k] = (out[m + k] + w * Hp[m]) % MOD
        return out

    Hd = [((m + 1) * H81[m + 1]) % MOD for m in range(KX)] + [0]
    uHdH = smul([0, 1] + [0] * (KX - 1), smul(Hd, sinv(H81)))  # u H'/H, exact
    one = [1] + [0] * KX
    fac1 = [(one[m] - uHdH[m]) % MOD for m in range(KX + 1)]
    G81 = smul(smul(smul(eps(ebs), eps(ets)), fac1), sinv(eps(dens)))
    assert G81[:18] == [g % MOD for g in Gs], "G mod 81 vs banked"
    print("D. own fixed point + residue formula: H81, G81 match banked "
          "series mod 81, k <= 17  OK")

    # ---- E. the family series and the LB parametrization, own code ----
    S = []
    Hn = spow(H81, -2)
    H3 = spow(H81, 3)
    for k in range(KX + 1):
        S.append(sum(G81[j] * Hn[k - j] for j in range(k + 1)) % MOD)
        Hn = smul(Hn, H3)
    c0, c1, c2 = 1, peval(P[1], 1) % MOD, peval(P[2], 4) % MOD
    assert (c0, c1, c2) == (1, 61, 1)
    for k in range(KX + 1):
        want = (c0, c1, c2)[k] if k < 3 else (54, 0, 27)[k % 3]
        assert S[k] == want, (k, S[k], want)
    fac3 = [(one[m] - 3 * uHdH[m]) % MOD for m in range(KX + 1)]
    LHSu = smul(smul(G81, spow(H81, -2)), sinv(fac3))
    vu = smul([0, 1] + [0] * (KX - 1), spow(H81, -3))
    comp = [S[KX] % MOD] + [0] * KX
    for c in reversed(S[:KX]):
        comp = smul(comp, vu)
        comp[0] = (comp[0] + c) % MOD
    assert LHSu == comp, "S(v(u)) == G H^-2 / (1 - 3uH'/H)"
    print(f"E. own series: [v^k]S = (1,61,1) then 27*(2,0,1) for k <= {KX}; "
          "LB parametrization identity holds  OK")

    # ---- F. certificate polynomials from the re-derived lists ----
    def build(ints, ebs, dens):
        Dint = max(k + l for k, l, _, _ in ints)
        E = {(Dint + 1, 0): 1, (Dint, 0): MOD - 1}
        for k, l, w, _ in ints:
            E[(Dint - k - l, k)] = (E.get((Dint - k - l, k), 0) - w) % MOD
        Deps = max(k + l for k, l, _, _ in ebs)
        ep = {(Deps, 0): 1}
        for k, l, w, _ in ebs:
            ep[(Deps - k - l, k)] = (ep.get((Deps - k - l, k), 0) + w) % MOD
        Dden = max(k + l for k, l, _, _ in dens)
        dp = {(Dden, 0): 1}
        for k, l, w, _ in dens:
            dp[(Dden - k - l, k)] = (dp.get((Dden - k - l, k), 0) + w) % MOD
        return E, ep, dp

    E81, epsp, dp = build(ints, ebs, dens)
    assert E81 == {(9, 0): 1, (8, 0): 80, (6, 1): 56, (5, 2): 45,
                   (4, 2): 36, (2, 3): 9, (0, 4): 54}  # -1,-25,-36,-45,-72,-27
    assert epsp == {(6, 0): 1, (4, 1): 15, (3, 2): 27, (2, 2): 27, (0, 3): 27}
    assert dp == {(8, 0): 1, (6, 1): 50, (5, 2): 72, (4, 2): 54,
                  (2, 3): 45, (0, 4): 54}
    # numeric guards on the curve with own evaluator
    assert all(c == 0 for c in poly_at_series(E81, H81)), "E81(H81,u) == 0"
    A, B = dH(E81), pscale(dU(E81), MOD - 1)
    lhs = smul(poly_at_series(A, H81), Hd)
    rhs = poly_at_series(B, H81)
    assert lhs[:KX] == rhs[:KX], "A H' == B (top coefficient excluded)"
    # Step-5 congruence algebra as series: X(AH-3uB) == Y(AH-uB) mod 81
    AH = pmul(A, {(1, 0): 1})
    uB = pmul(B, {(0, 1): 1})
    AHm3uB = padd(AH, pscale(uB, MOD - 3))
    AHmuB = padd(AH, pscale(uB, MOD - 1))
    X, Y = fac1, fac3
    assert smul(X, poly_at_series(AHm3uB, H81)) == \
        smul(Y, poly_at_series(AHmuB, H81)), "X(AH-3uB) == Y(AH-uB)"

    def certificate(E, ep, dpoly, cs, cycle):
        A, B = dH(E), pscale(dU(E), MOD - 1)
        AH = pmul(A, {(1, 0): 1})
        uB = pmul(B, {(0, 1): 1})
        AHmuB = padd(AH, pscale(uB, MOD - 1))
        AHm3uB = padd(AH, pscale(uB, MOD - 3))
        H9mu3 = {(9, 0): 1, (0, 3): MOD - 1}
        c0, c1, c2 = cs
        r3, r4, r5 = cycle          # target residues at k = 3, 4, 5
        Mnum = padd(pmul({(6, 0): c0, (3, 1): c1, (0, 2): c2}, H9mu3),
                    pscale({(6, 3): r3, (3, 4): r4, (0, 5): r5}, 27))
        N = padd(pmul(pmul(pmul(ep, ep), AHmuB), H9mu3),
                 pscale(pmul(pmul(Mnum, dpoly), AHm3uB), MOD - 1))
        return reduce_monic(N, E)

    # Mnum cross-check: target numerator over H^6(H^9-u^3) with v = u/H^3 is
    # (c0 H^6 + c1 uH^3 + c2 u^2)(H^9-u^3) + 27(2u^3 H^6 + 0*u^4 H^3 + u^5);
    # the generic 'cycle' slot places 27*r at (H^{6-3(k-3)}, u^k), k = 3,4,5.
    r = certificate(E81, epsp, dp, (1, 61, 1), (2, 0, 1))
    assert r == {}, f"CERTIFICATE FAILED: remainder {r}"
    print("F. certificate reproved by OWN monic reduction over (Z/81)[u][H]: "
          "remainder identically zero  OK")

    # ---- G. sensitivity battery: each corruption must break it ----
    def broken(**kw):
        E, ep, dpoly = kw.get('E', E81), kw.get('ep', epsp), kw.get('dp', dp)
        cs, cyc = kw.get('cs', (1, 61, 1)), kw.get('cycle', (2, 0, 1))
        return certificate(E, ep, dpoly, cs, cyc) != {}

    assert broken(cycle=(2, 1, 0)), "permuted target cycle PASSED"
    assert broken(cycle=(1, 0, 2)), "rotated target cycle PASSED"
    assert broken(cs=(1, 62, 1)), "wrong below-onset constant PASSED"
    dp_bad = dict(dp); dp_bad[(6, 1)] = 77
    assert broken(dp=dp_bad), "corrupted denominator weight PASSED"
    ep_bad = dict(epsp); ep_bad[(4, 1)] = 42
    assert broken(ep=ep_bad), "corrupted boundary weight PASSED"
    E_bad = dict(E81); E_bad[(2, 3)] = 36   # 72 -> 45 as signed coefficient
    assert broken(E=E_bad), "corrupted master-equation weight PASSED"
    # the mod-27 curve promoted verbatim (drop the four-pair 27u^4 term and
    # the mod-81-only digits): E27*H^2 lifted -- must NOT prove the claim
    E27 = {(9, 0): 1, (8, 0): 80, (6, 1): 56, (5, 2): 72, (4, 2): 63,
           (2, 3): 63}  # H^2*(H^7 - H^6 - 25uH^4 - 9u^2H^3 - 18u^2H^2 - 18u^3)
    assert broken(E=E27), "mod-27 curve stand-in PASSED"
    # the four-pair stack W(2,2,2,2) = 68314 is the ONE weight new at this
    # level and the one surviving weight with no direct-enumeration
    # cross-check (DP-only; validate() covers k <= 3). Only its mod-3 digit
    # (= 1) enters. Both wrong digits must break the certificate:
    for digit in (0, 2):
        Ew = dict(E81); dpw = dict(dp)
        if digit == 0:
            del Ew[(0, 4)], dpw[(0, 4)]
        else:                       # W == 2 mod 3: Ehat = 54, (l+1)What = 27
            Ew[(0, 4)] = (-54) % MOD
            dpw[(0, 4)] = 27
        assert broken(E=Ew, dp=dpw), f"W(2^4) digit {digit} PASSED"
    print("G. sensitivity: all 9 deliberate corruptions break the "
          "certificate (nonzero remainder), including both wrong mod-3 "
          "digits of the DP-only weight W(2,2,2,2)  OK")

    print(f"\nADVERSARY AUDIT: ALL CHECKS PASS  [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
