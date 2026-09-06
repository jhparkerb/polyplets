# The Lean development: what it proves, what it does not, and how to check it

One record for the formalization in `polyplets/`, merged 2026-09-06 from four
files written between 2026-07-21 and 2026-08-22: the citable-artifact
description, the adversarial audit, the authorized staircase-growth job, and
the scope split for the below-onset frame. The toolchain and the build recipes
are separate, in `docs/lean-environment.md`; the per-theorem ledger is
`polyplets/PROOF-STATUS.md`, which is the status of record and the file to
believe if this one drifts from it.

As of 2026-09-06 the development is **86 sorry-free modules**, about 35,700
lines, plus one deliberately unproved skeleton (`polyplets/Draft/Prop6Skeleton.lean`)
that `lake build` never compiles.

## 1. The development as a citable artifact

Written 2026-08-06. Papers 2 and 3 carry tier-2 results whose warrant *is* this
development, so it has to be citable, checkable by someone who did not write
it, and honest about where computation enters.

### What it is

`polyplets/` — 86 modules and about 35,700 lines as of 2026-09-06, Lean 4
v4.31.0 against mathlib v4.31.0, **zero occurrences of `sorry`**. The receipt
of 2026-08-06 (`polyplets/build-receipt-2026-08-06.log`) recorded 65 modules,
21,659 lines and 8624 build targets current; the tree has grown since and the
receipt is the reproducible snapshot, not the current count.

One file is deliberately outside that: `polyplets/Draft/Prop6Skeleton.lean`,
which carries five `sorry`s. It is not a library, `lake build` never compiles
it, and nothing in `Polyplets/` imports it. It states the architecture of the
rest of Proposition 6 — every statement typechecks, and each `sorry` is a named
contract whose paper proof and numeric gate are cited beside it in the file's
header. Its `#print axioms` prints `sorryAx`, which is the point: the file
says what it has not proved. A reader auditing the artifact should read that
header first, then `PROOF-STATUS.md`'s staircase section for what *is* proved.

### How a reader checks it

```
cd polyplets
lake build              # from cold: mathlib dominates; the development itself is minutes
lake build --no-build   # verifies everything is built and current, ~6 s
```

Part of the axiom discipline is enforced by the build rather than by a separate
audit run, and the paper should describe it precisely, because the two halves
are not equally strong:

- **88 guarded.** `Grand/Audit.lean` (18) and `AuditOutworks.lean` (70, of
  which the last eight are sortie B1's three and the five staircase-growth
  ones) wrap `#print axioms` in `#guard_msgs`, so a changed footprint is a
  **build error**. A reader who builds the project has checked these without
  being asked to trust a log.
- **148 unguarded.** The modules themselves print footprints on every build,
  but nothing enforces them. They are informational.

### The footprint, stated plainly

- Of the 88 guarded: 55 standard axioms only, 33 with named `native_decide`
  leaves.
- Of the 148 unguarded: 100 standard only, 48 with named leaves.
- A named leaf is one axiom per finite computation, e.g.
  `a_6._native.native_decide.ax_1_1` for a(6) = 3832.
- No `sorryAx`. No anonymous `Lean.ofReduceBool`.

Naming matters here: a named leaf says exactly which computation is being
trusted, so the compiled-evaluation surface is enumerable rather than diffuse.
The papers should say so in that form.

### What each paper cites it for

**Paper 2 — the universal diagonal law.** The engine
(`Universal.universal_shape_d`, `universal_shape`,
`universal_shape_production`, `universal_production_int_all`) and the
`kingSystem` / `peelSystem` instances are **standard-axioms-only**. The
per-lattice instance pins (`king_P1_*`, `square_P1_*`, `hex_P1_*`) and the
cross-family row-sum gates carry named leaves that are two triangle cells per
lattice. `grand_form` and `grand_form_prod` are standard-axioms-only; the
k ≤ 18 production pinning (`P18_grand_of_banked`, `P18_grand_prod`) carries
the chunked weight cards as leaves.

