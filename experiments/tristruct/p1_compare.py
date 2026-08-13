"""p1_compare.py -- compare Proposer 1's independent enumerator output against
the banked triangle, cell by cell.

Usage: python3 p1_compare.py <enum_output_file> [nmax]
The enum file is p1_enum's stdout ("n H T" lines plus "n SUM a(n)" lines).
"""
import sys
from triangle import Triangle


def main():
    path = sys.argv[1]
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    tri = Triangle.load()
    mine = {}
    sums = {}
    for line in open(path):
        parts = line.split()
        if parts[1] == "SUM":
            sums[int(parts[0])] = int(parts[2])
        else:
            mine[(int(parts[0]), int(parts[1]))] = int(parts[2])
    bad = 0
    checked = 0
    for n in range(1, nmax + 1):
        for H in range(1, n + 1):
            b = tri.cell(n, H)
            m = mine.get((n, H), 0)
            checked += 1
            if b != m:
                bad += 1
                print("MISMATCH T(%d,%d): mine=%d banked=%d" % (n, H, m, b))
        if sums.get(n) != tri.rowsum(n):
            bad += 1
            print("MISMATCH a(%d): mine=%s banked=%d" % (n, sums.get(n), tri.rowsum(n)))
    print("checked %d cells + %d row sums, %d mismatches" % (checked, nmax, bad))


if __name__ == "__main__":
    main()
