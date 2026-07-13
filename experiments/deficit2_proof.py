#!/usr/bin/env python3
"""Symbolic proof of the deficit-2 spine law (see results/ternary-spine.md):

    T(3m+2, 2m+1) == 2 (mod 3)  for all m >= 1,
    equivalently P_{m+1}(3m+2) == 18 (mod 27).

Method: the family GF D(v) = sum_m P_{m+1}(3m+2) v^m is a diagonal of
G(u) H(u)^n, so formal Lagrange-Buermann (valid over Z/27) gives
1 + v D(v) = Phi(u0) v / (u0 (1 - v B'(u0))) with u0 = v H(u0)^3,
Phi = G H^2. Parametrizing by u (v = u/H^3), the claim
D = 5 + 18v/(1-v) becomes a rational identity on the mod-27 master curve

  E(H,u) = H^7 - H^6 - 25u H^4 - 9u^2 H^3 - 18u^2 H^2 - 18u^3 == 0 (mod 27)

with H' = -E_u/E_H and the derived G-formula. Cross-multiplying yields a
polynomial N(H,u); E is MONIC in H, so N mod (E, 27) is decided by exact
division -- the remainder is identically zero (asserted below). All
cleared denominators are power-series units, so the series identity and
hence the law follow, in the same conditional frame as the rest of the
ladder (master equation + boundary residue, both derived from the gas).
"""
import sympy as sp


def main():
    H, u = sp.symbols('H u')
    E = H**7 - H**6 - 25*u*H**4 - 9*u**2*H**3 - 18*u**2*H**2 - 18*u**3
    A = sp.diff(E, H)
    B_ = -sp.diff(E, u)
    Dp = H**6 + 23*u*H**4 + 18*u**2*H**3 + 18*u**3
    N = sp.expand((H**2 + 15*u)**2 * (A*H - u*B_) * H * H**3 * (H**3 - u)
                  - (H**3*(H**3 - u) + 5*u*(H**3 - u) + 18*u**2)
                  * Dp * (A*H - 3*u*B_))
    q, r = sp.div(sp.Poly(N, H, domain='QQ[u]'),
                  sp.Poly(E, H, domain='QQ[u]'))
    for c in sp.Poly(r, H).all_coeffs():
        for cc in sp.Poly(sp.expand(c), u).all_coeffs():
            assert sp.Rational(cc).q == 1 and int(cc) % 27 == 0, cc
    print("deficit-2 law: N == 0 mod (E, 27) -- "
          "T(3m+2,2m+1) == 2 (mod 3) PROVED  OK")


if __name__ == "__main__":
    main()
