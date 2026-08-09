#!/usr/bin/env python3
"""Asymptotics of the depth-1 defect from the gap-walk series (past k = 19).

Input: D_1(k) exact for k = 1..K from experiments/depth1_gap_walk.py's
identity D_1 = [y^k](Phat - B^2/(3+S)) — verified there against all 19 banked
cells, so everything here rests on the walk, not on P_k.

  1. theta and C_1 = sqrt6/(27 sqrt(pi)), re-extracted at K terms with
     Richardson whose digit budget is set by same-length NON-TERMINATING
     controls (exp(c/k) forms — a truncated 1/k polynomial is the vacuous
     control both reviews flagged; defect_controls.py is not imported, its
     (c3) labels being inverted per the handoff).
  2. the amplitude squared, theta-free: h_k = [y^k] F1^2 has
     h_k/9^k -> A^2 (A = sqrt6/27) iff F1 ~ A (1-9y)^(-1/2); fitted on a
     half-power ladder.
  3. the 1/k coefficient a (second_term's kill criterion fired at k <= 19;
     re-attempted here), rational scan + PSLQ at honest tolerance.
  4. P-finite and algebraic-GF searches mod 2^61-1, holdouts, live controls.

Run from repo root: python3 experiments/depth1_asymptotics.py [K]
"""
import os
import random
import sys
import time
from fractions import Fraction as F

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth1_gap_walk import walk_families, series_D1            # noqa: E402

mp.mp.dps = 120
PRIME = (1 << 61) - 1


def richardson(seq, order, k0):
    """seq[i] ~ L + c1/k + c2/k^2 + ... at k = k0 + i; iterated elimination."""
    t = list(seq)
    ks = list(range(k0, k0 + len(seq)))
    for m in range(1, order + 1):
        t = [(ks[i + m] * t[i + 1] - ks[i] * t[i]) / (ks[i + m] - ks[i])
             for i in range(len(t) - 1)]
    return t[-1]


def rich_ladder(seq, k0, max_order=8):
    return [richardson(seq, m, k0) for m in range(1, max_order + 1)]


def control_bar(K, max_order=8):
    """Digit budget: |error| of the same pipeline on non-terminating controls
    of the same length. exp(c1/k + c2/k^2) has an infinite 1/k ladder."""
    ks = range(1, K + 1)
    base = [mp.exp(mp.mpf(1) / (10 * k) - mp.mpf(1) / (30 * k ** 2))
            for k in ks]
    flavours = {
        'smooth':  base,
        'geom':    [base[k - 1] + mp.mpf('0.02') * mp.mpf('0.8') ** k
                    for k in ks],
        'halfpow': [base[k - 1] + mp.mpf('5e-4') * k ** mp.mpf('-1.5')
                    for k in ks],
        'logk':    [base[k - 1] + mp.mpf('5e-4') * mp.log(k) / k for k in ks],
    }
    worst = {}
    for name, s in flavours.items():
        errs = [abs(v - 1) for v in rich_ladder(s, 1, max_order)]
        worst[name] = min(errs)          # best order that flavour allows
    return worst


def halfpower_fit(vals, terms):
    """vals[k-1] ~ sum_t c_t k^(-t/2), t = 0..terms-1, on the last points."""
    K = len(vals)
    pts = list(range(K - terms + 1, K + 1))
    A = mp.matrix(terms, terms)
    b = mp.matrix(terms, 1)
    for r, k in enumerate(pts):
        for c in range(terms):
            A[r, c] = mp.mpf(k) ** (-mp.mpf(c) / 2)
        b[r] = vals[k - 1]
    x = mp.lu_solve(A, b)
    return x[0]


# ---------------------------------------------------- mod-p structure searches

def modp_nullspace(rows, p):
    if not rows:
        return []
    ncol = len(rows[0])
    M = [r[:] for r in rows]
    piv_of_col = {}
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] % p), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], p - 2, p)
        M[r] = [x * inv % p for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % p:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(ncol)]
        piv_of_col[c] = r
        r += 1
    basis = []
    for fc in (c for c in range(ncol) if c not in piv_of_col):
        v = [0] * ncol
        v[fc] = 1
        for c, pr in piv_of_col.items():
            v[c] = (-M[pr][fc]) % p
        basis.append(v)
    return basis


