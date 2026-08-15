#!/usr/bin/env python3
"""Ridgeline 1: the depth tower in closed form -- G(Y,t) = t*(Phat + Bhat^2/(t-3-Shat)).

Derivation (no fitting, no series input).  The proved chain identity
(docs/proofs/diagonal-law.md Step 2, quoted in experiments/severance_w3_depths.py)
is

    F(y,z) = E_b (1-S)^-1 E_t + P,     S = 3z + sigma,
    E_b = z(1 + sum_c W^b_c y^k_c z^l_c),   E_t = 1 + sum_c W^t_c y^k_c z^l_c,
    sigma = sum_c W_c y^k_c z^(l_c+1),      P = sum_c W^p_c y^k_c z^l_c,

with c ranging over cluster types (s_1..s_l), s_i >= 2, surplus k_c = sum(s_i-1),
l_c rows, excess e_c = k_c - l_c = sum(s_i-2) >= 0.

Change variables to

    Y = y z,      t = 1/z        (so y = Y t, z = 1/t).

Every monomial y^k z^l = Y^k z^(l-k) = Y^k t^e depends on the type only through
(k, e).  Hence, with the excess-graded aggregates of severance_w3_depths.families,

    Shat(Y,t) = sum_e t^e Sig_e(Y),   Bhat(Y,t) = sum_e t^e Bb_e(Y)  (Bb_0 has +1),
    Phat(Y,t) = sum_e t^e Pp_e(Y),

we get sigma = z Shat, E_b = z Bhat, E_t = Bhat (aggregate palindromy: reversal of
a type is a bijection preserving (k,e) and swapping W^b with W^t), P = Phat, and

    F = z Bhat^2 / (1 - 3z - z Shat) + Phat = Phat + Bhat^2 / (t - 3 - Shat).   (M)

The grading is legitimate as formal series: a type of excess e has l >= 1 rows and
k = l + e, so t^e comes with at least Y^(e+1); F is a power series in Y whose
t-coefficients are well defined.

Extraction.  Step 4/5 give [y^k]F = R_k(z)/(1-3z)^(k+1), R_k = sum_i a_i w^i with
w = 1-3z, and D_j(k) = [z^(k+1-j)] sum_{m>=0} a_(k+1+m) w^m.  Substituting
y = Yt, w = (t-3)/t,

    F = sum_k Y^k sum_s a_(2k+1-s) t^s (t-3)^(k-s),

so [Y^k t^(j-1)] F = (-3)^(k+1-j) sum_(s<j) C(k-s, j-1-s) a_(2k+1-s), which is
identity (D) of severance_w3_depths verbatim.  Therefore

    D_j(k) = [Y^k t^(j-1)] ( Phat + Bhat^2/(t-3-Shat) )   for  j-1 <= k.   (M')

(The law part of R_k, i = 0..k, contributes only to t-powers >= k+1, so it cannot
contaminate t^(j-1) while j-1 <= k.)

(M) is a *single closed form* for the whole depth tower.  It replaces the
binomial double sum (C)/(D) and makes the depth variable t what it structurally
is: a marker for cluster excess, i.e. a perturbation of the row-transfer of the
all-pairs gap walk.  At t = 0 it is identity (II) of
results/onset-defect-depth1-closed.md: Phat_0 - Bb_0^2/(3 + Sig_0).

This script verifies (M') against severance_w3_depths.D_series (which computes the
same defects through the independent route (C)/(D)) and, at j = 1, against
depth1_gap_walk's (II).  RED control included.

Run from repo root:  python3 experiments/ridgeline_master.py [K] [JMAX]
"""
import os
import re
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from severance_w3_depths import families, D_series, TABLE_DIR      # noqa: E402


def load_families(K, emax):
    """families(K, emax), preferring a cached table of any K_table >= K.

    severance_w3_depths._load_table only scans K_table < 40, so the K = 60
    excess-1 pass it cannot see; this reader accepts any K_table.  The cap in the
    file is the exact bound 2l+e+1 for the l <= K_table rows that contribute, so
    truncating a larger table to K is identity on cells k <= K -- which is what
    the caller then checks against D_series.
    """
    best = None
    for name in sorted(os.listdir(TABLE_DIR)):
        m = re.match(r"severance_w3_families_K(\d+)_e(\d+)\.txt$", name)
        if not m or int(m.group(2)) != emax or int(m.group(1)) < K:
            continue
        if best is None or int(m.group(1)) < best[0]:
            best = (int(m.group(1)), name)
    if best is None:
        return families(K, emax)
    sig = [[0] * (K + 1) for _ in range(emax + 1)]
    bb = [[0] * (K + 1) for _ in range(emax + 1)]
    pp = [[0] * (K + 1) for _ in range(emax + 1)]
    with open(os.path.join(TABLE_DIR, best[1])) as fh:
        head = fh.readline().split()
        assert head[:4] == ["#", "severance_w3_families",
                            "K=%d" % best[0], "emax=%d" % emax], head
        for line in fh:
            if line.startswith("#"):
                continue
            e, k, a, b, c = (int(x) for x in line.split())
            if k <= K and e <= emax:
                sig[e][k], bb[e][k], pp[e][k] = a, b, c
    return sig, bb, pp


