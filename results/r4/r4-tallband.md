# r4-tallband — what actually establishes T(40,H) for H = 22..40

SCOUT, round 4. Question: what establishes the H = 22..40 block of row n = 40,
and is any of it second-sourced?

**Verdict in one line: `r4-gen4` §1.1's row for this block is wrong on two of
its three clauses, and the block is not a fifth epistemic object at all — it is
a Lean-verified function of thirty named cells at H ≤ 20, of which twenty-three
already have an exact second source today.**

Every share below is MEASURED by desk arithmetic on `results/triangle.txt`
row n = 40 (a(40) = 56,749,893,611,764,175,164,545,926,946,127).

---

## 1. The corrections to the accounting table

`r4-gen4` §1.1 files the block as:

> | H = 22..40 | **4.1449%** | **never swept by anything**; closed-form injection; outside the Lean theorem's scope |

Clause by clause:

| clause | verdict | evidence |
|---|---|---|
| 4.1449% | **CORRECT** | MEASURED, reproduced: 4.14487% |
| "closed-form injection" | **CORRECT** | `results/ns_a40/PROVENANCE.md`: "Real sweeps H3-H21; H22-H40 via wired P_k closed forms (k = 40−H ≤ 18)" |
| "never swept by anything" | **MISLEADING** | true of the *cells* at n = 40; false of the *rule*. Every P_k, k ≤ 18, has a passed real-swept holdout (same file, "Mass P_k holdout certification") |
| "outside the Lean theorem's scope" | **FALSE — INVERTED** | see §1.1 |

### 1.1 The Lean scope claim is backwards

`polyplets/PROOF-STATUS.md`, line 6, verbatim:

> The engine wires k = 0..19. Lean covers **k ≤ 18**, all grand-pinned from
> two real-swept cells per level.

At n = 40, k = 40 − H, so k = 0..18 **is exactly H = 40..22**. The Lean theorem
`P<k>_grand_of_banked`, k = 1..18, sorry-free, pins the production polynomial
for all n ≥ 2k+1 given two real-swept anchor cells per level. k = 19 — which at
n = 40 is **H = 21**, the cell this round is spending a cross-ISA production run
on — is the one deliberately *not* formalized.

So the true statement is the reverse of gen4's: **the H = 22..40 block is the
only part of row 40 whose generating rule is machine-checked in Lean**, and the
swept bulk (H = 15..19, 43.84%) is the part with no Lean coverage at all.
gen4's "95.85% = the Lean statement's scope is exactly the swept cells" has the
two sides of the split exchanged.

Supporting: `Polyplets/Grand/Audit.lean` records `grand_form` at
`[propext, Classical.choice, Quot.sound]` — standard axioms, no `native_decide`
in the cone; `P<k>_grand_of_banked` adds only `P3_pinned`'s heavy-k = 3
`native_decide` set. Build receipt `polyplets/build-receipt-2026-07-30.log`
(rev `7a62883`, 8592 jobs up-to-date, Lean v4.31.0).

### 1.2 The lead's k ≤ 3 premise is also wrong

The dispatch said `docs/proofs/diagonal-law.md` "scopes the sharp onset to
k ≤ 3, i.e. H ≥ 37". It does not. The header's "k ≤ 3" is the scope of the
*machine checker* (`experiments/diagonal_law_proof_check.py`, `KMAX = 3` at
source line 22 — MEASURED). The theorem statement is:

> **THEOREM.** For every k ≥ 0 there is a polynomial q_k of degree ≤ k with
> T(n, n−k) = P_k(n) · 3^(n−1−3k) for all n ≥ 2k+1

At n = 40 the tightest cell is H = 22 (k = 18, onset n ≥ 37). **40 ≥ 37: every
cell of the block is inside the proved onset**, with three to thirty-nine rows
of margin. Onset *sharpness* (failure at n = 2k) is the file's open item, and it
is a claim about the region below onset — irrelevant here.

MEASURED spot checks against the closed forms proved from first principles:
T(40,40) = 3^39 ✓, T(40,39) = 955·3^36 ✓.

### 1.3 The corrected row

Replacement for gen4 §1.1's last row, for lanes now quoting that table:

| H = 22..40 | 4.14487% | derived, not counted: shape theorem + grand form (both proved, `grand_form` Lean standard-axioms) evaluated on **30 real-swept anchor cells at H ≤ 20**. Machine-checked in Lean for k ≤ 18 — the *only* block in row 40 that is. Its grade is the grade of its anchors, not a grade of its own. |

---

## 2. Where the block's mass actually sits

MEASURED, per height:

| H | k | onset | share of a(40) | cumulative |
|---|---|---|---|---|
| 22 | 18 | n ≥ 37 | **1.82621%** | 1.82621% |
| 23 | 17 | n ≥ 35 | 1.09960% | 2.92581% |
| 24 | 16 | n ≥ 33 | 0.61898% | 3.54479% |
| 25 | 15 | n ≥ 31 | 0.32470% | 3.86949% |
| 26 | 14 | n ≥ 29 | 0.15813% | 4.02762% |
| 27..40 | 13..0 | — | 0.11725% | **4.14487%** |

