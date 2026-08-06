# Middle Kingdom follow-ups — the five avenues the campaign left open

**Status:** planned 2026-08-05, authored in-session with jasonp. Execute
post-`/clear` from this file alone. Nothing below has been run except where
marked MEASURED — those numbers were measured in this session and are the
reference values every phase compares against.

Source of the avenues: `results/middle-kingdom.md` ("Open"),
`results/middle-kingdom-phase3.md` ("Open"), and a review pass over the
campaign against the rest of the repo. The campaign itself is closed; this is
its tail, plus one repo-wide item the review turned up.

Off the a(n) record path. The project still closes at a(40); none of this
reopens it.

## Model targeting

| phase | model | why |
|---|---|---|
| 0 | **Sonnet** | transcription of measurements already made, into named files |
| 1 | **Opus** | an operator/kernel argument; open-ended mathematics |
| 2a | **Sonnet** | a new TM mode, a RED control, a gate, a timed run |
| 2b | **Opus** | D-finiteness verdict and what it means for the perimeter lever |
| 3 | **Opus** | correcting a banked criterion; judgement, not mechanics |
| 4a | **Sonnet** | a min-reduce in an existing DFS, a run, a read-only OEIS lookup |
| 4b | **Opus** | convention pinning, then guess-and-prove |
| 5 | **Sonnet** | a fitting script and a table; the reading is already written below |

A Sonnet run that hits *any* mismatch against the reference values below stops
and reports. It does not adjust the reference.

## Hard rules (from MEMORY.md; violating any fails the phase)

- **C++ for compute, Python as thin glue.** Anything running over a minute gets
  ported.
- **Named on-disk scripts only** — no `/tmp`, no heredocs, no long-lived
  `python -c`. Binaries build into `build/`. `docs/job-checklist.md` before any
  compute job.
- **RED-first**: every new counting routine gets a test that fails before it
  works, and a control that must diverge.
- **`make` once** in any session that touches code, not just the nearest gate.
- **No dalby/ayr job without asking jasonp first**, and nothing over an hour
  without explicit agreement. Everything here is laptop-scale by design except
  where Phase 5 says otherwise, and Phase 5 says *do not start it*.
- **Nothing goes to OEIS or any external service.** `experiments/oeis_lookup.py`
  is a read-only lookup and is allowed; submission is jasonp's, gated on the
  viva.
- **`paper/technical-report.tex` is read-only.** Check `lsof` for jasonp's
  `.swp` files before editing anything in `paper/`.
- Before calling any sequence or result new, grep `results/`, `docs/`,
  `papers/` and run `experiments/oeis_lookup.py`.

## Reference values — MEASURED 2026-08-05, gympie, `git=54440c2-dirty`

Do not "fix" a mismatch by editing this table.

**A. A006770, exclusion boxes on the 40 banked terms** (`build/prec_guess`,
input `results/b006770_upload.txt`, prime 2^61−1, seconds per box):

| box (J,D) | `prec` verdict | `alg` verdict |
|---|---|---|
| (4,5) (5,4) (4,6) (3,7) (3,8) (2,11) (6,3) (7,3) | EXCLUDED | EXCLUDED |
| (5,5) | INCONCLUSIVE (35 rows ≤ 36 unknowns) | EXCLUDED |
| (6,4) | INCONCLUSIVE (34 rows ≤ 35 unknowns) | — |

**B. (dir4, HV-convex) against unrestricted HV-convex** (700-term series,
`results/mk_hvdir4_terms_n700.txt`, `results/convex_area_terms_n700_king.txt`):

```
amplitude ratio a_dir4(n)/a_HV(n), 54 trusted digits (n=600 vs n=700, minus 2 guard):
0.462109049209942440035662387700305832841163439729980425
subdominant ratio d_n/d_(n-1):  dir4  0.803651401483    unrestricted  0.481008794
PSLQ at 54 digits: NO relation in any in-capacity box --
  degree <= 12 at height <= 1e2, <= 5 at 1e4, <= 3 at 1e6, <= 2 at 1e8
```

**C. A006770 by the geometric-case growth pipeline**
(`experiments/convex_growth.py results/b006770_upload.txt`): d_n/d_(n−1) rises
0.94519 → 0.95062 over n = 35..39 — drifting toward 1, the power-law signature,
against a flat 0.481 for HV-convex. Trusted digits: **0**; the tool's µ = 7.1058
is wrong at the 3rd digit, correctly, because Aitken-on-ratios is the wrong
accelerator when θ ≠ 0. This corroborates `results/series-analysis-da.md`'s
θ = −1.000(1) by a method that assumes no ansatz.

