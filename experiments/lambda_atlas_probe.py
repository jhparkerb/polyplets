#!/usr/bin/env python3
"""Does coordination number set lambda, or does local cycle structure move it?

`results/unexplored-avenues.md` idea 4 (the lambda atlas) proposes a designed
family of row-local lattices and states a prediction before measuring:

> is lambda a function of coordination number, or does local cycle structure
> move it?
> Prediction to state before measuring: spread-8 should land noticeably above
> king's 7.11, toward the tree bound (q-1)^(q-1)/(q-2)^(q-2), because
> clustering suppresses lambda.

`docs/last-orders.md` C1.1.  The full atlas wants certified two-sided brackets
and is a compute item.  This is the cheap half that makes the prediction
falsifiable now: enumerate three lattices to the SAME small n by brute force,
estimate lambda the same way on each, and calibrate that estimator against the
two lattices whose lambda is known.

  square    q=4   D = {(+-1,0),(0,+-1)}                  lambda = 4.0626 (known)
  king      q=8   D = square + the four diagonals        lambda = 7.1102 (known)
  spread-8  q=8   D = {(+-1,0),(0,+-1),(+-2,0),(0,+-2)}  lambda = ?

Square and king are the controls: whatever bias a 9-term ratio estimate has,
it has on all three, and the two known values measure it.

RED controls:
  - square and king counts must reproduce A001168 and A006770;
  - spread-8 must have q = 8, same as king, or the comparison is not
    controlled;
  - spread-8 must NOT be isomorphic to king -- its triangle count per site
    must differ, which is the whole point of the design.

Usage: python3 experiments/lambda_atlas_probe.py [--nmax 9]
"""
import argparse
import sys

SQUARE = ((1, 0), (-1, 0), (0, 1), (0, -1))
KING = SQUARE + ((1, 1), (1, -1), (-1, 1), (-1, -1))
SPREAD8 = SQUARE + ((2, 0), (-2, 0), (0, 2), (0, -2))

A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446]
A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180]

KNOWN = {"square": 4.0626, "king": 7.1102}


def canon(cells):
    xs = min(c[0] for c in cells)
    ys = min(c[1] for c in cells)
    return frozenset((x - xs, y - ys) for x, y in cells)


def counts(nmax, nbrs):
    lv = {canon([(0, 0)])}
    out = [len(lv)]
    for _ in range(2, nmax + 1):
        nxt = set()
        for a in lv:
            for (x, y) in a:
                for dx, dy in nbrs:
                    c = (x + dx, y + dy)
                    if c not in a:
                        nxt.add(canon(set(a) | {c}))
        lv = nxt
        out.append(len(lv))
    return out


def triangles_per_site(nbrs):
    """Unordered triples {0, u, v} with u, v and u-v all in the neighbourhood.

    A measure of local cycle structure: how much the neighbourhood clusters.
    """
    s = set(nbrs)
    t = 0
    nb = list(nbrs)
    for i, u in enumerate(nb):
        for v in nb[i + 1:]:
            if (v[0] - u[0], v[1] - u[1]) in s:
                t += 1
    return t


def ratio_estimates(c):
    """a(n)/a(n-1), and a 1/n-corrected extrapolation from the last three."""
    r = [c[i] / c[i - 1] for i in range(1, len(c))]
    # r_n = lambda (1 + theta/n); solve on the last two ratios with theta free
    n2, n1 = len(c) - 1, len(c) - 2          # 1-based n of r[-1], r[-2]
    rn2, rn1 = r[-1], r[-2]
    # lam(1+t/n2)=rn2, lam(1+t/n1)=rn1  ->  two equations
    # rn2/rn1 = (1+t/n2)/(1+t/n1)
    k = rn2 / rn1
    # (1+t/n2) = k(1+t/n1) -> t(1/n2 - k/n1) = k - 1
    denom = (1.0 / n2 - k / n1)
    t = (k - 1) / denom if denom else float('nan')
    lam = rn2 / (1 + t / n2)
    return r, lam, t


