# OEIS submission drafts

Staged drafts in OEIS **internal format** (`%I %S %T %U %N %C %D %H %F %e %Y %K %O %A %E`).
**Nothing here is submitted.** These are reviewable, staged drafts; jasonp pushes the
actual submission to oeis.org — Claude prepares and stages, never submits to an external
service (see ROADMAP #25). Normal care for outward-facing steps; no signoff ceremony.

## Files
- `A######.txt` — an **existing** OEIS entry we extend. Commit history per file:
  1. first commit = the entry **verbatim** from OEIS (`?fmt=text`), unmodified;
  2. later commits = **our** additions (terms, comments, GF notes, cross-refs),
     one commit per change, with the **data provenance in the commit message**.
  So `git log -p A######.txt` shows exactly what we changed vs. OEIS.
- `draft-<name>.txt` — a **new** sequence we propose. Placeholder A-number
  (`Axxxxxx`) until OEIS assigns one.

## Provenance legend (for commit messages / %C)
- **flood** — per-animal 4-connected-background flood fill, exact, n ≤ 14.
- **engine** — column transfer matrix with Euler/hole accounting (`cpp/tma`,
  thread #28), exact; validated byte-identical to the flood (n ≤ 14) and k-sums
  match A006770. Reaches n ≈ 16–18 (exact counts), higher via mod-p for GFs.
- **cross-ISA** — independently reproduced on ayr (gcc/x86) vs gympie (clang/ARM).
- **confirmed** (a(n), A006770) — two architecture-decorrelated Redelmeier
  enumerations + an algorithm-independent transfer-matrix recount agree.

## Bylines
Author/extender bylines are `_Jason H Parker_` (OEIS contributor,
https://oeis.org/history?user=Jason%20H%20Parker). Only new-draft `%A` lines and our
`%E` extension credits carry this name; the original `%A` authors of extended entries
(Sloane, Cook, Wilson, Melik, ...) are preserved.

## Status
| file | status |
|---|---|
| A006770 (fixed) | extend: +a(19) confirmed; a(20) candidate, cross-ISA confirmation running |
| A030222 (free) | extend: +a(18),a(19) confirmed |
| A030233 (one-sided) | extend: +a(18),a(19) confirmed |
| A194596 (free, non-polyomino) | extend: +a(18),a(19) confirmed (= A030222 - A000105, per the entry's own formula); a(20)=128193840456415 candidate |
| A030234/A030235 (symmetric) | pending: verify our bilateral-symmetry counts first |
| draft hole triangle T(n,k) | new (4-bg convention), **exact through n=18; rows n=15..18 cross-ISA confirmed** |
| draft A_0 (hole-free), A_1 (one-hole) | new, **novelty-confirmed via Superseeker (2026-06-19)**; b-files `b-draft-A0-holefree.txt` (n=1..18), `b-draft-A1-onehole.txt` (n=4..18), **n=15..18 cross-ISA confirmed**; submission-ready. These ARE columns k=0,1 of the triangle (standalone per the OEIS triangle+headline-columns idiom; A_2,A_3,... are NOT minted separately) |
| draft M(n) = max hole AREA (draft-maxholearea.txt) | new; a DISTINCT statistic (max enclosed empty *area*, not a column of the count triangle); **exact to n=16, diamond-tight at n=4,8,12,16** |
| draft GF orders deg Q_H (draft-gf-orders.txt) | new, **Superseeker-novel**; 1,3,7,15,42,...,5005 (fixed-height GF denominator orders); lifetime-3 law |
| draft atom degrees deg N_H (draft-atom-degrees.txt) | new, **Superseeker-novel**; 1,2,4,9,29,...,3289 (the lifetime-3 atoms); H<=7 verified, H>=8 law-derived |
| draft free-polyplet symmetry classes (8: draft-sym-*.txt) | new, **plain-search novel** (Superseeker not yet run); the D4 exact-symmetry-group breakdown of A030222 to n=19 (asymmetric, axial, diagonal, C2, C4, D2-ortho, D2-diag, D4); validated (8 classes sum to A030222, 5 reflection classes sum to A030234); polyplet analogues of A006746/A006747/A006748/A006749/A056877/A056878/A142886/A144553, none of which had a polyplet counterpart |

## Novelty re-checks (OEIS, 2026-06-19)
- **A_0 (hole-free) and A_1 (one-hole): confirmed not in OEIS via Superseeker**
  (`superseeker@oeis.org`, the heavy program: direct lookup + the full T001–T115
  transform battery — ±constant, scaling, binomial, Euler, Möbius/Stirling,
  differences — plus gfun/Rate/guesss closed-form search). Both came back clean, so
  novelty is closed beyond a plain term-prefix search (the additive/transform
  "secretly a known sequence" cases are ruled out). Cross-checked independently by
  our own consecutive-run and first/second-difference oeis.org searches.
- Triangle T(n,k): covered by the A_0/A_1 column lookups — Superseeker's own advice
  is to look up an array's rows/columns/diagonals, not the flattened array; no
  separate flattened-triangle lookup needed.
- M(n) (max hole area; NOT a triangle column): definition is new, and the prior 9-term
  prefix 0,0,0,1,1,2,3,5,6 matched 16 unrelated short sequences -- now **disambiguated by
  extension to 16 terms** (0,0,0,1,1,2,3,5,6,8,10,13,15,18,21,25) via `maxhole_split` (C++
  Redelmeier+flood, 4-connected-background primary convention).
- **Lifetime-3 byproducts (results/lifetime3-proof.md), Superseeker 2026-06-21 -- BOTH NOVEL.**
  (a) atom degrees `1 2 4 9 29 68 181 462 1254 3289` (deg N_H) and (b) GF orders
  `1 3 7 15 42 106 278 711 1897 5005` (deg Q_H) each returned no match from
  superseeker-reply@oeis.org -- the complete run (direct lookup + the full T001-T115
  transform battery + closed-form search). **Staged: `draft-atom-degrees.txt` (Axxxxxe),
  `draft-gf-orders.txt` (Axxxxxd).**
- **Free-polyplet symmetry classes (8), 2026-06-21:** the D4 exact-symmetry-group
  breakdown of A030222. Each class's distinctive term-window returns "No results" on
  the OEIS consecutive-term search (only the coarse A030234/A030235 split existed for
  polyplets). Plain-search clean; a Superseeker pass per class is the gold standard
  still to run before submission. Derivation (`sym/symmetry_classes.py`) is validated:
  the 8 classes sum to A030222(n) and the five reflection classes to A030234(n) for all
  n <= 19 (the latter is the proven bilateral = (H+D)/2 identity).
- (Lesson from A030233: always search before claiming novelty.)

OEIS content is under the OEIS End-User License; baselines are copied here for
drafting and are attributed to their original authors in the `%A`/`%E` lines.
