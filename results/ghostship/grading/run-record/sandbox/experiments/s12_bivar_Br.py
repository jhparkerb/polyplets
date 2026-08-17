#!/usr/bin/env python3
"""Session 11: bivariate area-moment closed forms M_r = (A_r + B_r*sqrt(Delta))
/ (K^(r+1) Delta^(2r+2)) for r = 1,2,3 (king; control has K-power absent),
extracted by modular fit + CRT from the validated r<=4 moment DP
(s07_area_moments_r4.gm_table) over a full WBOX x WBOX exact-box table,
then verified EXACTLY over Z on the full grid, then factored:

  REGISTERED PREDICTION (s10 OPEN 2, written in reports/session-11.md
  before this run): Delta | B_r exactly over Z for r = 2,3 and
      B_r = Delta * x^2y^2 * (1+x+y) * C_r   [king]
      B_r = Delta * 4x^2y^2 * E_r            [control]
  with C_r, E_r symmetric integer polynomials.

r=1 is run first as a CONTROL: the fit must reproduce the banked
out_s07_bivar_moment{,_poly}.json coefficients exactly (independent code
path: new equation builder, I<=J half-grid, new solver invocation).

Method per r and mode:
  1. exact table M_r(w,h), w,h <= WBOX, from the validated DP (exact ints);
  2. mod p in {2^61-1, 9223372036854775783}: fit symmetric unknown pairs
     A:{i<=j, i+j<=6r+8}, B:{i<=j, i+j<=6r+5} against target
     T = M_r * K^(r+1) * Delta^(2r+2) on half-grid cells 0<=I<=J<=WBOX
     (all inputs symmetric; (J,I)-equations are identical);
     require full rank + consistency of every surplus row;
  3. CRT-lift to symmetric range, require |coeff| << p1*p2 (small ints);
  4. EXACT over-Z/Q check: A + B*sqrt(Delta) - M_r*den == 0 at every cell
     of the FULL grid I,J <= WBOX (sqrt(Delta) via Fraction recursion);
  5. exact division ladder on B_r: /Delta, /x^2y^2, /(1+x+y) [king].

Output: out_s12_bivar_Br.txt, out_s12_bivar_Br.json
Usage: python3 experiments/s11_bivar_Br.py [WBOX] [rmax]
"""
import sys, os, json, time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s07_area_moments_r4 as R4

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WBOX = int(sys.argv[1]) if len(sys.argv) > 1 else 30
RMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 3
P1 = (1 << 61) - 1
P2 = 9223372036854775783  # largest prime < 2^63 (s07's choice)

OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


# ---------- exact bivariate series helpers (dicts {(i,j): coeff}) ----------
DELTA = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (1, 1): -2, (0, 2): 1}
KPOL = {(1, 0): 1, (0, 1): 1, (1, 1): 1}


def dmul(u, v, nmax, ring=int):
    w = {}
    for (i1, j1), c1 in u.items():
        if i1 > nmax or j1 > nmax or not c1:
            continue
        for (i2, j2), c2 in v.items():
            I, J = i1 + i2, j1 + j2
            if I <= nmax and J <= nmax and c2:
                w[(I, J)] = w.get((I, J), 0) + c1 * c2
    return {k: c for k, c in w.items() if c}


def den_poly(r, king):
    d = {(0, 0): 1}
    if king:
        for _ in range(r + 1):
            d = dmul(d, KPOL, 10 ** 9)
    for _ in range(2 * r + 2):
        d = dmul(d, DELTA, 10 ** 9)
    return d


