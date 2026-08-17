#!/usr/bin/env python3
"""Session 04: validate the AREA-marked (q-deformed) functional equation for
convex king animals: same phase/transition system as s03_funceq_check.py, with
every new row of length k' additionally weighted q^{k'} (area = sum of row
lengths).  State (phase, k) -> dict {(w, n): count}, w = box width so far,
n = area so far.  Initial row of length k: weight x^k y (qs)^k.

Check: the resulting joint table f(w,h;n) equals the ground-truth table of
s04_area_truth.py (brute-force + interval-DP validated) for all w,h <= WMAX,
every area, king AND polyomino modes.
"""
import sys, os, json
from collections import defaultdict

WMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def qfe_table(W, H, king=True):
    """f[w][h] = dict {n: count} from the q-FE transitions."""
    dp = [defaultdict(lambda: defaultdict(int)) for _ in range(4)]
    for k in range(1, W + 1):
        dp[0][k][(k, k)] = 1
    f = [[defaultdict(int) for _ in range(H + 1)] for _ in range(W + 1)]

    def collect(dp, h):
        for ph in range(4):
            for k, d in dp[ph].items():
                for (w, n), c in d.items():
                    if w <= W:
                        f[w][h][n] += c

    collect(dp, 1)
    for h in range(2, H + 1):
        nd = [defaultdict(lambda: defaultdict(int)) for _ in range(4)]

        def add(ph, k, w, n, c):
            if k >= 1 and w <= W:
                nd[ph][k][(w, n)] += c

        for k in range(1, W + 1):
            for (w, n), c in dp[0][k].items():
                for u in range(0, W - w + 1):
                    for v in range(0, W - w - u + 1):
                        add(0, k + u + v, w + u + v, n + k + u + v, c)
                imax = k if king else k - 1
                for i in range(1, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, W - w + 1):
                        add(1, k + e - i, w + e, n + k + e - i, c)
                        add(2, k + e - i, w + e, n + k + e - i, c)
                for i in range(1, k - 1 + 1):
                    for j in range(1, k - 1 - i + 1):
                        add(3, k - i - j, w, n + k - i - j, c)
            for (w, n), c in dp[1][k].items():
                imax = k if king else k - 1
                for i in range(0, imax + 1):
                    emin = 1 if (king and i == k) else 0
                    for e in range(emin, W - w + 1):
                        add(1, k + e - i, w + e, n + k + e - i, c)
                for i in range(0, k - 1 + 1):
                    for j in range(1, k - 1 - i + 1):
                        add(3, k - i - j, w, n + k - i - j, c)
            for (w, n), c in dp[2][k].items():
                jmax = k if king else k - 1
                for j in range(0, jmax + 1):
                    umin = 1 if (king and j == k) else 0
                    for u in range(umin, W - w + 1):
                        add(2, k + u - j, w + u, n + k + u - j, c)
                for i in range(1, k - 1 + 1):
                    for j in range(0, k - 1 - i + 1):
                        add(3, k - i - j, w, n + k - i - j, c)
            for (w, n), c in dp[3][k].items():
                for i in range(0, k - 1 + 1):
                    for j in range(0, k - 1 - i + 1):
                        add(3, k - i - j, w, n + k - i - j, c)
        dp = nd
        collect(dp, h)
    return f


def main():
    path = os.path.join(os.path.dirname(__file__), "..",
                        "out_s04_area_truth.json")
    truth = json.load(open(path))
    for king in (True, False):
        tag = "king" if king else "poly"
        T = truth[tag]
        f = qfe_table(WMAX, WMAX, king=king)
        nbad = 0
        ncmp = 0
        for w in range(1, WMAX + 1):
            for h in range(1, WMAX + 1):
                want = {int(n): c for n, c in T[f"{w},{h}"].items()}
                got = {n: c for n, c in f[w][h].items() if c}
                ncmp += 1
                if got != want:
                    nbad += 1
                    if nbad <= 5:
                        print(f"  {tag} MISMATCH {w}x{h}: fe={got} "
                              f"truth={want}")
        print(f"{tag.upper()}: q-FE transitions vs ground truth, {ncmp} boxes "
              f"w,h<={WMAX}, per-area: {'OK' if nbad == 0 else 'FAIL'}")
        assert nbad == 0


if __name__ == "__main__":
    main()
