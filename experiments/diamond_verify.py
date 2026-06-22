#!/usr/bin/env python3
# Numerically confirm the T3 proof's mechanics (docs/diamond-optimality.md):
#  (1) every king step has |du|+|dv| = 2  (u=x+y, v=x-y),
#  (2) the L1 diamond saturates the wall lemma |C| = W_u + W_v = a+c+4 = 4r and
#      encloses 2r^2-2r+1 cells -- matching M(4r) from results/maxhole.txt.
KING = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)]

# (1) the engine identity
assert all(abs(dx + dy) + abs(dx - dy) == 2 for dx, dy in KING)
print("(1) |du|+|dv| = 2 for all 8 king steps:  OK")

# (2) diamonds
M = {4: 1, 8: 5, 12: 13, 16: 25}  # exact, results/maxhole.txt
print("\n r  |sphere S_r|  hole |B_{r-1}|  a+c  W_u+W_v  4r  matches M(4r)?")
for r in range(1, 7):
    sphere = [(x, y) for x in range(-r, r + 1) for y in range(-r, r + 1)
              if abs(x) + abs(y) == r]
    ball = [(x, y) for x in range(-(r - 1), r) for y in range(-(r - 1), r)
            if abs(x) + abs(y) <= r - 1]
    us = [x + y for x, y in ball]; vs = [x - y for x, y in ball]
    a = max(us) - min(us); c = max(vs) - min(vs)
    Wu = max(x + y for x, y in sphere) - min(x + y for x, y in sphere)
    Wv = max(x - y for x, y in sphere) - min(x - y for x, y in sphere)
    formula = 2 * r * r - 2 * r + 1
    n = 4 * r
    ok = (len(sphere) == n and len(ball) == formula and a + c == n - 4
          and Wu + Wv == n and (M.get(n) == formula if n in M else True))
    print(f" {r}     {len(sphere):3d}        {len(ball):4d}        {a+c:3d}   "
          f"{Wu+Wv:4d}    {n:3d}   {'OK' if ok else 'FAIL'}"
          + (f"  (M({n})={M[n]})" if n in M else ""))
print("\nAll diamonds saturate |C| = W_u+W_v = a+c+4 = 4r and enclose 2r^2-2r+1.")
