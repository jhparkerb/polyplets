#!/usr/bin/env python3
"""r3_inv_candidates.py -- queue rows L4-3 / LEAD-2: non-group involutions on
fixed (n,H) king animals.

For each candidate rule sigma we test mechanically, on ALL fixed king animals
of n cells grouped by exact bounding-box height H (n <= MAXN):

  well-defined : sigma(A) is a valid fixed n-animal of the SAME exact height H
                 (or A is declared fixed by the rule)
  involutive   : sigma(sigma(A)) == A for every non-fixed A
  fixed set    : |Fix(sigma)| per (n,H), and whether Fix(sigma) equals the
                 D2ax-symmetric set (same bit in disguise) or differs

Parity law used throughout: ANY involution on the (n,H) class forces
T(n,H) == |Fix(sigma)| (mod 2).  So for a PASSING candidate the fixed-set
parity must equal T mod 2 on every cell -- we assert that as a consistency
check of the test harness itself, with the enumerated T (not the banked file)
as the reference.  Row sums are cross-checked against A006770.

Enumeration is self-grown (translation-normalised growth, same scheme as
experiments/move_graph_connectivity.py) -- no banked data is read.

Usage: python3 experiments/tristruct/r3_inv_candidates.py [MAXN]
"""

import sys
import time
from collections import defaultdict

NBRS = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180]


