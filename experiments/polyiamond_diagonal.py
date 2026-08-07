#!/usr/bin/env python3
"""Polyiamonds: the diagonal law outside the row-local class.

Polyiamonds are animals of equilateral triangles. Model them on Z^2 with
cell (x, y) an up- or down-triangle by the parity of x + y:

    within a row:  (x, y) ~ (x +- 1, y)                     always
    between rows:  (x, y) ~ (x, y + 1)   iff (x + y) is ODD

So the "drift set" is parity-dependent -- there is no single D -- and
docs/proofs/universal-diagonal-law.md Theorem A does not apply. Its condition
(U) fails outright. What this script asks is whether the law survives anyway in
a periodic form.

Two structural facts, measured here rather than assumed:

  * the MINIMUM cell count at height H is n = 2H - 2 (H >= 2), not H, because a
    single cell in a row can only connect upward when its parity allows it, so
    the cheapest ladder alternates 1 and 2 cells per row;
  * the top diagonals are T(2H-2, H) = 2^(H-2) and T(2H-1, H) = H*2^(H-1),
    which experiments/universal_law_check.py has probed since July.

Indexing: k counts cells above the minimum, n = 2H - 2 + k. The question is
whether T(2H-2+k, H) / 2^H is a polynomial in H, or a quasi-polynomial with
period 2, or neither.

The counts come from a surplus-budgeted row transfer DP (state = this row's
cells normalized with parity preserved, which component of the animal-so-far
each belongs to, cells used) whose cost depends on k and H rather than on the
number of polyiamonds -- the same device as experiments/diagonal_machine.py,
with the parity rule in place of a drift set. It is validated against brute
force before it is believed.

Usage: python3 -m experiments.polyiamond_diagonal
"""
import sys
from collections import defaultdict
from fractions import Fraction as F

KMAX = 4
HMAX = 14
WINDOW = 6


def nbr(c):
    x, y = c
    return [(x - 1, y), (x + 1, y),
            ((x, y - 1) if (x + y) % 2 == 0 else (x, y + 1))]


def brute(nmax):
    """Fixed polyiamonds by (cells, height). Parity-preserving translation."""
    def canon(cells):
        mx = min(x for x, _ in cells)
        my = min(y for _, y in cells)
        dx = mx - ((mx + my) % 2)
        return frozenset((x - dx, y - my) for x, y in cells)

    T = defaultdict(int)
    T[(1, 1)] = 1
    seen = {canon({(0, 0)})}
    frontier = list(seen)
    while frontier:
        nxt = []
        for a in frontier:
            if len(a) >= nmax:
                continue
            for c in a:
                for b in nbr(c):
                    if b in a:
                        continue
                    q = canon(a | {b})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.append(q)
                    h = max(y for _, y in q) - min(y for _, y in q) + 1
                    T[(len(q), h)] += 1
        frontier = nxt
    return T


def find(par, a):
    while par[a] != a:
        par[a] = par[par[a]]
        a = par[a]
    return a


def union(par, a, b):
    ra, rb = find(par, a), find(par, b)
    if ra != rb:
        par[rb] = ra


def normalize(cells, comp, parity):
    """Shift so min = 0, carrying the parity of (x + y) with the shift."""
    m = min(cells)
    out = tuple(c - m for c in cells)
    seen = {}
    labels = []
    for c in cells:
        if comp[c] not in seen:
            seen[comp[c]] = len(seen)
        labels.append(seen[comp[c]])
    return out, tuple(labels), (parity + m) % 2


