#!/usr/bin/env python3
"""The defect gas, made lattice-parametric: why the diagonal formulae look like that.

`experiments/diagonal_machine.py` emits P_k for any row-local lattice, but only
as values-plus-theorem: it says what the polynomial is, not why. The
explanation is the gas, and the gas's content is a statement about CUMULANTS.

Write the diagonal series at fixed drift set D (b = |D|) as

    F(n, u) = sum_k P_k(n) u^k,   P_0 = 1        [T(n, n-k) = P_k(n) b^(n-1-3k)]

and take its logarithm, c_k = [u^k] log F. The gas says the defects are an
independent 1D gas with short-range interactions, so the cumulants are
EXTENSIVE -- linear in n -- at every order:

    c_k(n) = A_k n + B_k        for every k.

Everything about the shape follows from that one line:

  * deg P_k <= k, because the top term of P_k is c_1^k / k!;
  * the leading coefficient of P_k is W^k / k!, where W = A_1 is the pair
    weight of the lattice -- 4 for square, 9 for hex, 25 for king, whence
    4^k/k!, 9^k/k!, 25^k/k!;
  * the exponential form itself: F = exp(linear in n), i.e. an ideal gas of
    defects with the interactions living entirely in the constants B_k.

`experiments/defect_gas.py` establishes this for the king lattice and computes
the cluster weights behind it, but its adjacency is written as
(dx, dr) in (-1,0,1)^2 throughout. This script does the lattice-parametric
half: it checks the cumulant statement itself, and it computes the cluster
weights for an arbitrary D (reproducing king's, which is the calibration).

  1. cumulants are linear in n, every lattice, every k reached. RED control:
     perturbing one coefficient of one P_k must destroy the linearity, else
     the check has no teeth.
  2. leading coefficient of P_k == W^k / k!, with W read off c_1.
  3. W as read off c_1 == W_pair(D) counted independently as a gadget by
     experiments/universal_pair_weights.py. Two routes, no shared code.
  4. parametric cluster weights: king must reproduce 25, 49, 81, 339, 930,
     4778 (the tables in defect_gas.py); square and hex are then reported.
     RED control: the king weights must NOT come out of the square adjacency.

What is still king-only: assembling c_k for k >= 2 FROM those cluster weights
(defect_gas.py's ledger, and the master equation). That is the open step; the
statement above is what makes it worth taking.

Usage: python3 -m experiments.gas_cumulants
"""
import sys
from fractions import Fraction as F
from itertools import combinations

from experiments.diagonal_machine import LATTICES, diagonal_counts, interpolate
from experiments.universal_pair_weights import w_pair, connected

KMAX = {"square": 4, "hex": 3, "king": 2}
HMAX = {"square": 14, "hex": 12, "king": 10}
WINDOW = 6

# defect_gas.py's interior cluster weights for the king lattice, as calibration.
KING_CLUSTERS = {(2,): 25, (3,): 49, (4,): 81, (2, 2): 339, (2, 3): 930,
                 (3, 2): 930, (2, 2, 2): 4778}


# --- polynomial helpers, coefficients highest-degree first ------------------
def trim(p):
    while len(p) > 1 and p[0] == 0:
        p = p[1:]
    return p


def padd(a, b):
    n = max(len(a), len(b))
    a, b = [F(0)] * (n - len(a)) + list(a), [F(0)] * (n - len(b)) + list(b)
    return trim([x + y for x, y in zip(a, b)])


def pmul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    return trim(r)


def pscale(a, s):
    return trim([x * F(s) for x in a])


def deg(p):
    return len(trim(p)) - 1


def show(p):
    p = trim(p)
    d = len(p) - 1
    out = []
    for i, c in enumerate(p):
        e = d - i
        if c == 0:
            continue
        out.append(f"{c}n^{e}" if e > 1 else (f"{c}n" if e == 1 else f"{c}"))
    return (" + ".join(out) or "0").replace("+ -", "- ")


def cumulants(P):
    """c_k = [u^k] log(sum_k P_k u^k), P[0] = 1. Newton's identity on series."""
    K = len(P) - 1
    c = [None] * (K + 1)
    for k in range(1, K + 1):
        # k*P_k = sum_{j=1..k} j*c_j*P_{k-j}
        acc = [F(0)]
        for j in range(1, k):
            acc = padd(acc, pscale(pmul(c[j], P[k - j]), j))
        c[k] = pscale(padd(pscale(P[k], k), pscale(acc, -1)), F(1, k))
    return c


