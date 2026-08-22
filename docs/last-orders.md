# Last Orders — the round before the landing

Written 2026-08-22 against `d9f9317`, at jasonp's direction, from a survey of
the tree rather than from memory.

**The rule this list defines.** When every item below is either done or struck
with a one-line reason, we work `PRE-LANDING.md` together, publish the
repository, and make the OEIS submissions. Nothing from that checklist is
repeated here — the licence, the branches, the history, the ledgers, the
front-door README, the clean-clone run, the gates. Their inclusion is implied.
This file is everything *else* that could sensibly happen first.

**What this file is not.** It is not a plan and it does not authorise anything.
Every item carries what it costs where that is measured, an honest "asserted"
where it is not, and the standing filter — *name the sentence that gets
shorter*. Items that shorten no sentence say so.

**STATUS 2026-08-22 — section C is complete.** Every C item is closed: eight
were executed and are banked in `results/`, three were scoped and deliberately
not run, and the reasons are per-item below. C returned four things that change
A or B, folded in where they belong and listed together in "What C changed" at
the end of this file.

Three sections, and they are not equally urgent. **B is the only one that
compounds**: every day the tree carries a stale duplicate is a day a reader
might cite it. A and C are both optional in the strict sense — the repository
can land without any of them.

---

## A. Work that could be planned

### A1. Mathematics and compute

**A1.1 — The H = 20 sweep at Nmax 41. The last soft spot, and the price is
disputed inside the repo.**

`scripts/dalby_a41_h20.sh` exists and its header carries a *corrected* price:
~10–11 h on 48 cores and ~185–190 GB, extrapolated from a(40)'s measured
H20-solo phase (9.6 h / 48 cores / 172 GB peak) through the measured Nmax
scaling. Three places still carry the superseded figure of ~20–30 h and
~450 GB: `docs/five-terms-plan.md`, `results/a41/PROVENANCE.md`, and the
*same script's* own disk-fit paragraph, which computes the phase profile at
450 GB two lines above the correction that rejects it. Whatever gets run,
the 2–3× disagreement should be resolved in the tree first; it is desk work.

What it buys, and this is the strongest single mathematical item on the list:
a swept `T(41,20)` is a genuine **holdout** for `P_21`, which today is pinned
from one pair with nothing checking it, and a(41) stops depending on `P_21`
at all. `results/confidence.md` names this as the last soft spot in the whole
construction.

*Sentence that gets shorter:* confidence.md's "the formula governing it is
fixed by exactly two data points with nothing left over to check it against".

**A1.2 — Depth 5, and the gate before it.**
`experiments/severance_w3_depth5_gate.py` is written red-first. The cost is
**contested and should be treated as unpriced**: `docs/lastditch-ideas.md` §2
says ~16 h / ~103 GB from a geometric mean, and `results/undertow-review-queue.md`
row L-2 shows the per-K ratio is *decelerating* (4.18× per +2K from K=8→10,
2.68× from K=10→12), putting the honest range at ~110–390 GB against dalby's
125. Two staging points, K = 14 (~15 min) and K = 16 (~50 min), settle it.
Row B13 requires the depth-5 gate to pass against banked cells at k ≤ 19
before `D_5` is used at k = 21, and that check is free.

**A1.3 — The five-terms sweep.** `docs/five-terms-plan.md`, not launched,
jasonp's call. Its own honest recommendation is Nmax 43 — three new terms
inside the disk budget — with 44/45 only after `runs/a41_low` is cleared and
behind a disk guard. Row 45 rests on a level with one pin pair and no holdout,
and the plan says to report it that way or hold it. Its two-data-point
extrapolation of the Nmax exponent out six heights is flagged as weak by the
plan itself.

**A1.4 — Square-lattice validation against a published series. DONE at J = 1**
— `results/undertow-square-validation.md`, 2026-08-22. Undertow's core claim
holds at every level k = 1..6 on a lattice whose counts are published: the
below-onset fit equals the classical one as a polynomial and reproduces the
tallest cell it was denied, with a RED control confirming the wrong defect sign
breaks it. **What is left of this item** is depth, not principle: only square
`D_1` is derived, so the saving is one height rather than the king's two or
three, and the n = 56 headline still needs square below-onset cells at H ≤ 28
against a triangle that stops at n = 21. Deriving square `D_2` via the now
lattice-parametric ledger is the next step and is a derivation, not machine
time.

