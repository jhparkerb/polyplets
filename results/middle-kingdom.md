# Middle Kingdom — the poly-time tier of king-animal subclasses (2026-08-05)

Index for the campaign specified in `docs/middle-kingdom-plan.md`. Everything
here is summarised from four detailed notes; this file duplicates nothing and
links out for every claim.

**Objective.** King-animal subclasses fall into three cost tiers: closed-form,
poly-time-with-no-closed-form, and exponential. The middle tier was thought to
be exactly the subclasses with no OEIS entry. Map it: cross the directedness
axis with the convexity axis, fill every cell, extend every sequence in it,
and check each cell for novelty.

Off the a(n) record path — pure enumeration and GF work. The project still
closes at a(40).

## The grid

Rows are directedness, columns convexity; both axes are defined in
`docs/middle-kingdom-plan.md`. Cells are counts of fixed king animals by area,
up to translation.

| | none | column-convex | HV-convex | staircase |
|---|---|---|---|---|
| **none** | A006770 | A187077 | NOVEL (convex polyplets) | A225114 |
| **dir5** (5-cone, Bacher) | A047781 | **NOVEL** | = (none, HV) | = A225114 |
| **dir4** (4-cone, half-plane) | A055834 | **A018902** | **NOVEL** | = A225114 |
| **ctrlB** (bottom row waived) | control-B seq. (novel) | **NOVEL** | = (none, HV) | = A225114 |
| **multi-directed** | **A222205** | = A187077 | = (none, HV) | = A225114 |

No empty cells. Five novel sequences: HV-convex by area, control B unfiltered,
and the three Phase 3 settled — (dir5, column-convex), (ctrlB, column-convex),
(dir4, HV-convex). HV-convex by semiperimeter is a sixth, counted by a
different statistic (`results/mk-dir4-perimeter.md`,
`docs/middle-kingdom-followups-plan.md` Phase 2a).

## Headline results

**Convexity subsumes directedness.** Eight of the twelve cells that were open
collapse onto the unfiltered row, and all eight are now proved rather than
observed (`results/middle-kingdom-phase3.md`). The mechanism is one lemma: on a
column-convex animal, neither forward cone contains a southward step, so each
directedness predicate reduces to a condition on the column-bottom profile `b`
alone. Proposition 1: 5-cone directed iff `b` is valley-unimodal.
Proposition 2: 4-cone directed iff `b` never drops by more than one row.
Proposition 3: control B iff every local minimum of `b` is the global one.
Proposition 5: every column-convex king animal is multi-directed. With
HV-convex = column-convex + `b` valley-unimodal + `t` peak-unimodal, that gives
HV-convex ⊂ dir5, staircase ⊂ both cones, column-convex ⊂ multi-directed, and
the collapses fall out one line each. Brute-forced to n = 14 alongside the
proofs (`results/mk_grid20_n14.txt`, `make gate-king-grid`).

**The four cells that resist.** (dir5, column-convex) is rational with a double
pole, growth 2+√2 and an extra factor n. (dir4, column-convex) is A018902, an
existing entry that acquires its first lattice-animal interpretation and an
explanation of its own INVERT-of-A007052 formula. (ctrlB, column-convex) is the
only column-convex cell with no closed form — µ = 3.811527945110, not D-finite
in the boxes tested, and its subdominant singularity is the (dir5,
column-convex) cell's dominant one. (dir4, HV-convex) shares the unrestricted
HV-convex growth constant to all 49 significant digits measured, with a stable
amplitude ratio 0.46210904920994244004.

**The Convex Mirage, an order of magnitude stronger.** HV-convex king animals
by area and the convex-polyomino control are both excluded at order ≤ 24,
degree ≤ 24 on 700 terms, and separately shown non-algebraic; µ is pinned to
199 and 121 digits, θ = 0 is measured, and neither µ is algebraic in the
searched box (`results/convex-polyplets.md`).

**Two corrections to the record.**

