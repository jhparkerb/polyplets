# Time at the Bar — the last round before the landing

Written 2026-08-22 against `b534558`, at jasonp's direction, from a survey of
the tree. It is the round after `docs/last-orders.md`, which is complete: its
C section executed eight items and scoped three, its A section closed
everything that was work rather than a decision, and its B section made every
removal that was a removal.

**The rule this list defines.** When every item below is either done or struck
with a one-line reason, we work the publication plan together, publish the
repository, and make the OEIS submissions. Nothing from that plan appears here
— the licence, the branches, the history, the ledgers, the front-door README,
the clean-clone run, the gates at R, the submissions themselves. Their
inclusion is implied. `PRE-LANDING.md` is that checklist and it is not
repeated.

**What this file is not.** It is not authorisation. Every item carries what it
costs where that is measured and an honest *asserted* where it is not, and
every one names the sentence that gets shorter — or says that none does.

**What is new since Last Orders.** Four things changed the picture and each
moves at least one item below: depth 5 was repriced by an order of magnitude
(`results/depth5-cost-settled.md`); the reach merge was established and parked
(`results/skeletonkey-nfamily-merge.md`); the square-lattice validation put an
external oracle under Undertow at J = 1
(`results/undertow-square-validation.md`); and `results/mathematics.md` and
`results/confidence.md` between them now say in plain terms what the project
found and how far it can be trusted, which is the baseline any of this has to
improve on.

Three sections, run in order, with the corrections each pass forced on the
next recorded at the end.

---

## A. Research that could still be fruitful

Ordered by cost. The standing filter from `docs/skeletonkey-reprompt.md`
applies to every counting item: place it in one of the three boxes and answer
the bijection, cancellation and accounting tests before opening a file. Two of
the items below are in box 3 and say so.

### A1. Combinations of things that already work

**A1.1 — The reach merge against Motley's wall, and what the census is worth.**

`results/skeletonkey-nfamily-merge.md` is established, gated eight ways, and
parked at jasonp's direction 2026-08-20. What the file does not do — because it
was parked before it could — is connect its number to the decision that is
actually open.

The merge collapses the end-of-column frontier from `2.70^H` to `2.48^H`, and
6.71× at H = 8 once the exact-height flags come off in favour of the `C_H`
telescope. `results/kink-carry.md` names that frontier as the wall. The a(40)
run's H = 21 frontier peaked at 355,390,806 records and 363.4 GB of disk. The
two items `results/confidence.md` calls the last soft spot — the H = 20 sweep
that turns `P_21` into a holdout, and the H = 21 cell that never fits — are
both priced against that frontier.

So the merge's payoff is not abstract. It is whether H = 20 at Nmax 41 costs
190 GB or something materially less, and whether H = 21 comes back inside the
disk budget at all. **Nobody can answer that today** because the file forbids
quoting a number at H = 21, correctly: the ratio compounds ~1.087×/height from
nine points with no closed form, no OEIS match on `8, 19, 43, 101, 239, 575,
1399, 3441` and no recurrence with surplus.

The cheapest step of the unpark ladder is exactly the one that removes the
extrapolation: a C++ census of the key space at H = 18..21, generating
successors cell-at-a-time so it costs `states × H` rather than `states × 2^H`.
That is a measurement, not a build, and it is the input to the decision rather
than the decision.

Two things the census does not settle, both already written down in the merge
file and repeated here so the item is not oversold: whether the mid-column
stage tables inherit the cut (the congruence is proved at column boundaries
only), and what the telescope costs the completion prune, which knows how many
cells are still needed to reach an untouched boundary row and loses that half
of its knowledge in a flagless run.

**On Motley specifically.** Gates B and D of the merge probe show the merged
key automaton reproduces `cutcount_b1`'s banked `C_H` rows exactly, so a
merged-key engine is an alternative producer of Motley's own object. It does
**not** follow that Motley's cancellation DP state admits the same cut — that
is a different state space and nobody has looked. Say the weaker thing.