def norm(cells):
    """Canonical translation representative as a frozenset, min x = min y = 0."""
    mx = min(x for x, y in cells)
    my = min(y for x, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def height(a):
    return max(y for _, y in a) + 1


def width(a):
    return max(x for x, _ in a) + 1


def connected(cells):
    s = set(cells)
    seed = next(iter(s))
    seen, stack = {seed}, [seed]
    while stack:
        x, y = stack.pop()
        for dx, dy in NBRS:
            c = (x + dx, y + dy)
            if c in s and c not in seen:
                seen.add(c)
                stack.append(c)
    return len(seen) == len(s)


def grow(maxn):
    """dict n -> set of normalised fixed king animals, n = 1..maxn."""
    out = {1: {norm([(0, 0)])}}
    cur = out[1]
    for n in range(2, maxn + 1):
        nxt = set()
        for a in cur:
            for x, y in a:
                for dx, dy in NBRS:
                    c = (x + dx, y + dy)
                    if c not in a:
                        nxt.add(norm(list(a) + [c]))
        out[n] = nxt
        cur = nxt
    return out


# ---------- symmetry helpers (independence comparison) ----------

def hmirror(a):
    return norm([(-x, y) for x, y in a])


def vmirror(a):
    return norm([(x, -y) for x, y in a])


def d2ax_fixed(a):
    return a == hmirror(a) and a == vmirror(a)


# ---------- candidate rules ----------
# Each returns (image, tag). image is a normalised animal (possibly == a when
# the rule declares a fixed).  tag is 'fixed' or 'moved'.  A rule may also
# return ('INVALID', reason) if its own move produced an illegal object --
# that is a well-definedness failure we count rather than mask.


def scan_sites(a):
    """Bounding-box sites in row-major (y, then x) order."""
    W, H = width(a), height(a)
    for y in range(H):
        for x in range(W):
            yield x, y


def valid_same_H(a, cells):
    """cells (iterable of coords) is a valid animal of the same exact H."""
    if not connected(cells):
        return None
    b = norm(cells)
    if height(b) != height(a):
        return None
    return b


def cand_vmirror(a):
    """C1 (group baseline): v-mirror as a pairing.  Sanity anchor."""
    b = vmirror(a)
    return (b, 'fixed' if b == a else 'moved')


def cand_slide(a):
    """C2: first-site 2x2 diagonal slide.  Site (x,y) is switchable when the
    anti-diagonal pair (x,y+1),(x+1,y) is present and exactly one of the
    diagonal pair (x,y),(x+1,y+1) is present; the move slides the lone
    diagonal cell to the opposite diagonal corner.  First site (row-major)
    where the move yields a valid same-H animal wins."""
    s = set(a)
    for x, y in scan_sites(a):
        if (x, y + 1) in s and (x + 1, y) in s:
            p, q = (x, y), (x + 1, y + 1)
            inp, inq = p in s, q in s
            if inp != inq:
                cells = (s - {p} | {q}) if inp else (s - {q} | {p})
                b = valid_same_H(a, cells)
                if b is not None:
                    return (b, 'moved')
    return (a, 'fixed')


def cand_diagswap(a):
    """C7: first-site diagonal-pair swap.  If a 2x2 window holds exactly the
    diagonal pair, replace it by the anti-diagonal pair, and vice versa."""
    s = set(a)
    for x, y in scan_sites(a):
        p, q = (x, y), (x + 1, y + 1)
        r, t = (x + 1, y), (x, y + 1)
        diag = (p in s) and (q in s) and (r not in s) and (t not in s)
        anti = (r in s) and (t in s) and (p not in s) and (q not in s)
        if diag or anti:
            if diag:
                cells = s - {p, q} | {r, t}
            else:
                cells = s - {r, t} | {p, q}
            b = valid_same_H(a, cells)
            if b is not None:
                return (b, 'moved')
    return (a, 'fixed')


def cand_rowswap(a):
    """C3 (Franklin-style): compare the x-sets of the top and bottom rows.
    Lex-smaller row moves to the far side (top row drops below the bottom,
    or bottom row lifts above the top), preserving H.  Equal x-sets, or an
    invalid move, leaves A fixed."""
    s = set(a)
    H = height(a)
    if H == 1:
        return (a, 'fixed')
    top = sorted(x for x, y in a if y == H - 1)
    bot = sorted(x for x, y in a if y == 0)
    if top == bot:
        return (a, 'fixed')
    if top < bot:
        cells = {(x, y) for x, y in s if y < H - 1} | {(x, -1) for x in top}
    else:
        cells = {(x, y) for x, y in s if y > 0} | {(x, H) for x in bot}
    b = valid_same_H(a, cells)
    if b is None:
        return (a, 'fixed')
    return (b, 'moved')


def cand_cornerflip(a):
    """C5: move the extremal cell (max by (y,x)) to its point reflection
    through the bounding-box centre, when that site is empty and the move is
    valid with the SAME bounding box (so the pairing key is stable)."""
    s = set(a)
    W, H = width(a), height(a)
    cx = max(s, key=lambda c: (c[1], c[0]))
    rx = (W - 1 - cx[0], H - 1 - cx[1])
    if rx == cx or rx in s:
        return (a, 'fixed')
    cells = s - {cx} | {rx}
    if not connected(cells):
        return (a, 'fixed')
    b = norm(cells)
    if height(b) != H or width(b) != W:
        return (a, 'fixed')
    return (b, 'moved')


def cand_pairtoggle(a):
    """C4: canonical-pair occupancy swap.  Key the pair on the animal's
    OCCUPIED+EMPTY multiset inside the bounding box: the first row-major site
    pair ((x,y),(x+1,y)) with exactly one occupied, where swapping which end
    is occupied is valid and same-H.  A horizontal Franklin 'slide by one'."""
    s = set(a)
    for x, y in scan_sites(a):
        p, q = (x, y), (x + 1, y)
        inp, inq = p in s, q in s
        if inp != inq:
            cells = (s - {p} | {q}) if inp else (s - {q} | {p})
            b = valid_same_H(a, cells)
            if b is not None:
                return (b, 'moved')
    return (a, 'fixed')


def cand_slide_local(a):
    """C2L: the same 2x2 slide as C2, but candidacy is decided LOCALLY only
    (anti-diagonal support present, exactly one diagonal cell) -- no global
    connectivity or height check.  This is the other horn of the dilemma: if
    global validity is dropped so first-site candidacy becomes stable under
    the move, the image can leave the (n,H) class."""
    s = set(a)
    for x, y in scan_sites(a):
        if (x, y + 1) in s and (x + 1, y) in s:
            p, q = (x, y), (x + 1, y + 1)
            inp, inq = p in s, q in s
            if inp != inq:
                cells = (s - {p} | {q}) if inp else (s - {q} | {p})
                return (norm(cells), 'moved')  # may be disconnected/wrong H
    return (a, 'fixed')


CANDIDATES = [
    ('C1 vmirror (group baseline)', cand_vmirror),
    ('C2 first-site 2x2 slide', cand_slide),
    ('C2L local-candidacy 2x2 slide', cand_slide_local),
    ('C7 first-site diag-pair swap', cand_diagswap),
    ('C3 top/bottom row Franklin', cand_rowswap),
    ('C5 extremal corner reflection', cand_cornerflip),
    ('C4 first horizontal 1-slide', cand_pairtoggle),
]


def test_candidate(name, rule, animals_by_n, maxreport=3):
    print(f"\n=== {name} ===")
    overall_ok = True
    for n in sorted(animals_by_n):
        byH = defaultdict(list)
        for a in animals_by_n[n]:
            byH[height(a)].append(a)
        for H in sorted(byH):
            group = byH[H]
            gset = set(group)
            bad_wd = []      # image leaves the (n,H) class
            bad_inv = []     # sigma(sigma(A)) != A
            fixed = []
            for a in group:
                b, tag = rule(a)
                if tag == 'fixed':
                    fixed.append(a)
                    continue
                if len(b) != n or height(b) != H or b not in gset:
                    bad_wd.append(a)
                    continue
                c, tag2 = rule(b)
                if tag2 == 'fixed' or c != a:
                    bad_inv.append((a, b, c))
            T = len(group)
            nfix = len(fixed)
            ok = not bad_wd and not bad_inv
            parity_ok = (T - nfix) % 2 == 0 if ok else None
            d2 = sum(1 for a in fixed if d2ax_fixed(a))
            same_as_d2ax = (ok and nfix == d2
                            and nfix == sum(1 for a in group if d2ax_fixed(a)))
            print(f"  n={n} H={H}: T={T} fix={nfix} "
                  f"wd_fail={len(bad_wd)} inv_fail={len(bad_inv)} "
                  f"{'OK' if ok else 'FAIL'}"
                  + (f" parity{'OK' if parity_ok else 'BAD'}" if ok else "")
                  + (" fix==D2axFix" if same_as_d2ax else ""))
            if ok and not parity_ok:
                print("      *** parity violation: harness bug or bad rule")
                overall_ok = False
            if bad_inv and len(bad_inv) <= 999:
                for (a, b, c) in bad_inv[:maxreport]:
                    print("      inv-fail example: A -> B -> C, C != A")
                    for tag, x in (('A', a), ('B', b), ('C', c if c else a)):
                        draw(x, indent=f"        {tag}: ")
            overall_ok = overall_ok and ok
    print(f"  VERDICT: {'PASSES (involution on every class tested)' if overall_ok else 'FAILS'}")
    return overall_ok


def draw(a, indent=""):
    W, H = width(a), height(a)
    for y in range(H - 1, -1, -1):
        row = "".join("#" if (x, y) in a else "." for x in range(W))
        print(indent + row)
        indent = " " * len(indent)


def main():
    maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    t0 = time.time()
    animals = grow(maxn)
    for n in sorted(animals):
        assert len(animals[n]) == A006770[n - 1], \
            f"grower bad at n={n}: {len(animals[n])} != {A006770[n-1]}"
    print(f"grower validated against A006770 for n <= {maxn} "
          f"({time.time()-t0:.1f}s)")

    # RED control: a deliberately broken 'rule' (move the max cell one step
    # right whenever legal) must FAIL involutivity -- if the harness calls it
    # an involution, the harness is broken.
    def red_rule(a):
        s = set(a)
        c = max(s)
        t = (c[0] + 1, c[1])
        if t in s:
            return (a, 'fixed')
        cells = s - {c} | {t}
        b = valid_same_H(a, cells)
        if b is None:
            return (a, 'fixed')
        return (b, 'moved')

    print("\n--- RED control (must FAIL) ---")
    red = test_candidate('RED broken shift rule', red_rule,
                         {n: animals[n] for n in (4, 5)})
    if red:
        print("RED CONTROL PASSED AS INVOLUTION -- HARNESS BROKEN, ABORT")
        return 1

    results = {}
    for name, rule in CANDIDATES:
        results[name] = test_candidate(name, rule, animals)

    print("\n=== summary ===")
    for name, ok in results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    print(f"total wall {time.time()-t0:.1f}s")
    return 0


if __name__ == '__main__':
    sys.exit(main())
