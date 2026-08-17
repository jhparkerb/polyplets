#!/usr/bin/env python3
"""Session 13: the LOCAL PROFILE RECURSION at the collision, closed form.

Derived by hand from the s08/s12 solve_level operators expanded in the
inner chart s = 2 + delta^2*tau on the slice x = 1/4 (z := tau - 2, so
the kernel-evaluation point sigma+ is tau = -2 i.e. z = -4):

  seeds     psi00_0 = -1/(4 z),  chi_0 = -1/(16 z),  phi_0 = -1/(64 z)
  M00 chain psi00_r = -2r psi00'_{r-1}/z          [=> -(2r)!/(4 z^(2r+1))]
  M10 chain chi_r   = psi00_r/4 + r chi'_{r-1}
  A2M       a_r     = chi_r + 2r phi'_{r-1}
  M11 chain phi_r   = (a_r(z) - a_r(-4)) / (z + 4)   [K11 root at z=-4]
  constant  c_r     = a_r(-4)/2
  channels  D2-channel = chi_r(-4)/2,  I11-channel = r phi'_{r-1}(-4)

(derivations: PK(2+d^2 tau) = d^2, K11(2+d^2 tau) = d^2(tau+2),
D00 = -d^2 z/4, W = 1/2, 1-xs = 1/2, y = 1/4, D = s d/ds -> 2 d^{-2} d/tau,
B[G] = [(G-sG(1))/(s-1) + xsG(1)]/(1-xs), D2[G](sig+) -> 2G(sig+),
M00^(r) = (1-xs)^2 I_M00/D00; all mode-dependent terms (Qcomp, king term
of B, M101, G(1)/G'(1) atoms) enter at subdominant delta-order =>
the recursion is IDENTICAL for king and polyomino).

Equivalent Borel form (z^-(j+1) <-> t^j/j!, so d/dz <-> *(-t),
division (a(z)-a(-4))/(z+4) <-> unique polynomial solution of
Phi' + 4Phi = A, and a(-4) = -A-primitive boundary value = -Phi(0)):

  X_0 = -1/16,   X_r = -t^(2r)/16 - r t X_{r-1}
  Phi_r = (4+D)^{-1} [ X_r - 2r t Phi_{r-1} ],   Phi_0 = -1/64
  c_r = -Phi_r(0)/2

CHECKS in this script (all exact rationals):
  C1  z-form recursion: c_r == (r!)^2/2^(r+7) for r <= RMAX
  C2  channel constants r=1..4 == s12 banked (3,1)/1024,(17,15)/4096,
      (423,729)/32768,(4617,13815)/65536
  C3  Borel form == z-form (chi_r <-> X_r, phi_r <-> Phi_r coefficientwise)
      and c_r == -Phi_r(0)/2
  C4  profile match vs the s13 chassis extraction receipts
      (out_s13_tau_profiles.json): inner profiles of M10, M11 at every
      r <= 6, BOTH modes, both primes (mod-p comparison of the rational
      functions chi_r, phi_r against the chart tables)
  C5  d_r law: M11'(1) leading coeff should be 2c_r -- reported as the
      internal identity a_r(-2)... a_r(-4) = 2c_r (definitionally) plus
      the removability of z=-4 in phi_r (asserted by construction).

Output: out_s13_local_recursion.txt; Phi_r polynomials printed for
closed-form identification.
"""
import os, json, sys
from fractions import Fraction as Fr
from math import factorial, comb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 24
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


# ---- Laurent-in-1/z rational profiles: dict m -> coeff of z^-m (m>=1) ---
def dz(a):
    return {m + 1: -m * c for m, c in a.items()}


def ev(a, z):
    return sum(c * Fr(1, z ** m) for m, c in a.items())


def add(*As):
    r = {}
    for a in As:
        for m, c in a.items():
            r[m] = r.get(m, Fr(0)) + c
    return {m: c for m, c in r.items() if c}


def scal(a, k):
    return {m: k * c for m, c in a.items()}


def divz4(a):
    """g = (a(z) - a(-4))/(z+4) for Laurent-poly a; asserts termination."""
    av = ev(a, -4)
    M = max(a) if a else 0
    g = {1: -av}
    for k in range(1, M + 1):
        g[k + 1] = a.get(k, Fr(0)) - 4 * g.get(k, Fr(0))
    assert g.get(M + 1, Fr(0)) == 0, "divz4: non-terminating"
    g.pop(M + 1, None)
    return {m: c for m, c in g.items() if c}


# ---- Part 1: z-form recursion ------------------------------------------
say(f"== C1/C2: z-form local recursion, r <= {RMAX} ==")
chi = {1: Fr(-1, 16)}
phi = {1: Fr(-1, 64)}
BANKED = {1: (Fr(3, 1024), Fr(1, 1024)), 2: (Fr(17, 4096), Fr(15, 4096)),
          3: (Fr(423, 32768), Fr(729, 32768)),
          4: (Fr(4617, 65536), Fr(13815, 65536))}
