# The solvable-subfamily sweep of the king lattice (2026-07-14)

Question #4 of the fresh-questions menu: which convexity/directedness
subfamilies of polyplets are unsolved and absent from OEIS? Answer: NONE
are absent -- but two land on known sequences with genuinely NEW
combinatorial interpretations, provable with one-line Temperley
derivations. Classifier + checks: `experiments/king_subfamilies.py`.

**Entry point, 2026-08-05:** this note is one input to the Middle Kingdom
campaign, which crossed the convexity and directedness axes completely and
superseded the "NONE are absent" answer above. `results/middle-kingdom.md`
is the current overview of the family -- the 5x4 grid, the novel cells, the
b-files and the staged OEIS comments. Read that first; this note for the
derivations it cites.

| subfamily (king lattice) | first terms | identity |
|---|---|---|
| column-convex | 1,4,18,83,385,... | A187077 (Bevan; our derivation results/convex-polyplets.md) |
| bargraph (grounded columns) | 2^(n-1) | compositions -- king contact trivializes connectivity |
| Ferrers (grounded, monotone) | 1,2,3,5,7,11,... | partitions A000041 (trivially) |
| stack (grounded, unimodal) | 1,2,4,8,15,27,47,79 | unimodal compositions A001523 |
| **directed column-convex** | 1,3,10,34,116,396,... | **A007052** -- NEW interpretation |
| **staircase (both boundaries monotone)** | 1,3,9,28,87,272,... | **A225114 = skew shapes** -- NEW, with proof |

**Theorem (dcc).** Directed column-convex polyplets (column intervals,
bottoms nondecreasing) with n cells are counted by A007052
("order-consecutive partitions"): placements of a height-h' column against
height-h are h+1 (bottom shift in [0,h], king reach caps at top+1),
independent of h', so Temperley closes to GF = x(1-x)/(1-4x+2x^2),
a(n) = 4a(n-1)-2a(n-2), growth exactly 2+sqrt(2). Matches A007052's GF
verbatim (offset 1 vs 0); 10 terms verified. A007052 previously had
poker/Pell/path interpretations but no lattice-animal one.

**Theorem (staircase).** King staircase animals (column intervals, bottoms
AND tops nondecreasing) = skew Young diagrams with no empty rows/columns
(A225114), by the identity map: monotone boundaries make the columns a skew
shape; "no empty rows" forces bottom_{i+1} <= top_i + 1, which is exactly
king contact, and conversely. 8 terms verified.

