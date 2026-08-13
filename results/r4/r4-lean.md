# r4-lean — the definition-level theorem: what must be proved, in what order

Scout `r4-lean`, round 4, 2026-08-12. Question: what exactly has to be proved,
in what order, for the definition-level theorem (r3's L3-5) to close the
chartered objection for the swept cells, and what is the smallest first
increment a lead can dispatch a build for tonight.

**Standing label: I ran no compute of any kind. No `lake build`, no `lake env
lean`, no Lean invocation on any machine. Every Lean statement and proof in
this deliverable and in the file it references is UNCOMPILED. Nothing here is
a theorem until a lead's build says so.**

---

## 0. Three corrections to the inherited picture, made before anything else

The brief told me to check r3's claims rather than inherit them. Three of them
do not survive the check, and two of the corrections change the plan.

### 0.1 `Tc_eq_T` is not "half of (a)". It is none of (a).

r3 (`triangle-r3-l3-proofscope.md` §1, `triangle-r3-synthesis.md`) says (a) is
"reachable, and half of it already exists in the committed Lean development",
citing `polyplets/Polyplets/Compute.lean:207`, `Tc_eq_T`.

Read in full, `Tc_eq_T` says: the `Finset.filter` of `IsCanonical` over
`(box n H).powersetCard n` equals `(canonical_finite n H).toFinset`, hence has
the same card as the `Set.ncard` defining `T`. Its whole proof is one
`Finset.ext` plus the box containment (`Compute.lean:207-223`, 17 lines). There
is no column, no prefix, no cut, no state, no fold, no induction over a sweep.
It is a change of *container* — `ncard` of a set to `card` of a materialized
enumeration — not a change of *algorithm*. Against the target "the frontier
recurrence counts exactly the king-connected height-`H` `n`-sets", its
contribution is zero.

This matters practically: r3's cost estimate (3–5 sessions) was anchored partly
on "half is done". That anchor is void. My own estimate below is built from the
lemma graph instead.

### 0.2 The calibration anchor r3 said does not exist, exists — in the same tree.

`triangle-r3-l3-proofscope.md` §7 files as NOT ESTABLISHED: "no comparable
Finset-geometry induction exists in the development to calibrate against
(`GapWalkBij` is the nearest and it stayed on sequences, not planar cell
sets)." I checked `GapWalk*` (9,647 lines): r3 is right that it is power series
and sequences — `GapWalkColumns.lean`'s "columns" are `PowerSeries` columns of
a matrix identity, not grid columns.

But `polyplets/Polyplets/Finite.lean:61-76` is exactly the missing anchor:

```
lemma exists_adj_cross_of_reflTransGen {S : Finset (ℤ × ℤ)} {p q : ℤ × ℤ} {k : ℤ}
    (proj : ℤ × ℤ → ℤ)
    (hlip : ∀ a b : ℤ × ℤ, kingAdj a b → |proj a - proj b| ≤ 1)
    (h : Relation.ReflTransGen (fun a b => a ∈ S ∧ b ∈ S ∧ kingAdj a b) p q)
    (hp : proj p ≤ k) (hq : k + 1 ≤ proj q) :
    ∃ a b, a ∈ S ∧ b ∈ S ∧ kingAdj a b ∧ proj a = k ∧ proj b = k + 1
```

That is a path-splitting induction at a column cut, over `Relation.ReflTransGen`
on `Finset (ℤ × ℤ)`, committed and sorry-free, and it is **16 lines including
the statement**, closing with `omega`. Its siblings
`exists_proj_eq_of_cross` (13 lines) and the width bound `canonical_x_le`
(23 lines) are the same shape. This is the single most useful calibration
datum in the deliverable and §3 turns it into a number.

Collateral finding: `canonical_x_le` (`Finite.lean:82`) already proves the
width ≤ n bound in the committed tree. The r3 L5 lane wrote
`experiments/tristruct/r3_l5_normalization.lean` to prove that same bound from
scratch, and that file is the one that failed to compile with 9 errors at 6
sites. The proof it needed was already in the build.

### 0.3 The r3 skeleton's `stateOf` is stated wrong, and the wrong version is
not provable.

`triangle-r3-l3-proofscope.md` §4.2: "`stateOf S c` = (partition of S's
column-c cells by connectivity-**in-S**, flags)". Connectivity in the whole of
`S` is not a function of the prefix `S ∩ {x ≤ c}` — two cells of column `c` can
be joined only through columns `> c`. A DP reading columns left to right cannot
compute it, and the prefix-census theorem as worded is false. The invariant has
to be connectivity **in the prefix**. Everything below uses the prefix version.
This is a drafting slip, not a hole in the idea, but it would have cost a wave
to find at the keyboard.

