> **NOTE: authored by Claude at jasonp's direction, 2026-08-18.** A proposal,
> not a decision. It revises `docs/publication-split.md` — that file's §1 (the
> two categories and the disclosure blocks) and §4 (the OEIS lineup) stand
> unchanged; its §3 table, §5 gates and its suggested order are what this
> replaces.

# Release strategy, revised

## 0. The venue, stated first, because it changes everything below

**This is not a journal submission.** Per jasonp, 2026-08-18: the release is a
public git repo — code, results, the PDFs, a gist or two — plus the OEIS
entries. There is no referee, no editor, no acceptance.

That removes the gatekeeper and puts the burden somewhere harder. A journal
reviewer is obliged to read; a stranger who lands on the repo from an OEIS
cross-reference is not. He clones it, runs something, and decides in about ten
minutes whether the numbers are real. Everything below is ordered by what he
touches in those ten minutes.

The corollary the old plan got backwards: **the repo is the publication and the
PDFs are attachments to it.** The 08-07 plan sequenced on manuscript readiness.
Manuscripts are now the part in best shape and the part least likely to be read
first.

## 1. What changed since 08-07

**The L side got built.** Seven compiling drafts — L1–L6 as planned, plus **L7
(the subdominant exponential and the amplitude ratio)**, carved out of L5 and
never contemplated by the split doc. Then a five-phase trim (34,758 → 31,339
words, −9.8%), an LLM-tic sweep, a coinage sweep that demoted "law" and renamed
king animals to polyplets, and a readability pilot on L2. `paper/README.md` is
stale on one point: it still lists six.

**The P side did not move.** `technical-report.tex` is 331 lines, ~40% built,
read-only to the machine. The 08-07 order assumed P1 was in flight and the L
papers ran alongside. The opposite happened.

**Three new inputs:**

- **The literature-priority gate** (adopted 2026-08-17). Ghost Ship Layer 3 was
  correct, internally verified, and already in Richard arXiv:0704.0716. For a
  repo release this matters *more* than it would for a journal, not less: there
  is no referee to catch a "new" that isn't, and a stranger who finds the
  collision himself discounts everything else in the tree.
- **The reviewer-tier map** (`docs/reviewer-expertise-tiers.md`): a(40) is the
  cheapest claim in the project to assess and the most heavily corroborated. It
  is also the only one most visitors will care about.
- **The acceptance queue** (`docs/acceptance-queue.md`): four items that are
  now not prerequisites *for* the publication — under a repo release they **are
  the publication.**

## 2. The revision, in one sentence

Ship the repo as the artifact: make `git clone && make && <one command>`
reproduce a real value on a clean box, put one provenance table at the front
door, and let the PDFs be what a visitor reads *second*.

## 3. Proposed order

**Track A — the front door.** Acceptance-queue items 2–4, and they are the
release, not the run-up to it.

- A genuine clean-clone run on ayr or dalby. Currently broken two ways:
  `build/ns/*_worker` isn't built by a bare `make`, and the citation gate wants
  `papers/` PDFs a clone deliberately doesn't have. One documented command that
  reproduces a(26) from nothing.
- **One per-cell provenance table**, gated against the banked rows so it cannot
  drift. Today "what is confirmed, by which independent source, covering what
  share" is spread across five files, and that spread already caused one
  error — the strip-coverage vs holdout confusion. For a repo release this
  table is the single most valuable page in the tree: it is the honest answer to
  "why should I believe a(40)", in a form a visitor can check.
- A fail-closed check of every b-file and OEIS artifact against primary data.
  A wrong digit in a b-file is the worst failure mode available here, and OEIS
  is the channel that brings visitors in.
- A top-level README that opens with the claim, the one reproduce command, and
  a link to the provenance table. Right now the front page does not do that job.

**Track B — the ladder.** Confetti (H=18), then Ticker Tape (H=19). The only
compute item, and the only thing that changes what P1 may claim: rule-independent
closure 33 → 35 → 37, residual band on row 40 shrinking 9 → 7 → 5 → 3 cells.
Runs alongside Track A without competing for anyone's attention.

