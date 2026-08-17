#!/usr/bin/env python3
"""s10: CERTIFIED enclosures of the amplitude constants of the area
statistic on convex king animals (+ polyomino control).

Target quantities (s05 residue formulas, s04 Temperley solution):
    A      = -c1(q_c) * alpha(q_c) / (K'(q_c) * q_c)   [full family]
    A_dir  = -alpha(q_c) / (K'(q_c) * q_c)             [directed subfamily]
where q_c is the smallest positive zero of K (king) / J (control), and
alpha, c1 are the analytic q-series of F(1,1,q) = c0 + c1*alpha/K.

Rigor chain, ALL arithmetic exact rational (fractions.Fraction):

[M] March (s06 machinery, generalized to both modes): alternating-term
    bracketing of K/J valid on (0,QV]; left lemma K>=S_1>0 on (0,QL];
    Lipschitz bound L >= sup|K'| on [QL,QHI]; exact Lipschitz march
    certifies K>0 on (0,a_f]; then K(b_f)<0 certified => q_c in (a_f,b_f].
    King: QV,QL,QHI = .34,.29,.33 (s06 rerun).  Control: .45,.38,.44 (NEW):
      - term-ratio validity: t_{m+1}/t_m <= q^2/(1-q^2)^2 (m>=1), <1 at .45;
      - left lemma: J >= S_1 = (1-3q+q^2)/(1-q)^2 > 0 at q=.38 (poly
        decreasing on [0,1], value 44/10000 > 0 exact).

[I] Interval arithmetic: endpoints Fraction, every op outward-rounded to
    the grid Z/10^90 (rounding only widens => enclosure preserved).
    Dual intervals (a,b) track (value, d/ds at s=1) of the catalytic
    variable; mag(u):=sup|a|+sup|b| is submultiplicative.

[T] Tail bounds (b := q_hi rounded up, c := 1/(1-b), I1 := c+b*c^2,
    V := 1/Pinf_lb^2 with Pinf_lb an exact lower bound on (b;b)_inf,
    CP := V(1+2bc^2)):
    - mag((1-w_k)^{-1}), mag((w_k-1)^{-1}) <= I1 for k>=1 (w_k=(q^k,q^k));
    - any product prod(1-w_j)^{-2} over distinct j>=1: value <= V, dual
      part = value * sum_j 2q^j/(1-q^j) <= 2Vbc^2, so mag <= CP;
    - F00(m) tail after N terms: term_n = w*(1-w)^{-1}*prod, so
      mag(t_n) <= 2 I1 CP b^{m+n+1}; tail <= 2 I1 CP b^{m+N+1}/(1-b);
      uniform bound CF00 := 2 I1 CP b/(1-b) >= mag(F00(m)) all m>=0;
    - mag(R(w_j)) <= 2 b^j I1^2, mag(V1(w_j)) <= 4 b^{2j} I1^2 (decreasing
      in j) => alpha/beta/F10/P/Q1/Q2 tails are geometric with ratio
      rho = (first omitted factor bound) < 1: tail <= mag(prod_N)*C/(1-rho)
      with C a uniform mag bound on the non-product factor (CA1, CT, CA2,
      CV1, CV2 below), since interval mags are submultiplicative;
    - CA1 >= mag(A1(t)): (CF00+2b*CF00)I1^2 [+ 2b*CF00*I1 king term];
      CT >= mag(T): (4b^2+4b)I1^2 king / 2b*I1^2 control;
      CF10 >= mag(F10(t)), t>=1: (CA1+CT)*S, S >= sum_n prod_{j<=n} 2b^{1+j}I1^2
      (computed with geometric tail, factors decreasing and <1/2 at cutoff);
      CD1, CD2, CA2 assembled from the D1F00/D2F10 formulas with |F101|<=1,
      mag(F10p1) <= mag(alpha)+mag(beta) (computed intervals).
    - K' via q-duals (seed (Q,1)): termwise to m<=40; tails from s06 [R3]:
      t_m <= taucap*q^{T_m} (taucap=F/Pinf_lb^2, F=2 king / 1 control),
      |t_m'| <= t_m*B_m, B_m <= beta(m) := m + T_m/q_lo + 2/(1-b)^3;
      successive-ratio sigma = 3b^{41} < 1/2 => tails <= 2*taucap*b^{T_41}
      (value) and *beta(41) (derivative).

Outputs: certified enclosures of alpha, c1, det, K', residue -c1*alpha/K',
A, A_dir for both modes; digit prefixes; containment checks vs s05 banked
values and (control) Kotesovec's published constants in OEIS A067675.
"""
from fractions import Fraction as Fr
import sys, time

