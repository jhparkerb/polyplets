#!/usr/bin/env python3
"""Session 04: ground-truth JOINT table f(w,h;n) = # convex king animals with
bounding box exactly w x h and area (cell count) n, both king and polyomino
modes.  Two independent computations cross-checked:

  (A) definitional subset brute force over the w x h grid (HV-convex +
      connectivity + touch all four sides), area = popcount; boxes wh <= 16.
  (B) area-marked row-interval DP (the s01-validated model convex_box.g_table
      with each row weighted by its length); w,h <= WMAX, ALL areas.

Checks:
  1. (A) == (B) on every box wh <= 16, per-area, both modes.
  2. sum_n f(w,h;n) == banked convex_box f(w,h) for all w,h <= WMAX (q=1).
  3. king area marginal sum_{w,h} f(w,h;n) for n <= WMAX == convex_tm.py
     banked sequence (out_convex_tm_check.txt); polyomino marginal == the
     known convex-polyomino-by-area control terms (convex-mirage.md).

Output: out_s04_area_truth.json  {mode: {"w,h": {n: count}}}
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_box import g_table, f_from_g
from collections import defaultdict

WMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10

MIRAGE_KING = [1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834, 271174,
               853111, 2677214, 8389720, 26271014, 82230035, 257333334,
               805229818, 2519563026, 7883577553, 24667161861, 77181772540,
               241496421322, 755626445009, 2364307821370, 7397776287396,
               23147205741474, 72426263089887, 226617613513394,
               709073559601858]
MIRAGE_POLY = [1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312, 23320, 57279,
               138536, 331032]  # docs/proofs/convex-mirage.md control


def gq_table(wmax, hmax, king=True):
    """gq[w][h] = dict {n: count} over interval sequences inside [0,w)."""
    reach = 1 if king else 0
    gq = [[None] * (hmax + 1) for _ in range(wmax + 1)]
    for w in range(1, wmax + 1):
        nmax = w * hmax
        dp = {}
        for l in range(w):
            for r in range(l, w):
                key = (l, r, 0, 0)
                vec = [0] * (nmax + 1)
                vec[r - l + 1] = 1
                dp[key] = vec
        for h in range(1, hmax + 1):
            tot = defaultdict(int)
            for vec in dp.values():
                for n, v in enumerate(vec):
                    if v:
                        tot[n] += v
            gq[w][h] = dict(tot)
            if h == hmax:
                break
            ndp = {}
            for (l, r, pl, pr), vec in dp.items():
                lo_l = l if pl else 0
                hi_r = r if pr else w - 1
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        wp = rp - lp + 1
                        key = (lp, rp, npl, npr)
                        tgt = ndp.get(key)
                        if tgt is None:
                            tgt = [0] * (nmax + 1)
                            ndp[key] = tgt
                        for n, v in enumerate(vec):
                            if v and n + wp <= nmax:
                                tgt[n + wp] += v
            dp = ndp
    return gq


def fq_from_gq(gq, wmax, hmax):
    fq = [[None] * (hmax + 1) for _ in range(wmax + 1)]
    for w in range(1, wmax + 1):
        for h in range(1, hmax + 1):
            d = defaultdict(int)
            for n, c in gq[w][h].items():
                d[n] += c
            if w >= 2:
                for n, c in gq[w - 1][h].items():
                    d[n] -= 2 * c
            if w >= 3:
                for n, c in gq[w - 2][h].items():
                    d[n] += c
            fq[w][h] = {n: c for n, c in d.items() if c}
    return fq


def brute_box_area(w, h, king=True):
    """dict {n: count} of subsets: HV-convex + connected + touch 4 sides."""
    cells = [(x, y) for y in range(h) for x in range(w)]
    n = len(cells)
    if king:
        nbr = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               if (dx, dy) != (0, 0)]
    else:
        nbr = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    out = defaultdict(int)
    for mask in range(1, 1 << n):
        occ = [cells[i] for i in range(n) if mask >> i & 1]
        xs = [x for x, y in occ]
        ys = [y for x, y in occ]
        if min(xs) != 0 or max(xs) != w - 1 or min(ys) != 0 or max(ys) != h - 1:
            continue
        rows, cols = {}, {}
        for x, y in occ:
            rows.setdefault(y, []).append(x)
            cols.setdefault(x, []).append(y)
        if any(max(v) - min(v) + 1 != len(v) for v in rows.values()):
            continue
        if any(max(v) - min(v) + 1 != len(v) for v in cols.values()):
            continue
        occs = set(occ)
        seen = {occ[0]}
        stack = [occ[0]]
        while stack:
            x, y = stack.pop()
            for dx, dy in nbr:
                p = (x + dx, y + dy)
                if p in occs and p not in seen:
                    seen.add(p)
                    stack.append(p)
        if len(seen) == len(occ):
            out[len(occ)] += 1
    return dict(out)


def main():
    result = {}
    for king in (True, False):
        tag = "king" if king else "poly"
        gq = gq_table(WMAX, WMAX, king=king)
        fq = fq_from_gq(gq, WMAX, WMAX)

        # check 1: brute force per-area, wh <= 16
        nbad = 0
        ncmp = 0
        for w in range(1, WMAX + 1):
            for h in range(1, WMAX + 1):
                if w * h > 16:
                    continue
                b = brute_box_area(w, h, king=king)
                ncmp += 1
                if b != fq[w][h]:
                    nbad += 1
                    print(f"  {tag} MISMATCH box {w}x{h}: dp={fq[w][h]} "
                          f"brute={b}")
        print(f"{tag}: check1 brute-force per-area, {ncmp} boxes wh<=16: "
              f"{'OK' if nbad == 0 else 'FAIL'}")
        assert nbad == 0

        # check 2: q=1 marginal vs banked DP table
        g = g_table(WMAX, WMAX, king=king)
        f = f_from_g(g, WMAX, WMAX)
        bad = [(w, h) for w in range(1, WMAX + 1) for h in range(1, WMAX + 1)
               if sum(fq[w][h].values()) != f[w][h]]
        print(f"{tag}: check2 sum_n f(w,h;n) == f(w,h) all w,h<={WMAX}: "
              f"{'OK' if not bad else 'FAIL ' + str(bad[:5])}")
        assert not bad

        # check 3: area marginal vs banked area sequences (n <= WMAX:
        # any animal with n cells has w,h <= n <= WMAX, so marginal complete)
        marg = defaultdict(int)
        for w in range(1, WMAX + 1):
            for h in range(1, WMAX + 1):
                for n, c in fq[w][h].items():
                    marg[n] += c
        ref = MIRAGE_KING if king else MIRAGE_POLY
        got = [marg[n] for n in range(1, WMAX + 1)]
        want = ref[:WMAX]
        print(f"{tag}: check3 area marginal n<={WMAX} vs banked: "
              f"{'OK' if got == want else 'FAIL got ' + str(got)}")
        assert got == want

        result[tag] = {f"{w},{h}": fq[w][h]
                       for w in range(1, WMAX + 1) for h in range(1, WMAX + 1)}

    out = os.path.join(os.path.dirname(__file__), "..",
                       "out_s04_area_truth.json")
    with open(out, "w") as fh:
        json.dump(result, fh)
    print(f"joint truth table (w,h<={WMAX}, all areas, both modes) -> "
          f"out_s04_area_truth.json")


if __name__ == "__main__":
    main()
