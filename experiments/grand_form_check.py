#!/usr/bin/env python3
"""Machine checks for docs/proofs/grand-form.md (exact one-mode resummation).

From the Lean-verified aggregated cluster weights alone (V(l,j), Vt(l,j),
j <= 3 — polyplets/Polyplets/Weights.lean, Weights3.lean, Weights3Heavy.lean),
constructs every object in the proof and verifies, to y-order 3:

  1. Step 1: the (z*, u) induction — (z*-z)*u = 1-S exactly, deg u_j <= j,
     and 1 - S(y, z*) = 0 (z* is a root);
  2. Step 2: deg [y^k] u^(-1) <= k and deg [y^k] G <= k+1 for
     G = E_b * E_t * u^(-1);
  3. Step 3: T(H+k, H) = [y^k](C * mu^H) for every k <= 3 and every REAL
     banked point H = k+1 .. 19 (results/ns_a36/perheight, real sweeps only);
  4. Step 5: the production constants a_j, b_j computed ab initio through the
     diagonal Lagrange substitution reproduce the production polynomials
     P_1..P_3 of orchestrator/sweep.go diagCoeffTable coefficient-exactly,
     and b_1 = 25, a_1 = -45 (leading coefficient 25^k/k! mechanism).

All arithmetic exact (Fraction). Run: python3 experiments/grand_form_check.py
"""
import os
import re
import sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMAX = 3

# Aggregated weights V(l,j) (interior) and Vt(l,j) (edge), l rows, surplus j.
# Lean-verified values: V(1,1)=25, Vt(1,1)=5, V(1,2)=49, Vt(1,2)=7,
# V(2,2)=339, Vt(2,2)=66 (Weights.lean); V(1,3)=81, Vt(1,3)=9, V(2,3)=1860,
# Vt(2,3)=307 (Weights3.lean); V(3,3)=4778, Vt(3,3)=919 (Weights3Heavy).
V = {(1, 1): 25, (1, 2): 49, (2, 2): 339, (1, 3): 81, (2, 3): 1860,
     (3, 3): 4778}
VT = {(1, 1): 5, (1, 2): 7, (2, 2): 66, (1, 3): 9, (2, 3): 307, (3, 3): 919}


# ---- y-series with z-polynomial coefficients: list (y-order) of list (z) ----
def yz_zero():
    return [[F(0)] for _ in range(KMAX + 1)]


def polyadd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0))
            for i in range(n)]


def polymul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return r


def polydeg(a):
    d = -1
    for i, c in enumerate(a):
        if c != 0:
            d = i
    return d


def yzmul(A, B):
    R = yz_zero()
    for ka in range(KMAX + 1):
        for kb in range(KMAX + 1 - ka):
            R[ka + kb] = polyadd(R[ka + kb], polymul(A[ka], B[kb]))
    return R


# ---- scalar y-series (lists of Fraction) ----
def smul(a, b):
    r = [F(0)] * (KMAX + 1)
    for i in range(KMAX + 1):
        for j in range(KMAX + 1 - i):
            r[i + j] += a[i] * b[j]
    return r


def sinv(a):
    assert a[0] != 0
    r = [F(1) / a[0]] + [F(0)] * KMAX
    for k in range(1, KMAX + 1):
        r[k] = -sum(a[m] * r[k - m] for m in range(1, k + 1)) / a[0]
    return r


def spow(a, e):
    r = [F(1)] + [F(0)] * KMAX
    base, e_ = (a, e) if e >= 0 else (sinv(a), -e)
    for _ in range(e_):
        r = smul(r, base)
    return r


def slog1p(a):
    """log of a series with constant term 1."""
    assert a[0] == 1
    x = [F(0)] + a[1:]
    r = [F(0)] * (KMAX + 1)
    term = [F(1)] + [F(0)] * KMAX
    for m in range(1, KMAX + 1):
        term = smul(term, x)
        sign = F(-1) ** (m + 1)
        for i in range(KMAX + 1):
            r[i] += sign * term[i] / m
    return r


def sexp(a):
    assert a[0] == 0
    r = [F(1)] + [F(0)] * KMAX
    term = [F(1)] + [F(0)] * KMAX
    for m in range(1, KMAX + 1):
        term = smul(term, a)
        for i in range(KMAX + 1):
            r[i] += term[i] / __import__("math").factorial(m)
    return r


