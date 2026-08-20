# Undertow review, Lane B — interaction, and what a(41)/a(42) would nail down

2026-08-20, branch `lastditch`. Brief: `docs/undertow-review-brief.md` §3 Lane B.
Blind findings filed 07:31 EDT in `results/undertow-review-queue.md` (B1-B15).
Everything below is worked from the dependency structure in
`experiments/undertow_pin.py` / `undertow_ri.py` and costed against
`results/ns_a40/PROVENANCE.md` + `rundir_size.log` (phase-wise du peaks
recomputed from the log: A 69.2 GB, B 172.3 GB, C 363.4 GB — matching the
figures `results/undertow.md` quotes).

## Answer, one paragraph

**No n = 41 or n = 42 run can close a(40)'s remaining gap in the sense the gap
is stated.** The gap (`undertow_ri.py`: `row 40 ... GAP [19]`) is
*rule-independence* of `T(40,19)`, and every cell an n = 41/42 run produces
comes from the incumbent kink engine, so by construction it cannot make any
cell rule-independent. What such a run CAN buy is *validation*: exactly one
cell per row bears on level 21 — `T(41,20)` (depth 2, needs a real H = 20
sweep at Nmax 41) and `T(42,21)` (depth 1, needs H = 21 at Nmax 42) — and
either one turns `T(40,19)` from a pinning input into a genuine holdout. The
two routes that do close the rule-independence gap are not n = 41/42 runs at
all: **Motley `C_19`** (direct enumeration under the second rule, the only
route that touches neither `D_j` nor the grand form) and **depth 5** (level 21
pinned from Motley's banked `T(39,18)`, `T(38,17)`, both H <= 18). Costed
below, the cheap-and-decisive combination is depth 5 (staged) or Motley `C_19`
(census first) — and the n = 41/42 sweeps are the most expensive instruments
on the table for the least distinctive good, unless the five-terms sweep runs
anyway, in which case their content arrives as a side effect.

## 1. The dependency structure — what bears on T(40,19)

`T(40,19)` sits on level k = n - H = 21. Onset (`diagonal-law` step 5) is
n >= 2k+1 = 43, so it is a below-onset cell at depth j = 43 - 40 = **3**:

    T(40,19) = P_21(40) * 3^(40-1-63) + D_3(21)

Its value is fixed by (a) levels k <= 20 (all overdetermined or wired-and-
validated), (b) the two free constants (a_21, b_21), and (c) `D_3(21)`. So
the only external cells that bear on it are **level-21 cells**, and there is
exactly one per row in the question's range:

| row | level-21 cell | depth j | produced by | status |
|---|---|---|---|---|
| n=39 | T(39,18) | 4 | banked (incumbent) AND banked (Motley H<=18) | two-sourced |
| n=40 | T(40,19) | 3 | banked (incumbent, a(40) phase A) | the gap itself |
| n=41 | T(41,20) | 2 | sweep H=20 @ Nmax 41 | not run |
| n=42 | T(42,21) | 1 | sweep H=21 @ Nmax 42 | not run |
| n=43,44 | T(43,22), T(44,23) | onset anchors | H=22/23 sweeps | out of scope |

Depth 5 adds one more usable cell below the frontier: T(38,17), j = 5, banked
under both rules — usable only once `D_5` exists.

Level 21 today has exactly one pin pair, (j=3, j=4) = {T(40,19), T(39,18)},
zero internal cross-checks (`results/a41/PROVENANCE.md` says this plainly).
Because T(40,19) is a pinning INPUT, no banked-data tower can predict it —
two equations, two unknowns. Every route below is a way of buying a THIRD
level-21 equation so that T(40,19) can be predicted by the other two.

## 2. The routes, and what each one establishes

Held apart throughout, per the brief: **validation** = the banked swept
T(40,19) is checked against something it did not feed; **rule-independence**
= a value for T(40,19) derived with no incumbent-rule input anywhere.

### Route V1 — sweep H = 20 at Nmax 41 (an "n = 41 run")

Produces swept T(41,20). Level 21 then has pairs (2,3), (2,4), (3,4); pin
from (2,4) = {T(41,20), T(39,18)} and predict T(40,19) as a holdout.
Equivalently (same consistency relation, three equations two unknowns): pin
from (3,4) and predict T(41,20) — the framing a41/PROVENANCE uses. Either
way it is ONE independent check on the triple {T(39,18), T(40,19), T(41,20)}
jointly with {D_2, D_3, D_4}(21); a failure does not localize.

- Buys: **validation of T(40,19)** (and simultaneously retires a(41)'s stated
  weak point — P_21's prediction of T(41,20) becomes a holdout against an
  enumeration). Buys **no rule-independence**: T(41,20) is incumbent-rule.
- Cost: ASSERTED ~20-30 h / ~450 GB (`results/a41/PROVENANCE.md:56`), but the
  cited script `scripts/dalby_a41_h20.sh` **does not exist on this branch**
  (nor do `dalby_a41_low.sh`, `nmax_scaling.sh` — presumably dalby working-tree
  files; queue B7/B15). EXTRAPOLATED from measured a(40) phase B (9.6 h wall
  /48c, phase disk peak 172 GB) times the measured Nmax exponent (~3.9 at
  H=20, `docs/five-terms-plan.md`): **~11 h /48c, ~190 GB of H20 shards** —
  2-3x under the asserted figure. Unresolved which is right; the 450 GB may
  include ~200 GB of retained `runs/a41_low`. Disk, not RAM, is the pressure
  (kink rss_max ~1 GB at H=20).

### Route V2 — sweep H = 21 at Nmax 42 (an "n = 42 run")

Produces swept T(42,21) (j = 1). Same logical role as V1: one more level-21
equation, validation only.

- Cost: EXTRAPOLATED from measured phase C (36.4 h /32c, 363 GB) x 1.22
  (five-terms Nmax-42 factor): **~44 h, ~443 GB.**
- **Dominated by V1 for a(40)'s gap**: strictly more wall and disk, identical
  kind of evidence, and V1 additionally fixes a(41). V2's only distinctive
  content is T(42,21) itself, which serves a future a(42), not a(40).
- Note the old reason to want an n = 42 run is gone: ns_a40/PROVENANCE's
  "a(42) is the next validation seam" (T(41,22) as P_19's first holdout) is
  superseded — Undertow's `--audit` already re-derives P_19 from H <= 18 and
  predicts the swept T(39,20) and T(40,21) as enumeration holdouts (queue B8).

### Route R1 — Motley C_19 at Nmax 40 (not an n = 41/42 run)

`T(n,19) = C_19 - 2C_18 + C_17`; C_17, C_18 are banked (C_18's five residue
passes completed and banked 2026-08-19, `results/cutcount_b1/PROVENANCE.md`),
so one `motley_par` ladder at H = 19 enumerates T(40,19) directly under the
second connectivity rule.

- Buys: **rule-independence AND validation in one act** — the only route that
  makes a statement about T(40,19) through neither `D_j` nor the grand form.
  Agreement with the incumbent's swept cell is a cross-rule, cross-code-path
  confirmation of the exact kind the certification map is built on. Closes
  `undertow_ri.py`'s GAP [19] outright: a(40) rule-independent in all 40 cells.
- Also buys, for free, level 21's Motley pin pair (3,4) — which is what the
  five-terms plan's "a(41) two-sourced from birth" needs (run it at Nmax 41,
  +~10% cost, to cover row 41's own cells too).
- Cost: wall ASSERTED ~11-15 h on dalby (undertow.md's repricing; five-terms
  says ~1.2 h/prime x 9 sixteen-bit primes at 80 threads). **RAM is unpriced
  in every document that quotes the wall** (queue B6). Extrapolating the
  MEASURED parallel-engine point (H=18/Nmax40, u32 payload: 60.2 GB RSS,
  72.5M states, ayr) at the measured ~x3.0/height: ~180 GB (u32 primes) /
  ~110 GB (u16) / ~68 GB (u8) against dalby's 125 GB. So the route survives,
  but the prime width and pass count — hence the real wall — are undecided
  until the H = 19 state count is measured. That is job request J1.

### Route R2 — depth 5 (`families 21 4`; not an n = 41/42 run)

With `D_5` exact, level 21 pins from Motley's banked {T(39,18), T(38,17)}
(both H <= 18), and the tower then computes T(40,19) = P_21(40)*3^-24 +
D_3(21) with no incumbent input.

- Buys: **rule-independence of the derivation**, plus validation-by-agreement
  when compared to the incumbent's swept cell. Weaker in kind than R1: the
  chain runs through `D_3, D_4, D_5` at k = 21, i.e. an extrapolation of the
  W3 derivation past its checked range (k <= 19), and D_5 as of today has
  passed no gate at all. Two mitigations, both cheap: the swept-cell
  comparison itself checks the whole chain, and a W3-style gate of D_5
  against banked depth-5 cells at k <= 19 (~15 cells exist) is free desk work
  and must precede any use at k = 21 (queue B13).
- Cost: EXTRAPOLATED ~16 h / ~103 GB on dalby (undertow.md; 1.82x/K wall and
  1.6x/K RSS, measured at K = 8, 10, 12). The RSS figure is **nine K-steps of
  extrapolation ending 22 GB under the box** — a +5% error in the 1.6 ratio
  compounds past 125 GB. Stage it: K = 14 (~15 min, ~4 GB) and K = 16
  (~50 min, ~10 GB) refine the exponent before the 16-h commitment (B10).
- Side effect: depth 5 also gives levels 20-23 a second pin pair each, which
  is what rescues row 45 in the five-terms plan and gives level 21 "agreement"
  standing for a(41).

### Route V0 — what already happened

The a41 low sweep (H <= 19, Nmax 41, banked) re-swept T(40,19) at a different
Nmax/config — part of the 760-cell regression. Same engine, same rule: it
catches machine and configuration error, nothing about the rule (B11).

## 3. Interactions — who makes whom cheaper, and who secretly agrees

**Undertow x depth ladder.** Each exact depth J adds one row per level of
reach (k_max = Hs + J - 2). Depth 5 makes Motley H <= 18 sufficient for level
21 — i.e. it makes R1 unnecessary *for the tower route*, and makes V1
unnecessary *for a(41)'s second-pair fix* (agreement rather than holdout).
Both substitutions trade evidence kind for cost: identity-vs-identity
agreement instead of agreement with an enumeration.

**Undertow x Motley.** Undertow is what converts Motley's short rows into
tall-band coverage (levels 10..20 pinned from H <= 18 cells), which is why
b1-closure's RAM ladder to H = 20/21 — rungs E and G, "H = 21 never fits" —
is moot for row-40 closure. Conversely the parallel engine's measured 24x is
what turned Motley H = 19 from the 27-40-day Ticker Tape estimate into an
overnight run, IF the RAM fits (B6).

**Undertow x the sweep.** Undertow removed the production need for H = 20/21
(the dry run reassembles a(40) from H <= 19), which is exactly the two disk
poles (172/363 GB of the 363 GB peak). Any tall sweep bought now is bought
purely as a validation instrument — so its price competes with R1/R2, not
with a production schedule.

**The five-terms plan x everything.** Its own sweep is H <= 21 at Nmax 43-45
— Undertow's economy there is terms-per-sweep, not height reduction — and any
Nmax >= 42 tall sweep produces T(41,20) and T(42,21) **as side effects**. So
if five-terms launches, V1/V2's entire content arrives free inside it, and
buying V1 standalone first duplicates ~all of its cost. The converse does not
hold: no five-terms sweep ever supplies R1 or R2, because rule-independence
is not producible by the incumbent engine at any Nmax (B9). Sequencing
consequence: R1/R2 are worth buying regardless of the five-terms decision;
V1 only if five-terms is declined or far away.

**Where two routes look independent but are not** (B4, B5):

- Every tower statement about T(40,19) contains `D_3(21)`. V1's holdout
  framing (pin (2,4), predict j=3) and R2 (pin (4,5), predict j=3) share
  D_3(21), D_4(21) and the grand form; if the two towers agree with each
  other but disagree with the swept cell, the suspect is D_3(21) — their
  mutual agreement checks pinning cells, never the shared defect machinery.
  Only an enumeration (the incumbent's banked sweep, or Motley C_19) sits
  outside that family.
- Re-running the tower "under the other rule" adds nothing: the Motley-pinned
  and incumbent-pinned level-21 towers pin from the SAME (n,H) cells (j=3,4),
  so once the cells agree the towers are numerically identical. All
  cross-rule content lives in the cells.
- The W3 family tables feed every depth at every level; the gate checked them
  only at k <= 19. A shared-machinery error surfacing first at k >= 20 would
  move all depth pairs coherently and could pass every agreement-only check.
  This is the precise sense in which V1 (holdout against an enumeration) is
  stronger in kind than R2's agreement — and in which R1 is stronger than
  both for the one cell in question.

## 4. Job requests to the lead

Per brief §4; nothing here was run by this lane. Both change a real decision;
neither is urgent before the desk items (B13, B15) are done.

- **J1 — `motley_par --census 19 40`, dalby.** Exact H = 19 frontier state
  count (no payload). wall: EXTRAPOLATED ~1-3 h at 80 threads (census is the
  cheap mode; H = 18 modp full pass was 0.92 h/32t on ayr); RAM: EXTRAPOLATED
  ~15-25 GB (24 B/bucket x 2 tables at ~226M states, +-20%); disk: nil;
  cores: 80. **Decision changed:** prime width (u16 vs u8) and pass count for
  R1, hence whether R1 (~11-25 h) or R2 (~16 h) is the cheaper
  rule-independence route — and whether R1 fits dalby at all.
- **J2 — `severance_w3_families` at K = 14 then K = 16, dalby.** wall:
  EXTRAPOLATED ~15 min / ~50 min; RAM ~4 / ~10 GB; one core. **Decision
  changed:** whether the K = 21 (depth-5) run's 103-GB RSS extrapolation
  holds inside 125 GB, i.e. whether R2 is launchable on dalby at all.

## 5. Bottom line, ranked

For closing a(40)'s gap:

1. **R1, Motley C_19** (after J1 prices RAM; run at Nmax 41): rule-independence
   + cross-rule validation of T(40,19) in one overnight run; also hands the
   five-terms plan its second source for a(41). The single most decisive
   purchase available.
2. **R2, depth 5** (after J2 + the D_5 gate at k <= 19): rule-independent
   derivation + validation-by-agreement; also the second-pin fix for levels
   20-23. Weaker in kind than R1 for T(40,19), broader in reach for the tower.
3. **V1, H = 20 @ Nmax 41**: the strongest single check for a(41) and for
   the level-21 machinery (enumeration holdout), but for a(40)'s gap it is
   validation-only at the biggest disk price on the table — and it comes free
   inside the five-terms sweep if that launches. Buy it standalone only if
   five-terms is declined.
4. **V2, H = 21 @ Nmax 42**: dominated. Its historical justification (the
   P_19 seam) is already closed from banked data.

R1 and R2 together would give T(40,19) three assumption-disjoint sources
(incumbent enumeration, Motley enumeration, W3 tower) — more than any other
cell of row 40 has. That is not needed; either one closes the gap as stated.
