"""Cross-lattice combination: king vs square height triangles, cell by cell.

Square-lattice B(n,H,W) is banked to n=21 (results/bbox_square4_n21.txt, format
"n H W count"). Summing over W gives the square height triangle. Compare with
the king triangle on the same cells: is the ratio structured?
Controls: both triangles must reproduce their own row sums (A001168, A006770).
"""
import glob, re
from fractions import Fraction

# king
K = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2: K[(int(p[0]), H)] = int(p[1])

# square, summed over width
S = {}
for line in open('results/bbox_square4_n21.txt'):
    p = line.split()
    if len(p) == 4 and p[0].isdigit():
        n, H, W, c = map(int, p)
        S[(n, H)] = S.get((n, H), 0) + c

A001168 = [1, 2, 6, 19, 63, 216, 760, 2725, 9910, 36446, 135268, 505861,
           1903890, 7204874, 27394666, 104592937, 400795844, 1540820542,
           5940738676, 22964779660, 88983512783]
ok = all(sum(v for (m, H), v in S.items() if m == n) == A001168[n - 1]
         for n in range(1, 22))
print(f"control: square row sums == A001168 for n<=21: {ok}")

print("\nratio T_king(n,H) / T_square(n,H):")
print(f"{'n\\H':>4s}" + "".join(f"{H:>9d}" for H in range(1, 11)))
for n in range(6, 22):
    line = f"{n:4d}"
    for H in range(1, 11):
        if (n, H) in S and S[(n, H)] and (n, H) in K:
            line += f"{K[(n,H)]/S[(n,H)]:9.3f}"
        else:
            line += "        ."
    print(line)

print("\nsame ratio down each diagonal n-H = k (king law base 3, square base 1):")
for k in range(0, 6):
    vals = []
    for n in range(k + 1, 22):
        H = n - k
        if (n, H) in S and S[(n, H)] and (n, H) in K:
            vals.append((n, Fraction(K[(n, H)], S[(n, H)])))
    if len(vals) >= 4:
        rat = [float(vals[i][1] / vals[i - 1][1]) for i in range(1, len(vals))]
        print(f"  k={k}: ratio-of-ratios {['%.4f' % r for r in rat[-6:]]}")
        exact = [str(v[1]) for v in vals[:4]]
        print(f"        first exact values: {exact}")
