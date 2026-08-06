#!/usr/bin/env python3
"""How many digits does the mu_H cross-check actually establish?

results/strip-growth-lambda-bounds.md used to say cpp/strip_mu.cpp "reproduces
the GF-root mu_H exactly for H<=11". It does not, and could not: this script
measures the two sides of that comparison, and the write-ups now state what it
found (agreement to the engine's 7 printed decimals, 7.8-8.9 significant
digits; and the GF side's own precision, which at the old mp.dps=50 default was
8 digits at H=11 -- see --diagnose below).

  GF-root side   the old experiments/mu_H_from_atoms.py: 1/(smallest positive
                 root of Q_H) by scan-and-bisect in mpmath at mp.dps=50. Its
                 own precision is measured here by recomputing at dps=200 with
                 a bisection deep enough for that precision.
  engine side    build/strip_mu: double-precision power iteration, rho
                 converged to 1e-11 relative, x* bisected to 1e-13, printed
                 %.7f (results/mu_H_powiter_2_11.log).

Agreement is reported in matching significant digits, floor(-log10(relative
difference)), which is what the claim can honestly assert.

Usage:  python3 experiments/mu_H_precision_audit.py [powiter.log]
        (default log: results/mu_H_powiter_2_11.log, from `build/strip_mu 2 11`)
        python3 experiments/mu_H_precision_audit.py --diagnose H
        (one H at dps=50,60,120,200: the scan bracket and the root, so a
         precision loss can be told apart from a mis-bracketed root)
Cost:   ~3 min for the table, ~6 min for --diagnose 11 (measured); the dps=200
        recomputations dominate. Records: results/mu_H_diagnose_H11.log.
"""
import ast
import os
import re
import sys

from mpmath import mp, mpf, log10, fabs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFS = os.path.join(ROOT, "results", "fixed_height_gfs.txt")
LOG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "results", "mu_H_powiter_2_11.log")


def read_Q():
    """{H: denominator coefficients low->high} from the banked fixed-height GFs."""
    Q, H = {}, None
    with open(GFS) as f:
        for line in f:
            m = re.match(r"H=(\d+)", line)
            if m:
                H = int(m.group(1))
            if line.startswith("Q:") and H is not None:
                Q[H] = ast.literal_eval(line[2:].strip())
    return Q


def mu_of(q, dps):
    """mu = 1/(smallest positive root of q), at working precision dps.

    Same scan-and-bisect as experiments/mu_H_from_atoms.py, but with the
    bisection depth tied to dps -- at 200 fixed halvings the bracket bottoms
    out near 1e-64 regardless of how many digits mpmath is carrying.
    """
    mp.dps = dps
    iters = int(3.4 * dps) + 50

    def polyval(x):
        s = mpf(0)
        for c in reversed(q):
            s = s * x + c
        return s

    step = mpf("0.0002")
    x = step
    prev = polyval(mpf(0))
    while x < mpf("0.6"):
        cur = polyval(x)
        if cur == 0:
            return 1 / x
        if (prev > 0) != (cur > 0):
            lo, hi = x - step, x
            for _ in range(iters):
                mid = (lo + hi) / 2
                if (polyval(lo) > 0) == (polyval(mid) > 0):
                    lo = mid
                else:
                    hi = mid
            return 1 / ((lo + hi) / 2)
        prev = cur
        x += step
    raise ValueError("no root found in (0,0.6)")


def scan_bracket(q, dps):
    """The first sign-change cell the coarse scan finds, at precision dps.

    Reported separately because a low-precision scan can misjudge the sign of
    Q near its own root and bracket the WRONG cell -- a failure that looks like
    a converged answer.
    """
    mp.dps = dps

    def polyval(x):
        s = mpf(0)
        for c in reversed(q):
            s = s * x + c
        return s

    step = mpf("0.0002")
    x = step
    prev = polyval(mpf(0))
    while x < mpf("0.6"):
        cur = polyval(x)
        if (prev > 0) != (cur > 0):
            return mp.nstr(x - step, 12), mp.nstr(x, 12), mp.nstr(cur, 8)
        prev = cur
        x += step
    return None


