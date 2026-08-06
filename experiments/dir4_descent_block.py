#!/usr/bin/env python3
"""The 4-cone-truncated descending block of results/hv-growth-sandwich.md.

Phase (0,1) of the HV-convex transfer operator -- bottoms still falling, tops
already falling -- has kernel min(h,h')+1 unrestricted. The 4-cone condition
d >= -1 truncates it to

    h' <= h      d in [-1, 0]     2 placements
    h' == h + 1  d == -1          1 placement
    h' >  h + 1  none             0

which is one of only two blocks the condition touches. Unlike the other three
blocks this one is NOT height-monotone (heights may climb, one row at a time),
so Lemma 2's stack bound does not apply to it and it can carry exponential
weight of its own. This script counts it by area and measures that weight, to
test whether it is the source of the (dir4, HV-convex) series' extra
subdominant singularity at mu * 0.803651401483 = 2.51457964388.

RED control: the same DP with the climb step allowed to carry weight 2 (i.e.
forgetting that d == -1 is forced when h' == h+1) must give different numbers,
and the brute-force enumeration over height sequences is the oracle for n <= 12.

Usage: python3 experiments/dir4_descent_block.py [--nmax 700] [--out FILE]
"""
import argparse
import sys
from functools import lru_cache


def brute(nmax, climb_weight=1):
    """Direct enumeration over height sequences, the oracle for the DP."""
    @lru_cache(maxsize=None)
    def rec(remaining, h):
        """Runs of total area `remaining` whose first column has height h."""
        if remaining == h:
            return 1
        total = 0
        rest = remaining - h
        for hp in range(1, min(h, rest) + 1):        # h' <= h: 2 placements
            total += 2 * rec(rest, hp)
        if h + 1 <= rest:                            # h' == h+1: 1 placement
            total += climb_weight * rec(rest, h + 1)
        return total

    out = [0] * (nmax + 1)
    for n in range(1, nmax + 1):
        out[n] = sum(rec(n, h) for h in range(1, n + 1))
    rec.cache_clear()
    return out


def dp(nmax, climb_weight=1):
    """O(n^2) with suffix sums over the previous column height."""
    # f[m] indexed by the height of the FIRST column of a run of area m.
    f = [None] * (nmax + 1)
    suf = [None] * (nmax + 1)      # suf[m][h] = sum_{h' >= h} f[m][h']
    out = [0] * (nmax + 1)
    for n in range(1, nmax + 1):
        row = [0] * (nmax + 2)
        for h in range(1, n + 1):
            m = n - h
            if m == 0:
                row[h] = 1
                continue
            # h' <= h, two placements each (f[m][h'] is 0 beyond h' = m, so the
            # suffix difference needs no clipping)
            v = 2 * (suf[m][1] - suf[m][h + 1])
            if h + 1 <= m:                       # h' == h+1, one placement
                v += climb_weight * f[m][h + 1]
            row[h] = v
        out[n] = sum(row[1:n + 1])
        s = [0] * (nmax + 3)
        for h in range(nmax, 0, -1):
            s[h] = s[h + 1] + row[h]
        f[n], suf[n] = row, s
    return out


def aitken(seq):
    out = []
    for i in range(len(seq) - 2):
        d1 = seq[i + 1] - seq[i]
        d2 = seq[i + 2] - 2 * seq[i + 1] + seq[i]
        out.append(seq[i] - d1 * d1 / d2 if d2 != 0 else seq[i])
    return out


def subdominant(path, prec, levels=6):
    """(mu, mu*rho) for a series a(n) ~ C mu^n (1 + c rho^n): the dominant
    growth constant and the subdominant one, both by Aitken on the tail."""
    from mpmath import mp, mpf
    mp.dps = prec
    a = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith('#'):
                a.append(int(line.split()[-1]))
    r = [mpf(a[i + 1]) / mpf(a[i]) for i in range(len(a) - 1)]
    d = [r[i] - r[i - 1] for i in range(1, len(r))]
    q = [d[i] / d[i - 1] for i in range(1, len(d)) if d[i - 1] != 0]

    def acc(seq):
        est = seq[-1]
        for _ in range(levels):
            if len(seq) < 3:
                break
            seq = aitken(seq)
            est = seq[-1]
        return est

    mu = acc(r[-60:])
    rho = acc(q[-60:])
    return mu, mu * rho


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nmax', type=int, default=700)
    ap.add_argument('--out', default=None)
    ap.add_argument('--compare', default=None,
                    help='series file whose SUBDOMINANT constant should equal '
                         'this block\'s DOMINANT one (pass the (dir4, '
                         'HV-convex) terms here)')
    ap.add_argument('--prec', type=int, default=400)
    args = ap.parse_args()

    ok, got = brute(12), dp(12)
    assert got[1:] == ok[1:], f"DP != brute force: {got[1:]} vs {ok[1:]}"
    print(f"ok   DP == brute force, n<=12: {ok[1:9]}")
    red_b, red_d = brute(12, climb_weight=2), dp(12, climb_weight=2)
    assert red_d[1:] == red_b[1:], "RED control DP/brute disagree"
    assert red_b[1:] != ok[1:], "RED control MUST diverge"
    print(f"ok   RED (climb step weighted 2) diverges: {red_b[1:9]}")

    R = dp(args.nmax)
    print(f"\nR(n) for n=1..10: {R[1:11]}")
    print(f"raw ratios R(n)/R(n-1) at the tail: "
          f"{[R[n] / R[n-1] for n in range(args.nmax - 3, args.nmax + 1)]}")
    if args.out:
        with open(args.out, 'w') as fh:
            for n in range(1, args.nmax + 1):
                fh.write(f"{n} {R[n]}\n")
        print(f"wrote {args.out}")

    if args.compare:
        from mpmath import mp, mpf, nstr
        out = args.out or 'results/mk_dir4_descblock_n700.txt'
        mu_o, mu2_o = subdominant(args.compare, args.prec)
        mu_b, _ = subdominant(out, args.prec)
        mp.dps = args.prec
        rel = abs(mu2_o - mu_b) / abs(mu_b)
        agree = int(-mp.log10(rel)) if rel > 0 else args.prec
        print(f"\n## does this block's DOMINANT constant equal "
              f"{args.compare}'s SUBDOMINANT one?")
        print(f"  block  mu           = {nstr(mu_b, 40)}")
        print(f"  series mu*rho       = {nstr(mu2_o, 40)}")
        print(f"  series mu           = {nstr(mu_o, 40)}")
        print(f"  => they agree to ~{agree} digits")

        # Peel both known exponentials off the compared series: applying the
        # annihilator (E - mu)(E - mu2) leaves the NEXT correction, whose ratio
        # says whether the shared 1.50505 subdominant is still present behind
        # the one the 4-cone condition inserts.
        vals = []
        with open(args.compare) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith('#'):
                    vals.append(int(line.split()[-1]))
        a = [mpf(v) for v in vals]
        c1, c2 = mu_o + mu_b, mu_o * mu_b
        u = [a[n] - c1 * a[n - 1] + c2 * a[n - 2] for n in range(2, len(a))]
        print(f"\n## after peeling mu and mu2: next correction's ratio")
        for k in (len(u) - 4, len(u) - 3, len(u) - 2, len(u) - 1):
            print(f"  n={k + 2:4d}  u(n)/u(n-1) = {nstr(u[k] / u[k - 1], 14)}"
                  f"   /mu = {nstr(u[k] / u[k - 1] / mu_o, 12)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
