"""refA_prooffirst_check.py -- Refuter A's checks on Proposer 1 (proof-first).

Targets (results/triangle-hunt-proof-first.md):
  T1  p1-two-term-lower-bound: T(n,H) >= 3T(n-1,H-1) + T(n-1,H), equality
      at H = n.  Checked on every banked cell; equality set located;
      tightness measured on the k=1 diagonal and globally; re-checked on
      Refuter A's own rule-independent TM data (H <= 6) out to n = 60,
      beyond the banked grid.
  T2  deficit-family congruences d = 3..6: residues recomputed from banked
      data, each holdout cell classified law-implied vs law-free using
      known.py's own predicates; the below-onset tail cells (k < d) of each
      line, which the candidates' region excludes, are measured too.
  T3  the d=3 pattern's zero placement (k == 1 mod 3) and the open-cell
      prediction T(40,26) == 1 (mod 3), checked directly.
  LUCK  empirical base rates of mod-3 residues over ALL 42 law-free sleeve
      cells (k = 14..19 in-grid), giving the a-priori pass probability of
      the three family predictions -- the number the lead asked for.
  FRAME  the claimed identity [y^k]F = R_k(z)/(1-3z)^(k+1): R_k recovered
      from banked diagonals as (1-3z)^(k+1) * D_k(z); verified to truncate
      to an integer polynomial of degree <= 2k+1 for k = 1..12, and the
      mod-9 refinement T(H+k,H) == r_{k,H} + 3(k+1) r_{k,H-1} checked.

Run from experiments/tristruct/:  python3 refA_prooffirst_check.py
"""

import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import known  # noqa: E402  (the cull baseline; used AS the standard)
from refA_columns_check import own_strip_series  # noqa: E402

NMAX = 40
FAILS = []


def report(name, ok, detail=""):
    print("%-64s %s  %s" % (name, "OK" if ok else "FAIL", detail))
    if not ok:
        FAILS.append(name)


def load_triangle():
    T = {}
    for H in range(1, NMAX + 1):
        with open(os.path.join(REPO, "results", "ns_a40", "perheight",
                               "h%d.out" % H)) as f:
            for line in f:
                n, v = line.split()
                T[(int(n), H)] = int(v)
    return T


class Shim:
    """Minimal tri interface for known.py predicates."""

    def __init__(self, T):
        self._T = T

    def cell(self, n, H):
        return self._T.get((n, H), 0)

    def col(self, H):
        return {n: self._T.get((n, H), 0) for n in range(1, NMAX + 1)}


def law_implied(tri, n, H):
    """Is the mod-3 residue of (n,H) implied by any banked relation?"""
    for kn in known.KNOWN:
        r = kn.predict_mod(tri, n, H, 3)
        if r is not None:
            assert r == tri.cell(n, H) % 3, (kn.name, n, H)
            return True
    return False


