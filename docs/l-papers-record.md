# The L papers: the contraction, and the literature-priority passes

> **Authored by Claude at jasonp's direction.** One record, merged 2026-09-06
> from three files of 2026-08-18 and 2026-08-23: the contraction that took ten
> manuscripts to six, the priority passes over L1-L9, and the pass over the
> Undertow material that became part of L8. Nothing here is a research result.
> The manuscripts themselves are indexed in `paper/README.md`, and the
> authorship rules are `docs/publication-split.md`.

## 1. The contraction of 2026-08-23

jasonp asked whether the L papers were truly worth the time spent, whether each
deserved its own write-up, and how to condense. This is the answer, and what
was done about it. It supersedes the per-paper rows of
`docs/publication-split.md` section 3 and the numbering narrative in
`paper/README.md`; both were updated to match.

jasonp asked whether the L papers were truly worth the time spent, whether each
deserved its own write-up, and how to condense. This is the answer, and what
was done about it.

### What the assessment found

**Ten papers, 108 pages, 33,067 words of prose, sixteen days of drafting.** The
manuscripts themselves were cheap: 36 commits between 2026-08-07 and 08-23. The
process around them was not.

| | |
|---|---|
| the `l-trim` adversarial campaign's ledger | **52,175 words** — longer than the corpus it reviewed |
| what five phases of it removed | 34,758 → 31,339 words, **−9.8%** |
| the rate | about 15 words of ledger per word cut |
| verdicts | 89 concessions, **one** RETAIN |
| `llm-tics` readability ledger | 10,468 words, five rounds |

The trim ladder ran *within* each paper, so it was structurally unable to
propose the one cut that mattered: deleting a section because another paper
already had it. Five phases of cutter-versus-defender never once looked across
a paper boundary, and the duplication that survived them is what this
contraction removed in a day.

**And nobody had read any of it.** All ten disclosure blocks read *"Human
verification: none, as of this draft."* The L scheme was priced at about eight
hours of jasonp's reading — his only job on that side being to read a statement
and decide to release it — and sixteen days in, that number was still zero on
every paper. jasonp's own account of why: *"we keep coming up with new but not
necessarily novel or interesting results right on the cusp of something great."*

**Three of the ten carried their weight** — L3, L4 and the law half of L1. The
three with clean novelty verdicts, which is not a coincidence.

### The seven moves

| | move | pages | why |
|---|---|---|---|
| **L3** λ bounds | kept as is | 13 | Both ends certified and re-runnable; no published upper bound existed; the lower end beats the published record where that value was numerical |
| **L4** not D-finite | kept as is | 10 | Unconditional, cheap, transports verbatim to polyominoes, polyhexes and polyiamonds |
| **L2 → L1** | merged, as Part II | 24 → **23** | L1's abstract already sold L2's spine cubic as its own third consequence; every L2 theorem was conditional on L1's Theorems A and C; L2 cited L1 eight times and spent its whole Setup restating the two results it imported |
| **L7 → L5** | merged | 25 → **21** | L7 called itself the companion in its first paragraph, restated L5's definition and four-block table verbatim — `tab:blocks` label collision included — quoted three L5 results without reproof, and was advertised in L5's abstract |
| **L10 → L8** | merged | 16 → **15** | jasonp's 08-22 ruling was "L8 absorbs the Undertow material", and absorb meant this. L10 spent about two of its seven pages restating L8's law, frame and square-lattice check; L8 carried zero `\cite` keys and L10 carried the near neighbour the priority pass found |
| **L6** | inverted and contracted | 13 → **14** | The minimum end leads, being the half the priority pass left whole; the maximum end now opens by saying it is the king analogue of a published theorem. The standalone "k = 6 verdict" section is dissolved into the four claims it decides |
| **L9** | withdrawn | 7 → **0** | Its own ledger: *novelty none claimed, and a collision found*; the load-bearing step is a reading of C++; "that any program computes the sum" is not addressed. Folded into `docs/proofs/cutcount-identity.md`, which was better than it in every part except one — the doc predated the 08-18 priority pass, so L9's FK/Potts finding is now its §9 |