*Original framing, for the record:*

`docs/lastditch-ideas.md` §1b: run the Undertow pin on a lattice where the
answers are other people's. The blocker was that Severance's ledger was
king-only; `results/skeletonkey-parametric-master.md` removed it — the
substitution is `b = |D|` for the 3 in the renewal chain, and the k = 4 leg
now agrees with the wired king table by two routes that share no code. Square
polyominoes are published to n = 56. The cost is a square-lattice `D_j`
derivation and below-onset square cells at H ≤ 28, not frontier machine time.

*Sentence that gets shorter:* every claim in the tree that says the diagonal
tower has never been checked against an external oracle.

**A1.5 — Bank the cell-sparsity measurement. DONE** —
`results/skeletonkey-cell-sparsity.md` and `results/skeletonkey/cellsparse.txt`,
2026-08-22, with the three docs that promised it updated. Char-0 sparsity is
real at 425×, the engine still loses on dimension, and H = 8 did not break the
trend.

*Original framing, for the record:* It ran on ayr, it landed, and
it lives only in `~/var/skeletonkey/cellsparse.txt`. Three tracked files
promise `results/skeletonkey-cell-sparsity.md` (planned, and it is this item)
— `docs/skeletonkey-reprompt.md` twice, `docs/resume-here.md`, and
`docs/README.md` — and
`results/skeletonkey-four-mechanisms.md` §8 uses the H = 8 row only indirectly,
through already-published figures, rather than on its own. A measurement that
exists on one box and nowhere in the repository is the failure mode this
project has a gate suite to prevent. The write-up is small; the data is done.

**A1.6 — Sweep the Undertow review queue.** `results/undertow-review-queue.md`
was last written before the Motley ladder landed on 08-21, so it still carries
OPEN rows the ladder answered: **B6** and **B12** ask for the H = 19 Motley RAM
price, which is now measured at 63.03 GB RSS; **B4** says only agreement
against an enumeration crosses assumption families, which is exactly what the
ladder delivered; **L-3** names Motley C_19 as the buy, and it was bought.
Nine rows are CLOSED and twelve read OPEN, and some of those twelve are not.
An open review queue that is stale in the *reader's* favour is worse than one
that is stale against it.

**A1.8 — Regenerate the provenance table; it is a height stale.** NEW, from
C1.4. `scripts/provenance_table.py` line 58 has `MOTLEY_H = 18` with the
comment "Confetti landed 2026-08-19", but the Nmax-41 ladder landed 08-21 with
H = 1..19 banked in `results/cutcount_b1/rows41/`. Three of the six cells the
table calls congruence-only
<!--q:congruence_only.count@18=6--><!--q:congruence_only.cells@18=(38,19),(39,19),(39,20),(40,19),(40,20),(40,21)-->
— T(38,19), T(39,19), T(40,19) — are at H = 19 and now have a second program; `results/confidence.md` already says a(40) is
complete in all forty cells, so the two documents disagree. `make
gate-provenance` cannot catch it: the gate compares the published note against
the generator, and a stale constant makes both stale together, green. This is a
front-door problem — `README.md` puts that table on page one as the answer to
"why believe a(40)". Advancing the constant, regenerating, and re-reading the
congruence-only set is the work; a gate that pins `MOTLEY_H` to the banked row
directories rather than to a hand-edited constant is the follow-up.

**A1.7 — The reach merge, if it is to be unparked.** `results/skeletonkey-nfamily-merge.md`
is established and banked; parked at jasonp's direction 2026-08-20, and the
cheapest-first ladder is already written down (a C++ key-space census at
H = 18..21, then the congruence written properly, then one call in
`kinkFinalizeColumn`). Listed so the decision is explicit, not so it is taken.

### A2. Authorship

**A2.1 — The missing manuscript, and it is the most consequential gap.**

