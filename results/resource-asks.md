# Resource asks — what a small breakthrough would actually cost

2026-08-04. Written at jasonp's request: spitball, kept realistic, of the
resources (papers, compute, textbooks, emails, people) that could move a
currently-stuck item. Companion to `results/unexplored-avenues.md`, which lists
the *ideas*; this lists the *inputs*.

> **Status: nothing here is authorised, costed, or agreed.** The compute figures
> are quoted from existing repo measurements where they exist and marked GUESS
> where they don't. No email has been sent. The project closes at a(40); every
> item below is downstream of report placeholders and publish prep.

Standing filter (MEMORY.md, claim-pruning): each item names the sentence that
gets shorter, or says it doesn't.

---

## 1. Emails — cheapest lever, by a wide margin

Three of the repo's banked results carry **novelty: UNCHECKED**. A single reply
from the right person either promotes one to a paper section or deletes it
before a referee does. That asymmetry is why this category is ranked first.

### 1a. Gill Barequet (Technion) — the finite-type barrier

One question: *is it already known that finite-type convolution bounds cannot
reach λ?*

`docs/open-problem-lambda-bracket.md` records the P2 slack audit
(`experiments/king_slack.py`): the 9.3153 over-count is diffuse (median slack
1.14, worst type 1.22) and **compounds at +0.022 per cell**. Slack growing with
n is the signature of a non-local over-count, which no finite context R can
see — so the whole method class floors strictly above λ. The doc itself calls
this "arguably a publishable observation in its own right."

Barequet owns that method class (Klarner–Rivest lineage, the cut hierarchy, the
concatenation paper already read and closed in `papers/MISSING.md`). He is the
person most likely to know in one line whether this is folklore.

**Sentence that gets shorter:** the paper's λ-bracket discussion either gains a
barrier theorem or loses a claim. Either outcome is worth more than a week of
compute.

### 1b. Guttmann or Jensen — series analysis and the anisotropic theorem

Two items land squarely in their lane:

- `results/anisotropic-not-dfinite.md` is an unconditional theorem whose
  **novelty vs the literature is explicitly unchecked**. Guttmann's circle would
  know instantly.
- The θ = −1.000(1) correction structure from the differential approximants
  (`results/series-analysis-da.md`, and the C2 margin analysis in
  `results/open-conjectures.md` which tracks −θ/n² to within 0.89→0.97 over
  n = 5..39).

Also the natural referee-in-advance for the four-method λ ≈ 7.110(1) estimate.

### 1c. Tremblay & Vernay — an independent second source

`results/ns_a40/PROVENANCE.md:127` records **H15–19 = 43.84% of a(40) with
"none available"** for a second source. H11–14 (37.49%) has the strip TM run,
but that source shares `core/transition.h`'s union-find rule, so it is not fully
independent.

Tremblay & Vernay held the prior a(18) record (RAIRO-ITA 2024, cited in
`oeis/A006770.txt`) and their enumerator is public:
`github.com/J-Vernay/discrete-figures`. Grepping the repo (2026-08-04) I find
**no record of that code ever having been fetched or run here** — only the two
citation mentions above. It is structurally unrelated to our machinery.

**Sentence that gets shorter:** the PROVENANCE row that currently says "none
available". This is the cheapest item in the whole file that touches the
frontier record — no email strictly required, the code is just sitting there.

### 1d. Lower priority

- **Klazar** — Thm 4 (P-recursive mod 2^k with no P-recursive parent) vs the
  ternary spine, the resonance flagged as "open and nobody has looked" in
  `results/anisotropic-not-dfinite.md`. The cheap probe already came back
  negative (`experiments/modp_bm_probe.py`: BM order ~n/2 mod every small
  prime), so this is a question, not a lead.
- **OEIS / Sloane** — already gated on the viva (see MEMORY.md), not a new ask.

---

## 2. Papers — a library card, essentially

`papers/MISSING.md` has three medium-priority items still outstanding:

| item | why |
|---|---|
| Conway 1995, "Enumerating 2D percolation series by the FLM: theory" | the finite-lattice-method architecture our bounding-box 4-direction split sits inside |
| Conway & Guttmann 1995, "On two-dimensional percolation" | same lineage; also feeds the matching-pair idea (§2 of unexplored-avenues) |
| Enting 1980, self-avoiding rings | origin of the FLM |

Alumni library access, or roughly $30/article of interlibrary loan, clears the
list. Also on that page: the Tremblay–Vernay paper is flagged as *probably* open
access at rairo-ita.org and worth trying directly before paying for anything.

