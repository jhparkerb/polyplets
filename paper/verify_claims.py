#!/usr/bin/env python3
"""Verify every arithmetic / algebraic claim in polyplets-report.tex.

Exact integer/rational arithmetic only (stdlib Fraction); no external packages.
Regenerates the hole tables and the 3^(H-1) closed form from build/g2, reads the
b-files for the published terms, and checks the transcribed paper tables against
all of it. Run from the repo root after `make build/g2`:  python3 paper/verify_claims.py

Exit 0 iff every check passed AND every optional group ran.  A group whose
input is missing prints "COVERAGE DEGRADED", is counted in the final line, and
makes the run exit nonzero; set ALLOW_PARTIAL=1 to accept a degraded run.
SHOW_COVERAGE=1 prints each group's contributed check count (used to refresh
the COVERAGE table below after adding checks).
"""
import ast, os, re, subprocess, glob
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

# ---- coverage accounting (AUDIT-2026-07-30 P6) -------------------------------
# Several blocks skip-and-continue when an input is missing.  They used to
# print one quiet parenthetical and the tool still ended with
# "N checks passed, 0 failed" and exit 0 -- in a tree without build/g2,
# build/symcount_fast and runs/, 220 of 448 checks vanished with no signal in
# the exit status.  Now every skip is loud, counted, and fatal unless
# ALLOW_PARTIAL=1 is set in the environment.
ALLOW_PARTIAL = os.environ.get("ALLOW_PARTIAL") == "1"
SHOW_COVERAGE = os.environ.get("SHOW_COVERAGE") == "1"
skipped = []

def skip(group, ncheck, reason):
    skipped.append((group, ncheck))
    print(f"  COVERAGE DEGRADED: skipped {group} ({ncheck} checks) -- {reason}")

def covered(group, expected, start):
    """A present group must contribute the checks it is supposed to."""
    global bad
    got = ok + bad - start
    if SHOW_COVERAGE:
        print(f"  coverage {group}: {got} checks")
    if got != expected:
        bad += 1
        print(f"  FAIL: coverage {group}: {got} checks contributed, "
              f"expected {expected}")

# ---- tracked fallback for the gitignored runs/sym3x columns ------------------
# runs/ is in .gitignore, so the symmetric fixed-point columns (weeks of
# compute) exist on one machine only.  results/sym_counts.txt is the tracked
# extraction; see scripts/bank_sym_counts.py.
def load_sym_bank():
    path = os.path.join(ROOT, "results", "sym_counts.txt")
    if not os.path.exists(path):
        return None, None
    cols, strips = {}, {}
    for line in open(path):
        p = line.split()
        if len(p) == 3 and p[1].isdigit():
            cols.setdefault(p[0], {})[int(p[1])] = int(p[2])
        elif len(p) == 4 and p[0] == "dmirror_strip":
            strips[(int(p[1]), int(p[2]))] = int(p[3])
    return (cols or None), (strips or None)

SYMCOLS, SYMSTRIPS = load_sym_bank()

# Checks each optional group contributes in a complete tree.  Asserted when the
# group runs and quoted when it is skipped, so the denominator is never a
# mystery.  Re-harvest with SHOW_COVERAGE=1 after adding checks to a group.
COVERAGE = {
    "g2_holes": 37,
    "g2_holetriangle": 7,
    "free_onesided": 4,
    "maxhole": 1,
    "holes_n18": 5,
    "symcount_1819": 4,
    "sym_companions": 132,
    "dmirror_strips": 40,
    "spine_mod3": 1,
    "byheight_h19": 32,
}   # 263 of the 448 checks live in an optional group

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
# B_H(19) and the B_H(H)=3^(H-1) closed form, per height.  Preferred source is
# the a(19) TMA run dirs under runs/ -- a DIFFERENT engine, so those two checks
# per height are cross-engine.  runs/ is gitignored, so fall back to the tracked
# triangle (same engine as the bank, weaker but not nothing); either way the
# check count is fixed and accounted for (AUDIT-2026-07-30 P6: this glob used
# to contribute a silently variable 0..32 checks).
_cov = ok + bad
_h19 = {}   # H -> (T(19,H), T(H,H))
for f in glob.glob(os.path.join(ROOT,"runs","**","h*.txt"), recursive=True):
    H = os.path.basename(f)[1:-4]
    if not H.isdigit(): continue
    v19 = vHH = None
    for line in open(f):
        p = line.split()
        if len(p)==2 and p[0]=="19": v19 = int(p[1])
        if len(p)==2 and p[0]==H:    vHH = int(p[1])
    if v19 is not None and vHH is not None:
        _h19[int(H)] = (v19, vHH)
_h19src = "runs/**/h*.txt (a(19) TMA run dirs, independent engine)"
if not _h19:
    _tri19 = {}
    for line in open(os.path.join(ROOT, "results", "triangle.txt")):
        p = line.split()
        if len(p) == 3 and p[0].isdigit():
            _tri19[(int(p[0]), int(p[1]))] = int(p[2])
    _h19 = {H: (_tri19[(19, H)], _tri19[(H, H)]) for H in range(1, 17)}
    _h19src = "results/triangle.txt (banked, same engine as the bank)"