The block is its own bottom two rows: H = 22 and H = 23 are 70.6% of it, and
everything at H ≥ 27 together is 0.117% — a rounding error. **Any statement
about this block is really a statement about P_18 and P_17.**

---

## 3. What the block actually depends on: thirty cells

`polyplets/PROOF-STATUS.md`, "Anchor provenance, measured (2026-07-30,
AUDIT-2026-07-30 L7)": the Lean pin for k ≤ 18 takes as hypotheses the 30 cells
`T(2j+1, j+1)`, `T(2j+2, j+2)` for j = 4..18 — "every one with H ≤ 20 and every
one REAL-SWEPT". Levels ≤ 3 are discharged from `P1_closed`/`P2_closed`/
`P3_pinned`.

That audit split them 19 strip-second-sourced / 11 kink-only:

    T(28,15) T(29,15) T(30,16) T(31,16) T(32,17) T(33,17)
    T(34,18) T(35,18) T(36,19) T(37,19) T(38,20)

**That audit is eleven days stale.** B1 landed 2026-08-11 and was banked
2026-08-12 (`results/cutcount_b1/`), and its exact rows reach H = 16 at all
n ≤ 40. Recomputing the four H = 15,16 anchors from the banked B1 rows by
`T(n,H) = C_H(n) − 2·C_{H−1}(n) + C_{H−2}(n)` — MEASURED, desk arithmetic on
`results/cutcount_b1/rows/C{14,15,16}.out`:

| anchor | B1 value | matches `triangle.txt` |
|---|---|---|
| T(28,15) | 343733831675681363476 | ✓ |
| T(29,15) | 2611110015255604740530 | ✓ |
| T(30,16) | 13969442417594351366268 | ✓ |
| T(31,16) | 106848447386284024770292 | ✓ |

So the ledger today is **19 strip + 4 B1 = 23 exact-second-sourced, 7
kink-only**:

    T(32,17) T(33,17) T(34,18) T(35,18) T(36,19) T(37,19) T(38,20)

This is the answer to the dispatch's question 2. The block was never "touched by
nothing". It was touched by two proved theorems and thirty cells, twenty-three
of which have an independent exact count.

### 3.1 What the strip does and does not reach

CONFIRMED, as the dispatch asked: `results/ns_a40/PROVENANCE.md` §"Strip second
source" — the strip TM extension to N = 40 completed 2026-07-30, 469 cells, 0
mismatch, and covers **H ≤ 14 only**. It touches no cell of the H = 22..40
block directly and never will. Its whole contribution here is indirect: 19 of
the 30 anchors.

### 3.2 What R4-G3-01 does and does not establish

`r4-gen3`'s reconciliation of the phase checkpoints against the per-height files
and `combine.log` on all 40 rows is a **harvest/combine** check: it proves the
number written to `perheight/h22.out` is the number `contributeDiagonalStrip`
produced, and that nothing was lost or double-counted between the sweep and the
banked triangle. It says nothing about whether `diagonalCell(40, 18)` is the
right integer. It is the check that would have caught the Zero Harvest incident,
and that is its actual scope.

---

## 4. Second-sourcing the block: the cheapest route, priced

The block needs no counting rule of its own. It needs its seven remaining
anchors. That reframing is what makes it cheap, and it produces three tiers.

### Tier 1 — 0.27538% of a(40), **zero marginal compute, available today**

k ≤ 14 (H = 26..40). Its anchors are j = 4..14, topping out at T(29,15) and
T(30,16) — both B1-exact per §3, both verified above. Nothing is missing.

Work required: none on any machine. `PinGrand.lean` already takes these cells as
hypotheses; the change is a provenance sentence in `PROOF-STATUS.md` recording
that j = 13 and j = 14's anchors are now two-sourced, superseding L7.

I checked whether the same trick lifts j = 15 by re-choosing its anchors, since
the Lean theorem accepts any two in-onset points: diagonal 15 needs n ≥ 31 and
B1 reaches H ≤ 16, so the only qualifying cell is T(31,16). One point, two
unknowns (a_15, b_15). **j = 15 provably cannot be re-anchored below H = 17.**

### Tier 2 — a further 2.04328% (H = 23..25), **zero marginal compute, as a by-product of the ladder already planned**

`r4-ladder` §item 4 (MEASURED framing, its own finding): the H = 17,18,19 ladder
predicts `C_H(n) mod p` for **all 40 values of n**, not just n = 40, because
`C_15`/`C_16` are banked exact and `T(n,17)` is banked. So a ladder run for
H = 17,18,19 confirms T(32,17), T(33,17), T(34,18), T(35,18), T(36,19),
T(37,19) at no additional cost whatever — they fall out of the same windows.

Those six are exactly the anchors for j = 15,16,17. Landing them takes
H = 23,24,25 to the same grade as the H = 17..19 band itself.

