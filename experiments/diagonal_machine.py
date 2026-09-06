#!/usr/bin/env python3
"""The diagonal machine: proved closed forms for T(n, n-k) on any row-local lattice.

docs/proofs/universal-diagonal-law.md Theorem A says that for every row-local
lattice with drift set D (b = |D|),

    T(H+k, H) = q_k(H) * b^H   for all H >= k+1,   deg q_k <= k.

A proved degree bound plus a proved onset turns k+1 enumerated values into a
theorem. This script supplies the values, for an ARBITRARY drift set, with a
surplus-budgeted row transfer DP whose cost depends on k and H rather than on
the number of animals -- so it reaches k where enumerating animals cannot.

    state = (this row's cells, normalized;
             which connected component of the animal-so-far each belongs to;
             surplus spent)

Every component must keep a cell in the current row or it can never reconnect,
so stranded components are pruned at the transition. At height H the states
with a single component are the animals with bounding-box height exactly H.

`experiments/defect_gas.py` does something finer for the king lattice -- it
factors the same counts into cluster weights, which is where the coefficients
come from rather than the values. That machinery is written for
(dx, dr) in (-1,0,1)^2 and is not lattice-parametric; this is.

WINDOW: rows may have gaps (that is what makes the king pair weight 25 =
16 + 9), so positions are searched in a window and the answer must be checked
for stability in the window size. defect_gas.py records a bug of exactly this
kind (W = 6 clipped a cluster weight); every run here reports the check.

Usage: python3 -m experiments.diagonal_machine
"""
import sys
from fractions import Fraction
from itertools import combinations

# Row-local lattices: D = up-offsets, b = |D|. Within-row adjacency is |dx| = 1.
LATTICES = {
    "square": (0,),
    "hex": (-1, 0),
    "king": (-1, 0, 1),
}

# Known values, to be reproduced rather than assumed (docs/proofs/*, OEIS).
KNOWN = {
    ("square", 1): "4n - 8",          # A308359, proved there
    ("square", 2): "8n^2 - 51n + 86",  # A308359, CONJECTURED there
    ("hex", 1): "9n - 15",            # results/diagonal-formula.md
    ("king", 1): "25n - 45",          # docs/proofs/diagonal-law.md
}


def canonical(cells, comp):
    """Normalize a row state: shift to min 0, relabel components in order."""
    m = min(cells)
    shifted = tuple(c - m for c in cells)
    seen = {}
    labels = []
    for c in shifted:
        cid = comp[c + m]
        if cid not in seen:
            seen[cid] = len(seen)
        labels.append(seen[cid])
    return shifted, tuple(labels)


def merge(parent, a, b):
    ra, rb = find(parent, a), find(parent, b)
    if ra != rb:
        parent[rb] = ra


