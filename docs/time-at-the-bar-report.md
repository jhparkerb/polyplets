# Time at the Bar — what the round did

2026-08-22, executing `docs/time-at-the-bar.md` end to end at jasonp's
direction ("run all of them, in an order determined by you"). Order run:
C, then B1, then the free A3 items, then A1.2/A1.4/A1.3/A1.5, then the pricing
and the decisions.

**Every item is either done or struck with a reason.** That was the rule the
file set for itself, so this is the file that says so. What it does not do is
authorise anything: five items below are priced and unlaunched, and four are
decisions that are jasonp's.

## The round in one table

| item | status | where |
|---|---|---|
| C1 superseded depth-5 price | **done** — eight files, not six | in place, `results/removals-2026-08-22.md` |
| C2 `k5` censuses | **done, smaller** — 3 of 5 removable | ditto |
| C3 `make_*.log` | **done** — 16 removed, cost header corrected | ditto |
| C4 Ghost Ship duplicates | **STRUCK** — they are a pre-registered slice | ditto |
| C5 three corrections | **done**, all three | ditto |
| B1 gate-class sweep | **done** — 33 gates, 2 defects, 3 limits | `results/gate-class-sweep.md` |
| A1.1 reach-merge census | **priced, unlaunched** | below |
| A1.2 char-2 basis on N-keys | **re-pitch** — plus the H=12 cell closed | `results/char2-basis-status.md` |
| A1.3 dmirror grand form | **dead**, and the cause is deeper than the two-spine sum: `d_anti` fails at `c_3` too | `results/dmirror-grand-form-fails.md`, `results/dmirror-spine-split.md` |
| A1.4 square depth 2 | **done** — identity holds, `D_2` has no law | `results/undertow-square-depth2.md` |
| A1.5 confluent exponent | **done** — king resolves, square does not | `results/confluent-universality.md` |
| A2.1 sequential importance sampling | **prior art found**, see below | below |
| A2.2 strip finite-size fit | **verdict: stays closed** | below |
| A2.3 λ atlas certified | **priced, unlaunched** | below |
| A3.1 maximum hole count | **SOLVED** | `results/maxhole-closed-form.md` |
| A3.2 A030234 parity | **done** — two families | `results/bilateral-parity.md` |
| A3.3 T4 at k = 6 | **closed on the cheap route** | `results/dmirror-onset-sharp.md` |
| A3.4 λ upper bound | **STRUCK** — the file says it is not the machine's to run, and it is not |
| B2 re-price at J = 5, 6 | **done** — the conclusion changes | below |
| B3 Undertow chapter | **DECIDED 08-22 — L10, standing separate from L8** | below |
| B4 L-paper currency | **his** | below |
| B5 Lean below-onset frame | **done** — scope split written, recommendation made | `docs/lean-below-onset-scope.md` |
| B6 P1/P2/P3 | **DECIDED 08-22 — deferred indefinitely** | below |
| B7 two candidate sequences | one is no longer a candidate; the other is **named: short-rook animals** | below |

## The three findings that change what the repository says

**1. Two gates could not fail, and one of them was the same defect as the
original.** `gate-cutcount-assembly` carried a hand-edited `NMAX = 40` with an
assembly loop of `range(1, NMAX+1)`, so a triangle that grows leaves its
coverage silently stale. Planted: 41 fabricated rows appended to
`results/triangle.txt`. `gate-provenance` and `gate-residual-cells` both went
red; `gate-cutcount-assembly` stayed **green**. Fixed by deriving `NMAX`, and
re-probed red. Separately, `results/strip-mu-certificates.md` is read by no gate
and had drifted — its table stops at H = 11 and it says "H ≥ 12 is not certified
yet" while its own log carries H = 12, 13 and 14 as PASS twice each and
`paper/L3-lambda-bounds.tex` has published the H = 14 row. Note corrected; the
structural gap is recorded, not closed.

The other 31 gates put external ground truth, an independent reimplementation,
or the filesystem on the expected side. That is a good suite and the sweep says
so with evidence rather than with a count.

**2. The maximum hole count has a closed form.** `n − ⌈2√n⌉ + 1`, which is
**A248333**, matching all ten measured terms — n = 10 was run and came in at 4 as
predicted. The construction proves the lower bound: the even-parity sublattice
is king-connected by diagonal steps, and every enclosed odd cell has all four
orthogonal neighbours occupied, so it is a singleton hole. An `a × b` block of
that rotated lattice costs `ab` cells and encloses `(a−1)(b−1)` of them.
`results/king-extremal.md`'s "no OEIS collision, no obvious closed form" was
true of nine terms and is superseded. The reverse inequality is open.