*Sentence that gets shorter:* `results/confidence.md`'s "the formula governing
it is fixed by exactly two data points with nothing left over to check it
against", by making the run that fixes it affordable rather than by running it.

**A1.2 — The characteristic-2 basis, asked on the N-family keys.**

`docs/skeletonkey-reprompt.md` calls the explicit char-2 basis "the single
largest open technical question in the mission". Two files in the tree hold
halves of an answer and have never been put together.

`results/exactchange-probes.md` §1: the char-2 rank is **A034299 exactly**,
`6, 15, 27, 58, 112, 229, 453, 912, 1818` at H = 4..12, with a closed form, a
generating function `1/((1−x²)(1−x−2x²))`, and the recurrence

    r(H) = 2·r(H−1) + (−1)^(H−1)·⌊(H+1)/2⌋

§2 of the same file then reports the negative that stopped the hunt: φ is
injective within every column mask class, all compression is cross-mask linear
algebra, and none of `(mask)`, `(mask, #blocks mod 2)`, `(mask, #blocks)`
parametrizes the quotient.

`results/skeletonkey-nfamily-merge.md` supplies a fourth candidate key that
those three lacked: the multiset of block reaches `N(b)`, which is **proved to
be a congruence** — gate C checks `succ_key(key(s), m) == key(succ(s, m))`
exhaustively over every reachable state against every column mask. Its class
counts are `8, 19, 43, 101, 239, 575, 1399, 3441, 8539` at H = 4..12.

Set the two side by side and the arithmetic is the point:

| H | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|
| N-key classes | 8 | 19 | 43 | 101 | 239 | 575 | 1399 | 3441 | 8539 |
| char-2 rank | 6 | 15 | 27 | 58 | 112 | 229 | 453 | 912 | 1818 |
| ratio | 1.33 | 1.27 | 1.59 | 1.74 | 2.13 | 2.51 | 3.09 | 3.77 | 4.70 |

Two readings, and both are useful.

The **negative** reading: the merge is not the collapse and increasingly is
not. The classes grow at ~2.48 per height and the rank at ~2 (asymptotically
`(4/9)·2^H`), so the ratio diverges and the char-2 quotient is doing something
the reach congruence does not see. That closes any hope that the merge
*explains* the collapse.

The **positive** reading, which is the item: the N-key gives a canonical,
combinatorial, a-priori labelling of a state set only 4.7× larger than the
rank at H = 12, and probe 1's negative was measured on raw partition states,
never on these. Redoing probe 1 with N-keys as the labels is exact GF(2)
linear algebra on ≤ 8,539 states — an afternoon — and it asks the one question
the three failed keys could not: is φ describable on a labelling that is
already known to be a congruence?

Alongside it, the recurrence is a construction schema nobody has tried to
realise. `r(H) = 2r(H−1) ± ⌊(H+1)/2⌋` reads as: a doubling map from height
`H−1` to height `H`, plus `O(H)` corrections. If a basis can be built
inductively in that shape it is checkable against the banked ranks at every
H ≤ 12 before it is believed anywhere. That is the first formulation of the
basis question in this tree that names a *construction* rather than an
existence.

Box 3, and the cancellation test is answered: the identity is the char-2 rank
collapse itself, which is measured, not hoped for.

*Sentence that gets shorter:* `results/mathematics.md` §7's "Nobody has a
basis, and without one it is not constructive" — the one open question the
mathematics page states as unqualifiedly open.

**A1.3 — Undertow against the dmirror triangle, and the five stranded
sequences.**

The most externally legible item in this file, and the one most likely to fail
at its first step. It should be attempted as a derivation and abandoned there
if the first step does not go.

`results/related-seqs-n33.md`: A030222, A030234, A030235 and A194596 stand at
n = 33 at **tier T3** — exact computation composed with empirically pinned,
unproven quasi-polynomials — and n = 34 was declined. The binding input is
`D(n)`, the diagonal-mirror count, whose direct route is the λ^(n/2) blocker
of that same file. Fixed polyplets are at n = 41. The companions are eight
terms behind and graded worse.

