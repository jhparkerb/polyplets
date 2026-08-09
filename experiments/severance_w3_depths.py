#!/usr/bin/env python3
"""Severance W3: below-onset defects at depth j from bounded-excess cluster weights.

Deliverable of docs/onset-defect-severance-plan.md Sec.3 W3.  Exposes

    D_series(j, K) -> [Fraction] of length K+1, entry k = D_j(k)

computed from independently enumerated cluster-weight families only.  Nothing
here reads the banked triangle, the wired P_k, or any defect series; the gate
experiments/severance_w3_gate.py owns that side of the comparison.

===========================================================================
1. The depth-j identity, derived from the proved chain identity
===========================================================================

docs/proofs/diagonal-law.md Step 2 (exact, proved):

    F = E_b (1-S)^(-1) E_t + P,     S = 3z + sigma,
    E_b = z (1 + sum_c W^b_c y^k_c z^l_c),   E_t = 1 + sum_c W^t_c y^k_c z^l_c,
    sigma = sum_c W_c y^k_c z^(l_c+1),       P = sum_c W^p_c y^k_c z^l_c,

the sums running over cluster types c = (s_1..s_l), s_i >= 2, with surplus
k_c = sum(s_i - 1) and l_c rows.  Define the *excess*

    e_c = k_c - l_c = sum (s_i - 2) >= 0,

zero exactly for all-pair stacks, 1 for one 3-row, 2 for one 4-row or two
3-rows, 3 for one 5-row / a 4-row and a 3-row / three 3-rows.

Step 4 gives  [y^k]F = R_k(z)/(1-3z)^(k+1), and expanding (1-S)^(-1) =
sum_m sigma^m (1-3z)^(-m-1),

    R_k(z) = sum_{m=0..k} [y^k](E_b sigma^m E_t)(z) (1-3z)^(k-m)
             + [y^k]P(z) (1-3z)^(k+1).                                   (A)

Degree bookkeeping, term by term (this is Step 4's count, kept exact instead
of bounded): a chain term with bottom type of excess e_b, m interior types of
total excess sum e_i, top type of excess e_t has z-degree exactly

    (1 + k_b - e_b) + sum (k_i - e_i + 1) + (k_t - e_t) = k + m + 1 - E,
    E := e_b + sum e_i + e_t,

and is multiplied by (1-3z)^(k-m), whose z^u term (u <= k-m) carries
C(k-m,u)(-3)^u.  So that term reaches z-degree 2k+1-E-(k-m-u): writing the
shortfall from the top degree as s,

    s = E + v,   v := k-m-u >= 0.                                        (B)

Likewise a pure term of excess e_p sits at degree k-e_p and is multiplied by
(1-3z)^(k+1), whose z^(k+1-v) term carries C(k+1,v)(-3)^(k+1-v); its shortfall
is s = e_p + v.  Hence, with

    A(k,E,m) := [y^k q^E] ( Bb(y,q) Sig(y,q)^m Bt(y,q) ),
    Sig(y,q) = sum_e q^e sum_{type: excess e} W_c y^k_c,
    Bb(y,q)  = 1 + sum_e q^e sum_{type: excess e} W^b_c y^k_c,   Bt = Bb,
    Pp(y,q)  = sum_e q^e sum_{type: excess e} W^p_c y^k_c,

the top j coefficients of R_k are the finite sums

    r_{2k+1-s} = sum_{E+v=s} sum_m A(k,E,m) C(k-m,v) (-3)^(k-m-v)
               + sum_{e+v=s} [y^k q^e]Pp  C(k+1,v) (-3)^(k+1-v).         (C)

(Bt = Bb as *aggregated* series: reversal of a type is a bijection preserving
(k,e) and exchanging W^b with W^t -- the palindromy used at depth 1, applied
to the aggregate rather than to a single type.)

Step 5 changes basis, R_k(z) = sum_i a_i (1-3z)^i, and the below-onset
correction polynomial is D(z) = sum_{m>=0} a_{k+1+m} (1-3z)^m, so with
D_j(k) = [z^(k+1-j)] D(z):

    a_{2k+1-t} = (-1)^(t+1) sum_{s=0..t} r_{2k+1-s} C(2k+1-s, 2k+1-t) 3^-(2k+1-s)
    D_j(k) = (-3)^(k+1-j) sum_{t=0..j-1} C(k-t, k+1-j) a_{2k+1-t}.       (D)

Only shortfalls s <= j-1 occur, so by (B) only types of total excess E <= j-1
contribute: **depth j needs exactly the cluster families of excess <= j-1**,
which is finitely many families per depth.  (Note the shape of the excess
budget: at depth 3 it is one 4-row *or* two 3-rows, not only 3-rows -- the
sub-claim in onset-defect-depth1-closed.md Sec.6, "all rows of size 2 except
up to j-1 rows of size 3", undercounts; the correct condition is
sum (s_i - 2) <= j-1.)

Check: at j = 1 only s = 0 survives, r_{2k+1} = sum_m A(k,0,m)(-3)^(k-m) +
Pp_0[k](-3)^(k+1), and (D) collapses to D_1(k) = r_{2k+1}/(-3)^(k+1) =
[y^k](Phat - B^2/(3+S)) -- identity (II) of onset-defect-depth1-closed.md,
recovered with no extra input.  main() asserts this against depth1_gap_walk.

===========================================================================
2. The weight families
===========================================================================

Weights are counted by the row-transfer DP of experiments/cluster_weight_dp.py
(same state, same normalization, same connectivity pruning), generalized so
that the row sizes are *chosen inside the DP*: one pass accumulates every type
of every excess level e <= EMAX at once, graded by (rows l, excess e), hence by
surplus k = l + e.  As there:

    interior W_c   = p below (fixed cell), cluster, q above (free),
    bottom edge W^b_c = cluster with q above, no p,
    pure W^p_c     = cluster alone,

i.e. q_end (count of q touching every pending component) versus bare_end (the
stack is already one component).

Span cap: a connected king animal's column projection is an interval, so a
c-cell animal spans at most c-1 columns; every row of a cluster of l rows and
excess e (plus p and q) therefore spans at most 2l+e+1.  Capping row spans
there is exact, not an approximation.

===========================================================================
3. Reach: depths 1-4 closed
===========================================================================

j = 1, 2, 3 are green at every banked cell (severance_w3_gate.py 3), costing
2 s and 79 s respectively for the e <= 1 and e <= 2 family passes at K = 19.

j = 4 needs excess 3, i.e. 5-cell rows (and 4-then-3, 3-then-3-then-3
adjacencies).  The identity (C)/(D) covers it unchanged -- the obstruction was
purely the size of the row-transfer state space in Python.  Measured on gympie
(2026-08-09): at K = 19 the span cap is 42, so a single 5-cell row has
C(42,4) = 111930 shapes, ~3e5 reachable states after partitions; the first DP
level alone lands 166254 interior states in 3.8 s, and level 2 -- where the
2 -> 5, 3 -> 4 and 4 -> 3 transition tables get built -- was still running at
3 min with the process at 1.5 GB (killed at 7 min rather than run a multi-hour
job).

Resolved 2026-08-09 by the standing rule for compute: cpp/severance_w3_families
.cpp is a straight port of families() and weights_for_type() below, enumerating
each row placement by pruned DFS rather than shape x offset and threading the
per-level expansion.  K = 19, emax = 3 costs 146 s wall / 494 MB on gympie
(10 threads) and is cached in results/severance_w3_families_K19_e3.txt, which
_load_table() picks up; every other call keeps the Python path.  Cross-checks:
the C++ agrees with the Python families() cell-for-cell at (K, emax) = (9, 3),
(19, 1) and (19, 2), and its own emax = 3 table (span cap 42) agrees with the
emax = 1, 2 tables (span caps 40, 41) wherever they overlap.
"""
import math
import os
import sys
import time
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------ row DP

