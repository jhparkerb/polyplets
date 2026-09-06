# OEIS submission drafts

**Scope, order, and readiness are decided in [`SUBMISSION.md`](SUBMISSION.md)**
(the authoritative index + case file, 2026-07-16); this README keeps per-file
detail and the pre-submission checklist.

Staged drafts in OEIS **internal format** (`%I %S %T %U %N %C %D %H %F %e %Y %K %O %A %E`).
**Nothing here is submitted.** These are reviewable, staged drafts; jasonp pushes the
actual submission to oeis.org — Claude prepares and stages, never submits to an external
service. Normal care for outward-facing steps; no signoff ceremony.

## Submission-status flags
- `draft-gf-orders.txt`, `draft-atom-degrees.txt` — **NOT READY**: the report
  asserts these are not in OEIS; submitting contradicts it. Discuss with OEIS
  editors first (jasonp).
- Superseded drafts (maxholearea, standalone A_0/A_1) were removed 2026-07-06;
  the canonical versions live in `oeis/wave2/`. Git history has them.

## Files
- `A######.txt` — an **existing** OEIS entry we extend. Commit history per file:
  1. first commit = the entry **verbatim** from OEIS (`?fmt=text`), unmodified;
  2. later commits = **our** additions (terms, comments, GF notes, cross-refs),
     one commit per change, with the **data provenance in the commit message**.
  So `git log -p A######.txt` shows exactly what we changed vs. OEIS.
- `draft-<name>.txt` — a **new** sequence we propose. Placeholder A-number
  (`Axxxxxx`) until OEIS assigns one.

## Pre-submission checklist (from jasonp's past OEIS review threads, 2019-2025)
Each of these caused editor pushback on a real past submission; check every
staged change against all four before jasonp submits:
1. **Extend cross-referenced sequences together.** If a new term of X implies
   a new term of a %Y-linked sequence (as A102976 implied A101841), stage both
   in the same batch — an editor WILL ask.
2. **Sign per the style sheet, with a real date.** `- _Jason H Parker_, Mon DD
   YYYY` — full month-day-year, and the date must be the day the change is
   actually proposed on oeis.org (Heinz: "date was not correct"). Before
   submitting on a different day than staged, update every new signature date.
3. **Respect each entry's own offset/indexing.** Related sequences can index
   differently (A101841 vs A102976); number claimed new terms against the
   target entry's %O and current last term — never "added a(14)" when that
   entry's latest is a(13).
4. **Additions only — never remove or rewrite existing content.** Existing
   comments, %E history, links stay verbatim (Heinz on A000522: "You removed
   the old comment ... this is not ok"). Our own staged-but-unsubmitted text
   may be edited freely; anything live on OEIS may not.

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

## Status (2026-07-16, post a(22) two-algorithm confirmation)
| file | status |
|---|---|
| A006770 (fixed) | **see `SUBMISSION.md`** — staged to a(40) and moving; this table went stale at a(35) and no longer tracks it |
| A030233 (one-sided) | staged: b-file to a(34) (promoted with A006770(34); Burnside arithmetic re-verified, R90(34)=0 structural); no conjectured comment left (reach cap) |
| A030222/A030234/A030235/A194596 | staged: b-files to n=32 (T2); n=33 as conjectured %C comments (T3, D(33) hybrid) |
| draft hole triangle T(n,k) | new (4-bg convention), exact through n=18, rows 15-18 cross-ISA confirmed |
| draft GF orders / atom degrees | Superseeker-novel; NOT READY (see flags) |
| draft free-polyplet symmetry classes (8: draft-sym-*.txt) | new, plain-search novel; D4 breakdown of A030222 to n=19, validated (classes sum to A030222/A030234) |

Submission is jasonp's, gated on the readiness process in docs/handoff.md.

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
  still to run before submission. Derivation (`scripts/symmetry_classes.py`) is validated:
  the 8 classes sum to A030222(n) and the five reflection classes to A030234(n) for all
  n <= 19 (the latter is the proven bilateral = (H+D)/2 identity).
- (Lesson from A030233: always search before claiming novelty.)

OEIS content is under the OEIS End-User License; baselines are copied here for
drafting and are attributed to their original authors in the `%A`/`%E` lines.

## Comment-grade edits to existing sequences (2026-07-14)

`draft-comments-subfamilies.txt` — three small edits: A187077 (correct the
polyhex-equivalence comment, add the Temperley derivation), A007052 (new
lattice-animal interpretation: directed column-convex polyplets), A225114
(identity: king staircases = skew shapes). Same authorship discipline as the
main batch: rewrite in own words before submitting; verification in
experiments/king_subfamilies.py + colconvex_king.py.
