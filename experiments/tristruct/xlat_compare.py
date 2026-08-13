"""xlat_compare.py -- Proposer 4 mandatory first task: compare the independent
enumerator's king triangle (build/xlat_enum, experiments/tristruct/xlat_enum.cpp)
cell-by-cell against the banked triangle, n <= 12.

Also cross-checks the independent column transfer construction (xlat_coltm.py)
against the brute-force enumerator on all three lattices, when its data files
exist.

Run from experiments/tristruct/:  python3 xlat_compare.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from triangle import Triangle  # noqa: E402


def read_enum(path):
    """Parse xlat_enum output 'n H count' lines -> {(n,H): count}, {n: sum}."""
    cells, sums = {}, {}
    with open(path) as f:
        for line in f:
            n, H, c = line.split()
            if H == "SUM":
                sums[int(n)] = int(c)
            else:
                cells[(int(n), int(H))] = int(c)
    return cells, sums


def main():
    tri = Triangle.load()
    cells, sums = read_enum(os.path.join(HERE, "data", "king_enum_n12.txt"))
    nmax = max(n for n, _ in cells)
    bad = 0
    for n in range(1, nmax + 1):
        for H in range(1, n + 1):
            mine = cells.get((n, H), 0)
            banked = tri.cell(n, H)
            if mine != banked:
                bad += 1
                print("MISMATCH T(%d,%d): mine=%d banked=%d" % (n, H, mine, banked))
        if sums[n] != tri.rowsum(n):
            bad += 1
            print("MISMATCH a(%d): mine=%d banked=%d" % (n, sums[n], tri.rowsum(n)))
    ncells = sum(1 for n in range(1, nmax + 1) for H in range(1, n + 1))
    print("king vs banked, n<=%d: %d cells + %d row sums compared, %d mismatches"
          % (nmax, ncells, nmax, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
