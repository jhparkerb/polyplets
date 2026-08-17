#!/usr/bin/env python3
"""Session 04: TEMPERLEY-STYLE q-SERIES SOLUTION of the area-marked
functional equation for convex king animals (and the polyomino control).

The q-FE (validated cell-by-cell in s04_qfe_check.py) is the s03 system with
every operator formula taken at z := q*s (new-row lengths marked by q), G(1),
G'(1) untouched:

  F00(s) = xyqs/(1-xqs) + y F00(qs)/(1-xqs)^2
  F10(s) = y*Bq[F00](s) + y*Cq[F10](s),      F01 = F10
  F11(s) = y*D1q[F00](s) + 2y*D2q[F10](s) + y*L3q[F11](s)
  F(x,y,q) = F00(1) + 2 F10(1) + F11(1)

  Bq[G](s) = (G(z)-zG1)/((z-1)(1-xz)) + [king] xzG1/(1-xz),     z = qs
  Cq[G](s) = z(G(z)-G1)/((z-1)(1-xz)) + [king] xzG1/(1-xz)
  L3q[G](s) = [z^2 G(z) - z^2 G1 - z(z-1)G1']/(z-1)^2
  D2q[G](s) = L3q[G](s) - z(G(z)-G1)/(z-1)
  D1q[G](s) = [G(z) - z^2 G1 - z(z-1)(G1'-2G1)]/(z-1)^2

Solution by q-iteration (each step multiplies by y and gains q-valuation, so
all sums below are q-adically convergent -- finitely many terms contribute
below q^N; kernel roots are never needed):

  F00(z)  = sum_{n>=0} x y^{n+1} q^{n+1} z
            * prod_{j=1}^{n} (1-x q^j z)^{-2} * (1-x q^{n+1} z)^{-1}
  F10(s)  = sum_{n>=0} y^n prod_{j=1}^{n} R(q^j s)
            * [ A1(q^n s) + y T(q^{n+1} s) F10(1) ]
      R(z) = z/((z-1)(1-xz)),
      T(z) = (xz(z-1)-z)/((z-1)(1-xz))  [king] ; -z/((z-1)(1-xz)) [control]
      A1   = y*Bq[F00]
      => F10(1) = alpha(1)/(1-beta(1))     [Temperley ratio of q-series]
  F11(s)  = sum_{n>=0} y^n prod_{j=1}^{n} U(q^j s)
            * [ A2(q^n s) - y V1(q^{n+1}s) F11(1) - y V2(q^{n+1}s) F11'(1) ]
      U(z) = V1(z) = z^2/(z-1)^2,  V2(z) = z/(z-1),  A2 = yD1q[F00]+2yD2q[F10]
      => 2x2 linear system for (F11(1), F11'(1)) from the dual (s=1+eps)
         evaluation; determinant = 1 + O(q), invertible.

All evaluations are at points z = q^m(1+eps), eps^2=0 (dual numbers encode
the s-derivative at 1); every inverted quantity is a unit in Q[[q]] since
m >= 1 wherever (z-1) is inverted.

Checks:
  1. joint: for several numeric (x,y), [q^n] F == sum_{w,h} f(w,h;n) x^w y^h
     from the ground-truth table (n <= 10), king AND polyomino modes;
  2. x=y=1, N=30: king [q^n]F == the banked 30-term convex-mirage area
     sequence; control == known convex-polyomino-by-area terms.
"""
import sys, os, json, time
from fractions import Fraction

NDEF = 30


class QS:
    """Truncated power series in q, Fraction coefficients, length N+1."""
    __slots__ = ("c",)
    N = NDEF

    def __init__(self, c=None):
        self.c = c if c is not None else [Fraction(0)] * (QS.N + 1)

    @staticmethod
    def const(v):
        r = QS()
        r.c[0] = Fraction(v)
        return r

    @staticmethod
    def mono(m, v=1):
        r = QS()
        if m <= QS.N:
            r.c[m] = Fraction(v)
        return r

    def __add__(a, b):
        return QS([x + y for x, y in zip(a.c, b.c)])

    def __sub__(a, b):
        return QS([x - y for x, y in zip(a.c, b.c)])

    def __neg__(a):
        return QS([-x for x in a.c])

    def __mul__(a, b):
        if not isinstance(b, QS):
            return a.scal(b)
        N = QS.N
        r = [Fraction(0)] * (N + 1)
        for i, x in enumerate(a.c):
            if x:
                for j in range(0, N - i + 1):
                    y = b.c[j]
                    if y:
                        r[i + j] += x * y
        return QS(r)

    def __rmul__(a, b):
        return a.scal(b)

    def scal(a, k):
        return QS([x * k for x in a.c])

    def inv(a):
        assert a.c[0] != 0, "inv of non-unit"
        N = QS.N
        r = [Fraction(0)] * (N + 1)
        r[0] = 1 / a.c[0]
        for j in range(1, N + 1):
            s = sum(a.c[i] * r[j - i] for i in range(1, j + 1) if a.c[i])
            r[j] = -r[0] * s
        return QS(r)

    def is_zero(a):
        return all(x == 0 for x in a.c)


