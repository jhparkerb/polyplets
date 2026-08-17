#!/usr/bin/env python3
"""Session 05: two-pole verification. The residue formula at the SECOND
real zero q_2 of the Temperley denominator must predict the subdominant
term of a(n): a(n) - A*mu^n ~ A2*mu2^n with A2 = -c1(q2)a(q2)/(K'(q2)q2).
Empirical fit from exact terms vs residue prediction, both modes."""
import os, sys
from decimal import Decimal, getcontext

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s05_asymptotics import (NSolver, denom_series, dderiv, find_root,
                             load_terms, D1)

getcontext().prec = 110


def residue_amp(qz, king):
    s = NSolver(qz, king=king)
    s.solve_F10()
    c0 = s.assemble(0)
    c1 = s.assemble(1) - c0
    det = s.det
    alpha = s.alpha.a
    Kp = dderiv(lambda q: denom_series(q, king), qz)
    return -(c1 * alpha) / (Kp * qz), -(alpha) / (Kp * qz), det


def main():
    seqs = load_terms()
    for king, tagf, tagd, b1, b2, b3, b4 in (
            (True, "king_full", "king_directed", "0.28", "0.36",
             "0.60", "0.70"),
            (False, "poly_full", "poly_directed", "0.40", "0.48",
             "0.65", "0.73")):
        tag = "KING" if king else "CONTROL"
        Kf = lambda q: denom_series(q, king)
        qc = find_root(Kf, b1, b2)
        q2 = find_root(Kf, b3, b4)
        mu, mu2 = D1 / qc, D1 / q2
        A, Ad, detc = residue_amp(qc, king)
        A2, A2d, det2 = residue_amp(q2, king)
        print(f"== {tag} ==")
        print(f"  q_2 = {q2}")
        print(f"  mu2 = {mu2}")
        print(f"  det(q_2) = {det2:.6f} (must be nonzero)")
        print(f"  residue-predicted A2 (full)     = {A2:.30f}")
        print(f"  residue-predicted A2 (directed) = {A2d:.30f}")
        # det scan on (q_c, q_2]
        dets = []
        for i in range(1, 21):
            qq = qc + (q2 - qc) * Decimal(i) / 20
            ss = NSolver(qq, king=king)
            ss.solve_F10()
            ss.assemble(0)
            dets.append(ss.det)
        ok = all(d > 0 for d in dets) or all(d < 0 for d in dets)
        print(f"  det sign constant on (q_c,q_2]: {ok} "
              f"(min|det|={min(abs(d) for d in dets):.3e})")
        for name, seq, Amp, A2p in ((tagf, seqs[tagf], A, A2),
                                    (tagd, seqs[tagd], Ad, A2d)):
            print(f"  {name}: empirical (a(n)-A*mu^n)/mu2^n vs predicted "
                  f"{A2p:.12f}")
            for n in (48, 52, 56, 60):
                emp = (Decimal(seq[n - 1]) - Amp * mu ** n) / mu2 ** n
                rel = emp / A2p - 1
                print(f"    n={n}: {emp:.12f}  rel.err={rel:.2e}")


if __name__ == "__main__":
    main()
