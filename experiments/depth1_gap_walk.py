#!/usr/bin/env python3
"""The depth-1 defect is the top coefficient of R_k, closed by the all-pairs gap walk.

Structure (all from docs/proofs/diagonal-law.md, nothing new assumed):
  Step 4:  [y^k]F = R_k(z)/(1-3z)^(k+1),  R_k in Z[z],  deg R_k <= 2k+1.
  Step 5:  below onset, T(H+k,H) = q_k(H) 3^H + [z^H]D(z), deg D <= k, and the
           z^k coefficient of D — the depth-1 defect D_1(k) = T(2k,k) - law —
           is reached only by the top basis element, so

               D_1(k) = lead(R_k) / (-3)^(k+1).                        (I)

  The z-degree bounds of Step 4 are tight ONLY on clusters with every row of
  size 2 (each cluster row must carry exactly 1 surplus), so lead(R_k)
  assembles from the all-pairs weight families alone:

      S(y)    = sum_l W (2^l) y^l   (interior),
      B(y) = 1 + sum_l W^b(2^l) y^l (bottom edge; = top edge, palindromic type),
      Phat(y) = sum_l W^p(2^l) y^l  (pure),

  via  lead(R_k) = (-3)^k [y^k]{ 3 B^2/(3+S) } + (-3)^(k+1) [y^k]Phat, i.e.

               D_1(k) = [y^k]( Phat(y) - B(y)^2/(3+S(y)) ).           (II)

This script verifies (I) law-free (R_k fitted from the banked triangle alone,
overdetermined, k <= 13) and (II) against the exact banked defects k <= 19,
then uses the gap walk (boundary/pure variants of experiments/allpairs_kernel.py,
validated against the cluster_weight_dp enumerations) to extend D_1(k) to
k = KMAX exactly — past the P_k <= 19 wall, which (II) does not need.

Run from repo root: python3 experiments/depth1_gap_walk.py [KMAX]
"""
import math
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slope2_law_vs_truth import read_pk, read_tri, law          # noqa: E402
from cluster_weight_dp import KNOWN_WEIGHTS, count_stack        # noqa: E402

REF_INTERIOR = [25, 339, 4778, 68314, 981085, 14115141, 203235615, 2927318947]


# ---------------------------------------------------------------- gap walk

def transitions(g, c, gp_max):
    """Verbatim from experiments/allpairs_kernel.py (validated l <= 8)."""
    out = {}
    for gp in range(1, gp_max + 1):
        for a in range(-1 - gp - 1, g + 3):
            T = (a, a + gp)
            touch0 = any(abs(t) <= 1 for t in T)
            touchg = any(abs(t - g) <= 1 for t in T)
            if c == 'P':
                if not (touch0 and touchg):
                    continue
            else:
                if not (touch0 or touchg):
                    continue
            if gp == 1:
                nc = 'J'
            elif c == 'J':
                a0 = (abs(T[0]) <= 1 or abs(T[0] - g) <= 1)
                a1 = (abs(T[1]) <= 1 or abs(T[1] - g) <= 1)
                nc = 'J' if (a0 and a1) else 'P'
            else:
                par = {k: k for k in 'ABxy'}

                def find(k):
                    while par[k] != k:
                        k = par[k]
                    return k

                def uni(u, v):
                    ru, rv = find(u), find(v)
                    if ru != rv:
                        par[ru] = rv

                if abs(T[0]) <= 1:
                    uni('x', 'A')
                if abs(T[0] - g) <= 1:
                    uni('x', 'B')
                if abs(T[1]) <= 1:
                    uni('y', 'A')
                if abs(T[1] - g) <= 1:
                    uni('y', 'B')
                nc = 'J' if find('x') == find('y') else 'P'
            out[(gp, nc)] = out.get((gp, nc), 0) + 1
    return out


def q_end(dp):
    """Finish with the free single-cell contact row q above (interior/bottom)."""
    tot = 0
    for (g, c), v in dp.items():
        if c == 'J':
            tot += v * (g + 3 if g <= 2 else 6)
        elif g <= 2:
            tot += v * (3 - g)
    return tot


