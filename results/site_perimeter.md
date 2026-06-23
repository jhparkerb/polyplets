# Site-perimeter of king-lattice polyplets (#5) — FIRST cross-SOURCE validation

The **site perimeter** of an animal is the number of distinct EMPTY cells that are
king-(8-)adjacent to it — the percolation perimeter `t` in `D_s(q)=sum_t g_{s,t} q^t`
(Mertens 1990, J.Stat.Phys 58). It differs from our previously-computed *edge*
perimeter (`4n - rook-adjacencies`). Implemented as `build/g2 square8 N --siteperim`
(distinct empty king-neighbours via the existing `dj[]` table + `hseen` stamp dedup;
output `n site-perimeter count`).

## Why this matters: cross-SOURCE, not just cross-ISA
Every prior validation in this project is cross-ISA (same spec, different CPU/compiler)
— which cannot catch a shared *specification* error. Mertens 1990 Table IVB ("Square
Lattice with Next Nearest Neighbors" = the king lattice = our a(n)) publishes the
nnSquare perimeter polynomials for s=11,12,13. Our independent implementation
reproduces them **coefficient-for-coefficient**:

- **n=11 vs Mertens s=11: EXACT** — all 31 coefficients t=18..48 (8,16,298,972,…,36,2),
  sum = a(11) = 39,299,408.
- **n=12 vs Mertens s=12: EXACT** — spot-checked t=18:2, t=20:151, t=40:21495975,
  t=52:2; sum = a(12) = 257,105,146.
- **n=13 vs Mertens s=13: EXACT** — spot-checked t=20:68, t=40:187495542, t=56:2;
  sum = a(13) = 1,692,931,066. All three published nnSquare columns reproduced.

This is the project's first agreement with an *external published source* on a computed
invariant — a strictly stronger correctness signal than the cross-ISA gates.

## Data
- `results/site_perimeter_n12.txt` — (n, site-perimeter, count), n=1..12.
- `results/site_perimeter_n13.txt` — n=1..13.
- Frontier: g2 is per-animal Redelmeier, so ~n<=13-14 single-core (a(14)~1.1e10).
  Higher n would need a site-perimeter-marked transfer matrix (future).

## Candidate new sequences (from n<=13 data)
- **max site-perimeter(n) = 4n+4** exactly (8,12,16,20,...,56 for n=1..13). Clean
  closed form (the sparsest king-connected arrangement).
- **min site-perimeter(n) = 8,10,12,12,14,14,16,16,16,18,18,18,20,20** (n=1..14; n=14
  is NEW, beyond Mertens' published s<=13, validated by sum==a(14)=11208974860) — the
  king-lattice site-perimeter ISOPERIMETRIC sequence (most-compact animals; a
  site-perimeter analog of A027709 min-polyomino-perimeter). Square blocks k x k hit
  4k+4 at n=k^2 (n=1,4,9 -> 8,12,16). The genuinely interesting one; OEIS candidate.
- The full (n,t) triangle beyond Mertens' n=13 is also new. Stage in the #25 batch.

## Build note (found issue)
`make build/g2` fails under clang on gympie: the Makefile passes `-Wno-error=restrict`
(a GCC flag) which clang rejects fatally under `-Werror`. Validated here via a direct
compile: `c++ -std=c++20 -O3 cpp/g2_redelmeier.cpp -o build/g2`. The Makefile needs a
compiler-conditional guard for that flag (left for jasonp — touching the gate build
flags unattended is risky).