---

## 1. Deliverable 1 — the proof skeleton for (a), as a dependency graph

### 1.0 Vocabulary (all new, all in the `Defs.lean` idiom)

```
def reach (S : Finset (ℤ × ℤ)) (a b : ℤ × ℤ) : Prop :=
  Relation.ReflTransGen (fun x y => x ∈ S ∧ y ∈ S ∧ kingAdj x y) a b
def colAt (S : Finset (ℤ × ℤ)) (c : ℤ) : Finset (ℤ × ℤ) := S.filter fun p => p.1 = c
def preAt (S : Finset (ℤ × ℤ)) (c : ℤ) : Finset (ℤ × ℤ) := S.filter fun p => p.1 ≤ c
def sufAt (S : Finset (ℤ × ℤ)) (c : ℤ) : Finset (ℤ × ℤ) := S.filter fun p => c < p.1
def Unstranded (P : Finset (ℤ × ℤ)) (c : ℤ) : Prop :=
  ∀ a ∈ P, ∃ a' ∈ colAt P c, reach P a a'
```

`KingConnected S ↔ ∀ p ∈ S, ∀ q ∈ S, reach S p q` is definitional
(`Defs.lean:29`), so `reach` is a notation convenience, not a new object.

The **reduced step relation** — the whole design turns on this:

```
def redStep (P M : Finset (ℤ × ℤ)) (c : ℤ) (x y : ℤ × ℤ) : Prop :=
    (x ∈ colAt P c ∧ y ∈ colAt P c ∧ reach P x y)
  ∨ (x ∈ M ∧ y ∈ M ∧ reach M x y)
  ∨ (kingAdj x y ∧ ((x ∈ colAt P c ∧ y ∈ M) ∨ (x ∈ M ∧ y ∈ colAt P c)))
```

Note the asymmetry, which is correct and not a slip: the past `P` enters only
through its column-`c` cells and the reachability relation *restricted to that
column*, whereas the future `M` enters in full. That asymmetry is precisely the
statement "the frontier state is a sufficient statistic for the past".

### 1.1 The graph

Difficulty scale: **E** trivial/mechanical, **M** an afternoon, **H** the risk.
"Mathlib" names the existing theorem; "author" means we write it.

