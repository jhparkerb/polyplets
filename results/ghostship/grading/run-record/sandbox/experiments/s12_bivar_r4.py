#!/usr/bin/env python3
"""Session 12: r=4 bivariate closed-form extraction, both modes, WBOX=38.

Purpose: (i) test the REGISTERED delta-multiplicity conjecture
nu_Delta(B_4) = ceil(4/2) = 2 bivariately (the slice/delta-engine data
r<=6 says the odd part deficit is m=ceil(r/2); bivariate confirmed r<=3);
(ii) probe the king even-r degree anomaly: king r=2 was INCONSISTENT at
the interpolated degrees (TA,TB)=(6r+8,6r+5) while r=1,3 sit exactly on
that line — does r=4 fail at (32,29) too?  Degree ladder built in.

Usage: python3 experiments/s12_bivar_r4.py [WBOX]
Output: out_s12_bivar_r4.txt, out_s12_bivar_r4.json
"""
import sys, os, json, time
from math import gcd
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s12_bivar_Br as BR
import s07_area_moments_r4 as R4
from s12_bivar_r2_king import fit_r_deg   # degree-parametrized fit
import s12_bivar_r2_king as DRV

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WBOX = int(sys.argv[1]) if len(sys.argv) > 1 else 38
DRV.WBOX = WBOX
BR.WBOX = WBOX
P1, P2 = BR.P1, BR.P2
OUT = []
R = 4


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def main():
    t00 = time.time()
    say(f"s12 r=4 bivariate extraction: WBOX={WBOX}")
    say("REGISTERED PREDICTION: nu_Delta(B_4) = 2, both modes "
        "(delta-multiplicity law m = ceil(r/2), see reports/session-12.md)")
    sqD = BR.sqrtD_frac(WBOX)
    sqDZ = {k: int(c) for k, c in sqD.items()}
    say(f"sqrt(Delta) to grid {WBOX} ({time.time()-t00:.0f}s)")
    js = {}
    for king, mode in ((True, "king"), (False, "poly")):
        t0 = time.time()
        gm = R4.gm_table(WBOX, lambda w: WBOX, king=king)
        tab = {(w, h): R4.m_from_gm(gm, w, h)[R]
               for w in range(1, WBOX + 1) for h in range(1, WBOX + 1)}
        say(f"[{mode}] r=4 DP table built ({time.time()-t0:.0f}s)")
        found = None
        base = 6 * R + 8
        for bump in (0, 1, 2, 3, 4, 6):
            TA, TB = base + bump, base - 3 + bump
            sqD_mod = {k: c % P1 for k, c in sqDZ.items()}
            idx, sol, rank, nsur, neq = fit_r_deg(tab, R, king, P1,
                                                  sqD_mod, TA, TB)
            if sol is None:
                say(f"[{mode}]  TA={TA} TB={TB} p1: rank={rank} "
                    f"({'inconsistent' if rank == -1 else 'underdet'})")
                continue
            say(f"[{mode}]  TA={TA} TB={TB} p1: unique fit, {len(idx)} "
                f"unknowns, {neq} eqs, {nsur} surplus")
            found = (TA, TB, idx, sol)
            break
        if not found:
            say(f"[{mode}] NO FIT up to TA={base+6}")
            continue
        TA, TB, idx, sol1 = found
        sqD_mod2 = {k: c % P2 for k, c in sqDZ.items()}
        _, sol2, rank2, nsur2, _ = fit_r_deg(tab, R, king, P2, sqD_mod2,
                                             TA, TB)
        assert sol2 is not None, "p2 failed at p1-successful degrees"
        say(f"[{mode}]  p2: unique fit, {nsur2} surplus")
        lift = BR.crt_lift(sol1, sol2)
        mx = max(abs(v) for v in lift)
        say(f"[{mode}]  CRT max|coeff| = {mx} "
            f"({'small' if mx < 10**15 else 'BIG - SUSPICIOUS'})")
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
        say(f"[{mode}]  deg A_4 = {max(i+j for i,j in Asym)}, "
            f"deg B_4 = {max(i+j for i,j in Bsym)}")
        # exact over-Z on full grid
        den = BR.den_poly(R, king)
        BsqD = BR.dmul(Bsym, sqDZ, WBOX)
        bad = 0
        for I in range(WBOX + 1):
            for J in range(WBOX + 1):
                t = 0
                for (a, b), dc in den.items():
                    w, h = I - a, J - b
                    if w >= 1 and h >= 1:
                        t += dc * tab[(w, h)]
                if Asym.get((I, J), 0) + BsqD.get((I, J), 0) != t:
                    bad += 1
        say(f"[{mode}]  EXACT over-Z full grid: "
            f"{'ZERO everywhere' if bad == 0 else f'{bad} BAD CELLS'}")
        # Delta-multiplicity ladder
        DELTA = {(0, 0): 1, (1, 0): -2, (0, 1): -2, (2, 0): 1, (0, 2): 1,
                 (1, 1): -2}
        cur = dict(Bsym)
        nu = 0
        while True:
            q, rem = BR.divide(dict(cur), DELTA, (2, 0))
            if rem:
                break
            nu += 1
            cur = q
        say(f"[{mode}]  nu_Delta(B_4) = {nu} "
            f"({'MATCHES prediction 2' if nu == 2 else 'PREDICTION FAILS'})")
        g = 0
        for c in cur.values():
            g = gcd(g, abs(c))
        say(f"[{mode}]  core after Delta^{nu}: {len(cur)} monomials, "
            f"deg {max(i+j for i,j in cur)}, content {g}")
        js[mode] = dict(TA=TA, TB=TB, nu=nu,
                        A={f"{i},{j}": c for (i, j), c in sorted(Asym.items())},
                        B={f"{i},{j}": c for (i, j), c in sorted(Bsym.items())})
        json.dump(js, open(os.path.join(ROOT, "out_s12_bivar_r4.json"), "w"))
        with open(os.path.join(ROOT, "out_s12_bivar_r4.txt"), "w") as fp:
            fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say(f"total wall {time.time()-t00:.0f}s")
    with open(os.path.join(ROOT, "out_s12_bivar_r4.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + "\n".join(OUT) + "\n")
    say("receipts: out_s12_bivar_r4.txt, out_s12_bivar_r4.json")


if __name__ == "__main__":
    main()