**Sentence that gets shorter:** the FLM one is the only way to know whether the
4-direction decomposition is a rediscovery. That is a prior-art risk on a paper
headline, not a research lead — which makes it cheap insurance rather than a
breakthrough.

---

## 3. Textbooks — one real gap, not several

**The gap: total positivity.** C2 (strict log-convexity of A006770) is walled,
and `results/open-conjectures.md` now records *why* from both sides: Liu–Wang
2007's entire apparatus bottoms out in either a three-term recurrence or a
construction from already-log-convex pieces, and a(n) has neither — the same
wall as "no clean injection is known", seen from the other side.

The one route named there and never attempted is **total positivity of the
transfer matrix**. That is a genuine unexplored attack rather than a
restatement, and it is textbook-shaped: Karlin's *Total Positivity*, or Brenti's
memoir on total positivity in combinatorics.

Secondary, only if the mod-p line revives: Allouche & Shallit for automatic
sequences (the Christol route to a(n) mod 2). Given the negative BM probe this
is not currently live.

Not a gap: analytic combinatorics generally. The series-analysis work already
in the repo is not limited by missing standard technique.

---

## 4. Compute and storage — RAM, not cores

Two blocked items are blocked on memory alone. Neither wants more cores.

### 4a. dmirror — 24h / 126GB (measured, `results/related-seqs-n33.md`)

Unblocking it pays twice:

- it is the mod-8 rung of the orbit-congruence ladder (§1 of
  `results/unexplored-avenues.md`) — hmirror and r180 are cheap, dmirror is the
  blocker;
- it is what the five related sequences (A030222/A030233/A030234/A030235/
  A194596) need. They have been **stranded at n=32–34 while fixed reached 40**.

A ~256GB box turns this from blocked into an overnight run. This is the one
hardware ask with two independent payoffs.

### 4b. Strip ladder H=18/19

`docs/open-problem-lambda-bracket.md`: the ladder buys ~+0.05 on λ's certified
lower bound per rung at ~3× cost per rung, and is **memory-limited near H≈18 on
current boxes**. H=17 already came in at 13 minutes with the frozen-stage-operator
engine.

This is the only item in this file with a *guaranteed* payoff — you know the
certified number improves before you spend anything. Everything else is a
gamble on an outcome.

### 4c. Free today, no purchase

The **mod-4 orbit census** — I(C4), I(D2ax), I(D2diag) — is guessed at ~λ^(n/4)
~ 3e8 objects at n=40 (GUESS, growth-rate arithmetic only, per
unexplored-avenues). That is laptop scale. It would give two independent bits
mod 4 on a(40) from a structurally unrelated algorithm on a quotient domain,
covering 100% of the row including the H15–19 gap in §1c.

Cheapest thing here that shortens a named sentence, and it needs nothing bought.

Storage note: `results/reach-scaling-*` / MEMORY.md record the engine as
disk/spill-bound at the top end, so NVMe capacity is the storage axis if any is
wanted, not bulk disk.

---

## 5. People — the thing the λ upper bound actually needs

`docs/open-problem-lambda-bracket.md` states it plainly: "genuinely hard, and
the bottleneck is mathematical insight, not compute." The dual asymmetry is the
whole problem — the μ_H ladder has full connectivity but bounded extent; the
twig method has unbounded extent but relaxed connectivity. **Connectivity plus
unbounded extent is what neither face achieves.**

No purchase fixes that. The realistic forms of this ask are: circulate the
framed open-problem doc to the Guttmann/Barequet circle, a combinatorics
seminar, or MathOverflow. Publishing decisions are jasonp's
(MEMORY.md, publishing-is-jasonps-call) — nothing here goes out without his say.

Idea 3 in `results/unexplored-avenues.md` (the bridge-credit sketch) is the only
home-grown candidate with both properties simultaneously, and it is filed there
as most-likely-wrong with a named fastest-way-to-kill-it.

---

## If only one thing

The Barequet email plus the mod-4 census on existing hardware: one message and a
day of laptop time, against a claim in the paper and a provenance gap in the
record. The RAM purchase (§4a/§4b) is the only item that costs real money, and
the strip ladder alone justifies it.

## Provenance

Figures quoted from: `results/ns_a40/PROVENANCE.md` (43.84% / none available),
`results/related-seqs-n33.md` (24h/126GB), `docs/open-problem-lambda-bracket.md`
(slack audit, ladder cost, H≈18 memory limit), `results/open-conjectures.md`
(Liu–Wang read, C2 margin), `papers/MISSING.md` (outstanding citations),
`results/unexplored-avenues.md` (orbit ladder, cost guesses). The Vernay-code
"no record in repo" finding is a grep run 2026-08-04 over `*.md`/`*.txt`;
only two citation mentions exist.
