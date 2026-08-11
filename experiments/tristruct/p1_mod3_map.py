"""p1_mod3_map.py -- Proposer 1 (proof-first): mod-3 map of the triangle from
SELF-ENUMERATED cells only (build/p1_enum output), with every cell whose mod-3
residue is already determined by prior work masked out, so that only the OPEN
residues show:

  known (masked):
    - activation zeros: n < floor(3H/2)            [T4, proved]
    - activation boundary n = floor(3H/2)          [T2/T3 spine values]
    - in-regime (n >= 2k+1, k=n-H) with e=n-1-3k>=1: T == 0 mod 3
    - spine n = 3k+1 (e=0): digit-product value
    - deficit-2 last nonzero: T(3m+2,2m+1) == 2 mod 3
  open (shown):
    - sleeve: in-regime-adjacent band 3k+1 > n >= 2k+1 is covered above
      EXCEPT nothing -- in-regime e>=1 and e=0 covers n>=2k+1 wholly, and
      deficit cells n<3k+1 with n>=2k+1 have T = P_k(n)/3^d, d=3k+1-n>=1:
      residue NOT determined by the spine unless zero-region. Wait: for
      n >= 2k+1 and n < 3k+1 the exponent e = n-1-3k < 0. These are the
      SLEEVE cells (deficit d = 3k+1-n >= 1... n-1-3k <= -2 => d >= 2? no:
      e<0 <=> n <= 3k; d = 3k+1-n >= 1). known.py returns None there except
      the deficit-2 family.
    - below onset: n <= 2k, i.e. n >= 2H (k >= H).

Usage: python3 p1_mod3_map.py data/p1_king_n13.txt [mod]
Prints a per-row map, '.'=known-region cell (also verified against the known
prediction where one exists), digits = open residues, '!'=known-region cell
whose enumerated residue CONTRADICTS the known prediction (would be a bug).
"""
import sys

def load(path):
    T = {}
    for line in open(path):
        p = line.split()
        if len(p) == 3 and p[1] != "SUM":
            T[(int(p[0]), int(p[1]))] = int(p[2])
    return T

def known_mod3(n, H):
    """Residue mod 3 if prior work determines it, else None. Mirrors known.py
    TernarySpineMod3 (reimplemented here so this script reads no banked data)."""
    k = n - H
    if k < 0:
        return 0  # structural zero
    e = n - 1 - 3 * k
    if n < (3 * H) // 2:
        return 0
    if n == (3 * H) // 2:
        return None if H % 2 == 1 else 1  # odd: spine digit product (skip; treat as known-but-unchecked)
    if e >= 1:
        return 0
    if n % 3 == 2 and n >= 5 and H == 2 * ((n - 2) // 3) + 1:
        return 2
    return None

def main():
    path = sys.argv[1]
    m = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    T = load(path)
    nmax = max(n for n, _ in T)
    print("map mod %d  ('.'=known, '!'=CONTRADICTION, digit=open residue)" % m)
    print("     H: " + "".join("%2d" % H for H in range(1, nmax + 1)))
    for n in range(1, nmax + 1):
        row = []
        for H in range(1, n + 1):
            v = T[(n, H)] % m
            km = known_mod3(n, H)
            if m == 3 and km is not None:
                row.append(" ." if v == km else " !")
            elif m == 3 and n == (3 * H) // 2 and H % 2 == 1:
                row.append(" .")  # odd spine boundary: known via digit product
            else:
                row.append("%2d" % v)
        print("n=%3d: %s" % (n, "".join(row)))
    # column reading of the open cells, below onset only (n >= 2H)
    print()
    print("below-onset columns (n >= 2H), residues mod %d:" % m)
    for H in range(1, nmax // 2 + 1):
        seq = [(n, T[(n, H)] % m) for n in range(2 * H, nmax + 1)]
        print("H=%2d: n=%2d..%2d: %s" % (H, 2 * H, nmax,
              " ".join(str(v) for _, v in seq)))
    # sleeve cells (2k+1 <= n <= 3k, i.e. in-regime with negative exponent)
    print()
    print("sleeve cells (2k+1 <= n <= 3k), residues mod %d by diagonal k:" % m)
    for k in range(1, nmax):
        cells = [(n, T[(n, n - k)] % m) for n in range(2 * k + 1, min(3 * k, nmax) + 1)
                 if (n, n - k) in T and n - k >= 1]
        cells = [(n, v) for n, v in cells if known_mod3(n, n - k) is None
                 and not (n == (3 * (n - k)) // 2)]
        if cells:
            print("k=%2d: " % k + " ".join("n=%d:%d" % (n, v) for n, v in cells))

if __name__ == "__main__":
    main()
