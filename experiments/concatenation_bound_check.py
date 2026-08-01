#!/usr/bin/env python3
"""What a concatenation (quasi sub-multiplicative) upper bound would buy for lambda.

Barequet-Ben-Shachar-Osegueda 2021 ("Concatenation arguments and their
applications to polyominoes and polycubes," Comput. Geom. 98, 101790) prove
growth-constant bounds from a SINGLE known term of the enumerating sequence,
given a quasi-multiplicativity relation:

  Theorem 1(a): if  Z(2n) <= c1 * n^c2 * Z(n)^2  for all n, and
                mu = lim Z(n)^(1/n) exists, then
                mu <= ( c1 * (2n)^c2 * Z(n) )^(1/n)   for every n.

We hold a(1..40) exactly for fixed king animals (A006770), so the question is
arithmetic: what would such a relation deliver, and how large may the slack
factor F = c1*(2n)^c2 be before the bound stops beating the banked certificate
lambda <= 9.3153?  A companion lower question: below which F is the relation
refuted outright by our own certified lower bound lambda >= 6.543?

Also: the measured ratio a(m+n)/(a(m)a(n)) that such a P must dominate, and the
same arithmetic for ordinary polyominoes, where the identical lemma would
improve the best known upper bound.

Run: python3 experiments/concatenation_bound_check.py
"""

from fractions import Fraction
from math import exp, log
from pathlib import Path

BFILE = Path(__file__).resolve().parent.parent / "results" / "b006770_upload.txt"

CERT_UPPER = 9.3153      # banked exact-rational certificate (Bui-style convolution)
CERT_LOWER = 6.543       # banked certified strip ladder, mu_17
LAMBDA_EST = 7.111       # confluent fit on 40 terms


def load_a():
    a = {}
    for line in BFILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()
        a[int(n)] = int(v)
    return a


