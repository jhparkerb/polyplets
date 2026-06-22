#!/usr/bin/env python3
# Tighten the polyplet growth-constant upper bound lambda <= 7^7/6^6 = 17.65.
#
# That bound counts direction-labelled spanning trees forbidding only the
# toward-PARENT direction per node (7 free of 8). A polyplet's true spanning tree
# also never revisits the GRANDPARENT cell, so forbidding that overlap too still
# over-counts (valid embedded trees subset constrained trees subset all trees), giving
# a STRICTLY TIGHTER yet still rigorous bound: lambda_polyplet <= growth(constrained).
#
# State = (u, w): u = parent->node king-vector, w = grandparent->parent king-vector.
# Node at N has parent P=N-u, grandparent G=N-u-w. A child C=N+c coincides with
#   P  iff c = -u                 (always forbidden -> the classic "7")
#   G  iff c = -(u+w)             (forbidden only when u+w is itself a king-step)
# A surviving child in direction c becomes state (c, u). The constrained
# direction-labelled tree GF  T_{u,w}=x * prod_{c allowed}(1+T_{c,u})  has growth rate
# lambda_bound = lim t_n^{1/n}; we read it from the coefficient ratios.
DIRS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]
def king(v): return v != (0, 0) and max(abs(v[0]), abs(v[1])) == 1
def neg(v): return (-v[0], -v[1])
def add(a, b): return (a[0] + b[0], a[1] + b[1])

def allowed(u, w):
    excl = {neg(u)}
    s = add(u, w)
    if king(s):
        excl.add(neg(s))
    return [c for c in DIRS if c not in excl]

N = 60
states = [(u, w) for u in DIRS for w in DIRS]
A = {s: allowed(*s) for s in states}
# branching histogram (sanity: how many children-directions per state)
from collections import Counter
hist = Counter(len(A[s]) for s in states)
print("child-directions per state (8 dirs minus parent, minus grandparent-if-adjacent):",
      dict(sorted(hist.items())))

T = {s: [0.0] * (N + 1) for s in states}
for _ in range(N + 1):                      # one pass fixes one more coefficient
    newT = {}
    for s in states:
        u, w = s
        prod = [0.0] * (N + 1); prod[0] = 1.0
        for c in A[s]:
            f = T[(c, u)]
            nxt = [0.0] * (N + 1)
            for i in range(N + 1):
                pi = prod[i]
                if pi == 0.0:
                    continue
                nxt[i] += pi                # *(1 + ...) -> the "1"
                for j in range(1, N + 1 - i):
                    nxt[i + j] += pi * f[j]  # the "+T[child]"
            prod = nxt
        res = [0.0] * (N + 1)
        for n in range(N):
            res[n + 1] = prod[n]            # *x
        newT[s] = res
    T = newT

tot = [sum(T[s][n] for s in states) for n in range(N + 1)]
print("\nratio t_n/t_(n-1) -> lambda_bound (converges from below):")
prev = None
for n in range(40, N + 1, 4):
    r = tot[n] / tot[n - 1]
    print(f"  n={n:3d}  ratio={r:.4f}")
    prev = r
print(f"\nclassic tree bound 7^7/6^6 = {7**7/6**6:.4f}")

# Pin lambda_bound = 1/x_c rigorously-in-spirit: the scalar fixed point y_s = x*prod(1+y_t)
# has a finite positive solution iff x <= x_c; the largest x that stays bounded gives
# x_c, and convergence at x=lo certifies x_c >= lo, hence lambda_bound <= 1/lo.
def converges(x, iters=4000):
    y = {s: 0.0 for s in states}
    for _ in range(iters):
        ny = {}
        for s in states:
            u, _w = s
            p = x
            for c in A[s]:
                p *= (1.0 + y[(c, u)])
            ny[s] = p
        if max(ny.values()) > 1e9:
            return False
        y = ny
    return True
lo, hi = 0.0, 0.1
for _ in range(60):
    mid = (lo + hi) / 2
    if converges(mid):
        lo = mid
    else:
        hi = mid
print(f"x_c ~ {lo:.7f}  ->  lambda_bound <= 1/x_c ~ {1/lo:.4f}")
print(f"so lambda_polyplet <= {1/lo:.3f}  (vs 17.65; the grandparent constraint)")