class D:
    """Dual number a + b*eps over QS (eps = s-1, eps^2 = 0)."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=None):
        self.a = a
        self.b = b if b is not None else QS()

    def __add__(x, y):
        y = D.lift(y)
        return D(x.a + y.a, x.b + y.b)

    def __radd__(x, y):
        return x + y

    def __sub__(x, y):
        y = D.lift(y)
        return D(x.a - y.a, x.b - y.b)

    def __rsub__(x, y):
        return D.lift(y) - x

    def __neg__(x):
        return D(-x.a, -x.b)

    def __mul__(x, y):
        y = D.lift(y)
        return D(x.a * y.a, x.a * y.b + x.b * y.a)

    def __rmul__(x, y):
        return x * y

    def inv(x):
        ia = x.a.inv()
        return D(ia, -(x.b * ia * ia))

    def is_zero(x):
        return x.a.is_zero() and x.b.is_zero()

    @staticmethod
    def lift(v):
        if isinstance(v, D):
            return v
        if isinstance(v, QS):
            return D(v, QS())
        return D(QS.const(v), QS())


class Solver:
    def __init__(self, x, y, king=True):
        self.x = Fraction(x)
        self.y = Fraction(y)
        self.king = king
        self._f00 = {}
        self._f10 = {}
        self.one = D(QS.const(1), QS())

    def Z(self, m):
        """the point q^m * (1+eps) as a dual number."""
        return D(QS.mono(m), QS.mono(m))

    # ---- phase (0,0): explicit q-product series ----
    def F00_at(self, m):
        if m in self._f00:
            return self._f00[m]
        x, y = self.x, self.y
        acc = D(QS(), QS())
        prod = self.one
        n = 0
        while m + n + 1 <= QS.N:
            zn = self.Z(m + n + 1)
            i1 = (self.one - x * zn).inv()
            term = (x * y ** (n + 1)) * zn * prod * i1
            acc = acc + term
            prod = prod * i1 * i1
            n += 1
        self._f00[m] = acc
        return acc

    # ---- operator ingredients ----
    def R_at(self, m):
        z = self.Z(m)
        return z * (z - 1).inv() * (self.one - self.x * z).inv()

    def T_at(self, m):
        z = self.Z(m)
        base = (z - 1).inv() * (self.one - self.x * z).inv()
        if self.king:
            return (self.x * z * (z - 1) - z) * base
        return -z * base

    def A1_at(self, t):
        """y * Bq[F00] at s-point q^t(1+eps)."""
        z = self.Z(t + 1)
        core = (self.F00_at(t + 1) - z * self.F001) * (z - 1).inv() \
            * (self.one - self.x * z).inv()
        if self.king:
            core = core + self.x * z * self.F001 \
                * (self.one - self.x * z).inv()
        return self.y * core

    # ---- phase (1,0)/(0,1): Temperley ratio ----
    def solve_F10(self):
        f0 = self.F00_at(0)
        self.F001, self.F00p1 = f0.a, f0.b
        alpha = D(QS(), QS())
        beta = D(QS(), QS())
        prod = self.one
        n = 0
        while n <= QS.N and not prod.is_zero():
            alpha = alpha + self.y ** n * prod * self.A1_at(n)
            beta = beta + self.y ** (n + 1) * prod * self.T_at(n + 1)
            prod = prod * self.R_at(n + 1)
            n += 1
        self.F101 = alpha.a * (QS.const(1) - beta.a).inv()
        self.F10p1 = alpha.b + beta.b * self.F101

    def F10_at(self, t):
        if t in self._f10:
            return self._f10[t]
        acc = D(QS(), QS())
        prod = self.one
        n = 0
        while t + n <= QS.N and not prod.is_zero():
            acc = acc + self.y ** n * prod * (
                self.A1_at(t + n) + self.y * self.T_at(t + n + 1) * self.F101)
            prod = prod * self.R_at(t + n + 1)
            n += 1
        self._f10[t] = acc
        return acc

    # ---- phase (1,1): 2x2 Temperley system ----
    def D1F00_at(self, t):
        z = self.Z(t + 1)
        iz1 = (z - 1).inv()
        return (self.F00_at(t + 1) - z * z * self.F001
                - z * (z - 1) * (self.F00p1 - 2 * self.F001)) * iz1 * iz1

    def D2F10_at(self, t):
        z = self.Z(t + 1)
        iz1 = (z - 1).inv()
        Gz = self.F10_at(t + 1)
        L = (z * z * Gz - z * z * self.F101
             - z * (z - 1) * self.F10p1) * iz1 * iz1
        return L - z * (Gz - self.F101) * iz1

    def A2_at(self, t):
        return self.y * self.D1F00_at(t) + 2 * self.y * self.D2F10_at(t)

    def solve_F11(self):
        P = D(QS(), QS())
        Q1 = D(QS(), QS())
        Q2 = D(QS(), QS())
        prod = self.one
        n = 0
        while n <= QS.N and not prod.is_zero():
            zn1 = self.Z(n + 1)
            iz1 = (zn1 - 1).inv()
            V1 = zn1 * zn1 * iz1 * iz1
            V2 = zn1 * iz1
            P = P + self.y ** n * prod * self.A2_at(n)
            Q1 = Q1 + self.y ** (n + 1) * prod * V1
            Q2 = Q2 + self.y ** (n + 1) * prod * V2
            prod = prod * V1        # U(q^{n+1} s) == V1 at the same point
            n += 1
        one = QS.const(1)
        a11, a12, r1 = one + Q1.a, Q2.a, P.a
        a21, a22, r2 = Q1.b, one + Q2.b, P.b
        det = a11 * a22 - a12 * a21
        idet = det.inv()
        self.F111 = (r1 * a22 - a12 * r2) * idet
        self.F11p1 = (a11 * r2 - a21 * r1) * idet

    def solve(self):
        self.solve_F10()
        self.solve_F11()
        return self.F001 + self.F101.scal(2) + self.F111


def series_ints(F):
    out = []
    for co in F.c:
        assert co.denominator == 1, f"non-integer coefficient {co}"
        out.append(int(co))
    return out


MIRAGE_KING = [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174,
               853111, 2677214, 8389720, 26271014, 82230035, 257333334,
               805229818, 2519563026, 7883577553, 24667161861, 77181772540,
               241496421322, 755626445009, 2364307821370, 7397776287396,
               23147205741474, 72426263089887, 226617613513394,
               709073559601858]
MIRAGE_POLY = [1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312, 23320, 57279,
               138536, 331032]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    truth = json.load(open(os.path.join(here, "..",
                                        "out_s04_area_truth.json")))

    # ---- check 1: joint (x,y) evaluations vs ground truth, N=10 ----
    QS.N = 10
    for king in (True, False):
        tag = "king" if king else "poly"
        T = truth[tag]
        for (xv, yv) in [(1, 1), (2, 1), (1, 3), (3, 2)]:
            want = [0] * (QS.N + 1)
            for wh, d in T.items():
                w, h = map(int, wh.split(","))
                for ns, c in d.items():
                    n = int(ns)
                    if n <= QS.N:
                        want[n] += c * xv ** w * yv ** h
            F = Solver(xv, yv, king=king).solve()
            got = series_ints(F)
            ok = got[1:] == want[1:]
            print(f"{tag} x={xv} y={yv}: q-Temperley solution vs truth "
                  f"(n<={QS.N}): {'OK' if ok else 'FAIL'}")
            if not ok:
                print("   got ", got[1:])
                print("   want", want[1:])
                sys.exit(1)

    # ---- check 2: x=y=1, N=30, vs banked area sequences ----
    QS.N = NDEF
    t0 = time.time()
    F = Solver(1, 1, king=True).solve()
    got = series_ints(F)[1:]
    ok = got == MIRAGE_KING[:len(got)]
    print(f"\nKING x=y=1, N={QS.N} ({time.time()-t0:.1f}s): area sequence "
          f"from q-Temperley formula vs banked 30-term convex-mirage "
          f"sequence: {'OK' if ok else 'FAIL'}")
    print("  " + ", ".join(map(str, got[:16])) + ", ...")
    if not ok:
        print("  want", MIRAGE_KING)
        sys.exit(1)

    t0 = time.time()
    F = Solver(1, 1, king=False).solve()
    gotp = series_ints(F)[1:]
    okp = gotp[:len(MIRAGE_POLY)] == MIRAGE_POLY
    print(f"CONTROL x=y=1, N={QS.N} ({time.time()-t0:.1f}s): convex "
          f"polyominoes by area, first {len(MIRAGE_POLY)} vs known: "
          f"{'OK' if okp else 'FAIL'}")
    print("  " + ", ".join(map(str, gotp)))
    if not okp:
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
