#!/usr/bin/env python3
"""s10 VERIFY of s09 claim 3 (Delta | B_1), by a STRONGER method:
exact multivariate polynomial long division over Q, not point-vanishing.

Input: banked bivariate first-moment closed forms M1 = (A + B*sqrt(Delta))
/(K^2 Delta^4) [king] resp. /(Delta^4) [control], A,B stored in
out_s07_bivar_moment.json (king) and out_s07_bivar_moment_poly.json
(control) as {"i,j": coeff} with ONLY the i<=j representative of each
symmetric monomial pair stored (s08 CARRY note) -- symmetrized here.

Divide B by Delta = (1-x-y)^2 - 4xy = 1 - 2x - 2y + x^2 - 2xy + y^2
exactly (lex-leading-term division; Delta is monic in x^2 so division
terminates and remainder has x-degree <= 1). Claim confirmed iff
remainder == 0 for both modes. Also re-checks A is NOT divisible
(divisibility is special to B). Output: out_s10_verify_B1_div.txt
"""
import json
from fractions import Fraction as Fr

def load(path):
    d = json.load(open(path))
    out = {}
    for key, poly in d.items():
        P = {}
        for k, c in poly.items():
            i, j = map(int, k.split(','))
            P[(i, j)] = P.get((i, j), 0) + Fr(c)
            if i != j:
                P[(j, i)] = P.get((j, i), 0) + Fr(c)
        out[key] = {k: c for k, c in P.items() if c}
    return out

DELTA = {(0,0): Fr(1), (1,0): Fr(-2), (0,1): Fr(-2),
         (2,0): Fr(1), (1,1): Fr(-2), (0,2): Fr(1)}

def divide(P, D):
    """exact division of P by D, leading term of D = x^2 (lex x>y).
    Returns (quotient, remainder)."""
    P = dict(P); Q = {}
    while True:
        # find a term with x-degree >= 2 (divisible by lead x^2), max lex
        cand = [k for k, c in P.items() if c and k[0] >= 2]
        if not cand:
            break
        i, j = max(cand)
        c = P[(i, j)]
        qk = (i-2, j)
        Q[qk] = Q.get(qk, Fr(0)) + c
        for (a, b), dc in DELTA.items():
            k2 = (qk[0]+a, qk[1]+b)
            P[k2] = P.get(k2, Fr(0)) - c*dc
            if P[k2] == 0:
                del P[k2]
    R = {k: c for k, c in P.items() if c}
    return Q, R

lines = []
allok = True
for tag, path in (("king", "out_s07_bivar_moment.json"),
                  ("control", "out_s07_bivar_moment_poly.json")):
    d = load(path)
    A, B = d["A"], d["B"]
    QB, RB = divide(B, DELTA)
    QA, RA = divide(A, DELTA)
    okB = (len(RB) == 0)
    okA = (len(RA) != 0)
    allok &= okB
    lines.append(f"{tag}: B_1 has {len(B)} monomials (symmetrized), "
                 f"max deg {max(i+j for i,j in B)}")
    lines.append(f"{tag}: Delta | B_1 by EXACT long division: "
                 f"{'CONFIRMED (remainder 0)' if okB else 'FAILED'}; "
                 f"quotient has {len(QB)} monomials")
    lines.append(f"{tag}: control check Delta | A_1? "
                 f"{'no (remainder nonzero, as expected)' if okA else 'YES?! unexpected'}")
    if okB:
        # print the quotient B_1/Delta explicitly (new bankable object)
        qs = sorted(QB.items())
        lines.append(f"{tag}: B_1/Delta = " + " + ".join(
            f"({c})x^{i}y^{j}" for (i, j), c in qs))
print("\n".join(lines))
print("VERDICT:", "s09 claim 3 (Delta | B_1) CONFIRMED by exact division, both modes"
      if allok else "REFUTED")
with open("out_s10_verify_B1_div.txt", "w") as f:
    f.write("\n".join(lines) + "\n")
    f.write("VERDICT: " + ("s09 claim 3 (Delta | B_1) CONFIRMED by exact division, "
            "both modes" if allok else "REFUTED") + "\n")
