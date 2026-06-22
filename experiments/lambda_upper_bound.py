#!/usr/bin/env python3
"""Rigorous UPPER bound on the king-lattice (polyplet, A006770) growth constant lambda via the
Eden / Klarner-Rivest spanning-encoding (Barequet-Shalah form, arXiv:1906.11447). Each non-root
king cell, discovered from an already-processed neighbor, need encode only its UNDETERMINED
king-neighbors; the need-set has size 5 (diagonal discoverer) or 3 (edge discoverer). This injects
size-n animals into weighted encoding-trees, so lambda <= 1/x* where x* is the GF branch point.
By symmetry the 8 discoverer directions reduce to 2 types (edge Te, diagonal Td):
  Te = x (1+Te)(1+Td)^2     (edge: 1 edge child-slot + 2 diagonal)
  Td = x (1+Te)^2 (1+Td)^3  (diagonal: 2 edge + 3 diagonal child-slots)
Verified below: square all-edge analog -> Eden 27/4 = 6.75 exactly; uniform (1+x)^5 -> 3125/256."""
def branch(step):
    lo, hi = 0.0, 0.5
    for _ in range(90):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if step(m) is None else (m, hi)
    return 1.0 / ((lo + hi) / 2)
def king(x, n=4000):
    Te = Td = 0.0
    for _ in range(n):
        a = x*(1+Te)*(1+Td)**2; b = x*(1+Te)**2*(1+Td)**3
        if a > 1e6 or b > 1e6: return None
        Te, Td = a, b
    return (Te, Td)
def sq(x, n=4000):
    T = 0.0
    for _ in range(n):
        t = x*(1+T)**3
        if t > 1e6: return None
        T = t
    return T
print("king directional twig: lambda <=", round(branch(king), 4))
print("square all-edge sanity:", round(branch(sq), 4), "(= Eden 27/4 = 6.75)")
print("uniform (1+x)^5 = 3125/256 =", round(3125/256, 4))
