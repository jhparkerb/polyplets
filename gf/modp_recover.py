#!/usr/bin/env python3
"""Recover the exact integer recurrence / generating function of the fixed-height
polyplet rows B_H(n), via the mod-p transfer matrix (build/gf_modp).

For each of several primes p: generate B_H(n) mod p, run Berlekamp-Massey mod p to
get the minimal recurrence mod p. The order agrees across primes (= the true
order, barring an unlucky prime). CRT the coefficients to lift to the exact
integer recurrence, then validate it against a fresh prime's sequence.

Usage:  python3 gf/modp_recover.py [Hmax]
"""
import sys, subprocess, os
from functools import reduce
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF = os.path.join(ROOT, "build", "gf_modp")

sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)

def _isprime(n):
    if n < 2: return False
    d = n - 1; r = 0
    while d % 2 == 0: d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def _primes_below(below, count):
    out = []; n = below - 1
    while len(out) < count:
        if _isprime(n): out.append(n)
        n -= 2
    return out

# Verified prime moduli just under 2^31. The fixed-height GF coefficients grow
# fast (max|coeff| roughly squares per height: ~1e11 at H=6, ~5e55 at H=8), so the
# CRT modulus must outrun them -- use a large pool. (A composite modulus, e.g. the
# tempting 2147483479, silently breaks the modular inverse, so all are MR-checked.)
PRIMES = _primes_below(1 << 31, 40)
VAL_PRIME = _primes_below(1 << 30, 1)[0]   # fresh prime for validation, disjoint

def seq_modp(H, N, p):
    out = subprocess.run([GF, str(H), str(N), str(p)], capture_output=True, text=True).stdout
    d = {0: 0}
    for line in out.split("\n"):
        q = line.split()
        if len(q) == 2: d[int(q[0])] = int(q[1])
    return [d[n] for n in range(N + 1)]

def bm_modp(s, p):
    C = [1]; B = [1]; L = 0; m = 1; b = 1
    for n in range(len(s)):
        d = s[n]
        for i in range(1, L + 1): d = (d + C[i] * s[n - i]) % p
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = C[:]; coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m: C.append(0)
            for i in range(len(B)): C[i + m] = (C[i + m] - coef * B[i]) % p
            L = n + 1 - L; B = T; b = d; m = 1
        else:
            coef = d * pow(b, p - 2, p) % p
            while len(C) < len(B) + m: C.append(0)
            for i in range(len(B)): C[i + m] = (C[i + m] - coef * B[i]) % p
            m += 1
    return C, L

def order_of(C):
    return max((i for i, c in enumerate(C) if c != 0), default=0)

def find_order(H):
    """Grow N until Berlekamp-Massey's order is comfortably below N/2."""
    N = 64
    while True:
        s = seq_modp(H, N, PRIMES[0])
        _, L = bm_modp(s, PRIMES[0])
        if L < N // 2 - 8 or N > 60000:
            return order_of(bm_modp(s, PRIMES[0])[0]), N
        N *= 2

def pconv_modp(Qp, s, p, d):
    """numerator column mod p: P_p[k] = sum_{i<=min(k,d)} Qp[i]*s[k-i] mod p, k=0..d.
    Qp is Q already reduced mod p (small ints) -- module-level so a Pool can run one
    prime per worker (the per-prime columns are independent)."""
    col = [0] * (d + 1)
    for k in range(d + 1):
        acc = 0
        for i in range(min(k, d) + 1):
            acc += Qp[i] * s[k - i]
        col[k] = acc % p
    return col

def crt(rems, mods):
    x, M = 0, 1
    for r, p in zip(rems, mods):
        # solve x' = x (mod M), x' = r (mod p)
        g = pow(M % p, p - 2, p)
        t = (r - x) % p * g % p
        x += M * t; M *= p
        x %= M
    return x, M

def sym(x, M):
    return x - M if x > M // 2 else x