`results/dmirror-diagonals.md` shows the family has the same diagonal
structure: `d(S, S+k)` is quasi-polynomial in `S`, period 2, degree `k` per
parity class, onset `S ≥ 2k+2`. `P_0..P_4` are pinned on both parities, `P_5`
is exp-fitted with six witnesses, and **level 6 refuses** — which is exactly
the place where Undertow's mechanism, pinning a level from cells *below* the
onset instead of above it, is designed to help.

What has to be true, in order, and each step is a paper-sized derivation
rather than machine time:

1. **A grand form for the dmirror family** — that level `k` carries exactly
   two new constants over the levels below. For the king lattice this is
   proved and Lean-complete (`docs/proofs/grand-form.md`). The dmirror family
   is *not* a row-local lattice animal class, so neither the universal
   diagonal law's proof nor the parametric master's `b = |D|` substitution
   transfers as stated. This is the step that decides the item.
2. **Below-onset defect terms** `D_j` for the family, the analogue of
   Severance W3's. Depth 1 alone buys one level.
3. Only then the pinning, which is arithmetic.

If step 1 goes, the payoff is unusually concrete: four OEIS sequences move off
a fitted grade, `P_6` and above become derivable rather than refused, and the
open conjecture T4 in `results/open-conjectures.md` — now reduced to a
statement about leading coefficients of `P^even_k − P^odd_k` — sits in the same
family and may fall out of the same frame.

If step 1 does not go, it dies in a paragraph about why a symmetry-restricted
family is not row-local, which is worth writing down either way.

*Sentence that gets shorter:* `results/related-seqs-n33.md`'s tier-T3 banner,
and the README's parenthetical that the higher-level constants are "fitted and
holdout-validated".

**A1.4 — Square Undertow at depth ≥ 2.**

Left over from Last Orders A1.4, which closed the principle at J = 1 and said
so. `results/undertow-square-validation.md` is the only check in the whole
construction that crosses out of the project, and it currently has one depth.
Deriving square `D_2` through the now lattice-parametric ledger
(`results/skeletonkey-parametric-master.md`) takes the external check from one
height of saving to two, and is the prerequisite for the n = 56 depth that
`docs/lastditch-ideas.md` §1b wanted. A derivation, not machine time.

*Sentence that gets shorter:* `results/mathematics.md` §4's "at every level
tested" gets a bigger set of levels, and `confidence.md`'s residual-risk
paragraph gets a second independent lattice under it.

**A1.5 — The confluent exponent and amplitude ratios, king against square.**

Free, and it is the strongest remaining universality test available on banked
data. `results/theta-universality.md` compared the leading exponents —
θ_king = −0.9997 against θ_square = −0.9995 at matched length — with one
script, one spectrum of 42 approximants and the same 40 terms on each side,
and the same code reproduces the published square λ to six digits.

Leading exponents are the weakest thing universality predicts. The
*correction-to-scaling* exponent Δ₁ and the dimensionless amplitude
combinations are the sharper test, and `results/series-analysis-da.md` already
fits a confluent term on the king side (Δ₁ = 1/2, and adding the confluent
term moved θ to −1.02). Running the same confluent fit on the square series at
matched length and comparing Δ₁ is one script on data already on disk, with
the same external anchor underneath it.

Honest limit stated first: Δ₁ is much harder to resolve than θ from 40 terms,
and the answer may well be "both fits are too loose to distinguish", which is
a result the file should be allowed to report.

*Sentence that gets shorter:* the θ paragraph in `results/mathematics.md` §5,
which currently rests the universality claim on one exponent.

### A2. Variations on things known not to work

Each names the counterexample or the blocker it has to beat. None is a
re-pitch of the closed door itself.

**A2.1 — Sampling without mixing: sequential importance sampling.**

Last Orders C3.2 scoped the sampler and left it open on purpose. Its blocker
is stated precisely there: a Markov chain over n-cell animals needs
irreducibility *at the n being sampled* and a bound on its **mixing time**, and
mixing is the whole programme rather than an afternoon.

