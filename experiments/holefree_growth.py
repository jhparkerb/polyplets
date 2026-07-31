#!/usr/bin/env python3
"""Hole-free growth constant lambda_0 vs lambda, from the exact hole distribution.

Usage: holefree_growth.py [TABLE]     (default results/holes_n18.txt)

Reads a "n holes count" table (tma_holes square8 --holes; banked exact n<=18).
Extracts A_k(n) (k holes) and a(n)=sum_k, estimates growth constants by
Domb-Sykes, Richardson, and a 3-parameter log-linear fit
(log f = logC + n logL + theta log n), and shows that the hole-free fraction
A0/a decays as a clean geometric (lambda_0/lambda)^n.

Result (n<=18): lambda~7.10, lambda_0~6.94, ratio 0.978 (pinned by the clean
exponential fraction decay); hole-free = simple-connectivity is ~2.2%/cell costly.
See results/hole-free-growth-constant.md.

Pass results/holes_n19.txt to include the n=19 term -- note that table is
TIER-DEGRADED (dirty binary stamp); see its header.
"""
import math
import sys
from collections import defaultdict

DEFAULT_SRC = "results/holes_n18.txt"


def load(src):
    tab = defaultdict(dict)
    for ln in open(src):
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        n, h, c = ln.split()
        tab[int(n)][int(h)] = int(c)
    return tab


def fit_logLinear(seq, ns, use=8):
    """log f = a + b n + c log n  ->  L=exp(b), theta=c, over the last `use` terms."""
    pts = [(n, seq[n]) for n in ns if seq[n] > 0][-use:]
    X = [[1.0, n, math.log(n)] for n, _ in pts]
    Y = [math.log(v) for _, v in pts]
    XtX = [[sum(X[k][i] * X[k][j] for k in range(len(X))) for j in range(3)] for i in range(3)]
    XtY = [sum(X[k][i] * Y[k] for k in range(len(X))) for i in range(3)]
    M = [row[:] + [XtY[i]] for i, row in enumerate(XtX)]      # Gauss-Jordan 3x3
    for i in range(3):
        p = M[i][i]
        for j in range(i, 4):
            M[i][j] /= p
        for k in range(3):
            if k != i:
                f = M[k][i]
                for j in range(i, 4):
                    M[k][j] -= f * M[i][j]
    logC, logL, theta = M[0][3], M[1][3], M[2][3]
    return math.exp(logL), theta


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    print(f"source: {src}")
    tab = load(src)
    ns = sorted(tab)
    tot = {n: sum(tab[n].values()) for n in ns}
    A = {k: {n: tab[n].get(k, 0) for n in ns} for k in range(4)}

    print(f"{'n':>3} {'a(n)':>16} {'A0':>16} {'A0/a':>7} {'a ratio':>8} {'A0 ratio':>8}")
    for n in ns:
        ar = tot[n] / tot[n - 1] if n - 1 in tot else 0
        a0r = A[0][n] / A[0][n - 1] if n - 1 in A[0] and A[0][n - 1] else 0
        print(f"{n:>3} {tot[n]:>16} {A[0][n]:>16} {A[0][n]/tot[n]:>7.4f} {ar:>8.4f} {a0r:>8.4f}")

    la, tha = fit_logLinear(tot, ns)
    l0, th0 = fit_logLinear(A[0], ns)
    print(f"\nlambda   = {la:.4f}  theta = {tha:+.2f}")
    print(f"lambda_0 = {l0:.4f}  theta = {th0:+.2f}   gap = {la-l0:.4f}   ratio = {l0/la:.5f}")

    top, prev = ns[-1], ns[-2]
    decay = (A[0][top] / tot[top]) / (A[0][prev] / tot[prev])
    print(f"\nfraction A0/a per-cell decay (n={prev}->{top}): {decay:.5f}"
          f"  vs lambda_0/lambda = {l0/la:.5f}")
    print("log(A0/a) second differences (flat => pure exponential):")
    lg = [(n, math.log(A[0][n] / tot[n])) for n in ns]
    for i in range(2, len(lg)):
        n = lg[i][0]
        d2 = lg[i][1] - 2 * lg[i - 1][1] + lg[i - 2][1]
        if n >= 13:
            print(f"  n={n:2d}  d2={d2:+.6f}")


if __name__ == "__main__":
    main()
