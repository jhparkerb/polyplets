#!/usr/bin/env python3
"""Head-check the banked fixed-height GFs against the exact triangle, n <= 40.

results/fixed_height_gfs.txt banks G_H(x) = P_H(x)/Q_H(x) for H = 1..11, with
G_H = sum_n T(n,H) x^n (fixed polyplets of n cells, bbox height exactly H).
H = 1..10 are flagged validated=True; H = 11 is validated=False and behaves
anomalously in the root structure (results/anisotropic-not-dfinite.md).

This checks the only thing the exact triangle can check: the HEAD of the series.
Exact integer series division P/Q (Q[0] = 1, so no fractions ever appear) using
only the first NMAX+1 coefficients of P and Q -- tails beyond x^NMAX cannot
influence coefficients <= NMAX, so the degree-13381 polynomials are never
materialized. Coefficient n is compared against T(n,H) from results/triangle.txt
for every n = H..40; the vanishing of coefficients n < H is checked too.

Fails closed: any parse surprise, any missing cell, or any mismatch exits 1.

Run:  python3 experiments/gf_head_check.py [gf_file]
      (the optional argument points at an alternate/corrupted GF file; the
       RED control in results/gf-head-check.md uses it.)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GF_FILE = os.path.join(ROOT, "results", "fixed_height_gfs.txt")
TRIANGLE = os.path.join(ROOT, "results", "triangle.txt")
NMAX = 40


def head_coeffs(s, k):
    """First k integers of a '[c0, c1, ...]' list literal, without parsing the
    rest of the line (these lists run to degree 13381 / 12 MB per line)."""
    s = s.strip()
    if not s.startswith("["):
        raise ValueError(f"not a coefficient list: {s[:40]!r}")
    out = []
    i = 1
    while len(out) < k:
        j = s.find(",", i)
        end = j if j != -1 else s.find("]", i)
        if end < 0:
            raise ValueError("unterminated coefficient list")
        tok = s[i:end].strip()
        if not tok:
            break
        out.append(int(tok))
        if j < 0:
            break
        i = j + 1
    return out


def load_gfs(path, k):
    """H -> (order, validated, P head, Q head), heads truncated to k coeffs."""
    gfs = {}
    H = order = validated = None
    P = None
    with open(path) as f:
        for line in f:
            m = re.match(r"H=(\d+)\s+order=(\d+)\s+validated=(True|False)", line)
            if m:
                H, order, validated = int(m.group(1)), int(m.group(2)), m.group(3) == "True"
                P = None
                continue
            if line.startswith("P:"):
                if H is None:
                    raise ValueError("P: line before any H= header")
                P = head_coeffs(line[2:], k)
            elif line.startswith("Q:"):
                if H is None or P is None:
                    raise ValueError(f"Q: line out of order at H={H}")
                Q = head_coeffs(line[2:], k)
                if not Q or Q[0] != 1:
                    raise ValueError(f"H={H}: Q[0] != 1 (got {Q[:1]})")
                gfs[H] = (order, validated, P, Q)
                P = None
    if not gfs:
        raise ValueError(f"no generating functions parsed from {path}")
    return gfs


def series_div(P, Q, nmax):
    """Power-series coefficients of P/Q up to x^nmax, exact integers (Q[0]=1)."""
    c = []
    for n in range(nmax + 1):
        v = P[n] if n < len(P) else 0
        for k in range(1, min(n, len(Q) - 1) + 1):
            if Q[k]:
                v -= Q[k] * c[n - k]
        c.append(v)
    return c


def load_triangle(path):
    T = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        n, H, v = line.split()
        T[(int(n), int(H))] = int(v)
    return T


def main():
    gf_file = sys.argv[1] if len(sys.argv) > 1 else GF_FILE
    gfs = load_gfs(gf_file, NMAX + 1)
    T = load_triangle(TRIANGLE)

    print(f"GF file:   {gf_file}")
    print(f"triangle:  {TRIANGLE}   (n <= {NMAX})")
    print()
    print("  H  order  validated  cells  match  low0  first mismatch")
    bad = 0
    for H in sorted(gfs):
        order, validated, P, Q = gfs[H]
        c = series_div(P, Q, NMAX)
        cells = match = 0
        first = None
        for n in range(H, NMAX + 1):
            if (n, H) not in T:
                raise ValueError(f"triangle has no cell T({n},{H})")
            want = T[(n, H)]
            cells += 1
            if c[n] == want:
                match += 1
            elif first is None:
                first = (n, c[n], want)
        # exact-height means no polyplet of n < H cells: those coefficients vanish
        low0 = all(c[n] == 0 for n in range(0, H))
        if first is None and not low0:
            first = (min(n for n in range(0, H) if c[n]), "nonzero", 0)
        if first:
            bad += 1
            n, got, want = first
            note = f"n={n}: GF {got} != triangle {want}"
        else:
            note = "-"
        print(f" {H:2d}  {order:5d}  {str(validated):9s}  {cells:5d}  {match:5d}  "
              f"{'yes' if low0 else 'NO':4s}  {note}")

    print()
    if bad:
        print(f"MISMATCH: {bad} height(s) disagree with the exact triangle")
        return 1
    print(f"OK: all {len(gfs)} heights reproduce T(n,H) exactly for n <= {NMAX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
