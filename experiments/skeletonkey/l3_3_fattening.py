#!/usr/bin/env python3
"""L3-3: the fattening bijection from king animals to decorated polyominoes.

`results/r4/r4-floors.md (deleted)` sec."Routes the floors do not close that have been
treated as closed" objects that L3-3 was pruned by a rank floor -- "paying a
floor of ~1.5e4 at H=21 is not a cost objection to anything" -- and calls the
kill "merely asserted". `docs/skeletonkey-reprompt.md (deleted)` then finds that L3-4,
its twin, has a second and sound kill, leaving L3-3 as the one open row.

The row (`git show triangle-structure:results/triangle-r3-queue.md (deleted)`, L3-3):

    Object change, not encoding change: bijection from king animals to a
    decorated polyomino class on a refined lattice (fatten each cell to a 2x2
    block, fill a marked corner cell at each pinch) -- boundary becomes
    pinch-free and edge-based, so polyomino contour/SAP technology applies
    verbatim to the image class.
    OPEN | half-formed; injectivity and the marked-cell convention need
    checking at small n

This script is that check, and nothing more. It builds the map under several
marking conventions and asks two questions of each:

  1. **Pinch-free?** Does the image have no corner where exactly two
     diagonally-opposite refined cells are filled? That is the whole premise:
     without it the image is not a polyomino with an edge-based boundary and
     no contour technology applies.
  2. **Injective?** Do two distinct king animals ever share an image, up to
     translation? If they do, the image carries less information than the
     animal and the "bijection" is not one.

A convention that answers yes to both is what L3-3 needs to exist at all.

RED control: convention "none" (fatten, fill nothing) MUST fail question 1 --
a diagonal contact stays a corner contact after fattening, which is the whole
reason the filler is in the construction. If "none" comes out pinch-free the
pinch detector is broken and the other verdicts mean nothing.

Gate: the animal counts must reproduce A006770 (1, 4, 20, 110, 638, 3832,
23592, ...) before any verdict is reported.

Usage: python3 experiments/skeletonkey/l3_3_fattening.py [NMAX]     (ayr)
Cost:  n <= 7 is seconds and megabytes; n = 8 is ~150k animals, still small.
"""

import sys
from collections import defaultdict

A006770 = [1, 4, 20, 110, 638, 3832, 23592, 147941]

NB = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]


def norm(cells):
    """Translate a cell set so its bounding box starts at the origin."""
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def king_animals(nmax):
    """Fixed king animals (up to translation) by size, 1 .. nmax."""
    levels = [{norm({(0, 0)})}]
    for _ in range(2, nmax + 1):
        cur = set()
        for a in levels[-1]:
            for (x, y) in a:
                for dx, dy in NB:
                    c = (x + dx, y + dy)
                    if c not in a:
                        cur.add(norm(a | {c}))
        levels.append(cur)
    return levels


# ---------------------------------------------------------------- the map
#
# King cell (x, y) fattens to the 2x2 refined block
#     {(2x, 2y), (2x+1, 2y), (2x, 2y+1), (2x+1, 2y+1)}.
#
# The grid corner (x, y) -- the point where king cells (x-1, y-1), (x, y-1),
# (x-1, y) and (x, y) meet -- is a PINCH when exactly one diagonal pair of
# those four is in the animal. The two absent cells are the two candidate
# blocks for the filler, and the refined cell each contributes is the one it
# owns at that corner.

def corner_cells(x, y):
    """The four (king cell, refined cell it owns) pairs at grid corner (x,y)."""
    return {(x - 1, y - 1): (2 * x - 1, 2 * y - 1),
            (x, y - 1):     (2 * x, 2 * y - 1),
            (x - 1, y):     (2 * x - 1, 2 * y),
            (x, y):         (2 * x, 2 * y)}


def pinches(animal):
    """Grid corners that pinch, with the two candidate blocks at each."""
    out = []
    xs = [x for x, _ in animal]
    ys = [y for _, y in animal]
    for x in range(min(xs), max(xs) + 2):
        for y in range(min(ys), max(ys) + 2):
            own = corner_cells(x, y)
            sw, se = (x - 1, y - 1), (x, y - 1)
            nw, ne = (x - 1, y), (x, y)
            inside = [k for k in (sw, se, nw, ne) if k in animal]
            if len(inside) != 2:
                continue
            if set(inside) == {sw, ne}:
                out.append((own[se], own[nw], se, nw))
            elif set(inside) == {se, nw}:
                out.append((own[sw], own[ne], sw, ne))
    return out


