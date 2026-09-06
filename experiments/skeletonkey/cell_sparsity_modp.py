#!/usr/bin/env python3
"""Skeleton Key probe 1 -- is the compressed cell-level transfer SPARSE in
characteristic 0, as it is in characteristic 2?

WHY THIS ONE NUMBER.  A-S1 (git show second-source:results/scaling-exploration-A.md (deleted),
"Crossover: never") priced the rank-compressed engine and rejected it on compute:
the compressed column transfer was taken to be a DENSE d x d matrix, so per-column
cost grows as d^2 ~ 5.7x/height against the incumbent's sparse states x H ~
2.65x/height -- already 12.8x more work at H = 9.  That file names its own single
escape:

    "The one unprobed rescue: if the compressed d x d matrix had exploitable
     structure (sparsity, low displacement rank) the d^2 could drop; nothing
     measured here supports that and the burden is on it."

Exact Change probe 2/4 (results/arithmetic-structure.md sec. 4) then measured exactly
that -- in GF(2) -- and found the two compressed cell-level transition matrices
SPARSE: average row weight 1.8->3.6 (A_0) and 2.7->5.0 (A_1) at H = 4..7, ~O(H),
against dense ~r/2.  Nobody has measured it in characteristic 0, which is the only
characteristic that can carry an exact value (the T3 theorem in
results/arithmetic-structure.md makes p = 2 the sole collapsing
prime, so mod-2 is worth one bit and nothing else).

So the live question is a two-line table:
  * char-0 cell-level Hankel rank d(H), and its growth base vs the incumbent's;
  * average/max row weight of the two compressed transition matrices in char 0.
If the weights stay O(H) while d grows at ~2.4x/height, A-S1's "never" is wrong
and the compressed engine wins on BOTH axes.  If they go dense (~d/2), "never"
stands and the last non-engineering lever closes with a measurement instead of an
assumption.

METHOD.  Reuses build_cell_automaton() from the gated Exact Change probe verbatim
-- same object, so the state census / A034299 anchors upstream still apply.  The
closure is taken over F_p with the basis held in REDUCED row echelon form, which
is what makes the sparsity free: for an RREF basis B with pivot columns piv,
any h in the span satisfies h = h[piv] . B exactly, so the row of the compressed
matrix IS h[piv] and its weight is a count_nonzero.  No reduction, no basis-order
artefact beyond the pivot choice itself.

FAIL-CLOSED.  Runs p = 2 through the identical code path first and asserts the
banked char-2 cell ranks 32, 93, 210, 516 at H = 4..7 (results/arithmetic-structure.md
sec. 3).  Exits non-zero on mismatch.  RED control: a corrupted successor map must
break that gate.  Two primes per height; a disagreement is fatal, not a warning.

  usage:   experiments/skeletonkey/cell_sparsity_modp.py MAXH [OUT]
  machine: ayr  (dalby is running the Motley ladder; gympie is banned)
  cost:    predicted H<=7 seconds-to-a-minute, H=8 ~5-15 min and ~2 GB,
           H=9 not attempted here (basis alone is ~7-27 GB).
  resume:  per-height lines are appended and flushed; rerun with a lower MAXH
           costs only the heights below it.  No checkpoint needed at this size.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'tristruct'))

from exactchange_cell_rank import build_cell_automaton          # noqa: E402
from r3_inv_rank_probe import motzkin                           # noqa: E402

# results/arithmetic-structure.md sec. 3, char-2 cell-level rank.
BANKED_GF2_CELL_RANK = {4: 32, 5: 93, 6: 210, 7: 516}

# Two primes well clear of the only two that can move the rank (p = 2, p = 3;
# results/arithmetic-structure.md).  Both small enough that a
# float64 dot of length d stays exact: d * (p-1)^2 < 2^53 for d up to ~5e5.
PRIMES = (131071, 65521)


class RREF:
    """Row-reduced echelon basis over F_p, grown one generator at a time."""

    def __init__(self, n, p, cap):
        # Grown by doubling, NEVER preallocated to cap: cap is the number of
        # cell states, and cap x n float64 is 340 GB at H = 8.  cap survives
        # only as a fail-closed ceiling.
        self.n, self.p, self.cap = n, p, cap
        self.B = np.zeros((256, n), dtype=np.float64)
        self.piv = np.zeros(256, dtype=np.int64)
        self.nb = 0

    def _grow(self):
        if self.nb < len(self.B):
            return
        if 2 * len(self.B) > self.cap:
            raise RuntimeError('RREF capacity exceeded')
        self.B = np.resize(self.B, (2 * len(self.B), self.n))
        self.B[self.nb:] = 0.0
        self.piv = np.resize(self.piv, 2 * len(self.piv))

    def coeffs(self, h):
        """Coefficient row of h against the current basis (exact iff h is in
        the span, which the caller asserts by checking the residual)."""
        return h[self.piv[:self.nb]] % self.p if self.nb else np.zeros(0)

    def residual(self, h, c):
        if self.nb == 0:
            return h % self.p
        return (h - c @ self.B[:self.nb]) % self.p

    def add(self, h):
        """Add h if independent.  Returns True iff the basis grew."""
        c = self.coeffs(h)
        r = self.residual(h.astype(np.float64), c)
        nz = np.flatnonzero(r)
        if nz.size == 0:
            return False
        self._grow()
        j = int(nz[0])
        r = (r * pow(int(r[j]), self.p - 2, self.p)) % self.p
        col = self.B[:self.nb, j].copy()
        if self.nb:
            self.B[:self.nb] = (self.B[:self.nb] - np.outer(col, r)) % self.p
        self.B[self.nb] = r
        self.piv[self.nb] = j
        self.nb += 1
        return True


def closure(d2, acc, p, cap):
    """Observability closure of the cell functional over F_p.

    Generators are gathers of 0/1 vectors, so every residual is 0/1; the span
    is what carries the characteristic.  Only KEPT generators are expanded --
    sound because g -> g o delta_b is linear, so anything in the span of the
    kept set has its images in the span of their images."""
    n = d2.shape[0]
    basis = RREF(n, p, cap)
    keep = []
    if basis.add(acc.astype(np.float64)):
        keep.append(acc.astype(np.uint8))
    frontier = list(keep)
    while frontier:
        nxt = []
        for g in frontier:
            for b in (0, 1):
                d = d2[:, b]
                ok = d >= 0
                h = np.zeros(n, dtype=np.uint8)
                h[ok] = g[d[ok]]
                if basis.add(h.astype(np.float64)):
                    keep.append(h)
                    nxt.append(h)
        frontier = nxt
    return basis, keep


def row_weights(d2, basis, rows, p):
    """Row weights of a compressed transition matrix, in ONE basis.

    `rows` is the domain basis, given as vectors in F_p^n.  B is in RREF with
    pivot columns piv, so the coordinates of any vector v of the span are
    exactly v[piv]; hence row i of the compressed A_b is (rows[i] o delta_b)[piv]
    and its weight is a count_nonzero.  Domain and codomain are the same basis
    only when `rows` IS B -- which is why B is what the headline number uses.
    The residual is checked: a nonzero one means the closure is not invariant
    and the measurement is void."""
    n = d2.shape[0]
    out = {}
    for b in (0, 1):
        d = d2[:, b]
        ok = d >= 0
        w = np.empty(len(rows), dtype=np.int64)
        for i in range(len(rows)):
            g = rows[i]
            h = np.zeros(n, dtype=np.float64)
            h[ok] = g[d[ok]]
            h %= p
            c = basis.coeffs(h)
            r = basis.residual(h, c)
            if np.flatnonzero(r).size:
                raise AssertionError(f'closure not invariant at b={b}, i={i}')
            w[i] = int(np.count_nonzero(c))
        out[b] = w
    return out


# TODO(2026-08-24, /simplify): build_cell_automaton(H) is rebuilt once per
# prime, and it is p-INDEPENDENT -- so the table loop below builds it three
# times per height (two primes plus char 2), and for H<=7 recomputes the char-2
# closure twice (fail-closed gate, then table). Building (order2, d2, acc2)
# once per H and passing it in is a real fraction of the H=8 run (5-15 min).
def run_height(H, p, want_weights=True):
    order2, d2, acc2 = build_cell_automaton(H)
    n = len(order2)
    basis, keep = closure(d2, acc2, p, n)
    d = basis.nb
    if not want_weights:
        return n, d, None, None
    # Headline: the RREF basis itself, so domain and codomain agree.
    wB = row_weights(d2, basis, basis.B[:d], p)
    # Control: the 0/1 closure generators as the domain basis -- a different
    # legitimate basis, reported so the basis-sensitivity is visible rather
    # than assumed away.
    wK = row_weights(d2, basis, [g.astype(np.float64) for g in keep], p)
    return n, d, wB, wK


def main():
    maxh = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    out = open(sys.argv[2], 'a') if len(sys.argv) > 2 else sys.stdout

    def say(s):
        print(s, file=out, flush=True)
        if out is not sys.stdout:
            print(s, flush=True)

    say(f'# skeletonkey cell_sparsity_modp  maxh={maxh}  primes={PRIMES}')

    # ---- fail-closed gate: char-2 cell ranks through the same code path ----
    for H, banked in sorted(BANKED_GF2_CELL_RANK.items()):
        if H > maxh:
            continue
        n, d, _, _ = run_height(H, 2, want_weights=False)
        if d != banked:
            say(f'GATE FAILED H={H}: char-2 cell rank {d} != banked {banked}')
            return 1
        say(f'# gate ok H={H}: char-2 cell rank {d} == banked {banked} '
            f'(cell states {n})')

    # ---- RED control: a corrupted successor map must break the gate --------
    # A single redirected edge does NOT move the rank (measured: it does not),
    # so the control redirects a tenth of the filled-cell edges under three
    # fixed seeds and requires ALL THREE to depart from the banked 93.  One
    # survivor fails the run: a control that can pass on a broken object is
    # not a control.
    order2, d2, acc2 = build_cell_automaton(5)
    live = np.flatnonzero(d2[:, 1] >= 0)
    got = []
    for seed in (1, 2, 3):
        rng = np.random.default_rng(seed)
        pick = rng.choice(live, size=max(2, live.size // 10), replace=False)
        d2r = d2.copy()
        d2r[pick, 1] = rng.permutation(d2r[pick, 1])
        basis, _ = closure(d2r, acc2, 2, len(order2))
        got.append(basis.nb)
    if any(g == BANKED_GF2_CELL_RANK[5] for g in got):
        say(f'RED CONTROL FAILED: perturbed maps gave {got}, one still 93')
        return 1
    say(f'# RED ok: perturbed successor maps give {got}, none 93')

    say('')
    # char 2 goes through the IDENTICAL code path and the identical RREF basis
    # convention, so any difference in the weights is the characteristic and
    # not the basis choice.  That control is the whole point of the table.
    say('H  cellstates  colstates | d_p  A0_p  A1_p  nnz_p [generator-basis '
        'A0/A1] | d_2  A0_2  A1_2  nnz_2 | dense d_p/2  wall_s')
    for H in range(4, maxh + 1):
        t0 = time.time()
        n, d1, wB, wK = run_height(H, PRIMES[0])
        _, d1b, _, _ = run_height(H, PRIMES[1], want_weights=False)
        if d1 != d1b:
            say(f'PRIME DISAGREEMENT H={H}: {PRIMES[0]}->{d1} '
                f'{PRIMES[1]}->{d1b}')
            return 1
        _, d0, vB, _ = run_height(H, 2)
        a0, a1 = wB[0].mean(), wB[1].mean()
        k0, k1 = wK[0].mean(), wK[1].mean()
        b0, b1 = vB[0].mean(), vB[1].mean()
        say(f'{H}  {n}  {motzkin(H+1)-1} | {d1}  {a0:.2f}  {a1:.2f}  '
            f'{d1*(a0+a1):.0f}  [gen {k0:.2f}/{k1:.2f}] | '
            f'{d0}  {b0:.2f}  {b1:.2f}  {d0*(b0+b1):.0f} | '
            f'{d1/2:.1f}  {time.time()-t0:.1f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
