#!/usr/bin/env python3
"""Session 04: remove the mod-p caveat of docs/proofs/convex-box-kernel.md §7.

Reruns Part B of s03_specialize_close.py in EXACT rational arithmetic:
for each c in {2..85}, the whole kernel pipeline specialized at x=c
(univariate series in u to degree NU), then check

    T1_c = 2*K*Delta^2*F + M + S*sqrt(Delta)  == 0   up to u-degree 242

exactly over Q.  M is re-derived exactly over Z in-process (Part A of
s03_specialize_close, which is already exact integer arithmetic).

Usage:
  python3 s04_exact_close.py probe C      -- run single c=C, print timing
  python3 s04_exact_close.py all [NPROC]  -- run c=2..85 in a process pool
"""
import sys, os, time
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s04_kernel_solve_exact as kx
import s03_specialize_close as sc

MARGIN = 8
NU = 242 + MARGIN


def specialize(poly, c):
    """x:=c in Z[x,y] poly -> u-series dict {(0,2j): int coeff}."""
    d = {}
    for (i, j), co in poly.items():
        m = (0, 2 * j)
        d[m] = d.get(m, 0) + co * c ** i
    return {m: co for m, co in d.items() if co}


def usqrt(dser, c, nu):
    """Exact sqrt of specialized Delta as u-series, constant term (1-c)."""
    a = [0] * (nu + 1)
    for (_, j), co in dser.items():
        if j <= nu:
            a[j] = co
    g = [Fraction(0)] * (nu + 1)
    g[0] = Fraction(1 - c)
    inv2g0 = 1 / (2 * g[0])
    for j in range(1, nu + 1):
        s = sum(g[i] * g[j - i] for i in range(1, j))
        g[j] = (a[j] - s) * inv2g0
    for j in range(nu + 1):
        s = sum(g[i] * g[j - i] for i in range(0, j + 1))
        assert s == a[j], "sqrt verify fail"
    return g


def run_c(args):
    c, M = args
    t0 = time.time()
    kx.NX = 0
    kx.NU = NU
    F = kx.solve(king=True, xval=c)
    Kc = kx.Ser(specialize(sc.K, c))
    Dc = kx.Ser(specialize(sc.DELTA, c))
    Mc = kx.Ser(specialize(M, c))
    Sc = kx.Ser(specialize(sc.S, c))
    g = usqrt(specialize(sc.DELTA, c), c, NU)
    R = kx.Ser({(0, j): g[j] for j in range(NU + 1) if g[j]})
    T1 = (Kc * Dc * Dc * F).scal(2) + Mc + Sc * R
    bad = [(j, co) for (_, j), co in T1.d.items()
           if co != 0 and j <= min(T1.vu, 242)]
    dt = time.time() - t0
    return (c, F.vu, sorted(bad)[:3], dt)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
    M = sc.part_a()
    if mode == "probe":
        c = int(sys.argv[2]) if len(sys.argv) > 2 else 85
        c_, vu, bad, dt = run_c((c, M))
        print(f"c={c}: validity u-deg {vu}, bad={bad}, time {dt:.1f}s")
        return
    import multiprocessing as mp
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    cs = list(range(2, 86))
    t0 = time.time()
    nbad = 0
    minvu = 10 ** 9
    with mp.Pool(nproc) as pool:
        for c, vu, bad, dt in pool.imap_unordered(run_c,
                                                  [(c, M) for c in cs]):
            minvu = min(minvu, vu)
            status = "OK" if not bad else f"FAIL {bad}"
            print(f"  c={c}: validity {vu}, {dt:.0f}s  {status}", flush=True)
            if bad:
                nbad += 1
    print(f"EXACT-Q Part B: {len(cs)} specializations c=2..85, identity "
          f"2K*Delta^2*F+M+S*sqrt(Delta)=0 checked to u-deg 242 over Q; "
          f"min validity {minvu}; failures {nbad}; wall {time.time()-t0:.0f}s")
    assert minvu >= 242 and nbad == 0
    print("CAVEAT REMOVED: identity holds over Q on the full sufficient box "
          "(84 values x deg_x<=79, u-deg 242 >= 2*119+4).")


if __name__ == "__main__":
    main()
