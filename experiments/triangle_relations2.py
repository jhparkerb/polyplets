#!/usr/bin/env python3
"""Deeper relation hunt in the polyplet triangle T(n,H) -- part 2.

Follow-ups to triangle_relations.py (which confirmed per-column constant-coeff
recurrences of order 1,3,7,15 for H=1..4 and nothing pinnable for H>=5):

  (A) characteristic polynomials of the confirmed column recurrences and
      whether p_{H-1} divides p_H (nested strip denominators);
  (B) cross-column stencil hunt: exact constant-coeff linear relations
          T(n,H) = sum_{(j,d) in stencil} c_{j,d} T(n-j, H-d)
      for middle heights -- the literal "T(n,H) vs T(n-1,_)" question;
  (C) P-recursive hunt: per-column recurrences with coefficients polynomial
      in n (holonomic columns can have far lower order than the rational-GF
      order; calibrate on H=2..4 where the answer is known);
  (D) strip cumulative sequences C_H(n) = sum_h (H-h+1) T(n,h) (what a naive
      height-<=H strip transfer matrix actually counts): minimal recurrences;
  (E) second-source coverage count of the 35-row triangle
      (columns H<=4 by recurrence + diagonals covered by P_k closed forms).
"""
import os, sys
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triangle_relations import load_triangle, col_seq, find_min_recurrence, NMAX


