#!/usr/bin/env python3
"""Severance W1 assembly: P_k ab initio from cluster weights alone.

Reads the exact aggregated cluster weights produced by build/severance_w1
(results/severance_w1_weights_k9.txt), assembles [y^k]F(z) via the chain
identity of docs/proofs/diagonal-law.md Step 2,

    F = E_b * (1 - S)^(-1) * E_t + P,

extracts R_k(z) with [y^k]F = R_k(z)/(1-3z)^(k+1) (Step 4), and turns R_k into
the diagonal polynomial P_k by the partial-fraction change of basis (Step 5).
Every derived P_k is then checked against the wired diagCoeffTable
(orchestrator/sweep.go), against banked in-onset cells T(n, n-k), and against
the banked deg/lead facts for R_k.

Level-k weights are the only input to R_k (E_b, E_t, sigma and the pure part
all enter at surplus <= k), so a weight file complete through level L supports
exactly k <= L.  Nothing is extrapolated and no swept value ever enters the
derivation -- the wired table and the banked cells are compared against, never
used as inputs.

Pathologies avoided (results/diagonal-formula.md:242-251): no fixed-point iteration
of mu (this route is finite polynomial algebra, order-by-order by construction),
and no mixing of the u-series master equation H with the y-series chain -- only
the y-series chain appears here.

Run:  python3 experiments/severance_w1_assemble.py [weights.txt] [--red]
"""
import os
import sys
import time
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri  # noqa: E402
from cluster_weight_dp import compositions, KNOWN_WEIGHTS  # noqa: E402

DEFAULT_WEIGHTS = os.path.join(ROOT, "results", "severance_w1_weights_k9.txt")

# deg R_k = 2k+1 with these leading coefficients, banked k <= 5
# (docs/proofs/diagonal-law.md "what remains open"; experiments/spine_deeper.py)
BANKED_LEADS = [1, 4, -80, 1753, -40928, 987355]

# banked triangle spot-checks: misreading the per-height files is silent, so
# assert known cells before trusting anything read out of them.
TRI_ANCHORS = {(1, 1): 1, (2, 2): 3, (3, 2): 10, (4, 2): 27, (5, 3): 248}


def load_weights(path):
    """{composition tuple: (interior, boundary_bottom, boundary_top, pure)}."""
    weights = {}
    with open(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 5:
                raise ValueError(f"{path}:{lineno}: expected 5 fields, "
                                 f"got {len(parts)}: {line!r}")
            v = tuple(int(x) for x in parts[0].split(","))
            if any(s < 2 for s in v):
                raise ValueError(f"{path}:{lineno}: bad composition {v}")
            weights[v] = tuple(int(x) for x in parts[1:])
    return weights


def check_weight_coverage(weights):
    """Highest surplus level L for which every composition is present."""
    have = set(weights)
    level = 0
    while True:
        comps = set(compositions(level + 1))
        if not comps <= have:
            return level
        level += 1


def check_known_weights(weights):
    """The file must agree with cluster_weight_dp.KNOWN_WEIGHTS everywhere."""
    bad = [(v, weights.get(v), w) for v, w in KNOWN_WEIGHTS.items()
           if weights.get(v) != w]
    if bad:
        raise AssertionError(f"weight file disagrees with KNOWN_WEIGHTS: {bad}")
    return len(KNOWN_WEIGHTS)


# ---------------------------------------------------------------- polynomials

def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
            for i in range(n)]


def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return r


