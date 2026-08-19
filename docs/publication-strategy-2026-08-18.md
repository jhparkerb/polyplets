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

- A genuine clean-clone run on ayr or dalby. **Run 2026-08-18 on ayr**
  (`scripts/clean_clone_check.sh`), and it broke in three places the working
  tree hid: the citations gate was judging against 50 local refs a clone does
  not have, four translation units do not compile under GCC, and the term
  runner started with `cd ~/src/polyominoes`. All three fixed. What the item
  still wants is the documented command that reproduces a term from nothing,
  with a measured cost against it.
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
closure 33 → 35 <!--q:closure_n@17=33--><!--q:closure_n@18=35--> → 37
<!--q:closure_n@19=37-->, and row 40's residual band shrinking with it. The
counts and the cells are generated in `results/residual-cells.md`.
Runs alongside Track A without competing for anyone's attention.

**Track C — the L papers.** Nine now, not six: L7 was carved out of L5, and L8
and L9 were written on 2026-08-18. Release order stays L3, L1, L4 first: clean
novelty verdicts, and warrants a stranger can re-run in exact arithmetic, which
is exactly the kind of paper that survives having no
referee. The priority passes are done -- all nine, 2026-08-18,
`docs/priority-passes-2026-08-18.md`. What each still needs is enough reading
from jasonp to replace "human verification: none" in the ledger with a specific
line; then it goes in the repo with the rest.

**Track D — P1, after the provenance table exists.** The 30–50 hour estimate
stands and most of it is the engine chapter and §Reproducibility. Writing
§Reproducibility before the table exists means writing it twice. Under a repo
release P1 is also allowed to be shorter than a journal version would be: it can
point at the tree instead of reproducing it.

Then P2, P3, and the analytic papers.

## 4. Per-paper state and gate

| | paper | drafted | gate before it goes public |
|---|---|---|---|
| **L3** | λ bracket 6.543 ≤ λ ≤ 9.3154 | yes, 14pp | pass done 08-18, no collision on the king constant; certificates regenerate on a clean box; **9.3154, never rounded back** |
| **L1** | diagonal law | yes, 15pp | pass done 08-18 |
| **L4** | not D-finite | yes, 11pp | pass done 08-18 (nothing re-searched since its own sweep) |
| **L2** | mod-3 arithmetic | yes, 10pp | pass done 08-18, no collision on the spine cubic, the digit product or the SNF count; Rowland–Yassawi cited as the adjacent method |
| **L5** | convex polyplets | yes, 18pp | Gouyou-Beauchamps–Leroux cited in three places, every revision; Richard arXiv:0704.0716 in three more. See §5 |
| **L7** | subdominant exponential, amplitude ratio | yes, 11pp | same attribution, two places; the sharp-asymptotic conjecture stays labelled a conjecture |
| **L6** | perimeter gradings | yes, 11pp | compute gate **cleared**; cites the ANALCO text, and hands the degree column back to Asinowski–Barequet–Zheng as their conjecture |
| **L8** | below the onset | yes, 8pp | pass done 08-18 and the paper says on page 1 why the negative is weak |
| **L9** | the cut-count identity | yes, 6pp | **the identity is not new** — Fortuin–Kasteleyn/Potts in scan order; claims no theorem |
| **P1** | fixed polyplets through a(40) | 40% | Track A |
| **P2**, **P3** | — | not started | his prose; P3 additionally on the `hv-growth-sandwich` reading gate |

Every L ledger currently reads "human verification: none", and every L paper
carries a loud draft banner saying so. A repo release can honestly ship a draft
banner in a way a journal cannot — but then the banner has to be true, and
"none" across nine papers is a weaker position than "statements read" across
three. This is the one gate on the L side that no amount of machine work
closes.

## 5. Open decisions

**L6, L5, L7 — done, not decisions.** All three were rewritten on 2026-08-18
and the two questions this section originally posed are answered. L6's compute
gate cleared: three of four k = 6 predictions held, the Φ₂ closed form was
refuted and withdrawn, and the universality claim now runs through k = 6. L5
folded in the salvage with Richard and Enting–Guttmann cited in three places,
and L7 gained the kernel mechanism for its measured spectrum. Two new papers
were written for material that had no home: **L8** (the below-onset defect
campaign) and **L9** (the cut-count identity behind the second source).

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