def _row_partition(cells):
    """Blocks of one row's cells by within-row adjacency (labels 0,1,.. in order)."""
    lab = list(range(len(cells)))
    for i in range(len(cells) - 1):
        if cells[i + 1] - cells[i] <= 1:
            lab[i + 1] = lab[i]
    canon, out = {}, []
    for x in lab:
        if x not in canon:
            canon[x] = len(canon)
        out.append(canon[x])
    return tuple(out)


@lru_cache(maxsize=None)
def _shapes(t, span):
    """Normalized row shapes: t cells, first at 0, total span <= span."""
    if t == 1:
        return ((0,),)
    return tuple((0,) + c for c in combinations(range(1, span + 1), t - 1))


_TRANS = {}


def transitions(state, t, span):
    """All next rows of t cells: dict new_state -> multiplicity.

    Valid iff every pending component of `state` has a cell adjacent to the new
    row (an untouched component can never reconnect: king adjacency moves the
    row index by at most 1).  New blocks: within-row runs, merged through the
    old components they share.
    """
    key = (span, t, state)
    got = _TRANS.get(key)
    if got is not None:
        return got
    cells, part = state
    nb = max(part) + 1
    full = (1 << nb) - 1
    mask = {}
    for c, b in zip(cells, part):
        bit = 1 << b
        for y in (c - 1, c, c + 1):
            mask[y] = mask.get(y, 0) | bit
    xmin, xmax = cells[0], cells[-1]
    out = {}
    for sh in _shapes(t, span):
        sp = sh[-1]
        for a in range(xmin - sp - 1, xmax + 2):
            T = [a + d for d in sh]
            ms = [mask.get(y, 0) for y in T]
            tot = 0
            for m in ms:
                tot |= m
            if tot != full:
                continue
            lab = list(range(t))

            def find(x, lab=lab):
                while lab[x] != x:
                    lab[x] = lab[lab[x]]
                    x = lab[x]
                return x

            for i in range(t - 1):
                if T[i + 1] - T[i] <= 1:
                    ri, rj = find(i), find(i + 1)
                    if ri != rj:
                        lab[ri] = rj
            for i in range(t):
                if not ms[i]:
                    continue
                for jj in range(i + 1, t):
                    if ms[i] & ms[jj]:
                        ri, rj = find(i), find(jj)
                        if ri != rj:
                            lab[ri] = rj
            canon, npart = {}, []
            for i in range(t):
                r = find(i)
                if r not in canon:
                    canon[r] = len(canon)
                npart.append(canon[r])
            st = (tuple(y - T[0] for y in T), tuple(npart))
            out[st] = out.get(st, 0) + 1
    _TRANS[key] = out
    return out