print(f"  byHeight cross-check source: {_h19src}")
for H, (v19, vHH) in sorted(_h19.items()):
    chk(f"B_{H}(19) vs run data", BH[H]==v19, f"paper {BH[H]} vs run {v19}")
    chk(f"B_{H}({H})==3^{H-1}", vHH==3**(H-1))
covered("byHeight per-height cross-check", COVERAGE["byheight_h19"], _cov)

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
_cov = ok + bad
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
    covered("hole tables (build/g2)", COVERAGE["g2_holes"], _cov)
else:
    skip("hole tables (build/g2)", COVERAGE["g2_holes"],
         "build/g2 not found; run `make build/g2`")

# === Claims added in the elevated paper (Sections 3, 7, 8) ===

# Companions: extended free / one-sided (n=18,19) vs the symmetric-enumerator output
fo_path = os.path.join(ROOT, "results", "free_onesided_polyplets.txt")
_cov = ok + bad
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
    covered("free/one-sided n=18,19", COVERAGE["free_onesided"], _cov)
else:
    skip("free/one-sided n=18,19", COVERAGE["free_onesided"],
         "results/free_onesided_polyplets.txt absent")

# Bilateral (A030234) and asymmetric (A030235) at n=19, from the subcounts
bil19 = F(Hsym + D, 2)
chk("bilateral(19)=(H+D)/2=9344655", bil19.denominator==1 and int(bil19)==9344655)
chk("asymmetric(19)=Free-bilateral=18951146976435", int(free)-int(bil19)==18951146976435)

