#!/usr/bin/env python3
"""FEASIBILITY PROBE -- MPS/entanglement of the transfer-matrix frontier.

Reads a dumped frontier ({signature -> exact count}) from dump_frontier.cpp,
reshapes the amplitude vector into a matrix by splitting each signature string
at a boundary cut, and computes the SVD across that cut.

The frontier is a vector psi(sig) over signatures. A signature is H boundary
labels + 2 touch flags. We treat psi as living on a 1-D chain of the H boundary
sites. A bipartition at cut position c splits the H sites into left = sites
[0,c) and right = sites [c,H); the two touch flags are appended to the right
block (they are global bits; putting them on one side only inflates that side's
index space slightly and can only INCREASE apparent rank -> conservative).

M[L, R] = psi( left_bytes(L) ++ right_bytes(R) ++ flags(R) ), densified over the
DISTINCT left-tuples (rows) and right-tuples-with-flags (columns) that actually
occur. sig <-> (L, R) is a bijection (just splitting the byte string), so this is
the exact TT/MPS reshape at the cut. rank(M) is the exact MPS bond dimension chi
required at that cut; the singular-value decay says how far truncation can shrink
it.

chi_eff(epsilon) = #{ sigma_i : sigma_i > epsilon * sigma_max }.
MPS cost model: H * chi^2 vs current frontier size (= len(psi)). MPS wins iff
chi_eff stays small (poly in H) while the frontier grows ~ exponentially.
"""

import sys
import numpy as np


def load(path):
    with open(path) as f:
        header = f.readline().split()
        H = int(header[1]); col = int(header[3])
        maxn = int(header[5]); nstates = int(header[7])
        sigs = np.empty((nstates, H + 2), dtype=np.int16)
        vals = np.empty(nstates, dtype=np.float64)
        for i, line in enumerate(f):
            left, right = line.split("|")
            b = left.split()
            sigs[i, :] = [int(x) for x in b]
            vals[i] = float(right.strip())
    return H, col, maxn, sigs, vals


def build_matrix(H, sigs, vals, cut):
    """Reshape psi into M by splitting each signature at boundary site `cut`.
    Left index = bytes[0:cut]; right index = bytes[cut:H] plus the 2 flags."""
    left_keys = {}
    right_keys = {}
    triples = []
    for i in range(sigs.shape[0]):
        row = sigs[i]
        lk = row[0:cut].tobytes()
        rk = np.concatenate([row[cut:H], row[H:H + 2]]).tobytes()
        li = left_keys.setdefault(lk, len(left_keys))
        ri = right_keys.setdefault(rk, len(right_keys))
        triples.append((li, ri, vals[i]))
    nL, nR = len(left_keys), len(right_keys)
    M = np.zeros((nL, nR), dtype=np.float64)
    for li, ri, v in triples:
        M[li, ri] = v  # bijection: each (li,ri) hit at most once
    return M


def chi_eff(sv, eps):
    if sv.size == 0:
        return 0
    return int(np.count_nonzero(sv > eps * sv[0]))


def probe(path, cuts=None):
    H, col, maxn, sigs, vals = load(path)
    N = len(vals)
    print(f"\n=== {path}: H={H} col={col} maxn={maxn} frontier_states={N} ===")
    if cuts is None:
        cuts = sorted(set([H // 2, max(1, H // 2 - 2), min(H - 1, H // 2 + 2),
                           max(1, H // 4), min(H - 1, 3 * H // 4)]))
    eps_list = [1e-3, 1e-6, 1e-9]
    results = {}
    for c in cuts:
        M = build_matrix(H, sigs, vals, c)
        sv = np.linalg.svd(M, compute_uv=False)
        sv = sv[sv > 0]
        full_rank = int(np.count_nonzero(sv > 1e-12 * sv[0]))
        ce = {e: chi_eff(sv, e) for e in eps_list}
        results[c] = (M.shape, full_rank, ce, sv)
        print(f"  cut c={c:2d}: M={M.shape[0]}x{M.shape[1]}  "
              f"exact_rank={full_rank}  "
              f"chi_eff(1e-3)={ce[1e-3]:4d}  "
              f"chi_eff(1e-6)={ce[1e-6]:4d}  "
              f"chi_eff(1e-9)={ce[1e-9]:4d}  "
              f"MPS_cost(H*chi^2 @1e-6)={H*ce[1e-6]**2}")
    # spectrum at the central cut
    cmid = H // 2
    sv = results[cmid][3]
    print(f"  -- singular-value decay at central cut c={cmid} "
          f"(sigma_i/sigma_max), first 24:")
    ratios = sv / sv[0]
    line = " ".join(f"{r:.2e}" for r in ratios[:24])
    print("     " + line)
    return H, N, results


if __name__ == "__main__":
    paths = sys.argv[1:]
    summary = []
    for p in paths:
        H, N, res = probe(p)
        cmid = H // 2
        _, rank, ce, _ = res[cmid]
        summary.append((H, N, rank, ce[1e-3], ce[1e-6], ce[1e-9]))
    print("\n=== SUMMARY (central cut) ===")
    print(f"{'H':>3} {'frontier':>10} {'exact_rank':>11} "
          f"{'chi(1e-3)':>10} {'chi(1e-6)':>10} {'chi(1e-9)':>10} "
          f"{'MPS H*chi^2(1e-6)':>18} {'ratio front/MPS':>16}")
    for H, N, rank, c3, c6, c9 in summary:
        mps = H * c6 * c6
        print(f"{H:>3} {N:>10} {rank:>11} {c3:>10} {c6:>10} {c9:>10} "
              f"{mps:>18} {N / max(mps,1):>16.2f}")
