#!/usr/bin/env python3
"""Cross-check the five height-H dimension ladders against each other.

Banked numbers only, no enumeration; runs in well under a second.  Every
assertion is one of the inequalities argued in the "Five ladders" section of
results/skeletonkey-hankel-closure.md, or a re-check of a negative result
quoted there.  Exits nonzero on the first failure.

Sources:
  char-2 column rank r(H)      results/exactchange-probes.md  (A034299)
  char-0 Hankel rank           results/skeletonkey-hankel-closure.md
  reach-merged classes N(H)    results/nkey-census.md
  raw column frontier          Motzkin(H+1) - 1
  deg psi_H                    results/anisotropic-not-dfinite.md
  cell-level d_p, d_2          results/skeletonkey-cell-sparsity.md
"""
import sys
from fractions import Fraction

fail = []


def check(name, ok):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        fail.append(name)


# ---------------------------------------------------------------- the ladders
r2 = dict(zip(range(4, 14), [6, 15, 27, 58, 112, 229, 453, 912, 1818, 3643]))
hankel = dict(zip(range(4, 12), [6, 17, 35, 88, 204, 501, 1217, 3016]))
merged = dict(zip(range(4, 22),
                  [8, 19, 43, 101, 239, 575, 1399, 3441, 8539, 21355, 53763,
                   136145, 346539, 886111, 2275103, 5862925, 15159215,
                   39314963]))
psi = dict(zip(range(1, 11), [1, 2, 4, 9, 29, 68, 181, 462, 1254, 3289]))
d_p = dict(zip(range(4, 9), [32, 99, 249, 692, 1826]))
d_2 = dict(zip(range(4, 9), [32, 93, 210, 516, 1155]))


def motzkin(n):
    m = [1, 1]
    while len(m) <= n:
        k = len(m) - 1
        m.append(m[k] + sum(m[i] * m[k - 1 - i] for i in range(k)))
    return m[n]


frontier = {H: motzkin(H + 1) - 1 for H in range(2, 22)}

check("frontier = Motzkin(H+1)-1 reproduces the banked rook control",
      [frontier[H] for H in range(2, 11)] ==
      [3, 8, 20, 50, 126, 322, 834, 2187, 5797])

# ------------------------------------------------------------- the inequalities
# rank over F_2 <= rank over Q of the same integer matrix (x = 1)
check("char-2 column rank <= char-0 Hankel rank (H = 4..11)",
      all(r2[H] <= hankel[H] for H in range(4, 12)))
check("char-2 cell rank <= cell-level d_p (H = 4..8)",
      all(d_2[H] <= d_p[H] for H in range(4, 9)))

# reach-equivalent states have identical Hankel rows over every field
check("char-0 Hankel rank <= merged class count (H = 4..11)",
      all(hankel[H] <= merged[H] for H in range(4, 12)))
check("char-2 column rank <= merged class count (H = 4..13)",
      all(r2[H] <= merged[H] for H in range(4, 14)))

# the merged set is a quotient of the raw frontier
check("merged class count <= raw column frontier (H = 4..21)",
      all(merged[H] <= frontier[H] for H in range(4, 22)))

# the column-level Hankel matrix is a submatrix of the cell-level one
check("column ranks <= cell ranks, both characteristics (H = 4..8)",
      all(hankel[H] <= d_p[H] and r2[H] <= d_2[H] for H in range(4, 9)))

# each column carries at most H cells, so deg Q_H <= H * (number of states)
check("deg psi_H <= H * merged class count (H = 4..10)",
      all(psi[H] <= H * merged[H] for H in range(4, 11)))

# and deg psi_H is NOT bounded by the char-0 Hankel rank: different objects
check("deg psi_H exceeds the char-0 Hankel rank at H = 7..10",
      all(psi[H] > hankel[H] for H in range(7, 11)))

# ------------------------------------------- no short C-finite fit for the floor
seq = [hankel[H] for H in range(4, 12)]


def cfinite_consistent(order, constant=True):
    """Is there a recurrence seq[i+order] = sum c_j seq[i+j] (+ c) fitting
    every window?  Exact rational elimination; None when the system carries
    no surplus and so cannot exclude anything."""
    unknowns = order + (1 if constant else 0)
    windows = len(seq) - order
    if windows - unknowns < 1:
        return None
    A = []
    for i in range(windows):
        row = [Fraction(seq[i + j]) for j in range(order)]
        if constant:
            row.append(Fraction(1))
        A.append(row + [Fraction(seq[i + order])])
    piv = 0
    for col in range(unknowns):
        sel = next((r for r in range(piv, len(A)) if A[r][col] != 0), None)
        if sel is None:
            continue
        A[piv], A[sel] = A[sel], A[piv]
        inv = A[piv][col]
        A[piv] = [v / inv for v in A[piv]]
        for r in range(len(A)):
            if r != piv and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[piv])]
        piv += 1
    return not any(all(v == 0 for v in row[:unknowns]) and row[unknowns] != 0
                   for row in A)


tested = {k: cfinite_consistent(k) for k in range(1, 6)}
print("C-finite fits with a constant term, eight char-0 Hankel values:")
for k, v in tested.items():
    print("  order %d: %s" % (k, {True: "FITS", False: "excluded",
                                  None: "no surplus, untestable"}[v]))
check("no C-finite recurrence of order <= 3 with constant term fits",
      all(tested[k] is False for k in (1, 2, 3)))
check("order 4 and 5 carry no surplus at eight points and are NOT excluded",
      tested[4] is None and tested[5] is None)
check("homogeneous order 4 carries no surplus either",
      cfinite_consistent(4, constant=False) is None)

# ------------------------------------------------------------------ growth rates
def geo(d, lo, hi):
    return (d[hi] / d[lo]) ** (1.0 / (hi - lo))


print("\ngrowth per height (over the range known / last rung):")
rows = [("char-2 column rank", r2, 4, 13), ("char-0 Hankel rank", hankel, 4, 11),
        ("reach-merged classes", merged, 4, 21), ("deg psi_H", psi, 1, 10),
        ("cell-level d_2", d_2, 4, 8), ("cell-level d_p", d_p, 4, 8), ("raw column frontier", frontier, 4, 21)]
for name, d, lo, hi in rows:
    print("  %-22s H=%-2d..%-2d  %.3f  %.3f"
          % (name, lo, hi, geo(d, lo, hi), d[hi] / d[hi - 1]))

check("growth order over the common ladder: char-2 < Hankel < merged < frontier",
      geo(r2, 4, 13) < geo(hankel, 4, 11) < geo(merged, 4, 21)
      < geo(frontier, 4, 21))
check("same order on last rungs",
      r2[13] / r2[12] < hankel[11] / hankel[10]
      < merged[21] / merged[20] < frontier[21] / frontier[20])

if fail:
    print("\n%d CHECK(S) FAILED: %s" % (len(fail), "; ".join(fail)))
    sys.exit(1)
print("\nall checks green")
