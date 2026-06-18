#!/usr/bin/env python3
"""Recover the rational generating function G_H(x) = sum_n B_H(n) x^n for the
fixed-height polyplet rows, by Berlekamp-Massey over Q on terms from the column
transfer matrix. Each row is C-finite, so the GF is rational and exact.

Usage:  python3 gf/recover.py [Hmax] [N]
  Hmax  highest strip height to do   (default 4)
  N     terms per height to gather   (default 36; B_H overflows u64 past ~n=50
        for H>=3, and exactly at n=32 for H=4 -- the wall the mod-p engine lifts)

Recovery is exact (fractions); a result is trustworthy only when the recurrence,
fit on a prefix, reproduces the held-out tail. Where N gives only ~2*order terms
(e.g. H=4) the fit is reported but flagged as not held-out-validated.
"""
import sys, subprocess, os
from fractions import Fraction as Fr
from math import gcd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMA = os.path.join(ROOT, "build", "tma")

def row(H, N):
    """B_H(0..N), truncated where exact u64 counts would overflow (the values
    wrap past 2^63, breaking monotonicity) so only correct terms are returned."""
    out = subprocess.run([TMA, "square8", str(N), "--only-height", str(H)],
                         capture_output=True, text=True).stdout
    d = {0: 0}
    for line in out.split("\n"):
        p = line.split()
        if len(p) == 2 and p[0].isdigit():
            d[int(p[0])] = int(p[1])
    s = [d[n] for n in range(N + 1)]
    onset = next((i for i, v in enumerate(s) if v), len(s))   # first nonzero
    safe = len(s)
    for i in range(onset + 1, len(s)):       # u64 wrap shows as a drop below the
        if s[i] < s[i - 1]:                  # predecessor (counts are increasing)
            safe = i; break
    return s[:safe]

def berlekamp_massey(seq):
    s = [Fr(x) for x in seq]
    C = [Fr(1)]; B = [Fr(1)]; L = 0; m = 1; b = Fr(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = C[:]; c = d / b
            while len(C) < len(B) + m: C.append(Fr(0))
            for i in range(len(B)): C[i + m] -= c * B[i]
            L = n + 1 - L; B = T; b = d; m = 1
        else:
            c = d / b
            while len(C) < len(B) + m: C.append(Fr(0))
            for i in range(len(B)): C[i + m] -= c * B[i]
            m += 1
    return C, L              # recurrence holds for n >= L (untrimmed; trailing
                             # zeros of C mean the denominator has lower degree)

def integerize_pair(P, Q):
    """Clear denominators and remove a common factor across BOTH polynomials at
    once, so the ratio P/Q is preserved."""
    coeffs = P + Q
    den = 1
    for c in coeffs: den = den * c.denominator // gcd(den, c.denominator)
    iP = [int(c * den) for c in P]; iQ = [int(c * den) for c in Q]
    g = 0
    for c in iP + iQ: g = gcd(g, c)
    g = g or 1
    return [c // g for c in iP], [c // g for c in iQ]

def poly(coeffs):
    out = []
    for i, c in enumerate(coeffs):
        if c == 0: continue
        mon = "" if i == 0 else ("x" if i == 1 else f"x^{i}")
        if mon == "": out.append(str(c))
        elif abs(c) == 1: out.append(("-" if c < 0 else "") + mon)
        else: out.append(f"{c}{mon}")
    return " + ".join(out).replace("+ -", "- ") or "0"

def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    N    = int(sys.argv[2]) if len(sys.argv) > 2 else 36
    for H in range(1, Hmax + 1):
        s = row(H, N)
        Cfull, Lfull = berlekamp_massey(s)
        hold = len(s) - Lfull >= Lfull + 2       # margin to hold terms out?
        fit = s[: len(s) - max(2, len(s) // 8)] if hold else s
        C, L = berlekamp_massey(fit)
        def rec(seq, k): return -sum(C[i] * Fr(seq[k - i]) for i in range(1, len(C)))
        validated = hold and all(rec(s, k) == s[k] for k in range(L, len(s)))
        if not validated:                        # fall back to the all-terms fit
            C, L = Cfull, Lfull
        order = max((i for i, c in enumerate(C) if c != 0), default=0)   # deg Q
        # numerator P = S*Q, a polynomial of degree <= len(C)-1
        Praw = [sum(C[i] * Fr(s[k - i]) for i in range(min(k, len(C) - 1) + 1))
                for k in range(len(C))]
        P, Q = integerize_pair(Praw, [Fr(c) for c in C])
        print(f"\n=== H={H}: order {order}  (2^{H}-1 = {2**H - 1})  "
              f"held-out-validated: {validated}  [{len(s)} exact terms] ===")
        print(f"  G_{H}(x) = ({poly(P)}) / ({poly(Q)})")
        print(f"  B_{H}(19) = {s[19] if len(s) > 19 else 'n/a'}")

if __name__ == "__main__":
    main()
