# External anchor — the shared rule schema vs other people's square-lattice numbers

2026-08-12, wave-4 scout off queue row ADV-3 (cost adversary's
missing-from-both list). Scored under `docs/skeptical-reader-standard.md`,
mapped to phase 1 per the round brief. Script:
`experiments/tristruct/r3_adv3_rook_schema.py` (+ `.log`); external table copy:
`experiments/tristruct/r3_adv3_a292357.txt`.

## The entry ticket, answered honestly

This instrument decides king-connectedness **nowhere**: it is not a route to
any band cell and it clears neither entry-ticket level *as a route*, because it
is not one. It is a **consistency check on the schema itself** — the first test
of the harness Part-3 shared propositions against numbers this project did not
produce, at sizes and heights the project's external king anchors never reach.
The three propositions every frontier engine shares (cross-cut stencil,
label-partition sufficiency + stranded-component death, one-component + both
touch flags = height exactly H) are lattice-generic. Instantiated with a rook
stencil — a **one-line diff** against L3's executable spec — they must
reproduce fixed square-lattice polyominoes by height. They do, on 117 external
comparisons including n = 33 at H = 2 and H = 3. What that buys and does not
buy is in the disclosure block; the king-specific stencil content stays
untested by construction, and this file says so everywhere it matters.

## Disclosure block (mapped to phase 1)

    claim:              the shared rule schema (props 2+3 verbatim + the generic
                        shape of prop 1), rook-instantiated, reproduces published
                        square-lattice per-height polyomino counts exactly
    share of a(40) reached:            0%  (no king cell is touched; this tests
                                       the schema, not the king numbers)
    bits against enumeration error:    0   (for a(40); the instrument's bits are
                                       against SCHEMA error: 117 exact external
                                       comparisons, integers up to 3.0e12)
    bits against formula-chain error:  0   conditional on: nothing — no formula
                                       chain is exercised
    rule independence:                 N/A with reason: the rule itself is the
                                       object under test; the reference values
                                       come from other authors' methods
                                       (inclusion-exclusion over box-spanning
                                       arrays; automaton/GF; direct enumeration)
    derivation independence:           full — no banked king data read or used;
                                       the rook run consumes ONLY external OEIS
                                       data and its own arithmetic
    input footprint:                   0 banked cells
    checker:                           experiments/tristruct/r3_adv3_rook_schema.py,
                                       14.5 s at NMAX=9 on gympie, fail-closed;
                                       RED = --red corrupts a compared external
                                       table cell, run aborts nonzero
    sensitivity:                       corruption battery: (i) --red table
                                       corruption -> ABORT (exit 1); (ii) the
                                       king stencil against square data is the
                                       standing cross-lattice RED — the king
                                       stencil disagrees with these tables from
                                       the first non-trivial cell (king T(3,2)
                                       = 10 banked vs square T_sq(3,2) = 4);
                                       (iii) incident, kept: the FIRST --red
                                       corrupted an entry with n > NMAX and
                                       PASSED — the guard was blind to
                                       out-of-window corruption; fixed to
                                       corrupt a compared cell. False-pass rate
                                       of the shipped battery: 0/2 after fix
    prior-work grep:                   git log --all --oneline --name-only --
                                       'results/*.md' 'docs/*.md' 'docs/**/*.md'
                                       piped through grep -iE 'rook|square-
                                       lattice|external-anchor|jensen|A292357|
                                       A308359|polyomino.*height'; plus working-
                                       tree grep for the OEIS ids. Hits: A308359
                                       used for the diagonal-law corollary
                                       (docs/proofs/universal-diagonal-law.md,
                                       experiments/oeis_a308359_check.py — a
                                       project-authored brute-force enumerator,
                                       NOT the schema DP and NOT an external
                                       comparison); A292357 cited by L1 as
                                       carrying no cell counts (corrected
                                       below); no prior schema-vs-external test
                                       anywhere, any branch

## 1. Citable external data — what actually exists

Checked today by direct OEIS fetch (read-only lookups, standing-allowed) and
against `papers/`. Nothing here is paraphrased from an abstract; the one paper
pulled fresh is now in `papers/`.

