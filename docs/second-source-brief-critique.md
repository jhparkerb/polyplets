# Critique of the "second algorithm for T(n,H)" team brief

2026-08-11. The brief as written is well-constructed as a research-team prompt
— the literature split is clean, the kill-list-is-a-deliverable rule and the
citations gate are right, the probe time-box is right. What it gets wrong is
almost entirely *repo state*: it asks for something that partly exists, states
a target that this project's own warrant scale cannot grant, and hands down
two constraints as settled that are not.

Corrections below, then a corrected brief in §B.

---

## A. Corrections

### A1. A second algorithm already exists, and its coverage is measured

The brief opens "we need a second algorithm that can verify either T(n,H) or
a(n) directly." One is built, run, and banked: the strip transfer matrix
(`results/strip-engine.md`, `cpp/strip_tm.cpp`), a whole-column
connectivity-partition sweep sharing no code, frontier, or state encoding with
the kink kernel that produced the banked triangle. Its N=40 run completed
2026-07-30: **469 cells, 0 mismatch, H ≤ 14 at every n ≤ 40**.

So the target is not "get a second source." It is a named, measured *residue*:

| region | status |
|---|---|
| H ≤ 4 | closed by exact recurrences |
| H ≤ 14, all n ≤ 40 | strip-confirmed (469 cells) |
| H = 15..21 | **kink-only** — the real swept tall heights, no second source |
| diagonals k = n−H ≤ 18 | P_k closed forms; a closed form is not a second source for a cell it generated |

Honest cell coverage is **72.2%** (592 of 820 cells, `results/strip-engine.md`
§Coverage); the remaining 228 cells are the job. By mass the residue is
larger than the coverage: the strip run reaches **45.0%** of a(40), 47.9% of
a(39), 50.8% of a(38), 53.8% of a(37) — so **over half of a(40) has one
source**. And the Grand tier's 30 anchors include **11 that are kink-only and
beyond strip reach at any n**: T(28,15), T(29,15), T(30,16), T(31,16),
T(32,17), T(33,17), T(34,18), T(35,18), T(36,19), T(37,19), T(38,20).

Why the strip engine cannot just be pushed: C_14 measured ~38 GB, C_15
projects to ~200+ GB, and its state is packed 4 bits/row with an H ≤ 15 cap
(`results/strip-engine.md` §Complexity). That measurement is the floor any
candidate has to beat, and the brief never mentions it.

### A2. "Top tier of reliability" is not a thing an enumeration can reach here

This repo has a defined four-tier warrant scale (`docs/provenance-tables.md`):
tier 1 jasonp-vetted, tier 2 Lean kernel, tier 3 exact-arithmetic certificate,
tier 4 reproducible measurement. A record enumeration is tier 4 by nature —
that is stated in the Paper 1 table as the subject, not a weakness. Asking for
"the top tier" for every T(n,H) value asks for something the scale does not
grant.

State the goal in the repo's own terms, which also makes it checkable:

- move single-source tier-4 cells to **two-source tier-4**; or
- produce a **tier-3** artifact: an exact-arithmetic certificate for a cell or
  a row that a short independent checker can verify, in the shape of
  `results/strip-mu-certificates.md` or the mod-p degree certificates in
  `results/anisotropic-not-dfinite.md`.

The second is strictly more valuable and nobody has proposed a mechanism for
it. It belongs in the brief as an explicit second track.

### A3. The "truly different" bar, as written, disqualifies the incumbent second source

"If a candidate is a frontier DP over a compressed state, it shares an error
surface with the existing method and does not count." The strip engine *is* a
frontier DP over a compressed state, and it is the project's accepted second
source. Applied literally the bar kills everything computable at this scale,
because at n=40 with ~7 growth nothing that materialises objects survives —
which the brief itself says.

The repo already has the finer version of this distinction, from the
2026-07-30 audit (`results/strip-engine.md` §Independence). The strip engine
is disjoint on four axes — boundary granularity, accounting layer, count
representation, orchestration — and **explicitly not disjoint on one**: its
union-find-with-stranded-component-death connectivity rule is the same rule as
`core/transition.h`. A shared misconception about king-connectivity would not
be caught.

That is the actual bar, and it is sharper than the brief's: **the open axis is
the connectivity rule.** A candidate that decides connectivity by a different
mechanism — inclusion–exclusion over cuts, spanning-structure algebra,
rank-based representative sets, a Tutte/reliability polynomial specialisation
— buys the one thing the existing pair does not have, even if it is a frontier
DP in every other respect. Say that instead.

