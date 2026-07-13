# The solvable-subfamily sweep of the king lattice (2026-07-14)

Question #4 of the fresh-questions menu: which convexity/directedness
subfamilies of polyplets are unsolved and absent from OEIS? Answer: NONE
are absent -- but two land on known sequences with genuinely NEW
combinatorial interpretations, provable with one-line Temperley
derivations. Classifier + checks: `experiments/king_subfamilies.py`.

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

**The meta-finding:** every classical restriction (grounded, directed,
staircase) collapses king animals into composition/partition-land or a
known sequence -- corner contact makes connectivity too easy to be
interesting under these restrictions. The genuinely king-specific objects
remain the full count (A006770) and the HV-convex family (the Mirage).
No new sequences to submit; two comment-grade interpretations staged
conceptually (jasonp's call).