def bare_end(dp):
    """Finish with nothing above: the stack itself must be one component."""
    return sum(v for (g, c), v in dp.items() if c == 'J')


def walk_families(L):
    """(W(2^l), W^b(2^l), W^p(2^l)) for l = 1..L, exact, via the gap walk.

    Two DPs over the same transition table: 'interior' starts against the fixed
    contact cell p below (as in allpairs_kernel.W_via_walk), 'bare' starts with
    the first pair-row alone (one normalized placement per gap).  Ends: q_end
    adds the free contact row above (interior weight from the p-start, bottom
    edge weight from the bare start); bare_end closes with nothing above
    (pure weight from the bare start).  W^t(2^l) = W^b(2^l): the type is a
    palindrome and reversal is a bijection on configurations.
    """
    gmax = 2 * L + 3
    trans = {}
    for g in range(1, gmax + 1):
        for c in 'JP':
            trans[(g, c)] = transitions(g, c, gmax)

    dp_int = defaultdict(int)
    for g in range(1, gmax + 1):
        for a in range(-1 - g - 1, 3):
            T = (a, a + g)
            if not any(abs(t) <= 1 for t in T):
                continue
            nc = 'J' if (g == 1 or (abs(T[0]) <= 1 and abs(T[1]) <= 1)) else 'P'
            dp_int[(g, nc)] += 1
    dp_bare = defaultdict(int)
    for g in range(1, gmax + 1):
        dp_bare[(g, 'J' if g == 1 else 'P')] += 1

    out = []
    for _ in range(L):
        out.append((q_end(dp_int), q_end(dp_bare), bare_end(dp_bare)))
        ndp_int, ndp_bare = defaultdict(int), defaultdict(int)
        for dp, ndp in ((dp_int, ndp_int), (dp_bare, ndp_bare)):
            for (g, c), v in dp.items():
                for (gp, nc), t in trans[(g, c)].items():
                    ndp[(gp, nc)] += v * t
        dp_int, dp_bare = ndp_int, ndp_bare
    return out


# ------------------------------------------------------------- series algebra

def series_D1(fams, K):
    """[y^k](Phat - B^2/(3+S)) for k = 1..K as exact Fractions."""
    S = [F(0)] + [F(w) for w, _, _ in fams[:K]]
    B = [F(1)] + [F(wb) for _, wb, _ in fams[:K]]
    Ph = [F(0)] + [F(wp) for _, _, wp in fams[:K]]

    def smul(a, b):
        return [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(K + 1)]

    denom = [F(3) + S[0]] + S[1:]
    inv = [F(1) / denom[0]] + [F(0)] * K
    for m in range(1, K + 1):
        inv[m] = -sum(denom[i] * inv[m - i] for i in range(1, m + 1)) / denom[0]
    chain = smul(smul(B, B), inv)
    return [Ph[k] - chain[k] for k in range(K + 1)]


# ------------------------------------------------- law-free R_k from the triangle

def fit_Rk(k, tri, nmax=40):
    """Solve T(H+k,H) = [z^H] R_k/(1-3z)^(k+1) for R_k's 2k+2 integer
    coefficients from the banked column alone (H = 0..nmax-k, T(k,0) = 0).
    Returns (coeffs, slack) or None if underdetermined; asserts every
    surplus equation holds exactly."""
    nunk = 2 * k + 2
    Hs = list(range(0, nmax - k + 1))
    if len(Hs) < nunk:
        return None
    rows, rhs = [], []
    for H in Hs:
        row = [F(math.comb(H - i + k, k) * 3 ** (H - i)) if H >= i else F(0)
               for i in range(nunk)]
        rows.append(row)
        rhs.append(F(tri[(H + k, H)] if H > 0 else 0))
    M = [rows[i] + [rhs[i]] for i in range(len(rows))]
    ncol = nunk
    piv_rows = []
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            raise AssertionError(f"k={k}: rank-deficient at column {c}")
        M[r], M[piv] = M[piv], M[r]
        M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(ncol + 1)]
        piv_rows.append(r)
        r += 1
    for i in range(r, len(M)):
        assert M[i][ncol] == 0, f"k={k}: inconsistent overdetermined system"
    coeffs = [M[i][ncol] for i in range(nunk)]
    for x in coeffs:
        assert x.denominator == 1, f"k={k}: non-integer R_k coefficient {x}"
    return [int(x) for x in coeffs], len(M) - nunk