`paper/L8-below-onset.tex` has the below-onset mathematics: the exact frame,
the depth-1 closed form, depths 2–4, `θ_j = j − 3/2`, the velocity α = 50/81.
Nothing anywhere has the **application** — that those defects let a level be
pinned from cells *below* the onset, which is what took row 40's cost off the
two tall poles and produced a(41) at a fraction of the classical price. Nine L
papers, and the result that most changed what this project can compute is in
none of them. Whether it is an L paper, a section of P1, or jasonp's own is a
decision; that it currently has no home is not.

Same paragraph, second gap: L8 was drafted on 08-18 and its own material moved
on 08-20 (`docs/lastditch-ideas.md` §1a's correction to the equations-versus-
unknowns accounting, and the §5 P-finite kill). A paper whose subject advanced
after it was drafted should say so or absorb it.

**A2.2 — P1.** `paper/technical-report.tex` is ~40% built and read-only to the
machine; `docs/main-paper-audit-2026-08-18.md` holds findings on it that are
unapplied by design. `docs/publication-strategy-2026-08-18.md` Track D says the
repo is the publication and P1 comes later — so this is on the list as a
*choice already made*, not as a blocker. Its two named costs are the engine
chapter and §Reproducibility.

**A2.3 — P2 and P3 are not started**, and under the split they are jasonp's
prose and not the machine's to write. P3 additionally sits behind the
`hv-growth-sandwich` reading gate. What the machine *can* do here is assemble
source material, which is what `docs/paper1-engine-chapter.md` and
`docs/paper1-reproducibility.md` already are for P1.

**A2.4 — The L papers predate a(41).** They were drafted when the frontier was
a(40) and the ladder was closed. Three results postdate all nine: a(41) with a
second source, the parametric master equation (`b = |D|`, so the ledger is no
longer king-only), and the transfer floor's base measured at 2.43 rather than
3 (`results/skeletonkey-hankel-closure.md`, H = 11 killing both extrapolations).
Each needs a decision — absorb, footnote, or leave — and the decision is
cheaper made once across all nine than nine times.

**A2.5 — The finite-type barrier as a result in its own right.**
`docs/open-problem-lambda-bracket.md` states it plainly: slack that *grows*
with n is the signature of a non-local over-count, no finite context R can see
it, and "this whole method class floors strictly above λ" — then adds that this
is "arguably a publishable observation in its own right". `paper/L3-lambda-bounds.tex`
carries the slack audit as a measurement (median 1.144, max 1.222, +0.022 per
cell) and notes that king slack grows where the rook method's saturates, but
does not develop the barrier as the standalone negative the open-problem doc
describes. Turning a measured obstruction into a stated limitation of a method
class is the kind of result that survives having no referee.

**A2.6 — There is no stranger-facing account of anything except a(n).**
`results/confidence.md` does that job, in plain terms, for the sequence values
— and it is the best-written document in the tree. Everything else a visitor
might want to know (what the λ bracket is and why it is wide, what the diagonal
law says, what was tried and failed) is reachable only through `HANDOFF.md`,
which is 111 KB of reverse-chronological campaign log, or through 113 files in
`docs/`. A second `confidence.md`-shaped page for the mathematics is cheap and
would be read.

---

## B. What could be removed

**The rule I applied, from the standing claim-pruning practice: never cut
evidence and never cut a closed door.** Nothing below is a result, a
provenance record, a kill with its counterexample, or a measurement. Empty
`.err` files under `results/ghostship/grading/run-record/logs/` are *evidence*
— a clean stderr is a finding — and they stay. What follows is duplicates,
strays, and one genuine hazard.

**B1 — The one that is actually dangerous: stale forks inside
`results/ghostship/grading/run-record/sandbox/`.**

The sandbox holds a partial copy of the repo as it stood during the experiment.
Eight proof notes under `sandbox/docs/proofs/`:

- **three DIFFER from the live files they shadow** — `convex-mirage.md`,
  `diagonal-law.md`, `polyplet-upper-bound.md`. A reader who greps the tree for
  the diagonal law finds two versions and no marker saying which is live. The
  diagonal law is a *proved theorem* with a Lean artefact behind it; a stale
  fork of it is the worst kind of duplicate to leave in a published tree.