**D. Strip ladder, two-parameter finite-size fit** `ln µ_H = ln λ − a/H − b/H²`
on consecutive triples of the banked `µ_H` (H = 2..17,
`results/strip-mu-certificates.md`, `results/strip-mu-engine-resumption.md`):

| triple | λ | a | b |
|---|---|---|---|
| [11,12,13] | 7.29817 | 1.65351 | 3.19705 |
| [13,14,15] | 7.25820 | 1.51121 | 4.11872 |
| [15,16,17] | 7.22999 | 1.39472 | 4.99006 |

`H(ln λ − ln µ_H)` with λ = 7.1102: still falling at H = 17 by 0.035 per rung,
increments shrinking only ~6.5% per rung where a clean 1/H² correction predicts
(16/17)² = 11.4%. Identical for λ = 7.111.

---

## Phase 0 — bank the measurements (Sonnet)

Three results measured in-session have no home on disk. They are cheap to
re-derive and worthless if lost.

1. **Table A into a new `results/isotropic-dfinite-boxes.md`.** State the
   method in one paragraph (full column rank mod p is a proof over Q, boxes
   nest — both already written up in `cpp/prec_guess.cpp`'s header and
   `results/convex-polyplets.md`), the table, and the honest scope: the boxes
   are small because 40 terms is short, and a finite-box exclusion is not a
   non-D-finiteness proof. Cross-reference `paper/related-work-notes.md:51`
   ("OPEN (isotropic): believed not D-finite, not proven") and
   `paper/polyplets-report.tex:878` (the anisotropic theorem, which this does
   not touch). Re-run every box in the table and confirm before writing.
2. **Table B and C into `results/middle-kingdom-phase3.md`**, replacing the
   "stable to 20 digits" line in the (dir4, HV-convex) section — 54 digits is
   the measured figure — and adding the subdominant rates and the PSLQ
   negative. Table C goes into `results/series-analysis-da.md` as a short
   "independent corroboration" section.
3. **Table D into `results/strip-growth-lambda-bounds.md`** as a new section,
   "the ladder's approach to λ is not analytic in 1/H in the range measured".
   Phase 5 replaces this with the full treatment; if Phase 5 runs first, skip
   this item.

**Acceptance:** every number reproduced from scratch by the commands recorded
alongside it; no claim in any of the three write-ups that is not in the tables
above or already banked elsewhere; `make` GREEN.

## Phase 1 — (dir4, HV-convex): find the operator argument (Opus)

The two series share a dominant singularity to 49+ digits and do **not** share
the subdominant one (0.8037 vs 0.4810), and the amplitude ratio has no small
algebraic form at 54 digits (Table B). That combination argues against the
bijection framing in `results/middle-kingdom-phase3.md`'s "Open" section: a
bijection would move both singularities together.

Target instead a **factorization of the HV-convex transfer operator** in which
the 4-cone condition (`b` never drops by more than one row, Proposition 2)
changes the numerator and the second pole but leaves the first pole fixed.
Concretely:

1. Write both operators in the same basis. `cpp/middle_kingdom_tm.cpp` modes
   `hv` and `hvdir4` already differ by exactly that one condition on the
   descending phase — the code is the statement of the difference.
2. Ask whether the dir4 constraint acts as a rank-bounded perturbation of the
   HV operator, or as a change of the boundary/phase structure only. The
   dominant eigenvalue surviving to 49 digits means the perturbation must not
   touch the leading spectral data.
3. If a mechanism is found, the deliverable is a proposition with the same
   status as Propositions 1–5 of Phase 3: proved, and brute-force-checked
   against `results/mk_grid20_n14.txt`.

**Kill criterion:** if no mechanism is visible after the operator comparison,
stop and write the negative up as a sharpened open problem (the three measured
facts of Table B are already worth more than the "bijection waiting" framing
they replace). Do not start a term-level search for a bijection.

**Acceptance:** either a proposition with a proof and an n ≤ 14 check, or a
one-section write-up of the sharpened problem citing Table B. Either way the
"Open" sections of `results/middle-kingdom.md` and
`results/middle-kingdom-phase3.md` get updated in place.

## Phase 2a — (dir4, HV-convex) by semiperimeter: the mode and its validator (Sonnet)

`cpp/convex_perim_tm.cpp` counts HV-convex animals by semiperimeter and takes
only `SMAX [king]`. Add a dir4-filtered mode.

**Expected translation — VERIFY, DO NOT ASSUME.** In a row-interval DP,
Proposition 2's "`b` never drops by more than one row" should become "on the
left-descending phase the left boundary strictly decreases every row": if a row
fails to extend left and a later row does, the columns either side of that gap
differ in `b` by at least 2. Check this on paper against Proposition 2 and then
against the brute force below *before* trusting it; if it is wrong, the correct
condition is what the brute force says it is.

