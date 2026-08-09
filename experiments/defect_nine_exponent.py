#!/usr/bin/env python3
"""Pin the below-onset defect law:  D_j(k) = T - law ~ C_j * 9^k * k^(theta_j).

Hypothesis from experiments/onset_defect_nine.py: the exponential rate is
exactly 9 = 3^2 at every depth j below the onset, and theta_j = j - 3/2.

Method, deliberately not a curve fit: if D = C 9^k k^theta then
   L_k := k*(D_k/D_{k-1}/9 - 1) -> theta   with an O(1/k) error,
so a Richardson step in 1/k on L_k gives theta with the leading correction
removed.  A control runs the same estimator on an EXACTLY constructed
C * 9^k * k^theta sequence to show what the estimator's own error is at k<=19.
"""
import math, os, sys
from fractions import Fraction as F
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from slope2_law_vs_truth import read_pk, read_tri, law

P, tri = read_pk(), read_tri()

def est(seq):
    """seq: list of (k, value). returns (raw L at last k, Richardson theta)."""
    L = []
    for i in range(1, len(seq)):
        k, v = seq[i]; k0, v0 = seq[i-1]
        L.append((k, k * (v / v0 / 9.0 - 1.0)))
    if len(L) < 2: return None, None
    (k1, l1), (k2, l2) = L[-2], L[-1]
    return l2, (k2*l2 - k1*l1) / (k2 - k1)

print("== control: exact C * 9^k * k^theta, k=2..19, same estimator")
print("  %8s %10s %10s" % ("true", "raw L(19)", "Richardson"))
for th in (-1.5, -0.5, 0.5, 1.5, 2.5):
    seq = [(k, 9.0**k * k**th) for k in range(2, 20)]
    raw, rich = est(seq)
    print("  %8.2f %10.4f %10.4f" % (th, raw, rich))

print()
print("== measured, depth j below onset (n = 2k+1-j)")
print("  %3s %6s %10s %12s %14s" % ("j", "pts", "raw L", "Richardson", "j - 3/2"))
for j in range(1, 9):
    seq = []
    for k in range(2, 20):
        n = 2*k+1-j; H = n-k
        if H < 1 or (n,H) not in tri or k not in P: continue
        D = F(tri[(n,H)]) - law(n,k,P)
        if D <= 0: continue
        seq.append((k, float(D)))
    if len(seq) < 4: continue
    raw, rich = est(seq)
    print("  %3d %6d %10.4f %12.4f %14.1f" % (j, len(seq), raw, rich, j-1.5))

print()
print("== CONTROL for the rate estimator: exactly-built sequences, known rate")
print("   A clean C r^k k^th is recovered exactly, which proves nothing; the")
print("   informative control multiplies it by a non-terminating 1/k series,")
print("   which is what a real asymptotic sequence has.")
print("  %8s %8s %14s %14s" % ("true r", "corr", "r at k=19", "Richardson r"))


def rate_of(seq, th):
    R = [(k, (v/v0) * (k0/float(k))**th)
         for (k0, v0), (k, v) in zip(seq, seq[1:])]
    (k1, r1), (k2, r2) = R[-2], R[-1]
    return r2, (k2*r2 - k1*r1) / (k2 - k1)


for r_true in (9.0, 8.9, 8.95, 9.1):
    for cname, cf in (("none", lambda k: 1.0),
                      ("1/k", lambda k: (1+0.7/k)/(1-0.3/k))):
        seq = [(k, r_true**k * k**-0.5 * cf(k)) for k in range(2, 20)]
        raw, rich = rate_of(seq, -0.5)
        print("  %8.2f %8s %14.6f %14.6f" % (r_true, cname, raw, rich))
print("   -> one Richardson step leaves an O(0.03) bias when a realistic 1/k")
print("      correction is present, so the column below resolves the rate to")
print("      about +-0.03, not to 4 decimals.  A rate of 8.95 vs 9 IS")
print("      separable; 8.99 vs 9.00 is not.  Higher-order Richardson on the")
print("      same r_k sequence tightens this: experiments/defect_controls.py.")

print()
print("== is the rate exactly 9?  fit D ~ C * r^k * k^(j-3/2), solve for r")
print("  %3s %14s %14s" % ("j", "r at k=19", "Richardson r"))
for j in range(1, 7):
    seq = []
    for k in range(2, 20):
        n = 2*k+1-j; H = n-k
        if H < 1 or (n,H) not in tri or k not in P: continue
        D = F(tri[(n,H)]) - law(n,k,P)
        if D <= 0: continue
        seq.append((k, float(D)))
    if len(seq) < 4: continue
    th = j - 1.5
    R = [(k, (v/v0) * (k0/float(k))**th)
         for (k0,v0),(k,v) in zip(seq, seq[1:])]
    (k1,r1),(k2,r2) = R[-2], R[-1]
    print("  %3d %14.6f %14.6f" % (j, r2, (k2*r2-k1*r1)/(k2-k1)))
