#!/usr/bin/env python3
"""Extract the per-row growth series of the height-diagonal defect gas directly
from the triangle -- no enumeration needed -- and equation-guess for a closed
form. Restored + extended to the a(40) triangle (was removed in 78602f8; the
a(21) run in docs/proofs/T-n-nm2-and-general.md sec.5 reached only 9 terms and
found no closed form).

lambda_raw(y) = Z_N(y)/Z_{N-1}(y),  Z_N(y) = sum_e T(N+e,N) y^e   (fixed height N).
This is the *wide* slice of the triangle; lambda_raw converges in N, so the
n=NMAX triangle yields ~(NMAX-1)/2 converged terms.

Run:  python3 experiments/braw_from_data.py [NMAX]
"""
import sys
from fractions import Fraction

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 40
DATA = f"results/ns_a{NMAX}/perheight"   # h{N}.out: lines "n T(n,N)"


def Trow(N):
    d = {}
    with open(f"{DATA}/h{N}.out") as fh:
        for line in fh:
            p = line.split()
            if len(p) == 2:
                d[int(p[0])] = int(p[1])
    return d


ROWS = {N: Trow(N) for N in range(1, NMAX + 1)}


def ZN(N, K):
    return [Fraction(ROWS[N].get(N + e, 0)) for e in range(K + 1)]


def divseries(num, den, K):
    q = [Fraction(0)] * (K + 1)
    for i in range(K + 1):
        q[i] = (num[i] - sum(den[j] * q[i - j] for j in range(1, i + 1))) / den[0]
    return q


def logseries(f, K):
    g = [Fraction(0)] * (K + 1)
    for i in range(1, K + 1):
        s = Fraction(i) * f[i]
        for j in range(1, i):
            s -= Fraction(j) * g[j] * f[i - j]
        g[i] = s / (Fraction(i) * f[0])
    return g


def converged(coeff_at_N):
    Ns = sorted(coeff_at_N)
    for i in range(1, len(Ns)):
        if coeff_at_N[Ns[i]] == coeff_at_N[Ns[i - 1]]:
            return coeff_at_N[Ns[i]], Ns[i] - 1
    return None


def extract():
    lam, braw, kmax = [], [], 0
    for k in range(1, NMAX):
        bvals, lvals = {}, {}
        for N in range(max(2, k), NMAX - k + 1):   # Z_N, Z_{N-1} known to order k
            lam_s = divseries(ZN(N, k), ZN(N - 1, k), k)
            lvals[N] = lam_s[k]
            bvals[N] = logseries(lam_s, k)[k]
        cb, cl = converged(bvals), converged(lvals)
        if cb is None or cl is None:
            break
        braw.append(cb[0]); lam.append(cl[0]); kmax = k
    return [Fraction(3)] + lam, [Fraction(0)] + braw, kmax


# ---- equation guessing --------------------------------------------------

def mulseries(a, b, K):
    return [sum(a[j] * b[i - j] for j in range(i + 1)) for i in range(K + 1)]


def powers(f, maxdeg, K):
    ps = [[Fraction(1)] + [Fraction(0)] * K]
    for _ in range(maxdeg):
        ps.append(mulseries(ps[-1], f, K))
    return ps


def nullspace(M):
    """Exact rational null space of matrix M (list of rows). Returns list of
    basis vectors (as Fraction lists)."""
    A = [row[:] for row in M]
    rows, cols = len(A), len(A[0]) if A else 0
    pivots, r = [], 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = A[r][c]
        A[r] = [x / inv for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(cols)]
        pivots.append(c); r += 1
        if r == rows:
            break
    free = [c for c in range(cols) if c not in pivots]
    basis = []
    for fc in free:
        v = [Fraction(0)] * cols
        v[fc] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -A[i][fc]
        basis.append(v)
    return basis


