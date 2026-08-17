#!/usr/bin/env python3
"""Session 07: fit A_3, A_4 closed forms and TEST the registered limit-law
prediction (out_s07_limit_law_prediction.txt, written before the r>=3 data
existed):

  denominators (2+t)^(r+1)(1-4t)^(2r+2) [king] / (1-4t)^(2r+2) [poly]
  p_0(A_3) = 9/256,  p_0(A_4) = 9/32   (both modes)
  E[area^3]/s^6 -> 1/1120,  E[area^4]/s^8 -> 1/10080

Data: out_s07_area_moments_r4_57.json (SMAX=57; r<=4 DP validated V1/V3/V4).
Also cross-checks r<=2 sequences against the independent earlier runs.
Output: out_s07_r4_fit.txt
"""
import json, os, sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s07_moment_fit as MF   # try_fit, fmt_poly operate on MF.DATA/NTRUNC

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def main():
    data = json.load(open(os.path.join(ROOT,
                          "out_s07_area_moments_r4_57.json")))
    MF.DATA = data
    MF.NTRUNC = data["smax"] + 1
    lines = []

    # cross-check r<=2 against the independent SMAX=52 run
    d52 = json.load(open(os.path.join(ROOT, "out_s07_area_moments52.json")))
    for mode in ("king", "poly"):
        for r in range(3):
            a, b = d52[mode][f"a{r}"], data[mode][f"a{r}"]
            assert a == b[:len(a)], (mode, r)
    lines.append("cross-check: r<=2 sequences of the r4 run == independent "
                 "SMAX=52 run on all 51 shared terms: OK")

    p0_bank = {}
    for mode, king in (("king", True), ("poly", False)):
        for r in (3, 4):
            seq = data[mode][f"a{r}"]
            a_pred = (r + 1) if king else 0
            b_pred = 2 * r + 2
            found = None
            for d in range(2, 24):
                if MF.NTRUNC - 2 * (d + 1) < 8:
                    break
                got = MF.try_fit(seq, data["start"], a_pred, b_pred,
                                 d, d, king)
                if got:
                    found = (a_pred, b_pred, d, got)
                    break
            tag = f"[{mode}] A_{r}"
            if not found:
                lines.append(f"{tag}: predicted denominator "
                             f"(a={a_pred},b={b_pred}) FAILED for d<=23 "
                             f"-> prediction REFUTED at denominator level")
                continue
            a, b, d, (P, Q, surplus) = found
            den = (f"(2+t)^{a} (1-4t)^{b}" if king else f"(1-4t)^{b}")
            lines.append(f"{tag} = [P + Q*sqrt(1-4t)] / {den}   "
                         f"(degP=degQ<={d}, surplus={surplus})")
            lines.append(f"  P = {MF.fmt_poly(P)}")
            lines.append(f"  Q = {MF.fmt_poly(Q)}")
            # p_0 = P(1/4) / (9/4)^a
            P14 = sum(Fraction(c) * Fraction(1, 4) ** k
                      for k, c in enumerate(P))
            p0 = P14 / Fraction(9, 4) ** a
            p0_bank[(mode, r)] = p0
            lines.append(f"  p_0 = {p0}")

    lines.append("")
    lines.append("REGISTERED-PREDICTION TEST (limit law X = U(1-U)/2):")
    c0 = Fraction(1, 128)
    targets = {3: (Fraction(9, 256), Fraction(1, 1120)),
               4: (Fraction(9, 32), Fraction(1, 10080))}
    allok = True
    for mode in ("king", "poly"):
        for r in (3, 4):
            if (mode, r) not in p0_bank:
                allok = False
                continue
            p0 = p0_bank[(mode, r)]
            pred_p0, pred_E = targets[r]
            fact = 1
            for k in range(2, 2 * r + 2):
                fact *= k
            E = (p0 / c0) / fact  # (2r+1)!
            ok = (p0 == pred_p0) and (E == pred_E)
            allok &= ok
            lines.append(f"  [{mode}] r={r}: p_0={p0} (predicted {pred_p0}), "
                         f"E[area^{r}]/s^{2*r} -> {E} (predicted {pred_E}): "
                         + ("MATCH" if ok else "MISMATCH"))
    lines.append(f"limit-law prediction verdict: "
                 f"{'CONFIRMED' if allok else 'REFUTED/incomplete'}")
    body = "\n".join(lines)
    print(body)
    with open(os.path.join(ROOT, "out_s07_r4_fit.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")


if __name__ == "__main__":
    main()
