# Probe: D(n,H) = T(n,H) - 3T(n-1,H-1) - T(n-1,H) on the banked triangle.
# Share s = D/T; behavior along columns (fixed H) and diagonals (fixed k=n-H).
import sys
sys.path.insert(0, "/Users/jasonp/src/polyominoes/experiments/tristruct")
from triangle import Triangle

t = Triangle.load()
T = t.cell

def s(n, H):
    d = T(n, H) - 3 * T(n - 1, H - 1) - T(n - 1, H)
    return d, d / T(n, H)

print("== row 40, defect share by H ==")
for H in (3, 5, 8, 10, 12, 15, 18, 21, 25, 30, 35, 38, 39):
    d, sh = s(40, H)
    print(f"  H={H:2d}  s={sh:.4f}")

print("== fixed column H, share vs n (does s converge?) ==")
for H in (3, 5, 8, 10):
    xs = [(n, s(n, H)[1]) for n in range(H + 2, 41)]
    tail = "  ".join(f"n={n}:{v:.4f}" for n, v in xs[-4:])
    print(f"  H={H:2d}  {tail}")
    # column growth ratio for comparison with 1 - 1/mu_H
    mu = T(40, H) / T(39, H)
    print(f"        T(40,{H})/T(39,{H}) = {mu:.4f}   1-1/mu = {1-1/mu:.4f}")

print("== fixed diagonal k=n-H, share vs n (n*s -> const?) ==")
for k in (1, 2, 3, 4, 5):
    xs = [(n, s(n, n - k)[1]) for n in range(max(k + 3, 2 * k + 1), 41)]
    tail = "  ".join(f"n={n}:{v:.5f} (n*s={n*v:.3f})" for n, v in xs[-4:])
    print(f"  k={k}  {tail}")

print("== is D itself always >= 0 and where zero (sanity vs proved) ==")
neg = zero = 0
for n in range(3, 41):
    for H in range(2, n):
        d, _ = s(n, H)
        if d < 0:
            neg += 1
        if d == 0:
            zero += 1
print(f"  strict-region cells: negatives={neg} zeros={zero}")
