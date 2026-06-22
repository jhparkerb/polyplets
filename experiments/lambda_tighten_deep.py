#!/usr/bin/env python3
# Depth-d ancestor-exclusion bound on the polyplet growth constant lambda.
# Generalizes lambda_tighten.py (d=2, grandparent -> 16.63). A node's child cell cannot
# coincide with ANY ancestor cell; remembering the last d edge-directions, we forbid the
# child landing on any of the d nearest ancestors. Every embedded king-tree obeys this, so
# the constrained direction-labelled tree count still OVER-counts polyplets => a rigorous
# upper bound lambda <= 1/x_c, and larger d only removes more, so it is monotone tighter.
# State = (u_1,...,u_d) edge-direction history (u_1 = parent->node). Ancestor_k sits at
# -(u_1+...+u_k) relative to the node; a child direction c is excluded iff c = -(prefix sum)
# for some k (which is automatically a king-step when it lands on a neighbour).
import sys

DIRS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
DSET = set(DIRS)


def excluded(hist):                       # directions forbidden for a child, given history
    excl = set()
    sx = sy = 0
    for (dx, dy) in hist:                  # prefix sums of the history
        sx += dx; sy += dy
        c = (-sx, -sy)
        if c in DSET:                      # ancestor sits one king-step from the node
            excl.add(c)
    return excl


def bound_for_depth(d):
    # enumerate states = length-d histories; allowed children + child's next state
    def histories(k):
        if k == 0:
            return [()]
        return [(a,) + rest for a in DIRS for rest in histories(k - 1)]
    states = histories(d)
    allowed = {}
    nextstate = {}
    for s in states:
        ex = excluded(s)
        al = [c for c in DIRS if c not in ex]
        allowed[s] = al
        nextstate[s] = {c: (c,) + s[:d - 1] for c in al}   # shift c in, drop oldest

    # x_c = sup{ x : scalar fixed point y_s = x * prod_{c}(1 + y_{next}) stays bounded }.
    # Converges iff x <= x_c; bisect. Then lambda <= 1/x_c.
    def converges(x, iters=2000):
        y = {s: 0.0 for s in states}
        for _ in range(iters):
            ny = {}
            ok = True
            for s in states:
                p = x
                ns = nextstate[s]
                for c in allowed[s]:
                    p *= (1.0 + y[ns[c]])
                if p > 1e12:
                    ok = False
                    break
                ny[s] = p
            if not ok:
                return False
            # early-out when stable
            if max(abs(ny[s] - y[s]) for s in ny) < 1e-13 and len(ny) == len(states):
                return True
            y = ny
        return True
    lo, hi = 0.0, 0.2
    for _ in range(54):
        mid = (lo + hi) / 2
        if converges(mid):
            lo = mid
        else:
            hi = mid
    return 1.0 / lo, len(states)


print("classic tree bound 7^7/6^6 = %.4f" % (7 ** 7 / 6 ** 6))
maxd = int(sys.argv[1]) if len(sys.argv) > 1 else 4
for d in range(1, maxd + 1):
    lam, ns = bound_for_depth(d)
    print(f"  depth d={d}  ({ns:5d} states)  lambda_polyplet <= {lam:.4f}")