def q_end(state):
    """Number of placements of the free walk cell q above closing the animal."""
    cells, part = state
    nb = max(part) + 1
    full = (1 << nb) - 1
    mask = {}
    for c, b in zip(cells, part):
        bit = 1 << b
        for y in (c - 1, c, c + 1):
            mask[y] = mask.get(y, 0) | bit
    return sum(1 for y, m in mask.items() if m == full)


def bare_end(state):
    """1 if the stack is already a single component (pure cluster), else 0."""
    return 1 if max(state[1]) == 0 else 0


def weights_for_type(v):
    """(W, W^b, W^t, W^p) for one cluster type, by the same DP -- validation only."""
    v = tuple(v)
    span = sum(v) + 2

    def run(seq, start_p):
        if start_p:
            dp = {((0,), (0,)): 1}
            seq_run = seq
        else:
            dp = {}
            for sh in _shapes(seq[0], span):
                dp[(sh, _row_partition(sh))] = 1
            seq_run = seq[1:]
        for t in seq_run:
            ndp = {}
            for st, c in dp.items():
                for st2, w in transitions(st, t, span).items():
                    ndp[st2] = ndp.get(st2, 0) + c * w
            dp = ndp
        return dp

    dp_i = run(v, True)
    dp_b = run(v, False)
    dp_t = run(tuple(reversed(v)), False)
    return (sum(c * q_end(st) for st, c in dp_i.items()),
            sum(c * q_end(st) for st, c in dp_b.items()),
            sum(c * q_end(st) for st, c in dp_t.items()),
            sum(c * bare_end(st) for st, c in dp_b.items()))


