#!/usr/bin/env python3
"""Session 05 MAIN: exact singularity analysis of the area generating
function F(1,1,q) of convex king animals (+ polyomino control).

Structure theorem (from the s04 Temperley solution, s05_beta_forms.py):
  F(1,1,q) = c0(q) + c1(q) * alpha(q) / K(q),
  K(q) = 1 - beta(q) = sum_{m>=0} (-1)^m (2-q^m) q^{m(m+1)/2}/(q;q)_m^2  [king]
  J(q) = 1 - beta(q) = sum_{m>=0} (-1)^m         q^{m(m+1)/2}/(q;q)_m^2  [control]
where alpha, c0, c1 are analytic in |q|<1 except possibly at zeros of the
2x2 Temperley determinant det(q) (checked nonvanishing on the relevant
range below).  Hence the dominant singularity of F on [0,1) is a SIMPLE
POLE at the smallest zero q_c of K (resp. J), provided c1*alpha does not
vanish there (checked), and

  a(n) ~ A * mu^n,  mu = 1/q_c,  A = -c1(q_c)*alpha(q_c) / (K'(q_c)*q_c).

This script computes q_c, mu, A to high precision (Decimal, 110 digits
working precision), for king and control, plus the directed subfamilies
(F00+F10: amplitude A_dir = -alpha(q_c)/(K'(q_c)*q_c), same mu), and
validates everything against the exact 60-term sequences
(out_s05_terms60.txt) and a numeric-vs-series evaluation at q=1/10.
"""
import os, re, sys
from decimal import Decimal, getcontext

getcontext().prec = 110
TOL = Decimal("1e-100")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

D0 = Decimal(0)
D1 = Decimal(1)


