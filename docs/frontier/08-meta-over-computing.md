# Frontier idea 08 — Meta: are we over-computing?
*Source: docs/scheduling-design.md §"Unexplored axes" #8. Related: docs/a20-submission-draft.md (the deliverable target this audits), ROADMAP.md (#21 b-files, #26 GFs, #28 holes), results/holes.md, results/fixed_height_gf.md.*

## Idea
Not an engineering lever — the "improvement" is doing **LESS**. The actual deliverable is
*extend A006770 on OEIS + a publishable paper*. The minimal path to that may be only the
a(n) **spine** (the single new term + its Burnside-derived shape siblings), while we are
ALSO generating the full by-height triangle B_H(n), the holes distribution, and fixed-height
GFs. If those are enrichment rather than load-bearing, trimming them frees the heaviest
compute for the spine and the cliff. This attacks **WORK VOLUME** by not computing what the
target doesn't require.

## Why it might matter here
The spine is what the RAM cliff is about — the pole height H=N−1 (scheduling-design
§"Strategic staging"). The by-height triangle is the *reason* every state carries a full
counts row for all n (state-store-compression.md: the counts row is **85%** of per-state
RAM). The holes engine is 2D and *more* RAM-hungry than the spine. So the optional artifacts
aren't free riders — they inflate the binding constraint. If the paper doesn't need them at
the frontier, trimming directly relieves RAM and wall at the pole.

## Smoke test (dead-on-arrival)
Read the OEIS b-file format + the submission draft's central claim (~30 min reading). If
the draft cites only a(n), the triangle / holes / GF are non-load-bearing **trim
candidates** — and trimming is live. Dead-on-arrival *for trimming* only if the paper's
thesis turns out to depend on them (a stated claim needing B_H(n) at frontier height). The
draft's promotion checklist is five b-file lines with no triangle/holes/GF row, so trim is
on the table — proceed to the full requirements audit.

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** are the triangle / holes / GFs load-bearing for the paper's
*claims* and the OEIS submission, or are they enrichment that can ride below the frontier?
**Setup:** a **requirements audit** — conclusive by reading the target, no compute. Read
docs/a20-submission-draft.md and infer what a b-file + publishable paper STRICTLY require.
**Measure (what the target actually demands):**
  - **OEIS b-file (A006770 + the four shape siblings A030222/30233/30234/30235):** needs
    the **spine term only** — Fixed(n) plus the n-row symmetry counts (r90/r180/axis/diag)
    that Burnside-assemble the siblings. The draft's promotion checklist is five b-file
    lines; **no triangle, holes, or GF row appears.** The GF cross-check is named as ONE
    corroboration sentence ("heights 1–10 additionally cross-checked against recovered
    fixed-height GFs") — a *verification garnish on H≤9 we already have*, not a claim
    requiring frontier-height GFs.
  - **Paper:** the headline is the method (algorithm-independent column transfer matrix,
    a(n)=Σ_H B_H(n), cross-ISA confirmed). The triangle/holes/GFs are *separate scientific
    contributions* (ROADMAP #26/#28, the novel-on-OEIS structural sequences) — they enrich
    the paper but the a(n)-extension claim stands without the frontier-height triangle.
**NO-GO for trimming if:** the triangle/holes/GFs turn out load-bearing for a stated paper
claim at frontier height (e.g. the paper *proves* something needing B_H(n) at H≈N−1, or the
b-file requires a per-height column). The draft shows they do not.
**GO (trim scope) if:** they are enrichment recoverable below the frontier. The audit says
**GO** — but as a *decision for jasonp*, not an automatic cut (see ladder).

## Substantial-improvement ladder (must clear ALL)
- **C1 — compute saved is on the BINDING axis** — trimming must lighten the **pole**, not
  just total work. The counts-row-for-all-n (triangle) is 85% of per-state RAM; a
  spine-only run could store one (or a narrow ranged) count instead of [0…maxn] ⇒ directly
  relieves the cliff. Quantify via `--profile-rows` (the §0.2 measurement) + a spine-only
  vs full-triangle peak-RSS A/B at the calibration height.
- **C2 — the trimmed artifacts are recoverable LATER, below the frontier** — holes runs
  and H≤9 GFs already complete at n≤19/20 off the critical path; trimming them at the pole
  loses nothing permanent, only defers enrichment.
- **C3 — no paper claim or b-file line goes unsupported** — the requirements audit must
  show every promotion-checklist item still has its input from the spine alone.
*Per-idea bar:* "substantial" = the saved pole-compute (RAM + wall) is large AND the lost
scientific/archival value is recoverable later — framed as an **explicit trade for jasonp**,
not an automatic cut. The triangle/holes/GFs are genuine novel-on-OEIS results; trimming is
a *sequencing* choice (spine first at the frontier, enrichment below it), not a deletion.

## Composition / foreclosures
- **Reframes idea 01.** If the spine doesn't need the all-n counts row, the ranged row
  collapses to ~1 wide (or a single count) — a far bigger RAM win than the +1.3-term
  ranged-row projection, because the triangle is *why* the row is dense in the first place.
  So this idea and docs/frontier/01-state-compression.md compound: trim-then-pack.
- **Orthogonal to scheduling and to #2/#3** — it changes *what* is computed, not *how* it's
  distributed or stored.
- **Forecloses nothing** and is reversible: a later full-triangle pass can always be run
  below the frontier where it's cheap.

## If it passes: effort & where it lands
**XS (ESTIMATE)** — the audit itself is a read of docs/a20-submission-draft.md (done here:
verdict = triangle/holes/GFs are enrichment, spine suffices for the b-file + the core paper
claim). The *consequence* — a spine-only sweep mode (single/narrow count instead of the
all-n row) — is **S–M** and lands as a build flag on `cpp/tma` + the ranged-row work in
frontier-revision-plan Phase 1. **No ETA fabricated.** This is a scope decision for jasonp:
the menu is "frontier spine-only now, enrichment triangle/holes/GFs below the frontier,"
with the saved pole-RAM/wall as the quantified upside.