**Ten papers, 108 pages → six papers, 96 pages.** Prose 33,067 → 30,405 words.

Every merged manuscript builds with zero undefined references and
`paper/verify_l_papers.py`'s 336 checks stay green, 23 RED controls firing.

### Two things the estimate got wrong

**L6 was estimated at ~8 pages and came out at 14.** The estimate was wrong, not
the execution. What makes L6 long is evidence and closed doors — the six dead
readings in "Doors closed", the coefficient triangle, the recentred basis — and
neither gets cut. The inversion and the reframing were the real content of that
move; the page count was never going to fall much without deleting results.

**The proposal said "five papers" in prose and listed six in its own table.**
Six is right: L1, L3, L4, L5, L6, L8.

### What the merges fixed on the way

- **L1** — L2's `\vthree` macro was defined in the file that no longer exists,
  which `pdflatex` caught. And "the spine" meant two different things across the
  boundary: Part I's universal curve, and Part II's first non-divisible cell of
  a column, now "the spine of a column".
- **L5** — the Gouyou-Beauchamps and Leroux attribution that
  `docs/publication-split.md` requires in three places came out better than it
  went in. The split had forced *four* placements numbered as two separate
  "k of 2" pairs, so both files said "2 of 2" and neither counted to three. One
  file, three placements, counted 1-2-3.
- **L8** — L10's abstract ended "we have run no priority pass", false since
  08-23 when the pass ran and found something. Gone with the abstract that
  carried it.

### The coverage measurement this produced

Merging the corpus made it worth asking what any of it is checked by.
`results/l-paper-verifier-coverage.md`: **74 of 531 numeric literals are read by
any check.** L5 and L8 are 0 of 144 and 0 of 69. The tool is
`tests/l_paper_coverage_audit.py`, 80 seconds for the whole corpus.

### What was also closed

- **The `llm-tics` readability campaign.** Round 5 reached the verdict itself:
  four of six tracked constructions are at zero across the corpus, dash-asides
  are 0.16/1k against the P control's 0.40, and the two that remain are carrying
  epistemic status rather than habit. `docs/reviews/llm-tics/PLAN.md` says
  closed.
- **`scripts/l_trim_gate.sh`.** **Deleted.** Campaign-scoped and never wired
  into `make`; it stood between a phase and a commit, and there are no more
  phases. Two of the six manuscripts its baseline names are gone, and
  `paper/verify_l_papers.py` had to leave its checksummed `FROZEN` list to admit
  the coverage audit, so it had been red at `HEAD` for a stale-baseline reason
  since before `docs/reviews/llm-tics/round5-L6.md` recorded it. Its check 7 —
  the one that caught an attribution vanishing when a paper drops its last
  `\cite` of a key — was run by hand over this contraction instead, and found
  one: Blöte–Nightingale 1982, now carried in the proof doc.

### What was decided not to do

**The short-rook certified brackets are not an eleventh paper.**
`docs/state-2026-08-23.md` §5 priced them as "the material of a separate short
paper". They are a section of L3, which is already the certificate paper:
making the certificate program lattice-parametric turns its two-sided bracket
into a family of them. That is a stronger L3, not a thinner L11.

**Of the five priced runs in `docs/state-2026-08-23.md` §5, none changes a
sentence in any L paper.** The five terms, the census past H = 17 and the H = 13
rank test are ladder and reach work, and the ladder closed at a(41). c₆ on the
main-diagonal spine is a day of compute to settle a judgement call about a
family no paper claims.

## 2. The priority passes over L1-L9, 2026-08-18

Run under the standing rule adopted 2026-08-17, after a result was derived at
length and found afterwards to be published. One subsection per paper: what was
searched, what was found, what changed in the paper.

**Method.** Web search over the combinatorics and statistical-mechanics
literature, following named authors and citation chains rather than keyword
alone; full text pulled where free. This is a search, not a proof of absence,
and the sections below say which searches were run so the next pass starts
after this one rather than before it. Anything unobtainable goes to
`literature/MISSING.md`.

