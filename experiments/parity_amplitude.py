"""|F_n(-1)|/a(n) is the height distribution's Fourier coefficient at frequency
pi. For a Gaussian core of width w it decays as exp(-pi^2 w^2/2); for an
exponential/Laplace core as exp(-alpha w). Which one does the data follow?
Fit both on n <= 33, predict n = 34..40.  (Sign oscillation removed by taking
|.| and fitting the envelope through the run maxima.)
"""
import glob, re, math
import numpy as np
T, A = {}, {}
for f in glob.glob('results/ns_a40/perheight/h*.out'):
    H = int(re.findall(r'h(\d+)', f)[0])
    for line in open(f):
        p = line.split()
        if len(p) == 2:
            n, v = int(p[0]), int(p[1]); T[(n, H)] = v
            if v: A[n] = A.get(n, 0) + v

ns = list(range(10, 41))
alt = {n: abs(sum((-1) ** H * T.get((n, H), 0) for H in range(1, n + 1))) for n in ns}
mean = {n: sum(H * T.get((n, H), 0) for H in range(1, n + 1)) / A[n] for n in ns}
w = {n: math.sqrt(sum((H - mean[n]) ** 2 * T.get((n, H), 0) for H in range(1, n + 1)) / A[n])
     for n in ns}
y = {n: math.log(alt[n] / A[n]) for n in ns if alt[n]}

print(f"{'n':>3s}{'width w':>9s}{'ln(|F|/a)':>12s}{'/w':>9s}{'/w^2':>9s}")
for n in ns:
    if n in y:
        print(f"{n:3d}{w[n]:9.3f}{y[n]:12.3f}{y[n]/w[n]:9.3f}{y[n]/w[n]**2:9.4f}")

fit = [n for n in ns if n in y and n <= 33]
out = [n for n in ns if n in y and n >= 34]
for label, basis in (("exp(-alpha*w)   ", lambda n: [1.0, w[n]]),
                     ("exp(-beta*w^2)  ", lambda n: [1.0, w[n] ** 2]),
                     ("both            ", lambda n: [1.0, w[n], w[n] ** 2])):
    X = np.array([basis(n) for n in fit]); Y = np.array([y[n] for n in fit])
    c, *_ = np.linalg.lstsq(X, Y, rcond=None)
    pred = np.array([basis(n) for n in out]) @ c
    err = np.max(np.abs(pred - np.array([y[n] for n in out])))
    print(f"{label}: coeffs {np.round(c, 4)}   max holdout error in ln  {err:.3f}")
