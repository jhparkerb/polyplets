# R1-K — pre-launch adversary on docs/rook1-brief.md

Filed 2026-08-13. Charter: two questions (premise truth; gate movement per
lane), verdict per lane and for the round. Everything below re-derived from the
repo on branch master, not from the brief's say-so. Arithmetic re-run in
python3 this session; the numbers quoted are those outputs.

## Q1 — Is the premise true?

### 1a. The 84% cpu split — CONFIRMED (results/ns_a40/PROVENANCE.md)

PROVENANCE.md:12-19 gives phase cpu: A = 871,963 s, B (H20 solo) = 1,116,858 s,
C (H21 solo) = 3,329,644 s. Sum = 5,318,465 s exactly as the brief states.
(B+C)/total = 4,446,502 / 5,318,465 = 0.83605 → "84%" is honest rounding.
Phases B and C are H=20 and H=21, i.e. k = 40−H = 20 and 19 as the goal file
says (rook-parity.md:60-63). One nit, immaterial: the goal says "kink sweep
H ≤ 19 (Phase A)"; Phase A is H1-19 **plus the closed-form band H22-40**
(PROVENANCE.md:12), so Phase A's 871,963 s slightly overstates the pure
H ≤ 19 sweep cost. Conservative in the route's favor.

### 1b. β < ln 2.42 / ln 1.73 = 1.61 — CONFIRMED (arithmetic), with a stated conditional

ln 2.42 / ln 1.73 = 1.6124. The kill logic is right: a size-β reduction costs
1.73^(βn) and beats a 2.42^n incumbent iff β < 1.6124. King-cell → 2×2 block
is β = 4 (n cells → 4n, linear); dead under every reading. Diagonal-splice
β ≥ 2 is asserted, not derived, in rook-parity.md:86 — but a β = 2 family dies
whenever the incumbent's base is < 1.73² = 2.993, which holds under all three
of the repo's post-kink readings (2.42, ~2.5, ~1.73; see 1d). Only the
pre-kink 4.4 reading (ln 4.4 / ln 1.73 = 2.70 > 2) would let a β = 2 splice
survive, and a(40) was produced by the kink kernel
(results/ns_a40/PROVENANCE.md:132). So the kill is robust to the base
contradiction, not contingent on resolving it. The one soft spot is the
asserted "diagonal-splice β ≥ 2"; R1-D's obstruction lane is where that either
gets derived or replaced.

### 1c. √λ sandwich and the vacuity of the 2.67 pin — CONFIRMED

√6.543 = 2.5579, √9.3154 = 3.0521; the brief's [2.558, 3.052] is correct
(2.558 rounds the lower end *up*, which is the safe direction for the vacuity
argument). 2.67 lies strictly inside. Every in-repo reading of the incumbent's
per-term base — 2.42 and ~2.5 (results/kink-carry.md:46-49), √3 ≈ 1.73 (the
PROVENANCE cpu ratio, 1d) — is below 2.5579, so the incumbent is below √λ_king
under every admissible λ regardless of which of the three contradictory base
claims wins. The 2.67 pin is unfailable by vacuity; the desk-refutation at
rook-parity.md:30 stands. (Sandwich endpoints themselves: banked, 9.3154 is
the exact-certificate value — results/kink-carry.md is not their source; taken
from the banked polyplet-upper-bound result as the goal does. Not re-proved
here.)

### 1d. The three contradictory base claims — CONFIRMED as mutually contradictory; what each asserts

- **results/kink-carry.md:46** — asserts the *pre-kink whole-column engine's
  per-term (per-n) compute growth* is ~4.4× = state growth (~2.42) ×
  masks-per-state growth (~1.8), and (line 48-49) that kink carry drops
  per-term compute to ~the state growth, **b ≈ 2.5**. Quantity: per-n cost and
  per-n state growth. Implied base: **2.42–2.5**.
- **results/kink-carry.md:69** — asserts frontier state count **D_H ~ 2.6^H
  with H ≈ n/2 − const**. Quantity: states per unit *height*. Per-n
  implication: √2.6 = **1.612**. This cannot coexist with line 46's per-n
  state growth of 2.42 — same engine family, same quantity (states), two
  numbers.
- **results/ns_a40/PROVENANCE.md:19,25** — line 19 (with line 16) gives
  measured production cpu: phase C / phase B = 3,329,644 / 1,116,858 = 2.981
  per unit height for the kink kernel at n=40; line 25 gives the structure
  (real sweeps to H21, H ≈ n/2 territory). Quantity: measured *cost* per unit
  height, 2.98 ⇒ per-n √2.98 = **1.727 ≈ 1.73**. Adjacent at line 20:
  "~2.7x per-column cost" (records), a third per-height number.