The variation is to not use a Markov chain. Rosenbluth-style sequential
importance sampling — grow an animal cell by cell, carry the weight, and prune
and enrich (PERM) to control variance — produces unbiased estimates of `a(n)`
by construction and has no mixing time to bound, because it is not a chain on
the state space at all. That is the specific blocker it beats and it should be
stated that way or the item is just C3.2 again.

Grepping the tree for `Rosenbluth`, `PERM`, `importance sampl` returns nothing
in `results/`. `sampling/` holds one script and it is `maxhole_split.py`.

What it buys, and this is why it is worth more than a curiosity here: it is the
only channel available that could **falsify** a tower-derived term. A second
tower route agreeing with the first checks the pinning cells and never the
shared machinery — Lane B established that, and it is why Motley `C_19` was the
buy for `T(40,19)`. A statistical estimate of `a(42)`..`a(45)` with a
calibrated error bar comes from an entirely different family of assumption. It
can never confirm a digit; it can say a digit is wrong.

Controls the project's own practice would demand, before any new number is
quoted: calibrate on n ≤ 41, where every answer is known exactly, and report
the measured bias and spread there; and check the prior art first, starting
with the Janse van Rensburg–Madras entry in `papers/MISSING.md`, since animals
under Rosenbluth sampling is not a new idea and its failure modes are likely
already documented.

*Sentence that gets shorter:* none today, and one later — `confidence.md`
currently has no way to say anything at all about a term past the frontier.

**A2.2 — The strip finite-size fit, third pass, and why it is now A1.1's
dependent.**

Idea 6.1 was struck, then the strike's reasoning was itself corrected on
2026-08-22: `results/strip-fss-lambda-sensitivity.md` finds the obstruction is
that the correction series has not converged at H ≤ 17, **not** that a
logarithmic term is required. That correction changes what the variation is.
It is no longer "fit the three-parameter form the data implies"; it is "how
many more heights would it take", which is a question about the strip
certificate ladder's reach.

Which makes it downstream of A1.1: the same frontier collapse that prices the
sweep prices the certificates. If the census says the merged frontier makes
H = 18 and H = 19 certificates affordable, the fit becomes a live question
again; if it does not, the item stays closed and the reason is quantified
rather than assumed.

*Sentence that gets shorter:* none unless the fit succeeds, in which case the
central-charge paragraph that does not exist gets written.

**A2.3 — The λ atlas, certified rather than estimated.**

`results/lambda-atlas-probe.md` delivered idea 4's headline question — λ is
not a function of coordination number; two q = 8 lattices differ by 26% —
and explicitly did not deliver the atlas. What remains is a compute item with a
measured motivation: make `cpp/strip_mu_cert.cpp` lattice-parametric, then run
it per lattice per height. `results/strip-growth-lambda-bounds.md` measures
H = 18 on king at tens of minutes and tens of GB; a spread-8 strip reaches two
rows and has a different, probably larger frontier.

**Checked today, and it was flagged as unchecked:** the spread-8 counts
`1, 4, 24, 164, 1200, 9126, 71296, 567706` return **no results** from OEIS.
Nine terms of a sequence nobody has entered.

Certified two-sided brackets for more than one or two lattices do not appear
to exist anywhere, and producing several would make two of this project's
universal theorems non-vacuous by exhibiting instances. It shortens no sentence
in the polyplets papers, and the probe file already says the honest thing: it
is the kind of fact a separate short paper is made of.

### A3. Open, small, and unclaimed

Four items that are cheap, concrete, and have nobody assigned to them.

**A3.1 — The maximum hole count.** `results/king-extremal.md` produced
`0, 0, 0, 1, 1, 2, 2, 3, 4` with no OEIS collision and no conjecture. The
project has run exactly this shape before — measure at small n, guess the
closed form, prove it — and it produced a theorem
(`results/maxhole-proof.md`). Nine terms is thin; the oracle can produce more.
The lattice-dependence is the interesting part: four king cells enclose a hole
where the square lattice needs eight.