def sqrtD_frac(nmax):
    """sqrt(Delta) as bivariate series over Q, grid-truncated at (nmax,nmax):
    solve S^2 = Delta degree by degree (homogeneous total degree).
    Exact for all grid coefficients: any product landing on the grid has
    both factors componentwise <= the target, hence on the grid too."""
    bydeg = {0: {(0, 0): Fr(1)}}
    for d in range(1, 2 * nmax + 1):
        conv = {}
        for t1 in range(1, d):
            t2 = d - t1
            if t1 > t2 or t2 not in bydeg or t1 not in bydeg:
                continue
            mult = 1 if t1 == t2 else 2
            for (i1, j1), c1 in bydeg[t1].items():
                for (i2, j2), c2 in bydeg[t2].items():
                    k = (i1 + i2, j1 + j2)
                    if k[0] <= nmax and k[1] <= nmax:
                        conv[k] = conv.get(k, Fr(0)) + mult * c1 * c2
        lev = {}
        for i in range(d + 1):
            j = d - i
            if i > nmax or j > nmax:
                continue
            rhs = Fr(DELTA.get((i, j), 0)) - conv.get((i, j), Fr(0))
            lev[(i, j)] = rhs / 2
        bydeg[d] = lev
    S = {}
    for lev in bydeg.values():
        for k, c in lev.items():
            if c:
                S[k] = c
    return S


# ---------- modular fit ----------
def solve_mod(rows, rhs, p, nunk):
    """sparse Gaussian elimination mod p (s07_bivar_moment.solve_mod)."""
    m = len(rows)
    A = [dict(rows[i]) for i in range(m)]
    b = rhs[:]
    piv_of_col = {}
    row_used = [False] * m
    for c in range(nunk):
        pr = None
        for i in range(m):
            if not row_used[i] and A[i].get(c, 0) % p != 0:
                pr = i
                break
        if pr is None:
            continue
        row_used[pr] = True
        piv_of_col[c] = pr
        inv = pow(A[pr][c], p - 2, p)
        A[pr] = {k: v * inv % p for k, v in A[pr].items()}
        b[pr] = b[pr] * inv % p
        for i in range(m):
            if i != pr and A[i].get(c, 0):
                f = A[i][c]
                for k, v in A[pr].items():
                    A[i][k] = (A[i].get(k, 0) - f * v) % p
                b[i] = (b[i] - f * b[pr]) % p
    nsurplus = 0
    for i in range(m):
        if not row_used[i]:
            if any(v % p for v in A[i].values()):
                continue  # dependent row with leftover entries can't occur
            if b[i] % p:
                return None, -1, 0  # inconsistent
            nsurplus += 1
    if len(piv_of_col) < nunk:
        return None, len(piv_of_col), nsurplus
    x = [0] * nunk
    for c, i in piv_of_col.items():
        x[c] = b[i]
    return x, nunk, nsurplus


def fit_r(Mtab, r, king, p, sqD_mod):
    """fit A,B mod p; returns (idx, sol, nsurplus) or (None, rank, _)."""
    TA, TB = 6 * r + 8, 6 * r + 5
    idx = {}
    n = 0
    for i in range(TA + 1):
        for j in range(i, TA + 1 - i):
            idx[("A", i, j)] = n
            n += 1
    for i in range(TB + 1):
        for j in range(i, TB + 1 - i):
            idx[("B", i, j)] = n
            n += 1
    den = den_poly(r, king)
    denm = {k: c % p for k, c in den.items()}
    Mm = {k: v % p for k, v in Mtab.items()}
    # target on half-grid
    rows, rhs = [], []
    for I in range(WBOX + 1):
        for J in range(I, WBOX + 1):
            t = 0
            for (a, b), dc in denm.items():
                w, h = I - a, J - b
                if w >= 1 and h >= 1:
                    t = (t + dc * Mm.get((w, h), 0)) % p
            row = {}
            key = ("A", I, J)
            if key in idx:
                row[idx[key]] = 1
            for (tag, i, j), col in idx.items():
                if tag != "B":
                    continue
                c = sqD_mod.get((I - i, J - j), 0)
                if i != j:
                    c = (c + sqD_mod.get((I - j, J - i), 0)) % p
                if c:
                    row[col] = (row.get(col, 0) + c) % p
            rows.append(row)
            rhs.append(t)
    sol, rank, nsur = solve_mod(rows, rhs, p, n)
    return idx, sol, rank, nsur, len(rows)


def crt_lift(x1, x2):
    M = P1 * P2
    inv = pow(P1, P2 - 2, P2)
    out = []
    for a1, a2 in zip(x1, x2):
        t = (a2 - a1) * inv % P2
        v = a1 + P1 * t
        if v > M // 2:
            v -= M
        out.append(v)
    return out


