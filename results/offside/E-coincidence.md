# Offside Lane E — the three judgement instruments, run by hand

2026-08-14. Lane B (`results/offside/B-adversary.md` §"The ceiling question")
argued the candidate design is capped at fidelity, and that *great* would mean
a render that computes judgement prompts rather than status. It named three
such instruments. This lane ran all three by hand over the corpus as it stands
and reports whether they find anything a human here had not already found.

Desk only, nothing executed. Method was `grep`, `ls`, `sed -n` to read line
ranges, and `git log` to date files. I did use `sort | uniq -c` to count
`grep -o` output for the constants sweep — coreutils over text, no project
code, no build, no fleet. Flagging it because the brief said grep/ls.

## Verdict first

**Instrument 1 (repeated constants) found nothing.** Not "little" — nothing.
Every distinctive repeated constant in the corpus is same-family, a shared
literature constant, already explicitly cross-linked in prose, or a false
positive. That includes its own motivating incident: the 5⁵/4⁴ recurrence had
already been explained in the tree a week before it "recurred".

**Instrument 2 (repeated obstructions) found one and a half real clusters.**
One is genuinely unnamed and cross-domain; one was discovered twice
independently, three days apart, by two notes that do not cite each other.

**Instrument 3 (settling-cost drops), as specified, found nothing.** But a
cheaper check sitting right next to it found three items, one of them the
single worst-aged row in the project's headline provenance artifact. That
check needs no schema, no TTL, no `what would settle it` field, and would run
on today's tree.

So Lane B's ceiling argument survives, but not its instrument list. The
finding that matters is in the last paragraph of §3 and in §5.

---

## 1. The best finding: `PROVENANCE.md` still says "none available"

`results/ns_a40/PROVENANCE.md:127`, the a(40) corroboration table:

| height band | share of a(40) | independent corroboration |
|---|---|---|
| H15-19 | **43.84%** | **none available** |

That row is the weakest thing in the a(40) close and it is the row a referee
reads first. It has been answerable since 2026-08-07.

`results/subgroup-mod4.md:6-9`, committed that day and gated as
`gate-subgroup`:

> **Headline: 820 cells of the a(40) triangle, 0 parity mismatches, covering
> 100% of a(40)'s mass — including the 43.84% band that had no second source
> at all.**

The corroborating file names the row, quotes its share, and says it covers
it. `PROVENANCE.md` contains **zero** occurrences of "subgroup", "mod 4" or
"mod-4" — I grepped. The citation runs one way only.

What makes this the top finding is not that it is stale. It is that the fix
is a table edit costing minutes, the evidence is already banked and already
gated, and the row it repairs is the one the project is most exposed on.
Seven days, and the two files sit four directory entries apart.

The honest caveat to carry into any edit, stated in `subgroup-mod4.md` and in
`HANDOFF.md:456-469`: this is a congruence-level second source, not an exact
recount — a wrong a(40) survives iff its error is 0 mod 4. The row should say
so. "Congruence-level corroboration, `results/subgroup-mod4.md`" is still
strictly shorter than "none available", and it retires the Tremblay–Vernay
external-enumerator ask in `results/resource-asks.md:58-73` as the cheapest
frontier-touching item on the books.

## 2. `triangle-snf.md` has been asking for something it was handed a month ago

`results/triangle-snf.md:102-105`, under **## Still open**:

> - Prove the ladder itself (G ≡ 1 mod 9; H ≡ W mod 3; S ≡ t²+tW mod 3) —
>   needs the cluster combinatorics of the cumulants.

`results/defect-gas.md` is the cluster combinatorics of the cumulants. Its
first commits are 2026-07-12, the day `triangle-snf.md` was last touched, and
it closes all three ladder items by name — `(⋆a)` DERIVED at :185, `(⋆b)` at
:162, `(⋆c)` CLOSED with a symbolic proof at :193 — concluding at :217:

> all three ladder items (⋆a,b,c) now stand on the defect gas **symbolically**
> — the ladder is retired as an empirical input in full.

`triangle-snf.md` contains no occurrence of "defect-gas". The second bullet
under Still open (individual 3-adic exponents `e_i(N)`) is correctly still
open, and HANDOFF lists it as such. Only the first bullet is stale, and the
fix is deleting it and pointing at `defect-gas.md` §(⋆a)/(⋆c).

## 3. `onset-defect-law.md` says "Nothing available"; Ridgeline answered it

`results/onset-defect-law.md:195`:

> **What would move this.** Nothing available. The bar is set by the
> correction tail at k ≤ 19, and `P_k` stops at 19.

