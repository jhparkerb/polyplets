"""Cross-lattice tests of the OTHER proposers' filed relations (Proposer 4,
falsification service, docs/triangle-structure-team-brief.md).

P2 (results/triangle-hunt-klein-parity.md): T(n,H) even for n odd, H even
   — proved on the king lattice via the box-midline reflection involution.
   The same involution is a symmetry of the square lattice, and of the
   triangular lattice when H is even (the midline flip preserves the
   up/down parity rule there iff H is even) — so the theorem should
   TRANSFER.  Tested here on: every enumerator cell (all H; square n <= 14,
   tri n <= 16) and every TM column cell (H in {2,4}, n <= 140).

P3 (results/triangle-hunt-atoms-ab-initio.md): king strip counts C_H have
   one-atom minimal annihilators with degrees 1,2,4,9,29,68, and the
   exact-height column order is the sum of three consecutive atom degrees
   (3=2+1, 7=4+2+1, 15=9+4+2).  Cross-lattice analogue tested here:
   compute C_H = sum_{h<=H} (H-h+1) T(n,h) for square/tri, measure the
   minimal C-finite order d_H of each C_H, and check the additivity
   ord T(.,H) = d_H + d_{H-1} + d_{H-2}.

Usage: python3 xlat_proposer_checks.py   (from experiments/tristruct/)
"""

import os
from xlat_verdicts import load_col, min_cfinite_order

HERE = os.path.dirname(os.path.abspath(__file__))


def load_all(path):
    cells = {}
    with open(path) as f:
        for line in f:
            p = line.split()
            if len(p) == 3 and p[1] != 'SUM':
                cells[(int(p[0]), int(p[1]))] = int(p[2])
    return cells


def p2_parity():
    print("== P2 parity theorem analogue: T(n,H) even for n odd, H even ==")
    srcs = [
        ('square enum (all H, n<=14)', 'data/square_enum_n14.txt', None),
        ('tri    enum (all H, n<=16)', 'data/tri_enum_n16.txt', None),
        ('square TM   (H=2,4, n<=140)', 'data/square_col_tm_n140.txt',
         (2, 4)),
        ('tri    TM   (H=2,4, n<=140)', 'data/tri_col_tm_n140.txt', (2, 4)),
    ]
    for name, path, hs in srcs:
        cells = load_all(os.path.join(HERE, path))
        region = [(n, H) for (n, H) in cells
                  if n % 2 == 1 and H % 2 == 0 and (hs is None or H in hs)]
        bad = [(n, H) for (n, H) in region if cells[(n, H)] % 2 != 0]
        print(f"  {name}: {len(region)} cells in region, "
              f"{len(bad)} odd-valued {'<-- VIOLATION' if bad else '(all even)'}")
        for n, H in sorted(bad)[:10]:
            print(f"    VIOLATION n={n} H={H} T={cells[(n, H)]}")


def p3_atoms():
    print()
    print("== P3 atom-ladder analogue: ord C_H additivity ==")
    for lat in ('square', 'tri'):
        path = os.path.join(HERE, f'data/{lat}_col_tm_n140.txt')
        cells = load_all(path)
        nmax = max(n for (n, _) in cells)
        d = {}
        for H in range(1, 6):
            lo = min(n for (n, h) in cells if h == H)
            # C_H(n) = sum_{h<=H} (H-h+1) T(n,h); T(n,h)=0 below onset
            vals = []
            for n in range(1, nmax + 1):
                vals.append(sum((H - h + 1) * cells.get((n, h), 0)
                                for h in range(1, H + 1)))
            r = min_cfinite_order(vals, max_order=45)
            d[H] = r[0] if r else None
        tord = {}
        for H in (3, 4):
            lo = min(n for (n, h) in cells if h == H)
            vals = [cells.get((n, H), 0) for n in range(lo, nmax + 1)]
            r = min_cfinite_order(vals, max_order=45)
            tord[H] = r[0] if r else None
        print(f"  {lat}: ord C_H for H=1..5: "
              f"{[d[H] for H in range(1, 6)]}")
        for H in (3, 4):
            if None in (tord[H], d.get(H), d.get(H - 1), d.get(H - 2)):
                print(f"    H={H}: undetermined (some order > 45)")
                continue
            s = d[H] + d[H - 1] + d[H - 2]
            ok = 'MATCHES' if s == tord[H] else 'FAILS'
            print(f"    H={H}: ord T = {tord[H]} vs "
                  f"d_{H}+d_{H-1}+d_{H-2} = {d[H]}+{d[H-1]}+{d[H-2]} = {s}"
                  f"  -> {ok}")


if __name__ == '__main__':
    p2_parity()
    p3_atoms()