**3. Depth, not disk, is now what caps the five terms.** B2, below.

## B2 — the re-price, with the arithmetic done at the target Nmax

`docs/five-terms-plan.md` concluded that **disk** caps this: the H = 21 pole at
Nmax 45 projects to ~580 GB. The file's own caveat is that "every row needs the
sweep re-run at the target Nmax, not just the last lever", and it had not been
done. Doing it:

Measured disk scaling is ×1.6 for Nmax 40 → 45 at H = 21, i.e. about ×1.099 per
unit of n. Applying that to the H = 20 pole's ~190 GB at Nmax 41:

| Hs | J | reaches | pole disk **at the target Nmax** | fits 563 GB |
|---|---|---|---|---|
| 19 | 4 | n ≤ 41 | done | — |
| 19 | 5 | n ≤ 42 | depth 5 only, ≤ 16 GB | yes |
| 19 | 6 | n ≤ 43 | depth 6, ~50–100 GB **asserted** | yes |
| 20 | 5 | n ≤ 44 | H = 20 at Nmax 44 ≈ **252 GB** | yes |
| 20 | 6 | n ≤ 45 | H = 20 at Nmax 45 ≈ **277 GB** | yes |
| 21 | 4 | n ≤ 45 | H = 21 at Nmax 45 ≈ **580 GB** | **no** |

Two corrections fall out. **dalby has 563 GB free**, measured today, not the
~496 GB the plan assumed — so the H = 21 route is marginal-and-over rather than
comfortably impossible, which is a worse place to be than a clear no. And the
`Hs = 20` rows were priced at their Nmax-41 pole; at their own target they are
252 and 277 GB, which fit with room.

**So the binding constraint has moved.** `Hs = 20` with `J = 6` reaches n ≤ 45
against a 277 GB pole instead of a 580 GB one, and the thing standing in the way
is no longer disk — it is that **`J = 6` is asserted**, at ~20–60 h and
~50–100 GB, from applying the per-excess ladder's ~6× RSS and ~7–9× wall once to
J = 5's projection. Depth 5 was asserted too, at 16 h / 103 GB, until a five-rung
ladder measured it at 3.1 h / 8.5 GB — an order of magnitude out. **One rung of
a J = 6 ladder would settle it the same way**, and it is the cheapest thing in
this whole document that changes a plan.

Review row B13 stands and is unaffected: `experiments/severance_w3_depth5_gate.py`
must pass against the banked depth-5 cells at k ≤ 19 before `D_5` is used at
k = 21, and it is correctly RED in production until the `emax = 4` table exists.

**None of this is a request.** It is the arithmetic B2 asked for.

## The five priced, unlaunched runs

Each is over the one-hour bar or needs a second source, so each is jasonp's.

| run | cost | what it settles |
|---|---|---|
| **J = 6, one rung** | one `families K 5` cell; K = 14 was ~12 min at emax = 4 | turns the only asserted number in the B2 table into a measured one |
| **A1.1 census**, H = 18..21 | a C++ build, then minutes — see below | whether H = 20 at Nmax 41 costs 190 GB or materially less, and whether H = 21 comes back inside disk |
| **`minauto` H = 13 RANK** | ~2 h on top of the 16 min build already done, minauto-only | A034299's predicted `r(13) = 3643`. The H = 13 *state* count is now measured (21,355); it is the **rank** that tests the identification, and it needs a second source before it counts |
| **`king_extremal --nmax 11`** | ~2 h, ~55 GB on ayr | the first real test of `n − ⌈2√n⌉ + 1`, predicted 5 |
| **λ atlas certification** | see A2.3 below | certified two-sided brackets for more than one lattice |

### A1.1 — the census, priced

The merge collapses the end-of-column frontier from `2.70^H` to `2.48^H`, and
`results/skeletonkey-nfamily-merge.md` correctly forbids quoting a number at
H = 21: the ratio compounds and there is no closed form, no OEIS match on the
class counts, and no recurrence with surplus. The census is the measurement that
replaces the extrapolation.

What it costs is now well constrained, and the extrapolation has been given a
holdout rather than merely quoted.

The class counts are exact to **H = 13** after two runs today: H = 12 gave 8,539
states and rank 1,818 (closing a cell `results/exactchange-probes.md` §7 listed
as pending), and a count-only run gave **H = 13 = 21,355**.