| # | lemma | statement (informal) | depends on | source | diff |
|---|---|---|---|---|---|
| A1 | `kingAdj_symm` | `kingAdj p q → kingAdj q p` | — | author (`abs_sub_comm`) | E |
| A2 | `reach_symm` | `reach S a b → reach S b a` | A1 | author, or Mathlib `Relation.ReflTransGen.swap` + `reflTransGen_swap` (`Logic/Relation.lean:746,751`) | E |
| A3 | `reach_mono` | `S ⊆ S' → reach S a b → reach S' a b` | — | **Mathlib** `Relation.ReflTransGen.mono` (`Logic/Relation.lean:703`) | E |
| A4 | `reach_of_notMem` | `x ∉ S → reach S x b → b = x` | — | author (`ReflTransGen.cases_head`, `Logic/Relation.lean:477`) | E |
| A5 | `cut_edge_cols` | `a.1 ≤ c → c < b.1 → kingAdj a b → a.1 = c ∧ b.1 = c+1` | — | author (`omega` off `kingAdj`) | E |
| A6 | `pre_union_suf` | `preAt S c ∪ sufAt S c = S`, and they are disjoint | — | author (`Finset.filter_union_filter_neg_eq`) | E |
| **B1** | `fnl` | the funnel map: `x ↦ x` on `colAt P c`, else a chosen column-`c` representative reachable in `P`, else `x` | A4 | author (`dite` + `Exists.choose`), noncomputable | E |
| **B2** | `fnl_eq_self_of_notMem` | `x ∉ P → fnl P c x = x` | A4, B1 | author | E |
| **B3** | `fnl_mem_col` | `x ∈ P → Unstranded P c → fnl P c x ∈ colAt P c ∧ reach P x (fnl P c x)` | B1 | author | E |
| **C1** | `redStep_of_step` | **the crux, single-step form**: every king edge of `P ∪ M` lifts to `ReflTransGen (redStep P M c)` between the funnel images | A1–A6, B2, B3 | author, 4 cases | **M** |
| **C2** | `redReach_of_reach` | `reach (P ∪ M) x y → ReflTransGen (redStep P M c) (fnl x) (fnl y)` | C1 | **Mathlib** `Relation.ReflTransGen.lift'` (`Logic/Relation.lean:737`) — one line | E |
| **C3** | `reach_of_redStep` | each `redStep` is a real `reach (P ∪ M)` | A3, A5 | author | E |
| **C4** | `reach_of_redReach` | `ReflTransGen (redStep) x y → reach (P ∪ M) x y` | C3 | `reflTransGen_closed` (`Logic/Relation.lean:742`) | E |
| **D1** | `reduction` | `Unstranded P c → (KingConnected (P ∪ M) ↔ every pair of `colAt P c ∪ M` is `redStep`-reachable)`, with the empty/degenerate cases split out | C2, C4, B3, A2 | author | **M** |
| **D2** | `strand_dead` | a `reach P`-component of the prefix missing column `c` can never join anything later — soundness *and* completeness of the death rule | A4, A5, A6 | author (edge-closed subset argument) | M |
| **D3** | `sufficiency` | same column-`c` occupancy + same restricted reachability + both `Unstranded` ⟹ `KingConnected (P ∪ M) ↔ KingConnected (P' ∪ M)` | D1 | author — near-immediate from D1 | E |
| **E1** | `State` | finite state type: canonical label vector over `Fin H` + two sticky flags; `Fintype`, `DecidableEq` | — | author | M |
| **E2** | `encode_faithful` | the label vector encodes exactly the restricted reachability relation of D3 — `encode P = encode P' ↔ (occupancy and restricted reach agree)` | E1, D3 | author | **H (see §2)** |
| **E3** | `step` | the transition function: place a column, merge labels, apply the death rule, update flags | E1 | author, transcription of the three propositions | M |
| **E4** | `step_correct` | `encode (P ∪ newcol) = step (encode P) newcol` | E2, D1, D2 | author | **H** |
| **F1** | `frontierT` | `frontierT n H` by fold over columns with a cell budget; termination | E1, E3 | author | M |
| **F2** | `prefix_census` | after `k` columns the DP table equals the census of viable `k`-column prefixes by `(state, cells)` | E4, F1 | author, induction on `k` | M |
| **G1** | `completion` | one class + both flags ⟺ `KingConnected` ∧ height exactly `H`, for the full set | D1, D2 | author | M |
| **G2** | `frontierT_eq_T` | **the head theorem** | F2, G1, `canonical_x_le` (`Finite.lean:82`, existing), `T_eq_toFinset_card` (`Finite.lean:125`, existing) | author | M |
| **H1** | pins | `native_decide` battery `frontierT n H = <banked>` for `n ≤ 9`, plus a `#guard_msgs` axiom audit in the `AuditOutworks.lean` pattern | G2 | author | E |

### 1.2 The load-bearing induction — and why it is smaller than r3 thought

r3 named the crux "partition-sufficiency, Finset path-splitting" and said the
risk was concentrated in an induction "uncalibrated against anything in the
development". The decomposition above says something more specific.