- **five exist nowhere else** — `area-moment-kernel.md`, `area-moments-method.md`,
  `convex-area-q-temperley.md`, `convex-box-kernel.md`, `row-gf-specializations.md`.
  These are not removals at all. They are content that may want recovering
  into `docs/proofs/`, or may be superseded — but somebody has to look, because
  right now the only copy of five proof notes is inside a graded experiment's
  sandbox.

Whatever is decided about whether the Ghost Ship tree goes public — that
decision is in the landing checklist and is not repeated here — this hazard
exists in either direction, because it is a hazard to *us* reading our own
tree.

**B2 — Uncited bulk data.** `results/a19_samples.txt`, 2.5 MB, named by no
tracked file. `results/perimdefect_k7_calib/`, 36 files and 891 KB, named by
no tracked file, from the k = 7 census that was priced at 76–179 days and
declined. Both are outputs nothing reads.

**B3 — `results/dead-2026-08-07-powercut/`.** Three files from the ayr power
cut, one of them empty, cited only by `HANDOFF.md`'s account of the incident.
The *lesson* is banked in `docs/lessons-learned.md` and stays; the three
truncated output files are not evidence of anything except that the run died.

**B4 — Twenty-four empty tracked files.** Fourteen are ghostship's `.err`
files and stay, per the rule above. The other ten are stray: four under
`experiments/tristruct/`, two `.out` files under
`results/dalby-run-telemetry-202606/a21fold/` that are empty where the
sibling `.log` files are not, `results/j7_20260807.log`,
`results/perimmin_free_15_15_0_r7.txt`, and the powercut file from B3.

**B5 — June run telemetry.** `results/dalby-run-telemetry-202606/`, 217 files
and 3.5 MB of run logs, cited by `HANDOFF.md` and
`results/hole-free-growth-constant.md`. Not a straight removal — the a(35) and
holes runs are provenance — but 217 files of console log is a lot of tree for
what two documents actually cite, and a thinning down to what is cited is
available if the tree wants to be smaller.

**B6 — `experiments/tristruct/`**, 170 files and 1.7 MB, of which 78 are named
nowhere outside `experiments/` itself. The campaign's *conclusions* are in
`docs/triangle-postmortem.md` and the `results/triangle-*` files and stay
regardless. This is about how much of the working apparatus ships with them.

**B8 — NEW, from C: nothing. C added files, it did not make any removable.**
Worth stating so the section is not padded. The eight executed items produced
eight `results/*.md`, five probes under `experiments/`, and two data files
(`results/b001168_external.txt`, 72 lines, and
`results/skeletonkey/cellsparse.txt`, 13 lines). All are cited. The one thing C
*changes* about B is B1: five proof notes exist only inside the Ghost Ship
sandbox, and C touched none of them, so that hazard is exactly as it was.

**B7 — Two one-line tidies.** `.gitignore` lists `build/` twice. And the
superseded v1 prompt is kept inline in `docs/skeletonkey-reprompt.md` "for its
rationale" — which is a good reason, but the file is the *entry point* for the
whole Skeleton Key mission per `docs/README.md`, and a reader meets 40 lines of
superseded instruction on the way in.

---

## C. Research still worth doing

Ordered by what it costs, not by what it promises. Read
`docs/skeletonkey-reprompt.md` first — its kill inventory is the expensive
thing to reconstruct, and its three-box placement plus three triage tests
(bijection, cancellation, accounting) should be applied to anything below
before a file is opened. Its own verdict on the odds is worth repeating: for
"past n = 40 by a new method", box 1 is fenced by an information floor with no
known construction, box 2 is λⁿ, and box 3 needs an explicit char-2 basis
nobody has. That is a reason to aim carefully, not a reason to stop.

### C1. Combinations of things that already work

These are the cheapest ideas in this file, because both halves of each are
already built and measured.

