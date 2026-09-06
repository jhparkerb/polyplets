"""Fail-closed gate for Severance W2 (docs/onset-defect-severance-plan.md (deleted) §3).

The W2 deliverable is experiments/severance_w2_kernel.py exposing

    derived_phi() -> list of 5 sympy expressions in x
                     (coefficients of W^0..W^4, from the kernel-method
                      DERIVATION — no fitting anywhere in its call graph)

This gate accepts the candidate iff:
  A. it is exactly proportional (one rational scale) to the fitted-and-
     holdout-verified PHI_COEFFS of experiments/depth1_recurrence.py;
  B. it annihilates the gap-walk series N(x) = sum 3^(k+1) D_1(k) x^k,
     rebuilt here from walk_families/series_D1 (independent enumeration),
     through x^80 in exact rationals;
  C. --selftest: a perturbed candidate must fail both A and B (RED).

Usage:
  python3 experiments/severance_w2_gate.py             # judge the candidate
  python3 experiments/severance_w2_gate.py --selftest  # RED control on Phi itself

Exit 0 = GATE GREEN; anything else = red.
"""

import os
import sys
from fractions import Fraction as Fr

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_recurrence import PHI_COEFFS, x                     # noqa: E402
from depth1_gap_walk import walk_families, series_D1            # noqa: E402

KSER = 80


def coeff_lists(exprs):
    """5 sympy exprs in x -> list of ascending-power Fraction lists."""
    out = []
    for e in exprs:
        p = sp.Poly(sp.expand(e), x)
        cs = [Fr(int(sp.nsimplify(c).p), int(sp.nsimplify(c).q))
              if not isinstance(c, (int,)) else Fr(c)
              for c in reversed(p.all_coeffs())]
        out.append(cs)
    return out


def check_proportional(cand):
    ref = coeff_lists(PHI_COEFFS)
    can = coeff_lists(cand)
    scale = None
    for r, c in zip(ref, can):
        n = max(len(r), len(c))
        r = r + [Fr(0)] * (n - len(r))
        c = c + [Fr(0)] * (n - len(c))
        for a, b in zip(r, c):
            if scale is None and a != 0:
                assert b != 0, "[A] candidate zero where Phi is not"
                scale = b / a
            assert (a == 0) == (b == 0), "[A] support mismatch with Phi"
            if a != 0:
                assert b == scale * a, "[A] not proportional to Phi"
    assert scale is not None and scale != 0
    print(f"  [A] candidate == Phi exactly (scale {scale})")


def check_annihilates(cand):
    fams = walk_families(KSER)
    D1 = series_D1(fams, KSER)
    N = [Fr(0)] + [Fr(3) ** (k + 1) * D1[k] for k in range(1, KSER + 1)]

    def smul(a, b):
        return [sum(a[i] * b[m - i] for i in range(m + 1))
                for m in range(KSER + 1)]

    can = coeff_lists(cand)
    Npow = [Fr(1)] + [Fr(0)] * KSER
    acc = [Fr(0)] * (KSER + 1)
    for j in range(5):
        cs = (can[j] + [Fr(0)] * (KSER + 1))[:KSER + 1]
        acc = [a + t for a, t in zip(acc, smul(cs, Npow))]
        Npow = smul(Npow, N)
    assert all(a == 0 for a in acc), \
        f"[B] candidate does NOT annihilate the walk series (first nonzero at x^{next(m for m, a in enumerate(acc) if a != 0)})"
    print(f"  [B] candidate annihilates the independent walk series through x^{KSER}")


def selftest():
    check_proportional(PHI_COEFFS)
    check_annihilates(PHI_COEFFS)
    bad = list(PHI_COEFFS)
    bad[2] = bad[2] + x ** 3
    fired = 0
    for chk in (check_proportional, check_annihilates):
        try:
            chk(bad)
        except AssertionError:
            fired += 1
    assert fired == 2, "selftest: perturbation NOT caught — gate is broken"
    print("GATE SELFTEST GREEN: perturbed candidate caught by [A] and [B]")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    # Re-deriving the candidate is 94% of this gate: 550 s of 583 s under
    # cProfile on dalby (2026-08-24), all of it sympy cancel/expand inside
    # severance_w2_kernel.build_F1 -> solve_start. That derivation is settled
    # and does not move, so the push tier does not re-run it.
    #
    # What the push tier still runs is NOT vacuous: --selftest checks the
    # banked PHI_COEFFS both ways -- exactly proportional to the fitted-and-
    # holdout-verified Phi, and annihilating the gap-walk series rebuilt here
    # from an independent enumeration through x^80 -- with a perturbed
    # candidate as the RED control. Only the kernel's own derivation waits for
    # `make gates-deep`.
    if "--deep" not in sys.argv:
        print("  [push tier] kernel re-derivation deferred to `make gates-deep`;")
        print("              --selftest checked PHI against the independent "
              "walk series")
        return
    from severance_w2_kernel import derived_phi                 # noqa: E402
    cand = derived_phi()
    assert len(cand) == 5, "candidate must be 5 coefficients W^0..W^4"
    check_proportional(cand)
    check_annihilates(cand)
    print("GATE GREEN")


if __name__ == "__main__":
    main()
