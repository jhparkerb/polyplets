#!/usr/bin/env python3
"""#5b: recover the exact rational GF G_{H,k}(x) = sum_n B_{H,k}(n) x^n for fixed
strip height H and fixed hole count k, via the mod-p holes transfer matrix --
lifting the u64 wall that limited gf/hole_recover.py to ~30-40 terms.

For each prime p (build/tma_holes ... --modp p) we get B_{H,k}(n) mod p for as
many n as we like (no overflow). Berlekamp-Massey mod p gives the minimal
recurrence mod p; the order agrees across primes; CRT lifts the coefficients to
exact integers; a fresh prime validates the full GF as a power series. Same
machine as modp_recover.py (fixed-height GFs), now carrying the hole index.

Each [q^k] slice of the rational bivariate G_H(x,q) is itself rational, with
order growing with k -- so for a fixed term budget N the low-k slices recover and
the highest-k slices (onset near N, too few terms) are reported as pending.

Usage:  python3 gf/hole_modp_recover.py [Hmax] [N]   (defaults: Hmax=5, N=240)
"""
import os
import sys
import subprocess
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modp_recover import _primes_below, bm_modp, order_of, crt, sym
from recover import poly  # single-source the GF pretty-printer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMA = os.path.join(ROOT, "build", "tma_holes")

sys.path.insert(0, ROOT)
import obs  # shared observability/provenance runtime (docs/observability.md)

PRIMES = _primes_below(1 << 31, 40)
VAL_PRIME = _primes_below(1 << 30, 1)[0]   # fresh, disjoint from PRIMES