# Maximum hole area M(n): values to n=16 (results/maxhole.txt), diamond bound, isoperimetric
M = [0,0,0,1,1,2,3,5,6,8,10,13,15,18,21,25]   # n=1..16 (maxhole_split, 4-conn-bg primary)
chk("M(4)=1=2*1^2-2*1+1",   M[3]==1==2*1-2*1+1)
chk("M(8)=5=2*2^2-2*2+1",   M[7]==5==2*4-2*2+1)
chk("M(12)=13=2*3^2-2*3+1", M[11]==13==2*9-6+1)   # diamond tight at the n=12 4r-point
chk("M(16)=25=2*4^2-2*4+1", M[15]==25==2*16-8+1)  # diamond tight at the n=16 4r-point too
chk("M(n)<=floor(n^2/8), n=1..16", all(M[n-1] <= n*n//8 for n in range(1,17)))
# results/maxhole.txt (the maxhole_split output) must reproduce M(1..16)
mh = os.path.join(ROOT, "results", "maxhole.txt")
_cov = ok + bad
if os.path.exists(mh):
    mv = {int(l.split()[0]): int(l.split()[1]) for l in open(mh)
          if l.split() and l.split()[0].isdigit()}
    chk("maxhole.txt reproduces M(1..16)",
        [mv.get(n) for n in range(1,17)]==M, str([mv.get(n) for n in range(1,17)]))
    covered("maxhole M(1..16)", COVERAGE["maxhole"], _cov)
else:
    skip("maxhole M(1..16)", COVERAGE["maxhole"], "results/maxhole.txt absent")

# GF transcriptions: paper coefficients must match the recovered data files
def gf_block(path, header):
    P = Q = None; want = False
    for line in open(os.path.join(ROOT, path)):
        if line.startswith(header): want = True; continue
        if want and line.startswith("P: "): P = ast.literal_eval(line[3:])
        if want and line.startswith("Q: "): Q = ast.literal_eval(line[3:]); break
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
orders = [order_of("results/fixed_height_gfs.txt", f"H={H} ") for H in range(1,11)]
chk("fixed-height orders H=1..10 = 1,3,7,15,42,106,278,711,1897,5005",
    orders==[1,3,7,15,42,106,278,711,1897,5005], str(orders))
# lifetime-3: atom degrees deg N_H = deg Q_H - deg N_{H-1} - deg N_{H-2} reproduce the
# proof's verified values (paper, GF section "Denominator structure")
_N = [0, 0]
for _q in orders: _N.append(_q - _N[-1] - _N[-2])
chk("lifetime-3 atom degrees (H<=7) == 1,2,4,9,29,68,181",
    _N[2:9] == [1, 2, 4, 9, 29, 68, 181], str(_N[2:9]))

# Rigorous lower bound  a(n) >= sum_{H<=10} [x^n] G_H  (cf. paper/gf_bound.py): expand the
# recovered GFs as exact integer power series; check captured fraction + the a(25) bound.
def _gf_series(Pc, Qc, N):
    b = [0]*(N+1)
    for m in range(N+1):
        v = Pc[m] if m < len(Pc) else 0
        for j in range(1, min(m, len(Qc)-1)+1): v -= Qc[j]*b[m-j]
        b[m] = v
    return b
_gfs, _H, _P = {}, None, None
for line in open(os.path.join(ROOT, "results", "fixed_height_gfs.txt")):
    s = line.strip()
    if s.startswith("H="):   _H = int(s.split()[0].split("=")[1])
    elif s.startswith("P:"): _P = ast.literal_eval(s[2:].strip())
    elif s.startswith("Q:"): _gfs[_H] = (_P, ast.literal_eval(s[2:].strip()))
_ser = {H: _gf_series(Pc, Qc, 25) for H, (Pc, Qc) in _gfs.items()}
chk("GF-expanded B_H(19) == byHeight, H=1..10", all(_ser[H][19] == BH[H] for H in range(1, 11)))
chk("bound sanity: sum_{H<=9} @ n=25 == prior 4380493652795380053",
    sum(_ser[H][25] for H in range(1, 10)) == 4380493652795380053)
chk("a(25) lower bound (H<=10) == 6657105903966723073",
    sum(_ser[H][25] for H in range(1, 11)) == 6657105903966723073)
chk("H<=10 captures 74.9% of a(19)",
    round(F(100*sum(_ser[H][19] for H in range(1, 11)), A[19]), 1) == F(749, 10))

for H,c in [(3,6),(4,20),(5,68),(6,185),(7,537)]:
    s = order_of("results/hole_gfs.txt", f"H={H} k=2 ") - \
        order_of("results/hole_gfs.txt", f"H={H} k=1 ")
    chk(f"c_{H}={c} (hole-GF order-law slope)", s==c, f"slope {s}")
# H=7 order law c_7(k+1): rows k=0,1,2 must be exactly 537,1074,1611
chk("H=7 hole-GF orders == 537,1074,1611 = 537*(k+1)",
    [order_of("results/hole_gfs.txt", f"H=7 k={k} ") for k in (0,1,2)]==[537,1074,1611])
# H=8 k=0 recovered (order 1499); provisional c_8=1499 (single row, k=1,2 pending)
chk("H=8 k=0 hole-GF order==1499", order_of("results/hole_gfs.txt", "H=8 k=0 ")==1499)

# Hole triangle rows in Table tab:holes and the A_0/A_1 caption sequences
_cov = ok + bad
if os.path.exists(G2):
    paper_rows = {4:{0:109,1:1}, 5:{0:622,1:16}, 6:{0:3664,1:166,2:2},
                  7:{0:22094,1:1456,2:42}, 8:{0:135609,1:11788,2:538,3:6}}
    for n,row in paper_rows.items():
        chk(f"hole-triangle row n={n}", all(h4[n].get(k,0)==v for k,v in row.items()))
    chk("A_0 caption seq n=1..9",
        [h4[n].get(0,0) for n in range(1,10)]==[1,4,20,109,622,3664,22094,135609,843941])
    chk("A_1 caption seq n=4..9",
        [h4[n].get(1,0) for n in range(4,10)]==[1,16,166,1456,11788,91300])
    covered("hole triangle rows (build/g2)", COVERAGE["g2_holetriangle"], _cov)
else:
    skip("hole triangle rows (build/g2)", COVERAGE["g2_holetriangle"],
         "build/g2 not found; run `make build/g2`")

# Hole triangle extended to n=18 (transfer matrix; the flood oracle caps at n=14) and
# its cross-ISA confirmation: dalby clang/ARM == ayr gcc/x86, byte-identical.
hn18 = os.path.join(ROOT, "results", "holes_n18.txt")
_cov = ok + bad
if os.path.exists(hn18):
    T18 = {}
    for line in open(hn18):
        p = line.split()
        if len(p) == 3 and p[0].isdigit():
            T18.setdefault(int(p[0]), {})[int(p[1])] = int(p[2])
    chk("A_0(18)==16503616943998", T18[18].get(0) == 16503616943998)
    chk("A_1(18)==4970078092354",  T18[18].get(1) == 4970078092354)
    chk("max holes at n=18 is 10", max(T18[18]) == 10)
    chk("hole rows sum to a(n), n=1..18", all(sum(T18[n].values()) == A[n] for n in range(1, 19)))
    dn18 = os.path.join(ROOT, "results", "holes_n18.dalby.txt")
    if os.path.exists(dn18):
        def _norm(path):
            return sorted((int(p[0]), int(p[1]), int(p[2])) for p in
                          (l.split() for l in open(path)) if len(p) == 3 and p[0].isdigit())
        chk("holes n<=18 cross-ISA byte-identical (dalby clang/ARM == ayr gcc/x86)",
            _norm(hn18) == _norm(dn18))
    covered("hole triangle n<=18", COVERAGE["holes_n18"], _cov)
else:
    skip("hole triangle n<=18", COVERAGE["holes_n18"],
         "results/holes_n18.txt absent")

# Companions table: bilaterally-symmetric (A030234) and asymmetric (A030235) at
# n=18,19, regenerated from the mirror sub-counts via symcount_fast, or read
# from the tracked results/sym_counts.txt bank when the binary is absent.
SC = os.path.join(ROOT, "build", "symcount_fast")
_cov = ok + bad
Hm = Dm = _symsrc = None
if os.path.exists(SC):
    def sc(t):
        out = subprocess.run([SC, t, "19"], capture_output=True, text=True).stdout
        d = {}
        for line in out.split("\n"):
            p = line.split()
            if len(p) == 2 and p[0].lstrip("-").isdigit(): d[int(p[0])] = int(p[1])
        return d
    Hm, Dm, _symsrc = sc("hmirror"), sc("dmirror"), "build/symcount_fast (live)"
elif SYMCOLS and "hmirror" in SYMCOLS and "dmirror33" in SYMCOLS:
    Hm, Dm = SYMCOLS["hmirror"], SYMCOLS["dmirror33"]
    _symsrc = "results/sym_counts.txt (banked)"
if Hm is not None:
    print(f"  symmetric n=18,19 source: {_symsrc}")
    freeN = {18: 2808898025438, 19: 18951156321090}
    for n, bil, asym in [(18, 3791465, 2808894233973), (19, 9344655, 18951146976435)]:
        b = (Hm.get(n,0) + Dm.get(n,0)) // 2
        chk(f"bilateral({n})=(hmirror+dmirror)/2={bil}", b == bil, f"got {b}")
        chk(f"asymmetric({n})=Free-bilateral={asym}", freeN[n] - b == asym)
    covered("symmetric n=18,19", COVERAGE["symcount_1819"], _cov)
else:
    skip("symmetric n=18,19", COVERAGE["symcount_1819"],
         "build/symcount_fast not found and results/sym_counts.txt absent")

# === Claims of the full computational report (a(40) close, 2026-07) ===
# These parse the report's tables straight out of the .tex, so transcription
# errors in the paper are caught, then validate against the banked data.

TEX = open(os.path.join(ROOT, "paper", "polyplets-report.tex")).read()

def table_text(label):
    i = TEX.find("\\label{%s}" % label)
    assert i >= 0, label
    return TEX[TEX.rfind("\\begin{table}", 0, i):TEX.find("\\end{table}", i)]

def table_rows(label):
    """Rows of integers from a tabular body (\\num{} unwrapped, --- -> None)."""
    rows = []
    for line in table_text(label).splitlines():
        if "multicolumn" in line or "&" not in line:
            continue
        s = re.sub(r"\\num\{(\d+)\}", r"\1", line)
        s = re.sub(r"\\(textbf|mathbf)", "", s)
        cells = [c.strip(" ${}\\") for c in s.split("&")]
        row = []
        for c in cells:
            if c == "---":
                row.append(None)
            elif re.fullmatch(r"\d+", c):
                row.append(int(c))
        if len(row) >= 2:
            rows.append(row)
    return rows

TRI = load("results/ns_a40/triangle.txt")          # a(n) totals to 40
chk("triangle totals extend b-file", all(TRI[n] == A[n] for n in A))

# tab:terms -- all 40 values vs the banked totals
terms = {}
for row in table_rows("tab:terms"):
    for i in range(0, len(row) - 1, 2):
        terms[row[i]] = row[i + 1]
chk("tab:terms has n=1..40", sorted(terms) == list(range(1, 41)))
for n, v in sorted(terms.items()):
    chk(f"tab:terms a({n}) vs banked", TRI.get(n) == v, f"paper {v} vs {TRI.get(n)}")

# growth paragraph: quoted ratios and both lambda fits recomputed
r34 = {n: TRI[n] / TRI[n - 1] for n in range(2, 41)}
for n, q in ((20, 6.765), (27, 6.853), (34, 6.905), (40, 6.935)):
    chk(f"quoted ratio r_{n}~{q}", round(r34[n], 3) == q, f"{r34[n]:.4f}")

def lstsq(rows_, rhs):
    m = len(rows_[0])
    Aq = [[sum(rr[p] * rr[q] for rr in rows_) for q in range(m)] for p in range(m)]
    bq = [sum(rr[p] * y for rr, y in zip(rows_, rhs)) for p in range(m)]
    for col in range(m):
        piv = max(range(col, m), key=lambda i: abs(Aq[i][col]))
        Aq[col], Aq[piv] = Aq[piv], Aq[col]
        bq[col], bq[piv] = bq[piv], bq[col]
        for i in range(m):
            if i != col and Aq[i][col]:
                f_ = Aq[i][col] / Aq[col][col]
                Aq[i] = [x - f_ * y for x, y in zip(Aq[i], Aq[col])]
                bq[i] -= f_ * bq[col]
    return [bq[i] / Aq[i][i] for i in range(m)]

lam2q = [7.102, 7.104, 7.106, 7.107]
for s, q in zip((10, 15, 20, 25), lam2q):
    ns = range(s, 41)
    lam, lt = lstsq([[1.0, 1.0 / n] for n in ns], [r34[n] for n in ns])
    chk(f"2-param lambda window {s}..40 == {q}", round(lam, 3) == q, f"{lam:.4f}")
    chk(f"2-param theta window {s}..40 rounds into [-0.96,-0.95]",
        -0.96 <= round(lt / lam, 2) <= -0.95)
rss = {}
for D1 in (0.5, 1.0):
    for s in (10, 15, 20, 25):
        ns = range(s, 41)
        sol = lstsq([[1.0, 1.0 / n, 1.0 / n ** (1 + D1)] for n in ns],
                    [r34[n] for n in ns])
        lam, th = sol[0], sol[1] / sol[0]
        res = sum((sol[0] + sol[1] / n + sol[2] / n ** (1 + D1) - r34[n]) ** 2
                  for n in ns)
        rss[(D1, s)] = res
        if D1 == 0.5:
            chk(f"3-param lambda window {s}..40 in [7.1108,7.1111]",
                7.1108 <= round(lam, 4) <= 7.1111, f"{lam:.5f}")
            chk(f"3-param theta window {s}..40 in [-1.03,-1.02]",
                -1.03 <= round(th, 2) <= -1.02, f"{th:.4f}")
chk("Delta1=1/2 beats Delta1=1 on every window (~4x shortest, ~140x longest)",
    all(rss[(0.5, s)] * 3.5 <= rss[(1.0, s)] for s in (10, 15, 20, 25))
    and rss[(0.5, 10)] * 140 <= rss[(1.0, 10)])

# tab:byheight40 -- swept heights vs run data; whole column sums to a(40)
bh40 = {row[i]: row[i + 1] for row in table_rows("tab:byheight40")
        for i in range(0, len(row) - 1, 2)}
chk("tab:byheight40 has H=1..40", sorted(bh40) == list(range(1, 41)))
chk("tab:byheight40 sums to a(40)", sum(bh40.values()) == TRI[40])
chk("T(40,40)==3^39", bh40[40] == 3 ** 39)
chk("byheight40 peak at H=14", max(bh40, key=bh40.get) == 14)
inj40 = sum(v for h, v in bh40.items() if h >= 22)
chk("injected share H>=22 rounds to 4.1%", round(100 * inj40 / TRI[40], 1) == 4.1)
chk("real-swept share H=3..21 rounds to 95.9%",
    round(100 * sum(v for h, v in bh40.items() if 3 <= h <= 21) / TRI[40], 1) == 95.9)
for h in range(1, 41):
    ph = os.path.join(ROOT, "results", "ns_a40", "perheight", f"h{h}.out")
    if os.path.exists(ph):
        chk(f"T(40,{h}) vs perheight run data",
            load(f"results/ns_a40/perheight/h{h}.out").get(40) == bh40[h])

# GF lower bound vs the now-exact a(40): captures 7.5%
chk("GF bound captures 7.5% of exact a(40)",
    round(100 * 4266005101622209395058618248135 / TRI[40], 1) == 7.5)

# --- Held-out diagonal chain: refit every P_k from its two EARLIEST in-onset
# cells (the production protocol) and demand every later banked cell on the
# diagonal, through n=40, match exactly. Subsumes the quoted holdouts
# P_15->T(33,18), P_16->T(35,19), P_17->T(37,20), P_18->T(39,21) and the
# a(40) H=21 mass certification (rows n=21..39). Exact rational arithmetic.
PH40 = {}
for _f in glob.glob(os.path.join(ROOT, "results", "ns_a40", "perheight", "h*.out")):
    _H = int(os.path.basename(_f)[1:-4])
    PH40[_H] = load(os.path.relpath(_f, ROOT))
def _Pcell(n, k):                       # P_k(n) = T(n,n-k) * 3^(1+3k-n), exact
    t = PH40.get(n - k, {}).get(n)
    if t is None:
        return None
    e = 1 + 3 * k - n
    return F(t) * F(3) ** e
_ab = {}                                # k -> (a_k, b_k) cumulant constants
def _Q(n, k):                           # [y^k] exp(sum_{j<k} (a_j+b_j n) y^j)
    c = [F(0)] * (k + 1)
    c[0] = F(1)
    for j in range(1, k):
        aj, bj = _ab[j]
        cy = [F(0)] * (k + 1)
        cy[0] = F(1)
        term = F(1)
        for m in range(1, k // j + 1):
            term *= (aj + bj * n)
            term /= m
            if m * j <= k:
                cy[m * j] = term
        c = [sum(c[i] * cy[m - i] for i in range(m + 1)) for m in range(k + 1)]
    return c[k]
holdout_ok, holdout_n = True, 0
for k in range(1, 19):
    n1, n2 = 2 * k + 1, 2 * k + 2       # earliest in-onset fit points
    v1, v2 = _Pcell(n1, k) - _Q(n1, k), _Pcell(n2, k) - _Q(n2, k)
    bk = v2 - v1
    ak = v1 - bk * n1
    _ab[k] = (ak, bk)
    for n in range(2 * k + 1, 41):      # every banked in-onset cell
        want = _Pcell(n, k)
        if want is None or n in (n1, n2):
            continue
        holdout_n += 1
        if _Q(n, k) + ak + bk * n != want:
            holdout_ok = False
            print(f"  FAIL: P_{k} holdout at n={n}")
chk(f"P_k 2-point refit predicts every later banked diagonal cell "
    f"(k=1..18, {holdout_n} holdout cells)", holdout_ok)
chk("named holdouts present in the sweep",
    all(_Pcell(n, k) is not None for n, k in
        ((33, 15), (35, 16), (37, 17), (39, 18))))
# leading coefficient 25^k/k!: P_k(n) - 25^k/k! n^k must have degree < k;
# check via k-th finite difference == k! * lead == 25^k
for k in (15, 16, 17, 18):
    vals = [_Q(n, k) + _ab[k][0] + _ab[k][1] * n for n in range(2 * k + 1, 3 * k + 3)]
    d = vals[:]
    for _ in range(k):
        d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
    chk(f"P_{k} k-th difference == 25^{k} (leading coeff 25^k/k!)",
        all(x == F(25) ** k for x in d))

# symmetry counts: tab:symcounts vs banked engine outputs; Burnside companions
_cov = ok + bad
_symcolsrc = None
if os.path.exists(os.path.join(ROOT, "runs", "sym34", "r90.out")):
    S34 = {t: load(f"runs/sym34/{t}.out") for t in ("r90", "r180", "hmirror")}
    _symcolsrc = "runs/sym34 + runs/sym3{2,3} (live run dirs)"
elif SYMCOLS and all(t in SYMCOLS for t in ("r90", "r180", "hmirror")):
    S34 = {t: SYMCOLS[t] for t in ("r90", "r180", "hmirror")}
    _symcolsrc = "results/sym_counts.txt (banked)"
else:
    S34 = None
DM = load("runs/sym32/dmirror.out") \
    if os.path.exists(os.path.join(ROOT, "runs", "sym32", "dmirror.out")) \
    else (SYMCOLS or {}).get("dmirror32")
# D(33) in tab:symcounts is the T3 hybrid (direct strips + pinned closed
# forms, scripts/dmirror_hybrid_sum.py); validate it against that assembly.
DM33 = load("runs/sym33/dmirror.out") \
    if os.path.exists(os.path.join(ROOT, "runs", "sym33", "dmirror.out")) \
    else (SYMCOLS or {}).get("dmirror33")
if DM is not None and DM33 is not None:
    chk("hybrid dmirror.out prefix-matches n<=32", all(DM33[n] == DM[n] for n in DM))
    DM = DM33
if S34 and DM:
    print(f"  symmetry/companion source: {_symcolsrc}")
    for row in table_rows("tab:symcounts"):
        n, r9, r1, hm = row[0], row[1], row[2], row[3]
        d = row[4] if len(row) > 4 else None
        chk(f"tab:symcounts R90({n})", S34["r90"].get(n, 0) == r9)
        chk(f"tab:symcounts R180({n})", S34["r180"].get(n, 0) == r1)
        chk(f"tab:symcounts H({n})", S34["hmirror"].get(n, 0) == hm)
        if d is not None:
            chk(f"tab:symcounts D({n})", DM.get(n) == d, f"paper {d} vs {DM.get(n)}")

    B233 = load("results/b030233_upload.txt")
    ones_rows = {row[i]: row[i + 1] for row in table_rows("tab:onesided")
                 for i in range(0, len(row) - 1, 2)}
    for n, v in sorted(ones_rows.items()):
        num = TRI[n] + 2 * S34["r90"].get(n, 0) + S34["r180"].get(n, 0)
        chk(f"tab:onesided({n}) == Burnside/4", num % 4 == 0 and num // 4 == v)
        if n <= 33:
            chk(f"b030233({n}) == table", B233.get(n) == v)

    B = {s: load(f"results/b{s}_upload.txt")
         for s in ("030222", "030234", "030235", "194596")}
    A105 = load("fixtures/b000105.txt")
    for row in table_rows("tab:companions"):
        n, fr, bi, asy, fnp = row
        num = (TRI[n] + 2 * S34["r90"].get(n, 0) + S34["r180"].get(n, 0)
               + 2 * S34["hmirror"].get(n, 0) + 2 * DM.get(n, 0))
        chk(f"tab:companions free({n})", num % 8 == 0 and num // 8 == fr)
        chk(f"tab:companions bilat({n})",
            (S34["hmirror"].get(n, 0) + DM.get(n, 0)) % 2 == 0
            and (S34["hmirror"].get(n, 0) + DM.get(n, 0)) // 2 == bi)
        chk(f"tab:companions asym({n})", fr - bi == asy)
        chk(f"tab:companions freenonpoly({n})", fr - A105[n] == fnp)
        for s, v in (("030222", fr), ("030234", bi), ("030235", asy), ("194596", fnp)):
            chk(f"b{s}({n}) == table", B[s].get(n) == v)
    covered("symmetry/companions n<=34", COVERAGE["sym_companions"], _cov)
else:
    skip("symmetry/companions n<=34", COVERAGE["sym_companions"],
         "runs/sym34 or runs/sym32 absent and results/sym_counts.txt absent")

# dmirror diagonal quasi-polynomials (tab:dmpk) and GF numerators N_k
_cov = ok + bad
strips = glob.glob(os.path.join(ROOT, "runs", "sym32", "dmirror.S*.out"))
dd = None
if strips:
    dd = {}
    for f in strips:
        S = int(re.search(r"S(\d+)\.out", f).group(1))
        for line in open(f):
            p = line.split()
            if len(p) == 2 and p[0].isdigit():
                dd[(S, int(p[0]))] = int(p[1])
elif SYMSTRIPS:
    dd = SYMSTRIPS
if dd:
    print("  dmirror strip source: "
          + ("runs/sym32 (live)" if strips else "results/sym_counts.txt (banked)"))
    # P_k per parity: coefficient lists (constant first), Fractions
    PK = {  # (k, parity 0=even,1=odd): coeffs
        (0, 0): [2], (0, 1): [2],
        (1, 0): [6, 1], (1, 1): [7, 1],
        (2, 0): [12, 7, F(1, 2)], (2, 1): [F(27, 2), 6, F(1, 2)],
        (3, 0): [50, F(40, 3), 3, F(1, 6)],
        (3, 1): [F(93, 2), F(83, 6), F(7, 2), F(1, 6)],
        (4, 0): [180, 33, F(28, 3), F(3, 2), F(1, 24)],
        (4, 1): [F(1367, 8), F(119, 3), F(97, 12), F(4, 3), F(1, 24)],
        (5, 0): [570, F(2278, 15), F(55, 3), 4, F(5, 12), F(1, 120)],
        (5, 1): [F(4545, 8), F(18869, 120), F(185, 12), F(19, 4), F(11, 24), F(1, 120)],
    }
    for (k, par), cs in sorted(PK.items()):
        onset = 2 * k + 2 + par
        pts = [(S, v) for (S, n), v in dd.items()
               if n - S == k and S % 2 == par and S >= onset]
        good = all(sum(c * S ** i for i, c in enumerate(cs)) == v for S, v in pts)
        chk(f"tab:dmpk P_{k} {'even' if par==0 else 'odd'} on {len(pts)} points",
            len(pts) >= 3 and good)
    # N_k transcriptions: series of N_k/((1-x)^(k+1)(1+x)^k) == d(S,S+k) for ALL S
    NK = {0: [2], 1: [6, 2, -6], 2: [12, 8, -16, -8, 8],
          3: [50, 14, -124, -8, 110, 2, -36],
          4: [180, 40, -644, -54, 942, 12, -600, 2, 138],
          5: [570, 176, -2610, -520, 4996, 764, -4816, -496, 2282, 108, -422]}
    for k, N in NK.items():
        den = [1]
        for _ in range(k + 1):          # (1-x)^{k+1}
            den = [a - (den[i - 1] if i else 0)
                   for i, a in enumerate(den + [0])]
        for _ in range(k):              # (1+x)^k
            den = [a + (den[i - 1] if i else 0)
                   for i, a in enumerate(den + [0])]
        top = 32 - k
        b = []
        for m in range(top + 1):
            v = N[m] if m < len(N) else 0
            for j in range(1, min(m, len(den) - 1) + 1):
                v -= den[j] * b[m - j]
            b.append(v)
        # G_k generates the polynomial law P_k(S) at every S; its coefficients
        # agree with the raw counts exactly in-regime (S >= onset per parity).
        chk(f"N_{k} series == P_k(S) extension, S<= {top}",
            all(b[S] == sum(c * S ** i for i, c in
                            enumerate(PK[(k, S % 2)]))
                for S in range(0, top + 1)))
        chk(f"N_{k} series == d(S,S+k) in-regime, S<= {top}",
            all(b[S] == dd.get((S, S + k), 0)
                for S in range(2 * k + 2, top + 1)))
        if k >= 1:  # boundary law is k>=1 (N_0=2 is the two-spine factor)
            chk(f"N_{k}(1)==2^{k}", sum(N) == 2 ** k)
            chk(f"N_{k}(-1)==(-2)^{k}",
                sum(c * (-1) ** i for i, c in enumerate(N)) == (-2) ** k)
        chk(f"deg N_{k}==2k", len(N) - 1 == 2 * k)
    covered("dmirror P_k / N_k", COVERAGE["dmirror_strips"], _cov)
else:
    skip("dmirror P_k / N_k", COVERAGE["dmirror_strips"],
         "runs/sym32 strips absent and results/sym_counts.txt absent")

# Theorem (single-hole) / Conjecture (multi-hole total): M(n) = round((n-2)^2/8)
chk("M(n)==round((n-2)^2/8) for n=1..16",
    all(M[n - 1] == ((n - 2) ** 2 + 4) // 8 for n in range(1, 17)))

# ---- second-wave checkers: universality, hole-graded laws, deficit-2 -------
for script, tag in (("hex_gas.py", "hex law + dyadic spine"),
                    ("universal_law_check.py", "square b=1 + polyiamond ext"),
                    ("holefree_gas.py", "hole-free diagonal law"),
                    ("hole_strata_gas.py", "hole-marked strata"),
                    ("deficit2_proof.py", "deficit-2 symbolic proof")):
    rr = subprocess.run(["python3", os.path.join(ROOT, "experiments", script)],
                        capture_output=True, text=True)
    chk(f"checker: {tag}", rr.returncode == 0 and "OK" in rr.stdout,
        rr.stdout[-150:] + rr.stderr[-150:])

# ---- Theorem (not D-finite): monotonicity + irreducibility ingredients -----
r2 = subprocess.run(["python3",
                     os.path.join(ROOT, "experiments", "anisotropic_dfinite.py")],
                    capture_output=True, text=True)
chk("not-D-finite ingredients (psi, monotone mu, irreducibility) checker",
    r2.returncode == 0 and "irreducible" in r2.stdout, r2.stdout[-200:])

# ---- Theorem 1 (diagonal law) + spine cubic + ab-initio constants ----------
import sys
sys.path.insert(0, os.path.join(ROOT, "experiments"))

# (a) machine checks of the proof (rational structure, onset, sharpness k<=3)
r = subprocess.run(["python3",
                    os.path.join(ROOT, "experiments", "diagonal_law_proof_check.py")],
                   capture_output=True, text=True)
chk("diagonal-law proof checker ALL CHECKS PASS",
    r.returncode == 0 and "ALL CHECKS PASS" in r.stdout, r.stdout[-200:])

# (b) grand form ab initio through u^5 (h and g coefficients from cluster weights)
try:
    from cluster_weight_dp import check_grand_form, count_stack
    check_grand_form()
    chk("grand form (H,G) ab initio through u^5 from cluster weights", True)
except AssertionError as e:
    chk("grand form (H,G) ab initio through u^5 from cluster weights", False, str(e))

# (c) single-row cluster weight (2s+1)^2, the 25=5^2 of the leading coefficient
chk("single-row cluster weight == (2s+1)^2 for s=2..6",
    all(count_stack([1, s, 1]) == (2 * s + 1) ** 2 for s in range(2, 7)))

# (d) spine cubic: digit-product formula reproduces every in-band banked cell mod 3
_ph = os.path.join(ROOT, "results", "ns_a40", "perheight")
_cov = ok + bad
if os.path.isdir(_ph):
    T3 = {}
    for f in os.listdir(_ph):
        if f.startswith("h") and f.endswith(".out"):
            Hc = int(f[1:-4])
            for line in open(os.path.join(_ph, f)):
                a_, b_ = line.split()
                T3[(int(a_), Hc)] = int(b_)
    KX = 40
    Wm = [1] + [0] * KX
    for _ in range(KX + 2):
        inv = [1] + [0] * KX
        for m in range(1, KX + 1):
            inv[m] = (-sum(Wm[i] * inv[m - i] for i in range(1, m + 1))) % 3
        i2 = [sum(inv[i] * inv[m - i] for i in range(m + 1)) % 3
              for m in range(KX + 1)]
        Wn = [1] + [i2[m - 1] for m in range(1, KX + 1)]
        if Wn == Wm:
            break
        Wm = Wn

    def digit_product(n, kmax):
        prod = [1] + [0] * kmax
        i = 0
        nn = n
        while nn:
            d = nn % 3
            for _ in range(d):
                new = [0] * (kmax + 1)
                for a2 in range(kmax + 1):
                    if prod[a2]:
                        for b2 in range(0, kmax + 1 - a2, 3 ** i):
                            if b2 % (3 ** i) == 0 and b2 // (3 ** i) <= KX:
                                w = Wm[b2 // (3 ** i)]
                                if w:
                                    new[a2 + b2] = (new[a2 + b2] + prod[a2] * w) % 3
                prod = new
            nn //= 3
            i += 1
        return prod

    okc = 0
    badc = 0
    for (n, Hc), t in T3.items():
        k = n - Hc
        if not (1 <= Hc <= n <= 40 and n <= 2 * Hc - 1):
            continue
        e = n - 1 - 3 * k
        pk = digit_product(n, k)[k]
        if e > 0:
            want = 0 if pk == 0 else pk  # T = P_k*3^e: mod 3 == 0 always when e>0
            good = (t % 3 == 0)
            # and the stronger claim: P_k(n) mod 3 == digit product
            good = good and (t % 3 ** e == 0) and ((t // 3 ** e) % 3 == pk)
        elif e == 0:
            good = (t % 3 == pk)
        else:
            good = (pk == 0)  # P_k = T*3^{|e|} == 0 mod 3
        okc += good
        badc += not good
    chk(f"spine digit-product formula on all in-band banked cells ({okc} cells)",
        badc == 0, f"{badc} mismatches")
    covered("spine mod 3", COVERAGE["spine_mod3"], _cov)
else:
    skip("spine mod 3", COVERAGE["spine_mod3"],
         "results/ns_a40/perheight absent")

nskip = sum(n for _, n in skipped)
print()
print(f"{ok} checks passed, {bad} failed, {len(skipped)} skipped-groups "
      f"({nskip} checks).")
if skipped:
    for g, n in skipped:
        print(f"  SKIPPED: {g} ({n} checks)")
    print(f"  This run covered {ok + bad} of {ok + bad + nskip} checks. "
          + ("ALLOW_PARTIAL=1 set: exiting on failures only."
             if ALLOW_PARTIAL else
             "Set ALLOW_PARTIAL=1 to accept a degraded run."))
raise SystemExit(1 if (bad or (skipped and not ALLOW_PARTIAL)) else 0)
