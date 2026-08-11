"""p3_compare.py -- compare Proposer 3's independent enumerator output
(p3_enum_out.txt, from p3_enum.cc) against the banked triangle for n <= 12.

Run from experiments/tristruct/:  python3 p3_compare.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from triangle import Triangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    tri = Triangle.load()
    mine = {}
    with open(os.path.join(HERE, "p3_enum_out.txt")) as f:
        for line in f:
            n, h, v = line.split()
            mine[(int(n), int(h))] = int(v)
    nmax = max(n for n, _ in mine)
    bad = 0
    for n in range(1, nmax + 1):
        for h in range(1, n + 1):
            banked = tri.cell(n, h)
            got = mine.get((n, h), 0)
            if banked != got:
                bad += 1
                print("MISMATCH n=%d H=%d banked=%d mine=%d" % (n, h, banked, got))
    # also row sums vs a(n)
    for n in range(1, nmax + 1):
        s = sum(v for (nn, _), v in mine.items() if nn == n)
        if s != tri.rowsum(n):
            bad += 1
            print("ROWSUM MISMATCH n=%d banked=%d mine=%d" % (n, tri.rowsum(n), s))
    if bad == 0:
        cells = sum(1 for n in range(1, nmax + 1) for h in range(1, n + 1))
        print("OK: all %d cells and %d row sums agree, n <= %d" % (cells, nmax, nmax))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
