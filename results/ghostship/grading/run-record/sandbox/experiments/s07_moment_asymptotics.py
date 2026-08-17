#!/usr/bin/env python3
"""Session 07: exact singularity analysis of the fitted area-moment GFs.

For each closed form A_r(t) = (P + Q*sqrt(1-4t)) / ((2+t)^a (1-4t)^b),
substitute u = 1-4t (t = (1-u)/4) and Taylor-expand the regular parts:

  A_r = sum_{k>=0} p_k u^{k-b}  +  sum_{k>=0} q_k u^{k+1/2-b}

with exact rational p_k, q_k.  Coefficient extraction is exact:
  [t^s] (1-4t)^{-beta} = C(s+beta-1, beta-1) 4^s          (integer beta)
  [t^s] (1-4t)^{-g}    = 4^s * prod_{j=0}^{s-1}(g+j)/s!    (any rational g)

Outputs:
  * exact rational limit constants
      mean:     E_s[area] / s^2  ->  (p_0(r=1)/p_0(r=0)) / 6
      2nd mom:  E_s[area^2]/s^4  ->  (p_0(r=2)/p_0(r=0)) / 120
      variance: Var_s[area]/s^4  ->  the difference
    for king and control (r=0 closed forms = s01 banked / Delest-Viennot);
  * numeric sanity: multi-term singular expansion vs the exact a_r(s) at
    s = SCHK (relative errors must be small and shrink with s).

Receipt output: out_s07_moment_asymptotics.txt
"""
import json, os, sys
from fractions import Fraction as Fr

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATAFILE = (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".json")
            else "out_s07_area_moments46.json")
DATA = json.load(open(os.path.join(ROOT, DATAFILE)))
SCHK = DATA["smax"]

# (a, b, P, Q) with P,Q coeff lists in t; r=0 forms are the PROVEN ones
# (s01 kernel-proven king form; Delest-Viennot control form).
FORMS = {
    ("king", 0): (1, 2, [0, 0, 2, -10, 14, -5, -4],
                  [0, 0, 0, -1, -4, -4]),        # -t^3(1+2t)^2
    ("king", 1): (2, 4, [0, 0, 4, -52, 230, -348, 120, -84, -54, 80, 32],
                  [0, 0, 0, 8, -29, -34, 100, -40, -32]),
    ("king", 2): (3, 6, [0, 0, 8, 12, -444, 474, 7140, -23614, 25140, 766,
                         -17936, 5936, 4928, -2304, -1024],
                  [0, 0, 0, -128, 1010, -2093, -470, 3534, 1428, -6548,
                   16, 3344, 960]),
    ("poly", 0): (0, 2, [0, 0, 1, -6, 11, -4], [0, 0, 0, 0, -4]),
    ("poly", 1): (0, 4, [0, 0, 1, -12, 50, -76, 42, -48, 32],
                  [0, 0, 0, 0, 4, -16]),
    ("poly", 2): (0, 6, [0, 0, 1, -16, 172, -1116, 4062, -8304, 10160,
                         -7872, 3840, -1024],
                  [0, 0, 0, 0, -54, 528, -1896, 3216, -2736, 960]),
}

KEXP = 8  # u-expansion depth


def poly_in_u(coeffs):
    """P(t) with t=(1-u)/4 -> exact coeff list in u."""
    # t^k = ((1-u)/4)^k ; build by Horner in u
    res = [Fr(0)] * (len(coeffs) + 1)
    for k, c in enumerate(coeffs):
        if c == 0:
            continue
        # expand ((1-u)/4)^k
        term = [Fr(1)]
        for _ in range(k):
            nt = [Fr(0)] * (len(term) + 1)
            for i, v in enumerate(term):
                nt[i] += v * Fr(1, 4)
                nt[i + 1] -= v * Fr(1, 4)
            term = nt
        for i, v in enumerate(term):
            res[i] += Fr(c) * v
    return res


def series_div(num, den, n):
    """num/den as u-power series to n terms (den[0] != 0)."""
    out = []
    num = num + [Fr(0)] * n
    den = den + [Fr(0)] * n
    for k in range(n):
        v = num[k]
        for j in range(1, k + 1):
            v -= den[j] * out[k - j]
        out.append(v / den[0])
    return out


def expansions(a, b, P, Q, king):
    Pu = poly_in_u(P)
    Qu = poly_in_u(Q)
    den = [Fr(1)]
    if king:
        d = poly_in_u([2, 1])  # 2+t in u: (9-u)/4
        for _ in range(a):
            den = [sum(den[i] * d[k - i] for i in range(max(0, k - len(d) + 1), min(k, len(den) - 1) + 1)) for k in range(len(den) + len(d) - 1)]
    p = series_div(Pu, den, KEXP)
    q = series_div(Qu, den, KEXP)
    return p, q  # A = sum p_k u^{k-b} + sum q_k u^{k+1/2-b}


def coeff_u_power(g, s):
    """exact [t^s] (1-4t)^{-g} / 4^s = prod_{j=0}^{s-1} (g+j)/ (j+1)."""
    v = Fr(1)
    for j in range(s):
        v *= (g + j)
        v /= (j + 1)
    return v


def main():
    lines = []
    p0 = {}
    for (mode, r), (a, b, P, Q) in FORMS.items():
        king = mode == "king"
        p, q = expansions(a, b, P, Q, king)
        p0[(mode, r)] = (p, q, b)
        lines.append(f"[{mode}] r={r}: A_r = sum p_k u^(k-{b}) + q_k u^(k+1/2-{b}), u=1-4t")
        lines.append(f"  p_0 = {p[0]}   q_0 = {q[0]}")

    lines.append("")
    for mode in ("king", "poly"):
        c0 = p0[(mode, 0)][0][0]
        c1 = p0[(mode, 1)][0][0]
        c2 = p0[(mode, 2)][0][0]
        mean = (c1 / c0) / 6
        second = (c2 / c0) / 120
        var = second - mean * mean
        lines.append(f"[{mode}] c0={c0} c1={c1} c2={c2}")
        lines.append(f"[{mode}] E[area]/s^2   -> {mean}  = {float(mean):.12f}")
        lines.append(f"[{mode}] E[area^2]/s^4 -> {second} = {float(second):.12f}")
        lines.append(f"[{mode}] Var[area]/s^4 -> {var} = {float(var):.12f}")
        lines.append("")

    # numeric sanity: multi-term prediction vs exact terms
    for mode in ("king", "poly"):
        for r in (0, 1, 2):
            if r == 0:
                # reconstruct a0 from data? data has a0
                seq = DATA[mode]["a0"]
            else:
                seq = DATA[mode][f"a{r}"]
            s = SCHK
            actual = seq[s - 2]
            p, q, b = p0[(mode, r)]
            pred = Fr(0)
            for k in range(KEXP):
                if k - b < 0:
                    pred += p[k] * coeff_u_power(Fr(b - k), s)
                elif k - b == 0:
                    pred += p[k]
                pred += q[k] * coeff_u_power(Fr(b - k) - Fr(1, 2), s)
            pred_int = pred * Fr(4) ** s
            rel = float((pred_int - actual) / actual)
            lines.append(f"[{mode}] a{r}({s}): singular-expansion rel.err = {rel:.3e}")

    body = "\n".join(lines)
    print(body)
    with open(os.path.join(ROOT, "out_s07_moment_asymptotics.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")


if __name__ == "__main__":
    main()
