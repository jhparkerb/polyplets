> **NOTE: authored by Claude at jasonp's direction, 2026-08-08.** Brief for the
> LLM-tic sweep over the six L papers, compiled from web sources on the tells
> of machine-written prose. The sweep's findings ledgers sit beside this file.

# The tic catalog

Sources: Wikipedia's "Signs of AI writing" (WP:AISIGNS); "Why does ChatGPT
delve so much?" (21 focal words, arXiv 2024); Kobak et al., "Delving into
LLM-assisted writing in biomedical publications through excess vocabulary"
(arXiv 2406.07016); Reissmann, "Contrastive negation used to be a rhetorical
device"; Liang et al. on formulaic-expression spikes (arXiv 2505.12218);
assorted 2025-26 wordlists (TextSight, Walter Writes, Alston Antony).

**The bar is set very low, at jasonp's instruction: log every candidate, even
ones kept.** A finding costs a ledger row; a miss costs the pass its point.

## A. Contrastive negation / negative parallelism

"It's not X, it's Y." "Not just X but Y." "X is not merely A; it is B."
"No A, no B, just C." The single most reliable structural tell. BUT: in these
papers many not-X-but-Y contrasts are *epistemic substance* — "measured, not
proved" is a disclosure the authorship split requires, not a flourish. Fix the
rhetorical ones; KEEP the load-bearing ones and say why.

## B. Focal vocabulary

delve, intricate, tapestry, testament, landscape, realm, pivotal, crucial,
meticulous, robust, seamless, compelling, paramount, vibrant, boasts,
underscore/underscoring, highlight/highlighting, showcase/showcasing, foster,
leverage, harness, navigate, elevate, surpass, resonate, interplay, enduring,
unwavering, garner, notably/importantly/interestingly/crucially as sentence
openers. In a math paper most of these have plain substitutes or delete clean.

## C. Copula avoidance

"serves as", "stands as", "marks", "features", "represents", "acts as" where
"is" does the work. Math prose says "is".

## D. Rule of three, adjective stacks, elegant variation

Triads deployed for rhythm rather than because there are three things.
Rotating fancy synonyms for one object to avoid repeating its name — math
prose repeats the name.

## E. Editorializing and -ing trailers

"plays a crucial role", "valuable insights", significance inflation, and the
superficial participial trailer: "..., highlighting the depth of the method",
"..., underscoring its importance". The trailer usually deletes whole.

## F. Em-dash asides and punctuation habits

Paired-dash asides that exist for rhythm (phase 5 of the trim already took
some; sweep what remains). Boldface for emphasis. Title Case headings where
the paper's own style is sentence case.

## G. Precious noun phrases / decorative metaphor

"sits at the heart of", "does the heavy lifting", "a window into", "the story
of", "the beauty of", one-off decorative metaphors. DISTINGUISH: this
project's *established coined terms* (the spine, the ladder, kink carry, the
squeeze — defined once, used consistently, load-bearing) are house style, not
tics. A metaphor used once for decoration is a tic; a term the paper defines
and computes with is vocabulary.

## H. Scaffolding and meta-prose

"It is worth noting that", "In essence", "In conclusion", "Taken together",
"To summarize", "Let us now". ("Note that" and "Observe that" are ordinary
mathematical usage — flag only when stacked.)

## I. Hedging doubles and templatic framing

"may potentially", "could possibly"; "existing methods often", "recent
advances in". 

# Hard constraints on the sweep

- Only `paper/L1-…L6-*.tex`. Nothing else.
- NEVER touch: `\Ldisclosure` blocks and their ledgers; the draft banners (L2
  novelty, L6 compute-gated); L5's three attribution sites (`rem:attr1`,
  `rem:attr2`, `sec:related`'s opening paragraph); L1's erratum/notsquares
  remark; any `\cite`, `\ref`, `\label`; any number, constant, or math-mode
  content; the pinned literals (`CONSTANTS` in `scripts/l_trim_gate.sh`).
- Meaning preservation is absolute: same claim, same scope, same epistemic
  status. When in doubt, KEEP and log why.
- No paper may grow in words; prefer strictly shorter.
- Every edit: verify the OLD text is unique in its file before replacing; log
  OLD → NEW verbatim in the findings ledger.
