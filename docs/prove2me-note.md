# Prove2Me: what to borrow, what not to buy

2026-09-04. A note, not a plan. Triggered by Anthropic's announcement that
Claude produced an end-to-end Lean proof of Fermat's Last Theorem; the
question asked was whether the tooling behind it advances this repository's
open Lean work. Decision: **take the architecture, do not join the platform,
do not start the formalization yet.**

## 1. What was announced

Anthropic, 2026-09-04 (`anthropic.com/research/formalizing-fermats-last-theorem`,
repo `github.com/anthropics/fermats-last-theorem`): full FLT via the
Frey-curve / modularity-lifting route, following Darmon-Diamond-Taylor — not
the regular-primes special case. ~13M lines of Lean, 30,300 theorems proved
(29,500 in the final cone), 60,475 modules, all kernel-checked, no `sorry`,
only Lean's three standard axioms, with a comparator tool confirming the top
statement matches Mathlib's FLT statement. Roughly 11 days, led by Tianyi
Peng, ~6 billion output tokens from an internal research model. Kevin Buzzard
reviewed after the fact and signed off.

Cost of entry, stated plainly: six billion output tokens. That number is the
whole reason the rest of this note is about structure rather than scale.

## 2. Prove2Me splits into two things

**The architecture** (arXiv 2608.28433; workspace repo
`github.com/prove2me/prove2me_workspace`):

- Immutable theorem objects — description, preamble, formal statement ending
  `:= by sorry`. Stated once; many proofs may target one statement.
- Statements and proofs in **separate files**, so a proof attempt compiles one
  leaf rather than a chain.
- Decomposition by proof-sketch: a proof may import *open* theorems, which is
  what makes the dependency DAG.
- A natural-language description on every statement, indexed for search; agents
  are instructed to search before they write.

**The platform** — `prove2.me`: server-side kernel verification
(`POST /api/v1/verify`), account plus a 30-day API key, a public corpus
("Formalpedia"), other people's agents, a leaderboard. Missions start as
draft proposals and go public only on moderator launch approval.
`GET /api/v1/missions` is auth-gated: there is no browsing before registering.

## 3. How FLT actually used it

Privately. Buzzard's own account
(`xenaproject.wordpress.com/2026/09/04/flt-anthropic-has-beaten-me-to-it/`)
is that he learned of it after completion — emailed by Anthropic, assumed
spam, read it a week later — with no community visibility during the eleven
days and no outside contributors. He is explicit that it is not the proof his
Imperial project is formalizing.

The contrast is in Anthropic's own wording: the Vinogradov three-primes side
experiment is the one "collaborating entirely through Prove2Me," on three
consumer Claude Max plans. FLT gets "Prove2Me and a Claude Code-based
multi-agent harness." The three missions the Prove2Me paper reports as public
(exact matrix completion, bandit algorithms, Sipser-Gacs-Lautemann, mid-June
to end-July 2026) do not include FLT.

So the platform was used for its harness, not its collaborative surface. That
is the mode this repository would want, and it is available without the
platform.

## 4. What is worth adopting here, at no external exposure and no new spend

1. **The compile split.** Statements in one module, each proof in its own, so
   a failed attempt rebuilds one leaf instead of everything downstream. Failed
   round-trips are where Lean agent tokens go — the model re-reads errors it
   caused three files away. This is a token saving, not a token cost.
2. **A generated declaration index.** Docstring plus signature over
   `Polyplets/` (77 files) and the mathlib declarations actually imported, so
   an agent greps a small local index rather than scanning mathlib's 8169
   files to rediscover a lemma already in the tree. `docs/lean-environment.md`
   §4 hand-codes this as recipes; generating it makes a repeated expensive
   scan cheap. Also a saving.
3. **Immutable statements, audited once.** A statement is written, read
   against the source document by jasonp, then frozen. The expensive failure
   in agent formalization is not a hard proof; it is an agent quietly
   weakening a statement until it goes through, and everyone re-reading it
   afterwards.

What is *not* available for free is the part that made FLT work: many agents
in parallel. One subscription is one agent, better organised.

## 5. Two claims not to be taken at face value

- **The server verification is not a stronger check than ours.** It is the
  same Lean kernel. `lake build` on dalby plus the `#guard_msgs` axiom pins of
  `Polyplets/Grand/Audit.lean` is the identical check on our own hardware. The
  only thing prove2.me adds is that a third party ran it — provenance, not
  correctness.
- **Faithfulness auditing is still human.** The Prove2Me paper puts automated
  faithfulness auditing at ~43% accuracy and says human audit remains
  essential. A proof that type-checks against the wrong statement is the
  failure mode, and no server catches it.

## 6. Status of the work this would serve

Unchanged and unstarted. `docs/proofs/cutcount-identity.md` §10 names
formalizing Lemmas 1-5 and the main identity as a scoped target, and §8
concedes it is a paper proof against a development whose own standard is
"every cell a real kernel-recorded theorem." Tier 2 of
`docs/b1-closure-plan.md` §7 — that the window DP realises the sum — is the
larger follow-on and encodes the engine's actual rule.

Neither is started. Structure of the kind in §4 moves the cost of that work by
perhaps a third, not by an order of magnitude, and nothing announced today
makes it urgent. It has been open since 2026-08-14 and it stays open until
jasonp decides to spend on it.

## 7. Not doing

- No prove2.me account, no API key, no proposal draft, no upload of any
  statement from this tree.
- No second subscription.
- No agent fan-out on the Lean target.
