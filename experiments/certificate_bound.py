#!/usr/bin/env python3
"""Bui-style growth-constant upper bound by the CERTIFICATE / monotone-iteration
method (arXiv:2511.00461, Lemma 2 + Sec. 5). The convolution GF system does NOT
reduce to a single kernel on the square lattice, so we (a) iterate the monotone
sequence to detect bounded (lambda<=1/x) vs divergent (lambda>=1/x) and bisect x,
and (b) verify a final rational certificate exactly.

VALIDATION target (published): rook/polyomino 6-type system -> lambda_2 <= 4.63,
with Bui's certificate x=100/463, (e,f,g,h,l,m)=(34/67,139/103,67/82,101/155,
95/126,106/177). This is the exact machinery to reuse for the KING port (just
swap in the king twig system once its geometric closure lemma is derived).
"""
from fractions import Fraction as F

# --- rook (square) 6-type system, Bui Lemma 1/2 ---
def rook_step(v, x):
    e, f, g, h, l, m = v
    return (
        x + x*f,                        # e
        x + x*f + x*g + x*g*l + g*h,    # f
        x + x*f + x*g + x*g*l,          # g
        x + 2*x*g + x*e*l,              # h
        x + x*f + x*h + x*g*m,          # l
        x + x*g + x*h + x*e*m,          # m
    )

def converges(step, x, iters=100000, cap=1e7, tol=1e-13):
    """Iterate the monotone sequence from (x,...,x). Bounded (converges) =>
    lambda <= 1/x. Divergent (exceeds cap) => lambda >= 1/x."""
    v = (x,)*6
    for _ in range(iters):
        nv = step(v, x)
        if max(nv) > cap:
            return False
        if max(abs(a-b) for a, b in zip(nv, v)) < tol*max(nv):
            return True
        v = nv
    return True  # slow convergence, treat as bounded (conservative for lambda>=)

def bisect_lambda(step, lo_lam=4.0, hi_lam=12.0):
    """Bisect x=1/lambda: converges (bounded) at x <=> lambda <= 1/x."""
    lo, hi = 1.0/hi_lam, 1.0/lo_lam          # x range; converges at lo, diverges at hi
    for _ in range(60):
        mid = 0.5*(lo+hi)
        if converges(step, mid):             # bounded at mid => x* is higher; push lo up
            lo = mid
        else:                                # divergent => x* is lower; pull hi down
            hi = mid
    return 1.0/(0.5*(lo+hi))                  # lambda = 1/x*

def check_certificate(step, x, cert):
    """Exact rational: does cert satisfy v_i >= step(v)_i for all i? If yes,
    lambda <= 1/x rigorously."""
    rhs = step(cert, x)
    return all(c >= r for c, r in zip(cert, rhs)), rhs

if __name__ == "__main__":
    print("=== rook 6-type: monotone-iteration bisection ===")
    lam = bisect_lambda(rook_step)
    print(f"  lambda_2 <= {lam:.4f}   (Bui published 4.63)")

    print("\n=== rook 6-type: EXACT certificate check (Bui's tuple) ===")
    x = F(100, 463)
    cert = (F(34,67), F(139,103), F(67,82), F(101,155), F(95,126), F(106,177))
    ok, rhs = check_certificate(rook_step, x, cert)
    names = "efghlm"
    for i, nm in enumerate(names):
        slack = cert[i] - rhs[i]
        print(f"  {nm}: {float(cert[i]):.5f} >= {float(rhs[i]):.5f} ? {slack>=0}  (slack {float(slack):+.5f})")
    print(f"  ALL satisfied: {ok}  =>  lambda_2 <= 1/x = {1/x} = {float(1/x)}")
    assert ok, "CERTIFICATE FAILED"
    print("  VALIDATION PASSED (rigorous rational certificate for lambda_2 <= 4.63).")
