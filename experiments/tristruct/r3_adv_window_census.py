#!/usr/bin/env python3
"""r3_adv_window_census.py — independence adversary, round 3, follow-up.

Exact window-state census for the cancellation DP at H = 15..21, replacing
the flat-x2.9 extrapolation in L6-1's RAM model with measurement.

Method.  A window is the last H+1 cells in column-major order.  Its king-
adjacency graph decomposes (verified programmatically per (H, r)) into two
consecutive-slot paths plus at most three cross edges whose endpoints lie in
slots {0, 1, H-1, H}.  Occupied cells within the window group into chunks
(window-connected components); a reachable window state is (mask, partition
of chunks into colour classes).  HYPOTHESIS: every (mask, partition) pair is
reachable, i.e. census(H) = max over kink position r of
    sum over masks of Bell(#chunks(mask)).
The hypothesis is TESTED against the measured DP censuses (my
r3_adv_state_iso.py Part 5 / L6's probe, which agree bit-for-bit with the
branch's C++ census) at H = 4..12 and against the branch's H = 13, 14 values
by direct mask enumeration; the polynomial-cost path-DP evaluation is then
cross-checked against the same mask enumeration at H <= 14 before being
trusted at H = 15..21.

Also: exact column-cut censuses sum_{k>=1} C(H+1,2k) Bell(k) at H = 15..21,
RAM tables for the 8-bit-prime and 63-bit payload models, and wall
estimates from the branch-measured 0.94 us/slot-col.

Laptop, exact integer arithmetic, throwaway.
"""

import sys, time
from math import comb
from itertools import product

LOG = open(sys.argv[0].replace(".py", ".log"), "w")


def out(s):
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def bell_list(nmax):
    B = [1]
    row = [1]
    for _ in range(nmax):
        new = [row[-1]]
        for v in row:
            new.append(new[-1] + v)
        B.append(new[0])
        row = new
    return B  # B[k] = Bell(k), Bell(0)=1


BELL = bell_list(40)


