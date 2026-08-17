#!/usr/bin/env python3
"""Session 07: first and second AREA MOMENTS of convex king animals
(+ polyomino control) by exact bounding box, then by semiperimeter.

M_r(w,h) = sum over convex animals with bounding box exactly w x h of
area^r  (r=0,1,2).  M_0 is the banked f(w,h).

Method: the s01-validated row-interval DP (convex_box.g_table model),
extended to carry (count, sum area, sum area^2) per state.  Adding a row
of length k maps (c, m1, m2) -> contributes (c, m1 + k c, m2 + 2 k m1 +
k^2 c) to the successor state.  Exact-width extraction by the same second
difference in w as f_from_g (valid: moment weights are translation
invariant, the operator is linear).

Validations (all hard asserts):
  V1. definitional subset brute force (independent: raw subsets, area =
      popcount) for all boxes wh <= 16, r=0,1,2, king AND polyomino.
  V2. r=0 table == convex_box.g_table/f_from_g output (w,h <= 12).
  V3. against the s04 joint truth table out_s04_area_truth.json:
      M_r(w,h) == sum_n n^r f(w,h;n) for all w,h <= 10, both modes.
  V4. transpose symmetry M_r(w,h) == M_r(h,w).

Output: semiperimeter moment sequences a_r(s) = sum_{w+h=s} M_r(w,h),
s = 2..SMAX, both modes -> out_s07_area_moments.json (+ .txt receipt).

Usage: python3 experiments/s07_area_moments.py [SMAX]
"""
import sys, os, json
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from convex_box import g_table, f_from_g

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SMAX = (int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit()
        else 37)


def gm_table(wmax, hmax_of_w, king=True):
    """gm[w][h] = (G0,G1,G2) moment sums over interval sequences in [0,w)."""
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
                dp[(l, r, 0, 0)] = (1, k, k * k)
        for h in range(1, hmax + 1):
            G0 = G1 = G2 = 0
            for (c, m1, m2) in dp.values():
                G0 += c; G1 += m1; G2 += m2
            gm[(w, h)] = (G0, G1, G2)
            if h == hmax:
                break
            ndp = defaultdict(lambda: [0, 0, 0])
            for (l, r, pl, pr), (c, m1, m2) in dp.items():
                lo_l = l if pl else 0
                hi_r = r if pr else w - 1
                for lp in range(lo_l, min(r + reach, w - 1) + 1):
                    npl = pl or (1 if lp > l else 0)
                    rp_lo = max(lp, l - reach)
                    for rp in range(rp_lo, hi_r + 1):
                        npr = pr or (1 if rp < r else 0)
                        k = rp - lp + 1
                        e = ndp[(lp, rp, npl, npr)]
                        e[0] += c
                        e[1] += m1 + k * c
                        e[2] += m2 + 2 * k * m1 + k * k * c
            dp = {s: tuple(v) for s, v in ndp.items()}
    return gm


def m_from_gm(gm, w, h):
    def g(ww):
        return gm.get((ww, h), (0, 0, 0)) if ww >= 1 else (0, 0, 0)
    a, b, c = g(w), g(w - 1), g(w - 2)
    return tuple(a[i] - 2 * b[i] + c[i] for i in range(3))


# ---------- V1: definitional brute force ----------
def brute_box_moments(w, h, king=True):
    cells = [(x, y) for y in range(h) for x in range(w)]
    n = len(cells)
    s0 = s1 = s2 = 0
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
        s0 += 1; s1 += a; s2 += a * a
    return (s0, s1, s2)


def main():
    wmax = SMAX - 1
    out = {}
    truth = json.load(open(os.path.join(ROOT, "out_s04_area_truth.json")))
    txt = []
    for king, mode in ((True, "king"), (False, "poly")):
        gm = gm_table(wmax, lambda w: min(SMAX - w, wmax), king=king)
        M = {}
        for w in range(1, wmax + 1):
            for h in range(1, min(SMAX - w, wmax) + 1):
                M[(w, h)] = m_from_gm(gm, w, h)

        # V1 brute force
        for w in range(1, 9):
            for h in range(1, 9):
                if w * h > 16:
                    continue
                b = brute_box_moments(w, h, king=king)
                assert b == M[(w, h)], ("V1", mode, w, h, b, M[(w, h)])
        txt.append(f"[{mode}] V1 brute force wh<=16, r=0,1,2: OK")

        # V2 counts vs banked DP
        g = g_table(12, 12, king=king)
        f = f_from_g(g, 12, 12)
        nv2 = 0
        for w in range(1, 13):
            for h in range(1, 13):
                if (w, h) in M:
                    assert f[w][h] == M[(w, h)][0], ("V2", mode, w, h)
                    nv2 += 1
        txt.append(f"[{mode}] V2 r=0 == convex_box f(w,h), w,h<=12 "
                   f"({nv2} cells): OK")

        # V3 joint truth table
        tt = truth[mode]
        nv3 = 0
        for key, dist in tt.items():
            w, h = map(int, key.split(","))
            if (w, h) not in M:
                continue
            m0 = sum(dist.values())
            m1 = sum(int(n) * c for n, c in dist.items())
            m2 = sum(int(n) ** 2 * c for n, c in dist.items())
            assert (m0, m1, m2) == M[(w, h)], ("V3", mode, w, h)
            nv3 += 1
        txt.append(f"[{mode}] V3 == s04 joint truth table ({nv3} boxes): OK")

        # V4 transpose symmetry
        for (w, h), v in M.items():
            if (h, w) in M:
                assert M[(h, w)] == v, ("V4", mode, w, h)
        txt.append(f"[{mode}] V4 transpose symmetry: OK")

        seqs = {r: [] for r in range(3)}
        for s in range(2, SMAX + 1):
            tot = [0, 0, 0]
            for w in range(1, s):
                h = s - w
                v = M.get((w, h))
                assert v is not None, (mode, s, w, h)
                for i in range(3):
                    tot[i] += v[i]
            for r in range(3):
                seqs[r].append(tot[r])
        out[mode] = {f"a{r}": seqs[r] for r in range(3)}
        for r in range(3):
            txt.append(f"[{mode}] a{r}(s), s=2..{SMAX}: "
                       + ", ".join(map(str, seqs[r][:12])) + " ...")
            txt.append(f"[{mode}]   a{r}({SMAX}) = {seqs[r][-1]}")

    suffix = "" if SMAX == 37 else str(SMAX)
    with open(os.path.join(ROOT, f"out_s07_area_moments{suffix}.json"), "w") as fp:
        json.dump({"smax": SMAX, "start": 2, **out}, fp)
    body = "\n".join(txt)
    with open(os.path.join(ROOT, f"out_s07_area_moments{suffix}.txt"), "w") as fp:
        fp.write(__doc__ + "\n" + body + "\n")
    print(body)


if __name__ == "__main__":
    main()