Validation, in this order:

1. **RED control first.** A deliberately wrong variant (e.g. non-strict
   decrease) must fail to reproduce the brute-force values.
2. **Brute force by semiperimeter.** For HV-convex animals the semiperimeter is
   the bounding box `W + H`, so `build/directed_cone_anchor`'s existing
   enumeration can tally `HV ∧ dir4` animals by `W + H` instead of by area.
   Coverage caveat, state it in the write-up: an area-≤14 enumeration only
   settles `s ≤ 7` completely (an animal of semiperimeter s can have area up to
   ~s²/4), so this validates the first several terms, not the tail.
3. **Termwise sanity against the unrestricted mode**: dir4 counts must be ≤ the
   `king` counts at every s, with equality only where every animal of that
   semiperimeter is 4-cone directed.
4. Keep the A005436 polyomino control wired throughout — an unpowered guesser
   is the failure mode that matters in Phase 2b.

**Acceptance:** the new mode reproduces the brute force on every s it covers;
the RED control diverges; `make gate-*` for the new gate GREEN; full `make`
GREEN; series to s = 200 written to `results/` (the unrestricted run took
1246 s at s = 200 — budget similar, measure and record wall and peak RSS).

## Phase 2b — is the perimeter lever robust to directedness? (Opus)

Run the guessers on the Phase 2a series: `experiments/convex_perimeter.py`'s
`find_prec` for a P-recurrence, and `build/prec_guess prec|alg` for exclusions.
The banked fact this tests: HV-convex king animals are **D-finite by
semiperimeter** (order-5 degree-2, holdout-verified to s = 200) and **not
D-finite by area** — `results/convex-polyplets.md`.

- **D-finite** ⇒ "area wild, perimeter tame" is a property of HV-convexity
  itself and survives the 4-cone restriction. Report the recurrence with a
  genuine holdout (fit on the first rows only, predict the rest), exactly as
  Phase 1b did.
- **Not D-finite** ⇒ the first case in the repo where the perimeter lever
  fails, which is the more interesting outcome and needs the four-arm control
  discipline of `tests/gate_convex_dfinite.py` before it is believed.

**Acceptance:** a verdict with its box stated, the control arms reported
alongside, and `results/convex-polyplets.md` updated in place (it already owns
the perimeter section — do not start a new note).

## Phase 3 — correct the countable-subpopulations criterion (Opus)

`results/countable-subpopulations-criterion.md` says convexity ⇒ 1D profile
evolution ⇒ algebraic/rational GF. Phase 3 of the campaign falsifies that as
stated: (ctrlB, column-convex) is column-convex, is a 1D profile evolution, has
rational **rigorously excluded** to order 12 and D-finite excluded in (12,12)
(`results/middle-kingdom-phase3.md`).

