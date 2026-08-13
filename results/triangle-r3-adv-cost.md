# Round-3 cost & completeness adversary

2026-08-12. Audit of every filed round-3 deliverable against
`docs/triangle-round3-brief.md` and `docs/skeptical-reader-standard.md`.
Arithmetic re-derived exactly in
`experiments/tristruct/r3_adv_cost_arith.py` (log alongside); source
anchors re-checked by `git show` where cited. **Not seen at audit time:**
`results/triangle-r3-adv-independence.md` (not filed), the synthesis, the
status of the dalby B1 calibration run, `docs/viva-reserve.md`
(permission denied per harness).

---

## PART A — cost audit

### The table

| figure | lane | status | wrong-by-3× consequence |
|---|---|---|---|
| window census 891,074 @ H=14; 34.2 s/col; 0.94 µs/slot-col | L6-1 | MEASURED (second-source branch, exact-payload binary; quotes verified against `git show second-source:results/second-source-candidates-B.md`) | anchor itself solid |
| state growth ×2.9/height | L6-1 | MEASURED to H=14 (branch) and H=11 (own probe) — but the two measurements **disagree**: own probe says ×2.98–3.04 | compounds to ×1.3–1.5 in windows at H=20–21; feeds the RAM figure below |
| windows at H=20 (530M), H=21 (1.54G) | L6-1 | EXTRAPOLATED **6–7 heights** past the last measured census (×594–×1723) | see RAM |
| **RAM 55 GB @ H=20 / 160 GB @ H=21** | L6-1 | EXTRAPOLATED + MODELED — per-state bytes are a tight-packing model; **no measured RSS exists for this DP at any scale**; the branch's 72/207 GB figures it "reproduces" come from the same model (circular) | **decision-changing well below 3×**: at the own-probe base ×3.04 plus a routine ×1.5 hash-container overhead, H=20 = **102 GiB — does not fit ayr's 78 GB**; even at ×2.9 + ×1.5 it is 77 GiB, exactly at the line. H=21 → 200–310 GiB. The phase-2 pitch "8-bit residues to H=20 in RAM" rests on this figure |
| wall ~5 d @ H=20 (1 thread) | L6-1 | EXTRAPOLATED — constant 0.94 µs/slot-col held over a 594× working-set growth (90 MB → 55 GB); project history (tmpfs a34 win, a35 NVMe, spill-bound scaling) says random-access throughput degrades at that scale; partially offset by the 1-byte payload being cheaper than the measured exact payload | days → weeks; survivable on fleet but the pitch changes. Note also: ~5 d is **H=20 alone**; the full H=15..20 ladder is **7.7 days/prime** single-thread (re-derived) |
| **13 CRT runs for exact values** | L6-1 | ASSERTED — **and wrong**. Exact check: log₂ T(40,15) = 103 bits; the top thirteen 8-bit primes (≤251) give a 100.8-bit product, which does **not** cover T(40,15). **14 runs**, first-exceeds check in the log | +8% wall only; flagged because it is exactly the class of slip the round exists to catch, in the round's own flagship number |
| single-thread → fleet scaling | L6-1 | ASSERTED ("state-sharded parallelism is this project's stock in trade") — never measured for this DP; the incumbent's own history here is straggler tails and 19.8% utilization | wall pitch, not feasibility |
| spin-basis 3^20 states / ~18 GB / fleet-days | L6-2 | states MEASURED (exact arithmetic); throughput ASSERTED (self-flagged as the file's weakest number) | backstop only; no decision hangs on it |
| piece/cell overhead ×1.15–1.18 per H; ~7× @ H=15, ~18× @ H=21 | L1 | overhead-per-H MEASURED (H ≤ 9); band figures EXTRAPOLATED 6–12 heights, labeled as such | none — the verdict rests on the measured monotone sign (piece > cell at every measured H), which no 3× error touches. Honest cost model |
| answer-size floor I(⟨h⟩)(40) ≈ 6.6e15, I(C2)(40) ≈ 1.8e16 | L4 | EXTRAPOLATED 8 terms by λ⁴ = 2575 from banked exact n=32 values; corroborated by measured wall ratios (N=14..18) bracketing λ^(1/2) = 2.669 | none — the floor's *logic* (an explicit enumeration visits ≥ 1 node per accepted candidate) is sound independent of the magnitude, and 3× down still leaves ~80–1300 laptop-years. Robust decline. Arithmetic re-verified: 570/4033 laptop-yr, 244/1859 yr floors all reproduce |
| Lean proof 3–5 sessions | L3-5 | ASSERTED by analogy (Notary wave-B precedent); the S3 risk is uncalibrated **by the lane's own admission** ("no comparable Finset-geometry induction exists in the development") | at 3× (9–15 sessions) the dispatch decision plausibly changes. **The fallback is real**: the MoatBound named-hypothesis pattern exists (`polyplets/Polyplets/HolesUpper.lean`), `Tc_eq_T` exists sorry-free (`polyplets/Polyplets/Compute.lean:207`), and the executable spec (45/45 cells, RED caught) is the strongest pre-verification any Notary wave started from. Risk is real but bounded: the failure mode is a conditional theorem, not nothing |
| model-count floor: band sum 2.885e31 | L5 | MEASURED (banked exact sums; re-derived here) — the strongest cost figure in the round; no error model touches a 10¹⁴-year verdict | none. L5's reach verdict is the round's most secure |
| CNF instance sizes 167k vars / 682k clauses @ (40,21) | L5 | MEASURED (emitted) | none |

### The regime question (short-range conservative vs long-range collapse)

- **L4, L1, L5** are short-range or floor-type: measured anchors, small
  extrapolation spans, verdicts that survive 10× errors. Conservative regime.
- **L6-1 is the long-range regime**, and it is the round's live proposal:
  every band figure sits 6–7 compounding steps past the last measurement, the
  RAM model has never been compared to a real RSS, the growth base is the
  larger of two measured values in nobody's table, and the throughput constant
  is assumed scale-invariant against this project's own spill-bound history.
  None of this kills the route — the family is real, the anchors are real —
  but the phase-2 proposal as written ("H=15..20 in RAM on ayr, ~5 days")
  is the optimistic corner of every uncertain factor simultaneously. Before
  any commitment: (i) pull the dalby B1 run's H=15/16 walls if that run
  completed — **measured first-two-rows may already exist and L6 did not
  look** (its own NOT ESTABLISHED); (ii) one C++ census + RSS measurement at
  H=13–14 with the residue payload settles base, bytes/state, and µs/slot in
  an afternoon. Queue row filed.

### Measurement-provenance defect (process finding, added on the lead's stop order)

**Every round-3 measurement was taken on gympie — jasonp's working laptop —
in violation of the project's standing no-jobs-on-gympie rule.** The defect
is the round's, not any lane's: the brief's "measurement boundary" section
explicitly granted "laptop minutes" (`docs/triangle-round3-brief.md`, Rules
of engagement), and the lanes ran where the lead's brief told them to. This
audit's own script (`r3_adv_cost_arith.py`, ~1 s) ran there too, before the
stop order; disclosed alike.

Figures that came from runs that should not have happened, split by whether
the *value* is machine-relative:

- **Machine-relative (gympie-calibrated walls/throughput — the cost models):**
  L4's N=14..18 walls (7.49 s / 53.1 s, 8 threads) and accept rates
  (8.5×10⁵/s, 3.1×10⁵/s) — the entire basis of the 570/4,000 laptop-year
  extrapolations and 240/1,900-year floors; L6's Python 51.6 s/col scale
  point; L3's 196 s enumeration and 41 s spec-DP walls; L1's 81 s; L5's
  Lean/CNF timings; INV's 2.2 s. These are additionally "laptop-year"
  figures calibrated to the one machine jobs are banned on.
- **Machine-independent (exact counts — value unaffected, rule still
  violated):** L1's state closures, L3's pinch/hole censuses, L4's per-cell
  cross-checks and exclusion boxes, L5's 23-cell reproduction and 74,388
  subset self-test, L6's [q¹] matches and window censuses (incl. the
  ×2.98–3.04 growth corroboration), INV's 176k-animal table, the harness
  exposure run.
