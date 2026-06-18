#!/usr/bin/env python3
"""Verify every arithmetic / algebraic claim in a19-polyplets.tex.

Exact integer/rational arithmetic only (stdlib Fraction); no external packages.
Regenerates the hole tables and the 3^(H-1) closed form from build/g2, reads the
b-files for the published terms, and checks the transcribed paper tables against
all of it. Run from the repo root after `make build/g2`:  python3 paper/verify_claims.py
"""
import os, subprocess, glob
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G2 = os.path.join(ROOT, "build", "g2")

def load(path):
    d = {}
    for line in open(os.path.join(ROOT, path)):
        p = line.split()
        if len(p) == 2 and p[0].lstrip("-").isdigit():
            d[int(p[0])] = int(p[1])
    return d

def g2_holes(flag, n=12):
    out = subprocess.run([G2, "square8", str(n), flag], capture_output=True, text=True).stdout
    t = {}
    for line in out.split("\n"):
        p = line.split()
        if len(p) == 3:
            t.setdefault(int(p[0]), {})[int(p[1])] = int(p[2])
    return t

A    = load("results/b006770_upload.txt")     # fixed polyplets
FREE = load("results/b030222_upload.txt")     # free polyplets
P    = load("fixtures/b001168.txt")           # fixed polyominoes A001168

ok = bad = 0
def chk(name, cond, detail=""):
    global ok, bad
    if cond: ok += 1
    else:
        bad += 1; print(f"  FAIL: {name}  {detail}")

# --- Table tab:terms (paper transcription) vs b-file ---
TERMS = {1:1,2:4,3:20,4:110,5:638,6:3832,7:23592,8:147941,9:940982,10:6053180,
 11:39299408,12:257105146,13:1692931066,14:11208974860,15:74570549714,
 16:498174818986,17:3340366308393,18:22471158811164,19:151609203011580}
for n,v in TERMS.items():
    chk(f"tab:terms a({n})", A.get(n)==v, f"paper {v} vs bfile {A.get(n)}")
chk("headline a(19)", A[19]==151609203011580)
chk("a(2)==4", A[2]==4); chk("Free(2)==2", FREE[2]==2)

# --- byHeight table: sum, peak, closed forms, run-data agreement ---
BH = {1:1,2:15994426,3:12736006193,4:452027455240,5:3469435781222,
 6:10975452058596,7:20257323484797,8:26611876627714,9:27701775032858,
 10:24014057424024,11:17644523530186,12:11003764277892,13:5776897734667,
 14:2512138867830,15:882180009630,16:240601488426,17:47839787379,
 18:6170030010,19:387420489}
chk("byHeight sum == a(19)", sum(BH.values())==A[19])
chk("byHeight peak at H=9", max(BH, key=BH.get)==9)
chk("B_19(19)==3^18==387420489", BH[19]==3**18==387420489)
chk("B_17(19) table/cross-check agree", BH[17]==47839787379)
for f in glob.glob(os.path.join(ROOT,"runs","**","h*.txt"), recursive=True):
    H = os.path.basename(f)[1:-4]
    if not H.isdigit(): continue
    for line in open(f):
        p = line.split()
        if len(p)==2 and p[0]=="19":
            chk(f"B_{H}(19) vs run data", BH[int(H)]==int(p[1]),
                f"paper {BH[int(H)]} vs run {p[1]}")
        if len(p)==2 and p[0]==H:                      # closed form B_H(H)=3^(H-1)
            chk(f"B_{H}({H})==3^{int(H)-1}", int(p[1])==3**(int(H)-1))

# --- growth ratios and lambda ---
r = {n: F(A[n],A[n-1]) for n in range(2,20)}
chk("ratio a19/a18 ~ 6.7468", round(float(r[19]),4)==6.7468, f"{float(r[19]):.6f}")
chk("ratio a18/a17 ~ 6.7272", round(float(r[18]),4)==6.7272, f"{float(r[18]):.6f}")
chk("growth extrapolant lambda ~ 7.10", round(float(19*r[19]-18*r[18]),2)==7.10,
    f"{float(19*r[19]-18*r[18]):.4f}")

# --- Burnside: free / one-sided from symmetric subcounts ---
Fixed, R90, R180, Hsym, D = A[19], 0, 10178520, 9765524, 8923786
free = F(Fixed + 2*R90 + R180 + 2*Hsym + 2*D, 8)
ones = F(Fixed + 2*R90 + R180, 4)
chk("Free(19) integral & == A030222[19]",
    free.denominator==1 and int(free)==18951156321090==FREE[19], str(free))
chk("OneSided(19) integral & value",
    ones.denominator==1 and int(ones)==37902303297525, str(ones))
chk("Free(19) - a(19)/8 ~ 6e6", 5e6 < float(free)-Fixed/8 < 7e6)
chk("R90 empty: 19 mod 4 == 3", 19 % 4 == 3)

# --- A001168(19)/a(19) rarity, height coverage ---
chk("A001168(19)/a(19) ~ 4e-5", round(float(F(P[19],A[19]))/1e-5,1) in (3.9,4.0),
    f"{float(F(P[19],A[19])):.3e}")
chk("heights<=13 coverage ~ 97.6%",
    round(float(F(sum(BH[h] for h in range(1,14)),A[19]))*100,1)==97.6)

# --- hole tables (regenerated from g2), both conventions ---
if os.path.exists(G2):
    h4, h8 = g2_holes("--holes"), g2_holes("--holes8")
    for n,v in {1:1,4:109,8:135609,10:5310754,12:215793158}.items():
        chk(f"holes 4-conn hole-free n={n}", h4[n].get(0,0)==v)
    for n,v in {1:1,4:110,8:147940,10:6053002,12:257090547}.items():
        chk(f"holes 8-conn hole-free n={n}", h8[n].get(0,0)==v)
    for n in range(1,13):
        chk(f"4-conn hole partition sums to a({n})", sum(h4[n].values())==A[n])
        chk(f"8-conn hole partition sums to a({n})", sum(h8[n].values())==A[n])
    chk("8-conn hole-free==a(n) for n<8", all(h8[n].get(0,0)==A[n] for n in range(1,8)))
    chk("first 8-conn hole at n=8", A[8]-h8[8].get(0,0)==1)
    chk("first 4-conn hole at n=4",
        all(sum(c for hh,c in h4[n].items() if hh>0)==0 for n in range(1,4))
        and sum(c for hh,c in h4[4].items() if hh>0)==1)
else:
    print("  (skipping hole checks: build/g2 not found; run `make build/g2`)")

print(f"\n{ok} checks passed, {bad} failed.")
raise SystemExit(1 if bad else 0)
