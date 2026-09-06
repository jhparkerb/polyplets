#!/usr/bin/env python3
"""5-adic structure of the grand-form constants (v5 denominator problem).

Open question (results/closed-doors.md #2): D_k = k!/5^{c_k} is the minimal
common denominator of P_k; measured c_k = 0 (k<=4), 1 (k=5..10,12..14),
2 (k=11, 15..18).  Conjectured law c_k = ceil(v5(k!)/2), exception k=11.

This probe extracts the exact grand-form constants a_j, b_j (j <= 18) from
the production polynomials (polyplets/pin-data.md, generated independently of
this script) via the exp recurrence

    k P_k = sum_{j=1}^{k} j (a_j + b_j n) P_{k-j},   c_k = P_k - known_k,

and tabulates the 5-adic valuations of everything in sight: a_j, b_j,
j!a_j, j!b_j, the k!-basis numerator coefficients of P_k, and the boundary
series G(y) = exp(sum a_j y^j) = sum P_k(0) y^k and its n-companion
Lambda(y) = exp(sum b_j y^j).

Cost: <2 s, pure Fraction arithmetic on pinned data.  No enumeration.
Usage: python3 experiments/v5_denominator.py
"""
import os
import re
import sys
from fractions import Fraction as F
from math import factorial

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def v5(x):
    """5-adic valuation of a nonzero int or Fraction; None for 0."""
    if x == 0:
        return None
    if isinstance(x, F):
        return v5(x.numerator) - v5(x.denominator)
    x = abs(x)
    v = 0
    while x % 5 == 0:
        x //= 5
        v += 1
    return v


def load_pk():
    """P_k coefficient lists (ascending in n, Fractions) from pin-data.md."""
    P, k = {}, None
    for line in open(os.path.join(ROOT, "polyplets/pin-data.md")):
        m = re.match(r"## k=(\d+)", line)
        if m:
            k = int(m.group(1))
            continue
        m = re.match(r"numerator \(desc n\): \[([-0-9, ]+)\]", line)
        if m and k is not None:
            desc = [int(t) for t in m.group(1).split(",")]
            kf = factorial(k)
            P[k] = [F(c, kf) for c in reversed(desc)]
    P[0] = [F(1)]
    return P


def padd(a, b):
    n = max(len(a), len(b))
    a = a + [F(0)] * (n - len(a))
    b = b + [F(0)] * (n - len(b))
    return [x + y for x, y in zip(a, b)]


def pmul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i + j] += x * y
    return r


def pscale(a, s):
    return [x * s for x in a]


