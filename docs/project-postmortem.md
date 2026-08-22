# Project postmortem — ten weeks, forty-one terms, and one idea that arrived last

2026-08-22, at jasonp's direction. Written after `docs/last-orders.md` closed.

**What this is and is not.** `docs/lessons-learned.md` already holds the
thematic account — the six failure classes, the verification culture, the
bestiary of computational bugs, the collaboration contract — and this file does
not repeat it. `docs/triangle-postmortem.md` holds the write-up of one specific
four-round failure. This file is the whole-project view, and it is organised
around the three things those two do not do: **the arc**, **luck**, and
**what transfers** to another attempt at a mathematical contribution.

Section 6 is action items. If you read one section, read that one.

---

## 1. The arc, in one page

| when | what |
|---|---|
| 2026-06-11 | first commit: scaffolding, the Redelmeier oracle, the campaign harness |
| 2026-06 | the transfer-matrix engine, 460 commits |
| 2026-07-03 to 07-04 | a(30) through a(34) land in about thirty hours |
| 2026-07-06 | **a(40)**. The enumeration ladder closes |
| 2026-07 to 08 | the analytic side: diagonal law, λ bracket, non-D-finiteness, ternary spine, below-onset defects; nine short papers drafted |
| 2026-08-17 | the literature-priority rule is adopted — after a result was found to be published |
| 2026-08-20 | **Undertow**, and **a(41)** the same day |
| 2026-08-21 | the Motley ladder lands: a(40) complete in all forty cells, a(41) second-sourced |
| 2026-08-22 | the pre-landing work list closed |

1,482 commits. Three home machines. The published frontier when this started
was n = 18.

## 2. What went well

**The gate suite is the single best decision in the project.** Thirty-three
gates, red-first, fail-closed, run before every push. It is not a testing
convenience; it is the reason claims in this tree can be believed. It caught
things on the last day of the project: a dangling citation in a file I had just
written, a residual-cell claim I had stated in prose instead of generating, and
the pinned-figure mechanism forcing a note to be updated when the table it
quotes changed. A gate that fires on its author is worth more than a gate that
fires on a stranger.

**Everything that mattered became machinery rather than advice.** This is
`lessons-learned.md` §1.2 and it held for ten weeks. The rules that stayed prose
got violated; the ones that became scripts did not.

**Correction in place, next to the claim.** The tree is full of struck
paragraphs, "WRONG, corrected 2026-xx-xx", and superseded readings kept with
their reasons. `results/confidence.md` ends by saying several of its own
session's characterizations were wrong and were corrected. That habit is why
the numbers can be trusted even though the descriptions around them moved.

**Negative results were banked as results**, with the counterexample that killed
each. `docs/lastditch-ideas.md` §6–§7 and `docs/skeletonkey-reprompt.md`'s
twenty-row table are the most valuable documents in the repo for anyone
continuing, and they exist only because kills were written down at the moment
they happened.

**Naming.** Undertow, Motley, Confetti, Ternary Spine, Kink Carry, Ghost Ship,
Skeleton Key, Coin Lift. Named things get remembered, cross-referenced, and not
re-derived. This is a small practice with a large return.

## 3. What could have been better

**The big one: the project optimised an implementation for two months before
questioning the rule the implementation was serving.**

The classical rule pins a diagonal level from its two *tallest* cells. Under
that rule, row 40's top two heights were three-quarters of the processor time
and took disk from 69 GB to 363 GB. Enormous engineering went into making those
cells reachable: kink carry, work stealing, spill formats, tmpfs experiments,
fleet scheduling, a 4.6× media win, a failed two-media plan.

Undertow says: **you never needed those cells.** Below-onset cells, corrected by
a defect that was itself derivable, are equally valid equations, and a level
needs only two. It arrived on 2026-08-20 — week ten of ten — and produced a(41)
the same day, on a sweep that stopped at height 19.

Nothing about Undertow required the hardware or the engineering that preceded
it. The below-onset defect mathematics was derived in the same project. The
grand form — "each level carries exactly two new constants" — was proved and
Lean-checked well before. **The lever was lying in the project's own results
directory.** What was missing was a pass that asked "what are we assuming we
have to compute?"

Everything else in this section is smaller than that.

**Priority passes came after drafting, not before.** The rule was adopted
2026-08-17, after a result was derived at length and found to be published.
By then nine papers existed; the passes ran retroactively and found that one
paper's central identity was Fortuin–Kasteleyn/Potts, another's square-lattice
column reproduced Asinowski–Barequet–Zheng, and a third's negative was weak.
None of that work was wasted, but some of it was spent.

