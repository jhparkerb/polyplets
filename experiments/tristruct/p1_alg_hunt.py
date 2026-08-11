"""p1_alg_hunt.py -- Proposer 1 (proof-first): hunt a polynomial equation
Q(y, z, F) = 0 over F_3 for the mod-3 triangle series

    F(y,z) = sum_{n>=1, 1<=H<=n} (T(n,H) mod 3) y^(n-H) z^H,

using SELF-ENUMERATED data only (build/p1_enum output). Motivation (see
results/triangle-hunt-proof-first.md): the open mod-3 region is the coefficient
array of R_k mod 3; periodicity-class laws are machine-refuted there; the
remaining mechanism-backed class is algebraicity (Christol / 3-automatic,
the class the proved spine cubic W^3 = W^2 + t lives in).

Grading: weight of y^k z^H is k + H = n, so all coefficients of F with weight
<= NDATA are known exactly from an n <= NDATA enumeration, and so are those of
F^i (products only lower weights).

Method: for an ansatz (D, dy, dz) -- Q = sum_{i<=D} c_i(y,z) F^i with
deg_y c_i <= dy, deg_z c_i <= dz -- set up the F_3-linear system
"coefficient of y^A z^B in Q vanishes for all A+B <= NDATA" and compute the
kernel. Report kernel dimension and slack (#eqs - #unknowns); print minimal
kernel vectors. A kernel that persists with slack >> 0 is a candidate
equation; the schema candidate then refits it inside the n <= 22 sandbox.

Usage: python3 p1_alg_hunt.py data/p1_king_n13.txt [D dy dz]
       (no D given: scan a small ladder of ansatzes)
"""
import sys
from itertools import product

def load_mod3(path):
    f = {}
    nmax = 0
    for line in open(path):
        p = line.split()
        if len(p) == 3 and p[1] != "SUM":
            n, H, v = int(p[0]), int(p[1]), int(p[2])
            nmax = max(nmax, n)
            r = v % 3
            if r:
                f[(n - H, H)] = r
    return f, nmax

def series_mul(a, b, N):
    """Multiply weight-truncated bivariate F_3 series (dicts (k,H)->coef)."""
    out = {}
    for (k1, h1), v1 in a.items():
        if k1 + h1 >= N:
            continue
        for (k2, h2), v2 in b.items():
            if k1 + k2 + h1 + h2 <= N:
                key = (k1 + k2, h1 + h2)
                out[key] = (out.get(key, 0) + v1 * v2) % 3
    return {k: v for k, v in out.items() if v}

def kernel_mod3(rows, ncols):
    """Kernel basis of the matrix given as list of dict-rows over F_3."""
    # Gaussian elimination; rows: list of dicts col->val
    dense = []
    for r in rows:
        dense.append([r.get(c, 0) % 3 for c in range(ncols)])
    pivots = []  # (row_idx, col)
    ri = 0
    for c in range(ncols):
        pr = None
        for i in range(ri, len(dense)):
            if dense[i][c]:
                pr = i
                break
        if pr is None:
            continue
        dense[ri], dense[pr] = dense[pr], dense[ri]
        inv = 1 if dense[ri][c] == 1 else 2
        dense[ri] = [(x * inv) % 3 for x in dense[ri]]
        for i in range(len(dense)):
            if i != ri and dense[i][c]:
                m = dense[i][c]
                dense[i] = [(a - m * b) % 3 for a, b in zip(dense[i], dense[ri])]
        pivots.append((ri, c))
        ri += 1
    pivot_cols = {c for _, c in pivots}
    free = [c for c in range(ncols) if c not in pivot_cols]
    basis = []
    for fc in free:
        v = [0] * ncols
        v[fc] = 1
        for pr, pc in pivots:
            v[pc] = (-dense[pr][fc]) % 3
        basis.append(v)
    return basis