def seval_poly(p, s):
    """Evaluate z-polynomial p at a scalar y-series s."""
    r = [F(0)] * (KMAX + 1)
    for c in reversed(p):
        r = smul(r, s)
        r[0] += c
    return r


def main():
    fails = 0

    def check(name, ok):
        nonlocal fails
        print(f"  {name}: {'ok' if ok else '*** FAIL ***'}")
        if not ok:
            fails += 1

    # ---- build S, E_b, E_t per y-order ----
    S = yz_zero()
    S[0] = [F(0), F(3)]                                # 3z
    for (l, j), w in V.items():
        S[j] = polyadd(S[j], [F(0)] * (l + 1) + [F(w)])  # w * z^(l+1)
    Eb = yz_zero()
    Eb[0] = [F(0), F(1)]                               # z
    for (l, j), w in VT.items():
        Eb[j] = polyadd(Eb[j], [F(0)] * (l + 1) + [F(w)])  # z * w z^l
    Et = yz_zero()
    Et[0] = [F(1)]
    for (l, j), w in VT.items():
        Et[j] = polyadd(Et[j], [F(0)] * l + [F(w)])

    # ---- Step 1: (z*, u) induction ----
    zs = [F(1, 3)] + [F(0)] * KMAX                     # z* as scalar y-series
    u = yz_zero()
    u[0] = [F(3)]
    for j in range(1, KMAX + 1):
        Nj = [-c for c in S[j]]
        for m in range(1, j):
            Nj = polyadd(Nj, [-zs[m] * c for c in u[j - m]])
        val = sum(c * F(1, 3) ** i for i, c in enumerate(Nj))
        zs[j] = val / 3
        rhs = polyadd(Nj, [-3 * zs[j]])
        # exact division by (1/3 - z), fail-closed:
        # coeff of z^d in (1/3 - z)q is q_d/3 - q_(d-1)
        D = len(rhs) - 1
        q = [F(0)] * max(D, 1)
        carry = F(0)
        for d in range(D, 0, -1):
            q[d - 1] = carry / 3 - rhs[d]
            carry = q[d - 1]
        if rhs[0] - q[0] / 3 != 0:
            sys.exit(f"Step 1: division not exact at order {j}")
        u[j] = q
    check("Step1 deg u_j <= j", all(polydeg(u[j]) <= j
                                    for j in range(KMAX + 1)))
    # (z*-z)*u == 1-S
    zsz = yz_zero()
    for j in range(KMAX + 1):
        zsz[j] = [zs[j]] + ([-F(1)] if j == 0 else [])
    prod = yzmul(zsz, u)
    one_minus_S = [[F(1) - S[0][0], -S[0][1]]] + \
                  [[-c for c in S[j]] for j in range(1, KMAX + 1)]
    ok = all(polydeg(polyadd(prod[j], [-c for c in one_minus_S[j]])) == -1
             for j in range(KMAX + 1))
    check("Step1 (z*-z)u == 1-S", ok)
    # z* is a root: 1 - S(y, z*) == 0
    root = [F(1)] + [F(0)] * KMAX
    for j in range(KMAX + 1):
        contrib = seval_poly(S[j], zs)
        shifted = [F(0)] * j + contrib[:KMAX + 1 - j]
        root = [r - s for r, s in zip(root, shifted)]
    check("Step1 1-S(y,z*) == 0", all(c == 0 for c in root))

    # ---- Step 2: u^(-1) polynomial per order, degree bounds ----
    uinv = yz_zero()
    uinv[0] = [F(1, 3)]
    for j in range(1, KMAX + 1):
        acc = [F(0)]
        for m in range(1, j + 1):
            acc = polyadd(acc, polymul(u[m], uinv[j - m]))
        uinv[j] = [-c / 3 for c in acc]
    idcheck = yzmul(u, uinv)
    check("Step2 u*u^-1 == 1",
          polydeg(polyadd(idcheck[0], [-F(1)])) == -1 and
          all(polydeg(idcheck[j]) == -1 for j in range(1, KMAX + 1)))
    check("Step2 deg u^-1_k <= k", all(polydeg(uinv[j]) <= j
                                       for j in range(KMAX + 1)))
    G = yzmul(yzmul(Eb, Et), uinv)
    check("Step2 deg G_k <= k+1", all(polydeg(G[j]) <= j + 1
                                      for j in range(KMAX + 1)))

    # ---- Step 3: T(H+k,H) == [y^k](C mu^H) vs banked REAL cells ----
    mu = sinv(zs)
    Chat = [F(0)] * (KMAX + 1)
    maxdeg = max(len(G[j]) for j in range(KMAX + 1))
    for i in range(maxdeg):
        gi = [G[j][i] if i < len(G[j]) else F(0) for j in range(KMAX + 1)]
        Chat = [a + b for a, b in zip(Chat, smul(gi, spow(zs, i)))]
    C = smul(Chat, mu)
    real = {}
    for H in range(1, 20):
        with open(os.path.join(ROOT, f"results/ns_a36/perheight/h{H}.out")) as f:
            for line in f:
                p = line.split()
                if len(p) == 2:
                    real[(int(p[0]), H)] = int(p[1])
    npts, ok = 0, True
    for k in range(KMAX + 1):
        for H in range(k + 1, 20):
            mode = smul(C, spow(mu, H))[k]
            if mode != real[(H + k, H)]:
                ok = False
            npts += 1
    check(f"Step3 T(H+k,H) == [y^k](C mu^H), {npts} real points", ok)

    # ---- Step 5: production constants ab initio ----
    phi = sinv(mu)
    # w-hat solves w = y*phi(w): iterate to fixed point (converges y-adically)
    wh = [F(0)] * (KMAX + 1)
    for _ in range(KMAX + 2):
        # compose phi at w-hat (phi is a series in w)
        comp = [F(0)] * (KMAX + 1)
        power = [F(1)] + [F(0)] * KMAX
        for c in phi:
            comp = [a + c * b for a, b in zip(comp, power)]
            power = smul(power, wh)
        wh = [F(0)] + comp[:KMAX]                       # y * phi(w-hat)
    # compose a scalar series s(w) at w = wh
    def comp_at_wh(s):
        r = [F(0)] * (KMAX + 1)
        power = [F(1)] + [F(0)] * KMAX
        for c in s:
            r = [a + c * b for a, b in zip(r, power)]
            power = smul(power, wh)
        return r
    dphi = [F(i + 1) * phi[i + 1] for i in range(KMAX)] + [F(0)]
    denom = [F(1)] + [F(0)] * KMAX
    ydphi = [F(0)] + comp_at_wh(dphi)[:KMAX]
    denom = [a - b for a, b in zip(denom, ydphi)]
    Kser = smul(comp_at_wh(C), sinv(denom))
    Mser = comp_at_wh(mu)
    # substitute y -> 27y and normalize
    K27 = [Kser[i] * F(27) ** i for i in range(KMAX + 1)]
    M27 = [Mser[i] * F(27) ** i for i in range(KMAX + 1)]
    threeK = [3 * c for c in K27]
    Mover3 = [c / 3 for c in M27]
    check("Step5 3K(27y), M(27y)/3 have constant term 1",
          threeK[0] == 1 and Mover3[0] == 1)
    a = slog1p(threeK)
    b = slog1p(Mover3)
    check("Step5 b_1 == 25 and a_1 == -45", b[1] == 25 and a[1] == -45)

    # reconstruct P_k(n) = [y^k] exp(sum (a_j + b_j n) y^j), compare to
    # production diagCoeffTable at k+1 points (pins the degree-k polynomial)
    src = open(os.path.join(ROOT, "orchestrator/sweep.go")).read()
    tbl = {}
    for m in re.finditer(r'\n\t(\d+): \{\[\]string\{([^}]*)\}, (\d+)\}', src):
        k = int(m.group(1))
        tbl[k] = ([int(x) for x in re.findall(r'"(-?\d+)"', m.group(2))],
                  int(m.group(3)))
    ok = True
    for k in range(1, KMAX + 1):
        coeffs, kfact = tbl[k]
        for n in range(2 * k + 1, 2 * k + 2 + k + 1):
            cum = [F(0)] + [a[j] + b[j] * n for j in range(1, KMAX + 1)]
            theory = sexp(cum)[k]
            num = 0
            for c in coeffs:
                num = num * n + c
            if theory != F(num, kfact):
                ok = False
    check("Step5 ab-initio P_1..P_3 == production diagCoeffTable", ok)

    print()
    if fails:
        sys.exit(f"{fails} FAILURES")
    print("ALL CHECKS PASS")


if __name__ == "__main__":
    main()
