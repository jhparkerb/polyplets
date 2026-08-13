"""r3_harness_exposure.py -- round-3 harness, PART 2: row-40 exposure table.

Recomputes, from the banked file via Triangle.load(), the share of a(40) held
by each band, the per-cell shares for H=15..21 at n=40, and the loader's
provenance string for each of those cells. Exact integer arithmetic; shares
printed as exact fractions and as 4-decimal roundings.
"""

from fractions import Fraction
from triangle import Triangle

tri = Triangle.load()
a40 = tri.rowsum(40)
print("a(40) =", a40)
rowsum_check = sum(tri.cell(40, H) for H in range(1, 41))
print("sum_H T(40,H) == a(40):", rowsum_check == a40)

bands = [
    ("H<=2", range(1, 3)),
    ("H=3..14", range(3, 15)),
    ("H=15..19", range(15, 20)),
    ("H=15..21", range(15, 22)),
    ("H>=22", range(22, 41)),
    ("H<=14", range(1, 15)),
]
for name, Hs in bands:
    s = sum(tri.cell(40, H) for H in Hs)
    f = Fraction(s, a40)
    print("%-9s sum=%d  share=%s  pct=%.4f%%" % (name, s, f, float(f) * 100))

print()
print("per-cell, n=40, H=15..21:")
for H in range(15, 22):
    c = tri.cell(40, H)
    f = Fraction(c, a40)
    print("H=%d  T(40,%d)=%d  share_pct=%.4f%%  provenance=%r"
          % (H, H, c, float(f) * 100, tri.provenance(40, H)))