**A gate that compares two derived artifacts cannot see a stale input.**
`make gate-provenance` regenerates the front-door table and fails if the
published note disagrees. On 2026-08-22 the generator still carried
`MOTLEY_H = 18` while the banked rows had held H = 19 for a day — so the table
and the note were stale *together*, and the gate was green. The fix was to
derive the constant from the banked row sets. The general lesson: **a gate must
compare against ground truth somewhere, or it only enforces internal
consistency.**

**Measurements lived on compute boxes.** The cell-sparsity result sat in
`~/var` on ayr for two days while three tracked documents promised the file. A
number that exists on one machine and nowhere in the repository is not a result
yet.

**Asserted prices propagated.** "~20–30 h, ~450 GB" for the H = 20 sweep was
written before anything was measured, then copied into three places; the
measured figure is ~10–11 h and ~185–190 GB. One of those three places was the
script's own header, which computed the wrong number two lines above the
correction rejecting it. An adversarial review caught it, which is the system
working — but a number should not be quotable until it is measured.

**Review queues went stale in the reader's favour.** The Undertow review queue
still read OPEN on rows the Motley ladder had answered. An open queue that
overstates what is unknown is a different failure from one that overstates what
is known, and it is the more forgivable — but it still misleads.

## 4. Luck

Distinguishing luck from skill in the record matters, because a method that
worked because the problem was kind should not be sold as a method that works.

### Where we were lucky

**The triangle had exact structure on its diagonals, and it was provable.**
Nothing guaranteed that `T(n, n−k)` would be a polynomial times `3^(n−1−3k)`
with a sharp onset. It is the fact the entire frontier rests on. Had the
diagonals been merely asymptotic, the closed-form tower would not exist and the
ladder would have stopped several terms earlier.

**The below-onset error was structured rather than noisy.** Undertow needs the
defect to be *exactly* computable. It turned out to be algebraic at depth 1 —
an irreducible quartic — and closable at depths 2, 3 and 4. If the defect had
been an ordinary asymptotic correction, the whole idea would have been worth
nothing.

**The machinery turned out to be lattice-generic.** The diagonal law holds on
every row-local lattice; the master equation is parametric in `b = |D|`. That
was not designed in — it was discovered late — and it is what made an external
validation channel possible at all (`results/undertow-square-validation.md`).
A project with no way to check itself against outside answers is in a much worse
position, and this one nearly was.

**A genuinely independent second algorithm existed.** The cut-count identity
gives a program that counts by colouring and *never decides connectivity*. Two
methods sharing no counting logic is the gold tier of evidence, and there was no
guarantee such a method existed for this problem.

**The sequence was under-explored.** The literature stopped at n = 18. Ten weeks
of home hardware would have bought nothing on a problem where the frontier was
already at 40.

**Three home machines were just enough.** dalby's 125 GB and 76 cores fit the
H = 18 and H = 19 Motley passes with room to spare — the H = 19 prime pass
peaked at 63 GB against 125. One hardware generation earlier, no.

**Two power cuts did not land on the long runs.** ayr is mains-exposed. One cut
on 2026-08-07 killed a perimeter run; the 22-hour ladder and the week-long a(40)
run were untouched.

### Where we were unlucky

**λ's upper bound is blocked by a barrier we then proved.** The measured
over-count of the certificate method is diffuse and *grows with n* — the
signature of a non-local constraint no finite window can see. So the entire
finite-type method class floors strictly above λ. That is not a tuning failure
and no amount of effort inside that class would have helped. The bracket
[6.543, 9.3154] stays embarrassingly wide around a value known to be 7.110.

**The sequence is not D-finite** — proved, unconditionally. It closes the
holonomic shortcut permanently.

**Every algorithmic lever hit the same wall.** New sweep axis, finite-lattice
method, MPS/boundary compression, holonomic accelerator, the 45° sweep, the
dual-connectivity transfer matrix, rank compression: seven independent ideas,
all measured dead, all against the fact that tracking connectivity is what
costs. The two genuine openings found — the characteristic-2 rank collapse and
the characteristic-0 Hankel room — are both **real and non-constructive**. There
is space under the floor and no known way to build in it.