class DD:
    """dual number a + b*eps over Decimal (eps = s-1, eps^2=0)."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=D0):
        self.a = a
        self.b = b

    @staticmethod
    def lift(v):
        if isinstance(v, DD):
            return v
        return DD(Decimal(v))

    def __add__(x, y):
        y = DD.lift(y)
        return DD(x.a + y.a, x.b + y.b)

    __radd__ = __add__

    def __sub__(x, y):
        y = DD.lift(y)
        return DD(x.a - y.a, x.b - y.b)

    def __rsub__(x, y):
        return DD.lift(y) - x

    def __neg__(x):
        return DD(-x.a, -x.b)

    def __mul__(x, y):
        y = DD.lift(y)
        return DD(x.a * y.a, x.a * y.b + x.b * y.a)

    __rmul__ = __mul__

    def inv(x):
        ia = D1 / x.a
        return DD(ia, -(x.b * ia * ia))

    def mag(x):
        return abs(x.a) + abs(x.b)


class NSolver:
    """Numeric (Decimal) mirror of s04_q_temperley.Solver at fixed q."""

    def __init__(self, q, king=True, x=1, y=1):
        self.q = Decimal(q)
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.king = king
        self._f00 = {}
        self._f10 = {}
        self.one = DD(D1)
        self._qp = {}

    def qpow(self, m):
        if m not in self._qp:
            self._qp[m] = self.q ** m
        return self._qp[m]

    def Z(self, m):
        p = self.qpow(m)
        return DD(p, p)

    def F00_at(self, m):
        if m in self._f00:
            return self._f00[m]
        x, y = self.x, self.y
        acc = DD(D0)
        prod = self.one
        n = 0
        while n < 2000:
            zn = self.Z(m + n + 1)
            i1 = (self.one - x * zn).inv()
            term = (x * y ** (n + 1)) * zn * prod * i1
            acc = acc + term
            if term.mag() < TOL:
                break
            prod = prod * i1 * i1
            n += 1
        self._f00[m] = acc
        return acc

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
        z = self.Z(t + 1)
        core = (self.F00_at(t + 1) - z * self.F001) * (z - 1).inv() \
            * (self.one - self.x * z).inv()
        if self.king:
            core = core + self.x * z * self.F001 \
                * (self.one - self.x * z).inv()
        return self.y * core

    def solve_F10(self):
        f0 = self.F00_at(0)
        self.F001, self.F00p1 = f0.a, f0.b
        alpha = DD(D0)
        beta = DD(D0)
        prod = self.one
        n = 0
        while n < 2000 and prod.mag() > TOL:
            alpha = alpha + self.y ** n * prod * self.A1_at(n)
            beta = beta + self.y ** (n + 1) * prod * self.T_at(n + 1)
            prod = prod * self.R_at(n + 1)
            n += 1
        self.alpha, self.beta = alpha, beta

    def F10_at(self, t):
        if t in self._f10:
            return self._f10[t]
        acc = DD(D0)
        prod = self.one
        n = 0
        while n < 2000 and prod.mag() > TOL:
            acc = acc + self.y ** n * prod * (
                self.A1_at(t + n)
                + self.y * self.T_at(t + n + 1) * self.F101)
            prod = prod * self.R_at(t + n + 1)
            n += 1
        self._f10[t] = acc
        return acc

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
        P = DD(D0)
        Q1 = DD(D0)
        Q2 = DD(D0)
        prod = self.one
        n = 0
        while n < 2000 and prod.mag() > TOL:
            zn1 = self.Z(n + 1)
            iz1 = (zn1 - 1).inv()
            V1 = zn1 * zn1 * iz1 * iz1
            V2 = zn1 * iz1
            P = P + self.y ** n * prod * self.A2_at(n)
            Q1 = Q1 + self.y ** (n + 1) * prod * V1
            Q2 = Q2 + self.y ** (n + 1) * prod * V2
            prod = prod * V1
            n += 1
        a11, a12, r1 = D1 + Q1.a, Q2.a, P.a
        a21, a22, r2 = Q1.b, D1 + Q2.b, P.b
        self.det = a11 * a22 - a12 * a21
        self.F111 = (r1 * a22 - a12 * r2) / self.det
        self.F11p1 = (a11 * r2 - a21 * r1) / self.det

    def assemble(self, f101):
        """full F given an injected value of F10(1) (F is affine in it)."""
        self.F101 = Decimal(f101)
        self.F10p1 = self.alpha.b + self.beta.b * self.F101
        self._f10 = {}
        self.solve_F11()
        return self.F001 + 2 * self.F101 + self.F111


# ---------- closed normal forms (independent implementation) ----------

def denom_series(q, king, need_terms=None):
    """K(q) [king] or J(q) [control]; sum_{m} with (q;q)_m running."""
    q = Decimal(q)
    tot = D0
    poch = D1  # (q;q)_m
    qm = D1    # q^m
    qtri = D1  # q^{m(m+1)/2}
    m = 0
    while m < 5000:
        t = qtri / (poch * poch)
        if king:
            t *= (2 - qm)
        tot += t if m % 2 == 0 else -t
        if abs(t) < TOL and m > 3:
            break
        m += 1
        qm *= q
        qtri *= qm
        poch *= (D1 - qm)
    return tot


def dderiv(f, q, h=Decimal("1e-40")):
    return (f(q + h) - f(q - h)) / (2 * h)


def find_root(f, lo, hi, iters=400):
    lo, hi = Decimal(lo), Decimal(hi)
    flo, fhi = f(lo), f(hi)
    assert flo * fhi < 0, "not bracketed"
    # bisection to full precision (robust; ~350 iters for 1e-105)
    for _ in range(iters):
        mid = (lo + hi) / 2
        fm = f(mid)
        if fm == 0:
            return mid
        if flo * fm < 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if hi - lo < Decimal("1e-102"):
            break
    return (lo + hi) / 2


def load_terms():
    seqs = {}
    cur = None
    for line in open(os.path.join(ROOT, "out_s05_terms60.txt")):
        m = re.match(r"(\w+) \(n=1", line)
        if m:
            cur = m.group(1)
            seqs[cur] = []
            continue
        m = re.match(r"\s+(\d+)\s+(\d+)\s*$", line)
        if m and cur:
            seqs[cur].append(int(m.group(2)))
    return seqs


def analyze(king, seq_full, seq_dir, lo, hi):
    tag = "KING" if king else "CONTROL(polyomino)"
    Kf = lambda q: denom_series(q, king)
    print(f"\n===================== {tag} =====================")

    # 1. numeric beta vs closed form (independent implementations)
    for qt in ("0.1", "0.3"):
        s = NSolver(Decimal(qt), king=king)
        s.solve_F10()
        d = abs((D1 - s.beta.a) - Kf(Decimal(qt)))
        print(f"  1-beta(NSolver) vs closed denom at q={qt}: |diff| = {d:.2e}")
        assert d < Decimal("1e-95")

    # 2. root
    qc = find_root(Kf, lo, hi)
    mu = D1 / qc
    print(f"  q_c = {qc}")
    print(f"  mu  = {mu}")
    resid = Kf(qc)
    print(f"  |K(q_c)| = {abs(resid):.2e}")

    # 3. no earlier zero on (0, q_c): scan
    bad = []
    for i in range(1, 32):
        qq = qc * Decimal(i) / 32
        v = Kf(qq)
        if v <= 0:
            bad.append((qq, v))
    print(f"  scan (0,q_c) in 31 steps: K>0 everywhere: {not bad}")
    assert not bad

    # 4. full-F pieces at q_c; det scan
    s = NSolver(qc, king=king)
    s.solve_F10()
    c0 = s.assemble(0)
    det0 = s.det
    c1 = s.assemble(1) - c0
    alpha_c = s.alpha.a
    print(f"  alpha(q_c) = {alpha_c:.40f}")
    print(f"  c1(q_c)    = {c1:.40f}")
    print(f"  det(q_c)   = {det0:.40f}")
    dets = []
    for i in range(1, 24):
        qq = qc * Decimal(i + 8) / 32  # 0.28*qc .. ~qc
        ss = NSolver(qq, king=king)
        ss.solve_F10()
        ss.assemble(0)
        dets.append(ss.det)
    ok = all(d > 0 for d in dets) or all(d < 0 for d in dets)
    print(f"  det sign constant on scan up to q_c: {ok} "
          f"(min|det|={min(abs(d) for d in dets):.3e})")
    assert ok and abs(det0) > Decimal("1e-6")

    # 5. derivative and amplitudes
    Kp = dderiv(Kf, qc)
    print(f"  K'(q_c) = {Kp:.40f}")
    A_full = -(c1 * alpha_c) / (Kp * qc)
    A_dir = -(alpha_c) / (Kp * qc)
    print(f"  amplitude A (full)     = {A_full}")
    print(f"  amplitude A (directed) = {A_dir}")

    # 6. numeric-vs-series validation at q=1/10
    q0 = Decimal("0.1")
    s = NSolver(q0, king=king)
    s.solve_F10()
    c0v = s.assemble(0)
    c1v = s.assemble(1) - c0v
    F101 = s.alpha.a / (D1 - s.beta.a)
    Fnum = c0v + c1v * F101
    Fdir = s.F001 + F101
    Sfull = sum(Decimal(a) * q0 ** (n + 1) for n, a in enumerate(seq_full))
    Sdir = sum(Decimal(a) * q0 ** (n + 1) for n, a in enumerate(seq_dir))
    tail = Decimal(seq_full[-1]) * mu * q0 ** 61 / (1 - mu * q0)
    print(f"  F(0.1) numeric vs 60-term series: diff = {Fnum-Sfull:.3e} "
          f"(tail est {tail:.1e})")
    print(f"  Fdir(0.1) numeric vs 60-term series: diff = {Fdir-Sdir:.3e}")
    assert abs(Fnum - Sfull) < Decimal("1e-28")
    assert abs(Fdir - Sdir) < Decimal("1e-28")

    # pole cross-check: (q_c-q)*F near q_c should approach -c1*alpha/K'
    qq = qc - Decimal("1e-12")
    ss = NSolver(qq, king=king)
    ss.solve_F10()
    c0w = ss.assemble(0)
    c1w = ss.assemble(1) - c0w
    Fw = c0w + c1w * ss.alpha.a / (D1 - ss.beta.a)
    lhs = (qc - qq) * Fw
    rhs = -(c1 * alpha_c) / Kp
    print(f"  (q_c-q)F at q_c-1e-12: {lhs:.15f} vs residue {rhs:.15f}")

    # 7. asymptotic confirmation against exact terms
    print("  n   a(n)/(A*mu^n) - 1        [full]      err ratio")
    prev = None
    for n in range(40, 61, 2):
        r = Decimal(seq_full[n - 1]) / (A_full * mu ** n) - 1
        ratio = f"{(r/prev):.4f}" if prev else ""
        print(f"  {n}  {r:+.3e}   {ratio}")
        prev = r
    print("  n   a(n)/(A*mu^n) - 1        [directed]")
    for n in (50, 55, 60):
        r = Decimal(seq_dir[n - 1]) / (A_dir * mu ** n) - 1
        print(f"  {n}  {r:+.3e}")

    # 8. next real zero of the denominator (subdominant candidate)
    grid = [qc + Decimal(i) / 200 for i in range(1, 130)]
    q2 = None
    pv = Kf(grid[0])
    for qq in grid[1:]:
        v = Kf(qq)
        if pv * v < 0:
            q2 = find_root(Kf, qq - Decimal("0.005"), qq, iters=200)
            break
        pv = v
    if q2:
        print(f"  next real zero q_2 = {q2:.30f}; (q_c/q_2) = "
              f"{(qc/q2):.6f}")
    else:
        print("  no further real zero found on scan up to "
              f"{grid[-1]:.3f}")
    return qc, mu, A_full, A_dir


def main():
    seqs = load_terms()
    print("exact terms loaded:", {k: len(v) for k, v in seqs.items()})

    k = analyze(True, seqs["king_full"], seqs["king_directed"],
                "0.28", "0.36")
    p = analyze(False, seqs["poly_full"], seqs["poly_directed"],
                "0.40", "0.48")

    print("\n===================== SUMMARY =====================")
    for tag, (qc, mu, A, Ad) in (("king", k), ("control", p)):
        print(f"{tag}: q_c = {str(qc)[:55]}")
        print(f"{tag}: mu  = {str(mu)[:55]}")
        print(f"{tag}: A_full = {str(A)[:40]}")
        print(f"{tag}: A_dir  = {str(Ad)[:40]}")


if __name__ == "__main__":
    main()