- **Not tainted:** L6-1's decisive anchors — 891,074 windows and
  34.2 s/col at H=14 — were measured on **dalby** by the second-source
  branch before this round. The round's flagship cost model survives the
  provenance defect at its core; the gympie contribution there is the
  corroborating growth base and correctness probe.

**Re-measurement, now that it cannot happen here** (all items already
NOT ESTABLISHED or flagged above, restated with off-laptop cost if jasonp
authorizes): ADV-1's re-anchor (C++ census + measured RSS at H=13–14,
residue payload) is minutes-to-an-hour single-core on ayr or dalby at
~100 MB — the natural first phase-2 gate anyway; L4's walls re-anchor on
ayr in minutes (symcount_fast builds native there) if anyone ever needs
fleet-years instead of laptop-years, which the decline does not; the
small-n validation runs are seconds anywhere and their values stand as
machine-independent. This audit itself needs no further compute.

---

## PART B — completeness

### Blind lists vs the withheld seed list

Read order followed: all five blind lists first, then the seed.

**Scouts found, seed lacks:** the Cut&Count / BCKN / site-Potts
color-coincidence **cancellation family — the round's only surviving
route** (L6 blind items 6, 10, 28, 29, converging with the one-day-old
second-source B1). The seed's nearest entry, "FK (random-cluster)
representations", names the physics face only, with no cancellation
mechanism, no residue reading, no site version. Also scout-only: the
Euler-characteristic DP, ASP/clingo concretely, Lean-as-counter, CP graph
globals, ZDD/Graphillion (named to kill), dancing links, heaps, species,
and the whole involution program. **Seeding would have anchored the round
on a list that does not contain the round's product.**