**Headline: three real collisions, two of them on load-bearing statements.**

| paper | verdict | action |
|---|---|---|
| L9 | **collision, at the level of the whole statement** | reframed; novelty claim withdrawn entirely |
| L6 | **collision on the structural theorem and on the defect identity** | attributed; claims narrowed to the king column |
| L5 | **antecedent found for the kernel method** | Bousquet-Mélou–Fédou cited; the earlier Richard collision stands |
| L7 | no new collision | the L5 attributions carry over |
| L2 | no collision; one method-adjacent body of work | Rowland–Yassawi cited, with why it does not apply |
| L8 | no collision found | recorded; the paper still claims nothing |
| L1, L3, L4 | no collision on the new material | recorded |

### L9 — the cut-count identity. COLLISION, and a large one.

Searched: connected-subgraph counting by transfer matrix with `q^{components}`
weights; Fortuin–Kasteleyn random-cluster versus Potts spin representation;
Blöte–Nightingale transfer matrices; Hoshen–Kopelman cluster labelling;
Jensen's polyomino algorithm and the Barequet-group complexity analyses of it.

**Finding.** The identity is an instance of the Fortuin–Kasteleyn/Potts
correspondence. The random-cluster partition function is
`Z = Σ_g v^{bonds} q^{clusters}`, and counting connected subgraphs is its
`q → 0`, `v = 1` content; the standard device for evaluating `q^{c}` without
tracking connectivity is exactly the **spin representation** — colour the
components, count colourings — which is what our model does, scan order and
all. The unsigned ancestor of the scan-order labelling is Hoshen–Kopelman
(1976). The connectivity-tracking method our engine is an alternative to is
Jensen's signature algorithm.

Read against that, the telescoping in §Proof is the FK↔spin equivalence
executed cell by cell: each component contributes `b` reuse terms and one
`(q − b)` birth term, summing to `q`. That is not a new theorem.

**What survives.** The window-bounded scan-order *form* of it: that a window of
`H+1` cells suffices under king adjacency (our Lemma 1), and that the resulting
rule is exactly what one particular engine implements. That is
implementation-grade, and the paper now says so in the abstract rather than in
a novelty section at the back.

**Action taken.** Abstract, introduction and novelty section rewritten; the
identity is presented as the specialization it is, with the FK/Potts and
Hoshen–Kopelman references in place. The paper is kept because the *proof of
the specific rule*, with its window and liveness convention, is what licenses
the second source, and nothing published states that rule.

### L6 — perimeter gradings. COLLISION on the structure, as suspected, and worse than recorded.

Searched: Asinowski–Barequet–Zheng and Barequet–Magal on fixed perimeter
defect; the polycube generalisation; minimal-perimeter animals and the
constant-isomer conjecture. **The Asinowski slides were obtained in full text
this pass** (`mat.univie.ac.at/~slc/wpapers/s79vortrag/asinowski.pdf`), where
the repository previously held only the fact of their existence.

**Findings, three of them.**

1. **The defect identity is theirs.** Their Proposition is `k = e + 2f` with
   `e` the total excess of perimeter cells and `f` the circuit rank. Our
   `k = 2c + t` — the identity L6's ledger calls proved and load-bearing, and
   which licenses the enumeration prune — is that statement with `c = f` and
   `t = e`. Independently derived here for the king lattice; published for the
   square one.
2. **The structural theorem is theirs.** "For each fixed `k`, the generating
   function of `(A(n, 2n+2−k))` is rational, and more precisely its denominator
   is a product of cyclotomic polynomials" — stated for polyominoes and, they
   note, with the same main result in `d` dimensions for polycubes. L6's
   cyclotomic-denominator framing is therefore the king analogue of a published
   theorem, not an observation of ours.
3. **Their small cases match ours.** `A(n, 2n+2) = 1` for `n ≥ 2` and
   `A(n, 2n+1) = 4(n−2)` for `n ≥ 3` are the square-lattice `k = 0, 1` rows.

