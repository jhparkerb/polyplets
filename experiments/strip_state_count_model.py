from math import comb
from functools import lru_cache

@lru_cache(None)
def bell(n):
    if n == 0: return 1
    return sum(comb(n-1, k) * bell(k) for k in range(n))

def cat(n):
    return comb(2*n, n)//(n+1)

# N(H,r): binary strings of length H with exactly r maximal runs of 1s.
# choose r block lengths >=1 summing to m, and r+1 gaps (interior gaps >=1, ends >=0)
def N(H, r):
    if r == 0: return 1
    tot = 0
    for m in range(r, H+1):          # total occupied cells
        blocks = comb(m-1, r-1)      # compositions of m into r positive parts
        g = H - m                    # total gap cells
        # r-1 interior gaps >=1, 2 end gaps >=0  -> subtract (r-1)
        if g < r-1: continue
        gaps = comb(g - (r-1) + (r+1) - 1, (r+1) - 1)
        tot += blocks * gaps
    return tot

actual = {9:2187, 10:5797, 11:15510, 12:41834, 13:113633,
          14:310571, 15:853466, 16:2356778}

print(f"{'H':>3} {'actual':>10} {'runs only':>10} {'x Catalan':>12} {'x Bell':>14}")
for H in sorted(actual):
    runs = sum(N(H,r) for r in range(0, H//1+1) if N(H,r))
    nc  = sum(N(H,r)*cat(r) for r in range(0, H+1))
    al  = sum(N(H,r)*bell(r) for r in range(0, H+1))
    print(f"{H:>3} {actual[H]:>10} {runs:>10} {nc:>12} {al:>14}")

print()
print("growth ratios")
ks = sorted(actual)
for a,b in zip(ks, ks[1:]):
    ncA = sum(N(a,r)*cat(r) for r in range(0,a+1)); ncB = sum(N(b,r)*cat(r) for r in range(0,b+1))
    alA = sum(N(a,r)*bell(r) for r in range(0,a+1)); alB = sum(N(b,r)*bell(r) for r in range(0,b+1))
    print(f"  {a}->{b}: actual {actual[b]/actual[a]:.3f}  NC {ncB/ncA:.3f}  Bell {alB/alA:.3f}")