So the repo simultaneously supports per-n base 2.42–2.5 (kink-carry's stated
b), 1.61 (kink-carry's own frontier law), and 1.73 (the production cpu
measurement). These are not three phrasings of one number; at most one per-n
cost base is true. The brief's characterization is accurate, and R1-A's
charter (reconcile: which is the base, which is a bound on something else,
which is wrong) is exactly the right question. Note the delicious hostile
corollary R1-A must not dodge: if 1.73 is the real per-n cost base of the
shipped engine, the incumbent is already *at* rook parity and gate 1's
"strictly below the incumbent's curve" becomes the entire goal — the measured
clause matters more than the pin.

### 1e. Citation sweep — every checked citation readable and accurate

| citation | check | verdict |
|---|---|---|
| docs/rook-parity.md:106-123 (gates 0-3) | read; gates at lines 104-123, numeric | CONFIRMED — docs/rook-parity.md |
| docs/rook-parity.md:125-137 (first questions) | line 125 is the section head | CONFIRMED — docs/rook-parity.md |
| docs/rook-parity.md:88-90 (transport survivor lane) | exact text present | CONFIRMED — docs/rook-parity.md |
| results/kink-carry.md:46,69 | quoted above, 1d | CONFIRMED — results/kink-carry.md |
| results/ns_a40/PROVENANCE.md:19,25,132 | quoted above, 1a/1d | CONFIRMED — results/ns_a40/PROVENANCE.md |
| commit 210fb0b | msg: "diagonal sweep FALSIFIED: correct king diag TM base ~4.52 (worse), 2.04 was a phantom" | CONFIRMED — results/rook1/R1-K-checks.txt |
| severance §Ceiling: k=9 = 53 GB / 66 min / 16 threads dalby; k=10 past 125 GB, needs state-space reduction not cores | lines 42, 46-50 | CONFIRMED — results/severance-w1-anchor-cut.md |
| triangle-r3-involution §2: char-2 rank 0.42-0.45·2^H vs mod-p 2.5-2.8×/height | lines 304-309 | CONFIRMED — results/triangle-r3-involution.md |
| g2 --rook-bishop, rook-connected polyplets ARE polyominoes, A001168 | comment at lines 84-93; binary present | CONFIRMED — results/rook1/R1-K-checks.txt (source comment + binary listing) |
| Barequet–Moffie O(n^{5/2}·(√3)^n) | pdftotext abstract: verbatim "O(n5/2 (√3)n) on the running time" | CONFIRMED — results/rook1/R1-K-checks.txt (pdftotext capture) |
| record n=70, Algorithmica 2026 | pdftotext p.1: "count of polyominoes from 56 to 70 terms", "published at Algorithmica" 2026 | CONFIRMED — results/rook1/R1-K-checks.txt (pdftotext capture) |
| finite-lattice-crossover quotable only for FLM-doesn't-stack; floors two-thirds over-applied/false | both files read; r4-floors verdict lines present | CONFIRMED — results/finite-lattice-crossover.md, results/r4/r4-floors.md |
| docs/middle-kingdom-plan.md, docs/r3-job-dispatch.md, docs/skeptical-reader-standard.md, docs/triangle-postmortem.md | exist, non-empty | CONFIRMED — ls, this tree |
| receipts gate | target in Makefile:136; script present | CONFIRMED — scripts/check_receipts.sh, Makefile |
| queue/INSTRUMENTS/LEDGER open before spawn | all three exist with headers | CONFIRMED — results/rook1/queue.md, results/rook1/INSTRUMENTS.md, results/rook1/LEDGER.md |

