#!/usr/bin/env python3
"""Order ideals of the square4 diamond-tip cone, by size.

The min-end law says each corner of the isoperimetric hull contributes a factor
P(x) -- a Young diagram grown independently at that corner -- so a hull with c
corners has free-removal generating function P(x)^c.  King boxes (c=4) and tri6
hexagons (c=6) obey it.  square4's diamond does not: its per-tip 4th root is
1, 1, 3, 5, 9, 14, ... and not the partition numbers.

The reason is that the diamond's tips are not lattice-aligned.  A king corner
spans the lattice's own quadrant {a >= 0, b >= 0}, whose order ideals are Young
diagrams -- hence P(x).  Undo the diamond's 45-degree rotation and a tip is
instead the cone

    C = {(a, b) in Z^2 : a >= |b|}

so the tip factor should be the order-ideal series of C, the cone's analogue of
a Young diagram.  This script computes it.

Coordinates.  Put u = a - b, v = a + b.  Then C is carried to

    Q = {(u, v) in Z_{>=0}^2 : u = v (mod 2)}

with the componentwise order, an index-2 sublattice of the quadrant.  Writing a
finite downset of Q by its column sizes c_u = #{v : (u,v) in I}, downward
closure is exactly

    a_i = c_{2i}   non-increasing        (even columns)
    b_i = c_{2i+1} non-increasing        (odd columns)
    a_i >= b_i                           (odd column sits inside its even one)
    b_i >= a_{i+1} - 1                   (the -1 is the parity offset)

i.e. pairs of partitions (lambda, mu) with mu contained in lambda and lambda
minus its first row and column contained in mu.  Size = |lambda| + |mu|.
Setting the offset to 0 instead of 1 collapses lambda = mu and recovers P(x),
which is the king control.
"""

import sys
from functools import lru_cache


def ideal_series(nmax, offset=1, slack=0):
    """[x^n] for n <= nmax of the order-ideal series of a cone.

    Two half-integer offsets control which coset of the index-2 sublattice the
    cone's apex lands on, and they are what distinguishes a SHARP corner from a
    BEVELLED one:

        offset=1, slack=0   apex ON the lattice -- the sharp diamond tip, phi_2
        offset=0, slack=1   apex OFF it -- the bevel, two minimal cells
        offset=0, slack=0   degenerate: a = b throughout, i.e. P(x) = phi_1

    In column terms: b_i <= a_i + slack and a_i <= b_{i-1} + offset, with both
    sequences non-increasing.
    """

    @lru_cache(maxsize=None)
    def rest(a_prev, b_prev, budget):
        """Counts by size for columns i, i+1, ... given column i-1 = (a_prev, b_prev)."""
        out = [0] * (budget + 1)
        out[0] = 1  # stop here: this column and every later one empty
        # `a` starts at 0, not 1.  With slack the even column may be EMPTY while
        # the odd one is not -- the bevel's ideal {(1,0)} has nothing below it,
        # so forcing a >= 1 silently drops those.  Both sequences are
        # non-increasing, so a = b = 0 really is the terminal case and is
        # counted once, above.
        for a in range(0, min(a_prev, b_prev + offset, budget) + 1):
            for b in range(0, min(a + slack, b_prev, budget - a) + 1):
                if a == 0 and b == 0:
                    continue
                used = a + b
                for n, cnt in enumerate(rest(a, b, budget - used)):
                    out[used + n] += cnt
        return tuple(out)

    # column 0 is unconstrained from the left
    return list(rest(nmax, nmax, nmax))


def index_m_cone_series(m, nmax):
    """Downsets by size of the general index-m cone, by brute-force enumeration.

    The cone spanned by the primitive rays (1,0) and (1,m) has index m; in the
    basis of those rays, scaled by m, the ambient lattice inside it becomes

        Q_m = {(U, V) in Z_{>=0}^2 : U + V = 0 (mod m)}

    under the componentwise order.  m=1 is the quadrant and must return the
    partition numbers; m=2 must agree with ideal_series() above.  This is the
    slow, obviously-correct enumerator, kept as the control on that one.
    """
    bound = m * nmax + m
    elts = [
        (u, v)
        for u in range(bound + 1)
        for v in range(bound + 1)
        if (u + v) % m == 0
    ]

    def below(p):
        u, v = p
        return [
            (u - du, v - dv)
            for du in range(m + 1)
            for dv in range(m + 1)
            if (du or dv) and u - du >= 0 and v - dv >= 0 and (u - du + v - dv) % m == 0
        ]

    cur = {frozenset()}
    counts = [1]
    for _ in range(nmax):
        nxt = set()
        for s in cur:
            for p in elts:
                if p not in s and all(q in s for q in below(p)):
                    nxt.add(s | {p})
        counts.append(len(nxt))
        cur = nxt
    return counts


