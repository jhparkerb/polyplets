#!/usr/bin/env python3
"""#32 multi-box height-scheduling calculator (Q2||Cmax).

The fold engine computes each bounding-box height H as an INDEPENDENT sweep, but
a single height is ATOMIC across machines: parallelizing one height across boxes
would need a per-column frontier shuffle (the column transition moves states
between key-ranges), which is a network all-to-all with no shared FS -- a loss at
2-box scale (see designs/07). So cross-machine scheduling assigns whole heights to
boxes, and the question is makespan (Cmax) on two UNEQUAL machines.

Cost model: height H costs ~r^H (geometric, r~=2.0-2.4 measured), so the top two
heights are ~80% of the work and the top height H=N is atomic at ~50-58%. A box
runs its assigned heights sequentially (one height fills all its cores); its
finish time = (sum of assigned costs) / throughput. Makespan = max over boxes.

This evaluates the candidate schemes against the perfectly-divisible ideal. Feed
it the geometric model now; once a(20)/a(21) `--per-height-out` land, feed the
measured per-height cpu-seconds via --costs to re-rank on real numbers.

Usage:
    heightsplit_plan.py [--N 22] [--r 2.4] [--sa 25.5] [--sb 44.5]
                        [--costs FILE]   # one "H cost" per line, overrides --r
Schemes (A = slow box / ayr ascending; B = fast box / dalby, gets the pole):
    contiguous  odd/even-heights  LPT-static  meet-in-the-middle  dynamic-pull
"""
import argparse
import sys


def geometric_costs(N, r):
    """Height H -> normalized cost (sum = 1), cost(H) ~ r^H."""
    raw = {H: r ** H for H in range(1, N + 1)}
    tot = sum(raw.values())
    return {H: c / tot for H, c in raw.items()}


def load_costs(path):
    cost = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            h, c = line.split()[:2]
            cost[int(h)] = float(c)
    tot = sum(cost.values())
    return {h: c / tot for h, c in cost.items()}


def makespan(A, cost, sa, sb):
    """A = set of heights on slow box (speed sa); the rest on fast box (sb)."""
    la = sum(cost[h] for h in A)
    lb = sum(cost[h] for h in cost if h not in A)
    return max(la / sa, lb / sb)


def ideal(cost, sa, sb):
    """Perfectly-divisible lower bound (also the atomic LB here, since the
    biggest job fits under it on the fast box)."""
    tot = sum(cost.values())
    return max(tot / (sa + sb), max(cost.values()) / max(sa, sb))


def scheme_contiguous(cost, sa, sb):
    """ayr gets a low contiguous block H1..k, dalby the high block. Best k."""
    hs = sorted(cost)
    best = None
    for k in range(len(hs) + 1):
        A = set(hs[:k])
        m = makespan(A, cost, sa, sb)
        if best is None or m < best[0]:
            best = (m, A)
    return best[1]


def scheme_oddeven(cost):
    """Fast box (dalby) takes heights of the same parity as the top (N, N-2, ...);
    slow box (ayr) takes the rest. Parameter-free."""
    N = max(cost)
    B = {h for h in cost if (N - h) % 2 == 0}   # N, N-2, N-4, ...
    return set(cost) - B                        # A = the rest


def scheme_lpt(cost, sa, sb):
    """Longest-Processing-Time first on unequal machines: each height (largest
    first) goes to whichever box would FINISH it soonest given current load."""
    la = lb = 0.0
    A = set()
    for h in sorted(cost, key=lambda x: -cost[x]):
        if (la + cost[h]) / sa <= (lb + cost[h]) / sb:
            A.add(h); la += cost[h]
        else:
            lb += cost[h]
    return A