| source | what it holds | extent | provenance |
|---|---|---|---|
| **A292357 a-file** (`a292357.txt`, local copy `r3_adv3_a292357.txt`) | fixed polyominoes by (width, height, **cells**) | every box with W+H ≤ 24 → complete per-height sums T_sq(n,H) for **all n ≤ 23, every H** | Andrew Howroyd, 2017; his stated route is inclusion–exclusion over A287151 (connected binary arrays spanning a box) |
| A292357 main + b-file | per-box totals (no cell grading) | 435 antidiagonal terms | same; independently reproduced for b ≤ 6 by Marin 2024 (below) |
| A308359 + b-file | triangle: fixed n-ominoes by bounding-box width (= by height, transpose bijection) | n ≤ ~14 | R. J. Mathar, 2019, direct enumeration |
| A027053 (= column w=2 of A308359) | T_sq(n, H=2) | n ≤ 33 | OEIS |
| A335606 (column w=3) | T_sq(n, H=3) | n ≤ 33; **order-14 linear recurrence** (Zeilberger link in entry) → extensible to any n, n = 40 included | R. J. Mathar / D. Zeilberger |
| A001168 + b-file | fixed polyominoes, totals (row-sum control) | **n ≤ 70** | Jensen 2001/2003 lineage → `papers/counting_polyominoes_revisited.pdf`; b-file fetched today |
| `papers/marin_2024_counting_polyominoes_rectangle.pdf` (arXiv:2406.16413, pulled today) | inscribed-in-b×h counts, automaton + rational GF method, G_b explicit for b = 2..6 | per-box totals; second method for the A292357 marginals | Louis Marin, UQAM LACIM, 2024 |
| `papers/jensen_lattice_animals.pdf`, `papers/jensen_counting_polyominoes_parallel.pdf` | the FLM lineage; internally counts width-exact rectangle-spanning animals | **published tables are totals only — no per-height series** (checked by text search today: the width/height mentions are methodological) | Jensen 2001, 2003 |

Nothing needed `papers/MISSING.md`: every wanted source was free.

Two corrections to project statements found on the way:

- **L1's data claim is wrong in one clause**: `triangle-r3-l1-corner-gluing.md`
  lines 122–128 says A292357 is "by width×height without a cell count". The
  a-file **has the cell count** — (width, height, cells, count) for W+H ≤ 24.
  L1's conclusion stands (the range still falls far short of pieces-to-39-cells
  at heights to 21), but the clause is factually wrong and the a-file is the
  best per-height square data in existence.
- The external king series (A006770) holds **18 terms** — Redelmeier 1991
  emails, plus Tremblay & Vernay 2024 (doi:10.1051/ita/2024013) as a modern
  external generation paper. Relevant to successor ADV3-S2 below.

## 2. Transfer analysis — is it genuinely a stencil swap?

Diff of `r3_adv3_rook_schema.py` against `r3_l3_schema_dp.py`, proposition by
proposition:

- **Prop 1 (stencil): changes, by exactly one line.** In-column adjacency
  (vertical runs) is identical on both lattices. The cross-cut set changes
  `(r-1, r, r+1)` → `(r,)` — the marked line in the script. Nothing else.
- **Prop 2 (partition sufficiency + stranded death): byte-identical code.**
  One honest caveat on its *truth* rather than its text: the proposition is
  valid only for stencils whose cross-cut reach is one column — true for rook
  and king both — so the transfer is clean here, but a lattice with 2-column
  reach (e.g. knight adjacency) would need a widened boundary, i.e. prop 2 is
  generic over one-column-reach stencils, not over all lattices.
- **Prop 3 (completion): byte-identical code.** Same sticky-flag
  height-exactness, same one-component predicate. No different completion rule
  is smuggled in: the implicit assumption both instantiations share — a
  connected animal has no empty column inside its bounding box — holds on both
  lattices for the same reason (both adjacencies step columns by ≤ 1).