def pfinite_search(seq_modp, rmax, dmax, p, label, expect_found=None):
    """sum_i p_i(k) s(k+i) = 0, deg p_i <= d: nullspace mod p, holdout 6."""
    hits = []
    for r in range(1, rmax + 1):
        for d in range(0, dmax + 1):
            nunk = (r + 1) * (d + 1)
            fit = len(seq_modp) - r - 6
            if fit < nunk + 4:
                continue
            rows = []
            for k in range(1, fit + 1):
                row = []
                for i in range(r + 1):
                    kp = 1
                    for e in range(d + 1):
                        row.append(seq_modp[k - 1 + i] * kp % p)
                        kp = kp * k % p
                rows.append(row)
            ns = modp_nullspace(rows, p)
            ok = 0
            for v in ns:
                good = True
                for k in range(fit + 1, fit + 7):
                    tot, idx = 0, 0
                    for i in range(r + 1):
                        kp = 1
                        for e in range(d + 1):
                            tot = (tot + v[idx] * seq_modp[k - 1 + i] * kp) % p
                            kp = kp * k % p
                            idx += 1
                    if tot % p:
                        good = False
                        break
                ok += good
            if ok:
                hits.append((r, d, ok))
    if expect_found is True:
        assert hits, f"{label}: control NOT found"
        print(f"   control {label}: FOUND (r,d) = {hits[0][:2]}  (must fire)")
    elif expect_found is False:
        assert not hits, f"{label}: noise control found {hits}"
        print(f"   control {label}: none  (must not fire)")
    else:
        print(f"   {label}: " + (f"CANDIDATE recurrences {hits}" if hits else
              f"none up to (r,d) = ({rmax},{dmax}), holdout 6"))
    return hits