**Paper 3 — Proposition 6's Lemma 3, and `µ`.** `Stair.join_valid`,
`Stair.cut_join` and `Stair.join_injOn` (`Polyplets/StairAnimals.lean`, sortie
B1) formalize the column-join and its inverse: the join stays in the class, and
the cut at cumulative area `i` inverts it, so the map is injective once both
areas are fixed. Guarded, and their footprint is `[propext, Quot.sound]` — not
even `Classical.choice`. Since 2026-08-06 the counting layer and the Fekete
step are there too (`StairGrowth.lean`), so **Lemma 3 itself is a Lean
theorem**: `Stair.M_supermul : M i * M j ≤ M (i + j)` for all `i` and `j`,
standard three axioms, guarded. With it, `Stair.M_tendsto` (`µ` exists) and
`Stair.M_le_mu_pow` (`M n ≤ µⁿ` for every `n`, so banked terms are floors, not
approximations), and the conditional `Stair.mu_gt_of_banked` giving
`3.1234 < µ ≤ 4` from the banked `M 700`.

What Paper 3 must *not* claim from this: Proposition 6. Lemmas 1 and 2, the
geometric HV-convex layer and the squeeze are **not** formalized, so Lean
states the growth constant of the *staircase* class, not the sandwich. Cite
the paper proof for Proposition 6 and this development for Lemma 3.

**Paper 3 — the λ bracket, upper end.** `BuiSystem.certSum_le`,
`lambda_le_of_buiSystem` and `RatCert.lambda_le` are standard-axioms-only; the
concrete certificate `lambda_le_of_bui_rd3` depends on `buiRD3_valid`, a named
leaf that is the certificate's arithmetic validity check. `lambda_lb` /
`lambda_gt` depend on the evaluation of a(6). Fekete's ladder for λ —
`a_supermul`, `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le` — is
standard-axioms-only, and since 2026-08-06 it is literally shared with the
staircase constant: `Fekete.lean` carries the ladder once and `lambda` and `mu`
are two instances of it.

