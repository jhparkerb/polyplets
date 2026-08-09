"""Does the below-onset defect obey a large-deviation scaling form?

Hypothesis: (1/k) * ln( D_k(H) / T(H+k,H) )  =  g(H/k) + o(1),
i.e. the RELATIVE error of the diagonal law below onset has a scaling limit.
Test: parameter-free collapse. Interpolate each k's curve onto a common x grid
and measure the spread across k; compare against deliberately wrong scalings
(1/k^0 and 1/k^2) as negative controls.
"""
import glob, re, math
from fractions import Fraction
import numpy as np
T = {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2: T[(int(p[0]), H)] = int(p[1])
src = open('orchestrator/sweep.go').read()
block = src[src.index('var diagCoeffTable = map[int]diagCoeffs{'):]
block = block[:block.index('\n}\n')]
PK = {}
for m in re.finditer(r'(\d+):\s*\{\s*\[\]string\{([^}]*)\}\s*,\s*(\d+)\s*\}', block, re.S):
    PK[int(m.group(1))] = ([int(x) for x in re.findall(r'-?\d+', m.group(2))], int(m.group(3)))
def law(k, n):
    c, den = PK[k]; v = Fraction(0)
    for x in c: v = v * n + x
    return v / den * Fraction(3) ** (n - 1 - 3 * k)

curves = {}
for k in sorted(PK):
    xs, ys = [], []
    for H in range(1, k + 1):
        n = H + k
        if (n, H) not in T: continue
        d = Fraction(T[(n, H)]) - law(k, n)
        if d <= 0: continue
        rel = float(d / Fraction(T[(n, H)]))
        xs.append(H / k); ys.append(math.log(rel))
    if len(xs) >= 6: curves[k] = (np.array(xs), np.array(ys))

grid = np.linspace(0.25, 0.85, 13)
def spread(power):
    """relative spread across k of (1/k^power) ln rel, on the common grid"""
    stack = []
    for k, (xs, ys) in curves.items():
        if k < 8: continue
        stack.append(np.interp(grid, xs, ys / k ** power))
    A = np.array(stack)
    return float(np.mean(np.std(A, axis=0) / (np.abs(np.mean(A, axis=0)) + 1e-12)))

print("collapse quality (mean relative spread across k = 8..19; lower = better)")
for p in (0.0, 0.5, 1.0, 1.5, 2.0):
    print(f"  scaling exponent {p:.1f}:  spread {spread(p):.4f}"
          + ("   <-- hypothesis" if p == 1.0 else ""))

print("\nthe collapsed curve g(x) = (1/k) ln(D/T), at x = H/k:")
print(f"{'x':>6s}" + "".join(f"{k:>9d}" for k in (10, 13, 16, 19)))
for x in grid:
    row = f"{x:6.2f}"
    for k in (10, 13, 16, 19):
        xs, ys = curves[k]
        row += f"{np.interp(x, xs, ys) / k:9.4f}"
    print(row)

print("\n=== Richardson extrapolation in 1/k to the limit shape g(x) ===")
print("g_k(x) = g(x) + c(x)/k   fitted on the four largest k available per x")
print(f"{'x':>6s}{'g(x)':>10s}{'c(x)':>9s}{'resid':>9s}   digits correct at k=19,25,40")
KS = [k for k in sorted(curves) if k >= 10]
for x in np.linspace(0.35, 0.95, 13):
    pts = []
    for k in KS:
        xs, ys = curves[k]
        if xs[0] <= x <= xs[-1]:
            pts.append((1.0 / k, np.interp(x, xs, ys) / k))
    if len(pts) < 4: continue
    pts = pts[-6:]
    A = np.array([[1.0, p[0]] for p in pts]); b = np.array([p[1] for p in pts])
    (g, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    resid = float(np.max(np.abs(A @ [g, c] - b)))
    dig = [(-k * g / math.log(10)) for k in (19, 25, 40)]
    print(f"{x:6.2f}{g:10.4f}{c:9.4f}{resid:9.4f}   "
          + "  ".join(f"{d:5.1f}" for d in dig))

# where does the law stop giving even one correct digit?
xs_g, gs = [], []
for x in np.linspace(0.30, 0.95, 40):
    pts = []
    for k in KS:
        cx, cy = curves[k]
        if cx[0] <= x <= cx[-1]: pts.append((1.0 / k, np.interp(x, cx, cy) / k))
    if len(pts) < 4: continue
    A = np.array([[1.0, p[0]] for p in pts[-6:]]); b = np.array([p[1] for p in pts[-6:]])
    (g, c), *_ = np.linalg.lstsq(A, b, rcond=None)
    xs_g.append(x); gs.append(g)
xs_g, gs = np.array(xs_g), np.array(gs)
cross = np.interp(0.0, gs[::-1], xs_g[::-1]) if gs.min() < 0 < gs.max() else float('nan')
print(f"\ng(x) = 0 at x = H/k = {cross:.3f}  -- below this the law's relative error")
print("exceeds 1 and it carries no information; above it, accuracy grows")
print(f"exponentially in k.  x = {cross:.3f} corresponds to slope n/H = "
      f"{1 + 1/cross:.2f} in the n = sH parametrisation.")