def algebraic_search(coeffs_modp, pmax_y, qmax, p, K, label,
                     expect_found=None):
    """sum_{i<=pmax_y, j<=qmax} c_ij y^i F(y)^j = 0 mod p, holdout 10.
    coeffs_modp[m] = [y^m]F mod p, m = 0..K."""
    powers = [[1] + [0] * K]
    cur = powers[0]
    for _ in range(qmax):
        nxt = [0] * (K + 1)
        for a2 in range(K + 1):
            if cur[a2]:
                for b2 in range(K + 1 - a2):
                    if coeffs_modp[b2]:
                        nxt[a2 + b2] = (nxt[a2 + b2]
                                        + cur[a2] * coeffs_modp[b2]) % p
        cur = nxt
        powers.append(cur)
    nunk = (pmax_y + 1) * (qmax + 1)
    usable = K - 10
    rows = []
    for m in range(usable + 1):
        row = []
        for j in range(qmax + 1):
            for i in range(pmax_y + 1):
                row.append(powers[j][m - i] if 0 <= m - i else 0)
        rows.append(row)
    ns = modp_nullspace(rows, p)
    ok = 0
    for v in ns:
        good = True
        for m in range(usable + 1, K + 1):
            tot, idx = 0, 0
            for j in range(qmax + 1):
                for i in range(pmax_y + 1):
                    if 0 <= m - i:
                        tot = (tot + v[idx] * powers[j][m - i]) % p
                    idx += 1
            if tot % p:
                good = False
                break
        if good and any(v[idx] for idx in range(pmax_y + 1, nunk)):
            ok += 1
    tag = (f"CANDIDATE algebraic relation ({ok} independent)" if ok else
           f"none with deg_y <= {pmax_y}, deg_F <= {qmax}, holdout 10")
    if expect_found is True:
        assert ok, f"{label}: control NOT found"
        print(f"   control {label}: found  (must fire)")
    else:
        print(f"   {label}: {tag}")
    return ok


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    fams = walk_families(K)
    D1 = series_D1(fams, K)
    print(f"series to k = {K} in {time.time() - t0:.1f}s")

    Dv = [mp.mpf(D1[k].numerator) / mp.mpf(D1[k].denominator)
          for k in range(1, K + 1)]
    l9 = mp.log(9)

    print()
    print("== controls: digit budget for Richardson at this length")
    bars = control_bar(K)
    for name, err in bars.items():
        print(f"   {name:9s} best |error| = {mp.nstr(err, 3)}")
    bar = max(bars['smooth'], bars['geom'])
    bar_contam = max(bars['halfpow'], bars['logk'])
    print(f"   budget, pure 1/k ladder: {mp.nstr(bar, 3)}; with 5e-4 "
          f"half-power/log contaminant: {mp.nstr(bar_contam, 3)}")

    print()
    print("== theta: k(D_k/(9 D_{k-1}) - 1) -> theta   [assumes only rate 9]")
    th = [mp.mpf(k) * (Dv[k - 1] / (9 * Dv[k - 2]) - 1)
          for k in range(2, K + 1)]
    lad = rich_ladder(th, 2)
    for m, v in enumerate(lad, 1):
        print(f"   order {m}: {mp.nstr(v, 12)}")
    print(f"   target -1/2; spread of orders 3..8 = "
          f"{mp.nstr(max(lad[2:]) - min(lad[2:]), 3)}")

    print()
    print("== C_1: c_k = D_1(k) 9^-k k^(1/2)   [conditional on theta = -1/2]")
    ck = [Dv[k - 1] * mp.exp(-k * l9) * mp.sqrt(k) for k in range(1, K + 1)]
    lad = rich_ladder(ck, 1)
    C1_target = mp.sqrt(6) / (27 * mp.sqrt(mp.pi))
    for m, v in enumerate(lad, 1):
        print(f"   order {m}: {mp.nstr(v, 20)}   (rel to target: "
              f"{mp.nstr(v / C1_target - 1, 3)})")
    C1_best = lad[5]
    spread = max(abs(lad[i] - lad[j]) for i in range(3, 8)
                 for j in range(3, 8)) / C1_target
    print(f"   order spread (rel), orders 4..8: {mp.nstr(spread, 3)}")
    print(f"   sqrt6/(27 sqrt pi) = {mp.nstr(C1_target, 20)}")
    print(f"   measured / target - 1 = {mp.nstr(C1_best / C1_target - 1, 5)}")

    print()
    print("== amplitude squared, theta-free: h_k/9^k for h = [y^k]F1^2")
    print("   F1 ~ A (1-9y)^(-1/2)  =>  h_k/9^k -> A^2 = 6/729 = 2/243")
    h = [F(0)] * (K + 1)
    d_full = [F(0)] + D1[1:]
    for a2 in range(K + 1):
        if d_full[a2]:
            for b2 in range(K + 1 - a2):
                if d_full[b2]:
                    h[a2 + b2] += d_full[a2] * d_full[b2]
    hv = [mp.mpf(h[k].numerator) / mp.mpf(h[k].denominator) * mp.exp(-k * l9)
          for k in range(1, K + 1)]
    for terms in (6, 8, 10, 12):
        est = halfpower_fit(hv, terms)
        print(f"   half-power ladder, {terms:2d} terms: A^2 = "
              f"{mp.nstr(est, 15)}  (rel to 2/243: "
              f"{mp.nstr(est * mp.mpf(243) / 2 - 1, 3)})")

    print()
    print("== the 1/k coefficient a: k B_k, B_k = c_k/C_1_exact - 1")
    kb = [mp.mpf(k) * (ck[k - 1] / C1_target - 1) for k in range(1, K + 1)]
    lad = rich_ladder(kb, 1)
    for m, v in enumerate(lad, 1):
        print(f"   order {m}: {mp.nstr(v, 15)}")
    a_est = lad[5]
    a_spread = max(abs(lad[i] - lad[j]) for i in range(3, 8)
                   for j in range(3, 8))
    print(f"   a = {mp.nstr(a_est, 12)}   order-spread {mp.nstr(a_spread, 3)}")
    print("   (k <= 19 run: 0.005139, indicative bar 3.3e-5, shipped 2e-2)")
    aq = float(a_est)
    inside = [(round(aq * q), q) for q in range(1, 4001)
              if round(aq * q) and abs(aq - round(aq * q) / q)
              < 10 * float(a_spread)]
    best = min(inside, key=lambda t: abs(aq - t[0] / t[1]), default=None)
    print(f"   rationals q <= 4000 within 10x spread: {len(inside)}"
          + (f"; nearest {best[0]}/{best[1]}" if best else ""))
    tol = max(float(a_spread) * 10, 1e-40)
    vec = [a_est, mp.mpf(1), mp.sqrt(3)]
    rel = mp.pslq(vec, tol=mp.mpf(tol), maxcoeff=10 ** 6, maxsteps=10 ** 5)
    print(f"   PSLQ [a, 1, sqrt3], tol 10x spread: "
          + (str(rel) if rel else "no relation, coeffs <= 1e6"))
    a_exact = mp.mpf(3293) / 92928 - 3251 * mp.sqrt(3) / 185856
    print(f"   exact value from the minimal polynomial "
          f"(depth1_minpoly.py): 3293/92928 - 3251 sqrt3/185856 = "
          f"{mp.nstr(a_exact, 15)}")
    print(f"   measured - exact = {mp.nstr(a_est - a_exact, 3)}  "
          f"(order-spread {mp.nstr(a_spread, 3)})")

    print()
    print("== structure searches mod 2^61-1 on N_k = 3^(k+1) D_1(k)")
    seqp = [(D1[k] * F(3) ** (k + 1)).numerator % PRIME
            for k in range(1, K + 1)]
    ctrl_binom, b = [], 1
    for k in range(1, K + 1):
        b = b * 2 * k * (2 * k - 1) // (k * k)
        ctrl_binom.append(b * pow(9, k, PRIME)
                          * pow(pow(4, k, PRIME), PRIME - 2, PRIME) % PRIME)
    random.seed(7)
    ctrl_noise = [random.randrange(PRIME) for _ in range(K)]
    t1 = time.time()
    pfinite_search(ctrl_binom, 2, 2, PRIME, "binom(2k,k)(9/4)^k",
                   expect_found=True)
    pfinite_search(ctrl_noise, 3, 3, PRIME, "hash noise", expect_found=False)
    pfinite_search(seqp, 6, 8, PRIME, "N_k P-finite")
    print(f"   [{time.time() - t1:.0f}s]")

    t1 = time.time()
    inv3 = pow(3, PRIME - 2, PRIME)
    coeffs_modp = [0] + [seqp[k - 1] * pow(inv3, k + 1, PRIME) % PRIME
                         for k in range(1, K + 1)]
    cat = [0, 1]                              # Catalan: G = sum C_n y^n, n>=1
    for n in range(2, K + 1):
        cat.append(cat[-1] * (4 * n - 2) // (n + 1))
    algebraic_search([c % PRIME for c in cat], 3, 3, PRIME, K,
                     "catalan GF (algebraic)", expect_found=True)
    algebraic_search(coeffs_modp, 12, 4, PRIME, K, "F1 algebraic")
    print(f"   [{time.time() - t1:.0f}s]")

    print(f"\ntotal {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
