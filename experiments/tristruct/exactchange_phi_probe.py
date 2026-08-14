#!/usr/bin/env python3
"""Exact Change probe 1: is the GF(2) observability quotient locally computable?

Context: results/triangle-r3-involution.md INV-4.  The char-2 Hankel rank of
the strip functional is measured at H = 4..12 as 6, 15, 27, 58, 112, 229,
453, 912, 1818 = A034299(H-1), closed form (2^(H+4) - (-1)^H (6H+7) - 9)/36.
The minimal GF(2) weighted automaton of that dimension exists abstractly; an
algorithm at H = 21 (predicted dim 932,071) needs its quotient map phi to be
computable per-state WITHOUT the observability closure.

This probe computes phi exactly at small H and asks what determines it:

  T1: is phi(s) a function of the column occupancy mask alone?
  T2: if not, of (mask, number of blocks mod 2)?  (mask, number of blocks)?
  T3: how many Nerode classes (distinct phi values) are there at all?

Fail-closed: the rank must equal the banked A034299 values exactly (RED
anchor -- a broken closure cannot silently pass), and phi must separate
accepting from non-accepting states.
"""
import sys
import time

import numpy as np

from r3_inv_rank_probe import build_automaton

BANKED_RANK = {4: 6, 5: 15, 6: 27, 7: 58, 8: 112, 9: 229, 10: 453, 11: 912,
               12: 1818}


def a034299(H):
    return (2 ** (H + 4) - (-1) ** H * (6 * H + 7) - 9) // 36


def obs_basis_gf2(delta, accept):
    """Basis (as ints, bit s = value at state s) of span{accept o delta words}."""
    n, na = delta.shape
    basis = {}

    def reduce_add(row):
        while row:
            p = row.bit_length() - 1
            if p in basis:
                row ^= basis[p]
            else:
                basis[p] = row
                return True
        return False

    def vec_to_int(v):
        return int.from_bytes(np.packbits(v[::-1]).tobytes(), 'big')

    frontier = [accept.copy()]
    reduce_add(vec_to_int(accept))
    while frontier:
        nxt = []
        for g in frontier:
            for mi in range(na):
                d = delta[:, mi]
                h = np.zeros(n, dtype=bool)
                ok = d >= 0
                h[ok] = g[d[ok]]
                if reduce_add(vec_to_int(h)):
                    nxt.append(h)
        frontier = nxt
    return list(basis.values())


def classes_by(keys, phi):
    """Given a key per state, return (n_keys, n_keys_split, max_classes_per_key,
    total_classes)."""
    groups = {}
    for k, p in zip(keys, phi):
        groups.setdefault(k, set()).add(p)
    split = sum(1 for v in groups.values() if len(v) > 1)
    return (len(groups), split, max(len(v) for v in groups.values()),
            sum(len(v) for v in groups.values()))


def main():
    hs = [int(a) for a in sys.argv[1:]] or list(range(4, 11))
    for H in hs:
        t0 = time.time()
        order, delta, accept, masks = build_automaton(H)
        n = len(order)
        vecs = obs_basis_gf2(delta, accept)
        r = len(vecs)
        want = BANKED_RANK.get(H, a034299(H))
        assert r == want, f"H={H}: rank {r} != banked/predicted {want}"
        assert a034299(H) == want, f"H={H}: formula breaks: {a034299(H)} vs {want}"

        # vec_to_int packs state s at bit position s + pad (packbits pads the
        # tail byte with zeros, which land in the low bits of the int)
        pad = (-n) % 8
        phi = [0] * n
        for i, v in enumerate(vecs):
            for s in range(n):
                if v >> (s + pad) & 1:
                    phi[s] |= 1 << i

        # fail-closed separation check: accept vector is in the span, so an
        # accepting and a non-accepting state can never share phi
        acc_phis = {phi[s] for s in range(n) if accept[s]}
        rej_phis = {phi[s] for s in range(n) if not accept[s]}
        assert not (acc_phis & rej_phis), f"H={H}: phi fails to separate accept"

        smask = [sum(1 << row for row, v in enumerate(st) if v >= 0)
                 for st in order]
        nblk = [max(st) + 1 for st in order]

        nerode = len(set(phi))
        t1 = classes_by(smask, phi)
        t2a = classes_by(list(zip(smask, [b % 2 for b in nblk])), phi)
        t2b = classes_by(list(zip(smask, nblk)), phi)

        print(f"H={H} states={n} rank={r} nerode_classes={nerode} "
              f"masks={len(masks)}")
        print(f"  T1 mask alone:        keys={t1[0]} split={t1[1]} "
              f"maxper={t1[2]} classes={t1[3]}")
        print(f"  T2 mask+nblocks%2:    keys={t2a[0]} split={t2a[1]} "
              f"maxper={t2a[2]} classes={t2a[3]}")
        print(f"  T2 mask+nblocks:      keys={t2b[0]} split={t2b[1]} "
              f"maxper={t2b[2]} classes={t2b[3]}")
        # T4: greedy pivot basis in canonical state order -- which states carry
        # the rank?  Candidate combinatorial laws are tested on the chosen set.
        stlist = sorted(range(n), key=lambda s: (smask[s], order[s]))
        gb = {}

        def greedy_add(row):
            while row:
                p = row.bit_length() - 1
                if p in gb:
                    row ^= gb[p]
                else:
                    gb[p] = row
                    return True
            return False

        chosen = [s for s in stlist if greedy_add(phi[s])]
        assert len(chosen) == r

        def contiguous(st):
            # every block is a single contiguous run of rows
            blocks = {}
            for row, v in enumerate(st):
                if v >= 0:
                    blocks.setdefault(v, []).append(row)
            return all(rs == list(range(rs[0], rs[0] + len(rs)))
                       for rs in blocks.values())

        ncontig_chosen = sum(1 for s in chosen if contiguous(order[s]))
        ncontig_all = sum(1 for s in range(n) if contiguous(order[s]))
        nsingle_chosen = sum(1 for s in chosen if nblk[s] == 1)
        print(f"  T4 greedy basis: chosen={len(chosen)} "
              f"all-blocks-contiguous {ncontig_chosen}/{len(chosen)} "
              f"(population {ncontig_all}/{n}); single-block {nsingle_chosen}")
        if H <= 5:
            for s in chosen:
                print(f"     {order[s]}")
        print(f"  ({time.time()-t0:.1f}s)", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