**Paper 1 — the hole section, if it ships.** `maxhole_lower` and
`maxhole_upper` are standard-axioms-only, and `maxhole` is **conditional on the
hypothesis `MoatBound`**. That conditionality is a formalization gap, not a
mathematical one: (II') is proved on paper by the moat-cycle winding argument
(`results/subclasses.md`), and mathlib has no discrete-Jordan material to
carry it. The *multi-hole* reduction the Lean file does not attempt is no
longer open either (`results/subclasses.md` §The union argument, 2026-08-06)
— but formalizing it would mean assuming the grid isoperimetric inequality for
arbitrary finite subsets, a bigger hypothesis than `MoatBound`, so the file
stays as it is.

### What it does not certify

Nothing about the engine, the banked triangle, or the anchor values. Those
enter as explicit hypotheses or as named native leaves; `PROOF-STATUS.md` is
the per-theorem ledger. A paper that cites the development for a(40) itself
would be citing the wrong artifact — a(40)'s warrant is
`docs/publication.md`, not this.

### Packaging

For an archived release, the citable unit is `polyplets/` at a tagged
revision, plus the build receipt, plus `PROOF-STATUS.md`. Nothing else in the
repo is needed to build or check it. The receipt names host, date, revision,
toolchain, mathlib revision, job count, source size, sorry count and the
axiom-footprint summary, which is what a reviewer needs to reproduce the check
rather than repeat the reasoning.

## 2. What the formalization does not reach: the below-onset frame

Written 2026-08-22 from the module inventory. The instruction was to split the
scope honestly before anything was attempted, decide whether the frame is worth
the Lean hours, and if not, say in `PROOF-STATUS.md` that the newest result is
the one the formalization does not reach. **Nothing here was started**, and the
note it asks for is now the second section of `polyplets/PROOF-STATUS.md`.

### The gap, stated precisely

`Grand/PinGrand.lean` certifies the production polynomials `P_1..P_16` for all
`n ≥ 2k+1` from exactly **two real-swept cells per level**:

    A_k = T(2k+1, k+1)      B_k = T(2k+2, k+2)

Both sit **at or above** the onset. That is the whole of what Lean currently
knows about how a level gets pinned.

Undertow replaces one of those anchors with a cell **below** the onset,
corrected by the defect `D_j(k)`. a(41) rests on that substitution, and Lean has
no statement of it. So the missing theorem is not deep in the machinery — it is
one substitution lemma away from work already finished, and that is what makes
it worth pricing rather than dismissing.

### What Lean already has, and what it does not

| piece | module | status |
|---|---|---|
| the diagonal law's *shape* | `Shape.lean` | theorem |
| the grand form | `Grand/*` | theorem, standard axioms |
| pinning from two **onset** cells | `Grand/PinGrand.lean` | `P_1..P_16`, 26 anchors for levels 4..16 |
| the depth-`j` assembly arithmetic | `DepthAssembly.lean` | the `(C)`/`(D)` identities, as exact rational arithmetic |
| **the below-onset identity itself** | — | **absent** |
| **that a corrected below-onset cell may substitute for an anchor** | — | **absent** |

`DepthAssembly.lean` is the piece most likely to be mistaken for coverage it does
not give. It formalizes `D_j(k) = [z^(k+1−j)] D(z)` as a finite exact-rational
assembly of the excess-graded cluster weight families, which is real and is
sorry-free. But its `sigTable`, `bbTable` and `ppTable` are `def`s carrying
hardcoded data, and its theorems take `(sig bb pp : BivZ)` as **hypotheses** —
they say "if the tables are these, then `D_1(k)` is that". The tables come from
the family DP. **They are certificates, not theorems**, and the module is
honest about being parameterized on them.

### The split

**Formalizable — the frame.** Given `D_j(k)` as an opaque rational, two things:

- **(F1)** the below-onset identity: for `n = 2k+1−j`,
  `T(n, n−k) = (P_k(n) + D_j(k))·3^(n−1−3k)` — that the corrected value lies on
  the same polynomial;
- **(F2)** the substitution: two such equations, or one of them together with one
  real onset cell, pin the level — i.e. `PinGrand`'s anchor pair may have a
  member replaced by a corrected below-onset cell.

F2 is nearly bookkeeping once F1 exists: `PinGrand` already does the linear
algebra, and F2 says the new equation is of the same form. **F1 is the work**,
and it is grand-form-shaped — it is a statement about the same staircase
identity, extended one step past its stated range, with a named error term.

**Not formalizable now — the values.** That `D_j(k)` *is* what the family DP
says it is. That needs the DP's correctness against the combinatorial
definition, which is a different and much larger project, and it is the same
class of input as the cluster weight tables `PinGrand` already depends on.

Stating it that way is what makes the split honest: **Lean would not be
certifying a(41), it would be certifying that a(41)'s argument is valid given
the same kind of certificate the existing proof already takes on trust.** That
is a real gain — it removes a step of hand-reasoning from the newest result — and
it is a smaller gain than "a(41) is proved", which nobody should be able to read
into it.

### The honest cost

I am not going to quote hours. What can be said from the tree:

- `Grand/PinGrand.lean` is **machine-generated** by `scripts/gen_grand_pin.py`.
  If F1 lands, F2's per-level instances are generated the same way, so the
  per-level cost is a generator change and not 16 hand proofs.
- F1 has no precedent in the tree to copy. `Shape.lean` and the `Grand/` chain
  are the nearest work, and the below-onset extension is not a special case of
  either — it is one step outside the range the staircase is proved on.
- There is no gate. `polyplets/PROOF-STATUS.md` says it plainly: no `make` gate
  runs Lean, the Linux boxes have no toolchain, and the only thing between the
  tree and a red one is somebody typing `lake build` on gympie. Any Lean work
  inherits that, and the 2026-08-19 duplicate-declaration incident — 8643 green
  module targets and a red root, unnoticed for a whole campaign — is what that
  risk looks like in practice.

### The recommendation, and it is a recommendation and not a decision

**Do not start F1 now.** Two reasons, in order:

1. It is not on the landing path. `docs/pre-landing.md` does not need it, and B1 —
   the gate sweep, done — was the item about the repository being trustworthy.
   F1 makes the repository *more proved*, which is a different axis and a slower
   one.
2. The cheaper half of its value is available immediately by writing the gap
   down, which is what B5's fallback asks for and what the next section does.

If it is started, start with F1 alone and stop there until it is green: F2
without F1 is worth nothing, and F1 without F2 is still a publishable statement
about the diagonal law past its onset.

### What goes in `PROOF-STATUS.md` if F1 is not started

A short section saying, in the file's own register, that **the formalization
covers the route a(40) took and not the route a(41) took** — that `PinGrand`
pins from two onset cells, that Undertow's below-onset substitution is not
stated in Lean, and that `DepthAssembly` formalizes the arithmetic of `D_j`
while taking its weight tables as inputs. A reader who sees "86 sorry-free
modules" and "the grand form against standard axioms" should not have to
reconstruct which of the project's results that covers.

That note is one paragraph, it costs nothing, and it is the part of B5 that
should happen whatever is decided about the Lean hours.

## 3. The staircase growth constant: the one authorized slice of Proposition 6

Written 2026-08-06 as a brief, after a skeptical pass over four routes to
Proposition 6 in Lean, and **executed**: `Polyplets/StairGrowth.lean` carries
`Stair.M_supermul`, `Stair.M_tendsto`, `Stair.M_le_mu_pow` and the conditional
`Stair.mu_gt_of_banked`, and `Fekete.lean` carries the ladder once with
`lambda` and `mu` as two instances of it. The brief is kept because it says why
only this slice was done and what the measured pitfalls were.

### Goal

Two theorems in Lean, sorry-free:

1. `M i * M j ≤ M (i + j)` — `results/subclasses.md` Lemma 3, where `M n`
   counts staircase king animals of area `n` up to translation.
2. `µ = lim M(n)^(1/n)` exists, with the limit-is-supremum half, so
   `M n ≤ µ ^ n` for every `n`.

Plus the conditional numeric floor in the style of `Growth.lean:779`'s
`lambda_gt_of_banked`: given `M 700` as a hypothesis, `µ ≥ 3.1234045…`.

### Why only this slice

Proposition 6's paper proof is three elementary steps a referee can check
unaided, and `make gate-middle-kingdom` already backs both lemmas
computationally with RED controls that make the check non-vacuous (zero
supermultiplicativity violations over all `i+j ≤ 700`; the `d=0` join provably
leaves the class; the area-`(i+1)` cut provably fails to invert; `P(n)` provably
is *not* supermultiplicative). Formalizing the rest competes against that and
loses on cost — the full statement is 2000–3000 lines for a result that is not
central to the project.

What this slice buys that neither the paper proof nor the gate does: the gate
checks supermultiplicativity on 700 terms; Lean makes it a theorem for all `n`.
That is the one place the existing evidence is genuinely finite.

### What already exists

- `polyplets/Polyplets/StairAnimals.lean` (190 lines, sorry-free, footprint
  `[propext, Quot.sound]`) — the `List Col` encoding, `Valid`, `join`, `cut`, and
  `join_valid` / `area_join` / `cut_join` / `join_injOn`. **The combinatorial core
  is done.** What is missing is the counting layer on top of it.
- `polyplets/Polyplets/Growth.lean:648–730` — the Fekete chain for `λ`. 83 lines
  that use exactly three facts about `a`: supermultiplicativity, `1 ≤ a k`, and an
  exponential ceiling.
- `polyplets/Draft/Prop6Skeleton.lean` — typechecking skeleton with the target
  statements and the `Fekete` structure. Start here; it compiles in ~3s via
  `lake env lean Draft/Prop6Skeleton.lean`.

### Deliverables

1. **`M n` and its finiteness.** `Nat.card` over `{l : List Stair.Col // Stair.Valid l ∧ Stair.area l = n}`.
   Finiteness comes from mathlib's `Set.finite_length_lt` plus a bounding
   injection (heights, offsets and length are all `≤ n`) — do **not** copy
   `Sequence.lean`'s `canonicalAnimal_finite`, which is a geometric argument
   about `Finset (ℤ × ℤ)` and a different, longer proof.
2. **Lemma 3.** Turn `join_injOn` into `M i * M j ≤ M (i + j)` by the card-of-
   product injection. `Growth.lean:608 a_supermul` is the same 26-line move one
   encoding over; follow it.
3. **The ceiling `M n ≤ 4 ^ n`.** Heights form a composition of `n` (`2^(n-1)`)
   and the offsets contribute `Π (h_j + 1) ≤ 2^n` because `Σ h_j = n` and
   `h + 1 ≤ 2^h`. This is a real induction, ~100–150 lines. Do not try to inherit
   `a_le_ratio_pow` via `M n ≤ a n`; that needs the geometric bridge this brief
   exists to avoid.
4. **Generalize Fekete — do not transcribe it.** Extract `Growth.lean:648–730`
   into a `Fekete` structure (`f`, `c`, `one_le_c`, `supermul`, `one_le`,
   `ceiling`) carrying `negLog`, `subadditive`, `bddBelow`, `growth`, `tendsto`,
   `le_growth_pow`. Then `lambda := polypletFekete.growth` and
   `mu := stairFekete.growth`. `Growth.lean` gets shorter; `mu` costs ~10 lines.

Budget: **~300 lines**, of which the ceiling is the largest single piece.

### Pitfalls, all measured

- **The numeric floor is conditional.** Fekete gives `M n ≤ µ^n` abstractly; the
  value `M 700` can only enter as a hypothesis or a named native leaf. State it
  as `mu_ge_of_banked`, mirroring `lambda_gt_of_banked`. Do not claim an
  unconditional `µ ≥ 3.1234…`.
- **`lambda`'s public names must survive the refactor.** `lambda`,
  `lambda_tendsto`, `a_le_lambda_pow`, `lambda_le`, `lambda_gt` are cited by
  `PROOF-STATUS.md`, `docs/lean-record.md` and the papers. Keep them as thin
  wrappers over the instance. `AuditOutworks.lean:120–126` pins
  `#print axioms lambda_tendsto` and `a_le_lambda_pow` to
  `[propext, Classical.choice, Quot.sound]` as `/-- info: -/` guards, so a
  footprint regression fails the build rather than passing quietly — that is the
  safety net, use it.
- **Naming.** Phase labels like `(1,1)` mean nothing outside
  `results/subclasses.md`'s table. If any appear, name the bits
  (`bottomRising`, `topFalling`).

### Acceptance

- `lake build` green, no `sorry` in the new material.
- `#print axioms` on both new theorems: standard axioms only, no native leaves
  (the conditional floor may carry the banked hypothesis, not a leaf).
- `AuditOutworks.lean`'s pinned footprints unchanged.
- Full `make` green (16 gates).
- `PROOF-STATUS.md` updated with the two new theorems and their tier.

### Explicitly out of scope

Lemma 2 (the stack bound and its transpose), Lemma 1 (the phase split), the
geometric layer `IsHVCanonical`, Corollary 4, and the squeeze `A_tendsto`. Those
are 1700–2700 further lines and are **not** authorized by this brief. If the
answer to "should we do those too" is ever revisited, the flip conditions are:
Paper 3 leads with Proposition 6 rather than the λ bracket, or jasonp would
rather not personally vouch for the lemmas in print.

## 4. Hostile Witness: the adversarial audit of 2026-07-21

Brief: attack the Lean proofs as a hostile referee and shake out what a careful
OEIS editor reading the paper could reasonably object to. Seven attack lines,
each with a pre-registered kill condition. Kernel outputs (`#print axioms`) were
re-run live, all 26 PinGrand anchor values re-checked against
`results/triangle.txt`, and the definitional bridge brute-forced independently.
Every item on its fix list was applied, the last on 2026-07-22.

### Verdict

**The formalization survives the attack.** No sorry, no custom axioms, no circularity:
`T` is defined directly as a set cardinality (`Polyplets/Defs.lean:49`), the peeling
recursion is proved as bijections *against* that `T`, and the kernel confirms
`grand_form`, `T_staircase`, and the full shape chain (`shape_d`, `shape`,
`shape_production`, `production_int_*`) depend on `[propext, Classical.choice,
Quot.sound]` only — no `native_decide` anywhere in those cones. The seed really is
Sanity.lean's hand proof (`ExpForm.lean:7` imports Sanity; `base_match` uses
`T_one_one`).