# ----------------------------------------------------------------- families

_FAM = {}

TABLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def _load_table(K, emax):
    """Cached C++ family table, or None.

    Written by build/severance_w3_families (cpp/severance_w3_families.cpp), a
    straight port of families() below: header line
    '# severance_w3_families K=<K> emax=<E>' then one 'e k sig bb pp' line per
    (excess, surplus) cell.  Only the e <= 3 / K = 19 pass needs it (section 3);
    everything else stays on the Python path.

    A table with K_table >= K and the same emax is usable: the span cap
    2*K+emax+1 only has to *exceed* the exact bound 2*l+e+1 for the l <= K rows
    that contribute, so cells k <= K are identical under either cap.  validate()
    checks that empirically against the banked weights and the gap walk.
    """
    for Kt in range(K, 40):
        path = os.path.join(TABLE_DIR, f"severance_w3_families_K{Kt}_e{emax}.txt")
        if not os.path.exists(path):
            continue
        sig = [[0] * (K + 1) for _ in range(emax + 1)]
        bb = [[0] * (K + 1) for _ in range(emax + 1)]
        pp = [[0] * (K + 1) for _ in range(emax + 1)]
        with open(path) as fh:
            head = fh.readline().split()
            assert head[:4] == ["#", "severance_w3_families", f"K={Kt}", f"emax={emax}"], \
                f"{path}: unexpected header {head}"
            for line in fh:
                if line.startswith("#"):
                    continue
                e, k, a, b, c = (int(x) for x in line.split())
                if k <= K:
                    sig[e][k], bb[e][k], pp[e][k] = a, b, c
        return sig, bb, pp
    return None


def families(K, emax, verbose=False):
    """Aggregated weight series by excess level.

    Returns (sig, bb, pp): sig[e][k] = sum of interior weights over all cluster
    types of surplus k and excess e; bb = bottom-edge, pp = pure.  Types with
    k > K or excess > emax are not generated.
    """
    key = (K, emax)
    if key in _FAM:
        return _FAM[key]
    cached = _load_table(K, emax)
    if cached is not None:
        _FAM[key] = cached
        return cached
    span = 2 * K + emax + 1
    sizes = [2 + d for d in range(emax + 1)]
    sig = [[0] * (K + 1) for _ in range(emax + 1)]
    bb = [[0] * (K + 1) for _ in range(emax + 1)]
    pp = [[0] * (K + 1) for _ in range(emax + 1)]
    dp_i = {(0, ((0,), (0,))): 1}
    dp_b = {}
    for ell in range(1, K + 1):
        t0 = time.time()
        n_i, n_b = {}, {}
        for t in sizes:
            de = t - 2
            for src, dst in ((dp_i, n_i), (dp_b, n_b)):
                for (e, st), c in src.items():
                    e2 = e + de
                    if e2 > emax or ell + e2 > K:
                        continue
                    for st2, w in transitions(st, t, span).items():
                        k2 = (e2, st2)
                        dst[k2] = dst.get(k2, 0) + c * w
            if ell == 1 and de <= emax and 1 + de <= K:
                for sh in _shapes(t, span):
                    k2 = (de, (sh, _row_partition(sh)))
                    n_b[k2] = n_b.get(k2, 0) + 1
        dp_i, dp_b = n_i, n_b
        for (e, st), c in dp_i.items():
            sig[e][ell + e] += c * q_end(st)
        for (e, st), c in dp_b.items():
            qe, be = q_end(st), bare_end(st)
            if qe:
                bb[e][ell + e] += c * qe
            if be:
                pp[e][ell + e] += c * be
        if verbose:
            print(f"   l={ell:2d}: states int={len(dp_i)} bare={len(dp_b)} "
                  f"[{time.time() - t0:.1f}s]", flush=True)
    _FAM[key] = (sig, bb, pp)
    return _FAM[key]


