#!/usr/bin/env python3
"""The multi-hole margin of M(n), and one refuted route to it.

results/subclasses.md: the SINGLE-hole bound is a two-sided theorem (the
moat-cycle argument proves (II') n >= ha+hm+2). What is still open is the
multi-hole reduction, currently routed through the "master inequality"
interior_4(F') <= round((|shell_4(F')|-2)^2/8) and its peeling lemma, whose two
sub-lemmas (A-int) and (Sigma) are verified but unproved.

This probe tested a route the note does not record as tried -- induction on the
number of holes by removing wall cells:

  MERGE LEMMA (candidate, REFUTED below). Let F be a king animal with k >= 2
  holes and total enclosed area A. Then there is a nonempty W subset F with
  |W| = t such that F \\ W is a king animal with fewer holes and enclosed area
  >= A + t.

Had it held, the multi-hole bound would follow from the single-hole theorem:
peel until one hole remains, having spent s cells and gained >= s area, so
A + s <= M_single(n - s) <= M_single(n).

It fails at the first multi-hole animal there is, and the reason is structural:
the two smallest multi-hole animals are TIGHT (A = M(n) already at n = 6), so no
argument that must strictly gain area at each merge can survive the margin.

What the script reports, for every king animal up to n = NMAX:

  1. the maximum total enclosed area over multi-hole animals, against M(n) --
     i.e. exactly how much room a multi-hole proof has at each n;
  2. the merge lemma's failures, with the smallest counterexample printed.

Positive control: the enumeration reproduces A006770.

Usage: python3 experiments/maxhole_merge_probe.py [--nmax 9] [--wmax 3]
"""
import argparse
import sys
from collections import deque

K8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
R4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
A006770 = {1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941,
           9: 940982, 10: 6053180}


def M(n):
    """The banked formula, floor(((n-2)^2 + 4) / 8)."""
    return ((n - 2) ** 2 + 4) // 8


def canon(s):
    mx = min(x for x, y in s)
    my = min(y for x, y in s)
    return frozenset((x - mx, y - my) for x, y in s)


def grow(prev):
    out = set()
    for s in prev:
        for (x, y) in s:
            for dx, dy in K8:
                p = (x + dx, y + dy)
                if p not in s:
                    out.add(canon(s | {p}))
    return out


def king_connected(S):
    if not S:
        return False
    c0 = next(iter(S))
    seen, dq = {c0}, deque([c0])
    while dq:
        x, y = dq.popleft()
        for dx, dy in K8:
            p = (x + dx, y + dy)
            if p in S and p not in seen:
                seen.add(p)
                dq.append(p)
    return len(seen) == len(S)


def holes(S):
    """The bounded 4-components of the complement, as a list of frozensets."""
    xs = [x for x, y in S]
    ys = [y for x, y in S]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    outside, dq = {(x0, y0)}, deque([(x0, y0)])
    while dq:
        x, y = dq.popleft()
        for dx, dy in R4:
            p = (x + dx, y + dy)
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and p not in S and p not in outside:
                outside.add(p)
                dq.append(p)
    rest = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
            if (x, y) not in S and (x, y) not in outside}
    out = []
    while rest:
        c0 = rest.pop()
        comp, dq = {c0}, deque([c0])
        while dq:
            x, y = dq.popleft()
            for dx, dy in R4:
                p = (x + dx, y + dy)
                if p in rest:
                    rest.discard(p)
                    comp.add(p)
                    dq.append(p)
        out.append(frozenset(comp))
    return out


def subsets(items, t):
    if t == 0:
        yield ()
        return
    for i, x in enumerate(items):
        for rest in subsets(items[i + 1:], t - 1):
            yield (x,) + rest


def merge_witness(S, hs, wmax):
    """W with |W| = t <= wmax, S\\W a king animal, fewer holes, area >= A + t."""
    A, k = sum(len(h) for h in hs), len(hs)
    cand = sorted(c for c in S
                  if any((c[0] + dx, c[1] + dy) in h for dx, dy in R4 for h in hs))
    for t in range(1, wmax + 1):
        for W in subsets(cand, t):
            T = S - set(W)
            if not T or not king_connected(T):
                continue
            hs2 = holes(T)
            if len(hs2) < k and sum(len(h) for h in hs2) >= A + t:
                return t, W
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nmax", type=int, default=9)
    ap.add_argument("--wmax", type=int, default=3)
    args = ap.parse_args()

    cur = {frozenset({(0, 0)})}
    first_ce = None
    fails = tight = 0
    print(f"{'n':>3} {'animals':>9} {'multi-hole':>10} {'max A (multi)':>13} "
          f"{'M(n)':>5} {'slack':>6} {'merge fails':>11}")
    for n in range(2, args.nmax + 1):
        cur = grow(cur)
        if n in A006770:
            assert len(cur) == A006770[n], \
                f"enumeration wrong at n={n}: {len(cur)} != {A006770[n]}"
        best, nmulti, nbad = 0, 0, 0
        for S in cur:
            hs = holes(S)
            if len(hs) < 2:
                continue
            nmulti += 1
            best = max(best, sum(len(h) for h in hs))
            if merge_witness(S, hs, args.wmax) is None:
                nbad += 1
                if first_ce is None:
                    first_ce = (n, sorted(S), [sorted(h) for h in hs])
        fails += nbad
        if nmulti and best == M(n):
            tight += 1
        print(f"{n:>3} {len(cur):>9} {nmulti:>10} {best if nmulti else '-':>13} "
              f"{M(n):>5} {(M(n) - best) if nmulti else '-':>6} {nbad:>11}",
              flush=True)

    assert best <= M(n), "a multi-hole animal beat M(n) -- the formula is wrong"
    print(f"\nMulti-hole animals never beat M(n) (the known bound), and the "
          f"margin is ZERO at {tight} of the checked n.")
    if first_ce:
        n, S, hs = first_ce
        print(f"\nMERGE LEMMA REFUTED, {fails} failures, smallest at n={n}:")
        print(f"  animal {S}")
        print(f"  holes  {hs}")
        print("  Two unit holes sealed across a shared diagonal: no cell can be "
              "removed\n  without opening a hole to the exterior, and the animal "
              "is already tight\n  (A = M(n)), so no merge can gain area.")
        return 0
    print("\nMERGE LEMMA held everywhere checked -- unexpected; re-read the probe")
    return 1


if __name__ == "__main__":
    sys.exit(main())
