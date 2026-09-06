#!/usr/bin/env python3
"""Hex diagonal cells T_hex(n, n-k) for k <= 4, and the second route to hex A_4.

Purpose: `results/skeletonkey-parametric-master.md` gives hex `A_4 = 3915/4`
from the cluster weights alone, with nothing to check it against because there
is no wired hex `P_k` table.  This file supplies the other route: enumerate the
hex height triangle deep enough to fit `P_4` directly, then read `A_4` off the
cumulant `c_4` and compare.

Method: the same row-transfer DP as `experiments/hex_gas.py` (asymmetric hex
touch-up `x' in {x-1, x}`, state = row cells + connectivity partition +
surplus), rewritten so the surplus budget can reach 4.  `hex_gas.py` generates a
row transition by taking every subset of a window of width `spread + 2M + 1`;
at budget 4 that is C(30,5) subsets per state and does not finish.  Here the
new row is generated left to right with two prunes -- an old component whose
touch positions all lie left of the cursor can never be touched again, and the
cell budget is bounded -- which is exact, not heuristic: it enumerates the same
subsets, it just abandons dead prefixes.  The window half-width beyond the old
row's extent is a parameter, and `--converge` checks that widening it by one
changes nothing.

Target machine: gympie, single core, seconds to a few minutes; no RAM concern.
Exact integer arithmetic throughout.

    python3 experiments/hex_diag_deep.py --generate      # writes the data file
    python3 experiments/hex_diag_deep.py                 # fit + gate (fail-closed)
    python3 experiments/hex_diag_deep.py --converge      # window-width control

Data file: results/hex_diagonal_cells.txt, one `n H count` per line.
"""
import argparse
import os
import sys
import time
from collections import defaultdict
from fractions import Fraction as Fr
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hex_gas import A001207, brute, rowpart                        # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'results', 'hex_diagonal_cells.txt')

# Banked, from results/hex-diagonal-law.md.
P1 = lambda n: 9 * n - 15
P2 = lambda n: Fr(81 * n * n - 307 * n + 142, 2)
A_WEIGHTS = {1: Fr(9), 2: Fr(-37, 2), 3: Fr(32)}   # banked hex c_k slopes
A4_CLUSTER = Fr(3915, 4)                       # the one-route number under test


# ------------------------------------------------------------------ the walk



