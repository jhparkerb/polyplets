# Team brief — adversarial structure hunt on the T(n,H) triangle

## The object

T(n,H) = number of fixed king-animals (polyplets) with n cells and bounding-box
height exactly H. The banked triangle is `results/ns_a36/perheight/hH.out`
extended to n ≤ 40 (see HANDOFF.md for the authoritative path and provenance);
a(n) = Σ_H T(n,H), and a(40) is the project's final term. Nothing past n = 40
has value.

Directions through the triangle:

- **rows** — n fixed, H varying (the height distribution)
- **columns** — H fixed, n varying (strip transfer matrix, growth rate μ_H)
- **diagonals** — k = n − H fixed
- **cells** — individual T(n,H), and small local stencils
- **arbitrary slopes** — s·n + t·H fixed, including anti-diagonals

The first four have a combinatorial move behind them: adding a cell, adding a
row, walking the excess. Arbitrary slopes do not — nothing adds a cell and
removes a row — so they are **not an agent's assignment**. The harness sweeps
all small (s,t) slices and stencils mechanically through the auto-verifier, at
no judgment cost, and an agent looks only if something survives. Priority goes
to slices with a mechanism.

## Mission

Find relations that are NEW to this repo, and rank them by one criterion:
**does the relation let a(40) (and the huge T(n,H) near it) be checked by a
route that does not re-run the enumeration engines?**

The winning result is the simplest relation that turns banked numbers into a
prediction. A messy relation that predicts row 40 from validated small rows
beats an elegant one that predicts nothing. Complexity beyond what the
prediction requires is a defect, not a bonus.

## The independence problem — read this before anything else

A relation fitted on banked cells and then used to "check" a(40) inherits the
lineage of its inputs. If it consumes row 39, it catches a bug local to row 40
and nothing else; a shared misconception about king-connectivity passes
straight through it. This is the same ruling as
`docs/second-source-team-brief.md`, applied to structure hunting.

Three defences, and every candidate is scored on all three.