c1ok = c2ok = True
chis = {0: chi}
phis = {0: phi}
c_list = {0: ev(chi, -4) / 2}
ok0 = (c_list[0] == Fr(1, 128))
say(f"  r=0: c_0 = {c_list[0]} want 1/128 {'OK' if ok0 else 'FAIL'}")
c1ok &= ok0
for r in range(1, RMAX + 1):
    psi = {2 * r + 1: Fr(-factorial(2 * r), 4)}
    chi = add(scal(psi, Fr(1, 4)), scal(dz(chis[r - 1]), r))
    a = add(chi, scal(dz(phis[r - 1]), 2 * r))
    cr = ev(a, -4) / 2
    phi = divz4(a)
    chis[r], phis[r], c_list[r] = chi, phi, cr
    want = Fr(factorial(r) ** 2, 2 ** (r + 7))
    ok = (cr == want)
    c1ok &= ok
    line = f"  r={r}: c_r = {cr} want (r!)^2/2^(r+7) {'OK' if ok else 'FAIL'}"
    if r in BANKED:
        d2c = ev(chi, -4) / 2
        i11c = r * ev(dz(phis[r - 1]), -4)
        okb = (d2c, i11c) == BANKED[r]
        c2ok &= okb
        line += (f"  channels D2={d2c} I11={i11c} "
                 f"{'OK(banked)' if okb else 'FAIL vs banked'}")
    say(line)
say(f"C1 (c_r law, r<={RMAX}): {'PASS' if c1ok else 'FAIL'}")
say(f"C2 (s12 banked channel split r=1..4): {'PASS' if c2ok else 'FAIL'}")

# ---- Part 2: Borel form -------------------------------------------------
say(f"\n== C3: Borel polynomial form ==")


def pdiff(p):
    return [i * c for i, c in enumerate(p)][1:]


def padd(a, b, kb=Fr(1)):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else Fr(0)) +
            kb * (b[i] if i < len(b) else Fr(0)) for i in range(n)]


def inv4D(p):
    """unique polynomial solution of Phi' + 4 Phi = p."""
    q = [Fr(0)] * len(p)
    d = list(p)
    k = 0
    while any(d):
        q = padd(q, d, Fr((-1) ** k, 4 ** (k + 1)))
        d = pdiff(d)
        k += 1
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return q


c3ok = True
X = [Fr(-1, 16)]
Phi = inv4D(X)
Phis = {0: Phi}
for r in range(0, RMAX + 1):
    if r > 0:
        X = padd([Fr(0)] * (2 * r) + [Fr(-1, 16)], [Fr(0)] + X, Fr(-r))
        A = padd(X, [Fr(0)] + Phis[r - 1], Fr(-2 * r))
        Phi = inv4D(A)
        Phis[r] = Phi
    # equivalence with z-form: chi_r(z) = sum_j X[j] j! z^-(j+1)
    zchi = {j + 1: X[j] * factorial(j) for j in range(len(X)) if X[j]}
    zphi = {j + 1: Phi[j] * factorial(j) for j in range(len(Phi)) if Phi[j]}
    okc = (zchi == chis[r])
    okp = (zphi == phis[r])
    okv = (-Phi[0] / 2 == c_list[r])
    c3ok &= okc and okp and okv
    if r <= 6 or not (okc and okp and okv):
        say(f"  r={r}: chi<->X {'OK' if okc else 'FAIL'} "
            f"phi<->Phi {'OK' if okp else 'FAIL'} "
            f"c_r=-Phi_r(0)/2 {'OK' if okv else 'FAIL'}")
say(f"C3 (Borel form equivalent, r<={RMAX}): {'PASS' if c3ok else 'FAIL'}")
say("\nPhi_r polynomials (coeff list, t^0 first), for identification:")
for r in range(min(8, RMAX) + 1):
    say(f"  Phi_{r} = {Phis[r]}")
    n = [c * Fr(-64) for c in Phis[r]]
    say(f"    -64*Phi_{r} = {n}")

# ---- Part 2b: C6 closed-form solution of the recursion ------------------
say(f"\n== C6: closed form Phi_r == [w^r] -(1/64) e^(t^2 w) * "
    f"sum_k k! w^k / (2^k (1+tw)^(2k+2)) ==")
c6ok = True
for r in range(RMAX + 1):
    hat = {}
    for k in range(r + 1):
        for m in range(r - k + 1):
            i = r - k - m
            coef = (Fr(-1, 64) * Fr(factorial(k), 2 ** k)
                    * comb(2 * k + 1 + m, m) * (-1) ** m
                    * Fr(factorial(r), factorial(i)))
            d = m + 2 * i
            hat[d] = hat.get(d, Fr(0)) + coef
    lst = [hat.get(d, Fr(0)) for d in range(max(hat) + 1)]
    while len(lst) > 1 and lst[-1] == 0:
        lst.pop()
    ok = (lst == Phis[r])
    c6ok &= ok
    if r <= 3 or not ok:
        say(f"  r={r}: {'OK' if ok else 'FAIL'}")
