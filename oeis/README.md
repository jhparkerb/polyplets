# OEIS submission drafts

Staged drafts in OEIS **internal format** (`%I %S %T %U %N %C %D %H %F %e %Y %K %O %A %E`).
**Nothing here is submitted.** Live submission to oeis.org requires explicit signed
orders + the 24-h cooling-off (ROADMAP #25). These files are a reviewable staging area.

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
Author/extender bylines use the placeholder `_[submitter]_` — replace with the
real OEIS contributor name before any submission.

## Status
| file | status |
|---|---|
| A006770 (fixed) | extend: +a(19) confirmed; a(20) pending h19 assembly |
| A030222 (free) | extend: +a(18),a(19) |
| A030233 (one-sided) | extend: +a(18),a(19) |
| A030234/A030235 (symmetric) | pending: verify our bilateral-symmetry counts first |
| draft hole triangle T(n,k) | new (4-bg convention), exact through n=16 |
| draft A_0 (hole-free), A_1 (one-hole) | new, exact through n=16 |
| draft A_max (max hole area) | new; few terms, extendable |

## Novelty re-checks (OEIS search, 2026)
- Triangle T(n,k), A_0 (hole-free), A_1 (one-hole): **no OEIS match** on their term
  prefixes — genuinely new.
- A_max: definition is new, but the 9-term data 0,0,0,1,1,2,3,5,6 matches 16
  unrelated short sequences (partition counts, etc.). Extend the brute force
  (n >= 10) to disambiguate before submitting.
- (Lesson from A030233: always search before claiming novelty.)

OEIS content is under the OEIS End-User License; baselines are copied here for
drafting and are attributed to their original authors in the `%A`/`%E` lines.
