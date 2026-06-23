"""Finite-size-scaling extrapolation of the king-lattice growth constant lambda.

Idea under test: the per-height growth constants lambda_H = 1/rho_H (rho_H =
smallest positive real root of the fixed-height denominator Q_H) should approach
lambda_infty as a POWER LAW in 1/H for a 2D system, not geometrically. The project
previously tried Aitken (which assumes geometric convergence) on the lambda_H
ladder and found it worse than direct a(n)/a(n-1) ratio fits -- consistent with
the convergence being power-law, which Aitken cannot capture.

This fits lambda_H = lambda_infty - A * H^(-p) (and BST/Bulirsch-Stoer-style and
1/H, 1/H^2 forms) to the EXACT algebraic lambda_H from the recovered Q_H.
No new compute: reads results/fixed_height_gfs.txt.
"""
import numpy as np
import re, sys

def load_PQ():
    Ps, Qs = {}, {}
    H = None
    for line in open("results/fixed_height_gfs.txt"):
        m = re.match(r"H=(\d+)\s+order", line)
        if m:
            # skip unvalidated heights (e.g. H=11 validated=False, 2026-06-23) --
            # an unvalidated GF has wrong coefficients, would corrupt the FSS.
            H = int(m.group(1)) if "validated=False" not in line else None
        elif line.startswith("P:") and H is not None:
            Ps[H] = [int(x) for x in re.findall(r"-?\d+", line.split(":",1)[1])]
        elif line.startswith("Q:") and H is not None:
            Qs[H] = [int(x) for x in re.findall(r"-?\d+", line.split(":",1)[1])]
    return Ps, Qs

def series(P, Q, N):
    # exact integer series of P/Q to order N (Q[0]==1 assumed; P,Q low->high).
    b = [0]*(N+1)
    for n in range(N+1):
        s = P[n] if n < len(P) else 0
        for j in range(1, min(n, len(Q)-1)+1):
            s -= Q[j]*b[n-j]
        b[n] = s  # Q[0]=1
    return b

def lambda_H(P, Q, N=400):
    # lambda_H = lim B(n)/B(n-1); Richardson-accelerate the ratio sequence.
    b = series(P, Q, N)
    ns, r = [], []
    for n in range(N-30, N+1):
        if b[n-1] != 0:
            ns.append(n); r.append(b[n]/b[n-1])  # big-int true division -> float
    ns = np.array(ns, float); r = np.array(r)
    # ratio r_n ~ lam (1 + c/n): regress on 1/n, intercept = lam_infty for this H
    A = np.vstack([1.0/ns, np.ones_like(ns)]).T
    coef, *_ = np.linalg.lstsq(A, r, rcond=None)
    return coef[1]

def main():
    Ps, Qs = load_PQ()
    Hs = sorted(Qs)
    lam = {H: lambda_H(Ps[H], Qs[H]) for H in Hs}
    # GF-free rungs from experiments/lambda_ladder_fast.py (Aitken, N=120): extends the
    # ladder past the H<=10 GFs (the H=11 GF recovery failed; the fast path bypasses it).
    lam.update({11: 6.11591, 12: 6.21937, 13: 6.30668})  # fast-ladder Aitken, N=120
    Hs = sorted(lam)
    print("Per-height growth constants lambda_H = 1/rho_H:")
    for H in Hs:
        d = lam[H]-lam[H-1] if H-1 in lam else float('nan')
        print(f"  H={H:2d}  lambda_H = {lam[H]:.6f}   delta = {d:.6f}")

    L = np.array([lam[H] for H in Hs], float)
    Harr = np.array(Hs, float)

    print()
    # --- robust extrapolation. The ladder converges as a POWER LAW (the old free-w BST
    # found degenerate optima -> garbage 5.889 < lam_12). Increments d_H = lam_H-lam_{H-1}
    # decay ~ C*H^{-alpha}; fit alpha,C on the tail (log-log) and SUM the remaining tail:
    # lambda_infty = lam_last + sum_{H>last} C*H^{-alpha}. (Valid only if alpha>1.) ---
    dH = np.array([lam[H]-lam[H-1] for H in Hs if H-1 in lam])
    nH = np.array([float(H) for H in Hs if H-1 in lam])
    last = Hs[-1]
    for Hmin in (4, 6, 8):
        m = nH >= Hmin
        if m.sum() < 3: continue
        slope, c0 = np.polyfit(np.log(nH[m]), np.log(dH[m]), 1)
        alpha, C = -slope, np.exp(c0)
        if alpha <= 1.0:
            print(f"increment-decay (H>={Hmin}): alpha={alpha:.2f}<=1 -> tail diverges "
                  "(too few rungs to bound lambda_infty)")
            continue
        tail = float(np.sum(C * np.arange(last+1, 200000, dtype=float)**(-alpha)))
        print(f"increment-decay (H>={Hmin}): alpha={alpha:.3f}  lambda_infty ~ {lam[last]+tail:.4f}")
    # iterated Aitken delta^2 (robust accelerator; under-extrapolates power-law but
    # never diverges -> a sanity floor)
    def aitken(s):
        return [s[i] - (s[i+1]-s[i])**2/(s[i+2]-2*s[i+1]+s[i])
                for i in range(len(s)-2) if abs(s[i+2]-2*s[i+1]+s[i]) > 1e-12]
    a = list(L)
    for _ in range(3):
        if len(a) >= 3: a = aitken(a)
    if a: print(f"iterated Aitken: lambda_infty >~ {a[-1]:.4f}  (floor; power-law undersells)")

    # --- power-law fits lambda_infty - lam_H = A H^{-p}, grid over (lambda_infty,p) ---
    # For a guessed Linf and p, regress log(Linf-lam_H) ~ log A - p log H; pick Linf,p
    # giving the straightest line (max R^2) using H>=Hmin tail.
    for Hmin in (3,4,5,6):
        mask = Harr>=Hmin
        Hs2, L2 = Harr[mask], L[mask]
        bestfit=None
        for Linf in np.linspace(L[-1]+0.001, 9.5, 1700):
            y = np.log(Linf - L2)
            x = np.log(Hs2)
            A = np.vstack([x, np.ones_like(x)]).T
            (slope, inter), res, *_ = np.linalg.lstsq(A, y, rcond=None)
            yhat = A@np.array([slope,inter])
            ss_res = np.sum((y-yhat)**2); ss_tot=np.sum((y-y.mean())**2)
            r2 = 1-ss_res/ss_tot if ss_tot>0 else -1
            if bestfit is None or r2>bestfit[0]:
                bestfit=(r2, Linf, -slope)
        print(f"power-law (H>={Hmin}): lambda_infty ~ {bestfit[1]:.4f}  p={bestfit[2]:.3f}  R^2={bestfit[0]:.6f}")

if __name__=="__main__":
    main()
