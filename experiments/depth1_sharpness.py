#!/usr/bin/env python3
"""Onset sharpness at depth 1, proved: D_1(k) != 0 for every k >= 1, mod 3.

The diagonal formula T(n, n-k) = P_k(n) 3^(n-1-3k) is proved for n >= 2k+1
(docs/proofs/diagonal-law.md).  Sharpness is the statement that it fails at
n = 2k, i.e. that the depth-1 defect D_1(k) = T(2k,k) - P_k(2k) / 3^(k+1) is
nonzero for every k >= 1.

No tail bound is needed.  Put N(x) = sum_k N_k x^k, N_0 = 0 and
N_k = 3^(k+1) D_1(k) in Z for k >= 1 (an integer: P_k has degree k and is
integer-valued at the k+1 consecutive integers 2k+1..3k+1, hence on Z) -- the
normalization of results/below-onset.md sec 3, annihilated by the DERIVED
quartic Phi (experiments/severance_w2_kernel.py, gated by
experiments/severance_w2_gate.py).  Reduce Phi mod 3.  It factors:

    Phi(x, W) = 2 (W - 1)^3 ((1 + x) W - x)   in F_3[x, W].            (*)

F_3[[x]] is an integral domain, so Phi(x, Nbar) = 0 leaves exactly two
branches: Nbar = 1, or (1 + x) Nbar = x.  The first needs N_1 = 0 mod 3 and
N_1 = 4, so the second holds:

    Nbar = x / (1 + x) = sum_{k>=1} (-1)^(k+1) x^k,

hence N_k = (-1)^(k+1) mod 3 for every k >= 1.  In particular 3 does not
divide N_k, so N_k != 0 and D_1(k) = N_k / 3^(k+1) != 0.  (The same line
proves what sec 2 of the note had only observed: D_1(k) in lowest terms has
denominator exactly 3^(k+1).)

This script is the fail-closed check of every step that is a computation:

  A. rebuild D_1(k) exactly to k = K by the gap walk (no Phi, no P_k) and
     confirm N_k is an integer throughout;
  B. confirm Phi(x, N(x)) = 0 through x^K in exact integers;
  C. confirm (*) as an identity in F_3[x, W], coefficient by coefficient;
  D. confirm N_1 = 4, which kills the Nbar = 1 branch;
  E. confirm the conclusion against the rebuilt series: N_k = (-1)^(k+1)
     mod 3 and D_1(k) != 0 for every 1 <= k <= K.

  --selftest: RED control.  A one-coefficient perturbation of Phi must break
  C, and a one-term perturbation of N must break B and E.

Exit 0 = green; anything else = red.

Run from repo root: python3 experiments/depth1_sharpness.py [K]
"""
import os
import sys
import time
from fractions import Fraction as Fr

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import walk_families, series_D1            # noqa: E402
from depth1_recurrence import PHI_COEFFS, x                     # noqa: E402

KDEF = 200
FAILURES = []


def check(ok, label):
    print(f"   [{'ok ' if ok else 'RED'}] {label}")
    if not ok:
        FAILURES.append(label)
    return ok


def phi_int_coeffs(perturb=None):
    """Phi as 5 ascending-power integer lists (W^0..W^4); perturb = (j, i)."""
    out = []
    for e in PHI_COEFFS:
        p = sp.Poly(sp.expand(sp.sympify(e)), x).all_coeffs()[::-1]
        out.append([int(c) for c in p])
    if perturb is not None:
        j, i = perturb
        out[j][i] += 1
    return out


def phi_at_series(phi, N, K):
    """Coefficients 0..K of Phi(x, N(x)) in exact integers."""
    powers = [[1] + [0] * K]
    for _ in range(len(phi) - 1):
        cur, nxt = powers[-1], [0] * (K + 1)
        for a in range(K + 1):
            ca = cur[a]
            if ca:
                for b in range(K + 1 - a):
                    if N[b]:
                        nxt[a + b] += ca * N[b]
        powers.append(nxt)
    tot = [0] * (K + 1)
    for j, cs in enumerate(phi):
        for i, ci in enumerate(cs):
            if ci:
                for m in range(K + 1 - i):
                    tot[m + i] += ci * powers[j][m]
    return tot


def factorization_holds(phi):
    """Phi = 2 (W-1)^3 ((1+x) W - x) in F_3[x, W], coefficient by coefficient."""
    W = sp.Symbol('W')
    lhs = sum(sum(c * x ** i for i, c in enumerate(cs)) * W ** j
              for j, cs in enumerate(phi))
    rhs = 2 * (W - 1) ** 3 * ((1 + x) * W - x)
    return sp.Poly(sp.expand(lhs - rhs), W, x, modulus=3).is_zero


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else KDEF
    selftest = '--selftest' in sys.argv
    t0 = time.time()

    print(f"== A. gap-walk rebuild of D_1 to k = {K}")
    D1 = series_D1(walk_families(K), K)
    Nq = [Fr(0)] + [Fr(3) ** (k + 1) * D1[k] for k in range(1, K + 1)]
    check(all(v.denominator == 1 for v in Nq), "N_k integral for all k <= K")
    N = [int(v) for v in Nq]
    print(f"       {time.time() - t0:.1f}s; N_1..N_5 = {N[1:6]}")

    print("== B. the derived quartic annihilates the rebuilt series")
    phi = phi_int_coeffs()
    check(all(c == 0 for c in phi_at_series(phi, N, K)),
          f"Phi(x, N(x)) = 0 through x^{K} in exact integers")

    print("== C. the mod-3 factorization")
    check(factorization_holds(phi),
          "Phi = 2 (W-1)^3 ((1+x) W - x) in F_3[x, W]")

    print("== D. branch selection")
    check(N[1] % 3 != 0, f"N_1 = {N[1]} is nonzero mod 3, so Nbar != 1")

    print("== E. the conclusion, against the rebuilt series")
    check(all(N[k] % 3 == (1 if k % 2 else 2) for k in range(1, K + 1)),
          f"N_k = (-1)^(k+1) mod 3 for 1 <= k <= {K}")
    check(all(D1[k] != 0 for k in range(1, K + 1)),
          f"D_1(k) != 0 for 1 <= k <= {K}")

    if selftest:
        print("== RED control (these must all report broken)")
        check(not factorization_holds(phi_int_coeffs(perturb=(4, 0))),
              "perturbed Phi breaks the mod-3 factorization")
        Nbad = N[:]
        Nbad[7] += 1
        check(any(c != 0 for c in phi_at_series(phi, Nbad, K)),
              "perturbed N breaks annihilation")
        check(not all(Nbad[k] % 3 == (1 if k % 2 else 2)
                      for k in range(1, K + 1)),
              "perturbed N breaks the mod-3 congruence")

    print()
    if FAILURES:
        print(f"RED: {len(FAILURES)} check(s) failed: {FAILURES}")
        return 1
    print(f"GREEN: sharpness proved for every k >= 1 "
          f"({time.time() - t0:.1f}s, K = {K})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
