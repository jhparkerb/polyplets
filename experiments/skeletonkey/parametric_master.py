#!/usr/bin/env python3
"""The master equation is lattice-parametric, and here is the substitution.

`docs/proofs/universal-diagonal-law.md` §"The gas, made lattice-parametric"
ends with what is still missing:

    What is still king-only: assembling c_k for k >= 2 *from* the cluster
    weights, i.e. defect_gas.py's ledger and the master equation.

`docs/lastditch-ideas.md (deleted)` §1b names that same gap as the blocker on running
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
import time
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


_WCACHE = {}


def weight(name, sizes):
    """cluster_weight, cached and timed.

    Cached because the RED control re-solves square and would otherwise pay
    for every weight twice; timed because at K = 4 a single weight is the
    unit of progress, and a run that prints nothing for an hour is
    indistinguishable from a hung one -- which is what the first K = 4
    attempt looked like when it died inside hex.
    """
    key = (name, sizes)
    if key not in _WCACHE:
        t0 = time.time()
        _WCACHE[key] = cluster_weight(LATTICES[name][0], sizes)
        print("#   W %-6s %-14s = %-12d %8.1f s"
              % (name, str(sizes), _WCACHE[key], time.time() - t0), flush=True)
    return _WCACHE[key]


def solve_H(name, K, perturb=None):
    _, b = LATTICES[name]   # D is re-looked-up inside weight()
    hat = []
    for sizes in clusters(K):
        l = len(sizes)
        k = sum(sizes) - l
        w = weight(name, sizes)
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


def wired_king_ck(K, perturb=None):
    """King cumulant slopes read off the WIRED P_k, for k = 1..K.

    The gas says c_k(n) = A_k n + B_k. Both sides of that are available for
    king without touching a cluster weight: the wired diagonal table gives
    P_k(n) as an exact polynomial, so evaluating F(n,u) = sum_k P_k(n) u^k at
    several n and taking log F gives c_k(n) at those n. Linearity is then a
    check with teeth -- the P_k have degree k, so c_k's n^2..n^k coefficients
    all have to cancel, k-1 conditions at order k -- and the surviving slope
    is what the cluster weights have to predict.

    Returns {k: (slope, constant)}; {} if the wired table is too short; None
    if some c_k came out non-linear, which is the failure the caller decides
    what to do about.

    `perturb` is (k, i): add 1 to the i-th descending coefficient of P_k, for
    RED controls. Evaluating and fitting beats carrying polynomials: slog()
    already does series log over any field, and Fractions make the fit exact.
    """
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    from slope2_law_vs_truth import read_pk  # noqa: E402
    wired = dict(read_pk())
    if max(wired) < K:
        return {}
    if perturb is not None:
        k, i = perturb
        co, den = wired[k]
        co = list(co)
        co[i] += 1
        wired[k] = (co, den)

    ns = list(range(10, 13 + K))            # >= 3 points, so linearity is real
    rows = []
    for n in ns:
        Fser = [F(1)]
        for k in range(1, K + 1):
            co, den = wired[k]
            v = 0
            for c in co:                    # descending, Horner
                v = v * n + c
            Fser.append(F(v, den))
        rows.append((n, slog(Fser, K)))

    out = {}
    for k in range(1, K + 1):
        pts = [(n, c[k]) for n, c in rows]
        (n0, y0), (n1, y1) = pts[0], pts[1]
        slope = (y1 - y0) / (n1 - n0)
        const = y0 - slope * n0
        for n, y in pts:
            if y != slope * n + const:
                return None
        out[k] = (slope, const)
    return out


def wired_selfcheck():
    """wired_king_ck against the moment-cumulant formulae, written out.

    wired_king_ck gets c_k by evaluating F(n,u) at several n and fitting. That
    is one code path for nineteen numbers, so it is checked here against the
    other way of doing it: carry the P_k as polynomials in n and expand
    log(1+x) explicitly, which is what the k=3 gate did before it was
    generalized. Agreement means the fit is not an artifact of the fit.
    """
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    from slope2_law_vs_truth import read_pk  # noqa: E402
    wired = read_pk()

    def poly(k):                            # ascending coefficients
        co, den = wired[k]
        return [F(c, den) for c in reversed(co)]

    def pmul(a, b):
        out = [F(0)] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[i + j] += x * y
        return out

    def padd(*ps):
        out = [F(0)] * max(len(p) for p in ps)
        for p in ps:
            for i, x in enumerate(p):
                out[i] += x
        return out

    def scale(p, c):
        return [x * c for x in p]

    P1, P2, P3, P4 = poly(1), poly(2), poly(3), poly(4)
    # log(1+x) = x - x^2/2 + x^3/3 - x^4/4 at x = sum_k P_k u^k.
    explicit = {
        2: padd(P2, scale(pmul(P1, P1), F(-1, 2))),
        3: padd(P3, scale(pmul(P1, P2), F(-1)),
                scale(pmul(pmul(P1, P1), P1), F(1, 3))),
        4: padd(P4, scale(pmul(P1, P3), F(-1)),
                scale(pmul(P2, P2), F(-1, 2)),
                pmul(pmul(P1, P1), P2),
                scale(pmul(pmul(P1, P1), pmul(P1, P1)), F(-1, 4))),
    }

    fitted = wired_king_ck(4)
    if fitted is None:
        sys.exit("SELFCHECK FAILED: wired king c_k came out non-linear")
    for k, p in sorted(explicit.items()):
        while len(p) > 1 and p[-1] == 0:
            p.pop()
        if len(p) > 2:
            sys.exit("SELFCHECK FAILED: explicit c_%d is not linear: %s"
                     % (k, p))
        slope, const = fitted[k]
        if (p[1], p[0]) != (slope, const):
            sys.exit("SELFCHECK FAILED: explicit c_%d = %s n + %s, fit says "
                     "%s n + %s" % (k, p[1], p[0], slope, const))
        print("# selfcheck ok k=%d: explicit expansion gives %s n + %s"
              % (k, p[1], p[0]))


def main():
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    K = int(pos[0]) if pos else 3

    if "--selfcheck" in sys.argv:
        wired_selfcheck()
        return

    if "--wired-only" in sys.argv:
        # The king half of gate K, with no cluster weights computed at all --
        # so the target for a long K=4 run can be read off before it lands,
        # and so the linearity cancellation can be run as an audit of the
        # wired table in its own right, to k = 19 rather than the k = 2 that
        # gas_cumulants.py can afford from the DP.
        ck = wired_king_ck(K)
        if ck is None:
            sys.exit("AUDIT FAILED: wired king c_k is not linear in n")
        if not ck:
            sys.exit("wired table stops below k = %d" % K)
        for k, (slope, const) in sorted(ck.items()):
            print("wired king c_%d = %s n + %s" % (k, slope, const))
        print("# %d cancellations: c_k's n^2..n^k coefficients all vanish"
              % sum(k - 1 for k in ck))

        # RED: the n^2 coefficient of P_K is inside what linearity sees.
        if K >= 2 and wired_king_ck(K, perturb=(K, K - 2)) is not None:
            sys.exit("RED FAILED: bumping P_%d's n^2 coefficient left every "
                     "c_k linear, so the audit has no teeth" % K)
        print("# RED ok: +1 on P_%d's n^2 coefficient breaks linearity" % K)

        # The blind spot, recorded rather than hidden. A perturbation of P_k's
        # CONSTANT term enters c_k as a constant and nothing else, so it can
        # never disturb linearity. Same for the n^1 term. The audit therefore
        # pins the n^2..n^k coefficients of each P_k and says nothing about
        # the other two.
        if wired_king_ck(K, perturb=(K, K)) is None:
            sys.exit("BLIND-SPOT CONTROL FAILED: bumping P_%d's constant term "
                     "broke linearity, so the scope claim below is wrong" % K)
        print("# scope: constant and n^1 coefficients are invisible to this "
              "audit (control: bumping P_%d's constant term changes nothing)"
              % K)
        return
    print("# parametric master equation: What_c = W_c * b^(2k-l-1), "
          "A_k = [u^k] log H, K = %d" % K, flush=True)

    print("# clusters at K=%d: %s"
          % (K, ", ".join(str(c) for c in clusters(K))), flush=True)

    for name in LATTICES:
        for sizes, want in BANKED_W[name].items():
            got = weight(name, sizes)
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

    # Gate K -- the banked table stops at k = 2 for king, so every king A_k
    # above that is checked against the WIRED P_k instead. See wired_king_ck.
    wired = wired_king_ck(K)
    if wired is None:
        sys.exit("GATE K FAILED: wired king c_k is not linear in n")
    if wired:
        A = slog(solve_H("king", K), K)
        for k in sorted(wired):
            slope, const = wired[k]
            if slope != A[k]:
                sys.exit("GATE K FAILED: wired king c_%d slope %s != A_%d %s"
                         % (k, slope, k, A[k]))
            print("# gate K ok king k=%d: wired P_1..P_%d give c_%d = %s n + "
                  "%s, slope matches A_%d from the weights"
                  % (k, k, k, slope, const, k), flush=True)

    # RED: bump one cluster weight by 1 and the slopes must move.
    Ab = slog(solve_H("square", K, perturb=(2, 2)), K)
    Ag = slog(solve_H("square", K), K)
    if Ab == Ag:
        sys.exit("RED FAILED: perturbing W(2,2) left the square slopes alone")
    print("# RED ok: W(2,2) 12 -> 13 moves square A_k to %s"
          % [str(x) for x in Ab[1:K + 1]], flush=True)


if __name__ == "__main__":
    main()
