#!/usr/bin/env python3
"""verify_redelmeier.py -- Job 3 verdict for docs/a25-verification-plan.md.

Aggregates the independent Redelmeier enumerator's `--per-box` output
("n w h count") over width w -> T(n,H), and compares to the transfer-matrix
swept stripe (results/ns_a25/swept_rows.txt). Any mismatch on a swept height
(H=3..16) is a stepColumnSquare8 logic bug.

Usage: verify_redelmeier.py <g2_per_box.txt> <swept_rows.txt>
Exit 0 = all swept cells match (PASS), 1 = mismatch (FAIL).
"""

import sys

def load_perbox(path):
    """g2 --per-box lines 'n w h count' -> T[(n,h)] = sum over w."""
    T = {}
    for line in open(path):
        p = line.split()
        if len(p) == 4 and all(x.lstrip("-").isdigit() for x in p):
            n, w, h, c = map(int, p)
            T[(n, h)] = T.get((n, h), 0) + c
    return T

def load_swept(path):
    """swept_rows.txt (===H<h>=== blocks of 'n value') -> S[(n,h)]."""
    S, h = {}, None
    for line in open(path):
        line = line.strip()
        if line.startswith("===H"):
            h = int(line[4:].rstrip("="))
        elif line and h is not None:
            p = line.split()
            if len(p) == 2 and all(x.lstrip("-").isdigit() for x in p):
                S[(int(p[0]), h)] = int(p[1])
    return S

def main():
    red = load_perbox(sys.argv[1])
    swept = load_swept(sys.argv[2])
    maxn_red = max(n for n, _ in red) if red else 0
    print(f"Redelmeier reaches n={maxn_red}; comparing swept heights H=3..16\n")
    fails, checked = [], 0
    for (n, h), sv in sorted(swept.items()):
        if not (3 <= h <= 16) or sv == 0:
            continue
        if n > maxn_red:
            continue                      # beyond Redelmeier's reach this run
        checked += 1
        rv = red.get((n, h), 0)
        if rv != sv:
            fails.append((n, h, sv, rv))
    if fails:
        print(f"FAIL: {len(fails)}/{checked} cells disagree:")
        for n, h, sv, rv in fails[:20]:
            print(f"  T({n},{h}): swept={sv:,}  redelmeier={rv:,}")
        sys.exit(1)
    print(f"PASS: all {checked} swept cells (H=3..16, n<={maxn_red}) match Redelmeier.")
    sys.exit(0)

if __name__ == "__main__":
    main()