**What survives.** The king column throughout; the onset formula
`k(k+1)/2 + 3`; the two-lattice universality of period, degree, onset and
leading coefficient, now tested through `k = 6`; the coefficient triangle and
its one-diagonal-deep lattice independence; and the whole minimum end. None of
those appear in the slides. The minimal-perimeter literature that does exist
(constant-isomer, square and hexagonal) is structural — inflation of
minimal-perimeter animals — and does not count by perimeter the way §min does.

**Action taken.** Attribution paragraph promoted out of §Novelty into the
statement of the defect identity and into the cyclotomic section; the ledger
now records the identity as *theirs, re-derived here for king*; the novelty
section rewritten around the three findings above.

### L5 and L7 — convex polyplets. One antecedent, and the earlier collision stands.

Searched: Bousquet-Mélou and Fédou on the convex-polyomino `q`-differential
system; the festoon approach; Klarner–Rivest and Bender constants; `q`-Bessel
zero literature; Kotesovec's constants for A067675/A067676.

**Finding.** Bousquet-Mélou and Fédou, *The generating function of convex
polyominoes: the resolution of a q-differential system*, Discrete Math. 137
(1995) 53–75, is the classical antecedent of §Kernel: the same shape of object,
solved for the square lattice by a `q`-differential system, with the
Klarner–Rivest function as the denominator whose smallest positive zero gives
the growth constant. Our kernel `K` is the king analogue, and the control arm
of our own pipeline reproduces their constants — which is the anchor, and is
also the reason the antecedent must be cited rather than merely noted.

No separate collision was found for the certified-interval treatment of the
constants, for the negative zero at `q = −0.795`, or for the identification of
the measured Prony spectrum with `1/zeros(K)`.

The area-moment collision found on 2026-08-17 (Richard, arXiv:0704.0716;
Enting–Guttmann 1989) is unchanged and remains cited in three places.

**Action taken.** Bousquet-Mélou–Fédou cited in §Kernel and in related work.

### L2 — the mod-3 arithmetic. No collision; one adjacent method.

Searched: congruences modulo powers of 3 for combinatorial sequences;
Krattenthaler–Müller's method for mod-`3^k` behaviour of recursive sequences;
Rowland–Yassawi automatic congruences for diagonals of rational functions;
Smith normal form of combinatorial triangles; base-3 digit-product formulas.

**Finding.** Rowland–Yassawi (J. Théor. Nombres Bordeaux 27 (2015) 245–288) is
the closest machinery: for a sequence whose generating function is the diagonal
of a rational power series, they compute a finite automaton modulo `p^α`. It
does not apply here, and the reason is a result of ours — companion paper L4
proves the height generating function is not D-finite, so it is not such a
diagonal. That is worth a sentence in L2 precisely because a reader who knows
that literature will ask.

No collision on the spine cubic, the digit product, or the all-3-powers Smith
normal form.

**Action taken.** A related-work paragraph in L2 naming both and saying why
neither applies.

### L8 — below the onset. No collision found.

Searched: corrections and error terms to fixed-height / bounding-box animal
formulas; asymptotics of defects below a formula's threshold; algebraic
generating functions for leading coefficients of such families; polyomino
enumeration by bounding box.

Nothing close. That is a weak negative — the object is defined relative to our
own diagonal law, so a collision would have to be with a paper that had that
law first, and companion paper L1's sweeps cover that. The paper continues to
claim nothing.

### L1, L3, L4 — the new material only.

Their N1–N6 sweeps stand for the material they covered. This pass looked only
at what postdates those sweeps.

- **L3's BFS-frame encoding** (the repaired proof of the `5^5/4^4` bound). No
  collision found on the king constant. Adjacent and worth watching: the
  Barequet-group improved upper bounds for polyominoes and polycubes, a 2025
  convolutional approach to bounding polyomino counts, and a 2025 short proof
  of a polyiamond bound. All are square-lattice or polyiamond and none states a
  king number.