**Honest caveat, and it is the one that matters.** The ladder produces
*residues*, not integers. A mod-p residue confirms an anchor; it does not
reconstruct one, and it cannot discharge the Lean hypothesis, which needs the
exact integer. Tier 2 raises H = 23..25 from "kink-only" to "kink + confirmed
mod p by a rule that never decides connectivity" — the same grade, and the same
caveat (`r4-ladder` §4.4: a systematic error shared by both rules is caught by
no number of primes), as the H = 17..19 band the residues come from. It is not
the exact two-sourcing Tier 1 gives.

### Tier 3 — the last 1.82621% (H = 22) is gated on one cell

P_18's second anchor is **T(38,20)**, and nothing reaches it:

- strip stops at H = 14;
- B1's exact binary stops at H = 16;
- the planned ladder stops at H = 19;
- the spin route is a parity bit, not a count.

Its present grade is cross-run, cross-revision, single-kernel: H = 20 was swept
in the a(38), a(39) and a(40) runs and agrees digit-for-digit, plus the a(40)
H = 20 byte-identical standalone re-sweep (`results/ns_a40/recheck/`). That
rules out machine, build and transient faults, not a logic bug in the kernel.

Cost to recount it, EXTRAPOLATED and I would not defend the second digit:
extending `r4-ladder`'s own H = 18 → 19 step ratio (22.7 h → 79.3 h; 63.8 GiB →
197.6 GiB) one more tier gives **~277 h and ~612 GiB per prime** for H = 20.
612 GiB fits neither dalby (126 GiB) nor ayr (78 GiB). Reducing maxn from 40 to
38 buys about 5% and changes nothing.

I looked for a structural escape and did not find one. The obvious idea — that
tall-narrow animals are nearly paths, so transpose them into B1's H ≤ 16 reach —
**fails on king adjacency**: a diagonal staircase of L cells spans L rows and L
columns, so a height-H animal of n cells has width bounded only by n, not by
n − H + 1. The bound that makes the trick work for edge-connected polyominoes
(n ≥ H + W − 1) is false for polyplets. I record this as a killed idea so nobody
re-derives it.

**Tier 3 is NOT ESTABLISHED as reachable.** H = 22 stays kink-only unless
something new appears.

---

## 5. The comparison that decides where effort goes

Cost per percent of a(40), thread-hours. Ladder walls from `r4-ladder` §1.4
(MEASURED-anchored at H ≤ 16, extrapolated above); spin bracket from
`r4-adv-cost` §4.1 (6.6–33 thread-hours for the whole of m = 18..21).

| route | share of a(40) | marginal cost | th/% | what it delivers |
|---|---|---|---|---|
| **(a1) block Tier 1, H = 26..40** | **0.27538%** | **0** | **0** | **exact recount of every anchor** |
| **(a2) block Tier 2, H = 23..25** | **2.04328%** | **0** (by-product) | **0** | mod-p confirmation of every anchor |
| (a3) block Tier 3, H = 22 | 1.82621% | ~277 h, 612 GiB — fits nothing | n/a | — |
| (b) H = 21, spin | 2.8431% | 6.6–33 th (buys H = 20+21 = 7.0013%) | 0.94–4.71 | one parity bit, and `r4-inv` shows it is not independent of B1 |
| (c) H = 17,18 ladder, 2 primes | 16.4767% | 58.6 th | 3.56 | mod-p confirmation |
| (c) H = 17,18,19 ladder, 2 primes | 22.1993% | 217.2 th | 9.78 | mod-p confirmation |

**Plainly, as the dispatch asked: yes, this block is cheaper per percent than
anything the round is doing — 2.31866% of a(40) at zero marginal thread-hours,
against 0.94 th/% for the cheapest live route.** That is 82% of the block gen4
called unconfirmed, and it comes from bookkeeping on results already banked plus
a by-product of a job already planned.

The number to quote is **2.31866% for free**, and the action is not a job. It is
(i) recording the B1 anchor upgrade in `PROOF-STATUS.md`, superseding L7, and
(ii) making the ladder emit and bank its full n = 1..40 residue rows rather than
only the n = 40 cells, so Tier 2 actually lands instead of being discarded at
harvest.

Item (ii) is the one that can silently fail. If the ladder run is configured to
report only row 40, the six anchor confirmations are computed and thrown away.

### What I did *not* establish

- Tier 3's cost is EXTRAPOLATED one tier past the last measurement, from a
  two-point ratio. `r4-ladder` itself declines to extrapolate six heights from
  three points, and I am doing worse; treat ~277 h / ~612 GiB as an order of
  magnitude, not a figure.
- I did not verify that `scripts/gen_grand_pin.py` regenerates cleanly against
  substituted anchor values. Tier 1 assumes the generator is anchor-agnostic
  because `PinGrand.lean` is described as generated and fail-closed; that is
  ASSERTED from the file's description, not run.
- The spin bracket buys H = 20 and H = 21 jointly; I could not separate H = 21's
  share of it, so (b)'s th/% is generous to the spin route.

---

## 6. Queue rows filed

Appended to `results/r4/queue.md` as `R4-TB-01 .. R4-TB-04`.
