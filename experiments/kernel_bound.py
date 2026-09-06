#!/usr/bin/env python3
"""Bui-style kernel-method upper-bound extractor (arXiv:2510.06806) + Eden closed
form. For a convolution GF system reducing to a kernel  x = z/Q(z)  (Q = poly,
nonneg coeffs), the growth-constant upper bound is  lambda = Q'(z*)  where z* is
the smallest positive root of  Q(z) - z*Q'(z) = 0  (the saddle/branch point,
dx/dz=0). Validated on the polyiamond result lambda_T <= 3.6108.

Once the KING twig/neighborhood convolution system is derived (the load-bearing
geometric lemma, docs/proofs/polyplet-upper-bound.md), feed its kernel Q here to
read off the polyplet upper bound. MUST clear the sanity gate: result > a(n)
ratios (~6.9) and > mu_13 = 6.306, and the rook analog must reproduce a TRUE
polyomino bound (not < 4.06).
"""
import numpy as np

def eden_bound(K):
    """Crudest twig (Eden) bound: alphabet = all 2^K occupancy patterns of the K
    newly-exposed neighbors per BFS step. lambda <= K^K/(K-1)^(K-1)."""
    return K**K / (K-1)**(K-1)

def kernel_bound(Qc):
    """Qc = coeffs of Q(z) low->high (x = z/Q(z)). Return lambda = Q'(z*), z* the
    smallest positive root of Q(z) - z Q'(z)."""
    Q  = np.polynomial.Polynomial(Qc)
    dQ = Q.deriv()
    # saddle: Q(z) - z*dQ(z) = 0
    sad = Q - np.polynomial.Polynomial([0,1])*dQ
    roots = sad.roots()
    pos = sorted(r.real for r in roots if abs(r.imag) < 1e-9 and r.real > 1e-9)
    if not pos: raise ValueError("no positive saddle root")
    z = pos[0]
    return dQ(z), z

print("=== Eden closed-form bounds  K^K/(K-1)^(K-1) ===")
for K, lat in [(3, "rook/polyomino"), (5, "king/polyplet")]:
    print(f"  K={K} ({lat}): lambda <= {eden_bound(K):.4f}")

print("\n=== Bui kernel bound, VALIDATION on polyiamonds ===")
# triangular (Bui arXiv:2510.06806): x = z/(1+z+z^2+z^3)
lam, z = kernel_bound([1,1,1,1])
print(f"  Q = 1+z+z^2+z^3  ->  z* = {z:.5f},  lambda_T <= {lam:.5f}   (published: 3.6108)")
assert abs(lam - 3.6108) < 1e-3, "polyiamond validation FAILED"
print("  VALIDATION PASSED (matches 3.6108).")

print("\n=== KING kernel: PENDING the geometric lemma ===")
print("  Derive king twig/neighborhood convolution system -> Q_king(z), then:")
print("  kernel_bound(Q_king)  ->  polyplet upper bound.  (Sanity-gate the result.)")