What the Lean work does NOT do — and what an editor can push on — is certify the
engine data. For k ≥ 4 the explicit production polynomials are conditional theorems
(`P<k>_grand_of_banked`), and for **levels 12–16 the hypothesis cells are
single-algorithm** (kink TM only). The honest one-line grading: *the Lean proofs
convert "P_k was fitted" into "P_k is forced by a machine-checked shape theorem given
26 engine integers, 17 of which are two-algorithm-confirmed and 9 of which are
single-algorithm."* That is a real credibility upgrade, but it is bounded by the
engine at the top levels.

### Attack results

#### A1 — claim language vs literal Lean statements: mostly survived, 2 wounds

The internal ledger (PROOF-STATUS.md) is honest: hypotheses are consistently
disclosed ("with hypotheses", "modulo TWO real-swept banked cells per level"), no
document claims "kernel-checked" for `native_decide`-rooted results, and every
recorded axiom expectation matched the live kernel output word for word.

Wounds:
1. **T-n-nm1.md (uncommitted) "Production P_1..P_16 are certified for all n ≥ 2k+1
   from two real-swept onset cells per level"** — for k ≥ 4 the cells are *assumed*,
   not certified-in-Lean; the summary bullet drops the "conditional" qualifier that
   PROOF-STATUS keeps. Say "certified conditional on" or "pinned from".
