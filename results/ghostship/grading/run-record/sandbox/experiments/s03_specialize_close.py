#!/usr/bin/env python3
"""Session 03: close the kernel-derivation identity on the FULL sufficient
degree box via per-x specializations (recipe of docs/proofs/convex-box-kernel.md
section 7).

Target identity:   2*K*Delta^2*F_derived + M + S*sqrt(Delta) = 0
with K = x+y+xy, Delta = (1-x-y)^2-4xy, S = 2x^2y^2(1+x+y)^2, M = A1/Delta^2
(A_i from s02's holdout-validated equation JSON).

Degree bounds (s03_degree_bounds.py): the identity's numerator components
P, Q (rational and radical part) have deg_x <= 79, deg_u <= 119 (u = sqrt(y)).

Closure logic:
 - Part A (exact, over Z): verify A2 == Delta^4*K, A1 == Delta^2*M (exact
   division, zero remainder), 4*K*A0 == M^2 - Delta*S^2, and
   A1^2 - 4*A2*A0 == Delta^5*S^2, as integer polynomial identities.  These
   also imply (pure algebra, see proof doc) that -(M+S*sqrt(Delta))/(2K
   Delta^2) satisfies s02's quadratic.
 - Part B (mod two primes): for each c in {2,...,85} (84 > 79+1 distinct
   values, all != 0,1), run the whole kernel pipeline specialized at x=c
   (univariate series in u, degree <= 242+margin) and check the identity
   vanishes to u-degree 242 = 2*119+4.  Per c, Delta(c,u^2) has 4 distinct
   roots (disc_y = 16c != 0, (1-c)^2 != 0), so it is not a square and
   T1_c == 0 up to u-deg 242 forces P(c,.) = Q(c,.) = 0 (valuation argument).
   84 values then force P = Q = 0 (mod p) since deg_x <= 79.
Result: the identity holds as a polynomial identity modulo both primes
(jointly ~2^121); everything else in the chain is exact/proved.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s03_kernel_solve as ks

MARGIN = 8
NU = 242 + MARGIN


# ---------- Part A: exact integer bivariate polynomial identities ----------
def pmul(a, b):
    r = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m = (m1[0] + m2[0], m1[1] + m2[1])
            r[m] = r.get(m, 0) + c1 * c2
    return {m: c for m, c in r.items() if c}


def padd(a, b):
    r = dict(a)
    for m, c in b.items():
        r[m] = r.get(m, 0) + c
        if r[m] == 0:
            del r[m]
    return r


def pscal(a, k):
    return {m: c * k for m, c in a.items()}


def ppow(a, n):
    r = {(0, 0): 1}
    for _ in range(n):
        r = pmul(r, a)
    return r


def pdivexact(a, b):
    """Exact division in Z[x,y], lex order, leading coeff of b must be +-1."""
    a = dict(a)
    q = {}
    lb = max(b)  # lex-max monomial
    cb = b[lb]
    assert cb in (1, -1)
    while a:
        la = max(a)
        if la[0] < lb[0] or la[1] < lb[1]:
            raise AssertionError(f"not divisible, remainder lead {la}")
        m = (la[0] - lb[0], la[1] - lb[1])
        coef = a[la] // cb
        assert coef * cb == a[la]
        q[m] = q.get(m, 0) + coef
        sub = {(m[0] + mb[0], m[1] + mb[1]): -coef * cb2
               for mb, cb2 in b.items()}
        a = padd(a, sub)
    return q


DELTA = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (1, 1): -2, (2, 0): 1, (0, 2): 1}
K = {(1, 0): 1, (0, 1): 1, (1, 1): 1}
ONEXY = {(0, 0): 1, (1, 0): 1, (0, 1): 1}
S = pscal(pmul({(2, 2): 1}, pmul(ONEXY, ONEXY)), 2)


def part_a():
    eq = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                                     "out_s02_bivar_eq_king_D2.json")))
    A = []
    for k in "012":
        A.append({tuple(map(int, m.split(","))): c for m, c in eq[k].items()})
    A0, A1, A2 = A
    D2 = ppow(DELTA, 2)
    D4 = pmul(D2, D2)
    ok1 = padd(A2, pscal(pmul(D4, K), -1)) == {}
    M = pdivexact(A1, D2)
    ok2 = padd(A1, pscal(pmul(D2, M), -1)) == {}
    lhs3 = pscal(pmul(K, A0), 4)
    rhs3 = padd(pmul(M, M), pscal(pmul(DELTA, pmul(S, S)), -1))
    ok3 = padd(lhs3, pscal(rhs3, -1)) == {}
    lhs4 = padd(pmul(A1, A1), pscal(pmul(A2, A0), -4))
    rhs4 = pmul(ppow(DELTA, 5), pmul(S, S))
    ok4 = padd(lhs4, pscal(rhs4, -1)) == {}
    # cross-check -M(t,t) = 2t^3(2-10t+14t^2-5t^3-4t^4)
    mt = {}
    for (i, j), c in M.items():
        mt[i + j] = mt.get(i + j, 0) + c
    mt = {d: c for d, c in mt.items() if c}
    ok5 = mt == {3: -4, 4: 20, 5: -28, 6: 10, 7: 8}
    print(f"Part A (exact over Z): A2==Delta^4*K: {ok1}; A1==Delta^2*M "
          f"(exact div): {ok2}; 4*K*A0==M^2-Delta*S^2: {ok3}; "
          f"disc==Delta^5*S^2: {ok4}; M diagonal check: {ok5}")
    assert ok1 and ok2 and ok3 and ok4 and ok5
    return M


# ---------- Part B: per-x specialized runs ----------
def specialize(poly, c, p):
    """x:=c in Z[x,y] poly -> u-series dict {(0,2j): coeff mod p}."""
    d = {}
    for (i, j), co in poly.items():
        m = (0, 2 * j)
        d[m] = (d.get(m, 0) + co * pow(c, i, p)) % p
    return {m: co for m, co in d.items() if co}


def usqrt(dser, c, p, nu):
    """sqrt of specialized Delta as u-series, constant term (1-c) mod p."""
    a = [0] * (nu + 1)
    for (_, j), co in dser.items():
        if j <= nu:
            a[j] = co
    g = [0] * (nu + 1)
    g[0] = (1 - c) % p
    inv2g0 = pow(2 * g[0] % p, p - 2, p)
    for j in range(1, nu + 1):
        s = sum(g[i] * g[j - i] for i in range(1, j)) % p
        g[j] = (a[j] - s) * inv2g0 % p
    # verify
    for j in range(nu + 1):
        s = sum(g[i] * g[j - i] for i in range(0, j + 1)) % p
        assert s == a[j] % p, "sqrt verify fail"
    return g


def part_b(M):
    for p in ks.PRIMES:
        ks.P = p
        ks.NX = 0
        ks.NU = NU
        nbad = 0
        minvu = 10 ** 9
        cs = list(range(2, 86))
        for c in cs:
            F = ks.solve(king=True, xval=c)
            minvu = min(minvu, F.vu)
            Kc = ks.Ser(specialize(K, c, p))
            Dc = ks.Ser(specialize(DELTA, c, p))
            Mc = ks.Ser(specialize(M, c, p))
            Sc = ks.Ser(specialize(S, c, p))
            g = usqrt(specialize(DELTA, c, p), c, p, NU)
            R = ks.Ser({(0, j): g[j] for j in range(NU + 1) if g[j]})
            T1 = Kc * Dc * Dc * F
            T1 = ks.Ser({m: 2 * co % p for m, co in T1.d.items()},
                        T1.vx, T1.vu) + Mc + Sc * R
            bad = [(j, co) for (_, j), co in T1.d.items()
                   if co % p and j <= min(T1.vu, 242)]
            if bad:
                nbad += 1
                print(f"  c={c}: FAIL first {sorted(bad)[:3]}")
        print(f"prime p={p}: {len(cs)} specializations c=2..85, "
              f"identity checked to u-deg min(validity,242); "
              f"min F validity u-deg = {minvu}; failures: {nbad}")
        assert minvu >= 242, f"validity {minvu} < 242: raise MARGIN"
        assert nbad == 0


if __name__ == "__main__":
    M = part_a()
    part_b(M)
    print("CLOSED: identity 2*K*Delta^2*F + M + S*sqrt(Delta) = 0 holds as a "
          "polynomial identity modulo both primes on the full sufficient box "
          "(deg_x<=79 via 84 values, deg_u<=242 directly).")
