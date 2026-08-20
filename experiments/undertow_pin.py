#!/usr/bin/env python3
"""Undertow: pin P_k from BELOW-onset cells, so the tower stops needing the tall sweep.

The standing rule (docs/b1-closure-plan.md §1) is that level k costs two
above-onset anchors, T(2k+1, k+1) and T(2k+2, k+2) -- the two TALLEST cells on
its diagonal.  That is what makes row 40 expensive: level 19's anchors are
T(39,20) and T(40,21), and T(40,21) is the 36-hour cell.

But the grand form (docs/proofs/grand-form.md, Lean-complete) says a level
carries exactly two new constants,

    P_k(n) = [y^k] exp( sum_j (a_j + b_j n) y^j ),

so ANY two independent linear equations in (a_k, b_k) pin it -- and Severance W3
(results/onset-defect-depths234.md) supplies them from cells that are far SHORTER
than the onset anchors.  For a below-onset cell at depth j,

    T(2k+1-j, k+1-j) = P_k(2k+1-j) * 3^(2k-3k-j) + D_j(k),                  (*)

with D_j(k) computed ab initio from bounded-excess cluster weight families --
no triangle, no wired P_k.  Its left side sits at height k+1-j, i.e. j rows
BELOW the onset anchor.  Two depths, two equations, one level pinned.

What this file does:

  --verify   For every wired level k, re-derive (a_k, b_k) from two below-onset
             cells and compare against the wired table.  This is the claim's
             whole content and it is checkable on levels we already trust.
  --predict  Pin levels past the wired table from banked cells only, and print
             the cells they predict -- including T(41,H), which no sweep has
             ever produced.
  --selftest RED controls: a perturbed D_j must break the pin, and one equation
             must fail to determine the level.

Run: python3 experiments/undertow_pin.py --verify
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from slope2_law_vs_truth import read_pk, read_tri, law  # noqa: E402


# ------------------------------------------------------------------ polynomials
# Polynomials in n, ascending coefficient lists of Fractions.

def padd(u, v):
    m = max(len(u), len(v))
    return [(u[i] if i < len(u) else F(0)) + (v[i] if i < len(v) else F(0))
            for i in range(m)]


def pmul(u, v):
    if not u or not v:
        return []
    out = [F(0)] * (len(u) + len(v) - 1)
    for i, a in enumerate(u):
        if a:
            for j, b in enumerate(v):
                if b:
                    out[i + j] += a * b
    return out


def peval(u, n):
    v = F(0)
    for c in reversed(u):
        v = v * n + c
    return v


def ptrim(u):
    while u and u[-1] == 0:
        u.pop()
    return u


def wired_poly(P, k):
    """Wired P_k as an ascending-coefficient polynomial in n."""
    coeffs, den = P[k]                      # descending, over a denominator
    return [F(c, den) for c in reversed(coeffs)]


# ------------------------------------------------------------------ grand form
# exp(sum_j (a_j + b_j n) y^j) truncated at y^K; coefficient of y^k is a
# polynomial in n.  Computed by the standard exp-of-series recurrence
#   k * E_k = sum_{j=1..k} j * L_j * E_{k-j},   E_0 = 1.

def grand_form(ab, K):
    """ab: dict j -> (a_j, b_j).  Returns list E[0..K] of polynomials in n."""
    L = {j: [F(a), F(b)] for j, (a, b) in ab.items()}
    E = [[F(1)]]
    for k in range(1, K + 1):
        acc = []
        for j in range(1, k + 1):
            if j in L:
                acc = padd(acc, pmul([F(j) * c for c in L[j]], E[k - j]))
        E.append(ptrim([c / k for c in acc]))
    return E


def extract_ab(P, kmax):
    """(a_j, b_j) for j = 1..kmax from the wired table, with the grand form's
    own consistency as the check: P_k - (lower-level part) must be LINEAR."""
    ab = {}
    for k in range(1, kmax + 1):
        E = grand_form(ab, k)               # levels < k only; E[k] is the rest
        rem = ptrim(padd(wired_poly(P, k), [-c for c in E[k]]))
        if len(rem) > 2:
            raise AssertionError(
                f"grand form violated at k={k}: residual degree {len(rem)-1} > 1")
        a = rem[0] if len(rem) > 0 else F(0)
        b = rem[1] if len(rem) > 1 else F(0)
        ab[k] = (a, b)
    return ab


# ------------------------------------------------------------------ the pin
def pow3(e):
    return F(3) ** e if e >= 0 else F(1, 3 ** (-e))


def pin_level(k, ab_lower, depths, tri, Dj):
    """Solve (a_k, b_k) from below-onset cells at the two depths given.

    Dj: dict j -> list indexed by k of exact D_j(k).
    Returns (a_k, b_k), or raises if a cell is missing / the system is singular.
    """
    E = grand_form(ab_lower, k)             # levels < k; E[k] = Q_k(n)
    Qk = E[k]
    rows, rhs = [], []
    for j in depths:
        n, H = 2 * k + 1 - j, k + 1 - j
        if (n, H) not in tri:
            raise KeyError(f"cell T({n},{H}) not banked")
        s = pow3(n - 1 - 3 * k)
        # T = (a_k + b_k n + Q_k(n)) * s + D_j(k)
        rows.append((s, s * n))
        rhs.append(F(tri[(n, H)]) - Dj[j][k] - peval(Qk, n) * s)
    (p, q), (r, t) = rows
    det = p * t - q * r
    if det == 0:
        raise AssertionError(f"singular pin at k={k} with depths {depths}")
    a = (rhs[0] * t - q * rhs[1]) / det
    b = (p * rhs[1] - rhs[0] * r) / det
    return a, b


def load_depths(jmax, K):
    """Dj[j][k] for j = 1..jmax, k = 0..K, all ab initio."""
    from depth1_gap_walk import walk_families, series_D1
    from severance_w3_depths import D_series
    out = {1: list(series_D1(walk_families(K), K))}
    for j in range(2, jmax + 1):
        out[j] = list(D_series(j, K))
    return out


# ------------------------------------------------------------------ modes
def verify(jmax=3):
    P, tri = read_pk(), read_tri()
    kmax = max(P)
    ab = extract_ab(P, kmax)
    print(f"grand form consistent on wired levels k = 1..{kmax} "
          f"(every residual linear in n)")
    Dj = load_depths(jmax, kmax)
    print(f"ab-initio depth series loaded for j = 1..{jmax}, k <= {kmax}")

    ok = bad = skip = 0
    for k in sorted(ab):
        cells = [j for j in range(1, jmax + 1)
                 if k + 1 - j >= 1 and (2 * k + 1 - j, k + 1 - j) in tri]
        if len(cells) < 2:
            skip += 1
            continue
        depths = cells[:2]
        got = pin_level(k, {j: ab[j] for j in ab if j < k}, depths, tri, Dj)
        want = ab[k]
        tallest = k + 1 - min(depths)
        onset_h = k + 2
        mark = "OK " if got == want else "BAD"
        if got == want:
            ok += 1
        else:
            bad += 1
        print(f"  k={k:2d} depths={depths} pin height {tallest:2d} "
              f"(onset anchors need {onset_h:2d})  {mark}")
        if got != want:
            print(f"      got  a={got[0]} b={got[1]}")
            print(f"      want a={want[0]} b={want[1]}")
    print(f"\nverify: {ok} levels re-derived exactly, {bad} wrong, {skip} skipped")
    return bad == 0 and ok >= 10


def selftest(jmax=3):
    P, tri = read_pk(), read_tri()
    kmax = max(P)
    ab = extract_ab(P, kmax)
    Dj = load_depths(jmax, kmax)
    k = 15
    lower = {j: ab[j] for j in ab if j < k}

    bad = {j: list(v) for j, v in Dj.items()}
    bad[1][k] += 1
    got = pin_level(k, lower, [1, 2], tri, bad)
    assert got != ab[k], "RED CONTROL FAILED: perturbed D_1 still pinned the level"
    print("RED 1 GREEN: a perturbed D_j breaks the pin")

    try:
        pin_level(k, lower, [1, 1], tri, Dj)
    except AssertionError:
        print("RED 2 GREEN: one equation twice is refused as singular")
    else:
        raise SystemExit("RED CONTROL FAILED: singular system accepted")

    wrong = dict(lower)
    wrong[k - 1] = (lower[k - 1][0] + 1, lower[k - 1][1])
    got = pin_level(k, wrong, [1, 2], tri, Dj)
    assert got != ab[k], "RED CONTROL FAILED: corrupted lower level still pinned"
    print("RED 3 GREEN: a corrupted lower level breaks the pin")


def predict(jmax=3, kmax_new=21):
    """Pin levels past the wired table from banked cells, then print what they
    predict -- the cells the tower could not reach before."""
    P, tri = read_pk(), read_tri()
    kw = max(P)
    ab = extract_ab(P, kw)
    Dj = load_depths(jmax, kmax_new)

    for k in range(kw + 1, kmax_new + 1):
        cells = [j for j in range(1, jmax + 1)
                 if (2 * k + 1 - j, k + 1 - j) in tri]
        if len(cells) < 2:
            print(f"  k={k}: only {len(cells)} banked below-onset cells at "
                  f"j <= {jmax} -- needs deeper depths")
            continue
        depths = cells[:2]
        ab[k] = pin_level(k, {j: ab[j] for j in ab if j < k}, depths, tri, Dj)
        print(f"  k={k:2d} pinned from depths {depths} "
              f"= cells T({2*k+1-depths[0]},{k+1-depths[0]}), "
              f"T({2*k+1-depths[1]},{k+1-depths[1]})")

    print("\npredicted cells (formula vs banked where banked exists):")
    E = grand_form(ab, max(ab))
    for k in sorted(ab):
        for n in range(2 * k + 1, 43):
            H = n - k
            if H < 1:
                continue
            v = peval(E[k], n) * pow3(n - 1 - 3 * k)
            if (n, H) in tri:
                if k > kw or n >= 40:
                    flag = "match" if F(tri[(n, H)]) == v else "MISMATCH"
                    print(f"  T({n},{H}) k={k}: {flag}")
            elif n >= 41:
                print(f"  T({n},{H}) k={k}: {v}  [NEW -- no sweep has this cell]")


def main():
    jmax = 3
    for a in sys.argv[1:]:
        if a.startswith("--jmax="):
            jmax = int(a.split("=")[1])
    if "--selftest" in sys.argv:
        selftest(jmax)
    elif "--predict" in sys.argv:
        predict(jmax)
    else:
        if not verify(jmax):
            raise SystemExit("VERIFY RED")
        print("VERIFY GREEN")


if __name__ == "__main__":
    main()