def main():
    P = load_pk()
    kmax = max(P)
    print(f"loaded P_0..P_{kmax} from pin-data.md")

    # extract c_j = a_j + b_j n via  c_k = P_k - (1/k) sum_{j<k} j c_j P_{k-j}
    c = {}
    for k in range(1, kmax + 1):
        known = [F(0)]
        for j in range(1, k):
            known = padd(known, pscale(pmul(c[j], P[k - j]), F(j)))
        known = pscale(known, F(1, k))
        ck = padd(P[k], pscale(known, F(-1)))
        assert all(x == 0 for x in ck[2:]), f"c_{k} not linear"
        c[k] = ck[:2]

    print("\n== grand-form constants: v5 profile ==")
    print(f"{'j':>2} {'v5(a_j)':>8} {'v5(b_j)':>8} {'v5(j!a_j)':>10} "
          f"{'v5(j!b_j)':>10} {'v5(j!)':>7}  a_j, b_j (den 5-part shown)")
    for j in range(1, kmax + 1):
        aj, bj = c[j]
        jf = factorial(j)
        print(f"{j:>2} {str(v5(aj)):>8} {str(v5(bj)):>8} "
              f"{str(v5(jf*aj)):>10} {str(v5(jf*bj)):>10} {v5(jf):>7}  "
              f"den5(a)={5**max(0,-(v5(aj) or 0))} "
              f"den5(b)={5**max(0,-(v5(bj) or 0))}")

    print("\n== per-k coefficient v5 profile of k!*P_k (asc n), min = c_k ==")
    print(f"{'k':>2} {'v5(k!)':>6} {'c_k':>4} {'ceil/2':>6}  profile")
    for k in range(1, kmax + 1):
        kf = factorial(k)
        prof = [v5(kf * x) for x in P[k]]
        ck = min(p for p in prof if p is not None)
        law = -(-v5(kf) // 2)
        mark = "" if ck == law else "  <-- EXCEPTION"
        print(f"{k:>2} {v5(kf):>6} {ck:>4} {law:>6}  {prof}{mark}")

    # G and Lambda series
    print("\n== G(y)=sum P_k(0) y^k and Lambda(y)=exp(sum b_j y^j): v5 ==")
    ga = [F(1)]  # exp(sum a_j y^j)
    gb = [F(1)]
    for k in range(1, kmax + 1):
        # [y^k] exp: use recurrence k g_k = sum j t_j g_{k-j}
        sa = sum(F(j) * c[j][0] * ga[k - j] for j in range(1, k + 1))
        sb = sum(F(j) * c[j][1] * gb[k - j] for j in range(1, k + 1))
        ga.append(sa / k)
        gb.append(sb / k)
    print(f"{'k':>2} {'v5(g_k)':>8} {'v5(k!g_k)':>10} {'v5(L_k)':>8} "
          f"{'v5(k!L_k)':>10}")
    for k in range(kmax + 1):
        kf = factorial(k)
        print(f"{k:>2} {str(v5(ga[k])):>8} {str(v5(kf*ga[k])):>10} "
              f"{str(v5(gb[k])):>8} {str(v5(kf*gb[k])):>10}")
    # sanity: g_k must equal P_k(0)
    for k in range(kmax + 1):
        assert ga[k] == P[k][0], f"G mismatch at k={k}"
    print("sanity: g_k == P_k(0) for all k -- ok")

    # ---- the theorem inputs, checked exactly ----
    # G = sum P_k(0) y^k and Lambda = exp(sum b_j y^j) are INTEGER series
    # (G by Step 6 integer values; Lambda = (sum P_k(1) y^k)/G, G(0)=1),
    # with the two taxed order-1 coefficients u_1 = 25, g_1 = -45.
    print("\n== theorem inputs ==")
    assert all(x.denominator == 1 for x in ga), "G not integral"
    assert all(x.denominator == 1 for x in gb), "Lambda not integral"
    u = gb[:]  # u = Lambda - 1
    u[0] = F(0)
    assert u[1] == 25 and ga[1] == -45
    print("G, Lambda integer series; u_1 = 25, g_1 = -45 -- ok")

    # ---- the law:  min_j v5([n^j] k! P_k) = v5(k!) - H(k) ----
    def Hval(k):
        """H(k) = max over {j_G + sum_t t*m_t = k, m_1 = 0 wlog} of
        sum_t v5(m_t!) - [j_G == 1].  The all-2s/leftover case-split
        collapses (jasonp's observation, 2026-07-31) to the one-liner
        v5(floor(k/2)!) - [k = 1 mod 10]: for odd k the max form
        max(v5((m-1)!), v5(m!)-1) = v5(m!) - min(v5(m), 1) and
        5 | floor(k/2) iff k = 1 (mod 10); k = 0, 1 absorb too."""
        return v5(factorial(k // 2)) - (1 if k % 10 == 1 else 0)

    def Hbrute(k):
        """Direct max over all partitions j_G + sum t*m_t = k (t >= 1),
        payoff sum_t v5(m_t!) - 2*m_1 - [j_G == 1]."""
        best = [-10**9]

        def rec(rem, t, acc):
            for jg in ([rem] if t > rem else []):
                pass
            best[0] = max(best[0], acc - (1 if rem == 1 else 0))
            for tt in range(t, rem + 1):
                for m in range(1, rem // tt + 1):
                    tax = 2 * m if tt == 1 else 0
                    rec(rem - tt * m, tt + 1,
                        acc + v5(factorial(m)) - tax)
        rec(k, 1, 0)
        return best[0]

    def oddprod_v5(k):
        """v5 of the odd double factorial <= k; c-hat_k = this + [k=1 mod 10]
        (k! = 2^floor(k/2) * floor(k/2)! * oddprod)."""
        return sum(v5(j) for j in range(1, k + 1, 2))

    print("\n== law check: c-hat_k = v5(k!) - H(k) ==")
    ok = True
    for k in range(1, kmax + 1):
        kf = factorial(k)
        chat = min(p for p in (v5(kf * x) for x in P[k]) if p is not None)
        h, hb = Hval(k), Hbrute(k)
        assert h == hb, f"H closed form mismatch at k={k}: {h} vs {hb}"
        assert v5(kf) - h == oddprod_v5(k) + (1 if k % 10 == 1 else 0), \
            f"odd-double-factorial form mismatch at k={k}"
        law = v5(kf) - h
        tag = "ok" if chat == law else "*** MISMATCH ***"
        if chat != law:
            ok = False
        old = -(-v5(kf) // 2)
        note = "" if law == old else f"  (old ceil-fit said {old})"
        print(f"  k={k:2d}: c-hat={chat} v5(k!)-H = {v5(kf)}-{h} = {law}"
              f"  {tag}{note}")
    print(f"law {'HOLDS' if ok else 'FAILS'} at every measured level")

    print("\n== profile structure (second pass, 2026-07-31) ==")
    # (a) upper half exact: v5([n^i] k! P_k) = 2(2i-k) + v5(k!/((2i-k)!(k-i)!))
    #     for every i >= ceil(k/2) -- the "ramp" is pure multinomial arithmetic
    # (b) i = 0 column exact: v5 = v5(k!) + v5(g_k)  (single term k!*g_k)
    ramp_bad, col0_bad = [], []
    for k in range(1, kmax + 1):
        kf = factorial(k)
        prof = [v5(kf * x) for x in P[k]]
        for i in range((k + 1) // 2, k + 1):
            m1, m2 = 2 * i - k, k - i
            want = 2 * m1 + v5(kf // (factorial(m1) * factorial(m2)))
            if prof[i] != want:
                ramp_bad.append((k, i))
        if prof[0] != v5(kf) + v5(ga[k]):
            col0_bad.append(k)
    assert not ramp_bad, f"upper-half law fails at {ramp_bad}"
    assert not col0_bad, f"i=0 column law fails at {col0_bad}"
    print("upper-half law (i >= ceil(k/2)) and i=0 column law: EXACT at "
          f"every coefficient, k <= {kmax}")

    print("\n== predictions (assume attainment; H from proved bounds) ==")
    for k in range(19, 27):
        kf = factorial(k)
        law = v5(kf) - Hval(k)
        old = -(-v5(kf) // 2)
        d = "" if law == old else "  <-- diverges from ceil(v5(k!)/2)"
        print(f"  k={k}: predicted c-hat = {v5(kf)} - {Hval(k)} = {law}{d}")


def check_k19():
    """Out-of-sample test: derive P_19 from real-swept cells (two-point pin,
    grand form) and test the law at k = 19 -- no k=19 data touched the law."""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import derive_pk_fast as dpf
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        P, _ = dpf.derive(19)
    pinned = load_pk()
    for k in range(1, 19):
        assert P[k] == pinned[k], f"derive vs pin-data mismatch at k={k}"
    kf = factorial(19)
    prof = [v5(kf * x) for x in P[19]]
    chat = min(p for p in prof if p is not None)
    print("\n== k=19 out-of-sample test (derived from real-swept cells; "
          "P_1..P_18 agree with pin-data) ==")
    print(f"  profile v5(19! P_19): {prof}")
    print(f"  c-hat_19 = {chat}; law predicts v5(19!) - H(19) = 3 - 1 = 2: "
          f"{'CONFIRMED' if chat == 2 else '*** REFUTED ***'}")


if __name__ == "__main__":
    main()
    check_k19()
