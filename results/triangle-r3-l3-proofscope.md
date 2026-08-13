# L3-2 proof scope — prove the frontier rule instead of varying it

2026-08-12, L3 scout, dispatched by the lead from queue row L3-2. Companion
to `results/triangle-r3-l3-contour.md`. New measurement artifact:
`experiments/tristruct/r3_l3_schema_dp.py` (+ `.log`) — see §3.

## 1. The (a)/(b)/(c) line, answered first

**(a) The abstract frontier recurrence counts exactly the king-connected
n-cell sets of height exactly H — reachable, and half of it already exists
in the committed Lean development.** `polyplets/Polyplets/Defs.lean` defines
`kingAdj`, `KingConnected` (Mathlib `Relation.ReflTransGen`, no algorithm),
`IsCanonical n H`, and the abstract `T n H`; `Compute.lean` defines a
computable brute-force `Tc` and **proves `Tc_eq_T`**, with native_decide
pins on small cells; `Sequence.lean` proves `a(n) = Σ_H T(n,H)` and pins
a(1..6). None of this was assumed — checked in the working tree today. What
does not exist anywhere is a Lean *frontier DP* and the theorem that it
equals `T`. That theorem is (a), and it is a lemma-sized target (§4).

**(b) The harness Part-3 wording implements (a) — handled by literalness,
not by proof.** The Lean DP is written as a transcription of the three
shared propositions, and the transcription question is settled by an
executable spec: `r3_l3_schema_dp.py` implements the three propositions
verbatim (stencil, label-partition + stranding, completion predicate) with
no engine code, and reproduces the banked triangle exactly on all 45 cells
1 ≤ H ≤ n ≤ 9, fail-closed, with a RED run (stencil deliberately narrowed
to {r−1, r}) caught at 15 mismatches. (b) reduces to "the Lean definition
mirrors these ~40 lines", an inspection claim made as small as it can be.

**(c) The compiled kernels implement (b) — out of reach, and not
proposed.** That is program verification of optimized C++: the kink carry
byte, packed signatures, mask pre-pruning, the Go orchestrator, resume
logic. Nobody should price that as sessions. **The line falls between (b)
and (c).**

## 2. What a referee actually gets from (a)+(b)

The chartered objection — `2b3115b`, quoted by the brief as "a shared
misconception about *what is being counted* passes through both and shows
up as agreement" — is an objection to the **rule schema**, and (a)+(b)
closes it at the definition level: the schema becomes a theorem relative to
a connectivity definition the counter never implements (Mathlib
reachability; independently, L5's `r3_l5_king_connected.lean` formalises
the same object a second way). It covers every swept cell at once — all
`real-sweep` provenance, H = 3..21, **95.85% of a(40)** — with zero
enumeration, and it is the only instrument in the round that touches 100%
of the band rather than a residue of it.

What it does **not** buy, said plainly: implementation faults of
individual binaries. After the proof, the residual hypothesis space is
"one binary has a bug on cells only it swept" — in-band H = 15..21 is a
single kink-kernel computation, and a theorem about the schema does not
re-run it. Two consequences worth writing down:

- **Retroactive upgrade of the existing agreements.** The strip-TM's 469
  cells, the dual production kernels, and symtm agree *as implementations
  of a schema*; today that agreement is discounted wholesale because the
  schema itself was unproved (the 2b3115b ruling). With the schema proved,
  those agreements become independent-implementation cross-checks of a
  proved rule — different codebases have disjoint bug modes, which is
  exactly the argument the ruling said was insufficient *while the shared
  rule was in doubt*. The H ≤ 14 story strengthens without a single new
  cycle.
