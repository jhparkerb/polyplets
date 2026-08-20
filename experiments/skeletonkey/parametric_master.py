#!/usr/bin/env python3
"""The master equation is lattice-parametric, and here is the substitution.

`docs/proofs/universal-diagonal-law.md` §"The gas, made lattice-parametric"
ends with what is still missing:

    What is still king-only: assembling c_k for k >= 2 *from* the cluster
    weights, i.e. defect_gas.py's ledger and the master equation.

`docs/lastditch-ideas.md` §1b names that same gap as the blocker on running
the Undertow pin against an external oracle (square-lattice polyominoes,
published to n = 56).

It is one substitution. defect_gas.py's chain is `1 = 3z + sum_c W_c y^k
z^{l+1}` at `z = 1/mu`, i.e. `mu = 3 + sum W_c y^k mu^{-l}`, where the 3 is
the drift-step weight -- the number of continuations of a one-cell row, which
is `b = |D|` for a row-local lattice with drift set D. Writing `mu = b*H` and
`u = y*mu/b^3`:

    H(u) = 1 + sum_c  What_c u^{k_c} H^{-(k_c + l_c)},
    What_c = W_c * b^{2 k_c - l_c - 1}

which is the king form with 3 -> b throughout, and the cumulant slopes are

    A_k = [u^k] log H       (c_k(n) = A_k n + B_k)

because the grand form gives `F(n,u) = C(u) * H(u)^n`, so `log F` is linear in
n with slope `log H`.

This probe runs that on three lattices and checks A_k against the values
`universal-diagonal-law.md` obtained by a different route (a drift-parametric
DP over the triangle, not the weights). Agreement is the claim; the two routes
share no code.

Usage: python3 experiments/skeletonkey/parametric_master.py [KMAX]
"""

import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from experiments.gas_cumulants import cluster_weight  # noqa: E402
from experiments.diagonal_machine import LATTICES as DRIFT  # noqa: E402

# b is the drift-step weight -- the number of continuations of a one-cell row
# -- which is |D|, exactly as diagonal_machine.py computes it.
LATTICES = {name: (D, len(D)) for name, D in DRIFT.items()}

# universal-diagonal-law.md, "The gas, made lattice-parametric" table. These
# came from a drift-parametric DP over the triangle; this probe reaches them
# from the cluster weights instead.
BANKED_A = {
    "square": [F(4), F(-19), F(472, 3), F(-3099, 2)],
    "hex":    [F(9), F(-37, 2), F(32)],
    "king":   [F(25), F(-209, 2)],
}

# Same file's cluster-weight table, as a gate on the parametric enumeration.
BANKED_W = {
    "square": {(2,): 4, (3,): 9, (4,): 16, (2, 2): 12, (2, 3): 30,
               (2, 2, 2): 36},
    "hex":    {(2,): 9, (3,): 16, (4,): 25, (2, 2): 60, (2, 3): 138,
               (2, 2, 2): 409},
    "king":   {(2,): 25, (3,): 49, (4,): 81, (2, 2): 339, (2, 3): 930,
               (2, 2, 2): 4778},
}


# ------------------------------------------------------------ series in u
def smul(a, b, K):
    return [sum(a[i] * b[m - i] for i in range(m + 1)) for m in range(K + 1)]


def sinv(a, K):
    r = [F(1) / a[0]] + [F(0)] * K
    for m in range(1, K + 1):
        r[m] = -sum(a[i] * r[m - i] for i in range(1, m + 1)) / a[0]
    return r


def spow(a, p, K):
    base = a if p >= 0 else sinv(a, K)
    r = [F(1)] + [F(0)] * K
    for _ in range(abs(p)):
        r = smul(r, base, K)
    return r


def slog(a, K):
    """log of a series with a[0] = 1, by integrating a'/a."""
    assert a[0] == 1
    inv = sinv(a, K)
    d = [a[m + 1] * (m + 1) for m in range(K)] + [F(0)]
    q = smul(d, inv, K)
    return [F(0)] + [q[m - 1] / m for m in range(1, K + 1)]


def clusters(K):
    """Row-size tuples with every s_i >= 2 and surplus sum(s)-l <= K."""
    out = []

    def rec(pref, surplus):
        if pref:
            out.append(tuple(pref))
        for s in range(2, K - surplus + 2):
            if surplus + s - 1 > K:
                break
            rec(pref + [s], surplus + s - 1)

    rec([], 0)
    return out