**The path-splitting induction does not need to be written.** The naive proof
of D1's forward direction extracts the vertex list of a king path, cuts it at
each crossing of the column-`c` boundary, and merges consecutive same-side
segments — an induction over a chain with a strengthened invariant, and
`Relation.ReflTransGen` gives no handle on the intermediate vertices, so it
would have to be routed through `List.Chain'` or `SimpleGraph.Walk`
(`Mathlib/Combinatorics/SimpleGraph/Walk/Decomp.lean:35,78` — `takeUntil` /
`dropUntil`) and back. That is the month-shaped object.

It is avoidable. Funnel every prefix cell to a column-`c` representative
(B1–B3), and then the *single-step* lemma C1 suffices, because
`Relation.ReflTransGen.lift'` closes the induction for us:

```
theorem redReach_of_reach … :=
  Relation.ReflTransGen.lift' (fnl P c) redStep_of_step h
```

C1 has four cases and each is short: both endpoints in `P` (funnel both, glue
with `reach_symm` and transitivity — clause 1); both in `M` (funnel is the
identity by B2 — clause 2); one each way (A5 forces the `P`-side cell into
column `c`, so its funnel is itself — clause 3); and the mirror image.

So the risk does not sit where r3 put it. **On this decomposition the crux is
C1 + D1, and D1's hard direction is one `lift'` application.** What is left
genuinely hard is the *encoding* layer, E2/E4 — canonical label vectors,
`Fintype` instances, and the merge/death step as a function on them. That is
bookkeeping rather than mathematics, but bookkeeping is what consumes Lean
sessions, and it is where I would now expect the schedule to slip.

**This paragraph is a claim about UNCOMPILED source and is exactly the kind of
claim r3's L5 lane got wrong.** §2 is the test.

---

## 2. Deliverable 2 — the calibration answer

**The question the brief calls the most valuable thing in this deliverable:
nobody knows whether the load-bearing induction is a day or a month. What is
the cheapest thing that would tell us?**

Three candidates were available and I rank them.

### 2.1 The scaled-down analogue already in the development — free, and it
already answers half the question

`Finite.lean:30-104` is three cut-and-path lemmas over
`Relation.ReflTransGen` on `Finset (ℤ × ℤ)`, committed and sorry-free:
`exists_proj_eq_of_cross` (13 lines), `exists_adj_cross_of_reflTransGen`
(16 lines), `canonical_x_le` (23 lines). They are the *same species* as the
skeleton's layer A/D2: induction over a king path, case split on which side of
a cut the current vertex is, closed by `omega`. Someone in this project has
already written king-path-splitting-at-a-column in Lean, three times, at ~15
lines each. r3's §7 recorded the opposite ("no comparable Finset-geometry
induction exists in the development") because it looked at `GapWalk*`.

That is a real datum and it is free. It bounds the *layer-A* risk hard: the
arithmetic-and-stencil floor of this programme is a known quantity in this
codebase at roughly 50 lines. It does **not** settle the crux, because none of
the three carries a *state* across the cut — they all conclude "some cell
exists there", never "the past is summarized by this".

### 2.2 The Mathlib theorem of the same shape — `Relation.ReflTransGen.lift'`

`Mathlib/Logic/Relation.lean:737`:

```
theorem ReflTransGen.lift' {p : β → β → Prop} {a b : α} (f : α → β)
    (h : ∀ a b, r a b → ReflTransGen p (f a) (f b))
    (hab : ReflTransGen r a b) : ReflTransGen p (f a) (f b)
```

This is not merely "the same shape" — it is, if the construction in §1.2 is
sound, *the* induction, already proved, generic. The month-shaped version of
the crux is the one that walks the vertex list of a king path and merges
consecutive same-side segments; `lift'` exists precisely so that a
homomorphism-like projection never has to do that. The whole question reduces
to whether a projection exists that makes every single king edge lift, and
§1.2 claims the funnel map is one.