def window_cells(H, r, col=5):
    """Cells (col, row) held by slots 0..H when the next cell is (col, r)."""
    k = col * H + r
    cells = []
    for j in range(H + 1):
        m = k - H - 1 + j
        cells.append((m // H, m % H))
    return cells


def adjacency(cells):
    n = len(cells)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            (c1, r1), (c2, r2) = cells[i], cells[j]
            if abs(c1 - c2) <= 1 and abs(r1 - r2) <= 1:
                edges.append((i, j))
    return edges


def chunks_of_mask(mask, nbrmask):
    """Component count of occupied slots under the window adjacency."""
    todo = mask
    c = 0
    while todo:
        c += 1
        seed = todo & -todo
        comp = seed
        while True:
            grow = comp
            m = comp
            while m:
                b = m & -m
                grow |= nbrmask[b.bit_length() - 1] & mask
                m ^= b
            if grow == comp:
                break
            comp = grow
        todo &= ~comp
    return c


def census_brute(H, r):
    """sum over masks of Bell(chunks), by direct enumeration."""
    cells = window_cells(H, r)
    edges = adjacency(cells)
    n = H + 1
    nbrmask = [0] * n
    for i, j in edges:
        nbrmask[i] |= 1 << j
        nbrmask[j] |= 1 << i
    total = 0
    for mask in range(1 << n):
        total += BELL[chunks_of_mask(mask, nbrmask)]
    return total


def seg_distribution(L, sstar):
    """Path of length L; sstar = sorted local positions whose occupancy is
    tracked (subset of {0,1,L-2,L-1} in practice).  Returns dict
    (spattern tuple, runs) -> count over all 2^L masks, where runs = number
    of occupied runs along the path."""
    counts = {((), 0, 0): 1}   # (spattern-so-far, last_occ, runs) -> count
    for p in range(L):
        new = {}
        for (sp, last, runs), c in counts.items():
            for occ in (0, 1):
                nsp = sp + (occ,) if p in sstar else sp
                nruns = runs + (1 if occ and not last else 0)
                key = (nsp, occ, nruns)
                new[key] = new.get(key, 0) + c
        counts = new
    fin = {}
    for (sp, last, runs), c in counts.items():
        fin[(sp, runs)] = fin.get((sp, runs), 0) + c
    return fin


def census_pathdp(H, r):
    """Same quantity via the two-path + cross-edge structure, polynomial
    cost.  Asserts the structural facts it relies on."""
    cells = window_cells(H, r)
    edges = adjacency(cells)
    n = H + 1
    consec = [(i, j) for (i, j) in edges if j == i + 1]
    cross = [(i, j) for (i, j) in edges if j != i + 1]
    assert all(i in (0, 1, n - 2, n - 1) and j in (0, 1, n - 2, n - 1)
               for i, j in cross), (H, r, cross)
    # split into consecutive-run segments
    consec_set = {i for i, j in consec}
    segs, start = [], 0
    for i in range(n - 1):
        if i not in consec_set:
            segs.append((start, i))
            start = i + 1
    segs.append((start, n - 1))
    assert len(segs) <= 2, (H, r, segs)
    if len(segs) == 1:                       # fully consecutive: plain path
        dist = seg_distribution(n, set())
        return sum(c * BELL[runs] for (sp, runs), c in dist.items())
    (a0, a1), (b0, b1) = segs
    # cross edges must join the two segments
    assert all((i <= a1) != (j <= a1) for i, j in cross), (H, r, cross)
    sstar = sorted({e for ij in cross for e in ij})
    sA = [s - a0 for s in sstar if s <= a1]
    sB = [s - b0 for s in sstar if s >= b0]
    # two tracked slots in one segment must be adjacent positions (same run
    # when both occupied) — holds for all r; asserted
    for sl in (sA, sB):
        assert len(sl) <= 2 and (len(sl) < 2 or sl[1] - sl[0] == 1), (H, r, sl)
    dA = seg_distribution(a1 - a0 + 1, set(sA))
    dB = seg_distribution(b1 - b0 + 1, set(sB))
    # precompute Delta(patternA, patternB): merges from active cross edges
    def delta(pA, pB):
        occ = {}
        for pos, v in zip(sA, pA):
            occ[pos + a0] = v
        for pos, v in zip(sB, pB):
            occ[pos + b0] = v
        # nodes: runs touching occupied tracked slots; same-segment tracked
        # slots share a run iff both occupied (adjacent positions)
        node = {}
        for s in occ:
            if occ[s]:
                seg = 0 if s <= a1 else 1
                node[s] = seg   # provisional: one run per segment side
        # (both tracked slots of a side occupied -> same run; one occupied
        #  -> that run; so <=1 node per side)
        active = [(i, j) for i, j in cross if occ.get(i, 0) and occ.get(j, 0)]
        if not active:
            return 0
        # any active edge joins side-0 run with side-1 run: exactly 1 merge
        return 1
    total = 0
    for (pA, rA), cA in dA.items():
        for (pB, rB), cB in dB.items():
            total += cA * cB * BELL[rA + rB - delta(pA, pB)]
    return total


def main():
    t0 = time.time()
    measured = {4: 45, 5: 111, 6: 279, 7: 718, 8: 1884, 9: 5041, 10: 13733,
                11: 38065, 12: 107241, 13: 306858, 14: 891074}
    # measured: H<=12 my r3_adv_state_iso.py Part 5 (== L6 probe == branch);
    # H=13,14 branch C++ census (second-source-candidates-B.md)

    out("== Step 1: hypothesis test, mask enumeration vs measured, H=4..14 ==")
    exact = {}
    for H in range(4, 15):
        per_r = [census_brute(H, r) for r in range(H)]
        mx = max(per_r)
        exact[H] = mx
        mark = "MATCH" if mx == measured[H] else \
            f"MISMATCH measured={measured[H]}"
        out(f"  H={H}: max over r = {mx} (argmax r={per_r.index(mx)})  {mark}")
        assert mx == measured[H], (H, mx, measured[H])

    out("== Step 2: path-DP vs mask enumeration, H=4..14, every r ==")
    for H in range(4, 15):
        for r in range(H):
            b, p = census_brute(H, r), census_pathdp(H, r)
            assert b == p, (H, r, b, p)
    out("  path-DP == enumeration at every (H, r), H=4..14: OK")

    out("== Step 3: exact censuses H=15..21 (path-DP, now trusted) ==")
    prev = exact[14]
    win = {}
    for H in range(15, 22):
        per_r = [census_pathdp(H, r) for r in range(H)]
        mx = max(per_r)
        win[H] = mx
        out(f"  H={H}: windows = {mx}  ratio vs H-1 = {mx/prev:.4f}")
        prev = mx
    out("  (H=13->14 measured ratio was 2.9038; the closed form is exact "
        "arithmetic, no fit)")

    out("== Step 4: exact column-cut censuses (for completeness) ==")
    for H in range(15, 22):
        cut = sum(comb(H + 1, 2 * k) * BELL[k]
                  for k in range(1, (H + 1) // 2 + 1))
        out(f"  H={H}: cut states = {cut}")
    out("  (reachability = all (fill, partition) pairs verified only at "
        "H<=9, r3_adv_state_iso.py Part 4; cut counts are not the RAM "
        "driver)")

    out("== Step 5: RAM and wall, exact windows, stated payload model ==")
    out("  model per window (L6/branch): key+hash ~22 B; payload = 41 area "
        "slots x bytes(m) x 2 buffers")
    out("  8-bit prime: 104 B/window; 63-bit prime: 678 B/window")
    out("  wall/height ~ windows x 41 slots x 0.94 us x (41-H) columns "
        "(branch-measured throughput at H=14)")
    out("  H | windows | RAM 8-bit | RAM 63-bit | wall (1 thread)")
    for H in range(15, 22):
        w = win[H]
        r8 = w * 104 / 2 ** 30
        r63 = w * 678 / 2 ** 30
        wall = w * 41 * 0.94e-6 * (41 - H) / 3600
        out(f"  {H} | {w} | {r8:.1f} GiB | {r63:.1f} GiB | {wall:.1f} h")
    out(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