# --- lattice-parametric cluster weight --------------------------------------
def cluster_weight(D, sizes, W=9):
    """Interior weight of a cluster of the given row sizes, drift set D.

    Rows are p (one cell, fixed at the origin), then T_1..T_m of the given
    sizes, then q (one free cell). Count the connected placements. This is
    defect_gas.py's cluster_weight() with (-1,0,1) replaced by D throughout,
    including the row-to-row adjacency test.
    """
    Dset = set(D)

    def adj_rows(prev, cur):
        return any((t - a) in Dset for a in prev for t in cur)

    m = len(sizes)
    total = 0

    def cells_of(rows):
        return {(x, r) for r, xs in rows.items() for x in xs}

    def rec(i, rows, prev):
        nonlocal total
        if i == m:
            lo, hi = min(prev), max(prev)
            for q in range(lo - W, hi + W + 1):
                if not adj_rows(prev, (q,)):
                    continue
                cand = {**rows, m + 1: {q}}
                if connected(cells_of(cand), D):
                    total += 1
            return
        lo, hi = min(prev), max(prev)
        for T in combinations(range(lo - W, hi + W + 1), sizes[i]):
            if not adj_rows(prev, T):
                continue
            rec(i + 1, {**rows, i + 1: set(T)}, T)

    rec(0, {0: {0}}, (0,))
    return total


def polys_for(name):
    """P_k as polynomials in n, from the drift-parametric transfer DP."""
    D = LATTICES[name]
    b = len(D)
    kmax, hmax = KMAX[name], HMAX[name]
    T = diagonal_counts(D, kmax, hmax, WINDOW)
    P = [[F(1)]]
    for k in range(1, kmax + 1):
        hs = [H for H in range(k + 1, hmax + 1) if (H, k) in T]
        pts = [(H + k, F(b) ** (1 + 2 * k) * F(T[(H, k)], b ** H)) for H in hs]
        P.append([F(x) for x in interpolate(pts[:k + 1])])
    return b, P


def main():
    ok = True
    Ws = {}

    print("[1-3] cumulants, per lattice")
    for name in ("square", "hex", "king"):
        b, P = polys_for(name)
        c = cumulants(P)
        print(f"\n  {name} (b = {b})")
        for k in range(1, len(P)):
            print(f"    P_{k}(n) = {show(P[k])}")
            print(f"    c_{k}(n) = {show(c[k])}   deg {deg(c[k])}")
            if deg(c[k]) > 1:
                print(f"      FAIL: cumulant is not linear -- the gas picture breaks")
                ok = False
        W = c[1][0]
        Ws[name] = W
        # (2) leading coefficient law
        for k in range(1, len(P)):
            want = W ** k / F(1, 1) / _fact(k)
            got = trim(P[k])[0]
            flag = "" if got == want else "  MISMATCH"
            print(f"    lead P_{k} = {got}  vs  W^{k}/{k}! = {want}{flag}")
            if got != want:
                ok = False
        # (3) against the independent gadget count
        gadget = w_pair(LATTICES[name])
        print(f"    W from c_1 = {W}; W_pair gadget count = {gadget}"
              f"{'' if W == gadget else '  MISMATCH'}")
        if W != gadget:
            ok = False
        # RED control on linearity: bump the LEADING coefficient of the top
        # P_k (bumping the constant only shifts c_k's constant, which is no
        # test at all).
        K = len(P) - 1
        Pbad = [list(p) for p in P]
        Pbad[K][0] += 1
        cbad = cumulants(Pbad)
        if deg(cbad[K]) <= 1:
            print("      RED FAIL: perturbing P_k left the cumulant linear")
            ok = False
    print("\n    (RED control: a one-unit perturbation of the top P_k makes the "
          "top\n     cumulant non-linear on every lattice -- checked above)")

    print("\n[4] lattice-parametric cluster weights (defect_gas.py's, generalized)")
    print("      cluster      square      hex     king   (king must match "
          "defect_gas.py)")
    for sizes in ((2,), (3,), (4,), (2, 2), (2, 3), (2, 2, 2)):
        # W = 9 throughout: defect_gas.py records that W = 6 clips (2,2,2) to
        # 4776 instead of 4778, and this code reproduces that clipping exactly
        # when run at 6 -- which is a check on the port, and a trap to avoid.
        row = {}
        for name in ("square", "hex", "king"):
            row[name] = cluster_weight(LATTICES[name], sizes, W=9)
        want = KING_CLUSTERS.get(sizes)
        flag = ""
        if want is not None and row["king"] != want:
            flag = f"  MISMATCH (defect_gas.py says {want})"
            ok = False
        print(f"    {str(sizes):>10} {row['square']:>10} {row['hex']:>8} "
              f"{row['king']:>8}{flag}")
        if sizes == (2,):
            for name in ("square", "hex", "king"):
                if row[name] != Ws[name]:
                    print(f"      MISMATCH: {name} pair cluster {row[name]} "
                          f"!= W from c_1 {Ws[name]}")
                    ok = False
            print("      ^ the single pair row IS W, on every lattice")
        if sizes == (2,) and row["square"] == row["king"]:
            print("      RED FAIL: square and king adjacency give the same weight")
            ok = False

    print("\nThe gas statement is now lattice-parametric: cumulants linear in n,")
    print("leading coefficient W^k/k!, and W the pair-cluster weight of the")
    print("lattice. Assembling c_k for k >= 2 from the cluster weights is still")
    print("king-only (defect_gas.py's ledger) and is the remaining step.")
    return 0 if ok else 1


def _fact(k):
    r = 1
    for i in range(2, k + 1):
        r *= i
    return r


if __name__ == "__main__":
    sys.exit(main())