and its limits ledger at :311, "The amplitude family is **verified only for
j ≤ 4** … 8 to 20 other simple rationals fit equally well."

`results/ridgeline-depth-amplitudes.md:16` (untracked, today):

> **The one-line answer to "35/8 or 118/27 at j = 5": 35/8.**

by derivation — a closed form for the depth tower plus a finite enumeration
giving α = 450/729 = 50/81 exactly — not by the longer exact data the blocker
assumed was required. `onset-defect-law.md` does not cite `ridgeline`.

I rank this third rather than first only because it is same-day and the
operator is inside it. It will age into item 1 if nobody edits the ledger.

**The shape these three share is the actual news of this pass.** None of them
is "a tool landed that made settling cheap", which is what instrument 3 was
specified to find. All three are: *a file states an open question or "nothing
available", the answer exists in a second file, and the second file cites the
first while the first does not cite the second.* That asymmetry is
mechanically detectable on the tree as it stands today — it needs no
`what would settle it` field, no TTL, no bet schema, and no migration. It is a
strictly cheaper instrument than the one Lane B proposed, and on this corpus
it is the only one of the three that paid.

## 4. Instrument 1 found nothing, and its own exemplar is a rediscovery

I swept `results/*.md`, `docs/*.md` and `docs/proofs/*.md` for every decimal
constant with four or more places appearing two or more times (≈120 distinct
values), plus every OEIS A-number (39 distinct), plus the quadratic-surd and
rational algebraic forms. Every repeat resolved into one of four buckets:

- **Same family.** The `μ_H` strip ladder values (3.4437, 4.1823, 5.1153,
  5.4178, 5.8404, 5.9916, 6.1158, 6.3800) recur across seven `strip-*` files
  because they are one table. 3.128943…, 2.309138…, 0.481008… recur across
  the convex/HV/middle-kingdom files for the same reason.
- **Shared literature constant.** 4.5252 appears in
  `results/concatenation-upper-bound.md`, `results/king-twigs-l1.md`,
  `docs/proofs/polyplet-upper-bound.md`, `docs/glossary.md` and
  `docs/rook-parity-bar.md` — it is Barequet–Shalah's polyomino bound, doing
  the same job in each.
- **Already cross-linked in prose.** The 3-adic cluster looked like the best
  candidate in the corpus: rate exactly 9 = 3² in the onset defect, the mod-3
  spine cubic, the mod-81 tower, the v₃ valuations. It is already wired.
  `results/defect-gas.md:71` has a section headed "**3-adic hook (Ternary
  Spine connection)**"; `results/onset-defect-law.md:246` says of 9 = 3²
  "That is the same measured fact in a different variable". Likewise A001207
  (a polyhex *control* in both places) and A308359 (the same corollary in
  both).
- **False positive.** 2511.00461 appears in `results/king-twigs-l1.md` and
  `results/triangle-r3-l6-wildcard.md` — two unrelated campaigns, which is
  exactly the signal shape the instrument hunts. It is arXiv:2511.00461. Any
  build of this instrument needs arXiv IDs, dates and line numbers excluded
  before it emits its first row.

Now the part that bears on the ceiling question. Lane B's motivating incident
is that the king-twigs bound landed on 5⁵/4⁴ = 12.207 on 2026-08-14, the same
constant as the crude bound in `docs/proofs/polyplet-upper-bound.md:36`, and
that a grep would have flagged it the day it happened.

It would have. And the operator would have already known, because
`results/strip-growth-lambda-bounds.md:281` — committed 2026-08-07, a week
earlier — says:

> "Injectively encode each object as (bounded-alphabet label per element) x
> (member of a countable simpler class)" is exactly the family our own bounds
> live in — the crude king-Eden `5^5/4^4 = 12.2` and the Bui-style convolution
> `9.3154` are both over-counts of this shape.

That is the unification the coincidence render exists to prompt, written in
prose, before the coincidence, and it is *stronger* than what the render would
emit: it names the mechanism (the encoding shape), covers a third bound the
render would not have grouped in, and draws the consequence (BBP's win came
from a structure theorem we lack). The instrument's flagship case is one where
a human beat it by a week.

I checked the one candidate that might have escaped: `1+√2` appears in
`results/exactchange-probes.md:220` as the spin engine's coloring-space state
count `~(1+√2)^H`, and separately across the strip corpus as `μ_2 = 1+√2`
exactly. Different indices (states per height vs. growth per cell), and 1+√2
is common enough in lattice combinatorics to sit near the brief's stated noise
floor alongside 3 and 9. I record it as a weak candidate, not a finding.

