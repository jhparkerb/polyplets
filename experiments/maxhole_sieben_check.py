#!/usr/bin/env python3
"""M(n) is Sieben's minimum-site-perimeter theorem, inverted.

results/subclasses.md gave M(n) = floor(((n-2)^2 + 4)/8) for the maximum
enclosed empty area of an n-cell king animal, and proved the single-hole case
here from scratch (the (I') parity count, the (II') moat-cycle winding
argument, and the diagonal-box construction).

The literature already had it, twice. Sieben 2008 (European J. Combin. 29(1)
108-117) gives the minimum SITE-perimeter -- the number of empty cells
edge-adjacent to the shape -- of an n-cell polyomino, and its inverse:

    Thm 5.3   eps(s)  = ceil(2 + sqrt(8s - 4))      min site-perimeter, size s
    Thm 4.1   sigma(e) = floor(e^2/8 - e/2 + 1)     max size, site-perimeter e

sigma IS M, with no inversion at all: floor(e^2/8 - e/2 + 1) = M(e).

A sealed hole is a polyomino, every cell edge-adjacent to it from outside is
foreground, so n >= eps(A). That is the single-hole bound.

Altshuler, Yanovsky, Vainsencher, Wagner & Bruckstein (DGCI 2006, LNCS 4245,
17-28) prove the same numbers for an ARBITRARY finite subset of Z^2 -- no
connectivity hypothesis anywhere (their Thm 1, and the self-contained
slanted-bounding-rectangle argument of their Thm 7). Applied to the union of
ALL the holes at once, that closes the multi-hole case: the union's
4-neighbourhood is still foreground, so n >= eps(total area), and the overlap
question the earlier note stopped on never arises.

Checks (the papers are held locally now, literature/INDEX.txt; the formulas are
still checked here rather than taken on trust):

  1. eps brute-forced over all fixed polyominoes n <= NMAX_BRUTE, against
     the formula. RED control: the off-by-one variant must NOT match.
  2. M(n) = max{A : eps(A) <= n}, i.e. the two statements are the same
     statement, over n <= NMAX_INV.
  3. The tightness half: eps(M(n) + 1) > n.
  4. M superadditive, M(a) + M(b) <= M(a+b) for a, b >= 4 -- the far-apart
     multi-hole case, which needs no overlap argument.
  5. Banked M(n) from results/maxhole.txt, n <= 17.
  6. Sieben's eps == Altshuler et al.'s n(k), i.e. the two papers state one
     theorem. Also sigma(e) == M(e) directly.
  7. The hypothesis the multi-hole closure rests on: DISCONNECTED subsets do
     not beat eps. Exhaustive over every >=2-component subset of size
     k <= KMAX_DC built from components placed at every relative offset.

Usage: python3 -m experiments.maxhole_sieben_check
"""
import math
import os
import sys

NMAX_BRUTE = 9
NMAX_INV = 2000
NMAX_AREA = 200000
KMAX_DC = 10          # exhaustive 2-component search up to this total size
KMAX_DC3 = 8          # ... and 3-component up to this one
OFFSET_DC = 5         # relative placements: components within +-5 of each other
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXHOLE_TXT = os.path.join(ROOT, "results", "maxhole.txt")
STEPS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def ceil_sqrt(x):
    r = math.isqrt(x)
    return r if r * r == x else r + 1


def sp_min(a):
    """Sieben's minimum site-perimeter of an a-cell polyomino."""
    return ceil_sqrt(8 * a - 4) + 2


def M(n):
    """The maxhole formula, no rounding convention."""
    return ((n - 2) ** 2 + 4) // 8


def site_perimeter(cells):
    return len({(x + dx, y + dy) for (x, y) in cells for dx, dy in STEPS4}
               - cells)


def grow(polys):
    """All fixed polyominoes with one more cell, normalized to the origin."""
    out = set()
    for p in polys:
        for (x, y) in p:
            for dx, dy in STEPS4:
                c = (x + dx, y + dy)
                if c in p:
                    continue
                q = p | {c}
                mx = min(a for a, _ in q)
                my = min(b for _, b in q)
                out.add(frozenset((a - mx, b - my) for a, b in q))
    return out


def check_brute():
    """(1) Sieben's formula, brute-forced. Plus a RED control."""
    print(f"[1] min site-perimeter by brute force, n <= {NMAX_BRUTE}")
    print("      n    polyominoes   brute   Sieben   red")
    polys = {frozenset({(0, 0)})}
    ok = True
    red_ever_matched = False
    for n in range(1, NMAX_BRUTE + 1):
        if n > 1:
            polys = grow(polys)
        brute = min(site_perimeter(set(p)) for p in polys)
        want = sp_min(n)
        red = ceil_sqrt(8 * n - 4) + 1          # RED control: off by one
        ok &= brute == want
        red_ever_matched |= brute == red
        print(f"    {n:>3} {len(polys):>14} {brute:>7} {want:>8} {red:>5}"
              f"   {'' if brute == want else '  MISMATCH'}")
    if not ok:
        print("    FAIL: Sieben's formula does not match brute force")
        return False
    if red_ever_matched:
        print("    FAIL: the RED control matched -- the check discriminates "
              "nothing")
        return False
    print("    OK, and the off-by-one control never matches")
    return True