def andrews_phi2(nmax):
    """Andrews' phi_2 via Memoirs AMS 301 eq. (5.9), an eta quotient.

    prod_{k>0} [(1-x^k)(1-x^{12k-10})(1-x^{12k-9})(1-x^{12k-3})(1-x^{12k-2})]^{-1}
    """
    out = [1] + [0] * nmax
    for k in range(1, nmax + 2):
        for e in (k, 12 * k - 10, 12 * k - 9, 12 * k - 3, 12 * k - 2):
            if 1 <= e <= nmax:
                for i in range(e, nmax + 1):
                    out[i] += out[i - e]
    return out


def poly_pow(series, k, nmax):
    out = [1] + [0] * nmax
    for _ in range(k):
        new = [0] * (nmax + 1)
        for i, x in enumerate(out):
            if not x:
                continue
            for j, y in enumerate(series[: nmax + 1 - i]):
                new[i + j] += x * y
        out = new
    return out


def andrews_a201077(nmax):
    """A201077, the bevel: 1 / prod (1-q^(2i-1))^2 (1-q^(12i-8))(1-q^(12i-6))
    (1-q^(12i-4))(1-q^(12i)).  An eta quotient, like phi_2."""
    out = [1] + [0] * nmax
    for i in range(1, nmax + 2):
        for e in (2 * i - 1, 2 * i - 1, 12 * i - 8, 12 * i - 6,
                  12 * i - 4, 12 * i):
            if 1 <= e <= nmax:
                for k in range(e, nmax + 1):
                    out[k] += out[k - e]
    return out


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    tip = ideal_series(nmax)
    bevel = ideal_series(nmax, offset=0, slack=1)
    print("cone {a >= |b|} order ideals by size:")
    print("  ", " ".join(str(x) for x in tip))
    print("quadrant control (offset 0, must be the partition numbers):")
    print("  ", " ".join(str(x) for x in ideal_series(nmax, offset=0)))
    print("bevel (same cone, apex OFF the lattice) = A201077:")
    print("  ", " ".join(str(x) for x in bevel))
    assert bevel == andrews_a201077(nmax), "bevel is not A201077"

    # The three square4 hull families, all with nothing fitted.
    c2 = poly_pow(tip, 2, nmax)
    d2 = poly_pow(bevel, 2, nmax)
    mixed = [sum(c2[k] * d2[n - k] for k in range(n + 1)) for n in range(nmax + 1)]
    print("odd W parity 0, 4 sharp tips        C^4    :",
          " ".join(str(x) for x in poly_pow(tip, 4, nmax)))
    print("even W parity 0, 2 sharp + 2 bevels C^2 D^2:",
          " ".join(str(x) for x in mixed))
    print("odd W parity 1, 4 bevels            D^4    :",
          " ".join(str(x) for x in poly_pow(bevel, 4, nmax)))
    print("A120452, the six-term match that is wrong at the seventh:")
    print("   1 1 3 5 9 14 23 34 52 75 109 155 219")
    print("4th power = square4 diamond free-removals:")
    print("  ", " ".join(str(x) for x in poly_pow(tip, 4, nmax)))

    andrews = andrews_phi2(nmax)
    print("Andrews phi_2 = A053993, product form (5.9):")
    print("  ", " ".join(str(x) for x in andrews))
    assert andrews == tip, "cone ideals are not phi_2"

    # controls: the brute-force enumerator must reproduce both known cases
    small = min(nmax, 9)
    assert index_m_cone_series(1, small) == ideal_series(small, offset=0)[: small + 1]
    assert index_m_cone_series(2, small) == tip[: small + 1]
    print("index-3 cone (phi_m generalization FAILS here; phi_3 is A053992):")
    print("  ", " ".join(str(x) for x in index_m_cone_series(3, small)))


if __name__ == "__main__":
    main()
