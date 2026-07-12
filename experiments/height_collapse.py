#!/usr/bin/env python3
"""Universal shape of the polyplet height distribution: a data collapse.

Reads the FULL exact height triangle T(n,H) from results/ns_a36/perheight/hH.out
(all H, n<=36; row sums verified == a(n) against the b-file). Tests whether the
height (extent) distribution has a universal limiting shape.

Two scalings:
  - exponent collapse:  x=H/n^nu, y=n^nu * T/a  (needs nu; finite-size-renormalized)
  - PARAMETER-FREE shape collapse: x=H/<H>, y=<H>*T/a  -> universal g(x) if it
    collapses. This is the clean test (no exponent assumed).

Findings (n<=36):
  - Parameter-free shape collapses, and TIGHTENS with n (rel-var 0.19 -> 0.065
    as the window moves from n=8..20 to n=24..36): a universal limit shape g.
  - Its moments converge: std/mean -> ~0.225, skew -> ~0.35 (right-skewed tail).
  - <H> ~ n^nu_eff with nu_eff drifting 0.72 -> 0.68 (n=10->36), slowly toward the
    asymptotic 2D lattice-animal value 0.6407; n<=36 is still pre-asymptotic.
See results/height-distribution-collapse.md.
"""
import os, math

D = "results/ns_a36/perheight"


def load():
    T = {}
    for f in os.listdir(D):
        if f.startswith("h") and f.endswith(".out"):
            H = int(f[1:-4])
            for ln in open(os.path.join(D, f)):
                n, c = ln.split()
                T[(int(n), H)] = int(c)
    return T


def main():
    T = load()
    a = {n: sum(T.get((n, H), 0) for H in range(1, 37)) for n in range(1, 37)}
    mean = {n: sum(H * T.get((n, H), 0) for H in range(1, n + 1)) / a[n] for n in range(4, 37)}

    print("nu_eff from <H> ~ n^nu (full untruncated triangle):")
    for n in range(12, 37, 4):
        nu = (math.log(mean[n]) - math.log(mean[n - 4])) / (math.log(n) - math.log(n - 4))
        print(f"  n={n:2d}  <H>={mean[n]:6.3f}  nu_eff[{n-4},{n}]={nu:.4f}")

    def curve(n):
        return sorted((H / mean[n], mean[n] * T.get((n, H), 0) / a[n])
                      for H in range(1, n + 1) if T.get((n, H), 0))

    def interp(c, x):
        if x < c[0][0] or x > c[-1][0]:
            return None
        for i in range(1, len(c)):
            if c[i][0] >= x:
                (x0, y0), (x1, y1) = c[i - 1], c[i]
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0) if x1 > x0 else y0

    def rel_var(ns, xlo=0.2, xhi=2.2, m=50):
        curves = [curve(n) for n in ns]
        grid = [xlo + (xhi - xlo) * i / m for i in range(m + 1)]
        tot = cnt = 0
        for x in grid:
            ys = [v for v in (interp(c, x) for c in curves) if v is not None]
            if len(ys) >= len(ns) - 1 and len(ys) >= 3:
                mu = sum(ys) / len(ys)
                tot += (sum((v - mu) ** 2 for v in ys) / len(ys)) / (mu * mu + 1e-12)
                cnt += 1
        return tot / cnt

    print("\nparameter-free shape-collapse rel-variance (lower=tighter, by n-window):")
    for ns in ([8, 12, 16, 20], [16, 20, 24, 28], [24, 28, 32, 36]):
        print(f"  n={ns}: {rel_var(ns):.4f}")

    print("\nmoments of H/<H> (converge to universal shape):")
    for n in range(12, 37, 4):
        m2 = sum((H / mean[n]) ** 2 * T.get((n, H), 0) for H in range(1, n + 1)) / a[n]
        m3 = sum((H / mean[n]) ** 3 * T.get((n, H), 0) for H in range(1, n + 1)) / a[n]
        cv = math.sqrt(m2 - 1)
        print(f"  n={n:2d}  std/mean={cv:.4f}  skew={(m3 - 3 * m2 + 2) / cv ** 3:+.4f}")

    # ASCII overlay of the collapsed shape at large n
    print("\ncollapsed shape g(x=H/<H>)  [n=24 '.'  n=36 '#'  overlaid]:")
    for n, mk in ((24, "."), (36, "#")):
        pass
    grid = [0.3 + 0.05 * i for i in range(34)]
    for x in grid:
        row = ""
        y = interp(curve(36), x)
        if y is None:
            continue
        bar = int(round(y * 30))
        print(f"  x={x:.2f} |" + "#" * bar)


if __name__ == "__main__":
    main()