def main():
    T = load_triangle()
    tri = Shim(T)

    # ---------------- T1: inequality on every banked cell ----------------
    viol, eq = [], []
    ratios = []
    for n in range(2, NMAX + 1):
        for H in range(2, n + 1):
            lo = 3 * T.get((n - 1, H - 1), 0) + T.get((n - 1, H), 0)
            v = T[(n, H)]
            if v < lo:
                viol.append((n, H))
            elif v == lo:
                eq.append((n, H))
            elif lo:
                ratios.append((Fraction(v, lo), n, H))
    report("T1 inequality holds on all banked cells (2<=H<=n<=40)",
           not viol, "%d violations" % len(viol))
    report("T1 equality set is EXACTLY the H=n column",
           eq == [(n, n) for n in range(2, NMAX + 1)],
           "%d equalities" % len(eq))
    k1 = [(n, float(r)) for (r, n, H) in ratios if H == n - 1]
    k1.sort()
    print("T1 k=1 diagonal ratio T/(bound): " +
          ", ".join("n=%d:%.4f" % (n, r) for n, r in k1[::7] + k1[-1:]))
    rmin = min(ratios)
    rmax = max(ratios)
    print("T1 strict-cell ratio: min %.4f at (%d,%d); max %.3g at (%d,%d)"
          % (float(rmin[0]), rmin[1], rmin[2],
             float(rmax[0]), rmax[1], rmax[2]))
    mono = all(k1[i][1] > k1[i + 1][1] for i in range(len(k1) - 1))
    report("T1 k=1 ratio strictly decreasing in n (tightness claim)", mono)

    # ---- T1 on own rule-independent TM data, beyond the banked grid ----
    NOWN = 60
    S = {0: [0] * (NOWN + 1), -1: [0] * (NOWN + 1)}
    for H in range(1, 7):
        S[H], _ = own_strip_series(H, NOWN)
    To = {(n, H): S[H][n] - 2 * S[H - 1][n] + S[H - 2][n]
          for H in range(1, 7) for n in range(1, NOWN + 1)}
    bad = [(n, H) for n in range(2, NOWN + 1) for H in range(2, 7)
           if To[(n, H)] < 3 * To[(n - 1, H - 1)] + To[(n - 1, H)]]
    report("T1 holds on OWN TM data H<=6 out to n=60 (beyond grid)",
           not bad, "%d cells checked" % (5 * (NOWN - 1)))

    # ---------------- T2/T3: deficit families from banked ----------------
    def fam(d):
        out = []
        for k in range(d, 40):
            n, H = 3 * k + 1 - d, 2 * k + 1 - d
            if 1 <= H <= n <= NMAX:
                out.append((k, n, H))
        return out

    print()
    for d in (3, 4, 5, 6):
        rows = []
        for k, n, H in fam(d):
            rows.append((k, n, H, T[(n, H)] % 3,
                         "impl" if law_implied(tri, n, H) else "FREE"))
        print("d=%d: " % d + "  ".join(
            "k%d(%d,%d)=%d%s" % (k, n, H, r, "*" if tag == "FREE" else "")
            for k, n, H, r, tag in rows))
        # below-onset tail on the same line (k < d), excluded by the region
        tail = []
        for k in range(max(1, d - 3), d):
            n, H = 3 * k + 1 - d, 2 * k + 1 - d
            if 1 <= H <= n:
                tail.append((k, n, H, T[(n, H)] % 3))
        if tail:
            print("      below-onset tail (excluded): " + "  ".join(
                "k%d(%d,%d)=%d" % t for t in tail))

    d3 = {k: T[(3 * k - 2, 2 * k - 2)] % 3 for k in range(3, 15)}
    pat = {k: (2, 0, 1)[(k - 3) % 3] for k in range(3, 15)}
    report("T3 d=3 pattern 2,0,1 by (k-3) mod 3 holds k=3..14", d3 == pat)
    report("T3 zeros on d=3 line exactly at k == 1 (mod 3), k=3..14",
           all((r == 0) == (k % 3 == 1) for k, r in d3.items()))
    report("T3 open-cell prediction T(40,26) == 1 (mod 3)",
           T[(40, 26)] % 3 == 1, "banked residue %d" % (T[(40, 26)] % 3))
    report("T2 d=4 constant 2, k=4..14 (incl. law-free k=14, n=39)",
           all(T[(3 * k - 3, 2 * k - 3)] % 3 == 2 for k in range(4, 15)))
    report("T2 d=5 constant 2, k=5..14 (incl. law-free k=14, n=38)",
           all(T[(3 * k - 4, 2 * k - 4)] % 3 == 2 for k in range(5, 15)))
    d6 = [T[(3 * k - 5, 2 * k - 5)] % 3 for k in range(6, 15)]
    print("d=6 residues k=6..14: %s (no const tail / period<=4 => unfittable,"
          " matches CULLED(FIT-ERROR))" % d6)

    # ---------------- LUCK: base rates over law-free sleeve cells --------
    sleeve = []
    for k in range(14, 20):
        for n in range(2 * k + 1, min(3 * k + 1, NMAX) + 1):
            H = n - k
            assert not law_implied(tri, n, H), (n, H)
            sleeve.append((n, H, T[(n, H)] % 3))
    from collections import Counter
    cnt = Counter(r for _, _, r in sleeve)
    tot = len(sleeve)
    print()
    print("LUCK: %d law-free in-grid sleeve cells (k=14..19); residue "
          "distribution mod 3: %s" % (tot, dict(cnt)))
    p = {r: Fraction(cnt.get(r, 0), tot) for r in (0, 1, 2)}
    joint = p[1] * p[2] * p[2]  # d=3 predicts 1 at k=14; d=4,5 predict 2
    print("LUCK: empirical pass prob of the three family predictions "
          "(residues 1,2,2): %.4f * %.4f * %.4f = %.4f  (uniform null: "
          "(1/3)^3 = 0.0370)" % (float(p[1]), float(p[2]), float(p[2]),
                                 float(joint)))

    # ---------------- FRAME: R_k truncation + mod-9 identity -------------
    print()
    frame_ok = True
    for k in range(1, 13):
        D = [0] * (NMAX - k + 1)
        for H in range(1, NMAX - k + 1):
            D[H] = T.get((H + k, H), 0)
        # r_j = sum_i C(k+1,i) (-3)^i D_{j-i}
        from math import comb
        r = []
        for j in range(NMAX - k + 1):
            r.append(sum(comb(k + 1, i) * (-3) ** i * D[j - i]
                         for i in range(min(k + 1, j) + 1)))
        tail_zero = all(x == 0 for x in r[2 * k + 2:])
        deg = max((j for j, x in enumerate(r) if x != 0), default=0)
        mod9 = all((T.get((H + k, H), 0)
                    - (r[H] + 3 * (k + 1) * r[H - 1])) % 9 == 0
                   for H in range(1, NMAX - k + 1))
        if not (tail_zero and deg <= 2 * k + 1 and mod9):
            frame_ok = False
            print("FRAME k=%d: tail_zero=%s deg=%d mod9=%s"
                  % (k, tail_zero, deg, mod9))
    report("FRAME identity: R_k integer poly, deg <= 2k+1, mod-9 form, "
           "k=1..12", frame_ok)

    print()
    if FAILS:
        print("FAILURES:", FAILS)
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