**C1.1 — The parametric master × the λ atlas.**
`results/unexplored-avenues.md` idea 4 proposes certified two-sided λ brackets
across a *designed* family of row-local lattices — square (q=4), hex (6),
king (8), and a **spread** q=8 set such as `{(±1,0),(0,±1),(±2,0),(0,±2)}`,
same coordination number, far fewer triangles — to settle whether λ is a
function of coordination number or whether local cycle structure moves it. The
idea was ranked *last* and called "a separate project" because the machinery
was per-lattice. It no longer is: the diagonal law is proved for every
row-local lattice, the anisotropic criterion is lattice-generic, the strip
ladder and certificate checker are generic, and now the master equation is
parametric in `b = |D|`. The stated prediction — spread-8 lands noticeably
above king's 7.11, toward the tree bound — is falsifiable before anything is
run. Certified brackets for more than one or two lattices do not appear to
exist anywhere, and producing several would make two of this project's
universal theorems non-vacuous by exhibiting instances.

**C1.2 — The perimeter-defect machinery × the Sykes–Essam matching pair.**
`results/unexplored-avenues.md` idea 2 stalls on one sentence: the matching
identity grades the king side by size and the rook side by *site-perimeter at
unbounded size*, "and nothing here is enumerated that way". That was true when
it was written. `results/perimeter-defect-diagonals.md` and the banked
`results/perimdefect_square*` series are square-lattice enumeration graded by
site-perimeter defect to n = 78 at k ≤ 6. Whether the defect grading is the
grading the identity wants is exactly the question — it may not be, since
defect is measured from `pmax(n)` rather than absolutely — but the two halves
have never been put in the same room, and `results/matching-pair-convention.md`
has already pinned the convention that decides whether anything checks out
(perimeter is SAME-lattice; connectivity is what crosses). If it works it is a
cross-family exact identity, which is a validation channel of a kind this
project has never had. If it fails it fails on a paragraph of arithmetic.

**C1.3 — Undertow × the square lattice.** Listed above as A1.4 because it is
as much a validation chore as a research idea. It belongs in both places.

**C1.4 — The D2ax per-cell congruence × the Motley residue ladder.**
`results/subgroup-mod4.md` shipped `T(n,H) ≡ I_H(D2ax) (mod 2)` on all 820
cells — one independent bit per *cell*, from the height-preserving subgroup.
The Motley ladder produces every cell mod nine primes and reconstructs by CRT
with one prime held out. These are two independent modular views of the same
triangle and they have never been combined into a single per-cell warrant.
Probably nothing new falls out; the check costs an afternoon on banked data
and the provenance table is where it would show up.

### C2. Variations on things known not to work

Each of these has a specific counterexample in the tree. **A variation is only
worth writing down if it names the counterexample it has to beat**, so each
does. None of these is a re-pitch of the closed door itself.

**C2.1 — The per-level span cap, indexed differently.** The cap failed because
a *prefix's* span is bounded by the final cluster's cell count, not its own —
`{0,3}` over `{1,2}` is the counterexample, and the gate caught it undercounting
333 against 339 at `(e,k) = (0,2)`, K = 9. The variation that is not the same
idea: a two-pass DP that indexes by the final cluster's excess, so the bound
being applied is the honest `span ≤ 2K − e₂ − 1` rather than the per-level one.
It has to beat that counterexample explicitly, and it may just reproduce the
global cap, in which case it dies in a paragraph — which is the point.

**C2.2 — The dual-connectivity transfer matrix, made conditional.** It died on
a state count: `b·Cat(b)` against `Bell(b)` is 11,440 vs 4,140 at b = 8, so the
dual is *worse* where it matters. The arithmetic is only lopsided at large
block counts. A hybrid that carries the dual only where b is small is not
obviously useless — but it has to show that the small-b regime carries enough
of the frontier to matter, and the reason connectivity is the wall is that it
does not. Cheapest possible kill: measure the block-count distribution over a
real frontier, which is banked data.

**C2.3 — The strip finite-size fit, with the term the data says is there.**
Idea 6.1 was struck because `H(ln λ − ln μ_H)` is still falling at H = 17 and
its increments shrink ~6.5% per rung where a clean `1/H²` correction demands
~11.4% — so there is a term between `1/H` and `1/H²`, most likely logarithmic,
that the two-parameter ansatz cannot see. That is a *negative with a shape*.
Fitting the three-parameter form the data implies is not the same experiment,
and it either recovers a central charge or produces a sharper statement about
why five certified `μ_H` values cannot. Honest limit, unchanged: five points is
a short series and the certificates bracket rather than pin each `μ_H`, so the
fit must propagate the brackets or it is worthless.