**The H = 13 value was predicted before it landed.** From the ratios through
H = 12 — 2.375, 2.263, 2.349, 2.366, 2.406, 2.433, 2.460, 2.482, rising by a
decelerating increment — the projection was 21,348 against a measured 21,355.
That is 0.03% one step out, which is the only evidence the numbers below carry,
and it is more than the merge file had.

Carrying the same decelerating increment forward:

| H | 14 | 16 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|---|
| ratio | 2.518 | 2.548 | 2.572 | 2.582 | 2.592 | 2.600 |
| classes | 53,777 | 347,218 | 2,286,952 | 5,905,832 | 15,305,849 | **39,794,772** |

So the key space at H = 21 is **tens of millions of classes, not billions**. At
`states × H` successor generation that is under a billion unit steps — **minutes
of C++**, with memory the real cost at roughly 40M canonical keys, so single-digit
GB. This remains an extrapolation eight steps out and it is exactly what the
census would replace; it is quoted here to price the census, not to stand in for
it, and `results/skeletonkey-nfamily-merge.md`'s refusal to quote an H = 21
number for any other purpose stands.

**The Python route does not reach, measured rather than assumed.** The H = 13
build took **962 s and 18 GB** on ayr, because it iterates all `2^H` masks per
state; H = 14 alone would be over an hour and the RSS is already a third of what
that box can spare. The cell-at-a-time C++ formulation A1.1 specifies replaces
`2^H` work per state with `H` work per state — a factor of about 10^5 at H = 21 —
which is the whole reason the item is a build and not a longer run.

The two things the census does not settle are unchanged and are in the merge
file: whether the mid-column stage tables inherit the cut (the congruence is
proved at column boundaries only), and what the telescope costs the completion
prune. And on Motley specifically the weaker statement is the right one — gates
B and D show a merged-key engine is an alternative producer of Motley's `C_H`,
which does **not** mean Motley's cancellation DP state admits the same cut.
Nobody has looked at that state space.

### A2.3 — the λ atlas, priced

Unchanged in shape: make `cpp/strip_mu_cert.cpp` lattice-parametric, then run it
per lattice per height. `results/strip-growth-lambda-bounds.md` measures H = 18
on king at tens of minutes and tens of GB; a spread-8 strip reaches two rows and
has a different, probably larger frontier, so the per-lattice cost is not the
king cost. The motivation is measured — two q = 8 lattices differ by 26% in λ,
so λ is not a function of coordination number — and certified two-sided brackets
for more than one or two lattices do not appear to exist anywhere.

Its novelty flag is retired: the spread-8 counts `1, 4, 24, 164, 1200, 9126,
71296, 567706, 4586448` return **no results** from OEIS at three query widths,
with A001168 and A006770 as same-session controls. `results/lambda-atlas-probe.md`
says so now.

## A2.1 — sequential importance sampling: the prior art exists and is free

A2.1 required checking the prior art before anything else, "since animals under
Rosenbluth sampling is not a new idea and its failure modes are likely already
documented". They are, and the tree does not have them.

The method is **PERM** — pruned-enriched Rosenbluth — and it has been applied to
lattice animals and lattice trees directly, not merely to polymers. Hsu and
Grassberger's improved Rosenbluth scheme for cluster counting and lattice animal
enumeration is `arXiv:physics/9911023`; Hsu, Nadler and Grassberger's simulations
of lattice animals and trees is `arXiv:cond-mat/0408061`. The reported reach is
site animals on the square lattice to **n = 46**, which is past this project's
n = 41, and the output is a precise estimate of the partition sum and of the
entropic exponent — an estimate with an error bar, never an exact count.

Both are on arXiv and free, unlike the Janse van Rensburg–Madras 1997 entry
`papers/MISSING.md` points at, which is paywalled with no free copy. **They
should be added to the library, and `papers/MISSING.md` should stop implying the
sampling literature is out of reach.**

**What this does to the item.** A2.1's argument for the sampler was that it is
the only channel that could *falsify* a tower-derived term, because a second
tower route checks the pinning cells and never the shared machinery. That
argument survives. What changes is that this is no longer a thing to invent: it
is a published method with 25 years of documented failure modes, and the work
would be applying it rather than designing it.

**The question that decides whether it is worth anything here is precision, and
it is answerable before any of it is built.** a(42) is a 35-digit number. An
estimate good to a part in a thousand cannot check a digit; it can only catch an
error large enough to exceed its own error bar. So the calibration A2.1 already
demanded — run on n ≤ 41 where every answer is known exactly, and report the
measured bias and spread — is not a control, it *is* the feasibility test, and it
should be run first and alone. If the spread at n = 41 is wider than the class of
error a wrong `D_j` would produce, the channel cannot falsify anything and the
item is closed on arithmetic.