**Seed holds, no scout found:** four items — Gröbner-basis counting
frameworks, lace expansions, Martin-polynomial / matrix-tree routes,
automatic-sequence methods. Scored honestly: the first three die at F1/F2
under the scouts' own pre-registered filters (no exact-T(n,H) mechanism at
reach; lace expansions are asymptotics machinery); automatic-sequence
methods are the only near-miss with content — a mod-p algebraic-kernel
reading — and L4's algebraic-GF and P-recurrence exclusion boxes cover its
mechanism without its name. **The seed was load-bearing nowhere**; the
round need not adopt anything from it.

**Convergence:** ~11 of the 14 seed items independently named
(L5 territory 4½/5, L6 territory 6½/9) — high, and the asymmetry runs
entirely in the scouts' favor. The withholding cost nothing and the
blind protocol earned its keep: it is the *evidence* that the convergence
is real rather than an echo.

### The framing-risk instrument

The seed's recorded risk — routes unstateable under "where is
connectivity decided" — **materialized, twice, mildly, and the round's
own mechanisms caught both**: L6 filed the Mertens external-anchor class
explicitly as not fitting the ticket (the brief's escape clause, used as
designed), and L3-2/L3-5 — prove the rule rather than vary it, the round's
other phase-2 half — is a route with no recount-style answer to the
ticket at all; it surfaced only through the mid-round generativity
amendment, not through any lane's ticket paragraph. No lane contorted a
candidate to fit; the queue was the outlet. But the risk has a residue the
round has not noticed, which is the next section.

### Missing from both — what a competent outsider would ask

The ticket's vocabulary steered every lane toward *rule-class variation*.
A referee attacks provenance and artifacts too, and neither the lanes, the
seed, nor the 35-row queue touches:

1. **Binary provenance of the banked a(40) run.** The harness names it NOT
   ESTABLISHED (were the dalby phase A/B/C binaries built from revs
   38956525/801afd59?) and **no lane or queue row picked it up**. It is the
   cheapest attack on the record — run.log headers vs stated revs, an
   afternoon — and no amount of rule-independence answers it. (The harness's
   other unclaimed item, the strip_tm link-line audit, is the same class.)
