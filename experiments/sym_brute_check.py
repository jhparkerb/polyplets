#!/usr/bin/env python3
"""Independent brute-force check of the OW-7 symmetry counts, n = 1..6.

Purpose: the 2026-07-31 adversarial review (docs/reviews/
outworks-adversarial.md, M2) found Symmetry.lean's claim of an n = 6
out-of-file verification had no committed artifact. This is that artifact:
a from-scratch enumeration, independent of both the Lean tree and the
engine pipeline that produced results/sym_counts.txt.

Method: enumerate ALL fixed king animals n = 1..6 by growth (counts must
reproduce A006770: 1, 4, 20, 110, 638, 3832), then for each of the eight
D4 point maps count the animals whose canonical form is fixed. Conventions
match Symmetry.lean and the engine: r90 (x,y)->(-y,x); r180 (x,y)->(-x,-y);
hmirror = axis mirror (x,y)->(x,-y); dmirror = diagonal mirror
(x,y)->(y,x). Derived Burnside counts free/onesided/bilateral are checked
against A030222 / A030233 / A030234.

Expected values (results/sym_counts.txt):
  r90    n=1..6: 1, 0, 0, 2, 2, 0
  r180   n=1..6: 1, 4, 4, 22, 22, 132
  hmirror n=1..6: 1, 2, 4, 10, 22, 58
  dmirror n=1..6: 1, 2, 4, 10, 22, 56     <- the 58/56 split at n = 6 is
                                             exactly what Lean's in-file
                                             anchors (n <= 5) cannot see.
Exact command:  python3 experiments/sym_brute_check.py \
                  | tee experiments/sym_brute_check.log
Target machine: any (run 2026-07-31 on the local Mac).
Predicted cost: seconds (3,832 animals at n = 6). Pure stdlib.
Resume/kill:    stateless.
"""

K8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]

A006770 = [1, 4, 20, 110, 638, 3832]
EXPECT = {
    "r90":     [1, 0, 0, 2, 2, 0],
    "r180":    [1, 4, 4, 22, 22, 132],
    "hmirror": [1, 2, 4, 10, 22, 58],
    "dmirror": [1, 2, 4, 10, 22, 56],
}
A030222 = [1, 2, 5, 22, 94, 524]      # free
A030233 = [1, 2, 6, 34, 166, 991]     # one-sided
A030234 = [1, 2, 4, 10, 22, 57]       # bilateral

MAPS = {
    "id":      lambda x, y: (x, y),
    "r90":     lambda x, y: (-y, x),
    "r180":    lambda x, y: (-x, -y),
    "r270":    lambda x, y: (y, -x),
    "hmirror": lambda x, y: (x, -y),
    "vmirror": lambda x, y: (-x, y),
    "dmirror": lambda x, y: (y, x),
    "amirror": lambda x, y: (-y, -x),
}


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


def main():
    cur = {frozenset({(0, 0)})}
    ok = True
    for i, n in enumerate(range(1, 7)):
        if n > 1:
            cur = grow(cur)
        assert len(cur) == A006770[i], f"A006770({n}) mismatch: {len(cur)}"
        fix = {}
        for name, f in MAPS.items():
            fix[name] = sum(1 for S in cur
                            if canon({f(x, y) for x, y in S}) == S)
        line = f"n={n} fixed={fix['id']}"
        for name in ("r90", "r180", "hmirror", "dmirror"):
            got, want = fix[name], EXPECT[name][i]
            tag = "" if got == want else f" MISMATCH(want {want})"
            ok = ok and got == want
            line += f" {name}={got}{tag}"
        # sanity: conjugate elements have equal fixed counts
        assert fix["r90"] == fix["r270"] and fix["hmirror"] == fix["vmirror"] \
            and fix["dmirror"] == fix["amirror"]
        free8 = fix["id"] + 2 * fix["r90"] + fix["r180"] \
            + 2 * fix["hmirror"] + 2 * fix["dmirror"]
        one4 = fix["id"] + 2 * fix["r90"] + fix["r180"]
        bil2 = fix["hmirror"] + fix["dmirror"]
        assert free8 % 8 == 0 and one4 % 4 == 0 and bil2 % 2 == 0
        d = {"free": free8 // 8, "onesided": one4 // 4, "bilateral": bil2 // 2}
        for name, oeis in (("free", A030222), ("onesided", A030233),
                           ("bilateral", A030234)):
            got, want = d[name], oeis[i]
            tag = "" if got == want else f" MISMATCH(want {want})"
            ok = ok and got == want
            line += f" {name}={got}{tag}"
        print(line, flush=True)
    print("ALL MATCH" if ok else "MISMATCHES FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
