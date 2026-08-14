#!/usr/bin/env python3
"""r3_lift_snf_probe.py -- Coin Lift gate G2, in its well-posed form.

docs/coin-lift-plan.md §2 G2 asks for "the Z/4 free rank" of the Hankel
matrices and kills the program if it "jumps toward the mod-p curve".  As
written that gate can never fire: the free rank over Z/4 -- the number of
invariant factors that are units mod 4 -- counts the ODD invariant factors,
and a factor is odd iff it survives reduction mod 2, so it is identically the
GF(2) rank the ladder already measured.  Nothing can jump.

The object that does decide the gate is the minimal number of generators of
the Hankel column module over Z/2^k, which is the floor on the dimension of
any Z/2^k-linear realization -- the exact analogue, over the ring, of the
field rank:

    mu_k(H) = #{ invariant factors d_i of the observability matrix
                 with v_2(d_i) < k }

    mu_1 = rank over GF(2)          (the collapse, 0.44 * 2^H measured)
    mu_inf = rank over Q >= rank over F_p   (the mod-p curve, ~2.45x/height)

and mu_1 <= mu_2 <= mu_3 <= ... <= mu_inf.  G2 reads mu_2 and mu_3: Coin Lift
to Z/4 or Z/8 is worth building only if two or three deterministic bits per
cell cost a dimension near mu_1 rather than near mu_inf.

  PASS  mu_2 (and mu_3) stay near mu_1 ~ 0.44 * 2^H
  KILL  mu_2 tracks the mod-p curve -- the collapse is a characteristic-2
        degeneracy (x + x = 0), dies mod 4, and only Coin Flip / Coin Roll /
        Biased Coin Flip survive.

Method.  The automaton (built here from the definition of king-connectivity by
r3_inv_rank_probe.build_automaton, not from the incumbent engine) is
deterministic, so every residual functional a o delta_w is a 0/1 vector and
the Hankel column module is the Z-module they span.  Closure is computed mod
2^K with echelon pruning: a residual that reduces to zero against the rows
kept so far is a Z/2^K-combination of them, so its own successors are too and
it need not be expanded.  Elementary divisors are then counted by 2-adic
elimination -- clear all unit pivots, halve the remainder, repeat -- which
over the local ring Z/2^K yields exactly the valuation profile of the
invariant factors of valuation < K.

Checks (fail-closed; the script exits nonzero unless every GREEN passes and
every RED fires):
  GREEN  mu_1 equals the banked GF(2) ladder 6,15,27,58,112,229 at H=4..9;
  GREEN  mu_1 equals obs_rank_gf2_x1's own value, a second and independently
         written elimination (bitset over GF(2) vs local elimination mod 2^K);
  GREEN  mu_K equals A-S1's measured mod-p rank where both exist -- if it did
         not, either the closure is incomplete or invariant factors of
         valuation >= K exist, and both need saying;
  RED    the red=True stencil (one diagonal dropped from the merge) must move
         the mu profile; an identical profile means the probe is not reading
         the connectivity rule at all.

Usage:   r3_lift_snf_probe.py [MAXH] [K] [P]    default MAXH=9, K=8, P=2\n         P > 2 asks the same question in another characteristic: is the\n         collapse a char-2 accident, or does some small prime also thin the\n         module?  mu_1 is then the rank over F_P.
Cost:    seconds to H=8, ~minutes at H=9 (gympie).  Single core, <2 GB.
"""

import sys
import time
import numpy as np

from r3_inv_rank_probe import (build_automaton, obs_rank_gf2_x1, AS1_MODP,
                               motzkin)

BANKED_GF2 = {4: 6, 5: 15, 6: 27, 7: 58, 8: 112, 9: 229}


def vp(x, P):
    """P-adic valuation of a nonzero int."""
    j = 0
    while x % P == 0:
        x //= P
        j += 1
    return j


def module_generators(delta, accept, K, P=2):
    """Generating set, mod 2^K, of the Hankel column module: the Z/2^K-module
    spanned by all residuals a o delta_w.

    Returns the list of residuals kept.  A residual is kept unless it reduces
    to zero against those already kept, in which case it lies in their span
    and -- the successor map g -> g o delta_m being linear -- so does every
    functional it could generate."""
    M = P ** K
    n, na = delta.shape
    basis = {}          # pivot column -> (valuation, row), row[pivot] = 2^val * unit
    kept = []

    def reduce_add(row):
        """Reduce row against the basis, which is kept in echelon form: every
        basis row is zero before its pivot column.  Returns True iff the basis
        changed, which happens exactly when the row was not already in the
        module the basis spans -- either it reaches a fresh pivot column, or
        it reaches an occupied one carrying a shallower 2-adic valuation, and
        no combination of the rows can match that (only the row pivoted at
        that column is nonzero there, and its valuation is deeper)."""
        row = row.copy()
        changed = False
        for c in range(n):
            x = int(row[c]) % M
            if x == 0:
                continue
            vx = vp(x, P)
            while c in basis:
                vb, brow = basis[c]
                if vb > vx:
                    basis[c] = (vx, row)          # keep the shallower pivot
                    changed = True
                    row, vx, x = brow, vb, int(brow[c]) % M
                    continue
                u = (x // P**vb) * pow(int(brow[c]) // P**vb, -1, M) % M
                row = (row - u * brow) % M
                x = int(row[c]) % M
                if x == 0:
                    break
                vx = vp(x, P)
            if x == 0:
                continue
            basis[c] = (vx, row)
            return True
        return changed

    frontier = [accept.astype(np.int64) % M]
    new = reduce_add(frontier[0])
    if new:
        kept.append(frontier[0])
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=np.int64)
                ok = d >= 0
                h[ok] = g[d[ok]]
                new = reduce_add(h)
                if new:
                    kept.append(h)
                    nxt.append(h)
        frontier = nxt
    return kept