def main():
    a = load_a()
    N = max(a)
    r = exp(log(a[N]) / N)          # a(N)^(1/N); a(40) ~ 5.7e31 fits a float fine
    print(f"banked a(1..{N}); a({N})^(1/{N}) = {r:.4f}   [the Fekete lower bound]")

    print("\n== 1. the slack window at n = 40 ==")
    print("   bound(F) = (F * a(40))^(1/40).  Useful iff bound < 9.3153;")
    print("   impossible iff bound < 6.543 (contradicts our certified ladder).")
    f_useful = (CERT_UPPER / r) ** N
    f_refuted = (CERT_LOWER / r) ** N
    f_est = (LAMBDA_EST / r) ** N
    print(f"   F < {f_refuted:.2f}          -> relation is REFUTED (rigorously)")
    print(f"   F < {f_est:.1f}         -> refuted modulo lambda ~ {LAMBDA_EST} (numeric only)")
    print(f"   F < {f_useful:.3g}      -> beats the 9.3153 certificate")
    print(f"   so the live window at n=40 is  {f_refuted:.1f} <= F <= {f_useful:.3g}.")

    print("\n== 2. what that window allows for the degree of P ==")
    c1 = 1.002
    for c2 in range(0, 6):
        F = c1 * (2 * N) ** c2
        b = exp((log(F) + log(a[N])) / N)
        if b < CERT_LOWER:
            verdict = "REFUTED by the certified lower bound"
        elif b < LAMBDA_EST:
            verdict = f"refuted numerically (below lambda ~ {LAMBDA_EST})"
        elif b < CERT_UPPER:
            verdict = "USEFUL -- would beat 9.3153"
        else:
            verdict = "no gain over 9.3153"
        print(f"   deg P = {c2}:  F = {F:12.1f}   lambda <= {b:7.4f}   {verdict}")
    print("   => a concatenation lemma helps iff deg P <= 3.")
    print("      BBO's convex-polyomino P is deg 2 (mn + 2(m+n) + 1), which would")
    print(f"      give lambda <= {exp((log(c1 * (2*N)**2) + log(a[N])) / N):.4f}.")

    print("\n== 3. the ratio the lemma must bound: a(m+n) / (a(m) a(n)) ==")
    C = a[N] * N / (LAMBDA_EST ** N)     # a(n) ~ C lambda^n / n  (theta = -1)
    for s in (10, 20, 30, 40):
        vals = [(m, s - m, Fraction(a[s], a[m] * a[s - m])) for m in range(1, s // 2 + 1)]
        m, k, ratio = max(vals, key=lambda t: t[2])
        print(f"   m+n={s:2d}: max at ({m},{k})  ratio {float(ratio):8.2f}"
              f"    mn/(C(m+n)) = {m * k / (C * s):8.2f}")
    print(f"   (C = {C:.4f} from a(40) and lambda = {LAMBDA_EST})")
    print("   the ratio grows LINEARLY in m+n, exactly as a(n) ~ C lambda^n / n")
    print("   predicts. Nothing in 40 terms refutes quasi sub-multiplicativity;")
    print("   a deg-2 P is consistent with every banked term.")

    print("\n== 4. what more terms would buy (deg-2 P, ESTIMATED via the fit) ==")
    for n in (40, 50, 60, 80, 120, 200):
        an = a[n] if n in a else C * LAMBDA_EST ** n / n
        b = exp((log(c1 * (2 * n) ** 2) + log(an)) / n)
        tag = "exact" if n in a else "est."
        print(f"   n = {n:3d} ({tag}):  lambda <= {b:.4f}")
    print("   slow: the (2n)^2 factor decays like exp(2 ln(2n)/n).")

    print("\n== 5. the same lemma applied to ordinary polyominoes (A001168) ==")
    poly_root56 = 3.7031          # BBO sec. 2.1: A(56)^(1/56)
    poly_bound = poly_root56 * exp(2 * log(2 * 56) / 56)
    print(f"   A(56)^(1/56) = {poly_root56}  (BBO sec. 2.1)")
    print(f"   a deg-2 relation would give lambda_poly <= {poly_bound:.4f}")
    print("   best known upper bound: 4.5252 (Barequet-Shalah 2016, C_21 twigs)")
    print(f"   => the missing lemma would beat the Klarner-Rivest line by "
          f"{4.5252 - poly_bound:.4f},")
    print("      with no computation beyond already-published terms.")


def comb(k, arm=1):
    """King animal: a vertical spine at x=0 with k+1 teeth to the right,
    teeth two rows apart (the minimum that keeps them king-independent)."""
    cells = {(0, y) for y in range(3 * k + 1)}
    for i in range(k + 1):
        for x in range(1, arm + 1):
            cells.add((x, 3 * i))
    return cells


def components(cells):
    """King-connectivity components of a cell set."""
    seen, comps = set(), 0
    for c in cells:
        if c in seen:
            continue
        comps += 1
        stack = [c]
        seen.add(c)
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in cells and nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
    return comps


def worst_split(cells):
    """Max components on either side over all lexicographic split ranks."""
    order = sorted(cells)                      # by x then y == BBO's order
    worst = 0
    for m in range(1, len(order)):
        worst = max(worst, components(set(order[:m])), components(set(order[m:])))
    return worst


def shattering():
    print("\n== 6. why the split argument does not port: measured shattering ==")
    print("   BBO's Theorem 8 needs the lex split of an (m+n)-cell member to land")
    print("   in O(1) pieces per side (convexity gives <= 2, one of them a stick).")
    print("   For king animals a comb shatters:")
    print("     n   cells  worst #components over all split ranks")
    for k in (2, 4, 6, 8, 12, 16):
        cells = comb(k)
        print(f"    k={k:2d}  {len(cells):4d}   {worst_split(cells):4d}"
              f"     (= k+1 = ~n/4)")
    print("   => Theta(n) pieces, each needing its own vertical offset to be")
    print("      restored: n^Theta(n) codes, super-exponential, not a P(x).")
    print("   The other split that DOES keep both sides connected -- cut a spanning")
    print("   tree at a centroid edge -- cannot prescribe the two sizes to within")
    print("   O(1), which is what Theorem 1(a)/(b) require; approximate splits give")
    print("   only the convolution form a(n) <= K n^2 sum_m a(m)a(n-m), which every")
    print("   sequence with a(n) ~ C lambda^n / n satisfies outright: no info on lambda.")


if __name__ == "__main__":
    main()
    shattering()