def solve_H(name, K, perturb=None):
    D, b = LATTICES[name]
    hat = []
    for sizes in clusters(K):
        l = len(sizes)
        k = sum(sizes) - l
        w = cluster_weight(D, sizes)
        if perturb is not None and sizes == perturb:
            w += 1
        hat.append((F(w) * F(b) ** (2 * k - l - 1), k, l))
    H = [F(1)] + [F(0)] * K
    for _ in range(2 * K + 6):          # fixed point; converges by u-order
        rhs = [F(1)] + [F(0)] * K
        for What, k, l in hat:
            Hp = spow(H, -(k + l), K)
            for m in range(K + 1 - k):
                rhs[m + k] += What * Hp[m]
        if rhs == H:
            break
        H = rhs
    else:
        sys.exit("FAILED: master-equation iteration did not settle for " + name)
    return H


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print("# parametric master equation: What_c = W_c * b^(2k-l-1), "
          "A_k = [u^k] log H, K = %d" % K, flush=True)

    for name, (D, b) in LATTICES.items():
        for sizes, want in BANKED_W[name].items():
            got = cluster_weight(D, sizes)
            if got != want:
                sys.exit("GATE W FAILED %s %s: %d != banked %d"
                         % (name, sizes, got, want))
        print("# gate W ok %-6s: cluster weights match the banked table" % name,
              flush=True)

    ok = 0
    for name in LATTICES:
        A = slog(solve_H(name, K), K)
        want = BANKED_A[name]
        for k in range(1, min(K, len(want)) + 1):
            if A[k] != want[k - 1]:
                sys.exit("GATE A FAILED %s k=%d: %s != banked %s"
                         % (name, k, A[k], want[k - 1]))
            ok += 1
        print("%-6s b=%d  A_k = %s   (banked: %s)"
              % (name, LATTICES[name][1],
                 [str(x) for x in A[1:K + 1]],
                 [str(x) for x in want[:K]]), flush=True)
    print("# %d cumulant slopes reproduced from the cluster weights alone"
          % ok, flush=True)

    # Gate K -- king A_3 is not in the banked table (universal-diagonal-law.md
    # stops at k = 2 for king), so check it against the WIRED P_k instead:
    # c_3 = P_3 - P_1 P_2 + P_1^3/3, whose n^3 and n^2 parts must vanish
    # (linearity) and whose slope must equal A_3.
    if K >= 3:
        sys.path.insert(0, os.path.join(ROOT, "experiments"))
        from slope2_law_vs_truth import read_pk  # noqa: E402
        wired = read_pk()

        def poly(k):                       # descending coeffs / denominator
            co, den = wired[k]
            return [F(c, den) for c in reversed(co)]

        def mul(a, b):
            out = [F(0)] * (len(a) + len(b) - 1)
            for i, x in enumerate(a):
                for j, y in enumerate(b):
                    out[i + j] += x * y
            return out

        P1, P2, P3 = poly(1), poly(2), poly(3)
        c3 = [a - b + c for a, b, c in zip(
            P3 + [F(0)] * 4, mul(P1, P2) + [F(0)] * 4,
            [x / 3 for x in mul(mul(P1, P1), P1)] + [F(0)] * 4)]
        while len(c3) > 1 and c3[-1] == 0:
            c3.pop()
        A3 = slog(solve_H("king", K), K)[3]
        if len(c3) > 2:
            sys.exit("GATE K FAILED: king c_3 is not linear in n: %s" % c3)
        if c3[1] != A3:
            sys.exit("GATE K FAILED: wired king c_3 slope %s != A_3 %s"
                     % (c3[1], A3))
        print("# gate K ok king: wired P_1..P_3 give c_3 = %s n + %s, slope "
              "matches A_3 from the weights" % (c3[1], c3[0]), flush=True)

    # RED: bump one cluster weight by 1 and the slopes must move.
    Ab = slog(solve_H("square", K, perturb=(2, 2)), K)
    Ag = slog(solve_H("square", K), K)
    if Ab == Ag:
        sys.exit("RED FAILED: perturbing W(2,2) left the square slopes alone")
    print("# RED ok: W(2,2) 12 -> 13 moves square A_k to %s"
          % [str(x) for x in Ab[1:K + 1]], flush=True)


if __name__ == "__main__":
    main()
