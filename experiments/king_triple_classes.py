#!/usr/bin/env python3
"""What else do the animals inside one (n, H, p) class share?

experiments/king_joint_nhp.py showed the triple almost never pins a single fixed
king animal.  This asks the better question: when the class is bigger than one,
is it still homogeneous in some OTHER attribute -- width, holes, bond count,
symmetry -- and is the multiplicity just the D4 elements that preserve height?

Only the height-preserving subgroup of D4 can act within a class: the identity,
the two axis reflections, and the half turn (a quarter turn swaps H and W).  So
every class is a union of orbits of that Klein four-group; a class that is ONE
such orbit is morally a single animal seen four ways.

    python3 experiments/king_triple_classes.py 9
"""
from __future__ import annotations

import sys
from collections import defaultdict

K8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
R4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def canon(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def generate(nmax):
    seen = {frozenset({(0, 0)})}
    frontier = list(seen)
    yield frozenset({(0, 0)})
    for _ in range(2, nmax + 1):
        nxt = []
        for a in frontier:
            for cx, cy in a:
                for dx, dy in K8:
                    b = (cx + dx, cy + dy)
                    if b in a:
                        continue
                    q = canon(a | {b})
                    if q in seen:
                        continue
                    seen.add(q)
                    nxt.append(q)
                    yield q
        frontier = nxt


def holes(a):
    """4-connected empty components of the complement not reaching the outside."""
    xs = [x for x, _ in a]
    ys = [y for _, y in a]
    x0, x1 = min(xs) - 1, max(xs) + 1
    y0, y1 = min(ys) - 1, max(ys) + 1
    outside, stack = set(), [(x0, y0)]
    while stack:
        c = stack.pop()
        if c in outside or c in a or not (x0 <= c[0] <= x1 and y0 <= c[1] <= y1):
            continue
        outside.add(c)
        stack.extend((c[0] + dx, c[1] + dy) for dx, dy in R4)
    empty = {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
             if (x, y) not in a and (x, y) not in outside}
    n_holes, area = 0, len(empty)
    while empty:
        n_holes += 1
        stack = [next(iter(empty))]
        while stack:
            c = stack.pop()
            if c not in empty:
                continue
            empty.discard(c)
            stack.extend((c[0] + dx, c[1] + dy) for dx, dy in R4)
    return n_holes, area


def attributes(a):
    xs = [x for x, _ in a]
    ys = [y for _, y in a]
    n = len(a)
    king_bonds = sum(1 for x, y in a for dx, dy in K8 if (x + dx, y + dy) in a) // 2
    rook_bonds = sum(1 for x, y in a for dx, dy in R4 if (x + dx, y + dy) in a) // 2
    nh, harea = holes(a)
    # rook-connectivity: is this polyplet actually a polyomino?
    stack, seen4 = [next(iter(a))], set()
    while stack:
        c = stack.pop()
        if c in seen4:
            continue
        seen4.add(c)
        stack.extend(q for q in ((c[0] + dx, c[1] + dy) for dx, dy in R4) if q in a)
    cols = len({x for x, _ in a})
    rows_used = len({y for _, y in a})
    return {
        "W": max(xs) - min(xs) + 1,
        "king_bonds": king_bonds,
        "rook_bonds": rook_bonds,
        "cycle_rank": king_bonds - n + 1,
        "holes": nh,
        "hole_area": harea,
        "rook_conn": int(len(seen4) == n),
        "occupied_cols": cols,
        "occupied_rows": rows_used,
        "sym_order": symmetry_order(a),
    }


D4 = (lambda x, y: (x, y), lambda x, y: (-x, y), lambda x, y: (x, -y),
      lambda x, y: (-x, -y), lambda x, y: (y, x), lambda x, y: (-y, x),
      lambda x, y: (y, -x), lambda x, y: (-y, -x))
# the four that fix bounding-box height: identity, both reflections, half turn
KLEIN = D4[:4]


def symmetry_order(a):
    return sum(1 for t in D4 if canon({t(x, y) for x, y in a}) == a)


def klein_orbit(a):
    return frozenset(canon({t(x, y) for x, y in a}) for t in KLEIN)


def main(argv):
    nmax = int(argv[1]) if len(argv) > 1 else 9
    classes = defaultdict(list)
    for a in generate(nmax):
        ys = [y for _, y in a]
        p = len({(x + dx, y + dy) for x, y in a for dx, dy in K8} - a)
        classes[(len(a), max(ys) - min(ys) + 1, p)].append(a)

    keys = sorted(classes)
    multi = [k for k in keys if len(classes[k]) > 1]
    print(f"n <= {nmax}: {len(keys)} live (n,H,p) triples, "
          f"{len(keys) - len(multi)} singleton, {len(multi)} with >1 animal")

    names = sorted(attributes(next(iter(classes[keys[0]]))))
    const = {name: 0 for name in names}
    spread = {name: (0, None) for name in names}
    for k in multi:
        attrs = [attributes(a) for a in classes[k]]
        for name in names:
            vals = {d[name] for d in attrs}
            if len(vals) == 1:
                const[name] += 1
            if len(vals) > spread[name][0]:
                spread[name] = (len(vals), k)

    print("\nattributes constant across a multi-animal class:")
    for name in sorted(names, key=lambda s: -const[s]):
        cnt, worst = spread[name]
        print(f"  {name:14s} constant in {const[name]:4d}/{len(multi)} classes"
              f"   (worst: {cnt} values at n,H,p={worst})")

    print("\nis the multiplicity just symmetry?")
    orbit_hist = defaultdict(int)
    for k in multi:
        orbit_hist[len({klein_orbit(a) for a in classes[k]})] += 1
    one = orbit_hist[1]
    print(f"  {one}/{len(multi)} multi-animal classes are a SINGLE orbit of the "
          f"height-preserving Klein group")
    print(f"  orbits-per-class histogram: "
          f"{dict(sorted(orbit_hist.items()))}")

    # Counting classes flatters the answer: most classes are tiny.  Weight by
    # animals, and split by defect k = 4n+4-p, since the low-defect classes are
    # the structured ones (docs/perimeter-defect-plan.md).
    total = sum(len(classes[k]) for k in multi)
    print("\nsame, weighted by animals, and by defect k = 4n+4-p:")
    print(f"  {'attribute':14s} {'wtd const':>10s}   " +
          "  ".join(f"k={kk}" for kk in range(6)))
    bydefect = defaultdict(list)
    for key in multi:
        bydefect[4 * key[0] + 4 - key[2]].append(key)
    cache = {key: [attributes(a) for a in classes[key]] for key in multi}
    for name in names:
        wt = sum(len(classes[key]) for key in multi
                 if len({d[name] for d in cache[key]}) == 1)
        cells = []
        for kk in range(6):
            ks = bydefect.get(kk, [])
            hom = sum(1 for key in ks if len({d[name] for d in cache[key]}) == 1)
            cells.append(f"{hom}/{len(ks)}" if ks else "-")
        print(f"  {name:14s} {100*wt/total:9.1f}%   " + "  ".join(f"{c:>5s}" for c in cells))

    print("\nlargest classes:")
    for k in sorted(multi, key=lambda k: -len(classes[k]))[:5]:
        orbs = len({klein_orbit(a) for a in classes[k]})
        varying = [name for name in names
                   if len({attributes(a)[name] for a in classes[k]}) > 1]
        print(f"  n,H,p={k}: {len(classes[k])} animals, {orbs} orbits, "
              f"varies in {varying}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
