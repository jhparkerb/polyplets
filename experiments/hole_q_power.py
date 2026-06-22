#!/usr/bin/env python3
# Test the SHARP T2 mechanism: is the k-hole denominator Q_{H,k} literally Q_{H,0}^{k+1}?
# That (with a single q-pole G_H = A/(Q_0 - qB)) would make order(G_{H,k})=(k+1)d_H a
# theorem, not a fit. Parse the exact denominators from results/hole_gfs.txt and compare.
import re

# parse blocks: "H=h k=k ..." followed (within a few lines) by "Q: [ ... ]"
Q = {}
cur = None
for line in open("results/hole_gfs.txt"):
    m = re.match(r"H=(\d+) k=(\d+)\s+order=", line)
    if m:
        cur = (int(m.group(1)), int(m.group(2)))
    elif cur and line.strip().startswith("Q:"):
        coeffs = [int(c) for c in re.findall(r"-?\d+", line.split("Q:")[1])]
        Q[cur] = coeffs
        cur = None


def polymul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                r[i + j] += ai * bj
    return r


def polypow(a, e):
    r = [1]
    for _ in range(e):
        r = polymul(r, a)
    return r


# Test 1: is Q_{H,0}^{k+1} the denominator?  (refuted below — degrees don't even match)
# Test 2 (the real structure): for k>=1 are the denominators a GEOMETRIC progression
#   Q_{H,k} = const * R_H^k  (R_H deg m_H)?  <=>  Q_{H,k} * Q_{H,k+2} == Q_{H,k+1}^2.
# That would make order(G_{H,k})=(k+1)m_H structural (each hole multiplies by R_H).
print("Test: Q_{H,k}*Q_{H,k+2} == Q_{H,k+1}^2  (geometric denominators, k>=1)")
print(" H   k    holds?")
for h in sorted({h for (h, _k) in Q}):
    ks = sorted(k for (hh, k) in Q if hh == h and k >= 1)
    for k in ks:
        if (h, k) in Q and (h, k + 1) in Q and (h, k + 2) in Q:
            lhs = polymul(Q[(h, k)], Q[(h, k + 2)])
            rhs = polymul(Q[(h, k + 1)], Q[(h, k + 1)])
            print(f" {h}   {k}    {'YES' if lhs == rhs else 'NO'}")
