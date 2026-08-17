#!/usr/bin/env python3
"""Session 03: machine receipts for the two OEIS identifications of
directed-convex KING animals (phase parse stays in {(0,0),(1,0)}, i.e. the
top boundary r is non-decreasing):

 (1) semiperimeter sequence a_dir(s) = Sum_{w+h=s} d(w,h) equals A014300
     shifted: a_dir(s) = A014300(s-1), via A014300's binomial formula
     a(n) = Sum_{j=0..floor((n-1)/2)} C(2n-2j-2, n-1);
     plus its twist identity 2*A(n) + A(n-1) = (3n-1)*Catalan(n-1)
     (the same 2a(s)+a(s-1) twist as the full convex family, s02).
 (2) exact n x n box count d(n,n) = A112029(n-1) = Sum_{k=0..n-1} C(n-1+k,k)^2.
 (control) directed-convex polyominoes: a_dir_poly(s) = C(2(s-2), s-2)
     (central binomials) and d_poly(n,n) = C(2n-2, n-1)^2.

All exact integer arithmetic, boxes up to 17x17.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from math import comb
import s03_directed_convex as dc

dc.N = 17
N = dc.N


def A014300(n):
    return sum(comb(2 * n - 2 * j - 2, n - 1) for j in range((n - 1) // 2 + 1))


def catalan(n):
    return comb(2 * n, n) // (n + 1)


f = dc.table(king=True)
a = [sum(f[w][s - w] for w in range(max(1, s - N), min(s, N + 1)))
     for s in range(2, N + 2)]
ok1 = all(a[s - 2] == A014300(s - 1) for s in range(2, N + 2))
print(f"(1) a_dir(s) == A014300(s-1) for s=2..{N+1}: {ok1}")
ok1b = all(2 * A014300(n) + A014300(n - 1) == (3 * n - 1) * catalan(n - 1)
           for n in range(2, 40))
print(f"    twist 2A(n)+A(n-1)==(3n-1)Cat(n-1) for n=2..39: {ok1b}")
ok2 = all(f[n][n] == sum(comb(n - 1 + k, k) ** 2 for k in range(n))
          for n in range(1, N + 1))
print(f"(2) d(n,n) == Sum C(n-1+k,k)^2 (A112029) for n=1..{N}: {ok2}")

g = dc.table(king=False)
okc1 = all(sum(g[w][s - w] for w in range(max(1, s - N), min(s, N + 1)))
           == comb(2 * (s - 2), s - 2) for s in range(2, N + 2))
okc2 = all(g[n][n] == comb(2 * n - 2, n - 1) ** 2 for n in range(1, N + 1))
print(f"(control) poly a_dir(s)==C(2s-4,s-2): {okc1}; "
      f"d(n,n)==C(2n-2,n-1)^2: {okc2}")
assert ok1 and ok1b and ok2 and okc1 and okc2
print("all identifications verified exactly")
