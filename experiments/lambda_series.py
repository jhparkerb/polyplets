#!/usr/bin/env python3
"""Series analysis of A006770 (fixed polyplets): growth constant lambda and the
sub-exponential form a(n) ~ C * lambda^n * n^g, from the n<=20 reach data.
a(20) is the (single-method) candidate; the qualitative picture is robust to it."""
import numpy as np
a = [1,4,20,110,638,3832,23592,147941,940982,6053180,39299408,257105146,
     1692931066,11208974860,74570549714,498174818986,3340366308393,
     22471158811164,151609203011580,1025573519362016]            # n=1..20
n  = np.arange(1, len(a)+1)
r  = np.array([a[i]/a[i-1] for i in range(1, len(a))])           # r(n), n=2..20
nr = np.arange(2, len(a)+1)
print("ratios r(n)=a(n)/a(n-1):  " + "  ".join(f"{m}:{rv:.4f}" for m,rv in zip(nr,r)))

def fit(x, y):
    A = np.vstack([np.ones_like(x), x]).T
    c,*_ = np.linalg.lstsq(A, y, rcond=None)
    return c, float(np.std(y - A@c))

for lo in (6, 8, 11):
    m = nr >= lo
    (l1,s1),e1 = fit(1/nr[m], r[m])                # r ~ lambda - lambda*theta / n
    (l2,s2),e2 = fit(1/np.sqrt(nr[m]), r[m])       # r ~ lambda + b / sqrt(n)
    print(f"n>={lo:2d}:  1/n  lambda={l1:.4f} theta={-s1/l1:.3f} resid={e1:.1e}"
          f"   |  1/sqrt(n) lambda={l2:.4f} resid={e2:.1e}")

ln = np.log(np.array(a, float))                    # log a = logC + n*log(lam) + g*log n
for lo in (8, 12):
    m = n >= lo
    M = np.vstack([np.ones(m.sum()), n[m], np.log(n[m])]).T
    c,*_ = np.linalg.lstsq(M, ln[m], rcond=None)
    print(f"log-fit n>={lo:2d}: lambda={np.exp(c[1]):.4f}  g={c[2]:.3f}  C={np.exp(c[0]):.4f}")
print("(2D lattice-animal universality predicts g = -1; lambda is the open growth constant)")