### A4. Wrong growth number

"Growth is ~6.8 per cell" is stale. Measured and banked here: a(40)/a(39) =
**6.935**, λ estimated **7.110(1)** by four agreeing methods, rigorous bracket
**6.543 ≤ λ ≤ 9.3154** (`docs/open-problem-lambda-bracket.md`;
`results/b006770_upload.txt`). The brief forbids estimation in the
deliverables while opening with an estimate that is off by 0.3.

### A5. The incumbent is misdescribed, and named on the exhausted list

Two errors that will send a teammate at the wrong target:

- "The existing method is a column-height transfer matrix." The production
  base is a column sweep (`cpp/tma/sweep8.h`, `docs/engine-design.md`), but
  the banked triangle and a(40) came from the **cell-at-a-time NW-carry kink
  kernel** — the serpentine frontier.
- The exhausted list names "serpentine cell-by-cell frontier ('kink')" as a
  dead candidate. It is the incumbent, not a candidate.

The bottleneck sentence is right and can be sharpened with the measured
numbers: disk/spill-bound, ~4.4×/term on the pre-kink base and ~2.5× on the
kink base; cost tracks frontier size ~2^H, not object count, so a top height
is never cheap however few animals it contributes (a(40)'s H21 phase alone:
36.4 h on 32 cores, 363 GB disk peak — `docs/paper1-engine-chapter.md` §7–8).

### A6. The pathwidth constraint is asserted, not sourced

"A column is a separator in the king graph, so column-scan already achieves
minimum pathwidth. Reordering the scan does not help." The separator claim is
true (king adjacency reaches only the neighbouring column). "Therefore minimum
pathwidth" does not follow from it, and the brief supplies no citation or
probe — in a brief whose own rule is that every quantitative claim comes from
a probe or a paper. It is also precisely Teammate B's subject: the pathwidth
of P_m ⊠ P_n is a citable quantity.

Handing this down as a constraint risks killing valid candidates by fiat.
Demote it to a question B must answer with a citation, and keep the
consequence — that a candidate must beat, not match, the kink frontier width —
as the actual constraint.

The diagonal exclusion, by contrast, is correct and should stay: on the cut
i+j = c the neighbour (i+1, j+1) sits two layers ahead, so the frontier needs
extra depth — which is exactly the anti-diagonal rejection already recorded at
`docs/dmirror-design.md` §"Recommended geometry". Point teammates there, and
at `results/finite-lattice-crossover.md` (which concludes the diagonal sweep is
essentially optimal and the remaining speed is engineering), rather than making
them re-derive it.

### A7. Redelmeier's reach is understated and the tool is unnamed

"Dies around n=20" — the actual banked figures: `build/g2` two-algorithm
confirms the fixed counts through n = 19 (b-file provenance,
`results/b030222_upload.txt`), and the second-algorithm confirmation row
reaches **n ≤ 22** (`results/redelmeier_row22/`, Paper 1 table row 3, with a
RED control). Name `build/g2` as the canonical gated enumerator — it exists,
and the repo rule is to check `build/` before writing a new tool.

### A8. The exhausted list is incomplete, and the reasons are missing

Add, with pointers, so teammates do not re-propose them:

- **The four algorithmic levers**, all measured dead — the connectivity wall
  (`docs/paper1-engine-chapter.md` §8, `results/second-wind.md`,
  `results/strip-growth-lambda-bounds.md`,
  `docs/full-utilization-redesign.md` Part 4). What is left there is
  engineering, not algorithms.
- **Engineering negatives**: PGO, LPT scheduling, work-stealing at scale,
  tmpfs past a(34), cloud burst, rook/bishop edge distribution.
- **Finite-type convolution certificates** (Klarner–Rivest, Barequet–Shalah,
  Bui) — proven to floor strictly above λ by the slack audit; a different
  target than T(n,H), but the whole method class is characterised in
  `docs/open-problem-lambda-bracket.md` and its barrier argument transfers.
- **The bivariate depth tower** — closed negative
  (`results/depth-tower-bivariate-dead-end.md`).

And give the *reason* for the mod-p entry, which is the one most likely to
come back in a new hat: CRT/mod-p residues catch arithmetic and transcription
faults but share the enumeration, so they are not independence
(`results/crt-counter-shaping.md`; the a(23) readiness analysis behind
`results/ns_a23`).

### A9. Teammate C's "different name" sweep is partly done

