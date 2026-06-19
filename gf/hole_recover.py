#!/usr/bin/env python3
"""Recover the rational GF G_{H,k}(x) = sum_n B_{H,k}(n) x^n for fixed strip
height H and fixed hole count k, where B_{H,k}(n) = # height-exactly-H polyplets
of n cells with exactly k enclosed holes (primary 4-connected-background
convention). Each (H,k) slice is a [q^k] coefficient of the rational bivariate
G_H(x,q), hence itself C-finite -> rational and exact.

Terms come from the single-height holes sweep (build/tma_holes, the #5(a)
--only-height path): one LOW strip height sweeps cheaply to high n. Recovery is
exact (Berlekamp-Massey over Q, reused from recover.py); a slice is trusted only
when the recurrence fit on a prefix reproduces the held-out tail. The u64 engine
limits the reach: counts overflow ~2^63 at modest n, so high H (order > ~20)
needs the mod-p holes engine (#5(b), deferred). H=3,4 recover cleanly here.

Usage:  python3 gf/hole_recover.py [Hmax] [N]   (defaults: Hmax=4, N=60)

Confidence note: G_{3,1} (order 12) was independently confirmed by expanding the
recovered P/Q as a power series and matching the engine's B_{3,1}(n) for every
exact n; at n=37 the series gives 20893569315475265294 (> 2^64) while the engine
prints a wrapped value -- the GF supplies the correct term the u64 engine cannot,
which is exactly the overflow wall that motivates the mod-p engine (#5b).
"""
import sys, os
import subprocess
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recover import berlekamp_massey, integerize_pair, poly  # exact BM + assembly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMA = os.path.join(ROOT, "build", "tma_holes")  # holes-capable engine


def _truncate_at_wrap(seq):
    """Cut a single B_{H,k}(0..N) at the first u64 wrap. For fixed (H,k) the
    count is non-decreasing once it onsets (more cells => at least as many ways),
    so a drop below the previous nonzero term signals the engine's u64 counter
    wrapped past 2^64. Same heuristic recover.py uses per fixed-height row."""
    onset = next((i for i, v in enumerate(seq) if v), len(seq))
    safe = len(seq)
    for i in range(onset + 1, len(seq)):
        if seq[i] and seq[i] < seq[i - 1]:
            safe = i
            break
    return seq[:safe]


def slices(H, N):
    """Return by_k: by_k[k] = [B_{H,k}(0..)] truncated per slice at its own u64
    wrap (slices overflow at different n, so truncating each independently keeps
    the most exact terms from each)."""
    out = subprocess.run([TMA, "square8", str(N), "--holes", "--only-height",
                          str(H)], capture_output=True, text=True).stdout
    raw = {}        # (k, n) -> count
    ks = set()
    for line in out.splitlines():
        p = line.split()
        if len(p) != 4:
            continue
        _, n, k, c = (int(x) for x in p)
        raw[(k, n)] = c
        ks.add(k)
    by_k = {}
    for k in sorted(ks):
        full = [raw.get((k, n), 0) for n in range(N + 1)]
        by_k[k] = _truncate_at_wrap(full)
    return by_k


def recover(seq):
    """(P, Q, order, validated) for one slice, or None if too few terms. Mirrors
    recover.py's hold-out logic: fit on a prefix, accept only if it reproduces
    the tail; else fall back to the all-terms fit (reported unvalidated)."""
    nz = sum(1 for v in seq if v)
    if nz < 4:
        return None
    Cfull, Lfull = berlekamp_massey(seq)
    hold = len(seq) - Lfull >= Lfull + 2
    fit = seq[: len(seq) - max(2, len(seq) // 8)] if hold else seq
    C, L = berlekamp_massey(fit)

    def rec(s, k):
        return -sum(C[i] * Fr(s[k - i]) for i in range(1, len(C)))

    validated = hold and all(rec(seq, k) == seq[k] for k in range(L, len(seq)))
    if not validated:
        C, L = Cfull, Lfull
    order = max((i for i, c in enumerate(C) if c != 0), default=0)
    Praw = [sum(C[i] * Fr(seq[k - i]) for i in range(min(k, len(C) - 1) + 1))
            for k in range(len(C))]
    P, Q = integerize_pair(Praw, [Fr(c) for c in C])
    return P, Q, order, validated


def main():
    Hmax = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    out_path = os.path.join(ROOT, "results", "hole_gfs.txt")
    lines = [
        "# Fixed-(height, #holes) polyplet generating functions",
        "#   G_{H,k}(x) = P/Q = sum_n B_{H,k}(n) x^n,",
        "#   B_{H,k}(n) = # height-exactly-H n-cell polyplets with exactly k holes",
        "#   (primary 4-connected-background convention).",
        "# Recovered by Berlekamp-Massey over Q from the single-height holes sweep;",
        "# 'validated' = held-out tail reproduced. P,Q coeffs low->high, Q[0]=1.",
        "",
    ]
    pending = []   # (H, k, exact_terms) needing the mod-p engine (#5b)
    for H in range(1, Hmax + 1):
        by_k = slices(H, N)
        lines.append(f"## H={H}")
        for k in sorted(by_k):
            seq = by_k[k]
            r = recover(seq)
            if r is None:
                continue
            P, Q, order, validated = r
            onset = next((i for i, v in enumerate(seq) if v), None)
            if not validated:
                # The fit is an overfit on too few exact terms (u64 wraps before
                # enough terms accrue); don't emit a bogus closed form.
                pending.append((H, k, len(seq)))
                continue
            lines.append(f"H={H} k={k}  order={order}  onset_n={onset}  "
                         f"validated [{len(seq)} exact terms]")
            lines.append(f"P: {P}")
            lines.append(f"Q: {Q}")
            lines.append(f"G_{{{H},{k}}}(x) = ({poly(P)}) / ({poly(Q)})")
        lines.append("")
    if pending:
        lines.append("## Not recoverable in u64 (need the mod-p holes engine, #5b)")
        lines.append("# Listed (H, k, #exact terms available before u64 wrap). The")
        lines.append("# minimal recurrence order exceeds what these terms pin down.")
        for H, k, t in pending:
            lines.append(f"#   H={H} k={k}  ({t} exact terms)")
    text = "\n".join(lines)
    with open(out_path, "w") as f:
        f.write(text + "\n")
    print(text)
    print(f"\n-> wrote {out_path}")


if __name__ == "__main__":
    main()
