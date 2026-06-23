#!/usr/bin/env python3
# Combine g2 --per-box --split worker outputs ("n w h count") into the square-bounding-box
# polyplet count (the w==h diagonal) and verify the full (w,h) marginal equals A006770(n).
# Named on-disk (not a heredoc) so the combine is traceable and re-runnable.
# USAGE: bbox_combine.py DIR N
import glob
import sys

d, N = sys.argv[1], int(sys.argv[2])
A006770 = {1: 1, 2: 4, 3: 20, 4: 110, 5: 638, 6: 3832, 7: 23592, 8: 147941,
           9: 940982, 10: 6053180, 11: 39299408, 12: 257105146, 13: 1692931066,
           14: 11208974860, 15: 74570549714, 16: 498174818986, 17: 3340366308393,
           18: 22471158811164}
sq = {}
tot = {}
for path in glob.glob(f"{d}/w*.txt"):
    for ln in open(path):
        p = ln.split()
        if len(p) != 4:
            continue
        n, w, h, c = int(p[0]), int(p[1]), int(p[2]), int(p[3])
        tot[n] = tot.get(n, 0) + c
        if w == h:
            sq[n] = sq.get(n, 0) + c

print("n  squareBBox       marginal        A006770          ok")
allok = True
for n in sorted(tot):
    ref = A006770.get(n)
    ok = "OK" if (ref is None or tot[n] == ref) else f"MISMATCH({ref})"
    if ref is not None and tot[n] != ref:
        allok = False
    print(f"{n:2d} {sq.get(n, 0):>14d} {tot[n]:>16d} {ref if ref else 0:>16d}  {ok}")
print(f"marginal fully matches A006770 through n={max(tot)}: {allok}")
print("SQ:", ",".join(str(sq[n]) for n in sorted(sq)))
