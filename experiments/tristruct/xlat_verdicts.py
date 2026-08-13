"""Cross-lattice falsification verdicts on the four machine-sweep survivors
(docs/triangle-structure-team-brief.md, Proposer 4).

The four survivors of Wave 0's mechanical sweep (before known.py culled them
as KNOWN-COINCIDENT) were, on the KING triangle:

  S1: T(n,3) mod 4 eventually periodic, period 8
  S2: T(n,3) mod 2 eventually periodic, period 4
  S3: T(n,4) mod 2 eventually periodic, period 4
  S4: T(n,3) satisfies an order-7 constant-coefficient recurrence

Lead's prior: all four are consequences of the column having a rational GF
(strip transfer matrix; results/triangle-structure.md pins king column GF
orders 3,7,15,42,106 for H=2..6).  If so, the SAME phenomena must appear on
the square and triangular lattices with their own orders/periods.  This
script measures that, in exact integer arithmetic:

  - minimal constant-coefficient linear recurrence order for each column
    T_lat(n,H), H = 3,4, fitted on a prefix and REQUIRED to hold on every
    remaining term (fit-low predict-high in n);
  - minimal eventual period mod m (m = 2,3,4,8), with preperiod, verified
    over the full available range with at least 3 full periods of holdout.

Inputs (all with recorded provenance):
  king   : banked triangle via triangle.py (results/ns_a40/perheight),
           columns H=3,4 are real-sweep for all n (README provenance table).
  square : data/square_col_tm_n60.txt from xlat_striptm.py, cross-checked
           cell-for-cell against the independent Redelmeier enumerator
           (build/xlat_enum) for n <= 14, and against OEIS (see the results
           file for A-numbers).
  tri    : data/tri_col_tm_n60.txt, same cross-checks, n <= 16.

Usage: python3 xlat_verdicts.py   (from experiments/tristruct/)
"""

import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))


def load_col(path, H):
    seq = {}
    with open(path) as f:
        for line in f:
            n, h, v = line.split()
            if int(h) == H:
                seq[int(n)] = int(v)
    lo = min(seq)
    hi = max(seq)
    assert set(seq) == set(range(lo, hi + 1))
    return lo, [seq[n] for n in range(lo, hi + 1)]


def load_king_col(H):
    import sys
    sys.path.insert(0, HERE)
    from triangle import Triangle
    t = Triangle.load()
    vals = [t.cell(n, H) for n in range(H, 41)]
    return H, vals


def solve_lin(A, b):
    """Solve A x = b exactly over Q (A square, lists of Fractions).
    Returns x or None if singular."""
    m = [row[:] + [bv] for row, bv in zip(A, b)]
    nr = len(m)
    for col in range(nr):
        piv = next((r for r in range(col, nr) if m[r][col] != 0), None)
        if piv is None:
            return None
        m[col], m[piv] = m[piv], m[col]
        inv = m[col][col]
        m[col] = [v / inv for v in m[col]]
        for r in range(nr):
            if r != col and m[r][col] != 0:
                f = m[r][col]
                m[r] = [a - f * b2 for a, b2 in zip(m[r], m[col])]
    return [m[r][nr] for r in range(nr)]


def min_cfinite_order(vals, max_order=20):
    """Smallest r such that a constant-coefficient order-r recurrence fitted
    on the first 2r terms holds for EVERY subsequent term.  Returns
    (r, coeffs) with vals[k] = sum_i coeffs[i]*vals[k-1-i], or None."""
    N = len(vals)
    for r in range(1, max_order + 1):
        if 2 * r > N:
            return None
        A = [[Fraction(vals[k - 1 - i]) for i in range(r)]
             for k in range(r, 2 * r)]
        b = [Fraction(vals[k]) for k in range(r, 2 * r)]
        c = solve_lin(A, b)
        if c is None:
            continue
        ok = all(vals[k] == sum(c[i] * vals[k - 1 - i] for i in range(r))
                 for k in range(2 * r, N))
        if ok and N > 2 * r:
            return r, c
    return None


def eventual_period(vals, m, max_pre=20, max_per=64):
    """Smallest (preperiod, period) lexicographic-by-period such that
    vals[k] mod m is periodic for all k >= preperiod, verified over the whole
    range with >= 3 full periods after the preperiod.  None if not found."""
    res = [v % m for v in vals]
    N = len(res)
    for per in range(1, max_per + 1):
        for pre in range(0, max_pre + 1):
            if N - pre < 4 * per:
                break
            if all(res[k] == res[k + per] for k in range(pre, N - per)):
                return pre, per
    return None


def exact_period_from_recurrence(vals, order, coeffs, m):
    """Exact (preperiod, period) of vals mod m, given a verified
    constant-coefficient recurrence of the given order (coeffs as in
    min_cfinite_order).  The state (r consecutive residues) evolves
    deterministically mod m, so first-repeat of a state gives the exact
    preperiod and period of the residue sequence.  Integer coefficients
    required (checked); exact arithmetic throughout."""
    c = [int(x) for x in coeffs]
    assert all(x == y for x, y in zip(c, coeffs)), "non-integer coeffs"
    r = order
    state = tuple(v % m for v in vals[:r])
    seen = {state: 0}
    k = 0
    while k < 10**7:
        nxt = sum(c[i] * state[r - 1 - i] for i in range(r)) % m
        state = state[1:] + (nxt,)
        k += 1
        if state in seen:
            return seen[state], k - seen[state]
        seen[state] = k
    return None


def fmt_coeffs(c):
    return "[" + ", ".join(str(x) for x in c) + "]"


def main():
    cols = {}
    for lat, path in (('square', 'data/square_col_tm_n140.txt'),
                      ('tri', 'data/tri_col_tm_n140.txt')):
        for H in (3, 4):
            cols[(lat, H)] = load_col(os.path.join(HERE, path), H)
    for H in (3, 4):
        cols[('king', H)] = load_king_col(H)

    recs = {}
    print("column | n-range | min C-finite order (fit=first 2r, "
          "holdout=rest) | recurrence coeffs")
    for (lat, H), (lo, vals) in sorted(cols.items()):
        r = min_cfinite_order(vals, max_order=45)
        recs[(lat, H)] = r
        if r is None:
            print(f"T_{lat}(n,{H}) | n={lo}..{lo+len(vals)-1} | "
                  f"NONE up to order 45 | -")
        else:
            order, c = r
            hold = len(vals) - 2 * order
            print(f"T_{lat}(n,{H}) | n={lo}..{lo+len(vals)-1} | "
                  f"order {order} ({hold} holdout terms exact) | "
                  f"{fmt_coeffs(c)}")

    print()
    print("column | mod | (preperiod, period)")
    for (lat, H), (lo, vals) in sorted(cols.items()):
        rec = recs[(lat, H)]
        for m in (2, 3, 4, 8):
            if rec is not None:
                order, c = rec
                p = exact_period_from_recurrence(vals, order, c, m)
                if p is not None:
                    print(f"T_{lat}(n,{H}) | mod {m} | pre<={p[0]+lo}, "
                          f"period={p[1]} (EXACT via verified recurrence)")
                else:
                    print(f"T_{lat}(n,{H}) | mod {m} | period exists "
                          f"(C-finite) but cycle > 1e7 cap, undetermined")
                continue
            p = eventual_period(vals, m)
            s = (f"pre={p[0]+lo}, period={p[1]} (window n<={lo+len(vals)-1})"
                 if p else f"period>64 or pre>20 in window n<={lo+len(vals)-1}")
            print(f"T_{lat}(n,{H}) | mod {m} | {s}")


if __name__ == '__main__':
    main()
