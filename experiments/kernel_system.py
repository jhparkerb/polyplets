#!/usr/bin/env python3
"""Reduce a Bui-style convolution GF SYSTEM to its dominant singularity and read
off the growth-constant upper bound. General infrastructure for the king port:
the king twig system will be several equations, not a single kernel.

Input: equations {G_i = rhs_i(x, G_1..G_m)} (polynomial in x and the G's), and a
target GF whose radius of convergence 1/lambda we want. Method: eliminate the
other G's to a single P(x, G)=0, then the algebraic-function singularity is the
smallest x>0 with P=0 AND dP/dG=0 simultaneously (branch point) -> resultant.
lambda = 1/x*.

Validated on polyiamonds (must give 3.6108)."""
import sympy as sp

def growth_bound(eqs, target, x, verbose=False):
    """eqs: dict {G: rhs}. target: the G symbol. x: marking symbol. Returns lambda."""
    Gs = list(eqs.keys())
    # P(x, target) = 0 : eliminate the non-target G's via resultants
    polys = [sp.together(G - rhs).as_numer_denom()[0] for G, rhs in eqs.items()]
    others = [G for G in Gs if G != target]
    cur = polys
    for G in others:
        nxt = []
        # pick one poly containing G to eliminate with
        pivot = next(p for p in cur if p.has(G))
        for p in cur:
            if p is pivot: continue
            nxt.append(sp.resultant(p, pivot, G) if p.has(G) else p)
        cur = [sp.expand(p) for p in nxt if p != 0]
    P = sp.factor(cur[0])
    # strip spurious factors independent of target
    P = sp.Poly(P, target)
    if verbose: print("  P(x,G):", P.as_expr())
    dP = P.diff(target)
    # branch point: resultant_G(P, dP) = 0 -> poly in x
    R = sp.resultant(P.as_expr(), dP.as_expr(), target)
    # drop spurious monomial x^k factors; keep the real singularity polynomial
    _, facs = sp.factor_list(R)
    core = sp.Integer(1)
    for f, m in facs:
        if sp.Poly(f, x).degree() > 0 and f != x:
            core *= f
    if verbose: print("  singularity poly in x:", sp.expand(core))
    import numpy as np
    coeffs = [float(c) for c in sp.Poly(core, x).all_coeffs()]
    xs = sorted(r.real for r in np.roots(coeffs)
                if abs(r.imag) < 1e-9 and r.real > 1e-9)
    return 1.0 / xs[0]

if __name__ == "__main__":
    x = sp.Symbol('x', positive=True)
    g, h, k = sp.symbols('g h k')
    # polyiamond (Bui): g=1+xgh, h=1+xgk, k=1+xg
    eqs = {g: 1 + x*g*h, h: 1 + x*g*k, k: 1 + x*g}
    lam = growth_bound(eqs, g, x, verbose=True)
    print(f"\n  polyiamond lambda_T <= {lam:.5f}   (published 3.6108)")
    assert abs(lam - 3.6108) < 1e-3, "VALIDATION FAILED"
    print("  VALIDATION PASSED.")