def dp_counts(kmax, hmax, window):
    """T[(n, H)] for n <= 2H-2+kmax, by surplus-budgeted row transfer.

    A state's parity flag p means: the cell at offset 0 of this row has
    (x + y) % 2 == p. Offset j therefore has parity (j + p) % 2, and connects
    to the row above exactly when that is odd.

    THE BUDGET. A cell that receives from below has even parity and so cannot
    send upward: every row except the first and the last needs at least TWO
    cells, the first needs one. So a partial animal of h rows has used at least
    2h - 1 cells if it is going to continue, and the right surplus to bound is

        s = used - (2h - 1),      0 <= s <= kmax,

    which is non-decreasing while the animal continues. At final height H the
    minimum is 2H - 2 (the last row needs only one cell), so a state collected
    at height H with surplus s is the diagonal k = s + 1.

    Budgeting by the CURRENT height's allowance instead is wrong and silently
    undercounts: the allowance grows by 2 per row while a row can cost 1, so a
    wide early row gets pruned even though later rows pay it back. That bug
    cost 376 -> 262 at (n, H) = (8, 3) before the brute-force check caught it.
    """
    T = defaultdict(int)
    # Seed row 1: any set of cells, either parity. s = size - 1.
    states = defaultdict(int)
    for p in (0, 1):
        for size in range(1, kmax + 2):
            for cells in _subsets(0, window, size):
                if cells[0] != 0:
                    continue
                comp = {c: c for c in cells}
                for a, b in zip(cells, cells[1:]):
                    if b - a == 1:
                        union(comp, a, b)
                comp = {c: find(comp, c) for c in cells}
                states[normalize(cells, comp, p) + (size, size - 1)] += 1

    for H in range(1, hmax + 1):
        for (cells, labels, p, used, s), cnt in states.items():
            if len(set(labels)) == 1 and s + 1 <= kmax:
                T[(used, H)] += cnt
        if H == hmax:
            break
        nxt = defaultdict(int)
        for (cells, labels, p, used, s), cnt in states.items():
            up = [c for c in cells if (c + p) % 2 == 1]   # can reach row H+1
            if not up:
                continue
            lo, hi = min(cells) - window, max(cells) + window
            for size in range(1, kmax + 2 - s + 2):
                if s + size - 2 > kmax:
                    break
                for new in _subsets(lo, hi, size):
                    par = {}
                    for lab in set(labels):
                        par[("o", lab)] = ("o", lab)
                    for c in new:
                        par[("n", c)] = ("n", c)
                    for a, b in zip(new, new[1:]):
                        if b - a == 1:
                            union(par, ("n", a), ("n", b))
                    touched = set()
                    for c, lab in zip(cells, labels):
                        if (c + p) % 2 == 1 and c in new:
                            union(par, ("o", lab), ("n", c))
                            touched.add(lab)
                    if touched != set(labels):
                        continue
                    comp = {q: find(par, ("n", q)) for q in new}
                    ids = {}
                    for q in new:
                        ids.setdefault(comp[q], len(ids))
                    key = normalize(new, {q: ids[comp[q]] for q in new},
                                    (p + 1) % 2) + (used + size,
                                                    s + size - 2)
                    nxt[key] += cnt
        states = nxt
    return T


def _subsets(lo, hi, size):
    from itertools import combinations
    return combinations(range(lo, hi + 1), size)


