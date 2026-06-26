# Frontier idea 01 — Do less work: state compression + more symmetry reduction
*Source: docs/scheduling-design.md §"Unexplored axes" #1. Related: docs/state-store-compression.md (the design/decision record — this idea is ALREADY DEEPLY PLANNED there), docs/frontier-revision-plan.md (Phase 0 kill-tests §0.1/§0.2), docs/frontier/02-out-of-core-spill.md.*

## Idea
Shrink the in-RAM frontier rather than spread/spill it: ranged counts row, u32 mod-p
rows, Sig-shrink, vertical-flip symmetry fold. Attacks **RAM** (the binding constraint)
by storing fewer bytes per state and fewer states. This file does NOT re-derive the
levers — that's state-store-compression.md (§A packing, §B structural, §C count) and
frontier-revision-plan.md (Phase 1–3). It restates the idea in the goal's structure and
makes ONE decisive distinction explicit: **shift vs bend.**

## Why it might matter here
Stacked, the planned levers project ranged (~1.8× on `vals`) + u32 (mod-p, ~2×) +
symmetry fold (~2× count) + chunked drain (~2× double-buffer). state-store-compression.md
"Combined projection": a(22) heaviest stratum → ~45 GB (inside ayr's 78 GB ⇒ cross-ISA
*confirmable*); a(23) ~95–110 GB after ranged ⇒ pushed toward dalby's 122 GB. The stated
reach gain is **+1.3 effective terms** (frontier-revision-plan §Goal). That is real and
worth banking. But every one of these is **constant-factor**: it slides each `reach.md`
row rightward by a fixed multiplier. It does NOT change the **2.42×/term** pole law that
sets where the cliff is. So compression buys ~1 term and **moves the a(24) cliff to ~a(25)
— it does not remove it.**

## Kill-test — quickest path to INFEASIBLE
**Question it answers:** is there a compression that BENDS the 2.42×/term curve, or are
all the planned levers merely SHIFTS (≈1 term, no scaling change)?
**Setup:** REUSE the two existing Phase-0 kill-tests verbatim — do not invent new ones.
  - §0.1 **FLM scaling back-of-envelope** (frontier-revision-plan): estimate width-bounded
    (finite-lattice) boundary-state growth vs our height-bounded diagonal over n=19..24,
    from the `peak_states`-by-height data in reach.md + a quick width-bounded count at
    small n. An afternoon, no build. This is the ONLY lever that could bend the curve.
  - §0.2 **`--profile-rows`** (one gympie core): histogram live count-row width `hi−lo+1`
    at the peak height, weighted by state → sizes the ranged-row shift factor.
**Measure:** §0.1 — the per-term ratio of width-bounded states (does it grow slower than
2.42×?). §0.2 — mean row width vs maxn ⇒ ranged factor = maxn / mean-width.
**NO-GO (as a game-changer) if:** §0.1 shows width-bounded growth ≈ the same 2.42×/term
base (just a smaller constant). Then FLM is a SHIFT, not a BEND — and so is everything
else in the stack. Decisive because a shift caps the *entire* compression program at the
already-stated +1.3 terms: still build it (a(22) confirmable is the deliverable), but
**cap expectations — it is not the a(24)+ answer.** Only a §0.1 BEND would reorder the
whole plan (frontier-revision-plan §Sequencing makes this exact branch the keystone).
*Arithmetic settling the shift case:* a 4× total RAM cut = log(4)/log(2.42) ≈ **1.57
terms** of reach — bounded, matches the doc's +1.3, and independent of N. A constant
factor can never out-run a geometric base; that is the whole point of the distinction.

## Substantial-improvement ladder (must clear ALL)
- **C1 — terms-of-reach gained ≥ +1 effective** — from the measured stacked factor via
  log(factor)/log(2.42); the doc's +1.3 is the target, ≥+1 is the floor to be worth the
  engine surgery.
- **C2 — a(22) heaviest stratum measures < 78 GB** — the confirmability gate
  (frontier-revision-plan §Benchmarking, calibration case `square8 18 --only-height 17`);
  this is the concrete near-term payoff, not a projection.
- **C3 — every lever byte-identical to dense baseline under serial · MT · checkpoint ·
  reserve** — the hard invariant (gate checks M/M′/O/P); a lever that changes one count is
  a defect, not a tradeoff.
*Per-idea bar:* "substantial" here = **C1+C2 (ship the +1.3 and make a(22) confirmable)**.
A separate, higher bar — *game-changer* — is reserved for the §0.1 FLM BEND outcome only;
absent that, this idea is explicitly a strong constant-factor win, not a cliff-remover.

## Composition / foreclosures
- **ALREADY DONE / decided — do not re-litigate:** `--reserve` pre-size + load-factor 0.85
  **landed, gate-green**; Motzkin/compact-noncrossing encoding **ruled out** (square-8
  boundary partitions genuinely cross — signature.h L9–13; Sig is only ~15% of RAM anyway);
  auto-`kmax` for holes **dropped** (max holes grows ~linearly, near n).
- **Stacks multiplicatively** with nothing else on the frontier list (it's the only
  do-less-bytes axis); it is **orthogonal to all scheduling** (the queue, M4/M5).
- **Shares a seam with #2:** the chunked/blocked store (§B6 / Phase 3.2) is simultaneously
  the in-RAM 2× and the **out-of-core precursor** for docs/frontier/02-out-of-core-spill.md
  — build it once, it pays both. Ordering: Phase 1 ranged → Phase 2 u32+CRT → Phase 3
  structural; the blocked store is the bridge to #2/#3.

## If it passes: effort & where it lands
**M–L (ESTIMATE)** — ranged row is the keystone drop-in (M); u32+CRT (S–M); symmetry fold
is correctness-critical parity work, gate hardest (the L, land last). All behind
`statedb.h`'s `slot()`/`for_each()`/`addCounts()` — "the designed-to-be-replaced component."
ROADMAP: the memory-stack / frontier-revision-plan Phases 1–3. Engine: `cpp/tma/statedb.h`,
`cpp/tma/sweep8_holes.h`, gate `gate_tma.py`. **Effort is a t-shirt size, not a wall-clock
— no ETA fabricated.** §0.1/§0.2 are the cheap gates that price the rest before building.