2. **grand-form.md contradicts itself**: the Formalization section declares the Lean
   item CLOSED and the PREDICTED tier retired, while Corollary 3 and "What remains
   open" still call the PREDICTED points "the remaining gap … planned". Stale
   paragraphs; a referee reading top-to-bottom sees the doc disagree with itself.

Nuance (label, not defect): the "UNCONDITIONAL k = 0, 1, 2" tier is unconditional in
the no-hypotheses sense but not native-free — kernel shows `P1_closed` carries
T(3,2)/T(4,3) `native_decide` leaves, `P2_closed`/`T_n_nm2` carry ~12 (weights + seed
values). Only the Grand chain (`grand_form`, shape) is truly clean.

#### A2 — anchor provenance: the real finding

All 26 anchor integers in PinGrand.lean match `results/triangle.txt` exactly, and the
circularity guard is real (`scripts/gen_grand_pin.py:40,136` hard-caps anchors at
H ≤ 18; every H ≥ 20 triangle cell is P_k-generated and none is hypothesized).

Classification of the 26 cells:
- **Levels 4–12A (17 cells): MULTI-SOURCE.** The independent strip engine
  (enumeration-disjoint) confirms every cell with H ≤ 13; row totals are
  two-algorithm (g2 Redelmeier) through n = 22 and OEIS-external through n = 18.