def tree_bound(q):
    return (q - 1) ** (q - 1) / (q - 2) ** (q - 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=9)
    args = ap.parse_args()

    lattices = (("square", SQUARE), ("king", KING), ("spread-8", SPREAD8))

    print("=" * 74)
    print(f"Lambda atlas probe: three row-local lattices to n = {args.nmax}")
    print("=" * 74)
    print(f"{'lattice':>9} {'q':>3} {'triangles':>10}  counts")
    data = {}
    for name, nbrs in lattices:
        c = counts(args.nmax, nbrs)
        data[name] = c
        print(f"{name:>9} {len(nbrs):>3} {triangles_per_site(nbrs):>10}  "
              f"{c[:6]}...")
    print()

    print("--- Ratio ladders ---")
    for name, _ in lattices:
        r, lam, t = ratio_estimates(data[name])
        rs = "  ".join(f"{x:.3f}" for x in r[-5:])
        known = KNOWN.get(name)
        kn = f"   known {known}" if known else "   known --"
        print(f"  {name:>9}: last ratios {rs}")
        print(f"  {'':>9}  1/n-corrected lambda = {lam:.4f}  "
              f"(theta = {t:+.3f}){kn}")
    print()

    print("--- Calibration: how wrong is the estimator, where we can check? ---")
    biases = {}
    for name in ("square", "king"):
        _, lam, _ = ratio_estimates(data[name])
        b = lam / KNOWN[name]
        biases[name] = b
        print(f"  {name:>9}: estimate {lam:.4f} / known {KNOWN[name]} "
              f"= {b:.4f}")
    mb = sum(biases.values()) / len(biases)
    print(f"  mean bias {mb:.4f}; the two agree to "
          f"{abs(biases['square']-biases['king'])/mb*100:.1f}%")
    print()

    print("--- The prediction, tested ---")
    _, lam_s, _ = ratio_estimates(data["spread-8"])
    corrected = lam_s / mb
    print(f"  spread-8 raw estimate       {lam_s:.4f}")
    print(f"  bias-corrected              {corrected:.4f}")
    print(f"  king (known)                {KNOWN['king']:.4f}")
    print(f"  tree bound at q = 8         {tree_bound(8):.4f}")
    print()
    if corrected > KNOWN["king"]:
        frac = ((corrected - KNOWN['king'])
                / (tree_bound(8) - KNOWN['king']) * 100)
        print(f"  spread-8 lands ABOVE king, by {corrected-KNOWN['king']:.3f},")
        print(f"  which is {frac:.0f}% of the way from king to the tree bound.")
        print(f"  The idea-4 prediction is CONFIRMED in direction.")
    else:
        print(f"  spread-8 lands BELOW king. The idea-4 prediction is REFUTED.")
    print()

    print("--- RED controls ---")
    ok = True
    good = data["square"] == A001168[:len(data["square"])]
    print(f"RED  square reproduces A001168  {'OK' if good else 'FAILED'}")
    ok &= good
    good = data["king"] == A006770[:len(data["king"])]
    print(f"RED  king reproduces A006770  {'OK' if good else 'FAILED'}")
    ok &= good
    good = len(SPREAD8) == len(KING) == 8
    print(f"RED  spread-8 and king have the same coordination number 8  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good
    tk, ts = triangles_per_site(KING), triangles_per_site(SPREAD8)
    good = tk != ts
    print(f"RED  spread-8 is not king: triangles per site {ts} vs {tk}  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good
    good = data["spread-8"] != data["king"]
    print(f"RED  the two q=8 lattices give different counts  "
          f"{'OK' if good else 'FAILED'}")
    ok &= good

    if not ok:
        print("\nSELFTEST: FAILED")
        return 1
    print("\nSELFTEST: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