- **L1** — the below-onset link is L8's material and is covered above.
- **L4** — unchanged since its sweep; nothing re-searched.

### What the next pass should do differently

Two of the three collisions were found by pulling **full text of a source we
already knew about** rather than by a new search. The slides had been sitting in
`literature/MISSING.md` as unobtainable; they were free. Before the next round of
keyword searching, re-try every entry in that file.

### ABZ full text — obtained the same day, and it answers the question the slides left open

The paywalled Asinowski–Barequet–Zheng paper the L6 pass wanted is free: the
ANALCO 2018 polycube companion, "Polycubes with small perimeter defect,"
Proc. ANALCO 2018, 93–100. Filed in `literature/`. It carries the proofs the slides
only stated.

**What the proof actually is.** For a polycube `P` in `Z^d` under face
connectivity: `p = 6n − e − 2|E|` counting the two ways perimeter is lost,
giving `p <= 4n+2` and `k = e + 2r` with `r` the circuit rank (their
Proposition 2.1 — our `k = 2c + t`). Rationality (their Theorem 3.1) is proved
by *cut shrinking*: a `j`-orthogonal cut is a maximal run of grid slices whose
projection is a set of pairwise non-adjacent cells with no common neighbours;
deleting a cut's slices and regluing preserves the defect, cuts are pairwise
independent, so every polycube shrinks to a unique reduced one. A pattern class
is a fibre of that map, its generating function is `x^b` times a product of
`1/(1−x^s)` (s = number of ports of a cut), hence cyclotomic. Finiteness of the
class count comes from bounding three kinds of special cell — excess cells,
L-cells, and degree-1 cells — each against `k = e + 2r`, with the degree-1
bound `|V_1| <= 4|V_{>=3}| + 2` coming from the handshake inequality at maximum
degree 6.

