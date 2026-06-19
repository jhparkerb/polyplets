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

# === Claims added in the elevated paper (Sections 3, 7, 8) ===

# Companions: extended free / one-sided (n=18,19) vs the symmetric-enumerator output
fo_path = os.path.join(ROOT, "results", "free_onesided_polyplets.txt")
if os.path.exists(fo_path):
    FO = {}
    for line in open(fo_path):
        p = line.split()
        if len(p) >= 3 and p[0].isdigit():
            FO[int(p[0])] = (int(p[1]), int(p[2]))
    chk("Free(18)==2808898025438",       FO.get(18,(0,0))[0]==2808898025438)
    chk("Free(19)==18951156321090",      FO.get(19,(0,0))[0]==18951156321090)
    chk("OneSided(18)==5617792259411",   FO.get(18,(0,0))[1]==5617792259411)
    chk("OneSided(19)==37902303297525",  FO.get(19,(0,0))[1]==37902303297525)

# Bilateral (A030234) and asymmetric (A030235) at n=19, from the subcounts
bil19 = F(Hsym + D, 2)
chk("bilateral(19)=(H+D)/2=9344655", bil19.denominator==1 and int(bil19)==9344655)
chk("asymmetric(19)=Free-bilateral=18951146976435", int(free)-int(bil19)==18951146976435)

# Maximum hole area M(n): values, centered-square formula, isoperimetric bound
M = [0,0,0,1,1,2,3,5,6]   # n=1..9, brute force (sampling/amax_brute.py)
chk("M(4)=1=2*1^2-2*1+1", M[3]==1==2*1-2*1+1)
chk("M(8)=5=2*2^2-2*2+1", M[7]==5==2*4-2*2+1)
chk("M(n)<=floor(n^2/8), n=1..9", all(M[n-1] <= n*n//8 for n in range(1,10)))

# GF transcriptions: paper coefficients must match the recovered data files
def gf_block(path, header):
    P = Q = None; want = False
    for line in open(os.path.join(ROOT, path)):
        if line.startswith(header): want = True; continue
        if want and line.startswith("P: "): P = eval(line[3:])
        if want and line.startswith("Q: "): Q = eval(line[3:]); break
    return P, Q
P3, Q3 = gf_block("results/fixed_height_gfs.txt", "H=3 ")
chk("G_3 numerator transcription",   P3==[0,0,0,9,-8,-2,4,1])
chk("G_3 denominator transcription", Q3==[1,-7,15,-9,-3,5,-1,-1])
P31, Q31 = gf_block("results/hole_gfs.txt", "H=3 k=1 ")
chk("G_{3,1} numerator transcription",   P31==[0,0,0,0,1,2,0,-2,-1])
chk("G_{3,1} denominator transcription", Q31==[1,-8,20,-14,-8,18,3,-16,6,6,-3,-2,1])

# Fixed-height GF orders, and hole-GF order-law slopes c_H = ord(H,2)-ord(H,1)
def order_of(path, header):
    for line in open(os.path.join(ROOT, path)):
        if line.startswith(header) and "order=" in line:
            return int(line.split("order=")[1].split()[0])
orders = [order_of("results/fixed_height_gfs.txt", f"H={H} ") for H in range(1,10)]
chk("fixed-height orders H=1..9 = 1,3,7,15,42,106,278,711,1897",
    orders==[1,3,7,15,42,106,278,711,1897], str(orders))
for H,c in [(3,6),(4,20),(5,68),(6,185)]:
    s = order_of("results/hole_gfs.txt", f"H={H} k=2 ") - \
        order_of("results/hole_gfs.txt", f"H={H} k=1 ")
    chk(f"c_{H}={c} (hole-GF order-law slope)", s==c, f"slope {s}")

# Hole triangle rows in Table tab:holes and the A_0/A_1 caption sequences
if os.path.exists(G2):
    paper_rows = {4:{0:109,1:1}, 5:{0:622,1:16}, 6:{0:3664,1:166,2:2},
                  7:{0:22094,1:1456,2:42}, 8:{0:135609,1:11788,2:538,3:6}}
    for n,row in paper_rows.items():
        chk(f"hole-triangle row n={n}", all(h4[n].get(k,0)==v for k,v in row.items()))
    chk("A_0 caption seq n=1..8",
        [h4[n].get(0,0) for n in range(1,9)]==[1,4,20,109,622,3664,22094,135609])
    chk("A_1 caption seq n=4..8",
        [h4[n].get(1,0) for n in range(4,9)]==[1,16,166,1456,11788])

# Companions table: bilaterally-symmetric (A030234) and asymmetric (A030235) at
# n=18,19, regenerated from the mirror sub-counts via symcount_fast
SC = os.path.join(ROOT, "build", "symcount_fast")
if os.path.exists(SC):
    def sc(t):
        out = subprocess.run([SC, t, "19"], capture_output=True, text=True).stdout
        d = {}
        for line in out.split("\n"):
            p = line.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit(): d[int(p[0])] = int(p[1])
        return d
    Hm, Dm = sc("hmirror"), sc("dmirror")
    freeN = {18: 2808898025438, 19: 18951156321090}
    for n, bil, asym in [(18, 3791465, 2808894233973), (19, 9344655, 18951146976435)]:
        b = (Hm.get(n,0) + Dm.get(n,0)) // 2
        chk(f"bilateral({n})=(hmirror+dmirror)/2={bil}", b == bil, f"got {b}")
        chk(f"asymmetric({n})=Free-bilateral={asym}", freeN[n] - b == asym)
else:
    print("  (skipping symmetric n=18,19 checks: build/symcount_fast not found)")

print(f"\n{ok} checks passed, {bad} failed.")
raise SystemExit(1 if bad else 0)