# ----------------------------------------------------------- series assembly

def _bimul(a, b, K, emax):
    """Product of two (emax+1) x (K+1) arrays, truncated in both gradings."""
    out = [[0] * (K + 1) for _ in range(emax + 1)]
    for e1 in range(emax + 1):
        r1 = a[e1]
        for e2 in range(emax + 1 - e1):
            r2 = b[e2]
            row = out[e1 + e2]
            for k1 in range(K + 1):
                c1 = r1[k1]
                if not c1:
                    continue
                for k2 in range(K + 1 - k1):
                    c2 = r2[k2]
                    if c2:
                        row[k1 + k2] += c1 * c2
    return out


def D_series(j, K, verbose=False):
    """[D_j(0), ..., D_j(K)] as exact Fractions, from the weight families."""
    emax = j - 1
    sig, bb, pp = families(K, emax, verbose=verbose)
    Bb = [row[:] for row in bb]
    Bb[0][0] += 1                                   # the empty edge term
    A = []                                          # A[m][E][k]
    cur = Bb
    for m in range(K + 1):
        A.append(_bimul(cur, Bb, K, emax))          # Bt = Bb (aggregate palindromy)
        cur = _bimul(cur, sig, K, emax)

    def r_coeff(k, s):
        tot = F(0)
        for E in range(s + 1):
            v = s - E
            for m in range(k + 1):
                if v > k - m:
                    continue
                a = A[m][E][k]
                if a:
                    tot += a * math.comb(k - m, v) * F(-3) ** (k - m - v)
        for e in range(min(s, emax) + 1):
            v = s - e
            c = pp[e][k]
            if c and v <= k + 1:
                tot += c * math.comb(k + 1, v) * F(-3) ** (k + 1 - v)
        return tot

    out = []
    for k in range(K + 1):
        if k + 1 - j < 0:
            out.append(F(0))
            continue
        r = {s: r_coeff(k, s) for s in range(j)}
        tot = F(0)
        for t in range(j):
            cb = math.comb(k - t, k + 1 - j) if k - t >= k + 1 - j else 0
            if not cb:
                continue
            a = F(0)
            for s in range(t + 1):
                a += (r[s] * math.comb(2 * k + 1 - s, 2 * k + 1 - t)
                      * F(1, 3) ** (2 * k + 1 - s))
            a *= (-1) ** (t + 1)
            tot += cb * a
        out.append(tot * F(-3) ** (k + 1 - j))
    return out


# --------------------------------------------------------------- validation