def check_inversion():
    """(2)+(3) M(n) = max{A : sp_min(A) <= n}, both directions."""
    print(f"\n[2] M(n) = max area with sp_min(A) <= n, n = 4..{NMAX_INV}")
    bad = [(n, a) for n in range(4, NMAX_INV + 1)
           for a in (M(n),) if sp_min(a) > n]
    tight = [n for n in range(3, NMAX_INV + 1) if sp_min(M(n) + 1) <= n]
    if bad:
        print(f"    FAIL: M(n) not reachable at {bad[:5]}")
        return False
    if tight:
        print(f"    FAIL: M(n)+1 also reachable at n = {tight[:5]}")
        return False
    print("    OK, and M(n)+1 is never reachable -- the two statements are one")

    print(f"\n[3] sp_min(A) <= n <=> A <= M(n) at every A <= {NMAX_AREA}")
    bad = [a for a in range(1, NMAX_AREA + 1)
           if not (a <= M(sp_min(a))) or a <= M(sp_min(a) - 1)]
    if bad:
        print(f"    FAIL at A = {bad[:5]}")
        return False
    print(f"    OK, {NMAX_AREA} areas, tight at each")
    return True


def check_superadditive():
    """(4) The multi-hole bound, modulo overlap."""
    print("\n[4] M(a) + M(b) <= M(a+b) for 4 <= a, b < 400")
    bad = [(a, b) for a in range(4, 400) for b in range(4, 400)
           if M(a) + M(b) > M(a + b)]
    if bad:
        print(f"    FAIL at {bad[:5]}")
        return False
    print("    OK -- so disjoint sealing sets would close the multi-hole case")
    return True


def sigma(e):
    """Sieben Thm 4.1: max size of an animal of site-perimeter e."""
    return (e * e - 4 * e + 8) // 8


def n_altshuler(k):
    """Altshuler et al. Thm 1: min |N(A)| over ALL finite A subset Z^2, |A|>=k.

    No connectivity hypothesis -- that is the whole point. (m, i) is scanned
    lexicographically with priority to m; caps[i] is their four cases.
    """
    if k <= 0:
        return 0
    m = 0
    while True:
        caps = (2 * m * m + 2 * m + 1, 2 * m * m + 3 * m + 1,
                2 * m * m + 4 * m + 2, 2 * m * m + 5 * m + 3)
        for i in range(4):
            if k <= caps[i]:
                return 4 * (m + 1) + i
        m += 1


def check_papers_agree():
    """(6) The two papers state one theorem, and sigma is M on the nose."""
    print(f"\n[6] Sieben eps(k) == Altshuler n(k), k <= {NMAX_AREA}")
    bad = [k for k in range(1, NMAX_AREA + 1) if sp_min(k) != n_altshuler(k)]
    if bad:
        print(f"    FAIL: they disagree at k = {bad[:5]} "
              f"(eps={sp_min(bad[0])}, n={n_altshuler(bad[0])})")
        return False
    print("    OK -- the connected and the arbitrary-subset minima coincide")
    print(f"    sigma(e) = floor(e^2/8 - e/2 + 1) == M(e), e = 4..{NMAX_INV}")
    # e = 5 is outside Sieben's Thm 4.1 domain (no animal has site-perimeter
    # 5); M(5) = sigma(4) = 1 all the same, so the closed form needs no case.
    bad = [e for e in range(4, NMAX_INV + 1) if sigma(e) != M(e)]
    if bad:
        print(f"    FAIL at e = {bad[:5]}")
        return False
    print("    OK -- M is Sieben's sigma verbatim, no inversion needed")
    return True


# --- (7) the multi-hole hypothesis: disconnected subsets do not beat eps ----
#
# Cells are packed one per bit at (x + PAD) * STRIDE + (y + PAD), so a
# relative placement is a single shift by dx * STRIDE + dy. Sizes <= 10 and
# offsets <= 5 keep every coordinate inside the padding, so nothing wraps.
STRIDE = 32
PAD = 8


def _masks(cells):
    """(occupied, 4-neighbourhood) as bitmasks, for a normalized polyomino."""
    c = n = 0
    for (x, y) in cells:
        c |= 1 << ((x + PAD) * STRIDE + (y + PAD))
    for (x, y) in cells:
        for dx, dy in STEPS4:
            n |= 1 << ((x + dx + PAD) * STRIDE + (y + dy + PAD))
    return c, n