say(f"C6 (closed-form solution, r<={RMAX}): {'PASS' if c6ok else 'FAIL'}")

# ---- Part 3: C4 profile match vs chassis receipts -----------------------
say(f"\n== C4: inner profiles vs chassis extraction ==")
fn = os.path.join(ROOT, os.environ.get("S13_PROFILE_JSON",
                                       "out_s13_tau_profiles.json"))
if not os.path.exists(fn):
    say("  SKIP: no out_s13_tau_profiles.json yet")
    c4ok = None
else:
    data = json.load(open(fn))
    c4ok = True
    for mode in data:
        for pstr in data[mode]:
            p = int(pstr)
            for rstr in sorted(data[mode][pstr], key=int):
                r = int(rstr)
                if r not in chis:
                    continue
                for ph, prof in (("M10", chis[r]), ("M11", phis[r])):
                    rec = data[mode][pstr][rstr][ph]
                    inn = rec["inn"]
                    if inn is None:
                        continue
                    # chassis inner form: num_rows[0] at delta^num_m over
                    # den = prod atoms (name,e,am,row): reconstruct the
                    # rational function of T at leading order mod p and
                    # compare with prof (in z = T - 2) as poly identity:
                    # prof = N(T)/D(T) <=> N(T) - prof*D(T) == 0.
                    # prof has poles only at z=0 (T=2): clear z^Mmax.
                    Mmax = max(prof)
                    num = inn["num_rows"][0]
                    if any(v == "PREC" for v in num.values()):
                        say(f"  [{mode} p={p} r={r} {ph}] PREC in num; skip")
                        continue
                    # denominator polynomial in T mod p
                    denp = [1]
                    for nm, e, am, row in inn["den"]:
                        if any(v == "PREC" for v in row.values()):
                            denp = None
                            break
                        js = sorted(int(j) for j in row)
                        ap = [0] * (max(js) + 1)
                        for j in js:
                            ap[int(j)] = row[str(j)] % p
                        for _ in range(e):
                            new = [0] * (len(denp) + len(ap) - 1)
                            for i, ci in enumerate(denp):
                                for j2, cj in enumerate(ap):
                                    new[i + j2] = (new[i + j2] + ci * cj) % p
                            denp = new
                    if denp is None:
                        say(f"  [{mode} p={p} r={r} {ph}] PREC in den; skip")
                        continue
                    nump = [0] * (max(int(j) for j in num) + 1 if num else 1)
                    for j, v in num.items():
                        nump[int(j)] = v % p
                    # prof*z^Mmax as polynomial in z, then in T = z+2:
                    pz = [0] * (Mmax + 1)
                    for m, c in prof.items():
                        pz[Mmax - m] = (c.numerator *
                                        pow(c.denominator, p - 2, p)) % p
                    # N(T)*z^Mmax - P(z(T))*D(T) == 0 as poly in T
                    # z = T-2: build z^Mmax and P(z) in T by Horner/shift
                    def shift(poly):    # p(z) -> p(T-2) coeffs in T
                        out = [0] * len(poly)
                        for c in reversed(poly):
                            # out = out*(T-2) + c
                            new = [0] * (len(out) + 1)
                            for i, ci in enumerate(out):
                                new[i + 1] = (new[i + 1] + ci) % p
                                new[i] = (new[i] - 2 * ci) % p
                            new[0] = (new[0] + c) % p
                            out = new[:max(len(poly), len(new))]
                            while len(out) > 1 and out[-1] == 0 and \
                                    len(out) > len(poly):
                                out.pop()
                        return out
                    zM = shift([0] * Mmax + [1])
                    PT = shift(pz)
                    L = max(len(nump) + len(zM), len(PT) + len(denp)) - 1
                    lhs = [0] * L
                    for i, ci in enumerate(nump):
                        for j2, cj in enumerate(zM):
                            lhs[i + j2] = (lhs[i + j2] + ci * cj) % p
                    for i, ci in enumerate(PT):
                        for j2, cj in enumerate(denp):
                            lhs[i + j2] = (lhs[i + j2] - ci * cj) % p
                    ok = all(c % p == 0 for c in lhs)
                    c4ok &= ok
                    if not ok:
                        say(f"  [{mode} p={p} r={r} {ph}] PROFILE MISMATCH")
            say(f"  [{mode} p={p}] r<=  checked")
    say(f"C4 (chassis profile match): "
        f"{'PASS' if c4ok else 'FAIL' if c4ok is not None else 'SKIP'}")

with open(os.path.join(ROOT, "out_s13_local_recursion.txt"), "w") as fp:
    fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
say("receipt: out_s13_local_recursion.txt")