**C2.4 — The basis question, asked in characteristic 0.**
`docs/skeletonkey-reprompt.md` calls the char-2 basis "the single largest open
technical question in the mission". `results/skeletonkey-hankel-closure.md` now
measures the char-0 transfer floor's base at **2.43, not 3** — the room is real
and it is a *different* room from the char-2 collapse. Both are
non-constructive today. Whether the char-0 sparsity pattern (row weights
1.06→1.77 and 1.75→2.19 against a dense d/2 = 346 at H = 7) exhibits any
structure a basis could be read off is a question nobody has asked, because the
sparsity was measured to answer A-S1's "crossover: never" and then set down.
Note what it does *not* rescue: the compressed dimension grows ~2.78×/height
against the column frontier's ~2.55×, so it crosses over near H ≈ 14 and sits
~2× worse by H = 21. The engine stays dead; the basis question does not depend
on the engine.

### C3. Genuinely new avenues

All of these are new-paper-sized and none of them shortens a sentence in any
current manuscript. That is stated, not hidden.

**C3.1 — Universality: is the king lattice in the same class as the square
one? DONE** — `results/theta-universality.md`. θ_king = −0.9997 against
θ_square = −0.9995 at matched length, and the same code reproduces the
published square λ to six digits, which makes it an external anchor for the
method the king exponent rests on.
 `results/unexplored-avenues.md` idea 6.2, untouched, and it survived the
closure of 6.1 because it does not run through the strip ladder. It is a
comparison of two θ fits — a *prediction* being tested, rather than a count
being extended. The repo measures θ = −1 by differential approximants and
never says why that number; Parisi–Sourlas dimensional reduction and Yang–Lee
appear nowhere in the tree.

**C3.2 — The limit object, and the sampler that would make it measurable.
SCOPED, NOT RUN.** The blocker is mixing, and mixing is not an afternoon: it
needs a chain whose irreducibility holds at the n being sampled, a bound on
its mixing time, and prior art checked (Janse van Rensburg–Madras, in
`papers/MISSING.md`). This is the only route in this file that gets past n = 40
by not counting, and it is a project rather than an item. Left open
deliberately.

Ideas 5 and 8 together. Idea 8's first gate is cleared — the move graph is
connected at every n ≤ 10, one component, no animal with n ≥ 2 ever stuck.
What was struck was collapsing that into a sampler: irreducibility is necessary
and nowhere near sufficient, the chain has to *mix*, and it has to be
irreducible at the n being sampled. Mixing is the missing step and it is the
whole programme — with a sampler, ν and the local weak limit become measurable
at n = 100+, far past the enumeration frontier, which is the only route in this
file that gets past n = 40 by not counting. Prior art likely exists; the
Janse van Rensburg–Madras entry in `papers/MISSING.md` is the first place to
look, and this project has a practice for un-findable papers.

**C3.3 — Extremal questions that are not the one already closed. DONE: three
trivial, one open** — `results/king-extremal.md`. Max diameter is n−1, max
articulation points n−2, min diameter ⌈√n⌉−1. Max hole *count* is the only
non-trivial one — 0,0,0,1,1,2,2,3,4, no OEIS collision, and king-specific
(four cells can enclose a hole where the square lattice needs eight).
 Minimum
site-perimeter is closed — the closed form was already published as A235382 and
was not re-proved, by design. What idea 7 lists and nobody has touched: max
and min diameter at fixed n, max articulation points, max hole *count* as
opposed to max single-hole area. "diameter" appears nowhere in the repo. The
oracle already computes what is needed at oracle scale, so entry is a
one-line reduction over data the repo can produce — and OEIS should be grepped
before anything is called new, because the square-lattice cases are classical.