def nullspace(rows, ncols):
    """Exact nullspace basis of the m x ncols system rows . x = 0."""
    M = [[F(x) for x in r] for r in rows]
    m = len(M)
    pivots = []
    r = 0
    for c in range(ncols):
        if r >= m:
            break
        piv = next((i for i in range(r, m) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = F(1) / M[r][c]
        M[r] = [x * inv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for fc in free:
        v = [F(0)] * ncols
        v[fc] = F(1)
        for i, pc in enumerate(pivots):
            v[pc] = -M[i][fc]
        basis.append(v)
    return basis


def poly_divides(p, q):
    """True if poly p divides q exactly (coeff lists, highest degree first)."""
    q = [F(x) for x in q]
    dp, dq = len(p) - 1, len(q) - 1
    if dp > dq:
        return False
    for i in range(dq - dp + 1):
        f = q[i] / p[0]
        for j in range(dp + 1):
            q[i + j] -= f * p[j]
    return all(x == 0 for x in q[dq - dp + 1:])


def charpoly(coeffs):
    """T(n)=sum c_j T(n-j)  ->  x^d - c1 x^{d-1} - ... - cd (highest first)."""
    return [F(1)] + [-c for c in coeffs]


def section_A(T):
    print("== (A) column char polys and nesting ==")
    polys = {}
    for H in range(1, 5):
        seq = col_seq(T, H)
        d, c, ho = find_min_recurrence(seq)
        polys[H] = charpoly(c)
        cs = ", ".join(str(x) for x in c)
        print(f"  H={H}: order {d}, T(n) = {cs} (coeffs on T(n-1)..T(n-{d}))")
    for H in range(2, 5):
        div = poly_divides(polys[H - 1], polys[H])
        print(f"  p_{H-1} | p_{H}: {'YES' if div else 'no'}")
    return polys


def stencil_hunt(T, H, maxj, dset, nstart):
    """Exact relation T(n,H) - sum c_{j,d} T(n-j,H-d) = 0 over all n in
    [nstart..NMAX]. Returns (vars, coeffs, excess) or None."""
    vars_ = [(j, d) for j in range(0, maxj + 1) for d in dset
             if (j, d) != (0, 0) and 1 <= H - d]
    rows = []
    for n in range(nstart, NMAX + 1):
        row = [T.get((n, H), 0)]
        for (j, d) in vars_:
            row.append(-T.get((n - j, H - d), 0))
        rows.append(row)
    ncols = 1 + len(vars_)
    excess = len(rows) - ncols
    if excess < 4:
        return None
    for v in nullspace(rows, ncols):
        if v[0] != 0:
            coeffs = [x / v[0] for x in v[1:]]
            return (vars_, coeffs, excess)
    return None


def section_B(T):
    print()
    print("== (B) cross-column stencil hunt (constant coeffs) ==")
    dsets = [(0,), (0, 1), (-1, 0, 1), (0, 1, 2), (-1, 0, 1, 2)]
    any_found = False
    for H in range(5, 13):
        found = None
        for maxj in (1, 2, 3, 4):
            for dset in dsets:
                nvars = sum(1 for j in range(maxj + 1) for d in dset
                            if (j, d) != (0, 0) and H - d >= 1)
                if nvars > 18:
                    continue
                for nstart in (H, H + 3):
                    r = stencil_hunt(T, H, maxj, dset, nstart)
                    if r:
                        found = (maxj, dset, nstart, r)
                        break
                if found:
                    break
            if found:
                break
        if found:
            any_found = True
            maxj, dset, nstart, (vars_, coeffs, excess) = found
            print(f"  H={H}: RELATION depth j<={maxj} cols H-{list(dset)} "
                  f"from n={nstart} (excess {excess})")
            terms = [f"{c}*T(n-{j},H-{d})" for (j, d), c in zip(vars_, coeffs)
                     if c != 0]
            print(f"        T(n,{H}) = " + " + ".join(terms))
        else:
            print(f"  H={H}: none (stencils up to depth 4 x cols H-2..H+1)")
    if not any_found:
        print("  -> no finite constant-coeff cross-column stencil fits any middle column")


def precursive_hunt(seq, d, deg):
    """Nontrivial sum_{j=0..d} p_j(n) seq[n-j] = 0 with deg(p_j)<=deg,
    valid at every index. Returns (kernel, excess) or None.
    n here = actual index within seq (offset-free; a poly in seq-index is a
    poly in n)."""
    L = len(seq)
    ncols = (d + 1) * (deg + 1)
    rows = []
    for i in range(d, L):
        row = []
        for j in range(d + 1):
            for e in range(deg + 1):
                row.append((i ** e) * seq[i - j])
        rows.append(row)
    excess = len(rows) - ncols
    if excess < 5:
        return None
    ns = nullspace(rows, ncols)
    for v in ns:
        # require the j=0 coefficient polynomial nonzero (usable as recurrence)
        if any(v[e] != 0 for e in range(deg + 1)):
            return (v, excess)
    if ns:
        return (ns[0], excess)
    return None


def section_C(T):
    print()
    print("== (C) P-recursive hunt (poly-in-n coefficients) ==")
    print("  calibration on H=2..4 (rational, orders 3/7/15), then H=5..12")
    for H in range(2, 13):
        seq = col_seq(T, H)
        best = None
        for total in range(2, 40):
            for d in range(1, 7):
                for deg in range(0, 4):
                    if (d + 1) * (deg + 1) != total:
                        continue
                    r = precursive_hunt(seq, d, deg)
                    if r:
                        best = (d, deg, r[1])
                        break
                if best:
                    break
            if best:
                break
        if best:
            d, deg, excess = best
            print(f"  H={H:2d}: P-recurrence order {d}, coeff deg {deg} "
                  f"(unknowns {(d+1)*(deg+1)}, excess {excess})")
        else:
            print(f"  H={H:2d}: none up to order 6 / deg 3 with excess>=5")


def section_D(T):
    print()
    print("== (D) strip cumulative C_H(n) = sum_h (H-h+1) T(n,h) ==")
    print("  (what a naive height-H strip TM counts; starts at n=1, 35 terms)")
    for H in range(1, 7):
        seq = [sum((H - h + 1) * T.get((n, h), 0) for h in range(1, H + 1))
               for n in range(1, NMAX + 1)]
        r = find_min_recurrence(seq)
        if r:
            d, c, ho = r
            print(f"  H={H}: order {d}, holdout {ho}")
        else:
            print(f"  H={H}: not pinnable from 35 terms")
    return


def section_E(T):
    print()
    print("== (E) second-source coverage of the triangle ==")
    total = sum(1 for n in range(1, NMAX + 1) for H in range(1, n + 1))
    cov = set()
    # columns H<=4: independently regenerable by confirmed recurrence
    for H in range(1, 5):
        for n in range(H, NMAX + 1):
            cov.add((n, H))
    # diagonals H = n-k with P_k closed form: derived for k<=16, valid n>=3k+1
    diag = set()
    for k in range(0, 17):
        for n in range(3 * k + 1, NMAX + 1):
            H = n - k
            if 1 <= H <= n:
                diag.add((n, H))
    both = cov & diag
    cov |= diag
    print(f"  triangle entries (n<=35):          {total}")
    print(f"  columns H<=4 (recurrence):         {sum(1 for c in cov if c[1] <= 4)}")
    print(f"  diagonals k<=16 via P_k (n>=3k+1): {len(diag)}  (overlap {len(both)})")
    print(f"  second-sourced total:              {len(cov)}  "
          f"({100.0*len(cov)/total:.1f}%)")
    single = total - len(cov)
    print(f"  single-source middle entries:      {single}")
    # what naive strip TM up to H=K would add
    for K in (8, 10, 12, 14):
        add = sum(1 for n in range(1, NMAX + 1) for H in range(5, min(n, K) + 1)
                  if (n, H) not in cov)
        print(f"  + naive strip engine to H={K:2d} adds {add:3d} "
              f"-> {100.0*(len(cov)+add)/total:.1f}%")


def main():
    T = load_triangle()
    section_A(T)
    section_B(T)
    section_C(T)
    section_D(T)
    section_E(T)


if __name__ == "__main__":
    main()