def image(animal, convention):
    """The refined-lattice image of a king animal under a filling rule."""
    img = set()
    for (x, y) in animal:
        img |= {(2 * x, 2 * y), (2 * x + 1, 2 * y),
                (2 * x, 2 * y + 1), (2 * x + 1, 2 * y + 1)}
    for r1, r2, b1, b2 in pinches(animal):
        if convention == "none":            # RED control
            continue
        elif convention == "both":
            img |= {r1, r2}
        elif convention == "lex":
            img.add(r1 if b1 < b2 else r2)
        elif convention == "lexmax":
            img.add(r1 if b1 > b2 else r2)
        else:
            sys.exit("unknown convention " + convention)
    return img


def decode(img):
    """Recover the animal: the king cells are exactly the FULL 2x2 blocks.

    Sound under "lex" for a reason that is a proof, not a measurement. Block
    (x, y) owns refined cell (2x, 2y) at grid corner (x, y), and the two
    candidates at that corner are always (x-1, y-1) and (x, y) -- so the block
    itself is the lex-LARGER candidate there and never wins that mark. Its
    bottom-left cell therefore stays empty unless the block is a real animal
    cell, a block is never completed by marks, and the map is injective.
    """
    blocks = defaultdict(int)
    for (u, v) in img:
        blocks[(u // 2, v // 2)] += 1
    return frozenset(k for k, c in blocks.items() if c == 4)


def pinched(img):
    """A corner of the REFINED grid with exactly one diagonal pair filled."""
    for (x, y) in list(img):
        for dx, dy in ((1, 1), (1, -1)):
            a, b = (x + dx, y + dy), (x + dx, y)
            c = (x, y + dy)
            if a in img and b not in img and c not in img:
                return ((x, y), a)
    return None


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    levels = king_animals(nmax)

    for n, lv in enumerate(levels, start=1):
        if len(lv) != A006770[n - 1]:
            sys.exit("GATE FAILED: %d king animals at n=%d, A006770 says %d"
                     % (len(lv), n, A006770[n - 1]))
    print("# gate ok: animal counts reproduce A006770 through n=%d" % nmax)
    print("# %s" % ", ".join("n=%d:%d" % (n, len(lv))
                             for n, lv in enumerate(levels, start=1)))

    for convention in ("none", "lex", "lexmax", "both"):
        red = convention == "none"
        seen = defaultdict(list)
        bad_pinch = None
        bad_decode = None
        for n, lv in enumerate(levels, start=1):
            for a in sorted(lv, key=sorted):
                img = image(a, convention)
                if bad_pinch is None:
                    p = pinched(img)
                    if p is not None:
                        bad_pinch = (n, sorted(a), p)
                if bad_decode is None and decode(img) != a:
                    bad_decode = (n, sorted(a), sorted(decode(img)))
                seen[norm(img)].append((n, tuple(sorted(a))))

        collisions = [v for v in seen.values() if len(v) > 1]
        tag = "RED " if red else "    "
        print("\n%s convention %-7s" % (tag, convention))
        if bad_pinch is None:
            print("%s   pinch-free : YES on all %d animals"
                  % (tag, sum(len(lv) for lv in levels)))
        else:
            n, a, p = bad_pinch
            print("%s   pinch-free : NO -- first at n=%d %s, refined corner "
                  "%s/%s" % (tag, n, a, p[0], p[1]))
        if bad_decode is None:
            print("%s   full-block decode : recovers the animal every time"
                  % tag)
        else:
            n, a, got = bad_decode
            print("%s   full-block decode : FAILS at n=%d %s -> %s"
                  % (tag, n, a, got))
        if not collisions:
            print("%s   injective  : YES, %d distinct images"
                  % (tag, len(seen)))
        else:
            first = min(collisions, key=lambda v: (v[0][0], v[0][1]))
            print("%s   injective  : NO -- %d colliding images; smallest:"
                  % (tag, len(collisions)))
            for n, a in first:
                print("%s                n=%d  %s" % (tag, n, list(a)))

        if red:
            if bad_pinch is None:
                sys.exit("RED FAILED: fattening with no filler came out "
                         "pinch-free, so the pinch detector has no teeth")
            print("%s   -> fired as expected" % tag)


if __name__ == "__main__":
    main()