**Verdict for L6: the king column is a separate derivation, not a corollary.**
Every mechanical step above is stated in face-adjacency terms — the perimeter
accounting `6n − e − 2|E|`, the L-cell definition ("occupied neighbours that
are not opposite"), the non-adjacency condition defining a cut, and the
handshake bound at max degree 6. None of it is stated lattice-generically, and
king adjacency breaks the cut condition in particular. The *shape* of the
argument plainly transports; the theorem does not. So L6's king results are not
inside their framework, while our square-lattice statements remain their
theorem re-derived.

**They conjecture what we measured.** Their §4 conjectures that for any `d` and
fixed `k` the highest-degree factor of the characteristic polynomial is
`(x−1)^{k+1}`, so that the count is asymptotically `γ n^k`. Our table in
`results/perimeter.md` has exactly `Φ₁^{k+1}` and degree `k`
for every `k <= 6` on **both** lattices. That reframes the degree row: for the
square lattice it is evidence for a published conjecture rather than an
observation of ours, and for king it is evidence for the same conjecture on a
lattice their framework does not reach. L6 should say so.

**Also settled by the same paper:** their `B(n,d,0) = d` and
`B(n,d,1) = d(d−1)(n−2)/2`, and the observation that a pattern of defect `k`
spans at most `k+1` dimensions.

**Not done here, and open for his call:** the L6 edits implied by the two
paragraphs above — citing the ANALCO paper rather than the slides, and
restating the degree row as a conjecture-confirmation.

## 3. The pass over the Undertow material, 2026-08-23

Run overnight at jasonp's direction over what was then `paper/L10-undertow.tex`,
drafted the day before with a banner saying no pass had been run. The
manuscript was merged into `paper/L8-below-onset.tex` the next day and this
pass's verdict stands there as its Novelty section.

**Verdict: a near neighbour exists, in a different problem, and the paper must
cite it. No collision on the specific claim.**

### What was searched

Five web searches, in this order:

1. lattice animal enumeration + correction term below threshold + exact defect
   polynomial + fixed height / bounding box + asymptotic law;
2. "below the threshold" / "before the onset" + exact correction to a
   polynomial formula + series extrapolation + fewer terms needed;
3. Jensen / Guttmann + series expansion percolation probability + correction
   terms + finite lattice method;
4. polyomino enumeration + transfer matrix + finite lattice method + correction
   terms + exact error term below validity threshold;
5. "finite lattice method" + corrections known exactly + quasi-polynomial +
   onset + validity range + animals.

### What it found — the near neighbour, and it is close

**Directed-percolation series extrapolation by correction terms.** Baxter and
Guttmann (1988), then Jensen and Guttmann through the 1990s, extend the
percolation-probability series for directed lattices by exactly the manoeuvre
this paper's method is built on: a finite-lattice calculation of size `N` is
exact only up to some order, the difference between the exact infinite series
and the finite one is a *correction term* `d_{N,r}`, and knowing those
corrections lets a series be pushed past where the finite lattice is exact —
so the same reach is bought with smaller calculations.

- R. J. Baxter and A. J. Guttmann, *Series expansion of the percolation
  probability for the directed square lattice*, J. Phys. A 21 (1988) 3193.
- I. Jensen and A. J. Guttmann, *Series expansions of the percolation
  probability for directed square and honeycomb lattices*,
  `arXiv:cond-mat/9509121`; and the directed triangular lattice,
  `arXiv:cond-mat/9511084`.

**The ambient family** is the finite-lattice method (Enting; Jensen), in which
small-lattice transfer-matrix data is combined to reach the infinite lattice.
Undertow is a member of that family and the paper should say so rather than
present the shape of the idea as new.

### The one distinction that survives, and it is the honest claim

In the percolation work the correction terms are **conjectured and fitted** —
Baxter and Guttmann conjecture them as rational functions of Catalan numbers,
and the extrapolation rests on that ansatz holding at the next order. That is
what makes their extended series a prediction rather than an enumeration.

Here the correction is **computed exactly, ab initio, by a machine that never
sees the object it corrects**: `D_j(k)` comes from a bounded-excess family
enumeration that reads neither the triangle nor `P_k`. And the number of
unknowns it has to determine per level is not assumed but **proved** — the
grand form gives exactly two constants per level, and that proof is
Lean-complete against the standard axioms.

So the honest form of the claim is the one the draft already anticipated: what
may be new is not the idea of correcting finite-size data, which is standard
practice in this literature, but the combination of an exact independently
computed correction with a proved constant count, in a setting where the saving
is measured in banked compute rather than in extrapolated series orders.

### No collision on the specific claim

Nothing found applies a correction of this kind to **bounding-box-height
animal counts**, and nothing found corrects a **diagonal law** for such counts
in order to pin polynomial levels from below its onset. Searches 1, 4 and 5
were aimed squarely at that and returned the finite-lattice-method literature
and the polyomino enumeration record, not this.

### What this pass is worth, stated as a limit

Web search only. No MathSciNet, no Zentralblatt, no citation-graph crawl of the
Baxter–Guttmann line — which is exactly where a closer instance would sit if
one exists, because a paper that did this for animals would likely cite them.
Five queries is a thin sweep for a negative. The positive finding above is
solid; the negative is provisional and should be re-run against a citation
database before submission.

### Side finding, which the tree had already made

The searches turned up that the square-lattice fixed-polyomino record is not
`n = 56`: OEIS [A001168](https://oeis.org/A001168)'s b-file, contributed by
Barequet and Ben-Shachar, runs to **n = 70**, and Shirakawa,
*Enumeration of Polyominoes up to Size N=59* ([arXiv:2510.22446](https://arxiv.org/abs/2510.22446),
October 2025) independently reaches 59.

**This project found that first** — `docs/lessons-learned.md:151` says so, and
`results/rook1/queue.md` row K4 is an open chore to sweep the stale mentions.
So the correct status is "known, unswept", not "found tonight". The sweep has
now been done and K4 is closed:
`docs/publication.md` is the one place, it lists all six
live sites and what each becomes, and the answer is that no conclusion moves —
the record that grew is the sequence of *totals*, while every use this project
has wants the bounding-box triangle or a perimeter grading, and neither is
published at any n.