- **The right partner is L6-1.** The proof closes the rule half; a mod-p
  recount by a different rule class (L6-1's cancellation DP) closes the
  implementation half on the band. Either alone leaves the objection it
  cannot reach; together they are the complete answer the round was
  chartered to find. Filed as a queue row.

## 3. Measurement anchor (this session, laptop)

`experiments/tristruct/r3_l3_schema_dp.py`, from scratch, no engine code:

- GREEN: all 45 banked cells 1 ≤ H ≤ n ≤ 9 reproduced exactly
  (41 s total; peak 3,360 states at H = 9 — the (partition × flags)
  refinement of Motzkin M(10)−1 = 2,187, as expected).
- RED: stencil narrowed to {r−1, r} → 15 mismatches, abort
  (scratch copy; command in the session log).

This file is the pre-verified numeric spec the Lean skeleton mirrors, the
same discipline every Notary wave used (skeletons pre-verified, agents
never change statements).

## 4. Exact Lean scope

New modules under `Polyplets/` (names provisional), vocabulary of
`Defs.lean`/`Compute.lean`, no new axioms beyond the standard three +
named native_decide leaves:

1. **FrontierDef.lean** — computable: `State H` = canonical label vector +
   two sticky flags; `step` = the three-proposition transition;
   `frontierT n H` by fold with cell budget (termination: each column
   places ≥ 1 cell). Fable-drafted skeleton, statements only.
2. **FrontierPrefix.lean** — the load-bearing induction. `stateOf S c` =
   (partition of S's column-c cells by connectivity-in-S, flags); theorem:
   after k columns the DP's (state → count-by-cells) table equals the
   census of viable k-column prefixes under `stateOf`. Three lemmas:
   - *L-stencil*: a cell in column c+1 is king-adjacent only to columns
     {c, c+1}, rows within 1 — pure arithmetic from `kingAdj`.
   - *L-partition* (the crux): connectivity of S ∪ M restricted through
     the cut is determined by (partition of the boundary column, M); by
     splitting any path at its last visit to columns ≤ c. Folklore TM
     correctness; written nowhere in-project as a proof; does NOT need
     the non-crossing/K₄ theorem (that is a state-counting fact, kept out
     of scope deliberately).
   - *L-strand*: a component absent from the boundary column can never
     gain a cell — soundness and completeness of the death rule.
3. **FrontierComplete.lean** — completion: one class + both flags ⟺
   `KingConnected` + height exactly H, for prefix-closed S; head theorem
   `frontierT_eq_T` via `Tc`/`Tc_eq_T` (count the same canonical set).
4. **FrontierPins.lean** — native_decide battery `frontierT n H = <banked
   literal>` for all n ≤ 9 (matching the spec's validated range) plus the
   guarded axiom audit in the `AuditOutworks.lean` pattern.

Already proved and reusable: the definition layer and `Tc_eq_T`
(committed, sorry-free); the paper-level statements of the three
propositions (harness Part 3). Genuinely new: everything in modules 2–3.

## 5. Cost, in sessions

Notary precedent: wave B = four modules, four Sonnet agents against
pre-verified skeletons, one day, zero statement changes.

- **S1 (Fable):** skeletons + statements + RED-first `gate-frontier` +
  the paper proof of L-partition/L-strand written into the module headers
  (drafting the skeleton forces it; this is where the certified-paper
  fallback is banked for free).
- **S2 (agents, wave 1):** FrontierDef well-formedness + FrontierComplete
  — independent, two agents.
- **S3 (agents, wave 2):** FrontierPrefix. The risk concentrates here:
  path-splitting inductions over `Finset (ℤ × ℤ)` are API-fiddly, and this
  is the one module that could spill into a fourth working session of
  lemma splitting.
- **S4:** pins, audit, gate green, writeup.

**Estimate: 3–5 sessions**, risk concentrated in S3. Fallback if S3
stalls: `frontierT_eq_T` conditional on L-partition as a named hypothesis
(the `MoatBound` pattern from `HolesUpper.lean`) plus the finite pin
battery — a real artifact but NOT the prize; the prize requires no
sorries and no load-bearing hypothesis.

## 6. The certified-checker alternative, priced honestly

There is none for this target. The claim is an equivalence of two
definitions, not an arithmetic identity — an exact-arithmetic checker can
only test instances, and instance agreement is exactly what the standard
discounts ("the same measurement, read again"). The instances are
moreover already tested to death: the 45-cell spec validation (this
session), `Tc` pins, four independent enumerators at n ≤ 12
(`results/triangle-hunt-enumerator-crosscheck.md`), Redelmeier rows
n ≤ 22. The cheap sibling is the **paper proof** of L-partition/L-strand
(~1 session, and S1 produces it as a by-product). A paper proof by this
project answers most referees; it does not answer the objection's
mechanism — a shared blind spot surviving in-house reasoning — which is
the one thing formalisation against an independent definition is *for*.
So: paper proof lands in S1 regardless; the Lean increment (S2–S4) is
what converts it from "our proof of our rule" to a machine-checked
theorem, and that increment is 2–4 agent-sessions.

## 7. NOT ESTABLISHED

- Whether the S3 induction is one wave or three: unmeasured, and no
  comparable Finset-geometry induction exists in the development to
  calibrate against (`GapWalkBij` is the nearest and it stayed on
  sequences, not planar cell sets).
- native_decide compile cost of the pin battery at n = 9 (the Python spec
  needs 41 s interpreted; Lean native is typically faster, but no Lean
  was built this session per constraints — the L5 file's measured small-n
  costs suggest minutes, not hours, at n ≤ 9 with a DP rather than a
  powerset filter).
- Whether the whole-column reference kernel ever validated in-band cells
  (would sharpen §2's residual statement); the harness records it as
  gate-validation oracle only, small n.