# ---------------------------------------------------------------- intervals
DEN = 10**90

def _rd(x):
    return Fr((x.numerator*DEN)//x.denominator, DEN)

def _ru(x):
    return Fr(-((-x.numerator*DEN)//x.denominator), DEN)

class Iv:
    __slots__ = ("lo","hi")
    def __init__(self, lo, hi=None, raw=False):
        if hi is None: hi = lo
        if not isinstance(lo, Fr): lo = Fr(lo)
        if not isinstance(hi, Fr): hi = Fr(hi)
        if not raw:
            lo = _rd(lo); hi = _ru(hi)
        assert lo <= hi
        self.lo = lo; self.hi = hi
    @staticmethod
    def lift(v):
        return v if isinstance(v, Iv) else Iv(v)
    def __add__(s, o):
        o = Iv.lift(o); return Iv(s.lo+o.lo, s.hi+o.hi)
    __radd__ = __add__
    def __sub__(s, o):
        o = Iv.lift(o); return Iv(s.lo-o.hi, s.hi-o.lo)
    def __rsub__(s, o):
        return Iv.lift(o) - s
    def __neg__(s):
        return Iv(-s.hi, -s.lo, raw=True)
    def __mul__(s, o):
        o = Iv.lift(o)
        p = (s.lo*o.lo, s.lo*o.hi, s.hi*o.lo, s.hi*o.hi)
        return Iv(min(p), max(p))
    __rmul__ = __mul__
    def inv(s):
        assert s.lo > 0 or s.hi < 0, ("interval contains 0", float(s.lo), float(s.hi))
        return Iv(Fr(1)/s.hi, Fr(1)/s.lo)
    def mag(s):
        return max(abs(s.lo), abs(s.hi))
    def contains0(s):
        return s.lo <= 0 <= s.hi
    def width(s):
        return s.hi - s.lo

IV0 = Iv(0); IV1 = Iv(1)

class Dv:
    """dual interval: value + d/ds component, s the catalytic variable."""
    __slots__ = ("a","b")
    def __init__(s, a, b=None):
        s.a = Iv.lift(a); s.b = IV0 if b is None else Iv.lift(b)
    @staticmethod
    def lift(v):
        return v if isinstance(v, Dv) else Dv(Iv.lift(v))
    def __add__(s, o):
        o = Dv.lift(o); return Dv(s.a+o.a, s.b+o.b)
    __radd__ = __add__
    def __sub__(s, o):
        o = Dv.lift(o); return Dv(s.a-o.a, s.b-o.b)
    def __rsub__(s, o):
        return Dv.lift(o) - s
    def __neg__(s):
        return Dv(-s.a, -s.b)
    def __mul__(s, o):
        o = Dv.lift(o); return Dv(s.a*o.a, s.a*o.b + s.b*o.a)
    __rmul__ = __mul__
    def inv(s):
        ia = s.a.inv()
        return Dv(ia, -(s.b*ia*ia))
    def mag(s):
        return s.a.mag() + s.b.mag()
    def pad(s, T):
        t = Iv(-T, T)
        return Dv(s.a+t, s.b+t)

DV1 = Dv(IV1)

# ---------------------------------------------------------------- march [M]
def dec(fr, ndig):
    sign = "-" if fr < 0 else ""
    fr = abs(fr)
    num, den = fr.numerator, fr.denominator
    ip = num // den; rem = num - ip*den
    digs = []
    for _ in range(ndig):
        rem *= 10; d = rem // den; rem -= d*den; digs.append(str(d))
    return "%s%d.%s" % (sign, ip, "".join(digs))

def march(king):
    """certified bracket (a_f, b_f] for the smallest positive zero of K/J."""
    tag = "KING" if king else "CONTROL"
    if king:
        QV, QL, QHI, NTERM = Fr(34,100), Fr(29,100), Fr(33,100), 26
    else:
        QV, QL, QHI, NTERM = Fr(45,100), Fr(38,100), Fr(44,100), 22
    NL = 30
    print(f"\n----- [{tag}] march for q_c -----")

    def terms(q, N):
        t = []; poch2 = Fr(1); qm = Fr(1); qT = Fr(1)
        for m in range(N+1):
            if m > 0:
                qm *= q; qT *= qm; poch2 *= (1-qm)**2
            f = (2-qm) if king else Fr(1)
            t.append(f*qT/poch2)
        return t

    def bracket_K(q, N=NTERM):
        assert Fr(0) < q <= QV
        t = terms(q, N+1)
        for m in range(1, N+1):
            assert t[m] >= t[m+1], (float(q), m)
        S = Fr(0); brackets = []
        for m in range(N+1):
            S += t[m] if m % 2 == 0 else -t[m]
            if m >= 1: brackets.append(S)
        return min(brackets[-2:]), max(brackets[-2:])

    # [R1] term-ratio validity at QV
    if king:
        r = 2*QV*QV / ((2-QV)*(1-QV*QV)**2)
    else:
        r = QV*QV/(1-QV*QV)**2
    assert r < 1
    print(f"[R1] ratio bound r({float(QV)}) = {float(r):.6f} < 1")

    # [R2] left lemma at QL (polys decreasing on [0,1])
    v = (1 - 4*QL + 2*QL*QL) if king else (1 - 3*QL + QL*QL)
    assert v > 0
    print(f"[R2] S_1 numerator at q={float(QL)}: {v} > 0  => K>0 on (0,{float(QL)}]")

    # [R3] Lipschitz bound on [QL,QHI]
    P = Fr(1); qj = Fr(1)
    for j in range(1, 41):
        qj *= QHI; P *= (1-qj)
    Pinf_lb = P * (1 - QHI**41/(1-QHI))
    assert Pinf_lb > 0
    F = 2 if king else 1
    taucap = Fr(F)/Pinf_lb**2
    L = Fr(0); poch2 = Fr(1); qm = Fr(1); qT = Fr(1); sj = Fr(0)
    for m in range(NL+1):
        if m > 0:
            qm *= QHI; qT *= qm; poch2 *= (1-qm)**2
            sj += m*qm/QHI/(1-qm)
        Tm = Fr(m*(m+1),2)
        f = (2-qm) if king else Fr(1)
        tau_m = f*qT/poch2
        B_m = (m*qm/QHI/(2-qm) if m>0 else Fr(0)) + Tm/QL + 2*sj
        L += tau_m*B_m
    sigma = 3*QHI**(NL+1)
    assert sigma < Fr(1,2)
    TmN = Fr((NL+1)*(NL+2),2)
    beta = (NL+1) + TmN/QL + 2/(1-QHI)**3
    L += 2*taucap*QHI**TmN*beta
    print(f"[R3] certified Lipschitz bound L = {float(L):.6f} on [{float(QL)},{float(QHI)}]")

    # [R4] march
    t0 = time.time(); x = QL; it = 0
    SCALE = 10**50
    while True:
        lo, hi = bracket_K(x)
        assert lo > 0, ("march hit nonpositive lower bracket", float(x))
        step = lo/L*Fr(999999,1000000)
        if step < Fr(1, 10**46):
            break
        xn = x + step
        x = Fr((xn*SCALE).__floor__(), SCALE)
        assert x <= QHI, "march left the Lipschitz window"
        it += 1
        if it % 100 == 0:
            print("   march it=%d  x=%.20f  step~%.3e  (%.1fs)" %
                  (it, float(x), float(step), time.time()-t0))
        assert it < 20000
    a_f = x
    print(f"[R4] march done: {it} steps, {time.time()-t0:.1f}s; K>0 on (0,a_f]")
    delta = Fr(1, 10**46); b_f = None
    for j in range(1, 200):
        cand = a_f + delta
        lo, hi = bracket_K(cand)
        if hi < 0:
            b_f = cand; break
        delta *= 2
    assert b_f is not None and b_f <= QHI
    print(f"[R4] K(b_f)<0 certified; width = {float(b_f-a_f):.3e}")
    print(f"  a_f = {dec(a_f,48)}")
    print(f"  b_f = {dec(b_f,48)}")
    return a_f, b_f

# ------------------------------------------------------- q-series solver [T]
def ru6(x):
    return Fr(-((-x.numerator*10**6)//x.denominator), 10**6)

class CertSolver:
    def __init__(self, a_f, b_f, king):
        self.king = king
        self.Q = Iv(a_f, b_f, raw=True)
        self.qlo = a_f
        b = ru6(Fr(b_f)); self.bU = b
        MAXP = 260
        self.qp = [IV1]
        for m in range(1, MAXP+1):
            self.qp.append(self.qp[-1]*self.Q)
        self._f00 = {}; self._f10 = {}
        # tail constants
        c = 1/(1-b); self.c = c
        I1 = c + b*c*c; self.I1 = I1
        P = Fr(1); bj = Fr(1)
        for j in range(1, 61):
            bj *= b; P *= (1-bj)
        Plb = P*(1 - b**61/(1-b))
        assert Plb > 0
        self.Plb = Plb
        V = 1/Plb**2
        CP = V*(1 + 2*b*c*c)
        self.V, self.CP = V, CP
        self.CF00 = 2*I1*CP*b/(1-b)
        if king:
            self.CA1 = (self.CF00 + 2*b*self.CF00)*I1*I1 + 2*b*self.CF00*I1
            self.CT  = (4*b*b + 4*b)*I1*I1
        else:
            self.CA1 = (self.CF00 + 2*b*self.CF00)*I1*I1
            self.CT  = 2*b*I1*I1
        # S >= sum_n prod_{j=1..n} (2 b^{1+j} I1^2), for CF10 (t>=1 uniform)
        S = Fr(0); pr = Fr(1); n = 0
        while True:
            S += pr
            n += 1
            f = 2*b**(1+n)*I1*I1
            pr *= f
            if f < Fr(1,2) and pr < Fr(1, 10**40):
                S += 2*pr
                break
            assert n < 500
        self.CF10 = (self.CA1 + self.CT)*S
        self.NF00 = 200   # F00(m) uses N = max(20, NF00-m) terms
        self.NAB  = 32
        self.NF10 = 28
        self.NP   = 26

    def w(self, m):
        p = self.qp[m]
        return Dv(p, p)

    def F00(self, m):
        if m in self._f00:
            return self._f00[m]
        N = max(20, self.NF00 - m)
        acc = Dv(IV0); prod = DV1
        for n in range(N):
            z = self.w(m+n+1)
            i1 = (1 - z).inv()
            acc = acc + z*prod*i1
            prod = prod*i1*i1
        tail = 2*self.I1*self.CP*self.bU**(m+N+1)/(1-self.bU)
        acc = acc.pad(tail)
        self._f00[m] = acc
        return acc

    def R(self, m):
        z = self.w(m)
        return z*(z-1).inv()*(1-z).inv()

    def T(self, m):
        z = self.w(m)
        base = (z-1).inv()*(1-z).inv()
        if self.king:
            return (z*(z-1) - z)*base
        return -z*base

    def A1(self, t):
        z = self.w(t+1)
        core = (self.F00(t+1) - z*self.F001)*(z-1).inv()*(1-z).inv()
        if self.king:
            core = core + z*self.F001*(1-z).inv()
        return core

    def solve_F10(self):
        f0 = self.F00(0)
        self.F001, self.F00p1 = f0.a, f0.b
        alpha = Dv(IV0); beta = Dv(IV0); prod = DV1
        for n in range(self.NAB):
            alpha = alpha + prod*self.A1(n)
            beta = beta + prod*self.T(n+1)
            prod = prod*self.R(n+1)
        rho = 2*self.bU**(self.NAB+1)*self.I1**2
        assert rho < 1
        pm = prod.mag()
        self.alpha = alpha.pad(pm*self.CA1/(1-rho))
        self.beta  = beta.pad(pm*self.CT/(1-rho))
        # F10p1 mag bound for CA2 (|F101|<=1)
        self.CF10p = self.alpha.mag() + self.beta.mag()
        b, I1 = self.bU, self.I1
        CD1 = (self.CF00 + 4*b*b*self.CF00 + 2*b*(1+2*b)*3*self.CF00)*I1*I1
        CD2 = (4*b*b*self.CF10 + 4*b*b + 2*b*(1+2*b)*self.CF10p)*I1*I1 \
              + 2*b*(self.CF10+1)*I1
        self.CA2 = CD1 + 2*CD2

    def F10(self, t):
        if t in self._f10:
            return self._f10[t]
        acc = Dv(IV0); prod = DV1
        for n in range(self.NF10):
            acc = acc + prod*(self.A1(t+n) + self.T(t+n+1)*self.F101)
            prod = prod*self.R(t+n+1)
        rho = 2*self.bU**(t+self.NF10+1)*self.I1**2
        assert rho < 1
        acc = acc.pad(prod.mag()*(self.CA1+self.CT)/(1-rho))
        self._f10[t] = acc
        return acc

    def D1F00(self, t):
        z = self.w(t+1); iz1 = (z-1).inv()
        return (self.F00(t+1) - z*z*self.F001
                - z*(z-1)*(self.F00p1 - 2*self.F001))*iz1*iz1

    def D2F10(self, t):
        z = self.w(t+1); iz1 = (z-1).inv()
        Gz = self.F10(t+1)
        L = (z*z*Gz - z*z*self.F101 - z*(z-1)*self.F10p1)*iz1*iz1
        return L - z*(Gz - self.F101)*iz1

    def A2(self, t):
        return self.D1F00(t) + 2*self.D2F10(t)

    def solve_F11(self):
        P = Dv(IV0); Q1 = Dv(IV0); Q2 = Dv(IV0); prod = DV1
        for n in range(self.NP):
            z = self.w(n+1); iz1 = (z-1).inv()
            V1 = z*z*iz1*iz1; V2 = z*iz1
            P = P + prod*self.A2(n)
            Q1 = Q1 + prod*V1
            Q2 = Q2 + prod*V2
            prod = prod*V1
        b, I1 = self.bU, self.I1
        rho = 4*b**(2*(self.NP+1))*I1*I1
        assert rho < 1
        pm = prod.mag()
        CV1 = 4*b**(2*(self.NP+1))*I1*I1
        CV2 = 2*b**(self.NP+1)*I1
        P = P.pad(pm*self.CA2/(1-rho))
        Q1 = Q1.pad(pm*CV1/(1-rho))
        Q2 = Q2.pad(pm*CV2/(1-rho))
        a11 = Q1.a + 1; a12 = Q2.a; r1 = P.a
        a21 = Q1.b; a22 = Q2.b + 1; r2 = P.b
        det = a11*a22 - a12*a21
        assert not det.contains0()
        self.det = det
        self.F111 = (r1*a22 - a12*r2)*det.inv()

    def assemble(self, f101):
        self.F101 = f101
        self.F10p1 = self.alpha.b + self.beta.b*f101
        self._f10 = {}
        self.solve_F11()
        return self.F001 + 2*f101 + self.F111

def kprime(a_f, b_f, king, qp, NM=40):
    """dual-in-q enclosure of (K(q), K'(q)) over q in [a_f,b_f]."""
    Q = Iv(a_f, b_f, raw=True)
    qd = Dv(Q, IV1)
    qm = DV1; qT = DV1; poch2 = DV1
    tot = Dv(IV0)
    for m in range(NM+1):
        if m:
            qm = qm*qd; qT = qT*qm
            f = 1 - qm
            poch2 = poch2*f*f
        term = qT*poch2.inv()
        if king:
            term = (2 - qm)*term
        tot = (tot + term) if m % 2 == 0 else (tot - term)
    b = ru6(Fr(b_f))
    P = Fr(1); bj = Fr(1)
    for j in range(1, 61):
        bj *= b; P *= (1-bj)
    Plb = P*(1 - b**61/(1-b)); assert Plb > 0
    taucap = Fr(2 if king else 1)/Plb**2
    sigma = 3*b**(NM+1); assert sigma < Fr(1,2)
    TmN = (NM+1)*(NM+2)//2
    beta = (NM+1) + Fr(TmN)/Fr(a_f) + 2/(1-b)**3
    tail_val = 2*taucap*b**TmN
    tail_der = tail_val*beta
    return Dv(tot.a + Iv(-tail_val, tail_val), tot.b + Iv(-tail_der, tail_der))

# ---------------------------------------------------------------- reporting
def show(name, iv, nd=55):
    lo, hi = dec(iv.lo, nd), dec(iv.hi, nd)
    pref = 0
    for c1_, c2_ in zip(lo, hi):
        if c1_ == c2_: pref += 1
        else: break
    print(f"  {name}: [{lo},")
    print(f"  {' '*len(name)}   {hi}]")
    print(f"  {' '*len(name)}  certified prefix: {lo[:pref]}  ({pref} chars, width {float(iv.width()):.2e})")
    return lo[:pref]

def contains_decimal(iv, s):
    """does the enclosure intersect [v-ulp, v+ulp]? (banked digits may be
    truncated or rounded at the last place)"""
    v = Fr(s)
    ulp = Fr(1, 10**(len(s.split('.')[1].lstrip('-'))))
    return iv.lo <= v + ulp and v - ulp <= iv.hi

S05 = {
 True: dict(alpha="0.5114252387864446468287030907410268638982",
            c1="2.5954038468208004387979002255652372135233",
            det="0.5819349775941028280377065774205423095839",
            Kp="-4.2621059691523816006465243873642055378879",
            A="0.97445221313500464915132942086024332742538445801511603159338928033365080770674763415213812142916812547011232703",
            Adir="0.37545302027992473174348924381907282070710016721066507440757008078575922324097992412983106583117984354597640356"),
 False: dict(alpha="1.0752421413407181242032795712898072148120",
            c1="4.4306456570765369530418187082243531429511",
            det="0.3974367737798422541009534679292569073961",
            Kp="-3.7679068890847522987817323393030456464573",
            A="2.9195985097136070553847095156513356859151689414730565863067926897718594239726370933605703001017643742005777693",
            Adir="0.65895554185211895992099818790088342084923176241464006269910575358978406271543723231144854626710388645214141796"),
}
KOTESOVEC_A  = "2.91959850971360705538470951565133568591516894147305658630679268977185942"
KOTESOVEC_MU = "2.3091385933304947310987203050172125319118144725816284016944029002844564407483"

def amplitude_phase(a_f, b_f, king):
    tag = "KING" if king else "CONTROL"
    print(f"\n----- [{tag}] certified amplitude phase on q_c-bracket -----")
    t0 = time.time()
    S = CertSolver(a_f, b_f, king)
    print(f"  tail constants: CF00={float(S.CF00):.3g} CA1={float(S.CA1):.3g} "
          f"CT={float(S.CT):.3g} CF10={float(S.CF10):.3g}")
    S.solve_F10()
    print(f"  CA2={float(S.CA2):.3g}  (alpha/beta solved, {time.time()-t0:.1f}s)")
    c0 = S.assemble(0)
    det = S.det
    c1v = S.assemble(1) - c0
    alpha = S.alpha.a
    KP = kprime(a_f, b_f, king, S.qp)
    print(f"  series phase done ({time.time()-t0:.1f}s)")
    assert KP.a.contains0(), "K(q_c-interval) must contain 0"
    Kp = KP.b
    assert not Kp.contains0()
    Q = Iv(a_f, b_f, raw=True)
    res = -(c1v*alpha)*Kp.inv()          # pole residue -c1*alpha/K'
    Af  = res*Q.inv()
    Ad  = -alpha*(Kp*Q).inv()
    print(f"  [sanity] K-value enclosure contains 0: width {float(KP.a.width()):.2e}")
    out = {}
    for nm, iv in (("alpha", alpha), ("c1", c1v), ("det", det), ("Kp", Kp),
                   ("residue", res), ("A", Af), ("Adir", Ad)):
        out[nm] = iv
        show(nm, iv)
    # certified sign facts
    assert not (c1v*alpha).contains0(), "residue numerator must exclude 0"
    print("  CERTIFIED: K'(q_c) != 0 (simple zero), c1(q_c)*alpha(q_c) != 0,")
    print("             det(q_c) != 0  => F(1,1,q) has a SIMPLE POLE at q_c")
    # containment vs banked s05 values
    for nm in ("alpha","c1","det","Kp","A","Adir"):
        ok = contains_decimal(out[nm], S05[king][nm])
        print(f"  s05 banked {nm}: containment {'OK' if ok else 'FAIL'}")
        assert ok, (tag, nm)
    if not king:
        okA  = contains_decimal(out["A"], KOTESOVEC_A)
        okmu = True  # mu checked in march section by caller
        print(f"  Kotesovec A067675 amplitude containment: {'OK' if okA else 'FAIL'}")
        assert okA
    return out

def main():
    print("s10: certified amplitude constants (exact rational interval arithmetic)")
    print("grid: Z/10^%d; all tail bounds per docstring" % 90)
    results = {}
    for king in (True, False):
        a_f, b_f = march(king)
        mu_lo, mu_hi = Fr(1)/Fr(b_f), Fr(1)/Fr(a_f)
        print(f"  mu in [{dec(mu_lo,48)},")
        print(f"         {dec(mu_hi,48)}]")
        if not king:
            v = Fr(KOTESOVEC_MU); ulp = Fr(1, 10**76)
            ok = mu_lo <= v + ulp and v <= mu_hi
            print(f"  Kotesovec/A276994 growth-constant containment: {'OK' if ok else 'FAIL'}")
            assert ok
        results[king] = amplitude_phase(a_f, b_f, king)
    print("\nALL CHECKS PASSED")

if __name__ == "__main__":
    main()