**Track C — the L papers, three at a time.** L3 (λ bracket), L1 (diagonal law),
L4 (not D-finite): clean novelty verdicts, and warrants a stranger can re-run in
exact arithmetic — which is exactly the kind of paper that survives having no
referee. Each needs, in order: a priority pass dated after its own drafting;
enough reading from jasonp to replace "human verification: none" in the ledger
with a specific line; then it goes in the repo with the rest.

**Track D — P1, after the provenance table exists.** The 30–50 hour estimate
stands and most of it is the engine chapter and §Reproducibility. Writing
§Reproducibility before the table exists means writing it twice. Under a repo
release P1 is also allowed to be shorter than a journal version would be: it can
point at the tree instead of reproducing it.

Then P2, P3, and the analytic papers.

## 4. Per-paper state and gate

| | paper | drafted | gate before it goes public |
|---|---|---|---|
| **L3** | λ bracket 6.543 ≤ λ ≤ 9.3154 | yes, 14pp | priority pass; certificates regenerate on a clean box; **9.3154, never rounded back** |
| **L1** | diagonal law | yes, 15pp | priority pass |
| **L4** | not D-finite | yes, 11pp | priority pass |
| **L2** | mod-3 arithmetic | yes, 10pp | **novelty never swept** — N1–N6 never touched the spine cubic, the digit product or the SNF count |
| **L5** | convex polyplets | yes, 18pp | Gouyou-Beauchamps–Leroux cited in three places, every revision. See §5 |
| **L7** | subdominant exponential, amplitude ratio | yes, 11pp | same attribution, two places; the sharp-asymptotic conjecture stays labelled a conjecture |
| **L6** | perimeter gradings | yes, 11pp | **compute-gated and unresolved** — §5 |
| **P1** | fixed polyplets through a(40) | 40% | Track A |
| **P2**, **P3** | — | not started | his prose; P3 additionally on the `hv-growth-sandwich` reading gate |

Every L ledger currently reads "human verification: none", and every L paper
carries a loud draft banner saying so. A repo release can honestly ship a draft
banner in a way a journal cannot — but then the banner has to be true, and
"none" across seven papers is a weaker position than "statements read" across
three.

## 5. Open decisions

**L6's perimeter gradings — no longer a decision, but a rewrite.** Both k = 6
censuses turned out to have finished on dalby on 2026-08-09 and 08-10 and never
to have been brought back into the repo; they were harvested 2026-08-18 and the
verdict is in `results/perimeter-defect-diagonals.md`. Three of the paper's four
k = 6 tests pass (onset 24, the Phi_3 exponent, no Phi_4) and **one fails**: the
Phi_2 leading diagonal is 5/2, not the 15/4 the closed form predicted. A second
k = 5 statement also fails to extend — the full Phi_3 block is lattice-
independent at k = 5 and only its leading coefficient is at k = 6. The
universality claim itself survives and now runs through k = 6. So L6 needs its
placeholder section written, two claims withdrawn, and its do-not-submit banner
removed — not a compute decision.

**L5 and the 08-17 salvage.** `results/convex-polyplets.md` gained the box GF,
the area q-series and 44-digit certified μ and A on 08-17, after L5 was drafted.
Folding them in strengthens the paper and drags in the area-moment material,
where Richard arXiv:0704.0716 and Enting–Guttmann (1989) become mandatory
citations. Fold in and cite, or leave L5 as drafted and keep the salvage in
`results/`.

**How much of the tree is public.** A repo release makes this a real question
the journal plan never had to ask. `papers/` is gitignored copyrighted PDFs and
stays out. But `docs/` currently holds campaign briefs, postmortems, grading
records and the Ghost Ship tree — which is either the most unusual and
convincing thing in the repo or a large distraction, and I don't think that is
mine to judge. The viva files are already marked local-only.

## 6. What this does not change

Split-doc §1 — the two categories, the fixed disclosure blocks, the per-result
ledger — is untouched. So is §4's OEIS lineup and its rule that an entry may
cite a P-paper as warrant and never an L-paper. The OEIS submissions stay
exactly where they are in the queue.