So the answer to the task's question 2 is: **the transfer is clean, and the
schema is genuinely generic over one-column-reach stencils.** Agreement with
the square tables therefore corroborates props 2 and 3 verbatim and the
one-column-reach *shape* of prop 1. It does **not** touch the king-specific
stencil content — the `{r-1, r+1}` diagonal entries across the cut. That class
of error is exactly the one the independence adversary measured the structural
self-checks to be blind to (dropped-NW passes both identities; see the ADV-1
gate-fact row), and it stays untested by any square-lattice comparison, by
construction. Anyone citing this result cites that sentence with it.

## 3. Measured result (gympie, foreground, seconds-scale per dispatch rules)

`r3_adv3_rook_schema.py 9`, 14.5 s total, fail-closed:

- **Full triangle vs Howroyd's box table**: all cells 1 ≤ H ≤ n ≤ 9 match.
- **H = 2 to n = 33 vs A027053**: all 32 terms match (largest 516,743,376).
- **H = 3 to n = 33 vs A335606**: all 31 terms match (largest 3,014,693,395,137).
- **Row sums vs A001168**: n ≤ 9 match.
- 117 exact comparisons, zero mismatches; RED battery per disclosure block.
- Peak states H=9: 1,928 (king spec at same cell: 3,360 — rook is smaller, as
  the Motzkin-type censuses predict).

The H = 2, 3 deep runs matter more than their share suggests: they exercise
stranding and completion over 30+ column transitions — sweep depths no king
external anchor reaches (external king data stops at n = 18; the project's own
Redelmeier confirmations at n ≤ 22 are project-run).

## 4. Reach estimate

Measured anchors: total wall 2.6 s (NMAX=8) → 14.3 s (NMAX=9), ×5.5 per unit
n; per-H at NMAX=9: 0.67 / 2.69 / 10.68 s for H = 7/8/9 (×~4 per H).

- **n ≤ 12, all H**: ×5.5³ → ~40 min. EXTRAPOLATED. Single core.
- **n ≤ 14, all H**: ×5.5⁵ → ~20 h single-core. EXTRAPOLATED. This is the
  largest run the unmodified Python spec should be asked for.