- **Levels 12B–16 (9 cells): SINGLE-ALGORITHM.** `T(26,14), T(27,14), T(28,15),
  T(29,15), T(30,16), T(31,16), T(32,17), T(33,17), T(34,18)` are kink-TM only.
  Cross-ISA byte-identical re-runs (a34 verify covers all 26 anchors) and
  cross-revision re-runs rule out machine/build/transient corruption but cannot catch
  a logic bug shared by every run of the same kernel. This matches the grading the
  project already applies to a(23)+ ("single-algorithm, multiply cross-checked") —
  the P_k for k ≥ 12 inherit exactly that status, not two-algorithm independence.

**Superseded 2026-07-30 (AUDIT-2026-07-30 L7/S5).** The classification above
is the 2026-07-21 state (26 anchors, k ≤ 16). Two things moved: the completed
C_14 strip run (dalby 2026-07-22, `results/strip_C14_run.log`) confirmed
columns H ≤ 14 to n = 36, and the Grand tier extended to k ≤ 18 at the a(40)
close (`c54ce70`), taking the anchor set to **30**. The current split is
**19 strip-second-sourced / 11 kink-only**. The 11 are beyond strip reach
even at N = 40 (H ≥ 15):

    T(28,15) T(29,15) T(30,16) T(31,16) T(32,17) T(33,17)
    T(34,18) T(35,18) T(36,19) T(37,19) T(38,20)