### 2.3 The recommendation: a first increment whose success or failure is
diagnostic

**Build `experiments/tristruct/r4_lean_funnel_probe.lean` (written today,
UNCOMPILED, ~130 lines of content). Its whole purpose is to answer the
calibration question and nothing else.**

It contains layers A, B and C of §1.1 and stops: the funnel map, the four-case
single-step lemma `redStep_of_step`, the one-line `lift'` application
`redReach_of_reach`, and the easy converse `reach_of_redReach`. No state type,
no `Fintype`, no fold, no pins, no cell counting.

The reading is unambiguous, which is the property that makes it worth a build
slot:

| outcome | what it means | schedule |
|---|---|---|
| Gate A green | the crux is `lift'` + four short cases. The partition-sufficiency risk r3 could not calibrate is retired, and the programme's residual risk moves to the encoding layer E2/E4 | crux is a day; total revised to §3 |
| `redStep_of_step` fails with `unsolved goals` or `omega could not prove the goal` | the funnel construction has a hole — most likely the both-endpoints-in-`P` case, where the two funnel images must be shown `reach P`-related | back to r3's estimate; route through `SimpleGraph.Walk.takeUntil` (`Walk/Decomp.lean:35`) and price the month |
| failure naming an identifier, an instance, or a `dif_pos` mismatch | neither answer; it is the mechanical class, and the file header lists five such points with their repairs | one more slot |
| Gate B (RED) green — the mutant compiles | worse than a failure: the probe is not testing what it claims. Treat gate A's pass as void | rewrite the probe |