def ptrim(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def zpow(e):
    return [0] * e + [1]


def omz(e):
    """(1 - 3z)^e."""
    r = [1]
    for _ in range(e):
        r = pmul(r, [1, -3])
    return r


def ymulp(A, B, kmax):
    """Product of two y-graded families of z-polynomials, truncated at y^kmax."""
    R = {}
    for ka, pa in A.items():
        for kb, pb in B.items():
            if ka + kb <= kmax:
                R[ka + kb] = padd(R.get(ka + kb, [0]), pmul(pa, pb))
    return R


def assemble_R(weights, kmax):
    """R_k(z) for k = 0..kmax, from the chain identity (Steps 2 and 4)."""
    Eb = {0: zpow(1)}          # z * (1 + sum W^b y^k z^l)
    Et = {0: [1]}              # 1 + sum W^t y^k z^l
    sig = {}                   # S - 3z = sum W y^k z^(l+1)
    Pp = {}                    # pure part
    for v, (wi, wb, wt, wp) in weights.items():
        k, l = sum(v) - len(v), len(v)
        if k > kmax:
            continue
        Eb[k] = padd(Eb.get(k, [0]), [wb * c for c in zpow(l + 1)])
        Et[k] = padd(Et.get(k, [0]), [wt * c for c in zpow(l)])
        sig[k] = padd(sig.get(k, [0]), [wi * c for c in zpow(l + 1)])
        Pp[k] = padd(Pp.get(k, [0]), [wp * c for c in zpow(l)])

    # sigma^m, m = 0..kmax (every sigma term has y-order >= 1, so m <= k)
    sp = [{0: [1]}]
    for _ in range(kmax):
        sp.append(ymulp(sp[-1], sig, kmax))

    out = []
    for k in range(kmax + 1):
        num = [0]
        for kb, pb in Eb.items():
            if kb > k:
                continue
            pbt = pmul(pb, [1])
            for kt, pt in Et.items():
                km = k - kb - kt
                if km < 0:
                    continue
                head = pmul(pbt, pt)
                for m in range(km + 1):
                    s = sp[m].get(km)
                    if s is None:
                        continue
                    num = padd(num, pmul(pmul(head, s), omz(k - m)))
        if k in Pp:
            num = padd(num, pmul(Pp[k], omz(k + 1)))
        out.append(ptrim(num))
    return out


def pk_from_R(R, k):
    """Step 5: R_k(z)/(1-3z)^(k+1) -> P_k(n), exact Fractions, ascending."""
    # a_j: coefficients of R_k((1-w)/3) in w
    a = [F(0)] * len(R)
    sub = [F(1)]                              # ((1-w)/3)^i
    third = [F(1, 3), F(-1, 3)]
    for i, c in enumerate(R):
        if c:
            for j, s in enumerate(sub):
                a[j] += c * s
        sub = pmul(sub, third)

    # q_k(H) = sum_{i=1}^{k+1} a_{k+1-i} * C(H+i-1, i-1)
    q = [F(0)]
    for i in range(1, k + 2):
        coef = a[k + 1 - i] if k + 1 - i < len(a) else F(0)
        if coef == 0:
            continue
        binom = [F(1)]                        # (H+1)...(H+i-1)/(i-1)!
        for t in range(1, i):
            binom = pmul(binom, [F(t), F(1)])
            binom = [c / t for c in binom]
        q = padd(q, [coef * c for c in binom])

    # P_k(n) = 3^(1+2k) * q_k(n-k)
    shifted = [F(0)]
    pw = [F(1)]                               # (n-k)^d
    for d, c in enumerate(q):
        if c:
            shifted = padd(shifted, [c * x for x in pw])
        pw = pmul(pw, [F(-k), F(1)])
    return [F(3) ** (1 + 2 * k) * c for c in shifted]


def peval(poly_asc, n):
    r = F(0)
    for c in reversed(poly_asc):
        r = r * n + c
    return r


def wired_poly(P, k):
    """Wired P_k as ascending exact Fractions."""
    coeffs, den = P[k]
    return [F(c, den) for c in reversed(coeffs)]


def main():
    t0 = time.time()
    args = [a for a in sys.argv[1:] if a != "--red"]
    red = "--red" in sys.argv[1:]
    path = args[0] if args else DEFAULT_WEIGHTS

    weights = load_weights(path)
    nknown = check_known_weights(weights)
    L = check_weight_coverage(weights)
    print(f"weights: {len(weights)} compositions from {path}")
    print(f"cross-check vs KNOWN_WEIGHTS: {nknown}/{nknown} agree")
    print(f"complete surplus levels: 1..{L}  ->  K_max = {L}")
    if L < 1:
        raise SystemExit("weight file does not even cover level 1")

    if red:
        # lowest level, so the perturbation propagates into every derived P_k
        victim = min(weights, key=lambda v: (sum(v) - len(v), v))
        wi, wb, wt, wp = weights[victim]
        weights[victim] = (wi + 1, wb, wt, wp)
        print(f"RED: perturbed interior weight of {victim}: {wi} -> {wi + 1}")

    P = read_pk()
    tri = read_tri()
    for cell, val in TRI_ANCHORS.items():
        got = tri.get(cell)
        assert got == val, f"banked triangle misread at T{cell}: {got} != {val}"
    print(f"banked triangle: {len(tri)} cells, {len(TRI_ANCHORS)} anchors OK")

    Rs = assemble_R(weights, L)

    failures = []
    print()
    print(f"{'k':>2} {'degR':>5} {'lead(R_k)':>12} {'wired':>8} {'cells':>16} "
          f"{'deg/lead':>9}")
    for k in range(1, L + 1):
        R = Rs[k]
        deg, lead = len(R) - 1, R[-1]

        derived = pk_from_R(R, k)
        derived = derived + [F(0)] * max(0, (k + 1) - len(derived))
        wired = wired_poly(P, k) if k in P else None
        if wired is None:
            vw = "no-wired"
            failures.append(f"k={k}: no wired P_k to compare")
        else:
            w = wired + [F(0)] * max(0, len(derived) - len(wired))
            d = derived + [F(0)] * max(0, len(wired) - len(derived))
            ok = d == w
            vw = "MATCH" if ok else "DIFFER"
            if not ok:
                failures.append(f"k={k}: derived P_k != wired "
                                f"(derived {d}, wired {w})")

        # in-onset cells: n >= 2k+1, T(n, n-k) = P_k(n) * 3^(n-1-3k)
        cells, cells_ok = [], 0
        for n in range(2 * k + 1, 2 * k + 9):
            H = n - k
            if (n, H) not in tri:
                continue
            e = n - 1 - 3 * k
            pred = peval(derived, n) * (F(3) ** e if e >= 0
                                        else F(1, 3 ** (-e)))
            cells.append((n, H, pred == tri[(n, H)]))
            if pred == tri[(n, H)]:
                cells_ok += 1
            if len(cells) >= 3:
                break
        if len(cells) < 2:
            failures.append(f"k={k}: fewer than 2 banked in-onset cells found")
        if cells_ok != len(cells):
            bad = [(n, H) for n, H, o in cells if not o]
            failures.append(f"k={k}: law with derived P_k misses cells {bad}")
        vc = f"{cells_ok}/{len(cells)} ok"

        dl_ok = (deg == 2 * k + 1)
        if not dl_ok:
            failures.append(f"k={k}: deg R_k = {deg}, expected {2 * k + 1}")
        if k < len(BANKED_LEADS):
            if lead != BANKED_LEADS[k]:
                dl_ok = False
                failures.append(f"k={k}: lead(R_k) = {lead}, banked "
                                f"{BANKED_LEADS[k]}")
            vd = "OK" if dl_ok else "BAD"
        else:
            vd = "OK*" if dl_ok else "BAD"      # * = deg only, no banked lead

        print(f"{k:>2} {deg:>5} {lead:>12} {vw:>8} {vc:>16} {vd:>9}")

    print()
    print("(* deg checked; no banked lead beyond k=5)")
    dt = time.time() - t0
    if red:
        if failures:
            print(f"RED CONTROL FIRED: {len(failures)} assertion(s) failed")
            for f in failures[:5]:
                print(f"  - {f}")
            print(f"runtime {dt:.2f}s")
            return 0
        print("RED CONTROL DID NOT FIRE -- gate is blind, this is a failure")
        print(f"runtime {dt:.2f}s")
        return 2
    if failures:
        print(f"GATE RED: {len(failures)} failure(s)")
        for f in failures:
            print(f"  - {f}")
        print(f"runtime {dt:.2f}s")
        return 1
    print("GATE GREEN")
    print(f"SEVERED: k = 1..{L}")
    print(f"runtime {dt:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