`T(26,14)` and `T(27,14)`, single-algorithm above, are now strip-confirmed.
The reasoning about what cross-ISA and cross-revision re-runs can and cannot
catch is unchanged and still applies to the 11.

Two documentation errors found:
1. **Strip-engine coverage is H ≤ 13, not H ≤ 14** (`results/second-sources.md:44-47`:
   C_14 was never completed; the H=14 log only computed the growth constant, no
   per-cell diff). The "0 mismatch H ≤ 14" note in project memory overstated by one
   column. Corrected.
2. **`oeis/SUBMISSION.md:97-100` cites T(36,20) as a P16 holdout — it is circular**
   (T(36,20) was itself P16-generated per `ns_a36/PROVENANCE.md:9-11`). Only
   T(35,19) is a genuine holdout, and it is same-algorithm.

Cheapest provenance upgrade: complete strip C_14 — flips T(26,14) and T(27,14) to
multi-source in one run.

#### A3 — build integrity and audit enforcement: survived, 2 process dings

The heavy certificate set (15 `CFGVchunk` `native_decide`s + `Vt_3_3` + `d_3_4`) was
green in one coherent 8579-job build finishing 02:46 on 2026-07-21
(`polyplets/weights3heavy.log`), and the import chain (root → Grand.Audit → PinGrand
→ Weights3Heavy → chunks) puts every certificate in the build graph. Live re-run of
`Grand/Audit.lean` reproduced the recorded axiom sets exactly, including the full
~40-leaf list for `P16_grand_of_banked`.

Dings:
1. `#print axioms` is advisory — nothing fails the build if an axiom set drifts.
   A `#guard_msgs` wrapper (or a CI grep on the audit output) would make the
   "standard axioms only" claim self-enforcing.
2. The heavy build's only record is an untracked log file plus local `.olean`
   timestamps. Commit the log (or a dated one-line receipt in PROOF-STATUS).

#### A4 — definitional bridge: attack failed

Lean `IsCanonical` ≡ engine definition term-for-term (fixed animals, translation
anchored, 8-connected, bounding-box height exactly H; `g2_redelmeier.cpp` per-box
h = maxy+1, miny = 0). Every plausible near-miss formalization (height ≤ H,
4-connectivity, free counting, |Δ| off-by-one, maxy = H, missing anchor) diverges at
a cell that IS machine-checked — most by n ≤ 3 — and an independent brute force
reproduced the banked triangle exactly through (6,5). The only "survivor" (allowing
p = q in `kingAdj`) is semantically identical, not an error.

Correction to the ledger's implication: the machine-checked bridge is **9 nonzero
cells** — (1,1),(2,1),(2,2),(3,1),(3,2),(3,3),(4,3),(5,3),(5,4) — not "n ≤ 5 all H";
the n = 6 values at `Compute.lean:285-286` are a prose comment, not checks. The 9
cells happen to be well-chosen (they kill every natural near-miss), but adding the
missing n ≤ 5 columns and the two n = 6 probes as real `native_decide` theorems is
cheap insurance.

#### A5 — native_decide trust base: survived

All 56 `native_decide` uses bottom out in `Lean.ofReduceBool` (compiler trust, not
kernel). The classic escalation vectors are absent — zero `implemented_by`,
`@[extern]`, `unsafe`, `partial def` in project files — and every
`native_decide`-rooted result is labeled as such in the ledger with its axiom
footprint. Toolchain pinned (lean4 v4.31.0, mathlib v4.31.0). Residual risk is
generic compiler trust, honestly disclosed.

#### A6/A7 — the paper vs the proofs: the paper is the weak document, not Lean

