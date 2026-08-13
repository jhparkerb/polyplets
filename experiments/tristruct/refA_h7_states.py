"""refA_h7_states.py -- Refuter A: settle the H=7 state-count discrepancy.

Proved count (results/king-column-motzkin.md, branch second-source,
a6b8f6a): reachable whole-column states number Motzkin(H+1)-1, i.e. 322 at
H=7.  P3 reported 323.  Construct the H=7 state space two ways -- Refuter
A's own TM (refA_columns_check) and P3's build_states -- count both, and if
they differ, print the states one side has that the other lacks.

State-construction only, no series DP: seconds.

Run from experiments/tristruct/:  python3 refA_h7_states.py
"""

import sys

from refA_columns_check import components_after, start_partition
import p3_striptm


def own_states(H):
    masks = list(range(1, 1 << H))
    states = set()
    frontier = []
    for m in masks:
        st = (m, start_partition(H, m))
        if st not in states:
            states.add(st)
            frontier.append(st)
    k = 0
    expanded = set()
    while k < len(frontier):
        mask, part = frontier[k]
        k += 1
        if (mask, part) in expanded:
            continue
        expanded.add((mask, part))
        ocells = [b for b in range(H) if (mask >> b) & 1]
        for m2 in masks:
            p2 = components_after(H, mask, part, ocells, m2)
            if p2 is None:
                continue
            if (m2, p2) not in states:
                states.add((m2, p2))
                frontier.append((m2, p2))
    return states


def main():
    H = 7
    mine = own_states(H)
    p3s, _edges, _starts, _accept = p3_striptm.build_states(H)
    p3set = set(p3s.keys())
    print("H=%d  own TM states: %d   p3 build_states: %d"
          % (H, len(mine), len(p3set)))
    only_p3 = sorted(p3set - mine)
    only_own = sorted(mine - p3set)
    for mask, part in only_p3:
        print("p3-only state: mask=%s part=%s" % (bin(mask), part))
    for mask, part in only_own:
        print("own-only state: mask=%s part=%s" % (bin(mask), part))
    # also print both counts for H=1..6 as a control
    for h in range(1, 7):
        m = len(own_states(h))
        p, _e, _s, _a = p3_striptm.build_states(h)
        print("H=%d control: own=%d p3=%d" % (h, m, len(p)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
