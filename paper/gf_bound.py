#!/usr/bin/env python3
# Rigorous lower bound  a(n) >= sum_{H<=Hmax} [x^n] G_H(x), by expanding the recovered
# fixed-height rational GFs in results/fixed_height_gfs.txt as exact integer power
# series. This is the paper's "rigorous lower bound" figure + the captured-fraction.
# Sanity: GF-expanded B_H(19) must match the known byHeight row, and sum_{H<=9} at
# n=25 must match the paper's existing 4,380,493,652,795,380,053.
import ast, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "results", "fixed_height_gfs.txt")

def parse_gfs():
    gfs, H, P = {}, None, None
    for line in open(PATH):
        s = line.strip()
        if s.startswith("H="):
            H = int(s.split()[0].split("=")[1])
        elif s.startswith("P:"):
            P = ast.literal_eval(s[2:].strip())
        elif s.startswith("Q:"):
            gfs[H] = (P, ast.literal_eval(s[2:].strip()))
    return gfs

def series(P, Q, N):
    # b_n = P[n] - sum_{j=1..n} Q[j] b[n-j],  with Q[0] == 1 (exact integers)
    b = [0] * (N + 1)
    for n in range(N + 1):
        v = P[n] if n < len(P) else 0
        for j in range(1, min(n, len(Q) - 1) + 1):
            v -= Q[j] * b[n - j]
        b[n] = v
    return b

A19 = 151609203011580
BH19 = {1: 1, 2: 15994426, 3: 12736006193, 4: 452027455240, 5: 3469435781222,
        6: 10975452058596, 7: 20257323484797, 8: 26611876627714,
        9: 27701775032858, 10: 24014057424024}

A25 = 14994811325186658577
A34 = 515316838423862758858377704

gfs = parse_gfs()
N = 40
ser = {H: series(P, Q, N) for H, (P, Q) in gfs.items()}
print(f"heights recovered: {sorted(ser)}")
print("=== cross-check GF-expanded B_H(19) vs byHeight ===")
for H in sorted(ser):
    got, exp = ser[H][19], BH19.get(H)
    print(f"  H={H:2d}: {got}  {'ok' if exp is None or got == exp else 'MISMATCH '+str(exp)}")
for n in (19, 25, 34, 35, 40):
    s9 = sum(ser[H][n] for H in range(1, 10) if H in ser)
    s10 = sum(ser[H][n] for H in range(1, 11) if H in ser)
    print(f"=== n={n}:  sum_H<=9 = {s9}")
    print(f"          sum_H<=10 = {s10}")
    if n == 19:
        print(f"   captured: H<=9 = {100*s9/A19:.1f}%,  H<=10 = {100*s10/A19:.1f}%")
    if n == 25:
        print(f"   captured vs a(25): {100*s10/A25:.1f}%")
    if n == 34:
        print(f"   captured vs a(34): {100*s10/A34:.1f}%")
