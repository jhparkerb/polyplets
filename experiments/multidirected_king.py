#!/usr/bin/env python3
"""Multi-directed king animals: exact terms from Bacher's Nordic-decomposition GF.

Source: Axel Bacher, "Directed and multi-directed animals in the king's lattice",
arXiv:1301.1365v3 (literature/bacher_2015_directed_multidirected_king_lattice.pdf).

The scheme (Theorem 8, Lemma 9, Lemma 11):

    S  = t (1+S)^2 / (1 - t (1+S))                    (1)  half-animals, A001003
    R  = S + t (1+S)                                  (3)
    D  = S + S^2 / (1 - R)                            (2) at u=1, A047781
    Q  = (2 - 2t) S - t                               (10)
    B  = sum_{k>=0} S (1+S)^k * Q R^k / (1 - Q R^k)   (Lemma 11)
    M  = D / (1 - B)                                  (11)

[t^n] M = number of multi-directed king animals of area n, up to translation.

Valuations: v(S)=v(R)=v(Q)=1, so the k-th summand of B has valuation k+2 and the
sum is a well-defined formal power series; only k <= N-2 matters mod t^(N+1).

Growth: M has a simple pole at rho_M with B(rho_M)=1, so m(n) ~ lambda * mu^n
with mu = 1/rho_M = 6.475... (Corollary 12).  The intermediate series B has its
own pole rho_B, root of 1 - 5x - 7x^2 + x^3 (Lemma 11), 1/rho_B = 6.118... --
that is NOT the growth constant, and the ratio test below reports both so the
two cannot be confused.

Everything is exact integer arithmetic.  Cross-checks (all fail-closed):
  * S against A001003 (little Schroeder)
  * D against the closed form (1/4)((1+t)/sqrt(1-6t+t^2) - 1), computed by an
    independent exact series square root -- so the S/R/D chain is anchored
  * M against the brute-force enumeration of Definition 2
    (build/directed_cone_anchor mdir), where available

Usage: python3 experiments/multidirected_king.py [N] [--out FILE] [--crosstab M]
       --crosstab M runs the from-scratch brute force below and cross-tabulates
       Definition 2 against "control B" for n = 1..M (M <= 8 is seconds).
"""
import argparse
import sys
import time

# ---------------------------------------------------------------- series ops
# A series is a list of N+1 ints, index = exponent.  All truncated mod t^(N+1).


def mul(a, b, n):
    out = [0] * (n + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        if i > n:
            break
        for j, bj in enumerate(b[: n - i + 1]):
            if bj:
                out[i + j] += ai * bj
    return out


def inv(a, n):
    """1/a for a with a[0] == 1 (all series inverted here are 1 - (val>=1))."""
    if a[0] != 1:
        raise ValueError("inv expects constant term 1")
    out = [0] * (n + 1)
    out[0] = 1
    for k in range(1, n + 1):
        s = 0
        for j in range(1, min(k, len(a) - 1) + 1):
            if a[j]:
                s += a[j] * out[k - j]
        out[k] = -s
    return out


def sub(a, b, n):
    return [(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n + 1)]


def add(a, b, n):
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n + 1)]


def shift(a, k, n):
    """multiply by t^k"""
    return ([0] * k + a)[: n + 1] + [0] * max(0, n + 1 - k - len(a))


def one(n):
    return [1] + [0] * n


# ---------------------------------------------------------------- the scheme


def half_animals(n):
    """S from the functional equation (1), by fixed-point iteration.

    Each pass gains one order, so n passes suffice; S has valuation 1.
    """
    s = [0] * (n + 1)
    for _ in range(n):
        ops = add(one(n), s, n)                 # 1 + S
        num = shift(mul(ops, ops, n), 1, n)     # t (1+S)^2
        den = sub(one(n), shift(ops, 1, n), n)  # 1 - t (1+S)
        s = mul(num, inv(den, n), n)
    return s


def sqrt_kernel(n):
    """sqrt(1 - 6t + t^2) as an exact integer series, independent of S."""
    # c = 1 - 6t + t^2; solve r^2 = c with r[0] = 1 by the standard recurrence.
    c = [0] * (n + 1)
    c[0] = 1
    if n >= 1:
        c[1] = -6
    if n >= 2:
        c[2] = 1
    r = [0] * (n + 1)
    r[0] = 1
    for k in range(1, n + 1):
        s = 0
        for j in range(1, k):
            s += r[j] * r[k - j]
        num = c[k] - s
        if num % 2:
            raise AssertionError("series sqrt left a non-integer coefficient")
        r[k] = num // 2
    return r