def main():
    # usage: modp_recover.py [Hmax] [Hmin] [nprimes]
    #   Hmin>1 appends to the existing file; nprimes enlarges the CRT pool for high
    #   H (coeffs ~square per height: H=11 ~1e445 needs ~48 primes, H=12 ~96).
    global PRIMES
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    Hmin = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    if len(sys.argv) > 3:
        PRIMES = _primes_below(1 << 31, int(sys.argv[3]))
    path = sys.argv[4] if len(sys.argv) > 4 else \
        os.path.join(ROOT, "results", "fixed_height_gfs.txt")
    cap = int(os.environ.get("POLY_MAX_WORKERS", 0)) or (os.cpu_count() or 4)
    job = f"fixedgf-H{Hmin}_{Hmax}"
    # Two-level checkpoint: coarse (a height's finished GF block) skips the height
    # entirely on resume; fine (a single (H,N,prime) mod-p sweep) skips just the
    # banked sweeps when a height was interrupted mid-pool. Result is assembled and
    # written ONCE at the end (atomic), so resume never double-appends a height --
    # the failure mode of the old per-height out.write() path.
    ckpt = obs.Checkpoint(os.path.join(ROOT, "runs", "ckpt", job),
                          {"script": "modp_recover", "Hmin": Hmin, "Hmax": Hmax,
                           "path": os.path.abspath(path)})
    header = []
    if Hmin == 1:
        header = obs.file_header("modp_recover", job, __file__).rstrip("\n").split("\n") + [
            "# Fixed-height polyplet generating functions G_H(x) = P_H(x)/Q_H(x)",
            "# B_H(n) = fixed polyplets of n cells, bounding-box height exactly H.",
            "# Recovered by mod-p transfer matrix + Berlekamp-Massey + CRT; validated.",
            "# Format per height:  P: <numerator coeffs, low->high>",
            "#                     Q: <denominator coeffs, low->high, Q[0]=1>", ""]
    body, nval = [], 0
    with obs.Reporter(job, script=__file__, total=Hmax - Hmin + 1, threads=cap) as rep:
        for H in range(Hmin, Hmax + 1):
            blk = ckpt.get_or_none(f"H{H}-gf")     # coarse: whole height already done
            if blk is not None:
                body += blk["lines"]
                nval += blk["nval"]
                rep.beat(done=H - Hmin + 1, force=True, H=H, cached=1)
                continue
            order, _ = find_order(H)
            N = 2 * order + 30
            # CRT pool must outrun the coefficient magnitudes (log10|coeff| grows ~
            # linearly in deg). A FIXED estimate is unsafe: `need = order//110 + 12`
            # silently WRAPPED at H=11 (deg 13381) -- 133 primes too few, CRT produced
            # garbage that only the fresh-prime check caught, after a 15h run. So now
            # ADAPTIVE: start at the estimate, then GROW primes + retry until the GF
            # VALIDATES against an independent prime (a wrapped reconstruction fails that
            # ~2^-31 of the time). Per-prime sweeps are cached by (H,N,p) and reused
            # across rounds + runs, so each prime's sweep is computed at most once.
            # POLY_GF_START forces a low start (test the growth path on a small height).
            np_try = int(os.environ.get("POLY_GF_START", 0)) or \
                     max(len(PRIMES), order // 110 + 12)
            np_cap = 3 * (order // 110 + 12) + 50   # backstop; report if hit unvalidated
            ok = False; Ls = [0]; d = 0; P = [0]; Q = [1]
            while True:
                PRIMES = _primes_below(1 << 31, np_try)
                # per-prime sweeps: independent, CPU-bound -> process pool; load banked,
                # compute only misses, bank each (cheap on rerun/regrow).
                _nproc = min(len(PRIMES), os.cpu_count() or 4,
                             int(os.environ.get("POLY_MAX_WORKERS", 1 << 30)))
                seqs = [ckpt.get_or_none(f"H{H}-N{N}-p{p}") for p in PRIMES]
                miss = [ki for ki, s in enumerate(seqs) if s is None]
                if miss:
                    with Pool(min(_nproc, len(miss))) as _pool:
                        for ki, s in zip(miss, _pool.starmap(
                                seq_modp, [(H, N, PRIMES[ki]) for ki in miss])):
                            ckpt.save(f"H{H}-N{N}-p{PRIMES[ki]}", s)
                            seqs[ki] = s
                # Berlekamp-Massey per prime: independent -> PARALLEL (was a serial list
                # comp; ~1.5h serial at H=11). Reuse the sweep worker pool.
                with Pool(_nproc) as _pool:
                    Cs = _pool.starmap(bm_modp,
                                       [(seqs[k], PRIMES[k]) for k in range(len(PRIMES))])
                Ls = [order_of(C) for C, _ in Cs]
                if len(set(Ls)) != 1:
                    rep.event("order_disagree", H=H, orders=str(Ls))  # needs more N, not primes
                    break
                d = Ls[0]
                # denominator Q[0..d] by CRT (Q[0]=1), symmetric lift; numerator P next
                Q = [1] + [sym(*crt([Cs[k][0][i] for k in range(len(PRIMES))], PRIMES))
                           for i in range(1, d + 1)]
                # numerator P[k] = sum_{i<=min(k,d)} Q[i]*B(k-i), deg P <= d. PER PRIME:
                # pre-reduce Q mod p ONCE (the old code recomputed Q[i]%p -- a ~1200-digit
                # bignum mod -- inside the k,prime,i triple loop, ~1.2e10 times = ~4.6h at
                # H=11), then convolve with that prime's B mod p using small ints.
                Qp_all = [[qi % p for qi in Q] for p in PRIMES]   # reduce Q mod p once
                with Pool(_nproc) as _pool:                       # one prime per worker
                    Pmod = _pool.starmap(pconv_modp,
                        [(Qp_all[ki], seqs[ki], PRIMES[ki], d) for ki in range(len(PRIMES))])
                P = [sym(*crt([Pmod[ki][k] for ki in range(len(PRIMES))], PRIMES))
                     for k in range(d + 1)]
                while len(P) > 1 and P[-1] == 0: P.pop()   # trim leading-zero high terms
                # validate the FULL GF against a fresh prime (the soundness gate): expand
                # P/Q as a power series and compare to the engine's sequence.
                vp = VAL_PRIME
                sv = ckpt.get_or_none(f"H{H}-N{N}-val{vp}")
                if sv is None:
                    sv = seq_modp(H, N, vp)
                    ckpt.save(f"H{H}-N{N}-val{vp}", sv)
                b = [0] * (N + 1)
                for n in range(N + 1):
                    v = (P[n] if n < len(P) else 0)
                    for i in range(1, d + 1):
                        if n - i >= 0: v -= Q[i] * b[n - i]
                    b[n] = v % vp
                ok = all(b[n] == sv[n] % vp for n in range(N + 1))
                # wrap diagnostic: a sound result has max|coeff| well below M/2 =
                # (prod primes)/2; near-ceiling coeffs are the wraparound signature.
                M = 1
                for p in PRIMES: M *= p
                maxc = max((abs(c) for c in Q + P), default=0)
                rep.event("crt_round", H=H, primes=len(PRIMES), order=d, validated=ok,
                          coeff_digits=len(str(maxc)), ceil_digits=len(str(M // 2)))
                if ok or np_try >= np_cap:
                    break
                np_try = int(np_try * 1.4) + 8          # grow + retry (sweeps cached)
            if len(set(Ls)) != 1:                       # order disagreement: skip height
                continue
            hlines = [f"H={H}  order={d}  validated={ok}", f"P: {P}", f"Q: {Q}", ""]
            ckpt.save(f"H{H}-gf", {"lines": hlines, "nval": int(ok)})
            body += hlines
            nval += int(ok)
            # one heartbeat per completed height (coarse units, minutes-to-hours
            # each): liveness + the per-height detail that used to print to stdout.
            rep.beat(done=H - Hmin + 1, force=True, H=H, order=d, validated=ok,
                     degP=len(P) - 1, primes=len(PRIMES))
        with open(path, "a" if Hmin > 1 else "w") as out:   # single assembled write
            out.write("\n".join(header + body) + "\n")
        rep.done(result=nval, resumed=ckpt.n_resumed, out=path)
    # Keep the cache if ANY height failed validation: the per-prime sweeps are the
    # expensive part (hours), and a rerun must reuse them. (The OLD unconditional
    # clear() discarded H=11's 133 sweeps after it finished validated=False -> 15h lost.)
    if nval == (Hmax - Hmin + 1):
        ckpt.clear()
    else:
        print(f"# {nval}/{Hmax - Hmin + 1} heights validated; KEEPING checkpoints in "
              f"{ckpt.dir} for reuse on rerun", file=sys.stderr)

if __name__ == "__main__":
    main()