def guess_algebraic(f, df, dy, K):
    """Look for sum_{i<=df, j<=dy} c_ij f^i y^j = 0. Needs K+1 >= #unknowns to be
    falsifiable. Returns list of nonzero relations (coefficient vectors)."""
    fp = powers(f, df, K)
    terms = []          # (i,j)
    cols = []           # each column = series coeffs of f^i * y^j
    for i in range(df + 1):
        for j in range(dy + 1):
            col = [Fraction(0)] * (K + 1)
            for n in range(j, K + 1):
                col[n] = fp[i][n - j]
            terms.append((i, j)); cols.append(col)
    nun = len(terms)
    # every order 0..K is one equation — an over-determined system when
    # falsifiable (K+1 > nun), so the extra orders can reject a low-order fit
    # (matches guess_odf; a bare nun×nun square would ignore the holdout orders)
    M = [[cols[t][n] for t in range(nun)] for n in range(K + 1)]
    ns = nullspace(M)
    return terms, ns, (K + 1 > nun)


def deriv(f, K):
    return [Fraction(n + 1) * f[n + 1] for n in range(K)] + [Fraction(0)]


def guess_odf(f, order, deg, K):
    """Linear ODE sum_{j<=order} p_j(y) f^(j) = 0, deg p_j <= deg. Falsifiable
    iff K+1 > #unknowns = (order+1)(deg+1)."""
    ders = [f[:]]
    for _ in range(order):
        ders.append(deriv(ders[-1], K))
    terms, cols = [], []
    for j in range(order + 1):
        for d in range(deg + 1):
            col = [Fraction(0)] * (K + 1)
            for n in range(d, K + 1):
                col[n] = ders[j][n - d]
            terms.append((j, d)); cols.append(col)
    nun = len(terms)
    M = [[cols[t][n] for t in range(nun)] for n in range(K + 1)]
    ns = nullspace(M)
    return terms, ns, (K + 1 > nun)


def sweep_odf(name, f, K):
    print(f"=== D-finite (linear ODE) guessing on {name} (K={K}) ===")
    found = False
    for order in range(1, 5):
        for deg in range(0, 8):
            if (order + 1) * (deg + 1) >= K + 1:
                continue
            terms, ns, falsifiable = guess_odf(f, order, deg, K)
            if ns:
                print(f"  order={order}, deg={deg}: {len(ns)} relation(s), "
                      f"#unknowns={len(terms)}, #eqs={K+1}  <== NONTRIVIAL")
                found = True
                for v in ns[:1]:
                    rel = [(terms[i], v[i]) for i in range(len(v)) if v[i] != 0]
                    print("    ", rel)
    if not found:
        print("  no D-finite relation (all falsifiable forms trivial)")


def sweep_alg(name, f, K):
    print(f"=== algebraic equation guessing on {name} (K={K}) ===")
    found = False
    for df in range(2, 8):
        for dy in range(1, 8):
            terms, ns, falsifiable = guess_algebraic(f, df, dy, K)
            if not falsifiable:
                continue
            if ns:
                print(f"  deg(f)={df}, deg(y)={dy}: {len(ns)} relation(s), "
                      f"#unknowns={len(terms)}, #eqs={K+1}  <== NONTRIVIAL")
                found = True
                for v in ns[:1]:
                    rel = [(terms[i], v[i]) for i in range(len(v)) if v[i] != 0]
                    print("    ", rel)
    if not found:
        print("  no algebraic relation (all falsifiable forms trivial)")


if __name__ == "__main__":
    lam, braw, kmax = extract()
    print(f"NMAX={NMAX}: {kmax} converged terms (a21 reached 9)")
    print("lambda_raw =", [str(c) for c in lam])
    print("b_raw      =", [str(c) for c in braw])
    print()
    K = kmax  # series orders 0..K reliable for lambda_raw
    sweep_alg("lambda_raw", lam[:K + 1], K)
    print()
    sweep_odf("lambda_raw", lam[:K + 1], K)
    print()
    sweep_alg("b_raw (=log lambda_raw)", braw[:K + 1], K)
    print()
    sweep_odf("b_raw (=log lambda_raw)", braw[:K + 1], K)