def directed_closed_form(n):
    """D(t) = (1/4)((1+t)/sqrt(1-6t+t^2) - 1), the A047781 anchor."""
    ker = inv(sqrt_kernel(n), n)
    num = mul([1, 1] + [0] * (n - 1), ker, n)
    d = sub(num, one(n), n)
    out = []
    for v in d:
        if v % 4:
            raise AssertionError("closed form left a non-integer coefficient")
        out.append(v // 4)
    return out


def multidirected(n, progress=None):
    """Return (S, R, Q, D, B, M) truncated mod t^(n+1)."""
    s = half_animals(n)
    ops = add(one(n), s, n)                       # 1 + S
    r = add(s, shift(ops, 1, n), n)               # (3)
    d = add(s, mul(mul(s, s, n), inv(sub(one(n), r, n), n), n), n)   # (2) at u=1
    q = sub(mul([2, -2] + [0] * (n - 1), s, n), [0, 1] + [0] * (n - 1), n)  # (10)

    b = [0] * (n + 1)
    pow_ops = one(n)   # (1+S)^k
    pow_r = one(n)     # R^k
    for k in range(0, max(0, n - 1)):
        x = mul(q, pow_r, n)                      # Q R^k, valuation k+1
        term = mul(mul(s, pow_ops, n), mul(x, inv(sub(one(n), x, n), n), n), n)
        b = add(b, term, n)
        if progress and k % 25 == 0:
            progress(k)
        pow_ops = mul(pow_ops, ops, n)
        pow_r = mul(pow_r, r, n)
    m = mul(d, inv(sub(one(n), b, n), n), n)
    return s, r, q, d, b, m


# ---------------------------------------------------------------- references

A001003 = [1, 1, 3, 11, 45, 197, 903, 4279, 20793, 103049, 518859, 2646723]
A047781 = [1, 4, 19, 96, 501, 2668, 14407, 78592, 432073, 2390004]

# results/subclasses.md, ctrlB column (bottom-row-waived BFS), n=1..14.
# NOT multi-directed -- kept here so the two can be compared explicitly.
CTRL_B = [1, 4, 20, 106, 576, 3179, 17736, 99748, 564430, 3209194,
          18316729, 104872413, 602013085, 3463412836]


# ------------------------------------- third implementation: from-scratch brute
# Shares nothing with cpp/directed_cone_anchor.cpp: frozenset growth with
# explicit translation canonicalisation instead of Redelmeier's untried set,
# dict-of-sets reachability instead of a stamped grid. Its job here is the 2x2
# cross-tabulation of Bacher's Definition 2 against "control B", which the C++
# filter modes cannot produce (they evaluate one predicate per run).
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
CONE5 = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0)]


