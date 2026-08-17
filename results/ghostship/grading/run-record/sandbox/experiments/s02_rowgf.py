#!/usr/bin/env python3
"""Session 02: row GF numerators N_h(x).

Claim under test (extends s01's h<=5): for each fixed h, the row series
R_h(x) = sum_{w>=1} f(w,h) x^w is rational with denominator exactly
(1-x)^(2h-1), i.e. N_h(x) = (1-x)^(2h-1) R_h(x) is a POLYNOMIAL of degree
<= 2h-1. With 38 columns this is testable (with slack) for h <= ~18:
coefficients of x^(2h) .. x^37 of N_h must all vanish (the last coefficient
of a truncated product is contaminated, so we drop index 38... to be safe
we require zeros on 2h..36 and demand at least 5 zero checks).

Outputs the integer polynomials N_h, plus fingerprints:
  N_h(1)  = (2h-2)! * (leading coeff of the w-polynomial f(w,h))
  N_h(-1), N_h(0), coefficient rows for OEIS.
"""
from math import comb, factorial
from fractions import Fraction

def load_banked():
    tab = {}
    with open('out_convex_box_38.txt') as f:
        lines = f.read().splitlines()
    idx = lines.index('f(w,h) table (rows w=1..38, cols h=1..38):')
    for w, line in enumerate(lines[idx + 1:idx + 39], start=1):
        for h, v in enumerate(line.split(), start=1):
            tab[(w, h)] = int(v)
    return tab

def main():
    tab = load_banked()
    W = 38
    print('h : deg(N_h) : zero-checks : N_h coeffs (x^0..)')
    fingerprints = []
    for h in range(1, 19):
        series = [0] + [tab[(w, h)] for w in range(1, W + 1)]  # index = power of x
        m = 2 * h - 1
        # N = (1-x)^m * series, truncated at x^W; coefficients 0..W-? valid
        N = [0] * (W + 1)
        for k in range(W + 1):
            s = 0
            for j in range(0, min(m, k) + 1):
                s += (-1) ** j * comb(m, j) * series[k - j]
            N[k] = s
        # valid coefficients: k <= W (series known to w=38; product coeff k
        # needs series indices k-m..k, all <= W -> all k <= W valid).
        zeros_needed = range(2 * h, W + 1)
        nz = [k for k in zeros_needed if N[k] != 0]
        ok = (len(nz) == 0)
        ncoef = N[:2 * h]
        while ncoef and ncoef[-1] == 0:
            ncoef.pop()
        deg = len(ncoef) - 1
        n1 = sum(ncoef)
        nm1 = sum(c * (-1) ** i for i, c in enumerate(ncoef))
        lead = Fraction(n1, factorial(2 * h - 2))
        fingerprints.append((h, deg, n1, nm1, lead))
        print(f'h={h}: deg={deg} zerocheck={"OK" if ok else "FAIL at "+str(nz[:3])} '
              f'#zeros_verified={len(list(zeros_needed))}')
        print(f'   N_{h}(x) = {ncoef}')
    print()
    print('fingerprints:')
    print('h, deg N_h, N_h(1), N_h(-1), leading coeff of f(w,h) in w')
    for fp in fingerprints:
        print('  ', fp)
    print()
    print('N_h(1) sequence: ', [int(f[2]) for f in fingerprints])
    print('N_h(-1) sequence:', [int(f[3]) for f in fingerprints])

if __name__ == '__main__':
    main()
