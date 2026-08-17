# Ghost Ship — value triage

2026-08-17. `REPORT.md` graded the loop's **hygiene** (is each claim true,
is there a receipt, did it re-derive banked repo content). It did not ask
whether any of the output is **new** or **worth keeping**. This file does,
on the four headline layers of
`grading/run-record/sandbox/results/FINAL-SYNTHESIS.md`.

Not a regrade. Different axis, run after the fact, with tools the sandbox
did not have: a working OEIS search and the literature.

## A. OEIS novelty claims — CONFIRMED (independently, not repaired)

**Corrected 2026-08-17 after reading `reports/session-01.md`.** This section
first said the loop's `/search` was Cloudflare-blocked and its novelty
claims therefore rested on a crippled search. That is false, and the source
of the error is itself a finding — see §F. The loop had a working search
from session 01 and used it through session 05. What follows is an
independent second search, not a repair.

Pipeline validated on the control family first: `1,2,7,28,120,528,2344,10416,46160` → **A005436** (convex polygons
by perimeter), exact hit. So a real hit would have been found.

All four king sequences return zero results, both at full length and at
shifted 4–6 term prefixes (to catch offset-shifted entries):

| sequence | prefix | result |
|---|---|---|
| king convex semiperimeter | 1,2,9,36,154,668,2916,12740,55570,241692 | absent |
| twist b(s) | 2,5,20,81,344 | absent |
| king convex area (60 exact terms) | 1,4,16,61,221,766,2566,8390,26982 | absent |
| directed-convex king by area | 1,3,10,33,107,342 | absent |

**Disposition: the loop was right, on its own working search.** Four new
sequences plus the certified constants (q_c, mu, A, A_dir,
and a control amplitude for A067676) are submission-grade material.

## B. Three cross-family identifications — REAL, and new to the target entries

Verified against the live entries (name, data, comments, formulas):

- `a_dir(s) = A014300(s−1)` — A014300 is "nodes of odd outdegree in all
  ordered rooted trees with n edges". Its comment field carries Catalan
  noncrossing-partition, central-binomial/Fine convolution, unimodal
  function, and binary-fraction interpretations. **No polyomino, convex,
  king or polyplet interpretation.**
- `d(n,n) = A112029(n−1) = Σ_k C(n−1+k,k)²` — pure binomial-sum entry,
  Kotesovec asymptotics, Bala congruences. **No combinatorial geometry.**
- `N_h(1) = A153337` (zig-zag path counts), proven at GF level. **No
  polyomino interpretation.**

**Disposition: OEIS-comment-grade, three entries.** Loop verified all three
against b-files; I confirmed the entries carry nothing equivalent. (Any
submission is gated behind the viva, as ever — noted, not proposed.)

## C. Layer 3 area-moment limit law — SUPERSEDED BY LITERATURE

The load-bearing finding of this triage.

Christoph Richard, *Limit distributions and scaling functions*
(arXiv:0704.0716), Table 1 and the accompanying remark: rectangles have
area limit law **β₁,₁/₂**, density `p(x) = 1/(2√(1−x))` on [0,1], and
"**a model with the same area limit law as rectangles is convex
polygons**" (his ref [87]). Rectangles of semiperimeter m: normalised area
`4U(1−U)`, U uniform.

The loop's Layer 3 headline is
`E[area^r]/s^{2r} → (r!)²/((2r+1)!·2^r)`, i.e. `area/s² → U(1−U)/2`. That
moment sequence is exactly `E[(U(1−U)/2)^r] = 2^{−r}·B(r+1,r+1)` — the same
beta law, differing from the rectangle statement only by a factor 2 in the
normalisation (box-fill convention, or looseness in Richard's "same law";
unreconciled, and not worth reconciling unless the item is pursued).

So the `c_r = (r!)²/2^{r+7}` law, and the limit law it implies, **re-derive
a published result** for the control family.

This is not a failure of the grading — the rubric checked re-derivation
against *our repo*, where the count of 0 stands. The sandbox had the 21
shipped files and no literature. Neither arm could see this.

Cost: sessions 09, 11, 12, 13, 14 are largely this line of work, and
include the run's three most expensive sessions (s09 17.5M, s12 21.1M,
s13 12.0M tokens — a third of the run's 91.13M by itself).

What survives the collision:

1. **king ≡ polyomino universality**, stated explicitly and checked to
   r ≤ 12. Once the law is known to be a bounding-box/shape effect this is
   unsurprising, but it is not in Richard.
2. **Moment-GF algebraicity for every r** via the shared kernel
   (`docs/proofs/area-moment-kernel.md`) — a structural theorem about the
   GFs, not about the limit; Richard makes no such statement.
3. The **local transfer / inner-chart derivation** as method.

All three are real but far thinner than `FINAL-SYNTHESIS.md` reads.

## D. Layer 1 — box/semiperimeter algebraic GF: NO COLLISION FOUND

Searches over the convex-polyomino enumeration literature (Delest–Viennot,
Bousquet-Mélou, Lin–Chang, k-convex, directed k-convex, column-convex,
Carlitz, honeycomb and symmetry-class variants) surface nothing using
**king adjacency**. The family's absence from OEIS corroborates — coverage
of convex-polyomino variants there is dense.