# ----------------------------------------------------------------------- main

def main():
    KMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    t0 = time.time()

    print(f"== gap walk: all-pairs families to l = {KMAX} "
          f"(gmax = {2 * KMAX + 3})")
    fams = walk_families(KMAX)
    print(f"   built in {time.time() - t0:.1f}s")

    got_int = [w for w, _, _ in fams[:8]]
    assert got_int == REF_INTERIOR, got_int
    print("   interior l <= 8 == allpairs_kernel REF  OK")
    for ell in range(1, 6):
        v = tuple([2] * ell)
        wi, wb, wt, wp = KNOWN_WEIGHTS[v]
        assert fams[ell - 1] == (wi, wb, wp), (ell, fams[ell - 1], (wi, wb, wp))
    print("   (W, W^b, W^p) l <= 5 == cluster_weight_dp KNOWN_WEIGHTS  OK")
    t1 = time.time()
    wb6 = count_stack([1, 2, 2, 2, 2, 2, 2])
    wp6 = count_stack([2, 2, 2, 2, 2, 2])
    assert (fams[5][1], fams[5][2]) == (wb6, wp6), (fams[5], wb6, wp6)
    print(f"   l = 6 boundary/pure fresh DP holdout ({wb6}, {wp6})  OK"
          f"  [{time.time() - t1:.1f}s]")

    D1 = series_D1(fams, KMAX)

    print()
    print("== banked substrate: D_1(k) = T(2k,k) - law, exact, k <= 19")
    P = read_pk()
    tri = read_tri()
    n_banked = 0
    for k in range(1, 20):
        if (2 * k, k) not in tri or k not in P:
            continue
        d_banked = F(tri[(2 * k, k)]) - law(2 * k, k, P)
        assert D1[k] == d_banked, (k, D1[k], d_banked)
        n_banked += 1
    print(f"   walk identity (II) == banked defect at ALL {n_banked} cells "
          f"k = 1..19  OK")

    print()
    print("== law-free check: R_k fitted from the triangle column alone")
    spine_lead = {0: 1, 1: 4, 2: -80, 3: 1753, 4: -40928, 5: 987355}
    for k in range(0, 14):
        fit = fit_Rk(k, tri)
        if fit is None:
            continue
        coeffs, slack = fit
        lead = coeffs[2 * k + 1]
        if k in spine_lead:
            assert lead == spine_lead[k], (k, lead)
        if k >= 1:
            want = D1[k] * F(-3) ** (k + 1)
            assert F(lead) == want, (k, lead, want)
        tag = " == spine_deeper" if k in spine_lead else ""
        print(f"   k={k:2d}: lead(R_k) = {lead:>24d}  slack={slack:2d}{tag}")
    print("   lead(R_k) = (-3)^(k+1) D_1(k) at every fitted level  OK")

    print()
    print("== the extended series (rate should approach 9, not rho = 14.41)")
    print("   %3s %-44s %12s %12s" % ("k", "D_1(k) = N_k / 3^(k+1)",
                                      "ratio", "ratio*sqrt(k/(k-1))"))
    prev = None
    for k in range(1, KMAX + 1):
        num = D1[k] * F(3) ** (k + 1)
        assert num.denominator == 1, (k, "denominator not 3^(k+1)")
        assert D1[k] > 0, (k, "defect not positive")
        r = float(D1[k] / prev) if prev else float('nan')
        radj = r * math.sqrt(k / (k - 1)) if k > 1 else float('nan')
        show = (k <= 6 or k % 5 == 0 or k >= KMAX - 2)
        if show:
            ns = str(num.numerator)
            if len(ns) > 40:
                ns = ns[:18] + "..." + ns[-18:]
            print("   %3d %-44s %12.6f %12.6f" % (k, ns, r, radj))
        prev = D1[k]
    print(f"   positivity and 3-power denominator hold k = 1..{KMAX}  OK")
    print(f"\ntotal {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