def sim_mitm(cost, sa, sb):
    """Meet-in-the-middle: slow box pulls smallest-unclaimed (ascending), fast box
    pulls largest-unclaimed (descending); whichever box is free earlier claims
    next. Returns the slow-box set."""
    asc = sorted(cost)
    desc = sorted(cost, reverse=True)
    unclaimed = set(cost)
    ta = tb = 0.0
    A = set()
    while unclaimed:
        a_next = next((h for h in asc if h in unclaimed), None)
        b_next = next((h for h in desc if h in unclaimed), None)
        if a_next == b_next:                      # one height left
            if ta <= tb:
                A.add(a_next); ta += cost[a_next] / sa
            else:
                tb += cost[b_next] / sb
            unclaimed.discard(a_next)
        elif ta <= tb:                            # slow box free first, claims small
            A.add(a_next); ta += cost[a_next] / sa
            unclaimed.discard(a_next)
        else:                                     # fast box free first, claims large
            tb += cost[b_next] / sb
            unclaimed.discard(b_next)
    return A


def sim_dynamic_pull(cost, sa, sb):
    """Dynamic pull-queue: pin the single largest height to the fast box, then
    each box pulls the largest-unclaimed height whenever it goes idle (online
    LPT). Returns the slow-box set."""
    order = sorted(cost, key=lambda x: -cost[x])
    top = order[0]
    ta = 0.0
    tb = cost[top] / sb                            # pole pinned to fast box
    A = set()
    for h in order[1:]:
        if ta <= tb:
            A.add(h); ta += cost[h] / sa
        else:
            tb += cost[h] / sb
    return A


SCHEMES = [
    ("contiguous (#6 now)", lambda c, sa, sb: scheme_contiguous(c, sa, sb)),
    ("meet-in-the-middle",  lambda c, sa, sb: sim_mitm(c, sa, sb)),
    ("odd/even heights",    lambda c, sa, sb: scheme_oddeven(c)),
    ("LPT static",          lambda c, sa, sb: scheme_lpt(c, sa, sb)),
    ("dynamic pull",        lambda c, sa, sb: sim_dynamic_pull(c, sa, sb)),
]


def report(cost, sa, sb, label):
    N = max(cost)
    lo = ideal(cost, sa, sb)
    print(f"## {label}   N={N}  sa(ayr)={sa}  sb(dalby)={sb}  "
          f"ratio={sb/sa:.2f}  ideal(divisible)={lo:.5f}")
    top3 = sorted(cost.values(), reverse=True)[:3]
    print(f"   top-3 height weights: {top3[0]:.3f} {top3[1]:.3f} {top3[2]:.3f}"
          f"  (sum {sum(top3):.3f})")
    print(f"   {'scheme':22} {'makespan':>9} {'penalty':>8}   dalby gets")
    for name, fn in SCHEMES:
        A = fn(cost, sa, sb)
        B = sorted((h for h in cost if h not in A), reverse=True)
        m = makespan(A, cost, sa, sb)
        pen = 100 * (m / lo - 1)
        # show only the heaviest few dalby heights (the rest are tail)
        shown = ", ".join(str(h) for h in B[:6]) + ("..." if len(B) > 6 else "")
        print(f"   {name:22} {m:9.5f} {pen:7.1f}%   {{{shown}}}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=22)
    ap.add_argument("--r", type=float, default=2.4)
    ap.add_argument("--sa", type=float, default=25.5)
    ap.add_argument("--sb", type=float, default=44.5)
    ap.add_argument("--costs", default="")
    args = ap.parse_args()

    if args.costs:
        cost = load_costs(args.costs)
        report(cost, args.sa, args.sb, f"measured costs {args.costs}")
        return 0

    # Sweep the uncertain axes: geometric ratio r and the throughput pair.
    # measured this session: ayr 25.5/30 eff, dalby 44.5/80 (unfixed, merge-bound)
    # forecast (a22-forecast.md): ayr 30, dalby 76 (optimistic cross-process)
    tputs = [(25.5, 44.5, "measured-this-session"), (30.0, 76.0, "forecast")]
    for N in (args.N, args.N + 1):
        for r in (2.0, 2.4):
            for sa, sb, tlabel in tputs:
                cost = geometric_costs(N, r)
                report(cost, sa, sb, f"geometric r={r}  [{tlabel}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