`paper/technical-report.tex` mentions Lean **zero** times and:
- states the diagonal law as hand-waving ("cell placement choices are sufficiently
  constrained to require…") when it is a machine-checked theorem;
- says P_k were "**fitted** against computed values … and verified against values
  from later rows" in the same breath as the exact `25^k/k!` claim — the single
  sentence an OEIS editor will push on. "Fitted" is also wrong in kind: given the
  proved degree-k bound, P_k is a determined exact solve, over-determined by later
  rows, not a regression;
- gives no provenance statement for which a(n) rest on pinned closed forms vs
  independent enumeration.

The admitted gaps (onset sharpness ab initio only k ≤ 5; monomial *coefficient*
integrality observed, only integer *values* proved) are stated consistently in
diagonal-law.md and grand-form.md and are not contradicted elsewhere.

### What an OEIS editor could reasonably object to, ranked

1. "Fitted" polynomials next to exact leading-coefficient claims, with the proof
   apparatus uncited (paper).
2. No provenance grading in the paper: which a(n) and which P_k are two-algorithm
   vs single-algorithm (levels 12–16 anchors and a(23)+ are single-algorithm).
3. T(36,20) presented as a holdout in SUBMISSION.md when it is P16-generated.
4. grand-form.md's stale self-contradiction about what remains open.
5. "Certified" without "conditional" in the T-n-nm1.md supersession bullet.

None of these is a defect in the Lean proofs. The attack brief — "show the proofs do
not lend credibility" — is not sustained by the evidence; what is sustained is that
the *documents around them* currently undersell (paper) or slightly oversell
(one bullet, one stale section) what was proved, and that the top five levels of the
pinned tier are exactly as strong as the kink engine and no stronger.

### Fix list (cheap → costly)

1. Reword T-n-nm1.md bullet: "certified conditional on two real-swept cells/level".
2. Delete/rewrite the two stale grand-form.md paragraphs (Corollary 3 note, "What
   remains open" Lean item).
3. Fix SUBMISSION.md holdout claim: T(35,19) only; drop or re-label T(36,20).
4. Commit weights3heavy.log (or a receipt); wrap Audit.lean in `#guard_msgs`.
5. Add the missing n ≤ 5 cells + the two n = 6 probes as real `native_decide`
   theorems in Compute.lean.
6. Paper: replace "fitted" with the determined-solve statement, cite the Lean
   theorems for shape/degree/integrality/25^k/k!, add a provenance table.
7. Complete strip C_14 (flips two anchors to multi-source; upgrades level 12–13
   provenance).

### Applied (2026-07-21, same day)

1. **Done** — T-n-nm1.md bullet now states the k = 4..16 conditionality
   explicitly.
2. **Done** — both stale grand-form.md paragraphs rewritten to match the
   Formalization section.
3. **Done** — SUBMISSION.md: T(35,19) is the holdout; T(36,20) re-labeled a
   consistency check (P_16-generated).
4. **Done** — `Grand/Audit.lean` wrapped in `#guard_msgs` (axiom drift now
   FAILS the build; verified against live output, all 8 guards pass);
   `weights3heavy.log` committed.
5. **Done** — `Polyplets/ComputeBridge.lean`: rows n ≤ 5 complete + T(6,4),
   T(6,5) as in-tree `native_decide` theorems; built green (258 s), bridge is
   now 17 kernel-recorded nonzero cells.
6. **Done** (paragraph rewrite incl. provenance grading; a fuller provenance
   table remains a paper-polish item).
7. **Done (2026-07-22)** — full Hmax=14 strip sweep vs banked triangle:
   **413 cells, 0 mismatches, columns H ≤ 14 independently confirmed to
   n = 36** (`results/strip_C14_run.log`; ran on dalby after the gympie
   attempt thrashed at a measured ~38 GB footprint). Anchors T(26,14) and
   T(27,14) flip to MULTI-SOURCE; the single-algorithm set shrinks from 9
   cells to the 7 of levels 13B–16. Recorded in `results/second-sources.md`.
