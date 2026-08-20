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
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from slope2_law_vs_truth import read_pk, read_tri, law  # noqa: E402


def read_tri_motley(rowdir=None):
    """T(n,H) assembled from MOTLEY's banked C_H rows alone.

    T(n,H) = C_H - 2 C_{H-1} + C_{H-2}, the same telescope cutcount_b1
    --assemble uses.  Nothing here reads the production sweep, so a pin built
    on this triangle owes the incumbent connectivity rule nothing."""
    rowdir = rowdir or os.path.join(ROOT, "results", "cutcount_b1", "rows")
    C = {}
    for fn in os.listdir(rowdir):
        m = re.match(r"C(\d+)\.out$", fn)
        if not m:
            continue
        H = int(m.group(1))
        C[H] = {}
        for line in open(os.path.join(rowdir, fn)):
            p = line.split()
            if len(p) == 2:
                C[H][int(p[0])] = int(p[1])
    if not C:
        raise SystemExit(f"no Motley C rows in {rowdir}")
    tri = {}
    for H in sorted(C):
        for n in C[H]:
            v = C[H][n]
            if H - 1 in C:
                v -= 2 * C[H - 1].get(n, 0)
            elif H - 1 >= 1:
                continue                      # cannot telescope without C_{H-1}
            if H - 2 in C:
                v += C[H - 2].get(n, 0)
            elif H - 2 >= 1:
                continue
            tri[(n, H)] = v
    return tri


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
def all_pairs(k, jmax, tri, hmax=None):
    """Every depth pair whose two cells are banked, as (j1, j2).

    hmax caps the HEIGHT of a usable pinning cell.  Without it a run that
    claims to use only heights <= H can still pin its tower from taller ones,
    which is exactly the sort of quiet circularity this file exists to avoid."""
    have = [j for j in range(1, jmax + 1)
            if k + 1 - j >= 1 and (2 * k + 1 - j, k + 1 - j) in tri
            and (hmax is None or k + 1 - j <= hmax)]
    return [(have[i], have[j]) for i in range(len(have)) for j in range(i + 1, len(have))]


def verify(jmax=3):
    P, tri = read_pk(), read_tri()
    kmax = max(P)
    ab = extract_ab(P, kmax)
    print(f"grand form consistent on wired levels k = 1..{kmax} "
          f"(every residual linear in n)")
    Dj = load_depths(jmax, kmax)
    print(f"ab-initio depth series loaded for j = 1..{jmax}, k <= {kmax}")

    ok = bad = skip = npairs = 0
    for k in sorted(ab):
        pairs = all_pairs(k, jmax, tri)
        if not pairs:
            skip += 1
            continue
        lower = {j: ab[j] for j in ab if j < k}
        want = ab[k]
        wrong = [d for d in pairs if pin_level(k, lower, d, tri, Dj) != want]
        npairs += len(pairs)
        tallest = k + 1 - min(min(d) for d in pairs)
        mark = "OK " if not wrong else "BAD"
        if wrong:
            bad += 1
        else:
            ok += 1
        print(f"  k={k:2d} {len(pairs)} depth pairs, tallest cell H={tallest:2d} "
              f"(onset anchors need H={k+2:2d})  {mark}")
        for d in wrong:
            got = pin_level(k, lower, d, tri, Dj)
            print(f"      pair {d}: got a={got[0]} b={got[1]}")
            print(f"                want a={want[0]} b={want[1]}")
    print(f"\nverify: {ok} levels re-derived exactly over {npairs} depth pairs, "
          f"{bad} wrong, {skip} skipped")
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
        pairs = all_pairs(k, jmax, tri)
        if not pairs:
            print(f"  k={k}: no banked below-onset pair at j <= {jmax} "
                  f"-- needs deeper depths")
            continue
        lower = {j: ab[j] for j in ab if j < k}
        sols = {d: pin_level(k, lower, d, tri, Dj) for d in pairs}
        vals = set(sols.values())
        if len(vals) != 1:
            print(f"  k={k:2d} INCONSISTENT across {len(pairs)} depth pairs:")
            for d, v in sols.items():
                print(f"      {d}: a={v[0]} b={v[1]}")
            raise SystemExit("PREDICT RED: depth pairs disagree")
        ab[k] = vals.pop()
        cells = ", ".join(f"T({2*k+1-j},{k+1-j})" for j in
                          sorted({x for d in pairs for x in d}))
        print(f"  k={k:2d} pinned, {len(pairs)} depth pairs AGREE "
              f"({len(pairs)-1} independent checks); cells {cells}")

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


