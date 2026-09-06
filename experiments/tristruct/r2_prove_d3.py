#!/usr/bin/env python3
"""r2 prover (triangle-structure round 2, agent 2): the d=3 sleeve unit
formula, PROVED on the mod-81 master curve.

    THEOREM (conditional frame below).  For every k >= 3,
        P_k(3k-2) == 27 * r_k  (mod 81),   r_k = (2, 0, 1) for
        k == 0, 1, 2 (mod 3).
    Equivalently, on the d=3 deficit family (n, H) = (3k-2, 2k-2):
        T(3k-2, 2k-2) == 2 (mod 3)  for k == 0 (mod 3),
        T(3k-2, 2k-2) == 1 (mod 3)  for k == 2 (mod 3),
        v3(P_k(3k-2)) >= 4          for k == 1 (mod 3),
    and since r_k != 0 for k !== 1,   v3(P_k(3k-2)) > 3  <=>  k == 1 (mod 3).

Method (the deficit2_proof.py route, one tower level up): the family GF
S(v) = sum_{k>=0} P_k(3k-2) v^k is a diagonal of G(u) H(u)^n, so the formal
Lagrange-Buermann lemma (grand-form.md Step 5, valid over Z and hence mod 81)
with Phi = G H^-2, phi = H^3, u0 = v H(u0)^3 gives
    S(v) = Phi(u0) / (1 - v phi'(u0)).
Parametrizing by u (v = u/H^3, so u0(v(u)) = u by uniqueness of the fixed
point) turns the claim
    S(v) == c0 + c1 v + c2 v^2 + 27(2v^3 + v^5)/(1 - v^3)   (mod 81)
into a rational identity on the mod-81 master curve
    E81 = H^9 - H^8 - 25uH^6 - 36u^2H^5 - 45u^2H^4 - 72u^3H^2 - 27u^4 == 0,
with H' = -E_u/E_H (implicit differentiation of the congruence) and the
derived G mod 81 (r2_tower_mod81.py).  Cross-multiplying yields a polynomial
N(H, u); E81 is MONIC in H, so N mod (E81, 81) is decided by exact division.
The remainder is identically zero mod 81 (asserted below), all cleared
denominators are power-series units mod 81, so the series identity and hence
the theorem follow.

Conditional frame (same as the proved d=1,2 cases): diagonal-law shape
theorem + grand form (both proved, Lean-checked) + the defect-gas renewal
formalism's master equation and boundary residue formula reduced mod 81
(derived in results/diagonal-formula.md / results/triangle-r2-tower-mod81.md (deleted) from
the exact chain identity; verified against banked g_k, h_k mod 81, k <= 17).

Exact integer / symbolic arithmetic throughout.  Runtime ~15 s.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sympy as sp

import r2_tower_mod81 as t81

MOD = 81
KX = t81.KX  # 122


def main():
    t0 = time.time()
    xmul, xinv, xpow = t81.series_ops(MOD)

    # ---- 0. rebuild agent 1's derived objects and re-assert the handoff ----
    P, Gs, Hb, peval = t81.banked(17)
    ints, ebs, ets, dens = t81.survivors_mod(4)
    assert sorted((v, w) for v, _, _, w in ints) == \
        [((2,), 25), ((2, 2), 45), ((2, 2, 2), 72), ((2, 2, 2, 2), 27),
         ((3,), 36)]
    assert ebs == ets
    assert sorted((v, w) for v, _, _, w in ebs) == \
        [((2,), 15), ((2, 2), 27), ((2, 2, 2), 27), ((3,), 27)]
    assert sorted((v, w) for v, _, _, w in dens) == \
        [((2,), 50), ((2, 2), 54), ((2, 2, 2), 45), ((2, 2, 2, 2), 54),
         ((3,), 72)]

    H81 = t81.fixed_point(ints, MOD)
    assert H81[:18] == [h % MOD for h in Hb], "H mod 81 vs banked"

    def eps_series(terms):
        out = [1] + [0] * KX
        for _, k, l, w in terms:
            Hp = xpow(H81, -(k + l))
            for m in range(KX + 1 - k):
                if Hp[m]:
                    out[m + k] = (out[m + k] + w * Hp[m]) % MOD
        return out

    u1 = [0, 1] + [0] * (KX - 1)
    Hd = [((m + 1) * H81[m + 1]) % MOD for m in range(KX)] + [0]  # dH/du
    fac1 = [((1 if m == 0 else 0)
             - xmul(xmul(u1, Hd), xinv(H81))[m]) % MOD
            for m in range(KX + 1)]                               # 1 - uH'/H
    G81 = xmul(xmul(xmul(eps_series(ebs), eps_series(ets)), fac1),
               xinv(eps_series(dens)))
    assert G81[:18] == [g % MOD for g in Gs], "G mod 81 vs banked"
    print("agent-1 objects rebuilt: H81, G81 match banked series mod 81, "
          "k <= 17  OK")

    # ---- 1. the target constants c0, c1, c2 (exact, below family onset) ----
    # S(v) = sum_{k>=0} P_k(3k-2) v^k with P_k(n) = [u^k] G H^n for ALL
    # integer n (grand form for n >= 2k+1; both sides polynomial in n of
    # degree <= k, so the identity extends).  The family claim is k >= 3
    # (= onset 3k-2 >= 2k+1); k = 0,1,2 are fixed constants of the GF.
    c0 = 1                                    # P_0 = 1
    c1 = int(peval(P[1], 1)) % MOD            # P_1(1)  = -20
    c2 = int(peval(P[2], 4)) % MOD            # P_2(4)  = 649
    assert (c1, c2) == (61, 1), (c1, c2)

    # ---- 2. the target identity, numerically on the derived series ----
    # S[k] = [u^k] G81 * H81^(3k-2), k = 0..KX; R(v) coefficient check.
    S = []
    Hn = xpow(H81, -2)
    H3 = xpow(H81, 3)
    for k in range(KX + 1):
        S.append(sum(G81[j] * Hn[k - j] for j in range(k + 1)) % MOD)
        Hn = xmul(Hn, H3)

    def Rcoef(k):
        if k < 3:
            return (c0, c1, c2)[k]
        return (54, 0, 27)[k % 3]

    assert all(S[k] == Rcoef(k) for k in range(KX + 1)), \
        [(k, S[k], Rcoef(k)) for k in range(KX + 1) if S[k] != Rcoef(k)]
    # cross-check against the exact banked P_k where they exist
    for k in range(3, 18):
        assert int(peval(P[k], 3 * k - 2)) % MOD == S[k], k
    print("target series: [v^k] S == c0,c1,c2 then 27*(2,0,1)-cycle, "
          f"k <= {KX}; matches exact banked P_k(3k-2), k = 3..17  OK")

    # ---- 3. the symbolic objects, built from the derived survivor lists ----
    H, u = sp.symbols('H u')
    Dint = max(k + l for _, k, l, _ in ints)      # 8
    Deps = max(k + l for _, k, l, _ in ebs)       # 6
    Dden = max(k + l for _, k, l, _ in dens)      # 8
    assert (Dint, Deps, Dden) == (8, 6, 8)
    E = (H ** (Dint + 1) - H ** Dint
         - sum(w * u ** k * H ** (Dint - k - l) for _, k, l, w in ints))
    assert sp.expand(E - (H**9 - H**8 - 25*u*H**6 - 36*u**2*H**5
                          - 45*u**2*H**4 - 72*u**3*H**2 - 27*u**4)) == 0
    epsp = (H ** Deps
            + sum(w * u ** k * H ** (Deps - k - l) for _, k, l, w in ebs))
    dp = (H ** Dden
          + sum(w * u ** k * H ** (Dden - k - l) for _, k, l, w in dens))
    A = sp.diff(E, H)          # E_H
    B = -sp.diff(E, u)         # -E_u,  so  A H' == B  (mod 81)

    def poly_series(expr):
        """Evaluate a polynomial in (H, u) at (H81(u), u) as a series."""
        out = [0] * (KX + 1)
        for (i, j), c in sp.Poly(expr, H, u).terms():
            Hp = xpow(H81, i)
            cc = int(c) % MOD
            for m in range(KX + 1 - j):
                if Hp[m]:
                    out[m + j] = (out[m + j] + cc * Hp[m]) % MOD
        return out

    # ---- 4. numeric guard: E81 vanishes; implicit differentiation holds ----
    assert all(c == 0 for c in poly_series(E)), "E81(H81, u) == 0 mod 81"
    # Hd is exact only to order KX-1 (its top coefficient needs H[KX+1]);
    # everywhere else Hd enters u-shifted, so only this check is range-limited
    lhs = xmul(poly_series(A), Hd)
    assert lhs[:KX] == poly_series(B)[:KX], "A * H' == B mod 81 (impl diff)"
    print("numeric guards: E81(H81,u) == 0 and E_H*H' == -E_u, mod 81  OK")

    # ---- 5. numeric guard: the Lagrange-Buermann application ----
    # Claim: S(v(u)) == Phi(u)/(1 - 3uH'/H) with v(u) = u/H^3.  (The LB
    # lemma itself is proved -- grand-form.md Step 5 -- this checks my
    # application of it, to series order KX.)
    def compose(a, b):
        assert b[0] == 0
        out = [a[KX] % MOD] + [0] * KX
        for c in reversed(a[:KX]):
            out = xmul(out, b)
            out[0] = (out[0] + c) % MOD
        return out

    fac3 = [((1 if m == 0 else 0)
             - 3 * xmul(xmul(u1, Hd), xinv(H81))[m]) % MOD
            for m in range(KX + 1)]                        # 1 - 3uH'/H
    LHSu = xmul(xmul(G81, xpow(H81, -2)), xinv(fac3))      # Phi/(1-3uH'/H)
    vu = xmul(u1, xpow(H81, -3))                           # v(u) = u/H^3
    assert LHSu == compose(S, vu), "LB application: S(v(u)) == Phi/(1-3uH'/H)"
    print("numeric guard: Lagrange-Buermann application verified to order "
          f"{KX} mod 81  OK")

    # ---- 6. THE CERTIFICATE: cross-multiplied identity, divided by E81 ----
    # LHS  = eps'^2 (AH - uB) / (H^6 dp (AH - 3uB))          [G-formula, H'=B/A]
    # RHS  = Mnum / (H^6 (H^9 - u^3))                        [target, v = u/H^3]
    # Mnum = (c0 H^6 + c1 u H^3 + c2 u^2)(H^9 - u^3) + 27(2u^3 H^6 + u^5)
    # N    = eps'^2 (AH - uB)(H^9 - u^3) - Mnum dp (AH - 3uB)
    Mnum = ((c0 * H**6 + c1 * u * H**3 + c2 * u**2) * (H**9 - u**3)
            + 27 * (2 * u**3 * H**6 + u**5))
    N = sp.expand(epsp**2 * (A * H - u * B) * (H**9 - u**3)
                  - Mnum * dp * (A * H - 3 * u * B))
    # numeric guard first: N must vanish on the series
    assert all(c == 0 for c in poly_series(N)), "N(H81, u) == 0 mod 81"
    q, r = sp.div(sp.Poly(N, H, domain='QQ[u]'),
                  sp.Poly(E, H, domain='QQ[u]'))
    for c in sp.Poly(r, H).all_coeffs():
        for cc in sp.Poly(sp.expand(c), u).all_coeffs():
            assert sp.Rational(cc).q == 1 and int(cc) % MOD == 0, cc
    print("CERTIFICATE: N == 0 mod (E81, 81) by exact division -- "
          "remainder vanishes identically")

    # ---- 7. provenance of the family's banked cells (brief rule 2) ----
    from triangle import Triangle
    tri = Triangle.load()
    print("\nd=3 family cells in the banked triangle "
          "(n, H) = (3k-2, 2k-2), provenance per triangle.py:")
    for k in range(3, 15):
        n, Hh = 3 * k - 2, 2 * k - 2
        T = tri.cell(n, Hh)
        r_pred = (2, 0, 1)[k % 3]
        assert T % 3 == r_pred, (k, T % 3, r_pred)
        print(f"  k={k:2d} (n,H)=({n},{Hh}):  T mod 3 = {T % 3} "
              f"(predicted {r_pred})  [{tri.provenance(n, Hh)}]")

    print(f"\nd=3 sleeve unit formula PROVED (conditional frame in "
          f"docstring)  ALL CHECKS PASS  [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