- **n ≤ 23, all H (the full extent of Howroyd's table)**: dominant cell is
  H ≈ 12: ~1.1e5 full states × 4,095 masks × ~50 ops × ~12 columns ≈ 3e11 ops
  → **out of reach for the Python spec** (~months); a C++ port runs it in
  single-digit core-days, per-H parallel, wall ~1–2 days on ayr. EXTRAPOLATED
  from the ops model, no C++ anchor. A port trades away some of the
  40-line-spec character; mitigation is validating the port against the spec
  over the n ≤ 14 overlap.
- **H = 3 at n = 40**: the schema side is trivial (seconds — 7 masks, ~15
  states, 38 columns). The external side needs A335606 extended n = 34..40 by
  its published order-14 recurrence — the one place an external per-height
  square value at **n = 40 itself** is obtainable. Recurrence coefficients not
  yet pulled (see NOT ESTABLISHED).

## 5. JOB REQUEST — filed per docs/r3-job-dispatch.md

    job id:            ADV3-JOB-1
    measures:          rook-schema T_sq(n,H) for all 1 <= H <= n <= 14 vs
                       Howroyd's per-cell box table + A001168 row sums
                       (~100 further external cells beyond today's n <= 9,
                       including every height the spec can reach at 14)
    decides:           whether the shared schema carries external corroboration
                       at real multi-column depths, or fails it. A single
                       mismatch => the three propositions are wrong AS STATED
                       and every engine inherits that — round-changing, and it
                       re-opens the harness Part-3 statement. Agreement =>
                       the corroboration L3-5's proof proposal and the
                       synthesis's 2b3115b wording can cite.
    command:           python3 experiments/tristruct/r3_adv3_rook_schema.py 14
    script:            experiments/tristruct/r3_adv3_rook_schema.py (written,
                       validated at NMAX=9 GREEN, RED battery in place)
    wall estimate:     ~20 h single-core — EXTRAPOLATED (measured 2.6 s ->
                       14.3 s for NMAX 8 -> 9, factor 5.5/n, compounded x5)
    RAM estimate:      < 2 GB peak — ASSERTED (measured 1,928 states at
                       (9,9); state dict growth ~x2.5/H; vecs are short)
    disk estimate:     log file only, < 1 MB
    cores:             1 (per-H parallelism exists but the script is serial;
                       not worth a rewrite at this wall)
    interruptible:     no checkpoint; on kill, restart loses everything below
                       the last completed H line in the log
    RED control:       --red corrupts a COMPARED external cell -> abort
                       (verified exit 1); fail-closed on any mismatch;
                       row-sum control vs A001168 built in
    closes:            ADV-3's open question above n = 9; corrects its
                       "laptop-minutes" cost guess (minutes was true only to
                       n <= 9)

Not requested: the n ≤ 23 C++ tier (priced above; the lead can ask for it if
Tier A's ~100 cells are judged not enough) and the H=3-at-n=40 recurrence
extension (desk work first — pull the coefficients).

## 6. What this buys, ranked honestly

It cannot verify a(40) and it is not a route: 0% share, 0 enumeration bits, and
it must be ranked below every band-reaching candidate. What it is: the only
test in three rounds that puts the shared propositions in front of arithmetic
this project did not produce, above the n ≈ 22 external wall on the king side
(to n = 33 on the square side, n = 23 prospectively at all heights). It is the
empirical complement of L3-5: the Lean program proves the schema against an
independent *definition*; this checks it against independent *data*. If both
land, the residual objection contracts to exactly the harness's last clause —
single-binary implementation faults on cells only the kink kernel swept —
which is L6-1's territory, per L3-6's package framing.

## 7. Successor rows (filed in results/triangle-r3-queue.md)

- **ADV3-S1** — polyhex instantiation: the hex cross-cut stencil is
  *asymmetric* ({r−1, r} type), which is precisely the error class both the
  structural self-checks (ADV-1 gate fact) and any symmetric-census check are
  blind to, and which the rook swap cannot probe. External per-height polyhex
  data existence NOT ESTABLISHED — the row starts there.
- **ADV3-S2** — king-stencil analogue against the external king prefix: the
  king schema spec's row sums vs A006770's 18 external terms (Redelmeier 1991;
  Tremblay & Vernay 2024). Tests the stencil content this file cannot; Python
  spec reaches n ≈ 13 (×5.5/n from the measured 41 s at n = 9), so it overlaps
  the external prefix by one term past the four-enumerator n ≤ 12 lock — thin,
  priced honestly in the row.
- **ADV3-S3** — cross-lane data correction to L1 (the a-file's cell counts),
  plus its one live use: exact external ingredient values for the top-strata
  anchor rows L1-5/L1-9 at small boxes.

## NOT ESTABLISHED

- Anything about the king-specific stencil content — restated once more
  because it is the caveat: no square-lattice agreement, at any n, tests
  `{r-1, r+1}` across the cut. What would establish it: ADV3-S2 (weakly,
  small n), the L3-5 proof (fully, at the definition level), or an
  asymmetric-stencil lattice with external data (ADV3-S1).
- Howroyd's a-file method independence in the strong sense: his U/V
  inclusion–exclusion runs over A287151 (connected spanning arrays), whose own
  computation route I did not audit; Marin 2024 independently reproduces only
  the per-box *marginals* (b ≤ 6), not the cell-graded values. The cell-graded
  table above n ≈ 14 (Mathar's triangle ends there) rests on Howroyd alone.
  What would establish it: any second cell-graded source, including our own
  tier-B run being confirmed against a third-party rectangle enumerator.
- The order-14 recurrence coefficients for A335606 (needed for the H=3,
  n=40 external value): not pulled; the Zeilberger link in the OEIS entry is
  the place to get them, with the OEIS b-file terms as the seed check.
- Whether the ×5.5/n wall factor holds past n = 14 (it should worsen as H
  grows past 9; the tier-A estimate carries 3x dispatch headroom per the
  protocol's ASSERTED rule if the lead prefers to treat it so).
