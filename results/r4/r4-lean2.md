# r4-lean2 — the encoding layer: source written, gates written, nothing built

> Some files cited below were filed on the unmerged branch `triangle-structure` and never reached this one: `git show triangle-structure:<path>`.

Scout/builder `r4-lean2`, round 4, 2026-08-13. Task: author the next increment
of the definition-level theorem (r3's L3-5), chosen to reduce the most
remaining risk; write it to compile; gate it GREEN/RED; and state the honest
position of statements (a) and (b).

**Standing label: I ran no compute of any kind. No `lake`, no `lean`, no `lake
env lean`, on any machine including gympie. Every Lean artifact named below is
UNCOMPILED. Nothing in this deliverable is a theorem until the lead's build
says so, and I do not describe my own source as correct anywhere in it.**

Artifacts, all UNCOMPILED:

| file | what | lines | Lean lines | decls | sorries |
|---|---|---|---|---|---|
| `experiments/tristruct/r4_lean2_encode.lean` | the encoding layer's faithfulness theorem, claimed complete | 390 | 204 | 20 | **0** |
| `experiments/tristruct/r4_lean2_state.lean` | the packaged finite state + three named holes | 269 | 109 | 15 | **3** |
| `experiments/tristruct/r4_lean2_gate.sh` | six gates: 1 byte-identity, 1 GREEN, 3 RED, 1 exact-hole-count | 205 | — | — | — |

("Lean lines" excludes the file header and all doc comments. For calibration
the funnel probe, which compiled, is 302/161/17/0 by the same counts.)

---

## 1. The increment I chose, and why it is not the easy one

**Chosen: increment 3, the encoding layer — E1 `State` and E2
`encode_faithful` — not increment 2 (D1 `reduction`, D2 `strand_dead`, D3
`sufficiency`).**

The brief said to go where the risk lives rather than where the work is easy,
and two independent readings on disk agree about where that is.
`results/r4/r4-lean.md` §1.2 concludes its own decomposition with "what is left
genuinely hard is the *encoding* layer, E2/E4 … it is where I would now expect
the schedule to slip". `results/r4/r4-adv-cost.md` §5.2 goes further and is
sharper: it accepts the funnel probe's calibration, agrees with the lane that
D1 follows easily — "I also independently worked whether D1 follows as easily
as claimed … **It does**" — and then names E2 as the single unpriced,
unattacked item, rejecting the lane's own "bookkeeping rather than mathematics"
verdict on it: *"The reverse requires showing the canonicalization is a normal
form for partitions under relabeling — a quotient argument, and the standard
place this kind of development stalls."* So the adversary has told us both that
increment 2 is now the easy one and exactly which sentence of increment 3 it
does not believe. Going to increment 2 next would be picking up the lemma the
hostile reader has already conceded, and would leave the one it named
untouched for another round. Increment 3 is also the increment that can be
attacked *now*: E2 does not depend on D1/D2/D3 — it is a statement about a
label function and the reachability relation on one column, with the sufficiency
theorem consuming it later rather than the other way round — so choosing it
costs no sequencing and blocks nothing.

**And the reason to write it rather than argue about it is that I think the
adversary's specific objection can be dissolved by a design choice, which is a
claim only a compile can settle.** r3, r4-lean and the adversary all picture the
state as a *canonical label vector* and expect a proof that canonicalization is
a normal form for partitions under relabeling. That is the quotient argument.
It is avoidable: define the label of a cut-column row *by the relation itself* —
the least row of the cut column reachable from it inside the prefix, and `⊤`
for a row the prefix does not occupy. Then "same label" is "same least element
of the class", which is "same class", because `reach P` restricted to the
column is an equivalence relation (`refl`, `reach_symm`, `ReflTransGen.trans`).
No relabeling, no quotient, no normal form. If the file compiles, E2 is not
merely reduced, it is gone, and the residue is one small packaging lemma
(HOLE 1). If it does not compile, we learn that at a cost of one 10-second
elaboration instead of a session of argument — which is the same trade that
made the funnel probe worth its slot.

---

## 2. What the two files contain

### 2.1 `r4_lean2_encode.lean` — claimed complete, zero sorries

Twenty declarations in four layers. The chain, in dependency order:

| decl | says | rests on |
|---|---|---|
| `reach`, `colAt`, `Unstranded`, `rowCls`, `lbl`, `encodeCol` | the vocabulary | — |
| `kingAdj_symm`, `reach_symm` | relation hygiene | copied **verbatim** from the compiled funnel probe |
| `mem_rowCls` | **the one bridge**: for an occupied cut-column cell, membership in its row class is "occupied, and reached inside `P`" | `Compute.lean`'s `reachSet_sound` (:83), `reachSet_complete` (:144), `iterate_stepExpand_subset` (:57) |
| `self_mem_rowCls`, `rowCls_eq_of_reach` | classes of related rows coincide | `reach_symm`, `ReflTransGen.trans` |
| `lbl_ne_top`, `lbl_eq_top`, `lbl_eq_top_iff` | the label reads off occupancy | `Finset.min_eq_top` |
| `lbl_eq_iff` | **the label reads off the component structure** | `Finset.min_of_mem`, `Finset.mem_of_min` |
| `encode_faithful` | the head theorem, row-indexed | all of the above |
| `mem_colAt`, `mk_mem_colAt`, `colAt_eq_iff`, `encode_faithful_colAt` | the same theorem in the form `sufficiency` will consume | `encode_faithful` |

Two things about this shape are deliberate and worth a lead's attention.

**It reuses `Compute.lean` instead of rebuilding connectivity machinery.**
`rowCls` is defined off the committed computable closure `reachSet`, so the
bridge between the `ReflTransGen` view and the closure view is made once, in
`mem_rowCls`, and nothing downstream touches `reachSet` again. This is the
direct application of R4-LEAN-3's lesson: r3's L5 lane re-derived
`canonical_x_le` from scratch — in the file that failed with nine errors at six
sites — while it sat committed and sorry-free at `Finite.lean:82`. I grepped
the committed tree before authoring, and the payoff is that the hardest
ingredient here (that path-reachability and closure-reachability agree) is
already a theorem in this build.

**There is no induction in the file.** Every proof is a case split, a rewrite,
or an application. The only inductive content is inside `reach_symm` (copied
from a compiled file) and inside `Compute.lean`'s closure lemmas (committed).
That is the structural reason I think the increment is smaller than the
adversary priced it, and also the reason its failure mode, if it fails, will be
`unsolved goals` at a named lemma rather than a diffuse mess.

### 2.2 `r4_lean2_state.lean` — three named holes, and a gate that counts them

The brief asked for `sorry`-marked skeletons with each hole named, in
preference to confident prose. The encode file is the exception and I say why
below; this file is the rule. It carries **exactly three** sorries:

| # | name | r4-lean §1.1 row | why open |
|---|---|---|---|
| 1 | `labelFin_faithful` | E2 residue | the `Fin H` packaging is injective on height-bounded prefixes; unattempted, expected short |
| 2 | `strand_dead` | D2 | unattempted; the adversary rates it non-trivial and I agree |
| 3 | `sufficiency` | D3 | increment 2; the funnel probe supplies both halves, the packaging is missing |

and its gate is not silence but **exit 0, zero `error:` lines, exactly three
`declaration uses 'sorry'`, and no other output**. Both directions bind: four
sorries fails and two fails. What a green gate here buys, with no `sorry`
involved in it, is that `State H` really has `Fintype` and `DecidableEq`
instances, that `rowFin`'s `Fin` bound discharges, and that `encodeState`
elaborates — so holes 1 and 3 are statements about a real object rather than
about `sorry`. A state type with no `Fintype` is not a state type, and that is
the class of thing that fails silently.

**Why the encode file has no `sorry` when the brief preferred them.** I could
not find a hole in it to name. Naming a hole I do not believe in would make the
gate lie; the discipline the brief is actually after — that the compiler, not
my prose, localizes the failure — is served here by *granularity* instead:
fourteen declarations, none longer than twelve lines, each provable in
isolation, so an error message names one step rather than an argument. The
funnel probe made the same choice and its RED landed at the designed line.

**What I declined to write.** `step` (E3), `step_correct` (E4), `frontierT`
(F1), `prefix_census` (F2), `completion` (G1), `frontierT_eq_T` (G2) and the
pins (H1) are not stated, in any form. A transition function has to be written
against the `reduction` lemma increment 2 produces; stating one now is guessing
at the shape of an object nobody has built, and a `def step := sorry` would
make every theorem downstream of it vacuous while looking like progress. §4
prices those rows as NOT ESTABLISHED rather than guessing at them.

### 2.3 The gate script

`r4_lean2_gate.sh`, in the shape of `r4_lean_funnel_probe.sh` — fail-closed on
missing inputs, missing toolchain, an empty log, and a mutation that turns out
to be a no-op; nothing written outside the repo, no `/tmp`; mutant copies
created and removed beside the sources.

| gate | kind | criterion |
|---|---|---|
| D | free | the `SHARED DEFS` block is byte-identical in the two `.lean` files |
| A | GREEN | the encode file elaborates, exit 0, **zero** bytes of elaborator output |
| B | **RED 1** | `rowCls` taken over all of `P` instead of the reachable closure — every cut-column cell falls in every class. Must be REJECTED |
| C | **RED 2** | the occupancy guard removed from `lbl` — an unoccupied row gets a real label. Must be REJECTED |
| E | exact | the skeleton: exit 0, zero errors, exactly three sorry warnings, nothing else |
| F | **RED 3** | `rowFin`'s range test weakened so `omega` cannot discharge the `Fin` bound. Must produce an error |

Three notes on the design, each of which is a deliberate difference from the
probe's gate rather than a copy of it.

- **RED 1 is the mutation that matters** and it is aimed at the file's semantic
  claim, not at an arithmetic step. "Every cut-column cell falls in every
  class" *is* the failure "the state cannot tell two components from one",
  which is the entire purpose of the encoding. The probe's single RED was a
  stencil token; this one is the proposition.
- **Gate D exists because the two files cannot import each other.** Neither is
  a module, so the six shared definitions are physically duplicated. Duplicated
  text drifts; a diff is free and runs before any elaboration. (The state file
  was *generated* by splicing the block out of the encode file, so the two
  start identical by construction.)
- **Gate A classifies a `#guard_msgs` axiom-pin mismatch separately** as
  `AXIOM-PIN-ONLY`, still failing and still exiting nonzero. A pin mismatch is
  a fact about the axiom footprint, not a hole in an argument, and the lead
  should not have to read the log to tell those apart. This one is a genuine
  guess, unlike the probe's: nothing in the encode file invokes choice
  explicitly, but `Finset.min`'s order instances on `WithTop ℤ` may drag
  `Classical.choice` in.

---

## 3. Identifier ledger

Every Mathlib and in-project name used in the two files, with where I read it.
This is the check r3's L5 lane is on record as having skipped; it is *not*
sufficient, because L5's nine errors were mostly holes in arguments rather than
identifier drift, but it removes one failure class.

**Read in the vendored mathlib at `v4.31.0` on 2026-08-13** (paths relative to
`polyplets/.lake/packages/mathlib/Mathlib/`):

| name | file:line | note |
|---|---|---|
| `Finset.min` | `Data/Finset/Max.lean:110` | **valued in `WithTop α`, `⊤` on `∅`** — not `WithBot`. The docstring is explicit and this is the single easiest thing to get backwards in this file |
| `Finset.min_of_mem` | `Data/Finset/Max.lean:134` | |
| `Finset.min_eq_top` | `Data/Finset/Max.lean:142` | `s.min = ⊤ ↔ s = ∅` |
| `Finset.mem_of_min` | `Data/Finset/Max.lean:145` | |
| `Finset.notMem_empty` | `Data/Finset/Empty.lean:104` | new-style `notMem` spelling |
| `Finset.mem_filter` | `Data/Finset/Filter.lean:127` | |
| `Finset.mem_image` | `Data/Finset/Image.lean:284` | `b ∈ s.image f ↔ ∃ a ∈ s, f a = b` |
| `Finset.ext` | `Data/Finset/Defs.lean:145` | |
| `Finset.decidableExistsAndFinset` | `Data/Finset/Defs.lean:365` | for `decide (∃ p ∈ P, …)` in `encodeState` |
| `Fintype.decidablePiFintype` | `Data/Fintype/Defs.lean:204` | `DecidableEq` for the label field |
| `WithBot.recBotCoe` | `Order/TypeTags.lean:59` | the `WithTop` dual is generated by `to_dual`; named only as the repair for fragile point 2 |

**Read in the project's own committed, sorry-free tree:**

| name | file:line |
|---|---|
| `kingAdj`, `KingConnected` | `Polyplets/Defs.lean:24,29` |
| `reachSet` | `Polyplets/Compute.lean:50` |
| `iterate_stepExpand_subset` | `Polyplets/Compute.lean:57` |
| `mem_iterate_self` | `Polyplets/Compute.lean:71` |
| `reachSet_sound` | `Polyplets/Compute.lean:83` |
| `reachSet_complete` | `Polyplets/Compute.lean:144` |
| `exists_adj_cross_of_reflTransGen` | `Polyplets/Finite.lean:61` (cited in HOLE 2's docstring as the committed lemma that will discharge it) |

**Verified by *use* in an already-compiled file in this tree, which is stronger
than a grep:** `Prod.ext_iff` (`Compute.lean:186`),
`Relation.ReflTransGen.head` (funnel probe:135), `Relation.ReflTransGen.trans`,
`Relation.ReflTransGen.refl`, `abs_sub_comm` (funnel probe:126),
`#guard_msgs` + `#print axioms` (funnel probe:281).

**Five fragile points are listed in each file's header with its repair**, so a
mechanical failure is one edit rather than a re-think. The two I rate most
likely: `noncomputable section` (whether `Finset.min` on `WithTop ℤ` resolves
to a computable order instance is NOT ESTABLISHED — `Compute.lean`'s `box`
docstring records that `Finset.Icc` on `ℤ` does not, which is why a section is
used rather than per-definition markers), and the `unfold lbl` + `rw [if_pos]`
idiom, which is used precisely because the funnel probe used it successfully on
`fnl`.

---

## 4. The honest state of (a) and (b)

### 4.1 (a), row by row against r4-lean's §1.1 graph

The graph has 25 rows. Their status this morning, with no rounding:

| status | rows | count |
|---|---|---|
| **COMPILED GREEN** | A1-A6, B1-B3, C1-C4 | 13 |
| **AUTHORED, UNCOMPILED, claimed complete** | E2 (`encode_faithful`, this session) | 1 |
| **DEFINED, UNCOMPILED** | E1 (`State`, `encodeState`, this session) | 1 |
| **STATED, sorry** | D2, D3 (this session), + E2's packaging residue | 2 |
| **NOT STATED IN ANY FORM** | D1, E3, E4, F1, F2, G1, G2, H1 | 8 |

Do not read "13 of 25" as 52% of the work. Row counts are the wrong unit and I
am giving the table only because it is checkable. The 13 green rows include the
crux, which is the one thing that was feared to be a month; the 8 unstated rows
include the transition function, which is the one thing nobody has looked at.

### 4.2 (b) is untouched, and the round should stop saying "(a)+(b)"

Statement (b) — the harness's Part-3 wording implements (a) — reduces, per
`results/triangle-r3-l3-proofscope.md` §1, to "the Lean definition mirrors
these ~40 lines" of `r3_l3_schema_dp.py`. **The Lean definition it must mirror
is `step`, and `step` does not exist in any form: not as a definition, not as a
statement, not as a `sorry`.** Nothing in the funnel probe or in either of my
files touches (b), and no artifact in the campaign does. (b) becomes assessable
on the day E3 is written and not before. Every sentence in the round's
deliverables of the form "(a)+(b) closes the objection for 95.85%" is therefore
resting one of its two halves on an object that has not been started. That is
not an argument against the programme — (b) really is the cheap half, and
"literalness, not proof" is the right method for it — but the phrase is
currently doing work the artifacts do not support, and a referee would notice
before we did.

### 4.3 Where the risk actually is now

**It moved again, and it is E3/E4, the transition function and its
correctness.** The reasoning, and each link is checkable:

1. The crux (C1/C2, partition sufficiency) is retired — MEASURED, funnel probe
   gate A, axiom footprint clean of `sorryAx`.
2. D1 is conceded easy by the adversary who was looking for reasons it was not
   (`r4-adv-cost.md` §5.1, its own independent working).
3. E2 was the adversary's pick for the new concentration. If my file compiles,
   the specific mechanism it feared — a normal-form-under-relabeling quotient
   argument — never appears, because the canonical form is defined by the
   relation. **If it does not compile, E2 is exactly as bad as the adversary
   said and this paragraph is void.**
4. That leaves E3/E4 and F2. Of these, **E4 `step_correct` is the only
   remaining row that consumes another hard row** — it needs D2 `strand_dead`,
   which is a soundness *and* completeness claim about the death rule, i.e. a
   claim about columns the DP has not read. Everything else is downstream
   assembly.
5. F2 `prefix_census` is the only genuine induction left in the whole graph
   (over columns, with a cell budget). It is uncalibrated and I have no anchor
   for it.

So: **E4, gated on D2, is the new concentration; F2 is the new uncalibrated
induction.** I am filing that as a prediction, not a measurement, and it is the
third time this campaign has moved the risk concentration rather than reduced
it. The pattern is worth naming: each increment retires the thing that was
feared and reveals the thing behind it, and the total has not yet come down.

---

## 5. Pricing, and where I refuse to price

`results/r4/r4-adv-cost.md` §5.2 is right that increments 3-6 of r4-lean's
schedule were "priced on nothing", and the correct response is not a
better-argued guess.

### 5.1 The anchors that exist (MEASURED)

| quantity | value | source |
|---|---|---|
| single-file elaboration, Mathlib-importing, ~300 lines, 8 short tactic proofs | **9.61 s wall** | `r4_lean_funnel_probe.log`, gympie, v4.31.0 |
| peak RSS, same | **5,515,296,768 B (5.5 GB)** | same log |
| author-to-first-compile-green, one agent session, zero repair rounds | **n = 1** (the funnel probe) | `r4-lean.md` + the log |

That third row is the only pricing anchor the campaign has for *proof
authoring*, and it is a single observation. It is also the most flattering one
available, since the probe was designed to be the smallest possible increment.

### 5.2 What I can price from them

| item | estimate | label |
|---|---|---|
| gate A elaboration (encode file, 204 Lean lines vs the probe's 161, one extra import, no `decide`/`native_decide`) | **8-15 s** | EXTRAPOLATED from a MEASURED anchor |
| gate E elaboration (state file, 109 Lean lines) | **8-15 s** | same |
| the three RED elaborations | **8-15 s each** | same |
| **whole gate script, five elaborations sequential + `lake` startup** | **1-3 min** | EXTRAPOLATED |
| peak RSS, any one elaboration | **5.5-6 GB** | MEASURED anchor, +0.5 GB ASSERTED for the extra import |
| repair rounds if gate A fails mechanically | **1-2 more runs**, each 1-3 min | ASSERTED — the five fragile points each carry a one-edit repair, but nothing measures how many fire |

### 5.3 What I refuse to price

- **Increment 4 (E3 `step` + E4 `step_correct`): NOT ESTABLISHED.** No anchor
  exists and I decline to invent one. What I can say is structural rather than
  numeric: it is the only remaining row that consumes another hard row (D2),
  and it is the first row in the graph that requires *inventing* an object
  rather than proving something about an object the definitions already name.
  Every prior increment, including this one, had its target determined by
  `Defs.lean`; `step` does not.
- **Increment 5 (F1/F2/G1/G2): NOT ESTABLISHED.** F2 is an induction over
  columns and no comparable induction has been done in this development.
  `Finite.lean`'s three cut lemmas are ~15 lines each but none carries a state
  across the cut, which is precisely the difference (r4-lean §2.1 made the same
  observation about a different layer, and it was right there too).
- **Total sessions to the head theorem: NOT ESTABLISHED.** r3 said 3-5,
  r4-lean said 5-7; neither number had an anchor under the encoding layer and
  now neither has one under the transition layer. **A third guess would be
  worse than no number**, because it would look like a revision of a
  measurement. If the lead needs a planning figure, the defensible statement is:
  two increments (2 and 3) are authored or nearly so, and three (4, 5, 6) are
  unpriced, one of which requires designing an object that does not exist.

### 5.4 One correction to the inherited numbers

`r4-adv-cost.md` §5.3 is right that r4-lean's job request reported **two**
gympie limit breaches when there was one. Wall was estimated 6-16 min against a
measured 9.61 s, a factor of ~50 in the conservative direction; the only real
breach was RAM. I inherit the same single breach and no other: my five
elaborations at ~5.5 GB each exceed the standing 2 GB limit and nothing else
does. There is no way to bring a Mathlib-importing elaboration under 2 GB, so
the choice is per-job approval or no Lean on gympie — which is what queue row
**R4-LEAN-1** (elan + `lake exe cache get` on ayr) exists to remove permanently.

---

## 6. The job request

```
job id:            R4-LEAN2-JOB-1
measures:          (i) whether the encoding layer's faithfulness theorem
                   elaborates as written — i.e. whether defining the canonical
                   label as the least reachable row dissolves the
                   normal-form/quotient argument r4-adv-cost §5.2 predicted;
                   (ii) whether the packaged finite state type and the three
                   hole statements type-check.
decides:           whether E2 is closed or is exactly as bad as the adversary
                   said; whether increment 4 (E3/E4) can be dispatched against
                   a real State type or has to design one first; and which of
                   the five fragile points, if any, cost a repair round.
command:           sh experiments/tristruct/r4_lean2_gate.sh \
                     /Users/jasonp/src/polyominoes
script:            experiments/tristruct/r4_lean2_gate.sh — six gates, D A B C
                   E F in that order, fail-closed on missing inputs, missing
                   toolchain, no-op mutations and an empty log. Writes
                   experiments/tristruct/r4_lean2_gate.log. Mutant copies are
                   created and removed inside the repo; no /tmp.
box:               gympie ONLY. Not a preference: r4-lean.md §4.1 MEASURED that
                   neither ayr nor dalby has elan, lake or lean, and neither
                   has a .lake/build for mathlib or the project.
cores:             1 — the gates run sequentially, never concurrently.
wall estimate:     1-3 min for all six gates, EXTRAPOLATED from the MEASURED
                   9.61 s of r4_lean_funnel_probe.log. Five elaborations of
                   109-204 Lean lines each, import-dominated, no decide or
                   native_decide anywhere. Gate D costs nothing (two awks and
                   a diff).
RAM estimate:      5.5-6 GB peak RSS per elaboration, sequential so never
                   summed. 5.5 GB is MEASURED (same log); the +0.5 GB for the
                   extra import (Polyplets.Compute rather than
                   Polyplets.Finite) is ASSERTED.
disk estimate:     log ~10-30 KB; mutant copies ~14-18 KB each, removed by the
                   script. No download. Nothing under /tmp.
interruptible:     yes — stateless and rerunnable. A kill loses the log and
                   may leave experiments/tristruct/r4_lean2_mutant.lean behind.
GYMPIE LIMIT:      **exceeds the standing limit on RAM and needs jasonp's
                   per-job approval. One breach, not two** — the 2 GB limit
                   (1 GB/core x 2 cores) against ~5.5 GB. Wall (1-3 min) and
                   cores (1) are inside the limits with room. This is the same
                   single breach the funnel probe had, and r4-adv-cost.md §5.3
                   is on record correcting r4-lean for reporting it as two.
if approval is
refused:           run gates D, A and B only (~30 s, same RSS) — that still
                   answers the increment's question and exercises the RED that
                   matters, at the cost of leaving the skeleton and two REDs
                   unrun. Better: stand up elan on ayr first (R4-LEAN-1) and
                   run there with no limit, which is the right trade now that
                   the campaign has at least three more Lean increments.
RED controls:      three, all in-script. B: rowCls over-merges (the semantic
                   heart). C: lbl loses its occupancy guard. F: rowFin's Fin
                   bound cannot be discharged, which is what makes gate E's
                   zero-errors clause non-inert. A fourth (drop reach_symm in
                   rowCls_eq_of_reach) is documented in the encode file's
                   header for a later pass and is not run.
closes:            results/r4/r4-adv-cost.md §5.2 — "increments 3-6 have no
                   anchor" — for increment 3 only, and only in the direction
                   the gate reports. §5 above leaves 4-6 NOT ESTABLISHED.
```

---

## 7. NOT ESTABLISHED

- **Everything Lean in this deliverable is UNCOMPILED.** I ran no Lean on any
  machine. The claim that the min-representative encoding dissolves the
  quotient argument is a claim about source that has never been elaborated, and
  it is the same class of claim r3's L5 lane got wrong at nine errors and six
  sites. R4-LEAN2-JOB-1 exists to settle it, and I have designed the gate on
  the assumption that I have made that mistake.
- Whether `Finset.min` on `WithTop ℤ` resolves to a computable order instance
  in this Mathlib. `noncomputable section` is correct either way, which is why
  it is used, but the consequence — that no `decide`/`native_decide` sanity pin
  on the encoding is available — is unconfirmed in both directions.
- The `#guard_msgs` axiom footprint pinned at the foot of the encode file
  (`[propext, Classical.choice, Quot.sound]`) is a guess, not a prediction from
  a known use of choice. Gate A reports a pin-only failure separately for this
  reason.
- Whether `Fintype (State H)` and `DecidableEq (State H)` resolve by
  `inferInstance`. The two `example`s in the state file are there to find out;
  I did not verify the instance chain past `Fintype.decidablePiFintype`.
- Session cost of increments 4, 5 and 6 — see §5.3. Not estimated, not
  extrapolated, not asserted.
- Whether HOLE 2 `strand_dead` as I have stated it is the exact condition the
  production engines' death rule implements. The statement is the one I believe
  is true and sufficient; the match to the harness's Part-3 wording is an
  inspection claim nobody has made, and it is the same item r4-lean §7 left
  open.
- Whether the `Unstranded` hypothesis is needed in HOLE 3 `sufficiency` at all,
  given that `encodeCol` equality already forces cut-column agreement. I
  carried it from the funnel probe's footer rather than dropping it; if
  increment 2 finds it redundant, the statement gets simpler, not weaker.

---

## 8. Successor queue rows

Four filed in `results/r4/queue.md`, three different in kind (proof increment,
a correction to how the round states its own result, a cross-lane audit) plus
the deferred RED:

- **R4-LEAN2-1** — increment 4, E3 `step` + E4 `step_correct`, named as the new
  risk concentration and as the first row that requires *inventing* an object.
- **R4-LEAN2-2** — (b) is untouched and the round should stop writing "(a)+(b)"
  until `step` exists. A correction to the campaign's own prose, not to a
  number.
- **R4-LEAN2-3** — the deferred fourth RED (drop `reach_symm` in
  `rowCls_eq_of_reach`) plus the general principle it stands for: this
  campaign's REDs have been one-token arithmetic mutations, and the ones that
  test *propositions* are the ones worth a slot.
- **R4-LEAN2-4** — the risk concentration has now moved three times without the
  total coming down; someone should audit whether that is progress or a
  treadmill, and the lane that produced it is the wrong lane to ask.
