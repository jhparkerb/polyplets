#!/usr/bin/env python3
"""Session 07: registered-prediction holdout test for the fitted moment GFs.

Mode 'predict': expand the fitted closed forms (hard-coded from
out_s07_moment_fit.txt, fitted ONLY on s<=37 data) to t^46 and write the
predicted a_1(38..46) [king+poly] and a_2(38..46) [poly] to
out_s07_predictions.json.  Run BEFORE the SMAX=46 DP data exists.

Mode 'check': compare predictions against the fresh DP output
out_s07_area_moments46.json.  Any mismatch is a refutation of the fit.

Usage: python3 experiments/s07_predict_holdout.py predict|check
"""
import json, os, sys
from fractions import Fraction
from math import comb

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
N = 53  # coefficients t^0..t^52
LO, HI = 47, 52  # holdout window (phase 2; phase 1 was 38..46, confirmed)

FITS = {
    # (mode, r): (a, b, P coeffs from t^0, Q coeffs from t^0)
    ("king", 1): (2, 4,
                  [0, 0, 4, -52, 230, -348, 120, -84, -54, 80, 32],
                  [0, 0, 0, 8, -29, -34, 100, -40, -32]),
    ("king", 2): (3, 6,
                  [0, 0, 8, 12, -444, 474, 7140, -23614, 25140, 766,
                   -17936, 5936, 4928, -2304, -1024],
                  [0, 0, 0, -128, 1010, -2093, -470, 3534, 1428, -6548,
                   16, 3344, 960]),
    ("poly", 1): (0, 4,
                  [0, 0, 1, -12, 50, -76, 42, -48, 32],
                  [0, 0, 0, 0, 4, -16]),
    ("poly", 2): (0, 6,
                  [0, 0, 1, -16, 172, -1116, 4062, -8304, 10160, -7872,
                   3840, -1024],
                  [0, 0, 0, 0, -54, 528, -1896, 3216, -2736, 960]),
}


def series_mul(u, v):
    w = [Fraction(0)] * N
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j, vj in enumerate(v):
            if i + j >= N:
                break
            if vj:
                w[i + j] += ui * vj
    return w


def series_inv(p):
    """1/p with p[0] != 0."""
    out = [Fraction(0)] * N
    out[0] = 1 / Fraction(p[0])
    for k in range(1, N):
        s = Fraction(0)
        for j in range(1, min(k, len(p) - 1) + 1):
            s += Fraction(p[j]) * out[k - j]
        out[k] = -s / Fraction(p[0])
    return out


def expand(a, b, P, Q):
    S = [Fraction(-comb(2 * k, k), 2 * k - 1) for k in range(N)]
    num = [Fraction(c) for c in P] + [Fraction(0)] * (N - len(P))
    qs = series_mul([Fraction(c) for c in Q] + [Fraction(0)] * (N - len(Q)), S)
    num = [x + y for x, y in zip(num, qs)]
    den = [Fraction(1)] + [Fraction(0)] * (N - 1)
    for _ in range(a):
        den = series_mul(den, [Fraction(2), Fraction(1)] + [Fraction(0)] * (N - 2))
    for _ in range(b):
        den = series_mul(den, [Fraction(1), Fraction(-4)] + [Fraction(0)] * (N - 2))
    ser = series_mul(num, series_inv(den))
    for k, c in enumerate(ser):
        assert c.denominator == 1, (k, c)
    return [int(c) for c in ser]


def main():
    mode = sys.argv[1]
    pf = os.path.join(ROOT, "out_s07_predictions2.json")
    if mode == "predict":
        pred = {}
        for (fam, r), (a, b, P, Q) in FITS.items():
            ser = expand(a, b, P, Q)
            pred[f"{fam}_a{r}"] = {str(s): ser[s] for s in range(LO, HI + 1)}
        json.dump(pred, open(pf, "w"), indent=1)
        print(f"registered predictions for s={LO}..{HI}:")
        for k, v in pred.items():
            print(f"  {k}: s={LO} -> {v[str(LO)]}")
    elif mode == "check":
        pred = json.load(open(pf))
        data = json.load(open(os.path.join(ROOT, "out_s07_area_moments52.json")))
        assert data["smax"] == 52
        lines = []
        allok = True
        for key, d in pred.items():
            fam, ar = key.split("_")
            seq = data[fam][ar]
            ok = all(seq[int(s) - 2] == v for s, v in d.items())
            allok &= ok
            lines.append(f"  {key}: {HI-LO+1} held-out terms s={LO}..{HI} "
                         + ("ALL MATCH" if ok else "MISMATCH"))
        lines.append(f"holdout verdict: {'CONFIRMED' if allok else 'REFUTED'}")
        body = "\n".join(lines)
        print(body)
        with open(os.path.join(ROOT, "out_s07_holdout_check2.txt"), "w") as fp:
            fp.write(__doc__ + "\n" + body + "\n")
    else:
        raise SystemExit("usage: predict|check")


if __name__ == "__main__":
    main()