# ---------- exact division ladder ----------
def divide(P, D, leadkey):
    """exact multivariate division (s10 routine, generalized lead term)."""
    la, lb = leadkey
    P = dict(P)
    Q = {}
    while True:
        cand = [k for k, c in P.items() if c and k[0] >= la and k[1] >= lb]
        if not cand:
            break
        i, j = max(cand)
        c = P[(i, j)]
        qk = (i - la, j - lb)
        Q[qk] = Q.get(qk, 0) + c
        for (a, b), dc in D.items():
            k2 = (qk[0] + a, qk[1] + b)
            P[k2] = P.get(k2, 0) - c * dc
            if P[k2] == 0:
                del P[k2]
    return Q, {k: c for k, c in P.items() if c}


def main():
    t00 = time.time()
    say(f"s11 bivariate B_r extraction: WBOX={WBOX} rmax={RMAX} "
        f"primes {P1},{P2}")
    say("REGISTERED PREDICTION (see reports/session-11.md): Delta | B_r and "
        "B_r = Delta*x^2y^2*(1+x+y)*C_r [king] / Delta*4x^2y^2*E_r [control]")
    sqD = sqrtD_frac(WBOX)
    assert all(c.denominator == 1 for c in sqD.values()), \
        "sqrt(Delta) not integral"
    sqDZ = {k: int(c) for k, c in sqD.items()}
    say(f"sqrt(Delta) over Z to grid {WBOX}: {len(sqDZ)} terms "
        f"({time.time()-t00:.0f}s)")
    js = {}
    allok = True
    for king, mode in ((True, "king"), (False, "poly")):
        t0 = time.time()
        gm = R4.gm_table(WBOX, lambda w: WBOX, king=king)
        tables = {}
        for rr in range(1, RMAX + 1):
            tables[rr] = {(w, h): R4.m_from_gm(gm, w, h)[rr]
                          for w in range(1, WBOX + 1)
                          for h in range(1, WBOX + 1)}
        # transpose sanity
        for rr in range(1, RMAX + 1):
            for (w, h), v in tables[rr].items():
                assert tables[rr][(h, w)] == v, ("transpose", mode, rr, w, h)
        say(f"[{mode}] DP tables r<=({RMAX}) built, transpose OK "
            f"({time.time()-t0:.0f}s)")
        for rr in range(1, RMAX + 1):
            t1 = time.time()
            sols = {}
            for p in (P1, P2):
                sqD_mod = {k: c % p for k, c in sqDZ.items()}
                idx, sol, rank, nsur, neq = fit_r(tables[rr], rr, king, p,
                                                  sqD_mod)
                if sol is None:
                    say(f"[{mode}] r={rr} p={p}: FIT FAILED rank={rank}")
                    allok = False
                    break
                say(f"[{mode}] r={rr} p={p}: unique fit, {len(idx)} unknowns, "
                    f"{neq} equations, {nsur} consistent surplus rows "
                    f"({time.time()-t1:.0f}s)")
                sols[p] = sol
            if len(sols) != 2:
                continue
            lift = crt_lift(sols[P1], sols[P2])
            mx = max(abs(v) for v in lift)
            say(f"[{mode}] r={rr}: CRT lift max|coeff| = {mx} "
                f"({'small' if mx < 10**14 else 'NOT SMALL - suspicious'})")
            A = {}
            B = {}
            for key, col in idx.items():
                v = lift[col]
                if not v:
                    continue
                tag, i, j = key
                (A if tag == "A" else B)[(i, j)] = v
            # exact over-Z verification on the FULL grid
            Asym = dict(A)
            Bsym = dict(B)
            for (i, j), c in list(A.items()):
                if i != j:
                    Asym[(j, i)] = c
            for (i, j), c in list(B.items()):
                if i != j:
                    Bsym[(j, i)] = c
            den = den_poly(rr, king)
            resid_bad = 0
            BsqD = dmul(Bsym, sqDZ, WBOX)
            Mden = {}
            for (a, b), dc in den.items():
                for (w, h), v in tables[rr].items():
                    I, J = w + a, h + b
                    if I <= WBOX and J <= WBOX:
                        Mden[(I, J)] = Mden.get((I, J), 0) + dc * v
            for I in range(WBOX + 1):
                for J in range(WBOX + 1):
                    lhs = Asym.get((I, J), 0) + BsqD.get((I, J), 0)
                    if lhs != Mden.get((I, J), 0):
                        resid_bad += 1
            say(f"[{mode}] r={rr}: EXACT over-Z residual on full "
                f"{WBOX+1}x{WBOX+1} grid: "
                f"{'ZERO everywhere' if resid_bad == 0 else str(resid_bad)+' BAD CELLS'}")
            allok &= resid_bad == 0
            if rr == 1:
                # VERIFY vs banked s07 bivariate M1 closed form
                fn = ("out_s07_bivar_moment.json" if king
                      else "out_s07_bivar_moment_poly.json")
                cf = json.load(open(os.path.join(ROOT, fn)))
                bankA = {tuple(map(int, k.split(","))): v
                         for k, v in cf["A"].items()}
                bankB = {tuple(map(int, k.split(","))): v
                         for k, v in cf["B"].items()}
                okA1 = bankA == A
                okB1 = bankB == B
                say(f"[{mode}] r=1 CONTROL vs banked s07 json: "
                    f"A {'==' if okA1 else '!='} banked, "
                    f"B {'==' if okB1 else '!='} banked")
                allok &= okA1 and okB1
            # division ladder on B
            Q1, R1 = divide(Bsym, DELTA, (2, 0))
            okD = not R1
            say(f"[{mode}] r={rr}: Delta | B_{rr} exact division: "
                f"{'CONFIRMED' if okD else 'REFUTED (remainder '+str(len(R1))+' terms)'}")
            entry = dict(A={f"{i},{j}": c for (i, j), c in sorted(A.items())},
                         B={f"{i},{j}": c for (i, j), c in sorted(B.items())})
            if okD:
                # /x^2y^2
                okxy = all(i >= 2 and j >= 2 for i, j in Q1)
                say(f"[{mode}] r={rr}: x^2y^2 | (B/Delta): "
                    f"{'yes' if okxy else 'NO'}")
                if okxy:
                    Q2 = {(i - 2, j - 2): c for (i, j), c in Q1.items()}
                    if king:
                        Q3, R3 = divide(Q2, {(0, 0): 1, (1, 0): 1, (0, 1): 1},
                                        (1, 0))
                        ok3 = not R3
                        say(f"[{mode}] r={rr}: (1+x+y) | (B/(Delta x^2y^2)): "
                            f"{'CONFIRMED' if ok3 else 'no'}")
                        C = Q3 if ok3 else Q2
                        tagname = "C" if ok3 else "B_over_Dxy"
                    else:
                        g = 0
                        for c in Q2.values():
                            g = gcd(g, c)
                        say(f"[{mode}] r={rr}: content gcd of B/(Delta x^2y^2)"
                            f" = {g}")
                        C = {k: c // g for k, c in Q2.items()} if g else Q2
                        tagname = f"E_times (content {g})"
                    say(f"[{mode}] r={rr}: quotient [{tagname}] "
                        f"{len(C)} monomials, max total deg "
                        f"{max((i+j for i, j in C), default=0)}:")
                    for (i, j), c in sorted(C.items()):
                        if i <= j:
                            pass
                    say("    " + " + ".join(
                        f"({c})x^{i}y^{j}" for (i, j), c in sorted(C.items())))
                    entry["quotient"] = {f"{i},{j}": c
                                         for (i, j), c in sorted(C.items())}
                    entry["quotient_tag"] = tagname
            js[f"{mode}_r{rr}"] = entry
        say(f"[{mode}] total wall {time.time()-t0:.0f}s")
    say(f"VERDICT: {'ALL FITS + EXACT CHECKS PASS' if allok else 'FAILURES PRESENT'}")
    with open(os.path.join(ROOT, "out_s12_bivar_Br.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    json.dump(js, open(os.path.join(ROOT, "out_s12_bivar_Br.json"), "w"))
    say("receipts: out_s12_bivar_Br.txt, out_s12_bivar_Br.json")


def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


if __name__ == "__main__":
    main()