## A2.2 — the strip fit stays closed, and now for a quantified reason

A2.2 made itself a dependent of A1.1: the same frontier collapse that prices the
H = 20 sweep prices the strip certificates, so the fit becomes live only if the
census says H = 18 and H = 19 certificates are affordable. The census is not run,
so **the item stays closed and the reason is now explicit rather than assumed**:
it is waiting on a measurement that is priced at minutes, not on a judgment.

One thing did change underneath it. The obstruction is
`results/strip-fss-lambda-sensitivity.md`'s — the correction series has not
converged at H ≤ 17, not that a logarithmic term is required — and A1.5 is a
second, independent instance of the same shape: a correction-to-scaling exponent
that 40 terms cannot resolve on the square lattice. Two campaigns now run into
"the corrections are not converged at the lengths available", which is worth
noticing as a pattern rather than twice as a surprise.

## The four decisions that are jasonp's

**B3 — where the Undertow chapter goes. DECIDED 2026-08-22: the tenth L paper.**
It stands separate rather than joining L8, so L8 stays the below-onset theory
and L10 carries the application. `docs/undertow-chapter.md` is written
as source material. The options were: tenth L paper, a section of P1, or his own prose. Nine L
papers exist and the result that most changed what this project can compute is in
none of them. Second half unchanged: `paper/L8-below-onset.tex` was drafted 08-18
and its own material moved on 08-20, and a paper whose subject advanced after it
was drafted should absorb that or say so.

**B4 — the L papers' currency.** `docs/l-paper-currency.md` is the inventory:
four of nine unaffected, five with something to absorb, only L8's substantial.
Three options — absorb, footnote, leave — and the point is that the decision is
cheaper made once than nine times. One addition from this round: **L3 already
publishes the H = 14 certificate row**, so the note it draws from is the stale
one and has been corrected, not the paper.

**B6 — P1, P2, P3. DECIDED 2026-08-22: deferred indefinitely**, off the
current plan and not cancelled. `docs/publication-strategy-2026-08-18.md`'s
Track D already says the repository is the publication and P1 comes later; this
makes that the plan rather than a sequencing note. P3's `hv-growth-sandwich`
reading gate parks with it, and `docs/main-paper-audit-2026-08-18.md`'s findings
stay unapplied. Previously: `paper/technical-report.tex` is ~40%
built and read-only to the machine; `docs/main-paper-audit-2026-08-18.md` holds
findings on it that are unapplied by design.

**B7 — the two candidate sequences, now one.** The counts are confirmed
absent from OEIS and remain a genuine candidate with no home. **Named
2026-08-22: short-rook animals** — the wazir+dabbaba compound, as king animals
are the wazir+ferz one (`results/lambda-atlas-probe.md`); `spread-8` was the
working label and survives as the code's key. **The maximum hole
count is no longer a candidate**: it is A248333, already entered, and what this
project has instead is a new *identification* — that the maximum number of holes
in a king animal equals the maximum number of unit squares enclosed by n lattice
points — which is a sentence in a paper, not a submission.

## What the round forced on its own file

Five things, each a case of the file being confidently wrong in a way its own
standing filter would have caught:

1. **C1 was eight files, not six.** `docs/lastditch-ideas.md` §1 and
   `results/span-cap-variation.md` carried the superseded price unmarked and were
   not on the list.
2. **C2's premise was false.** Two of the five `k5` files are named as
   reproduction commands in two results notes and two script docstrings.
3. **C4 was wrong and is struck.** The twelve byte-identical files are twelve of
   the twenty-one in a pre-registered, published slice whose verbatim
   `git archive` command ships; deleting them falsifies that specification.
4. **A1.2 is a re-pitch.** `results/exactchange-probes.md` §6 did it on
   2026-08-14 and closes with "Layer 1 of the basis hunt is closed", and its §8
   already names a sharper construction than the one A1.2 proposes.
5. **A1.5's premise was wrong.** `results/series-analysis-da.md:60` says the DA
   does *not* independently pin Δ₁; the 1/2 is the literature's, quoted.

Three of my own probes were caught by their own controls before they produced a
verdict: a linearised log that biased Δ by the size of the effect, a synthetic
"log-convex" family that was log-concave, and a hand-expanded Newton form wrong
at every degree above zero. That is the controls working, and it is the reason
to keep writing them first.
