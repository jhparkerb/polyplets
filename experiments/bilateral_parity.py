#!/usr/bin/env python3
"""Why A030234 alone among the companions is not log-convex --
docs/time-at-the-bar.md (deleted) A3.2.

results/closed-doors.md C2 records the fact and calls it "a parity effect
worth its own look", and nobody has looked.  A006770, A030222, A030233 and
A030235 are all log-convex past small n; the bilateral count A030234 fails
"at every even n".  A failure that systematic is usually two families added
together, not one family misbehaving.

THE STRUCTURAL CLAIM THIS TESTS.  A bilaterally symmetric animal has a mirror
axis, and on the square grid an axis comes in two kinds:

  through-cell   the axis runs along a column of cells.  Cells on the axis are
                 fixed by the reflection; every other cell is paired.  So
                 n = (cells on the axis) + 2*(pairs), and n may be odd or even
                 according to how many axis cells there are.
  between-cell   the axis runs between two columns.  NO cell is fixed;
                 every cell is in a 2-cycle.  So n is necessarily EVEN.

So odd n is served by one family and even n by two, and

    b(n) = T(n) + [n even] * B(n)

with T and B growing at different rates.  An extra positive term switched on at
every second index is exactly the shape that breaks log-convexity on the
interleaved sequence while leaving each parity class well behaved.

WHAT WOULD FALSIFY IT.  If the parity effect were noise rather than an additive
family, the even-only and odd-only subsequences would be no better behaved than
the interleaved one.  So the test is: check log-convexity ON EACH PARITY CLASS
SEPARATELY, in exact integer arithmetic.  If both classes are clean and only
the interleaving fails, the two-family reading is supported.  If a parity class
also fails, it is not, and this script says so.

CONTROLS.
  (a) The other four companions must be reported log-convex past small n, or
      the checker is not measuring log-convexity.
  (b) A planted sequence of exactly the conjectured shape -- one geometric
      family plus a second switched on at even n -- must reproduce the
      signature (interleaved fails, parity classes pass).
  (c) A planted single-family geometric sequence must pass everywhere, so the
      signature is not something the checker prints for any input.

Usage: python3 experiments/bilateral_parity.py

Target machine: ayr or dalby.  Cost: instant, exact integer arithmetic on
banked b-files.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")

SERIES = {
    "A006770 fixed": "b006770_upload.txt",
    "A030222 free": "b030222_upload.txt",
    "A030233 one-sided": "b030233_upload.txt",
    "A030234 bilateral": "b030234_upload.txt",
    "A030235 asymmetric": "b030235_upload.txt",
}


def load(fn):
    d = {}
    with open(os.path.join(RESULTS, fn)) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            p = ln.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit():
                d[int(p[0])] = int(p[1])
    return d


def violations(d, step=1):
    """Indices n where a(n)^2 >= a(n-step)*a(n+step) -- exact integers."""
    bad = []
    ns = sorted(d)
    for n in ns:
        lo, hi = n - step, n + step
        if lo in d and hi in d and d[lo] > 0 and d[hi] > 0:
            if d[n] * d[n] >= d[lo] * d[hi]:
                bad.append(n)
    return bad


def describe(name, d):
    inter = violations(d, 1)
    par = violations(d, 2)
    ns = sorted(d)
    print("  %-20s n=%d..%d   interleaved: %-22s  same-parity: %s"
          % (name, ns[0], ns[-1],
             ("clean" if not inter else "%d viol, first %d, last %d"
              % (len(inter), inter[0], inter[-1])),
             ("clean" if not par else "%d viol: %s" % (len(par), par[:8]))))


def controls():
    ok = True

    # (c) one geometric family: clean both ways.
    single = {n: 3 ** n for n in range(1, 33)}
    # a(n)^2 == a(n-1)a(n+1) exactly for a pure geometric, so it is the
    # boundary case and must be reported as a violation of STRICT convexity.
    v1 = violations(single, 1)
    good = len(v1) > 0
    print("RED  a pure geometric is at the strict-convexity boundary, "
          "not strictly log-convex (%d flagged)   %s"
          % (len(v1), "OK" if good else "FAILED"))
    ok &= good

    # A single log-convex family must be clean both ways.  The shape has to be
    # the REAL one: a(n) ~ B*lam^n*n^theta with theta = -1, whose log is
    # n*log(lam) - log(n) + const, and -log(n) is the convex part.  The first
    # version of this control used lam^n * n^2, which is log-CONCAVE -- the
    # control caught it before the script was used on anything.
    SC = 10 ** 9   # fixed-point scale, so the arithmetic stays exact integers
    conv = {n: (3 ** n * SC) // n for n in range(1, 33)}
    good = not violations(conv, 1) and not violations(conv, 2)
    print("RED  a single log-convex family (lam^n/n) is clean interleaved AND "
          "same-parity   %s" % ("OK" if good else "FAILED"))
    ok &= good

    # (b) the conjectured shape: second family switched on at even n.
    two = {}
    for n in range(1, 33):
        v = (3 ** n * SC) // n
        if n % 2 == 0:
            v += (2 ** n * SC) // n
        two[n] = v
    iv, pv = violations(two, 1), violations(two, 2)
    good = len(iv) > 0 and not pv
    print("RED  a family switched on at even n breaks the interleaved test "
          "(%d) and leaves both parity classes clean (%d)   %s"
          % (len(iv), len(pv), "OK" if good else "FAILED"))
    ok &= good
    return ok


def main():
    print("A030234's parity effect -- controls first")
    if not controls():
        print("\nCONTROLS FAILED -- nothing below is worth reading")
        return 1

    print("\nthe five companions, exact integer arithmetic:")
    data = {}
    for name, fn in SERIES.items():
        data[name] = load(fn)
        describe(name, data[name])

    b = data["A030234 bilateral"]
    print("\nA030234 in detail.  Ratio b(n)/b(n-1), which log-convexity says")
    print("must increase; a drop is a violation at n-1:")
    ns = sorted(b)
    prev = None
    for n in ns[1:]:
        if n - 1 not in b or b[n - 1] == 0:
            continue
        r = b[n] / b[n - 1]
        mark = ""
        if prev is not None and r < prev:
            mark = "   <- DROP (even n)" if n % 2 == 0 else "   <- DROP (odd n)"
        print("   n=%2d  ratio=%.5f%s" % (n, r, mark))
        prev = r

    # The decomposition, made quantitative.  Write T for the through-cell
    # family and B for the between-cell one, so b(odd) = T and b(even) = T + B,
    # and let rho = B/T.  With T(n) ~ C mu^n n^theta the two consecutive
    # ratios are
    #
    #     g(even) = b(even)/b(odd)  ~ mu * (1 + rho)
    #     g(odd)  = b(odd)/b(even)  ~ mu / (1 + rho)
    #
    # so their product recovers mu with rho cancelling, and their quotient
    # recovers (1 + rho)^2 with mu cancelling.  Neither needs a fit.
    print("\nDecomposition.  b(odd) = T, b(even) = T + B, rho = B/T:")
    print("   %-6s %-10s %-10s %-10s" % ("n", "mu_est", "rho", "B/T as 1 in"))
    for n in ns:
        if n % 2 or n - 1 not in b or n + 1 not in b or n - 2 not in b:
            continue
        g_even = b[n] / b[n - 1]
        g_odd = b[n + 1] / b[n]
        mu = (g_even * g_odd) ** 0.5
        rho = (g_even / g_odd) ** 0.5 - 1.0
        if n >= 8:
            print("   %-6d %-10.5f %-10.5f 1 in %.1f"
                  % (n, mu, rho, 1.0 / rho if rho else float('inf')))
    print("\n   mu is the bilateral growth constant; sqrt(lambda_king) =")
    print("   sqrt(7.1102) = 2.66650 is what it must approach if a symmetric")
    print("   animal is determined by half of itself.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