**Disposition: highest-confidence new result of the run**, and it lands
directly on `results/convex-polyplets.md`, an OPEN side-quest. The explicit
closed form `F = −(M + 2x²y²(1+x+y)²√Δ)/(2KΔ²)`, `Δ = (1−x−y)²−4xy`,
`K = x+y+xy`, derived by kernel method with no fitting in the final chain,
is the piece to import.

## E. Layer 2 — q-series closed form, certified asymptotics,
## non-D-finiteness: NO COLLISION FOUND

The Temperley/q-functional-equation machinery is classical (Bousquet-Mélou
q-Bessel); its application under king adjacency is not in evidence
anywhere. The certified constants (mu = 3.128943269730886…,
A = 0.974452213135004…, 44+ digits by exact-rational interval arithmetic)
are new by construction, the sequence being new.

The striking item is the non-D-finiteness route: K(q) with ≥40 located real
zeros accumulating at q=1 under
`K(e^−ε) ≈ 2·3^{1/4}√(ε/2π)·cos(V/ε − π/12)`, `V = 2Cl₂(π/3)` the
Gieseking constant / figure-eight complement volume. No collision found;
this is Zagier quantum-modularity territory, and the mechanism there is
well-studied even if this instance is not.

**Disposition: most interesting, weakest rigor.** The loop scoped its own
gap correctly (rigorous steepest descent for the oscillation law; residue
nonvanishing at infinitely many zeros). Keep as a lead, not a result.

## F. A false banked fact, lost at a session boundary

Found while reading `reports/session-01.md`; not part of the novelty pass,
but the most legible defect in the run.

Session 01 hit the Cloudflare challenge on a bare `curl` to `/search`,
**solved it in the same session** with a browser User-Agent, and logged both
queries verbatim (lines 94–97). The workaround was then used continuously:
s02 (A153337), s03 (A014300, A112029 and `id:` lookups), s04 (seven
searches plus two b-files), s05 (five, including constant lookups).

Session 06 ran `curl` **without the `-A` flag**, hit the challenge, and
banked:

> `DEAD: ... note OEIS SEARCH is Cloudflare-blocked for curl — use b-file
> URLs (oeis.org/Axxxxxx/bxxxxxx.txt), which work.`

s07 repeated it as fact. It reached the capstone unchallenged, where
`FINAL-SYNTHESIS.md` lists "OEIS /search endpoint via curl
(Cloudflare-blocked — b-file URLs work)" under **Dead ends (do not retry)**.

So the run's own capstone carries a false infrastructure claim, refuted by a
log five sessions earlier in the same document series, and it was persuasive
enough to mislead this triage on first pass.

Why grading missed it: the claim table grades CARRY claims. DEAD lines are
not claims under the rubric, so a false one is invisible — and a false DEAD
line is the expensive kind, because it removes a capability from every
successor.

This is the **fourth** instance of the failure family `REPORT.md` names as
session-boundary handoff (three job-relaunch instances, s11–s14), and the
cheapest to describe: a working technique lost at a boundary, re-recorded as
a property of the world. Any second run needs DEAD lines inside the graded
grammar, and a successor rule that re-tests an inherited infrastructure
negative before honouring it.

## Net

| item | disposition |
|---|---|
| 4 new sequences + certified constants | KEEP — novel, verified |
| 3 OEIS identifications (A014300 / A112029 / A153337) | KEEP — new to those entries |
| Layer 1 box/semiperimeter algebraic GF | KEEP — best new result; import to convex-polyplets |
| Layer 2 q-series + certified asymptotics | KEEP |
| Layer 2 non-D-finiteness / Gieseking | LEAD — firm empirical, rigor gap scoped |
| Layer 3 limit law + c_r law | SUPERSEDED — known (Richard 0704.0716) |
| Layer 3 moment algebraicity for all r | KEEP (narrow) — structural, not in Richard |

Roughly two genuinely new results, three OEIS comments, four sequences —
and the most expensive third of the run spent re-deriving a published
limit law.

## Consequence for the experiment design

The rubric's headline "0 unwitting re-derivations" is scoped to the repo.
Against the **literature** the loop re-derived a published result at
something like a third of its budget, and neither the loop nor the grading
could have seen it: the sandbox ships 21 files and no library, and the
grading rubric never asks the question.

A sealed sandbox cannot avoid this failure mode. Any second run needs
either literature access inside the sandbox (which weakens the blind) or a
literature-priority pass added to grading (cheap — this triage was under an
hour). Absent one of the two, an unattended loop's cost-per-new-result is
unmeasurable, and the rung ladder measures the wrong thing regardless.

This defect is larger than the untested bulletin. The §F regression is a
second, independent argument for widening the rubric: it grades what the
loop asserts, not what the loop concludes it cannot do.

## Method

OEIS: read-only JSON API from gympie, control-validated before use.
Literature: search plus `ar5iv` full-text read of arXiv:0704.0716. Sources
recorded inline above. No claim here re-verifies the loop's mathematics —
`grading/verify-{A,B,C}.md` already did that, and this file takes those
verdicts as given.