`results/novelty-sortie.md` N1–N6 already ran a targeted novelty sweep with
verdicts, `papers/` holds 60+ PDFs (`papers/INDEX.txt`) including Jensen,
Barequet–Shalah, Conway–Guttmann, Chan–Rechnitzer, Bousquet-Mélou–Rechnitzer,
and the OEIS/Superseeker lookups for this family are done and returned novel.
C should start from those and extend, not restart. Two repo conventions to
inherit: the literature term is **polyplets** (with "king-connected animals"
as a first-use gloss), and un-findable references go to `papers/MISSING.md`
rather than being dropped.

### A10. The ranking metric is the wrong objective

"The highest n it could plausibly reach at any cost" was the right metric a
year ago. **a(40) is the final term; the project closes there.** Nothing past
n = 40 has value. Rank instead by banked cells verified per unit resource,
with the 11 kink-only Grand anchors and the H = 15..21 mass weighted heaviest,
and treat a candidate that reaches n = 60 at H = 10 as worth nothing — that
region is already two-sourced.

### A11. The finite lattice method is not an open question here — for reach

The brief lists FLM (Enting, Conway–Guttmann) as "on the table, a floor to
beat." Its reach question was closed negative on 2026-07-10:
`results/finite-lattice-crossover.md`. FLM's payoff is the bounding-box
inequality H+W ≤ n+1, letting you sweep the longer side and pay only for
min(H,W) ≤ n/2 — and this engine already caps the swept dimension at n/2 by
transpose symmetry plus the diagonal-polynomial derivation. Same ½; it does not
stack, and would only add overhead.

That verdict is about *reach*, not *independence*. Inclusion–exclusion over
W×L rectangles is a genuinely different accounting layer, even though a
straight column transfer matrix sits inside each rectangle — so FLM may still
be a legitimate second source for cells the strip engine cannot reach, and the
brief should say which of the two questions it is asking. The connectivity rule
inside the rectangles would still be shared, which is the axis §A3 identifies
as the one that matters.

### A12. Operational gaps

- **"The shared findings document"** is undefined. Repo convention: one
  `results/<name>.md`, negative results banked as their own note in the shape
  of `results/depth-tower-bivariate-dead-end.md`.
- **Probes** must follow `docs/job-checklist.md`: anything that could exceed
  5 minutes runs in a tmux window on an existing session, never in the
  foreground and never `nohup`; binaries build into `build/`, nothing in
  `/tmp`; named on-disk scripts, no stdin jobs; no `find /` or `grep -r /`;
  per-worker RAM = (total × margin)/cores; gympie caps at 10 perf cores.
- **Cross-critique needs a mechanism.** Three agents running concurrently
  cannot read each other's findings. Either run a shared append-only file with
  a stated write protocol, or make the critique a second wave that reads the
  first wave's output.
- **Team composition**: judgment work goes to Fable-class agents, and the
  3-hour usage window means staggering waves rather than firing all three plus
  a critic at once.

---

## B. Corrected brief