Replace the implication with the mechanism, which is now visible in three
places (defect-gas's unbounded interval width, the convex-area mirage, and
ctrlB's running minimum):

> **Does the predicate need a running extremum — an unbounded integer that is
> not the area — in the transfer state?** No ⇒ rank-1 operator, rational GF.
> Yes ⇒ O(n²) states and no closed form.

Also close that file's "open nugget" (HV-convex polyplets, "plausibly still
algebraic") — the guess was wrong, and `results/convex-polyplets.md` has the
disproof at order ≤ 24 / degree ≤ 24.

Record, and do **not** pursue: the interpolating family "every local minimum of
`b` within k rows of the global minimum" needs an unbounded counter for every
finite k (a later descent retroactively invalidates earlier local minima), so
it would farm a supply of sequences all as synthetic as ctrlB. The design rule
is the deliverable; the sequence family is not.

**Acceptance:** the criterion file states the rule, cites the three instances,
marks the nugget closed, and contradicts nothing in `results/king-subfamilies.md`
or `results/middle-kingdom-phase3.md`.

## Phase 4a — minimum site-perimeter, on the existing enumeration (Sonnet)

`unexplored-avenues.md` idea 7, re-scoped: this is a min-reduce over animals
already being generated, not a new search. Add to
`cpp/directed_cone_anchor.cpp`'s pass a per-n minimum of the site perimeter,
and emit `n → min perimeter` alongside the grid table.

**Before writing the reduce**, pin the convention and put it in the write-up:
site perimeter = the set of empty cells adjacent to the animal, under **which**
adjacency (king or rook)? `results/polyplet-zoo.md` cross-checked a
site-perimeter convention against the percolation literature — use that one,
cite it, and state it explicitly. `unexplored-avenues.md` idea 10 is the reason
this matters: on this lattice "boundary" is convention-dependent.

Sanity anchor: a k×k block has king site-perimeter 4k+4, so the answer should
sit near 4√n + 4.

**Acceptance:** values to n = 14 (the pass already runs there in 512 s on 8
threads; adding a min-reduce should not move that materially — measure it);
reproduces 4k+4 at every perfect square by hand check; a RED control (a
deliberately wrong adjacency) that gives different numbers;
`experiments/oeis_lookup.py` run on the resulting sequence and its 6-term
prefix, result recorded either way. Compare against the square-lattice
analogues — A027709 (minimum edge perimeter of an n-omino) and A261491
(minimum site perimeter, `ceil(2+sqrt(8n-4))`) — and say plainly whether ours
matches, since a match would mean the king constraint is not biting. Verify
any OEIS A-number before citing it: A-numbers are sequential by submission,
not by topic, and an earlier draft of this line cited A027710, which is a
balls-in-boxes sequence unrelated to perimeter.

## Phase 4b — closed form, if the data supports one (Opus)

Guess-and-prove in the style of `results/maxhole-proof.md`: fit a closed form to
the small-n data, then prove it by an extremal argument (the lower bound from a
discrete isoperimetric inequality, the upper bound by exhibiting the family).

**Kill criterion:** if `oeis_lookup.py` returns a hit in Phase 4a, this is a
known sequence and the phase reduces to a one-paragraph note plus a
cross-reference. Do not prove someone else's theorem.

**Acceptance:** a closed form with a proof and a check against every n the
enumeration reached, or a written negative saying which n the guess breaks at.

## Phase 5 — the finite-size scaling ladder (Sonnet for the mechanics)

Turn Table D into a proper section of `results/strip-growth-lambda-bounds.md`
with the fits reproducible from a named script (`experiments/strip_fss.py`).

What it must say, and this is the reading — do not re-derive it, verify it:

- The two-parameter fit `ln µ_H = ln λ − a/H − b/H²` does not converge on 16
  rungs. λ overshoots the differential-approximant 7.1102 by 0.12 at the top
  triple and drifts ~0.013 per rung; b is still climbing.
- The surface term itself is not converged: `H(ln λ − ln µ_H)` falls by 0.035
  per rung at H = 17, and its increments shrink by only ~6.5% per rung against
  the 11.4% a 1/H² correction predicts. There is a term between 1/H and 1/H²,
  most likely a log.
- Consequence: **no 1/H² coefficient, hence no central charge, can be read off
  this ladder** — `unexplored-avenues.md` idea 6.1 is not an afternoon's
  fitting, and its own stated prerequisite ("is λ known precisely enough") is
  now answered: no, not from the ladder side.
- Insensitive to the λ input: the picture is identical at 7.1102 and 7.111.

**Do NOT start a job for more rungs.** H ≥ 18 is where the enumerator's build
RSS binds (4.94 GB measured at H = 16) and it is a beg-and-agree item, not a
laptop run. Cost it from `results/strip-mu-fast.md` throughputs and record the
estimate; the decision is jasonp's.

Optional and cheap, if the fitting script is there anyway: test a third ansatz
`ln µ_H = ln λ − a/H − c·ln H/H²` and report whether λ then lands nearer 7.110.
A positive is a hint, not a result — with three free parameters on 16 rungs it
proves nothing, and the write-up must say so.

**Acceptance:** the script reproduces every number in Table D; the section says
the four things above and claims nothing beyond them; `make` GREEN.

---

## Ordering and cost

Cheapest first, and they are independent — nothing here blocks anything else:

| phase | model | cost | why in this position |
|---|---|---|---|
| 0 | Sonnet | ~1 session | banks measurements that otherwise evaporate |
| 5 | Sonnet | ~1 session | data on disk, reading already written |
| 3 | Opus | short | a correction to a banked criterion, no compute |
| 4a/4b | Sonnet/Opus | ~1 session + proof | min-reduce on an existing pass |
| 2a/2b | Sonnet/Opus | ~1 session + 20 min run | the only real code build here |
| 1 | Opus | open-ended | genuine mathematics; kill criterion above |

Phase 1 is the only one that can fail to produce a deliverable, and its kill
criterion converts that failure into a sharpened open problem.

## Explicitly out of scope

- Re-opening the grid. Twelve cells are settled and eight are proved.
- Any λ bound from these families — the door is shut from the subclass side
  (multi-directed's 6.475196280297 < the certified 6.543).
- The frontier engine, the a(n) record, and `paper/technical-report.tex`.
- OEIS submission of anything, including the b-files this campaign staged.