def validate(K=9, verbose=True):
    """Every check that does not touch the triangle, the law, or P_k."""
    from cluster_weight_dp import KNOWN_WEIGHTS, count_stack     # noqa: E402
    from depth1_gap_walk import walk_families                    # noqa: E402

    print("== per-type weights vs cluster_weight_dp.KNOWN_WEIGHTS (k <= 5)")
    for v, w in sorted(KNOWN_WEIGHTS.items()):
        got = weights_for_type(v)
        assert got == w, (v, got, w)
    print(f"   {len(KNOWN_WEIGHTS)} types, all four weights each  OK")

    print("== aggregated families vs results/severance_w1_weights_k9.txt")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "results", "severance_w1_weights_k9.txt")
    ref_sig, ref_bb, ref_bt, ref_pp = {}, {}, {}, {}
    ntypes = 0
    with open(path) as fh:
        for line in fh:
            f = line.split("\t")
            v = tuple(int(x) for x in f[0].split(","))
            k, e = sum(v) - len(v), sum(s - 2 for s in v)
            ntypes += 1
            for d, val in ((ref_sig, int(f[1])), (ref_bb, int(f[2])),
                           (ref_bt, int(f[3])), (ref_pp, int(f[4]))):
                d[(k, e)] = d.get((k, e), 0) + val
    emax = max(e for _, e in ref_sig)
    sig, bb, pp = families(K, min(emax, 3), verbose=verbose)
    ncell = 0
    for (k, e), val in sorted(ref_sig.items()):
        if k > K or e > 3:
            continue
        assert sig[e][k] == val, ("interior", k, e, sig[e][k], val)
        assert bb[e][k] == ref_bb[(k, e)], ("bottom", k, e)
        assert ref_bt[(k, e)] == ref_bb[(k, e)], ("palindromy", k, e)
        assert pp[e][k] == ref_pp[(k, e)], ("pure", k, e)
        ncell += 1
    print(f"   {ntypes} banked types aggregate into {ncell} (k,e) cells, "
          f"all four families exact  OK")

    print("== all-pairs families vs depth1_gap_walk.walk_families")
    fams = walk_families(K)
    for ell in range(1, K + 1):
        wi, wb, wp = fams[ell - 1]
        assert (sig[0][ell], bb[0][ell], pp[0][ell]) == (wi, wb, wp), ell
    print(f"   e = 0 series agree at l = 1..{K}  OK")


def holdouts(cases, verbose=True):
    """Fresh count_stack cross-checks: types no banked table contains (k >= 10)."""
    from cluster_weight_dp import count_stack                    # noqa: E402
    print("== fresh count_stack holdouts (k >= 10, absent from every banked table)")
    for v, which in cases:
        t0 = time.time()
        mine = weights_for_type(v)
        if which == "pure":
            ref, idx = count_stack(list(v)), 3
        elif which == "bottom":
            ref, idx = count_stack([1] + list(reversed(v))), 1
        else:
            ref, idx = count_stack([1] + list(v) + [1]), 0
        e = sum(s - 2 for s in v)
        assert mine[idx] == ref, (v, which, mine[idx], ref)
        print(f"   {str(v):20} e={e} {which:8} = {ref:<14} "
              f"[{time.time() - t0:.1f}s]  OK", flush=True)


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 19
    J = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    t0 = time.time()
    validate(K=min(K, 9))
    cases = [((2,) * 11, "pure"),                     # e = 0, k = 11
             ((3,) + (2,) * 9, "pure"),               # e = 1
             ((3,) + (2,) * 9, "bottom"),
             ((4,) + (2,) * 8, "pure"),               # e = 2, one 4-row
             ((3, 3) + (2,) * 7, "pure"),             # e = 2, two 3-rows
             ((5,) + (2,) * 7, "pure"),               # e = 3, one 5-row
             ((4, 3) + (2,) * 6, "pure"),             # e = 3, 4-row and 3-row
             ((3, 3, 3) + (2,) * 5, "pure"),          # e = 3, three 3-rows
             ((5,) + (2,) * 6, "pure"),               # e = 3, k = 10 (2026-08-09)
             ((3, 3, 3) + (2,) * 4, "pure")]          # e = 3, k = 10 (2026-08-09)
    holdouts([(v, w) for v, w in cases if sum(s - 2 for s in v) <= J - 1])

    print(f"\n== D_j series to k = {K}")
    from depth1_gap_walk import series_D1, walk_families         # noqa: E402
    D1ref = series_D1(walk_families(K), K)
    D1 = D_series(1, K)
    for k in range(1, K + 1):
        assert D1[k] == D1ref[k], (k, D1[k], D1ref[k])
    print(f"   j=1: identity (D) reproduces depth1_gap_walk (II) at k <= {K}  OK")
    for j in range(2, J + 1):
        t1 = time.time()
        Dj = D_series(j, K, verbose=True)
        print(f"   j={j}: D_{j}({j}..{min(j + 3, K)}) = "
              f"{[str(x) for x in Dj[j:j + 4]]}  [{time.time() - t1:.1f}s]",
              flush=True)
    print(f"\ntotal {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