**A3.2 — Bilateral A030234 is not log-convex, and it fails at every even n.**
`results/open-conjectures.md` C2 records this as "a parity effect worth its own
look" and nobody has looked. Every other companion is log-convex past small n.
The failure is systematic rather than sporadic, which usually means there is a
two-term structure underneath it. Free, on banked data.

**A3.3 — T4, now reduced.** `N_k(±1) = (±2)^k` for the dmirror numerators is
reduced (2026-07-31) to a statement about leading coefficients:
`N_k(1) = 2^k` ⟺ each parity class has leading coefficient `S^k/k!` (banked),
and `N_k(−1) = (−2)^k` ⟺ `lead(P^even_k − P^odd_k) = (−1)^k/(k−1)!` (verified
exactly for k = 1..5). That is a combinatorial identity about defect density on
two ground-state spines, and it is the most provable-looking open statement in
the tree. Shares a family with A1.3.

**A3.4 — λ's upper bound.** Unchanged and stated so the list is complete:
`docs/open-problem-lambda-bracket.md` is framed as a collaboration target where
the bottleneck is mathematical insight and not compute, and machine effort
spent there without that judgment reproduces the bridge-credit sketch, which
was closed as *unsound*. Not the machine's to run.

### What A changed in B and C

Three things, folded in below and collected here.

1. **B gains the depth-versus-height re-plan.** Working A1.1 against the
   frontier numbers made it obvious that the five-terms plan was costed at
   J = 4 and that depth 5's reprice moves its binding constraint. That is B2,
   and it is arithmetic on banked ladders rather than a new idea.
2. **C gains the superseded depth-5 price.** Six tracked files still carry
   `~16 h / ~103 GB` or `~51 GB / ~23 h` with no marker, against the measured
   `3.1–6.7 h / 8.5–16.1 GB`. Found while pricing A1.1 and B2. That is C1.
3. **A2.3's novelty flag is retired.** The spread-8 sequence was checked
   against OEIS today and is absent, so `results/lambda-atlas-probe.md`'s
   "worth an OEIS check before anyone calls it anything" has been answered and
   the file should say so. Small, and it belongs in C's correction pass rather
   than as an item.

---

## B. Work that could be planned

Mathematical and authorship both. Two items here are jasonp's judgment and are
marked as such rather than left implicit.

### B1. The gate-class sweep. This is the highest-value item in the file.

`docs/last-orders.md` closes by naming it and not doing it, which is the right
place for it to have ended up and the wrong place for it to stay.

The failure that prompted it: `make gate-provenance` stayed green while the
front-door provenance table went a height stale, because the gate compares the
published note against its generator and a hand-edited constant makes both
stale together. That particular constant is now derived from the banked row
directories. **The pattern is not swept.**

The sweep is one question asked of each of the 33 members of `GATE_TARGETS`:
does this gate touch ground truth, or does it compare two artifacts that a
single stale input makes wrong together? Red-first, per the standing rule — for
each gate, plant the staleness the gate is supposed to catch and confirm it
goes red. A gate that stays green under its own planted failure is the finding.

This is the last thing between the tree and a reader who trusts the gate suite
because the README tells them to. It is desk work, it is bounded by 33, and it
is the item that should not wait.