**(a) Fit low, predict high.** The default fit region is **n ≤ 22**. A relation
fitted there and then reproducing n = 23…39 exactly has been tested against
seventeen rows before it ever touches a(40); a(40) becomes its eighteenth
prediction, not its first. A proposer wanting a longer fit region must name the
hypothesis class that forced it (some classes genuinely cannot be fitted below
the diagonal law's onset) and accept a lower independence score. Hold out **by
n**, never randomly — the target is extrapolation in n.

**(b) Derivation blind, validation informed.** Derive from the lattice
definition and cells you brute-forced yourself. Do not read banked data while
deriving. A separate verifier then tests the finished relation against the
triangle, so every banked cell it matches is a real test rather than a fitted
point. This does not mean pretending the repo does not exist: read the
prior-work list below first, so you do not spend the round re-deriving the
diagonal law.

**(c) Prefer provable to fitted.** A congruence proved from the definition
checks a(40) with zero engine dependence. `docs/proofs/diagonal-law.md` and
`results/ternary-spine.md` show this project can get there. A proof-backed
relation outranks an empirical one of the same tier, always.

### Mandatory first task, every proposer

Before anything else, write your own polyplet enumerator from the lattice
definition — your own connectivity rule, your own code. Do **not** read
`core/transition.h`, `cpp/strip_tm.cpp`, or any existing kernel first. Compare
against the banked triangle out to n ≈ 12 and report the comparison.

This costs minutes and buys a genuinely independent connectivity rule per
proposer. A disagreement at small n would be the most important thing this team
could produce; report it immediately and stop.

## What already exists — you must beat this, not rediscover it

Any candidate that restates one of these scores zero, and a report claiming
novelty without showing the grep is rejected outright.

- `docs/proofs/diagonal-law.md` — T(n, n−k) = P_k(n)·3^(n−1−3k) for n ≥ 2k+1,
  proved, integrality proved. Diagonals are SOLVED near the top edge.
- `docs/proofs/universal-diagonal-law.md`, `docs/proofs/T-n-nm1.md`,
  `docs/proofs/T-n-nm2-and-general.md`
- `results/diagonal-closed-forms.md`, `results/diagonal-law-below-onset.md`,
  `results/dm-diagonal-recon.md`, `results/dmirror-diagonals.md`
- `results/triangle-structure.md`, `results/triangle-combinations.md`,
  `results/triangle-snf.md` — prior triangle-wide structure hunts
- `results/subgroup-mod4.md`, `results/percell-mod4.md` — **omitted from the
  first version of this list, which cost a proposer part of a round.** The
  first banks T(n,H) ≡ I_H(D2ax) (mod 2) checked on all 820 cells *including
  row 40*, a(n) mod 4 at every n ≤ 40, and mod 8 to n = 32 (Fix(d) wall); the
  second verifies the per-cell mod-4 refinement to n = 32 with an explicit
  measured decision NOT to buy it at n = 40. Anyone assigned Burnside or
  parity structure must read both first — most of that ground is taken.
- `results/height-distribution-collapse.md` — universal row shape, ⟨H⟩ ~ n^0.6407
- `results/ternary-spine.md` — mod-3 spine, cubic W³ = W² + t
- `results/anisotropic-not-dfinite.md` — the bivariate GF is NOT D-finite, an
  unconditional theorem. Do not propose a global P-recurrence in (n,H). Sliced,
  local, modular, and asymptotic-with-error-bar relations remain open; so does
  a slice-wise recurrence whose order grows with the slice.
- `results/strip-growth-lambda-bounds.md`, `results/band-structure-probes.md`,
  `results/king-column-motzkin.md` — column direction. **Note:** that last
  file lives on branch `second-source` (commit a6b8f6a), not on this branch —
  read it with `git show a6b8f6a:results/king-column-motzkin.md`. It banks,
  with proof, that the king column TM has exactly Motzkin(H+1) − 1 states
  (series H=1..10: 1, 3, 8, 20, 50, 126, 322, 834, 2187, 5797), so the
  Motzkin identification is prior work, not a novel observation.
- `docs/second-source-team-brief.md`, `docs/second-source-brief-critique.md`
  — **also on branch `second-source` only** (commit 2b3115b), not on this
  branch: `git show 2b3115b:docs/second-source-team-brief.md`. Read it before
  scoring any candidate's rule independence. Its ruling: the strip transfer
  matrix **does not qualify as verification**, because its union-find rule is
  the same rule as `core/transition.h` and the kink kernel. Agreement between
  them is evidence against transcription, overflow, and sharding faults, and
  "no evidence at all" against a wrong shared connectivity rule. Any candidate
  of strip-TM class is therefore a consistency check, not a second count.

## Calibration — where the value actually is

Tier A (below) is a long shot. If a low-order relation predicted a(40) from
smaller n, the column and diagonal work would very likely have tripped over it
already. Expected value is concentrated in **Tier C**: exact congruences and
valuation identities, ideally proved. Do not chase Tier A and report nothing.

## Team shape

Sized deliberately small. This is not a code search where more agents see more
evidence — the triangle is a fixed, finite object of a few hundred cells. Extra
rounds do not gather information, they re-mine the same numbers, and coincidence
yield rises with the mining.

**Wave 0 — 1 agent.** Build the harness before anything else runs: the triangle
loader, the candidate schema, the automatic verifier implementing the fit-on-
n≤22 / predict-23…39 rule in exact integer arithmetic, and the mechanical sweep
over small (s,t) slices and stencils. Every later agent emits candidates in this
schema, and the verifier culls before any agent reads them. Without this, four
proposers write four loaders and produce candidates nobody can compare.

**Wave 1 — 4 proposers**, split by **hypothesis class**, not by geometry.
Splitting by slice guarantees four agents independently try low-order linear
fits and small-modulus congruences and you pay four times for one negative.

1. **Proof-first.** Derive from the definition. Push the proved structures off
   their onset boundaries. Aim at statements with proofs, however weak.
2. **Congruence, valuation, and symmetry.** Modular and p-adic structure across
   the whole triangle, beyond mod 3. Includes Burnside cross-links: identities
   tying fixed counts T(n,H) to the free and one-sided counts this project
   computed on a different path (the related-sequences work) bring genuinely
   independent inputs into the check.
3. **Slice recurrences.** Rows, columns, diagonals, and cross-direction links
   between a column's rational structure and a diagonal's polynomial structure.
   Fitted on the short region; report honestly when a class cannot be.
4. **Cross-lattice control.** Square polyominoes and polyiamonds have published
   counts nobody here produced. Any relation with a real mechanism should have
   an analogue there — test it against OEIS data. A fitting procedure that
   "finds" relations contradicting published square counts is exposed for free.

**Wave 1 refuters — 2 fixed agents**, working the shortlist that survived the
machine, not one refuter per candidate. Default verdict is "overfit". Standard
attacks: free parameters against held-out cells actually predicted; the edges
(small H, H near n, the onset boundary n = 2k+1 where the diagonal law is known
to fail at n = 2k); the same fitting procedure applied where it should fail;
and whether the candidate is a restatement of prior work. A relation survives
only if the refuter reports it could not be broken and names the attacks tried.

**Synthesis — the lead, not an agent.** It is judgment on a short list; an extra
hop only loses detail.

Seven agents. **Two rounds, the second conditional and narrow** — 1 to 3 agents
chasing one specific thing round 1 turned up. If round 1 produces nothing above
Tier D, stop. Round 3 on fixed data returns numerology in a confident tone.

## Acceptance ladder

- **Tier A** — predicts T(40,H) or a(40) from strictly smaller n, exactly, with
  a checker short enough to read in one sitting.
- **Tier B** — predicts a nontrivial subset of the n = 40 row (all H above a
  threshold, all H in a residue class), exactly.
- **Tier C** — an exact congruence or valuation identity that row 40 satisfies
  and a wrong count would almost certainly violate. This is where the value is.
- **Tier D** — an asymptotic relation with an error bar tight enough to catch a
  digit-level error in a(40). State the error bar and how it was obtained.
- Softer than that: a collapse or a qualitative pattern. Report it, do not lead
  with it.

Every survivor reports, explicitly:

- **bits of independent check on a(40)** — defined as log₂ of the a-priori
  probability that a wrong count passes. A congruence mod m gives log₂(m). No
  handwaving.
- **input footprint** — how many banked cells it consumes and the largest n
  among them.
- **derivation independence** — did the derivation touch banked data, or only
  the definition and self-enumerated cells?
- **rule independence** — does it decide connectivity the way the engines do?

## Rules of engagement

- Measure before you reason. If a claim is cheap to test against the banked
  triangle, test it first and quote the numbers.
- No uncited empirical claims. No "typically", "often", "tends to" without the
  computation behind it.
- Fit on a proper subset, hold out the rest by n, report both sets. A relation
  fitted on all available cells is not a result.
- Exact integer arithmetic. These numbers overflow everything; floating point is
  for asymptotics only, and then with a stated error model.
- C++ or exact-arithmetic Python for compute; Python is thin glue. Named scripts
  on disk under `experiments/`, never stdin, never /tmp, never binaries outside
  `build/`.
- No job over an hour without asking. Anything that might exceed 5 minutes runs
  in tmux, not the foreground.
- Do not edit `paper/technical-report.tex`. Do not commit `docs/viva-*.md`.
- Deliverable per round: one markdown file under `results/` per surviving
  relation, plus one ranked summary. Negative results get written down too — a
  slice with provably no low-order relation is worth recording so nobody
  re-probes it.

## The failure mode to avoid

The natural output of a naive run is numerology: linear combinations that hold
on the fitted cells, mod-p coincidences with no mechanism, and "laws" that are
the diagonal law in disguise. The machine filter and the refuters exist to burn
those. One relation that survives a hostile refuter and predicts real cells is
worth more than ten that merely fit.
