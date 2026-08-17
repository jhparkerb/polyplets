#!/usr/bin/env python3
"""Session 12: factor-structure probe of the extracted B_r quotients
(out_s12_bivar_Br.json).  s10's conjectured king shape B_r =
Delta*x^2y^2*(1+x+y)*C_r was REFUTED at r=3 by the main run; here we ask
what DOES divide the quotients Q_r := B_r/(Delta*x^2y^2), king and poly,
r = 2,3 (r=1 anchors: king Q_1 = (1+x+y)*C_1, poly Q_1 = 4(1-x+y)(1+x-y)).

Candidate atoms (all seen in the s02/s10 factor zoo): 1+x+y, 1-x+y, 1+x-y,
1-x-y, K = x+y+xy, Delta itself (multiplicity 2?), x+y, 1-x, 1-y, C_1.
Also: symmetry check Q(x,y)==Q(y,x), content, evaluation on the curve
Delta=0 at (a^2,(1-a)^2) for rational a (does Q vanish on the curve?).

Usage: python3 experiments/s12_factor_probe.py
Output: out_s12_factor_probe.txt
"""
import json, os, sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_bivar_Br as BR

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def parsepoly(dct):
    out = {}
    for k, c in dct.items():
        i, j = map(int, k.split(","))
        out[(i, j)] = int(c)
    return out


ATOMS = {
    "1+x+y": {(0, 0): 1, (1, 0): 1, (0, 1): 1},
    "1-x+y": {(0, 0): 1, (1, 0): -1, (0, 1): 1},
    "1+x-y": {(0, 0): 1, (1, 0): 1, (0, 1): -1},
    "1-x-y": {(0, 0): 1, (1, 0): -1, (0, 1): -1},
    "K=x+y+xy": {(1, 0): 1, (0, 1): 1, (1, 1): 1},
    "Delta": {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (0, 2): 1,
              (1, 1): -2},
    "x+y": {(1, 0): 1, (0, 1): 1},
    "1-x": {(0, 0): 1, (1, 0): -1},
    # C_1 (s10, u=x+y, v=xy): 4u-4u^2+3v+2uv-u^2v+8v^2
    "C1": {(1, 0): 4, (0, 1): 4, (2, 0): -4, (0, 2): -4, (1, 1): -8 + 3,
           (2, 1): 2, (1, 2): 2, (3, 1): -1, (1, 3): -1,
           (2, 2): -2 + 8},
}
# C1 expansion check: u^2 = x^2+2xy+y^2; uv = x^2y+xy^2; u^2 v =
# x^3y+2x^2y^2+xy^3; v^2 = x^2y^2 =>
# 4x+4y -4x^2-8xy-4y^2 +3xy +2x^2y+2xy^2 -x^3y-2x^2y^2-xy^3 +8x^2y^2


def peval(p, xv, yv):
    return sum(c * xv ** i * yv ** j for (i, j), c in p.items())


def gdivide(Pd, D):
    """general exact multivariate division P/D over Q, lex order x>y.
    Returns (Q, R) with R the remainder of top-reduction (R=={} iff D|P
    when reduction only ever needs the lead term -- standard division
    algorithm with a single divisor)."""
    lead = max(k for k, c in D.items() if c)
    lc = Fr(D[lead])
    Pw = {k: Fr(c) for k, c in Pd.items() if c}
    Q, R = {}, {}
    while Pw:
        k = max(Pw)
        c = Pw.pop(k)
        if k[0] >= lead[0] and k[1] >= lead[1]:
            qk = (k[0] - lead[0], k[1] - lead[1])
            f = c / lc
            Q[qk] = Q.get(qk, Fr(0)) + f
            for (a, b), dc in D.items():
                if (a, b) == lead or not dc:
                    continue
                k2 = (qk[0] + a, qk[1] + b)
                v = Pw.get(k2, Fr(0)) - f * dc
                if v:
                    Pw[k2] = v
                elif k2 in Pw:
                    del Pw[k2]
        else:
            R[k] = c
    return Q, R


def probe(tag, Q):
    say(f"-- {tag}: {len(Q)} monomials, deg {max(i+j for i,j in Q)}, "
        f"symmetric: {all(Q.get((j,i),0)==c for (i,j),c in Q.items())}")
    from math import gcd
    g = 0
    for c in Q.values():
        g = gcd(g, abs(c))
    say(f"   content = {g}")
    core = {k: Fr(c) for k, c in Q.items()}
    facs = []
    changed = True
    while changed:
        changed = False
        for name, atom in ATOMS.items():
            q, rem = gdivide(core, atom)
            if not rem and q:
                facs.append(name)
                core = q
                changed = True
    say(f"   atom factorization: {' * '.join(facs) if facs else '(none)'}"
        f" * CORE[{len(core)} monomials, deg "
        f"{max(i+j for i, j in core) if core else 0}]")
    corev = []
    for anum, aden in ((1, 2), (1, 3), (2, 5)):
        a = Fr(anum, aden)
        corev.append(peval(core, a * a, (1 - a) ** 2) == 0)
    say(f"   core vanishes on curve: {corev}")
    # curve evaluation at 6 rational points a
    vals = []
    for anum, aden in ((1, 2), (1, 3), (2, 5), (1, 4), (3, 7), (2, 7)):
        a = Fr(anum, aden)
        v = peval(Q, a * a, (1 - a) ** 2)
        vals.append((f"a={a}", v == 0))
    say(f"   vanishes on curve Delta=0: {vals}")


def main():
    d = json.load(open(os.path.join(ROOT, "out_s12_bivar_Br.json")))
    for key in ("king_r1", "king_r3", "poly_r1", "poly_r2", "poly_r3"):
        rec = d[key]
        Q = parsepoly(rec["quotient"])
        say(f"{key}: quotient_tag = {rec['quotient_tag']}")
        probe(key, Q)
    with open(os.path.join(ROOT, "out_s12_factor_probe.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipt: out_s12_factor_probe.txt")


if __name__ == "__main__":
    main()
