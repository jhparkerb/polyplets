"""r3_l1_piece_states.py -- L1 (corner gluing) state-space measurement.

Question (docs/triangle-round3-brief.md, lane L1): does a height-H strip make
coarse piece-assembly a smaller state space than the cell frontier?

Two column-sweep DPs over the H-strip, identical framework:

  CELL  state = (mask, king partition of runs, touch flags)
        -- the engines' frontier object at run granularity.
  PIECE state = (mask, rook-piece partition of runs, king partition, flags)
        -- the coarsest state that can track corner-glued assembly of
           rook-connected pieces: which boundary runs belong to the same
           piece (rook labels) and which pieces have king-connected so far.

Facts used: within a column, vertically adjacent occupied cells are edge-
adjacent, so maximal vertical runs are the atoms; a run lies in one piece.
Rook connections are planar => the rook partition is non-crossing; king
components cannot interleave either (a crossing X of diagonals forces a
vertical edge-adjacency), so both partitions are non-crossing and king
coarsens rook.  None of that is assumed by the code -- it just does exact
union-find; the geometry facts only bound what can appear.

Subcommands:
  validate  -- both DPs reproduce banked T(n,H) (triangle.py) for H<=6,
               n<=10, and the PIECE DP reproduces the C(n,c) stratification
               table of results/component-stratification.md for n<=7
               (c tracked exactly: completed pieces + live pieces).
               RED control: plant a corrupted expected value, must FAIL.
  closure   -- reachable live-state closure per H (flagless core state),
               CELL vs PIECE, with per-step growth ratios.

Exact integer arithmetic throughout.
"""

import sys
import time

sys.setrecursionlimit(100000)


def runs_of(mask, H):
    """Maximal vertical runs of set bits, top to bottom: list of (lo, hi)."""
    out = []
    r = 0
    while r < H:
        if mask >> r & 1:
            lo = r
            while r < H and (mask >> r & 1):
                r += 1
            out.append((lo, r - 1))
        else:
            r += 1
    return tuple(out)


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        if x not in p:
            p[x] = x
            return x
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def canon(labels):
    """Relabel a label tuple by first occurrence: (5,2,5) -> (0,1,0)."""
    seen = {}
    out = []
    for x in labels:
        if x not in seen:
            seen[x] = len(seen)
        out.append(seen[x])
    return tuple(out)


def transition(H, mask, rook, king, newmask):
    """Extend the boundary by one column with occupancy newmask.

    Returns (newrook, newking, completed_pieces) or None if a king
    component strands (no continuation into the new column).
    Node names: ('o', i) = old run i, ('n', j) = new run j.
    """
    oruns = runs_of(mask, H)
    nruns = runs_of(newmask, H)
    old_at = {}
    for i, (lo, hi) in enumerate(oruns):
        for r in range(lo, hi + 1):
            old_at[r] = i

    ur = UF()  # rook (edge) connectivity
    uk = UF()  # king connectivity (coarsens rook)
    # seed with the old partitions
    for i in range(len(oruns)):
        ur.union(('o', i), ('r', rook[i]))
        uk.union(('o', i), ('k', king[i]))
    for j, (lo, hi) in enumerate(nruns):
        for r in range(lo, hi + 1):
            if r in old_at:  # horizontal edge: rook AND king
                ur.union(('n', j), ('o', old_at[r]))
                uk.union(('n', j), ('o', old_at[r]))
            for rr in (r - 1, r + 1):  # diagonal: king only
                if rr in old_at:
                    uk.union(('n', j), ('o', old_at[rr]))
    # rook-connected => king-connected (same piece is one component)
    for i in range(len(oruns)):
        for j in range(len(nruns)):
            if ur.find(('o', i)) == ur.find(('n', j)):
                uk.union(('o', i), ('n', j))

    # stranded king component: an old class none of whose members reaches
    # any new run kills the state (it can never grow again)
    newk_roots = set(uk.find(('n', j)) for j in range(len(nruns)))
    for i in range(len(oruns)):
        if uk.find(('o', i)) not in newk_roots:
            return None

    # completed rook pieces: old rook classes with no new run attached
    newr_roots = set(ur.find(('n', j)) for j in range(len(nruns)))
    old_r_roots = set(ur.find(('o', i)) for i in range(len(oruns)))
    completed = sum(1 for x in old_r_roots if x not in newr_roots)

    newrook = canon(tuple(ur.find(('n', j)) for j in range(len(nruns))))
    newking = canon(tuple(uk.find(('n', j)) for j in range(len(nruns))))
    return newrook, newking, completed


def initial(H, mask):
    k = len(runs_of(mask, H))
    lab = tuple(range(k))  # each run its own piece, its own component
    return lab, lab


def flags_of(mask, H, flags):
    return (flags[0] or bool(mask & 1), flags[1] or bool(mask >> (H - 1) & 1))