def interpolate(points):
    n = len(points)
    acc = [F(0)] * n
    for i, (xi, yi) in enumerate(points):
        basis, den = [F(1)], F(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            sh = [F(0)] + basis
            sc = [F(xj) * c for c in basis] + [F(0)]
            basis = [a - b for a, b in zip(sh, sc)]
            den *= F(xi - xj)
        s = F(yi) / den
        for idx, c in enumerate(basis):
            acc[idx] += c * s
    return acc[::-1]


def show(p):
    while len(p) > 1 and p[0] == 0:
        p = p[1:]
    d = len(p) - 1
    out = []
    for i, c in enumerate(p):
        e = d - i
        if c == 0:
            continue
        out.append(f"{c}H^{e}" if e > 1 else (f"{c}H" if e == 1 else f"{c}"))
    return (" + ".join(out) or "0").replace("+ -", "- ")


def ev(p, x):
    v = F(0)
    for c in p:
        v = v * x + c
    return v


def main():
    print("[1] DP against brute force (n <= 12)")
    B = brute(12)
    D = dp_counts(KMAX, 8, WINDOW)
    bad = []
    for (n, H), v in B.items():
        if H >= 2 and n <= 2 * H - 2 + KMAX and H <= 8:
            if D.get((n, H), 0) != v:
                bad.append((n, H, v, D.get((n, H), 0)))
    if bad:
        print(f"    FAIL: {bad[:6]}")
        return 1
    print(f"    OK, every (n, H) with H <= 8 and n <= 2H-2+{KMAX}")

    # Window stability is checked at small H, where the wider window is
    # affordable; the wide window costs far more than extra rows do.
    if dp_counts(KMAX, 8, WINDOW) != dp_counts(KMAX, 8, WINDOW + 2):
        print(f"    FAIL: window {WINDOW} vs {WINDOW+2} disagree")
        return 1
    print(f"    window {WINDOW} stable against {WINDOW+2} (H <= 8)")
    T = dp_counts(KMAX, HMAX, WINDOW)

    print(f"\n[2] the diagonals, n = 2H-2+k, normalized by 2^H")
    print("      k   H:", "  ".join(f"{h:>10}" for h in range(2, 9)))
    for k in range(KMAX + 1):
        row = []
        for H in range(2, 9):
            v = T.get((2 * H - 2 + k, H), 0)
            row.append(f"{F(v, 2 ** H)}")
        print(f"    k={k}    ", "  ".join(f"{x:>10}" for x in row))

    print("\n[3] is T/2^H a polynomial in H, or quasi-polynomial mod 2?")
    ok = True
    qs = {}
    onsets = {}
    for k in range(KMAX + 1):
        pts = [(H, F(T.get((2 * H - 2 + k, H), 0), 2 ** H))
               for H in range(2, HMAX + 1) if (2 * H - 2 + k, H) in T]
        settled = False
        for onset in range(0, 6):
            use = pts[onset:]
            if len(use) < k + 2:            # need a fit plus one holdout
                print(f"    k={k}: UNDETERMINED -- ran out of points "
                      f"(had {len(pts)}, need {k + 2} past the onset)")
                ok = False
                settled = True
                break
            p_ = interpolate(use[:k + 1])
            if all(ev(p_, H) == v for H, v in use):
                print(f"    k={k}: POLYNOMIAL of degree {k} from H={use[0][0]}"
                      f", {len(use) - (k + 1)} holdouts: {show(p_)}")
                qs[k] = p_
                onsets[k] = use[0][0]
                settled = True
                break
            # a period-2 quasi-polynomial would show up here; on this lattice
            # it never has to, which is the point of the exercise
            evp = [q for q in use if q[0] % 2 == 0]
            odp = [q for q in use if q[0] % 2 == 1]
            if len(evp) >= k + 2 and len(odp) >= k + 2:
                pe, po = interpolate(evp[:k + 1]), interpolate(odp[:k + 1])
                if (all(ev(pe, H) == v for H, v in evp)
                        and all(ev(po, H) == v for H, v in odp)):
                    print(f"    k={k}: QUASI-POLYNOMIAL period 2 from "
                          f"H={use[0][0]}\n          even: {show(pe)}"
                          f"\n          odd:  {show(po)}")
                    onsets[k] = use[0][0]
                    settled = True
                    break
        if not settled:
            print(f"    k={k}: neither polynomial nor period-2 quasi-polynomial "
                  f"at any onset H <= {pts[5][0] if len(pts) > 5 else '?'}")
            ok = False

    print("\n[4] the onsets, and the gas laws")
    print("      k   onset H   floor(k/2)+2")
    for k in sorted(onsets):
        want = k // 2 + 2
        flag = "" if onsets[k] == want else "   != floor(k/2)+2"
        print(f"    {k:>3} {onsets[k]:>9} {want:>13}{flag}")
        if onsets[k] != want:
            ok = False

    if set(qs) == set(range(KMAX + 1)):
        q0 = qs[0][-1]
        pk = {k: [c / q0 for c in qs[k]] for k in qs}
        print(f"\n    normalizing by q_0 = {q0} so p_0 = 1:")
        fact = 1
        for k in range(1, KMAX + 1):
            fact *= k
            lead = [c for c in pk[k]][0]
            got, want = lead * fact, 2 ** k
            print(f"      lead(p_{k}) * {k}! = {got}   vs W^k with W=2: {want}"
                  f"{'' if got == want else '   MISMATCH'}")
            if got != want:
                ok = False
        # cumulants: c_k = [u^k] log sum_k p_k u^k
        c = [None] * (KMAX + 1)
        for k in range(1, KMAX + 1):
            acc = [F(0)]
            for j in range(1, k):
                acc = _padd(acc, _pscale(_pmul(c[j], pk[k - j]), j))
            c[k] = _pscale(_padd(_pscale(pk[k], k), _pscale(acc, -1)), F(1, k))
        print("\n    cumulants of the same series:")
        for k in range(1, KMAX + 1):
            d = len(_trim(c[k])) - 1
            print(f"      c_{k} = {show(c[k])}   deg {d}"
                  f"{'' if d <= 1 else '   NOT LINEAR'}")
            if d > 1:
                ok = False
        print("\n    Linear cumulants and lead = W^k/k! with W = 2: the defect")
        print("    gas of docs/proofs/universal-diagonal-law.md, on a lattice")
        print("    that is NOT in the row-local class. Condition (U) is")
        print("    sufficient for the law, not necessary.")
    return 0 if ok else 1


def _trim(p):
    p = list(p)
    while len(p) > 1 and p[0] == 0:
        p = p[1:]
    return p


def _padd(a, b):
    n = max(len(a), len(b))
    a = [F(0)] * (n - len(a)) + list(a)
    b = [F(0)] * (n - len(b)) + list(b)
    return _trim([x + y for x, y in zip(a, b)])


def _pmul(a, b):
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] += x * y
    return _trim(r)


def _pscale(a, s):
    return _trim([x * F(s) for x in a])


if __name__ == "__main__":
    sys.exit(main())