2. **External anchor for the shared rule schema itself.** The three shared
   propositions are lattice-generic; only the stencil is king-specific. The
   executable spec (`r3_l3_schema_dp.py`) with a rook stencil, run against
   Jensen's *published* fixed-height square-lattice polyomino series, would
   test partition-sufficiency and the completion predicate against other
   people's numbers at real heights — the only way anything in this round
   tests the schema against external ground truth above n≈22. Nobody named
   it; the king-only Mertens anchor stops at s≈14/22 and everyone filed it
   as terminal, but the *schema* does not stop there.
3. **Archived-state replay.** If any in-band frontier state or shard
   artifact survives from the H=15..21 sweep on dalby, replaying one column
   transition through the literal executable spec is an implementation-level
   spot audit that neither L3-5 (schema proof — its own residual statement
   says so) nor L6-1 (independent recount) provides, at ~zero cost. Nobody
   asked whether the state survives.
4. **Transpose-accounting consistency.** T(n,H) as height marginal must
   equal the width marginal cell-for-cell (90° rotation); the sweep computes
   the two by different accounting through the same rule. Consistency-class
   only — but it is the cheapest whole-band lattice not yet named anywhere.
5. **The proved height-distribution limit shape vs row 40's band shares** —
   worth one line only if the banked law carries usable error bounds;
   otherwise a smell test. Named for completeness; likely zero.

Rows filed for 1–4 (ADV-2..ADV-5) plus the L6-1 re-anchor (ADV-1).

---

## PART C — silent caps

The forbidden kind — a top-N, read cap, or sample bound hidden from the
deliverable — **was not found in any lane file**; declared caps (L6's
6-paper cap with queue spillover, L4's exclusion boxes and 32-term order
cap, INV's n ≤ 7, L1/L3's labeled extrapolations) are all on the surface.
Three findings at the boundary:

- **L6-1's RAM/wall table is labeled "proj." in one column and then spent
  as settled fact in prose** ("residues to H = 20 within ayr's 78 GB",
  "RAM-feasible today") — an extrapolation presented, one paragraph later,
  as a measurement. Part A quantifies why that matters: the feasibility
  claim dies under the lane's *own* alternate growth measurement plus
  ordinary container overhead. This is the round's one instance of the
  collapse-at-long-range pattern, in its most decision-adjacent number.
- **L6's web triage is unauditable**: "search-level, no full read" with the
  queries summarized, not recorded. The kill counts are reproducible from
  the blind list + filter; the *coverage* of the post-2015 sweep is not. A
  soft cap on the wildcard lane's negative half.
- **L6 did not check whether the dalby B1 run completed** (declared in its
  NOT ESTABLISHED, so not silent — but it caps the anchor set at
  extrapolation where measurement may exist on disk).

One found arithmetic error, restated: **the CRT ladder needs 14 runs, not
13** (top-13 8-bit primes: 100.8 bits < 103). And one reading correction
for the synthesis: the lead's dispatch summary "H=15..20 in ~55 GB, ~5
days single-threaded" conflates the H=20 row with the ladder — the full
single-prime ladder is ~7.7 days, and exact values via CRT are ~108
single-thread days (~fleet-days ×14 if the parallel scaling holds).

## Queue rows filed

ADV-1..ADV-5 appended to `results/triangle-r3-queue.md`.

## NOT ESTABLISHED

- Whether ayr's *available* (vs total) RAM at phase-2 time clears even the
  optimistic 51 GiB — depends on cohabiting jobs; phase-2 fact.
- Actual container overhead of the L6-1 DP (the ×1.5 used in the
  sensitivity check is a typical figure, not a measurement of this DP —
  the point is that the pitch is sensitive to it, not that 1.5 is right).
- Whether Jensen-style published fixed-height square-lattice series are
  citable at the heights item B-2 wants (they exist in the literature this
  project has partly archived; the specific tables were not pulled during
  this audit).