**Why this is cheaper than every alternative I considered.** A paper proof of
the crux (r3's §6 "certified-paper fallback") costs a session and cannot
distinguish outcome 1 from outcome 2 — it is precisely the in-house reasoning
whose blind spots the exercise exists to catch, and r3's L5 lane demonstrated
the failure mode directly: two claims filed as "complete written proofs, no
step missing", nine errors at six sites, two of them genuine holes. Writing
increment 2 first and building both together costs 3-4x the elaboration and
confounds the two signals. Building the whole of r3's four-module skeleton
costs the campaign before the calibration question is answered.

The probe is also the one increment whose *failure* is worth as much as its
success, which is the property a calibration instrument needs.

---

## 3. Deliverable 3 — the sequenced build plan

Each increment ends in something that compiles or fails loudly. Wall figures
are for the elaboration only, on a warm cache; the session cost is the agent
time.

| # | contents (§1.1 rows) | ends in | gate | session estimate |
|---|---|---|---|---|
| **1** | A1-A6, B1-B3, C1-C4 | `r4_lean_funnel_probe.lean` elaborates silently, RED mutant rejected | the script's gates A + B | **tonight, one build** — file is written |
| 2 | D1 `reduction`, D2 `strand_dead`, D3 `sufficiency`, degenerate cases | `sufficiency` as a standalone theorem | same script pattern, plus RED controls 2 and 3 from the probe header | 1 session |
| 3 | E1 `State`, E2 `encode_faithful` | a `Fintype` state type with a faithfulness theorem | `decide` on small columns | 1-2 sessions — **the new risk concentration** |
| 4 | E3 `step`, E4 `step_correct` | the transition function, proved | `decide` agreement with `r3_l3_schema_dp.py` on H ≤ 4 | 1-2 sessions |
| 5 | F1 `frontierT`, F2 `prefix_census`, G1 `completion`, G2 `frontierT_eq_T` | **the head theorem** | `gate-frontier`, RED-first, in the `gate-notary` pattern (`Makefile:393-400`) | 1 session |
| 6 | H1 pins + `#guard_msgs` axiom audit; promote from `experiments/` into `Polyplets/` and add to `Polyplets.lean` | `make` green | bare `make` at repo root | 1 session |

**Revised total: 5-7 sessions**, conditional on increment 1 going green — more
than r3's 3-5, and the difference is not pessimism about the crux but the
removal of r3's void "half is already done" anchor plus the honest pricing of
the encoding layer that r3 folded into "FrontierDef well-formedness".

**Where the source lives, and why.** Increments 1-5 go in
`experiments/tristruct/r4_lean_<purpose>.lean`, **not** in
`polyplets/Polyplets/`. `docs/lean-environment.md` §1 is explicit that every
file under `Polyplets/` is imported by `Polyplets.lean` and built by
`lake build`, and that the one file deliberately kept out of the build,
`Draft/Prop6Skeleton.lean`, is out precisely because it carries `sorry`s. An
uncompiled probe placed in the module tree would break bare `make` for
everyone until it went green — the opposite of failing loudly in one place.
Increment 6 is the promotion step, and it is a separate increment for that
reason. The probe still does `import Polyplets.Finite`, so it is written
against the project's real `kingAdj` / `KingConnected` / `Relation.ReflTransGen`
vocabulary and inherits the warm olean cache; nothing is copy-pasted.

**The fallback, if increment 3 or 4 stalls.** `HolesUpper.lean:376-391` is the
pattern, verified in-tree: `def MoatBound : Prop := …` states the unproved
proposition as a named `Prop`, and `theorem maxhole_upper (hmoat : MoatBound)
…` takes it as a hypothesis, so the conditional theorem is sorry-free and the
one assumption is a single readable line a referee can audit. The analogue here
is `def StateSufficient : Prop := …` (D3's statement) with
`theorem frontierT_eq_T (hs : StateSufficient) …`. Two things to say about it
honestly: it is a real artifact and the axiom audit stays clean, but it is
**not the prize** — a referee reading `StateSufficient` is reading exactly the
proposition the chartered objection doubts. And if increment 1 goes green the
fallback is much more likely to be needed at the *encoding* layer, where the
named hypothesis would be "the label vector faithfully encodes the partition"
— a far less alarming thing to assume than sufficiency itself.

---

## 4. Deliverable 4 — the job request

### 4.1 The box question, answered by measurement, not assumption

Checked by read-only ssh on 2026-08-12 (MEASURED):

| box | arch | elan | `lake`/`lean` | repo | project Lean build |
|---|---|---|---|---|---|
| gympie | arm64 macOS | `~/.elan/toolchains/{v4.31.0, v4.32.2}` | yes | working tree | **warm**: 7.0 GB mathlib `.olean` + 2.5 GB project |
| ayr | x86_64 Linux | **absent** (`~/.elan` does not exist) | absent | `~/src/polyominoes` on branch `second-source` | none |
| dalby | **aarch64** Linux | **absent** | absent | `~/src/polyominoes` on `master`, `.lake/packages` *sources* present | none (`.lake/build` does not exist on either the project or mathlib) |

**Lean is gympie-only today.** That is a finding, not a preference, and §6
files it as a queue row: ayr is x86_64, the platform mathlib publishes prebuilt
`.olean` releases for, so `lake exe cache get` should work there and take the
whole campaign off the laptop for a one-time ~5-6 GB download. dalby is
aarch64 Linux, for which the existence of a prebuilt mathlib cache is
**NOT ESTABLISHED** — I did not check upstream, and if there is none, dalby
means building mathlib from source.

### 4.2 The request

```
job id:            R4-LEAN-JOB-1
measures:          the calibration verdict of §2.3 — does the frontier state's
                   sufficiency-for-the-past reduce to Relation.ReflTransGen.lift'
                   plus a four-case single-step lemma, or not
decides:           whether the L3-5 crux is a day or a month, and therefore
                   whether increments 2-6 are dispatched at all this round;
                   also which of §3's two fallback layers is the live one
command:           sh experiments/tristruct/r4_lean_funnel_probe.sh \
                     /Users/jasonp/src/polyominoes
                   (equivalently, by hand:
                    cd /Users/jasonp/src/polyominoes/polyplets && \
                    ~/.elan/bin/lake env lean \
                      ../experiments/tristruct/r4_lean_funnel_probe.lean)
script:            experiments/tristruct/r4_lean_funnel_probe.sh — fail-closed:
                   gate A requires exit 0 AND zero bytes of elaborator output
                   (warnings are failures); gate B mutates one token in
                   cut_edge_cols and requires the mutant to be REJECTED; an
                   empty log is a failure. Writes
                   experiments/tristruct/r4_lean_funnel_probe.log; the mutant
                   copy is created and removed inside the repo, no /tmp.
box:               gympie ONLY — measured above. Not a preference.
cores:             1 (single-file elaboration; the script runs its two gates
                   sequentially, never concurrently)
wall estimate:     6-16 min total for both gates, EXTRAPOLATED. Basis: gate A
                   and gate B are one `lake env lean` each against the warm
                   cache, import-dominated; `lake build --no-build` verify is
                   ~6 s (docs/lean-artifact.md) and r3's L5 addendum ASSERTED
                   5-15 min for a single-file elaboration of a ~700-line file.
                   Mine is ~230 lines including comments, with eight short
                   tactic proofs and no `decide`/`native_decide` anywhere.
                   NO MEASURED ANCHOR EXISTS: r3's one authorized Lean job left
                   experiments/tristruct/r3_l5_job1.log, which records the nine
                   errors and `exit=1` but no wall clock and no RSS. Gate A's
                   own `/usr/bin/time -l` block is the first real anchor and
                   lands in the log.
RAM estimate:      5.5-7 GB peak RSS, EXTRAPOLATED. Basis: the round-4 brief
                   states r3's Lean runs on gympie measured ~5.4 GB RSS each;
                   this file's transitive import is the same (`Polyplets.Finite`
                   -> `Polyplets.Defs` -> `import Mathlib`). ASSERTED: eight
                   short tactic proofs add well under 0.5 GB.
disk estimate:     log ~KB; the mutant copy ~9 KB, removed by the script. No
                   download — gympie's 7.0 GB mathlib cache is already built.
                   Nothing under /tmp.
interruptible:     yes — stateless and rerunnable; a kill loses only the log
GYMPIE LIMIT:      **exceeds the standing limit and needs jasonp's per-job
                   approval.** The limit is 1 GB/core and 2 cores, i.e. 2 GB;
                   this is ~3x that on RAM. Wall and cores are inside the
                   limits (<=16 min against 10 min is the second breach, and
                   only if both gates run; gate A alone should fit). There is
                   no way to bring a Mathlib-importing elaboration under 2 GB,
                   so the choice is approval or no Lean on gympie at all.
if approval is
refused:           two options, in order. (i) Run gate A only (~3-8 min,
                   same RSS) and defer the RED control — this still answers the
                   calibration question, at the cost of an unexercised RED,
                   which the skeptical-reader standard discounts. (ii) Stand up
                   elan + `lake exe cache get` on ayr first (queue row
                   R4-LEAN-1) and run there with no limit at all; this delays
                   the answer by one setup job but is the better trade if more
                   than one increment is coming, which it is.
RED control:       gate B, in-script: `have h := hadj.2.1` -> `have h :=
                   hadj.2.2` in cut_edge_cols draws the column conclusion from
                   the row bound; `omega` must then fail. A mutant that
                   compiles voids gate A. Two further RED controls (over-merging
                   in redStep, and weakening Unstranded) are documented in the
                   probe's header for increment 2's job, not this one.
closes:            the NOT ESTABLISHED item of triangle-r3-l3-proofscope.md §7,
                   "whether the S3 induction is one wave or three: unmeasured"
```

---

## 5. Deliverable 5 — what (a)+(b) does and does not buy, referee-facing

> Both production engines decide king-connectivity the same way: union-find
> over a frontier, against the previous column's component labels. The
> objection on the record is that a shared misconception about *what is being
> counted* would pass through both engines unaltered and surface as agreement.
> Recounting answers that objection one band cell at a time, by a different
> rule, at a cost that rises with height. The definition-level theorem answers
> it differently, and for everything at once: it makes the rule a theorem.
>
> The statement to be proved is that the frontier recurrence — the abstract
> rule, not any binary — counts exactly the king-connected `n`-cell sets whose
> bounding box has height exactly `H`, where king-connectedness is Mathlib's
> reflexive-transitive closure of king adjacency: a definition with no cut, no
> frontier, no component labels and no completion predicate, that the engines
> never implement and could not have shaped. Once that theorem holds, the
> objection is closed for **every cell the sweep touched — H = 3..21, 95.85% of
> a(40) — with no enumeration performed at all.** No other instrument in this
> project reaches the whole band rather than a residue of it.
>
> The theorem also changes the standing of evidence already in hand. The
> strip-transfer-matrix's 469 cells, the two production kernels, and `symtm`
> agree; today that agreement is discounted wholesale, precisely because they
> agree *as implementations of a rule that was itself unproved*. With the rule
> proved, the same agreements become what they always looked like:
> cross-checks between independently written codebases, whose bug modes are
> disjoint, of a rule that is now a theorem. Nothing is recomputed and the
> H ≤ 14 story strengthens.
>
> What survives, stated plainly. The theorem is about the rule, not about the
> binaries: a fault in one compiled kernel, on cells only that kernel swept,
> is untouched by it. Program verification of the optimized C++ — the carry
> byte, the packed signatures, the mask pre-pruning, the Go orchestrator — is
> not proposed, at any price. And the band itself, H = 15..21, remains a single
> kink-kernel computation that no theorem re-runs. The proof closes the rule
> half of the objection; an independent recount closes the implementation half
> on the band. Each leaves exactly what the other reaches, and the honest
> position is that both are wanted.

---

## 6. Deliverable 6 — successor queue rows

Four filed in `results/r4/queue.md`, three different in kind (infrastructure,
proof increment, cross-lane audit) plus the fallback. Summarized: **R4-LEAN-1**
stand up elan + mathlib cache on ayr and take the campaign off gympie;
**R4-LEAN-2** increment 2, `reduction`/`sufficiency`, gated on JOB-1 green;
**R4-LEAN-3** audit every r3 skeleton for the prefix-vs-global invariant slip
found in §0.3, and for duplicated work already committed in-tree (§0.2's
`canonical_x_le`); **R4-LEAN-4** the `MoatBound`-pattern conditional theorem,
filed now so the decision to take it is deliberate rather than a retreat.

---

## 7. NOT ESTABLISHED

- **Everything Lean in this deliverable and in
  `experiments/tristruct/r4_lean_funnel_probe.lean` is UNCOMPILED.** I ran no
  Lean on any machine. The claim that the crux reduces to `lift'` plus four
  cases is an argument about source that has never been elaborated, and it is
  the same class of claim r3's L5 lane got wrong at nine errors and six sites.
  R4-LEAN-JOB-1 exists to settle it.
- Wall and peak RSS for any Lean elaboration in this repo: no measured anchor
  exists. `experiments/tristruct/r3_l5_job1.log` records errors and `exit=1`
  and no timing. Every number in §4.2 is EXTRAPOLATED or ASSERTED as labelled.
- Whether a prebuilt mathlib `.olean` cache exists for aarch64 Linux (dalby).
  Not checked upstream. If not, dalby means a from-source mathlib build.
- Whether `lake exe cache get` succeeds on ayr. Inferred from ayr being
  x86_64 Linux and reaching the network; not run.
- The session estimates in §3 for increments 3-6. They are my judgement against
  the lemma graph, with no comparable encoding-layer work in this development
  to anchor them — the same gap r3 had, now moved from the crux to the encoding
  layer rather than removed.
- Whether the `Unstranded` viability condition as written is the exact
  condition the production engines' death rule implements. §1.1 D2
  (`strand_dead`) is the theorem that would settle it, and it is increment 2.
  The wording match to the harness's Part-3 proposition is an inspection claim,
  not checked here.
- The `#guard_msgs` axiom footprint pinned at the foot of the probe
  (`[propext, Classical.choice, Quot.sound]`) is predicted from `fnl`'s use of
  choice, not observed.