> **Target.** The banked T(n,H) triangle (n ≤ 40) has 228 of its 820 cells
> resting on a single enumeration, including **11 of the 30 Grand-tier
> anchors** and **over half of a(40) by mass**. The covered region is H ≤ 4
> (exact recurrences) and H ≤ 14 at every n ≤ 40 (the strip transfer matrix,
> 469 cells, 0 mismatch). Read `results/strip-engine.md` before anything else;
> §Independence there is the standard your candidate is measured against.
>
> Two acceptable outcomes, the second worth more:
>
> 1. **Two-source tier 4** — a method that independently reproduces cells in
>    H = 15..21, or the kink-only anchors, at n ≤ 40.
> 2. **Tier 3** — an exact-arithmetic certificate for a cell or a row that a
>    short independent checker verifies, in the shape of
>    `results/strip-mu-certificates.md`. Nobody has proposed a mechanism for
>    this. It is open, and it is the higher prize.
>
> a(40) is the project's final term. A method that reaches large n at small H
> is worth nothing — that region is already two-sourced. Rank by banked cells
> and by a(37)–a(40) mass verified, not by reach.
>
> **The independence bar.** The existing pair is disjoint on boundary
> granularity, accounting layer, count representation, and orchestration, and
> is **not** disjoint on the connectivity rule: both decide king-connectivity
> by union-find over column labels with stranded-component death. A shared
> misconception there is invisible to both. So: a candidate earns its place by
> deciding connectivity by a *different mechanism* — inclusion–exclusion over
> cuts, spanning-structure algebra, rank-based representative sets, a
> Tutte/reliability specialisation — even if it is a frontier DP in every
> other respect. State the failure mode your candidate would exhibit and argue
> it is disjoint from union-find-over-a-frontier's.
>
> **Ground truth to work against.**
> - Growth: a(40)/a(39) = 6.935, λ ≈ 7.110(1), rigorous 6.543 ≤ λ ≤ 9.3154.
>   Anything that materialises individual objects dies near n = 20; `build/g2`
>   (canonical gated Redelmeier) confirms to n = 19, and the banked
>   second-algorithm row reaches n ≤ 22.
> - The incumbent is the cell-at-a-time NW-carry serpentine ("kink") kernel,
>   with the `cpp/tma` column sweep as its base. Disk/spill-bound, ~2.5×/term
>   on the kink base; cost tracks frontier ~2^H, not object count (a(40)'s H21
>   phase: 36.4 h, 363 GB disk peak).
> - The strip second source cannot be pushed: C_14 measured ~38 GB, C_15
>   projects ~200+ GB, 4-bits/row packing caps at H = 15. Beat that number or
>   explain why your candidate's state does not grow the same way.
> - A diagonal frontier is ruled out: on i+j = c the neighbour (i+1,j+1) is
>   two layers ahead, so the cut needs extra depth.
> - **Open question, not a constraint** (Teammate B, with a citation): what is
>   the pathwidth of P_m ⊠ P_n, and does the kink frontier achieve it? The
>   binding constraint either way is that a candidate must beat the kink
>   frontier width, not match it.
>
> **Exhausted — do not propose; combinations only with a specific argument for
> why the combination behaves differently.** Burnside/symmetry decomposition;
> alternative decompositions of the count; recombination across a second
> machine; mod-p/CRT (catches arithmetic and transcription faults but shares
> the enumeration, so it is not independence); in-flight redundancy checking;
> Lean verification of the implementation; the four algorithmic levers
> measured dead at the connectivity wall (`docs/paper1-engine-chapter.md` §8);
> the engineering negatives (PGO, LPT, work-stealing at scale, tmpfs past
> a(34), cloud); finite-type convolution certificates, whose barrier argument
> is in `docs/open-problem-lambda-bracket.md`; the bivariate depth tower
> (`results/depth-tower-bivariate-dead-end.md`).
>
> **On the table as a floor to beat, not as answers:** the finite lattice
> method (Enting, Conway–Guttmann) — but read
> `results/finite-lattice-crossover.md` first: its *reach* payoff is closed
> negative here (it is the same ½ the engine already gets from transpose
> symmetry), so propose it only as an independent *accounting layer*, and say
> which of the two questions you are answering; tree-decomposition exact model counting
> (sharpSAT-td, GANAK lineage); inclusion–exclusion over component structure;
> sequential importance sampling for confidence intervals rather than exact
> values.
>
> **Split** (as the original brief, with C's start point corrected):
> A — enumeration and statistical mechanics. B — exact model counting and
> parameterised algorithms. C — coverage map: which methods reached what scale
> on adjacent lattice objects, the ceiling each hit, the bottleneck each
> author reported; and where this problem is solved under another name.
> C starts from `results/novelty-sortie.md` N1–N6 and `papers/INDEX.txt` — the
> targeted novelty sweep and the OEIS/Superseeker lookups are already done and
> returned novel. The literature term here is **polyplets**, glossed at first
> use as king-connected animals.
>
> **Deliverables**, appended to `results/second-source-candidates.md`:
> ranked candidates, each with the region of the triangle it could verify, the
> independence argument against the connectivity-rule axis, and the resource
> that binds it first; a kill list with the number or citation that killed
> each entry; and citations with title, authors, year, and a resolvable
> identifier. Do not cite from memory. Un-findable references go to
> `papers/MISSING.md` with what was searched. Tasks are gated on citations
> resolving.
>
> **Probes.** Code exists only to produce measurements — state-space sizes,
> where an existing tool falls over, growth of an intermediate representation.
> Throwaway, small instances, time-boxed to 15 minutes; a probe that exceeds
> its budget is a measurement and the candidate goes on the kill list with
> that number attached. Do not implement a candidate, do not tune a slow
> probe. Follow `docs/job-checklist.md`: tmux window for anything that could
> exceed 5 minutes, named scripts on disk, build into `build/`, nothing in
> `/tmp`, no filesystem-wide scans.
>
> Critique each other's candidates directly. Two of you agreeing is not
> evidence. No candidate leaves the list without either a probe number or a
> resolvable citation; a candidate that cannot be killed cheaply gets a stated
> measurement plan instead of a verdict.