def diagnose(H):
    """Where does the old mp.dps=50 default lose H's root? Bracket, or bisection?"""
    q = read_Q()[H]
    for dps in (50, 60, 120, 200):
        br = scan_bracket(q, dps)
        mu = mu_of(q, dps)
        mp.dps = 30
        print(f"dps={dps:3d}  bracket={br}  mu={mp.nstr(mu, 25)}")


def digits(a, b):
    """Matching significant digits of a vs b (b the reference)."""
    mp.dps = 220
    d = fabs(mpf(a) - mpf(b))
    if d == 0:
        return None
    return int(-log10(d / fabs(mpf(b))))


def read_cert_receipts():
    """{H: mu_float} from results/strip_mu_certificates.log.

    A second, sharper arm of the same cross-check: strip_mu_cert's search phase
    records its power-iteration value to 10 significant digits, three more than
    build/strip_mu prints. Last receipt per H wins.
    """
    out = {}
    path = os.path.join(ROOT, "results", "strip_mu_certificates.log")
    if not os.path.isfile(path):
        return out
    for line in open(path):
        kv = dict(p.split("=", 1) for p in line.split() if "=" in p)
        if kv.get("event") == "certificate" and "mu_float" in kv:
            out[int(kv["H"])] = kv["mu_float"]
    return out


def read_powiter(path):
    """{H: printed mu_H} from a `build/strip_mu Hmin Hmax` log."""
    out = {}
    with open(path) as f:
        for line in f:
            p = [c.strip() for c in line.split("|")]
            if len(p) >= 3 and p[0].isdigit():
                out[int(p[0])] = p[2]
    return out


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--diagnose":
        return diagnose(int(sys.argv[2]))
    Q = read_Q()
    pw = read_powiter(LOG)
    cert = read_cert_receipts()
    hs = [H for H in sorted(Q) if H >= 2]

    ref = {H: mu_of(Q[H], 200) for H in hs}
    at50 = {H: mu_of(Q[H], 50) for H in hs}

    print(f"engine log: {LOG}")
    print(" H   mu_H (GF root, dps=200)          dps=50 ok  strip_mu     agree"
          "   cert mu_float  agree")
    worst_gf, worst_x, worst_c = 10**9, 10**9, 10**9
    for H in hs:
        mp.dps = 40
        gf50 = digits(at50[H], ref[H])
        row = f"{H:2d}   {mp.nstr(ref[H], 25):<32s} {str(gf50):>7s}"
        for src, wid in ((pw, 11), (cert, 14)):
            if H in src:
                ag = digits(mpf(src[H]), ref[H])
                row += f"  {src[H]:>{wid}s} {ag:>6d}"
                if src is pw:
                    worst_x = min(worst_x, ag)
                else:
                    worst_c = min(worst_c, ag)
            else:
                row += f"  {'-':>{wid}s} {'-':>6s}"
        if gf50 is not None:
            worst_gf = min(worst_gf, gf50)
        print(row)

    print()
    print(f"GF side at the script's mp.dps=50: >= {worst_gf} matching digits vs"
          " the dps=200 recomputation")
    print(f"cross-check vs build/strip_mu (H={min(pw)}..{max(pw)}):"
          f" {worst_x} significant digits, worst case")
    print("  (the engine prints %.7f, so more digits are not even visible;"
          " its own\n   convergence tolerances are rho 1e-11 / x* 1e-13.)")
    if worst_c < 10**9:
        chs = [H for H in hs if H in cert]
        print(f"cross-check vs strip_mu_cert receipts (H={min(chs)}..{max(chs)},"
              f" mu_float at 10 digits): {worst_c} significant digits, worst case")


if __name__ == "__main__":
    main()