*Sentence that gets shorter:* the README's "It is generated, and `make
gate-provenance` fails if any figure in it drifts from the banked rows" — which
is currently a claim about one gate that a reader will read as a claim about
the suite.

### B2. Re-price the five terms at J = 5 and J = 6. Depth is now the cheap lever for the next two terms.

`docs/five-terms-plan.md` was written 2026-08-20 at J = 4 and its conclusion is
that **disk, not time, is what caps this**: the H = 21 pole at Nmax 45
projects to ~580 GB against ~496 GB free, marginal at best after clearing run
directories. Depth 5's reprice on 2026-08-22 changes the trade it is choosing
between, and nobody has redone the arithmetic.

The reach rule is `n ≤ 2·Hs + J − 1`. Costs, with their provenance marked:

| lever | cost | grade |
|---|---|---|
| `Hs = 19` at Nmax 41 | 4.72 h / 40 cores | **measured** (a(41), dalby) |
| `Hs = 20` at Nmax 41 | ~10–11 h / 48 cores, ~185–190 GB | extrapolated from a(40)'s measured H20 phase |
| `Hs = 21` at Nmax 40 | 36.4 h / 32 cores, 363.4 GB disk | **measured** |
| Nmax 40 → 45 at fixed height | ×1.45 cpu at H = 14, 15; ~×1.6 at H = 21 | measured at two heights, extrapolated six |
| `J = 5` | 3.1 h / 8.5 GB, or 6.7 h / 16.1 GB pessimistic | projected from a 5-rung fixed-thread ladder with a K = 16 holdout at ≤ 8% |
| `J = 6` | ~20–60 h, ~50–100 GB | **asserted** — the per-excess ladder's ~6× RSS and ~7–9× wall, applied once to J = 5's projection |

What that buys:

| Hs | J | reaches | the marginal lever, and its disk |
|---|---|---|---|
| 19 | 4 | n ≤ 41 | done |
| 19 | 5 | n ≤ 42 | depth 5 — ≤ 16 GB |
| 19 | 6 | n ≤ 43 | depth 6 — ~50–100 GB, asserted |
| 20 | 5 | n ≤ 44 | + the H = 20 pole, ~190 GB at Nmax 41 |
| 20 | 6 | n ≤ 45 | as above |
| 21 | 4 | n ≤ 45 | + the H = 21 pole, ~580 GB at Nmax 45 — does not fit |

**The observation, stated carefully.** `docs/skeletonkey-reprompt.md`'s two
cost laws say height is the right lever by a factor of four to five in the
exponent — 1.70× per unit of n against depth's 7–9×. That is a statement about
slopes and it is not wrong. But the next two rungs of the height ladder are the
two most expensive computations this project has ever run, and the next rung of
the depth ladder is an afternoon, so in absolute terms depth is cheaper for
n = 42 and n = 43 and the crossover sits around J = 6 against H = 21. The
five-terms plan reaches n ≤ 45 by paying the H = 21 pole's disk; `Hs = 20`
with `J = 6` reaches the same n against the H = 20 pole instead, which is the
constraint the plan itself identifies as binding.

**Three things this does not say.** Depth 6 is asserted and one rung of a
ladder would settle it, the same way K = 14 and K = 16 settled depth 5. Every
row needs the sweep re-run at the target Nmax, not just the last lever. And
review row B13 stands: `experiments/severance_w3_depth5_gate.py` must pass
against the banked depth-5 cells at k ≤ 19 before `D_5` is used at k = 21, and
that gate is correctly RED in production until the `emax = 4` table exists.
[**Closed 2026-08-24** — the table landed and the gate is green;
`results/depth5-gate-green.md`.]

**Whether any of it runs is jasonp's call.** This item is the arithmetic, not
the request.

### B3. Where the Undertow chapter goes.

`docs/undertow-chapter.md` is written as source material — the claim, why it is
not circular, what it bought with the measurements, the external validation,
what is still soft. The decision is untouched and is jasonp's: tenth L paper,
a section of P1, or his own prose. Nine L papers exist and the result that
most changed what this project can compute is in none of them.

Second half of the same decision, unchanged: `paper/L8-below-onset.tex` was
drafted 08-18 and its own material moved on 08-20. A paper whose subject
advanced after it was drafted should absorb that or say so.

### B4. The L papers' currency, one decision across nine.

`docs/l-paper-currency.md` is the inventory: four of the nine are unaffected,
five have something to absorb, and only L8's is substantial. Three options —
absorb, footnote, leave — and the point of the inventory is that the decision
is cheaper made once than nine times.

### B5. Lean: the below-onset frame.

The Lean development covers the diagonal law's shape as a theorem
(`Shape.lean`), the grand form against standard axioms, and the production
`P_k` for k ≤ 18 grand-pinned from two real-swept cells per level. What has no
Lean coverage is the statement a(41) actually rests on: that a cell *below* the
onset, corrected by `D_j(k)`, is a valid linear equation for the same level.

The scope has to be split honestly before anything is attempted. What looks
formalizable is the **frame** — given `D_j`, that the below-onset identity
holds and that two such equations pin a level, which is grand-form-shaped and
sits next to work already done. What is not is the *values* of `D_j`, which
come from the family DP and are certificates rather than theorems.

That split is the item: write it down, decide whether the frame is worth the
Lean hours, and if it is not, say in `PROOF-STATUS.md` that the newest result
is the one the formalization does not reach.

### B6. P1, P2, P3 — his, and unchanged.

`paper/technical-report.tex` is ~40% built and read-only to the machine;
`docs/main-paper-audit-2026-08-18.md` holds findings on it that are unapplied
by design; the current strategy's Track D says the repo is the publication and
P1 comes later. P2 and P3 are not started and are his prose under the
authorship split, with P3 additionally behind the `hv-growth-sandwich` reading
gate. What the machine can do is assemble source material, which is what
`docs/paper1-engine-chapter.md` and `docs/paper1-reproducibility.md` already
are.

### B7. Two candidate sequences with nowhere to go yet.

Stated so they are not lost, not as a submission plan. The spread-8 counts
(A2.3, absent from OEIS as of today) and the maximum hole count (A3.1, nine
terms, no closed form) are both new sequences produced by this project that no
current paper carries and no submission wave covers. Each needs a home or an
explicit decision to leave it in `results/`.

### What B changed in C

One thing. **B2 puts a second superseded price into C1's scope.**
`results/lastditch-cost-ladders.md` §3 projects depth 5 at "~51 GB, ~23 h at
16 threads" from a two-point slope, and its own K = 14 rung (705.92 s,
2.69 GB) agrees closely with the newer ladder's K = 14 at 8 threads (731.86 s,
2459 MB) — so the two ladders do not disagree about any measurement, only
about the extrapolation, and the newer one carries a holdout. That is worth
saying in the file rather than silently deleting a number, because the file's
own methodology note is the reason the newer ladder was run at fixed threads
at all.

---

## C. What could be removed, or corrected, before publication

The rule from the standing practice: **never cut evidence and never cut a
closed door.** Nothing below is a result, a provenance record, a kill with its
counterexample, or a measurement. Two of the five items are corrections rather
than deletions and say so.

**C1 — The superseded depth-5 price, in six tracked files.**

Measured on 2026-08-22: `families 21 4` costs **3.1 h / 8.5 GB** at 8 threads,
or 6.7 h / 16.1 GB on the pessimistic bound (`results/depth5-cost-settled.md`).
`docs/lastditch-ideas.md` carries the correction in place. These do not:

| file | line | carries |
|---|---|---|
| `HANDOFF.md` | 184 | ~16 h / ~103 GB |
| `docs/five-terms-plan.md` | 88, 142 | ~16 h / ~103 GB |
| `docs/lastditch-campaign.md` | 108, 142 | ~51 GB, ~23 h |
| `results/a41/PROVENANCE.md` | 105 | ~16 h / ~103 GB |
| `results/undertow.md` | 132 | ~16 h and 103 GB |
| `results/lastditch-cost-ladders.md` | 70, 82 | ~51 GB, ~23 h |

This is the failure class `docs/project-postmortem.md` names — asserted prices
propagate — recurring on the very figure the project most recently corrected.
The fix is a marker next to each, not a deletion; the old numbers are what the
files said and the correction is the interesting part. `lastditch-cost-ladders`
gets the treatment B2 describes, since its measurements are fine and only its
extrapolation is superseded.

*What gets shorter:* nothing. What gets **right** is the price a reader takes
away from six of the seven places that quote it.

**C2 — `results/perimdefect_square*_k5.txt`: 670 KB of strictly redundant data.**

Five files, verified today as **exact subsets** of the `k6` files that
superseded them — every one of the 45,648 lines across them appears in
`perimdefect_square4_n78_k6.txt` or `perimdefect_square8_n78_k6.txt`, zero
lines missing:

| file | lines | in k6 |
|---|---|---|
| `perimdefect_square4_n70_k5.txt` | 16,460 | all |
| `perimdefect_square4_n40_k5.txt` | 5,195 | all |
| `perimdefect_square8_n70_k5.txt` | 11,631 | all |
| `perimdefect_square8_n60_k5.txt` | 8,552 | all |
| `perimdefect_square8_n40_k5.txt` | 3,810 | all |

None is named by any tracked file. Their `.log` siblings are the run records
for real runs and are evidence: keep those, and note the removal in
`results/removals-2026-08-22.md` the way B2 and B3 of Last Orders were noted,
so a `.log` that points at a removed `.txt` still explains itself.

**C3 — `results/make_*.log`: 16 build logs, 324 KB, cited by nothing.**

Written by `scripts/run_full_make.sh`, which is the only tracked file that
names them. They are gate-suite console output from 2026-08-07, a tree several
hundred commits ago, and no document reads a line of any of them. The practice
that produces them stays; the artifacts of one day's runs do not have to ship.
If a build log is wanted as evidence, the one that ships should be the one
taken at R.

**C4 — The Ghost Ship sandbox's twelve byte-identical duplicates.**

Measured today across the 278 tracked files under
`results/ghostship/grading/run-record/sandbox/`: **257 are the experiment's own
output** and exist nowhere else, **9 differ from the live files they shadow**,
and **12 are byte-identical copies of live files**.

The nine are the hazard and are already handled — `SNAPSHOT-WARNING.md` marks
them and they stay, because the sandbox is a mechanically derived slice at
`74b2c20` and is evidence. The twelve are pure duplication: a `git grep` for a
proof statement returns two hits and one of them is a copy. Removing them
changes no evidence and no conclusion, and the snapshot warning already
documents that the slice is partial.

Explicitly **not** in scope here: whether `results/ghostship/` goes public at
all. That is a `PRE-LANDING.md` section-A decision and is not re-litigated.

**C5 — Three small corrections that are not removals.**

- `results/lambda-atlas-probe.md` says the spread-8 sequence is "worth an OEIS
  check before anyone calls it anything". The check was run today and returned
  no results; the file should say so, since the sentence currently reads as an
  open question.
- `paper/README.md` was recorded as stale on the paper count by
  `docs/publication-strategy-2026-08-18.md`. It now lists all nine including
  L7, L8 and L9 — verified today — so the strategy doc's remark is what is
  stale, and it is the one that should be marked.
- `results/dalby-perf-audit.png` (290 KB) is named by no tracked file, not
  even `results/dalby-perf-audit.md`, which is what cites the audit.
  Either the figure belongs in the note that shares its name or it is an
  orphan; a reader cannot tell which, and neither can a grep.

**C6 — What is deliberately not here, and why.**

- `experiments/tristruct/` (143 tracked files) and
  `results/dalby-run-telemetry-202606/` (217 files). Both were left in Last
  Orders as B6 and B5 on the same reasoning and it has not changed: they are
  cited, and thinning them is a judgment about how much working apparatus
  ships, which is the same class of decision as "does `docs/` go public".
- `results/offside/` (six review-lane files, ~136 KB). Review records are
  evidence under the standing rule.
- Empty `.err` files under `results/ghostship/grading/run-record/logs/`. A
  clean stderr is a finding.
- Everything in `PRE-LANDING.md` — the front-door README's a(41) gap, the Lean
  file count, machine paths, the branches, the history.

---

## Where this leaves things

Nothing in A is a prerequisite for publishing. B1 is the one item that is
about the repository being *trustworthy* rather than about it being *larger*,
and it is desk work bounded by 33 gates. C is four hours of tidying and two
corrections.

The three items that would most change what the repository says, in order of
how much they change it:

1. **B1**, because a gate suite that a reader is told to trust should have been
   asked whether it can fail.
2. **A1.1's census**, because it converts the last soft spot in `confidence.md`
   from an unpriced run into a priced one.
3. **A1.2**, because it is the first formulation of the mission's largest open
   question that names a construction to test rather than a hope.

Everything else is optional in the strict sense: the repository can land
without any of it.