def _shift(mask, dx, dy):
    d = dx * STRIDE + dy
    return mask << d if d >= 0 else mask >> -d


def _by_size(nmax):
    out = {}
    polys = {frozenset({(0, 0)})}
    for n in range(1, nmax + 1):
        if n > 1:
            polys = grow(polys)
        out[n] = [_masks(p) for p in polys]
    return out


def check_disconnected():
    """(7) Every >=2-component subset of size k, over a window of offsets."""
    print(f"\n[7] disconnected subsets vs eps(k), k <= {KMAX_DC} (pairs), "
          f"{KMAX_DC3} (triples)")
    print("      k   eps(k)   best 2-comp   best 3-comp   configurations")
    by_size = _by_size(KMAX_DC - 1)
    offs = [(dx, dy) for dx in range(-OFFSET_DC, OFFSET_DC + 1)
            for dy in range(-OFFSET_DC, OFFSET_DC + 1)]
    offs3 = [(dx, dy) for dx in range(-3, 4) for dy in range(-3, 4)]
    ok = True
    overlap_seen = False          # RED control, see below
    for k in range(2, KMAX_DC + 1):
        want = sp_min(k)
        seen = 0
        best2 = None
        for a in range(1, k // 2 + 1):
            for (ca, na) in by_size[a]:
                for (cb0, nb0) in by_size[k - a]:
                    for dx, dy in offs:
                        cb = _shift(cb0, dx, dy)
                        if ca & cb:
                            continue          # overlapping placement
                        nb = _shift(nb0, dx, dy)
                        if (ca & nb) or (cb & na):
                            continue          # 4-adjacent: one component
                        seen += 1
                        v = bin((na | nb) & ~(ca | cb)).count("1")
                        if (na & nb) and v < sp_min(a) + sp_min(k - a):
                            overlap_seen = True
                        if best2 is None or v < best2:
                            best2 = v
        best3 = None
        if k <= KMAX_DC3:
            for a in range(1, k - 1):
                for b in range(a, k - a):
                    c = k - a - b
                    if c < b:
                        continue
                    for (ca, na) in by_size[a]:
                        for (cb0, nb0) in by_size[b]:
                            for dx, dy in offs3:
                                cb = _shift(cb0, dx, dy)
                                if ca & cb:
                                    continue
                                nb = _shift(nb0, dx, dy)
                                if (ca & nb) or (cb & na):
                                    continue
                                for (cc0, nc0) in by_size[c]:
                                    for ex, ey in offs3:
                                        cc = _shift(cc0, ex, ey)
                                        if (ca | cb) & cc:
                                            continue
                                        nc = _shift(nc0, ex, ey)
                                        if ((ca | cb) & nc) or (cc & (na | nb)):
                                            continue
                                        seen += 1
                                        v = bin((na | nb | nc)
                                                & ~(ca | cb | cc)).count("1")
                                        if best3 is None or v < best3:
                                            best3 = v
        flag = ""
        for got in (best2, best3):
            if got is not None and got < want:
                ok = False
                flag = "   BEATS eps"
        print(f"    {k:>3} {want:>8} {str(best2):>13} {str(best3):>13} "
              f"{seen:>16,}{flag}")
    if not ok:
        print("    FAIL: a disconnected subset beat the minimum site-perimeter")
        return False
    if not overlap_seen:
        print("    FAIL: no configuration with SHARED neighbours was reached "
              "-- the search never left the far-apart regime, so a negative "
              "result would be vacuous")
        return False
    print("    OK -- splitting never beats eps (it ties at k = 2, where a")
    print("    diagonal pair shares two neighbours), and the search does reach")
    print("    configurations whose components share neighbours")
    return True


def check_banked():
    """(5) The formula against the enumerated M(n)."""
    print("\n[5] banked results/maxhole.txt")
    rows = {}
    with open(MAXHOLE_TXT) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                rows[int(parts[0])] = int(parts[1])
    if not rows:
        print(f"    FAIL: no rows parsed from {MAXHOLE_TXT}")
        return False
    bad = {n: (v, M(n)) for n, v in rows.items() if v != M(n)}
    if bad:
        print(f"    FAIL: {bad}")
        return False
    print(f"    OK, {len(rows)} rows, n <= {max(rows)}, M({max(rows)}) = "
          f"{rows[max(rows)]}")
    return True


def main():
    ok = check_brute()
    ok &= check_inversion()
    ok &= check_superadditive()
    ok &= check_banked()
    ok &= check_papers_agree()
    ok &= check_disconnected()
    if ok:
        print("\nAll checks pass: the maxhole formula and the minimum "
              "site-perimeter formula\nare the same theorem, so the "
              "single-hole bound is a corollary of Sieben. The\narbitrary-"
              "subset form (Altshuler et al.) applies to the union of all the "
              "holes\nat once, which closes the multi-hole case too -- no "
              "overlap argument needed.")
        return 0
    print("\nFAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