**Several results collided with the literature after being derived at length.**
Ghost Ship's Layer 3 was in Richard arXiv:0704.0716; the minimum-site-perimeter
closed form was already A235382; L9's identity was Fortuin–Kasteleyn. Each cost
real work. The fix is in §6 and it is cheap, which is what makes these
unlucky rather than careless — but only for the ones that predate the rule.

**H = 21 was just out of reach.** Not by an order of magnitude — by a factor of
about two. The keys alone are 135 GB. A slightly larger machine changes the
project's whole shape.

### The one that is both

**Undertow arrived at all** — lucky. **It arrived in week ten** — unlucky, and
§3 argues it was not only luck.

## 5. Did it deliver?

Against the stated goal — extend A006770 past the published n = 18 — yes,
by twenty-three terms, with a(n) confirmed by two independent programs for
every n ≤ 41 and every cell of row 40.

Against the harder goal — a genuinely new way to count that reaches well past
n = 40 — no. The honest verdict from the project's own kill inventory is that
the three method classes are fenced: cut methods by an information floor with no
known construction, no-cut methods by λⁿ, and cancellation methods by the
absence of an explicit basis. That is a real answer to a real question, and it
is written down with the evidence, which is worth more than a vague "we tried".

## 6. Action items for the next attempt at a mathematical contribution

Ordered by expected value, not by effort.

1. **Budget an explicit "what are we assuming we must compute?" pass, early
   and repeatedly.** Put it on the calendar, not in the culture. The question is
   not "can we compute X faster" but "does the result actually require X". This
   project's single largest lever was found by asking it, in week ten. Ask it in
   week two, and again whenever a cost estimate crosses a threshold.

2. **Run the literature-priority pass BEFORE deriving, not before publishing.**
   The cost is minutes — an OEIS lookup, a targeted search — and the alternative
   is deriving something at length and finding it published. Adopt this on day
   one. It is the cheapest rule in this document.

3. **Design the external validation channel on day one.** Ask at the start:
   *what published number will this machinery reproduce that it did not
   produce?* Every internal second source shares your conceptual errors. This
   project got its external channel by accident, late, because the mathematics
   happened to be lattice-generic. Do not rely on that.

4. **Every gate must touch ground truth somewhere.** A gate that compares two
   derived artifacts enforces consistency, not correctness, and will stay green
   through a stale input. Derive constants from the evidence; never hand-edit a
   constant that a gate then checks against a note quoting it.

5. **A result is not a result until it is in the repository.** No measurement
   lives only on a compute box. Bank it the day it lands, with its provenance,
   or it will be re-derived or quietly lost.

6. **Never let an unmeasured number become quotable.** Mark estimates as
   asserted, in the text, and re-mark them when measured. Asserted prices
   propagate into plans and then into decisions; this project had one wrong by
   2–3× sitting in three documents.

7. **Keep a kill inventory as a first-class artifact.** Every dead end with the
   counterexample or the arithmetic that killed it. Its value compounds: it is
   what stops a fresh session re-deriving five dead ideas and feeling productive.
   Make it the entry point for anyone resuming.

8. **Apply an accounting test before opening a file.** Equations against
   unknowns; ansatz coefficients against available data; image size against the
   literature record. Most candidate ideas can be priced in a paragraph of
   arithmetic, and the ones that die there cost nothing.

9. **Distinguish a bijection from a reduction.** A map onto another class
   restates a counting problem; it does not reduce one. The image carries the
   same information however much published technology exists for the target.
   This killed a construction here that was correct, pretty, and survived two
   rounds of triage.

10. **Name the sentence that gets shorter.** Before starting any line of work,
    say which claim in the write-up improves if it succeeds. Work that shortens
    no sentence may still be worth doing, but it should be chosen knowingly.

11. **Write the collaboration contract on day one.** Ten weeks of friction
    converged on the rules in `lessons-learned.md` §6. They would have been just
    as correct in week one.

12. **Separate the lab from the publication from the start.** Two repos or a
    strict subtree. The cleanup cost at the end is real and entirely avoidable.

13. **Record luck as luck.** When a result depends on the problem being kind —
    exact structure where none was promised, a defect that happened to be
    algebraic — say so next to the result. It changes what a reader should
    expect the method to do elsewhere, and it is the first thing an outside
    reader will want to know.

## 7. For jasonp to write

`docs/lessons-learned.md` §7 already lists five [JP] sections and they are
unwritten. They are the half of this that a machine cannot supply: what the
project was for, whether it delivered that, the human-side counterfactual, the
viva experience, and the cost/benefit of ten weeks of hardware and of the
collaboration itself.