- The multi-directed row is **not novel**: it is A222205 (Sloane 2013, from the
  same Bacher paper the definition was pinned from), and all 23 of the entry's
  terms match ours. What survives is the extension — 200 terms, no b-file
  existed, and µ = 6.475196280297 to twelve digits where the literature had a
  numerical 6.4752 (`results/multi-directed.md`). The plan's grid and this one
  are corrected.
- A187077's comment "Equivalent to a sequence of row-convex polyhexes
  (A059716)" is wrong in its plain reading, measured on both lattices with all
  fixed polyhexes reproducing A001207 as a control: 1, 4, 18, 83, 385 against
  1, 3, 11, 42, 162 (`results/convex-polyplets.md`, "A187077 provenance
  check"). The entry carries no derivation; ours is Temperley's method with the
  last column's height as catalytic variable.

Two definitional corrections came out of the campaign as well: "multi-directed"
in this repo had meant a split bottom row, which is control B's predicate and
is **incomparable** with Bacher's Definition 2, witnessed both ways
(`results/multi-directed.md`); and the "directed column-convex = A007052" label
was a naming collision — A007052 is column-convex with bottoms nondecreasing
and no cone filter at all (`results/middle-kingdom-grid.md`, Finding 1).

## Deliverables

Phase notes:

| file | phase | what is in it |
|---|---|---|
| `results/middle-kingdom-grid.md` | 0 | the 20-cell brute-force table to n = 14, one enumeration pass, Findings 1 and 2 |
| `results/convex-polyplets.md` | 1a, 1b, 2a, 2b | HV-convex by area to n = 700 and by semiperimeter to s = 200; the non-D-finite and non-algebraic exclusions; µ to 199 digits |
| `results/multi-directed.md` | 1c, 2c | Bacher's Definition 2 pinned, control B shown incomparable, 200 terms, µ to 12 digits |
| `results/middle-kingdom-phase3.md` | 3 | the twelve open cells: eight collapses with proofs, three new sequences, A018902 |
| `results/hv-growth-sandwich.md` | followups 1 | Proposition 6: staircase ⊆ C ⊆ HV-convex ⇒ growth constant µ; the phase-block factorisation of the HV-convex transfer operator; µ for A225114 |

b-files, staged in OEIS format, none submitted:

| file | sequence | terms |
|---|---|---|
| `results/b222205_upload.txt` | A222205, multi-directed animals | 200 (n = 1..200) |
| `results/b_hvconvex_area_upload.txt` | HV-convex polyplets by area (novel) | 700 (n = 1..700) |
| `results/b_hvconvex_perimeter_upload.txt` | HV-convex polyplets by semiperimeter (novel) | 199 (s = 2..200) |
| `results/b_ccdir5_upload.txt` | (dir5, column-convex) (novel) | 700 (n = 1..700) |
| `results/b_ccctrlb_upload.txt` | (ctrlB, column-convex) (novel) | 250 (n = 1..250) |
| `results/b_hvdir4_upload.txt` | (dir4, HV-convex) (novel) | 700 (n = 1..700) |
| `results/b_ctrlb_unfiltered_upload.txt` | control B unfiltered (novel) | 14 (n = 1..14, brute-force bound) |

The five novel sequences have no A-number, so their b-files carry descriptive
names and a header stating the class. `b_ctrlb_unfiltered_upload.txt` is short
because that cell has no transfer matrix — it is DFS-bound at n = 14.

Draft OEIS comments, four new interpretations plus one correction, all staged
and all jasonp's call:

| entry | what it says | where |
|---|---|---|
| A055834 | 4-cone directed king animals | `results/king-subfamilies.md` |
| A007052 | directed column-convex polyplets, with the Temperley derivation | `results/king-subfamilies.md` (as "Theorem (dcc)"; comment text in `oeis/draft-comments-subfamilies.txt`) |
| A225114 | staircase king animals = skew shapes with no empty rows or columns, with the bijection | `results/king-subfamilies.md` |
| A018902 | 4-cone directed column-convex polyplets, explaining the entry's INVERT-of-A007052 formula | `results/middle-kingdom-phase3.md` |
| A187077 | correction of the A059716 comment, plus the missing derivation | `results/convex-polyplets.md` |

Tools and gates: `cpp/directed_cone_anchor.cpp` (mode `grid`, 20 cells),
`cpp/middle_kingdom_tm.cpp`, `cpp/convex_area_tm.cpp`,
`cpp/convex_perim_tm.cpp`, `cpp/prec_guess.cpp`,
`experiments/multidirected_king.py`, `experiments/convex_growth.py`,
`experiments/oeis_lookup.py`. Gates `make gate-king-grid gate-multidirected
gate-convex-dfinite gate-middle-kingdom`, all GREEN 2026-08-05.

## Open

From `results/middle-kingdom-phase3.md`:

- (ctrlB, column-convex) and (dir4, HV-convex) are non-D-finite only as
  exclusions in a box, like the unrestricted HV-convex verdict they sit beside.
  No proof.
- (ctrlB, column-convex)'s box is the smaller of the two only because its
  series is 250 terms rather than 700; n = 400 is measured at about 11 minutes
  and 4 GB single-core and would carry the exclusion to roughly order ≤ 16 /
  degree ≤ 16. Not run — no current claim needs it.
- ~~(dir4, HV-convex) sharing the unrestricted constant to 49 digits looks like
  a theorem waiting.~~ **CLOSED 2026-08-05**, `results/hv-growth-sandwich.md`:
  Proposition 6 proves that every class between staircase and HV-convex has
  growth constant µ, so no bijection is involved and the 4-cone condition is
  not special. Two by-products: A225114 (the grid's whole staircase column) has
  growth constant µ, measured to 204 digits and absent from the OEIS entry; and
  the 4-cone series carries an extra exponential at 2.51457964387872918851…,
  the growth constant of the truncated descending block. **Corrected
  2026-08-06:** the plan's Table B does not say the two series fail to share a
  subdominant rate. Splitting the 4-cone series by unimodality phase gives a
  4-cone-directed subclass with `d_n/d_(n−1) = 0.48100879371`, the unrestricted
  rate, trusted to 76 digits; the restricted series has the extra exponential
  *in front of* the shared one, and the diagnostic reports only the largest.
  That the extra one is the descending block's is proved as an equality of
  growth rates (Proposition 7) and conjectured at the level of the sharp
  asymptotics Table B measures. **The amplitude ratio, 2026-08-06:** it has no
  closed form but it does have an explicit expression —
  `r = (1/2)(w4·φ)/(w·φ)`, a ratio of two `q`-series at `q = 1/µ` contracted
  against the staircase operator's Perron eigenvector, which is the bounded
  solution of the three-term recurrence
  `φ(h) = (2 − x^{h−1})φ(h−1) − φ(h−2)` (Propositions 9–11 of
  `results/hv-growth-sandwich.md`). That identity and the re-measured split
  series agree to 293 digits, which takes the ratio from 54 trusted digits to
  251; PSLQ is negative in every enlarged box, over `Q` and over `Q(µ)` alike.
  The same recurrence gives `µ` by shooting, 987 digits in 1.6 s.
- Nothing outstanding on the twelve cells themselves.

Also open, from earlier phases: A222205's µ has no minimal polynomial, because
ρ_M is defined transcendentally through Bacher's non-D-finite intermediate
series B (`results/multi-directed.md`); and the A055834 comment stays
conjecture-grade until the 4-cone cone gets a heaps-of-pieces derivation
(`results/king-subfamilies.md`).

## Nothing is submitted

No sequence, b-file or comment from this campaign has been sent to OEIS or to
any other external service. Submission is jasonp's call and is gated on the
viva. `oeis/SUBMISSION.md` records the standing pacing, and puts the
comment-grade edits to A187077, A007052 and A225114 in the discuss-first wave
— after editor rapport exists, not first.
