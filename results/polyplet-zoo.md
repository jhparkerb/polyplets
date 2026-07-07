# The polyplet zoo: properties, relationships, rough proportions at size n

2026-07-07. A reference catalog, prompted by an evening spent probing
structural properties of king-connected polyplets (A006770). Organizes
what's exactly tracked, what's sampled-only, what's discussed-but-not-built,
how properties relate to each other, and rough size-n behavior. Growth
constant throughout: lambda ~= 7.11 (Domb-Sykes fit on the 34 known terms,
this session; matches the ~7.1 already in project memory).

## Metric properties (geometry of the bounding box / cell placement)

| property | tracked? | range at size n | asymptotic / rough proportion |
|---|---|---|---|
| **height H** | exact, all n (the core T(n,H) triangle) | 1..n | peaks around H ~= 0.38n (a34: peaks at H=13 of 34); T(n,n)=3^(n-1) exact closed form at the diagonal |
| **bounding box (W,H) jointly** | exact, oracle-scale only (n<=~19, `byBox`) | W,H >= 1, W*H >= n | transpose-symmetric: byBox[n][w][h]==byBox[n][h][w] (gate F) |
| **edge-perimeter P** (rook-based, 4n - 2*rook-edges) | exact, BOTH oracle and production TM (`--perimeter`) | roughly [O(sqrt n), 4n] | max (4n) hit exactly by the 0-rook-edge (entirely-diagonal) shapes; min shrinks toward compact-blob scaling |
| **site-perimeter** (king/8-adjacency variant) | exact, oracle-scale only | different convention, cross-checked vs a percolation-literature source | not further characterized this session |

## Topological properties (holes)

| property | tracked? | range | asymptotic / rough proportion |
|---|---|---|---|
| **hole count** | exact, both oracle and production TM (`--holes`) | 0..~n/4ish (empirically small counts dominate) | hole-free fraction SHRINKS with n: ~73.4% at n=18 (16,503,616,943,998 / 22,471,158,811,164), falling as n grows -- more room for enclosed regions in bigger shapes |
| **hole area (M(n) = max single-hole area)** | exact for n<=16 (M17 in flight tonight, dalby) | 0..~n^2/8 | conjectured M(n) ~ round((n-2)^2/8), A001971 shift; first untested prediction M(17)=28 |
| **interior cells (I)**: cells with all 4 rook-neighbors present | NOT directly tracked, but exactly bracketed by perimeter (this session) | 0..n | **n - P <= I <= n - P/4** (exact, provable); empirically the upper bound is tight for real large (spindly) shapes (mean slack 2.73 at n=12), lower bound is nearly useless (mean slack 25) |

## Edge-type / connectivity-flavor properties

| property | tracked? | range | asymptotic / rough proportion |
|---|---|---|---|
| **diagonal-contact count** | exact, oracle-scale (`--contacts`, `byContacts`) | 0..2n | -- |
| **rook-edge count** | NOT a dedicated flag yet (buildable, same machinery as `--contacts`); sampled this session (n=12, 2000 draws) | 0..~n-1 (spanning-tree cap; more with cycles) | **unimodal, peaks near the middle** (6 of ~11 at n=12, 19.85%) -- NOT concentrated near 0 (see below) |
| **entirely-diagonal (0 rook edges)** | exact, oracle-scale (`bishopConn == A001168`, gated) | binary flag | fraction = A001168(n)/a(n) -- vanishing fast: A001168 grows ~4.06^n, a(n) grows ~7.11^n, ratio ~ (4.06/7.11)^n -> 0. Measured 0.20% at n=12 |
| **entirely-rook (ordinary polyomino)** | exact, oracle-scale (`rookConn == A001168`, gated) | binary flag | same vanishing fraction, same reason (rook<->bishop are an exact isomorphic pair, both count A001168(n)) |
| **rook<->bishop "dual" existence** (does swapping which edges are rook vs bishop, keeping the same abstract graph, realize as ANOTHER valid polyplet?) | sampled this session (backtracking search, n=12, n<=300) | binary per-shape | **1% found, 99% PROVEN not to exist** (exhaustive search, not budget-limited) -- n=3's self-dual asymmetric class was a small-n artifact (only 2 possible connected 3-vertex graphs exist at all) |

## Structural / graph-theoretic properties