## 5. Instrument 2: one unnamed cluster, one discovered-twice cluster

### 5a. Half-named: the closure that killed our own instrument, not the object

Eleven closures where what died was an artifact of our own representation,
fit, gate or proxy — not a fact about polyplets. Each is filed as though a
research route had been tested.

| file:line | thread | what was actually killed |
|---|---|---|
| `docs/rook-parity-bar.md:1`, `HANDOFF.md:227` | rook parity r1 | the goal's √3 pin sits below what the incumbent already measures |
| `results/v5-denominator-law.md:3` | v5 denominator law | "a fact about our representation, not about polyplets" — its own words |
| `results/coin-lift-g2.md:24` | Coin Lift G2 gate | the gate as written can never fire; Z/4 free rank ≡ the banked GF(2) rank |
| `results/completion-oracle.md:39` | completion-prune headroom | the prior audit's 79% proxy was never headroom; perfect prune buys ≤1.037× |
| `results/r4/r4-floors.md:12` | round-4 floors | two of three self-authored impossibility floors wrong or over-applied |
| `docs/rook-parity-bar.md:56` | gate 0 | measured the full weight DP; the route needs two constants per level |
| `results/map-body-profile.md:20` | arena allocator | the audit mis-estimated the target (2/3405 samples) |
| `results/perf-outcomes.md:36` | counts pool | the headline 14% was a single-process leaf-sample artifact |
| `results/terminal-velocity.md:20` | terminal velocity | the branch-miss hypothesis was ours, not the machine's |
| `results/strip-growth-lambda-bounds.md:232` | implicit trial vector | "I had the bottleneck wrong" — it saves ψ; ψ was never the constraint |
| `results/convex-polyplets.md:1` | convex re-derivation | re-derived, worse, a deeper note already banked |

**Already named?** Half. `docs/lessons-learned.md` §4 carries "Measure, don't
reason" and "Grep before claiming new" as *practices*, and names two instances
(convex polyplets, the Temperley GF). `docs/triangle-postmortem.md:43` treats
it for one campaign. `HANDOFF.md:290` is the closest thing to the general
statement — jasonp's own "the actual failure was target selection **again**"
— and the "again" points at nothing.

What is unfiled is the count and the crossing. Nobody has put the perf-side
instances (`map-body-profile`, `perf-outcomes`, `terminal-velocity`,
`completion-oracle`) next to the math-side ones (`v5`, the G2 gate,
`r4-floors`, the rook goal) and observed they are the same mistake. Eleven, in
two domains that never cite each other, against a practice list that names
two. That is a real gap, and it is the one thing in this pass that supports
Lane B's argument on Lane B's own terms.

Honest discount: this cluster is a *process* finding, not a mathematical one.
It changes how briefs get audited, which is what
`docs/rook-parity-team-process.md` already exists to do. It would not have
produced a theorem.

### 5b. Discovered twice, three days apart, uncited: a control that also fails

The rule is: *a test that a known positive also fails cannot close a thread.*
Two notes found it independently and neither cites the other:

- `results/band-structure-probes.md:132` — the mod-m test detects periodicity,
  not automaticity; Catalan, a known 2-automatic sequence, passes straight
  through. The question is not closed and cannot be closed on banked data.
- `results/strip-spectrum-defect-rate.md:73` — float root extraction rejected
  at H=8 **by its own control**.

And the same mechanism, unlinked, in five more places:
`results/hv-growth-sandwich.md:872` (PSLQ boxes bounded by PSLQ's own cost,
"cannot become conclusive"); `results/nu-exponent.md:3` (5% off, drifting, no
more terms — evidence neither way); `docs/onset-defect-plans.md:119` (family
"excluded outright, **missing its own control floor**");
`results/triangle-r3-l4-quotient.md:339` (more terms only enlarge the
exclusion box); `results/stretched-exponential-test.md:19`, which is the
repair case — differential approximants are structurally blind to μ₁^√n, so a
banked θ had been resting on a blind instrument until this ran.

`results/countable-subpopulations-criterion.md:56` states the limitation
squarely — "No family here has a *proof* of no closed form; every negative is
an exclusion box" — but only for the GF-class family. "Exclusion box" is real
shared vocabulary in that corner and nowhere else. The constant-fitting,
exponent-fitting, arithmetic and control-failure cases are never gathered with
it. `docs/lessons-learned.md` §2–3 treats control calibration as hygiene for
trusting **positives**; the mirror rule for negatives is unwritten.

This is the cluster I would actually write down, because unlike 5a it has a
one-line statement and it would change what a lane is allowed to claim.

