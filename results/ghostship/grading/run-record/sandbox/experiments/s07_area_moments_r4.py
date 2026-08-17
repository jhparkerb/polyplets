#!/usr/bin/env python3
"""Session 07: area moments r=0..4 of convex king animals (+ control) by
semiperimeter — generalization of s07_area_moments.py (same validated
row-interval DP model), written to TEST the registered limit-law
prediction out_s07_limit_law_prediction.txt (r=3,4 constants).

State carries (m0..m4); adding a row of length k updates
  m_r' += sum_j C(r,j) k^(r-j) m_j   (area shift by k).

Validations: V1 definitional brute force wh<=16 (r<=4, both modes);
V3 s04 joint truth table (r<=4, w,h<=10, both modes); V4 transpose.

Output: out_s07_area_moments_r4_{SMAX}.json / .txt

Usage: python3 experiments/s07_area_moments_r4.py [SMAX]
"""
import sys, os, json
from collections import defaultdict
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s07_area_moments import brute_box_moments  # reuse V1 core (r<=2)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 56
R = 4


def shift(m, k):
    """moment vector of X+k given that of X (counts weighted)."""
    return tuple(sum(comb(r, j) * k ** (r - j) * m[j] for j in range(r + 1))
                 for r in range(R + 1))


def gm_table(wmax, hmax_of_w, king=True):
    reach = 1 if king else 0
    gm = {}
    for w in range(1, wmax + 1):
        hmax = hmax_of_w(w)
        if hmax < 1:
            continue
        dp = {}
        for l in range(w):
            for r in range(l, w):
                k = r - l + 1
                dp[(l, r, 0, 0)] = tuple(k ** j for j in range(R + 1))
        for h in range(1, hmax + 1):
            tot = [0] * (R + 1)
            for m in dp.values():
                for i in range(R + 1):
                    tot[i] += m[i]
            gm[(w, h)] = tuple(tot)
            if h == hmax:
                break
            ndp = defaultdict(lambda: [0] * (R + 1))
            for (l, r, pl, pr), m in dp.items():
                lo_l = l if pl else 0
                hi_r = r if pr else w - 1
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        k = rp - lp + 1
                        sm = shift(m, k)
                        e = ndp[(lp, rp, npl, npr)]
                        for i in range(R + 1):
                            e[i] += sm[i]
            dp = {s: tuple(v) for s, v in ndp.items()}
    return gm


def m_from_gm(gm, w, h):
    def g(ww):
        return gm.get((ww, h), (0,) * (R + 1)) if ww >= 1 else (0,) * (R + 1)
    a, b, c = g(w), g(w - 1), g(w - 2)
    return tuple(a[i] - 2 * b[i] + c[i] for i in range(R + 1))


def brute_r4(w, h, king):
    """definitional brute force, moments r<=4 (independent recount)."""
    from convex_box import brute_box  # noqa: F401 (import proves availability)
    # reimplement with area powers using the s07 brute machinery internals
    import itertools
    cells = [(x, y) for y in range(h) for x in range(w)]
    n = len(cells)
    tot = [0] * (R + 1)
    for mask in range(1, 1 << n):
        occ = [cells[i] for i in range(n) if mask >> i & 1]
        xs = [x for x, y in occ]; ys = [y for x, y in occ]
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
        occs = set(occ); seen = {occ[0]}; stack = [occ[0]]
        if king:
            nbrs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if (dx, dy) != (0, 0)]
        else:
            nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while stack:
            x, y = stack.pop()
            for dx, dy in nbrs:
                p = (x + dx, y + dy)
                if p in occs and p not in seen:
                    seen.add(p); stack.append(p)
        if len(seen) != len(occ):
            continue
        a = len(occ)
        for i in range(R + 1):
            tot[i] += a ** i
    return tuple(tot)


def main():
    wmax = SMAX - 1
    truth = json.load(open(os.path.join(ROOT, "out_s04_area_truth.json")))
    out = {}
    txt = []
    for king, mode in ((True, "king"), (False, "poly")):
        gm = gm_table(wmax, lambda w: min(SMAX - w, wmax), king=king)
        M = {}
        for w in range(1, wmax + 1):
            for h in range(1, min(SMAX - w, wmax) + 1):
                M[(w, h)] = m_from_gm(gm, w, h)

        for w in range(1, 9):
            for h in range(1, 9):
                if w * h > 16:
                    continue
                b = brute_r4(w, h, king)
                assert b == M[(w, h)], ("V1", mode, w, h, b, M[(w, h)])
        txt.append(f"[{mode}] V1 brute force wh<=16, r=0..4: OK")

        nv3 = 0
        for key, dist in truth[mode].items():
            w, h = map(int, key.split(","))
            if (w, h) not in M:
                continue
            mom = tuple(sum(int(n) ** r * c for n, c in dist.items())
                        for r in range(R + 1))
            assert mom == M[(w, h)], ("V3", mode, w, h)
            nv3 += 1
        txt.append(f"[{mode}] V3 == s04 joint truth table r=0..4 ({nv3} boxes): OK")

        for (w, h), v in M.items():
            if (h, w) in M:
                assert M[(h, w)] == v, ("V4", mode, w, h)
        txt.append(f"[{mode}] V4 transpose symmetry: OK")

        seqs = {r: [] for r in range(R + 1)}
        for s in range(2, SMAX + 1):
            tot = [0] * (R + 1)
            for w in range(1, s):
                v = M[(w, s - w)]
                for i in range(R + 1):
                    tot[i] += v[i]
            for r in range(R + 1):
                seqs[r].append(tot[r])
        out[mode] = {f"a{r}": seqs[r] for r in range(R + 1)}
        for r in range(R + 1):
            txt.append(f"[{mode}] a{r}({SMAX}) = {seqs[r][-1]}")

    with open(os.path.join(ROOT, f"out_s07_area_moments_r4_{SMAX}.json"), "w") as fp:
        json.dump({"smax": SMAX, "start": 2, **out}, fp)
    body = "\n".join(txt)
    with open(os.path.join(ROOT, f"out_s07_area_moments_r4_{SMAX}.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")
    print(body)


if __name__ == "__main__":
    main()