@lru_cache(maxsize=None)
def transitions(cells, part, budget, halo):
    """Every new row over the old row (cells, part), as (newcells, newpart, ds).

    A new cell `t` touches an old cell `c` iff `t == c` or `t == c - 1` (the hex
    up-neighbours of `(c, y)` are `(c, y+1)` and `(c-1, y+1)`).  Every old
    component must be touched, else it is sealed off below and the animal can
    never be connected.  `ds = len(new) - 1` is the surplus the row spends.
    """
    nb = len(set(part))
    reach = defaultdict(list)                  # position -> old components it touches
    last = {}                                  # component -> last position touching it
    for c, b in zip(cells, part):
        for t in (c - 1, c):
            reach[t].append(b)
            last[b] = max(last.get(b, t), t)
    lo, hi = cells[0] - 1 - halo, cells[-1] + halo
    out = []
    chosen = []

    def rec(p, untouched, left):
        if p > hi:
            if not untouched and chosen:
                out.append(tuple(chosen))
            return
        if any(last[b] < p for b in untouched):
            return
        rec(p + 1, untouched, left)                       # skip p
        if left:
            chosen.append(p)
            rec(p + 1, untouched - set(reach.get(p, ())), left - 1)
            chosen.pop()

    rec(lo, frozenset(range(nb)), budget + 1)
    res = []
    for T in out:
        n_new = len(T)
        lab = list(range(nb + n_new))

        def find(x):
            while lab[x] != x:
                lab[x] = lab[lab[x]]
                x = lab[x]
            return x

        def uni(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                lab[ra] = rb

        for j, t in enumerate(T):
            for b in reach.get(t, ()):
                uni(b, nb + j)
            if j and T[j] - T[j - 1] == 1:
                uni(nb + j - 1, nb + j)
        cmap, npart = {}, []
        for j in range(n_new):
            r = find(nb + j)
            cmap.setdefault(r, len(cmap))
            npart.append(cmap[r])
        sh = T[0]
        res.append((tuple(t - sh for t in T), tuple(npart), n_new - 1))
    return res



def hex_T_all(hmax, budget, halo):
    """{H: {n: T_hex(n, H)}} for H = 1 .. hmax and n = H .. H + budget, from ONE
    row sweep: after each row the connected states are harvested for that
    height and the sweep continues, so hmax heights cost hmax row steps
    rather than hmax(hmax+1)/2."""
    dp = defaultdict(int)
    for s in range(1, budget + 2):
        for T in _first_rows(s, halo):
            dp[(T, rowpart(T), s - 1)] += 1
    out = {}
    for H in range(1, hmax + 1):
        if H > 1:
            ndp = defaultdict(int)
            for (cells, part, sur), v in dp.items():
                for nc, np_, ds in transitions(cells, part, budget - sur, halo):
                    ndp[(nc, np_, sur + ds)] += v
            dp = ndp
        row = defaultdict(int)
        for (cells, part, sur), v in dp.items():
            if len(set(part)) == 1:
                row[H + sur] += v
        out[H] = dict(row)
    return out


def hex_T(H, budget, halo):
    """{n: T_hex(n, H)} for n = H .. H + budget (one height; see hex_T_all)."""
    return hex_T_all(H, budget, halo)[H]


def _first_rows(s, halo):
    """Sorted s-cell tuples starting at 0, internal gaps bounded by the halo."""
    res = []

    def rec(pref, left):
        if not left:
            res.append(tuple(pref))
            return
        for nxt in range(pref[-1] + 1, pref[-1] + 2 + halo):
            rec(pref + [nxt], left - 1)

    rec([0], s - 1)
    return res


# --------------------------------------------------------------- brute force



# ------------------------------------------------------------- fit and gate

def lagrange(pts):
    """Interpolating polynomial of the (x, y) points, as a coefficient list."""
    n = len(pts)
    coeffs = [Fr(0)] * n
    for i, (xi, yi) in enumerate(pts):
        basis = [Fr(1)]
        den = Fr(1)
        for j, (xj, _) in enumerate(pts):
            if j == i:
                continue
            den *= xi - xj
            basis = [Fr(0)] + basis
            for m in range(len(basis) - 1):
                basis[m] -= xj * basis[m + 1]
        for m, b in enumerate(basis):
            coeffs[m] += yi * b / den
    return coeffs


def evalp(coeffs, x):
    return sum(c * Fr(x) ** m for m, c in enumerate(coeffs))


def cumulant_slopes(P, kmax):
    """A_k = coefficient of n in c_k, where sum_k P_k(n) u^k = exp(sum_k c_k u^k).

    Series arithmetic in u over Q[n] represented as coefficient lists.
    """
    def pmul(a, b):
        out = [Fr(0)] * (kmax + 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b):
                    if i + j <= kmax and bj:
                        out[i + j] += ai * bj
        return out

    # log of the series G = sum_k P_k u^k (P_0 = 1) in Q[n][[u]]
    G = [[Fr(1)]] + [P[k] for k in range(1, kmax + 1)]
    C = [[Fr(0)] for _ in range(kmax + 1)]
    for k in range(1, kmax + 1):
        # k C_k = k G_k - sum_{j=1}^{k-1} j C_j G_{k-j}
        acc = [Fr(0)] * (2 * kmax + 2)
        for j in range(1, k):
            t = pmul([Fr(j) * c for c in C[j]], G[k - j])
            for m, v in enumerate(t):
                acc[m] += v
        term = [Fr(k) * g for g in G[k]]
        term += [Fr(0)] * (len(acc) - len(term))
        C[k] = [(term[m] - acc[m]) / k for m in range(len(acc))]
    return C


def load():
    cells = {}
    with open(DATA) as fh:
        for line in fh:
            line = line.split('#')[0].strip()
            if not line:
                continue
            n, H, v = line.split()
            cells[(int(n), int(H))] = int(v)
    return cells


def generate(kmax, hmax, halo):
    t0 = time.time()
    tot, TB = brute(9)
    assert [tot[n] for n in sorted(tot)] == A001207, 'brute != A001207'
    rows = []
    t1 = time.time()
    table = hex_T_all(hmax, kmax, halo)
    print(f"  one sweep to H={hmax}: {time.time() - t1:.2f}s", flush=True)
    for H in range(1, hmax + 1):
        vals = table[H]
        for k in range(kmax + 1):
            n = H + k
            if (n, H) in TB or n <= 9:
                assert vals.get(n, 0) == TB.get((n, H), 0), ('brute', n, H)
            rows.append((n, H, vals.get(n, 0)))
        print(f"  H={H:2d}  { {k: vals.get(H + k, 0) for k in range(kmax + 1)} }", flush=True)
    with open(DATA, 'w') as fh:
        fh.write("# T_hex(n, H): fixed polyhexes of n cells, bounding-box height H.\n")
        fh.write("# Row-transfer DP, experiments/hex_diag_deep.py --generate.\n")
        fh.write("# n H count\n")
        for n, H, v in rows:
            fh.write(f"{n} {H} {v}\n")
    print(f"wrote {DATA} ({len(rows)} cells, {time.time() - t0:.1f}s)")


def fit(cells, kmax, verbose=True):
    """P_k from T_hex(n, n-k) = P_k(n) 2^(n-1-3k), with holdouts."""
    P, holdouts = {}, 0
    for k in range(1, kmax + 1):
        pts = []
        for (n, H), v in sorted(cells.items()):
            if n - H != k or n < 2 * k + 1:
                continue
            pts.append((n, Fr(v) / Fr(2) ** (n - 1 - 3 * k)))
        assert len(pts) >= k + 1, f'k={k}: {len(pts)} in-onset cells, need {k + 1}'
        c = lagrange(pts[:k + 1])
        for x, y in pts[k + 1:]:
            if evalp(c, x) != y:
                raise SystemExit(f"FAIL: P_{k} misses the holdout at n={x}")
            holdouts += 1
        P[k] = c
        if verbose:
            print(f"  P_{k} = {' + '.join(f'{v}*n^{m}' for m, v in enumerate(c) if v)}"
                  f"   ({len(pts) - k - 1} holdouts)")
    return P, holdouts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--generate', action='store_true')
    ap.add_argument('--converge', action='store_true')
    ap.add_argument('--kmax', type=int, default=6)
    ap.add_argument('--hmax', type=int, default=20)
    ap.add_argument('--halo', type=int, default=6)
    a = ap.parse_args()

    if a.converge:
        print(f"== window control: halos {a.halo} and {a.halo + 1} must agree")
        for H in range(1, 9):
            u = hex_T(H, a.kmax, a.halo)
            assert u == hex_T(H, a.kmax, a.halo + 1), H
            print(f"  H={H}  {u}  OK")
        print("halo-independent  OK")
        return 0

    if a.generate:
        generate(a.kmax, a.hmax, a.halo)
        return 0

    cells = load()
    print("== fit P_k on the hex diagonal, T_hex(n, n-k) = P_k(n) 2^(n-1-3k)")
    P, hold = fit(cells, a.kmax)
    print(f"  {hold} holdout cells, all exact")

    print("== control: P_1, P_2 against results/hex-diagonal-law.md")
    for n in range(3, 20):
        assert evalp(P[1], n) == P1(n), ('P_1', n)
        assert evalp(P[2], n) == P2(n), ('P_2', n)
    print("  P_1 = 9n-15, P_2 = (81n^2-307n+142)/2  OK")

    print("== cumulants: c_k(n) must be linear in n, slope A_k")
    C = cumulant_slopes(P, a.kmax)
    A = {}
    for k in range(1, a.kmax + 1):
        c = C[k]
        for m in range(2, len(c)):
            if c[m] != 0:
                raise SystemExit(f"FAIL: c_{k} is not linear in n (n^{m} = {c[m]})")
        A[k] = c[1]
        print(f"  A_{k} = {A[k]}   B_{k} = {c[0]}")
    for k, want in A_WEIGHTS.items():
        if A[k] != want:
            raise SystemExit(f"FAIL: A_{k} = {A[k]}, master file says {want}")
    print("  A_1 = 9, A_2 = -37/2, A_3 = 32 match the banked slopes  OK")

    print("== the test: hex A_4 against the cluster-weight prediction 3915/4")
    if A[4] != A4_CLUSTER:
        raise SystemExit(f"FAIL: enumerated A_4 = {A[4]}, weights give {A4_CLUSTER}")
    print(f"  A_4 = {A[4]} = {float(A[4])}  -- two routes agree  OK")

    print("== RED: perturbing one enumerated cell must break the fit")
    bad = dict(cells)
    key = (13, 9)
    assert key in bad
    bad[key] += 2 ** (13 - 1 - 12)
    try:
        Pb, _ = fit(bad, a.kmax, verbose=False)
        Cb = cumulant_slopes(Pb, a.kmax)
        broke = any(Cb[k][m] != 0 for k in range(1, a.kmax + 1)
                    for m in range(2, len(Cb[k]))) or Cb[4][1] != A4_CLUSTER
    except SystemExit:
        broke = True
    if not broke:
        raise SystemExit("FAIL: RED control did not fire")
    print("  perturbed T_hex(13,9) breaks the fit  OK")
    return 0


if __name__ == '__main__':
    sys.exit(main())