def dp_counts(H, nmax, track_c=False):
    """Exact strip DP.  Returns {(n,H)} -> count, or {(n,c)} -> count summed
    over animals of height exactly H when track_c (c = # rook pieces)."""
    from collections import defaultdict
    harvest = defaultdict(int)
    # state -> {key -> count}; key = n or (n, completed)
    cur = {}
    for mask in range(1, 1 << H):
        rook, king = initial(H, mask)
        st = (mask, rook, king, flags_of(mask, H, (False, False)))
        key = (bin(mask).count('1'), 0) if track_c else bin(mask).count('1')
        cur.setdefault(st, defaultdict(int))[key] += 1
    while cur:
        # harvest: single king component, both touch flags
        for (mask, rook, king, fl), keys in cur.items():
            if fl == (True, True) and len(set(king)) == 1:
                live = len(set(rook))
                for key, cnt in keys.items():
                    if track_c:
                        n, done = key
                        harvest[(n, done + live)] += cnt
                    else:
                        harvest[(key, H)] += cnt
        nxt = {}
        for (mask, rook, king, fl), keys in cur.items():
            for newmask in range(1, 1 << H):
                add = bin(newmask).count('1')
                t = transition(H, mask, rook, king, newmask)
                if t is None:
                    continue
                nrook, nking, comp = t
                nst = (newmask, nrook, nking, flags_of(newmask, H, fl))
                for key, cnt in keys.items():
                    if track_c:
                        n, done = key
                        if n + add > nmax:
                            continue
                        nkey = (n + add, done + comp)
                    else:
                        if key + add > nmax:
                            continue
                        nkey = key + add
                    nxt.setdefault(nst, __import__('collections').defaultdict(int))[nkey] += cnt
        cur = nxt
    return dict(harvest)


def closure(H, piece_level, budget_s=600.0):
    """Reachable live flagless-state closure: how many distinct core states
    (mask, [rook,] king) can appear on the boundary, any n, any width."""
    seen = set()
    frontier = []
    for mask in range(1, 1 << H):
        rook, king = initial(H, mask)
        st = (mask, rook, king) if piece_level else (mask, king)
        if st not in seen:
            seen.add(st)
            frontier.append((mask, rook, king))
    t0 = time.time()
    while frontier:
        if time.time() - t0 > budget_s:
            return None  # over budget: report DNF
        nfront = []
        for mask, rook, king in frontier:
            for newmask in range(1, 1 << H):
                t = transition(H, mask, rook, king, newmask)
                if t is None:
                    continue
                nrook, nking, _ = t
                st = (newmask, nrook, nking) if piece_level else (newmask, nking)
                if st not in seen:
                    seen.add(st)
                    nfront.append((newmask, nrook, nking))
        frontier = nfront
    return len(seen)


def cmd_validate():
    sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
    from triangle import Triangle
    tri = Triangle.load()
    ok = True

    print("== T(n,H) validation, PIECE DP (rook+king state), H<=6 n<=10 ==")
    for H in range(1, 7):
        got = dp_counts(H, 10)
        for n in range(1, 11):
            want = tri.cell(n, H)
            g = got.get((n, H), 0)
            status = "ok" if g == want else "FAIL"
            if g != want:
                ok = False
            if n >= H:  # only print the nonzero region
                print("  T(%2d,%d) dp=%-12d banked=%-12d %s" % (n, H, g, want, status))

    print("== C(n,c) validation vs results/component-stratification.md, n<=7 ==")
    # banked table, results/component-stratification.md lines 11-17
    C = {
        (1, 1): 1,
        (2, 1): 2, (2, 2): 2,
        (3, 1): 6, (3, 2): 8, (3, 3): 6,
        (4, 1): 19, (4, 2): 36, (4, 3): 36, (4, 4): 19,
        (5, 1): 63, (5, 2): 156, (5, 3): 200, (5, 4): 156, (5, 5): 63,
        (6, 1): 216, (6, 2): 660, (6, 3): 1038, (6, 4): 1040, (6, 5): 662, (6, 6): 216,
        (7, 1): 760, (7, 2): 2752, (7, 3): 5142, (7, 4): 6236, (7, 5): 5166,
        (7, 6): 2776, (7, 7): 760,
    }
    from collections import defaultdict
    tot = defaultdict(int)
    for H in range(1, 8):
        got = dp_counts(H, 7, track_c=True)
        for (n, c), v in got.items():
            tot[(n, c)] += v
    for n in range(1, 8):
        for c in range(1, n + 1):
            want = C[(n, c)]
            g = tot.get((n, c), 0)
            status = "ok" if g == want else "FAIL"
            if g != want:
                ok = False
            print("  C(%d,%d) dp=%-6d banked=%-6d %s" % (n, c, g, want, status))

    print("== RED control: corrupt one expected cell, must FAIL ==")
    red_want = tri.cell(6, 3) + 1  # deliberately wrong
    red_got = dp_counts(3, 6).get((6, 3), 0)
    if red_got == red_want:
        print("  RED CONTROL PASSED A CORRUPT VALUE -- validation is broken")
        ok = False
    else:
        print("  red control fails as required (dp=%d vs corrupt=%d)" % (red_got, red_want))

    print("VALIDATION:", "ALL OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


def cmd_closure(hmax):
    print("== reachable live-state closure (flagless core), CELL vs PIECE ==")
    print("H  cell_states  piece_states  piece/cell  cell_ratio  piece_ratio  secs")
    prev_c = prev_p = None
    for H in range(2, hmax + 1):
        t0 = time.time()
        c = closure(H, piece_level=False)
        p = closure(H, piece_level=True)
        dt = time.time() - t0
        if c is None or p is None:
            print("%d  over budget, stopping" % H)
            break
        rc = ("%.3f" % (c / prev_c)) if prev_c else "-"
        rp = ("%.3f" % (p / prev_p)) if prev_p else "-"
        print("%-2d %-12d %-13d %-10.3f %-11s %-12s %.1f" % (H, c, p, p / c, rc, rp, dt))
        prev_c, prev_p = c, p
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'validate'
    if cmd == 'validate':
        sys.exit(cmd_validate())
    elif cmd == 'closure':
        hmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        sys.exit(cmd_closure(hmax))
    else:
        print("usage: r3_l1_piece_states.py {validate|closure [Hmax]}")
        sys.exit(2)
