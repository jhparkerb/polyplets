#!/usr/bin/env python3
"""Session 07: optimized rewrite of s07_area_moments_r4.py (unrolled
moment-shift transitions, no per-transition comb()); same validations
V1 (definitional brute force, r<=4, wh<=16), V3 (s04 joint truth table),
V4 (transpose).  Output identical format: out_s07_area_moments_r4_{SMAX}.json

Usage: python3 experiments/s07_area_moments_r4b.py [SMAX]
"""
import sys, os, json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s07_area_moments_r4 import brute_r4  # same definitional check

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SMAX = (int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit()
        else 57)
R = 4


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
                dp[(l, r, 0, 0)] = [1, k, k * k, k ** 3, k ** 4]
        for h in range(1, hmax + 1):
            tot = [0] * 5
            for m in dp.values():
                tot[0] += m[0]; tot[1] += m[1]; tot[2] += m[2]
                tot[3] += m[3]; tot[4] += m[4]
            gm[(w, h)] = tuple(tot)
            if h == hmax:
                break
            ndp = defaultdict(lambda: [0, 0, 0, 0, 0])
            for (l, r, pl, pr), m in dp.items():
                m0, m1, m2, m3, m4 = m
                lo_l = l if pl else 0
                hi_r = r if pr else w - 1
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        k = rp - lp + 1
                        k2 = k * k; k3 = k2 * k; k4 = k2 * k2
                        e = ndp[(lp, rp, npl, npr)]
                        e[0] += m0
                        e[1] += m1 + k * m0
                        e[2] += m2 + 2 * k * m1 + k2 * m0
                        e[3] += m3 + 3 * k * m2 + 3 * k2 * m1 + k3 * m0
                        e[4] += (m4 + 4 * k * m3 + 6 * k2 * m2
                                 + 4 * k3 * m1 + k4 * m0)
            dp = ndp
    return gm


def m_from_gm(gm, w, h):
    z = (0,) * 5
    a = gm.get((w, h), z)
    b = gm.get((w - 1, h), z) if w >= 2 else z
    c = gm.get((w - 2, h), z) if w >= 3 else z
    return tuple(a[i] - 2 * b[i] + c[i] for i in range(5))


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
                assert b == M[(w, h)], ("V1", mode, w, h)
        txt.append(f"[{mode}] V1 brute force wh<=16, r=0..4: OK")
        nv3 = 0
        for key, dist in truth[mode].items():
            w, h = map(int, key.split(","))
            if (w, h) not in M:
                continue
            mom = tuple(sum(int(n) ** r * c for n, c in dist.items())
                        for r in range(5))
            assert mom == M[(w, h)], ("V3", mode, w, h)
            nv3 += 1
        txt.append(f"[{mode}] V3 == s04 joint truth table r=0..4 ({nv3} boxes): OK")
        for (w, h), v in M.items():
            if (h, w) in M:
                assert M[(h, w)] == v, ("V4", mode, w, h)
        txt.append(f"[{mode}] V4 transpose symmetry: OK")
        seqs = {r: [] for r in range(5)}
        for s in range(2, SMAX + 1):
            tot = [0] * 5
            for w in range(1, s):
                v = M[(w, s - w)]
                for i in range(5):
                    tot[i] += v[i]
            for r in range(5):
                seqs[r].append(tot[r])
        out[mode] = {f"a{r}": seqs[r] for r in range(5)}
        for r in range(5):
            txt.append(f"[{mode}] a{r}({SMAX}) = {seqs[r][-1]}")
    with open(os.path.join(ROOT, f"out_s07_area_moments_r4_{SMAX}.json"),
              "w") as fp:
        json.dump({"smax": SMAX, "start": 2, **out}, fp)
    body = "\n".join(txt)
    with open(os.path.join(ROOT, f"out_s07_area_moments_r4_{SMAX}.txt"),
              "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")
    print(body)


if __name__ == "__main__":
    main()