**C3.4 — λ's upper bound, candidate 1. SCOPED, NOT RUN — and it is not mine
to run.** `docs/open-problem-lambda-bracket.md` is explicitly framed as a
collaboration target where "the bottleneck is mathematical insight, not
compute" and the decision of which direction to chance "is where a
mathematician's judgment is the lever". Machine effort spent here without that
judgment reproduces the bridge-credit sketch, which was closed as *unsound*.
 `docs/open-problem-lambda-bracket.md`
reads strip-decomposition-plus-vertical-join-bound as the most promising
direction and flags that the join multiplicity may itself be non-local. The
bridge-credit sketch that tried it is closed and was *unsound* rather than
merely unproved — step 1's encoding is not injective, 96% of the n = 8 census
collides at H = 1 — but the kill landed one step earlier than the load-bearing
claim, and step 2 held in everything measured. This is the item where a
mathematician's judgment is the lever and machine effort is not, which is what
the document was framed for.

**C3.5 — Two fields away, listed for completeness. SCOPED, NOT RUN.**
Different fields, different papers, and neither shortens a sentence here. The
one piece worth carrying forward is the convention observation, which C3.3
independently ran into: four king cells can enclose a hole where the square
lattice needs eight, so "hole" is lattice-dependent in a way that matters if a
published king number ever disagrees with ours.
 Discrete tomography
(reconstruct a polyplet from row and column sums; NP-hard in general for
polyominoes, polynomial for hv-convex, and king-connectivity changes the
constraint structure in a way that is not obviously either) and tiling, where
the interesting part is not the tiling questions but the convention underneath
them: a polyplet realised as a closed planar region joins at *points*, so
"hole", "boundary" and "simply connected" are convention-dependent in a way the
square lattice hides. If a published king-lattice number ever disagrees with
ours, that is the first place to look.

---

## What is deliberately not here

The closed doors, with their counterexamples, in `docs/lastditch-ideas.md` §6
and §7 and the twenty-row breadth table in `docs/skeletonkey-reprompt.md`. The
declined runs: Ticker Tape at H = 19, the k = 7 perimeter-defect census, the
P19 holdout, the cross-ISA a(40) recount, the d = 15..19 triangle tower, the
a(26)–a(30) diagonal ladder, the cloud. Anything in `PRE-LANDING.md`.

---

## What C changed

Four things, all folded in above; collected here so the delta is visible in one
place.

1. **A1.4 and A1.5 are done**, and were done as part of C — the square-lattice
   validation was C1.3, the cell-sparsity banking was C2.4's input.
2. **A1.8 is new**: the provenance table is a height stale and its gate cannot
   see it. C1.4 found it while checking what the table records.
3. **Three banked readings are corrected in place**, none of them by
   overturning a conclusion:
   - `results/strip-growth-lambda-bounds.md` — the non-analyticity inference is
     withdrawn; idea 6.1's closure stands on a quantified reason instead.
   - `docs/lastditch-ideas.md` §6 — the dual-connectivity kill's baseline was
     `Bell(b)` where the incumbent pays `Cat(b)`; corrected, the kill is
     stronger and uniform in b.
   - `docs/resume-here.md` — the compressed dimension is not catching up with
     the column frontier, it was behind from H = 4.
4. **Two external anchors were gained**, which the repo had few of: the DA code
   reproduces the published square-lattice λ to six digits, and Undertow's
   mechanism is validated against counts this project did not produce.

Nothing in C changed what B should remove, and nothing in C is a reason to
delay the landing.

## What C did not settle

Stated so that "section C is complete" is not read as more than it is.

- **C1.1 delivered the question, not the atlas.** λ ≈ 8.97 for spread-8 is a
  calibrated estimate from nine terms, not a bound. Certified brackets are a
  priced, unlaunched compute item.
- **C1.3 validated the frame at J = 1, not the king `D_j` values**, and not at
  the n = 56 depth §1b hoped for.
- **C3.2 and C3.4 are open on purpose** — one is a project, the other is
  explicitly not the machine's to attempt.
- **The max-hole-count sequence has nine terms and no conjecture.** It is a
  candidate for guess-and-prove, not a result, and OEIS must be grepped before
  it is called anything.