def slices_modp(H, N, p, K=None):
    """{k: [B_{H,k}(0..N) mod p]} from one mod-p single-height holes sweep.
    K (kmax) with --hdrop drops holes>K (exact for k<=K) so RAM is O(D_H*N*K),
    letting high N (many terms, tall H) fit in memory."""
    cmd = [TMA, "square8", str(N), "--holes", "--only-height", str(H), "--modp",
           str(p)]
    if K is not None:
        cmd += ["--kmax", str(K), "--hdrop"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    by = {}
    for line in out.split("\n"):
        q = line.split()
        if len(q) != 4:
            continue
        _, n, k, c = (int(x) for x in q)
        by.setdefault(k, [0] * (N + 1))[n] = c % p
    return by


def _slice_job(args):
    """Pool worker: (H, N, p, K) -> (p, slices). Tagged with p so results can be
    banked per (height, prime) as they complete -- the checkpoint unit."""
    H, N, p, K = args
    return p, slices_modp(H, N, p, K)


def recover_slice(seqs, val_seq, N):
    """seqs[i] = B_{H,k}(0..N) mod PRIMES[i]; returns
    ('ok', order, P, Q, validated) | ('order_disagree', Ls) |
    ('insufficient', order) | None (trivial/empty)."""
    Cs = [bm_modp(seqs[i], PRIMES[i]) for i in range(len(PRIMES))]
    Ls = [order_of(C) for C, _ in Cs]
    if len(set(Ls)) != 1:
        return ("order_disagree", Ls)
    d = Ls[0]
    if d == 0:
        return None
    if N < 2 * d + 2:                       # not enough terms to trust/validate
        return ("insufficient", d)
    Q = [1] + [sym(*crt([Cs[i][0][j] for i in range(len(PRIMES))], PRIMES))
               for j in range(1, d + 1)]
    P = []
    for kk in range(d + 1):
        rems = [sum(Q[j] % p * seqs[i][kk - j] for j in range(min(kk, d) + 1)) % p
                for i, p in enumerate(PRIMES)]
        P.append(sym(*crt(rems, PRIMES)))
    while len(P) > 1 and P[-1] == 0:
        P.pop()
    # validate full GF P/Q as a power series against a fresh prime
    b = [0] * (N + 1)
    for n in range(N + 1):
        v = P[n] if n < len(P) else 0
        for j in range(1, d + 1):
            if n - j >= 0:
                v -= Q[j] * b[n - j]
        b[n] = v % VAL_PRIME
    ok = all(b[n] == val_seq[n] % VAL_PRIME for n in range(N + 1))
    return ("ok", d, P, Q, ok)


HEADER = [
    "# Fixed-(height, #holes) polyplet generating functions",
    "#   G_{H,k}(x) = P/Q = sum_n B_{H,k}(n) x^n,",
    "#   B_{H,k}(n) = # height-exactly-H n-cell polyplets with exactly k holes",
    "#   (primary 4-connected-background convention).",
    "# Recovered by mod-p holes transfer matrix + Berlekamp-Massey + CRT,",
    "# full-GF validated against a fresh prime (#5b). P,Q low->high, Q[0]=1.",
    "",
]


def main():
    # usage: hole_modp_recover.py Hmin Hmax N [K] [nprimes]
    #   K (kmax) given => --hdrop mode: drop holes>K, recover slices k=0..K with
    #     RAM O(D_H*N*K) (lets tall H / high N fit). K omitted => all k (RAM ~N^2).
    #   Hmin>1 APPENDS to results/hole_gfs.txt (preserves lower heights).
    global PRIMES
    Hmin = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    Hmax = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 240
    K = int(sys.argv[4]) if len(sys.argv) > 4 else None
    if len(sys.argv) > 5:
        PRIMES = _primes_below(1 << 31, int(sys.argv[5]))
    out_path = os.path.join(ROOT, "results", "hole_gfs.txt")

    job = f"holegf-H{Hmin}_{Hmax}-k{K}"
    banner = obs.file_header("hole_modp_recover", job, __file__).rstrip("\n").split("\n")
    lines = banner + (list(HEADER) if Hmin == 1 else [])
    if Hmin > 1:
        lines.append(f"# --- extension run: H={Hmin}..{Hmax}, N={N}, "
                     f"kmax={K} (hdrop), {len(PRIMES)} primes ---")
    # the per-prime engine sweeps are independent and CPU-bound -- run them in a
    # process pool (one core each). On a 32-core box this is ~min(#primes,cores)x
    # faster than the serial loop and is what makes high H / large N tractable.
    # POLY_MAX_WORKERS caps the pool to honor a machine's core budget (set =10 on
    # gympie's 10 performance cores; efficiency cores are off-limits). Without it the
    # pool grabs every logical core and oversubscribes. Fewer workers just means each
    # handles more primes serially -- still correct, only slower.
    nproc = min(len(PRIMES) + 1, os.cpu_count() or 4,
                int(os.environ.get("POLY_MAX_WORKERS", 1 << 30)))
    # Checkpoint at the (height, prime) sweep -- the expensive C++ unit. A kill
    # re-runs only the primes not yet banked (resumes by re-issuing the same
    # command); the meta-guard refuses a resume whose N/kmax/primes differ.
    allprimes = PRIMES + [VAL_PRIME]
    ckpt = obs.Checkpoint(
        os.path.join(ROOT, "runs", "ckpt", f"{job}-N{N}-p{len(PRIMES)}"),
        {"N": N, "kmax": K, "primes": PRIMES, "val": VAL_PRIME})
    pending, disagree, nval = [], [], 0
    with obs.Reporter(job, script=__file__, total=Hmax - Hmin + 1, threads=nproc,
                      N=N, kmax=K, primes=len(PRIMES)) as rep:
        for H in range(Hmin, Hmax + 1):
            # gather per-prime sequences: cache-hit, or compute & bank the misses.
            by_p, missing = {}, []
            for p in allprimes:
                cached = ckpt.get_or_none(f"H{H}-p{p}")
                if cached is not None:
                    by_p[p] = {int(k): v for k, v in cached.items()}  # JSON keys -> int
                else:
                    missing.append(p)
            if missing:
                with Pool(min(nproc, len(missing))) as pool:
                    for p, by in pool.imap_unordered(
                            _slice_job, [(H, N, p, K) for p in missing]):
                        ckpt.save(f"H{H}-p{p}", by)   # durable the instant it lands
                        by_p[p] = by
            seqs_by_prime = [by_p[p] for p in PRIMES]
            val_by_k = by_p[VAL_PRIME]
            lines.append(f"## H={H}")
            h_nval = 0
            for k in sorted(seqs_by_prime[0]):
                seqs = [sb.get(k, [0] * (N + 1)) for sb in seqs_by_prime]
                r = recover_slice(seqs, val_by_k.get(k, [0] * (N + 1)), N)
                if r is None:
                    continue
                if r[0] == "insufficient":
                    pending.append((H, k, r[1]))
                    continue
                if r[0] == "order_disagree":
                    disagree.append((H, k, r[1]))
                    continue
                _, d, P, Q, ok = r
                nval += ok
                h_nval += int(ok)
                onset = next((i for i, v in enumerate(val_by_k.get(k, [])) if v), None)
                lines.append(f"H={H} k={k}  order={d}  onset_n={onset}  validated={ok}")
                lines.append(f"P: {P}")
                lines.append(f"Q: {Q}")
                lines.append(f"G_{{{H},{k}}}(x) = ({poly(P)}) / ({poly(Q)})")
            lines.append("")
            # one heartbeat per height (each is a full mod-p sweep across all primes,
            # the long pole); carries the slices validated and the running backlog.
            rep.beat(done=H - Hmin + 1, force=True, H=H, validated_k=h_nval,
                     pending=len(pending), disagree=len(disagree))
        if pending:
            lines.append(f"## Pending: order >= N/2 at N={N} (raise N to recover)")
            for H, k, d in pending:
                lines.append(f"#   H={H} k={k}  (BM order ~{d}, need ~{2*d+2} terms)")
        if disagree:
            lines.append("## Order disagreement across primes (investigate):")
            for H, k, Ls in disagree:
                lines.append(f"#   H={H} k={k}  orders={sorted(set(Ls))}")
        with open(out_path, "a" if Hmin > 1 else "w") as f:
            f.write("\n".join(lines) + "\n")
        rep.done(result=nval, pending=len(pending), disagreements=len(disagree),
                 mode=("appended" if Hmin > 1 else "written"), out=out_path,
                 resumed=ckpt.n_resumed)
        ckpt.clear()   # result is durable now; drop the per-prime scaffolding


if __name__ == "__main__":
    main()