# ------------------------------------------------- bigraded series arithmetic
# A series is a list of (K+1)-lists of Fractions, indexed [e][k], 0 <= e <= emax.

def zero(K, emax):
    return [[F(0)] * (K + 1) for _ in range(emax + 1)]


def from_int_table(tab, K, emax):
    return [[F(tab[e][k]) for k in range(K + 1)] for e in range(emax + 1)]


def bimul(a, b, K, emax):
    out = zero(K, emax)
    for e1 in range(emax + 1):
        for e2 in range(emax + 1 - e1):
            r1, r2, row = a[e1], b[e2], out[e1 + e2]
            for k1 in range(K + 1):
                c1 = r1[k1]
                if not c1:
                    continue
                for k2 in range(K + 1 - k1):
                    c2 = r2[k2]
                    if c2:
                        row[k1 + k2] += c1 * c2
    return out


def bidiv(num, den, K, emax):
    """out with num = den * out; requires den[0][0] != 0."""
    assert den[0][0] != 0, "unit constant term required"
    out = zero(K, emax)
    for w in range(K + emax + 1):                      # ascending total weight
        for e in range(min(w, emax) + 1):
            k = w - e
            if k > K:
                continue
            acc = num[e][k]
            for e2 in range(e + 1):
                for k2 in range(k + 1):
                    if e2 == 0 and k2 == 0:
                        continue
                    d = den[e2][k2]
                    if d:
                        acc -= d * out[e - e2][k - k2]
            out[e][k] = acc / den[0][0]
    return out


def master_G(K, emax, tweak=None):
    """[e][k] table of Phat + Bhat^2/(t-3-Shat); entry [j-1][k] should be D_j(k).

    `tweak` = (which, e, k, delta) perturbs one family coefficient (RED control).
    """
    sig, bb, pp = load_families(K, emax)
    S = from_int_table(sig, K, emax)
    B = from_int_table(bb, K, emax)
    P = from_int_table(pp, K, emax)
    B[0][0] += 1                                       # the empty bottom edge
    if tweak is not None:
        which, e, k, delta = tweak
        {'sig': S, 'bb': B, 'pp': P}[which][e][k] += F(delta)
    den = zero(K, emax)
    for e in range(emax + 1):
        for k in range(K + 1):
            den[e][k] = -S[e][k]
    den[0][0] -= 3
    if emax >= 1:
        den[1][0] += 1                                 # the explicit +t
    G = bimul(B, B, K, emax)
    G = bidiv(G, den, K, emax)
    for e in range(emax + 1):
        for k in range(K + 1):
            G[e][k] += P[e][k]
    return G


# ------------------------------------------------------------------- checking

def compare(G, K, jmax, label, expect_equal=True, verbose=True):
    ok = True
    for j in range(1, jmax + 1):
        ref = D_series(j, K)
        for k in range(j - 1, K + 1):
            got = G[j - 1][k]
            if got != ref[k]:
                ok = False
                if verbose:
                    print(f"   MISMATCH j={j} k={k}: master={got} (C)/(D)={ref[k]}")
                break
        else:
            if verbose:
                print(f"   j={j}: agrees at all {K + 2 - j} cells k = {j-1}..{K}")
            continue
        break
    verdict = "OK" if ok == expect_equal else "FAIL"
    print(f"   {label}: {'agrees' if ok else 'differs'}  [{verdict}]")
    return ok == expect_equal


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    JMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    emax = JMAX - 1
    t0 = time.time()

    print(f"== master identity (M'): D_j(k) = [Y^k t^(j-1)] (Phat + Bhat^2/(t-3-Shat))")
    print(f"   K = {K}, depths j = 1..{JMAX} (excess families e <= {emax})")
    G = master_G(K, emax)
    print(f"   assembled in {time.time() - t0:.1f}s")
    green = compare(G, K, JMAX, "master vs (C)/(D)")

    print()
    print("== j = 1 slice vs identity (II) of onset-defect-depth1-closed.md")
    from depth1_gap_walk import walk_families, series_D1            # noqa: E402
    D1ref = series_D1(walk_families(K), K)
    same = all(G[0][k] == D1ref[k] for k in range(1, K + 1))
    print(f"   [t^0](M) == Phat_0 - B_0^2/(3+S_0) at k = 1..{K}: "
          f"{'OK' if same else 'FAIL'}")
    green = green and same

    print()
    print("== the depth tower, exact (first cells of each depth)")
    for j in range(1, JMAX + 1):
        vals = [str(G[j - 1][k]) for k in range(j - 1, j + 2)]
        print(f"   D_{j}(k), k = {j-1}..{j+1}:  {', '.join(vals)}")

    print()
    print("== RED control: perturb one excess-1 pure weight by +1")
    if emax >= 1:
        Gred = master_G(K, emax, tweak=('pp', 1, 3, 1))
        fired = compare(Gred, K, JMAX, "perturbed master vs (C)/(D)",
                        expect_equal=False, verbose=False)
        print(f"   control fires: {'OK' if fired else 'FAIL -- control is vacuous'}")
        green = green and fired
    else:
        print("   skipped (needs JMAX >= 2)")
        green = False

    print()
    print(f"VERDICT: {'GREEN' if green else 'RED'}   [{time.time() - t0:.1f}s]")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