def find(parent, a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


def row_sets(lo, hi, size):
    """All size-element subsets of [lo, hi]."""
    return combinations(range(lo, hi + 1), size)


def diagonal_counts(drift, kmax, hmax, window):
    """T[(H, k)] for H <= hmax, k <= kmax: animals of height exactly H, H+k cells."""
    D = set(drift)
    T = {}
    # Seed: row 1, with (1 + s) cells; components from within-row adjacency.
    states = {}
    for s in range(kmax + 1):
        for cells in row_sets(0, window, 1 + s):
            if cells[0] != 0:
                continue                      # normalized: leftmost at 0
            comp = {c: c for c in cells}
            for a, bcell in zip(cells, cells[1:]):
                if bcell - a == 1:
                    merge(comp, a, bcell)
            comp = {c: find(comp, c) for c in cells}
            key = (canonical(cells, comp), s)
            states[key] = states.get(key, 0) + 1

    for H in range(1, hmax + 1):
        for ((cells, labels), s), cnt in states.items():
            if len(set(labels)) == 1:
                T[(H, s)] = T.get((H, s), 0) + cnt
        if H == hmax:
            break
        nxt = {}
        for ((cells, labels), s), cnt in states.items():
            budget = kmax - s
            lo, hi = min(cells) - window, max(cells) + window
            for extra in range(budget + 1):
                for new in row_sets(lo, hi, 1 + extra):
                    # union-find over old components (by label) and new cells
                    parent = {}
                    for lab in set(labels):
                        parent[("o", lab)] = ("o", lab)
                    for c in new:
                        parent[("n", c)] = ("n", c)
                    for a, bcell in zip(new, new[1:]):
                        if bcell - a == 1:
                            merge(parent, ("n", a), ("n", bcell))
                    touched = set()
                    for c, lab in zip(cells, labels):
                        for q in new:
                            if q - c in D:
                                merge(parent, ("o", lab), ("n", q))
                                touched.add(lab)
                    if touched != set(labels):
                        continue              # a component is stranded
                    comp = {q: find(parent, ("n", q)) for q in new}
                    ids = {}
                    for q in new:
                        ids.setdefault(comp[q], len(ids))
                    key = (canonical(new, {q: ids[comp[q]] for q in new}),
                           s + extra)
                    nxt[key] = nxt.get(key, 0) + cnt
        states = nxt
    return T


def interpolate(points):
    """Exact interpolation, coefficients highest degree first."""
    n = len(points)
    acc = [Fraction(0)] * n
    for i, (xi, yi) in enumerate(points):
        basis, denom = [Fraction(1)], Fraction(1)
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            shifted = [Fraction(0)] + basis
            scaled = [Fraction(xj) * c for c in basis] + [Fraction(0)]
            basis = [a - b for a, b in zip(shifted, scaled)]
            denom *= Fraction(xi - xj)
        scale = Fraction(yi) / denom
        for idx, c in enumerate(basis):
            acc[idx] += c * scale
    return acc[::-1]


def fmt(co):
    deg = len(co) - 1
    out = []
    for i, c in enumerate(co):
        p = deg - i
        if c == 0:
            continue
        term = f"{c}" if p == 0 else (f"{c}n" if p == 1 else f"{c}n^{p}")
        out.append(term)
    return " + ".join(out).replace("+ -", "- ") if out else "0"


def evaluate(co, x):
    v = Fraction(0)
    for c in co:
        v = v * x + c
    return v


def run(name, kmax, hmax, window):
    drift = LATTICES[name]
    b = len(drift)
    T = diagonal_counts(drift, kmax, hmax, window)
    Tw = diagonal_counts(drift, kmax, hmax, window + 2)
    if T != Tw:
        diff = [key for key in set(T) | set(Tw) if T.get(key) != Tw.get(key)]
        print(f"  WINDOW UNSTABLE at w={window} vs {window+2}: {diff[:5]}")
        return False, {}

    print(f"  {name} (b = {b}), window {window} stable")
    forms = {}
    ok = True
    for k in range(1, kmax + 1):
        onset = k + 1                       # H >= k+1, i.e. n >= 2k+1
        hs = [H for H in range(onset, hmax + 1) if (H, k) in T]
        if len(hs) < k + 2:
            print(f"    k={k}: need {k+2} values from H={onset}, have {len(hs)}")
            ok = False
            continue
        # q_k(H) = T(H+k, H) / b^H, interpolated from the first k+1 on-onset values
        pts = [(H, Fraction(T[(H, k)], b ** H)) for H in hs[:k + 1]]
        q = interpolate(pts)
        held = [H for H in hs[k + 1:] if evaluate(q, H) != Fraction(T[(H, k)], b ** H)]
        # in n: T(n, n-k) = P_k(n) b^(n-1-3k), P_k(n) = b^(1+2k) q_k(n-k)
        Pn = [c for c in interpolate([(H + k, Fraction(b) ** (1 + 2 * k) * evaluate(q, H))
                                      for H in hs[:k + 1]])]
        status = "HOLDS" if not held else f"FAILS at H={held[:3]}"
        print(f"    k={k}: P_{k}(n) = {fmt(Pn)}   [{len(hs) - (k+1)} holdouts {status}]")
        if held:
            ok = False
        forms[(name, k)] = fmt(Pn)
        want = KNOWN.get((name, k))
        if want:
            got = fmt(Pn).replace(" ", "")
            if got != want.replace(" ", ""):
                print(f"      MISMATCH against known {want}")
                ok = False
            else:
                print(f"      == {want}  (matches the published form)")
        # onset must be sharp: the formula must fail one step earlier
        if (k, k) in [(H, k) for H in [k]] or (k, k) in T:
            if evaluate(q, k) == Fraction(T[(k, k)], b ** k):
                print(f"      onset control: FAILS -- formula also holds at H=k")
                ok = False
    return ok, forms


def identify():
    """Which lattice is each drift set, really? Brute force small n and name it.

    Guards against a mislabelling that would be easy to make and hard to spot:
    D = (-1, 0) is SIX-regular, i.e. polyhexes -- cells are HEXAGONS, and it is
    their centres that form the triangular point lattice. Animals of equilateral
    TRIANGLES (polyiamonds) are a different object: three neighbours per cell,
    alternating orientation, A001420 rather than A001207, and outside this class
    entirely because the adjacency is parity-dependent.
    """
    from experiments.universal_pair_weights import neighbors

    KNOWN_TOTALS = {
        "square": ("A001168 fixed polyominoes",
                   [1, 2, 6, 19, 63, 216, 760, 2725]),
        "hex": ("A001207 fixed hexagonal polyominoes (= triangular-lattice "
                "site animals)", [1, 3, 11, 44, 186, 814, 3652, 16689]),
        "king": ("A006770 fixed polyplets", [1, 4, 20, 110, 638, 3832, 23592,
                                             147941]),
    }
    print("Lattice identification (brute force, n <= 8):")
    ok = True
    for name, D in LATTICES.items():
        seen = {frozenset({(0, 0)})}
        frontier = list(seen)
        got = [1]
        for _ in range(2, 9):
            nxt = set()
            for a in frontier:
                for c in a:
                    for nb in neighbors(c, D):
                        if nb in a:
                            continue
                        q = a | {nb}
                        mx = min(x for x, _ in q)
                        my = min(y for _, y in q)
                        q = frozenset((x - mx, y - my) for x, y in q)
                        if q not in seen:
                            seen.add(q)
                            nxt.add(q)
            got.append(len(nxt))
            frontier = list(nxt)
        deg = len(set(neighbors((0, 0), D)))
        label, want = KNOWN_TOTALS[name]
        match = got == want
        ok &= match
        print(f"  {name:7s} D={str(D):11s} degree {deg}  {label}"
              f"{'' if match else '  MISMATCH: ' + str(got)}")
    return ok


def main():
    if not identify():
        print("lattice identification failed; the labels are wrong")
        return 1
    print("\nReproducing the three published instances, then extending:")
    ok = True
    o1, _ = run("square", 4, 14, 6)
    o2, _ = run("hex", 3, 12, 6)
    o3, _ = run("king", 2, 10, 6)
    ok = o1 and o2 and o3
    print("\nEach P_k above is a THEOREM given Theorem A: the degree bound and "
          "the\nonset are proved there, the values are enumerated here, and the "
          "holdouts\nare a check rather than the evidence.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