def invariant_valuations(rows, K, P=2):
    """counts[j] = number of invariant factors of valuation j, j < K, of the
    integer matrix whose rows generate the module (read mod 2^K).

    2-adic elimination over the local ring Z/2^K: clear every unit pivot,
    halve what is left, repeat.  A factor of valuation >= K is invisible mod
    2^K and is not counted -- which is exactly what mu_k for k <= K needs."""
    if not rows:
        return [0] * K
    A = (np.array(rows, dtype=np.int64) % P ** K)
    counts = [0] * K
    live_r = np.ones(A.shape[0], dtype=bool)
    live_c = np.ones(A.shape[1], dtype=bool)
    for j in range(K):
        M = P ** (K - j)
        A %= M
        while True:
            sub = A[np.ix_(live_r, live_c)]
            if sub.size == 0:
                break
            odd = (sub % P != 0)
            if not odd.any():
                break
            ri, ci = np.argwhere(odd)[0]
            r = np.flatnonzero(live_r)[ri]
            c = np.flatnonzero(live_c)[ci]
            inv = pow(int(A[r, c]) % M, -1, M)
            prow = (A[r] * inv) % M
            col = A[:, c].copy()
            col[r] = 0
            col[~live_r] = 0
            A = (A - np.outer(col, prow)) % M
            live_r[r] = False
            live_c[c] = False
            counts[j] += 1
        if not live_r.any() or not live_c.any():
            break
        A //= P
    return counts


def mu_profile(H, K, P=2, red=False):
    t0 = time.time()
    order, delta, accept, masks = build_automaton(H, red=red)
    assert red or len(order) == motzkin(H + 1) - 1, (H, len(order))
    gens = module_generators(delta, accept, K, P)
    counts = invariant_valuations(gens, K, P)
    mu = [sum(counts[:k]) for k in range(1, K + 1)]
    return dict(H=H, states=len(order), gens=len(gens), counts=counts, mu=mu,
                wall=time.time() - t0)


def main():
    maxh = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    P = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    fail = 0

    print(f"Coin Lift G2 -- mu_k(H) = #invariant factors with v_{P} < k, "
          f"p={P}, K={K}")
    print(f"mu_1 = rank over F_{P} (the collapse, if any); "
          f"mu_K ~ rank_Q (the generic curve)")
    print()
    print("H  states  gens  " + "  ".join(f"mu_{k}" for k in range(1, K + 1))
          + "   GF2  modp   mu_2/mu_1  mu_1/2^H   wall")

    for H in range(4, maxh + 1):
        r = mu_profile(H, K, P)
        banked = BANKED_GF2.get(H)
        modp = AS1_MODP.get(H)
        mus = "  ".join(str(m) for m in r['mu'])
        print(f"{H}  {r['states']}  {r['gens']}  {mus}   {banked}  {modp}   "
              f"{r['mu'][1] / r['mu'][0]:.3f}  {r['mu'][0] / 2**H:.3f}  "
              f"({r['wall']:.1f}s)")

        if P == 2:
            gf2 = obs_rank_gf2_x1(*build_automaton(H)[1:3])
            if r['mu'][0] != gf2:
                print(f"  GREEN FAILED H={H}: mu_1={r['mu'][0]} != "
                      f"obs_rank_gf2_x1={gf2}")
                fail = 1
            if banked is not None and r['mu'][0] != banked:
                print(f"  GREEN FAILED H={H}: mu_1={r['mu'][0]} != banked "
                      f"GF(2) rank {banked}")
                fail = 1
        if modp is not None and r['mu'][K - 1] != modp:
            print(f"  NOTE H={H}: mu_{K}={r['mu'][K-1]} != A-S1 mod-p rank "
                  f"{modp} -- incomplete closure, or invariant factors of "
                  f"valuation >= {K}")
            fail = 1

    print()
    print(f"RED control: dropping the (r-1) diagonal from the merge stencil "
          f"must move the mu profile")
    for H in (4, 5):
        true_mu = mu_profile(H, K, P)['mu']
        red_mu = mu_profile(H, K, P, red=True)['mu']
        print(f"  H={H}  true {true_mu}   red {red_mu}")
        if true_mu == red_mu:
            print(f"  RED CONTROL FAILED H={H}: corrupted stencil gives the "
                  f"same mu profile")
            fail = 1

    print()
    print("RESULT: " + ("GREEN" if not fail else "FAILED"))
    return fail


if __name__ == '__main__':
    sys.exit(main())