def _canon(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def _reach(A, seeds, blocked=(), steps=CONE5):
    seen, stack = set(seeds), list(seeds)
    while stack:
        x, y = stack.pop()
        for dx, dy in steps:
            c = (x + dx, y + dy)
            if c in A and c not in seen and c not in blocked:
                seen.add(c)
                stack.append(c)
    return seen


def sources_keystones(A):
    """Definition 2's marks: strict local minima / maxima of the column-bottom
    profile b(x), leftmost column of a plateau taking the mark."""
    xs = sorted({x for x, _ in A})
    b = {x: min(y for xx, y in A if xx == x) for x in xs}
    src, key = [], []
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and b[xs[j + 1]] == b[xs[i]]:
            j += 1
        v = b[xs[i]]
        lo_l = i > 0 and b[xs[i - 1]] < v
        lo_r = j + 1 < len(xs) and b[xs[j + 1]] < v
        if not lo_l and not lo_r:
            src.append((xs[i], v))
        elif lo_l and lo_r:
            key.append((xs[i], v))
        i = j + 1
    return src, key


def is_multidirected(A, check_keystones=True):
    src, key = sources_keystones(A)
    if len(_reach(A, src)) != len(A):
        return False
    if not check_keystones:
        return True
    back = [(-dx, -dy) for dx, dy in CONE5]
    for t in key:
        blocked = {k for k in key if k != t and k[1] == t[1]}
        got = _reach(A, [t], blocked, back)
        if not any(s in got and s[0] < t[0] for s in src):
            return False
        if not any(s in got and s[0] > t[0] for s in src):
            return False
    return True


def is_ctrl_b(A):
    """'Control B' of results/subclasses.md: forward flood seeded from
    every cell of the GLOBAL bottom row."""
    ys = min(y for _, y in A)
    seeds = [(x, y) for x, y in A if y == ys]
    return len(_reach(A, seeds)) == len(A)


def crosstab(nmax):
    """-> {n: (both, mdir_only, ctrlB_only, neither, total)}."""
    out = {}
    layer = {frozenset({(0, 0)})}
    for n in range(1, nmax + 1):
        cells = [0, 0, 0, 0]
        for A in layer:
            md, cb = is_multidirected(A), is_ctrl_b(A)
            cells[0 if (md and cb) else 1 if md else 2 if cb else 3] += 1
        out[n] = tuple(cells) + (len(layer),)
        if n < nmax:
            nxt = set()
            for A in layer:
                for x, y in A:
                    for dx, dy in KING:
                        c = (x + dx, y + dy)
                        if c not in A:
                            nxt.add(_canon(A | {c}))
            layer = nxt
    return out


def rho_b():
    """Root of 1 - 5x - 7x^2 + x^3 in (0,1): the pole of B (Lemma 11)."""
    lo, hi = 0.0, 0.2

    def f(x):
        return 1 - 5 * x - 7 * x * x + x ** 3

    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("n", nargs="?", type=int, default=100)
    ap.add_argument("--out", help="write 'n m(n)' lines here")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--crosstab", type=int, metavar="NMAX",
                    help="from-scratch brute force: cross-tabulate Definition 2 "
                         "against control B for n=1..NMAX (n<=8 is seconds)")
    args = ap.parse_args()
    n = args.n

    t0 = time.time()
    s, r, q, d, b, m = multidirected(n)
    elapsed = time.time() - t0

    # --- fail-closed cross-checks -------------------------------------------
    k = min(n, len(A001003) - 1)
    if s[1:k + 1] != A001003[1:k + 1]:
        print("FAIL: S != A001003 (little Schroeder)", file=sys.stderr)
        print("  got %s" % s[1:k + 1], file=sys.stderr)
        return 1
    cf = directed_closed_form(n)
    if d != cf:
        print("FAIL: D from (1)-(3) != closed form (1/4)((1+t)/sqrt(1-6t+t^2)-1)",
              file=sys.stderr)
        return 1
    k = min(n, len(A047781))
    if d[1:k + 1] != A047781[:k]:
        print("FAIL: D != A047781", file=sys.stderr)
        return 1
    if m[0] != 0 or m[1] != 1:
        print("FAIL: M has the wrong low-order shape", file=sys.stderr)
        return 1
    for i in range(1, n + 1):
        if m[i] < d[i]:
            print("FAIL: m(%d) < d(%d) -- multi-directed must contain directed"
                  % (i, i), file=sys.stderr)
            return 1

    if args.out:
        with open(args.out, "w") as fh:
            for i in range(1, n + 1):
                fh.write("%d %d\n" % (i, m[i]))

    if args.crosstab:
        print("brute force, Definition 2 vs control B (both, mdir only, "
              "ctrlB only, neither):")
        print("%3s %12s %12s %12s %12s %12s %12s" %
              ("n", "both", "mdir only", "ctrlB only", "neither", "m(n)", "all"))
        ok = True
        for k, (both, mo, co, ne, tot) in crosstab(args.crosstab).items():
            print("%3d %12d %12d %12d %12d %12d %12d" %
                  (k, both, mo, co, ne, both + mo, tot))
            if both + mo != m[k]:
                print("FAIL: brute m(%d)=%d != series %d" % (k, both + mo, m[k]),
                      file=sys.stderr)
                ok = False
        if not ok:
            return 1
        print()

    if args.quiet:
        return 0

    print("multi-directed king animals, Bacher arXiv:1301.1365 Theorem 8")
    print("N=%d  series built in %.2f s" % (n, elapsed))
    print("checks: S=A001003 ok; D=closed form ok; D=A047781 ok; m(n)>=d(n) ok")
    print()
    hdr = "%3s %24s %24s %24s" % ("n", "m(n) multi-directed", "d(n) directed A047781",
                                  "ctrlB (bottom-row waived)")
    print(hdr)
    for i in range(1, min(n, 20) + 1):
        cb = str(CTRL_B[i - 1]) if i <= len(CTRL_B) else "-"
        flag = ""
        if i <= len(CTRL_B):
            flag = "  ==" if m[i] == CTRL_B[i - 1] else "  != ctrlB"
        print("%3d %24d %24d %24s%s" % (i, m[i], d[i], cb, flag))
    if n > 20:
        print("...")
        print("%3d %24d" % (n, m[n]))
    print()
    mu_b = 1.0 / rho_b()
    print("ratio test (must approach 1/rho_M = 6.4752, NOT 1/rho_B = %.4f):" % mu_b)
    for i in list(range(max(2, n - 4), n + 1)):
        print("  m(%d)/m(%d) = %.6f" % (i, i - 1, m[i] / m[i - 1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