**Draft comment (staged 2026-08-05, jasonp's call):**

> a(n) is also the number of staircase polyplets with n cells: king-lattice
> animals (sets of cells of Z^2 joined by edge or corner contact, counted up
> to translation) in which every column is a contiguous interval and both the
> column bottoms and the column tops are nondecreasing from left to right.
> The identity is the identity map on diagrams. Monotone bottoms and tops
> make the occupied columns a skew shape; a diagram with no empty row is one
> in which bottom(j+1) <= top(j) + 1 for every pair of consecutive columns,
> and that inequality is exactly corner contact between those columns, so the
> no-empty-row condition and king-connectivity are the same condition.
> Verified for n <= 8. Cf. A006770, A007052, A018902, A187077.

Prior text for the same edit, written 2026-07-14 before the grid work, is in
`oeis/draft-comments-subfamilies.txt`; the version above is the current one.
The animal side is independently brute-forced to n = 14 -- 1, 3, 9, 28, 87,
272, 850, 2659, 8318, 26025, 81427, 254777, 797175, 2494307
(`results/mk_grid20_n14.txt`) -- but only the first 8 were matched against
the entry's own data, which is what the comment claims. The same 14 terms are
what the four collapsed staircase cells of the grid produce
(`results/middle-kingdom-phase3.md`, Corollary 4).

**The meta-finding:** every classical restriction (grounded, directed,
staircase) collapses king animals into composition/partition-land or a
known sequence -- corner contact makes connectivity too easy to be
interesting under these restrictions. The genuinely king-specific objects
remain the full count (A006770) and the HV-convex family (the Mirage).
No new sequences to submit; three comment-grade interpretations staged
conceptually (jasonp's call).

## Addendum 2026-07-23: half-plane directed king animals = A055834

Source: external working notes (~/Downloads/polyplet-enumeration-directions.md,
claims re-verified here from scratch). Model: n-cell sets containing the
origin, every cell reachable from the origin via steps (0,1), (1,0),
(1,1), (1,-1) within the set — the four-step forward cone {N, NE, E, SE}.

| subfamily (king lattice) | first terms | identity |
|---|---|---|
| **half-plane directed** | 1,4,18,85,413,2044,... | **A055834** -- NEW interpretation |

**Distinct from Bacher's directed king animals** (A047781 = 1,4,19,96,...,
growth 3+2sqrt(2); results/directed-king-animals.md): Bacher's forward cone
is FIVE directions {W, NW, N, NE, E} with horizontal steps counted as
forward and a leftmost-bottommost source. The four-step cone diverges at
n=3 (18 vs 19) and has growth 27/5 = 5.4 (Kotesovec's asymptotic on the
entry), consistent with the smaller cone.

**Verification:** independent Redelmeier-style untried-set DFS
(`experiments/directed_halfplane.cpp`, ~6s to n=15) matches Alekseyev's
formula a(n) = Sum_k C(n+k-1,n)*C(k,n-k) AND the A055834 data (offset 0)
exactly for all n <= 15 — including 36196706 (n=12), 187938842 (n=13),
978599560 (n=14), 5108177816 (n=15), all beyond the source doc's own n=11.
A055834's entry (Kimberling 2000) is defined purely as array diagonal
T(2n,n) of A055830 — no combinatorial interpretation, no animal
references; OEIS search on the terms hits A055834 uniquely.

**Draft comment (staged, jasonp's call):**

> Conjecture: for n >= 1, a(n) is the number of n-celled directed
> polyplets in the four-step cone (directed site animals on the king
> lattice with steps (0,1), (1,0), (1,1), (1,-1)), i.e., sets of n cells
> of Z^2 containing the origin such that every cell can be reached from
> the origin by those steps without leaving the set. Verified for n <= 15.
> Cf. A006770, A030222, A047781.

**Prior-art pass:** Bacher arXiv:1301.1365 = the 5-step model only. The
quarter-cone variant (steps (1,0),(0,1),(1,1)) = C(2n-1,n-1) = A001700 is
KNOWN — A001700 already cites directed-animal literature (Bousquet-Melou,
Discr. Math. 180 (1998) Eq. (1); Baril–Bevan–Kirgizov) — do not claim it.
Open before any novelty claim beyond conjecture-grade: check the
Bousquet-Melou–Conway non-planar L_n family Eq-by-Eq for the 4-step cone
(GF is algebraic via A001002 per Kruchinin's formula on the entry, so a
heaps-of-pieces/gas derivation likely exists and would upgrade the
conjecture to a theorem).

## Addendum 2026-08-05: the meta-finding, sharpened by Phase 3

`results/middle-kingdom-phase3.md` crossed the directedness and convexity axes
completely (a 5x4 grid). The reason every classical restriction collapses is
now a proposition rather than an observation: **on a column-convex king animal
each directedness predicate is a condition on the bottom profile alone**, and
HV-convexity already forces that condition. HV-convex ⊂ 5-cone directed,
staircase ⊂ both cones, column-convex ⊂ multi-directed. Eight of the grid's
twelve open cells are equalities with the unfiltered row for that reason.

A fourth comment-grade interpretation joins the three above:

| subfamily (king lattice) | first terms | identity |
|---|---|---|
| **4-cone directed column-convex** | 1,4,17,73,314,1351,... | **A018902**, g.f. x(1-x)/(1-5x+3x^2) -- NEW interpretation, and it explains the entry's INVERT-of-A007052 formula: cut the profile at each one-row drop and the pieces are the A007052 class above |

Three cells resist and are new sequences: (5-cone, column-convex), (control B,
column-convex) and (4-cone, HV-convex). So "no new sequences to submit" is no
longer the whole story for this family, though submission remains jasonp's
call.
