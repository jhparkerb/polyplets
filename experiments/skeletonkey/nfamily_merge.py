#!/usr/bin/env python3
"""Skeleton Key probe 2 -- is the N-family congruence a plain state merge for
the production column automaton, in characteristic 0?

Two files in the tree disagree without noticing each other:

  results/r4/r4-floors.md (2026-08-13) calls the pairwise Nerode-
  distinguishability of the M(H+1)-1 column states "the single highest-value
  missing brick" and marks it NOT ESTABLISHED -- "nobody appears to have
  asked".

  results/exactchange-probes.md section 6 (2026-08-14) answers it: two strip
  states are equivalent iff they carry the same multiset of block
  neighbourhoods N(b) = rows(b) expanded +-1, clipped to [0,H).  Measured
  2187 -> 575 at H = 9.  But that file states the result as GF(2)-Nerode
  equivalence and section 10 prices the whole campaign as one mod-2 bit.

The argument given there reads nothing about a block except N(b), so it is a
statement about the LANGUAGE, hence a congruence over any semiring -- and then
it is not a characteristic-2 fact but a state-space cut for exact counting.
This probe tests exactly that, re-deriving the automaton from scratch (no
exactchange code, no production code is imported) and gating on the banked
C_H rows, which are exact integers.

Gates, all fail-closed:
  A   raw reachable state count == Motzkin(H+1) - 1
  B   raw automaton reproduces banked C_H(n) exactly, every n <= NMAX
  C   the N-key is a congruence -- succ_key(key(s), m) == key(succ(s, m)) for
      every reachable s and every column mask m
  D   the a-priori key automaton, built with no reference to the raw states,
      reproduces banked C_H(n) exactly
  RED a key that drops the +-1 expansion must break gate C or gate D

Usage: nfamily_merge.py MAXH_FULL MAXH_KEYONLY [NMAX]
"""

import os
import sys
import time
from collections import defaultdict

# results/exactchange-probes.md section 6, minimized state counts N(H),
# H = 4..11, computed there by a separate implementation (a GF(2) Nerode
# closure).  Gate E is a two-implementation cross-check: this probe never
# reads that code, so agreement is independent corroboration and disagreement
# means one of us is wrong.
BANKED_N = {4: 8, 5: 19, 6: 43, 7: 101, 8: 239, 9: 575, 10: 1399, 11: 3441}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROWDIR = os.path.join(ROOT, "results", "cutcount_b1", "rows")


# ---------------------------------------------------------------- lattice bits

def runs_of(mask, H):
    """Maximal vertical runs of a column fill; cells in one run are king- (in
    fact rook-) adjacent, so a run is always inside one component."""
    out, i = [], 0
    while i < H:
        if (mask >> i) & 1:
            j = i
            while j + 1 < H and (mask >> (j + 1)) & 1:
                j += 1
            out.append(tuple(range(i, j + 1)))
            i = j + 1
        else:
            i += 1
    return out


def nbhd(block, H, expand=1):
    """N(b) as a BITMASK: the rows of the NEXT column at which a new cell
    attaches to block b.  King adjacency is |dr| <= 1, so expand=1.  expand=0
    is the RED control (rook-only attachment), which must not reproduce king
    counts.

    A bitmask, not a frozenset, on purpose: an N-key is a SORTED multiset of
    these, and `sorted` over frozensets sorts by the SUBSET partial order,
    which is not a total order -- two equal multisets presented in different
    orders can then canonicalize differently and split one class into two.
    Integers sort totally, so the key is a genuine canonical form."""
    m = 0
    for r in block:
        for d in range(-expand, expand + 1):
            if 0 <= r + d < H:
                m |= 1 << (r + d)
    return m


def canon(groups):
    return tuple(sorted(tuple(sorted(g)) for g in groups))


def succ_state(state, mask, H, expand=1):
    """Successor partition, or None if some live block strands.

    A block that no new cell attaches to can never be rejoined (every later
    cell is strictly to the right of the new column), so the configuration is
    dead."""
    R = runs_of(mask, H)
    nb = [nbhd(b, H, expand) for b in state]
    touch = [frozenset(i for i, N in enumerate(nb)
                       if any((N >> r) & 1 for r in run))
             for run in R]
    used = set()
    for t in touch:
        used |= t
    if len(used) != len(state):
        return None
    return _regroup(R, touch)