One citation is misattributed, not wrong: the brief (rook1-brief.md:161) cites
`docs/agent-types.md:51-54` to bind R1-D to two successor rows; those lines
state the **scout** rule, and R1-D is an adversary. The obligation binds
anyway via the queue control (brief §Controls: "every closed candidate files
at least two successor rows"). No action needed; recorded so nobody
litigates it later.

Also verified negative: the goal's correction that `min(H,W) ≤ n/2` fails for
king animals is right (diagonal staircase, min(H,W)=n), and
results/finite-lattice-crossover.md:10-13 does claim the cap via the polyomino
bbox inequality — the correction is needed and correctly aimed.

## Q2 — Does each chartered deliverable move a gate?

- **R1-A** → moves **gate 1** (rook-parity.md:113-120): its second clause
  ("fitted per-term ratio over n=24..30 below the incumbent's curve") is
  currently unevaluable because the threshold does not exist. R1-A creates
  the number and the bar file registers it. Total-success hostile test: the
  bar moves from unstatable to numeric and failable — that is movement, and
  it is also the round deliverable's clause 1. It additionally resolves 1d,
  on which the β kill's headline constant and the g<5.9 threshold both lean.
  **PASS.**
- **R1-B** → **is gate 0** (rook-parity.md:111-112): "measure g … decides the
  route before any engine exists." Total success = gate 0 executed, go/kill
  decided against pre-registered thresholds. The strongest lane-to-gate
  coupling on the board. **PASS.**
- **R1-C** → moves **gate 0's route decision**, not a gate number: the k=10
  ceiling needs a state-space reduction (severance §Ceiling), the char-2 rank
  collapse is the only measured crack below Motzkin, and rook data is the one
  cheap test of whether that crack is lattice-general or king-only
  (rook-parity.md:132-136 charters exactly this). Hostile test: a "no crack,
  no king decision changes" outcome moves no gate number — but it banks a
  negative-map entry (counts under the strike rule) and closes a door round 2
  would otherwise re-open. This is the marginal lane; it survives because it
  is cheap, chartered by the goal file, and its null is bankable. **PASS**,
  with the note that its verdict must name the specific king decision changed
  or state "changes nothing" in so many words — the brief already requires
  this; hold R1-C to it.
- **R1-D** → moves no gate number; it is the process-sanctioned bounded
  "find a route" lane (process #7 amended; rook-parity.md:88-90), and either
  outcome is a negative-map entry, bankable under the strike rule. Its real
  gate value: it converts the one asserted number in the transport kill
  (diagonal-splice β ≥ 2, see 1b) into either a derivation or a sharper
  obstruction. **PASS.**

**Lead audit.** No silent caps found: the three held spawn slots are declared
(rook1-brief.md:102-104); the queue is open and append-only; the CLOSED list
is a negative map (doors, not candidates) and the brief hands out no candidate
list — "Nothing here tells you what to try" is accurate on inspection. R1-A's
"existing run logs only" and R1-C's "seconds-scale or job request, nothing in
between" are charter-faithful narrowings from the goal file, not lead
inventions. The round deliverable is genuinely falsifiable: a named file whose
absence is failure, plus queue close and a mechanical gate.

## Pre-registration audit — one real defect

The g thresholds are registered before measurement and the kill→go conversion
is reserved to jasonp: good. But the threshold table (rook1-brief.md:41-45)
is **not a partition**:

1. **The band 5.9 ≤ g ≤ 6 is unassigned.** "3 < g < 5.9" survives-but-beats-
   incumbent-only; "g > 6" kills. A measured g = 5.95 fires nothing, and the
   argument about it would happen *after* the number exists — precisely what
   pre-registration is for.
2. **"g ≲ 3" is not a number.** A measured g = 3.05 invites relitigation of
   "≲". The parity condition is exact: √g ≤ √3 ⟺ g ≤ 3.
3. **5.9 rounds the wrong way.** Beats-incumbent is √g < 2.42 ⟺ g < 5.8564.
   A measured g ∈ [5.8564, 5.9) would satisfy the registered clause while
   actually exceeding the incumbent's claimed base. Register 5.856 (or state
   g < 2.42², exact), not 5.9. (And note the boundary inherits R1-A's
   resolution of 1d — the brief should say the incumbent constant in this
   threshold is provisional on R1-A, fixed the moment the bar file registers.)
4. Cosmetic, record it once: the goal says "g ≫ 6 kills" (rook-parity.md:111)
   while the brief registers "g > 6". The brief's tighter form is the binding
   one, registered at brief time; fine, but the bar file should restate it so
   round 2 cites one number.

None of this is a lane defect — it is a table defect, fixable by the lead in
minutes, and it must be fixed **before** wave 2 spawns so that no threshold is
written after anyone has seen a measurement.

## Verdicts

| lane | verdict |
|---|---|
| R1-A | PASS — this file §Q2 |
| R1-B | PASS — this file §Q2 |
| R1-C | PASS (marginal; verdict must name the decision changed) — this file §Q2 |
| R1-D | PASS — this file §Q2 |
| round | PASS, conditional — this file §Pre-registration audit; condition in results/rook1/R1-K.PASS |

Premise items: 1a CONFIRMED, 1b CONFIRMED (with the β ≥ 2 assertion flagged to
R1-D), 1c CONFIRMED, 1d CONFIRMED (contradiction is real; statements pinned
above), 1e CONFIRMED with one misattributed-but-harmless citation. Nothing
came back WRONG; nothing material NOT ESTABLISHED. Hostility spent where it
belonged: the one genuine defect found is the threshold table, and it is
gating, not advisory.
