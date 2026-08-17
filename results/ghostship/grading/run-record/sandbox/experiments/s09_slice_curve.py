#!/usr/bin/env python3
"""s09: SECOND slice x = 1/9 of the moment-kernel recursion — registered
test of the curve-amplitude conjecture

    C_r(x,y) := lim_{Delta->0} Delta^(2r+2) M_r(x,y)
              = (r!)^2 * 2^(5r+3) * (xy)^((3r+5)/2)   on Delta=0,
              identical for king and polyomino modes,

which was inferred ONLY from r<=1 exact bivariate forms and the x=1/4
slice (diagonal point a=1/2).  The slice x=1/9 crosses Delta=0 at
y_c=(1-1/3)^2=4/9 (curve parameter a=1/3), Delta(1/9,y)=(y-4/9)(y-16/9),
K(1/9,4/9)=49/81.  Predicted slice constants (written BEFORE the run):

    P_r(4/9)/K_c^(r+1)  ==  (r!)^2 * 2^(5r+3) * (2/9)^(3r+5),  r=0..MAXR.

Usage: python3 experiments/s09_slice_curve.py [MAXR] [NU]
Output: out_s09_slice_curve.txt
"""
import sys, os
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s09_slice_moments as S9
import s03_kernel_solve as K3

MAXR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
NU = int(sys.argv[2]) if len(sys.argv) > 2 else 220
OUT = []


def say(m):
    print(m, flush=True)
    OUT.append(str(m))


def main():
    say(f"s09 curve test: slice x=1/9, MAXR={MAXR}, NU={NU}")
    allok = True
    for mode in ("king", "poly"):
        king = mode == "king"
        for P in S9.PRIMES:
            K3.P = P
            K3.NX = 0
            K3.NU = NU
            ctx, levels = S9.solve_all_levels(king, MAXR, 1, 9)
            xm = pow(9, P - 2, P)
            yc = 4 * pow(9, P - 2, P) % P          # crossing point 4/9
            Kc = 49 * pow(81, P - 2, P) % P        # K(1/9,4/9)
            for r, L in enumerate(levels):
                tot = L["tot"]
                ny = tot.vu // 2 + 1
                S = S9.ser_to_ylist(tot, ny)
                fit = S9.fit_PQ(S, r, ny, P, xm)
                assert fit, f"no fit r={r} {mode} {P}"
                e, eA, d, pC, qC, sur = fit
                assert e == 0 and eA == 0
                cP = S9.ypolyval(pC, yc) * pow(pow(Kc, r + 1, P),
                                               P - 2, P) % P
                # registered prediction:
                tgt = Fr(1)
                for i in range(1, r + 1):
                    tgt *= i * i
                tgt *= Fr(2) ** (5 * r + 3) * Fr(2, 9) ** (3 * r + 5)
                tm = tgt.numerator % P * pow(tgt.denominator % P,
                                             P - 2, P) % P
                ok = cP == tm
                allok &= ok
                qc9 = S9.ypolyval(qC, yc) if r >= 1 else None
                say(f"  [{mode}] p={P} r={r}: surplus={sur} "
                    f"C_r(a=1/3) == (r!)^2 2^{5*r+3} (2/9)^{3*r+5}: "
                    f"{'MATCH' if ok else 'MISMATCH'}"
                    + (f"  Q_r(4/9)==0: {qc9 == 0}" if r >= 1 else ""))
    say("VERDICT: " + ("ALL MATCH — curve-amplitude conjecture holds at "
                       "a=1/3 for all computed r, both modes"
                       if allok else "MISMATCHES PRESENT"))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "out_s09_slice_curve.txt"), "w").write(
        __doc__ + "\n" + "\n".join(OUT) + "\n")


if __name__ == "__main__":
    main()