| property | tracked? | range | asymptotic / rough proportion |
|---|---|---|---|
| **cut vertices (articulation points, full king graph)** | sampled this session (n=12, 2000 draws) | 0..n-2ish | 99.9% have >=1 (mean 6.7 of 12) -- large polyplets are close to the tree-like extreme, not blob-like |
| **biconnected blocks**: count, max size, mean size | sampled this session | count: 1..n; sizes: 2..n | mean max-block-size 3.97 (of 12), mean block size 2.39, mean 8.47 blocks/shape -- most "hard" 2-connected structure is small and local |
| **cyclomatic number** (edges - vertices + 1, independent-cycle count) | NOT tracked; discussed as plausible (DP already distinguishes tree-merge vs cycle-closing events) | 0..~n | not measured; would follow from block-size data (blocks of size 2 contribute 0, bigger blocks contribute their own internal cycle count) |
| **rook-only components** ("how many separate ordinary polyominoes is this built from") | sampled this session | 1..n | 99.8% are NOT single polyominoes (mean 6.575 separate pieces of 12), needing mean 5.575 diagonal glue-edges -- the worst-fragmented of the three edge-restriction splits tried |

## Symmetry properties (the companion-sequence family)

| property | tracked? | range | asymptotic / rough proportion |
|---|---|---|---|
| **stabilizer under D4** (asymmetric / one mirror / one rotation / full D4 etc.) | exact via symtm (r90, r180, hmirror, dmirror fixed-point counts), T1 to n=24, T2 n=25-32 | 8 possible subgroups of D4 | symmetric sub-counts (R90, R180, H, D) are "sqrt(a(n))-scale" per the report -- asymmetric fraction -> ~100% as n grows (folklore-consistent: almost all large lattice animals are totally asymmetric) |
| **Burnside-derived companion counts** (Free, OneSided, Bilateral, Asymmetric) | exact, derived via `derive_related.py` from Fixed + symmetry counts | -- | Bilateral = (H+D)/2 (exact identity, drill-verified this session); OneSided = (Fixed+2R90+R180)/4 |

## Diagonal-strip structure (a DIFFERENT parameterization: not per-shape, per diagonal-mirror-strip)

| property | tracked? | notes |
|---|---|---|
| **d(S, S+k)**: diagonal-mirror-symmetric count at bounding box SxS, k extra cells | exact direct strips S<=28 for n=33; pinned closed forms P_k for k<=5 | period-2 quasi-polynomial in S, degree k, onset ~2k+2; P_5-odd still fitted not pinned |

## Known exact relationships (identities, not just correlations)

1. **Bilateral = (H + D)/2** -- Burnside double-count over reflections vs. over free classes (drill 1, this session, both directions verified at n=2,3).
2. **Rook <-> bishop (both diagonals) isomorphism**: exact graph isomorphism via (p,q)=((c+r)/2,(c-r)/2) restricted to one checkerboard color; this is WHY rookConn==bishopConn==A001168 exactly, not approximately.
3. **Perimeter/interior-cell bracket**: n - P <= I <= n - P/4 (exact, from d(c) in {0,1,2,3,4} definitions).
4. **Hole-fill bijection**: {n-cell, 1-hole, area-1 polyplets} <-> {(T,x): T hole-free size n+1, x an interior non-cut-vertex cell of T} -- exact, and the combined identity 1-hole-area-1(n) = sum_T (interior, non-cut-vertex cells of T) ties properties 3 and this list's cut-vertex row together. One-directional only (fill is free; un-fill needs T's full interior+cut-vertex structure) -- see `hole-fill-interior-cell-identity.md`.
5. **T(n,n) = 3^(n-1)** exact closed form at the top diagonal (every cell forced into the bounding box).

## What's NOT in this zoo (checked and killed this session, not just omitted)

Crossing-partition / Temperley-Lieb compression of the frontier (measured negative, `boundary-push-tensornetwork.md`); a literal diagonal (anti-diagonal) sweep direction (real state-explosion, reach-2 problem, verified by definition); rook+one-diagonal / both-diagonals-as-2-layers / rook-only-as-base decompositions (all measured: correction is NOT sparse, 96.7%-99.8% disconnected); #SAT/ASP/ZDD/Gröbner/holographic-algorithm/quantum/symbolic-regression alternatives to the counting engine itself (all separately killed, see this session's transcript and the `viva`/drill discussion context).

## Honest summary

Every property above that's cheap to compute (perimeter, holes, height, rook-edge count) is either exactly tracked already or a small extension of existing machinery. Every property that would require GLOBAL shape knowledge (cut vertices, block structure, interior-cell-minus-cut-vertex counts) resists cheap incremental tracking during a column/kink sweep, for the same reason each time: it depends on connectivity resolved arbitrarily later in the sweep, not on the local frontier state. That asymmetry -- cheap local statistics vs. hard global ones -- is the one structural fact that keeps reappearing across every different-looking probe this session.