### 5c. Weaker, reported for audit

- **Compression floors across three sub-projects.** The incumbent frontier
  already sits near the object's entropy, so re-representation pays a
  constant-factor penalty: `results/boundary-push-tensornetwork.md:11` (MPS
  0.26–0.45× worse, 2026-07-11), `results/triangle-r3-synthesis.md:150,156,160`
  (three routes), `results/coin-lift-g2.md:58` ("no compression at all",
  2026-08-14), `results/rook1/R1-D.md:114` (β ≥ 1.244 counting floor),
  `results/completion-oracle.md:51`. Round 3 coined "state floor" and
  "information floor" for its own three lanes only; `coin-lift-g2.md` cites no
  prior compression negative six weeks later. Real, but each instance is
  honestly priced in place and the generalization would not have changed a
  decision.
- **Ladder economics** (multiplicative cost per rung against additive payoff):
  seven instances, all correctly priced individually, `docs/rook-parity-bar.md`
  even formalizes the comparison as `b` vs `g`. Not news.
- **The connectivity wall** is already named as a single obstruction with its
  own doc (`docs/open-problem-lambda-bracket.md`) and memory entry. Not news —
  with one unlinked face worth a line:
  `results/triangle-r3-involution.md:12`, where move-validity is a global
  connectivity predicate so a validity-aware site key drifts under its own
  move. That is the wall showing up in involutions rather than in bounds or
  engines, and no file connects it.

## 6. Byproduct: a check cheaper than all three of them

`results/rook1/R1-D.md:114` cites `docs/rook-parity.md:38` for the λ_k ≥ 6.543
certificate. `docs/rook-parity.md` does not exist — it is the operator's own
pending deletion, recorded at `HANDOFF.md:66`, and R1-D cites it with a line
number.

Dangling in-tree path citations are greppable in one pass, need no schema, and
fail closed. Neither Lane B's instrument list nor the candidate design
contains this check, and it is cheaper than any of them. Filed as a queue row
rather than a finding, since this instance is a known in-flight edit.

## 7. Does the ceiling argument hold?

Yes, in a modified form, and the modification matters.

Lane B's claim was that a fidelity system is capped, and that great means a
render computing judgement prompts. This pass supports the first half and
substantially revises the second.

**Against Lane B:** the constants instrument — the one it led with, the one it
priced at twenty lines — returns zero on this corpus, and returns zero
including on its own exemplar, which a human had already unified a week
earlier and better. Instrument 3 as specified also returns zero. If those two
were the evidence that great is reachable, the evidence is weaker than the
argument.

**For Lane B:** the obstruction instrument found a genuine unwritten rule
(5b), and something adjacent to instrument 3 found three real stale-open
items, one of them sitting on the a(40) provenance table for a week with the
answer banked and gated four directory entries away.

The revision: **the thing that pays is not coincidence detection over content,
it is asymmetry detection over citations.** All three of §1–§3 have the same
shape, and so does §6. A file asserts an open question or a missing source;
another file answers it and says so; the citation runs one way. That is
findable with grep on today's tree, it needs nothing the candidate design
proposes to build, and it does not depend on the agent being clever about what
counts as a distinctive constant. It also degrades gracefully — a false
positive is a pair of files to glance at, not a wrong claim.

So the honest ceiling statement is narrower than Lane B's and more useful:
this family can exceed HANDOFF, but the mechanism that gets it there is a
one-way-citation sweep, not a coincidence render, and that sweep is available
now, standalone, alongside item 7 — with no schema, no TTL, and no migration.

Lane B's hard cap stands untouched: every one of these surfaces to the same
person. This pass produced three edits and two write-ups for one operator, and
found them in an afternoon.

## Weakest items in this file, conceded

- §5a's eleven-member cluster is inherited from a delegated sweep. I verified
  four members against the tree (`v5-denominator-law.md:3`,
  `coin-lift-g2.md:24`, `r4/r4-floors.md:12`, `HANDOFF.md:290`) and the
  claim that `lessons-learned.md` does not name the class. The other seven are
  reported, not confirmed.
- §4's "nothing" is bounded by my regex: decimals with ≥4 places, A-numbers,
  and hand-listed surds. A constant written only as a fraction in two
  different reduced forms would have escaped it. That is a real hole and it
  cuts *toward* Lane B.
- §1–§3 are three joins, not a rate. Whether one-way-citation sweeping pays
  depends on the false-positive rate over the whole corpus, which I did not
  measure and which is the first thing to measure before anyone builds it.
</content>
