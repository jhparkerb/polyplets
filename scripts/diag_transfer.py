#!/usr/bin/env python3
"""Transfer-matrix derivation of the diagonal closed forms P_k (option 5).

Instead of fitting a_k,b_k from computed T(n,n-k) data, derive them from a
finite row-to-row transfer matrix on *interface states* (the top row's column
pattern, normalized, plus any pending gap-2 bridge obligation), with y marking
per-row excess. For bounded excess the state set is finite and the matrix is
symbolic in y; T(n,H=R) = L . T(y)^(R-1) . R, and [y^k] T(n,R) = T(R+k, R).

This file starts with the excess<=1 sector (states S, D1, D2b, D2p) and
verifies it reproduces T(n,n) = 3^(n-1) and T(n,n-1) = (25n-45) 3^(n-4)
exactly -- the k=1 closed form, boundary term included. Higher excess (for
b_2 = -209/2 and beyond) extends the state set the same way.

No data, no runs: the a_k,b_k are read off the matrix. Validation: the
excess<=k sector must reproduce the known P_0..P_k.
"""
from fractions import Fraction as F

# --- truncated power series in y (mod y^(K+1)), coefficients in Q ---

class PS:
    __slots__ = ("c", "K")
    def __init__(self, c, K):
        self.K = K
        self.c = [F(x) for x in c[:K + 1]] + [F(0)] * (K + 1 - len(c))
    def __add__(self, o):
        return PS([a + b for a, b in zip(self.c, o.c)], self.K)
    def __mul__(self, o):
        if isinstance(o, PS):
            r = [F(0)] * (self.K + 1)
            for i, a in enumerate(self.c):
                if a == 0:
                    continue
                for j, b in enumerate(o.c):
                    if i + j > self.K:
                        break
                    r[i + j] += a * b
            return PS(r, self.K)
        return PS([a * F(o) for a in self.c], self.K)
    __rmul__ = __mul__
    def __repr__(self):
        return " + ".join(f"{a}y^{i}" for i, a in enumerate(self.c) if a != 0) or "0"


def zero(K): return PS([0], K)
def const(x, K): return PS([x], K)
def ymono(coeff, deg, K):
    c = [0] * (deg + 1); c[deg] = coeff; return PS(c, K)


def matvec(M, v, K):
    n = len(v)
    return [sum((M[i][j] * v[j] for j in range(n)), zero(K)) for i in range(n)]


def matmat(A, B, K):
    n = len(A)
    return [[sum((A[i][k] * B[k][j] for k in range(n)), zero(K))
             for j in range(n)] for i in range(n)]


# --- excess<=1 transfer matrix: states [S, D1, D2b, D2p] ---

def build_excess1(K):
    """Return (T, L, R) for the excess<=1 interface sector."""
    S, D1, D2b, D2p = 0, 1, 2, 3
    N = 4
    T = [[zero(K) for _ in range(N)] for _ in range(N)]
    # from S: single->single 3; single->domino 4y; single->gap2 (1 bridged, 4 pending) y
    T[S][S]  = const(3, K)
    T[S][D1] = ymono(4, 1, K)
    T[S][D2b] = ymono(1, 1, K)
    T[S][D2p] = ymono(4, 1, K)
    # from doubled rows back to single (excess budget spent): king-touch counts
    T[D1][S]  = const(4, K)   # touch {0,1}: c in {-1,0,1,2}
    T[D2b][S] = const(5, K)   # touch {0,2}: c in {-1,0,1,2,3}
    T[D2p][S] = const(1, K)   # forced bridge at column 1
    # boundary vectors: bottom row L (doubled bottom marks y; D2b needs a row
    # below so cannot be a bottom row), top row R (D2p unbridged at top invalid)
    L = [const(1, K), ymono(1, 1, K), zero(K), ymono(1, 1, K)]
    Rv = [const(1, K), const(1, K), const(1, K), zero(K)]
    return T, L, Rv


def T_nH(T, L, Rv, R, K):
    """T(n, H=R) as a power series in y; [y^k] = T(R+k, R)."""
    N = len(L)
    # M = T^(R-1)
    M = [[const(1, K) if i == j else zero(K) for j in range(N)] for i in range(N)]
    for _ in range(R - 1):
        M = matmat(M, T, K)
    Mr = matvec(M, Rv, K)
    return sum((L[i] * Mr[i] for i in range(N)), zero(K))


def closed_form_check(K):
    T, L, Rv = build_excess1(K)
    print(f"excess<=1 sector, {len(L)} states, truncation y^{K}")
    print(f"{'R':>3} {'H=R':>4} | " + "  ".join(f"[y^{k}]=T({{n}},{{n-{k}}})" for k in range(K + 1)))
    for R in range(2, 9):
        ps = T_nH(T, L, Rv, R, K)
        vals = [ps.c[k] for k in range(K + 1)]
        # expected: k=0 -> 3^(R-1); k=1 -> (25*(R+1)-45)*3^((R+1)-4)=(25R-20)3^(R-3)
        exp0 = F(3) ** (R - 1)
        exp1 = (25 * (R + 1) - 45) * F(3) ** ((R + 1) - 4) if R >= 3 else None
        tag = "OK" if vals[0] == exp0 and (K < 1 or exp1 is None or vals[1] == exp1) else "MISMATCH"
        print(f"{R:>3} {R:>4} | " + "  ".join(str(v) for v in vals) +
              f"   (exp k0={exp0}, k1={exp1})  {tag}")


if __name__ == "__main__":
    closed_form_check(1)