def hunt(f, N, D, dy, dz, verbose=True):
    # powers of F up to D, truncated to weight N
    powers = [{(0, 0): 1}, dict(f)]
    for _ in range(2, D + 1):
        powers.append(series_mul(powers[-1], powers[1], N))
    unknowns = [(i, a, b) for i in range(D + 1)
                for a in range(dy + 1) for b in range(dz + 1)]
    uidx = {u: j for j, u in enumerate(unknowns)}
    # equation per (A,B), A+B <= N: sum_{i,a,b} c_iab * F^i[(A-a, B-b)] = 0
    rows = []
    for A in range(N + 1):
        for B in range(N + 1 - A):
            row = {}
            for (i, a, b) in unknowns:
                if a <= A and b <= B:
                    v = powers[i].get((A - a, B - b), 0)
                    if v:
                        row[uidx[(i, a, b)]] = v
            if row:
                rows.append(row)
    basis = kernel_mod3(rows, len(unknowns))
    neq, nun = len(rows), len(unknowns)
    # discard kernel vectors that never touch F (pure c_0 = 0 is impossible as
    # a row-satisfying vector unless c_0 kills itself -- but guard anyway)
    real = []
    for v in basis:
        if any(v[uidx[(i, a, b)]] for (i, a, b) in unknowns if i >= 1):
            real.append(v)
    if verbose:
        print("ansatz D=%d dy=%d dz=%d: unknowns=%d eqs=%d kernel=%d (nontrivial %d)"
              % (D, dy, dz, nun, neq, len(basis), len(real)))
        for v in real[:4]:
            terms = []
            for (i, a, b) in unknowns:
                cv = v[uidx[(i, a, b)]]
                if cv:
                    terms.append("%s%s%s%s" % ("" if cv == 1 else "2*",
                                               "y^%d" % a if a else "",
                                               "z^%d" % b if b else "",
                                               "F^%d" % i if i else ""))
            print("   Q = " + " + ".join(terms))
    return real, neq, nun

def main():
    path = sys.argv[1]
    f, nmax = load_mod3(path)
    print("loaded own data to n=%d; F has %d nonzero coefficients (w<=%d)"
          % (nmax, len(f), nmax))
    if len(sys.argv) > 2:
        D, dy, dz = map(int, sys.argv[2:5])
        hunt(f, nmax, D, dy, dz)
        return
    for D in (1, 2, 3):
        for dy in (1, 2, 3):
            for dz in (1, 2, 3, 4):
                nun = (D + 1) * (dy + 1) * (dz + 1)
                neq_est = (nmax + 1) * (nmax + 2) // 2
                if neq_est < 2 * nun:
                    continue
                hunt(f, nmax, D, dy, dz)

if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Hensel continuation: given Q (coeff vector + ansatz dims) and the graded
# components of a root F up to some weight, extend the root order by order.
# Char-3-safe as long as Q'(F) != 0 (detected; pure-Frobenius Q is rejected).

def q_terms(vec, D, dy, dz):
    """Non-zero (i, a, b, coef) terms of Q from a kernel vector."""
    out = []
    j = 0
    for i in range(D + 1):
        for a in range(dy + 1):
            for b in range(dz + 1):
                if vec[j]:
                    out.append((i, a, b, vec[j]))
                j += 1
    return out

def eval_Q(terms, f, N):
    """Q(F) truncated to weight N; f is the series dict."""
    Dmax = max(i for i, _, _, _ in terms)
    powers = [{(0, 0): 1}]
    for _ in range(Dmax):
        powers.append(series_mul(powers[-1], f, N))
    out = {}
    for i, a, b, c in terms:
        for (k, h), v in powers[i].items():
            if k + a + h + b <= N:
                key = (k + a, h + b)
                out[key] = (out.get(key, 0) + c * v) % 3
    return {k: v for k, v in out.items() if v}

def eval_Qprime(terms, f, N):
    """dQ/dF (F) truncated to weight N (coefficient arithmetic in F_3)."""
    Dmax = max(i for i, _, _, _ in terms)
    powers = [{(0, 0): 1}]
    for _ in range(max(1, Dmax - 1)):
        powers.append(series_mul(powers[-1], f, N))
    out = {}
    for i, a, b, c in terms:
        if i == 0:
            continue
        ci = (c * i) % 3
        if ci == 0:
            continue
        for (k, h), v in powers[i - 1].items():
            if k + a + h + b <= N:
                key = (k + a, h + b)
                out[key] = (out.get(key, 0) + ci * v) % 3
    return {k: v for k, v in out.items() if v}