def _regroup(R, touch):
    """Runs sharing an old block are one component; runs touching nothing are
    fresh components."""
    parent = list(range(len(R)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    byold = {}
    for i, t in enumerate(touch):
        for o in t:
            if o in byold:
                a, b = find(byold[o]), find(i)
                if a != b:
                    parent[a] = b
            else:
                byold[o] = i
    groups = defaultdict(list)
    for i in range(len(R)):
        groups[find(i)].extend(R[i])
    return canon(groups.values())


# ------------------------------------------------------------------ the N-key

def key_of(state, H, expand=1):
    return tuple(sorted(nbhd(b, H, expand) for b in state))


def succ_key(key, mask, H, expand=1):
    """Successor of an N-key, computed WITHOUT any partition state: this is the
    a-priori automaton.  Same shape as succ_state, reading each old block only
    through its neighbourhood set."""
    R = runs_of(mask, H)
    touch = [frozenset(i for i, N in enumerate(key)
                       if any((N >> r) & 1 for r in run))
             for run in R]
    used = set()
    for t in touch:
        used |= t
    if len(used) != len(key):
        return None
    return tuple(sorted(nbhd(b, H, expand) for b in _regroup(R, touch)))


# ------------------------------------------------------------------ machinery

def motzkin(n):
    m = [1, 1]
    for k in range(2, n + 1):
        m.append(((2 * k + 1) * m[k - 1] + (3 * k - 3) * m[k - 2]) // (k + 2))
    return m[n]


def banked_C(H):
    p = os.path.join(ROWDIR, "C%d.out" % H)
    if not os.path.exists(p):
        return None
    out = {}
    with open(p) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                out[int(parts[0])] = int(parts[1])
    return out


def build(H, start, succ, expand=1):
    """BFS the reachable automaton; returns (states, transition table).

    trans[i] = list of (mask_popcount, j) over nonempty masks."""
    idx = {start: 0}
    order = [start]
    trans = []
    qi = 0
    while qi < len(order):
        s = order[qi]
        qi += 1
        row = []
        for mask in range(1, 1 << H):
            t = succ(s, mask, H, expand)
            if t is None:
                continue
            j = idx.get(t)
            if j is None:
                j = len(order)
                idx[t] = j
                order.append(t)
            row.append((bin(mask).count("1"), j))
        trans.append(row)
    return order, trans


def build_flagged(H, start, succ, expand=1):
    """Same automaton with the exact-height flags the production engine
    carries (cpp/tma/signature.h b[H], b[H+1]).  The flags are updated from
    the new column mask alone, so (state, ftop, fbot) is a congruence exactly
    when state is -- but they BLOCK merges between states that differ in
    whether row 0 or row H-1 was ever occupied, so this measures what the
    merge is worth to an engine that does not telescope."""
    top, bot = 1, 1 << (H - 1)
    s0 = (start, 0, 0)
    idx = {s0: 0}
    order = [s0]
    trans = []
    qi = 0
    while qi < len(order):
        st, ft, fb = order[qi]
        qi += 1
        row = []
        for mask in range(1, 1 << H):
            t = succ(st, mask, H, expand)
            if t is None:
                continue
            k = (t, ft | (1 if mask & top else 0), fb | (1 if mask & bot else 0))
            j = idx.get(k)
            if j is None:
                j = len(order)
                idx[k] = j
                order.append(k)
            row.append((bin(mask).count("1"), j))
        trans.append(row)
    return order, trans


def count_T(order, trans, nmax):
    """T(n,H): accept only when one block is left AND both boundary rows have
    been touched, i.e. the animal spans exactly H."""
    accept = [1 if (len(st) == 1 and ft and fb) else 0 for st, ft, fb in order]
    return _count(order, trans, accept, nmax)


def count_C(order, trans, nmax):
    """C_H(n): words over nonempty column fills whose final state has exactly
    one live block.  Start state is index 0 (the empty frontier)."""
    accept = [1 if len(s) == 1 else 0 for s in order]
    return _count(order, trans, accept, nmax)


def _count(order, trans, accept, nmax):
    dp = [[0] * (nmax + 1) for _ in order]
    dp[0][0] = 1
    tot = [0] * (nmax + 1)
    for _ in range(nmax):
        nxt = [[0] * (nmax + 1) for _ in order]
        for i, row in enumerate(trans):
            di = dp[i]
            if not any(di):
                continue
            for w, j in row:
                dj = nxt[j]
                for n in range(0, nmax + 1 - w):
                    v = di[n]
                    if v:
                        dj[n + w] += v
        dp = nxt
        for i in range(len(order)):
            if accept[i]:
                for n in range(nmax + 1):
                    tot[n] += dp[i][n]
    return tot


# ---------------------------------------------------------------------- driver

def main():
    maxh_full = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    maxh_key = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    nmax = int(sys.argv[3]) if len(sys.argv) > 3 else 12

    print("# skeletonkey nfamily_merge  maxh_full=%d maxh_key=%d nmax=%d"
          % (maxh_full, maxh_key, nmax), flush=True)

    rows = []
    for H in range(2, maxh_full + 1):
        t0 = time.time()
        raw, rawT = build(H, (), succ_state)
        nraw = len(raw) - 1                      # drop the empty start state
        want = motzkin(H + 1) - 1
        if nraw != want:
            sys.exit("GATE A FAILED H=%d: %d reachable, Motzkin(H+1)-1=%d"
                     % (H, nraw, want))
        print("# gate A ok H=%d: %d states == Motzkin(%d)-1" % (H, nraw, H + 1),
              flush=True)

        C = banked_C(H)
        got = count_C(raw, rawT, nmax)
        if C is not None:
            for n in range(1, nmax + 1):
                if n in C and got[n] != C[n]:
                    sys.exit("GATE B FAILED H=%d n=%d: %d != banked %d"
                             % (H, n, got[n], C[n]))
            print("# gate B ok H=%d: C_H(n) matches banked rows n<=%d"
                  % (H, nmax), flush=True)
        else:
            print("# gate B SKIPPED H=%d: no banked C%d.out" % (H, H), flush=True)

        # gate C -- the key is a congruence on the reachable set
        for i, s in enumerate(raw):
            ks = key_of(s, H)
            for mask in range(1, 1 << H):
                t = succ_state(s, mask, H)
                kt = succ_key(ks, mask, H)
                if (t is None) != (kt is None):
                    sys.exit("GATE C FAILED H=%d: liveness disagrees" % H)
                if t is not None and key_of(t, H) != kt:
                    sys.exit("GATE C FAILED H=%d: key(succ) != succ(key)" % H)
        print("# gate C ok H=%d: N-key is a congruence over all %d states"
              % (H, nraw), flush=True)

        keys, keyT = build(H, (), succ_key, expand=1)
        nkey = len(keys) - 1
        gotk = count_C(keys, keyT, nmax)
        if gotk != got:
            sys.exit("GATE D FAILED H=%d: key automaton disagrees" % H)
        print("# gate D ok H=%d: %d key states reproduce the same C_H"
              % (H, nkey), flush=True)

        # merge classes counted the other way round, as a cross-check
        cls = len(set(key_of(s, H) for s in raw)) - 1
        if cls != nkey:
            sys.exit("GATE D FAILED H=%d: %d classes vs %d key states"
                     % (H, cls, nkey))

        if H in BANKED_N and nkey != BANKED_N[H]:
            sys.exit("GATE E FAILED H=%d: %d classes vs exactchange's %d"
                     % (H, nkey, BANKED_N[H]))

        # gate F -- the flagged machine emits T(n,H) directly, and it must
        # agree with the telescope C_H - 2C_{H-1} + C_{H-2} over banked rows.
        # Two different mechanisms for exact height, same numbers or bust.
        fr, frT = build_flagged(H, (), succ_state)
        fk, fkT = build_flagged(H, (), succ_key)
        Cm1, Cm2 = banked_C(H - 1), banked_C(H - 2)
        # counting the flagged machine is states x masks x nmax^2; it says
        # nothing new above the heights where the telescope is already
        # confirmed, so cap it and keep the state-count column at every H.
        if H <= 7 and C is not None and Cm1 is not None:
            Tflag = count_T(fr, frT, nmax)
            if count_T(fk, fkT, nmax) != Tflag:
                sys.exit("GATE F FAILED H=%d: flagged key machine disagrees" % H)
            for n in range(1, nmax + 1):
                if n not in C or n not in Cm1:
                    continue
                tel = C[n] - 2 * Cm1[n] + (Cm2[n] if Cm2 and n in Cm2 else 0)
                if tel != Tflag[n]:
                    sys.exit("GATE F FAILED H=%d n=%d: flags give %d, "
                             "telescope gives %d" % (H, n, Tflag[n], tel))
            print("# gate F ok H=%d: flagged machine == C_H telescope, n<=%d"
                  % (H, nmax), flush=True)
        nrawf, nkeyf = len(fr) - 1, len(fk) - 1

        # rook control: with expand=0 the neighbourhood IS the block, so the
        # key is the state and nothing merges.  The compression is a fact
        # about KING adjacency blurring rows, not about strips.
        rr, _ = build(H, (), succ_state, expand=0)
        rk, _ = build(H, (), succ_key, expand=0)
        if len(rr) != len(rk):
            sys.exit("GATE G FAILED H=%d: rook merged %d -> %d, it must not"
                     % (H, len(rr) - 1, len(rk) - 1))
        print("# gate G ok H=%d: on the ROOK lattice the key is the state "
              "(%d = %d), so nothing merges -- the compression is a fact "
              "about king adjacency" % (H, len(rr) - 1, len(rk) - 1),
              flush=True)

        # gate H -- the key fits the production signature's existing width.
        # A row r is in N(b) only if b has a cell in {r-1, r, r+1}, and
        # distinct blocks are >= 2 rows apart, so at most TWO blocks' N-sets
        # can cover any row: two nibbles per row encode the whole key in the
        # H bytes cpp/tma/signature.h already spends on labels.  If this ever
        # fails, the key needs a wider Sig and the drop-in is not a drop-in.
        for st in keys[1:]:
            for r in range(H):
                if sum(1 for N in st if (N >> r) & 1) > 2:
                    sys.exit("GATE H FAILED H=%d: row %d covered by %d "
                             "neighbourhoods" % (H, r,
                             sum(1 for N in st if (N >> r) & 1)))
        print("# gate H ok H=%d: no row is covered by more than two "
              "neighbourhoods, so the key fits H bytes" % H, flush=True)

        # vertical mirror: does the merge subsume the R1 fold, or compose?
        def refl(k):
            out = []
            for N in k:
                m = 0
                for r in range(H):
                    if (N >> r) & 1:
                        m |= 1 << (H - 1 - r)
                out.append(m)
            return tuple(sorted(out))
        orb = set()
        for s in keys[1:]:
            orb.add(min(s, refl(s)))
        rows.append((H, nraw, nkey, len(orb)))
        print("H=%-3d raw=%-9d key=%-8d ratio=%.3f  mirror=%-7d "
              "flagged %d/%d=%.3f  %.1fs"
              % (H, nraw, nkey, nraw / nkey, len(orb), nrawf, nkeyf,
                 nrawf / nkeyf, time.time() - t0), flush=True)

    # RED control: rook-only attachment must not reproduce king counts
    Hr = min(5, maxh_full)
    redk, redT = build(Hr, (), succ_key, expand=0)
    red = count_C(redk, redT, nmax)
    raw, rawT = build(Hr, (), succ_state)
    good = count_C(raw, rawT, nmax)
    if red == good:
        sys.exit("RED FAILED H=%d: expand=0 reproduces the king counts" % Hr)
    print("# RED ok H=%d: expand=0 gives %s, king gives %s"
          % (Hr, red[1:6], good[1:6]), flush=True)

    # key-only ladder, no raw states built at all
    print("\n# key-only ladder (a-priori automaton, no partition states built)",
          flush=True)
    for H in range(maxh_full + 1, maxh_key + 1):
        t0 = time.time()
        keys, _ = build(H, (), succ_key, expand=1)
        nkey = len(keys) - 1
        want = motzkin(H + 1) - 1
        if H in BANKED_N and nkey != BANKED_N[H]:
            sys.exit("GATE E FAILED H=%d: %d classes vs exactchange's %d"
                     % (H, nkey, BANKED_N[H]))
        print("H=%-3d raw=%-12d key=%-9d ratio=%.3f   %.1fs"
              % (H, want, nkey, want / nkey, time.time() - t0), flush=True)
        rows.append((H, want, nkey, None))

    print("\n# H  raw  key  ratio  growth_raw  growth_key", flush=True)
    for i, (H, nraw, nkey, _o) in enumerate(rows):
        gr = gk = float("nan")
        if i:
            gr = nraw / rows[i - 1][1]
            gk = nkey / rows[i - 1][2]
        print("%-4d %-12d %-9d %.3f  %.4f  %.4f" % (H, nraw, nkey, nraw / nkey, gr, gk),
              flush=True)


if __name__ == "__main__":
    main()
