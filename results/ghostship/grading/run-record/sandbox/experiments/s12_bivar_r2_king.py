#!/usr/bin/env python3
"""Session 12 follow-up: king r=2 bivariate fit FAILED (inconsistent) at the
s11 ansatz degrees TA=6r+8=20, TB=6r+5=17 (out_s12_bivar_Br.txt).  Poly r=2
and king r=1,3 fit fine, and the slice denominator law K^(r+1)Delta^(2r+2)
is r<=8-verified (s09), so the suspect is the DEGREE BOUND, not the
denominator.  This driver retries king r=2 with a ladder of larger (TA,TB)
until the fit closes, then runs the same CRT + exact-over-Z + division
ladder as the main script.

Usage: python3 experiments/s12_bivar_r2_king.py
Output: out_s12_bivar_r2_king.txt (+ json)
"""
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_bivar_Br as BR
import s07_area_moments_r4 as R4

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WBOX = BR.WBOX          # 30 (default argv-free import)
P1, P2 = BR.P1, BR.P2
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def fit_r_deg(Mtab, r, king, p, sqD_mod, TA, TB):
    """BR.fit_r with explicit degree bounds."""
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
    den = BR.den_poly(r, king)
    denm = {k: c % p for k, c in den.items()}
    Mm = {k: v % p for k, v in Mtab.items()}
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
    sol, rank, nsur = BR.solve_mod(rows, rhs, p, n)
    return idx, sol, rank, nsur, len(rows)


def main():
    t00 = time.time()
    say(f"s12 king r=2 degree-ladder retry: WBOX={WBOX}")
    sqD = BR.sqrtD_frac(WBOX)
    sqDZ = {k: int(c) for k, c in sqD.items()}
    gm = R4.gm_table(WBOX, lambda w: WBOX, king=True)
    tab = {(w, h): R4.m_from_gm(gm, w, h)[2]
           for w in range(1, WBOX + 1) for h in range(1, WBOX + 1)}
    say(f"[king] r=2 DP table built ({time.time()-t00:.0f}s)")

    found = None
    for TA, TB in ((21, 18), (22, 19), (23, 20), (24, 21), (26, 23)):
        sqD_mod = {k: c % P1 for k, c in sqDZ.items()}
        idx, sol, rank, nsur, neq = fit_r_deg(tab, 2, True, P1, sqD_mod,
                                              TA, TB)
        if sol is None:
            say(f"  TA={TA} TB={TB} p1: rank={rank} "
                f"({'inconsistent' if rank == -1 else 'underdetermined'})")
            continue
        say(f"  TA={TA} TB={TB} p1: unique fit, {len(idx)} unknowns, "
            f"{neq} eqs, {nsur} surplus")
        found = (TA, TB, idx, sol)
        break
    if not found:
        say("NO FIT up to TA=26 -- denominator law itself suspect at r=2")
        write_out()
        return
    TA, TB, idx, sol1 = found
    sqD_mod2 = {k: c % P2 for k, c in sqDZ.items()}
    idx2, sol2, rank2, nsur2, neq2 = fit_r_deg(tab, 2, True, P2, sqD_mod2,
                                               TA, TB)
    assert sol2 is not None, "p2 fit failed at the p1-successful degrees"
    say(f"  TA={TA} TB={TB} p2: unique fit, {nsur2} surplus")
    lift = BR.crt_lift(sol1, sol2)
    mx = max(abs(v) for v in lift)
    say(f"  CRT lift max|coeff| = {mx} ({'small' if mx < 10**14 else 'BIG'})")
    A, B = {}, {}
    for key, col in idx.items():
        v = lift[col]
        if v:
            tag, i, j = key
            (A if tag == "A" else B)[(i, j)] = v
    Asym, Bsym = dict(A), dict(B)
    for (i, j), c in list(A.items()):
        if i != j:
            Asym[(j, i)] = c
    for (i, j), c in list(B.items()):
        if i != j:
            Bsym[(j, i)] = c
    say(f"  deg A_2 = {max(i+j for i,j in Asym)}, "
        f"deg B_2 = {max(i+j for i,j in Bsym)}, "
        f"terms {len(Asym)}/{len(Bsym)}")
    # exact over-Z check on the full grid (BR.check_exact equivalent)
    den = BR.den_poly(2, True)
    BsqD = BR.dmul(Bsym, sqDZ, WBOX)
    bad = 0
    for I in range(WBOX + 1):
        for J in range(WBOX + 1):
            t = 0
            for (a, b), dc in den.items():
                w, h = I - a, J - b
                if w >= 1 and h >= 1:
                    t += dc * tab[(w, h)]
            lhs = Asym.get((I, J), 0) + BsqD.get((I, J), 0)
            if lhs != t:
                bad += 1
    say(f"  EXACT over-Z residual on full {WBOX+1}x{WBOX+1} grid: "
        f"{'ZERO everywhere' if bad == 0 else f'{bad} BAD CELLS'}")
    js = dict(TA=TA, TB=TB,
              A={f"{i},{j}": c for (i, j), c in sorted(Asym.items())},
              B={f"{i},{j}": c for (i, j), c in sorted(Bsym.items())})
    json.dump(js, open(os.path.join(ROOT, "out_s12_bivar_r2_king.json"),
                       "w"))
    # division ladder (leadkey = lex-leading monomial of divisor, coeff 1)
    DELTA = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (0, 2): 1,
             (1, 1): -2}
    Q, rem = BR.divide(dict(Bsym), DELTA, (2, 0))
    say(f"  Delta | B_2: {'CONFIRMED' if not rem else 'NO'}")
    if not rem:
        Q2 = {(i - 2, j - 2): c for (i, j), c in Q.items()}
        ok_xy = all(i >= 0 and j >= 0 for i, j in Q2)
        say(f"  x^2y^2 | (B/Delta): {'yes' if ok_xy else 'NO'}")
        if ok_xy:
            W1 = {(0, 0): 1, (1, 0): 1, (0, 1): 1}
            Q3, rem3 = BR.divide(dict(Q2), W1, (1, 0))
            say(f"  (1+x+y) | (B/(Delta x^2y^2)): "
                f"{'CONFIRMED' if not rem3 else 'no'}")
            from math import gcd
            g = 0
            for c in Q2.values():
                g = gcd(g, abs(c))
            say(f"  content gcd of B/(Delta x^2y^2) = {g}")
            js["quotient"] = {f"{i},{j}": c
                              for (i, j), c in sorted(Q2.items())}
            json.dump(js, open(os.path.join(ROOT,
                                            "out_s12_bivar_r2_king.json"),
                               "w"))
    write_out()


def write_out():
    with open(os.path.join(ROOT, "out_s12_bivar_r2_king.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipts: out_s12_bivar_r2_king.txt, out_s12_bivar_r2_king.json")


if __name__ == "__main__":
    main()