def hensel_extend(terms, f, w_from, w_to, seed=None):
    """Extend root f (complete through weight w_from-1) to weight w_to.

    At each weight w the unknown block phi (coefficients at k+h == w, h >= 1,
    k >= 0) satisfies A_{w+vB} + B_{vB} * phi = 0 where A = Q(F_{<w}),
    B = Q'(F_{<w}), vB = valuation of B. Multiplication by the homogeneous
    block B_{vB} is injective over F_3[y,z], so the solution is unique if it
    exists; inconsistency raises ValueError. If the linear system is
    underdetermined at weight w (cannot happen with B_{vB} != 0, guarded) or
    B == 0 (pure-Frobenius Q), raises ValueError. seed, if given, supplies
    known components to CHECK against (dict), not to assume.
    """
    f = dict(f)
    for w in range(w_from, w_to + 1):
        B = eval_Qprime(terms, f, w + 2 * w + 2)
        if not B:
            raise ValueError("Q'(F)=0: pure-Frobenius equation, no Hensel")
        vB = min(k + h for k, h in B)
        Bv = {m: v for m, v in B.items() if m[0] + m[1] == vB}
        A = eval_Q(terms, f, w + vB)
        # unknowns phi_{(k,h)}, k+h = w, h >= 1 (no H=0 cells exist)
        unk = [(k, w - k) for k in range(0, w)]
        # equations: monomials of weight w+vB: A_m + sum Bv_{m-u} phi_u = 0
        rows = []
        rhs = []
        for K in range(0, w + vB + 1):
            Hh = w + vB - K
            m = (K, Hh)
            row = {}
            for j, (k, h) in enumerate(unk):
                bm = Bv.get((K - k, Hh - h), 0)
                if bm:
                    row[j] = bm
            av = A.get(m, 0)
            if row or av:
                rows.append(row)
                rhs.append((-av) % 3)
        phi = _solve_unique(rows, rhs, len(unk))
        if phi is None:
            raise ValueError("Hensel step w=%d: no unique solution" % w)
        for j, (k, h) in enumerate(unk):
            if phi[j]:
                f[(k, h)] = phi[j]
            if seed is not None and seed.get((k, h), 0) != phi[j]:
                raise ValueError("Hensel mismatch vs seed at (k=%d,h=%d) w=%d"
                                 % (k, h, w))
    return f

def _solve_unique(rows, rhs, nuk):
    """Solve over F_3; return solution vector iff it exists and is unique."""
    aug = []
    for r, b in zip(rows, rhs):
        aug.append([r.get(c, 0) for c in range(nuk)] + [b])
    ri = 0
    piv = []
    for c in range(nuk):
        pr = next((i for i in range(ri, len(aug)) if aug[i][c]), None)
        if pr is None:
            continue
        aug[ri], aug[pr] = aug[pr], aug[ri]
        inv = 1 if aug[ri][c] == 1 else 2
        aug[ri] = [(x * inv) % 3 for x in aug[ri]]
        for i in range(len(aug)):
            if i != ri and aug[i][c]:
                m = aug[i][c]
                aug[i] = [(a - m * b) % 3 for a, b in zip(aug[i], aug[ri])]
        piv.append(c)
        ri += 1
    for i in range(ri, len(aug)):
        if aug[i][nuk]:
            return None  # inconsistent
    if len(piv) < nuk:
        return None  # underdetermined
    sol = [0] * nuk
    for i, c in enumerate(piv):
        sol[c] = aug[i][nuk]
    return sol

def selftest():
    """Machinery check on a synthetic algebraic (here rational) series:
    F = z / (1 - z - y*z), i.e. (1 - z - y*z) F - z = 0."""
    N = 13
    f = {}
    # coefficients: F = sum_{H>=1} z^H (1+y)^{H-1} -> f[(k,H)] = C(H-1,k) mod 3
    from math import comb
    for H in range(1, N + 1):
        for k in range(0, H):
            v = comb(H - 1, k) % 3
            if v and k + H <= N:
                f[(k, H)] = v
    real, neq, nun = hunt(f, N, 1, 1, 1, verbose=False)
    assert real, "selftest: kernel not found for rational series"
    terms = q_terms(real[0], 1, 1, 1)
    # extend from scratch: start with empty series, weights 1..N
    g = hensel_extend(terms, {}, 1, N)
    assert g == f, "selftest: Hensel continuation disagrees with truth"
    print("selftest OK: kernel found (%d eqs, %d unknowns) and Hensel "
          "reproduces all %d coefficients from the equation alone"
          % (neq, nun, len(f)))

