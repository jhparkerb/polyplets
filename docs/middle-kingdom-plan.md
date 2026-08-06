# Middle Kingdom — the poly-time belt of king-animal subclasses

**Status:** planned 2026-08-05. Authored in-session with jasonp; execute
post-`/clear` from this file alone. Phases 0, 1 (1a/1b/1c), 2 and 3 all DONE
2026-08-05, uncommitted -- see `results/middle-kingdom-grid.md`,
`results/convex-polyplets.md`, `results/multi-directed.md`,
`results/middle-kingdom-phase3.md`. `make gate-king-grid gate-multidirected
gate-convex-dfinite gate-middle-kingdom` GREEN; full `make` GREEN. **Phase 4
is what remains.** Nothing below has been run except where marked MEASURED.

Phase 3's outcome in one line: of the twelve open cells (the nine below plus
the three the multi-directed row adds), **eight collapse onto the unfiltered
row with proofs, three are new sequences, and one is A018902**. Convexity
subsumes directedness -- HV-convexity forces 5-cone directedness, staircase
forces both cones, column-convexity forces multi-directedness. Phase 3 also
found the multi-directed row itself is **not** novel: it is **A222205**.

**Objective.** King-animal subclasses fall into three cost tiers: closed-form
(microseconds at any n), poly-time-no-closed-form, and exponential. The middle
tier contains exactly the sequences with **no OEIS entry** (Phase 3 falsified
the "exactly": multi-directed is not D-finite and is nevertheless A222205,
entered by Sloane from Bacher's paper in 2013). Map it completely:
extend every sequence in it far past current reach, sharpen the D-finiteness
verdicts that currently rest on 38 terms, pin the growth constants, and fill the
empty cells of the classification grid.

Off the a(n) record path. Pure enumeration/GF work. The project still closes at
a(40); this does not reopen it.

## Model targeting

| phase | model | why |
|---|---|---|
| 0, 1a, 1b, 4 | **Sonnet** | mechanical: predicate plumbing, a loop rewrite, a b-file. Acceptance criteria below are exact. |
| 1c, 2, 3 | **Opus** | definition-pinning from a paper, D-finiteness/algebraicity judgement, novelty calls |

A Sonnet run that hits *any* mismatch against the reference values in this file
stops and reports — it does not adjust the reference.

## Hard rules (from MEMORY.md; violating any of these fails the phase)

- **C++ for compute, Python as thin glue.** The Python TMs here are legacy;
  anything that needs to run longer than a minute gets ported.
- **Named on-disk scripts only** — no `/tmp`, no heredocs, no long-lived
  `python -c`. Binaries build into `build/`. `docs/job-checklist.md` before any
  compute job.
- **RED-first**: every new counting routine gets a test that fails before it
  works, and a control that *must* diverge (see Phase 0).
- **`make` once** in any session that touches code, not just the nearest gate.
- **No dalby/ayr job without asking jasonp first**, and no job over 1 hour
  without explicit agreement. Phases 0–2 are laptop-scale by design.
- **Nothing goes to OEIS or any external service.** Prep only; jasonp submits,
  and submission is gated on the viva.
- **`paper/technical-report.tex` is read-only.**
- Check `lsof` for jasonp's `.swp` files before editing anything in `paper/`.

## Definitions (all classes: cells of Z², 8-connected, counted up to translation)

**Directedness axis** — from a canonical source, every cell reachable by cone
steps *staying inside the animal*:

- **none** — king-connected only.
- **directed** (Bacher, 5-step) — cone `{W, NW, N, NE, E}` = `(-1,0) (-1,1)
  (0,1) (1,1) (1,0)`; source = leftmost-bottommost cell. Bottom row is forced
  contiguous (consequence, not an added rule).
- **half-plane directed** (4-step) — cone `{N, NE, E, SE}`; source = bottommost
  cell of the leftmost column. Contains a downward step, so **not nested** with
  the 5-step class in either direction.
- **multi-directed** — pinned 2026-08-05, Bacher's Definition 2
  (`results/multi-directed.md`): sources are *local minima* of the
  column-bottom profile (any height, not just the global bottom row),
  keystones are local maxima, every cell cone-reachable from some source, and
  every keystone reachable from a source strictly left and one strictly right.
  **Not** the split-bottom-row predicate — that's control B (`ctrlB`),
  incomparable with multi-directed (witnessed both directions,
  `results/multi-directed.md`).

**Convexity axis:**

- **none**.
- **column-convex** — every column a single contiguous run; rows unconstrained.
  (Row-convex is the transpose, same counts.)
- **HV-convex** ("convex") — every row *and* column a single contiguous run;
  equivalently left border v-shaped, right border ∧-shaped.
- **staircase** — column intervals with bottoms *and* tops nondecreasing left to
  right. Strictly inside HV-convex.

Excluded deliberately: the **grounded** axis (bargraph 2^(n-1), stack A001523,
Ferrers A000041). All trivial; crossing it adds only empty boxes.

## The grid

Filled in by Phase 3 (`results/middle-kingdom-phase3.md`); the `ctrlB` row is
the fifth directedness value Phase 0 carried as its own column and Phase 1c
made permanent. **Bold** = new in Phase 3.

|  | none | column-convex | HV-convex | staircase |
|---|---|---|---|---|
| **none** | A006770 | A187077 | **NOVEL** (MEASURED to n=700) | A225114 |
| **directed** (5-cone) | A047781 | **NOVEL** | = (none, HV-convex) | = A225114 |
| **half-plane** (4-cone) | A055834 | **A018902** | **NOVEL** | = A225114 |
| **control B** (bottom row waived) | control-B seq. (novel) | **NOVEL** | = (none, HV-convex) | = A225114 |
| **multi-directed** | **A222205** (200 terms, `results/multidirected_terms_n200.txt`) | = A187077 | = (none, HV-convex) | = A225114 |

No empty cells. Five novel sequences in the grid: HV-convex by area, control B
unfiltered, and the three Phase 3 found ((5-cone, column-convex),
(control B, column-convex), (half-plane, HV-convex)). HV-convex by
semiperimeter is novel too but counts by a different statistic.

The old table filled `directed x column-convex = A007052` and called the
multi-directed row novel. Both were wrong: A007052 is column-convex with
bottoms nondecreasing and NO cone filter (Phase 0, Finding 1), and the
multi-directed row is A222205 (Phase 3's novelty check).

## Reference values — every check in this plan compares against these

Do not "fix" a mismatch by editing this table.

| sequence | first terms | growth |
|---|---|---|
| all king animals A006770 | 1, 4, 20, 110, 638, 3832, 23592, 147941, 940982, 6053180 | 7.110 (est) |
| directed A047781 | 1, 4, 19, 96, 501, 2668, 14407, 78592, 432073, 2390004 | 3+2√2 = 5.82843 |
| half-plane directed A055834 | 1, 4, 18, 85, 413, 2044 | 27/5 = 5.4 |
| column-convex A187077 | 1, 4, 18, 83, 385 | 4.64468 (quartic root) |
| directed column-convex A007052 | 1, 3, 10, 34, 116, 396 | 2+√2 = 3.41421 |
| staircase A225114 | 1, 3, 9, 28, 87, 272 | — |
| **HV-convex by area (novel)** | 1, 4, 16, 61, 221, 766, 2566, 8390, 26982, 85834 | 3.1289432697308862523 (Phase 2b, 199 digits) |
| **HV-convex by semiperimeter (novel)** | 1, 2, 9, 36, 154, 668, 2916, 12740 | ~4.13 falling |
| multi-directed = A222205 | 1, 4, 20, 110, 636, 3790, 23036, 141946 | 6.475196280297 (12 digits, 400-term series, `results/multi-directed.md`) |
| cone-anchor control B (bottom row waived) | 1, 4, 20, 106, 576, 3179, 17736, 99748 | — |
| convex polyomino by area (CONTROL) = A067675 | 1, 2, 6, 19, 59, 176, 502, 1374, 3630, 9312 | 2.3091385933304947311 (Phase 2b, 121 digits) |
| convex polyomino by semiperimeter A005436 (CONTROL) | 1, 2, 7, 28, 120, 528, 2344 | — |

Spot value, MEASURED 2026-08-05 on gympie, `python3 experiments/convex_tm.py 128`
(~4 min, exit 0), term n=128 of HV-convex by area:

```
2509948162052912103766963600364762350348141297853178810057013197
```

## Existing assets

| file | what it does | reach MEASURED |
|---|---|---|
| `cpp/directed_cone_anchor.cpp` → `build/directed_cone_anchor` | Redelmeier untried-set DFS over all fixed king animals with a pluggable directedness predicate; modes `dir5`, `cone5`, `dir4`, `dir5nb`; already has the three RED controls | filter n=15 (458 s, 8 threads); cone growth n=17 (195 s) |
| `experiments/directed_cone_anchor.py` | driver + closed-form reference (three independent evaluations) | n≤25 closed form |
| `experiments/convex_tm.py` | HV-convex by area, row TM, state `(width, left-phase, right-phase)` | n=38 in 0.33 s; **n=100 in 32 s; n=128 in ~4 min** |
| `experiments/convex_perimeter.py` | HV-convex by semiperimeter + P-recurrence guesser + polyomino control | s=36 |
| `experiments/colconvex_king.py` | column-convex Temperley derivation | — |
| `experiments/anisotropic_dfinite.py` | mod-`2^61-1` polynomial arithmetic used for D-finiteness work | — |

Primary prior notes, read before starting: `docs/proofs/convex-mirage.md`,
`results/convex-polyplets.md`, `results/king-subfamilies.md`,
`results/directed-king-animals.md`, `results/directed-cone-anchor.md`.

---

## Phase 0 — one enumeration, sixteen ground truths (Sonnet)

Extend `cpp/directed_cone_anchor.cpp` so a **single** Redelmeier pass evaluates
every grid cell on every animal generated, emitting a 16-column table by n. The
enumeration is the expensive part and it is already written; the predicates are
O(cells) each.

Per animal, compute: the four directedness verdicts (none / 5-cone / 4-cone /
multi-directed-candidate) × the four convexity verdicts (none / column-convex /
HV-convex / staircase), and increment the 16 counters.

Convexity predicates are trivial (per-column and per-row run counts; staircase
adds monotone bottoms and tops). The multi-directed column used control B's
predicate as a stand-in, labeled `ctrlB`. **Resolved by Phase 1c: `ctrlB` was
never a stand-in for multi-directed — the two are incomparable
(`results/multi-directed.md`). `ctrlB` stays as its own permanent column;
multi-directed (Bacher's Definition 2, predicate `mdir`) is a fifth
directedness value this grid has no row for. Phase 3 on the multi-directed
row needs `mdir` tallied separately, not read off `ctrlB`.**

**Acceptance:**
- Reproduces every row-1 and column-1 entry of the reference table above.
- Reproduces A006770 to n=12 as the unfiltered control.
- The three existing RED controls still diverge exactly where recorded (4-cone
  18 vs 19 at n=3; bottom-row-waived 20 vs 19 at n=3).
- New RED control: a deliberately wrong staircase predicate (tops monotonicity
  dropped) must **fail** to reproduce A225114.
- Runs to n≥12 in under 10 minutes on 8 threads.

**Deliverable:** the 16-cell table to n=12–14, written to `results/`. This is the
acceptance test for every transfer matrix in Phases 1 and 3 — no TM is trusted
until it matches this table on its overlap.

## Phase 1a — HV-convex by area to n=500 (Sonnet)

Current cost is ~N⁵: O(N⁴) DP work × bigint width (digits ≈ 0.5n). MEASURED:
0.33 s at 38, 32 s at 100, ~4 min at 128, >2 min timeout at 200.

Two independent speedups, in this order:

1. **Prefix sums.** The inner `dl` loop in `experiments/convex_tm.py` sums over a
   contiguous range of offsets — a convolution with a box. Replace with running
   prefix sums over the width dimension: N⁵ → N⁴. Verify first in Python against
   all 128 known terms, then time it.
2. **C++/GMP port** if (1) doesn't reach n=500 in ten minutes. `cpp/`, `build/`
   target, baked commit stamp, `start`/`heartbeat`/`done` events per
   `docs/observability.md`.

**Acceptance:** all 128 MEASURED terms reproduced exactly, including the n=128
spot value above; the ratio sequence still converges to 3.12894; runtime and peak
RSS recorded for n=100/200/500.

## Phase 1b — HV-convex by semiperimeter to s=200 (Sonnet)

Same treatment on `experiments/convex_perimeter.py`. Keep the convex-polyomino
control (A005436) wired in — it calibrates the guesser and an unpowered guesser
is the failure mode that matters here.

**Acceptance:** reproduces 1, 2, 9, 36, 154, 668, 2916, 12740 and the A005436
control; the banked order-5 degree-2 P-recurrence, fitted on s≤22, still predicts
correctly at s=200 (a far stronger holdout than the original s≤36). If it
**fails** out there, that is a significant finding — stop and report, do not
re-fit quietly.

## Phase 1c — multi-directed: pin, then implement (Opus)

The repo contradicts itself. `results/directed-king-animals.md` calls a split
bottom row "multi-directed"; `results/directed-cone-anchor.md` calls the same
predicate (control B) "a genuine third sequence, matching neither A047781 nor
A006770". Both cannot be right, and no implementation exists.

1. Pin Bacher's definition from arXiv:1301.1365 — Lemma 11 (the intermediate
   series B, root of `ρ³ − 7ρ² − 5ρ + 1 = 0`, `1/ρ_B ≈ 6.118`, **not** the growth
   constant) and Theorem 10 / Corollary 12 (`B(ρ_M) = 1`, `μ = 1/ρ_M ≈ 6.4752`).
   If the paper isn't to hand, `papers/MISSING.md` practice applies.
2. Decide whether control B is Bacher's class, a superset, or incomparable —
   Phase 0's brute-force table settles it at small n against terms derived from
   Bacher's own GF.
3. Implement the B-series scheme for terms. Target n≥100.
4. Correct whichever of the two notes is wrong.

**Acceptance:** terms agree with an independent brute-force filter (Phase 0
machinery, correct predicate) for all n where both are available; the series
ratio converges toward 6.4752 and **not** toward 6.118 — conflating those two
constants is the specific trap this phase exists to avoid.

## Phase 2 — the analysis that changes claims (Opus)

**2a/2b: DONE 2026-08-05** — `results/convex-polyplets.md`, section "Non-D-finite
at order<=24, degree<=24; mu to 199 digits". Both series (king and the A067675
control) extended to n=700 and excluded at order ≤ 24, degree ≤ 24 *and* for
algebraic relations of the same size; μ pinned to 199 / 121 trusted digits;
θ = 0 measured, correction geometric not power-law; μ not algebraic in the
searched boxes. Tools: `cpp/prec_guess.cpp`, `experiments/convex_growth.py`,
`build/convex_area_tm N 0` (new king=0 mode). Gate: `make gate-convex-dfinite`.

**2a. Sharpen the non-D-finite verdict.** Banked result rules out order ≤ 6,
degree ≤ 5 on 38 terms. With ~500 terms, exclude order ≤ 20, degree ≤ 20 — a
qualitatively stronger statement. Fit mod `2^61-1` (machinery in
`experiments/anisotropic_dfinite.py`) so the Ansätze stay cheap. Retain the
convex-polyomino area control throughout: **a guesser whose known control also
fails is the only reason the negative means anything.** Test algebraicity
separately from D-finiteness.

**2b. Nail the constants.** Differential approximants on the extended series:
μ_convex to 8+ significant figures (today: 3.12894), plus the subexponential
exponent θ. Then test whether μ is algebraic (integer relation on its powers).
A closed form for μ is the best available outcome in this whole row.

**2c. Independently estimate the multi-directed growth constant.** Bacher's
6.4752 is numerical-only in the literature — no minimal polynomial. Our series
estimate would independently confirm a published number that currently sits just
under the certified λ bracket (`6.543 ≤ λ ≤ 9.3153`). Note the tension worth
checking: 6.4752 < 6.543, consistent with multi-directed ⊂ all, as required.

**2c: DONE, subsumed by Phase 1c (2026-08-05).** Phase 1c's 400-term GF series
already delivers exactly this: μ = 6.475196280297 (12 digits, Aitken-stable),
independently confirming Bacher's numerical 6.4752 and extending it well past
publication precision — no separate estimate needed. Consistency with the
bracket checked and holds: 6.475196280297 < 6.543. Still no minimal polynomial
(ρ_M is defined transcendentally through the non-D-finite intermediate series
B, per Bacher Theorem 10) — that remains open, not a gap in this phase.
Full detail: `results/multi-directed.md`.

## Phase 3 — fill the nine empty cells (Opus)

**DONE 2026-08-05, uncommitted: `results/middle-kingdom-phase3.md`.** Twelve
cells settled (the nine here plus the multi-directed row's three), eight by
proof rather than by transfer matrix. New tool `cpp/middle_kingdom_tm.cpp`
(`make gate-middle-kingdom`); `grid` mode extended from 16 to 20 cells. The
kill criterion did NOT fire (two of the first three cells landed on existing
OEIS entries, not three). Growth constants: `2+sqrt(2)` with a double pole for
(dir5, column-convex), `(5+sqrt(13))/2` for (dir4, column-convex) = A018902,
3.8115279451099252 for (ctrlB, column-convex) (not D-finite in the boxes
tested), and the unrestricted HV-convex constant to all 51 digits measured for
(dir4, HV-convex) (also not D-finite).

Each cell: a transfer matrix (validated against Phase 0's table on the overlap),
terms, growth constant, GF class, novelty check against OEIS and literature.

**Expected outcome is mostly negative.** The banked meta-finding
(`results/king-subfamilies.md`) is that every classical restriction collapses
king animals into composition/partition-land, because corner contact makes
connectivity too easy to be interesting. **Kill criterion: if the first three
cells attempted all land on existing OEIS entries, stop.** "The grid has exactly
three interesting cells, and here is why" is a better result than nine more
transfer matrices, and it's cheaper.

Order cells by expected interest: `multi-directed × column-convex` first (the
only novel row crossed with the only nontrivial solved column), then
`directed × HV-convex`, then `half-plane × column-convex`.

## Phase 4 — prep, not publish (Sonnet for mechanics, Opus for the write-up)

**DONE 2026-08-05, uncommitted: `results/middle-kingdom.md`** is the campaign's
index. Seven b-files staged (`results/b222205_upload.txt`,
`b_hvconvex_area_upload.txt`, `b_hvconvex_perimeter_upload.txt`,
`b_ccdir5_upload.txt`, `b_ccctrlb_upload.txt`, `b_hvdir4_upload.txt`,
`b_ctrlb_unfiltered_upload.txt`); five OEIS comments drafted (A055834, A007052,
A225114 in `results/king-subfamilies.md`; A018902 in
`results/middle-kingdom-phase3.md`; the A187077 correction plus its missing
derivation in `results/convex-polyplets.md`). Nothing submitted.

- b-files in OEIS format for each novel sequence, into `results/b*_upload.txt`
  following the existing convention.
- Draft OEIS comments for the four staged new interpretations: A055834
  (four-step cone), A007052 (directed column-convex, with the Temperley
  derivation), A225114 (staircase = skew shapes, with the bijection), and
  A018902 (4-cone directed column-convex, draft text in
  `results/middle-kingdom-phase3.md`). Draft text
  for A055834 and A007052 already exists in `results/king-subfamilies.md`.
- A222205 has 23 terms and no b-file; ours reaches 200
  (`results/multidirected_terms_n200.txt`).
- Consider the A187077 correction comment: our brute force shows the entry's
  "equivalent to row-convex polyhexes (A059716)" comment is wrong in its plain
  reading (1,4,18,83,385 vs 1,3,11,42,162), and the entry carries no derivation.
- Results note in `results/middle-kingdom.md`; update `results/king-subfamilies.md`
  and `results/convex-polyplets.md` in place rather than duplicating.

**Nothing is submitted.** Submission is jasonp's, gated on the viva.

## Explicitly out of scope

- Re-deriving the closed-form tier — microseconds at n=41, nothing to learn.
- λ bounds from these families — superseded by the certified strip ladder at
  6.543; directed's 3+2√2 and convex's 3.129 are both below it.
- The frontier engine, the a(n) record, and `paper/technical-report.tex`.

## Compute

Phases 0–2 are laptop-scale as specified. If Phase 1a's target moves past n≈2000,
that becomes a real job: measure first, predict cost per `docs/job-checklist.md`,
then ask jasonp. Dalby's use here is three concurrent long extensions, not core
count — the DPs are serial in their layer dimension and 32 cores do not help a
serial recurrence.