def emit(jmax=4, kmax_new=21):
    """Print orchestrator/sweep.go diagCoeffTable entries for the pinned levels.

    Coefficients descending over kfact = k!, exactly as the wired table stores
    them; a level whose coefficients are not integral over k! is refused rather
    than rounded."""
    import math
    P, tri = read_pk(), read_tri()
    kw = max(P)
    ab = extract_ab(P, kw)
    Dj = load_depths(jmax, kmax_new)
    for k in range(kw + 1, kmax_new + 1):
        pairs = all_pairs(k, jmax, tri)
        if not pairs:
            print(f"// k={k}: no banked below-onset pair at j <= {jmax}")
            continue
        lower = {j: ab[j] for j in ab if j < k}
        sols = {d: pin_level(k, lower, d, tri, Dj) for d in pairs}
        if len(set(sols.values())) != 1:
            raise SystemExit(f"EMIT RED: depth pairs disagree at k={k}")
        ab[k] = next(iter(sols.values()))
        poly = grand_form(ab, k)[k]                    # ascending in n
        kfact = math.factorial(k)
        desc = []
        for c in reversed(poly):
            v = c * kfact
            if v.denominator != 1:
                raise SystemExit(f"EMIT RED: k={k} coefficient {c} not integral over {k}!")
            desc.append(str(v.numerator))
        while len(desc) < k + 1:                        # pad leading zeros
            desc.insert(0, "0")
        cells = ", ".join(f"T({2*k+1-j},{k+1-j})" for j in
                          sorted({x for d in pairs for x in d}))
        print(f"\t// k={k}: Undertow-pinned from below-onset cells {cells};")
        print(f"\t// {len(pairs)} depth pairs agree ({len(pairs)-1} independent checks).")
        print("\t%d: {[]string{%s}, %d}," %
              (k, ", ".join('"%s"' % c for c in desc), kfact))


def audit(jmax=3):
    """Pin every level from its SHORTEST available cells, then check the tower
    against every banked cell on that diagonal it did not use.

    This is the systematic version of the row-40 regression: the incumbent's
    tall cells, predicted from its short ones, through ab-initio depth
    identities.  A transcription or dispatch error anywhere in the tall band
    shows up here as a mismatch."""
    P, tri = read_pk(), read_tri()
    ab = extract_ab(P, max(P))
    Dj = load_depths(jmax, max(P))
    total_ok = total_bad = 0
    for k in sorted(ab):
        pairs = all_pairs(k, jmax, tri)
        if not pairs:
            continue
        deep = max(pairs, key=lambda d: (min(d), max(d)))   # the two shortest cells
        used = {(2 * k + 1 - j, k + 1 - j) for j in deep}
        lower = {j: ab[j] for j in ab if j < k}
        a, b = pin_level(k, lower, deep, tri, Dj)
        E = grand_form({**lower, k: (a, b)}, k)
        ok = bad = 0
        for n in range(2 * k + 1, 41):          # in-onset cells only
            H = n - k
            if (n, H) not in tri or (n, H) in used:
                continue
            v = peval(E[k], n) * pow3(n - 1 - 3 * k)
            if F(tri[(n, H)]) == v:
                ok += 1
            else:
                bad += 1
                print(f"  MISMATCH T({n},{H}) k={k}")
        if ok or bad:
            tall = max(H for _, H in used)
            print(f"  k={k:2d} pinned at H<={tall:2d} (depths {deep}); "
                  f"{ok} banked cells predicted, {bad} wrong")
        total_ok += ok
        total_bad += bad
    print(f"audit: {total_ok} banked cells predicted from shorter cells, "
          f"{total_bad} wrong")
    return total_bad == 0 and total_ok >= 50


def main():
    jmax = 3
    for a in sys.argv[1:]:
        if a.startswith("--jmax="):
            jmax = int(a.split("=")[1])
    if "--selftest" in sys.argv:
        selftest(jmax)
    elif "--audit" in sys.argv:
        if not audit(jmax):
            raise SystemExit("AUDIT RED")
        print("AUDIT GREEN")
    elif "--emit" in sys.argv:
        emit(jmax)
    elif "--predict" in sys.argv:
        predict(jmax)
    else:
        if not verify(jmax):
            raise SystemExit("VERIFY RED")
        print("VERIFY GREEN")


if __name__ == "__main__":
    main()
